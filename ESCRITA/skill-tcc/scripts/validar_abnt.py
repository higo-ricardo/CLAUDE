"""
validar_abnt.py — audita mecanicamente um .docx final gerado por
docx_builder/paginacao_sumario contra as regras fixas da NBR 15287:2025:
margens, fonte/tamanho do corpo, espaçamento e larguras de tabela.

Não substitui a checagem visual do PDF (layout, quebras de página,
legibilidade) — complementa com o que dá pra verificar por número.
"""
from __future__ import annotations

from docx import Document
from docx.shared import Cm, Pt

MARGEM_TOPO_ESPERADA = Cm(3)
MARGEM_ESQUERDA_ESPERADA = Cm(3)
MARGEM_BAIXO_ESPERADA = Cm(2)
MARGEM_DIREITA_ESPERADA = Cm(2)
FONTE_ESPERADA = "Times New Roman"
FONTES_PERMITIDAS = {FONTE_ESPERADA, "Courier New"}  # Courier New: fluxo conceitual monoespaçado, recurso visual documentado no SKILL.md — não é a NBR que exige, mas é intencional
TAMANHO_CORPO_ESPERADO = Pt(12)
ESPACAMENTO_ESPERADO = 1.5
TOLERANCIA_EMU = 1000  # tolerância de arredondamento (~0.003cm)


def _proximo(a, b, tolerancia=TOLERANCIA_EMU) -> bool:
    return abs(int(a) - int(b)) <= tolerancia


def validar(caminho_docx: str) -> dict:
    doc = Document(caminho_docx)
    problemas: list[str] = []

    # --- margens (checa todas as seções, já que cada uma pode ter as suas) ---
    for i, section in enumerate(doc.sections):
        if not _proximo(section.top_margin, MARGEM_TOPO_ESPERADA):
            problemas.append(f"seção {i}: margem superior {section.top_margin.cm:.2f}cm (esperado 3cm)")
        if not _proximo(section.left_margin, MARGEM_ESQUERDA_ESPERADA):
            problemas.append(f"seção {i}: margem esquerda {section.left_margin.cm:.2f}cm (esperado 3cm)")
        if not _proximo(section.bottom_margin, MARGEM_BAIXO_ESPERADA):
            problemas.append(f"seção {i}: margem inferior {section.bottom_margin.cm:.2f}cm (esperado 2cm)")
        if not _proximo(section.right_margin, MARGEM_DIREITA_ESPERADA):
            problemas.append(f"seção {i}: margem direita {section.right_margin.cm:.2f}cm (esperado 2cm)")

    # --- fonte e tamanho do estilo Normal (corpo) ---
    normal = doc.styles["Normal"]
    if normal.font.name != FONTE_ESPERADA:
        problemas.append(f"estilo Normal: fonte {normal.font.name!r} (esperado {FONTE_ESPERADA!r})")
    if normal.font.size != TAMANHO_CORPO_ESPERADO:
        tamanho_atual = normal.font.size.pt if normal.font.size else None
        problemas.append(f"estilo Normal: tamanho {tamanho_atual}pt (esperado {TAMANHO_CORPO_ESPERADO.pt}pt)")

    # --- espaçamento 1,5 e fonte/tamanho por parágrafo de corpo ---
    for i, p in enumerate(doc.paragraphs):
        if not p.runs:
            continue
        espacamento = p.paragraph_format.line_spacing
        if espacamento is not None and espacamento != ESPACAMENTO_ESPERADO:
            # tabelas de sumário e itens numerados também usam 1,5; só reporta desvio de verdade
            if espacamento not in (ESPACAMENTO_ESPERADO, None):
                problemas.append(f"parágrafo {i}: espaçamento {espacamento} (esperado {ESPACAMENTO_ESPERADO})")
        for run in p.runs:
            if run.font.name and run.font.name not in FONTES_PERMITIDAS:
                problemas.append(f"parágrafo {i}: fonte de run {run.font.name!r} (esperado um de {sorted(FONTES_PERMITIDAS)})")
                break

    # --- larguras de tabela: cada célula de cada linha precisa ter width setado ---
    for t, table in enumerate(doc.tables):
        larguras_header = [c.width for c in table.rows[0].cells]
        for r, row in enumerate(table.rows):
            larguras_linha = [c.width for c in row.cells]
            if any(w is None for w in larguras_linha):
                problemas.append(f"tabela {t}, linha {r}: célula sem width definido")
            elif larguras_linha != larguras_header:
                problemas.append(
                    f"tabela {t}, linha {r}: larguras {[w.cm if w else None for w in larguras_linha]} "
                    f"diferem do cabeçalho {[w.cm if w else None for w in larguras_header]}"
                )

    return {"ok": len(problemas) == 0, "problemas": problemas}


if __name__ == "__main__":
    import sys
    import json

    relatorio = validar(sys.argv[1])
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    sys.exit(0 if relatorio["ok"] else 1)

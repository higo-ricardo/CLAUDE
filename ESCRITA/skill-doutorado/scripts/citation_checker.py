#!/usr/bin/env python3
"""
citation_checker.py — extrai citações (AUTOR, ano) do rascunho e cruza contra as
fontes validadas no research_log.json. Mecaniza a etapa 7 do fluxo (validar antes
de redigir): não julga se uma citação está bem empregada no argumento (isso é do
LLM), só verifica se ela tem lastro em uma fonte de fato validada — pega o caso
clássico de referência inventada "de memória".

Uso:
  python citation_checker.py --draft rascunho.md --log research_log.json
  python citation_checker.py --draft rascunho.md --log research_log.json --json
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from research_log import carregar, todas_fontes  # noqa: E402

# (SOBRENOME, ano) | (SOBRENOME; SOBRENOME2, ano) | (SOBRENOME et al., ano)
RE_PARENTETICA = re.compile(
    r"\(\s*([A-ZÀ-Ý][A-ZÀ-Ý\s;\.]*?(?:et al\.)?)\s*,\s*(\d{4}[a-z]?)\s*\)"
)
# Sobrenome (ano) | Sobrenome et al. (ano)
RE_NARRATIVA = re.compile(
    r"\b([A-ZÀ-Ý][a-zà-ÿ]+(?:\s+et\s+al\.)?)\s*\(\s*(\d{4}[a-z]?)\s*\)"
)


def extrair_citacoes(texto: str):
    """Retorna lista de (sobrenome_normalizado, ano) encontrados no texto."""
    citacoes = []
    for m in RE_PARENTETICA.finditer(texto):
        bloco, ano = m.group(1), m.group(2)
        # bloco pode ter vários autores separados por ';'
        for autor in bloco.split(";"):
            autor = autor.replace("et al.", "").strip().strip(",")
            if autor:
                citacoes.append((_normaliza(autor), ano))
    for m in RE_NARRATIVA.finditer(texto):
        autor, ano = m.group(1), m.group(2)
        autor = autor.replace(" et al.", "").strip()
        citacoes.append((_normaliza(autor), ano))
    return citacoes


def _normaliza(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().upper()


def _sobrenome_da_fonte(fonte: dict) -> str:
    # autor esperado no formato "SOBRENOME, Nome"
    return _normaliza(fonte["autor"].split(",")[0])


def auditar_citacoes(texto: str, log: dict) -> dict:
    citacoes = extrair_citacoes(texto)
    fontes = todas_fontes(log)

    citacoes_orfas = []
    citacoes_ok = []
    for sobrenome, ano in citacoes:
        match = any(
            sobrenome in _sobrenome_da_fonte(f) or _sobrenome_da_fonte(f) in sobrenome
            for f in fontes if str(f["ano"]) == str(ano)
        )
        (citacoes_ok if match else citacoes_orfas).append({"autor": sobrenome, "ano": ano})

    citadas = {(c["autor"], c["ano"]) for c in citacoes_ok}
    fontes_nao_citadas = [
        f for f in fontes
        if not any(_sobrenome_da_fonte(f) == a and str(f["ano"]) == y for a, y in citadas)
    ]

    return {
        "total_citacoes_no_texto": len(citacoes),
        "citacoes_ok": citacoes_ok,
        "citacoes_orfas": citacoes_orfas,
        "fontes_validadas_nao_citadas": [
            {"autor": f["autor"], "ano": f["ano"], "titulo": f["titulo"], "subtema": f["subtema"]}
            for f in fontes_nao_citadas
        ],
    }


def imprimir_relatorio(r: dict) -> None:
    print(f"Citações encontradas no texto: {r['total_citacoes_no_texto']}")
    if r["citacoes_orfas"]:
        print(f"\nCITAÇÕES SEM FONTE VALIDADA CORRESPONDENTE ({len(r['citacoes_orfas'])}) — "
              f"risco de referência fabricada, confirme com busca real antes de manter:")
        for c in r["citacoes_orfas"]:
            print(f"    - ({c['autor']}, {c['ano']})")
    else:
        print("Nenhuma citação órfã — todas têm fonte validada correspondente.")

    if r["fontes_validadas_nao_citadas"]:
        print(f"\nFontes validadas mas nunca citadas no texto ({len(r['fontes_validadas_nao_citadas'])}):")
        for f in r["fontes_validadas_nao_citadas"]:
            print(f"    - {f['autor']} ({f['ano']}) [{f['subtema']}] — {f['titulo']}")

    print()
    if r["citacoes_orfas"]:
        print("RESULTADO: NÃO redigir a versão final até resolver as citações órfãs.")
    else:
        print("RESULTADO: OK — todas as citações do rascunho têm lastro em fonte validada.")


def _cli():
    ap = argparse.ArgumentParser(description="Cruza citações do rascunho com fontes validadas")
    ap.add_argument("--draft", required=True, type=Path, help="arquivo .md/.txt do rascunho")
    ap.add_argument("--log", required=True, type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    texto = args.draft.read_text(encoding="utf-8")
    log = carregar(args.log)
    r = auditar_citacoes(texto, log)

    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        imprimir_relatorio(r)

    sys.exit(1 if r["citacoes_orfas"] else 0)


if __name__ == "__main__":
    _cli()

"""
paginacao_sumario.py — pipeline de duas passadas que calcula os números de
página REAIS do sumário (NBR 6027) e o ponto onde a numeração visível deve
começar (NBR 15287: conta-se a partir da folha de rosto, mas o número só
aparece a partir da Introdução) — sem chutar nada.

Passada 1: gera um rascunho sem números de página, converte pra PDF
(LibreOffice) e localiza a página real de cada heading via `pdftotext`.
Passada 2: gera o documento final com o sumário e o footer já corretos.

Assume que a Capa sempre ocupa exatamente 1 página não contada pela
norma ("conta-se a partir da folha de rosto") — daí o OFFSET_CAPA.
Se um spec futuro tornar a capa opcional, ajuste esta constante.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from docx_builder import build_document, heading1_text, referencias_heading_text
from numeracao import numerar_secoes

OFFSET_CAPA = 1


def _converter_para_pdf(docx_path: Path, pasta_saida: Path) -> Path:
    resultado = subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(pasta_saida), str(docx_path)],
        capture_output=True, text=True, timeout=120,
    )
    if resultado.returncode != 0:
        raise RuntimeError(f"soffice falhou: {resultado.stdout}\n{resultado.stderr}")
    return pasta_saida / (docx_path.stem + ".pdf")


def _extrair_paginas_texto(pdf_path: Path) -> list[str]:
    resultado = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True, text=True, timeout=60,
    )
    if resultado.returncode != 0:
        raise RuntimeError(f"pdftotext falhou: {resultado.stderr}")
    paginas = resultado.stdout.split("\x0c")
    # pdftotext deixa uma string vazia após o último form-feed
    if paginas and not paginas[-1].strip():
        paginas = paginas[:-1]
    return paginas


def _localizar_paginas_reais(paginas_texto: list[str], titulos: list[str]) -> dict[str, int]:
    """Devolve {titulo: pagina_raw (1-indexada)} — só procura DEPOIS da página do SUMÁRIO
    pra não confundir a entrada do sumário com o heading de verdade no corpo."""
    pagina_sumario = next((i for i, p in enumerate(paginas_texto) if "SUMÁRIO" in p), 0)
    localizacao: dict[str, int] = {}
    for titulo in titulos:
        for i in range(pagina_sumario + 1, len(paginas_texto)):
            if titulo in paginas_texto[i]:
                localizacao[titulo] = i + 1  # 1-indexado
                break
    return localizacao


def gerar_com_paginacao_real(spec: dict, saida_path: str | Path) -> Path:
    saida_path = Path(saida_path)

    if spec["metadata"].get("tipo_projeto") == "tcc_artigo":
        # Artigo (NBR 6022): sem capa/sumário, numeração já começa em 1 de
        # verdade — não há offset a calcular nem heading a localizar, então o
        # documento sai pronto numa passada só (mais simples e mais barato).
        build_document(spec).save(saida_path)
        return saida_path

    secoes_numeradas = numerar_secoes(spec["secoes"])
    titulos = [heading1_text(s) for s in secoes_numeradas] + [referencias_heading_text()]

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        # --- passada 1: rascunho ---------------------------------------
        rascunho_docx = tmp_dir / "rascunho.docx"
        build_document(spec).save(rascunho_docx)
        rascunho_pdf = _converter_para_pdf(rascunho_docx, tmp_dir)
        paginas_texto = _extrair_paginas_texto(rascunho_pdf)

        paginas_raw = _localizar_paginas_reais(paginas_texto, titulos)
        faltantes = [t for t in titulos if t not in paginas_raw]
        if faltantes:
            raise RuntimeError(
                f"não encontrei no PDF de rascunho a(s) seção(ões): {faltantes} — "
                "verifique se o texto do heading bate exatamente com o do spec."
            )

        # ABNT conta a partir da folha de rosto: subtrai a página da capa
        sumario_paginas = {t: p - OFFSET_CAPA for t, p in paginas_raw.items()}
        titulo_introducao = heading1_text(secoes_numeradas[0])
        pagina_inicio_corpo = sumario_paginas[titulo_introducao]

        # --- passada 2: documento final ----------------------------------
        doc_final = build_document(
            spec, sumario_paginas=sumario_paginas, pagina_inicio_corpo=pagina_inicio_corpo
        )
        doc_final.save(saida_path)

    return saida_path

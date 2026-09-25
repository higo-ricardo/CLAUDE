#!/usr/bin/env python3
"""
extrair_estrutura.py — lê um TCC/tese/dissertação (.docx ou .md/.txt já extraído)
e devolve a estrutura de capítulos/seções com contagem de palavras de cada um.

Isso NÃO decide quantos artigos o documento deve virar nem onde cortar — essa é
uma decisão de conteúdo do orquestrador (junto com o usuário). O script só entrega
o mapa real do documento (títulos, níveis, tamanho de cada seção em palavras) para
essa decisão ser tomada com números reais, em vez de "achismo" sobre o que cada
capítulo contém.

Uso:
  python extrair_estrutura.py --fonte tese.docx --out estrutura.json
  python extrair_estrutura.py --fonte tese.md --out estrutura.json

Para PDF: use a skill pdf-reading para extrair o texto primeiro (com marcação de
títulos em Markdown, ex. "# Capítulo 1"), salve como .md, e rode este script sobre
o .md.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def _extrair_de_docx(caminho: Path):
    from docx import Document
    doc = Document(str(caminho))

    secoes = []
    atual = None
    for p in doc.paragraphs:
        nivel = _nivel_heading(p.style.name if p.style else "")
        texto = p.text.strip()
        if nivel and texto:
            if atual:
                secoes.append(atual)
            atual = {"nivel": nivel, "titulo": texto, "paragrafos": []}
        elif texto and atual:
            atual["paragrafos"].append(texto)
        elif texto and not atual:
            # texto antes de qualquer heading detectado (ex.: capa/resumo sem estilo de título)
            if not secoes and atual is None:
                atual = {"nivel": 0, "titulo": "[antes do primeiro título detectado]", "paragrafos": []}
            atual["paragrafos"].append(texto)
    if atual:
        secoes.append(atual)
    return secoes


def _nivel_heading(nome_estilo: str):
    nome_estilo = nome_estilo.strip().lower()
    m = re.match(r"(heading|título|titulo)\s*(\d)", nome_estilo)
    if m:
        return int(m.group(2))
    return None


def _extrair_de_markdown(caminho: Path):
    texto = caminho.read_text(encoding="utf-8")
    linhas = texto.split("\n")
    secoes = []
    atual = None
    for linha in linhas:
        m = re.match(r"^(#{1,6})\s+(.*)", linha)
        if m:
            if atual:
                secoes.append(atual)
            atual = {"nivel": len(m.group(1)), "titulo": m.group(2).strip(), "paragrafos": []}
        elif linha.strip():
            if atual is None:
                atual = {"nivel": 0, "titulo": "[antes do primeiro título detectado]", "paragrafos": []}
            atual["paragrafos"].append(linha.strip())
    if atual:
        secoes.append(atual)
    return secoes


def _contar_palavras(texto: str) -> int:
    return len(re.findall(r"\S+", texto))


def gerar_estrutura(caminho: Path) -> dict:
    if caminho.suffix.lower() == ".docx":
        secoes_brutas = _extrair_de_docx(caminho)
    elif caminho.suffix.lower() in (".md", ".txt"):
        secoes_brutas = _extrair_de_markdown(caminho)
    else:
        raise ValueError("formato não suportado — use .docx, .md ou .txt (ver docstring para PDF)")

    secoes = []
    total_palavras = 0
    for s in secoes_brutas:
        texto_secao = " ".join(s["paragrafos"])
        n_palavras = _contar_palavras(texto_secao)
        total_palavras += n_palavras
        secoes.append({
            "nivel": s["nivel"], "titulo": s["titulo"],
            "palavras": n_palavras, "paragrafos": len(s["paragrafos"]),
        })

    return {"arquivo": str(caminho), "total_palavras": total_palavras, "secoes": secoes}


def imprimir_resumo(estrutura: dict) -> None:
    print(f"Arquivo: {estrutura['arquivo']}")
    print(f"Total de palavras (corpo, exclui títulos): {estrutura['total_palavras']}\n")
    for s in estrutura["secoes"]:
        indent = "  " * max(s["nivel"] - 1, 0)
        print(f"{indent}[Nível {s['nivel']}] {s['titulo']} — {s['palavras']} palavras "
              f"({s['paragrafos']} parágrafos)")


def _cli():
    ap = argparse.ArgumentParser(description="Extrai estrutura e contagem de palavras de um documento fonte")
    ap.add_argument("--fonte", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="grava a estrutura em JSON nesse arquivo")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    estrutura = gerar_estrutura(args.fonte)

    if args.out:
        args.out.write_text(json.dumps(estrutura, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Estrutura gravada em {args.out}")
    if args.json:
        print(json.dumps(estrutura, ensure_ascii=False, indent=2))
    else:
        imprimir_resumo(estrutura)


if __name__ == "__main__":
    _cli()

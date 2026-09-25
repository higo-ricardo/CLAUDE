#!/usr/bin/env python3
"""
reference_formatter.py — formata a lista de fontes_validadas do research_log.json
em referências, na norma escolhida para o periódico-alvo (ABNT NBR 6023, APA ou
Vancouver — as três mais comuns em periódicos científicos brasileiros). Regra fixa
e mecânica por tipo de documento e por norma — não decide se a fonte é boa (isso já
foi validado pelo LLM/agente antes de entrar no log), só formata a string.

Uso:
  python reference_formatter.py --log research_log.json --estilo abnt
  python reference_formatter.py --log research_log.json --estilo apa --out referencias.md
  python reference_formatter.py --log research_log.json --estilo vancouver --json
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from research_log import carregar, todas_fontes  # noqa: E402

ESTILOS_VALIDOS = ["abnt", "apa", "vancouver"]


# ------------------------------------------------------------ autor ----

def _autor_abnt(autor: str) -> str:
    if "," not in autor:
        return autor.upper()
    sobrenome, resto = autor.split(",", 1)
    return f"{sobrenome.strip().upper()}, {resto.strip()}"


def _autor_apa(autor: str) -> str:
    """'SILVA, João Carlos' -> 'Silva, J. C.' (sobrenome em title case, não em versalete)."""
    if "," not in autor:
        return autor
    sobrenome, resto = autor.split(",", 1)
    iniciais = " ".join(f"{n[0].upper()}." for n in resto.strip().split() if n)
    return f"{sobrenome.strip().title()}, {iniciais}".strip()


def _autor_vancouver(autor: str) -> str:
    """'SILVA, João Carlos' -> 'Silva JC' (sobrenome em title case, não em versalete)."""
    if "," not in autor:
        return autor
    sobrenome, resto = autor.split(",", 1)
    iniciais = "".join(n[0].upper() for n in resto.strip().split() if n)
    return f"{sobrenome.strip().title()} {iniciais}".strip()


# --------------------------------------------------------- templates ----

def _disponivel_em(url: str, estilo: str) -> str:
    if not url:
        return ""
    if estilo == "abnt":
        return f" Disponível em: {url}. Acesso em: [DATA DE ACESSO A PREENCHER]."
    if estilo == "apa":
        return f" {url}"
    return f" Available from: {url}"  # vancouver costuma usar "Available from:"


def _formatar_abnt(f: dict) -> str:
    autor = _autor_abnt(f["autor"])
    titulo = f["titulo"].rstrip(".")
    veiculo = f.get("veiculo", "").rstrip(".")
    ano, url, tipo = f["ano"], f.get("url", "").strip(), f["tipo"]
    da = _disponivel_em(url, "abnt")

    if tipo in ("artigo", "revisao"):
        return f"{autor}. {titulo}. {veiculo}, {ano}.{da}"
    if tipo == "tese":
        return f"{autor}. {titulo}. {ano}. Tese (Doutorado) – {veiculo}.{da}"
    if tipo == "dissertacao":
        return f"{autor}. {titulo}. {ano}. Dissertação (Mestrado) – {veiculo}.{da}"
    if tipo == "livro":
        return f"{autor}. {titulo}. {veiculo}, {ano}.{da}"
    if tipo == "capitulo":
        return f"{autor}. {titulo}. In: {veiculo}, {ano}.{da}"
    return f"{autor}. {titulo}. {veiculo}, {ano}.{da}"  # site / fallback


def _formatar_apa(f: dict) -> str:
    autor = _autor_apa(f["autor"])
    titulo = f["titulo"].rstrip(".")
    veiculo = f.get("veiculo", "").rstrip(".")
    ano, url, tipo = f["ano"], f.get("url", "").strip(), f["tipo"]
    da = _disponivel_em(url, "apa")

    if tipo in ("artigo", "revisao"):
        return f"{autor} ({ano}). {titulo}. {veiculo}.{da}"
    if tipo in ("tese", "dissertacao"):
        grau = "Doctoral dissertation" if tipo == "tese" else "Master's thesis"
        return f"{autor} ({ano}). {titulo} [{grau}, {veiculo}].{da}"
    if tipo == "livro":
        return f"{autor} ({ano}). {titulo}. {veiculo}.{da}"
    if tipo == "capitulo":
        return f"{autor} ({ano}). {titulo}. In {veiculo}.{da}"
    return f"{autor} ({ano}). {titulo}. {veiculo}.{da}"  # site / fallback


def _formatar_vancouver(f: dict) -> str:
    autor = _autor_vancouver(f["autor"])
    titulo = f["titulo"].rstrip(".")
    veiculo = f.get("veiculo", "").rstrip(".")
    ano, url, tipo = f["ano"], f.get("url", "").strip(), f["tipo"]
    da = _disponivel_em(url, "vancouver")

    if tipo in ("artigo", "revisao"):
        return f"{autor}. {titulo}. {veiculo}. {ano}.{da}"
    if tipo in ("tese", "dissertacao"):
        grau = "tese" if tipo == "tese" else "dissertação"
        return f"{autor}. {titulo} [{grau}]. {veiculo}; {ano}.{da}"
    if tipo == "livro":
        return f"{autor}. {titulo}. {veiculo}; {ano}.{da}"
    if tipo == "capitulo":
        return f"{autor}. {titulo}. In: {veiculo}; {ano}.{da}"
    return f"{autor}. {titulo}. {veiculo}; {ano}.{da}"  # site / fallback


_FORMATADORES = {"abnt": _formatar_abnt, "apa": _formatar_apa, "vancouver": _formatar_vancouver}


def formatar_fonte(f: dict, estilo: str) -> str:
    if estilo not in _FORMATADORES:
        raise ValueError(f"estilo deve ser um de: {', '.join(ESTILOS_VALIDOS)}")
    return _FORMATADORES[estilo](f)


def gerar_lista_referencias(log: dict, estilo: str = "abnt"):
    fontes = todas_fontes(log)
    formatadas = [(f, formatar_fonte(f, estilo)) for f in fontes]
    formatadas.sort(key=lambda par: par[0]["autor"].split(",")[0].strip().upper())
    return [texto for _, texto in formatadas]


def _cli():
    ap = argparse.ArgumentParser(description="Formata referências a partir do research_log")
    ap.add_argument("--log", required=True, type=Path)
    ap.add_argument("--estilo", choices=ESTILOS_VALIDOS, default="abnt")
    ap.add_argument("--out", type=Path, help="se informado, grava a lista formatada nesse arquivo")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    log = carregar(args.log)
    referencias = gerar_lista_referencias(log, args.estilo)

    saida = json.dumps(referencias, ensure_ascii=False, indent=2) if args.json else "\n\n".join(referencias)

    if args.out:
        args.out.write_text(saida + "\n", encoding="utf-8")
        print(f"{len(referencias)} referências ({args.estilo}) gravadas em {args.out}")
    else:
        print(saida)


if __name__ == "__main__":
    _cli()

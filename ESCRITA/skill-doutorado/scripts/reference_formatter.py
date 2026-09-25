#!/usr/bin/env python3
"""
reference_formatter.py — formata a lista de fontes_validadas do research_log.json
em referências no padrão NBR 6023, ordenadas alfabeticamente. Regra fixa e mecânica
por tipo de documento — não decide se a fonte é boa (isso já foi validado pelo LLM
antes de entrar no log), só formata a string.

Uso:
  python reference_formatter.py --log research_log.json
  python reference_formatter.py --log research_log.json --out referencias.md
  python reference_formatter.py --log research_log.json --json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from research_log import carregar, todas_fontes  # noqa: E402


def _autor_abnt(autor: str) -> str:
    """'Silva, João' -> 'SILVA, João' (sobrenome em versalete/maiúsculas)."""
    if "," not in autor:
        return autor.upper()
    sobrenome, resto = autor.split(",", 1)
    return f"{sobrenome.strip().upper()}, {resto.strip()}"


def formatar_fonte(f: dict) -> str:
    autor = _autor_abnt(f["autor"])
    titulo = f["titulo"].rstrip(".")
    veiculo = f.get("veiculo", "").rstrip(".")
    ano = f["ano"]
    url = f.get("url", "").strip()
    tipo = f["tipo"]

    disponivel_em = f" Disponível em: {url}. Acesso em: [DATA DE ACESSO A PREENCHER]." if url else ""

    if tipo in ("artigo", "revisao"):
        return f"{autor}. {titulo}. {veiculo}, {ano}.{disponivel_em}"

    if tipo == "tese":
        return (f"{autor}. {titulo}. {ano}. Tese (Doutorado) – {veiculo}.{disponivel_em}")

    if tipo == "dissertacao":
        return (f"{autor}. {titulo}. {ano}. Dissertação (Mestrado) – {veiculo}.{disponivel_em}")

    if tipo == "livro":
        return f"{autor}. {titulo}. {veiculo}, {ano}.{disponivel_em}"

    if tipo == "capitulo":
        return f"{autor}. {titulo}. In: {veiculo}, {ano}.{disponivel_em}"

    if tipo == "site":
        return f"{autor}. {titulo}. {veiculo}, {ano}.{disponivel_em}"

    # tipo desconhecido — formatação genérica, nunca falha silenciosamente
    return f"{autor}. {titulo}. {veiculo}, {ano}.{disponivel_em} [ATENÇÃO: tipo '{tipo}' sem template — revisar manualmente]"


def gerar_lista_referencias(log: dict):
    fontes = todas_fontes(log)
    formatadas = [(f, formatar_fonte(f)) for f in fontes]
    # ordena por sobrenome (parte antes da vírgula do autor)
    formatadas.sort(key=lambda par: par[0]["autor"].split(",")[0].strip().upper())
    return [texto for _, texto in formatadas]


def _cli():
    ap = argparse.ArgumentParser(description="Formata referências NBR 6023 a partir do research_log")
    ap.add_argument("--log", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="se informado, grava a lista formatada nesse arquivo")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    log = carregar(args.log)
    referencias = gerar_lista_referencias(log)

    if args.json:
        saida = json.dumps(referencias, ensure_ascii=False, indent=2)
    else:
        saida = "\n\n".join(referencias)

    if args.out:
        args.out.write_text(saida + "\n", encoding="utf-8")
        print(f"{len(referencias)} referências gravadas em {args.out}")
    else:
        print(saida)


if __name__ == "__main__":
    _cli()

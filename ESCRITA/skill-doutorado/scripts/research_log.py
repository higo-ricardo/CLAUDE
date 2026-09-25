#!/usr/bin/env python3
"""
research_log.py — gerencia o estado compartilhado da pesquisa (research_log.json).

Este módulo NÃO decide conteúdo (query a buscar, se uma fonte é idônea, etc.) —
isso é sempre julgamento do LLM. Ele só registra o que o LLM já decidiu, para que
os outros scripts (search_tracker, citation_checker, reference_formatter,
docx_builder) possam auditar e formatar de forma determinística.

Uso via CLI:
  python research_log.py init --log research_log.json --recorte "..." --idioma ptbr|ptbr+en
  python research_log.py add-busca --log research_log.json --subtema conceitual --idioma pt|en --query "..."
  python research_log.py add-fonte --log research_log.json --subtema conceitual \
      --autor "SILVA, J." --ano 2023 --titulo "..." --veiculo "..." --tipo artigo \
      --url "..." [--lido]
  python research_log.py show --log research_log.json
"""
import argparse
import json
import sys
from pathlib import Path

SUBTEMAS_PADRAO = ["conceitual", "estado_da_arte", "lacunas", "viabilidade"]
TIPOS_FONTE_VALIDOS = ["artigo", "tese", "dissertacao", "livro", "capitulo", "site", "revisao"]


def _subtema_vazio():
    return {"buscas_ptbr": [], "buscas_en": [], "fontes_validadas": []}


def novo_log(recorte: str, idioma: str, subtemas=None) -> dict:
    if idioma not in ("ptbr", "ptbr+en"):
        raise ValueError("idioma deve ser 'ptbr' ou 'ptbr+en'")
    subtemas = subtemas or SUBTEMAS_PADRAO
    return {
        "recorte": recorte,
        "idioma": idioma,
        "subtemas": {s: _subtema_vazio() for s in subtemas},
    }


def carregar(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} não existe ainda — rode 'init' primeiro para criar o research_log."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def salvar(path: Path, log: dict) -> None:
    path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def _garantir_subtema(log: dict, subtema: str) -> None:
    if subtema not in log["subtemas"]:
        log["subtemas"][subtema] = _subtema_vazio()


def add_busca(log: dict, subtema: str, idioma: str, query: str) -> dict:
    if idioma not in ("pt", "en"):
        raise ValueError("idioma da busca deve ser 'pt' ou 'en'")
    _garantir_subtema(log, subtema)
    chave = "buscas_ptbr" if idioma == "pt" else "buscas_en"
    log["subtemas"][subtema][chave].append(query)
    return log


def add_fonte(log: dict, subtema: str, autor: str, ano, titulo: str, veiculo: str,
              tipo: str, url: str = "", lido: bool = True) -> dict:
    if tipo not in TIPOS_FONTE_VALIDOS:
        raise ValueError(f"tipo deve ser um de: {', '.join(TIPOS_FONTE_VALIDOS)}")
    _garantir_subtema(log, subtema)
    fonte = {
        "autor": autor, "ano": ano, "titulo": titulo, "veiculo": veiculo,
        "tipo": tipo, "url": url, "lido": bool(lido),
    }
    log["subtemas"][subtema]["fontes_validadas"].append(fonte)
    return log


def todas_fontes(log: dict):
    """Retorna todas as fontes validadas de todos os subtemas, com o subtema anexado."""
    out = []
    for subtema, dados in log["subtemas"].items():
        for f in dados["fontes_validadas"]:
            out.append({**f, "subtema": subtema})
    return out


def _cli():
    p = argparse.ArgumentParser(description="Gerencia o research_log.json compartilhado")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Cria um novo research_log.json")
    p_init.add_argument("--log", required=True, type=Path)
    p_init.add_argument("--recorte", required=True)
    p_init.add_argument("--idioma", required=True, choices=["ptbr", "ptbr+en"])

    p_busca = sub.add_parser("add-busca", help="Registra uma busca realizada")
    p_busca.add_argument("--log", required=True, type=Path)
    p_busca.add_argument("--subtema", required=True)
    p_busca.add_argument("--idioma", required=True, choices=["pt", "en"])
    p_busca.add_argument("--query", required=True)

    p_fonte = sub.add_parser("add-fonte", help="Registra uma fonte validada")
    p_fonte.add_argument("--log", required=True, type=Path)
    p_fonte.add_argument("--subtema", required=True)
    p_fonte.add_argument("--autor", required=True, help="Formato: SOBRENOME, Nome")
    p_fonte.add_argument("--ano", required=True)
    p_fonte.add_argument("--titulo", required=True)
    p_fonte.add_argument("--veiculo", required=True, help="Periódico, editora, repositório etc.")
    p_fonte.add_argument("--tipo", required=True, choices=TIPOS_FONTE_VALIDOS)
    p_fonte.add_argument("--url", default="")
    p_fonte.add_argument("--lido", action="store_true", default=True)
    p_fonte.add_argument("--nao-lido", dest="lido", action="store_false")

    p_show = sub.add_parser("show", help="Imprime o log atual formatado")
    p_show.add_argument("--log", required=True, type=Path)

    args = p.parse_args()

    if args.cmd == "init":
        if args.log.exists():
            print(f"AVISO: {args.log} já existe — nada foi sobrescrito.", file=sys.stderr)
            sys.exit(1)
        log = novo_log(args.recorte, args.idioma)
        salvar(args.log, log)
        print(f"research_log criado em {args.log}")
        return

    if args.cmd == "add-busca":
        log = carregar(args.log)
        add_busca(log, args.subtema, args.idioma, args.query)
        salvar(args.log, log)
        print(f"Busca registrada em '{args.subtema}' ({args.idioma}): {args.query}")
        return

    if args.cmd == "add-fonte":
        log = carregar(args.log)
        add_fonte(log, args.subtema, args.autor, args.ano, args.titulo,
                   args.veiculo, args.tipo, args.url, args.lido)
        salvar(args.log, log)
        print(f"Fonte registrada em '{args.subtema}': {args.autor} ({args.ano})")
        return

    if args.cmd == "show":
        log = carregar(args.log)
        print(json.dumps(log, ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    _cli()

"""
validar_ciclo_pesquisa.py — gate mecânico do piso de busca do Passo 2,
calibrado para o escopo mais leve de TCC/monografia (não o de mestrado):
1-3 sub-temas no total, 2-4 fontes validadas por sub-tema, mínimo de
1 busca por sub-tema (reformulada se não bater o piso de fontes).

Lê um `buscas_log.json` ({sub_tema: [queries feitas]}) e o `fontes.json`
persistido por `fontes_registry.py` (cada fonte carrega o campo
"subtema"), e devolve um relatório pass/fail por sub-tema em vez de
deixar a LLM "se autoavaliar".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

MIN_BUSCAS = 1
MIN_FONTES = 2
MAX_FONTES_RECOMENDADO = 4
MAX_SUBTEMAS_RECOMENDADO = 3


def validar_ciclo(buscas_log: dict[str, list[str]], fontes_json: dict) -> dict:
    fontes_por_subtema: dict[str, int] = {}
    for fonte in fontes_json.get("fontes", []):
        subtema = fonte.get("subtema") or "(sem sub-tema)"
        fontes_por_subtema[subtema] = fontes_por_subtema.get(subtema, 0) + 1

    todos_subtemas = set(buscas_log) | set(fontes_por_subtema)
    relatorio_por_subtema = {}
    ok_geral = True

    for subtema in sorted(todos_subtemas):
        n_buscas = len(buscas_log.get(subtema, []))
        n_fontes = fontes_por_subtema.get(subtema, 0)
        buscas_ok = n_buscas >= MIN_BUSCAS
        fontes_ok = n_fontes >= MIN_FONTES
        acima_do_recomendado = n_fontes > MAX_FONTES_RECOMENDADO
        relatorio_por_subtema[subtema] = {
            "buscas": n_buscas, "buscas_ok": buscas_ok,
            "fontes": n_fontes, "fontes_ok": fontes_ok,
            "aviso_escopo": (
                f"{n_fontes} fontes > {MAX_FONTES_RECOMENDADO} recomendado para TCC — "
                "não é erro, mas considere se o escopo não cresceu demais"
            ) if acima_do_recomendado else None,
            "ok": buscas_ok and fontes_ok,
        }
        ok_geral = ok_geral and buscas_ok and fontes_ok

    n_subtemas = len(todos_subtemas)
    aviso_subtemas = (
        f"{n_subtemas} sub-temas > {MAX_SUBTEMAS_RECOMENDADO} recomendado para TCC — "
        "considere consolidar ou verificar se o tema não ficou amplo demais"
        if n_subtemas > MAX_SUBTEMAS_RECOMENDADO else None
    )

    return {
        "ok": ok_geral,
        "piso": {"min_buscas": MIN_BUSCAS, "min_fontes": MIN_FONTES, "max_fontes_recomendado": MAX_FONTES_RECOMENDADO},
        "n_subtemas": n_subtemas,
        "aviso_subtemas": aviso_subtemas,
        "subtemas": relatorio_por_subtema,
    }


def validar_arquivos(buscas_log_path: str, fontes_json_path: str) -> dict:
    buscas_log = json.loads(Path(buscas_log_path).read_text(encoding="utf-8"))
    fontes_json = json.loads(Path(fontes_json_path).read_text(encoding="utf-8"))
    return validar_ciclo(buscas_log, fontes_json)


if __name__ == "__main__":
    relatorio = validar_arquivos(sys.argv[1], sys.argv[2])
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    sys.exit(0 if relatorio["ok"] else 1)

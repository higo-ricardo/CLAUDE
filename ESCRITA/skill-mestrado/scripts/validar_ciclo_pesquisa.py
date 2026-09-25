"""
validar_ciclo_pesquisa.py — gate mecânico do piso de busca do Passo 2.

Lê um `buscas_log.json` ({sub_tema: [queries feitas]}) e o `fontes.json`
persistido por `fontes_registry.py` (cada fonte carrega o campo
"subtema"), e aplica o piso combinado no SKILL.md: no mínimo 2-3 buscas
e 3-5 fontes validadas por sub-tema. Devolve um relatório pass/fail por
sub-tema em vez de deixar a LLM "se autoavaliar".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

MIN_BUSCAS = 2
MIN_FONTES = 3


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
        relatorio_por_subtema[subtema] = {
            "buscas": n_buscas, "buscas_ok": buscas_ok,
            "fontes": n_fontes, "fontes_ok": fontes_ok,
            "ok": buscas_ok and fontes_ok,
        }
        ok_geral = ok_geral and buscas_ok and fontes_ok

    return {"ok": ok_geral, "piso": {"min_buscas": MIN_BUSCAS, "min_fontes": MIN_FONTES}, "subtemas": relatorio_por_subtema}


def validar_arquivos(buscas_log_path: str, fontes_json_path: str) -> dict:
    buscas_log = json.loads(Path(buscas_log_path).read_text(encoding="utf-8"))
    fontes_json = json.loads(Path(fontes_json_path).read_text(encoding="utf-8"))
    return validar_ciclo(buscas_log, fontes_json)


if __name__ == "__main__":
    relatorio = validar_arquivos(sys.argv[1], sys.argv[2])
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    sys.exit(0 if relatorio["ok"] else 1)

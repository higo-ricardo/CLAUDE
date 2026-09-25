#!/usr/bin/env python3
"""
search_tracker.py — audita o research_log.json contra o piso mínimo de cobertura
definido no SKILL.md (3-5 buscas por subtema/idioma, 5-7 fontes validadas por
subtema). Não decide se um subtema "está bom" no sentido de conteúdo — só conta
e compara contra o limiar. Julgamento de qualidade/relevância continua com o LLM.

Uso:
  python search_tracker.py --log research_log.json
  python search_tracker.py --log research_log.json --min-buscas 3 --min-fontes 5
  python search_tracker.py --log research_log.json --json     # saída máquina-legível
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from research_log import carregar  # noqa: E402


def auditar(log: dict, min_buscas: int = 3, min_fontes: int = 5) -> dict:
    idioma = log.get("idioma", "ptbr")
    exige_en = idioma == "ptbr+en"

    resultado = {"idioma": idioma, "min_buscas": min_buscas, "min_fontes": min_fontes,
                 "subtemas": {}, "conforme": True}

    for subtema, dados in log["subtemas"].items():
        n_pt = len(dados["buscas_ptbr"])
        n_en = len(dados["buscas_en"])
        n_fontes = len(dados["fontes_validadas"])
        n_fontes_lidas = sum(1 for f in dados["fontes_validadas"] if f.get("lido"))

        ok_pt = n_pt >= min_buscas
        ok_en = (not exige_en) or (n_en >= min_buscas)
        ok_fontes = n_fontes >= min_fontes
        ok_lidas = n_fontes_lidas == n_fontes  # toda fonte validada precisa ter sido lida

        conforme = ok_pt and ok_en and ok_fontes and ok_lidas
        resultado["conforme"] &= conforme

        resultado["subtemas"][subtema] = {
            "buscas_ptbr": n_pt, "buscas_en": n_en if exige_en else None,
            "fontes_validadas": n_fontes, "fontes_lidas": n_fontes_lidas,
            "conforme": conforme,
            "pendencias": [
                p for p, cond in [
                    (f"faltam buscas PT-BR ({n_pt}/{min_buscas})", not ok_pt),
                    (f"faltam buscas em inglês ({n_en}/{min_buscas})", exige_en and not ok_en),
                    (f"faltam fontes validadas ({n_fontes}/{min_fontes})", not ok_fontes),
                    (f"{n_fontes - n_fontes_lidas} fonte(s) validada(s) mas não lida(s)", not ok_lidas),
                ] if cond
            ],
        }

    return resultado


def imprimir_relatorio(resultado: dict) -> None:
    print(f"Idioma configurado: {resultado['idioma']}")
    print(f"Piso: {resultado['min_buscas']} buscas/idioma e {resultado['min_fontes']} fontes por subtema\n")
    for subtema, r in resultado["subtemas"].items():
        status = "OK" if r["conforme"] else "INSUFICIENTE"
        linha = f"[{status}] {subtema}: {r['buscas_ptbr']} buscas PT"
        if r["buscas_en"] is not None:
            linha += f", {r['buscas_en']} buscas EN"
        linha += f", {r['fontes_validadas']} fontes ({r['fontes_lidas']} lidas)"
        print(linha)
        for p in r["pendencias"]:
            print(f"    - {p}")
    print()
    print("RESULTADO GERAL:", "CONFORME — pode avançar" if resultado["conforme"]
          else "AINDA NÃO CONFORME — não avance para a redação/validação final")


def _cli():
    ap = argparse.ArgumentParser(description="Audita cobertura de busca vs. piso mínimo")
    ap.add_argument("--log", required=True, type=Path)
    ap.add_argument("--min-buscas", type=int, default=3)
    ap.add_argument("--min-fontes", type=int, default=5)
    ap.add_argument("--json", action="store_true", help="saída em JSON em vez de texto")
    args = ap.parse_args()

    log = carregar(args.log)
    resultado = auditar(log, args.min_buscas, args.min_fontes)

    if args.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        imprimir_relatorio(resultado)

    sys.exit(0 if resultado["conforme"] else 1)


if __name__ == "__main__":
    _cli()

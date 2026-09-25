#!/usr/bin/env python3
"""
cronograma_builder.py — distribui etapas-padrão de um doutorado ao longo da duração
informada e gera a tabela de cronograma (NBR 15287, seção 8 do template). É uma
distribuição proporcional determinística sobre uma lista de etapas — o LLM pode
sobrescrever etapas/proporções via --etapas para casos fora do padrão, mas a conta
de "em que período cada etapa cai" não exige julgamento, só aritmética.

Uso:
  python cronograma_builder.py --duracao-meses 48 --granularidade semestre --out cronograma.json
  python cronograma_builder.py --duracao-meses 48 --etapas etapas_custom.json --out cronograma.json

Formato de --etapas (opcional; se omitido, usa ETAPAS_PADRAO abaixo):
[
  {"nome": "Revisão de literatura aprofundada", "inicio_frac": 0.0, "fim_frac": 0.35},
  ...
]
inicio_frac/fim_frac são frações (0.0-1.0) da duração total em que a etapa está ativa.
"""
import argparse
import json
import math
import sys
from pathlib import Path

ETAPAS_PADRAO = [
    {"nome": "Revisão de literatura aprofundada", "inicio_frac": 0.00, "fim_frac": 0.35},
    {"nome": "Qualificação", "inicio_frac": 0.30, "fim_frac": 0.40},
    {"nome": "Coleta de dados", "inicio_frac": 0.35, "fim_frac": 0.65},
    {"nome": "Análise dos dados", "inicio_frac": 0.55, "fim_frac": 0.80},
    {"nome": "Redação de artigos", "inicio_frac": 0.60, "fim_frac": 0.90},
    {"nome": "Redação e defesa da tese", "inicio_frac": 0.80, "fim_frac": 1.00},
]


def gerar_cronograma(duracao_meses: int, granularidade: str = "semestre", etapas=None) -> dict:
    if granularidade not in ("semestre", "ano", "trimestre"):
        raise ValueError("granularidade deve ser 'trimestre', 'semestre' ou 'ano'")
    etapas = etapas or ETAPAS_PADRAO

    meses_por_periodo = {"trimestre": 3, "semestre": 6, "ano": 12}[granularidade]
    n_periodos = max(1, math.ceil(duracao_meses / meses_por_periodo))
    rotulo = {"trimestre": "Trim.", "semestre": "Sem.", "ano": "Ano"}[granularidade]
    periodos = [f"{rotulo} {i + 1}" for i in range(n_periodos)]

    linhas = []
    for etapa in etapas:
        ini_mes = etapa["inicio_frac"] * duracao_meses
        fim_mes = etapa["fim_frac"] * duracao_meses
        marcacoes = []
        for i in range(n_periodos):
            p_ini = i * meses_por_periodo
            p_fim = (i + 1) * meses_por_periodo
            ativo = not (fim_mes < p_ini or ini_mes > p_fim)
            marcacoes.append("X" if ativo else "")
        linhas.append({"etapa": etapa["nome"], "marcacoes": marcacoes})

    return {"duracao_meses": duracao_meses, "granularidade": granularidade,
            "periodos": periodos, "linhas": linhas}


def imprimir_tabela(cronograma: dict) -> None:
    cabecalho = ["Etapa"] + cronograma["periodos"]
    print(" | ".join(cabecalho))
    print("-" * (len(" | ".join(cabecalho))))
    for linha in cronograma["linhas"]:
        print(" | ".join([linha["etapa"]] + [m or "-" for m in linha["marcacoes"]]))


def _cli():
    ap = argparse.ArgumentParser(description="Gera tabela de cronograma proporcional")
    ap.add_argument("--duracao-meses", type=int, default=48)
    ap.add_argument("--granularidade", choices=["trimestre", "semestre", "ano"], default="semestre")
    ap.add_argument("--etapas", type=Path, help="JSON custom de etapas (ver docstring)")
    ap.add_argument("--out", type=Path, help="grava o cronograma em JSON nesse arquivo")
    args = ap.parse_args()

    etapas = json.loads(args.etapas.read_text(encoding="utf-8")) if args.etapas else None
    cronograma = gerar_cronograma(args.duracao_meses, args.granularidade, etapas)

    if args.out:
        args.out.write_text(json.dumps(cronograma, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Cronograma gravado em {args.out}")
    imprimir_tabela(cronograma)


if __name__ == "__main__":
    _cli()

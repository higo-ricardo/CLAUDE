"""
gerar_projeto.py — CLI que orquestra a geração final do projeto de pesquisa
a partir do que o Agente Redator produziu.

Uso:
    python3 gerar_projeto.py --spec spec.json --fontes fontes.json --out saida/<slug>.docx

Passos (todos determinísticos — nenhuma decisão de conteúdo acontece aqui):
  1. Carrega spec.json (conteúdo já escrito pelo Agente Redator) e fontes.json
     (registro de fontes do Agente Pesquisador, via fontes_registry.py).
  2. Injeta spec["referencias_formatadas"] (NBR 6023, ordenada alfabeticamente)
     e spec["fichamento"] (tabela de Registro das Fontes, se a seção existir
     no spec) — ambos calculados a partir de fontes.json; o Agente Redator
     nunca formata isso à mão.
  3. Chama paginacao_sumario.gerar_com_paginacao_real() para produzir o
     .docx final com sumário e paginação reais (não estimados).
  4. Roda validar_abnt.py sobre o resultado e imprime o relatório.

Sai com código 0 se a validação ABNT passar, 1 caso contrário — mas o
arquivo é gerado e salvo de qualquer forma (falha de formatação é
reportada, não bloqueia a entrega do rascunho pro usuário revisar).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fontes_registry import FontesRegistry
from paginacao_sumario import gerar_com_paginacao_real
from validar_abnt import validar


def gerar(spec_path: str, fontes_path: str, saida_path: str) -> dict:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    registry = FontesRegistry.carregar(fontes_path)
    spec["referencias_formatadas"] = registry.listar_referencias_formatadas()
    spec["fichamento"] = registry.listar_fichamento()

    Path(saida_path).parent.mkdir(parents=True, exist_ok=True)
    saida = gerar_com_paginacao_real(spec, saida_path)
    relatorio_abnt = validar(str(saida))

    return {
        "arquivo": str(saida),
        "n_referencias": len(spec["referencias_formatadas"]),
        "validacao_abnt": relatorio_abnt,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera o .docx final do TCC/monografia (NBR 15287:2025) a partir de spec.json + fontes.json."
    )
    parser.add_argument("--spec", required=True, help="caminho para spec.json (saída do Agente Redator)")
    parser.add_argument("--fontes", required=True, help="caminho para fontes.json (saída do Agente Pesquisador)")
    parser.add_argument("--out", required=True, help="caminho de saída do .docx final")
    args = parser.parse_args()

    resultado = gerar(args.spec, args.fontes, args.out)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    sys.exit(0 if resultado["validacao_abnt"]["ok"] else 1)


if __name__ == "__main__":
    main()

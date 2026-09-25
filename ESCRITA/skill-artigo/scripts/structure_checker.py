#!/usr/bin/env python3
"""
structure_checker.py — confere a completude estrutural de um artigo científico
contra o config usado pelo docx_builder.py (mesmo arquivo, então o que passa aqui
já está pronto para virar .docx). Puramente mecânico: contagem de palavras, presença
de seções obrigatórias, contagem de palavras-chave. Não julga qualidade do conteúdo
— isso é a auditoria de citações (citation_checker.py) e a leitura crítica do
agente auditor.

Uso:
  python structure_checker.py --config artigo.json
  python structure_checker.py --config artigo.json --secoes-obrigatorias "Introdução,Método,Resultados,Discussão,Conclusão"
  python structure_checker.py --config artigo.json --limite-palavras 6000
"""
import argparse
import json
import re
import sys
from pathlib import Path

SECOES_OBRIGATORIAS_PADRAO = ["Introdução", "Método", "Resultados", "Discussão", "Conclusão"]


def _contar_palavras(texto: str) -> int:
    return len(re.findall(r"\S+", texto or ""))


def _normaliza(s: str) -> str:
    return s.strip().lower()


def auditar(config: dict, secoes_obrigatorias=None, min_palavras_secao=50,
            resumo_min=100, resumo_max=250, min_palavras_chave=3, max_palavras_chave=5,
            limite_palavras_total=None) -> dict:
    secoes_obrigatorias = secoes_obrigatorias or SECOES_OBRIGATORIAS_PADRAO
    meta = config.get("meta", {})
    secoes = config.get("secoes", [])

    problemas = []
    avisos = []

    # título
    if not meta.get("titulo", "").strip():
        problemas.append("Título ausente ou vazio.")

    # resumo / abstract
    for campo, rotulo in [("resumo", "Resumo"), ("abstract", "Abstract")]:
        texto = meta.get(campo, "")
        n = _contar_palavras(texto)
        if not texto.strip():
            problemas.append(f"{rotulo} ausente.")
        elif not (resumo_min <= n <= resumo_max):
            avisos.append(f"{rotulo} com {n} palavras — fora da faixa usual {resumo_min}-{resumo_max} "
                           f"(confira o limite do periódico-alvo).")

    # palavras-chave / keywords
    for campo, rotulo in [("palavras_chave", "Palavras-chave"), ("keywords", "Keywords")]:
        lista = meta.get(campo, [])
        n = len(lista)
        if n == 0:
            problemas.append(f"{rotulo} ausentes.")
        elif not (min_palavras_chave <= n <= max_palavras_chave):
            avisos.append(f"{rotulo}: {n} termos — fora da faixa usual {min_palavras_chave}-{max_palavras_chave}.")

    # seções obrigatórias
    titulos_presentes = {_normaliza(s.get("titulo", "")): s for s in secoes}
    for obrigatoria in secoes_obrigatorias:
        chave = _normaliza(obrigatoria)
        encontrada = next((s for t, s in titulos_presentes.items() if chave in t or t in chave), None)
        if not encontrada:
            problemas.append(f"Seção obrigatória ausente: '{obrigatoria}'.")
        else:
            n = _contar_palavras(encontrada.get("texto", ""))
            if n < min_palavras_secao:
                problemas.append(f"Seção '{obrigatoria}' muito curta ({n} palavras, "
                                  f"mínimo esperado {min_palavras_secao}) — parece placeholder.")

    # limite de palavras do periódico-alvo
    total_corpo = sum(_contar_palavras(s.get("texto", "")) for s in secoes)
    resultado_extra = {"total_palavras_corpo": total_corpo}
    if limite_palavras_total:
        if total_corpo > limite_palavras_total:
            problemas.append(f"Corpo do artigo com {total_corpo} palavras excede o limite "
                              f"informado do periódico-alvo ({limite_palavras_total}).")
        resultado_extra["limite_palavras_total"] = limite_palavras_total

    return {"conforme": len(problemas) == 0, "problemas": problemas, "avisos": avisos, **resultado_extra}


def imprimir_relatorio(r: dict) -> None:
    print(f"Total de palavras no corpo (soma das seções): {r['total_palavras_corpo']}")
    if r.get("limite_palavras_total"):
        print(f"Limite do periódico-alvo: {r['limite_palavras_total']}")
    print()
    if r["problemas"]:
        print(f"PROBLEMAS BLOQUEANTES ({len(r['problemas'])}):")
        for p in r["problemas"]:
            print(f"    - {p}")
    else:
        print("Nenhum problema estrutural bloqueante encontrado.")
    if r["avisos"]:
        print(f"\nAvisos (não bloqueantes, vale revisar):")
        for a in r["avisos"]:
            print(f"    - {a}")
    print()
    print("RESULTADO:", "CONFORME" if r["conforme"] else "AINDA NÃO CONFORME — resolva os problemas bloqueantes")


def _cli():
    ap = argparse.ArgumentParser(description="Audita completude estrutural do artigo (config do docx_builder)")
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--secoes-obrigatorias", help="lista separada por vírgula (padrão: IMRaD + Conclusão)")
    ap.add_argument("--min-palavras-secao", type=int, default=50)
    ap.add_argument("--resumo-min", type=int, default=100)
    ap.add_argument("--resumo-max", type=int, default=250)
    ap.add_argument("--min-palavras-chave", type=int, default=3)
    ap.add_argument("--max-palavras-chave", type=int, default=5)
    ap.add_argument("--limite-palavras", type=int, help="limite total de palavras do periódico-alvo")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    secoes_obrig = [s.strip() for s in args.secoes_obrigatorias.split(",")] if args.secoes_obrigatorias else None

    r = auditar(config, secoes_obrig, args.min_palavras_secao, args.resumo_min, args.resumo_max,
                args.min_palavras_chave, args.max_palavras_chave, args.limite_palavras)

    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        imprimir_relatorio(r)

    sys.exit(0 if r["conforme"] else 1)


if __name__ == "__main__":
    _cli()

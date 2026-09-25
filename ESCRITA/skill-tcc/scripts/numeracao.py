"""
numeracao.py — NBR 6024: numeração progressiva de seções.

Dada uma árvore de seções (nível 1 com subseções opcionais em nível 2),
devolve os títulos já prefixados com o número — como texto estático,
sem depender de heading style automático do Word.
"""
from __future__ import annotations


def numerar_secoes(secoes: list[dict]) -> list[dict]:
    """
    secoes: [{"titulo": "Introdução", "paragrafos": [...], "subsecoes": [...]}, ...]

    Devolve uma cópia rasa de cada seção com "titulo_numerado" adicionado
    (e o mesmo para cada item de "subsecoes"). Seções com "opcional": True
    e ausentes/vazias (sem paragrafos/lista_numerada/subsecoes) são
    puladas e não recebem número — a numeração das seguintes se ajusta.
    """
    resultado = []
    n = 0
    for secao in secoes:
        if secao.get("opcional") and _secao_vazia(secao):
            continue
        n += 1
        nova = dict(secao)
        nova["titulo_numerado"] = f'{n} {secao["titulo"]}'
        subsecoes = secao.get("subsecoes")
        if subsecoes:
            nova["subsecoes"] = [
                {**sub, "titulo_numerado": f'{n}.{m} {sub["titulo"]}'}
                for m, sub in enumerate(subsecoes, start=1)
            ]
        resultado.append(nova)
    return resultado


def _secao_vazia(secao: dict) -> bool:
    return (
        not secao.get("paragrafos")
        and not secao.get("lista_numerada")
        and not secao.get("subsecoes")
    )

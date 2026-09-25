"""
cronograma.py — gera as colunas do cronograma a partir da duração do
mestrado/doutorado, e a matriz final a partir de atividades + marcações
já decididas pela LLM.
"""
from __future__ import annotations


def gerar_colunas(duracao_meses: int, granularidade: str) -> list[str]:
    """granularidade: 'mensal' ou 'semestral'."""
    if granularidade == "mensal":
        return [f"Mês {i}" for i in range(1, duracao_meses + 1)]
    if granularidade == "semestral":
        n_semestres = -(-duracao_meses // 6)  # arredonda pra cima
        return [f"Sem {i}" for i in range(1, n_semestres + 1)]
    raise ValueError(f"granularidade inválida: {granularidade!r} (use 'mensal' ou 'semestral')")


def montar_tabela(atividades: list[str], marcacoes: dict[str, list[int]], colunas: list[str]) -> dict:
    """
    marcacoes: {"0": [0,1], "1": [1,2], ...} — índice da atividade (str) -> índices de coluna marcados.

    Valida os índices e devolve uma estrutura pronta pra renderização:
    {"cabecalho": [...], "linhas": [{"atividade": str, "marcado": [bool, ...]}, ...]}
    """
    n_col = len(colunas)
    linhas = []
    for i, atividade in enumerate(atividades):
        marcados_idx = marcacoes.get(str(i), [])
        for idx in marcados_idx:
            if not (0 <= idx < n_col):
                raise ValueError(
                    f"marcação inválida para atividade {i} ({atividade!r}): "
                    f"coluna {idx} fora do intervalo [0, {n_col - 1}]"
                )
        linhas.append({
            "atividade": atividade,
            "marcado": [idx in marcados_idx for idx in range(n_col)],
        })
    return {"cabecalho": colunas, "linhas": linhas}

"""
fontes_registry.py — Registro incremental de fontes de pesquisa.

Chamado pela LLM durante o Passo 2 (Ciclo de pesquisa), uma vez por fonte
validada. Devolve a chave de citação já correta (com sufixo a/b/c quando
há outro autor+ano igual) para a LLM inserir na prosa — a LLM nunca
formata NBR 10520/6023 "na mão".

Uso típico:
    registry = FontesRegistry()
    cit = registry.registrar(
        autores=[{"sobrenome": "SILVA", "nome": "João"}],
        titulo="Personalização de ensino via IA",
        ano=2022,
        tipo="periodico",
        subtema="tutoria_inteligente",
        periodico="Revista Brasileira de Informática na Educação",
        local="Porto Alegre", volume="30", numero="1", paginas="45-60",
    )
    # cit["citacao_parentese"] -> "(SILVA, 2022)"
    # cit["citacao_sujeito"]   -> "Silva (2022)"
    registry.persistir("fontes.json")
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


TIPOS_VALIDOS = {"periodico", "livro", "capitulo", "dissertacao", "tese", "anais", "eletronico"}

_MESES = [
    "jan.", "fev.", "mar.", "abr.", "maio", "jun.",
    "jul.", "ago.", "set.", "out.", "nov.", "dez.",
]


def _sobrenome_principal(autores: list[dict]) -> str:
    return autores[0]["sobrenome"].strip().upper()


def _autores_referencia(autores: list[dict]) -> str:
    """'SOBRENOME, Nome' para cada autor, separados por ';' (NBR 6023)."""
    partes = [f'{a["sobrenome"].strip().upper()}, {a["nome"].strip()}' for a in autores]
    return "; ".join(partes)


def _autores_citacao(autores: list[dict]) -> str:
    """SOBRENOME(S) para uso em citação (NBR 10520): 1 autor, 2 autores, ou 'et al.' a partir de 3."""
    sobrenomes = [a["sobrenome"].strip().upper() for a in autores]
    if len(sobrenomes) == 1:
        return sobrenomes[0]
    if len(sobrenomes) == 2:
        return "; ".join(sobrenomes)
    return f"{sobrenomes[0]} et al."


def _autores_citacao_sujeito(autores: list[dict]) -> str:
    """Forma 'Sobrenome' / 'Sobrenome1 e Sobrenome2' / 'Sobrenome1 et al.' quando o autor é sujeito da frase."""
    nomes = [a["sobrenome"].strip().capitalize() for a in autores]
    if len(nomes) == 1:
        return nomes[0]
    if len(nomes) == 2:
        return " e ".join(nomes)
    return f"{nomes[0]} et al."


@dataclass
class Fonte:
    chave: str
    autores: list[dict]
    titulo: str
    ano: int
    tipo: str
    subtema: Optional[str] = None
    sufixo: str = ""
    resumo: Optional[str] = None
    campos: dict = field(default_factory=dict)

    def ano_com_sufixo(self) -> str:
        return f"{self.ano}{self.sufixo}"


class FontesRegistry:
    def __init__(self):
        # (SOBRENOME, ano) -> lista de Fonte, na ordem em que foram registradas
        self._grupos: dict[tuple[str, int], list[Fonte]] = {}
        self._por_chave: dict[str, Fonte] = {}
        self.renomeacoes: list[dict] = []  # avisos de retro-desambiguação

    # ------------------------------------------------------------------ #
    def registrar(
        self,
        autores: list[dict],
        titulo: str,
        ano: int,
        tipo: str,
        subtema: str | None = None,
        pagina: str | None = None,
        resumo: str | None = None,
        **campos_extra,
    ) -> dict:
        """Registra uma fonte validada e devolve as formas de citação prontas para uso.

        `resumo` (opcional): 1-2 frases sobre por que esta fonte é relevante — vai
        direto para a coluna "Resumo/Relevância" da tabela de Registro das Fontes
        (Passo 3, elemento condicional de revisão bibliográfica). Registre no
        momento da validação, quando a relevância está fresca — não invente depois.
        """
        if tipo not in TIPOS_VALIDOS:
            raise ValueError(f"tipo inválido: {tipo!r} (use um de {sorted(TIPOS_VALIDOS)})")
        if not autores:
            raise ValueError("autores não pode ser vazio")

        sobrenome = _sobrenome_principal(autores)
        grupo_key = (sobrenome, ano)
        grupo = self._grupos.setdefault(grupo_key, [])

        if not grupo:
            sufixo = ""
        elif len(grupo) == 1 and grupo[0].sufixo == "":
            # segunda ocorrência do mesmo autor+ano: retroage sufixo "a" na primeira
            anterior = grupo[0]
            chave_antiga = anterior.chave
            anterior.sufixo = "a"
            anterior.chave = f"{sobrenome}{ano}a"
            del self._por_chave[chave_antiga]
            self._por_chave[anterior.chave] = anterior
            self.renomeacoes.append({
                "chave_antiga": chave_antiga,
                "chave_nova": anterior.chave,
                "aviso": "atualize citações já escritas no texto para esta nova chave",
            })
            sufixo = "b"
        else:
            sufixo = chr(ord("a") + len(grupo))

        chave = f"{sobrenome}{ano}{sufixo}"
        fonte = Fonte(
            chave=chave, autores=autores, titulo=titulo, ano=ano, tipo=tipo,
            subtema=subtema, sufixo=sufixo, resumo=resumo,
            campos={**campos_extra, **({"pagina": pagina} if pagina else {})},
        )
        grupo.append(fonte)
        self._por_chave[chave] = fonte

        return self._formas_citacao(fonte)

    # ------------------------------------------------------------------ #
    def _formas_citacao(self, fonte: Fonte) -> dict:
        ano_txt = fonte.ano_com_sufixo()
        autores_cit = _autores_citacao(fonte.autores)
        autores_sujeito = _autores_citacao_sujeito(fonte.autores)
        pagina = fonte.campos.get("pagina")
        sufixo_pagina = f", p. {pagina}" if pagina else ""
        return {
            "chave": fonte.chave,
            "citacao_parentese": f"({autores_cit}, {ano_txt}{sufixo_pagina})",
            "citacao_sujeito": f"{autores_sujeito} ({ano_txt})",
        }

    # ------------------------------------------------------------------ #
    def formatar_referencia(self, chave: str) -> str:
        fonte = self._por_chave[chave]
        return formatar_referencia(asdict(fonte))

    def listar_referencias_formatadas(self) -> list[str]:
        """Todas as referências, formatadas (NBR 6023) e ordenadas alfabeticamente pelo autor principal."""
        fontes_ordenadas = sorted(
            self._por_chave.values(),
            key=lambda f: (_sobrenome_principal(f.autores), f.ano, f.sufixo),
        )
        return [formatar_referencia(asdict(f)) for f in fontes_ordenadas]

    def listar_fichamento(self) -> list[dict]:
        """Uma linha por fonte, pronta para a tabela de Registro das Fontes
        (chave, autores formatados, ano, resumo) — mesma ordenação alfabética
        das referências."""
        fontes_ordenadas = sorted(
            self._por_chave.values(),
            key=lambda f: (_sobrenome_principal(f.autores), f.ano, f.sufixo),
        )
        return [
            {
                "chave": f.chave,
                "autores": _autores_referencia(f.autores),
                "ano": f.ano_com_sufixo(),
                "resumo": f.resumo or "",
            }
            for f in fontes_ordenadas
        ]

    # ------------------------------------------------------------------ #
    def persistir(self, caminho: str | Path) -> None:
        dados = {
            "fontes": [asdict(f) for f in self._por_chave.values()],
            "renomeacoes": self.renomeacoes,
        }
        Path(caminho).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def carregar(cls, caminho: str | Path) -> "FontesRegistry":
        dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
        registry = cls()
        for f in dados.get("fontes", []):
            fonte = Fonte(**f)
            registry._por_chave[fonte.chave] = fonte
            grupo_key = (_sobrenome_principal(fonte.autores), fonte.ano)
            registry._grupos.setdefault(grupo_key, []).append(fonte)
        registry.renomeacoes = dados.get("renomeacoes", [])
        return registry


# ---------------------------------------------------------------------- #
# Formatação NBR 6023 pura (não depende do registro — usável isoladamente)
# ---------------------------------------------------------------------- #
def formatar_referencia(fonte: dict) -> str:
    """Formata uma fonte (dict com autores/titulo/ano/tipo/campos) conforme NBR 6023."""
    tipo = fonte["tipo"]
    autores_txt = _autores_referencia(fonte["autores"])
    titulo = fonte["titulo"]
    ano = fonte["ano"]
    c = fonte.get("campos", {})

    if tipo == "periodico":
        partes = [f"{autores_txt}. {titulo}. {c.get('periodico', '')}"]
        loc = c.get("local")
        if loc:
            partes.append(f", {loc}")
        v = c.get("volume")
        n = c.get("numero")
        vn = []
        if v:
            vn.append(f"v. {v}")
        if n:
            vn.append(f"n. {n}")
        if vn:
            partes.append(f", {', '.join(vn)}")
        if c.get("paginas"):
            partes.append(f", p. {c['paginas']}")
        partes.append(f", {ano}.")
        return "".join(partes)

    if tipo == "livro":
        edicao = f" {c['edicao']}." if c.get("edicao") else ""
        return f"{autores_txt}. {titulo}.{edicao} {c.get('local', '')}: {c.get('editora', '')}, {ano}."

    if tipo == "capitulo":
        org = c.get("organizador", "")
        return (
            f"{autores_txt}. {titulo}. In: {org} (org.). {c.get('titulo_livro', '')}. "
            f"{c.get('local', '')}: {c.get('editora', '')}, {ano}. p. {c.get('paginas', '')}."
        )

    if tipo in ("dissertacao", "tese"):
        grau = "Dissertação (Mestrado" if tipo == "dissertacao" else "Tese (Doutorado"
        area = c.get("area")
        grau += f" em {area})" if area else ")"
        folhas = f" {c['folhas']} f." if c.get("folhas") else ""
        return (
            f"{autores_txt}. {titulo}. {ano}.{folhas} {grau} – "
            f"{c.get('instituicao', '')}, {c.get('local', '')}, {ano}."
        )

    if tipo == "anais":
        return (
            f"{autores_txt}. {titulo}. In: {c.get('evento', '')}, {c.get('numero_evento', '')}., "
            f"{ano}, {c.get('local', '')}. Anais [...]. {c.get('local', '')}: {c.get('editora', '')}, "
            f"{ano}. p. {c.get('paginas', '')}."
        )

    if tipo == "eletronico":
        acesso = c.get("acesso", "")
        return (
            f"{autores_txt}. {titulo}. {c.get('local', '')}: {c.get('instituicao', '')}, {ano}. "
            f"Disponível em: {c.get('url', '')}. Acesso em: {acesso}."
        )

    raise ValueError(f"tipo inválido: {tipo!r}")

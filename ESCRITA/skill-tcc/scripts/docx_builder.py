"""
docx_builder.py — monta o .docx do projeto de pesquisa (NBR 15287:2025)
a partir de um `spec` (dict) com o conteúdo já decidido/escrito pela LLM.

Números de seção e de lista são texto estático (calculado por
`numeracao.py` e pelo próprio spec) — não há dependência de numeração
automática do Word em nenhum lugar deste módulo.

`build_document()` é usado em duas passadas por `paginacao_sumario.py`:
  - passada 1 (rascunho): sumario_paginas=None, pagina_inicio_corpo=None
  - passada 2 (final): ambos preenchidos com os valores reais calculados
"""
from __future__ import annotations

from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from numeracao import numerar_secoes
from cronograma import gerar_colunas, montar_tabela

FONT = "Times New Roman"
SIZE = Pt(12)
SIZE_SMALL = Pt(10)
BLACK = RGBColor(0, 0, 0)


# --------------------------------------------------------------------- #
# Helpers de formatação de texto (reaproveitados por quem precisar casar
# com o texto exato renderizado, ex.: paginacao_sumario.py)
# --------------------------------------------------------------------- #
def heading1_text(secao: dict) -> str:
    return secao["titulo_numerado"].upper()


def heading2_text(sub: dict) -> str:
    return sub["titulo_numerado"]


def referencias_heading_text() -> str:
    return "REFERÊNCIAS"


# --------------------------------------------------------------------- #
def _set_estilo_padrao(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = SIZE
    normal.font.color.rgb = BLACK
    normal.paragraph_format.line_spacing = 1.5
    # garante a fonte também para runs do Complex Script / East Asian
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), FONT)


def _config_pagina(section) -> None:
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(3)
    section.left_margin = Cm(3)
    section.bottom_margin = Cm(2)
    section.right_margin = Cm(2)


def _paragrafo_centralizado(doc, texto, negrito=False, tamanho=SIZE, espaco_antes=0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if espaco_antes:
        p.paragraph_format.space_before = Pt(espaco_antes)
    run = p.add_run(texto)
    run.font.name = FONT
    run.font.size = tamanho
    run.bold = negrito
    run.font.color.rgb = BLACK
    return p


def _corpo(doc, texto, justificar=True):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if justificar else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(texto)
    run.font.name = FONT
    run.font.size = SIZE
    run.font.color.rgb = BLACK
    return p


def _heading1(doc, texto):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(texto)
    run.font.name = FONT
    run.font.size = SIZE
    run.bold = True
    run.font.color.rgb = BLACK
    return p


def _heading2(doc, texto):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(texto)
    run.font.name = FONT
    run.font.size = SIZE
    run.bold = True
    run.font.color.rgb = BLACK
    return p


def _item_numerado(doc, numero, texto):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.25)
    p.paragraph_format.first_line_indent = Cm(-1.25)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(f"{numero}. {texto}")
    run.font.name = FONT
    run.font.size = SIZE
    run.font.color.rgb = BLACK
    return p


def _linha_sumario(doc, texto, pagina):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    run = p.add_run(f"{texto}\t{pagina if pagina is not None else ''}")
    run.font.name = FONT
    run.font.size = SIZE
    run.font.color.rgb = BLACK
    return p


def _quebra_pagina(doc):
    doc.add_page_break()


def _nova_secao_com_footer(doc, pagina_inicio: int):
    """Cria uma nova seção (nova página) com footer numerando a partir de `pagina_inicio`."""
    from docx.enum.section import WD_SECTION

    nova = doc.add_section(WD_SECTION.NEW_PAGE)
    _config_pagina(nova)

    # w:pgNumType/@w:start no sectPr desta seção
    sect_pr = nova._sectPr
    pg_num_type = sect_pr.find(qn("w:pgNumType"))
    if pg_num_type is None:
        pg_num_type = OxmlElement("w:pgNumType")
        sect_pr.append(pg_num_type)
    pg_num_type.set(qn("w:start"), str(pagina_inicio))

    footer = nova.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run()
    run.font.name = FONT
    run.font.size = SIZE_SMALL
    run.font.color.rgb = BLACK
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)
    return nova


def _tabela_cronograma(doc, cronograma_spec: dict):
    colunas = gerar_colunas(cronograma_spec["duracao_meses"], cronograma_spec["granularidade"])
    tabela_dados = montar_tabela(cronograma_spec["atividades"], cronograma_spec["marcacoes"], colunas)

    largura_atividade = Cm(6.0)
    n_col = len(colunas)
    largura_periodo = Cm(min(2.0, 10.0 / max(n_col, 1)))

    table = doc.add_table(rows=1, cols=1 + n_col)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    header_cells = table.rows[0].cells
    _preencher_celula(header_cells[0], "Atividade", largura_atividade, negrito=True, centralizado=False)
    for j, col in enumerate(colunas):
        _preencher_celula(header_cells[1 + j], col, largura_periodo, negrito=True, centralizado=True)

    for linha in tabela_dados["linhas"]:
        row_cells = table.add_row().cells
        _preencher_celula(row_cells[0], linha["atividade"], largura_atividade, centralizado=False)
        for j, marcado in enumerate(linha["marcado"]):
            _preencher_celula(row_cells[1 + j], "X" if marcado else "", largura_periodo, centralizado=True)

    # largura precisa ser fixada em TODA célula de TODA linha (gotcha do python-docx,
    # análogo ao columnWidths do docx-js) — reforça mais uma vez percorrendo a tabela inteira
    larguras = [largura_atividade] + [largura_periodo] * n_col
    for row in table.rows:
        for cell, largura in zip(row.cells, larguras):
            cell.width = largura
    return table


def _preencher_celula(cell, texto, largura, negrito=False, centralizado=False):
    cell.width = largura
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if centralizado else WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(texto)
    run.font.name = FONT
    run.font.size = SIZE_SMALL
    run.bold = negrito
    run.font.color.rgb = BLACK


def _fluxo_conceitual(doc, texto):
    """Modelo conceitual: cadeia sequencial (ex.: 'Frontend → API → Banco de Dados'),
    centralizada, fonte monoespaçada, preservando as setas literalmente."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(texto)
    run.font.name = "Courier New"
    run.font.size = SIZE
    run.font.color.rgb = BLACK
    return p


def _tabela_fichamento(doc, fichamento: list[dict]):
    """Registro das fontes: tabela com cabeçalho fixo (Fonte, Autor(es), Ano, Resumo/Relevância),
    uma linha por fonte já registrada em fontes.json — ou uma linha-molde em branco se `fichamento`
    vier vazio, pronta para o usuário duplicar."""
    colunas = [("Fonte", Cm(2.2)), ("Autor(es)", Cm(3.5)), ("Ano", Cm(1.3)), ("Resumo/Relevância", Cm(6.5))]
    table = doc.add_table(rows=1, cols=len(colunas))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    header_cells = table.rows[0].cells
    for j, (nome, largura) in enumerate(colunas):
        _preencher_celula(header_cells[j], nome, largura, negrito=True, centralizado=(nome == "Ano"))

    linhas = fichamento if fichamento else [{"chave": "", "autores": "", "ano": "", "resumo": ""}]
    for item in linhas:
        row_cells = table.add_row().cells
        _preencher_celula(row_cells[0], item.get("chave", ""), colunas[0][1])
        _preencher_celula(row_cells[1], item.get("autores", ""), colunas[1][1])
        _preencher_celula(row_cells[2], str(item.get("ano", "")), colunas[2][1], centralizado=True)
        _preencher_celula(row_cells[3], item.get("resumo", ""), colunas[3][1])

    larguras = [c[1] for c in colunas]
    for row in table.rows:
        for cell, largura in zip(row.cells, larguras):
            cell.width = largura
    return table


def _folha_aprovacao(doc, meta):
    """Folha de aprovação (NBR 14724:2024, elemento pré-textual obrigatório para
    trabalho acadêmico finalizado — monografia/artigo, não para projeto de pesquisa).
    Espaço para assinatura da banca fica em branco — só se preenche após a defesa."""
    _paragrafo_centralizado(doc, meta["autor"], espaco_antes=40)
    _paragrafo_centralizado(doc, meta["titulo"], negrito=True, tamanho=Pt(14), espaco_antes=40)
    natureza = {
        "tcc_monografia": "Trabalho de Conclusão de Curso, em formato de monografia",
        "tcc_artigo": "Trabalho de Conclusão de Curso, em formato de artigo científico",
    }.get(meta.get("tipo_projeto"), "Trabalho de Conclusão de Curso")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.left_indent = Cm(8)
    p.paragraph_format.space_before = Pt(40)
    run = p.add_run(
        f'{natureza} apresentado ao Curso de {meta.get("curso") or meta.get("programa", "")} '
        f'da {meta["instituicao"]} como requisito parcial para obtenção do grau de graduado, '
        f'aprovado pela banca examinadora composta pelos membros abaixo.'
    )
    run.font.name, run.font.size, run.font.color.rgb = FONT, SIZE, BLACK
    _paragrafo_centralizado(doc, f'Aprovado em: ____/____/______', espaco_antes=100)
    for papel in ("Orientador(a)", "Membro da banca", "Membro da banca"):
        _paragrafo_centralizado(doc, "_" * 40, espaco_antes=70)
        _paragrafo_centralizado(doc, papel)
    _quebra_pagina(doc)


def _bloco_resumo(doc, titulo, texto, palavras_chave, rotulo_palavras_chave):
    """Um bloco de resumo (NBR 6028): parágrafo único justificado, sem recuo de
    primeira linha, seguido da linha de palavras-chave."""
    _heading1(doc, titulo)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(12)
    run = p.add_run(texto)
    run.font.name, run.font.size, run.font.color.rgb = FONT, SIZE, BLACK

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    termos = "; ".join(palavras_chave)
    run2 = p2.add_run(f"{rotulo_palavras_chave}: {termos}.")
    run2.font.name, run2.font.size, run2.font.color.rgb = FONT, SIZE, BLACK


def _resumo_bilingue(doc, resumo: dict, quebrar_pagina: bool = True):
    """Resumo (NBR 6028, obrigatório em português) + Abstract (obrigatório em
    língua estrangeira desde a NBR 14724:2024) — só para trabalho finalizado.
    `quebrar_pagina=False` mantém os dois blocos na mesma página (uso em artigo,
    onde título+autor+resumo+abstract cabem juntos na primeira página)."""
    pt = resumo.get("pt", {})
    if pt:
        _bloco_resumo(doc, "RESUMO", pt.get("texto", ""), pt.get("palavras_chave", []), "Palavras-chave")
        if quebrar_pagina:
            _quebra_pagina(doc)
    en = resumo.get("en", {})
    if en:
        _bloco_resumo(doc, "ABSTRACT", en.get("texto", ""), en.get("palavras_chave", []), "Keywords")
        if quebrar_pagina:
            _quebra_pagina(doc)


def _adicionar_footer_pagina(section):
    """Numeração de página simples na seção default — sem valor de início customizado,
    porque um artigo não tem pré-textual a descontar (a numeração já começa em 1 de verdade)."""
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run()
    run.font.name = FONT
    run.font.size = SIZE_SMALL
    run.font.color.rgb = BLACK
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)


def _pretextual_artigo(doc, spec, meta):
    """Pré-textual de artigo científico (NBR 6022) — sem capa, folha de rosto ou
    folha de aprovação: título, autor(es) com afiliação, Resumo/Abstract, tudo na
    mesma página inicial, sem quebras de página forçadas entre os blocos."""
    _paragrafo_centralizado(doc, meta["titulo"], negrito=True, tamanho=Pt(14))
    _paragrafo_centralizado(doc, meta["autor"], espaco_antes=120)
    afiliacao = f'{meta.get("curso") or meta.get("programa", "")}, {meta["instituicao"]}'
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(afiliacao)
    run.font.name, run.font.size, run.font.color.rgb = FONT, SIZE_SMALL, BLACK
    run.italic = True
    if meta.get("orientador"):
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run2 = p2.add_run(f'Orientador(a): {meta["orientador"]}')
        run2.font.name, run2.font.size, run2.font.color.rgb = FONT, SIZE_SMALL, BLACK
        run2.italic = True
    if spec.get("resumo"):
        _resumo_bilingue(doc, spec["resumo"], quebrar_pagina=False)


# --------------------------------------------------------------------- #
def build_document(spec: dict, sumario_paginas: dict | None = None, pagina_inicio_corpo: int | None = None) -> Document:
    doc = Document()
    _set_estilo_padrao(doc)
    _config_pagina(doc.sections[0])

    meta = spec["metadata"]
    curso_ou_programa = meta.get("curso") or meta.get("programa", "")
    eh_artigo = meta.get("tipo_projeto") == "tcc_artigo"

    if eh_artigo:
        # --- Artigo científico (NBR 6022) — sem capa, folha de rosto, folha de
        # aprovação ou sumário: título+autor+resumo/abstract na 1ª página, direto
        # para o corpo. Paginação simples (sem pré-textual a descontar). ---
        _pretextual_artigo(doc, spec, meta)
        _adicionar_footer_pagina(doc.sections[0])
        secoes_numeradas = numerar_secoes(spec["secoes"])
    else:
        # --- Capa -----------------------------------------------------------
        _paragrafo_centralizado(doc, f'{meta["instituicao"]} — Curso de {curso_ou_programa}')
        _paragrafo_centralizado(doc, meta["titulo"], negrito=True, tamanho=Pt(16), espaco_antes=120)
        _paragrafo_centralizado(doc, meta["autor"], espaco_antes=180)
        _paragrafo_centralizado(doc, meta["cidade"], espaco_antes=180)
        _paragrafo_centralizado(doc, str(meta["ano"]))
        _quebra_pagina(doc)

        # --- Folha de rosto ---------------------------------------------------
        _paragrafo_centralizado(doc, meta["autor"], espaco_antes=60)
        _paragrafo_centralizado(doc, meta["titulo"], negrito=True, tamanho=Pt(14), espaco_antes=40)
        tipo_txt = {
            "tcc_monografia": "elaboração do Trabalho de Conclusão de Curso, em formato de monografia",
            "projeto_pesquisa_tcc": "aprovação do projeto de pesquisa do Trabalho de Conclusão de Curso",
        }.get(meta.get("tipo_projeto"), meta.get("tipo_projeto_label", "elaboração do Trabalho de Conclusão de Curso"))
        linha_txt = f', na linha de pesquisa {meta["linha_pesquisa"]}' if meta.get("linha_pesquisa") else ""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.left_indent = Cm(8)
        p.paragraph_format.space_before = Pt(40)
        run = p.add_run(
            f'Projeto de pesquisa apresentado ao Curso de {curso_ou_programa} da {meta["instituicao"]}, '
            f'como requisito parcial para {tipo_txt}{linha_txt}.'
        )
        run.font.name, run.font.size, run.font.color.rgb = FONT, SIZE, BLACK
        if meta.get("orientador"):
            p2 = doc.add_paragraph()
            p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p2.paragraph_format.left_indent = Cm(8)
            p2.paragraph_format.space_before = Pt(20)
            run2 = p2.add_run(f'Orientador(a): {meta["orientador"]}')
            run2.font.name, run2.font.size, run2.font.color.rgb = FONT, SIZE, BLACK
        _paragrafo_centralizado(doc, meta["cidade"], espaco_antes=200)
        _paragrafo_centralizado(doc, str(meta["ano"]))
        _quebra_pagina(doc)

        # --- Folha de Aprovação + Resumo/Abstract (NBR 14724) — só p/ monografia ---
        if meta.get("tipo_projeto") == "tcc_monografia":
            _folha_aprovacao(doc, meta)
            if spec.get("resumo"):
                _resumo_bilingue(doc, spec["resumo"])

        # --- Sumário ------------------------------------------------------
        secoes_numeradas = numerar_secoes(spec["secoes"])
        _heading1(doc, "SUMÁRIO")
        for secao in secoes_numeradas:
            titulo = heading1_text(secao)
            pagina = sumario_paginas.get(titulo) if sumario_paginas else None
            _linha_sumario(doc, titulo, pagina)
        pagina_ref = sumario_paginas.get(referencias_heading_text()) if sumario_paginas else None
        _linha_sumario(doc, referencias_heading_text(), pagina_ref)

        # --- Corpo (elementos textuais) — nova seção para paginação --------
        if pagina_inicio_corpo is not None:
            _nova_secao_com_footer(doc, pagina_inicio_corpo)
        else:
            _quebra_pagina(doc)

    for secao in secoes_numeradas:
        _heading1(doc, heading1_text(secao))
        for paragrafo in secao.get("paragrafos", []):
            _corpo(doc, paragrafo)
        if secao["titulo"].strip().lower() == "modelo conceitual" and secao.get("fluxo"):
            _fluxo_conceitual(doc, secao["fluxo"])
        for i, item in enumerate(secao.get("lista_numerada", []), start=1):
            _item_numerado(doc, i, item)
        for sub in secao.get("subsecoes", []):
            _heading2(doc, heading2_text(sub))
            for paragrafo in sub.get("paragrafos", []):
                _corpo(doc, paragrafo)
        if secao["titulo"].strip().lower() in ("cronograma",) and spec.get("cronograma"):
            _tabela_cronograma(doc, spec["cronograma"])
        if secao["titulo"].strip().lower() in ("registro das fontes", "ficha de registro de fontes"):
            _tabela_fichamento(doc, spec.get("fichamento", []))

    # --- Referências ------------------------------------------------------
    _heading1(doc, referencias_heading_text())
    for ref in spec.get("referencias_formatadas", []):
        _corpo(doc, ref, justificar=False)

    return doc

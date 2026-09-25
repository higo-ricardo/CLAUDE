# Arquitetura Python — implementada (exceto o CLI orquestrador)

Este README registra o pacote Python (`python-docx`) que separa o que é **determinístico** (script, testável e sem ambiguidade) do que é **não-determinístico** (fica a cargo da LLM/agentes, ver `../agents/README.md`). Testado módulo a módulo com `soffice`+`pdftotext` (conversão real pra PDF e checagem visual/textual) durante a implementação.

```
scripts/
├── fontes_registry.py     # registro incremental de fontes (chamado no Passo 2)
├── numeracao.py            # NBR 6024 — numeração progressiva de seções
├── cronograma.py            # gera colunas (mensal/semestral) e a tabela final
├── docx_builder.py         # monta capa, folha de rosto, corpo, tabela, referências
├── paginacao_sumario.py    # pipeline de 2 passadas p/ sumário e paginação reais
├── validar_abnt.py         # audita o .docx final (margens, fonte, espaçamento)
├── validar_ciclo_pesquisa.py  # gate do piso de busca (Passo 2)
└── gerar_projeto.py         # CLI que orquestra tudo a partir de um spec.json
```

## Responsabilidade de cada script

- **`fontes_registry.py`** — a LLM chama isso durante o Passo 2, uma vez por fonte validada: recebe autor/título/ano/tipo, devolve a chave de citação já correta (com sufixo a/b/c se houver outro autor+ano igual) e persiste em `fontes.json`. A LLM só insere essa chave devolvida na prosa — não formata NBR 10520 na cabeça. Expõe `formatar_referencia()` (NBR 6023) e `formatar_citacao()` (NBR 10520) como funções puras testáveis por tipo de fonte (periódico, livro, capítulo, dissertação/tese, anais, eletrônico).
- **`numeracao.py`** — NBR 6024: dado uma árvore `[{titulo, nivel, subsecoes:[...]}]`, devolve os títulos já prefixados (ex.: `"3.1 Relevância Científica"`), sem depender de heading style automático do Word.
- **`cronograma.py`** — dado duração (meses) + granularidade (mensal/semestral), gera os cabeçalhos de coluna; dado atividades+marcações já decididas pela LLM, gera a matriz da tabela final.
- **`docx_builder.py`** — monta capa, folha de rosto, corpo (numerado via `numeracao.py`), tabela de cronograma (via `cronograma.py`) e lista de referências (ordenada e formatada via `fontes_registry.py`), usando números de seção/lista como texto estático em vez de numeração automática do Word.
- **`paginacao_sumario.py`** — pipeline de duas passadas: gera rascunho → converte para PDF via `soffice` → localiza a página real de cada heading (`pdftotext`/`pdfplumber`) → regenera o documento final com sumário e paginação corretos (contagem a partir da folha de rosto, número visível só a partir da Introdução).
- **`validar_abnt.py`** — abre o `.docx` final e confere margens (3/2/2/3cm), fonte/tamanho, espaçamento 1,5, larguras de tabela — relatório de conformidade automático antes de apresentar ao usuário.
- **`validar_ciclo_pesquisa.py`** — lê um `buscas_log.json` (sub-tema → queries feitas) + `fontes.json`, aplica o piso de 2-3 buscas / 3-5 fontes por sub-tema, devolve relatório pass/fail por sub-tema — gate mecânico antes de avançar ao Passo 3.
- **`gerar_projeto.py`** — CLI única: recebe um `spec.json` (metadata, seções com texto já escrito pela LLM, cronograma decidido, lista de fontes) e devolve o `.docx` final, rodando `validar_abnt.py` internamente.

## Análise do workflow — determinístico vs. não-determinístico

| Etapa do SKILL.md | Natureza | Por quê |
|---|---|---|
| Elicitação (tema, programa, duração, idioma, edital) | **Não-determinístico** | Requer entender linguagem natural e decidir o que perguntar |
| Detectar tema amplo + propor 2-3 recortes | **Não-determinístico** | Julgamento de domínio — não há regra fixa pra "isso é amplo demais" |
| Formular perguntas-chave e dividir em sub-temas | **Não-determinístico** | Depende do conteúdo do tema |
| Executar `web_search`/`web_fetch`, decidir relevância | **Não-determinístico** (a decisão) / a chamada em si é I/O, não lógica a codificar | Julgar se uma fonte é boa é semântico |
| Comparar fontes, identificar lacunas, validar afirmações | **Não-determinístico** | Julgamento acadêmico |
| Contar buscas/fontes por sub-tema e aplicar o piso (2-3 / 3-5) | **Determinístico** | É uma contagem sobre dados estruturados — hoje isso é "autoavaliação" da LLM, pode virar gate mecânico |
| Escrever Introdução, Problema, Justificativa, Objetivos, Hipóteses, Fundamentação, Metodologia | **Não-determinístico** | Redação argumentativa — é o produto intelectual do projeto |
| Escolher DSR vs. outra metodologia | **Não-determinístico** | Julgamento sobre o objeto de estudo |
| Decidir quais atividades entram no cronograma e quando | **Não-determinístico** | Julgamento sobre o plano de trabalho |
| Formatar referência (NBR 6023) dado autor/título/ano/tipo | **Determinístico** | É uma regra fixa por tipo de fonte |
| Formatar citação em texto (NBR 10520), incl. "et al." a partir de 3 autores, sufixo a/b/c pra mesmo autor+ano | **Determinístico** | Regra fixa — hoje a LLM formata "na mão" e pode errar |
| Numeração progressiva das seções (NBR 6024) | **Determinístico** | Dado um esqueleto de seções/subseções, a numeração é mecânica |
| Renderizar tabela de cronograma dado atividades+marcações já decididas | **Determinístico** | Só rendering, a decisão já foi tomada |
| Montar capa/folha de rosto/margens/fontes/espaçamento | **Determinístico** | Regras fixas da NBR 15287:2025 |
| Calcular sumário com números de página reais e paginação só a partir da Introdução | **Determinístico** — implementado via pipeline de 2 passadas (`paginacao_sumario.py`) | Antes era chute estático; agora renderiza um rascunho, localiza a página real de cada heading via `pdftotext` e regenera o final |
| Auditar o .docx final (margens, fonte, espaçamento, largura de tabela) | **Determinístico** | É verificação mecânica contra números fixos |
| Slug do nome do arquivo | **Determinístico** | Função pura |

## Nota de trade-off

A skill pública `docx` do ambiente recomenda `docx-js` (npm) por ter suporte nativo mais maduro para numeração de lista e TOC. A forma de neutralizar essa desvantagem ao migrar para `python-docx` é não depender de numeração automática do Word em nenhum lugar: números de seção, de lista e de página do sumário saem todos como texto/valor já calculado pelo script, não como campo dinâmico do Word — mais simples e mais determinístico do que manipular `numbering.xml`/campos TOC via XML bruto.

**Status:** `fontes_registry.py`, `numeracao.py`, `cronograma.py`, `docx_builder.py`, `paginacao_sumario.py`, `validar_abnt.py` e `validar_ciclo_pesquisa.py` implementados e testados isoladamente (geração real de .docx, conversão pra PDF, extração de texto por página). **Pendente:** `gerar_projeto.py` (o CLI que orquestra tudo a partir de um `spec.json` + `fontes.json`) — ainda não implementado; depende do formato final do `spec.json` que o Agente Redator vai produzir (ver `../agents/README.md`).

---
name: skill-tcc
description: Conduz um ciclo real de pesquisa (1 a 3 sub-temas, 2 a 4 fontes validadas por sub-tema) e a partir dele gera um Trabalho de Conclusão de Curso em .docx — monografia, artigo científico, ou projeto de pesquisa de TCC, a critério do usuário — formatado pela ABNT NBR 15287:2025 e normas correlatas (NBR 6023 referências, NBR 10520 citações, NBR 6027 sumário). Use sempre que o usuário pedir para criar, estruturar ou pesquisar um TCC, TFC, monografia, artigo de graduação ou projeto de pesquisa de curso, mesmo sem dizer "TCC" — gatilhos incluem problema de pesquisa, objetivos, justificativa acadêmica, tags de busca, critérios de exclusão, protocolo de seleção de fontes, fichamento, modelo conceitual ou orientador de graduação.
---

# Skill TCC — Trabalho de Conclusão de Curso em .docx

Esta skill transforma um tema — às vezes só uma frase, às vezes já um rascunho — em um TCC completo: monografia, artigo científico, ou projeto de pesquisa, conforme o usuário preferir. Assim como em `skill-mestrado` (da qual esta skill herda a arquitetura), o conteúdo não pode vir só da cabeça de quem escreve — problema de pesquisa, justificativa e fundamentação teórica precisam estar ancorados no que a literatura de fato diz, o que só se descobre pesquisando com múltiplas buscas e comparação entre fontes, não com uma única busca solta.

O piso de pesquisa aqui é mais leve que o de mestrado, proporcional ao escopo de graduação: **1 a 3 sub-temas no total, 2 a 4 fontes validadas por sub-tema**. Se o usuário quiser o rigor mais pesado de mestrado/doutorado (mais sub-temas, mais fontes, trilha DSR completa), prefira `skill-mestrado`.

O princípio que guia tudo aqui: **um TCC não é uma lista de seções preenchidas isoladamente**. Cada elemento estruturante (objetivos, critérios, tags de busca) deve se conectar explicitamente ao problema de pesquisa. Se ao definir uma tag de busca ou um critério você não conseguir explicar por que ele ajuda a responder ao problema de pesquisa, ele não pertence ao escopo do trabalho.

## Visão geral do fluxo

1. **Elicitação** — tema, o que já existe, a variação de entrega (monografia, artigo, ou projeto de pesquisa), e a metodologia pretendida.
2. **Ciclo de pesquisa** — 1 a 3 sub-temas, 2 a 4 fontes validadas cada, com o piso conferido mecanicamente.
3. **Elementos estruturantes** — problema, justificativa, objetivos, metodologia, e os blocos condicionais que dependem dela (tags de busca, modelo conceitual, DSR, etc.).
4. **Geração do documento** — `.docx` único, formatado pela NBR 15287:2025.

Trate isso como um processo iterativo de plano-confirma-implementa: depois do ciclo de pesquisa, mostre ao usuário um resumo do que foi encontrado antes de escrever o documento inteiro.

## Orquestração multi-agente

| Papel | Cobre | Arquivo | Produz |
|---|---|---|---|
| Agente Elicitador | Passo 1 | `agents/elicitador.md` | `elicitacao.json` |
| Agente Pesquisador | Passo 2 | `agents/pesquisador.md` | `buscas_log.json`, `fontes.json`, `mapa_lacunas.json` |
| Agente Redator | Passos 3-4 | `agents/redator.md` | `spec.json` |

O Passo 5 (formatação/geração do `.docx`) é **determinístico** — `scripts/gerar_projeto.py` (ver `scripts/README.md`), não um agente.

Se o ambiente suportar spawn de subagente, invoque cada papel como uma tarefa separada. Se não, leia o `agents/<papel>.md` da fase antes de começá-la e siga como troca de papel na mesma thread. Antes de avançar do Pesquisador para o Redator, rode `scripts/validar_ciclo_pesquisa.py`; se o piso não for atingido em algum sub-tema, volte só para esses sub-temas. Diagrama completo e schemas em `agents/README.md` e `template/`.

## Passo 1 — Elicitação inicial (Agente Elicitador)

Extraia da conversa (ou pergunte o que faltar):

- **Tema** — já delimitado ou ainda amplo? Se amplo, proponha 2-3 recortes e pergunte qual o usuário prefere, como em `skill-mestrado` — não decida sozinho.
- **Variação de entrega, a critério do usuário** — monografia tradicional, artigo científico formatado como TCC, ou apenas o projeto de pesquisa (proposta, sem capítulos de resultado)? Pergunte explicitamente se não estiver claro; isso muda o `tipo_projeto` em `elicitacao.json` (`tcc_monografia`, `tcc_artigo`, `projeto_pesquisa_tcc`) e o texto da folha de rosto.
- **Se a variação for monografia/artigo (trabalho finalizado): pergunte se o usuário já tem os resultados/achados prontos** (dados coletados, protótipo testado, análise feita) **antes de assumir esse `tipo_projeto`.** Resultados e Discussão relatam algo que já aconteceu — a skill nunca inventa nem pesquisa esse conteúdo no lugar do usuário. Se o usuário ainda não tem resultados, oriente que `projeto_pesquisa_tcc` (proposta) é o formato correto por enquanto, e a monografia/artigo final vem depois, quando houver o que relatar.
- **Já existe um problema de pesquisa** definido, ou é preciso ajudar a formulá-lo a partir do tema?
- **Metodologia pretendida** — bibliográfica/revisão de literatura, estudo de caso, pesquisa de campo, pesquisa-ação, experimental, Design Science Research (se o objeto for um artefato técnico a construir), ou combinação. Se o usuário não souber, ajude a decidir com base no tipo de pergunta de pesquisa (ver `references/metodologias-tcc.md`).
- **O objeto de estudo é um processo, sistema ou fluxo** (ex.: uma requisição HTTP, um pipeline, um algoritmo)? Se sim, o documento terá um Modelo Conceitual.
- **Curso, instituição, orientador, cidade, ano, duração** (tipicamente 1-2 semestres, não os 24+ meses de um mestrado) — para a folha de rosto e o cronograma.
- **Idioma das buscas** — só português, ou português + inglês.

Se o usuário já mandou um arquivo, rascunho ou conversa anterior com essas informações, extraia o que puder de lá antes de perguntar.

## Passo 2 — Ciclo de pesquisa (Agente Pesquisador)

1. **Define o que precisa descobrir** — 2-4 perguntas-chave a partir do tema.
2. **Divide em 1 a 3 sub-temas** — não mais que isso; se o tema exigir mais de 3 frentes, é sinal de que o recorte do Passo 1 ficou amplo demais para escopo de TCC.
3. **Pesquisa múltiplas fontes por sub-tema** — no mínimo 1 busca (`web_search`), reformulando se necessário, até reunir **2 a 4 fontes validadas**. Use o idioma definido no Passo 1. Priorize artigos, TCCs/monografias similares e revisões recentes.
4. **Usa `web_fetch`** antes de citar qualquer fonte.
5. **Compara, identifica lacunas** — onde a literatura levantada diverge ou deixa algo em aberto.
6. **Valida** — a cada fonte aceita, registre via `scripts/fontes_registry.py` (`FontesRegistry.registrar(...)`), incluindo um `resumo` de 1-2 frases (isso alimenta a tabela de fichamento automaticamente, sem trabalho manual depois).
7. **Roda `scripts/validar_ciclo_pesquisa.py`** antes de prosseguir — só avance com `"ok": true`.

Nunca reproduza trechos longos das fontes; parafraseie, e nunca invente uma citação ou fonte que não foi de fato consultada.

## Passo 3 — Elementos estruturantes universais (Agente Redator)

Estes blocos aparecem em praticamente qualquer TCC, independentemente da metodologia:

1. **Título** — deixa claro o recorte do trabalho, não só o tema geral.
2. **Problema de pesquisa** — uma pergunta, ancorada em uma lacuna de `mapa_lacunas.json`.
3. **Justificativa**:
   - *Relevância Acadêmica* — a lacuna conceitual encontrada;
   - *Relevância Prática e Didática* — a quem serve fora da academia;
   - *Originalidade e Contribuição* — o que diferencia esta abordagem.
4. **Objetivo geral** — uma frase, amarrada ao problema de pesquisa.
5. **Objetivos específicos** — 3 a 5 ações verificáveis (descrever, identificar, explicar, demonstrar, comparar, avaliar...).
6. **Metodologia** — o tipo de pesquisa e por que é adequado ao problema (ver `references/metodologias-tcc.md`).

## Passo 4 — Elementos condicionais (Agente Redator)

| Condição | Blocos a incluir |
|---|---|
| `tipo_projeto` = `tcc_monografia` (trabalho **finalizado**, NBR 14724:2024) | Capa, Folha de Rosto, Folha de Aprovação, Resumo/Abstract (NBR 6028), Sumário; **Resultados e Discussão + Conclusão** no lugar de Cronograma |
| `tipo_projeto` = `tcc_artigo` (trabalho **finalizado**, NBR 6022) | **Sem** Capa, Folha de Rosto, Folha de Aprovação nem Sumário — só título+autor+afiliação+Resumo/Abstract na 1ª página, direto pro corpo; **Resultados e Discussão + Conclusão** no lugar de Cronograma; dobre a Fundamentação Teórica dentro da Introdução em vez de seção própria (artigo não costuma ter capítulo de revisão separado) |
| `tipo_projeto` = `projeto_pesquisa_tcc` (proposta, NBR 15287:2025) | Capa, Folha de Rosto, Sumário; Cronograma normal (ver Passo 5); sem Resultados/Conclusão/Resumo/Folha de Aprovação — a pesquisa ainda não foi feita |
| Metodologia = revisão bibliográfica | Tags de Busca, Critérios de Exclusão, Estrutura Proposta da Revisão, Protocolo de Seleção das Fontes, Registro das Fontes (fichamento — gerado automaticamente, ver Passo 5) |
| Objeto de estudo é um processo/sistema/fluxo | Modelo Conceitual (`secao["fluxo"]`, ver `SKILL.md` → `scripts/docx_builder.py`) |
| Objeto de estudo é um artefato técnico a construir | Trilha Design Science Research em vez de estudo de caso/experimental — ver `references/metodologias-tcc.md` |
| Metodologia = estudo de caso / pesquisa de campo / pesquisa-ação / experimental | Ver seção correspondente em `references/metodologias-tcc.md` |
| Metodologias combinadas | Seção própria de "Integração Metodológica" — ver `references/metodologias-tcc.md` |

**Regra dura para Resultados e Discussão**: este bloco relata dados, achados ou análises que o **usuário** produziu — nunca invente um número, uma tabela de desempenho, uma fala de entrevista ou qualquer achado empírico. Se a metodologia é revisão bibliográfica, "Resultados" pode legitimamente ser a síntese comparativa das fontes já levantada em `mapa_lacunas.json` (isso não é invenção, é reaproveitamento do que já foi pesquisado e validado). Para qualquer outra metodologia (estudo de caso, campo, experimental, DSR), os resultados têm que vir de algo que o usuário forneceu nesta conversa — peça os dados/achados explicitamente antes de escrever esta seção se eles não estiverem disponíveis.

Nunca inclua um bloco condicional só porque ele "sempre aparece" em trabalhos parecidos — cada bloco deve ter uma razão de existir dada a metodologia declarada.

## Passo 5 — Geração do documento (.docx) — determinístico, via scripts

Não é responsabilidade de nenhum agente — coberto por `scripts/` (ver `scripts/README.md`). A ordem e os elementos pré-textuais mudam conforme `tipo_projeto` (ver Passo 4) — são **três** estruturas possíveis, não duas:

**`tcc_monografia` (trabalho finalizado, NBR 14724:2024):**
```
[Elementos pré-textuais]
- Capa, Folha de rosto, Folha de Aprovação, Resumo (NBR 6028) + Abstract, Sumário (NBR 6027)

[Elementos textuais]
1. Introdução
2. Problema de Pesquisa
3. Justificativa (3.1 Acadêmica, 3.2 Prática e Didática, 3.3 Originalidade)
4. Objetivo Geral
5. Objetivos Específicos
6. Modelo Conceitual (se aplicável)
7. Fundamentação Teórica (um subtítulo por sub-tema)
8. Metodologia
9. Tags de Busca / Critérios de Exclusão / Estrutura da Revisão / Protocolo de Seleção (se bibliográfica)
10. Resultados e Discussão
11. Conclusão
12. Registro das Fontes (se bibliográfica)

[Elementos pós-textuais]
Referências (NBR 6023) — sem número progressivo
```

**`tcc_artigo` (trabalho finalizado, NBR 6022 — mais compacto, sem pré-textual de monografia):**
```
[Primeira página, sem quebra entre os blocos]
- Título, Autor(es) + afiliação, Resumo (NBR 6028) + Abstract

[Elementos textuais — numeração de página já começa em 1, sem sumário]
1. Introdução (incorpora a revisão de literatura — sem capítulo de Fundamentação Teórica separado)
2. Modelo Conceitual (se aplicável)
3. Metodologia
4. Resultados e Discussão
5. Conclusão

[Elementos pós-textuais]
Referências (NBR 6023) — sem número progressivo
```

**`projeto_pesquisa_tcc` (proposta, NBR 15287:2025) — mesma estrutura de `skill-mestrado`:**
```
[Elementos pré-textuais]
- Capa, Folha de rosto, Sumário (NBR 6027)

[Elementos textuais]
1. Introdução
2. Problema de Pesquisa
3. Justificativa (3.1 Acadêmica, 3.2 Prática e Didática, 3.3 Originalidade)
4. Objetivo Geral
5. Objetivos Específicos
6. Modelo Conceitual (se aplicável)
7. Fundamentação Teórica (um subtítulo por sub-tema)
8. Metodologia
9. Tags de Busca / Critérios de Exclusão / Estrutura da Revisão / Protocolo de Seleção (se bibliográfica)
10. Cronograma
11. Registro das Fontes (se bibliográfica)

[Elementos pós-textuais]
Referências (NBR 6023) — sem número progressivo
```

Nos três casos, pule condicionais que não se aplicam sem alterar a ordem relativa dos que ficarem.

**Como gerar:** depois que o Agente Redator produzir `spec.json` (conforme `template/spec.schema.json`):
```
python3 scripts/gerar_projeto.py --spec spec.json --fontes fontes.json --out saida/<slug>.docx
```
Isso injeta `referencias_formatadas` e `fichamento` a partir de `fontes.json` (o Agente Redator nunca formata nem preenche isso à mão), calcula sumário e paginação reais (`paginacao_sumario.py`) e roda `validar_abnt.py`. Para `tcc_artigo`, `paginacao_sumario.py` pula o cálculo de duas passadas — não há sumário nem pré-textual a descontar, então o documento sai pronto numa passada só. Converta em PDF e confira visualmente antes de `present_files`.

**Formatação (NBR 15287:2025 / NBR 14724:2024 / NBR 6022, conforme `tipo_projeto`)**: A4, margens 3cm/3cm/2cm/2cm, Times New Roman 12 no corpo, espaçamento 1,5, parágrafos justificados, títulos `N TÍTULO EM CAIXA ALTA`. Exceção documentada: o **Modelo Conceitual** usa fonte monoespaçada (Courier New) centralizada para preservar fluxos com setas (`→`, `↔`) literalmente — é um recurso visual, não uma exigência da NBR, e `validar_abnt.py` já sabe aceitar essa exceção.

**Limite conhecido do template de artigo**: a estrutura acima é um formato ABNT genérico (NBR 6022), não o template de um periódico/evento específico. Se o usuário já souber para qual revista/evento vai submeter, avise que muitas exigem template próprio (frequentemente duas colunas, margens e fontes diferentes) e que esta skill não reproduz esses templates específicos — o que ela entrega é um artigo estruturalmente correto e completo, que precisa ser reformatado para o template exato do periódico-alvo na hora da submissão.

**Cronograma** — só para `tipo_projeto = projeto_pesquisa_tcc` (não existe cronograma de algo já concluído). Tabela (atividades × períodos), granularidade tipicamente mensal para a duração mais curta de um TCC (1-2 semestres) — o Agente Redator só decide quais atividades existem e quando; a tabela em si é renderizada por `scripts/cronograma.py` + `scripts/docx_builder.py`.

## Checklist de qualidade antes de entregar

- O ciclo de pesquisa respeitou o piso (1-3 sub-temas, 2-4 fontes validadas cada) — `validar_ciclo_pesquisa.py` com `"ok": true`?
- Cada objetivo específico contribui claramente para o objetivo geral?
- Cada tag de busca e cada critério de exclusão (quando existirem) se conecta de volta ao problema de pesquisa central?
- Nenhum bloco condicional foi incluído sem necessidade dada a metodologia escolhida?
- Se `tipo_projeto` é monografia/artigo: todo achado em Resultados e Discussão veio do usuário ou da síntese já validada em `mapa_lacunas.json` — nenhum número, tabela ou achado empírico foi inventado?
- Nenhuma citação, referência ou resumo de fichamento foi inventado — tudo remete a uma fonte de fato registrada em `fontes.json`?

---
name: skill-mestrado
description: Conduz um ciclo real de pesquisa (define o que precisa descobrir, divide em etapas, busca em múltiplas fontes, compara, identifica lacunas, valida) e a partir dele gera um Projeto de Pesquisa completo em .docx para seleção ou qualificação de Mestrado/Doutorado, formatado pela ABNT NBR 15287:2025 e normas correlatas (NBR 6023 referências, NBR 10520 citações, NBR 6027 sumário, NBR 6024 numeração progressiva). Use sempre que o usuário pedir para criar, estruturar ou pesquisar um projeto de pesquisa de mestrado/doutorado, pré-projeto para seleção de pós-graduação (PPG), projeto de qualificação, ou mencionar tema de dissertação/tese, mesmo sem dizer "mestrado" — gatilhos incluem problema de pesquisa, hipóteses, fundamentação teórica, revisão de literatura, cronograma de pesquisa, linha de pesquisa, orientador, programa de pós-graduação, edital de seleção de mestrado/doutorado.
---

# Skill Mestrado — Projeto de Pesquisa com Ciclo de Pesquisa Real

Esta skill transforma um tema (às vezes só uma frase, como "Inteligência Artificial na Educação") em um Projeto de Pesquisa completo para Mestrado ou Doutorado. A diferença central em relação a um trabalho de TCC é que aqui **o conteúdo não pode vir só da cabeça do usuário ou da sua memória** — problema de pesquisa, justificativa e fundamentação teórica de um projeto de pós-graduação precisam estar ancorados no que já existe de fato na literatura, o que só se descobre pesquisando de verdade, com múltiplas buscas, comparação entre fontes e validação — não com uma única busca solta.

Se o usuário quiser algo mais simples (TCC, monografia, artigo de graduação) sem esse ciclo de pesquisa aprofundado, prefira a skill `skill-tcc`, que é mais leve e direta.

## Princípio que guia tudo aqui

Um projeto de mestrado convence uma banca/comissão de seleção de duas coisas: (1) que o problema proposto é real e ainda não está resolvido na literatura, e (2) que o candidato já mapeou esse terreno com seriedade. Isso só se sustenta se a lacuna apontada na justificativa foi de fato verificada — não presumida. Por isso o ciclo de pesquisa (Passo 2) não é uma etapa opcional de "enriquecimento": é o que dá lastro a todo o resto do documento. Um objetivo específico, uma hipótese ou uma afirmação na fundamentação teórica que não se conecte a algo que você efetivamente pesquisou e comparou entre fontes é o mesmo problema apontado na skill-tcc para tags de busca soltas — só que mais grave, porque aqui o documento é avaliado por especialistas na área.

## Visão geral do fluxo

1. **Elicitação** — tema, programa/instituição (se já souber o edital/linha de pesquisa), se já existe um problema de pesquisa ou hipótese de partida, e o tipo de projeto (seleção de mestrado, qualificação, projeto para bolsa/edital de fomento).
2. **Ciclo de pesquisa** — o coração da skill: descobrir o que já existe sobre o tema antes de escrever qualquer seção do documento.
3. **Elementos estruturantes do projeto** — preencher introdução, problema, justificativa, objetivos, hipóteses (quando aplicável), fundamentação teórica, metodologia e cronograma, todos amarrados ao que foi descoberto no ciclo de pesquisa.
4. **Geração do documento** — montar tudo em um único `.docx` formatado pela NBR 15287:2025, com referências reais (não inventadas) das fontes usadas no ciclo de pesquisa.

Trate isso como um processo iterativo de plano-confirma-implementa: depois do ciclo de pesquisa, mostre ao usuário um resumo do que foi encontrado (principais lacunas, ângulo proposto) antes de escrever o documento inteiro — é mais barato ajustar o rumo nessa hora do que depois de gerar 15 páginas.

## Orquestração multi-agente

Os Passos 1-4 abaixo (não-determinísticos) estão organizados em três papéis, cada um com arquivo de instrução próprio em `agents/`:

| Papel | Cobre | Arquivo | Produz |
|---|---|---|---|
| Agente Elicitador | Passo 1 | `agents/elicitador.md` | `elicitacao.json` |
| Agente Pesquisador | Passo 2 | `agents/pesquisador.md` | `buscas_log.json`, `fontes.json`, `mapa_lacunas.json` |
| Agente Redator | Passos 3-4 | `agents/redator.md` | `spec.json` |

O Passo 5 (formatação/geração do `.docx`) é **determinístico** e não é um agente — é o script `scripts/gerar_projeto.py` (ver `scripts/README.md`).

Se o ambiente suportar spawn de subagente (ex.: Task tool), invoque cada papel como uma tarefa separada, passando só o JSON de entrada e o caminho do arquivo de instrução correspondente. Se não suportar (ex.: esta própria conversa no claude.ai), leia o `agents/<papel>.md` da fase antes de começá-la e siga como troca de papel na mesma thread — a arquitetura não depende de spawn pra funcionar. Antes de avançar do Pesquisador para o Redator, rode `scripts/validar_ciclo_pesquisa.py`; se o piso de busca não for atingido em algum sub-tema, volte ao Pesquisador só para esses sub-temas em vez de prosseguir. Diagrama completo do workflow e os schemas de cada JSON em `agents/README.md` e `template/`.

## Passo 1 — Elicitação inicial (Agente Elicitador)

Extraia da conversa (ou pergunte o que faltar):

- **Tema** — já delimitado ou ainda amplo? Um tema amplo (ex.: "Inteligência Artificial na Educação", sem nível de ensino, tecnologia específica ou contexto definidos) não é um problema — é sinal de que a delimitação é parte do trabalho. Nesse caso **não delimite sozinho**: proponha ao usuário 2-3 recortes possíveis (por nível de ensino, população, tecnologia específica, contexto de aplicação etc.) e pergunte qual ele prefere antes de seguir para o ciclo de pesquisa (Passo 2) — use `ask_user_input_v0` com os recortes como opções, quando disponível. Se você não tiver contexto suficiente para propor recortes com segurança (por exemplo, não sabe quais linhas de pesquisa o programa-alvo oferece), pergunte primeiro ao usuário quais são as linhas de pesquisa disponíveis no programa, e só então proponha recortes que calcem em alguma delas.
- **Nível e tipo de projeto** — seleção de mestrado, seleção de doutorado, qualificação (projeto já em andamento), ou projeto para edital de fomento/bolsa? Isso muda o grau de detalhe esperado no cronograma e na fundamentação.
- **Programa de pós-graduação / instituição / linha de pesquisa**, se já souber — vai na folha de rosto, ajuda a calibrar o vocabulário da área e a checar se o recorte escolhido cabe em alguma linha do programa.
- **Já existe problema de pesquisa ou hipótese** definidos pelo usuário, ou é para construir a partir do tema (e do recorte escolhido)?
- **Prazo/duração do mestrado ou doutorado** (geralmente 24 meses para mestrado, 48 para doutorado no Brasil, mas confirme) — necessário para o cronograma.
- **Idioma das buscas** — pergunte ao usuário se o ciclo de pesquisa (Passo 2) deve buscar só em português (fontes nacionais/lusófonas) ou em português + inglês (amplia para a literatura internacional, mas exige mais cuidado ao verificar a tradução de conceitos e terminologia). A resposta vale para todas as buscas do Passo 2.
- **Exigências específicas do edital**, se houver (algumas instituições pedem seções extras ou limite de páginas — quando há edital, ele prevalece sobre a norma genérica).

## Passo 2 — Ciclo de pesquisa (Agente Pesquisador)

Esta é a etapa que diferencia um projeto de mestrado de um exercício de preenchimento de template. Execute-a de verdade, com chamadas reais de busca — não escreva a fundamentação teórica de memória.

1. **Define o que precisa descobrir** — a partir do tema, formule 3-5 perguntas-chave que a pesquisa precisa responder antes de você conseguir escrever o problema de pesquisa com segurança (ex.: "quais abordagens de IA já foram aplicadas em educação básica?", "que lacunas os autores mais citados apontam como não resolvidas?").
2. **Divide o problema em etapas** — quebre o tema em sub-temas de busca (ex.: "IA na educação" → tutoria inteligente, avaliação automatizada, personalização de ensino, ética e viés algorítmico em educação). Cada sub-tema vira uma frente de busca própria.
3. **Pesquisa múltiplas fontes** — para cada sub-tema, faça **no mínimo 2-3 buscas** (`web_search`) com termos diferentes — não se contente com uma busca genérica — até reunir **no mínimo 3-5 fontes validadas por sub-tema** antes de passar para o próximo; se não atingir esse piso nas primeiras tentativas, reformule os termos e busque de novo em vez de seguir com poucas fontes. Use o idioma definido no Passo 1: se o usuário escolheu português + inglês, gere também as palavras-chave equivalentes em inglês para cada sub-tema — não traduza termo a termo, use o vocabulário que a literatura internacional efetivamente emprega para o conceito. Priorize artigos de periódicos, anais de eventos científicos, dissertações/teses similares (Catálogo de Teses e Dissertações da CAPES, BDTD) e revisões sistemáticas recentes (últimos 5 anos, salvo justificativa para trabalhos clássicos/fundadores).
4. **Usa ferramentas** — use `web_fetch` para ler o conteúdo completo de artigos/resumos relevantes antes de citá-los; não cite com base só no título ou snippet de busca.
5. **Compara informações** — depois de reunir várias fontes por sub-tema, identifique onde elas convergem (consenso já estabelecido — não é sua contribuição) e onde divergem (controvérsia = pode virar problema de pesquisa).
6. **Identifica lacunas** — o que os próprios autores apontam como "trabalhos futuros" ou "não explorado"? O que está bem coberto para um contexto (ex.: ensino superior) mas pouco para outro (ex.: educação infantil)? Isso é o que vai sustentar a justificativa e a originalidade do projeto.
7. **Faz novas buscas** — quando uma lacuna aparece, não pare aí: faça buscas adicionais e mais específicas para confirmar que ela é real e não apenas um ponto cego da sua primeira rodada de busca.
8. **Valida os resultados** — antes de usar qualquer afirmação específica (dado, estatística, definição de conceito) na fundamentação teórica, confira se pelo menos duas fontes concordam com ela, ou marque explicitamente como "segundo [autor]" quando for uma posição isolada. Nunca invente uma citação, autor ou dado que não veio de uma fonte real que você efetivamente pesquisou.

Ao final do ciclo, monte um mapa curto (pode ser interno, para orientar a escrita, ou mostrado ao usuário) ligando: sub-tema → principais fontes → convergência/divergência → lacuna identificada. Esse mapa é o que alimenta a Justificativa e a Fundamentação Teórica no Passo 3 — cada afirmação relevante nessas seções deve remeter a algo desse mapa.

Sempre siga as regras de copyright ao lidar com o conteúdo das fontes: parafraseie, nunca reproduza trechos longos, e construa a lista de referências (NBR 6023) só com fontes que você de fato consultou.

## Passo 3 — Elementos estruturantes do projeto (Agente Redator)

Um projeto de mestrado/doutorado é mais extenso e mais rigoroso que um projeto de TCC. Preencha, nesta ordem lógica (a ordem final de seções está no Passo 5):

1. **Introdução** — apresentação do tema, contextualização e delimitação do objeto de estudo (o que fica dentro e fora do escopo).
2. **Problema de pesquisa** — uma pergunta clara, delimitada e investigável, construída (ou confirmada) a partir das lacunas identificadas no ciclo de pesquisa.
3. **Justificativa** — articula relevância científica (a lacuna real encontrada na literatura), relevância social/prática, e originalidade (o ângulo que este projeto propõe que ainda não foi coberto).
4. **Objetivo geral** — uma frase, amarrada diretamente ao problema de pesquisa.
5. **Objetivos específicos** — 3-5 ações verificáveis que, somadas, entregam o objetivo geral.
6. **Hipóteses** — quando o problema de pesquisa permitir uma resposta testável a priori (comum em pesquisas empíricas/quantitativas), formule hipóteses testáveis. Em pesquisas qualitativas ou puramente teóricas/bibliográficas, é normal não haver hipóteses formais — não force essa seção quando ela não fizer sentido metodológico.
7. **Fundamentação teórica / Revisão de literatura** — organizada por sub-tema (os mesmos sub-temas do ciclo de pesquisa), apresentando o estado da arte, os principais autores/conceitos, e terminando cada bloco apontando a lacuna que conecta aquele sub-tema ao problema de pesquisa. Esta seção tende a ser a mais extensa do documento.
8. **Metodologia** — tipo de pesquisa (bibliográfica, estudo de caso, pesquisa de campo/survey, pesquisa-ação, experimental, **Design Science Research quando o objeto de estudo for um artefato técnico a construir e avaliar** (sistema, algoritmo, protótipo, framework), ou combinação — ver `references/metodologias-mestrado.md` para o detalhamento de cada uma no contexto de pós-graduação, incluindo população/amostra, instrumentos de coleta e procedimentos de análise de dados quando aplicável).
9. **Cronograma** — distribuição das atividades ao longo da duração do mestrado/doutorado (ver formato no Passo 5).
10. **Referências** — apenas as fontes efetivamente pesquisadas e validadas no Passo 2, formatadas conforme NBR 6023.

## Passo 4 — Elementos condicionais (Agente Redator)

| Condição | O que incluir/ajustar |
|---|---|
| Pesquisa empírica (quantitativa ou quali-quanti) | Inclui Hipóteses; Metodologia detalha população, amostra, instrumento e tratamento estatístico dos dados |
| Pesquisa qualitativa (entrevistas, estudo de caso, análise de discurso) | Hipóteses geralmente ausentes ou substituídas por "questões norteadoras"; Metodologia detalha critério de seleção dos sujeitos/casos e procedimento de análise |
| Pesquisa bibliográfica/teórica pura | Sem Hipóteses; sem população/amostra; a Fundamentação Teórica carrega mais peso relativo no documento |
| Projeto para edital de fomento (ex.: CAPES, CNPq, FAPESP) | Confira exigências específicas do edital (algumas pedem orçamento, impacto/aderência a linhas de fomento, ou limite rígido de páginas) — o edital sempre prevalece sobre a estrutura genérica desta skill quando houver conflito |
| Projeto de qualificação (já em andamento, não é seleção) | Pode incluir uma seção adicional de "Resultados parciais", se o usuário já tiver dados/achados preliminares |
| Objeto de estudo é um artefato técnico a construir (sistema, algoritmo, protótipo, framework, arquitetura de software) | Siga a trilha de Design Science Research (DSR): Problema → Artefato Proposto → Ciclos de Construção/Avaliação → Validação frente ao estado da arte. Hipóteses tendem a dar lugar a critérios de avaliação do artefato (desempenho, usabilidade, precisão, escalabilidade). Ver detalhamento em `references/metodologias-mestrado.md` |

## Passo 5 — Ordem das seções e formatação (NBR 15287:2025) — determinístico, via scripts

Este passo **não é responsabilidade de nenhum agente** — é inteiramente coberto pelos scripts Python em `scripts/` (ver `scripts/README.md` para a arquitetura completa). A ABNT NBR 15287:2025 (que cancelou e substituiu a versão de 2011) organiza o projeto de pesquisa em parte externa e parte interna, com elementos pré-textuais, textuais e pós-textuais. Estrutura de referência para o `.docx` (já implementada em `scripts/docx_builder.py`):

```
[Elementos pré-textuais]
- Capa (opcional, mas recomendado incluir para submissão formal)
- Folha de rosto (autor, título, instituição, programa de pós-graduação,
  linha de pesquisa, nome do orientador se houver, local, ano)
- Sumário (NBR 6027 — lista as seções na mesma ordem e grafia do texto)

[Elementos textuais]
1. Introdução
2. Problema de Pesquisa
3. Justificativa
   3.1 Relevância Científica
   3.2 Relevância Social/Prática
   3.3 Originalidade
4. Objetivo Geral
5. Objetivos Específicos
6. Hipóteses (se aplicável)
7. Fundamentação Teórica / Revisão de Literatura
   7.1, 7.2... (um subtítulo por sub-tema do ciclo de pesquisa)
8. Metodologia
9. Cronograma

[Elementos pós-textuais]
Referências (NBR 6023) — sem número progressivo, por convenção
- Apêndices (opcional)
- Anexos (opcional)
```

`scripts/numeracao.py` pula automaticamente blocos condicionais vazios (ver Passo 4) sem deixar buraco na numeração — o Agente Redator não precisa calcular os números manualmente, só decidir quais seções existem.

**Formatação (NBR 15287:2025), já aplicada por `scripts/docx_builder.py`:**
- Papel A4, margens: 3cm superior/esquerda, 2cm inferior/direita.
- Fonte Times New Roman, tamanho 12 no corpo; tabelas e legendas em tamanho 10.
- Espaçamento 1,5 entre linhas no corpo do texto.
- Parágrafos justificados.
- Títulos de seção primária: `N TÍTULO EM CAIXA ALTA`, negrito. Subtítulos: `N.M Subtítulo`, negrito, sem caixa alta.
- Paginação: conta-se a partir da folha de rosto, mas o número só aparece a partir da Introdução — calculado de verdade (não estimado) por `scripts/paginacao_sumario.py`, que renderiza um rascunho, localiza a página real de cada heading e regenera o documento final com os números corretos.
- Citações seguem NBR 10520 e referências seguem NBR 6023 — nenhuma das duas é formatada pelo Agente Redator "à mão": ele usa as chaves de citação devolvidas por `scripts/fontes_registry.py` durante o Passo 2, e a lista final de referências é montada automaticamente por `scripts/gerar_projeto.py` a partir de `fontes.json`.

**Como gerar o arquivo final:** depois que o Agente Redator produzir `spec.json` (conforme `template/spec.schema.json`), rode:
```
python3 scripts/gerar_projeto.py --spec spec.json --fontes fontes.json --out saida/<slug>.docx
```
Isso injeta as referências formatadas, chama `paginacao_sumario.gerar_com_paginacao_real()` e roda `scripts/validar_abnt.py` sobre o resultado, imprimindo um relatório de conformidade. Ainda assim, converta o `.docx` final em PDF e confira visualmente (a validação automática cobre margens/fonte/espaçamento/tabela, não legibilidade ou quebras de página estranhas) antes de apresentar com `present_files`.

**Cronograma** — sempre em formato de tabela: atividades nas linhas, períodos (meses ou semestres, conforme `granularidade_cronograma` da metadata) nas colunas, marcando com "X" os períodos em que cada atividade ocorre — a tabela em si é renderizada por `scripts/cronograma.py` + `scripts/docx_builder.py`; o Agente Redator só decide quais atividades existem e em quais períodos elas ocorrem. Inclua tipicamente: revisão de literatura (contínua, mas mais intensa no início), coleta de dados (se houver), análise de dados, redação dos capítulos, qualificação, defesa.

## Checklist de qualidade antes de entregar

- Se o tema chegou amplo, os recortes foram propostos e confirmados pelo usuário antes de seguir — em vez de delimitados sozinho?
- O piso de busca foi atingido em cada sub-tema (mínimo 2-3 buscas, 3-5 fontes validadas) e no idioma que o usuário escolheu?
- Se o objeto de estudo é um artefato técnico, a trilha de Design Science Research foi considerada em vez de forçar o objeto em estudo de caso/experimental?
- O ciclo de pesquisa foi realmente executado (múltiplas buscas, fontes lidas de verdade, não só títulos) — ou o documento tem seções escritas de memória sem lastro?
- A justificativa aponta uma lacuna que veio do que foi pesquisado, não uma lacuna genérica ou presumida?
- Cada afirmação relevante na Fundamentação Teórica remete a uma fonte real, e essa fonte está na lista de Referências?
- As Hipóteses (quando presentes) são testáveis e coerentes com a Metodologia escolhida?
- O Cronograma é compatível com a duração real do mestrado/doutorado informada pelo usuário?
- Nenhuma citação ou referência foi inventada — todas vieram de fontes efetivamente consultadas no ciclo de pesquisa?

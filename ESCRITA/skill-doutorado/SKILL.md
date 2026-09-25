---
name: skill-doutorado
description: >-
  Gera projetos de pesquisa de doutorado completos a partir de um tema, seguindo a NBR 15287 e normas ABNT correlatas (NBR 6023, NBR 10520, NBR 14724). Conduz pesquisa agêntica real — decompõe o tema, busca múltiplas fontes acadêmicas, compara e valida informações, identifica lacunas do estado da arte — antes de redigir, em vez de escrever de conhecimento genérico. Use SEMPRE que o usuário pedir para elaborar, redigir ou estruturar um projeto de pesquisa, anteprojeto, proposta ou pré-projeto de doutorado, seleção de PPG, edital de pós-graduação, exame de qualificação ou bolsa (CAPES/CNPq/FAPs). Ative mesmo sem menção a NBR 15287 — ex.: 'faça um projeto de pesquisa sobre X pro doutorado', 'preciso de um pré-projeto pra seleção do PPG'. Não usar para TCC de graduação/especialização isolado nem artigo científico avulso.
---

# Skill Doutorado — Projeto de Pesquisa (NBR 15287)

## O que esta skill produz

Um projeto de pesquisa de doutorado formatado conforme a NBR 15287:2011, pronto para submissão a um Programa de Pós-Graduação (PPG), edital de bolsa ou banca de seleção. Não é um resumo de conhecimento prévio: é o resultado de um processo de pesquisa real, com buscas, comparação de fontes e validação — porque um projeto de doutorado vive ou morre pela solidez do estado da arte e pela originalidade da lacuna que ele reivindica preencher.

## Por que o processo importa mais que o template

Qualquer modelo entrega os títulos das seções certas. O que diferencia um projeto de doutorado aprovável é:

1. **O problema é real e delimitado**, não uma reformulação vaga do tema.
2. **O estado da arte é verificado**, não inventado — bancas de doutorado detectam referências genéricas ou desatualizadas na hora.
3. **A lacuna é defensável** — o projeto mostra o que já foi feito, por quem, e por que isso ainda não resolve o problema proposto.
4. **A metodologia é coerente** com o problema e os objetivos, não um capítulo genérico de "abordagem qualitativa".

Por isso o fluxo abaixo é obrigatório antes de escrever qualquer seção do projeto. Pular direto para a redação produz um texto com a forma certa e o conteúdo fraco — exatamente o tipo de projeto que uma banca rejeita.

## Fluxo de pesquisa agêntica

Percorra as etapas em ordem. Elas espelham como um pesquisador de fato trabalha, não um checklist burocrático — cada etapa existe para blindar o projeto contra a fraqueza mais comum de propostas de doutorado (superficialidade no estado da arte).

> **Modo multi-agente:** as etapas 3 (pesquisa por subtema), 7 (auditoria do rascunho) e parte da 8 (subseções do Referencial teórico) podem ser delegadas a agentes especializados — em paralelo quando o ambiente suporta subagentes, ou seguidas inline uma de cada vez quando não suporta (claude.ai). Ver `agents/README.md` para o registro completo de papéis, responsabilidades e o diagrama do workflow. As demais etapas (1, 2, 4, 5, 6, 8a) exigem interação com o usuário ou visão de conjunto e ficam sempre com o orquestrador (você, seguindo este arquivo).

### 1. Defina o que precisa ser descoberto

A partir do tema dado pelo usuário, formule explicitamente (e mostre ao usuário, para validação antes de prosseguir se o tema for amplo ou ambíguo):
- Qual é o fenômeno/problema real por trás do tema?
- O que já se sabe sobre ele (hipótese inicial, a confirmar na pesquisa)?
- O que provavelmente ainda não se sabe, ou é contestado?

Se o tema vier muito amplo (ex.: "IA na Educação"), não tente cobrir tudo — é sinal de que a delimitação é parte do trabalho. Antes de iniciar qualquer busca, proponha ao usuário de 3 a 5 recortes possíveis (combinando eixos como nível de ensino, tecnologia específica, aspecto pedagógico, região/contexto institucional, abordagem teórica) e pergunte qual recorte ele prefere — não escolha sozinho um recorte de tema amplo sem confirmação, mesmo que um pareça óbvio. Use `ask_user_input_v0` quando disponível, ou pergunte diretamente no chat.

Ao mesmo tempo, verifique se há contexto suficiente sobre o programa de destino. Se o usuário não tiver informado o Programa de Pós-Graduação e sua(s) linha(s) de pesquisa, pergunte explicitamente antes de prosseguir — o recorte escolhido idealmente precisa se encaixar em uma linha de pesquisa existente do PPG-alvo, e propor um projeto fora de todas as linhas disponíveis é um erro que invalida a submissão. Se o usuário não souber as linhas de pesquisa, ofereça buscar o site do programa (se ele informar a instituição) antes de fechar o recorte.

Um projeto de doutorado precisa de um problema estreito e profundo, não um tema largo e raso. Só avance para a etapa 2 depois que o usuário confirmar o recorte.

### 2. Divida o problema em etapas de investigação

Quebre a pesquisa em frentes que, juntas, vão sustentar cada seção do projeto:
- **Conceitual**: definições e marcos teóricos centrais do tema.
- **Estado da arte**: o que já foi publicado (últimos ~5-10 anos, priorizando os últimos 2-3), quem são os autores/grupos de referência, quais as principais abordagens teóricas e metodológicas em disputa.
- **Lacunas e controvérsias**: onde a literatura diverge, o que ainda não foi testado, quais críticas metodológicas recorrem.
- **Viabilidade metodológica**: que métodos outros pesquisadores usaram para problemas próximos, e o que é factível para uma tese.

> **Divisão de trabalho nesta skill:** as etapas 1, 2, 4, 5, 6, 7 (julgamento) e a redação da etapa 8 são sempre feitas por você — exigem entender, comparar e argumentar. As partes puramente mecânicas de contagem, checagem e formatação foram extraídas para `scripts/` (ver "Scripts determinísticos" abaixo), que você chama via `bash_tool` no momento indicado em cada etapa. Os scripts nunca decidem conteúdo — só auditam e formatam o que você já decidiu.

### 3. Pesquise múltiplas fontes

Antes da primeira busca, pergunte ao usuário o idioma das fontes: apenas português (PT-BR) ou português + inglês. Não decida isso sozinho — doutorado em algumas áreas exige diálogo com a literatura internacional, mas o usuário pode preferir restringir a fontes em português por motivo de escopo, orientador ou norma do programa. Se o usuário pedir PT-BR + inglês, formule cada consulta de busca duas vezes (uma em português, uma em inglês) por subtema, não apenas traduza o resultado depois.

Com o recorte (etapa 1) e o idioma já confirmados, inicialize o log compartilhado que os scripts vão auditar:

```bash
python scripts/research_log.py init --log research_log.json --recorte "<recorte confirmado>" --idioma ptbr|ptbr+en
```

Use `web_search` e `web_fetch` de forma real — não escreva o estado da arte de memória. Priorize, nesta ordem:
1. Periódicos e repositórios acadêmicos (Google Scholar, SciELO, Periódicos CAPES, repositórios institucionais de teses/dissertações — especialmente teses de doutorado recentes sobre temas próximos, que mostram o que já foi "ocupado").
2. Revisões sistemáticas e meta-análises recentes sobre o tema, que já mapeiam o campo.
3. Trabalhos-âncora citados repetidamente por outros (indicam os marcos teóricos que o projeto precisa dialogar).

Faça várias buscas específicas em vez de uma busca genérica — trate a etapa 2 como o roteiro de busca: uma consulta por frente de investigação, refinando conforme os resultados. Ver "Diretrizes de busca" abaixo para o piso mínimo obrigatório de buscas e fontes.

Registre cada busca e cada fonte que você de fato ler e considerar idônea (isso é julgamento seu — o script só guarda o que você decidir):

```bash
python scripts/research_log.py add-busca --log research_log.json --subtema estado_da_arte --idioma pt --query "..."
python scripts/research_log.py add-fonte --log research_log.json --subtema estado_da_arte \
    --autor "SOBRENOME, Nome" --ano 2024 --titulo "..." --veiculo "..." --tipo artigo --url "..."
```

### 4. Compare as informações entre si

Para cada afirmação relevante que for entrar no projeto, verifique se outras fontes concordam, divergem ou nuançam. Não trate a primeira fonte encontrada como verdade — um projeto de doutorado precisa mostrar domínio do debate, inclusive das divergências.

### 5. Identifique lacunas

A lacuna é o coração da justificativa e do problema de pesquisa. Ela deve ser específica: não "faltam estudos sobre X" (genérico demais), mas "os estudos sobre X tratam de [contexto A], mas não de [contexto B]", ou "há consenso sobre [achado], mas os mecanismos causais permanecem não testados empiricamente". Se a pesquisa das etapas 3-4 não revelar uma lacuna clara e defensável, isso é sinal para voltar à etapa 3 com buscas mais direcionadas — não para inventar uma lacuna genérica.

### 6. Faça novas buscas para fechar os pontos fracos

Depois de identificar a lacuna candidata, faça buscas adicionais direcionadas a testá-la: existe algum trabalho recente que já a preencheu (nesse caso, reformule a lacuna) ou algo que a confirma? Repita este ciclo (buscar → comparar → identificar lacuna) até a lacuna se sustentar. Não avance para a etapa 7 sem antes rodar a auditoria de cobertura:

```bash
python scripts/search_tracker.py --log research_log.json
```

Se sair `AINDA NÃO CONFORME`, o relatório aponta exatamente quais subtemas/idiomas estão abaixo do piso — volte à etapa 3/6 para esses subtemas específicos antes de seguir. Isso mecaniza a contagem; decidir *quais* buscas fazer para cobrir o que falta continua sendo seu julgamento.

### 7. Valide os resultados antes de redigir

Antes de passar para a redação, confira:
- As referências mais importantes são de fato recentes e de fontes idôneas (evite depender de posts de blog, resumos de terceiros ou material didático genérico como base do referencial teórico).
- Não há alegação factual no rascunho que não tenha sido checada em busca real — nunca invente citações, autores ou anos de publicação. Referência fabricada é a forma mais rápida de reprovar um projeto de doutorado.
- Se alguma citação foi feita "de memória" durante a redação, volte e confirme com uma busca antes de manter no texto final.

Depois de escrever um rascunho (mesmo que parcial, em markdown), rode a checagem mecânica de citações contra o que foi de fato registrado como fonte validada:

```bash
python scripts/citation_checker.py --draft rascunho.md --log research_log.json
```

Toda citação marcada como "órfã" precisa ser resolvida — ou você confirma a fonte com uma busca real e a registra via `add-fonte`, ou remove a citação do texto. Nunca mantenha uma citação órfã na versão final só porque "parece plausível". Julgar se a fonte é idônea continua com você; o script só encontra o que ficou sem lastro.

### 8. Produza o projeto

Só agora redija o documento completo, seção por seção, seguindo a estrutura da NBR 15287 detalhada em `references/estrutura-nbr15287.md` e o esqueleto de `assets/template-projeto.md` — preenchido com o conteúdo levantado nas etapas 1-7, não com generalidades. A redação em si (introdução, justificativa, referencial teórico, metodologia) é sempre sua. A montagem física do documento final é mecânica — ver "Scripts determinísticos" a seguir.

## Diretrizes de busca

**Piso mínimo obrigatório** (não é teto — amplie se o tema pedir mais):
- **3 a 5 buscas por subtema/frente de investigação** definida na etapa 2 (conceitual, estado da arte, lacunas/controvérsias, viabilidade metodológica — e, se o idioma escolhido for PT-BR + inglês, essa faixa vale para cada idioma, não para o total).
- **5 a 7 fontes validadas por tema/subtema** antes de considerar aquela frente encerrada — "validada" significa: fonte idônea (periódico, repositório acadêmico, tese/dissertação — não blog ou resumo de terceiros), com autor/ano/veículo conferíveis, e cujo conteúdo foi de fato lido (via `web_fetch`), não só o título/snippet da busca.
- Se, ao final do piso mínimo, uma frente de investigação ainda não tiver 5-7 fontes validadas ou revelar lacuna genérica demais, isso é sinal para buscar mais naquela frente antes de avançar — não para preencher com menos fontes.

Escale acima do piso conforme a complexidade e amplitude do tema — um tema amplo (mesmo já recortado na etapa 1) exige mais cobertura que um tema estreito. Para um projeto completo, é comum passar de 20-30 buscas somando todos os subtemas e idiomas. Priorize, além do piso por subtema: 2-3 revisões sistemáticas/meta-análises recentes, e buscas de fechamento de lacuna (etapa 6).

Cada citação no texto final deve ter uma fonte real, rastreável e coerente com o padrão ABNT de citação (autor-data). Ao usar `web_search`/`web_fetch`, siga as regras normais de copyright: parafraseie, nunca reproduza parágrafos de artigos, e cite (nome do autor, ano) no corpo do texto — não blocos de texto copiado.

## Scripts determinísticos

Tudo em `scripts/` faz apenas contagem, checagem cruzada ou formatação mecânica sobre o que você já decidiu — nunca gera conteúdo, nunca julga relevância ou qualidade. Todos são chamados via `bash_tool`; rode `python scripts/<nome>.py --help` para ver os argumentos completos.

| Script | Quando chamar | O que faz |
|---|---|---|
| `research_log.py` | Início da etapa 3 (`init`); a cada busca/fonte validada (`add-busca`/`add-fonte`) | Mantém o `research_log.json` — o estado compartilhado que os outros scripts leem |
| `search_tracker.py` | Antes de passar da etapa 6 para a 7 | Confere o piso mínimo (3-5 buscas/idioma, 5-7 fontes por subtema) e aponta o que falta |
| `citation_checker.py` | Depois de qualquer rascunho, antes da versão final | Cruza citações `(AUTOR, ano)` do texto com `fontes_validadas`; sinaliza citação sem fonte real (fabricação) e fonte validada nunca citada |
| `reference_formatter.py` | Ao montar a seção Referências | Formata `fontes_validadas` em NBR 6023, ordenadas alfabeticamente |
| `cronograma_builder.py` | Ao montar a etapa 8 do projeto (cronograma) | Distribui proporcionalmente as etapas-padrão (ou customizadas) ao longo da duração informada |
| `docx_builder.py` | Etapa 8, versão final | Monta o `.docx` completo (capa, folha de rosto, sumário automático, numeração progressiva, margens/fonte/espaçamento NBR 14724, cronograma, referências) a partir de um JSON de config — ver docstring do script para o formato exato |

Fluxo típico de fechamento (etapa 8): redija cada seção em texto puro, monte o JSON de config (`meta` + `secoes`; `referencias_log` apontando para o `research_log.json` gera as referências automaticamente; `cronograma` vem da saída de `cronograma_builder.py`), rode `docx_builder.py`, e então siga o passo de verificação visual descrito em "Formato de entrega" abaixo.

## Estrutura e formatação (NBR 15287)

Antes de montar o documento final, leia `references/estrutura-nbr15287.md` — ele traz a lista completa de elementos pré-textuais, textuais e pós-textuais exigidos pela norma, com o que cada seção deve conter especificamente para nível de doutorado (o que muda em relação a mestrado: originalidade mais exigente, estado da arte mais extenso, contribuição teórica explícita).

## Formato de entrega

Um projeto de pesquisa é um documento formal para submissão — gere sempre como arquivo `.docx`, nunca apenas como texto no chat. A montagem em si é feita por `scripts/docx_builder.py` (ver "Scripts determinísticos" acima), que já aplica a formatação ABNT descrita em `references/estrutura-nbr15287.md` (fonte, espaçamento, margens, paginação, capa e folha de rosto, numeração progressiva). Depois de gerar o `.docx`, converta para PDF e olhe as páginas antes de entregar — o script acerta a mecânica, mas só a inspeção visual pega quebra de página estranha, tabela deformada etc.:

```bash
python /mnt/skills/public/docx/scripts/office/soffice.py --headless --convert-to pdf saida.docx
pdftoppm -jpeg -r 100 saida.pdf pagina
```

Salve o `.docx` final em `/mnt/user-data/outputs/` e apresente o arquivo ao usuário.

Se o usuário pedir apenas um rascunho rápido ou quiser revisar a estrutura antes da versão final, ofereça primeiro um resumo em markdown no chat (título provisório, problema, objetivos, lacuna identificada e sumário) para validação, e só gere o `.docx` completo depois de confirmado — evita retrabalho de formatação quando o conteúdo ainda vai mudar.

## Perguntas a esclarecer com o usuário (quando não estiverem claras no pedido)

Não interrompa o fluxo de pesquisa para perguntar tudo de uma vez — mas antes de redigir a versão final, confirme o que for essencial e não estiver implícito no pedido:
- Programa de Pós-Graduação, instituição e (se souber) linha de pesquisa/orientador — vão na folha de rosto.
- Se o projeto é para seleção (edital) ou para exame de qualificação (nesse caso a estrutura e o tom mudam: qualificação assume que a pesquisa já está em andamento).
- Extensão esperada (editais variam de 5 a 30+ páginas) — impacta o quanto aprofundar cada seção.

Se o usuário não souber ou não informar, prossiga com uma estrutura completa e genérica de submissão a edital, deixando marcado com `[A PREENCHER]` os campos que dependem de dados institucionais (nome do PPG, orientador, etc.).

# Blocos condicionais por metodologia (TCC/monografia)

Este arquivo detalha os blocos que só entram na especificação do TCC dependendo da metodologia escolhida. Leia apenas a seção relevante para o caso em mãos.

## Revisão bibliográfica (detalhamento completo)

Quando a metodologia é pesquisa/revisão bibliográfica, os blocos abaixo substituem qualquer bloco de coleta de dados em campo.

**Tags de busca**: combinações booleanas (AND/OR/aspas para frases exatas) construídas diretamente a partir dos termos-chave do problema de pesquisa e dos objetivos específicos — não organizadas por eixos temáticos. Cada tag deve ser rastreável a uma parte específica do problema de pesquisa. O recorte temporal e o(s) idioma(s) aceitos entram como parte desta mesma seção (ex.: "aplicar as tags restringindo a resultados dos últimos 5 anos, em português ou inglês"), não como uma seção separada. Isso corresponde diretamente ao que o Agente Pesquisador registra em `buscas_log.json` por sub-tema — as tags de busca da seção nada mais são do que essas queries já organizadas para leitura.

**Critérios de exclusão**: o que descarta uma fonte mesmo que ela contenha as palavras-chave buscadas — fora do escopo definido, aspectos excessivamente específicos que não contribuem para o quadro geral, duplicatas, ou fora do recorte temporal/idioma definido nas tags de busca.

**Registro das fontes (fichamento)**: para cada fonte incluída, referência completa, objetivo/contribuição da fonte, conceitos relevantes, como contribui para o TCC. **Isto não é preenchido à mão** — é a tabela produzida automaticamente por `scripts/gerar_projeto.py` a partir do campo `resumo` que o Agente Pesquisador já registrou em `fontes.json` no momento em que validou cada fonte (`FontesRegistry.registrar(..., resumo="...")`). Se uma fonte chegar à Fundamentação Teórica sem um resumo registrado, isso é sinal de que ela não passou pela validação do Passo 2 — não invente o resumo depois, volte e registre a fonte corretamente.

**Estrutura proposta da revisão**: esqueleto dos capítulos que a revisão bibliográfica vai ter no texto final da monografia — organizados pelos 1 a 3 sub-temas definidos no ciclo de pesquisa (ver piso abaixo), terminando sempre com um capítulo de integração que reconstrói a relação entre eles à luz do problema de pesquisa (e do modelo conceitual, se houver um).

**Protocolo de seleção das fontes**: sequência fixa de 4 etapas —
1. Busca (aplicar as tags de busca definidas, já com o recorte temporal/idioma aplicado);
2. Triagem inicial (título, resumo, tipo de publicação);
3. Aplicação dos critérios de exclusão;
4. Fichamento e síntese (registrar via `fontes_registry.py` cada fonte incluída, com resumo, e cruzar as fontes buscando conceitos em comum, divergências, convergências e lacunas — isto alimenta `mapa_lacunas.json`).

**Piso de pesquisa (escopo de TCC, mais leve que mestrado):** 1 a 3 sub-temas no total, 2 a 4 fontes validadas por sub-tema, mínimo de 1 busca por sub-tema (reformulada se não bater o piso de fontes). `scripts/validar_ciclo_pesquisa.py` aplica isso mecanicamente — mais de 3 sub-temas ou mais de 4 fontes por sub-tema não é erro, mas é aviso de que o escopo pode ter crescido além do esperado para um TCC.

## Estudo de caso

- **Unidade de análise**: o que exatamente está sendo estudado (uma organização, um processo, um sistema, um grupo específico).
- **Critério de seleção do caso**: por que este caso e não outro — representatividade, acesso, criticidade, ineditismo.
- **Fontes de evidência**: documentos, entrevistas, observação direta, registros internos — e como serão triangulados entre si.
- **Protocolo do caso**: perguntas que guiam a coleta, e como os dados coletados serão organizados para análise.

Se o estudo de caso incluir uma etapa de revisão de literatura como preparação teórica, incorpore também o bloco de "tags de busca" da seção de revisão bibliográfica acima, mas apenas como fundamentação — não replique o protocolo de seleção de fontes completo a menos que a revisão seja extensa.

## Pesquisa de campo

- **População e amostra**: quem serão os respondentes/participantes, critério de seleção, tamanho da amostra e justificativa.
- **Instrumento de coleta**: questionário, roteiro de entrevista, formulário — com indicação de que tipo de dado cada bloco de perguntas produz.
- **Procedimento de coleta**: como e quando os dados serão coletados (presencial, online, prazo).
- **Tratamento dos dados**: método de análise (estatística descritiva, análise de conteúdo, codificação temática etc.), coerente com o tipo de dado coletado (quantitativo, qualitativo ou ambos).

## Pesquisa-ação

- **Contexto de intervenção**: onde e com quem a intervenção ocorre.
- **Papel do pesquisador**: se ele é também participante ativo do processo que está estudando (e como isso é declarado e controlado metodologicamente).
- **Ciclos de intervenção**: descrever o ciclo planejar → agir → observar → refletir, e quantas iterações estão previstas.
- **Critério de avaliação da intervenção**: como será avaliado se a intervenção teve o efeito esperado.

## Pesquisa experimental

- **Variáveis**: independente(s) e dependente(s), e como cada uma será operacionalizada/medida.
- **Grupo de controle**: se existe, e como os grupos são formados (aleatorização, pareamento).
- **Desenho experimental**: pré-teste/pós-teste, entre-grupos, dentro-do-grupo, etc.
- **Ameaças à validade**: variáveis de confusão previsíveis e como serão controladas.

## Design Science Research (DSR) / Pesquisa e Desenvolvimento

Use esta trilha (em vez de forçar o objeto em estudo de caso/experimental) quando o TCC propõe **construir um artefato técnico** — um sistema, algoritmo, protótipo, script, aplicativo. Comum em TCCs de Ciência da Computação, Engenharia e áreas afins; é a versão mais leve, para escopo de graduação, da mesma trilha usada em `skill-mestrado`.

- **Artefato proposto**: nomeie com precisão o que será construído (não "um sistema de X", mas o tipo concreto — um classificador, um protótipo de aplicativo, um script de automação).
- **Ciclos de construção e avaliação**: para um TCC, **1 a 2 ciclos** de build → avaliação → ajuste costuma ser realista dentro do prazo (diferente do mestrado, que comporta 2-3).
- **Critérios de avaliação do artefato**: métricas objetivas (acurácia, tempo de resposta, usabilidade) e um baseline de comparação simples — geralmente uma abordagem já estabelecida na literatura levantada no ciclo de pesquisa.
- **Ambiente de aplicação/teste**: onde e com que dados o artefato será testado (um dataset público, um cenário simulado).
- Use o bloco **Modelo Conceitual** (ver `SKILL.md`) para ilustrar o fluxo do artefato — a maioria dos TCCs de DSR se beneficia de um diagrama de fluxo simples, mesmo sem o aparato completo de contribuição científica generalizável que um mestrado exigiria.

## Metodologias combinadas

Quando o TCC combina mais de uma metodologia (ex.: revisão bibliográfica + estudo de caso, ou pesquisa quantitativa + qualitativa), não basta justapor os blocos de cada uma. Adicione uma seção própria — **Integração Metodológica** — respondendo:

- Qual metodologia vem primeiro e alimenta a outra (ex.: a revisão bibliográfica define as categorias que serão buscadas no estudo de caso)?
- Os resultados são triangulados (comparados/cruzados) ao final, ou usados para propósitos diferentes e complementares?
- Existe um ponto único de síntese onde as duas linhas de evidência se encontram — e qual pergunta esse ponto de síntese responde?

Sem essa seção de integração explícita, um TCC de metodologia combinada corre o risco de parecer dois trabalhos menores colados, em vez de um único trabalho coerente.

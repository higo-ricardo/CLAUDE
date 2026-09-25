# Metodologias em projetos de Mestrado/Doutorado

Detalhamento por tipo de metodologia, para preencher a seção 8 (Metodologia) do projeto com os elementos que uma banca de pós-graduação espera ver — mais granulares do que num projeto de TCC, porque aqui o candidato precisa demonstrar domínio do desenho de pesquisa, não só nomear o tipo.

## Pesquisa bibliográfica / revisão de literatura

- Tipo de revisão: narrativa, sistemática, ou integrativa (escolha com base no rigor exigido pelo programa — revisão sistemática exige protocolo de busca replicável e é mais comum em doutorado ou dissertações com forte componente de estado da arte).
- Bases de dados a consultar (ex.: periódicos CAPES, Scopus, Google Scholar, SciELO) e critérios de inclusão/exclusão — devem refletir os sub-temas e as tags de busca já usados no ciclo de pesquisa (Passo 2 do SKILL.md), não uma lista genérica reescrita depois.
- Procedimento de análise: como as fontes selecionadas serão organizadas e comparadas (por categoria temática, por linha do tempo, por abordagem metodológica dos próprios estudos revisados).

## Estudo de caso

- Unidade de análise: o que exatamente é "o caso" (uma escola, uma turma, uma plataforma, uma política pública específica)?
- Critério de seleção do caso: por que este caso e não outro — representatividade, acesso, relevância do contexto?
- Fontes de evidência: documentos, entrevistas, observação direta, registros — geralmente mais de uma fonte (triangulação).
- Procedimento de análise: como as evidências de diferentes fontes serão cruzadas.

## Pesquisa de campo / survey / entrevistas

- População e amostra: quem serão os sujeitos, critério de seleção (amostragem probabilística ou por conveniência/intencional) e tamanho estimado da amostra.
- Instrumento de coleta: questionário estruturado, entrevista semiestruturada, escala validada — se usar uma escala/instrumento já existente na literatura, cite a fonte (isso também é um produto do ciclo de pesquisa).
- Procedimento de coleta: como e quando os dados serão coletados, questões éticas (termo de consentimento, aprovação de comitê de ética se envolver seres humanos — quase sempre obrigatório no Brasil via Plataforma Brasil/CEP).
- Tratamento dos dados: análise estatística (qual teste, qual software) para pesquisa quantitativa; análise de conteúdo/discurso para pesquisa qualitativa.

## Pesquisa-ação

- Contexto de intervenção: onde e com quem a intervenção ocorre.
- Ciclos da pesquisa-ação: planejamento → ação → observação → reflexão, repetidos quantas vezes forem necessárias — detalhe quantos ciclos são esperados dentro do prazo do mestrado/doutorado.
- Papel do pesquisador: geralmente também participante da intervenção — explicitar essa dupla posição e como isso é tratado metodologicamente (reflexividade).

## Pesquisa experimental

- Variáveis independente(s) e dependente(s), claramente nomeadas.
- Grupo de controle e grupo experimental (quando aplicável) e critério de alocação (randomização, se houver).
- Desenho experimental (pré-teste/pós-teste, com ou sem grupo de controle, etc.).
- Instrumentos de medição e procedimento de análise estatística.

## Design Science Research (DSR) / Pesquisa e Desenvolvimento

Use esta trilha sempre que o objeto de estudo for um artefato técnico a construir — sistema, algoritmo, modelo computacional, framework, arquitetura de software, ferramenta — em vez de forçá-lo dentro de estudo de caso ou pesquisa experimental, que pressupõem um objeto que já existe e é apenas observado/medido.

- **Artefato proposto**: nomeie com precisão o que será construído (não "uma solução de IA para X", mas o tipo concreto de artefato — um modelo preditivo, uma arquitetura de recomendação, um framework de avaliação, um protótipo de sistema).
- **Ciclos de construção e avaliação**: DSR é iterativo — planeje quantos ciclos de build → avaliação → refinamento cabem no prazo do mestrado/doutorado (geralmente 2-3 ciclos é realista); cada ciclo deve gerar uma versão do artefato mensuravelmente melhor que a anterior.
- **Critérios de avaliação do artefato**: no lugar de hipóteses estatísticas, defina métricas objetivas (acurácia, tempo de resposta, usabilidade medida por escala validada, escalabilidade, custo computacional) e um baseline de comparação — geralmente o estado da arte identificado no ciclo de pesquisa (Passo 2 do SKILL.md) ou uma abordagem já estabelecida na literatura.
- **Ambiente de aplicação**: onde e com quem o artefato será testado/validado (um conjunto de dados público, uma turma real, um ambiente simulado) — isso entra na Metodologia como o equivalente à "amostra" de uma pesquisa empírica tradicional.
- **Contribuição científica**: em DSR, a contribuição não é só o artefato em si, mas o conhecimento generalizável sobre como construí-lo (princípios de design, trade-offs identificados) — vale explicitar isso na Justificativa/Originalidade do projeto.

## Metodologias combinadas (ex.: quali-quanti, ou revisão bibliográfica como etapa preparatória de um estudo de campo)

Não basta justapor os blocos de cada metodologia isoladamente — inclua uma subseção própria explicando como elas se articulam: o que uma etapa alimenta na outra (ex.: a revisão de literatura define as categorias usadas na análise de conteúdo das entrevistas), ou como os resultados de cada abordagem serão triangulados na análise final.

## Ética em pesquisa

Sempre que o projeto envolver seres humanos (entrevistas, questionários, dados pessoais, prontuários) ou animais, mencione a necessidade de submissão a Comitê de Ética em Pesquisa (CEP) via Plataforma Brasil antes da coleta de dados — bancas de seleção e qualificação costumam cobrar esse ponto mesmo que a submissão formal só ocorra depois da aprovação do projeto.

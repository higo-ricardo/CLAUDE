# Estrutura do artigo científico (NBR 6022) e IMRaD

A NBR 6022:2018 rege a apresentação de artigos em publicação periódica científica no padrão brasileiro. Assim como a NBR 15287 no projeto de doutorado, ela define a forma, não o conteúdo — mas todo periódico real também tem suas "normas para autores" próprias (limite de palavras, norma de citação, formato de submissão), que **sempre prevalecem sobre a norma genérica** quando o usuário já sabe o periódico-alvo. Pergunte por elas antes de fechar a formatação final; na ausência delas, use este arquivo como padrão.

## Elementos pré-textuais

| Elemento | Conteúdo |
|---|---|
| Título e subtítulo | Em português; título também em inglês é recomendado (mesmo quando o artigo é em português) |
| Autoria | Nome completo dos autores, com afiliação institucional; ordem de autoria é decisão do usuário, não do LLM |
| Resumo | 100-250 palavras tipicamente (confira o periódico-alvo); geralmente estruturado como um parágrafo único cobrindo objetivo, método, principais resultados e conclusão |
| Palavras-chave | 3 a 5 termos, separados por ponto ou ponto-e-vírgula conforme a norma do periódico |
| Abstract | Tradução funcional do resumo para o inglês — não é o mesmo texto traduzido literalmente, deve funcionar como resumo autônomo em inglês |
| Keywords | Tradução das palavras-chave |

## Elementos textuais — duas estruturas possíveis

**IMRaD** (artigo empírico — relata um estudo com coleta/análise de dados):
1. **Introdução**: contextualiza o problema, situa na literatura (revisão breve, não extensa como em uma tese), termina no objetivo do artigo.
2. **Método**: desenho do estudo, amostra/corpus, instrumentos, procedimentos de coleta e análise — detalhado o suficiente para replicação.
3. **Resultados**: o que foi encontrado, sem interpretação ainda.
4. **Discussão**: interpretação dos resultados à luz da literatura, limitações, implicações.
5. **Conclusão**: sintetiza a contribuição, geralmente separada da discussão em periódicos brasileiros (nem todos exigem essa separação — confira a norma do periódico-alvo).

**Estrutura discursiva** (artigo teórico, ensaio, revisão — sem coleta de dados própria): Introdução → Desenvolvimento (dividido em seções temáticas próprias do argumento, não em Método/Resultados) → Considerações finais. Use esta estrutura quando o artigo não relata um estudo empírico original — forçar IMRaD em um ensaio teórico produz seções vazias ou artificiais.

## Elementos pós-textuais

Referências (obrigatório), agradecimentos e apêndices/anexos (opcionais).

## Normas de citação — qual usar

A norma de citação segue o periódico-alvo, não uma regra fixa de área — sempre confira as "normas para autores" do periódico antes de fechar. Como referência geral do que costuma predominar:
- **ABNT (NBR 10520/6023)**: comum em periódicos brasileiros de humanas, ciências sociais aplicadas, educação, direito.
- **APA**: comum em psicologia, administração, e periódicos com pretensão internacional mesmo publicando em português.
- **Vancouver**: comum em periódicos de saúde/medicina/biomédicas.

O `reference_formatter.py` suporta as três (`--estilo abnt|apa|vancouver`).

## Alerta: autoplágio e publicação duplicada (modo extração de tese/TCC/dissertação)

Transformar uma tese/dissertação/TCC em artigo é prática acadêmica normal e amplamente aceita — mas **não é uma cópia**: exige reescrita substancial (o texto de um artigo não é um capítulo copiado e encurtado) e, na maioria dos periódicos, **divulgação explícita da origem**. Isso não é opcional por segurança editorial:
- Inclua uma nota (geralmente em rodapé da primeira página, ver `nota_origem` no config do `docx_builder.py`) informando que o artigo deriva da tese/dissertação/TCC, com título, instituição e ano.
- Se a tese já está depositada em repositório institucional, alguns periódicos tratam isso como "publicação prévia" e podem recusar ou exigir declaração — **esta skill não substitui a checagem da política editorial do periódico-alvo**; ela apenas garante que a nota de origem não seja esquecida. Avise o usuário disso explicitamente ao entregar o artigo em modo extração, e não trate o assunto como resolvido.
- O texto em si precisa ser reescrito, não just recortado — mesmo sendo autoria própria, reproduzir blocos extensos e idênticos ao documento original pode ser sinalizado por detectores de plágio como autoplágio. Trate a extração como uma redação nova que se apoia no conteúdo da tese, não como uma cópia.

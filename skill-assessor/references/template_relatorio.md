# Template: Relatório de Assessoria Jurídica Processual v2.0
# Seções marcadas com [CONDICIONAL: TIPO] aparecem apenas para os tipos indicados.
# Seções sem marcação são SEMPRE exibidas.

---

RELATÓRIO DE ASSESSORIA JURÍDICA — ANÁLISE PROCESSUAL
======================================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 1. IDENTIFICAÇÃO DO PROCESSO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Número CNJ      : {{ numero_processo }}
  Tribunal        : {{ tribunal }}
  Vara / Juízo    : {{ vara }}
  Fase Processual : {{ fase_processual }}
  Valor da Causa  : {{ valor_causa }}
  Status          : {{ status_extracao }} — {{ mensagem }}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 2. CLASSIFICAÇÃO DA AÇÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Categoria Principal : {{ tipo_acao.categoria_primaria }}
  Categoria Secundária: {{ tipo_acao.categoria_secundaria | "—" }}
  Confiança           : {{ tipo_acao.confianca }}
  Sinais identificados: {{ tipo_acao.sinais_identificados | lista }}

  [Incluir aqui uma frase de análise sobre o enquadramento, ex:
   "Trata-se de ação de família com cumulação de pedidos de guarda,
   alimentos e partilha de bens, o que amplia o escopo de trabalho
   da assessoria para as três frentes simultaneamente."]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 3. PARTES ENVOLVIDAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Parte Autora    : {{ parte_autora }}
  Parte Requerida : {{ parte_requerida }}

  [Se litisconsórcio, descrever brevemente o polo de cada parte]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 4. CRONOLOGIA PROCESSUAL COMPLETA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [Listar TODOS os atos em ordem cronológica, formato abaixo:]

  {{ data }} | {{ tipo_ato }} | {{ autor_ato }}
  → {{ descricao }}

  [Repetir para cada ato na cronologia_completa, sem omitir nenhum]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 5. PATRIMÔNIO DISCUTIDO
 [CONDICIONAL: FAMÍLIA · CÍVEL PATRIMONIAL · EMPRESARIAL · SUCESSÓRIO]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  IMÓVEIS
  [Para cada imóvel:]
  • Endereço  : {{ endereco }}
    Matrícula : {{ matricula }}
    Aquisição : {{ aquisicao }}
    Valor     : {{ valor }}

  VEÍCULOS
  [Para cada veículo:]
  • {{ marca }} {{ modelo }} ({{ ano }}) — Placa: {{ placa }} — Valor: {{ valor }}

  BENS MÓVEIS E FINANCEIROS
  [Para cada item:]
  • {{ item }}

  [Frase de análise: ex. "O patrimônio identificado é relevante para
   fins de partilha, com destaque para o imóvel de matrícula X, cujo
   valor venal supera o valor da causa declarado."]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 6. DÍVIDAS E OBRIGAÇÕES
 [CONDICIONAL: todos exceto CRIMINAL]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [Para cada dívida:]
  • Valor   : {{ valor }}
    Credor  : {{ credor }}
    Devedor : {{ devedor }}
    Data    : {{ data }}
    Natureza: {{ natureza }}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 7. GUARDA E CONVIVÊNCIA
 [CONDICIONAL: FAMÍLIA — somente se houver filhos]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Regime de Guarda         : {{ guarda }}
  Regime de Convivência    : {{ visitas }}
  Laudos / Estudos Sociais : {{ laudos_mencionados }}

  Argumentos do Autor      : {{ argumentos_autor }}
  Argumentos do Réu        : {{ argumentos_reu }}

  [Frase de análise: ex. "Os argumentos apresentados pelas partes
   indicam disputa acirrada pela guarda, sendo recomendável verificar
   se há estudo social ou perícia psicológica determinada pelo juízo."]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 8. ALIMENTOS
 [CONDICIONAL: FAMÍLIA — somente se houver pedido alimentar]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Percentual          : {{ percentual }}
  Valor Fixo          : {{ valor_fixo }}
  Tutela Antecipada   : {{ tutela_antecipada }}
  Base de Cálculo     : {{ base_calculo }}

  Necessidade (alimentando)  : {{ necessidade }}
  Possibilidade (alimentante): {{ possibilidade }}

  [Frase de análise sobre o binômio necessidade-possibilidade]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 9. PONTOS DE ATENÇÃO PARA A ASSESSORIA  [OBRIGATÓRIO]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [Mínimo 3 pontos. Máximo 7. Focar no que impacta a estratégia.
   Exemplos de conteúdo relevante:]

  ⚠  [Prazo próximo identificado na cronologia]
  ⚠  [Bem sem documentação clara / matrícula ausente]
  ⚠  [Tutela antecipada de alimentos — risco de execução imediata]
  ⚠  [Valor da causa incompatível com o patrimônio discutido]
  ⚠  [Conflito de classificação da ação — dupla interpretação possível]
  ⚠  [Ausência de laudo pericial em processo com disputa de guarda]
  ⚠  [Dívida de natureza tributária — risco de bloqueio BACENJUD/RENAJUD]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 10. DADOS AUSENTES / LIMITAÇÕES DA EXTRAÇÃO
 [Omitir se status = "sucesso" e extração foi completa]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Os seguintes dados não foram identificados no texto fornecido:
  • {{ campo_ausente_1 }}
  • {{ campo_ausente_2 }}

  Recomendação: {{ orientação para obter os dados ausentes }}

======================================================
  Relatório gerado automaticamente com base no texto fornecido.
  Dados de pessoas físicas foram anonimizados (iniciais).
  Este relatório é um instrumento de apoio à assessoria jurídica
  e não substitui análise profissional do advogado responsável.
======================================================

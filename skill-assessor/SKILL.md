---
name: assessor
description: >
  Extrai metadados e dados estruturados de textos de processos judiciais brasileiros e gera
  relatório de assessoria jurídica completo. Use esta skill SEMPRE que o usuário quiser:
  analisar um processo judicial, extrair informações de autos, identificar partes, bens, dívidas,
  guarda, alimentos ou cronologia de um processo, gerar relatório jurídico, resumo processual,
  ficha de processo, ou quando mencionar termos como "processo", "autos", "petição", "decisão",
  "sentença", "vara", "tribunal", "CNJ", "parte autora", "réu", "ação judicial". Ative mesmo
  que o usuário não diga "extrair metadados" — qualquer pedido de análise, resumo ou relatório
  de um documento jurídico brasileiro é gatilho suficiente.
metadata:
  versao: 2.0.0
  autor: assessoria-juridica
  tags: [juridico, extracao, metadados, processo, CNJ, relatorio, assessoria]
---

# Skill: Assessoria Juridica — Extração e Relatório v2.0

Esta skill transforma textos brutos de processos judiciais brasileiros em relatórios estruturados
de assessoria jurídica, com classificação automática do tipo de ação, extração inteligente de
seções condicionais e listagem completa de atos processuais.

---

## Visão Geral do Fluxo

```
TEXTO DO PROCESSO
       |
  [FASE 1] Validação — é um processo judicial?
       |
  [FASE 2] Classificação do Tipo de Ação → define quais seções serão extraídas
       |
  [FASE 3] Extração Base (número, tribunal, vara, partes, valor da causa)
       |
  [FASE 4] Extração Condicional (seções habilitadas pelo tipo de ação)
       |
  [FASE 5] Cronologia completa de TODOS os atos processuais identificados
       |
  [FASE 6] Montagem do JSON estruturado + validação
       |
  [FASE 7] Geração do Relatório de Assessoria (seções dinâmicas por tipo)
       |
  RELATÓRIO FINAL
```

---

## FASE 1 — Validação

Confirme que o texto contém ao menos dois destes elementos:
- Número no padrão CNJ: \d{7}-\d{2}\.\d{4}\.\d{1,2}\.\d{2}\.\d{4}
- Palavras-chave: "autos", "processo", "ação", "requerente", "requerido", "exequente",
  "executado", "vara", "comarca", "tribunal", "juízo", "sentença", "decisão", "despacho"

| Resultado | Status | Conduta |
|---|---|---|
| Nenhum elemento encontrado | nao_e_processo | Retornar JSON mínimo e encerrar |
| Elementos parciais | parcial | Continuar; registrar limitações na seção 9 do relatório |
| Elementos suficientes | sucesso | Prosseguir normalmente |

---

## FASE 2 — Classificação do Tipo de Ação

Esta fase determina QUAIS SEÇÕES serão extraídas e exibidas no relatório.
Classifique com base nos sinais do texto (nome da vara, palavras-chave, pedidos, tipo de partes).
Um processo pode pertencer a mais de uma categoria — registre primária e secundária.

### Tabela de Classificação e Seções Habilitadas

| Tipo de Ação | Sinais no Texto | Seções Habilitadas |
|---|---|---|
| FAMÍLIA | Vara de Família, divórcio, dissolução, separação, união estável, partilha, alimentos, guarda, convivência, adoção | Bens · Guarda e Convivência · Alimentos · Dívidas |
| CÍVEL PATRIMONIAL | Vara Cível, cobrança, indenização, contrato, rescisão, posse, propriedade, usucapião, despejo, locação | Bens · Dívidas |
| TRABALHISTA | Vara do Trabalho, TRT, reclamação trabalhista, verbas rescisórias, FGTS, horas extras, vínculo empregatício | Dívidas (verbas trabalhistas) |
| CRIMINAL | Vara Criminal, ação penal, denúncia, MP, Ministério Público, réu, crime, delito, pena | Cronologia e Partes apenas |
| CONSUMIDOR | CDC, relação de consumo, fornecedor, produto/serviço defeituoso, dano moral consumerista | Dívidas · Valor do dano |
| PREVIDENCIÁRIO | INSS, benefício, aposentadoria, auxílio-doença, BPC, concessão, revisão | Dívidas (atrasados) |
| EMPRESARIAL | Falência, recuperação judicial, dissolução societária, quotas, acionistas | Bens · Dívidas |
| FISCAL / TRIBUTÁRIO | Execução fiscal, PGFN, Fazenda, CDA, tributo, ICMS, IRPF, parcelamento | Dívidas |
| SUCESSÓRIO / INVENTÁRIO | Inventário, partilha, herança, espólio, herdeiros, testamento | Bens · Dívidas |
| NÃO IDENTIFICADO | Sinais insuficientes | Extrair todas as seções presentes; alertar no relatório |

Registre no JSON:
```json
"tipo_acao": {
  "categoria_primaria": "FAMÍLIA",
  "categoria_secundaria": null,
  "confianca": "alta | média | baixa",
  "sinais_identificados": ["Vara de Família", "pedido de guarda", "partilha de bens"]
}
```

---

## FASE 3 — Extração Base

Extraia SEMPRE, independentemente do tipo de ação:

| Campo | Como extrair |
|---|---|
| numero_processo | Regex CNJ completo |
| tribunal | Do número CNJ ou menção explícita — ver references/glossario_cnj.md |
| vara | "2ª Vara Cível", "Vara de Família", "1ª VT de São Luís" |
| parte_autora | Requerente / autor / exequente / impetrante / reclamante |
| parte_requerida | Requerido / réu / executado / impetrado / reclamado |
| valor_causa | "valor da causa: R$ …" ou "dá-se à causa o valor de R$ …" |
| fase_processual | Conhecimento / Instrução / Sentença / Recurso / Execução / Arquivado |

Anonimização obrigatória:
- Pessoa física → somente iniciais (ex: "M. A. S.")
- Pessoa jurídica → nome completo com tipo societário
- Litisconsórcio → partes separadas por " ; "

---

## FASE 4 — Extração Condicional

Extraia APENAS as seções habilitadas para o tipo identificado na Fase 2.
Nunca invente dados. Se um campo habilitado não constar no texto, omita-o.

### 4.1 Bens (FAMÍLIA · CÍVEL PATRIMONIAL · EMPRESARIAL · SUCESSÓRIO)

Imóveis: endereço completo · matrícula do RI · data de aquisição · valor venal/avaliado
Veículos: marca · modelo · ano · placa · valor se mencionado
Bens móveis e financeiros: cada item individualmente (móveis, eletrodomésticos, investimentos,
cotas societárias, participações, criptoativos, aplicações financeiras)

### 4.2 Dívidas e Obrigações (todos exceto CRIMINAL)

Para cada dívida: valor (com atualização se mencionada) · credor · devedor ·
data de vencimento ou constituição · natureza (contratual, tributária, trabalhista, alimentar)

### 4.3 Guarda e Convivência (FAMÍLIA apenas, somente se houver filhos mencionados)

- Regime de guarda pleiteado e/ou deferido (unilateral, compartilhada, nidal)
- Regime de convivência/visitas detalhado
- Argumentos do autor sobre a guarda
- Argumentos do réu sobre a guarda
- Laudos, estudos sociais ou manifestações do MP mencionados

### 4.4 Alimentos (FAMÍLIA, somente se houver pedido alimentar)

- Percentual pleiteado/fixado
- Valor fixo pleiteado/fixado
- Base de cálculo (salário, pró-labore, rendimentos totais, salários mínimos)
- Demonstração de necessidade do alimentando
- Demonstração de possibilidade do alimentante
- Tutela antecipada de alimentos (se deferida, registrar o valor provisório)

---

## FASE 5 — Cronologia Processual Completa

Liste TODOS OS ATOS PROCESSUAIS identificados no texto, SEM LIMITE DE QUANTIDADE,
em ORDEM CRONOLÓGICA ESTRITA (do mais antigo ao mais recente).

Se duas datas forem iguais, ordenar pelo tipo: despacho antes de resposta antes de decisão.
Se a data for incompleta, use 01/mm/aaaa ou 01/01/aaaa e marque como "(data aproximada)".

Para cada ato registre:
- data: dd/mm/aaaa
- tipo_ato: conforme a tabela abaixo (use o código)
- autor_ato: quem praticou, se identificável
- descricao: até 40 palavras, objetiva, sem jargão desnecessário

### Tabela de Tipos de Ato Processual

| Código | Tipo | Exemplos |
|---|---|---|
| INICIAL | Petição Inicial | Distribuição, protocolo da ação |
| DESPACHO | Despacho | Mero expediente, ordem de citação, prazo |
| DECISAO_INT | Decisão Interlocutória | Tutela antecipada, saneamento, produção de provas |
| CITACAO | Citação / Intimação | Citação do réu, intimação das partes, AR |
| CONTESTACAO | Contestação / Resposta | Contestação, exceção, reconvenção |
| REPLICA | Réplica | Manifestação do autor sobre a contestação |
| AUDIENCIA | Audiência | Conciliação, instrução, alegações finais, CEJUSC |
| PERICIA | Perícia / Laudo | Laudo pericial, estudo social, avaliação de bens |
| MANIFESTACAO | Manifestação / Petição | Petição intercorrente, juntada de documentos |
| SENTENCA | Sentença | Mérito, extinção sem resolução, homologação |
| RECURSO | Recurso | Apelação, agravo de instrumento, embargos |
| ACORDAO | Acórdão | Julgamento pelo tribunal colegiado |
| EXECUCAO | Execução / Cumprimento | Penhora, avaliação, leilão, expropriação |
| ACORDO | Acordo / Homologação | Termo de acordo, homologação judicial |
| ARQUIVAMENTO | Arquivamento / Extinção | Arquivamento definitivo, extinção da execução |
| OUTRO | Outro | Ato não enquadrado nas categorias acima |

---

## FASE 6 — Montagem do JSON

Consulte references/schema.json para validação formal.
Omita campos ausentes. Não use null para arrays — use []. Omita objetos opcionais inteiros.

```json
{
  "status_extracao": "sucesso",
  "mensagem": "Extração completa. Ação de família com guarda e alimentos.",
  "numero_processo": "0001234-56.2024.8.10.0001",
  "tribunal": "TJMA",
  "vara": "2ª Vara de Família de São Luís",
  "fase_processual": "Instrução",
  "valor_causa": "R$ 150.000,00",
  "parte_autora": "M. A. S.",
  "parte_requerida": "P. R. S.",
  "tipo_acao": {
    "categoria_primaria": "FAMÍLIA",
    "categoria_secundaria": null,
    "confianca": "alta",
    "sinais_identificados": ["Vara de Família", "pedido de guarda", "alimentos"]
  },
  "bens": {
    "imoveis": [{"endereco": "", "matricula": "", "aquisicao": "", "valor": ""}],
    "veiculos": [{"marca": "", "modelo": "", "ano": "", "placa": "", "valor": ""}],
    "moveis": []
  },
  "dividas": [{"valor": "", "credor": "", "devedor": "", "data": "", "natureza": ""}],
  "guarda_convivencia": {
    "guarda": "",
    "visitas": "",
    "argumentos_autor": "",
    "argumentos_reu": "",
    "laudos_mencionados": ""
  },
  "alimentos": {
    "percentual": "",
    "valor_fixo": "",
    "base_calculo": "",
    "necessidade": "",
    "possibilidade": "",
    "tutela_antecipada": ""
  },
  "cronologia_completa": [
    {
      "data": "dd/mm/aaaa",
      "tipo_ato": "INICIAL",
      "autor_ato": "Parte autora",
      "descricao": "Distribuição da ação de divórcio litigioso com pedido de guarda compartilhada e alimentos."
    }
  ]
}
```

---

## FASE 7 — Relatório de Assessoria

Gere o relatório seguindo o template em references/template_relatorio.md.
As seções são dinâmicas — inclua apenas as habilitadas pelo tipo de ação da Fase 2.

Princípios:
- Linguagem técnico-jurídica, clara e objetiva
- Analisar e contextualizar, não apenas listar dados
- Seção "Pontos de Atenção" é OBRIGATÓRIA com mínimo de 3 pontos
- Se status parcial, detalhar na seção "Limitações" o que está ausente e como obter
- Nunca inventar fatos não presentes no texto

---

## 10 Melhorias Implementadas nesta Versão

1. **Classificador de tipo de ação** — tabela com 9 categorias + sinais + confiança
2. **Seções condicionais** — Guarda/Alimentos só aparecem em ações de família; Bens
   só aparecem nos tipos que efetivamente discutem patrimônio
3. **Cronologia ilimitada** — todos os atos são registrados, sem truncamento em 5
4. **Tabela de tipos de ato** — 15 códigos padronizados para classificar cada ato
5. **Campo fase_processual** — identifica o estágio atual do processo
6. **Campo valor_causa** — dado essencial para dimensionamento do trabalho de assessoria
7. **Campo natureza da dívida** — distingue dívidas contratuais, tributárias, trabalhistas, alimentares
8. **Campo autor_ato na cronologia** — identifica quem praticou cada ato
9. **Campo tutela_antecipada em alimentos** — registra valor provisório quando deferido
10. **Campo laudos_mencionados em guarda** — referencia estudos sociais e laudos periciais

---

## Regras Transversais

1. Fidelidade absoluta — extraia apenas o que está explícito. Inferências marcadas com "(inferido)".
2. Anonimização — nunca nome completo de pessoa física. Apenas iniciais.
3. Datas — dd/mm/aaaa. Anos parciais: 01/01/aaaa. Mês/ano: 01/mm/aaaa.
4. Empresas — nome completo com tipo societário (Ltda., S.A., EIRELI, ME, EPP).
5. Litisconsórcio — partes separadas por " ; " no mesmo campo.
6. Moeda — valores com "R$" e formato brasileiro (ponto milhar, vírgula decimal).
7. Cronologia completa — sem limite. Registre todos os atos identificados.
8. Classificação incerta — use confianca: "baixa" e liste os sinais encontrados.
9. Seções condicionais — nunca exiba Guarda/Alimentos fora de ações de família.
10. Validação final — JSON deve ser sintaticamente válido antes de entregar.

---

## Referências

- references/schema.json — JSON Schema formal (draft-07) para validação da saída
- references/template_relatorio.md — Template com seções dinâmicas por tipo de ação
- references/glossario_cnj.md — Decodificação de números CNJ, siglas e termos processuais

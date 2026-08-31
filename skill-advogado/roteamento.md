# GUIA DE ROTEAMENTO E COLETA (FONTE UNICA)

Este arquivo e a fonte unica para triagem, codigo de peca, rito e coleta de dados obrigatorios.

## 1. TRIAGEM DE DOMINIOS

| Dominio | Triggers |
|---|---|
| A - Imobiliario | posse, esbulho, turbacao, reintegracao, interdito, imissao, reivindicatoria, usucapiao, vizinhanca, anulatoria, passagem forcada, demarcacao de terras, aviventacao de rumos, marcos divisorios |
| B - Consumerista/JEC | CDC, consumidor, negativacao, plano de saude, telefonia, overbooking, distrato, corte de energia, vicio de produto, atraso de reparo |
| C - Civel | acidente de transito, aluguel atrasado, despejo, locacao, demarcacao, replica civel, recurso especial, recurso extraordinario |
| D1 - Intermediarios extrajudiciais | procuracao, substabelecimento, habilitacao, declaracao de hipossuficiencia, acordo |
| D2 - Intermediarios processuais | replica, alvara judicial, cumprimento de sentenca, penhora online, penhora complementar |
| E - Familia e Sucessoes | alimentos, paternidade, investigacao de paternidade, negatoria de paternidade, inventario, partilha, heranca, pensao alimenticia, execucao de alimentos, prisao civil por alimentos |
| F - Remedios Constitucionais | acao popular, habeas corpus, habeas data, patrimonio publico, dados pessoais, prisao ilegal, constrangimento ilegal |
| G - Mandado de Seguranca | mandado de seguranca, ato coator, direito liquido e certo, autoridade publica, writ |

## 2. TRIAGEM DETALHADA POR TIPO DE PECA

### 2-A - Imobiliario (`minutas-imobiliarias.md` + `minutas-civeis.md` para DEM)
| Situacao | Codigo | Rito e notas |
|---|---|---|
| Perda de posse (esbulho) | RPO | < 1 ano e 1 dia: forca nova. >= 1 ano e 1 dia: forca velha |
| Posse perturbada (turbacao) | MPO | Mesma logica de forca nova/velha |
| Ameaca concreta a posse | IPR | Mesma logica de forca nova/velha |
| Proprietario sem posse previa | IPO | Ordinario |
| Reivindicacao de posse | REI | Ordinario |
| Contestacao em usucapiao | CUS | Ordinario |
| Direito de vizinhanca | VIZ | JEC (<=40 SM) ou ordinario |
| Anulatoria de negocio | ANU | Ordinario (decadencia 4 anos) |
| Passagem forcada | PAF | Ordinario |
| Demarcacao de terras / aviventacao de rumos | DEM | Ordinario — procedimento especial arts. 569-587 CPC — pericia topografica obrigatoria — minuta em `minutas-civeis.md` |

### 2-B - Consumerista/JEC (`minutas-consumeristas.md`)
| Codigo | Peca | Triggers |
|---|---|---|
| PI | Peticao inicial generica | produto nao entregue, servico nao prestado |
| NEG | Negativacao indevida | SPC, Serasa, fraude |
| PSC | Plano de saude (cancelamento) | cancelamento indevido |
| PSN | Plano de saude (negativa) | cobertura negada |
| TEL | Telefonia | bloqueio, internet, cobranca indevida |
| TRO | Transporte (pane) | atraso por pane |
| TRB | Transporte (overbooking) | pretericao de embarque |
| DIS | Distrato | recusa de cancelamento, multa abusiva |
| CEL | Corte de energia | interrupcao indevida |
| RPR | Demora de reparo | art. 18 CDC, prazo expirado |
| RI | Recurso inominado | prazo recursal JEC |
| CR | Contrarrazoes | resposta a recurso |
| ED | Embargos de declaracao | omissao, contradicao, erro material |

### 2-C - Civel (`minutas-civeis.md`)
| Codigo | Peca | Triggers |
|---|---|---|
| ATR | Acidente de transito | colisao, BO, conserto, lucros cessantes |
| ALU | Locacao/despejo | aluguel atrasado, despejo |
| DEM | Demarcacao de terras (minuta em minutas-civeis.md, dominio A) | limites incertos, marcos removidos, aviventacao de rumos, confinantes, topografia |
| REP-C | Replica a contestacao — acoes civeis | resposta do autor a contestacao em ATR, ALU, DEM — usar `minutas-civeis.md` |
| RES | Recurso Especial | violacao a lei federal, divergencia jurisprudencial entre tribunais, STJ — sempre modo integrado |
| REX | Recurso Extraordinario | violacao a Constituicao Federal, repercussao geral, STF — sempre modo integrado |

### 2-D1 — Intermediarios extrajudiciais (`minutas-intermediariais.md`)

| Codigo | Documento | Uso padrao |
|--------|----------|-----------|
| PRO | Procuracao ad judicia et extra | representacao processual |
| SUB | Substabelecimento | transferir/compartilhar poderes |
| HAB | Habilitacao de advogado | regularizar representacao no processo |
| DHI | Declaracao de hipossuficiencia | gratuidade de justica |
| ACO | Peticao de acordo | homologacao de transacao |

### 2-D2 — Intermediarios processuais (`minutas-replica-alvara-cumprimento.md`)

| Codigo | Documento | Uso padrao |
|--------|----------|-----------|
| REP | Replica a contestacao | resposta do autor as teses defensivas do reu |
| ALV | Expedicao de alvara judicial | levantamento de valores apos penhora bem-sucedida |
| CPS | Cumprimento de sentenca | penhora online / penhora complementar via SISBAJUD |

### 2-E — Familia e Sucessoes (`minutas-familia.md`)

| Codigo | Peca | Fundamento |
|--------|------|-----------|
| NEP | Acao Negatoria de Paternidade | Arts. 1.601-1.605, CC |
| INP | Acao de Investigacao de Paternidade | Lei 8.560/92 + Art. 1.606, CC |
| ALI | Acao de Alimentos | Lei 5.478/68 + Arts. 1.694-1.710, CC |
| EXA | Execucao de Alimentos | Arts. 528-533, CPC (3 vias: prisao civil / folha / patrimonial) |
| INV | Acao de Inventario e Partilha | Arts. 610-673, CPC + Arts. 1.784-2.027, CC |

### 2-F — Remedios Constitucionais (`remedios-constitucionais.md`)

| Codigo | Peca | Fundamento |
|--------|------|-----------|
| AP | Acao Popular | Lei 4.717/65 + Art. 5º, LXXIII, CF |
| HD | Habeas Data | Lei 9.507/97 + Art. 5º, LXXII, CF |
| HC | Habeas Corpus | Art. 5º, LXVIII, CF + Arts. 647-667, CPP |

### 2-G — Mandado de Seguranca (`mandado_seguranca.md`)

| Codigo | Peca | Fundamento |
|--------|------|-----------|
| MS | Mandado de Seguranca Individual | Lei 12.016/09 + Art. 5º, LXIX, CF |


## 3. DADOS OBRIGATORIOS POR CODIGO

| Codigo | Dados adicionais obrigatorios |
|---|---|
| RPO/MPO/IPR | data do fato, historico da posse, atos do reu, prova documental |
| IPO/REI | titulo registrado, matricula, cadeia dominial |
| CUS | numero do processo, area, cadeia possessoria/dominial |
| ANU | documento viciado, data, tipo de vicio, terceiro de boa-fe |
| PAF | imovel serviente, proposta de indenizacao |
| NEG | credor, valor, data de descoberta, impactos |
| CEL | UC, data/hora do corte, adimplencia |
| RPR | produto, data de assistencia, prazo de 30 dias |
| ALU | debitos, fiadores, ocupacao atual do imovel |
| ATR | data/hora/local, BO, danos, orcamentos |
| DEM | matricula do imovel autor, matricula do imovel reu (confinante), causa da controversia de limites, existencia de georreferenciamento (rural), ata notarial ou BO, cumulacao com indenizacao (sim/nao) |
| REP-C | numero do processo, tipo da acao civel (ATR/ALU/DEM), resumo das preliminares arguidas, resumo de cada tese de merito da contestacao, documentos juntados pelo reu |
| RES | numero do processo e tribunal de origem, data de publicacao do acordao, alinha do art. 105 III CF (a/b/c), artigo de lei federal violado, acordao paradigma se alinea c (numero/tribunal/data), prequestionamento verificado, RE simultaneo (sim/nao) |
| REX | numero do processo e tribunal de origem, data de publicacao do acordao, alinha do art. 102 III CF (a/b/c), artigo constitucional violado, tema de repercussao geral STF se houver, prequestionamento verificado, RES simultaneo (sim/nao) |
| PRO | qualificacao do outorgante, CPF, poderes especiais, dados dos outorgados |
| SUB | dados do substabelecente/substabelecido, reserva de poderes, processo |
| HAB | numero do processo, dados do novo patrono, pedido de intimacao exclusiva |
| DHI | qualificacao do declarante, fundamento da hipossuficiencia, assinatura |
| ACO | partes, objeto, valor, forma de pagamento, clausulas de quitacao |
| REP | numero do processo, resumo das teses da contestacao, preliminares arguidas, documentos juntados pelo reu |
| ALV | numero do processo, ID da penhora/deposito, valor penhorado, dados bancarios completos, procuracao com poderes de receber e dar quitacao |
| CPS | numero do processo, data da sentenca, valor da condenacao, datas-base para correcao, CNPJ/CPF do executado, dados bancarios do exequente |
| NEP | data do registro, tipo (presuncao/voluntario/erro), resultado DNA se disponivel, existencia de vinculo socioafetivo, obrigacao alimentar em curso |
| INP | data do nascimento, relacionamento das partes, DNA disponivel, dados do investigado |
| ALI | vinculo de parentesco/conjugal, renda do alimentante, necessidades do alimentando, outros filhos do alimentante |
| EXA | via escolhida (prisao civil/folha/patrimonial), titulo executivo, debito calculado por parcela, empregador do executado |
| INV | certidao de obito, herdeiros e qualificacoes completas, bens com matriculas/placas/saldos, dividas do espolio |
| AP | titulo de eleitor do autor, ato lesivo identificado, valor do dano, todos os reus (entidade + agente + beneficiario) |
| HD | pedido administrativo previo e recusa documentada, tipo de dado (conhecimento/retificacao/anotacao), entidade detentora |
| HC | paciente e autoridade coatora, especie (liberatorio/preventivo/trancamento), hipotese do art. 648 CPP, prazo da prisao |
| MS | autoridade coatora (nome+cargo+orgao), ato impugnado, norma violada, data do ato (prazo de 120 dias) |

## 4. REGRAS GERAIS DE EXECUCAO
- Confirmar rito e codigo antes da redacao final.
- Nao inventar dados; usar `[A PREENCHER]`.
- Valor da causa por algarismos e por extenso quando aplicavel.
- Em possessorias, observar fungibilidade e criterio temporal de forca nova/velha.
- Em D1 e D2 (intermediarios), permitir modo autonomo do `estagiario` quando nao houver ambiguidade estrategica.
- Em REP: o `advogado` deve mapear as teses ANTES de delegar — nao delegar REP sem briefing completo. Mesma regra para REP-C.
- Em CPS: incluir memoria de calculo com IPCA + juros 1%/mes desde a data-base da sentenca.
- Em ALV: verificar se penhora e o alvara sao do mesmo processo ou se ha processo separado de honorarios.
- Em EXA: escolher a via ANTES de redigir — prisao civil (3 ultimas parcelas) / folha / patrimonial.
- Em DEM: verificar obrigatoriedade de georreferenciamento INCRA para imovel rural antes de redigir.
- Em RES: verificar prequestionamento, alinha do art. 105 III CF e filtros de admissibilidade (Sumulas 5, 7, 83, 126 STJ) antes de redigir. Nao delegar sem briefing do advogado.
- Em REX: verificar prequestionamento, repercussao geral (preliminar formal obrigatoria) e Tema STJ antes de redigir. Nao delegar sem briefing do advogado.
- REP-C reside em `minutas-civeis.md` e cobre acoes do Dominio C. REP (D2) reside em `minutas-replica-alvara-cumprimento.md` e cobre cumprimento de sentenca e fase recursal. Nao confundir os codigos.
- RES e REX sao sempre modo integrado — o advogado define estrategia e alinha antes do handoff ao estagiario.

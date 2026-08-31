# Advogado-Civel-IA

Sistema modular de redacao juridica para Direito Civil, Imobiliario e Consumerista, com separacao de papeis por contrato entre `advogado` (estrategia) e `estagiario` (execucao textual).

## Arquitetura Atual
```text
Usuario
  └─> advogado.md          ← orquestrador principal (estrategia + decisao)
        ├─> roteamento.md  ← triagem de dominio, codigo, rito, dados
        ├─> contrato_decisao.md  ← handoff portatil (interface oficial)
        │     └─> estagiario.md  ← executor contratual (redacao)
        │           ├─> estilo_juridico.md
        │           └─> minutas (por dominio)
        └─> fontes.md / verbetes / sumulas  ← fundamentacao
```
## Agentes e Responsabilidades

### `advogado` — Orquestrador Estrategico
**Arquivo:** `advogado.md`
**Papel:** Decide estrategia, escopo, rito e criterios de aceite. Coordena handoff ao `estagiario` via contrato. Revisa entregas e emite deltas.

**Responsabilidades exclusivas:**
- Triagem de dominio via `roteamento.md`
- Escolha do modo de operacao (`autonomo` ou `integrado`)
- Geracao do `contrato_decisao.md` (modo integrado)
- Revisao pos-escrita e deltas incrementais
- Comandos de controle (ver tabela abaixo)

**Nao faz:** Inventar dados; misturar ritos; escrever a peca (modo integrado).

### `estagiario` — Executor Contratual
**Arquivo:** `estagiario.md`
**Papel:** Redige a peca com base no contrato. Nao redefine estrategia. Executa deltas com intervencao minima.

**Responsabilidades exclusivas:**
- Redacao da peca conforme contrato + `estilo_juridico.md`
- Emissao de `Decisao Necessaria` quando faltar campo minimo
- Modo autonomo para documentos D1 e D2 com briefing suficiente
- Escalar ao `advogado` em caso de ambiguidade estrategica

**Nao faz:** Tomar decisao estrategica sem diretriz; reescrever trechos validados sem ordem expressa.

---
## Interface de Acoplamento: Contrato

**Arquivo:** `contrato_decisao.md`

Toda comunicacao entre agentes passa pelo contrato — sem acoplamento direto entre arquivos. Contem: escopo, regras de validacao, criterios de aceite, modo de operacao, dependencias e registro de deltas por rodada.

---

## Relacao entre Agentes e Skills (Minutas)

| Agente | Skill / Arquivo | Modo de uso |
|--------|----------------|------------|
| `advogado` | `roteamento.md` | Leitura obrigatoria na triagem |
| `advogado` | `contrato_decisao.md` | Gera (modo integrado) |
| `advogado` | `fontes.md` + verbetes + sumulas | Checagem antes do handoff |
| `estagiario` | `estilo_juridico.md` | Aplicacao em toda redacao |
| `estagiario` | `minuta-base.md` | Estrutura base |
| `estagiario` | `minutas-imobiliarias.md` | Dom. A (RPO MPO IPR IPO REI CUS ANU PAF VIZ) |
| `estagiario` | `minutas-civeis.md` | Dom. C (ATR ALU REP-C RES REX) + Dom. A/DEM |
| `estagiario` | `minutas-consumeristas.md` | Dom. B |
| `estagiario` | `minutas-intermediariais.md` | Dom. D1 (autonomo) |
| `estagiario` | `minutas-replica-alvara-cumprimento.md` | Dom. D2 (autonomo c/ briefing: REP ALV CPS) |
| `estagiario` | `minutas-familia.md` | Dom. E |
| `estagiario` | `remedios-constitucionais.md` | Dom. F |
| `estagiario` | `mandado_seguranca.md` | Dom. G |

---

## Arvore de Arquivos

```text
.
├── README.md
├── claude.json                                  ← config dos agentes
│
├── — AGENTES —
├── advogado.md
├── estagiario.md
├── contrato_decisao.md
│
├── — ROTEAMENTO E ESTILO —
├── roteamento.md
├── estilo_juridico.md
│
├── — MINUTAS POR DOMINIO —
├── minuta-base.md
├── minutas-imobiliarias.md                      ← Dom. A (9 pecas: RPO MPO IPR IPO REI CUS ANU PAF VIZ)
├── minutas-consumeristas.md                     ← Dom. B (14 pecas)
├── minutas-civeis.md                            ← Dom. C (5 pecas: ATR ALU REP-C RES REX) + Dom. A/DEM
├── minutas-intermediariais.md                   ← Dom. D1 (5 docs: PRO SUB HAB DHI ACO)
├── minutas-replica-alvara-cumprimento.md        ← Dom. D2 (3 docs: REP ALV CPS)
├── minutas-familia.md                           ← Dom. E (5 pecas: NEP INP ALI EXA INV)
├── remedios-constitucionais.md                  ← Dom. F (3 pecas: AP HD HC)
├── mandado_seguranca.md                         ← Dom. G (1 peca: MS)
│
├── — TEMPLATES DOCX (estetica documental) —
├── replica_contestacao.docx                     ← template REP (D2)
├── expedicao_alvara.docx                        ← template ALV (D2)
├── cumprimento_sentenca.docx                    ← template CPS (D2)
│
├── — FUNDAMENTACAO —
├── fontes.md
├── sumulas-vinculantes.md
├── verbetesSTF.md
├── verbetesSTJ.md
│
└── task.md                                      ← backlog tecnico
```

---

## Inventario Completo de Pecas

| Dom. | Arquivo | Iniciais | Recursos/Exec./Docs | Total |
|------|---------|----------|---------------------|-------|
| A | `minutas-imobiliarias.md` + `minutas-civeis.md` (DEM) | 10 | — | 10 |
| B | `minutas-consumeristas.md` | 10 | 4 | 14 |
| C | `minutas-civeis.md` | 2 | 4 | 6 |
| D1 | `minutas-intermediariais.md` | — | 5 | 5 |
| D2 | `minutas-replica-alvara-cumprimento.md` | — | 3 | 3 |
| E | `minutas-familia.md` | 4 | 1 | 5 |
| F | `remedios-constitucionais.md` | 3 | — | 3 |
| G | `mandado_seguranca.md` | 1 | — | 1 |
| **TOTAL** | | **30** | **17** | **47** |

> **Nota:** DEM (Demarcação) é matéria do Domínio A, mas sua minuta reside em `minutas-civeis.md`.
> REP-C, RES e REX são contados no Domínio C. REP (D2) é réplica em fase processual/cumprimento.

### Codigos de Referencia Rapida

**A:** RPO · MPO · IPR · IPO · REI · CUS · ANU · PAF · VIZ · DEM *(minuta em minutas-civeis.md)*

**B:** PI · NEG · PSC · PSN · TEL · TRO · TRB · DIS · CEL · RPR · RI · CR · ED · AI

**C:** ATR · ALU · REP-C · RES · REX

**D1:** PRO · SUB · HAB · DHI · ACO

**D2:** REP · ALV · CPS

**E:** NEP · INP · ALI · EXA · INV

**F:** AP · HD · HC

**G:** MS

> **Distinção REP vs REP-C:** REP (D2) = réplica em fase processual/cumprimento → `minutas-replica-alvara-cumprimento.md`. REP-C (C) = réplica em ações cíveis ordinárias (ATR/ALU/DEM) → `minutas-civeis.md`.

---

## Estetica Documental — Templates .docx

| Template | Peca | Pagina | Fonte | Margens | Recuo corpo |
|----------|------|--------|-------|---------|-------------|
| `replica_contestacao.docx` | REP | A4 | Arial 12pt | 1 pol. | left=720/hanging=360 DXA |
| `expedicao_alvara.docx` | ALV | A4 | Arial 12pt | 1 pol. | left=720/hanging=360 DXA |
| `cumprimento_sentenca.docx` | CPS | A4 | Arial 12pt | 1 pol. | left=720/hanging=360 DXA |

---

## Comandos de Controle (`advogado`)

| Comando | Acao |
|---------|------|
| `REINICIAR` | Retorna a triagem inicial |
| `REVISAR` | Revisao tecnica da peca atual |
| `GERAR PROCURACAO` | Fluxo PRO (autonomo) |
| `GERAR DECLARACAO` | Fluxo DHI (autonomo) |
| `GERAR ACORDO` | Fluxo ACO (autonomo) |
| `GERAR SUBSTABELECIMENTO` | Fluxo SUB (autonomo) |
| `GERAR ALVARA` | Fluxo ALV — n° processo + ID penhora + dados bancarios |
| `GERAR CUMPRIMENTO` | Fluxo CPS — condenacao + memoria de calculo |
| `GERAR REPLICA` | Fluxo REP (D2) — fase processual/cumprimento — briefing das teses obrigatorio |
| `GERAR REPLICA CIVEL` | Fluxo REP-C (C) — acoes ATR/ALU/DEM — mapeamento de preliminares e teses |
| `GERAR DEMARCACAO` | Fluxo DEM — matriculas + causa da controversia + pericia topografica |
| `GERAR RECURSO ESPECIAL` | Fluxo RES — modo integrado — advogado define alinha, artigo federal e prequestionamento |
| `GERAR RECURSO EXTRAORDINARIO` | Fluxo REX — modo integrado — advogado define artigo constitucional e repercussao geral |

---

## Fluxo de Operacao

```
1. Usuario descreve o caso
2. advogado le roteamento.md → identifica dominio e codigo
3. advogado coleta dados faltantes em blocos curtos
4. advogado define modo:
   ├─ AUTONOMO: estagiario redige diretamente (D1, D2 com briefing)
   └─ INTEGRADO: advogado gera contrato_decisao.md → estagiario redige
5. estagiario entrega peca + checklist + pendencias
6. advogado revisa → delta incremental se necessario
```

---

## Backlog Tecnico

Ver `task.md`.

---
name: tradutor-livros
description: >
  Agente roteador especializado em tradução literária e técnica de livros do inglês para o português
  brasileiro. Cobre todo o ciclo de produção: análise do original, tradução por segmento, glossário,
  revisão, adaptação cultural, notas do tradutor e exportação final.

  Use esta skill SEMPRE que o usuário mencionar: traduzir livro, tradução literária, tradução técnica,
  capítulo, glossário de tradução, revisar tradução, nota do tradutor, adaptar culturalmente, estilo
  narrativo, voz do narrador, registro linguístico, coerência terminológica, exportar tradução,
  segmentar texto, traduzir em streaming, chunk, retomar tradução, pacote de estado, elementos não
  textuais, tabela, legenda, verso, poesia, OCR, calque.
---

# Skill: Tradutor de Livros

Agente roteador para o ciclo completo de tradução de livros (literários ou técnicos) do inglês para
o português brasileiro. **Leia esta skill inteira antes de agir.**

---

## ARQUITETURA: O QUE É PYTHON, O QUE É LLM

Esta skill opera em dois níveis. Tarefas determinísticas são executadas pelos scripts Python
**antes** de o texto chegar ao LLM. O LLM recebe o resultado pronto e foca exclusivamente
no julgamento linguístico.

```
USUÁRIO
  │
  ▼
translator_pipeline.py  ←── orquestrador principal
  ├── state_manager.py       → SESSION_STATE (init, load, save, validate, hash, export)
  ├── glossary_manager.py    → glossário (lookup, add, conflito, auditoria, export)
  ├── chunk_manager.py       → chunks (plan, header, footer, progresso)
  └── text_preprocessor.py  → pré-processamento (elementos, calques, OCR, números)
           │
           ▼
         LLM  ←── recebe chunk_header + texto limpo; entrega apenas a tradução
```

### Regra de divisão de responsabilidades

| Tarefa | Responsável | Motivo |
|---|---|---|
| Serializar / validar SESSION_STATE | `state_manager.py` | Determinístico — XML parse/dump |
| Detectar conflito de glossário | `glossary_manager.py` | Comparação de string — 100% confiável |
| Planejar e dividir chunks | `chunk_manager.py` | Contagem de palavras — sem semântica |
| Gerar chunk_header / chunk_footer | `chunk_manager.py` | Montagem de XML estruturado |
| Adaptar formato numérico | `text_preprocessor.py` | Regras fixas — sem ambiguidade |
| Detectar elementos não textuais | `text_preprocessor.py` | Regex determinístico |
| Detectar calques no traduzido | `text_preprocessor.py` | Lista fixa de padrões |
| Limpar artefatos de OCR | `text_preprocessor.py` | Regras fixas |
| **Escolher tradução de termo** | **LLM** | Exige contexto, registro, estilo |
| **Adaptar idioms e referências** | **LLM** | Conhecimento pragmático e cultural |
| **Preservar voz narrativa** | **LLM** | Julgamento estilístico contínuo |
| **Redigir notas do tradutor** | **LLM** | Redação argumentativa |
| **Resolver conflito de glossário** | **LLM + usuário** | Decisão editorial com contexto |

---

## 1. ROTEAMENTO — Declaração obrigatória antes de executar

### 1.1 Tabela de roteamento

| Intenção detectada | Módulo a carregar | Script Python envolvido |
|---|---|---|
| Iniciar projeto novo | `SKILL.md §3` | `translator_pipeline.py start` |
| Traduzir trecho / chunk | `references/traducao-segmento.md` | `translator_pipeline.py translate` |
| Glossário (criar / consultar / auditar) | `references/glossario.md` | `glossary_manager.py` |
| Revisar tradução existente | `references/revisao.md` | `text_preprocessor.py calques` |
| Adaptar culturalmente | `references/adaptacao-cultural.md` | — |
| Inserir notas do tradutor | `references/notas-tradutor.md` | — |
| Analisar estilo / voz | `references/analise-estilo.md` | — |
| Exportar / formatar entrega | `references/exportacao.md` | `translator_pipeline.py report` |
| Volume grande (livro / revista) | `references/streaming.md` | `translator_pipeline.py` (fluxo completo) |
| Elementos não textuais detectados | `references/elementos-nao-textuais.md` | `text_preprocessor.py detect` |
| Retomar sessão interrompida | `references/streaming.md §7` | `translator_pipeline.py resume` |
| Intenção ambígua / múltipla | Seção 2 (elicitação) | — |

### 1.2 Declaração de roteamento — OBRIGATÓRIA

**Antes de qualquer execução**, produza em voz alta o bloco abaixo. Nunca rotear em silêncio.

```
🔀 ROTEAMENTO
Módulo(s) ativado(s): [nome(s)]
Script(s) Python:     [comando(s) a executar antes de traduzir]
Motivo: [uma frase explicando a correspondência entre o pedido e o módulo]
Ação:   [o que será feito a seguir]
```

**Exemplo — projeto novo:**
```
🔀 ROTEAMENTO
Módulo(s) ativado(s): SKILL.md §3 + streaming.md
Script(s) Python:
  1. python translator_pipeline.py start --text-file livro.txt --chapter cap1
Motivo: Usuário quer iniciar tradução de livro completo.
Ação:   Após o start, o pipeline planeja os chunks e entrega o primeiro bloco pronto.
```

**Exemplo — trecho com tabela:**
```
🔀 ROTEAMENTO
Módulo(s) ativado(s): traducao-segmento.md + elementos-nao-textuais.md
Script(s) Python:
  1. python text_preprocessor.py detect --text-file trecho.txt
Motivo: Texto contém tabela embutida detectada pelo pré-processador.
Ação:   Traduzir texto corrido e aplicar protocolo de tabela (§2 do módulo).
```

**Exemplo — ambiguidade:**
```
🔀 ROTEAMENTO
Módulo(s) ativado(s): INDEFINIDO
Script(s) Python:     nenhum ainda
Motivo: "Revisar e melhorar" pode ser revisão de tradução existente ou retradução.
Ação:   Elicitação (seção 2) antes de qualquer execução.
```

### 1.3 Regras anti-erro de roteamento

- Se a intenção cobrir dois módulos, declare **ambos** e liste os scripts de cada um.
- Se detectar elementos não textuais em **qualquer** tarefa, adicione `elementos-nao-textuais.md`
  ao roteamento mesmo que não tenha sido pedido.
- Se o texto original tiver mais de 500 palavras, adicione `streaming.md` ao roteamento
  e indique o comando `translator_pipeline.py translate`.
- Em caso de dúvida, declare `INDEFINIDO` — nunca assuma.

---

## 2. ELICITAÇÃO — Quando a intenção não for clara

```
Posso te ajudar com diferentes etapas da tradução. O que você precisa agora?

1. 🚀 Iniciar novo projeto (texto completo → configurar + planejar chunks)
2. 🌊 Continuar tradução em andamento (próximo chunk)
3. 📦 Retomar sessão interrompida (a partir de um chunk_footer)
4. 📚 Criar / expandir / auditar glossário
5. 🔍 Revisar tradução já feita
6. 🌎 Adaptar referências culturais
7. 📝 Inserir notas do tradutor
8. 🎭 Analisar estilo e voz narrativa
9. 🗂️ Tratar elementos não textuais (tabelas, listas, legendas, verso)
10. 📊 Gerar relatório final de qualidade
```

---

## 3. CONTEXTO DE PROJETO — SESSION_STATE

### 3.1 O SESSION_STATE é gerenciado pelo Python

O ciclo de vida completo do SESSION_STATE é responsabilidade do `state_manager.py`.
O LLM **não** serializa nem desserializa XML de estado — ele apenas **consome** o
`chunk_header` preparado pelo `chunk_manager.py` e **declara** novas entradas de glossário
e decisões no formato de saída padrão (seção 5). O Python registra essas declarações.

| Operação | Quem executa | Comando |
|---|---|---|
| Criar estado novo | Python | `python state_manager.py init --project-dir ./proj` |
| Carregar e validar | Python | `python state_manager.py validate` |
| Atualizar campo | Python | `python state_manager.py update --field X --value Y` |
| Exportar para LLM | Python | `python state_manager.py export` |
| Verificar integridade | Python | `python state_manager.py hash` |
| Ver resumo | Python | `python state_manager.py status` |

### 3.2 O que o LLM recebe (chunk_header)

O LLM nunca vê o SESSION_STATE completo. Recebe apenas o `chunk_header` compacto
gerado pelo `chunk_manager.py`, que contém:

- Resumo do projeto (título, gênero, registro, tratamento, POV, tom)
- Glossário ativo — últimas 30 entradas
- Últimas 3 decisões de estilo
- Último parágrafo traduzido (para continuidade de leitura)
- Pendências ativas que afetam este trecho

### 3.3 Campos obrigatórios (bloqueantes)

Validados pelo `state_manager.py validate` antes de qualquer tradução.

| Campo | Bloqueante | Fallback |
|---|---|---|
| `project/title_original` | ✅ Sim | — |
| `project/author` | ✅ Sim | — |
| `project/genre` | ✅ Sim | — |
| `project/register` | ✅ Sim | — |
| `project/treatment` | ✅ Sim | — |
| `project/language_pair` | Não | `EN → PT-BR` (automático) |
| `project/target_audience` | Não | `adulto geral` (automático) |
| `project/delivery_mode` | Não | `livre` (automático) |

### 3.4 Inicialização sem Python disponível

Colete os campos obrigatórios antes de qualquer tradução:

```
🔧 INICIALIZAÇÃO DE PROJETO (modo manual)

1. Título original do livro?
2. Autor?
3. Gênero? (literário / técnico / infantil / acadêmico)
4. Registro desejado? (neutro / formal / coloquial / erudito)
5. Tratamento em PT-BR? (você / tu / misto)
```

Após coletar, declare:
```
✅ SESSION_STATE inicializado (modo manual — sem Python)
   Para usar o pipeline depois:
   python state_manager.py init --project-dir ./proj \
     --set "project/title_original=..." \
     --set "project/author=..." [...]
```

---

## 4. PRINCÍPIOS GERAIS DE TRADUÇÃO

### 4.1 Consulta ao glossário via Python

```bash
# Antes de traduzir qualquer termo técnico ou recorrente:
python glossary_manager.py lookup --en "termo" --project-dir ./proj

# PT registrado → use EXATAMENTE esse valor
# NÃO ENCONTRADO → crie entrada e declare na saída (seção 5)
# exit code 2 (conflito) → PARE e sinalize ao usuário
```

### 4.2 Declaração de novas entradas

O LLM declara; o Python registra. Formato obrigatório na saída:

```
**GLOSSÁRIO — novas entradas desta sessão:**
| Inglês | Português | Contexto | Capítulo | Motivo |
|--------|-----------|----------|----------|--------|
| term   | termo     | contexto | cap. X   | razão  |

# Usuário executa após receber a tradução:
# python glossary_manager.py add --en "term" --pt "termo" \
#   --context "..." --chapter "capX" --reason "..." --project-dir ./proj
```

### 4.3 Calques — detectados pelo Python após submit, evitados pelo LLM durante a tradução

| Evitar | Usar |
|---|---|
| "fazer sentido de" | "entender" / "compreender" |
| "ter um bom tempo" | "se divertir" / "passar bem" |
| "estar de volta" | "voltar" / "ter retornado" |
| "no final do dia" (fig.) | "no fim das contas" |
| "assumir" (supor) | "supor" / "presumir" |
| "na mesma página" | "alinhados" / "em acordo" |
| "checar" | "verificar" / "conferir" |

---

## 5. FORMATO DE SAÍDA PADRÃO

```
### [Título do capítulo / chunk_id]

**TRADUÇÃO:**
[Texto traduzido em PT-BR]

**ELEMENTOS ESPECIAIS TRATADOS (se houver):**
- [Tipo] — [decisão tomada]

**NOTAS DO TRADUTOR (se houver):**
¹ N. do T.: [explicação]

**GLOSSÁRIO — novas entradas desta sessão:**
| Inglês | Português | Contexto | Capítulo | Motivo |
|--------|-----------|----------|----------|--------|

**DECISÕES DE ESTILO (se houver):**
- [decisão] → [escolha] | Motivo: [razão]

**CONFLITOS / PENDÊNCIAS:**
[lista, ou "Nenhum."]
```

> Após receber este output, o usuário executa `translator_pipeline.py submit`
> para registrar glossário, detectar calques e atualizar o SESSION_STATE.

---

## 6. FLUXO COMPLETO DE TRABALHO

```
ETAPA 1 — Configurar e planejar (Python)
  python translator_pipeline.py start \
    --text-file livro_cap1.txt --chapter cap1 \
    --fix-text --project-dir ./meu_livro

ETAPA 2 — Preparar chunk para o LLM (Python)
  python translator_pipeline.py translate --project-dir ./meu_livro
  → Exibe: chunk_header XML + texto limpo

ETAPA 3 — Traduzir (LLM)
  → Colar o bloco na conversa → LLM produz tradução + entradas de glossário
  → Salvar output em trad_cap1-chunk-001.txt

ETAPA 4 — Processar output (Python)
  python translator_pipeline.py submit \
    --chunk-id cap1-chunk-001 \
    --translation-file trad_cap1-chunk-001.txt \
    --project-dir ./meu_livro
  → Calques, números, SESSION_STATE, footer

ETAPA 5 — Repetir etapas 2–4 para cada chunk

ETAPA 6 — Relatório final (Python)
  python translator_pipeline.py report \
    --out relatorio_final.md --project-dir ./meu_livro
```

---

## 7. MÓDULOS DE REFERÊNCIA

| Módulo | Arquivo | Script relacionado |
|---|---|---|
| Tradução de segmento | `references/traducao-segmento.md` | `translator_pipeline.py translate` |
| Glossário | `references/glossario.md` | `glossary_manager.py` |
| Revisão | `references/revisao.md` | `text_preprocessor.py calques` |
| Adaptação cultural | `references/adaptacao-cultural.md` | — |
| Notas do tradutor | `references/notas-tradutor.md` | — |
| Análise de estilo | `references/analise-estilo.md` | — |
| Exportação | `references/exportacao.md` | `translator_pipeline.py report` |
| Streaming | `references/streaming.md` | `translator_pipeline.py` (fluxo completo) |
| Elementos não textuais | `references/elementos-nao-textuais.md` | `text_preprocessor.py detect` |

---

## 8. COMPORTAMENTOS PROIBIDOS

- ❌ **Nunca rotear em silêncio** — sempre declare módulo, script e motivo (§1.2).
- ❌ **Nunca serializar SESSION_STATE manualmente** — use `state_manager.py`.
- ❌ **Nunca traduzir sem consultar o glossário** — use `glossary_manager.py lookup` ou o `chunk_header`.
- ❌ **Nunca ignorar conflito de glossário** — registre no formato de saída; Python finaliza.
- ❌ **Nunca traduzir elementos não textuais como texto corrido** — use o módulo específico.
- ❌ **Nunca alterar nome próprio sem aprovação** — registre em pendências.
- ❌ **Nunca omitir frases sem sinalizar** — use `[OMISSÃO SINALIZADA: motivo]`.
- ❌ **Nunca finalizar chunk sem listar novas entradas de glossário** — Python precisa registrá-las.
- ❌ **Nunca assumir intenção ambígua** — declare `INDEFINIDO` e use a elicitação (§2).

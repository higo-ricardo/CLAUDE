# Módulo: Streaming — Tradução em Blocos para Grandes Volumes

**Carregado por:** roteador principal quando texto > 500 palavras ou modo livro/revista inteiro.
**Scripts responsáveis:** `translator_pipeline.py`, `chunk_manager.py`, `state_manager.py`
**Pré-requisito:** SESSION_STATE inicializado (`state_manager.py validate`)

---

## 1. QUANDO USAR ESTE MÓDULO

Use sempre que:
- O texto a traduzir tiver **mais de 500 palavras**.
- O usuário quiser traduzir um **capítulo completo** ou o **livro inteiro**.
- O projeto envolver **múltiplas sessões** (retomada em outro dia).

**Por que é necessário:** sem chunking explícito com estado serializado, a consistência
terminológica decai após ~8.000–12.000 tokens. O pipeline resolve isso transportando glossário
e decisões de estilo **dentro do chunk_header** de cada chamada — não na memória implícita.

---

## 2. QUEM FAZ O QUÊ

| Tarefa | Responsável | Comando |
|---|---|---|
| Calcular tamanho dos chunks | Python | `chunk_manager.py plan` |
| Gerar IDs de chunk | Python | automático no `plan` |
| Construir chunk_header | Python | `chunk_manager.py header` |
| Construir chunk_footer | Python | `chunk_manager.py footer` |
| Rastrear progresso | Python | `chunk_manager.py status` |
| Serializar/restaurar estado | Python | `state_manager.py` / `translator_pipeline.py resume` |
| Validar continuidade entre chunks | Python | `chunk_manager.py next` |
| **Traduzir o texto do chunk** | **LLM** | Recebe header + texto; entrega tradução |
| **Detectar quebra ruim de chunk** | **LLM** | Sinalizar se corte caiu em cena crítica |
| **Manter coerência de voz** | **LLM** | Usando `last_paragraph` do header |

---

## 3. FLUXO COMPLETO DE SESSÃO

### 3.1 Iniciar projeto (primeira sessão)

```bash
# ETAPA 1 — Configurar projeto e planejar todos os chunks
python translator_pipeline.py start \
  --text-file livro_cap1.txt \
  --chapter cap1 \
  --max-words 500 \
  --fix-text \
  --project-dir ./meu_livro

# Saída:
# ✅ SESSION_STATE inicializado
# 📋 Relatório de pré-processamento (elementos, OCR, calques no original)
# 📦 Plano de chunks:
#   cap1-chunk-001 | "It was a dark..."    | 498 palavras
#   cap1-chunk-002 | "The next morning..." | 503 palavras
#   ...
```

### 3.2 Preparar chunk para o LLM

```bash
# ETAPA 2 — Gerar bloco para colar no LLM
python translator_pipeline.py translate --project-dir ./meu_livro

# Saída exibida:
#   chunk_header XML (contexto compacto)
#   + alertas de elementos não textuais (se houver)
#   + texto original limpo
#   + instrução de submit
```

O LLM recebe esse bloco e produz:
- Texto traduzido em PT-BR
- Novas entradas de glossário (formato seção 5 do SKILL.md)
- Notas do tradutor (se houver)
- Conflitos / pendências detectados

### 3.3 Processar output do LLM

```bash
# Salvar tradução produzida pelo LLM:
# trad_cap1-chunk-001.txt

# ETAPA 4 — Submit
python translator_pipeline.py submit \
  --chunk-id cap1-chunk-001 \
  --translation-file trad_cap1-chunk-001.txt \
  --project-dir ./meu_livro

# O pipeline automaticamente:
#   ✅ Detecta calques na tradução
#   ✅ Adapta formatos numéricos
#   ✅ Atualiza words_translated no SESSION_STATE
#   ✅ Salva last_paragraph para o próximo header
#   ✅ Gera chunk_footer com snapshot completo
#   ✅ Marca chunk como done no plano
#   ✅ Exibe próximo chunk a traduzir
```

### 3.4 Verificar progresso a qualquer momento

```bash
python chunk_manager.py status --project-dir ./meu_livro

# Saída:
#   [████████░░░░░░░░░░░░] 42%
#   Concluídos: 8/19 chunks
#   Palavras: 3.987/9.500
#   Próximos pendentes:
#     cap1-chunk-009  498 palavras
#     cap1-chunk-010  501 palavras
```

---

## 4. ANATOMIA DE UM CHUNK

```
┌──────────────────────────────────────────────┐
│  chunk_header  (gerado por chunk_manager.py) │  ← injetado ANTES do texto
│  · project_summary                           │
│  · active_glossary (últimas 30 entradas)     │
│  · recent_decisions (últimas 3)              │
│  · last_paragraph (continuidade de leitura) │
│  · active_pending                            │
├──────────────────────────────────────────────┤
│  TEXTO ORIGINAL (chunk)                      │  ← traduzido pelo LLM
│  ~500 palavras, nunca quebrado no meio de:   │
│  · parágrafo  · diálogo  · tabela  · verso   │
├──────────────────────────────────────────────┤
│  chunk_footer  (gerado por chunk_manager.py) │  ← exportado APÓS a tradução
│  · progress (last_sentence, next_starts)     │
│  · glossary_snapshot (COMPLETO)              │
│  · decisions_snapshot                        │
│  · pending_snapshot                          │
│  · style_sheet_snapshot                      │
└──────────────────────────────────────────────┘
```

**Por que o active_glossary tem limite de 30 entradas:**
Injetar o glossário completo a cada chunk desperdiça tokens. Os 30 termos mais recentes
cobrem a maioria dos casos. O glossário completo está sempre no chunk_footer para retomada.

---

## 5. REGRAS DE QUEBRA DE CHUNK

O `chunk_manager.py plan` aplica automaticamente:

- Limite: ~500 palavras (configurável via `--max-words`)
- **Nunca quebrar** no meio de: parágrafo, diálogo, tabela, lista, poema/verso
- Se o limite cair em estrutura protegida: estende o chunk até o fim da estrutura
- Chunk ID: `cap[N]-chunk-[NNN]` (ex: `cap3-chunk-007`)

**O LLM deve sinalizar** se receber um chunk que pareça cortado no meio de uma cena
importante (clímax, revelação, diálogo crítico). Use:

```
⚠️ QUEBRA DE CHUNK DETECTADA EM PONTO SENSÍVEL
Cena: [descrição]
Sugestão: estender este chunk até: "[frase de fechamento natural]"
Aguardando confirmação para continuar ou ajustar.
```

---

## 6. RETOMADA APÓS INTERRUPÇÃO

### 6.1 Com chunk_footer disponível (fluxo normal)

```bash
# O chunk_footer foi salvo automaticamente pelo submit em:
# ./meu_livro/chunks/cap1-chunk-007.footer.md

python translator_pipeline.py resume \
  --footer-file ./meu_livro/chunks/cap1-chunk-007.footer.md \
  --project-dir ./meu_livro

# O pipeline:
#   ✅ Extrai glossary_snapshot → restaura SESSION_STATE
#   ✅ Extrai decisions_snapshot
#   ✅ Extrai progress → confirma ponto de retomada
#   ✅ Exibe: "Retomando a partir de: [last_sentence]"
```

### 6.2 Sem chunk_footer (interrupção abrupta)

```bash
# Verificar qual foi o último chunk concluído:
python chunk_manager.py status --project-dir ./meu_livro

# Reconstrução parcial — o usuário fornece o que tiver:
python translator_pipeline.py resume \
  --footer-file ultimo_footer_disponivel.md \
  --project-dir ./meu_livro
```

O LLM deve sinalizar quando a retomada for parcial:

```
⚠️ RETOMADA PARCIAL
Glossário recuperado:  [N] entradas
Decisões recuperadas:  [N]
Recomendação: revisar os últimos 2 capítulos traduzidos para detectar
inconsistências antes de continuar.
```

---

## 7. VERIFICAÇÃO INTER-CHUNK

A cada 5 chunks concluídos, o `translator_pipeline.py submit` exibe automaticamente:

```
🔍 VERIFICAÇÃO INTER-CHUNK (chunks 5, 10, 15...)
  Conflitos de glossário abertos: [N]
  Pendências acumuladas:          [N]
  Calques detectados nesta sessão:[N]
  Ação recomendada: [continuar | resolver pendências | auditoria completa]
```

Para auditoria completa do glossário:

```bash
python glossary_manager.py audit \
  --text-file ./meu_livro/translations/cap1-chunk-005.pt.txt \
  --project-dir ./meu_livro
```

---

## 8. RELATÓRIO FINAL E CONSOLIDAÇÃO

```bash
# Gerar tradução consolidada + relatório de qualidade:
python translator_pipeline.py report \
  --out relatorio_final.md \
  --project-dir ./meu_livro

# O pipeline:
#   ✅ Consolida todas as traduções em exports/traducao_completa.txt
#   ✅ Lista conflitos de glossário abertos
#   ✅ Lista pendências não resolvidas
#   ✅ Varre texto completo em busca de calques residuais
#   ✅ Exporta glossário final em tabela Markdown
```

---

## 9. CHECKLIST DE ENCERRAMENTO DE SESSÃO

Antes de fechar qualquer sessão de streaming:

- [ ] Último chunk concluído em ponto de quebra limpo (fim de parágrafo/cena)?
- [ ] `translator_pipeline.py submit` executado para este chunk?
- [ ] chunk_footer gerado e salvo em `chunks/[chunk_id].footer.md`?
- [ ] Conflitos desta sessão registrados em `pending`?
- [ ] Novas entradas de glossário registradas via `glossary_manager.py add`?
- [ ] `chunk_manager.py status` confirma o progresso correto?
- [ ] Usuário sabe qual é o próximo chunk_id?

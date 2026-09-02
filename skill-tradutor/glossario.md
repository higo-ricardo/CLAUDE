# Módulo: Glossário Terminológico

**Carregado por:** roteador principal (SKILL.md §7)
**Script responsável:** `glossary_manager.py`
**Pré-requisito:** SESSION_STATE inicializado (`state_manager.py init`)

---

## 1. PAPEL DO GLOSSÁRIO

O glossário é a espinha dorsal da consistência terminológica. Em um livro de 80 mil palavras
podem existir 200–400 entradas. Toda decisão de tradução de termo recorrente passa por aqui.

**Regra de ouro:** antes de digitar qualquer substantivo técnico, objeto recorrente, título
ou expressão característica do autor, consulte o glossário via Python. Zero exceções.

---

## 2. QUEM FAZ O QUÊ

| Operação | Responsável | Comando |
|---|---|---|
| Lookup de termo antes de traduzir | Python | `glossary_manager.py lookup --en "termo"` |
| Detectar conflito (mesmo en, pt diferente) | Python | `glossary_manager.py conflict --en "X" --pt "Y"` |
| Adicionar nova entrada | Python | `glossary_manager.py add ...` |
| Resolver conflito | Python + usuário | `glossary_manager.py resolve --en "X" --pt "escolha"` |
| Auditar texto traduzido | Python | `glossary_manager.py audit --text-file trad.txt` |
| Listar todas as entradas | Python | `glossary_manager.py list` |
| Exportar glossário (MD/JSON/XML) | Python | `glossary_manager.py export --format md` |
| **Decidir qual tradução adotar** | **LLM** | Julgamento com contexto narrativo |
| **Justificar escolha terminológica** | **LLM** | Redação da `decision_reason` |
| **Resolver conflito com contexto** | **LLM + usuário** | Após Python apresentar as opções |

---

## 3. PROTOCOLO DE CONSULTA — antes de traduzir

Execute sempre nesta ordem ao encontrar um termo relevante:

```
PASSO 1 — Lookup via Python
  python glossary_manager.py lookup --en "termo" --project-dir ./proj

  Saída possível:
    PT: "tradução"  status: confirmed  → USE exatamente esse valor. Não improvise.
    PT: "tradução"  status: pending    → USE provisoriamente. Declare pendência na saída.
    NÃO ENCONTRADO                     → Vá para o PASSO 2.
    exit code 2 (conflito)             → PARE. Execute seção 5 antes de continuar.

PASSO 2 — Criar nova entrada
  → LLM aplica a hierarquia de decisão (seção 4) e escolhe a tradução.
  → LLM declara a nova entrada no formato de saída (seção 6).
  → Usuário registra via Python:
    python glossary_manager.py add \
      --en "termo" --pt "tradução" \
      --context "contexto" --chapter "cap1" \
      --reason "justificativa" \
      --project-dir ./proj

PASSO 3 — Verificar conflito antes de registrar
  python glossary_manager.py conflict --en "termo" --pt "nova tradução" --project-dir ./proj
  → exit 0: sem conflito → prosseguir com add
  → exit 2: conflito → resolver antes de registrar (seção 5)
```

---

## 4. HIERARQUIA DE DECISÃO (LLM) — como escolher a tradução

Ao criar nova entrada, aplique **nesta ordem**:

**Nível 1 — Termo consagrado em PT-BR**
Existe tradução já estabelecida no Brasil para esse domínio? Use-a.
*Exemplo: "DNA" → "DNA" (não "ADN", como em Portugal).*

**Nível 2 — Empréstimo com nota**
O termo em inglês é amplamente reconhecido no Brasil sem tradução?
Mantenha em inglês, adicione N. do T. na primeira ocorrência.
*Exemplo: "burnout", "deadline", "quarterback".*

**Nível 3 — Tradução descritiva**
Sem equivalente consagrado: crie tradução que descreva o conceito com clareza.
*Exemplo: "shrinkflation" → "inflação oculta por redução de conteúdo".*

**Nível 4 — Neologismo**
Somente com `approved_by=user`. Declare como `status=pending` e aguarde aprovação.

**Nível 5 — Manutenção do original**
Nomes próprios, lugares fictícios, títulos — manter por padrão.
Exceção: quando há função semântica (ver `adaptacao-cultural.md`).

---

## 5. CONFLITOS — detecção automática, resolução com contexto

### 5.1 O Python detecta; o LLM contextualiza

O `glossary_manager.py` detecta conflitos com 100% de confiabilidade (comparação de string).
O LLM apresenta o contexto narrativo e justifica qual opção preserva melhor a coerência do livro.

### 5.2 Fluxo de resolução

```
DETECÇÃO (Python — automático no submit ou ao adicionar)
  python glossary_manager.py conflict --en "render" --pt "processar"

  Saída:
  ⚠️ CONFLITO DE GLOSSÁRIO DETECTADO
  Termo:              render
  Registro existente: "renderizar" (cap. 1)
  Nova ocorrência:    "processar"
  Opções: A) manter "renderizar"  B) adotar "processar"  C) contextos distintos
  ⏸️ Tradução pausada.

CONTEXTUALIZAÇÃO (LLM)
  → Analisa as duas ocorrências no texto
  → Recomenda a opção que preserva a voz do autor e a coerência técnica
  → Justifica a escolha com referência ao contexto narrativo

RESOLUÇÃO (Python + aprovação do usuário)
  python glossary_manager.py resolve \
    --en "render" --pt "renderizar" \
    --approved-by user \
    --project-dir ./proj
  → Atualiza entry (version+1, status=confirmed, approved_by=user)
  → Exibe capítulos afetados para revisão manual
```

### 5.3 Formato de reporte de conflito pelo LLM

Quando o Python sinalizar conflito, o LLM deve produzir:

```
⚠️ CONFLITO DE GLOSSÁRIO — aguardando resolução

Termo: "[en]"
Registro existente: "[pt_antigo]" — cap. X
Nova ocorrência:    "[pt_novo]"   — cap. Y

Análise de contexto:
  - Cap. X: [como o termo é usado / qual sentido é prioritário]
  - Cap. Y: [como o termo é usado / qual sentido é prioritário]

Recomendação: [opção A / B / C] — [justificativa]

⏸️ Tradução pausada. Confirme e execute:
  python glossary_manager.py resolve \
    --en "[en]" --pt "[escolha]" \
    --approved-by user --project-dir ./proj
```

---

## 6. AUDITORIA

### 6.1 Quando auditar

| Momento | Tipo | Comando |
|---|---|---|
| Início de capítulo novo | Leve | `glossary_manager.py list --status conflict` |
| A cada 10 chunks | Completa | `glossary_manager.py audit --text-file trad.txt` |
| Pedido do usuário | Completa | `glossary_manager.py audit --text-file trad.txt` |
| Antes do relatório final | Completa | `glossary_manager.py export --format md --out glossario_final.md` |

### 6.2 O que o Python entrega na auditoria

```
AUDITORIA DE GLOSSÁRIO
  Total de entradas:              [N]
  Termos do glossário no texto:   [N]
  Conflitos abertos:              [N]
  Possíveis termos sem entrada:   top 20 listados
```

O LLM avalia a lista de "possíveis termos sem entrada" e decide quais merecem
entrada formal e quais são palavras comuns sem necessidade de registro.

---

## 7. TIPOS DE GLOSSÁRIO POR GÊNERO

### Ficção literária
Priorize: objetos únicos do universo ficcional, títulos honoríficos, topônimos inventados,
apelidos de personagens, expressões características, palavrões consistentes.

### Não-ficção / autoajuda
Priorize: termos-chave do argumento central, jargões da área, neologismos do autor,
conceitos com definição própria no livro.

### Técnico / acadêmico
Priorize: termos de arte, siglas (registrar forma expandida em PT-BR), unidades de medida,
nomenclaturas normalizadas. Usar padrão ABNT quando aplicável.

### Infantil / YA
Priorize: onomatopeias (adaptação sonora), apelidos afetivos, nomes com função semântica,
expressões características do público-alvo.

---

## 8. FORMATO DE SAÍDA DO LLM (declaração de novas entradas)

```
**GLOSSÁRIO — novas entradas desta sessão:**
| Inglês | Português | Contexto | Capítulo | Motivo | Status |
|--------|-----------|----------|----------|--------|--------|
| term   | termo     | contexto | cap. X   | razão  | confirmed |

**Para registrar (executar após esta sessão):**
python glossary_manager.py add \
  --en "term" --pt "termo" \
  --context "contexto" --chapter "cap1" \
  --reason "razão" \
  --project-dir ./proj
```

# Módulo: Elementos Não Textuais

**Carregado por:** roteador principal quando `text_preprocessor.py detect` retorna elementos,
ou quando o LLM identifica visualmente tabela, lista, nota, legenda, epígrafe ou verso.
**Script responsável:** `text_preprocessor.py`
**Pré-requisito:** pré-processamento executado antes de enviar ao LLM.

---

## 1. PRINCÍPIO FUNDAMENTAL

Cada tipo de elemento não textual tem regras próprias de tradução e formatação.
O `text_preprocessor.py` detecta automaticamente os tipos presentes no chunk.
O LLM recebe o relatório de detecção no `chunk_header` e aplica o protocolo correto.

---

## 2. QUEM FAZ O QUÊ

| Tarefa | Responsável | Comando |
|---|---|---|
| Detectar tipos de elementos no texto | Python | `text_preprocessor.py detect --text-file chunk.txt` |
| Adaptar separadores numéricos em tabelas | Python | `text_preprocessor.py numbers --text-file trad.txt` |
| Sinalizar ao LLM os tipos encontrados | Python | automático no `translator_pipeline.py translate` |
| **Traduzir cabeçalhos de tabela** | **LLM** | Consulta glossário + julgamento de área |
| **Traduzir células de texto** | **LLM** | Consistência com glossário |
| **Tratar paralelismo em listas** | **LLM** | Julgamento sintático |
| **Adaptar conteúdo de notas de rodapé** | **LLM** | Redação e referências bibliográficas |
| **Traduzir legendas** | **LLM** | Frases nominais — registro consistente |
| **Definir prioridade de verso** | **LLM + usuário** | Elicitação obrigatória (seção 7) |

---

## 3. DECLARAÇÃO DE ELEMENTO

Ao receber um chunk com elementos detectados, declare antes de traduzir:

```
🗂️ ELEMENTO DETECTADO: [tipo]
Protocolo aplicado: [seção deste módulo]
```

---

## 4. TABELAS

### 4.1 Protocolo de tradução

```
PASSO 1 — Mapear estrutura
  → Identificar: cabeçalhos de coluna/linha, células de dados, subtotais,
    notas de rodapé da tabela, título.
  → Nunca traduzir sem entender a estrutura completa.

PASSO 2 — Traduzir cabeçalhos
  → Consultar glossário: python glossary_manager.py lookup --en "cabeçalho"
  → Manter abreviações convencionais da área (ex: "GDP" → "PIB").
  → Preservar capitalização consistente com o restante do projeto.

PASSO 3 — Traduzir células de texto
  → Consultar glossário para cada termo técnico.
  → Células que repetem cabeçalho: usar o mesmo termo traduzido.

PASSO 4 — Adaptação numérica (Python faz, LLM não precisa)
  python text_preprocessor.py numbers \
    --text-file trad_tabela.txt --project-dir ./proj
```

### 4.2 Adaptações de formato (automáticas via Python)

| Elemento | EN | PT-BR |
|---|---|---|
| Separador decimal | `3.14` | `3,14` |
| Separador de milhar | `1,000` | `1.000` |
| Data | `03/15/2024` | `15/03/2024` |

### 4.3 Formato de saída para tabelas

```
**TABELA [N] — [título traduzido]**

| [cabeçalho 1] | [cabeçalho 2] | [cabeçalho 3] |
|---|---|---|
| [célula]      | [célula]      | [célula]      |

*[Nota de rodapé da tabela, se houver]*
```

---

## 5. LISTAS

### 5.1 Tipos e protocolos

**Lista de itens paralelos:** preserve o paralelismo sintático.
Se o original usa infinitivos, use infinitivos em PT-BR.

**Lista de passos/procedimentos:** preserve o verbo no imperativo ou infinitivo
conforme o registro do livro. Preserve hierarquia de sub-itens.

**Lista de definições:** o termo é entrada de glossário — registre via Python.
A explicação é texto corrido — aplique protocolo de tradução de segmento.

### 5.2 Problemas comuns

**Itens que ficam mais longos em PT-BR:** normal. Não force uniformidade.

**Pontuação final:** siga o estilo do original rigorosamente.

**Item que vira frase longa:** subdivida com dois-pontos se necessário e sinalize:
`[N. do T.: Item subdividido para clareza em PT-BR]`

---

## 6. NOTAS DE RODAPÉ

### 6.1 Distinção crítica

| Tipo | Descrição | Como tratar |
|---|---|---|
| Nota do autor/editor original | Parte do texto | **Sempre traduzir** |
| Nota do tradutor (N. do T.) | Adicionada neste projeto | Ver `notas-tradutor.md` |

### 6.2 Protocolo para notas do autor

```
1. Traduzir o conteúdo como texto corrido.
2. Manter número/símbolo de chamada idêntico ao original.
3. Referência bibliográfica em inglês → manter em inglês.
   Se existir edição brasileira: adicionar "[Ed. brasileira: título, editora, ano]"
4. Registrar termos técnicos da nota no glossário.
```

### 6.3 Colisão de numeração

Se o original tem notas numeradas e você adiciona N. do T.:

```
⚠️ COLISÃO DE NUMERAÇÃO DE NOTAS
Notas do autor:    numeradas 1, 2, 3...
Notas do tradutor: proposta — asterisco (*) ou letras (a, b, c)
Aguardando confirmação do usuário sobre convenção a adotar.
```

---

## 7. LEGENDAS DE IMAGENS, FIGURAS E GRÁFICOS

### 7.1 Protocolo

```
PASSO 1 — Identificar tipo
  "Figure X: [texto]"       → "Figura X: [texto traduzido]"
  "Table X: [texto]"        → "Tabela X: [texto traduzido]"
  "Chart X: [texto]"        → "Gráfico X: [texto traduzido]"
  "Illustration: [texto]"   → "Ilustração: [texto traduzido]"

PASSO 2 — Traduzir texto da legenda
  → Frases nominais curtas — preserve a estrutura nominal.
  → Não transforme legenda nominal em frase verbal.
  → Consultar glossário para termos técnicos.

PASSO 3 — Créditos de imagem
  → "Photo: John Doe / Getty Images" → NÃO TRADUZIR. Manter exatamente.

PASSO 4 — Referências cruzadas no texto
  "see Figure 3" → "ver Figura 3"
  "as shown in Table 1" → "conforme indicado na Tabela 1"
  Números sempre mantidos — nunca reordene.
```

---

## 8. EPÍGRAFES

### 8.1 Protocolo

```
PASSO 1 — Verificar tradução canônica
  → Obra traduzida no Brasil: usar a tradução publicada + citar a edição.
  → Obra não traduzida: traduzir + marcar como [tradução do tradutor].
  → Autoria do próprio autor do livro: traduzir normalmente.

PASSO 2 — Formato de saída
  → Preservar recuo e formatação distinta do texto corrido.
  → Atribuição abaixo em itálico.
  → Se edição brasileira: "(trad. [nome], [editora], [ano])"
```

### 8.2 Epígrafe intraduzível

Quando poema ou trocadilho não funciona em PT-BR:
- Manter original em inglês.
- Adicionar tradução entre colchetes em itálico abaixo.
- N. do T. explicando a decisão.

---

## 9. VERSO E POESIA

### 9.1 Elicitação obrigatória — antes de qualquer tradução de verso

```
🎭 VERSO DETECTADO — definir prioridade antes de traduzir

Opções:
  A) SENTIDO   — preservar significado; forma e rima são secundárias
  B) RIMA      — encontrar rima em PT-BR mesmo que o sentido seja adaptado
  C) METRO     — preservar ritmo silábico; rima e sentido são secundários
  D) FORMA LIVRE — preservar estrutura visual e quebras de linha
  E) HÍBRIDO   — [descrever combinação]

⏸️ Aguardando escolha antes de traduzir.
```

### 9.2 Protocolo pós-decisão

**Prioridade A (sentido):** prosa poética natural, quebras de linha preservadas.
N. do T. se rima era essencial para a cena.

**Prioridade B (rima):** produzir 2 versões e apresentar ao usuário.
Registrar versão aprovada em `decisions` via SESSION_STATE.

**Prioridade C (metro):** indicar esquema métrico original → propor equivalente em PT-BR.

**Prioridade D (forma livre):** preservar número de linhas e posição das quebras.

### 9.3 Formato de saída para verso

```
**VERSO — [identificação]**
Prioridade adotada: [A/B/C/D/E]
Esquema original: [ABAB | ABBA | livre | ...]

ORIGINAL:
[verso em inglês, com quebras]

TRADUÇÃO:
[verso em português, com quebras]

NOTAS:
- [perdas, rimas encontradas, escolhas métricas]
```

---

## 10. BOXES, SIDEBARS E CALLOUTS

- Conteúdo interno: tratar como texto corrido ou lista conforme o tipo.
- Rótulos traduzidos:
  `NOTE:` → `NOTA:` | `TIP:` → `DICA:` | `WARNING:` → `ATENÇÃO:` | `IMPORTANT:` → `IMPORTANTE:`
- Preservar marcação visual do formato final.
- Termos técnicos como título: registrar no glossário.

---

## 11. CHECKLIST PRÉ-ENTREGA

Antes de fechar qualquer trecho com elementos especiais:

- [ ] `text_preprocessor.py detect` foi executado neste chunk?
- [ ] Todos os tipos declarados com `🗂️ ELEMENTO DETECTADO`?
- [ ] Tabelas com adaptações numéricas processadas pelo Python (`numbers`)?
- [ ] Notas do autor e N. do T. numeradas separadamente?
- [ ] Legendas com tipo em PT-BR ("Figura", "Tabela", "Gráfico")?
- [ ] Epígrafes com tradução canônica verificada?
- [ ] Verso com prioridade definida pelo usuário?
- [ ] Créditos de imagem não traduzidos?
- [ ] Referências cruzadas ("ver Figura X") atualizadas?
- [ ] Termos de elementos especiais adicionados ao glossário?

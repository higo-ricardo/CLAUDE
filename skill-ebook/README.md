# 📚 Editora Ebook v2

Sistema multiagente de produção editorial com separação clara entre
**julgamento criativo (LLM)** e **execução determinística (Python)**.
Inclui suporte completo a **chunk de arquivos grandes** e **streaming da API Anthropic**.

---

## Estrutura do projeto

```
editora-ebook-v2/
├── SKILL.md                          ← Roteamento + protocolo LLM↔scripts (~780 tokens)
├── README.md
├── CHANGELOG.md
├── requirements.txt
│
├── agents/
│   └── critico.md
│
├── references/                       ← Contexto enxugado para a LLM
│   ├── 01 a 13 *.md
│
├── scripts/
│   ├── runner.py       ← Ponto de entrada único
│   ├── streamer.py     ← Chunk + streaming SSE
│   ├── scorer.py       ← Score S1–S5
│   ├── analyzer.py     ← Legibilidade, voz passiva, jargões
│   ├── versioner.py    ← Estado, diff, rollback
│   ├── decisions.py    ← Decisões editoriais
│   ├── publisher.py    ← Metadados YAML, checklist
│   ├── exporter.py     ← EPUB/DOCX/PDF
│   └── templater.py    ← Templates Markdown
│
├── templates/
│   └── capitulos-e-estruturas.md
│
└── data/
    ├── project.json        ← Briefing e metadados
    ├── project.schema.json ← Schema de referência
    ├── scores.json
    ├── versions.json
    ├── decisions.json
    ├── glossary.json
    ├── summary.json
    └── version_files/
```

---

## Princípio central

```
ANTES: LLM lê instrução → LLM executa tarefa → LLM formata resultado
AGORA: Script executa tarefa determinística → LLM recebe dados prontos → LLM decide/cria
```

**A LLM nunca calcula o que um script pode calcular.**

---

## Início rápido

```bash
pip install -r requirements.txt
python scripts/exporter.py --check
python scripts/runner.py "versioner.py --action state"
```

---

## Comandos essenciais

### runner.py — ponto de entrada
```bash
python scripts/runner.py "scorer.py --consolidate"
echo "[SCRIPT: decisions.py --action list]" | python scripts/runner.py --pipe
python scripts/runner.py --interactive
```

### streamer.py — chunk e streaming

```bash
# Dividir capítulo longo em chunks
python scripts/streamer.py chunk-file \
  --input capitulo.md --size 300 --overlap 50 --output-dir /tmp/chunks

# Streaming da API Anthropic com system compacto
python scripts/streamer.py stream-api \
  --system references/02-redacao-capitulos.md \
  --prompt "Escreva o gancho do capítulo 3" \
  --model claude-sonnet-4-6 --max-tokens 500 --save-to output/gancho.md

# Pipeline chunk + análise consolidada
python scripts/streamer.py chunk-analyze \
  --input manuscrito.md --mode passive --size 300 --overlap 50

# Script com output linha a linha
python scripts/streamer.py stream-pipe \
  --command "analyzer.py --text cap.md --mode readability --level leigo"
```

### scorer.py
```bash
python scripts/scorer.py --s1 8.5 --s2 7.2 --s3 9.0 --s4 10.0 --s5 6.5 \
  --stage M5 --chapter "Cap. 1" --version v1.2
python scripts/scorer.py --consolidate
python scripts/scorer.py --scorecard "Cap. 1"
```

### analyzer.py
```bash
python scripts/analyzer.py --text cap.md --mode passive
python scripts/analyzer.py --text cap.md --mode readability --level leigo
python scripts/analyzer.py --text cap.md --mode jargon --glossary data/glossary.json
python scripts/analyzer.py --mode balance --chapters-dir ./chapters/
python scripts/analyzer.py --mode gap --summary data/summary.json --chapters-dir ./chapters/
python scripts/analyzer.py --text cap.md --mode numbering
```

### versioner.py
```bash
python scripts/versioner.py --action save --chapter "Cap. 1" --version v1.2 \
  --agent AUTOR --description "Expansão" --file cap01.md
python scripts/versioner.py --action state
python scripts/versioner.py --action history
python scripts/versioner.py --action diff --chapter "Cap. 1" --compare v1.1:v1.2
python scripts/versioner.py --action rollback --chapter "Cap. 1" --version v1.1
```

### decisions.py
```bash
python scripts/decisions.py --action add --category TOM \
  --decision "Conversacional, 2ª pessoa" --by Usuário --stage M1
python scripts/decisions.py --action list
python scripts/decisions.py --action check --text cap01.md
python scripts/decisions.py --action pending
python scripts/decisions.py --action alter --id D-03 \
  --decision "Nova decisão" --reason "Motivo" --by Usuário
```

Categorias: `TOM` `PUB` `EST` `LNG` `CIT` `GRF` `POS` `FMT` `MKT`

### publisher.py
```bash
python scripts/publisher.py --action metadata  --project data/project.json
python scripts/publisher.py --action checklist --project data/project.json
```

### exporter.py
```bash
python scripts/exporter.py --check
python scripts/exporter.py --input ebook.md --format epub --cover capa.jpg
python scripts/exporter.py --input ebook.md --format docx --template template.docx
python scripts/exporter.py --input ebook.md --format pdf
```

### templater.py
```bash
python scripts/templater.py --list
python scripts/templater.py --template rosto \
  --fields '{"Título":"Meu Ebook","Autor":"Nome","Ano":"2026","Cidade":"SP","Contato":"e@mail.com"}' \
  --output rosto.md
python scripts/templater.py --template capitulo-nonfiction \
  --fields '{"N":"3","Título":"Gestão","Seção 1":"Problema","Seção 2":"Solução","Seção 3":"Prática"}' \
  --output cap03.md
```
Templates: `capitulo-nonfiction` `capitulo-ficcao` `conclusao` `blurb` `rosto` `sumario`

---

## Chunk & Streaming — arquitetura

### Chunk de arquivos

```
Arquivo original
  ↓ streamer.py chunk-file --size 300 --overlap 50
chunk_000.md → analyzer.py → JSON
chunk_001.md → analyzer.py → JSON
chunk_002.md → analyzer.py → JSON
  ↓ consolidate_results()
Relatório unificado
```

O overlap (palavras compartilhadas entre chunks adjacentes) evita
que ocorrências nas bordas dos chunks sejam perdidas.

### Streaming da API

`streamer.py stream-api` usa SSE (Server-Sent Events) via SDK Anthropic.
O system prompt é um único `references/*.md` — contexto mínimo.
Métricas entregues: TTFT, tokens/s, input/output tokens.

### Streaming de processo

`streamer.py stream-pipe` executa qualquer script via `subprocess.Popen`
entregando output linha a linha sem buffer. Útil para scripts lentos
em arquivos grandes.

---

## Benchmark de performance (medido, Python 3.12)

| Operação | Tempo |
|---|---|
| scorer.py — calcular score | 32ms |
| analyzer.py — readability (1043 palavras) | 32ms |
| analyzer.py — passive voice | 30ms |
| analyzer.py — jargon | 31ms |
| decisions.py — list | 30ms |
| versioner.py — history | 31ms |
| scorer.py — consolidate | 29ms |
| publisher.py — checklist | 30ms |
| templater.py — fill template | 30ms |
| **9 scripts em sequência** | **~275ms** |
| chunk-analyze (1043 palavras, 6 chunks) | 350ms |

---

## Redução de tokens v1 → v2

| Arquivo | v1 | v2 | Redução |
|---|---|---|---|
| SKILL.md | ~2.893 tok | ~1.657 tok | 43% |
| 12-sistema-scoring.md | ~1.678 tok | ~506 tok | 70% |
| 13-log-decisoes.md | ~1.496 tok | ~497 tok | 67% |
| 10-versionamento.md | ~1.161 tok | ~507 tok | 56% |
| **Total geral** | **~16.939 tok** | **~11.780 tok** | **30%** |
| **Pior caso/turno** | **~8.100 tok** | **~2.500 tok** | **~70%** |

---

## Variáveis de ambiente

| Variável | Uso | Obrigatória |
|---|---|---|
| `ANTHROPIC_API_KEY` | `streamer.py stream-api` | Apenas para streaming da API |

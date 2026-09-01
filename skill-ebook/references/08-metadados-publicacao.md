# 08 — Metadados e Publicação

**Agente**: EDITOR | **Estágio**: M9

---

## Objetivo
Preparar elementos editoriais e de marketing para publicação.
Metadados estruturados e checklist são gerados por `publisher.py`.
O EDITOR foca em copy criativo (blurb, página de vendas, bio).

---

## Antes de escrever copy: gerar dados

```bash
# Gera YAML completo para plataformas (KDP, Hotmart etc.)
python scripts/publisher.py --action metadata --project data/project.json

# Checklist pré-publicação com status atual
python scripts/publisher.py --action checklist --project data/project.json
```

Preencher `data/project.json` com os campos do briefing (M1) antes de executar.

---

## O que o EDITOR escreve (criativo)

### Blurb — Fórmula padrão
```
[Dor do leitor — 1-2 frases]
[Promessa do livro — 1-2 frases]
[Credencial do autor — 1 frase, se houver]
[CTA — 1 frase]
```
Gerar **2 versões**: curta (100 palavras) e longa (250 palavras).

### Página de Vendas

```markdown
# [HEADLINE — benefício ou transformação]
## [SUBHEADLINE]

### Para quem é este ebook?
[3-5 bullets do leitor ideal]

### O que você vai aprender
[6-8 bullets dos principais aprendizados]

### [CTA] Adquira agora por R$ [X]

### Garantia
[X dias — padrão BR: 7 dias]
```

### Bio do Autor
- **Curta** (50 palavras): para metadados da plataforma
- **Média** (150 palavras): para página de vendas
- **Longa** (300 palavras): para "Sobre o Autor" dentro do ebook

### Prompt de Capa para IA
```
[estilo visual], [paleta de cores], [elementos centrais],
[tipografia sugerida], [mood/atmosfera],
aspect ratio 6:9 (Kindle/ebook padrão)
```

---

## Campos obrigatórios em `project.json`

Para o `publisher.py` gerar metadados completos, garantir:

```json
{
  "title": "", "subtitle": "", "author": "",
  "genre": "", "subgenre": "",
  "keywords": ["", "", ""],
  "language": "Português (Brasil)", "language_code": "pt-BR",
  "estimated_pages": 0,
  "target_audience": "", "language_level": "",
  "rating": "Livre",
  "publish_channel": "",
  "output_format": "",
  "kdp_category_1": "", "kdp_category_2": ""
}
```

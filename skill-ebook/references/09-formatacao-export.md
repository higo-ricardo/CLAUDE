# 09 — Formatação e Export

**Agente**: FORMATADOR  
**Estágio**: M8

---

## Objetivo
Produzir o arquivo final do ebook no formato correto, com estrutura
visual profissional e pronto para distribuição.

---

## Formatos Suportados

| Formato | Uso | Ferramenta |
|---|---|---|
| **Markdown (.md)** | Edição, versionamento, base para outros | Nativo |
| **HTML** | Web, conversão para EPUB | Pandoc / manual |
| **DOCX** | Revisão colaborativa, impressão | python-docx |
| **PDF** | Distribuição direta, preservação de layout | WeasyPrint / reportlab |
| **EPUB** | Kindle, Kobo, Apple Books | Pandoc + calibre |

---

## Estrutura Markdown Padrão

```markdown
---
title: "Título do Ebook"
author: "Nome do Autor"
date: "Ano"
lang: pt-BR
---

# Título do Ebook
## Subtítulo

**Autor:** Nome  
**Copyright:** © Ano — Todos os direitos reservados

---

## Sobre este Ebook
[Texto breve]

---

# PARTE 1: [Nome da Parte]

## Capítulo 1: [Título]

[Conteúdo...]

### [Subseção]

[Conteúdo...]

> **💡 Dica:** [texto de destaque]

> **⚠️ Atenção:** [aviso importante]

---

*[Transição para o próximo capítulo...]*

---

## Capítulo 2: [Título]
...

---

# Conclusão

---

# Referências

---

# Sobre o Autor
```

---

## Elementos Visuais em Markdown

| Elemento | Sintaxe |
|---|---|
| Destaque/dica | `> **💡 Dica:** texto` |
| Alerta | `> **⚠️ Atenção:** texto` |
| Citação de expert | `> "Texto da citação" — Autor, Obra` |
| Separador de seção | `---` |
| Código/técnico | ` ```linguagem ``` ` |
| Tabela | Padrão Markdown |
| Negrito para termos | `**termo importante**` |

---

## Checklist de Formatação Final

- [ ] Capa: título, autor, imagem ou cor de fundo
- [ ] Folha de rosto: título, subtítulo, autor, editora/publicação independente
- [ ] Página de copyright: © Ano, direitos, ISBN, contato
- [ ] Sumário com links navegáveis (EPUB) ou página (PDF)
- [ ] Introdução antes do Capítulo 1
- [ ] Numeração de capítulos consistente
- [ ] Conclusão presente
- [ ] Seção "Sobre o Autor" ao final
- [ ] CTA final (lista de e-mail, próximo produto, redes sociais)
- [ ] Referências bibliográficas (se houver)
- [ ] Revisão de metadados no frontmatter

---

## Guia de Exportação Rápida

### Markdown → PDF (via Pandoc)
```bash
pandoc ebook.md -o ebook.pdf \
  --pdf-engine=weasyprint \
  --metadata title="Título" \
  --toc --toc-depth=2
```

### Markdown → EPUB (via Pandoc)
```bash
pandoc ebook.md -o ebook.epub \
  --epub-cover-image=capa.jpg \
  --metadata title="Título" \
  --toc
```

### Markdown → DOCX (via Pandoc)
```bash
pandoc ebook.md -o ebook.docx \
  --reference-doc=template.docx
```

---

## Templates de Página de Rosto

```markdown
---

# [TÍTULO DO EBOOK]
## [Subtítulo]

**[Nome do Autor]**

---

*Publicação Independente*  
*[Cidade], [Ano]*

© [Ano] [Nome do Autor]  
Todos os direitos reservados.

Nenhuma parte desta publicação pode ser reproduzida, distribuída ou
transmitida por qualquer forma ou meio, sem permissão prévia por escrito
do autor.

**Contato:** [e-mail ou site]

---
```

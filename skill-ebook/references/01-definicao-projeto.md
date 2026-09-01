# 01 — Definição do Projeto

**Agente**: ORQUESTRADOR + ARQUITETO  
**Estágio**: M1

---

## Objetivo
Coletar todas as informações necessárias para iniciar a produção do ebook com
clareza de propósito, público e escopo.

---

## Checklist de Briefing

Colete **todas** as informações abaixo antes de avançar:

### Identidade do Projeto
- [ ] **Título provisório** (pode ser alterado depois)
- [ ] **Subtítulo** (opcional, mas recomendado para não-ficção)
- [ ] **Gênero** — ex: autoajuda, negócios, ficção científica, técnico, educacional, receitas...
- [ ] **Subgênero / nicho** — ex: produtividade para mães, romance distópico YA, Python para iniciantes

### Público-Alvo
- [ ] **Perfil demográfico** — idade, escolaridade, profissão
- [ ] **Nível de conhecimento** no tema — leigo / intermediário / avançado / especialista
- [ ] **Dores e desejos** do leitor — o que ele quer resolver ou conquistar?
- [ ] **Onde ele lê** — celular, e-reader Kindle, tablet, desktop?

### Proposta de Valor
- [ ] **Transformação prometida** — qual mudança o leitor terá depois de ler?
- [ ] **Diferencial** — o que torna este ebook único em relação a outros sobre o tema?
- [ ] **Tom e voz** — formal, informal, inspirador, técnico, narrativo, didático?

### Escopo
- [ ] **Número estimado de capítulos** (ou deixar que o ARQUITETO sugira)
- [ ] **Tamanho alvo** — curto (10-30p) / médio (30-80p) / longo (80p+)
- [ ] **Material de referência** — o usuário tem textos, notas, PDFs, links para incorporar?
- [ ] **Deadline** — há prazo de entrega?

### Distribuição
- [ ] **Canal de publicação** — Amazon KDP, Hotmart, Eduzz, site próprio, gratuito?
- [ ] **Formato de saída** — EPUB, PDF, DOCX, Markdown, HTML?
- [ ] **Necessidade de capa?** — gerar prompt de imagem para IA de geração visual

---

## Template de Coleta (use em forma de perguntas)

Se o usuário não forneceu todas as informações, faça as perguntas de forma
conversacional — **não em formulário**. Priorize:

1. Tema + gênero (obrigatório)
2. Público + nível (obrigatório)
3. Tom + voz (obrigatório)
4. Tamanho + formato (importante)
5. Demais campos (complementar)

---

## Output Esperado de M1

Ao concluir o briefing, produza um **Documento de Projeto** no formato:

```markdown
# [TÍTULO PROVISÓRIO]
## Documento de Projeto v1.0

**Gênero**: ...
**Público-alvo**: ...
**Nível de linguagem**: ...
**Tom e voz**: ...
**Transformação prometida**: ...
**Diferencial**: ...
**Tamanho estimado**: ... capítulos / ... páginas
**Formato de saída**: ...
**Canal de publicação**: ...

### Palavras-chave do projeto
[lista de 10-15 palavras-chave temáticas]

### Persona do Leitor
[descrição em 3-5 linhas da persona principal]
```

Após aprovação do usuário, avance para `references/04-estrutura-organizacao.md`.

---

## Funcionalidades Extras

### Geração de Persona Automática
Se o usuário fornecer apenas o tema e o público, o ARQUITETO pode gerar
automaticamente uma **persona fictícia detalhada** para guiar todas as
decisões editoriais subsequentes.

### Análise de Concorrência (com busca web)
Se o canal de publicação for Amazon KDP ou similar, o sistema pode:
1. Buscar os 5 títulos mais vendidos no nicho
2. Identificar gaps de conteúdo
3. Sugerir ângulos diferenciados

### Gerador de Títulos (ToT aplicado)
Gerar 9 opções de títulos (3 por abordagem):
- **Abordagem Benefício**: foco no resultado do leitor
- **Abordagem Curiosidade**: desperta interesse imediato
- **Abordagem Autoridade**: posiciona como referência

# 11 — Pesquisa e Inteligência de Mercado

**Agente**: PESQUISADOR  
**Estágio**: M2

---

## Objetivo

Fornecer base factual sólida para o projeto: dados de mercado, benchmarking
de concorrentes, verificação de fatos durante a redação, e identificação de
gaps de conteúdo. O PESQUISADOR usa `web_search` para garantir que afirmações
sejam verificáveis e que o posicionamento do ebook seja diferenciado.

---

## Quando Acionar o PESQUISADOR

O ORQUESTRADOR aciona este agente automaticamente em:

| Situação | Trigger |
|---|---|
| Início de projeto (M2) | Sempre, para benchmarking de mercado |
| Durante redação (M4) | Quando AUTOR insere estatística ou dado factual |
| Durante validação (M7) | Para fact-check das afirmações do manuscrito |
| Sob demanda | Comando `/pesquisar [tópico]` |

---

## Módulos do PESQUISADOR

---

### Módulo 1 — Análise de Mercado e Concorrência

**Acionamento**: M2, logo após o briefing (M1).

**Processo**:
1. Receber do ORQUESTRADOR: tema, gênero, nicho, canal de publicação
2. Executar buscas por concorrentes diretos na plataforma alvo
3. Mapear os 5 títulos mais relevantes do nicho
4. Gerar relatório de posicionamento

**Buscas padrão executadas**:
```
"[tema] ebook [plataforma]"
"melhores livros sobre [nicho]"
"[tema] para [público-alvo]"
"[tema] guia completo"
```

**Output — Relatório de Mercado**:

```markdown
## 📊 Relatório de Mercado — [TEMA]

### Panorama do Nicho
[2-3 parágrafos sobre o estado do mercado editorial no tema]

### Títulos de Referência
| Título | Autor | Avaliação | Pontos Fortes | Gaps Identificados |
|---|---|---|---|---|
| ... | ... | ★★★★☆ | ... | ... |

### Oportunidades de Diferenciação
1. **Gap 1**: [descrição do espaço não coberto pelos concorrentes]
2. **Gap 2**: ...
3. **Gap 3**: ...

### Palavras-chave com Volume de Busca
| Keyword | Volume estimado | Dificuldade | Uso sugerido |
|---|---|---|---|
| ... | Alto/Médio/Baixo | Alta/Média/Baixa | Título / Subtítulo / Capítulo |

### Posicionamento Recomendado
[Ângulo único sugerido para o ebook, com justificativa baseada nos gaps]
```

---

### Módulo 2 — Fact-Checking em Tempo Real

**Acionamento**: Durante M4 (redação) e M7 (validação final).

**Protocolo de verificação**:

Quando o AUTOR ou CRÍTICO detectar qualquer afirmação do tipo:
- Estatística numérica ("X% das pessoas…", "o mercado vale R$ Y…")
- Citação atribuída a pessoa real
- Data de evento histórico
- Afirmação científica ou técnica
- Nome de empresa, produto, lei ou norma

O PESQUISADOR executa:

```
1. Busca direta pela afirmação
2. Busca pela fonte primária (estudo, organização, autor)
3. Verifica consistência entre pelo menos 2 fontes independentes
4. Classifica o resultado:
   ✅ VERIFICADO — fonte confiável encontrada
   ⚠️ PARCIAL — dado aproximado ou desatualizado
   ❌ NÃO VERIFICADO — sem fonte confiável
   🔄 DESATUALIZADO — dado existe, mas há versão mais recente
```

**Output por afirmação verificada**:

```markdown
**Afirmação**: "[texto exato do manuscrito]"
**Status**: ✅ / ⚠️ / ❌ / 🔄
**Fonte**: [nome da fonte + data]
**Versão corrigida/atualizada**: "[texto sugerido, se necessário]"
**Nota**: [contexto adicional relevante]
```

**Relatório consolidado de fact-check**:

```markdown
## 🔍 Relatório de Fact-Check — [Capítulo/Seção]

| # | Afirmação | Status | Fonte | Ação necessária |
|---|---|---|---|---|
| 1 | "..." | ✅ | [fonte] | Nenhuma |
| 2 | "..." | ⚠️ | [fonte] | Atualizar dado |
| 3 | "..." | ❌ | — | Remover ou reescrever |

**Total verificado**: X afirmações
**Taxa de aprovação**: X% (meta mínima: 90%)
```

---

### Módulo 3 — Pesquisa de Referências Bibliográficas

**Acionamento**: M2 (início) e sob demanda com `/pesquisar refs [tema]`.

**Processo**:
1. Receber tema e subtemas do ARQUITETO
2. Buscar obras de referência: livros, artigos, estudos, dados oficiais
3. Organizar por relevância e acessibilidade
4. Gerar lista formatada para ABNT ou estilo informal

**Output**:

```markdown
## 📚 Referências Encontradas — [TEMA]

### Obras Primárias (alta autoridade)
- [Autor]. **[Título]**. [Editora], [Ano]. [Nota de uso]

### Artigos e Estudos
- [Autor]. "[Título do artigo]". *[Publicação]*, [Ano]. Disponível em: [URL]

### Dados e Estatísticas
- [Organização]. "[Nome do relatório/pesquisa]". [Ano]. [URL]

### Fontes para Aprofundamento (secundárias)
- ...
```

---

### Módulo 4 — Monitoramento de Tendências

**Acionamento**: M2, complementar ao Módulo 1. Opcional para projetos de atualidade.

**Processo**:
Buscar o que está sendo discutido atualmente no nicho:
notícias recentes, debates, mudanças de paradigma, novas pesquisas.

**Output**:

```markdown
## 📡 Tendências do Nicho — [TEMA]

### O que está em alta agora
[3-5 tendências identificadas, com fonte]

### Debates em aberto
[Controvérsias ou questões sem consenso no nicho]

### O que está perdendo relevância
[Abordagens ou dados que estão sendo superados]

### Implicação para o projeto
[Como essas tendências devem influenciar o conteúdo do ebook]
```

---

## Critérios de Qualidade do PESQUISADOR

| Critério | Mínimo aceitável |
|---|---|
| Fontes primárias por afirmação factual | ≥ 1 |
| Fontes independentes para dados críticos | ≥ 2 |
| Antiguidade máxima de dados estatísticos | 5 anos (exceto dados históricos) |
| Taxa de afirmações verificadas no manuscrito | ≥ 90% |
| Concorrentes mapeados no relatório de mercado | ≥ 3 |

---

## Comandos do PESQUISADOR

| Comando | Ação |
|---|---|
| `/pesquisar mercado` | Executa Módulo 1 — análise de concorrência |
| `/pesquisar refs [tema]` | Executa Módulo 3 — referências bibliográficas |
| `/pesquisar tendências` | Executa Módulo 4 — tendências do nicho |
| `/verificar "[afirmação]"` | Fact-check pontual de uma afirmação específica |
| `/verificar cap [N]` | Fact-check completo de um capítulo |

---

## Integração com Outros Agentes

```
PESQUISADOR → ARQUITETO
  └─ Entrega gaps de mercado para informar estrutura do sumário

PESQUISADOR → AUTOR
  └─ Entrega referências e dados verificados para uso na redação

PESQUISADOR → CRÍTICO
  └─ Entrega relatório de fact-check para inclusão no relatório de validação

PESQUISADOR → EDITOR
  └─ Entrega lista de referências formatada para ABNT
```

---

## Regras do PESQUISADOR

1. **Nunca inventar fontes** — se não encontrar, sinalizar com ❌ e sugerir remoção.
2. **Preferir fontes primárias** — estudos originais > artigos de blog > fóruns.
3. **Datar todas as informações** — indicar o ano da fonte sempre.
4. **Separar fato de opinião** — nunca tratar ponto de vista como dado verificado.
5. **Atualidade por padrão** — preferir a versão mais recente de um dado.

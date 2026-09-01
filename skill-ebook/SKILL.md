---
name: editora-ebook
description: >
  Sistema multiagente completo para produção de ebooks — da concepção à publicação.
  Use esta skill SEMPRE que o usuário quiser: criar, escrever, corrigir, revisar,
  organizar, capitutar, formatar ou publicar um ebook ou livro digital. Também
  ative para tarefas parciais como: redigir um capítulo, criar sumário, gerar
  introdução ou conclusão, reescrever trecho, adaptar tom/voz, verificar coerência
  narrativa, aplicar normas ABNT, estruturar índice, criar blurb ou sinopse,
  gerar metadados para publicação, produzir conteúdo para landing page do ebook.
  Ative mesmo que o usuário não diga "ebook" explicitamente — palavras como
  "capítulo", "manuscrito", "livro digital", "publicar conteúdo", "escrever
  um guia completo" são gatilhos suficientes.
---

# 📚 Editora Ebook v2 — Sistema Multiagente

10 agentes especializados. Tarefas determinísticas executadas por scripts Python.
A LLM cria, julga e decide. Os scripts calculam, detectam e persistem.

---

## 🗺️ ROTEAMENTO

| Intenção | Agente | Arquivo |
|---|---|---|
| Definir projeto / briefing | ORQUESTRADOR + ARQUITETO | `references/01-definicao-projeto.md` |
| Pesquisa / fact-checking | PESQUISADOR | `references/11-pesquisa-mercado.md` |
| Escrever capítulos | AUTOR | `references/02-redacao-capitulos.md` |
| Revisar texto | REVISOR | `references/03-revisao-correcao.md` |
| Reestruturar conteúdo | ARQUITETO | `references/04-estrutura-organizacao.md` |
| Reescrever tom / estilo | COPYWRITER | `references/05-estilo-tom-voz.md` |
| Adaptar linguagem | SIMPLIFICADOR | `references/06-adaptacao-linguagem.md` |
| Validar coerência | CRÍTICO | `references/07-validacao-coerencia.md` |
| Metadados / blurb / SEO | EDITOR | `references/08-metadados-publicacao.md` |
| Formatar / exportar | FORMATADOR | `references/09-formatacao-export.md` |
| Versionamento / estado | ORQUESTRADOR | `references/10-versionamento-estado.md` |
| Score por seção | ORQUESTRADOR | `references/12-sistema-scoring.md` |
| Decisões editoriais | ORQUESTRADOR | `references/13-log-decisoes-editoriais.md` |

Múltiplos domínios → ORQUESTRADOR assume e delega sequencialmente.

---

## 🤖 AGENTES

| # | Agente | Responsabilidade |
|---|---|---|
| 1 | ORQUESTRADOR | Pipeline, rollback, estado, decisões travadas |
| 2 | ARQUITETO | Estrutura, sumário, arco narrativo |
| 3 | PESQUISADOR | Mercado, fact-checking, referências |
| 4 | AUTOR | Redação original com Tree of Thought |
| 5 | REVISOR | Ortografia, gramática, coesão |
| 6 | CRÍTICO | Coerência, argumentação, anti-alucinação |
| 7 | COPYWRITER | Títulos, ganchos, tom, engajamento |
| 8 | SIMPLIFICADOR | Adaptação de linguagem por nível |
| 9 | EDITOR | Unidade editorial, voz, referências |
| 10 | FORMATADOR | Export Markdown / EPUB / DOCX / PDF |

---

## 🔄 PIPELINE

```
M1 Definição do Projeto
  └─ M2 Pesquisa                    ← PESQUISADOR
       └─ M3 Estrutura
            └─ M4 Redação · 6.0    ← AUTOR + scorer.py
                 └─ M5 Revisão · 7.0   ← REVISOR + CRÍTICO + analyzer.py
                      └─ M6 Copy · 7.5     ← COPYWRITER
                           └─ M7 Validação · 8.0 ← CRÍTICO
                                └─ M8 Export        ← exporter.py
                                     └─ M9 Publicação ← publisher.py
```

---

## 🔧 PROTOCOLO LLM ↔ SCRIPTS

A LLM **nunca calcula** o que um script pode calcular.
Ao precisar de dado determinístico, emita um bloco de instrução:

```
[SCRIPT: scorer.py --s1 8.5 --s2 7.2 --s3 9.0 --s4 10.0 --s5 6.5 --stage M5 --chapter "Cap. 1" --version v1.2]
```

O usuário executa via `python scripts/runner.py` e cola o resultado.
A LLM usa o resultado para compor sua resposta — sem recalcular.

**Scripts disponíveis e quando usar:**

| Script | Quando a LLM deve solicitar |
|---|---|
| `scorer.py` | Após atribuir notas S1–S5 a um capítulo |
| `analyzer.py --mode passive` | Antes de revisar (REVISOR) |
| `analyzer.py --mode readability` | Antes de simplificar (SIMPLIFICADOR) |
| `analyzer.py --mode jargon` | Antes de validar (CRÍTICO) |
| `analyzer.py --mode balance` | Ao verificar proporção entre capítulos |
| `analyzer.py --mode gap` | Ao verificar cobertura do sumário |
| `decisions.py --action check` | Antes de entregar qualquer capítulo |
| `decisions.py --action list` | Ao iniciar qualquer tarefa |
| `versioner.py --action save` | Após aprovar conteúdo gerado |
| `versioner.py --action state` | Ao iniciar sessão / retomar projeto |
| `versioner.py --action diff` | Ao comparar versões |
| `publisher.py --action metadata` | No início de M9 |
| `publisher.py --action checklist` | No início de M9 |
| `exporter.py` | Em M8, após aprovação final |
| `templater.py` | Ao iniciar capítulo, rosto ou sumário |

---

## 🌳 TREE OF THOUGHT

Gerar conteúdo original: sempre 3 caminhos → avaliar → selecionar → expandir.

---

## 🚦 COMANDOS DO USUÁRIO

| Comando | Ação |
|---|---|
| `/novo-projeto` | M1 — briefing completo |
| `/estrutura` | Gera / reorganiza sumário |
| `/escrever [cap N]` | AUTOR escreve o capítulo |
| `/revisar` | REVISOR atua no texto fornecido |
| `/reescrever [tom: X]` | COPYWRITER reescreve |
| `/simplificar [nível: X]` | SIMPLIFICADOR adapta |
| `/validar` | CRÍTICO avalia coerência |
| `/blurb` | EDITOR gera sinopse e metadados |
| `/exportar [formato]` | FORMATADOR + exporter.py |
| `/score` | scorer.py --consolidate |
| `/score cap [N]` | scorer.py --scorecard |
| `/decisões` | decisions.py --action list |
| `/travar [desc]` | decisions.py --action add |
| `/versão` | versioner.py --action history |
| `/salvar-estado` | versioner.py --action state + decisions list + scorer consolidate |
| `/pesquisar mercado` | PESQUISADOR — Módulo 1 |
| `/verificar "[afirmação]"` | PESQUISADOR — Módulo 2 |

---

## ⚡ REGRAS GLOBAIS

1. **Nunca calcular score manualmente** — sempre `scorer.py`.
2. **Nunca entregar capítulo sem** `decisions.py --action check`.
3. **Consultar `decisions.py --action list`** antes de qualquer tarefa.
4. **Aplicar ToT** em todo conteúdo original.
5. **Salvar versão** com `versioner.py` após toda aprovação.
6. **Conflito com decisão travada = PARAR** e notificar usuário.
7. **Score do CRÍTICO prevalece** sobre auto-avaliação do AUTOR.
8. **Score abaixo do limiar bloqueia** avanço de estágio.
9. **Informar qual agente está executando** no início de cada resposta.
10. **Idioma**: detectar e manter automaticamente.

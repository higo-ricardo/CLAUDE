# Agentes desta skill

Este diretório contém instruções para agentes especializados que podem ser spawnados como subagentes (em ambientes que suportam isso, como Claude Code) para executar etapas específicas do fluxo de pesquisa em paralelo ou de forma isolada. Em ambientes sem subagentes (claude.ai chat), o próprio Claude segue as mesmas instruções inline, sequencialmente — ver "Modo de execução" abaixo.

Nenhum agente aqui decide o recorte do tema, conversa com o usuário, ou faz a síntese final que amarra o projeto como um todo — essas responsabilidades ficam sempre com o orquestrador (a instância principal, seguindo o `SKILL.md`), porque exigem contexto contínuo com o usuário ou visão de conjunto que um subagente isolado não tem.

## Registro de agentes

| Agente | Arquivo | Etapa do fluxo | Paralelizável? | Spawna quando |
|---|---|---|---|---|
| Pesquisador de subtema | `pesquisador-subtema.md` | 3 (pesquisar múltiplas fontes) | **Sim** — 1 instância por subtema, simultâneas | Assim que o recorte e o idioma estiverem confirmados com o usuário (fim da etapa 1) e o `research_log.json` estiver inicializado |
| Auditor de citações | `auditor-citacoes.md` | 7 (validar antes de redigir) | Não (sequencial, 1 instância) | Depois que existir um rascunho (mesmo parcial) para auditar |
| Redator de subseção teórica | `redator-subtema-teorico.md` | 8 (produzir o projeto), apenas as subseções do Referencial teórico | **Sim** — 1 instância por subtema, simultâneas | Depois que a lacuna estiver definida (fim da etapa 5) e as fontes de cada subtema estiverem validadas |

## Responsabilidades — o que cada papel cobre e o que não cobre

**Pesquisador de subtema**
- Cobre: formular queries, buscar, ler (`web_fetch`), validar idoneidade da fonte, registrar no `research_log.json`, sintetizar o subtema.
- Não cobre: comparar seu subtema com os outros três (isso é etapa 4, do orquestrador, que só faz sentido vendo os quatro resumos juntos), decidir se a cobertura geral do projeto está suficiente (isso é o `search_tracker.py` rodado pelo orquestrador olhando todos os subtemas).

**Auditor de citações**
- Cobre: rodar `citation_checker.py`/`search_tracker.py`, ler criticamente as fontes por trás das afirmações centrais, sinalizar alegações sem lastro e lacunas genéricas demais.
- Não cobre: reescrever o texto (reporta pendências, não edita), decidir o que fazer com cada pendência (isso volta para o orquestrador, que decide se busca mais, remove a afirmação, ou ajusta o texto).

**Redator de subseção teórica**
- Cobre: redigir uma subseção do Referencial teórico a partir de fontes já validadas e de um brief de tom fixado pelo orquestrador.
- Não cobre: escolher fontes além das recebidas, redigir qualquer outra seção do projeto (Introdução, Justificativa, Objetivos, Metodologia, a síntese final da lacuna) — essas exigem visão de conjunto e ficam com o orquestrador.

## Workflow completo

```
Orquestrador                         Agentes
─────────────                        ───────
1. Definir o que precisa ser
   descoberto (interação com o
   usuário: recortes, linha de
   pesquisa)
2. Dividir em frentes de
   investigação (4 subtemas fixos)
   → inicializa research_log.json
                                      3. [PARALELO] 1x Pesquisador de
                                         subtema por frente
                                         (conceitual, estado_da_arte,
                                         lacunas, viabilidade)
                                         → cada um registra buscas e
                                           fontes no log compartilhado
                                         → cada um devolve síntese +
                                           pontos de atenção
4. Comparar as 4 sínteses recebidas
   (convergência/divergência entre
   subtemas)
5. Identificar a lacuna (a partir
   da comparação da etapa 4)
6. [se necessário] novas buscas
   pontuais para fechar a lacuna
   (inline, ou 1 agente Pesquisador
   por lacuna candidata se houver
   mais de uma sendo testada)
   → roda search_tracker.py:
     confere piso mínimo geral
─── ponto de decisão: se ainda
    NÃO CONFORME, volta à etapa 3/6
    para os subtemas insuficientes ───
8a. Redige Introdução, Problema,
    Justificativa, Objetivos,
    Metodologia e a "Síntese: a
    lacuna" (exige visão de
    conjunto — fica sempre aqui)
                                      8b. [PARALELO] 1x Redator de
                                          subseção teórica por subtema
                                          → cada um devolve o texto da
                                            subseção + citações usadas
8c. Consolida: monta o rascunho
    completo (8a + subseções de 8b),
    revisa coerência terminológica
    entre as subseções paralelas
                                      7. Auditor de citações revisa o
                                         rascunho consolidado
                                         → devolve pendências
                                           bloqueantes/não-bloqueantes
─── ponto de decisão: se houver
    pendência bloqueante, orquestra-
    dor resolve (busca mais, ajusta
    texto, remove afirmação) e manda
    auditar de novo ───
9. Monta o .docx final
   (reference_formatter.py,
   cronograma_builder.py,
   docx_builder.py) e verifica
   visualmente antes de entregar
```

Note que a etapa 7 (auditoria) aparece depois da 8 no diagrama, não antes — ela audita o rascunho consolidado, não seções isoladas. A numeração das etapas segue o `SKILL.md` (que descreve a lógica de cada uma); a ordem de execução real, quando o modo multi-agente está ativo, é a do diagrama acima.

## Modo de execução

**Com subagentes disponíveis** (ex.: Claude Code): spawne conforme a tabela acima, respeitando os pontos de paralelismo indicados. Cada agente recebe apenas os inputs listados no seu arquivo — não o histórico completo da conversa — então monte o prompt de invocação copiando exatamente os parâmetros pedidos em "Inputs" de cada `agents/*.md`.

**Sem subagentes** (claude.ai chat): não há paralelismo real, mas o raciocínio continua o mesmo. Siga o diagrama na ordem indicada, e para cada bloco marcado `[PARALELO]`, execute as instâncias uma de cada vez (ex.: pesquise `conceitual` do início ao fim seguindo `pesquisador-subtema.md`, depois `estado_da_arte`, e assim por diante) em vez de simultaneamente. O ganho de foco/isolamento de contexto de cada papel continua valendo mesmo sem o ganho de velocidade do paralelismo.

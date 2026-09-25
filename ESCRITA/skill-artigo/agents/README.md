# Agentes desta skill

Este diretório contém instruções para agentes especializados, spawnáveis como subagentes em ambientes que suportam isso (Claude Code). Em claude.ai (chat), não há subagentes de verdade — o próprio Claude segue as mesmas instruções inline, sequencialmente, um papel de cada vez (ver "Modo de execução" no fim deste arquivo).

Nenhum agente aqui decide o recorte do artigo, quantos artigos uma tese deve virar, conversa com o usuário, ou faz a síntese final que amarra o texto como um todo — isso fica sempre com o orquestrador (a instância principal, seguindo o `SKILL.md`).

## Registro de agentes

| Agente | Arquivo | Modo(s) | Paralelizável? | Spawna quando |
|---|---|---|---|---|
| Pesquisador de subtema | `pesquisador-subtema.md` | Criação (sempre) · Extração (se precisar de literatura complementar) | **Sim** — 1 por subtema (1-3 subtemas) | Recorte e idioma confirmados, `research_log.json` inicializado |
| Redator de seção | `redator-secao.md` | Criação | **Sim** — 1 por subtema, tipicamente na Introdução | Fontes do subtema já validadas e objetivo do artigo definido |
| Extrator de tese/TCC/dissertação | `extrator-tese.md` | Extração | **Sim** — 1 por fatia/artigo candidato | Depois que o orquestrador decidiu o fatiamento (quantos artigos, quais capítulos/seções para cada um) |
| Auditor de citações e estrutura | `auditor-citacoes.md` | Ambos | Não (sequencial) | Depois que existir um rascunho consolidado (config.json) para auditar |

## Responsabilidades

**Pesquisador de subtema** — Cobre: buscar, ler, validar fontes, registrar no log, sintetizar o subtema. Não cobre: decidir quantos subtemas o artigo tem, comparar subtemas entre si.

**Redator de seção** — Cobre: redigir um bloco de conteúdo (tipicamente Introdução por subtema) a partir de fontes já validadas. Não cobre: Método/Resultados/Discussão/Conclusão (ficam com o orquestrador, que tem a visão do estudo relatado), escolher fontes além das recebidas.

**Extrator de tese/TCC/dissertação** — Cobre: reescrever (não copiar) uma fatia já definida da tese como seção de artigo, respeitando limite de palavras e sinalizando conteúdo que pertence a outro artigo candidato. Não cobre: decidir o fatiamento em si, validar sozinho fontes novas sem repassar ao orquestrador.

**Auditor de citações e estrutura** — Cobre: rodar `citation_checker.py`/`search_tracker.py`/`structure_checker.py`, ler criticamente fontes centrais, conferir nota de origem em modo extração. Não cobre: editar o texto ou decidir como resolver as pendências.

## Workflow completo — Modo criação (artigo do zero a partir de um prompt)

```
Orquestrador                              Agentes
─────────────                             ───────
1. Definir o que precisa ser descoberto
   (interação com o usuário: recorte,
   periódico-alvo/norma de citação,
   se é artigo empírico ou teórico —
   ver aviso no SKILL.md sobre artigo
   empírico exigir dados do usuário)
2. Dividir em 1-3 subtemas
   → inicializa research_log.json
                                           3. [PARALELO] 1x Pesquisador de
                                              subtema por subtema
                                              → registra buscas/fontes,
                                                devolve síntese
4. Comparar as sínteses recebidas
5. Definir a contribuição/objetivo do
   artigo (mais pontual que a lacuna
   de uma tese)
6. [se necessário] buscas pontuais
   adicionais
   → search_tracker.py: confere piso
─── se ainda NÃO CONFORME, volta à
    etapa 3 para os subtemas que
    faltam ───
                                           redação da Introdução: [PARALELO]
                                           1x Redator de seção por subtema
                                           → cada um devolve o bloco +
                                             citações usadas
7. Redige Método/Resultados/Discussão/
   Conclusão (exige os dados do estudo,
   que só o orquestrador/usuário tem
   em mãos — ou fica vazio/hipotético
   se o artigo for teórico)
8. Consolida o rascunho completo em
   config.json (formato do
   docx_builder.py), revisa coerência
   entre os blocos paralelos
                                           Auditor de citações e estrutura
                                           revisa o rascunho consolidado
                                           → devolve pendências
─── se houver pendência bloqueante,
    orquestrador resolve e manda
    auditar de novo ───
9. Monta o .docx final
   (reference_formatter.py na norma
   escolhida, docx_builder.py) e
   verifica visualmente antes de
   entregar
```

## Workflow completo — Modo extração (tese/TCC/dissertação → artigo(s))

```
Orquestrador                              Agentes
─────────────                             ───────
1. Extrai a estrutura do documento fonte
   (extrair_estrutura.py) — mapa real de
   capítulos/seções com contagem de
   palavras
2. Decide, COM o usuário, quantos
   artigos o documento vai gerar e qual
   fatia (capítulos/seções) vai para
   cada um — usa os números reais do
   passo 1, nunca decide sozinho sem
   mostrar as opções ao usuário
3. Para cada artigo candidato: confirma
   com o usuário periódico-alvo, norma
   de citação, limite de palavras
   → inicializa 1 research_log.json por
     artigo candidato
                                           4. [PARALELO, se >1 artigo] 1x
                                              Extrator de tese por fatia
                                              → devolve seção(ões)
                                                reescritas + fontes citadas
                                                + conteúdo sinalizado como
                                                pertencente a outro artigo
5. Registra no research_log.json as
   fontes que vieram da tese e que o
   Extrator sinalizou (valida cada uma
   antes de registrar — a tese pode ter
   citações desatualizadas)
6. [opcional] Se a tese for antiga ou
   precisar de literatura mais recente
   para a versão-artigo:
                                           Pesquisador de subtema (mesmo
                                           agente do modo criação) busca
                                           literatura complementar
7. Redige a nota de origem (obrigatória
   — ver alerta de autoplágio) e monta
   o config.json de cada artigo
                                           Auditor de citações e estrutura
                                           revisa cada rascunho, incluindo
                                           a checagem da nota de origem
─── se houver pendência bloqueante,
    orquestrador resolve e manda
    auditar de novo ───
8. Monta o .docx final de cada artigo
   e verifica visualmente antes de
   entregar
```

## Modo de execução

**Com subagentes disponíveis** (Claude Code): spawne conforme as tabelas acima, respeitando os pontos de paralelismo. Cada agente recebe apenas os inputs listados no seu arquivo `agents/*.md` — não o histórico da conversa.

**Sem subagentes** (claude.ai): sem paralelismo real, mas siga a mesma ordem e o mesmo raciocínio — execute cada instância de agente por vez (ex.: subtema 1 do início ao fim, depois subtema 2) antes de passar para a etapa seguinte do orquestrador.

# Arquitetura de agentes — implementada

Este README documenta a atribuição das etapas **não-determinísticas** do workflow (identificadas em `scripts/README.md`) a agentes com arquivo de instrução próprio por papel, spawnados quando o ambiente permitir. `agents/elicitador.md`, `agents/pesquisador.md`, `agents/redator.md`, a pasta `template/` (schemas) e `scripts/gerar_projeto.py` (orquestração determinística final) já estão implementados e testados de ponta a ponta (fontes.json + spec.json de teste → .docx final, validado visualmente e por `validar_abnt.py`).

## Por que dividir em agentes (justificativa)

- **Higiene de contexto** — o ciclo de pesquisa (Pesquisador) gera dezenas de chamadas de busca e trechos de fonte; se isso tudo ficar na mesma conversa que depois escreve a Fundamentação Teórica, o contexto da fase de redação fica poluído com ruído de busca. Rodando como agente separado, só o resultado limpo (`fontes.json`, `mapa_lacunas.json`) volta para o orquestrador.
- **Modos de trabalho diferentes** — Elicitação é conversacional (pergunta e espera resposta), Pesquisa é autônoma/exploratória (roda muitas ferramentas sem interação), Redação é generativa/argumentativa (texto longo). Um único conjunto de instruções pra tudo isso arrisca vazamento de modo (ex.: concisão de modo-pesquisa contaminando a prosa). Arquivos de instrução separados = "chapéus" distintos, cada um calibrado pro seu modo.
- **Testabilidade/auditoria** — cada agente tem um contrato de entrada/saída bem definido (JSON). Dá pra re-rodar só o Pesquisador se o gate de piso de busca falhar, ou só o Redator se o usuário quiser outra prosa sem refazer a pesquisa — mesmo raciocínio que já aplicamos pra separar os scripts determinísticos, um nível acima.
- **Caminho pra paralelismo futuro** — se o ambiente suportar, cada sub-tema do ciclo de pesquisa poderia rodar como uma instância própria do Pesquisador em paralelo. Não é implementado agora, mas a separação em agente já deixa essa porta aberta sem redesenhar o workflow depois.

## Nota de plataforma — "spawnados quando possível"

Nesta conversa eu não tenho uma ferramenta de spawn de subagente disponível (não há algo como uma Task tool aqui). O desenho precisa funcionar nos dois cenários:

- **Com spawn** (ex.: Claude Code com Task tool, ou outro ambiente agno com subagentes) — o orquestrador invoca cada papel como uma tarefa separada, cada uma lendo só o seu `agents/<papel>.md` como instrução, devolvendo o JSON de saída.
- **Sem spawn** (ex.: esta conversa no claude.ai) — a mesma thread única lê o `agents/<papel>.md` da etapa antes de começá-la e segue como um checklist de troca de papel, sequencialmente. Degrada de forma graciosa: a arquitetura não depende de spawn pra funcionar, só se beneficia dele quando disponível.

## Agentes e responsabilidades

### Agente Elicitador
- **Corresponde a:** Passo 1 do `SKILL.md` (elicitação + delimitação de tema + idioma de busca).
- **Entrada:** mensagem inicial do usuário (tema, contexto já disponível na conversa).
- **Saída:** `elicitacao.json` — tema delimitado, tipo de projeto, programa/instituição/linha de pesquisa, orientador, duração, idioma das buscas, exigências de edital.
- **Ferramentas:** `ask_user_input_v0` (recortes como opções, perguntas sobre linhas de pesquisa), `web_search` leve (só o suficiente pra avaliar se um recorte proposto é razoável — não é o ciclo de pesquisa completo).
- **Critério de conclusão:** tema delimitado e confirmado pelo usuário (não decidido sozinho), idioma de busca definido, metadata suficiente pra prosseguir.
- **Arquivo de instrução:** `agents/elicitador.md`.

### Agente Pesquisador
- **Corresponde a:** Passo 2 do `SKILL.md` (ciclo de pesquisa completo).
- **Entrada:** `elicitacao.json`.
- **Saída:** `buscas_log.json` (sub-tema → queries feitas), `fontes.json` (via `fontes_registry.py`, cada fonte já com `subtema` marcado), `mapa_lacunas.json` (sub-tema → fontes → convergência/divergência → lacuna identificada).
- **Ferramentas:** `web_search`, `web_fetch`, `fontes_registry.py` (chamado a cada fonte validada), `validar_ciclo_pesquisa.py` (roda a própria checagem antes de devolver ao orquestrador).
- **Critério de conclusão:** `validar_ciclo_pesquisa.py` retorna `"ok": true` para todos os sub-temas (piso de 2-3 buscas / 3-5 fontes validadas) — esse critério já é o gate determinístico, não uma autoavaliação do agente.
- **Arquivo de instrução:** `agents/pesquisador.md`.

### Agente Redator
- **Corresponde a:** Passos 3 e 4 do `SKILL.md` (elementos estruturantes, escolha metodológica incl. trilha DSR, cronograma).
- **Entrada:** `elicitacao.json`, `fontes.json`, `mapa_lacunas.json`.
- **Saída:** `spec.json` — todo o conteúdo textual decidido (introdução, problema, justificativa, objetivos, hipóteses quando aplicável, fundamentação teórica por sub-tema citando pelas chaves do `fontes.json`, metodologia com a trilha escolhida, atividades e marcações do cronograma).
- **Ferramentas:** `fontes_registry.py` (só leitura, pra pegar a forma de citação já formatada — nunca formata NBR 10520 na mão).
- **Critério de conclusão:** todas as seções obrigatórias preenchidas, cada afirmação relevante da Fundamentação Teórica citando uma chave presente em `fontes.json` (nenhuma citação inventada), cronograma compatível com a duração informada.
- **Arquivo de instrução:** `agents/redator.md`.

## Workflow completo

```
Usuário: "Faça um projeto de pesquisa sobre X"
        │
        ▼
Orquestrador (thread principal)
        │
        ├─▶ [spawn/invoca] Agente Elicitador ──▶ elicitacao.json
        │
        ├─▶ [spawn/invoca] Agente Pesquisador (lê elicitacao.json)
        │        └─▶ buscas_log.json + fontes.json + mapa_lacunas.json
        │
        ├─▶ validar_ciclo_pesquisa.py (determinístico)
        │        ├─ "ok": false ──▶ volta pro Agente Pesquisador (só os sub-temas que faltam)
        │        └─ "ok": true  ──▶ segue
        │
        ├─▶ [spawn/invoca] Agente Redator (lê elicitacao.json + fontes.json + mapa_lacunas.json)
        │        └─▶ spec.json
        │
        ├─▶ gerar_projeto.py (determinístico)
        │        └─▶ paginacao_sumario.gerar_com_paginacao_real() ──▶ .docx final
        │        └─▶ validar_abnt.py ──▶ relatório de conformidade
        │
        └─▶ Orquestrador apresenta o .docx + relatório ao usuário
```

Nenhum agente decide sozinho passar pra próxima fase sem o gate determinístico correspondente conferir — a única exceção é a transição Redator → `gerar_projeto.py`, que não tem gate de conteúdo (o `validar_abnt.py` só audita formatação, não substância).

## Template do projeto (planejado)

Estrutura de diretório por execução (uma pasta por projeto gerado):

```
projeto_mestrado_<slug>/
├── elicitacao.json                  # saída do Agente Elicitador
├── buscas_log.json                   # saída do Agente Pesquisador
├── fontes.json                        # saída do Agente Pesquisador (via fontes_registry.py)
├── mapa_lacunas.json                 # saída do Agente Pesquisador
├── validacao_ciclo_pesquisa.json     # saída de validar_ciclo_pesquisa.py
├── spec.json                           # saída do Agente Redator
└── saida/
    ├── <slug>.docx
    ├── <slug>.pdf                     # conversão pra checagem visual
    └── validacao_abnt.json           # saída de validar_abnt.py
```

E, dentro da própria skill, uma pasta `template/` com o esqueleto vazio de cada schema acima (pra cada execução nova partir de um ponto conhecido em vez de a LLM inventar a forma do JSON):

```
skill-mestrado/
├── SKILL.md
├── references/            (já implementado)
├── scripts/                (já implementado)
├── agents/
│   ├── README.md            (este arquivo)
│   ├── elicitador.md
│   ├── pesquisador.md
│   └── redator.md
└── template/                 (schemas dos JSONs de handoff)
    ├── elicitacao.schema.json
    ├── buscas_log.schema.json
    ├── fontes.schema.json      (mesmo shape que fontes_registry.persistir() gera)
    ├── mapa_lacunas.schema.json
    └── spec.schema.json        (mesmo shape que gerar_projeto.py espera)
```

## Status

Implementado: os três arquivos de agente, `template/` com os 5 schemas, `scripts/gerar_projeto.py` (orquestração determinística final) e a seção "Orquestração multi-agente" no `SKILL.md` (mapeando Passos 1-4 aos agentes e o Passo 5 aos scripts). Testado de ponta a ponta com `fontes.json`+`spec.json` de exemplo → `.docx` final, verificado visualmente e por `validar_abnt.py`. **Ainda não testado:** um Agente Pesquisador de verdade rodando o ciclo de pesquisa completo com buscas reais — os testes até aqui usaram fontes/conteúdo de exemplo escritos à mão, não gerados pelos agentes em uma conversa real.

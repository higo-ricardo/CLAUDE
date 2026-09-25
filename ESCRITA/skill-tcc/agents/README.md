# Arquitetura de agentes — implementada

Herdada de `skill-mestrado`, adaptada para o escopo mais leve de TCC/monografia (1-3 sub-temas, 2-4 fontes validadas por sub-tema, variação de entrega — monografia/artigo/projeto de pesquisa — a critério do usuário). A justificativa para dividir em agentes (higiene de contexto, modos de trabalho diferentes, testabilidade, caminho pra paralelismo) e a nota de plataforma ("spawn quando possível", degrada com graça pra troca de papel sequencial na mesma thread) são as mesmas de `skill-mestrado` — não repetidas aqui.

## Agentes e responsabilidades

### Agente Elicitador
- **Corresponde a:** Passo 1 do `SKILL.md`.
- **Entrada:** mensagem inicial do usuário.
- **Saída:** `elicitacao.json` — tema delimitado, variação de entrega (`tcc_monografia`/`tcc_artigo`/`projeto_pesquisa_tcc`), curso/instituição/orientador, duração, idioma das buscas.
- **Ferramentas:** `ask_user_input_v0`, `web_search` leve.
- **Arquivo de instrução:** `agents/elicitador.md`.

### Agente Pesquisador
- **Corresponde a:** Passo 2 do `SKILL.md`.
- **Entrada:** `elicitacao.json`.
- **Saída:** `buscas_log.json`, `fontes.json` (cada fonte com `resumo` preenchido), `mapa_lacunas.json`.
- **Ferramentas:** `web_search`, `web_fetch`, `scripts/fontes_registry.py`, `scripts/validar_ciclo_pesquisa.py`.
- **Critério de conclusão:** gate determinístico com piso de TCC (1-3 sub-temas, 2-4 fontes/sub-tema) retornando `"ok": true`.
- **Arquivo de instrução:** `agents/pesquisador.md`.

### Agente Redator
- **Corresponde a:** Passos 3-4 do `SKILL.md`.
- **Entrada:** `elicitacao.json`, `fontes.json`, `mapa_lacunas.json`.
- **Saída:** `spec.json` — sem `referencias_formatadas` nem `fichamento` (calculados por `gerar_projeto.py`).
- **Ferramentas:** `scripts/fontes_registry.py` (só leitura).
- **Arquivo de instrução:** `agents/redator.md`.

## Workflow completo

```
Usuário: "Faça um TCC sobre X"
        │
        ▼
Orquestrador (thread principal)
        │
        ├─▶ Agente Elicitador ──▶ elicitacao.json
        │
        ├─▶ Agente Pesquisador (lê elicitacao.json)
        │        └─▶ buscas_log.json + fontes.json (com resumo) + mapa_lacunas.json
        │
        ├─▶ validar_ciclo_pesquisa.py (determinístico, piso de TCC)
        │        ├─ "ok": false ──▶ volta pro Agente Pesquisador (só os sub-temas que faltam)
        │        └─ "ok": true  ──▶ segue
        │
        ├─▶ Agente Redator (lê elicitacao.json + fontes.json + mapa_lacunas.json)
        │        └─▶ spec.json
        │
        ├─▶ gerar_projeto.py (determinístico)
        │        └─▶ injeta referencias_formatadas + fichamento a partir de fontes.json
        │        └─▶ paginacao_sumario.gerar_com_paginacao_real() ──▶ .docx final
        │        └─▶ validar_abnt.py ──▶ relatório de conformidade
        │
        └─▶ Orquestrador apresenta o .docx + relatório ao usuário
```

## Template do projeto

```
projeto_tcc_<slug>/
├── elicitacao.json
├── buscas_log.json
├── fontes.json
├── mapa_lacunas.json
├── validacao_ciclo_pesquisa.json
├── spec.json
└── saida/
    ├── <slug>.docx
    ├── <slug>.pdf
    └── validacao_abnt.json
```

E, dentro da própria skill, `template/` com os 5 schemas (mesma função de `skill-mestrado`, com `metadata` adaptado ao vocabulário de TCC — `curso`, `tipo_projeto` com valores de TCC).

## Status

Implementado e testado de ponta a ponta com `fontes.json`+`spec.json` de exemplo (incluindo Modelo Conceitual e fichamento auto-preenchido) → `.docx` final, verificado visualmente e por `validar_abnt.py`. **Ainda não testado:** um Agente Pesquisador de verdade rodando o ciclo de pesquisa completo com buscas reais numa conversa — os testes usaram conteúdo de exemplo escrito à mão como stand-in, igual ao que ocorreu na primeira validação de `skill-mestrado`.

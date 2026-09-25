# Arquitetura Python — implementada

Pacote `python-docx` que separa o que é **determinístico** (script, testável, sem ambiguidade) do que é **não-determinístico** (fica a cargo dos agentes, ver `../agents/README.md`). Herdado de `skill-mestrado`, adaptado para o escopo mais leve de TCC/monografia. Testado módulo a módulo e de ponta a ponta (`fontes.json` + `spec.json` de exemplo → `.docx` final, verificado visualmente e por `validar_abnt.py`).

```
scripts/
├── fontes_registry.py        # registro de fontes (NBR 6023/10520) + fichamento (campo `resumo`)
├── numeracao.py                # NBR 6024 — numeração progressiva de seções
├── cronograma.py                 # gera colunas (mensal/semestral) e a tabela final
├── docx_builder.py              # monta capa, folha de rosto, corpo, tabelas, referências
├── paginacao_sumario.py         # pipeline de 2 passadas p/ sumário e paginação reais
├── validar_abnt.py               # audita o .docx final (margens, fonte, espaçamento)
├── validar_ciclo_pesquisa.py     # gate do piso de busca (1-3 sub-temas, 2-4 fontes)
└── gerar_projeto.py               # CLI que orquestra tudo a partir de spec.json + fontes.json
```

## O que muda em relação a `skill-mestrado`

- **`validar_ciclo_pesquisa.py`**: piso mais leve (`MIN_BUSCAS=1`, `MIN_FONTES=2`, `MAX_FONTES_RECOMENDADO=4`, `MAX_SUBTEMAS_RECOMENDADO=3`) — excesso gera aviso, não falha, já que mais pesquisa nunca é "errado", só fora do escopo típico de TCC.
- **`fontes_registry.py`**: `Fonte` ganhou o campo `resumo` (opcional, mas o Agente Pesquisador sempre preenche) e o método `listar_fichamento()`, que devolve a tabela de Registro das Fontes já pronta — o Agente Redator nunca escreve isso à mão.
- **`docx_builder.py`**: vocabulário de folha de rosto trocado para TCC (`curso` em vez de `programa`, `linha_pesquisa` totalmente opcional, `tipo_projeto` com valores `tcc_monografia`/`tcc_artigo`/`projeto_pesquisa_tcc`); ganhou seis blocos condicionais novos — `_fluxo_conceitual()` (Modelo Conceitual, fonte Courier New centralizada preservando setas), `_tabela_fichamento()` (Registro das Fontes), `_folha_aprovacao()` e `_resumo_bilingue()` (NBR 6028 — Resumo/Abstract, só para `tcc_monografia`, trabalho finalizado NBR 14724:2024), e `_pretextual_artigo()` + `_adicionar_footer_pagina()` (NBR 6022 — `tcc_artigo` não usa capa/folha de rosto/folha de aprovação/sumário nenhum, `build_document()` desvia pra um ramo próprio bem mais enxuto). Cronograma só é renderizado se `tipo_projeto=projeto_pesquisa_tcc`; Resultados e Discussão/Conclusão são seções comuns (sem renderer especial) que o Agente Redator só inclui para trabalho finalizado — ver `references/normas-abnt.md` pra a distinção completa entre as três normas.
- **`paginacao_sumario.py`**: para `tipo_projeto=tcc_artigo`, `gerar_com_paginacao_real()` pula o pipeline de duas passadas inteiro — sem sumário nem pré-textual a descontar, o documento sai pronto numa passada só, mais simples e mais barato.
- **`gerar_projeto.py`**: além de `referencias_formatadas`, também injeta `spec["fichamento"] = registry.listar_fichamento()`.
- **`validar_abnt.py`**: a checagem de fonte agora aceita `{"Times New Roman", "Courier New"}` em vez de só a primeira — o Courier New do Modelo Conceitual é uma exceção documentada, não um erro de formatação.

## Nota de trade-off (herdada de skill-mestrado)

Mesma decisão de não depender de numeração automática do Word em nenhum lugar (números de seção/lista/página são texto ou valor já calculado pelo script) — mais simples e mais determinístico do que manipular `numbering.xml`/campos TOC via XML bruto, ao custo de abrir mão do suporte nativo mais maduro que `docx-js` tem pra isso.

## Status

Todos os 8 scripts implementados e testados: geração real de `.docx` com capa, folha de rosto, sumário e paginação reais, cronograma, modelo conceitual, tabela de fichamento auto-preenchida e referências — validado visualmente (PDF) e por `validar_abnt.py` (`"ok": true`).

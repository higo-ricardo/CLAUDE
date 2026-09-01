# 03 — Revisão e Correção

**Agente**: REVISOR | **Estágio**: M5

---

## Objetivo
Entregar texto limpo, correto e coeso, com diff comentado das alterações.
Métricas quantitativas (legibilidade, voz passiva, jargões) são calculadas
por `scripts/analyzer.py` antes de chegar ao REVISOR.

---

## Níveis de Revisão

| Nível | Foco |
|---|---|
| **Rápida** | Ortografia e gramática |
| **Padrão** | Ortografia + gramática + fluidez + coesão |
| **Profunda** | Tudo + estilo + consistência + normas ABNT |

Padrão se não especificado.

---

## O que o REVISOR faz (julgamento de linguagem)

- Concordância verbal e nominal
- Regência, crase, pontuação
- Coesão e coerência entre parágrafos
- Voz passiva excessiva → converter para ativa
- Nominalização excessiva → simplificar
- Pleonasmos e redundâncias
- Conectivos inadequados

## O que o script faz (não gastar tokens)

```
# Antes de revisar, execute:
python scripts/analyzer.py --text cap.md --mode passive
python scripts/analyzer.py --text cap.md --mode readability --level [nivel]
python scripts/analyzer.py --text cap.md --mode jargon --glossary data/glossary.json
python scripts/analyzer.py --text cap.md --mode numbering
```

O REVISOR recebe o JSON de resultado e age sobre os problemas apontados,
sem precisar detectá-los manualmente.

---

## Checklist ABNT (revisão profunda)

- [ ] Citações curtas (≤3 linhas): aspas no corpo
- [ ] Citações longas (>3 linhas): recuo 4cm, fonte 10, sem aspas
- [ ] Citações indiretas: sem aspas, referência autor-data
- [ ] Referências: ordem alfabética, ABNT NBR 6023
- [ ] Figuras: título abaixo; Tabelas: título acima

---

## Formato de Output

### Opção A — Diff comentado
```
[ORIGINAL]: "As pessoas que trabalha..."
[CORRIGIDO]: "As pessoas que trabalham..."
[NOTA]: Concordância verbal.
```

### Opção B — Texto limpo + resumo
Texto corrigido seguido de:
```
## Resumo das Correções
- X erros ortográficos
- Y problemas de concordância
- Z trechos reestruturados
```

### Opção C — Inline Markdown
- ~~removido~~ / **adicionado** / > [Nota do revisor]

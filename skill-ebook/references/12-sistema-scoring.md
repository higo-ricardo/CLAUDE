# 12 — Sistema de Scoring

**Agente**: ORQUESTRADOR (coordena) + agentes (avaliam seções)
**Estágio**: M4, M5, M6, M7

---

## Regra fundamental

**A LLM avalia. O script calcula.**
O agente atribui notas brutas S1–S5. O `scorer.py` faz a média ponderada,
compara com o limiar do estágio e gera o scorecard formatado.

```bash
python scripts/scorer.py \
  --s1 [nota] --s2 [nota] --s3 [nota] --s4 [nota] --s5 [nota] \
  --stage [M4|M5|M6|M7] \
  --chapter "[nome]" --version [vX.Y]
```

---

## O que cada seção avalia (para o agente atribuir a nota)

| Seção | Peso | Avalie |
|---|---|---|
| **S1 — Gancho** | 20% | Impacto emocional/cognitivo da abertura; curiosidade gerada |
| **S2 — Desenvolvimento** | 35% | Clareza, suporte a afirmações, densidade adequada ao nível |
| **S3 — Público** | 20% | Tom correto, vocabulário no nível, analogias presentes |
| **S4 — Integridade Factual** | 15% | Afirmações verificáveis, absolutas justificadas |
| **S5 — Fechamento** | 10% | Síntese presente, transição para próximo capítulo |

Escala: **0 a 10** por seção, uma casa decimal.

---

## Limiares por estágio (enforçados pelo scorer.py)

| Estágio | Limiar | Consequência se não atingido |
|---|---|---|
| M4 — Rascunho | 6.0 | AUTOR regenera capítulo |
| M5 — Revisão | 7.0 | REVISOR/CRÍTICO retrabalhham seção mais fraca |
| M6 — Copywriting | 7.5 | COPYWRITER refina gancho e fechamento |
| M7 — Validação Final | 8.0 | Pipeline bloqueado até aprovação |

---

## Score consolidado do projeto

```bash
# Tabela de todos os capítulos com status
python scripts/scorer.py --consolidate

# Scorecard detalhado de um capítulo específico
python scripts/scorer.py --scorecard "Cap. 1"
```

---

## Regras

1. Nunca calcule score manualmente — use sempre `scorer.py`.
2. Score do CRÍTICO prevalece sobre auto-avaliação do AUTOR.
3. Toda nota abaixo de 6.0 em qualquer seção exige comentário justificando.
4. Score não arredondado — usar uma casa decimal.

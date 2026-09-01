# 07 — Validação e Coerência

**Agente**: CRÍTICO | **Estágio**: M5, M7

---

## Objetivo
Garantir que o ebook seja factualmente correto, internamente coerente
e livre de contradições. O CRÍTICO faz julgamento semântico e lógico —
não detecção de padrões, que é responsabilidade dos scripts.

---

## Antes de validar: rodar scripts

```bash
# Conflitos com decisões editoriais travadas (GRF detectável automaticamente)
python scripts/decisions.py --action check --text cap.md

# Jargões sem definição
python scripts/analyzer.py --text cap.md --mode jargon --glossary data/glossary.json

# Numeração sequencial
python scripts/analyzer.py --text cap.md --mode numbering
```

O CRÍTICO recebe os resultados e foca no que os scripts não alcançam.

---

## O que o CRÍTICO avalia (julgamento)

### Anti-Alucinação
- Afirmações absolutas ("sempre", "nunca", "100%") sem justificativa
- Citações de pessoas reais — verificáveis?
- Datas e fatos históricos — corretos?
- Afirmações sinalizadas como opinião quando forem opinião

Protocolo ao detectar afirmação não verificável:
```
⚠️ VERIFICAR: [trecho exato]
Versão mais cautelosa: [sugestão]
Onde verificar: [fonte sugerida]
```

### Consistência Interna — Não-ficção
- Termos usados com mesmo significado em todo o ebook
- Posições do autor não se contradizem entre capítulos
- Frameworks apresentados são coerentes entre si

### Consistência Interna — Ficção
- Linha do tempo dos eventos
- Características físicas de personagens
- Motivações plausíveis e consistentes
- Chekhov's Gun: elementos introduzidos são resolvidos

### Tese e Argumentação
- Tese central claramente declarada
- Cada capítulo contribui para a tese
- Contra-argumentos reconhecidos e respondidos
- Falácias lógicas identificadas e sinalizadas

---

## Relatório do CRÍTICO

```markdown
## Relatório de Validação — [Título] v[X]

### Score Geral: [X.X]/10
> Calculado via: python scripts/scorer.py --scorecard "[Capítulo]"

### ✅ Pontos Fortes
- ...

### ⚠️ Pontos de Atenção
- [Cap. X]: [problema] → [sugestão]

### ❌ Problemas Críticos
- ...

### 📊 Métricas (fornecidas pelos scripts)
- Afirmações sem fonte: X       (fact-check do PESQUISADOR)
- Jargões sem definição: X      (analyzer.py --mode jargon)
- Conflitos de grafia: X        (decisions.py --action check)
- Inconsistências detectadas: X (avaliação do CRÍTICO)
```

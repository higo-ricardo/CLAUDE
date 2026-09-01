# 10 — Versionamento e Estado do Projeto

**Agente**: ORQUESTRADOR | **Estágio**: ativo M1–M9

---

## Objetivo
Manter histórico de versões e estado persistente entre sessões.
Todo CRUD é executado por `versioner.py` — o ORQUESTRADOR decide
quando e por quê, não como.

---

## Comandos do script

```bash
# Salvar versão de um capítulo
python scripts/versioner.py --action save \
  --chapter "Cap. 1" --version v1.2 \
  --agent AUTOR --description "Expansão +800 palavras" \
  --file cap01.md

# Ver estado completo do projeto (tabela de scores + histórico)
python scripts/versioner.py --action state

# Ver histórico completo de versões
python scripts/versioner.py --action history

# Diff entre duas versões
python scripts/versioner.py --action diff \
  --chapter "Cap. 1" --compare v1.1:v1.2

# Rollback para versão anterior
python scripts/versioner.py --action rollback \
  --chapter "Cap. 1" --version v1.1
```

---

## Numeração de versões

| Padrão | Quando usar |
|---|---|
| `v1.0` | Versão base — estrutura aprovada |
| `v1.1`, `v1.2`… | Revisões menores — correções pontuais |
| `v2.0` | Revisão maior — reestruturação ou mudança de tom |
| `vX.Y-draft` | Rascunho não aprovado |
| `vX.Y-final` | Aprovado para publicação |

---

## Política de rollback (decisão do ORQUESTRADOR)

Se o score de um capítulo regredir em relação à versão anterior:
1. ORQUESTRADOR detecta via scorecard (`scorer.py --consolidate`)
2. Identifica seção que regrediu (comparação S1–S5)
3. Notifica usuário com `versioner.py --action diff`
4. Aguarda decisão: manter / reverter / mesclar
5. Executa `versioner.py --action rollback` se aprovado

---

## Retomada de sessão

```bash
# Exibir estado atual para colar na nova sessão
python scripts/versioner.py --action state
python scripts/decisions.py --action list
python scripts/scorer.py --consolidate
```

O ORQUESTRADOR solicita ao usuário que execute os três comandos
e cole os resultados para retomar sem perda de contexto.

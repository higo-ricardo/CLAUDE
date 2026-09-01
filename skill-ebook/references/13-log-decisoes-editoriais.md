# 13 — Log de Decisões Editoriais

**Agente**: ORQUESTRADOR | **Estágio**: ativo M1–M9

---

## Objetivo
Registrar e enforçar decisões editoriais travadas.
Todo CRUD é executado por `decisions.py`.
O ORQUESTRADOR decide o que travar; o script gerencia o registro.

---

## Comandos do script

```bash
# Travar uma decisão nova
python scripts/decisions.py --action add \
  --category TOM \
  --decision "Conversacional, 2ª pessoa, sem formalidade" \
  --by Usuário --stage M1

# Listar todas as decisões travadas
python scripts/decisions.py --action list

# Verificar conflitos de grafia num arquivo
python scripts/decisions.py --action check --text cap01.md

# Registrar decisão pendente (em aberto)
python scripts/decisions.py --action add-pending \
  --category FMT --question "Usar bullets ou listas numeradas?" --urgency Alta

# Ver pendências
python scripts/decisions.py --action pending

# Alterar decisão travada (requer motivo)
python scripts/decisions.py --action alter \
  --id D-03 --decision "Nova decisão" --reason "Mudança de público" --by Usuário
```

---

## Categorias

| Código | Categoria |
|---|---|
| TOM | Tom e voz |
| PUB | Público-alvo |
| EST | Estrutura |
| LNG | Linguagem |
| CIT | Citação e fontes |
| GRF | Grafia (detectável automaticamente pelo script) |
| POS | Posição autoral |
| FMT | Formatação |
| MKT | Marketing e publicação |

---

## Protocolo do ORQUESTRADOR

**Quando criar decisão travada:**
- Usuário aprova proposta do ARQUITETO
- Usuário confirma Documento de Projeto (M1)
- Usuário corrige um agente e define a regra
- REVISOR padroniza grafia após dúvida

**Quando detectar conflito:**
```
⚠️ Conflito com decisão travada [D-XX]: [descrição].
Deseja manter a decisão atual ou alterá-la?
```
PARAR. Não avançar sem resposta do usuário.

**Verificação automática de grafia** antes de entregar qualquer capítulo:
```bash
python scripts/decisions.py --action check --text [arquivo.md]
```

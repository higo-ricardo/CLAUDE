# 06 — Adaptação de Linguagem

**Agente**: SIMPLIFICADOR  
**Estágio**: M5/M6

---

## Níveis de Linguagem

| Nível | Público | Características |
|---|---|---|
| **Leigo** | Sem conhecimento prévio | Vocabulário simples, analogias do cotidiano, evitar jargões, frases curtas (≤15 palavras) |
| **Iniciante** | Curioso, pouco conhecimento | Jargões explicados, exemplos concretos, ritmo lento |
| **Intermediário** | Alguma experiência | Jargões aceitos, exemplos aplicados, ritmo moderado |
| **Avançado** | Profissional ou estudante | Linguagem técnica plena, referências implícitas, densidade alta |
| **Especialista** | Expert na área | Pressuposição de domínio, foco em nuances e bordas |

---

## Processo de Adaptação

### Leigo → Especialista
1. Identificar todos os termos técnicos
2. Para cada termo: substituir por palavra simples OU adicionar glossário inline
3. Quebrar frases longas
4. Adicionar analogias para cada conceito abstrato
5. Verificar: uma criança de 14 anos entenderia?

### Especialista → Leigo
1. Manter a substância, trocar a embalagem
2. Substituir jargões por descrições funcionais
3. Adicionar "o que isso significa na prática?" após cada conceito
4. Incluir exemplos do dia a dia
5. Reduzir densidade: máximo 1 conceito novo por parágrafo

---

## Checklist de Acessibilidade

- [ ] Frases com média ≤ 20 palavras (leigo) / ≤ 30 palavras (intermediário)
- [ ] Primeiro uso de todo jargão acompanhado de explicação
- [ ] Parágrafos com ≤ 5 linhas
- [ ] Exemplos concretos para cada conceito abstrato
- [ ] Glossário gerado para termos técnicos frequentes
- [ ] Linguagem inclusiva (evitar gênero excludente quando possível)

---

## Gerador de Analogias

Para qualquer conceito técnico, o SIMPLIFICADOR gera 3 analogias do cotidiano:

Exemplo: "cache de memória"
1. "É como a bancada de trabalho de um carpinteiro — os materiais mais usados ficam ali do lado, não no armário"
2. "Como o bolso da calça: você guarda o que vai usar agora, não a mochila inteira"
3. "Como a lista mental de supermercado: você lembra os 5 itens principais sem consultar o papel"

---

## Glossário Automático

Gerar glossário ao final do ebook com todos os termos técnicos identificados:

```markdown
## Glossário

**[Termo]**: [Definição em linguagem acessível]. *Exemplo: ...*
```

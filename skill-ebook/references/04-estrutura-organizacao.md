# 04 — Estrutura e Organização

**Agente**: ARQUITETO  
**Estágio**: M3

---

## Objetivo
Projetar a arquitetura completa do ebook: sumário, progressão temática,
arcos narrativos (ficção) ou lógica argumentativa (não-ficção).

---

## Modelos de Estrutura por Gênero

### Não-ficção / Autoajuda / Negócios

**Modelo Clássico (Problema-Solução)**
```
Introdução — A promessa e o leitor ideal
Parte 1: O Problema (1-3 cap.)
  └─ Cap. 1: O custo de não resolver
  └─ Cap. 2: Por que as soluções comuns falham
Parte 2: O Framework (3-5 cap.)
  └─ Cap. 3-7: Os pilares da solução (1 por capítulo)
Parte 3: A Implementação (2-3 cap.)
  └─ Cap. 8: Passo a passo
  └─ Cap. 9: Obstáculos e como superá-los
Conclusão — A transformação e os próximos passos
Bônus / Apêndices (opcional)
```

**Modelo Jornada do Herói (para autoajuda narrativo)**
```
Ato 1: O Mundo Comum — situação atual do leitor
Ato 2: O Chamado — o problema / a virada
Ato 3: A Provação — o processo de mudança
Ato 4: O Retorno — a nova versão do leitor
```

**Modelo Pilares (para livros técnicos)**
```
Introdução
Fundamentos (cap. 1-2)
Pilar 1 (cap. 3-4)
Pilar 2 (cap. 5-6)
Pilar 3 (cap. 7-8)
Integração dos pilares (cap. 9)
Conclusão + Referências
```

### Ficção

**Modelo Três Atos**
```
Ato 1 (25%): Apresentação — mundo, protagonista, incidente incitante
Ato 2a (25%): Complicação — protagonista tenta resolver, falha
Ponto de Virada Central (1 cena)
Ato 2b (25%): Crise — tudo piora, o protagonista muda
Ato 3 (25%): Clímax + Resolução
```

**Modelo Save the Cat (15 batidas)**
```
1. Imagem de abertura  2. Tema  3. Setup  4. Catalisador  5. Debate
6. Break into Two  7. B Story  8. Fun and Games  9. Midpoint
10. Bad Guys Close In  11. All Is Lost  12. Dark Night of the Soul
13. Break into Three  14. Finale  15. Final Image
```

---

## Geração de Sumário (output padrão)

O ARQUITETO produz o sumário no seguinte formato:

```markdown
# SUMÁRIO — [TÍTULO DO PROJETO]

## Introdução
- Propósito do livro
- Para quem é este livro
- Como usar este livro

## PARTE 1: [NOME DA PARTE]

### Capítulo 1: [TÍTULO]
*Objetivo do capítulo: ...*
Tópicos: tópico A, tópico B, tópico C
Desfecho: o leitor vai aprender/sentir/decidir...

### Capítulo 2: [TÍTULO]
...

## PARTE 2: [NOME DA PARTE]
...

## Conclusão
- Síntese
- Próximos passos
- Chamada para ação

## Apêndices (se houver)
- Apêndice A: ...
```

---

## Princípios de Arquitetura Editorial

1. **Progressão**: cada capítulo deve construir sobre o anterior
2. **Proporção**: nenhuma parte deve ser mais que 40% do total
3. **Equilíbrio teoria/prática**: máximo 60% teoria em livros práticos
4. **Ganchos entre capítulos**: criar antecipação ao final de cada um
5. **Densidade crescente**: começar acessível, aprofundar gradualmente
6. **Fechamento satisfatório**: conclusão deve responder às promessas da introdução

---

## Funcionalidades Extras

### Reorganizador de Conteúdo
Dado um sumário ou lista de tópicos desordenados, o ARQUITETO:
1. Identifica agrupamentos naturais
2. Detecta lacunas de conteúdo
3. Sugere nova ordem com justificativa
4. Identifica conteúdo redundante a ser mesclado

### Análise de Gap
Comparar o conteúdo existente com o sumário planejado e gerar relatório:
- Capítulos completos ✅
- Capítulos parciais (%) 🔶
- Capítulos ausentes ❌

### Divisão Automática de Texto Longo
Dado um texto contínuo longo (sem divisão em capítulos), o ARQUITETO:
1. Detecta mudanças de tema/subtema
2. Propõe divisão em capítulos com títulos
3. Gera sumário retroativo

### Calculadora de Equilíbrio
Analisar o manuscrito atual e reportar:
- Palavras por capítulo (tabela)
- Capítulos desproporcionais (acima/abaixo da média ±30%)
- Sugestão de divisão ou fusão de capítulos

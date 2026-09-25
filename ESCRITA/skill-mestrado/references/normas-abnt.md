# Normas ABNT aplicáveis a um Projeto de Pesquisa de Mestrado/Doutorado

A NBR 15287:2025 (que substitui a NBR 15287:2011) rege a estrutura do projeto de pesquisa em si, mas remete a outras normas para detalhes específicos. Esta referência resume o que essas normas exigem na prática, com exemplos prontos para usar na geração do `.docx`.

## NBR 10520 — Citações no texto

Duas formas de indicar a mesma citação, escolha uma e seja consistente no documento inteiro:

- **Autor como sujeito da frase**: `Segundo Silva (2022), a personalização de ensino via IA ainda carece de validação longitudinal.`
- **Autor entre parênteses**: `A personalização de ensino via IA ainda carece de validação longitudinal (SILVA, 2022).`

Regras práticas:
- Sobrenome do autor sempre em caixa alta quando aparece entre parênteses; em caixa normal quando é sujeito da frase.
- Dois autores: `(SILVA; COSTA, 2021)`. Três ou mais: `(SILVA et al., 2021)`.
- Citação direta (transcrição literal) de até 3 linhas: entre aspas duplas, no corpo do parágrafo, com página: `(SILVA, 2022, p. 45)`. Evite citações diretas longas em um projeto de pesquisa — prefira parafrasear (além de ser boa prática acadêmica, evita problemas de direitos autorais).
- Citação direta de mais de 3 linhas: parágrafo próprio, recuado 4cm da margem esquerda, fonte menor (geralmente 10), espaçamento simples, sem aspas.
- Informação obtida em site/documento eletrônico sem autoria de pessoa física: usar o nome da instituição responsável (ex.: `(MINISTÉRIO DA EDUCAÇÃO, 2023)`).

## NBR 6023 — Referências (lista final)

Formato geral: `SOBRENOME, Nome. Título: subtítulo. Edição. Local: Editora, ano.` — ordem alfabética por sobrenome do primeiro autor, alinhamento à esquerda (sem recuo na primeira linha; recuo nas linhas seguintes é opcional mas comum), espaçamento simples entre linhas de uma mesma referência e espaço simples ou 1,5 entre referências diferentes (mantenha consistente com o restante do documento).

**Artigo de periódico:**
```
SOBRENOME, Nome. Título do artigo. Nome do Periódico, Local, v. X, n. Y, p. XX-XX, mês/ano.
```

**Livro:**
```
SOBRENOME, Nome. Título: subtítulo. Edição. Local: Editora, ano.
```

**Capítulo de livro (com organizador):**
```
SOBRENOME, Nome. Título do capítulo. In: SOBRENOME, Nome (org.). Título do livro. Local: Editora, ano. p. XX-XX.
```

**Dissertação/Tese:**
```
SOBRENOME, Nome. Título: subtítulo. Ano. Nº de folhas. Dissertação (Mestrado em Área) ou Tese (Doutorado em Área) – Instituição, Local, ano.
```

**Trabalho publicado em anais de evento/congresso:**
```
SOBRENOME, Nome. Título do trabalho. In: NOME DO EVENTO, número., ano, Local. Anais [...]. Local: Editora/Instituição, ano. p. XX-XX.
```

**Documento eletrônico/site (sem editora física):**
```
SOBRENOME, Nome ou NOME DA INSTITUIÇÃO. Título da página/documento. Local: Instituição, ano. Disponível em: URL. Acesso em: dia mês. ano.
```

Nunca inclua na lista de Referências uma fonte que não foi de fato consultada durante o ciclo de pesquisa (Passo 2 do SKILL.md) — a lista deve ser um retrato fiel do que embasou o projeto, nunca preenchimento genérico.

## NBR 6027 — Sumário

Lista as seções na mesma ordem e com a mesma grafia (incluindo numeração) em que aparecem no texto, cada uma com o número da página correspondente. Em `docx-js`, a forma mais confiável é montar o sumário manualmente como uma lista de parágrafos com `Título .......... página`, já que campos de TOC automático (`TableOfContents`) exigem que o usuário abra o Word e atualize o campo manualmente — para consistência e para não depender dessa etapa manual, prefira o sumário estático, e avise o usuário que, se ele reordenar seções depois, precisa atualizar o sumário à mão.

## NBR 6024 — Numeração progressiva

Seções primárias em algarismos arábicos únicos (`1`, `2`, `3`...); subseções com numeração composta separada por ponto, sem ponto final (`3.1`, `3.2`); a numeração faz parte do próprio texto do título (não é numeração automática de heading do Word).

## Diferenças entre a NBR 15287:2011 e a versão 2025

A versão 2025 reforça a exigência de coerência entre elementos (introdução, problema, objetivos, metodologia e cronograma devem se conectar como parte do mesmo argumento — não são seções isoladas) e é mais explícita sobre o aparato bibliográfico robusto via NBR 6023. Se o usuário mencionar que sua instituição ainda usa a versão 2011 como referência, a estrutura geral (parte externa/interna, pré-textual/textual/pós-textual) é praticamente a mesma; a diferença prática mais relevante é essa ênfase maior em coerência e em hipóteses/questões norteadoras bem articuladas com o problema.

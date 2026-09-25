---
name: skill-artigo
description: >-
  Produz artigos científicos no padrão NBR 6022/IMRaD, em dois modos: (1) transformar um TCC, tese ou dissertação existente em um ou mais artigos derivados, decidindo o fatiamento com o usuário a partir da estrutura real do documento; (2) criar um artigo do zero a partir de um prompt/tema, com pesquisa por 1-3 subtemas e piso de 2-4 fontes validadas por subtema. Conduz pesquisa agêntica real antes de redigir e nunca reproduz trechos de uma tese como se fossem novos (reescreve, sinalizando a origem). Use SEMPRE que o usuário pedir para transformar/converter/extrair um TCC, tese, dissertação ou monografia em artigo, publicação ou paper; ou para escrever/elaborar um artigo científico a partir de um tema. Ative mesmo sem menção a normas específicas — ex.: 'transforma minha dissertação em 2 artigos', 'escreve um artigo científico sobre X pra eu submeter'. Não usar para projetos de pesquisa de doutorado/mestrado (ver skill-doutorado) nem resumos/resenhas sem fim de submissão.
---

# Skill Artigo — Transformação e Criação de Artigos Científicos

## O que esta skill produz

Um ou mais artigos científicos formatados conforme a NBR 6022 (elementos pré-textuais, IMRaD ou estrutura discursiva, elementos pós-textuais), prontos para submissão a um periódico — seja extraindo de um TCC/tese/dissertação já escrito, seja criando do zero a partir de um tema.

## Dois modos — escolha logo no início

Pergunte ao usuário (ou infira do pedido, confirmando antes de prosseguir) qual modo se aplica:

- **Modo A — Extração**: o usuário já tem um TCC, tese ou dissertação e quer transformá-lo em 1 ou mais artigos.
- **Modo B — Criação**: o usuário quer um artigo novo, a partir de um tema/prompt, sem documento fonte.

> **Modo B funciona melhor para artigos teóricos/de revisão.** Um artigo empírico relata dados de um estudo (Método, Resultados) — esta skill não coleta dados de campo. Se o usuário quer um artigo empírico do zero, pergunte se já tem os dados/resultados para fornecer; sem isso, oriente para um recorte teórico/de revisão de literatura, ou para o modo A se já houver uma tese/TCC com o estudo pronto.

> **Agentes e workflow completo:** ambos os modos têm um diagrama detalhado, com o que é paralelizável e o que fica sempre com o orquestrador, em `agents/README.md`. Leia-o antes de conduzir qualquer um dos dois modos — este arquivo dá a visão geral; o `agents/README.md` dá a sequência exata de execução.

> **Divisão de trabalho:** decisões de recorte, fatiamento, comparação de fontes, definição de contribuição/objetivo e a redação de Método/Resultados/Discussão sempre exigem julgamento seu (ou de um agente especializado, nunca de um script). As partes mecânicas — contagem de cobertura de busca, cruzamento de citações, formatação de referências, extração de estrutura de documento, checagem de completude estrutural, montagem do `.docx` — foram extraídas para `scripts/` (ver tabela abaixo).

## Modo A — Extração (TCC/tese/dissertação → artigo(s))

### 1. Extraia a estrutura real do documento

Nunca decida o fatiamento "de cabeça" — rode primeiro:
```bash
python scripts/extrair_estrutura.py --fonte <documento.docx> --out estrutura.json
```
Se a fonte for PDF, use a skill de leitura de PDF para extrair o texto com marcação de títulos em Markdown primeiro, salve como `.md`, e rode o script sobre esse `.md` (ver docstring do script).

### 2. Decida o fatiamento junto com o usuário

Com os números reais de cada capítulo/seção em mãos, proponha ao usuário quantos artigos fazem sentido e o que vai em cada um (ex.: um capítulo de revisão teórica robusto pode virar um artigo teórico próprio; cada estudo empírico distinto da tese vira um artigo IMRaD separado). Não decida sozinho sem checar com o usuário — é uma decisão editorial, não só de conteúdo.

### 3. Para cada artigo candidato, confirme periódico-alvo, norma e limite

Pergunte periódico-alvo (se já souber), norma de citação (ABNT/APA/Vancouver) e limite de palavras. Sem essas informações, use os padrões de `references/estrutura-imrad-nbr6022.md`.

### 4. Extraia e reescreva cada fatia

Use o agente `agents/extrator-tese.md` (ou siga as mesmas instruções inline) para condensar cada fatia em seções de artigo — nunca copiando trechos da tese verbatim. Registre no `research_log.json` de cada artigo as fontes que vieram da tese (revalidando cada uma — não herde citações desatualizadas sem checar).

### 5. Redija a nota de origem — obrigatória

Todo artigo derivado de tese/TCC/dissertação leva uma nota (`nota_origem` no config do `docx_builder.py`) informando a origem. Ver o alerta completo em `references/estrutura-imrad-nbr6022.md` antes de pular esta etapa — não é opcional.

### 6. Valide e monte (ver "Scripts determinísticos" e "Formato de entrega" abaixo)

## Modo B — Criação (artigo do zero a partir de um prompt)

### 1. Defina o recorte com o usuário

Tema, periódico-alvo (se já souber), norma de citação, e se o artigo é teórico/revisão ou empírico (ver aviso acima sobre dados). Não presuma — pergunte.

### 2. Divida em 1 a 3 subtemas

Menos frentes que uma tese — um artigo argumenta um ponto, não mapeia um campo inteiro. Inicialize o log:
```bash
python scripts/research_log.py init --log research_log.json --recorte "<recorte>" --idioma ptbr|ptbr+en --subtemas "sub1,sub2"
```

### 3. Pesquise (piso: 2 buscas/idioma e 2-4 fontes por subtema)

Mesma lógica de busca real (nunca de memória) da skill-doutorado, em escala menor. Registre tudo:
```bash
python scripts/research_log.py add-busca --log research_log.json --subtema <sub> --idioma pt|en --query "..."
python scripts/research_log.py add-fonte --log research_log.json --subtema <sub> --autor "SOBRENOME, Nome" --ano <ano> --titulo "..." --veiculo "..." --tipo artigo --url "..."
```
Confira o piso antes de seguir:
```bash
python scripts/search_tracker.py --log research_log.json
```

### 4. Compare as fontes e defina a contribuição do artigo

Mais pontual que a lacuna de uma tese — o que este artigo especificamente acrescenta, não um mapeamento do campo inteiro.

### 5. Redija (Introdução a partir dos subtemas; Método/Resultados/Discussão/Conclusão com o orquestrador)

### 6. Valide e monte (ver abaixo)

## Scripts determinísticos

Tudo em `scripts/` faz apenas contagem, checagem cruzada, extração estrutural ou formatação mecânica — nunca gera conteúdo nem julga qualidade/relevância.

| Script | Usado em | O que faz |
|---|---|---|
| `research_log.py` | Ambos os modos | Mantém o `research_log.json` — `init` (com `--subtemas`), `add-busca`, `add-fonte`, `show` |
| `search_tracker.py` | Ambos | Confere piso mínimo (2 buscas/idioma, 2-4 fontes por subtema) |
| `citation_checker.py` | Ambos | Cruza citações do rascunho com fontes validadas — pega citação fabricada |
| `reference_formatter.py` | Ambos | Formata referências em ABNT, APA ou Vancouver (`--estilo`), conforme o periódico-alvo |
| `extrair_estrutura.py` | Modo A | Lê a tese/TCC (.docx ou .md) e devolve capítulos/seções com contagem de palavras — apoia a decisão de fatiamento |
| `structure_checker.py` | Ambos | Confere completude do `config.json` do artigo: seções IMRaD obrigatórias presentes e com tamanho mínimo, resumo/abstract dentro da faixa de palavras, contagem de palavras-chave, limite total do periódico |
| `docx_builder.py` | Ambos | Monta o `.docx` final (título, autoria, resumo/abstract bilíngue, corpo, referências) a partir do `config.json` — ver docstring e `assets/config_exemplo.json` |

Fluxo de fechamento: monte o `config.json` (meta + secoes; `referencias_log` aponta para o `research_log.json` e gera as referências na norma escolhida automaticamente), rode `structure_checker.py` e `citation_checker.py`, resolva pendências, rode `docx_builder.py`, e siga a verificação visual em "Formato de entrega".

## Estrutura, IMRaD e normas de citação

Antes de montar qualquer artigo, leia `references/estrutura-imrad-nbr6022.md` — traz a estrutura completa (NBR 6022, IMRaD vs. estrutura discursiva para artigos teóricos), quando usar cada norma de citação (ABNT/APA/Vancouver), e o alerta obrigatório sobre autoplágio/publicação duplicada no modo extração.

## Formato de entrega

Gere sempre como `.docx`, nunca só texto no chat. Depois de rodar `docx_builder.py`, converta para PDF e confira visualmente antes de entregar:
```bash
python /mnt/skills/public/docx/scripts/office/soffice.py --headless --convert-to pdf artigo.docx
pdftoppm -jpeg -r 100 artigo.pdf pagina
```
Salve em `/mnt/user-data/outputs/` e apresente o(s) arquivo(s) ao usuário. Se o modo A gerar mais de um artigo, apresente todos, deixando claro no nome do arquivo a qual artigo cada um corresponde.

## Perguntas a esclarecer com o usuário

- Modo A ou B (se não estiver claro no pedido).
- Periódico-alvo e norma de citação — sem isso, use os padrões ABNT de `references/estrutura-imrad-nbr6022.md`, mas avise que pode precisar ajustar depois.
- Modo A: quantos artigos e qual fatiamento (sempre com os números reais de `extrair_estrutura.py` em mãos, nunca decidido sozinho).
- Modo B: se o artigo é teórico/revisão ou empírico (e, se empírico, se o usuário tem os dados para fornecer).

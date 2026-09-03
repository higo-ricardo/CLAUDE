---
name: skill-poema
description: >
  Compõe, corrige, avalia e transforma poemas em português, aplicando
  conceitos de verso, estrofe, métrica, rima e musicalidade. Cobre
  formas fixas internacionais (soneto shakespeariano, soneto
  petrarquiano, haicai, tanka, villanelle, limerique) e também formas
  luso-brasileiras (redondilha, soneto camoniano, cordel, trova) quando
  o poema pedir. Use esta skill sempre que o usuário quiser escrever um
  poema, revisar ou corrigir a métrica ou a rima de um poema, escandir
  versos, contar sílabas poéticas, analisar esquema de rima, avaliar a
  qualidade ou musicalidade de um poema, reescrever um poema em outra
  forma (por exemplo transformar verso livre em soneto, ou soneto em
  haicai), ou gerar variações de um mesmo poema. Ative mesmo que o
  usuário não use termos técnicos — pedidos como "melhora esse poema",
  "isso rima direito?", "escreve um poema sobre X em forma de soneto",
  "conta as sílabas desse verso" ou "faz uma versão curta desse poema"
  já são gatilho suficiente.
---

# Oficina Poética

Uma skill para trabalhar poemas em português com o vocabulário técnico
certo (verso, estrofe, métrica, rima, musicalidade) sem perder de vista
que métrica e rima servem ao efeito do poema — não são um fim em si.
Corrigir um poema não é só fazer a conta bater; é entender o que o
verso está tentando soar como, e ajustar sem matar a voz do autor.

Esta skill cobre quatro modos de uso: **compor**, **corrigir**,
**avaliar** e **transformar**. Todos compartilham a mesma base de
conceitos — leia primeiro:

- `references/metrica-e-rima.md` — como contar sílabas poéticas
  (sinalefa, regra da última tônica), classificação de versos e
  estrofes, tipos de rima e esquemas, recursos de musicalidade.
- `references/formas-fixas.md` — catálogo de formas fixas (soneto
  shakespeariano, petrarquiano, camoniano, haicai, tanka, villanelle,
  limerique, rondó, verso livre, e formas luso-brasileiras como
  redondilha, cordel, trova), com estrutura, esquema de rima e o efeito
  que cada forma busca.

Carregue esses dois arquivos sempre que a tarefa envolver classificar,
contar ou comparar versos — não tente escandir de cabeça quando o
`scripts/escandir_verso.py` está disponível para isso (ver abaixo).

## Escansão automática: `scripts/escandir_verso.py`

Contar sílabas poéticas de cabeça é enganoso — sinalefa e tonicidade têm
regras específicas que erram fácil "no olho". Use o script sempre que
precisar de uma contagem confiável:

```bash
# um verso avulso
python3 scripts/escandir_verso.py "Amor é fogo que arde sem se ver"

# um poema inteiro (arquivo com um verso por linha)
python3 scripts/escandir_verso.py --arquivo poema.txt

# haicai/tanka: use --simples (ver por quê em metrica-e-rima.md)
python3 scripts/escandir_verso.py --arquivo haicai.txt --simples

# validar contra o perfil estrutural de uma forma fixa (ver formas
# cadastradas em scripts/formas.json): compara nº de versos, sílabas
# por verso e esquema de rima contra o esperado, e devolve um relatório
# em JSON — fatos mensuráveis, não julgamento de qualidade
python3 scripts/escandir_verso.py --arquivo poema.txt --validar soneto_shakespeariano

# relatório de rima expandido: agrupa por som e classifica cada grupo
# por tonicidade (aguda/grave/esdrúxula) e qualidade (consoante/toante)
python3 scripts/escandir_verso.py --arquivo poema.txt --rima

# contagens objetivas: nº de versos, estrofes, palavras, média de
# sílabas por verso
python3 scripts/escandir_verso.py --arquivo poema.txt --stats
```

Use `--validar <forma>` sempre que o pedido nomear uma forma fixa
cadastrada (soneto_shakespeariano, soneto_petrarquiano, soneto_camoniano,
haicai, tanka, villanelle, limerique — ver a lista completa e os
critérios de cada uma em `scripts/formas.json`). O relatório separa o
que é fato objetivo (a forma bate ou não) do julgamento que cabe a você
fazer depois (se o desvio é erro ou licença poética).

A saída mostra, por verso: número de sílabas poéticas, classificação
(redondilha, decassílabo etc.) e quantas elisões foram aplicadas. Se
houver mais de um verso, mostra também o esquema de rima aproximado
(ABAB, AABB...) calculado a partir da última palavra de cada verso.

**O script é uma ferramenta de apoio, não um oráculo.** A separação
silábica e a acentuação do português têm exceções reais (hiatos sem
acento gráfico, nomes próprios, licenças poéticas). Trate o resultado
como um ponto de partida objetivo — confira de ouvido, principalmente
quando a contagem estiver "quase certa" (1 sílaba de diferença) ou o
esquema de rima parecer estranho. Isso vale tanto para você quanto para
o que você reporta ao usuário: mostre a contagem, mas fale como "o
verso está escandindo em N sílabas" em vez de "está errado" quando o
desvio puder ser licença poética deliberada.

## Compor

1. Confirme (ou infira do pedido) tema, tom e forma desejada. Se o
   usuário não especificar forma, verso livre é uma escolha segura —
   mas se ele mencionar "soneto", "haicai" etc., abra
   `references/formas-fixas.md` e siga a estrutura à risca (número de
   versos, esquema de rima, métrica).
2. Escreva um rascunho pensando primeiro na imagem/ideia central, depois
   ajuste à forma — poemas que nascem "encaixando palavras na métrica"
   costumam soar arrastados. É mais natural escrever o sentido e depois
   lapidar o verso para caber, trocando sinônimos e reordenando frases.
3. Rode `escandir_verso.py` no rascunho para conferir se a métrica e o
   esquema de rima realmente batem com a forma escolhida. Ajuste os
   versos que destoarem.
4. Releia em voz alta (mentalmente) checando musicalidade — não só a
   contagem, mas se os acentos internos caem em posições parecidas
   entre versos análogos (ver seção de ritmo em `metrica-e-rima.md`).

## Corrigir

1. Rode `escandir_verso.py --validar <forma>` (se o poema tiver uma
   forma fixa alvo cadastrada em `scripts/formas.json`) ou, sem forma
   definida, `--arquivo poema.txt` simples para ter a escansão de cada
   verso. Rode também `--rima` para ver os grupos de rima com
   tonicidade e qualidade sonora já classificadas.
2. Compare com a forma pretendida (se houver uma) ou com o padrão que o
   próprio poema estabeleceu nos primeiros versos (se for verso livre
   com métrica solta, o "padrão" é a variação natural do autor, não uma
   forma fixa).
3. Para cada verso fora do padrão, pergunte-se: é um deslize (quebra a
   expectativa sem parecer proposital) ou uma licença poética (dá
   ênfase de propósito)? Só proponha correção para o primeiro caso;
   para o segundo, é melhor observar isso na sua resposta e deixar a
   decisão com o usuário.
4. Ao propor um ajuste, prefira trocar palavras por sinônimos ou
   reordenar a sintaxe em vez de cortar imagens — o objetivo é acertar
   o verso sem esvaziar o sentido.
5. Quando o poema estiver em um arquivo, aplique as correções
   diretamente no arquivo e acrescente um changelog inline (ex.: um
   comentário ou nota ao final, ou uma lista logo após o poema) listando
   verso por verso o que mudou e por quê — não deixe a correção só
   descrita em prosa se o usuário pode simplesmente querer o arquivo
   pronto.

## Avaliar

Estruture a avaliação em torno do que o script e os arquivos de
referência revelam, mas não pare na métrica — uma avaliação só técnica
perde o que faz o poema funcionar (ou não):

- **Forma:** o poema segue uma forma fixa identificável? Se sim, ela
  está completa e correta (número de versos, esquema de rima, métrica)?
- **Métrica:** os versos escandem de forma regular ou há variação? A
  variação parece proposital?
- **Rima:** que tipo (rica/pobre, consoante/toante) e que esquema? O
  esquema se sustenta do início ao fim?
- **Musicalidade:** que recursos sonoros aparecem (aliteração,
  assonância, anáfora, enjambement)? Eles reforçam o sentido ou parecem
  gratuitos?
- **Imagem e sentido:** isso está fora do escopo puramente métrico, mas
  é o que dá substância à avaliação — vale comentar se a forma escolhida
  serve ao conteúdo (ex.: um haicai que tenta narrar uma história inteira
  está brigando com a própria forma).

## Transformar em variações

Ao transformar um poema em outra forma ou registro, leia a seção final
de `references/formas-fixas.md` ("Escolhendo a forma certa numa
transformação") — cada transformação corta e ganha coisas diferentes, e
vale nomear isso para o usuário em vez de só entregar o resultado:

- Mudança de forma (verso livre → soneto, soneto → haicai etc.)
- Mudança de tom ou registro (sério ↔ cômico, formal ↔ coloquial)
- Mudança de métrica (ex.: redondilha maior → decassílabo)
- Condensação ou expansão (resumir um poema longo em uma quadra, ou
  desenvolver uma quadra em um poema maior)
- Modernização ou arcaização de vocabulário e sintaxe

Depois de transformar, rode `escandir_verso.py` na variação para
confirmar que a nova forma realmente bate com o que foi pedido.

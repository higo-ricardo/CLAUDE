# Formas fixas — catálogo de referência

Consulte este arquivo ao compor, corrigir, avaliar ou transformar um
poema numa forma específica. Prioridade das formas internacionais (o
usuário desta skill pediu foco nelas), com as formas luso-brasileiras
citadas de forma mais breve para os casos em que o poema pedir.

Para cada forma: estrutura, esquema de rima, métrica esperada e o efeito
que a forma busca — o efeito importa tanto quanto a contagem, porque uma
"correção" que acerta a métrica mas destrói o efeito da forma não
cumpriu o pedido.

## Soneto

### Soneto shakespeariano (inglês)
- 14 versos: 3 quartetos + 1 dístico final.
- Esquema de rima: ABAB CDCD EFEF GG.
- Métrica original: pentâmetro iâmbico (5 pés de 2 sílabas, tônica na
  segunda). Em adaptações portuguesas, usa-se o **decassílabo** como
  equivalente natural.
- Efeito: cada quarteto desenvolve uma faceta ou argumento; o dístico
  final vira, resume ou contradiz ("volta") o que veio antes — é onde
  mora a "conclusão" ou o golpe de efeito do poema.

### Soneto petrarquiano (italiano)
- 14 versos: 1 octeto (8) + 1 sexteto (6).
- Esquema do octeto: ABBAABBA (rima interpolada, repetida duas vezes).
- Esquema do sexteto: variável — CDECDE, CDCDCD, CDEDCE, entre outras.
- Efeito: o octeto apresenta uma questão, tensão ou imagem; a "volta"
  (turn) acontece na virada para o sexteto, que responde, resolve ou
  reflete sobre o octeto. A volta do petrarquiano é mais cedo e mais
  "filosófica" que a do shakespeariano.

### Soneto camoniano (português — citar quando o poema for em decassílabos clássicos)
- 14 versos decassílabos: 2 quartetos (geralmente ABBA ABBA) + 2
  tercetos (esquemas variados, ex.: CDC DCD).
- Efeito: síntese entre o encadeamento do petrarquiano e a musicalidade
  do decassílabo heróico português.

## Haicai (haiku)
- 3 versos, contagem de sílabas **5-7-5** — em português, conte com
  `escandir_verso.py --simples` (soma direta, sem sinalefa nem corte na
  tônica final; ver `metrica-e-rima.md`).
- Sem rima obrigatória.
- Elementos tradicionais (nem sempre exigidos em haicais contemporâneos,
  mas valem para avaliação e para composição fiel à forma clássica):
  - **Kigo:** referência sazonal, explícita ou por imagem (flor de
    cerejeira = primavera; folhas secas = outono).
  - **Kireji** (corte): uma pausa ou quebra de pensamento entre duas
    partes do poema, geralmente marcada em português por travessão,
    reticências ou ponto-e-vírgula.
  - Foco em uma **imagem concreta e um instante único**, sem explicar a
    emoção diretamente — a emoção deve emergir da justaposição de
    imagens, não de adjetivos que a nomeiam.

## Tanka
- 5 versos, **5-7-5-7-7** sílabas (mesma lógica de contagem do haicai).
- Os três primeiros versos costumam funcionar como um haicai; os dois
  últimos (7-7) acrescentam uma reflexão, resposta emocional ou giro de
  perspectiva que o haicai, por natureza, evita.

## Villanelle
- 19 versos: 5 tercetos + 1 quarteto final.
- Dois **refrões** (versos inteiros repetidos): o 1º verso do primeiro
  terceto e o 3º verso do primeiro terceto reaparecem alternadamente
  como o fechamento dos tercetos seguintes, e os dois juntos fecham o
  quarteto final.
- Esquema de rima: ABA, repetido em cada terceto, ABAA no quarteto final.
- Efeito: a obsessão — a repetição dos refrões cria a sensação de um
  pensamento do qual o eu lírico não consegue escapar. Bom para temas de
  perda, insistência, memória circular.

## Limerique (limerick)
- 5 versos, esquema AABBA.
- Versos 1, 2 e 5 mais longos (tradicionalmente 3 pés anapésticos);
  versos 3 e 4 mais curtos (2 pés).
- Tom cômico ou nonsense quase por definição; a "piada" ou virada
  engraçada geralmente cai no verso 5.

## Rondó / rondel
- Forma de refrão: um verso ou par de versos inicial retorna como
  fechamento de estrofes subsequentes, criando um efeito circular.
- Existem várias variantes (rondó simples, rondel de 13/14 versos); ao
  usar, confirme com o usuário se ele tem uma variante específica em
  mente, já que o nome cobre estruturas distintas.

## Verso livre
- Sem contagem silábica fixa nem esquema de rima obrigatório.
- A musicalidade vem de outros recursos: aliteração, assonância,
  anáfora, ritmo de frase, disposição visual dos versos (quebras de
  linha como pontuação), repetição de estruturas sintáticas.
- Ao avaliar verso livre, não cobre métrica regular — avalie coerência
  de imagem, economia de linguagem, e se as quebras de linha fazem
  trabalho expressivo (não são arbitrárias).

## Formas luso-brasileiras (citar quando o pedido pedir explicitamente)
- **Redondilha (maior/menor):** estrofes tradicionais em versos de 5 ou
  7 sílabas, usadas na poesia popular, no cordel e por poetas como
  Camões e Gil Vicente fora do soneto.
- **Cordel:** sextilhas ou setilhas de redondilha maior (7 sílabas),
  rima geralmente ABCBDB ou variantes, tom narrativo e popular.
- **Trova:** quadra (4 versos) de redondilha maior, rima ABAB ou ABCB,
  tema geralmente sintético e de efeito ("golpe") no último verso.

## Escolhendo a forma certa numa transformação

Ao transformar um poema em outra forma (pedido do tipo "vira soneto" ou
"faz uma versão em haicai"), pergunte-se o que a nova forma vai *cortar*
e o que vai *ganhar*:
- Verso livre → soneto: será preciso condensar a ideia em 14 versos
  decassílabos com rima — normalmente exige escolher a imagem ou
  argumento central e descartar o resto.
- Poema longo → haicai: é um exercício de redução radical a um único
  instante/imagem — o haicai não cabe uma narrativa inteira.
- Soneto → verso livre: abre espaço para imagens que a métrica e a rima
  forçavam a cortar ou reformular; vale perguntar ao usuário se ele quer
  manter o conteúdo do original ao pé da letra ou aproveitar a liberdade
  para desenvolver algo que a forma fechada não permitia.

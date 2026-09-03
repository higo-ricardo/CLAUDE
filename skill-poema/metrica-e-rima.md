# Métrica e rima — conceitos de referência

Este arquivo detalha os conceitos usados para escandir, corrigir e avaliar
poemas em português. Consulte-o sempre que precisar classificar um verso,
identificar um esquema de rima ou explicar ao usuário por que um verso
"não bate" com os outros.

## Verso: contagem de sílabas poéticas

A sílaba poética **não é igual** à sílaba gramatical. Duas regras mudam a
contagem:

1. **Sinalefa (elisão):** quando uma palavra termina em vogal e a
   seguinte começa em vogal (ou "h" mudo + vogal), as duas vogais se
   fundem em uma única sílaba poética na leitura em voz alta. Ex.: "que
   arde" soa como "quear-de" — uma sílaba a menos do que a soma das
   partes. Monossílabos tônicos de conteúdo ("dói", "sol", "luz", "ver")
   tendem a resistir à fusão, porque perderiam o próprio acento.
2. **Conta-se até a última sílaba tônica do verso.** Sílabas átonas
   depois da última tônica não entram na contagem. Por isso, versos que
   terminam em palavra oxítona (chuVÁ) contam "cheio"; terminando em
   paroxítona (CHU-va), descarta-se a última sílaba; terminando em
   proparoxítona (LÂM-pa-da), descartam-se as duas últimas.

Use `scripts/escandir_verso.py` para aplicar essas regras automaticamente
em vez de contar de cabeça — é fácil errar sinalefa e tonicidade "no
olho", e o script torna a contagem auditável (mostra quantas elisões
aplicou).

**Exceção importante — formas importadas (haicai, tanka):** essas formas
não seguem a métrica clássica portuguesa; nas adaptações em português,
conta-se cada sílaba escrita, sem sinalefa e sem truncar na tônica final
(mais perto da contagem de moras do japonês). Use
`escandir_verso.py --simples` para esse caso. Ver `formas-fixas.md`.

### Classificação do verso pelo número de sílabas

| Sílabas | Nome                                   |
|---------|-----------------------------------------|
| 1       | monossílabo                             |
| 2       | dissílabo                               |
| 3       | trissílabo                              |
| 4       | tetrassílabo                            |
| 5       | redondilha menor                        |
| 6       | hexassílabo                             |
| 7       | redondilha maior                        |
| 8       | octossílabo                             |
| 9       | eneassílabo                             |
| 10      | decassílabo (o "verso heróico" dos sonetos e épicos) |
| 12      | dodecassílabo / alexandrino (cesura em 6+6) |

O decassílabo é o verso-padrão dos sonetos camonianos e da adaptação
portuguesa do pentâmetro iâmbico dos sonetos shakespearianos.

## Estrofe: nome pelo número de versos

| Versos | Nome       |
|--------|------------|
| 2      | dístico    |
| 3      | terceto    |
| 4      | quarteto   |
| 5      | quintilha  |
| 6      | sextilha   |
| 7      | sétima     |
| 8      | oitava     |
| 9      | nona       |
| 10     | década     |

## Rima

### Pela posição da sílaba tônica da última palavra
- **Aguda/oxítona:** tonic na última sílaba (ex.: "coração / paixão").
- **Grave/paroxítona:** tônica na penúltima (ex.: "amores / flores").
- **Esdrúxula/proparoxítona:** tônica na antepenúltima (ex.: "pássaro /
  ábaco") — rara, soa marcada, útil para efeito cômico ou virtuosístico.

### Pela qualidade sonora
- **Consoante:** identidade total de sons a partir da vogal tônica
  (vogal + consoantes seguintes iguais). É a rima "cheia" esperada na
  maioria das formas fixas.
- **Toante/assonante:** só as vogais coincidem, as consoantes diferem
  (ex.: "cantar / fadas" — vogal tônica "a" repete, mas o resto não é
  idêntico). Comum em cordel e em poesia popular.
- **Rica:** rima entre palavras de classes gramaticais diferentes (ex.:
  substantivo com verbo) — valorizada por exigir mais engenho.
- **Pobre:** rima entre palavras da mesma classe gramatical (ex.: dois
  substantivos, dois verbos na mesma flexão) — mais fácil de obter, por
  vezes soa previsível se usada em excesso.

### Esquemas (posição no poema)
Notação por letras, uma por som de rima distinto:
- **Emparelhada (AABB):** rima verso a verso, dois a dois.
- **Cruzada/alternada (ABAB):** alterna dois sons de rima.
- **Interpolada/opposta (ABBA):** rima "abraçada", comum no octeto do
  soneto petrarquiano.
- **Encadeada/terza rima (ABA BCB CDC...):** cada terceto retoma um som
  do anterior — usada por Dante na Divina Comédia.

Use `escandir_verso.py` (sem `--simples`) sobre um poema de várias linhas
para obter o esquema automaticamente a partir da última palavra de cada
verso — é uma aproximação fonética, então confira de ouvido quando o
resultado parecer estranho, especialmente com palavras raras ou nomes
próprios.

## Musicalidade — recursos sonoros e rítmicos

- **Aliteração:** repetição de sons consonantais no início ou interior
  de palavras próximas (ex.: "o rato roeu a roupa do rei de Roma").
- **Assonância:** repetição de sons vocálicos.
- **Anáfora:** repetição da mesma palavra ou expressão no início de
  versos sucessivos — cria cadência e ênfase.
- **Paranomásia:** aproximação sonora entre palavras de sentidos
  diferentes (ex.: "casa / caça").
- **Enjambement (encavalgamento):** quando a frase não termina no fim do
  verso e "transborda" para o verso seguinte, criando tensão entre a
  unidade métrica e a unidade sintática.
- **Ritmo:** padrão de alternância entre sílabas tônicas e átonas ao
  longo do verso. Versos com acentos regularmente espaçados (ex.: a cada
  2 ou 3 sílabas) soam mais cantantes; acentos irregulares soam mais
  próximos da fala natural. Ao corrigir um poema, vale observar não só
  se o número de sílabas bate, mas se as tônicas caem em posições
  parecidas verso a verso — dois decassílabos com 10 sílabas cada podem
  soar muito diferentes se os acentos internos não se correspondem.

## Como aplicar isso em correção e avaliação

Ao corrigir ou avaliar um poema, não trate a métrica como um fim em si
— ela serve ao efeito sonoro e emocional do poema. Um verso "fora da
métrica" pode ser:
- um erro real (quebra a expectativa criada pelo resto do poema, e não
  parece proposital) — vale sugerir ajuste;
- uma licença poética deliberada (dá ênfase, quebra o ritmo de propósito
  para marcar uma virada de sentido) — vale perguntar ao usuário antes
  de "consertar", ou observar isso na avaliação em vez de propor troca.

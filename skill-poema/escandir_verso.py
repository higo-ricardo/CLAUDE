#!/usr/bin/env python3
"""
escandir_verso.py — escansão métrica, rima e ritmo de versos em português.

Uso:
    python escandir_verso.py "verso único aqui"
    python escandir_verso.py --arquivo poema.txt
    python escandir_verso.py --arquivo poema.txt --simples   (para haicai/tanka)
    echo "linha1\nlinha2" | python escandir_verso.py -

    python escandir_verso.py --arquivo poema.txt --validar soneto_shakespeariano
        (compara o poema contra o perfil da forma em formas.json; ver
        lista de formas cadastradas nesse arquivo)
    python escandir_verso.py --arquivo poema.txt --rima
        (relatório expandido: agrupa por som de rima e classifica cada
        grupo por tonicidade e qualidade sonora — consoante/toante)
    python escandir_verso.py --arquivo poema.txt --stats
        (contagens objetivas: nº de versos, estrofes, palavras, média
        de sílabas por verso)

Modo padrão ("clássico"): aplica sinalefa e conta até a última sílaba
tônica do verso — é a regra da métrica portuguesa tradicional (redondilhas,
decassílabos, sonetos camonianos/shakespearianos adaptados etc.).

Modo --simples: soma direta das sílabas gramaticais, sem sinalefa e sem
truncar na tônica final. Use para haicai, tanka e formas orientais, cuja
contagem em português costuma seguir "uma sílaba escrita = uma conta".

Saída: para cada verso, número de sílabas poéticas (contadas até a última
sílaba tônica), classificação do verso, e — quando há mais de um verso —
o esquema de rima do conjunto (A, B, C...).

IMPORTANTE — isto é uma ferramenta de apoio, não um oráculo:
A separação silábica e a acentuação do português têm muitas exceções
(hiatos sem acento gráfico, palavras estrangeiras, nomes próprios,
licenças poéticas). O script aplica regras gerais e cobre a grande
maioria dos casos, mas o resultado deve ser conferido de ouvido,
especialmente em versos "quase certos" (1 sílaba de diferença) ou
com palavras raras. Trate a contagem como um ponto de partida objetivo
para a revisão, não como veredito final.
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

VOGAIS = "aeiouáéíóúâêôãõà"
VOGAIS_ACENTUADAS_HIATO = "íúÍÚ"  # í/ú acentuados quebram ditongo -> hiato
ONSETS_VALIDOS = {
    "pr", "pl", "br", "bl", "tr", "tl", "dr", "cr", "cl",
    "gr", "gl", "fr", "fl", "vr", "vl", "ch", "lh", "nh",
    "qu", "gu",
}


def _is_vowel(ch):
    return ch.lower() in VOGAIS


def separar_silabas(palavra):
    """Separa uma palavra em sílabas gramaticais (aproximação heurística)."""
    w = palavra.lower()
    if not w:
        return []

    # 1) localizar núcleos vocálicos (sequências de vogais = 1 núcleo,
    #    exceto quando a 2a vogal tem acento em í/ú -> hiato, separa)
    nucleos = []  # lista de (inicio, fim) de cada núcleo vocálico
    i = 0
    n = len(w)
    while i < n:
        if _is_vowel(w[i]):
            j = i + 1
            while j < n and _is_vowel(w[j]):
                # quebra de hiato: vogal acentuada em í/ú depois de outra vogal
                if w[j] in VOGAIS_ACENTUADAS_HIATO.lower():
                    break
                j += 1
            nucleos.append((i, j))
            i = j
        else:
            i += 1

    if not nucleos:
        return [w]  # sem vogais (raro/sigla) — trata como sílaba única

    silabas = []
    limite_anterior = 0
    for idx, (ini, fim) in enumerate(nucleos):
        if idx == 0:
            consoantes_antes = w[0:ini]
        else:
            consoantes_antes = w[limite_anterior:ini]

        if idx == 0:
            silabas.append(consoantes_antes + w[ini:fim])
        else:
            # decidir quanto do cluster de consoantes fica com a sílaba
            # anterior e quanto abre a próxima sílaba
            cluster = consoantes_antes
            if len(cluster) <= 1:
                onset = cluster
                coda_anterior = ""
            elif cluster[-2:] in ONSETS_VALIDOS:
                onset = cluster[-2:]
                coda_anterior = cluster[:-2]
            else:
                onset = cluster[-1:]
                coda_anterior = cluster[:-1]
            silabas[-1] += coda_anterior
            silabas.append(onset + w[ini:fim])
        limite_anterior = fim

    # consoantes finais (coda da palavra) ficam com a última sílaba
    silabas[-1] += w[limite_anterior:]
    return silabas


def _tem_acento(silaba):
    for ch in silaba:
        if ch in "áéíóúâêô":
            return True
    return False


ATONAS_COMUNS = {
    "o", "a", "os", "as", "um", "uns", "uma", "umas",
    "de", "em", "por", "com", "sem", "sob", "sobre", "ante", "após",
    "até", "desde", "entre", "para", "perante", "trás",
    "e", "ou", "mas", "nem", "que", "se", "como", "quando", "porque", "pois",
    "me", "te", "lhe", "nos", "vos", "lhes", "lo", "la", "los", "las", "no", "na",
}


def posicao_tonica(silabas, palavra=None):
    """
    Retorna o índice (0-based) da sílaba tônica, por heurística.
    Palavras monossilábicas átonas (artigos, preposições, conjunções,
    pronomes clíticos) retornam None: não carregam acento de intensidade
    dentro do verso, mesmo tendo uma única sílaba.
    """
    n = len(silabas)
    if n == 1:
        if palavra and re.sub(r"[.,;:!?]+$", "", palavra.lower()) in ATONAS_COMUNS:
            return None
        return 0

    for i, s in enumerate(silabas):
        if _tem_acento(s):
            return i

    ultima = silabas[-1]
    # terminações tipicamente oxítonas (quando sem acento gráfico)
    oxitonas_fim = (
        "r", "l", "z", "x", "n", "i", "u", "ã", "ão", "ãe", "ãos", "ãe s",
    )
    if ultima.endswith(("em", "ens")):
        return n - 1  # -em/-ens tônico final (ex.: também, ninguém)
    if ultima.rstrip("s").endswith(oxitonas_fim):
        return n - 1

    # regra geral: maioria das palavras portuguesas é paroxítona
    return max(n - 2, 0)


def _strip_acentos(txt):
    return "".join(
        c for c in unicodedata.normalize("NFD", txt)
        if unicodedata.category(c) != "Mn"
    )


def escandir_verso(verso):
    """
    Retorna dict com:
      palavras_silabadas: lista de (palavra, [sílabas], indice_tonica)
      total: nº de sílabas poéticas do verso (conta até a última tônica)
      elisoes: nº de fusões por sinalefa aplicadas
    """
    # separa palavras, preservando pontuação para saber onde há pausa forte
    tokens = re.findall(r"[\wÀ-ÿ]+|[^\wÀ-ÿ\s]", verso, re.UNICODE)
    palavras = [t for t in tokens if re.match(r"[\wÀ-ÿ]+", t)]

    info_palavras = []
    for p in palavras:
        sils = separar_silabas(p)
        tonica = posicao_tonica(sils, p)
        info_palavras.append({"palavra": p, "silabas": sils, "tonica": tonica})

    if not info_palavras:
        return {"palavras": [], "total": 0, "elisoes": 0}

    # monta a sequência linear de sílabas com marca de fim-de-palavra
    sequencia = []  # cada item: (texto_silaba, indice_palavra, eh_tonica)
    for pi, info in enumerate(info_palavras):
        for si, s in enumerate(info["silabas"]):
            sequencia.append([s, pi, si == info["tonica"]])

    # aplica sinalefa: se a sílaba final de uma palavra termina em vogal
    # (sem consoante depois) e a sílaba inicial da próxima começa em vogal,
    # fundem-se em uma só sílaba poética (mantém a marca de tônica se
    # alguma das duas era tônica).
    elisoes = 0
    i = 0
    while i < len(sequencia) - 1:
        atual = sequencia[i]
        prox = sequencia[i + 1]
        pi_atual, pi_prox = atual[1], prox[1]
        # só funde na fronteira entre a ÚLTIMA sílaba de uma palavra
        # e a PRIMEIRA da palavra seguinte
        # pi_prox == pi_atual + 1 só ocorre na transição entre a última
        # sílaba de uma palavra e a primeira sílaba da palavra seguinte,
        # já que a sequência é construída palavra por palavra em ordem
        eh_fronteira = pi_prox == pi_atual + 1
        # monossílabos tônicos (palavras de conteúdo: "dói", "sol", "luz"...)
        # tendem a resistir à sinalefa para não perder o próprio acento
        atual_eh_monossilabo_tonico = (
            len(info_palavras[pi_atual]["silabas"]) == 1 and atual[2] is True
        )
        if (
            eh_fronteira
            and not atual_eh_monossilabo_tonico
            and atual[0][-1:].lower() in VOGAIS
            and prox[0][:1].lower() in VOGAIS
        ):
            fundida_texto = atual[0] + prox[0]
            fundida_tonica = atual[2] or prox[2]
            sequencia[i] = [fundida_texto, pi_atual, fundida_tonica]
            del sequencia[i + 1]
            elisoes += 1
            # não avança i, para permitir fusão em cadeia (ex.: "a alma amada")
            continue
        i += 1

    total_bruto = len(sequencia)
    # sílaba poética conta-se ATÉ a última tônica do verso: descarta o que
    # vem depois da última sílaba marcada como tônica
    ultimo_indice_tonico = None
    for idx, item in enumerate(sequencia):
        if item[2]:
            ultimo_indice_tonico = idx
    if ultimo_indice_tonico is None:
        total = total_bruto
    else:
        total = ultimo_indice_tonico + 1

    return {
        "palavras": info_palavras,
        "sequencia": sequencia,
        "total": total,
        "elisoes": elisoes,
    }


CLASSIFICACAO_VERSO = {
    1: "monossílabo",
    2: "dissílabo",
    3: "trissílabo",
    4: "tetrassílabo",
    5: "redondilha menor",
    6: "hexassílabo",
    7: "redondilha maior",
    8: "octossílabo",
    9: "eneassílabo",
    10: "decassílabo",
    11: "hendecassílabo",
    12: "dodecassílabo (alexandrino, se com cesura em 6+6)",
    13: "tridecassílabo",
    14: "tetradecassílabo",
}


def classificar_verso(n):
    return CLASSIFICACAO_VERSO.get(n, f"verso de {n} sílabas (fora dos padrões clássicos)")


def chave_rima(palavra):
    """
    Aproximação fonética da terminação rimante: a partir da VOGAL da
    sílaba tônica (sem a consoante de abertura dessa sílaba — rima
    compara sons a partir da vogal tônica, não a consoante que a
    antecede) até o fim da palavra, com normalização leve de grafia
    (ç/ss/c(e,i) -> s ; ch -> x ; acentos removidos para comparação de
    timbre aberto/fechado simplificada).
    """
    sils = separar_silabas(palavra)
    tonica = posicao_tonica(sils)
    if tonica is None:
        tonica = len(sils) - 1
    silaba_tonica = sils[tonica]
    m = re.search(f"[{VOGAIS}]", silaba_tonica)
    silaba_tonica_sem_onset = silaba_tonica[m.start():] if m else silaba_tonica
    trecho = silaba_tonica_sem_onset + "".join(sils[tonica + 1:])
    trecho = trecho.lower()
    trecho = trecho.replace("ç", "s").replace("ss", "s")
    trecho = re.sub(r"c(?=[ei])", "s", trecho)
    trecho = trecho.replace("ch", "x")
    trecho = _strip_acentos(trecho)
    return trecho


def tipo_tonicidade_rima(palavra):
    """Classifica a palavra-rima quanto à posição da tônica."""
    sils = separar_silabas(palavra)
    tonica = posicao_tonica(sils, palavra)
    n = len(sils)
    if tonica is None:
        return "átona"
    if tonica == n - 1:
        return "aguda/oxítona"
    if tonica == n - 2:
        return "grave/paroxítona"
    if tonica == n - 3:
        return "esdrúxula/proparoxítona"
    return "indeterminada"


def tipo_qualidade_rima(chave_a, chave_b):
    """
    Compara duas chaves de rima (ver chave_rima) e classifica o par:
    'consoante' (vogais e consoantes coincidem), 'toante'/assonante
    (só as vogais coincidem) ou 'não rima' (nenhuma das duas).
    """
    if not chave_a or not chave_b:
        return "não rima"
    if chave_a == chave_b:
        return "consoante"
    vogais_a = "".join(c for c in chave_a if c in VOGAIS)
    vogais_b = "".join(c for c in chave_b if c in VOGAIS)
    if vogais_a and vogais_a == vogais_b:
        return "toante"
    return "não rima"


CLASSIFICACAO_ESTROFE = {
    1: "monóstico",
    2: "dístico",
    3: "terceto",
    4: "quarteto",
    5: "quintilha",
    6: "sextilha",
    7: "sétima",
    8: "oitava",
    9: "nona",
    10: "década",
}


def classificar_estrofe(n_versos):
    return CLASSIFICACAO_ESTROFE.get(n_versos, f"estrofe de {n_versos} versos")


def separar_estrofes(texto):
    """Divide o texto em estrofes por linhas em branco; cada estrofe é
    uma lista de versos (strings), ignorando linhas vazias internas."""
    estrofes = []
    atual = []
    for linha in texto.splitlines():
        if linha.strip():
            atual.append(linha)
        elif atual:
            estrofes.append(atual)
            atual = []
    if atual:
        estrofes.append(atual)
    return estrofes


def estatisticas_poema(texto, modo="classico"):
    """Contagens objetivas do poema: versos, estrofes, palavras e média
    de sílabas poéticas por verso."""
    estrofes = separar_estrofes(texto)
    linhas = [l for l in texto.splitlines() if l.strip()]
    n_palavras = sum(len(re.findall(r"[\wÀ-ÿ]+", l, re.UNICODE)) for l in linhas)

    totais = []
    for l in linhas:
        if modo == "simples":
            totais.append(contar_silabas_simples(l))
        else:
            totais.append(escandir_verso(l)["total"])

    media = round(sum(totais) / len(totais), 2) if totais else 0

    return {
        "n_versos": len(linhas),
        "n_estrofes": len(estrofes),
        "versos_por_estrofe": [len(e) for e in estrofes],
        "n_palavras": n_palavras,
        "media_silabas_por_verso": media,
        "silabas_por_verso": totais,
    }


def esquema_de_rima(versos):
    """Recebe lista de strings (versos) e retorna string tipo 'ABAB'."""
    ultimas_palavras = []
    for v in versos:
        palavras = re.findall(r"[\wÀ-ÿ]+", v, re.UNICODE)
        ultimas_palavras.append(palavras[-1] if palavras else "")

    chaves = [chave_rima(p) if p else "" for p in ultimas_palavras]
    letras = {}
    resultado = []
    proxima_letra = ord("A")
    for chave in chaves:
        if not chave:
            resultado.append("-")
            continue
        if chave not in letras:
            letras[chave] = chr(proxima_letra)
            proxima_letra += 1
        resultado.append(letras[chave])
    return "".join(resultado)


def contar_silabas_simples(verso):
    """
    Contagem simples: soma das sílabas gramaticais de cada palavra, sem
    sinalefa e sem truncar na última tônica. Use este modo para formas
    importadas que não seguem a métrica clássica portuguesa (haicai,
    tanka e afins costumam ser contados assim nas traduções/adaptações
    em português, seguindo a lógica de "uma sílaba escrita = uma conta",
    mais próxima da contagem de moras do japonês do que da escansão
    tradicional lusófona).
    """
    palavras = re.findall(r"[\wÀ-ÿ]+", verso, re.UNICODE)
    return sum(len(separar_silabas(p)) for p in palavras)


def analisar_poema(texto, modo="classico"):
    linhas = [l for l in texto.splitlines() if l.strip()]
    resultados = []
    for linha in linhas:
        if modo == "simples":
            total = contar_silabas_simples(linha)
            elisoes = 0
        else:
            r = escandir_verso(linha)
            total = r["total"]
            elisoes = r["elisoes"]
        resultados.append({
            "verso": linha,
            "silabas": total,
            "classificacao": classificar_verso(total),
            "elisoes": elisoes,
        })
    esquema = esquema_de_rima(linhas) if len(linhas) > 1 else None
    return resultados, esquema


def carregar_formas():
    caminho = Path(__file__).parent / "formas.json"
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _checar_esquema(obtido, esperado):
    """Compara dois esquemas de rima 'ABAB' etc. — mesma estrutura de
    repetição, não necessariamente as mesmas letras (a rima B do poema
    pode não ser a 2a letra usada, por isso comparamos o PADRÃO, não o
    texto literal)."""
    def normalizar(esq):
        mapa = {}
        prox = ord("A")
        saida = []
        for letra in esq:
            if letra == "-":
                saida.append("-")
                continue
            if letra not in mapa:
                mapa[letra] = chr(prox)
                prox += 1
            saida.append(mapa[letra])
        return "".join(saida)
    return normalizar(obtido) == normalizar(esperado)


def validar_forma(texto, nome_forma, formas=None):
    """
    Valida um poema contra o perfil estrutural de uma forma fixa
    (ver formas.json). Retorna um relatório objetivo (dict) — fatos
    mensuráveis (nº de versos, sílabas, esquema de rima), não um
    julgamento de qualidade.
    """
    formas = formas or carregar_formas()
    perfil = formas.get(nome_forma)
    if perfil is None:
        return {"erro": f"forma '{nome_forma}' não cadastrada em formas.json"}

    modo = perfil.get("modo", "classico")
    linhas = [l for l in texto.splitlines() if l.strip()]
    relatorio = {"forma": nome_forma}

    relatorio["n_versos"] = {
        "esperado": perfil["n_versos"], "obtido": len(linhas),
        "ok": len(linhas) == perfil["n_versos"],
    }

    totais = []
    for l in linhas:
        totais.append(contar_silabas_simples(l) if modo == "simples" else escandir_verso(l)["total"])

    if "silabas_por_verso" in perfil:
        alvo = perfil["silabas_por_verso"]
        fora = [
            {"linha": i + 1, "esperado": alvo, "obtido": t}
            for i, t in enumerate(totais) if t != alvo
        ]
        relatorio["versos_fora_da_metrica"] = fora
    elif "silabas_por_verso_lista" in perfil:
        alvo_lista = perfil["silabas_por_verso_lista"]
        fora = [
            {"linha": i + 1, "esperado": alvo_lista[i], "obtido": t}
            for i, t in enumerate(totais)
            if i < len(alvo_lista) and t != alvo_lista[i]
        ]
        relatorio["versos_fora_da_metrica"] = fora

    esquema_obtido = esquema_de_rima(linhas) if len(linhas) > 1 else ""
    relatorio["esquema_rima_obtido"] = esquema_obtido

    if "esquema_rima" in perfil:
        esperado = perfil["esquema_rima"]
        if esperado is None:
            relatorio["esquema_rima_check"] = "não exigido nesta forma"
        else:
            relatorio["esquema_rima_ok"] = (
                len(esquema_obtido) == len(esperado)
                and _checar_esquema(esquema_obtido, esperado)
            )
    elif "esquema_rima_octeto" in perfil:
        # soneto petrarquiano: 8 (octeto) + 6 (sexteto), regras distintas
        octeto, sexteto = esquema_obtido[:8], esquema_obtido[8:]
        relatorio["octeto_ok"] = _checar_esquema(octeto, perfil["esquema_rima_octeto"])
        relatorio["sexteto_ok"] = any(
            _checar_esquema(sexteto, opc) for opc in perfil["esquema_rima_sexteto_opcoes"]
        )
    elif "esquema_rima_quartetos" in perfil:
        # soneto camoniano: 8 (2 quartetos) + 6 (2 tercetos)
        quartetos, tercetos = esquema_obtido[:8], esquema_obtido[8:]
        relatorio["quartetos_ok"] = _checar_esquema(quartetos, perfil["esquema_rima_quartetos"])
        relatorio["tercetos_ok"] = any(
            _checar_esquema(tercetos, opc) for opc in perfil["esquema_rima_tercetos_opcoes"]
        )

    if "observacao" in perfil:
        relatorio["observacao"] = perfil["observacao"]

    return relatorio


def relatorio_rima(texto, modo="classico"):
    """Relatório de rima expandido: tonicidade e qualidade de cada par
    que compartilha o mesmo esquema de rima."""
    linhas = [l for l in texto.splitlines() if l.strip()]
    ultimas = []
    for l in linhas:
        palavras = re.findall(r"[\wÀ-ÿ]+", l, re.UNICODE)
        ultimas.append(palavras[-1] if palavras else "")

    chaves = [chave_rima(p) if p else "" for p in ultimas]
    esquema = esquema_de_rima(linhas)

    por_letra = {}
    for i, letra in enumerate(esquema):
        por_letra.setdefault(letra, []).append(i)

    grupos = []
    for letra, indices in sorted(por_letra.items()):
        if letra == "-":
            continue
        palavras_grupo = [ultimas[i] for i in indices]
        tonicidades = [tipo_tonicidade_rima(ultimas[i]) for i in indices]
        qualidade = "único" if len(indices) < 2 else tipo_qualidade_rima(
            chaves[indices[0]], chaves[indices[1]]
        )
        grupos.append({
            "letra": letra,
            "versos": [i + 1 for i in indices],
            "palavras": palavras_grupo,
            "tonicidade": tonicidades,
            "qualidade_sonora": qualidade,
        })

    return {"esquema": esquema, "grupos": grupos}


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    modo = "classico"
    if "--simples" in args:
        modo = "simples"
        args = [a for a in args if a != "--simples"]

    modo_especial = None
    forma_alvo = None
    if "--validar" in args:
        idx = args.index("--validar")
        forma_alvo = args[idx + 1]
        modo_especial = "validar"
        args = args[:idx] + args[idx + 2:]
    elif "--rima" in args:
        modo_especial = "rima"
        args = [a for a in args if a != "--rima"]
    elif "--stats" in args:
        modo_especial = "stats"
        args = [a for a in args if a != "--stats"]

    if args[0] == "--arquivo" and len(args) > 1:
        with open(args[1], encoding="utf-8") as f:
            texto = f.read()
    elif args[0] == "-":
        texto = sys.stdin.read()
    else:
        texto = "\n".join(args)

    if modo_especial == "validar":
        relatorio = validar_forma(texto, forma_alvo)
        print(json.dumps(relatorio, ensure_ascii=False, indent=2))
        return

    if modo_especial == "rima":
        relatorio = relatorio_rima(texto, modo=modo)
        print(json.dumps(relatorio, ensure_ascii=False, indent=2))
        return

    if modo_especial == "stats":
        relatorio = estatisticas_poema(texto, modo=modo)
        print(json.dumps(relatorio, ensure_ascii=False, indent=2))
        return

    resultados, esquema = analisar_poema(texto, modo=modo)
    for i, r in enumerate(resultados, 1):
        nota_elisao = f"  ({r['elisoes']} elisão(ões))" if r["elisoes"] else ""
        print(f"{i:2d}. [{r['silabas']:2d} sílabas | {r['classificacao']}]{nota_elisao}  {r['verso']}")

    if esquema:
        print(f"\nEsquema de rima (aproximado): {esquema}")


if __name__ == "__main__":
    main()

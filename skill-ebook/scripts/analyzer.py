#!/usr/bin/env python3
"""
analyzer.py — Análise determinística de texto para a Editora Ebook.
Retorna dados estruturados para a LLM usar no julgamento editorial.

Modos disponíveis:
  passive      — detecta frases em voz passiva
  readability  — índice Flesch, média palavras/frase
  jargon       — termos técnicos sem explicação no texto
  balance      — palavras por capítulo, desvio da média
  gap          — cobertura do sumário vs. conteúdo existente
  numbering    — inconsistências em listas numeradas

Uso:
  python analyzer.py --text cap1.md --mode passive
  python analyzer.py --text cap1.md --mode readability --level leigo
  python analyzer.py --text cap1.md --mode jargon --glossary glossary.json
  python analyzer.py --mode balance --chapters-dir ./chapters/
  python analyzer.py --mode gap --summary summary.json --chapters-dir ./chapters/
"""

import argparse
import json
import os
import re
import sys


# ── Voz passiva ───────────────────────────────────────────────────────────────

PASSIVE_PATTERNS = [
    r'\b(é|são|foi|foram|será|serão|seria|seriam|tem sido|têm sido)\s+\w+d[ao]s?\b',
    r'\b(está|estão|estava|estavam|estará|estarão)\s+sendo\s+\w+d[ao]s?\b',
    r'\b(pode|podem|deve|devem)\s+ser\s+\w+d[ao]s?\b',
]


def detect_passive(text):
    results = []
    for i, line in enumerate(text.splitlines(), 1):
        for pat in PASSIVE_PATTERNS:
            matches = re.findall(pat, line, re.IGNORECASE)
            if matches:
                results.append({"linha": i, "trecho": line.strip()[:120]})
                break
    return results


# ── Legibilidade ──────────────────────────────────────────────────────────────

def count_syllables_pt(word):
    """Estimativa de sílabas em português por contagem de vogais."""
    word = re.sub(r'[^a-záéíóúãõâêîôûàü]', '', word.lower())
    vowels = re.findall(r'[aeiouáéíóúãõâêîôûàü]', word)
    count = len(vowels)
    # Ditongos reduzem contagem
    diphthongs = re.findall(r'[aeiou][aeiou]', word.lower())
    return max(1, count - len(diphthongs))


def flesch_pt(text):
    """Índice Flesch adaptado para português (Martins et al.)."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    if not sentences:
        return None, None, None

    words_all = re.findall(r'\b[a-záéíóúãõâêîôûàü]+\b', text.lower())
    if not words_all:
        return None, None, None

    total_words = len(words_all)
    total_sentences = len(sentences)
    total_syllables = sum(count_syllables_pt(w) for w in words_all)

    avg_words = round(total_words / total_sentences, 1)
    avg_syllables = round(total_syllables / total_words, 2)

    # Fórmula Flesch para PT-BR
    flesch = round(248.835 - (1.015 * avg_words) - (84.6 * avg_syllables), 1)
    flesch = max(0, min(100, flesch))

    if flesch >= 75:
        classification = "Fácil"
    elif flesch >= 50:
        classification = "Médio"
    elif flesch >= 25:
        classification = "Difícil"
    else:
        classification = "Muito difícil"

    return avg_words, flesch, classification


LEVEL_LIMITS = {
    "leigo": 20, "iniciante": 22, "intermediario": 28,
    "avancado": 32, "especialista": 40,
}


def readability_report(text, level):
    avg_words, flesch, classification = flesch_pt(text)
    if avg_words is None:
        return {"erro": "Texto muito curto ou sem sentenças detectáveis."}

    limit = LEVEL_LIMITS.get(level, 25)
    sentences = re.split(r'[.!?]+', text)
    long_sentences = [
        {"trecho": s.strip()[:100], "palavras": len(s.split())}
        for s in sentences
        if len(s.split()) > limit
    ]

    return {
        "media_palavras_por_frase": avg_words,
        "limite_para_nivel": limit,
        "frases_acima_limite": len(long_sentences),
        "exemplos_frases_longas": long_sentences[:5],
        "flesch": flesch,
        "classificacao": classification,
        "nivel_alvo": level,
        "status": "✅ adequado" if avg_words <= limit else "⚠️ acima do limite",
    }


# ── Jargões ───────────────────────────────────────────────────────────────────

def detect_jargon(text, glossary):
    """Termos do glossário que aparecem no texto sem definição inline."""
    results = []
    text_lower = text.lower()
    for term in glossary.get("terms", []):
        term_lower = term.lower()
        if term_lower in text_lower:
            # Verificar se há definição inline (padrão: "termo: definição" ou "termo (definição)")
            inline = re.search(
                rf'\b{re.escape(term_lower)}\b\s*[:(—]',
                text_lower
            )
            if not inline:
                results.append(term)
    return results


# ── Equilíbrio de capítulos ───────────────────────────────────────────────────

def balance_report(chapters_dir):
    chapters = {}
    for fname in sorted(os.listdir(chapters_dir)):
        if fname.endswith(".md"):
            path = os.path.join(chapters_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            words = len(re.findall(r'\b\w+\b', content))
            chapters[fname] = words

    if not chapters:
        return {"erro": "Nenhum arquivo .md encontrado no diretório."}

    values = list(chapters.values())
    avg = round(sum(values) / len(values))
    threshold = avg * 0.30

    report = []
    for name, count in chapters.items():
        deviation = count - avg
        flag = ""
        if abs(deviation) > threshold:
            flag = "⚠️ desproporcional"
        report.append({
            "arquivo": name,
            "palavras": count,
            "desvio_da_media": deviation,
            "flag": flag,
        })

    return {
        "media_palavras": avg,
        "limite_desvio_30pct": round(threshold),
        "capitulos": report,
    }


# ── Gap do sumário ────────────────────────────────────────────────────────────

def gap_report(summary_file, chapters_dir):
    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)

    existing = {
        fname.replace(".md", "").lower()
        for fname in os.listdir(chapters_dir)
        if fname.endswith(".md")
    }

    results = []
    for item in summary.get("chapters", []):
        key = item["id"].lower()
        title = item.get("title", item["id"])
        if key in existing:
            # Estimar cobertura pela contagem de palavras
            path = os.path.join(chapters_dir, f"{item['id']}.md")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    words = len(re.findall(r'\b\w+\b', f.read()))
                target = item.get("target_words", 1000)
                pct = min(100, round((words / target) * 100))
                status = "✅" if pct >= 80 else "🔶"
                results.append({"capitulo": title, "status": status,
                                 "cobertura": f"{pct}%", "palavras": words})
            else:
                results.append({"capitulo": title, "status": "❌", "cobertura": "0%"})
        else:
            results.append({"capitulo": title, "status": "❌", "cobertura": "0%"})

    total = len(results)
    completos = sum(1 for r in results if r["status"] == "✅")
    parciais = sum(1 for r in results if r["status"] == "🔶")
    ausentes = sum(1 for r in results if r["status"] == "❌")

    return {
        "resumo": {"total": total, "completos": completos,
                   "parciais": parciais, "ausentes": ausentes},
        "capitulos": results,
    }


# ── Numeração sequencial ──────────────────────────────────────────────────────

def numbering_report(text):
    issues = []
    in_list = False
    expected = 1
    for i, line in enumerate(text.splitlines(), 1):
        m = re.match(r'^(\d+)\.\s', line.strip())
        if m:
            num = int(m.group(1))
            if in_list and num != expected:
                issues.append({
                    "linha": i,
                    "encontrado": num,
                    "esperado": expected,
                    "trecho": line.strip()[:80],
                })
            in_list = True
            expected = num + 1
        elif in_list and line.strip() == "":
            in_list = False
            expected = 1
        elif in_list and not re.match(r'^\s', line):
            in_list = False
            expected = 1

    return issues


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analyzer da Editora Ebook")
    parser.add_argument("--text", help="Arquivo .md para análise")
    parser.add_argument("--mode", required=True,
                        choices=["passive", "readability", "jargon",
                                 "balance", "gap", "numbering"])
    parser.add_argument("--level", default="intermediario",
                        choices=["leigo", "iniciante", "intermediario",
                                 "avancado", "especialista"])
    parser.add_argument("--glossary", help="JSON com lista de termos técnicos")
    parser.add_argument("--summary", help="JSON com sumário planejado (modo gap)")
    parser.add_argument("--chapters-dir", default=".", help="Diretório com .md dos capítulos")
    args = parser.parse_args()

    if args.mode in ("passive", "readability", "jargon", "numbering"):
        if not args.text:
            parser.error(f"--text é obrigatório para o modo {args.mode}")
        with open(args.text, "r", encoding="utf-8") as f:
            text = f.read()

    if args.mode == "passive":
        results = detect_passive(text)
        print(json.dumps({"total": len(results), "ocorrencias": results},
                         ensure_ascii=False, indent=2))

    elif args.mode == "readability":
        print(json.dumps(readability_report(text, args.level),
                         ensure_ascii=False, indent=2))

    elif args.mode == "jargon":
        if not args.glossary:
            parser.error("--glossary é obrigatório para o modo jargon")
        with open(args.glossary, "r", encoding="utf-8") as f:
            glossary = json.load(f)
        results = detect_jargon(text, glossary)
        print(json.dumps({"total_sem_definicao": len(results),
                          "termos": results}, ensure_ascii=False, indent=2))

    elif args.mode == "balance":
        print(json.dumps(balance_report(args.chapters_dir),
                         ensure_ascii=False, indent=2))

    elif args.mode == "gap":
        if not args.summary:
            parser.error("--summary é obrigatório para o modo gap")
        print(json.dumps(gap_report(args.summary, args.chapters_dir),
                         ensure_ascii=False, indent=2))

    elif args.mode == "numbering":
        issues = numbering_report(text)
        print(json.dumps({"total_inconsistencias": len(issues),
                          "problemas": issues}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

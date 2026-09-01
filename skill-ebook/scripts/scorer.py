#!/usr/bin/env python3
"""
scorer.py — Cálculo determinístico de scores da Editora Ebook.
A LLM fornece as notas brutas S1–S5; este script calcula tudo o mais.

Uso:
  python scorer.py --s1 8.5 --s2 7.2 --s3 9.0 --s4 10.0 --s5 6.5 \
                   --stage M5 --chapter "Cap. 1" --version v1.2

  python scorer.py --consolidate          # tabela de todos os capítulos
  python scorer.py --scorecard Cap1       # scorecard de um capítulo específico
"""

import argparse
import json
import os
import sys
from datetime import datetime

SCORES_FILE = os.path.join(os.path.dirname(__file__), "../data/scores.json")

WEIGHTS = {"S1": 0.20, "S2": 0.35, "S3": 0.20, "S4": 0.15, "S5": 0.10}

SECTION_NAMES = {
    "S1": "Gancho / Abertura",
    "S2": "Desenvolvimento",
    "S3": "Adequação ao Público",
    "S4": "Integridade Factual",
    "S5": "Fechamento / Transição",
}

STAGE_THRESHOLDS = {"M4": 6.0, "M5": 7.0, "M6": 7.5, "M7": 8.0}


def load_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_scores(data):
    os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def calculate_score(s1, s2, s3, s4, s5):
    raw = {"S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": s5}
    total = sum(raw[k] * WEIGHTS[k] for k in raw)
    return round(total, 1)


def weakest_section(s1, s2, s3, s4, s5):
    scores = {"S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": s5}
    key = min(scores, key=scores.get)
    return f"{key} — {SECTION_NAMES[key]} ({scores[key]})"


def scorecard_md(chapter, version, stage, s1, s2, s3, s4, s5, final, threshold, status):
    lines = [
        f"## 📊 Scorecard — {chapter}",
        f"**Estágio**: {stage} | **Versão**: {version} | **Data**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| Seção | Peso | Score | Seção |",
        "|---|---|---|---|",
        f"| S1 — {SECTION_NAMES['S1']} | 20% | {s1}/10 | Gancho |",
        f"| S2 — {SECTION_NAMES['S2']} | 35% | {s2}/10 | Corpo |",
        f"| S3 — {SECTION_NAMES['S3']} | 20% | {s3}/10 | Público |",
        f"| S4 — {SECTION_NAMES['S4']} | 15% | {s4}/10 | Fatos |",
        f"| S5 — {SECTION_NAMES['S5']} | 10% | {s5}/10 | Fechamento |",
        "",
        f"**Score Final**: {final}/10",
        f"**Limiar {stage}**: {threshold}/10",
        f"**Status**: {'✅ APROVADO' if status else '❌ RETRABALHO NECESSÁRIO'}",
        f"**Seção mais fraca**: {weakest_section(s1, s2, s3, s4, s5)}",
    ]
    return "\n".join(lines)


def consolidate_md(data):
    if not data:
        return "Nenhum capítulo registrado ainda."
    lines = [
        "## 📊 Score Geral do Projeto",
        "",
        "| Capítulo | S1 | S2 | S3 | S4 | S5 | Final | Status |",
        "|---|---|---|---|---|---|---|---|",
    ]
    scores_list = []
    for chapter, info in data.items():
        s = info.get("scores", {})
        final = info.get("final", 0)
        status = "✅" if info.get("approved") else "❌"
        lines.append(
            f"| {chapter} | {s.get('S1','—')} | {s.get('S2','—')} | "
            f"{s.get('S3','—')} | {s.get('S4','—')} | {s.get('S5','—')} | "
            f"**{final}** | {status} |"
        )
        scores_list.append(final)

    if scores_list:
        avg = round(sum(scores_list) / len(scores_list), 1)
        approved = sum(1 for v in data.values() if v.get("approved"))
        rework = len(data) - approved
        lines += [
            "",
            f"**Média do manuscrito**: {avg}/10",
            f"**Capítulos aprovados**: {approved}/{len(data)}",
            f"**Em retrabalho**: {rework}",
        ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scorer da Editora Ebook")
    parser.add_argument("--s1", type=float)
    parser.add_argument("--s2", type=float)
    parser.add_argument("--s3", type=float)
    parser.add_argument("--s4", type=float)
    parser.add_argument("--s5", type=float)
    parser.add_argument("--stage", choices=["M4", "M5", "M6", "M7"], default="M5")
    parser.add_argument("--chapter", default="Capítulo")
    parser.add_argument("--version", default="v1.0")
    parser.add_argument("--consolidate", action="store_true")
    parser.add_argument("--scorecard", metavar="CHAPTER")
    args = parser.parse_args()

    data = load_scores()

    if args.consolidate:
        print(consolidate_md(data))
        return

    if args.scorecard:
        entry = data.get(args.scorecard)
        if not entry:
            print(f"Capítulo '{args.scorecard}' não encontrado em scores.json")
            sys.exit(1)
        s = entry["scores"]
        final = entry["final"]
        stage = entry.get("stage", "M5")
        threshold = STAGE_THRESHOLDS.get(stage, 7.0)
        print(scorecard_md(
            args.scorecard, entry.get("version", "v1.0"), stage,
            s["S1"], s["S2"], s["S3"], s["S4"], s["S5"],
            final, threshold, entry.get("approved", False)
        ))
        return

    # Calcular e salvar
    if None in (args.s1, args.s2, args.s3, args.s4, args.s5):
        parser.error("Forneça --s1 --s2 --s3 --s4 --s5 para calcular score.")

    final = calculate_score(args.s1, args.s2, args.s3, args.s4, args.s5)
    threshold = STAGE_THRESHOLDS.get(args.stage, 7.0)
    approved = final >= threshold

    data[args.chapter] = {
        "scores": {"S1": args.s1, "S2": args.s2, "S3": args.s3,
                   "S4": args.s4, "S5": args.s5},
        "final": final,
        "stage": args.stage,
        "version": args.version,
        "approved": approved,
        "timestamp": datetime.now().isoformat(),
    }
    save_scores(data)

    print(scorecard_md(
        args.chapter, args.version, args.stage,
        args.s1, args.s2, args.s3, args.s4, args.s5,
        final, threshold, approved
    ))
    print(f"\n[RESULTADO: score_final={final} status={'APROVADO' if approved else 'RETRABALHO'} "
          f"limiar={threshold} secao_mais_fraca={weakest_section(args.s1, args.s2, args.s3, args.s4, args.s5)}]")


if __name__ == "__main__":
    main()

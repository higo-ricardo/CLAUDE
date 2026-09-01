#!/usr/bin/env python3
"""
decisions.py — Log determinístico de decisões editoriais da Editora Ebook.

Uso:
  python decisions.py --action add --category TOM \
         --decision "Conversacional, 2ª pessoa, sem formalidade" --by Usuário --stage M1

  python decisions.py --action list
  python decisions.py --action check --text cap1.md
  python decisions.py --action pending
  python decisions.py --action alter --id D-03 --decision "Nova decisão"
"""

import argparse
import json
import os
import re
import shutil
from datetime import datetime

DATA_DIR   = os.path.join(os.path.dirname(__file__), "../data")
DEC_FILE   = os.path.join(DATA_DIR, "decisions.json")

CATEGORIES = ["TOM", "PUB", "EST", "LNG", "CIT", "GRF", "POS", "FMT", "MKT"]

CATEGORY_NAMES = {
    "TOM": "Tom e voz",
    "PUB": "Público-alvo",
    "EST": "Estrutura",
    "LNG": "Linguagem",
    "CIT": "Citação e fontes",
    "GRF": "Grafia",
    "POS": "Posição autoral",
    "FMT": "Formatação",
    "MKT": "Marketing e publicação",
}


def load():
    if os.path.exists(DEC_FILE):
        with open(DEC_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"locked": [], "pending": [], "history": []}


def save(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(DEC_FILE):
        shutil.copy2(DEC_FILE, DEC_FILE + ".bak")
    with open(DEC_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def next_id(data):
    existing = [d["id"] for d in data["locked"]]
    nums = [int(re.search(r'\d+', eid).group()) for eid in existing if re.search(r'\d+', eid)]
    return f"D-{(max(nums) + 1):02d}" if nums else "D-01"


# ── Add ───────────────────────────────────────────────────────────────────────

def action_add(category, decision, by, stage):
    if category not in CATEGORIES:
        print(f"Categoria inválida. Use: {', '.join(CATEGORIES)}")
        return

    data = load()
    did = next_id(data)
    entry = {
        "id": did,
        "category": category,
        "category_name": CATEGORY_NAMES[category],
        "decision": decision,
        "stage": stage,
        "by": by,
        "timestamp": datetime.now().isoformat(),
        "status": "locked",
    }
    data["locked"].append(entry)
    save(data)
    print(f"✅ Decisão travada: {did}")
    print(f"   Categoria: {CATEGORY_NAMES[category]} ({category})")
    print(f"   Decisão: {decision}")
    print(f"   Registrada em: {stage} por {by}")


# ── List ──────────────────────────────────────────────────────────────────────

def action_list():
    data = load()
    locked = data.get("locked", [])
    if not locked:
        print("Nenhuma decisão travada ainda.")
        return

    lines = [
        "## 📌 Decisões Editoriais Travadas", "",
        "| ID | Cat. | Decisão | Estágio | Por |",
        "|---|---|---|---|---|",
    ]
    for d in locked:
        lines.append(
            f"| {d['id']} | {d['category']} | {d['decision'][:60]} | {d['stage']} | {d['by']} |"
        )

    pending = data.get("pending", [])
    if pending:
        lines += ["", "## ⏳ Decisões em Aberto", "",
                  "| # | Questão | Urgência |", "|---|---|---|"]
        for p in pending:
            lines.append(f"| {p.get('id','—')} | {p['question']} | {p.get('urgency','—')} |")

    print("\n".join(lines))


# ── Check ─────────────────────────────────────────────────────────────────────

def action_check(text_file):
    """
    Verifica conflitos entre o texto e decisões travadas de grafia (GRF)
    e linguagem (LNG) — as únicas detectáveis deterministicamente.
    Decisões de TOM, POS etc. são julgamento da LLM.
    """
    data = load()
    if not os.path.exists(text_file):
        print(f"Arquivo não encontrado: {text_file}")
        return

    with open(text_file, "r", encoding="utf-8") as f:
        text = f.read()

    conflicts = []
    for d in data.get("locked", []):
        if d["category"] == "GRF":
            # Extrair pares de grafia correta/errada da decisão
            # Padrão esperado: '"termo-correto" não "termo-errado"' ou '"e-mail" (com hífen)'
            correct = re.findall(r'"([^"]+)"', d["decision"])
            for term in correct:
                # Verificar variações comuns (com/sem hífen, maiúsculas)
                variants = set()
                variants.add(term.replace("-", ""))
                variants.add(term.replace("-", " "))
                for var in variants:
                    if var.lower() != term.lower() and var.lower() in text.lower():
                        lines_found = [
                            i + 1 for i, line in enumerate(text.splitlines())
                            if var.lower() in line.lower()
                        ]
                        conflicts.append({
                            "decisao": d["id"],
                            "categoria": d["category"],
                            "problema": f"Grafia '{var}' encontrada; decisão exige '{term}'",
                            "linhas": lines_found[:5],
                        })

    if not conflicts:
        print("✅ Nenhum conflito detectável com decisões travadas.")
    else:
        print(f"⚠️ {len(conflicts)} conflito(s) detectado(s):\n")
        for c in conflicts:
            print(f"  [{c['decisao']}] {c['problema']}")
            print(f"  Linhas: {c['linhas']}")
            print()
        print("Nota: conflitos de TOM, PUB, EST, LNG, POS, FMT, MKT requerem avaliação da LLM.")


# ── Pending ───────────────────────────────────────────────────────────────────

def action_pending():
    data = load()
    pending = data.get("pending", [])
    if not pending:
        print("Nenhuma decisão pendente.")
        return

    lines = ["## ⏳ Decisões em Aberto", "",
             "| ID | Categoria | Questão | Urgência |",
             "|---|---|---|---|"]
    for p in pending:
        lines.append(
            f"| {p.get('id','—')} | {p.get('category','—')} | {p['question']} | {p.get('urgency','—')} |"
        )
    print("\n".join(lines))


def action_add_pending(category, question, urgency):
    data = load()
    pid = f"P-{(len(data['pending']) + 1):02d}"
    data["pending"].append({
        "id": pid, "category": category,
        "question": question, "urgency": urgency,
    })
    save(data)
    print(f"✅ Decisão pendente registrada: {pid} — {question}")


# ── Alter ─────────────────────────────────────────────────────────────────────

def action_alter(did, new_decision, reason, by):
    data = load()
    entry = next((d for d in data["locked"] if d["id"] == did), None)
    if not entry:
        print(f"Decisão '{did}' não encontrada.")
        return

    old = entry["decision"]
    entry["decision"] = new_decision
    entry["last_modified"] = datetime.now().isoformat()

    data["history"].append({
        "id": did,
        "old_decision": old,
        "new_decision": new_decision,
        "reason": reason,
        "altered_by": by,
        "timestamp": datetime.now().isoformat(),
    })
    save(data)
    print(f"✅ Decisão {did} alterada.")
    print(f"   Anterior: {old}")
    print(f"   Nova:     {new_decision}")
    print(f"   Motivo:   {reason}")
    print(f"   ⚠️  Verifique capítulos já escritos para atualizar conforme nova decisão.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Decisions da Editora Ebook")
    parser.add_argument("--action", required=True,
                        choices=["add", "list", "check", "pending",
                                 "add-pending", "alter"])
    parser.add_argument("--category")
    parser.add_argument("--decision")
    parser.add_argument("--by", default="Usuário")
    parser.add_argument("--stage", default="M1")
    parser.add_argument("--text", help="Arquivo .md para verificar conflitos")
    parser.add_argument("--id", help="ID da decisão para alterar (ex: D-03)")
    parser.add_argument("--reason", default="Não especificado")
    parser.add_argument("--question", help="Questão em aberto (add-pending)")
    parser.add_argument("--urgency", default="Média")
    args = parser.parse_args()

    if args.action == "add":
        action_add(args.category, args.decision, args.by, args.stage)
    elif args.action == "list":
        action_list()
    elif args.action == "check":
        action_check(args.text)
    elif args.action == "pending":
        action_pending()
    elif args.action == "add-pending":
        action_add_pending(args.category, args.question, args.urgency)
    elif args.action == "alter":
        action_alter(args.id, args.decision, args.reason, args.by)


if __name__ == "__main__":
    main()

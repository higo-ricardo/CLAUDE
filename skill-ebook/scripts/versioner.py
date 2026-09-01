#!/usr/bin/env python3
"""
versioner.py — Versionamento determinístico para a Editora Ebook.
Gerencia state.json e histórico de versões por capítulo.

Uso:
  python versioner.py --action save --chapter "Cap. 1" --version v1.2 \
                      --agent AUTOR --description "Expansão +800 palavras" \
                      --file cap1.md

  python versioner.py --action history
  python versioner.py --action diff --chapter "Cap. 1" --compare v1.1:v1.2
  python versioner.py --action rollback --chapter "Cap. 1" --version v1.1
  python versioner.py --action state        # exibe bloco de estado completo
"""

import argparse
import difflib
import json
import os
import shutil
from datetime import datetime

DATA_DIR   = os.path.join(os.path.dirname(__file__), "../data")
STATE_FILE = os.path.join(DATA_DIR, "project.json")
VER_FILE   = os.path.join(DATA_DIR, "versions.json")
VER_DIR    = os.path.join(DATA_DIR, "version_files")


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Backup antes de sobrescrever
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Save ──────────────────────────────────────────────────────────────────────

def action_save(chapter, version, agent, description, file_path):
    versions = load_json(VER_FILE, {})
    if chapter not in versions:
        versions[chapter] = []

    # Salvar o conteúdo do arquivo nesta versão
    if file_path and os.path.exists(file_path):
        os.makedirs(VER_DIR, exist_ok=True)
        safe_name = chapter.replace(" ", "_").replace("/", "-")
        dest = os.path.join(VER_DIR, f"{safe_name}__{version}.md")
        shutil.copy2(file_path, dest)
        content_saved = dest
    else:
        content_saved = None

    entry = {
        "version": version,
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "description": description,
        "file": content_saved,
    }
    versions[chapter].append(entry)
    save_json(VER_FILE, versions)

    print(f"✅ Versão {version} salva para '{chapter}' (agente: {agent})")
    print(f"   Descrição: {description}")
    if content_saved:
        print(f"   Arquivo: {content_saved}")


# ── History ───────────────────────────────────────────────────────────────────

def action_history():
    versions = load_json(VER_FILE, {})
    if not versions:
        print("Nenhuma versão registrada ainda.")
        return

    lines = ["## 📜 Histórico de Versões", "",
             "| Capítulo | Versão | Data | Agente | Descrição |",
             "|---|---|---|---|---|"]

    for chapter, entries in versions.items():
        for e in sorted(entries, key=lambda x: x["timestamp"], reverse=True):
            ts = e["timestamp"][:16].replace("T", " ")
            lines.append(
                f"| {chapter} | {e['version']} | {ts} | {e['agent']} | {e['description']} |"
            )
    print("\n".join(lines))


# ── Diff ──────────────────────────────────────────────────────────────────────

def action_diff(chapter, compare):
    versions = load_json(VER_FILE, {})
    entries = {e["version"]: e for e in versions.get(chapter, [])}

    v_a, v_b = compare.split(":")
    for v in (v_a, v_b):
        if v not in entries:
            print(f"Versão '{v}' não encontrada para '{chapter}'")
            return

    def read_file(entry):
        f = entry.get("file")
        if f and os.path.exists(f):
            with open(f, "r", encoding="utf-8") as fh:
                return fh.readlines()
        return []

    lines_a = read_file(entries[v_a])
    lines_b = read_file(entries[v_b])

    diff = list(difflib.unified_diff(
        lines_a, lines_b,
        fromfile=f"{chapter} {v_a}",
        tofile=f"{chapter} {v_b}",
        lineterm=""
    ))

    if not diff:
        print("Nenhuma diferença encontrada entre as versões.")
        return

    # Converter para Markdown com marcação visual
    md_lines = [f"## 🔀 Diff: {chapter} — {v_a} → {v_b}", "", "```diff"]
    md_lines.extend(diff[:200])  # limitar para não explodir contexto
    md_lines.append("```")
    print("\n".join(md_lines))


# ── Rollback ──────────────────────────────────────────────────────────────────

def action_rollback(chapter, version):
    versions = load_json(VER_FILE, {})
    entries = {e["version"]: e for e in versions.get(chapter, [])}

    if version not in entries:
        print(f"Versão '{version}' não encontrada para '{chapter}'")
        return

    entry = entries[version]
    f = entry.get("file")
    if f and os.path.exists(f):
        # Copiar de volta para o diretório de trabalho
        dest = f"{chapter.replace(' ', '_')}.md"
        shutil.copy2(f, dest)
        print(f"✅ Rollback concluído: '{chapter}' restaurado para {version}")
        print(f"   Arquivo restaurado: {dest}")
        print(f"   Data da versão: {entry['timestamp'][:16]}")
        print(f"   Agente original: {entry['agent']}")
    else:
        print(f"⚠️ Arquivo da versão {version} não encontrado. Apenas metadados disponíveis.")
        print(json.dumps(entry, ensure_ascii=False, indent=2))


# ── State ─────────────────────────────────────────────────────────────────────

def action_state():
    state = load_json(STATE_FILE, {})
    versions = load_json(VER_FILE, {})
    scores_file = os.path.join(DATA_DIR, "scores.json")
    scores = load_json(scores_file, {})

    title = state.get("title", "[Título não definido]")
    stage = state.get("current_stage", "—")
    version = state.get("current_version", "—")

    lines = [
        f"## 📋 ESTADO DO PROJETO — {title}",
        "",
        f"**Versão atual**: {version}",
        f"**Última atualização**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Estágio atual**: {stage}",
        "",
        "---",
        "",
        "### Sumário de Progresso",
        "",
        "| Capítulo | Status | S1 | S2 | S3 | S4 | S5 | Score | Versão |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for chapter, score_data in scores.items():
        s = score_data.get("scores", {})
        final = score_data.get("final", "—")
        approved = score_data.get("approved", False)
        status = "✅ Completo" if approved else "🔶 Em revisão"
        ver = score_data.get("version", "—")
        lines.append(
            f"| {chapter} | {status} | {s.get('S1','—')} | {s.get('S2','—')} | "
            f"{s.get('S3','—')} | {s.get('S4','—')} | {s.get('S5','—')} | "
            f"**{final}** | {ver} |"
        )

    # Histórico resumido
    lines += ["", "---", "", "### Histórico Recente",
              "", "| Capítulo | Versão | Agente | Descrição |", "|---|---|---|---|"]
    all_entries = []
    for chapter, entries in versions.items():
        for e in entries:
            all_entries.append((chapter, e))
    all_entries.sort(key=lambda x: x[1]["timestamp"], reverse=True)
    for chapter, e in all_entries[:10]:
        lines.append(f"| {chapter} | {e['version']} | {e['agent']} | {e['description']} |")

    print("\n".join(lines))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Versioner da Editora Ebook")
    parser.add_argument("--action", required=True,
                        choices=["save", "history", "diff", "rollback", "state"])
    parser.add_argument("--chapter")
    parser.add_argument("--version")
    parser.add_argument("--agent", default="LLM")
    parser.add_argument("--description", default="")
    parser.add_argument("--file")
    parser.add_argument("--compare", help="Ex: v1.1:v1.2")
    args = parser.parse_args()

    if args.action == "save":
        action_save(args.chapter, args.version, args.agent,
                    args.description, args.file)
    elif args.action == "history":
        action_history()
    elif args.action == "diff":
        action_diff(args.chapter, args.compare)
    elif args.action == "rollback":
        action_rollback(args.chapter, args.version)
    elif args.action == "state":
        action_state()


if __name__ == "__main__":
    main()

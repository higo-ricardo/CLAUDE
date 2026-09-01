#!/usr/bin/env python3
"""
publisher.py — Geração determinística de metadados e checklist de publicação.

Uso:
  python publisher.py --action metadata --project project.json
  python publisher.py --action checklist --project project.json
"""

import argparse
import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")


def load_project(path):
    if not os.path.exists(path):
        print(f"Arquivo não encontrado: {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Metadados ─────────────────────────────────────────────────────────────────

def action_metadata(project):
    p = project
    yaml_lines = [
        "# Metadados para publicação — gerado automaticamente",
        f"# {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f'titulo: "{p.get("title", "")}"',
        f'subtitulo: "{p.get("subtitle", "")}"',
        f'autor: "{p.get("author", "")}"',
        f'genero_principal: "{p.get("genre", "")}"',
        f'subgenero: "{p.get("subgenre", "")}"',
        "palavras_chave:",
    ]
    for kw in p.get("keywords", [])[:10]:
        yaml_lines.append(f'  - "{kw}"')

    yaml_lines += [
        f'idioma: "{p.get("language", "Português (Brasil)")}"',
        f'paginas_estimadas: {p.get("estimated_pages", "?")}',
        f'publico_alvo: "{p.get("target_audience", "")}"',
        f'nivel_linguagem: "{p.get("language_level", "")}"',
        f'classificacao_indicativa: "{p.get("rating", "Livre")}"',
        f'canal_publicacao: "{p.get("publish_channel", "")}"',
        f'formato_saida: "{p.get("output_format", "")}"',
        'isbn: "pendente"',
    ]

    # KDP específico
    if "kdp" in str(p.get("publish_channel", "")).lower():
        yaml_lines += [
            "",
            "# Amazon KDP",
            f'kdp_categoria_1: "{p.get("kdp_category_1", "")}"',
            f'kdp_categoria_2: "{p.get("kdp_category_2", "")}"',
            "kdp_keywords:",
        ]
        for kw in p.get("keywords", [])[:7]:
            yaml_lines.append(f'  - "{kw}"')

    print("\n".join(yaml_lines))


# ── Checklist ─────────────────────────────────────────────────────────────────

CHECKLIST_ITEMS = [
    ("blurb_short",      "Blurb curto (100 palavras) revisado"),
    ("blurb_long",       "Blurb longo (250 palavras) revisado"),
    ("metadata_complete","Metadados completos (título, autor, gênero, keywords)"),
    ("keywords_researched","Palavras-chave pesquisadas (volume de busca)"),
    ("sales_page",       "Página de vendas redigida"),
    ("cover_ready",      "Capa criada ou prompt gerado"),
    ("correct_format",   "Formato de arquivo correto para a plataforma"),
    ("isbn",             "ISBN obtido (se necessário)"),
    ("copyright_page",   "Direitos autorais e copyright na página de rosto"),
    ("author_contact",   "Informações de contato / redes sociais do autor"),
    ("final_cta",        "Chamada para ação final dentro do ebook"),
    ("toc_links",        "Sumário com links navegáveis (EPUB) ou numerado (PDF)"),
    ("author_bio",       "Seção 'Sobre o Autor' presente"),
    ("conclusion",       "Conclusão presente e revisada"),
    ("references",       "Referências bibliográficas (se houver)"),
]


def action_checklist(project):
    completed = project.get("checklist", {})
    lines = [
        "## ✅ Checklist Pré-Publicação",
        f"Projeto: **{project.get('title', '—')}**",
        f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| Status | Item |",
        "|---|---|",
    ]

    done = 0
    for key, label in CHECKLIST_ITEMS:
        status = "✅" if completed.get(key) else "❌"
        if completed.get(key):
            done += 1
        lines.append(f"| {status} | {label} |")

    pct = round((done / len(CHECKLIST_ITEMS)) * 100)
    lines += [
        "",
        f"**Concluído**: {done}/{len(CHECKLIST_ITEMS)} ({pct}%)",
        "",
        "Para marcar um item como concluído, adicione a chave em `checklist` no `project.json`.",
    ]
    print("\n".join(lines))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Publisher da Editora Ebook")
    parser.add_argument("--action", required=True, choices=["metadata", "checklist"])
    parser.add_argument("--project",
                        default=os.path.join(DATA_DIR, "project.json"))
    args = parser.parse_args()

    project = load_project(args.project)
    if not project:
        return

    if args.action == "metadata":
        action_metadata(project)
    elif args.action == "checklist":
        action_checklist(project)


if __name__ == "__main__":
    main()

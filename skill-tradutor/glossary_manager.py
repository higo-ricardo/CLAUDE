#!/usr/bin/env python3
"""
glossary_manager.py
===================
Gerencia o glossário terminológico do projeto de tradução.

Responsabilidades:
  - Lookup rápido de termos (en → pt)
  - Adicionar novas entradas com metadados
  - Detectar conflitos (mesmo en, pt diferente)
  - Resolver conflitos com aprovação do usuário
  - Auditar texto traduzido em busca de termos faltantes
  - Exportar glossário em Markdown ou XML
  - Versionar entradas alteradas

Uso:
  python glossary_manager.py lookup      --en "render"
  python glossary_manager.py add         --en "render" --pt "renderizar" --context "verbo técnico" --chapter "cap1" --reason "termo de arte da área"
  python glossary_manager.py conflict    --en "render" --pt "processar"
  python glossary_manager.py resolve     --en "render" --pt "renderizar" --approved-by user
  python glossary_manager.py audit       --text-file capitulo3.txt
  python glossary_manager.py list        [--status confirmed|pending|conflict]
  python glossary_manager.py export      [--format md|xml|json]
  python glossary_manager.py import-csv  --file glossario.csv
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

STATE_FILENAME = "session_state.xml"

# Substantivos / adjetivos comuns de alta frequência que NÃO devem ser
# registrados automaticamente no glossário
STOP_WORDS_EN = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "that",
    "this", "these", "those", "it", "he", "she", "they", "we", "you", "i",
    "my", "your", "his", "her", "their", "our", "its", "not", "no", "any",
    "all", "one", "two", "three", "first", "last", "said", "go", "went",
    "come", "came", "get", "got", "make", "made", "take", "took", "see",
    "saw", "know", "knew", "think", "thought", "look", "looked", "like",
    "just", "back", "then", "than", "more", "very", "so", "up", "out",
    "about", "what", "when", "where", "who", "how", "which", "there",
    "their", "if", "into", "also", "him", "her", "us", "them", "after",
    "before", "over", "under", "between", "through", "well", "still",
    "only", "even", "same", "another", "each", "other", "new", "old",
    "good", "great", "little", "own", "right", "too", "now", "down",
    "never", "always", "again", "away", "around", "every", "both",
}

# ---------------------------------------------------------------------------
# Helpers XML / State
# ---------------------------------------------------------------------------

def _pretty_xml(root: ET.Element) -> str:
    raw = ET.tostring(root, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ", encoding=None)


def _load_root(project_dir: Path) -> ET.Element:
    path = project_dir / STATE_FILENAME
    if not path.exists():
        raise FileNotFoundError(
            f"SESSION_STATE não encontrado em {path}.\n"
            f"Execute: python state_manager.py init --project-dir {project_dir}"
        )
    return ET.parse(path).getroot()


def _save_root(root: ET.Element, project_dir: Path) -> None:
    path = project_dir / STATE_FILENAME
    path.write_text(_pretty_xml(root), encoding="utf-8")


def _get_glossary_el(root: ET.Element) -> ET.Element:
    gl = root.find("glossary")
    if gl is None:
        gl = ET.SubElement(root, "glossary", version="1")
    return gl


def _glossary_dict(root: ET.Element) -> dict:
    """Retorna dict {en_lower: entry_element} para lookup O(1)."""
    gl = root.find("glossary") if root.find("glossary") is not None else []
    return {entry.get("en", "").lower(): entry for entry in gl}

# ---------------------------------------------------------------------------
# Funções de negócio
# ---------------------------------------------------------------------------

def lookup(root: ET.Element, en_term: str) -> ET.Element | None:
    """Busca termo por chave `en` (case-insensitive)."""
    key = en_term.strip().lower()
    return _glossary_dict(root).get(key)


def add_entry(root: ET.Element, en: str, pt: str, context: str,
              chapter: str, reason: str,
              status: str = "confirmed",
              approved_by: str = "model") -> tuple[ET.Element, bool]:
    """
    Adiciona entrada ao glossário.
    Retorna (entry_element, is_new).
    Se o termo já existe com mesmo pt: retorna existente sem duplicar.
    Se existe com pt diferente: marca como conflito (não substitui).
    """
    gl = _get_glossary_el(root)
    key = en.strip().lower()
    existing = _glossary_dict(root).get(key)

    if existing is not None:
        existing_pt = existing.get("pt", "")
        if existing_pt.lower() == pt.strip().lower():
            return existing, False  # já existe igual, sem mudança
        else:
            # Conflito detectado — não substituir
            existing.set("status", "conflict")
            existing.set("conflict_candidate", pt.strip())
            existing.set("conflict_detected_at", chapter)
            return existing, False

    # Nova entrada
    version = str(len(list(gl)) + 1)
    entry = ET.SubElement(gl, "entry")
    entry.set("en", en.strip())
    entry.set("pt", pt.strip())
    entry.set("context", context.strip())
    entry.set("chapter", chapter.strip())
    entry.set("decision_reason", reason.strip())
    entry.set("status", status)
    entry.set("approved_by", approved_by)
    entry.set("version", "1")
    entry.set("added_at", datetime.now().isoformat(timespec="seconds"))
    return entry, True


def detect_conflict(root: ET.Element, en: str, new_pt: str) -> dict | None:
    """
    Verifica se `en` já existe com `pt` diferente de `new_pt`.
    Retorna dict com detalhes do conflito ou None se não há conflito.
    """
    existing = lookup(root, en)
    if existing is None:
        return None
    existing_pt = existing.get("pt", "")
    if existing_pt.lower() == new_pt.strip().lower():
        return None
    return {
        "en": en,
        "existing_pt": existing_pt,
        "new_pt": new_pt.strip(),
        "chapter_original": existing.get("chapter", "?"),
        "status": existing.get("status", "?"),
    }


def resolve_conflict(root: ET.Element, en: str, chosen_pt: str,
                     approved_by: str = "user") -> tuple[bool, list[str]]:
    """
    Resolve conflito adotando `chosen_pt` como tradução canônica.
    Retorna (success, affected_notes).
    """
    existing = lookup(root, en)
    if existing is None:
        return False, [f"Termo '{en}' não encontrado no glossário."]

    old_pt = existing.get("pt", "")
    old_version = int(existing.get("version", "1"))

    existing.set("pt", chosen_pt.strip())
    existing.set("status", "confirmed")
    existing.set("approved_by", approved_by)
    existing.set("version", str(old_version + 1))
    existing.set("resolved_at", datetime.now().isoformat(timespec="seconds"))
    # Limpar atributos de conflito
    for attr in ["conflict_candidate", "conflict_detected_at"]:
        if attr in existing.attrib:
            del existing.attrib[attr]

    notes = []
    if old_pt != chosen_pt:
        notes.append(
            f"ATENÇÃO: '{en}' era traduzido como '{old_pt}'. "
            f"Adotado '{chosen_pt}'. Revisar ocorrências anteriores no texto."
        )
    return True, notes


def audit_text(root: ET.Element, text: str,
               min_word_len: int = 4) -> dict:
    """
    Analisa um texto traduzido em busca de:
    1. Termos do glossário que aparecem no texto (verificação de uso)
    2. Possíveis termos não registrados (palavras de conteúdo sem entrada)

    Retorna dict com resultados.
    """
    gl_dict = _glossary_dict(root)
    words_in_text = set(
        w.strip(".,;:!?\"'()[]{}").lower()
        for w in text.split()
        if len(w) >= min_word_len
    )

    # Termos do glossário encontrados no texto original (só faz sentido se texto for EN)
    found_in_glossary = {en: gl_dict[en].get("pt") for en in gl_dict if en in words_in_text}

    # Palavras do texto não registradas (filtrar stop words)
    potential_missing = sorted(
        w for w in words_in_text
        if w not in gl_dict and w not in STOP_WORDS_EN and w.isalpha()
    )

    return {
        "total_glossary_entries": len(gl_dict),
        "glossary_terms_found_in_text": found_in_glossary,
        "potential_missing_terms": potential_missing[:50],  # Top 50
        "conflicts_open": [
            {"en": e.get("en"), "pt": e.get("pt"), "candidate": e.get("conflict_candidate")}
            for e in (root.find("glossary") if root.find("glossary") is not None else [])
            if e.get("status") == "conflict"
        ],
    }


def bump_version(root: ET.Element, en: str) -> bool:
    """Incrementa o número de versão de uma entrada."""
    existing = lookup(root, en)
    if existing is None:
        return False
    v = int(existing.get("version", "1"))
    existing.set("version", str(v + 1))
    return True

# ---------------------------------------------------------------------------
# Formatação de saída
# ---------------------------------------------------------------------------

def format_entry_md(entry: ET.Element) -> str:
    status_icon = {"confirmed": "✅", "pending": "🔲", "conflict": "⚠️"}.get(
        entry.get("status", ""), "❓"
    )
    conflict_note = ""
    if entry.get("status") == "conflict":
        conflict_note = f" | ⚠️ Candidato: **{entry.get('conflict_candidate', '?')}**"
    return (
        f"| {status_icon} | `{entry.get('en')}` | {entry.get('pt')} "
        f"| {entry.get('context', '—')} | {entry.get('chapter', '—')} "
        f"| v{entry.get('version', '1')}{conflict_note} |"
    )


def format_conflict_alert(conflict: dict) -> str:
    return (
        f"\n⚠️ CONFLITO DE GLOSSÁRIO DETECTADO\n"
        f"{'─'*50}\n"
        f"Termo:              {conflict['en']}\n"
        f"Registro existente: \"{conflict['existing_pt']}\" "
        f"(cap. {conflict['chapter_original']})\n"
        f"Nova ocorrência:    \"{conflict['new_pt']}\"\n\n"
        f"Opções:\n"
        f"  A) Manter \"{conflict['existing_pt']}\" em todo o livro\n"
        f"  B) Adotar \"{conflict['new_pt']}\" em todo o livro\n"
        f"  C) Manter ambos com contextos distintos\n\n"
        f"⏸️  Tradução pausada. Execute:\n"
        f"  python glossary_manager.py resolve "
        f"--en \"{conflict['en']}\" --pt \"<escolha>\" --approved-by user\n"
    )


def export_markdown(root: ET.Element, status_filter: str | None = None) -> str:
    gl = root.find("glossary") if root.find("glossary") is not None else []
    entries = list(gl)
    if status_filter:
        entries = [e for e in entries if e.get("status") == status_filter]

    if not entries:
        return "*(Glossário vazio)*"

    lines = [
        f"## Glossário do Projeto — {len(entries)} entradas\n",
        "| Status | EN | PT | Contexto | Capítulo | Versão |",
        "|--------|----|----|----------|----------|--------|",
    ]
    lines += [format_entry_md(e) for e in entries]
    return "\n".join(lines)


def export_json(root: ET.Element) -> str:
    gl = root.find("glossary") if root.find("glossary") is not None else []
    data = [dict(e.attrib) for e in gl]
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_xml_block(root: ET.Element) -> str:
    gl = _get_glossary_el(root)
    raw = ET.tostring(gl, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ", encoding=None)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_lookup(args):
    root = _load_root(Path(args.project_dir))
    entry = lookup(root, args.en)
    if entry is None:
        print(f"[NÃO ENCONTRADO] '{args.en}' não está no glossário.")
        sys.exit(1)
    print(f"\n  EN:      {entry.get('en')}")
    print(f"  PT:      {entry.get('pt')}")
    print(f"  Status:  {entry.get('status')}")
    print(f"  Contexto:{entry.get('context')}")
    print(f"  Capítulo:{entry.get('chapter')}")
    print(f"  Motivo:  {entry.get('decision_reason')}")
    print(f"  Versão:  {entry.get('version')}\n")


def cmd_add(args):
    root = _load_root(Path(args.project_dir))

    # Verificar conflito antes de adicionar
    conflict = detect_conflict(root, args.en, args.pt)
    if conflict:
        print(format_conflict_alert(conflict))
        sys.exit(2)  # exit 2 = conflito (não erro)

    entry, is_new = add_entry(
        root, args.en, args.pt, args.context,
        args.chapter, args.reason,
        status=args.status, approved_by=args.approved_by,
    )
    _save_root(root, Path(args.project_dir))

    if is_new:
        print(f"[OK] Entrada adicionada: '{args.en}' → '{args.pt}'")
    else:
        print(f"[SKIP] '{args.en}' já existe com mesmo valor.")


def cmd_conflict(args):
    root = _load_root(Path(args.project_dir))
    conflict = detect_conflict(root, args.en, args.pt)
    if conflict is None:
        print(f"[OK] Sem conflito para '{args.en}'.")
    else:
        print(format_conflict_alert(conflict))
        # Marcar no estado
        entry = lookup(root, args.en)
        if entry is not None:
            entry.set("status", "conflict")
            entry.set("conflict_candidate", args.pt)
            _save_root(root, Path(args.project_dir))
        sys.exit(2)


def cmd_resolve(args):
    root = _load_root(Path(args.project_dir))
    ok, notes = resolve_conflict(root, args.en, args.pt, args.approved_by)
    if ok:
        _save_root(root, Path(args.project_dir))
        print(f"[OK] Conflito resolvido: '{args.en}' → '{args.pt}'")
        for note in notes:
            print(f"  ℹ️  {note}")
    else:
        for note in notes:
            print(f"[ERRO] {note}")
        sys.exit(1)


def cmd_audit(args):
    root = _load_root(Path(args.project_dir))
    text_path = Path(args.text_file)
    if not text_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {text_path}")
        sys.exit(1)
    text = text_path.read_text(encoding="utf-8")
    result = audit_text(root, text)

    print(f"\n{'='*60}")
    print("  AUDITORIA DE GLOSSÁRIO")
    print(f"{'='*60}")
    print(f"  Total de entradas no glossário: {result['total_glossary_entries']}")
    print(f"  Termos do glossário no texto:   {len(result['glossary_terms_found_in_text'])}")
    print(f"  Conflitos abertos:              {len(result['conflicts_open'])}")
    print(f"  Possíveis termos sem entrada:   {len(result['potential_missing_terms'])}")

    if result["conflicts_open"]:
        print("\n⚠️  CONFLITOS ABERTOS:")
        for c in result["conflicts_open"]:
            print(f"    {c['en']} → '{c['pt']}' | candidato: '{c['candidate']}'")

    if result["potential_missing_terms"]:
        print("\n🔲 TOP 20 POSSÍVEIS TERMOS SEM ENTRADA:")
        for w in result["potential_missing_terms"][:20]:
            print(f"    {w}")
    print()


def cmd_list(args):
    root = _load_root(Path(args.project_dir))
    print(export_markdown(root, status_filter=args.status))


def cmd_export(args):
    root = _load_root(Path(args.project_dir))
    fmt = args.format or "md"
    if fmt == "md":
        out = export_markdown(root)
    elif fmt == "json":
        out = export_json(root)
    elif fmt == "xml":
        out = export_xml_block(root)
    else:
        print(f"[ERRO] Formato desconhecido: {fmt}")
        sys.exit(1)
    print(out)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"\n[OK] Exportado para: {args.out}")


def cmd_import_csv(args):
    root = _load_root(Path(args.project_dir))
    path = Path(args.file)
    if not path.exists():
        print(f"[ERRO] CSV não encontrado: {path}")
        sys.exit(1)

    added = skipped = conflicts = 0
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            en = row.get("en", "").strip()
            pt = row.get("pt", "").strip()
            if not en or not pt:
                skipped += 1
                continue
            conflict = detect_conflict(root, en, pt)
            if conflict:
                print(f"  ⚠️  Conflito: {en} → '{pt}' vs '{conflict['existing_pt']}'")
                conflicts += 1
                continue
            _, is_new = add_entry(
                root, en, pt,
                context=row.get("context", "importado"),
                chapter=row.get("chapter", "?"),
                reason=row.get("reason", "importado via CSV"),
                status=row.get("status", "confirmed"),
                approved_by=row.get("approved_by", "user"),
            )
            if is_new:
                added += 1
            else:
                skipped += 1

    _save_root(root, Path(args.project_dir))
    print(f"[OK] Importação concluída: {added} adicionados | "
          f"{skipped} ignorados | {conflicts} conflitos")


def main():
    parser = argparse.ArgumentParser(
        description="Glossário terminológico — skill tradutor-livros",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--project-dir", "-p", default="./translation_project")

    sub = parser.add_subparsers(dest="command", required=True)

    # lookup
    p = sub.add_parser("lookup", help="Buscar termo EN no glossário")
    p.add_argument("--en", required=True)
    p.set_defaults(func=cmd_lookup)

    # add
    p = sub.add_parser("add", help="Adicionar entrada ao glossário")
    p.add_argument("--en", required=True)
    p.add_argument("--pt", required=True)
    p.add_argument("--context", default="")
    p.add_argument("--chapter", default="?")
    p.add_argument("--reason", default="")
    p.add_argument("--status", default="confirmed",
                   choices=["confirmed", "pending", "conflict"])
    p.add_argument("--approved-by", default="model",
                   choices=["model", "user"])
    p.set_defaults(func=cmd_add)

    # conflict
    p = sub.add_parser("conflict", help="Verificar conflito para um termo")
    p.add_argument("--en", required=True)
    p.add_argument("--pt", required=True)
    p.set_defaults(func=cmd_conflict)

    # resolve
    p = sub.add_parser("resolve", help="Resolver conflito de glossário")
    p.add_argument("--en", required=True)
    p.add_argument("--pt", required=True, help="Tradução canônica escolhida")
    p.add_argument("--approved-by", default="user",
                   choices=["model", "user"])
    p.set_defaults(func=cmd_resolve)

    # audit
    p = sub.add_parser("audit", help="Auditar texto em busca de termos faltantes")
    p.add_argument("--text-file", required=True)
    p.set_defaults(func=cmd_audit)

    # list
    p = sub.add_parser("list", help="Listar entradas do glossário")
    p.add_argument("--status", choices=["confirmed", "pending", "conflict"],
                   help="Filtrar por status")
    p.set_defaults(func=cmd_list)

    # export
    p = sub.add_parser("export", help="Exportar glossário")
    p.add_argument("--format", choices=["md", "json", "xml"], default="md")
    p.add_argument("--out", help="Arquivo de saída (opcional)")
    p.set_defaults(func=cmd_export)

    # import-csv
    p = sub.add_parser("import-csv", help="Importar glossário de arquivo CSV")
    p.add_argument("--file", required=True)
    p.set_defaults(func=cmd_import_csv)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

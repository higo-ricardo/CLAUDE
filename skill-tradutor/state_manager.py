#!/usr/bin/env python3
"""
state_manager.py
================
Gerencia o ciclo de vida do SESSION_STATE da skill tradutor-livros.

Responsabilidades:
  - Inicializar novo estado de projeto
  - Carregar / salvar estado em XML
  - Validar campos obrigatórios
  - Calcular hash de integridade entre sessões
  - Exportar bloco colapsável Markdown para o LLM injetar na conversa
  - Atualizar campos individuais sem reescrever o arquivo inteiro

Uso:
  python state_manager.py init   --project-dir ./meu_livro
  python state_manager.py load   --project-dir ./meu_livro
  python state_manager.py validate
  python state_manager.py update --field progress.current_chapter --value "Capítulo 3"
  python state_manager.py hash
  python state_manager.py export
  python state_manager.py status
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

STATE_FILENAME = "session_state.xml"
VERSION = "1.0"

# Campos que BLOQUEIAM execução se ausentes (mapeados como xpath simples)
BLOCKING_FIELDS = {
    "project/title_original": "Título original",
    "project/author":         "Autor",
    "project/genre":          "Gênero",
    "project/register":       "Registro/tom",
    "project/treatment":      "Tratamento (você/tu)",
}

# Campos com fallback automático (não bloqueantes)
DEFAULT_FIELDS = {
    "project/language_pair":  "EN → PT-BR",
    "project/target_audience": "adulto geral",
    "project/delivery_mode":  "livre",
    "progress/words_translated": "0",
}

# ---------------------------------------------------------------------------
# Helpers XML
# ---------------------------------------------------------------------------

def _pretty_xml(root: ET.Element) -> str:
    """Serializa ElementTree com indentação legível."""
    raw = ET.tostring(root, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ", encoding=None)


def _get_or_create(parent: ET.Element, tag: str) -> ET.Element:
    el = parent.find(tag)
    if el is None:
        el = ET.SubElement(parent, tag)
    return el


def _set_nested(root: ET.Element, dotpath: str, value: str) -> None:
    """Define root/a/b/c = value criando nós intermediários se necessário."""
    parts = dotpath.split("/")
    node = root
    for part in parts[:-1]:
        node = _get_or_create(node, part)
    leaf = _get_or_create(node, parts[-1])
    leaf.text = value

# ---------------------------------------------------------------------------
# Funções principais
# ---------------------------------------------------------------------------

def state_path(project_dir: Path) -> Path:
    return project_dir / STATE_FILENAME


def load_state(project_dir: Path) -> ET.Element:
    """Carrega SESSION_STATE. Levanta FileNotFoundError se inexistente."""
    path = state_path(project_dir)
    if not path.exists():
        raise FileNotFoundError(
            f"SESSION_STATE não encontrado em: {path}\n"
            f"Execute: python state_manager.py init --project-dir {project_dir}"
        )
    tree = ET.parse(path)
    return tree.getroot()


def save_state(root: ET.Element, project_dir: Path) -> None:
    """Salva SESSION_STATE com backup automático."""
    path = state_path(project_dir)
    # backup do anterior
    if path.exists():
        backup = project_dir / f"session_state.backup_{datetime.now():%Y%m%d_%H%M%S}.xml"
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    path.write_text(_pretty_xml(root), encoding="utf-8")


def build_empty_state() -> ET.Element:
    """Cria o template XML vazio do SESSION_STATE."""
    root = ET.Element("session_state", version=VERSION)

    project = ET.SubElement(root, "project")
    for tag in ["title_original", "title_pt", "author", "genre",
                "language_pair", "target_audience", "register",
                "treatment", "delivery_mode"]:
        ET.SubElement(project, tag).text = ""

    progress = ET.SubElement(root, "progress")
    for tag, val in [("total_chapters", "?"), ("current_chapter", ""),
                     ("current_chunk_id", ""), ("words_translated", "0"),
                     ("last_paragraph_id", "")]:
        ET.SubElement(progress, tag).text = val

    ET.SubElement(root, "glossary", version="1")
    style = ET.SubElement(root, "style_sheet")
    for tag in ["pov", "sentence_rhythm", "vocabulary_level", "tone",
                "humor", "narrator_reliable"]:
        ET.SubElement(style, tag).text = ""

    ET.SubElement(root, "decisions")
    ET.SubElement(root, "pending")
    return root


def validate_state(root: ET.Element) -> tuple[bool, list[str]]:
    """
    Valida campos obrigatórios e aplica defaults.
    Retorna (is_valid, list_of_errors).
    """
    errors = []
    for xpath, label in BLOCKING_FIELDS.items():
        node = root.find(xpath)
        if node is None or not (node.text or "").strip():
            errors.append(f"[BLOQUEANTE] Campo ausente: {label} ({xpath})")

    # Aplicar defaults silenciosamente
    for xpath, default in DEFAULT_FIELDS.items():
        node = root.find(xpath)
        if node is None or not (node.text or "").strip():
            _set_nested(root, xpath, default)

    return (len(errors) == 0), errors


def compute_hash(root: ET.Element) -> str:
    """SHA-256 do glossário + decisões para verificação de integridade entre sessões."""
    glossary = root.find("glossary")
    decisions = root.find("decisions")

    data = {
        "glossary": [
            {k: entry.get(k, "") for k in ["en", "pt", "version", "status"]}
            for entry in (glossary if glossary is not None else [])
        ],
        "decisions": [
            {k: d.get(k, "") for k in ["id", "en", "pt", "approved_by"]}
            for d in (decisions if decisions is not None else [])
        ],
    }
    payload = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def export_markdown(root: ET.Element) -> str:
    """Gera bloco colapsável Markdown para colar na conversa com o LLM."""
    xml_text = _pretty_xml(root)
    h = compute_hash(root)
    proj = root.find("project")
    title = (proj.findtext("title_original") or "sem título") if proj else "sem título"
    chapter = root.findtext("progress/current_chapter") or "—"
    words = root.findtext("progress/words_translated") or "0"
    pending = len(list(root.findall("pending/item")))
    conflicts = sum(
        1 for e in root.findall("glossary/entry")
        if e.get("status") == "conflict"
    )

    lines = [
        "<details>",
        f"<summary>📦 Estado da sessão — {title} | Cap.: {chapter} | "
        f"Palavras: {words} | Pendências: {pending} | Conflitos: {conflicts} | "
        f"Hash: {h[:12]}...</summary>",
        "",
        "```xml",
        xml_text.strip(),
        "```",
        "",
        "</details>",
    ]
    return "\n".join(lines)


def print_status(root: ET.Element) -> None:
    """Imprime resumo legível do estado atual."""
    proj = root.find("project")
    prog = root.find("progress")
    glossary = root.find("glossary")
    pending = root.find("pending")
    decisions = root.find("decisions")

    print("\n" + "="*60)
    print("  SESSION_STATE — STATUS")
    print("="*60)

    if proj is not None:
        print(f"  Título:    {proj.findtext('title_original') or '—'}")
        print(f"  Autor:     {proj.findtext('author') or '—'}")
        print(f"  Gênero:    {proj.findtext('genre') or '—'}")
        print(f"  Registro:  {proj.findtext('register') or '—'}")
        print(f"  Tratamento:{proj.findtext('treatment') or '—'}")
        print(f"  Modo:      {proj.findtext('delivery_mode') or '—'}")

    print()
    if prog is not None:
        print(f"  Capítulo atual:  {prog.findtext('current_chapter') or '—'}")
        print(f"  Chunk atual:     {prog.findtext('current_chunk_id') or '—'}")
        print(f"  Palavras trad.:  {prog.findtext('words_translated') or '0'}")

    n_glossary  = len(list(glossary or []))
    n_confirmed = sum(1 for e in (glossary or []) if e.get("status") == "confirmed")
    n_conflict  = sum(1 for e in (glossary or []) if e.get("status") == "conflict")
    n_pending   = len(list((pending or [])))
    n_decisions = len(list((decisions or [])))

    print()
    print(f"  Glossário:   {n_glossary} entradas "
          f"({n_confirmed} confirmadas, {n_conflict} com conflito)")
    print(f"  Decisões:    {n_decisions}")
    print(f"  Pendências:  {n_pending}")
    print(f"  Hash:        {compute_hash(root)[:16]}...")
    print("="*60 + "\n")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_init(args):
    project_dir = Path(args.project_dir)
    project_dir.mkdir(parents=True, exist_ok=True)
    path = state_path(project_dir)

    if path.exists() and not args.force:
        print(f"[AVISO] SESSION_STATE já existe em {path}.")
        print("Use --force para reinicializar (apaga o estado atual).")
        sys.exit(1)

    root = build_empty_state()

    # Preencher com valores passados via --set key=value
    if args.set:
        for kv in args.set:
            if "=" not in kv:
                print(f"[ERRO] Formato inválido: '{kv}'. Use campo/sub=valor")
                sys.exit(1)
            key, _, val = kv.partition("=")
            _set_nested(root, key.strip(), val.strip())

    save_state(root, project_dir)
    print(f"[OK] SESSION_STATE inicializado em: {path}")
    print_status(root)


def cmd_load(args):
    project_dir = Path(args.project_dir)
    root = load_state(project_dir)
    print_status(root)


def cmd_validate(args):
    project_dir = Path(args.project_dir)
    root = load_state(project_dir)
    valid, errors = validate_state(root)
    if valid:
        print("[OK] SESSION_STATE válido. Todos os campos obrigatórios presentes.")
    else:
        print("[FALHA] Validação encontrou problemas:\n")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    # Salvar com defaults aplicados
    save_state(root, project_dir)


def cmd_update(args):
    project_dir = Path(args.project_dir)
    root = load_state(project_dir)
    _set_nested(root, args.field, args.value)
    save_state(root, project_dir)
    print(f"[OK] {args.field} = {args.value!r}")


def cmd_hash(args):
    project_dir = Path(args.project_dir)
    root = load_state(project_dir)
    h = compute_hash(root)
    print(f"Hash SHA-256: {h}")
    print(f"Resumo:       {h[:16]}...")


def cmd_export(args):
    project_dir = Path(args.project_dir)
    root = load_state(project_dir)
    md = export_markdown(root)
    print(md)
    if args.out:
        Path(args.out).write_text(md, encoding="utf-8")
        print(f"\n[OK] Exportado para: {args.out}")


def cmd_status(args):
    project_dir = Path(args.project_dir)
    root = load_state(project_dir)
    print_status(root)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Gerenciador de SESSION_STATE — skill tradutor-livros",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--project-dir", "-p", default="./translation_project",
        help="Diretório do projeto (default: ./translation_project)"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = sub.add_parser("init", help="Inicializar novo SESSION_STATE")
    p_init.add_argument("--force", action="store_true",
                        help="Reinicializar mesmo se já existir")
    p_init.add_argument("--set", action="append", metavar="campo/sub=valor",
                        help="Preencher campos na inicialização (repetível). Ex: --set project/author=Jane")
    p_init.set_defaults(func=cmd_init)

    # load
    p_load = sub.add_parser("load", help="Carregar e exibir o estado atual")
    p_load.set_defaults(func=cmd_load)

    # validate
    p_val = sub.add_parser("validate", help="Validar campos obrigatórios")
    p_val.set_defaults(func=cmd_validate)

    # update
    p_upd = sub.add_parser("update", help="Atualizar campo específico")
    p_upd.add_argument("--field", required=True, help="Caminho do campo (ex: progress/current_chapter)")
    p_upd.add_argument("--value", required=True, help="Novo valor")
    p_upd.set_defaults(func=cmd_update)

    # hash
    p_hash = sub.add_parser("hash", help="Calcular hash de integridade")
    p_hash.set_defaults(func=cmd_hash)

    # export
    p_exp = sub.add_parser("export", help="Exportar bloco Markdown para o LLM")
    p_exp.add_argument("--out", help="Salvar em arquivo (opcional)")
    p_exp.set_defaults(func=cmd_export)

    # status
    p_st = sub.add_parser("status", help="Exibir resumo do projeto")
    p_st.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

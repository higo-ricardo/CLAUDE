#!/usr/bin/env python3
"""
chunk_manager.py
================
Divide texto longo em chunks de tradução e gerencia o progresso por chunk.

Responsabilidades:
  - Dividir texto em blocos de ~500 palavras sem quebrar parágrafos/diálogos
  - Gerar e persistir plano de chunks
  - Construir chunk_header (contexto compacto para o LLM)
  - Construir chunk_footer (pacote de estado pós-tradução)
  - Rastrear progresso e apontar próximo chunk
  - Validar continuidade entre chunks

Uso:
  python chunk_manager.py plan    --text-file livro.txt --chapter 1
  python chunk_manager.py show    --chunk-id cap1-chunk-001
  python chunk_manager.py header  --chunk-id cap1-chunk-001
  python chunk_manager.py footer  --chunk-id cap1-chunk-001 --translation-file trad.txt
  python chunk_manager.py next
  python chunk_manager.py status
  python chunk_manager.py mark-done --chunk-id cap1-chunk-001
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

STATE_FILENAME   = "session_state.xml"
PLAN_FILENAME    = "chunks/plan.json"
MAX_WORDS        = 500
ACTIVE_GLOSSARY_LIMIT = 30  # máx de entradas no chunk_header

# Padrões que NÃO devem ser cortados no meio
# (detectados por heurística de início de linha)
PROTECTED_PATTERNS = [
    re.compile(r"^\s*\|"),           # linha de tabela Markdown
    re.compile(r"^\s*[-*+]\s"),      # item de lista
    re.compile(r"^\s*\d+\.\s"),      # lista numerada
    re.compile(r"^\s*>"),            # blockquote
    re.compile(r"^\s*#{1,6}\s"),     # título Markdown
    re.compile(r'^[-—"\'«]'),        # início de diálogo
]

# ---------------------------------------------------------------------------
# Helpers
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


def _load_plan(project_dir: Path) -> list:
    path = project_dir / PLAN_FILENAME
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _save_plan(project_dir: Path, plan: list) -> None:
    path = project_dir / PLAN_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")


def _count_words(text: str) -> int:
    return len(text.split())


def _is_protected_start(line: str) -> bool:
    return any(p.match(line) for p in PROTECTED_PATTERNS)


def _is_dialog_active(paragraph: str) -> bool:
    """Heurística: parágrafo contém abertura de aspas sem fechamento."""
    # \u00ab = «  \u00bb = »  \u201c = "  \u201d = "
    open_count  = (paragraph.count('"') + paragraph.count("\u00ab")
                   + paragraph.count("\u201c"))
    close_count = (paragraph.count('"') + paragraph.count("\u00bb")
                   + paragraph.count("\u201d"))
    return open_count > close_count

# ---------------------------------------------------------------------------
# Core: segmentação de texto
# ---------------------------------------------------------------------------

def split_text_into_chunks(
    text: str,
    chapter: str,
    max_words: int = MAX_WORDS,
) -> list[dict]:
    """
    Divide texto em chunks respeitando:
    - Limite de max_words palavras
    - Não quebrar no meio de parágrafo
    - Não quebrar no meio de diálogo
    - Não quebrar no meio de tabela/lista

    Retorna lista de dicts:
    [{"chunk_id": ..., "chapter": ..., "start_word": ...,
      "end_word": ..., "word_count": ..., "text": ...,
      "first_sentence": ..., "last_sentence": ...}]
    """
    # Dividir em parágrafos (preservando blocos vazios como separadores)
    paragraphs = re.split(r'\n\n+', text.strip())
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks = []
    current_pars = []
    current_words = 0
    chunk_index = 1
    total_words = 0

    def _flush(pars: list, idx: int) -> dict:
        chunk_text = "\n\n".join(pars)
        wc = _count_words(chunk_text)
        sentences = re.split(r'(?<=[.!?])\s+', chunk_text)
        return {
            "chunk_id":       f"{chapter}-chunk-{idx:03d}",
            "chapter":        chapter,
            "word_count":     wc,
            "text":           chunk_text,
            "first_sentence": sentences[0][:120] if sentences else "",
            "last_sentence":  sentences[-1][:120] if sentences else "",
            "status":         "pending",
            "translated_at":  None,
        }

    for par in paragraphs:
        par_words = _count_words(par)
        in_dialog = _is_dialog_active("\n\n".join(current_pars))
        is_protected = _is_protected_start(par)

        should_cut = (
            current_words + par_words > max_words
            and current_pars  # não cortar no primeiro parágrafo
            and not in_dialog
            and not is_protected
        )

        if should_cut:
            chunks.append(_flush(current_pars, chunk_index))
            total_words += current_words
            chunk_index += 1
            current_pars = [par]
            current_words = par_words
        else:
            current_pars.append(par)
            current_words += par_words

    # Último chunk
    if current_pars:
        chunks.append(_flush(current_pars, chunk_index))
        total_words += current_words

    return chunks


# ---------------------------------------------------------------------------
# Header / Footer
# ---------------------------------------------------------------------------

def build_header(root: ET.Element, chunk: dict) -> str:
    """
    Constrói o chunk_header XML que o LLM recebe antes de traduzir.
    Inclui: projeto resumido, últimas 30 entradas do glossário, 3 últimas decisões,
    último parágrafo traduzido e pendências ativas.
    """
    proj    = root.find("project")
    style   = root.find("style_sheet")
    gl      = list(root.find("glossary") if root.find("glossary") is not None else [])
    decs    = list(root.find("decisions") if root.find("decisions") is not None else [])
    pending = list(root.find("pending") if root.find("pending") is not None else [])
    prog    = root.find("progress")

    # Glossário: últimas ACTIVE_GLOSSARY_LIMIT entradas
    recent_gl = gl[-ACTIVE_GLOSSARY_LIMIT:]

    header = ET.Element("chunk_header")

    ET.SubElement(header, "chunk_id").text        = chunk["chunk_id"]
    ET.SubElement(header, "words_in_chunk").text  = str(chunk["word_count"])
    ET.SubElement(header, "chapter").text         = chunk["chapter"]

    # Resumo do projeto
    ps = ET.SubElement(header, "project_summary")
    for tag in ["title_original", "genre", "register", "treatment"]:
        node = proj.find(tag) if proj is not None else None
        ET.SubElement(ps, tag).text = (node.text or "") if node is not None else ""
    for tag in ["pov", "sentence_rhythm", "tone"]:
        node = style.find(tag) if style is not None else None
        ET.SubElement(ps, tag).text = (node.text or "") if node is not None else ""

    # Glossário ativo
    agl = ET.SubElement(header, "active_glossary",
                         count=str(len(recent_gl)),
                         note=f"Últimas {ACTIVE_GLOSSARY_LIMIT} entradas. Glossário completo no chunk_footer.")
    for entry in recent_gl:
        e = ET.SubElement(agl, "entry")
        e.set("en", entry.get("en", ""))
        e.set("pt", entry.get("pt", ""))
        e.set("status", entry.get("status", "confirmed"))

    # Últimas 3 decisões
    rd = ET.SubElement(header, "recent_decisions")
    for d in decs[-3:]:
        dec = ET.SubElement(rd, "decision")
        dec.set("en",        d.get("en", ""))
        dec.set("pt",        d.get("pt", ""))
        dec.set("rationale", d.get("rationale", ""))

    # Último parágrafo traduzido (para continuidade de leitura)
    last_par = ""
    if prog is not None:
        # Tentar ler do arquivo de tradução do chunk anterior
        lp = prog.find("last_paragraph_translated")
        if lp is not None and lp.text:
            last_par = lp.text
    ET.SubElement(header, "last_paragraph").text = last_par

    # Pendências que afetam este chunk
    ap = ET.SubElement(header, "active_pending")
    for item in pending:
        pi = ET.SubElement(ap, "item")
        pi.set("id",          item.get("id", ""))
        pi.set("type",        item.get("type", ""))
        pi.set("description", item.get("description", ""))

    raw = ET.tostring(header, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ", encoding=None)


def build_footer(root: ET.Element, chunk: dict,
                 translation_text: str,
                 new_glossary_entries: list | None = None) -> str:
    """
    Constrói o chunk_footer XML que é exportado ao final de cada chunk traduzido.
    Contém o snapshot completo do estado para retomada futura.
    """
    footer = ET.Element("chunk_footer")

    ET.SubElement(footer, "chunk_id").text                   = chunk["chunk_id"]
    ET.SubElement(footer, "timestamp").text                  = datetime.now().isoformat(timespec="seconds")
    ET.SubElement(footer, "words_translated_this_chunk").text = str(chunk["word_count"])

    # Progresso
    prog_node = root.find("progress")
    total_prev = int((prog_node.findtext("words_translated") or "0")) if prog_node else 0
    total_now  = total_prev + chunk["word_count"]

    prog = ET.SubElement(footer, "progress")
    ET.SubElement(prog, "last_paragraph_id").text   = chunk["chunk_id"]
    ET.SubElement(prog, "words_translated_total").text = str(total_now)

    # Última frase traduzida
    sentences = re.split(r'(?<=[.!?])\s+', translation_text.strip())
    ET.SubElement(prog, "last_sentence").text = sentences[-1][:200] if sentences else ""

    # Primeira frase do próximo chunk (para orientar retomada)
    ET.SubElement(prog, "next_chunk_starts").text = chunk.get("first_sentence", "")[:200]

    # Snapshot completo do glossário
    gl_src = root.find("glossary"); gl_src = gl_src if gl_src is not None else ET.Element("glossary")
    gl_snap = ET.SubElement(footer, "glossary_snapshot",
                             version=gl_src.get("version", "1"))
    for entry in gl_src:
        gl_snap.append(ET.fromstring(ET.tostring(entry)))

    # Snapshot de decisões
    decs_src = root.find("decisions"); decs_src = decs_src if decs_src is not None else ET.Element("decisions")
    decs_snap = ET.SubElement(footer, "decisions_snapshot")
    for d in decs_src:
        decs_snap.append(ET.fromstring(ET.tostring(d)))

    # Snapshot de pendências
    pend_src = root.find("pending"); pend_src = pend_src if pend_src is not None else ET.Element("pending")
    pend_snap = ET.SubElement(footer, "pending_snapshot")
    for item in pend_src:
        pend_snap.append(ET.fromstring(ET.tostring(item)))

    # Ficha de estilo
    style_src = root.find("style_sheet"); style_src = style_src if style_src is not None else ET.Element("style_sheet")
    footer.append(ET.fromstring(ET.tostring(style_src)))

    raw = ET.tostring(footer, encoding="unicode")
    xml_str = minidom.parseString(raw).toprettyxml(indent="  ", encoding=None)

    # Empacotar em bloco colapsável Markdown
    lines = [
        "<details>",
        f"<summary>📦 Pacote de estado — {chunk['chunk_id']} | "
        f"Palavras totais: {total_now} | "
        f"{datetime.now():%d/%m/%Y %H:%M}</summary>",
        "",
        "```xml",
        xml_str.strip(),
        "```",
        "",
        "</details>",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _find_chunk(plan: list, chunk_id: str) -> dict | None:
    return next((c for c in plan if c["chunk_id"] == chunk_id), None)


def _next_pending(plan: list) -> dict | None:
    return next((c for c in plan if c["status"] == "pending"), None)

# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_plan(args):
    project_dir = Path(args.project_dir)
    text_path   = Path(args.text_file)
    if not text_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {text_path}")
        sys.exit(1)

    text    = text_path.read_text(encoding="utf-8")
    chapter = args.chapter or "cap1"
    max_w   = args.max_words or MAX_WORDS

    chunks = split_text_into_chunks(text, chapter, max_words=max_w)

    # Salvar arquivos de chunk
    chunks_dir = project_dir / "chunks" / chapter
    chunks_dir.mkdir(parents=True, exist_ok=True)
    for chunk in chunks:
        (chunks_dir / f"{chunk['chunk_id']}.txt").write_text(
            chunk["text"], encoding="utf-8"
        )

    # Persistir plano
    existing_plan = _load_plan(project_dir)
    chunk_ids_existing = {c["chunk_id"] for c in existing_plan}
    new_chunks = [c for c in chunks if c["chunk_id"] not in chunk_ids_existing]
    plan = existing_plan + new_chunks
    _save_plan(project_dir, plan)

    # Exibir plano
    total_words = sum(c["word_count"] for c in chunks)
    print(f"\n{'='*65}")
    print(f"  PLANO DE CHUNKS — {chapter}")
    print(f"{'='*65}")
    print(f"  Total de palavras:  {total_words}")
    print(f"  Total de chunks:    {len(chunks)}")
    print(f"  Limite por chunk:   {max_w} palavras")
    print()
    print(f"  {'Chunk ID':<22} {'Início (60 chars)':<45} {'Palavras':>8}")
    print(f"  {'-'*22} {'-'*45} {'-'*8}")
    for c in chunks:
        start = c["first_sentence"][:42] + "..." if len(c["first_sentence"]) > 42 else c["first_sentence"]
        print(f"  {c['chunk_id']:<22} {start:<45} {c['word_count']:>8}")
    print(f"{'='*65}\n")
    print(f"[OK] Plano salvo. Próximo: python chunk_manager.py next "
          f"--project-dir {project_dir}")


def cmd_show(args):
    project_dir = Path(args.project_dir)
    plan = _load_plan(project_dir)
    chunk = _find_chunk(plan, args.chunk_id)
    if chunk is None:
        print(f"[ERRO] chunk_id '{args.chunk_id}' não encontrado no plano.")
        sys.exit(1)

    print(f"\n--- {chunk['chunk_id']} ({chunk['word_count']} palavras) ---\n")
    print(chunk["text"])
    print(f"\n--- fim do chunk ---\n")


def cmd_header(args):
    project_dir = Path(args.project_dir)
    root  = _load_root(project_dir)
    plan  = _load_plan(project_dir)
    chunk = _find_chunk(plan, args.chunk_id)
    if chunk is None:
        print(f"[ERRO] chunk_id '{args.chunk_id}' não encontrado no plano.")
        sys.exit(1)

    header_xml = build_header(root, chunk)
    print(header_xml)

    if args.out:
        Path(args.out).write_text(header_xml, encoding="utf-8")
        print(f"\n[OK] Header salvo em: {args.out}")


def cmd_footer(args):
    project_dir = Path(args.project_dir)
    root  = _load_root(project_dir)
    plan  = _load_plan(project_dir)
    chunk = _find_chunk(plan, args.chunk_id)
    if chunk is None:
        print(f"[ERRO] chunk_id '{args.chunk_id}' não encontrado no plano.")
        sys.exit(1)

    translation = ""
    if args.translation_file:
        tf = Path(args.translation_file)
        if not tf.exists():
            print(f"[ERRO] Arquivo de tradução não encontrado: {tf}")
            sys.exit(1)
        translation = tf.read_text(encoding="utf-8")

    footer_md = build_footer(root, chunk, translation)
    print(footer_md)

    if args.out:
        Path(args.out).write_text(footer_md, encoding="utf-8")
        print(f"\n[OK] Footer salvo em: {args.out}")


def cmd_next(args):
    project_dir = Path(args.project_dir)
    plan = _load_plan(project_dir)
    if not plan:
        print("[AVISO] Nenhum plano encontrado. Execute 'plan' primeiro.")
        sys.exit(1)

    chunk = _next_pending(plan)
    if chunk is None:
        done = sum(1 for c in plan if c["status"] == "done")
        print(f"[OK] Todos os {done} chunks foram traduzidos! 🎉")
        return

    done  = sum(1 for c in plan if c["status"] == "done")
    total = len(plan)
    print(f"\n  Próximo chunk: {chunk['chunk_id']}")
    print(f"  Progresso: {done}/{total} chunks concluídos")
    print(f"  Palavras:  {chunk['word_count']}")
    print(f"\n  Início: \"{chunk['first_sentence'][:80]}...\"")
    print(f"\n  Para obter o header de contexto:")
    print(f"    python chunk_manager.py header --chunk-id {chunk['chunk_id']} "
          f"--project-dir {args.project_dir}\n")


def cmd_mark_done(args):
    project_dir = Path(args.project_dir)
    plan = _load_plan(project_dir)
    chunk = _find_chunk(plan, args.chunk_id)
    if chunk is None:
        print(f"[ERRO] chunk_id '{args.chunk_id}' não encontrado.")
        sys.exit(1)

    chunk["status"] = "done"
    chunk["translated_at"] = datetime.now().isoformat(timespec="seconds")
    _save_plan(project_dir, plan)

    # Atualizar progresso no SESSION_STATE
    root = _load_root(project_dir)
    prog = root.find("progress")
    if prog is not None:
        wt = prog.find("words_translated")
        if wt is not None:
            wt.text = str(int(wt.text or "0") + chunk["word_count"])
        cur = prog.find("current_chunk_id")
        if cur is not None:
            cur.text = chunk["chunk_id"]
    _save_root(root, project_dir)

    done  = sum(1 for c in plan if c["status"] == "done")
    total = len(plan)
    print(f"[OK] {args.chunk_id} marcado como concluído. ({done}/{total})")


def cmd_status(args):
    project_dir = Path(args.project_dir)
    plan = _load_plan(project_dir)
    if not plan:
        print("[AVISO] Nenhum plano encontrado.")
        return

    done    = [c for c in plan if c["status"] == "done"]
    pending = [c for c in plan if c["status"] == "pending"]
    total_w = sum(c["word_count"] for c in plan)
    done_w  = sum(c["word_count"] for c in done)

    pct = int(done_w / total_w * 100) if total_w else 0
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)

    print(f"\n{'='*60}")
    print(f"  PROGRESSO DE CHUNKS")
    print(f"{'='*60}")
    print(f"  [{bar}] {pct}%")
    print(f"  Concluídos: {len(done)}/{len(plan)} chunks")
    print(f"  Palavras:   {done_w:,}/{total_w:,}")

    if pending:
        print(f"\n  PRÓXIMOS PENDENTES:")
        for c in pending[:5]:
            print(f"    {c['chunk_id']:<25} {c['word_count']:>5} palavras")
        if len(pending) > 5:
            print(f"    ... e mais {len(pending)-5} chunks")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Chunk manager — skill tradutor-livros",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--project-dir", "-p", default="./translation_project")

    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("plan", help="Dividir texto em chunks e gerar plano")
    p.add_argument("--text-file", required=True)
    p.add_argument("--chapter", default="cap1")
    p.add_argument("--max-words", type=int, default=MAX_WORDS)
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("show", help="Exibir texto de um chunk")
    p.add_argument("--chunk-id", required=True)
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("header", help="Gerar chunk_header para o LLM")
    p.add_argument("--chunk-id", required=True)
    p.add_argument("--out", help="Salvar em arquivo")
    p.set_defaults(func=cmd_header)

    p = sub.add_parser("footer", help="Gerar chunk_footer pós-tradução")
    p.add_argument("--chunk-id", required=True)
    p.add_argument("--translation-file", help="Arquivo com a tradução produzida")
    p.add_argument("--out", help="Salvar em arquivo")
    p.set_defaults(func=cmd_footer)

    p = sub.add_parser("next", help="Mostrar próximo chunk a traduzir")
    p.set_defaults(func=cmd_next)

    p = sub.add_parser("mark-done", help="Marcar chunk como concluído")
    p.add_argument("--chunk-id", required=True)
    p.set_defaults(func=cmd_mark_done)

    p = sub.add_parser("status", help="Exibir progresso geral")
    p.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

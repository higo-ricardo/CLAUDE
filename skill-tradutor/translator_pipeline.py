#!/usr/bin/env python3
"""
translator_pipeline.py
======================
Orquestrador principal da skill tradutor-livros.

Coordena state_manager, glossary_manager, chunk_manager e text_preprocessor
para conduzir o ciclo completo de tradução sem exigir que o LLM execute
tarefas determinísticas.

Fluxo de trabalho:
  1. start    → inicializar projeto, pré-processar texto, planejar chunks
  2. translate → preparar próximo chunk para o LLM (header + texto limpo)
  3. submit   → processar output do LLM (footer, glossário, calques)
  4. resume   → retomar projeto de sessão anterior
  5. status   → visão geral do projeto
  6. report   → relatório final de qualidade

Uso:
  python translator_pipeline.py start   --text-file livro.txt --chapter cap1
  python translator_pipeline.py translate [--chunk-id cap1-chunk-001]
  python translator_pipeline.py submit  --chunk-id cap1-chunk-001 --translation-file trad.txt
  python translator_pipeline.py resume  --footer-file footer.xml
  python translator_pipeline.py status
  python translator_pipeline.py report  [--out relatorio.md]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

# Importar os módulos do projeto
# (assumindo que estão no mesmo diretório ou no PYTHONPATH)
try:
    import state_manager    as sm
    import glossary_manager as gm
    import chunk_manager    as cm
    import text_preprocessor as tp
except ImportError as e:
    print(f"[ERRO] Módulo não encontrado: {e}")
    print("Certifique-se de que todos os scripts estão no mesmo diretório.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

PIPELINE_LOG = "pipeline.log.json"

# ---------------------------------------------------------------------------
# Log de pipeline
# ---------------------------------------------------------------------------

def _load_log(project_dir: Path) -> list:
    path = project_dir / PIPELINE_LOG
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _append_log(project_dir: Path, event: dict) -> None:
    log = _load_log(project_dir)
    log.append({"timestamp": datetime.now().isoformat(timespec="seconds"), **event})
    path = project_dir / PIPELINE_LOG
    path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------------------------------------------------------------------------
# Interação com o usuário
# ---------------------------------------------------------------------------

def _ask(prompt: str, default: str = "") -> str:
    display = f"{prompt} [{default}]: " if default else f"{prompt}: "
    try:
        val = input(display).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return val if val else default


def _confirm(prompt: str) -> bool:
    try:
        ans = input(f"{prompt} [s/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return ans in ("s", "sim", "y", "yes")


def _collect_project_info() -> dict:
    """Coleta interativamente os metadados do projeto."""
    print("\n" + "═"*60)
    print("  NOVO PROJETO — Configuração Inicial")
    print("═"*60 + "\n")

    info = {}
    info["project/title_original"] = _ask("Título original (EN)")
    info["project/author"]         = _ask("Autor")

    print("\n  Gênero:")
    print("    1) literario   2) tecnico   3) infantil   4) academico   5) outro")
    genre_map = {"1": "literario", "2": "tecnico", "3": "infantil",
                 "4": "academico", "5": "outro"}
    g = _ask("  Escolha [1-5]", "1")
    info["project/genre"] = genre_map.get(g, "literario")

    print("\n  Registro/tom:")
    print("    1) neutro   2) formal   3) coloquial   4) erudito")
    reg_map = {"1": "neutro", "2": "formal", "3": "coloquial", "4": "erudito"}
    r = _ask("  Escolha [1-4]", "1")
    info["project/register"] = reg_map.get(r, "neutro")

    print("\n  Tratamento em PT-BR:")
    t = _ask("  você / tu / misto", "você")
    info["project/treatment"] = t

    info["project/target_audience"] = _ask("\n  Público-alvo", "adulto geral")
    info["project/title_pt"]        = _ask("  Título em PT-BR (deixe vazio se indefinido)", "")

    print("\n  Modo de entrega:")
    print("    1) chunk (500 palavras)   2) capitulo   3) livre")
    dm_map = {"1": "chunk", "2": "capitulo", "3": "livre"}
    d = _ask("  Escolha [1-3]", "1")
    info["project/delivery_mode"] = dm_map.get(d, "chunk")

    return info

# ---------------------------------------------------------------------------
# Comandos do pipeline
# ---------------------------------------------------------------------------

def cmd_start(args):
    """
    Inicializa projeto, pré-processa texto e planeja chunks.
    Ponto de entrada para projetos novos.
    """
    project_dir = Path(args.project_dir)
    project_dir.mkdir(parents=True, exist_ok=True)

    text_path = Path(args.text_file)
    if not text_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {text_path}")
        sys.exit(1)

    print(f"\n🚀 Iniciando projeto em: {project_dir}")

    # 1. Coletar metadados do projeto (interativo ou via --meta JSON)
    if args.meta:
        meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))
    else:
        meta = _collect_project_info()

    # 2. Inicializar SESSION_STATE
    state_path = sm.state_path(project_dir)
    if state_path.exists() and not args.force:
        if not _confirm("\n  SESSION_STATE já existe. Reinicializar?"):
            print("  Abortado. Use --force para forçar.")
            sys.exit(0)

    root = sm.build_empty_state()
    for field, value in meta.items():
        sm._set_nested(root, field, value)
    sm.save_state(root, project_dir)
    print("\n✅ SESSION_STATE inicializado.")

    # 3. Validar campos obrigatórios
    valid, errors = sm.validate_state(root)
    if not valid:
        print("\n[AVISO] Campos obrigatórios ausentes:")
        for e in errors:
            print(f"  {e}")
        if not _confirm("  Continuar mesmo assim?"):
            sys.exit(1)

    # 4. Pré-processar texto
    print(f"\n📋 Pré-processando: {text_path.name}")
    text = text_path.read_text(encoding="utf-8")
    prep_result = tp.prepare(text, fix=args.fix_text)
    print(tp.format_prepare_report(prep_result))

    # Salvar texto processado se houver correções
    source_text = prep_result["processed_text"]
    if args.fix_text and source_text != text:
        prepared_path = project_dir / f"{text_path.stem}.prepared.txt"
        prepared_path.write_text(source_text, encoding="utf-8")
        print(f"[OK] Texto pré-processado salvo em: {prepared_path}")
        text_path = prepared_path

    # Alertar sobre elementos não textuais
    if prep_result["elements"]:
        print(f"\n⚠️  {len(prep_result['elements'])} tipo(s) de elementos não textuais detectados.")
        print("   O módulo 'elementos-nao-textuais.md' será ativado automaticamente durante a tradução.")

    # 5. Planejar chunks
    chapter = args.chapter or "cap1"
    max_words = args.max_words or cm.MAX_WORDS
    print(f"\n📦 Planejando chunks ({max_words} palavras/chunk, capítulo: {chapter})...")

    chunks = cm.split_text_into_chunks(source_text, chapter, max_words=max_words)

    # Salvar arquivos de chunk
    chunks_dir = project_dir / "chunks" / chapter
    chunks_dir.mkdir(parents=True, exist_ok=True)
    for chunk in chunks:
        (chunks_dir / f"{chunk['chunk_id']}.txt").write_text(
            chunk["text"], encoding="utf-8"
        )

    plan = cm._load_plan(project_dir)
    existing_ids = {c["chunk_id"] for c in plan}
    plan += [c for c in chunks if c["chunk_id"] not in existing_ids]
    cm._save_plan(project_dir, plan)

    total_words = sum(c["word_count"] for c in chunks)
    print(f"\n  ✅ {len(chunks)} chunks planejados | {total_words:,} palavras")
    print(f"  Estimativa de sessões: ~{len(chunks)} (1 chunk por chamada ao LLM)\n")

    # 6. Registro no log
    _append_log(project_dir, {
        "event":         "project_started",
        "text_file":     str(text_path),
        "chapter":       chapter,
        "total_chunks":  len(chunks),
        "total_words":   total_words,
        "elements_found": len(prep_result["elements"]),
    })

    print("═"*60)
    print("  PROJETO PRONTO")
    print("═"*60)
    print(f"\n  Próximo passo:")
    print(f"    python translator_pipeline.py translate --project-dir {project_dir}\n")


def cmd_translate(args):
    """
    Prepara o próximo chunk (ou o especificado) para envio ao LLM.
    Produz: chunk_header + texto original limpo + instruções ao LLM.
    """
    project_dir = Path(args.project_dir)
    root = sm.load_state(project_dir)
    plan = cm._load_plan(project_dir)

    if not plan:
        print("[ERRO] Nenhum plano encontrado. Execute 'start' primeiro.")
        sys.exit(1)

    # Selecionar chunk
    if args.chunk_id:
        chunk = cm._find_chunk(plan, args.chunk_id)
        if chunk is None:
            print(f"[ERRO] chunk_id '{args.chunk_id}' não encontrado.")
            sys.exit(1)
    else:
        chunk = cm._next_pending(plan)
        if chunk is None:
            print("🎉 Todos os chunks foram traduzidos!")
            return

    # Verificar conflitos abertos de glossário
    gl = root.find("glossary") or []
    open_conflicts = [e for e in (gl if gl is not None else []) if e.get("status") == "conflict"]
    if open_conflicts:
        print(f"\n⚠️  {len(open_conflicts)} conflito(s) de glossário em aberto!")
        print("   Resolva antes de continuar:")
        for c in open_conflicts:
            print(f"   python glossary_manager.py resolve --en \"{c.get('en')}\" "
                  f"--pt \"<escolha>\" --project-dir {project_dir}")
        if not _confirm("\n   Continuar mesmo assim?"):
            sys.exit(0)

    # Verificar elementos não textuais no chunk
    chunk_text = chunk["text"]
    elements   = tp.detect_elements(chunk_text)
    calques_in_src = []  # calques só fazem sentido no texto traduzido

    # Construir header
    header_xml = cm.build_header(root, chunk)

    # Montar prompt completo para o LLM
    done  = sum(1 for c in plan if c["status"] == "done")
    total = len(plan)

    print("\n" + "═"*65)
    print(f"  CHUNK PRONTO PARA TRADUÇÃO — {chunk['chunk_id']}")
    print(f"  Progresso: {done}/{total} | Palavras: {chunk['word_count']}")
    print("═"*65)

    print("\n─── COLE ESTE BLOCO INTEIRO NA CONVERSA COM O LLM ─────────\n")

    output_lines = [
        "<!-- INÍCIO DO BLOCO DE TRADUÇÃO -->",
        "",
        f"<!-- chunk_header — contexto do projeto -->",
        "```xml",
        header_xml.strip(),
        "```",
        "",
    ]

    if elements:
        output_lines += [
            "🗂️ **ELEMENTOS NÃO TEXTUAIS DETECTADOS NESTE CHUNK**",
            "",
            tp.format_detection_report(elements, chunk_text),
            "Carregue o módulo `referencias/elementos-nao-textuais.md` antes de traduzir.",
            "",
        ]

    output_lines += [
        "**TEXTO A TRADUZIR:**",
        "",
        chunk_text,
        "",
        "<!-- FIM DO BLOCO DE TRADUÇÃO -->",
        "",
        "**Após receber a tradução do LLM, execute:**",
        f"  1. Salve a tradução em um arquivo (ex: trad_{chunk['chunk_id']}.txt)",
        f"  2. python translator_pipeline.py submit \\",
        f"       --chunk-id {chunk['chunk_id']} \\",
        f"       --translation-file trad_{chunk['chunk_id']}.txt \\",
        f"       --project-dir {project_dir}",
    ]

    print("\n".join(output_lines))

    _append_log(project_dir, {
        "event":         "chunk_sent_to_llm",
        "chunk_id":      chunk["chunk_id"],
        "word_count":    chunk["word_count"],
        "elements_found": len(elements),
    })


def cmd_submit(args):
    """
    Processa a tradução retornada pelo LLM:
    - Detecta calques no texto traduzido
    - Atualiza progresso no SESSION_STATE
    - Gera chunk_footer
    - Marca chunk como concluído
    """
    project_dir = Path(args.project_dir)
    root = sm.load_state(project_dir)
    plan = cm._load_plan(project_dir)

    chunk = cm._find_chunk(plan, args.chunk_id)
    if chunk is None:
        print(f"[ERRO] chunk_id '{args.chunk_id}' não encontrado.")
        sys.exit(1)

    trad_path = Path(args.translation_file)
    if not trad_path.exists():
        print(f"[ERRO] Arquivo de tradução não encontrado: {trad_path}")
        sys.exit(1)

    translation = trad_path.read_text(encoding="utf-8")

    print(f"\n📥 Processando tradução: {args.chunk_id}")

    # 1. Detectar calques na tradução
    calques = tp.detect_calques(translation)
    if calques:
        print(f"\n⚠️  {len(calques)} calque(s) detectado(s) na tradução:")
        print(tp.format_calques_report(calques))
        if not _confirm("   Continuar mesmo com calques?"):
            print("   Corrija a tradução e reenvie.")
            sys.exit(0)
    else:
        print("  ✅ Nenhum calque detectado na tradução.")

    # 2. Adaptar formatos numéricos na tradução
    fixed_translation, num_changes = tp.fix_number_format(translation)
    if num_changes:
        print(f"\n  📐 {len(num_changes)} adaptação(ões) numérica(s) aplicada(s):")
        for c in num_changes:
            print(f"    {c}")
        # Salvar tradução corrigida
        trad_path.write_text(fixed_translation, encoding="utf-8")
        translation = fixed_translation

    # 3. Atualizar progresso no SESSION_STATE
    prog = root.find("progress")
    if prog is not None:
        wt = prog.find("words_translated")
        if wt is not None:
            wt.text = str(int(wt.text or "0") + chunk["word_count"])
        cur = prog.find("current_chunk_id")
        if cur is not None:
            cur.text = chunk["chunk_id"]
        # Guardar último parágrafo para o próximo header
        pars = [p.strip() for p in translation.split("\n\n") if p.strip()]
        last_par_node = prog.find("last_paragraph_translated")
        if last_par_node is None:
            import xml.etree.ElementTree as ET
            last_par_node = ET.SubElement(prog, "last_paragraph_translated")
        last_par_node.text = pars[-1][:500] if pars else ""

    sm.save_state(root, project_dir)

    # 4. Marcar chunk como concluído no plano
    chunk["status"]        = "done"
    chunk["translated_at"] = datetime.now().isoformat(timespec="seconds")
    cm._save_plan(project_dir, plan)

    # 5. Salvar tradução na pasta do projeto
    trad_dir = project_dir / "translations"
    trad_dir.mkdir(exist_ok=True)
    final_trad = trad_dir / f"{chunk['chunk_id']}.pt.txt"
    final_trad.write_text(translation, encoding="utf-8")

    # 6. Gerar chunk_footer
    footer_md = cm.build_footer(root, chunk, translation)
    footer_path = project_dir / "chunks" / f"{chunk['chunk_id']}.footer.md"
    footer_path.write_text(footer_md, encoding="utf-8")

    # 7. Exibir footer e próximo passo
    done  = sum(1 for c in plan if c["status"] == "done")
    total = len(plan)
    next_chunk = cm._next_pending(plan)

    print(f"\n  ✅ {chunk['chunk_id']} concluído. ({done}/{total})")
    print(f"\n─── PACOTE DE ESTADO ─────────────────────────────────────\n")
    print(footer_md)

    if next_chunk:
        print(f"\n─── PRÓXIMO CHUNK ────────────────────────────────────────")
        print(f"  {next_chunk['chunk_id']} | {next_chunk['word_count']} palavras")
        print(f"\n  python translator_pipeline.py translate --project-dir {project_dir}\n")
    else:
        print("\n🎉 TODOS OS CHUNKS TRADUZIDOS!")
        print(f"\n  Gerar relatório final:")
        print(f"  python translator_pipeline.py report --project-dir {project_dir}\n")

    _append_log(project_dir, {
        "event":       "chunk_submitted",
        "chunk_id":    chunk["chunk_id"],
        "calques":     len(calques),
        "num_changes": len(num_changes),
        "words":       chunk["word_count"],
    })


def cmd_resume(args):
    """
    Retoma projeto a partir de um chunk_footer exportado pelo LLM.
    Reconstrói o SESSION_STATE a partir do snapshot no footer.
    """
    project_dir = Path(args.project_dir)
    project_dir.mkdir(parents=True, exist_ok=True)

    if not args.footer_file:
        print("[ERRO] Informe o arquivo com o chunk_footer: --footer-file footer.xml")
        sys.exit(1)

    footer_path = Path(args.footer_file)
    if not footer_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {footer_path}")
        sys.exit(1)

    # Tentar extrair XML do footer (pode estar dentro de bloco Markdown)
    raw = footer_path.read_text(encoding="utf-8")

    # Remover blocos de código Markdown se presentes
    import re
    xml_match = re.search(r"```xml\s*([\s\S]+?)```", raw)
    xml_content = xml_match.group(1).strip() if xml_match else raw.strip()

    try:
        footer = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"[ERRO] XML inválido no footer: {e}")
        sys.exit(1)

    print(f"\n📂 Retomando projeto a partir de: {footer_path.name}")

    # Reconstruir SESSION_STATE
    state_path = sm.state_path(project_dir)
    if state_path.exists():
        root = sm.load_state(project_dir)
    else:
        root = sm.build_empty_state()

    # Restaurar glossário do snapshot
    gl_snap = footer.find("glossary_snapshot")
    if gl_snap is not None:
        gl_existing = root.find("glossary")
        if gl_existing is not None:
            root.remove(gl_existing)
        import xml.etree.ElementTree as _ET
        new_gl = _ET.SubElement(root, "glossary",
                                version=gl_snap.get("version", "1"))
        for entry in gl_snap:
            new_gl.append(_ET.fromstring(_ET.tostring(entry)))
        print(f"  ✅ Glossário restaurado: {len(list(new_gl))} entradas")

    # Restaurar decisões
    dec_snap = footer.find("decisions_snapshot")
    if dec_snap is not None:
        dec_existing = root.find("decisions")
        if dec_existing is not None:
            root.remove(dec_existing)
        import xml.etree.ElementTree as _ET
        new_dec = _ET.SubElement(root, "decisions")
        for d in dec_snap:
            new_dec.append(_ET.fromstring(_ET.tostring(d)))
        print(f"  ✅ Decisões restauradas: {len(list(new_dec))}")

    # Restaurar pendências
    pend_snap = footer.find("pending_snapshot")
    if pend_snap is not None:
        pend_existing = root.find("pending")
        if pend_existing is not None:
            root.remove(pend_existing)
        import xml.etree.ElementTree as _ET
        new_pend = _ET.SubElement(root, "pending")
        for item in pend_snap:
            new_pend.append(_ET.fromstring(_ET.tostring(item)))

    # Restaurar progresso
    prog_snap = footer.find("progress")
    if prog_snap is not None:
        prog_existing = root.find("progress")
        if prog_existing is not None:
            for field in ["last_paragraph_id", "words_translated_total", "last_sentence"]:
                val = prog_snap.findtext(field)
                if val:
                    sm._set_nested(root, f"progress/{field.replace('words_translated_total', 'words_translated')}", val)

    sm.save_state(root, project_dir)

    # Mostrar estado restaurado e próximo chunk
    chunk_id = footer.findtext("chunk_id") or "?"
    print(f"\n  Último chunk concluído: {chunk_id}")
    next_sent = footer.findtext("progress/next_chunk_starts") or "?"
    print(f"  Próximo trecho começa: \"{next_sent[:80]}...\"")
    print(f"\n  SESSION_STATE atualizado: {sm.state_path(project_dir)}")
    print(f"\n  Próximo passo:")
    print(f"    python translator_pipeline.py translate --project-dir {project_dir}\n")

    _append_log(project_dir, {
        "event":       "session_resumed",
        "from_footer": str(footer_path),
        "last_chunk":  chunk_id,
    })


def cmd_status(args):
    """Visão geral do projeto."""
    project_dir = Path(args.project_dir)

    # SESSION_STATE
    try:
        root = sm.load_state(project_dir)
        sm.print_status(root)
    except FileNotFoundError:
        print("[AVISO] SESSION_STATE não encontrado.")

    # Plano de chunks
    plan = cm._load_plan(project_dir)
    if plan:
        done  = sum(1 for c in plan if c["status"] == "done")
        total = len(plan)
        total_w = sum(c["word_count"] for c in plan)
        done_w  = sum(c["word_count"] for c in plan if c["status"] == "done")
        pct = int(done_w / total_w * 100) if total_w else 0
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)

        print(f"  CHUNKS: [{bar}] {pct}% | {done}/{total} | {done_w:,}/{total_w:,} palavras\n")

    # Log de eventos
    log = _load_log(project_dir)
    if log:
        print(f"  Último evento: {log[-1].get('event')} — {log[-1].get('timestamp')}")
    print()


def cmd_report(args):
    """Gera relatório final de qualidade do projeto."""
    project_dir = Path(args.project_dir)

    try:
        root = sm.load_state(project_dir)
    except FileNotFoundError:
        print("[ERRO] SESSION_STATE não encontrado.")
        sys.exit(1)

    plan  = cm._load_plan(project_dir)
    log   = _load_log(project_dir)
    proj  = root.find("project")
    gl    = list(root.find("glossary") or [])
    decs  = list(root.find("decisions") or [])
    pend  = list(root.find("pending") or [])

    done      = [c for c in plan if c["status"] == "done"]
    total_w   = sum(c["word_count"] for c in plan)
    done_w    = sum(c["word_count"] for c in done)
    conflicts = [e for e in (gl if gl is not None else []) if e.get("status") == "conflict"]

    # Consolidar traduções
    translations_dir = project_dir / "translations"
    full_translation = ""
    if translations_dir.exists():
        for chunk in sorted(done, key=lambda c: c["chunk_id"]):
            tfile = translations_dir / f"{chunk['chunk_id']}.pt.txt"
            if tfile.exists():
                full_translation += tfile.read_text(encoding="utf-8") + "\n\n"

    # Calques no texto completo
    all_calques = tp.detect_calques(full_translation) if full_translation else []

    title = (proj.findtext("title_original") or "—") if proj else "—"
    author = (proj.findtext("author") or "—") if proj else "—"

    lines = [
        f"# Relatório Final — {title}",
        f"Autor: {author}",
        f"Gerado em: {datetime.now():%d/%m/%Y %H:%M}",
        "",
        "---",
        "",
        "## Progresso",
        "",
        f"- Chunks traduzidos: {len(done)}/{len(plan)}",
        f"- Palavras traduzidas: {done_w:,}/{total_w:,}",
        f"- Percentual: {int(done_w/total_w*100) if total_w else 0}%",
        "",
        "## Glossário",
        "",
        f"- Total de entradas: {len(gl)}",
        f"- Confirmadas: {sum(1 for e in (gl if gl is not None else []) if e.get('status') == 'confirmed')}",
        f"- Pendentes: {sum(1 for e in (gl if gl is not None else []) if e.get('status') == 'pending')}",
        f"- Com conflito: {len(conflicts)}",
        "",
    ]

    if conflicts:
        lines += ["### ⚠️ Conflitos de glossário em aberto", ""]
        for c in conflicts:
            lines.append(f"- `{c.get('en')}` → '{c.get('pt')}' | candidato: '{c.get('conflict_candidate', '?')}'")
        lines.append("")

    if pend:
        lines += ["## Pendências", ""]
        for item in pend:
            lines.append(f"- [{item.get('type', '?')}] {item.get('description', '?')}")
        lines.append("")

    if all_calques:
        lines += [f"## ⚠️ Calques detectados no texto completo ({len(all_calques)})", ""]
        for h in all_calques[:20]:
            lines.append(f"- \"{h['match']}\" → sugestão: {h['suggestion']}")
        if len(all_calques) > 20:
            lines.append(f"- ... e mais {len(all_calques)-20} ocorrências")
        lines.append("")
    else:
        lines.append("## ✅ Calques: nenhum detectado no texto completo\n")

    lines += [
        "## Glossário completo",
        "",
        "| EN | PT | Contexto | Capítulo | Status |",
        "|----|-----|----------|----------|--------|",
    ]
    for entry in gl:
        lines.append(
            f"| {entry.get('en')} | {entry.get('pt')} | "
            f"{entry.get('context','—')} | {entry.get('chapter','—')} | "
            f"{entry.get('status','?')} |"
        )

    report = "\n".join(lines)
    print(report)

    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"\n[OK] Relatório salvo em: {args.out}")

    # Salvar tradução consolidada
    if full_translation:
        consolidated = project_dir / "exports" / "traducao_completa.txt"
        consolidated.parent.mkdir(exist_ok=True)
        consolidated.write_text(full_translation, encoding="utf-8")
        print(f"[OK] Tradução consolidada salva em: {consolidated}")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline de tradução — skill tradutor-livros",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Fluxo típico:
  1. python translator_pipeline.py start     --text-file cap1.txt
  2. python translator_pipeline.py translate
  3. [LLM produz tradução → salvar em trad_cap1-chunk-001.txt]
  4. python translator_pipeline.py submit    --chunk-id cap1-chunk-001 --translation-file trad_cap1-chunk-001.txt
  5. Repetir 2-4 até status mostrar 100%
  6. python translator_pipeline.py report    --out relatorio_final.md
        """,
    )
    parser.add_argument("--project-dir", "-p", default="./translation_project")

    sub = parser.add_subparsers(dest="command", required=True)

    # start
    p = sub.add_parser("start", help="Iniciar novo projeto de tradução")
    p.add_argument("--text-file",  required=True, help="Arquivo de texto original (.txt)")
    p.add_argument("--chapter",    default="cap1", help="ID do capítulo (ex: cap1)")
    p.add_argument("--max-words",  type=int, default=500)
    p.add_argument("--meta",       help="JSON com metadados do projeto (evita modo interativo)")
    p.add_argument("--fix-text",   action="store_true", help="Aplicar correções OCR e numéricas")
    p.add_argument("--force",      action="store_true", help="Reinicializar mesmo se já existir")
    p.set_defaults(func=cmd_start)

    # translate
    p = sub.add_parser("translate", help="Preparar próximo chunk para o LLM")
    p.add_argument("--chunk-id", help="Chunk específico (padrão: próximo pendente)")
    p.set_defaults(func=cmd_translate)

    # submit
    p = sub.add_parser("submit", help="Processar tradução retornada pelo LLM")
    p.add_argument("--chunk-id",         required=True)
    p.add_argument("--translation-file", required=True)
    p.set_defaults(func=cmd_submit)

    # resume
    p = sub.add_parser("resume", help="Retomar projeto a partir de um chunk_footer")
    p.add_argument("--footer-file", required=True, help="Arquivo com o chunk_footer XML/MD")
    p.set_defaults(func=cmd_resume)

    # status
    p = sub.add_parser("status", help="Exibir status geral do projeto")
    p.set_defaults(func=cmd_status)

    # report
    p = sub.add_parser("report", help="Gerar relatório final de qualidade")
    p.add_argument("--out", help="Salvar relatório em arquivo Markdown")
    p.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

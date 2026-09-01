#!/usr/bin/env python3
"""
streamer.py — Chunk & Streaming para a Editora Ebook v2.

Três modos de operação:
  1. chunk-file   — divide arquivo .md grande em chunks para processamento paralelo
  2. stream-api   — chama API Anthropic com streaming SSE, entrega tokens progressivamente
  3. stream-pipe  — executa script + captura output em streaming linha a linha

Uso:
  # Dividir capítulo longo em chunks para analyzer.py
  python scripts/streamer.py chunk-file --input cap_longo.md --size 500

  # Streaming da API com system prompt e contexto compacto
  python scripts/streamer.py stream-api \
    --system references/02-redacao-capitulos.md \
    --prompt "Escreva o gancho do capítulo 3 sobre gestão do tempo" \
    --model claude-sonnet-4-20250514

  # Executar script com output em streaming (linha a linha)
  python scripts/streamer.py stream-pipe \
    --command "analyzer.py --text cap01.md --mode readability --level leigo"
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent

# ─────────────────────────────────────────────────────────────────────────────
# MODO 1: CHUNK DE ARQUIVO
# ─────────────────────────────────────────────────────────────────────────────

def chunk_file(input_path: str, chunk_size: int, overlap: int, output_dir: str):
    """
    Divide um arquivo .md em chunks de N palavras com overlap configurável.
    Preserva parágrafos inteiros — nunca corta no meio de uma frase.
    Retorna manifesto JSON com metadados de cada chunk.
    """
    path = Path(input_path)
    if not path.exists():
        print(f"[CHUNK] Arquivo não encontrado: {input_path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    paragraphs = [p.strip() for p in re.split(r'\n\n+', text) if p.strip()]

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    chunks = []
    current_words = []
    current_paras = []
    chunk_idx = 0
    total_words = len(text.split())

    print(f"[CHUNK] Arquivo: {path.name}")
    print(f"[CHUNK] Total de palavras: {total_words}")
    print(f"[CHUNK] Tamanho do chunk: {chunk_size} palavras | Overlap: {overlap} palavras")
    print()

    for para in paragraphs:
        para_words = para.split()
        current_words.extend(para_words)
        current_paras.append(para)

        if len(current_words) >= chunk_size:
            # Salvar chunk
            chunk_text = "\n\n".join(current_paras)
            chunk_file_path = out_dir / f"chunk_{chunk_idx:03d}.md"
            chunk_file_path.write_text(chunk_text, encoding="utf-8")

            word_count = len(current_words)
            chunk_meta = {
                "index": chunk_idx,
                "file": str(chunk_file_path),
                "words": word_count,
                "paragraphs": len(current_paras),
                "start_para": paragraphs.index(current_paras[0]),
            }
            chunks.append(chunk_meta)

            print(f"  chunk_{chunk_idx:03d}.md  →  {word_count} palavras  ({len(current_paras)} parágrafos)")

            # Overlap: manter últimos N palavras para contexto
            if overlap > 0:
                overlap_text = " ".join(current_words[-overlap:])
                # Encontrar parágrafo que contém essas palavras
                carry_paras = []
                carry_words = 0
                for p in reversed(current_paras):
                    carry_paras.insert(0, p)
                    carry_words += len(p.split())
                    if carry_words >= overlap:
                        break
                current_paras = carry_paras
                current_words = " ".join(carry_paras).split()
            else:
                current_paras = []
                current_words = []

            chunk_idx += 1

    # Último chunk (palavras restantes)
    if current_paras:
        chunk_text = "\n\n".join(current_paras)
        chunk_file_path = out_dir / f"chunk_{chunk_idx:03d}.md"
        chunk_file_path.write_text(chunk_text, encoding="utf-8")
        word_count = len(current_words)
        chunks.append({
            "index": chunk_idx,
            "file": str(chunk_file_path),
            "words": word_count,
            "paragraphs": len(current_paras),
        })
        print(f"  chunk_{chunk_idx:03d}.md  →  {word_count} palavras  ({len(current_paras)} parágrafos)")
        chunk_idx += 1

    # Salvar manifesto
    manifest = {
        "source": str(path.resolve()),
        "total_words": total_words,
        "total_chunks": chunk_idx,
        "chunk_size": chunk_size,
        "overlap": overlap,
        "chunks": chunks,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"[CHUNK] {chunk_idx} chunks gerados em '{out_dir}'")
    print(f"[CHUNK] Manifesto: {manifest_path}")
    return manifest


# ─────────────────────────────────────────────────────────────────────────────
# MODO 2: STREAMING DA API ANTHROPIC
# ─────────────────────────────────────────────────────────────────────────────

def stream_api(system_file: str, prompt: str, model: str, max_tokens: int, save_to: str):
    """
    Chama a API Anthropic com streaming SSE.
    Entrega tokens progressivamente no stdout.
    Opcionalmente salva o output completo em arquivo.
    """
    try:
        import anthropic
    except ImportError:
        print("[STREAM-API] anthropic não instalado. Execute: pip install anthropic", file=sys.stderr)
        sys.exit(1)

    # Carregar system prompt (compacto — só o reference relevante)
    system_content = ""
    if system_file:
        sp = Path(system_file)
        if not sp.exists():
            sp = PROJECT_ROOT / system_file
        if sp.exists():
            system_content = sp.read_text(encoding="utf-8")
            word_count = len(system_content.split())
            print(f"[STREAM-API] System: {sp.name} ({word_count} palavras / ~{word_count//3} tokens estimados)")
        else:
            print(f"[STREAM-API] Arquivo system não encontrado: {system_file}", file=sys.stderr)

    print(f"[STREAM-API] Modelo: {model}")
    print(f"[STREAM-API] Max tokens: {max_tokens}")
    print(f"[STREAM-API] Iniciando stream...\n")
    print("─" * 60)

    client = anthropic.Anthropic()

    full_response = []
    input_tokens = 0
    output_tokens = 0
    start_time = time.time()
    first_token_time = None

    try:
        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=system_content if system_content else "Você é um assistente editorial especializado.",
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                if first_token_time is None:
                    first_token_time = time.time()
                print(text, end="", flush=True)
                full_response.append(text)

        # Métricas finais
        message = stream.get_final_message()
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens

    except anthropic.APIConnectionError:
        print("\n[STREAM-API] Erro de conexão com a API.", file=sys.stderr)
        sys.exit(1)
    except anthropic.AuthenticationError:
        print("\n[STREAM-API] Chave de API inválida ou ausente.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[STREAM-API] Erro: {e}", file=sys.stderr)
        sys.exit(1)

    elapsed = time.time() - start_time
    ttft = (first_token_time - start_time) if first_token_time else 0
    full_text = "".join(full_response)

    print("\n" + "─" * 60)
    print(f"\n[STREAM-API] Concluído em {elapsed:.1f}s")
    print(f"[STREAM-API] Time to first token: {ttft:.2f}s")
    print(f"[STREAM-API] Tokens de entrada: {input_tokens}")
    print(f"[STREAM-API] Tokens de saída: {output_tokens}")
    print(f"[STREAM-API] Velocidade: {output_tokens/elapsed:.1f} tokens/s")

    if save_to:
        out_path = Path(save_to)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(full_text, encoding="utf-8")
        print(f"[STREAM-API] Output salvo: {save_to}")

    return full_text, {"input_tokens": input_tokens, "output_tokens": output_tokens,
                       "elapsed": elapsed, "ttft": ttft}


# ─────────────────────────────────────────────────────────────────────────────
# MODO 3: STREAM-PIPE — script com output linha a linha
# ─────────────────────────────────────────────────────────────────────────────

def stream_pipe(command: str, label: str):
    """
    Executa um script da Editora Ebook e entrega output linha a linha (streaming).
    Captura stderr separadamente. Mede tempo de execução.
    """
    parts = command.split()
    if not parts:
        print("[STREAM-PIPE] Comando vazio.", file=sys.stderr)
        return

    script_name = parts[0]
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"[STREAM-PIPE] Script não encontrado: {script_name}", file=sys.stderr)
        return

    cmd = [sys.executable, str(script_path)] + parts[1:]

    # Resolver caminhos relativos
    resolved_cmd = []
    for i, arg in enumerate(cmd):
        if i > 1 and not arg.startswith("-"):
            candidate = PROJECT_ROOT / arg
            if candidate.exists() and not Path(arg).exists():
                resolved_cmd.append(str(candidate))
                continue
        resolved_cmd.append(arg)

    tag = f"[{label}]" if label else f"[{script_name}]"
    print(f"{tag} Executando: {command}")
    print("─" * 60)

    start = time.time()
    lines_out = 0

    try:
        proc = subprocess.Popen(
            resolved_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(PROJECT_ROOT),
        )

        # Streaming linha a linha
        for line in proc.stdout:
            print(line, end="", flush=True)
            lines_out += 1

        proc.wait()
        stderr_out = proc.stderr.read()
        elapsed = time.time() - start

        print("─" * 60)
        print(f"{tag} Concluído em {elapsed:.3f}s | {lines_out} linhas | exit={proc.returncode}")

        if stderr_out.strip():
            print(f"{tag} STDERR: {stderr_out[:200]}", file=sys.stderr)

        return proc.returncode, elapsed, lines_out

    except Exception as e:
        print(f"{tag} Erro: {e}", file=sys.stderr)
        return 1, 0, 0


# ─────────────────────────────────────────────────────────────────────────────
# MODO 4: CHUNK + ANALYZE (pipeline completo)
# ─────────────────────────────────────────────────────────────────────────────

def chunk_and_analyze(input_path: str, mode: str, level: str, chunk_size: int, overlap: int):
    """
    Pipeline completo: chunk → analyzer.py por chunk → consolida resultados.
    Demonstra processamento em chunks de arquivo grande.
    """
    out_dir = f"/tmp/editora_chunks_{Path(input_path).stem}"

    print(f"[PIPELINE] Arquivo: {input_path}")
    print(f"[PIPELINE] Modo de análise: {mode}")
    print(f"[PIPELINE] Chunk size: {chunk_size} palavras | Overlap: {overlap} palavras")
    print()

    # Step 1: Chunking
    print("═" * 60)
    print("FASE 1 — CHUNKING")
    print("═" * 60)
    manifest = chunk_file(input_path, chunk_size, overlap, out_dir)

    # Step 2: Analyzer em cada chunk (streaming)
    print()
    print("═" * 60)
    print(f"FASE 2 — ANÁLISE ({mode.upper()}) POR CHUNK")
    print("═" * 60)

    all_results = []
    total_start = time.time()

    for chunk in manifest["chunks"]:
        chunk_path = chunk["file"]
        args = f"analyzer.py --text {chunk_path} --mode {mode}"
        if mode == "readability":
            args += f" --level {level}"
        if mode == "jargon":
            args += f" --glossary {PROJECT_ROOT}/data/glossary.json"

        rc, elapsed, lines = stream_pipe(args, f"chunk_{chunk['index']:03d}")

        # Capturar resultado JSON do chunk
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "analyzer.py"),
             "--text", chunk_path, "--mode", mode]
            + (["--level", level] if mode == "readability" else [])
            + (["--glossary", str(PROJECT_ROOT / "data/glossary.json")] if mode == "jargon" else []),
            capture_output=True, text=True, cwd=str(PROJECT_ROOT)
        )
        try:
            chunk_result = json.loads(result.stdout)
            chunk_result["_chunk"] = chunk["index"]
            chunk_result["_words"] = chunk["words"]
            chunk_result["_elapsed"] = round(elapsed, 3)
            all_results.append(chunk_result)
        except json.JSONDecodeError:
            pass
        print()

    total_elapsed = time.time() - total_start

    # Step 3: Consolidação
    print("═" * 60)
    print("FASE 3 — CONSOLIDAÇÃO DOS RESULTADOS")
    print("═" * 60)
    print()
    consolidate_results(all_results, mode, manifest, total_elapsed)


def consolidate_results(results: list, mode: str, manifest: dict, total_elapsed: float):
    """Consolida resultados de múltiplos chunks em relatório unificado."""

    print(f"Arquivo original: {Path(manifest['source']).name}")
    print(f"Total de palavras: {manifest['total_words']}")
    print(f"Chunks processados: {manifest['total_chunks']}")
    print(f"Tempo total de análise: {total_elapsed:.2f}s")
    print()

    if mode == "passive":
        total = sum(r.get("total", 0) for r in results)
        all_occ = []
        for r in results:
            all_occ.extend(r.get("ocorrencias", []))
        print(f"Ocorrências de voz passiva: {total}")
        if all_occ:
            print("\nExemplos encontrados:")
            for o in all_occ[:5]:
                print(f"  Linha {o['linha']}: {o['trecho'][:80]}...")

    elif mode == "readability":
        medias = [r["media_palavras_por_frase"] for r in results if "media_palavras_por_frase" in r]
        fleschs = [r["flesch"] for r in results if "flesch" in r]
        if medias:
            avg_media = round(sum(medias) / len(medias), 1)
            avg_flesch = round(sum(fleschs) / len(fleschs), 1)
            classificacoes = [r.get("classificacao", "") for r in results]
            mais_comum = max(set(classificacoes), key=classificacoes.count)
            print(f"Média de palavras/frase (agregada): {avg_media}")
            print(f"Índice Flesch médio: {avg_flesch}")
            print(f"Classificação predominante: {mais_comum}")

            total_longas = sum(r.get("frases_acima_limite", 0) for r in results)
            print(f"Total de frases acima do limite: {total_longas}")

    elif mode == "jargon":
        all_terms = set()
        for r in results:
            all_terms.update(r.get("termos", []))
        print(f"Jargões sem definição (únicos): {len(all_terms)}")
        if all_terms:
            print(f"Termos: {', '.join(sorted(all_terms))}")

    elif mode == "numbering":
        total = sum(r.get("total_inconsistencias", 0) for r in results)
        print(f"Inconsistências de numeração: {total}")

    print()
    print("[PIPELINE] Análise por chunks concluída.")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Streamer da Editora Ebook v2 — Chunk & Streaming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    # chunk-file
    p1 = sub.add_parser("chunk-file", help="Dividir arquivo .md em chunks")
    p1.add_argument("--input", required=True)
    p1.add_argument("--size", type=int, default=300, help="Palavras por chunk (padrão: 300)")
    p1.add_argument("--overlap", type=int, default=50, help="Palavras de overlap (padrão: 50)")
    p1.add_argument("--output-dir", default="/tmp/editora_chunks")

    # stream-api
    p2 = sub.add_parser("stream-api", help="Streaming da API Anthropic")
    p2.add_argument("--system", help="Arquivo .md de referência como system prompt")
    p2.add_argument("--prompt", required=True)
    p2.add_argument("--model", default="claude-sonnet-4-20250514")
    p2.add_argument("--max-tokens", type=int, default=1000)
    p2.add_argument("--save-to", help="Salvar output em arquivo")

    # stream-pipe
    p3 = sub.add_parser("stream-pipe", help="Executar script com output em streaming")
    p3.add_argument("--command", required=True, help="Ex: 'analyzer.py --text cap.md --mode passive'")
    p3.add_argument("--label", default="")

    # chunk-and-analyze (pipeline completo)
    p4 = sub.add_parser("chunk-analyze", help="Pipeline completo: chunk + análise por chunks")
    p4.add_argument("--input", required=True)
    p4.add_argument("--mode", choices=["passive", "readability", "jargon", "numbering"],
                    default="readability")
    p4.add_argument("--level", default="intermediario")
    p4.add_argument("--size", type=int, default=300)
    p4.add_argument("--overlap", type=int, default=50)

    args = parser.parse_args()

    if args.mode == "chunk-file":
        chunk_file(args.input, args.size, args.overlap, args.output_dir)
    elif args.mode == "stream-api":
        stream_api(args.system, args.prompt, args.model, args.max_tokens, args.save_to)
    elif args.mode == "stream-pipe":
        stream_pipe(args.command, args.label)
    elif args.mode == "chunk-analyze":
        chunk_and_analyze(args.input, args.mode, args.level, args.size, args.overlap)


if __name__ == "__main__":
    main()

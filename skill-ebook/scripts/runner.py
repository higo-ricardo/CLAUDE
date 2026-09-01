#!/usr/bin/env python3
"""
runner.py — Ponto de entrada único para a Editora Ebook.
Interpreta blocos [SCRIPT: ...] emitidos pela LLM e executa o script correto.

Uso direto:
  python scripts/runner.py "scorer.py --s1 8.5 --s2 7.0 --s3 9.0 --s4 10.0 --s5 6.5 --stage M5 --chapter Cap1 --version v1.2"
  python scripts/runner.py "analyzer.py --text cap01.md --mode passive"
  python scripts/runner.py "decisions.py --action list"
  python scripts/runner.py "versioner.py --action state"

Modo pipe (colar bloco [SCRIPT:] diretamente):
  echo "[SCRIPT: scorer.py --consolidate]" | python scripts/runner.py --pipe

Modo interativo:
  python scripts/runner.py --interactive
"""

import argparse
import os
import re
import subprocess
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

ALLOWED_SCRIPTS = {
    "scorer.py", "analyzer.py", "versioner.py",
    "decisions.py", "publisher.py", "exporter.py", "templater.py",
}


def parse_script_block(text):
    """Extrai conteúdo de [SCRIPT: ...] emitido pela LLM."""
    match = re.search(r'\[SCRIPT:\s*(.+?)\]', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def run_command(command_str):
    """Valida e executa o comando, retornando output formatado."""
    parts = command_str.split()
    if not parts:
        print("[RUNNER] Comando vazio.")
        return

    script_name = parts[0]
    if script_name not in ALLOWED_SCRIPTS:
        print(f"[RUNNER] Script não permitido: {script_name}")
        print(f"[RUNNER] Scripts válidos: {', '.join(sorted(ALLOWED_SCRIPTS))}")
        return

    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"[RUNNER] Script não encontrado: {script_path}")
        return

    cmd = [sys.executable, script_path] + parts[1:]

    # Resolver caminhos relativos passados como argumentos
    # (ex: --text cap01.md → procurar no diretório pai dos scripts)
    project_root = os.path.dirname(SCRIPTS_DIR)
    adjusted_cmd = []
    for i, arg in enumerate(cmd):
        if i > 1 and not arg.startswith("--") and not arg.startswith("-"):
            # Possível path — tentar resolver
            candidate = os.path.join(project_root, arg)
            if os.path.exists(candidate) and not os.path.exists(arg):
                adjusted_cmd.append(candidate)
                continue
        adjusted_cmd.append(arg)

    print(f"\n[RUNNER] Executando: {' '.join(parts)}")
    print("─" * 60)

    try:
        result = subprocess.run(
            adjusted_cmd,
            capture_output=True,
            text=True,
            cwd=project_root,
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"[STDERR] {result.stderr[:300]}", file=sys.stderr)
        print("─" * 60)
        print(f"[RUNNER] Concluído com código {result.returncode}")
    except Exception as e:
        print(f"[RUNNER] Erro ao executar: {e}")


def interactive_mode():
    print("Editora Ebook — Runner Interativo")
    print("Cole um bloco [SCRIPT: ...] ou o comando diretamente.")
    print("Digite 'sair' para encerrar.\n")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if line.lower() in ("sair", "exit", "quit"):
            break
        if not line:
            continue
        command = parse_script_block(line)
        run_command(command)


def main():
    parser = argparse.ArgumentParser(description="Runner da Editora Ebook")
    parser.add_argument("command", nargs="?",
                        help="Comando a executar (ex: 'scorer.py --consolidate')")
    parser.add_argument("--pipe", action="store_true",
                        help="Ler bloco [SCRIPT:] do stdin")
    parser.add_argument("--interactive", action="store_true",
                        help="Modo interativo")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.pipe:
        text = sys.stdin.read()
        command = parse_script_block(text)
        run_command(command)
    elif args.command:
        command = parse_script_block(args.command)
        run_command(command)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

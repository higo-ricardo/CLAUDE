#!/usr/bin/env python3
"""
cli.py — Interface de linha de comando para o Agente da Editora Ebook v2.

Uso:
  # Executar objetivo direto (com streaming de output)
  python scripts/cli.py "Escreva o Capítulo 3 sobre gestão do tempo"

  # Modo interativo (sessão contínua)
  python scripts/cli.py --interactive

  # Sem streaming (aguarda resposta completa)
  python scripts/cli.py --no-stream "Revise o Capítulo 1"

  # Ver estado atual do projeto
  python scripts/cli.py --status

  # Ver histórico de versões
  python scripts/cli.py --history

  # Ver decisões editoriais
  python scripts/cli.py --decisions

  # Silencioso — só o output final, sem logs de tool calls
  python scripts/cli.py --quiet "Gere o blurb do projeto"

Exemplos de objetivos:
  "Escreva o Capítulo 2 sobre produtividade para iniciantes, tom conversacional"
  "Revise o Capítulo 1 e corrija problemas de voz passiva e legibilidade"
  "Verifique a coerência de todo o manuscrito e gere relatório"
  "Exporte o manuscrito para EPUB"
  "Gere metadados e checklist de publicação para KDP"
  "Mostre o estado atual do projeto com scorecard por capítulo"
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR  = Path(__file__).parent
PROJECT_ROOT = SCRIPTS_DIR.parent

# Garantir que scripts/ está no path para importar agent
sys.path.insert(0, str(SCRIPTS_DIR))


def check_environment() -> bool:
    """Verifica pré-requisitos antes de iniciar o agente."""
    ok = True

    # API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY não definida.")
        print("   Export: export ANTHROPIC_API_KEY='sua-chave'")
        ok = False

    # SDK
    try:
        import anthropic
    except ImportError:
        print("❌ SDK Anthropic não instalado.")
        print("   Instale: pip install anthropic")
        ok = False

    # data/
    data_dir = PROJECT_ROOT / "data"
    if not data_dir.exists():
        print("⚠️  Diretório data/ não encontrado. Criando...")
        data_dir.mkdir(parents=True)

    return ok


def run_script(command: str) -> str:
    """Executa um script via runner.py e retorna output."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "runner.py"), command],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT),
    )
    return result.stdout.strip()


def cmd_status():
    """Mostra estado atual do projeto."""
    print("\n" + "═" * 60)
    print("📋  ESTADO DO PROJETO")
    print("═" * 60)
    print(run_script("versioner.py --action state"))
    print("\n" + "─" * 60)
    print(run_script("scorer.py --consolidate"))
    print("\n" + "─" * 60)
    print(run_script("decisions.py --action list"))


def cmd_history():
    """Mostra histórico de versões."""
    print("\n" + "═" * 60)
    print("📜  HISTÓRICO DE VERSÕES")
    print("═" * 60)
    print(run_script("versioner.py --action history"))


def cmd_decisions():
    """Mostra decisões editoriais."""
    print("\n" + "═" * 60)
    print("📌  DECISÕES EDITORIAIS")
    print("═" * 60)
    print(run_script("decisions.py --action list"))
    print("\n" + "─" * 60)
    print(run_script("decisions.py --action pending"))


def run_agent_streaming(objetivo: str, verbose: bool = True):
    """Executa o agente com streaming de texto."""
    from agent import EditoraAgent

    agent = EditoraAgent(verbose=verbose)
    print("\n" + "═" * 60)
    print(f"▶  {objetivo}")
    print("═" * 60 + "\n")

    full = []
    for chunk in agent.stream(objetivo):
        print(chunk, end="", flush=True)
        full.append(chunk)
    print()
    return "".join(full)


def run_agent_sync(objetivo: str, verbose: bool = True):
    """Executa o agente de forma síncrona (aguarda resposta completa)."""
    from agent import EditoraAgent

    agent = EditoraAgent(verbose=verbose)
    result = agent.run(objetivo)
    print("\n" + "═" * 60)
    print(result)
    return result


def interactive_mode(verbose: bool = True):
    """Modo interativo: sessão contínua com o agente."""
    from agent import EditoraAgent

    print("\n" + "═" * 60)
    print("📚  Editora Ebook v2 — Agente Interativo")
    print("═" * 60)
    print("Digite seu objetivo em linguagem natural.")
    print("Comandos especiais: /status  /histórico  /decisões  /sair\n")

    agent = EditoraAgent(verbose=verbose)

    while True:
        try:
            raw = input("▶ ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            break

        if not raw:
            continue

        # Comandos de atalho
        if raw in ("/sair", "/exit", "exit", "quit"):
            print("Encerrando.")
            break
        elif raw in ("/status", "/estado"):
            cmd_status()
            continue
        elif raw in ("/histórico", "/historico"):
            cmd_history()
            continue
        elif raw in ("/decisões", "/decisoes"):
            cmd_decisions()
            continue
        elif raw.startswith("/"):
            print(f"Comando desconhecido: {raw}")
            continue

        # Executar objetivo com streaming
        print()
        full = []
        try:
            for chunk in agent.stream(raw):
                print(chunk, end="", flush=True)
                full.append(chunk)
            print("\n")
        except KeyboardInterrupt:
            print("\n[interrompido]")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CLI do Agente da Editora Ebook v2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "objetivo",
        nargs="?",
        help="Objetivo em linguagem natural para o agente executar",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Modo interativo (sessão contínua)",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Desativar streaming — aguardar resposta completa",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suprimir logs de tool calls (só output final)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Mostrar estado atual do projeto e sair",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Mostrar histórico de versões e sair",
    )
    parser.add_argument(
        "--decisions",
        action="store_true",
        help="Mostrar decisões editoriais e sair",
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-6",
        help="Modelo Anthropic a usar (default: claude-sonnet-4-6)",
    )

    args = parser.parse_args()

    # Comandos que não precisam da API
    if args.status:
        cmd_status()
        return
    if args.history:
        cmd_history()
        return
    if args.decisions:
        cmd_decisions()
        return

    # Verificar ambiente antes de chamar a API
    if not check_environment():
        sys.exit(1)

    verbose = not args.quiet

    if args.interactive:
        interactive_mode(verbose=verbose)
        return

    if args.objetivo:
        if args.no_stream:
            run_agent_sync(args.objetivo, verbose=verbose)
        else:
            run_agent_streaming(args.objetivo, verbose=verbose)
        return

    # Nenhum argumento útil — mostrar help
    parser.print_help()


if __name__ == "__main__":
    main()

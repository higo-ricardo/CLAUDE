#!/usr/bin/env python3
"""
exporter.py — Exportação determinística de Markdown para formatos finais.
Requer pandoc instalado. Detecta ausência e instrui instalação.

Uso:
  python exporter.py --input ebook.md --format epub --cover capa.jpg
  python exporter.py --input ebook.md --format docx --template template.docx
  python exporter.py --input ebook.md --format pdf
  python exporter.py --check        # verifica se pandoc está disponível
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")


def check_pandoc():
    return shutil.which("pandoc") is not None


def load_project():
    path = os.path.join(DATA_DIR, "project.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def build_metadata_args(project):
    """Constrói argumentos --metadata para pandoc a partir de project.json."""
    args = []
    if project.get("title"):
        args += ["--metadata", f'title={project["title"]}']
    if project.get("author"):
        args += ["--metadata", f'author={project["author"]}']
    if project.get("language"):
        args += ["--metadata", f'lang={project.get("language_code", "pt-BR")}']
    return args


def export_epub(input_file, output_file, cover, project):
    if not check_pandoc():
        _pandoc_missing()
        return False

    cmd = ["pandoc", input_file, "-o", output_file, "--toc", "--toc-depth=2"]
    cmd += build_metadata_args(project)
    if cover and os.path.exists(cover):
        cmd += [f"--epub-cover-image={cover}"]

    return _run(cmd, output_file)


def export_docx(input_file, output_file, template, project):
    if not check_pandoc():
        _pandoc_missing()
        return False

    cmd = ["pandoc", input_file, "-o", output_file]
    cmd += build_metadata_args(project)
    if template and os.path.exists(template):
        cmd += [f"--reference-doc={template}"]

    return _run(cmd, output_file)


def export_pdf(input_file, output_file, project):
    if not check_pandoc():
        _pandoc_missing()
        return False

    # Tentar weasyprint primeiro, fallback para xelatex
    engines = ["weasyprint", "xelatex", "pdflatex"]
    for engine in engines:
        if shutil.which(engine):
            cmd = ["pandoc", input_file, "-o", output_file,
                   f"--pdf-engine={engine}", "--toc", "--toc-depth=2"]
            cmd += build_metadata_args(project)
            if _run(cmd, output_file):
                return True
    print("❌ Nenhum motor PDF disponível (weasyprint, xelatex, pdflatex).")
    print("   Instale: pip install weasyprint  ou  sudo apt install texlive")
    return False


def _run(cmd, output_file):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
            print(f"✅ Exportado: {output_file} ({size:,} bytes)")
            print(f"   Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            return True
        else:
            print(f"❌ Erro na exportação:")
            print(result.stderr[:500])
            return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout na exportação (>120s). Arquivo muito grande?")
        return False
    except FileNotFoundError:
        print(f"❌ Comando não encontrado: {cmd[0]}")
        return False


def _pandoc_missing():
    print("❌ pandoc não encontrado.")
    print("   Instale em: https://pandoc.org/installing.html")
    print("   Ubuntu/Debian: sudo apt install pandoc")
    print("   macOS: brew install pandoc")
    print("   Windows: winget install JohnMacFarlane.Pandoc")


def main():
    parser = argparse.ArgumentParser(description="Exporter da Editora Ebook")
    parser.add_argument("--input", help="Arquivo .md de entrada")
    parser.add_argument("--format", choices=["epub", "docx", "pdf"])
    parser.add_argument("--output", help="Nome do arquivo de saída (opcional)")
    parser.add_argument("--cover", help="Imagem de capa (para EPUB)")
    parser.add_argument("--template", help="Template .docx de referência")
    parser.add_argument("--check", action="store_true",
                        help="Verificar se pandoc está disponível")
    args = parser.parse_args()

    if args.check:
        if check_pandoc():
            result = subprocess.run(["pandoc", "--version"],
                                    capture_output=True, text=True)
            print("✅ pandoc disponível:")
            print(result.stdout.splitlines()[0])
        else:
            _pandoc_missing()
        return

    if not args.input or not args.format:
        parser.error("--input e --format são obrigatórios")

    if not os.path.exists(args.input):
        print(f"❌ Arquivo não encontrado: {args.input}")
        sys.exit(1)

    base = os.path.splitext(args.input)[0]
    output = args.output or f"{base}.{args.format}"
    project = load_project()

    if args.format == "epub":
        export_epub(args.input, output, args.cover, project)
    elif args.format == "docx":
        export_docx(args.input, output, args.template, project)
    elif args.format == "pdf":
        export_pdf(args.input, output, project)


if __name__ == "__main__":
    main()

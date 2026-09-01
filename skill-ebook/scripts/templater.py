#!/usr/bin/env python3
"""
templater.py — Preenchimento determinístico de templates Markdown.
Substitui marcadores [CAMPO] pelos valores fornecidos via JSON.

Templates disponíveis:
  capitulo-nonfiction   capítulo-ficção   conclusao
  blurb                 rosto             sumario

Uso:
  python templater.py --template capitulo-nonfiction \
         --fields '{"N": "3", "Título": "Gestão do Tempo"}' \
         --output cap03.md

  python templater.py --template rosto \
         --fields-file project.json --output rosto.md

  python templater.py --list   # lista todos os templates disponíveis
"""

import argparse
import json
import os
import re
from datetime import datetime

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../templates")
DATA_DIR      = os.path.join(os.path.dirname(__file__), "../data")

BUILTIN_TEMPLATES = {
    "capitulo-nonfiction": """\
## Capítulo {N}: {Título}

[GANCHO — 1-2 parágrafos]

[INTRODUÇÃO DO CAPÍTULO — 1 parágrafo]

### {Seção 1}
[Conteúdo...]

### {Seção 2}
[Conteúdo...]

> **💡 Dica:** [texto]

### {Seção 3 — Aplicação Prática}
[Conteúdo...]

---

**Em resumo:** [síntese em 2-3 frases]

*No próximo capítulo, você vai descobrir...*
""",

    "capitulo-ficcao": """\
## Capítulo {N}

[Cena de abertura — ação ou diálogo]

[Desenvolvimento — conflito, tensão, revelação]

[Fechamento — cliffhanger ou respirada antes do próximo]
""",

    "conclusao": """\
# Conclusão

[Retomar a promessa da introdução]

[Síntese da jornada — o que o leitor aprendeu/viveu]

[Transformação — onde o leitor está agora vs. onde estava]

[Próximos passos concretos]

[Mensagem final do autor — pessoal, memorável]

---

**Obrigado por chegar até aqui.**

[CTA — lista de e-mail / próximo livro / comunidade]
""",

    "blurb": """\
[Pergunta ou afirmação de dor — 1 frase]

[Promessa do livro — 2 frases]

[O que está dentro — 2-3 bullets rápidos]
• ...
• ...
• ...

[Quem é o autor — 1 frase de credencial]

[CTA — 1 frase]
""",

    "rosto": """\
---

# {Título}
## {Subtítulo}

**{Autor}**

---

*Publicação Independente*
*{Cidade}, {Ano}*

© {Ano} {Autor}
Todos os direitos reservados.

Nenhuma parte desta publicação pode ser reproduzida, distribuída ou
transmitida por qualquer forma ou meio, sem permissão prévia por escrito
do autor.

**Contato:** {Contato}

---
""",

    "sumario": """\
# SUMÁRIO — {Título}

## Introdução
- Propósito do livro
- Para quem é este livro
- Como usar este livro

## PARTE 1: {Parte 1}

### Capítulo 1: [TÍTULO]
*Objetivo: ...*
Tópicos: tópico A, tópico B, tópico C

### Capítulo 2: [TÍTULO]
*Objetivo: ...*

## PARTE 2: {Parte 2}

## Conclusão
- Síntese
- Próximos passos
- Chamada para ação
""",
}


def fill_template(template_str, fields):
    """Substitui {Campo} pelos valores do dicionário fields."""
    result = template_str

    # Substituir marcadores {Campo}
    for key, value in fields.items():
        result = result.replace(f"{{{key}}}", str(value))

    # Marcar campos não preenchidos
    unfilled = re.findall(r'\{([^}]+)\}', result)
    for field in set(unfilled):
        result = result.replace(f"{{{field}}}", f"[PENDENTE: {field}]")

    return result


def load_fields_from_project(project_path):
    """Extrai campos relevantes de project.json."""
    if not os.path.exists(project_path):
        return {}
    with open(project_path, "r", encoding="utf-8") as f:
        p = json.load(f)
    return {
        "Título": p.get("title", ""),
        "Subtítulo": p.get("subtitle", ""),
        "Autor": p.get("author", ""),
        "Ano": str(datetime.now().year),
        "Cidade": p.get("city", ""),
        "Contato": p.get("contact", ""),
        "Parte 1": p.get("part1_name", ""),
        "Parte 2": p.get("part2_name", ""),
    }


def main():
    parser = argparse.ArgumentParser(description="Templater da Editora Ebook")
    parser.add_argument("--template", help="Nome do template")
    parser.add_argument("--fields", help="JSON inline com campos a preencher")
    parser.add_argument("--fields-file", help="Arquivo JSON ou project.json com campos")
    parser.add_argument("--output", help="Arquivo .md de saída")
    parser.add_argument("--list", action="store_true", help="Listar templates disponíveis")
    args = parser.parse_args()

    if args.list:
        print("## Templates disponíveis\n")
        for name in BUILTIN_TEMPLATES:
            print(f"  {name}")
        # Checar templates customizados em /templates/
        if os.path.exists(TEMPLATES_DIR):
            for f in os.listdir(TEMPLATES_DIR):
                if f.endswith(".md"):
                    print(f"  {f} (arquivo externo)")
        return

    if not args.template:
        parser.error("--template é obrigatório")

    # Carregar template
    if args.template in BUILTIN_TEMPLATES:
        template_str = BUILTIN_TEMPLATES[args.template]
    else:
        # Tentar carregar de arquivo externo
        tpl_path = os.path.join(TEMPLATES_DIR, f"{args.template}.md")
        if not os.path.exists(tpl_path):
            print(f"Template '{args.template}' não encontrado.")
            print("Use --list para ver os disponíveis.")
            return
        with open(tpl_path, "r", encoding="utf-8") as f:
            template_str = f.read()

    # Carregar campos
    fields = {}
    if args.fields_file:
        if "project.json" in args.fields_file:
            fields = load_fields_from_project(args.fields_file)
        else:
            with open(args.fields_file, "r", encoding="utf-8") as f:
                fields.update(json.load(f))
    if args.fields:
        fields.update(json.loads(args.fields))

    # Preencher e salvar
    result = fill_template(template_str, fields)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"✅ Template '{args.template}' preenchido: {args.output}")
        pendentes = re.findall(r'\[PENDENTE: ([^\]]+)\]', result)
        if pendentes:
            print(f"   ⚠️  Campos pendentes: {', '.join(set(pendentes))}")
    else:
        print(result)


if __name__ == "__main__":
    main()

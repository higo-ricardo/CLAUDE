#!/usr/bin/env python3
"""
text_preprocessor.py
====================
Pré-processamento determinístico do texto antes de enviar ao LLM.

Responsabilidades:
  - Detectar elementos não textuais (tabelas, listas, notas, legendas, versos)
  - Adaptar formato numérico EN → PT-BR (decimais, milhares, datas)
  - Detectar calques proibidos no texto traduzido
  - Limpar artefatos de OCR (hifenização incorreta, caracteres confusos)
  - Produzir relatório estruturado para o LLM consumir

Uso:
  python text_preprocessor.py detect   --text-file cap1.txt
  python text_preprocessor.py calques  --text-file trad_cap1.txt
  python text_preprocessor.py numbers  --text-file cap1.txt [--dry-run]
  python text_preprocessor.py ocr      --text-file scan_cap1.txt [--dry-run]
  python text_preprocessor.py prepare  --text-file cap1.txt [--fix]
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Definições de padrões
# ---------------------------------------------------------------------------

# --- Elementos não textuais ---

RE_TABLE_ROW    = re.compile(r"^\s*\|.+\|", re.MULTILINE)
RE_TABLE_SEP    = re.compile(r"^\s*\|[-:| ]+\|", re.MULTILINE)
RE_UNORDERED    = re.compile(r"^\s*[-*+]\s+\S", re.MULTILINE)
RE_ORDERED      = re.compile(r"^\s*\d+[.)]\s+\S", re.MULTILINE)
RE_FOOTNOTE_REF = re.compile(r"\[\^(\w+)\]")
RE_FOOTNOTE_DEF = re.compile(r"^\[\^(\w+)\]:\s+.+", re.MULTILINE)
RE_FIGURE_LABEL = re.compile(r"\b(Figure|Fig\.|Table|Chart|Illustration|Diagram)\s+\d+", re.IGNORECASE)
RE_CAPTION      = re.compile(r"^(Figure|Fig\.|Table|Tbl\.|Chart|Illustration)\s+\d+[\.:]\s+.+",
                              re.IGNORECASE | re.MULTILINE)
RE_EPIGRAPH     = re.compile(r"^>\s*.+", re.MULTILINE)          # blockquote usado como epígrafe
RE_HEADING      = re.compile(r"^#{1,6}\s+.+", re.MULTILINE)
RE_CODE_BLOCK   = re.compile(r"```[\s\S]+?```", re.MULTILINE)
RE_INLINE_CODE  = re.compile(r"`[^`]+`")
RE_VERSE        = re.compile(                                   # linhas curtas intercaladas
    r"(?:^.{3,60}\n){3,}",                                     # 3+ linhas de até 60 chars
    re.MULTILINE,
)

# --- Formatos numéricos EN → PT-BR ---

# decimal: 3.14 → 3,14  (não confundir com separadores de milhar)
RE_DECIMAL      = re.compile(r"(\d+)\.(\d{1,2})\b")
# milhar: 1,000 → 1.000
RE_THOUSAND     = re.compile(r"(\d{1,3}),(\d{3})(?!\d)")
# data MM/DD/YYYY → DD/MM/YYYY
RE_DATE_US      = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
# temperatura: 98°F → já coberto no adaptacao-cultural.md (não converter aqui)

# --- Calques proibidos (PT-BR) ---
# Formato: (padrão regex, substituição sugerida, explicação)
CALQUES = [
    (re.compile(r"\bfazer sentido\b",          re.IGNORECASE), "entender / fazer sentido de",       "calque de 'make sense'"),
    (re.compile(r"\bter um bom tempo\b",        re.IGNORECASE), "se divertir / passar bem",          "calque de 'have a good time'"),
    (re.compile(r"\bestar de volta\b",          re.IGNORECASE), "voltar / ter retornado",            "calque de 'be back'"),
    (re.compile(r"\bno final do dia\b",         re.IGNORECASE), "no fim das contas",                 "calque de 'at the end of the day'"),
    (re.compile(r"\bassumir que\b",             re.IGNORECASE), "supor que / presumir que",          "calque de 'assume' (no sentido cognitivo)"),
    (re.compile(r"\bmover on\b",                re.IGNORECASE), "seguir em frente",                  "calque de 'move on'"),
    (re.compile(r"\bé o que é\b",               re.IGNORECASE), "[adaptar conforme contexto]",       "calque de 'it is what it is'"),
    (re.compile(r"\bna mesma página\b",         re.IGNORECASE), "alinhados / em acordo",             "calque de 'on the same page'"),
    (re.compile(r"\bpegar um drink\b",          re.IGNORECASE), "tomar uma bebida / tomar um drinque", "calque de 'grab a drink'"),
    (re.compile(r"\btime\b(?! [a-záéíóú])",    re.IGNORECASE), "equipe / time [verificar contexto]","'time' pode ser empréstimo aceitável ou calque"),
    (re.compile(r"\bcheck(?:ar|ei|ou|amos)\b", re.IGNORECASE), "verificar / conferir",              "calque de 'check'"),
    (re.compile(r"\bcomeç(?:ar|ou) a fazer sentido\b", re.IGNORECASE), "começou a fazer sentido / começou a ficar claro", "calque composto"),
    (re.compile(r"\bdar um passo para trás\b",  re.IGNORECASE), "recuar / refletir com distância",  "calque de 'step back'"),
    (re.compile(r"\bde qualquer forma\b",       re.IGNORECASE), "de qualquer maneira / enfim [OK se informal]", "pode ser aceitável"),
    (re.compile(r"\bfazer o melhor\b",          re.IGNORECASE), "dar o melhor de si",               "calque de 'do one's best'"),
    (re.compile(r"\bpushing through\b",         re.IGNORECASE), "persistir / continuar apesar de",  "calque não traduzido"),
    (re.compile(r"\bworkshop(?:ar|ei|ou)\b",   re.IGNORECASE), "revisar em grupo / trabalhar em",  "calque de 'workshop' como verbo"),
]

# --- Artefatos de OCR ---
OCR_FIXES = [
    # Hifenização de fim de linha (word- \nword → word)
    (re.compile(r"(\w+)-\s*\n\s*(\w+)"),              r"\1\2"),
    # l confundido com 1 no início de palavra
    (re.compile(r"\b1([a-z]{2,})\b"),                  r"l\1"),
    # 0 confundido com O em palavras
    (re.compile(r"\b([A-Z])0([a-z])\b"),               r"\1O\2"),
    # Espaços duplos
    (re.compile(r"  +"),                               r" "),
    # Travessão partido (- - ou - -)
    (re.compile(r"\s-\s-\s"),                          r" — "),
    # Aspas tipográficas inconsistentes
    (re.compile(r"\'\'"),                              r'"'),
    (re.compile(r"``"),                                r'"'),
    # Ponto e vírgula colados
    (re.compile(r"(\w)([;:])(\w)"),                    r"\1\2 \3"),
    # Quebras de linha múltiplas (> 2)
    (re.compile(r"\n{3,}"),                            r"\n\n"),
]

# ---------------------------------------------------------------------------
# Detecção de elementos
# ---------------------------------------------------------------------------

ElementReport = dict  # type alias para clareza

def detect_elements(text: str) -> list[ElementReport]:
    """
    Detecta todos os elementos não textuais presentes no texto.
    Retorna lista de dicts com tipo, posição e protocolo a aplicar.
    """
    found = []

    def _add(type_: str, matches, protocol: str, note: str = ""):
        for m in matches:
            found.append({
                "type":     type_,
                "position": m.start(),
                "preview":  m.group(0)[:60].replace("\n", "↵"),
                "protocol": protocol,
                "note":     note,
            })

    # Tabelas
    table_rows = list(RE_TABLE_ROW.finditer(text))
    if table_rows:
        _add("TABELA", table_rows[:1],
             "elementos-nao-textuais.md §2",
             f"{len(table_rows)} linhas de tabela detectadas")

    # Listas
    unordered = list(RE_UNORDERED.finditer(text))
    if unordered:
        _add("LISTA_NAO_ORDENADA", unordered[:1],
             "elementos-nao-textuais.md §3",
             f"{len(unordered)} itens")

    ordered = list(RE_ORDERED.finditer(text))
    if ordered:
        _add("LISTA_ORDENADA", ordered[:1],
             "elementos-nao-textuais.md §3",
             f"{len(ordered)} itens")

    # Notas de rodapé
    fn_refs = list(RE_FOOTNOTE_REF.finditer(text))
    fn_defs = list(RE_FOOTNOTE_DEF.finditer(text))
    if fn_refs or fn_defs:
        _add("NOTA_DE_RODAPE", (fn_refs + fn_defs)[:1],
             "elementos-nao-textuais.md §4",
             f"{len(fn_refs)} referências, {len(fn_defs)} definições")

    # Legendas
    captions = list(RE_CAPTION.finditer(text))
    if captions:
        _add("LEGENDA", captions[:1],
             "elementos-nao-textuais.md §5",
             f"{len(captions)} legendas")

    # Epígrafes
    epigraphs = list(RE_EPIGRAPH.finditer(text))
    if epigraphs:
        _add("EPIGRAFE", epigraphs[:1],
             "elementos-nao-textuais.md §6")

    # Títulos/cabeçalhos
    headings = list(RE_HEADING.finditer(text))
    if headings:
        _add("TITULO", headings[:1],
             "preservar hierarquia de títulos",
             f"{len(headings)} títulos")

    # Blocos de código
    code_blocks = list(RE_CODE_BLOCK.finditer(text))
    if code_blocks:
        _add("BLOCO_CODIGO", code_blocks[:1],
             "NÃO TRADUZIR — manter exatamente como está",
             f"{len(code_blocks)} blocos")

    # Verso (heurística)
    verse_matches = list(RE_VERSE.finditer(text))
    if verse_matches:
        _add("VERSO_POSSIVEL", verse_matches[:1],
             "elementos-nao-textuais.md §7 — definir prioridade com usuário",
             "verificar se é verso ou lista curta")

    return sorted(found, key=lambda x: x["position"])


def format_detection_report(elements: list[ElementReport], text: str) -> str:
    if not elements:
        return "✅ Nenhum elemento não textual detectado. Texto corrido puro.\n"

    lines = [
        f"🗂️  ELEMENTOS NÃO TEXTUAIS DETECTADOS — {len(elements)} tipo(s)\n",
        f"{'─'*60}",
    ]
    for el in elements:
        lines += [
            f"  Tipo:      {el['type']}",
            f"  Protocolo: {el['protocol']}",
            f"  Preview:   \"{el['preview']}\"",
        ]
        if el["note"]:
            lines.append(f"  Nota:      {el['note']}")
        lines.append("")

    lines.append(
        "⚠️  Carregue o módulo 'elementos-nao-textuais.md' antes de traduzir este trecho."
    )
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Detecção de calques
# ---------------------------------------------------------------------------

def detect_calques(text: str) -> list[dict]:
    """Varre o texto traduzido em busca de calques da lista proibida."""
    hits = []
    for pattern, suggestion, explanation in CALQUES:
        for m in pattern.finditer(text):
            # Contexto: 40 chars antes e depois
            start = max(0, m.start() - 40)
            end   = min(len(text), m.end() + 40)
            hits.append({
                "match":       m.group(0),
                "position":    m.start(),
                "suggestion":  suggestion,
                "explanation": explanation,
                "context":     "..." + text[start:end].replace("\n", " ") + "...",
            })
    return hits


def format_calques_report(hits: list[dict]) -> str:
    if not hits:
        return "✅ Nenhum calque proibido detectado.\n"

    lines = [
        f"⚠️  CALQUES DETECTADOS — {len(hits)} ocorrência(s)\n",
        f"{'─'*60}",
    ]
    for h in hits:
        lines += [
            f"  Calque:    \"{h['match']}\"",
            f"  Sugestão:  {h['suggestion']}",
            f"  Motivo:    {h['explanation']}",
            f"  Contexto:  {h['context']}",
            "",
        ]
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Adaptação de números
# ---------------------------------------------------------------------------

def fix_number_format(text: str) -> tuple[str, list[str]]:
    """
    Adapta formatos numéricos de EN para PT-BR.
    Retorna (texto_adaptado, lista_de_mudanças).
    
    ATENÇÃO: aplicar apenas ao texto traduzido, não ao original.
    Não converte temperaturas (coberto por adaptacao-cultural.md).
    """
    changes = []
    result = text

    # Datas MM/DD/YYYY → DD/MM/YYYY (primeiro, antes de outras conversões)
    def _fix_date(m):
        month, day, year = m.group(1), m.group(2), m.group(3)
        new = f"{day}/{month}/{year}"
        changes.append(f"Data: {m.group(0)} → {new}")
        return new

    result = RE_DATE_US.sub(_fix_date, result)

    # Decimal: 3.14 → 3,14  (antes do milhar para não conflitar)
    # Só converte quando há 1-2 dígitos após o ponto (3 dígitos = separador de milhar)
    def _fix_decimal(m):
        new = f"{m.group(1)},{m.group(2)}"
        changes.append(f"Decimal: {m.group(0)} → {new}")
        return new

    result = RE_DECIMAL.sub(_fix_decimal, result)

    # Milhar: 1,000 → 1.000 (depois do decimal)
    def _fix_thousand(m):
        new = f"{m.group(1)}.{m.group(2)}"
        changes.append(f"Milhar: {m.group(0)} → {new}")
        return new

    result = RE_THOUSAND.sub(_fix_thousand, result)

    return result, changes

# ---------------------------------------------------------------------------
# Limpeza de OCR
# ---------------------------------------------------------------------------

def clean_ocr(text: str) -> tuple[str, list[str]]:
    """Aplica correções heurísticas de artefatos de OCR."""
    changes = []
    result = text

    for pattern, replacement in OCR_FIXES:
        new = pattern.sub(replacement, result)
        if new != result:
            count = len(pattern.findall(result))
            changes.append(f"Padrão corrigido ({count}x): {pattern.pattern[:40]}")
            result = new

    return result, changes

# ---------------------------------------------------------------------------
# Prepare: relatório completo pré-tradução
# ---------------------------------------------------------------------------

def prepare(text: str, fix: bool = False) -> dict:
    """
    Executa todos os pré-processamentos e retorna um relatório completo.
    Se fix=True, aplica as correções determinísticas no texto.
    """
    result = {
        "original_words":  len(text.split()),
        "elements":        [],
        "calques":         [],
        "number_changes":  [],
        "ocr_changes":     [],
        "processed_text":  text,
        "needs_attention": False,
    }

    # 1. Detectar elementos não textuais
    result["elements"] = detect_elements(text)

    # 2. OCR
    cleaned, ocr_changes = clean_ocr(text)
    result["ocr_changes"] = ocr_changes
    if fix:
        result["processed_text"] = cleaned

    # 3. Números (aplicar no texto já limpo)
    if fix:
        fixed, num_changes = fix_number_format(result["processed_text"])
        result["processed_text"] = fixed
        result["number_changes"] = num_changes

    # 4. Calques (verificar no texto já tratado)
    result["calques"] = detect_calques(result["processed_text"])

    result["needs_attention"] = bool(
        result["elements"] or result["calques"]
        or result["ocr_changes"] or result["number_changes"]
    )
    return result


def format_prepare_report(r: dict) -> str:
    lines = [
        "╔══════════════════════════════════════════════════════════╗",
        "║        PRÉ-PROCESSAMENTO — RELATÓRIO COMPLETO           ║",
        "╚══════════════════════════════════════════════════════════╝",
        f"  Palavras no texto:       {r['original_words']}",
        f"  Elementos não textuais:  {len(r['elements'])}",
        f"  Calques detectados:      {len(r['calques'])}",
        f"  Correções OCR:           {len(r['ocr_changes'])}",
        f"  Adaptações numéricas:    {len(r['number_changes'])}",
        f"  Requer atenção:          {'⚠️  SIM' if r['needs_attention'] else '✅ Não'}",
        "",
    ]

    if r["elements"]:
        lines += ["─── ELEMENTOS NÃO TEXTUAIS ──────────────────────────────", ""]
        lines.append(format_detection_report(r["elements"], ""))

    if r["ocr_changes"]:
        lines += ["─── CORREÇÕES OCR ───────────────────────────────────────", ""]
        for c in r["ocr_changes"]:
            lines.append(f"  ✓ {c}")
        lines.append("")

    if r["number_changes"]:
        lines += ["─── ADAPTAÇÕES NUMÉRICAS ────────────────────────────────", ""]
        for c in r["number_changes"]:
            lines.append(f"  ✓ {c}")
        lines.append("")

    if r["calques"]:
        lines += ["─── CALQUES ─────────────────────────────────────────────", ""]
        lines.append(format_calques_report(r["calques"]))

    if not r["needs_attention"]:
        lines.append("✅ Texto limpo. Nenhuma intervenção necessária.")

    return "\n".join(lines)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_detect(args):
    text = Path(args.text_file).read_text(encoding="utf-8")
    elements = detect_elements(text)
    print(format_detection_report(elements, text))


def cmd_calques(args):
    text = Path(args.text_file).read_text(encoding="utf-8")
    hits = detect_calques(text)
    print(format_calques_report(hits))


def cmd_numbers(args):
    text = Path(args.text_file).read_text(encoding="utf-8")
    fixed, changes = fix_number_format(text)
    if not changes:
        print("✅ Nenhuma adaptação numérica necessária.")
        return
    for c in changes:
        print(f"  {c}")
    if not args.dry_run:
        out = Path(args.text_file).with_suffix(".fixed.txt")
        out.write_text(fixed, encoding="utf-8")
        print(f"\n[OK] Salvo em: {out}")


def cmd_ocr(args):
    text = Path(args.text_file).read_text(encoding="utf-8")
    cleaned, changes = clean_ocr(text)
    if not changes:
        print("✅ Nenhum artefato de OCR detectado.")
        return
    for c in changes:
        print(f"  {c}")
    if not args.dry_run:
        out = Path(args.text_file).with_suffix(".cleaned.txt")
        out.write_text(cleaned, encoding="utf-8")
        print(f"\n[OK] Salvo em: {out}")


def cmd_prepare(args):
    text = Path(args.text_file).read_text(encoding="utf-8")
    result = prepare(text, fix=args.fix)
    print(format_prepare_report(result))

    if args.fix and result["processed_text"] != text:
        out = Path(args.text_file).with_suffix(".prepared.txt")
        out.write_text(result["processed_text"], encoding="utf-8")
        print(f"\n[OK] Texto processado salvo em: {out}")

    if result["needs_attention"]:
        sys.exit(2)  # exit 2 = atenção necessária, não erro fatal


def main():
    parser = argparse.ArgumentParser(
        description="Pré-processador de texto — skill tradutor-livros",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("detect", help="Detectar elementos não textuais")
    p.add_argument("--text-file", required=True)
    p.set_defaults(func=cmd_detect)

    p = sub.add_parser("calques", help="Detectar calques no texto traduzido")
    p.add_argument("--text-file", required=True)
    p.set_defaults(func=cmd_calques)

    p = sub.add_parser("numbers", help="Adaptar formato numérico EN → PT-BR")
    p.add_argument("--text-file", required=True)
    p.add_argument("--dry-run", action="store_true", help="Mostrar sem salvar")
    p.set_defaults(func=cmd_numbers)

    p = sub.add_parser("ocr", help="Limpar artefatos de OCR")
    p.add_argument("--text-file", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_ocr)

    p = sub.add_parser("prepare", help="Relatório completo de pré-processamento")
    p.add_argument("--text-file", required=True)
    p.add_argument("--fix", action="store_true",
                   help="Aplicar correções determinísticas (OCR + números)")
    p.set_defaults(func=cmd_prepare)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
checker-prequestionamento.py — Validador de prequestionamento e filtros de admissibilidade
para Recurso Especial (RES) e Recurso Extraordinário (REX).

Uso:
    python scripts/checker-prequestionamento.py --acordao data/acordao.pdf --tipo RES --alinea a --artigo "art. 14 CDC"
    python scripts/checker-prequestionamento.py --acordao acordao.txt --tipo REX --alinea a --artigo "art. 5º, XXXII, CF" --json-output data/checks/preq.json

Saída: JSON em stdout + arquivo opcional --json-output
Referências: fontes.md §3.1.2, roteamento.md §2-C, minutas-civeis.md RES/REX
"""
import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Permite importar constants.py do mesmo diretório
sys.path.insert(0, str(Path(__file__).parent))
try:
    from constants import FILTROS_ADMISSIBILIDADE, ALINEAS_RES, ALINEAS_REX, PRAZO_RECURSO_DIAS
except ImportError:
    FILTROS_ADMISSIBILIDADE = {}
    ALINEAS_RES = {"a": "105 III a", "b": "105 III b", "c": "105 III c"}
    ALINEAS_REX = {"a": "102 III a", "b": "102 III b", "c": "102 III c"}
    PRAZO_RECURSO_DIAS = 15


# ---------------------------------------------------------------------------
# Extração de texto
# ---------------------------------------------------------------------------
def extract_text(path: Path) -> str:
    """Extrai texto de .txt/.md/.pdf (tenta PyMuPDF, fallback para leitura direta)."""
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="replace")

    if suffix == ".pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(path))
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            if text.strip():
                return text
        except ImportError:
            pass
        except Exception as e:
            print(f"[aviso] PyMuPDF falhou ({e}), tentando leitura binária", file=sys.stderr)
        # fallback: tenta ler como texto (pode ser pdf textual simples)
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            raise RuntimeError(
                "Não foi possível extrair PDF. Instale PyMuPDF: pip install PyMuPDF"
            )
    # genérico
    return path.read_text(encoding="utf-8", errors="replace")


def segment_acordao(text: str) -> dict:
    """Segmenta acórdão em seções para distinguir VOTO/EMENTA vs RELATÓRIO."""
    upper = text.upper()
    sections = {"full": text, "voto": "", "ementa": "", "relatorio": ""}

    # Heurística simples por marcadores
    for marker, key in [("VOTO", "voto"), ("EMENTA", "ementa"), ("RELATÓRIO", "relatorio")]:
        idx = upper.find(marker)
        if idx != -1:
            # pega 8000 chars a partir do marcador
            sections[key] = text[idx: idx + 8000]
    # Se não achou segmentação, voto = full para não bloquear
    if not sections["voto"] and not sections["ementa"]:
        sections["voto"] = text
    return sections


# ---------------------------------------------------------------------------
# Normalização e busca de artigo
# ---------------------------------------------------------------------------
def normalize_artigo(artigo: str) -> list[str]:
    """
    Gera variantes de busca para um artigo.
    Ex: "art. 14, §1º, CDC" -> ["art. 14", "artigo 14", "14 CDC", "14 do CDC"]
    """
    artigo = artigo.strip()
    variants = [artigo]

    # extrai número principal
    m = re.search(r"(\d+)", artigo)
    if m:
        num = m.group(1)
        variants.append(f"art. {num}")
        variants.append(f"artigo {num}")
        variants.append(f"art. {num} do CDC")
        variants.append(f"art. {num} do Código de Defesa")
        if "CF" in artigo.upper() or "CONSTITU" in artigo.upper():
            variants.append(f"art. {num} da CF")
            variants.append(f"art. {num} da Constituição")

    # remove duplicatas preservando ordem
    seen = set()
    uniq = []
    for v in variants:
        low = v.lower()
        if low not in seen:
            seen.add(low)
            uniq.append(v)
    return uniq


def find_artigo_in_text(variants: list[str], sections: dict) -> dict:
    """
    Busca variantes no acórdão, priorizando VOTO/EMENTA.
    Retorna {encontrado, local, trecho, confianca}
    """
    # padrões: art. 14 com tolerância a espaços/pontuação
    for variant in variants:
        # escapa mas permite flexibilidade de pontuação
        base = re.escape(variant)
        # permite "art. 14" casar "art. 14, §1º"
        base = base.replace(r"\ ", r"\s*")
        pattern = re.compile(base, re.IGNORECASE)

        for loc in ["voto", "ementa", "full"]:
            text = sections.get(loc, "")
            if not text:
                continue
            m = pattern.search(text)
            if m:
                start = max(0, m.start() - 120)
                end = min(len(text), m.end() + 120)
                trecho = text[start:end].replace("\n", " ").strip()
                # confiança: voto/ementa = alta, full/relatório = média
                confianca = 0.92 if loc in ("voto", "ementa") else 0.65
                return {
                    "encontrado": True,
                    "local": loc,
                    "variante": variant,
                    "trecho": trecho,
                    "confianca": confianca,
                }

    return {"encontrado": False, "local": None, "variante": None, "trecho": None, "confianca": 0.0}


# ---------------------------------------------------------------------------
# Filtros de admissibilidade (heurísticas)
# ---------------------------------------------------------------------------
def check_filtros(text: str, tipo: str, alinea: str) -> dict:
    """Verifica Súmulas 5/7/83/126/279 de forma heurística (keywords)."""
    low = text.lower()
    filtros = {}

    # Súmula 7 / 279 — reexame de prova (bloqueia RES/REX)
    keywords_prova = ["reexame de prova", "revolver matéria fática", "conjunto probatório", "reapreciação da prova"]
    if tipo == "RES":
        hit = any(k in low for k in keywords_prova)
        filtros["sumula_7_stj"] = "alerta" if hit else "ok"
        filtros["sumula_7_detalhe"] = "Tese parece exigir reexame fático — RES incabível (Súmula 7)" if hit else "Sem indício de reexame fático"
    if tipo == "REX":
        hit = any(k in low for k in keywords_prova)
        filtros["sumula_279_stf"] = "alerta" if hit else "ok"

    # Súmula 5 — cláusula contratual (só RES)
    if tipo == "RES":
        hit5 = "cláusula contratual" in low or "interpretação de contrato" in low
        filtros["sumula_5_stj"] = "alerta" if hit5 else "ok"

    # Súmula 83 — divergência (só alínea c)
    if alinea == "c":
        filtros["sumula_83_stj"] = "verificar"
        filtros["sumula_83_detalhe"] = "Alínea c: é obrigatório verificar se paradigma tem tese divergente real (distinguishing)"
    else:
        filtros["sumula_83_stj"] = "n/a"

    # Súmula 126 — fundamentos duplos (heurística simples)
    has_const = "constituição" in low or "art. 5º" in low
    has_infra = "código civil" in low or "cdc" in low or "lei federal" in low
    if has_const and has_infra:
        filtros["sumula_126_stj"] = "alerta"
        filtros["sumula_126_detalhe"] = "Acórdão com fundamento constitucional + infraconstitucional — se for RES, exige REX simultâneo (Súmula 126)"
    else:
        filtros["sumula_126_stj"] = "ok"

    return filtros


# ---------------------------------------------------------------------------
# Prazo
# ---------------------------------------------------------------------------
def calcula_prazo(publicacao: str | None) -> dict:
    if not publicacao:
        return {"prazo_limite": None, "observacao": f"Prazo: {PRAZO_RECURSO_DIAS} dias corridos da publicação (art. 1.003, §5º, CPC). Informe --publicacao YYYY-MM-DD para cálculo exato."}
    try:
        dt = datetime.strptime(publicacao, "%Y-%m-%d")
        # CPC: dias corridos (não úteis) para RES/REX, mas muitos TJs contam úteis — alerta
        limite = dt + timedelta(days=PRAZO_RECURSO_DIAS)
        return {
            "publicacao": publicacao,
            "prazo_limite": limite.strftime("%Y-%m-%d"),
            "prazo_dias": PRAZO_RECURSO_DIAS,
            "observacao": "Art. 1.003, §5º, CPC — 15 dias corridos. Verifique se o TJ conta dias úteis (CPC/2015) ou corridos.",
        }
    except ValueError:
        return {"erro": "Formato de --publicacao inválido. Use YYYY-MM-DD"}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Checker de prequestionamento RES/REX")
    parser.add_argument("--acordao", required=True, help="Caminho para acórdão (.pdf/.txt/.md)")
    parser.add_argument("--tipo", required=True, choices=["RES", "REX"], help="Tipo de recurso")
    parser.add_argument("--alinea", required=True, choices=["a", "b", "c"], help="Alínea constitucional")
    parser.add_argument("--artigo", required=True, help='Artigo violado. Ex: "art. 14 CDC" ou "art. 5º, XXXII, CF"')
    parser.add_argument("--paradigma", help="Caminho para acórdão paradigma (obrigatório se alínea c)")
    parser.add_argument("--publicacao", help="Data de publicação do acórdão YYYY-MM-DD para cálculo de prazo")
    parser.add_argument("--json-output", help="Salvar JSON em arquivo (ex: data/checks/preq.json)")
    parser.add_argument("--verbose", action="store_true", help="Exibe trechos encontrados")
    args = parser.parse_args()

    # Validação alínea c
    if args.alinea == "c" and not args.paradigma:
        print("[erro] Alínea c exige --paradigma (acórdão divergente). Ver roteamento.md:120", file=sys.stderr)
        sys.exit(2)

    # Extração
    acordao_path = Path(args.acordao)
    try:
        text = extract_text(acordao_path)
    except Exception as e:
        print(f"[erro] {e}", file=sys.stderr)
        sys.exit(1)

    if len(text.strip()) < 50:
        print(f"[erro] Texto do acórdão muito curto ({len(text)} chars). PDF pode ser imagem (OCR necessário).", file=sys.stderr)
        sys.exit(1)

    sections = segment_acordao(text)
    variants = normalize_artigo(args.artigo)
    found = find_artigo_in_text(variants, sections)
    filtros = check_filtros(text, args.tipo, args.alinea)
    prazo = calcula_prazo(args.publicacao)

    # Monta resultado
    alinea_desc = (ALINEAS_RES if args.tipo == "RES" else ALINEAS_REX).get(args.alinea, args.alinea)

    if found["encontrado"]:
        prequestionado = True
        recomendacao = f"Prequestionamento OK: {found['variante']} encontrado em {found['local'].upper()} com confiança {found['confianca']:.0%}. Prosseguir para bundle."
        if filtros.get("sumula_7_stj") == "alerta" or filtros.get("sumula_279_stf") == "alerta":
            recomendacao += " ATENÇÃO: filtro Súmula 7/279 acendeu — verifique se tese não é reexame fático."
    else:
        prequestionado = False
        recomendacao = (
            f"Prequestionamento NÃO configurado: nenhuma variante de '{args.artigo}' encontrada em VOTO/EMENTA. "
            "Súmulas 282/STF e 211/STJ exigem debate expresso. "
            "Recomendação: opor Embargos de Declaração (art. 1.022 CPC) com prequestionamento explícito do dispositivo antes de interpor o recurso. "
            "O prazo do RES/REX ficará interrompido até julgamento dos EDs."
        )

    result = {
        "versao": "1.0.0",
        "tipo": args.tipo,
        "alinea": args.alinea,
        "alinea_descricao": alinea_desc,
        "artigo": args.artigo,
        "variantes_buscadas": variants,
        "acordao": str(acordao_path),
        "prequestionado": prequestionado,
        "deteccao": found,
        "filtros": filtros,
        "prazo": prazo,
        "recomendacao": recomendacao,
        "gerado_em": datetime.now().isoformat(),
    }

    # Paradigma check (se fornecido)
    if args.paradigma:
        paradigma_path = Path(args.paradigma)
        if paradigma_path.exists():
            try:
                ptext = extract_text(paradigma_path)
                pfiltros = check_filtros(ptext, args.tipo, args.alinea)
                result["paradigma"] = {"arquivo": str(paradigma_path), "chars": len(ptext), "filtros": pfiltros}
                if "diverg" in ptext.lower() or "dissidio" in ptext.lower():
                    result["paradigma"]["observacao"] = "Paradigma parece tratar de divergência jurisprudencial — verificar distinguishing."
            except Exception as e:
                result["paradigma"] = {"erro": str(e)}
        else:
            result["paradigma"] = {"erro": f"Arquivo não encontrado: {paradigma_path}"}

    # Output
    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    print(json_str)

    if args.json_output:
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json_str, encoding="utf-8")
        print(f"\n[ok] JSON salvo em {out}", file=sys.stderr)

    if args.verbose and found.get("trecho"):
        print(f"\n--- Trecho ({found['local']}) ---\n{found['trecho']}\n", file=sys.stderr)

    # Exit code: 0 = prequestionado, 1 = não prequestionado (útil para CI/pre-commit)
    sys.exit(0 if prequestionado else 1)


if __name__ == "__main__":
    main()

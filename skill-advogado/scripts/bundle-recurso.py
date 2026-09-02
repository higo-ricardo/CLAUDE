#!/usr/bin/env python3
"""
bundle-recurso.py — Empacotador e validador de Recurso Especial / Extraordinário
para protocolo no tribunal de origem.

Valida checklist roteamento.md:120-121 + minutas-civeis.md:966-972 / 1222-1227
e gera ZIP com manifesto.

Uso:
    python scripts/bundle-recurso.py --tipo RES --processo 0801234-56.2024.8.10.0001 --acordao data/acordao.pdf --peca output/RES.md --preparo data/gru.pdf --output dist/bundle_RES.zip
    python scripts/bundle-recurso.py --tipo RES --processo 0801234-56.2024.8.10.0001 --acordao data/acordao.pdf --peca output/RES.md --validate-only
    python scripts/bundle-recurso.py --tipo REX --processo 0801234-56.2024.8.10.0001 --acordao data/acordao.pdf --peca output/REX.md --paradigma data/re_123.pdf --check data/checks/preq.json --output dist/bundle_REX.zip
"""
import argparse
import json
import re
import sys
import zipfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
try:
    from constants import PRAZO_RECURSO_DIAS
except ImportError:
    PRAZO_RECURSO_DIAS = 15

# ---------------------------------------------------------------------------
# Validações
# ---------------------------------------------------------------------------

def validate_processo(numero: str) -> dict:
    """Valida formato CNJ NNNNNNN-DD.AAAA.J.TR.OOOO"""
    pattern = re.compile(r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$")
    ok = bool(pattern.match(numero.strip()))
    return {
        "ok": ok,
        "mensagem": "Formato CNJ válido" if ok else "Formato CNJ inválido. Esperado: 0801234-56.2024.8.10.0001",
    }

def validate_tribunal_origem(text_acordao: str) -> dict:
    """Heurística: verifica se acórdão é de TJ/TRF (RES/REX só cabe de 2º grau)."""
    low = text_acordao.lower() if text_acordao else ""
    is_tj = "tribunal de justiça" in low or "tj-" in low or "tj/" in low
    is_trf = "tribunal regional federal" in low or "trf" in low
    is_primeiro_grau = "vara cível" in low and "acórdão" not in low and "apelação" not in low
    if is_tj or is_trf:
        return {"ok": True, "origem": "TJ/TRF (2º grau) — cabimento OK"}
    if is_primeiro_grau:
        return {"ok": False, "origem": "1º grau (Vara) — RES/REX incabível. Só cabe de acórdão de TJ/TRF (minutas-civeis.md:772)"}
    return {"ok": None, "origem": "Não identificado — verificar manualmente se é acórdão de TJ/TRF"}

def validate_peca(peca_path: Path, tipo: str, alinea: str | None) -> dict:
    if not peca_path.exists():
        return {"ok": False, "mensagem": f"Peça não encontrada: {peca_path}"}
    text = peca_path.read_text(encoding="utf-8", errors="replace")
    checks = {}
    # Endereçamento ao presidente/vice do tribunal de origem
    checks["enderecamento"] = "presidente" in text.lower() and "vice-presidente" in text.lower() or "presidente" in text.lower()
    # Alínea citada
    if alinea:
        checks["alinea_citada"] = alinea.lower() in text.lower() or f"alínea {alinea}" in text.lower() or f"alinea {alinea}" in text.lower()
    # Repercussão geral (só REX)
    if tipo == "REX":
        checks["repercussao_geral"] = "repercussão geral" in text.lower() or "repercussao geral" in text.lower()
        if not checks["repercussao_geral"]:
            checks["repercussao_geral_msg"] = "REX exige preliminar formal de repercussão geral (art. 1.035, §2º, CPC) — não encontrada na peça"
    # Prequestionamento mencionado
    checks["prequestionamento_mencionado"] = "prequestionamento" in text.lower()
    # Pedido de admissibilidade
    checks["pedido_admissibilidade"] = "admissibilidade" in text.lower()
    # Tamanho mínimo (peça real tem >1500 chars; exemplo enxuto tolera 400)
    checks["tamanho_ok"] = len(text) > 400
    ok = all(v for k, v in checks.items() if isinstance(v, bool))
    return {"ok": ok, "checks": checks, "chars": len(text), "linhas": text.count("\n") + 1}

def validate_check(check_path: Path | None) -> dict:
    if not check_path:
        return {"ok": None, "mensagem": "Nenhum --check informado. Recomendado rodar checker-prequestionamento.py antes."}
    if not check_path.exists():
        return {"ok": False, "mensagem": f"Check não encontrado: {check_path}"}
    try:
        data = json.loads(check_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"ok": False, "mensagem": f"JSON inválido: {e}"}
    preq = data.get("prequestionado")
    if preq is True:
        return {"ok": True, "mensagem": "Prequestionamento OK (checker)", "data": data}
    if preq is False:
        return {"ok": False, "mensagem": "Prequestionamento NÃO configurado — recomenda EDs antes do recurso", "data": data}
    return {"ok": None, "mensagem": "Campo prequestionado ausente no JSON"}

def extract_text_safe(path: Path) -> str:
    if not path or not path.exists():
        return ""
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        try:
            import fitz
            doc = fitz.open(str(path))
            text = "\n".join(p.get_text() for p in doc)
            doc.close()
            return text
        except Exception:
            return path.read_text(encoding="utf-8", errors="replace")
    return path.read_text(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Manifesto
# ---------------------------------------------------------------------------
MANIFESTO_TEMPLATE = """# MANIFESTO — Bundle {tipo} — Processo {processo}

**Gerado em:** {data}
**Tipo:** {tipo} ({tipo_extenso})
**Processo:** {processo}
**Alínea:** {alinea}

## Checklist de Validação (roteamento.md:120 + minutas-civeis.md)

| Item | Status | Detalhe |
|------|--------|---------|
{rows}

## Prazos

- **Publicação do acórdão:** {publicacao}
- **Prazo limite (15 dias, art. 1.003 §5º CPC):** {prazo_limite}
- **Observação:** {prazo_obs}

## Arquivos no Bundle

{arquivos}

## Recomendação

{recomendacao}

---
*Gerado por bundle-recurso.py v1.0.0 — skill-advogado*
"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Bundle de Recurso Especial/Extraordinário")
    parser.add_argument("--tipo", required=True, choices=["RES", "REX"], help="Tipo de recurso")
    parser.add_argument("--processo", required=True, help="Número CNJ do processo")
    parser.add_argument("--acordao", required=True, help="Caminho do acórdão recorrido")
    parser.add_argument("--peca", required=True, help="Caminho da peça RES/REX (.md/.pdf)")
    parser.add_argument("--alinea", choices=["a", "b", "c"], help="Alínea (a/b/c) — se omitida tenta deduzir da peça")
    parser.add_argument("--paradigma", help="Acórdão paradigma (obrigatório se alínea c)")
    parser.add_argument("--preparo", help="Comprovante de preparo (GRU)")
    parser.add_argument("--check", dest="check_path", help="JSON do checker-prequestionamento.py")
    parser.add_argument("--publicacao", help="Data de publicação do acórdão YYYY-MM-DD")
    parser.add_argument("--output", help="Caminho do ZIP de saída (ex: dist/bundle_RES.zip)")
    parser.add_argument("--validate-only", action="store_true", help="Só valida, não gera ZIP")
    args = parser.parse_args()

    processo = args.processo.strip()
    tipo = args.tipo
    acordao_path = Path(args.acordao)
    peca_path = Path(args.peca)

    # --- Validações ---
    results = {}

    # 1. Processo
    results["processo"] = validate_processo(processo)

    # 2. Acórdão existe
    if not acordao_path.exists():
        print(f"[erro] Acórdão não encontrado: {acordao_path}", file=sys.stderr)
        sys.exit(2)
    results["acordao_existe"] = {"ok": True, "arquivo": str(acordao_path)}

    # 3. Tribunal origem
    text_acordao = extract_text_safe(acordao_path)
    results["tribunal"] = validate_tribunal_origem(text_acordao)

    # 4. Peça
    results["peca"] = validate_peca(peca_path, tipo, args.alinea)

    # 5. Paradigma se alínea c
    if args.alinea == "c":
        if not args.paradigma:
            results["paradigma"] = {"ok": False, "mensagem": "Alínea c exige --paradigma (roteamento.md:120)"}
        else:
            par_path = Path(args.paradigma)
            results["paradigma"] = {"ok": par_path.exists(), "arquivo": str(par_path), "mensagem": "Paradigma OK" if par_path.exists() else "Paradigma não encontrado"}
    else:
        if args.paradigma:
            par_path = Path(args.paradigma)
            results["paradigma"] = {"ok": par_path.exists(), "arquivo": str(par_path), "nota": "Paradigma fornecido mas alínea não é c"}

    # 6. Preparo
    if args.preparo:
        prep = Path(args.preparo)
        results["preparo"] = {"ok": prep.exists(), "arquivo": str(prep), "mensagem": "Comprovante OK" if prep.exists() else "Comprovante não encontrado"}
    else:
        results["preparo"] = {"ok": None, "mensagem": "Nenhum --preparo informado. Verificar recolhimento porte remessa/retorno (tabela STJ/STF)"}

    # 7. Checker
    check_path = Path(args.check_path) if args.check_path else None
    results["prequestionamento"] = validate_check(check_path)

    # 8. Prazo
    if args.publicacao:
        try:
            dt = datetime.strptime(args.publicacao, "%Y-%m-%d")
            limite = dt + timedelta(days=PRAZO_RECURSO_DIAS)
            results["prazo"] = {"publicacao": args.publicacao, "limite": limite.strftime("%Y-%m-%d"), "ok": True}
        except ValueError:
            results["prazo"] = {"ok": False, "mensagem": "Formato --publicacao inválido (YYYY-MM-DD)"}
    else:
        results["prazo"] = {"ok": None, "mensagem": f"Sem --publicacao. Prazo: {PRAZO_RECURSO_DIAS} dias (art. 1.003 §5º CPC)"}

    # 9. Petição separada RE/RES simultâneo (alerta)
    if tipo in ("RES", "REX"):
        # heurística: se peça menciona ambos os recursos
        peca_text = extract_text_safe(peca_path).lower() if peca_path.exists() else ""
        menciona_ambos = "recurso especial" in peca_text and "recurso extraordinário" in peca_text
        if menciona_ambos:
            results["peticao_separada"] = {"ok": False, "mensagem": "Peça menciona RES e REX — exige petições separadas (art. 1.029 §3º CPC)"}
        else:
            results["peticao_separada"] = {"ok": True}

    # --- Resumo para manifesto ---
    has_failure = any(v.get("ok") is False for v in results.values())
    has_unknown = any(v.get("ok") is None for v in results.values())

    if has_failure:
        recomendacao = "⛔ Bundle COM PENDÊNCIAS — não protocolar até corrigir itens ❌. Se prequestionamento falhou, opor EDs primeiro."
        status_label = "REPROVADO"
    elif has_unknown:
        recomendacao = "⚠️ Bundle com pendências de verificação manual (⚠️). Conferir itens antes de protocolar."
        status_label = "COM RESSALVAS"
    else:
        recomendacao = "✅ Bundle APROVADO — pronto para protocolo no presidente/vice do tribunal de origem."
        status_label = "APROVADO"

    # --- Output validação ---
    print(json.dumps(results, ensure_ascii=False, indent=2))

    # Monta linhas do manifesto
    rows = []
    for key, val in results.items():
        ok = val.get("ok")
        if ok is True:
            icon = "✅"
        elif ok is False:
            icon = "❌"
        else:
            icon = "⚠️"
        detalhe = val.get("mensagem") or val.get("origem") or val.get("arquivo") or str(val.get("checks", ""))[:120]
        rows.append(f"| {key} | {icon} | {detalhe} |")

    # Se validate-only, encerra
    if args.validate_only:
        print(f"\n[{status_label}] Validação concluída (validate-only).", file=sys.stderr)
        sys.exit(0 if not has_failure else 1)

    # --- Geração do ZIP ---
    if not args.output:
        print("[erro] Informe --output para gerar ZIP ou use --validate-only", file=sys.stderr)
        sys.exit(2)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Arquivos a incluir
    files_to_zip = []
    files_to_zip.append((acordao_path, f"02_acordao_recortido{acordao_path.suffix}"))
    if peca_path.exists():
        files_to_zip.append((peca_path, f"01_{tipo}{peca_path.suffix}"))
    if args.paradigma and Path(args.paradigma).exists():
        files_to_zip.append((Path(args.paradigma), f"05_paradigma{Path(args.paradigma).suffix}"))
    if args.preparo and Path(args.preparo).exists():
        files_to_zip.append((Path(args.preparo), f"04_comprovante_preparo{Path(args.preparo).suffix}"))
    if check_path and check_path.exists():
        files_to_zip.append((check_path, "06_check_prequestionamento.json"))

    # Gera manifesto
    tipo_extenso = "Recurso Especial (STJ)" if tipo == "RES" else "Recurso Extraordinário (STF)"
    prazo_pub = results.get("prazo", {}).get("publicacao", "não informada")
    prazo_lim = results.get("prazo", {}).get("limite", f"+{PRAZO_RECURSO_DIAS} dias da publicação")
    prazo_obs = results.get("prazo", {}).get("mensagem", "Art. 1.003, §5º, CPC")
    arquivos_list = "\n".join(f"- `{dst}` ← `{src.name}`" for src, dst in files_to_zip) or "- (nenhum arquivo adicional)"

    manifesto = MANIFESTO_TEMPLATE.format(
        tipo=tipo,
        tipo_extenso=tipo_extenso,
        processo=processo,
        alinea=args.alinea or "não informada",
        data=datetime.now().strftime("%Y-%m-%d %H:%M"),
        rows="\n".join(rows),
        publicacao=prazo_pub,
        prazo_limite=prazo_lim,
        prazo_obs=prazo_obs,
        arquivos=arquivos_list,
        recomendacao=recomendacao,
    )

    # Escreve ZIP
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
        for src, dst in files_to_zip:
            z.write(src, dst)
        # manifesto
        z.writestr("MANIFESTO.md", manifesto)
        # cópia do contrato se existir
        contrato = Path("contrato_decisao.md")
        if contrato.exists():
            z.write(contrato, "contrato_decisao.md")
        # validação
        z.writestr("validacao.json", json.dumps(results, ensure_ascii=False, indent=2))

    print(f"\n[{status_label}] Bundle gerado: {output_path} ({output_path.stat().st_size} bytes)", file=sys.stderr)
    print(f"Arquivos: {len(files_to_zip) + 2} (inclui MANIFESTO.md + validacao.json)", file=sys.stderr)
    if has_failure:
        print("[aviso] Bundle contém falhas — revisar antes de protocolar.", file=sys.stderr)

    sys.exit(0 if not has_failure else 1)


if __name__ == "__main__":
    main()

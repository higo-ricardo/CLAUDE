#!/usr/bin/env python3
"""
agent.py — Agente da Editora Ebook v2.

Loop agentico completo:
  1. Carrega estado do projeto automaticamente (versioner state + decisions list + scorer consolidate)
  2. Recebe objetivo em linguagem natural
  3. Chama tools (scripts Python) autonomamente via API Anthropic
  4. Pausa apenas em checkpoints editoriais genuínos
  5. Entrega resultado ao usuário

Uso via CLI:
  python scripts/cli.py "Escreva o Capítulo 3 sobre gestão do tempo"
  python scripts/cli.py --interactive

Uso programático:
  from scripts.agent import EditoraAgent
  agent = EditoraAgent()
  result = agent.run("Revise o Capítulo 1 e salve a versão aprovada")
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Generator

import anthropic

from tools import TOOLS

# ── Paths ─────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR     = PROJECT_ROOT / "data"
SCRIPTS_DIR  = PROJECT_ROOT / "scripts"
CHAPTERS_DIR = PROJECT_ROOT / "chapters"

CHAPTERS_DIR.mkdir(exist_ok=True)

# ── Checkpoints — critérios para pausar e pedir input humano ─────────────────

HUMAN_TRIGGERS = [
    "INSUFICIÊNCIA DE FONTES",
    "conflito detectado",
    "Conflito com decisão travada",
    "⚠️ Conflito",
]

REWORK_SIGNAL  = "RETRABALHO NECESSÁRIO"
MAX_REWORK_ATTEMPTS = 2


# ─────────────────────────────────────────────────────────────────────────────
# EXECUTOR DE TOOLS
# ─────────────────────────────────────────────────────────────────────────────

def _params_to_args(tool_name: str, params: dict) -> list[str]:
    """Converte parâmetros JSON da tool em argumentos CLI para os scripts."""
    script = f"{tool_name}.py"
    args   = [script]

    # Mapeamentos especiais de parâmetros para flags CLI
    BOOL_FLAGS = {
        "consolidate": "--consolidate",
        "check":       "--check",
        "list_templates": "--list",
    }
    RENAME = {
        "chapters_dir": "--chapters-dir",
        "list_templates": "--list",
    }

    for key, val in params.items():
        if val is None:
            continue

        # Flags booleanas sem valor
        if key in BOOL_FLAGS and val is True:
            args.append(BOOL_FLAGS[key])
            continue

        # Campos mapeados para nomes diferentes de flag
        flag = RENAME.get(key, f"--{key.replace('_', '-')}")

        if isinstance(val, bool):
            if val:
                args.append(flag)
        elif isinstance(val, dict):
            # Objeto → JSON inline (ex: --fields '{"N":"3"}')
            args.extend([flag, json.dumps(val, ensure_ascii=False)])
        elif isinstance(val, list):
            for item in val:
                args.extend([flag, str(item)])
        else:
            args.extend([flag, str(val)])

    return args


def execute_tool(tool_name: str, params: dict) -> str:
    """Executa um script via runner.py e retorna o output como string."""

    # write_file e read_file são implementados aqui, não como scripts externos
    if tool_name == "write_file":
        return _tool_write_file(params)

    if tool_name == "read_file":
        return _tool_read_file(params)

    if tool_name == "ask_human":
        return _tool_ask_human(params)

    args = _params_to_args(tool_name, params)
    command_str = " ".join(args)

    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "runner.py"), command_str],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )

    output = result.stdout.strip()
    if result.stderr.strip():
        output += f"\n[STDERR] {result.stderr.strip()[:300]}"

    return output or "(sem output)"


def _tool_write_file(params: dict) -> str:
    path    = PROJECT_ROOT / params["path"]
    content = params["content"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    words = len(content.split())
    return f"✅ Arquivo salvo: {params['path']} ({words} palavras, {len(content)} chars)"


def _tool_read_file(params: dict) -> str:
    path = PROJECT_ROOT / params["path"]
    if not path.exists():
        # Tentar caminho absoluto
        path = Path(params["path"])
    if not path.exists():
        return f"❌ Arquivo não encontrado: {params['path']}"
    content = path.read_text(encoding="utf-8")
    words   = len(content.split())
    return f"[ARQUIVO: {params['path']} — {words} palavras]\n\n{content}"


def _tool_ask_human(params: dict) -> str:
    """
    Pausa o agente e coleta input do usuário via stdin.
    Em ambiente não-interativo, retorna sinal de pausa para o caller.
    """
    return f"__ASK_HUMAN__:{json.dumps(params, ensure_ascii=False)}"


# ─────────────────────────────────────────────────────────────────────────────
# SISTEMA PROMPT — SKILL.md + ESTADO ATUAL
# ─────────────────────────────────────────────────────────────────────────────

def build_system_prompt() -> str:
    skill_path = PROJECT_ROOT / "SKILL.md"
    skill_md   = skill_path.read_text(encoding="utf-8") if skill_path.exists() else ""

    # Carregar estado atual automaticamente (sem intervenção humana)
    state_parts = []

    scores_file = DATA_DIR / "scores.json"
    if scores_file.exists():
        scores = json.loads(scores_file.read_text())
        if scores:
            state_parts.append(f"SCORES ATUAIS:\n{json.dumps(scores, ensure_ascii=False, indent=2)}")
        else:
            state_parts.append("SCORES: nenhum capítulo avaliado ainda.")

    dec_file = DATA_DIR / "decisions.json"
    if dec_file.exists():
        decisions = json.loads(dec_file.read_text())
        locked    = decisions.get("locked", [])
        pending   = decisions.get("pending", [])
        if locked:
            state_parts.append(
                f"DECISÕES TRAVADAS ({len(locked)}):\n" +
                "\n".join(f"  [{d['id']}] {d['category']}: {d['decision']}" for d in locked)
            )
        else:
            state_parts.append("DECISÕES TRAVADAS: nenhuma ainda.")
        if pending:
            state_parts.append(
                f"DECISÕES PENDENTES ({len(pending)}):\n" +
                "\n".join(f"  [{p.get('id','?')}] {p['question']}" for p in pending)
            )

    proj_file = DATA_DIR / "project.json"
    if proj_file.exists():
        proj = json.loads(proj_file.read_text())
        title   = proj.get("title", "")
        stage   = proj.get("current_stage", "M1")
        version = proj.get("current_version", "v0.1")
        if title:
            state_parts.append(
                f"PROJETO: \"{title}\" | Estágio: {stage} | Versão: {version}"
            )

    state_block = ""
    if state_parts:
        state_block = (
            "\n\n---\n## ESTADO ATUAL DO PROJETO (carregado automaticamente)\n\n"
            + "\n\n".join(state_parts)
        )

    agent_rules = """

---
## REGRAS DO AGENTE

Você é o ORQUESTRADOR da Editora Ebook. Execute autonomamente:
- Consulte decisões travadas (decisions list) antes de qualquer tarefa
- Use scorer para calcular scores — nunca calcule manualmente
- Use analyzer antes de revisar (passive, readability, jargon)
- Salve versões (versioner save) após cada capítulo aprovado
- Verifique grafia (decisions check) antes de entregar capítulo
- Use write_file para salvar conteúdo gerado antes de versionar
- Use ask_human SOMENTE para: conflito editorial, ambiguidade no briefing, escolha criativa, score < limiar após 2 tentativas

Quando score < limiar: regenere automaticamente (até 2 tentativas).
Quando detectar conflito com decisão travada: use ask_human imediatamente.
Informe qual agente está executando no início de cada etapa.
"""

    return skill_md + state_block + agent_rules


# ─────────────────────────────────────────────────────────────────────────────
# CHECKPOINT — decidir se requer input humano
# ─────────────────────────────────────────────────────────────────────────────

def _requires_human(tool_results: list[dict]) -> tuple[bool, dict | None]:
    """
    Retorna (True, params) se algum resultado exige intervenção humana.
    Retorna (False, None) caso contrário.
    """
    for r in tool_results:
        # tool_dicts usa "output"; tool_results (API) usa "content"
        content = r.get("output", r.get("content", ""))

        # ask_human foi chamado pela LLM
        if isinstance(content, str) and content.startswith("__ASK_HUMAN__:"):
            raw    = content.removeprefix("__ASK_HUMAN__:")
            params = json.loads(raw)
            return True, params

        # Triggers de pausa detectados no output de scripts
        if isinstance(content, str):
            for trigger in HUMAN_TRIGGERS:
                if trigger.lower() in content.lower():
                    return True, {
                        "question": "O agente detectou uma situação que requer sua decisão.",
                        "context":  content[:800],
                    }

    return False, None


# ─────────────────────────────────────────────────────────────────────────────
# CLASSE PRINCIPAL DO AGENTE
# ─────────────────────────────────────────────────────────────────────────────

class EditoraAgent:

    def __init__(self, model: str = "claude-sonnet-4-6", verbose: bool = True):
        self.client   = anthropic.Anthropic()
        self.model    = model
        self.verbose  = verbose
        self._rework_count: dict[str, int] = {}

    # ── Log helper ────────────────────────────────────────────────────────

    def _log(self, msg: str, prefix: str = "●"):
        if self.verbose:
            print(f"\n{prefix} {msg}", flush=True)

    def _log_tool(self, name: str, params: dict):
        p = {k: v for k, v in params.items() if k != "content"}
        print(f"\n  ⚙  tool:{name}  {json.dumps(p, ensure_ascii=False)[:120]}", flush=True)

    def _log_result(self, name: str, result: str):
        preview = result[:200].replace("\n", " ")
        print(f"     → {preview}{'…' if len(result) > 200 else ''}", flush=True)

    # ── Executar bloco de tools retornado pela API ─────────────────────────

    def _execute_tools(self, response) -> tuple[list[dict], list[dict]]:
        """
        Executa todos os tool_use blocks do response.
        Retorna (tool_result_blocks, tool_result_dicts).
        """
        tool_results = []
        tool_dicts   = []

        for block in response.content:
            if block.type != "tool_use":
                continue

            self._log_tool(block.name, block.input)

            output = execute_tool(block.name, block.input)

            # Tracking de retrabalho por capítulo
            if block.name == "scorer" and REWORK_SIGNAL in output:
                chapter = block.input.get("chapter", "?")
                self._rework_count[chapter] = self._rework_count.get(chapter, 0) + 1
                if self._rework_count[chapter] >= MAX_REWORK_ATTEMPTS:
                    output += (
                        f"\n\n⚠️  ATENÇÃO: score abaixo do limiar após "
                        f"{MAX_REWORK_ATTEMPTS} tentativas para '{chapter}'. "
                        "Use ask_human para consultar o usuário."
                    )

            self._log_result(block.name, output)

            tool_results.append({
                "type":        "tool_result",
                "tool_use_id": block.id,
                "content":     output,
            })
            tool_dicts.append({"tool": block.name, "output": output})

        return tool_results, tool_dicts

    # ── Extrai texto final da resposta ────────────────────────────────────

    @staticmethod
    def _extract_text(response) -> str:
        parts = []
        for block in response.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts).strip()

    # ── Loop principal ────────────────────────────────────────────────────

    def run(self, objetivo: str, human_input_fn=None) -> str:
        """
        Executa o agente até completar o objetivo ou encontrar checkpoint humano.

        Args:
            objetivo:        Instrução em linguagem natural
            human_input_fn:  Função opcional para coletar input humano.
                             Assinatura: fn(question, context, options) -> str
                             Se None, usa input() do terminal.

        Returns:
            Resposta final do agente como string.
        """
        if human_input_fn is None:
            human_input_fn = _default_human_input

        system  = build_system_prompt()
        messages = [{"role": "user", "content": objetivo}]

        self._log(f"Objetivo: {objetivo}", "▶")
        self._rework_count = {}
        turn = 0

        while True:
            turn += 1
            self._log(f"Turno {turn}", "─")

            response = self.client.messages.create(
                model      = self.model,
                max_tokens = 8096,
                system     = system,
                tools      = TOOLS,
                messages   = messages,
            )

            # ── Agente terminou ──────────────────────────────────────────
            if response.stop_reason == "end_turn":
                final = self._extract_text(response)
                self._log("Concluído.", "✓")
                return final

            # ── Agente quer executar tools ───────────────────────────────
            if response.stop_reason == "tool_use":
                tool_results, tool_dicts = self._execute_tools(response)

                # Verificar checkpoint humano
                needs_human, params = _requires_human(tool_dicts)
                if needs_human:
                    self._log("Checkpoint humano necessário.", "⏸")
                    human_answer = human_input_fn(
                        question=params.get("question", ""),
                        context =params.get("context",  ""),
                        options =params.get("options",  []),
                    )

                    # Injetar resposta humana e continuar o loop
                    messages += [
                        {"role": "assistant", "content": response.content},
                        {"role": "user",      "content": tool_results},
                        {"role": "user",      "content": (
                            f"[Resposta do usuário ao checkpoint]: {human_answer}"
                        )},
                    ]
                else:
                    messages += [
                        {"role": "assistant", "content": response.content},
                        {"role": "user",      "content": tool_results},
                    ]

            # ── Stop reason inesperado ───────────────────────────────────
            else:
                self._log(f"Stop reason inesperado: {response.stop_reason}", "⚠")
                return self._extract_text(response)

    # ── Streaming do texto final ─────────────────────────────────────────

    def stream(self, objetivo: str, human_input_fn=None) -> Generator[str, None, None]:
        """
        Versão streaming: igual ao run(), mas o texto final chega token a token.
        Tools são executadas de forma síncrona (sem streaming de tool calls).
        Faz yield de cada chunk de texto.
        """
        if human_input_fn is None:
            human_input_fn = _default_human_input

        system   = build_system_prompt()
        messages = [{"role": "user", "content": objetivo}]
        self._rework_count = {}
        turn = 0

        while True:
            turn += 1

            # Verificar se a última resposta pode ter tool calls
            # Para tools: usar API síncrona; para texto final: usar streaming
            response = self.client.messages.create(
                model      = self.model,
                max_tokens = 8096,
                system     = system,
                tools      = TOOLS,
                messages   = messages,
            )

            if response.stop_reason == "end_turn":
                # Re-fazer a última call com streaming para entregar token a token
                with self.client.messages.stream(
                    model      = self.model,
                    max_tokens = 8096,
                    system     = system,
                    tools      = TOOLS,
                    messages   = messages,
                ) as stream:
                    for chunk in stream.text_stream:
                        yield chunk
                return

            if response.stop_reason == "tool_use":
                tool_results, tool_dicts = self._execute_tools(response)

                needs_human, params = _requires_human(tool_dicts)
                if needs_human:
                    yield "\n\n⏸ **Checkpoint — aguardando sua decisão:**\n"
                    yield f"\n{params.get('question', '')}\n"
                    if params.get("context"):
                        yield f"\n```\n{params['context'][:600]}\n```\n"
                    human_answer = human_input_fn(
                        question=params.get("question", ""),
                        context =params.get("context",  ""),
                        options =params.get("options",  []),
                    )
                    messages += [
                        {"role": "assistant", "content": response.content},
                        {"role": "user",      "content": tool_results},
                        {"role": "user",      "content": (
                            f"[Resposta do usuário ao checkpoint]: {human_answer}"
                        )},
                    ]
                else:
                    messages += [
                        {"role": "assistant", "content": response.content},
                        {"role": "user",      "content": tool_results},
                    ]
            else:
                yield self._extract_text(response)
                return


# ─────────────────────────────────────────────────────────────────────────────
# INPUT HUMANO — fallback para terminal
# ─────────────────────────────────────────────────────────────────────────────

def _default_human_input(question: str, context: str = "", options: list = []) -> str:
    print("\n" + "═" * 60)
    print("⏸  CHECKPOINT — Decisão editorial necessária")
    print("═" * 60)
    if context:
        print(f"\nContexto:\n{context[:600]}")
    print(f"\n❓ {question}")
    if options:
        print("\nOpções:")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        print()
        raw = input("Sua escolha (número ou texto livre): ").strip()
        # Tentar resolver por número
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        return raw
    else:
        return input("\nSua resposta: ").strip()

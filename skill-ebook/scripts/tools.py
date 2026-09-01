#!/usr/bin/env python3
"""
tools.py — Declarações de tools para a API Anthropic.
Cada entrada mapeia exatamente para um script da Editora Ebook v2.
A LLM usa as descriptions para decidir quando e como chamar cada tool.
"""

TOOLS = [

    # ── scorer.py ──────────────────────────────────────────────────────────
    {
        "name": "scorer",
        "description": (
            "Calcula o score ponderado S1-S5 de um capítulo e persiste em scores.json. "
            "Use SEMPRE após avaliar as seções de qualquer capítulo. "
            "Nunca calcule scores manualmente — delegue sempre a esta tool. "
            "Use --consolidate para ver o scorecard geral do projeto. "
            "Use --scorecard CHAPTER para ver detalhes de um capítulo específico."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "s1": {"type": "number", "description": "Gancho/Abertura (0-10)"},
                "s2": {"type": "number", "description": "Desenvolvimento (0-10)"},
                "s3": {"type": "number", "description": "Adequação ao público (0-10)"},
                "s4": {"type": "number", "description": "Integridade factual (0-10)"},
                "s5": {"type": "number", "description": "Fechamento/Transição (0-10)"},
                "stage": {
                    "type": "string",
                    "enum": ["M4", "M5", "M6", "M7"],
                    "description": "Estágio atual: M4=rascunho(6.0), M5=revisão(7.0), M6=copy(7.5), M7=final(8.0)"
                },
                "chapter": {"type": "string", "description": "Nome do capítulo, ex: 'Capítulo 1'"},
                "version": {"type": "string", "description": "Versão, ex: 'v1.0'"},
                "consolidate": {
                    "type": "boolean",
                    "description": "Se true, retorna tabela consolidada de todos os capítulos. Ignora s1-s5."
                },
                "scorecard": {
                    "type": "string",
                    "description": "Nome do capítulo para ver scorecard detalhado. Ignora s1-s5."
                },
            },
            "required": [],
        },
    },

    # ── analyzer.py ────────────────────────────────────────────────────────
    {
        "name": "analyzer",
        "description": (
            "Analisa texto de capítulos detectando problemas objetivos. "
            "Use ANTES de revisar (passive, readability, jargon, numbering). "
            "Use para verificar equilíbrio entre capítulos (balance). "
            "Use para verificar cobertura do sumário (gap). "
            "Retorna JSON estruturado — não tente detectar esses padrões manualmente."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["passive", "readability", "jargon", "balance", "gap", "numbering"],
                    "description": (
                        "passive: voz passiva | "
                        "readability: Flesch PT-BR e frases longas | "
                        "jargon: termos sem definição inline | "
                        "balance: palavras por capítulo | "
                        "gap: cobertura do sumário | "
                        "numbering: listas numeradas inconsistentes"
                    ),
                },
                "text": {
                    "type": "string",
                    "description": "Caminho para o arquivo .md (obrigatório para passive/readability/jargon/numbering)"
                },
                "level": {
                    "type": "string",
                    "enum": ["leigo", "iniciante", "intermediario", "avancado", "especialista"],
                    "description": "Nível do público (obrigatório para readability)"
                },
                "glossary": {
                    "type": "string",
                    "description": "Caminho para glossary.json (obrigatório para jargon). Default: data/glossary.json"
                },
                "chapters_dir": {
                    "type": "string",
                    "description": "Diretório com .md dos capítulos (para balance e gap). Default: chapters/"
                },
                "summary": {
                    "type": "string",
                    "description": "Caminho para summary.json (obrigatório para gap). Default: data/summary.json"
                },
            },
            "required": ["mode"],
        },
    },

    # ── decisions.py ───────────────────────────────────────────────────────
    {
        "name": "decisions",
        "description": (
            "Gerencia o log de decisões editoriais travadas. "
            "Use 'list' no início de cada tarefa para consultar decisões vigentes. "
            "Use 'check' antes de entregar qualquer capítulo para detectar conflitos de grafia. "
            "Use 'add' quando o usuário aprovar uma decisão editorial. "
            "Use 'alter' quando o usuário solicitar mudança em decisão existente. "
            "NUNCA ignore conflitos detectados — sempre parar e notificar o usuário."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "list", "check", "pending", "add-pending", "alter"],
                    "description": (
                        "add: travar nova decisão | "
                        "list: listar decisões travadas | "
                        "check: detectar conflitos num arquivo | "
                        "pending: ver decisões em aberto | "
                        "add-pending: registrar questão em aberto | "
                        "alter: modificar decisão travada (requer id+reason)"
                    ),
                },
                "category": {
                    "type": "string",
                    "enum": ["TOM", "PUB", "EST", "LNG", "CIT", "GRF", "POS", "FMT", "MKT"],
                    "description": "Categoria da decisão (obrigatório para add/add-pending)"
                },
                "decision": {
                    "type": "string",
                    "description": "Texto da decisão (obrigatório para add/alter)"
                },
                "by": {
                    "type": "string",
                    "description": "Quem tomou a decisão. Default: Usuário"
                },
                "stage": {
                    "type": "string",
                    "description": "Estágio em que foi tomada (ex: M1). Default: M1"
                },
                "text": {
                    "type": "string",
                    "description": "Caminho para arquivo .md a verificar (obrigatório para check)"
                },
                "id": {
                    "type": "string",
                    "description": "ID da decisão a alterar, ex: D-03 (obrigatório para alter)"
                },
                "reason": {
                    "type": "string",
                    "description": "Motivo da alteração (obrigatório para alter)"
                },
                "question": {
                    "type": "string",
                    "description": "Questão em aberto (obrigatório para add-pending)"
                },
                "urgency": {
                    "type": "string",
                    "description": "Urgência da questão pendente: Alta/Média/Baixa. Default: Média"
                },
            },
            "required": ["action"],
        },
    },

    # ── versioner.py ───────────────────────────────────────────────────────
    {
        "name": "versioner",
        "description": (
            "Gerencia versionamento de capítulos e estado do projeto. "
            "Use 'state' ao iniciar qualquer sessão para carregar o contexto atual. "
            "Use 'save' após cada capítulo aprovado. "
            "Use 'history' para ver o histórico completo de alterações. "
            "Use 'diff' para comparar duas versões de um capítulo. "
            "Use 'rollback' quando o usuário solicitar reversão."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["save", "history", "diff", "rollback", "state"],
                    "description": (
                        "save: salvar versão de um capítulo | "
                        "history: listar histórico completo | "
                        "diff: comparar duas versões | "
                        "rollback: restaurar versão anterior | "
                        "state: exibir estado completo do projeto"
                    ),
                },
                "chapter": {
                    "type": "string",
                    "description": "Nome do capítulo (obrigatório para save/diff/rollback)"
                },
                "version": {
                    "type": "string",
                    "description": "Versão a salvar ou restaurar, ex: v1.2 (obrigatório para save/rollback)"
                },
                "agent": {
                    "type": "string",
                    "description": "Nome do agente que fez a alteração. Default: LLM"
                },
                "description": {
                    "type": "string",
                    "description": "Descrição da alteração (obrigatório para save)"
                },
                "file": {
                    "type": "string",
                    "description": "Caminho para o arquivo .md a versionar (obrigatório para save)"
                },
                "compare": {
                    "type": "string",
                    "description": "Versões a comparar, ex: v1.1:v1.2 (obrigatório para diff)"
                },
            },
            "required": ["action"],
        },
    },

    # ── publisher.py ───────────────────────────────────────────────────────
    {
        "name": "publisher",
        "description": (
            "Gera metadados estruturados e checklist de publicação. "
            "Use 'metadata' no início de M9 para gerar YAML completo para KDP/Hotmart. "
            "Use 'checklist' para verificar o status de todos os itens pré-publicação. "
            "Requer data/project.json preenchido com os dados do briefing."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["metadata", "checklist"],
                    "description": "metadata: gera YAML para plataformas | checklist: status dos 15 itens pré-publicação"
                },
            },
            "required": ["action"],
        },
    },

    # ── exporter.py ────────────────────────────────────────────────────────
    {
        "name": "exporter",
        "description": (
            "Exporta o manuscrito Markdown para EPUB, DOCX ou PDF. "
            "Use em M8 após aprovação final do manuscrito. "
            "Use 'check' para verificar se pandoc está instalado antes de exportar. "
            "Detecta automaticamente o melhor motor PDF disponível."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "enum": ["epub", "docx", "pdf"],
                    "description": "Formato de saída"
                },
                "input": {
                    "type": "string",
                    "description": "Caminho para o arquivo .md de entrada"
                },
                "output": {
                    "type": "string",
                    "description": "Nome do arquivo de saída (opcional — gerado automaticamente se omitido)"
                },
                "cover": {
                    "type": "string",
                    "description": "Caminho para imagem de capa (opcional, apenas EPUB)"
                },
                "template": {
                    "type": "string",
                    "description": "Caminho para template .docx de referência (opcional, apenas DOCX)"
                },
                "check": {
                    "type": "boolean",
                    "description": "Se true, verifica disponibilidade do pandoc sem exportar"
                },
            },
            "required": [],
        },
    },

    # ── templater.py ───────────────────────────────────────────────────────
    {
        "name": "templater",
        "description": (
            "Preenche templates Markdown com campos do projeto. "
            "Use ao iniciar um novo capítulo, rosto, sumário ou blurb. "
            "Campos não fornecidos aparecem como [PENDENTE: campo] no output. "
            "Templates disponíveis: capitulo-nonfiction, capitulo-ficcao, "
            "conclusao, blurb, rosto, sumario."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "template": {
                    "type": "string",
                    "enum": ["capitulo-nonfiction", "capitulo-ficcao", "conclusao",
                             "blurb", "rosto", "sumario"],
                    "description": "Nome do template a preencher"
                },
                "fields": {
                    "type": "object",
                    "description": (
                        "Campos a substituir no template. "
                        "Exemplos: {N: '3', Título: 'Gestão do Tempo', "
                        "Seção 1: 'O Problema', Autor: 'Nome'}"
                    ),
                    "additionalProperties": {"type": "string"},
                },
                "output": {
                    "type": "string",
                    "description": "Caminho para salvar o .md preenchido"
                },
                "list_templates": {
                    "type": "boolean",
                    "description": "Se true, lista os templates disponíveis sem preencher nenhum"
                },
            },
            "required": [],
        },
    },

    # ── write_file ─────────────────────────────────────────────────────────
    {
        "name": "write_file",
        "description": (
            "Escreve conteúdo textual em um arquivo no sistema. "
            "Use para salvar capítulos redigidos, rascunhos, blurbs ou qualquer "
            "conteúdo gerado em arquivo .md antes de versionar. "
            "Cria o arquivo se não existir; sobrescreve se existir."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho do arquivo a criar/sobrescrever, ex: chapters/cap03.md"
                },
                "content": {
                    "type": "string",
                    "description": "Conteúdo completo a escrever no arquivo"
                },
            },
            "required": ["path", "content"],
        },
    },

    # ── read_file ──────────────────────────────────────────────────────────
    {
        "name": "read_file",
        "description": (
            "Lê o conteúdo de um arquivo do sistema. "
            "Use para ler capítulos existentes antes de revisá-los, "
            "ler project.json para verificar metadados, "
            "ou ler qualquer arquivo .md ou .json do projeto."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Caminho do arquivo a ler"
                },
            },
            "required": ["path"],
        },
    },

    # ── ask_human ──────────────────────────────────────────────────────────
    {
        "name": "ask_human",
        "description": (
            "Pausa o agente e solicita input do usuário. "
            "Use SOMENTE para decisões genuinamente editoriais que o autor precisa tomar: "
            "conflito com decisão travada, ambiguidade no briefing, "
            "escolha criativa de título/tom/estrutura, "
            "ou score abaixo do limiar após 2 tentativas de regeneração. "
            "NÃO use para tarefas determinísticas — essas ficam com os outros scripts."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Pergunta clara e objetiva para o usuário"
                },
                "context": {
                    "type": "string",
                    "description": "Contexto necessário para o usuário decidir (resultado do script, trecho do texto, etc.)"
                },
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Opções pré-definidas para o usuário escolher (opcional)"
                },
            },
            "required": ["question"],
        },
    },
]

"""
constants.py — Fonte única para Súmulas, filtros e limites da skill-advogado.
Evita DRY entre roteamento.md / fontes.md / checker / bundle.
"""

# Filtros de admissibilidade - referência: fontes.md § 3.1.2
FILTROS_ADMISSIBILIDADE = {
    "sumula_5_stj": {
        "enunciado": "A simples interpretação de cláusula contratual não enseja recurso especial.",
        "aplica_a": ["RES"],
        "keywords": ["cláusula contratual", "interpretação de contrato", "pacto contratual"],
    },
    "sumula_7_stj": {
        "enunciado": "A pretensão de simples reexame de prova não enseja recurso especial.",
        "aplica_a": ["RES"],
        "keywords": ["reexame de prova", "revolver matéria fática", "conjunto probatório"],
    },
    "sumula_83_stj": {
        "enunciado": "Não se conhece do recurso especial pela divergência quando a orientação se firmou no mesmo sentido.",
        "aplica_a": ["RES"],
        "alinia": "c",
    },
    "sumula_126_stj": {
        "enunciado": "Inadmissível RES quando acórdão assenta em fundamentos constitucional e infraconstitucional e RE não interposto.",
        "aplica_a": ["RES"],
    },
    "sumula_211_stj": {
        "enunciado": "Inadmissível RES quanto à questão não apreciada pelo tribunal a quo apesar de EDs.",
        "aplica_a": ["RES"],
    },
    "sumula_279_stf": {
        "enunciado": "Para simples reexame de prova não cabe recurso extraordinário.",
        "aplica_a": ["REX"],
    },
    "sumula_282_stf": {
        "enunciado": "Inadmissível RE quando não ventilada na decisão recorrida a questão federal suscitada.",
        "aplica_a": ["REX", "RES"],
    },
    "sumula_356_stf": {
        "enunciado": "Ponto omisso sem EDs não pode ser objeto de RE por falta de prequestionamento.",
        "aplica_a": ["REX", "RES"],
    },
}

# Alíneas constitucionais — roteamento.md § 2-C + fontes.md § 1.2.1
ALINEAS_RES = {
    "a": "Art. 105, III, a — contrariar tratado ou lei federal",
    "b": "Art. 105, III, b — julgar válido ato de governo local contestado em face de lei federal",
    "c": "Art. 105, III, c — divergência de interpretação de lei federal entre tribunais",
}
ALINEAS_REX = {
    "a": "Art. 102, III, a — contrariar dispositivo da CF",
    "b": "Art. 102, III, b — declarar inconstitucional tratado ou lei federal",
    "c": "Art. 102, III, c — julgar válida lei/ato local contestado em face da CF",
}

PRAZO_RECURSO_DIAS = 15  # art. 1.003, §5º, CPC

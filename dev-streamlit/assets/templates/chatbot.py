"""
TEMPLATE: Chatbot com IA
Uso: Interface de chat com streaming e histórico persistente
Adapte: model, system prompt, integração de API
Dependências: pip install streamlit openai
"""
import streamlit as st

st.set_page_config(page_title="Assistente IA", page_icon="🤖", layout="centered")

# ── Config ────────────────────────────────────────────────────
SYSTEM_PROMPT = """Você é um assistente especializado em [SEU DOMÍNIO].
Responda sempre em português, de forma clara e objetiva.
Se não souber a resposta, diga honestamente."""

MODEL = "gpt-4o-mini"

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configurações")
    
    temperatura = st.slider("Criatividade", 0.0, 1.0, 0.7, 0.1,
                             help="Maior = mais criativo. Menor = mais preciso.")
    max_tokens = st.number_input("Máx. tokens resposta", 100, 4000, 1000, 100)
    
    st.divider()
    
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()
    
    st.caption(f"Modelo: `{MODEL}`")
    st.caption(f"Mensagens: {max(0, len(st.session_state.get('messages', [])) - 1)}")

# ── Estado ────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# ── Header ────────────────────────────────────────────────────
st.title("🤖 Assistente Inteligente")
st.caption("Pergunte qualquer coisa. Eu estou aqui para ajudar!")
st.divider()

# ── Histórico ────────────────────────────────────────────────
for msg in st.session_state.messages[1:]:  # skip system
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Mensagem inicial (se conversa vazia) ─────────────────────
if len(st.session_state.messages) == 1:
    with st.chat_message("assistant"):
        st.markdown("Olá! Como posso ajudar você hoje? 😊")

# ── Input ─────────────────────────────────────────────────────
if prompt := st.chat_input("Digite sua mensagem..."):
    # Adicionar mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Gerar resposta
    with st.chat_message("assistant"):
        # OPÇÃO 1: OpenAI com streaming
        # from openai import OpenAI
        # client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        # stream = client.chat.completions.create(
        #     model=MODEL,
        #     messages=st.session_state.messages,
        #     max_tokens=max_tokens,
        #     temperature=temperatura,
        #     stream=True,
        # )
        # resposta = st.write_stream(
        #     chunk.choices[0].delta.content or ""
        #     for chunk in stream
        #     if chunk.choices[0].delta.content
        # )
        
        # PLACEHOLDER (substitua pela integração real):
        with st.spinner("Pensando..."):
            import time
            time.sleep(1)
            resposta = f"[Resposta para: '{prompt}']\n\n*Configure a integração com sua API de IA aqui.*"
        st.markdown(resposta)
    
    st.session_state.messages.append({"role": "assistant", "content": resposta})

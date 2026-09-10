---
name: dev-streamlit
description: >
  Skill completa para desenvolvimento de aplicações Python com Streamlit. Use esta skill SEMPRE que o usuário quiser criar, melhorar, depurar ou estruturar um app Streamlit — mesmo que não cite "Streamlit" explicitamente. Gatilhos incluem: "quero criar um dashboard", "fazer um app de dados em Python", "app de machine learning", "interface para meu modelo", "painel de monitoramento", "visualizador de dados", "app de análise", "formulário de cadastro em Python", "chatbot com interface", "app de upload de arquivos". Esta skill cobre toda a API do Streamlit: widgets, layout, estado, cache, gráficos, páginas múltiplas e padrões de arquitetura. Inclui componentes reutilizáveis prontos para copiar e colar.
---

# 🎈 Streamlit Dev Skill

Skill para desenvolvimento de apps Streamlit com componentes reutilizáveis, padrões de arquitetura e referência completa da API.

## Referências disponíveis

Leia os arquivos de referência conforme a necessidade:

| Arquivo | Quando ler |
|---|---|
| `references/api-cheatsheet.md` | Referência rápida de toda a API (widgets, layout, texto, dados, gráficos) |
| `references/patterns.md` | Padrões arquiteturais: multi-page, estado, cache, autenticação |
| `references/components.md` | Componentes reutilizáveis prontos para uso |
| `assets/templates/` | Templates completos de apps por finalidade |

---

## Fluxo de trabalho para criar um app

### 1. Entender o tipo de app

Identifique a finalidade principal:

- **Dashboard de dados** → múltiplos `st.metric`, `st.dataframe`, gráficos
- **Formulário / CRUD** → `st.form`, `st.data_editor`, `session_state`
- **Ferramenta de ML/AI** → `st.file_uploader`, `@st.cache_resource`, `st.chat_*`
- **Explorador de dados** → filtros com `st.sidebar`, `st.dataframe`, gráficos interativos
- **Chatbot** → `st.chat_message`, `st.chat_input`, histórico em `session_state`
- **Multi-página** → `st.navigation`, `st.Page`, sidebar com links

### 2. Estruturar o projeto

```
meu_app/
├── app.py               # Entry point (st.navigation para multi-page)
├── pages/
│   ├── home.py
│   ├── dados.py
│   └── configuracoes.py
├── components/
│   └── widgets.py       # Componentes reutilizáveis do projeto
├── utils/
│   └── data.py          # Funções com @st.cache_data
└── requirements.txt
```

### 3. Padrão base de um app

```python
import streamlit as st

# --- Configuração da página (DEVE ser o primeiro comando st.*) ---
st.set_page_config(
    page_title="Meu App",
    page_icon="🎈",
    layout="wide",          # "centered" ou "wide"
    initial_sidebar_state="expanded"
)

# --- CSS customizado (opcional) ---
st.markdown("""
<style>
.metric-card { background: #f0f2f6; border-radius: 8px; padding: 16px; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Configurações")
    opcao = st.selectbox("Modo", ["A", "B"])

# --- Conteúdo principal ---
st.title("Meu App 🎈")
st.divider()

# ... lógica do app
```

---

## API rápida — os mais usados

### Texto
```python
st.title("Título")          # h1
st.header("Cabeçalho")      # h2
st.subheader("Subtítulo")   # h3
st.markdown("**negrito** _itálico_ `code`")
st.caption("texto pequeno")
st.divider()
st.badge("Novo", color="blue")
```

### Layout
```python
# Colunas
col1, col2, col3 = st.columns([2, 1, 1])  # proporções
with col1:
    st.write("coluna maior")

# Tabs
tab1, tab2 = st.tabs(["📊 Dados", "⚙️ Config"])
with tab1:
    st.write("conteúdo da tab 1")

# Expander
with st.expander("Ver mais detalhes"):
    st.write("conteúdo oculto")

# Sidebar
with st.sidebar:
    st.write("menu lateral")

# Container
with st.container(border=True):
    st.write("caixa com borda")
```

### Widgets — Inputs
```python
# Texto
nome = st.text_input("Nome", placeholder="Digite aqui")
descricao = st.text_area("Descrição", height=150)

# Numérico
valor = st.number_input("Valor", min_value=0.0, max_value=100.0, step=0.5)
nivel = st.slider("Nível", 0, 100, value=50)

# Seleção
opcao = st.selectbox("Escolha", ["A", "B", "C"])
multiplos = st.multiselect("Tags", ["Python", "ML", "Web"])
ativo = st.toggle("Ativar modo escuro")
aceito = st.checkbox("Li e aceito os termos")
tipo = st.radio("Tipo", ["Básico", "Pro", "Enterprise"], horizontal=True)

# Data/Hora
data = st.date_input("Data")
hora = st.time_input("Hora")

# Arquivo
arquivo = st.file_uploader("Upload CSV", type=["csv", "xlsx"])

# Botões
if st.button("Salvar", type="primary"):
    st.success("Salvo!")

st.download_button("Baixar resultado", data=bytes_data, file_name="resultado.csv")
```

### Dados e gráficos
```python
st.dataframe(df, use_container_width=True)  # tabela interativa
st.data_editor(df, num_rows="dynamic")       # tabela editável
st.metric("Receita", "R$ 45.000", delta="+12%")

# Gráficos nativos
st.line_chart(df[["col1", "col2"]])
st.bar_chart(df.set_index("categoria")["valor"])
st.area_chart(df)
st.scatter_chart(df, x="col_x", y="col_y", color="categoria")
st.map(df[["lat", "lon"]])  # mapa

# Plotly (recomendado para gráficos avançados)
import plotly.express as px
fig = px.bar(df, x="mes", y="vendas", color="produto")
st.plotly_chart(fig, use_container_width=True)
```

### Status e feedback
```python
st.success("Operação concluída!")
st.error("Algo deu errado.")
st.warning("Atenção!")
st.info("Informação importante.")
st.toast("Salvo!", icon="✅")

with st.spinner("Carregando..."):
    time.sleep(2)

barra = st.progress(0, text="Processando...")
for i in range(100):
    barra.progress(i + 1, text=f"Processando {i+1}%")
```

### Estado e cache
```python
# Session State — persiste entre reruns
if "contador" not in st.session_state:
    st.session_state.contador = 0

st.session_state.contador += 1

# Cache de dados — para funções que buscam/processam dados
@st.cache_data
def carregar_dados(url: str):
    return pd.read_csv(url)

# Cache de recursos — para modelos ML, conexões DB
@st.cache_resource
def carregar_modelo():
    return load_model("modelo.pkl")
```

---

## Princípios de performance

1. **`@st.cache_data`** em toda função que lê arquivos, chama APIs ou transforma DataFrames grandes
2. **`@st.cache_resource`** para modelos ML, conexões de banco, clientes de API
3. **`st.session_state`** para guardar estado entre interações do usuário
4. Evite recalcular dentro de loops — pré-processe fora do fluxo principal
5. Use `st.fragment` para re-renderizar apenas parte do app (Streamlit ≥ 1.37)

---

## Para aprofundar

- Leia `references/api-cheatsheet.md` para referência completa da API
- Leia `references/patterns.md` para padrões avançados (multi-page, auth, DB)
- Leia `references/components.md` para componentes prontos copiáveis
- Veja `assets/templates/` para apps completos por tipo de uso

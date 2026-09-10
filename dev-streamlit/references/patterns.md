# Padrões Arquiteturais para Streamlit

---

## Padrão 1: Multi-Page App

### Estrutura de arquivos
```
app.py
pages/
  home.py
  analise.py
  configuracoes.py
  admin.py
```

### app.py
```python
import streamlit as st

st.set_page_config(page_title="Meu App", page_icon="🎈", layout="wide")

# Definir páginas condicionalmente (ex: só admin vê página de admin)
paginas = [
    st.Page("pages/home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/analise.py", title="Análise", icon="📊"),
    st.Page("pages/configuracoes.py", title="Config", icon="⚙️"),
]

if st.session_state.get("role") == "admin":
    paginas.append(st.Page("pages/admin.py", title="Admin", icon="🔒"))

pg = st.navigation(paginas)
pg.run()
```

### Página individual (pages/analise.py)
```python
import streamlit as st
import pandas as pd

# Estado compartilhado via session_state
if "dados" not in st.session_state:
    st.session_state.dados = None

st.title("📊 Análise de Dados")

# Conteúdo da página
...
```

---

## Padrão 2: Estado Centralizado

Use `st.session_state` como "store" global do app:

```python
# Em um módulo separado: state.py
import streamlit as st

def init_state():
    """Inicializar todos os estados do app."""
    defaults = {
        "usuario": None,
        "autenticado": False,
        "dados": None,
        "filtros": {},
        "pagina": "home",
        "tema": "light",
    }
    for chave, valor in defaults.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor

def get(chave, default=None):
    return st.session_state.get(chave, default)

def set(chave, valor):
    st.session_state[chave] = valor

def reset(*chaves):
    for chave in chaves:
        if chave in st.session_state:
            del st.session_state[chave]

# No app principal:
import state
state.init_state()

usuario = state.get("usuario")
state.set("dados", df_carregado)
```

---

## Padrão 3: Data Layer com Cache

```python
# data.py — camada de dados isolada
import streamlit as st
import pandas as pd
import sqlalchemy as sa

@st.cache_resource
def get_engine():
    """Conexão singleton com o banco de dados."""
    return sa.create_engine(st.secrets["DATABASE_URL"])

@st.cache_data(ttl=300)  # 5 minutos
def buscar_vendas(data_inicio: str, data_fim: str) -> pd.DataFrame:
    engine = get_engine()
    query = """
        SELECT * FROM vendas
        WHERE data_venda BETWEEN :inicio AND :fim
    """
    return pd.read_sql(query, engine, params={"inicio": data_inicio, "fim": data_fim})

@st.cache_data(ttl=3600)
def buscar_produtos() -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql("SELECT * FROM produtos WHERE ativo = true", engine)

# Invalidar cache específico
def invalidar_vendas():
    buscar_vendas.clear()
```

---

## Padrão 4: Callbacks e Reatividade

```python
# Callback para reação a mudanças
def ao_mudar_filtro():
    """Executado quando o filtro muda, antes do próximo rerun."""
    st.session_state.pagina_atual = 1  # Resetar paginação
    st.session_state.cache_invalido = True

def ao_selecionar_item(item_id):
    st.session_state.item_selecionado = item_id

# Widgets com callbacks
filtro = st.selectbox(
    "Categoria",
    options=categorias,
    on_change=ao_mudar_filtro
)

# Botão com argumento via partial
from functools import partial
for item in lista:
    st.button(
        f"Ver {item['nome']}",
        on_click=partial(ao_selecionar_item, item["id"]),
        key=f"btn_{item['id']}"
    )
```

---

## Padrão 5: Dashboard Analítico Completo

```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Dashboard")

# 1. Dados
@st.cache_data
def carregar():
    return pd.read_csv("dados.csv", parse_dates=["data"])

df = carregar()

# 2. Sidebar de filtros
with st.sidebar:
    st.header("Filtros")
    periodo = st.date_input("Período", value=(df.data.min(), df.data.max()))
    categorias = st.multiselect("Categorias", df.categoria.unique(), 
                                 default=df.categoria.unique())

# 3. Aplicar filtros
mask = (
    (df.data.dt.date >= periodo[0]) &
    (df.data.dt.date <= periodo[1]) &
    (df.categoria.isin(categorias))
)
df_filtrado = df[mask]

# 4. KPIs
st.title("📊 Dashboard de Vendas")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Receita Total", f"R$ {df_filtrado.valor.sum():,.0f}")
c2.metric("Pedidos", f"{len(df_filtrado):,}")
c3.metric("Ticket Médio", f"R$ {df_filtrado.valor.mean():,.0f}")
c4.metric("Clientes", f"{df_filtrado.cliente_id.nunique():,}")

st.divider()

# 5. Gráficos em tabs
tab1, tab2, tab3 = st.tabs(["📈 Evolução", "🥧 Distribuição", "📋 Detalhes"])

with tab1:
    serie = df_filtrado.groupby("data")["valor"].sum().reset_index()
    fig = px.area(serie, x="data", y="valor", title="Receita Diária")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    dist = df_filtrado.groupby("categoria")["valor"].sum().reset_index()
    fig = px.pie(dist, values="valor", names="categoria", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
```

---

## Padrão 6: App de Chatbot com IA

```python
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Assistente IA", page_icon="🤖")
st.title("🤖 Assistente Inteligente")

# Cliente (singleton)
@st.cache_resource
def get_client():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Inicializar histórico
if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {"role": "system", "content": "Você é um assistente útil e amigável."}
    ]

# Exibir histórico (pular system message)
for msg in st.session_state.mensagens[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input do usuário
if prompt := st.chat_input("Como posso ajudar?"):
    # Adicionar mensagem do usuário
    st.session_state.mensagens.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Gerar resposta com streaming
    with st.chat_message("assistant"):
        client = get_client()
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.mensagens,
            stream=True,
        )
        resposta = st.write_stream(
            chunk.choices[0].delta.content or ""
            for chunk in stream
            if chunk.choices[0].delta.content
        )
    
    st.session_state.mensagens.append({"role": "assistant", "content": resposta})

# Botão para limpar histórico
if st.sidebar.button("🗑️ Limpar conversa"):
    st.session_state.mensagens = st.session_state.mensagens[:1]
    st.rerun()
```

---

## Padrão 7: Upload, Processamento e Download

```python
import streamlit as st
import pandas as pd
import io

st.title("🔄 Processador de Dados")

arquivo = st.file_uploader("📂 Envie seu arquivo CSV ou Excel", 
                             type=["csv", "xlsx"])

if arquivo:
    # Carregamento
    with st.spinner("Carregando..."):
        if arquivo.name.endswith(".csv"):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo)
    
    st.success(f"✅ {len(df):,} registros carregados")
    
    # Configurações de processamento
    with st.expander("⚙️ Configurações de processamento"):
        remover_duplicados = st.checkbox("Remover duplicados", value=True)
        remover_nulos = st.checkbox("Remover linhas com valores nulos")
        colunas_manter = st.multiselect("Colunas a manter", df.columns.tolist(), 
                                         default=df.columns.tolist())
    
    if st.button("▶️ Processar", type="primary"):
        with st.spinner("Processando..."):
            resultado = df[colunas_manter].copy()
            if remover_duplicados:
                resultado = resultado.drop_duplicates()
            if remover_nulos:
                resultado = resultado.dropna()
        
        st.metric("Registros após processamento", len(resultado))
        st.dataframe(resultado.head(50), use_container_width=True)
        
        # Download
        buffer = io.BytesIO()
        resultado.to_excel(buffer, index=False)
        st.download_button(
            "📥 Baixar resultado",
            data=buffer.getvalue(),
            file_name="resultado_processado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
```

---

## Padrão 8: Configuração por secrets.toml

```toml
# .streamlit/secrets.toml (NÃO versionar este arquivo!)

# Banco de dados
DATABASE_URL = "postgresql://user:senha@host:5432/db"

# APIs
[openai]
api_key = "sk-..."

[google]
client_id = "..."
client_secret = "..."

# App config
[app]
titulo = "Meu App"
admin_email = "admin@empresa.com"
```

```python
# Acessar no código:
db_url = st.secrets["DATABASE_URL"]
openai_key = st.secrets["openai"]["api_key"]
admin = st.secrets["app"]["admin_email"]
```

---

## Padrão 9: Theming

```toml
# .streamlit/config.toml

[theme]
primaryColor = "#0066CC"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"   # "sans serif" | "serif" | "monospace"
```

---

## Padrão 10: Fragmentos para Performance

```python
# Isola parte do app que re-renderiza com frequência
# sem re-renderizar o app inteiro

@st.fragment
def grafico_interativo():
    """Esta função re-roda sozinha sem afetar o restante."""
    periodo = st.slider("Últimos N dias", 7, 365, 30)
    df_periodo = filtrar_por_periodo(df, periodo)
    fig = px.line(df_periodo, x="data", y="valor")
    st.plotly_chart(fig, use_container_width=True)

# App principal
st.title("Dashboard")
mostrar_kpis()    # renderiza uma vez
grafico_interativo()  # re-renderiza isoladamente
mostrar_tabela()  # não é afetado pelo slider acima
```

---

## Anti-padrões — O que evitar

```python
# ❌ ERRADO: leitura de arquivo sem cache
def pagina():
    df = pd.read_csv("grande_arquivo.csv")  # lê a cada interação!

# ✅ CERTO:
@st.cache_data
def carregar():
    return pd.read_csv("grande_arquivo.csv")

# ❌ ERRADO: conexão de banco sem cache
conn = psycopg2.connect(...)  # nova conexão a cada rerun!

# ✅ CERTO:
@st.cache_resource
def get_conn():
    return psycopg2.connect(...)

# ❌ ERRADO: lógica de negócio misturada com UI
valor = st.number_input("Desconto %")
preco_final = preco_original * (1 - valor/100)  # OK para simples
# Para cálculos complexos, separe em função pura testável

# ❌ ERRADO: estado mutável em variável global
lista_items = []  # reiniciada a cada rerun

# ✅ CERTO:
if "lista_items" not in st.session_state:
    st.session_state.lista_items = []
```

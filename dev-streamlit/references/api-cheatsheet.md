# Streamlit API Cheatsheet — Referência Completa

## Configuração de página

```python
st.set_page_config(
    page_title="App",           # título na aba do browser
    page_icon="🎈",             # ícone da aba (emoji ou URL de imagem)
    layout="wide",              # "centered" | "wide"
    initial_sidebar_state="expanded",  # "expanded" | "collapsed" | "auto"
    menu_items={
        "Get Help": "https://meusite.com/ajuda",
        "Report a bug": "https://meusite.com/bug",
        "About": "Meu app incrível v1.0"
    }
)
```

---

## Texto e tipografia

| Função | Uso |
|--------|-----|
| `st.title(text)` | Título h1 |
| `st.header(text, divider="gray")` | Cabeçalho h2 com linha opcional |
| `st.subheader(text)` | Subtítulo h3 |
| `st.markdown(text, unsafe_allow_html=False)` | Markdown / HTML |
| `st.text(text)` | Texto monoespaçado |
| `st.caption(text)` | Texto pequeno/legenda |
| `st.code(code, language="python")` | Bloco de código com highlight |
| `st.latex(formula)` | Fórmula LaTeX |
| `st.divider()` | Linha horizontal |
| `st.badge("Texto", color="blue")` | Badge colorido inline |
| `st.html("<tag>")` | HTML puro |
| `st.write(*args)` | Auto-detect: texto, df, dict, fig, etc. |

### Cores no Markdown (novidade)
```python
st.markdown(":red[texto vermelho] :blue[texto azul] :green[verde]")
st.markdown("<span style='color:#FF5733'>cor hex</span>", unsafe_allow_html=True)
```

---

## Widgets — Botões

```python
# Botão simples
clicked = st.button("Label", type="primary", icon="🚀", use_container_width=True)
# type: "primary" | "secondary" | "tertiary"

# Download
st.download_button(
    label="📥 Baixar CSV",
    data=df.to_csv(index=False),
    file_name="dados.csv",
    mime="text/csv"
)

# Link
st.link_button("Acessar docs", url="https://docs.streamlit.io")

# Menu dropdown de ações
escolha = st.menu_button("⚙️ Exportar", options=["CSV", "Excel", "PDF"])

# Navegação (multi-page)
st.page_link("pages/dados.py", label="Ver Dados", icon="📊")
```

---

## Widgets — Seleção

```python
# Checkbox
aceito = st.checkbox("Aceitar termos", value=False)

# Toggle (on/off)
modo_escuro = st.toggle("Modo escuro", value=False)

# Radio
opcao = st.radio(
    "Período",
    options=["Diário", "Semanal", "Mensal"],
    horizontal=True,        # exibir na horizontal
    captions=["24h", "7d", "30d"]  # legendas opcionais
)

# Selectbox (dropdown)
cidade = st.selectbox(
    "Cidade",
    options=df["cidade"].unique(),
    index=0,
    placeholder="Selecione..."
)

# Multiselect
tags = st.multiselect(
    "Categorias",
    options=["ML", "Web", "Data", "API"],
    default=["Web"],
    max_selections=3
)

# Pills (botões pill)
filtro = st.pills("Status", ["Ativo", "Inativo", "Pendente"], selection_mode="multi")

# Segmented control
view = st.segmented_control("Visualização", ["📊 Gráfico", "📋 Tabela", "🗺️ Mapa"])

# Select Slider (lista de opções)
tamanho = st.select_slider("Tamanho", options=["XS", "S", "M", "L", "XL"], value="M")

# Color picker
cor = st.color_picker("Cor do tema", value="#0066CC")

# Feedback (rating)
nota = st.feedback("stars")  # "stars" | "thumbs"
```

---

## Widgets — Numérico

```python
# Number input
qtd = st.number_input("Quantidade", min_value=1, max_value=1000, value=10, step=1)

# Slider (valor único ou range)
nivel = st.slider("Nível de confiança", 0.0, 1.0, value=0.8, step=0.05)
intervalo = st.slider("Faixa de preço", 0, 10000, value=(500, 5000))
```

---

## Widgets — Data e Hora

```python
data = st.date_input("Data", value="today", format="DD/MM/YYYY")
hora = st.time_input("Hora", value=datetime.time(9, 0), step=900)  # step em segundos
dt = st.datetime_input("Data e hora")

# Intervalo de datas
inicio, fim = st.date_input("Período", value=(date.today(), date.today()))
```

---

## Widgets — Texto

```python
nome = st.text_input("Nome", placeholder="Ex: João Silva", max_chars=100)

descricao = st.text_area(
    "Descrição",
    height=200,
    placeholder="Descreva aqui...",
    help="Dica de ajuda que aparece ao hover"
)

prompt = st.chat_input("Digite sua mensagem...")
```

---

## Widgets — Arquivos e Mídia

```python
# Upload de arquivo
arquivo = st.file_uploader(
    "Selecione o arquivo",
    type=["csv", "xlsx", "json", "pdf"],
    accept_multiple_files=False
)
if arquivo:
    df = pd.read_csv(arquivo)

# Câmera
foto = st.camera_input("Tirar foto")

# Áudio
audio = st.audio_input("Gravar áudio")
```

---

## Formulários (evitam reruns intermediários)

```python
with st.form("meu_form", clear_on_submit=False):
    nome = st.text_input("Nome")
    email = st.text_input("E-mail")
    mensagem = st.text_area("Mensagem")
    
    col1, col2 = st.columns(2)
    enviado = col1.form_submit_button("Enviar", type="primary")
    cancelado = col2.form_submit_button("Cancelar")

if enviado:
    # Processar somente após submit
    salvar_dados(nome, email, mensagem)
    st.success("Enviado com sucesso!")
```

---

## Layout e Containers

### Colunas
```python
# Proporções flexíveis
col1, col2, col3 = st.columns([3, 1, 1], gap="medium", vertical_alignment="center")
# gap: "small" | "medium" | "large"
# vertical_alignment: "top" | "center" | "bottom"

with col1:
    st.metric("Receita", "R$ 45k", "+12%")
```

### Tabs
```python
tabs = st.tabs(["📊 Overview", "📈 Análise", "⚙️ Config"])
with tabs[0]:
    mostrar_overview()
with tabs[1]:
    mostrar_analise()
```

### Expander
```python
with st.expander("🔍 Filtros avançados", expanded=False):
    col1, col2 = st.columns(2)
    inicio = col1.date_input("De")
    fim = col2.date_input("Até")
```

### Container com borda
```python
with st.container(border=True, height=400):
    # height cria scroll interno
    for item in lista_longa:
        st.write(item)
```

### Popover
```python
with st.popover("⚙️ Opções"):
    st.checkbox("Mostrar legendas")
    st.slider("Tamanho da fonte", 10, 24, 14)
```

### Empty (placeholder atualizável)
```python
placeholder = st.empty()
# Mais tarde no código:
placeholder.metric("Progresso", f"{valor}%")
# Ou para limpar:
placeholder.empty()
```

### Dialog (modal)
```python
@st.dialog("Confirmar exclusão")
def confirmar_exclusao(item_id):
    st.warning(f"Tem certeza que deseja excluir o item {item_id}?")
    col1, col2 = st.columns(2)
    if col1.button("Sim, excluir", type="primary"):
        deletar(item_id)
        st.rerun()
    if col2.button("Cancelar"):
        st.rerun()

# Chamar o dialog:
if st.button("Excluir"):
    confirmar_exclusao(item_id=42)
```

### Espaço
```python
st.space("small")   # "small" | "medium" | "large"
```

---

## Dados

```python
# DataFrame interativo (com sort, resize, busca)
st.dataframe(
    df,
    use_container_width=True,
    height=400,
    column_config={
        "preco": st.column_config.NumberColumn("Preço", format="R$ %.2f"),
        "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
        "ativo": st.column_config.CheckboxColumn("Ativo"),
        "url": st.column_config.LinkColumn("Link"),
        "imagem": st.column_config.ImageColumn("Foto"),
    },
    hide_index=True,
)

# Data editor (tabela editável)
df_editado = st.data_editor(
    df,
    num_rows="dynamic",   # permite adicionar/remover linhas
    use_container_width=True,
)

# Tabela estática
st.table(df.head(10))

# JSON/dicionário
st.json({"chave": "valor", "lista": [1, 2, 3]}, expanded=2)
```

### Métricas
```python
col1, col2, col3, col4 = st.columns(4)
col1.metric("Usuários", "12.543", delta="+234", delta_color="normal",
            delta_description="vs. mês anterior")
col2.metric("Receita", "R$ 89k", delta="-5%", delta_color="inverse")
col3.metric("Uptime", "99,9%")
col4.metric("Tickets", "47", delta="+8", delta_color="off")
```

---

## Gráficos

### Nativos (simples, rápidos)
```python
st.line_chart(df, x="data", y=["vendas", "meta"], color=["#FF5733", "#0066CC"])
st.bar_chart(df, x="produto", y="quantidade", horizontal=True)
st.area_chart(df)
st.scatter_chart(df, x="preco", y="volume", size="margem", color="categoria")
st.map(df[["lat", "lon"]], zoom=10)
```

### Plotly (recomendado para produção)
```python
import plotly.express as px
import plotly.graph_objects as go

# Bar chart
fig = px.bar(df, x="mes", y="receita", color="produto", barmode="group",
             title="Receita por Produto")
st.plotly_chart(fig, use_container_width=True)

# Line chart com múltiplas séries
fig = px.line(df, x="data", y="valor", color="categoria", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Pie / Donut
fig = px.pie(df, values="vendas", names="categoria", hole=0.4)
st.plotly_chart(fig, use_container_width=True)

# Scatter com tamanho e cor
fig = px.scatter(df, x="x", y="y", size="tamanho", color="grupo",
                 hover_data=["nome"])
st.plotly_chart(fig, use_container_width=True)
```

---

## Status e Feedback

```python
st.success("✅ Operação realizada com sucesso!")
st.error("❌ Erro ao processar os dados.")
st.warning("⚠️ Atenção: dados podem estar desatualizados.")
st.info("ℹ️ Informação importante para o usuário.")
st.exception(erro)  # exibe traceback de exceção

# Toast (notificação temporária)
st.toast("Configurações salvas!", icon="✅")

# Spinner de carregamento
with st.spinner("Carregando modelo..."):
    modelo = carregar_modelo()

# Barra de progresso
progresso = st.progress(0, text="Iniciando...")
for i, item in enumerate(lista):
    processar(item)
    progresso.progress((i+1)/len(lista), text=f"Item {i+1}/{len(lista)}")
progresso.empty()
```

---

## Chat

```python
# Inicializar histórico
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Exibir histórico
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):  # "user" | "assistant"
        st.markdown(msg["content"])

# Input do usuário
if prompt := st.chat_input("Digite sua mensagem..."):
    # Adicionar mensagem do usuário
    st.session_state.mensagens.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Resposta do assistente com streaming
    with st.chat_message("assistant"):
        resposta = st.write_stream(gerar_resposta(prompt))
    st.session_state.mensagens.append({"role": "assistant", "content": resposta})
```

---

## Execução e Controle de Fluxo

```python
st.rerun()               # forçar rerun do script
st.stop()                # parar execução aqui

# Reruns parciais (Streamlit ≥ 1.37)
@st.fragment
def componente_independente():
    valor = st.slider("Ajuste")
    st.line_chart(calcular(valor))

# Fragmento com rerun automático
@st.fragment(run_every="5s")
def painel_tempo_real():
    dados = buscar_dados_live()
    st.metric("Preço atual", dados["preco"])
```

---

## Session State

```python
# Inicialização segura
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# Leitura
usuario_logado = st.session_state.get("usuario")

# Escrita
st.session_state["usuario"] = {"nome": "João", "role": "admin"}
st.session_state.contador += 1

# Callback com state
def ao_clicar():
    st.session_state.modo = "editando"

st.button("Editar", on_click=ao_clicar)
```

---

## Cache

```python
# Para dados — invalida automaticamente se os argumentos mudarem
@st.cache_data(ttl=3600)  # TTL em segundos
def buscar_dados(data_inicio: str, data_fim: str) -> pd.DataFrame:
    return consultar_banco(data_inicio, data_fim)

# Para recursos globais — singleton por sessão
@st.cache_resource
def conectar_banco():
    return psycopg2.connect(st.secrets["DATABASE_URL"])

@st.cache_resource
def carregar_modelo_ml():
    return joblib.load("modelo.pkl")

# Limpar cache manualmente
if st.button("Atualizar dados"):
    buscar_dados.clear()
    st.rerun()
```

---

## Secrets e Configurações

```python
# .streamlit/secrets.toml
# DATABASE_URL = "postgresql://..."
# [api_keys]
# openai = "sk-..."

# Acessar no código:
db_url = st.secrets["DATABASE_URL"]
openai_key = st.secrets["api_keys"]["openai"]
```

---

## Multi-page (navegação)

```python
# app.py — entry point
import streamlit as st

pg = st.navigation([
    st.Page("pages/home.py", title="Home", icon="🏠"),
    st.Page("pages/dados.py", title="Dados", icon="📊"),
    st.Page("pages/config.py", title="Config", icon="⚙️"),
])
pg.run()
```

---

## Mídia

```python
st.image("logo.png", caption="Logo", use_container_width=True, link="https://site.com")
st.video("video.mp4", start_time=30)
st.audio("audio.mp3")
```

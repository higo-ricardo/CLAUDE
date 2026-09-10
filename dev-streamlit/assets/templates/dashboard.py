"""
TEMPLATE: Dashboard Analítico
Uso: Dashboard de KPIs com gráficos, filtros e exportação
Adapte: colunas do DataFrame, métricas, título
Dependências: pip install streamlit pandas plotly openpyxl
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import io
from datetime import date, timedelta
import numpy as np

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Dados de exemplo (substitua pela sua fonte) ──────────────
@st.cache_data
def gerar_dados_exemplo():
    np.random.seed(42)
    datas = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
    categorias = ["Produto A", "Produto B", "Produto C"]
    regioes = ["Sul", "Sudeste", "Norte", "Nordeste"]
    
    registros = []
    for data in datas:
        for _ in range(np.random.randint(3, 10)):
            registros.append({
                "data": data,
                "produto": np.random.choice(categorias),
                "regiao": np.random.choice(regioes),
                "valor": np.random.uniform(100, 5000),
                "quantidade": np.random.randint(1, 50),
                "cliente_id": np.random.randint(1, 500),
            })
    return pd.DataFrame(registros)

df = gerar_dados_exemplo()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Filtros")
    
    data_min = df["data"].min().date()
    data_max = df["data"].max().date()
    periodo = st.date_input(
        "Período",
        value=(date.today() - timedelta(days=90), date.today()),
        min_value=data_min,
        max_value=data_max
    )
    
    produtos = st.multiselect(
        "Produtos",
        options=df["produto"].unique(),
        default=df["produto"].unique()
    )
    
    regioes = st.multiselect(
        "Regiões",
        options=df["regiao"].unique(),
        default=df["regiao"].unique()
    )
    
    st.divider()
    granularidade = st.radio("Granularidade", ["Diário", "Semanal", "Mensal"], index=2)

# ── Aplicar filtros ───────────────────────────────────────────
if len(periodo) == 2:
    inicio, fim = periodo
    mask = (
        (df["data"].dt.date >= inicio) &
        (df["data"].dt.date <= fim) &
        (df["produto"].isin(produtos)) &
        (df["regiao"].isin(regioes))
    )
    df_f = df[mask].copy()
else:
    df_f = df.copy()

# ── Título ────────────────────────────────────────────────────
st.title("📊 Dashboard de Vendas")
if len(periodo) == 2:
    st.caption(f"Período: {inicio.strftime('%d/%m/%Y')} → {fim.strftime('%d/%m/%Y')}")
st.divider()

# ── KPIs ─────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
receita = df_f["valor"].sum()
pedidos = len(df_f)
ticket = df_f["valor"].mean() if pedidos else 0
clientes = df_f["cliente_id"].nunique()

c1.metric("💰 Receita Total", f"R$ {receita:,.0f}")
c2.metric("📦 Pedidos", f"{pedidos:,}")
c3.metric("🎯 Ticket Médio", f"R$ {ticket:,.0f}")
c4.metric("👥 Clientes Únicos", f"{clientes:,}")

st.divider()

# ── Gráficos ─────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Evolução", "🏆 Produtos", "🗺️ Regiões", "📋 Detalhes"])

with tab1:
    freq_map = {"Diário": "D", "Semanal": "W", "Mensal": "ME"}
    serie = (
        df_f.set_index("data")
        .resample(freq_map[granularidade])["valor"]
        .sum()
        .reset_index()
    )
    fig = px.area(
        serie, x="data", y="valor",
        title=f"Receita {granularidade}",
        labels={"valor": "Receita (R$)", "data": ""},
        color_discrete_sequence=["#0066CC"]
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    col_a, col_b = st.columns(2)
    
    por_produto = df_f.groupby("produto")["valor"].sum().reset_index()
    fig_bar = px.bar(
        por_produto.sort_values("valor", ascending=True),
        x="valor", y="produto", orientation="h",
        title="Receita por Produto",
        color="produto",
        labels={"valor": "Receita (R$)", "produto": ""}
    )
    col_a.plotly_chart(fig_bar, use_container_width=True)
    
    fig_pie = px.pie(por_produto, values="valor", names="produto",
                      title="Participação %", hole=0.5)
    col_b.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    por_regiao = df_f.groupby("regiao")[["valor", "quantidade"]].sum().reset_index()
    fig = px.bar(
        por_regiao.sort_values("valor", ascending=False),
        x="regiao", y="valor",
        color="regiao",
        title="Receita por Região",
        labels={"valor": "Receita (R$)", "regiao": "Região"}
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.dataframe(
        df_f.sort_values("data", ascending=False).head(500),
        use_container_width=True,
        hide_index=True,
        column_config={
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
        }
    )
    
    buffer = io.BytesIO()
    df_f.to_excel(buffer, index=False)
    st.download_button(
        "📥 Exportar Excel",
        data=buffer.getvalue(),
        file_name="dashboard_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

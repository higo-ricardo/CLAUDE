# Componentes Reutilizáveis para Streamlit

Componentes prontos para copiar e adaptar em qualquer projeto.

---

## 1. Metric Card (card de KPI)

```python
def metric_card(titulo: str, valor, delta=None, icone="📊", cor="#0066CC"):
    """Card de métrica estilizado com fundo colorido."""
    delta_html = ""
    if delta is not None:
        sinal = "▲" if str(delta).startswith("+") or (isinstance(delta, (int, float)) and delta > 0) else "▼"
        cor_delta = "green" if sinal == "▲" else "red"
        delta_html = f'<span style="color:{cor_delta};font-size:0.85rem">{sinal} {delta}</span>'
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {cor}15, {cor}30);
        border-left: 4px solid {cor};
        border-radius: 8px;
        padding: 16px 20px;
        margin: 4px 0;
    ">
        <div style="font-size:1.5rem">{icone}</div>
        <div style="color:#888;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:1px">
            {titulo}
        </div>
        <div style="font-size:1.8rem;font-weight:bold;color:#1a1a1a;margin:4px 0">
            {valor}
        </div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# Uso:
col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Receita Total", "R$ 145.230", delta="+18%", icone="💰", cor="#0066CC")
with col2:
    metric_card("Usuários Ativos", "2.847", delta="+234", icone="👥", cor="#00AA44")
with col3:
    metric_card("Taxa de Erro", "0,3%", delta="-0,1%", icone="⚠️", cor="#FF5733")
```

---

## 2. Sidebar de Filtros

```python
def sidebar_filtros(df: pd.DataFrame, colunas_categoricas: list, 
                    colunas_data: list = None) -> pd.DataFrame:
    """
    Gera sidebar de filtros automaticamente a partir das colunas do DataFrame.
    Retorna o DataFrame filtrado.
    """
    with st.sidebar:
        st.header("🔍 Filtros")
        
        df_filtrado = df.copy()
        
        # Filtros de data
        if colunas_data:
            for col in colunas_data:
                if col in df.columns:
                    st.subheader(f"📅 {col}")
                    df[col] = pd.to_datetime(df[col])
                    data_min = df[col].min().date()
                    data_max = df[col].max().date()
                    intervalo = st.date_input(
                        f"Período ({col})",
                        value=(data_min, data_max),
                        key=f"filtro_data_{col}"
                    )
                    if len(intervalo) == 2:
                        inicio, fim = intervalo
                        df_filtrado = df_filtrado[
                            (df_filtrado[col].dt.date >= inicio) &
                            (df_filtrado[col].dt.date <= fim)
                        ]
        
        # Filtros categóricos
        for col in colunas_categoricas:
            if col in df.columns:
                opcoes = sorted(df[col].dropna().unique().tolist())
                selecionados = st.multiselect(
                    col.replace("_", " ").title(),
                    options=opcoes,
                    default=opcoes,
                    key=f"filtro_{col}"
                )
                if selecionados:
                    df_filtrado = df_filtrado[df_filtrado[col].isin(selecionados)]
        
        # Info do resultado
        st.divider()
        total = len(df)
        filtrado = len(df_filtrado)
        st.caption(f"📊 {filtrado:,} de {total:,} registros")
        
        if st.button("🔄 Limpar filtros", use_container_width=True):
            st.rerun()
    
    return df_filtrado

# Uso:
df_filtrado = sidebar_filtros(
    df,
    colunas_categoricas=["categoria", "status", "regiao"],
    colunas_data=["data_venda"]
)
```

---

## 3. Header com navegação

```python
def header_app(titulo: str, subtitulo: str = "", versao: str = "1.0"):
    """Header profissional com título, subtítulo e badges."""
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title(titulo)
        if subtitulo:
            st.caption(subtitulo)
    with col2:
        st.badge(f"v{versao}", color="blue")
        st.caption(f"📅 {pd.Timestamp.now().strftime('%d/%m/%Y')}")
    st.divider()

# Uso:
header_app("Dashboard de Vendas", "Análise em tempo real", versao="2.1")
```

---

## 4. Tabela com busca e paginação

```python
def tabela_paginada(df: pd.DataFrame, linhas_por_pagina: int = 20,
                    titulo: str = ""):
    """DataFrame com barra de busca e paginação."""
    if titulo:
        st.subheader(titulo)
    
    # Busca
    busca = st.text_input("🔍 Buscar", placeholder="Filtrar registros...", 
                           label_visibility="collapsed")
    
    if busca:
        mask = df.astype(str).apply(lambda x: x.str.contains(busca, case=False)).any(axis=1)
        df = df[mask]
    
    total = len(df)
    total_paginas = max(1, (total - 1) // linhas_por_pagina + 1)
    
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        pagina = st.number_input("Página", min_value=1, max_value=total_paginas, 
                                  value=1, label_visibility="collapsed")
    
    inicio = (pagina - 1) * linhas_por_pagina
    fim = inicio + linhas_por_pagina
    
    st.dataframe(df.iloc[inicio:fim], use_container_width=True, hide_index=True)
    st.caption(f"Página {pagina} de {total_paginas} · {total:,} registros")

# Uso:
tabela_paginada(df, linhas_por_pagina=25, titulo="📋 Lista de Clientes")
```

---

## 5. Upload com preview automático

```python
def upload_com_preview(tipos: list = ["csv", "xlsx"],
                        label: str = "Selecione o arquivo") -> pd.DataFrame | None:
    """Upload de arquivo com preview automático e validação."""
    arquivo = st.file_uploader(label, type=tipos)
    
    if arquivo is None:
        return None
    
    try:
        with st.spinner("Carregando arquivo..."):
            if arquivo.name.endswith(".csv"):
                # Detectar separador automaticamente
                conteudo = arquivo.read()
                arquivo.seek(0)
                sep = ";" if conteudo[:200].count(b";") > conteudo[:200].count(b",") else ","
                df = pd.read_csv(arquivo, sep=sep)
            elif arquivo.name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(arquivo)
            else:
                st.error("Formato não suportado.")
                return None
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Linhas", f"{len(df):,}")
        col2.metric("Colunas", len(df.columns))
        col3.metric("Tamanho", f"{arquivo.size / 1024:.1f} KB")
        
        with st.expander("👁️ Preview (primeiras 5 linhas)"):
            st.dataframe(df.head(), use_container_width=True)
        
        with st.expander("📊 Tipos de dados"):
            tipos_df = df.dtypes.reset_index()
            tipos_df.columns = ["Coluna", "Tipo"]
            tipos_df["Nulos"] = df.isnull().sum().values
            st.dataframe(tipos_df, use_container_width=True, hide_index=True)
        
        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return None

# Uso:
df = upload_com_preview(tipos=["csv", "xlsx"], label="📂 Upload do relatório")
if df is not None:
    processar(df)
```

---

## 6. Formulário de contato / cadastro

```python
def formulario_contato(titulo: str = "📬 Entre em Contato",
                        campos_extras: dict = None) -> dict | None:
    """
    Formulário de contato genérico.
    campos_extras: {"label": "tipo"} onde tipo é "text", "textarea", "select", "number"
    Retorna dict com os dados ou None se não enviado.
    """
    st.subheader(titulo)
    
    with st.form("formulario_contato", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome *", placeholder="Seu nome completo")
        email = col2.text_input("E-mail *", placeholder="seu@email.com")
        
        extras = {}
        if campos_extras:
            for label, tipo in campos_extras.items():
                key = label.lower().replace(" ", "_")
                if tipo == "textarea":
                    extras[key] = st.text_area(label)
                elif tipo == "text":
                    extras[key] = st.text_input(label)
                elif tipo == "number":
                    extras[key] = st.number_input(label, min_value=0)
        
        mensagem = st.text_area("Mensagem *", height=120, placeholder="Escreva aqui...")
        
        col1, col2 = st.columns([1, 3])
        enviado = col1.form_submit_button("✉️ Enviar", type="primary", use_container_width=True)
    
    if enviado:
        erros = []
        if not nome:
            erros.append("Nome é obrigatório")
        if not email or "@" not in email:
            erros.append("E-mail inválido")
        if not mensagem:
            erros.append("Mensagem é obrigatória")
        
        if erros:
            for erro in erros:
                st.error(f"❌ {erro}")
            return None
        
        dados = {"nome": nome, "email": email, "mensagem": mensagem, **extras}
        st.success("✅ Mensagem enviada com sucesso!")
        return dados
    
    return None

# Uso:
resultado = formulario_contato(
    titulo="📬 Fale Conosco",
    campos_extras={"Telefone": "text", "Assunto": "text"}
)
if resultado:
    salvar_no_banco(resultado)
```

---

## 7. Painel de monitoramento em tempo real

```python
def painel_tempo_real(fn_dados, intervalo_seg: int = 5, 
                       titulo: str = "🔴 Live"):
    """
    Painel que se atualiza automaticamente.
    fn_dados: função que retorna dict {"metrica": valor}
    """
    st.subheader(titulo)
    st.caption(f"Atualização a cada {intervalo_seg}s")
    
    @st.fragment(run_every=f"{intervalo_seg}s")
    def _inner():
        dados = fn_dados()
        cols = st.columns(len(dados))
        for col, (nome, valor) in zip(cols, dados.items()):
            col.metric(nome, valor)
        st.caption(f"Última atualização: {pd.Timestamp.now().strftime('%H:%M:%S')}")
    
    _inner()

# Uso:
def meus_dados_live():
    return {
        "CPU": f"{psutil.cpu_percent():.1f}%",
        "RAM": f"{psutil.virtual_memory().percent:.1f}%",
        "Disco": f"{psutil.disk_usage('/').percent:.1f}%",
    }

painel_tempo_real(meus_dados_live, intervalo_seg=3, titulo="🖥️ Monitoramento")
```

---

## 8. Autenticação simples (sem banco)

```python
USUARIOS = {
    "admin": "senha123",
    "usuario": "abc456"
}

def login_screen() -> bool:
    """Tela de login simples. Retorna True se autenticado."""
    if st.session_state.get("autenticado"):
        return True
    
    st.title("🔐 Login")
    
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar", type="primary")
    
    if entrar:
        if USUARIOS.get(usuario) == senha:
            st.session_state.autenticado = True
            st.session_state.usuario_logado = usuario
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos.")
    
    return False

def logout():
    st.session_state.autenticado = False
    st.session_state.usuario_logado = None
    st.rerun()

# Uso no app.py:
if not login_screen():
    st.stop()

# App principal
with st.sidebar:
    st.caption(f"👤 {st.session_state.usuario_logado}")
    if st.button("Sair"):
        logout()
```

---

## 9. Stepper (formulário multi-etapas)

```python
def stepper(etapas: list[str]) -> int:
    """
    Exibe indicador de progresso em etapas.
    Retorna o índice da etapa atual.
    """
    if "etapa_atual" not in st.session_state:
        st.session_state.etapa_atual = 0
    
    etapa = st.session_state.etapa_atual
    total = len(etapas)
    
    # Barra visual
    progresso = (etapa) / (total - 1) if total > 1 else 1.0
    st.progress(progresso)
    
    # Labels das etapas
    cols = st.columns(total)
    for i, (col, nome) in enumerate(zip(cols, etapas)):
        if i < etapa:
            col.markdown(f"✅ ~~{nome}~~")
        elif i == etapa:
            col.markdown(f"**🔵 {nome}**")
        else:
            col.markdown(f"⬜ {nome}")
    
    st.divider()
    return etapa

def avancar_etapa():
    st.session_state.etapa_atual += 1

def voltar_etapa():
    st.session_state.etapa_atual -= 1

# Uso:
ETAPAS = ["Dados Pessoais", "Endereço", "Pagamento", "Confirmação"]
etapa = stepper(ETAPAS)

if etapa == 0:
    nome = st.text_input("Nome completo")
    cpf = st.text_input("CPF")
    col1, col2 = st.columns([5, 1])
    col2.button("Próximo →", on_click=avancar_etapa, type="primary")

elif etapa == 1:
    rua = st.text_input("Rua")
    cidade = st.text_input("Cidade")
    col1, col2 = st.columns(2)
    col1.button("← Voltar", on_click=voltar_etapa)
    col2.button("Próximo →", on_click=avancar_etapa, type="primary")
```

---

## 10. Exportador de dados

```python
def botoes_exportar(df: pd.DataFrame, nome_arquivo: str = "dados"):
    """Botões de exportação para CSV, Excel e JSON."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "📥 CSV",
            data=df.to_csv(index=False, encoding="utf-8-sig"),
            file_name=f"{nome_arquivo}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Dados")
        st.download_button(
            "📥 Excel",
            data=buffer.getvalue(),
            file_name=f"{nome_arquivo}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col3:
        st.download_button(
            "📥 JSON",
            data=df.to_json(orient="records", force_ascii=False, indent=2),
            file_name=f"{nome_arquivo}.json",
            mime="application/json",
            use_container_width=True
        )

# Uso:
st.subheader("📊 Resultados")
st.dataframe(df_resultado, use_container_width=True)
botoes_exportar(df_resultado, nome_arquivo="relatorio_vendas")
```

"""
TEMPLATE: App CRUD (Create, Read, Update, Delete)
Uso: Gerenciamento de registros com interface completa
Adapte: campos do formulário, lógica de persistência
Dependências: pip install streamlit pandas
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import json

st.set_page_config(page_title="Gerenciador", page_icon="📋", layout="wide")

# ── "Banco de dados" em session_state (substitua por DB real) ─
if "registros" not in st.session_state:
    st.session_state.registros = [
        {"id": 1, "nome": "Item Exemplo", "categoria": "A", 
         "valor": 99.90, "ativo": True, "criado_em": "2024-01-01"},
    ]
    st.session_state.proximo_id = 2

# ── Helpers ───────────────────────────────────────────────────
def get_df():
    return pd.DataFrame(st.session_state.registros)

def adicionar(nome, categoria, valor, ativo):
    st.session_state.registros.append({
        "id": st.session_state.proximo_id,
        "nome": nome,
        "categoria": categoria,
        "valor": valor,
        "ativo": ativo,
        "criado_em": datetime.now().strftime("%Y-%m-%d"),
    })
    st.session_state.proximo_id += 1

def atualizar(id_, nome, categoria, valor, ativo):
    for r in st.session_state.registros:
        if r["id"] == id_:
            r.update({"nome": nome, "categoria": categoria, 
                       "valor": valor, "ativo": ativo})
            break

def deletar(id_):
    st.session_state.registros = [
        r for r in st.session_state.registros if r["id"] != id_
    ]

# ── UI ────────────────────────────────────────────────────────
st.title("📋 Gerenciador de Registros")

tab_lista, tab_novo, tab_exportar = st.tabs(["📋 Lista", "➕ Novo Registro", "📥 Exportar"])

# ── TAB 1: Lista ─────────────────────────────────────────────
with tab_lista:
    df = get_df()
    
    if df.empty:
        st.info("Nenhum registro cadastrado ainda.")
    else:
        # Filtros rápidos
        col1, col2, col3 = st.columns([2, 2, 1])
        busca = col1.text_input("🔍 Buscar", placeholder="Nome...")
        cat_filtro = col2.selectbox("Categoria", ["Todas"] + sorted(df["categoria"].unique().tolist()))
        so_ativos = col3.toggle("Só ativos", value=False)
        
        df_vis = df.copy()
        if busca:
            df_vis = df_vis[df_vis["nome"].str.contains(busca, case=False)]
        if cat_filtro != "Todas":
            df_vis = df_vis[df_vis["categoria"] == cat_filtro]
        if so_ativos:
            df_vis = df_vis[df_vis["ativo"] == True]
        
        st.caption(f"{len(df_vis)} de {len(df)} registros")
        
        # Tabela com ações por linha
        for _, row in df_vis.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1, 1])
                c1.write(f"**{row['nome']}**")
                c2.caption(f"Categoria: {row['categoria']}")
                c3.write(f"R$ {row['valor']:.2f}")
                c4.write("✅" if row["ativo"] else "❌")
                
                with c5:
                    col_e, col_d = st.columns(2)
                    if col_e.button("✏️", key=f"edit_{row['id']}", help="Editar"):
                        st.session_state.editando_id = row["id"]
                        st.session_state.editando_dados = row.to_dict()
                    if col_d.button("🗑️", key=f"del_{row['id']}", help="Excluir"):
                        st.session_state.confirmar_delete = row["id"]
        
        # Modal de edição
        if "editando_id" in st.session_state:
            dados = st.session_state.editando_dados
            
            @st.dialog(f"✏️ Editar Registro #{dados['id']}")
            def modal_edicao():
                nome = st.text_input("Nome", value=dados["nome"])
                col1, col2 = st.columns(2)
                cat = col1.selectbox("Categoria", ["A", "B", "C"], 
                                      index=["A","B","C"].index(dados["categoria"]))
                val = col2.number_input("Valor", value=float(dados["valor"]), step=0.01)
                ativo = st.toggle("Ativo", value=bool(dados["ativo"]))
                
                c1, c2 = st.columns(2)
                if c1.button("💾 Salvar", type="primary"):
                    atualizar(dados["id"], nome, cat, val, ativo)
                    del st.session_state.editando_id
                    st.toast("Registro atualizado!", icon="✅")
                    st.rerun()
                if c2.button("Cancelar"):
                    del st.session_state.editando_id
                    st.rerun()
            
            modal_edicao()
        
        # Confirmação de delete
        if "confirmar_delete" in st.session_state:
            id_del = st.session_state.confirmar_delete
            
            @st.dialog("⚠️ Confirmar exclusão")
            def modal_delete():
                st.warning(f"Tem certeza que deseja excluir o registro #{id_del}?")
                c1, c2 = st.columns(2)
                if c1.button("🗑️ Sim, excluir", type="primary"):
                    deletar(id_del)
                    del st.session_state.confirmar_delete
                    st.toast("Registro excluído.", icon="🗑️")
                    st.rerun()
                if c2.button("Cancelar"):
                    del st.session_state.confirmar_delete
                    st.rerun()
            
            modal_delete()

# ── TAB 2: Novo Registro ──────────────────────────────────────
with tab_novo:
    st.subheader("➕ Cadastrar Novo Registro")
    
    with st.form("novo_registro", clear_on_submit=True):
        nome = st.text_input("Nome *", placeholder="Nome do item")
        
        col1, col2 = st.columns(2)
        categoria = col1.selectbox("Categoria *", ["A", "B", "C"])
        valor = col2.number_input("Valor (R$) *", min_value=0.0, step=0.01)
        
        ativo = st.toggle("Ativo", value=True)
        
        salvar = st.form_submit_button("💾 Salvar", type="primary")
    
    if salvar:
        if not nome:
            st.error("❌ Nome é obrigatório.")
        elif valor <= 0:
            st.error("❌ Valor deve ser maior que zero.")
        else:
            adicionar(nome, categoria, valor, ativo)
            st.success(f"✅ Registro '{nome}' cadastrado com sucesso!")

# ── TAB 3: Exportar ───────────────────────────────────────────
with tab_exportar:
    st.subheader("📥 Exportar Dados")
    df = get_df()
    
    if df.empty:
        st.info("Nenhum dado para exportar.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        col1.download_button(
            "📥 Baixar CSV",
            data=df.to_csv(index=False, encoding="utf-8-sig"),
            file_name="registros.csv",
            mime="text/csv",
            use_container_width=True
        )
        col2.download_button(
            "📥 Baixar JSON",
            data=df.to_json(orient="records", force_ascii=False, indent=2),
            file_name="registros.json",
            mime="application/json",
            use_container_width=True
        )

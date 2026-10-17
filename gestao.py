import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gestão Mensal & ROI | Tour360vr",
    page_icon="📈",
    layout="wide"
)

# --- BANCO DE DADOS (SQLite) ---
DB_NAME = "gestao_gmb.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tabela de Clientes
    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_empresa TEXT NOT NULL,
            responsavel TEXT,
            whatsapp TEXT,
            data_inicio TEXT
        )
    ''')
    # Tabela de Métricas Mensais
    c.execute('''
        CREATE TABLE IF NOT EXISTS metricas_mensais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            mes_ano TEXT NOT NULL,
            chamadas INTEGER DEFAULT 0,
            rotas INTEGER DEFAULT 0,
            cliques_site INTEGER DEFAULT 0,
            visualizacoes INTEGER DEFAULT 0,
            novas_avaliacoes INTEGER DEFAULT 0,
            resumo_acoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- FUNÇÕES DE SUPORTE ---
def obter_clientes():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT id, nome_empresa FROM clientes ORDER BY nome_empresa", conn)
    conn.close()
    return df

# --- ESTILIZAÇÃO CSS (Dark + Neon) ---
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #E0E6ED; }
    .main-title { color: #FFFFFF; font-weight: 800; font-size: 1.8rem; text-shadow: 0 0 10px rgba(0, 229, 255, 0.5); }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>📈 Gestão Mensal & Performance ROI GMB</h1>", unsafe_allow_html=True)

# --- ABAS DA APLICAÇÃO ---
aba1, aba2, aba3 = st.tabs(["📋 Inserir Métricas", "📊 Dashboard & ROI", "⚙️ Cadastrar Clientes"])

# ==========================================
# ABA 1: INSERIR MÉTRICAS DO MÊS
# ==========================================
with aba1:
    st.subheader("Registo de Performance Mensal")
    df_clientes = obter_clientes()
    
    if df_clientes.empty:
        st.warning("Nenhum cliente cadastrado. Registe um cliente na aba 'Cadastrar Clientes' primeiro.")
    else:
        with st.form("form_metricas"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                cliente_sel = st.selectbox("Selecione o Cliente", df_clientes["nome_empresa"].tolist())
                cliente_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_sel]["id"].values[0])
            with col_c2:
                mes_referencia = st.date_input("Mês de Referência", value=datetime.today()).strftime("%Y-%m")

            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                chamadas = st.number_input("📞 Chamadas Telefónicas", min_value=0, step=1)
            with c2:
                rotas = st.number_input("🗺️ Solicitações de Rota", min_value=0, step=1)
            with c3:
                cliques_site = st.number_input("🌐 Cliques no Site/WhatsApp", min_value=0, step=1)
            with c4:
                visualizacoes = st.number_input("👁️ Total de Visualizações", min_value=0, step=1)

            novas_avaliacoes = st.number_input("⭐ Novas Avaliações Recebidas", min_value=0, step=1)
            resumo_acoes = st.text_area("🛠️ Ações Realizadas no Mês (Otimizações, fotos 360°, posts, etc.)")

            btn_salvar_metricas = st.form_submit_button("Salvar Métricas do Mês")

            if btn_salvar_metricas:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute('''
                    INSERT INTO metricas_mensais 
                    (cliente_id, mes_ano, chamadas, rotas, cliques_site, visualizacoes, novas_avaliacoes, resumo_acoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (cliente_id, mes_referencia, chamadas, rotas, cliques_site, visualizacoes, novas_avaliacoes, resumo_acoes))
                conn.commit()
                conn.close()
                st.success(f"Métricas do mês {mes_referencia} salvas com sucesso para {cliente_sel}!")

# ==========================================
# ABA 2: DASHBOARD & DESEMPENHO
# ==========================================
with aba2:
    st.subheader("Análise de Desempenho e ROI")
    df_clientes = obter_clientes()
    
    if not df_clientes.empty:
        cliente_dash = st.selectbox("Selecione o Cliente para Visualizar", df_clientes["nome_empresa"].tolist(), key="dash_cliente")
        cliente_id_dash = int(df_clientes[df_clientes["nome_empresa"] == cliente_dash]["id"].values[0])
        
        conn = sqlite3.connect(DB_NAME)
        df_metricas = pd.read_sql_query(
            "SELECT mes_ano, chamadas, rotas, cliques_site, visualizacoes, novas_avaliacoes FROM metricas_mensais WHERE cliente_id = ? ORDER BY mes_ano ASC", 
            conn, params=(cliente_id_dash,)
        )
        conn.close()

        if df_metricas.empty:
            st.info("Ainda não existem métricas registadas para este cliente.")
        else:
            # Exibição de Métricas Recentes
            ultimas = df_metricas.iloc[-1]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Chamadas (Último Mês)", ultimas["chamadas"])
            m2.metric("Rotas (Último Mês)", ultimas["rotas"])
            m3.metric("Cliques Site/Whats", ultimas["cliques_site"])
            m4.metric("Visualizações Ficha", ultimas["visualizacoes"])

            st.markdown("---")
            st.line_chart(df_metricas.set_index("mes_ano")[["chamadas", "rotas", "cliques_site"]])

# ==========================================
# ABA 3: CADASTRAR CLIENTES
# ==========================================
with aba3:
    st.subheader("Registo de Novo Cliente de Gestão")
    with st.form("form_cliente"):
        nome_empresa = st.text_input("Nome da Empresa / Ficha GMB")
        responsavel = st.text_input("Nome do Responsável")
        whatsapp = st.text_input("WhatsApp de Contacto")
        btn_cadastrar = st.form_submit_button("Cadastrar Cliente")

        if btn_cadastrar and nome_empresa:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute(
                "INSERT INTO clientes (nome_empresa, responsavel, whatsapp, data_inicio) VALUES (?, ?, ?, ?)",
                (nome_empresa, responsavel, whatsapp, datetime.today().strftime("%Y-%m-%d"))
            )
            conn.commit()
            conn.close()
            st.success(f"Cliente '{nome_empresa}' cadastrado com sucesso!")
            st.rerun()

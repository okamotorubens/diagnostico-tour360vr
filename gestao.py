import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# Importações do ReportLab para PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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
    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_empresa TEXT NOT NULL,
            responsavel TEXT,
            whatsapp TEXT,
            data_inicio TEXT
        )
    ''')
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

def obter_clientes():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT id, nome_empresa FROM clientes ORDER BY nome_empresa", conn)
    conn.close()
    return df

# --- FUNÇÃO DE GERAÇÃO DO RELATÓRIO PDF ---
def gerar_pdf_relatorio(nome_empresa, mes_ano, chamadas, rotas, cliques, visualizacoes, avaliacoes, acoes):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.HexColor('#00E5FF')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#94A3B8')
    )
    section_style = ParagraphStyle(
        'DocSection', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#1E2640')
    )
    body_style = ParagraphStyle(
        'DocBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#334155')
    )

    # Cabeçalho do Relatório
    story.append(Paragraph("<b>TOUR360VR — GESTÃO MENSAL GMB</b>", title_style))
    story.append(Paragraph(f"Relatório Executivo de Performance | <b>{nome_empresa}</b> — Mês: <b>{mes_ano}</b>", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#00E5FF'), spaceAfter=15))

    # Tabela de Métricas
    data_table = [
        [Paragraph("<b>Indicador de Desempenho</b>", section_style), Paragraph("<b>Resultado do Mês</b>", section_style)],
        [Paragraph("📞 Chamadas Telefónicas Diretas", body_style), Paragraph(f"<b>{chamadas}</b>", body_style)],
        [Paragraph("🗺️ Solicitações de Rota (GPS)", body_style), Paragraph(f"<b>{rotas}</b>", body_style)],
        [Paragraph("🌐 Cliques no Website / WhatsApp", body_style), Paragraph(f"<b>{cliques}</b>", body_style)],
        [Paragraph("👁️ Visualizações Totais da Ficha", body_style), Paragraph(f"<b>{visualizacoes}</b>", body_style)],
        [Paragraph("⭐ Novas Avaliações Recebidas", body_style), Paragraph(f"<b>{avaliacoes}</b>", body_style)],
    ]

    t = Table(data_table, colWidths=[320, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Ações Realizadas
    story.append(Paragraph("<b>Ações e Otimizações Executadas no Período:</b>", section_style))
    story.append(Spacer(1, 6))
    acoes_texto = acoes if acoes else "Otimizações de rotina e monitorização contínua do perfil."
    story.append(Paragraph(acoes_texto.replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 20))

    # Rodapé
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94A3B8'), spaceAfter=10))
    story.append(Paragraph("<b>Okamoto Mídias Visuais & Tour360vr</b> — Gestão e Estratégia de Presença Local", subtitle_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #E0E6ED; }
    .main-title { color: #FFFFFF; font-weight: 800; font-size: 1.8rem; text-shadow: 0 0 10px rgba(0, 229, 255, 0.5); }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>📈 Gestão Mensal & Performance ROI GMB</h1>", unsafe_allow_html=True)

# --- ABAS DA APLICAÇÃO ---
aba1, aba2, aba3, aba4 = st.tabs(["📋 Inserir Métricas", "📊 Dashboard & ROI", "📄 Relatório PDF", "⚙️ Cadastrar Clientes"])

# ==========================================
# ABA 1: INSERIR MÉTRICAS
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
# ABA 2: DASHBOARD & ROI
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
            ultimas = df_metricas.iloc[-1]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Chamadas (Último Mês)", ultimas["chamadas"])
            m2.metric("Rotas (Último Mês)", ultimas["rotas"])
            m3.metric("Cliques Site/Whats", ultimas["cliques_site"])
            m4.metric("Visualizações Ficha", ultimas["visualizacoes"])

            st.markdown("---")
            st.line_chart(df_metricas.set_index("mes_ano")[["chamadas", "rotas", "cliques_site"]])

# ==========================================
# ABA 3: RELATÓRIO PDF
# ==========================================
with aba3:
    st.subheader("Emitir Relatório em PDF")
    df_clientes = obter_clientes()

    if df_clientes.empty:
        st.info("Registe um cliente e insira métricas para gerar o relatório.")
    else:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            cliente_pdf_sel = st.selectbox("Selecione o Cliente", df_clientes["nome_empresa"].tolist(), key="pdf_cliente")
            cliente_pdf_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_pdf_sel]["id"].values[0])

        conn = sqlite3.connect(DB_NAME)
        df_m = pd.read_sql_query(
            "SELECT * FROM metricas_mensais WHERE cliente_id = ? ORDER BY mes_ano DESC", 
            conn, params=(cliente_pdf_id,)
        )
        conn.close()

        if df_m.empty:
            st.warning("Nenhuma métrica encontrada para este cliente.")
        else:
            with col_r2:
                mes_pdf_sel = st.selectbox("Selecione o Mês", df_m["mes_ano"].tolist())

            dados_mes = df_m[df_m["mes_ano"] == mes_pdf_sel].iloc[0]

            st.markdown("---")
            st.write(f"**Resumo Selecionado:** {cliente_pdf_sel} - Mês {mes_pdf_sel}")

            pdf_bytes = gerar_pdf_relatorio(
                nome_empresa=cliente_pdf_sel,
                mes_ano=dados_mes["mes_ano"],
                chamadas=dados_mes["chamadas"],
                rotas=dados_mes["rotas"],
                cliques=dados_mes["cliques_site"],
                visualizacoes=dados_mes["visualizacoes"],
                avaliacoes=dados_mes["novas_avaliacoes"],
                acoes=dados_mes["resumo_acoes"]
            )

            st.download_button(
                label="📥 Baixar Relatório Executivo em PDF",
                data=pdf_bytes,
                file_name=f"Relatorio_GMB_{cliente_pdf_sel.replace(' ', '_')}_{mes_pdf_sel}.pdf",
                mime="application/pdf"
            )

# ==========================================
# ABA 4: CADASTRAR CLIENTES
# ==========================================
with aba4:
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

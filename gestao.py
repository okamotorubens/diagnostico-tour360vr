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

# --- BANCO DE DADOS (SQLite Expandido com Ficha GMB Completa) ---
DB_NAME = "gestao_gmb.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Tabela de Clientes Completa
    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_empresa TEXT UNIQUE NOT NULL,
            responsavel TEXT,
            data_abertura TEXT,
            categoria_principal TEXT,
            categorias_secundarias TEXT,
            descricao_empresa TEXT,
            telefone_contato TEXT,
            whatsapp TEXT,
            chat_status TEXT,
            website TEXT,
            redes_sociais TEXT,
            endereco_local TEXT,
            area_cobertura TEXT,
            horario_funcionamento TEXT,
            horarios_especiais TEXT,
            outros_horarios TEXT,
            observacoes_tecnicas TEXT,
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

# Busca apenas clientes ÚNICOS
def obter_clientes_unicos():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT DISTINCT id, nome_empresa FROM clientes ORDER BY nome_empresa ASC", conn)
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

    story.append(Paragraph("<b>TOUR360VR — GESTÃO MENSAL GMB</b>", title_style))
    story.append(Paragraph(f"Relatório Executivo de Performance | <b>{nome_empresa}</b> — Mês: <b>{mes_ano}</b>", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#00E5FF'), spaceAfter=15))

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

    story.append(Paragraph("<b>Ações e Otimizações Executadas no Período:</b>", section_style))
    story.append(Spacer(1, 6))
    acoes_texto = acoes if acoes else "Otimizações de rotina e monitorização contínua do perfil."
    story.append(Paragraph(acoes_texto.replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 20))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94A3B8'), spaceAfter=10))
    story.append(Paragraph("<b>Okamoto Mídias Visuais & Tour360vr</b> — Gestão e Estratégia de Presença Local", subtitle_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- CSS PERSONALIZADO (Padrão Unificado Neon) ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 98% !important;
    }
    
    header[data-testid="stHeader"] {
        display: none !important;
    }

    .stApp {
        background-color: #0B0E14;
        color: #E0E6ED;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main-title {
        color: #FFFFFF;
        font-weight: 800;
        font-size: 1.85rem;
        text-shadow: 0 0 12px rgba(0, 229, 255, 0.6);
        margin-bottom: 1.2rem;
    }

    /* BOTÕES DE NAVEGAÇÃO SUPERIOR DO HUB */
    div[data-testid="stColumn"] > div > div > button {
        width: 100% !important;
        background-color: #121824 !important;
        border: 1.5px solid #FFFFFF !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        padding: 10px 6px !important;
        font-weight: 700 !important;
        font-size: 0.90rem !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 0 5px rgba(255, 255, 255, 0.15) !important;
    }

    div[data-testid="stColumn"] > div > div > button:hover {
        border-color: #00E5FF !important;
        color: #00E5FF !important;
        box-shadow: 0 0 16px #00E5FF !important;
        background-color: #161F30 !important;
        transform: translateY(-2px) !important;
    }

    div[data-testid="stColumn"] > div > div > button[kind="primary"] {
        background-color: #161F30 !important;
        border-color: #00E5FF !important;
        color: #00E5FF !important;
        box-shadow: 0 0 14px #00E5FF !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown("<h1 class='main-title'>📈 Gestão Mensal & Performance ROI GMB</h1>", unsafe_allow_html=True)

# --- CONTROLADOR DE NAVEGAÇÃO PRINCIPAL ---
if "aba_ativa" not in st.session_state:
    st.session_state["aba_ativa"] = "cadastrar"

col_n1, col_n2, col_n3, col_n4 = st.columns(4)

with col_n1:
    if st.button("⚙️ Cadastrar Cliente & Ficha", key="btn_cad", type="primary" if st.session_state["aba_ativa"] == "cadastrar" else "secondary"):
        st.session_state["aba_ativa"] = "cadastrar"
        st.rerun()

with col_n2:
    if st.button("📋 Inserir Métricas Mensais", key="btn_inc", type="primary" if st.session_state["aba_ativa"] == "metricas" else "secondary"):
        st.session_state["aba_ativa"] = "metricas"
        st.rerun()

with col_n3:
    if st.button("📊 Dashboard & ROI", key="btn_dash", type="primary" if st.session_state["aba_ativa"] == "dashboard" else "secondary"):
        st.session_state["aba_ativa"] = "dashboard"
        st.rerun()

with col_n4:
    if st.button("📄 Relatório Executivo PDF", key="btn_pdf", type="primary" if st.session_state["aba_ativa"] == "pdf" else "secondary"):
        st.session_state["aba_ativa"] = "pdf"
        st.rerun()

st.markdown("<hr style='margin: 12px 0 20px 0; border-color: #1E2640;'>", unsafe_allow_html=True)

# ==========================================
# MÓDULO 1: CADASTRAR CLIENTE & FICHA COMPLETA (PAINEL GMB)
# ==========================================
if st.session_state["aba_ativa"] == "cadastrar":
    st.subheader("⚙️ Cadastro do Cliente & Mapeamento de Informações Comerciais (GMB)")
    
    with st.form("form_cliente_gmb_completo"):
        sub_tab_sobre, sub_tab_contato, sub_tab_local, sub_tab_horario, sub_tab_mais = st.tabs([
            "🏢 Sobre", "📞 Contato", "📍 Local & Áreas", "⏰ Horários", "🛠️ Mais / Pendências"
        ])
        
        # SUB-ABA 1: SOBRE
        with sub_tab_sobre:
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                nome_empresa = st.text_input("Nome Comercial da Empresa / Ficha GMB *")
                responsavel = st.text_input("Nome do Responsável / Contato")
                data_abertura = st.text_input("Data de Abertura (Mês/Ano)")
            with c_s2:
                categoria_principal = st.text_input("Categoria Principal no GMB (ex: Serviço de fotografia)")
                categorias_secundarias = st.text_input("Categorias Secundárias (ex: Fotógrafo comercial, Produção de Vídeo)")
            
            descricao_empresa = st.text_area("Descrição Oficial da Empresa (Otimizada para SEO Local)", height=100)

        # SUB-ABA 2: CONTATO
        with sub_tab_contato:
            c_c1, c_c2 = st.columns(2)
            with c_c1:
                telefone_contato = st.text_input("Número de Telefone Comercial")
                whatsapp = st.text_input("WhatsApp para Atendimento")
                chat_status = st.selectbox("Mensagens / Chat no Perfil", ["Ativado", "Desativado", "Não Configurado"])
            with c_c2:
                website = st.text_input("Website / Link Principal")
                redes_sociais = st.text_input("Perfis das Redes Sociais (Instagram, Facebook, LinkedIn)")

        # SUB-ABA 3: LOCAL & ÁREAS
        with sub_tab_local:
            c_l1, c_l2 = st.columns(2)
            with c_l1:
                endereco_local = st.text_input("Local da Empresa (Endereço Completo ou 'Ficha Sem Endereço Exibido')")
            with c_l2:
                area_cobertura = st.text_input("Áreas de Cobertura / Atendimento (Cidades, Bairros, Regiões)")

        # SUB-ABA 4: HORÁRIOS
        with sub_tab_horario:
            c_h1, c_h2 = st.columns(2)
            with c_h1:
                horario_funcionamento = st.text_input("Horário Padrão (ex: Segunda a Sexta: 08:00 - 18:00)")
                horarios_especiais = st.text_input("Horários Especiais / Feriados")
            with c_h2:
                outros_horarios = st.text_input("Outros Horários (Almoço, Happy Hour, Drive-thru, Delivery)")

        # SUB-ABA 5: MAIS / PENDÊNCIAS
        with sub_tab_mais:
            observacoes_tecnicas = st.text_area("Pendências de Otimização e Observações Técnicas da Ficha", height=100)

        st.markdown("---")
        btn_cadastrar = st.form_submit_button("Salvar Ficha Completa do Cliente")

        if btn_cadastrar and nome_empresa:
            try:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute('''
                    INSERT INTO clientes 
                    (nome_empresa, responsavel, data_abertura, categoria_principal, categorias_secundarias, descricao_empresa, telefone_contato, whatsapp, chat_status, website, redes_sociais, endereco_local, area_cobertura, horario_funcionamento, horarios_especiais, outros_horarios, observacoes_tecnicas, data_inicio) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    nome_empresa, responsavel, data_abertura, categoria_principal, categorias_secundarias, descricao_empresa, telefone_contato, whatsapp, chat_status, website, redes_sociais, endereco_local, area_cobertura, horario_funcionamento, horarios_especiais, outros_horarios, observacoes_tecnicas, datetime.today().strftime("%Y-%m-%d")
                ))
                conn.commit()
                conn.close()
                st.success(f"Ficha comercial de '{nome_empresa}' cadastrada com sucesso!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error(f"O cliente '{nome_empresa}' já está cadastrado no sistema!")

# ==========================================
# MÓDULO 2: INSERIR MÉTRICAS MENSAIS
# ==========================================
elif st.session_state["aba_ativa"] == "metricas":
    st.subheader("📋 Lançamento de Performance Mensal")
    df_clientes = obter_clientes_unicos()
    
    if df_clientes.empty:
        st.warning("Nenhum cliente cadastrado. Cadastre um cliente na aba '⚙️ Cadastrar Cliente & Ficha'.")
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
                st.success(f"Métricas salvas para {cliente_sel} no período {mes_referencia}!")

# ==========================================
# MÓDULO 3: DASHBOARD & ROI
# ==========================================
elif st.session_state["aba_ativa"] == "dashboard":
    st.subheader("📊 Análise de Desempenho e ROI")
    df_clientes = obter_clientes_unicos()
    
    if df_clientes.empty:
        st.info("Nenhum cliente cadastrado ainda.")
    else:
        cliente_dash = st.selectbox("Selecione o Cliente para Visualizar", df_clientes["nome_empresa"].tolist(), key="dash_cliente")
        cliente_id_dash = int(df_clientes[df_clientes["nome_empresa"] == cliente_dash]["id"].values[0])
        
        conn = sqlite3.connect(DB_NAME)
        df_metricas = pd.read_sql_query(
            "SELECT mes_ano, chamadas, rotas, cliques_site, visualizacoes, novas_avaliacoes FROM metricas_mensais WHERE cliente_id = ? ORDER BY mes_ano ASC", 
            conn, params=(cliente_id_dash,)
        )
        conn.close()

        if df_metricas.empty:
            st.info("Ainda não existem métricas registradas para este cliente.")
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
# MÓDULO 4: RELATÓRIO PDF
# ==========================================
elif st.session_state["aba_ativa"] == "pdf":
    st.subheader("📄 Emitir Relatório Executivo em PDF")
    df_clientes = obter_clientes_unicos()

    if df_clientes.empty:
        st.info("Cadastre um cliente e insira métricas para gerar o relatório.")
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

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

# --- BANCO DE DADOS (SQLite com Métricas Iniciais de Avaliações) ---
DB_NAME = "gestao_gmb.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Tabela Principal de Clientes
    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_empresa TEXT UNIQUE NOT NULL,
            responsavel TEXT,
            data_abertura TEXT,
            ficha_reivindicada TEXT,
            status_avaliacoes TEXT,
            qtd_avaliacoes_inicio INTEGER DEFAULT 0,
            nota_media_inicio REAL DEFAULT 0.0,
            status_respostas_avaliacoes TEXT,
            categoria_principal TEXT,
            categorias_secundarias TEXT,
            descricao_empresa TEXT,
            telefone_contato TEXT,
            whatsapp TEXT,
            chat_status TEXT,
            website TEXT,
            instagram TEXT,
            facebook TEXT,
            linkedin TEXT,
            youtube TEXT,
            tiktok TEXT,
            atendimento_local_cliente INTEGER DEFAULT 0,
            endereco_local TEXT,
            area_cobertura TEXT,
            horario_seg TEXT,
            horario_ter TEXT,
            horario_qua TEXT,
            horario_qui TEXT,
            horario_sex TEXT,
            horario_sab TEXT,
            horario_dom TEXT,
            horarios_especiais TEXT,
            outros_horarios TEXT,
            pendencias_checklist TEXT,
            observacoes_tecnicas TEXT,
            data_inicio TEXT
        )
    ''')

    # Tabela de Histórico / Auditoria da Ficha
    c.execute('''
        CREATE TABLE IF NOT EXISTS historico_ficha (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data_alteracao TEXT,
            descricao_alteracao TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
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

def obter_clientes_unicos():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT DISTINCT id, nome_empresa FROM clientes ORDER BY nome_empresa ASC", conn)
    conn.close()
    return df

def obter_dados_cliente_por_id(cliente_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
    row = c.fetchone()
    conn.close()
    return row

# --- LISTA DE HORÁRIOS PRÉ-CONFIGURADOS (Intervalos de 30 min) ---
HORARIOS_OPCOES = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]

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

# --- CSS PERSONALIZADO ---
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

    /* BOTÕES DA BARRA DE NAVEGAÇÃO - PADRÃO DO HUB */
    div[data-testid="stColumn"] > div > div > button {
        width: 100% !important;
        background: #121824 !important;
        border: 1.5px solid #FFFFFF !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        padding: 12px 10px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.12) !important;
        transition: all 0.3s ease-in-out !important;
    }

    div[data-testid="stColumn"] > div > div > button:hover {
        border-color: #00E5FF !important;
        color: #00E5FF !important;
        box-shadow: 0 0 18px #00E5FF, 0 0 28px rgba(0, 229, 255, 0.4) !important;
        background: #161F30 !important;
        transform: translateY(-3px) !important;
    }

    div[data-testid="stColumn"] > div > div > button[kind="primary"] {
        background: #161F30 !important;
        border-color: #00E5FF !important;
        color: #00E5FF !important;
        box-shadow: 0 0 18px #00E5FF !important;
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
    if st.button("⚙️ Cadastrar / Editar Ficha", key="btn_cad", type="primary" if st.session_state["aba_ativa"] == "cadastrar" else "secondary"):
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
# MÓDULO 1: CADASTRAR / EDITAR FICHA DO CLIENTE
# ==========================================
if st.session_state["aba_ativa"] == "cadastrar":
    st.subheader("⚙️ Cadastro e Atualização de Informações Comerciais (GMB)")
    
    df_clientes_existentes = obter_clientes_unicos()
    modo_edicao = False
    dados_existentes = None
    
    if not df_clientes_existentes.empty:
        opcoes_clientes = ["➕ Cadastrar Novo Cliente"] + df_clientes_existentes["nome_empresa"].tolist()
        cliente_selecionado_menu = st.selectbox("Selecione para Cadastrar ou Editar um Cliente Existente:", opcoes_clientes)
        
        if cliente_selecionado_menu != "➕ Cadastrar Novo Cliente":
            modo_edicao = True
            c_id = int(df_clientes_existentes[df_clientes_existentes["nome_empresa"] == cliente_selecionado_menu]["id"].values[0])
            dados_existentes = obter_dados_cliente_por_id(c_id)
            st.info(f"Modo de Edição Ativo: Alterando a Ficha de **{cliente_selecionado_menu}**.")

    with st.form("form_cliente_gmb_completo"):
        sub_tab_sobre, sub_tab_contato, sub_tab_local, sub_tab_horario, sub_tab_mais, sub_tab_historico = st.tabs([
            "🏢 Sobre & Status Ficha", "📞 Contato & Redes", "📍 Local & Áreas", "⏰ Horários Rápidos", "🛠️ Checklist de Pendências", "📜 Histórico de Alterações"
        ])
        
        # SUB-ABA 1: SOBRE & AUDITORIA DA FICHA
        with sub_tab_sobre:
            st.markdown("**Identificação Comercial & Auditoria Inicial:**")
            c_s1, c_s2 = st.columns(2)
            
            opts_reivindicada = ["Reivindicada & Verificada", "Não Reivindicada / Perfil Aberto", "Em Processo de Verificação"]
            opts_avaliacoes = ["Possui Avaliações (Com Nota Exibida)", "Sem Avaliações Recebidas"]
            opts_respostas = ["100% Respondidas", "Parcialmente Respondidas", "Nenhuma Avaliação Respondida", "N/A (Sem Avaliações)"]

            with c_s1:
                nome_empresa = st.text_input("Nome Comercial da Empresa / Ficha GMB *", value=dados_existentes[1] if modo_edicao else "")
                responsavel = st.text_input("Nome do Responsável / Contato Interno", value=dados_existentes[2] if modo_edicao else "")
                data_abertura = st.text_input("Data de Abertura (Mês/Ano)", value=dados_existentes[3] if modo_edicao else "")
                
                idx_reiv = opts_reivindicada.index(dados_existentes[4]) if (modo_edicao and dados_existentes[4] in opts_reivindicada) else 0
                ficha_reivindicada = st.selectbox("Status de Reivindicação da Ficha", opts_reivindicada, index=idx_reiv)
                
                idx_resp = opts_respostas.index(dados_existentes[8]) if (modo_edicao and len(dados_existentes) > 8 and dados_existentes[8] in opts_respostas) else 0
                status_respostas_avaliacoes = st.selectbox("Status de Resposta às Avaliações", opts_respostas, index=idx_resp)

            with c_s2:
                categoria_principal = st.text_input("Categoria Principal no GMB (ex: Serviço de fotografia)", value=dados_existentes[9] if (modo_edicao and len(dados_existentes) > 9) else "")
                categorias_secundarias = st.text_input("Categorias Secundárias (separadas por vírgula)", value=dados_existentes[10] if (modo_edicao and len(dados_existentes) > 10) else "")
                
                idx_aval = opts_avaliacoes.index(dados_existentes[5]) if (modo_edicao and dados_existentes[5] in opts_avaliacoes) else 0
                status_avaliacoes = st.selectbox("Possui Avaliações de Clientes?", opts_avaliacoes, index=idx_aval)

                # CAMPOS DE PONTO DE PARTIDA DAS AVALIAÇÕES (ROI ANCORAGEM)
                st.markdown("**Métricas das Avaliações no Início da Gestão:**")
                col_av1, col_av2 = st.columns(2)
                with col_av1:
                    qtd_avaliacoes_inicio = st.number_input(
                        "Quantidade Inicial de Avaliações",
                        min_value=0, step=1,
                        value=int(dados_existentes[6]) if (modo_edicao and len(dados_existentes) > 6 and dados_existentes[6] is not None) else 0
                    )
                with col_av2:
                    nota_media_inicio = st.number_input(
                        "Nota Média Inicial (0.0 a 5.0)",
                        min_value=0.0, max_value=5.0, step=0.1,
                        value=float(dados_existentes[7]) if (modo_edicao and len(dados_existentes) > 7 and dados_existentes[7] is not None) else 5.0
                    )
            
            st.markdown("---")
            descricao_empresa = st.text_area("Descrição Oficial da Empresa (Otimizada para SEO Local)", value=dados_existentes[11] if (modo_edicao and len(dados_existentes) > 11) else "", height=200)

        # SUB-ABA 2: CONTATO & REDES SOCIAIS
        with sub_tab_contato:
            opts_chat = ["Ativado", "Desativado", "Não Configurado"]
            c_c1, c_c2 = st.columns(2)
            with c_c1:
                telefone_contato = st.text_input("Número de Telefone Comercial", value=dados_existentes[12] if (modo_edicao and len(dados_existentes) > 12) else "")
                whatsapp = st.text_input("WhatsApp para Atendimento", value=dados_existentes[13] if (modo_edicao and len(dados_existentes) > 13) else "")
                website = st.text_input("Website / Link Principal", value=dados_existentes[15] if (modo_edicao and len(dados_existentes) > 15) else "")
                
                chat_val = dados_existentes[14] if (modo_edicao and len(dados_existentes) > 14) else "Ativado"
                idx_chat = opts_chat.index(chat_val) if chat_val in opts_chat else 0
                chat_status = st.selectbox("Mensagens / Chat no Perfil", opts_chat, index=idx_chat)
            with c_c2:
                instagram = st.text_input("Link do Instagram", value=dados_existentes[16] if (modo_edicao and len(dados_existentes) > 16) else "")
                facebook = st.text_input("Link do Facebook", value=dados_existentes[17] if (modo_edicao and len(dados_existentes) > 17) else "")
                linkedin = st.text_input("Link do LinkedIn", value=dados_existentes[18] if (modo_edicao and len(dados_existentes) > 18) else "")
                youtube = st.text_input("Link do YouTube", value=dados_existentes[19] if (modo_edicao and len(dados_existentes) > 19) else "")
                tiktok = st.text_input("Link do TikTok", value=dados_existentes[20] if (modo_edicao and len(dados_existentes) > 20) else "")

        # SUB-ABA 3: LOCAL & ÁREAS
        with sub_tab_local:
            atend_val = bool(dados_existentes[21]) if (modo_edicao and len(dados_existentes) > 21) else False
            atendimento_local_cliente = st.checkbox("📍 Atendimento no local do cliente / Prestador de serviço itinerante (Endereço oculto no Google)", value=atend_val)
            st.markdown("---")
            c_l1, c_l2 = st.columns(2)
            with c_l1:
                endereco_local = st.text_input("Endereço Físico Completo", value=dados_existentes[22] if (modo_edicao and len(dados_existentes) > 22) else "")
            with c_l2:
                area_cobertura = st.text_input("Áreas de Cobertura / Atendimento (ex: Ribeirão Preto, Sertãozinho, Brodowski)", value=dados_existentes[23] if (modo_edicao and len(dados_existentes) > 23) else "")

        # SUB-ABA 4: HORÁRIOS RÁPIDOS
        with sub_tab_horario:
            st.markdown("**Horários de Funcionamento (Clique para selecionar a hora pré-configurada):**")
            
            dias_semana = [
                ("Segunda-feira", 24, "08:00", "18:00", False),
                ("Terça-feira", 25, "08:00", "18:00", False),
                ("Quarta-feira", 26, "08:00", "18:00", False),
                ("Quinta-feira", 27, "08:00", "18:00", False),
                ("Sexta-feira", 28, "08:00", "18:00", False),
                ("Sábado", 29, "08:00", "12:00", False),
                ("Domingo", 30, "08:00", "12:00", True)
            ]
            
            horarios_coletados = {}

            for dia_nome, idx_db, h_ab_def, h_fe_def, fechado_def in dias_semana:
                st.markdown(f"**{dia_nome}**")
                col_h1, col_h2, col_h3 = st.columns([2, 2, 1])
                
                is_fechado = fechado_def
                val_ab = h_ab_def
                val_fe = h_fe_def

                if modo_edicao and len(dados_existentes) > idx_db and dados_existentes[idx_db]:
                    txt_h = dados_existentes[idx_db]
                    if txt_h == "Fechado":
                        is_fechado = True
                    elif " - " in txt_h:
                        is_fechado = False
                        parts = txt_h.split(" - ")
                        if len(parts) == 2:
                            val_ab = parts[0]
                            val_fe = parts[1]

                with col_h3:
                    fechado = st.checkbox("Fechado", key=f"chk_fechado_{dia_nome}", value=is_fechado)
                with col_h1:
                    idx_ab = HORARIOS_OPCOES.index(val_ab) if val_ab in HORARIOS_OPCOES else HORARIOS_OPCOES.index("08:00")
                    h_abre_sel = st.selectbox(f"Abertura ({dia_nome})", HORARIOS_OPCOES, index=idx_ab, disabled=fechado, key=f"sel_ab_{dia_nome}")
                with col_h2:
                    idx_fe = HORARIOS_OPCOES.index(val_fe) if val_fe in HORARIOS_OPCOES else HORARIOS_OPCOES.index("18:00")
                    h_fecha_sel = st.selectbox(f"Fechamento ({dia_nome})", HORARIOS_OPCOES, index=idx_fe, disabled=fechado, key=f"sel_fe_{dia_nome}")
                
                if fechado:
                    horarios_coletados[dia_nome] = "Fechado"
                else:
                    horarios_coletados[dia_nome] = f"{h_abre_sel} - {h_fecha_sel}"

            st.markdown("---")
            c_he1, c_he2 = st.columns(2)
            with c_he1:
                horarios_especiais = st.text_input("Horários Especiais / Feriados (ex: 25/12 Fechado)", value=dados_existentes[31] if (modo_edicao and len(dados_existentes) > 31) else "")
            with c_he2:
                outros_horarios = st.text_input("Outros Horários (Almoço, Happy Hour, Delivery)", value=dados_existentes[32] if (modo_edicao and len(dados_existentes) > 32) else "")

        # SUB-ABA 5: CHECKLIST DE PENDÊNCIAS
        with sub_tab_mais:
            st.markdown("**Checklist de Otimização Identificadas no Diagnóstico:**")
            pendencias_salvas = dados_existentes[33] if (modo_edicao and len(dados_existentes) > 33 and dados_existentes[33]) else ""

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                p_fita = st.checkbox("📷 Cadastrar / Atualizar Tour Virtual 360° & Fotos", value="Fotos/Tour 360°" in pendencias_salvas)
                p_cat = st.checkbox("🏷️ Otimizar Categoria Principal e Categorias Secundárias", value="Categorias GMB" in pendencias_salvas)
                p_desc = st.checkbox("✍️ Reescrever Descrição Comercial com SEO Local", value="Descrição SEO" in pendencias_salvas)
                p_redes = st.checkbox("🔗 Vincular Perfis Sociais (Instagram, Facebook, etc.)", value="Redes Sociais" in pendencias_salvas)
            with col_p2:
                p_chat = st.checkbox("💬 Ativar e Configurar Chat / Mensagens", value="Chat/Mensagens" in pendencias_salvas)
                p_prod = st.checkbox("🛍️ Cadastrar Produtos e/ou Lista de Serviços", value="Produtos/Serviços" in pendencias_salvas)
                p_aval = st.checkbox("⭐ Gerar Link Curto Direto para Solicitação de Avaliações", value="Link de Avaliações" in pendencias_salvas)
                p_hor = st.checkbox("⏰ Corrigir / Validar Horários Especiais e de Funcionamento", value="Ajuste de Horários" in pendencias_salvas)

            st.markdown("---")
            observacoes_tecnicas = st.text_area("Observações Técnicas Adicionais / Diagnóstico Específico", value=dados_existentes[34] if (modo_edicao and len(dados_existentes) > 34) else "", height=180)

        # SUB-ABA 6: HISTÓRICO DE AUDITORIA & ALTERAÇÕES
        with sub_tab_historico:
            if not modo_edicao:
                st.info("O histórico de alterações ficará disponível após o primeiro cadastro da ficha.")
            else:
                st.markdown(f"**Histórico de Registros e Otimizações Realizadas — {cliente_selecionado_menu}:**")
                conn = sqlite3.connect(DB_NAME)
                df_hist = pd.read_sql_query(
                    "SELECT data_alteracao as 'Data', descricao_alteracao as 'Alteração Realizada / Registro' FROM historico_ficha WHERE cliente_id = ? ORDER BY id DESC", 
                    conn, params=(c_id,)
                )
                conn.close()
                
                if df_hist.empty:
                    st.write("Ficha cadastrada na versão inicial (Sem alterações adicionais registradas).")
                else:
                    st.dataframe(df_hist, use_container_width=True)

        st.markdown("---")
        btn_salvar = st.form_submit_button("Salvar Nova Ficha" if not modo_edicao else "Atualizar Ficha e Gravar Histórico")

        if btn_salvar and nome_empresa:
            checklist_list = []
            if p_fita: checklist_list.append("Fotos/Tour 360°")
            if p_cat: checklist_list.append("Categorias GMB")
            if p_desc: checklist_list.append("Descrição SEO")
            if p_redes: checklist_list.append("Redes Sociais")
            if p_chat: checklist_list.append("Chat/Mensagens")
            if p_prod: checklist_list.append("Produtos/Serviços")
            if p_aval: checklist_list.append("Link de Avaliações")
            if p_hor: checklist_list.append("Ajuste de Horários")
            pendencias_str = ", ".join(checklist_list) if checklist_list else "Nenhuma pendência marcada"

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            if not modo_edicao:
                try:
                    c.execute('''
                        INSERT INTO clientes 
                        (nome_empresa, responsavel, data_abertura, ficha_reivindicada, status_avaliacoes, qtd_avaliacoes_inicio, nota_media_inicio, status_respostas_avaliacoes, categoria_principal, categorias_secundarias, descricao_empresa, telefone_contato, whatsapp, chat_status, website, instagram, facebook, linkedin, youtube, tiktok, atendimento_local_cliente, endereco_local, area_cobertura, horario_seg, horario_ter, horario_qua, horario_qui, horario_sex, horario_sab, horario_dom, horarios_especiais, outros_horarios, pendencias_checklist, observacoes_tecnicas, data_inicio) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        nome_empresa, responsavel, data_abertura, ficha_reivindicada, status_avaliacoes, qtd_avaliacoes_inicio, nota_media_inicio, status_respostas_avaliacoes, categoria_principal, categorias_secundarias, descricao_empresa, telefone_contato, whatsapp, chat_status, website, instagram, facebook, linkedin, youtube, tiktok, 1 if atendimento_local_cliente else 0, endereco_local, area_cobertura, 
                        horarios_coletados["Segunda-feira"], horarios_coletados["Terça-feira"], horarios_coletados["Quarta-feira"], horarios_coletados["Quinta-feira"], horarios_coletados["Sexta-feira"], horarios_coletados["Sábado"], horarios_coletados["Domingo"],
                        horarios_especiais, outros_horarios, pendencias_str, observacoes_tecnicas, datetime.today().strftime("%Y-%m-%d")
                    ))
                    cliente_novo_id = c.lastrowid
                    c.execute("INSERT INTO historico_ficha (cliente_id, data_alteracao, descricao_alteracao) VALUES (?, ?, ?)",
                              (cliente_novo_id, datetime.now().strftime("%Y-%m-%d %H:%M"), f"Cadastro Inicial da Ficha ({qtd_avaliacoes_inicio} avaliações / Nota {nota_media_inicio})"))
                    conn.commit()
                    st.success(f"Ficha comercial de '{nome_empresa}' cadastrada com sucesso!")
                except sqlite3.IntegrityError:
                    st.error(f"O cliente '{nome_empresa}' já está cadastrado no sistema!")
            else:
                c.execute('''
                    UPDATE clientes SET 
                    responsavel=?, data_abertura=?, ficha_reivindicada=?, status_avaliacoes=?, qtd_avaliacoes_inicio=?, nota_media_inicio=?, status_respostas_avaliacoes=?, categoria_principal=?, categorias_secundarias=?, descricao_empresa=?, telefone_contato=?, whatsapp=?, chat_status=?, website=?, instagram=?, facebook=?, linkedin=?, youtube=?, tiktok=?, atendimento_local_cliente=?, endereco_local=?, area_cobertura=?, horario_seg=?, horario_ter=?, horario_qua=?, horario_qui=?, horario_sex=?, horario_sab=?, horario_dom=?, horarios_especiais=?, outros_horarios=?, pendencias_checklist=?, observacoes_tecnicas=?
                    WHERE id=?
                ''', (
                    responsavel, data_abertura, ficha_reivindicada, status_avaliacoes, qtd_avaliacoes_inicio, nota_media_inicio, status_respostas_avaliacoes, categoria_principal, categorias_secundarias, descricao_empresa, telefone_contato, whatsapp, chat_status, website, instagram, facebook, linkedin, youtube, tiktok, 1 if atendimento_local_cliente else 0, endereco_local, area_cobertura, 
                    horarios_coletados["Segunda-feira"], horarios_coletados["Terça-feira"], horarios_coletados["Quarta-feira"], horarios_coletados["Quinta-feira"], horarios_coletados["Sexta-feira"], horarios_coletados["Sábado"], horarios_coletados["Domingo"],
                    horarios_especiais, outros_horarios, pendencias_str, observacoes_tecnicas, c_id
                ))
                
                c.execute("INSERT INTO historico_ficha (cliente_id, data_alteracao, descricao_alteracao) VALUES (?, ?, ?)",
                          (c_id, datetime.now().strftime("%Y-%m-%d %H:%M"), f"Atualização Ficha: Pendências ({pendencias_str}) / Categoria: {categoria_principal}"))
                conn.commit()
                st.success(f"Ficha comercial de '{nome_empresa}' atualizada e histórico registrado com sucesso!")
            
            conn.close()
            st.rerun()

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

            novas_avaliacoes = st.number_input("⭐ Novas Avaliações Recebidas no Mês", min_value=0, step=1)
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

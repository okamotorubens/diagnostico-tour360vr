import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Central de Sistemas | Tour360vr & Okamoto",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONALIZADO (Layout, Tipografia e Cards Unificados) ---
st.markdown("""
    <style>
    /* Remoção de espaço superior no topo da página */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 98% !important;
    }
    
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Estilização do Fundo */
    .stApp {
        background-color: #0B0E14;
        color: #E0E6ED;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #07090E;
        border-right: 1px solid #1E2640;
    }

    /* Títulos da Página Principal */
    .neon-main-title {
        color: #FFFFFF;
        text-shadow: 0 0 12px rgba(0, 229, 255, 0.6);
        font-weight: 800;
        font-size: 1.8rem;
        margin-top: 0rem;
        margin-bottom: 0.15rem;
    }
    
    /* Subtítulo (+1 ponto) */
    .subtitle-header {
        color: #8A99AD;
        font-size: 1.0rem;
        margin-bottom: 1.2rem;
    }

    /* Títulos das Seções (+1 ponto) */
    .neon-section-title {
        color: #00E5FF;
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid rgba(0, 229, 255, 0.25);
        padding-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Container de Card com Botão Integrado */
    .card-container {
        background: #121824;
        border: 1px solid #1E2640;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        min-height: 165px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        transition: all 0.3s ease-in-out;
    }
    
    .card-container:hover {
        border-color: #00E5FF;
        box-shadow: 0 0 14px rgba(0, 229, 255, 0.25);
        transform: translateY(-2px);
    }

    .card-container h3 {
        color: #FFFFFF !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
        margin-bottom: 6px !important;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .card-container p {
        color: #94A3B8;
        font-size: 0.83rem;
        line-height: 1.38;
        margin: 0;
    }

    /* Botão de Ação Centralizado dentro do Card */
    .card-btn-wrapper {
        margin-top: 12px;
        width: 100%;
        display: flex;
        justify-content: center;
    }

    /* Botões/Links Personalizados (Estilo Neon) */
    .stLinkButton > a {
        display: inline-block !important;
        width: 85% !important;
        text-align: center !important;
        border: 1.5px solid #FFFFFF !important;
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        padding: 7px 12px !important;
        text-decoration: none !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 0 6px rgba(255, 255, 255, 0.15) !important;
    }

    .stLinkButton > a:hover {
        border-color: #00E5FF !important;
        color: #00E5FF !important;
        box-shadow: 0 0 16px #00E5FF, 0 0 24px rgba(0, 229, 255, 0.4) !important;
        transform: translateY(-2px) !important;
    }

    /* Botões da Sidebar (Mesmo Tamanho Padronizado) */
    .sidebar-btn-container .stLinkButton > a {
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (Sidebar) ---
with st.sidebar:
    # 1. Logos
    col_l1, col_l2, col_l3 = st.columns([1, 6, 1])
    with col_l2:
        caminho_logo_tour = "logo_tour_transparente.png"
        if os.path.exists(caminho_logo_tour):
            st.image(caminho_logo_tour, width=140)
        else:
            st.markdown("<h3 style='color:#FFF;'>TOUR360VR</h3>", unsafe_allow_html=True)
            
        st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
        
        caminho_logo_okamoto = "logo_okamoto.png"
        if os.path.exists(caminho_logo_okamoto):
            st.image(caminho_logo_okamoto, width=180) # Logo maior conforme solicitado
        elif os.path.exists("okamoto_preto.png"):
            st.image("okamoto_preto.png", width=180)

    st.markdown("<hr style='margin: 12px 0; border-color: #1E2640;'>", unsafe_allow_html=True)
    
    # 2. Navegação Rápida (Texto Maior)
    st.markdown("<p style='color: #FFFFFF; font-weight: 800; font-size: 0.95rem; letter-spacing: 0.5px; margin-bottom: 10px;'>NAVEGAÇÃO RÁPIDA</p>", unsafe_allow_html=True)
    
    # Botões Padronizados do Sidebar
    st.markdown("<div class='sidebar-btn-container'>", unsafe_allow_html=True)
    st.link_button("🌐 Tour360vr", "#tour360vr-prospeccao-diagnostico-gestao")
    st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
    st.link_button("📸 Okamoto Mídias Visuais", "#okamoto-midias-visuais-comercial-precificacao")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 14px 0; border-color: #1E2640;'>", unsafe_allow_html=True)
    
    # 3. Rodapé Dividido em 2 Linhas
    st.markdown("<div style='color: #8A99AD; font-size: 0.78rem; line-height: 1.4;'>Painel Unificado de Operações<br>Okamoto Mídias Visuais</div>", unsafe_allow_html=True)

# --- CABEÇALHO DA CENTRAL ---
st.markdown("<h1 class='neon-main-title'>Central de Sistemas e Operações</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-header'>Selecione o módulo operacional desejado para abrir a aplicação.</div>", unsafe_allow_html=True)

# ==========================================
# SEÇÃO 1: TOUR360VR (GMB & PROSPECÇÃO)
# ==========================================
st.markdown("<div id='tour360vr-prospeccao-diagnostico-gestao' class='neon-section-title'>🌐 Tour360vr — Prospecção, Diagnóstico & Gestão GMB</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class='card-container'>
            <div>
                <h3>📡 Radar de Prospecção</h3>
                <p>Mapeamento de campo e varredura de fichas do Google Meu Negócio (Buscador de Clientes).</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='card-btn-wrapper'>", unsafe_allow_html=True)
    st.link_button("Abrir Radar", "https://radar-comercial-tour360vr.streamlit.app/")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class='card-container'>
            <div>
                <h3>📊 Diagnóstico & Audit PDF</h3>
                <p>Análise de saúde do perfil local com geração de proposta visual e relatório técnico em PDF.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='card-btn-wrapper'>", unsafe_allow_html=True)
    st.link_button("Abrir Diagnóstico", "https://tour360vr.streamlit.app/")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class='card-container'>
            <div>
                <h3>📈 Gestão Mensal & ROI</h3>
                <p>Acompanhamento recorrente de métricas (chamadas, rotas, WhatsApp) e relatórios executivos.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='card-btn-wrapper'>", unsafe_allow_html=True)
    st.link_button("Abrir Gestão Mensal", "https://seu-link-da-gestao.streamlit.app")
    st.markdown("</div>", unsafe_allow_html=True)

# Espaçamento aumentado entre blocos
st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)

# ==========================================
# SEÇÃO 2: OKAMOTO MÍDIAS VISUAIS
# ==========================================
st.markdown("<div id='okamoto-midias-visuais-comercial-precificacao' class='neon-section-title'>📸 Okamoto Mídias Visuais — Comercial & Precificação</div>", unsafe_allow_html=True)

col4, col5, col_vazia = st.columns([1, 1, 1])

with col4:
    st.markdown("""
        <div class='card-container'>
            <div>
                <h3>💼 Propostas & Custos</h3>
                <p>Elaboração de propostas comerciais e orçamentos de logística e produção visual.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='card-btn-wrapper'>", unsafe_allow_html=True)
    st.link_button("Abrir Propostas", "https://okamoto-proposta-comercial.streamlit.app/")
    st.markdown("</div>", unsafe_allow_html=True)

with col5:
    st.markdown("""
        <div class='card-container'>
            <div>
                <h3>🧮 Custos & Logística</h3>
                <p>Cálculo de custos operacionais e logística de transporte para atendimentos e produções.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='card-btn-wrapper'>", unsafe_allow_html=True)
    st.link_button("Abrir Custos", "https://seu-link-de-custos.streamlit.app")
    st.markdown("</div>", unsafe_allow_html=True)

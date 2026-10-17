import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Central de Sistemas | Tour360vr & Okamoto",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    /* 1. Margens Globais */
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

    /* 2. SIDEBAR E CENTRALIZAÇÃO DAS LOGOS */
    [data-testid="stSidebar"] {
        background-color: #07090E;
        border-right: 1px solid #1E2640;
    }

    /* Força centralização de qualquer elemento nativo de imagem na sidebar */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin: 0 auto !important;
    }

    [data-testid="stSidebar"] [data-testid="stImage"] img {
        margin: 0 auto !important;
        display: block !important;
    }

    .sidebar-text-center {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
    }

    /* 3. TÍTULOS DA PÁGINA COM TAMANHO AUMENTADO */
    .neon-main-title {
        color: #FFFFFF;
        text-shadow: 0 0 12px rgba(0, 229, 255, 0.6);
        font-weight: 800;
        font-size: 1.85rem;
        margin-top: 0rem;
        margin-bottom: 0.2rem;
    }
    
    /* Subtítulo Aumentado */
    .subtitle-header {
        color: #94A3B8;
        font-size: 1.18rem !important; /* Aumentado */
        margin-bottom: 1.6rem;
    }

    /* Títulos das Seções Aumentados (+1.5 ponto) */
    .neon-section-title {
        color: #00E5FF;
        font-size: 1.45rem !important; /* Aumentado */
        font-weight: 700;
        margin-top: 0.5rem;
        margin-bottom: 1.2rem;
        border-bottom: 1px solid rgba(0, 229, 255, 0.25);
        padding-bottom: 0.5rem;
    }

    .section-divider-space {
        margin-top: 2.2rem;
    }

    /* 4. CARDS CLICÁVEIS CENTRALIZADOS */
    .clickable-card {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        text-align: center !important;
        background: #121824;
        border: 1.5px solid #FFFFFF;
        border-radius: 10px;
        padding: 20px 18px 22px 18px;
        height: 150px !important;
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.12);
        text-decoration: none !important;
        transition: all 0.3s ease-in-out;
        box-sizing: border-box;
    }
    
    .clickable-card:hover {
        border-color: #00E5FF !important;
        box-shadow: 0 0 18px #00E5FF, 0 0 28px rgba(0, 229, 255, 0.4) !important;
        transform: translateY(-3px);
        background: #161F30;
    }

    .clickable-card h3 {
        color: #FFFFFF !important;
        font-size: 1.08rem !important;
        font-weight: 700 !important;
        margin: 0 0 8px 0 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100%;
        text-align: center !important;
    }

    .clickable-card p {
        color: #94A3B8;
        font-size: 0.84rem;
        line-height: 1.45;
        margin: 0;
        text-align: center !important;
    }

    .clickable-card:hover h3 {
        color: #00E5FF !important;
    }

    /* 5. BOTÕES DA SIDEBAR CENTRALIZADOS E PADRONIZADOS */
    .sidebar-btn-group {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
    }

    .sidebar-nav-btn {
        display: block;
        width: 90% !important;
        text-align: center;
        border: 1.5px solid #FFFFFF;
        background-color: #0E1117;
        color: #FFFFFF !important;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 9px 6px;
        text-decoration: none !important;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 0 5px rgba(255, 255, 255, 0.15);
        white-space: nowrap;
        box-sizing: border-box;
    }

    .sidebar-nav-btn:hover {
        border-color: #00E5FF !important;
        color: #00E5FF !important;
        box-shadow: 0 0 14px #00E5FF;
        background-color: #1A202C;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (Sidebar) ---
with st.sidebar:
    # Logos Centralizadas via st.image + CSS
    caminho_logo_tour = "logo_tour_transparente.png"
    if os.path.exists(caminho_logo_tour):
        st.image(caminho_logo_tour, width=130)
    else:
        st.markdown("<h3 class='sidebar-text-center' style='color:#FFF; margin:0;'>TOUR360VR</h3>", unsafe_allow_html=True)
        
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    
    caminho_logo_okamoto = "logo_okamoto.png"
    if os.path.exists(caminho_logo_okamoto):
        st.image(caminho_logo_okamoto, width=165)
    elif os.path.exists("okamoto_preto.png"):
        st.image("okamoto_preto.png", width=165)

    st.markdown("<hr style='margin: 16px 0; border-color: #1E2640; width: 100%;'>", unsafe_allow_html=True)
    
    # Navegação Rápida Centralizada
    st.markdown("<p class='sidebar-text-center' style='color: #FFFFFF; font-weight: 800; font-size: 0.92rem; letter-spacing: 0.5px; margin-bottom: 12px;'>NAVEGAÇÃO RÁPIDA</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-btn-group'>", unsafe_allow_html=True)
    st.markdown("<a href='#tour360vr-prospeccao-diagnostico-gestao' class='sidebar-nav-btn'>🌐 Tour360vr</a>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    st.markdown("<a href='#okamoto-midias-visuais-comercial-precificacao' class='sidebar-nav-btn'>📸 Okamoto Mídias Visuais</a>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 16px 0; border-color: #1E2640; width: 100%;'>", unsafe_allow_html=True)
    
    # Rodapé
    st.markdown("<div class='sidebar-text-center' style='color: #8A99AD; font-size: 0.75rem; line-height: 1.4;'>Painel Unificado de Operações<br>© Okamoto Mídias Visuais</div>", unsafe_allow_html=True)

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
        <a href='https://radar-comercial-tour360vr.streamlit.app/' target='_blank' class='clickable-card'>
            <h3>📡 Radar de Prospecção</h3>
            <p>Mapeamento de campo e varredura de fichas do Google Meu Negócio (Buscador de Clientes).</p>
        </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <a href='https://tour360vr.streamlit.app/' target='_blank' class='clickable-card'>
            <h3>📊 Diagnóstico & Audit PDF</h3>
            <p>Análise de saúde do perfil local com geração de proposta visual e relatório técnico em PDF.</p>
        </a>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <a href='https://seu-link-da-gestao.streamlit.app' target='_blank' class='clickable-card'>
            <h3>📈 Gestão Mensal & ROI</h3>
            <p>Acompanhamento recorrente de métricas (chamadas, rotas, WhatsApp) e relatórios executivos.</p>
        </a>
    """, unsafe_allow_html=True)

# Espaçamento entre os blocos
st.markdown("<div class='section-divider-space'></div>", unsafe_allow_html=True)

# ==========================================
# SEÇÃO 2: OKAMOTO MÍDIAS VISUAIS
# ==========================================
st.markdown("<div id='okamoto-midias-visuais-comercial-precificacao' class='neon-section-title'>📸 Okamoto Mídias Visuais — Comercial & Precificação</div>", unsafe_allow_html=True)

col4, col5, col_vazia = st.columns([1, 1, 1])

with col4:
    st.markdown("""
        <a href='https://okamoto-proposta-comercial.streamlit.app/' target='_blank' class='clickable-card'>
            <h3>💼 Propostas & Custos</h3>
            <p>Elaboração de propostas comerciais e orçamentos de logística e produção visual.</p>
        </a>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
        <a href='https://seu-link-de-custos.streamlit.app' target='_blank' class='clickable-card'>
            <h3>🧮 Custos & Logística</h3>
            <p>Cálculo de custos operacionais e logística de transporte para atendimentos e produções.</p>
        </a>
    """, unsafe_allow_html=True)

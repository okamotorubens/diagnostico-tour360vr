import streamlit as st
import os
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Central de Sistemas | Tour360vr & Okamoto",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNÇÃO PARA CONVERTER IMAGEM LOCAL PARA BASE64 ---
def carregar_imagem_base64(caminho):
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_tour_b64 = carregar_imagem_base64("logo_tour_transparente.png")
logo_okamoto_b64 = carregar_imagem_base64("logo_okamoto.png") or carregar_imagem_base64("okamoto_preto.png")

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    /* 1. Margens Globais e Limpeza de Cabeçalho */
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

    /* 2. SIDEBAR COM LOGOS */
    [data-testid="stSidebar"] {
        background-color: #07090E;
        border-right: 1px solid #1E2640;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: center !important;
        padding-top: 6.8rem !important;
    }

    /* Container das Logos na Sidebar */
    .sidebar-center-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        text-align: center;
        padding: 0 10px;
        box-sizing: border-box;
    }

    .sidebar-logo-img-1 {
        width: 155px !important;
        height: auto;
        margin-bottom: 16px;
        display: block;
    }

    .sidebar-logo-img-2 {
        width: 195px !important;
        height: auto;
        display: block;
    }

    /* 3. TÍTULOS DA PÁGINA PRINCIPAL */
    .neon-main-title {
        color: #FFFFFF;
        text-shadow: 0 0 12px rgba(0, 229, 255, 0.6);
        font-weight: 800;
        font-size: 1.85rem;
        margin-top: 0rem;
        margin-bottom: 0.2rem;
    }
    
    .subtitle-header {
        color: #94A3B8;
        font-size: 1.18rem !important;
        margin-bottom: 1.6rem;
    }

    .neon-section-title {
        color: #00E5FF;
        font-size: 1.45rem !important;
        font-weight: 700;
        margin-top: 0.5rem;
        margin-bottom: 1.2rem;
        border-bottom: 1px solid rgba(0, 229, 255, 0.25);
        padding-bottom: 0.5rem;
    }

    .section-divider-space {
        margin-top: 2.2rem;
    }

    /* 4. CARDS CLICÁVEIS (Layout em Coluna Perfeitamente Centralizado) */
    .clickable-card {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        text-align: center !important;
        background: #121824;
        border: 1.5px solid #FFFFFF;
        border-radius: 10px;
        padding: 16px 16px 18px 16px;
        height: 155px !important;
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

    /* Emoji / Ícone no Topo do Card */
    .card-icon {
        font-size: 1.5rem !important;
        margin-bottom: 4px;
        line-height: 1;
    }

    /* Nome do Sistema 100% Centralizado */
    .card-title-text {
        color: #FFFFFF !important;
        font-size: 1.18rem !important;
        font-weight: 700 !important;
        margin-bottom: 6px !important;
        text-align: center !important;
        width: 100% !important;
    }

    .clickable-card p {
        color: #94A3B8;
        font-size: 0.83rem;
        line-height: 1.4;
        margin: 0;
        text-align: center !important;
    }

    .clickable-card:hover .card-title-text {
        color: #00E5FF !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (Sidebar) ---
with st.sidebar:
    html_logos = "<div class='sidebar-center-container'>"
    
    if logo_tour_b64:
        html_logos += f"<img src='data:image/png;base64,{logo_tour_b64}' class='sidebar-logo-img-1'>"
    else:
        html_logos += "<h3 style='color:#FFF; margin-bottom:15px;'>TOUR360VR</h3>"
        
    if logo_okamoto_b64:
        html_logos += f"<img src='data:image/png;base64,{logo_okamoto_b64}' class='sidebar-logo-img-2'>"
        
    html_logos += """
        <div style='margin-top: 25px; border-top: 1px solid #1E2640; width: 85%; padding-top: 15px;'>
            <p style='color: #8A99AD; font-size: 0.75rem; line-height: 1.4; margin:0;'>
                Painel Unificado de Operações<br>© Okamoto Mídias Visuais
            </p>
        </div>
    </div>
    """
    
    st.markdown(html_logos, unsafe_allow_html=True)

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
            <div class='card-icon'>📡</div>
            <div class='card-title-text'>Radar de Prospecção</div>
            <p>Mapeamento de campo e varredura de fichas do Google Meu Negócio (Buscador de Clientes).</p>
        </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <a href='https://tour360vr.streamlit.app/' target='_blank' class='clickable-card'>
            <div class='card-icon'>📊</div>
            <div class='card-title-text'>Diagnóstico & Auditoria</div>
            <p>Análise de saúde do perfil local com geração de proposta visual e relatório técnico em PDF.</p>
        </a>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <a href='https://seu-link-da-gestao.streamlit.app' target='_blank' class='clickable-card'>
            <div class='card-icon'>📈</div>
            <div class='card-title-text'>Gestão Mensal & ROI</div>
            <p>Acompanhamento recorrente de métricas (chamadas, rotas, WhatsApp) e relatórios executivos.</p>
        </a>
    """, unsafe_allow_html=True)

# Espaçamento entre os dois blocos
st.markdown("<div class='section-divider-space'></div>", unsafe_allow_html=True)

# ==========================================
# SEÇÃO 2: OKAMOTO MÍDIAS VISUAIS
# ==========================================
st.markdown("<div id='okamoto-midias-visuais-comercial-precificacao' class='neon-section-title'>📸 Okamoto Mídias Visuais — Comercial & Precificação</div>", unsafe_allow_html=True)

col4, col5, col_vazia = st.columns([1, 1, 1])

with col4:
    st.markdown("""
        <a href='https://okamoto-proposta-comercial.streamlit.app/' target='_blank' class='clickable-card'>
            <div class='card-icon'>💼</div>
            <div class='card-title-text'>Propostas & Custos</div>
            <p>Elaboração de propostas comerciais e orçamentos de logística e produção visual.</p>
        </a>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
        <a href='https://seu-link-de-custos.streamlit.app' target='_blank' class='clickable-card'>
            <div class='card-icon'>🧮</div>
            <div class='card-title-text'>Custos & Logística</div>
            <p>Cálculo de custos operacionais e logística de transporte para atendimentos e produções.</p>
        </a>
    """, unsafe_allow_html=True)

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

    /* 2. SIDEBAR COM ALINHAMENTO SUPERIOR NA LINHA DO TÍTULO */
    [data-testid="stSidebar"] {
        background-color: #07090E;
        border-right: 1px solid #1E2640;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important; /* Alinha ao topo */
        align-items: center !important;
        padding-top: 5.8rem !important; /* Desce o topo das logos exatamente para a linha do título */
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

    /* Logos com Tamanho Aumentado */
    .sidebar-logo-img-1 {
        width: 155px !important; /* Aumentado de 135px */
        height: auto;
        margin-bottom: 16px;
        display: block;
    }

    .sidebar-logo-img-2 {
        width: 195px !important; /* Aumentado de 170px */
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

    /* 4. CARDS CLICÁVEIS COM BORDA BRANCA E HOVER NEON AZUL */
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
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (Sidebar Posicionada na Linha do Título) ---
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

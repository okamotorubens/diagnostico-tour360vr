import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Central de Sistemas | Tour360vr & Okamoto",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONALIZADO (Padrão Dark + Efeito Neon Pro) ---
st.markdown("""
    <style>
    /* Estilização global do fundo */
    .stApp {
        background-color: #0B0E14;
        color: #E0E6ED;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Barra Lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #07090E;
        border-right: 1px solid #1E2640;
    }

    /* Títulos e Tipografia Neon */
    .neon-main-title {
        color: #FFFFFF;
        text-shadow: 0 0 12px rgba(0, 229, 255, 0.6);
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.2rem;
    }
    
    .subtitle-header {
        color: #8A99AD;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    .neon-section-title {
        color: #00E5FF;
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1.2rem;
        border-bottom: 1px solid rgba(0, 229, 255, 0.25);
        padding-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Estilização dos Cards dos Sistemas */
    .system-card {
        background: #121824;
        border: 1px solid #1E2640;
        border-radius: 10px;
        padding: 22px 20px 15px 20px;
        margin-bottom: 12px;
        min-height: 140px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: all 0.3s ease-in-out;
    }
    
    .system-card:hover {
        border-color: #00E5FF;
        box-shadow: 0 0 18px rgba(0, 229, 255, 0.25);
        transform: translateY(-2px);
    }

    .system-card h3 {
        color: #FFFFFF !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
        margin-bottom: 8px !important;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .system-card p {
        color: #94A3B8;
        font-size: 0.88rem;
        line-height: 1.45;
        margin: 0;
    }

    /* Botões/Links Personalizados com Contorno Branco e Efeito Neon */
    .stLinkButton > a {
        display: block !important;
        width: 100% !important;
        text-align: center !important;
        border: 1.5px solid #FFFFFF !important;
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        padding: 10px 16px !important;
        text-decoration: none !important;
        transition: all 0.3s ease-in-out !important;
        box-shadow: 0 0 6px rgba(255, 255, 255, 0.15) !important;
    }

    .stLinkButton > a:hover {
        border-color: #00E5FF !important;
        color: #00E5FF !important;
        box-shadow: 0 0 16px #00E5FF, 0 0 28px rgba(0, 229, 255, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (Sidebar com o arquivo exato da logo no seu repositório) ---
with st.sidebar:
    caminho_logo = "logo_tour_transparente.png"
    if os.path.exists(caminho_logo):
        st.image(caminho_logo, use_container_width=True)
    else:
        st.markdown("<h2 class='neon-main-title' style='font-size: 1.5rem;'>TOUR360VR</h2>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='color: #00E5FF; font-weight: 600; font-size: 0.85rem; letter-spacing: 0.5px;'>NAVEGAÇÃO RÁPIDA</p>", unsafe_allow_html=True)
    st.markdown("- [Tour360vr](#tour360vr-prospeccao-diagnostico-gestao)")
    st.markdown("- [Okamoto Mídias Visuais](#okamoto-midias-visuais-comercial-precificacao)")
    st.markdown("---")
    st.caption("Painel Unificado de Operações\n© Okamoto Mídias Visuais")

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
        <div class='system-card'>
            <h3>📡 Radar de Prospecção</h3>
            <p>Mapeamento de campo e varredura de fichas do Google Meu Negócio (Buscador de Clientes).</p>
        </div>
    """, unsafe_allow_html=True)
    # Coloque aqui o link do seu app do Buscador de Clientes
    st.link_button("Abrir Radar", "https://radar-comercial-tour360vr.streamlit.app/")

with col2:
    st.markdown("""
        <div class='system-card'>
            <h3>📊 Diagnóstico & Audit PDF</h3>
            <p>Análise de saúde do perfil local com geração de proposta visual e relatório técnico em PDF.</p>
        </div>
    """, unsafe_allow_html=True)
    # Coloque aqui o link do seu app de Diagnóstico
    st.link_button("Abrir Diagnóstico", "https://tour360vr.streamlit.app/")

with col3:
    st.markdown("""
        <div class='system-card'>
            <h3>📈 Gestão Mensal & ROI</h3>
            <p>Acompanhamento recorrente de métricas (chamadas, rotas, WhatsApp) e relatórios executivos.</p>
        </div>
    """, unsafe_allow_html=True)
    # Coloque aqui o link do seu app de Gestão Mensal
    st.link_button("Abrir Gestão Mensal", "https://seu-link-da-gestao.streamlit.app")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# SEÇÃO 2: OKAMOTO MÍDIAS VISUAIS
# ==========================================
st.markdown("<div id='okamoto-midias-visuais-comercial-precificacao' class='neon-section-title'>📸 Okamoto Mídias Visuais — Comercial & Precificação</div>", unsafe_allow_html=True)

col4, col5, col_vazia = st.columns([1, 1, 1])

with col4:
    st.markdown("""
        <div class='system-card'>
            <h3>💼 Propostas & Custos</h3>
            <p>Elaboração de propostas comerciais e orçamentos de logística e produção visual.</p>
        </div>
    """, unsafe_allow_html=True)
    # Coloque aqui o link do seu app de Propostas/Custos
    st.link_button("Abrir Propostas", "https://okamoto-proposta-comercial.streamlit.app/")

with col5:
    st.markdown("""
        <div class='system-card'>
            <h3>🧮 Custos & Logística</h3>
            <p>Cálculo de custos operacionais e logística de transporte para atendimentos e produções.</p>
        </div>
    """, unsafe_allow_html=True)
    # Coloque aqui o link do seu app de Custos Logística
    st.link_button("Abrir Custos", "https://seu-link-de-custos.streamlit.app")

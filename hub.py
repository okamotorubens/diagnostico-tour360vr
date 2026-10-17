import streamlit as st
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Central de Sistemas | Tour360vr & Okamoto",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS PERSONALIZADO (Ajustes de Layout, Centralização e Embutimento) ---
st.markdown("""
    <style>
    /* 1. Remoção de espaçamento superior e barra de rolagem */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        max-width: 98% !important;
    }
    
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Fundo Global */
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

    /* Centralização na Sidebar */
    .sidebar-center {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        width: 100%;
    }

    /* Título Principal */
    .neon-main-title {
        color: #FFFFFF;
        text-shadow: 0 0 12px rgba(0, 229, 255, 0.6);
        font-weight: 800;
        font-size: 1.75rem;
        margin-top: 0rem;
        margin-bottom: 0.1rem;
    }
    
    /* Subtítulo da Página Principal (+1 Ponto) */
    .subtitle-header {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 0.8rem;
    }

    /* Títulos das Seções */
    .neon-section-title {
        color: #00E5FF;
        font-size: 1.15rem;
        font-weight: 700;
        margin-top: 0.6rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid rgba(0, 229, 255, 0.25);
        padding-bottom: 0.25rem;
    }

    /* 2. CARD UNIFICADO (Descrição + Botão Embutido) */
    .system-card-full {
        background: #121824;
        border: 1px solid #1E2640;
        border-radius: 10px;
        padding: 14px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 145px !important; /* Altura exata e fixa */
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        transition: all 0.3s ease-in-out;
        box-sizing: border-box;
    }
    
    .system-card-full:hover {
        border-color: #00E5FF;
        box-shadow: 0 0 14px rgba(0, 229, 255, 0.25);
        transform: translateY(-2px);
    }

    .system-card-full h3 {
        color: #FFFFFF !important;
        font-size: 1.0rem !important;
        font-weight: 700 !important;
        margin: 0 0 4px 0 !important;
    }

    .system-card-full p {
        color: #94A3B8;
        font-size: 0.80rem;
        line-height: 1.3;
        margin: 0;
    }

    /* Botão de Ação EMBUTIDO DENTRO DO CARD */
    .card-action-btn {
        display: block;
        width: 80%;
        margin: 8px auto 0 auto;
        text-align: center;
        border: 1.5px solid #FFFFFF;
        background-color: #0E1117;
        color: #FFFFFF !important;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
        padding: 6px 10px;
        text-decoration: none !important;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 0 6px rgba(255, 255, 255, 0.15);
        white-space: nowrap;
    }

    .card-action-btn:hover {
        border-color: #00E5FF;
        color: #00E5FF !important;
        box-shadow: 0 0 14px #00E5FF;
        background-color: #07090E;
    }

    /* 3. BOTÕES DA SIDEBAR (Identicos, Mesma Largura, Linha Única) */
    .sidebar-nav-btn {
        display: block;
        width: 100%;
        text-align: center;
        border: 1.5px solid #FFFFFF;
        background-color: #0E1117;
        color: #FFFFFF !important;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.82rem;
        padding: 8px 6px;
        text-decoration: none !important;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 0 5px rgba(255, 255, 255, 0.15);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        box-sizing: border-box;
    }

    .sidebar-nav-btn:hover {
        border-color: #FFFFFF;
        color: #FFFFFF !important;
        box-shadow: 0 0 14px #FFFFFF;
        background-color: #1A202C;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (Sidebar) ---
with st.sidebar:
    # Logos Centralizadas
    st.markdown("<div class='sidebar-center'>", unsafe_allow_html=True)
    
    caminho_logo_tour = "logo_tour_transparente.png"
    if os.path.exists(caminho_logo_tour):
        st.image(caminho_logo_tour, width=130)
    else:
        st.markdown("<h3 style='color:#FFF; margin:0;'>TOUR360VR</h3>", unsafe_allow_html=True)
        
    st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
    
    caminho_logo_okamoto = "logo_okamoto.png"
    if os.path.exists(caminho_logo_okamoto):
        st.image(caminho_logo_okamoto, width=170)
    elif os.path.exists("okamoto_preto.png"):
        st.image("okamoto_preto.png", width=170)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin: 10px 0; border-color: #1E2640;'>", unsafe_allow_html=True)
    
    # Navegação Rápida Centralizada
    st.markdown("<div class='sidebar-center'>", unsafe_allow_html=True)
    st.markdown("<p style='color: #FFFFFF; font-weight: 800; font-size: 0.9rem; letter-spacing: 0.5px; margin-bottom: 8px;'>NAVEGAÇÃO RÁPIDA</p>", unsafe_allow_html=True)
    
    # Botões em Linha Única
    st.markdown("<a href='#tour360vr-prospeccao-diagnostico-gestao' class='sidebar-nav-btn'>🌐 Tour360vr</a>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
    st.markdown("<a href='#okamoto-midias-visuais-comercial-precificacao' class='sidebar-nav-btn'>📸 Okamoto Mídias Visuais</a>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 12px 0; border-color: #1E2640;'>", unsafe_allow_html=True)
    
    # Rodapé Dividido em 2 Linhas
    st.markdown("<div class='sidebar-center' style='color: #8A99AD; font-size: 0.75rem; line-height: 1.35;'>Painel Unificado de Operações<br>© Okamoto Mídias Visuais</div>", unsafe_allow_html=True)

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
        <div class='system-card-full'>
            <div>
                <h3>📡 Radar de Prospecção</h3>
                <p>Mapeamento de campo e varredura de fichas do Google Meu Negócio (Buscador de Clientes).</p>
            </div>
            <a href='https://radar-comercial-tour360vr.streamlit.app/' target='_blank' class='card-action-btn'>Abrir Radar</a>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class='system-card-full'>
            <div>
                <h3>📊 Diagnóstico & Audit PDF</h3>
                <p>Análise de saúde do perfil local com geração de proposta visual e relatório técnico em PDF.</p>
            </div>
            <a href='https://tour360vr.streamlit.app/' target='_blank' class='card-action-btn'>Abrir Diagnóstico</a>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class='system-card-full'>
            <div>
                <h3>📈 Gestão Mensal & ROI</h3>
                <p>Acompanhamento recorrente de métricas (chamadas, rotas, WhatsApp) e relatórios executivos.</p>
            </div>
            <a href='https://seu-link-da-gestao.streamlit.app' target='_blank' class='card-action-btn'>Abrir Gestão Mensal</a>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# SEÇÃO 2: OKAMOTO MÍDIAS VISUAIS
# ==========================================
st.markdown("<div id='okamoto-midias-visuais-comercial-precificacao' class='neon-section-title'>📸 Okamoto Mídias Visuais — Comercial & Precificação</div>", unsafe_allow_html=True)

col4, col5, col_vazia = st.columns([1, 1, 1])

with col4:
    st.markdown("""
        <div class='system-card-full'>
            <div>
                <h3>💼 Propostas & Custos</h3>
                <p>Elaboração de propostas comerciais e orçamentos de logística e produção visual.</p>
            </div>
            <a href='https://okamoto-proposta-comercial.streamlit.app/' target='_blank' class='card-action-btn'>Abrir Propostas</a>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
        <div class='system-card-full'>
            <div>
                <h3>🧮 Custos & Logística</h3>
                <p>Cálculo de custos operacionais e logística de transporte para atendimentos e produções.</p>
            </div>
            <a href='https://seu-link-de-custos.streamlit.app' target='_blank' class='card-action-btn'>Abrir Custos</a>
        </div>
    """, unsafe_allow_html=True)

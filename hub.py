import streamlit as st
import os
import base64

st.set_page_config(
    page_title="Central de Sistemas | Tour360VR & Okamoto",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ASSETS ---
def carregar_imagem_base64(caminho):
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_tour_b64 = carregar_imagem_base64("logo_tour_transparente.png")
logo_okamoto_b64 = carregar_imagem_base64("logo_okamoto.png") or carregar_imagem_base64("okamoto_preto.png")

# --- TEMA GLASSMORPHISM DARK ---
st.markdown("""
<style>
:root {
    --bg: #0B0E14;
    --bg-glow: #16213A;
    --glass: rgba(22, 31, 48, 0.55);
    --glass-hover: rgba(37, 45, 66, 0.70);
    --border: rgba(255, 255, 255, 0.10);
    --border-hover: rgba(255, 255, 255, 0.30);
    --text: #E6EDF7;
    --text-strong: #FFFFFF;
    --text-muted: #8E9BAE;
    --accent: #4AA3DA;
    --accent-2: #FFA733;
    --success: #9DBE5A;
    --coral: #F76C4A;
    --gradient-brand: linear-gradient(90deg, #FFA733, #4AA3DA, #9DBE5A, #F76C4A);
    --blur: 18px;
}

html, body, .stApp {
    background:
        radial-gradient(circle at 15% 0%, var(--bg-glow) 0%, transparent 45%),
        radial-gradient(circle at 90% 100%, rgba(247,108,74,0.08) 0%, transparent 40%),
        var(--bg) !important;
    color: var(--text);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
header[data-testid="stHeader"] { display: none !important; }
.block-container { padding-top: 1.6rem !important; padding-bottom: 2rem !important; max-width: 1200px !important; }
h1, h2, h3, h4 { color: var(--text-strong) !important; letter-spacing: -0.01em; }

/* Sidebar em vidro */
[data-testid="stSidebar"] {
    background: rgba(7, 9, 14, 0.75) !important;
    backdrop-filter: blur(var(--blur));
    border-right: 1px solid var(--border);
}
.sidebar-box {
    display: flex; flex-direction: column; align-items: center; text-align: center;
    padding: 2.5rem 0.5rem 0 0.5rem; gap: 14px;
}
.sidebar-box img.logo-tour { width: 105px; height: auto; }
.sidebar-box img.logo-okamoto { width: 180px; height: auto; margin-top: 14px; }
.sidebar-footer {
    margin-top: 18px; padding-top: 14px; width: 85%;
    border-top: 1px solid var(--border);
    color: var(--text-muted); font-size: .75rem; line-height: 1.4;
}

/* Hero centralizado */
.hero {
    position: relative; overflow: hidden;
    display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
    background: var(--glass);
    backdrop-filter: blur(var(--blur)); -webkit-backdrop-filter: blur(var(--blur));
    border: 1px solid var(--border); border-radius: 18px;
    padding: 26px 30px; margin-bottom: 26px;
    box-shadow: 0 8px 32px rgba(0,0,0,.35);
}
.hero::before {
    content: ""; position: absolute; left: 0; top: 0; right: 0; height: 3px;
    background: var(--gradient-brand);
}
.hero h1 { margin: 0 !important; font-size: 1.7rem !important; font-weight: 800; text-align: center; }
.hero p { margin: 6px 0 0 0; color: var(--text-muted); font-size: 1rem; text-align: center; }

/* Títulos de seção */
.section-title {
    display: flex; align-items: center; gap: 10px;
    margin: 30px 0 14px 0; padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
    color: var(--text-strong); font-size: 1.15rem; font-weight: 700;
}
.section-title .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 10px var(--accent); }

/* Cards clicáveis em vidro (mesmo tamanho, texto branco) */
a.sys-card, a.sys-card:visited, a.sys-card:hover, a.sys-card:focus {
    color: #FFFFFF !important;
}
a.sys-card {
    display: flex; flex-direction: column; align-items: flex-start; gap: 6px;
    height: 185px; box-sizing: border-box; padding: 18px 20px;
    background: var(--glass);
    backdrop-filter: blur(var(--blur)); -webkit-backdrop-filter: blur(var(--blur));
    border: 1px solid var(--border); border-radius: 14px;
    text-decoration: none !important;
    box-shadow: 0 4px 16px rgba(0,0,0,.25);
    transition: all .2s ease;
}
a.sys-card:hover {
    background: var(--glass-hover);
    border-color: var(--border-hover);
    transform: translateY(-3px);
    box-shadow: 0 0 18px rgba(74,163,218,.35);
}
a.sys-card .icon { font-size: 1.7rem; line-height: 1; }
a.sys-card .name { color: #FFFFFF !important; font-size: 1.05rem; font-weight: 700; }
a.sys-card .desc { color: var(--text-muted); font-size: .85rem; line-height: 1.45; }
a.sys-card:hover .name { color: var(--accent) !important; }
a.sys-card .go { margin-top: auto; color: #FFFFFF !important; font-size: .78rem; font-weight: 600; }

/* Espaço entre blocos de cards */
.gap-lg { height: 22px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    html_logos = "<div class='sidebar-box'>"
    if logo_tour_b64:
        html_logos += f"<img class='logo-tour' src='data:image/png;base64,{logo_tour_b64}'/>"
    else:
        html_logos += "<h3 style='color:#FFF; margin:0;'>TOUR360VR</h3>"
    if logo_okamoto_b64:
        html_logos += f"<img class='logo-okamoto' src='data:image/png;base64,{logo_okamoto_b64}'/>"
    html_logos += (
        "<div class='sidebar-footer'>Painel Unificado de Operações<br>© Okamoto Mídias Visuais</div>"
        "</div>"
    )
    st.markdown(html_logos, unsafe_allow_html=True)

# --- HERO (centralizado) ---
st.markdown("""
<div class="hero">
    <h1>Central de Sistemas e Operações</h1>
    <p>Selecione o módulo operacional desejado para abrir a aplicação.</p>
</div>
""", unsafe_allow_html=True)


# --- COMPONENTE DE CARD ---
def render_cards(cards):
    cols = st.columns(len(cards))
    for col, c in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <a class="sys-card" href="{c['url']}" target="_blank">
                    <div class="icon">{c['icon']}</div>
                    <div class="name">{c['name']}</div>
                    <div class="desc">{c['desc']}</div>
                    <div class="go">Abrir sistema →</div>
                </a>
                """,
                unsafe_allow_html=True,
            )


# ==========================================
# SEÇÃO 1: TOUR360VR
# ==========================================
st.markdown(
    "<div class='section-title'><span class='dot'></span>🌐 Tour360vr — Prospecção, Diagnóstico & Gestão GMB</div>",
    unsafe_allow_html=True,
)
render_cards([
    {"icon": "📡", "name": "Radar de Prospecção",
     "desc": "Mapeamento de campo e varredura de fichas do Google Meu Negócio (Buscador de Clientes).",
     "url": "https://radar-comercial-tour360vr.streamlit.app/"},
    {"icon": "📊", "name": "Diagnóstico & Auditoria",
     "desc": "Análise de saúde do perfil local com geração de proposta visual e relatório técnico em PDF.",
     "url": "https://tour360vr.streamlit.app/"},
    {"icon": "📈", "name": "Gestão Mensal & ROI",
     "desc": "Acompanhamento recorrente de métricas (chamadas, rotas, WhatsApp) e relatórios executivos.",
     "url": "https://gestao-mensal-tour360vr.streamlit.app/"},
])

# Espaço de 1 linha entre os blocos
st.markdown("<div class='gap-lg'></div>", unsafe_allow_html=True)

# ==========================================
# SEÇÃO 2: OKAMOTO MÍDIAS VISUAIS
# ==========================================
st.markdown(
    "<div class='section-title'><span class='dot' style='background:var(--accent-2); box-shadow:0 0 10px var(--accent-2);'></span>"
    "📸 Okamoto Mídias Visuais — Comercial & Precificação</div>",
    unsafe_allow_html=True,
)
render_cards([
    {"icon": "💼", "name": "Propostas & Custos",
     "desc": "Elaboração de propostas comerciais e orçamentos de logística e produção visual.",
     "url": "https://okamoto-proposta-comercial.streamlit.app/"},
    {"icon": "🧮", "name": "Custos & Logística",
     "desc": "Cálculo de custos operacionais e logística de transporte para atendimentos e produções.",
     "url": "https://seu-link-de-custos.streamlit.app"},
])


"""Injeção do tema global (glassmorphism dark) no Streamlit."""
import streamlit as st
from design.tokens import COLORS, RADIUS, BLUR, SHADOW, GRADIENT_BRAND, FONT_FAMILY


def _css_variables() -> str:
    lines = [f"  --{k.replace('_', '-')}: {v};" for k, v in COLORS.items()]
    lines += [f"  --radius-{k}: {v};" for k, v in RADIUS.items()]
    lines += [f"  --shadow-{k}: {v};" for k, v in SHADOW.items()]
    lines += [f"  --blur: {BLUR};", f"  --gradient-brand: {GRADIENT_BRAND};",
              f"  --font: {FONT_FAMILY};"]
    return ":root {\n" + "\n".join(lines) + "\n}\n"


# CSS sem f-string para não precisar escapar chaves
_BASE_CSS = """
/* ---------- Base ---------- */
html, body, .stApp {
    background:
        radial-gradient(circle at 15% 0%, var(--bg-glow) 0%, transparent 45%),
        radial-gradient(circle at 90% 100%, rgba(247,108,74,0.08) 0%, transparent 40%),
        var(--bg);
    color: var(--text);
    font-family: var(--font);
}
header[data-testid="stHeader"] { display: none !important; }
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px !important;
}
h1, h2, h3, h4 { color: var(--text-strong) !important; letter-spacing: -0.01em; }
hr { border-color: var(--border) !important; margin: var(--spacing-lg, 24px) 0 !important; }
p, label, span, div { font-family: var(--font); }

/* ---------- Glass: containers nativos (st.container(border=True)) ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--glass) !important;
    backdrop-filter: blur(var(--blur)) !important;
    -webkit-backdrop-filter: blur(var(--blur)) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-md) !important;
    padding: 4px 6px;
}

/* Formulários */
div[data-testid="stForm"] {
    background: var(--glass) !important;
    backdrop-filter: blur(var(--blur));
    -webkit-backdrop-filter: blur(var(--blur));
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 20px !important;
    box-shadow: var(--shadow-md);
}

/* ---------- Hero (cabeçalho) ---------- */
.gl-hero {
    position: relative;
    display: flex; align-items: center; gap: 22px;
    background: var(--glass);
    backdrop-filter: blur(var(--blur));
    -webkit-backdrop-filter: blur(var(--blur));
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 22px 28px;
    box-shadow: var(--shadow-md);
    overflow: hidden;
    margin-bottom: 14px;
}
.gl-hero::before {               /* faixa de gradiente da marca */
    content: ""; position: absolute; left: 0; top: 0; right: 0; height: 3px;
    background: var(--gradient-brand);
}
.gl-hero img { width: 76px; height: auto; }
.gl-hero h1 { margin: 0 !important; font-size: 1.6rem !important; font-weight: 800; }
.gl-hero p  { margin: 4px 0 0 0; color: var(--text-muted); font-size: 0.92rem; }

/* ---------- KPI cards ---------- */
.gl-kpi {
    background: var(--glass);
    backdrop-filter: blur(var(--blur));
    -webkit-backdrop-filter: blur(var(--blur));
    border: 1px solid var(--border);
    border-left: 3px solid var(--kpi-accent, var(--accent));
    border-radius: var(--radius-md);
    padding: 16px 18px;
    transition: border-color .2s ease, transform .2s ease;
}
.gl-kpi:hover { border-color: var(--border-hover); transform: translateY(-2px); }
.gl-kpi .label { color: var(--text-muted); font-size: .78rem; text-transform: uppercase; letter-spacing: .06em; }
.gl-kpi .value { color: var(--text-strong); font-size: 1.6rem; font-weight: 800; margin-top: 4px; }
.gl-kpi .delta { font-size: .8rem; margin-top: 2px; }

/* ---------- Botões ---------- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
    background: var(--glass) !important;
    backdrop-filter: blur(12px);
    border: 1px solid var(--border) !important;
    color: var(--text-strong) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    min-height: 42px;
    transition: all .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
    background: var(--glass-hover) !important;
    border-color: var(--border-hover) !important;
    box-shadow: var(--shadow-glow);
    transform: translateY(-1px);
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(74,163,218,.45), rgba(74,163,218,.18)) !important;
    border-color: var(--accent) !important;
    box-shadow: var(--shadow-glow);
}

/* Navegação em abas (linha de botões do topo) */
div[data-testid="stHorizontalBlock"] { gap: .4rem !important; }
div[data-testid="stHorizontalBlock"] button { font-size: .72rem !important; }

/* ---------- Inputs ---------- */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="base-input"] {
    background: rgba(11, 14, 20, 0.55) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    transition: border-color .2s ease, box-shadow .2s ease;
}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(74,163,218,.18) !important;
}
input, textarea { color: var(--text-strong) !important; }

/* ---------- Abas (tabs) ---------- */
button[data-baseweb="tab"] {
    color: var(--text-muted) !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] { color: var(--accent) !important; }
div[data-baseweb="tab-highlight"] { background: var(--gradient-brand) !important; height: 2px !important; }
div[data-baseweb="tab-border"] { background: var(--border) !important; }

/* ---------- Métricas, alertas e tabelas ---------- */
div[data-testid="stMetric"] {
    background: var(--glass);
    backdrop-filter: blur(var(--blur));
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px 18px;
}
div[data-testid="stMetricValue"] { color: var(--text-strong) !important; }
div[data-testid="stAlert"] {
    background: var(--glass) !important;
    backdrop-filter: blur(var(--blur));
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    overflow: hidden;
}

/* ---------- Scrollbar ---------- */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.12); border-radius: 8px; }
::-webkit-scrollbar-track { background: transparent; }
"""


def inject_theme() -> None:
    """Chame uma única vez, logo após st.set_page_config()."""
    st.markdown(f"<style>{_css_variables()}{_BASE_CSS}</style>", unsafe_allow_html=True)

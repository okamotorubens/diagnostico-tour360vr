"""Componentes visuais reutilizáveis (Gestão e Radar)."""
import streamlit as st
from design.tokens import COLORS

PALETA = {"alta": "#F76C4A", "media": "#FFA733", "baixa": "#9DBE5A", "azul": "#4AA3DA"}

CSS_EXTRA = """
<style>
section[data-testid="stSidebar"] {
    background: rgba(7, 9, 14, 0.80) !important;
    backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
    border-right: 1px solid var(--border);
    width: 300px !important; min-width: 300px !important; max-width: 300px !important;
}
[data-testid="stSidebarNav"], [data-testid="stSidebarResizer"] { display: none !important; }

a.gl-wpp, a.gl-wpp:visited, a.gl-wpp:hover, a.gl-wpp:focus, a.gl-wpp * {
    color: #FFFFFF !important; text-decoration: none !important;
}
a.gl-wpp {
    display: block; box-sizing: border-box; text-align: center;
    background: #25D366 !important; padding: 11px; border-radius: 12px;
    font-weight: 700; margin-top: 8px;
}
a.gl-btn-sec {
    display: block; box-sizing: border-box; text-align: center; padding: 9px;
    border-radius: 12px; border: 1px solid var(--border); background: var(--glass);
    color: var(--text-strong) !important; text-decoration: none !important;
    font-weight: 600; margin-top: 8px;
}
a.gl-btn-sec:hover { border-color: var(--border-hover); background: var(--glass-hover); }

.gl-badge { text-align: center; padding: 8px 12px; border-radius: 12px; font-weight: 700; border: 1px solid; display: inline-block; min-width: 170px; }
.gl-badge .r { font-size: .66rem; letter-spacing: .06em; }
.gl-badge .n { font-size: 1.3rem; }
.gl-badge.alta  { color: #F76C4A; border-color: rgba(247,108,74,.5);  background: rgba(247,108,74,.12); }
.gl-badge.media { color: #FFA733; border-color: rgba(255,167,51,.5);  background: rgba(255,167,51,.12); }
.gl-badge.baixa { color: #9DBE5A; border-color: rgba(157,190,90,.5);  background: rgba(157,190,90,.12); }

.gl-muted { color: var(--text-muted); font-size: .86rem; }
.gl-critico { color: #FCA5A5; font-size: .86rem; margin-bottom: 6px; }
.gl-side-title { text-align: center; font-size: .78rem; color: var(--text-muted); letter-spacing: .12em; text-transform: uppercase; margin: 6px 0 10px 0; }
.gl-side-logo { display: flex; justify-content: center; margin-bottom: 8px; }
.gl-side-logo img { width: 130px; height: auto; }
.gl-side-footer { margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border); text-align: center; color: var(--text-muted); font-size: .72rem; }
.gl-side-footer img { width: 120px; height: auto; margin-top: 8px; }
.gl-user { text-align: right; font-size: .85rem; color: var(--text-muted); margin-bottom: 4px; }
.gl-user b { color: var(--text-strong); }
</style>
"""


def aplicar_extras():
    """Chame logo depois de inject_theme()."""
    st.markdown(CSS_EXTRA, unsafe_allow_html=True)


def render_hero(logo_b64: str, title: str, subtitle: str) -> None:
    img = f'<img src="data:image/png;base64,{logo_b64}" alt="Tour360VR"/>' if logo_b64 else ""
    st.markdown(
        f'<div class="gl-hero">{img}<div><h1>{title}</h1><p>{subtitle}</p></div></div>',
        unsafe_allow_html=True,
    )


def section_title(text: str, caption: str | None = None) -> None:
    st.markdown(f"#### {text}")
    if caption:
        st.caption(caption)


def kpi_card(label: str, value: str, delta: str | None = None, accent: str | None = None) -> None:
    accent = accent or COLORS["accent"]
    delta_html = ""
    if delta:
        color = COLORS["success"] if delta.startswith("+") else COLORS["danger"]
        delta_html = f'<div class="delta" style="color:{color}">{delta}</div>'
    st.markdown(
        f'<div class="gl-kpi" style="--kpi-accent:{accent}">'
        f'<div class="label">{label}</div><div class="value">{value}</div>{delta_html}</div>',
        unsafe_allow_html=True,
    )


def glass_container():
    return st.container(border=True)


def classificar_score(score: int):
    """Retorna (classe CSS, rótulo, cor) conforme a faixa de oportunidade."""
    if score >= 60:
        return "alta", "ALTA OPORTUNIDADE", PALETA["alta"]
    if score >= 30:
        return "media", "MÉDIA OPORTUNIDADE", PALETA["media"]
    return "baixa", "BAIXA OPORTUNIDADE", PALETA["baixa"]


def badge_score(score: int) -> str:
    classe, rotulo, _ = classificar_score(score)
    return f'<div class="gl-badge {classe}"><div class="r">{rotulo}</div><div class="n">{score}/100</div></div>'


def botao_whatsapp(url: str, texto: str) -> None:
    st.markdown(f'<a class="gl-wpp" href="{url}" target="_blank">{texto}</a>', unsafe_allow_html=True)


def link_secundario(url: str, texto: str) -> None:
    st.markdown(f'<a class="gl-btn-sec" href="{url}" target="_blank">{texto}</a>', unsafe_allow_html=True)

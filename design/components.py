"""Componentes visuais reutilizáveis."""
import streamlit as st
from design.tokens import COLORS


def render_hero(logo_b64: str, title: str, subtitle: str) -> None:
    img = (f'<img src="data:image/png;base64,{logo_b64}" alt="Tour360VR"/>'
           if logo_b64 else "")
    st.markdown(
        f'<div class="gl-hero">{img}<div><h1>{title}</h1><p>{subtitle}</p></div></div>',
        unsafe_allow_html=True,
    )


def section_title(text: str, caption: str | None = None) -> None:
    st.markdown(f"#### {text}")
    if caption:
        st.caption(caption)


def kpi_card(label: str, value: str, delta: str | None = None,
             accent: str | None = None) -> None:
    """Cartão KPI em vidro. `accent` aceita qualquer cor hex/CSS."""
    accent = accent or COLORS["accent"]
    delta_html = ""
    if delta:
        color = COLORS["success"] if delta.startswith("+") else COLORS["danger"]
        delta_html = f'<div class="delta" style="color:{color}">{delta}</div>'
    st.markdown(
        f'<div class="gl-kpi" style="--kpi-accent:{accent}">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>{delta_html}</div>',
        unsafe_allow_html=True,
    )


def glass_container():
    """Use com `with glass_container():` — o CSS do tema aplica o vidro."""
    return st.container(border=True)


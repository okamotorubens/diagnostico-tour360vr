import streamlit as st

# Configuração da página principal (Ferramenta de Busca)
st.set_page_config(
    page_title="Consultoria Tour360VR",
    page_icon="🔎",
    layout="wide"
)

# Atualização dos textos institucionais na barra lateral
st.sidebar.markdown("""
<div style="padding: 10px 0px;">
    <h3 style="margin: 0; color: #f8fafc; font-size: 18px;">OKAMOTO MÍDIAS VISUAIS</h3>
    <p style="margin: 2px 0 0 0; color: #94a3b8; font-size: 12px;">criado por Rubens Okamoto</p>
</div>
<hr style="margin: 10px 0; border-color: #334155;"/>
""", unsafe_allow_html=True)

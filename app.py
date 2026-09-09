import streamlit as st

# 1. Configuração da página
st.set_page_config(
    page_title="Consultoria & Diagnóstico Tour360VR",
    page_icon="🔎",
    layout="wide"
)

# 2. Barra lateral
st.sidebar.markdown("""
<div style="padding: 10px 0px;">
    <h3 style="margin: 0; color: #f8fafc; font-size: 18px;">OKAMOTO MÍDIAS VISUAIS</h3>
    <p style="margin: 2px 0 0 0; color: #94a3b8; font-size: 12px;">criado por Rubens Okamoto</p>
</div>
<hr style="margin: 10px 0; border-color: #334155;"/>
""", unsafe_allow_html=True)

# 3. Conteúdo principal do Diagnóstico Tour360VR
st.title("🔎 PLATAFORMA DE CONSULTORIA TOUR360VR")
st.subheader("Gestão & Diagnóstico Google Meu Negócio")

col1, col2 = st.columns(2)
with col1:
    empresa = st.text_input("Nome da Empresa / Cliente:", placeholder="Ex: Taiwan Hotel Ltda")
with col2:
    cidade = st.text_input("Localização / Cidade:", placeholder="Ex: Ribeirão Preto, SP")

if st.button("🚀 Buscar no Google Maps / Analisar Perfil", use_container_width=True):
    st.info(f"Analisando perfil para: {empresa} - {cidade}")

st.markdown("---")
st.subheader("⚙️ Auditoria Fina do Perfil")

c1, c2, c3, c4 = st.columns(4)
tour_ok = c1.checkbox("Tour Virtual 360°")
fotos_ok = c2.checkbox("Fotos Profissionais HD")
cat_ok = c3.checkbox("Categorias OK")
horarios_ok = c4.checkbox("Horários OK")

itens = [tour_ok, fotos_ok, cat_ok, horarios_ok]
score = int((sum(itens) / len(itens)) * 100)

st.metric("Score Geral do Perfil", f"{score}/100")

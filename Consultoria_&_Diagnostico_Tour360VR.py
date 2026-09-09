import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA PRINCIPAL
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Consultoria & Diagnóstico Tour360VR",
    page_icon="🔎",
    layout="wide"
)

# Estilização CSS Escura / SaaS
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f17;
    }
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .header-title {
        color: #f8fafc;
        font-size: 24px;
        font-weight: 700;
        margin: 0;
    }
    .card-diag {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Assinatura na Barra Lateral
st.sidebar.markdown("""
<div style="padding: 10px 0px;">
    <h3 style="margin: 0; color: #f8fafc; font-size: 18px;">OKAMOTO MÍDIAS VISUAIS</h3>
    <p style="margin: 2px 0 0 0; color: #94a3b8; font-size: 12px;">criado por Rubens Okamoto</p>
</div>
<hr style="margin: 10px 0; border-color: #334155;"/>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# INTERFACE PRINCIPAL DO DIAGNÓSTICO TOUR360VR
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-box">
    <div class="header-title">🔎 PLATAFORMA DE CONSULTORIA TOUR360VR - GESTÃO & DIAGNÓSTICO GOOGLE MEU NEGÓCIO</div>
</div>
""", unsafe_allow_html=True)

col_input1, col_input2 = st.columns(2)

with col_input1:
    st.markdown("### CAPA DE DIAGNÓSTICO: [NOVO CLIENTE]")
    empresa_nome = st.text_input("Nome da Empresa:", placeholder="Ex: Taiwan Hotel Ltda")

with col_input2:
    st.markdown("### VISÃO GERAL DO DIAGNÓSTICO")
    localizacao = st.text_input("Localização:", placeholder="Ex: Ribeirão Preto, SP")

btn_buscar = st.button("🚀 Buscar no Google Maps / Analisar Perfil", use_container_width=True)

st.markdown("---")

col_auditoria, col_score = st.columns([1.2, 1])

with col_auditoria:
    st.markdown("### ⚙️ AJUSTE FINO DOS ITENS DA AUDITORIA")
    
    c1, c2, c3, c4 = st.columns(4)
    tour_ok = c1.checkbox("Tour 360°", value=False)
    fotos_ok = c2.checkbox("Fotos HD", value=False)
    cat_ok = c3.checkbox("Categorias OK", value=False)
    horarios_ok = c4.checkbox("Horários OK", value=False)
    
    c5, c6, c7 = st.columns(3)
    desc_ok = c5.checkbox("Descrição/Resumo", value=False)
    atrib_ok = c6.checkbox("Atributos Serviços", value=False)
    resp_ok = c7.checkbox("Respostas Ativas", value=False)

with col_score:
    # Cálculo dinâmico da pontuação
    itens = [tour_ok, fotos_ok, cat_ok, horarios_ok, desc_ok, atrib_ok, resp_ok]
    score = int((sum(itens) / len(itens)) * 100)
    
    st.markdown(f"""
    <div class="card-diag">
        <h2 style="color: #f8fafc; margin: 0;">Score Geral: {score}/100</h2>
        <br/>
        <h4 style="color: #f8fafc; margin-bottom: 10px;">Falhas e Recomendações:</h4>
        <ul style="color: #cbd5e1; font-size: 14px; line-height: 1.8;">
            <li>Tour 360°: {'✅ Presente' if tour_ok else '❌ Ausente'}</li>
            <li>Fotos HD: {'✅ OK' if fotos_ok else '❌ Poucas / Inexistentes'}</li>
            <li>Categorias: {'✅ OK' if cat_ok else '❌ Incompletas (Ajustar Secundárias)'}</li>
            <li>Horários: {'✅ Atualizados' if horarios_ok else '❌ Falta atualizar'}</li>
            <li>Descrição: {'✅ OK' if desc_ok else '❌ Ausente'}</li>
            <li>Atributos de Serviços: {'✅ Completos' if atrib_ok else '❌ Ausentes / Pendentes'}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/><br/>", unsafe_allow_html=True)
st.caption("tour360vr.com.br | contato@tour360vr.com.br | Whatsapp: (16) 99133-2121 | Tour360VR - Gestão de Perfil do Google")

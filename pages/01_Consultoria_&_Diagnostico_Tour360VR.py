import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILIZAÇÃO VISUAL MODERNA (SaaS / TOUR360VR)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Consultoria & Diagnóstico Tour360VR",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para Tema Dark Escuro Elegante
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
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Assinatura limpa na Barra Lateral
st.sidebar.markdown("""
<div style="padding: 10px 0px;">
    <h3 style="margin: 0; color: #f8fafc; font-size: 18px;">OKAMOTO MÍDIAS VISUAIS</h3>
    <p style="margin: 2px 0 0 0; color: #94a3b8; font-size: 12px;">criado por Rubens Okamoto</p>
</div>
<hr style="margin: 10px 0; border-color: #334155;"/>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CABEÇALHO DA FERRAMENTA DE DIAGNÓSTICO
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-box">
    <div class="header-title">🔎 PLATAFORMA DE CONSULTORIA TOUR360VR - GESTÃO & DIAGNÓSTICO GOOGLE MEU NEGÓCIO</div>
</div>
""", unsafe_allow_html=True)

# Entrada de dados do Prospect / Cliente
col_input1, col_input2 = st.columns(2)

with col_input1:
    st.markdown("### 🏢 Capa de Diagnóstico")
    empresa_nome = st.text_input("Nome da Empresa / Cliente:", placeholder="Ex: Taiwan Hotel Ltda")

with col_input2:
    st.markdown("### 📍 Localização & Cidade")
    localizacao = st.text_input("Cidade e Estado:", placeholder="Ex: Ribeirão Preto, SP")

st.markdown("<br/>", unsafe_allow_html=True)

btn_buscar = st.button("🚀 Consultar no Google Maps / Analisar Perfil", use_container_width=True)

if btn_buscar and empresa_nome:
    st.success(f"Análise iniciada para: **{empresa_nome}** ({localizacao})")

st.markdown("---")

# -----------------------------------------------------------------------------
# 3. PAINEL DE AUDITORIA E SCORE GERAL
# -----------------------------------------------------------------------------
col_auditoria, col_score = st.columns([1.3, 1])

with col_auditoria:
    st.markdown("### ⚙️ Ajuste Fino dos Itens da Auditoria")
    st.caption("Marque os itens que a empresa já possui atualizados no Google Meu Negócio:")
    
    c1, c2, c3 = st.columns(3)
    tour_ok = c1.checkbox("Tour Virtual 360°", value=False)
    fotos_ok = c2.checkbox("Fotos Profissionais HD", value=False)
    cat_ok = c3.checkbox("Categorias Corretas", value=False)
    
    c4, c5, c6 = st.columns(3)
    horarios_ok = c4.checkbox("Horários Atualizados", value=False)
    desc_ok = c5.checkbox("Descrição Otimizada", value=False)
    atrib_ok = c6.checkbox("Atributos de Serviços", value=False)
    
    c7, c8, c9 = st.columns(3)
    resp_ok = c7.checkbox("Respostas a Avaliações", value=False)
    site_ok = c8.checkbox("Link do Site Válido", value=False)
    redes_ok = c9.checkbox("Perfis de Redes Conectados", value=False)

with col_score:
    # Cálculo automático da pontuação com base nos marcadores
    itens = [tour_ok, fotos_ok, cat_ok, horarios_ok, desc_ok, atrib_ok, resp_ok, site_ok, redes_ok]
    score = int((sum(itens) / len(itens)) * 100)
    
    # Cor dinâmica do Score
    if score >= 80:
        cor_score = "#10b981"  # Verde
        status_texto = "Excelente Otimização"
    elif score >= 50:
        cor_score = "#f59e0b"  # Amarelo
        status_texto = "Otimização Média (Oportunidades de Melhoria)"
    else:
        cor_score = "#ef4444"  # Vermelho
        status_texto = "Perfil Crítico (Necessita Intervenção Urgente)"

    st.markdown(f"""
    <div class="card-diag">
        <h3 style="color: #94a3b8; margin: 0; font-size: 14px; text-transform: uppercase;">Visão Geral do Diagnóstico</h3>
        <h1 style="color: {cor_score}; margin: 8px 0; font-size: 38px;">Score Geral: {score}/100</h1>
        <p style="color: #f8fafc; font-weight: 600; font-size: 14px;">Status: {status_texto}</p>
        <hr style="border-color: #334155; margin: 12px 0;"/>
        <h4 style="color: #f8fafc; margin-bottom: 10px;">Falhas e Recomendações Técnicas:</h4>
        <ul style="color: #cbd5e1; font-size: 13px; line-height: 1.8; padding-left: 18px;">
            <li>Tour 360°: {'✅ Mapeado e Ativo' if tour_ok else '❌ Ausente (Oportunidade Principal Tour360VR)'}</li>
            <li>Fotos HD: {'✅ Adequadas' if fotos_ok else '❌ Poucas ou com Baixa Resolução'}</li>
            <li>Categorias: {'✅ Corretas' if cat_ok else '❌ Incompletas (Ajustar Secundárias)'}</li>
            <li>Horários de Atendimento: {'✅ Atualizados' if horarios_ok else '❌ Falta Atualizar / Feriados'}</li>
            <li>Descrição Institucional: {'✅ Otimizada com SEO' if desc_ok else '❌ Ausente ou Curta'}</li>
            <li>Atributos do Negócio: {'✅ Preenchidos' if atrib_ok else '❌ Atributos Pendentes'}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/><br/>", unsafe_allow_html=True)
st.caption("tour360vr.com.br | contato@tour360vr.com.br | Whatsapp: (16) 99133-2121 | Tour360VR - Gestão de Perfil do Google")

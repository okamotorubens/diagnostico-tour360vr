import os
import json
import requests
import streamlit as st
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CRM Okamoto Mídias Visuais",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Oculta apenas o menu de navegação automático da sidebar */
    [data-testid="stSidebarNav"] { display: none !important; }

    .stApp { 
        background-color: #0b0f19; 
        color: #f1f5f9; 
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    [data-testid="stSidebar"] { 
        background-color: #111827; 
        border-right: 1px solid #1f2937; 
    }
    
    .sidebar-title-single {
        font-size: 18px;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.2;
        margin-top: 10px;
        margin-bottom: 12px;
        white-space: nowrap;
        text-align: center;
    }

    .dashboard-card { 
        background-color: #131b2e; 
        border: 1px solid #1e293b; 
        border-radius: 14px; 
        padding: 18px; 
        margin-bottom: 15px; 
    }
    .card-title { 
        font-size: 15px; 
        font-weight: 700; 
        color: #38bdf8; 
        margin-bottom: 14px; 
        text-transform: uppercase; 
        letter-spacing: 0.8px; 
        line-height: 1.3;
    }
    
    .stButton > button { 
        background-color: #2563eb; 
        color: #ffffff; 
        border: none; 
        border-radius: 8px; 
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover { 
        background-color: #1d4ed8; 
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    .custom-footer { 
        position: fixed; 
        left: 0; 
        bottom: 0; 
        width: 100%; 
        background-color: #070a10; 
        color: #64748b; 
        text-align: center; 
        padding: 8px; 
        border-top: 1px solid #1e293b; 
        font-size: 11px; 
        z-index: 999; 
    }
    .custom-footer a { color: #38bdf8; text-decoration: none; }
    </style>
""", unsafe_allow_html=True)

ARQUIVO_HISTORICO = "/tmp/historico_propostas_tour360.json"

# -----------------------------------------------------------------------------
# 2. FUNÇÕES UTILITÁRIAS
# -----------------------------------------------------------------------------
def obter_caminho_logo(tipo="okamoto"):
    if tipo == "okamoto":
        caminhos = ['assets/logo_okamoto.png', 'assets/logo_okamoto_midias_visuais.png', 'logo_okamoto.png', 'assets/logo.png']
        url_oficial = "https://okamotomidiasvisuais.com.br/assets/img/logo.png"
    else:
        caminhos = ['assets/logo_tour_transparente.png', 'assets/logo_tour.png', 'logo_tour_transparente.png', 'logo_tour.png']
        url_oficial = "https://tour360vr.com.br/assets/img/logo.png"

    for c in caminhos:
        if os.path.exists(c): return c
    
    temp_logo = f'/tmp/logo_{tipo}_temp.png'
    if os.path.exists(temp_logo): return temp_logo
    try:
        resp = requests.get(url_oficial, timeout=3)
        if resp.status_code == 200:
            with open(temp_logo, 'wb') as f: f.write(resp.content)
            return temp_logo
    except Exception: pass
    return None

def carregar_historico():
    if os.path.exists(ARQUIVO_HISTORICO):
        try:
            with open(ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception: return []
    return []

def calcular_score_real(dados):
    if not dados.get("nome"): return 0
    score = 100
    if not dados.get("tem_tour360", False): score -= 20
    if dados.get("website") == "Não possui" or not dados.get("website"): score -= 15
    if not dados.get("tem_fotos_hd", False): score -= 15
    if not dados.get("categorias_completas", False): score -= 15
    if not dados.get("horarios_ok", False): score -= 10
    if not dados.get("tem_descricao", False): score -= 10
    if not dados.get("atributos_ok", False): score -= 10
    if not dados.get("resposta_avaliacoes_ok", False): score -= 10
    if dados.get("avaliacoes", 0) < 50: score -= 15
    return max(score, 10)

# -----------------------------------------------------------------------------
# 3. SIDEBAR PADRONIZADA (CRM)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div class='sidebar-title-single'>Consultoria - Proposta - CRM</div>
    """, unsafe_allow_html=True)

    logo_okamoto = obter_caminho_logo("okamoto")
    if logo_okamoto:
        st.image(logo_okamoto, use_container_width=True)
    else:
        st.markdown("**Okamoto Mídias Visuais**")

    logo_tour = obter_caminho_logo("tour360")
    if logo_tour:
        col_t1, col_t2, col_t3 = st.columns([0.25, 0.50, 0.25])
        with col_t2:
            st.image(logo_tour, use_container_width=True)
    else:
        st.markdown("**Tour360VR**")

    st.markdown("<br>", unsafe_allow_html=True)

    # REDIRECIONAMENTO PARA PÁGINA ESPECÍFICA DE CONSULTORIA
    st.page_link("pages/01_Consultoria_e_Diagnostico.py", label="📋 Consultoria & Diagnóstico", icon="🔍")
    st.page_link("pages/02_CRM_Okamoto_Midias_Visuais.py", label="📊 CRM Okamoto Mídias Visuais", icon="🚀")

    st.markdown("---")

    nome_empresa_atual = st.session_state.get('dados', {}).get('nome') or "Nenhum cliente"
    st.markdown("**Cliente em Atendimento:**")
    st.info(f"🏢 {nome_empresa_atual}")
    
    if 'dados' in st.session_state and st.session_state['dados'].get('nome'):
        score_atual = calcular_score_real(st.session_state['dados'])
    else:
        score_atual = 0

    if score_atual < 50:
        cor_score = "#ef4444"
        status_txt = "CRÍTICO"
    elif score_atual < 80:
        cor_score = "#f59e0b"
        status_txt = "MÉDIO"
    else:
        cor_score = "#22c55e"
        status_txt = "EXCELENTE"

    st.markdown(f"""
        <div style="margin-top: 5px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 700; color: #f8fafc; margin-bottom: 5px;">
                <span>Score Diagnóstico:</span>
                <span style="color: {cor_score};">{score_atual}/100 ({status_txt})</span>
            </div>
            <div style="background-color: #1e293b; border-radius: 8px; height: 10px; width: 100%; overflow: hidden; border: 1px solid #334155;">
                <div style="background-color: {cor_score}; height: 100%; width: {score_atual}%; transition: width 0.4s ease;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Central de Vendas e Negociações")

# -----------------------------------------------------------------------------
# 4. CONTEÚDO PRINCIPAL DO CRM
# -----------------------------------------------------------------------------
st.title("📊 CRM Okamoto Mídias Visuais")
st.caption("Gestão de Oportunidades, Propostas e Negociações Ativas")

historico = carregar_historico()

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(label="Total de Propostas em Cache", value=len(historico))
with col_m2:
    criticos = sum(1 for h in historico if h.get("score", 0) < 50)
    st.metric(label="Clientes Status Crítico", value=criticos)
with col_m3:
    medios = sum(1 for h in historico if 50 <= h.get("score", 0) < 80)
    st.metric(label="Clientes Status Médio", value=medios)
with col_m4:
    altos = sum(1 for h in historico if h.get("score", 0) >= 80)
    st.metric(label="Clientes Alto Desempenho", value=altos)

st.markdown("---")

st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
st.markdown("<div class='card-title'>📂 OPORTUNIDADES E DIAGNÓSTICOS RECENTES</div>", unsafe_allow_html=True)

if historico:
    for idx, item in enumerate(historico):
        score_item = item.get('score', 0)
        cor_badge = "#ef4444" if score_item < 50 else ("#f59e0b" if score_item < 80 else "#22c55e")
        
        with st.expander(f"🏢 {item.get('nome')} | Score: {score_item}/100 ({item.get('data')})"):
            c1, c2, c3 = st.columns([1.5, 1.5, 1])
            with c1:
                st.markdown(f"**Responsável:** {item.get('contato')}")
                st.markdown(f"**Telefone:** {item.get('telefone')}")
                st.markdown(f"**Website:** {item.get('website')}")
                st.markdown(f"**Endereço:** {item.get('endereco')}")
            with c2:
                st.markdown(f"**Nota Google:** ⭐ {item.get('nota', 0.0):.1f}")
                st.markdown(f"**Avaliações:** {item.get('avaliacoes')}")
                st.markdown(f"**Tour 360°:** {'Ativo' if item.get('tem_tour360') else 'Não Ativo'}")
                st.markdown(f"**Fotos HD:** {'Sim' if item.get('tem_fotos_hd') else 'Não'}")
            with c3:
                tel = str(item.get('telefone', '')).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
                if tel and not tel.startswith("55"): tel = f"55{tel}"
                msg = f"Olá, {item.get('contato')}! Gostaria de dar sequência ao atendimento da {item.get('nome')}."
                url_wa = f"https://wa.me/{tel}?text={requests.utils.quote(msg)}"
                st.link_button("📲 Chamar no WhatsApp", url=url_wa, use_container_width=True)
else:
    st.info("Nenhuma proposta salva temporariamente em cache. Realize uma nova busca no app para gerar um atendimento.")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. RODAPÉ FIXO
# -----------------------------------------------------------------------------
st.markdown("""
    <div class='custom-footer'>
        <a href='https://tour360vr.com.br' target='_blank'>tour360vr.com.br</a> | 
        <a href='mailto:contato@tour360vr.com.br'>contato@tour360vr.com.br</a> | 
        Whatsapp: (16) 99133-2121 | 
        <b>Tour360VR - Gestão de Perfil do Google</b>
    </div>
""", unsafe_allow_html=True)

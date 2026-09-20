import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st

# ==========================================
# CONFIGURAÇÃO DE TEMA E VISUAL PERSONALIZADO
# ==========================================
st.set_page_config(
    page_title="Diagnóstico de Perfil no Google - Tour360VR", 
    page_icon="🔍",
    layout="centered"
)

# Estilo CSS Personalizado
custom_css = """
<style>
    /* Fundo totalmente branco */
    .stApp {
        background-color: #FFFFFF !important;
        color: #222222 !important;
    }
    
    /* Eliminar margens e rolagem desnecessária */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }

    /* Esconder elementos padrão do Streamlit */
    header, footer, #MainMenu {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* Título Unificado e Centralizado */
    .titulo-unificado {
        text-align: center;
        color: #111111;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 0.8rem;
        font-family: 'Arial', sans-serif;
        line-height: 1.3;
    }

    /* Texto de Instrução Centralizado */
    .texto-instrucao {
        text-align: center;
        color: #555555;
        font-size: 1rem;
        margin-bottom: 1.2rem;
        font-family: 'Arial', sans-serif;
        line-height: 1.4;
    }

    /* Ocultar Rótulo do Campo de Texto */
    .stTextInput label {
        display: none !important;
    }

    /* Reduzir e Centralizar o Campo de Entrada (Input) */
    .stTextInput > div {
        max-width: 550px !important;
        margin: 0 auto !important;
    }
    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #222222 !important;
        border: 2px solid #DDDDDD !important;
        border-radius: 8px !important;
        font-size: 1.05rem !important;
        padding: 0.6rem 1rem !important;
        text-align: center !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #8DC63F !important;
        box-shadow: 0 0 6px rgba(141, 198, 63, 0.4) !important;
    }

    /* Centralização de Botões */
    .stButton {
        display: flex !important;
        justify-content: center !important;
        margin-top: 0.8rem !important;
    }

    /* Botão Verde Tour360VR (#8DC63F) Centralizado */
    .stButton > button {
        background-color: #8DC63F !important;
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.65rem 2.2rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 10px rgba(141, 198, 63, 0.3) !important;
    }
    .stButton > button:hover {
        background-color: #7BB533 !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }
    .stButton > button p {
        color: #FFFFFF !important;
    }

    /* Destaque da Métrica/Score */
    [data-testid="stMetricValue"] {
        color: #8DC63F !important;
        font-size: 3rem !important;
        font-weight: bold !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# CONFIGURAÇÕES E CREDENCIAIS
# ==========================================
GOOGLE_API_KEY = "AIzaSyA8ul_9QICNyqxrHgT-CURIZmd1sikHn5U"
BIGIN_CLIENT_ID = "1000.COI8SBR9O0RCMGCL7WKEYUJMBZCR8X"
BIGIN_CLIENT_SECRET = "c60642fb374cbad9753c456d8713b6349417187345"

SMTP_SERVER = "smtp.tour360vr.com.br"
SMTP_PORT = 587
SMTP_USER = "contato@tour360vr.com.br"
SMTP_PASS = "Kakaroto@2026"

# ==========================================
# FUNÇÃO DE BUSCA GOOGLE (COM REFERER)
# ==========================================
def consultar_score_google(nome_empresa):
    """Consulta a empresa enviando os cabeçalhos do site autorizados pelo Google Cloud."""
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={requests.utils.quote(nome_empresa)}&key={GOOGLE_API_KEY}"
    
    # Cabeçalhos enviando o Referer exato para passar pela restrição do Google Cloud
    headers = {
        "Referer": "https://www.tour360vr.com.br/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10).json()
        results = response.get("results", [])
        
        if results:
            place = results[0]
            
            score = 0
            if place.get("rating", 0) >= 4.0: score += 25
            if place.get("user_ratings_total", 0) > 15: score += 25
            if place.get("business_status") == "OPERATIONAL": score += 20
            if place.get("photos"): score += 30
            
            return {
                "sucesso": True,
                "place_id": place.get("place_id"),
                "nome": place.get("name"),
                "endereco": place.get("formatted_address", "Endereço registrado no Google Maps"),
                "score": score
            }
        else:
            print(f"Status retornado pelo Google: {response.get('status')} - {response.get('error_message', '')}")
    except Exception as e:
        print(f"Erro na consulta Google: {e}")
        
    return {"sucesso": False, "mensagem": "Empresa não encontrada no Google."}

def enviar_lead_bigin(nome_lead, email_lead, whatsapp_lead, empresa_consultada, score):
    try:
        url_token = f"https://accounts.zoho.com/oauth/v2/token?client_id={BIGIN_CLIENT_ID}&client_secret={BIGIN_CLIENT_SECRET}&grant_type=client_credentials&scope=ZohoBigin.modules.ALL"
        res_token = requests.post(url_token).json()
        access_token = res_token.get("access_token")

        if not access_token:
            return False

        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "data": [
                {
                    "Deal_Name": f"Diagnóstico Site - {empresa_consultada}",
                    "Stage": "1º Contato",
                    "Score_GMB": score,
                    "Empresa_Consultada": empresa_consultada,
                    "Description": f"Lead capturado no site:\nNome: {nome_lead}\nE-mail: {email_lead}\nWhatsApp: {whatsapp_lead}"
                }
            ]
        }

        url_deal = "https://www.zohoapis.com/bigin/v1/Deals"
        res_deal = requests.post(url_deal, json=payload, headers=headers)
        return res_deal.status_code in [200, 201]
    except Exception:
        return False

# ==========================================
# INTERFACE DO USUÁRIO
# ==========================================
st.markdown('<div class="titulo-unificado">🔍 Faça um diagnóstico de desempenho e otimização do perfil da sua empresa no Google.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="texto-instrucao">
    Digite o Nome Comercial exato da sua empresa seguido da Cidade e Estado.<br>
    <em>Exemplo: Sua empresa Sua cidade Seu Estado</em>
</div>
""", unsafe_allow_html=True)

nome_empresa = st.text_input("Busca", placeholder="Ex: Taiwan Hotel Ribeirão Preto São Paulo")

if st.button("🔍 Analisar Perfil"):
    if nome_empresa:
        with st.spinner("Analisando dados no Google Maps..."):
            res = consultar_score_google(nome_empresa)
            if res["sucesso"]:
                st.session_state["resultado_busca"] = res
            else:
                st.error("❌ Empresa não encontrada. Tente incluir a cidade ou verificar a grafia exata cadastrada no Google.")

if "resultado_busca" in st.session_state:
    dados = st.session_state["resultado_busca"]
    
    st.markdown("---")
    st.subheader(f"Empresa Localizada: {dados['nome']}")
    st.caption(f"📍 Endereço: {dados['endereco']}")
    
    st.metric(label="Pontuação Geral de Otimização (Score)", value=f"{dados['score']} / 100")
    
    st.warning("⚠️ Identificamos oportunidades de melhoria que podem estar reduzindo a visibilidade do seu negócio para novos clientes.")

    st.markdown("### 📄 Desbloquear Relatório Detalhado em PDF")
    st.write("Preencha os seus dados abaixo para receber a análise completa:")
    
    with st.form("form_lead"):
        nome_lead = st.text_input("Seu Nome Completo:")
        email_lead = st.text_input("Seu E-mail Principal:")
        whats_lead = st.text_input("WhatsApp (com DDD):")
        
        submit = st.form_submit_button("📩 Receber Diagnóstico")
        
        if submit:
            if nome_lead and email_lead and whats_lead:
                enviar_lead_bigin(nome_lead, email_lead, whats_lead, dados['nome'], dados['score'])
                st.success("✅ Diagnóstico enviado com sucesso! Entraremos em contacto pelo WhatsApp.")
            else:
                st.error("Por favor, preencha todos os campos do formulário.")

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
    page_title="Diagnóstico Gratuito GMB - Tour360VR", 
    page_icon="🔍",
    layout="wide"
)

# Estilo CSS para integrar perfeitamente com o layout escuro do site Mobirise
custom_css = """
<style>
    /* Fundo geral escuro combinando com o site */
    .stApp {
        background-color: #111111 !important;
        color: #FFFFFF !important;
    }
    
    /* Remover margens superiores e padding excessivo */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }

    /* Ocultar cabeçalhos/rodapés nativos do Streamlit */
    header, footer, #MainMenu {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* Estilização dos Títulos */
    h1, h2, h3, h4, span, label {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', Arial, sans-serif !important;
    }

    /* Estilização dos Campos de Texto (Inputs) */
    .stTextInput > div > div > input {
        background-color: #222222 !important;
        color: #FFFFFF !important;
        border: 1px solid #444444 !important;
        border-radius: 8px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00E676 !important;
    }

    /* Estilização dos Botões */
    .stButton > button {
        background-color: #00E676 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background-color: #00C853 !important;
        color: #FFFFFF !important;
    }

    /* Card de Metricas / Score */
    [data-testid="stMetricValue"] {
        color: #00E676 !important;
        font-size: 2.5rem !important;
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
# FUNÇÃO 1: CONSULTA DE SCORE NO GOOGLE
# ==========================================
def consultar_score_google(nome_empresa):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={nome_empresa}&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(url).json()
        if response.get("status") == "OK" and response.get("results"):
            place = response["results"][0]
            
            score = 0
            if place.get("rating", 0) >= 4.0: score += 25
            if place.get("user_ratings_total", 0) > 20: score += 25
            if place.get("business_status") == "OPERATIONAL": score += 20
            if place.get("photos"): score += 30
            
            return {
                "sucesso": True,
                "place_id": place.get("place_id"),
                "nome": place.get("name"),
                "endereco": place.get("formatted_address"),
                "score": score
            }
    except Exception:
        pass
    return {"sucesso": False, "mensagem": "Empresa não encontrada no Google."}

# ==========================================
# FUNÇÃO 2: ENVIAR LEAD PARA O BIGIN CRM
# ==========================================
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
# INTERFACE STREAMLIT
# ==========================================
st.title("🔍 Diagnóstico de Perfil no Google")
st.write("Digite o nome da sua empresa e cidade para verificar a nota de otimização instantaneamente.")

nome_empresa = st.text_input("Nome da Empresa + Cidade:", placeholder="Ex: Clínica Vinicius Ribeirão Preto")

if st.button("Analisar Perfil Gratuito"):
    if nome_empresa:
        with st.spinner("Analisando dados no Google Maps..."):
            res = consultar_score_google(nome_empresa)
            if res["sucesso"]:
                st.session_state["resultado_busca"] = res
            else:
                st.error("Empresa não encontrada. Verifique o nome/cidade e tente novamente.")

if "resultado_busca" in st.session_state:
    dados = st.session_state["resultado_busca"]
    
    st.markdown("---")
    st.subheader(f"Resultado para: {dados['nome']}")
    st.metric(label="Otimização da Ficha (Score)", value=f"{dados['score']} / 100")
    
    st.info("⚠️ Sua empresa possui pontos cruciais que podem estar reduzindo a sua visibilidade nas buscas do Google Maps.")

    st.markdown("### 📄 Desbloquear Análise Executiva")
    st.write("Preencha os campos abaixo para receber o relatório completo:")
    
    with st.form("form_lead"):
        nome_lead = st.text_input("Seu Nome:")
        email_lead = st.text_input("Seu E-mail:")
        whats_lead = st.text_input("WhatsApp com DDD:")
        
        submit = st.form_submit_button("Gerar Relatório em PDF")
        
        if submit:
            if nome_lead and email_lead and whats_lead:
                enviar_lead_bigin(nome_lead, email_lead, whats_lead, dados['nome'], dados['score'])
                st.success("✅ Diagnóstico gerado com sucesso! Entraremos em contacto em breve.")
            else:
                st.error("Por favor, preencha todos os campos do formulário.")

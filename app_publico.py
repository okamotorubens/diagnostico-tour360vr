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
    layout="centered"
)

# Estilo CSS Personalizado (Fundo Branco, Botão Verde com Texto Branco)
custom_css = """
<style>
    /* Fundo totalmente branco e texto escuro */
    .stApp {
        background-color: #FFFFFF !important;
        color: #222222 !important;
    }
    
    /* Eliminar margens e rolagem desnecessária */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 100% !important;
    }

    /* Esconder elementos padrão do Streamlit */
    header, footer, #MainMenu {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* Centralização e Destaque dos Títulos */
    .titulo-principal {
        text-align: center;
        color: #222222;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        font-family: 'Arial', sans-serif;
    }
    .subtitulo {
        text-align: center;
        color: #555555;
        font-size: 1.15rem;
        margin-bottom: 1.2rem;
        font-family: 'Arial', sans-serif;
    }

    /* Estilização das Legendas e Rótulos */
    label, p, span {
        color: #222222 !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }

    /* Caixa explicativa de instrução (Sem o 'Como pesquisar corretamente') */
    .caixa-instrucao {
        background-color: #F4F6F8;
        border-left: 5px solid #8CC63F;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 15px;
        font-size: 1rem;
        color: #333333;
    }

    /* Campos de Entrada (Inputs) */
    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #222222 !important;
        border: 2px solid #CCCCCC !important;
        border-radius: 8px !important;
        font-size: 1.1rem !important;
        padding: 0.6rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #8CC63F !important;
        box-shadow: 0 0 5px rgba(140, 198, 63, 0.5) !important;
    }

    /* Botão Verde Oficial Tour360VR (#8cc63f) com TEXTO BRANCO */
    .stButton > button {
        background-color: #8CC63F !important;
        color: #FFFFFF !important;
        font-size: 1.15rem !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 10px rgba(140, 198, 63, 0.3) !important;
    }
    .stButton > button:hover {
        background-color: #7BB433 !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }
    .stButton > button p {
        color: #FFFFFF !important;
    }

    /* Destaque da Métrica/Score */
    [data-testid="stMetricValue"] {
        color: #8CC63F !important;
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
# FUNÇÕES DE BUSCA E INTEGRAÇÃO ROBUSTAS
# ==========================================
def consultar_score_google(nome_empresa):
    """Realiza busca robusta usando o Places API FindPlaceFromText com fallback para TextSearch."""
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # 1. Tentativa via FindPlaceFromText (Mais preciso e rápido)
    url_find = (
        f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        f"?input={requests.utils.quote(nome_empresa)}&inputtype=textquery"
        f"&fields=place_id,name,formatted_address,rating,user_ratings_total,business_status,photos"
        f"&key={GOOGLE_API_KEY}"
    )
    
    try:
        res = requests.get(url_find, headers=headers, timeout=8).json()
        
        candidates = res.get("candidates", [])
        if not candidates:
            # 2. Fallback via TextSearch caso o FindPlace não retorne
            url_text = (
                f"https://maps.googleapis.com/maps/api/place/textsearch/json"
                f"?query={requests.utils.quote(nome_empresa)}&key={GOOGLE_API_KEY}"
            )
            res_text = requests.get(url_text, headers=headers, timeout=8).json()
            candidates = res_text.get("results", [])

        if candidates:
            place = candidates[0]
            
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
st.markdown('<div class="titulo-principal">🔍 Diagnóstico de Perfil no Google</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Faça um diagnóstico de desempenho e otimização da sua empresa no Google.</div>', unsafe_allow_html=True)

# Instrução Direta e Objetiva
st.markdown("""
<div class="caixa-instrucao">
    📌 Digite o <strong>Nome Comercial exato</strong> da sua empresa seguido da <strong>Cidade e Estado</strong>.<br>
    <em>Exemplo: <strong>Toque de Letra Ribeirão Preto SP</strong></em>
</div>
""", unsafe_allow_html=True)

nome_empresa = st.text_input("🏢 Nome da Empresa + Cidade:", placeholder="Ex: Toque de Letra Ribeirão Preto SP")

if st.button("🔍 Analisar Perfil Gratuito"):
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
        
        submit = st.form_submit_button("📩 Receber Diagnóstico Gratuito")
        
        if submit:
            if nome_lead and email_lead and whats_lead:
                enviar_lead_bigin(nome_lead, email_lead, whats_lead, dados['nome'], dados['score'])
                st.success("✅ Diagnóstico enviado com sucesso! Entraremos em contacto pelo WhatsApp.")
            else:
                st.error("Por favor, preencha todos os campos do formulário.")

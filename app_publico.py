import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

# ==========================================
# CONFIGURAÇÃO DE TEMA E VISUAL PERSONALIZADO
# ==========================================
st.set_page_config(
    page_title="Diagnóstico do Perfil no Google - Tour360VR", 
    page_icon="🔍",
    layout="centered"
)

# Estilo CSS Ajustado (Textos sem cortes e botões centralizados)
custom_css = """
<style>
    /* Fundo totalmente branco */
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Largura adequada para não cortar textos */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 750px !important;
    }

    /* Esconder elementos nativos do Streamlit */
    header, footer, #MainMenu {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* Título Ajustado (Permite quebra fluida se a tela for menor) */
    .titulo-principal {
        text-align: center;
        color: #000000 !important;
        font-size: 1.55rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
        font-family: 'Arial', sans-serif;
        line-height: 1.3;
    }

    .instrucao-subtitulo {
        text-align: center;
        color: #333333 !important;
        font-size: 1.05rem;
        font-weight: bold;
        margin-bottom: 1.2rem;
        font-family: 'Arial', sans-serif;
        line-height: 1.3;
    }

    /* Reduzir Tamanho do Texto 'Empresa Localizada' */
    .empresa-localizada-titulo {
        text-align: center;
        color: #000000 !important;
        font-size: 1.25rem !important;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.2rem;
    }

    /* Alerta Amarelo em Destaque */
    .alerta-destaque {
        background-color: #FFFDE7 !important;
        border: 2px solid #FBC02D !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        text-align: center !important;
        color: #5D4037 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin: 1.2rem auto !important;
        max-width: 550px !important;
    }

    /* Estilização dos Rótulos e Textos */
    label, p, span, h1, h2, h3, h4 {
        color: #000000 !important;
        font-family: 'Arial', sans-serif !important;
    }

    /* Campos de Entrada de Texto Centralizados */
    .stTextInput {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    .stTextInput > div {
        max-width: 500px !important;
        width: 100% !important;
        margin: 0 auto !important;
    }
    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #CCCCCC !important;
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
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin: 1rem auto !important;
    }

    /* Botão Verde (#8DC63F) com Texto Perfeitamente Centralizado */
    .stButton > button {
        background-color: #8DC63F !important;
        color: #FFFFFF !important;
        font-size: 1.15rem !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(141, 198, 63, 0.3) !important;
        margin: 0 auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        max-width: 320px !important;
    }
    .stButton > button:hover {
        background-color: #7BB533 !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }
    .stButton > button p {
        color: #FFFFFF !important;
        font-size: 1.15rem !important;
        font-weight: bold !important;
        margin: 0 !important;
        text-align: center !important;
    }

    /* Métrica do Score Centralizada */
    [data-testid="stMetricValue"] {
        color: #8DC63F !important;
        font-size: 3.2rem !important;
        font-weight: bold !important;
        text-align: center !important;
    }
    [data-testid="stMetric"] {
        display: flex !important;
        justify-content: center !important;
        text-align: center !important;
    }

    /* Chamada do Formulário */
    .destaque-formulario {
        text-align: center;
        color: #000000 !important;
        font-size: 1.25rem;
        font-weight: 800;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        font-family: 'Arial', sans-serif;
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
# FUNÇÃO DE SCORE E BUSCA NO GOOGLE MAPS
# ==========================================
def consultar_score_google_rigoroso(nome_empresa):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={requests.utils.quote(nome_empresa)}&key={GOOGLE_API_KEY}"
    headers = {"Referer": "https://www.tour360vr.com.br/"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10).json()
        results = response.get("results", [])
        
        if results:
            place = results[0]
            place_id = place.get("place_id")
            
            url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,user_ratings_total,business_status,photos,formatted_phone_number,website,types,formatted_address,opening_hours&key={GOOGLE_API_KEY}"
            res_details = requests.get(url_details, headers=headers, timeout=10).json()
            details = res_details.get("result", place)

            score = 0
            if details.get("business_status") == "OPERATIONAL": score += 10
            if details.get("rating", 0) >= 4.2 and details.get("user_ratings_total", 0) >= 15: score += 20
            
            photos = details.get("photos", [])
            if len(photos) >= 5: score += 15
            elif len(photos) > 0: score += 5
                
            if details.get("formatted_phone_number"): score += 10
            if details.get("website"): score += 15
            if details.get("opening_hours"): score += 10
            
            addr = details.get("formatted_address", "")
            if addr and any(char.isdigit() for char in addr): score += 10
            if details.get("types"): score += 10

            return {
                "sucesso": True,
                "place_id": place_id,
                "nome": details.get("name"),
                "endereco": details.get("formatted_address", "Endereço registrado no Google Maps"),
                "score": min(score, 100)
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
                    "Score_GMB": str(score),
                    "Empresa_Consultada": empresa_consultada,
                    "Description": f"Lead capturado no site Tour360VR:\nNome: {nome_lead}\nE-mail: {email_lead}\nWhatsApp: {whatsapp_lead}\nScore: {score}/100"
                }
            ]
        }

        url_deal = "https://www.zohoapis.com/bigin/v1/Deals"
        res_deal = requests.post(url_deal, json=payload, headers=headers)
        return res_deal.status_code in [200, 201]
    except Exception as e:
        print(f"Erro Bigin: {e}")
        return False

def enviar_email_notificacao(nome_lead, email_lead, whatsapp_lead, empresa_consultada, score):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = SMTP_USER
        msg['Subject'] = f"Novo Lead Diagnóstico GMB - {empresa_consultada}"

        corpo = f"""
        Novo Lead Capturado na Isca do Site:

        Empresa Consultada: {empresa_consultada}
        Pontuação Score: {score}/100

        Dados do Cliente:
        - Nome: {nome_lead}
        - E-mail: {email_lead}
        - WhatsApp: {whatsapp_lead}
        """
        msg.attach(MIMEText(corpo, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erro Email: {e}")
        return False

# ==========================================
# INTERFACE DO USUÁRIO
# ==========================================
st.markdown('<div class="titulo-principal">🔍 Faça um diagnóstico do perfil da sua empresa no Google.</div>', unsafe_allow_html=True)
st.markdown('<div class="instrucao-subtitulo">Digite o Nome Comercial exato da sua empresa seguido da Cidade e Estado.</div>', unsafe_allow_html=True)

nome_empresa = st.text_input("BuscaEmpresa", placeholder="Nome da empresa + cidade + estado", label_visibility="collapsed")

if st.button("🔍 Analisar perfil"):
    if nome_empresa:
        with st.spinner("Analisando perfil no Google Maps..."):
            res = consultar_score_google_rigoroso(nome_empresa)
            if res["sucesso"]:
                st.session_state["resultado_busca"] = res
            else:
                st.error("❌ Empresa não encontrada. Tente incluir a cidade ou verificar a grafia exata cadastrada no Google.")

# Exibição dos Resultados
if "resultado_busca" in st.session_state:
    dados = st.session_state["resultado_busca"]
    
    st.markdown("<hr style='margin: 1.2rem 0;'>", unsafe_allow_html=True)
    
    st.markdown(f'<div class="empresa-localizada-titulo">Empresa Localizada: {dados["nome"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #666666; font-size: 0.95rem; margin-bottom: 0.8rem;">📍 {dados["endereco"]}</p>', unsafe_allow_html=True)
    
    st.metric(label="Pontuação Geral de Otimização (Score)", value=f"{dados['score']} / 100")
    
    st.markdown("""
    <div class="alerta-destaque">
        ⚠️ Identificamos oportunidades de melhoria que podem estar reduzindo a visibilidade do seu negócio para novos clientes.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="destaque-formulario">Preencha os dados abaixo e receba a análise completa</div>', unsafe_allow_html=True)
    
    with st.form("form_lead_publico"):
        nome_lead = st.text_input("NomeLead", placeholder="Seu nome completo", label_visibility="collapsed")
        email_lead = st.text_input("EmailLead", placeholder="Seu e-mail principal", label_visibility="collapsed")
        
        whats_num = st.text_input(
            "WhatsLead", 
            value="55 ", 
            max_chars=16, 
            placeholder="55 (XX) XXXXX-XXXX", 
            label_visibility="collapsed"
        )
        
        submit = st.form_submit_button("📩 Receber diagnóstico")
        
        if submit:
            if nome_lead and email_lead and whats_num and len(whats_num.strip()) > 5:
                whats_limpo = ''.join(filter(str.isdigit, whats_num))
                if not whats_limpo.startswith("55"):
                    whats_limpo = "55" + whats_limpo

                enviar_lead_bigin(nome_lead, email_lead, whats_limpo, dados['nome'], dados['score'])
                enviar_email_notificacao(nome_lead, email_lead, whats_limpo, dados['nome'], dados['score'])
                
                st.markdown("<p style='text-align: center; color: #2E7D32; font-weight: bold; font-size: 1.1rem; margin-top: 1rem;'>Diagnóstico enviado com sucesso!</p>", unsafe_allow_html=True)
            else:
                st.error("Por favor, preencha todos os campos do formulário corretamente.")

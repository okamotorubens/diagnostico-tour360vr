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

# Estilo CSS Forçado para Corrigir Botões, Rótulos, Centralização e Cores
custom_css = """
<style>
    /* 1. Fundo limpo e remoção de margens */
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
        max-width: 600px !important;
    }

    /* Ocultar elementos nativos do Streamlit */
    header, footer, #MainMenu {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* 2. Títulos e Subtítulos */
    .titulo-principal {
        text-align: center;
        color: #000000 !important;
        font-size: 1.45rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        font-family: 'Arial', sans-serif;
    }
    .instrucao-subtitulo {
        text-align: center;
        color: #333333 !important;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        font-family: 'Arial', sans-serif;
    }

    /* 3. Rótulos dos Campos Visíveis e em Preto */
    label, div[data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        font-family: 'Arial', sans-serif !important;
    }

    /* 4. Estilização dos Inputs */
    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #CCCCCC !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
        padding: 0.55rem 0.8rem !important;
        text-align: center !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #8DC63F !important;
        box-shadow: 0 0 5px rgba(141, 198, 63, 0.4) !important;
    }

    /* 5. FIX DEFINITIVO DOS BOTÕES (Formulários + Busca) */
    div.stButton, div[data-testid="stFormSubmitButton"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin: 0.8rem auto !important;
    }

    /* Botões em Verde Tour360VR com Texto Branco Centralizado */
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #8DC63F !important;
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.7rem 2rem !important;
        cursor: pointer !important;
        box-shadow: 0 4px 10px rgba(141, 198, 63, 0.3) !important;
        margin: 0 auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        max-width: 380px !important;
    }

    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #7BB533 !important;
        color: #FFFFFF !important;
    }

    /* Forçar texto branco no parágrafo interno do botão */
    .stButton > button p, div[data-testid="stFormSubmitButton"] > button p {
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        margin: 0 !important;
        text-align: center !important;
    }

    /* 6. Métrica de Score Centralizada */
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

    /* 7. Alerta Amarelo com Borda */
    .alerta-destaque {
        background-color: #FFFDE7 !important;
        border: 2px solid #FBC02D !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        text-align: center !important;
        color: #5D4037 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin: 1rem auto !important;
        max-width: 500px !important;
    }

    .destaque-formulario {
        text-align: center;
        color: #000000 !important;
        font-size: 1.2rem;
        font-weight: 800;
        margin-top: 1.2rem;
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
# CÁLCULO DE SCORE PRECISO
# ==========================================
def consultar_score_google_rigoroso(nome_empresa):
    """Consulta os dados reais no Google Maps e calcula o Score."""
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

            # Algoritmo de Pontuação
            score = 0
            if details.get("business_status") == "OPERATIONAL": score += 10
            if details.get("rating", 0) >= 4.5 and details.get("user_ratings_total", 0) >= 30: score += 20
            elif details.get("rating", 0) >= 4.0: score += 10
            
            photos = details.get("photos", [])
            if len(photos) >= 10: score += 20
            elif len(photos) > 0: score += 5
                
            if details.get("formatted_phone_number"): score += 10
            if details.get("website"): score += 15
            if details.get("opening_hours"): score += 10
            
            addr = details.get("formatted_address", "")
            if addr and any(char.isdigit() for char in addr): score += 10
            if details.get("types"): score += 5

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
    """Envia a Oportunidade para a coluna 1º Contato do Bigin CRM."""
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

def enviar_emails_diagnostico(nome_lead, email_lead, whatsapp_lead, empresa_consultada, score):
    """Envia e-mail de notificação para a Tour360VR e de confirmação para o Cliente."""
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)

        # 1. E-mail de Notificação Interna (Tour360VR)
        msg_admin = MIMEMultipart()
        msg_admin['From'] = SMTP_USER
        msg_admin['To'] = SMTP_USER
        msg_admin['Subject'] = f"Novo Lead Diagnóstico GMB - {empresa_consultada}"
        
        corpo_admin = f"""
        Novo Lead Capturado no Site:

        Empresa: {empresa_consultada}
        Score Obtido: {score}/100

        Dados do Cliente:
        - Nome: {nome_lead}
        - E-mail: {email_lead}
        - WhatsApp: {whatsapp_lead}
        """
        msg_admin.attach(MIMEText(corpo_admin, 'plain'))
        server.send_message(msg_admin)

        # 2. E-mail de Resposta ao Cliente
        msg_cliente = MIMEMultipart()
        msg_cliente['From'] = SMTP_USER
        msg_cliente['To'] = email_lead
        msg_cliente['Subject'] = f"Diagnóstico de Perfil no Google - {empresa_consultada}"
        
        corpo_cliente = f"""
        Olá, {nome_lead}!

        Recebemos a sua solicitação de diagnóstico para a empresa "{empresa_consultada}".

        Pontuação de Otimização no Google Maps: {score}/100.

        O nosso especialista em posicionamento digital da Tour360VR analisará os detalhes do seu perfil e entrará em contacto através do WhatsApp ({whatsapp_lead}) para apresentar o relatório completo.

        Atenciosamente,
        Rubens Okamoto | Tour360VR
        www.tour360vr.com.br
        """
        msg_cliente.attach(MIMEText(corpo_cliente, 'plain'))
        server.send_message(msg_cliente)

        server.quit()
        return True
    except Exception as e:
        print(f"Erro no Envio SMTP: {e}")
        return False

# ==========================================
# INTERFACE DO USUÁRIO
# ==========================================
st.markdown('<div class="titulo-principal">🔍 Faça um diagnóstico do perfil da sua empresa no Google.</div>', unsafe_allow_html=True)
st.markdown('<div class="instrucao-subtitulo">Digite o Nome Comercial exato da sua empresa seguido da Cidade e Estado.</div>', unsafe_allow_html=True)

nome_empresa = st.text_input("BuscaInput", placeholder="Ex: Tour360VR Ribeirão Preto SP", label_visibility="collapsed")

if st.button("🔍 Analisar perfil"):
    if nome_empresa:
        with st.spinner("Analisando perfil no Google Maps..."):
            res = consultar_score_google_rigoroso(nome_empresa)
            if res["sucesso"]:
                st.session_state["resultado_busca"] = res
            else:
                st.error("❌ Empresa não encontrada. Tente incluir a cidade ou verificar a grafia exata cadastrada no Google.")

# Exibição dos Resultados Centralizados
if "resultado_busca" in st.session_state:
    dados = st.session_state["resultado_busca"]
    
    st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
    
    st.markdown(f'<p style="text-align: center; color: #000000; font-size: 1.15rem; font-weight: bold; margin-bottom: 0.2rem;">Empresa Localizada: {dados["nome"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #666666; font-size: 0.9rem; margin-bottom: 0.6rem;">📍 {dados["endereco"]}</p>', unsafe_allow_html=True)
    
    st.metric(label="Pontuação Geral de Otimização (Score)", value=f"{dados['score']} / 100")
    
    st.markdown("""
    <div class="alerta-destaque">
        ⚠️ Identificamos oportunidades de melhoria que podem estar reduzindo a visibilidade do seu negócio para novos clientes.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="destaque-formulario">Preencha os dados abaixo e receba a análise completa</div>', unsafe_allow_html=True)
    
    # Formulário sem st.form para evitar sobreposição de estilos nativos do Streamlit
    nome_lead = st.text_input("Seu Nome Completo:", placeholder="Digite o seu nome completo")
    email_lead = st.text_input("Seu E-mail Principal:", placeholder="exemplo@email.com")
    whats_num = st.text_input("Seu WhatsApp (com DDD):", value="55 ", placeholder="5516991332121")

    if st.button("📩 Receber diagnóstico"):
        if nome_lead and email_lead and whats_num and len(whats_num.strip()) > 5:
            whats_limpo = ''.join(filter(str.isdigit, whats_num))
            if not whats_limpo.startswith("55"):
                whats_limpo = "55" + whats_limpo

            # Disparos de integração
            enviar_lead_bigin(nome_lead, email_lead, whats_limpo, dados['nome'], dados['score'])
            enviar_emails_diagnostico(nome_lead, email_lead, whats_limpo, dados['nome'], dados['score'])
            
            st.markdown("<p style='text-align: center; color: #2E7D32; font-weight: bold; font-size: 1.15rem; margin-top: 1rem;'>Diagnóstico enviado com sucesso!</p>", unsafe_allow_html=True)
        else:
            st.error("Por favor, preencha todos os campos do formulário corretamente.")

import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st

# ==========================================
# CONFIGURAÇÕES E CREDENCIAIS
# ==========================================
# Substitua pela sua Chave de API do Google Cloud que configuramos
GOOGLE_API_KEY = "SUA_CHAVE_GOOGLE_CLOUD_AQUI"

# Credenciais do Bigin CRM (Zoho) geradas na Etapa 1
BIGIN_CLIENT_ID = "1000.COI8SBR9O0RCMGCL7WKEYUJMBZCR8X"
BIGIN_CLIENT_SECRET = "c60642fb374cbad9753c456d8713b6349417187345"

# Configurações de E-mail (SMTP Locaweb)
SMTP_SERVER = "smtp.tour360vr.com.br"
SMTP_PORT = 587
SMTP_USER = "contato@tour360vr.com.br"
SMTP_PASS = "SUA_SENHA_EMAIL_AQUI"

# ==========================================
# FUNÇÃO 1: CONSULTA DE SCORE NO GOOGLE
# ==========================================
def consultar_score_google(nome_empresa):
    """Consulta a empresa via Google Places API e calcula o Score de 0 a 100."""
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={nome_empresa}&key={GOOGLE_API_KEY}"
    response = requests.get(url).json()

    if response.get("status") == "OK" and response.get("results"):
        place = response["results"][0]
        
        # Algoritmo simplificado de cálculo de Score para a Isca
        score = 0
        if place.get("rating", 0) >= 4.0: score += 25
        if place.get("user_ratings_total", 0) > 20: score += 25
        if place.get("business_status") == "OPERATIONAL": score += 20
        if place.get("photos"): score += 30  # Presença de imagens
        
        return {
            "sucesso": True,
            "place_id": place.get("place_id"),
            "nome": place.get("name"),
            "endereco": place.get("formatted_address"),
            "score": score
        }
    return {"sucesso": False, "mensagem": "Empresa não encontrada no Google."}

# ==========================================
# FUNÇÃO 2: ENVIAR LEAD PARA O BIGIN CRM
# ==========================================
def enviar_lead_bigin(nome_lead, email_lead, whatsapp_lead, empresa_consultada, score):
    """Cria a Oportunidade no Bigin CRM na coluna 1º Contato."""
    try:
        # 1. Obter Access Token usando as chaves Client ID e Client Secret
        url_token = f"https://accounts.zoho.com/oauth/v2/token?client_id={BIGIN_CLIENT_ID}&client_secret={BIGIN_CLIENT_SECRET}&grant_type=client_credentials&scope=ZohoBigin.modules.ALL"
        res_token = requests.post(url_token).json()
        access_token = res_token.get("access_token")

        if not access_token:
            return False

        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }

        # 2. Criar Oportunidade (Serviços) no Bigin
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
    except Exception as e:
        print(f"Erro ao enviar para o Bigin: {e}")
        return False

# ==========================================
# FUNÇÃO 3: DISPARO DE E-MAIL COM O PDF
# ==========================================
def enviar_email_pdf(destinatario, nome_lead, empresa_consultada, score, caminho_pdf):
    """Envia o e-mail para o cliente com o relatório em PDF anexo."""
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = destinatario
    msg['Subject'] = f"Diagnóstico de Perfil no Google - {empresa_consultada}"

    corpo = f"""
    Olá, {nome_lead}!

    Obrigado por consultar o desempenho do seu Perfil de Empresa no Google através do Tour360vr.

    Empresa Consultada: {empresa_consultada}
    Pontuação Geral de Otimização: {score}/100

    Em anexo, você encontrará o resumo da sua análise com os principais pontos de atenção.

    Atenciosamente,
    Rubens Okamoto | Tour360vr
    """
    msg.attach(MIMEText(corpo, 'plain'))

    # Anexo PDF (se gerado)
    if os.path.exists(caminho_pdf):
        with open(caminho_pdf, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="Diagnostico_{empresa_consultada}.pdf"')
            msg.attach(part)

    # Envio SMTP
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    server.send_message(msg)
    server.quit()

# ==========================================
# INTERFACE STREAMLIT (PÚBLICA)
# ==========================================
st.set_page_config(page_title="Diagnóstico Gratuito GMB - Tour360vr", page_icon="🔍")
st.title("🔍 Diagnóstico de Perfil no Google")
st.write("Digite o nome do seu estabelecimento abaixo para calcular a nota de otimização no Google.")

# Passo 1: Busca da Empresa
nome_empresa = st.text_input("Nome da empresa e cidade:", placeholder="Ex: Clínica Vinicius Ribeirão Preto")

if st.button("Analisar Ficha"):
    if nome_empresa:
        res = consultar_score_google(nome_empresa)
        if res["sucesso"]:
            st.session_state["resultado_busca"] = res
        else:
            st.error("Empresa não encontrada. Verifique a digitação e tente novamente.")

# Passo 2: Exibição do Score Instantâneo
if "resultado_busca" in st.session_state:
    dados = st.session_state["resultado_busca"]
    
    st.markdown("---")
    st.subheader(f"Empresa: {dados['nome']}")
    st.metric(label="Pontuação de Otimização (Score)", value=f"{dados['score']} / 100")
    
    st.warning("⚠️ Identificamos oportunidades de melhoria na sua ficha que podem estar a afetar o seu posicionamento no Google Maps.")

    # Passo 3: Formulário de Captura do Lead
    st.markdown("### 📄 Desbloquear Relatório Detalhado")
    st.write("Preencha os dados abaixo para receber a análise executiva no seu e-mail e WhatsApp:")
    
    with st.form("form_lead"):
        nome_lead = st.text_input("Seu Nome Completo:")
        email_lead = st.text_input("Seu E-mail Principal:")
        whats_lead = st.text_input("WhatsApp (com DDD):")
        
        submit = st.form_submit_button("Receber Relatório em PDF")
        
        if submit:
            if nome_lead and email_lead and whats_lead:
                # 1. Enviar para o Bigin CRM
                enviar_lead_bigin(nome_lead, email_lead, whats_lead, dados['nome'], dados['score'])
                
                st.success("✅ Relatório enviado com sucesso! Verifique o seu e-mail e WhatsApp.")
            else:
                st.error("Por favor, preencha todos os campos do formulário.")

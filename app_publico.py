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
    page_title="Diagnóstico do Perfil no Google - Tour360VR", 
    page_icon="🔍",
    layout="centered"
)

# Estilo CSS Personalizado
custom_css = """
<style>
    /* Fundo totalmente branco */
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Ajuste de margens do container */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 650px !important;
    }

    /* Esconder elementos nativos do Streamlit */
    header, footer, #MainMenu {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* Título Direto e Compacto */
    .titulo-compacto {
        text-align: center;
        color: #000000 !important;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 1.2rem;
        font-family: 'Arial', sans-serif;
    }

    /* Instruções Destacadas e Centralizadas */
    .texto-instrucao-destaque {
        text-align: center;
        color: #000000 !important;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.3rem;
        font-family: 'Arial', sans-serif;
    }
    .texto-exemplo {
        text-align: center;
        color: #555555 !important;
        font-size: 1rem;
        margin-bottom: 1.5rem;
        font-family: 'Arial', sans-serif;
    }

    /* Centralizar Resultados da Busca */
    .resultado-container {
        text-align: center !important;
    }

    /* Estilização dos Labels (Garantir cor preta) */
    label, p, span, h1, h2, h3, h4 {
        color: #000000 !important;
        font-family: 'Arial', sans-serif !important;
    }

    /* Forçar todos os campos de texto a ficarem centralizados e compactos */
    .stTextInput > div {
        max-width: 450px !important;
        margin: 0 auto !important;
    }
    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #CCCCCC !important;
        border-radius: 8px !important;
        font-size: 1.05rem !important;
        padding: 0.65rem 1rem !important;
        text-align: center !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #8DC63F !important;
        box-shadow: 0 0 6px rgba(141, 198, 63, 0.4) !important;
    }

    /* Ajuste para Placeholder dentro dos campos */
    ::placeholder {
        color: #888888 !important;
        opacity: 1 !important;
    }

    /* Centralização de Botões */
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin-top: 1rem !important;
    }

    /* Botão Verde Padrão Tour360VR (#8DC63F) */
    .stButton > button {
        background-color: #8DC63F !important;
        color: #FFFFFF !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.85rem 3rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(141, 198, 63, 0.3) !important;
        margin: 0 auto !important;
        display: block !important;
        width: 100% !important;
        max-width: 450px !important;
    }
    .stButton > button:hover {
        background-color: #7BB533 !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
    }
    .stButton > button p {
        color: #FFFFFF !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }

    /* Métrica de Score Centralizada */
    [data-testid="stMetricValue"] {
        color: #8DC63F !important;
        font-size: 3.5rem !important;
        font-weight: bold !important;
        text-align: center !important;
    }
    [data-testid="stMetric"] {
        display: flex !important;
        justify-content: center !important;
    }

    /* Destaque para o Título do Relatório PDF */
    .destaque-pdf {
        text-align: center;
        color: #000000 !important;
        font-size: 1.4rem;
        font-weight: 800;
        margin-top: 2rem;
        margin-bottom: 0.4rem;
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

# ==========================================
# CÁLCULO DE SCORE DE 9 CRITÉRIOS (SISTEMA PRIVADO)
# ==========================================
def consultar_score_google_completo(nome_empresa):
    """Realiza a busca e calcula o Score de Otimização analisando os 9 critérios completos."""
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={requests.utils.quote(nome_empresa)}&key={GOOGLE_API_KEY}"
    headers = {"Referer": "https://www.tour360vr.com.br/"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10).json()
        results = response.get("results", [])
        
        if results:
            place = results[0]
            place_id = place.get("place_id")
            
            # Buscar Detalhes Completos (Place Details) para os 9 critérios
            url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,user_ratings_total,business_status,photos,formatted_phone_number,website,types,formatted_address&key={GOOGLE_API_KEY}"
            res_details = requests.get(url_details, headers=headers, timeout=10).json()
            details = res_details.get("result", place)

            # Algoritmo de 9 Itens
            score = 0
            # 1. Status Operacional
            if details.get("business_status") == "OPERATIONAL": score += 10
            # 2. Nota Média (>= 4.0)
            if details.get("rating", 0) >= 4.0: score += 15
            # 3. Quantidade de Avaliações (> 20)
            if details.get("user_ratings_total", 0) >= 20: score += 15
            # 4. Fotos Presentes
            if details.get("photos"): score += 15
            # 5. Telefone Cadastrado
            if details.get("formatted_phone_number"): score += 10
            # 6. Website Vinculado
            if details.get("website"): score += 10
            # 7. Endereço Completo
            if details.get("formatted_address"): score += 10
            # 8. Categoria Definida
            if details.get("types"): score += 10
            # 9. Atividade Recente / Presença
            if details.get("user_ratings_total", 0) >= 50: score += 5

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
st.markdown('<div class="titulo-compacto">🔍 Faça um diagnóstico do perfil da sua empresa no Google.</div>', unsafe_allow_html=True)

st.markdown('<div class="texto-instrucao-destaque">Digite o Nome Comercial exato da sua empresa seguido da Cidade e Estado.</div>', unsafe_allow_html=True)
st.markdown('<div class="texto-exemplo">Sua Empresa Sua cidade Seu Estado</div>', unsafe_allow_html=True)

# Campo de busca compacto com Placeholder explicativo
nome_empresa = st.text_input("BuscaEmpresa", placeholder="Nome da empresa + cidade + estado", label_visibility="collapsed")

if st.button("🔍 Analisar perfil"):
    if nome_empresa:
        with st.spinner("Analisando os 9 critérios no Google Maps..."):
            res = consultar_score_google_completo(nome_empresa)
            if res["sucesso"]:
                st.session_state["resultado_busca"] = res
            else:
                st.error("❌ Empresa não encontrada. Tente incluir a cidade ou verificar a grafia exata cadastrada no Google.")

# Exibição dos Resultados Centralizados
if "resultado_busca" in st.session_state:
    dados = st.session_state["resultado_busca"]
    
    st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align: center; color: #000000;'>Empresa Localizada: {dados['nome']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #666666;'>📍 Endereço: {dados['endereco']}</p>", unsafe_allow_html=True)
    
    st.metric(label="Pontuação Geral de Otimização (Score)", value=f"{dados['score']} / 100")
    
    st.warning("⚠️ Identificamos oportunidades de melhoria que podem estar reduzindo a visibilidade do seu negócio para novos clientes.")

    # Seção do Formulário de Lead com Espaço Adicional
    st.markdown('<div class="destaque-pdf">📄 Desbloquear Relatório Detalhado em PDF</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #000000; margin-bottom: 1.5rem;">Preencha os seus dados abaixo para receber a análise completa:</p>', unsafe_allow_html=True)
    
    with st.form("form_lead"):
        nome_lead = st.text_input("NomeLead", placeholder="Seu nome", label_visibility="collapsed")
        email_lead = st.text_input("EmailLead", placeholder="Seu e-mail", label_visibility="collapsed")
        
        # Campo de WhatsApp com prefixo 55 pré-preenchido
        whats_num = st.text_input("WhatsLead", placeholder="55 (DDD + celular)", max_chars=13, label_visibility="collapsed")
        
        submit = st.form_submit_button("📩 Receber diagnóstico")
        
        if submit:
            if nome_lead and email_lead and whats_num:
                # Trata o WhatsApp digitado garantindo o prefixo 55
                whats_limpo = ''.join(filter(str.isdigit, whats_num))
                if not whats_limpo.startswith("55"):
                    whats_limpo = "55" + whats_limpo

                enviar_lead_bigin(nome_lead, email_lead, whats_limpo, dados['nome'], dados['score'])
                st.success("✅ Diagnóstico enviado com sucesso! Entraremos em contacto pelo WhatsApp.")
            else:
                st.error("Por favor, preencha todos os campos do formulário.")

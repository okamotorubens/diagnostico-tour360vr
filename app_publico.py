import os
import re
import requests
import smtplib
import tempfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st

# Importação das bibliotecas de PDF (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# ==========================================
# CONFIGURAÇÃO DE TEMA E VISUAL PERSONALIZADO
# ==========================================
st.set_page_config(
    page_title="Análise da Empresa no Google - Tour360VR", 
    page_icon="🔍",
    layout="centered"
)

# Estilo CSS Global com Ocultação Absoluta do Rodapé Nativo
custom_css = """
<style>
    /* Ocultar rodapé e barras nativas do Streamlit */
    footer, .stApp footer, [data-testid="stFooter"], header, #MainMenu, [data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
    }

    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
        max-width: 700px !important;
    }

    /* Títulos Principais */
    .titulo-uma-linha {
        text-align: center;
        color: #000000 !important;
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        font-family: 'Arial', sans-serif;
        white-space: nowrap;
    }
    .instrucao-subtitulo {
        text-align: center;
        color: #333333 !important;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        font-family: 'Arial', sans-serif;
    }

    /* Rótulos de Campos Centralizados */
    .rotulo-campo-centralizado {
        text-align: center !important;
        color: #000000 !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        font-family: 'Arial', sans-serif !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.1rem !important;
    }

    .subtexto-label {
        font-size: 0.8rem !important;
        color: #666666 !important;
        font-weight: normal !important;
        margin-bottom: 0.3rem !important;
    }

    /* Inputs Claros e Centralizados */
    .stTextInput {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }
    .stTextInput label {
        display: none !important;
    }
    .stTextInput > div {
        max-width: 480px !important;
        width: 100% !important;
        margin: 0 auto !important;
    }
    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #CCCCCC !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
        padding: 0.55rem 0.8rem !important;
        text-align: center !important;
    }

    /* Centralização dos Botões */
    div[data-testid="stButton"], div.stButton {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin: 0.8rem auto !important;
        text-align: center !important;
    }

    .stButton > button {
        background-color: #8DC63F !important;
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.65rem 2rem !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(141, 198, 63, 0.3) !important;
        margin: 0 auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        max-width: 480px !important;
    }

    .stButton > button:hover {
        background-color: #7BB533 !important;
        color: #FFFFFF !important;
    }

    .stButton > button p {
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        margin: 0 !important;
        text-align: center !important;
    }

    /* Título do Formulário */
    .destaque-formulario-linha {
        text-align: center;
        color: #000000 !important;
        font-size: 1.25rem;
        font-weight: 800;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
        font-family: 'Arial', sans-serif;
        white-space: nowrap;
    }

    /* Card de Sucesso */
    .card-sucesso-destaque {
        background-color: #E8F5E9 !important;
        border: 2px solid #2E7D32 !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        text-align: center !important;
        color: #1B5E20 !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        margin: 0.8rem auto !important;
        max-width: 480px !important;
        box-shadow: 0 2px 8px rgba(46, 125, 50, 0.15) !important;
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
# COR DINÂMICA DO SCORE
# ==========================================
def obter_cor_score(score):
    if score <= 40:
        return "#D32F2F"  # Vermelho Alerta
    elif score <= 70:
        return "#F57C00"  # Laranja / Amarelo Atenção
    else:
        return "#8DC63F"  # Verde Otimizado

# ==========================================
# CÁLCULO DE SCORE RIGOROSO (SINCRONIZADO)
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
            crit_det = []

            if details.get("business_status") == "OPERATIONAL": 
                score += 10
                crit_det.append("Status Operacional: Ativo")

            rating = details.get("rating", 0)
            reviews = details.get("user_ratings_total", 0)
            if rating >= 4.7 and reviews >= 100:
                score += 20
                crit_det.append(f"Avaliações: Excelente ({rating} / {reviews} avaliações)")
            elif rating >= 4.0 and reviews >= 15:
                score += 10
                crit_det.append(f"Avaliações: Moderadas ({rating} / {reviews} avaliações)")

            photos = details.get("photos", [])
            if len(photos) >= 30:
                score += 20
                crit_det.append("Galeria de Fotos: Completa")
            elif len(photos) >= 5:
                score += 10
                crit_det.append("Galeria de Fotos: Parcial")

            if details.get("formatted_phone_number"):
                score += 10
                crit_det.append("Telefone: Cadastrado")

            website = details.get("website", "")
            if website and not any(x in website for x in ["facebook", "instagram", "site.google"]):
                score += 15
                crit_det.append("Website: Próprio Vinculado")

            if details.get("opening_hours"):
                score += 10
                crit_det.append("Horários: Configurados")

            addr = details.get("formatted_address", "")
            if addr and any(char.isdigit() for char in addr):
                score += 10
                crit_det.append("Endereço: Completo com número")

            if details.get("types"):
                score += 5
                crit_det.append("Categoria: Definida")

            return {
                "sucesso": True,
                "place_id": place_id,
                "nome": details.get("name"),
                "endereco": details.get("formatted_address", "Endereço registrado no Google Maps"),
                "score": min(score, 100),
                "criterios": crit_det
            }
    except Exception as e:
        print(f"Erro na consulta Google: {e}")
        
    return {"sucesso": False, "mensagem": "Empresa não encontrada no Google."}

# ==========================================
# GERADOR DE PDF GRAVADO EM DISCO TEMPORÁRIO
# ==========================================
def gerar_pdf_diagnostico_arquivo(empresa_nome, endereco, score, criterios):
    try:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"Diagnostico_{empresa_nome.replace(' ', '_')}.pdf")
        
        doc = SimpleDocTemplate(file_path, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=35, bottomMargin=35)
        styles = getSampleStyleSheet()
        
        style_titulo = ParagraphStyle('TituloPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#1565C0'))
        style_sub = ParagraphStyle('SubPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#222222'))
        style_texto = ParagraphStyle('TextoPDF', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#444444'))
        
        elements = []
        elements.append(Paragraph("TOUR360VR • RELATÓRIO DE DIAGNÓSTICO DIGITAL", style_titulo))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Empresa Analisada: {empresa_nome}", style_sub))
        elements.append(Paragraph(f"Endereço: {endereco}", style_texto))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph(f"PONTUAÇÃO GERAL DE OTIMIZAÇÃO: {score} / 100", ParagraphStyle('ScorePDF', parent=style_titulo, fontSize=16, textColor=colors.HexColor('#1565C0'))))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("Critérios Analisados no Perfil do Google Maps:", style_sub))
        elements.append(Spacer(1, 8))
        
        tabela_dados = [["Critério / Requisito", "Status de Otimização"]]
        for item in criterios:
            partes = item.split(":")
            c1 = partes[0] if len(partes) > 0 else item
            c2 = partes[1] if len(partes) > 1 else "OK"
            tabela_dados.append([c1, c2])
            
        t = Table(tabela_dados, colWidths=[240, 240])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Próximos Passos Recomendados:", style_sub))
        elements.append(Paragraph("Para atingir os 100 pontos e garantir prioridade nas buscas locais do Google Maps, recomenda-se a inclusão de um Tour Virtual 360° homologado e atualização completa da galeria visual e categorias do perfil.", style_texto))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Tour360VR • Imagem e Presença Digital<br>www.tour360vr.com.br | contato@tour360vr.com.br", style_texto))
        
        doc.build(elements)
        return file_path
    except Exception as e:
        print(f"Erro ao gerar PDF em disco: {e}")
        return None

# ==========================================
# ENVIO DE LEAD PARA O BIGIN CRM
# ==========================================
def enviar_lead_bigin(nome_lead, email_lead, whatsapp_lead, empresa_consultada, score):
    try:
        url_token = f"https://accounts.zoho.com/oauth/v2/token?client_id={BIGIN_CLIENT_ID}&client_secret={BIGIN_CLIENT_SECRET}&grant_type=client_credentials&scope=ZohoBigin.modules.ALL"
        res_token = requests.post(url_token, timeout=8).json()
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
        res_deal = requests.post(url_deal, json=payload, headers=headers, timeout=8)
        return res_deal.status_code in [200, 201]
    except Exception as e:
        print(f"Erro Bigin: {e}")
        return False

# ==========================================
# DISPARO DE E-MAILS COM ANEXO FÍSICO DO PDF
# ==========================================
def enviar_emails_diagnostico_completo(nome_lead, email_lead, whatsapp_lead, dados_busca):
    try:
        empresa_nome = dados_busca['nome']
        score = dados_busca['score']
        endereco = dados_busca['endereco']
        criterios = dados_busca.get('criterios', [])
        cor_score_hex = obter_cor_score(score)

        pdf_file_path = gerar_pdf_diagnostico_arquivo(empresa_nome, endereco, score, criterios)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)

        # 1. E-mail Administrativo
        msg_admin = MIMEMultipart('mixed')
        msg_admin['From'] = SMTP_USER
        msg_admin['To'] = SMTP_USER
        msg_admin['Subject'] = f"🚀 NOVO LEAD: {empresa_nome} (Score: {score}/100)"
        
        corpo_admin_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; background-color: #ffffff; padding: 25px; border-radius: 10px; border-top: 5px solid #1E88E5; margin: 0 auto;">
                <h2 style="color: #333333; margin-top: 0;">Novo Lead Capturado no Site!</h2>
                <hr style="border: 0; border-top: 1px solid #eeeeee;">
                
                <h3 style="color: #1565C0; margin-bottom: 5px;">Empresa Consultada:</h3>
                <p style="font-size: 1.1rem; font-weight: bold; margin-top: 0; color: #1E88E5;">{empresa_nome}</p>
                
                <p><b>Pontuação Obtida:</b> <span style="font-size: 1.25rem; color: {cor_score_hex}; font-weight: bold;">{score} / 100</span></p>
                
                <div style="background-color: #F8F9FA; padding: 15px; border-radius: 8px; border-left: 4px solid #1E88E5; margin: 15px 0;">
                    <h4 style="margin-top: 0; color: #555555;">Dados do Cliente:</h4>
                    <p style="margin: 5px 0;"><b>Nome:</b> {nome_lead}</p>
                    <p style="margin: 5px 0;"><b>E-mail:</b> <a href="mailto:{email_lead}">{email_lead}</a></p>
                    <p style="margin: 5px 0;"><b>WhatsApp:</b> <a href="https://wa.me/{whatsapp_lead}" target="_blank" style="color: #1E88E5; font-weight: bold;">+{whatsapp_lead}</a></p>
                </div>
                
                <p style="font-size: 0.85rem; color: #888888; text-align: center;">Tour360VR • Sistema Automático de Captura</p>
            </div>
        </body>
        </html>
        """
        msg_admin.attach(MIMEText(corpo_admin_html, 'html'))
        
        if pdf_file_path and os.path.exists(pdf_file_path):
            with open(pdf_file_path, 'rb') as f:
                p_admin = MIMEBase('application', 'pdf')
                p_admin.set_payload(f.read())
                encoders.encode_base64(p_admin)
                p_admin.add_header('Content-Disposition', 'attachment', filename=f"Diagnostico_{empresa_nome.replace(' ', '_')}.pdf")
                msg_admin.attach(p_admin)

        server.send_message(msg_admin)

        # 2. E-mail Cliente
        msg_cliente = MIMEMultipart('mixed')
        msg_cliente['From'] = SMTP_USER
        msg_cliente['To'] = email_lead
        msg_cliente['Subject'] = f"Diagnóstico de Perfil no Google - {empresa_nome}"
        
        corpo_html_cliente = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6;">
            <p>Olá, {nome_lead}!</p>
            <p>Ficamos muito felizes pelo seu interesse em saber como está a ficha Google da sua empresa.</p>
            <p>Recebemos a solicitação de diagnóstico para <b>{empresa_nome}</b>.</p>
            <p>Pontuação de otimização no Google: <b style="font-size: 1.25rem; color: {cor_score_hex};">{score}/100</b>.</p>
            <p>O nosso especialista em posicionamento digital analisará os detalhes do seu perfil e entrará em contato através do WhatsApp (5516991332121) para apresentar o relatório completo.</p>
            <p>Anexamos a este e-mail o seu relatório preliminar em PDF.</p>
            <br>
            <p>Atenciosamente,<br><b>Rubens Okamoto | Tour360VR</b></p>
        </body>
        </html>
        """
        msg_cliente.attach(MIMEText(corpo_html_cliente, 'html'))

        if pdf_file_path and os.path.exists(pdf_file_path):
            with open(pdf_file_path, 'rb') as f:
                p_cliente = MIMEBase('application', 'pdf')
                p_cliente.set_payload(f.read())
                encoders.encode_base64(p_cliente)
                p_cliente.add_header('Content-Disposition', 'attachment', filename=f"Diagnostico_GMB_{empresa_nome.replace(' ', '_')}.pdf")
                msg_cliente.attach(p_cliente)

        server.send_message(msg_cliente)
        server.quit()
        
        if pdf_file_path and os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)

        return True
    except Exception as e:
        print(f"Erro Envio Email: {e}")
        return False

# ==========================================
# INTERFACE DO USUÁRIO
# ==========================================
st.markdown('<div class="titulo-uma-linha">🔍 Faça uma análise da sua empresa no Google</div>', unsafe_allow_html=True)
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

# Exibição do Resultado
if "resultado_busca" in st.session_state:
    dados = st.session_state["resultado_busca"]
    cor_nota = obter_cor_score(dados["score"])
    
    # CARD EM HTML PURO COM FUNDO CINZA/AZULADO INDEPENDENTE DO STREAMLIT
    html_card_resultado = f"""
    <div style="background-color: #F0F4F8 !important; border: 1px solid #D0D7DE !important; border-radius: 12px !important; padding: 20px !important; margin: 1.2rem auto !important; max-width: 600px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.04) !important;">
        <div style="text-align: center; color: #000000; font-size: 1.3rem; font-weight: 800; margin-bottom: 0.1rem;">Empresa Localizada: {dados["nome"]}</div>
        <p style="text-align: center; color: #666666; font-size: 0.95rem; margin-bottom: 0.4rem;">📍 {dados["endereco"]}</p>
        <p style="text-align: center; font-weight: 700; font-size: 1.1rem; margin-top: 0.6rem; margin-bottom: 0;">Pontuação Geral de Otimização</p>
        <div style="text-align: center; font-size: 3.2rem; font-weight: 900; line-height: 1; margin: 0.3rem 0 0.8rem 0; color: {cor_nota} !important;">{dados["score"]} / 100</div>
        <div style="background-color: #FFFDE7; border: 2px solid #FBC02D; border-radius: 8px; padding: 10px 14px; text-align: center; color: #5D4037; font-size: 0.95rem; font-weight: 600; margin: 0.8rem auto 0 auto;">
            ⚠️ Identificamos oportunidades de melhoria que podem estar reduzindo a visibilidade do seu negócio para novos clientes.
        </div>
    </div>
    """
    st.markdown(html_card_resultado, unsafe_allow_html=True)

    # Formulário de Captura
    st.markdown('<div class="destaque-formulario-linha">📋 Preencha os dados abaixo e receba a análise completa</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="rotulo-campo-centralizado">Nome:</div>', unsafe_allow_html=True)
    nome_lead = st.text_input("NomeInput", placeholder="Digite o seu nome completo", label_visibility="collapsed")
    
    st.markdown('<div class="rotulo-campo-centralizado">E-mail:</div>', unsafe_allow_html=True)
    email_lead = st.text_input("EmailInput", placeholder="exemplo@email.com", label_visibility="collapsed")
    
    st.markdown('<div class="rotulo-campo-centralizado">WhatsApp</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtexto-label" style="text-align: center;">(DDD + 9 dígitos - Apenas números)</div>', unsafe_allow_html=True)
    
    raw_whats = st.text_input("WhatsInput", max_chars=11, placeholder="16991332121", label_visibility="collapsed")

    if st.button("📩 Receber diagnóstico"):
        # Validação estrita: verifica se tem APENAS números e exatamente 11 dígitos
        apenas_numeros = re.sub(r'\D', '', raw_whats)
        
        if not nome_lead or len(nome_lead.strip()) < 2:
            st.error("Por favor, informe seu nome completo.")
        elif not email_lead or "@" not in email_lead:
            st.error("Por favor, informe um endereço de e-mail válido.")
        elif len(raw_whats) != len(apenas_numeros) or len(apenas_numeros) != 11:
            st.error("❌ O campo WhatsApp aceita APENAS NÚMEROS e deve ter exatamente 11 dígitos (DDD + Número, ex: 16991332121).")
        else:
            whats_completo = "55" + apenas_numeros

            # 1. Tenta enviar para o Bigin CRM
            enviar_lead_bigin(nome_lead, email_lead, whats_completo, dados['nome'], dados['score'])
            
            # 2. Envia e-mails com anexo do PDF
            com_sucesso = enviar_emails_diagnostico_completo(nome_lead, email_lead, whats_completo, dados)
            
            if com_sucesso:
                st.markdown("""
                <div class="card-sucesso-destaque">
                    ✅ Diagnóstico enviado com sucesso! Verifique sua caixa de entrada e spam.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Ocorreu uma falha ao disparar o e-mail. Tente novamente em instantes.")

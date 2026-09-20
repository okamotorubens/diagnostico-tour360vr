import os
import re
import io
import requests
import smtplib
import streamlit as st

# ReportLab para geração e diagramação do PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ==========================================
# CONFIGURAÇÃO DE PÁGINA E CSS STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Análise de Perfil no Google - Tour360VR",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS para Container Compacto Cinza/Azulado e Inputs 100% Brancos
custom_css = """
<style>
    html, body, [data-testid="stAppViewContainer"], .main {
        overflow-x: hidden !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 680px !important;
    }

    footer, .stApp footer, [data-testid="stFooter"], header, #MainMenu, [data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
    }

    .card-resultado-compacto {
        background-color: #F0F4F8 !important;
        border: 1px solid #D0D7DE !important;
        border-radius: 10px !important;
        padding: 16px 20px !important;
        margin: 0.8rem auto !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }

    .titulo-principal {
        text-align: center;
        color: #111111 !important;
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        font-family: 'Arial', sans-serif;
    }
    .instrucao-subtitulo {
        text-align: center;
        color: #444444 !important;
        font-size: 0.92rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        font-family: 'Arial', sans-serif;
    }

    div[data-baseweb="input"], 
    div[data-baseweb="input"] > div, 
    div[data-baseweb="base-input"],
    .stTextInput > div,
    .stTextInput > div > div,
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-color: #CCCCCC !important;
    }

    .stTextInput input {
        border: 1px solid #CCCCCC !important;
        border-radius: 6px !important;
        font-size: 0.98rem !important;
        padding: 0.55rem 0.8rem !important;
        text-align: center !important;
        color: #000000 !important;
    }

    .stTextInput input:focus {
        border-color: #8DC63F !important;
        box-shadow: 0 0 4px rgba(141, 198, 63, 0.4) !important;
    }

    input:-webkit-autofill,
    input:-webkit-autofill:hover, 
    input:-webkit-autofill:focus, 
    input:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 30px #FFFFFF inset !important;
        -webkit-text-fill-color: #000000 !important;
    }

    .rotulo-campo {
        text-align: center !important;
        color: #111111 !important;
        font-size: 0.92rem !important;
        font-weight: 700 !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.1rem !important;
    }
    .subtexto-label {
        font-size: 0.78rem !important;
        color: #666666 !important;
        text-align: center !important;
        margin-bottom: 0.2rem !important;
    }

    div[data-testid="stButton"], div.stButton {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin: 0.6rem auto !important;
    }
    .stButton > button {
        background-color: #8DC63F !important;
        color: #FFFFFF !important;
        font-size: 1.05rem !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        cursor: pointer !important;
        width: 100% !important;
        max-width: 480px !important;
    }
    .stButton > button:hover {
        background-color: #7BB533 !important;
    }
    .stButton > button p {
        color: #FFFFFF !important;
        margin: 0 !important;
        font-weight: bold !important;
    }

    .card-sucesso-destaque {
        background-color: #E8F5E9 !important;
        border: 1px solid #2E7D32 !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        text-align: center !important;
        color: #1B5E20 !important;
        font-size: 0.98rem !important;
        font-weight: 700 !important;
        margin: 0.8rem auto !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# CREDENCIAIS
# ==========================================
GOOGLE_API_KEY = "AIzaSyA8ul_9QICNyqxrHgT-CURIZmd1sikHn5U"

BIGIN_CLIENT_ID = "1000.COI8SBR9O0RCMGCL7WKEYUJMBZCR8X"
BIGIN_CLIENT_SECRET = "c60642fb374cbad9753c456d8713b6349417187345"

SMTP_SERVER = "smtp.tour360vr.com.br"
SMTP_PORT = 587
SMTP_USER = "contato@tour360vr.com.br"
SMTP_PASS = "Kakaroto@2026"

def obter_cor_score(score):
    if score <= 40:
        return "#D32F2F"
    elif score <= 70:
        return "#F57C00"
    else:
        return "#8DC63F"

# ==========================================
# CÁLCULO DE SCORE RIGOROSO E REALISTA
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

            # Algoritmo de auditoria rigorosa
            score = 0
            criterios_eval = []

            # 1. Status Operacional (+10)
            if details.get("business_status") == "OPERATIONAL":
                score += 10
                criterios_eval.append("1. Status Operacional: Ativo no Google Maps (+10 pts)")
            else:
                criterios_eval.append("1. Status Operacional: Pendente / Inativo (0 pts)")

            # 2. Avaliações e Volume (+15)
            rating = details.get("rating", 0)
            reviews = details.get("user_ratings_total", 0)
            if rating >= 4.8 and reviews >= 80:
                score += 15
                criterios_eval.append(f"2. Avaliações dos Clientes: Excelente ({rating}★ em {reviews} avaliações) (+15 pts)")
            elif rating >= 4.0 and reviews >= 10:
                score += 8
                criterios_eval.append(f"2. Avaliações dos Clientes: Moderado ({rating}★ em {reviews} avaliações) (+8 pts)")
            else:
                criterios_eval.append(f"2. Avaliações dos Clientes: Insuficiente ({rating}★ em {reviews} avaliações) (0 pts)")

            # 3. Galeria Visual e Fotos (+10)
            photos = details.get("photos", [])
            if len(photos) >= 30:
                score += 10
                criterios_eval.append(f"3. Galeria Visual: Completa ({len(photos)} fotos) (+10 pts)")
            elif len(photos) >= 5:
                score += 5
                criterios_eval.append(f"3. Galeria Visual: Parcial ({len(photos)} fotos) (+5 pts)")
            else:
                criterios_eval.append("3. Galeria Visual: Insuficiente (0 pts)")

            # 4. Telefone Cadastrado (+10)
            if details.get("formatted_phone_number"):
                score += 10
                criterios_eval.append("4. Telefone Principal: Cadastrado (+10 pts)")
            else:
                criterios_eval.append("4. Telefone Principal: Ausente (0 pts)")

            # 5. Website Próprio (+10)
            website = details.get("website", "")
            if website and not any(x in website for x in ["facebook", "instagram", "site.google"]):
                score += 10
                criterios_eval.append("5. Website Institucional: Domínio próprio vinculado (+10 pts)")
            elif website:
                score += 3
                criterios_eval.append("5. Website Institucional: Link secundário / Rede Social (+3 pts)")
            else:
                criterios_eval.append("5. Website Institucional: Ausente (0 pts)")

            # 6. Horários de Funcionamento (+5)
            if details.get("opening_hours"):
                score += 5
                criterios_eval.append("6. Horários de Atendimento: Atualizados (+5 pts)")
            else:
                criterios_eval.append("6. Horários de Atendimento: Não informados (0 pts)")

            # 7. Endereço Completo (+5)
            addr = details.get("formatted_address", "")
            if addr and any(char.isdigit() for char in addr):
                score += 5
                criterios_eval.append("7. Endereço Físico: Completo com número (+5 pts)")
            else:
                criterios_eval.append("7. Endereço Físico: Incompleto (0 pts)")

            # 8. Categoria Principal (+5)
            if details.get("types"):
                score += 5
                criterios_eval.append("8. Categoria Principal: Configurada (+5 pts)")
            else:
                criterios_eval.append("8. Categoria Principal: Ausente (0 pts)")

            # 9. Tour Virtual 360° Interativo (Item Decisivo do Diagnóstico)
            criterios_eval.append("9. Tour Virtual 360° Street View: Não detectado no perfil (Pendente de Otimização)")

            return {
                "sucesso": True,
                "place_id": place_id,
                "nome": details.get("name"),
                "endereco": details.get("formatted_address", "Endereço registrado no Google Maps"),
                "score": min(score, 100),
                "criterios": criterios_eval
            }
    except Exception as e:
        print(f"Erro no cálculo do score Google: {e}")
        
    return {"sucesso": False, "mensagem": "Empresa não encontrada no Google."}

# ==========================================
# GERADOR DE PDF DIRETO EM MEMÓRIA / BYTES
# ==========================================
def gerar_pdf_diagnostico_bytes(empresa_nome, endereco, score, criterios):
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=30,
            rightMargin=30,
            topMargin=30,
            bottomMargin=30
        )
        
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('HeaderTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=colors.HexColor('#1565C0'))
        style_sub = ParagraphStyle('HeaderSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor('#222222'))
        style_body = ParagraphStyle('HeaderBody', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=colors.HexColor('#444444'))
        style_cell = ParagraphStyle('CellText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#333333'))
        style_cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=10, textColor=colors.white)

        elements = []
        
        elements.append(Paragraph("TOUR360VR • RELATÓRIO DE AUDITORIA DE PERFIL GOOGLE", style_title))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1565C0'), spaceBefore=4, spaceAfter=8))
        
        elements.append(Paragraph(f"<b>Empresa Analisada:</b> {empresa_nome}", style_sub))
        elements.append(Paragraph(f"<b>Endereço Cadastrado:</b> {endereco}", style_body))
        elements.append(Spacer(1, 10))
        
        cor_score_hex = obter_cor_score(score)
        elements.append(Paragraph(f"DIAGNÓSTICO DE OTIMIZAÇÃO: <font color='{cor_score_hex}'><b>{score} / 100 PONTOS</b></font>", ParagraphStyle('ScorePDF', parent=style_title, fontSize=13.5)))
        elements.append(Spacer(1, 8))
        
        elements.append(Paragraph("<b>Detalhamento dos 9 Critérios Avaliados:</b>", style_sub))
        elements.append(Spacer(1, 4))
        
        tabela_dados = [[Paragraph("Critério Avaliado", style_cell_bold), Paragraph("Status no Perfil Google", style_cell_bold)]]
        for crit in criterios:
            partes = crit.split(":")
            c_item = partes[0] if len(partes) > 0 else crit
            c_res = partes[1] if len(partes) > 1 else "Verificado"
            tabela_dados.append([Paragraph(c_item, style_cell), Paragraph(c_res, style_cell)])
            
        t = Table(tabela_dados, colWidths=[200, 335])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')])
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("<b>Recomendações para Atingir Nota Máxima (100 PONTOS):</b>", style_sub))
        elements.append(Paragraph("1. Implantação de Tour Virtual 360° Interativo homologado no Google Street View.<br>2. Atualização visual contínua da galeria de fotos e estímulo a avaliações positivas.<br>3. Vinculação de domínio próprio e alinhamento de horários.", style_body))
        
        elements.append(Spacer(1, 14))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CCCCCC'), spaceBefore=2, spaceAfter=4))
        elements.append(Paragraph("Tour360VR • Rubens Okamoto | contato@tour360vr.com.br | www.tour360vr.com.br", ParagraphStyle('Foot', parent=style_body, fontSize=7.5, alignment=1)))
        
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    except Exception as e:
        print(f"Erro na construção do PDF: {e}")
        return None

# ==========================================
# ENVIO DE E-MAILS COM ATTACHMENT EM MEMÓRIA
# ==========================================
def enviar_emails_diagnostico_completo(nome_lead, email_lead, whatsapp_lead, dados_busca):
    try:
        empresa_nome = dados_busca['nome']
        score = dados_busca['score']
        endereco = dados_busca['endereco']
        criterios = dados_busca.get('criterios', [])
        cor_score_hex = obter_cor_score(score)

        # Gera o PDF em memória (Bytes)
        pdf_data = gerar_pdf_diagnostico_bytes(empresa_nome, endereco, score, criterios)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)

        # 1. E-mail Notificação Interna
        msg_admin = MIMEMultipart('mixed')
        msg_admin['From'] = f"Tour360VR <{SMTP_USER}>"
        msg_admin['To'] = SMTP_USER
        msg_admin['Reply-To'] = SMTP_USER
        msg_admin['Subject'] = f"🚀 NOVO LEAD: {empresa_nome} (Score: {score}/100)"
        
        corpo_admin_html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: Arial, sans-serif; background-color: #F4F6F9; padding: 20px; margin: 0;">
            <div style="max-width: 580px; background-color: #FFFFFF; padding: 25px; border-radius: 10px; border-top: 5px solid #1E88E5; margin: 0 auto; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <h2 style="color: #111111; margin-top: 0; font-size: 18px;">Novo Lead Capturado no Site!</h2>
                <hr style="border: 0; border-top: 1px solid #EEEEEE; margin: 15px 0;">
                <p style="font-size: 14px; margin: 5px 0;"><b>Empresa:</b> {empresa_nome}</p>
                <p style="font-size: 14px; margin: 5px 0;"><b>Pontuação:</b> <span style="font-size: 16px; color: {cor_score_hex}; font-weight: bold;">{score} / 100</span></p>
                
                <div style="background-color: #F8F9FA; padding: 15px; border-radius: 8px; border-left: 4px solid #1E88E5; margin: 18px 0;">
                    <p style="margin: 4px 0; font-size: 14px;"><b>Nome:</b> {nome_lead}</p>
                    <p style="margin: 4px 0; font-size: 14px;"><b>E-mail:</b> <a href="mailto:{email_lead}" style="color: #1E88E5;">{email_lead}</a></p>
                    <p style="margin: 4px 0; font-size: 14px;"><b>WhatsApp:</b> <a href="https://wa.me/{whatsapp_lead}" target="_blank" style="color: #1E88E5; font-weight: bold;">+{whatsapp_lead}</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        msg_admin.attach(MIMEText(corpo_admin_html, 'html', 'utf-8'))
        
        if pdf_data:
            p_admin = MIMEBase('application', 'pdf')
            p_admin.set_payload(pdf_data)
            encoders.encode_base64(p_admin)
            p_admin.add_header('Content-Disposition', 'attachment', filename=f"Diagnostico_{re.sub(r'[^a-zA-Z0-9]', '_', empresa_nome)}.pdf")
            msg_admin.attach(p_admin)

        server.send_message(msg_admin)

        # 2. E-mail Cliente
        msg_cliente = MIMEMultipart('mixed')
        msg_cliente['From'] = f"Rubens Okamoto | Tour360VR <{SMTP_USER}>"
        msg_cliente['To'] = email_lead
        msg_cliente['Reply-To'] = SMTP_USER
        msg_cliente['Subject'] = f"Diagnóstico de Perfil no Google - {empresa_nome}"
        
        corpo_html_cliente = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6; background-color: #FFFFFF; padding: 15px;">
            <div style="max-width: 600px; margin: 0 auto;">
                <p>Olá, <b>{nome_lead}</b>!</p>
                <p>Recebemos a solicitação de diagnóstico para a empresa <b>{empresa_nome}</b>.</p>
                <p>Sua pontuação de otimização atual no Google é: <b style="font-size: 18px; color: {cor_score_hex};">{score}/100</b>.</p>
                <p>Anexamos a este e-mail o seu relatório detalhado em PDF.</p>
                <p>Em breve, um especialista entrará em contato via WhatsApp para apresentar como atingir a nota máxima e alavancar a visibilidade da sua empresa.</p>
                <br>
                <p>Atenciosamente,<br><b>Rubens Okamoto | Tour360VR</b><br><a href="https://www.tour360vr.com.br" style="color: #1E88E5;">www.tour360vr.com.br</a></p>
            </div>
        </body>
        </html>
        """
        msg_cliente.attach(MIMEText(corpo_html_cliente, 'html', 'utf-8'))

        if pdf_data:
            p_cliente = MIMEBase('application', 'pdf')
            p_cliente.set_payload(pdf_data)
            encoders.encode_base64(p_cliente)
            p_cliente.add_header('Content-Disposition', 'attachment', filename=f"Diagnostico_Google_{re.sub(r'[^a-zA-Z0-9]', '_', empresa_nome)}.pdf")
            msg_cliente.attach(p_cliente)

        server.send_message(msg_cliente)
        server.quit()

        return True
    except Exception as e:
        print(f"Erro na rotina de envio de e-mails: {e}")
        return False

# ==========================================
# INTERFACE DO USUÁRIO
# ==========================================
st.markdown('<div class="titulo-principal">🔍 Faça uma análise da sua empresa no Google</div>', unsafe_allow_html=True)
st.markdown('<div class="instrucao-subtitulo">Digite o Nome Comercial exato da sua empresa seguido da Cidade e Estado.</div>', unsafe_allow_html=True)

nome_empresa = st.text_input("BuscaInput", value="", placeholder="Ex: Tour360VR Ribeirão Preto SP", label_visibility="collapsed")

if st.button("🔍 Analisar perfil"):
    if nome_empresa:
        with st.spinner("Analisando perfil no Google Maps..."):
            res = consultar_score_google_rigoroso(nome_empresa)
            if res["sucesso"]:
                st.session_state["resultado_busca"] = res
            else:
                st.error("❌ Empresa não encontrada. Tente incluir a cidade ou verificar a grafia exata cadastrada no Google.")

# Exibição do Resultado no Container Compacto Cinza/Azulado
if "resultado_busca" in st.session_state:
    dados = st.session_state["resultado_busca"]
    cor_nota = obter_cor_score(dados["score"])
    
    html_card_resultado = f"""
    <div class="card-resultado-compacto">
        <div style="text-align: center; color: #111111; font-size: 1.2rem; font-weight: 800; margin-bottom: 2px;">Empresa Localizada: {dados["nome"]}</div>
        <p style="text-align: center; color: #555555; font-size: 0.88rem; margin-top: 0; margin-bottom: 6px;">📍 {dados["endereco"]}</p>
        <p style="text-align: center; font-weight: 700; font-size: 1rem; margin-top: 4px; margin-bottom: 2px;">Pontuação Geral de Otimização</p>
        <div style="text-align: center; font-size: 3rem; font-weight: 900; line-height: 1; margin: 2px 0 8px 0; color: {cor_nota} !important;">{dados["score"]} / 100</div>
        <div style="background-color: #FFFDE7; border: 1px solid #FBC02D; border-radius: 6px; padding: 6px 10px; text-align: center; color: #5D4037; font-size: 0.88rem; font-weight: 600;">
            ⚠️ Identificamos oportunidades de melhoria que podem estar reduzindo a visibilidade do seu negócio para novos clientes.
        </div>
    </div>
    """
    st.markdown(html_card_resultado, unsafe_allow_html=True)

    # Formulário de Captura
    st.markdown('<div class="titulo-principal" style="font-size: 1.15rem; margin-top: 1rem;">📋 Preencha os dados abaixo e receba a análise completa</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="rotulo-campo">Nome:</div>', unsafe_allow_html=True)
    nome_lead = st.text_input("NomeInput", value="", placeholder="Digite o seu nome completo", label_visibility="collapsed")
    
    st.markdown('<div class="rotulo-campo">E-mail:</div>', unsafe_allow_html=True)
    email_lead = st.text_input("EmailInput", value="", placeholder="exemplo@email.com", label_visibility="collapsed")
    
    st.markdown('<div class="rotulo-campo">WhatsApp</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtexto-label">(DDD + 9 dígitos - Apenas números)</div>', unsafe_allow_html=True)
    
    raw_whats = st.text_input("WhatsInput", value="", placeholder="16991332121", label_visibility="collapsed")

    if st.button("📩 Receber diagnóstico"):
        apenas_numeros = re.sub(r'\D', '', raw_whats)[:11]
        
        if not nome_lead or len(nome_lead.strip()) < 2:
            st.error("Por favor, informe seu nome completo.")
        elif not email_lead or "@" not in email_lead:
            st.error("Por favor, informe um endereço de e-mail válido.")
        elif len(apenas_numeros) != 11:
            st.error(f"❌ O campo WhatsApp exige exatamente 11 NÚMEROS (DDD + Celular, ex: 16991332121). Você informou {len(apenas_numeros)} números.")
        else:
            whats_completo = "55" + apenas_numeros

            # Envia e-mails com o PDF
            com_sucesso = enviar_emails_diagnostico_completo(nome_lead, email_lead, whats_completo, dados)
            
            if com_sucesso:
                st.markdown("""
                <div class="card-sucesso-destaque">
                    ✅ Diagnóstico enviado com sucesso! Verifique sua caixa de entrada e spam.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Ocorreu uma falha ao disparar o e-mail. Tente novamente em instantes.")

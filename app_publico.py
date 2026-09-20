import os
import re
import io
import requests
import smtplib
import streamlit as st
import streamlit.components.v1 as components

# ReportLab para geração do PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# ==========================================
# CONFIGURAÇÃO DE PÁGINA E CSS STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Análise de Perfil no Google - Tour360VR",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS Definitivo de Trava e Ocultação Total dos Ícones do Streamlit
custom_css = """
<style>
    html, body, [data-testid="stAppViewContainer"], .main, .stApp {
        overflow: hidden !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 900px !important;
    }

    /* Oculta rigorosamente menus, headers, footers e ícones/badges flutuantes */
    header, 
    [data-testid="stHeader"], 
    [data-testid="stAppHeader"],
    [data-testid="stToolbar"], 
    [data-testid="stDecoration"], 
    [data-testid="stStatusWidget"],
    #MainMenu, 
    footer, 
    .stApp footer, 
    [data-testid="stFooter"],
    .viewerBadge_container__1QSob, 
    .styles_viewerBadge__1yB5_,
    button[title="View source"],
    a[href*="streamlit"],
    a[href*="github"],
    div[class*="viewerBadge"],
    div[class*="styles_viewerBadge"],
    div[class*="stStatusWidget"],
    div[class*="viewerBadge_container"],
    div[data-testid*="stStatusWidget"],
    div[data-testid*="viewerBadge"],
    .stStatusWidget,
    div[class*="StatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
        width: 0px !important;
        pointer-events: none !important;
    }

    .card-resultado-compacto {
        background-color: #F0F4F8 !important;
        border: 1px solid #D0D7DE !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        margin: 0.2rem auto !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    }

    .titulo-principal {
        text-align: center;
        color: #111111 !important;
        font-size: 2.1rem;
        font-weight: 800;
        margin-bottom: 0.1rem;
        line-height: 1.2;
        font-family: 'Arial', sans-serif;
    }

    .instrucao-subtitulo {
        text-align: center;
        color: #444444 !important;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
        font-family: 'Arial', sans-serif;
    }

    .titulo-secundario {
        text-align: center;
        color: #111111 !important;
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 0.4rem;
        margin-bottom: 0.2rem;
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
        font-size: 0.95rem !important;
        padding: 0.4rem 0.8rem !important;
        text-align: center !important;
        color: #000000 !important;
    }

    .stTextInput input:focus {
        border-color: #1565C0 !important;
        box-shadow: 0 0 4px rgba(21, 101, 192, 0.4) !important;
    }

    .rotulo-campo {
        text-align: center !important;
        color: #111111 !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        margin-top: 0.15rem !important;
        margin-bottom: 0.05rem !important;
    }
    .subtexto-label {
        font-size: 0.75rem !important;
        color: #666666 !important;
        text-align: center !important;
        margin-bottom: 0.15rem !important;
    }

    div[data-testid="stButton"], div.stButton {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin: 0.3rem auto !important;
    }
    .stButton > button {
        background-color: #1565C0 !important;
        color: #FFFFFF !important;
        font-size: 1rem !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
        cursor: pointer !important;
        width: 100% !important;
        max-width: 520px !important;
        transition: background-color 0.2s ease-in-out !important;
    }
    .stButton > button:hover {
        background-color: #0D47A1 !important;
    }
    .stButton > button p {
        color: #FFFFFF !important;
        margin: 0 !important;
        font-weight: bold !important;
    }

    .card-sucesso-destaque {
        background-color: #E8F5E9 !important;
        border: 2px solid #2E7D32 !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        text-align: center !important;
        color: #1B5E20 !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        margin: 0.4rem auto !important;
        max-width: 520px !important;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.15) !important;
        line-height: 1.4 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# JS Rígido de Remoção do Pop-up Flutuante do Streamlit no DOM Pai
components.html("""
<script>
    function destroyStreamlitBadges() {
        var targets = [document, window.parent.document, window.top.document];
        targets.forEach(function(doc) {
            try {
                if(!doc) return;
                var selectors = [
                    '[data-testid="stStatusWidget"]',
                    '[data-testid="stHeader"]',
                    '.viewerBadge_container__1QSob',
                    '[class*="viewerBadge"]',
                    '[class*="styles_viewerBadge"]',
                    'a[href*="streamlit"]',
                    'a[href*="github"]',
                    'div[data-testid*="Status"]',
                    'iframe[src*="streamlit"]'
                ];
                selectors.forEach(function(s) {
                    var elements = doc.querySelectorAll(s);
                    elements.forEach(function(el) {
                        el.style.display = 'none';
                        el.style.visibility = 'hidden';
                        el.style.opacity = '0';
                        el.remove();
                    });
                });
            } catch(e){}
        });
    }
    setInterval(destroyStreamlitBadges, 150);
</script>
""", height=0, width=0)

# ==========================================
# CREDENCIAIS DO SISTEMA
# ==========================================
GOOGLE_API_KEY = "AIzaSyA8ul_9QICNyqxrHgT-CURIZmd1sikHn5U"

SMTP_SERVER = "smtp.tour360vr.com.br"
SMTP_PORT_SSL = 465
SMTP_USER = "contato@tour360vr.com.br"
SMTP_PASS = "Kakaroto@2026"

def obter_cor_score(score):
    if score <= 40:
        return "#D32F2F"
    elif score <= 70:
        return "#F57C00"
    else:
        return "#8DC63F"

def extrair_cidade(endereco):
    try:
        if "-" in endereco:
            partes = endereco.split("-")
            for i, p in enumerate(partes):
                if any(uf in p for uf in ["SP", "RJ", "MG", "PR", "RS", "SC", "BA", "GO", "DF", "PE", "CE"]):
                    cidade_part = partes[i-1].strip()
                    return cidade_part.split(",")[-1].strip()
        partes_v = [x.strip() for x in endereco.split(",")]
        if len(partes_v) >= 3:
            return partes_v[-3]
    except Exception:
        pass
    return "Não Informada"

# ==========================================
# INTEGRAÇÃO ZOHO BIGIN (SINALIZADOR 1 - NO NOME)
# ==========================================
def enviar_lead_zoho_bigin(nome_lead, email_lead, whatsapp_lead, empresa_nome, endereco, score):
    url_bigin = "https://bigin.zoho.com/crm/WebToContactForm"
    
    cidade = extrair_cidade(endereco)

    # Prefixado com "1 - " para ir diretamente para o topo da lista de Clientes
    nome_identificado = f"1 - {nome_lead.strip()}"
    partes_nome = nome_identificado.split(" ", 1)
    primeiro_nome = partes_nome[0]
    sobrenome = partes_nome[1] if len(partes_nome) > 1 else "."

    payload = {
        'xnQsjsdp': '15d54e8d1dfa724381be9ad892936abd18de3deadc2763d67c0dd5f939138a91',
        'zc_gad': '',
        'xmIwtLD': '7bf1ddf18cd4b2e66bc992eae51f7e88125018eba8806dd498fb7e87e015ca5085bf99ead8aa16f7a6ff561d393a37ef',
        'actionType': 'Q29udGFjdHM=',
        'rmsg': 'true',
        'returnURL': 'null',
        'First Name': primeiro_nome,
        'Last Name': sobrenome,
        'Email': email_lead,
        'Accounts.Account Name': empresa_nome,
        'Phone': whatsapp_lead,
        'CONTACTCF6': f"{score}/100",
        'Description': f"📌 ORIGEM: Formulário Diagnóstico Site\nCidade: {cidade}\nEndereço: {endereco}\nPontuação Google: {score}/100"
    }
    
    try:
        res = requests.post(url_bigin, data=payload, timeout=8)
        return res.status_code == 200
    except Exception as e:
        print(f"Erro no Bigin: {e}")
        return False

# ==========================================
# CÁLCULO DE SCORE GOOGLE MAPS
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
            criterios_eval = []

            if details.get("business_status") == "OPERATIONAL":
                score += 10
                criterios_eval.append("1. Status Operacional: Ativo no Google Maps")
            else:
                criterios_eval.append("1. Status Operacional: Pendente / Inativo")

            rating = details.get("rating", 0)
            reviews = details.get("user_ratings_total", 0)
            if rating >= 4.8 and reviews >= 100:
                score += 20
                criterios_eval.append(f"2. Avaliações dos Clientes: Excelente ({rating}★ em {reviews} avaliações)")
            elif rating >= 4.5 and reviews >= 30:
                score += 10
                criterios_eval.append(f"2. Avaliações dos Clientes: Moderado ({rating}★ em {reviews} avaliações)")
            else:
                criterios_eval.append(f"2. Avaliações dos Clientes: Volume Insuficiente ({rating}★ em {reviews} avaliações)")

            photos = details.get("photos", [])
            if len(photos) >= 30:
                score += 20
                criterios_eval.append(f"3. Galeria Visual: Completa ({len(photos)} fotos)")
            elif len(photos) >= 15:
                score += 10
                criterios_eval.append(f"3. Galeria Visual: Parcial ({len(photos)} fotos)")
            else:
                criterios_eval.append("3. Galeria Visual: Insuficiente")

            if details.get("formatted_phone_number"):
                score += 5
                criterios_eval.append("4. Telefone Principal: Cadastrado")
            else:
                criterios_eval.append("4. Telefone Principal: Ausente")

            website = details.get("website", "")
            if website and not any(x in website for x in ["facebook", "instagram", "site.google", "wa.me", "linktr.ee"]):
                score += 20
                criterios_eval.append("5. Website Institucional: Domínio próprio vinculado")
            else:
                criterios_eval.append("5. Website Institucional: Ausente / Link Genérico")

            if details.get("opening_hours"):
                score += 5
                criterios_eval.append("6. Horários de Atendimento: Configurados")
            else:
                criterios_eval.append("6. Horários de Atendimento: Incompletos")

            addr = details.get("formatted_address", "")
            if addr and any(char.isdigit() for char in addr):
                score += 10
                criterios_eval.append("7. Endereço Físico: Completo com número")
            else:
                criterios_eval.append("7. Endereço Físico: Incompleto")

            if details.get("types"):
                score += 10
                criterios_eval.append("8. Categoria Principal: Mapeada")
            else:
                criterios_eval.append("8. Categoria Principal: Ausente")

            criterios_eval.append("9. Tour Virtual 360° Street View: Ausente (Oportunidade de Destaque)")
            score = min(score, 10)

            return {
                "sucesso": True,
                "place_id": place_id,
                "nome": details.get("name"),
                "endereco": details.get("formatted_address", "Endereço registrado no Google Maps"),
                "score": score,
                "criterios": criterios_eval
            }
    except Exception as e:
        print(f"Erro no cálculo do score Google: {e}")
        
    return {"sucesso": False, "mensagem": "Empresa não encontrada no Google."}

# ==========================================
# GERADOR DE PDF (RODAPÉ FIXO NO FINAL DA PÁGINA)
# ==========================================
def desenhar_rodape_fixo(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#CCCCCC'))
    canvas.setLineWidth(0.5)
    canvas.line(35, 40, 560, 40)
    
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#555555'))
    canvas.drawCentredString(297, 26, "Tour360VR • Rubens Okamoto | contato@tour360vr.com.br | www.tour360vr.com.br")
    canvas.restoreState()

def gerar_pdf_bytes_in_memory(empresa_nome, endereco, score, criterios):
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=35,
            rightMargin=35,
            topMargin=35,
            bottomMargin=50
        )
        
        styles = getSampleStyleSheet()
        style_title = ParagraphStyle('HeaderTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13.5, leading=16, textColor=colors.HexColor('#1565C0'))
        style_sub = ParagraphStyle('HeaderSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor('#222222'))
        style_body = ParagraphStyle('HeaderBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#444444'))
        style_cell = ParagraphStyle('CellText', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor('#333333'))
        style_cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white)

        elements = []
        
        elements.append(Paragraph("AUDITORIA DE POSICIONAMENTO GOOGLE MAPS - TOUR360VR", style_title))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1565C0'), spaceBefore=6, spaceAfter=16))
        
        elements.append(Spacer(1, 14))
        elements.append(Paragraph(f"<b>Empresa Analisada:</b> {empresa_nome}", style_sub))
        elements.append(Paragraph(f"<b>Endereço Registrado:</b> {endereco}", style_body))
        elements.append(Spacer(1, 16))
        
        cor_score_hex = obter_cor_score(score)
        elements.append(Paragraph(f"PONTUAÇÃO DE OTIMIZAÇÃO: <font color='{cor_score_hex}'><b>{score} / 100 PONTOS</b></font>", ParagraphStyle('ScorePDF', parent=style_title, fontSize=13)))
        elements.append(Spacer(1, 14))
        
        elements.append(Paragraph("<b>Análise Detalhada dos Critérios Avaliados:</b>", style_sub))
        elements.append(Spacer(1, 8))
        
        tabela_dados = [[Paragraph("Critério de Otimização", style_cell_bold), Paragraph("Diagnóstico do Perfil", style_cell_bold)]]
        for crit in criterios:
            partes = crit.split(":")
            c_item = partes[0] if len(partes) > 0 else crit
            c_res = partes[1] if len(partes) > 1 else "Verificado"
            tabela_dados.append([Paragraph(c_item, style_cell), Paragraph(c_res, style_cell)])
            
        t = Table(tabela_dados, colWidths=[210, 315])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')])
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("<b>Plano de Ação Sugerido para Alta Visibilidade:</b>", style_sub))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph("1. Implantação de Tour Virtual 360° Interativo integrado ao Google Street View.<br/>2. Atualização visual contínua da galeria de fotos e gestão ativa de avaliações.<br/>3. Alinhamento de horários de funcionamento e inclusão do site oficial.", style_body))
        
        doc.build(elements, onFirstPage=desenhar_rodape_fixo, onLaterPages=desenhar_rodape_fixo)
        val = buffer.getvalue()
        buffer.close()
        return val
    except Exception as e:
        st.error(f"Erro na geração do PDF: {e}")
        return None

# ==========================================
# ENVIO DE E-MAILS
# ==========================================
def enviar_emails_diagnostico_completo(nome_lead, email_lead, whatsapp_lead, dados_busca):
    try:
        empresa_nome = dados_busca['nome']
        score = dados_busca['score']
        endereco = dados_busca['endereco']
        criterios = dados_busca.get('criterios', [])
        cor_score_hex = obter_cor_score(score)

        pdf_bytes = gerar_pdf_bytes_in_memory(empresa_nome, endereco, score, criterios)

        if not pdf_bytes:
            return False, "Não foi possível gerar o arquivo PDF do relatório."

        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT_SSL, timeout=15)
        server.login(SMTP_USER, SMTP_PASS)

        filename_clean = f"Diagnostico_{re.sub(r'[^a-zA-Z0-9]', '_', empresa_nome)}.pdf"

        # 1. E-mail Admin
        msg_admin = MIMEMultipart('mixed')
        msg_admin['From'] = f"Tour360VR <{SMTP_USER}>"
        msg_admin['To'] = SMTP_USER
        msg_admin['Reply-To'] = SMTP_USER
        msg_admin['Subject'] = f"🚀 NOVO LEAD: {empresa_nome} (Score: {score}/100)"
        
        corpo_admin_html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: Arial, sans-serif; background-color: #F4F6F9; padding: 15px; margin: 0;">
            <div style="max-width: 580px; background-color: #FFFFFF; padding: 20px; border-radius: 10px; border-top: 5px solid #1565C0; margin: 0 auto; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <h2 style="color: #111111; margin-top: 0; font-size: 18px;">Novo Lead Capturado no Site!</h2>
                <hr style="border: 0; border-top: 1px solid #EEEEEE; margin: 12px 0;">
                <p style="font-size: 14px; margin: 4px 0;"><b>Empresa:</b> {empresa_nome}</p>
                <p style="font-size: 14px; margin: 4px 0;"><b>Pontuação:</b> <span style="font-size: 16px; color: {cor_score_hex}; font-weight: bold;">{score} / 100</span></p>
                
                <div style="background-color: #F8F9FA; padding: 12px; border-radius: 8px; border-left: 4px solid #1565C0; margin: 14px 0;">
                    <p style="margin: 3px 0; font-size: 14px;"><b>Nome:</b> {nome_lead}</p>
                    <p style="margin: 3px 0; font-size: 14px;"><b>E-mail:</b> <a href="mailto:{email_lead}" style="color: #1565C0;">{email_lead}</a></p>
                    <p style="margin: 3px 0; font-size: 14px;"><b>WhatsApp:</b> <a href="https://wa.me/{whatsapp_lead}" target="_blank" style="color: #1565C0; font-weight: bold;">+{whatsapp_lead}</a></p>
                </div>

                <hr style="border: 0; border-top: 1px solid #EEEEEE; margin: 18px 0 12px 0;">
                <div style="text-align: center; color: #777777; font-size: 12px; line-height: 1.4;">
                    <p style="margin: 2px 0;"><b>Tour360VR • Soluções em Imagem e Presença Digital</b></p>
                    <p style="margin: 2px 0;">Rubens Okamoto | <a href="mailto:contato@tour360vr.com.br" style="color: #1565C0; text-decoration: none;">contato@tour360vr.com.br</a></p>
                    <p style="margin: 2px 0;"><a href="https://www.tour360vr.com.br" target="_blank" style="color: #1565C0; text-decoration: none;">www.tour360vr.com.br</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        msg_admin.attach(MIMEText(corpo_admin_html, 'html', 'utf-8'))
        
        if pdf_bytes:
            part_admin = MIMEApplication(pdf_bytes, _subtype="pdf")
            part_admin.add_header('Content-Disposition', 'attachment', filename=filename_clean)
            msg_admin.attach(part_admin)

        server.send_message(msg_admin)

        # 2. E-mail Cliente
        msg_cliente = MIMEMultipart('mixed')
        msg_cliente['From'] = f"Rubens Okamoto | Tour360VR <{SMTP_USER}>"
        msg_cliente['To'] = email_lead
        msg_cliente['Reply-To'] = SMTP_USER
        msg_cliente['Subject'] = f"Diagnóstico de Perfil no Google - {empresa_nome}"
        
        corpo_html_cliente = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; color: #333333; font-size: 15px; line-height: 1.4; background-color: #FFFFFF; padding: 10px; margin: 0;">
<div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; font-size: 15px; color: #333333;">
<p style="margin: 0 0 32px 0; font-size: 15px; font-family: Arial, sans-serif; color: #333333;">Olá, {nome_lead}!</p>

<p style="margin: 0 0 16px 0; font-size: 15px; font-family: Arial, sans-serif; color: #333333;">Ficamos felizes pelo seu interesse em melhorar a presença online da sua empresa!</p>

<p style="margin: 0 0 16px 0; font-size: 15px; font-family: Arial, sans-serif; color: #333333;">Recebemos a solicitação de diagnóstico para <b>{empresa_nome}</b>.</p>

<p style="margin: 0 0 16px 0; font-size: 15px; font-family: Arial, sans-serif; color: #333333;">Sua pontuação de otimização atual no Google é: <b style="font-size: 17px; color: {cor_score_hex}; font-weight: bold;">{score}/100</b>.</p>

<p style="margin: 0 0 16px 0; font-size: 15px; font-family: Arial, sans-serif; color: #333333;">Anexamos a este e-mail o seu relatório detalhado em PDF.</p>

<p style="margin: 32px 0 24px 0; font-size: 15px; font-family: Arial, sans-serif; color: #333333;">Em breve, um especialista entrará em contato para apresentar como alavancar a visibilidade da sua empresa.</p>

<p style="margin: 0; font-size: 15px; font-family: Arial, sans-serif; color: #333333; line-height: 1.4;">
Atenciosamente,<br/>
<b>Rubens Okamoto | Tour360VR</b><br/>
<a href="https://www.tour360vr.com.br" target="_blank" style="color: #1565C0; text-decoration: none;">www.tour360vr.com.br</a>
</p>
</div>
</body>
</html>
"""
        msg_cliente.attach(MIMEText(corpo_html_cliente, 'html', 'utf-8'))

        if pdf_bytes:
            part_cliente = MIMEApplication(pdf_bytes, _subtype="pdf")
            part_cliente.add_header('Content-Disposition', 'attachment', filename=filename_clean)
            msg_cliente.attach(part_cliente)

        server.send_message(msg_cliente)
        server.quit()

        return True, "E-mails e PDF enviados com sucesso!"
    except Exception as e:
        return False, f"Falha no envio do e-mail/PDF: {str(e)}"

# ==========================================
# INTERFACE STREAMLIT
# ==========================================
st.markdown('<div class="titulo-principal">Pronto para destacar sua empresa no Google?</div>', unsafe_allow_html=True)
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

if "resultado_busca" in st.session_state:
    dados = st.session_state["resultado_busca"]
    cor_nota = obter_cor_score(dados["score"])
    
    html_card_resultado = f"""
    <div class="card-resultado-compacto">
        <div style="text-align: center; color: #111111; font-size: 1.2rem; font-weight: 800; margin-bottom: 2px;">Empresa Localizada: {dados["nome"]}</div>
        <p style="text-align: center; color: #555555; font-size: 0.88rem; margin-top: 0; margin-bottom: 4px;">📍 {dados["endereco"]}</p>
        <p style="text-align: center; font-weight: 700; font-size: 1rem; margin-top: 2px; margin-bottom: 2px;">Pontuação Geral de Otimização</p>
        <div style="text-align: center; font-size: 3rem; font-weight: 900; line-height: 1; margin: 2px 0 6px 0; color: {cor_nota} !important;">{dados["score"]} / 100</div>
        <div style="background-color: #FFFDE7; border: 1px solid #FBC02D; border-radius: 6px; padding: 5px 8px; text-align: center; color: #5D4037; font-size: 0.88rem; font-weight: 600;">
            ⚠️ Identificamos oportunidades de melhoria que podem estar reduzindo a visibilidade do seu negócio para novos clientes.
        </div>
    </div>
    """
    st.markdown(html_card_resultado, unsafe_allow_html=True)

    st.markdown('<div class="titulo-secundario">Preencha os dados abaixo e receba o diagnóstico completo do seu posicionamento digital.</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="rotulo-campo">Nome:</div>', unsafe_allow_html=True)
    nome_lead = st.text_input("NomeInput", value="", placeholder="Digite o seu nome completo", label_visibility="collapsed")
    
    st.markdown('<div class="rotulo-campo">E-mail:</div>', unsafe_allow_html=True)
    email_lead = st.text_input("EmailInput", value="", placeholder="exemplo@email.com", label_visibility="collapsed")
    
    st.markdown('<div class="rotulo-campo">WhatsApp</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtexto-label">(DDD + 9 dígitos - Apenas números)</div>', unsafe_allow_html=True)
    
    raw_whats_input = st.text_input("WhatsInput", value="", placeholder="16991332121", label_visibility="collapsed")
    apenas_numeros = re.sub(r'\D', '', raw_whats_input)[:11]

    if st.session_state.get("envio_sucesso"):
        st.markdown("""
        <div class="card-sucesso-destaque">
            ✅ Diagnóstico enviado com sucesso!<br/>Verifique sua caixa de entrada e spam.
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("📩 Receber diagnóstico"):
            if not nome_lead or len(nome_lead.strip()) < 2:
                st.error("Por favor, informe seu nome completo.")
            elif not email_lead or "@" not in email_lead:
                st.error("Por favor, informe um endereço de e-mail válido.")
            elif len(apenas_numeros) != 11:
                st.error(f"❌ O campo WhatsApp exige exatamente 11 NÚMEROS (DDD + Celular, ex: 16991332121). Apenas números são aceitos.")
            else:
                whats_completo = "55" + apenas_numeros

                with st.spinner("Gerando diagnóstico e enviando por e-mail..."):
                    email_sucesso, email_msg = enviar_emails_diagnostico_completo(nome_lead, email_lead, whats_completo, dados)
                    enviar_lead_zoho_bigin(nome_lead, email_lead, whats_completo, dados['nome'], dados['endereco'], dados['score'])

                if email_sucesso:
                    st.session_state["envio_sucesso"] = True
                    st.rerun()
                else:
                    st.error(f"❌ Erro ao enviar e-mail: {email_msg}")

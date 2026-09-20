import os
import requests
import smtplib
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st

# Tenta importar o ReportLab; se ainda estiver instalando, o código não quebra
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    PDF_DISPONIVEL = True
except ImportError:
    PDF_DISPONIVEL = False

# ==========================================
# CONFIGURAÇÃO DE TEMA E VISUAL PERSONALIZADO
# ==========================================
st.set_page_config(
    page_title="Análise da Empresa no Google - Tour360VR", 
    page_icon="🔍",
    layout="centered"
)

# Estilo CSS com Prioridade Máxima
custom_css = """
<style>
    /* 1. Fundo limpo e container otimizado */
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
        max-width: 750px !important;
    }

    header, footer, #MainMenu {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* 2. Título sem quebras e Rótulos */
    .titulo-uma-linha {
        text-align: center;
        color: #000000 !important;
        font-size: 1.45rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        font-family: 'Arial', sans-serif;
        white-space: nowrap;
    }
    .instrucao-subtitulo {
        text-align: center;
        color: #333333 !important;
        font-size: 0.98rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        font-family: 'Arial', sans-serif;
    }

    .empresa-localizada-titulo {
        text-align: center;
        color: #000000 !important;
        font-size: 1.35rem !important;
        font-weight: 800;
        margin-top: 0.2rem;
        margin-bottom: 0.1rem;
    }

    /* Rótulos Visíveis e Claros */
    label, div[data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        font-family: 'Arial', sans-serif !important;
    }

    /* 3. Inputs Claros e Alinhados */
    .stTextInput {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
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

    /* 4. NOTA DO SCORE GIGANTE E EM DESTAQUE */
    .nota-score-gigante {
        text-align: center !important;
        color: #8DC63F !important;
        font-size: 4.8rem !important;
        font-weight: 900 !important;
        font-family: 'Arial', sans-serif !important;
        line-height: 1 !important;
        margin: 0.2rem 0 0.8rem 0 !important;
    }

    /* 5. FIX DEFINITIVO DE CENTRALIZAÇÃO DOS BOTÕES */
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin: 0.8rem auto !important;
    }

    .stButton > button {
        background-color: #8DC63F !important;
        color: #FFFFFF !important;
        font-size: 1.15rem !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        cursor: pointer !important;
        box-shadow: 0 4px 12px rgba(141, 198, 63, 0.3) !important;
        margin: 0 auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        max-width: 380px !important;
    }

    .stButton > button:hover {
        background-color: #7BB533 !important;
        color: #FFFFFF !important;
    }

    .stButton > button p {
        color: #FFFFFF !important;
        font-size: 1.15rem !important;
        font-weight: bold !important;
        margin: 0 !important;
        text-align: center !important;
    }

    /* 6. Alerta Amarelo com Borda */
    .alerta-destaque {
        background-color: #FFFDE7 !important;
        border: 2px solid #FBC02D !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        text-align: center !important;
        color: #5D4037 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin: 0.8rem auto !important;
        max-width: 520px !important;
    }

    .destaque-formulario-linha {
        text-align: center;
        color: #000000 !important;
        font-size: 1.15rem;
        font-weight: 800;
        margin-top: 1rem;
        margin-bottom: 0.6rem;
        font-family: 'Arial', sans-serif;
        white-space: nowrap;
    }

    /* Card de Sucesso Profissional Destacado */
    .card-sucesso-destaque {
        background-color: #E8F5E9 !important;
        border: 2px solid #2E7D32 !important;
        border-radius: 10px !important;
        padding: 14px 20px !important;
        text-align: center !important;
        color: #1B5E20 !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        margin: 1.2rem auto !important;
        max-width: 480px !important;
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.15) !important;
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
# CÁLCULO DE SCORE RIGOROSO
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

            # Algoritmo de 9 Critérios Rígidos
            score = 0
            crit_det = []

            if details.get("business_status") == "OPERATIONAL": 
                score += 10
                crit_det.append("Status Operacional: Ativo")

            rating = details.get("rating", 0)
            reviews = details.get("user_ratings_total", 0)
            if rating >= 4.5 and reviews >= 50:
                score += 20
                crit_det.append(f"Avaliações: Excelente ({rating}★ - {reviews} avaliações)")

            photos = details.get("photos", [])
            if len(photos) >= 15:
                score += 20
                crit_det.append("Galeria de Fotos: Completa")

            if details.get("formatted_phone_number"):
                score += 10
                crit_det.append("Telefone: Cadastrado")

            if details.get("website"):
                score += 15
                crit_det.append("Website: Vinculado")

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
# GERADOR DE PDF
# ==========================================
def gerar_pdf_diagnostico(empresa_nome, endereco, score, criterios):
    if not PDF_DISPONIVEL:
        return None
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=35, bottomMargin=35)
        
        styles = getSampleStyleSheet()
        style_titulo = ParagraphStyle('TituloPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#8DC63F'))
        style_sub = ParagraphStyle('SubPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#222222'))
        style_texto = ParagraphStyle('TextoPDF', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#444444'))
        
        elements = []
        elements.append(Paragraph("TOUR360VR • RELATÓRIO DE DIAGNÓSTICO DIGITAL", style_titulo))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>Empresa Analisada:</b> {empresa_nome}", style_sub))
        elements.append(Paragraph(f"<b>Endereço:</b> {endereco}", style_texto))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph(f"<b>PONTUAÇÃO GERAL DE OTIMIZAÇÃO: {score} / 100</b>", ParagraphStyle('ScorePDF', parent=style_titulo, fontSize=16, textColor=colors.HexColor('#8DC63F'))))
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("<b>Critérios Analisados no Perfil do Google Maps:</b>", style_sub))
        elements.append(Spacer(1, 8))
        
        tabela_dados = [["Critério / Requisito", "Status de Otimização"]]
        for item in criterios:
            tabela_dados.append([item.split(":")[0], item.split(":")[1] if ":" in item else "Analisado"])
            
        t = Table(tabela_dados, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8DC63F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<b>Próximos Passos Recomendados:</b>", style_sub))
        elements.append(Paragraph("Para atingir os 100 pontos e garantir prioridade nas buscas locais do Google Maps, recomenda-se a inclusão de um Tour Virtual 360° homologado e atualização completa da galeria visual e categorias do perfil.", style_texto))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<b>Tour360VR • Imagem e Presença Digital</b><br>www.tour360vr.com.br | contato@tour360vr.com.br", style_texto))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return None

# ==========================================
# ENVIO DE LEAD PARA O BIGIN CRM
# ==========================================
def enviar_lead_bigin(nome_lead, email_lead, whatsapp_lead, empresa_consultada, score):
    try:
        url_token = f"https://accounts.zoho.com/oauth/v2/token?client_id={BIGIN_CLIENT_ID}&client_secret={BIGIN_CLIENT_SECRET}&grant_type=client_credentials&scope=ZohoBigin.modules.ALL"
        res_token = requests.post(url_token, timeout=10).json()
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
        res_deal = requests.post(url_deal, json=payload, headers=headers, timeout=10)
        return res_deal.status_code in [200, 201]
    except Exception as e:
        print(f"Erro Bigin: {e}")
        return False

# ==========================================
# DISPARO DE E-MAILS
# ==========================================
def enviar_emails_diagnostico_completo(nome_lead, email_lead, whatsapp_lead, dados_busca):
    try:
        empresa_nome = dados_busca['nome']
        score = dados_busca['score']
        endereco = dados_busca['endereco']
        criterios = dados_busca.get('criterios', [])

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)

        # 1. E-mail Administrativo para Tour360VR
        msg_admin = MIMEMultipart()
        msg_admin['From'] = SMTP_USER
        msg_admin['To'] = SMTP_USER
        msg_admin['Subject'] = f"Novo Lead Diagnóstico GMB - {empresa_nome}"
        
        corpo_admin = f"""
        Novo Lead Capturado no Site:

        Empresa: {empresa_nome}
        Score Obtido: {score}/100

        Dados do Cliente:
        - Nome: {nome_lead}
        - E-mail: {email_lead}
        - WhatsApp: {whatsapp_lead}
        """
        msg_admin.attach(MIMEText(corpo_admin, 'plain'))
        server.send_message(msg_admin)

        # 2. E-mail Limpo para o Cliente
        msg_cliente = MIMEMultipart()
        msg_cliente['From'] = SMTP_USER
        msg_cliente['To'] = email_lead
        msg_cliente['Subject'] = f"Diagnóstico de Perfil no Google - {empresa_nome}"
        
        corpo_texto_cliente = f"""
Olá, {nome_lead}!

Recebemos a sua solicitação de diagnóstico para a empresa "{empresa_nome}".

Pontuação de Otimização no Google Maps: {score}/100.

O nosso especialista em posicionamento digital da Tour360VR analisará os detalhes do seu perfil e entrará em contacto através do WhatsApp ({whatsapp_lead}) para apresentar o relatório completo.

Atenciosamente,
Rubens Okamoto | Tour360VR
www.tour360vr.com.br
        """
        msg_cliente.attach(MIMEText(corpo_texto_cliente, 'plain'))

        # Anexa PDF se o gerador estiver ativo
        pdf_bytes = gerar_pdf_diagnostico(empresa_nome, endereco, score, criterios)
        if pdf_bytes:
            part_pdf = MIMEBase('application', 'oct-stream')
            part_pdf.set_payload(pdf_bytes)
            encoders.encode_base64(part_pdf)
            part_pdf.add_header('Content-Disposition', f'attachment; filename="Diagnostico_GMB_{empresa_nome.replace(" ", "_")}.pdf"')
            msg_cliente.attach(part_pdf)

        server.send_message(msg_cliente)
        server.quit()
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

# Exibição dos Resultados Centralizados
if "resultado_busca" in st.session_state:
    dados = st.session_state["resultado_busca"]
    
    st.markdown("<hr style='margin: 0.8rem 0;'>", unsafe_allow_html=True)
    
    st.markdown(f'<div class="empresa-localizada-titulo">Empresa Localizada: {dados["nome"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #666666; font-size: 0.95rem; margin-bottom: 0.4rem;">📍 {dados["endereco"]}</p>', unsafe_allow_html=True)
    
    st.markdown('<p style="text-align: center; font-weight: 700; font-size: 1.1rem; margin-top: 0.6rem; margin-bottom: 0;">Pontuação Geral de Otimização</p>', unsafe_allow_html=True)
    
    # Exibição do Score Gigante
    st.markdown(f'<div class="nota-score-gigante">{dados["score"]} / 100</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="alerta-destaque">
        ⚠️ Identificamos oportunidades de melhoria que podem estar reduzindo a visibilidade do seu negócio para novos clientes.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="destaque-formulario-linha">Preencha os dados abaixo e receba a análise completa</div>', unsafe_allow_html=True)
    
    nome_lead = st.text_input("Nome:", placeholder="Digite o seu nome completo")
    email_lead = st.text_input("E-mail:", placeholder="exemplo@email.com")
    whats_num = st.text_input("WhatsApp (com DDD):", value="55 ", placeholder="5516991332121")

    if st.button("📩 Receber diagnóstico"):
        if nome_lead and email_lead and whats_num and len(whats_num.strip()) > 5:
            whats_limpo = ''.join(filter(str.isdigit, whats_num))
            if not whats_limpo.startswith("55"):
                whats_limpo = "55" + whats_limpo

            # Disparos de integração
            enviar_lead_bigin(nome_lead, email_lead, whats_limpo, dados['nome'], dados['score'])
            enviar_emails_diagnostico_completo(nome_lead, email_lead, whats_limpo, dados)
            
            st.markdown("""
            <div class="card-sucesso-destaque">
                ✅ Diagnóstico enviado com sucesso!
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Por favor, preencha todos os campos do formulário corretamente.")

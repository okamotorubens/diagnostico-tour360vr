import os
import re
import io
import requests
import smtplib
import tempfile
import streamlit as st

# Importações do ReportLab para Geração do PDF com Visual Profissional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ==========================================
# CONFIGURAÇÃO DE PÁGINA E TEMA STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Análise de Perfil no Google - Tour360VR",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilo CSS de Alta Precisão (Elimina Scrollbar, Oculta Rodapé e Padroniza Inputs)
custom_css = """
<style>
    /* 1. Eliminar Scrollbars Laterais e Margens Excessivas */
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

    /* 2. Ocultar absolutamente cabeçalhos, rodapés e 'Built with Streamlit' */
    footer, .stApp footer, [data-testid="stFooter"], header, #MainMenu, [data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0px !important;
    }

    /* 3. Títulos e Subtítulos */
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

    /* 4. Inputs com Fundo Branco Limpo e Texto Escuro */
    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 6px !important;
        font-size: 0.98rem !important;
        padding: 0.55rem 0.8rem !important;
        text-align: center !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #8DC63F !important;
        box-shadow: 0 0 4px rgba(141, 198, 63, 0.4) !important;
    }
    .stTextInput label {
        display: none !important;
    }

    /* Remoção do fundo escuro no autopreenchimento dos navegadores */
    input:-webkit-autofill,
    input:-webkit-autofill:hover, 
    input:-webkit-autofill:focus, 
    input:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 30px #FFFFFF inset !important;
        -webkit-text-fill-color: #111111 !important;
    }

    /* Rótulos Centralizados */
    .rotulo-campo {
        text-align: center !important;
        color: #111111 !important;
        font-size: 0.92rem !important;
        font-weight: 700 !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.1rem !important;
        font-family: 'Arial', sans-serif;
    }
    .subtexto-label {
        font-size: 0.78rem !important;
        color: #666666 !important;
        text-align: center !important;
        margin-bottom: 0.2rem !important;
    }

    /* 5. Botões Estilizados */
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
        box-shadow: 0 3px 8px rgba(141, 198, 63, 0.25) !important;
    }
    .stButton > button:hover {
        background-color: #7BB533 !important;
    }
    .stButton > button p {
        color: #FFFFFF !important;
        margin: 0 !important;
        font-weight: bold !important;
    }

    /* Card de Alerta e Mensagens */
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
        max-width: 480px !important;
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

def obter_cor_score(score):
    if score <= 40:
        return "#D32F2F"  # Vermelho
    elif score <= 70:
        return "#F57C00"  # Laranja / Amarelo
    else:
        return "#8DC63F"  # Verde

# ==========================================
# CONSULTA GOOGLE PLACES API (PRECISA)
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
                crit_det.append("Status Operacional: Ativo no Google Maps")

            rating = details.get("rating", 0)
            reviews = details.get("user_ratings_total", 0)
            if rating >= 4.7 and reviews >= 100:
                score += 20
                crit_det.append(f"Avaliações dos Clientes: Excelente ({rating}★ em {reviews} avaliações)")
            elif rating >= 4.0 and reviews >= 15:
                score += 10
                crit_det.append(f"Avaliações dos Clientes: Moderado ({rating}★ em {reviews} avaliações)")

            photos = details.get("photos", [])
            if len(photos) >= 30:
                score += 20
                crit_det.append("Galeria Visual: Galeria completa de fotos")
            elif len(photos) >= 5:
                score += 10
                crit_det.append("Galeria Visual: Galeria parcial cadastrada")

            if details.get("formatted_phone_number"):
                score += 10
                crit_det.append("Contato: Telefone principal cadastrado")

            website = details.get("website", "")
            if website and not any(x in website for x in ["facebook", "instagram", "site.google"]):
                score += 15
                crit_det.append("Website: Domínio próprio vinculado")

            if details.get("opening_hours"):
                score += 10
                crit_det.append("Horários de Funcionamento: Ativos e configurados")

            addr = details.get("formatted_address", "")
            if addr and any(char.isdigit() for char in addr):
                score += 10
                crit_det.append("Endereço Físico: Endereço completo verificado")

            if details.get("types"):
                score += 5
                crit_det.append("Categorias de Negócio: Categoria definida")

            return {
                "sucesso": True,
                "place_id": place_id,
                "nome": details.get("name"),
                "endereco": details.get("formatted_address", "Endereço registrado no Google Maps"),
                "score": min(score, 100),
                "criterios": crit_det
            }
    except Exception as e:
        print(f"Erro na consulta do Google Places: {e}")
        
    return {"sucesso": False, "mensagem": "Empresa não encontrada no Google."}

# ==========================================
# GERADOR DE PDF PROFISSIONAL (REPORTLAB)
# ==========================================
def gerar_pdf_diagnostico_arquivo(empresa_nome, endereco, score, criterios):
    try:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"Diagnostico_{re.sub(r'[^a-zA-Z0-9]', '_', empresa_nome)}.pdf")
        
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        style_header = ParagraphStyle('HeaderPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#1565C0'))
        style_sub = ParagraphStyle('SubPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=colors.HexColor('#222222'))
        style_text = ParagraphStyle('TextPDF', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=colors.HexColor('#444444'))
        
        elements = []
        
        # Cabeçalho da Empresa
        elements.append(Paragraph("TOUR360VR • SOLUÇÕES EM PRESENÇA DIGITAL E FOTO 360°", style_header))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1565C0'), spaceBefore=8, spaceAfter=12))
        
        # Dados da Consulta
        elements.append(Paragraph(f"<b>Relatório de Diagnóstico do Perfil Google</b>", style_sub))
        elements.append(Paragraph(f"<b>Empresa Analisada:</b> {empresa_nome}", style_text))
        elements.append(Paragraph(f"<b>Endereço:</b> {endereco}", style_text))
        elements.append(Spacer(1, 14))
        
        # Bloco da Nota do Score
        cor_score_hex = obter_cor_score(score)
        elements.append(Paragraph(f"PONTUAÇÃO GERAL DE OTIMIZAÇÃO: <font color='{cor_score_hex}'><b>{score} / 100</b></font>", ParagraphStyle('ScorePDF', parent=style_header, fontSize=15)))
        elements.append(Spacer(1, 10))
        
        # Tabela de Critérios
        elements.append(Paragraph("<b>Detalhamento da Pontuação e Requisitos Verificados:</b>", style_sub))
        elements.append(Spacer(1, 6))
        
        tabela_dados = [["Requisito Avaliado", "Status no Perfil Google"]]
        for item in criterios:
            partes = item.split(":")
            col1 = partes[0] if len(partes) > 0 else item
            col2 = partes[1] if len(partes) > 1 else "Conforme"
            tabela_dados.append([col1, col2])
            
        t = Table(tabela_dados, colWidths=[260, 260])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')])
        ]))
        elements.append(t)
        
        elements.append(Spacer(1, 16))
        elements.append(Paragraph("<b>Recomendações Estratégicas:</b>", style_sub))
        elements.append(Paragraph("Para otimizar a pontuação em 100% e conquistar as primeiras posições nas pesquisas locais do Google Maps e Busca, recomenda-se a inclusão de um <b>Tour Virtual 360° Interativo homologado no Google Street View</b> e a atualização visual contínua.", style_text))
        
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CCCCCC'), spaceBefore=5, spaceAfter=8))
        elements.append(Paragraph("Tour360VR • Rubens Okamoto | contato@tour360vr.com.br | www.tour360vr.com.br", ParagraphStyle('Foot', parent=style_text, fontSize=8, alignment=1)))
        
        doc.build(elements)
        return file_path
    except Exception as e:
        print(f"Erro na construção do PDF com ReportLab: {e}")
        return None

# ==========================================
# ENVIO INTEGRADO ZOHO BIGIN CRM
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
                    "Last_Name": nome_lead,
                    "Email": email_lead,
                    "Phone": whatsapp_lead,
                    "Description": f"Lead do Diagnóstico de Perfil:\nEmpresa: {empresa_consultada}\nScore: {score}/100\nWhatsApp: {whatsapp_lead}"
                }
            ]
        }

        url_contact = "https://www.zohoapis.com/bigin/v1/Contacts"
        res_contact = requests.post(url_contact, json=payload, headers=headers, timeout=8)
        return res_contact.status_code in [200, 201]
    except Exception as e:
        print(f"Erro ao enviar lead para o Zoho Bigin: {e}")
        return False

# ==========================================
# DISPARO DE E-MAILS VIA SMTP COM ANEXO
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

        # 1. E-mail Notificação Interna
        msg_admin = MIMEMultipart('mixed')
        msg_admin['From'] = SMTP_USER
        msg_admin['To'] = SMTP_USER
        msg_admin['Subject'] = f"🚀 NOVO LEAD: {empresa_nome} (Score: {score}/100)"
        
        corpo_admin_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #F4F4F4; padding: 20px;">
            <div style="max-width: 600px; background-color: #FFFFFF; padding: 25px; border-radius: 8px; border-top: 5px solid #1E88E5; margin: 0 auto;">
                <h2 style="color: #333333; margin-top: 0;">Novo Lead Capturado no Site!</h2>
                <hr style="border: 0; border-top: 1px solid #EEEEEE;">
                <p><b>Empresa Consultada:</b> {empresa_nome}</p>
                <p><b>Pontuação Obtida:</b> <span style="font-size: 1.2rem; color: {cor_score_hex}; font-weight: bold;">{score} / 100</span></p>
                <div style="background-color: #F8F9FA; padding: 15px; border-radius: 6px; border-left: 4px solid #1E88E5; margin: 15px 0;">
                    <p style="margin: 4px 0;"><b>Nome:</b> {nome_lead}</p>
                    <p style="margin: 4px 0;"><b>E-mail:</b> <a href="mailto:{email_lead}">{email_lead}</a></p>
                    <p style="margin: 4px 0;"><b>WhatsApp:</b> <a href="https://wa.me/{whatsapp_lead}" target="_blank">+{whatsapp_lead}</a></p>
                </div>
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
                p_admin.add_header('Content-Disposition', f'attachment; filename="Diagnostico_{re.sub(r"[^a-zA-Z0-9]", "_", empresa_nome)}.pdf"')
                msg_admin.attach(p_admin)

        server.send_message(msg_admin)

        # 2. E-mail Cliente com o Relatório
        msg_cliente = MIMEMultipart('mixed')
        msg_cliente['From'] = SMTP_USER
        msg_cliente['To'] = email_lead
        msg_cliente['Subject'] = f"Diagnóstico de Perfil no Google - {empresa_nome}"
        
        corpo_html_cliente = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6;">
            <p>Olá, <b>{nome_lead}</b>!</p>
            <p>Recebemos a sua solicitação de diagnóstico para a empresa <b>{empresa_nome}</b>.</p>
            <p>Sua pontuação de otimização atual no Google é: <b style="font-size: 1.2rem; color: {cor_score_hex};">{score}/100</b>.</p>
            <p>Anexamos a este e-mail o seu relatório em PDF detalhado com os pontos analisados.</p>
            <p>Nossos especialistas em presença digital entrarão em contato via WhatsApp para apresentar como atingir a nota máxima e alavancar seus resultados locais.</p>
            <br>
            <p>Atenciosamente,<br><b>Rubens Okamoto | Tour360VR</b><br>www.tour360vr.com.br</p>
        </body>
        </html>
        """
        msg_cliente.attach(MIMEText(corpo_html_cliente, 'html'))

        if pdf_file_path and os.path.exists(pdf_file_path):
            with open(pdf_file_path, 'rb') as f:
                p_cliente = MIMEBase('application', 'pdf')
                p_cliente.set_payload(f.read())
                encoders.encode_base64(p_cliente)
                p_cliente.add_header('Content-Disposition', f'attachment; filename="Diagnostico_Google_{re.sub(r"[^a-zA-Z0-9]", "_", empresa_nome)}.pdf"')
                msg_cliente.attach(p_cliente)

        server.send_message(msg_cliente)
        server.quit()
        
        if pdf_file_path and os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)

        return True
    except Exception as e:
        print(f"Erro na rotina de envio de e-mails: {e}")
        return False

# ==========================================
# INTERFACE PRINCIPAL
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

# Card de Exibição de Resultado
if "resultado_busca" in st.session_state:
    dados = st.session_state["resultado_busca"]
    cor_nota = obter_cor_score(dados["score"])
    
    html_card_resultado = f"""
    <div style="background-color: #F0F4F8 !important; border: 1px solid #D0D7DE !important; border-radius: 10px !important; padding: 18px !important; margin: 1rem auto !important; max-width: 600px !important;">
        <div style="text-align: center; color: #111111; font-size: 1.25rem; font-weight: 800; margin-bottom: 0.1rem;">Empresa Localizada: {dados["nome"]}</div>
        <p style="text-align: center; color: #666666; font-size: 0.9rem; margin-bottom: 0.4rem;">📍 {dados["endereco"]}</p>
        <p style="text-align: center; font-weight: 700; font-size: 1.05rem; margin-top: 0.5rem; margin-bottom: 0;">Pontuação Geral de Otimização</p>
        <div style="text-align: center; font-size: 3.2rem; font-weight: 900; line-height: 1; margin: 0.3rem 0 0.8rem 0; color: {cor_nota} !important;">{dados["score"]} / 100</div>
        <div style="background-color: #FFFDE7; border: 1.5px solid #FBC02D; border-radius: 6px; padding: 8px 12px; text-align: center; color: #5D4037; font-size: 0.9rem; font-weight: 600;">
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
    
    # Campo com Bloqueio Numérico
    raw_whats = st.text_input("WhatsInput", value="", max_chars=11, placeholder="16991332121", label_visibility="collapsed")

    # Injeção JavaScript de Segurança no DOM para Filtrar Letras Instantaneamente
    js_filtro_numerico = """
    <script>
        const inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(input => {
            if (input.placeholder === "16991332121") {
                input.addEventListener('input', function(e) {
                    this.value = this.value.replace(/[^0-9]/g, '');
                });
            }
        });
    </script>
    """
    st.components.v1.html(js_filtro_numerico, height=0, width=0)

    if st.button("📩 Receber diagnóstico"):
        apenas_numeros = re.sub(r'\D', '', raw_whats)
        
        if not nome_lead or len(nome_lead.strip()) < 2:
            st.error("Por favor, informe seu nome completo.")
        elif not email_lead or "@" not in email_lead:
            st.error("Por favor, informe um endereço de e-mail válido.")
        elif len(apenas_numeros) != 11:
            st.error("❌ O campo WhatsApp deve conter exatamente 11 NÚMEROS (DDD + Celular, ex: 16991332121).")
        else:
            whats_completo = "55" + apenas_numeros

            # 1. Registro no Bigin CRM
            enviar_lead_bigin(nome_lead, email_lead, whats_completo, dados['nome'], dados['score'])
            
            # 2. Disparo de E-mail com PDF
            com_sucesso = enviar_emails_diagnostico_completo(nome_lead, email_lead, whats_completo, dados)
            
            if com_sucesso:
                st.markdown("""
                <div class="card-sucesso-destaque">
                    ✅ Diagnóstico enviado com sucesso! Verifique sua caixa de entrada e spam.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Ocorreu uma falha ao disparar o e-mail. Tente novamente em instantes.")

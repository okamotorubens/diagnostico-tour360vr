import streamlit as st
import time
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage, KeepTogether
from reportlab.pdfgen import canvas
import io
import os
import re
from datetime import datetime
from PIL import Image as PILImage
import smtplib
import urllib.request
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def fmt_brl(val):
    s = f"{val:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

# Função para converter número em valor por extenso simples para moeda
def valor_por_extenso(v):
    # Função auxiliar básica para compor o extenso do valor em Reais
    try:
        inteiro = int(v)
        centavos = int(round((v - inteiro) * 100))
        
        # Para simplificar e garantir precisão nos valores comuns de propostas fotográficas:
        # Vamos usar a biblioteca num2words se houver ou um conversor interno robusto.
        # Caso prefira direto, podemos gerar via regra padrão:
        unidades = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze", "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
        dezenas = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
        centenas = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos"]

        def extenso_ate_999(n):
            if n == 0: return ""
            if n == 100: return "cem"
            c = n // 100
            d = (n % 100) // 10
            u = n % 10
            res = []
            if c > 0: res.append(centenas[c])
            if n % 100 < 20 and n % 100 > 0:
                res.append(unidades[n % 100])
            else:
                if d > 0: res.append(dezenas[d])
                if u > 0: res.append(unidades[u])
            return " e ".join([r for r in res if r])

        if inteiro == 0:
            str_int = "zero reais"
        elif inteiro == 1:
            str_int = "um real"
        else:
            milhar = inteiro // 1000
            resto = inteiro % 1000
            partes = []
            if milhar > 0:
                if milhar == 1: partes.append("mil")
                else: partes.append(extenso_ate_999(milhar) + " mil")
            if resto > 0:
                partes.append(extenso_ate_999(resto))
            str_int = " e ".join(partes) + " reais"
            
        if centavos > 0:
            str_cent = f" e {extenso_ate_999(centavos)} centavos"
            return f"({str_int.capitalize()}{str_cent})"
        else:
            return f"({str_int.capitalize()})"
    except Exception:
        return ""

MESES_PT = {
    1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
    5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
    9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
}

TABELAS_SERVICOS = {
    "Evento social": {1: 180.0, 2: 350.0, 3: 450.0, 4: 600.0, 5: 750.0, 6: 900.0, 7: 1000.0, 8: 1100.0, 9: 1200.0, 10: 1300.0, 11: 1400.0, 12: 1500.0},
    "Evento Corporativo": {1: 180.0, 2: 350.0, 3: 450.0, 4: 600.0, 5: 750.0, 6: 900.0, 7: 1000.0, 8: 1100.0, 9: 1200.0, 10: 1300.0, 11: 1400.0, 12: 1500.0},
    "Aniversário infantil": {1: 200.0, 2: 400.0, 3: 600.0, 4: 800.0, 5: 900.0},
    "Aniversário": {1: 180.0, 2: 350.0, 3: 450.0, 4: 600.0, 5: 750.0, 6: 900.0, 7: 1000.0, 8: 1100.0, 9: 1200.0, 10: 1300.0, 11: 1400.0, 12: 1500.0},
    "Retrato Corporativo": {1: 250.0, 2: 500.0, 3: 700.0, 4: 850.0, 5: 1000.0},
    "Institucional": {1: 180.0, 2: 350.0, 3: 450.0, 4: 600.0, 5: 750.0, 6: 900.0, 7: 1000.0, 8: 1100.0, 9: 1200.0, 10: 1300.0, 11: 1400.0, 12: 1500.0},
    "Ações de Marketing": {1: 180.0, 2: 350.0, 3: 450.0, 4: 600.0, 5: 750.0, 6: 900.0, 7: 1000.0, 8: 1100.0, 9: 1200.0, 10: 1300.0, 11: 1400.0, 12: 1500.0},
    "Outro": {1: 180.0, 2: 350.0, 3: 450.0, 4: 600.0, 5: 750.0, 6: 900.0, 7: 1000.0, 8: 1100.0, 9: 1200.0, 10: 1300.0, 11: 1400.0, 12: 1500.0}
}

OPCOES_CARGA_HORARIA = [
    "1h", "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "10h", "11h", "12h",
    "1 diária", "2 diárias", "3 diárias", "4 diárias", "5 diárias"
]

ESTADOS_BR = [
    "SP", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", 
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SE", "TO"
]

SMTP_SERVER = "smtp.tour360vr.com.br"
SMTP_PORT_SSL = 465
SMTP_USER = "contato@tour360vr.com.br"
SMTP_PASS = "Kakaroto@2026"

st.set_page_config(page_title="Proposta Comercial & Custos - Okamoto Mídias Visuais", page_icon="📊", layout="wide")

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            max-width: 80rem;
        }
        div[data-baseweb="input"] {
            max-width: 100%;
        }
        [data-testid="stNumberInput"] input {
            text-align: center;
        }
        /* Correção definitiva para exibir a logo inteira sem cortes na tela */
        [data-testid="stImage"] {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        [data-testid="stImage"] > img {
            max-width: 100% !important;
            height: auto !important;
            object-fit: contain !important;
        }
    </style>
""", unsafe_allow_html=True)

def scroll_to_top():
    st.markdown("""
        <script>
            window.scrollTo({top: 0, behavior: 'smooth'});
            parent.window.scrollTo({top: 0, behavior: 'smooth'});
        </script>
    """, unsafe_allow_html=True)

def calcular_distancia_maps(destino_endereco):
    try:
        api_key = st.secrets.get("google", {}).get("maps_api_key", "")
        if not api_key:
            return None
        origem = "Rua Manoel Achê, 327, Ribeirão Preto - SP"
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={urllib.parse.quote(origem)}&destinations={urllib.parse.quote(destino_endereco)}&key={api_key}&language=pt-BR"
        
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode('utf-8'))
        
        if data['status'] == 'OK':
            elemento = data['rows'][0]['elements'][0]
            if elemento['status'] == 'OK':
                distancia_metros = elemento['distance']['value']
                distancia_km_ida = distancia_metros / 1000.0
                distancia_ida_volta = distancia_km_ida * 2
                return round(distancia_ida_volta)
    except Exception:
        pass
    return None

class NumberedCanvasProposal(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer_content(num_pages)
            super().showPage()
        super().save()

    def draw_footer_content(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#475569'))
        
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(40, 40, 555, 40)
        
        p_num = self._pageNumber
        page_str = f"{p_num:02d} de {page_count:02d}"
        
        footer_text = "okamotomidiasvisuais.com.br  |  contato@okamotomidiasvisuais.com.br  |  16 99133 2121"
        self.drawCentredString(297.5, 26, footer_text)
        
        self.drawRightString(555, 26, page_str)
        self.restoreState()

class SimpleCanvasInternal(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def showPage(self):
        self.draw_footer_content()
        super().showPage()

    def save(self):
        super().save()

    def draw_footer_content(self):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#475569'))
        
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(35, 35, 575, 35)
        
        footer_text = "okamotomidiasvisuais.com.br  |  contato@okamotomidiasvisuais.com.br  |  16 99133 2121"
        self.drawCentredString(297.6, 22, footer_text)
        self.restoreState()

def get_logo_app_path():
    caminho = "logo_okamoto.png"
    if not os.path.exists(caminho):
        caminho = "okamoto_black.png"
    return caminho if os.path.exists(caminho) else None

def get_logo_pdf_path():
    caminho = "okamoto_black.png"
    if not os.path.exists(caminho):
        caminho = "logo_okamoto.png"
    return caminho if os.path.exists(caminho) else None

def criar_imagem_proporcional(path, target_width=150):
    try:
        im = PILImage.open(path)
        orig_w, orig_h = im.size
        target_height = int(target_width * (orig_h / orig_w))
        return RLImage(path, width=target_width, height=target_height)
    except Exception:
        return RLImage(path, width=150, height=44)

def enviar_pdf_por_email(pdf_cliente_bytes, pdf_interno_bytes, nome_cliente, nome_servico):
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT_SSL, timeout=15)
        server.login(SMTP_USER, SMTP_PASS)

        safe_name = "".join([c for c in nome_cliente if c.isalnum() or c in (' ', '_', '-')]).strip().replace(' ', '_') if nome_cliente else "Cliente"
        
        msg = MIMEMultipart('mixed')
        msg['From'] = f"Okamoto Mídias Visuais <{SMTP_USER}>"
        msg['To'] = SMTP_USER
        msg['Reply-To'] = SMTP_USER
        msg['Subject'] = f"📊 Novo Orçamento Gerado - {nome_servico} ({safe_name})"

        corpo_html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: Arial, sans-serif; background-color: #F4F6F9; padding: 15px; margin: 0;">
            <div style="max-width: 580px; background-color: #FFFFFF; padding: 20px; border-radius: 10px; border-top: 5px solid #1565C0; margin: 0 auto;">
                <h2 style="color: #111111; margin-top: 0; font-size: 18px;">Novo Orçamento Gerado no Sistema!</h2>
                <hr style="border: 0; border-top: 1px solid #EEEEEE; margin: 12px 0;">
                <p style="font-size: 14px; margin: 4px 0;"><b>Cliente / Empresa:</b> {nome_cliente}</p>
                <p style="font-size: 14px; margin: 4px 0;"><b>Serviço:</b> {nome_servico}</p>
                <p style="font-size: 14px; margin: 12px 0; color: #555;">Os arquivos em PDF (Proposta Comercial e Relatório Interno de Custos) seguem anexados a este e-mail.</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(corpo_html, 'html', 'utf-8'))

        part_cliente = MIMEApplication(pdf_cliente_bytes.getvalue(), _subtype="pdf")
        part_cliente.add_header('Content-Disposition', 'attachment', filename=f"Proposta_Comercial_{safe_name}.pdf")
        msg.attach(part_cliente)

        part_interno = MIMEApplication(pdf_interno_bytes.getvalue(), _subtype="pdf")
        part_interno.add_header('Content-Disposition', 'attachment', filename=f"Relatorio_Interno_Custos_{safe_name}.pdf")
        msg.attach(part_interno)

        server.send_message(msg)
        server.quit()
        return True, "Sucesso"
    except Exception as e:
        return False, str(e)

def gerar_pdf_cliente(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=15, bottomMargin=50)
    
    servico_nome = dados['tipo_servico'] if dados['tipo_servico'] != "Outro" else dados['outro_servico_nome']
    nome_serv_ev = dados['nome_servico_input'] if dados['nome_servico_input'] else servico_nome
    data_ev_str = dados['data_evento'].strftime('%d/%m/%Y')
    
    doc.title = f"Proposta comercial - {nome_serv_ev} - {data_ev_str}"
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('TituloPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, alignment=1, textColor=colors.HexColor('#0f172a'))
    style_servico_sub = ParagraphStyle('ServSubPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=1, textColor=colors.HexColor('#1e3a8a'))
    style_corpo = ParagraphStyle('CorpoPDF', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('BoldPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#0f172a'))
    style_cat_titulo = ParagraphStyle('CatTitPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=colors.HexColor('#0f172a'))
    style_destaque_1 = ParagraphStyle('Dest1PDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=17, alignment=1, textColor=colors.HexColor('#0f172a'))
    style_destaque_2 = ParagraphStyle('Dest2PDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, alignment=1, textColor=colors.HexColor('#334155'))
    
    story = []

    logo_path = get_logo_pdf_path()
    if logo_path:
        img = criar_imagem_proporcional(logo_path, target_width=170)
        img.hAlign = 'CENTER'
        story.append(img)
    else:
        story.append(Paragraph("<b>[ OKAMOTO MÍDIAS VISUAIS ]</b>", style_titulo))
    
    story.append(Spacer(1, 6))
    
    t_linha = Table([['']], colWidths=[515], rowHeights=[1])
    t_linha.hAlign = 'CENTER'
    t_linha.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.75, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_linha)
    story.append(Spacer(1, 8))
    
    d_orc = dados['data_orcamento']
    data_extenso = f"Ribeirão Preto, {d_orc.day} de {MESES_PT[d_orc.month]} de {d_orc.year}"
    story.append(Paragraph(data_extenso, style_corpo))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("Proposta Comercial", style_titulo))
    story.append(Spacer(1, 3))
    story.append(Paragraph(f"{nome_serv_ev}", style_servico_sub))
    story.append(Spacer(1, 10))
    
    # Itens 1 a 9 estritamente um abaixo do outro
    story.append(Paragraph("<b>1. Dados do cliente:</b>", style_bold))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"<b>Contato:</b> {dados['contato']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Empresa:</b> {dados['empresa']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Telefone:</b> {dados['telefone']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>E-mail:</b> {dados['email']}", style_corpo))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>2. Dados do serviço:</b>", style_bold))
    story.append(Spacer(1, 2))
    data_evento_str = dados['data_evento'].strftime('%d/%m/%Y')
    if dados['tem_data_termino']:
        data_evento_str += f" até {dados['data_termino'].strftime('%d/%m/%Y')}"
    horario_txt = f"&nbsp;&nbsp; <b>Horário:</b> {dados['horario']}" if dados['horario'] else ""
    local_txt = dados['local'] if dados['local'] else "Local a definir"
    story.append(Paragraph(f"<b>Data:</b> {data_evento_str}{horario_txt} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Local:</b> {local_txt} — {dados['cidade']}/{dados['estado']}", style_corpo))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>3. Escopo do serviço:</b>", style_bold))
    story.append(Spacer(1, 2))
    story.append(Paragraph(dados['escopo_servico'].replace('\n', '<br/>'), style_corpo))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>4. Captação:</b>", style_bold))
    story.append(Spacer(1, 2))
    story.append(Paragraph(dados['captacao'].replace('\n', '<br/>'), style_corpo))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>5. Entrega:</b>", style_bold))
    story.append(Spacer(1, 2))
    story.append(Paragraph("Até 72h após o término do serviço, editado e enviado via link para download, em alta e baixa resolução, disponível por 30 dias.", style_corpo))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>6. Forma de pagamento:</b>", style_bold))
    story.append(Spacer(1, 2))
    story.append(Paragraph(dados['forma_pagamento_tipo'], style_corpo))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>7. Condições:</b>", style_bold))
    story.append(Spacer(1, 2))
    story.append(Paragraph(dados['condicao_pagamento'], style_corpo))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>8. Validade:</b>", style_bold))
    story.append(Spacer(1, 2))
    story.append(Paragraph(dados['validade_orcamento'], style_corpo))
    story.append(Spacer(1, 10))
    
    # 9. Valor total de investimento com valor por extenso na linha de baixo
    val_fmt = fmt_brl(dados['valor_final'])
    extenso_fmt = valor_por_extenso(dados['valor_final'])
    
    texto_valor = f"<b>9. VALOR TOTAL DE INVESTIMENTO:</b> {val_fmt}"
    if extenso_fmt:
        texto_valor += f"<br/><font size=9 color='#475569'><i>{extenso_fmt}</i></font>"
        
    p_valor = Paragraph(texto_valor, ParagraphStyle('ValBox', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, alignment=1, textColor=colors.HexColor('#1e3a8a')))
    t_valor_box = Table([[p_valor]], colWidths=[420])
    t_valor_box.hAlign = 'CENTER'
    t_valor_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1e3a8a')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    
    bloco_final_p1 = KeepTogether([
        t_valor_box,
        Spacer(1, 12),
        Paragraph("Ficamos à disposição para quaisquer esclarecimentos e ajustes, caso necessário.", style_corpo),
        Spacer(1, 8),
        Paragraph("Atenciosamente, &nbsp; <b>Rubens Okamoto</b> (Okamoto Mídias Visuais)", style_corpo)
    ])
    story.append(bloco_final_p1)
    story.append(PageBreak())
    
    if logo_path:
        img_inst = criar_imagem_proporcional(logo_path, target_width=180)
        img_inst.hAlign = 'CENTER'
        story.append(img_inst)
    else:
        story.append(Paragraph("<b>[ OKAMOTO MÍDIAS VISUAIS ]</b>", style_titulo))
        
    story.append(Spacer(1, 8))
    t_linha_p2 = Table([['']], colWidths=[515], rowHeights=[1])
    t_linha_p2.hAlign = 'CENTER'
    t_linha_p2.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.75, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_linha_p2)
    
    story.append(Spacer(1, 24))
    story.append(Paragraph("É registrando a sua história, que nós construímos a nossa!", style_destaque_1))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Especialistas em Imagem, Vídeo e Experiências Imersivas", style_destaque_2))
    story.append(Spacer(1, 18))
    
    story.append(Spacer(1, 12))
    intro_inst = "Unimos a bagagem de três décadas às inovações tecnológicas mais recentes, transformando sua marca com soluções visuais de alta performance:"
    story.append(Paragraph(intro_inst, style_corpo))
    story.append(Spacer(1, 14))
    
    topicos_inst = "<b>• Fotografia Corporativa e Estratégica:</b><br/>Imagens que reforçam a autoridade da sua empresa e destacam seu negócio no mercado.<br/><br/><b>• Tours Virtuais 360º:</b><br/>Experiências imersivas que levam seu cliente para dentro do seu espaço físico.<br/><br/><b>• Vídeos de Alto Impacto:</b><br/>Produções pensadas para converter e engajar seu público em redes sociais e plataformas digitais."
    story.append(Paragraph(topicos_inst, style_corpo))
    story.append(Spacer(1, 24))
    
    style_dados_normal = ParagraphStyle('DadosNormais', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=15, textColor=colors.HexColor('#334155'))
    
    bloco_dados_institucionais = KeepTogether([
        Spacer(1, 12),
        Paragraph("Dados da Empresa", style_cat_titulo),
        Spacer(1, 4),
        Paragraph("Okamoto Reportagens Fotográficas SS Ltda<br/>CNPJ: 04.824.331/0001-05<br/>Rua General Carneiro, 860 — Centro, Brodowski - SP<br/>CEP: 14.340-023", style_dados_normal),
        Spacer(1, 14),
        Paragraph("Dados Pessoais", style_cat_titulo),
        Spacer(1, 4),
        Paragraph("Rubens Heigasi Okamoto<br/>CPF: 287.932.298-79<br/>RG: 25.450.624-0 SSP/SP<br/>Tel. Cel.: 16 99133 2121<br/>E-mail: contato@okamotomidiasvisuais.com.br", style_dados_normal),
        Spacer(1, 14),
        Paragraph("Dados Bancários", style_cat_titulo),
        Spacer(1, 4),
        Paragraph("Banco do Brasil<br/>Agência: 3235-2<br/>C. Corrente: 11.935-0<br/>Chave PIX: 04824331000105", style_dados_normal)
    ])
    story.append(bloco_dados_institucionais)

    doc.build(story, canvasmaker=NumberedCanvasProposal)
    buffer.seek(0)
    return buffer

def gerar_pdf_interno(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=15, bottomMargin=35)
    
    servico_exibido = dados['tipo_servico'] if dados['tipo_servico'] != "Outro" else dados['outro_servico_nome']
    nome_serv_ev = dados['nome_servico_input'] if dados['nome_servico_input'] else servico_exibido
    data_ev_str = dados['data_evento'].strftime('%d/%m/%Y')
    
    doc.title = f"Relatório de custos - {nome_serv_ev} - {data_ev_str}"
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('TitInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=18, alignment=0, textColor=colors.HexColor('#0f172a'))
    style_subtitulo_serv = ParagraphStyle('SubServInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=0, textColor=colors.HexColor('#1e3a8a'))
    style_data_criacao = ParagraphStyle('DataCriacaoInt', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=11, alignment=0, textColor=colors.HexColor('#64748b'))
    style_secao = ParagraphStyle('SecInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=12, alignment=0, textColor=colors.HexColor('#1e3a8a'))
    style_corpo = ParagraphStyle('CorpoInt', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=11, textColor=colors.HexColor('#000000'))
    style_bold = ParagraphStyle('BoldInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.HexColor('#000000'))
    
    story = []

    logo_path = get_logo_pdf_path()
    data_criacao_str = dados['data_orcamento'].strftime('%d/%m/%Y')
    
    # Alinhamento estrito da logo à esquerda no relatório interno de custos
    if logo_path:
        img_int = criar_imagem_proporcional(logo_path, target_width=120)
        img_int.hAlign = 'LEFT'
        
        col_cab_esq = img_int
        col_cab_dir = [
            Paragraph("Relatório de Custos", style_titulo),
            Spacer(1, 2),
            Paragraph(f"{nome_serv_ev}", style_subtitulo_serv),
            Spacer(1, 2),
            Paragraph(f"Data de criação: {data_criacao_str}", style_data_criacao)
        ]
        
        t_cabecalho = Table([[col_cab_esq, col_cab_dir]], colWidths=[130, 410])
        t_cabecalho.hAlign = 'LEFT'
        t_cabecalho.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('ALIGN', (0,0), (0,0), 'LEFT'),
        ]))
        story.append(t_cabecalho)
    else:
        story.append(Paragraph("<b>[ LOGO OKAMOTO ]</b>", style_bold))
        story.append(Spacer(1, 4))
        story.append(Paragraph("Relatório de Custos", style_titulo))
        story.append(Paragraph(f"{nome_serv_ev}", style_subtitulo_serv))
        story.append(Paragraph(f"Data de criação: {data_criacao_str}", style_data_criacao))
        
    story.append(Spacer(1, 6))
    
    t_linha_int = Table([['']], colWidths=[540], rowHeights=[1])
    t_linha_int.hAlign = 'LEFT'
    t_linha_int.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.75, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_linha_int)
    story.append(Spacer(1, 10))
    
    data_fim_str = dados['data_termino'].strftime('%d/%m/%Y') if dados['tem_data_termino'] else data_ev_str
    local_txt = dados['local'] if dados['local'] else "Local a definir"
    
    story.append(Spacer(1, 6))
    
    info_geral = [
        [Paragraph("<b>Cliente:</b>", style_bold), Paragraph(dados['contato'], style_corpo), Paragraph("<b>Data de Início:</b>", style_bold), Paragraph(data_ev_str, style_corpo)],
        [Paragraph("<b>Serviço:</b>", style_bold), Paragraph(f"{nome_serv_ev}", style_corpo), Paragraph("<b>Data de Término:</b>", style_bold), Paragraph(data_fim_str, style_corpo)],
        [Paragraph("<b>Carga Horária:</b>", style_bold), Paragraph(dados['carga_horaria_sel'], style_corpo), Paragraph("<b>Prazo Pagamento:</b>", style_bold), Paragraph(f"{dados.get('prazo_pagamento_dias', '5')} dias", style_corpo)],
        [Paragraph("<b>Local:</b>", style_bold), Paragraph(f"{local_txt} — {dados['cidade']}/{dados['estado']}", style_corpo), Paragraph("", style_corpo), Paragraph("", style_corpo)]
    ]
    t_geral = Table(info_geral, colWidths=[80, 190, 95, 175])
    t_geral.hAlign = 'LEFT'
    t_geral.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
        ('BOTTOMPADDING', (0,0), (-1,-1), 2), 
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('SPAN', (1, 3), (3, 3))
    ]))
    story.append(t_geral)
    
    story.append(Spacer(1, 18))
    
    story.append(Paragraph("1. Custos de Logística, Deslocamento & Operacionais", style_secao))
    story.append(Spacer(1, 4))
    
    combustivel_detalhe = f"Consumo: {dados['consumo_veiculo']} km/L | {dados['litros_gastos']:.1f}L a {fmt_brl(dados['preco_combustivel'])}/L"
    custo_logistica_parcial = dados['custo_combustivel'] + dados['pedagios'] + dados['custo_estacionamento'] + dados['custo_hospedagem_total'] + dados['custo_almoco'] + dados['custo_jantar'] + dados['custo_freelancer'] + dados['custo_outros']
    
    tabela_log_dados = [
        [Paragraph("<b>Parâmetro</b>", style_bold), Paragraph("<b>Detalhe / Métrica</b>", style_bold), Paragraph("<b>Custo Parcial</b>", style_bold)],
        [Paragraph("Distância Total", style_corpo), Paragraph(f"{dados['distancia']} km (Ida e Volta)", style_corpo), Paragraph("-", style_corpo)],
        [Paragraph("Combustível", style_corpo), Paragraph(combustivel_detalhe, style_corpo), Paragraph(fmt_brl(dados['custo_combustivel']), style_corpo)],
        [Paragraph("Pedágios", style_corpo), Paragraph("Tarifas de estrada", style_corpo), Paragraph(fmt_brl(dados['pedagios']), style_corpo)],
        [Paragraph("Estacionamento", style_corpo), Paragraph("Estacionamento / Local", style_corpo), Paragraph(fmt_brl(dados['custo_estacionamento']), style_corpo)],
        [Paragraph("Hospedagem", style_corpo), Paragraph("Diárias de hospedagem", style_corpo), Paragraph(fmt_brl(dados['custo_hospedagem_total']), style_corpo)],
        [Paragraph("Almoço", style_corpo), Paragraph("Refeição", style_corpo), Paragraph(fmt_brl(dados['custo_almoco']), style_corpo)],
        [Paragraph("Jantar", style_corpo), Paragraph("Refeição", style_corpo), Paragraph(fmt_brl(dados['custo_jantar']), style_corpo)],
        [Paragraph("Freelancer", style_corpo), Paragraph("Apoio profissional extra", style_corpo), Paragraph(fmt_brl(dados['custo_freelancer']), style_corpo)],
        [Paragraph("Outros", style_corpo), Paragraph("Despesas diversas", style_corpo), Paragraph(fmt_brl(dados['custo_outros']), style_corpo)],
        [Paragraph("<b>TOTAL LOGÍSTICA & OPERACIONAL</b>", style_bold), Paragraph("", style_corpo), Paragraph(f"<b>{fmt_brl(custo_logistica_parcial)}</b>", style_bold)]
    ]
    t_log = Table(tabela_log_dados, colWidths=[130, 270, 140])
    t_log.hAlign = 'LEFT'
    ts_log = TableStyle()
    ts_log.add('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9'))
    ts_log.add('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e2e8f0'))
    ts_log.add('ALIGN', (0,0), (-1,-1), 'LEFT')
    ts_log.add('ALIGN', (2,0), (2,-1), 'RIGHT')
    ts_log.add('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ts_log.add('BOTTOMPADDING', (0,0), (-1,-1), 2)
    ts_log.add('TOPPADDING', (0,0), (-1,-1), 2)
    ts_log.add('LEFTPADDING', (0,0), (-1,-1), 5)
    ts_log.add('RIGHTPADDING', (0,0), (-1,-1), 5)
    ts_log.add('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    ts_log.add('SPAN', (0, -1), (1, -1))
    t_log.setStyle(ts_log)
    story.append(t_log)
    
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("2. Impostos & Comissão", style_secao))
    story.append(Spacer(1, 4))
    
    total_impostos_comissao = dados['valor_impostos'] + dados['comissao']
    
    tabela_op_dados = [
        [Paragraph("<b>Descrição</b>", style_bold), Paragraph("<b>Base / Alíquota</b>", style_bold), Paragraph("<b>Valor Estimado</b>", style_bold)],
        [Paragraph("Valor Base dos Serviços", style_corpo), Paragraph(f"Tabela ({dados['carga_horaria_sel']})", style_corpo), Paragraph(fmt_brl(dados['valor_base']), style_corpo)],
        [Paragraph("Desconto Aplicado", style_corpo), Paragraph("Desconto comercial", style_corpo), Paragraph(f"- {fmt_brl(dados['valor_desconto_calculado'])}", style_corpo)],
        [Paragraph("Ajuste Manual / Especial", style_corpo), Paragraph("Subtração aplicada", style_corpo), Paragraph(f"- {fmt_brl(dados['ajuste_manual'])}", style_corpo)],
        [Paragraph("Impostos (Nota Fiscal)", style_corpo), Paragraph(f"{dados['imposto_perc']}% sobre o faturamento", style_corpo), Paragraph(fmt_brl(dados['valor_impostos']), style_corpo)],
        [Paragraph("Comissão", style_corpo), Paragraph(f"{dados['comissao_perc']}% sobre o faturamento", style_corpo), Paragraph(fmt_brl(dados['comissao']), style_corpo)],
        [Paragraph("<b>TOTAL IMPOSTOS & COMISSÃO</b>", style_bold), Paragraph("", style_corpo), Paragraph(f"<b>{fmt_brl(total_impostos_comissao)}</b>", style_bold)]
    ]
    t_op = Table(tabela_op_dados, colWidths=[130, 270, 140])
    t_op.hAlign = 'LEFT'
    ts_op = TableStyle()
    ts_op.add('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9'))
    ts_op.add('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#e2e8f0'))
    ts_op.add('ALIGN', (0,0), (-1,-1), 'LEFT')
    ts_op.add('ALIGN', (2,0), (2,-1), 'RIGHT')
    ts_op.add('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ts_op.add('BOTTOMPADDING', (0,0), (-1,-1), 2)
    ts_op.add('TOPPADDING', (0,0), (-1,-1), 2)
    ts_op.add('LEFTPADDING', (0,0), (-1,-1), 5)
    ts_op.add('RIGHTPADDING', (0,0), (-1,-1), 5)
    ts_op.add('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    ts_op.add('SPAN', (0, -1), (1, -1))
    t_op.setStyle(ts_op)
    story.append(t_op)
    
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("3. Fechamento Financeiro & Margem", style_secao))
    story.append(Spacer(1, 4))
    
    style_res_fat = ParagraphStyle('ResFatInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor('#1e3a8a'))
    style_res_corpo = ParagraphStyle('ResCorpoInt', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#000000'))
    style_res_lucro = ParagraphStyle('ResLucroInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#047857'))
    
    tabela_resumo_interno = [
        [Paragraph("<b>Faturamento:</b>", style_res_fat), Paragraph(f"<b>{fmt_brl(dados['valor_final'])}</b>", style_res_fat)],
        [Paragraph("<b>Custo Operacional:</b>", style_bold), Paragraph(fmt_brl(dados['custo_total_interno']), style_res_corpo)],
        [Paragraph("<b>Lucro Líquido Estimado:</b>", style_bold), Paragraph(f"<b>{fmt_brl(dados['lucro_liquido'])} ({dados['margem_lucro']:.1f}%)</b>", style_res_lucro)]
    ]
    t_res_int = Table(tabela_resumo_interno, colWidths=[310, 230])
    t_res_int.hAlign = 'LEFT'
    ts_res = TableStyle()
    ts_res.add('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e2e8f0'))
    ts_res.add('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ts_res.add('ALIGN', (1,0), (1,-1), 'RIGHT')
    ts_res.add('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ts_res.add('TOPPADDING', (0,0), (-1,-1), 4)
    ts_res.add('LEFTPADDING', (0,0), (-1,-1), 8)
    ts_res.add('RIGHTPADDING', (0,0), (-1,-1), 8)
    ts_res.add('BOX', (0,0), (-1,-1), 1.2, colors.HexColor('#1e3a8a'))
    t_res_int.setStyle(ts_res)
    story.append(t_res_int)
    
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("4. Observações", style_secao))
    story.append(Spacer(1, 4))
    
    # Altura adequada das linhas do bloco 4 restaurada (22 pontos por linha)
    obs_linhas = [
        [Paragraph("", style_corpo)],
        [Paragraph("", style_corpo)],
        [Paragraph("", style_corpo)],
        [Paragraph("", style_corpo)]
    ]
    t_obs = Table(obs_linhas, colWidths=[540], rowHeights=[22, 22, 22, 22])
    t_obs.hAlign = 'LEFT'
    t_obs.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#cbd5e1')),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fcfcfc')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_obs)

    doc.build(story, canvasmaker=SimpleCanvasInternal)
    buffer.seek(0)
    return buffer

logo_app_path = get_logo_app_path()
if logo_app_path:
    st.image(logo_app_path, width=280)

st.markdown("<h1 style='text-align: center; margin-top: -1rem; margin-bottom: 0rem;'>⚡ Sistema de Propostas & Custos</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; margin-top: 0rem; margin-bottom: 0.5rem;'>Gerencie orçamentos comerciais, analise a viabilidade interna e gere documentação profissional em PDF.</p>", unsafe_allow_html=True)

if 'current_tab_idx' not in st.session_state:
    st.session_state.current_tab_idx = 0

tab_names = ["1. 📋 Dados & Serviços", "2. 🚗 Custos & Logística", "3. 📄 Prazos, Resumo & Relatórios"]

st.markdown("<br>", unsafe_allow_html=True)
tab_selecionada = st.radio("Navegação:", tab_names, index=st.session_state.current_tab_idx, horizontal=True, label_visibility="collapsed")
nova_aba_idx = tab_names.index(tab_selecionada)

if nova_aba_idx != st.session_state.current_tab_idx:
    st.session_state.current_tab_idx = nova_aba_idx
    scroll_to_top()
    st.rerun()

st.markdown("<hr style='margin-top: 0px; margin-bottom: 20px;'>", unsafe_allow_html=True)

default_entrega_txt = "Até 72h após o término do serviço, editado e enviado via link para download, em alta e baixa resolução, disponível por 30 dias."

if st.session_state.current_tab_idx == 0:
    st.subheader("1. Dados do Cliente e Serviço")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.contato = st.text_input("Contato", st.session_state.get("contato", ""))
        st.session_state.empresa = st.text_input("Empresa", st.session_state.get("empresa", ""))
        st.session_state.telefone = st.text_input("Telefone", st.session_state.get("telefone", ""))
        st.session_state.email = st.text_input("E-mail", st.session_state.get("email", ""))
        
        st.markdown("<br>", unsafe_allow_html=True)
        tipo_servico_idx = list(TABELAS_SERVICOS.keys()).index(st.session_state.get("tipo_servico", "Evento social")) if st.session_state.get("tipo_servico", "Evento social") in TABELAS_SERVICOS else 0
        st.session_state.tipo_servico = st.selectbox("Tipo de Serviço", list(TABELAS_SERVICOS.keys()), index=tipo_servico_idx)
        
        st.session_state.outro_servico_nome = ""
        if st.session_state.tipo_servico == "Outro":
            st.session_state.outro_servico_nome = st.text_input("Especifique o nome do serviço", st.session_state.get("outro_servico_nome", ""))

        carga_idx = OPCOES_CARGA_HORARIA.index(st.session_state.get("carga_horaria_sel", "1h")) if st.session_state.get("carga_horaria_sel", "1h") in OPCOES_CARGA_HORARIA else 0
        st.session_state.carga_horaria_sel = st.selectbox("Carga Horária", OPCOES_CARGA_HORARIA, index=carga_idx)

    with col2:
        st.session_state.data_orcamento = st.date_input("Data do Orçamento (dia/mês/ano)", st.session_state.get("data_orcamento", datetime.now()))
        st.session_state.data_evento = st.date_input("Data do Serviço (dia/mês/ano)", st.session_state.get("data_evento", datetime.now()))
        
        st.session_state.tem_data_termino = st.checkbox("Serviço com mais de um dia (Data de Término)", st.session_state.get("tem_data_termino", False))
        st.session_state.data_termino = st.session_state.data_evento
        if st.session_state.tem_data_termino:
            st.session_state.data_termino = st.date_input("Data de Término do Serviço (dia/mês/ano)", st.session_state.get("data_termino", datetime.now()))
            
        st.session_state.horario = st.text_input("Horário do Serviço", st.session_state.get("horario", "08h00"))
        st.session_state.nome_servico_input = st.text_input("Nome do Serviço / Evento", st.session_state.get("nome_servico_input", ""))
        
        st.session_state.local = st.text_input("Local (Rua, Número, Bairro, etc.)", st.session_state.get("local", ""))
        
        col_cidade, col_uf = st.columns([3, 1])
        with col_cidade:
            st.session_state.cidade = st.text_input("Cidade", st.session_state.get("cidade", "Ribeirão Preto"))
        with col_uf:
            st.session_state.estado = st.selectbox("Estado (UF)", ESTADOS_BR, index=ESTADOS_BR.index(st.session_state.get("estado", "SP")) if st.session_state.get("estado", "SP") in ESTADOS_BR else 0)

        if st.button("🗺️ Calcular KM Automático (Google Maps)", use_container_width=True):
            endereco_completo = f"{st.session_state.local}, {st.session_state.cidade} - {st.session_state.estado}"
            km_calc = calcular_distancia_maps(endereco_completo)
            if km_calc is not None:
                st.session_state.distancia_ida_volta = km_calc
                st.markdown(f"<div style='text-align: center; padding: 10px; background-color: #d1fae5; color: #065f46; border-radius: 6px; margin-top: 10px;'><b>Rota encontrada com sucesso!</b><br>Distância de ida e volta: {km_calc} km (a partir da Rua Manoel Achê, 327).</div>", unsafe_allow_html=True)
                time.sleep(3)
                st.rerun()
            else:
                st.markdown("<div style='text-align: center; padding: 10px; background-color: #fee2e2; color: #991b1b; border-radius: 6px; margin-top: 10px;'>⚠️ Não foi possível calcular automaticamente. Verifique o endereço e a chave da API.</div>", unsafe_allow_html=True)
                time.sleep(3)
                st.rerun()

    st.markdown("---")
    st.subheader("2. Detalhamento Técnico (Escopo & Captação)")
    
    s_tipo = st.session_state.tipo_servico
    s_outro = st.session_state.outro_servico_nome
    s_input = st.session_state.nome_servico_input
    nome_serv_atual = s_input if s_input else (s_tipo if s_tipo != "Outro" else s_outro)
    
    mes_extenso_ev = MESES_PT[st.session_state.data_evento.month]
    if st.session_state.tem_data_termino:
        mes_extenso_ter = MESES_PT[st.session_state.data_termino.month]
        data_str_escopo = f"{st.session_state.data_evento.day} de {mes_extenso_ev} até {st.session_state.data_termino.day} de {mes_extenso_ter} de {st.session_state.data_termino.year}"
    else:
        data_str_escopo = f"{st.session_state.data_evento.day} de {mes_extenso_ev} de {st.session_state.data_evento.year}"

    default_escopo = f"{nome_serv_atual}\n{data_str_escopo}\n{st.session_state.horario if st.session_state.horario else 'Horário a definir'}\n{st.session_state.local if st.session_state.local else 'Local a definir'}\n{st.session_state.cidade} - {st.session_state.estado}\n01 (um) profissional".strip()
    
    st.session_state.escopo_servico = st.text_area("Escopo do serviço", default_escopo, height=130)
    st.session_state.captacao = st.text_area("Captação", st.session_state.get("captacao", "Cobertura profissional com equipamentos de alto padrão"), height=60)
    
    st.markdown("---")
    if st.button("Avançar ➡️", key="btn_avancar_aba0", use_container_width=True):
        st.session_state.current_tab_idx = 1
        scroll_to_top()
        st.rerun()

elif st.session_state.current_tab_idx == 1:
    st.subheader("Custos operacionais")
    
    st.markdown("##### 🚗 Parâmetros de Deslocamento & Logística")
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        st.session_state.distancia_ida_volta = st.number_input("Distância Total (Ida e Volta em km)", min_value=0, value=st.session_state.get("distancia_ida_volta", 0), step=1, format="%d")
    with col_l2:
        st.session_state.consumo_medio = st.number_input("Consumo Médio (km/L)", min_value=1.0, value=st.session_state.get("consumo_medio", 11.50), step=0.5)
    with col_l3:
        st.session_state.preco_combustivel = st.number_input("Preço do Litro (R$)", min_value=0.0, value=st.session_state.get("preco_combustivel", 6.80), step=0.10)
        
    col_est1, col_est2 = st.columns(2)
    with col_est1:
        st.session_state.pedagio_total = st.number_input("Valor Total de Pedágios (R$)", min_value=0.0, value=st.session_state.get("pedagio_total", 0.00), step=5.0, format="%.2f")
    with col_est2:
        st.session_state.custo_estacionamento = st.number_input("Estacionamento (R$)", min_value=0.0, value=st.session_state.get("custo_estacionamento", 0.00), step=5.0, format="%.2f")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 🏨 Hospedagem")
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.session_state.qtd_hosp = st.number_input("Qtd. Diárias Hospedagem", min_value=0, value=st.session_state.get("qtd_hosp", 0), step=1)
    with col_h2:
        st.session_state.val_hosp = st.number_input("R$ Hospedagem (diária)", min_value=0.0, value=st.session_state.get("val_hosp", 250.00), step=10.0, format="%.2f")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 🍽️ Alimentação")
    col_alim1, col_alim2 = st.columns(2)
    with col_alim1:
        st.session_state.custo_almoco = st.number_input("Almoço (R$)", min_value=0.0, value=st.session_state.get("custo_almoco", 0.00), step=5.0, format="%.2f")
    with col_alim2:
        st.session_state.custo_jantar = st.number_input("Jantar (R$)", min_value=0.0, value=st.session_state.get("custo_jantar", 0.00), step=5.0, format="%.2f")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📦 Outros Custos")
    col_ap1, col_ap2 = st.columns(2)
    with col_ap1:
        st.session_state.custo_freelancer = st.number_input("Freelancer (R$)", min_value=0.0, value=st.session_state.get("custo_freelancer", 0.00), step=50.0, format="%.2f")
    with col_ap2:
        st.session_state.custo_outros = st.number_input("Outros (R$)", min_value=0.0, value=st.session_state.get("custo_outros", 0.00), step=10.0, format="%.2f")

    st.markdown("---")
    st.subheader("Impostos & Comissão")
    col_op1, col_op2, col_op3 = st.columns(3)
    with col_op1:
        st.session_state.imposto_perc = st.number_input("Alíquota de Impostos / Notas (%)", min_value=0.0, max_value=30.0, value=st.session_state.get("imposto_perc", 6.0), step=0.5)
    with col_op2:
        st.session_state.comissao_perc = st.number_input("Comissão (%)", min_value=0, max_value=50, value=st.session_state.get("comissao_perc", 0), step=1, format="%d")
    with col_op3:
        st.session_state.ajuste_manual = st.number_input("Ajuste Manual do Valor Final (R$ - Subtração)", min_value=0.0, value=st.session_state.get("ajuste_manual", 0.0), step=10.0, format="%.2f")

    st.markdown("---")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("⬅️ Voltar", key="btn_voltar_aba1", use_container_width=True):
            st.session_state.current_tab_idx = 0
            scroll_to_top()
            st.rerun()
    with col_b2:
        if st.button("Avançar ➡️", key="btn_avancar_aba1", use_container_width=True):
            st.session_state.current_tab_idx = 2
            scroll_to_top()
            st.rerun()

elif st.session_state.current_tab_idx == 2:
    st.subheader("Validade do Orçamento, Forma de Entrega & Condições de Pagamento")
    
    st.session_state.valor_personalizado = st.number_input(
        "Valor Personalizado / Sob Consulta (R$ - Deixe 0 para usar a regra da tabela)",
        min_value=0.0,
        value=st.session_state.get("valor_personalizado", 0.0),
        step=50.0,
        format="%.2f"
    )
    
    st.session_state.validade_orcamento = st.text_input("Validade do Orçamento", st.session_state.get("validade_orcamento", "05 dias"))
    st.session_state.forma_entrega = st.text_input("Forma de entrega", st.session_state.get("forma_entrega", default_entrega_txt))
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        fp_idx = ["À vista", "Parcelado"].index(st.session_state.get("forma_pagamento_tipo", "À vista")) if st.session_state.get("forma_pagamento_tipo", "À vista") in ["À vista", "Parcelado"] else 0
        st.session_state.forma_pagamento_tipo = st.selectbox("Forma de Pagamento", ["À vista", "Parcelado"], index=fp_idx)
    with col_p2:
        cp_opcoes = ["PIX", "Transferência", "PIX ou transferência bancária", "Cartão de crédito", "Cartão de Crédito parcelado"]
        cp_idx = cp_opcoes.index(st.session_state.get("condicao_pagamento", "PIX")) if st.session_state.get("condicao_pagamento", "PIX") in cp_opcoes else 0
        st.session_state.condicao_pagamento = st.selectbox("Condições de Pagamento", cp_opcoes, index=cp_idx)
    with col_p3:
        st.session_state.prazo_pagamento_dias = st.number_input("Prazo de Pagamento (dias)", min_value=1, max_value=45, value=st.session_state.get("prazo_pagamento_dias", 5), step=1, format="%d")

    dias_txt = f"em até {st.session_state.prazo_pagamento_dias} dias" if st.session_state.prazo_pagamento_dias > 0 else "à vista"
    parcelas_cartao = 1
    if "parcelado" in st.session_state.condicao_pagamento.lower() or st.session_state.forma_pagamento_tipo == "Parcelado":
        parcelas_cartao = st.number_input("Cartão de Crédito parcelado em X vezes", min_value=1, max_value=12, value=3)
        st.session_state.condicao_pagamento_final = f"{st.session_state.condicao_pagamento} em {parcelas_cartao}X ({dias_txt})"
    else:
        st.session_state.condicao_pagamento_final = f"{st.session_state.condicao_pagamento} ({dias_txt})"

    st.markdown("---")
    st.subheader("Descontos & Condições Comerciais")
    col_desc1, col_desc2 = st.columns(2)
    with col_desc1:
        modo_idx = ["Porcentagem (%)", "Valor Fixo (R$)"].index(st.session_state.get("tipo_desc_modo", "Porcentagem (%)")) if st.session_state.get("tipo_desc_modo", "Porcentagem (%)") in ["Porcentagem (%)", "Valor Fixo (R$)"] else 0
        st.session_state.tipo_desc_modo = st.radio("Modalidade de Desconto", ["Porcentagem (%)", "Valor Fixo (R$)"], index=modo_idx, horizontal=True)
    with col_desc2:
        if st.session_state.tipo_desc_modo == "Porcentagem (%)":
            st.session_state.desconto_perc = st.slider("Desconto (%)", min_value=0.0, max_value=50.0, value=st.session_state.get("desconto_perc", 0.0), step=0.5)
            st.session_state.desconto_valor_input = 0.0
        else:
            st.session_state.desconto_perc = 0.0
            st.session_state.desconto_valor_input = st.number_input("Desconto em Valor Fixo (R$)", min_value=0.0, value=st.session_state.get("desconto_valor_input", 0.0), step=10.0, format="%.2f")

    st.markdown("---")
    if st.button("⬅️ Voltar", key="btn_voltar_aba2", use_container_width=True):
        st.session_state.current_tab_idx = 1
        scroll_to_top()
        st.rerun()

try:
    s_tipo = st.session_state.get("tipo_servico", "Evento social")
    s_outro = st.session_state.get("outro_servico_nome", "")
    s_input = st.session_state.get("nome_servico_input", "")
    
    servico_nome = s_tipo if s_tipo != "Outro" else s_outro
    nome_serv_ev = s_input if s_input else servico_nome
    
    tabela_atual = TABELAS_SERVICOS.get(s_tipo, TABELAS_SERVICOS["Evento social"])
    
    dias_evento = 1
    d_ev = st.session_state.get("data_evento", datetime.now())
    d_ter = st.session_state.get("data_termino", datetime.now())
    if st.session_state.get("tem_data_termino", False):
        dias_evento = max(1, (d_ter - d_ev).days + 1)

    val_pers = st.session_state.get("valor_personalizado", 0.0)
    if val_pers > 0:
        valor_base = val_pers
    else:
        c_horaria = st.session_state.get("carga_horaria_sel", "1h")
        if "diária" in c_horaria:
            qtd_diarias = int(c_horaria.split()[0])
            valor_base = tabela_atual.get(10, 1300.0) * qtd_diarias * dias_evento
        else:
            horas_num = int(c_horaria.replace("h", ""))
            horas_buscadas = min(horas_num, 12)
            valor_base = tabela_atual.get(horas_buscadas, 1500.0) * dias_evento
            if horas_num > 12:
                valor_base += (horas_num - 12) * tabela_atual.get(1, 180.0) * dias_evento

    d_perc = st.session_state.get("desconto_perc", 0.0)
    d_val = st.session_state.get("desconto_valor_input", 0.0)
    aj_man = st.session_state.get("ajuste_manual", 0.0)
    
    if d_perc > 0:
        valor_desconto_calculado = valor_base * (d_perc / 100.0)
    else:
        valor_desconto_calculado = d_val

    valor_intermediario = valor_base - valor_desconto_calculado - aj_man
    valor_final = max(0.0, valor_intermediario)

    dist = st.session_state.get("distancia_ida_volta", 0)
    cons = st.session_state.get("consumo_medio", 11.5)
    p_comb = st.session_state.get("preco_combustivel", 6.8)
    ped = st.session_state.get("pedagio_total", 0.0)
    est = st.session_state.get("custo_estacionamento", 0.0)
    
    litros_gastos = dist / cons if cons > 0 else 0
    custo_combustivel = litros_gastos * p_comb
    custo_logistica_total = custo_combustivel + ped + est

    hosp_tot = st.session_state.get("qtd_hosp", 0) * st.session_state.get("val_hosp", 250.0)
    custo_total_operacional_log = custo_logistica_total + hosp_tot + st.session_state.get("custo_almoco", 0.0) + st.session_state.get("custo_jantar", 0.0) + st.session_state.get("custo_freelancer", 0.0) + st.session_state.get("custo_outros", 0.0)
    
    imp_p = st.session_state.get("imposto_perc", 6.0)
    com_p = st.session_state.get("comissao_perc", 0)
    
    valor_impostos = valor_final * (imp_p / 100.0)
    valor_comissao = valor_final * (com_p / 100.0)
    
    custo_total_interno = custo_total_operacional_log + valor_impostos + valor_comissao
    lucro_liquido = valor_final - custo_total_interno
    margem_lucro = (lucro_liquido / valor_final * 100) if valor_final > 0 else 0
except Exception:
    valor_base = 0.0
    valor_desconto_calculado = 0.0
    valor_final = 0.0
    litros_gastos = 0.0
    custo_combustivel = 0.0
    hosp_tot = 0.0
    custo_total_interno = 0.0
    lucro_liquido = 0.0
    margem_lucro = 0.0
    valor_impostos = 0.0
    valor_comissao = 0.0

st.markdown("---")
st.markdown("### 📈 Quadro de Prévia em Tempo Real (Visão Geral)")

c_horaria_sel_str = st.session_state.get("carga_horaria_sel", "1h")
if "diária" in c_horaria_sel_str:
    num_diarias_unit = int(c_horaria_sel_str.split()[0])
    carga_horaria_total_exibida = f"{num_diarias_unit * dias_evento} diária(s)"
else:
    horas_unit = int(c_horaria_sel_str.replace("h", ""))
    total_horas_calc = horas_unit * dias_evento
    if dias_evento > 1:
        carga_horaria_total_exibida = f"{total_horas_calc}h ({dias_evento}d x {horas_unit}h)"
    else:
        carga_horaria_total_exibida = f"{total_horas_calc}h"

col_res1, col_res2, col_res3, col_res4, col_res5 = st.columns([1.2, 1.2, 1.2, 1.1, 1.3])
col_res1.metric("Valor Cliente", fmt_brl(valor_final))
col_res2.metric("Custos", fmt_brl(custo_total_interno))
col_res3.metric("Lucro Est.", fmt_brl(lucro_liquido))
col_res4.metric("Margem", f"{margem_lucro:.1f}%")
col_res5.metric("Carga Horária", carga_horaria_total_exibida)

dados_completos = {
    "contato": st.session_state.get("contato", ""),
    "empresa": st.session_state.get("empresa", ""),
    "telefone": st.session_state.get("telefone", ""),
    "email": st.session_state.get("email", ""),
    "data_orcamento": st.session_state.get("data_orcamento", datetime.now()),
    "data_evento": st.session_state.get("data_evento", datetime.now()),
    "tem_data_termino": st.session_state.get("tem_data_termino", False),
    "data_termino": st.session_state.get("data_termino", datetime.now()),
    "horario": st.session_state.get("horario", "08h00"),
    "nome_servico_input": st.session_state.get("nome_servico_input", ""),
    "local": st.session_state.get("local", ""),
    "cidade": st.session_state.get("cidade", "Ribeirão Preto"),
    "estado": st.session_state.get("estado", "SP"),
    "tipo_servico": st.session_state.get("tipo_servico", "Evento social"),
    "outro_servico_nome": st.session_state.get("outro_servico_nome", ""),
    "carga_horaria_sel": carga_horaria_total_exibida,
    "escopo_servico": st.session_state.get("escopo_servico", ""),
    "captacao": st.session_state.get("captacao", ""),
    "validade_orcamento": st.session_state.get("validade_orcamento", "05 dias"),
    "forma_entrega": st.session_state.get("forma_entrega", default_entrega_txt),
    "forma_pagamento_tipo": st.session_state.get("forma_pagamento_tipo", "À vista"),
    "condicao_pagamento": st.session_state.get("condicao_pagamento_final", "PIX"),
    "prazo_pagamento_dias": st.session_state.get("prazo_pagamento_dias", 5),
    "desconto_perc": st.session_state.get("desconto_perc", 0.0),
    "ajuste_manual": st.session_state.get("ajuste_manual", 0.0),
    "valor_base": valor_base,
    "valor_desconto_calculado": valor_desconto_calculado,
    "valor_final": valor_final,
    "distancia": st.session_state.get("distancia_ida_volta", 0),
    "consumo_veiculo": st.session_state.get("consumo_medio", 11.5),
    "litros_gastos": litros_gastos,
    "preco_combustivel": st.session_state.get("preco_combustivel", 6.8),
    "custo_combustivel": custo_combustivel,
    "pedagios": st.session_state.get("pedagio_total", 0.0),
    "custo_estacionamento": st.session_state.get("custo_estacionamento", 0.0),
    "custo_hospedagem_total": hosp_tot,
    "custo_almoco": st.session_state.get("custo_almoco", 0.0),
    "custo_jantar": st.session_state.get("custo_jantar", 0.0),
    "custo_freelancer": st.session_state.get("custo_freelancer", 0.0),
    "custo_outros": st.session_state.get("custo_outros", 0.0),
    "imposto_perc": st.session_state.get("imposto_perc", 6.0),
    "valor_impostos": valor_impostos,
    "comissao_perc": st.session_state.get("comissao_perc", 0),
    "comissao": valor_comissao,
    "custo_total_interno": custo_total_interno,
    "lucro_liquido": lucro_liquido,
    "margem_lucro": margem_lucro
}

if st.session_state.current_tab_idx == 2:
    st.markdown("---")
    st.subheader("📥 Geração de Documentos (PDF)")
    
    pdf_cliente_bytes = gerar_pdf_cliente(dados_completos)
    pdf_interno_bytes = gerar_pdf_interno(dados_completos)

    id_envio = f"{dados_completos['empresa']}_{dados_completos['data_evento']}_{dados_completos['valor_final']}"
    if st.session_state.get("ultimo_envio_email") != id_envio:
        nome_cliente_lead = dados_completos.get('empresa') or dados_completos.get('contato') or "Cliente"
        sucesso, erro_msg = enviar_pdf_por_email(pdf_cliente_bytes, pdf_interno_bytes, nome_cliente_lead, nome_serv_ev)
        if sucesso:
            st.session_state["ultimo_envio_email"] = id_envio
            st.toast("📧 Cópia dos PDFs enviada com sucesso para contato@okamotomidiasvisuais.com.br!", icon="✅")
        else:
            st.warning(f"⚠️ Erro ao enviar e-mail automático: {erro_msg}")

    col_down1, col_down2 = st.columns(2)
    
    data_arquivo_str = datetime.now().strftime('%d-%m-%Y')
    nome_arquivo_cliente = f"Proposta comercial - Okamoto Midias Visuais - {nome_serv_ev} - {data_arquivo_str}.pdf"
    nome_arquivo_interno = f"Relatorio de custos - {nome_serv_ev} - {data_arquivo_str}.pdf"

    with col_down1:
        st.download_button(
            label="📄 Baixar Proposta Comercial (Cliente)",
            data=pdf_cliente_bytes,
            file_name=nome_arquivo_cliente,
            mime="application/pdf",
            use_container_width=True
        )

    with col_down2:
        st.download_button(
            label="🔒 Baixar Relatório Interno (Custos)",
            data=pdf_interno_bytes,
            file_name=nome_arquivo_interno,
            mime="application/pdf",
            use_container_width=True
        )

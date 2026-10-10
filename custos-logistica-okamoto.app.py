import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.pdfgen import canvas
import io
import os
from datetime import datetime
from PIL import Image as PILImage, ImageDraw

def fmt_brl(val):
    s = f"{val:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

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

st.set_page_config(page_title="Proposta Comercial & Custos - Okamoto Mídias Visuais", page_icon="📊", layout="wide")

class ModernFooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer()
            super().showPage()
        super().save()

    def draw_footer(self):
        self.saveState()
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.75)
        self.line(35, 42, 575, 42)
        self.restoreState()

def get_logo_path():
    caminho = "logo_okamoto.png"
    try:
        if not os.path.exists(caminho):
            img = PILImage.new('RGB', (1200, 350), (255, 255, 255))
            d = ImageDraw.Draw(img)
            d.rectangle([0, 0, 1200, 350], fill=(255, 255, 255))
            d.text((50, 80), "OKAMOTO", fill="#0f172a")
            d.text((50, 180), "MÍDIAS VISUAIS", fill="#64748b")
            img.save(caminho, "PNG")
        return caminho
    except Exception:
        if os.path.exists(caminho):
            return caminho
        return None

def criar_rodape_story(styles):
    style_footer = ParagraphStyle(
        'FooterTextModern', 
        parent=styles['Normal'], 
        fontName='Helvetica', 
        fontSize=8, 
        leading=11, 
        alignment=1, 
        textColor=colors.HexColor('#64748b')
    )
    texto = (
        "Okamoto Mídias Visuais &nbsp;&nbsp;|&nbsp;&nbsp; "
        "<a href='https://okamotomidiasvisuais.com.br' color='#1e3a8a'>okamotomidiasvisuais.com.br</a> "
        "&nbsp;&nbsp;|&nbsp;&nbsp; contato@okamotomidiasvisuais.com.br &nbsp;&nbsp;|&nbsp;&nbsp; "
        "<a href='https://wa.me/5516991332121' color='#047857'>WhatsApp: 16 99133 2121</a>"
    )
    return Paragraph(texto, style_footer)

def gerar_pdf_cliente(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=30, bottomMargin=40)
    
    servico_nome = dados['tipo_servico'] if dados['tipo_servico'] != "Outro" else dados['outro_servico_nome']
    nome_serv_ev = dados['nome_servico_input'] if dados['nome_servico_input'] else servico_nome
    data_ev_str = dados['data_evento'].strftime('%d/%m/%Y')
    
    doc.title = f"Proposta comercial - {nome_serv_ev} - {data_ev_str}"
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('TituloPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, alignment=1, textColor=colors.HexColor('#0f172a'))
    style_servico_sub = ParagraphStyle('ServSubPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16, alignment=1, textColor=colors.HexColor('#1e3a8a'))
    style_corpo = ParagraphStyle('CorpoPDF', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=14, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('BoldPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=14, textColor=colors.HexColor('#0f172a'))
    style_assinatura = ParagraphStyle('AssinaturaPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=colors.HexColor('#0f172a'))
    style_cat_titulo = ParagraphStyle('CatTitPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.HexColor('#0f172a'))
    style_destaque_1 = ParagraphStyle('Dest1PDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=19, alignment=1, textColor=colors.HexColor('#0f172a'))
    style_destaque_2 = ParagraphStyle('Dest2PDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=15, alignment=1, textColor=colors.HexColor('#64748b'))
    
    story = []

    logo_path = get_logo_path()
    if logo_path:
        img = RLImage(logo_path, width=130, height=38)
        img.hAlign = 'CENTER'
        story.append(img)
    else:
        story.append(Paragraph("<b>[ OKAMOTO MÍDIAS VISUAIS ]</b>", style_titulo))
    
    story.append(Spacer(1, 16))
    
    d_orc = dados['data_orcamento']
    data_extenso = f"Ribeirão Preto, {d_orc.day} de {MESES_PT[d_orc.month]} de {d_orc.year}"
    story.append(Paragraph(data_extenso, style_corpo))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Proposta Comercial", style_titulo))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"{servico_nome} — {nome_serv_ev}", style_servico_sub))
    story.append(Spacer(1, 14))
    
    story.append(Paragraph("<b>1. Dados do cliente:</b>", style_bold))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Contato:</b> {dados['contato']}", style_corpo))
    story.append(Paragraph(f"<b>Empresa:</b> {dados['empresa']}", style_corpo))
    story.append(Paragraph(f"<b>Telefone:</b> {dados['telefone']}", style_corpo))
    story.append(Paragraph(f"<b>E-mail:</b> {dados['email']}", style_corpo))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>2. Data do serviço:</b>", style_bold))
    data_evento_str = dados['data_evento'].strftime('%d/%m/%Y')
    if dados['tem_data_termino']:
        data_evento_str += f" até {dados['data_termino'].strftime('%d/%m/%Y')}"
    texto_evento = f"<b>Data:</b> {data_evento_str} &nbsp;&nbsp; <b>Horário:</b> {dados['horario']} &nbsp;&nbsp; <b>Local:</b> {dados['local']} — {dados['cidade']}/{dados['estado']}"
    story.append(Paragraph(texto_evento, style_corpo))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>3. Serviço:</b>", style_bold))
    story.append(Paragraph(f"{servico_nome} ({nome_serv_ev})", style_corpo))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>4. Escopo do serviço:</b>", style_bold))
    story.append(Paragraph(dados['escopo_servico'].replace('\n', '<br/>'), style_corpo))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>5. Captação:</b>", style_bold))
    story.append(Paragraph(dados['captacao'].replace('\n', '<br/>'), style_corpo))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>6. Forma de entrega:</b> Link exclusivo para download, disponível por 30 dias.", style_corpo))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"<b>7. Formas de pagamento:</b> {dados['forma_pagamento_tipo']}", style_corpo))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"<b>8. Condições de

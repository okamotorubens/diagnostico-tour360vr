import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas

# -----------------------------------------------------------------------------
# GERADOR DE PDF IDENTICO AO LAYOUT "PROPOSTA COMERCIAL 007-2026"
# -----------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
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
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(555, 20, f"Página {self._pageNumber}/{num_pages}")
            self.restoreState()
            super().showPage()
        super().save()

def gerar_pdf_layout_oficial(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=30, bottomMargin=35)
    styles = getSampleStyleSheet()
    
    style_tit_empresa = ParagraphStyle('TitEmp', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor('#0f172a'))
    style_sub_empresa = ParagraphStyle('SubEmp', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#475569'))
    style_tit_proposta = ParagraphStyle('TitProp', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=colors.HexColor('#0284c7'))
    style_cliente = ParagraphStyle('Cli', fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#334155'))
    style_th = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor('#0f172a'))
    style_td = ParagraphStyle('TD', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#334155'))
    style_sec = ParagraphStyle('Sec', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=colors.HexColor('#0284c7'))
    style_bold_sm = ParagraphStyle('BSm', fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=colors.HexColor('#0f172a'))

    story = []

    # 1. CABEÇALHO (EMPRESA À ESQUERDA | PROPOSTA/CLIENTE À DIREITA)
    col_esquerda = []
    if st.session_state.get('logo_bytes'):
        try:
            img_buf = io.BytesIO(st.session_state['logo_bytes'])
            col_esquerda.append(Image(img_buf, width=70, height=70))
            col_esquerda.append(Spacer(1, 4))
        except Exception:
            pass
            
    col_esquerda.extend([
        Paragraph("<b>OKAMOTO REPORTAGENS FOTOGRAFICAS S/S LTDA</b>", style_tit_empresa),
        Paragraph("CNPJ: 04.824.331/0001-05<br/>contato@tour360vr.com.br<br/>+55 (16) 99133-2121<br/>+55 (16) 99622-2121<br/><i>A mais nova forma de ver o mundo</i>", style_sub_empresa)
    ])

    col_direita = [
        Paragraph(f"Proposta comercial {dados['num_pedido']}", style_tit_proposta),
        Spacer(1, 6),
        Paragraph(f"<b>{dados['empresa']}</b><br/>Cliente: {dados['contato']}<br/>{dados['telefone_cli']}", style_cliente)
    ]

    t_header = Table([[col_esquerda, col_direita]], colWidths=[270, 250])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 15))

    # 2. TABELA DE SERVIÇOS
    srv_table_data = [[Paragraph("Serviços", style_th), Paragraph("Descrição", style_th), Paragraph("Qtd.", style_th)]]
    for item in dados['itens']:
        srv_table_data.append([
            Paragraph(f"<b>{item['nome']}</b>", style_td),
            Paragraph(item.get('desc', ''), style_td),
            Paragraph(str(item.get('qtd', 1)), style_td)
        ])
    
    # Linha do Total
    srv_table_data.append([
        Paragraph("<b>Total</b>", style_th),
        "",
        Paragraph(f"<b>R$ {dados['valor_final']:,.2f}</b>", style_th)
    ])

    t_servicos = Table(srv_table_data, colWidths=[180, 270, 70])
    t_servicos.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#0284c7')),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#cbd5e1')),
        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#0f172a')),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_servicos)
    story.append(Spacer(1, 15))

    # 3. PAGAMENTO E INFORMAÇÕES ADICIONAIS (DUAS COLUNAS)
    col_pagamento = [
        Paragraph("Pagamento", style_sec),
        Spacer(1, 3),
        Paragraph("<b>Meios de pagamento</b><br/>Transferência bancária, cartão de crédito ou pix.", style_td),
        Spacer(1, 4),
        Paragraph("<b>Dados bancários</b><br/>Banco: Banco do Brasil<br/>Agência: 3235-2 | Conta: 11935-0 (Corrente)<br/>Titular: 04.824.331/0001-05", style_td),
        Spacer(1, 4),
        Paragraph(f"<b>PIX:</b> 04824331000105<br/><b>Condições:</b> {dados['condicoes_pag']}", style_td)
    ]

    col_info = [
        Paragraph("Informações adicionais", style_sec),
        Spacer(1, 3),
        Paragraph(dados['info_adicionais'].replace('\n', '<br/>'), style_td)
    ]

    t_rodape = Table([[col_pagamento, col_info]], colWidths=[260, 260])
    t_rodape.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_rodape)
    story.append(Spacer(1, 25))

    # 4. CAMPOS DE ASSINATURA E DATAS
    ass_data = [
        [
            Paragraph("___________________________________<br/><b>Rubens Okamoto</b><br/>Tour360VR", style_td),
            Paragraph(f"___________________________________<br/><b>{dados['contato']}</b><br/>Data: {dados['data_orcamento']}", style_td)
        ]
    ]
    t_ass = Table(ass_data, colWidths=[260, 260])
    t_ass.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(t_ass)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

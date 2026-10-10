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
            self.draw_footer_content(num_pages)
            super().showPage()
        super().save()

    def draw_footer_content(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#64748b'))
        
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(35, 38, 575, 38)
        
        texto_rodape = "Okamoto Mídias Visuais    |    okamotomidiasvisuais.com.br    |    contato@okamotomidiasvisuais.com.br    |    WhatsApp: 16 99133 2121"
        self.drawString(35, 26, texto_rodape)
        self.drawRightString(575, 26, f"Página {self._pageNumber} de {page_count}")
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

def gerar_pdf_cliente(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=30, bottomMargin=50)
    
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
        img = RLImage(logo_path, width=150, height=44)
        img.hAlign = 'CENTER'
        story.append(img)
    else:
        story.append(Paragraph("<b>[ OKAMOTO MÍDIAS VISUAIS ]</b>", style_titulo))
    
    story.append(Spacer(1, 14))
    
    d_orc = dados['data_orcamento']
    data_extenso = f"Ribeirão Preto, {d_orc.day} de {MESES_PT[d_orc.month]} de {d_orc.year}"
    story.append(Paragraph(data_extenso, style_corpo))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Proposta Comercial", style_titulo))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"{nome_serv_ev}", style_servico_sub))
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
    
    horario_txt = f"&nbsp;&nbsp; <b>Horário:</b> {dados['horario']}" if dados['horario'] else ""
    texto_evento = f"<b>Data:</b> {data_evento_str}{horario_txt} &nbsp;&nbsp; <b>Local:</b> {dados['local']} — {dados['cidade']}/{dados['estado']}"
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
    
    story.append(Paragraph(f"<b>8. Condições de pagamento:</b> {dados['condicao_pagamento']}", style_corpo))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"<b>9. Validade do orçamento:</b> {dados['validade_orcamento']}", style_corpo))
    story.append(Spacer(1, 14))
    
    val_fmt = fmt_brl(dados['valor_final'])
    texto_valor = f"<b>VALOR TOTAL DO INVESTIMENTO ({dados['carga_horaria_sel']}):</b><br/>{val_fmt}"
        
    p_valor = Paragraph(texto_valor, ParagraphStyle('ValBox', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16, alignment=1, textColor=colors.HexColor('#1e3a8a')))
    t_valor_box = Table([[p_valor]], colWidths=[380])
    t_valor_box.hAlign = 'CENTER'
    t_valor_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#1e3a8a')),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
    ]))
    story.append(t_valor_box)
    story.append(Spacer(1, 14))
    
    story.append(Paragraph("Ficamos à disposição para quaisquer esclarecimentos e ajustes, caso necessário.", style_corpo))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Atenciosamente,", style_corpo))
    story.append(Spacer(1, 3))
    story.append(Paragraph("Rubens Okamoto", style_assinatura))
    story.append(Paragraph("Okamoto Mídias Visuais", style_corpo))
    story.append(PageBreak())
    
    if logo_path:
        img_inst = RLImage(logo_path, width=150, height=44)
        img_inst.hAlign = 'CENTER'
        story.append(img_inst)
    else:
        story.append(Paragraph("<b>[ OKAMOTO MÍDIAS VISUAIS ]</b>", style_titulo))
        
    story.append(Spacer(1, 16))
    story.append(Paragraph("É registrando a sua história, que nós construímos a nossa!", style_destaque_1))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Especialistas em Imagem, Vídeo e Experiências Imersivas", style_destaque_2))
    story.append(Spacer(1, 18))
    
    intro_inst = "Unimos a bagagem de três décadas às inovações tecnológicas mais recentes, transformando sua marca com soluções visuais de alta performance:"
    story.append(Paragraph(intro_inst, style_corpo))
    story.append(Spacer(1, 12))
    
    topicos_inst = "<b>• Fotografia Corporativa e Estratégica:</b><br/>Imagens que reforçam a autoridade da sua empresa e destacam seu negócio no mercado.<br/><br/><b>• Tours Virtuais 360º:</b><br/>Experiências imersivas que levam seu cliente para dentro do seu espaço físico.<br/><br/><b>• Vídeos de Alto Impacto:</b><br/>Produções pensadas para converter e engajar seu público em redes sociais e plataformas digitais."
    story.append(Paragraph(topicos_inst, style_corpo))
    story.append(Spacer(1, 18))
    
    style_dados_normal = ParagraphStyle('DadosNormais', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=14, textColor=colors.HexColor('#334155'))
    
    story.append(Paragraph("Dados da Empresa", style_cat_titulo))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Okamoto Reportagens Fotográficas SS Ltda<br/>CNPJ: 04.824.331/0001-05<br/>Rua General Carneiro, 860 — Centro, Brodowski - SP<br/>CEP: 14.340-023", style_dados_normal))
    story.append(Spacer(1, 14))
    
    story.append(Paragraph("Dados Pessoais", style_cat_titulo))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Rubens Heigasi Okamoto<br/>CPF: 287.932.298-79 &nbsp;|&nbsp; RG: 25.450.624-0 SSP/SP<br/>Tel. Cel.: 16 99133 2121 &nbsp;|&nbsp; E-mail: contato@okamotomidiasvisuais.com.br", style_dados_normal))
    story.append(Spacer(1, 14))
    
    story.append(Paragraph("Dados Bancários", style_cat_titulo))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Banco do Brasil<br/>Agência: 3235-2 &nbsp;|&nbsp; C. Corrente: 11.935-0<br/>Chave PIX: 04824331000105", style_dados_normal))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

def gerar_pdf_interno(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=25, bottomMargin=50)
    
    servico_exibido = dados['tipo_servico'] if dados['tipo_servico'] != "Outro" else dados['outro_servico_nome']
    nome_serv_ev = dados['nome_servico_input'] if dados['nome_servico_input'] else servico_exibido
    data_ev_str = dados['data_evento'].strftime('%d/%m/%Y')
    
    doc.title = f"Relatório de custos - {nome_serv_ev} - {data_ev_str}"
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('TitInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=18, alignment=1, textColor=colors.HexColor('#0f172a'))
    style_subtitulo = ParagraphStyle('SubInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#1e3a8a'))
    style_corpo = ParagraphStyle('CorpoInt', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=13, textColor=colors.HexColor('#000000'))
    style_bold = ParagraphStyle('BoldInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=13, textColor=colors.HexColor('#000000'))
    style_destaque_fat = ParagraphStyle('FatInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor('#1e3a8a'))
    style_destaque_lucro = ParagraphStyle('LucInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#047857'))
    
    story = []

    logo_path = get_logo_path()
    if logo_path:
        img_int = RLImage(logo_path, width=140, height=41)
        img_int.hAlign = 'CENTER'
        story.append(img_int)
    else:
        story.append(Paragraph("<b>[ LOGO OKAMOTO ]</b>", style_bold))
        
    story.append(Spacer(1, 14))
    story.append(Paragraph("Relatório de Custos", style_titulo))
    story.append(Spacer(1, 14))
    
    data_fim_str = dados['data_termino'].strftime('%d/%m/%Y') if dados['tem_data_termino'] else data_ev_str
    
    info_geral = [
        [Paragraph("<b>Cliente:</b>", style_bold), Paragraph(dados['contato'], style_corpo), Paragraph("<b>Data de Início:</b>", style_bold), Paragraph(data_ev_str, style_corpo)],
        [Paragraph("<b>Empresa:</b>", style_bold), Paragraph(dados['empresa'], style_corpo), Paragraph("<b>Data de Término:</b>", style_bold), Paragraph(data_fim_str, style_corpo)],
        [Paragraph("<b>Serviço:</b>", style_bold), Paragraph(f"{servico_exibido} ({nome_serv_ev})", style_corpo), Paragraph("<b>Carga Horária:</b>", style_bold), Paragraph(dados['carga_horaria_sel'], style_corpo)]
    ]
    t_geral = Table(info_geral, colWidths=[70, 195, 95, 180])
    t_geral.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4), ('TOPPADDING', (0,0), (-1,-1), 4)]))
    story.append(t_geral)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1. Custos de Logística, Deslocamento & Operacionais", style_subtitulo))
    story.append(Spacer(1, 6))
    
    combustivel_detalhe = f"Consumo: {dados['consumo_veiculo']} km/L | {dados['litros_gastos']:.1f}L a {fmt_brl(dados['preco_combustivel'])}/L"
    
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
        [Paragraph("Outros", style_corpo), Paragraph("Despesas diversas", style_corpo), Paragraph(fmt_brl(dados['custo_outros']), style_corpo)]
    ]
    t_log = Table(tabela_log_dados, colWidths=[110, 330, 100])
    ts_log = TableStyle()
    ts_log.add('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9'))
    ts_log.add('ALIGN', (0,0), (-1,-1), 'LEFT')
    ts_log.add('ALIGN', (2,0), (2,-1), 'RIGHT')
    ts_log.add('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ts_log.add('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ts_log.add('TOPPADDING', (0,0), (-1,-1), 4)
    ts_log.add('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    t_log.setStyle(ts_log)
    story.append(t_log)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2. Impostos & Comissão", style_subtitulo))
    story.append(Spacer(1, 6))
    
    tabela_op_dados = [
        [Paragraph("<b>Descrição</b>", style_bold), Paragraph("<b>Base / Alíquota</b>", style_bold), Paragraph("<b>Valor Estimado</b>", style_bold)],
        [Paragraph("Valor Base dos Serviços", style_corpo), Paragraph(f"Tabela ({dados['carga_horaria_sel']})", style_corpo), Paragraph(fmt_brl(dados['valor_base']), style_corpo)],
        [Paragraph("Desconto Aplicado", style_corpo), Paragraph("Desconto comercial", style_corpo), Paragraph(f"- {fmt_brl(dados['valor_desconto_calculado'])}", style_corpo)],
        [Paragraph("Ajuste Manual / Especial", style_corpo), Paragraph("Subtração aplicada", style_corpo), Paragraph(f"- {fmt_brl(dados['ajuste_manual'])}", style_corpo)],
        [Paragraph("Impostos (Nota Fiscal)", style_corpo), Paragraph(f"{dados['imposto_perc']}% sobre o faturamento", style_corpo), Paragraph(fmt_brl(dados['valor_impostos']), style_corpo)],
        [Paragraph("Comissão", style_corpo), Paragraph(f"{dados['comissao_perc']}% sobre o faturamento", style_corpo), Paragraph(fmt_brl(dados['valor_comissao']), style_corpo)]
    ]
    t_op = Table(tabela_op_dados, colWidths=[120, 320, 100])
    ts_op = TableStyle()
    ts_op.add('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9'))
    ts_op.add('ALIGN', (0,0), (-1,-1), 'LEFT')
    ts_op.add('ALIGN', (2,0), (2,-1), 'RIGHT')
    ts_op.add('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ts_op.add('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ts_op.add('TOPPADDING', (0,0), (-1,-1), 4)
    ts_op.add('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    t_op.setStyle(ts_op)
    story.append(t_op)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("3. Fechamento Financeiro & Margem", style_subtitulo))
    story.append(Spacer(1, 6))
    
    tabela_resumo_interno = [
        [Paragraph("<b>Faturamento Total Proposto:</b>", style_bold), Paragraph(f"<b>{fmt_brl(dados['valor_final'])}</b>", style_destaque_fat)],
        [Paragraph("<b>Custo Operacional Total:</b>", style_bold), Paragraph(fmt_brl(dados['custo_total_interno']), style_corpo)],
        [Paragraph("<b>Lucro Líquido Estimado:</b>", style_bold), Paragraph(f"<b>{fmt_brl(dados['lucro_liquido'])} ({dados['margem_lucro']:.1f}%)</b>", style_destaque_lucro)]
    ]
    t_res_int = Table(tabela_resumo_interno, colWidths=[310, 230])
    ts_res = TableStyle()
    ts_res.add('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e2e8f0'))
    ts_res.add('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ts_res.add('ALIGN', (1,0), (1,-1), 'RIGHT')
    ts_res.add('BOTTOMPADDING', (0,0), (-1,-1), 6)
    ts_res.add('TOPPADDING', (0,0), (-1,-1), 6)
    ts_res.add('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1e3a8a'))
    t_res_int.setStyle(ts_res)
    story.append(t_res_int)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

# CABEÇALHO DO SISTEMA COM LOGO CENTRALIZADO
logo_sys_path = get_logo_path()
if logo_sys_path:
    col_vazia1, col_logo, col_vazia2 = st.columns([1, 2, 1])
    with col_logo:
        st.image(logo_sys_path, width=320)

st.markdown("<h1 style='text-align: center;'>⚡ Sistema de Propostas & Custos</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>Gerencie orçamentos comerciais, analise a viabilidade interna e gere documentação profissional em PDF.</p>", unsafe_allow_html=True)
st.markdown("---")

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

tab_names = ["1. Dados & Serviços", "2. Custos & Logística", "3. Prazos, Resumo & Relatórios"]
tabs_topo = st.tabs(tab_names)

with tabs_topo[0]:
    st.subheader("1. Dados do Cliente & Serviço")
    col1, col2 = st.columns(2)
    with col1:
        contato = st.text_input("Contato", "")
        empresa = st.text_input("Empresa", "")
        telefone = st.text_input("Telefone", "")
        email = st.text_input("E-mail", "")
    with col2:
        data_orcamento = st.date_input("Data do Orçamento (dia/mês/ano)", datetime.now())
        data_evento = st.date_input("Data do Serviço (dia/mês/ano)", datetime.now())
        
        tem_data_termino = st.checkbox("Serviço com mais de um dia (Data de Término)")
        data_termino = data_evento
        if tem_data_termino:
            data_termino = st.date_input("Data de Término do Serviço (dia/mês/ano)", datetime.now())
            
        horario = st.text_input("Horário do Serviço", "08:00")
            
        nome_servico_input = st.text_input("Nome do Serviço / Evento", "")
        local = st.text_input("Local", "")
        
        col_cidade, col_uf = st.columns([3, 1])
        with col_cidade:
            cidade = st.text_input("Cidade", "Ribeirão Preto")
        with col_uf:
            estado = st.selectbox("Estado (UF)", ESTADOS_BR, index=0)

    st.markdown("---")
    st.subheader("2. Seleção de Serviço & Carga Horária")
    tipo_servico = st.selectbox("Tipo de Serviço", list(TABELAS_SERVICOS.keys()))
    
    outro_servico_nome = ""
    if tipo_servico == "Outro":
        outro_servico_nome = st.text_input("Especifique o nome do serviço", "")

    carga_horaria_sel = st.selectbox("Carga Horária", OPCOES_CARGA_HORARIA)

    st.markdown("---")
    st.subheader("3. Detalhamento Técnico (Escopo & Captação)")
    
    nome_servico_atual = tipo_servico if tipo_servico != "Outro" else outro_servico_nome
    mes_extenso_ev = MESES_PT[data_evento.month]
    
    if tem_data_termino:
        mes_extenso_ter = MESES_PT[data_termino.month]
        data_str_escopo = f"{data_evento.day} de {mes_extenso_ev} até {data_termino.day} de {mes_extenso_ter} de {data_termino.year}"
    else:
        data_str_escopo = f"{data_evento.day} de {mes_extenso_ev} de {data_evento.year}"

    default_escopo = f"{nome_servico_atual} — {nome_servico_input if nome_servico_input else 'Serviço Profissional'}\n{data_str_escopo}\n{horario if horario else 'Horário a definir'}\n{local if local else 'Local a definir'}\n{cidade} - {estado}\n01 (um) profissional"
    default_captacao = "Cobertura profissional com equipamentos de alto padrão"
    
    escopo_servico = st.text_area("Escopo do serviço", default_escopo, height=150)
    captacao = st.text_area("Captação", default_captacao, height=80)
    
    st.markdown("---")
    if st.button("Avançar ➡️", key="btn_avancar_aba0", use_container_width=True):
        st.session_state.active_tab = 1
        st.rerun()

with tabs_topo[1]:
    st.subheader("Custos operacionais")
    
    st.markdown("##### 🚗 Parâmetros de Deslocamento & Logística")
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        distancia_ida_volta = st.number_input("Distância Total (Ida e Volta em km)", min_value=0, value=0, step=1, format="%d")
    with col_l2:
        consumo_medio = st.number_input("Consumo Médio (km/L)", min_value=1.0, value=11.50, step=0.5)
    with col_l3:
        preco_combustivel = st.number_input("Preço do Litro (R$)", min_value=0.0, value=6.80, step=0.10)
        
    col_est1, col_est2 = st.columns(2)
    with col_est1:
        pedagio_total = st.number_input("Valor Total de Pedágios (R$)", min_value=0.0, value=0.00, step=5.0, format="%.2f")
    with col_est2:
        custo_estacionamento = st.number_input("Estacionamento (R$)", min_value=0.0, value=0.00, step=5.0, format="%.2f")

    st.markdown("---")
    st.markdown("##### 🏨 Hospedagem")
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        qtd_hosp = st.number_input("Qtd. Diárias Hospedagem", min_value=0, value=0, step=1)
    with col_h2:
        val_hosp = st.number_input("R$ Hospedagem (diária)", min_value=0.0, value=250.00, step=10.0, format="%.2f")

    custo_hospedagem_total = qtd_hosp * val_hosp

    st.markdown("---")
    st.markdown("##### 🍽️ Alimentação")
    col_alim1, col_alim2 = st.columns(2)
    with col_alim1:
        custo_almoco = st.number_input("Almoço (R$)", min_value=0.0, value=0.00, step=5.0, format="%.2f")
    with col_alim2:
        custo_jantar = st.number_input("Jantar (R$)", min_value=0.0, value=0.00, step=5.0, format="%.2f")

    st.markdown("---")
    st.markdown("##### 📦 Outros Custos")
    col_ap1, col_ap2 = st.columns(2)
    with col_ap1:
        custo_freelancer = st.number_input("Freelancer (R$)", min_value=0.0, value=0.00, step=50.0, format="%.2f")
    with col_ap2:
        custo_outros = st.number_input("Outros (R$)", min_value=0.0, value=0.00, step=10.0, format="%.2f")

    st.markdown("---")
    st.subheader("Impostos & Comissão")
    col_op1, col_op2, col_op3 = st.columns(3)
    with col_op1:
        imposto_perc = st.number_input("Alíquota de Impostos / Notas (%)", min_value=0.0, max_value=30.0, value=6.0, step=0.5)
    with col_op2:
        comissao_perc = st.number_input("Comissão (%)", min_value=0, max_value=50, value=0, step=1, format="%d")
    with col_op3:
        ajuste_manual = st.number_input("Ajuste Manual do Valor Final (R$ - Subtração)", min_value=0.0, value=0.0, step=10.0, format="%.2f")

    st.markdown("---")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("⬅️ Voltar", key="btn_voltar_aba1", use_container_width=True):
            st.session_state.active_tab = 0
            st.rerun()
    with col_b2:
        if st.button("Avançar ➡️", key="btn_avancar_aba1", use_container_width=True):
            st.session_state.active_tab = 2
            st.rerun()

with tabs_topo[2]:
    st.subheader("Validade do Orçamento, Forma de Entrega & Pagamento")
    validade_orcamento = st.text_input("Validade do Orçamento", "05 dias")
    forma_entrega = st.text_input("Forma de entrega", "Link exclusivo para download, disponível por 30 dias.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        forma_pagamento_tipo = st.selectbox("Forma de Pagamento", ["À vista", "Parcelado"])
    with col_p2:
        condicao_pagamento = st.selectbox("Condições de Pagamento", ["PIX", "Transferência", "PIX ou transferência bancária", "Cartão de crédito", "Cartão de Crédito parcelado"])
    
    parcelas_cartao = 1
    if "parcelado" in condicao_pagamento.lower() or forma_pagamento_tipo == "Parcelado":
        parcelas_cartao = st.number_input("Cartão de Crédito parcelado em X vezes", min_value=1, max_value=12, value=3)
        condicao_pagamento = f"{condicao_pagamento} em {parcelas_cartao}X"

    st.markdown("---")
    st.subheader("Descontos & Condições Comerciais")
    col_desc1, col_desc2 = st.columns(2)
    with col_desc1:
        tipo_desc_modo = st.radio("Modalidade de Desconto", ["Porcentagem (%)", "Valor Fixo (R$)"], horizontal=True)
    with col_desc2:
        if tipo_desc_modo == "Porcentagem (%)":
            desconto_perc = st.slider("Desconto (%)", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
            desconto_valor_input = 0.0
        else:
            desconto_perc = 0.0
            desconto_valor_input = st.number_input("Desconto em Valor Fixo (R$)", min_value=0.0, value=0.0, step=10.0, format="%.2f")

    st.markdown("---")
    if st.button("⬅️ Voltar", key="btn_voltar_aba2", use_container_width=True):
        st.session_state.active_tab = 1
        st.rerun()

# CÁLCULOS DINÂMICOS EM TEMPO REAL
try:
    servico_nome = tipo_servico if tipo_servico != "Outro" else outro_servico_nome
    nome_serv_ev = nome_servico_input if 'nome_servico_input' in locals() and nome_servico_input else servico_nome
    
    tabela_atual = TABELAS_SERVICOS.get(tipo_servico, TABELAS_SERVICOS["Evento social"])
    
    dias_evento = 1
    if 'tem_data_termino' in locals() and tem_data_termino:
        dias_evento = max(1, (data_termino - data_evento).days + 1)

    if "diária" in carga_horaria_sel:
        qtd_diarias = int(carga_horaria_sel.split()[0])
        valor_base = tabela_atual.get(10, 1300.0) * qtd_diarias * dias_evento
    else:
        horas_num = int(carga_horaria_sel.replace("h", ""))
        horas_buscadas = min(horas_num, 12)
        valor_base = tabela_atual.get(horas_buscadas, 1500.0) * dias_evento
        if horas_num > 12:
            valor_base += (horas_num - 12) * tabela_atual.get(1, 180.0) * dias_evento

    desp_perc = desconto_perc if 'desconto_perc' in locals() else 0.0
    desp_val = desconto_valor_input if 'desconto_valor_input' in locals() else 0.0
    aj_man = ajuste_manual if 'ajuste_manual' in locals() else 0.0
    
    if desp_perc > 0:
        valor_desconto_calculado = valor_base * (desp_perc / 100.0)
    else:
        valor_desconto_calculado = desp_val

    valor_intermediario = valor_base - valor_desconto_calculado - aj_man
    valor_final = max(0.0, valor_intermediario)

    dist_iv = distancia_ida_volta if 'distancia_ida_volta' in locals() else 0
    cons_m = consumo_medio if 'consumo_medio' in locals() else 11.5
    p_comb = preco_combustivel if 'preco_combustivel' in locals() else 6.8
    ped_tot = pedagio_total if 'pedagio_total' in locals() else 0.0
    est_c = custo_estacionamento if 'custo_estacionamento' in locals() else 0.0
    
    litros_gastos = dist_iv / cons_m if cons_m > 0 else 0
    custo_combustivel = litros_gastos * p_comb
    custo_logistica_total = custo_combustivel + ped_tot + est_c

    hosp_tot = custo_hospedagem_total if 'custo_hospedagem_total' in locals() else 0.0
    alm_c = custo_almoco if 'custo_almoco' in locals() else 0.0
    jan_c = custo_jantar if 'custo_jantar' in locals() else 0.0
    free_c = custo_freelancer if 'custo_freelancer' in locals() else 0.0
    out_c = custo_outros if 'custo_outros' in locals() else 0.0

    custo_total_operacional_log = custo_logistica_total + hosp_tot + alm_c + jan_c + free_c + out_c
    
    imp_p = imposto_perc if 'imposto_perc' in locals() else 6.0
    com_p = comissao_perc if 'comissao_perc' in locals() else 0
    
    valor_impostos = valor_final * (imp_p / 100.0)
    valor_comissao = valor_final * (com_p / 100.0)
    
    custo_total_interno = custo_total_operacional_log + valor_impostos + valor_comissao
    lucro_liquido = valor_final - custo_total_interno
    margem_lucro = (lucro_liquido / valor_final * 100) if valor_final > 0 else 0
except Exception:
    valor_base = 0.0
    valor_desconto_calculado = 0.0
    valor_final = 0.0
    dist_iv = 0
    cons_m = 11.5
    litros_gastos = 0.0
    p_comb = 6.8
    custo_combustivel = 0.0
    ped_tot = 0.0
    est_c = 0.0
    hosp_tot = 0.0
    alm_c = 0.0
    jan_c = 0.0
    free_c = 0.0
    out_c = 0.0
    custo_total_interno = 0.0
    lucro_liquido = 0.0
    margem_lucro = 0.0
    valor_impostos = 0.0
    valor_comissao = 0.0

# QUADRO DE PRÉVIA EM TEMPO REAL FIXO ABAIXO DAS ABAS
st.markdown("---")
st.markdown("### 📈 Quadro de Prévia em Tempo Real (Visão Geral)")
col_res1, col_res2, col_res3, col_res4 = st.columns(4)
col_res1.metric("Valor para o Cliente", fmt_brl(valor_final))
col_res2.metric("Custos Operacionais", fmt_brl(custo_total_interno))
col_res3.metric("Lucro Líquido Est.", fmt_brl(lucro_liquido))
col_res4.metric("Margem de Lucro", f"{margem_lucro:.1f}%")

dados_completos = {}
dados_completos["contato"] = contato if 'contato' in locals() else ""
dados_completos["empresa"] = empresa if 'empresa' in locals() else ""
dados_completos["telefone"] = telefone if 'telefone' in locals() else ""
dados_completos["email"] = email if 'email' in locals() else ""
dados_completos["data_orcamento"] = data_orcamento if 'data_orcamento' in locals() else datetime.now()
dados_completos["data_evento"] = data_evento if 'data_evento' in locals() else datetime.now()
dados_completos["tem_data_termino"] = tem_data_termino if 'tem_data_termino' in locals() else False
dados_completos["data_termino"] = data_termino if 'data_termino' in locals() else datetime.now()
dados_completos["horario"] = horario if 'horario' in locals() else "08:00"
dados_completos["nome_servico_input"] = nome_servico_input if 'nome_servico_input' in locals() else ""
dados_completos["local"] = local if 'local' in locals() else ""
dados_completos["cidade"] = cidade if 'cidade' in locals() else "Ribeirão Preto"
dados_completos["estado"] = estado if 'estado' in locals() else "SP"
dados_completos["tipo_servico"] = tipo_servico if 'tipo_servico' in locals() else "Evento social"
dados_completos["outro_servico_nome"] = outro_servico_nome if 'outro_servico_nome' in locals() else ""
dados_completos["carga_horaria_sel"] = carga_horaria_sel if 'carga_horaria_sel' in locals() else "1h"
dados_completos["escopo_servico"] = escopo_servico if 'escopo_servico' in locals() else ""
dados_completos["captacao"] = captacao if 'captacao' in locals() else ""
dados_completos["validade_orcamento"] = validade_orcamento if 'validade_orcamento' in locals() else "05 dias"
dados_completos["forma_entrega"] = forma_entrega if 'forma_entrega' in locals() else ""
dados_completos["forma_pagamento_tipo"] = forma_pagamento_tipo if 'forma_pagamento_tipo' in locals() else "À vista"
dados_completos["condicao_pagamento"] = condicao_pagamento if 'condicao_pagamento' in locals() else "PIX"
dados_completos["desconto_perc"] = desp_perc if 'desp_perc' in locals() else 0.0
dados_completos["ajuste_manual"] = aj_man if 'ajuste_manual' in locals() else 0.0
dados_completos["valor_base"] = valor_base
dados_completos["valor_desconto_calculado"] = valor_desconto_calculado
dados_completos["valor_final"] = valor_final
dados_completos["distancia"] = dist_iv
dados_completos["consumo_veiculo"] = cons_m
dados_completos["litros_gastos"] = litros_gastos
dados_completos["preco_combustivel"] = p_comb
dados_completos["custo_combustivel"] = custo_combustivel
dados_completos["pedagios"] = ped_tot
dados_completos["custo_estacionamento"] = est_c
dados_completos["custo_hospedagem_total"] = hosp_tot
dados_completos["custo_almoco"] = alm_c
dados_completos["custo_jantar"] = jan_c
dados_completos["custo_freelancer"] = free_c
dados_completos["custo_outros"] = out_c
dados_completos["imposto_perc"] = imp_p if 'imp_p' in locals() else 6.0
dados_completos["valor_impostos"] = valor_impostos
dados_completos["comissao_perc"] = com_p if 'com_p' in locals() else 0
dados_completos["valor_comissao"] = valor_comissao
dados_completos["custo_total_interno"] = custo_total_interno
dados_completos["lucro_liquido"] = lucro_liquido
dados_completos["margem_lucro"] = margem_lucro

# EXIBIÇÃO APENAS NA ABA 3 DA GERAÇÃO DE DOCUMENTOS (PDF)
st.markdown("---")
st.subheader("📥 Geração de Documentos (PDF)")
col_down1, col_down2 = st.columns(2)

with col_down1:
    pdf_cliente_bytes = gerar_pdf_cliente(dados_completos)
    st.download_button(
        label="📄 Baixar Proposta Comercial (Cliente)",
        data=pdf_cliente_bytes,
        file_name=f"Proposta_Comercial_{empresa.replace(' ', '_')}.pdf" if 'empresa' in locals() and empresa else "Proposta_Comercial.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with col_down2:
    pdf_interno_bytes = gerar_pdf_interno(dados_completos)
    st.download_button(
        label="🔒 Baixar Relatório Interno (Custos)",
        data=pdf_interno_bytes,
        file_name=f"Relatorio_Interno_Custos_{empresa.replace(' ', '_')}.pdf" if 'empresa' in locals() and empresa else "Relatorio_Interno_Custos.pdf",
        mime="application/pdf",
        use_container_width=True
    )

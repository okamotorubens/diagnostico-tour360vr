import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.pdfgen import canvas
import io
import os
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO DE ESTILO E FORMATAÇÃO BRL
# ==========================================
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

# ==========================================
# CANVAS PROFISSIONAL (RODAPÉ FIXO NA BASE)
# ==========================================
class ModernCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_fixed_footer()
            super().showPage()
        super().save()

    def draw_fixed_footer(self):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Linha separadora rigorosamente no rodapé inferior (Y = 32)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(35, 38, 575, 38)
        
        footer_text = "Okamoto Mídias Visuais    |    okamotomidiasvisuais.com.br    |    contato@okamotomidiasvisuais.com.br    |    WhatsApp: 16 99133 2121"
        self.drawCentredString(305, 24, footer_text)
        self.restoreState()

def get_logo_path():
    caminhos = ["logo_okamoto.png", "./logo_okamoto.png", os.path.join(os.getcwd(), "logo_okamoto.png")]
    for c in caminhos:
        if os.path.exists(c):
            return c
    return None

# ==========================================
# FUNÇÃO 1: GERAR PDF DA PROPOSTA COMERCIAL
# ==========================================
def gerar_pdf_cliente(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=25, bottomMargin=50)
    
    nome_servico_titulo = dados['tipo_servico'] if dados['tipo_servico'] != "Outro" else dados['outro_servico_nome']
    doc.title = f"Proposta comercial - {nome_servico_titulo}"
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('TituloPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, alignment=1, textColor=colors.HexColor('#0f172a'))
    style_servico_sub = ParagraphStyle('ServSubPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=17, alignment=1, textColor=colors.HexColor('#0f172a'))
    style_corpo = ParagraphStyle('CorpoPDF', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=14.5, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('BoldPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=14.5, textColor=colors.HexColor('#0f172a'))
    style_assinatura = ParagraphStyle('AssinaturaPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#0f172a'))
    style_cat_titulo = ParagraphStyle('CatTitPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=colors.HexColor('#0f172a'))
    style_destaque_1 = ParagraphStyle('Dest1PDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, leading=20, alignment=1, textColor=colors.HexColor('#0f172a'))
    style_destaque_2 = ParagraphStyle('Dest2PDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16, alignment=1, textColor=colors.HexColor('#64748b'))
    style_rodape = ParagraphStyle('RodapePDF', parent=styles['Normal'], fontName='Helvetica', fontSize=8, alignment=1, textColor=colors.HexColor('#64748b'))
    
    story = []

    logo_path = get_logo_path()
    if logo_path:
        img = RLImage(logo_path, width=140, height=52)
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
    story.append(Spacer(1, 6))
    story.append(Paragraph(nome_servico_titulo, style_servico_sub))
    story.append(Spacer(1, 14))
    
    story.append(Paragraph("<b>1. Dados do cliente:</b>", style_bold))
    texto_cliente = f"<b>Contato:</b> {dados['contato']} &nbsp;|&nbsp; <b>Empresa:</b> {dados['empresa']} &nbsp;|&nbsp; <b>Tel:</b> {dados['telefone']} &nbsp;|&nbsp; <b>E-mail:</b> {dados['email']}"
    story.append(Paragraph(texto_cliente, style_corpo))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>2. Data do evento:</b>", style_bold))
    data_ev_str = dados['data_evento'].strftime('%d/%m/%Y')
    if dados['tem_data_termino']:
        data_ev_str += f" até {dados['data_termino'].strftime('%d/%m/%Y')}"
    texto_evento = f"<b>Data:</b> {data_ev_str} &nbsp;&nbsp; <b>Horário:</b> {dados['horario']} &nbsp;&nbsp; <b>Local:</b> {dados['local']} — {dados['cidade']}/{dados['estado']}"
    story.append(Paragraph(texto_evento, style_corpo))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>3. Serviço:</b>", style_bold))
    story.append(Paragraph(nome_servico_titulo, style_corpo))
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
    if dados['desconto_perc'] > 0:
        texto_valor = f"<b>Valor Total do Investimento ({dados['carga_horaria_sel']}):</b> {val_fmt} <i>(Já inclusos {dados['desconto_perc']}% de desconto)</i>"
    else:
        texto_valor = f"<b>Valor Total do Investimento ({dados['carga_horaria_sel']}):</b> {val_fmt}"
        
    story.append(Paragraph(texto_valor, ParagraphStyle('ValDarkPDF', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#0f172a'))))
    story.append(Spacer(1, 14))
    
    story.append(Paragraph("Ficamos à disposição para quaisquer esclarecimentos e ajustes, caso necessário.", style_corpo))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Atenciosamente,", style_corpo))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Rubens Okamoto", style_assinatura))
    story.append(Paragraph("Okamoto Mídias Visuais", style_corpo))
    
    story.append(Spacer(1, 15))
    texto_rodape = 'Okamoto Mídias Visuais &nbsp;&nbsp;|&nbsp;&nbsp; <a href="https://okamotomidiasvisuais.com.br" target="_blank" color="#64748b">okamotomidiasvisuais.com.br</a> &nbsp;&nbsp;|&nbsp;&nbsp; contato@okamotomidiasvisuais.com.br &nbsp;&nbsp;|&nbsp;&nbsp; <a href="https://wa.me/5516991332121" target="_blank" color="#64748b">WhatsApp: 16 99133 2121</a>'
    story.append(Paragraph(texto_rodape, style_rodape))
    
    # 2ª PÁGINA (INSTITUCIONAL)
    story.append(PageBreak())
    
    if logo_path:
        img_inst = RLImage(logo_path, width=150, height=56)
        img_inst.hAlign = 'CENTER'
        story.append(img_inst)
    else:
        story.append(Paragraph("<b>[ OKAMOTO MÍDIAS VISUAIS ]</b>", style_titulo))
        
    story.append(Spacer(1, 16))
    
    story.append(Paragraph("É registrando a sua história, que nós construímos a nossa!", style_destaque_1))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Especialistas em Imagem, Vídeo e Experiências Imersivas", style_destaque_2))
    story.append(Spacer(1, 22))
    
    intro_inst = "Unimos a bagagem de três décadas às inovações tecnológicas mais recentes, transformando sua marca com soluções visuais de alta performance:"
    story.append(Paragraph(intro_inst, style_corpo))
    story.append(Spacer(1, 14))
    
    topicos_inst = "<b>• Fotografia Corporativa e Estratégica:</b><br/>Imagens que reforçam a autoridade da sua empresa e destacam seu negócio no mercado.<br/><br/><b>• Tours Virtuais 360º:</b><br/>Experiências imersivas que levam seu cliente para dentro do seu espaço físico.<br/><br/><b>• Vídeos de Alto Impacto:</b><br/>Produções pensadas para converter e engajar seu público em redes sociais e plataformas digitais."
    story.append(Paragraph(topicos_inst, style_corpo))
    story.append(Spacer(1, 24))
    
    story.append(Paragraph("Dados da Empresa", style_cat_titulo))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Okamoto Reportagens Fotográficas SS Ltda<br/><b>CNPJ:</b> 04.824.331/0001-05<br/>Rua General Carneiro, 860 — Centro, Brodowski - SP<br/>CEP: 14.340-023", style_corpo))
    story.append(Spacer(1, 16))
    
    story.append(Paragraph("Dados Pessoais", style_cat_titulo))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Rubens Heigasi Okamoto</b><br/><b>CPF:</b> 287.932.298-79 &nbsp;|&nbsp; <b>RG:</b> 25.450.624-0 SSP/SP<br/><b>Tel. Cel.:</b> 16 99133 2121 &nbsp;|&nbsp; <b>E-mail:</b> contato@okamotomidiasvisuais.com.br", style_corpo))
    story.append(Spacer(1, 16))
    
    story.append(Paragraph("Dados Bancários", style_cat_titulo))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Banco do Brasil</b><br/><b>Agência:</b> 3235-2 &nbsp;|&nbsp; <b>C. Corrente:</b> 11.935-0<br/><b>Chave PIX:</b> 04824331000105", style_corpo))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(texto_rodape, style_rodape))

    doc.build(story, canvasmaker=ModernCanvas)
    buffer.seek(0)
    return buffer

# ==========================================
# FUNÇÃO 2: GERAR RELATÓRIO INTERNO (CUSTOS - 1 PÁGINA)
# ==========================================
def gerar_pdf_interno(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=20, bottomMargin=40)
    
    servico_exibido = dados['tipo_servico'] if dados['tipo_servico'] != "Outro" else dados['outro_servico_nome']
    data_ev_str = dados['data_evento'].strftime('%d/%m/%Y')
    doc.title = f"Relatório interno - {servico_exibido} - {data_ev_str}"
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('TitInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=18, alignment=1, textColor=colors.HexColor('#0f172a'))
    style_subtitulo = ParagraphStyle('SubInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor('#2563eb'))
    style_corpo = ParagraphStyle('CorpoInt', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11.5, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('BoldInt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11.5, textColor=colors.HexColor('#0f172a'))
    
    story = []

    logo_path = get_logo_path()
    if logo_path:
        img_int = RLImage(logo_path, width=110, height=41)
        img_int.hAlign = 'CENTER'
        story.append(img_int)
    else:
        story.append(Paragraph("<b>[ LOGO OKAMOTO ]</b>", style_bold))
        
    story.append(Spacer(1, 6))
    story.append(Paragraph("Relatório Interno de Viabilidade & Custos", style_titulo))
    story.append(Spacer(1, 8))
    
    data_fim_str = dados['data_termino'].strftime('%d/%m/%Y') if dados['tem_data_termino'] else data_ev_str
    
    info_geral = [
        [Paragraph("<b>Cliente:</b>", style_bold), Paragraph(dados['contato'], style_corpo), Paragraph("<b>Data de Início:</b>", style_bold), Paragraph(data_ev_str, style_corpo)],
        [Paragraph("<b>Empresa:</b>", style_bold), Paragraph(dados['empresa'], style_corpo), Paragraph("<b>Data de Término:</b>", style_bold), Paragraph(data_fim_str, style_corpo)],
        [Paragraph("<b>Serviço:</b>", style_bold), Paragraph(servico_exibido, style_corpo), Paragraph("<b>Carga Horária:</b>", style_bold), Paragraph(dados['carga_horaria_sel'], style_corpo)]
    ]
    t_geral = Table(info_geral, colWidths=[80, 185, 95, 145])
    t_geral.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 2), ('TOPPADDING', (0,0), (-1,-1), 2)]))
    story.append(t_geral)
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("1. Custos de Logística, Deslocamento & Operacionais", style_subtitulo))
    story.append(Spacer(1, 4))
    
    tabela_log_dados = [
        [Paragraph("<b>Parâmetro</b>", style_bold), Paragraph("<b>Detalhe / Métrica</b>", style_bold), Paragraph("<b>Custo Parcial</b>", style_bold)],
        [Paragraph("Distância Total", style_corpo), Paragraph(f"{dados['distancia']} km (Ida e Volta)", style_corpo), Paragraph("-", style_corpo)],
        [Paragraph("Combustível", style_corpo), Paragraph(f"Consumo: {dados['consumo_veiculo']} km/L | {dados['litros_gastos']:.1f}L a {fmt_brl(dados['preco_combustivel'])}/L", style_corpo), Paragraph(fmt_brl(dados['custo_combustivel']), style_corpo)],
        [Paragraph("Pedágios", style_corpo), Paragraph("Tarifas de estrada", style_corpo), Paragraph(fmt_brl(dados['pedagios']), style_corpo)],
        [Paragraph("Hospedagem", style_corpo), Paragraph("Diárias de hospedagem", style_corpo), Paragraph(fmt_brl(dados['custo_hospedagem_total']), style_corpo)],
        [Paragraph("Almoço", style_corpo), Paragraph("Refeição", style_corpo), Paragraph(fmt_brl(dados['custo_almoco']), style_corpo)],
        [Paragraph("Jantar", style_corpo), Paragraph("Refeição", style_corpo), Paragraph(fmt_brl(dados['custo_jantar']), style_corpo)],
        [Paragraph("Estacionamento", style_corpo), Paragraph("Estacionamento / Local", style_corpo), Paragraph(fmt_brl(dados['custo_estacionamento']), style_corpo)],
        [Paragraph("Freelancer", style_corpo), Paragraph("Apoio profissional extra", style_corpo), Paragraph(fmt_brl(dados['custo_freelancer']), style_corpo)],
        [Paragraph("Outros", style_corpo), Paragraph("Despesas diversas", style_corpo), Paragraph(fmt_brl(dados['custo_outros']), style_corpo)]
    ]
    t_log = Table(tabela_log_dados, colWidths=[120, 285, 100])
    ts_log = TableStyle()
    ts_log.add('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9'))
    ts_log.add('ALIGN', (0,0), (-1,-1), 'LEFT')
    ts_log.add('ALIGN', (2,0), (2,-1), 'RIGHT')
    ts_log.add('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ts_log.add('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ts_log.add('TOPPADDING', (0,0), (-1,-1), 3)
    ts_log.add('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    t_log.setStyle(ts_log)
    story.append(t_log)
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("2. Custos Operacionais & Impostos", style_subtitulo))
    story.append(Spacer(1, 4))
    
    tabela_op_dados = [
        [Paragraph("<b>Descrição</b>", style_bold), Paragraph("<b>Base / Alíquota</b>", style_bold), Paragraph("<b>Valor Estimado</b>", style_bold)],
        [Paragraph("Valor Base dos Serviços", style_corpo), Paragraph(f"Tabela ({dados['carga_horaria_sel']})", style_corpo), Paragraph(fmt_brl(dados['valor_base']), style_corpo)],
        [Paragraph("Desconto Aplicado", style_corpo), Paragraph(f"{dados['desconto_perc']}% de desconto comercial", style_corpo), Paragraph(f"- {fmt_brl(dados['valor_desconto'])}", style_corpo)],
        [Paragraph("Impostos (Nota Fiscal)", style_corpo), Paragraph(f"{dados['imposto_perc']}% sobre o faturamento", style_corpo), Paragraph(fmt_brl(dados['valor_impostos']), style_corpo)],
        [Paragraph("Outros Custos / Extras", style_corpo), Paragraph("Insumos gerais", style_corpo), Paragraph(fmt_brl(dados['custo_extra']), style_corpo)]
    ]
    t_op = Table(tabela_op_dados, colWidths=[130, 275, 100])
    ts_op = TableStyle()
    ts_op.add('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9'))
    ts_op.add('ALIGN', (0,0), (-1,-1), 'LEFT')
    ts_op.add('ALIGN', (2,0), (2,-1), 'RIGHT')
    ts_op.add('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ts_op.add('BOTTOMPADDING', (0,0), (-1,-1), 3)
    ts_op.add('TOPPADDING', (0,0), (-1,-1), 3)
    ts_op.add('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    t_op.setStyle(ts_op)
    story.append(t_op)
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("3. Fechamento Financeiro & Margem", style_subtitulo))
    story.append(Spacer(1, 4))
    
    tabela_resumo_interno = [
        [Paragraph("<b>Faturamento Total Proposto:</b>", style_bold), Paragraph(f"<b>{fmt_brl(dados['valor_final'])}</b>", style_corpo)],
        [Paragraph("<b>Custo Operacional Total:</b>", style_bold), Paragraph(fmt_brl(dados['custo_total_interno']), style_corpo)],
        [Paragraph("<b>Lucro Líquido Estimado:</b>", style_bold), Paragraph(f"<b>{fmt_brl(dados['lucro_liquido'])} ({dados['margem_lucro']:.1f}%)</b>", style_bold)]
    ]
    t_res_int = Table(tabela_resumo_interno, colWidths=[305, 200])
    ts_res = TableStyle()
    ts_res.add('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e2e8f0'))
    ts_res.add('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ts_res.add('ALIGN', (1,0), (1,-1), 'RIGHT')
    ts_res.add('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ts_res.add('TOPPADDING', (0,0), (-1,-1), 4)
    ts_res.add('BOX', (0,0), (-1,-1), 1, colors.HexColor('#475569'))
    t_res_int.setStyle(ts_res)
    story.append(t_res_int)
    
    doc.build(story, canvasmaker=ModernCanvas)
    buffer.seek(0)
    return buffer

# ==========================================
# INTERFACE DO USUÁRIO - STREAMLIT
# ==========================================
st.title("⚡ Sistema de Propostas & Custos")
st.markdown("Gerencie orçamentos comerciais, analise a viabilidade interna e gere documentação profissional em PDF.")

logo_path = get_logo_path()
if logo_path:
    col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
    with col_img2:
        st.image(logo_path, width=340)

tabs_topo = st.tabs(["1. Dados & Serviços", "2. Custos & Logística", "3. Prazos, Resumo & Relatórios"])

with tabs_topo[0]:
    st.subheader("1. Dados do Cliente & Evento")
    col1, col2 = st.columns(2)
    with col1:
        contato = st.text_input("Contato", "")
        empresa = st.text_input("Empresa", "")
        telefone = st.text_input("Telefone", "")
        email = st.text_input("E-mail", "")
    with col2:
        data_orcamento = st.date_input("Data do Orçamento", datetime.now())
        data_evento = st.date_input("Data do Evento", datetime.now())
        
        tem_data_termino = st.checkbox("Evento com mais de um dia (Data de Término)")
        data_termino = data_evento
        if tem_data_termino:
            data_termino = st.date_input("Data de Término do Evento", datetime.now())
            
        horario = st.text_input("Horário (ex: 08h00 às 18h00)", placeholder="00h00 às 00h00")
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
    
    opcoes_desconto_base = [0, 5, 10, 15, 20, 25, 30]
    tipo_desc = st.radio("Selecione a modalidade de desconto", ["Padrão", "Personalizado (Outro valor)"], horizontal=True)
    if tipo_desc == "Padrão":
        desconto_perc = st.selectbox("Aplicar Desconto (%)", opcoes_desconto_base)
    else:
        desconto_perc = st.number_input("Digite a porcentagem de desconto (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)

    st.markdown("---")
    st.subheader("3. Detalhamento Técnico (Escopo & Captação)")
    
    nome_servico_atual = tipo_servico if tipo_servico != "Outro" else outro_servico_nome
    mes_extenso_ev = MESES_PT[data_evento.month]
    
    if tem_data_termino:
        mes_extenso_ter = MESES_PT[data_termino.month]
        data_str_escopo = f"{data_evento.day} de {mes_extenso_ev} até {data_termino.day} de {mes_extenso_ter} de {data_termino.year}"
    else:
        data_str_escopo = f"{data_evento.day} de {mes_extenso_ev} de {data_evento.year}"

    default_escopo = f"{nome_servico_atual}\n{data_str_escopo}\n{horario if horario else 'Horário a definir'}\n{local if local else 'Local a definir'}\n{cidade} - {estado}\n01 (um) profissional"
    default_captacao = "Cobertura fotográfica do evento"
    
    escopo_servico = st.text_area("Escopo do serviço", default_escopo, height=90)
    captacao = st.text_area("Captação", default_captacao, height=60)

with tabs_topo[1]:
    st.subheader("🚗 Parâmetros de Deslocamento & Logística (Honda HR-V)")
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        distancia_ida_volta = st.number_input("Distância Total (Ida e Volta em km)", min_value=0, value=0, step=1, format="%d")
    with col_l2:
        consumo_medio = st.number_input("Consumo Médio (km/L)", min_value=1.0, value=11.50, step=0.5)
    with col_l3:
        preco_combustivel = st.number_input("Preço do Litro (R$)", min_value=0.0, value=6.80, step=0.10)
        
    pedagio_total = st.number_input("Valor Total de Pedágios (R$)", min_value=0.0, value=0.0, step=5.0)

    st.markdown("---")
    st.subheader("🏨 Hospedagem & Custos Operacionais")
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        qtd_hosp = st.number_input("Qtd. Diárias Hospedagem", min_value=0, value=0, step=1)
        val_hosp_input = st.number_input("R$ Hospedagem (diária)", min_value=0.0, value=150.00, step=10.0, format="%.2f")
        val_hosp = val_hosp_input * 100 if val_hosp_input < 1000 and val_hosp_input % 1 != 0 else val_hosp_input
    with col_h2:
        almoco_in = st.number_input("Almoço (R$)", min_value=0.0, value=0.00, step=10.0, format="%.2f")
        custo_almoco = almoco_in * 100 if almoco_in < 1000 and almoco_in % 1 != 0 else almoco_in
        
        jantar_in = st.number_input("Jantar (R$)", min_value=0.0, value=0.00, step=10.0, format="%.2f")
        custo_jantar = jantar_in * 100 if jantar_in < 1000 and jantar_in % 1 != 0 else jantar_in
    with col_h3:
        estac_in = st.number_input("Estacionamento (R$)", min_value=0.0, value=0.00, step=5.0, format="%.2f")
        custo_estacionamento = estac_in * 100 if estac_in < 1000 and estac_in % 1 != 0 else estac_in
        
        free_in = st.number_input("Freelancer (R$)", min_value=0.0, value=0.00, step=50.0, format="%.2f")
        custo_freelancer = free_in * 100 if free_in < 1000 and free_in % 1 != 0 else free_in
        
        outros_in = st.number_input("Outros (R$)", min_value=0.0, value=0.00, step=10.0, format="%.2f")
        custo_outros = outros_in * 100 if outros_in < 1000 and outros_in % 1 != 0 else outros_in

    custo_hospedagem_total = qtd_hosp * val_hosp

    st.markdown("---")
    st.subheader("💼 Custos Operacionais & Impostos (Uso Interno)")
    col_op1, col_op2 = st.columns(2)
    with col_op1:
        imposto_perc = st.number_input("Alíquota de Impostos / Notas (%)", min_value=0.0, max_value=30.0, value=6.0, step=0.5)
    with col_op2:
        extra_in = st.number_input("Outros Custos / Extras (R$)", min_value=0.0, value=0.00, step=10.0, format="%.2f")
        custo_extra = extra_in * 100 if extra_in < 1000 and extra_in % 1 != 0 else extra_in

with tabs_topo[2]:
    st.subheader("Condições Comerciais & Pagamento")
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

    tabela_atual = TABELAS_SERVICOS.get(tipo_servico, TABELAS_SERVICOS["Evento social"])
    
    dias_evento = 1
    if tem_data_termino:
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

    valor_desconto = valor_base * (desconto_perc / 100.0)
    valor_final = valor_base - valor_desconto

    litros_gastos = distancia_ida_volta / consumo_medio if consumo_medio > 0 else 0
    custo_combustivel = litros_gastos * preco_combustivel
    custo_logistica_total = custo_combustivel + pedagio_total

    custo_total_operacional_log = custo_logistica_total + custo_hospedagem_total + custo_almoco + custo_jantar + custo_estacionamento + custo_freelancer + custo_outros
    valor_impostos = valor_final * (imposto_perc / 100.0)
    custo_total_interno = custo_total_operacional_log + valor_impostos + custo_extra
    lucro_liquido = valor_final - custo_total_interno
    margem_lucro = (lucro_liquido / valor_final * 100) if valor_final > 0 else 0

    st.markdown("---")
    st.subheader("📊 Painel Resumo: Cliente vs. Interno")
    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    col_res1.metric("Valor para o Cliente", fmt_brl(valor_final))
    col_res2.metric("Custos Operacionais", fmt_brl(custo_total_interno))
    col_res3.metric("Lucro Líquido Est.", fmt_brl(lucro_liquido))
    col_res4.metric("Margem de Lucro", f"{margem_lucro:.1f}%")

    dados_completos = {
        "contato": contato,
        "empresa": empresa,
        "telefone": telefone,
        "email": email,
        "data_orcamento": data_orcamento,
        "data_evento": data_evento,
        "tem_data_termino": tem_data_termino,
        "data_termino": data_termino,
        "horario": horario,
        "local": local,
        "cidade": cidade,
        "estado": estado,
        "tipo_servico": tipo_servico,
        "outro_servico_nome": outro_servico_nome,
        "carga_horaria_sel": carga_horaria_sel,
        "escopo_servico": escopo_servico,
        "captacao": captacao,
        "validade_orcamento": validade_orcamento,
        "forma_entrega": forma_entrega,
        "forma_pagamento_tipo": forma_pagamento_tipo,
        "condicao_pagamento": condicao_pagamento,
        "desconto_perc": desconto_perc,
        "valor_base": valor_base,
        "valor_desconto": valor_desconto,
        "valor_final": valor_final,
        "distancia": distancia_ida_volta,
        "consumo_veiculo": consumo_medio,
        "litros_gastos": litros_gastos,
        "preco_combustivel": preco_combustivel,
        "custo_combustivel": custo_combustivel,
        "pedagios": pedagio_total,
        "custo_hospedagem_total": custo_hospedagem_total,
        "custo_almoco": custo_almoco,
        "custo_jantar": custo_jantar,
        "custo_estacionamento": custo_estacionamento,
        "custo_freelancer": custo_freelancer,
        "custo_outros": custo_outros,
        "imposto_perc": imposto_perc,
        "valor_impostos": valor_impostos,
        "custo_extra": custo_extra,
        "custo_total_interno": custo_total_interno,
        "lucro_liquido": lucro_liquido,
        "margem_lucro": margem_lucro
    }

    st.markdown("---")
    st.markdown("### 📥 Geração de Documentos (PDF)")
    col_down1, col_down2 = st.columns(2)

    with col_down1:
        pdf_cliente_bytes = gerar_pdf_cliente(dados_completos)
        st.download_button(
            label="📄 Baixar Proposta Comercial (Cliente)",
            data=pdf_cliente_bytes,
            file_name=f"Proposta_Comercial_{empresa.replace(' ', '_')}.pdf" if empresa else "Proposta_Comercial.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col_down2:
        pdf_interno_bytes = gerar_pdf_interno(dados_completos)
        st.download_button(
            label="🔒 Baixar Relatório Interno (Custos)",
            data=pdf_interno_bytes,
            file_name=f"Relatorio_Interno_Custos_{empresa.replace(' ', '_')}.pdf" if empresa else "Relatorio_Interno_Custos.pdf",
            mime="application/pdf",
            use_container_width=True
        )

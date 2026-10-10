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
# CANVAS COM LINKS CLICÁVEIS NO RODAPÉ
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
            self.draw_decorations()
            super().showPage()
        super().save()

    def draw_decorations(self):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(40, 30, 555, 30)
        
        footer_text = "Okamoto Mídias Visuais    |    okamotomidiasvisuais.com.br    |    contato@okamotomidiasvisuais.com.br    |    WhatsApp: 16 99133 2121"
        self.drawCentredString(297.5, 18, footer_text)
        
        # Links interativos clicáveis no rodapé
        self.linkURL("https://okamotomidiasvisuais.com.br", (170, 14, 300, 25), relative=0)
        self.linkURL("https://wa.me/5516991332121", (440, 14, 540, 25), relative=0)
        
        self.restoreState()

# ==========================================
# FUNÇÃO 1: GERAR PDF DA PROPOSTA COMERCIAL
# ==========================================
def gerar_pdf_cliente(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=20, bottomMargin=35)
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('Titulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=16, alignment=1, textColor=colors.HexColor('#1e293b'))
    style_servico_sub = ParagraphStyle('ServSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, alignment=1, textColor=colors.HexColor('#334155'))
    style_corpo = ParagraphStyle('Corpo', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10.5, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=colors.HexColor('#1e293b'))
    style_assinatura = ParagraphStyle('Assinatura', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#1e293b'))
    
    story = []
    
    # Atribuição correta do título do documento na barra do visualizador
    doc.title = f"Proposta Comercial - {dados['empresa'] if dados['empresa'] else 'Cliente'}"

    if os.path.exists("logo_okamoto.png"):
        img = RLImage("logo_okamoto.png", width=110, height=41)
        img.hAlign = 'CENTER'
        story.append(img)
    else:
        story.append(Paragraph("<b>[ OKAMOTO MÍDIAS VISUAIS ]</b>", style_titulo))
    
    story.append(Spacer(1, 4))
    
    d_orc = dados['data_orcamento']
    data_extenso = f"Ribeirão Preto, {d_orc.day} de {MESES_PT[d_orc.month]} de {d_orc.year}"
    story.append(Paragraph(data_extenso, style_corpo))
    story.append(Spacer(1, 3))
    
    nome_servico_titulo = dados['tipo_servico'] if dados['tipo_servico'] != "Outro" else dados['outro_servico_nome']
    story.append(Paragraph("<b>Proposta Comercial</b>", style_titulo))
    story.append(Spacer(1, 1))
    story.append(Paragraph(nome_servico_titulo, style_servico_sub))
    story.append(Spacer(1, 5))
    
    story.append(Paragraph("<b>1. Dados do cliente:</b>", style_bold))
    texto_cliente = f"<b>Contato:</b> {dados['contato']} &nbsp;|&nbsp; <b>Empresa:</b> {dados['empresa']} &nbsp;|&nbsp; <b>Tel:</b> {dados['telefone']} &nbsp;|&nbsp; <b>E-mail:</b> {dados['email']}"
    story.append(Paragraph(texto_cliente, style_corpo))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph("<b>2. Data do evento:</b>", style_bold))
    data_ev_str = dados['data_evento'].strftime('%d/%m/%Y')
    if dados['tem_data_termino']:
        data_ev_str += f" até {dados['data_termino'].strftime('%d/%m/%Y')}"
    texto_evento = f"<b>Data:</b> {data_ev_str} &nbsp;&nbsp; <b>Horário:</b> {dados['horario']} &nbsp;&nbsp; <b>Local:</b> {dados['local']} — {dados['cidade']}/{dados['estado']}"
    story.append(Paragraph(texto_evento, style_corpo))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph("<b>3. Serviço:</b>", style_bold))
    story.append(Paragraph(nome_servico_titulo, style_corpo))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph("<b>4. Escopo do serviço:</b>", style_bold))
    story.append(Paragraph(dados['escopo_servico'].replace('\n', '<br/>'), style_corpo))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph("<b>5. Captação:</b>", style_bold))
    story.append(Paragraph(dados['captacao'].replace('\n', '<br/>'), style_corpo))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph("<b>6. Forma de entrega:</b> Link exclusivo para download, disponível por 30 dias.", style_corpo))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph(f"<b>7. Formas de pagamento:</b> {dados['forma_pagamento_tipo']}", style_corpo))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph(f"<b>8. Condições de pagamento:</b> {dados['condicao_pagamento']}", style_corpo))
    story.append(Spacer(1, 3))
    
    story.append(Paragraph("<b>9. Validade do orçamento:</b> 05 dias", style_corpo))
    story.append(Spacer(1, 4))
    
    val_fmt = fmt_brl(dados['valor_final'])
    if dados['desconto_perc'] > 0:
        texto_valor = f"<b>Valor Total do Investimento ({dados['carga_horaria_sel']}):</b> {val_fmt} <i>(Já inclusos {dados['desconto_perc']}% de desconto)</i>"
    else:
        texto_valor = f"<b>Valor Total do Investimento ({dados['carga_horaria_sel']}):</b> {val_fmt}"
        
    story.append(Paragraph(texto_valor, ParagraphStyle('ValDark', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor('#334155'))))
    story.append(Spacer(1, 4))
    
    story.append(Paragraph("Ficamos à disposição para quaisquer esclarecimentos e ajustes, caso necessário.", style_corpo))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Atenciosamente,", style_corpo))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<b>Rubens Okamoto</b>", style_assinatura))
    story.append(Paragraph("Okamoto Mídias Visuais", style_corpo))
    
    # 2ª PÁGINA (INSTITUCIONAL COM TEXTOS AMPLIADOS E UNIFICADOS)
    story.append(PageBreak())
    
    if os.path.exists("logo_okamoto.png"):
        img_inst = RLImage("logo_okamoto.png", width=150, height=56)
        img_inst.hAlign = 'CENTER'
        story.append(img_inst)
    else:
        story.append(Paragraph("<b>[ OKAMOTO MÍDIAS VISUAIS ]</b>", style_titulo))
        
    story.append(Spacer(1, 15))
    
    style_destaque_1 = ParagraphStyle('Dest1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=19, alignment=1, textColor=colors.HexColor('#1e293b'))
    style_destaque_2 = ParagraphStyle('Dest2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=15, alignment=1, textColor=colors.HexColor('#475569'))
    
    story.append(Paragraph("É registrando a sua história, que nós construímos a nossa!", style_destaque_1))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Especialistas em Imagem, Vídeo e Experiências Imersivas", style_destaque_2))
    story.append(Spacer(1, 18))
    
    intro_inst = "Unimos a bagagem de três décadas às inovações tecnológicas mais recentes, transformando sua marca com soluções visuais de alta performance:"
    story.append(Paragraph(intro_inst, style_corpo))
    story.append(Spacer(1, 10))
    
    topicos_inst = "<b>• Fotografia Corporativa e Estratégica:</b><br/>Imagens que reforçam a autoridade da sua empresa e destacam seu negócio no mercado.<br/><br/><b>• Tours Virtuais 360º:</b><br/>Experiências imersivas que levam seu cliente para dentro do seu espaço físico.<br/><br/><b>• Vídeos de Alto Impacto:</b><br/>Produções pensadas para converter e engajar seu público em redes sociais e plataformas digitais."
    story.append(Paragraph(topicos_inst, style_corpo))
    story.append(Spacer(1, 18))
    
    style_cat_titulo = ParagraphStyle('CatTit', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.HexColor('#1e293b'))
    
    story.append(Paragraph("<b>Dados da Empresa</b>", style_cat_titulo))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Okamoto Reportagens Fotográficas SS Ltda<br/><b>CNPJ:</b> 04.824.331/0001-05<br/>Rua General Carneiro, 860 — Centro, Brodowski - SP<br/>CEP: 14.340-023", style_corpo))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Dados Pessoais</b>", style_cat_titulo))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Rubens Heigasi Okamoto</b><br/><b>CPF:</b> 287.932.298-79 &nbsp;|&nbsp; <b>RG:</b> 25.450.624-0 SSP/SP<br/><b>Tel. Cel.:</b> 16 99133 2121 &nbsp;|&nbsp; <b>E-mail:</b> contato@okamotomidiasvisuais.com.br", style_corpo))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Dados Bancários</b>", style_cat_titulo))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Banco do Brasil</b><br/><b>Agência:</b> 3235-2 &nbsp;|&nbsp; <b>C. Corrente:</b> 11.935-0<br/><b>Chave PIX:</b> 04824331000105", style_corpo))

    doc.build(story, canvasmaker=ModernCanvas)
    buffer.seek(0)
    return buffer

# ==========================================
# FUNÇÃO 2: GERAR RELATÓRIO INTERNO (CUSTOS)
# ==========================================
def gerar_pdf_interno(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=60)
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('Titulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, leading=19, alignment=1, textColor=colors.HexColor('#1e293b'))
    style_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#475569'))
    style_corpo = ParagraphStyle('Corpo', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=colors.HexColor('#1e293b'))
    
    story = []
    
    # Atribuição correta do título do relatório interno na barra do visualizador
    doc.title = f"Relatório Interno - {dados['empresa'] if dados['empresa'] else 'Custos'}"

    if os.path.exists("logo_okamoto.png"):
        img_int = RLImage("logo_okamoto.png", width=120, height=45)
        img_int.hAlign = 'CENTER'
        story.append(img_int)
    else:
        story.append(Paragraph("<b>[ LOGO OKAMOTO ]</b>", style_bold))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("Relatório Interno", style_subtitulo))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Análise Técnica de Custos, Logística e Margem", style_titulo))
    story.append(Spacer(1, 12))
    
    servico_exibido = dados['tipo_servico'] if dados['tipo_servico'] != "Outro" else dados['outro_servico_nome']
    
    info_geral = [
        [Paragraph("<b>Cliente / Empresa:</b>", style_bold), Paragraph(f"{dados['empresa']} ({dados['contato']})", style_corpo)],
        [Paragraph("<b>Serviço:</b>", style_bold), Paragraph(servico_exibido, style_corpo)],
        [Paragraph("<b>Carga Horária:</b>", style_bold), Paragraph(dados['carga_horaria_sel'], style_corpo)],
        [Paragraph("<b>Data do Evento:</b>", style_bold), Paragraph(dados['data_evento'].strftime('%d/%m/%Y'), style_corpo)]
    ]
    t_geral = Table(info_geral, colWidths=[110, 405])
    t_geral.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(t_geral)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1. Custos de Logística, Deslocamento & Operacionais", style_subtitulo))
    story.append(Spacer(1, 6))
    
    tabela_log_dados = [
        [Paragraph("<b>Parâmetro</b>", style_bold), Paragraph("<b>Detalhe / Métrica</b>", style_bold), Paragraph("<b>Custo Parcial</b>", style_bold)],
        [Paragraph("Distância Total", style_corpo), Paragraph(f"{dados['distancia']} km (Ida e Volta)", style_corpo), Paragraph("-", style_corpo)],
        [Paragraph("Combustível", style_corpo), Paragraph(f"Consumo: {dados['consumo_veiculo']} km/L | {dados['litros_gastos']:.1f}L a {fmt_brl(dados['preco_combustivel'])}/L", style_corpo), Paragraph(fmt_brl(dados['custo_combustivel']), style_corpo)],
        [Paragraph("Pedágios", style_corpo), Paragraph("Tarifas de estrada", style_corpo), Paragraph(fmt_brl(dados['pedagios']), style_corpo)],
        [Paragraph("Hospedagem", style_corpo), Paragraph("Diárias de hospedagem", style_corpo), Paragraph(fmt_brl(dados['custo_hospedagem_total']), style_corpo)],
        [Paragraph("Alimentação & Outros", style_corpo), Paragraph("Alimentação / Estacionamento", style_corpo), Paragraph(fmt_brl(dados['custo_outros_total']), style_corpo)]
    ]
    t_log = Table(tabela_log_dados, colWidths=[130, 275, 110])
    ts_log = TableStyle()
    ts_log.add('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9'))
    ts_log.add('ALIGN', (0,0), (-1,-1), 'LEFT')
    ts_log.add('ALIGN', (2,0), (2,-1), 'RIGHT')
    ts_log.add('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ts_log.add('BOTTOMPADDING', (0,0), (-1,-1), 5)
    ts_log.add('TOPPADDING', (0,0), (-1,-1), 5)
    ts_log.add('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    t_log.setStyle(ts_log)
    story.append(t_log)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2. Custos Operacionais & Impostos", style_subtitulo))
    story.append(Spacer(1, 6))
    
    tabela_op_dados = [
        [Paragraph("<b>Descrição</b>", style_bold), Paragraph("<b>Base / Alíquota</b>", style_bold), Paragraph("<b>Valor Estimado</b>", style_bold)],
        [Paragraph("Valor Base dos Serviços", style_corpo), Paragraph(f"Tabela ({dados['carga_horaria_sel']})", style_corpo), Paragraph(fmt_brl(dados['valor_base']), style_corpo)],
        [Paragraph("Desconto Aplicado", style_corpo), Paragraph(f"{dados['desconto_perc']}% de desconto comercial", style_corpo), Paragraph(f"- {fmt_brl(dados['valor_desconto'])}", style_corpo)],
        [Paragraph("Impostos (Nota Fiscal)", style_corpo), Paragraph(f"{dados['imposto_perc']}% sobre o faturamento", style_corpo), Paragraph(fmt_brl(dados['valor_impostos']), style_corpo)],
        [Paragraph("Outros Custos / Extras", style_corpo), Paragraph("Insumos gerais", style_corpo), Paragraph(fmt_brl(dados['custo_extra']), style_corpo)]
    ]
    t_op = Table(tabela_op_dados, colWidths=[140, 265, 110])
    ts_op = TableStyle()
    ts_op.add('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9'))
    ts_op.add('ALIGN', (0,0), (-1,-1), 'LEFT')
    ts_op.add('ALIGN', (2,0), (2,-1), 'RIGHT')
    ts_op.add('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ts_op.add('BOTTOMPADDING', (0,0), (-1,-1), 5)
    ts_op.add('TOPPADDING', (0,0), (-1,-1), 5)
    ts_op.add('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    t_op.setStyle(ts_op)
    story.append(t_op)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("3. Fechamento Financeiro & Margem", style_subtitulo))
    story.append(Spacer(1, 6))
    
    tabela_resumo_interno = [
        [Paragraph("<b>Faturamento Total Proposto:</b>", style_bold), Paragraph(f"<b>{fmt_brl(dados['valor_final'])}</b>", style_corpo)],
        [Paragraph("<b>Custo Operacional Total:</b>", style_bold), Paragraph(fmt_brl(dados['custo_total_interno']), style_corpo)],
        [Paragraph("<b>Lucro Líquido Estimado:</b>", style_bold), Paragraph(f"<b>{fmt_brl(dados['lucro_liquido'])} ({dados['margem_lucro']:.1f}%)</b>", style_bold)]
    ]
    t_res_int = Table(tabela_resumo_interno, colWidths=[315, 200])
    ts_res = TableStyle()
    ts_res.add('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e2e8f0'))
    ts_res.add('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ts_res.add('ALIGN', (1,0), (1,-1), 'RIGHT')
    ts_res.add('BOTTOMPADDING', (0,0), (-1,-1), 6)
    ts_res.add('TOPPADDING', (0,0), (-1,-1), 6)
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

if os.path.exists("logo_okamoto.png"):
    col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
    with col_img2:
        st.image("logo_okamoto.png", width=340)

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
    data_str_escopo = f"{data_evento.day} de {mes_extenso_ev} de {data_evento.year}"
    if tem_data_termino:
        mes_extenso_ter = MESES_PT[data_termino.month]
        data_str_escopo = f"de {data_evento.day} de {mes_extenso_ev} até {data_termino.day} de {mes_extenso_ter} de {data_termino.year}"

    default_escopo = f"{nome_servico_atual}\n{data_str_escopo}\n{horario if horario else 'Horário a definir'}\n{local if local else 'Local a definir'}\n{cidade} - {estado}\n01 (um) profissional"
    default_captacao = "Cobertura fotográfica do evento"
    
    escopo_servico = st.text_area("Escopo do serviço", default_escopo, height=90)
    captacao = st.text_area("Captação", default_captacao, height=60)

with tabs_topo[1]:
    st.subheader("🚗 Parâmetros de Deslocamento & Logística (Honda HR-V)")
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        distancia_ida_volta = st.number_input("Distância Total (Ida e Volta em km)", min_value=0.0, value=0.0, step=5.0)
    with col_l2:
        consumo_medio = st.number_input("Consumo Médio (km/L)", min_value=1.0, value=11.50, step=0.5)
    with col_l3:
        preco_combustivel = st.number_input("Preço do Litro (R$)", min_value=0.0, value=6.80, step=0.10)
        
    pedagio_total = st.number_input("Valor Total de Pedágios (R$)", min_value=0.0, value=0.0, step=5.0)

    st.markdown("---")
    st.subheader("🏨 Hospedagem, Alimentação & Outros Custos")
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        qtd_hosp = st.number_input("Qtd. Diárias Hospedagem", min_value=0, value=0, step=1)
        val_hosp = st.number_input("R$ Hospedagem (diária)", min_value=0.0, value=150.0, step=10.0)
    with col_h2:
        custo_alimentacao = st.number_input("Alimentação (Total R$)", min_value=0.0, value=0.0, step=10.0)
    with col_h3:
        custo_outros = st.number_input("Outros (Estacionamento, etc. R$)", min_value=0.0, value=0.0, step=10.0)

    custo_hospedagem_total = qtd_hosp * val_hosp

    st.markdown("---")
    st.subheader("💼 Custos Operacionais & Impostos (Uso Interno)")
    col_op1, col_op2 = st.columns(2)
    with col_op1:
        imposto_perc = st.number_input("Alíquota de Impostos / Notas (%)", min_value=0.0, max_value=30.0, value=6.0, step=0.5)
    with col_op2:
        custo_extra = st.number_input("Outros Custos / Extras (R$)", min_value=0.0, value=0.0, step=10.0)

with tabs_topo[2]:
    st.subheader("Condições Comerciais & Pagamento")
    forma_entrega = st.text_input("Forma de entrega", "Link exclusivo para download

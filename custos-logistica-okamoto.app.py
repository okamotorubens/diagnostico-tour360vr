import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.pdfgen import canvas
import io
import os
from datetime import datetime, timedelta

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

class ModernCanvas(canvas.Canvas):
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
            self.draw_decorations()
            super().showPage()
        super().save()

    def draw_decorations(self):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#475569"))
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(40, 45, 555, 45)
        footer_text = "Okamoto Mídias Visuais    |    okamotomidiasvisuais.com.br    |    contato@okamotomidiasvisuais.com.br    |    WhatsApp: 16 99133 2121"
        self.drawCentredString(297.5, 30, footer_text)
        self.restoreState()

# ==========================================
# FUNÇÃO 1: GERAR PDF DA PROPOSTA COMERCIAL (CLIENTE + 2ª PÁGINA)
# ==========================================
def gerar_pdf_cliente(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=60)
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('Titulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#1e293b'))
    style_corpo = ParagraphStyle('Corpo', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=15, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=15, textColor=colors.HexColor('#1e293b'))
    style_assinatura = ParagraphStyle('Assinatura', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=16, textColor=colors.HexColor('#1e293b'))
    
    story = []
    
    # 1ª PÁGINA: PROPOSTA COMERCIAL
    if os.path.exists("logo_okamoto.png"):
        story.append(RLImage("logo_okamoto.png", width=180, height=67)) # Logo ampliada
    else:
        story.append(Paragraph("<b>[ OKAMOTO MÍDIAS VISUAIS ]</b>", ParagraphStyle('LogoTxt', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, textColor=colors.HexColor('#1e293b'))))
    
    story.append(Spacer(1, 15))
    
    d_orc = dados['data_orcamento']
    data_extenso = f"Ribeirão Preto, {d_orc.day} de {MESES_PT[d_orc.month]} de {d_orc.year}"
    story.append(Paragraph(data_extenso, style_corpo))
    story.append(Spacer(1, 15))
    
    nome_servico_titulo = dados['tipo_servico'] if dados['tipo_servico'] != "Outro" else dados['outro_servico_nome']
    story.append(Paragraph(f"<b>Proposta Comercial - {nome_servico_titulo}</b>", style_titulo))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>1. Dados do cliente:</b>", style_bold))
    texto_cliente = f"""
    <b>Contato:</b> {dados['contato']}<br/>
    <b>Empresa:</b> {dados['empresa']}<br/>
    <b>Telefone:</b> {dados['telefone']}<br/>
    <b>E-mail:</b> {dados['email']}
    """
    story.append(Paragraph(texto_cliente, style_corpo))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>2. Data do evento:</b>", style_bold))
    data_ev_str = dados['data_evento'].strftime('%d/%m/%Y')
    if dados['tem_data_termino']:
        data_ev_str += f" até {dados['data_termino'].strftime('%d/%m/%Y')}"
        
    texto_evento = f"""
    <b>Data:</b> {data_ev_str} &nbsp;&nbsp;&nbsp;&nbsp; <b>Horário:</b> {dados['horario']}<br/>
    <b>Local:</b> {dados['local']}<br/>
    <b>Cidade / UF:</b> {dados['cidade']} - {dados['estado']}
    """
    story.append(Paragraph(texto_evento, style_corpo))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>3. Serviço:</b>", style_bold))
    story.append(Paragraph(nome_servico_titulo, style_corpo))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>4. Escopo do serviço:</b>", style_bold))
    story.append(Paragraph(dados['escopo_servico'].replace('\n', '<br/>'), style_corpo))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>5. Captação:</b>", style_bold))
    story.append(Paragraph(dados['captacao'].replace('\n', '<br/>'), style_corpo))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>6. Forma de entrega:</b> Link exclusivo para download, disponível por 30 dias.", style_corpo))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"<b>7. Formas de pagamento:</b> {dados['forma_pagamento_tipo']}", style_corpo))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"<b>8. Condições de pagamento:</b> {dados['condicao_pagamento']}", style_corpo))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>9. Validade do orçamento:</b> 05 dias", style_corpo))
    story.append(Spacer(1, 10))
    
    val_fmt = fmt_brl(dados['valor_final'])
    if dados['desconto_perc'] > 0:
        texto_valor = f"<b>Valor Total do Investimento ({dados['carga_horaria_sel']}):</b> {val_fmt} <i>(Já inclusos {dados['desconto_perc']}% de desconto)</i>"
    else:
        texto_valor = f"<b>Valor Total do Investimento ({dados['carga_horaria_sel']}):</b> {val_fmt}"
        
    story.append(Paragraph(texto_valor, ParagraphStyle('ValDark', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#334155'))))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Ficamos à disposição para quaisquer esclarecimentos e ajustes, caso necessário.", style_corpo))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Atenciosamente,", style_corpo))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Rubens Okamoto</b>", style_assinatura))
    story.append(Paragraph("Okamoto Mídias Visuais", style_corpo))
    
    # 2ª PÁGINA: DADOS INSTITUCIONAIS E BANCÁRIOS (Conforme anexo)
    story.append(PageBreak())
    
    if os.path.exists("logo_okamoto.png"):
        story.append(RLImage("logo_okamoto.png", width=180, height=67))
    else:
        story.append(Paragraph("<b>[ OKAMOTO MÍDIAS VISUAIS ]</b>", style_bold))
        
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Dados da Empresa</b>[cite: 2]", style_titulo))
    story.append(Spacer(1, 8))
    
    dados_empresa_txt = """
    <b>Okamoto Reportagens Fotográficas SS Ltda</b>[cite: 2]<br/>
    <b>CNPJ:</b> 04.824.331/0001-05[cite: 2]<br/>
    Rua General Carneiro, 860[cite: 2]<br/>
    Centro — Brodowski - SP[cite: 2]<br/>
    CEP: 14.340-023[cite: 2]
    """
    story.append(Paragraph(dados_empresa_txt, style_corpo))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>Dados Pessoais</b>[cite: 2]", style_titulo))
    story.append(Spacer(1, 8))
    dados_pessoais_txt = """
    <b>Rubens Heigasi Okamoto</b>[cite: 2]<br/>
    <b>CPF:</b> 287.932.298-79[cite: 2]<br/>
    <b>RG:</b> 25.450.624-0 — SSP/SP[cite: 2]<br/>
    <b>Tel. Cel.:</b> 16 99133 2121[cite: 2]<br/>
    <b>E-mail:</b> contato@okamotomidiasvisuais.com.br[cite: 2]
    """
    story.append(Paragraph(dados_pessoais_txt, style_corpo))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>Dados Bancários</b>[cite: 2]", style_titulo))
    story.append(Spacer(1, 8))
    dados_banco_txt = """
    <b>Banco do Brasil</b>[cite: 2]<br/>
    <b>Agência:</b> 3235-2[cite: 2]<br/>
    <b>C. Corrente:</b> 11.935-0[cite: 2]<br/>
    <b>Chave PIX:</b> 04824331000105[cite: 2]
    """
    story.append(Paragraph(dados_banco_txt, style_corpo))

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
    style_titulo = ParagraphStyle('Titulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor('#1e293b'))
    style_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#475569'))
    style_corpo = ParagraphStyle('Corpo', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#1e293b'))
    
    story = []
    
    if os.path.exists("logo_okamoto.png"):
        story.append(RLImage("logo_okamoto.png", width=180, height=67))
    else:
        story.append(Paragraph("<b>[ LOGO OKAMOTO ]</b>", style_bold))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("Relatório Interno", style_subtitulo))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Análise Técnica de Custos, Logística e Margem", style_titulo))
    story.append(Spacer(1, 15))
    
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
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("1. Custos de Logística, Deslocamento & Operacionais", style_subtitulo))
    story.append(Spacer(1, 8))
    
    tabela_log_dados = [
        [Paragraph("<b>Parâmetro</b>", style_bold), Paragraph("<b>Detalhe / Métrica</b>", style_bold), Paragraph("<b>Custo Parcial</b>", style_bold)],
        [Paragraph("Distância Total", style_corpo), Paragraph(f"{dados['distancia']} km (Ida e Volta)", style_corpo), Paragraph("-", style_corpo)],
        [Paragraph("Combustível", style_corpo), Paragraph(f"Consumo: {dados['consumo_veiculo']} km/L | {dados['litros_gastos']:.1f}L a {fmt_brl(dados['preco_combustivel'])}/L", style_corpo), Paragraph(fmt_brl(dados['custo_combustivel']), style_corpo)],
        [Paragraph("Pedágios", style_corpo), Paragraph("Tarifas de estrada", style_corpo), Paragraph(fmt_brl(dados['pedagios']), style_corpo)],
        [Paragraph("Alimentação", style_corpo), Paragraph("Almoço / Janta calculados", style_corpo), Paragraph(fmt_brl(dados['custo_alimentacao_total']), style_corpo)],
        [Paragraph("Outros Custos", style_corpo), Paragraph("Estacionamento / Freelancer / Outros", style_corpo), Paragraph(fmt_brl(dados['custo_outros_total']), style_corpo)]
    ]
    t_log = Table(tabela_log_dados, colWidths=[130, 275, 110])
    t_log.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    ]))
    story.append(t_log)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("2. Custos Operacionais & Impostos", style_subtitulo))
    story.append(Spacer(1, 8))
    
    tabela_op_dados = [
        [Paragraph("<b>Descrição</b>", style_bold), Paragraph("<b>Base / Alíquota</b>", style_bold), Paragraph("<b>Valor Estimado</b>", style_bold)],
        [Paragraph("Valor Base dos Serviços", style_corpo), Paragraph(f"Tabela ({dados['carga_horaria_sel']})", style_corpo), Paragraph(fmt_brl(dados['valor_base']), style_corpo)],
        [Paragraph("Desconto Aplicado", style_corpo), Paragraph(f"{dados['desconto_perc']}% de desconto comercial", style_corpo), Paragraph(f"- {fmt_brl(dados['valor_desconto'])}", style_corpo)],
        [Paragraph("Impostos (Nota Fiscal)", style_corpo), Paragraph(f"{dados['imposto_perc']}% sobre o faturamento", style_corpo), Paragraph(fmt_brl(dados['valor_impostos']), style_corpo)],
        [Paragraph("Outros Custos / Extras", style_corpo), Paragraph("Insumos gerais", style_corpo), Paragraph(fmt_brl(dados['custo_extra']), style_corpo)]
    ]
    t_op = Table(tabela_op_dados, colWidths=[140, 265, 110])
    t_op.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    ]))
    story.append(t_op)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("3. Fechamento Financeiro & Margem", style_subtitulo))
    story.append(Spacer(1, 8))
    
    tabela_resumo_interno = [
        [Paragraph("<b>Faturamento Total Proposto:</b>", style_bold), Paragraph(f"<b>{fmt_brl(dados['valor_final'])}</b>", style_corpo)],
        [Paragraph("<b>Custo Operacional Total:</b>", style_bold), Paragraph(fmt_brl(dados['custo_total_interno']), style_corpo)],
        [Paragraph("<b>Lucro Líquido Estimado:</b>", style_bold), Paragraph(f"<b>{fmt_brl(dados['lucro_liquido'])} ({dados['margem_lucro']:.1f}%)</b>", style_bold)]
    ]
    t_res_int = Table(tabela_resumo_interno, colWidths=[315, 200])
    t_res_int.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e2e8f0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#475569'))
    ]))
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
    st.image("logo_okamoto.png", width=220) # Logo ampliada no painel

# Criação de abas duplicadas (em cima e embaixo) para facilitar a navegação sem subir a tela
tabs_topo = st.tabs(["1. Dados & Serviços", "2. Custos & Logística", "3. Prazos, Resumo & Relatórios"])

with tabs_topo[0]:
    st.subheader("1. Dados do Cliente & Evento")
    col1, col2 = st.columns(2)
    with col1:
        contato = st.text_input("Contato", "Natalia")
        empresa = st.text_input("Empresa", "Ambient Serviços Ambientais S/A")
        telefone = st.text_input("Telefone", "(16) 99999-9999")
        email = st.text_input("E-mail", "natalia@ambient.com.br")
    with col2:
        data_orcamento = st.date_input("Data do Orçamento", datetime.now())
        data_evento = st.date_input("Data do Evento", datetime.now())
        
        tem_data_termino = st.checkbox("Evento com mais de um dia (Data de Término)")
        data_termino = data_evento
        if tem_data_termino:
            data_termino = st.date_input("Data de Término do Evento", datetime.now())
            
        horario = st.text_input("Horário", "18h00 às 22h30")
        local = st.text_input("Local", "Rua Clemente Ferreira, 330")
        
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
        outro_servico_nome = st.text_input("Especifique o nome do serviço", "Serviço Personalizado")

    carga_horaria_sel = st.selectbox("Carga Horária", OPCOES_CARGA_HORARIA)
    
    opcoes_desconto_base = [0, 5, 10, 15, 20, 25, 30]
    tipo_desc = st.radio("Selecione a modalidade de desconto", ["Padrão", "Personalizado (Outro valor)"], horizontal=True)
    if tipo_desc == "Padrão":
        desconto_perc = st.selectbox("Aplicar Desconto (%)", opcoes_desconto_base)
    else:
        desconto_perc = st.number_input("Digite a porcentagem de desconto (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)

    st.markdown("---")
    st.subheader("3. Detalhamento Técnico (Escopo & Captação)")
    
    nome_servico_atual = tipo_servico if tipo_servico != "Outro" else outro_servico_nome
    mes_extenso_ev = MESES_PT[data_evento.month]
    data_str_escopo = f"em {data_evento.day} de {mes_extenso_ev} de {data_evento.year}"
    if tem_data_termino:
        mes_extenso_ter = MESES_PT[data_termino.month]
        data_str_escopo = f"de {data_evento.day} de {mes_extenso_ev} até {data_termino.day} de {mes_extenso_ter} de {data_termino.year}"

    default_escopo = f"{nome_servico_atual}, {data_str_escopo}, das {horario}, {local} em {cidade} - {estado} e 01 (um) profissional."
    default_captacao = "Cobertura fotográfica do evento"
    
    escopo_servico = st.text_area("Escopo do serviço", default_escopo)
    captacao = st.text_area("Captação", default_captacao)

with tabs_topo[1]:
    st.subheader("🚗 Parâmetros de Deslocamento & Logística (Honda HR-V)")
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        distancia_ida_volta = st.number_input("Distância Total (Ida e Volta em km)", min_value=0.0, value=40.0, step=5.0)
    with col_l2:
        consumo_medio = st.number_input("Consumo Médio (km/L)", min_value=1.0, value=11.50, step=0.5)
    with col_l3:
        preco_combustivel = st.number_input("Preço do Litro (R$)", min_value=0.0, value=6.80, step=0.10)
        
    pedagio_total = st.number_input("Valor Total de Pedágios (R$)", min_value=0.0, value=0.0, step=5.0)

    st.markdown("---")
    st.subheader("🍽️ Custos de Alimentação & Outros")
    col_al1, col_al2, col_al3 = st.columns(3)
    with col_al1:
        qtd_almoco = st.number_input("Qtd. Almoços", min_value=0, value=1, step=1)
        valor_almoco_unit = st.number_input("Valor Unitário Almoço (R$)", min_value=0.0, value=35.0, step=5.0)
    with col_al2:
        qtd_janta = st.number_input("Qtd. Jantas", min_value=0, value=1, step=1)
        valor_janta_unit = st.number_input("Valor Unitário Janta (R$)", min_value=0.0, value=45.0, step=5.0)
    with col_al3:
        custo_outros = st.number_input("Outros (Estacionamento, Freelancer, etc.) (R$)", min_value=0.0, value=0.0, step=10.0)

    custo_alimentacao_total = (qtd_almoco * valor_almoco_unit) + (qtd_janta * valor_janta_unit)

    st.markdown("---")
    st.subheader("💼 Custos Operacionais & Impostos (Uso Interno)")
    col_op1, col_op2 = st.columns(2)
    with col_op1:
        imposto_perc = st.number_input("Alíquota de Impostos / Notas (%)", min_value=0.0, max_value=30.0, value=6.0, step=0.5)
    with col_op2:
        custo_extra = st.number_input("Outros Custos / Extras (R$)", min_value=0.0, value=0.0, step=10.0)

with tabs_topo[2]:
    st.subheader("Condições Comerciais & Pagamento")
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

    # ==========================================
    # CÁLCULOS MATEMÁTICOS DE VALORES E CUSTOS
    # ==========================================
    tabela_atual = TABELAS_SERVICOS.get(tipo_servico, TABELAS_SERVICOS["Evento social"])
    if "diária" in carga_horaria_sel:
        qtd_diarias = int(carga_horaria_sel.split()[0])
        valor_base = tabela_atual.get(10, 1300.0) * qtd_diarias
    else:
        horas_num = int(carga_horaria_sel.replace("h", ""))
        horas_buscadas = min(horas_num, 12)
        valor_base = tabela_atual.get(horas_buscadas, 1500.0)
        if horas_num > 12:
            valor_base += (horas_num - 12) * tabela_atual.get(1, 180.0)

    valor_desconto = valor_base * (desconto_perc / 100.0)
    valor_final = valor_base - valor_desconto

    litros_gastos = distancia_ida_volta / consumo_medio if consumo_medio > 0 else 0
    custo_combustivel = litros_gastos * preco_combustivel
    custo_logistica_total = custo_combustivel + pedagio_total

    custo_total_operacional_log = custo_logistica_total + custo_alimentacao_total + custo_outros
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
        "custo_alimentacao_total": custo_alimentacao_total,
        "custo_outros_total": custo_outros,
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
            file_name=f"Proposta_Comercial_{empresa.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col_down2:
        pdf_interno_bytes = gerar_pdf_interno(dados_completos)
        st.download_button(
            label="🔒 Baixar Relatório Interno (Custos)",
            data=pdf_interno_bytes,
            file_name=f"Relatorio_Interno_Custos_{empresa.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# Abas duplicadas na parte inferior da tela para facilitar a navegação
st.markdown("---")
st.markdown("### 📌 Navegação Rápida (Inferior)")
tabs_baixo = st.tabs(["1. Dados & Serviços (Inf)", "2. Custos & Logística (Inf)", "3. Prazos, Resumo & Relatórios (Inf)"])
with tabs_baixo[0]:
    st.info("💡 Dica: Você pode preencher os dados acima na aba superior ou alternar para cá a qualquer momento.")
with tabs_baixo[1]:
    st.info("💡 Dica: Os custos de combustível, alimentação e taxas são consolidados automaticamente no relatório interno.")
with tabs_baixo[2]:
    st.info("💡 Dica: O painel financeiro e os botões de download dos PDFs encontram-se na aba principal acima.")

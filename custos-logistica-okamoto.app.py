import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
import io
from datetime import datetime

# ==========================================
# TABELAS DE PREÇO POR TIPO DE EVENTO
# ==========================================
TABELAS_SERVICOS = {
    "Evento social": {1: 180.0, 2: 350.0, 3: 450.0, 4: 600.0, 5: 750.0, 6: 900.0, 7: 1000.0, 8: 1100.0, 9: 1200.0, 10: 1300.0, 11: 1400.0, 12: 1500.0},
    "Evento Corporativo": {1: 180.0, 2: 350.0, 3: 450.0, 4: 600.0, 5: 750.0, 6: 900.0, 7: 1000.0, 8: 1100.0, 9: 1200.0, 10: 1300.0, 11: 1400.0, 12: 1500.0},
    "Aniversário infantil": {1: 200.0, 2: 400.0, 3: 600.0, 4: 800.0, 5: 900.0},
    "Aniversário": {1: 180.0, 2: 350.0, 3: 450.0, 4: 600.0, 5: 750.0, 6: 900.0, 7: 1000.0, 8: 1100.0, 9: 1200.0, 10: 1300.0, 11: 1400.0, 12: 1500.0},
    "Retrato Corporativo": {1: 250.0, 2: 500.0, 3: 700.0, 4: 850.0, 5: 1000.0},
    "Institucional": {1: 180.0, 2: 350.0, 3: 450.0, 4: 600.0, 5: 750.0, 6: 900.0, 7: 1000.0, 8: 1100.0, 9: 1200.0, 10: 1300.0, 11: 1400.0, 12: 1500.0},
    "Ações de Marketing": {1: 180.0, 2: 350.0, 3: 450.0, 4: 600.0, 5: 750.0, 6: 900.0, 7: 1000.0, 8: 1100.0, 9: 1200.0, 10: 1300.0, 11: 1400.0, 12: 1500.0}
}

OPCOES_CARGA_HORARIA = [
    "1h", "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "10h", "11h", "12h",
    "1 diária", "2 diárias", "3 diárias", "4 diárias", "5 diárias"
]

st.set_page_config(page_title="Proposta Comercial & Custos - Okamoto Mídias Visuais", page_icon="📊", layout="wide")

# ==========================================
# CANVAS PARA RODAPÉ E CABEÇALHO DO CLIENTE
# ==========================================
class ClienteCanvas(canvas.Canvas):
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
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Linha separadora do rodapé
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(40, 45, 555, 45)
        
        # Rodapé centralizado com links clicables em azul
        footer_text = "Okamoto Mídias Visuais    |    okamotomidiasvisuais.com.br    |    WhatsApp: 16 99133 2121"
        self.drawCentredString(297.5, 30, footer_text)
        self.restoreState()

# ==========================================
# FUNÇÃO 1: GERAR PDF DA PROPOSTA COMERCIAL (CLIENTE)
# ==========================================
def gerar_pdf_cliente(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=60)
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('Titulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.HexColor('#0f172a'))
    style_corpo = ParagraphStyle('Corpo', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=15, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=15, textColor=colors.HexColor('#0f172a'))
    style_assinatura = ParagraphStyle('Assinatura', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=16, textColor=colors.HexColor('#0f172a'))
    
    story = []
    
    # 1. Logotipo no canto esquerdo superior em destaque (Placeholder estilizado em texto/caixa caso arquivo físico não esteja no path)
    story.append(Paragraph("<b>[ LOGO OKAMOTO MÍDIAS VISUAIS ]</b>", ParagraphStyle('Logo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor('#2563eb'))))
    story.append(Spacer(1, 15))
    
    # Data em Ribeirão Preto
    data_extenso = f"Ribeirão Preto, {dados['data_orcamento'].strftime('%d de %B de %Y')}" # Ajustar formato pt se necessário
    story.append(Paragraph(data_extenso, style_corpo))
    story.append(Spacer(1, 20))
    
    # Título Grande em Destaque
    story.append(Paragraph("<b>Proposta Comercial</b>", style_titulo))
    story.append(Spacer(1, 20))
    
    # 1. Dados do cliente
    story.append(Paragraph("<b>1. Dados do cliente:</b>", style_bold))
    texto_cliente = f"""
    <b>Contato:</b> {dados['contato']}<br/>
    <b>Empresa:</b> {dados['empresa']}<br/>
    <b>Telefone:</b> {dados['telefone']}<br/>
    <b>E-mail:</b> {dados['email']}
    """
    story.append(Paragraph(texto_cliente, style_corpo))
    story.append(Spacer(1, 15))
    
    # 2. Data do evento
    story.append(Paragraph("<b>2. Data do evento:</b>", style_bold))
    texto_evento = f"""
    <b>Data:</b> {dados['data_evento'].strftime('%d/%m/%Y')} &nbsp;&nbsp;&nbsp;&nbsp; <b>Horário:</b> {dados['horario']}<br/>
    <b>Local:</b> {dados['local']}<br/>
    <b>Cidade:</b> {dados['cidade']}
    """
    story.append(Paragraph(texto_evento, style_corpo))
    story.append(Spacer(1, 15))
    
    # 3. Serviço
    story.append(Paragraph(f"<b>3. Serviço:</b> {dados['tipo_servico']}", style_bold))
    story.append(Spacer(1, 15))
    
    # 4. Escopo do serviço
    story.append(Paragraph("<b>4. Escopo do serviço:</b>", style_bold))
    story.append(Paragraph(dados['escopo_servico'].replace('\n', '<br/>'), style_corpo))
    story.append(Spacer(1, 15))
    
    # 5. Captação
    story.append(Paragraph("<b>5. Captação:</b>", style_bold))
    story.append(Paragraph(dados['captacao'].replace('\n', '<br/>'), style_corpo))
    story.append(Spacer(1, 15))
    
    # 6. Forma de entrega
    story.append(Paragraph(f"<b>6. Forma de entrega:</b> {dados['forma_entrega']}", style_corpo))
    story.append(Spacer(1, 15))
    
    # 7. Formas de pagamento
    story.append(Paragraph(f"<b>7. Formas de pagamento:</b> {dados['forma_pagamento_tipo']}", style_corpo))
    story.append(Spacer(1, 15))
    
    # 8. Condições de pagamento
    story.append(Paragraph(f"<b>8. Condições de pagamento:</b> {dados['condicao_pagamento']}", style_corpo))
    story.append(Spacer(1, 15))
    
    # 9. Validade do orçamento & Valor Total com Desconto
    story.append(Paragraph("<b>9. Validade do orçamento:</b> 05 dias", style_corpo))
    story.append(Spacer(1, 10))
    
    # Destaque do Valor Investido
    if dados['desconto_perc'] > 0:
        texto_valor = f"<b>Valor Total do Investimento ({dados['carga_horaria_sel']}):</b> R$ {dados['valor_final']:.2f} <i>(Já inclusos {dados['desconto_perc']}% de desconto)</i>"
    else:
        texto_valor = f"<b>Valor Total do Investimento ({dados['carga_horaria_sel']}):</b> R$ {dados['valor_final']:.2f}"
    story.append(Paragraph(texto_valor, ParagraphStyle('Val', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#2563eb'))))
    story.append(Spacer(1, 20))
    
    # Mensagem de encerramento
    story.append(Paragraph("Ficamos à disposição para quaisquer esclarecimentos e ajustes, caso necessário.", style_corpo))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Atenciosamente,", style_corpo))
    story.append(Spacer(1, 15))
    
    # Assinatura Rubens Okamoto (em negrito e 1 ponto a mais)
    story.append(Paragraph("<b>Rubens Okamoto</b>", style_assinatura))
    story.append(Paragraph("Okamoto Mídias Visuais", style_corpo))
    
    doc.build(story, canvasmaker=ClienteCanvas)
    buffer.seek(0)
    return buffer

# ==========================================
# FUNÇÃO 2: GERAR RELATÓRIO INTERNO (CUSTOS)
# ==========================================
def gerar_pdf_interno(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=60)
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('Titulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#991b1b'))
    style_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.HexColor('#7f1d1d'))
    style_corpo = ParagraphStyle('Corpo', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#0f172a'))
    
    story = []
    
    story.append(Paragraph("OKAMOTO MÍDIAS VISUAIS — RELATÓRIO INTERNO", style_subtitulo))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Análise Técnica de Custos, Logística e Margem", style_titulo))
    story.append(Spacer(1, 15))
    
    info_geral = [
        [Paragraph("<b>Cliente / Empresa:</b>", style_bold), Paragraph(f"{dados['empresa']} ({dados['contato']})", style_corpo)],
        [Paragraph("<b>Serviço / Carga:</b>", style_bold), Paragraph(f"{dados['tipo_servico']} - {dados['carga_horaria_sel']}", style_corpo)],
        [Paragraph("<b>Data do Evento:</b>", style_bold), Paragraph(dados['data_evento'].strftime('%d/%m/%Y'), style_corpo)]
    ]
    t_geral = Table(info_geral, colWidths=[120, 395])
    t_geral.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(t_geral)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("1. Custos de Logística e Deslocamento (Honda HR-V)", style_subtitulo))
    story.append(Spacer(1, 8))
    
    tabela_log_dados = [
        [Paragraph("<b>Parâmetro</b>", style_bold), Paragraph("<b>Detalhe / Métrica</b>", style_bold), Paragraph("<b>Custo Parcial</b>", style_bold)],
        [Paragraph("Distância Total", style_corpo), Paragraph(f"{dados['distancia']} km (Ida e Volta)", style_corpo), Paragraph("-", style_corpo)],
        [Paragraph("Combustível", style_corpo), Paragraph(f"Consumo: {dados['consumo_veiculo']} km/L | {dados['litros_gastos']:.1f}L a R$ {dados['preco_combustivel']:.2f}/L", style_corpo), Paragraph(f"R$ {dados['custo_combustivel']:.2f}", style_corpo)],
        [Paragraph("Pedágios", style_corpo), Paragraph("Tarifas de estrada", style_corpo), Paragraph(f"R$ {dados['pedagios']:.2f}", style_corpo)]
    ]
    t_log = Table(tabela_log_dados, colWidths=[130, 275, 110])
    t_log.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fee2e2')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#fca5a5'))
    ]))
    story.append(t_log)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("2. Custos Operacionais & Impostos", style_subtitulo))
    story.append(Spacer(1, 8))
    
    tabela_op_dados = [
        [Paragraph("<b>Descrição</b>", style_bold), Paragraph("<b>Base / Alíquota</b>", style_bold), Paragraph("<b>Valor Estimado</b>", style_bold)],
        [Paragraph("Valor Base dos Serviços", style_corpo), Paragraph(f"Tabela ({dados['carga_horaria_sel']})", style_corpo), Paragraph(f"R$ {dados['valor_base']:.2f}", style_corpo)],
        [Paragraph("Desconto Aplicado", style_corpo), Paragraph(f"{dados['desconto_perc']}% de desconto comercial", style_corpo), Paragraph(f"- R$ {dados['valor_desconto']:.2f}", style_corpo)],
        [Paragraph("Impostos (Nota Fiscal)", style_corpo), Paragraph(f"{dados['imposto_perc']}% sobre o faturamento", style_corpo), Paragraph(f"R$ {dados['valor_impostos']:.2f}", style_corpo)],
        [Paragraph("Outros Custos / Extras", style_corpo), Paragraph("Manutenção preventiva / Insumos", style_corpo), Paragraph(f"R$ {dados['custo_extra']:.2f}", style_corpo)]
    ]
    t_op = Table(tabela_op_dados, colWidths=[140, 265, 110])
    t_op.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fee2e2')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#fca5a5'))
    ]))
    story.append(t_op)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("3. Fechamento Financeiro & Margem", style_subtitulo))
    story.append(Spacer(1, 8))
    
    tabela_resumo_interno = [
        [Paragraph("<b>Faturamento Total Proposto:</b>", style_bold), Paragraph(f"<b>R$ {dados['valor_final']:.2f}</b>", style_corpo)],
        [Paragraph("<b>Custo Operacional Total (Logística + Impostos + Extras):</b>", style_bold), Paragraph(f"R$ {dados['custo_total_interno']:.2f}", style_corpo)],
        [Paragraph("<b>Lucro Líquido Estimado:</b>", style_bold), Paragraph(f"<b>R$ {dados['lucro_liquido']:.2f} ({dados['margem_lucro']:.1f}%)</b>", style_bold)]
    ]
    t_res_int = Table(tabela_resumo_interno, colWidths=[315, 200])
    t_res_int.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fef2f2')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#dc2626'))
    ]))
    story.append(t_res_int)
    
    doc.build(story, canvasmaker=ClienteCanvas)
    buffer.seek(0)
    return buffer

# ==========================================
# INTERFACE DO USUÁRIO - STREAMLIT
# ==========================================
st.title("⚡ Sistema Integrado: Proposta Comercial & Custos")
st.markdown("Preencha os campos abaixo de acordo com o novo formato. O sistema calcula automaticamente os valores com base nas tabelas oficiais de cada serviço e gera os dois PDFs simultaneamente.")

tab1, tab2, tab3 = st.tabs(["1. Dados & Serviços", "2. Custos & Logística", "3. Prazos & Relatórios"])

with tab1:
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
        horario = st.text_input("Horário", "08h00 às 18h00")
        local = st.text_input("Local", "Rod. Alexandre Balbo km 334,6")
        cidade = st.text_input("Cidade", "Ribeirão Preto")

    st.markdown("---")
    st.subheader("2. Seleção de Serviço & Carga Horária")
    tipo_servico = st.selectbox("Tipo de Serviço", list(TABELAS_SERVICOS.keys()))
    carga_horaria_sel = st.selectbox("Carga Horária", OPCOES_CARGA_HORARIA)
    
    desconto_perc = st.selectbox("Aplicar Desconto (%)", [0, 5, 10, 15, 20, 25, 30])

    st.markdown("---")
    st.subheader("3. Detalhamento Técnico (Escopo & Captação)")
    escopo_servico = st.text_area("Escopo do serviço", "Cobertura fotográfica completa do evento corporativo com entrega em alta resolução.")
    captacao = st.text_area("Captação", "Fotografia profissional com câmeras Canon EOS R e lentes de alta performance.")

with tab2:
    st.subheader("🚗 Parâmetros de Deslocamento & Logística (Honda HR-V)")
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        distancia_ida_volta = st.number_input("Distância Total (Ida e Volta em km)", min_value=0.0, value=40.0, step=5.0)
    with col_l2:
        consumo_medio = st.number_input("Consumo Médio (km/L)", min_value=1.0, value=11.0, step=0.5)
    with col_l3:
        preco_combustivel = st.number_input("Preço do Litro (R$)", min_value=0.0, value=5.89, step=0.10)
        
    pedagio_total = st.number_input("Valor Total de Pedágios (R$)", min_value=0.0, value=0.0, step=5.0)

    st.markdown("---")
    st.subheader("💼 Custos Operacionais & Impostos (Uso Interno)")
    col_op1, col_op2 = st.columns(2)
    with col_op1:
        imposto_perc = st.number_input("Alíquota de Impostos / Notas (%)", min_value=0.0, max_value=30.0, value=6.0, step=0.5)
    with col_op2:
        custo_extra = st.number_input("Outros Custos / Extras (R$)", min_value=0.0, value=0.0, step=10.0)

with tab3:
    st.subheader("Condições Comerciais & Pagamento")
    forma_entrega = st.text_input("Forma de entrega", "Em até 72h após o evento (Link exclusivo para download).")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        forma_pagamento_tipo = st.selectbox("Forma de Pagamento", ["À vista", "Parcelado"])
    with col_p2:
        condicao_pagamento = st.selectbox("Condições de Pagamento", ["PIX", "Transferência", "Cartão de crédito", "Cartão de Crédito parcelado"])
    
    parcelas_cartao = 1
    if "parcelado" in condicao_pagamento.lower() or forma_pagamento_tipo == "Parcelado":
        parcelas_cartao = st.number_input("Cartão de Crédito parcelado em X vezes", min_value=1, max_value=12, value=3)
        condicao_pagamento = f"{condicao_pagamento} em {parcelas_cartao}X"

# ==========================================
# CÁLCULOS MATEMÁTICOS DE VALORES E CUSTOS
# ==========================================
# Determinar valor base conforme tabela oficial
tabela_atual = TABELAS_SERVICOS[tipo_servico]
if "diária" in carga_horaria_sel:
    qtd_diarias = int(carga_horaria_sel.split()[0])
    # Diária equivale a 10h na tabela ou base proporcional
    valor_base = tabela_atual.get(10, 1300.0) * qtd_diarias
else:
    horas_num = int(carga_horaria_sel.replace("h", ""))
    # Se passar de 12h, usa o valor de 12h + proporcional ou o teto de 12h
    horas_buscadas = min(horas_num, 12)
    valor_base = tabela_atual.get(horas_buscadas, 1500.0)
    if horas_num > 12:
        # Adicional por hora extra acima de 12h (base 1h)
        valor_base += (horas_num - 12) * tabela_atual.get(1, 180.0)

# Cálculo de Desconto
valor_desconto = valor_base * (desconto_perc / 100.0)
valor_final = valor_base - valor_desconto

# Cálculos Internos de Logística e Margem
litros_gastos = distancia_ida_volta / consumo_medio if consumo_medio > 0 else 0
custo_combustivel = litros_gastos * preco_combustivel
custo_logistica_total = custo_combustivel + pedagio_total

valor_impostos = valor_final * (imposto_perc / 100.0)
custo_total_interno = custo_logistica_total + valor_impostos + custo_extra
lucro_liquido = valor_final - custo_total_interno
margem_lucro = (lucro_liquido / valor_final * 100) if valor_final > 0 else 0

st.markdown("---")
st.subheader("📊 Painel Resumo: Cliente vs. Interno")
col_res1, col_res2, col_res3, col_res4 = st.columns(4)
col_res1.metric("Valor para o Cliente", f"R$ {valor_final:.2f}")
col_res2.metric("Custos Operacionais", f"R$ {custo_total_interno:.2f}")
col_res3.metric("Lucro Líquido Est.", f"R$ {lucro_liquido:.2f}")
col_res4.metric("Margem de Lucro", f"{margem_lucro:.1f}%")

# Dicionário consolidado
dados_completos = {
    "contato": contato,
    "empresa": empresa,
    "telefone": telefone,
    "email": email,
    "data_orcamento": data_orcamento,
    "data_evento": data_evento,
    "horario": horario,
    "local": local,
    "cidade": cidade,
    "tipo_servico": tipo_servico,
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

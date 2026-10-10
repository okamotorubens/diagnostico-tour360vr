import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
import io
from datetime import datetime

# ==========================================
# CONFIGURAÇÕES E TABELAS DE PREÇO BASE
# ==========================================
TABELA_HORAS = {
    "1h": 180.0,
    "2h": 350.0,
    "4h": 600.0,
    "10h (Diária)": 1300.0
}

SERVICOS_DISPONIVEIS = {
    "Cobertura fotográfica": {"fator": 1.0, "desc": "Registros fotográficos de alta resolução com edição de cores e contraste."},
    "Fotos institucionais": {"fator": 1.1, "desc": "Fotografia focada em arquitetura, estrutura corporativa e sinalização."},
    "Retrato corporativo": {"fator": 1.2, "desc": "Retratos individuais de diretoria, palestrantes e equipes com iluminação dedicada."},
    "Captação de vídeo": {"fator": 1.3, "desc": "Gravação de vídeo em Full HD/4K (material bruto entregue via link)."},
    "Rede social (Reels/Shorts)": {"fator": 1.25, "desc": "Captação dinâmica em formato vertical focada para mídias sociais."},
    "Foto-lembrança": {"fator": 1.4, "desc": "Impressão instantânea ou disponibilização de QR Code para participantes."}
}

st.set_page_config(page_title="Gerador de Propostas - Okamoto Mídias Visuais", page_icon="📄", layout="wide")

# ==========================================
# CLASSE PARA CABEÇALHO/RODAPÉ DO PDF
# ==========================================
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Linha do rodapé
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(40, 45, 555, 45)
        
        # Texto do Rodapé
        self.drawString(40, 30, "Okamoto Mídias Visuais | (16) 99133-2121 | okamotomidiasvisuais.com.br")
        self.drawRightString(555, 30, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

# ==========================================
# FUNÇÃO PARA GERAR O PDF
# ==========================================
def gerar_pdf(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=60
    )
    
    styles = getSampleStyleSheet()
    style_titulo = ParagraphStyle('Titulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=colors.HexColor('#0f172a'))
    style_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=colors.HexColor('#2563eb'))
    style_corpo = ParagraphStyle('Corpo', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=15, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=15, textColor=colors.HexColor('#0f172a'))
    
    story = []
    
    # ------------------------------------------
    # PÁGINA 1: APRESENTAÇÃO DA EMPRESA (CAPA)
    # ------------------------------------------
    story.append(Paragraph("OKAMOTO MÍDIAS VISUAIS", style_subtitulo))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Apresentação Institucional & Portfolio de Serviços", style_titulo))
    story.append(Spacer(1, 15))
    
    texto_apresentacao = (
        "Com mais de três décadas de atuação no mercado de imagem e fotografia profissional, a Okamoto Mídias Visuais "
        "é especializada na cobertura completa de eventos corporativos, institucionais e científicos, além de produção "
        "de tours virtuais e conteúdos em vídeo de alta definição. Contamos com equipamentos de ponta para assegurar "
        "agilidade, fidelidade de cores e padrão internacional de entrega."
    )
    story.append(Paragraph(texto_apresentacao, style_corpo))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Diferenciais Competitivos", style_subtitulo))
    story.append(Spacer(1, 10))
    
    dados_tabela_capa = [
        [Paragraph("<b>Item</b>", style_bold), Paragraph("<b>Descrição / Vantagem</b>", style_bold)],
        [Paragraph("Experiência", style_corpo), Paragraph("30 anos de atuação sólida no mercado de produção visual e cobertura de grandes eventos.", style_corpo)],
        [Paragraph("Equipamentos", style_corpo), Paragraph("Câmeras Canon EOS R e lentes profissionais de altíssima performance.", style_corpo)],
        [Paragraph("Agilidade", style_corpo), Paragraph("Fluxo otimizado com entrega rápida de material bruto e editado conforme a necessidade.", style_corpo)]
    ]
    t_capa = Table(dados_tabela_capa, colWidths=[110, 405])
    t_capa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    ]))
    story.append(t_capa)
    
    # Quebra para a Página de Orçamento
    story.append(PageBreak())
    
    # ------------------------------------------
    # PÁGINA 2: PROPOSTA COMERCIAL & ORÇAMENTO
    # ------------------------------------------
    story.append(Paragraph("PROPOSTA COMERCIAL", style_subtitulo))
    story.append(Spacer(1, 10))
    
    # Bloco de Informações do Cliente
    info_cliente = [
        [Paragraph("<b>Empresa / Cliente:</b>", style_bold), Paragraph(dados["empresa"], style_corpo)],
        [Paragraph("<b>Contato:</b>", style_bold), Paragraph(dados["contato"], style_corpo)],
        [Paragraph("<b>Local do Evento:</b>", style_bold), Paragraph(dados["local"], style_corpo)],
        [Paragraph("<b>Data do Orçamento:</b>", style_bold), Paragraph(dados["data_orcamento"].strftime('%d/%m/%Y'), style_corpo)],
        [Paragraph("<b>Data do Evento:</b>", style_bold), Paragraph(dados["data_evento"].strftime('%d/%m/%Y'), style_corpo)],
        [Paragraph("<b>Horário / Escala:</b>", style_bold), Paragraph(dados["horario"], style_corpo)]
    ]
    t_cliente = Table(info_cliente, colWidths=[130, 385])
    t_cliente.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cliente)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Escopo de Serviços & Valores", style_subtitulo))
    story.append(Spacer(1, 10))
    
    # Tabela de Serviços
    tabela_servicos_dados = [
        [Paragraph("<b>Serviço / Item</b>", style_bold), Paragraph("<b>Descrição Resumida</b>", style_bold), Paragraph("<b>Subtotal</b>", style_bold)]
    ]
    
    for s in dados["servicos_detalhados"]:
        tabela_servicos_dados.append([
            Paragraph(s["nome"], style_corpo),
            Paragraph(s["desc"], style_corpo),
            Paragraph(f"R$ {s['valor']:.2f}", style_corpo)
        ])
        
    # Adicionar linha de Logística se houver custo cadastrado
    if dados["custo_logistica"] > 0:
        tabela_servicos_dados.append([
            Paragraph("Deslocamento & Logística", style_corpo),
            Paragraph(f"Combustível e pedágios (Distância total: {dados['distancia']} km)", style_corpo),
            Paragraph(f"R$ {dados['custo_logistica']:.2f}", style_corpo)
        ])
        
    t_servicos = Table(tabela_servicos_dados, colWidths=[140, 265, 110])
    t_servicos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))
    ]))
    story.append(t_servicos)
    story.append(Spacer(1, 15))
    
    # Valor Total Destacado
    dados_total = [
        [Paragraph(f"<b>VALOR TOTAL DO INVESTIMENTO ({dados['periodo']}):</b>", style_bold), Paragraph(f"<b>R$ {dados['valor_total']:.2f}</b>", style_subtitulo)]
    ]
    t_total = Table(dados_total, colWidths=[350, 165])
    t_total.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e0f2fe')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0284c7'))
    ]))
    story.append(t_total)
    story.append(Spacer(1, 15))
    
    # Condições Comerciais
    story.append(Paragraph("Condições Comerciais & Prazos", style_subtitulo))
    story.append(Spacer(1, 8))
    
    texto_condicoes = f"""
    <b>Forma de Entrega:</b> {dados['forma_entrega']}<br/>
    <b>Prazo de Entrega:</b> {dados['prazo_entrega']}<br/>
    <b>Condições de Pagamento:</b> {dados['forma_pagamento']}
    """
    story.append(Paragraph(texto_condicoes, style_corpo))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

# ==========================================
# INTERFACE DO USUÁRIO - STREAMLIT
# ==========================================
st.title("⚡ Gerador de Propostas Comerciais com PDF")
st.markdown("Preencha os dados abaixo para calcular os valores, incluir os custos de logística e gerar o documento em PDF formatado.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Informações do Cliente & Evento")
    empresa = st.text_input("Nome da Empresa / Cliente", "Ambient Serviços Ambientais S/A")
    contato = st.text_input("Pessoa de Contato", "Natalia")
    local = st.text_input("Local do Evento", "Rod. Alexandre Balbo km 334,6 - Ribeirão Preto - SP")
    data_orcamento = st.date_input("Data do Orçamento", datetime.now())
    data_evento = st.date_input("Data do Evento", datetime.now())
    horario = st.text_input("Horário / Escala", "08h00 às 18h00 (Intervalo de 1h30)")

with col2:
    st.subheader("2. Configuração de Serviços & Período")
    periodo_sel = st.selectbox("Selecione a Carga Horária Base", list(TABELA_HORAS.keys()))
    servicos_sel = st.multiselect(
        "Selecione os Serviços Contratados",
        list(SERVICOS_DISPONIVEIS.keys()),
        default=["Cobertura fotográfica", "Captação de vídeo"]
    )

st.markdown("---")

# ==========================================
# CÁLCULO DE DESLOCAMENTO E COMBUSTÍVEL
# ==========================================
st.subheader("🚗 Custos de Deslocamento e Logística")

with st.expander("Configurar Deslocamento (Distância e Combustível)", expanded=True):
    col_log1, col_log2, col_log3 = st.columns(3)
    
    with col_log1:
        distancia_ida_volta = st.number_input("Distância Total (Ida e Volta em km)", min_value=0.0, value=0.0, step=5.0)
    with col_log2:
        consumo_medio = st.number_input("Consumo Médio (km/L)", min_value=1.0, value=11.0, step=0.5) # Ex: média para SUV
    with col_log3:
        preco_combustivel = st.number_input("Preço do Litro (R$)", min_value=0.0, value=5.89, step=0.10)
        
    pedagio_total = st.number_input("Valor Total de Pedágios (Ida e Volta R$)", min_value=0.0, value=0.0, step=5.0)

# Cálculo do custo de combustível
litros_gastos = distancia_ida_volta / consumo_medio if consumo_medio > 0 else 0
custo_combustivel = litros_gastos * preco_combustivel
custo_logistica_total = custo_combustivel + pedagio_total

if distancia_ida_volta > 0:
    st.info(f"**Resumo do Deslocamento:** Consumo estimado de {litros_gastos:.1f} litros "
            f"(R$ {custo_combustivel:.2f} de combustível) + R$ {pedagio_total:.2f} de pedágios. "
            f"**Total de Logística: R$ {custo_logistica_total:.2f}**")

st.markdown("---")
st.subheader("3. Prazos e Pagamento")
forma_entrega = st.text_input("Forma de Entrega", "Link exclusivo (disponível por 30 dias para download em alta e baixa resolução).")
prazo_entrega = st.text_input("Prazo de Entrega", "Até 72h após o término do evento.")
forma_pagamento = st.text_input("Condições de Pagamento", "Faturamento em até 20 dias após o evento.")

# ==========================================
# CÁLCULO DINÂMICO DE VALORES
# ==========================================
valor_base_hora = TABELA_HORAS[periodo_sel]
servicos_detalhados = []
valor_total_servicos = 0.0

if servicos_sel:
    soma_fatores = sum([SERVICOS_DISPONIVEIS[s]["fator"] for s in servicos_sel])
    for s in servicos_sel:
        fator = SERVICOS_DISPONIVEIS[s]["fator"]
        v_item = valor_base_hora * (fator / soma_fatores) * len(servicos_sel) * 0.85 if len(servicos_sel) > 1 else valor_base_hora * fator
        servicos_detalhados.append({
            "nome": s,
            "desc": SERVICOS_DISPONIVEIS[s]["desc"],
            "valor": v_item
        })
        valor_total_servicos += v_item
else:
    valor_total_servicos = valor_base_hora

# INTEGRAÇÃO 1 & 2: O valor total agora soma os serviços + a logística calculada
valor_total_geral = valor_total_servicos + custo_logistica_total

st.markdown("---")
st.subheader("📊 Resumo do Investimento Calculado")
col_res1, col_res2, col_res3 = st.columns(3)
col_res1.metric("Carga Horária Base", periodo_sel)
col_res2.metric("Subtotal Serviços", f"R$ {valor_total_servicos:.2f}")
col_res3.metric("Valor Total Final (com Logística)", f"R$ {valor_total_geral:.2f}")

dados_completos = {
    "empresa": empresa,
    "contato": contato,
    "local": local,
    "data_orcamento": data_orcamento,
    "data_evento": data_evento,
    "horario": horario,
    "periodo": periodo_sel,
    "servicos_detalhados": servicos_detalhados,
    "distancia": distancia_ida_volta,
    "custo_logistica": custo_logistica_total,
    "valor_total": valor_total_geral,
    "forma_entrega": forma_entrega,
    "prazo_entrega": prazo_entrega,
    "forma_pagamento": forma_pagamento
}

# Botão de Download do PDF
pdf_bytes = gerar_pdf(dados_completos)
st.download_button(
    label="📥 Baixar Proposta Comercial em PDF",
    data=pdf_bytes,
    file_name=f"Proposta_Comercial_{empresa.replace(' ', '_')}.pdf",
    mime="application/pdf"
)

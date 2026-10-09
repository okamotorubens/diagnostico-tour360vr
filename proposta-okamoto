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

st.set_page_config(page_title="Gerador de Propostas - Mídias Visuais", page_icon="📄", layout="wide")

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
        "de tours virtuais e conteúdos em vídeo de alta definição.

"
        "Nossa missão é registrar cada momento do seu evento com precisão técnica, sensibilidade artística e rigor editorial, "
        "garantindo que sua empresa disponha de um acervo visual estratégico para mídias sociais, assessoria de imprensa e relatórios anuais."
    )
    story.append(Paragraph(texto_apresentacao, style_corpo))
    story.append(Spacer(1, 20))

    # Tabela de Diferenciais da Empresa
    story.append(Paragraph("Diferenciais Competitivos", style_subtitulo))
    story.append(Spacer(1, 8))
    
    dados_diferenciais = [
        [Paragraph("Recurso / Diferencial", style_bold), Paragraph("Benefício para o Cliente", style_bold)],
        [Paragraph("Equipamentos de Última Geração", style_corpo), Paragraph("Câmeras Full Frame e captação em áudio/vídeo digital sem ruído.", style_corpo)],
        [Paragraph("Entrega Ágil de Conteúdo", style_corpo), Paragraph("Envio de seleção rápida para redes sociais durante o próprio evento.", style_corpo)],
        [Paragraph("Fluxo de Trabalho Organizado", style_corpo), Paragraph("Plataforma dedicada de download com prazo estendido e segurança.", style_corpo)],
        [Paragraph("Experiência Consolidada", style_corpo), Paragraph("Atendimento a grandes encontros nacionais e internacionais.", style_corpo)]
    ]
    
    tabela_diferenciais = Table(dados_diferenciais, colWidths=[180, 335])
    tabela_diferenciais.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(tabela_diferenciais)
    
    # Quebra de página obrigatória para a Proposta Comercial
    story.append(PageBreak())

    # ------------------------------------------
    # PÁGINA 2: PROPOSTA COMERCIAL & ORÇAMENTO
    # ------------------------------------------
    story.append(Paragraph("PROPOSTA COMERCIAL", style_titulo))
    story.append(Paragraph(f"Data de Emissão: {dados['data_orcamento'].strftime('%d/%m/%Y')}", style_corpo))
    story.append(Spacer(1, 15))

    # Tabela de Dados do Cliente
    dados_cliente = [
        [Paragraph("Empresa:", style_bold), Paragraph(dados['empresa'], style_corpo)],
        [Paragraph("Contato:", style_bold), Paragraph(dados['contato'], style_corpo)],
        [Paragraph("Data do Evento:", style_bold), Paragraph(dados['data_evento'].strftime('%d/%m/%Y'), style_corpo)],
        [Paragraph("Horário:", style_bold), Paragraph(dados['horario'], style_corpo)],
        [Paragraph("Local:", style_bold), Paragraph(dados['local'], style_corpo)],
    ]
    t_cliente = Table(dados_cliente, colWidths=[110, 405])
    t_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_cliente)
    story.append(Spacer(1, 15))

    # Escopo dos Serviços Selecionados
    story.append(Paragraph("Escopo dos Serviços Solicitados", style_subtitulo))
    story.append(Spacer(1, 8))
    
    tabela_itens = [[Paragraph("Serviço", style_bold), Paragraph("Descrição do Atendimento", style_bold), Paragraph("Subtotal (R$)", style_bold)]]
    for srv in dados['servicos_detalhados']:
        tabela_itens.append([
            Paragraph(srv['nome'], style_corpo),
            Paragraph(srv['desc'], style_corpo),
            Paragraph(f"R$ {srv['valor']:.2f}", style_corpo)
        ])
    
    t_servicos = Table(tabela_itens, colWidths=[150, 265, 100])
    t_servicos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 7),
    ]))
    # Ajustando estilo do cabeçalho da tabela de serviços
    for i in range(3):
        t_servicos.setStyle(TableStyle([('TEXTCOLOR', (i, 0), (i, 0), colors.white)]))
    story.append(t_servicos)
    story.append(Spacer(1, 12))

    # Quadro de Investimento Total
    dados_investimento = [
        [Paragraph("Período Total Contratado:", style_bold), Paragraph(dados['periodo'], style_corpo)],
        [Paragraph("INVESTIMENTO TOTAL:", style_bold), Paragraph(f"R$ {dados['valor_total']:.2f}", style_bold)]
    ]
    t_invest = Table(dados_investimento, colWidths=[200, 315])
    t_invest.setStyle(TableStyle([
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#dbeafe')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#93c5fd')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_invest)
    story.append(Spacer(1, 15))

    # Condições Gerais, Entrega e Pagamento
    story.append(Paragraph("Condições de Fornecimento e Pagamento", style_subtitulo))
    story.append(Spacer(1, 6))
    
    texto_condicoes = f"""
    Forma de Entrega: {dados['forma_entrega']}

    Prazo de Entrega: {dados['prazo_entrega']}

    Forma de Pagamento: {dados['forma_pagamento']}
    """
    story.append(Paragraph(texto_condicoes, style_corpo))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

# ==========================================
# INTERFACE DO USUÁRIO - STREAMLIT
# ==========================================
st.title("⚡ Gerador de Propostas Comerciais com PDF")
st.markdown("Preencha os dados abaixo para calcular os valores e gerar o documento em PDF formatado.")

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
    
    st.subheader("3. Prazos e Pagamento")
    forma_entrega = st.text_input("Forma de Entrega", "Link exclusivo (disponível por 30 dias para download em alta e baixa resolução).")
    prazo_entrega = st.text_input("Prazo de Entrega", "Até 72h após o término do evento.")
    forma_pagamento = st.text_input("Condições de Pagamento", "Faturamento em até 20 dias após o evento.")

# ==========================================
# CÁLCULO DINÂMICO DE VALORES
# ==========================================
valor_base_hora = TABELA_HORAS[periodo_sel]
servicos_detalhados = []
valor_total = 0.0

if servicos_sel:
    # Divisão do valor base proporcionalmente aos serviços selecionados e seus multiplicadores
    soma_fatores = sum([SERVICOS_DISPONIVEIS[s]["fator"] for s in servicos_sel])
    for s in servicos_sel:
        fator = SERVICOS_DISPONIVEIS[s]["fator"]
        v_item = valor_base_hora * (fator / soma_fatores) * len(servicos_sel) * 0.85 if len(servicos_sel) > 1 else valor_base_hora * fator
        servicos_detalhados.append({
            "nome": s,
            "desc": SERVICOS_DISPONIVEIS[s]["desc"],
            "valor": v_item
        })
        valor_total += v_item
else:
    valor_total = valor_base_hora

st.markdown("---")
st.subheader("📊 Resumo do Investimento Calculado")
col_res1, col_res2 = st.columns(2)
col_res1.metric("Carga Horária Base", periodo_sel)
col_res2.metric("Valor Total Calculado", f"R$ {valor_total:.2f}")

dados_completos = {
    "empresa": empresa,
    "contato": contato,
    "local": local,
    "data_orcamento": data_orcamento,
    "data_evento": data_evento,
    "horario": horario,
    "periodo": periodo_sel,
    "servicos_detalhados": servicos_detalhados,
    "valor_total": valor_total,
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



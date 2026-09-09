import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.pdfgen import canvas

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CRM Okamoto Mídias Visuais",
    page_icon="💼",
    layout="wide"
)

# Caminho da Logo
caminho_logo = "assets/logo_okamoto.png" if os.path.exists("assets/logo_okamoto.png") else None

# Barra Lateral com Logo e Assinatura
with st.sidebar:
    if caminho_logo:
        st.image(caminho_logo, width=180)
    else:
        st.markdown("<h3 style='color: #f8fafc; margin:0;'>OKAMOTO MÍDIAS VISUAIS</h3>", unsafe_allow_html=True)
    
    st.markdown("<p style='color: #94a3b8; font-size: 12px; margin-top: 4px;'>criado por Rubens Okamoto</p>", unsafe_allow_html=True)
    st.markdown("---")

# -----------------------------------------------------------------------------
# 2. AUTENTICAÇÃO E LOGIN SEGURO
# -----------------------------------------------------------------------------
def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.title("🔐 Acesso Restrito - Okamoto Mídias Visuais")
        senha = st.text_input("Digite a senha de acesso:", type="password")
        if st.button("Entrar"):
            if senha == "okamoto2026":
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return False
    return True

if not verificar_senha():
    st.stop()

# -----------------------------------------------------------------------------
# 3. BASE DE DADOS EM MEMÓRIA / SESSÃO
# -----------------------------------------------------------------------------
if 'df_pedidos' not in st.session_state:
    st.session_state['df_pedidos'] = pd.DataFrame(columns=[
        "Numero_Pedido", "Empresa", "Contato", "Data_Emissao", "Data_Evento", "Valor_Total", "Status", "Servicos"
    ])

# Servicos Padrao
df_servicos = pd.DataFrame([
    {"Nome_Servico": "Cobertura fotográfica", "Tipo_Cobranca": "Hora", "Valor_Base": 180.0, "Descricao": "Registros fotográficos de alta resolução com edição de cores e contraste."},
    {"Nome_Servico": "Captação de vídeo", "Tipo_Cobranca": "Hora", "Valor_Base": 200.0, "Descricao": "Gravação em Full HD/4K (material bruto entregue via link)."},
    {"Nome_Servico": "Tour Virtual 360°", "Tipo_Cobranca": "Pacote", "Valor_Base": 800.0, "Descricao": "Mapeamento completo e publicação no Google Street View e ambiente web."},
    {"Nome_Servico": "Otimização Ficha Google", "Tipo_Cobranca": "Pacote", "Valor_Base": 400.0, "Descricao": "Estruturação técnica e atualização de atributos no Google Meu Negócio."}
])

# -----------------------------------------------------------------------------
# 4. GERADOR DE PDF DA PROPOSTA COM LOGO
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(40, 45, 555, 45)
        self.drawString(40, 30, "Okamoto Mídias Visuais | (16) 99133-2121 | okamotomidiasvisuais.com.br")
        self.drawRightString(555, 30, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

def gerar_pdf_proposta(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=60)
    styles = getSampleStyleSheet()
    
    style_titulo = ParagraphStyle('Titulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.HexColor('#0f172a'))
    style_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=colors.HexColor('#2563eb'))
    style_corpo = ParagraphStyle('Corpo', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=15, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=15, textColor=colors.HexColor('#0f172a'))
    
    story = []

    # LOGO NO TOPO DO PDF
    if caminho_logo:
        try:
            story.append(Image(caminho_logo, width=140, height=45))
            story.append(Spacer(1, 10))
        except Exception:
            pass

    # PÁGINA 1: INSTITUCIONAL
    story.append(Paragraph("OKAMOTO MÍDIAS VISUAIS", style_subtitulo))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Apresentação Institucional & Portfólio de Serviços", style_titulo))
    story.append(Spacer(1, 15))
    
    apresentacao = (
        "Com sólida experiência no mercado de imagem e fotografia profissional, a <b>Okamoto Mídias Visuais</b> "
        "é especializada na cobertura completa de eventos corporativos, institucionais e científicos, além de produção "
        "de tours virtuais 360° e conteúdos em vídeo de alta definição.<br/><br/>"
        "Nossa missão é registrar cada momento com precisão técnica, agilidade e rigor editorial."
    )
    story.append(Paragraph(apresentacao, style_corpo))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Diferenciais Competitivos", style_subtitulo))
    story.append(Spacer(1, 8))
    
    diferenciais = [
        [Paragraph("<b>Diferencial</b>", style_bold), Paragraph("<b>Benefício para o Cliente</b>", style_bold)],
        [Paragraph("Equipamentos Profissionais", style_corpo), Paragraph("Câmeras Full Frame e captação digital sem ruído.", style_corpo)],
        [Paragraph("Agilidade na Entrega", style_corpo), Paragraph("Envio de seleção rápida para redes sociais.", style_corpo)],
        [Paragraph("Plataforma Dedicada", style_corpo), Paragraph("Download seguro via link exclusivo.", style_corpo)],
    ]
    t_dif = Table(diferenciais, colWidths=[170, 345])
    t_dif.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_dif)
    story.append(PageBreak())

    # PÁGINA 2: PROPOSTA COMERCIAL
    if caminho_logo:
        try:
            story.append(Image(caminho_logo, width=120, height=38))
            story.append(Spacer(1, 10))
        except Exception:
            pass

    story.append(Paragraph("PROPOSTA COMERCIAL", style_titulo))
    story.append(Paragraph(f"Emissão: {dados['data_orcamento']} | Pedido nº: {dados['num_pedido']}", style_corpo))
    story.append(Spacer(1, 12))

    cliente_data = [
        [Paragraph("<b>Empresa:</b>", style_bold), Paragraph(dados['empresa'], style_corpo)],
        [Paragraph("<b>Contato:</b>", style_bold), Paragraph(dados['contato'], style_corpo)],
        [Paragraph("<b>Data Evento:</b>", style_bold), Paragraph(dados['data_evento'], style_corpo)],
        [Paragraph("<b>Horário / Escala:</b>", style_bold), Paragraph(dados['horario'], style_corpo)],
        [Paragraph("<b>Local:</b>", style_bold), Paragraph(dados['local'], style_corpo)],
    ]
    t_cli = Table(cliente_data, colWidths=[110, 405])
    t_cli.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_cli)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Escopo dos Serviços Solicitados", style_subtitulo))
    story.append(Spacer(1, 6))
    
    itens_data = [[Paragraph("<b>Serviço</b>", style_bold), Paragraph("<b>Descrição</b>", style_bold), Paragraph("<b>Subtotal</b>", style_bold)]]
    for srv in dados['itens']:
        itens_data.append([
            Paragraph(srv['nome'], style_corpo),
            Paragraph(srv['desc'], style_corpo),
            Paragraph(f"R$ {srv['valor']:.2f}", style_corpo)
        ])
    
    t_srv = Table(itens_data, colWidths=[140, 275, 100])
    t_srv.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(t_srv)
    story.append(Spacer(1, 10))

    invest_data = [
        [Paragraph("<b>Período / Carga Horária:</b>", style_bold), Paragraph(dados['periodo'], style_corpo)],
        [Paragraph("<b>INVESTIMENTO TOTAL:</b>", style_bold), Paragraph(f"<b>R$ {dados['valor_final']:.2f}</b>", style_bold)]
    ]
    t_inv = Table(invest_data, colWidths=[180, 335])
    t_inv.setStyle(TableStyle([
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#dbeafe')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#93c5fd')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_inv)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 5. PAINEL DO CRM
# -----------------------------------------------------------------------------
st.title("💼 CRM Okamoto Mídias Visuais")
st.write("Emissão de Propostas Comerciais e Gestão de Atendimentos")

num_pedido = st.text_input("Número do Pedido", f"PED-{datetime.now().strftime('%Y%m%d%H%M')}")
empresa_sel = st.text_input("Nome da Empresa", "Ambient Serviços Ambientais S/A")
contato = st.text_input("Pessoa de Contato", "Natalia")
local = st.text_input("Local do Evento", "Ribeirão Preto - SP")

data_orcamento = st.date_input("Data da Emissão", datetime.now()).strftime('%d/%m/%Y')
data_evento = st.date_input("Data do Evento", datetime.now()).strftime('%d/%m/%Y')
horario = st.text_input("Horário / Escala", "08h00 às 18h00")
periodo = st.selectbox("Carga Horária", ["1 hora", "2 horas", "4 horas", "10 horas (Diária)"])

servicos_sel = st.multiselect("Serviços Incluídos", df_servicos["Nome_Servico"].tolist(), default=["Cobertura fotográfica"])

itens_detalhados = []
valor_calculado = 0.0
for s in servicos_sel:
    row = df_servicos[df_servicos["Nome_Servico"] == s].iloc[0]
    v_base = float(row.get("Valor_Base", 0.0))
    itens_detalhados.append({"nome": s, "desc": str(row.get("Descricao", "")), "valor": v_base})
    valor_calculado += v_base

valor_final = st.number_input("Valor Final da Proposta (R$)", value=float(valor_calculado), step=50.0)

dados_pdf = {
    "num_pedido": num_pedido, "empresa": empresa_sel, "contato": contato, "local": local,
    "data_orcamento": data_orcamento, "data_evento": data_evento, "horario": horario,
    "periodo": periodo, "itens": itens_detalhados, "valor_final": valor_final
}

pdf_bytes = gerar_pdf_proposta(dados_pdf)

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.download_button(
        label="📥 Baixar Proposta Comercial em PDF",
        data=pdf_bytes,
        file_name=f"Proposta_{num_pedido}_{empresa_sel.replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
with col_btn2:
    # Exportação direta em CSV para controle sem erros de permissão
    if st.button("💾 Registrar Pedido na Sessão Local", use_container_width=True):
        novo = pd.DataFrame([{
            "Numero_Pedido": num_pedido, "Empresa": empresa_sel, "Contato": contato,
            "Data_Emissao": data_orcamento, "Data_Evento": data_evento,
            "Valor_Total": valor_final, "Status": "Proposta Emitida", "Servicos": ", ".join(servicos_sel)
        }])
        st.session_state['df_pedidos'] = pd.concat([st.session_state['df_pedidos'], novo], ignore_index=True)
        st.success(f"Pedido {num_pedido} registrado!")

if not st.session_state['df_pedidos'].empty:
    st.markdown("---")
    st.subheader("📋 Pedidos Emitidos na Sessão")
    st.dataframe(st.session_state['df_pedidos'], use_container_width=True)
    
    csv = st.session_state['df_pedidos'].to_csv(index=False).encode('utf-8')
    st.download_button("📊 Baixar Planilha de Pedidos (CSV/Excel)", data=csv, file_name="pedidos_okamoto.csv", mime="text/csv")

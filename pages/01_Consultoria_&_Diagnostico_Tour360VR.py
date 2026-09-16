import io
import os
import requests
import streamlit as st
from datetime import datetime
from PIL import Image

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Tour360VR - Gerador de Diagnóstico GMB", page_icon="📸", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .header-bar { background-color: #0B3C5D; color: white; padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-bar">
        <h2 style="margin:0; padding:0; color:white;">TOUR360VR | Diagnóstico & Gerador de Propostas GMB</h2>
        <p style="margin:5px 0 0 0; font-size:13px; opacity:0.9;">Gere relatórios automatizados fiéis ao padrão da marca</p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DADOS DO PERFIL (MOCK AUTOMÁTICO - SIMULANDO RETORNO DA API)
# -----------------------------------------------------------------------------
# Em produção, este dicionário é preenchido automaticamente ao selecionar a empresa
dados_perfil_auto = {
    "nome": "Banana e Banana Moda Praia",
    "endereco": "Av. Independência, 2366 - Alto da Boa Vista, Ribeirão Preto - SP, 14025-230, Brasil",
    "telefone": "(16) 99621-0707",
    "nota": 4.2,
    "avaliacoes": 43,
    "recencia": "há 2 meses",
    "score": 61,
    "foto_capa_url": "https://lh3.googleusercontent.com/p/AF1QipN3_example_photo.jpg", # URL real da foto da ficha
    "categorias": ["clothing_store", "establishment", "point_of_interest", "store"],
    "horarios": "Segunda a sexta 09:00 – 18:30, sábado 09:00 – 13:00, domingo fechado"
}

# -----------------------------------------------------------------------------
# SIDEBAR - APENAS O QUE É EDITÁVEL
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Ajustes da Proposta")

url_capa_override = st.sidebar.text_input("URL da Imagem da Ficha (Capa)", value="")
obs_consultor = st.sidebar.text_area("Observação/Gatilho Personalizado", value="Seus concorrentes locais não possuem tour 360°. Oportunidade única para liderar a região.")

st.sidebar.subheader("💰 Tabela de Preços")
p1_valor = st.sidebar.text_input("Opção 1", "500,00 ou 2x de R$ 250,00 s/juros")
p2_valor = st.sidebar.text_input("Opção 2 (Recomendado)", "900,00 ou 3x de R$ 300,00 s/juros")
p3_valor = st.sidebar.text_input("Opção 3", "A combinar")

# -----------------------------------------------------------------------------
# CLASS CANVAS PARA RODAPÉ PADRÃO EM TODAS AS PÁGINAS
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
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#666666"))
        
        # Linha do rodapé
        self.setStrokeColor(colors.HexColor("#D0D0D0"))
        self.setLineWidth(0.5)
        self.line(1.5*cm, 1.2*cm, 19.5*cm, 1.2*cm)
        
        # Texto do rodapé
        rodape_txt = "Rubens Okamoto  |  contato@tour360vr.com.br  |  (16) 99133-2121  |  tour360vr.com.br  |  Ribeirão Preto - SP"
        self.drawString(1.5*cm, 0.8*cm, rodape_txt)
        self.drawRightString(19.5*cm, 0.8*cm, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

# -----------------------------------------------------------------------------
# GERADOR DE PDF
# -----------------------------------------------------------------------------
def gerar_pdf_oficial():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.8*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Cores
    c_blue = colors.HexColor("#0B3C5D")
    c_cyan = colors.HexColor("#328CC1")
    c_bg = colors.HexColor("#F8F9FA")
    c_dark = colors.HexColor("#1D2731")
    
    # Estilos de Texto
    st_header_brand = ParagraphStyle('Brand', fontName='Helvetica-Bold', fontSize=18, textColor=c_blue)
    st_title = ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=20, textColor=c_blue, leading=24)
    st_subtitle = ParagraphStyle('SubTitle', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#D9534F"), leading=14)
    st_h2 = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=13, textColor=c_blue, spaceBefore=10, spaceAfter=4)
    st_body = ParagraphStyle('Body', fontName='Helvetica', fontSize=8.5, textColor=c_dark, leading=11)
    st_body_bold = ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=8.5, textColor=c_dark, leading=11)
    st_th = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.white, leading=11)

    elements = []

    # -------------------------------------------------------------------------
    # PÁGINA 1: CAPA
    # -------------------------------------------------------------------------
    elements.append(Paragraph("<b>TOUR <font color='#328CC1'>360</font> VR</b>", st_header_brand))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph("DIAGNÓSTICO GOOGLE MEU NEGÓCIO", st_title))
    elements.append(Spacer(1, 0.1*cm))
    
    sub_txt = f"Seu perfil tem nota sólida, mas {dados_perfil_auto['avaliacoes']} avaliações e zero fotos 360° deixam dinheiro na mesa — concorrentes estão à frente."
    elements.append(Paragraph(sub_txt.upper(), st_subtitle))
    elements.append(Spacer(1, 0.4*cm))

    # Box de identificação
    info_capa = [
        [Paragraph(f"<b>Preparado para:</b> {dados_perfil_auto['nome']}", st_body)],
        [Paragraph(f"{dados_perfil_auto['endereco']}", st_body)],
        [Paragraph(f"<b>Data:</b> {datetime.now().strftime('%d/%m/%Y')}  |  <b>Avaliadores:</b> {dados_perfil_auto['avaliacoes']} avaliações ({dados_perfil_auto['nota']}★)", st_body)]
    ]
    t_info = Table(info_capa, colWidths=[17*cm])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 0.6*cm))

    # Imagem da Capa (Se informada URL ou padrao)
    img_target = url_capa_override if url_capa_override else dados_perfil_auto['foto_capa_url']
    try:
        resp = requests.get(img_target, timeout=3)
        if resp.status_code == 200:
            img_io = io.BytesIO(resp.content)
            elements.append(RLImage(img_io, width=17*cm, height=8.5*cm))
    except:
        # Moldura reservada caso a imagem não carregue via rede
        t_placeholder = Table([[Paragraph("<b>[IMAGEM DA FICHA GOOGLE DO CLIENTE]</b>", ParagraphStyle('Center', parent=st_body, alignment=1))]], colWidths=[17*cm], rowHeights=[7*cm])
        t_placeholder.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), c_bg), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elements.append(t_placeholder)

    elements.append(PageBreak())

    # -------------------------------------------------------------------------
    # PÁGINA 2: DIAGNÓSTICO E DIMENSÕES
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Como está o seu Google hoje", st_h2))
    elements.append(Spacer(1, 0.2*cm))

    # KPIs
    kpi_table = [
        [Paragraph("OTIMIZAÇÃO DO PERFIL", st_body_bold), Paragraph("NOTA DOS CLIENTES", st_body_bold), Paragraph("TOUR VIRTUAL 360°", st_body_bold)],
        [Paragraph(f"<font size=16 color='#0B3C5D'><b>{dados_perfil_auto['score']}/100</b></font>", st_body), Paragraph(f"<font size=16 color='#0B3C5D'><b>{dados_perfil_auto['nota']} ★</b></font>", st_body), Paragraph("<font size=12 color='#D9534F'><b>NÃO DETECTADO</b></font>", st_body)],
        [Paragraph("Oportunidades claras de ganho", st_body), Paragraph(f"{dados_perfil_auto['avaliacoes']} avaliações ({dados_perfil_auto['recencia']})", st_body), Paragraph("Oportunidade para sair na frente", st_body)]
    ]
    t_kpi = Table(kpi_table, colWidths=[5.6*cm, 5.6*cm, 5.6*cm])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    elements.append(t_kpi)
    elements.append(Spacer(1, 0.4*cm))

    # Dimensões
    elements.append(Paragraph("Análise de Dimensões do Perfil", st_h2))
    dim_data = [
        [Paragraph("Dimensão", st_th), Paragraph("Estado Atual", st_th), Paragraph("Impacto no Negócio", st_th)],
        [Paragraph("Completude do cadastro", st_body_bold), Paragraph("Nome, endereço e telefone preenchidos, sem site próprio e sem descrição.", st_body), Paragraph("Visitantes não conhecem sua história nem diferenciais.", st_body)],
        [Paragraph("Nota e avaliações", st_body_bold), Paragraph(f"{dados_perfil_auto['nota']} de 5 com {dados_perfil_auto['avaliacoes']} avaliações, sem respostas recentes.", st_body), Paragraph("Clientes 5 estrelas sem retorno. Concorrentes respondem e ganham confiança.", st_body)],
        [Paragraph("Consistência de NAP", st_body_bold), Paragraph(f"Telefone {dados_perfil_auto['telefone']} e endereço alinhados.", st_body), Paragraph("O Google confia nos seus dados de localização.", st_body)],
        [Paragraph("Fotos e Imersão 360°", st_body_bold), Paragraph("Fotos convencionais presentes; **zero tour 360°**.", st_body), Paragraph("Sem imersão visual. Visitantes passam menos tempo no seu perfil.", st_body)],
        [Paragraph("Horários e Posts", st_body_bold), Paragraph("Horários atualizados; sem publicações de novidades.", st_body), Paragraph("Perfil estático não atrai visitas de retorno.", st_body)]
    ]
    t_dim = Table(dim_data, colWidths=[4.0*cm, 6.5*cm, 6.5*cm])
    t_dim.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_blue),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D0D0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg])
    ]))
    elements.append(t_dim)
    elements.append(PageBreak())

    # -------------------------------------------------------------------------
    # PÁGINA 3: CONCORRÊNCIA E DIFERENCIAL
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Concorrentes na Região", st_h2))
    elements.append(Spacer(1, 0.2*cm))
    
    conc_data = [
        [Paragraph("#", st_th), Paragraph("Estabelecimento", st_th), Paragraph("Nota", st_th), Paragraph("Avaliações", st_th)],
        [Paragraph("1º", st_body), Paragraph("Empório das Essências Loja 1", st_body), Paragraph("4,7 ★", st_body), Paragraph("2.245", st_body)],
        [Paragraph("2º", st_body), Paragraph("Atelier Neide Amaral", st_body), Paragraph("4,7 ★", st_body), Paragraph("409", st_body)],
        [Paragraph("3º", st_body), Paragraph("Lojas Renner", st_body), Paragraph("4,4 ★", st_body), Paragraph("3.283", st_body)],
        [Paragraph("4º", st_body), Paragraph(f"<b>{dados_perfil_auto['nome']} (Você)</b>", st_body_bold), Paragraph(f"<b>{dados_perfil_auto['nota']} ★</b>", st_body_bold), Paragraph(f"<b>{dados_perfil_auto['avaliacoes']}</b>", st_body_bold)]
    ]
    t_conc = Table(conc_data, colWidths=[1.5*cm, 9.5*cm, 3.0*cm, 3.0*cm])
    t_conc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_blue),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D0D0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg])
    ]))
    elements.append(t_conc)
    elements.append(Spacer(1, 0.6*cm))

    elements.append(Paragraph("Planos de Ação e Investimento", st_h2))
    plans_data = [
        [Paragraph("OPÇÃO 1<br/>Ficha Otimizada", st_th), Paragraph("OPÇÃO 2 (RECOMENDADO)<br/>Ficha + Tour 360°", st_th), Paragraph("OPÇÃO 3<br/>Presença Completa", st_th)],
        [Paragraph(f"R$ {p1_valor}", st_body_bold), Paragraph(f"R$ {p2_valor}", st_body_bold), Paragraph(f"{p3_valor}", st_body_bold)],
        [
            Paragraph("• Otimização do perfil<br/>• Descrição SEO<br/>• Categorias corretas<br/>• Padronização NAP", st_body),
            Paragraph("• Tudo da Opção 1<br/><b>+ Tour Virtual 360° na Ficha do Google</b><br/>• Fotos HD de interatividade", st_body),
            Paragraph("• Tudo da Opção 2<br/><b>+ Tour 360° Personalizado no seu Site</b>", st_body)
        ]
    ]
    t_plans = Table(plans_data, colWidths=[5.6*cm, 5.6*cm, 5.6*cm])
    t_plans.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), c_blue),
        ('BACKGROUND', (1,0), (1,0), c_cyan),
        ('BACKGROUND', (2,0), (2,0), c_blue),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D0D0D0")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(t_plans)
    elements.append(Spacer(1, 0.6*cm))

    # Box Fechamento / CTA
    cta_box = [
        [Paragraph("<font color='white' size=11><b>Quer sair na frente da concorrência?</b></font>", st_body_bold)],
        [Paragraph("<font color='white'>Vamos mostrar como um Tour Virtual 360° + otimização de perfil pode aumentar sua visibilidade no Google local. Fale conosco pelo WhatsApp.</font>", st_body)],
        [Paragraph("<font color='#328CC1' size=11><b>📲 Falar com a TOUR360VR: (16) 99133-2121</b></font>", st_body_bold)]
    ]
    t_cta = Table(cta_box, colWidths=[17*cm])
    t_cta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_blue),
        ('PADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    elements.append(t_cta)

    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# INTERFACE DO STREAMLIT
# -----------------------------------------------------------------------------
st.subheader(f"Empresa Selecionada: {dados_perfil_auto['nome']}")
st.write(f"📍 {dados_perfil_auto['endereco']}")

col_a, col_b = st.columns(2)
with col_a:
    st.download_button(
        label="📥 Gerar e Baixar PDF do Diagnóstico",
        data=gerar_pdf_oficial(),
        file_name=f"Diagnostico_GMB_{dados_perfil_auto['nome'].replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

with col_b:
    st.info("O PDF gerado utilizará as fotos reais da ficha do cliente, a barra de rodapé com seus dados de contato e os valores ajustados na sidebar.")

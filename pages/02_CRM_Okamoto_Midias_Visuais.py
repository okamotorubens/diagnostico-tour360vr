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
# ALGORITMO NATIVO EM PYTHON PURO PARA VALOR POR EXTENSO
# -----------------------------------------------------------------------------
UNIDADES = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"]
DEZ_A_DEZANOVE = ["dez", "onze", "doze", "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
DEZENAS = ["", "", "vinte", "trinta", "quarenta", "quinquenta", "sessenta", "setenta", "oitenta", "noventa"]
CENTENAS = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos"]

def _converter_grupo_3(n):
    if n == 0:
        return ""
    if n == 100:
        return "cem"
    
    c = n // 100
    d = (n % 100) // 10
    u = n % 10
    
    partes = []
    if c > 0:
        partes.append(CENTENAS[c])
    
    dezena_unidade = n % 100
    if 10 <= dezena_unidade <= 19:
        partes.append(DEZ_A_DEZANOVE[dezena_unidade - 10])
    else:
        if d > 0:
            partes.append(DEZENAS[d])
        if u > 0:
            partes.append(UNIDADES[u])
            
    return " e ".join(partes)

def numero_por_extenso(valor):
    if valor == 0:
        return "zero"
    
    milhares = valor // 1000
    unidades = valor % 1000
    
    partes = []
    if milhares > 0:
        if milhares == 1:
            partes.append("um mil")
        else:
            partes.append(f"{_converter_grupo_3(milhares)} mil")
            
    if unidades > 0:
        ext_u = _converter_grupo_3(unidades)
        if ext_u:
            partes.append(ext_u)
            
    return " e ".join(partes)

def converter_valor_extenso(valor):
    try:
        val_float = float(valor)
        inteiro = int(val_float)
        centavos = int(round((val_float - inteiro) * 100))
        
        str_int = ""
        if inteiro == 1:
            str_int = "um real"
        elif inteiro > 1:
            ext_int = numero_por_extenso(inteiro)
            str_int = f"{ext_int} reais"
            
        str_cent = ""
        if centavos == 1:
            str_cent = "um centavo"
        elif centavos > 1:
            ext_cent = numero_por_extenso(centavos)
            str_cent = f"{ext_cent} centavos"
            
        if str_int and str_cent:
            res = f"({str_int} e {str_cent})"
        elif str_int:
            res = f"({str_int})"
        elif str_cent:
            res = f"({str_cent})"
        else:
            res = "(zero reais)"
            
        return res.capitalize()
    except Exception:
        return f"({valor:,.2f} reais)"

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E CSS TEMA DASHBOARD
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CRM Okamoto Mídias Visuais",
    page_icon="💼",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0b0f17; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }
    .card-kanban {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

LISTA_TAGS = [
    "ACADEMIA", "COMÉRCIO", "CONCESSIONÁRIA", "SALÃO DE BELEZA", 
    "IMOBILIÁRIA", "ESCOLAS", "ESPAÇO DE EVENTOS", "CLÍNICAS", 
    "VEICULOS", "AVIRRP", "SEBRAE", "HOTELARIA", "GASTRONOMIA", 
    "PREFEITURA", "TURISMO", "MOTEL", "BARZINHO", "OUTROS"
]

# -----------------------------------------------------------------------------
# 2. GERENCIAMENTO DA LOGO
# -----------------------------------------------------------------------------
if 'logo_bytes' not in st.session_state:
    st.session_state['logo_bytes'] = None

def obter_logo_imagem():
    caminhos = [
        'assets/logo_okamoto.png', 'logo_okamoto.png', 
        'assets/Logo_TOUR_transparente.png', 'Logo_TOUR_transparente.png'
    ]
    for c in caminhos:
        if os.path.exists(c):
            with open(c, "rb") as f:
                return f.read()
    return None

if st.session_state['logo_bytes'] is None:
    st.session_state['logo_bytes'] = obter_logo_imagem()

with st.sidebar:
    st.markdown("### 🖼️ Logo do Sistema")
    if st.session_state['logo_bytes']:
        st.image(st.session_state['logo_bytes'], use_container_width=True)
    else:
        st.info("Logo não encontrada no servidor.")
    
    upload_logo = st.file_uploader("Enviar/Atualizar Logo (PNG/JPG):", type=["png", "jpg", "jpeg"], key="upl_logo_side")
    if upload_logo:
        st.session_state['logo_bytes'] = upload_logo.getvalue()
        st.success("Logo carregada!")
        st.rerun()

    st.markdown("""
    <div style="padding: 5px 0px;">
        <h3 style="margin: 0; color: #f8fafc; font-size: 18px;">OKAMOTO MÍDIAS VISUAIS</h3>
        <p style="margin: 2px 0 0 0; color: #94a3b8; font-size: 12px;">criado por Rubens Okamoto</p>
    </div>
    <hr style="margin: 10px 0; border-color: #334155;"/>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. AUTENTICAÇÃO
# -----------------------------------------------------------------------------
def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.title("🔐 Acesso Restrito - Okamoto Mídias Visuais")
        senha = st.text_input("Digite a senha de acesso:", type="password")
        if st.button("Entrar", use_container_width=True):
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
# 4. BANCO DE DADOS EM SESSÃO PERSISTENTE
# -----------------------------------------------------------------------------
if 'df_pedidos' not in st.session_state:
    st.session_state['df_pedidos'] = pd.DataFrame([
        {
            "Numero_Pedido": "Pedido 0002",
            "Empresa": "Clínica Personalitté",
            "Contato": "Joseph",
            "Telefone": "(16) 99767-8802",
            "Local": "Ribeirão Preto - SP",
            "Data_Emissao": "08 de Setembro de 2026",
            "Nome_Evento": "2º Encontro Internacional Técnico GS Inima Brasil",
            "Data_Evento_Detalhada": "Dias 04 e 05/11/2026, das 8h00 as 17h00",
            "Objetivo": "Cobertura fotográfica do evento\n• Captação de vídeo em Full HD\n• Período das 08h00 as 18h00\nIntervalo de 1h30 de almoço",
            "Captacao": "Registros fotográficos e captações pontuais em vídeo (participantes, autoridades, apresentações, intervalos, entre outros momentos do evento).",
            "Entrega": "Todo material fotográfico será editado e enviado, em alta e baixa resolução.\n• Todo material em vídeo será enviado bruto (sem edição).\nOs materiais serão enviados via link e ficará disponível pelo prazo de 30 dias para download.",
            "Prazo_Entrega": "Até 72h após o término do evento.",
            "Valor_Subtotal": 3700.0,
            "Desconto_Pct": 0.0,
            "Valor_Total": 3700.0,
            "Valor_Extenso": converter_valor_extenso(3700.0),
            "Condicoes_Pag": "Até 20 dias após o evento.",
            "Status": "Orçamento / Proposta",
            "Servicos": "Cobertura Fotográfica e Captação de Vídeo"
        }
    ])

if 'df_clientes' not in st.session_state:
    st.session_state['df_clientes'] = pd.DataFrame([
        {
            "Empresa": "Clínica Personalitté", 
            "Contato": "Joseph", 
            "Cidade": "Ribeirão Preto - SP", 
            "Telefone": "+55 (16) 99767-8802", 
            "Email": "joseph@personalitte.com.br", 
            "Categoria / TAG": "CLÍNICAS",
            "Atividade": "Estética Avançada e Saúde",
            "Website": "www.clinicapersonalitte.com.br",
            "Instagram": "@clinicapersonalitte"
        }
    ])

if 'df_servicos' not in st.session_state:
    st.session_state['df_servicos'] = pd.DataFrame([
        {"Nome_Servico": "Cobertura Fotográfica e Captação de Vídeo", "Tipo_Cobranca": "Diária", "Valor_Base": 3700.0, "Descricao": "Cobertura completa em foto e vídeo para eventos institucionais."},
        {"Nome_Servico": "Google Street View / Tour 360°", "Tipo_Cobranca": "Pacote", "Valor_Base": 800.0, "Descricao": "Mapeamento panorâmico 360° e integração com Google Meu Negócio."}
    ])

if 'texto_institucional' not in st.session_state:
    st.session_state['texto_institucional'] = (
        "Com sólida experiência no mercado de imagem e fotografia profissional com mais de 30 anos de atuação, "
        "a Okamoto Mídias Visuais é especializada na cobertura completa de eventos corporativos, institucionais "
        "e científicos, além da produção de tours virtuais 360° de alta definição.\n\n"
        "Nossa missão é registrar cada projeto com precisão técnica, agilidade e excelência visual, "
        "garantindo um acervo de alta qualidade para ações de comunicação, mídias sociais e divulgação institucional."
    )

df_pedidos = st.session_state['df_pedidos']
df_clientes = st.session_state['df_clientes']
df_servicos = st.session_state['df_servicos']

# -----------------------------------------------------------------------------
# 5. GERADOR DE PDF AJUSTADO COM RODAPÉ COM LINKS E LAYOUT DESCOMPACTADO
# -----------------------------------------------------------------------------
class CanvasExecutivoAlinhado(canvas.Canvas):
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
            
            # Linha decorativa superior
            self.setStrokeColor(colors.HexColor('#0284c7'))
            self.setLineWidth(2.0)
            self.line(35, 815, 560, 815)
            
            # Linha e rodapé fixo
            self.setStrokeColor(colors.HexColor('#e2e8f0'))
            self.setLineWidth(0.5)
            self.line(35, 35, 560, 35)
            
            # RODAPÉ COM INVERSÃO: ENDEREÇO DO SITE PRIMEIRO, DEPOIS TELEFONE (AMBOS COM LINKS)
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#0284c7"))
            
            # Link para o site
            self.drawString(35, 20, "okamotomidiasvisuais.com.br")
            self.linkURL("https://okamotomidiasvisuais.com.br", (35, 15, 160, 28), relative=0)
            
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawString(165, 20, "|")
            
            # Link para o telefone/WhatsApp
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#0284c7"))
            self.drawString(175, 20, "16 99133 2121")
            self.linkURL("https://wa.me/5516991332121", (175, 15, 240, 28), relative=0)
            
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawRightString(560, 20, f"Página {self._pageNumber}/{num_pages}")
            self.restoreState()
            super().showPage()
        super().save()

def gerar_pdf_3_paginas_corrigido(dados, texto_institucional):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=40, bottomMargin=45)
    styles = getSampleStyleSheet()
    
    # TIPOGRAFIA AJUSTADA E RECALIBRADA
    style_tit_capa = ParagraphStyle('TitCapa', fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.HexColor('#0f172a'))
    style_sub_capa = ParagraphStyle('SubCapa', fontName='Helvetica', fontSize=10.5, leading=14, textColor=colors.HexColor('#0284c7'))
    style_tit_prop = ParagraphStyle('TitP', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#0f172a'))
    style_data = ParagraphStyle('DataP', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor('#0284c7'))
    
    # REDUZIDO TAMANHO DAS INFORMAÇÕES DO CLIENTE
    style_label_cli = ParagraphStyle('LblCli', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=colors.HexColor('#0f172a'))
    style_val_cli = ParagraphStyle('ValCli', fontName='Helvetica', fontSize=9.5, leading=13, textColor=colors.HexColor('#1e293b'))
    
    style_label = ParagraphStyle('Lbl', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor('#0f172a'))
    style_val = ParagraphStyle('Val', fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#334155'))
    style_sec_num = ParagraphStyle('SecNum', fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.HexColor('#0284c7'))
    
    # TITULOS PRINCIPAIS AUMENTADOS
    style_sec_tit = ParagraphStyle('SecTit', fontName='Helvetica-Bold', fontSize=13.5, leading=17, textColor=colors.HexColor('#0f172a'))
    style_sec_tit_sub = ParagraphStyle('SecTitSub', fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor('#0284c7'))
    
    style_txt_block = ParagraphStyle('TxtBlock', fontName='Helvetica', fontSize=9, leading=14, textColor=colors.HexColor('#334155'))
    style_inst = ParagraphStyle('Inst', fontName='Helvetica', fontSize=9.5, leading=15, textColor=colors.HexColor('#1e293b'))
    style_center = ParagraphStyle('CenterText', fontName='Helvetica', fontSize=9.5, leading=14, textColor=colors.HexColor('#334155'), alignment=1)

    story = []

    def obter_bloco_logo(w=140, h=45):
        if st.session_state.get('logo_bytes'):
            try:
                img_buf = io.BytesIO(st.session_state['logo_bytes'])
                return Image(img_buf, width=w, height=h)
            except Exception:
                pass
        return Paragraph("<font size='16' color='#0284c7'><b>OKAMOTO MÍDIAS VISUAIS</b></font>", style_label)

    # =========================================================================
    # PÁGINA 1: APRESENTAÇÃO INSTITUCIONAL
    # =========================================================================
    logo_p1 = obter_bloco_logo(155, 50)
    
    # TITULO "OKAMOTO MÍDIAS VISUAIS" AUMENTADO E "Fotografia Profissional..." REDUZIDO
    cabecalho_p1_text = (
        "<font size='18' color='#0f172a'><b>OKAMOTO MÍDIAS VISUAIS</b></font><br/>"
        "<font color='#0284c7' size='8.5'>Fotografia Profissional & Tours Virtuais 360°</font>"
    )
    t_top_p1 = Table([[logo_p1, Paragraph(cabecalho_p1_text, ParagraphStyle('RHead', fontName='Helvetica', alignment=2, leading=16))]], colWidths=[160, 365])
    t_top_p1.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_top_p1)
    story.append(Spacer(1, 25))

    story.append(Paragraph("Apresentação Institucional", style_sec_tit))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Excelência em Registros Visuais e Soluções Tecnológicas de Imagem", style_sub_capa))
    story.append(Spacer(1, 18))

    card_inst = [Paragraph(texto_institucional.replace('\n', '<br/>'), style_inst)]
    t_card_inst = Table([[card_inst]], colWidths=[525])
    t_card_inst.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0284c7')),
        ('PADDING', (0,0), (-1,-1), 14),
    ]))
    story.append(t_card_inst)
    story.append(Spacer(1, 28))

    story.append(Paragraph("Áreas de Atuação & Soluções Especializadas", style_sec_tit))
    story.append(Spacer(1, 16))

    solucoes = [
        ("• Eventos Corporativos & Científicos", "Cobertura fotográfica e em vídeo com equipamentos Full Frame e captações pontuais de alta precisão."),
        ("• Tours Virtuais 360° & Google GSV", "Mapeamento panorâmico imersivo de alta resolução com integração direta ao Google Meu Negócio."),
        ("• Agilidade para Mídias Sociais & Assessoria", "Envio acelerado de prévias em tempo real durante a execução do evento para publicações estratégicas."),
        ("• Plataforma Nuvem Exclusiva", "Acesso seguro, organizado e permanente para download dos acervos em alta e baixa resolução.")
    ]

    for tit_sol, desc_sol in solucoes:
        story.append(Paragraph(f"<b><font color='#0284c7'>{tit_sol}</font></b>", style_label))
        story.append(Spacer(1, 2))
        story.append(Paragraph(desc_sol, style_txt_block))
        story.append(Spacer(1, 10))

    # =========================================================================
    # PÁGINA 2: ORÇAMENTO COMERCIAL (COM ESPAÇOS DESCOMPACTADOS)
    # =========================================================================
    story.append(PageBreak())

    col_tit = [
        Paragraph("PROPOSTA COMERCIAL", style_tit_prop),
        Spacer(1, 4),
        Paragraph(f"Proposta {dados['num_pedido']}  |  {dados['data_orcamento']}", style_data)
    ]
    col_logo = [obter_bloco_logo(125, 40)]

    t_top_p2 = Table([[col_tit, col_logo]], colWidths=[330, 195])
    t_top_p2.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
    story.append(t_top_p2)
    story.append(Spacer(1, 18))

    # REDUZIDO O TAMANHO DOS CAMPOS DE EMPRESA, CONTATO E LOCAL
    t_cli_data = [
        [Paragraph("Empresa:", style_label_cli), Paragraph(f"<b>{dados['empresa']}</b>", style_val_cli)],
        [Paragraph("Contato:", style_label_cli), Paragraph(dados['contato'], style_val_cli)],
        [Paragraph("Local:", style_label_cli), Paragraph(dados['local'], style_val_cli)]
    ]
    t_cli = Table(t_cli_data, colWidths=[70, 455])
    t_cli.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
    ]))
    story.append(t_cli)
    story.append(Spacer(1, 24))

    # TÍTULO AUMENTADO PARA "Escopo do Serviço"
    story.append(Paragraph("Escopo do Serviço", style_sec_tit))
    story.append(Spacer(1, 14))

    def criar_bloco_escopo_item(numero, titulo, conteudo):
        c1 = Paragraph(f"<b>{numero}</b>", style_sec_num)
        c2 = [
            Paragraph(f"<b>{titulo}</b>", style_sec_tit_sub),
            Spacer(1, 3),
            Paragraph(conteudo.replace('\n', '<br/>'), style_txt_block)
        ]
        t = Table([[c1, c2]], colWidths=[22, 503])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6)
        ]))
        return t

    story.append(criar_bloco_escopo_item("1", "Evento", f"{dados['nome_evento']}\n• {dados['data_evento_detalhada']}\n{dados['local']}"))
    story.append(Spacer(1, 6))
    story.append(criar_bloco_escopo_item("2", "Objetivo", dados['objetivo']))
    story.append(Spacer(1, 6))
    story.append(criar_bloco_escopo_item("3", "Captação", dados['captacao']))
    story.append(Spacer(1, 6))
    story.append(criar_bloco_escopo_item("4", "Entrega", dados['entrega']))
    story.append(Spacer(1, 6))
    story.append(criar_bloco_escopo_item("5", "Prazo de Entrega", dados['prazo_entrega']))
    story.append(Spacer(1, 6))
    story.append(criar_bloco_escopo_item("6", "Forma de Pagamento", dados['condicoes_pag']))
    story.append(Spacer(1, 20))

    # REMOVIDO O QUADRO DO VALOR DO INVESTIMENTO - AGORA É TEXTO LIMPO NO CORPO
    story.append(Paragraph("<font color='#0284c7' size='11'><b>INVESTIMENTO DO SERVIÇO</b></font>", style_label))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<font size='13' color='#0f172a'><b>Valor Total: R$ {dados['valor_total']:,.2f}</b></font>", style_label))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"<b>{dados['valor_extenso']}</b>", style_txt_block))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Estamos à disposição para qualquer esclarecimento adicional, ou alteração, caso seja necessário.", style_txt_block))
    story.append(Spacer(1, 30))

    story.append(Paragraph("Atenciosamente,<br/><b>Rubens Okamoto</b><br/><font color='#0284c7'><b>OKAMOTO MÍDIAS VISUAIS</b></font>", style_center))

    # =========================================================================
    # PÁGINA 3: DADOS CADASTRAIS (COM ESPAÇAMENTO RECALIBRADO)
    # =========================================================================
    story.append(PageBreak())

    story.append(obter_bloco_logo(135, 44))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Dados Cadastrais & Informações Bancárias", style_sec_tit))
    story.append(Spacer(1, 24))

    def criar_bloco_vertical(titulo, linhas):
        c_tot = [Paragraph(f"<b><font color='#0284c7'>{titulo}</font></b>", style_sec_tit_sub), Spacer(1, 6)]
        for lbl, val in linhas:
            c_tot.append(Paragraph(f"<b>{lbl}:</b> {val}", style_val))
            c_tot.append(Spacer(1, 2))
        t = Table([[c_tot]], colWidths=[525])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 10),
        ]))
        return t

    b_emp_vert = criar_bloco_vertical("Dados da Empresa", [
        ("Razão Social", "Okamoto Reportagens Fotográficas SS Ltda"),
        ("CNPJ", "04.824.331/0001-05"),
        ("Endereço", "Rua General Carneiro, 860 - Centro"),
        ("Cidade/UF", "Brodowski - SP | CEP: 14.340-023")
    ])

    b_pes_vert = criar_bloco_vertical("Dados Pessoais", [
        ("Responsável", "Rubens Heigasi Okamoto"),
        ("CPF", "287.932.298-79"),
        ("Telefone/WhatsApp", "16 99133 2121"),
        ("E-mail", "contato@okamotomidiasvisuais.com.br")
    ])

    b_ban_vert = criar_bloco_vertical("Dados Bancários", [
        ("Banco", "Banco do Brasil"),
        ("Agência", "3235-2"),
        ("Conta Corrente", "11.935-0"),
        ("Chave PIX (CNPJ)", "04824331000105")
    ])

    story.append(b_emp_vert)
    story.append(Spacer(1, 20))
    story.append(b_pes_vert)
    story.append(Spacer(1, 20))
    story.append(b_ban_vert)

    doc.build(story, canvasmaker=CanvasExecutivoAlinhado)
    buffer.seek(0)
    return buffer

def gerar_pdf_ficha_cliente(cliente_data, pedidos_cli):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=35, bottomMargin=45)
    styles = getSampleStyleSheet()
    
    style_tit = ParagraphStyle('Tit', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor('#0f172a'))
    style_sub = ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#0284c7'))
    style_td = ParagraphStyle('TD', fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#334155'))

    story = [
        Paragraph("OKAMOTO MÍDIAS VISUAIS", style_sub),
        Paragraph(f"Ficha Cadastral de Cliente: {cliente_data.get('Empresa', '')}", style_tit),
        Spacer(1, 12)
    ]

    info_table = [
        [Paragraph("<b>Empresa:</b>", style_td), Paragraph(str(cliente_data.get('Empresa', '')), style_td)],
        [Paragraph("<b>Pessoa de Contato:</b>", style_td), Paragraph(str(cliente_data.get('Contato', '')), style_td)],
        [Paragraph("<b>Cidade / Local:</b>", style_td), Paragraph(str(cliente_data.get('Cidade', '')), style_td)],
        [Paragraph("<b>Telefone / WhatsApp:</b>", style_td), Paragraph(str(cliente_data.get('Telefone', '')), style_td)],
        [Paragraph("<b>Email:</b>", style_td), Paragraph(str(cliente_data.get('Email', '')), style_td)],
        [Paragraph("<b>Categoria / TAG:</b>", style_td), Paragraph(str(cliente_data.get('Categoria / TAG', '')), style_td)]
    ]
    t_info = Table(info_table, colWidths=[140, 380])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Histórico de Pedidos e Propostas Emitidas", style_sub))
    story.append(Spacer(1, 6))

    if not pedidos_cli.empty:
        p_table = [[Paragraph("<b>Nº Pedido</b>", style_td), Paragraph("<b>Data Emissao</b>", style_td), Paragraph("<b>Valor Total</b>", style_td), Paragraph("<b>Status</b>", style_td)]]
        for _, p in pedidos_cli.iterrows():
            p_table.append([
                Paragraph(str(p.get('Numero_Pedido', '')), style_td),
                Paragraph(str(p.get('Data_Emissao', '')), style_td),
                Paragraph(f"R$ {float(p.get('Valor_Total', 0)):,.2f}", style_td),
                Paragraph(str(p.get('Status', '')), style_td)
            ])
        t_ped = Table(p_table, colWidths=[120, 120, 130, 150])
        t_ped.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_ped)
    else:
        story.append(Paragraph("Nenhum pedido registrado para este cliente até o momento.", style_td))

    doc.build(story, canvasmaker=CanvasExecutivoAlinhado)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 6. DASHBOARD & ABAS PRINCIPAIS
# -----------------------------------------------------------------------------
st.title("💼 CRM Okamoto Mídias Visuais")

k1, k2, k3, k4 = st.columns(4)
k1.metric("🏢 Base de Clientes", f"{len(df_clientes)}")
k2.metric("📄 Propostas Emitidas", f"{len(df_pedidos)}")
k3.metric("💰 Volume em Negociação", f"R$ {df_pedidos['Valor_Total'].astype(float).sum():,.2f}" if not df_pedidos.empty else "R$ 0,00")
k4.metric("🛠️ Serviços Ativos", f"{len(df_servicos)}")

st.markdown("---")

aba_orcamento, aba_kanban, aba_clientes, aba_catalogo = st.tabs([
    "📄 Gerar Orçamento / Pedido",
    "📊 Funil de Vendas",
    "🏢 Gestão de Clientes",
    "🛠️ Catálogo de Serviços"
])

# ABA 1: GERAR / CARREGAR ORÇAMENTO EXISTENTE
with aba_orcamento:
    st.subheader("📄 Visualização e Emissão de Propostas Comerciais")
    
    opcoes_pedidos = ["➕ Criar Novo Pedido do Zero"] + [f"{p['Numero_Pedido']} - {p['Empresa']} ({p['Contato']})" for _, p in df_pedidos.iterrows()]
    pedido_selecionado = st.selectbox("📌 Selecione um Pedido / Orçamento Existente para Carregar:", opcoes_pedidos)
    
    val_num_ped = f"Pedido {len(df_pedidos)+1:04d}"
    val_empresa = "Clínica Personalitté"
    val_contato = "Joseph"
    val_tel = "(16) 99767-8802"
    val_local = "Ribeirão Preto - SP"
    val_data_emissao = "08 de Setembro de 2026"
    val_nome_evento = "2º Encontro Internacional Técnico GS Inima Brasil"
    val_data_evento_det = "Dias 04 e 05/11/2026, das 8h00 as 17h00"
    val_objetivo = "Cobertura fotográfica do evento\n• Captação de vídeo em Full HD\n• Período das 08h00 as 18h00\nIntervalo de 1h30 de almoço"
    val_captacao = "Registros fotográficos e captações pontuais em vídeo (participantes, autoridades, apresentações, intervalos, entre outros momentos do evento)."
    val_entrega = "Todo material fotográfico será editado e enviado, em alta e baixa resolução.\n• Todo material em vídeo será enviado bruto (sem edição).\nOs materiais serão enviados via link e ficará disponível pelo prazo de 30 dias para download."
    val_prazo = "Até 72h após o término do evento."
    val_servicos_sel = [df_servicos["Nome_Servico"].iloc[0]]
    val_subtotal = 3700.0
    val_desconto_pct = 0.0
    val_total = 3700.0
    val_extenso = converter_valor_extenso(3700.0)
    val_cond_pag = "Até 20 dias após o evento."
    val_status = "Orçamento / Proposta"

    if pedido_selecionado != "➕ Criar Novo Pedido do Zero":
        num_p_extraido = pedido_selecionado.split(" - ")[0]
        p_match = df_pedidos[df_pedidos["Numero_Pedido"] == num_p_extraido]
        if not p_match.empty:
            p_data = p_match.iloc[0]
            val_num_ped = str(p_data.get("Numero_Pedido", ""))
            val_empresa = str(p_data.get("Empresa", ""))
            val_contato = str(p_data.get("Contato", ""))
            val_tel = str(p_data.get("Telefone", ""))
            val_local = str(p_data.get("Local", ""))
            val_data_emissao = str(p_data.get("Data_Emissao", ""))
            val_nome_evento = str(p_data.get("Nome_Evento", ""))
            val_data_evento_det = str(p_data.get("Data_Evento_Detalhada", ""))
            val_objetivo = str(p_data.get("Objetivo", ""))
            val_captacao = str(p_data.get("Captacao", ""))
            val_entrega = str(p_data.get("Entrega", ""))
            val_prazo = str(p_data.get("Prazo_Entrega", ""))
            val_subtotal = float(p_data.get("Valor_Subtotal", 3700.0))
            val_desconto_pct = float(p_data.get("Desconto_Pct", 0.0))
            val_total = float(p_data.get("Valor_Total", 3700.0))
            val_extenso = str(p_data.get("Valor_Extenso", converter_valor_extenso(val_total)))
            val_cond_pag = str(p_data.get("Condicoes_Pag", ""))
            val_status = str(p_data.get("Status", "Orçamento / Proposta"))
            
            srv_str = str(p_data.get("Servicos", ""))
            val_servicos_sel = [s.strip() for s in srv_str.split(",") if s.strip() in df_servicos["Nome_Servico"].tolist()]
            if not val_servicos_sel:
                val_servicos_sel = [df_servicos["Nome_Servico"].iloc[0]]

    c1, c2 = st.columns(2)
    with c1:
        num_pedido = st.text_input("Número do Pedido/Proposta:", value=val_num_ped)
        lista_cli_dropdown = ["Digitado Manualmente"] + df_clientes["Empresa"].tolist()
        cli_sel_box = st.selectbox("Buscar Dados do Cliente Cadastrado:", lista_cli_dropdown)
        if cli_sel_box != "Digitado Manualmente":
            match_c = df_clientes[df_clientes["Empresa"] == cli_sel_box].iloc[0]
            val_empresa = match_c["Empresa"]
            val_contato = match_c["Contato"]
            val_tel = match_c["Telefone"]
            val_local = match_c["Cidade"]

        empresa_sel = st.text_input("Empresa:", value=val_empresa)
        contato = st.text_input("Contato:", value=val_contato)
        tel_cli = st.text_input("Telefone:", value=val_tel)
        local_cli = st.text_input("Local do Evento:", value=val_local)

    with c2:
        data_orcamento = st.text_input("Data de Emissão:", value=val_data_emissao)
        status_sel = st.selectbox("Status do Pedido (Funil de Vendas):", ["Orçamento / Proposta", "Em atendimento", "Negociação/Revisão", "Aprovado", "Produção", "Concluído", "Cancelado"], index=["Orçamento / Proposta", "Em atendimento", "Negociação/Revisão", "Aprovado", "Produção", "Concluído", "Cancelado"].index(val_status) if val_status in ["Orçamento / Proposta", "Em atendimento", "Negociação/Revisão", "Aprovado", "Produção", "Concluído", "Cancelado"] else 0)
        condicoes_pag = st.text_input("6. Forma de Pagamento:", value=val_cond_pag)
        prazo_entrega = st.text_input("5. Prazo de Entrega:", value=val_prazo)

    st.markdown("---")
    st.markdown("### 📝 ESCOPO DO SERVIÇO (DETALHAMENTO TÉCNICO)")
    
    col_e1, col_e2 = st.columns(2)
    nome_evento = col_e1.text_input("1. Nome do Evento:", value=val_nome_evento)
    data_evento_detalhada = col_e2.text_input("1. Datas e Horários do Evento:", value=val_data_evento_det)
    
    objetivo_txt = st.text_area("2. Objetivo:", value=val_objetivo, height=160)
    captacao_txt = st.text_area("3. Captação:", value=val_captacao, height=160)
    entrega_txt = st.text_area("4. Entrega:", value=val_entrega, height=180)

    st.markdown("---")
    st.markdown("### 💰 INVESTIMENTO & APRESENTAÇÃO INSTITUCIONAL")
    
    servicos_solicitados = st.multiselect("Selecione os Serviços do Catálogo para o Cálculo:", df_servicos["Nome_Servico"].tolist(), default=val_servicos_sel)
    
    subtotal_calculado_srv = 0.0
    for s_nome in servicos_solicitados:
        row_s = df_servicos[df_servicos["Nome_Servico"] == s_nome].iloc[0]
        subtotal_calculado_srv += float(row_s["Valor_Base"])

    if subtotal_calculado_srv == 0.0:
        subtotal_calculado_srv = val_subtotal

    ci1, ci2, ci3 = st.columns([1.5, 1, 1.5])
    subtotal_input = ci1.number_input("Subtotal dos Serviços (R$):", value=float(subtotal_calculado_srv), step=100.0)
    desconto_pct_input = ci2.number_input("Desconto (%):", value=float(val_desconto_pct), min_value=0.0, max_value=100.0, step=5.0)
    
    valor_final_com_desc = max(0.0, subtotal_input * (1.0 - (desconto_pct_input / 100.0)))
    ci3.metric("Valor Total com Desconto", f"R$ {valor_final_com_desc:,.2f}")

    valor_extenso_auto = converter_valor_extenso(valor_final_com_desc)
    valor_extenso = st.text_input("Valor por Extenso (Gerado Automático):", value=valor_extenso_auto)

    st.session_state['texto_institucional'] = st.text_area(
        "Apresentação Institucional da Empresa (exibida na Página 1 do PDF):",
        value=st.session_state['texto_institucional'],
        height=220
    )

    dados_pdf = {
        "num_pedido": num_pedido,
        "empresa": empresa_sel,
        "contato": contato,
        "telefone_cli": tel_cli,
        "local": local_cli,
        "data_orcamento": data_orcamento,
        "nome_evento": nome_evento,
        "data_evento_detalhada": data_evento_detalhada,
        "objetivo": objetivo_txt,
        "captacao": captacao_txt,
        "entrega": entrega_txt,
        "prazo_entrega": prazo_entrega,
        "valor_total": valor_final_com_desc,
        "valor_extenso": valor_extenso,
        "condicoes_pag": condicoes_pag
    }
    
    pdf_bytes = gerar_pdf_3_paginas_corrigido(dados_pdf, st.session_state['texto_institucional'])

    st.markdown("---")
    cb1, cb2 = st.columns(2)
    with cb1:
        st.download_button("📥 Baixar PDF da Proposta Comercial (3 Páginas)", data=pdf_bytes, file_name=f"Proposta_{num_pedido}.pdf", mime="application/pdf", use_container_width=True)
    with cb2:
        if st.button("💾 Salvar / Atualizar Pedido no CRM", use_container_width=True):
            idx_existente = df_pedidos[df_pedidos["Numero_Pedido"] == num_pedido].index
            novo_d = {
                "Numero_Pedido": num_pedido,
                "Empresa": empresa_sel,
                "Contato": contato,
                "Telefone": tel_cli,
                "Local": local_cli,
                "Data_Emissao": data_orcamento,
                "Data_Evento": data_orcamento,
                "Nome_Evento": nome_evento,
                "Data_Evento_Detalhada": data_evento_detalhada,
                "Objetivo": objetivo_txt,
                "Captacao": captacao_txt,
                "Entrega": entrega_txt,
                "Prazo_Entrega": prazo_entrega,
                "Valor_Subtotal": subtotal_input,
                "Desconto_Pct": desconto_pct_input,
                "Valor_Total": valor_final_com_desc,
                "Valor_Extenso": valor_extenso,
                "Condicoes_Pag": condicoes_pag,
                "Status": status_sel,
                "Servicos": ", ".join(servicos_solicitados) if servicos_solicitados else "Serviço Personalizado"
            }
            if not idx_existente.empty:
                for k, v in novo_d.items():
                    st.session_state['df_pedidos'].loc[idx_existente[0], k] = v
                st.success(f"Pedido {num_pedido} atualizado no CRM e Funil de Vendas!")
            else:
                st.session_state['df_pedidos'] = pd.concat([st.session_state['df_pedidos'], pd.DataFrame([novo_d])], ignore_index=True)
                st.success(f"Novo pedido {num_pedido} registrado no CRM!")
            st.rerun()

# ABA 2: FUNIL KANBAN
with aba_kanban:
    st.subheader("📊 Estágios do Atendimento Comercial (Funil de Vendas)")
    fases = ["Orçamento / Proposta", "Em atendimento", "Negociação/Revisão", "Aprovado", "Produção", "Concluído", "Cancelado"]
    cols = st.columns(len(fases))
    
    for idx, fase in enumerate(fases):
        with cols[idx]:
            st.markdown(f"**{fase}**")
            p_fase = df_pedidos[df_pedidos["Status"] == fase] if not df_pedidos.empty else pd.DataFrame()
            st.caption(f"{len(p_fase)} Item(ns)")
            
            if not p_fase.empty:
                for _, p in p_fase.iterrows():
                    st.markdown(f"""
                    <div class="card-kanban">
                        <b>{p['Numero_Pedido']}</b><br/>
                        <span>{p['Empresa'][:20]}</span><br/>
                        <b style="color: #38bdf8;">R$ {float(p['Valor_Total']):,.2f}</b><br/>
                        <span style="color:#94a3b8; font-size:10px;">📅 {p['Data_Emissao']}</span>
                    </div>
                    """, unsafe_allow_html=True)

# ABA 3: GESTÃO DE CLIENTES
with aba_clientes:
    st.subheader("🏢 Cadastrar / Consultar Cliente Individual")
    
    with st.expander("➕ Formulário para Cadastrar Novo Cliente"):
        with st.form("form_novo_cliente", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            n_empresa = c1.text_input("Empresa:")
            n_contato = c2.text_input("Contato:")
            n_cidade = c3.text_input("Cidade:")
            
            c4, c5, c6 = st.columns(3)
            n_tel = c4.text_input("Telefone:")
            n_email = c5.text_input("Email:")
            n_cat = c6.selectbox("Categoria / TAG:", LISTA_TAGS)
            
            c7, c8, c9 = st.columns(3)
            n_atividade = c7.text_input("Atividade / Ramo de Atuação:", placeholder="Ex: Estética, Hotelaria, Engenharia")
            n_site = c8.text_input("Website Oficial:", placeholder="www.suaempresa.com.br")
            n_insta = c9.text_input("Instagram:", placeholder="@seuinstagram")
            
            if st.form_submit_button("➕ Salvar Cliente"):
                if n_empresa:
                    novo_c = pd.DataFrame([{
                        "Empresa": n_empresa, "Contato": n_contato, "Cidade": n_cidade, 
                        "Telefone": n_tel, "Email": n_email, "Categoria / TAG": n_cat,
                        "Atividade": n_atividade, "Website": n_site, "Instagram": n_insta
                    }])
                    st.session_state['df_clientes'] = pd.concat([st.session_state['df_clientes'], novo_c], ignore_index=True)
                    st.success(f"Cliente {n_empresa} cadastrado!")
                    st.rerun()

    st.markdown("---")
    st.subheader("🔍 Base de Clientes Cadastrados & Acesso Individual")
    
    col_f1, col_f2 = st.columns([2, 1])
    termo = col_f1.text_input("Pesquisar Cliente por Nome, Atividade, Cidade ou Contato:")
    tag_filtro = col_f2.selectbox("Filtrar por Categoria / TAG:", ["TODAS"] + LISTA_TAGS)
    
    df_c_exibir = st.session_state['df_clientes'].copy()
    if tag_filtro != "TODAS":
        df_c_exibir = df_c_exibir[df_c_exibir["Categoria / TAG"] == tag_filtro]
    if termo:
        mask = df_c_exibir.astype(str).apply(lambda row: row.str.contains(termo, case=False).any(), axis=1)
        df_c_exibir = df_c_exibir[mask]
        
    st.dataframe(df_c_exibir, use_container_width=True)

    if not df_c_exibir.empty:
        st.markdown("---")
        st.markdown("### 📄 Visualizar Ficha Individual do Cliente")
        cli_selecionado = st.selectbox("Selecione uma empresa para abrir a ficha:", df_c_exibir["Empresa"].tolist())
        
        c_dados = df_c_exibir[df_c_exibir["Empresa"] == cli_selecionado].iloc[0]
        pedidos_cliente = df_pedidos[df_pedidos["Empresa"] == cli_selecionado] if not df_pedidos.empty else pd.DataFrame()

        box1, box2 = st.columns([2, 1])
        with box1:
            st.markdown(f"**Empresa:** {c_dados.get('Empresa')}")
            st.markdown(f"**Atividade:** {c_dados.get('Atividade', 'N/I')}")
            st.markdown(f"**Contato:** {c_dados.get('Contato')} | **Telefone:** {c_dados.get('Telefone')}")
            st.markdown(f"**Cidade:** {c_dados.get('Cidade')} | **TAG:** `{c_dados.get('Categoria / TAG')}`")
            st.markdown(f"**Email:** {c_dados.get('Email')}")
            st.markdown(f"**Website:** {c_dados.get('Website', 'N/I')} | **Instagram:** {c_dados.get('Instagram', 'N/I')}")

        with box2:
            st.metric("Pedidos do Cliente", f"{len(pedidos_cliente)}")
            pdf_ficha_bytes = gerar_pdf_ficha_cliente(c_dados, pedidos_cliente)
            st.download_button(
                "📥 Baixar Ficha do Cliente em PDF",
                data=pdf_ficha_bytes,
                file_name=f"Ficha_{cli_selecionado.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# ABA 4: CATÁLOGO DE SERVIÇOS
with aba_catalogo:
    st.subheader("🛠️ Gestão do Catálogo de Serviços")
    modo_acao = st.radio("Selecione a ação:", ["➕ Adicionar Novo Serviço", "✏️ Editar Serviço Existente", "❌ Excluir Serviço"], horizontal=True)
    
    if modo_acao == "➕ Adicionar Novo Serviço":
        with st.form("form_novo_servico", clear_on_submit=True):
            cs1, cs2, cs3 = st.columns([2, 1, 1])
            s_nome = cs1.text_input("Nome do Serviço:")
            s_tipo = cs2.selectbox("Tipo de Cobrança:", ["Hora", "Pacote", "Diária", "Unidade", "Mensal"])
            s_valor = cs3.number_input("Valor Base (R$):", min_value=0.0, step=50.0)
            s_desc = st.text_area("Descrição do Serviço:")
            if st.form_submit_button("➕ Salvar Serviço"):
                if s_nome:
                    novo_s = pd.DataFrame([{"Nome_Servico": s_nome, "Tipo_Cobranca": s_tipo, "Valor_Base": s_valor, "Descricao": s_desc}])
                    st.session_state['df_servicos'] = pd.concat([st.session_state['df_servicos'], novo_s], ignore_index=True)
                    st.success("Serviço adicionado!")
                    st.rerun()

    elif modo_acao == "✏️ Editar Serviço Existente":
        lista_s = st.session_state['df_servicos']["Nome_Servico"].tolist()
        if lista_s:
            servico_edit_sel = st.selectbox("Selecione o serviço para editar:", lista_s)
            idx_s = st.session_state['df_servicos'][st.session_state['df_servicos']["Nome_Servico"] == servico_edit_sel].index[0]
            dados_s = st.session_state['df_servicos'].loc[idx_s]
            
            with st.form("form_edit_servico"):
                ce1, ce2, ce3 = st.columns([2, 1, 1])
                e_nome = ce1.text_input("Nome:", value=dados_s["Nome_Servico"])
                e_tipo = ce2.selectbox("Tipo:", ["Hora", "Pacote", "Diária", "Unidade", "Mensal"], index=["Hora", "Pacote", "Diária", "Unidade", "Mensal"].index(dados_s["Tipo_Cobranca"]) if dados_s["Tipo_Cobranca"] in ["Hora", "Pacote", "Diária", "Unidade", "Mensal"] else 0)
                e_valor = ce3.number_input("Valor (R$):", value=float(dados_s["Valor_Base"]))
                e_desc = st.text_area("Descrição:", value=dados_s["Descricao"])
                
                if st.form_submit_button("💾 Salvar Alterações"):
                    st.session_state['df_servicos'].loc[idx_s, "Nome_Servico"] = e_nome
                    st.session_state['df_servicos'].loc[idx_s, "Tipo_Cobranca"] = e_tipo
                    st.session_state['df_servicos'].loc[idx_s, "Valor_Base"] = e_valor
                    st.session_state['df_servicos'].loc[idx_s, "Descricao"] = e_desc
                    st.success("Serviço atualizado com sucesso!")
                    st.rerun()

    elif modo_acao == "❌ Excluir Serviço":
        lista_s = st.session_state['df_servicos']["Nome_Servico"].tolist()
        if lista_s:
            servico_del = st.selectbox("Selecione o serviço para remover:", lista_s)
            if st.button("🚨 Confirmar Exclusão do Serviço", use_container_width=True):
                st.session_state['df_servicos'] = st.session_state['df_servicos'][st.session_state['df_servicos']["Nome_Servico"] != servico_del].reset_index(drop=True)
                st.success("Serviço removido!")
                st.rerun()

    st.markdown("---")
    st.subheader("Catálogo Ativo de Serviços")
    st.dataframe(st.session_state['df_servicos'], use_container_width=True)

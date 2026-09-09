import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS
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
            "Numero_Pedido": "Pedido 0001",
            "Empresa": "Clínica Personalitté",
            "Contato": "Joseph",
            "Telefone": "+55 (16) 99767-8802",
            "Data_Emissao": "09/09/2026",
            "Data_Evento": "09/09/2026",
            "Periodo_Servico": "2 horas e 30 minutos",
            "Forma_Entrega": "Link exclusivo Google Drive e plataforma web",
            "Prazo_Entrega": "Até 72 horas após a execução do serviço",
            "Valor_Total": 440.0,
            "Desconto_Pct": 20.0,
            "Status": "Orçamento / Proposta",
            "Servicos": "Cobertura fotográfica",
            "Condicoes_Pag": "Parcelas: 2",
            "Info_Adicionais": "• Captação;\n• Edição;\n• Envio de imagens em alta resolução."
        }
    ])

if 'df_clientes' not in st.session_state:
    st.session_state['df_clientes'] = pd.DataFrame([
        {"Empresa": "Clínica Personalitté", "Contato": "Joseph", "Cidade": "Ribeirão Preto - SP", "Telefone": "+55 (16) 99767-8802", "Email": "joseph@personalitte.com.br", "Categoria / TAG": "CLÍNICAS"},
        {"Empresa": "Taiwan Hotel Ltda", "Contato": "Gerência", "Cidade": "Ribeirão Preto - SP", "Telefone": "(16) 3900-0000", "Email": "reservas@taiwanhotel.com.br", "Categoria / TAG": "HOTELARIA"}
    ])

if 'df_servicos' not in st.session_state:
    st.session_state['df_servicos'] = pd.DataFrame([
        {"Nome_Servico": "Cobertura fotográfica", "Tipo_Cobranca": "Hora", "Valor_Base": 180.0, "Descricao": "Registros fotográficos de alta resolução com edição de cores."},
        {"Nome_Servico": "Captação de vídeo", "Tipo_Cobranca": "Hora", "Valor_Base": 200.0, "Descricao": "Gravação em Full HD/4K (material bruto entregue via link)."},
        {"Nome_Servico": "Google Street View", "Tipo_Cobranca": "Pacote", "Valor_Base": 560.0, "Descricao": "Envio de 06 imagens 360° para o perfil do Google."},
        {"Nome_Servico": "Tour Virtual 360°", "Tipo_Cobranca": "Pacote", "Valor_Base": 800.0, "Descricao": "Mapeamento completo e publicação em ambiente web."}
    ])

df_pedidos = st.session_state['df_pedidos']
df_clientes = st.session_state['df_clientes']
df_servicos = st.session_state['df_servicos']

# -----------------------------------------------------------------------------
# 5. GERADOR DE PDF DA PROPOSTA COMERCIAL
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
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(555, 20, f"Página {self._pageNumber}/{num_pages}")
            self.restoreState()
            super().showPage()
        super().save()

def gerar_pdf_layout_oficial(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=30, bottomMargin=35)
    styles = getSampleStyleSheet()
    
    style_tit_empresa = ParagraphStyle('TitEmp', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor('#0f172a'))
    style_sub_empresa = ParagraphStyle('SubEmp', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#475569'))
    style_tit_proposta = ParagraphStyle('TitProp', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=colors.HexColor('#0284c7'))
    style_cliente = ParagraphStyle('Cli', fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#334155'))
    style_th = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor('#0f172a'))
    style_td = ParagraphStyle('TD', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#334155'))
    style_sec = ParagraphStyle('Sec', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=colors.HexColor('#0284c7'))

    story = []

    col_esquerda = []
    if st.session_state.get('logo_bytes'):
        try:
            img_buf = io.BytesIO(st.session_state['logo_bytes'])
            col_esquerda.append(Image(img_buf, width=70, height=70))
            col_esquerda.append(Spacer(1, 4))
        except Exception:
            pass
            
    col_esquerda.extend([
        Paragraph("<b>OKAMOTO REPORTAGENS FOTOGRAFICAS S/S LTDA</b>", style_tit_empresa),
        Paragraph("CNPJ: 04.824.331/0001-05<br/>contato@tour360vr.com.br<br/>+55 (16) 99133-2121<br/>+55 (16) 99622-2121<br/><i>A mais nova forma de ver o mundo</i>", style_sub_empresa)
    ])

    col_direita = [
        Paragraph(f"Proposta comercial {dados['num_pedido']}", style_tit_proposta),
        Spacer(1, 6),
        Paragraph(f"<b>{dados['empresa']}</b><br/>Cliente: {dados['contato']}<br/>{dados.get('telefone_cli', '')}", style_cliente)
    ]

    t_header = Table([[col_esquerda, col_direita]], colWidths=[270, 250])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 15))

    srv_table_data = [[Paragraph("Serviços", style_th), Paragraph("Descrição / Escopo", style_th), Paragraph("Detalhes", style_th)]]
    for item in dados['itens']:
        srv_table_data.append([
            Paragraph(f"<b>{item['nome']}</b>", style_td),
            Paragraph(item.get('desc', ''), style_td),
            Paragraph(f"Período: {dados.get('periodo_servico', 'Atendimento Padrão')}", style_td)
        ])
    
    if dados.get('desconto_pct', 0) > 0:
        srv_table_data.append([
            Paragraph("<b>Desconto Aplicado</b>", style_td),
            "",
            Paragraph(f"- {dados['desconto_pct']:.0f}%", style_td)
        ])

    srv_table_data.append([
        Paragraph("<b>Total Final</b>", style_th),
        "",
        Paragraph(f"<b>R$ {dados['valor_final']:,.2f}</b>", style_th)
    ])

    t_servicos = Table(srv_table_data, colWidths=[160, 240, 120])
    t_servicos.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor('#0284c7')),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#cbd5e1')),
        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#0f172a')),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_servicos)
    story.append(Spacer(1, 12))

    col_pagamento = [
        Paragraph("Pagamento", style_sec),
        Spacer(1, 3),
        Paragraph("<b>Meios de pagamento</b><br/>Transferência bancária, cartão de crédito ou pix.", style_td),
        Spacer(1, 4),
        Paragraph("<b>Dados bancários</b><br/>Banco: Banco do Brasil<br/>Agência: 3235-2 | Conta: 11935-0 (Corrente)<br/>Titular: 04.824.331/0001-05", style_td),
        Spacer(1, 4),
        Paragraph(f"<b>PIX:</b> 04824331000105<br/><b>Condições:</b> {dados.get('condicoes_pag', 'Parcelas: 2')}", style_td)
    ]

    col_info = [
        Paragraph("Entrega e Informações Adicionais", style_sec),
        Spacer(1, 3),
        Paragraph(f"<b>Forma de Entrega:</b> {dados.get('forma_entrega', 'Link exclusivo')}", style_td),
        Paragraph(f"<b>Prazo de Entrega:</b> {dados.get('prazo_entrega', 'Até 72h')}", style_td),
        Spacer(1, 4),
        Paragraph("<b>Observações:</b>", style_td),
        Paragraph(dados.get('info_adicionais', '').replace('\n', '<br/>'), style_td)
    ]

    t_rodape = Table([[col_pagamento, col_info]], colWidths=[260, 260])
    t_rodape.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_rodape)
    story.append(Spacer(1, 20))

    ass_data = [
        [
            Paragraph("___________________________________<br/><b>Rubens Okamoto</b><br/>Tour360VR", style_td),
            Paragraph(f"___________________________________<br/><b>{dados['contato']}</b><br/>Data: {dados['data_orcamento']}", style_td)
        ]
    ]
    t_ass = Table(ass_data, colWidths=[260, 260])
    t_ass.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(t_ass)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

def gerar_pdf_ficha_cliente(cliente_data, pedidos_cli):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=30, bottomMargin=35)
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

    doc.build(story)
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
    
    # VALORES PADRÃO INICIAIS
    val_num_ped = f"Pedido {len(df_pedidos)+1:04d}"
    val_empresa = "Clínica Personalitté"
    val_contato = "Joseph"
    val_tel = "+55 (16) 99767-8802"
    val_data_emissao = datetime.now()
    val_servicos_sel = [df_servicos["Nome_Servico"].iloc[0]]
    val_status = "Orçamento / Proposta"
    val_cond_pag = "Parcelas: 2"
    val_info_adj = "• Captação;\n• Edição;\n• Envio de imagens em alta resolução."
    val_forma_entrega = "Link exclusivo Google Drive e plataforma web"
    val_prazo_entrega = "Até 72 horas após a execução do serviço"
    val_horas = 2
    val_minutos = 30
    val_desconto = 20.0

    if pedido_selecionado != "➕ Criar Novo Pedido do Zero":
        num_p_extraido = pedido_selecionado.split(" - ")[0]
        p_match = df_pedidos[df_pedidos["Numero_Pedido"] == num_p_extraido]
        if not p_match.empty:
            p_data = p_match.iloc[0]
            val_num_ped = str(p_data.get("Numero_Pedido", ""))
            val_empresa = str(p_data.get("Empresa", ""))
            val_contato = str(p_data.get("Contato", ""))
            val_tel = str(p_data.get("Telefone", ""))
            val_status = str(p_data.get("Status", "Orçamento / Proposta"))
            val_cond_pag = str(p_data.get("Condicoes_Pag", "Parcelas: 2"))
            val_info_adj = str(p_data.get("Info_Adicionais", ""))
            val_forma_entrega = str(p_data.get("Forma_Entrega", val_forma_entrega))
            val_prazo_entrega = str(p_data.get("Prazo_Entrega", val_prazo_entrega))
            val_desconto = float(p_data.get("Desconto_Pct", 0.0))
            
            srv_str = str(p_data.get("Servicos", ""))
            val_servicos_sel = [s.strip() for s in srv_str.split(",") if s.strip() in df_servicos["Nome_Servico"].tolist()]
            if not val_servicos_sel:
                val_servicos_sel = [df_servicos["Nome_Servico"].iloc[0]]

    col1, col2 = st.columns(2)
    with col1:
        num_pedido = st.text_input("Número do Pedido/Proposta", value=val_num_ped)
        empresa_sel = st.text_input("Empresa / Cliente", value=val_empresa)
        contato = st.text_input("Pessoa de Contato", value=val_contato)
        tel_cli = st.text_input("Telefone do Cliente", value=val_tel)
        data_orcamento = st.date_input("Data de Emissão", value=val_data_emissao).strftime('%d/%m/%Y')

    with col2:
        servicos_sel = st.multiselect("Serviços Solicitados", df_servicos["Nome_Servico"].tolist(), default=val_servicos_sel)
        status_sel = st.selectbox("Status do Pedido", ["Orçamento / Proposta", "Em atendimento", "Negociação/Revisão", "Aprovado", "Produção", "Concluído"], index=0)
        condicoes_pag = st.text_input("Condições de Pagamento", value=val_cond_pag)

    st.markdown("---")
    st.markdown("### ⏱️ Período do Serviço & Cálculo de Valores")
    
    cp1, cp2, cp3, cp4 = st.columns(4)
    qtd_horas = cp1.number_input("Horas de Serviço:", min_value=0, max_value=24, value=val_horas, step=1)
    qtd_minutos = cp2.selectbox("Minutos:", [0, 15, 30, 45], index=[0, 15, 30, 45].index(val_minutos) if val_minutos in [0, 15, 30, 45] else 2)
    pct_desconto = cp3.number_input("Desconto (%):", min_value=0.0, max_value=100.0, value=val_desconto, step=5.0)
    
    # CÁLCULO AUTOMÁTICO DE VALOR COM BASE NAS HORAS
    tempo_total_horas = qtd_horas + (qtd_minutos / 60.0)
    valor_hora_base = 180.0
    
    if servicos_sel:
        r_primeiro = df_servicos[df_servicos["Nome_Servico"] == servicos_sel[0]].iloc[0]
        if str(r_primeiro.get("Tipo_Cobranca", "")).lower() == "hora":
            valor_hora_base = float(r_primeiro.get("Valor_Base", 180.0))

    subtotal_calculado = tempo_total_horas * valor_hora_base if tempo_total_horas > 0 else valor_hora_base
    valor_desconto = subtotal_calculado * (pct_desconto / 100.0)
    valor_final_calculado = max(0.0, subtotal_calculado - valor_desconto)
    
    cp4.metric("Valor Final Calculado", f"R$ {valor_final_calculado:,.2f}", delta=f"- R$ {valor_desconto:,.2f}" if pct_desconto > 0 else None)

    str_periodo = f"{qtd_horas}h" + (f"{qtd_minutos}min" if qtd_minutos > 0 else "")

    st.markdown("---")
    st.markdown("### 📦 Condições de Entrega & Observações")
    ce1, ce2 = st.columns(2)
    forma_entrega = ce1.text_input("Forma de Entrega:", value=val_forma_entrega)
    prazo_entrega = ce2.text_input("Prazo de Entrega:", value=val_prazo_entrega)
    info_adicionais = st.text_area("Informações Adicionais", value=val_info_adj, height=100)

    itens_detalhados = []
    for s in servicos_sel:
        r = df_servicos[df_servicos["Nome_Servico"] == s].iloc[0]
        v = float(r["Valor_Base"])
        itens_detalhados.append({"nome": s, "desc": str(r.get("Descricao", "")), "valor": v})

    dados_pdf = {
        "num_pedido": num_pedido,
        "empresa": empresa_sel,
        "contato": contato,
        "telefone_cli": tel_cli,
        "data_orcamento": data_orcamento,
        "condicoes_pag": condicoes_pag,
        "periodo_servico": str_periodo,
        "forma_entrega": forma_entrega,
        "prazo_entrega": prazo_entrega,
        "info_adicionais": info_adicionais,
        "desconto_pct": pct_desconto,
        "itens": itens_detalhados,
        "valor_final": valor_final_calculado
    }
    
    pdf_bytes = gerar_pdf_layout_oficial(dados_pdf)

    st.markdown("---")
    cb1, cb2 = st.columns(2)
    with cb1:
        st.download_button("📥 Baixar PDF da Proposta Comercial", data=pdf_bytes, file_name=f"Proposta_{num_pedido}.pdf", mime="application/pdf", use_container_width=True)
    with cb2:
        if st.button("💾 Salvar / Atualizar Pedido no CRM", use_container_width=True):
            idx_existente = df_pedidos[df_pedidos["Numero_Pedido"] == num_pedido].index
            novo_d = {
                "Numero_Pedido": num_pedido,
                "Empresa": empresa_sel,
                "Contato": contato,
                "Telefone": tel_cli,
                "Data_Emissao": data_orcamento,
                "Data_Evento": data_orcamento,
                "Periodo_Servico": str_periodo,
                "Forma_Entrega": forma_entrega,
                "Prazo_Entrega": prazo_entrega,
                "Valor_Total": valor_final_calculado,
                "Desconto_Pct": pct_desconto,
                "Status": status_sel,
                "Servicos": ", ".join(servicos_sel),
                "Condicoes_Pag": condicoes_pag,
                "Info_Adicionais": info_adicionais
            }
            if not idx_existente.empty:
                for k, v in novo_d.items():
                    st.session_state['df_pedidos'].loc[idx_existente[0], k] = v
                st.success(f"Pedido {num_pedido} atualizado com sucesso!")
            else:
                st.session_state['df_pedidos'] = pd.concat([st.session_state['df_pedidos'], pd.DataFrame([novo_d])], ignore_index=True)
                st.success(f"Novo pedido {num_pedido} salvo com sucesso!")
            st.rerun()

# ABA 2: FUNIL KANBAN
with aba_kanban:
    st.subheader("Estágios do Atendimento Comercial")
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
                        <b>{p['Empresa'][:18]}</b><br/>
                        R$ {float(p['Valor_Total']):,.2f}<br/>
                        <span style="color:#94a3b8;">📅 {p['Data_Emissao']}</span>
                    </div>
                    """, unsafe_allow_html=True)

# ABA 3: GESTÃO DE CLIENTES (ACESSO E PDF INDIVIDUAL)
with aba_clientes:
    st.subheader("🏢 Cadastrar / Consultar Cliente Individual")
    
    with st.expander("➕ Formulario para Cadastrar Novo Cliente"):
        with st.form("form_novo_cliente", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            n_empresa = c1.text_input("Empresa:")
            n_contato = c2.text_input("Contato:")
            n_cidade = c3.text_input("Cidade:")
            c4, c5, c6 = st.columns(3)
            n_tel = c4.text_input("Telefone:")
            n_email = c5.text_input("Email:")
            n_cat = c6.selectbox("Categoria / TAG:", LISTA_TAGS)
            if st.form_submit_button("➕ Salvar Cliente"):
                if n_empresa:
                    novo_c = pd.DataFrame([{"Empresa": n_empresa, "Contato": n_contato, "Cidade": n_cidade, "Telefone": n_tel, "Email": n_email, "Categoria / TAG": n_cat}])
                    st.session_state['df_clientes'] = pd.concat([st.session_state['df_clientes'], novo_c], ignore_index=True)
                    st.success(f"Cliente {n_empresa} cadastrado!")
                    st.rerun()

    st.markdown("---")
    st.subheader("🔍 Base de Clientes Cadastrados & Acesso Individual")
    
    col_f1, col_f2 = st.columns([2, 1])
    termo = col_f1.text_input("Pesquisar Cliente:")
    tag_filtro = col_f2.selectbox("Filtrar por Categoria / TAG:", ["TODAS"] + LISTA_TAGS)
    
    df_c_exibir = st.session_state['df_clientes'].copy()
    if tag_filtro != "TODAS":
        df_c_exibir = df_c_exibir[df_c_exibir["Categoria / TAG"] == tag_filtro]
    if termo:
        mask = df_c_exibir.astype(str).apply(lambda row: row.str.contains(termo, case=False).any(), axis=1)
        df_c_exibir = df_c_exibir[mask]
        
    st.dataframe(df_c_exibir, use_container_width=True)

    # VISUALIZAÇÃO E PDF INDIVIDUAL DO CLIENTE
    if not df_c_exibir.empty:
        st.markdown("---")
        st.markdown("### 📄 Visualizar Ficha Individual do Cliente")
        cli_selecionado = st.selectbox("Selecione uma empresa para abrir a ficha:", df_c_exibir["Empresa"].tolist())
        
        c_dados = df_c_exibir[df_c_exibir["Empresa"] == cli_selecionado].iloc[0]
        pedidos_cliente = df_pedidos[df_pedidos["Empresa"] == cli_selecionado] if not df_pedidos.empty else pd.DataFrame()

        box1, box2 = st.columns([2, 1])
        with box1:
            st.markdown(f"**Empresa:** {c_dados.get('Empresa')}")
            st.markdown(f"**Contato:** {c_dados.get('Contato')} | **Telefone:** {c_dados.get('Telefone')}")
            st.markdown(f"**Cidade:** {c_dados.get('Cidade')} | **TAG:** `{c_dados.get('Categoria / TAG')}`")
            st.markdown(f"**Email:** {c_dados.get('Email')}")

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

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
            "Numero_Pedido": "PED-202609091200",
            "Empresa": "Ambient Serviços Ambientais S/A",
            "Contato": "Natalia",
            "Data_Emissao": "09/09/2026",
            "Data_Evento": "15/09/2026",
            "Valor_Total": 2400.0,
            "Status": "Orçamento / Proposta",
            "Servicos": "Cobertura fotográfica, Captação de vídeo"
        }
    ])

if 'df_clientes' not in st.session_state:
    st.session_state['df_clientes'] = pd.DataFrame([
        {"Empresa": "Ambient Serviços Ambientais S/A", "Contato": "Natalia", "Cidade": "Ribeirão Preto - SP", "Telefone": "(16) 99999-0000", "Email": "contato@ambient.com.br", "Categoria / TAG": "COMÉRCIO"},
        {"Empresa": "Taiwan Hotel Ltda", "Contato": "Gerência", "Cidade": "Ribeirão Preto - SP", "Telefone": "(16) 3900-0000", "Email": "reservas@taiwanhotel.com.br", "Categoria / TAG": "HOTELARIA"}
    ])

if 'df_servicos' not in st.session_state:
    st.session_state['df_servicos'] = pd.DataFrame([
        {"Nome_Servico": "Cobertura fotográfica", "Tipo_Cobranca": "Hora", "Valor_Base": 180.0, "Descricao": "Registros fotográficos de alta resolução com edição de cores e contraste."},
        {"Nome_Servico": "Captação de vídeo", "Tipo_Cobranca": "Hora", "Valor_Base": 200.0, "Descricao": "Gravação em Full HD/4K (material bruto entregue via link)."},
        {"Nome_Servico": "Tour Virtual 360°", "Tipo_Cobranca": "Pacote", "Valor_Base": 800.0, "Descricao": "Mapeamento completo e publicação no Google Street View e ambiente web."},
        {"Nome_Servico": "Otimização Ficha Google", "Tipo_Cobranca": "Pacote", "Valor_Base": 400.0, "Descricao": "Estruturação técnica e atualização de atributos no Google Meu Negócio."}
    ])

if 'texto_institucional' not in st.session_state:
    st.session_state['texto_institucional'] = (
        "Com sólida experiência no mercado de imagem e fotografia profissional com mais de 30 anos de atuação, "
        "a Okamoto Mídias Visuais é especializada na cobertura completa de eventos corporativos, institucionais "
        "e científicos, além da produção de tours virtuais 360° de alta definição.\n\n"
        "Nossa missão é registrar cada projeto com precisão técnica, agilidade e excelência visual."
    )

df_pedidos = st.session_state['df_pedidos']
df_clientes = st.session_state['df_clientes']
df_servicos = st.session_state['df_servicos']

# -----------------------------------------------------------------------------
# 5. GERADOR DE PDF COM DESIGN MODERNO
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
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(40, 40, 555, 40)
            self.drawString(40, 25, "Okamoto Mídias Visuais | (16) 99133-2121 | okamotomidiasvisuais.com.br")
            self.drawRightString(555, 25, f"Página {self._pageNumber} de {num_pages}")
            self.restoreState()
            super().showPage()
        super().save()

def gerar_pdf_proposta_moderna(dados, texto_institucional):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=35, bottomMargin=50)
    styles = getSampleStyleSheet()
    
    style_tit_principal = ParagraphStyle('TitP', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=colors.HexColor('#0f172a'))
    style_sub = ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#2563eb'))
    style_corpo = ParagraphStyle('Corpo', fontName='Helvetica', fontSize=9.5, leading=14, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=9.5, leading=14, textColor=colors.HexColor('#0f172a'))
    
    story = []

    # BANNER SUPERIOR DE CABEÇALHO COM LOGO
    header_data = []
    if st.session_state['logo_bytes']:
        try:
            img_buf = io.BytesIO(st.session_state['logo_bytes'])
            img = Image(img_buf, width=140, height=45)
            header_data = [[img, Paragraph("<b>OKAMOTO MÍDIAS VISUAIS</b><br/><font color='#64748b' size='8'>Fotografia Profissional & Tours Virtuais 360°<br/>Contato: (16) 99133-2121 | Brodowski - SP</font>", style_corpo)]]
        except Exception:
            header_data = [[Paragraph("<b>OKAMOTO MÍDIAS VISUAIS</b>", style_tit_principal), ""]]
    else:
        header_data = [[Paragraph("<b>OKAMOTO MÍDIAS VISUAIS</b>", style_tit_principal), Paragraph("<font color='#64748b' size='8'>Contato: (16) 99133-2121</font>", style_corpo)]]

    t_head = Table(header_data, colWidths=[180, 345])
    t_head.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_head)
    story.append(Spacer(1, 10))

    # PÁGINA 1: APRESENTAÇÃO INSTITUCIONAL
    story.append(Paragraph("APRESENTAÇÃO INSTITUCIONAL", style_sub))
    story.append(Spacer(1, 6))
    story.append(Paragraph(texto_institucional.replace('\n', '<br/>'), style_corpo))
    story.append(Spacer(1, 18))

    story.append(Paragraph("Diferenciais Estratégicos", style_sub))
    story.append(Spacer(1, 6))
    
    dif_data = [
        [Paragraph("<b>Diferencial Técnico</b>", style_bold), Paragraph("<b>Garantia de Qualidade</b>", style_bold)],
        [Paragraph("Equipamentos Câmera Full Frame e 360°", style_corpo), Paragraph("Alta nitidez e fidelidade de cores.", style_corpo)],
        [Paragraph("Agilidade na Entrega", style_corpo), Paragraph("Preview rápido enviado para cobertura ao vivo.", style_corpo)],
        [Paragraph("Download em Nuvem", style_corpo), Paragraph("Acesso por link exclusivo e seguro.", style_corpo)]
    ]
    t_dif = Table(dif_data, colWidths=[220, 305])
    t_dif.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_dif)
    story.append(PageBreak())

    # PÁGINA 2: PROPOSTA COMERCIAL DETALHADA
    story.append(Paragraph("PROPOSTA COMERCIAL", style_tit_principal))
    story.append(Paragraph(f"<font color='#2563eb'><b>Nº do Pedido:</b> {dados['num_pedido']}</font> | <b>Emissão:</b> {dados['data_orcamento']}", style_corpo))
    story.append(Spacer(1, 10))

    cli_info = [
        [Paragraph("<b>Cliente / Empresa:</b>", style_bold), Paragraph(dados['empresa'], style_corpo)],
        [Paragraph("<b>Pessoa de Contato:</b>", style_bold), Paragraph(dados['contato'], style_corpo)],
        [Paragraph("<b>Data do Evento/Serviço:</b>", style_bold), Paragraph(dados['data_evento'], style_corpo)],
        [Paragraph("<b>Local do Atendimento:</b>", style_bold), Paragraph(dados['local'], style_corpo)]
    ]
    t_cli = Table(cli_info, colWidths=[130, 395])
    t_cli.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_cli)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Escopo dos Serviços Solicitados", style_sub))
    story.append(Spacer(1, 6))

    srv_data = [[Paragraph("<b>Serviço</b>", style_bold), Paragraph("<b>Descrição do Escopo</b>", style_bold), Paragraph("<b>Valor (R$)</b>", style_bold)]]
    for item in dados['itens']:
        srv_data.append([
            Paragraph(item['nome'], style_corpo),
            Paragraph(item.get('desc', 'Atendimento conforme especificação.'), style_corpo),
            Paragraph(f"R$ {item['valor']:.2f}", style_corpo)
        ])
    
    t_srv = Table(srv_data, colWidths=[140, 285, 100])
    t_srv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_srv)
    story.append(Spacer(1, 12))

    inv_data = [[Paragraph("<b>INVESTIMENTO TOTAL RECOMENDADO:</b>", style_bold), Paragraph(f"<b>R$ {dados['valor_final']:.2f}</b>", style_bold)]]
    t_inv = Table(inv_data, colWidths=[220, 305])
    t_inv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#dbeafe')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#93c5fd')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_inv)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

def gerar_pdf_relatorio_clientes(df, tag_filtro):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=35, rightMargin=35, topMargin=35, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    story = [
        Paragraph("OKAMOTO MÍDIAS VISUAIS", ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor('#2563eb'))),
        Paragraph(f"Relatório de Base de Clientes - Categoria: {tag_filtro}", ParagraphStyle('Tit', fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor('#0f172a'))),
        Spacer(1, 12)
    ]
    
    t_data = [[Paragraph("<b>Empresa</b>", styles['Normal']), Paragraph("<b>Contato</b>", styles['Normal']), Paragraph("<b>Cidade</b>", styles['Normal']), Paragraph("<b>Telefone</b>", styles['Normal']), Paragraph("<b>TAG</b>", styles['Normal'])]]
    for _, row in df.iterrows():
        t_data.append([
            Paragraph(str(row.get('Empresa', '')), styles['Normal']),
            Paragraph(str(row.get('Contato', '')), styles['Normal']),
            Paragraph(str(row.get('Cidade', '')), styles['Normal']),
            Paragraph(str(row.get('Telefone', '')), styles['Normal']),
            Paragraph(str(row.get('Categoria / TAG', '')), styles['Normal'])
        ])
        
    t_table = Table(t_data, colWidths=[130, 90, 100, 90, 115])
    t_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_table)
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

# ABA 1: GERAR ORÇAMENTO
with aba_orcamento:
    col1, col2 = st.columns(2)
    with col1:
        num_pedido = st.text_input("Número do Pedido", f"PED-{datetime.now().strftime('%Y%m%d%H%M')}")
        empresa_sel = st.selectbox("Cliente Cadastrado", ["Outro / Novo"] + df_clientes["Empresa"].tolist())
        if empresa_sel != "Outro / Novo":
            d_c = df_clientes[df_clientes["Empresa"] == empresa_sel].iloc[0]
            contato = st.text_input("Contato", str(d_c["Contato"]))
            local = st.text_input("Local", str(d_c["Cidade"]))
        else:
            empresa_sel = st.text_input("Nome da Empresa", "Cliente Novo Ltda")
            contato = st.text_input("Contato", "Responsável")
            local = st.text_input("Local", "Ribeirão Preto - SP")
            
        data_orcamento = st.date_input("Emissão", datetime.now()).strftime('%d/%m/%Y')
        data_evento = st.date_input("Data Evento", datetime.now()).strftime('%d/%m/%Y')

    with col2:
        servicos_sel = st.multiselect("Serviços Solicitados", df_servicos["Nome_Servico"].tolist(), default=[df_servicos["Nome_Servico"].iloc[0]])
        status_sel = st.selectbox("Status Inicial do Pedido", ["Orçamento / Proposta", "Em atendimento", "Negociação/Revisão", "Aprovado", "Produção", "Concluído"])

    st.markdown("---")
    st.markdown("### ✍️ Descritivo Institucional da Empresa no PDF")
    st.session_state['texto_institucional'] = st.text_area(
        "Edite a apresentação da empresa que vai na 1ª página da proposta:",
        value=st.session_state['texto_institucional'],
        height=100
    )

    itens_detalhados = []
    valor_calculado = 0.0
    for s in servicos_sel:
        r = df_servicos[df_servicos["Nome_Servico"] == s].iloc[0]
        v = float(r["Valor_Base"])
        itens_detalhados.append({"nome": s, "desc": str(r.get("Descricao", "")), "valor": v})
        valor_calculado += v

    valor_final = st.number_input("Valor Final da Proposta (R$)", value=float(valor_calculado), step=50.0)

    dados_pdf = {"num_pedido": num_pedido, "empresa": empresa_sel, "contato": contato, "local": local, "data_orcamento": data_orcamento, "data_evento": data_evento, "itens": itens_detalhados, "valor_final": valor_final}
    pdf_bytes = gerar_pdf_proposta_moderna(dados_pdf, st.session_state['texto_institucional'])

    cb1, cb2 = st.columns(2)
    with cb1:
        st.download_button("📥 Baixar Proposta Comercial em PDF", data=pdf_bytes, file_name=f"Proposta_{num_pedido}.pdf", mime="application/pdf", use_container_width=True)
    with cb2:
        if st.button("💾 Salvar Pedido no CRM", use_container_width=True):
            novo_p = pd.DataFrame([{"Numero_Pedido": num_pedido, "Empresa": empresa_sel, "Contato": contato, "Data_Emissao": data_orcamento, "Data_Evento": data_evento, "Valor_Total": valor_final, "Status": status_sel, "Servicos": ", ".join(servicos_sel)}])
            st.session_state['df_pedidos'] = pd.concat([st.session_state['df_pedidos'], novo_p], ignore_index=True)
            st.success("Pedido registrado!")
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
                        <span style="color:#94a3b8;">📅 {p['Data_Evento']}</span>
                    </div>
                    """, unsafe_allow_html=True)

# ABA 3: GESTÃO DE CLIENTES
with aba_clientes:
    st.subheader("Cadastrar Novo Cliente")
    with st.form("form_novo_cliente", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        n_empresa = c1.text_input("Empresa:")
        n_contato = c2.text_input("Contato:")
        n_cidade = c3.text_input("Cidade:")
        c4, c5, c6 = st.columns(3)
        n_tel = c4.text_input("Telefone:")
        n_email = c5.text_input("Email:")
        n_cat = c6.selectbox("Categoria / TAG:", LISTA_TAGS)
        if st.form_submit_button("➕ Adicionar Cliente à Base"):
            if n_empresa:
                novo_c = pd.DataFrame([{"Empresa": n_empresa, "Contato": n_contato, "Cidade": n_cidade, "Telefone": n_tel, "Email": n_email, "Categoria / TAG": n_cat}])
                st.session_state['df_clientes'] = pd.concat([st.session_state['df_clientes'], novo_c], ignore_index=True)
                st.success(f"Cliente {n_empresa} cadastrado com sucesso!")
                st.rerun()

    st.markdown("---")
    st.subheader("Base de Clientes Cadastrados")
    
    col_f1, col_f2 = st.columns([2, 1])
    termo = col_f1.text_input("🔍 Pesquisar por Nome, Cidade, Contato:")
    tag_filtro = col_f2.selectbox("Filtrar por Categoria / TAG:", ["TODAS"] + LISTA_TAGS)
    
    df_c_exibir = st.session_state['df_clientes'].copy()
    
    if tag_filtro != "TODAS":
        df_c_exibir = df_c_exibir[df_c_exibir["Categoria / TAG"] == tag_filtro]
        
    if termo:
        mask = df_c_exibir.astype(str).apply(lambda row: row.str.contains(termo, case=False).any(), axis=1)
        df_c_exibir = df_c_exibir[mask]
        
    st.dataframe(df_c_exibir, use_container_width=True)
    
    pdf_cli_bytes = gerar_pdf_relatorio_clientes(df_c_exibir, tag_filtro)
    st.download_button("📄 Gerar Relatório de Clientes em PDF", data=pdf_cli_bytes, file_name=f"Relatorio_Clientes_{tag_filtro}.pdf", mime="application/pdf")

# ABA 4: CATÁLOGO DE SERVIÇOS (EDIÇÃO E EXCLUSÃO)
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

import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
from streamlit_gsheets import GSheetsConnection

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILIZAÇÃO VISUAL MODERNA (SaaS / CRM)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CRM Okamoto Mídias Visuais",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0b0f17;
    }
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .header-title {
        color: #f8fafc;
        font-size: 26px;
        font-weight: 700;
        margin: 0;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 6px;
    }
    .kpi-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .kpi-title {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .kpi-value {
        color: #38bdf8;
        font-size: 24px;
        font-weight: 700;
        margin-top: 6px;
    }
    .kanban-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-left: 4px solid #3b82f6;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .kanban-title {
        color: #f8fafc;
        font-weight: 600;
        font-size: 14px;
    }
    .kanban-price {
        color: #10b981;
        font-weight: 700;
        font-size: 15px;
        margin-top: 4px;
    }
    .kanban-date {
        color: #64748b;
        font-size: 11px;
        margin-top: 6px;
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="padding: 10px 0px;">
    <h3 style="margin: 0; color: #f8fafc; font-size: 18px;">OKAMOTO MÍDIAS VISUAIS</h3>
    <p style="margin: 2px 0 0 0; color: #94a3b8; font-size: 12px;">criado por Rubens Okamoto</p>
</div>
<hr style="margin: 10px 0; border-color: #334155;"/>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. AUTENTICAÇÃO E LOGIN SEGURO
# -----------------------------------------------------------------------------
def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<br/><br/>", unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            st.markdown("""
            <div class="header-box" style="text-align: center;">
                <h2 style="color: #f8fafc; margin-bottom: 8px;">🔐 Acesso Restrito</h2>
                <p style="color: #94a3b8; font-size: 14px;">Okamoto Mídias Visuais & Tour360VR</p>
            </div>
            """, unsafe_allow_html=True)
            senha = st.text_input("Senha de Acesso", type="password", placeholder="Digite a senha...")
            if st.button("Acessar Plataforma", use_container_width=True):
                if senha == "okamoto2026":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Senha incorreta! Tente novamente.")
        return False
    return True

if not verificar_senha():
    st.stop()

# -----------------------------------------------------------------------------
# 3. CONEXÃO COM O GOOGLE SHEETS
# -----------------------------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados_aba(aba_nome):
    try:
        df = conn.read(worksheet=aba_nome, ttl=0)
        return df
    except Exception:
        return pd.DataFrame()

df_clientes = carregar_dados_aba("Clientes")
df_servicos = carregar_dados_aba("Servicos")
df_pedidos = carregar_dados_aba("Pedidos")

if df_servicos.empty:
    df_servicos = pd.DataFrame([
        {"Nome_Servico": "Cobertura fotográfica", "Tipo_Cobranca": "Hora", "Valor_Base": 180.0, "Descricao": "Registros fotográficos de alta resolução com edição de cores e contraste."},
        {"Nome_Servico": "Captação de vídeo", "Tipo_Cobranca": "Hora", "Valor_Base": 200.0, "Descricao": "Gravação em Full HD/4K (material bruto entregue via link)."},
        {"Nome_Servico": "Tour Virtual 360°", "Tipo_Cobranca": "Pacote", "Valor_Base": 800.0, "Descricao": "Mapeamento completo e publicação no Google Street View e ambiente web."},
        {"Nome_Servico": "Otimização Ficha Google", "Tipo_Cobranca": "Pacote", "Valor_Base": 400.0, "Descricao": "Estruturação técnica e atualização de atributos no Google Meu Negócio."}
    ])

# -----------------------------------------------------------------------------
# 4. GERADOR DE PDF DA PROPOSTA COMERCIAL (2 PÁGINAS)
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

    # PÁGINA 1: INSTITUCIONAL
    story.append(Paragraph("OKAMOTO MÍDIAS VISUAIS", style_subtitulo))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Apresentação Institucional & Portfólio de Serviços", style_titulo))
    story.append(Spacer(1, 15))
    
    apresentacao = (
        "Com sólida experiência no mercado de imagem e fotografia profissional, a <b>Okamoto Mídias Visuais</b> "
        "é especializada na cobertura completa de eventos corporativos, institucionais e científicos, além de produção "
        "de tours virtuais 360° e conteúdos em vídeo de alta definição.<br/><br/>"
        "Nossa missão é registrar cada momento com precisão técnica, agilidade e rigor editorial, "
        "garantindo um acervo visual estratégico para mídias sociais, assessoria de imprensa e relatórios corporativos."
    )
    story.append(Paragraph(apresentacao, style_corpo))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Diferenciais Competitivos", style_subtitulo))
    story.append(Spacer(1, 8))
    
    diferenciais = [
        [Paragraph("<b>Diferencial</b>", style_bold), Paragraph("<b>Benefício para o Cliente</b>", style_bold)],
        [Paragraph("Equipamentos Profissionais", style_corpo), Paragraph("Câmeras Full Frame e captação digital sem ruído.", style_corpo)],
        [Paragraph("Agilidade na Entrega", style_corpo), Paragraph("Envio de seleção rápida para redes sociais durante o evento.", style_corpo)],
        [Paragraph("Plataforma Dedicada", style_corpo), Paragraph("Download seguro via link exclusivo com prazo estendido.", style_corpo)],
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
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 7),
    ]))
    for i in range(3):
        t_srv.setStyle(TableStyle([('TEXTCOLOR', (i, 0), (i, 0), colors.white)]))
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
    story.append(Spacer(1, 12))

    story.append(Paragraph("Condições de Fornecimento e Pagamento", style_subtitulo))
    story.append(Spacer(1, 4))
    condicoes = f"""
    <b>Forma de Entrega:</b> {dados['forma_entrega']}<br/>
    <b>Prazo de Entrega:</b> {dados['prazo_entrega']}<br/>
    <b>Forma de Pagamento:</b> {dados['forma_pagamento']}
    """
    story.append(Paragraph(condicoes, style_corpo))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 5. HEADER INSTITUCIONAL & MÉTRICAS (KPIs)
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-box">
    <div class="header-title">💼 CRM Okamoto Mídias Visuais</div>
    <div class="header-subtitle">Plataforma Integrada de Gestão de Clientes, Propostas Comerciais e Funil de Vendas</div>
</div>
""", unsafe_allow_html=True)

total_clientes = len(df_clientes) if not df_clientes.empty else 0
total_pedidos = len(df_pedidos) if not df_pedidos.empty else 0
valor_total_propostas = df_pedidos["Valor_Total"].astype(float).sum() if not df_pedidos.empty and "Valor_Total" in df_pedidos.columns else 0.0
total_servicos = len(df_servicos) if not df_servicos.empty else 0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🏢 Base de Clientes</div>
        <div class="kpi-value">{total_clientes:,}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">📄 Propostas Emitidas</div>
        <div class="kpi-value">{total_pedidos}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">💰 Volume em Negociação</div>
        <div class="kpi-value">R$ {valor_total_propostas:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🛠️ Serviços Ativos</div>
        <div class="kpi-value">{total_servicos}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. INTERFACE EM ABAS NATIVAS
# -----------------------------------------------------------------------------
aba_orcamento, aba_kanban, aba_clientes, aba_catalogo = st.tabs([
    "📄 Gerar Orçamento / Pedido",
    "📊 Funil de Vendas",
    "🏢 Gestão de Clientes",
    "🛠️ Catálogo de Serviços"
])

# ABA 1: GERAR ORÇAMENTO
with aba_orcamento:
    st.subheader("Emissão de Proposta Comercial em PDF")
    col1, col2 = st.columns(2)
    with col1:
        num_pedido = st.text_input("Número do Pedido/Orçamento", f"PED-{datetime.now().strftime('%Y%m%d%H%M')}")
        lista_empresas = ["Outro / Cliente Novo"] + (df_clientes["Empresa"].dropna().unique().tolist() if not df_clientes.empty and "Empresa" in df_clientes.columns else [])
        empresa_sel = st.selectbox("Selecione a Empresa / Cliente", lista_empresas)
        
        if empresa_sel != "Outro / Cliente Novo" and not df_clientes.empty:
            dados_cli = df_clientes[df_clientes["Empresa"] == empresa_sel].iloc[0]
            contato = st.text_input("Pessoa de Contato", str(dados_cli.get("Contato", "")))
            cidade_cli = str(dados_cli.get("Cidade", ""))
            local = st.text_input("Local do Evento / Atendimento", cidade_cli if cidade_cli else "Ribeirão Preto - SP")
        else:
            empresa_sel = st.text_input("Nome da Empresa", "Ambient Serviços Ambientais S/A")
            contato = st.text_input("Pessoa de Contato", "Natalia")
            local = st.text_input("Local do Evento / Atendimento", "Ribeirão Preto - SP")
            
        data_orcamento = st.date_input("Data da Emissão", datetime.now()).strftime('%d/%m/%Y')
        data_evento = st.date_input("Data do Evento/Serviço", datetime.now()).strftime('%d/%m/%Y')
        horario = st.text_input("Horário / Escala", "08h00 às 18h00 (Intervalo de 1h30)")

    with col2:
        periodo = st.selectbox("Carga Horária / Período Base", ["1 hora", "2 horas", "4 horas", "10 horas (Diária)", "Personalizado"])
        servicos_nomes = df_servicos["Nome_Servico"].tolist() if not df_servicos.empty else []
        servicos_sel = st.multiselect("Serviços Incluídos na Proposta", servicos_nomes, default=servicos_nomes[:1] if servicos_nomes else [])
        forma_entrega = st.text_input("Forma de Entrega", "Link exclusivo para download em alta e baixa resolução.")
        prazo_entrega = st.text_input("Prazo de Entrega", "Até 72h após o término do evento.")
        forma_pagamento = st.text_input("Condições de Pagamento", "Faturamento em até 20 dias após o evento.")

    itens_detalhados = []
    valor_calculado = 0.0
    for s in servicos_sel:
        row = df_servicos[df_servicos["Nome_Servico"] == s].iloc[0]
        v_base = float(row.get("Valor_Base", 0.0))
        itens_detalhados.append({"nome": s, "desc": str(row.get("Descricao", "")), "valor": v_base})
        valor_calculado += v_base

    st.markdown("---")
    c_calc, c_ajuste = st.columns(2)
    c_calc.metric("Valor Total Calculado", f"R$ {valor_calculado:.2f}")
    
    usar_desconto = c_ajuste.checkbox("Aplicar valor final ajustado / desconto")
    if usar_desconto:
        valor_final = c_ajuste.number_input("Digite o Valor Final Desejado (R$)", value=float(valor_calculado), step=50.0)
    else:
        valor_final = valor_calculado

    dados_pdf = {
        "num_pedido": num_pedido, "empresa": empresa_sel, "contato": contato, "local": local,
        "data_orcamento": data_orcamento, "data_evento": data_evento, "horario": horario,
        "periodo": periodo, "itens": itens_detalhados, "valor_final": valor_final,
        "forma_entrega": forma_entrega, "prazo_entrega": prazo_entrega, "forma_pagamento": forma_pagamento
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
        if st.button("💾 Salvar Pedido no Google Sheets", use_container_width=True):
            novo_registro = pd.DataFrame([{
                "Numero_Pedido": num_pedido,
                "Empresa": empresa_sel,
                "Contato": contato,
                "Data_Emissao": data_orcamento,
                "Data_Evento": data_evento,
                "Valor_Total": valor_final,
                "Status": "Orçamento / Proposta",
                "Servicos": ", ".join(servicos_sel)
            }])
            df_atualizado = pd.concat([df_pedidos, novo_registro], ignore_index=True)
            try:
                conn.update(worksheet="Pedidos", data=df_atualizado)
                st.success(f"Pedido {num_pedido} salvo com sucesso no Google Sheets!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar no Google Sheets: {e}")

# ABA 2: FUNIL KANBAN
with aba_kanban:
    st.subheader("Estágios do Atendimento Comercial")
    fases = ["Orçamento / Proposta", "Em atendimento", "Negociação/Revisão", "Aprovado", "Produção", "Concluído", "Cancelado"]
    cols = st.columns(len(fases))
    for idx, fase in enumerate(fases):
        with cols[idx]:
            st.markdown(f"**{fase}**")
            if not df_pedidos.empty and "Status" in df_pedidos.columns:
                pedidos_fase = df_pedidos[df_pedidos["Status"] == fase]
                st.caption(f"{len(pedidos_fase)} Projeto(s)")
                for _, ped in pedidos_fase.iterrows():
                    st.markdown(f"""
                    <div class="kanban-card">
                        <div class="kanban-title">{ped.get('Empresa', 'N/I')}</div>
                        <div class="kanban-price">R$ {float(ped.get('Valor_Total', 0)):,.2f}</div>
                        <div class="kanban-date">📅 Data: {ped.get('Data_Evento', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("0 Projetos")

# ABA 3: GESTÃO DE CLIENTES & EXPORTAÇÃO PDF POR CATEGORIA
with aba_clientes:
    st.subheader("Base de Empresas e Contatos Cadastrados")
    termo_busca = st.text_input("🔍 Pesquisar por Categoria, Nome da Empresa, Cidade ou Tag (ex: HOTELARIA, Ribeirão Preto, AVIRRP):")
    if not df_clientes.empty:
        df_exibir = df_clientes.copy()
        if termo_busca:
            mask = df_exibir.astype(str).apply(lambda row: row.str.contains(termo_busca, case=False).any(), axis=1)
            df_exibir = df_exibir[mask]
        st.dataframe(df_exibir, use_container_width=True)
        st.caption(f"Exibindo {len(df_exibir)} de {len(df_clientes)} cadastros encontrados.")
        if not df_exibir.empty:
            def gerar_pdf_relatorio_clientes(df, filtro):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=40)
                styles = getSampleStyleSheet()
                story = [
                    Paragraph("OKAMOTO MÍDIAS VISUAIS & TOUR360VR", ParagraphStyle('Sub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#2563eb'))),
                    Paragraph(f"Relatório de Clientes / Filtro: {filtro.upper() if filtro else 'GERAL'}", ParagraphStyle('Tit', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, leading=20)),
                    Spacer(1, 12)
                ]
                t_data = [[Paragraph("<b>Empresa</b>", styles['Normal']), Paragraph("<b>Cidade</b>", styles['Normal']), Paragraph("<b>Telefone</b>", styles['Normal']), Paragraph("<b>Contato / Email</b>", styles['Normal'])]]
                for _, row in df.iterrows():
                    t_data.append([
                        Paragraph(str(row.get('Empresa', '')), styles['Normal']),
                        Paragraph(str(row.get('Cidade', '')), styles['Normal']),
                        Paragraph(str(row.get('Telefone', '')), styles['Normal']),
                        Paragraph(f"{str(row.get('Contato', ''))}<br/>{str(row.get('Email', ''))}", styles['Normal'])
                    ])
                t_table = Table(t_data, colWidths=[170, 110, 100, 155])
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

            pdf_relatorio = gerar_pdf_relatorio_clientes(df_exibir, termo_busca)
            st.download_button(
                label=f"📥 Baixar Relatório em PDF ({len(df_exibir)} empresas listadas)",
                data=pdf_relatorio,
                file_name=f"Relatorio_{termo_busca if termo_busca else 'Geral'}.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Nenhum cliente cadastrado na aba 'Clientes' do Google Sheets.")

# ABA 4: CATÁLOGO DE SERVIÇOS
with aba_catalogo:
    st.subheader("Catálogo Geral de Serviços e Preços Base")
    st.dataframe(df_servicos, use_container_width=True)

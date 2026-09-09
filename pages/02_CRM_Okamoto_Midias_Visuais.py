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

# Estilização Dark SaaS
st.markdown("""
<style>
    .stApp { background-color: #0b0f17; }
    [data-testid="stSidebar"] { background-color: #111827; border-right: 1px solid #1f2937; }
    .card-crm { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# Função para localizar a Logo em diferentes caminhos
def obter_caminho_logo():
    caminhos = [
        'assets/logo_okamoto.png', 'logo_okamoto.png', 
        'assets/Logo_TOUR_transparente.png', 'Logo_TOUR_transparente.png',
        'assets/Logo TOUR transparente.png'
    ]
    for c in caminhos:
        if os.path.exists(c):
            return c
    return None

caminho_logo = obter_caminho_logo()

# BARRA LATERAL COM LOGO E ASSINATURA
with st.sidebar:
    if caminho_logo:
        st.image(caminho_logo, use_container_width=True)
    
    st.markdown("""
    <div style="padding: 5px 0px;">
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
# 3. BASE DE DADOS EM MEMÓRIA / BANCO LOCAL PERSISTENTE NA SESSÃO
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
        {"Empresa": "Ambient Serviços Ambientais S/A", "Contato": "Natalia", "Cidade": "Ribeirão Preto - SP", "Telefone": "(16) 99999-0000", "Email": "contato@ambient.com.br", "Categoria": "CORPORATIVO"},
        {"Empresa": "Taiwan Hotel Ltda", "Contato": "Gerência", "Cidade": "Ribeirão Preto - SP", "Telefone": "(16) 3900-0000", "Email": "reservas@taiwanhotel.com.br", "Categoria": "HOTELARIA"}
    ])

df_servicos = pd.DataFrame([
    {"Nome_Servico": "Cobertura fotográfica", "Tipo_Cobranca": "Hora", "Valor_Base": 180.0, "Descricao": "Registros fotográficos de alta resolução com edição de cores e contraste."},
    {"Nome_Servico": "Captação de vídeo", "Tipo_Cobranca": "Hora", "Valor_Base": 200.0, "Descricao": "Gravação em Full HD/4K (material bruto entregue via link)."},
    {"Nome_Servico": "Tour Virtual 360°", "Tipo_Cobranca": "Pacote", "Valor_Base": 800.0, "Descricao": "Mapeamento completo e publicação no Google Street View e ambiente web."},
    {"Nome_Servico": "Otimização Ficha Google", "Tipo_Cobranca": "Pacote", "Valor_Base": 400.0, "Descricao": "Estruturação técnica e atualização de atributos no Google Meu Negócio."}
])

# -----------------------------------------------------------------------------
# 4. GERADOR DE PDF DA PROPOSTA COM LOGO OFICIAL
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

    # LOGO DA OKAMOTO NO TOPO DA PÁGINA 1 DO PDF
    logo_path = obter_caminho_logo()
    if logo_path:
        try:
            story.append(Image(logo_path, width=150, height=48))
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
    if logo_path:
        try:
            story.append(Image(logo_path, width=120, height=38))
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
# 5. HEADER INSTITUCIONAL & METRICAS (KPIs)
# -----------------------------------------------------------------------------
st.title("💼 CRM Okamoto Mídias Visuais")
st.write("Plataforma Integrada de Gestão de Clientes, Propostas Comerciais e Funil de Vendas")

df_pedidos = st.session_state['df_pedidos']
df_clientes = st.session_state['df_clientes']

total_clientes = len(df_clientes)
total_pedidos = len(df_pedidos)
valor_total_propostas = df_pedidos["Valor_Total"].astype(float).sum() if not df_pedidos.empty else 0.0
total_servicos = len(df_servicos)

k1, k2, k3, k4 = st.columns(4)
k1.metric("🏢 Base de Clientes", f"{total_clientes:,}")
k2.metric("📄 Propostas Emitidas", f"{total_pedidos}")
k3.metric("💰 Volume em Negociação", f"R$ {valor_total_propostas:,.2f}")
k4.metric("🛠️ Serviços Ativos", f"{total_servicos}")

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. INTERFACE EM ABAS NATIVAS RESTAURADA (4 ABAS COMPLETAS)
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
        lista_empresas = ["Outro / Cliente Novo"] + df_clientes["Empresa"].dropna().unique().tolist()
        empresa_sel = st.selectbox("Selecione a Empresa / Cliente", lista_empresas)
        
        if empresa_sel != "Outro / Cliente Novo":
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
        servicos_sel = st.multiselect("Serviços Incluídos na Proposta", df_servicos["Nome_Servico"].tolist(), default=["Cobertura fotográfica"])
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
        if st.button("💾 Registrar Proposta no Histórico do CRM", use_container_width=True):
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
            st.session_state['df_pedidos'] = pd.concat([st.session_state['df_pedidos'], novo_registro], ignore_index=True)
            st.success(f"Proposta {num_pedido} salva no histórico do CRM com sucesso!")
            st.rerun()

# ABA 2: FUNIL KANBAN
with aba_kanban:
    st.subheader("Estágios do Atendimento Comercial")
    fases = ["Orçamento / Proposta", "Em atendimento", "Negociação/Revisão", "Aprovado", "Produção", "Concluído", "Cancelado"]
    cols = st.columns(len(fases))
    for idx, fase in enumerate(fases):
        with cols[idx]:
            st.markdown(f"**{fase}**")
            pedidos_fase = df_pedidos[df_pedidos["Status"] == fase] if not df_pedidos.empty else pd.DataFrame()
            st.caption(f"{len(pedidos_fase)} Projeto(s)")
            if not pedidos_fase.empty:
                for _, ped in pedidos_fase.iterrows():
                    st.write(f"**{ped.get('Empresa', 'N/I')}**")
                    st.write(f"R$ {float(ped.get('Valor_Total', 0)):,.2f}")
                    st.caption(f"📅 {ped.get('Data_Evento', '')}")
                    st.markdown("---")

# ABA 3: GESTÃO DE CLIENTES
with aba_clientes:
    st.subheader("Base de Empresas e Contatos Cadastrados")
    termo_busca = st.text_input("🔍 Pesquisar por Categoria, Nome da Empresa, Cidade ou Tag:")
    df_exibir = df_clientes.copy()
    if termo_busca:
        mask = df_exibir.astype(str).apply(lambda row: row.str.contains(termo_busca, case=False).any(), axis=1)
        df_exibir = df_exibir[mask]
    st.dataframe(df_exibir, use_container_width=True)
    
    # EXPORTAÇÃO COMPLETA DA BASE DE DADOS EM CSV/EXCEL
    csv_pedidos = st.session_state['df_pedidos'].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 Baixar Planilha Geral de Pedidos e Propostas (CSV / Excel)",
        data=csv_pedidos,
        file_name="relatorio_pedidos_okamoto.csv",
        mime="text/csv"
    )

# ABA 4: CATÁLOGO DE SERVIÇOS
with aba_catalogo:
    st.subheader("Catálogo Geral de Serviços e Preços Base")
    st.dataframe(df_servicos, use_container_width=True)

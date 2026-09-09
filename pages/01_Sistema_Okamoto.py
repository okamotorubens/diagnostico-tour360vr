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
# 1. CONFIGURAÇÃO DA PÁGINA E LOGIN SEGURO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sistema Okamoto & Tour360",
    page_icon="💼",
    layout="wide"
)

def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.title("🔒 Acesso Restrito - Okamoto Mídias Visuais")
        senha = st.text_input("Digite a senha de acesso ao sistema:", type="password")
        if st.button("Entrar"):
            if senha == "okamoto2026":  # Altere esta senha se desejar
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return False
    return True

if not verificar_senha():
    st.stop()

# -----------------------------------------------------------------------------
# 2. CONEXÃO COM O GOOGLE SHEETS
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

# Fallback para catálogo de serviços caso a planilha esteja vazia
if df_servicos.empty:
    df_servicos = pd.DataFrame([
        {"Nome_Servico": "Cobertura fotográfica", "Tipo_Cobranca": "Hora", "Valor_Base": 180.0, "Descricao": "Registros fotográficos de alta resolução com edição de cores e contraste."},
        {"Nome_Servico": "Captação de vídeo", "Tipo_Cobranca": "Hora", "Valor_Base": 200.0, "Descricao": "Gravação em Full HD/4K (material bruto entregue via link)."},
        {"Nome_Servico": "Tour Virtual 360°", "Tipo_Cobranca": "Pacote", "Valor_Base": 800.0, "Descricao": "Mapeamento completo e publicação no Google Street View e ambiente web."},
        {"Nome_Servico": "Otimização Ficha Google", "Tipo_Cobranca": "Pacote", "Valor_Base": 400.0, "Descricao": "Estruturação técnica e atualização de atributos no Google Meu Negócio."}
    ])

# -----------------------------------------------------------------------------
# 3. GERADOR DE PDF DE 2 PÁGINAS (REPORTLAB)
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

    # PÁGINA 1: APRESENTAÇÃO INSTITUCIONAL
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

    # PÁGINA 2: PROPOSTA COMERCIAL DETALHADA
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
# 4. INTERFACE PRINCIPAL E ABAS DE NAVEGAÇÃO
# -----------------------------------------------------------------------------
st.title("💼 Sistema Unificado - Okamoto Mídias & Tour360VR")

aba_orcamento, aba_kanban, aba_clientes, aba_catalogo = st.tabs([
    "📄 Gerar Orçamento / Pedido",
    "📊 Funil Kanban (Bigin)",
    "🏢 Gestão de Clientes",
    "🛠️ Catálogo de Serviços (Agenda Boa)"
])

# -----------------------------------------------------------------------------
# ABA 1: GERAR ORÇAMENTO E SALVAR NO GOOGLE SHEETS
# -----------------------------------------------------------------------------
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
            label="📥 1. Baixar Proposta Comercial em PDF",
            data=pdf_bytes,
            file_name=f"Proposta_{num_pedido}_{empresa_sel.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
    with col_btn2:
        if st.button("💾 2. Salvar Pedido no Google Sheets", use_container_width=True):
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

# -----------------------------------------------------------------------------
# ABA 2: FUNIL KANBAN (BIGIN)
# -----------------------------------------------------------------------------
with aba_kanban:
    st.subheader("Funil de Vendas - Estágios do Atendimento")
    fases = ["Orçamento / Proposta", "Em atendimento", "Negociação/Revisão", "Aprovado", "Produção", "Concluído", "Cancelado"]
    
    cols = st.columns(len(fases))
    for idx, fase in enumerate(fases):
        with cols[idx]:
            st.markdown(f"**{fase}**")
            if not df_pedidos.empty and "Status" in df_pedidos.columns:
                pedidos_fase = df_pedidos[df_pedidos["Status"] == fase]
                st.caption(f"{len(pedidos_fase)} Projeto(s)")
                for _, ped in pedidos_fase.iterrows():
                    with st.container():
                        st.write(f"**{ped.get('Empresa', 'N/I')}**")
                        st.write(f"R$ {float(ped.get('Valor_Total', 0)):.2f}")
                        st.caption(f"Data: {ped.get('Data_Evento', '')}")
                        st.markdown("---")
            else:
                st.caption("0 Projetos")

# -----------------------------------------------------------------------------
# ABA 3: GESTÃO DE CLIENTES (BUSCA AVANÇADA POR NOME, CIDADE OU TAG)
# -----------------------------------------------------------------------------
with aba_clientes:
    st.subheader("Base de Empresas e Contatos")
    termo_busca = st.text_input("🔍 Pesquisar por Nome da Empresa, Cidade, Tag ou Segmento:")
    
    if not df_clientes.empty:
        df_exibir = df_clientes.copy()
        if termo_busca:
            mask = df_exibir.astype(str).apply(lambda row: row.str.contains(termo_busca, case=False).any(), axis=1)
            df_exibir = df_exibir[mask]
        
        st.dataframe(df_exibir, use_container_width=True)
        st.caption(f"Exibindo {len(df_exibir)} de {len(df_clientes)} cadastros.")
    else:
        st.warning("Nenhum cliente cadastrado na aba 'Clientes' do Google Sheets.")

# -----------------------------------------------------------------------------
# ABA 4: CATÁLOGO DE SERVIÇOS (AGENDA BOA)
# -----------------------------------------------------------------------------
with aba_catalogo:
    st.subheader("Catálogo Geral de Serviços e Preços Base")
    st.dataframe(df_servicos, use_container_width=True)

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

def obter_caminho_logo():
    caminhos = [
        'assets/logo_okamoto.png', 'logo_okamoto.png', 
        'assets/Logo_TOUR_transparente.png', 'Logo_TOUR_transparente.png'
    ]
    for c in caminhos:
        if os.path.exists(c):
            return c
    return None

caminho_logo = obter_caminho_logo()

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
# 2. AUTENTICAÇÃO
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
# 3. BANCO DE DADOS EM SESSÃO PERSISTENTE
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

if 'df_servicos' not in st.session_state:
    st.session_state['df_servicos'] = pd.DataFrame([
        {"Nome_Servico": "Cobertura fotográfica", "Tipo_Cobranca": "Hora", "Valor_Base": 180.0, "Descricao": "Registros fotográficos de alta resolução com edição de cores e contraste."},
        {"Nome_Servico": "Captação de vídeo", "Tipo_Cobranca": "Hora", "Valor_Base": 200.0, "Descricao": "Gravação em Full HD/4K (material bruto entregue via link)."},
        {"Nome_Servico": "Tour Virtual 360°", "Tipo_Cobranca": "Pacote", "Valor_Base": 800.0, "Descricao": "Mapeamento completo e publicação no Google Street View e ambiente web."},
        {"Nome_Servico": "Otimização Ficha Google", "Tipo_Cobranca": "Pacote", "Valor_Base": 400.0, "Descricao": "Estruturação técnica e atualização de atributos no Google Meu Negócio."}
    ])

df_pedidos = st.session_state['df_pedidos']
df_clientes = st.session_state['df_clientes']
df_servicos = st.session_state['df_servicos']

# -----------------------------------------------------------------------------
# 4. GERADOR DE PDF
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
            self.drawString(40, 30, "Okamoto Mídias Visuais | (16) 99133-2121 | okamotomidiasvisuais.com.br")
            self.drawRightString(555, 30, f"Página {self._pageNumber} de {num_pages}")
            super().showPage()
        super().save()

def gerar_pdf_proposta(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=60)
    styles = getSampleStyleSheet()
    
    style_titulo = ParagraphStyle('Titulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.HexColor('#0f172a'))
    style_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=colors.HexColor('#2563eb'))
    style_corpo = ParagraphStyle('Corpo', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=15, textColor=colors.HexColor('#334155'))
    style_bold = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=15, textColor=colors.HexColor('#0f172a'))
    
    story = []
    logo_path = obter_caminho_logo()
    if logo_path:
        try:
            story.append(Image(logo_path, width=150, height=48))
            story.append(Spacer(1, 10))
        except Exception:
            pass

    story.append(Paragraph("OKAMOTO MÍDIAS VISUAIS", style_subtitulo))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Apresentação Institucional & Portfólio de Serviços", style_titulo))
    story.append(Spacer(1, 15))
    
    apresentacao = (
        "Com sólida experiência no mercado de imagem e fotografia profissional, a <b>Okamoto Mídias Visuais</b> "
        "é especializada na cobertura completa de eventos corporativos, institucionais e científicos."
    )
    story.append(Paragraph(apresentacao, style_corpo))
    story.append(Spacer(1, 20))
    story.append(PageBreak())

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
        [Paragraph("<b>Local:</b>", style_bold), Paragraph(dados['local'], style_corpo)],
    ]
    t_cli = Table(cliente_data, colWidths=[110, 405])
    t_cli.setStyle(TableStyle([('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f1f5f9')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0'))]))
    story.append(t_cli)
    story.append(Spacer(1, 12))

    itens_data = [[Paragraph("<b>Serviço</b>", style_bold), Paragraph("<b>Subtotal</b>", style_bold)]]
    for srv in dados['itens']:
        itens_data.append([Paragraph(srv['nome'], style_corpo), Paragraph(f"R$ {srv['valor']:.2f}", style_corpo)])
    
    t_srv = Table(itens_data, colWidths=[415, 100])
    t_srv.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1'))]))
    story.append(t_srv)
    story.append(Spacer(1, 10))

    invest_data = [[Paragraph("<b>INVESTIMENTO TOTAL:</b>", style_bold), Paragraph(f"<b>R$ {dados['valor_final']:.2f}</b>", style_bold)]]
    t_inv = Table(invest_data, colWidths=[180, 335])
    t_inv.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#dbeafe')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#93c5fd'))]))
    story.append(t_inv)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 5. DASHBOARD & ABAS
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

    itens_detalhados = []
    valor_calculado = 0.0
    for s in servicos_sel:
        r = df_servicos[df_servicos["Nome_Servico"] == s].iloc[0]
        v = float(r["Valor_Base"])
        itens_detalhados.append({"nome": s, "valor": v})
        valor_calculado += v

    valor_final = st.number_input("Valor Final (R$)", value=float(valor_calculado), step=50.0)

    dados_pdf = {"num_pedido": num_pedido, "empresa": empresa_sel, "contato": contato, "local": local, "data_orcamento": data_orcamento, "data_evento": data_evento, "itens": itens_detalhados, "valor_final": valor_final}
    pdf_bytes = gerar_pdf_proposta(dados_pdf)

    cb1, cb2 = st.columns(2)
    with cb1:
        st.download_button("📥 Baixar Proposta em PDF", data=pdf_bytes, file_name=f"Proposta_{num_pedido}.pdf", mime="application/pdf", use_container_width=True)
    with cb2:
        if st.button("💾 Salvar Pedido no CRM", use_container_width=True):
            novo_p = pd.DataFrame([{"Numero_Pedido": num_pedido, "Empresa": empresa_sel, "Contato": contato, "Data_Emissao": data_orcamento, "Data_Evento": data_evento, "Valor_Total": valor_final, "Status": status_sel, "Servicos": ", ".join(servicos_sel)}])
            st.session_state['df_pedidos'] = pd.concat([st.session_state['df_pedidos'], novo_p], ignore_index=True)
            st.success("Pedido registrado!")
            st.rerun()

# ABA 2: FUNIL KANBAN (LINHA ÚNICA ALINHADA)
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
        n_cat = c6.selectbox("Categoria:", ["CORPORATIVO", "HOTELARIA", "GASTRONOMIA", "SERVIÇOS", "OUTROS"])
        if st.form_submit_button("➕ Adicionar Cliente à Base"):
            if n_empresa:
                novo_c = pd.DataFrame([{"Empresa": n_empresa, "Contato": n_contato, "Cidade": n_cidade, "Telefone": n_tel, "Email": n_email, "Categoria": n_cat}])
                st.session_state['df_clientes'] = pd.concat([st.session_state['df_clientes'], novo_c], ignore_index=True)
                st.success(f"Cliente {n_empresa} cadastrado com sucesso!")
                st.rerun()

    st.markdown("---")
    st.subheader("Base de Clientes Cadastrados")
    termo = st.text_input("🔍 Pesquisar Cliente:")
    df_c_exibir = st.session_state['df_clientes'].copy()
    if termo:
        mask = df_c_exibir.astype(str).apply(lambda row: row.str.contains(termo, case=False).any(), axis=1)
        df_c_exibir = df_c_exibir[mask]
    st.dataframe(df_c_exibir, use_container_width=True)

# ABA 4: CATÁLOGO DE SERVIÇOS
with aba_catalogo:
    st.subheader("Cadastrar Novo Serviço / Preço")
    with st.form("form_novo_servico", clear_on_submit=True):
        cs1, cs2, cs3 = st.columns([2, 1, 1])
        s_nome = cs1.text_input("Nome do Serviço:")
        s_tipo = cs2.selectbox("Tipo de Cobrança:", ["Hora", "Pacote", "Diária", "Unidade", "Mensal"])
        s_valor = cs3.number_input("Valor Base (R$):", min_value=0.0, step=50.0)
        s_desc = st.text_area("Descrição do Serviço:")
        if st.form_submit_button("➕ Salvar Serviço no Catálogo"):
            if s_nome:
                novo_s = pd.DataFrame([{"Nome_Servico": s_nome, "Tipo_Cobranca": s_tipo, "Valor_Base": s_valor, "Descricao": s_desc}])
                st.session_state['df_servicos'] = pd.concat([st.session_state['df_servicos'], novo_s], ignore_index=True)
                st.success(f"Serviço '{s_nome}' adicionado ao catálogo!")
                st.rerun()

    st.markdown("---")
    st.subheader("Catálogo Ativo de Serviços")
    st.dataframe(st.session_state['df_servicos'], use_container_width=True)

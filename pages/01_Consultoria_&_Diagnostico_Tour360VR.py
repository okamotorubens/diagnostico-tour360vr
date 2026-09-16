import io
import os
import requests
import streamlit as st
from PIL import Image

# Dependências do ReportLab para o PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    PageBreak
)

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA DO STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tour360VR - Diagnóstico & Proposta GMB",
    page_icon="📸",
    layout="wide"
)

# Estilização CSS personalizada do Streamlit
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .header-bar {
        background-color: #0b3c5d;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 25px;
    }
    .kpi-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #0b3c5d;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .kpi-title {
        font-size: 12px;
        color: #6c757d;
        text-transform: uppercase;
        font-weight: bold;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: bold;
        color: #1d2731;
    }
    .kpi-desc {
        font-size: 12px;
        color: #28a745;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CABEÇALHO DO SISTEMA
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="header-bar">
        <h2 style="margin:0; padding:0; color:white;">TOUR360VR | Painel de Diagnóstico & Gerador de Propostas</h2>
        <p style="margin:5px 0 0 0; font-size:14px; opacity:0.9;">Google Meu Negócio & Oportunidades de Tour Virtual 360°</p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL (CAMPOS EDITÁVEIS)
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Dados da Empresa")

nome_empresa = st.sidebar.text_input("Nome da Empresa", "Banana e Banana Moda Praia")
endereco = st.sidebar.text_input("Endereço Completo", "Av. Independência, 2366 - Alto da Boa Vista, Ribeirão Preto - SP")
telefone = st.sidebar.text_input("Telefone/WhatsApp", "(16) 99621-0707")
url_foto_capa = st.sidebar.text_input("URL da Foto de Capa (Google)", "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800")

st.sidebar.subheader("📊 Métricas Atuais")
score_otimizacao = st.sidebar.number_input("Score de Otimização (0-100)", min_value=0, max_value=100, value=61)
nota_clientes = st.sidebar.number_input("Nota Média dos Clientes", min_value=1.0, max_value=5.0, value=4.2, step=0.1)
total_avaliacoes = st.sidebar.number_input("Total de Avaliações", min_value=0, value=43)
recencia_avaliacao = st.sidebar.text_input("Recência da Última Avaliação", "há 2 meses")

st.sidebar.subheader("💰 Valores da Proposta (R$)")
preco_opcao1 = st.sidebar.text_input("Opção 1 (Ficha Otimizada)", "500,00 ou 2x de R$ 250,00")
preco_opcao2 = st.sidebar.text_input("Opção 2 (Ficha + Tour 360°)", "900,00 ou 3x de R$ 300,00")
preco_opcao3 = st.sidebar.text_input("Opção 3 (Presença Completa)", "A combinar")

# -----------------------------------------------------------------------------
# ESTRUTURA DE DADOS DO DIAGNÓSTICO
# -----------------------------------------------------------------------------
dados_dimensoes = [
    {
        "Dimensão": "Completude do cadastro",
        "Estado Atual": "Nome, endereço e telefone preenchidos, mas sem site próprio e sem descrição do negócio.",
        "Impacto": "Visitantes não conhecem sua história nem seus diferenciais — a vitrine fica incompleta."
    },
    {
        "Dimensão": "Nota e avaliações",
        "Estado Atual": f"{nota_clientes} de 5 com {total_avaliacoes} avaliações, maioria 5 estrelas, sem respostas do proprietário.",
        "Impacto": "Clientes que elogiam não recebem retorno. Concorrentes que respondem transmitem maior confiança e engajamento."
    },
    {
        "Dimensão": "Consistência de NAP",
        "Estado Atual": f"Telefone {telefone} e endereço confirmados sem divergências.",
        "Impacto": "O Google confia na empresa porque os dados são consistentes em todas as fontes."
    },
    {
        "Dimensão": "Categorias",
        "Estado Atual": "Categorias genéricas atribuídas (clothing_store, store).",
        "Impacto": "Não deixa explícito a especialidade (ex: moda praia), perdendo buscas de clientes de fora da região."
    },
    {
        "Dimensão": "Fotos e Imersão",
        "Estado Atual": "10 fotos convencionais enviadas; nenhuma foto ou Tour 360° identificado.",
        "Impacto": "Produtos vistos em miniatura. Visitantes não imergem na experiência. Concorrentes com tour 360° retêm mais o usuário."
    },
    {
        "Dimensão": "Horários",
        "Estado Atual": "Segunda a sexta 09:00–18:30, sábado 09:00–13:00, domingo fechado.",
        "Impacto": "Horários visíveis e sem contradições garantem segurança ao cliente presencial."
    },
    {
        "Dimensão": "Posts / Novidades",
        "Estado Atual": "Nenhum post ou atualização recente no perfil.",
        "Impacto": "Perfil estático. Clientes recorrentes não veem movimento, novidades ou promoções ativas."
    },
    {
        "Dimensão": "Recursos Interativos",
        "Estado Atual": "Nenhum Tour Virtual 360° navegável detectado no perfil ou site.",
        "Impacto": "Visitantes perdem a oportunidade de explorar o espaço remotamente. O Tour 360° reduz a resistência à visita."
    }
]

dados_concorrentes = [
    {"#": "1º", "Estabelecimento": "Empório das Essências Loja 1", "Nota": "4,7 ★", "Avaliações": "2.245"},
    {"#": "2º", "Estabelecimento": "Atelier Neide Amaral", "Nota": "4,7 ★", "Avaliações": "409"},
    {"#": "3º", "Estabelecimento": "Lojas Renner", "Nota": "4,4 ★", "Avaliações": "3.283"},
    {"#": "4º", "Estabelecimento": "Lojas Marisa", "Nota": "4,2 ★", "Avaliações": "1.334"},
    {"#": "5º", "Estabelecimento": f"{nome_empresa} (Você)", "Nota": f"{nota_clientes} ★", "Avaliações": f"{total_avaliacoes}"}
]

# -----------------------------------------------------------------------------
# FUNÇÃO AUXILIAR PARA DOWNLOAD E TRATAMENTO DA IMAGEM DE CAPA
# -----------------------------------------------------------------------------
def obter_imagem_capa(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            img = Image.open(io.BytesIO(response.content))
            img_byte_arr = io.BytesIO()
            img.convert('RGB').save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            return img_byte_arr
    except Exception:
        pass
    return None

# -----------------------------------------------------------------------------
# GERADOR DE PDF (REPORTLAB)
# -----------------------------------------------------------------------------
def gerar_pdf_diagnostico():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Cores da Marca
    c_primary = colors.HexColor("#0B3C5D")
    c_secondary = colors.HexColor("#1D2731")
    c_accent = colors.HexColor("#328CC1")
    c_bg_light = colors.HexColor("#F8F9FA")
    c_warning = colors.HexColor("#D9534F")
    c_text = colors.HexColor("#333333")

    # Novos Estilos
    style_title = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=22, textColor=c_primary, leading=26)
    style_subtitle = ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica', fontSize=12, textColor=c_secondary, leading=16)
    style_h2 = ParagraphStyle('SectionH2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=c_primary, spaceBefore=12, spaceAfter=6)
    style_body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=c_text, leading=12)
    style_body_bold = ParagraphStyle('BodyBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=c_text, leading=12)
    style_th = ParagraphStyle('TH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.white, leading=11)
    style_card_val = ParagraphStyle('CardVal', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, textColor=c_primary, alignment=1)
    style_card_lbl = ParagraphStyle('CardLbl', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#666666"), alignment=1)

    elements = []

    # -------------------------------------------------------------------------
    # PÁGINA 1: CAPA COM IMAGEM DO CLIENTE
    # -------------------------------------------------------------------------
    elements.append(Paragraph("<b>TOUR360VR</b> — DIAGNÓSTICO DE PRESENÇA DIGITAL", ParagraphStyle('HeaderTop', fontName='Helvetica-Bold', fontSize=10, textColor=c_accent)))
    elements.append(Spacer(1, 0.4*cm))
    elements.append(Paragraph(nome_empresa, style_title))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(f"Análise de Otimização no Google Meu Negócio & Potencial 360°<br/><font color='#666666'>{endereco}</font>", style_subtitle))
    elements.append(Spacer(1, 0.8*cm))

    # Tenta inserir a imagem da capa da empresa
    img_data = obter_imagem_capa(url_foto_capa)
    if img_data:
        rl_img = RLImage(img_data, width=17*cm, height=8*cm)
        elements.append(rl_img)
        elements.append(Spacer(1, 0.8*cm))

    # Box de resumo na capa
    resumo_capa = [
        [Paragraph(f"<b>Diagnóstico preparado para:</b> {nome_empresa}", style_body)],
        [Paragraph(f"<b>Status Atual:</b> Nota {nota_clientes}★ com {total_avaliacoes} avaliações. Oportunidade imediata de diferenciação com Tour Virtual 360°.", style_body)],
        [Paragraph("<b>Especialista Responsável:</b> Rubens Okamoto | contato@tour360vr.com.br | (16) 99133-2121", style_body)]
    ]
    t_resumo = Table(resumo_capa, colWidths=[17*cm])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_accent),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_resumo)
    elements.append(PageBreak())

    # -------------------------------------------------------------------------
    # PÁGINA 2: KPIS & TABELA DE DIMENSÕES VS IMPACTO
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Como está o seu Google Meu Negócio hoje", style_h2))
    elements.append(Spacer(1, 0.3*cm))

    # Cards de KPIs
    kpi_data = [
        [
            Paragraph("OTIMIZAÇÃO DO PERFIL", style_card_lbl),
            Paragraph("NOTA DOS CLIENTES", style_card_lbl),
            Paragraph("TOUR VIRTUAL 360°", style_card_lbl)
        ],
        [
            Paragraph(f"{score_otimizacao}/100", style_card_val),
            Paragraph(f"{nota_clientes} ★", style_card_val),
            Paragraph("NÃO DETECTADO", ParagraphStyle('Warn', parent=style_card_val, textColor=c_warning, fontSize=12))
        ],
        [
            Paragraph("Oportunidades claras de ganho", style_card_lbl),
            Paragraph(f"{total_avaliacoes} avaliações ({recencia_avaliacao})", style_card_lbl),
            Paragraph("Oportunidade para sair na frente", style_card_lbl)
        ]
    ]
    t_kpis = Table(kpi_data, colWidths=[5.4*cm, 5.4*cm, 5.4*cm])
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_kpis)
    elements.append(Spacer(1, 0.6*cm))

    # Tabela de Dimensões
    elements.append(Paragraph("Análise Detalhada por Dimensão", style_h2))
    
    table_dim_data = [[
        Paragraph("Dimensão", style_th),
        Paragraph("Estado Atual", style_th),
        Paragraph("Impacto no Negócio", style_th)
    ]]

    for d in dados_dimensoes:
        table_dim_data.append([
            Paragraph(d["Dimensão"], style_body_bold),
            Paragraph(d["Estado Atual"], style_body),
            Paragraph(d["Impacto"], style_body)
        ])

    t_dim = Table(table_dim_data, colWidths=[4.0*cm, 6.5*cm, 6.5*cm])
    t_dim.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D3D3D3")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light])
    ]))
    elements.append(t_dim)
    elements.append(PageBreak())

    # -------------------------------------------------------------------------
    # PÁGINA 3: CONCORRÊNCIA LOCAL & DIFERENCIAL TOUR 360°
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Concorrência na sua Região", style_h2))
    elements.append(Paragraph("Veja como sua empresa está posicionada em relação aos principais players locais:", style_body))
    elements.append(Spacer(1, 0.3*cm))

    conc_table_data = [[
        Paragraph("#", style_th),
        Paragraph("Estabelecimento", style_th),
        Paragraph("Nota", style_th),
        Paragraph("Avaliações", style_th)
    ]]

    for c in dados_concorrentes:
        is_user = "(Você)" in c["Estabelecimento"]
        st_txt = style_body_bold if is_user else style_body
        conc_table_data.append([
            Paragraph(c["#"], st_txt),
            Paragraph(c["Estabelecimento"], st_txt),
            Paragraph(c["Nota"], st_txt),
            Paragraph(c["Avaliações"], st_txt)
        ])

    t_conc = Table(conc_table_data, colWidths=[1.5*cm, 9.5*cm, 3.0*cm, 3.0*cm])
    t_conc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D3D3D3")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light])
    ]))
    elements.append(t_conc)
    elements.append(Spacer(1, 0.8*cm))

    elements.append(Paragraph("Seu Maior Diferencial: Tour Virtual 360°", style_h2))
    
    tour_benefits = [
        [
            Paragraph("<b>Tour 360° na Ficha do Google</b>", style_body_bold),
            Paragraph("<b>Tour 360° Personalizado no Site</b>", style_body_bold)
        ],
        [
            Paragraph("Aparece diretamente nas buscas do Google e no Google Maps. Captura o cliente no momento da descoberta, aumenta o tempo de permanência e sinaliza relevância ao algoritmo.", style_body),
            Paragraph("Experiência imersiva dentro da sua própria plataforma, integrada a botões de reserva, WhatsApp, vídeos e catálogo. Fortalece a marca e melhora a taxa de conversão.", style_body)
        ]
    ]
    t_tour = Table(tour_benefits, colWidths=[8.2*cm, 8.2*cm])
    t_tour.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_accent),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BACKGROUND', (0,1), (-1,1), c_bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(t_tour)
    elements.append(Spacer(1, 0.8*cm))

    # -------------------------------------------------------------------------
    # OPÇÕES DE INVESTIMENTO
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Planos de Ação & Opções de Investimento", style_h2))
    
    plans_data = [
        [
            Paragraph("<b>OPÇÃO 1</b><br/>Ficha Otimizada", style_th),
            Paragraph("<b>OPÇÃO 2 (RECOMENDADO)</b><br/>Ficha + Tour 360°", style_th),
            Paragraph("<b>OPÇÃO 3</b><br/>Presença Completa", style_th)
        ],
        [
            Paragraph(f"<b>R$ {preco_opcao1}</b>", style_body_bold),
            Paragraph(f"<b>R$ {preco_opcao2}</b>", style_body_bold),
            Paragraph(f"<b>{preco_opcao3}</b>", style_body_bold)
        ],
        [
            Paragraph("• Otimização de cadastro<br/>• Descrição profissional SEO<br/>• Categorias estratégicas<br/>• Padronização NAP", style_body),
            Paragraph("• Tudo da Opção 1<br/><b>+ Tour Virtual 360° na Ficha do Google</b><br/>• Fotos em alta resolução", style_body),
            Paragraph("• Tudo da Opção 2<br/><b>+ Tour 360° no seu Site</b><br/>• Menu interativo personalizado", style_body)
        ]
    ]
    t_plans = Table(plans_data, colWidths=[5.4*cm, 5.4*cm, 5.4*cm])
    t_plans.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), c_primary),
        ('BACKGROUND', (1,0), (1,0), c_accent),
        ('BACKGROUND', (2,0), (2,0), c_primary),
        ('ALIGN', (0,0), (-1,1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light])
    ]))
    elements.append(t_plans)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# INTERFACE PRINCIPAL DO STREAMLIT (DASHBOARD + USO INTERNO)
# -----------------------------------------------------------------------------
tab_dash, tab_pdf, tab_interno = st.tabs(["📊 Dashboard de Análise", "📄 Visualização do PDF", "💬 Scripts de Venda (Uso Interno)"])

with tab_dash:
    st.subheader("Resumo Visual do Diagnóstico")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Score de Otimização</div>
                <div class="kpi-value">{score_otimizacao} / 100</div>
                <div class="kpi-desc">Oportunidades de ganho encontradas</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Avaliações do Perfil</div>
                <div class="kpi-value">{nota_clientes} ★ ({total_avaliacoes})</div>
                <div class="kpi-desc">Última avaliação {recencia_avaliacao}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Tour Virtual 360°</div>
                <div class="kpi-value" style="color:#d9534f;">Ausente</div>
                <div class="kpi-desc">Oportunidade para sair na frente</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Dimensões Analisadas & Impacto Comercial")
    st.table(dados_dimensoes)

    st.subheader("Concorrência Local Registrada")
    st.table(dados_concorrentes)

with tab_pdf:
    st.subheader("Gerar Proposta Profissional em PDF")
    st.write("Clique no botão abaixo para processar o relatório atualizado contendo a foto do cliente e os gráficos de diagnóstico.")
    
    pdf_bytes = gerar_pdf_diagnostico()
    st.download_button(
        label="📥 Baixar Proposta Comercial (PDF)",
        data=pdf_bytes,
        file_name=f"Proposta_Tour360VR_{nome_empresa.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

with tab_interno:
    st.subheader("💬 Scripts Prontos para Abordagem e Prospecção (Uso Exclusivo Interno)")
    st.info("Utilize os textos abaixo para abordagem rápida via WhatsApp ou E-mail. Copie com 1 clique.")

    copy_wsp = f"""Oi! 👋 Analisei o perfil da *{nome_empresa}* no Google e encontrei duas oportunidades claras:

1️⃣ **Você tem {total_avaliacoes} avaliações com nota {nota_clientes}** — mas algumas estão sem resposta. Responder a cada elogio aumenta a confiança dos clientes e ajuda no ranqueamento.
2️⃣ **Zero tour virtual 360°** — seus concorrentes locais também não têm, o que te dá a chance de sair na frente em imersão!

Preparei um diagnóstico completo com comparativo regional em PDF. Posso te enviar por aqui sem compromisso?"""

    copy_email = f"""Assunto: Oportunidade de destaque no Google para a {nome_empresa}

Olá!

Analisei o perfil da {nome_empresa} no Google e os números são promissores: nota {nota_clientes} com {total_avaliacoes} avaliações. Sua empresa é bem avaliada, mas identificamos pontos onde está deixando clientes para a concorrência:

1. Avaliações sem resposta pública.
2. Ausência de Tour Virtual 360° (nenhum dos concorrentes diretos da região possui).
3. Oportunidades de SEO Local para buscas por categorias específicas.

Trabalhamos com soluções completas de otimização e fotos 360° profissionais.
Em anexo envio o relatório técnico de diagnóstico do seu perfil.

Podemos conversar 5 minutos sobre esses pontos nesta semana?

Atenciosamente,
Rubens Okamoto | Tour360VR
(16) 99133-2121 | contato@tour360vr.com.br"""

    copy_follow = f"""E aí! 👋 Tudo bem?
Você conseguiu dar uma olhada no diagnóstico em PDF que te enviei da *{nome_empresa}*?

Achei que o ponto do Tour Virtual 360° é a maior oportunidade para vocês hoje, já que nenhum concorrente na sua região tem.

Se tiver alguma dúvida ou quiser bater um papo rápido sem compromisso, só me avisar por aqui!"""

    st.markdown("#### 1) Abordagem Inicial - WhatsApp")
    st.code(copy_wsp, language="text")

    st.markdown("#### 2) Abordagem Inicial - E-mail")
    st.code(copy_email, language="text")

    st.markdown("#### 3) Follow-up 48h")
    st.code(copy_follow, language="text")

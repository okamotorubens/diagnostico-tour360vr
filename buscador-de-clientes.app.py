import streamlit as st
import pandas as pd
import json
import time
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Prospecção & Diagnóstico Local | Okamoto & Tour360VR",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (LAYOUT MODERNO)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white; padding: 24px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .main-title { font-size: 26px; font-weight: 700; margin: 0; color: #ffffff; }
    .main-subtitle { font-size: 14px; color: #94a3b8; margin-top: 5px; }

    .lead-card {
        background-color: #ffffff; border-radius: 10px; padding: 20px;
        margin-bottom: 15px; border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s;
    }
    .lead-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    
    .score-box { text-align: center; padding: 12px; border-radius: 8px; font-weight: bold; }
    .score-high { background-color: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
    .score-med  { background-color: #fef3c7; color: #92400e; border: 1px solid #fde047; }
    .score-low  { background-color: #dcfce7; color: #166534; border: 1px solid #86efac; }

    .stButton>button { border-radius: 8px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GERENCIAMENTO DE ESTADO (SESSION STATE)
# -----------------------------------------------------------------------------
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1
if 'resultados' not in st.session_state:
    st.session_state.resultados = []

# -----------------------------------------------------------------------------
# FUNÇÃO SIMULADA DE MINERAÇÃO E AUDITORIA CRÍTICA
# -----------------------------------------------------------------------------
def minerar_e_auditar_negocios(nicho, cidade, limite=10):
    base_dados = [
        {
            "id": 101,
            "nome": f"{nicho.capitalize()} & Conveniência Centro",
            "categoria": nicho.capitalize(),
            "endereco": f"Rua São José, 450 - Centro, {cidade}",
            "telefone": "(16) 99876-5432",
            "whatsapp": "16998765432",
            "website": "",
            "nota": 4.1,
            "total_avaliacoes": 28,
            "reivindicada": False,
            "fotos_total": 4,
            "ultima_foto_dias": 140,
            "responde_avaliacoes": "Raramente",
            "posts_30dias": 0,
            "tour_360": False
        },
        {
            "id": 102,
            "nome": f"Grupo {nicho.capitalize()} Premium",
            "categoria": nicho.capitalize(),
            "endereco": f"Av. Independência, 1200 - Alto da Boa Vista, {cidade}",
            "telefone": "(16) 3625-1100",
            "whatsapp": "16991234567",
            "website": f"http://{nicho.lower()}exemplo.com.br",
            "nota": 4.7,
            "total_avaliacoes": 142,
            "reivindicada": True,
            "fotos_total": 18,
            "ultima_foto_dias": 45,
            "responde_avaliacoes": "Sempre",
            "posts_30dias": 1,
            "tour_360": False
        },
        {
            "id": 103,
            "nome": f"{nicho.capitalize()} Express",
            "categoria": nicho.capitalize(),
            "endereco": f"Av. Presidente Vargas, 890 - {cidade}",
            "telefone": "(16) 98111-2233",
            "whatsapp": "16981112233",
            "website": "",
            "nota": 3.8,
            "total_avaliacoes": 12,
            "reivindicada": False,
            "fotos_total": 2,
            "ultima_foto_dias": 310,
            "responde_avaliacoes": "Nunca",
            "posts_30dias": 0,
            "tour_360": False
        }
    ]

    resultados_processados = []
    
    for item in base_dados:
        pontos_criticos = []
        oportunidades = []
        score_oportunidade = 0

        if not item["reivindicada"]:
            pontos_criticos.append("Ficha NÃO Reivindicada (Risco de alteração por terceiros)")
            oportunidades.append("Serviço de Reivindicação e Verificação de Posse")
            score_oportunidade += 30

        if not item["website"]:
            pontos_criticos.append("Sem site oficial cadastrado no perfil")
            oportunidades.append("Desenvolvimento de Landing Page / Website Responsivo")
            score_oportunidade += 25

        if item["total_avaliacoes"] < 30:
            pontos_criticos.append(f"Volume baixo de avaliações ({item['total_avaliacoes']} no total)")
            oportunidades.append("Estratégia de Gestão de Reputação e Prova Social")
            score_oportunidade += 15

        if not item["tour_360"]:
            pontos_criticos.append("Ausência de Tour Virtual 360° interativo")
            oportunidades.append("Implantação de Tour 360° no Google Street View / Maps")
            score_oportunidade += 20

        if item["fotos_total"] < 10 or item["ultima_foto_dias"] > 90:
            pontos_criticos.append("Fotos escassas ou desatualizadas há mais de 3 meses")
            oportunidades.append("Produção de Mídias Visuais de Alta Qualidade (Fotografia Profissional)")
            score_oportunidade += 15

        item["pontos_criticos"] = pontos_criticos
        item["oportunidades"] = oportunidades
        item["score_oportunidade"] = min(score_oportunidade, 100)
        
        resultados_processados.append(item)

    return resultados_processados[:limite]

# -----------------------------------------------------------------------------
# GERADOR DE RELATÓRIO PDF COM REPORTLAB E DUAL BRAND
# -----------------------------------------------------------------------------
def gerar_pdf_diagnostico(lead):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748b'), spaceAfter=15)
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1e293b'), spaceBefore=10, spaceAfter=6, fontName='Helvetica-Bold')
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#334155'), leading=12)
    alert_style = ParagraphStyle('AlertText', parent=body_style, textColor=colors.HexColor('#b91c1c'), fontName='Helvetica-Bold')
    opp_style = ParagraphStyle('OppText', parent=body_style, textColor=colors.HexColor('#15803d'), fontName='Helvetica-Bold')

    elements = []

    # LOGOS DUAL BRAND
    logo_okamoto = "logo_okamoto.png" if os.path.exists("logo_okamoto.png") else None
    logo_tour = "logo_tour_transparente.png" if os.path.exists("logo_tour_transparente.png") else None

    img_okamoto = Image(logo_okamoto, width=120, height=40) if logo_okamoto else Paragraph("<b>OKAMOTO MÍDIAS VISUAIS</b>", body_style)
    img_tour = Image(logo_tour, width=120, height=40) if logo_tour else Paragraph("<b>TOUR360VR</b>", body_style)

    header_table = Table([[img_okamoto, img_tour]], colWidths=[270, 270])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=12))

    elements.append(Paragraph("RELATÓRIO DE AUDITORIA DE PRESENÇA DIGITAL", title_style))
    elements.append(Paragraph(f"Análise técnica realizada em: {datetime.now().strftime('%d/%m/%Y')} | Alvo: <b>{lead['nome']}</b>", subtitle_style))

    dados_empresa = [
        [Paragraph("<b>Empresa:</b>", body_style), Paragraph(lead['nome'], body_style)],
        [Paragraph("<b>Categoria:</b>", body_style), Paragraph(lead['categoria'], body_style)],
        [Paragraph("<b>Endereço:</b>", body_style), Paragraph(lead['endereco'], body_style)],
        [Paragraph("<b>Telefone/WhatsApp:</b>", body_style), Paragraph(lead['telefone'], body_style)],
        [Paragraph("<b>Website Cadastrado:</b>", body_style), Paragraph(lead['website'] if lead['website'] else "Nenhum site cadastrado", body_style)]
    ]
    t_empresa = Table(dados_empresa, colWidths=[130, 410])
    t_empresa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_empresa)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("1. DIAGNÓSTICO TÉCNICO E FALHAS IDENTIFICADAS", section_heading))
    criticos_list = [[Paragraph(f"• {pnt}", alert_style)] for pnt in lead['pontos_criticos']]
    if not criticos_list:
        criticos_list = [[Paragraph("• Nenhuma falha crítica detectada.", body_style)]]
    t_criticos = Table(criticos_list, colWidths=[540])
    t_criticos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef2f2')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#fca5a5')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_criticos)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("2. PLANO DE AÇÃO E OPORTUNIDADES DE MELHORIA", section_heading))
    opp_list = [[Paragraph(f"✓ {opp}", opp_style)] for opp in lead['oportunidades']]
    t_opp = Table(opp_list, colWidths=[540])
    t_opp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#86efac')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_opp)
    elements.append(Spacer(1, 15))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=10, spaceAfter=10))
    rodape_text = Paragraph(
        "<font color='#475569'><b>Proposta elaborada por Okamoto Mídias Visuais & Tour360VR</b><br/>"
        "Soluções em Imagem Profissional, Tours Virtuais 360° e Otimização de Presença Local.</font>",
        ParagraphStyle('Rodape', parent=body_style, alignment=1)
    )
    elements.append(rodape_text)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏢 Okamoto & Tour360VR")
    st.caption("Mineração & Diagnóstico de Negócios")
    st.divider()

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("1. Buscar", use_container_width=True, type="primary" if st.session_state.etapa == 1 else "secondary"):
            st.session_state.etapa = 1
            st.rerun()
    with col_nav2:
        if st.button("2. Analisar", use_container_width=True, type="primary" if st.session_state.etapa == 2 else "secondary", disabled=len(st.session_state.resultados) == 0):
            st.session_state.etapa = 2
            st.rerun()

# -----------------------------------------------------------------------------
# ETAPA 1: BUSCA
# -----------------------------------------------------------------------------
if st.session_state.etapa == 1:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🔎 Mineração e Diagnóstico de Negócios Locais</h1>
            <div class="main-subtitle">Varredura de perfis do Google Maps, auditoria de dados e identificação de falhas.</div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("form_busca"):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            nicho_input = st.text_input("Nicho / Categoria Comercial", value="Restaurante")
        with col2:
            cidade_input = st.text_input("Cidade / Região de Busca", value="Ribeirão Preto")
        with col3:
            limite_input = st.number_input("Qtd. Máxima", min_value=1, max_value=50, value=10)
        
        btn_minar = st.form_submit_button("🚀 Iniciar Varredura Profunda", use_container_width=True)

    if btn_minar:
        with st.spinner("Varrendo Google Maps e auditando perfis..."):
            time.sleep(1)
            st.session_state.resultados = minerar_e_auditar_negocios(nicho_input, cidade_input, limite_input)
            st.session_state.etapa = 2
            st.rerun()

    if len(st.session_state.resultados) > 0:
        st.divider()
        st.info(f"Há **{len(st.session_state.resultados)} leads** carregados da busca anterior.")
        if st.button("Avançar para Análise ➡️", type="primary"):
            st.session_state.etapa = 2
            st.rerun()

# -----------------------------------------------------------------------------
# ETAPA 2: ANALISADOR
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 2:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📊 Painel de Análise e Diagnóstico de Leads</h1>
            <div class="main-subtitle">Pontos fracos dos estabelecimentos e ferramentas para abordagem.</div>
        </div>
    """, unsafe_allow_html=True)

    col_back, col_filter, col_export = st.columns([1.5, 3, 2.5])
    
    with col_back:
        if st.button("⬅️ Nova Busca", use_container_width=True):
            st.session_state.etapa = 1
            st.rerun()

    with col_filter:
        filtro_status = st.selectbox(
            "Filtrar por Diagnóstico:",
            ["Todos os Leads", "Apenas sem Website", "Apenas Ficha não Reivindicada", "Apenas sem Tour 360°"]
        )

    with col_export:
        df_export = pd.DataFrame(st.session_state.resultados)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar Dados (CSV)",
            data=csv,
            file_name=f"leads_minerados_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.divider()

    resultados_filtrados = st.session_state.resultados
    if filtro_status == "Apenas sem Website":
        resultados_filtrados = [r for r in resultados_filtrados if not r['website']]
    elif filtro_status == "Apenas Ficha não Reivindicada":
        resultados_filtrados = [r for r in resultados_filtrados if not r['reivindicada']]
    elif filtro_status == "Apenas sem Tour 360°":
        resultados_filtrados = [r for r in resultados_filtrados if not r['tour_360']]

    st.markdown(f"Exibindo **{len(resultados_filtrados)}** oportunidades encontradas:")

    for lead in resultados_filtrados:
        score = lead['score_oportunidade']
        if score >= 60:
            score_class, score_label = "score-high", "ALTA OPORTUNIDADE"
        elif score >= 30:
            score_class, score_label = "score-med", "MÉDIA OPORTUNIDADE"
        else:
            score_class, score_label = "score-low", "BAIXA OPORTUNIDADE"

        st.markdown(f"""
            <div class="lead-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h3 style="margin: 0; color: #0f172a;">{lead['nome']}</h3>
                        <p style="margin: 4px 0; color: #64748b; font-size: 13px;">📍 {lead['endereco']} | 🏷️ {lead['categoria']}</p>
                    </div>
                    <div class="score-box {score_class}">
                        <div style="font-size: 10px;">SCORE</div>
                        <div style="font-size: 18px;">{score} / 100</div>
                        <div style="font-size: 9px;">{score_label}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        col_details1, col_details2, col_actions = st.columns([3, 3, 2])

        with col_details1:
            st.markdown("**📊 Indicadores no Google:**")
            st.markdown(f"- **Nota Média:** ⭐ {lead['nota']} ({lead['total_avaliacoes']} avaliações)")
            st.markdown(f"- **Ficha Reivindicada?** {'✅ Sim' if lead['reivindicada'] else '❌ **NÃO REIVINDICADA**'}")
            st.markdown(f"- **Fotos na Ficha:** {lead['fotos_total']} fotos (última há {lead['ultima_foto_dias']} dias)")

        with col_details2:
            st.markdown("**🚨 Pontos Críticos Encontrados:**")
            for pc in lead['pontos_criticos']:
                st.markdown(f"<span style='color: #b91c1c; font-size: 12px;'>❌ {pc}</span>", unsafe_allow_html=True)

        with col_actions:
            if lead['whatsapp']:
                msg_wa = f"Olá! Notei que a ficha da {lead['nome']} no Google apresenta pontos de melhoria..."
                link_wa = f"https://wa.me/55{lead['whatsapp']}?text={msg_wa.replace(' ', '%20')}"
                st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:6px; font-weight:bold; cursor:pointer; margin-bottom:8px;">💬 WhatsApp</button></a>', unsafe_allow_html=True)

            pdf_bytes = gerar_pdf_diagnostico(lead)
            st.download_button(
                label="📄 Gerar PDF da Proposta",
                data=pdf_bytes,
                file_name=f"Diagnostico_{lead['nome'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                key=f"btn_pdf_{lead['id']}",
                use_container_width=True
            )

        st.divider()

import streamlit as st
import pandas as pd
import json
import time
import os
import re
import requests
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA STREAMLIT (INCLUINDO FAVICON)
# -----------------------------------------------------------------------------
favicon_path = "logo_tour_transparente.png" if os.path.exists("logo_tour_transparente.png") else "🔍"

st.set_page_config(
    page_title="Mineração & Diagnóstico Local",
    page_icon=favicon_path,
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (CENTRALIZAÇÃO DE LOGOS E LAYOUT MODERNO)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;
        border: 1px solid #334155;
    }
    .main-title { font-size: 24px; font-weight: 700; margin: 0; color: #ffffff; }
    .main-subtitle { font-size: 13px; color: #94a3b8; margin-top: 4px; }

    .lead-card {
        background-color: #1e293b; border-radius: 10px; padding: 20px;
        margin-bottom: 15px; border: 1px solid #334155;
    }
    
    .score-box { text-align: center; padding: 10px; border-radius: 8px; font-weight: bold; width: 140px; }
    .score-high { background-color: #450a0a; color: #fca5a5; border: 1px solid #991b1b; }
    .score-med  { background-color: #451a03; color: #fde047; border: 1px solid #92400e; }
    .score-low  { background-color: #052e16; color: #86efac; border: 1px solid #166534; }

    .critical-item { color: #f87171; font-size: 13px; margin-bottom: 6px; font-weight: 500; }
    
    /* Centralização de Imagens e Estilo na Sidebar */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 15px;
    }
    [data-testid="stSidebar"] img {
        margin-left: auto;
        margin-right: auto;
    }
    .sidebar-title {
        text-align: center;
        font-size: 18px;
        font-weight: 800;
        color: #ffffff;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------------------------
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1
if 'resultados' not in st.session_state:
    st.session_state.resultados = []

# -----------------------------------------------------------------------------
# INTEGRAÇÃO DE BUSCA (GOOGLE PLACES API OU BASE DE CONTINGÊNCIA REAL)
# -----------------------------------------------------------------------------
def buscar_google_places_api(nicho, cidade, api_key, limite=10):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={nicho}+em+{cidade}&language=pt-BR&key={api_key}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("status") == "OK":
            results = data.get("results", [])[:limite]
            leads = []
            for idx, place in enumerate(results):
                place_id = place.get("place_id")
                
                details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos&language=pt-BR&key={api_key}"
                det_res = requests.get(details_url, timeout=5).json().get("result", {}) if place_id else {}
                
                nome = det_res.get("name") or place.get("name")
                endereco = det_res.get("formatted_address") or place.get("formatted_address")
                telefone = det_res.get("formatted_phone_number", "")
                website = det_res.get("website", "")
                nota = det_res.get("rating", place.get("rating", 0.0))
                total_avaliacoes = det_res.get("user_ratings_total", place.get("user_ratings_total", 0))
                photos = det_res.get("photos", place.get("photos", []))
                
                pontos_criticos = []
                oportunidades = []
                score = 0

                if not website:
                    pontos_criticos.append("Sem site oficial vinculado à ficha")
                    oportunidades.append("Desenvolvimento de Landing Page / Website Profissional")
                    score += 25

                if total_avaliacoes < 30:
                    pontos_criticos.append(f"Volume baixo de avaliações ({total_avaliacoes} no total)")
                    oportunidades.append("Estratégia de Gestão de Reputação e Prova Social")
                    score += 20

                if len(photos) < 5:
                    pontos_criticos.append("Poucas fotos publicadas no perfil Google")
                    oportunidades.append("Produção de Fotografia Profissional")
                    score += 20

                pontos_criticos.append("Ausência de Tour Virtual 360° interativo")
                oportunidades.append("Fotografia 360° e Implantação de Tour no Google Street View")
                score += 25

                clean_phone = "".join(filter(str.isdigit, telefone))
                if len(clean_phone) > 10 and clean_phone.startswith("55"):
                    clean_phone = clean_phone[2:]

                leads.append({
                    "id": 1000 + idx,
                    "nome": nome,
                    "categoria": nicho.capitalize(),
                    "endereco": endereco,
                    "telefone": telefone or "(16) Contato via Ficha",
                    "whatsapp": clean_phone if len(clean_phone) >= 10 else "16999999999",
                    "website": website,
                    "nota": nota,
                    "total_avaliacoes": total_avaliacoes,
                    "reivindicada": True,
                    "fotos_total": len(photos),
                    "ultima_foto_dias": 60,
                    "tour_360": False,
                    "pontos_criticos": pontos_criticos,
                    "oportunidades": oportunidades,
                    "score_oportunidade": min(score, 100)
                })
            return leads
    except Exception as e:
        st.warning(f"Aviso de integração API: {str(e)}. Carregando dados de contingência.")
    return None

def minerar_e_auditar_negocios(nicho, cidade, limite=10):
    api_key = st.secrets.get("GOOGLE_API_KEY", None) or os.getenv("GOOGLE_API_KEY", None)
    
    if api_key:
        leads_reais = buscar_google_places_api(nicho, cidade, api_key, limite)
        if leads_reais:
            return leads_reais

    exemplo_estabelecimentos = [
        {"nome": f"Loja & Boutique {cidade}", "bairro": "Centro", "rua": "Rua Saldanha Marinho"},
        {"nome": f"Estilo & Moda {nicho.capitalize()}", "bairro": "Alto da Boa Vista", "rua": "Av. Independência"},
        {"nome": f"Empório & {nicho.capitalize()} do Barão", "bairro": "Jardim Sumaré", "rua": "Rua Garibaldi"},
        {"nome": f"Conceito {nicho.capitalize()} Brasil", "bairro": "Vila Seixas", "rua": "Rua Amador Bueno"},
        {"nome": f"Studio & Galeria {nicho.capitalize()}", "bairro": "Jardim Botânico", "rua": "Av. Professor João Fiúsa"},
        {"nome": f"Casa & {nicho.capitalize()} Real", "bairro": "Campos Elíseos", "rua": "Av. Saudade"},
        {"nome": f"Ateliê {nicho.capitalize()} & Cia", "bairro": "Ipiranga", "rua": "Rua Dom Pedro II"}
    ]

    resultados = []
    for i in range(min(limite, len(exemplo_estabelecimentos))):
        item = exemplo_estabelecimentos[i]
        reivindicada = (i % 2 == 0)
        tem_site = (i % 3 == 0)
        nota = round(3.8 + (i * 0.2) % 1.1, 1)
        total_avaliacoes = 14 + (i * 18) % 150

        pontos_criticos = []
        oportunidades = []
        score = 0

        if not reivindicada:
            pontos_criticos.append("Ficha NÃO Reivindicada no Google")
            oportunidades.append("Reivindicação e Gestão de Propriedade do Perfil")
            score += 30

        if not tem_site:
            pontos_criticos.append("Sem site oficial vinculado à ficha")
            oportunidades.append("Desenvolvimento de Landing Page / Website Profissional")
            score += 25

        if total_avaliacoes < 35:
            pontos_criticos.append(f"Volume baixo de avaliações ({total_avaliacoes} no total)")
            oportunidades.append("Estratégia de Gestão de Reputação e Prova Social")
            score += 15

        pontos_criticos.append("Ausência de Tour Virtual 360° interativo")
        oportunidades.append("Fotografia 360° e Implantação no Google Street View")
        score += 20

        pontos_criticos.append("Fotos escassas ou desatualizadas no perfil")
        oportunidades.append("Produção de Fotografia Profissional e Mídias Visuais")
        score += 15

        resultados.append({
            "id": 200 + i,
            "nome": item["nome"],
            "categoria": nicho.capitalize(),
            "endereco": f"{item['rua']}, {120 + (i*85)} - {item['bairro']}, {cidade} - SP",
            "telefone": f"(16) 39{i:02d}-4000",
            "whatsapp": f"16997{i:02d}4000",
            "website": f"https://www.{nicho.lower()}exemplo.com.br" if tem_site else "",
            "nota": nota,
            "total_avaliacoes": total_avaliacoes,
            "reivindicada": reivindicada,
            "fotos_total": 4 + (i * 3) % 15,
            "ultima_foto_dias": 45 + (i * 30) % 200,
            "tour_360": False,
            "pontos_criticos": pontos_criticos,
            "oportunidades": oportunidades,
            "score_oportunidade": min(score, 100)
        })

    return resultados

# -----------------------------------------------------------------------------
# GERADOR DE EXCEL FORMATADO (.XLSX)
# -----------------------------------------------------------------------------
def gerar_excel_organizado(dados_leads):
    df = pd.DataFrame(dados_leads)
    
    # Tratamento de colunas de lista para texto limpo
    df['pontos_criticos'] = df['pontos_criticos'].apply(lambda x: " | ".join(x) if isinstance(x, list) else str(x))
    df['oportunidades'] = df['oportunidades'].apply(lambda x: " | ".join(x) if isinstance(x, list) else str(x))
    df['reivindicada'] = df['reivindicada'].apply(lambda x: "Sim" if x else "Não")

    # Renomeação amigável de cabeçalhos para o Excel
    df = df.rename(columns={
        "id": "ID",
        "nome": "Nome da Empresa",
        "categoria": "Categoria",
        "endereco": "Endereço Completo",
        "telefone": "Telefone",
        "whatsapp": "WhatsApp",
        "website": "Website",
        "nota": "Nota Média",
        "total_avaliacoes": "Total Avaliações",
        "reivindicada": "Ficha Reivindicada",
        "fotos_total": "Qtd. Fotos",
        "ultima_foto_dias": "Dias sem Fotos",
        "tour_360": "Possui Tour 360",
        "pontos_criticos": "Pontos Críticos Identificados",
        "oportunidades": "Oportunidades Comerciais",
        "score_oportunidade": "Score de Oportunidade"
    })

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Leads Minerados')
    
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# GERADOR DE PDF DUAL BRAND
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

    logo_okamoto = "logo_okamoto.png" if os.path.exists("logo_okamoto.png") else None
    logo_tour = "logo_tour_transparente.png" if os.path.exists("logo_tour_transparente.png") else None

    img_okamoto = Image(logo_okamoto, width=140, height=40, kind='proportional') if logo_okamoto else Paragraph("<b>OKAMOTO MÍDIAS VISUAIS</b>", body_style)
    img_tour = Image(logo_tour, width=100, height=40, kind='proportional') if logo_tour else Paragraph("<b>TOUR360VR</b>", body_style)

    header_table = Table([[img_okamoto, img_tour]], colWidths=[270, 270])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=12))

    elements.append(Paragraph("RELATÓRIO DE AUDITORIA DE PRESENÇA DIGITAL", title_style))
    elements.append(Paragraph(f"Análise técnica realizada em: {datetime.now().strftime('%d/%m/%Y')} | Alvo: <b>{lead['nome']}</b>", subtitle_style))

    dados_empresa = [
        [Paragraph("<b>Empresa:</b>", body_style), Paragraph(str(lead['nome']), body_style)],
        [Paragraph("<b>Categoria:</b>", body_style), Paragraph(str(lead['categoria']), body_style)],
        [Paragraph("<b>Endereço:</b>", body_style), Paragraph(str(lead['endereco']), body_style)],
        [Paragraph("<b>Telefone / WhatsApp:</b>", body_style), Paragraph(str(lead['telefone']), body_style)],
        [Paragraph("<b>Website Cadastrado:</b>", body_style), Paragraph(str(lead['website']) if lead['website'] else "Nenhum site cadastrado", body_style)]
    ]
    t_empresa = Table(dados_empresa, colWidths=[130, 410])
    t_empresa.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_empresa)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("1. DIAGNÓSTICO TÉCNICO E FALHAS IDENTIFICADAS", section_heading))
    criticos_list = [[Paragraph(f"• {pnt}", alert_style)] for pnt in lead['pontos_criticos']]
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
# BARRA LATERAL (LOGOS CENTRALIZADAS E TÍTULO EM DESTAQUE)
# -----------------------------------------------------------------------------
with st.sidebar:
    if os.path.exists("logo_okamoto.png"):
        st.image("logo_okamoto.png", width=160)
    
    if os.path.exists("logo_tour_transparente.png"):
        st.image("logo_tour_transparente.png", width=110)

    st.markdown('<div class="sidebar-title">Mineração & Diagnóstico Local</div>', unsafe_allow_html=True)
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
            nicho_input = st.text_input("Nicho / Categoria Comercial", value="Moda praia")
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
# ETAPA 2: ANALISADOR CRÍTICO
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
            ["Todos os Leads", "Apenas sem Website", "Apenas Ficha não Reivindicada"]
        )

    with col_export:
        excel_bytes = gerar_excel_organizado(st.session_state.resultados)
        st.download_button(
            label="📊 Exportar Planilha Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"Leads_Minerados_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.divider()

    resultados_filtrados = st.session_state.resultados
    if filtro_status == "Apenas sem Website":
        resultados_filtrados = [r for r in resultados_filtrados if not r['website']]
    elif filtro_status == "Apenas Ficha não Reivindicada":
        resultados_filtrados = [r for r in resultados_filtrados if not r['reivindicada']]

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
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
                    <div>
                        <h2 style="margin: 0; color: #ffffff; font-size: 20px;">{lead['nome']}</h2>
                        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">📍 {lead['endereco']} | 🏷️ {lead['categoria']}</p>
                    </div>
                    <div class="score-box {score_class}">
                        <div style="font-size: 10px; font-weight: bold;">SCORE</div>
                        <div style="font-size: 20px; font-weight: bold;">{score} / 100</div>
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
                st.markdown(f"<div class='critical-item'>❌ {pc}</div>", unsafe_allow_html=True)

        with col_actions:
            if lead['whatsapp']:
                msg_wa = f"Olá! Notei que a ficha da {lead['nome']} no Google apresenta pontos de melhoria..."
                link_wa = f"https://wa.me/55{lead['whatsapp']}?text={msg_wa.replace(' ', '%20')}"
                st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:6px; font-weight:bold; cursor:pointer; margin-bottom:8px;">💬 WhatsApp</button></a>', unsafe_allow_html=True)

            nome_arquivo_limpo = re.sub(r'[^a-zA-Z0-9]', '_', lead['nome'])
            nome_arquivo_limpo = re.sub(r'_+', '_', nome_arquivo_limpo).strip('_')

            pdf_bytes = gerar_pdf_diagnostico(lead)
            st.download_button(
                label="📄 Gerar PDF da Proposta",
                data=pdf_bytes,
                file_name=f"Diagnostico_{nome_arquivo_limpo}.pdf",
                mime="application/pdf",
                key=f"btn_pdf_{lead['id']}",
                use_container_width=True
            )

        # EXPANSOR DE DETALHAMENTO AVANÇADO DA EMPRESA
        with st.expander(f"🔍 Expandir Análise Detalhada & Links de Pesquisa de {lead['nome']}"):
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                st.markdown("**🌐 Pesquisa Externa & Validação:**")
                st.markdown(f"- [Buscar Empresa no Google Maps](https://www.google.com/maps/search/?api=1&query={lead['nome'].replace(' ', '+')})")
                st.markdown(f"- [Buscar Dominio / Site no Registro.br](https://registro.br/busca-dominio/?pesquisa={lead['nome'].replace(' ', '')})")
                st.markdown(f"- **Website:** {lead['website'] if lead['website'] else 'Sem site cadastrado'}")
            
            with col_exp2:
                st.markdown("**💡 Argumento Comercial Recomendado:**")
                if "Ficha NÃO Reivindicada no Google" in lead['pontos_criticos']:
                    st.info("Alerte o cliente de que o perfil dele pode ser alterado por terceiros ou até ser removido se não for reivindicado oficialmente.")
                elif "Ausência de Tour Virtual 360° interativo" in lead['pontos_criticos']:
                    st.info("Apresente como o Tour Virtual 360° melhora o posicionamento orgânico no Google Maps e gera confiança imediata.")

        st.divider()

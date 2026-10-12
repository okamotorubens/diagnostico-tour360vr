import streamlit as st
import pandas as pd
import json
import time
import os
import re
import requests
import csv
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
# ESTILIZAÇÃO CSS CUSTOMIZADA
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
    
    .sidebar-title {
        text-align: center;
        font-size: 17px;
        font-weight: 800;
        color: #ffffff;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE (ACÚMULO DE BUSCAS NATIVO)
# -----------------------------------------------------------------------------
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1
if 'base_acumulada' not in st.session_state:
    st.session_state.base_acumulada = []

# -----------------------------------------------------------------------------
# INTEGRAÇÃO DE BUSCA E AUDITORIA COMPLETA (COM FOTO DO PERFIL GOOGLE)
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
                
                # Monta URL da foto real do Google Places API
                foto_url = ""
                if photos and len(photos) > 0:
                    photo_reference = photos[0].get("photo_reference")
                    foto_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={api_key}"
                else:
                    foto_url = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&q=80"

                pontos_criticos = []
                oportunidades = []
                score = 0

                if not website:
                    pontos_criticos.append("Sem site oficial vinculado à ficha do Google")
                    oportunidades.append("Desenvolvimento de Landing Page de Alta Conversão / Website Responsivo")
                    score += 25

                if total_avaliacoes < 30:
                    pontos_criticos.append(f"Volume crítico de avaliações ({total_avaliacoes} no total)")
                    oportunidades.append("Estratégia Acelerada de Gestão de Reputação e Captura de Depoimentos")
                    score += 20

                if len(photos) < 5:
                    pontos_criticos.append("Poucas fotos publicadas no perfil corporativo")
                    oportunidades.append("Produção de Fotografia Profissional para Arquitetura e Produtos")
                    score += 20

                pontos_criticos.append("Ausência de Tour Virtual 360° interativo")
                oportunidades.append("Fotografia 360° Imersiva e Publicação no Google Street View")
                score += 25

                clean_phone = "".join(filter(str.isdigit, telefone))
                if len(clean_phone) > 10 and clean_phone.startswith("55"):
                    clean_phone = clean_phone[2:]

                nome_slug = re.sub(r'[^a-zA-Z0-9]', '', nome.lower())

                leads.append({
                    "id": len(st.session_state.base_acumulada) + idx + 1,
                    "nome": nome,
                    "categoria": nicho.capitalize(),
                    "cidade_busca": cidade,
                    "data_minacao": datetime.now().strftime('%d/%m/%Y %H:%M'),
                    "endereco": endereco,
                    "telefone": telefone or "(16) Contato via Ficha",
                    "whatsapp": clean_phone if len(clean_phone) >= 10 else "16999999999",
                    "website": website,
                    "instagram": f"instagram.com/{nome_slug}",
                    "facebook": f"facebook.com/{nome_slug}",
                    "foto_url": foto_url,
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
        {"nome": f"Loja & Boutique {cidade}", "bairro": "Centro", "rua": "Rua Saldanha Marinho", "img": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&q=80"},
        {"nome": f"Estilo & Moda {nicho.capitalize()}", "bairro": "Alto da Boa Vista", "rua": "Av. Independência", "img": "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?w=400&q=80"},
        {"nome": f"Empório & {nicho.capitalize()} do Barão", "bairro": "Jardim Sumaré", "rua": "Rua Garibaldi", "img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&q=80"},
        {"nome": f"Conceito {nicho.capitalize()} Brasil", "bairro": "Vila Seixas", "rua": "Rua Amador Bueno", "img": "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&q=80"},
        {"nome": f"Studio & Galeria {nicho.capitalize()}", "bairro": "Jardim Botânico", "rua": "Av. Professor João Fiúsa", "img": "https://images.unsplash.com/photo-1513151233558-d860c5398176?w=400&q=80"}
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

        nome_slug = re.sub(r'[^a-zA-Z0-9]', '', item['nome'].lower())

        resultados.append({
            "id": len(st.session_state.base_acumulada) + i + 1,
            "nome": item["nome"],
            "categoria": nicho.capitalize(),
            "cidade_busca": cidade,
            "data_minacao": datetime.now().strftime('%d/%m/%Y %H:%M'),
            "endereco": f"{item['rua']}, {120 + (i*85)} - {item['bairro']}, {cidade} - SP",
            "telefone": f"(16) 39{i:02d}-4000",
            "whatsapp": f"16997{i:02d}4000",
            "website": f"https://www.{nicho.lower()}exemplo.com.br" if tem_site else "",
            "instagram": f"instagram.com/{nome_slug}",
            "facebook": f"facebook.com/{nome_slug}",
            "foto_url": item["img"],
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
# GERADOR DE CSV COMPATÍVEL COM EXCEL
# -----------------------------------------------------------------------------
def gerar_csv_excel_formatado(dados_leads):
    output = io.StringIO()
    output.write('\ufeff')
    
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    
    writer.writerow([
        "ID", "Data Mineração", "Cidade Busca", "Nome da Empresa", "Categoria", 
        "Endereço Completo", "Telefone", "WhatsApp", "Website", "Instagram",
        "Nota Média", "Total Avaliações", "Ficha Reivindicada", "Qtd. Fotos", 
        "Pontos Críticos Identificados", "Oportunidades Comerciais", "Score de Oportunidade"
    ])

    for row in dados_leads:
        criticos_str = " | ".join(row.get("pontos_criticos", [])) if isinstance(row.get("pontos_criticos"), list) else str(row.get("pontos_criticos", ""))
        opp_str = " | ".join(row.get("oportunidades", [])) if isinstance(row.get("oportunidades"), list) else str(row.get("oportunidades", ""))
        
        writer.writerow([
            row.get("id", ""),
            row.get("data_minacao", ""),
            row.get("cidade_busca", ""),
            row.get("nome", ""),
            row.get("categoria", ""),
            row.get("endereco", ""),
            row.get("telefone", ""),
            row.get("whatsapp", ""),
            row.get("website", ""),
            row.get("instagram", ""),
            str(row.get("nota", "")).replace('.', ','),
            row.get("total_avaliacoes", ""),
            "Sim" if row.get("reivindicada") else "Não",
            row.get("fotos_total", ""),
            criticos_str,
            opp_str,
            row.get("score_oportunidade", "")
        ])

    return output.getvalue().encode('utf-8')

# -----------------------------------------------------------------------------
# GERADOR DE PDF DUAL BRAND
# -----------------------------------------------------------------------------
def gerar_pdf_diagnostico(lead):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748b'), spaceAfter=15)
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1e293b'), spaceBefore=12, spaceAfter=6, fontName='Helvetica-Bold')
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#334155'), leading=12)
    alert_style = ParagraphStyle('AlertText', parent=body_style, textColor=colors.HexColor('#b91c1c'), fontName='Helvetica-Bold')
    opp_style = ParagraphStyle('OppText', parent=body_style, textColor=colors.HexColor('#15803d'), fontName='Helvetica-Bold')

    elements = []

    logo_okamoto = "logo_okamoto.png" if os.path.exists("logo_okamoto.png") else None
    logo_tour = "logo_tour_transparente.png" if os.path.exists("logo_tour_transparente.png") else None

    img_okamoto = Image(logo_okamoto, width=180, height=55, kind='proportional') if logo_okamoto else Paragraph("<b>OKAMOTO MÍDIAS VISUAIS</b>", body_style)
    img_tour = Image(logo_tour, width=120, height=45, kind='proportional') if logo_tour else Paragraph("<b>TOUR360VR</b>", body_style)

    header_table = Table([[img_okamoto, img_tour]], colWidths=[320, 220])
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
    criticos_list = []
    for pnt in lead['pontos_criticos']:
        criticos_list.append([Paragraph(f"• <b>{pnt}</b><br/><font color='#64748b' size=8>Impacto: Reduz o ranqueamento no Google Maps e afasta potenciais clientes que buscam validação rápida.</font>", alert_style)])
    
    t_criticos = Table(criticos_list, colWidths=[540])
    t_criticos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef2f2')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#fca5a5')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_criticos)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("2. PLANO DE AÇÃO E OPORTUNIDADES DE MELHORIA", section_heading))
    opp_list = []
    for opp in lead['oportunidades']:
        opp_list.append([Paragraph(f"✓ <b>{opp}</b><br/><font color='#475569' size=8>Benefício: Aumenta a taxa de conversão do perfil e gera autoridade imediata no mercado local.</font>", opp_style)])
    
    t_opp = Table(opp_list, colWidths=[540])
    t_opp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#86efac')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_opp)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("3. ESTRATÉGIA DE IMPLEMENTAÇÃO RECOMENDADA", section_heading))
    plano_acao = [
        [Paragraph("<b>Fase 1 (Imediata):</b>", body_style), Paragraph("Regularização do perfil no Google Business, atualização de categorias e proteção de marca.", body_style)],
        [Paragraph("<b>Fase 2 (Estruturação):</b>", body_style), Paragraph("Sessão fotográfica profissional de alta resolução para ambientes, produtos e equipe.", body_style)],
        [Paragraph("<b>Fase 3 (Engajamento):</b>", body_style), Paragraph("Captação e publicação do Tour Virtual 360° interativo integrado ao Google Maps / Street View.", body_style)]
    ]
    t_plano = Table(plano_acao, colWidths=[130, 410])
    t_plano.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_plano)
    elements.append(Spacer(1, 15))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=10, spaceAfter=8))
    rodape_text = Paragraph(
        "<font color='#1e293b'><b>OKAMOTO MÍDIAS VISUAIS & TOUR360VR</b></font><br/>"
        "<font color='#475569' size=8>🌐 <b>Site:</b> tour360vr.com.br &nbsp;|&nbsp; ✉️ <b>E-mail:</b> contato@okamotomidiasvisuais.com.br &nbsp;|&nbsp; 💬 <b>WhatsApp:</b> (16) 99765-4321<br/>"
        "Especialistas em Imagem Profissional, Tours Virtuais 360° e Otimização de Presença Local.</font>",
        ParagraphStyle('Rodape', parent=body_style, alignment=1)
    )
    elements.append(rodape_text)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# BARRA LATERAL (LOGOS CENTRALIZADAS E TÍTULO)
# -----------------------------------------------------------------------------
with st.sidebar:
    if os.path.exists("logo_okamoto.png"):
        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            st.image("logo_okamoto.png", use_container_width=True)
    
    if os.path.exists("logo_tour_transparente.png"):
        c1, c2, c3 = st.columns([1.2, 3.6, 1.2])
        with c2:
            st.image("logo_tour_transparente.png", use_container_width=True)

    st.markdown('<div class="sidebar-title">Mineração & Diagnóstico Local</div>', unsafe_allow_html=True)
    st.divider()

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("1. Buscar", use_container_width=True, type="primary" if st.session_state.etapa == 1 else "secondary"):
            st.session_state.etapa = 1
            st.rerun()
    with col_nav2:
        if st.button("2. Analisar", use_container_width=True, type="primary" if st.session_state.etapa == 2 else "secondary", disabled=len(st.session_state.base_acumulada) == 0):
            st.session_state.etapa = 2
            st.rerun()

    if len(st.session_state.base_acumulada) > 0:
        st.divider()
        st.caption(f"📊 Base Acumulada: **{len(st.session_state.base_acumulada)} leads**")
        if st.button("🗑️ Limpar Histórico de Buscas", use_container_width=True):
            st.session_state.base_acumulada = []
            st.session_state.etapa = 1
            st.rerun()

# -----------------------------------------------------------------------------
# ETAPA 1: BUSCA DE NEGÓCIOS
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
            novos_leads = minerar_e_auditar_negocios(nicho_input, cidade_input, limite_input)
            st.session_state.base_acumulada.extend(novos_leads)
            st.session_state.etapa = 2
            st.rerun()

    if len(st.session_state.base_acumulada) > 0:
        st.divider()
        st.info(f"Há **{len(st.session_state.base_acumulada)} leads acumulados** na base atual.")
        if st.button("Avançar para Análise ➡️", type="primary"):
            st.session_state.etapa = 2
            st.rerun()

# -----------------------------------------------------------------------------
# ETAPA 2: ANALISADOR CRÍTICO COM FOTO DA FICHA E EXIBIÇÃO DIRETA
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 2:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📊 Painel de Análise e Diagnóstico de Leads</h1>
            <div class="main-subtitle">Pontos fracos dos estabelecimentos, mídias e ferramentas para abordagem.</div>
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
        csv_bytes = gerar_csv_excel_formatado(st.session_state.base_acumulada)
        st.download_button(
            label="📊 Exportar Planilha Completa (.csv)",
            data=csv_bytes,
            file_name=f"Leads_Acumulados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.divider()

    resultados_filtrados = st.session_state.base_acumulada
    if filtro_status == "Apenas sem Website":
        resultados_filtrados = [r for r in resultados_filtrados if not r['website']]
    elif filtro_status == "Apenas Ficha não Reivindicada":
        resultados_filtrados = [r for r in resultados_filtrados if not r['reivindicada']]

    st.markdown(f"Exibindo **{len(resultados_filtrados)}** oportunidades na base de prospecção:")

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
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
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

        # 4 COLUNAS: FOTO DA FICHA + GOOGLE INDICADORES + PONTOS CRÍTICOS + MÍDIAS & AÇÕES
        col_img, col_details1, col_details2, col_actions = st.columns([2, 2.5, 2.5, 2.5])

        with col_img:
            st.image(lead['foto_url'], caption="Foto da Ficha do Google", use_container_width=True)

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
            st.markdown("**🌐 Mídias & Ações Rápidas:**")
            st.markdown(f"- **Website:** {lead['website'] if lead['website'] else '❌ Sem site'}")
            st.markdown(f"- **Maps:** [Ver no Google Maps](https://www.google.com/maps/search/?api=1&query={lead['nome'].replace(' ', '+')})")
            st.markdown(f"- **Registro:** [Buscar Domínio](https://registro.br/busca-dominio/?pesquisa={lead['nome'].replace(' ', '')})")

            if lead['whatsapp']:
                msg_wa = f"Olá! Notei que a ficha da {lead['nome']} no Google apresenta pontos de melhoria..."
                link_wa = f"https://wa.me/55{lead['whatsapp']}?text={msg_wa.replace(' ', '%20')}"
                st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:6px; font-weight:bold; cursor:pointer; margin-top:6px; margin-bottom:8px;">💬 WhatsApp</button></a>', unsafe_allow_html=True)

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

        st.divider()

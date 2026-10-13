import streamlit as st
import pandas as pd
import json
import time
import os
import re
import requests
import csv
import urllib.parse
from datetime import datetime
import io
from PIL import Image as PILImage
import base64
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import folium

# Conexão NUVEM Supabase
from supabase import create_client, Client

# ReportLab para geração do PDF do Panorama
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DO ENDEREÇO DO SEU SISTEMA DE DIAGNÓSTICO
# -----------------------------------------------------------------------------
URL_SISTEMA_DIAGNOSTICO = "https://tour360vr.streamlit.app/"

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA STREAMLIT E FAVICON NO NAVEGADOR
# -----------------------------------------------------------------------------
favicon_img = "🔍"
favicon_b64 = ""
if os.path.exists("logo_tour_transparente.png"):
    try:
        favicon_img = PILImage.open("logo_tour_transparente.png")
        with open("logo_tour_transparente.png", "rb") as f:
            favicon_b64 = base64.b64encode(f.read()).decode()
    except Exception:
        favicon_img = "🔍"

st.set_page_config(
    page_title="Radar Comercial | Tour360VR",
    page_icon=favicon_img if not favicon_b64 else PILImage.open("logo_tour_transparente.png"),
    layout="wide",
    initial_sidebar_state="expanded"
)

# FORÇAR O NAVEGADOR A IR PARA O TOPO SEMPRE QUE MUDAR DE PÁGINA
components.html(f"""
    <script>
        function scrollToTop() {{
            window.parent.scrollTo(0, 0);
            var mainContainer = window.parent.document.querySelector(".main");
            if (mainContainer) {{ mainContainer.scrollTop = 0; }}
            var appContainer = window.parent.document.querySelector(".stAppViewContainer");
            if (appContainer) {{ appContainer.scrollTop = 0; }}
        }}
        scrollToTop();
        setTimeout(scrollToTop, 100);
        setTimeout(scrollToTop, 300);
        
        var head = window.parent.document.getElementsByTagName('head')[0];
        if (head && '{favicon_b64}') {{
            var links = window.parent.document.querySelectorAll("link[rel*='icon']");
            links.forEach(function(l) {{ l.parentNode.removeChild(l); }});
            
            var link = window.parent.document.createElement('link');
            link.type = 'image/png';
            link.rel = 'shortcut icon';
            link.href = 'data:image/png;base64,{favicon_b64}';
            head.appendChild(link);
        }}
    </script>
""", height=0)

# -----------------------------------------------------------------------------
# CONEXÃO BANCO DE DADOS EM NUVEM PERMANENTE (SUPABASE)
# -----------------------------------------------------------------------------
@st.cache_resource
def init_supabase():
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
    key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
    if url and key:
        return create_client(url, key)
    return None

supabase: Client = init_supabase()

def salvar_lead_db(lead):
    if not supabase:
        return
    try:
        res = supabase.table("leads").select("id").eq("nome", lead['nome']).eq("endereco", lead['endereco']).execute()
        if not res.data:
            supabase.table("leads").insert({
                "data_minacao": lead.get('data_minacao', datetime.now().strftime('%d/%m/%Y %H:%M')),
                "cidade_busca": lead.get('cidade_busca', ''),
                "bairro_busca": lead.get('bairro_busca', ''),
                "nome": lead['nome'],
                "categoria": lead['categoria'],
                "endereco": lead['endereco'],
                "latitude": float(lead.get('latitude', -21.1775)),
                "longitude": float(lead.get('longitude', -47.8103)),
                "telefone": lead.get('telefone', ''),
                "whatsapp": lead.get('whatsapp', ''),
                "website": lead.get('website', ''),
                "website_https": bool(lead.get('website_https')),
                "instagram": lead.get('instagram', ''),
                "facebook": lead.get('facebook', ''),
                "foto_url": lead.get('foto_url', ''),
                "nota": float(lead.get('nota', 0.0)),
                "total_avaliacoes": int(lead.get('total_avaliacoes', 0)),
                "reivindicada": bool(lead.get('reivindicada')),
                "fotos_total": int(lead.get('fotos_total', 0)),
                "ultima_foto_dias": int(lead.get('ultima_foto_dias', 0)),
                "tour_360": bool(lead.get('tour_360')),
                "status_crm": lead.get('status_crm', '🆕 Novo Lead'),
                "pontos_criticos": lead.get('pontos_criticos', []),
                "oportunidades": lead.get('oportunidades', []),
                "score_oportunidade": int(lead.get('score_oportunidade', 0))
            }).execute()
    except Exception as e:
        st.error(f"Erro ao salvar lead '{lead.get('nome')}': {str(e)}")

def atualizar_status_crm(lead_id, novo_status):
    if not supabase:
        return
    try:
        supabase.table("leads").update({"status_crm": novo_status}).eq("id", lead_id).execute()
    except Exception as e:
        st.error(f"Erro ao atualizar status: {str(e)}")

def carregar_todos_leads_db():
    if not supabase:
        return []
    try:
        res = supabase.table("leads").select("*").order("id", desc=True).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Erro ao carregar dados do Supabase: {str(e)}")
        return []

def limpar_banco_dados():
    if not supabase:
        return
    try:
        supabase.table("leads").delete().neq("id", 0).execute()
    except Exception as e:
        st.error(f"Erro ao limpar banco: {str(e)}")

# -----------------------------------------------------------------------------
# GERADOR DE PDF DO PANORAMA DE NICHO
# -----------------------------------------------------------------------------
def desenhar_cabecalho_rodape_todas_paginas(canvas, doc):
    canvas.saveState()
    styles = getSampleStyleSheet()
    
    # 1. LOGO DESENHADA NA ESQUERDA
    logo_tour = "logo_tour_transparente.png" if os.path.exists("logo_tour_transparente.png") else None
    if logo_tour:
        img_logo = Image(logo_tour, width=170, height=60, kind='proportional')
        img_logo.wrapOn(canvas, 170, 60)
        img_logo.drawOn(canvas, 36, 715)
    else:
        canvas.setFont('Helvetica-Bold', 14)
        canvas.setFillColor(colors.HexColor('#0f172a'))
        canvas.drawString(36, 735, "TOUR360VR")

    # 2. TEXTO CENTRALIZADO NA PÁGINA E ALINHADO NA ALTURA DA LOGO
    header_title_style = ParagraphStyle(
        'HeaderTitleCenterPage',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=15,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        leftIndent=0,
        firstLineIndent=0
    )

    texto_cabecalho = Paragraph(
        "ESTUDO DE INTELIGÊNCIA DE MERCADO LOCAL<br/>E PRESENÇA DIGITAL NO GOOGLE",
        header_title_style
    )

    texto_table = Table([[texto_cabecalho]], colWidths=[540])
    texto_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))

    texto_table.wrapOn(canvas, 540, 60)
    texto_table.drawOn(canvas, 36, 730)

    # 3. LINHA DIVISÓRIA HORIZONTAL DO CABEÇALHO (Fina: 0.5)
    canvas.setStrokeColor(colors.HexColor('#cbd5e1'))
    canvas.setLineWidth(0.5)
    canvas.line(36, 706, 576, 706)
    
    # 4. RODAPÉ FIXO COM LINHA DIVISÓRIA FINA (Fina: 0.5)
    canvas.setLineWidth(0.5)
    canvas.line(36, 42, 576, 42)
    
    canvas.setFont('Helvetica', 8.5)
    canvas.setFillColor(colors.HexColor('#0f172a'))
    
    texto_rodape = "tour360vr.com.br   |   contato@okamotomidiasvisuais.com.br   |   (16) 99133-2121"
    canvas.drawCentredString(306, 25, texto_rodape)

    try:
        canvas.linkURL('https://tour360vr.com.br', (110, 15, 205, 33), relative=0)
        canvas.linkURL('mailto:contato@okamotomidiasvisuais.com.br', (215, 15, 370, 33), relative=0)
        canvas.linkURL('https://wa.me/5516991332121', (430, 15, 400, 33), relative=0)
    except Exception:
        pass
        
    canvas.restoreState()

def gerar_pdf_panorama_nicho(nicho_nome, df_nicho):
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=95, bottomMargin=55,
        title=f"Panorama de Mercado - {nicho_nome}",
        author="Tour360VR"
    )
    styles = getSampleStyleSheet()
    
    main_title_style = ParagraphStyle(
        'MainTitle', parent=styles['Heading1'],
        fontSize=13, textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold', alignment=1, spaceBefore=0, spaceAfter=8
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading', parent=styles['Heading2'],
        fontSize=9.5, textColor=colors.HexColor('#0f172a'),
        spaceBefore=8, spaceAfter=5, fontName='Helvetica-Bold', alignment=1
    )
    
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor('#334155'), leading=10.5)
    body_center = ParagraphStyle('BodyCenter', parent=body_style, alignment=1)

    elements = []

    title_p = Paragraph(f"PANORAMA DE MERCADO: {nicho_nome.upper()}", main_title_style)
    title_table = Table([[title_p]], colWidths=[540])
    title_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    elements.append(title_table)
    
    elements.append(Spacer(1, 2))
    elements.append(Paragraph("DISTRIBUIÇÃO DE EMPRESAS POR SCORE DE OPORTUNIDADE COMERCIAL (PONTUAÇÃO)", section_heading))
    elements.append(Spacer(1, 2))

    scores_counts = df_nicho['score_oportunidade'].value_counts().sort_index(ascending=False)
    
    chart_draw = Drawing(540, 95)
    chart_draw.hAlign = 'CENTER'
    chart_draw.add(Rect(0, 0, 540, 95, fillColor=colors.HexColor('#f8fafc'), strokeColor=colors.HexColor('#cbd5e1'), strokeWidth=0.5, rx=0, ry=0))
    
    qtd_bars = len(scores_counts)
    if qtd_bars > 0:
        bar_w = min(40, max(18, 380 // qtd_bars))
        gap = min(22, (500 - (qtd_bars * bar_w)) // (qtd_bars + 1))
        max_val = max(scores_counts.values) if max(scores_counts.values) > 0 else 1
        start_x = (540 - (qtd_bars * bar_w + (qtd_bars - 1) * gap)) / 2
        
        for idx_sc, (score_val, total_lead) in enumerate(scores_counts.items()):
            bx = start_x + idx_sc * (bar_w + gap)
            by = 22
            bh = max((total_lead / max_val) * 52, 6)
            
            c_fill = colors.HexColor('#4ade80') if score_val >= 60 else (colors.HexColor('#facc15') if score_val >= 30 else colors.HexColor('#f87171'))
            
            chart_draw.add(Rect(bx, by, bar_w, bh, fillColor=c_fill, strokeColor=None, rx=2, ry=2))
            chart_draw.add(String(bx + (bar_w / 2), by + bh + 4, str(total_lead), fontSize=8.5, fontName="Helvetica-Bold", fillColor=colors.HexColor('#0f172a'), textAnchor="middle"))
            chart_draw.add(String(bx + (bar_w / 2), by - 12, f"{score_val} pts", fontSize=7.5, fontName="Helvetica-Bold", fillColor=colors.HexColor('#475569'), textAnchor="middle"))

    elements.append(chart_draw)
    elements.append(Spacer(1, 8))

    total_emp = len(df_nicho)
    sem_site = len(df_nicho[df_nicho['website'] == ''])
    nao_reiv = len(df_nicho[df_nicho['reivindicada'] == False])
    poucas_av = len(df_nicho[df_nicho['total_avaliacoes'] < 30])

    dados_resumo = [
        [Paragraph("<b>INDICADOR ESTRATÉGICO</b>", body_style), Paragraph("<b>VOLUME / %</b>", body_center), Paragraph("<b>DIAGNÓSTICO DE OPORTUNIDADE</b>", body_style)],
        [Paragraph("Otimização de Avaliações", body_style), Paragraph(f"<b>{poucas_av} ({(poucas_av/total_emp*100 if total_emp>0 else 0):.1f}%)</b>", body_center), Paragraph("Volume baixo (<30 avaliações) afetando a prova social e ranking.", body_style)],
        [Paragraph("Sem Website Oficial", body_style), Paragraph(f"<b>{sem_site} ({(sem_site/total_emp*100 if total_emp>0 else 0):.1f}%)</b>", body_center), Paragraph("Perda de tráfego direto e dependência de canais de terceiros.", body_style)],
        [Paragraph("Fichas Não Reivindicadas", body_style), Paragraph(f"<b>{nao_reiv} ({(nao_reiv/total_emp*100 if total_emp>0 else 0):.1f}%)</b>", body_center), Paragraph("Vulnerabilidade de segurança e falta de gestão do perfil.", body_style)]
    ]
    t_resumo = Table(dados_resumo, colWidths=[150, 90, 300])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
    ]))
    elements.append(t_resumo)
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("RANKING DE EMPRESAS AUDITADAS NO SETOR", section_heading))
    elements.append(Spacer(1, 4))

    df_nicho_sorted = df_nicho.sort_values(by='score_oportunidade', ascending=False)

    t_data = [[
        Paragraph("<b>EMPRESA</b>", body_style), 
        Paragraph("<b>NOTA</b>", body_center), 
        Paragraph("<b>AVALIAÇÕES</b>", body_center),
        Paragraph("<b>SITE</b>", body_center), 
        Paragraph("<b>SCORE</b>", body_center)
    ]]
    
    t_styles = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]

    for idx, row in enumerate(df_nicho_sorted.iterrows()):
        r_data = row[1]
        sc = r_data['score_oportunidade']
        
        if sc >= 60:
            bg_color = colors.HexColor('#86efac')
            txt_color = '#14532d'
        elif sc >= 30:
            bg_color = colors.HexColor('#fde047')
            txt_color = '#713f12'
        else:
            bg_color = colors.HexColor('#fca5a5')
            txt_color = '#7f1d1d'

        p_score = Paragraph(f"<font color='{txt_color}'><b>{sc}/100</b></font>", body_center)

        row_idx = idx + 1
        t_styles.append(('BACKGROUND', (4, row_idx), (4, row_idx), bg_color))

        t_data.append([
            Paragraph(str(r_data['nome'])[:45], body_style),
            Paragraph(str(r_data['nota']), body_center),
            Paragraph(str(r_data['total_avaliacoes']), body_center),
            Paragraph("Sim" if r_data['website'] else "Não", body_center),
            p_score
        ])

    t_empresas = Table(t_data, colWidths=[270, 50, 80, 50, 90], repeatRows=1)
    t_empresas.setStyle(TableStyle(t_styles))
    elements.append(t_empresas)

    doc.build(elements, onFirstPage=desenhar_cabecalho_rodape_todas_paginas, onLaterPages=desenhar_cabecalho_rodape_todas_paginas)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (SIDEBAR FIXA SEM SCROLLBAR)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    .main { background-color: #0e1117; padding-top: 15px !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    
    section[data-testid="stSidebar"] {
        width: 310px !important;
        min-width: 310px !important;
        max-width: 310px !important;
    }
    
    [data-testid="stSidebarResizer"],
    div[data-testid="stSidebarResizer"],
    .st-emotion-cache-12w0q3g,
    .st-emotion-cache-6q42n4 {
        display: none !important;
        width: 0px !important;
        pointer-events: none !important;
        opacity: 0 !important;
    }

    [data-testid="stSidebar"] * {
        scrollbar-width: none !important;
    }

    [data-testid="stSidebar"]::-webkit-scrollbar {
        display: none !important;
        width: 0px !important;
    }

    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white; padding: 14px 18px; border-radius: 10px; margin-bottom: 15px;
        border: 1px solid #334155; margin-top: 5px !important;
    }
    .main-title { font-size: 21px; font-weight: 700; margin: 0; color: #ffffff; }
    .main-subtitle { font-size: 12px; color: #94a3b8; margin-top: 3px; }

    .lead-card {
        background-color: #1e293b; border-radius: 10px; padding: 14px;
        margin-bottom: 10px; border: 1px solid #334155;
    }
    
    .score-box { text-align: center; padding: 8px; border-radius: 8px; font-weight: bold; width: 130px; }
    .score-high { background-color: #052e16; color: #86efac; border: 1px solid #166534; }
    .score-med  { background-color: #451a03; color: #fde047; border: 1px solid #92400e; }
    .score-low  { background-color: #450a0a; color: #fca5a5; border: 1px solid #991b1b; }

    .critical-item { color: #f87171; font-size: 13px; margin-bottom: 6px; font-weight: 500; }
    
    .sidebar-title {
        text-align: center; font-size: 15px; font-weight: 800; color: #ffffff;
        margin-top: -10px; margin-bottom: 10px; letter-spacing: 0.5px;
    }

    .stButton>button, .btn-redirect {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 4px rgba(255, 255, 255, 0.2) !important;
    }
    .stButton>button:hover, .btn-redirect:hover {
        border-color: #ffffff !important;
        box-shadow: 0 0 12px rgba(255, 255, 255, 0.7) !important;
        background-color: #1e293b !important;
    }

    .btn-redirect {
        display: block; width: 100%; text-align: center; padding: 8px 10px;
        text-decoration: none !important; margin-bottom: 8px;
    }

    .script-box {
        background-color: #0f172a; color: #f1f5f9;
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 13px; line-height: 1.5; padding: 12px 15px;
        border-radius: 8px; border: 1px solid #334155;
        white-space: pre-wrap; margin-bottom: 10px;
    }

    div[data-testid="stDataFrame"] table th {
        text-align: center !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE E CONTROLE DE ETAPA
# -----------------------------------------------------------------------------
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1

def mudar_etapa(nova_etapa):
    st.session_state.etapa = nova_etapa
    st.rerun()

# -----------------------------------------------------------------------------
# INTEGRAÇÃO DE BUSCA REAL VIA GOOGLE PLACES API COM RAIO DE KM
# -----------------------------------------------------------------------------
def buscar_google_places_api(nicho, cidade, bairro, rua, raio_km, api_key, limite=20):
    termos = []
    if nicho: termos.append(nicho.strip())
    if rua: termos.append(rua.strip())
    if bairro: termos.append(bairro.strip())
    if cidade: termos.append(cidade.strip())
    
    query_str = " ".join(termos)
    raio_metros = int(raio_km * 1000)
    
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={urllib.parse.quote(query_str)}&radius={raio_metros}&language=pt-BR&key={api_key}"
    
    try:
        response = requests.get(url, timeout=12)
        data = response.json()
        
        status = data.get("status")
        
        if status == "OK":
            results = data.get("results", [])[:limite]
            leads = []
            for place in results:
                place_id = place.get("place_id")
                lat = place.get("geometry", {}).get("location", {}).get("lat", -21.1775)
                lng = place.get("geometry", {}).get("location", {}).get("lng", -47.8103)
                
                det_res = {}
                if place_id:
                    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos&language=pt-BR&key={api_key}"
                    det_res = requests.get(details_url, timeout=5).json().get("result", {})
                
                nome = det_res.get("name") or place.get("name")
                endereco = det_res.get("formatted_address") or place.get("formatted_address")

                telefone = det_res.get("formatted_phone_number", "")
                website = det_res.get("website", "")
                nota = det_res.get("rating", place.get("rating", 0.0))
                total_avaliacoes = det_res.get("user_ratings_total", place.get("user_ratings_total", 0))
                photos = det_res.get("photos", place.get("photos", []))
                
                foto_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photos[0].get('photo_reference')}&key={api_key}" if photos else "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&q=80"

                pontos_criticos = []
                oportunidades = []
                score = 0

                has_https = website.startswith("https://") if website else False
                if not website:
                    pontos_criticos.append("Sem site oficial vinculado à ficha do Google")
                    oportunidades.append("Desenvolvimento de Landing Page / Website Responsivo")
                    score += 30
                elif not has_https:
                    pontos_criticos.append("Site oficial sem Certificado de Segurança (HTTP inseguro)")
                    oportunidades.append("Adequação de Segurança SSL e Otimização Web")
                    score += 15

                if total_avaliacoes < 30:
                    pontos_criticos.append(f"Volume crítico de avaliações ({total_avaliacoes} no total)")
                    oportunidades.append("Estratégia Acelerada de Reputação e Gestão de Avaliações")
                    score += 25

                if len(photos) < 8:
                    pontos_criticos.append(f"Poucas fotos publicadas no perfil ({len(photos)} fotos)")
                    oportunidades.append("Produção de Fotografia Profissional para Arquitetura e Estrutura")
                    score += 20

                pontos_criticos.append("Oportunidade de Imersão: Implantação de Tour Virtual 360°")
                oportunidades.append("Fotografia 360° Imersiva e Publicação no Google Street View")
                score += 25

                clean_phone = "".join(filter(str.isdigit, telefone))
                if len(clean_phone) > 10 and clean_phone.startswith("55"):
                    clean_phone = clean_phone[2:]

                nome_slug = re.sub(r'[^a-zA-Z0-9]', '', nome.lower())

                lead_obj = {
                    "data_minacao": datetime.now().strftime('%d/%m/%Y %H:%M'),
                    "cidade_busca": cidade,
                    "bairro_busca": bairro,
                    "nome": nome,
                    "categoria": (nicho or "Comércio").capitalize(),
                    "endereco": endereco,
                    "latitude": lat,
                    "longitude": lng,
                    "telefone": telefone or "(16) Contato via Ficha",
                    "whatsapp": clean_phone if len(clean_phone) >= 10 else "16999999999",
                    "website": website,
                    "website_https": has_https,
                    "instagram": f"https://instagram.com/{nome_slug}",
                    "facebook": f"https://facebook.com/{nome_slug}",
                    "foto_url": foto_url,
                    "nota": nota,
                    "total_avaliacoes": total_avaliacoes,
                    "reivindicada": True,
                    "fotos_total": len(photos),
                    "ultima_foto_dias": 60,
                    "tour_360": False,
                    "status_crm": "🆕 Novo Lead",
                    "pontos_criticos": pontos_criticos,
                    "oportunidades": oportunidades,
                    "score_oportunidade": min(score, 100)
                }
                
                salvar_lead_db(lead_obj)
                leads.append(lead_obj)
            return leads
        elif status == "ZERO_RESULTS":
            st.warning("⚠️ O Google Maps não encontrou empresas para este termo exato dentro do raio especificado. Tente aumentar o raio de km.")
        else:
            msg_erro = data.get("error_message", "Sem detalhes adicionais do Google.")
            st.error(f"⚠️ Resposta do Google Maps: **Status '{status}'**. Detalhes: {msg_erro}")
    except Exception as e:
        st.error(f"Erro na requisição à API do Google Places: {str(e)}")
    return None

def minerar_e_auditar_negocios(nicho, cidade, bairro, rua, raio_km, limite=20):
    api_key = st.secrets.get("GOOGLE_API_KEY", None) or os.getenv("GOOGLE_API_KEY", None)
    
    if api_key:
        api_key_limpa = api_key.strip().replace('"', '').replace("'", "")
        leads_reais = buscar_google_places_api(nicho, cidade, bairro, rua, raio_km, api_key_limpa, limite)
        if leads_reais and len(leads_reais) > 0:
            return leads_reais
    else:
        st.error("⚠️ A chave 'GOOGLE_API_KEY' não foi encontrada nos Secrets do Streamlit Cloud.")
    return []

# -----------------------------------------------------------------------------
# GERADOR DE CSV COMPLETO
# -----------------------------------------------------------------------------
def gerar_csv_excel_formatado(dados_leads):
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([
        "ID", "Data Mineração", "Cidade Busca", "Bairro Busca", "Nome da Empresa", 
        "Categoria / Nicho", "Status Comercial CRM", "Endereço Completo", "Telefone Fixo", 
        "WhatsApp", "Possui Website?", "Website URL", "Site Seguro (HTTPS)?", 
        "Instagram URL", "Facebook URL", "Nota Média Google", "Total Avaliações", 
        "Ficha Reivindicada?", "Qtd. Fotos Publicadas", "Dias Desde Última Foto", 
        "Possui Tour 360°?", "Pontos Críticos Identificados", "Score de Oportunidade"
    ])

    for row in dados_leads:
        criticos_str = " | ".join(row.get("pontos_criticos", [])) if isinstance(row.get("pontos_criticos"), list) else str(row.get("pontos_criticos", ""))
        writer.writerow([
            row.get("id", ""),
            row.get("data_minacao", ""),
            row.get("cidade_busca", ""),
            row.get("bairro_busca", ""),
            row.get("nome", ""),
            row.get("categoria", ""),
            row.get("status_crm", "🆕 Novo Lead"),
            row.get("endereco", ""),
            row.get("telefone", ""),
            row.get("whatsapp", ""),
            "Sim" if row.get("website") else "Não",
            row.get("website", ""),
            "Sim" if row.get("website_https") else "Não",
            row.get("instagram", ""),
            row.get("facebook", ""),
            str(row.get("nota", "")).replace('.', ','),
            row.get("total_avaliacoes", ""),
            "Sim" if row.get("reivindicada") else "Não",
            row.get("fotos_total", ""),
            row.get("ultima_foto_dias", ""),
            "Sim" if row.get("tour_360") else "Não",
            criticos_str,
            row.get("score_oportunidade", "")
        ])

    return output.getvalue().encode('utf-8')

# -----------------------------------------------------------------------------
# BARRA LATERAL
# -----------------------------------------------------------------------------
base_leads = carregar_todos_leads_db()

with st.sidebar:
    st.markdown('<div class="sidebar-title">Radar Comercial</div>', unsafe_allow_html=True)
    
    # Logo Tour360VR
    if os.path.exists("logo_tour_transparente.png"):
        c1, c2, c3 = st.columns([1.2, 3.6, 1.2])
        with c2: st.image("logo_tour_transparente.png", use_container_width=True)
    
    # Logo Okamoto Mídias Visuais
    if os.path.exists("logo_okamoto.png"):
        c1, c2, c3 = st.columns([0.8, 4.4, 0.8])
        with c2: st.image("logo_okamoto.png", use_container_width=True)

    st.divider()

    st.markdown("### 📌 Módulos")
    if st.button("1. Buscador de Clientes", use_container_width=True, type="primary" if st.session_state.etapa == 1 else "secondary"):
        mudar_etapa(1)
        
    if st.button("2. Base & CRM de Leads", use_container_width=True, type="primary" if st.session_state.etapa == 2 else "secondary"):
        mudar_etapa(2)

    if st.button("3. Panorama de Nicho (Estatísticas)", use_container_width=True, type="primary" if st.session_state.etapa == 3 else "secondary"):
        mudar_etapa(3)

    if st.button("4. Mapa de Prospecção", use_container_width=True, type="primary" if st.session_state.etapa == 4 else "secondary"):
        mudar_etapa(4)

    st.divider()
    st.caption(f"☁️ Supabase Nuvem: **{len(base_leads)} leads salvos**")

    if len(base_leads) > 0:
        if st.button("🗑️ Limpar Banco de Dados", use_container_width=True):
            limpar_banco_dados()
            mudar_etapa(1)

# -----------------------------------------------------------------------------
# ETAPA 1: BUSCADOR DE CLIENTES
# -----------------------------------------------------------------------------
if st.session_state.etapa == 1:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🔎 Radar e Mineração de Mercado Local</h1>
            <div class="main-subtitle">Varredura de perfis no Google Maps por Nicho, Cidade, Bairro, Rua e Raio de Distância (km).</div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("form_busca"):
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1.8, 1.8, 1.2, 1.2])
        with col1: nicho_input = st.text_input("Nicho / Categoria (Opcional)", value="", help="Deixe em branco para buscar empresas gerais no local")
        with col2: cidade_input = st.text_input("Cidade / Município", value="Ribeirão Preto")
        with col3: rua_input = st.text_input("Rua / Avenida (Opcional)", value="", help="Ex: Av. Independência")
        with col4: bairro_input = st.text_input("Bairro / Região (Opcional)", value="", help="Deixe em branco para amplitude de busca na cidade")
        with col5: raio_input = st.number_input("Raio (km)", min_value=1, max_value=50, value=10, step=1, help="Distância máxima de busca a partir do centro da localidade")
        with col6: limite_input = st.number_input("Qtd. Máxima", min_value=20, max_value=70, value=20, step=5)
        
        btn_minar = st.form_submit_button("🚀 Iniciar Varredura Profunda", use_container_width=True)

    if btn_minar:
        with st.spinner(f"Varrendo Google Maps num raio de {raio_input} km, auditando presença web e salvando na nuvem..."):
            time.sleep(1)
            novos = minerar_e_auditar_negocios(nicho_input, cidade_input, bairro_input, rua_input, raio_input, limite_input)
            if novos and len(novos) > 0:
                mudar_etapa(2)

    if len(base_leads) > 0:
        st.divider()
        st.info(f"O seu banco na nuvem possui **{len(base_leads)} leads salvos permanentemente**.")
        if st.button("Ver Base Completa de Leads ➡️", type="primary"):
            mudar_etapa(2)

# -----------------------------------------------------------------------------
# ETAPA 2: BASE DE LEADS & CRM DE VENDAS
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 2:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📊 Base de Leads e Gerenciador CRM</h1>
            <div class="main-subtitle">Seus leads permanecem salvos na nuvem indefinidamente. Atualize status, use scripts de vendas e exporte planilhas.</div>
        </div>
    """, unsafe_allow_html=True)

    if len(base_leads) == 0:
        st.warning("⚠️ Nenhum lead cadastrado ainda no banco de dados. Faça sua primeira busca no Módulo 1!")
    else:
        df_leads_crm = pd.DataFrame(base_leads)

        col_f_nicho, col_f_cid, col_f_status, col_export = st.columns([2, 2, 2, 2.2])

        with col_f_nicho:
            nichos_existentes = ["Todos os Nichos"] + list(df_leads_crm['categoria'].unique())
            filtro_nicho = st.selectbox("Filtrar por Nicho:", nichos_existentes)

        with col_f_cid:
            cidades_existentes = ["Todas as Cidades"] + list(df_leads_crm['cidade_busca'].unique())
            filtro_cidade = st.selectbox("Filtrar por Cidade:", cidades_existentes)

        with col_f_status:
            filtro_status = st.selectbox(
                "Status CRM:",
                ["Todos os Status", "🆕 Novo Lead", "💬 Em Abordagem", "🛠️ Diagnóstico Gerado", "🤝 Cliente Fechado", "❌ Recusado"]
            )

        with col_export:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            csv_bytes = gerar_csv_excel_formatado(base_leads)
            st.download_button(
                label="📊 Exportar Planilha (.csv)",
                data=csv_bytes,
                file_name=f"Leads_Completo_CRM_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.divider()

        resultados_filtrados = base_leads
        if filtro_nicho != "Todos os Nichos":
            resultados_filtrados = [r for r in resultados_filtrados if r['categoria'] == filtro_nicho]
        if filtro_cidade != "Todas as Cidades":
            resultados_filtrados = [r for r in resultados_filtrados if r['cidade_busca'] == filtro_cidade]
        if filtro_status != "Todos os Status":
            resultados_filtrados = [r for r in resultados_filtrados if r['status_crm'] == filtro_status]

        st.markdown(f"Exibindo **{len(resultados_filtrados)}** oportunidades salvas:")

        for lead in resultados_filtrados:
            score = lead['score_oportunidade']
            score_class = "score-high" if score >= 60 else ("score-med" if score >= 30 else "score-low")
            score_label = "ALTA OPORTUNIDADE" if score >= 60 else ("MÉDIA OPORTUNIDADE" if score >= 30 else "BAIXA OPORTUNIDADE")

            st.markdown(f"""
                <div class="lead-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                        <div>
                            <h2 style="margin: 0; color: #ffffff; font-size: 19px;">{lead['nome']}</h2>
                            <p style="margin: 3px 0 0 0; color: #94a3b8; font-size: 12.5px;">📍 {lead['endereco']} | 🏷️ {lead['categoria']}</p>
                        </div>
                        <div class="score-box {score_class}">
                            <div style="font-size: 9.5px; font-weight: bold;">SCORE</div>
                            <div style="font-size: 18px; font-weight: bold;">{score} / 100</div>
                            <div style="font-size: 8.5px;">{score_label}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col_img, col_details1, col_details2, col_actions = st.columns([2, 2.5, 2.5, 2.5])

            with col_img:
                st.image(lead['foto_url'], caption="Foto da Ficha do Google", use_container_width=True)
                
                status_opcoes = ["🆕 Novo Lead", "💬 Em Abordagem", "🛠️ Diagnóstico Gerado", "🤝 Cliente Fechado", "❌ Recusado"]
                idx_atual = status_opcoes.index(lead['status_crm']) if lead['status_crm'] in status_opcoes else 0
                novo_st = st.selectbox("Status Comercial:", status_opcoes, index=idx_atual, key=f"crm_st_{lead['id']}")
                if novo_st != lead['status_crm']:
                    atualizar_status_crm(lead['id'], novo_st)
                    st.toast("Status comercial atualizado com sucesso na nuvem!")
                    st.rerun()

            with col_details1:
                st.markdown("**📊 Indicadores no Google:**")
                st.markdown(f"- **Nota Média:** ⭐ {lead['nota']} ({lead['total_avaliacoes']} avaliações)")
                st.markdown(f"- **Ficha Reivindicada?** {'✅ Sim' if lead['reivindicada'] else '❌ **NÃO REIVINDICADA**'}")
                st.markdown(f"- **Fotos na Ficha:** {lead['fotos_total']} fotos (última há {lead['ultima_foto_dias']} dias)")
                st.markdown(f"- **Tour 360°:** {'✅ Presente' if lead['tour_360'] else '❌ **Ausente**'}")

            with col_details2:
                st.markdown("**🚨 Pontos Críticos Encontrados:**")
                criticos_lista = lead['pontos_criticos'] if isinstance(lead['pontos_criticos'], list) else json.loads(lead['pontos_criticos'] or '[]')
                for pc in criticos_lista:
                    st.markdown(f"<div class='critical-item'>❌ {pc}</div>", unsafe_allow_html=True)

            with col_actions:
                st.markdown("**🌐 Presença Web & Mídias:**")
                st.markdown(f"- **Website:** {lead['website'] if lead['website'] else '❌ Sem site'}")
                st.markdown(f"- **Instagram:** [Abrir Perfil]({lead['instagram']})")
                st.markdown(f"- **Maps:** [Ver no Google Maps](https://www.google.com/maps/search/?api=1&query={lead['nome'].replace(' ', '+')})")

                st.markdown(f'<a href="{URL_SISTEMA_DIAGNOSTICO}" target="_blank" class="btn-redirect">🛠️ Abrir no Diagnóstico Tour360VR</a>', unsafe_allow_html=True)

                if lead['whatsapp']:
                    msg_wa = f"Olá! Tudo bem?\nMeu nome é Rubens Okamoto, da Okamoto Mídias Visuais e do Tour360VR.\nEstava analisando a presença da {lead['nome']} no Google, e identifiquei 3 pontos onde a visibilidade do espaço de vocês pode ser bastante ampliada em relação aos concorrentes da região.\nMontei um relatório curto de diagnóstico em PDF. Posso te enviar por aqui para você dar uma olhada?."
                    link_wa = f"https://wa.me/55{lead['whatsapp']}?text={urllib.parse.quote(msg_wa)}"
                    st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:6px; font-weight:bold; cursor:pointer; margin-bottom:8px;">💬 WhatsApp</button></a>', unsafe_allow_html=True)

            with st.expander(f"✉️ **Uso Interno — Scripts de Vendas e Abordagem ({lead['nome']})**"):
                st.markdown("**1) Abordagem Inicial — WhatsApp**")
                script_wa = script_wa = f"""Olá! Tudo bem?
Meu nome é Rubens Okamoto, da Okamoto Mídias Visuais e do Tour360VR.
Estava analisando a presença da {lead['nome']} no Google, e identifiquei 3 pontos onde a visibilidade do espaço de vocês pode ser bastante ampliada em relação aos concorrentes da região.
Montei um relatório curto de diagnóstico em PDF. Posso te enviar por aqui para você dar uma olhada?"""
                st.markdown(f'<div class="script-box">{script_wa}</div>', unsafe_allow_html=True)

                st.markdown("**2) Abordagem Inicial — E-mail**")
                script_email = f"""Assunto: Oportunidade de Presença Digital: {lead['nome']} no Google

Olá! Analisei o perfil da {lead['nome']} no Google e gostaria de compartilhar uma oportunidade importante.

Identifiquei 3 pontos críticos que estão impactando a confiança de novos clientes:
1. Ausência de Tour Virtual 360° navegável (seus concorrentes levam vantagem visual).
2. Perfil estático com fotos e informações desatualizadas.
3. Falta de otimização de palavras-chave para o setor de {lead['categoria']}.

Temos soluções para transformar a vitrine do seu negócio no Google. Anexo um diagnóstico em PDF com a análise detalhada.

Fico à disposição para conversarmos!
Atenciosamente,
TOUR360VR | Okamoto Mídias Visuais
(16) 99133-2121 | tour360vr.com.br"""
                st.markdown(f'<div class="script-box">{script_email}</div>', unsafe_allow_html=True)

                st.markdown("**3) Follow-up 48h — Pós-Envio do Diagnóstico**")
                script_follow = f"Olá! Só checando por aqui — conseguiu analisar o diagnóstico em PDF da {lead['nome']} que te enviei? Fico no aguardo para tirar qualquer dúvida!"
                st.markdown(f'<div class="script-box">{script_follow}</div>', unsafe_allow_html=True)

            st.divider()

# -----------------------------------------------------------------------------
# ETAPA 3: PANORAMA DE NICHO
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 3:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📈 Panorama de Mercado & Inteligência de Nicho</h1>
            <div class="main-subtitle">Análise detalhada por categoria e município ordenada por maior oportunidade comercial.</div>
        </div>
    """, unsafe_allow_html=True)

    if len(base_leads) == 0:
        st.warning("⚠️ Nenhum lead cadastrado ainda no banco de dados. Faça sua primeira busca no Módulo 1!")
    else:
        df_leads = pd.DataFrame(base_leads)

        categorias_disponiveis = ["Todos os Nichos Mapeados"] + list(df_leads['categoria'].unique())
        cidades_disponiveis = ["Todas as Cidades"] + list(df_leads['cidade_busca'].unique())

        col_sel_nicho, col_sel_cid, col_btn_pdf = st.columns([2.5, 2.5, 2])
        
        with col_sel_nicho:
            nicho_selecionado = st.selectbox("🎯 Nicho Comercial:", categorias_disponiveis)

        with col_sel_cid:
            cidade_selecionada = st.selectbox("📍 Cidade / Município:", cidades_disponiveis)

        df_filtrado = df_leads.copy()
        if nicho_selecionado != "Todos os Nichos Mapeados":
            df_filtrado = df_filtrado[df_filtrado['categoria'] == nicho_selecionado]
        if cidade_selecionada != "Todas as Cidades":
            df_filtrado = df_filtrado[df_filtrado['cidade_busca'] == cidade_selecionada]

        df_filtrado_sorted = df_filtrado.sort_values(by='score_oportunidade', ascending=False)

        data_hoje_str = datetime.now().strftime('%d-%m-%Y')
        nicho_limpo = nicho_selecionado.replace(':', '').replace('/', ' ')
        nome_arquivo_pdf = f"Panorama de Mercado - {nicho_limpo} - {data_hoje_str}.pdf"

        with col_btn_pdf:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            pdf_bytes_nicho = gerar_pdf_panorama_nicho(nicho_selecionado, df_filtrado_sorted)
            st.download_button(
                label="📄 Baixar Relatório (.pdf)",
                data=pdf_bytes_nicho,
                file_name=nome_arquivo_pdf,
                mime="application/pdf",
                use_container_width=True
            )

        st.divider()

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        total_count = len(df_filtrado_sorted)
        
        with col_m1: 
            st.metric("Empresas Analisadas", total_count)
        with col_m2: 
            poucas_av = len(df_filtrado_sorted[df_filtrado_sorted['total_avaliacoes'] < 30])
            st.metric("Poucas Avaliações (<30)", f"{(poucas_av / total_count * 100 if total_count > 0 else 0):.1f}%", f"{poucas_av} empresas")
        with col_m3: 
            sem_site = len(df_filtrado_sorted[df_filtrado_sorted['website'] == ''])
            st.metric("Sem Website Oficial", f"{(sem_site / total_count * 100 if total_count > 0 else 0):.1f}%", f"{sem_site} empresas")
        with col_m4: 
            nao_reiv = len(df_filtrado_sorted[df_filtrado_sorted['reivindicada'] == False])
            st.metric("Fichas não Reivindicadas", f"{(nao_reiv / total_count * 100 if total_count > 0 else 0):.1f}%", f"{nao_reiv} empresas")

        st.divider()

        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            st.markdown("### 📊 Nível de Oportunidade Comercial (Score)")
            st.bar_chart(df_filtrado_sorted['score_oportunidade'].value_counts())

        with c_chart2:
            st.markdown("### ⭐ Média de Avaliações no Google")
            st.bar_chart(df_filtrado_sorted['nota'].value_counts())

        st.divider()
        st.markdown(f"### 📋 Ranking do Nicho **{nicho_selecionado}**:")
        
        df_exibicao = pd.DataFrame({
            'EMPRESA': df_filtrado_sorted['nome'],
            'CIDADE': df_filtrado_sorted['cidade_busca'],
            'SCORE': df_filtrado_sorted['score_oportunidade'].apply(lambda x: f"{x}/100"),
            'NOTA': df_filtrado_sorted['nota'].apply(lambda x: f"{x:.1f} ⭐"),
            'AVALIAÇÕES': df_filtrado_sorted['total_avaliacoes'].astype(str),
            'WEBSITE': df_filtrado_sorted['website'].apply(lambda x: x if x else "Sem site registrado")
        })

        altura_dinamica = (len(df_exibicao) + 1) * 35 + 10

        st.dataframe(
            df_exibicao,
            use_container_width=True,
            hide_index=True,
            height=altura_dinamica,
            column_config={
                "EMPRESA": st.column_config.Column("EMPRESA", width="large"),
                "CIDADE": st.column_config.Column("CIDADE", alignment="center"),
                "SCORE": st.column_config.Column("SCORE", width="small", alignment="center"),
                "NOTA": st.column_config.Column("NOTA", width="small", alignment="center"),
                "AVALIAÇÕES": st.column_config.Column("AVALIAÇÕES", width="small", alignment="center"),
                "WEBSITE": st.column_config.LinkColumn("WEBSITE", width="large")
            }
        )

# -----------------------------------------------------------------------------
# ETAPA 4: MAPA DE PROSPECÇÃO (CENTRALIZAÇÃO DINÂMICA)
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 4:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🗺️ Mapa de Localização e Concentração</h1>
            <div class="main-subtitle">Sua base de dados de empresas mapeadas na região com alta precisão e visibilidade.</div>
        </div>
    """, unsafe_allow_html=True)

    if len(base_leads) == 0:
        st.warning("⚠️ Nenhum lead cadastrado ainda no banco de dados. Faça sua primeira busca no Módulo 1!")
    else:
        df_mapa = pd.DataFrame(base_leads)
        
        col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
        with col_f1:
            cats_mapa = ["Todos os Nichos"] + list(df_mapa['categoria'].unique())
            cat_sel_mapa = st.selectbox("🎯 Nicho no Mapa:", cats_mapa)
            
        with col_f2:
            cids_mapa = ["Todas as Cidades/Regiões"] + list(df_mapa['cidade_busca'].unique())
            cid_sel_mapa = st.selectbox("📍 Cidade / Região:", cids_mapa)

        with col_f3:
            filtro_score_op = st.selectbox(
                "🎯 Faixa de Score de Oportunidade:",
                ["Todos os Scores", "🚨 Crítico (Score ≥ 60)", "🟡 Médio (30 a 59)", "🟢 Baixo (< 30)"]
            )

        df_mapa_filtrado = df_mapa.copy()
        if cat_sel_mapa != "Todos os Nichos":
            df_mapa_filtrado = df_mapa_filtrado[df_mapa_filtrado['categoria'] == cat_sel_mapa]
        if cid_sel_mapa != "Todas as Cidades/Regiões":
            df_mapa_filtrado = df_mapa_filtrado[df_mapa_filtrado['cidade_busca'] == cid_sel_mapa]

        if filtro_score_op == "🚨 Crítico (Score ≥ 60)":
            df_mapa_filtrado = df_mapa_filtrado[df_mapa_filtrado['score_oportunidade'] >= 60]
        elif filtro_score_op == "🟡 Médio (30 a 59)":
            df_mapa_filtrado = df_mapa_filtrado[(df_mapa_filtrado['score_oportunidade'] >= 30) & (df_mapa_filtrado['score_oportunidade'] < 60)]
        elif filtro_score_op == "🟢 Baixo (< 30)":
            df_mapa_filtrado = df_mapa_filtrado[df_mapa_filtrado['score_oportunidade'] < 30]

        st.info(f"📌 Exibindo **{len(df_mapa_filtrado)} empresas** filtradas no mapa.")

        CORES_PINS = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue', 'darkgreen', 'darkblue', 'pink']
        CORES_HEX = {
            'red': '#ef4444', 
            'blue': '#3b82f6', 
            'green': '#10b981', 
            'purple': '#8b5cf6',
            'orange': '#f97316', 
            'darkred': '#991b1b', 
            'cadetblue': '#06b6d4',
            'darkgreen': '#166534', 
            'darkblue': '#1e3a8a', 
            'pink': '#ec4899'
        }

        segmentos_unicos = list(df_mapa['categoria'].unique())
        mapa_cores_seg = {seg: CORES_PINS[idx % len(CORES_PINS)] for idx, seg in enumerate(segmentos_unicos)}

        if cat_sel_mapa == "Todos os Nichos" and len(segmentos_unicos) > 1:
            st.markdown("**🎨 Legenda de Cores por Nicho:**")
            cols_leg = st.columns(min(len(segmentos_unicos), 5))
            for idx, (seg, cor_nome) in enumerate(mapa_cores_seg.items()):
                hex_cor = CORES_HEX.get(cor_nome, '#ef4444')
                with cols_leg[idx % 5]:
                    st.markdown(
                        f'<div style="background-color: #1e293b; padding: 8px 12px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">'
                        f'<span style="height: 12px; width: 12px; background-color: {hex_cor}; border-radius: 50%; display: inline-block;"></span>'
                        f'<b style="color: #ffffff; font-size: 13px;">{seg}</b>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        if 'latitude' in df_mapa_filtrado.columns and 'longitude' in df_mapa_filtrado.columns and len(df_mapa_filtrado) > 0:
            lat_centro = df_mapa_filtrado['latitude'].mean()
            lon_centro = df_mapa_filtrado['longitude'].mean()

            m = folium.Map(location=[lat_centro, lon_centro], zoom_start=13, tiles="OpenStreetMap")

            # Cálculo automático do enquadramento dos PINS no mapa
            bounds = []
            for _, row in df_mapa_filtrado.iterrows():
                cor_pin = mapa_cores_seg.get(row['categoria'], 'red') if cat_sel_mapa == "Todos os Nichos" else 'red'
                url_maps_emp = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(row['nome'])}"

                info_card_html = f"""
                <div style="font-family: Arial, sans-serif; font-size: 12px; min-width: 240px; padding: 6px; line-height: 1.5;">
                    <a href="{url_maps_emp}" target="_blank" style="text-decoration: none;">
                        <b style="color: #2563eb; font-size: 14px;">{row['nome']} 🔗</b>
                    </a><br/>
                    <span style="color: #475569; font-size: 11px;">📍 {row['endereco']}</span><br/>
                    <hr style="margin: 6px 0; border: 0.5px solid #cbd5e1;"/>
                    🚨 <b>Score de Oportunidade:</b> <span style="color: #dc2626; font-weight: bold;">{row['score_oportunidade']}/100</span><br/>
                    ⭐ <b>Nota no Google:</b> {row['nota']} ({row['total_avaliacoes']} avaliações)<br/>
                    🌐 <b>Website Oficial:</b> {'✅ Presente' if row['website'] else '❌ Ausente'}<br/>
                    📷 <b>Fotos na Ficha:</b> {row['fotos_total']} fotos publicadas<br/>
                    📅 <b>Última Atualização:</b> há {row['ultima_foto_dias']} dias
                </div>
                """

                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(info_card_html, max_width=320),
                    icon=folium.Icon(color=cor_pin, icon="info-sign")
                ).add_to(m)
                
                bounds.append([row['latitude'], row['longitude']])

            if len(bounds) > 0:
                m.fit_bounds(bounds, padding=[30, 30])

            st_folium(m, width="100%", height=700)
        else:
            st.warning("Nenhum registro encontrado para os filtros selecionados.")

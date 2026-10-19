import os
import io
import csv
import json
import time
import base64
import urllib.parse
from datetime import datetime, date
import re
import unicodedata

import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from PIL import Image as PILImage
from supabase import create_client, Client

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
                "tour_360": False,
                "status_crm": lead.get('status_crm', '🆕 Novo Lead'),
                "pontos_criticos": lead.get('pontos_criticos', []),
                "oportunidades": lead.get('oportunidades', []),
                "score_oportunidade": int(lead.get('score_oportunidade', 0)),
                "anotacoes": lead.get('anotacoes', ''),
                "favorito": bool(lead.get('favorito', False)),
                "data_followup": lead.get('data_followup', str(date.today())),
                "obs_followup": lead.get('obs_followup', '')
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

def atualizar_anotacoes_db(lead_id, novas_anotacoes):
    if not supabase:
        return
    try:
        supabase.table("leads").update({"anotacoes": novas_anotacoes}).eq("id", lead_id).execute()
    except Exception as e:
        st.error(f"Erro ao atualizar anotações: {str(e)}")

def alternar_favorito_db(lead_id, status_atual):
    if not supabase:
        return
    try:
        novo_val = not status_atual
        supabase.table("leads").update({"favorito": novo_val}).eq("id", lead_id).execute()
    except Exception as e:
        st.error(f"Erro ao atualizar favorito: {str(e)}")

def atualizar_followup_db(lead_id, nova_data):
    if not supabase:
        return
    try:
        supabase.table("leads").update({"data_followup": str(nova_data)}).eq("id", lead_id).execute()
    except Exception as e:
        st.error(f"Erro ao atualizar follow-up: {str(e)}")

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
# GERADOR DE PDF DO PANORAMA DE NICHO (MÉTRICA INVERTIDA: MAIS COMPLETA NO TOPO)
# -----------------------------------------------------------------------------
def desenhar_cabecalho_rodape_todas_paginas(canvas, doc):
    canvas.saveState()
    styles = getSampleStyleSheet()
    
    logo_tour = "logo_tour_transparente.png" if os.path.exists("logo_tour_transparente.png") else None
    if logo_tour:
        img_logo = Image(logo_tour, width=170, height=60, kind='proportional')
        img_logo.wrapOn(canvas, 170, 60)
        img_logo.drawOn(canvas, 36, 715)
    else:
        canvas.setFont('Helvetica-Bold', 14)
        canvas.setFillColor(colors.HexColor('#0f172a'))
        canvas.drawString(36, 735, "TOUR360VR")

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

    canvas.setStrokeColor(colors.HexColor('#cbd5e1'))
    canvas.setLineWidth(0.5)
    canvas.line(36, 706, 576, 706)
    
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
    elements.append(Paragraph("DISTRIBUIÇÃO DE EMPRESAS POR NÍVEL DE MATURIDADE DIGITAL", section_heading))
    elements.append(Spacer(1, 2))

    df_pdf = df_nicho.copy()
    df_pdf['score_saude'] = 100 - df_pdf['score_oportunidade']
    
    scores_counts = df_pdf['score_saude'].value_counts().sort_index(ascending=False)
    
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
            
            c_fill = colors.HexColor('#4ade80') if score_val >= 70 else (colors.HexColor('#facc15') if score_val >= 40 else colors.HexColor('#f87171'))
            
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
    elements.append(Paragraph("RANKING DE EMPRESAS AUDITADAS NO SETOR (DA MAIS COMPLETA À MAIS FRACA)", section_heading))
    elements.append(Spacer(1, 4))

    df_pdf_sorted = df_pdf.sort_values(by='score_oportunidade', ascending=True)

    t_data = [[
        Paragraph("<b>EMPRESA</b>", body_style), 
        Paragraph("<b>NOTA</b>", body_center), 
        Paragraph("<b>AVALIAÇÕES</b>", body_center),
        Paragraph("<b>SITE</b>", body_center), 
        Paragraph("<b>SAÚDE DIGITAL</b>", body_center)
    ]]
    
    t_styles = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]

    for idx, row in enumerate(df_pdf_sorted.iterrows()):
        r_data = row[1]
        sc_saude = r_data['score_saude']
        
        if sc_saude >= 70:
            bg_color = colors.HexColor('#86efac')
            txt_color = '#14532d'
        elif sc_saude >= 40:
            bg_color = colors.HexColor('#fde047')
            txt_color = '#713f12'
        else:
            bg_color = colors.HexColor('#fca5a5')
            txt_color = '#7f1d1d'

        p_score = Paragraph(f"<font color='{txt_color}'><b>{sc_saude}/100</b></font>", body_center)

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
# ESTILIZAÇÃO CSS CUSTOMIZADA (TEMA DESIGN PREMIUM - SIDEBAR FIXA SEM SCROLLBAR)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp, .stMarkdown, button, input, textarea, select {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    .stApp {
        background: radial-gradient(1200px 600px at 10% -10%, #172554 0%, #0b1120 45%, #070b14 100%) !important;
    }
    .main { background-color: transparent !important; padding-top: 15px !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1400px; }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        width: 310px !important;
        min-width: 310px !important;
        max-width: 310px !important;
        background: linear-gradient(180deg, #0f172a 0%, #0b1120 100%) !important;
        border-right: 1px solid #1e293b !important;
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

    /* CABEÇALHO PRINCIPAL */
    .main-header {
        background: linear-gradient(135deg, rgba(37,99,235,0.18) 0%, rgba(15,23,42,0.95) 60%);
        color: white; padding: 18px 22px; border-radius: 14px; margin-bottom: 18px;
        border: 1px solid #1e3a8a; margin-top: 5px !important;
        box-shadow: 0 10px 30px -12px rgba(37,99,235,0.45);
        position: relative; overflow: hidden;
    }
    .main-header::before {
        content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
        background: linear-gradient(180deg, #38bdf8, #2563eb);
    }
    .main-title { font-size: 22px; font-weight: 800; margin: 0; color: #f8fafc; letter-spacing: -0.2px; }
    .main-subtitle { font-size: 13px; color: #94a3b8; margin-top: 4px; }

    /* CARDS DE LEAD */
    .lead-card {
        background: linear-gradient(180deg, #111c33 0%, #0f172a 100%);
        border-radius: 14px; padding: 16px 18px;
        margin-bottom: 12px; border: 1px solid #1e293b;
        border-left: 4px solid #2563eb;
        box-shadow: 0 6px 18px -10px rgba(0,0,0,0.6);
        transition: border-color .25s ease, transform .25s ease;
    }
    .lead-card:hover { border-color: #334155; border-left-color: #38bdf8; transform: translateY(-1px); }
    
    /* SCORE */
    .score-box {
        text-align: center; padding: 10px 12px; border-radius: 12px; font-weight: 700;
        width: 140px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .score-high { background: linear-gradient(180deg,#052e16,#064e3b); color: #86efac; border: 1px solid #166534; }
    .score-med  { background: linear-gradient(180deg,#451a03,#78350f); color: #fde047; border: 1px solid #92400e; }
    .score-low  { background: linear-gradient(180deg,#450a0a,#7f1d1d); color: #fca5a5; border: 1px solid #991b1b; }

    .critical-item {
        color: #fca5a5; font-size: 13px; margin-bottom: 6px; font-weight: 500;
        background: rgba(127,29,29,0.18); border: 1px solid rgba(153,27,27,0.35);
        padding: 5px 9px; border-radius: 8px;
    }
    
    .sidebar-title {
        text-align: center; font-size: 16px; font-weight: 800; color: #f8fafc;
        margin-top: -6px; margin-bottom: 12px; letter-spacing: 0.4px;
    }

    /* BOTÕES */
    .stButton>button, .btn-redirect {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        color: #f1f5f9 !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 2px 8px -2px rgba(0,0,0,0.5) !important;
    }
    .stButton>button:hover, .btn-redirect:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 14px rgba(56,189,248,0.35) !important;
        background: linear-gradient(180deg, #1e3a5f 0%, #0f172a 100%) !important;
        color: #ffffff !important;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%) !important;
        border: 1px solid #38bdf8 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px -4px rgba(37,99,235,0.7) !important;
    }

    .btn-redirect {
        display: block; width: 100%; text-align: center; padding: 9px 10px;
        text-decoration: none !important; margin-bottom: 8px; border-radius: 10px;
    }

    /* SCRIPTS */
    .script-box {
        background-color: #0b1220; color: #e2e8f0;
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 13px; line-height: 1.6; padding: 14px 16px;
        border-radius: 10px; border: 1px solid #1e293b;
        border-left: 3px solid #38bdf8;
        white-space: pre-wrap; margin-bottom: 10px;
    }

    /* MÉTRICAS */
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, #111c33 0%, #0f172a 100%);
        border: 1px solid #1e293b; border-radius: 12px; padding: 12px 16px;
        box-shadow: 0 6px 18px -12px rgba(0,0,0,0.7);
    }
    div[data-testid="stMetricLabel"] p { color: #94a3b8 !important; font-weight: 600 !important; font-size: 13px !important; }
    div[data-testid="stMetricValue"] { color: #f8fafc !important; font-weight: 800 !important; }

    /* TÍTULOS E DIVISORES */
    h3 { color: #e2e8f0 !important; font-weight: 700 !important; letter-spacing: -0.1px; }
    hr, div[data-testid="stDivider"] { border-color: #1e293b !important; opacity: 0.8; }

    /* ALERTAS */
    div[data-testid="stAlert"] { border-radius: 10px !important; }

    /* INPUTS */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, textarea {
        border-radius: 10px !important;
        background-color: #0b1220 !important;
        border-color: #1e293b !important;
    }

    /* TABELA */
    div[data-testid="stDataFrame"] {
        border: 1px solid #1e293b; border-radius: 12px; overflow: hidden;
    }
    div[data-testid="stDataFrame"] table th {
        text-align: center !important;
    }

    /* ===== TEMA MINIMALISTA DARK COM GLASSMORPHISM ===== */
    .stApp {
        background: radial-gradient(900px 500px at 15% -5%, rgba(99,102,241,0.18), transparent 60%),
                    radial-gradient(800px 500px at 100% 0%, rgba(14,165,233,0.12), transparent 55%),
                    #05070d !important;
    }

    section[data-testid="stSidebar"] {
        background: rgba(10,14,25,0.55) !important;
        backdrop-filter: blur(22px) saturate(140%) !important;
        -webkit-backdrop-filter: blur(22px) saturate(140%) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }

    .main-header, .lead-card, .script-box, .critical-item,
    div[data-testid="stMetric"], div[data-testid="stDataFrame"],
    div[data-testid="stAlert"], .score-box {
        background: rgba(255,255,255,0.04) !important;
        backdrop-filter: blur(18px) saturate(140%) !important;
        -webkit-backdrop-filter: blur(18px) saturate(140%) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-left: 1px solid rgba(255,255,255,0.08) !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.05) !important;
        border-radius: 16px !important;
    }
    .main-header::before { width: 2px !important; background: rgba(255,255,255,0.35) !important; }
    .lead-card:hover { transform: none !important; border-color: rgba(255,255,255,0.16) !important; }

    .main-title { font-weight: 600 !important; letter-spacing: -0.3px !important; color: #f5f7fb !important; }
    .main-subtitle { color: #8b93a7 !important; }

    .score-high, .score-med, .score-low {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
    }
    .score-high { color: #6ee7b7 !important; }
    .score-med  { color: #fde68a !important; }
    .score-low  { color: #fca5a5 !important; }
    .critical-item { color: #e2e8f0 !important; background: rgba(248,113,113,0.06) !important; border-color: rgba(248,113,113,0.18) !important; }

    .stButton>button, .btn-redirect {
        background: rgba(255,255,255,0.05) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 12px !important;
        color: #e5e7eb !important;
        box-shadow: none !important;
        font-weight: 500 !important;
    }
    .stButton>button:hover, .btn-redirect:hover {
        background: rgba(255,255,255,0.10) !important;
        border-color: rgba(255,255,255,0.22) !important;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.05) !important;
        color: #ffffff !important;
    }
    .stButton>button[kind="primary"] {
        background: rgba(99,102,241,0.28) !important;
        border: 1px solid rgba(129,140,248,0.45) !important;
        box-shadow: none !important;
    }
    .stButton>button[kind="primary"]:hover {
        background: rgba(99,102,241,0.42) !important;
    }

    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, textarea {
        background-color: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
    }

    h1, h2, h3 { color: #f1f5f9 !important; font-weight: 600 !important; }
    hr, div[data-testid="stDivider"] { border-color: rgba(255,255,255,0.06) !important; }

    /* ===== AJUSTE FINO: VISUAL DA REFERÊNCIA GESTÃO MENSAL (DARK + GLASS) ===== */
    .stApp {
        background:
            radial-gradient(900px 500px at 20% -10%, rgba(59,130,246,0.14), transparent 60%),
            radial-gradient(700px 500px at 95% 10%, rgba(168,85,247,0.08), transparent 55%),
            linear-gradient(180deg, #0b1020 0%, #070a14 100%) !important;
    }

    .main-header, .lead-card, .script-box, div[data-testid="stMetric"],
    div[data-testid="stDataFrame"], div[data-testid="stAlert"], div[data-testid="stForm"] {
        background: rgba(20,26,44,0.55) !important;
        border: 1px solid rgba(148,163,184,0.14) !important;
        border-radius: 14px !important;
        box-shadow: 0 10px 30px -12px rgba(0,0,0,0.6) !important;
    }

    .main-header { padding: 20px 24px !important; overflow: hidden; }
    .main-header::before {
        content: ""; position: absolute; left: 0; right: 0; top: 0; bottom: auto;
        width: auto !important; height: 3px !important;
        background: linear-gradient(90deg,#ef4444,#f59e0b,#22c55e,#3b82f6,#a855f7) !important;
    }
    .main-title { font-size: 22px !important; font-weight: 700 !important; color: #ffffff !important; }
    .main-subtitle { color: #94a3b8 !important; }

    .lead-card { border-left: 1px solid rgba(148,163,184,0.14) !important; }
    .lead-card:hover { border-color: rgba(59,130,246,0.35) !important; }

    .stButton>button, .btn-redirect {
        background: rgba(30,41,59,0.55) !important;
        border: 1px solid rgba(148,163,184,0.18) !important;
        border-radius: 999px !important;
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }
    .stButton>button:hover, .btn-redirect:hover {
        border-color: rgba(59,130,246,0.6) !important;
        box-shadow: 0 0 14px rgba(59,130,246,0.35) !important;
        background: rgba(37,99,235,0.15) !important;
    }
    .stButton>button[kind="primary"] {
        background: rgba(37,99,235,0.22) !important;
        border: 1px solid rgba(59,130,246,0.7) !important;
        box-shadow: 0 0 16px rgba(59,130,246,0.35) !important;
        color: #ffffff !important;
    }

    div[data-baseweb="tab-list"] { border-bottom: 1px solid rgba(148,163,184,0.14) !important; }
    button[data-baseweb="tab"] { color: #94a3b8 !important; font-weight: 500 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #f87171 !important; }
    div[data-baseweb="tab-highlight"] { background-color: #f87171 !important; }

    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, textarea {
        background-color: rgba(15,23,42,0.6) !important;
        border: 1px solid rgba(148,163,184,0.16) !important;
        border-radius: 10px !important;
    }

    div[data-testid="stAlert"] {
        background: rgba(30,58,138,0.22) !important;
        border: 1px solid rgba(59,130,246,0.3) !important;
        color: #dbeafe !important;
    }
    /* ===== AJUSTES: BOTÕES COM CONTORNO BRANCO, NEON NO ATIVO E RELEVO NO HOVER ===== */
    .stButton>button, .btn-redirect {
        border: 1px solid #ffffff !important;
        background: rgba(255,255,255,0.03) !important;
        color: #ffffff !important;
        transition: transform .25s ease, box-shadow .25s ease, background .25s ease !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        font-size: 12.5px !important;
        padding-left: 8px !important;
        padding-right: 8px !important;
    }
    .stButton>button:hover, .btn-redirect:hover {
        transform: scale(1.06) !important;
        border-color: #ffffff !important;
        background: rgba(255,255,255,0.10) !important;
        box-shadow: 0 0 10px rgba(255,255,255,0.45), 0 10px 24px -8px rgba(255,255,255,0.25) !important;
    }
    .stButton>button:active { transform: scale(1.02) !important; }
    .stButton>button[kind="primary"] {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid #ffffff !important;
        color: #ffffff !important;
        box-shadow: 0 0 6px #ffffff, 0 0 16px rgba(255,255,255,0.55), inset 0 0 8px rgba(255,255,255,0.15) !important;
    }
    .stButton>button[kind="primary"]:hover {
        transform: scale(1.06) !important;
        background: rgba(255,255,255,0.14) !important;
        box-shadow: 0 0 10px #ffffff, 0 0 26px rgba(255,255,255,0.65), inset 0 0 8px rgba(255,255,255,0.2) !important;
    }

    /* ALINHAMENTO E CORTES NOS CARDS */
    div[data-testid="column"] { min-width: 0 !important; }
    div[data-testid="stWidgetLabel"] {
        min-height: 2.6rem !important;
        display: flex !important;
        align-items: flex-end !important;
    }
    div[data-testid="stWidgetLabel"] p { line-height: 1.3 !important; white-space: normal !important; }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stDateInput"] input {
        font-size: 12.5px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    .lead-card h2 { white-space: normal !important; overflow-wrap: anywhere !important; line-height: 1.25 !important; }
    .lead-card p { white-space: normal !important; overflow-wrap: anywhere !important; }
    .critical-item { overflow-wrap: anywhere !important; }

    /* ===== AJUSTE: BOTÕES MENOS ARREDONDADOS E ABA ATIVA EM VIDRO ===== */
    .stButton>button, .btn-redirect {
        border-radius: 6px !important;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.22) 0%, rgba(255,255,255,0.06) 100%) !important;
        backdrop-filter: blur(14px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(14px) saturate(160%) !important;
        border: 1px solid rgba(255,255,255,0.45) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.35), 0 8px 24px -8px rgba(0,0,0,0.5) !important;
        color: #ffffff !important;
    }
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, rgba(255,255,255,0.28) 0%, rgba(255,255,255,0.10) 100%) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.4), 0 12px 28px -8px rgba(0,0,0,0.55) !important;
    }

    /* ===== AJUSTE: CAMPOS E CONTROLES NA MESMA LINHA, SEM CORTES ===== */
    div[data-testid="stWidgetLabel"] {
        min-height: 3rem !important;
        height: 3rem !important;
    }
    div[data-testid="stWidgetLabel"] p {
        font-size: 12px !important;
        line-height: 1.25 !important;
    }
    div[data-testid="stForm"] div[data-testid="stHorizontalBlock"],
    div[data-testid="column"] div[data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        align-items: flex-start !important;
    }
    div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
    div[data-testid="column"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        min-width: 120px !important;
    }
    div[data-testid="column"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"] button,
    div[data-testid="column"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"] button p {
        white-space: normal !important;
        line-height: 1.2 !important;
        text-overflow: clip !important;
    }
    div[data-testid="stDateInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        min-width: 0 !important;
    }

    /* ===== AJUSTE FINAL: FUNDO AZUL EM DEGRADÊ, TÍTULOS, BOTÕES DA SIDEBAR E CARDS ===== */
    .stApp {
        background:
            radial-gradient(1000px 600px at 0% 0%, rgba(37,99,235,0.38) 0%, transparent 60%),
            radial-gradient(900px 600px at 100% 100%, rgba(14,165,233,0.20) 0%, transparent 55%),
            linear-gradient(160deg, #0b1d3a 0%, #071026 45%, #050914 100%) !important;
    }
    .block-container { padding-top: 3.4rem !important; }
    .main-header { margin-top: 10px !important; }

    section[data-testid="stSidebar"] .stButton>button {
        background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%) !important;
        border: 1px solid rgba(255,255,255,0.85) !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stButton>button:hover {
        transform: scale(1.04) !important;
        border-color: #ffffff !important;
        box-shadow: 0 0 12px rgba(255,255,255,0.35) !important;
    }
    section[data-testid="stSidebar"] .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, rgba(37,99,235,0.75) 0%, rgba(14,165,233,0.35) 55%, rgba(15,23,42,0.6) 100%) !important;
        border: 1px solid #ffffff !important;
        color: #ffffff !important;
        box-shadow: 0 0 10px rgba(56,189,248,0.45), inset 0 1px 0 rgba(255,255,255,0.25) !important;
    }
    section[data-testid="stSidebar"] .stButton>button[kind="primary"]:hover {
        transform: scale(1.04) !important;
        box-shadow: 0 0 16px rgba(56,189,248,0.6), inset 0 1px 0 rgba(255,255,255,0.3) !important;
    }

    .lead-card { width: 100% !important; box-sizing: border-box !important; overflow: visible !important; }
    .lead-card > div > div:first-child { min-width: 0 !important; flex: 1 1 auto !important; }
    .score-box { width: auto !important; min-width: 150px !important; max-width: 200px !important; flex-shrink: 0 !important; box-sizing: border-box !important; }
    .lead-card h2, .lead-card p { white-space: normal !important; overflow-wrap: anywhere !important; word-break: break-word !important; }
    div[data-testid="stMetric"] { min-width: 0 !important; }
    div[data-testid="stMetricValue"] { white-space: normal !important; overflow: visible !important; font-size: 1.6rem !important; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE E CONTROLE DE ETAPA (MÓDULOS 1 A 5)
# -----------------------------------------------------------------------------
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1

def mudar_etapa(nova_etapa):
    st.session_state.etapa = nova_etapa
    st.rerun()

# -----------------------------------------------------------------------------
# INTEGRAÇÃO DE BUSCA REAL VIA GOOGLE PLACES API (PAGINAÇÃO BLINDADA)
# -----------------------------------------------------------------------------
def buscar_google_places_api(nome_empresa, nicho, cidade, bairro, rua, raio_km, api_key, limite=20):
    termos = []
    if nome_empresa: termos.append(nome_empresa.strip())
    if nicho: termos.append(nicho.strip())
    if rua: termos.append(rua.strip())
    if bairro: termos.append(bairro.strip())
    if cidade: termos.append(cidade.strip())
    
    query_str = " ".join(termos)
    raio_metros = int(raio_km * 1000)
    
    base_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={urllib.parse.quote(query_str)}&radius={raio_metros}&language=pt-BR&key={api_key}"
    
    leads = []
    seen_place_ids = set()
    next_page_token = None
    
    try:
        max_paginas = max(1, (limite // 20) + 1)
        for pagina in range(max_paginas):
            if len(leads) >= limite:
                break

            url_requisicao = base_url
            if pagina > 0:
                if not next_page_token:
                    break
                url_requisicao = f"https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={next_page_token}&key={api_key}"
                time.sleep(3.5)

            response = requests.get(url_requisicao, timeout=12)
            data = response.json()
            status = data.get("status")

            if status != "OK":
                if status == "ZERO_RESULTS" and len(leads) == 0:
                    st.warning("⚠️ O Google Maps não encontrou empresas para este termo exato dentro do raio especificado. Tente aumentar o raio de km.")
                break

            results = data.get("results", [])
            if not results:
                break

            for place in results:
                if len(leads) >= limite:
                    break

                place_id = place.get("place_id")
                if place_id in seen_place_ids:
                    continue
                seen_place_ids.add(place_id)

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
                photos = det_res.get("photos", place.get("photos", [])) or []
                
                if photos and photos[0].get('photo_reference'):
                    foto_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photos[0].get('photo_reference')}&key={api_key}"
                else:
                    foto_url = ""

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
                    pontos_criticos.append(f"Volume crítico de avaliações ({total_avaliacoes} total)")
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

                nome_normalizado = unicodedata.normalize('NFKD', nome.lower()).encode('ASCII', 'ignore').decode('ASCII')
                nome_slug = re.sub(r'[^a-zA-Z0-9]', '', nome_normalizado)
                instagram_url = f"https://instagram.com/{nome_slug}"
                facebook_url = f"https://facebook.com/{nome_slug}"

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
                    "instagram": instagram_url,
                    "facebook": facebook_url,
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
                    "score_oportunidade": min(score, 100),
                    "anotacoes": "",
                    "favorito": False,
                    "data_followup": str(date.today()),
                    "obs_followup": ""
                }
                
                salvar_lead_db(lead_obj)
                leads.append(lead_obj)

            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break

        return leads
    except Exception as e:
        st.error(f"Erro na requisição à API do Google Places: {str(e)}")
    return None

def minerar_e_auditar_negocios(nome_empresa, nicho, cidade, bairro, rua, raio_km, limite=20):
    api_key = st.secrets.get("GOOGLE_API_KEY", None) or os.getenv("GOOGLE_API_KEY", None)
    
    if api_key:
        api_key_limpa = api_key.strip().replace('"', '').replace("'", "")
        leads_reais = buscar_google_places_api(nome_empresa, nicho, cidade, bairro, rua, raio_km, api_key_limpa, limite)
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
        "Categoria / Nicho", "Status Comercial CRM", "Favorito?", "Data Follow-up", "Endereço Completo", "Telefone Fixo", 
        "WhatsApp", "Possui Website?", "Website URL", "Site Seguro (HTTPS)?", 
        "Instagram URL", "Facebook URL", "Nota Média Google", "Total Avaliações", 
        "Ficha Reivindicada?", "Qtd. Fotos Publicadas", "Dias Desde Última Foto", 
        "Possui Tour 360°?", "Anotações CRM", "Pontos Críticos Identificados", "Score de Oportunidade"
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
            "Sim" if row.get("favorito") else "Não",
            row.get("data_followup", ""),
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
            "Não",
            row.get("anotacoes", ""),
            criticos_str,
            row.get("score_oportunidade", "")
        ])

    return output.getvalue().encode('utf-8')

# -----------------------------------------------------------------------------
# BARRA LATERAL (COM CENTRAL DE NOTIFICAÇÕES DE FOLLOW-UP E CENTRALIZAÇÃO)
# -----------------------------------------------------------------------------
base_leads = carregar_todos_leads_db()

hoje_str = str(date.today())
pendentes_hoje = []
for l in base_leads:
    dt_fu = l.get('data_followup')
    if not dt_fu:
        dt_fu = hoje_str
    
    st_crm = l.get('status_crm', '')
    if dt_fu <= hoje_str and st_crm not in ['🤝 Cliente Fechado', '❌ Recusado']:
        pendentes_hoje.append(l)

with st.sidebar:
    st.markdown('<div class="sidebar-title">Radar Comercial</div>', unsafe_allow_html=True)
    
    if os.path.exists("logo_tour_transparente.png"):
        c1, c2, c3 = st.columns([1.2, 3.6, 1.2])
        with c2: st.image("logo_tour_transparente.png", use_container_width=True)
    
    if os.path.exists("logo_okamoto.png"):
        c1, c2, c3 = st.columns([0.8, 4.4, 0.8])
        with c2: st.image("logo_okamoto.png", use_container_width=True)

    st.divider()

    if len(pendentes_hoje) > 0:
        st.markdown(f"""
            <div style="background: linear-gradient(180deg,#7f1d1d,#450a0a); border: 1px solid #991b1b; padding: 12px; border-radius: 12px; margin-bottom: 14px; text-align: center; box-shadow: 0 6px 16px -8px rgba(220,38,38,0.5);">
                <span style="color: #fca5a5; font-weight: 700; font-size: 13px; letter-spacing: 0.3px;">🔔 Notificação Ativa</span><br/>
                <span style="color: #ffffff; font-size: 12px;"><b>{len(pendentes_hoje)} retornos pendentes</b> para hoje ou atrasados!</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background: linear-gradient(180deg,#064e3b,#022c22); border: 1px solid #065f46; padding: 10px; border-radius: 12px; margin-bottom: 14px; text-align: center;">
                <span style="color: #6ee7b7; font-weight: 700; font-size: 12px;">✅ Agenda em dia! Sem pendências.</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='text-align: center; font-weight: 700; font-size: 13px; letter-spacing: 1px; text-transform: uppercase; color:#94a3b8; margin-bottom: 10px;'>Módulos</div>", unsafe_allow_html=True)
    
    if st.button("1️⃣ Dashboard Executivo", use_container_width=True, type="primary" if st.session_state.etapa == 1 else "secondary"):
        mudar_etapa(1)
    if st.button("2️⃣ Buscador de Clientes", use_container_width=True, type="primary" if st.session_state.etapa == 2 else "secondary"):
        mudar_etapa(2)
    if st.button("3️⃣ Base & CRM de Leads", use_container_width=True, type="primary" if st.session_state.etapa == 3 else "secondary"):
        mudar_etapa(3)
    if st.button("4️⃣ Panorama de Nicho", use_container_width=True, type="primary" if st.session_state.etapa == 4 else "secondary"):
        mudar_etapa(4)
    if st.button("5️⃣ Mapa & Rota de Visitas", use_container_width=True, type="primary" if st.session_state.etapa == 5 else "secondary"):
        mudar_etapa(5)

    st.divider()
    st.markdown(f"""
        <div style='text-align: center; font-size: 12px; background:#0b1220; border:1px solid #1e293b; border-radius:12px; padding:10px;'>
            <span style='color:#94a3b8;'>☁️ Supabase Nuvem</span><br/>
            <b style='font-size:15px; color:#f8fafc;'>{len(base_leads)} leads salvos</b>
        </div>
    """, unsafe_allow_html=True)

    if len(base_leads) > 0:
        if st.button("🗑️ Limpar Banco de Dados", use_container_width=True):
            limpar_banco_dados()
            mudar_etapa(1)

# -----------------------------------------------------------------------------
# MÓDULO 1: DASHBOARD EXECUTIVO
# -----------------------------------------------------------------------------
if st.session_state.etapa == 1:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📈 Dashboard Executivo | Okamoto Mídias & Tour360VR</h1>
            <div class="main-subtitle">Visão geral do seu funil de prospecção e oportunidades de mercado mapeadas.</div>
        </div>
    """, unsafe_allow_html=True)

    if len(base_leads) == 0:
        st.warning("⚠️ Nenhum lead cadastrado ainda no banco de dados. Vá até o Módulo 2 para realizar sua primeira busca!")
    else:
        df_dash = pd.DataFrame(base_leads)

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Total de Leads na Base", len(df_dash))
        with col_m2:
            favoritos_tot = len(df_dash[df_dash['favorito'] == True])
            st.metric("⭐ Leads Favoritos / Quentes", favoritos_tot)
        with col_m3:
            fechados = len(df_dash[df_dash['status_crm'] == '🤝 Cliente Fechado'])
            st.metric("🤝 Clientes Fechados", fechados)
        with col_m4:
            sem_site_tot = len(df_dash[df_dash['website'] == ''])
            st.metric("🌐 Sem Website Oficial", f"{(sem_site_tot / len(df_dash) * 100):.1f}%")

        st.divider()

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("### 📊 Distribuição por Status no CRM")
            status_counts = df_dash['status_crm'].value_counts()
            st.bar_chart(status_counts)

        with col_c2:
            st.markdown("### 🏷️ Nichos / Categorias Mapeadas")
            nicho_counts = df_dash['categoria'].value_counts().head(8)
            st.bar_chart(nicho_counts)

        st.divider()
        st.markdown("### 🚨 Leads com Follow-up para Hoje ou Atrasados:")
        if len(pendentes_hoje) > 0:
            st.markdown(f"Você possui **{len(pendentes_hoje)} leads** pendentes de retorno na agenda:")
            for r_lead in pendentes_hoje[:5]:
                st.markdown(f"- **{r_lead['nome']}** ({r_lead['cidade_busca']}) — Status: `{r_lead['status_crm']}` — Retorno agendado para: **{r_lead['data_followup']}**")
        else:
            st.success("🎉 Nenhum follow-up pendente para hoje! Sua agenda está em dia.")

# -----------------------------------------------------------------------------
# MÓDULO 2: BUSCADOR DE CLIENTES
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 2:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🔎 Radar e Mineração de Mercado Local</h1>
            <div class="main-subtitle">Varredura de perfis no Google Maps por Nome, Nicho, Cidade, Bairro, Rua e Raio de Distância (km).</div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("form_busca"):
        col_nome_emp, col1, col2, col3, col4, col5, col6 = st.columns([2.4, 2.2, 2, 2, 2.2, 1.2, 1.2])
        with col_nome_emp: nome_empresa_input = st.text_input("Nome da Empresa (Opcional)", value="", help="Ex: Clínica Sorria ou Hotel X")
        with col1: nicho_input = st.text_input("Nicho / Categoria (Opcional)", value="", help="Deixe em branco para buscar empresas gerais no local")
        with col2: cidade_input = st.text_input("Cidade / Município", value="Ribeirão Preto")
        with col3: rua_input = st.text_input("Rua / Avenida (Opcional)", value="", help="Ex: Av. Independência")
        with col4: bairro_input = st.text_input("Bairro / Região (Opcional)", value="", help="Deixe em branco para amplitude de busca na cidade")
        with col5: raio_input = st.number_input("Raio (km)", min_value=1, max_value=50, value=10, step=1, help="Distância máxima de busca a partir do centro da localidade")
        with col6: limite_input = st.number_input("Qtd. Máxima", min_value=20, max_value=70, value=40, step=5)
        
        btn_minar = st.form_submit_button("🚀 Iniciar Varredura Profunda", use_container_width=True)

    if btn_minar:
        with st.spinner(f"Varrendo Google Maps num raio de {raio_input} km, auditando presença web e salvando na nuvem..."):
            time.sleep(1)
            novos = minerar_e_auditar_negocios(nome_empresa_input, nicho_input, cidade_input, bairro_input, rua_input, raio_input, limite_input)
            if novos and len(novos) > 0:
                mudar_etapa(3)

    if len(base_leads) > 0:
        st.divider()
        st.info(f"O seu banco na nuvem possui **{len(base_leads)} leads salvos permanentemente**.")
        if st.button("Ver Base Completa de Leads ➡️", type="primary"):
            mudar_etapa(3)

# -----------------------------------------------------------------------------
# MÓDULO 3: BASE DE LEADS & CRM DE VENDAS
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 3:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📊 Base de Leads e Gerenciador CRM</h1>
            <div class="main-subtitle">Seus leads permanecem salvos na nuvem. Atualize status, anotações, follow-up e exiba planilhas com facilidade.</div>
        </div>
    """, unsafe_allow_html=True)

    if len(base_leads) == 0:
        st.warning("⚠️ Nenhum lead cadastrado ainda no banco de dados. Faça sua primeira busca no Módulo 2!")
    else:
        df_leads_crm = pd.DataFrame(base_leads)

        col_f_busca, col_f_nicho, col_f_cid, col_f_status, col_f_fav, col_export = st.columns([2, 1.8, 1.8, 1.8, 1.6, 2])

        with col_f_busca:
            filtro_nome_busca = st.text_input("🔍 Buscar por Nome:", value="", placeholder="Ex: Nome da empresa")

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

        with col_f_fav:
            filtro_favorito = st.selectbox(
                "Filtro:",
                ["Todos", "⭐ Favoritos / Quentes"]
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
        if filtro_nome_busca.strip():
            termo_busca = filtro_nome_busca.strip().lower()
            resultados_filtrados = [r for r in resultados_filtrados if termo_busca in r['nome'].lower()]

        if filtro_nicho != "Todos os Nichos":
            resultados_filtrados = [r for r in resultados_filtrados if r['categoria'] == filtro_nicho]
        if filtro_cidade != "Todas as Cidades":
            resultados_filtrados = [r for r in resultados_filtrados if r['cidade_busca'] == filtro_cidade]
        if filtro_status != "Todos os Status":
            resultados_filtrados = [r for r in resultados_filtrados if r['status_crm'] == filtro_status]
        if filtro_favorito == "⭐ Favoritos / Quentes":
            resultados_filtrados = [r for r in resultados_filtrados if r.get('favorito') == True]

        st.markdown(f"Exibindo **{len(resultados_filtrados)}** oportunidades salvas:")

        for lead in resultados_filtrados:
            score = lead['score_oportunidade']
            score_class = "score-high" if score >= 60 else ("score-med" if score >= 30 else "score-low")
            score_label = "ALTA OPORTUNIDADE" if score >= 60 else ("MÉDIA OPORTUNIDADE" if score >= 30 else "BAIXA OPORTUNIDADE")

            is_fav = lead.get('favorito', False)
            fav_label = "⭐ Favorito" if is_fav else "☆ Favoritar"

            st.markdown(f"""
                <div class="lead-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px; gap: 12px;">
                        <div>
                            <h2 style="margin: 0; color: #f8fafc; font-size: 20px; font-weight: 800; letter-spacing: -0.2px;">{lead['nome']}</h2>
                            <p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 12.5px;">📍 {lead['endereco']} &nbsp;•&nbsp; 🏷️ {lead['categoria']}</p>
                        </div>
                        <div class="score-box {score_class}">
                            <div style="font-size: 9.5px; font-weight: 700; letter-spacing: 0.6px;">SCORE OPORTUNIDADE</div>
                            <div style="font-size: 20px; font-weight: 800;">{score} / 100</div>
                            <div style="font-size: 8.5px; font-weight: 700;">{score_label}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col_img, col_details1, col_details2, col_actions = st.columns([2.4, 2.4, 2.4, 2.4])

            with col_img:
                foto_lead = lead.get('foto_url', '')
                if foto_lead and foto_lead.startswith("http"):
                    try:
                        api_key_atual = st.secrets.get("GOOGLE_API_KEY", None) or os.getenv("GOOGLE_API_KEY", "")
                        if "key=" not in foto_lead and api_key_atual:
                            foto_lead_auth = f"{foto_lead}&key={api_key_atual.strip().replace('"', '').replace("'", "")}"
                        else:
                            foto_lead_auth = foto_lead
                            
                        resp_img = requests.get(foto_lead_auth, timeout=5)
                        if resp_img.status_code == 200:
                            st.image(resp_img.content, caption="Foto da Ficha do Google", use_container_width=True)
                        else:
                            st.info("📷 Sem foto")
                    except Exception:
                        st.info("📷 Sem foto")
                else:
                    st.info("📷 Sem foto")
                
                # ALINHADO EM UMA ÚNICA LINHA HORIZONTAL COM PROPORÇÃO OTIMIZADA
                c_fav, c_st, c_fu = st.columns([1.5, 2.2, 1.8])
                
                with c_fav:
                    if st.button(fav_label, key=f"fav_btn_{lead['id']}", use_container_width=True):
                        alternar_favorito_db(lead['id'], is_fav)
                        st.rerun()

                status_opcoes = ["🆕 Novo Lead", "💬 Em Abordagem", "🛠️ Diagnóstico Gerado", "🤝 Cliente Fechado", "❌ Recusado"]
                idx_atual = status_opcoes.index(lead['status_crm']) if lead['status_crm'] in status_opcoes else 0
                
                with c_st:
                    novo_st = st.selectbox("Status:", status_opcoes, index=idx_atual, key=f"crm_st_{lead['id']}", label_visibility="collapsed")
                    if novo_st != lead['status_crm']:
                        atualizar_status_crm(lead['id'], novo_st)
                        st.toast("Status atualizado na nuvem!")
                        st.rerun()

                dt_atual_str = lead.get('data_followup', str(date.today()))
                try:
                    dt_obj = datetime.strptime(dt_atual_str, '%Y-%m-%d').date()
                except Exception:
                    dt_obj = date.today()

                with c_fu:
                    nova_data_fu = st.date_input("Retorno:", value=dt_obj, key=f"dt_fu_{lead['id']}", label_visibility="collapsed")
                    if str(nova_data_fu) != dt_atual_str:
                        atualizar_followup_db(lead['id'], nova_data_fu)
                        st.toast("Data de follow-up atualizada!")

            with col_details1:
                st.markdown("**📊 Indicadores no Google:**")
                st.markdown(f"- **Nota Média:** ⭐ {lead['nota']} ({lead['total_avaliacoes']} avaliações)")
                st.markdown(f"- **Ficha Reivindicada?** {'✅ Sim' if lead['reivindicada'] else '❌ **NÃO REIVINDICADA**'}")
                st.markdown(f"- **Fotos na Ficha:** {lead['fotos_total']} fotos (última há {lead['ultima_foto_dias']} dias)")
                st.markdown(f"- **Tour 360°:** ❌ **Ausente (Oportunidade)**")

            with col_details2:
                st.markdown("**🚨 Pontos Críticos Encontrados:**")
                criticos_lista = lead['pontos_criticos'] if isinstance(lead['pontos_criticos'], list) else json.loads(lead['pontos_criticos'] or '[]')
                for pc in criticos_lista:
                    st.markdown(f"<div class='critical-item'>❌ {pc}</div>", unsafe_allow_html=True)

            with col_actions:
                st.markdown("**🌐 Presença Web & Mídias:**")
                st.markdown(f"- **Website:** {lead['website'] if lead['website'] else '❌ Sem site'}")
                
                insta_link = lead.get('instagram', '')
                if insta_link:
                    st.markdown(f"- **Instagram:** [Abrir Perfil]({insta_link})")
                else:
                    st.markdown("- **Instagram:** ❌ Não informado")

                fb_link = lead.get('facebook', '')
                if fb_link:
                    st.markdown(f"- **Facebook:** [Abrir Página]({fb_link})")
                else:
                    st.markdown("- **Facebook:** ❌ Não informado")

                st.markdown(f"- **Maps:** [Ver no Google Maps](https://www.google.com/maps/search/?api=1&query={lead['nome'].replace(' ', '+')})")

                st.markdown(f'<a href="{URL_SISTEMA_DIAGNOSTICO}" target="_blank" class="btn-redirect">🛠️ Abrir no Diagnóstico Tour360VR</a>', unsafe_allow_html=True)

                if lead['whatsapp']:
                    msg_wa = f"Olá! Tudo bem?\nMeu nome é Rubens Okamoto, da Okamoto Mídias Visuais e do Tour360VR.\nEstava analisando a presença da {lead['nome']} no Google, e identifiquei 3 pontos onde a visibilidade do espaço de vocês pode ser bastante ampliada em relação aos concorrentes da região.\nMontei um relatório curto de diagnóstico em PDF. Posso te enviar por aqui para você dar uma olhada?"
                    link_wa = f"https://wa.me/55{lead['whatsapp']}?text={urllib.parse.quote(msg_wa)}"
                    st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background: linear-gradient(135deg,#25D366,#128C7E); color:white; border:none; padding:9px; border-radius:10px; font-weight:700; cursor:pointer; margin-bottom:8px; box-shadow:0 4px 12px -4px rgba(37,211,102,0.6);">💬 WhatsApp</button></a>', unsafe_allow_html=True)

                assunto_email = f"Oportunidade de Presença Digital: {lead['nome']} no Google"
                corpo_email = f"""Olá! Analisei o perfil da {lead['nome']} no Google e gostaria de compartilhar uma oportunidade importante.

Identifiquei 3 pontos críticos que estão impactando a confiança de novos clientes no setor de {lead['categoria']}:
1. Ausência de Tour Virtual 360° navegável.
2. Perfil estático com fotos e informações defasadas.
3. Falta de otimização de presença digital.

Temos soluções para transformar a vitrine do seu negócio no Google. Fico à disposição para conversarmos!

Atenciosamente,
Rubens Okamoto
TOUR360VR | Okamoto Mídias Visuais
(16) 99133-2121 | tour360vr.com.br"""
                
                link_mailto = f"mailto:?subject={urllib.parse.quote(assunto_email)}&body={urllib.parse.quote(corpo_email)}"
                st.markdown(f'<a href="{link_mailto}" target="_blank"><button style="width:100%; background: linear-gradient(135deg,#2563eb,#0ea5e9); color:white; border:none; padding:9px; border-radius:10px; font-weight:700; cursor:pointer; margin-bottom:8px; box-shadow:0 4px 12px -4px rgba(37,99,235,0.6);">✉️ Enviar E-mail Pronto</button></a>', unsafe_allow_html=True)

            st.markdown("**📝 Anotações & Histórico de Contato:**")
            anotacoes_atuais = lead.get('anotacoes', '') or ''
            novas_anotacoes = st.text_area("Anotações:", value=anotacoes_atuais, height=80, key=f"txt_anot_{lead['id']}", label_visibility="collapsed", placeholder="Digite histórico de reuniões, conversas ou recados aqui...")
            
            if novas_anotacoes != anotacoes_atuais:
                atualizar_anotacoes_db(lead['id'], novas_anotacoes)

            with st.expander(f"✉️ **Scripts de Vendas e Abordagem Detalhada ({lead['nome']})**"):
                st.markdown("**1) Abordagem Inicial — WhatsApp**")
                script_wa = f"""Olá! Tudo bem?
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

Rubens Okamoto
TOUR360VR | Okamoto Mídias Visuais
(16) 99133-2121 | tour360vr.com.br"""
                st.markdown(f'<div class="script-box">{script_email}</div>', unsafe_allow_html=True)

                st.markdown("**3) Follow-up 48h — Pós-Envio do Diagnóstico**")
                script_follow = f"Olá! Só checando por aqui — conseguiu analisar o diagnóstico em PDF da {lead['nome']} que te enviei? Fico no aguardo para tirar qualquer dúvida!"
                st.markdown(f'<div class="script-box">{script_follow}</div>', unsafe_allow_html=True)

            st.divider()

# -----------------------------------------------------------------------------
# MÓDULO 4: PANORAMA DE NICHO
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 4:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📈 Panorama de Mercado & Inteligência de Nicho</h1>
            <div class="main-subtitle">Análise detalhada por categoria e município ordenada por maior oportunidade comercial.</div>
        </div>
    """, unsafe_allow_html=True)

    if len(base_leads) == 0:
        st.warning("⚠️ Nenhum lead cadastrado ainda no banco de dados. Faça sua primeira busca no Módulo 2!")
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
            pdf_bytes_nicho = gerar_pdf_panorama_nicho(nicho_selecionado, df_filtrado)
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
        st.markdown(f"### 📋 Ranking do Nicho **{nicho_selecionado}** (Ordem de Prospecção):")
        
        df_exibicao = pd.DataFrame({
            'EMPRESA': df_filtrado_sorted['nome'],
            'CIDADE': df_filtrado_sorted['cidade_busca'],
            'SCORE OPORTUNIDADE': df_filtrado_sorted['score_oportunidade'].apply(lambda x: f"{x}/100"),
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
                "SCORE OPORTUNIDADE": st.column_config.Column("SCORE OPORTUNIDADE", width="small", alignment="center"),
                "NOTA": st.column_config.Column("NOTA", width="small", alignment="center"),
                "AVALIAÇÕES": st.column_config.Column("AVALIAÇÕES", width="small", alignment="center"),
                "WEBSITE": st.column_config.LinkColumn("WEBSITE", width="large")
            }
        )

# -----------------------------------------------------------------------------
# MÓDULO 5: MAPA & ROTA DE VISITAS
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 5:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🗺️ Mapa & Planejador de Rotas de Visitas</h1>
            <div class="main-subtitle">Visualize leads no mapa e organize seu itinerário sequencial com rotas de navegação passo a passo.</div>
        </div>
    """, unsafe_allow_html=True)

    if len(base_leads) == 0:
        st.warning("⚠️ Nenhum lead cadastrado ainda no banco de dados. Faça sua primeira busca no Módulo 2!")
    else:
        df_mapa = pd.DataFrame(base_leads)
        
        col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
        with col_f1:
            cats_mapa = ["Todos os Nichos"] + list(df_mapa['categoria'].unique())
            cat_sel_mapa = st.selectbox("🎯 Nicho no Roteiro:", cats_mapa)
            
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

        st.info(f"📌 Exibindo **{len(df_mapa_filtrado)} empresas** no mapa e no itinerário de visitas.")

        CORES_PINS = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue', 'darkgreen', 'darkblue', 'pink']
        CORES_HEX = {
            'red': '#ef4444', 'blue': '#3b82f6', 'green': '#10b981', 'purple': '#8b5cf6',
            'orange': '#f97316', 'darkred': '#991b1b', 'cadetblue': '#06b6d4',
            'darkgreen': '#166534', 'darkblue': '#1e3a8a', 'pink': '#ec4899'
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
                        f'<div style="background: linear-gradient(180deg,#111c33,#0f172a); padding: 9px 12px; border-radius: 10px; border: 1px solid #1e293b; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; box-shadow: 0 4px 12px -8px rgba(0,0,0,0.6);">'
                        f'<span style="height: 12px; width: 12px; background-color: {hex_cor}; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px {hex_cor};"></span>'
                        f'<b style="color: #f1f5f9; font-size: 13px;">{seg}</b>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        if 'latitude' in df_mapa_filtrado.columns and 'longitude' in df_mapa_filtrado.columns and len(df_mapa_filtrado) > 0:
            lat_centro = df_mapa_filtrado['latitude'].mean()
            lon_centro = df_mapa_filtrado['longitude'].mean()

            m = folium.Map(location=[lat_centro, lon_centro], zoom_start=13, tiles="OpenStreetMap")

            bounds = []
            for _, row in df_mapa_filtrado.iterrows():
                cor_pin = mapa_cores_seg.get(row['categoria'], 'red') if cat_sel_mapa == "Todos os Nichos" else 'red'
                
                info_card_html = f"""
                <div style="font-family: Arial, sans-serif; font-size: 12px; min-width: 240px; padding: 6px; line-height: 1.5;">
                    <b style="color: #2563eb; font-size: 14px;">{row['nome']}</b><br/>
                    <span style="color: #475569; font-size: 11px;">📍 {row['endereco']}</span><br/>
                    <hr style="margin: 6px 0; border: 0.5px solid #cbd5e1;"/>
                    🚨 <b>Score Oportunidade:</b> <span style="color: #dc2626; font-weight: bold;">{row['score_oportunidade']}/100</span><br/>
                    ⭐ <b>Nota no Google:</b> {row['nota']} ({row['total_avaliacoes']} avaliações)<br/>
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

            st_folium(m, width="100%", height=500)
            
            st.divider()
            
            # ITINERÁRIO SEQUENCIAL (OS MAIORES SCORES DE OPORTUNIDADE PRIMEIRO)
            st.markdown("### 🚗 Itinerário Sequencial de Visitas Presenciais (Prioridade Comercial)")
            st.markdown("Lista ordenada do maior score de oportunidade (mais carente de serviços) para o menor:")

            df_mapa_sorted = df_mapa_filtrado.sort_values(by='score_oportunidade', ascending=False)
            
            for idx, (_, r_visita) in enumerate(df_mapa_sorted.iterrows(), start=1):
                url_rota_passo_a_passo = f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(r_visita['endereco'])}"
                
                with st.container():
                    col_num, col_info, col_acao = st.columns([0.8, 4.2, 2])
                    with col_num:
                        st.markdown(f"<div style='background: linear-gradient(180deg,#1e3a5f,#0f172a); color: #38bdf8; font-size: 20px; font-weight: 800; text-align: center; padding: 12px; border-radius: 12px; border: 1px solid #1e40af; box-shadow: 0 6px 16px -8px rgba(56,189,248,0.4);'>#{idx}</div>", unsafe_allow_html=True)
                    with col_info:
                        st.markdown(f"**{r_visita['nome']}** ({r_visita['categoria']})")
                        st.markdown(f"📍 {r_visita['endereco']}")
                        st.markdown(f"⭐ Nota: {r_visita['nota']} | 🚨 Score Oportunidade: **{r_visita['score_oportunidade']}/100**")
                    with col_acao:
                        st.markdown(f"<div style='height: 4px;'></div>", unsafe_allow_html=True)
                        st.markdown(f'<a href="{url_rota_passo_a_passo}" target="_blank"><button style="width:100%; background: linear-gradient(135deg,#2563eb,#0ea5e9); color:white; border:none; padding:8px; border-radius:10px; font-weight:700; cursor:pointer; margin-bottom:6px; box-shadow:0 4px 12px -4px rgba(37,99,235,0.6);">🧭 Iniciar Navegação (GPS)</button></a>', unsafe_allow_html=True)
                        if r_visita['whatsapp']:
                            link_wa_rota = f"https://wa.me/55{r_visita['whatsapp']}?text={urllib.parse.quote(f'Olá! Estou passando aqui na região e gostaria de agendar uma rápida apresentação presencial do Tour 360° para a {r_visita["nome"]}.')}"
                            st.markdown(f'<a href="{link_wa_rota}" target="_blank"><button style="width:100%; background: linear-gradient(135deg,#25D366,#128C7E); color:white; border:none; padding:8px; border-radius:10px; font-weight:700; cursor:pointer; box-shadow:0 4px 12px -4px rgba(37,211,102,0.6);">💬 Avisar via WhatsApp</button></a>', unsafe_allow_html=True)
                    st.divider()
        else:
            st.warning("Nenhum registro encontrado para os filtros selecionados.")

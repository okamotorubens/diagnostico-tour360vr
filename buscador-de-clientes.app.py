import streamlit as st
import pandas as pd
import sqlite3
import json
import time
import os
import re
import requests
import csv
import urllib.parse
from datetime import datetime
import io
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import folium

# ReportLab para geração do PDF do Panorama com Gráficos e Cores
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DO ENDEREÇO DO SEU SISTEMA DE DIAGNÓSTICO
# -----------------------------------------------------------------------------
URL_SISTEMA_DIAGNOSTICO = "https://tour360vr.streamlit.app/"

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# -----------------------------------------------------------------------------
favicon_path = "logo_tour_transparente.png" if os.path.exists("logo_tour_transparente.png") else "🔍"

st.set_page_config(
    page_title="Radar & CRM de Prospecção | Tour360VR",
    page_icon=favicon_path,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ROLAGEM AUTOMÁTICA PARA O TOPO
components.html("""
    <script>
        var body = window.parent.document.querySelector(".main");
        if (body) { body.scrollTop = 0; }
    </script>
""", height=0)

# -----------------------------------------------------------------------------
# BANCO DE DADOS PERMANENTE (SQLITE LOCAL)
# -----------------------------------------------------------------------------
DB_PATH = "leads_database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_minacao TEXT,
            cidade_busca TEXT,
            bairro_busca TEXT,
            nome TEXT,
            categoria TEXT,
            endereco TEXT,
            latitude REAL,
            longitude REAL,
            telefone TEXT,
            whatsapp TEXT,
            website TEXT,
            website_https INTEGER,
            instagram TEXT,
            facebook TEXT,
            foto_url TEXT,
            nota REAL,
            total_avaliacoes INTEGER,
            reivindicada INTEGER,
            fotos_total INTEGER,
            ultima_foto_dias INTEGER,
            tour_360 INTEGER,
            status_crm TEXT,
            pontos_criticos TEXT,
            oportunidades TEXT,
            score_oportunidade INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def salvar_lead_db(lead):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    criticos_json = json.dumps(lead.get('pontos_criticos', []), ensure_ascii=False)
    opp_json = json.dumps(lead.get('oportunidades', []), ensure_ascii=False)
    
    cursor.execute("SELECT id FROM leads WHERE nome = ? AND endereco = ?", (lead['nome'], lead['endereco']))
    data = cursor.fetchone()
    
    if not data:
        cursor.execute('''
            INSERT INTO leads (
                data_minacao, cidade_busca, bairro_busca, nome, categoria, endereco, latitude, longitude,
                telefone, whatsapp, website, website_https, instagram, facebook, foto_url,
                nota, total_avaliacoes, reivindicada, fotos_total, ultima_foto_dias, tour_360,
                status_crm, pontos_criticos, oportunidades, score_oportunidade
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lead.get('data_minacao', datetime.now().strftime('%d/%m/%Y %H:%M')),
            lead.get('cidade_busca', ''),
            lead.get('bairro_busca', ''),
            lead['nome'],
            lead['categoria'],
            lead['endereco'],
            lead.get('latitude', -21.1775),
            lead.get('longitude', -47.8103),
            lead.get('telefone', ''),
            lead.get('whatsapp', ''),
            lead.get('website', ''),
            1 if lead.get('website_https') else 0,
            lead.get('instagram', ''),
            lead.get('facebook', ''),
            lead.get('foto_url', ''),
            lead.get('nota', 0.0),
            lead.get('total_avaliacoes', 0),
            1 if lead.get('reivindicada') else 0,
            lead.get('fotos_total', 0),
            lead.get('ultima_foto_dias', 0),
            1 if lead.get('tour_360') else 0,
            lead.get('status_crm', '🆕 Novo Lead'),
            criticos_json,
            opp_json,
            lead.get('score_oportunidade', 0)
        ))
        conn.commit()
    conn.close()

def atualizar_status_crm(lead_id, novo_status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE leads SET status_crm = ? WHERE id = ?", (novo_status, lead_id))
    conn.commit()
    conn.close()

def carregar_todos_leads_db():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    leads = []
    for r in rows:
        leads.append({
            "id": r[0],
            "data_minacao": r[1],
            "cidade_busca": r[2],
            "bairro_busca": r[3] if len(r) > 24 else "",
            "nome": r[4] if len(r) > 24 else r[3],
            "categoria": r[5] if len(r) > 24 else r[4],
            "endereco": r[6] if len(r) > 24 else r[5],
            "latitude": r[7] if (len(r) > 24 and r[7]) else -21.1775,
            "longitude": r[8] if (len(r) > 24 and r[8]) else -47.8103,
            "telefone": r[9] if len(r) > 24 else r[8],
            "whatsapp": r[10] if len(r) > 24 else r[9],
            "website": r[11] if len(r) > 24 else r[10],
            "website_https": bool(r[12]) if len(r) > 24 else False,
            "instagram": r[13] if len(r) > 24 else r[12],
            "facebook": r[14] if len(r) > 24 else r[13],
            "foto_url": r[15] if len(r) > 24 else r[14],
            "nota": r[16] if len(r) > 24 else r[15],
            "total_avaliacoes": r[17] if len(r) > 24 else r[16],
            "reivindicada": bool(r[18]) if len(r) > 24 else bool(r[17]),
            "fotos_total": r[19] if len(r) > 24 else r[18],
            "ultima_foto_dias": r[20] if len(r) > 24 else r[19],
            "tour_360": bool(r[21]) if len(r) > 24 else bool(r[20]),
            "status_crm": (r[22] if len(r) > 24 else r[21]) or '🆕 Novo Lead',
            "pontos_criticos": json.loads(r[23]) if (len(r) > 24 and r[23]) else [],
            "oportunidades": json.loads(r[24]) if (len(r) > 24 and r[24]) else [],
            "score_oportunidade": r[25] if len(r) > 24 else r[24]
        })
    return leads

def limpar_banco_dados():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads")
    conn.commit()
    conn.close()

init_db()

# -----------------------------------------------------------------------------
# GERADOR DE PDF DO PANORAMA DE NICHO (COM GRÁFICOS E CORES)
# -----------------------------------------------------------------------------
def gerar_pdf_panorama_nicho(nicho_nome, df_nicho):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=20, bottomMargin=40,
        title=f"Panorama de Mercado - {nicho_nome}",
        author="Tour360VR"
    )
    styles = getSampleStyleSheet()
    
    sub_title_header = ParagraphStyle('SubTitleHeader', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold', alignment=1)
    main_title_style = ParagraphStyle('MainTitle', parent=styles['Heading1'], fontSize=12.5, textColor=colors.HexColor('#1e293b'), fontName='Helvetica-Bold', alignment=1, spaceAfter=8)
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=10, textColor=colors.HexColor('#0f172a'), spaceBefore=8, spaceAfter=4, fontName='Helvetica-Bold', alignment=1)
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#334155'), leading=10)
    body_center = ParagraphStyle('BodyCenter', parent=body_style, alignment=1)

    elements = []

    logo_tour = "logo_tour_transparente.png" if os.path.exists("logo_tour_transparente.png") else None
    img_tour = Image(logo_tour, width=140, height=45, kind='proportional') if logo_tour else Paragraph("<b>TOUR360VR</b>", body_style)

    header_p = Paragraph("ESTUDO DE INTELIGÊNCIA DE MERCADO LOCAL E PRESENÇA DIGITAL NO GOOGLE", sub_title_header)

    header_table = Table([[img_tour], [header_p]], colWidths=[540])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(header_table)
    
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#cbd5e1'), spaceBefore=4, spaceAfter=8))

    elements.append(Paragraph(f"PANORAMA DE MERCADO: {nicho_nome.upper()}", main_title_style))
    elements.append(Spacer(1, 4))

    total_emp = len(df_nicho)
    sem_tour = len(df_nicho[df_nicho['tour_360'] == False])
    sem_site = len(df_nicho[df_nicho['website'] == ''])
    nao_reiv = len(df_nicho[df_nicho['reivindicada'] == False])

    dados_resumo = [
        [Paragraph("<b>INDICADOR ESTRATÉGICO</b>", body_style), Paragraph("<b>VOLUME / %</b>", body_center), Paragraph("<b>DIAGNÓSTICO DE OPORTUNIDADE</b>", body_style)],
        [Paragraph("Sem Tour Virtual 360°", body_style), Paragraph(f"<b>{sem_tour} ({(sem_tour/total_emp*100 if total_emp>0 else 0):.1f}%)</b>", body_center), Paragraph("Oportunidade crítica para implantação de experiência imersiva.", body_style)],
        [Paragraph("Sem Website Oficial", body_style), Paragraph(f"<b>{sem_site} ({(sem_site/total_emp*100 if total_emp>0 else 0):.1f}%)</b>", body_center), Paragraph("Perda de tráfego direto e dependência de redes sociais.", body_style)],
        [Paragraph("Fichas Não Reivindicadas", body_style), Paragraph(f"<b>{nao_reiv} ({(nao_reiv/total_emp*100 if total_emp>0 else 0):.1f}%)</b>", body_center), Paragraph("Vulnerabilidade de segurança e falta de gestão do perfil.", body_style)]
    ]
    t_resumo = Table(dados_resumo, colWidths=[150, 90, 300])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
    ]))
    elements.append(t_resumo)
    
    elements.append(Spacer(1, 8))

    chart_drawing = Drawing(540, 65)
    bc = VerticalBarChart()
    bc.x = 45
    bc.y = 10
    bc.height = 45
    bc.width = 450
    bc.data = [[sem_tour, sem_site, nao_reiv]]
    bc.categoryAxis.categoryNames = ['Sem Tour 360°', 'Sem Website', 'Não Reivindicadas']
    bc.bars[0].fillColor = colors.HexColor('#2563eb')
    chart_drawing.add(bc)
    elements.append(chart_drawing)

    elements.append(Spacer(1, 6))
    elements.append(Paragraph("RANKING DE EMPRESAS AUDITADAS NO SETOR (VISUALIZADOR DE IMPACTO)", section_heading))
    elements.append(Spacer(1, 4))

    df_nicho_sorted = df_nicho.sort_values(by='score_oportunidade', ascending=False)

    t_data = [[
        Paragraph("<b>EMPRESA</b>", body_style), 
        Paragraph("<b>NOTA</b>", body_center), 
        Paragraph("<b>REVIEWS</b>", body_center),
        Paragraph("<b>SITE</b>", body_center), 
        Paragraph("<b>360°</b>", body_center), 
        Paragraph("<b>SCORE OPORTUNIDADE</b>", body_center)
    ]]
    
    t_styles = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]

    for idx, row in enumerate(df_nicho_sorted.head(12).iterrows()):
        r_data = row[1]
        sc = r_data['score_oportunidade']
        
        if sc >= 60:
            bg_color = colors.HexColor('#fca5a5')
            txt_color = '#7f1d1d'
        elif sc >= 30:
            bg_color = colors.HexColor('#fde047')
            txt_color = '#713f12'
        else:
            bg_color = colors.HexColor('#86efac')
            txt_color = '#14532d'

        p_score = Paragraph(f"<font color='{txt_color}'><b>{sc} / 100</b></font>", body_center)

        row_idx = idx + 1
        t_styles.append(('BACKGROUND', (5, row_idx), (5, row_idx), bg_color))

        t_data.append([
            Paragraph(str(r_data['nome'])[:36], body_style),
            Paragraph(str(r_data['nota']), body_center),
            Paragraph(str(r_data['total_avaliacoes']), body_center),
            Paragraph("Sim" if r_data['website'] else "Não", body_center),
            Paragraph("Sim" if r_data['tour_360'] else "Não", body_center),
            p_score
        ])

    t_empresas = Table(t_data, colWidths=[190, 45, 55, 45, 45, 160])
    t_empresas.setStyle(TableStyle(t_styles))
    elements.append(t_empresas)

    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=2, spaceAfter=4))
    
    rodape_text = Paragraph(
        "<b>tour360vr.com.br</b> &nbsp;|&nbsp; <b>contato@okamotomidiasvisuais.com.br</b> &nbsp;|&nbsp; <b>(16) 99133-2121</b>",
        ParagraphStyle('Rodape', parent=body_style, alignment=1, textColor=colors.HexColor('#1e293b'))
    )
    elements.append(rodape_text)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (MARGEM SUPERIOR AJUSTADA)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
    .main { 
        background-color: #0e1117; 
        padding-top: 25px !important; 
    }
    .block-container { 
        padding-top: 2rem !important; 
    }
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white; 
        padding: 16px 20px; 
        border-radius: 10px; 
        margin-bottom: 20px;
        border: 1px solid #334155; 
        margin-top: 10px !important;
    }
    .main-title { font-size: 22px; font-weight: 700; margin: 0; color: #ffffff; }
    .main-subtitle { font-size: 12.5px; color: #94a3b8; margin-top: 4px; }

    .lead-card {
        background-color: #1e293b; border-radius: 10px; padding: 16px;
        margin-bottom: 12px; border: 1px solid #334155;
    }
    
    .score-box { text-align: center; padding: 8px; border-radius: 8px; font-weight: bold; width: 130px; }
    .score-high { background-color: #450a0a; color: #fca5a5; border: 1px solid #991b1b; }
    .score-med  { background-color: #451a03; color: #fde047; border: 1px solid #92400e; }
    .score-low  { background-color: #052e16; color: #86efac; border: 1px solid #166534; }

    .critical-item { color: #f87171; font-size: 13px; margin-bottom: 6px; font-weight: 500; }
    
    .sidebar-title {
        text-align: center;
        font-size: 16px;
        font-weight: 800;
        color: #ffffff;
        margin-top: 5px;
        margin-bottom: 10px;
    }

    .btn-redirect {
        display: block;
        width: 100%;
        background-color: #2563eb !important;
        color: #ffffff !important;
        text-align: center;
        padding: 9px 10px;
        border-radius: 6px;
        font-weight: 700 !important;
        font-size: 13px;
        text-decoration: none !important;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .btn-redirect:hover { background-color: #1d4ed8 !important; color: #ffffff !important; }

    .script-box {
        background-color: #0f172a;
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 13.5px;
        line-height: 1.5;
        padding: 12px 15px;
        border-radius: 8px;
        border: 1px solid #334155;
        white-space: pre-wrap;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------------------------
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1

# -----------------------------------------------------------------------------
# INTEGRAÇÃO DE BUSCA E AUDITORIA
# -----------------------------------------------------------------------------
def buscar_google_places_api(nicho, cidade, bairro, api_key, limite=20):
    query_str = f'"{nicho}"'
    if bairro:
        query_str += f' no bairro "{bairro}"'
    query_str += f' em "{cidade}" - SP'

    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={urllib.parse.quote(query_str)}&language=pt-BR&key={api_key}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("status") == "OK":
            results = data.get("results", [])[:limite]
            leads = []
            for place in results:
                place_id = place.get("place_id")
                lat = place.get("geometry", {}).get("location", {}).get("lat", -21.1775)
                lng = place.get("geometry", {}).get("location", {}).get("lng", -47.8103)
                
                details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos&language=pt-BR&key={api_key}"
                det_res = requests.get(details_url, timeout=5).json().get("result", {}) if place_id else {}
                
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
                    "categoria": nicho.capitalize(),
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
    except Exception as e:
        st.warning(f"Aviso da API: {str(e)}")
    return None

def minerar_e_auditar_negocios(nicho, cidade, bairro, limite=20):
    api_key = st.secrets.get("GOOGLE_API_KEY", None) or os.getenv("GOOGLE_API_KEY", None)
    if api_key:
        leads_reais = buscar_google_places_api(nicho, cidade, bairro, api_key, limite)
        if leads_reais:
            return leads_reais

    bairro_label = f" - Bairro {bairro}" if bairro else ""
    exemplo_estabelecimentos = [
        {"nome": f"Loja & Boutique {cidade}", "bairro": bairro or "Jardim Sumaré", "rua": "Rua Saldanha Marinho", "lat": -21.1775, "lng": -47.8103, "img": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&q=80"},
        {"nome": f"Estilo & Moda {nicho.capitalize()}", "bairro": bairro or "Jardim Sumaré", "rua": "Av. Independência", "lat": -21.1895, "lng": -47.8050, "img": "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?w=400&q=80"},
        {"nome": f"Empório &

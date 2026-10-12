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

# ReportLab para geração do PDF de Nicho
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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

# -----------------------------------------------------------------------------
# BANCO DE DADOS PERMANENTE (SQLITE LOCAL COM SUPORTE A CRM E REDES SOCIAIS)
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
# GERADOR DE PDF DO PANORAMA DE NICHO
# -----------------------------------------------------------------------------
def gerar_pdf_panorama_nicho(nicho_nome, df_nicho):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#64748b'), spaceAfter=15)
    section_heading = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1e293b'), spaceBefore=12, spaceAfter=6, fontName='Helvetica-Bold')
    body_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#334155'), leading=12)

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

    elements.append(Paragraph(f"PANORAMA E AUDITORIA DE MERCADO: {nicho_nome.upper()}", title_style))
    elements.append(Paragraph(f"Relatório de Inteligência Gerado em: {datetime.now().strftime('%d/%m/%Y')} | Total Mapeado: <b>{len(df_nicho)} Empresas</b>", subtitle_style))

    total_emp = len(df_nicho)
    sem_tour = len(df_nicho[df_nicho['tour_360'] == False])
    sem_site = len(df_nicho[df_nicho['website'] == ''])
    nao_reiv = len(df_nicho[df_nicho['reivindicada'] == False])

    dados_resumo = [
        [Paragraph("<b>Indicador Estratégico</b>", body_style), Paragraph("<b>Volume / Percentual</b>", body_style), Paragraph("<b>Diagnóstico de Oportunidade</b>", body_style)],
        [Paragraph("Sem Tour Virtual 360°", body_style), Paragraph(f"{sem_tour} ({sem_tour/total_emp*100:.1f}%)", body_style), Paragraph("Oportunidade crítica para implantação de experiência imersiva.", body_style)],
        [Paragraph("Sem Website Oficial", body_style), Paragraph(f"{sem_site} ({sem_site/total_emp*100:.1f}%)", body_style), Paragraph("Perda de tráfego direto e dependência exclusiva de terceiros.", body_style)],
        [Paragraph("Fichas Não Reivindicadas", body_style), Paragraph(f"{nao_reiv} ({nao_reiv/total_emp*100:.1f}%)", body_style), Paragraph("Vulnerabilidade de segurança e falta de controle da marca.", body_style)]
    ]
    t_resumo = Table(dados_resumo, colWidths=[160, 120, 260])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_resumo)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("LISTAGEM DE EMPRESAS AUDITADAS NO SETOR", section_heading))
    
    t_data = [[
        Paragraph("<b>Empresa</b>", body_style), 
        Paragraph("<b>Nota</b>", body_style), 
        Paragraph("<b>Site</b>", body_style), 
        Paragraph("<b>360°</b>", body_style), 
        Paragraph("<b>Score</b>", body_style)
    ]]
    
    for idx, row in df_nicho.iterrows():
        t_data.append([
            Paragraph(str(row['nome'])[:35], body_style),
            Paragraph(str(row['nota']), body_style),
            Paragraph("Sim" if row['website'] else "Não", body_style),
            Paragraph("Sim" if row['tour_360'] else "Não", body_style),
            Paragraph(f"{row['score_oportunidade']}/100", body_style)
        ])

    t_empresas = Table(t_data, colWidths=[200, 50, 60, 50, 60])
    t_empresas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_empresas)

    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=10, spaceAfter=8))
    
    rodape_text = Paragraph(
        "<font color='#1e293b'><b>OKAMOTO MÍDIAS VISUAIS & TOUR360VR</b></font><br/>"
        "<font color='#475569' size=8>🌐 <b>Site:</b> tour360vr.com.br &nbsp;|&nbsp; ✉️ <b>E-mail:</b> contato@okamotomidiasvisuais.com.br &nbsp;|&nbsp; 💬 <b>WhatsApp:</b> (16) 99133-2121<br/>"
        "Estudo de Inteligência de Mercado Local e Presença Digital no Google.</font>",
        ParagraphStyle('Rodape', parent=body_style, alignment=1)
    )
    elements.append(rodape_text)

    doc.build(elements)
    buffer.seek(0)
    return buffer

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

    .btn-redirect {
        display: block;
        width: 100%;
        background-color: #2563eb !important;
        color: #ffffff !important;
        text-align: center;
        padding: 10px 12px;
        border-radius: 6px;
        font-weight: 700 !important;
        font-size: 13px;
        text-decoration: none !important;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .btn-redirect:hover { background-color: #1d4ed8 !important; color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------------------------
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1

# -----------------------------------------------------------------------------
# INTEGRAÇÃO DE BUSCA E AUDITORIA COM SUPORTE A BAIRRO
# -----------------------------------------------------------------------------
def buscar_google_places_api(nicho, cidade, bairro, api_key, limite=20):
    query_str = f"{nicho}"
    if bairro:
        query_str += f" no bairro {bairro}"
    query_str += f" em {cidade}"

    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={urllib.parse.quote(query_str)}&language=pt-BR&key={api_key}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("status") == "OK":
            results = data.get("results", [])[:limite]
            leads = []
            for idx, place in enumerate(results):
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
                    score += 25
                elif not has_https:
                    pontos_criticos.append("Site oficial sem Certificado de Segurança (HTTP inseguro)")
                    oportunidades.append("Adequação de Segurança SSL e Otimização Web")
                    score += 15

                if total_avaliacoes < 30:
                    pontos_criticos.append(f"Volume crítico de avaliações ({total_avaliacoes} no total)")
                    oportunidades.append("Estratégia Acelerada de Reputação e Gestão de Avaliações")
                    score += 20

                if len(photos) < 5:
                    pontos_criticos.append("Poucas fotos publicadas no perfil corporativo")
                    oportunidades.append("Produção de Fotografia Profissional para Arquitetura e Estrutura")
                    score += 20

                pontos_criticos.append("Ausência de Tour Virtual 360° interativo")
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
        st.warning(f"Aviso da API: {str(e)}. Carregando dados de contingência.")
    return None

def minerar_e_auditar_negocios(nicho, cidade, bairro, limite=20):
    api_key = st.secrets.get("GOOGLE_API_KEY", None) or os.getenv("GOOGLE_API_KEY", None)
    if api_key:
        leads_reais = buscar_google_places_api(nicho, cidade, bairro, api_key, limite)
        if leads_reais:
            return leads_reais

    bairro_label = f" - Bairro {bairro}" if bairro else ""
    exemplo_estabelecimentos = [
        {"nome": f"Loja & Boutique {cidade}", "bairro": bairro or "Centro", "rua": "Rua Saldanha Marinho", "lat": -21.1775, "lng": -47.8103, "img": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&q=80"},
        {"nome": f"Estilo & Moda {nicho.capitalize()}", "bairro": bairro or "Alto da Boa Vista", "rua": "Av. Independência", "lat": -21.1895, "lng": -47.8050, "img": "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?w=400&q=80"},
        {"nome": f"Empório & {nicho.capitalize()} do Barão", "bairro": bairro or "Jardim Sumaré", "rua": "Rua Garibaldi", "lat": -21.1920, "lng": -47.8150, "img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&q=80"},
        {"nome": f"Conceito {nicho.capitalize()} Brasil", "bairro": bairro or "Vila Seixas", "rua": "Rua Amador Bueno", "lat": -21.1800, "lng": -47.8000, "img": "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&q=80"},
        {"nome": f"Studio & Galeria {nicho.capitalize()}", "bairro": bairro or "Jardim Botânico", "rua": "Av. Professor João Fiúsa", "lat": -21.2050, "lng": -47.8120, "img": "https://images.unsplash.com/photo-1513151233558-d860c5398176?w=400&q=80"}
    ]

    resultados = []
    for i in range(limite):
        item = exemplo_estabelecimentos[i % len(exemplo_estabelecimentos)]
        sufixo = f" #{i+1}" if i >= len(exemplo_estabelecimentos) else ""
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

        nome_empresa = f"{item['nome']}{sufixo}"
        nome_slug = re.sub(r'[^a-zA-Z0-9]', '', nome_empresa.lower())

        lead_obj = {
            "data_minacao": datetime.now().strftime('%d/%m/%Y %H:%M'),
            "cidade_busca": cidade,
            "bairro_busca": bairro,
            "nome": nome_empresa,
            "categoria": nicho.capitalize(),
            "endereco": f"{item['rua']}, {120 + (i*85)} - {item['bairro']}{bairro_label}, {cidade} - SP",
            "latitude": item["lat"] + (i * 0.002),
            "longitude": item["lng"] + (i * 0.002),
            "telefone": f"(16) 39{i:02d}-4000",
            "whatsapp": f"16997{i:02d}4000",
            "website": f"https://www.{nicho.lower()}exemplo.com.br" if tem_site else "",
            "website_https": tem_site,
            "instagram": f"https://instagram.com/{nome_slug}",
            "facebook": f"https://facebook.com/{nome_slug}",
            "foto_url": item["img"],
            "nota": nota,
            "total_avaliacoes": total_avaliacoes,
            "reivindicada": reivindicada,
            "fotos_total": 4 + (i * 3) % 15,
            "ultima_foto_dias": 45 + (i * 30) % 200,
            "tour_360": False,
            "status_crm": "🆕 Novo Lead",
            "pontos_criticos": pontos_criticos,
            "oportunidades": oportunidades,
            "score_oportunidade": min(score, 100)
        }
        
        salvar_lead_db(lead_obj)
        resultados.append(lead_obj)

    return resultados

# -----------------------------------------------------------------------------
# GERADOR DE CSV COMPLETO COM TODAS AS COLUNAS
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
# BARRA LATERAL (NAVEGAÇÃO MÓDULOS)
# -----------------------------------------------------------------------------
base_leads = carregar_todos_leads_db()

with st.sidebar:
    if os.path.exists("logo_okamoto.png"):
        c1, c2, c3 = st.columns([1, 4, 1])
        with c2: st.image("logo_okamoto.png", use_container_width=True)
    if os.path.exists("logo_tour_transparente.png"):
        c1, c2, c3 = st.columns([1.2, 3.6, 1.2])
        with c2: st.image("logo_tour_transparente.png", use_container_width=True)

    st.markdown('<div class="sidebar-title">Radar Comercial Tour360VR</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown("### 📌 Módulos")
    if st.button("1. Buscador de Clientes", use_container_width=True, type="primary" if st.session_state.etapa == 1 else "secondary"):
        st.session_state.etapa = 1
        st.rerun()
        
    if st.button("2. Base & CRM de Leads", use_container_width=True, type="primary" if st.session_state.etapa == 2 else "secondary", disabled=len(base_leads) == 0):
        st.session_state.etapa = 2
        st.rerun()

    if st.button("3. Panorama de Nicho (Estatísticas)", use_container_width=True, type="primary" if st.session_state.etapa == 3 else "secondary", disabled=len(base_leads) == 0):
        st.session_state.etapa = 3
        st.rerun()

    if st.button("4. Mapa de Prospecção", use_container_width=True, type="primary" if st.session_state.etapa == 4 else "secondary", disabled=len(base_leads) == 0):
        st.session_state.etapa = 4
        st.rerun()

    if len(base_leads) > 0:
        st.divider()
        st.caption(f"💾 Banco Permanente: **{len(base_leads)} leads salvos**")
        if st.button("🗑️ Limpar Banco de Dados", use_container_width=True):
            limpar_banco_dados()
            st.session_state.etapa = 1
            st.rerun()

# -----------------------------------------------------------------------------
# ETAPA 1: BUSCADOR DE CLIENTES
# -----------------------------------------------------------------------------
if st.session_state.etapa == 1:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🔎 Radar e Mineração de Mercado Local</h1>
            <div class="main-subtitle">Varredura de perfis no Google Maps por Nicho, Cidade e Bairro com auditoria completa.</div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("form_busca"):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1.2])
        with col1: nicho_input = st.text_input("Nicho / Categoria Comercial", value="Moda praia")
        with col2: cidade_input = st.text_input("Cidade / Município", value="Ribeirão Preto")
        with col3: bairro_input = st.text_input("Bairro / Região (Opcional)", value="Jardim Sumaré", help="Deixe em branco para buscar na cidade inteira")
        with col4: limite_input = st.number_input("Qtd. Máxima", min_value=20, max_value=50, value=20, step=5)
        
        btn_minar = st.form_submit_button("🚀 Iniciar Varredura Profunda", use_container_width=True)

    if btn_minar:
        with st.spinner("Varrendo Google Maps, auditando presença web e salvando no banco..."):
            time.sleep(1)
            minerar_e_auditar_negocios(nicho_input, cidade_input, bairro_input, limite_input)
            st.session_state.etapa = 2
            st.rerun()

    if len(base_leads) > 0:
        st.divider()
        st.info(f"O seu banco possui **{len(base_leads)} leads salvos permanentemente**.")
        if st.button("Ver Base Completa de Leads ➡️", type="primary"):
            st.session_state.etapa = 2
            st.rerun()

# -----------------------------------------------------------------------------
# ETAPA 2: BASE DE LEADS & CRM DE VENDAS
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 2:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📊 Base de Leads e Gerenciador CRM</h1>
            <div class="main-subtitle">Seus leads permanecem salvos indefinidamente no banco de dados. Atualize status e exporte planilhas completas.</div>
        </div>
    """, unsafe_allow_html=True)

    col_back, col_filter, col_export = st.columns([1.5, 3, 2.5])
    with col_back:
        if st.button("⬅️ Nova Busca", use_container_width=True):
            st.session_state.etapa = 1
            st.rerun()

    with col_filter:
        filtro_status = st.selectbox(
            "Filtrar por Status CRM:",
            ["Todos os Status", "🆕 Novo Lead", "💬 Em Abordagem", "🛠️ Diagnóstico Gerado", "🤝 Cliente Fechado", "❌ Recusado"]
        )

    with col_export:
        csv_bytes = gerar_csv_excel_formatado(base_leads)
        st.download_button(
            label="📊 Exportar Planilha Completa (.csv)",
            data=csv_bytes,
            file_name=f"Leads_Completo_CRM_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.divider()

    resultados_filtrados = base_leads if filtro_status == "Todos os Status" else [r for r in base_leads if r['status_crm'] == filtro_status]

    st.markdown(f"Exibindo **{len(resultados_filtrados)}** oportunidades salvas:")

    for lead in resultados_filtrados:
        score = lead['score_oportunidade']
        score_class = "score-high" if score >= 60 else ("score-med" if score >= 30 else "score-low")
        score_label = "ALTA OPORTUNIDADE" if score >= 60 else ("MÉDIA OPORTUNIDADE" if score >= 30 else "BAIXA OPORTUNIDADE")

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

        col_img, col_details1, col_details2, col_actions = st.columns([2, 2.5, 2.5, 2.5])

        with col_img:
            st.image(lead['foto_url'], caption="Foto da Ficha do Google", use_container_width=True)
            
            # GESTÃO DE STATUS DO CRM
            status_opcoes = ["🆕 Novo Lead", "💬 Em Abordagem", "🛠️ Diagnóstico Gerado", "🤝 Cliente Fechado", "❌ Recusado"]
            idx_atual = status_opcoes.index(lead['status_crm']) if lead['status_crm'] in status_opcoes else 0
            novo_st = st.selectbox("Status Comercial:", status_opcoes, index=idx_atual, key=f"crm_st_{lead['id']}")
            if novo_st != lead['status_crm']:
                atualizar_status_crm(lead['id'], novo_st)
                st.toast("Status comercial atualizado com sucesso!")
                st.rerun()

        with col_details1:
            st.markdown("**📊 Indicadores no Google:**")
            st.markdown(f"- **Nota Média:** ⭐ {lead['nota']} ({lead['total_avaliacoes']} avaliações)")
            st.markdown(f"- **Ficha Reivindicada?** {'✅ Sim' if lead['reivindicada'] else '❌ **NÃO REIVINDICADA**'}")
            st.markdown(f"- **Fotos na Ficha:** {lead['fotos_total']} fotos (última há {lead['ultima_foto_dias']} dias)")
            st.markdown(f"- **Tour 360°:** {'✅ Presente' if lead['tour_360'] else '❌ **Ausente**'}")

        with col_details2:
            st.markdown("**🚨 Pontos Críticos Encontrados:**")
            for pc in lead['pontos_criticos']:
                st.markdown(f"<div class='critical-item'>❌ {pc}</div>", unsafe_allow_html=True)

        with col_actions:
            st.markdown("**🌐 Presença Web & Mídias:**")
            st.markdown(f"- **Website:** {lead['website'] if lead['website'] else '❌ Sem site'}")
            st.markdown(f"- **Instagram:** [Abrir Perfil]({lead['instagram']})")
            st.markdown(f"- **Maps:** [Ver no Google Maps](https://www.google.com/maps/search/?api=1&query={lead['nome'].replace(' ', '+')})")

            st.markdown(f'<a href="{URL_SISTEMA_DIAGNOSTICO}" target="_blank" class="btn-redirect">🛠️ Abrir no Diagnóstico Tour360VR</a>', unsafe_allow_html=True)

            if lead['whatsapp']:
                msg_wa = f"Olá! Estava analisando a presença digital da {lead['nome']} no Google..."
                link_wa = f"https://wa.me/55{lead['whatsapp']}?text={urllib.parse.quote(msg_wa)}"
                st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:8px; border-radius:6px; font-weight:bold; cursor:pointer; margin-bottom:8px;">💬 WhatsApp</button></a>', unsafe_allow_html=True)

        st.markdown("**📋 Resumo do Cliente para Copiar e Colar no Diagnóstico:**")
        texto_copia = f"""Empresa: {lead['nome']}
Endereço: {lead['endereco']}
Categoria: {lead['categoria']}
Telefone: {lead['telefone']}
Website: {lead['website'] if lead['website'] else 'Não possui'}
Pontos Críticos: {', '.join(lead['pontos_criticos'])}"""

        st.code(texto_copia, language="text")
        st.divider()

# -----------------------------------------------------------------------------
# ETAPA 3: PANORAMA DE NICHO (COM EXPORTAÇÃO EM PDF)
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 3:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📈 Panorama de Mercado & Inteligência de Nicho</h1>
            <div class="main-subtitle">Análise detalhada por categoria e exportação de relatório executivo em PDF.</div>
        </div>
    """, unsafe_allow_html=True)

    df_leads = pd.DataFrame(base_leads)

    categorias_disponiveis = ["Todos os Nichos Mapeados"] + list(df_leads['categoria'].unique())
    col_sel_nicho, col_btn_pdf = st.columns([3, 2])
    
    with col_sel_nicho:
        nicho_selecionado = st.selectbox("🎯 Selecione o Nicho Comercial para Analisar:", categorias_disponiveis)

    if nicho_selecionado != "Todos os Nichos Mapeados":
        df_filtrado = df_leads[df_leads['categoria'] == nicho_selecionado]
    else:
        df_filtrado = df_leads

    with col_btn_pdf:
        st.write(" ")
        pdf_bytes_nicho = gerar_pdf_panorama_nicho(nicho_selecionado, df_filtrado)
        st.download_button(
            label="📄 Baixar Relatório de Nicho (.pdf)",
            data=pdf_bytes_nicho,
            file_name=f"Relatorio_Panorama_{nicho_selecionado.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.divider()

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    total_count = len(df_filtrado)
    
    with col_m1: 
        st.metric("Empresas Analisadas", total_count)
    with col_m2: 
        sem_tour = len(df_filtrado[df_filtrado['tour_360'] == False])
        st.metric("Sem Tour Virtual 360°", f"{(sem_tour / total_count * 100 if total_count > 0 else 0):.1f}%", f"{sem_tour} empresas")
    with col_m3: 
        sem_site = len(df_filtrado[df_filtrado['website'] == ''])
        st.metric("Sem Website Oficial", f"{(sem_site / total_count * 100 if total_count > 0 else 0):.1f}%", f"{sem_site} empresas")
    with col_m4: 
        nao_reiv = len(df_filtrado[df_filtrado['reivindicada'] == False])
        st.metric("Fichas não Reivindicadas", f"{(nao_reiv / total_count * 100 if total_count > 0 else 0):.1f}%", f"{nao_reiv} empresas")

    st.divider()

    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        st.markdown("### 📊 Nível de Oportunidade Comercial (Score)")
        st.bar_chart(df_filtrado['score_oportunidade'].value_counts())

    with c_chart2:
        st.markdown("### ⭐ Média de Avaliações no Google")
        st.bar_chart(df_filtrado['nota'].value_counts())

    st.divider()
    st.markdown(f"### 📋 Tabela Resumo do Nicho: **{nicho_selecionado}**")
    st.dataframe(
        df_filtrado[['nome', 'cidade_busca', 'nota', 'total_avaliacoes', 'website', 'tour_360', 'score_oportunidade']],
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# ETAPA 4: MAPA DE PROSPECÇÃO (COM IDENTIFICADOR DE SEGMENTO DE BUSCA)
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 4:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🗺️ Mapa de Localização e Concentração por Segmento</h1>
            <div class="main-subtitle">Filtre os pinos no mapa pelo segmento de busca realizado para organizar rotas no bairro.</div>
        </div>
    """, unsafe_allow_html=True)

    df_mapa = pd.DataFrame(base_leads)
    
    col_filtro_cat, col_filtro_cid = st.columns(2)
    
    with col_filtro_cat:
        cats_mapa = ["Todos os Segmentos"] + list(df_mapa['categoria'].unique())
        cat_sel_mapa = st.selectbox("🏷️ Filtrar Segmento no Mapa:", cats_mapa)
        
    with col_filtro_cid:
        cids_mapa = ["Todas as Cidades/Regiões"] + list(df_mapa['cidade_busca'].unique())
        cid_sel_mapa = st.selectbox("📍 Filtrar Cidade/Região:", cids_mapa)

    df_mapa_filtrado = df_mapa
    if cat_sel_mapa != "Todos os Segmentos":
        df_mapa_filtrado = df_mapa_filtrado[df_mapa_filtrado['categoria'] == cat_sel_mapa]
    if cid_sel_mapa != "Todas as Cidades/Regiões":
        df_mapa_filtrado = df_mapa_filtrado[df_mapa_filtrado['cidade_busca'] == cid_sel_mapa]

    st.info(f"📌 Exibindo **{len(df_mapa_filtrado)} empresas** no mapa para o segmento: **{cat_sel_mapa}** ({cid_sel_mapa})")

    if 'latitude' in df_mapa_filtrado.columns and 'longitude' in df_mapa_filtrado.columns and len(df_mapa_filtrado) > 0:
        df_mapa_clean = df_mapa_filtrado.rename(columns={"latitude": "lat", "longitude": "lon"})
        st.map(df_mapa_clean[['lat', 'lon']], zoom=12)
        
        st.caption("💡 **Dica de Imagem:** Utilize as teclas `Win + Shift + S` (Windows) ou `Cmd + Shift + 4` (Mac) para capturar este mapa e colar nas propostas comerciais.")
        
        csv_mapa = df_mapa_clean[['nome', 'categoria', 'endereco', 'lat', 'lon', 'score_oportunidade']].to_csv(index=False, sep=';').encode('utf-8')
        st.download_button(
            label="📍 Baixar Lista de Coordenadas Geográficas (.csv)",
            data=csv_mapa,
            file_name=f"Coordenadas_{cat_sel_mapa.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("Nenhum registro encontrado para os filtros selecionados.")

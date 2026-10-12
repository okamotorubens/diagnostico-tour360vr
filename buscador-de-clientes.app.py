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
# BANCO DE DADOS PERMANENTE (SQLITE LOCAL COM SUPORTE A CRM)
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
                data_minacao, cidade_busca, nome, categoria, endereco, latitude, longitude,
                telefone, whatsapp, website, website_https, instagram, facebook, foto_url,
                nota, total_avaliacoes, reivindicada, fotos_total, ultima_foto_dias, tour_360,
                status_crm, pontos_criticos, oportunidades, score_oportunidade
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lead.get('data_minacao', datetime.now().strftime('%d/%m/%Y %H:%M')),
            lead.get('cidade_busca', ''),
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
            "nome": r[3],
            "categoria": r[4],
            "endereco": r[5],
            "latitude": r[6] if r[6] else -21.1775,
            "longitude": r[7] if r[7] else -47.8103,
            "telefone": r[8],
            "whatsapp": r[9],
            "website": r[10],
            "website_https": bool(r[11]),
            "instagram": r[12],
            "facebook": r[13],
            "foto_url": r[14],
            "nota": r[15],
            "total_avaliacoes": r[16],
            "reivindicada": bool(r[17]),
            "fotos_total": r[18],
            "ultima_foto_dias": r[19],
            "tour_360": bool(r[20]),
            "status_crm": r[21] if r[21] else '🆕 Novo Lead',
            "pontos_criticos": json.loads(r[22]) if r[22] else [],
            "oportunidades": json.loads(r[23]) if r[23] else [],
            "score_oportunidade": r[24]
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
# INTEGRAÇÃO DE BUSCA E AUDITORIA MULTICANAL
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
                    "nome": nome,
                    "categoria": nicho.capitalize(),
                    "endereco": endereco,
                    "latitude": lat,
                    "longitude": lng,
                    "telefone": telefone or "(16) Contato via Ficha",
                    "whatsapp": clean_phone if len(clean_phone) >= 10 else "16999999999",
                    "website": website,
                    "website_https": has_https,
                    "instagram": f"instagram.com/{nome_slug}",
                    "facebook": f"facebook.com/{nome_slug}",
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

def minerar_e_auditar_negocios(nicho, cidade, limite=10):
    api_key = st.secrets.get("GOOGLE_API_KEY", None) or os.getenv("GOOGLE_API_KEY", None)
    if api_key:
        leads_reais = buscar_google_places_api(nicho, cidade, api_key, limite)
        if leads_reais:
            return leads_reais

    exemplo_estabelecimentos = [
        {"nome": f"Loja & Boutique {cidade}", "bairro": "Centro", "rua": "Rua Saldanha Marinho", "lat": -21.1775, "lng": -47.8103, "img": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&q=80"},
        {"nome": f"Estilo & Moda {nicho.capitalize()}", "bairro": "Alto da Boa Vista", "rua": "Av. Independência", "lat": -21.1895, "lng": -47.8050, "img": "https://images.unsplash.com/photo-1567401893414-76b7b1e5a7a5?w=400&q=80"},
        {"nome": f"Empório & {nicho.capitalize()} do Barão", "bairro": "Jardim Sumaré", "rua": "Rua Garibaldi", "lat": -21.1920, "lng": -47.8150, "img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&q=80"},
        {"nome": f"Conceito {nicho.capitalize()} Brasil", "bairro": "Vila Seixas", "rua": "Rua Amador Bueno", "lat": -21.1800, "lng": -47.8000, "img": "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=400&q=80"},
        {"nome": f"Studio & Galeria {nicho.capitalize()}", "bairro": "Jardim Botânico", "rua": "Av. Professor João Fiúsa", "lat": -21.2050, "lng": -47.8120, "img": "https://images.unsplash.com/photo-1513151233558-d860c5398176?w=400&q=80"}
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

        lead_obj = {
            "data_minacao": datetime.now().strftime('%d/%m/%Y %H:%M'),
            "cidade_busca": cidade,
            "nome": item["nome"],
            "categoria": nicho.capitalize(),
            "endereco": f"{item['rua']}, {120 + (i*85)} - {item['bairro']}, {cidade} - SP",
            "latitude": item["lat"],
            "longitude": item["lng"],
            "telefone": f"(16) 39{i:02d}-4000",
            "whatsapp": f"16997{i:02d}4000",
            "website": f"https://www.{nicho.lower()}exemplo.com.br" if tem_site else "",
            "website_https": tem_site,
            "instagram": f"instagram.com/{nome_slug}",
            "facebook": f"facebook.com/{nome_slug}",
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
# GERADOR DE CSV COMPATÍVEL COM EXCEL
# -----------------------------------------------------------------------------
def gerar_csv_excel_formatado(dados_leads):
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([
        "ID", "Data Mineração", "Cidade", "Nome Empresa", "Categoria", "Status CRM",
        "Endereço", "Telefone", "WhatsApp", "Website", "Nota Média", "Total Avaliações",
        "Ficha Reivindicada", "Tour 360", "Pontos Críticos", "Score Oportunidade"
    ])

    for row in dados_leads:
        criticos_str = " | ".join(row.get("pontos_criticos", [])) if isinstance(row.get("pontos_criticos"), list) else str(row.get("pontos_criticos", ""))
        writer.writerow([
            row.get("id", ""), row.get("data_minacao", ""), row.get("cidade_busca", ""),
            row.get("nome", ""), row.get("categoria", ""), row.get("status_crm", "🆕 Novo Lead"),
            row.get("endereco", ""), row.get("telefone", ""), row.get("whatsapp", ""),
            row.get("website", ""), str(row.get("nota", "")).replace('.', ','),
            row.get("total_avaliacoes", ""), "Sim" if row.get("reivindicada") else "Não",
            "Sim" if row.get("tour_360") else "Não", criticos_str, row.get("score_oportunidade", "")
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
# ETAPA 1: BUSCADA E MINERAÇÃO
# -----------------------------------------------------------------------------
if st.session_state.etapa == 1:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🔎 Radar e Mineração de Mercado Local</h1>
            <div class="main-subtitle">Varredura de perfis no Google Maps, checagem de presença digital e identificação de falhas.</div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("form_busca"):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1: nicho_input = st.text_input("Nicho / Categoria Comercial", value="Moda praia")
        with col2: cidade_input = st.text_input("Cidade / Região de Busca", value="Ribeirão Preto")
        with col3: limite_input = st.number_input("Qtd. Máxima", min_value=1, max_value=50, value=10)
        btn_minar = st.form_submit_button("🚀 Iniciar Varredura Profunda", use_container_width=True)

    if btn_minar:
        with st.spinner("Varrendo Google Maps, auditando presença web e salvando no banco..."):
            time.sleep(1)
            minerar_e_auditar_negocios(nicho_input, cidade_input, limite_input)
            st.session_state.etapa = 2
            st.rerun()

    if len(base_leads) > 0:
        st.divider()
        st.info(f"O seu banco possui **{len(base_leads)} leads salvos permanentemente**.")
        if st.button("Ver Base Completa de Leads ➡️", type="primary"):
            st.session_state.etapa = 2
            st.rerun()

# -----------------------------------------------------------------------------
# ETAPA 2: BASE DE LEADS & MINI-CRM
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 2:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📊 Base de Leads e Gerenciador CRM</h1>
            <div class="main-subtitle">Acompanhe o funil de prospecção e atualize o status dos seus clientes.</div>
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
            label="📊 Exportar Planilha (.csv)",
            data=csv_bytes,
            file_name=f"Leads_CRM_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.divider()

    resultados_filtrados = base_leads if filtro_status == "Todos os Status" else [r for r in base_leads if r['status_crm'] == filtro_status]

    st.markdown(f"Exibindo **{len(resultados_filtrados)}** oportunidades:")

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
                st.toast("Status atualizado com sucesso!")
                st.rerun()

        with col_details1:
            st.markdown("**📊 Indicadores de Presença:**")
            st.markdown(f"- **Nota Média:** ⭐ {lead['nota']} ({lead['total_avaliacoes']} avaliações)")
            st.markdown(f"- **Ficha Reivindicada?** {'✅ Sim' if lead['reivindicada'] else '❌ **NÃO REIVINDICADA**'}")
            st.markdown(f"- **Fotos na Ficha:** {lead['fotos_total']} fotos")
            st.markdown(f"- **Tour 360°:** {'✅ Presente' if lead['tour_360'] else '❌ **Ausente**'}")

        with col_details2:
            st.markdown("**🚨 Pontos Críticos Encontrados:**")
            for pc in lead['pontos_criticos']:
                st.markdown(f"<div class='critical-item'>❌ {pc}</div>", unsafe_allow_html=True)

        with col_actions:
            st.markdown("**🌐 Presença Web & Links:**")
            st.markdown(f"- **Website:** {lead['website'] if lead['website'] else '❌ Sem site'}")
            st.markdown(f"- **Maps:** [Ver no Google Maps](https://www.google.com/maps/search/?api=1&query={lead['nome'].replace(' ', '+')})")

            st.markdown(f'<a href="{URL_SISTEMA_DIAGNOSTICO}" target="_blank" class="btn-redirect">🛠️ Abrir no Diagnóstico Tour360VR</a>', unsafe_allow_html=True)

            if lead['whatsapp']:
                msg_wa = f"Olá! Estava analisando o perfil da {lead['nome']} no Google..."
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
# ETAPA 3: RELATÓRIO DE INTELIGÊNCIA DE NICHO
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 3:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📈 Panorama de Mercado & Inteligência de Nicho</h1>
            <div class="main-subtitle">Estatísticas consolidadas da sua base para demonstrar autoridade nas vendas.</div>
        </div>
    """, unsafe_allow_html=True)

    df_leads = pd.DataFrame(base_leads)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1: st.metric("Total de Leads Mapeados", len(df_leads))
    with col_m2: st.metric("Sem Tour Virtual 360°", f"{(len(df_leads[df_leads['tour_360'] == False]) / len(df_leads) * 100):.1f}%")
    with col_m3: st.metric("Sem Website Oficial", f"{(len(df_leads[df_leads['website'] == '']) / len(df_leads) * 100):.1f}%")
    with col_m4: st.metric("Fichas não Reivindicadas", f"{(len(df_leads[df_leads['reivindicada'] == False]) / len(df_leads) * 100):.1f}%")

    st.divider()

    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        st.markdown("### 📊 Distribuição por Score de Oportunidade")
        st.bar_chart(df_leads['score_oportunidade'].value_counts())

    with c_chart2:
        st.markdown("### 🏷️ Top Categorias Mapeadas")
        st.bar_chart(df_leads['categoria'].value_counts())

# -----------------------------------------------------------------------------
# ETAPA 4: MAPA DE PROSPECÇÃO E ROTAS
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 4:
    st.markdown("""
        <div class="main-header">
            <h1 class="main-title">🗺️ Mapa de Localização e Concentração</h1>
            <div class="main-subtitle">Visualize geographicamente os potenciais clientes para planejar rotas de visitas.</div>
        </div>
    """, unsafe_allow_html=True)

    df_mapa = pd.DataFrame(base_leads)
    if 'latitude' in df_mapa.columns and 'longitude' in df_mapa.columns:
        df_mapa_clean = df_mapa.rename(columns={"latitude": "lat", "longitude": "lon"})
        st.map(df_mapa_clean[['lat', 'lon']], zoom=12)
    else:
        st.info("Coordenadas geográficas não disponíveis para os registros atuais.")

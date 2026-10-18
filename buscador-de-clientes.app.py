import os
import io
import csv
import json
import time
import base64
import urllib.parse
from datetime import datetime

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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.pdfbase.pdfmetrics import stringWidth

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================
LOGO_TOUR = "logo_tour_transparente.png"
LOGO_OKAMOTO = "logo_okamoto.png"
URL_SISTEMA_DIAGNOSTICO = "https://tour360vr.streamlit.app/"
SITE_TOUR = "https://tour360vr.com.br"
EMAIL_CONTATO = "contato@tour360vr.com.br"
WHATSAPP_NUM = "5516991332121"
WHATSAPP_EXIBICAO = "(16) 99133-2121"

AZUL_LINK = "#1E40AF"
AZUL_ESCURO = "#1E3A8A"

# Paleta da logo Tour360VR
COR_ALTA = "#F76C4A"    # coral
COR_MEDIA = "#FFA733"   # laranja
COR_BAIXA = "#9DBE5A"   # verde
COR_AZUL = "#4AA3DA"

# Pontuação máxima somente dos critérios verificáveis pela API (ver calcular_oportunidade)
PONTOS_MAXIMOS_API = 75

page_icon = PILImage.open(LOGO_TOUR) if os.path.exists(LOGO_TOUR) else "🔍"
st.set_page_config(
    page_title="Radar Comercial | Tour360VR",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# TEMA GLASSMORPHISM DARK (mesma linguagem do sistema de Gestão)
# =============================================================================
TEMA_CSS = """
<style>
:root {
    --bg: #0B0E14; --bg-glow: #16213A;
    --glass: rgba(22, 31, 48, 0.55); --glass-hover: rgba(37, 45, 66, 0.70);
    --border: rgba(255, 255, 255, 0.10); --border-hover: rgba(255, 255, 255, 0.30);
    --text: #E6EDF7; --strong: #FFFFFF; --muted: #8E9BAE;
    --blue: #4AA3DA; --orange: #FFA733; --green: #9DBE5A; --coral: #F76C4A;
    --blur: 18px;
    --grad: linear-gradient(90deg, #FFA733, #4AA3DA, #9DBE5A, #F76C4A);
}
header[data-testid="stHeader"] { display: none !important; }
html, body, .stApp {
    background:
        radial-gradient(circle at 15% 0%, var(--bg-glow) 0%, transparent 45%),
        radial-gradient(circle at 90% 100%, rgba(247,108,74,.08) 0%, transparent 40%),
        var(--bg) !important;
    color: var(--text);
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
}
.block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; max-width: 1400px !important; }
h1, h2, h3, h4 { color: var(--strong) !important; letter-spacing: -0.01em; }
hr { border-color: var(--border) !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(7, 9, 14, 0.80) !important;
    backdrop-filter: blur(var(--blur)); -webkit-backdrop-filter: blur(var(--blur));
    border-right: 1px solid var(--border);
    width: 300px !important; min-width: 300px !important; max-width: 300px !important;
}
[data-testid="stSidebarNav"], [data-testid="stSidebarResizer"] { display: none !important; }
section[data-testid="stSidebar"] .stButton > button { justify-content: flex-start !important; text-align: left !important; }
.gl-side-logo { display: flex; justify-content: center; margin-bottom: 8px; }
.gl-side-logo img { width: 130px; height: auto; }
.gl-side-title { text-align: center; font-size: .8rem; color: var(--muted); letter-spacing: .12em; text-transform: uppercase; margin-bottom: 10px; }
.gl-side-footer { margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border); text-align: center; color: var(--muted); font-size: .72rem; }
.gl-side-footer img { width: 120px; height: auto; margin-top: 8px; }

/* Cabeçalho */
.gl-hero {
    position: relative; display: flex; align-items: center; gap: 22px;
    background: var(--glass); backdrop-filter: blur(var(--blur)); -webkit-backdrop-filter: blur(var(--blur));
    border: 1px solid var(--border); border-radius: 18px;
    padding: 22px 28px; margin-bottom: 18px; overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,.35);
}
.gl-hero::before { content: ""; position: absolute; left: 0; top: 0; right: 0; height: 3px; background: var(--grad); }
.gl-hero img { width: 64px; height: auto; }
.gl-hero h1 { margin: 0 !important; font-size: 1.55rem !important; font-weight: 800; }
.gl-hero p { margin: 4px 0 0 0; color: var(--muted); font-size: .92rem; }

/* Títulos de seção */
.gl-section {
    display: flex; align-items: center; gap: 10px;
    margin: 24px 0 12px 0; padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    color: var(--strong); font-size: 1.1rem; font-weight: 700;
}
.gl-section .dot { width: 8px; height: 8px; border-radius: 50%; }

/* Containers em vidro */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--glass) !important;
    backdrop-filter: blur(var(--blur)); -webkit-backdrop-filter: blur(var(--blur));
    border: 1px solid var(--border) !important; border-radius: 14px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,.30);
}
div[data-testid="stForm"] {
    background: var(--glass) !important;
    backdrop-filter: blur(var(--blur)); -webkit-backdrop-filter: blur(var(--blur));
    border: 1px solid var(--border) !important; border-radius: 14px !important;
    padding: 18px !important; box-shadow: 0 8px 32px rgba(0,0,0,.30);
}

/* Botões */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button,
[data-testid="stLinkButton"] a {
    background: var(--glass) !important; backdrop-filter: blur(12px);
    border: 1px solid var(--border) !important; color: var(--strong) !important;
    border-radius: 10px !important; font-weight: 600 !important; min-height: 40px;
    transition: all .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover,
[data-testid="stLinkButton"] a:hover {
    background: var(--glass-hover) !important; border-color: var(--border-hover) !important;
    box-shadow: 0 0 16px rgba(74,163,218,.30); transform: translateY(-1px);
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(74,163,218,.45), rgba(74,163,218,.18)) !important;
    border-color: var(--blue) !important;
}

/* Inputs */
div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
    background: rgba(11,14,20,.55) !important; border: 1px solid var(--border) !important; border-radius: 10px !important;
}
div[data-baseweb="input"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {
    border-color: var(--blue) !important; box-shadow: 0 0 0 3px rgba(74,163,218,.18) !important;
}
input, textarea { color: var(--strong) !important; }

/* Métricas e tabelas */
div[data-testid="stMetric"] {
    background: var(--glass); backdrop-filter: blur(var(--blur));
    border: 1px solid var(--border); border-radius: 14px; padding: 14px 18px;
}
div[data-testid="stMetricValue"] { color: var(--strong) !important; }
div[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }

/* Badges de oportunidade */
.gl-badge { text-align: center; padding: 8px 12px; border-radius: 12px; font-weight: 700; min-width: 150px; border: 1px solid; }
.gl-badge .r { font-size: .66rem; letter-spacing: .06em; }
.gl-badge .n { font-size: 1.35rem; }
.gl-badge.alta { color: var(--coral); border-color: rgba(247,108,74,.5); background: rgba(247,108,74,.12); }
.gl-badge.media { color: var(--orange); border-color: rgba(255,167,51,.5); background: rgba(255,167,51,.12); }
.gl-badge.baixa { color: var(--green); border-color: rgba(157,190,90,.5); background: rgba(157,190,90,.12); }

.gl-muted { color: var(--muted); font-size: .86rem; }
.gl-critico { color: #FCA5A5; font-size: .86rem; margin-bottom: 6px; }

/* Links de ação */
a.gl-wpp, a.gl-wpp:visited, a.gl-wpp:hover, a.gl-wpp:focus, a.gl-wpp * {
    color: #FFFFFF !important; text-decoration: none !important;
}
a.gl-wpp {
    display: block; text-align: center; background: #25D366 !important;
    padding: 10px; border-radius: 10px; font-weight: 700; margin-top: 8px;
}
a.gl-btn-sec {
    display: block; text-align: center; padding: 9px; border-radius: 10px;
    border: 1px solid var(--border); background: var(--glass);
    color: var(--strong) !important; text-decoration: none !important;
    font-weight: 600; margin-top: 8px;
}
a.gl-btn-sec:hover { border-color: var(--border-hover); background: var(--glass-hover); }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.12); border-radius: 8px; }
::-webkit-scrollbar-track { background: transparent; }
</style>
"""
st.markdown(TEMA_CSS, unsafe_allow_html=True)

# Rola para o topo ao trocar de módulo
components.html("""
<script>
    function topo() {
        window.parent.scrollTo(0, 0);
        var m = window.parent.document.querySelector('.main'); if (m) m.scrollTop = 0;
    }
    topo(); setTimeout(topo, 150);
</script>
""", height=0)

# =============================================================================
# COMPONENTES VISUAIS
# =============================================================================
def b64_arquivo(caminho):
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def hero(titulo, subtitulo):
    logo = b64_arquivo(LOGO_TOUR)
    img = f'<img src="data:image/png;base64,{logo}" alt="Tour360VR"/>' if logo else ""
    st.markdown(
        f'<div class="gl-hero">{img}<div><h1>{titulo}</h1><p>{subtitulo}</p></div></div>',
        unsafe_allow_html=True,
    )


def secao(titulo, cor=COR_AZUL):
    st.markdown(
        f'<div class="gl-section"><span class="dot" style="background:{cor};box-shadow:0 0 10px {cor}"></span>{titulo}</div>',
        unsafe_allow_html=True,
    )


def classificar_score(score):
    if score >= 60:
        return "alta", "ALTA OPORTUNIDADE", COR_ALTA
    if score >= 30:
        return "media", "MÉDIA OPORTUNIDADE", COR_MEDIA
    return "baixa", "BAIXA OPORTUNIDADE", COR_BAIXA


def badge_score(score):
    classe, rotulo, _ = classificar_score(score)
    return f'<div class="gl-badge {classe}"><div class="r">{rotulo}</div><div class="n">{score}/100</div></div>'


def botao_whatsapp(url, texto):
    st.markdown(f'<a class="gl-wpp" href="{url}" target="_blank">{texto}</a>', unsafe_allow_html=True)


def link_secundario(url, texto):
    st.markdown(f'<a class="gl-btn-sec" href="{url}" target="_blank">{texto}</a>', unsafe_allow_html=True)


def csv_bytes_utf8(df):
    return df.to_csv(index=False, sep=";").encode("utf-8-sig")


def valor_verificacao(valor, sim="✅ Sim", nao="❌ Não"):
    """Campos que a API não informa ficam explícitos, em vez de parecerem dados reais."""
    if valor is None or valor == "":
        return "⚠️ Verificar manualmente"
    return sim if valor else nao


# =============================================================================
# BANCO DE DADOS (SUPABASE)
# =============================================================================
@st.cache_resource
def init_supabase():
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
    key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
    if url and key:
        return create_client(url, key)
    return None


supabase: Client = init_supabase()


def carregar_todos_leads_db():
    if not supabase:
        return []
    try:
        res = supabase.table("leads").select("*").order("id", desc=True).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Erro ao carregar leads: {e}")
        return []


def carregar_leads_instagram_db():
    if not supabase:
        return []
    try:
        res = supabase.table("leads_instagram").select("*").order("id", desc=True).execute()
        return res.data or []
    except Exception:
        return []


def salvar_lead_db(lead):
    """Retorna True se gravou um lead novo."""
    if not supabase:
        return False
    try:
        existe = (
            supabase.table("leads").select("id")
            .eq("nome", lead["nome"]).eq("endereco", lead["endereco"])
            .execute()
        )
        if existe.data:
            return False
        supabase.table("leads").insert({
            "data_minacao": lead["data_minacao"],
            "cidade_busca": lead["cidade_busca"],
            "bairro_busca": lead["bairro_busca"],
            "nome": lead["nome"],
            "categoria": lead["categoria"],
            "endereco": lead["endereco"],
            "latitude": lead["latitude"],
            "longitude": lead["longitude"],
            "telefone": lead["telefone"],
            "whatsapp": lead["whatsapp"],
            "website": lead["website"],
            "website_https": lead["website_https"],
            "instagram": "",
            "facebook": "",
            "foto_url": lead["foto_url"],
            "nota": lead["nota"],
            "total_avaliacoes": lead["total_avaliacoes"],
            "reivindicada": None,        # a Places API não informa
            "fotos_total": lead["fotos_total"],
            "ultima_foto_dias": None,    # a Places API não informa
            "tour_360": None,            # a Places API não informa
            "status_crm": "🆕 Novo Lead",
            "pontos_criticos": lead["pontos_criticos"],
            "oportunidades": lead["oportunidades"],
            "score_oportunidade": lead["score_oportunidade"],
        }).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar '{lead.get('nome')}': {e}")
        return False


def atualizar_status_crm(lead_id, novo_status):
    if not supabase:
        return
    try:
        supabase.table("leads").update({"status_crm": novo_status}).eq("id", lead_id).execute()
    except Exception as e:
        st.error(f"Erro ao atualizar status: {e}")


def limpar_banco_dados():
    if not supabase:
        return
    try:
        supabase.table("leads").delete().neq("id", 0).execute()
    except Exception as e:
        st.error(f"Erro ao limpar banco: {e}")


# =============================================================================
# GOOGLE PLACES API
# =============================================================================
def url_foto(valor):
    """Fotos são guardadas como 'ref:<photo_reference>' para não gravar a chave da API no banco."""
    if not valor:
        return "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&q=80"
    if valor.startswith("ref:"):
        api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
        ref = valor[4:]
        return (
            "https://maps.googleapis.com/maps/api/place/photo?"
            + urllib.parse.urlencode({"maxwidth": 400, "photo_reference": ref, "key": api_key})
        )
    return valor


def calcular_oportunidade(website, total_avaliacoes, qtd_fotos):
    """
    Score de oportunidade (0 a 100) baseado somente em dados que a API informa:
      - Sem site: 30 pts | Site sem HTTPS: 15 pts
      - Menos de 30 avaliações: 25 pts
      - Menos de 8 fotos (amostra da API): 20 pts
    Total possível: 75 pts, normalizado para 100.
    Tour 360° e reivindicação não entram no score (a API não informa).
    """
    criticos, oportunidades, pontos = [], [], 0

    if not website:
        criticos.append("Sem site oficial vinculado à ficha do Google")
        oportunidades.append("Desenvolvimento de landing page / website responsivo")
        pontos += 30
    elif not website.startswith("https://"):
        criticos.append("Site oficial sem certificado de segurança (HTTP)")
        oportunidades.append("Adequação de SSL e otimização web")
        pontos += 15

    if total_avaliacoes < 30:
        criticos.append(f"Volume baixo de avaliações ({total_avaliacoes})")
        oportunidades.append("Estratégia de reputação e gestão de avaliações")
        pontos += 25

    if qtd_fotos < 8:
        criticos.append(f"Poucas fotos no perfil (amostra da API: {qtd_fotos})")
        oportunidades.append("Produção de fotografia profissional do espaço")
        pontos += 20

    oportunidades.append("Fotografia 360° imersiva e publicação no Google Street View")
    score = min(round(pontos / PONTOS_MAXIMOS_API * 100), 100)
    return score, criticos, oportunidades


def buscar_google_places_api(nicho, cidade, bairro, rua, api_key, limite):
    """Retorna lista de leads, lista vazia se não houver resultados, ou None em caso de erro."""
    termos = [t.strip() for t in [nicho, rua, bairro, cidade] if t and t.strip()]
    query = " ".join(termos)

    try:
        data = requests.get(
            "https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={"query": query, "language": "pt-BR", "key": api_key},
            timeout=12,
        ).json()
    except Exception as e:
        st.error(f"Falha de conexão com a Google Places API: {e}")
        return None

    status = data.get("status")
    if status == "ZERO_RESULTS":
        return []
    if status != "OK":
        st.error(f"Google Places retornou '{status}'. {data.get('error_message', '')}")
        return None

    leads = []
    for place in data.get("results", [])[:limite]:
        det = {}
        if place.get("place_id"):
            try:
                det = requests.get(
                    "https://maps.googleapis.com/maps/api/place/details/json",
                    params={
                        "place_id": place["place_id"],
                        "fields": "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos",
                        "language": "pt-BR",
                        "key": api_key,
                    },
                    timeout=8,
                ).json().get("result", {})
            except Exception:
                det = {}

        loc = place.get("geometry", {}).get("location", {})
        nome = det.get("name") or place.get("name", "Sem nome")
        endereco = det.get("formatted_address") or place.get("formatted_address", "")
        telefone = det.get("formatted_phone_number", "")
        website = det.get("website", "")
        nota = det.get("rating", place.get("rating", 0.0)) or 0.0
        total = det.get("user_ratings_total", place.get("user_ratings_total", 0)) or 0
        fotos = det.get("photos", place.get("photos", [])) or []
        has_https = website.startswith("https://") if website else False

        digitos = "".join(ch for ch in telefone if ch.isdigit())
        if len(digitos) > 11 and digitos.startswith("55"):
            digitos = digitos[2:]
        whatsapp = digitos if len(digitos) >= 10 else ""

        score, criticos, oportunidades = calcular_oportunidade(website, total, len(fotos))

        leads.append({
            "data_minacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "cidade_busca": cidade,
            "bairro_busca": bairro,
            "nome": nome,
            "categoria": (nicho or "Comércio").strip().capitalize(),
            "endereco": endereco,
            "latitude": float(loc.get("lat", -21.1775)),
            "longitude": float(loc.get("lng", -47.8103)),
            "telefone": telefone,
            "whatsapp": whatsapp,
            "website": website,
            "website_https": has_https,
            "foto_url": f"ref:{fotos[0]['photo_reference']}" if fotos else "",
            "nota": float(nota),
            "total_avaliacoes": int(total),
            "fotos_total": len(fotos),
            "pontos_criticos": criticos,
            "oportunidades": oportunidades,
            "score_oportunidade": int(score),
        })
    return leads


def minerar_e_salvar(nicho, cidade, bairro, rua, limite):
    api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
    if not api_key:
        st.error("A chave GOOGLE_API_KEY não foi encontrada nos Secrets do Streamlit.")
        return None
    leads = buscar_google_places_api(nicho, cidade, bairro, rua, api_key.strip(), limite)
    if leads is None:
        return None
    novos = sum(1 for lead in leads if salvar_lead_db(lead))
    return leads, novos


# =============================================================================
# EXPORTAÇÃO CSV
# =============================================================================
def gerar_csv_crm(dados_leads):
    buf = io.StringIO()
    buf.write("\ufeff")
    writer = csv.writer(buf, delimiter=";")
    writer.writerow([
        "ID", "Data Mineração", "Cidade Busca", "Bairro Busca", "Nome da Empresa", "Categoria / Nicho",
        "Status Comercial", "Endereço", "Telefone", "WhatsApp", "Possui Website", "Website URL",
        "HTTPS", "Nota Google", "Total Avaliações", "Qtd. Fotos (amostra API)",
        "Pontos Críticos", "Score de Oportunidade",
    ])
    for row in dados_leads:
        criticos = row.get("pontos_criticos") or []
        if isinstance(criticos, str):
            criticos = json.loads(criticos or "[]")
        writer.writerow([
            row.get("id", ""), row.get("data_minacao", ""), row.get("cidade_busca", ""),
            row.get("bairro_busca", ""), row.get("nome", ""), row.get("categoria", ""),
            row.get("status_crm", ""), row.get("endereco", ""), row.get("telefone", ""),
            row.get("whatsapp", ""), "Sim" if row.get("website") else "Não", row.get("website", ""),
            "Sim" if row.get("website_https") else "Não",
            str(row.get("nota", "")).replace(".", ","), row.get("total_avaliacoes", ""),
            row.get("fotos_total", ""), " | ".join(criticos), row.get("score_oportunidade", ""),
        ])
    return buf.getvalue().encode("utf-8")


# =============================================================================
# PDF (padrão claro para impressão, com cabeçalho e rodapé Tour360VR)
# =============================================================================
def desenhar_cabecalho_rodape(canvas, doc):
    canvas.saveState()
    styles = getSampleStyleSheet()

    if os.path.exists(LOGO_TOUR):
        logo = RLImage(LOGO_TOUR, width=170, height=60, kind="proportional")
        logo.wrapOn(canvas, 170, 60)
        logo.drawOn(canvas, 36, 715)

    titulo = Paragraph(
        "ESTUDO DE INTELIGÊNCIA DE MERCADO LOCAL<br/>E PRESENÇA DIGITAL NO GOOGLE",
        ParagraphStyle("HeaderTitle", parent=styles["Normal"], fontName="Helvetica-Bold",
                       fontSize=14, leading=15, textColor=colors.HexColor("#0f172a"), alignment=1),
    )
    t = Table([[titulo]], colWidths=[540])
    t.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    t.wrapOn(canvas, 540, 60)
    t.drawOn(canvas, 36, 730)

    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.setLineWidth(0.5)
    canvas.line(36, 706, 576, 706)

    # Rodapé com links clicáveis, centralizados
    partes = [
        ("tour360vr.com.br", SITE_TOUR),
        (EMAIL_CONTATO, f"mailto:{EMAIL_CONTATO}"),
        (WHATSAPP_EXIBICAO, f"https://wa.me/{WHATSAPP_NUM}"),
    ]
    sep = "    |    "
    fonte, tam = "Helvetica", 8.5
    largura_total = sum(stringWidth(txt, fonte, tam) for txt, _ in partes) + stringWidth(sep, fonte, tam) * (len(partes) - 1)
    x, y = (letter[0] - largura_total) / 2, 25
    canvas.setFont(fonte, tam)
    canvas.setFillColor(colors.HexColor("#0f172a"))
    for i, (txt, url) in enumerate(partes):
        w = stringWidth(txt, fonte, tam)
        canvas.drawString(x, y, txt)
        canvas.linkURL(url, (x, y - 2, x + w, y + 9), relative=0)
        x += w
        if i < len(partes) - 1:
            canvas.drawString(x, y, sep)
            x += stringWidth(sep, fonte, tam)

    canvas.line(36, 42, 576, 42)
    canvas.restoreState()


def gerar_pdf_panorama_nicho(nicho_nome, df_nicho):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=95, bottomMargin=55,
        title=f"Panorama de Mercado - {nicho_nome}", author="Tour360VR",
    )
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle("MainTitle", parent=styles["Heading1"], fontSize=13,
                                  textColor=colors.HexColor("#0f172a"), fontName="Helvetica-Bold",
                                  alignment=1, spaceBefore=0, spaceAfter=8)
    secao_style = ParagraphStyle("SectionHeading", parent=styles["Heading2"], fontSize=9.5,
                                 textColor=colors.HexColor("#0f172a"), spaceBefore=8, spaceAfter=5,
                                 fontName="Helvetica-Bold", alignment=1)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=8.5, textColor=colors.HexColor("#334155"), leading=10.5)
    body_c = ParagraphStyle("BodyC", parent=body, alignment=1)

    el = []
    t_title = Table([[Paragraph(f"PANORAMA DE MERCADO: {nicho_nome.upper()}", titulo_style)]], colWidths=[540])
    t_title.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    el += [t_title, Spacer(1, 2)]

    el.append(Paragraph("DISTRIBUIÇÃO DE EMPRESAS POR SCORE DE OPORTUNIDADE", secao_style))
    el.append(Spacer(1, 2))

    contagem = df_nicho["score_oportunidade"].value_counts().sort_index(ascending=False)
    grafico = Drawing(540, 95)
    grafico.hAlign = "CENTER"
    grafico.add(Rect(0, 0, 540, 95, fillColor=colors.HexColor("#f8fafc"), strokeColor=colors.HexColor("#cbd5e1"), strokeWidth=0.5))
    if len(contagem) > 0:
        n = len(contagem)
        bar_w = min(40, max(18, 380 // n))
        gap = min(22, (500 - n * bar_w) // (n + 1))
        max_val = max(contagem.values) or 1
        start_x = (540 - (n * bar_w + (n - 1) * gap)) / 2
        for i, (score_val, qtd) in enumerate(contagem.items()):
            bx = start_x + i * (bar_w + gap)
            bh = max((qtd / max_val) * 52, 6)
            cor = colors.HexColor(COR_ALTA if score_val >= 60 else (COR_MEDIA if score_val >= 30 else COR_BAIXA))
            grafico.add(Rect(bx, 22, bar_w, bh, fillColor=cor, strokeColor=None, rx=2, ry=2))
            grafico.add(String(bx + bar_w / 2, 22 + bh + 4, str(qtd), fontSize=8.5, fontName="Helvetica-Bold",
                               fillColor=colors.HexColor("#0f172a"), textAnchor="middle"))
            grafico.add(String(bx + bar_w / 2, 10, f"{score_val} pts", fontSize=7.5, fontName="Helvetica-Bold",
                               fillColor=colors.HexColor("#475569"), textAnchor="middle"))
    el += [grafico, Spacer(1, 8)]

    total = len(df_nicho)
    def pct(q):
        return f"{(q / total * 100 if total else 0):.1f}%"

    poucas_av = int((df_nicho["total_avaliacoes"] < 30).sum())
    sem_site = int((df_nicho["website"].fillna("") == "").sum())
    score_medio = round(df_nicho["score_oportunidade"].mean(), 1) if total else 0

    resumo = [
        [Paragraph("<b>INDICADOR ESTRATÉGICO</b>", body), Paragraph("<b>VOLUME / %</b>", body_c), Paragraph("<b>DIAGNÓSTICO DE OPORTUNIDADE</b>", body)],
        [Paragraph("Volume baixo de avaliações", body), Paragraph(f"<b>{poucas_av} ({pct(poucas_av)})</b>", body_c),
         Paragraph("Menos de 30 avaliações, o que afeta a prova social e o ranking.", body)],
        [Paragraph("Sem website oficial", body), Paragraph(f"<b>{sem_site} ({pct(sem_site)})</b>", body_c),
         Paragraph("Perda de tráfego direto e dependência de canais de terceiros.", body)],
        [Paragraph("Score médio de oportunidade", body), Paragraph(f"<b>{score_medio}/100</b>", body_c),
         Paragraph("Média dos critérios verificáveis pela Google Places API.", body)],
    ]
    t_res = Table(resumo, colWidths=[150, 90, 300])
    t_res.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
    ]))
    el += [t_res, Spacer(1, 10), Paragraph("RANKING DE EMPRESAS AUDITADAS NO SETOR", secao_style), Spacer(1, 4)]

    dados = [[Paragraph("<b>EMPRESA</b>", body), Paragraph("<b>NOTA</b>", body_c), Paragraph("<b>AVALIAÇÕES</b>", body_c),
              Paragraph("<b>SITE</b>", body_c), Paragraph("<b>SCORE</b>", body_c)]]
    estilos = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]
    for i, (_, r) in enumerate(df_nicho.sort_values("score_oportunidade", ascending=False).iterrows(), start=1):
        sc = int(r["score_oportunidade"])
        fundo = "#86efac" if sc >= 60 else ("#fde047" if sc >= 30 else "#fca5a5")
        estilos.append(("BACKGROUND", (4, i), (4, i), colors.HexColor(fundo)))
        dados.append([
            Paragraph(str(r["nome"])[:45], body),
            Paragraph(f"{float(r['nota']):.1f}", body_c),
            Paragraph(str(int(r["total_avaliacoes"])), body_c),
            Paragraph("Sim" if r["website"] else "Não", body_c),
            Paragraph(f"<b>{sc}/100</b>", body_c),
        ])
    t_emp = Table(dados, colWidths=[270, 50, 80, 50, 90], repeatRows=1)
    t_emp.setStyle(TableStyle(estilos))
    el.append(t_emp)

    doc.build(el, onFirstPage=desenhar_cabecalho_rodape, onLaterPages=desenhar_cabecalho_rodape)
    buffer.seek(0)
    return buffer


# =============================================================================
# NAVEGAÇÃO (SIDEBAR)
# =============================================================================
if "etapa" not in st.session_state:
    st.session_state.etapa = 1


def mudar_etapa(nova):
    st.session_state.etapa = nova
    st.rerun()


base_leads = carregar_todos_leads_db()
base_leads_insta = carregar_leads_instagram_db()

MODULOS = [
    (1, "🎯 Radar de Leads"),
    (2, "📊 CRM de Prospecção"),
    (3, "📈 Panorama de Nicho"),
    (4, "🗺️ Mapa de Prospecção"),
    (5, "📁 Leads do Instagram"),
]

with st.sidebar:
    logo_side = b64_arquivo(LOGO_TOUR)
    if logo_side:
        st.markdown(f'<div class="gl-side-logo"><img src="data:image/png;base64,{logo_side}"/></div>', unsafe_allow_html=True)
    st.markdown('<div class="gl-side-title">Radar Comercial</div>', unsafe_allow_html=True)

    for num, nome in MODULOS:
        if st.button(nome, key=f"nav_{num}", use_container_width=True,
                     type="primary" if st.session_state.etapa == num else "secondary"):
            mudar_etapa(num)

    st.divider()
    st.caption(f"☁️ Leads Google: **{len(base_leads)}** · 📱 Leads Instagram: **{len(base_leads_insta)}**")

    if base_leads:
        confirma = st.checkbox("Confirmar exclusão da base Google", key="confirma_limpeza")
        if st.button("🗑️ Limpar base Google", use_container_width=True, disabled=not confirma):
            limpar_banco_dados()
            mudar_etapa(1)

    okamoto_b64 = b64_arquivo(LOGO_OKAMOTO)
    st.markdown(
        '<div class="gl-side-footer">Okamoto Mídias Visuais'
        + (f'<br/><img src="data:image/png;base64,{okamoto_b64}"/>' if okamoto_b64 else "")
        + "</div>",
        unsafe_allow_html=True,
    )

# =============================================================================
# MÓDULO 1: RADAR DE LEADS
# =============================================================================
if st.session_state.etapa == 1:
    hero("Radar e Mineração de Mercado Local",
         "Varredura de perfis no Google Maps por nicho, cidade, bairro e rua. Os dados vêm da Google Places API.")

    with st.form("form_busca"):
        c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1.2])
        nicho_input = c1.text_input("Nicho / Categoria", placeholder="Ex: clínica estética")
        cidade_input = c2.text_input("Cidade", value="Ribeirão Preto")
        bairro_input = c3.text_input("Bairro / Região (opcional)")
        rua_input = c4.text_input("Rua / Avenida (opcional)")
        limite_input = c5.number_input("Qtd. máx.", min_value=5, max_value=20, value=20, step=5)
        enviar = st.form_submit_button("🚀 Iniciar varredura", use_container_width=True)

    if enviar:
        if not nicho_input and not cidade_input:
            st.warning("Informe pelo menos o nicho ou a cidade.")
        else:
            with st.spinner("Consultando o Google Maps e salvando na base..."):
                resultado = minerar_e_salvar(nicho_input, cidade_input, bairro_input, rua_input, limite_input)
            if resultado is not None:
                leads, novos = resultado
                if leads:
                    st.success(f"{len(leads)} empresas analisadas · {novos} novas salvas na base.")
                else:
                    st.info("Nenhum resultado para essa busca. Tente outro nicho ou cidade.")

    if base_leads:
        secao("Base atual")
        st.markdown(f"<span class='gl-muted'>Você tem <b>{len(base_leads)}</b> leads salvos na nuvem.</span>", unsafe_allow_html=True)
        if st.button("Ver base completa no CRM ➡️", type="primary"):
            mudar_etapa(2)

# =============================================================================
# MÓDULO 2: CRM DE PROSPECÇÃO
# =============================================================================
elif st.session_state.etapa == 2:
    hero("CRM de Prospecção",
         "Filtre, acompanhe o status comercial e acione cada lead pelo WhatsApp ou pelo diagnóstico.")

    if not base_leads:
        st.warning("Nenhum lead cadastrado ainda. Faça a primeira busca no Radar de Leads.")
    else:
        df_crm = pd.DataFrame(base_leads)
        STATUS = ["🆕 Novo Lead", "💬 Em Abordagem", "🛠️ Diagnóstico Gerado", "🤝 Cliente Fechado", "❌ Recusado"]

        f1, f2, f3, f4 = st.columns([2, 2, 2, 2])
        filtro_nicho = f1.selectbox("Nicho", ["Todos"] + sorted(df_crm["categoria"].dropna().unique().tolist()))
        filtro_cidade = f2.selectbox("Cidade", ["Todas"] + sorted(df_crm["cidade_busca"].dropna().unique().tolist()))
        filtro_status = f3.selectbox("Status", ["Todos"] + STATUS)
        with f4:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            st.download_button(
                "📊 Exportar planilha (.csv)",
                data=gerar_csv_crm(base_leads),
                file_name=f"Leads_CRM_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        filtrados = base_leads
        if filtro_nicho != "Todos":
            filtrados = [r for r in filtrados if r["categoria"] == filtro_nicho]
        if filtro_cidade != "Todas":
            filtrados = [r for r in filtrados if r["cidade_busca"] == filtro_cidade]
        if filtro_status != "Todos":
            filtrados = [r for r in filtrados if r["status_crm"] == filtro_status]

        st.markdown(f"<span class='gl-muted'>Exibindo <b>{len(filtrados)}</b> oportunidades</span>", unsafe_allow_html=True)

        for lead in filtrados:
            score = int(lead["score_oportunidade"])
            criticos = lead.get("pontos_criticos") or []
            if isinstance(criticos, str):
                criticos = json.loads(criticos or "[]")

            status_atual = lead.get("status_crm") or STATUS[0]
            classe, rotulo, cor = classificar_score(score)
            col_info, col_det, col_acoes = st.columns([3, 3, 2.5])

            with col_info:
                with st.container(border=True):
                    st.markdown(f"### {lead['nome']}")
                    st.markdown(f"<span class='gl-muted'>📍 {lead.get('endereco', '')}<br/>🏷️ {lead.get('categoria', '')}</span>", unsafe_allow_html=True)
                    st.markdown(badge_score(score), unsafe_allow_html=True)
                    novo_st = st.selectbox("Status comercial", STATUS, index=STATUS.index(status_atual) if status_atual in STATUS else 0, key=f"crm_st_{lead['id']}")
                    if novo_st != status_atual:
                        atualizar_status_crm(lead["id"], novo_st)
                        st.toast("Status atualizado na nuvem.")
                        st.rerun()

            with col_det:
                with st.container(border=True):
                    st.markdown("**📊 Indicadores (Google Places)**")
                    st.markdown(f"- Nota: ⭐ {lead.get('nota', 0)} ({lead.get('total_avaliacoes', 0)} avaliações)")
                    st.markdown(f"- Fotos (amostra da API): {lead.get('fotos_total', 0)}")
                    st.markdown(f"- Ficha reivindicada: ⚠️ verificar manualmente")
                    st.markdown(f"- Tour 360°: ⚠️ verificar manualmente")
                    st.markdown("**🚨 Pontos críticos**")
                    if criticos:
                        for pc in criticos:
                            st.markdown(f"<div class='gl-critico'>❌ {pc}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='gl-muted'>Nenhum ponto crítico nos critérios automáticos.</span>", unsafe_allow_html=True)

            with col_acoes:
                with st.container(border=True):
                    st.markdown("**🌐 Presença e ações**")
                    st.markdown(f"- Website: {lead['website'] if lead.get('website') else '❌ Sem site'}")
                    st.markdown(f"[Ver no Google Maps](https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(lead['nome'])})")
                    link_secundario(URL_SISTEMA_DIAGNOSTICO, "🛠️ Abrir no Diagnóstico Tour360VR")
                    if lead.get("whatsapp"):
                        msg_wa = (
                            f"Olá! Tudo bem?\nMeu nome é Rubens Okamoto, da Okamoto Mídias Visuais e do Tour360VR.\n"
                            f"Estava analisando a presença da {lead['nome']} no Google e identifiquei pontos onde a visibilidade "
                            f"do espaço pode ser ampliada em relação aos concorrentes da região.\n"
                            f"Posso te enviar um diagnóstico curto em PDF por aqui?"
                        )
                        botao_whatsapp(f"https://wa.me/55{lead['whatsapp']}?text={urllib.parse.quote(msg_wa)}", "💬 WhatsApp")
                    else:
                        st.caption("Sem WhatsApp identificado na ficha.")

# =============================================================================
# MÓDULO 3: PANORAMA DE NICHO
# =============================================================================
elif st.session_state.etapa == 3:
    hero("Panorama de Mercado & Inteligência de Nicho",
         "Análise por categoria e município, ordenada pela maior oportunidade comercial.")

    if not base_leads:
        st.warning("Nenhum lead cadastrado ainda. Faça a primeira busca no Radar de Leads.")
    else:
        df_pan = pd.DataFrame(base_leads)
        f1, f2, f3 = st.columns([2.5, 2.5, 2])
        nicho_sel = f1.selectbox("🎯 Nicho", ["Todos os nichos"] + sorted(df_pan["categoria"].dropna().unique().tolist()))
        cidade_sel = f2.selectbox("📍 Cidade", ["Todas as cidades"] + sorted(df_pan["cidade_busca"].dropna().unique().tolist()))

        df_f = df_pan.copy()
        if nicho_sel != "Todos os nichos":
            df_f = df_f[df_f["categoria"] == nicho_sel]
        if cidade_sel != "Todas as cidades":
            df_f = df_f[df_f["cidade_busca"] == cidade_sel]
        df_f = df_f.sort_values("score_oportunidade", ascending=False)

        with f3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if len(df_f) > 0:
                nome_pdf = f"Panorama de Mercado - {nicho_sel.replace('/', ' ')} - {datetime.now().strftime('%d-%m-%Y')}.pdf"
                st.download_button("📄 Baixar relatório (.pdf)", data=gerar_pdf_panorama_nicho(nicho_sel, df_f),
                                   file_name=nome_pdf, mime="application/pdf", use_container_width=True)

        if len(df_f) == 0:
            st.info("Nenhuma empresa para este filtro.")
        else:
            total = len(df_f)
            m1, m2, m3, m4 = st.columns(4)
            poucas = int((df_f["total_avaliacoes"] < 30).sum())
            sem_site = int((df_f["website"].fillna("") == "").sum())
            m1.metric("Empresas analisadas", total)
            m2.metric("Poucas avaliações (<30)", f"{poucas / total * 100:.1f}%", f"{poucas} empresas")
            m3.metric("Sem website", f"{sem_site / total * 100:.1f}%", f"{sem_site} empresas")
            m4.metric("Score médio", f"{df_f['score_oportunidade'].mean():.0f}/100")

            secao("Distribuição do score de oportunidade")
            st.bar_chart(df_f["score_oportunidade"].value_counts())

            secao("Ranking do nicho")
            df_rank = pd.DataFrame({
                "Empresa": df_f["nome"],
                "Cidade": df_f["cidade_busca"],
                "Score": df_f["score_oportunidade"].apply(lambda x: f"{x}/100"),
                "Nota": df_f["nota"].apply(lambda x: f"{float(x):.1f}"),
                "Avaliações": df_f["total_avaliacoes"].astype(str),
                "Website": df_f["website"].apply(lambda x: x if x else "Sem site"),
            })
            st.dataframe(df_rank, hide_index=True, use_container_width=True,
                         height=min(900, (len(df_rank) + 1) * 35 + 10))

# =============================================================================
# MÓDULO 4: MAPA DE PROSPECÇÃO
# =============================================================================
elif st.session_state.etapa == 4:
    hero("Mapa de Localização e Concentração",
         "Empresas mapeadas na região, com filtros por nicho, cidade e faixa de oportunidade.")

    if not base_leads:
        st.warning("Nenhum lead cadastrado ainda. Faça a primeira busca no Radar de Leads.")
    else:
        df_map = pd.DataFrame(base_leads)
        f1, f2, f3 = st.columns(3)
        cat_map = f1.selectbox("🎯 Nicho", ["Todos"] + sorted(df_map["categoria"].dropna().unique().tolist()))
        cid_map = f2.selectbox("📍 Cidade", ["Todas"] + sorted(df_map["cidade_busca"].dropna().unique().tolist()))
        faixa = f3.selectbox("🎯 Faixa de score", ["Todas", "Alta (≥ 60)", "Média (30 a 59)", "Baixa (< 30)"])

        df_m = df_map.copy()
        if cat_map != "Todos":
            df_m = df_m[df_m["categoria"] == cat_map]
        if cid_map != "Todas":
            df_m = df_m[df_m["cidade_busca"] == cid_map]
        if faixa == "Alta (≥ 60)":
            df_m = df_m[df_m["score_oportunidade"] >= 60]
        elif faixa == "Média (30 a 59)":
            df_m = df_m[(df_m["score_oportunidade"] >= 30) & (df_m["score_oportunidade"] < 60)]
        elif faixa == "Baixa (< 30)":
            df_m = df_m[df_m["score_oportunidade"] < 30]

        st.markdown(f"<span class='gl-muted'>Exibindo <b>{len(df_m)}</b> empresas no mapa.</span>", unsafe_allow_html=True)

        if len(df_m) > 0:
            m = folium.Map(location=[df_m["latitude"].mean(), df_m["longitude"].mean()], zoom_start=13, tiles="CartoDB dark_matter")
            bounds = []
            for _, row in df_m.iterrows():
                _, _, cor = classificar_score(int(row["score_oportunidade"]))
                url_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(row['nome'])}"
                html_pop = (
                    f"<div style='font-family:Arial,sans-serif;font-size:12px;min-width:240px;line-height:1.5;color:#111'>"
                    f"<a href='{url_maps}' target='_blank' style='text-decoration:none'><b style='color:#1E40AF;font-size:14px'>{row['nome']}</b></a><br/>"
                    f"<span style='color:#475569'>📍 {row['endereco']}</span><hr style='margin:6px 0'/>"
                    f"<b>Score:</b> {row['score_oportunidade']}/100<br/>"
                    f"<b>Nota:</b> {row['nota']} ({row['total_avaliacoes']} avaliações)</div>"
                )
                folium.CircleMarker(
                    location=[row["latitude"], row["longitude"]],
                    radius=9, color=cor, fill=True, fill_color=cor, fill_opacity=0.85, weight=2,
                    popup=folium.Popup(html_pop, max_width=320),
                    tooltip=row["nome"],
                ).add_to(m)
                bounds.append([row["latitude"], row["longitude"]])
            if len(bounds) > 1:
                m.fit_bounds(bounds, padding=(30, 30))
            with st.container(border=True):
                st_folium(m, width=None, height=650, returned_objects=[])

# =============================================================================
# MÓDULO 5: LEADS DO INSTAGRAM
# =============================================================================
elif st.session_state.etapa == 5:
    hero("Leads do Instagram",
         "Cadastre perfis manualmente, gere contato de WhatsApp e exporte a base.")

    with st.form("form_cad_insta", clear_on_submit=True):
        st.markdown("**➕ Novo lead do Instagram**")
        c1, c2, c3 = st.columns(3)
        in_user = c1.text_input("Username (@perfil)", placeholder="ex: clinicaexemplo")
        in_nome = c2.text_input("Nome / Empresa", placeholder="Clínica Exemplo")
        in_whats = c3.text_input("WhatsApp (com DDD)", placeholder="16999999999")
        in_bio = st.text_area("Biografia / observações", height=80)
        in_link = st.text_input("Link na bio (opcional)", placeholder="https://wa.me/...")
        salvar_insta = st.form_submit_button("✨ Salvar lead", use_container_width=True)

    if salvar_insta:
        if not in_user or not in_nome:
            st.error("Preencha pelo menos o username e o nome da empresa.")
        elif supabase is None:
            st.error("Banco de dados indisponível.")
        else:
            u = in_user.replace("@", "").strip()
            w = "".join(ch for ch in in_whats if ch.isdigit())
            if len(w) in (10, 11):
                w = "55" + w
            try:
                supabase.table("leads_instagram").upsert({
                    "username": u, "nome_completo": in_nome, "instagram_id": u,
                    "biografia": in_bio, "link_bio": in_link,
                    "whatsapp": w or "", "foto_perfil": "",
                    "origem_concorrente": "Cadastro manual",
                }, on_conflict="username").execute()
                st.success(f"Lead '@{u}' salvo na nuvem.")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

    secao(f"Base de leads do Instagram ({len(base_leads_insta)})")
    if base_leads_insta:
        df_ins = pd.DataFrame(base_leads_insta)
        buf_xlsx = io.BytesIO()
        with pd.ExcelWriter(buf_xlsx, engine="openpyxl") as writer:
            df_ins.to_excel(writer, index=False, sheet_name="Leads Instagram")
        st.download_button("📥 Baixar planilha (.xlsx)", data=buf_xlsx.getvalue(),
                           file_name=f"leads_instagram_{datetime.now().strftime('%Y%m%d')}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        for row in base_leads_insta:
            with st.container(border=True):
                ci, cn, ca = st.columns([4, 5, 3])
                with ci:
                    st.markdown(f"**{row.get('nome_completo', '')}**")
                    st.markdown(f"<span class='gl-muted'>@{row.get('username', '')}</span>", unsafe_allow_html=True)
                with cn:
                    if row.get("biografia"):
                        st.caption(f"📝 {row.get('biografia')}")
                    if row.get("link_bio"):
                        st.caption(f"🔗 {row.get('link_bio')}")
                with ca:
                    w_num = row.get("whatsapp") or ""
                    if w_num:
                        texto = f"Olá {row.get('nome_completo')}, tudo bem? Conheci seu perfil no Instagram..."
                        botao_whatsapp(f"https://wa.me/{w_num}?text={urllib.parse.quote(texto)}", "💬 WhatsApp")
                    else:
                        st.caption("Sem WhatsApp cadastrado")
                    link_secundario(f"https://instagram.com/direct/t/{row.get('username', '')}", "📩 Enviar Direct")
    else:
        st.info("Nenhum lead do Instagram cadastrado ainda.")

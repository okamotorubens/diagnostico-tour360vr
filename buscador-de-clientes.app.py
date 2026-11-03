import base64
import csv
from datetime import date, datetime
import io
import json
import os
import re
import time
import unicodedata
import urllib.parse

import folium
import pandas as pd
from PIL import Image as PILImage
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
import requests
from streamlit_folium import st_folium
from supabase import Client, create_client
import streamlit as st
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# CONFIGURAÇÕES DO SISTEMA E LINKS INSTITUCIONAIS
# -----------------------------------------------------------------------------
URL_SISTEMA_DIAGNOSTICO = "https://tour360vr.streamlit.app/"
CONTATO_WHATSAPP = "(16) 99133-2121"
EMAIL_CONTATO = "contato@okamotomidiasvisuais.com.br"
WEBSITE_OFICIAL = "tour360vr.com.br"

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA STREAMLIT E FAVICON NO NAVEGADOR
# -----------------------------------------------------------------------------
favicon_img = "🔍"
favicon_b64 = ""
path_logo_png = (
    "assests/logo_tour_transparente.png"
    if os.path.exists("assests/logo_tour_transparente.png")
    else (
        "logo_tour_transparente.png"
        if os.path.exists("logo_tour_transparente.png")
        else None
    )
)

if path_logo_png:
  try:
    favicon_img = PILImage.open(path_logo_png)
    with open(path_logo_png, "rb") as f:
      favicon_b64 = base64.b64encode(f.read()).decode()
  except Exception:
    favicon_img = "🔍"

st.set_page_config(
    page_title="Radar Comercial | Tour360VR",
    page_icon=favicon_img if not favicon_b64 else PILImage.open(path_logo_png),
    layout="wide",
    initial_sidebar_state="expanded",
)

# FORÇAR O NAVEGADOR A IR PARA O TOPO
components.html(
    f"""
    <script>
        function scrollToTop() {{
            try {{
                window.parent.scrollTo({{ top: 0, behavior: 'instant' }});
                var containers = window.parent.document.querySelectorAll('.main, .stAppViewContainer, section.main, [data-testid="stAppViewContainer"], [data-testid="stMain"]');
                containers.forEach(function(el) {{
                    if (el) {{ el.scrollTop = 0; }}
                }});
            }} catch(e) {{}}
        }}
        scrollToTop();
        setTimeout(scrollToTop, 50);
        setTimeout(scrollToTop, 150);
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
""",
    height=0,
)

components.html(
    """
    <script>
        if (!window.parent.document.getElementById("btn-voltar-topo")) {
            const btnTop = window.parent.document.createElement("button");
            btnTop.id = "btn-voltar-topo";
            btnTop.innerHTML = "⬆️ Topo";
            btnTop.style.position = "fixed";
            btnTop.style.bottom = "85px";
            btnTop.style.right = "25px";
            btnTop.style.zIndex = "999999";
            btnTop.style.backgroundColor = "#2563eb";
            btnTop.style.color = "#ffffff";
            btnTop.style.border = "none";
            btnTop.style.borderRadius = "30px";
            btnTop.style.padding = "10px 16px";
            btnTop.style.fontSize = "13px";
            btnTop.style.fontWeight = "bold";
            btnTop.style.cursor = "pointer";
            btnTop.style.boxShadow = "0 4px 12px rgba(0,0,0,0.4)";
            btnTop.style.transition = "all 0.3s ease";

            btnTop.onmouseover = function() { btnTop.style.backgroundColor = "#1d4ed8"; };
            btnTop.onmouseout = function() { btnTop.style.backgroundColor = "#2563eb"; };

            btnTop.onclick = function() {
                window.parent.scrollTo({ top: 0, behavior: 'smooth' });
                var containers = window.parent.document.querySelectorAll('.main, .stAppViewContainer, section.main, [data-testid="stAppViewContainer"], [data-testid="stMain"]');
                containers.forEach(function(el) {
                    if (el) { el.scrollTop = 0; }
                });
            };

            window.parent.document.body.appendChild(btnTop);
        }
    </script>
""",
    height=0,
)

# -----------------------------------------------------------------------------
# BANCO DE DADOS EM NUVEM (SUPABASE)
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
    res = (
        supabase.table("leads")
        .select("id")
        .eq("nome", lead["nome"])
        .eq("endereco", lead["endereco"])
        .execute()
    )
    if not res.data:
      supabase.table("leads").insert({
          "data_minacao": lead.get(
              "data_minacao", datetime.now().strftime("%d/%m/%Y %H:%M")
          ),
          "cidade_busca": lead.get("cidade_busca", ""),
          "bairro_busca": lead.get("bairro_busca", ""),
          "nome": lead["nome"],
          "categoria": lead["categoria"],
          "endereco": lead["endereco"],
          "latitude": float(lead.get("latitude", -21.1775)),
          "longitude": float(lead.get("longitude", -47.8103)),
          "telefone": lead.get("telefone", ""),
          "whatsapp": lead.get("whatsapp", ""),
          "website": lead.get("website", ""),
          "website_https": bool(lead.get("website_https")),
          "instagram": lead.get("instagram", ""),
          "facebook": lead.get("facebook", ""),
          "foto_url": lead.get("foto_url", ""),
          "nota": float(lead.get("nota", 0.0)),
          "total_avaliacoes": int(lead.get("total_avaliacoes", 0)),
          "reivindicada": bool(lead.get("reivindicada")),
          "fotos_total": int(lead.get("fotos_total", 0)),
          "ultima_foto_dias": int(lead.get("ultima_foto_dias", 0)),
          "tour_360": bool(lead.get("tour_360", False)),
          "status_crm": lead.get("status_crm", "🆕 Novo Lead"),
          "pontos_criticos": lead.get("pontos_criticos", []),
          "oportunidades": lead.get("oportunidades", []),
          "score_oportunidade": int(lead.get("score_oportunidade", 0)),
          "anotacoes": lead.get("anotacoes", ""),
          "favorito": bool(lead.get("favorito", False)),
          "data_followup": lead.get("data_followup", str(date.today())),
          "obs_followup": lead.get("obs_followup", ""),
      }).execute()
  except Exception as e:
    st.error(f"Erro ao salvar lead '{lead.get('nome')}': {str(e)}")

def atualizar_status_crm(lead_id, novo_status):
  if not supabase:
    return
  try:
    (
        supabase.table("leads")
        .update({"status_crm": novo_status})
        .eq("id", lead_id)
        .execute()
    )
  except Exception as e:
    st.error(f"Erro ao atualizar status: {str(e)}")

def atualizar_categoria_db(lead_id, nova_categoria):
  if not supabase:
    return
  try:
    (
        supabase.table("leads")
        .update({"categoria": nova_categoria})
        .eq("id", lead_id)
        .execute()
    )
  except Exception as e:
    st.error(f"Erro ao atualizar categoria: {str(e)}")

def atualizar_anotacoes_db(lead_id, novas_anotacoes):
  if not supabase:
    return
  try:
    (
        supabase.table("leads")
        .update({"anotacoes": novas_anotacoes})
        .eq("id", lead_id)
        .execute()
    )
  except Exception as e:
    st.error(f"Erro ao atualizar anotações: {str(e)}")

def alternar_favorito_db(lead_id, status_atual):
  if not supabase:
    return
  try:
    novo_val = not status_atual
    (
        supabase.table("leads")
        .update({"favorito": novo_val})
        .eq("id", lead_id)
        .execute()
    )
  except Exception as e:
    st.error(f"Erro ao atualizar favorito: {str(e)}")

def atualizar_followup_db(lead_id, nova_data):
  if not supabase:
    return
  try:
    (
        supabase.table("leads")
        .update({"data_followup": str(nova_data)})
        .eq("id", lead_id)
        .execute()
    )
  except Exception as e:
    st.error(f"Erro ao atualizar follow-up: {str(e)}")

def atualizar_dados_cadastrais_db(lead_id, dados_dict):
  if not supabase:
    return
  try:
    supabase.table("leads").update(dados_dict).eq("id", lead_id).execute()
  except Exception as e:
    st.error(f"Erro ao atualizar dados do lead: {str(e)}")

def obter_coordenadas_endereco(endereco_completo, cidade):
  endereco_str = f"{endereco_completo}, {cidade}, Brasil"
  api_key = st.secrets.get("GOOGLE_API_KEY", None) or os.getenv(
      "GOOGLE_API_KEY", None
  )
  if api_key:
    api_key_limpa = api_key.strip().replace('"', "").replace("'", "")
    geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(endereco_str)}&key={api_key_limpa}"
    try:
      resp = requests.get(geo_url, timeout=5).json()
      if resp.get("status") == "OK":
        loc = resp["results"][0]["geometry"]["location"]
        return float(loc["lat"]), float(loc["lng"])
    except Exception:
      pass

  try:
    nom_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(endereco_str)}&format=json&limit=1"
    headers = {"User-Agent": "Tour360VR-RadarComercial/1.0"}
    resp_nom = requests.get(nom_url, headers=headers, timeout=5).json()
    if resp_nom and len(resp_nom) > 0:
      return float(resp_nom[0]["lat"]), float(resp_nom[0]["lon"])
  except Exception:
    pass

  return -21.1775, -47.8103

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
# CÁLCULO DE SCORE DE OTIMIZAÇÃO & AUDITORIA DA FICHA
# -----------------------------------------------------------------------------
def calcular_score_e_auditoria(
    fotos_total,
    tour_360,
    website,
    total_avaliacoes,
    nota,
    has_https=True,
    reivindicada=True,
):
  pontos_criticos = []
  oportunidades = []
  score_saude = 100

  if not website:
    pontos_criticos.append(
        "Sem website oficial vinculado à ficha do Google (perda de tráfego"
        " direto)"
    )
    oportunidades.append(
        "Desenvolvimento de Landing Page / Website Responsivo de alta"
        " conversão"
    )
    score_saude -= 20
  elif not has_https:
    pontos_criticos.append(
        "Website sem certificado de segurança SSL (alerta de site inseguro)"
    )
    oportunidades.append(
        "Adequação de Segurança SSL e Otimização Web Estrutural"
    )
    score_saude -= 10

  if total_avaliacoes < 30:
    pontos_criticos.append(
        f"Volume crítico de avaliações ({total_avaliacoes} total), afetando a"
        " prova social perante concorrentes"
    )
    oportunidades.append(
        "Estratégia Acelerada de Reputação, QR Codes e Gestão de Avaliações no"
        " Google"
    )
    score_saude -= 20

  if not tour_360:
    pontos_criticos.append(
        "Ausência de Tour Virtual 360° interativo navegável no perfil do Google"
        " Street View"
    )
    oportunidades.append(
        "Implantação de Fotografia 360° Imersiva e Publicação Oficial no Google"
        " Maps"
    )
    score_saude -= 25

  if fotos_total < 8:
    pontos_criticos.append(
        f"Acervo visual reduzido no perfil ({fotos_total} fotos públicas)"
    )
    oportunidades.append(
        "Produção de Fotografia Profissional em Alta Resolução"
    )
    score_saude -= 15

  score_saude = max(20, min(score_saude, 100))
  score_oportunidade = 100 - score_saude

  return {
      "score_saude": score_saude,
      "score_oportunidade": score_oportunidade,
      "pontos_criticos": pontos_criticos,
      "oportunidades": oportunidades,
  }

def revalidar_ficha_google(lead):
  api_key = st.secrets.get("GOOGLE_API_KEY", None) or os.getenv(
      "GOOGLE_API_KEY", None
  )
  if not api_key:
    st.error("Chave do Google API Key não configurada.")
    return lead

  api_key_limpa = api_key.strip().replace('"', "").replace("'", "")
  nome_limpo = re.sub(r"[´`\'\"]", "", lead["nome"])
  query_str = f"{nome_limpo} {lead['cidade_busca']}"
  base_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={urllib.parse.quote(query_str)}&language=pt-BR&key={api_key_limpa}"

  try:
    resp = requests.get(base_url, timeout=10).json()
    results = resp.get("results", [])
    if not results:
      st.warning(
          "⚠️ O Google Maps não retornou dados atualizados para esta empresa"
          " neste momento."
      )
      return lead

    place = results[0]
    place_id = place.get("place_id")

    det_res = {}
    if place_id:
      details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos&language=pt-BR&key={api_key_limpa}"
      det_res = requests.get(details_url, timeout=5).json().get("result", {})

    nova_nota = det_res.get("rating", place.get("rating", lead["nota"]))
    novas_av = det_res.get(
        "user_ratings_total",
        place.get("user_ratings_total", lead["total_avaliacoes"]),
    )
    novo_site = det_res.get("website", lead["website"])
    photos = det_res.get("photos", place.get("photos", [])) or []

    auditoria = calcular_score_e_auditoria(
        fotos_total=len(photos),
        tour_360=lead.get("tour_360", False),
        website=novo_site,
        total_avaliacoes=novas_av,
        nota=nova_nota,
    )

    dif_av = novas_av - lead["total_avaliacoes"]
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    aviso_reval = f"[{data_hoje}] 🔄 Revalidação Google: Nota {nova_nota} (Antes: {lead['nota']}), Avaliações: {novas_av} ({'+' if dif_av>=0 else ''}{dif_av}). Saúde Ficha: {auditoria['score_saude']}/100."

    anotacoes_atuais = lead.get("anotacoes", "") or ""
    novas_anotacoes = f"{aviso_reval}\n{anotacoes_atuais}"

    if supabase:
      supabase.table("leads").update({
          "nota": float(nova_nota),
          "total_avaliacoes": int(novas_av),
          "website": novo_site,
          "fotos_total": len(photos),
          "pontos_criticos": auditoria["pontos_criticos"],
          "oportunidades": auditoria["oportunidades"],
          "score_oportunidade": auditoria["score_oportunidade"],
          "anotacoes": novas_anotacoes,
      }).eq("id", lead["id"]).execute()

    lead["nota"] = nova_nota
    lead["total_avaliacoes"] = novas_av
    lead["website"] = novo_site
    lead["fotos_total"] = len(photos)
    lead["pontos_criticos"] = auditoria["pontos_criticos"]
    lead["oportunidades"] = auditoria["oportunidades"]
    lead["score_oportunidade"] = auditoria["score_oportunidade"]
    lead["anotacoes"] = novas_anotacoes

    st.success(
        "✅ Ficha revalidada com sucesso! (Variação de avaliações:"
        f" {'+' if dif_av>=0 else ''}{dif_av})"
    )
    return lead
  except Exception as e:
    st.error(f"Erro ao revalidar ficha: {str(e)}")
    return lead

# -----------------------------------------------------------------------------
# GERADOR DE PDF DO DIAGNÓSTICO (LAYOUT MODERNO DIAGRAMADO PROFISSIONALMENTE)
# -----------------------------------------------------------------------------
def desenhar_cabecalho_rodape_diagnostico(canvas, doc):
  canvas.saveState()
  styles = getSampleStyleSheet()

  # --- CABEÇALHO ---
  logo_tour_path = (
      "assests/logo_tour_transparente.png"
      if os.path.exists("assests/logo_tour_transparente.png")
      else (
          "logo_tour_transparente.png"
          if os.path.exists("logo_tour_transparente.png")
          else None
      )
  )

  # LOGO EXPANDIDA E REORGANIZADA
  if logo_tour_path:
    try:
      canvas.drawImage(
          logo_tour_path,
          36,
          730,
          width=110,
          height=48,
          preserveAspectRatio=True,
          mask="auto",
      )
    except Exception:
      pass

  header_text_style = ParagraphStyle(
      "HeaderDiagnostico",
      parent=styles["Normal"],
      fontName="Helvetica-Bold",
      fontSize=9.5,
      leading=12,
      textColor=colors.HexColor("#0f172a"),
      alignment=2,  # ALINHADO À DIREITA
  )

  head_p = Paragraph(
      "ESTUDO DE INTELIGÊNCIA DE MERCADO LOCAL<br/>E PRESENÇA DIGITAL NO"
      " GOOGLE",
      header_text_style,
  )
  head_table = Table([[head_p]], colWidths=[380])
  head_table.wrapOn(canvas, 380, 36)
  head_table.drawOn(canvas, 196, 736)

  # Linha divisória em tom Azul Marinho Fino
  canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
  canvas.setLineWidth(0.75)
  canvas.line(36, 724, 576, 724)

  # --- RODAPÉ (FIXO NO FINAL DA PÁGINA) ---
  canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
  canvas.setLineWidth(0.75)
  canvas.line(36, 34, 576, 34)

  style_footer = ParagraphStyle(
      "FooterLinkStyle",
      parent=styles["Normal"],
      fontName="Helvetica-Bold",
      fontSize=8,
      textColor=colors.HexColor("#334155"),
      alignment=1,  # Centralizado
  )

  zap_clean = "".join(filter(str.isdigit, CONTATO_WHATSAPP))
  footer_html = f'<a href="mailto:{EMAIL_CONTATO}" color="#0284c7">{EMAIL_CONTATO}</a> &nbsp;|&nbsp; <a href="https://{WEBSITE_OFICIAL}" color="#0284c7">{WEBSITE_OFICIAL}</a> &nbsp;|&nbsp; <a href="https://wa.me/55{zap_clean}" color="#16a34a">WhatsApp: {CONTATO_WHATSAPP}</a>'
  p_footer = Paragraph(footer_html, style_footer)
  t_footer = Table([[p_footer]], colWidths=[540])
  t_footer.wrapOn(canvas, 540, 20)
  t_footer.drawOn(canvas, 36, 16)

  canvas.restoreState()


def gerar_pdf_diagnostico_individual(lead):
  buffer = io.BytesIO()

  # Configuração visual A4 em página única
  doc = SimpleDocTemplate(
      buffer,
      pagesize=letter,
      rightMargin=36,
      leftMargin=36,
      topMargin=72,
      bottomMargin=42,
      title=f"Diagnóstico de Presença Digital - {lead['nome']}",
      author="Tour360VR",
  )

  styles = getSampleStyleSheet()

  style_normal = ParagraphStyle(
      "NormCustom",
      parent=styles["Normal"],
      fontName="Helvetica",
      fontSize=8,
      leading=10.5,
      textColor=colors.HexColor("#334155"),
  )
  style_title = ParagraphStyle(
      "TitleDiag",
      parent=styles["Heading1"],
      fontSize=12,
      leading=14,
      textColor=colors.HexColor("#0f172a"),
      fontName="Helvetica-Bold",
      alignment=1,
  )
  style_sub = ParagraphStyle(
      "SubDiag",
      parent=style_normal,
      fontSize=8.5,
      leading=11.5,
      textColor=colors.HexColor("#475569"),
      alignment=1,
  )
  style_section_heading = ParagraphStyle(
      "SectionHead",
      parent=styles["Heading2"],
      fontSize=8.5,
      leading=11,
      textColor=colors.HexColor("#0f172a"),
      fontName="Helvetica-Bold",
      spaceBefore=6,
      spaceAfter=3,
  )

  auditoria = calcular_score_e_auditoria(
      fotos_total=lead.get("fotos_total", 5),
      tour_360=lead.get("tour_360", False),
      website=lead.get("website", ""),
      total_avaliacoes=lead.get("total_avaliacoes", 0),
      nota=lead.get("nota", 0.0),
  )

  score_saude = auditoria["score_saude"]
  has_site = bool(lead.get("website"))
  has_tour = bool(lead.get("tour_360"))
  fotos_cnt = lead.get("fotos_total", 0)
  av_total = lead.get("total_avaliacoes", 0)
  nota_val = lead.get("nota", 0.0)

  # Cor dinâmica e viva para a nota do Score Geral
  if score_saude >= 80:
    cor_score = "#16a34a"  # Verde
  elif score_saude >= 50:
    cor_score = "#d97706"  # Laranja/Amarelo Escuro
  else:
    cor_score = "#dc2626"  # Vermelho

  elements = []

  # 1. TÍTULO CENTRALIZADO
  elements.append(Paragraph("DIAGNÓSTICO DE PRESENÇA DIGITAL", style_title))
  elements.append(Spacer(1, 6))

  # 2. CONTAINER COM DADOS DA EMPRESA
  dados_empresa_html = (
      f"<b>Empresa:</b> {lead['nome']} ({lead['categoria']}) &nbsp;|&nbsp;"
      f" <b>Cidade:</b> {lead['cidade_busca']}<br/><b>Endereço:</b>"
      f" {lead['endereco']}<br/><b>Contato/Fixo:</b>"
      f" {lead.get('telefone', '(16) Contato via Ficha')} &nbsp;|&nbsp;"
      f" <b>Website:</b> {lead.get('website', 'Não possui site vinculado')}"
  )
  p_dados = Paragraph(dados_empresa_html, style_normal)
  t_dados = Table([[p_dados]], colWidths=[540])
  t_dados.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
          ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
          ("PADDING", (0, 0), (-1, -1), 6),
      ])
  )
  elements.append(t_dados)
  elements.append(Spacer(1, 6))

  # 3. SUBTÍTULO
  subtitulo_html = "Este diagnóstico foi elaborado pelo Tour360VR com base em inteligência de mercado local<br/>para destacar pontos cegos na sua vitrine digital do Google."
  elements.append(Paragraph(subtitulo_html, style_sub))
  elements.append(Spacer(1, 8))

  # 4. QUADRO DE ATENÇÃO DA ATUAL SITUAÇÃO (AZUL MARINHO ELEGANTE)
  txt_alerta = f"SEU PERFIL TEM NOTA SÓLIDA DE {nota_val} COM {av_total} AVALIAÇÕES NO GOOGLE, MAS A FALTA DE EXPERIÊNCIA IMERSIVA DEIXA DINHEIRO NA MESA."
  p_alerta = Paragraph(
      f"<b><font color='#0f172a' size='9'>{txt_alerta}</font></b>",
      ParagraphStyle("AlertaTxt", parent=style_normal, alignment=1, leading=12),
  )
  t_alerta = Table([[p_alerta]], colWidths=[540])
  t_alerta.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f9ff")),
          ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#0284c7")),
          ("PADDING", (0, 0), (-1, -1), 7),
      ])
  )
  elements.append(t_alerta)
  elements.append(Spacer(1, 8))

  # 5. QUADRO DE SCORE GERAL E AVALIAÇÕES
  p_card_score = Paragraph(
      f"<b>SCORE GERAL</b><br/><font size='18'"
      f" color='{cor_score}'><b>{score_saude} / 100</b></font>",
      ParagraphStyle(
          "CScore", parent=style_normal, alignment=1, leading=18, fontSize=8
      ),
  )
  p_card_nota = Paragraph(
      f"<b>AVALIAÇÃO DO GOOGLE</b><br/><font size='16'"
      f" color='#0f172a'><b>{nota_val} ★</b></font><br/><font size='7'"
      f" color='#64748b'>({av_total} avaliações públicas)</font>",
      ParagraphStyle(
          "CNota", parent=style_normal, alignment=1, leading=14, fontSize=8
      ),
  )
  t_cards = Table([[p_card_score, p_card_nota]], colWidths=[265, 265])
  t_cards.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
          ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
          ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
          ("PADDING", (0, 0), (-1, -1), 6),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
      ])
  )
  elements.append(t_cards)
  elements.append(Spacer(1, 8))

  # 6. TABELA DOS 9 ITENS DE DIAGNÓSTICO (CABECALHO AZUL MARINHO)
  itens_9 = [
      (
          "1. Fotos e Resolução Visual",
          "Atende" if fotos_cnt >= 8 else "Reduzido",
          f"{fotos_cnt} fotos públicas cadastradas na ficha do Google Maps.",
      ),
      (
          "2. Tour Virtual 360° Interativo",
          "Ausente" if not has_tour else "Ativo",
          "Sem navegação imersiva no Street View (perda de retenção).",
      ),
      (
          "3. Categoria Principal",
          "Completo",
          f"Perfil categorizado corretamente como '{lead['categoria']}'.",
      ),
      (
          "4. Horários de Funcionamento",
          "Atualizado",
          "Horários de atendimento visíveis aos clientes.",
      ),
      (
          "5. Website Oficial",
          "Ativo" if has_site else "Ausente",
          (
              lead.get("website")[:38]
              if has_site
              else "Sem link oficial para conversão direta."
          ),
      ),
      (
          "6. Prova Social (Avaliações)",
          f"{nota_val} ★",
          f"Acervo de {av_total} avaliações públicas registradas.",
      ),
      (
          "7. Resumo Editorial",
          "Completo",
          "Descrição institucional e metadados ativos.",
      ),
      (
          "8. Atributos de Serviços",
          "Pendente",
          "Atributos essenciais pendentes de otimização.",
      ),
      (
          "9. Resposta a Avaliações",
          "Pendente",
          "Avaliações sem resposta oficial da gestão.",
      ),
  ]

  style_cell_head = ParagraphStyle(
      "CellHead", parent=style_normal, fontName="Helvetica-Bold", color=colors.white, fontSize=8
  )
  style_cell_tb = ParagraphStyle("CellTB", parent=style_normal, fontSize=7.5)
  style_cell_bold = ParagraphStyle(
      "CellTBBold", parent=style_cell_tb, fontName="Helvetica-Bold"
  )

  rows_9 = [[
      Paragraph("Item de Auditoria", style_cell_head),
      Paragraph("Status", style_cell_head),
      Paragraph("Diagnóstico Detalhado", style_cell_head),
  ]]

  for it, st_tag, obs in itens_9:
    c_color = (
        "#16a34a"
        if st_tag in ["Atende", "Completo", "Atualizado", "Ativo"]
        else "#dc2626"
    )
    rows_9.append([
        Paragraph(it, style_cell_bold),
        Paragraph(
            f"<b><font color='{c_color}'>{st_tag}</font></b>", style_cell_tb
        ),
        Paragraph(obs, style_cell_tb),
    ])

  t_9 = Table(rows_9, colWidths=[170, 75, 295])
  t_9.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),  # AZUL MARINHO
          ("BACKGROUND", (0, 1), (-1, -1), colors.white),
          ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
          ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
          ("TOPPADDING", (0, 0), (-1, -1), 3),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
      ])
  )
  elements.append(t_9)
  elements.append(Spacer(1, 8))

  # 7. PONTOS CRÍTICOS IDENTIFICADOS NA VITRINE DIGITAL
  elements.append(
      Paragraph(
          "PONTOS CRÍTICOS IDENTIFICADOS NA VITRINE DIGITAL",
          style_section_heading,
      )
  )
  elements.append(Spacer(1, 3))

  criticos_lista = (
      lead["pontos_criticos"]
      if isinstance(lead.get("pontos_criticos"), list)
      else auditoria["pontos_criticos"]
  )
  if not criticos_lista:
    criticos_lista = auditoria["pontos_criticos"]

  rows_criticos = []
  for pc in criticos_lista[:3]:
    rows_criticos.append(
        [Paragraph(f"<font color='#dc2626'>[X] {pc}</font>", style_cell_tb)]
    )

  t_criticos = Table(rows_criticos, colWidths=[540])
  t_criticos.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
          ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecaca")),
          ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fee2e2")),
          ("TOPPADDING", (0, 0), (-1, -1), 3),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
      ])
  )
  elements.append(t_criticos)
  elements.append(Spacer(1, 8))

  # 8. OPORTUNIDADES DE TRANSFORMAÇÃO E RETORNO COMERCIAL
  elements.append(
      Paragraph(
          "OPORTUNIDADES DE TRANSFORMAÇÃO E RETORNO COMERCIAL",
          style_section_heading,
      )
  )
  elements.append(Spacer(1, 3))

  op_lista = (
      lead["oportunidades"]
      if isinstance(lead.get("oportunidades"), list)
      else auditoria["oportunidades"]
  )
  if not op_lista:
    op_lista = auditoria["oportunidades"]

  rows_op = []
  for op in op_lista[:3]:
    rows_op.append(
        [Paragraph(f"<font color='#16a34a'>[V] {op}</font>", style_cell_tb)]
    )

  t_op = Table(rows_op, colWidths=[540])
  t_op.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
          ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbf7d0")),
          ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dcfce7")),
          ("TOPPADDING", (0, 0), (-1, -1), 3),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
      ])
  )
  elements.append(t_op)
  elements.append(Spacer(1, 10))

  # 9. CONTAINER DE CTA REFORMULADO E DESTACADO
  zap_num = (
      lead.get("whatsapp")
      or "".join(filter(str.isdigit, lead.get("telefone", "")))
      or "16991332121"
  )
  link_wa = f"https://wa.me/55{zap_num}?text=Olá!%20Gostaria%20de%20solicitar%20a%20implantação%20do%20Tour%20Virtual%20360°%20para%20a%20{urllib.parse.quote(lead['nome'])}"

  cta_html = f"""
    <b>🚀 VAMOS TRANSFORMAR A SUA FICHA EM UM ÍMÃ DE CLIENTES?</b><br/>
    Implante o <b>Tour Virtual 360°</b> e a reestruturação profissional do perfil no Google Maps.<br/>
    <div style="margin-top: 6px;">
        <a href="{link_wa}" color="#ffffff"><b><font size="8.5">CLIQUE AQUI E FALE DIRETO NO WHATSAPP: {CONTATO_WHATSAPP}</font></b></a>
    </div>
    """
  p_cta = Paragraph(
      cta_html,
      ParagraphStyle(
          "CtaTxt",
          parent=style_normal,
          alignment=1,
          fontSize=8,
          leading=12,
          textColor=colors.HexColor("#0f172a"),
      ),
  )

  t_cta = Table([[p_cta]], colWidths=[450])
  t_cta.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f9ff")),
          ("BOX", (0, 0), (-1, -1), 1.25, colors.HexColor("#0284c7")),
          ("PADDING", (0, 0), (-1, -1), 7),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
      ])
  )
  elements.append(t_cta)

  doc.build(
      elements,
      onFirstPage=desenhar_cabecalho_rodape_diagnostico,
      onLaterPages=desenhar_cabecalho_rodape_diagnostico,
  )
  buffer.seek(0)
  return buffer

# -----------------------------------------------------------------------------
# GERADOR DE PDF DO PANORAMA DE NICHO
# -----------------------------------------------------------------------------
def gerar_pdf_panorama_nicho(nicho_nome, df_nicho):
  buffer = io.BytesIO()

  doc = SimpleDocTemplate(
      buffer,
      pagesize=letter,
      rightMargin=36,
      leftMargin=36,
      topMargin=95,
      bottomMargin=55,
      title=f"Panorama de Mercado - {nicho_nome}",
      author="Tour360VR",
  )
  styles = getSampleStyleSheet()

  main_title_style = ParagraphStyle(
      "MainTitle",
      parent=styles["Heading1"],
      fontSize=13,
      textColor=colors.HexColor("#0f172a"),
      fontName="Helvetica-Bold",
      alignment=1,
      spaceBefore=0,
      spaceAfter=8,
  )

  section_heading = ParagraphStyle(
      "SectionHeading",
      parent=styles["Heading2"],
      fontSize=9.5,
      textColor=colors.HexColor("#0f172a"),
      spaceBefore=8,
      spaceAfter=5,
      fontName="Helvetica-Bold",
      alignment=1,
  )

  body_style = ParagraphStyle(
      "BodyTextCustom",
      parent=styles["Normal"],
      fontSize=8.5,
      textColor=colors.HexColor("#334155"),
      leading=10.5,
  )
  body_center = ParagraphStyle("BodyCenter", parent=body_style, alignment=1)

  elements = []

  title_p = Paragraph(
      f"PANORAMA DE MERCADO: {nicho_nome.upper()}", main_title_style
  )
  title_table = Table([[title_p]], colWidths=[540])
  title_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
  elements.append(title_table)

  elements.append(Spacer(1, 2))
  elements.append(
      Paragraph(
          "DISTRIBUIÇÃO DE EMPRESAS POR NÍVEL DE MATURIDADE DIGITAL",
          section_heading,
      )
  )
  elements.append(Spacer(1, 2))

  df_pdf = df_nicho.copy()
  df_pdf["score_saude"] = 100 - df_pdf["score_oportunidade"]

  scores_counts = (
      df_pdf["score_saude"].value_counts().sort_index(ascending=False)
  )

  chart_draw = Drawing(540, 95)
  chart_draw.hAlign = "CENTER"
  chart_draw.add(
      Rect(
          0,
          0,
          540,
          95,
          fillColor=colors.HexColor("#f8fafc"),
          strokeColor=colors.HexColor("#cbd5e1"),
          strokeWidth=0.5,
          rx=0,
          ry=0,
      )
  )

  qtd_bars = len(scores_counts)
  if qtd_bars > 0:
    bar_w = min(40, max(18, 380 // qtd_bars))
    gap = min(22, (500 - (qtd_bars * bar_w)) // (qtd_bars + 1))
    max_val = (
        max(scores_counts.values) if max(scores_counts.values) > 0 else 1
    )
    start_x = (540 - (qtd_bars * bar_w + (qtd_bars - 1) * gap)) / 2

    for idx_sc, (score_val, total_lead) in enumerate(scores_counts.items()):
      bx = start_x + idx_sc * (bar_w + gap)
      by = 22
      bh = max((total_lead / max_val) * 52, 6)

      c_fill = (
          colors.HexColor("#4ade80")
          if score_val >= 70
          else (
              colors.HexColor("#facc15")
              if score_val >= 40
              else colors.HexColor("#f87171")
          )
      )

      chart_draw.add(
          Rect(
              bx,
              by,
              bar_w,
              bh,
              fillColor=c_fill,
              strokeColor=None,
              rx=2,
              ry=2,
          )
      )
      chart_draw.add(
          String(
              bx + (bar_w / 2),
              by + bh + 4,
              str(total_lead),
              fontSize=8.5,
              fontName="Helvetica-Bold",
              fillColor=colors.HexColor("#0f172a"),
              textAnchor="middle",
          )
      )
      chart_draw.add(
          String(
              bx + (bar_w / 2),
              by - 12,
              f"{score_val} pts",
              fontSize=7.5,
              fontName="Helvetica-Bold",
              fillColor=colors.HexColor("#475569"),
              textAnchor="middle",
          )
      )

  elements.append(chart_draw)
  elements.append(Spacer(1, 8))

  total_emp = len(df_nicho)
  sem_site = len(df_nicho[df_nicho["website"] == ""])
  nao_reiv = len(df_nicho[df_nicho["reivindicada"] == False])
  poucas_av = len(df_nicho[df_nicho["total_avaliacoes"] < 30])

  dados_resumo = [
      [
          Paragraph("<b>INDICADOR ESTRATÉGICO</b>", body_style),
          Paragraph("<b>VOLUME / %</b>", body_center),
          Paragraph("<b>DIAGNÓSTICO DE OPORTUNIDADE</b>", body_style),
      ],
      [
          Paragraph("Otimização de Avaliações", body_style),
          Paragraph(
              f"<b>{poucas_av} ({(poucas_av/total_emp*100 if total_emp>0 else 0):.1f}%)</b>",
              body_center,
          ),
          Paragraph(
              "Volume baixo (<30 avaliações) afetando a prova social e ranking.",
              body_style,
          ),
      ],
      [
          Paragraph("Sem Website Oficial", body_style),
          Paragraph(
              f"<b>{sem_site} ({(sem_site/total_emp*100 if total_emp>0 else 0):.1f}%)</b>",
              body_center,
          ),
          Paragraph(
              "Perda de tráfego direto e dependência de canais de terceiros.",
              body_style,
          ),
      ],
      [
          Paragraph("Fichas Não Reivindicadas", body_style),
          Paragraph(
              f"<b>{nao_reiv} ({(nao_reiv/total_emp*100 if total_emp>0 else 0):.1f}%)</b>",
              body_center,
          ),
          Paragraph(
              "Vulnerabilidade de segurança e falta de gestão do perfil.",
              body_style,
          ),
      ],
  ]
  t_resumo = Table(dados_resumo, colWidths=[150, 90, 300])
  t_resumo.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
          ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
          ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
          ("TOPPADDING", (0, 0), (-1, -1), 3.5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
          ("ALIGN", (1, 0), (1, -1), "CENTER"),
      ])
  )
  elements.append(t_resumo)

  elements.append(Spacer(1, 10))
  elements.append(
      Paragraph(
          "RANKING DE EMPRESAS AUDITADAS NO SETOR (DA MAIS COMPLETA À MAIS FRACA)",
          section_heading,
      )
  )
  elements.append(Spacer(1, 4))

  df_pdf_sorted = df_pdf.sort_values(by="score_oportunidade", ascending=True)

  t_data = [[
      Paragraph("<b>EMPRESA</b>", body_style),
      Paragraph("<b>NOTA</b>", body_center),
      Paragraph("<b>AVALIAÇÕES</b>", body_center),
      Paragraph("<b>SITE</b>", body_center),
      Paragraph("<b>SAÚDE DIGITAL</b>", body_center),
  ]]

  t_styles = [
      ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f8fafc")),
      ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
      ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
      ("TOPPADDING", (0, 0), (-1, -1), 3),
      ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
      ("ALIGN", (1, 0), (-1, -1), "CENTER"),
  ]

  for idx, row in enumerate(df_pdf_sorted.iterrows()):
    r_data = row[1]
    sc_saude = r_data["score_saude"]

    if sc_saude >= 70:
      bg_color = colors.HexColor("#86efac")
      txt_color = "#14532d"
    elif sc_saude >= 40:
      bg_color = colors.HexColor("#fde047")
      txt_color = "#713f12"
    else:
      bg_color = colors.HexColor("#fca5a5")
      txt_color = "#7f1d1d"

    p_score = Paragraph(
        f"<font color='{txt_color}'><b>{sc_saude}/100</b></font>", body_center
    )

    row_idx = idx + 1
    t_styles.append(("BACKGROUND", (4, row_idx), (4, row_idx), bg_color))

    t_data.append([
        Paragraph(str(r_data["nome"])[:45], body_style),
        Paragraph(str(r_data["nota"]), body_center),
        Paragraph(str(r_data["total_avaliacoes"]), body_center),
        Paragraph("Sim" if r_data["website"] else "Não", body_center),
        p_score,
    ])

  t_empresas = Table(t_data, colWidths=[270, 50, 80, 50, 90], repeatRows=1)
  t_empresas.setStyle(TableStyle(t_styles))
  elements.append(t_empresas)

  doc.build(
      elements,
      onFirstPage=desenhar_cabecalho_rodape_diagnostico,
      onLaterPages=desenhar_cabecalho_rodape_diagnostico,
  )
  buffer.seek(0)
  return buffer

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA
# -----------------------------------------------------------------------------
st.markdown(
    """
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

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.8rem !important;
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
    .score-high { background-color: #450a0a; color: #fca5a5; border: 1px solid #991b1b; }
    .score-med  { background-color: #451a03; color: #fde047; border: 1px solid #92400e; }
    .score-low  { background-color: #052e16; color: #86efac; border: 1px solid #166534; }

    .critical-item { color: #f87171; font-size: 13px; margin-bottom: 6px; font-weight: 500; }
    
    .sidebar-title {
        text-align: center; font-size: 15px; font-weight: 800; color: #ffffff;
        margin-top: -5px; margin-bottom: 4px; letter-spacing: 0.5px;
    }

    .stButton>button, .btn-redirect {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        margin-bottom: 4px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 4px rgba(255, 255, 255, 0.2) !important;
    }
    
    .stButton>button:hover, .btn-redirect:hover {
        border-color: #ffffff !important;
        box-shadow: 0 0 12px rgba(255, 255, 255, 0.9) !important;
        background-color: #1e293b !important;
    }

    button[data-testid="stBaseButton-primary"] {
        background-color: #1e293b !important;
        border-color: #ffffff !important;
        box-shadow: 0 0 12px rgba(255, 255, 255, 0.9) !important;
        color: #ffffff !important;
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
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# SESSION STATE E CONTROLE DE ETAPAS
# -----------------------------------------------------------------------------
if "etapa" not in st.session_state:
  st.session_state.etapa = 1

def mudar_etapa(nova_etapa):
  st.session_state.etapa = nova_etapa
  st.rerun()

# -----------------------------------------------------------------------------
# BUSCA REAL GOOGLE PLACES API (VARREDURA REGIONAL DINÂMICA COM LOCALIZAÇÃO EXATA)
# -----------------------------------------------------------------------------
def enriquecer_redes_sociais(nome_empresa, website):
  nome_normalizado = (
      unicodedata.normalize("NFKD", nome_empresa.lower())
      .encode("ASCII", "ignore")
      .decode("ASCII")
  )
  nome_slug = re.sub(r"[^a-zA-Z0-9]", "", nome_normalizado)

  instagram_url = f"https://instagram.com/{nome_slug}"
  facebook_url = f"https://facebook.com/{nome_slug}"

  if website and "http" in website:
    dominio = (
        website.replace("https://", "")
        .replace("http://", "")
        .replace("www.", "")
        .split("/")[0]
    )
    nome_slug_dom = re.sub(r"[^a-zA-Z0-9]", "", dominio.split(".")[0])
    if len(nome_slug_dom) > 2:
      instagram_url = f"https://instagram.com/{nome_slug_dom}"

  return instagram_url, facebook_url

def obter_lat_lng_cidade(cidade_nome, api_key):
  """Obtém as coordenadas centrais dinâmicas de qualquer cidade digitada."""
  try:
    url_geo = f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(cidade_nome + ', Brasil')}&key={api_key}"
    resp = requests.get(url_geo, timeout=5).json()
    if resp.get("status") == "OK":
      loc = resp["results"][0]["geometry"]["location"]
      return loc["lat"], loc["lng"]
  except Exception:
    pass
  return -21.1775, -47.8103

def buscar_google_places_api(
    nome_empresa, nicho, cidade, bairro, rua, raio_km, api_key, limite=70
):
  cidade_str = cidade.strip() if cidade else "Ribeirão Preto"
  bairro_str = bairro.strip() if bairro else ""

  # 1. Obter coordenada central DINÂMICA da cidade informada
  lat_centro, lng_centro = obter_lat_lng_cidade(cidade_str, api_key)

  termos_base = []
  if nome_empresa:
    termos_base.append(re.sub(r"[´`\'\"]", "", nome_empresa.strip()))
  if nicho:
    termos_base.append(nicho.strip())
  if rua:
    termos_base.append(rua.strip())

  query_principal = " ".join(termos_base) if termos_base else (nicho or "Comércio")
  raio_metros = int(raio_km * 1000)

  # 2. Varredura regional por cidades
  queries_para_executar = []

  if bairro_str:
    queries_para_executar.append(f"{query_principal} {bairro_str} {cidade_str}")
  else:
    queries_para_executar.extend([
        f"{query_principal} {cidade_str}",
        f"{query_principal} Centro {cidade_str}",
        f"{query_principal} Zona Sul {cidade_str}",
        f"{query_principal} Zona Norte {cidade_str}",
        f"{query_principal} Zona Leste {cidade_str}",
        f"{query_principal} Zona Oeste {cidade_str}",
    ])

  leads = []
  seen_place_ids = set()

  try:
    for q_str in queries_para_executar:
      if len(leads) >= limite:
        break

      url_requisicao = (
          "https://maps.googleapis.com/maps/api/place/textsearch/json?"
          f"query={urllib.parse.quote(q_str)}"
          f"&location={lat_centro},{lng_centro}"
          f"&radius={raio_metros}"
          f"&language=pt-BR&key={api_key}"
      )

      response = requests.get(url_requisicao, timeout=10)
      data = response.json()

      if data.get("status") != "OK":
        continue

      results = data.get("results", [])
      for place in results:
        if len(leads) >= limite:
          break

        place_id = place.get("place_id")
        if not place_id or place_id in seen_place_ids:
          continue
        seen_place_ids.add(place_id)

        lat = (
            place.get("geometry", {})
            .get("location", {})
            .get("lat", lat_centro)
        )
        lng = (
            place.get("geometry", {})
            .get("location", {})
            .get("lng", lng_centro)
        )

        det_res = {}
        if place_id:
          try:
            details_url = (
                "https://maps.googleapis.com/maps/api/place/details/json?"
                f"place_id={place_id}"
                "&fields=name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos"
                f"&language=pt-BR&key={api_key}"
            )
            det_res = (
                requests.get(details_url, timeout=4).json().get("result", {})
            )
          except Exception:
            det_res = {}

        nome = det_res.get("name") or place.get("name")
        endereco = det_res.get("formatted_address") or place.get(
            "formatted_address"
        )
        telefone = det_res.get("formatted_phone_number", "")
        website = det_res.get("website", "")
        nota = det_res.get("rating", place.get("rating", 0.0))
        total_avaliacoes = det_res.get(
            "user_ratings_total", place.get("user_ratings_total", 0)
        )
        photos = det_res.get("photos", place.get("photos", [])) or []

        foto_url = ""
        if photos and photos[0].get("photo_reference"):
          foto_url = (
              "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&"
              f"photo_reference={photos[0].get('photo_reference')}&key={api_key}"
          )

        has_https = website.startswith("https://") if website else False

        auditoria = calcular_score_e_auditoria(
            fotos_total=len(photos),
            tour_360=False,
            website=website,
            total_avaliacoes=total_avaliacoes,
            nota=nota,
            has_https=has_https,
        )

        clean_phone = "".join(filter(str.isdigit, telefone))
        if len(clean_phone) > 10 and clean_phone.startswith("55"):
          clean_phone = clean_phone[2:]

        instagram_url, facebook_url = enriquecer_redes_sociais(nome, website)

        lead_obj = {
            "data_minacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "cidade_busca": cidade_str,
            "bairro_busca": bairro_str or "Varredura Geral",
            "nome": nome,
            "categoria": (nicho or "Comércio").capitalize(),
            "endereco": endereco,
            "latitude": lat,
            "longitude": lng,
            "telefone": telefone or "(16) Contato via Ficha",
            "whatsapp": (
                clean_phone if len(clean_phone) >= 10 else "16999999999"
            ),
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
            "pontos_criticos": auditoria["pontos_criticos"],
            "oportunidades": auditoria["oportunidades"],
            "score_oportunidade": auditoria["score_oportunidade"],
            "anotacoes": "",
            "favorito": False,
            "data_followup": str(date.today()),
            "obs_followup": "",
        }

        salvar_lead_db(lead_obj)
        leads.append(lead_obj)

    return leads
  except Exception as e:
    st.error(f"Erro na requisição à API do Google Places: {str(e)}")
  return None

def minerar_e_auditar_negocios(
    nome_empresa, nicho, cidade, bairro, rua, raio_km, limite=70
):
  api_key = st.secrets.get("GOOGLE_API_KEY", None) or os.getenv(
      "GOOGLE_API_KEY", None
  )

  if api_key:
    api_key_limpa = api_key.strip().replace('"', "").replace("'", "")
    leads_reais = buscar_google_places_api(
        nome_empresa,
        nicho,
        cidade,
        bairro,
        rua,
        raio_km,
        api_key_limpa,
        limite,
    )
    if leads_reais and len(leads_reais) > 0:
      return leads_reais
  else:
    st.error(
        "⚠️ A chave 'GOOGLE_API_KEY' não foi encontrada nos Secrets do Streamlit"
        " Cloud."
    )
  return []

# -----------------------------------------------------------------------------
# GERADOR DE CSV EXCEL FORMATADO
# -----------------------------------------------------------------------------
def gerar_csv_excel_formatado(dados_leads):
  output = io.StringIO()
  output.write("\ufeff")
  writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
  writer.writerow([
      "ID",
      "Data Mineração",
      "Cidade Busca",
      "Bairro Busca",
      "Nome da Empresa",
      "Categoria / Nicho",
      "Status Comercial CRM",
      "Favorito?",
      "Data Follow-up",
      "Endereço Completo",
      "Telefone Fixo",
      "WhatsApp",
      "Possui Website?",
      "Website URL",
      "Site Seguro (HTTPS)?",
      "Instagram URL",
      "Facebook URL",
      "Nota Média Google",
      "Total Avaliações",
      "Ficha Reivindicada?",
      "Qtd. Fotos Publicadas",
      "Dias Desde Última Foto",
      "Possui Tour 360°?",
      "Anotações CRM",
      "Pontos Críticos Identificados",
      "Score de Oportunidade",
  ])

  for row in dados_leads:
    criticos_str = (
        " | ".join(row.get("pontos_criticos", []))
        if isinstance(row.get("pontos_criticos"), list)
        else str(row.get("pontos_criticos", ""))
    )

    anotacoes_brutas = row.get("anotacoes", "") or ""
    anotacoes_limpas = " ".join(anotacoes_brutas.splitlines())

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
        str(row.get("nota", "")).replace(".", ","),
        row.get("total_avaliacoes", ""),
        "Sim" if row.get("reivindicada") else "Não",
        row.get("fotos_total", ""),
        row.get("ultima_foto_dias", ""),
        "Sim" if row.get("tour_360") else "Não",
        anotacoes_limpas,
        criticos_str,
        row.get("score_oportunidade", ""),
    ])

  return output.getvalue().encode("utf-8")

# -----------------------------------------------------------------------------
# BARRA LATERAL
# -----------------------------------------------------------------------------
base_leads = carregar_todos_leads_db()

hoje_str = str(date.today())
pendentes_hoje = []
for l in base_leads:
  dt_fu = l.get("data_followup")
  if not dt_fu:
    dt_fu = hoje_str

  st_crm = l.get("status_crm", "")
  if dt_fu <= hoje_str and st_crm not in [
      "🤝 Cliente Fechado",
      "❌ Recusado",
  ]:
    pendentes_hoje.append(l)

with st.sidebar:
  st.markdown(
      '<div class="sidebar-title">Radar Comercial</div>',
      unsafe_allow_html=True,
  )

  if path_logo_png and os.path.exists(path_logo_png):
    c1, c2, c3 = st.columns([1.74, 2.52, 1.74])
    with c2:
      st.image(path_logo_png, use_container_width=True)

  if os.path.exists("logo_okamoto.png"):
    c1, c2, c3 = st.columns([0.8, 4.4, 0.8])
    with c2:
      st.image("logo_okamoto.png", use_container_width=True)

  st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

  if len(pendentes_hoje) > 0:
    st.markdown(
        f"""
            <div style="background-color: #7f1d1d; border: 1px solid #991b1b; padding: 10px; border-radius: 8px; margin-bottom: 12px; text-align: center;">
                <span style="color: #fca5a5; font-weight: bold; font-size: 13px;">🔔 Notificação Ativa</span><br/>
                <span style="color: #ffffff; font-size: 12px;"><b>{len(pendentes_hoje)} retornos pendentes</b> para hoje ou atrasados!</span>
            </div>
        """,
        unsafe_allow_html=True,
    )
  else:
    st.markdown(
        """
            <div style="background-color: #064e3b; border: 1px solid #065f46; padding: 8px; border-radius: 8px; margin-bottom: 12px; text-align: center;">
                <span style="color: #6ee7b7; font-weight: bold; font-size: 12px;">✅ Agenda em dia! Sem pendências.</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown(
      "<div style='text-align: center; font-weight: 700; font-size: 14px;"
      " margin-top: 8px; margin-bottom: 10px;'>📌 Módulos</div>",
      unsafe_allow_html=True,
  )

  if st.button(
      "📊 Dashboard Executivo",
      use_container_width=True,
      type="primary" if st.session_state.etapa == 1 else "secondary",
  ):
    mudar_etapa(1)
  if st.button(
      "🔍 Buscador de Clientes",
      use_container_width=True,
      type="primary" if st.session_state.etapa == 2 else "secondary",
  ):
    mudar_etapa(2)
  if st.button(
      "📋 Base & CRM de Leads",
      use_container_width=True,
      type="primary" if st.session_state.etapa == 3 else "secondary",
  ):
    mudar_etapa(3)
  if st.button(
      "📈 Panorama de Nicho",
      use_container_width=True,
      type="primary" if st.session_state.etapa == 4 else "secondary",
  ):
    mudar_etapa(4)
  if st.button(
      "🗺️ Mapa & Rota de Visitas",
      use_container_width=True,
      type="primary" if st.session_state.etapa == 5 else "secondary",
  ):
    mudar_etapa(5)
  if st.button(
      "🚀 Radar Prospecção",
      use_container_width=True,
      type="primary" if st.session_state.etapa == 6 else "secondary",
  ):
    mudar_etapa(6)

  st.markdown(
      "<div style='border-top: 1px solid #334155; margin: 14px 0 10px 0;'></div>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<div style='text-align: center; font-size: 12px; margin-bottom: 8px;'>☁️"
      f" Supabase Nuvem:<br/><b>{len(base_leads)} leads salvos</b></div>",
      unsafe_allow_html=True,
  )

  if len(base_leads) > 0:
    if st.button("🗑️ Limpar Banco de Dados", use_container_width=True):
      limpar_banco_dados()
      mudar_etapa(1)

# -----------------------------------------------------------------------------
# MÓDULO 1: DASHBOARD EXECUTIVO
# -----------------------------------------------------------------------------
if st.session_state.etapa == 1:
  st.markdown(
      """
        <div class="main-header">
            <h1 class="main-title">📈 Dashboard Executivo | Tour360VR</h1>
            <div class="main-subtitle">Visão geral do seu funil de prospecção e oportunidades de mercado mapeadas.</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  if len(base_leads) == 0:
    st.warning(
        "⚠️ Nenhum lead cadastrado ainda no banco de dados. Vá até o Buscador"
        " de Clientes para realizar sua primeira busca!"
    )
  else:
    df_dash = pd.DataFrame(base_leads)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
      st.metric("Total de Leads na Base", len(df_dash))
    with col_m2:
      favoritos_tot = len(df_dash[df_dash["favorito"] == True])
      st.metric("⭐ Leads Favoritos / Quentes", favoritos_tot)
    with col_m3:
      fechados = len(df_dash[df_dash["status_crm"] == "🤝 Cliente Fechado"])
      st.metric("🤝 Clientes Fechados", fechados)
    with col_m4:
      sem_site_tot = len(df_dash[df_dash["website"] == ""])
      st.metric(
          "🌐 Sem Website Oficial", f"{(sem_site_tot / len(df_dash) * 100):.1f}%"
      )

    st.divider()

    col_c1, col_c2 = st.columns(2)
    with col_c1:
      st.markdown("### 📊 Distribuição por Status no CRM")
      status_counts = df_dash["status_crm"].value_counts()
      st.bar_chart(status_counts)

    with col_c2:
      st.markdown("### 🏷️ Nichos / Categorias Mapeadas")
      nicho_counts = df_dash["categoria"].value_counts().head(8)
      st.bar_chart(nicho_counts)

    st.divider()
    st.markdown("### 🚨 Leads com Follow-up para Hoje ou Atrasados:")
    if len(pendentes_hoje) > 0:
      st.markdown(
          f"Você possui **{len(pendentes_hoje)} leads** pendentes de retorno na"
          " agenda:"
      )
      for r_lead in pendentes_hoje[:5]:
        st.markdown(
            f"- **{r_lead['nome']}** ({r_lead['cidade_busca']}) — Status:"
            f" `{r_lead['status_crm']}` — Retorno agendado para:"
            f" **{r_lead['data_followup']}**"
        )
    else:
      st.success(
          "🎉 Nenhum follow-up pendente para hoje! Sua agenda está em dia."
      )

# -----------------------------------------------------------------------------
# MÓDULO 2: BUSCADOR DE CLIENTES & CADASTRO MANUAL
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 2:
  st.markdown(
      """
        <div class="main-header">
            <h1 class="main-title">🔎 Radar e Mineração de Mercado Local</h1>
            <div class="main-subtitle">Varredura automática no Google Maps ou Cadastro Manual de empresas de rua e indicações.</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  tab_busca, tab_manual = st.tabs([
      "🚀 Varredura Automática (Google Maps)",
      "✍️ Cadastro Manual de Lead",
  ])

  with tab_busca:
    with st.form("form_busca"):
      col_nome_emp, col1, col2, col3, col4, col5, col6 = st.columns(
          [2.2, 2, 2, 1.8, 1.8, 1.2, 1.2]
      )
      with col_nome_emp:
        nome_empresa_input = st.text_input(
            "Nome da Empresa (Opcional)",
            value="",
            help="Ex: Clínica Sorria ou Hotel X",
        )
      with col1:
        nicho_input = st.text_input(
            "Nicho / Categoria (Opcional)",
            value="",
            help="Deixe em branco para buscar empresas gerais no local",
        )
      with col2:
        cidade_input = st.text_input("Cidade / Município", value="Ribeirão Preto")
      with col3:
        rua_input = st.text_input(
            "Rua / Avenida (Opcional)", value="", help="Ex: Av. Independência"
        )
      with col4:
        bairro_input = st.text_input(
            "Bairro / Região (Opcional)",
            value="",
            help="Deixe em branco para amplitude de busca na cidade",
        )
      with col5:
        raio_input = st.number_input(
            "Raio (km)",
            min_value=1,
            max_value=50,
            value=10,
            step=1,
            help="Distância máxima de busca a partir do centro da localidade",
        )
      with col6:
        limite_input = st.number_input(
            "Qtd. Máxima", min_value=20, max_value=70, value=70, step=5
        )

      btn_minar = st.form_submit_button(
          "🚀 Iniciar Varredura Profunda", use_container_width=True
      )

    if btn_minar:
      with st.spinner(
          f"Varrendo Google Maps num raio de {raio_input} km e salvando na"
          " nuvem..."
      ):
        time.sleep(1)
        novos = minerar_e_auditar_negocios(
            nome_empresa_input,
            nicho_input,
            cidade_input,
            bairro_input,
            rua_input,
            raio_input,
            limite_input,
        )
        if novos and len(novos) > 0:
          mudar_etapa(3)

  with tab_manual:
    st.markdown("### Inserir Empresa Manualmente no CRM")
    st.caption(
        "Use esta opção para adicionar leads de rua, indicações ou empresas"
        " que não vieram na busca automática."
    )

    tags_existentes_cad = (
        sorted(
            list(
                set(
                    [l.get("categoria", "Comércio") for l in base_leads]
                )
            )
        )
        if base_leads
        else ["Comércio", "Vestuário", "Saúde", "Alimentação"]
    )
    opcoes_tag_cad = tags_existentes_cad + ["➕ Digitar Nova Categoria..."]

    man_nome = st.text_input("Nome da Empresa *", key="input_man_nome")
    escolha_cat_manual = st.selectbox(
        "Categoria / Tag / Nicho *",
        options=opcoes_tag_cad,
        key="input_escolha_cat",
    )

    man_nicho_novo = ""
    if escolha_cat_manual == "➕ Digitar Nova Categoria...":
      man_nicho_novo = st.text_input(
          "Digite a nova Categoria / Nicho *",
          placeholder="Ex: Ótica, Confeitaria, Imobiliária",
          key="input_man_nicho_novo",
      )

    m_col1, m_col2 = st.columns(2)
    with m_col1:
      man_cidade = st.text_input(
          "Cidade", value="Ribeirão Preto", key="input_man_cid"
      )
      man_endereco = st.text_input(
          "Endereço Completo *",
          value="",
          placeholder="Ex: Rua Exemplo, 100 - Centro",
          key="input_man_end",
      )
      man_tel = st.text_input(
          "Telefone / Contato",
          value="",
          placeholder="Ex: (16) 3333-4444",
          key="input_man_tel",
      )
    with m_col2:
      man_zap = st.text_input(
          "WhatsApp (apenas números com DDD)",
          value="",
          placeholder="Ex: 16999999999",
          key="input_man_zap",
      )
      man_site = st.text_input(
          "Website (Opcional)",
          value="",
          placeholder="Ex: https://www.site.com.br",
          key="input_man_site",
      )
      man_nota = st.number_input(
          "Nota Média Google (0 a 5)",
          min_value=0.0,
          max_value=5.0,
          value=5.0,
          step=0.1,
          key="input_man_nota",
      )
      man_av = st.number_input(
          "Total de Avaliações",
          min_value=0,
          max_value=5000,
          value=10,
          step=1,
          key="input_man_av",
      )

    if st.button(
        "💾 Salvar Lead Manualmente no CRM",
        use_container_width=True,
        type="primary",
    ):
      if escolha_cat_manual == "➕ Digitar Nova Categoria...":
        categoria_final = man_nicho_novo.strip()
      else:
        categoria_final = escolha_cat_manual

      if (
          not man_nome.strip()
          or not man_endereco.strip()
          or not categoria_final
      ):
        st.error(
            "⚠️ Preencha o Nome, o Endereço e a Categoria/Nicho da empresa."
        )
      else:
        with st.spinner("Geocodificando endereço exato e salvando na nuvem..."):
          lat_manual, lng_manual = obter_coordenadas_endereco(
              man_endereco.strip(), man_cidade
          )

        has_https = man_site.startswith("https://") if man_site else False

        auditoria_man = calcular_score_e_auditoria(
            fotos_total=5,
            tour_360=False,
            website=man_site.strip(),
            total_avaliacoes=man_av,
            nota=man_nota,
            has_https=has_https,
        )

        clean_zap = "".join(filter(str.isdigit, man_zap.strip()))
        instagram_url, facebook_url = enriquecer_redes_sociais(
            man_nome, man_site
        )

        lead_manual = {
            "data_minacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "cidade_busca": man_cidade,
            "bairro_busca": "Manual",
            "nome": man_nome.strip(),
            "categoria": categoria_final.capitalize(),
            "endereco": man_endereco.strip(),
            "latitude": lat_manual,
            "longitude": lng_manual,
            "telefone": (
                man_tel.strip() if man_tel else "(16) Contato via Ficha"
            ),
            "whatsapp": (
                clean_zap if len(clean_zap) >= 10 else "16999999999"
            ),
            "website": man_site.strip(),
            "website_https": has_https,
            "instagram": instagram_url,
            "facebook": facebook_url,
            "foto_url": "",
            "nota": man_nota,
            "total_avaliacoes": man_av,
            "reivindicada": True,
            "fotos_total": 5,
            "ultima_foto_dias": 30,
            "tour_360": False,
            "status_crm": "🆕 Novo Lead",
            "pontos_criticos": auditoria_man["pontos_criticos"],
            "oportunidades": auditoria_man["oportunidades"],
            "score_oportunidade": auditoria_man["score_oportunidade"],
            "anotacoes": (
                f"[{datetime.now().strftime('%d/%m/%Y %H:%M')}] Cadastrado"
                " manualmente no sistema."
            ),
            "favorito": True,
            "data_followup": str(date.today()),
            "obs_followup": "",
        }
        salvar_lead_db(lead_manual)
        st.success(f"✅ Empresa '{man_nome}' cadastrada e mapeada com sucesso!")
        time.sleep(1.5)
        mudar_etapa(3)

  if len(base_leads) > 0:
    st.divider()
    st.info(
        f"O seu banco na nuvem possui **{len(base_leads)} leads salvos"
        " permanentemente**."
    )
    if st.button("Ver Base Completa de Leads ➡️", type="secondary"):
      mudar_etapa(3)

# -----------------------------------------------------------------------------
# MÓDULO 3: BASE DE LEADS & CRM DE VENDAS
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 3:
  st.markdown(
      """
        <div class="main-header">
            <h1 class="main-title">📊 Base de Leads e Gerenciador CRM</h1>
            <div class="main-subtitle">Gerencie status, selecione tags, revalide fichas em tempo real, acompanhe a timeline de interações e exporte planilhas.</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  if len(base_leads) == 0:
    st.warning(
        "⚠️ Nenhum lead cadastrado ainda no banco de dados. Faça sua primeira"
        " busca ou cadastro manual no Buscador de Clientes!"
    )
  else:
    df_leads_crm = pd.DataFrame(base_leads)

    col_f_busca, col_f_nicho, col_f_cid, col_f_status, col_f_fav, col_export = (
        st.columns([2, 1.8, 1.8, 1.8, 1.6, 2])
    )

    with col_f_busca:
      filtro_nome_busca = st.text_input(
          "🔍 Buscar por Nome:", value="", placeholder="Ex: Nome da empresa"
      )

    with col_f_nicho:
      nichos_existentes = ["Todos os Nichos / Tags"] + list(
          df_leads_crm["categoria"].unique()
      )
      filtro_nicho = st.selectbox("Filtrar por Tag/Nicho:", nichos_existentes)

    with col_f_cid:
      cidades_existentes = ["Todas as Cidades"] + list(
          df_leads_crm["cidade_busca"].unique()
      )
      filtro_cidade = st.selectbox("Filtrar por Cidade:", cidades_existentes)

    with col_f_status:
      filtro_status = st.selectbox(
          "Status CRM:",
          [
              "Todos os Status",
              "🆕 Novo Lead",
              "💬 Em Abordagem",
              "🛠️ Diagnóstico Gerado",
              "🤝 Cliente Fechado",
              "❌ Recusado",
          ],
      )

    with col_f_fav:
      filtro_favorito = st.selectbox(
          "Filtro:", ["Todos", "⭐ Favoritos / Quentes"]
      )

    with col_export:
      st.markdown(
          "<div style='height: 28px;'></div>", unsafe_allow_html=True
      )
      csv_bytes = gerar_csv_excel_formatado(base_leads)
      st.download_button(
          label="📊 Exportar Planilha (.csv)",
          data=csv_bytes,
          file_name=(
              f"Leads Completo CRM {datetime.now().strftime('%Y%m%d_%H%M')}.csv"
          ),
          mime="text/csv",
          use_container_width=True,
      )

    st.divider()

    resultados_filtrados = base_leads
    if filtro_nome_busca.strip():
      termo_busca = filtro_nome_busca.strip().lower()
      resultados_filtrados = [
          r for r in resultados_filtrados if termo_busca in r["nome"].lower()
      ]

    if filtro_nicho != "Todos os Nichos / Tags":
      resultados_filtrados = [
          r for r in resultados_filtrados if r["categoria"] == filtro_nicho
      ]
    if filtro_cidade != "Todas as Cidades":
      resultados_filtrados = [
          r for r in resultados_filtrados if r["cidade_busca"] == filtro_cidade
      ]
    if filtro_status != "Todos os Status":
      resultados_filtrados = [
          r for r in resultados_filtrados if r["status_crm"] == filtro_status
      ]
    if filtro_favorito == "⭐ Favoritos / Quentes":
      resultados_filtrados = [
          r for r in resultados_filtrados if r.get("favorito") == True
      ]

    st.markdown(
        f"Exibindo **{len(resultados_filtrados)}** oportunidades salvas:"
    )

    tags_ja_salvas = sorted(list(df_leads_crm["categoria"].unique()))

    for lead in resultados_filtrados:
      score = lead["score_oportunidade"]
      score_class = (
          "score-high"
          if score >= 60
          else ("score-med" if score >= 30 else "score-low")
      )
      score_label = (
          "ALTA OPORTUNIDADE"
          if score >= 60
          else ("MÉDIA OPORTUNIDADE" if score >= 30 else "BAIXA OPORTUNIDADE")
      )

      is_fav = lead.get("favorito", False)
      fav_label = "⭐ Favorito" if is_fav else "☆ Favoritar"

      st.markdown(
          f"""
                <div class="lead-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                        <div>
                            <h2 style="margin: 0; color: #ffffff; font-size: 19px;">{lead['nome']}</h2>
                            <p style="margin: 3px 0 0 0; color: #94a3b8; font-size: 12.5px;">📍 {lead['endereco']} | 🏷️ <b>{lead['categoria']}</b></p>
                        </div>
                        <div class="score-box {score_class}">
                            <div style="font-size: 9.5px; font-weight: bold;">SCORE OPORTUNIDADE</div>
                            <div style="font-size: 18px; font-weight: bold;">{score} / 100</div>
                            <div style="font-size: 8.5px;">{score_label}</div>
                        </div>
                    </div>
                </div>
            """,
          unsafe_allow_html=True,
      )

      col_img, col_details1, col_details2, col_actions = st.columns(
          [2, 2.5, 2.5, 2.5]
      )

      with col_img:
        foto_lead = lead.get("foto_url", "")
        if foto_lead and foto_lead.startswith("http"):
          try:
            api_key_atual = st.secrets.get("GOOGLE_API_KEY", None) or os.getenv(
                "GOOGLE_API_KEY", ""
            )
            api_key_limpa_url = (
                api_key_atual.strip().replace('"', "").replace("'", "")
            )
            if "key=" not in foto_lead and api_key_limpa_url:
              foto_lead_auth = f"{foto_lead}&key={api_key_limpa_url}"
            else:
              foto_lead_auth = foto_lead

            resp_img = requests.get(foto_lead_auth, timeout=5)
            if resp_img.status_code == 200:
              st.image(
                  resp_img.content,
                  caption="Foto da Ficha do Google",
                  use_container_width=True,
              )
            else:
              st.info("📷 Sem foto")
          except Exception:
            st.info("📷 Sem foto")
        else:
          st.info("📷 Sem foto")

        cat_atual = lead.get("categoria", "Comércio")
        opcoes_tag_select = list(tags_ja_salvas)
        if cat_atual not in opcoes_tag_select:
          opcoes_tag_select.insert(0, cat_atual)
        opcoes_tag_select.append("➕ Digitar Nova Tag...")

        idx_tag_atual = (
            opcoes_tag_select.index(cat_atual)
            if cat_atual in opcoes_tag_select
            else 0
        )
        escolha_tag = st.selectbox(
            "Tag / Nicho:",
            options=opcoes_tag_select,
            index=idx_tag_atual,
            key=f"sel_tag_{lead['id']}",
        )

        if escolha_tag == "➕ Digitar Nova Tag...":
          nova_tag_digitada = st.text_input(
              "Nova Tag:",
              value="",
              key=f"txt_novo_tag_{lead['id']}",
              placeholder="Ex: Ótica, Vestuário",
          )
          if (
              nova_tag_digitada.strip()
              and nova_tag_digitada.strip() != cat_atual
          ):
            atualizar_categoria_db(
                lead["id"], nova_tag_digitada.strip().capitalize()
            )
            st.toast("Nova tag criada e salva!")
            st.rerun()
        elif escolha_tag != cat_atual:
          atualizar_categoria_db(lead["id"], escolha_tag)
          st.toast("Tag atualizada com sucesso!")
          st.rerun()

        if st.button(
            "🔄 Revalidar com Google Maps",
            key=f"reval_{lead['id']}",
            use_container_width=True,
        ):
          with st.spinner("Consultando dados atuais no Google Maps..."):
            revalidar_ficha_google(lead)
            st.rerun()

        pdf_bytes_ind = gerar_pdf_diagnostico_individual(lead)
        st.download_button(
            label="📄 Baixar Diagnóstico (.pdf)",
            data=pdf_bytes_ind,
            file_name=f"Diagnóstico de Presença Digital - {lead['nome'].replace(' ', ' ')}.pdf",
            mime="application/pdf",
            key=f"dl_pdf_{lead['id']}",
            use_container_width=True,
        )

      with col_details1:
        st.markdown("**📊 Indicadores no Google:**")
        st.markdown(
            f"- **Nota Média:** ⭐ {lead['nota']} ({lead['total_avaliacoes']}"
            " avaliações)"
        )
        st.markdown(
            "- **Ficha Reivindicada?**"
            f" {'✅ Sim' if lead['reivindicada'] else '❌ **NÃO REIVINDICADA**'}"
        )
        st.markdown(
            f"- **Fotos na Ficha:** {lead['fotos_total']} fotos (última há"
            f" {lead['ultima_foto_dias']} dias)"
        )
        st.markdown(
            "- **Tour 360°:**"
            f" {'✅ **Ativo**' if lead.get('tour_360') else '❌ **Ausente (Oportunidade)**'}"
        )

      with col_details2:
        st.markdown("**🚨 Pontos Críticos Identificados:**")
        criticos_lista = (
            lead["pontos_criticos"]
            if isinstance(lead["pontos_criticos"], list)
            else json.loads(lead["pontos_criticos"] or "[]")
        )
        for pc in criticos_lista:
          st.markdown(
              f"<div class='critical-item'>❌ {pc}</div>", unsafe_allow_html=True
          )

      with col_actions:
        st.markdown("**🌐 Presença Web & Mídias:**")
        st.markdown(
            f"- **Website:** {lead['website'] if lead['website'] else '❌ Sem site'}"
        )

        insta_link = lead.get("instagram", "")
        if insta_link:
          st.markdown(f"- **Instagram:** [Abrir Perfil]({insta_link})")
        else:
          st.markdown("- **Instagram:** ❌ Não informado")

        fb_link = lead.get("facebook", "")
        if fb_link:
          st.markdown(f"- **Facebook:** [Abrir Página]({fb_link})")
        else:
          st.markdown("- **Facebook:** ❌ Não informado")

        st.markdown(
            "- **Maps:** [Ver no Google"
            " Maps](https://www.google.com/maps/search/?api=1&query="
            f"{lead['nome'].replace(' ', '+')})"
        )

        st.markdown(
            f'<a href="{URL_SISTEMA_DIAGNOSTICO}" target="_blank"'
            ' class="btn-redirect">🛠️ Abrir no Diagnóstico Tour360VR</a>',
            unsafe_allow_html=True,
        )

        if lead["whatsapp"]:
          msg_wa = (
              "Olá! Tudo bem?\nMeu nome é Rubens Okamoto, da Okamoto Mídias"
              f" Visuais e do Tour360VR.\nEstava analisando a presença da"
              f" {lead['nome']} no Google, e identifiquei pontos estratégicos"
              " onde a visibilidade de vocês pode ser ampliada em relação aos"
              " concorrentes.\nMontei um relatório rápido de diagnóstico em PDF."
              " Posso te enviar por aqui?"
          )
          link_wa = (
              f"https://wa.me/55{lead['whatsapp']}?text={urllib.parse.quote(msg_wa)}"
          )
          st.markdown(
              f'<a href="{link_wa}" target="_blank"><button'
              ' style="width:100%; background-color:#25D366; color:white;'
              " border:none; padding:8px; border-radius:6px; font-weight:bold;"
              ' cursor:pointer; margin-bottom:8px;">💬 WhatsApp</button></a>',
              unsafe_allow_html=True,
          )

        assunto_email = (
            f"Oportunidade de Presença Digital: {lead['nome']} no Google"
        )
        corpo_email = f"""Olá! Analisei o perfil da {lead['nome']} no Google e gostaria de compartilhar uma oportunidade importante.

Identifiquei pontos críticos que estão impactando a confiança de novos clientes no setor de {lead['categoria']}:
1. Ausência de Tour Virtual 360° navegável.
​2. Perfil estático com fotos e informações defasadas.
3. Falta de otimização de presença digital.

Temos soluções para transformar a vitrine do seu negócio no Google. Fico à disposição para conversarmos!

Atenciosamente,
Rubens Okamoto
TOUR360VR | Okamoto Mídias Visuais
(16) 99133-2121 | tour360vr.com.br"""

        link_mailto = f"mailto:?subject={urllib.parse.quote(assunto_email)}&body={urllib.parse.quote(corpo_email)}"
        st.markdown(
            f'<a href="{link_mailto}" target="_blank"><button'
            ' style="width:100%; background-color:#0284c7; color:white;'
            " border:none; padding:8px; border-radius:6px; font-weight:bold;"
            ' cursor:pointer; margin-bottom:8px;">✉️ Enviar E-mail'
            " Pronto</button></a>",
            unsafe_allow_html=True,
        )

      st.markdown(
          "<div style='border-top: 1px solid #334155; margin: 12px 0;'></div>",
          unsafe_allow_html=True,
      )
      bar_col1, bar_col2, bar_col3 = st.columns([1.5, 3, 2.5])

      with bar_col1:
        st.markdown(
            "<div style='height: 28px;'></div>", unsafe_allow_html=True
        )
        if st.button(
            fav_label, key=f"fav_btn_{lead['id']}", use_container_width=True
        ):
          alternar_favorito_db(lead["id"], is_fav)
          st.rerun()

      status_opcoes = [
          "🆕 Novo Lead",
          "💬 Em Abordagem",
          "🛠️ Diagnóstico Gerado",
          "🤝 Cliente Fechado",
          "❌ Recusado",
      ]
      idx_atual = (
          status_opcoes.index(lead["status_crm"])
          if lead["status_crm"] in status_opcoes
          else 0
      )

      with bar_col2:
        novo_st = st.selectbox(
            "Status Comercial:",
            status_opcoes,
            index=idx_atual,
            key=f"crm_st_{lead['id']}",
        )
        if novo_st != lead["status_crm"]:
          atualizar_status_crm(lead["id"], novo_st)
          st.toast("Status atualizado na nuvem!")
          st.rerun()

      dt_atual_str = lead.get("data_followup", str(date.today()))
      try:
        dt_obj = datetime.strptime(dt_atual_str, "%Y-%m-%d").date()
      except Exception:
        dt_obj = date.today()

      with bar_col3:
        nova_data_fu = st.date_input(
            "Próximo Contato (Follow-up):",
            value=dt_obj,
            key=f"dt_fu_{lead['id']}",
        )
        if str(nova_data_fu) != dt_atual_str:
          atualizar_followup_db(lead["id"], nova_data_fu)
          st.toast("Data de follow-up atualizada!")

      with st.expander(
          "✏️ **Editar Dados Cadastrais (Nome, Endereço, Telefone, Site,"
          " Instagram)**"
      ):
        with st.form(key=f"form_edit_lead_{lead['id']}"):
          edit_nome = st.text_input(
              "Nome da Empresa", value=lead.get("nome", "")
          )
          edit_end = st.text_input(
              "Endereço Completo", value=lead.get("endereco", "")
          )
          edit_tel = st.text_input(
              "Telefone / Contato", value=lead.get("telefone", "")
          )
          edit_site = st.text_input(
              "Website URL", value=lead.get("website", "")
          )
          edit_insta = st.text_input(
              "Instagram URL", value=lead.get("instagram", "")
          )

          btn_salvar_edit = st.form_submit_button(
              "💾 Salvar Alterações Cadastrais", use_container_width=True
          )

          if btn_salvar_edit:
            novos_dados = {
                "nome": edit_nome.strip(),
                "endereco": edit_end.strip(),
                "telefone": edit_tel.strip(),
                "website": edit_site.strip(),
                "instagram": edit_insta.strip(),
            }

            if edit_end.strip() != lead.get("endereco", ""):
              with st.spinner("Recalculando coordenadas do novo endereço..."):
                lat_novo, lng_novo = obter_coordenadas_endereco(
                    edit_end.strip(),
                    lead.get("cidade_busca", "Ribeirão Preto"),
                )
                novos_dados["latitude"] = lat_novo
                novos_dados["longitude"] = lng_novo

            atualizar_dados_cadastrais_db(lead["id"], novos_dados)
            st.success("✅ Dados atualizados com sucesso!")
            time.sleep(1)
            st.rerun()

      st.markdown(
          "**📱 Histórico e Timeline de Interações (Log de Atividades):**"
      )
      anotacoes_atuais = lead.get("anotacoes", "") or ""

      with st.form(key=f"form_timeline_{lead['id']}"):
        nova_interacao = st.text_input(
            "Adicionar nova interação / log:",
            placeholder=(
                "Ex: Ligou, enviou proposta, marcou reunião para terça..."
            ),
        )
        col_btn_tl1, col_btn_tl2 = st.columns([2, 4])
        with col_btn_tl1:
          btn_add_tl = st.form_submit_button(
              "➕ Registrar na Timeline", use_container_width=True
          )

        if btn_add_tl and nova_interacao.strip():
          data_hora_agora = datetime.now().strftime("%d/%m/%Y %H:%M")
          registro_formatado = (
              f"[{data_hora_agora}] {nova_interacao.strip()}"
          )
          historico_atualizado = (
              f"{registro_formatado}\n{anotacoes_atuais}"
              if anotacoes_atuais
              else registro_formatado
          )
          atualizar_anotacoes_db(lead["id"], historico_atualizado)
          st.success("Interação registrada na timeline!")
          time.sleep(0.5)
          st.rerun()

      if anotacoes_atuais:
        st.markdown(
            '<div class="script-box" style="max-height: 150px; overflow-y:'
            f' auto;">{anotacoes_atuais}</div>',
            unsafe_allow_html=True,
        )
      else:
        st.caption("Nenhum histórico registrado ainda.")

      with st.expander(
          f"✉️ **Scripts de Vendas e Abordagem Detalhada ({lead['nome']})**"
      ):
        st.markdown("**1) Abordagem Inicial — WhatsApp**")
        script_wa = (
            "Olá! Tudo bem?\nMeu nome é Rubens Okamoto, da Okamoto Mídias"
            f" Visuais e do Tour360VR.\nEstava analisando a presença da"
            f" {lead['nome']} no Google, e identifiquei pontos estratégicos"
            " onde a visibilidade de vocês pode ser ampliada em relação aos"
            " concorrentes.\nMontei um relatório rápido de diagnóstico em PDF."
            " Posso te enviar por aqui?"
        )
        st.markdown(
            f'<div class="script-box">{script_wa}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**2) Abordagem Inicial — E-mail**")
        script_email = f"""Assunto: Oportunidade de Presença Digital: {lead['nome']} no Google

Olá! Analisei o perfil da {lead['nome']} no Google e gostaria de compartilhar uma oportunidade importante.

Identifiquei pontos críticos que estão impactando a confiança de novos clientes:
1. Ausência de Tour Virtual 360° navegável (seus concorrentes levam vantagem visual).
​2. Perfil estático com fotos e informações desatualizadas.
3. Falta de otimização de palavras-chave para o setor de {lead['categoria']}.

Temos soluções para transformar a vitrine do seu negócio no Google. Anexo um diagnóstico em PDF com a análise detalhada.

Fico à disposição para conversarmos!

Atenciosamente,

Rubens Okamoto
TOUR360VR | Okamoto Mídias Visuais
(16) 99133-2121 | tour360vr.com.br"""
        st.markdown(
            f'<div class="script-box">{script_email}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("**3) Follow-up 48h — Pós-Envio do Diagnóstico**")
        script_follow = (
            "Olá! Só checando por aqui — conseguiu analisar o diagnóstico em PDF"
            f" da {lead['nome']} que te enviei? Fico no aguardo para tirar"
            " qualquer dúvida!"
        )
        st.markdown(
            f'<div class="script-box">{script_follow}</div>',
            unsafe_allow_html=True,
        )

      st.divider()

# -----------------------------------------------------------------------------
# MÓDULO 4: PANORAMA DE NICHO
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 4:
  st.markdown(
      """
        <div class="main-header">
            <h1 class="main-title">📈 Panorama de Mercado & Inteligência de Nicho</h1>
            <div class="main-subtitle">Análise detalhada por categoria e município ordenada por maior oportunidade comercial.</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  if len(base_leads) == 0:
    st.warning(
        "⚠️ Nenhum lead cadastrado ainda no banco de dados. Faça sua primeira"
        " busca no Buscador de Clientes!"
    )
  else:
    df_leads = pd.DataFrame(base_leads)

    categorias_disponiveis = ["Todos os Nichos Mapeados"] + list(
        df_leads["categoria"].unique()
    )
    cidades_disponiveis = ["Todas as Cidades"] + list(
        df_leads["cidade_busca"].unique()
    )

    col_sel_nicho, col_sel_cid, col_btn_pdf = st.columns([2.5, 2.5, 2])

    with col_sel_nicho:
      nicho_selecionado = st.selectbox(
          "🎯 Nicho Comercial / Tag:", categorias_disponiveis
      )

    with col_sel_cid:
      cidade_selecionada = st.selectbox(
          "📍 Cidade / Município:", cidades_disponiveis
      )

    df_filtrado = df_leads.copy()
    if nicho_selecionado != "Todos os Nichos Mapeados":
      df_filtrado = df_filtrado[
          df_filtrado["categoria"] == nicho_selecionado
      ]
    if cidade_selecionada != "Todas as Cidades":
      df_filtrado = df_filtrado[
          df_filtrado["cidade_busca"] == cidade_selecionada
      ]

    df_filtrado_sorted = df_filtrado.sort_values(
        by="score_oportunidade", ascending=False
    )

    data_hoje_str = datetime.now().strftime("%d-%m-%Y")
    nicho_limpo = nicho_selecionado.replace(":", "").replace("/", " ")
    nome_arquivo_pdf = (
        f"Panorama de Mercado - {nicho_limpo} - {data_hoje_str}.pdf"
    )

    with col_btn_pdf:
      st.markdown(
          "<div style='height: 28px;'></div>", unsafe_allow_html=True
      )
      pdf_bytes_nicho = gerar_pdf_panorama_nicho(
          nicho_selecionado, df_filtrado
      )
      st.download_button(
          label="📄 Baixar Relatório (.pdf)",
          data=pdf_bytes_nicho,
          file_name=nome_arquivo_pdf,
          mime="application/pdf",
          use_container_width=True,
      )

    st.divider()

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    total_count = len(df_filtrado_sorted)

    with col_m1:
      st.metric("Empresas Analisadas", total_count)
    with col_m2:
      poucas_av = len(
          df_filtrado_sorted[df_filtrado_sorted["total_avaliacoes"] < 30]
      )
      st.metric(
          "Poucas Avaliações (<30)",
          f"{(poucas_av / total_count * 100 if total_count > 0 else 0):.1f}%",
          f"{poucas_av} empresas",
      )
    with col_m3:
      sem_site = len(df_filtrado_sorted[df_filtrado_sorted["website"] == ""])
      st.metric(
          "Sem Website Oficial",
          f"{(sem_site / total_count * 100 if total_count > 0 else 0):.1f}%",
          f"{sem_site} empresas",
      )
    with col_m4:
      nao_reiv = len(
          df_filtrado_sorted[df_filtrado_sorted["reivindicada"] == False]
      )
      st.metric(
          "Fichas não Reivindicadas",
          f"{(nao_reiv / total_count * 100 if total_count > 0 else 0):.1f}%",
          f"{nao_reiv} empresas",
      )

    st.divider()

    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
      st.markdown("### 📊 Nível de Oportunidade Comercial (Score)")
      st.bar_chart(df_filtrado_sorted["score_oportunidade"].value_counts())

    with c_chart2:
      st.markdown("### ⭐ Média de Avaliações no Google")
      st.bar_chart(df_filtrado_sorted["nota"].value_counts())

    st.divider()
    st.markdown(
        "### 📋 Ranking do Nicho"
        f" **{nicho_selecionado}** (Ordem de Prospecção):"
    )

    df_exibicao = pd.DataFrame({
        "EMPRESA": df_filtrado_sorted["nome"],
        "CIDADE": df_filtrado_sorted["cidade_busca"],
        "TAG / NICHO": df_filtrado_sorted["categoria"],
        "SCORE OPORTUNIDADE": df_filtrado_sorted["score_oportunidade"].apply(
            lambda x: f"{x}/100"
        ),
        "NOTA": df_filtrado_sorted["nota"].apply(lambda x: f"{x:.1f} ⭐"),
        "AVALIAÇÕES": df_filtrado_sorted["total_avaliacoes"].astype(str),
        "WEBSITE": df_filtrado_sorted["website"].apply(
            lambda x: x if x else "Sem site registrado"
        ),
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
            "TAG / NICHO": st.column_config.Column(
                "TAG / NICHO", alignment="center"
            ),
            "SCORE OPORTUNIDADE": st.column_config.Column(
                "SCORE OPORTUNIDADE", width="small", alignment="center"
            ),
            "NOTA": st.column_config.Column(
                "NOTA", width="small", alignment="center"
            ),
            "AVALIAÇÕES": st.column_config.Column(
                "AVALIAÇÕES", width="small", alignment="center"
            ),
            "WEBSITE": st.column_config.LinkColumn("WEBSITE", width="large"),
        },
    )

# -----------------------------------------------------------------------------
# MÓDULO 5: MAPA & ROTA DE VISITAS
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 5:
  st.markdown(
      """
        <div class="main-header">
            <h1 class="main-title">🗺️ Mapa & Planejador de Rotas de Visitas</h1>
            <div class="main-subtitle">Visualize leads no mapa com pins coloridos profissionais e organize seu itinerário sequencial.</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  if len(base_leads) == 0:
    st.warning(
        "⚠️ Nenhum lead cadastrado ainda no banco de dados. Faça sua primeira"
        " busca no Buscador de Clientes!"
    )
  else:
    df_mapa = pd.DataFrame(base_leads)

    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
      cats_mapa = ["Todos os Nichos / Tags"] + list(
          df_mapa["categoria"].unique()
      )
      cat_sel_mapa = st.selectbox("🎯 Nicho / Tag no Roteiro:", cats_mapa)

    with col_f2:
      cids_mapa = ["Todas as Cidades/Regiões"] + list(
          df_mapa["cidade_busca"].unique()
      )
      cid_sel_mapa = st.selectbox("📍 Cidade / Região:", cids_mapa)

    with col_f3:
      filtro_score_op = st.selectbox(
          "🎯 Faixa de Score de Oportunidade:",
          [
              "Todos os Scores",
              "🚨 Crítico (Score ≥ 60)",
              "🟡 Médio (30 a 59)",
              "🟢 Baixo (< 30)",
          ],
      )

    df_mapa_filtrado = df_mapa.copy()
    if cat_sel_mapa != "Todos os Nichos / Tags":
      df_mapa_filtrado = df_mapa_filtrado[
          df_mapa_filtrado["categoria"] == cat_sel_mapa
      ]
    if cid_sel_mapa != "Todas as Cidades/Regiões":
      df_mapa_filtrado = df_mapa_filtrado[
          df_mapa_filtrado["cidade_busca"] == cid_sel_mapa
      ]

    if filtro_score_op == "🚨 Crítico (Score ≥ 60)":
      df_mapa_filtrado = df_mapa_filtrado[
          df_mapa_filtrado["score_oportunidade"] >= 60
      ]
    elif filtro_score_op == "🟡 Médio (30 a 59)":
      df_mapa_filtrado = df_mapa_filtrado[
          (df_mapa_filtrado["score_oportunidade"] >= 30)
          & (df_mapa_filtrado["score_oportunidade"] < 60)
      ]
    elif filtro_score_op == "🟢 Baixo (< 30)":
      df_mapa_filtrado = df_mapa_filtrado[
          df_mapa_filtrado["score_oportunidade"] < 30
      ]

    st.info(
        f"📌 Exibindo **{len(df_mapa_filtrado)} empresas** no mapa e no"
        " itinerário de visitas."
    )

    CORES_PINS = [
        "red",
        "blue",
        "green",
        "purple",
        "orange",
        "darkred",
        "lightred",
        "darkblue",
        "darkgreen",
        "cadetblue",
        "darkpurple",
        "pink",
        "lightblue",
        "lightgreen",
        "gray",
        "black",
        "lightgray",
        "beige",
    ]

    CORES_HEX = {
        "red": "#ef4444",
        "blue": "#2563eb",
        "green": "#16a34a",
        "purple": "#9333ea",
        "orange": "#ea580c",
        "darkred": "#991b1b",
        "lightred": "#f87171",
        "darkblue": "#1e3a8a",
        "darkgreen": "#14532d",
        "cadetblue": "#0891b2",
        "darkpurple": "#581c87",
        "pink": "#ec4899",
        "lightblue": "#38bdf8",
        "lightgreen": "#4ade80",
        "gray": "#64748b",
        "black": "#0f172a",
        "lightgray": "#cbd5e1",
        "beige": "#d97706",
    }

    segmentos_unicos = sorted(list(df_mapa["categoria"].unique()))
    qtd_segmentos = len(segmentos_unicos)

    mapa_cores_seg = {
        seg: CORES_PINS[idx % len(CORES_PINS)]
        for idx, seg in enumerate(segmentos_unicos)
    }

    if cat_sel_mapa == "Todos os Nichos / Tags" and qtd_segmentos > 1:
      st.markdown("**🎨 Legenda de Cores por Tag / Nicho:**")

      num_cols = min(qtd_segmentos, 5)
      cols_leg = st.columns(num_cols)

      for idx, (seg, cor_nome) in enumerate(mapa_cores_seg.items()):
        hex_cor = CORES_HEX.get(cor_nome, "#ef4444")
        with cols_leg[idx % num_cols]:
          st.markdown(
              '<div style="background-color: #1e293b; padding: 6px 10px;'
              " border-radius: 8px; border: 1px solid #334155; margin-bottom:"
              ' 6px; display: flex; align-items: center; gap: 8px;">'
              f'<span style="height: 12px; width: 12px; min-width: 12px; background-color: {hex_cor}; border-radius: 50%; display: inline-block; border: 1px solid #ffffff;"></span>'
              f'<b style="color: #ffffff; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{seg}</b>'
              "</div>",
              unsafe_allow_html=True,
          )
      st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if (
        "latitude" in df_mapa_filtrado.columns
        and "longitude" in df_mapa_filtrado.columns
        and len(df_mapa_filtrado) > 0
    ):
      lat_centro = df_mapa_filtrado["latitude"].mean()
      lon_centro = df_mapa_filtrado["longitude"].mean()

      m = folium.Map(
          location=[lat_centro, lon_centro],
          zoom_start=13,
          tiles="OpenStreetMap",
      )

      bounds = []
      for _, row in df_mapa_filtrado.iterrows():
        cor_pin = mapa_cores_seg.get(row["categoria"], "red")
        hex_cor_tag = CORES_HEX.get(cor_pin, "#ef4444")

        info_card_html = f"""
                <div style="font-family: Arial, sans-serif; font-size: 12px; min-width: 240px; padding: 6px; line-height: 1.5;">
                    <b style="color: #2563eb; font-size: 14px;">{row['nome']}</b><br/>
                    <span style="color: #475569; font-size: 11px;">📍 {row['endereco']}</span><br/>
                    <hr style="margin: 6px 0; border: 0.5px solid #cbd5e1;"/>
                    🏷️ <b>Tag / Nicho:</b> <span style="color:{hex_cor_tag}; font-weight:bold;">{row['categoria']}</span><br/>
                    🚨 <b>Score Oportunidade:</b> <span style="color: #dc2626; font-weight: bold;">{row['score_oportunidade']}/100</span><br/>
                    ⭐ <b>Nota no Google:</b> {row['nota']} ({row['total_avaliacoes']} avaliações)<br/>
                </div>
                """

        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=folium.Popup(info_card_html, max_width=320),
            icon=folium.Icon(color=cor_pin, icon="info-sign"),
        ).add_to(m)

        bounds.append([row["latitude"], row["longitude"]])

      if len(bounds) > 0:
        m.fit_bounds(bounds, padding=[30, 30])

      st_folium(m, width="100%", height=500)

      st.divider()

      st.markdown(
          "### 🚗 Itinerário Sequencial de Visitas Presenciais (Prioridade"
          " Comercial)"
      )
      st.markdown(
          "Lista ordenada do maior score de oportunidade para o menor:"
      )

      df_mapa_sorted = df_mapa_filtrado.sort_values(
          by="score_oportunidade", ascending=False
      )

      for idx, (_, r_visita) in enumerate(
          df_mapa_sorted.iterrows(), start=1
      ):
        url_rota_passo_a_passo = f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(r_visita['endereco'])}"

        with st.container():
          col_num, col_info, col_acao = st.columns([0.8, 4.2, 2])
          with col_num:
            st.markdown(
                f"<div style='background-color: #1e293b; color: #38bdf8;"
                " font-size: 18px; font-weight: bold; text-align: center;"
                " padding: 12px; border-radius: 8px; border: 1px solid"
                f" #334155;'>#{idx}</div>",
                unsafe_allow_html=True,
            )
          with col_info:
            cor_nome = mapa_cores_seg.get(r_visita["categoria"], "red")
            hex_cor_tag = CORES_HEX.get(cor_nome, "#38bdf8")
            st.markdown(
                f"**{r_visita['nome']}** (Tag: <span"
                f" style='color:{hex_cor_tag}; font-weight:bold;'>{r_visita['categoria']}</span>)",
                unsafe_allow_html=True,
            )
            st.markdown(f"📍 {r_visita['endereco']}")
            st.markdown(
                f"⭐ Nota: {r_visita['nota']} | 🚨 Score Oportunidade:"
                f" **{r_visita['score_oportunidade']}/100**"
            )
          with col_acao:
            st.markdown(
                "<div style='height: 4px;'></div>", unsafe_allow_html=True
            )
            st.markdown(
                f'<a href="{url_rota_passo_a_passo}" target="_blank"><button'
                ' style="width:100%; background-color:#2563eb; color:white;'
                " border:none; padding:7px; border-radius:6px; font-weight:bold;"
                ' cursor:pointer; margin-bottom:5px;">🧭 Iniciar Navegação'
                " (GPS)</button></a>",
                unsafe_allow_html=True,
            )
            if r_visita["whatsapp"]:
              link_wa_rota = (
                  f"https://wa.me/55{r_visita['whatsapp']}?text={urllib.parse.quote(f'Olá! Estou passando aqui na região e gostaria de agendar uma rápida apresentação presencial do Tour 360° para a {r_visita["nome"]}.')}"
              )
              st.markdown(
                  f'<a href="{link_wa_rota}" target="_blank"><button'
                  ' style="width:100%; background-color:#25D366; color:white;'
                  " border:none; padding:7px; border-radius:6px;"
                  ' font-weight:bold; cursor:pointer;">💬 Avisar via'
                  " WhatsApp</button></a>",
                  unsafe_allow_html=True,
              )
          st.divider()
    else:
      st.warning(
          "Nenhum registro encontrado para os filtros selecionados."
      )

# -----------------------------------------------------------------------------
# MÓDULO 6: RADAR PROSPECÇÃO (KANBAN INTERATIVO)
# -----------------------------------------------------------------------------
elif st.session_state.etapa == 6:
  st.markdown(
      """
        <div class="main-header">
            <h1 class="main-title">🚀 Radar Prospecção Pro</h1>
            <div class="main-subtitle">Funil Kanban interativo: cards compactos expansíveis para otimizar sua visualização e agilizar o dia a dia.</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  if not base_leads:
    st.info(
        "ℹ️ Nenhum lead encontrado na base. Realize uma busca no Buscador de"
        " Clientes para abastecer o funil Kanban."
    )
  else:
    col_fk1, col_fk2 = st.columns([2, 2])
    df_kanban = pd.DataFrame(base_leads)

    with col_fk1:
      tags_k = ["Todos os Nichos / Tags"] + list(
          df_kanban["categoria"].unique()
      )
      filtro_tag_k = st.selectbox("🎯 Filtrar Kanban por Nicho/Tag:", tags_k)

    with col_fk2:
      cidades_k = ["Todas as Cidades"] + list(
          df_kanban["cidade_busca"].unique()
      )
      filtro_cid_k = st.selectbox("📍 Filtrar Kanban por Cidade:", cidades_k)

    if filtro_tag_k != "Todos os Nichos / Tags":
      df_kanban = df_kanban[df_kanban["categoria"] == filtro_tag_k]
    if filtro_cid_k != "Todas as Cidades":
      df_kanban = df_kanban[df_kanban["cidade_busca"] == filtro_cid_k]

    st.divider()

    col_k1, col_k2, col_k3, col_k4 = st.columns(4)

    status_colunas = [
        ("🆕 Novo Lead", col_k1),
        ("💬 Em Abordagem", col_k2),
        ("🛠️ Em Negociação", col_k3),
        ("🤝 Cliente Fechado", col_k4),
    ]

    status_opcoes_kanban = [
        "🆕 Novo Lead",
        "💬 Em Abordagem",
        "🛠️ Diagnóstico Gerado",
        "🤝 Cliente Fechado",
        "❌ Recusado",
    ]

    for status_nome, coluna_streamlit in status_colunas:
      with coluna_streamlit:
        if status_nome == "🛠️ Em Negociação":
          leads_col = (
              df_kanban[
                  df_kanban["status_crm"].isin(
                      ["🛠️ Diagnóstico Gerado", "Em Negociação"]
                  )
              ]
              if "status_crm" in df_kanban.columns
              else pd.DataFrame()
          )
        else:
          leads_col = (
              df_kanban[df_kanban["status_crm"] == status_nome]
              if "status_crm" in df_kanban.columns
              else pd.DataFrame()
          )

        st.markdown(f"#### {status_nome} ({len(leads_col)})")
        st.markdown(
            "<div style='height: 4px;'></div>", unsafe_allow_html=True
        )

        if len(leads_col) == 0:
          st.caption("Nenhum lead nesta etapa.")
        else:
          for _, l in leads_col.iterrows():
            tem_site_bool = bool(l.get("website"))

            titulo_card = (
                f"{l.get('nome', '')} ({l.get('categoria', 'Geral')}) - ⭐"
                f" {l.get('nota', 0.0)}"
            )

            with st.expander(titulo_card, expanded=False):
              st.markdown(
                  "<span style='color: #94a3b8; font-size: 11px;'>📍"
                  f" {l.get('endereco', '')} - {l.get('cidade_busca', '')}</span>",
                  unsafe_allow_html=True,
              )
              st.markdown(
                  "<span style='color:"
                  f" {'#4ade80' if tem_site_bool else '#f87171'}; font-size:"
                  f" 11px;'>{'🌐 Possui Site' if tem_site_bool else '❌ Sem Site'}</span>"
                  " | <span style='color: #fbbf24; font-size: 11px;'>Avaliações:"
                  f" {l.get('total_avaliacoes', 0)}</span>",
                  unsafe_allow_html=True,
              )

              anotacoes_atuais = l.get("anotacoes", "") or ""
              if anotacoes_atuais:
                st.markdown(
                    "<div style='margin-top: 6px; font-size: 11px; color:"
                    " #94a3b8;'><b>📜 Histórico Recente:</b></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="script-box" style="font-size: 11px; padding:'
                    " 6px 8px; max-height: 90px; overflow-y: auto;"
                    f' margin-bottom: 6px;">{anotacoes_atuais}</div>',
                    unsafe_allow_html=True,
                )
              else:
                st.caption("Sem histórico registrado.")

              with st.form(key=f"form_kanban_tl_{l['id']}"):
                nova_interacao_k = st.text_input(
                    "Nova interação:",
                    placeholder="Ex: Ligou, enviou proposta...",
                    label_visibility="collapsed",
                    key=f"input_tl_k_{l['id']}",
                )
                btn_add_tl_k = st.form_submit_button(
                    "➕ Salvar Log", use_container_width=True
                )

                if btn_add_tl_k and nova_interacao_k.strip():
                  data_hora_agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                  registro_formatado = (
                      f"[{data_hora_agora}] {nova_interacao_k.strip()}"
                  )
                  historico_atualizado = (
                      f"{registro_formatado}\n{anotacoes_atuais}"
                      if anotacoes_atuais
                      else registro_formatado
                  )
                  atualizar_anotacoes_db(l["id"], historico_atualizado)
                  st.toast("Interação salva!")
                  st.rerun()

              st.markdown(
                  "<div style='margin-top: 4px; margin-bottom: 2px; font-size:"
                  " 11px; color: #cbd5e1;'><b>Mover Coluna:</b></div>",
                  unsafe_allow_html=True,
              )
              idx_st = (
                  status_opcoes_kanban.index(l.get("status_crm", "🆕 Novo Lead"))
                  if l.get("status_crm", "🆕 Novo Lead") in status_opcoes_kanban
                  else 0
              )
              novo_status_card = st.selectbox(
                  "Mover Coluna",
                  status_opcoes_kanban,
                  index=idx_st,
                  key=f"kanban_move_{l['id']}",
                  label_visibility="collapsed",
              )

              if novo_status_card != l.get("status_crm"):
                atualizar_status_crm(l["id"], novo_status_card)
                st.toast(f"Lead '{l.get('nome')}' movido com sucesso!")
                st.rerun()

              if l.get("whatsapp"):
                msg_k = (
                    f"Olá, {l.get('nome')}! Tudo bem? Passando para retomarmos"
                    " nosso contato..."
                )
                link_wa_k = (
                    f"https://wa.me/55{l.get('whatsapp')}?text={urllib.parse.quote(msg_k)}"
                )
                st.markdown(
                    f'<a href="{link_wa_k}" target="_blank"><button'
                    ' style="width:100%; background-color:#25D366; color:white;'
                    " border:none; padding:6px; border-radius:6px;"
                    " font-weight:bold; font-size:12px; cursor:pointer;"
                    ' margin-top:6px;">💬 WhatsApp</button></a>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<div style='height: 4px;'></div>", unsafe_allow_html=True
            )

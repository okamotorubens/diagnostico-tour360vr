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
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph

from design.theme import inject_theme
from design.components import (
    aplicar_extras, render_hero, section_title, glass_container,
    badge_score, botao_whatsapp, link_secundario, classificar_score, PALETA,
)
from design.auth import exigir_login, barra_usuario
from design.pdf import cabecalho, rodape, tabela_padrao, grafico_barras, margens

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================
LOGO_TOUR = "logo_tour_transparente.png"
LOGO_OKAMOTO = "logo_okamoto.png"
URL_SISTEMA_DIAGNOSTICO = "https://tour360vr.streamlit.app/"
MAX_LEADS = 60
PONTOS_MAXIMOS_API = 75      # soma dos pesos dos critérios verificáveis pela API
PAUSA_PAGINACAO = 2          # a Places API exige alguns segundos antes do next_page_token

page_icon = PILImage.open(LOGO_TOUR) if os.path.exists(LOGO_TOUR) else "🔍"
st.set_page_config(
    page_title="Radar Comercial | Tour360VR",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()
aplicar_extras()

# Login compartilhado com a Gestão (mesmo projeto Supabase)
exigir_login("Acesso restrito ao Radar Comercial", "usuario_radar")
barra_usuario("usuario_radar")

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
# UTILITÁRIOS
# =============================================================================
def b64_arquivo(caminho):
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def hero_radar(titulo, subtitulo):
    render_hero(b64_arquivo(LOGO_TOUR), titulo, subtitulo)


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
        return supabase.table("leads").select("*").order("id", desc=True).execute().data or []
    except Exception as e:
        st.error(f"Erro ao carregar leads: {e}")
        return []


def carregar_leads_instagram_db():
    if not supabase:
        return []
    try:
        return supabase.table("leads_instagram").select("*").order("id", desc=True).execute().data or []
    except Exception:
        return []


def salvar_lead_db(lead):
    """Grava um lead novo. Retorna True se inseriu, False se já existia ou houve erro."""
    if not supabase:
        return False
    try:
        existe = (supabase.table("leads").select("id")
                  .eq("nome", lead["nome"]).eq("endereco", lead["endereco"]).execute())
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
            "foto_url": "",
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
    if supabase:
        try:
            supabase.table("leads").update({"status_crm": novo_status}).eq("id", lead_id).execute()
        except Exception as e:
            st.error(f"Erro ao atualizar status: {e}")


def limpar_banco_dados():
    if supabase:
        try:
            supabase.table("leads").delete().neq("id", 0).execute()
        except Exception as e:
            st.error(f"Erro ao limpar banco: {e}")


base_leads = carregar_todos_leads_db()
base_leads_insta = carregar_leads_instagram_db()


# =============================================================================
# GOOGLE PLACES API
# =============================================================================
def calcular_oportunidade(website, total_avaliacoes, qtd_fotos):
    """
    Score (0 a 100) só com dados que a API informa:
      - Sem site: 30 | Site sem HTTPS: 15
      - Menos de 30 avaliações: 25
      - Menos de 8 fotos (amostra da API): 20
    Tour 360° e reivindicação não entram (a API não informa).
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
    return min(round(pontos / PONTOS_MAXIMOS_API * 100), 100), criticos, oportunidades


def buscar_todas_paginas(query, api_key, limite):
    """Percorre as páginas da Text Search (20 por página). Retorna lista ou None em erro."""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "language": "pt-BR", "key": api_key}
    resultados = []
    while True:
        try:
            data = requests.get(url, params=params, timeout=12).json()
        except Exception as e:
            st.error(f"Falha de conexão com a Google Places API: {e}")
            return None
        status = data.get("status")
        if status == "ZERO_RESULTS":
            break
        if status != "OK":
            st.error(f"Google Places retornou '{status}'. {data.get('error_message', '')}")
            return None
        resultados += data.get("results", [])
        token = data.get("next_page_token")
        if not token or len(resultados) >= limite:
            break
        time.sleep(PAUSA_PAGINACAO)
        params = {"pagetoken": token, "key": api_key}
    return resultados[:limite]


def buscar_google_places_api(nicho, cidade, bairro, rua, api_key, limite):
    termos = [t.strip() for t in [nicho, rua, bairro, cidade] if t and t.strip()]
    places = buscar_todas_paginas(" ".join(termos), api_key, limite)
    if places is None:
        return None

    leads = []
    for place in places:
        det = {}
        if place.get("place_id"):
            try:
                det = requests.get(
                    "https://maps.googleapis.com/maps/api/place/details/json",
                    params={
                        "place_id": place["place_id"],
                        "fields": "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos",
                        "language": "pt-BR", "key": api_key,
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

        digitos = "".join(ch for ch in telefone if ch.isdigit())
        if len(digitos) > 11 and digitos.startswith("55"):
            digitos = digitos[2:]
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
            "whatsapp": digitos if len(digitos) >= 10 else "",
            "website": website,
            "website_https": website.startswith("https://") if website else False,
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
# PDF DO PANORAMA (padrão Gestão)
# =============================================================================
def gerar_pdf_panorama_nicho(nicho_nome, df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, title=f"Panorama de Mercado - {nicho_nome}",
        author="Tour360VR", **margens(),
    )
    sec = ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=10, leading=13,
                         textColor=colors.HexColor("#1E293B"), spaceBefore=8, spaceAfter=6)

    el = cabecalho(
        f"<b>PANORAMA DE MERCADO</b><br/>"
        f"<font size=9 color='#2563EB'><b>{nicho_nome}</b></font><br/>"
        f"<font size=8 color='#64748B'>Gerado em {datetime.now().strftime('%d/%m/%Y')}</font>",
        LOGO_TOUR,
    )

    total = len(df)
    contagem = df["score_oportunidade"].value_counts().sort_index(ascending=False)
    cats = [f"{int(s)} pts" for s in contagem.index]
    cores = [PALETA["alta"] if s >= 60 else PALETA["media"] if s >= 30 else PALETA["baixa"] for s in contagem.index]
    el.append(Paragraph("1. Distribuição por score de oportunidade", sec))
    el.append(grafico_barras(cats, [int(v) for v in contagem.values], cores))
    el.append(Spacer(1, 6))

    poucas = int((df["total_avaliacoes"] < 30).sum())
    sem_site = int((df["website"].fillna("") == "").sum())
    media = round(float(df["score_oportunidade"].mean()), 1) if total else 0

    def pct(q):
        return f"{q / total * 100:.1f}%" if total else "0%"

    el.append(Paragraph("2. Indicadores estratégicos", sec))
    el.append(tabela_padrao(
        ["Indicador", "Volume / %", "Diagnóstico de oportunidade"],
        [
            ["Volume baixo de avaliações", f"{poucas} ({pct(poucas)})",
             "Menos de 30 avaliações, o que afeta a prova social e o ranking."],
            ["Sem website oficial", f"{sem_site} ({pct(sem_site)})",
             "Perda de tráfego direto e dependência de canais de terceiros."],
            ["Score médio de oportunidade", f"{media}/100",
             "Média dos critérios verificáveis pela Google Places API."],
        ],
        [170, 100, 262],
    ))
    el.append(Spacer(1, 10))

    el.append(Paragraph("3. Ranking de empresas auditadas no setor", sec))
    linhas = []
    for _, r in df.sort_values("score_oportunidade", ascending=False).iterrows():
        linhas.append([
            str(r["nome"])[:50],
            f"{float(r['nota']):.1f}",
            str(int(r["total_avaliacoes"])),
            "Sim" if r["website"] else "Não",
            f"{int(r['score_oportunidade'])}/100",
        ])
    el.append(tabela_padrao(["Empresa", "Nota", "Avaliações", "Site", "Score"],
                            linhas, [222, 60, 80, 70, 100]))

    doc.build(el, onFirstPage=rodape, onLaterPages=rodape)
    buffer.seek(0)
    return buffer


# =============================================================================
# SIDEBAR E NAVEGAÇÃO
# =============================================================================
if "etapa" not in st.session_state:
    st.session_state.etapa = 1


def mudar_etapa(nova):
    st.session_state.etapa = nova
    st.rerun()


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
        st.markdown(f'<div class="gl-side-logo"><img src="data:image/png;base64,{logo_side}"/></div>',
                    unsafe_allow_html=True)
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
    hero_radar("Radar e Mineração de Mercado Local",
               "Varredura de perfis no Google Maps por nicho, cidade, bairro e rua. Dados da Google Places API.")

    with st.form("form_busca"):
        c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1.2])
        nicho_input = c1.text_input("Nicho / Categoria", placeholder="Ex: clínica estética")
        cidade_input = c2.text_input("Cidade", value="Ribeirão Preto")
        bairro_input = c3.text_input("Bairro / Região (opcional)")
        rua_input = c4.text_input("Rua / Avenida (opcional)")
        limite_input = c5.number_input("Qtd. máx.", min_value=5, max_value=MAX_LEADS, value=MAX_LEADS, step=5)
        enviar = st.form_submit_button("🚀 Iniciar varredura", use_container_width=True)

    if enviar:
        if not nicho_input and not cidade_input:
            st.warning("Informe pelo menos o nicho ou a cidade.")
        else:
            with st.spinner("Consultando o Google Maps e salvando na base (pode levar alguns segundos)..."):
                resultado = minerar_e_salvar(nicho_input, cidade_input, bairro_input, rua_input, int(limite_input))
            if resultado is not None:
                leads, novos = resultado
                if leads:
                    st.success(f"{len(leads)} empresas analisadas · {novos} novas salvas na base.")
                else:
                    st.info("Nenhum resultado para essa busca. Tente outro nicho ou cidade.")

    if base_leads:
        section_title("Base atual")
        with glass_container():
            st.markdown(f"Você tem **{len(base_leads)}** leads salvos na nuvem.")
            if st.button("Ver base completa no CRM ➡️", type="primary"):
                mudar_etapa(2)

# =============================================================================
# MÓDULO 2: CRM (um card único por lead)
# =============================================================================
elif st.session_state.etapa == 2:
    hero_radar("CRM de Prospecção",
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

        st.markdown(f"<span class='gl-muted'>Exibindo <b>{len(filtrados)}</b> oportunidades</span>",
                    unsafe_allow_html=True)

        for lead in filtrados:
            score = int(lead["score_oportunidade"])
            criticos = lead.get("pontos_criticos") or []
            if isinstance(criticos, str):
                criticos = json.loads(criticos or "[]")
            status_atual = lead.get("status_crm") or STATUS[0]

            with st.container(border=True):
                col_info, col_det, col_acoes = st.columns([3, 3, 2.5])

                with col_info:
                    st.markdown(f"### {lead['nome']}")
                    st.markdown(
                        f"<span class='gl-muted'>📍 {lead.get('endereco', '')}<br/>🏷️ {lead.get('categoria', '')}</span>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(badge_score(score), unsafe_allow_html=True)
                    novo_st = st.selectbox(
                        "Status comercial", STATUS,
                        index=STATUS.index(status_atual) if status_atual in STATUS else 0,
                        key=f"crm_st_{lead['id']}",
                    )
                    if novo_st != status_atual:
                        atualizar_status_crm(lead["id"], novo_st)
                        st.toast("Status atualizado na nuvem.")
                        st.rerun()

                with col_det:
                    st.markdown("**📊 Indicadores (Google Places)**")
                    st.markdown(f"- Nota: ⭐ {lead.get('nota', 0)} ({lead.get('total_avaliacoes', 0)} avaliações)")
                    st.markdown(f"- Fotos (amostra da API): {lead.get('fotos_total', 0)}")
                    st.markdown("- Ficha reivindicada: ⚠️ verificar manualmente")
                    st.markdown("- Tour 360°: ⚠️ verificar manualmente")
                    st.markdown("**🚨 Pontos críticos**")
                    if criticos:
                        for pc in criticos:
                            st.markdown(f"<div class='gl-critico'>❌ {pc}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='gl-muted'>Nenhum ponto crítico nos critérios automáticos.</span>",
                                    unsafe_allow_html=True)

                with col_acoes:
                    st.markdown("**🌐 Presença e ações**")
                    st.markdown(f"- Website: {lead['website'] if lead.get('website') else '❌ Sem site'}")
                    st.markdown(
                        f"[Ver no Google Maps](https://www.google.com/maps/search/?api=1&query="
                        f"{urllib.parse.quote(lead['nome'])})"
                    )
                    link_secundario(URL_SISTEMA_DIAGNOSTICO, "🛠️ Abrir no Diagnóstico Tour360VR")
                    if lead.get("whatsapp"):
                        msg_wa = (
                            f"Olá! Tudo bem?\nMeu nome é Rubens Okamoto, da Okamoto Mídias Visuais e do Tour360VR.\n"
                            f"Estava analisando a presença da {lead['nome']} no Google e identifiquei pontos onde a "
                            f"visibilidade do espaço pode ser ampliada em relação aos concorrentes da região.\n"
                            f"Posso te enviar um diagnóstico curto em PDF por aqui?"
                        )
                        botao_whatsapp(f"https://wa.me/55{lead['whatsapp']}?text={urllib.parse.quote(msg_wa)}",
                                       "💬 WhatsApp")
                    else:
                        st.caption("Sem WhatsApp identificado na ficha.")

# =============================================================================
# MÓDULO 3: PANORAMA DE NICHO
# =============================================================================
elif st.session_state.etapa == 3:
    hero_radar("Panorama de Mercado & Inteligência de Nicho",
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
                st.download_button("📄 Baixar relatório (.pdf)",
                                   data=gerar_pdf_panorama_nicho(nicho_sel, df_f),
                                   file_name=nome_pdf, mime="application/pdf", use_container_width=True)

        if len(df_f) == 0:
            st.info("Nenhuma empresa para este filtro.")
        else:
            total = len(df_f)
            poucas = int((df_f["total_avaliacoes"] < 30).sum())
            sem_site = int((df_f["website"].fillna("") == "").sum())
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Empresas analisadas", total)
            m2.metric("Poucas avaliações (<30)", f"{poucas / total * 100:.1f}%", f"{poucas} empresas")
            m3.metric("Sem website", f"{sem_site / total * 100:.1f}%", f"{sem_site} empresas")
            m4.metric("Score médio", f"{df_f['score_oportunidade'].mean():.0f}/100")

            section_title("Distribuição do score de oportunidade")
            with glass_container():
                st.bar_chart(df_f["score_oportunidade"].value_counts().sort_index(), color=PALETA["azul"])

            section_title("Ranking do nicho")
            df_rank = pd.DataFrame({
                "Empresa": df_f["nome"],
                "Cidade": df_f["cidade_busca"],
                "Score": df_f["score_oportunidade"].apply(lambda x: f"{int(x)}/100"),
                "Nota": df_f["nota"].apply(lambda x: f"{float(x):.1f}"),
                "Avaliações": df_f["total_avaliacoes"].astype(str),
                "Website": df_f["website"].apply(lambda x: x if x else "Sem site"),
            })
            st.dataframe(df_rank, hide_index=True, use_container_width=True,
                         height=min(900, (len(df_rank) + 1) * 35 + 10))

# =============================================================================
# MÓDULO 4: MAPA DE PROSPECÇÃO (pins com card no popup)
# =============================================================================
elif st.session_state.etapa == 4:
    hero_radar("Mapa de Localização e Concentração",
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

        st.markdown(f"<span class='gl-muted'>Exibindo <b>{len(df_m)}</b> empresas no mapa.</span>",
                    unsafe_allow_html=True)

        if len(df_m) > 0:
            CORES_PINS = ["red", "blue", "green", "purple", "orange", "darkred", "cadetblue", "darkgreen", "darkblue", "pink"]
            CORES_HEX = {
                "red": "#ef4444", "blue": "#3b82f6", "green": "#10b981", "purple": "#8b5cf6",
                "orange": "#f97316", "darkred": "#991b1b", "cadetblue": "#06b6d4",
                "darkgreen": "#166534", "darkblue": "#1e3a8a", "pink": "#ec4899",
            }
            COR_SCORE = {"alta": "red", "media": "orange", "baixa": "green"}

            # Cores por nicho calculadas sobre a base inteira, para ficarem estáveis entre filtros
            segmentos = sorted(df_map["categoria"].dropna().unique().tolist())
            mapa_cor_nicho = {seg: CORES_PINS[i % len(CORES_PINS)] for i, seg in enumerate(segmentos)}

        def cor_pin(row):
                if cat_map == "Todos":
                    return mapa_cor_nicho.get(row["categoria"], "red")
                classe, _, _ = classificar_score(int(row["score_oportunidade"]))
                return COR_SCORE[classe]

        def legenda_html(titulo, itens):
                linhas = "".join(
                    f"<div style='display:flex;align-items:center;gap:8px;margin:3px 0'>"
                    f"<span style='width:12px;height:12px;border-radius:50%;background:{cor};display:inline-block'></span>"
                    f"{rotulo}</div>"
                    for rotulo, cor in itens
                )
                return (
                    "<div style='position:fixed;bottom:18px;left:18px;z-index:9999;max-width:240px;"
                    "background:rgba(11,14,20,.88);color:#E6EDF7;padding:10px 14px;border-radius:12px;"
                    "border:1px solid rgba(255,255,255,.12);font-family:Inter,Arial,sans-serif;font-size:12px;'>"
                    f"<b style='color:#FFFFFF'>{titulo}</b>{linhas}</div>"
                )

                m = folium.Map(
                location=[df_m["latitude"].mean(), df_m["longitude"].mean()],
                zoom_start=13,
                tiles="OpenStreetMap",
                )
                bounds = []
        for _, row in df_m.iterrows():
                url_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(row['nome'])}"
                criticos = row.get("pontos_criticos") or []
                if isinstance(criticos, str):
                    criticos = json.loads(criticos or "[]")
                itens_crit = "".join(f"<li style='color:#b91c1c'>{c}</li>" for c in criticos[:4]) or "<li>Nenhum ponto crítico</li>"
                html_pop = (
                    f"<div style='font-family:Arial,sans-serif;font-size:12px;min-width:250px;line-height:1.5;color:#111'>"
                    f"<a href='{url_maps}' target='_blank' style='text-decoration:none'>"
                    f"<b style='color:#1E40AF;font-size:14px'>{row['nome']}</b></a><br/>"
                    f"<span style='color:#475569'>📍 {row['endereco']}</span><hr style='margin:6px 0'/>"
                    f"<b>Nicho:</b> {row['categoria']}<br/>"
                    f"<b>Score de oportunidade:</b> {row['score_oportunidade']}/100<br/>"
                    f"<b>Nota:</b> ⭐ {row['nota']} ({row['total_avaliacoes']} avaliações)<br/>"
                    f"<b>Pontos críticos:</b><ul style='margin:4px 0 0 16px;padding:0'>{itens_crit}</ul></div>"
                )
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    popup=folium.Popup(html_pop, max_width=340),
                    tooltip=row["nome"],
                    icon=folium.Icon(color=cor_pin(row), icon="info-sign"),
                ).add_to(m)
                bounds.append([row["latitude"], row["longitude"]])

            # Legenda
            if cat_map == "Todos":
                itens_leg = [(seg, CORES_HEX[mapa_cor_nicho[seg]]) for seg in segmentos]
                m.get_root().html.add_child(folium.Element(legenda_html("Legenda por nicho", itens_leg)))
            else:
                itens_leg = [
                    ("Alta (≥ 60)", "#ef4444"),
                    ("Média (30 a 59)", "#f97316"),
                    ("Baixa (< 30)", "#22c55e"),
                ]
                m.get_root().html.add_child(folium.Element(legenda_html("Legenda por score", itens_leg)))

            if len(bounds) > 1:
                m.fit_bounds(bounds, padding=(30, 30))
            with st.container(border=True):
                st_folium(m, width=None, height=650, returned_objects=[])


# =============================================================================
# MÓDULO 5: LEADS DO INSTAGRAM
# =============================================================================
elif st.session_state.etapa == 5:
    hero_radar("Leads do Instagram",
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

    section_title(f"Base de leads do Instagram ({len(base_leads_insta)})")
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

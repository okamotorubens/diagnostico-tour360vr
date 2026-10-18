import streamlit as st
import pandas as pd
import os
import time
import urllib.parse
from datetime import datetime, date
from io import BytesIO
import base64

import qrcode
from PIL import Image as PILImage
from supabase import create_client, Client
import pytz
import requests

# ReportLab (PDF)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Matplotlib (gráfico no PDF)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Design system Tour360VR
from design.theme import inject_theme
from design.components import render_hero, section_title, kpi_card, glass_container
from design.tokens import COLORS

# --- CONFIGURAÇÃO DA PÁGINA ---
FAVICON_TOUR360 = "https://tour360vr.com.br/favicon.ico"
AZUL_ESCURO = "#1E3A8A"
AZUL_LINK = "#1E40AF"
WHATSAPP_VERDE = "#25D366"

st.set_page_config(
    page_title="Gestão Mensal & Estratégia | Tour360VR",
    page_icon=FAVICON_TOUR360,
    layout="wide",
)
inject_theme()

# Botões WhatsApp: texto sempre branco (sobrescreve o azul de link do Streamlit)
st.markdown(
    """
    <style>
    a.gl-wpp, a.gl-wpp:visited, a.gl-wpp:hover, a.gl-wpp:focus, a.gl-wpp * {
        color: #FFFFFF !important; text-decoration: none !important;
    }
    a.gl-wpp {
        display: block; width: 100%; box-sizing: border-box;
        background: #25D366 !important; padding: 12px; border-radius: 12px;
        font-weight: 700; text-align: center; font-size: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Caminho da logo (aceita raiz, assets/ ou assests/)
LOGO_CANDIDATES = [
    "logo_tour_transparente.png",
    "assets/logo_tour_transparente.png",
    "assests/logo_tour_transparente.png",
]
LOGO_LOCAL_PATH = next((p for p in LOGO_CANDIDATES if os.path.exists(p)), LOGO_CANDIDATES[0])

# --- FUSO HORÁRIO BRASÍLIA ---
FUSO_BR = pytz.timezone("America/Sao_Paulo")


def agora_brasil():
    return datetime.now(FUSO_BR)


def obter_base64_logo(caminho):
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


def botao_whatsapp(url, texto):
    st.markdown(f'<a class="gl-wpp" href="{url}" target="_blank">{texto}</a>', unsafe_allow_html=True)


def csv_bytes(df):
    return df.to_csv(index=False, sep=";").encode("utf-8-sig")


# --- LOGO E RODAPÉ PADRÃO DO PDF ---
def get_rl_image_pdf(width=45, height=45):
    if os.path.exists(LOGO_LOCAL_PATH):
        try:
            with open(LOGO_LOCAL_PATH, "rb") as f:
                img_bytes = f.read()
            return RLImage(BytesIO(img_bytes), width=width, height=height, kind="proportional")
        except Exception:
            pass
    styles = getSampleStyleSheet()
    return Paragraph("<b>Tour360VR</b>", ParagraphStyle("Fallback", parent=styles["Normal"], fontName="Helvetica-Bold"))


def adicionar_rodape_padrao(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#BFDBFE"))
    canvas.setLineWidth(0.8)
    canvas.line(40, 32, letter[0] - 40, 32)
    footer_html = (
        '<font color="#334155">'
        f'<font color="{AZUL_LINK}"><a href="https://tour360vr.com.br">tour360vr.com.br</a></font> &nbsp;|&nbsp; '
        f'<font color="{AZUL_LINK}"><a href="mailto:contato@tour360vr.com.br">contato@tour360vr.com.br</a></font> &nbsp;|&nbsp; '
        f'WhatsApp: <font color="{AZUL_LINK}"><a href="https://wa.me/5516991332121">(16) 99133-2121</a></font>'
        '</font>'
    )
    p = Paragraph(footer_html, ParagraphStyle("FooterStyle", fontName="Helvetica", fontSize=8, alignment=1))
    p.wrap(letter[0] - 80, 20)
    p.drawOn(canvas, 40, 16)
    canvas.restoreState()


def cabecalho_pdf(titulo_direita_html, logo_size=45, col_logo=55):
    """Cabeçalho padrão: logo à esquerda, título à direita, linha divisória."""
    styles = getSampleStyleSheet()
    t = Table([[
        get_rl_image_pdf(logo_size, logo_size),
        Paragraph(titulo_direita_html, ParagraphStyle("RH", parent=styles["Normal"], alignment=2, fontName="Helvetica-Bold", fontSize=11, textColor=colors.HexColor(AZUL_ESCURO))),
    ]], colWidths=[col_logo, 512 - col_logo])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (0, 0), "LEFT")]))
    return [t, Spacer(1, 2), HRFlowable(width="100%", thickness=1.0, color=colors.HexColor("#BFDBFE"), spaceAfter=10)]


# --- CONEXÃO COM SUPABASE (banco) ---
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = get_supabase_client()


# --- AUTENTICAÇÃO (Supabase Auth, plano gratuito) ---
def get_auth_client() -> Client:
    """Cliente exclusivo da sessão do navegador, para não compartilhar login entre usuários."""
    if "auth_client" not in st.session_state:
        st.session_state["auth_client"] = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    return st.session_state["auth_client"]


def tela_login():
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
    section_title("🔐 Acesso restrito à plataforma")
    with glass_container():
        with st.form("form_login"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar")
    if entrar:
        try:
            res = get_auth_client().auth.sign_in_with_password({"email": email, "password": senha})
            st.session_state["usuario_logado"] = res.user.email
            st.rerun()
        except Exception:
            st.error("E-mail ou senha inválidos.")


# --- ROTA DE APROVAÇÃO EXTERNA (pública, sem login) ---
query_params = st.query_params
if "aprovar" in query_params or st.session_state.get("modo_aprovacao", False):
    logo_b64_aprov = obter_base64_logo(LOGO_LOCAL_PATH)
    render_hero(
        logo_b64_aprov,
        "Página de Aprovação de Pautas",
        "Planejamento Estratégico de Conteúdo e SEO Local",
    )

    with glass_container():
        st.markdown("**Bem-vindo à sua página exclusiva de validação e curadoria de pautas.**")

    section_title("Selecione as Pautas Aprovadas e Informe Ajustes se Necessário:")

    pautas_exemplo = [
        "1. Como escolher o melhor serviço especializado na região com garantia de qualidade.",
        "2. Bastidores da nossa equipe: Nosso compromisso absoluto com a excelência.",
        "3. Conheça nossa estrutura imersiva através do Tour Virtual 360° no Google Maps.",
        "4. Diferenciais técnicos que tornam nosso atendimento referência local.",
        "5. Atendimento rápido, orçamentos e facilidades pelo canal oficial de atendimento.",
        "6. Perguntas frequentes (FAQ): Tire todas as suas dúvidas diretamente conosco.",
    ]

    pautas_status = {}
    with glass_container():
        for idx, p in enumerate(pautas_exemplo, 1):
            pautas_status[p] = st.checkbox(p, value=False, key=f"aprov_pauta_{idx}")

    section_title("💬 Solicitar Ajustes ou Alterações")
    obs_cliente = st.text_area(
        "Tem alguma observação ou alteração para esta pauta? Digite aqui:",
        placeholder="Ex: Gostaria de alterar o foco da pauta 2 para...",
        height=100,
    )

    pautas_aprovadas_txt = "\n".join([k for k, v in pautas_status.items() if v])
    msg_envio = (
        "Olá Rubens!\nAvaliei o planejamento de pautas na plataforma da Tour360VR.\n\n"
        f"Pautas Aprovadas:\n{pautas_aprovadas_txt if pautas_aprovadas_txt else 'Nenhuma pauta marcada diretamente.'}\n\n"
        f"Ajustes Solicitados:\n{obs_cliente if obs_cliente else 'Nenhum ajuste adicional.'}"
    )
    link_wsp_final = f"https://wa.me/5516991332121?text={urllib.parse.quote(msg_envio)}"
    botao_whatsapp(link_wsp_final, "📤 Enviar Aprovação e Ajustes para o WhatsApp do Rubens")
    st.stop()

# --- CABEÇALHO ---
logo_base64 = obter_base64_logo(LOGO_LOCAL_PATH)
render_hero(
    logo_base64,
    "Gestão Mensal & Estratégia",
    "Plataforma corporativa de inteligência de Google Maps, auditoria, curadoria e contratos.",
)

# --- GATE DE LOGIN ---
if "usuario_logado" not in st.session_state:
    tela_login()
    st.stop()

st.markdown(
    "<style>"
    "div[data-testid='stHorizontalBlock']:has(.gl-logout) button {"
    "min-height: 30px !important; height: auto !important; padding: 2px 14px !important;"
    "font-size: 0.78rem !important; width: auto !important;}"
    "</style>",
    unsafe_allow_html=True,
)
col_u, col_s = st.columns([9, 1.4])
with col_u:
    st.markdown(
        f"<div style='text-align:right; font-size:0.85rem; color:#8E9BAE;'>"
        f"<span class='gl-logout'></span>Conectado como <b style='color:#FFFFFF'>{st.session_state['usuario_logado']}</b></div>",
        unsafe_allow_html=True,
    )
with col_s:
    if st.button("Sair", key="btn_sair"):
        try:
            get_auth_client().auth.sign_out()
        except Exception:
            pass
        for chave in ["usuario_logado", "auth_client"]:
            st.session_state.pop(chave, None)
        st.rerun()

# --- NAVEGAÇÃO SEQUENCIAL DAS ABAS ---
ORDEM_ABAS = ["cadastrar", "auditoria", "metricas", "ia", "dashboard", "cases", "pdf", "financeiro"]
NOMES_ABAS = {
    "cadastrar": "⚙️ Ficha Comercial",
    "auditoria": "🔍 Auditoria Link",
    "metricas": "📋 Métricas & SEO",
    "ia": "🎯 Curadoria & Pautas",
    "dashboard": "📊 Dashboard ROI",
    "cases": "🏆 Prospecção",
    "pdf": "📄 Relatório & Contrato",
    "financeiro": "💰 Financeiro MRR",
}


def gerar_botoes_navegacao_rodape():
    st.markdown("---")
    aba_atual = st.session_state.get("aba_ativa", "cadastrar")
    idx_atual = ORDEM_ABAS.index(aba_atual) if aba_atual in ORDEM_ABAS else 0
    col_v, col_p = st.columns([6, 2], gap="small")
    with col_v:
        if idx_atual > 0:
            aba_anterior = ORDEM_ABAS[idx_atual - 1]
            if st.button(f"⬅️ Voltar ({NOMES_ABAS[aba_anterior]})", key=f"btn_rodape_prev_{aba_atual}"):
                st.session_state["aba_ativa"] = aba_anterior
                st.rerun()
    with col_p:
        if idx_atual < len(ORDEM_ABAS) - 1:
            aba_proxima = ORDEM_ABAS[idx_atual + 1]
            if st.button(f"Próximo ({NOMES_ABAS[aba_proxima]}) ➡️", key=f"btn_rodape_next_{aba_atual}", use_container_width=True):
                st.session_state["aba_ativa"] = aba_proxima
                st.rerun()


def obter_clientes_unicos():
    res = supabase.table("clientes").select("id, nome_empresa").order("nome_empresa").execute()
    if res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["id", "nome_empresa"])


def obter_dados_cliente_por_id(cliente_id):
    res = supabase.table("clientes").select("*").eq("id", cliente_id).execute()
    if res.data:
        return res.data[0]
    return None


def calcular_variacao_pct(atual, anterior):
    if anterior is None or anterior == 0:
        return "+100%" if atual > 0 else "0%"
    diff = ((atual - anterior) / anterior) * 100
    if diff > 0:
        return f"+{diff:.1f}%"
    return f"{diff:.1f}%"


def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- AUDITORIA OFICIAL COM OS 9 CRITÉRIOS ---
def auditar_ficha_google_rigorosa(query_ou_url):
    api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key:
        return None, "Chave GOOGLE_API_KEY não configurada nos Secrets do Streamlit."

    try:
        termo_busca = query_ou_url
        if "http" in query_ou_url and ("maps.app.goo.gl" in query_ou_url or "goo.gl" in query_ou_url):
            resp_redirect = requests.get(query_ou_url, allow_redirects=True, timeout=10)
            termo_busca = resp_redirect.url

        url_search = (
            "https://maps.googleapis.com/maps/api/place/textsearch/json"
            f"?query={urllib.parse.quote(termo_busca)}&key={api_key}&language=pt-BR"
        )
        resp = requests.get(url_search, timeout=10).json()

        if not resp.get("results"):
            return None, "Nenhum local encontrado com esta URL ou termo na Google Places API."

        place = resp["results"][0]
        place_id = place.get("place_id")
        nome = place.get("name", "Empresa Selecionada")

        url_details = (
            "https://maps.googleapis.com/maps/api/place/details/json"
            f"?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,website,rating,"
            f"user_ratings_total,photos,opening_hours,business_status,types,editorial_summary,reviews"
            f"&key={api_key}&language=pt-BR"
        )
        details = requests.get(url_details, timeout=10).json().get("result", {})

        criterios = []
        score = 100

        fotos = details.get("photos", [])
        qtd_fotos = len(fotos)
        if qtd_fotos < 5:
            score -= 10
            criterios.append(("1. Fotos e Resolução Visual", "Poucas fotos encontradas / antigas no perfil.", "Baixo", "Incompletas"))
        else:
            criterios.append(("1. Fotos e Resolução Visual", f"{qtd_fotos} fotos registradas.", "Bom", "Atendido"))

        criterios.append(("2. Tour Virtual 360° Interativo", "A Places API não informa a existência de tour virtual. Conferir manualmente no perfil.", "Verificação manual", "Manual"))

        types = details.get("types", [])
        tipos_txt = ", ".join(t.replace("_", " ") for t in types[:4]) or "não informado"
        criterios.append(("3. Categorias Principal e Secundárias", f"Tipos retornados pela API: {tipos_txt}. Categoria principal e secundárias exigem conferência no painel do Google.", "Verificação manual", "Manual"))

        opening_hours = details.get("opening_hours", {})
        if not opening_hours or not opening_hours.get("periods"):
            score -= 10
            criterios.append(("4. Horários e Exceções (Feriados)", "Falta de horários detalhados e exceções em feriados.", "Médio", "Pendente"))
        else:
            criterios.append(("4. Horários e Exceções (Feriados)", "Horários regulares cadastrados.", "Bom", "Atendido"))

        website = details.get("website")
        if not website:
            score -= 15
            criterios.append(("5. Website e Links de Conversão", "Ficha sem Link de Website / Cartão Digital configurado.", "Crítico", "Ausente"))
        else:
            criterios.append(("5. Website e Links de Conversão", f"Website oficial: {website}", "Alto", "Ativo"))

        total_reviews = details.get("user_ratings_total", 0)
        rating = details.get("rating", 0.0)
        if total_reviews < 10:
            score -= 15
            criterios.append(("6. Avaliações no Google (Prova Social)", f"{total_reviews} avaliações registradas (Nota: {rating}). Volume baixo.", "Crítico", f"{rating}/5.0"))
        else:
            criterios.append(("6. Avaliações no Google (Prova Social)", f"{total_reviews} avaliações. Boa base de prova social.", "Alto", f"{rating}/5.0"))

        editorial = details.get("editorial_summary")
        if not editorial:
            score -= 10
            criterios.append(("7. Resumo Editorial & Descrição", "Descrição da empresa incompleta ou ausente na API.", "Médio", "Ausente"))
        else:
            criterios.append(("7. Resumo Editorial & Descrição", "Resumo editorial presente.", "Bom", "Atendido"))

        criterios.append(("8. Atributos de Acessibilidade/Serviços", "Não consultável pela API. Conferir atributos no painel do Google.", "Verificação manual", "Manual"))

        reviews = details.get("reviews", [])
        negativas = [r for r in reviews if r.get("rating", 5) <= 3]
        criterios.append(("9. Interação e Resposta a Avaliações", f"A API não informa respostas do gestor. Avaliações negativas na amostra: {len(negativas)}. Conferir respostas no painel.", "Verificação manual", "Manual"))

        score = max(0, score)

        return {
            "nome": nome,
            "score": score,
            "endereco": details.get("formatted_address", "Endereço não informado"),
            "telefone": details.get("formatted_phone_number", "Não informado"),
            "website": website or "Não informado",
            "rating": rating,
            "total_reviews": total_reviews,
            "criterios": criterios,
        }, None

    except Exception as e:
        return None, f"Erro ao consultar a Google Places API: {str(e)}"


# --- HISTÓRICO DE AUDITORIAS (Supabase, tabela "auditorias") ---
def salvar_auditoria_historico(res_aud):
    supabase.table("auditorias").insert({
        "nome_empresa": res_aud["nome"],
        "endereco": res_aud["endereco"],
        "score": int(res_aud["score"]),
        "criterios": [list(c) for c in res_aud["criterios"]],
    }).execute()


def listar_historico_auditorias(nome):
    try:
        res = (
            supabase.table("auditorias")
            .select("created_at, score, endereco")
            .eq("nome_empresa", nome)
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


# --- PDF DA AUDITORIA ---
def gerar_pdf_auditoria(res_aud):
    nome_doc = f"Diagnostico Auditoria Google Maps {res_aud['nome']}"
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=15, bottomMargin=55,
        title=nome_doc,
    )
    styles = getSampleStyleSheet()
    story = []

    section_style = ParagraphStyle("DocSection", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.HexColor("#1E293B"))
    body_style = ParagraphStyle("DocBody", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#334155"))
    th_style = ParagraphStyle("DocTh", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.white)
    nome_style = ParagraphStyle("DocNome", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=colors.HexColor(AZUL_ESCURO))
    score_style = ParagraphStyle("DocScore", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=colors.HexColor(AZUL_ESCURO))

    story += cabecalho_pdf("<b>DIAGNÓSTICO DE AUDITORIA GOOGLE MAPS</b>")

    story.append(Spacer(1, 12))  # 1 linha
    story.append(Paragraph(res_aud["nome"], nome_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Endereço:</b> {res_aud['endereco']} | <b>Telefone:</b> {res_aud['telefone']}", body_style))
    story.append(Spacer(1, 24))  # 2 linhas
    story.append(Paragraph(f"Score da Ficha: {res_aud['score']}/100", score_style))
    story.append(Spacer(1, 24))  # 2 linhas

    story.append(Paragraph("Auditoria Detalhada de Pontos (9 Critérios Oficiais)", section_style))
    story.append(Spacer(1, 6))

    t_data = [[Paragraph("Critério", th_style), Paragraph("Diagnóstico Técnico", th_style),
               Paragraph("Impacto", th_style), Paragraph("Status", th_style)]]
    for item, estado, impacto, status in res_aud["criterios"]:
        t_data.append([Paragraph(item, body_style), Paragraph(estado, body_style),
                       Paragraph(impacto, body_style), Paragraph(status, body_style)])

    t_aud = Table(t_data, colWidths=[150, 200, 70, 92], repeatRows=1)
    t_aud.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(AZUL_ESCURO)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#94A3B8")),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_aud)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Metodologia: score de 0 a 100 calculado sobre os critérios automáticos (fotos -10, horários -10, website -15, avaliações -15, resumo -10). Itens marcados como Verificação manual não pontuam.", body_style))
    story.append(Spacer(1, 12))  # 1 linha antes do plano

    story.append(Paragraph("Plano de Ação &amp; Oportunidades Recomendadas", section_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("1. Atração Local (SEO): Correção cadastral e otimização das categorias principal e secundárias.", body_style))
    story.append(Paragraph("2. Segurança &amp; Posicionamento: Frequência de atualização para sinalizar ao Google que o perfil está ativo.", body_style))
    story.append(Paragraph("3. Confiança &amp; Autoridade: Publicação do Tour Virtual 360° no Street View e fotos em alta resolução.", body_style))
    story.append(Paragraph("4. Vitrine Imersiva: Padronização do acervo visual do espaço e integração dos canais de contato direto.", body_style))

    doc.build(story, onFirstPage=adicionar_rodape_padrao, onLaterPages=adicionar_rodape_padrao)
    buffer.seek(0)
    return buffer


def gerar_imagem_grafico(df_historico):
    fig, ax = plt.subplots(figsize=(6.5, 2.0), dpi=200)
    ax.plot(df_historico["mes_ano"], df_historico["chamadas"], marker="o", color="#2563EB", linewidth=2, label="Chamadas")
    ax.plot(df_historico["mes_ano"], df_historico["rotas"], marker="s", color="#16A34A", linewidth=2, label="Rotas")
    ax.plot(df_historico["mes_ano"], df_historico["cliques_site"], marker="^", color="#0284C7", linewidth=2, label="Cliques")
    ax.set_facecolor("#F8FAFC")
    fig.patch.set_facecolor("#FFFFFF")
    ax.grid(True, linestyle="--", alpha=0.5, color="#CBD5E1")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.xticks(fontsize=8, color="#334155", fontweight="bold")
    plt.yticks(fontsize=8, color="#334155")
    ax.legend(loc="upper left", fontsize=7, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1")
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    img_buf.seek(0)
    return img_buf


# --- PDF DO RELATÓRIO ---
def gerar_pdf_relatorio(nome_empresa, mes_ano, dados_atual, dados_anterior, dados_inicio, df_historico=None, df_keywords=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=15, bottomMargin=55,
                            title=f"Relatorio de Desempenho {nome_empresa} {mes_ano}")
    story = []
    styles = getSampleStyleSheet()

    section_style = ParagraphStyle("DocSection", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.HexColor("#1E293B"))
    body_style = ParagraphStyle("DocBody", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#334155"))

    story += cabecalho_pdf(
        f"<b>RELATÓRIO DE DESEMPENHO</b><br/>"
        f"<font size=9 color='#2563EB'><b>{nome_empresa}</b></font><br/>"
        f"<font size=8 color='#64748B'>Mês de Referência: {mes_ano}</font>"
    )

    story.append(Paragraph("<b>1. Análise Comparativa de Desempenho e Crescimento:</b>", section_style))
    story.append(Spacer(1, 6))

    inicio = df_historico.iloc[0] if df_historico is not None and len(df_historico) > 0 else None
    c_chamadas_ant = dados_anterior["chamadas"] if dados_anterior else 0
    c_rotas_ant = dados_anterior["rotas"] if dados_anterior else 0
    c_cliques_ant = dados_anterior["cliques_site"] if dados_anterior else 0

    comp_table_data = [
        [Paragraph("<b>Indicador</b>", section_style), Paragraph("<b>1º Registro</b>", section_style),
         Paragraph("<b>Mês Ant.</b>", section_style), Paragraph("<b>Mês Atual</b>", section_style),
         Paragraph("<b>Evolução</b>", section_style)],
        [Paragraph("Chamadas Telefônicas", body_style), Paragraph(str(inicio["chamadas"]) if inicio is not None else "-", body_style),
         Paragraph(f"{c_chamadas_ant}", body_style), Paragraph(f"<b>{dados_atual['chamadas']}</b>", body_style),
         Paragraph(f"<b>{calcular_variacao_pct(dados_atual['chamadas'], c_chamadas_ant)}</b>", body_style)],
        [Paragraph("Rotas GPS", body_style), Paragraph(str(inicio["rotas"]) if inicio is not None else "-", body_style),
         Paragraph(f"{c_rotas_ant}", body_style), Paragraph(f"<b>{dados_atual['rotas']}</b>", body_style),
         Paragraph(f"<b>{calcular_variacao_pct(dados_atual['rotas'], c_rotas_ant)}</b>", body_style)],
        [Paragraph("Cliques Site", body_style), Paragraph(str(inicio["cliques_site"]) if inicio is not None else "-", body_style),
         Paragraph(f"{c_cliques_ant}", body_style), Paragraph(f"<b>{dados_atual['cliques_site']}</b>", body_style),
         Paragraph(f"<b>{calcular_variacao_pct(dados_atual['cliques_site'], c_cliques_ant)}</b>", body_style)],
    ]
    t_comp = Table(comp_table_data, colWidths=[160, 90, 90, 90, 100])
    t_comp.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 10))

    if df_keywords is not None and len(df_keywords) > 0:
        story.append(Paragraph("<b>2. Monitoramento de Palavras-Chave &amp; Termos de Busca (Google Maps):</b>", section_style))
        story.append(Spacer(1, 6))
        kw_table_data = [[Paragraph("<b>Termo / Palavra-Chave</b>", section_style), Paragraph("<b>Posição Anterior</b>", section_style),
                          Paragraph("<b>Posição Atual</b>", section_style), Paragraph("<b>Variação</b>", section_style)]]
        for _, kw in df_keywords.iterrows():
            kw_table_data.append([Paragraph(str(kw.get("termo", "-")), body_style), Paragraph(str(kw.get("posicao_anterior", "-")), body_style),
                                  Paragraph(f"<b>{kw.get('posicao_atual', '-')}</b>", body_style), Paragraph(str(kw.get("variacao", "-")), body_style)])
        t_kw = Table(kw_table_data, colWidths=[200, 100, 100, 112])
        t_kw.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ]))
        story.append(t_kw)
        story.append(Spacer(1, 10))

    if df_historico is not None and len(df_historico) > 1:
        story.append(Paragraph("<b>3. Curva de Evolução Histórica:</b>", section_style))
        story.append(Spacer(1, 6))
        story.append(RLImage(gerar_imagem_grafico(df_historico), width=520, height=120))
        story.append(Spacer(1, 10))

    doc.build(story, onFirstPage=adicionar_rodape_padrao, onLaterPages=adicionar_rodape_padrao)
    buffer.seek(0)
    return buffer


# --- PDF DO CONTRATO ---
def gerar_pdf_contrato(dados_cliente, plano_escolhido, valor_plano, meses_duracao=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=15, bottomMargin=55,
        title=f"Contrato Tour360VR - {dados_cliente.get('nome_empresa', 'Cliente')}",
    )
    story = []
    styles = getSampleStyleSheet()

    doc_title_style = ParagraphStyle("DocTitleStyle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=13, leading=16, alignment=1, textColor=colors.HexColor("#1E293B"))
    body_style = ParagraphStyle("DocBody", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=9.6, alignment=4, textColor=colors.HexColor("#1E293B"))
    signature_style = ParagraphStyle("DocSig", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12, alignment=1, textColor=colors.HexColor("#1E293B"))

    story += cabecalho_pdf("<b>CONTRATO DE PRESTAÇÃO DE SERVIÇOS</b>")

    meses_pt = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    hoje = agora_brasil()
    data_extenso = f"Ribeirão Preto - SP, {hoje.day} de {meses_pt[hoje.month - 1]} de {hoje.year}."

    story.append(Paragraph(data_extenso, ParagraphStyle("Date", fontName="Helvetica", fontSize=9, alignment=2, textColor=colors.HexColor("#000000"))))
    story.append(Spacer(1, 10))
    story.append(Paragraph("TERMO DE CONTRATAÇÃO DE SERVIÇOS", doc_title_style))
    story.append(Spacer(1, 8))

    nome_emp = dados_cliente.get("nome_empresa", "Empresa Cliente")
    resp_emp = dados_cliente.get("responsavel", "Responsável")
    tel_emp = dados_cliente.get("telefone_contato", "")

    if meses_duracao and "Gestão Mensal" in plano_escolhido:
        detalhe_plano = f"{plano_escolhido} com duração de {meses_duracao} meses, no valor total de R$ {valor_plano:,.2f}"
    else:
        detalhe_plano = f"{plano_escolhido}, no valor total de R$ {valor_plano:,.2f}"

    link_site = f'<font color="{AZUL_LINK}"><a href="https://tour360vr.com.br">tour360vr.com.br</a></font>'
    link_mail = f'<font color="{AZUL_LINK}"><a href="mailto:contato@tour360vr.com.br">contato@tour360vr.com.br</a></font>'
    link_wpp = f'<font color="{AZUL_LINK}"><a href="https://wa.me/5516991332121">(16) 99133-2121</a></font>'

    txt_qualificacao = f"""
    <b>CONTRATADA:</b> <b>Tour360VR</b>, representada por Rubens Okamoto, CNPJ: 04.824.331/0001-05. Site: {link_site} | E-mail: {link_mail} | WhatsApp: {link_wpp}.<br/><br/>
    <b>CONTRATANTE:</b> <b>{nome_emp}</b>, representada por {resp_emp}, Telefone: {tel_emp}.<br/><br/>
    A <b>Tour360VR</b> (<b>CONTRATADA</b>) compromete-se a executar os serviços profissionais especializados em otimização, reestruturação técnica, curadoria de pautas e produção de Tour Virtual 360 para o perfil do Google da <b>CONTRATANTE</b>, referentes ao plano contratado <b>{detalhe_plano}</b>.
    """
    story.append(Paragraph(txt_qualificacao, body_style))
    story.append(Spacer(1, 6))

    clausulas = """
    <b>CLÁUSULA PRIMEIRA - DO OBJETO:</b> Os serviços serão iniciados em até 5 dias úteis após a confirmação do acordo e o fornecimento de todos os acessos e informações necessárias à gestão do perfil pela <b>CONTRATANTE</b>.<br/><br/>
    <b>CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES E PAGAMENTO:</b> O não pagamento no prazo pactuado sujeitará o presente contrato à incidência de juros moratórios legais e à suspensão temporária dos serviços pela <b>Tour360VR</b> até a devida regularização financeira.<br/><br/>
    <b>CLÁUSULA TERCEIRA - DOS DIREITOS DE USO E PROPRIEDADE:</b> Os direitos de uso do Tour Virtual 360 e fotos em alta definição serão cedidos em caráter ilimitado à <b>CONTRATANTE</b> para veiculação oficial no Google. A <b>Tour360VR</b> reserva-se o direito de utilizar o material gerado em seu portfólio profissional de divulgação.<br/><br/>
    <b>CLÁUSULA QUARTA - CONFIDENCIALIDADE E LGPD:</b> As partes comprometem-se a manter sob sigilo absoluto todas as informações operacionais fornecidas, em estrita conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).<br/><br/>
    <b>CLÁUSULA QUINTA - VALIDADE DA PROPOSTA:</b> A presente proposta e condições comerciais possuem validade oficial de 15 (quinze) dias a contar da data de sua emissão.<br/><br/>
    <b>CLÁUSULA SEXTA - AUSÊNCIA DE GARANTIA DE RESULTADOS:</b> A <b>Tour360VR</b> não garante posição específica nos resultados de busca ou no Google Maps, pois o ranqueamento depende de algoritmos e critérios de terceiros, fora de seu controle.<br/><br/>
    <b>CLÁUSULA SÉTIMA - DAS RESPONSABILIDADES DA CONTRATANTE:</b> A <b>CONTRATANTE</b> compromete-se a fornecer informações verídicas e atualizadas, os acessos necessários e a aprovação das pautas no prazo combinado, abstendo-se de solicitar ou incentivar avaliações falsas ou fraudulentas, em conformidade com as políticas do Google.<br/><br/>
    <b>CLÁUSULA OITAVA - DA RESCISÃO:</b> Qualquer das partes poderá rescindir o presente contrato mediante aviso prévio por escrito de 30 (trinta) dias.<br/><br/>
    <b>CLÁUSULA NONA - DO REAJUSTE:</b> O valor da mensalidade poderá ser reajustado anualmente pela variação do IPCA ou de índice que venha a substituí-lo.<br/><br/>
    <b>CLÁUSULA DÉCIMA - DA LIMITAÇÃO DE RESPONSABILIDADE:</b> A responsabilidade total da <b>Tour360VR</b> limita-se ao valor efetivamente pago pela <b>CONTRATANTE</b> no mês em que ocorrer o fato gerador do dano.<br/><br/>
    <b>CLÁUSULA DÉCIMA PRIMEIRA - DO FORO:</b> Fica eleito o foro da Comarca de Ribeirão Preto/SP para dirimir quaisquer controvérsias oriundas deste contrato.<br/><br/>
    <b>CLÁUSULA DÉCIMA SEGUNDA - DA MORA:</b> O atraso no pagamento sujeitará a <b>CONTRATANTE</b> a multa de 2% (dois por cento) e juros de 1% (um por cento) ao mês, calculados sobre o valor em atraso.
    """
    story.append(Paragraph(clausulas.replace("<br/><br/>", "<br/>"), body_style))
    story.append(Spacer(1, 16))

    t_ass = Table([[
        Paragraph("__________________________________________<br/><b>Rubens Okamoto</b><br/>Tour360VR", signature_style),
        Paragraph(f"__________________________________________<br/><b>{resp_emp}</b><br/>{nome_emp}", signature_style),
    ]], colWidths=[240, 240])
    story.append(t_ass)

    doc.build(story, onFirstPage=adicionar_rodape_padrao, onLaterPages=adicionar_rodape_padrao)
    buffer.seek(0)
    return buffer


# --- ESTADO INICIAL ---
if "aba_ativa" not in st.session_state:
    st.session_state["aba_ativa"] = "cadastrar"

# --- NAVEGAÇÃO EM ABAS (BOTÕES) ---
aba_map = [
    ("cadastrar", "⚙️ Ficha"), ("auditoria", "🔍 Auditoria"), ("metricas", "📋 Métricas"),
    ("ia", "🎯 Curadoria"), ("dashboard", "📊 Dashboard"), ("cases", "🏆 Prospecção"),
    ("pdf", "📄 Relatório"), ("financeiro", "💰 Financeiro"),
]
cols = st.columns(len(aba_map))
for i, (key_aba, label_aba) in enumerate(aba_map):
    with cols[i]:
        if st.button(
            label_aba,
            key=f"btn_nav_{key_aba}",
            type="primary" if st.session_state["aba_ativa"] == key_aba else "secondary",
            use_container_width=True,
        ):
            st.session_state["aba_ativa"] = key_aba
            st.rerun()

st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

# ==========================================
# MÓDULO 1: FICHA COMERCIAL
# ==========================================
if st.session_state["aba_ativa"] == "cadastrar":
    section_title("⚙️ Cadastro e Atualização de Informações Comerciais (GMB)")
    df_clientes = obter_clientes_unicos()
    modo_edicao = False
    dados_existentes = None
    c_id = None
    cliente_menu = None

    if not df_clientes.empty:
        opcoes = ["➕ Cadastrar Novo Cliente"] + df_clientes["nome_empresa"].tolist()
        sel_idx = 0
        if "cliente_sel_cad" in st.session_state and st.session_state["cliente_sel_cad"] in opcoes:
            sel_idx = opcoes.index(st.session_state["cliente_sel_cad"])

        cliente_menu = st.selectbox("🔍 Pesquisar ou Adicionar um Cliente:", opcoes, index=sel_idx, key="sel_cliente_menu_cad")
        st.session_state["cliente_sel_cad"] = cliente_menu

        if cliente_menu != "➕ Cadastrar Novo Cliente":
            modo_edicao = True
            c_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_menu]["id"].values[0])
            st.session_state["cliente_id_edicao"] = c_id
            dados_existentes = obter_dados_cliente_por_id(c_id)
            st.success(f"⚡ **Modo de Edição Ativo:** Editando a ficha da empresa **{cliente_menu}**.")
        else:
            st.session_state.pop("cliente_id_edicao", None)
            st.info("✨ **Novo Cadastro:** Preencha os campos abaixo para registrar um novo cliente na base.")
    else:
        st.warning("Nenhum cliente cadastrado ainda na base. Preencha o formulário abaixo para registrar o primeiro.")

    st.markdown("<br>", unsafe_allow_html=True)

    def v(campo, padrao=""):
        """Valor do cliente em modo edição, ou padrão."""
        if modo_edicao and dados_existentes:
            valor = dados_existentes.get(campo)
            return valor if valor is not None else padrao
        return padrao

    with st.form("form_cliente_gmb_completo"):
        sub_t1, sub_t2, sub_t3, sub_t4, sub_t5, sub_t6 = st.tabs([
            "🏢 Sobre & Ficha", "⏰ Horários & Status", "💵 Contrato & Mídias",
            "📞 Contato & Redes", "🛠️ Checklist", "📜 Histórico",
        ])

        with sub_t1:
            c1, c_esp1, c2 = st.columns([4.8, 0.4, 4.8])
            with c1:
                nome_empresa = st.text_input("Nome Comercial da Empresa *", value=v("nome_empresa"))
                responsavel = st.text_input("Nome do Responsável", value=v("responsavel"))

                val_dt_abertura = date.today()
                if modo_edicao and dados_existentes and dados_existentes.get("data_abertura"):
                    try:
                        val_dt_abertura = datetime.strptime(dados_existentes["data_abertura"], "%d/%m/%Y").date()
                    except ValueError:
                        pass
                data_abertura_dt = st.date_input("Data de Abertura (Ficha GMB)", value=val_dt_abertura, format="DD/MM/YYYY")
                data_abertura_str = data_abertura_dt.strftime("%d/%m/%Y")

                atende_sem_endereco = st.checkbox(
                    "Prestador de Serviço sem Endereço Fixo (Área de Cobertura / SAB)",
                    value=bool(v("atende_sem_endereco", False)),
                )
                endereco_local = st.text_input("Endereço Físico (ou Fiscal/Origem se sem local)", value=v("endereco_local"))

            with c2:
                categoria_principal = st.text_input("Categoria Principal no GMB", value=v("categoria_principal"))
                categorias_secundarias = st.text_input("Categorias Secundárias", value=v("categorias_secundarias"))
                area_cobertura = st.text_input("Área de Cobertura / Regiões Atendidas", value=v("area_cobertura"))

            descricao_empresa = st.text_area("Descrição Oficial da Empresa", value=v("descricao_empresa"), height=90)

        with sub_t2:
            st.markdown("**Configurações de Reivindicação, Chat e Horários:**")
            c_s1, c_esp2, c_s2 = st.columns([4.8, 0.4, 4.8])
            opts_reivindicada = ["Reivindicada & Verificada", "Não Reivindicada", "Em Processo"]
            v_reiv = v("ficha_reivindicada")
            idx_reiv = opts_reivindicada.index(v_reiv) if v_reiv in opts_reivindicada else 0

            opts_chat = ["Ativado", "Desativado", "Não Configurado"]
            chat_val = v("chat_status", "Ativado")
            idx_chat = opts_chat.index(chat_val) if chat_val in opts_chat else 0

            with c_s1:
                ficha_reivindicada = st.radio("Status de Reivindicação da Ficha", opts_reivindicada, index=idx_reiv, horizontal=True)
            with c_s2:
                chat_status = st.radio("Status do Chat / Mensagens no Perfil", opts_chat, index=idx_chat, horizontal=True)

            st.markdown("---")
            st.markdown("**Horários de Funcionamento Rápidos:**")
            dias_semana = [
                ("Segunda-feira", "horario_seg", "08:00", "18:00", False),
                ("Terça-feira", "horario_ter", "08:00", "18:00", False),
                ("Quarta-feira", "horario_qua", "08:00", "18:00", False),
                ("Quinta-feira", "horario_qui", "08:00", "18:00", False),
                ("Sexta-feira", "horario_sex", "08:00", "18:00", False),
                ("Sábado", "horario_sab", "08:00", "12:00", False),
                ("Domingo", "horario_dom", "08:00", "12:00", True),
            ]
            horarios_coletados = {}
            for dia_nome, campo_db, h_ab_def, h_fe_def, fechado_def in dias_semana:
                is_f = fechado_def
                v_ab, v_fe = h_ab_def, h_fe_def
                txt_h = v(campo_db)
                if txt_h:
                    if txt_h == "Fechado":
                        is_f = True
                    elif " - " in txt_h:
                        is_f = False
                        parts = txt_h.split(" - ")
                        if len(parts) == 2:
                            v_ab, v_fe = parts[0], parts[1]

                cd, ca, cf, cc = st.columns([2.2, 2.2, 2.2, 1.4])
                with cd:
                    st.markdown(f"📅 **{dia_nome}**")
                with ca:
                    ha = st.text_input(f"Abre {dia_nome}", value=v_ab, label_visibility="collapsed", disabled=is_f, key=f"ab_{dia_nome}")
                with cf:
                    hf = st.text_input(f"Fecha {dia_nome}", value=v_fe, label_visibility="collapsed", disabled=is_f, key=f"fe_{dia_nome}")
                with cc:
                    fch = st.checkbox("Fechado", value=is_f, key=f"chk_{dia_nome}")
                horarios_coletados[campo_db] = "Fechado" if fch else f"{ha} - {hf}"

        with sub_t3:
            valor_contrato_mensal = st.number_input(
                "Valor da Mensalidade (R$)", min_value=0.0, step=50.0,
                value=float(v("valor_contrato_mensal", 450.0)),
            )
            dia_vencimento = st.number_input(
                "Dia Vencimento", min_value=1, max_value=31, step=1,
                value=int(v("dia_vencimento", 10)),
            )

            opts_status = ["Ativo", "Em Negociação", "Pausado", "Cancelado"]
            val_status_atual = v("status_contrato", "Ativo")
            idx_st = opts_status.index(val_status_atual) if val_status_atual in opts_status else 0
            status_contrato = st.selectbox("Status do Contrato", opts_status, index=idx_st)

            link_drive_midias = st.text_input("Link da Pasta de Mídias e Fotos 360° (Google Drive)", value=v("link_drive_midias"))

        with sub_t4:
            c1, c_esp3, c2 = st.columns([4.8, 0.4, 4.8])
            with c1:
                telefone_contato = st.text_input("Telefone Comercial", value=v("telefone_contato"))
                whatsapp = st.text_input("WhatsApp para Envio (Ex: 16991332121)", value=v("whatsapp"))
                website = st.text_input("Website / Link Principal", value=v("website"))
            with c2:
                instagram = st.text_input("Instagram", value=v("instagram"))
                facebook = st.text_input("Facebook", value=v("facebook"))
                linkedin = st.text_input("LinkedIn", value=v("linkedin"))
                youtube = st.text_input("YouTube", value=v("youtube"))
                tiktok = st.text_input("TikTok", value=v("tiktok"))

        with sub_t5:
            st.markdown("**Checklist de Otimização Identificadas no Diagnóstico:**")
            pendencias_salvas = v("pendencias_checklist")
            c_p1, c_esp4, c_p2 = st.columns([4.8, 0.4, 4.8])
            with c_p1:
                p_fita = st.checkbox("📷 Tour Virtual 360° & Fotos", value="Fotos/Tour 360°" in pendencias_salvas)
                p_cat = st.checkbox("🏷️ Otimizar Categorias GMB", value="Categorias GMB" in pendencias_salvas)
                p_desc = st.checkbox("✍️ Descrição SEO Local", value="Descrição SEO" in pendencias_salvas)
                p_redes = st.checkbox("🔗 Vincular Redes Sociais", value="Redes Sociais" in pendencias_salvas)
            with c_p2:
                p_chat = st.checkbox("💬 Ativar Chat / Mensagens", value="Chat/Mensagens" in pendencias_salvas)
                p_prod = st.checkbox("🛍️ Cadastrar Produtos/Serviços", value="Produtos/Serviços" in pendencias_salvas)
                p_aval = st.checkbox("⭐ Link Curto de Avaliações", value="Link de Avaliações" in pendencias_salvas)
                p_hor = st.checkbox("⏰ Validar Horários", value="Ajuste de Horários" in pendencias_salvas)

            observacoes_tecnicas = st.text_area("Observações Técnicas Adicionais", value=v("observacoes_tecnicas"), height=90)

        with sub_t6:
            if not modo_edicao:
                st.info("Histórico disponível após o primeiro salvamento.")
            else:
                st.markdown(f"**Histórico de Registros — {cliente_menu}:**")
                res_h = (
                    supabase.table("historico_ficha")
                    .select("data_alteracao, descricao_alteracao")
                    .eq("cliente_id", c_id)
                    .order("id", desc=True)
                    .execute()
                )
                if res_h.data:
                    df_hist = pd.DataFrame(res_h.data)
                    df_hist.columns = ["Data (São Paulo)", "Alteração Realizada"]
                    st.dataframe(df_hist)

        st.markdown("---")
        btn_salvar = st.form_submit_button("Salvar Nova Ficha" if not modo_edicao else "Atualizar Ficha e Gravar Histórico")

        if btn_salvar and nome_empresa:
            checklist_list = []
            if p_fita: checklist_list.append("Fotos/Tour 360°")
            if p_cat: checklist_list.append("Categorias GMB")
            if p_desc: checklist_list.append("Descrição SEO")
            if p_redes: checklist_list.append("Redes Sociais")
            if p_chat: checklist_list.append("Chat/Mensagens")
            if p_prod: checklist_list.append("Produtos/Serviços")
            if p_aval: checklist_list.append("Link de Avaliações")
            if p_hor: checklist_list.append("Ajuste de Horários")
            pendencias_str = ", ".join(checklist_list) if checklist_list else "Nenhuma pendência"

            payload = {
                "nome_empresa": nome_empresa, "responsavel": responsavel, "data_abertura": data_abertura_str,
                "ficha_reivindicada": ficha_reivindicada, "chat_status": chat_status,
                "categoria_principal": categoria_principal, "categorias_secundarias": categorias_secundarias,
                "area_cobertura": area_cobertura, "atende_sem_endereco": atende_sem_endereco,
                "descricao_empresa": descricao_empresa,
                "valor_contrato_mensal": valor_contrato_mensal, "dia_vencimento": dia_vencimento,
                "status_contrato": status_contrato, "link_drive_midias": link_drive_midias,
                "telefone_contato": telefone_contato, "whatsapp": whatsapp, "website": website,
                "instagram": instagram, "facebook": facebook, "linkedin": linkedin, "youtube": youtube, "tiktok": tiktok,
                "endereco_local": endereco_local, "pendencias_checklist": pendencias_str,
                "observacoes_tecnicas": observacoes_tecnicas,
                "horario_seg": horarios_coletados["horario_seg"], "horario_ter": horarios_coletados["horario_ter"],
                "horario_qua": horarios_coletados["horario_qua"], "horario_qui": horarios_coletados["horario_qui"],
                "horario_sex": horarios_coletados["horario_sex"], "horario_sab": horarios_coletados["horario_sab"],
                "horario_dom": horarios_coletados["horario_dom"],
            }
            try:
                data_hora_sp = agora_brasil().strftime("%Y-%m-%d %H:%M")
                if not modo_edicao:
                    payload["data_inicio"] = agora_brasil().strftime("%Y-%m-%d")
                    res_ins = supabase.table("clientes").insert(payload).execute()
                    if res_ins.data:
                        novo_id = res_ins.data[0]["id"]
                        supabase.table("historico_ficha").insert({
                            "cliente_id": novo_id, "data_alteracao": data_hora_sp,
                            "descricao_alteracao": "Cadastro Inicial",
                        }).execute()
                        st.success(f"Ficha de '{nome_empresa}' cadastrada com sucesso! Atualize a página para ver a lista.")
                else:
                    supabase.table("clientes").update(payload).eq("id", c_id).execute()
                    supabase.table("historico_ficha").insert({
                        "cliente_id": c_id, "data_alteracao": data_hora_sp,
                        "descricao_alteracao": "Atualização Cadastral",
                    }).execute()
                    st.success(f"Ficha comercial de '{nome_empresa}' atualizada com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")

    if modo_edicao and dados_existentes:
        st.markdown("<br>", unsafe_allow_html=True)
        section_title("🖨️ Gerador de QR Code de Avaliações")
        link_maps_qr = dados_existentes.get("website", "") or "https://g.page/r/..."
        link_qr_input = st.text_input(
            "Link Direto de Avaliações (Basta colar a URL do Google Maps):",
            value=link_maps_qr, key="input_url_qr_gerador",
        )
        if link_qr_input:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(link_qr_input)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            buf_qr = BytesIO()
            img_qr.save(buf_qr, format="PNG")
            buf_qr.seek(0)
            st.image(buf_qr, width=180, caption=f"QR Code Oficial - {cliente_menu}")
            st.download_button(
                "📥 Baixar Imagem QR Code",
                data=buf_qr,
                file_name=f"QRCode_Avaliacoes_{cliente_menu}.png",
                mime="image/png",
                key="btn_download_qr_code_safe",
            )

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 2: AUDITORIA
# ==========================================
elif st.session_state["aba_ativa"] == "auditoria":
    section_title("🔍 Auditoria Detalhada de Pontos de Busca (9 Critérios Oficiais)")
    url_prospect = st.text_input(
        "URL ou Nome da Empresa no Google Maps:",
        placeholder="https://maps.google.com/... ou Nome da Empresa",
    )

    if st.button("⚡ Executar Varredura Rigorosa (API Google)"):
        if url_prospect:
            with st.spinner("Analisando os 9 critérios da ficha na Google Places API..."):
                res_aud, err = auditar_ficha_google_rigorosa(url_prospect)
            if err:
                st.error(err)
            else:
                st.session_state["ultima_auditoria"] = res_aud
                try:
                    salvar_auditoria_historico(res_aud)
                except Exception:
                    st.warning("Auditoria concluída, mas não foi possível salvar no histórico (verifique a tabela 'auditorias').")
        else:
            st.warning("Insira uma URL ou o nome da empresa.")

    if "ultima_auditoria" in st.session_state:
        res_aud = st.session_state["ultima_auditoria"]
        with glass_container():
            st.markdown(f"### 🏢 {res_aud['nome']}")
            st.markdown(f"📍 **Endereço:** {res_aud['endereco']} | 📞 **Tel:** {res_aud['telefone']}")

            score = res_aud["score"]
            if score >= 75:
                st.success(f"⭐ **Score da Ficha: {score}/100** (Excelente otimização)")
            elif score >= 40:
                st.warning(f"⚠️ **Score da Ficha: {score}/100** (Requer otimizações)")
            else:
                st.error(f"❌ **Score da Ficha: {score}/100** (Crítico / Alto Potencial de Consultoria)")
            st.caption("Metodologia: score de 0 a 100 calculado sobre os critérios automáticos (fotos -10, horários -10, website -15, avaliações -15, resumo -10). Itens marcados como Verificação manual não pontuam.")

        section_title("📋 Auditoria Detalhada de Pontos (9 Critérios)")
        dados_tabela_ui = [
            {"Critério": item, "Diagnóstico Técnico": estado, "Impacto Local": impacto, "Status": status}
            for item, estado, impacto, status in res_aud["criterios"]
        ]
        st.dataframe(pd.DataFrame(dados_tabela_ui))

        section_title("🚀 Plano de Ação & Oportunidades Recomendadas:")
        st.markdown("- **1. Atração Local (SEO):** Correção cadastral e otimização das categorias principal e secundárias.")
        st.markdown("- **2. Segurança & Posicionamento:** Frequência de atualização para sinalizar ao Google que o perfil está ativo.")
        st.markdown("- **3. Confiança & Autoridade:** Publicação do Tour Virtual 360° no Street View e fotos em alta resolução.")
        st.markdown("- **4. Vitrine Imersiva:** Padronização do acervo visual e integração dos canais de contato direto.")

        st.markdown("---")
        col_pdf, col_db = st.columns(2)

        with col_pdf:
            pdf_aud_bytes = gerar_pdf_auditoria(res_aud)
            st.download_button(
                "📥 Baixar Relatório de Auditoria em PDF",
                data=pdf_aud_bytes,
                file_name=f"Diagnostico Auditoria Google Maps {res_aud['nome']}.pdf",
                mime="application/pdf",
                key="btn_download_auditoria_pdf",
            )

        with col_db:
            if st.button("💾 Salvar Ficha na Base de Clientes (Supabase)"):
                try:
                    payload_novo = {
                        "nome_empresa": res_aud["nome"],
                        "endereco_local": res_aud["endereco"],
                        "telefone_contato": res_aud["telefone"],
                        "website": res_aud["website"] if res_aud["website"] != "Não informado" else "",
                        "status_contrato": "Em Negociação",
                        "valor_contrato_mensal": 450.0,
                        "observacoes_tecnicas": f"Score de Auditoria: {res_aud['score']}/100.",
                    }
                    supabase.table("clientes").insert(payload_novo).execute()
                    st.success(f"Empresa '{res_aud['nome']}' salva com sucesso na aba 'Ficha Comercial'!")
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {str(e)}")

        with st.expander("🕓 Histórico de auditorias desta ficha"):
            df_hist_aud = listar_historico_auditorias(res_aud["nome"])
            if df_hist_aud.empty:
                st.caption("Nenhuma auditoria anterior registrada.")
            else:
                st.dataframe(df_hist_aud)
                st.download_button(
                    "📥 Exportar histórico (CSV)",
                    data=csv_bytes(df_hist_aud),
                    file_name=f"historico_auditorias_{res_aud['nome']}.csv",
                    mime="text/csv",
                    key="btn_csv_hist_aud",
                )

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 3: MÉTRICAS & SEO
# ==========================================
elif st.session_state["aba_ativa"] == "metricas":
    section_title("📋 Métricas Mensais, SEO Local & ROI")
    df_clientes = obter_clientes_unicos()
    if df_clientes.empty:
        st.warning("Cadastre um cliente primeiro.")
    else:
        cliente_sel = st.selectbox("Cliente:", df_clientes["nome_empresa"].tolist())
        c_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_sel]["id"].values[0])
        with st.form("form_met"):
            mes_ref = st.date_input("Mês Referência", value=datetime.today()).strftime("%Y-%m")
            c1, c_esp_m, c2 = st.columns([4.8, 0.4, 4.8])
            with c1:
                chamadas = st.number_input("Chamadas", min_value=0, step=1)
                rotas = st.number_input("Rotas", min_value=0, step=1)
            with c2:
                cliques = st.number_input("Cliques Site", min_value=0, step=1)
                tm = st.number_input("Ticket Médio (R$)", value=150.0, step=10.0)
            tc = st.number_input("Taxa Conversão (%)", value=10.0, step=1.0) / 100.0
            fat = (chamadas + rotas + cliques) * tc * tm
            st.info(f"Faturamento estimado: R$ {fat:,.2f}. Fórmula: (chamadas + rotas + cliques) × taxa de conversão × ticket médio. Valor indicativo, não é receita comprovada.")
            if st.form_submit_button("Salvar Métricas"):
                supabase.table("metricas_mensais").insert({
                    "cliente_id": c_id, "mes_ano": mes_ref, "chamadas": chamadas, "rotas": rotas,
                    "cliques_site": cliques, "ticket_medio": tm, "taxa_conversao": tc,
                    "faturamento_estimado": fat,
                }).execute()
                st.success("Métricas salvas! Atualize a página para ver os dados.")

        section_title("🔗 Gerador de Link UTM (rastrear cliques vindos do site)")
        with glass_container():
            utm_site = st.text_input("URL do site do cliente:", value="https://", key="utm_site")
            utm_campanha = st.text_input("Campanha (ex: google-maps-junho):", value="google-maps", key="utm_campanha")
            if utm_site and utm_site != "https://":
                sep = "&" if "?" in utm_site else "?"
                link_utm = f"{utm_site}{sep}utm_source=google&utm_medium=maps&utm_campaign={urllib.parse.quote(utm_campanha)}"
                st.code(link_utm, language=None)

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 4: CURADORIA & PAUTAS
# ==========================================
elif st.session_state["aba_ativa"] == "ia":
    section_title("🎯 Curadoria Enterprise & Pautas Editáveis")
    df_clientes = obter_clientes_unicos()

    if df_clientes.empty:
        st.info("Cadastre um cliente para acessar a curadoria.")
    else:
        cliente_ia = st.selectbox("Selecione o Cliente:", df_clientes["nome_empresa"].tolist())
        c_ia_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_ia]["id"].values[0])
        dados_c = obter_dados_cliente_por_id(c_ia_id)

        cat = dados_c.get("categoria_principal") or "serviços locais"
        reg = dados_c.get("area_cobertura") or "região"
        emp = dados_c.get("nome_empresa")
        resp_cliente = dados_c.get("responsavel") or emp

        st.markdown(f"**Banco Amplo de Pautas Inteligentes — Segmento: {cat} ({reg})**")

        pautas_sugeridas = [
            f"Como escolher o melhor serviço de {cat} em {reg}?",
            f"Bastidores da equipe da {emp}: Nosso compromisso com a excelência.",
            f"Conheça a estrutura imersiva da {emp} através do nosso Tour Virtual 360°.",
            f"Diferenciais técnicos que tornam a {emp} referência absoluta na região.",
            f"Atendimento rápido, orçamentos e facilidades pelo canal de atendimento da {emp}.",
            f"Erros comuns ao contratar serviços de {cat} e como evitar na prática.",
            f"Depoimentos, casos de sucesso e histórias de clientes atendidos pela {emp}.",
            f"Por que o atendimento especializado em {cat} faz toda a diferença para você?",
            f"Novidades, melhorias e atualizações nos serviços prestados pela {emp}.",
            f"Perguntas frequentes (FAQ): Tire todas as suas dúvidas sobre {cat} com a {emp}.",
            f"Quanto custa {cat} em {reg}? Fatores que definem o investimento.",
            f"Passo a passo: como preparar sua visita antes de contratar {cat}.",
            f"Tour Virtual 360° no Google Maps: como a {emp} aparece antes mesmo da visita.",
            f"Sinais de confiança: o que avaliar em um fornecedor de {cat}.",
            f"Sazonalidade: quando procurar {cat} em {reg} e como se planejar.",
            f"Mitos e verdades sobre {cat} na região.",
        ]

        section_title("Selecione e Personalize as Pautas do Mês:")
        pautas_selecionadas = []
        with glass_container():
            for idx, p_text in enumerate(pautas_sugeridas, 1):
                col_chk, col_txt = st.columns([0.1, 0.9])
                with col_chk:
                    ativo = st.checkbox(
                        f"Ativar pauta {idx}",
                        value=(idx <= 6),
                        key=f"chk_pauta_{idx}",
                        label_visibility="collapsed",
                    )
                with col_txt:
                    p_editada = st.text_input(
                        f"Pauta {idx}", value=p_text, key=f"txt_pauta_{idx}", label_visibility="collapsed",
                    )
                if ativo:
                    pautas_selecionadas.append(p_editada)

        section_title("✅ Otimizações Recomendadas para a Ficha")
        with glass_container():
            st.markdown(
                "- **Respostas às avaliações:** responder todas em até 48h, inclusive as negativas, com palavras-chave do segmento.\n"
                "- **Posts semanais no Perfil:** novidades, ofertas e eventos com foto e chamada para ação.\n"
                "- **Fotos reais em alta resolução:** atualizar o acervo mensalmente e incluir equipe e bastidores.\n"
                "- **Produtos e serviços:** cadastrar cada item com descrição e preço de referência.\n"
                "- **Perguntas e respostas (Q&A):** publicar as dúvidas frequentes respondidas pela própria empresa.\n"
                "- **Categorias:** revisar a principal e as secundárias a cada trimestre.\n"
                "- **Horários especiais:** cadastrar feriados e datas sazonais com antecedência.\n"
                "- **Rastreamento de links:** usar UTM no site para medir cliques e conversões reais.\n"
                "- **Link curto de avaliações:** com QR Code no balcão e na área de atendimento."
            )

        st.markdown("---")
        section_title("🔗 Link Único de Aprovação Externa (Copie e envie ao cliente)")
        link_exemplo = f"https://gestao-mensal-tour360vr.streamlit.app/?aprovar=true&cliente={emp.lower().replace(' ', '-')}"
        st.code(link_exemplo, language=None)

        num_wsp = dados_c.get("whatsapp", "")
        num_limpo = "".join([c for c in str(num_wsp) if c.isdigit()])

        texto_msg_wsp = (
            f"Olá {resp_cliente}!\nAqui é o Rubens da Tour360VR.\n"
            f"Segue o link com o planejamento de pautas estratégicas para sua aprovação este mês: {link_exemplo}"
        )
        msg_wsp = urllib.parse.quote(texto_msg_wsp)

        if num_limpo:
            botao_whatsapp(f"https://wa.me/55{num_limpo}?text={msg_wsp}", "Enviar para o WhatsApp do cliente")
        else:
            st.warning("Cadastre o WhatsApp do cliente na aba 'Ficha Comercial' para habilitar o botão de envio direto.")

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 5: DASHBOARD & ROI
# ==========================================
elif st.session_state["aba_ativa"] == "dashboard":
    section_title("📊 Dashboard Executivo & ROI")
    df_clientes = obter_clientes_unicos()
    if not df_clientes.empty:
        c_dash = st.selectbox("Cliente:", df_clientes["nome_empresa"].tolist())
        c_id_d = int(df_clientes[df_clientes["nome_empresa"] == c_dash]["id"].values[0])
        res_m = supabase.table("metricas_mensais").select("*").eq("cliente_id", c_id_d).order("mes_ano").execute()
        if res_m.data:
            df_m = pd.DataFrame(res_m.data)

            col1, col2, col3 = st.columns(3)
            with col1:
                kpi_card("Chamadas (total)", f"{int(df_m['chamadas'].sum()):,}".replace(",", "."), accent=COLORS["accent"])
            with col2:
                kpi_card("Rotas GPS (total)", f"{int(df_m['rotas'].sum()):,}".replace(",", "."), accent=COLORS["success"])
            with col3:
                kpi_card("Cliques no Site (total)", f"{int(df_m['cliques_site'].sum()):,}".replace(",", "."), accent=COLORS["accent_2"])

            st.markdown("<br>", unsafe_allow_html=True)
            with glass_container():
                st.line_chart(df_m.set_index("mes_ano")[["chamadas", "rotas", "cliques_site"]])
            st.download_button(
                "📥 Exportar métricas (CSV)",
                data=csv_bytes(df_m),
                file_name=f"metricas_{c_dash}.csv",
                mime="text/csv",
                key="btn_csv_metricas",
            )
        else:
            st.info("Sem métricas cadastradas.")
    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 6: PROSPECÇÃO
# ==========================================
elif st.session_state["aba_ativa"] == "cases":
    section_title("🏆 Gerador de Relatório Comercial de Prospecção")
    st.info("Módulo ativo com banco consolidado de cases da agência.")
    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 7: RELATÓRIO PDF & CONTRATO
# ==========================================
elif st.session_state["aba_ativa"] == "pdf":
    section_title("📄 Emissão de Relatório Executivo & Minuta de Contrato em PDF")
    df_clientes = obter_clientes_unicos()
    if df_clientes.empty:
        st.warning("Cadastre um cliente primeiro.")
    else:
        c_pdf = st.selectbox("Cliente:", df_clientes["nome_empresa"].tolist())
        c_id_p = int(df_clientes[df_clientes["nome_empresa"] == c_pdf]["id"].values[0])
        dados_cli = obter_dados_cliente_por_id(c_id_p)

        tab_pdf1, tab_pdf2 = st.tabs(["📄 Relatório Executivo PDF", "📜 Contrato Jurídico Oficial"])

        with tab_pdf1:
            res_m = supabase.table("metricas_mensais").select("*").eq("cliente_id", c_id_p).order("mes_ano").execute()
            if res_m.data:
                df_m = pd.DataFrame(res_m.data)
                mes_sel = st.selectbox("Mês Referência:", df_m["mes_ano"].tolist()[::-1])
                idx = df_m[df_m["mes_ano"] == mes_sel].index[0]
                d_atual = df_m.iloc[idx].to_dict()
                d_ant = df_m.iloc[idx - 1].to_dict() if idx - 1 >= 0 else None

                pdf_bytes = gerar_pdf_relatorio(
                    c_pdf, mes_sel, d_atual, d_ant,
                    {"qtd_avaliacoes_inicio": 0, "nota_media_inicio": 5.0, "qtd_fotos_inicio": 0},
                    df_m.iloc[: idx + 1],
                )
                st.download_button(
                    "📥 Baixar Relatório Executivo PDF",
                    data=pdf_bytes,
                    file_name=f"Relatorio_{c_pdf}_{mes_sel}.pdf",
                    mime="application/pdf",
                )
            else:
                st.info("Sem métricas cadastradas para gerar o relatório.")

        with tab_pdf2:
            st.markdown("**Gerador Automático da Minuta de Contrato Jurídico:**")

            plano_selecionado = st.selectbox("Selecione o Plano:", ["Plano Start", "Plano Pro", "Gestão Mensal"])

            meses_gestao = None
            if "Gestão Mensal" in plano_selecionado:
                meses_gestao = st.slider("Duração do Contrato (Meses):", min_value=3, max_value=12, value=6, step=1)

            valor_padrao = 500.0 if "Start" in plano_selecionado else (1500.0 if "Pro" in plano_selecionado else 600.0)
            valor_personalizado = st.number_input("Valor do Plano (R$)", min_value=0.0, step=50.0, value=valor_padrao)

            if st.button("Gerar Contrato Oficial em PDF"):
                pdf_contrato = gerar_pdf_contrato(dados_cli, plano_selecionado, valor_personalizado, meses_gestao)
                data_str_file = agora_brasil().strftime("%Y-%m-%d")
                nome_arquivo_pdf = f"Contrato Tour360VR - {c_pdf} - {data_str_file}.pdf"
                st.download_button(
                    "📥 Baixar Contrato Oficial PDF",
                    data=pdf_contrato,
                    file_name=nome_arquivo_pdf,
                    mime="application/pdf",
                )

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 8: FINANCEIRO & MRR
# ==========================================
elif st.session_state["aba_ativa"] == "financeiro":
    section_title("💰 Gestão Financeira MRR & Alertas")
    res_cli = supabase.table("clientes").select("*").execute()
    df_c = pd.DataFrame(res_cli.data) if res_cli.data else pd.DataFrame()
    if not df_c.empty:
        ativos = df_c[df_c["status_contrato"] == "Ativo"]
        mrr = ativos["valor_contrato_mensal"].sum()
        qtd_ativos = len(ativos)
        qtd_pend = int((df_c["status_contrato"] == "Pausado").sum())

        col1, col2, col3 = st.columns(3)
        with col1:
            kpi_card("MRR Total da Agência", formatar_brl(mrr), accent=COLORS["success"])
        with col2:
            kpi_card("Clientes Ativos", str(qtd_ativos), accent=COLORS["accent"])
        with col3:
            kpi_card("Contratos Pausados", str(qtd_pend), accent=COLORS["warning"])

        st.markdown("<br>", unsafe_allow_html=True)

        section_title("🔔 Lembretes de Vencimento (WhatsApp, sem API paga)")
        ativos_lembrete = ativos.sort_values("dia_vencimento") if "dia_vencimento" in ativos else ativos
        for _, row in ativos_lembrete.iterrows():
            num = "".join(c for c in str(row.get("whatsapp", "") or "") if c.isdigit())
            if not num:
                continue
            msg = (
                f"Olá {row.get('responsavel') or row.get('nome_empresa')}! Tudo bem? "
                f"Passando para lembrar do vencimento da mensalidade no dia {row.get('dia_vencimento')}, "
                f"no valor de {formatar_brl(float(row.get('valor_contrato_mensal') or 0))}. Obrigado!"
            )
            with glass_container():
                st.markdown(f"**{row['nome_empresa']}** · vencimento dia {row.get('dia_vencimento')}")
                botao_whatsapp(f"https://wa.me/55{num}?text={urllib.parse.quote(msg)}", "Enviar lembrete no WhatsApp")

        section_title("Lista de Clientes e Contratos Recorrentes")
        st.download_button(
            "📥 Exportar clientes (CSV)",
            data=csv_bytes(df_c),
            file_name="clientes_tour360vr.csv",
            mime="text/csv",
            key="btn_csv_clientes",
        )
        st.dataframe(df_c, height=650)
    gerar_botoes_navegacao_rodape()

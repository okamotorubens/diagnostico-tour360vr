import datetime
import requests
import streamlit as st
from fpdf import FPDF

st.set_page_config(
    page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered"
)

st.title("📍 Gerador de Diagnóstico")
st.subheader("Google Meu Negócio - Tour360vr")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    api_key = st.text_input("Digite sua Chave da API Google (Places API):", type="password")

with st.form("form_busca"):
    col1, col2 = st.columns([3, 2])
    with col1:
        empresa = st.text_input("Nome da Empresa:", placeholder="Ex: Amazone Açaí Shop")
    with col2:
        cidade = st.text_input("Cidade / Estado:", placeholder="Ex: Brodowski / SP")
    
    btn = st.form_submit_button("Gerar Relatório Executivo em PDF")


def clean_txt(txt):
    if not txt: return ""
    return str(txt).encode("latin-1", "replace").decode("latin-1")


def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()
    if not res.get("results"): return None
    result = res["results"][0]
    place_id = result["place_id"]
    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,opening_hours,types&key={key}"
    details = requests.get(url_details).json().get("result", {})
    return details


def calcular_score_critico(dados):
    score = 25
    if dados.get("website"): score += 15
    photos_count = len(dados.get("photos", []))
    if photos_count >= 25: score += 20
    elif photos_count >= 10: score += 10
    elif photos_count >= 5: score += 5
    try: rating = float(dados.get("rating", 0))
    except (ValueError, TypeError): rating = 0.0
    if rating >= 4.7: score += 15
    elif rating >= 4.3: score += 10
    elif rating >= 4.0: score += 5
    reviews = dados.get("user_ratings_total", 0)
    if reviews >= 150: score += 15
    elif reviews >= 50: score += 10
    elif reviews >= 15: score += 5
    if dados.get("opening_hours"): score += 10
    return min(max(score, 30), 85)


class PDFExecutivo(FPDF):
    def header(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 0, 210, 28, "F")
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 5)
        self.cell(0, 8, clean_txt("Tour360vr"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(186, 230, 253)
        self.set_y(16)
        self.cell(0, 4, clean_txt("DIAGNÓSTICO E AUDITORIA GOOGLE MEU NEGÓCIO"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(224, 242, 254)
        self.set_xy(130, 20)
        self.cell(70, 5, clean_txt(datetime.date.today().strftime('%d/%m/%Y')), align="R")
        self.set_y(32)

    def footer(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 285, 210, 12, "F")
        self.set_y(-8.5)
        self.set_font("Helvetica", "B", 8.5)
        self.set_x(20.5)
        self.set_text_color(224, 242, 254)
        self.cell(44, 5, clean_txt("contato@tour360vr.com.br"), align="C", link="mailto:contato@tour360vr.com.br")
        self.set_text_color(255, 255, 255)
        self.cell(4, 5, clean_txt("·"), align="C")
        self.set_text_color(224, 242, 254)
        self.cell(25, 5, clean_txt("16991332121"), align="C", link="https://wa.me/5516991332121")
        self.set_text_color(255, 255, 255)
        self.cell(4, 5, clean_txt("·"), align="C")
        self.set_text_color(224, 242, 254)
        self.cell(33, 5, clean_txt("tour360vr.com.br"), align="C", link="https://tour360vr.com.br/")
        self.set_text_color(255, 255, 255)
        self.cell(4, 5, clean_txt("·"), align="C")
        self.cell(34, 5, clean_txt("Ribeirão Preto - SP"), align="C")


def desenhar_estrelas_destaque(pdf, x_start, y_pos, rating_val):
    try:
        rating_num = round(float(rating_val))
    except (ValueError, TypeError):
        rating_num = 0
    pdf.set_font("Helvetica", "B", 22)
    for k in range(5):
        pdf.set_xy(x_start + (k * 7.5), y_pos)
        if k < rating_num:
            pdf.set_text_color(245, 158, 11)
            pdf.cell(7, 7, clean_txt("*"))
        else:
            pdf.set_text_color(203, 213, 225)
            pdf.cell(7, 7, clean_txt("-"))


def gerar_pdf_bytes(dados):
    pdf = PDFExecutivo()
    pdf.set_margins(10, 6, 10)
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    
    nome = dados.get("name", "N/A")
    endereco = dados.get("formatted_address", "N/A")
    telefone = dados.get("formatted_phone_number", "Não informado")
    rating_raw = dados.get("rating", 0.0)
    rating = str(rating_raw)
    reviews_count = dados.get("user_ratings_total", 0)
    reviews = str(reviews_count)
    photos_count = len(dados.get("photos", []))
    website = dados.get("website")
    has_hours = "Cadastrado" if dados.get("opening_hours") else "Ausente/Incompleto"
    score = calcular_score_critico(dados)
    W = pdf.epw

    # Quadro da Empresa
    y_empresa = pdf.get_y()
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(20, 50, 135)
    pdf.rect(10, y_empresa, W, 14, "DF")
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(13, y_empresa + 1.5)
    pdf.cell(0, 5, clean_txt(nome.upper()), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.set_x(13)
    pdf.cell(0, 4.2, clean_txt(f"Endereço: {endereco}  |  Telefone: {telefone}"), new_x="LMARGIN", new_y="NEXT")

    y_cards = y_empresa + 18
    w_card = 63.3
    h_card = 26.0

    # Cards
    boxes = [
        ("OTIMIZAÇÃO DO PERFIL", str(score), "/100", score, "Margem para crescimento local"),
        ("NOTA E REPUTAÇÃO", rating, " / 5.0", -1, f"Com base em {reviews} avaliações" if reviews_count >= 30 else f"Apenas {reviews} avaliações"),
        ("TOUR VIRTUAL 360°", "0", " FOTOS (AUSENTE)", -1, "Oportunidade de se diferenciar")
    ]
    for i, (title, val, label, sc, footer_txt) in enumerate(boxes):
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(20, 50, 135)
        pdf.rect(10 + (i * w_card), y_cards, w_card, h_card, "DF")
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(20, 50, 135)
        pdf.set_xy(12 + (i * w_card), y_cards + 2.0)
        pdf.cell(w_card - 4, 3.5, clean_txt(title))
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(249, 115, 22) if i != 2 else pdf.set_text_color(220, 38, 38)
        pdf.set_xy(12 + (i * w_card), y_cards + 6.0)
        pdf.cell(pdf.get_string_width(val) + 1, 6, val)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(20, 50, 135)
        pdf.cell(20, 6, clean_txt(label))
        if i == 1: desenhar_estrelas_destaque(pdf, 12 + (i * w_card), y_cards + 11.5, rating_raw)
        elif i == 0:
            pdf.set_fill_color(226, 232, 240)
            pdf.rect(12 + (i * w_card), y_cards + 13.5, w_card - 8, 3.2, "F")
            pdf.set_fill_color(20, 50, 135)
            pdf.rect(12 + (i * w_card), y_cards + 13.5, ((w_card - 8) * sc / 100), 3.2, "F")
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(100, 116, 139)
        pdf.set_xy(12 + (i * w_card), y_cards + 19.5)
        pdf.cell(w_card - 4, 3.5, clean_txt(footer_txt))

    pdf.set_y(y_cards + h_card + 4)
    # Matriz Diagnóstico
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 5.5, clean_txt("MATRIZ DE DIAGNÓSTICO E IMPACTO COMERCIAL"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_fill_color(20, 50, 135)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(42, 6, clean_txt(" Dimensão"), fill=True)
    pdf.cell(73, 6, clean_txt(" Estado Atual Identificado"), fill=True)
    pdf.cell(75, 6, clean_txt(" Impacto no Ranqueamento e Conversão"), fill=True, new_x="LMARGIN", new_y="NEXT")

    itens = [
        ("Completude do Cadastro", "Site cadastrado" if website else "Sem site próprio ou link de conversão cadastrado.", "Perfil incompleto reduz a conversão de novos clientes."),
        ("Nota e Avaliações", f"Nota {rating} baseada em {reviews} avaliações." if reviews_count >= 40 else f"Nota {rating} com apenas {reviews} avaliações.", "Reputação vulnerável; base pequena limita prova social."),
        ("Consistência de NAP", "Dados de endereço e telefone ativos.", "Informações corretas evitam perdas por buscas frustradas."),
        ("Categorias", "1 categoria cadastrada (Sem secundárias).", "Falta de categorias secundárias limita a visibilidade regional."),
        ("Fotos", f"Apenas {photos_count} fotos (Cobertura visual baixa).", "Poucas fotos impedem a avaliação do espaço."),
        ("Horários", f"Horários: {has_hours}.", "Informação correta evita perda de clientes."),
        ("Posts / Novidades", "Sem publicações recentes.", "Perfil estático não destaca ofertas nem novidades."),
        ("Recursos Interativos", "Sem tour virtual 360° interativo.", "Perdem-se conversões por falta de experiência imersiva 360.")
    ]

    for dim, est, imp in itens:
        y_curr = pdf.get_y()
        # Espaçamento de margem aumentada nas linhas
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(10, y_curr, W, 10, "F")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_xy(10, y_curr + 3)
        pdf.set_text_color(20, 50, 135)
        pdf.cell(42, 4, clean_txt(f" {dim}"))
        pdf.set_xy(52, y_curr + 3)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(73, 4, clean_txt(f" {est}"))
        pdf.set_xy(125, y_curr + 3)
        pdf.set_text_color(20, 50, 135)
        pdf.multi_cell(75, 4, clean_txt(imp))
        pdf.set_y(y_curr + 10)

    # Plano de Ação
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 5.5, clean_txt("PLANO DE AÇÃO RECOMENDADO"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)
    acoes = [
        ("1. TOUR VIRTUAL 360° INTERATIVO", "Mapeamento imersivo de alta definição para o Google Maps."),
        ("2. ENSAIO FOTOGRÁFICO PROFISSIONAL", "Fotografias profissionais das instalações e diferenciais."),
        ("3. OTIMIZAÇÃO SEO LOCAL & REPUTAÇÃO", "Reestruturação de palavras-chave e estratégia de avaliações.")
    ]
    for tit, desc in acoes:
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(20, 50, 135)
        pdf.rect(10, pdf.get_y(), W, 9, "DF")
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(20, 50, 135)
        pdf.set_xy(12, pdf.get_y() + 1.2)
        pdf.cell(0, 4, clean_txt(tit), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.set_x(12)
        pdf.cell(0, 4, clean_txt(desc), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # Frase Final
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 6, clean_txt("Pronto para elevar sua visibilidade?"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(W, 4.8, clean_txt("Vamos agendar uma visita, entender seus objetivos e montar um plano personalizado."), align="C")
    pdf.ln(1)
    pdf.multi_cell(W, 4.8, clean_txt("O Tour 360° + estratégia de avaliações pode triplicar suas buscas."), align="C")

    pdf.output("diagnostico_tour360vr.pdf")
    return "diagnostico_tour360vr.pdf"


if btn and empresa and cidade:
    if not api_key:
        st.error("Chave da API do Google não configurada nos Secrets.")
    else:
        with st.spinner("Analisando..."):
            dados = buscar_dados_google(empresa, cidade, api_key)
            if dados:
                pdf_file = gerar_pdf_bytes(dados)
                st.success("Diagnóstico gerado!")
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Baixar PDF", data=f, file_name="diagnostico.pdf", mime="application/pdf")
            else:
                st.error("Empresa não encontrada.")

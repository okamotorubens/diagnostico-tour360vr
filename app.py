import datetime
import requests
import streamlit as st
from fpdf import FPDF

st.set_page_config(
    page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered"
)

st.title("📍 Gerador de Diagnóstico Google Meu Negócio")
st.subheader("Padrão Executivo - Tour360vr")

# Recupera a chave dos Secrets do Streamlit Cloud
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    api_key = st.text_input(
        "Digite sua Chave da API Google (Places API):", type="password"
    )

with st.form("form_busca"):
    empresa = st.text_input(
        "Nome da Empresa:", placeholder="Ex: Amazone Açaí Shop"
    )
    cidade = st.text_input("Cidade / Estado:", placeholder="Ex: Brodowski / SP")
    btn = st.form_submit_button("Gerar Relatório Executivo em PDF")


def clean_txt(txt):
    """Trata caracteres acentuados mantendo compatibilidade com FPDF"""
    if not txt:
        return ""
    return str(txt).encode("latin-1", "replace").decode("latin-1")


def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()

    if not res.get("results"):
        return None

    result = res["results"][0]
    place_id = result["place_id"]

    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,opening_hours,types&key={key}"
    details = requests.get(url_details).json().get("result", {})

    return details


def calcular_score_critico(dados):
    """Calcula uma pontuação crítica e realista de otimização de perfil"""
    score = 25  # Base inicial rígida

    if dados.get("website"):
        score += 15

    photos_count = len(dados.get("photos", []))
    if photos_count >= 25:
        score += 20
    elif photos_count >= 10:
        score += 10
    elif photos_count >= 5:
        score += 5

    try:
        rating = float(dados.get("rating", 0))
    except (ValueError, TypeError):
        rating = 0.0

    if rating >= 4.7:
        score += 15
    elif rating >= 4.3:
        score += 10
    elif rating >= 4.0:
        score += 5

    reviews = dados.get("user_ratings_total", 0)
    if reviews >= 150:
        score += 15
    elif reviews >= 50:
        score += 10
    elif reviews >= 15:
        score += 5

    if dados.get("opening_hours"):
        score += 10

    return min(max(score, 30), 85)


class PDFExecutivo(FPDF):

    def header(self):
        # Tarja Azul #143287 (RGB: 20, 50, 135) - Altura 26mm
        self.set_fill_color(20, 50, 135)
        self.rect(0, 0, 210, 26, "F")

        # Título e Subtítulo Centralizados no Cabeçalho
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 5.5)
        self.cell(0, 6, clean_txt("TOUR360VR"), align="C", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(186, 230, 253)
        self.cell(0, 4, clean_txt("DIAGNÓSTICO E AUDITORIA GOOGLE MEU NEGÓCIO"), align="C", new_x="LMARGIN", new_y="NEXT")

        # Data alinhada no canto direito
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(224, 242, 254)
        self.set_xy(130, 18.5)
        self.cell(
            70,
            5,
            clean_txt(f"Data: {datetime.date.today().strftime('%d/%m/%Y')}"),
            align="R",
        )

        self.set_y(29)

    def footer(self):
        # Tarja Azul Fina no Rodapé #143287
        self.set_fill_color(20, 50, 135)
        self.rect(0, 285, 210, 12, "F")

        self.set_y(-9)
        self.set_font("Helvetica", "B", 8)

        self.set_x(12)

        self.set_text_color(255, 255, 255)
        self.cell(26, 5, clean_txt("Rubens Okamoto"), align="C")
        self.cell(4, 5, clean_txt(" · "), align="C")

        self.set_text_color(224, 242, 254)
        self.cell(41, 5, clean_txt("contato@tour360vr.com.br"), align="C", link="mailto:contato@tour360vr.com.br")

        self.set_text_color(255, 255, 255)
        self.cell(4, 5, clean_txt(" · "), align="C")

        self.set_text_color(224, 242, 254)
        self.cell(22, 5, clean_txt("16991332121"), align="C", link="https://wa.me/5516991332121")

        self.set_text_color(255, 255, 255)
        self.cell(4, 5, clean_txt(" · "), align="C")

        self.set_text_color(224, 242, 254)
        self.cell(28, 5, clean_txt("tour360vr.com.br"), align="C", link="https://tour360vr.com.br/")

        self.set_text_color(255, 255, 255)
        self.cell(4, 5, clean_txt(" · "), align="C")
        self.cell(32, 5, clean_txt("Ribeirão Preto - SP"), align="C")


def gerar_pdf_bytes(dados):
    pdf = PDFExecutivo()
    pdf.set_margins(10, 6, 10)
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    nome = dados.get("name", "N/A")
    endereco = dados.get("formatted_address", "N/A")
    telefone = dados.get("formatted_phone_number", "Não informado")
    rating = str(dados.get("rating", "0.0"))
    reviews_count = dados.get("user_ratings_total", 0)
    reviews = str(reviews_count)
    photos_count = len(dados.get("photos", []))
    website = dados.get("website")
    has_hours = "Cadastrado" if dados.get("opening_hours") else "Ausente/Incompleto"
    score = calcular_score_critico(dados)

    W = pdf.epw

    # Quadro da Empresa sem sobra de espaço abaixo (Altura reduzida para 14.5mm)
    y_empresa = pdf.get_y()
    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(20, 50, 135)
    pdf.rect(10, y_empresa, W, 14.5, "DF")

    pdf.set_font("Helvetica", "B", 12.5)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(13, y_empresa + 1.8)
    pdf.cell(0, 5, clean_txt(nome.upper()), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.set_x(13)
    pdf.cell(
        0,
        4.5,
        clean_txt(f"Endereço: {endereco}  |  Telefone: {telefone}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    # Início imediato dos quadros logo abaixo do bloco da empresa
    y_cards = y_empresa + 19.5

    # Box 1: Otimização do Perfil
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(20, 50, 135)
    pdf.rect(10, y_cards, 60, 24, "DF")

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(12, y_cards + 2)
    pdf.cell(56, 4, clean_txt("OTIMIZAÇÃO DO PERFIL"))

    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(249, 115, 22)
    pdf.set_xy(12, y_cards + 5.5)
    score_str = str(score)
    pdf.cell(pdf.get_string_width(score_str) + 1, 6, score_str)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(20, 6, "/100")

    pdf.set_fill_color(226, 232, 240)
    pdf.rect(12, y_cards + 13, 56, 3.5, "F")
    pdf.set_fill_color(20, 50, 135)
    pdf.rect(12, y_cards + 13, (56 * score / 100), 3.5, "F")

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.set_xy(12, y_cards + 17.5)
    pdf.cell(56, 4, clean_txt("Margem para crescimento local"))

    # Box 2: Nota e Reputação
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(75, y_cards, 60, 24, "DF")

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(77, y_cards + 2)
    pdf.cell(56, 4, clean_txt("NOTA E REPUTAÇÃO"))

    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(249, 115, 22)
    pdf.set_xy(77, y_cards + 5.5)
    pdf.cell(pdf.get_string_width(rating) + 1, 6, rating)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(20, 6, " / 5.0")

    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(77, y_cards + 14.5)
    if reviews_count < 30:
        pdf.cell(56, 4, clean_txt(f"Apenas {reviews} avaliações (Base pequena)"))
    else:
        pdf.cell(56, 4, clean_txt(f"Com base em {reviews} avaliações"))

    # Box 3: Tour Virtual 360°
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(20, 50, 135)
    pdf.rect(140, y_cards, 60, 24, "DF")

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(142, y_cards + 2)
    pdf.cell(56, 4, clean_txt("TOUR VIRTUAL 360°"))

    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(220, 38, 38)
    pdf.set_xy(142, y_cards + 5.5)
    txt_zero = "0"
    pdf.cell(pdf.get_string_width(txt_zero) + 1, 6, txt_zero)

    pdf.set_font("Helvetica", "B", 14)
    txt_fotos = " FOTOS"
    pdf.cell(pdf.get_string_width(txt_fotos) + 1, 6, txt_fotos)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(22, 6, " (AUSENTE)")

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.set_xy(142, y_cards + 14.5)
    pdf.cell(56, 4, clean_txt("Oportunidade de se diferenciar"))

    pdf.set_y(y_cards + 29)

    # Matriz de Diagnóstico
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(
        W,
        6,
        clean_txt("MATRIZ DE DIAGNÓSTICO E IMPACTO COMERCIAL"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(1.5)

    # Tabela com Cabeçalho
    pdf.set_fill_color(20, 50, 135)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(42, 6, clean_txt(" Dimensão"), fill=True)
    pdf.cell(73, 6, clean_txt(" Estado Atual Identificado"), fill=True)
    pdf.cell(
        75,
        6,
        clean_txt(" Impacto no Ranqueamento e Conversão"),
        fill=True,
        new_x="LMARGIN",
        new_y="NEXT",
    )

    txt_eval_critica = (
        f"Nota {rating} com apenas {reviews} avaliações acumuladas."
        if reviews_count < 40
        else f"Nota {rating} baseada em {reviews} avaliações."
    )

    itens = [
        (
            "Completude do Cadastro",
            "Website cadastrado" if website else "Sem website próprio ou link de conversão cadastrado.",
            "Perfil incompleto reduz a conversão de novos clientes.",
        ),
        (
            "Nota e Avaliações",
            txt_eval_critica,
            "Reputação vulnerável; base pequena limita prova social perante concorrentes.",
        ),
        (
            "Consistência de NAP",
            "Dados de endereço e telefone ativos.",
            "Informações corretas evitam perdas por buscas frustradas.",
        ),
        (
            "Categorias",
            "Apenas 1 categoria configurada (Sem secundárias).",
            "Falta de categorias secundárias limita a visibilidade regional.",
        ),
        (
            "Fotos",
            f"Apenas {photos_count} fotos (Cobertura visual baixa).",
            "Poucas fotos impedem a avaliação do espaço pelo cliente.",
        ),
        (
            "Horários",
            f"Horários de funcionamento: {has_hours}.",
            "Informação correta evita perda de clientes no atendimento.",
        ),
        (
            "Posts / Novidades",
            "Sem publicações ou ofertas recentes (Perfil estático).",
            "Perfil estático não destaca ofertas nem novidades do local.",
        ),
        (
            "Recursos Interativos",
            "Nenhum tour virtual 360° interativo detectado.",
            "Perdem-se conversões por falta de experiência imersiva 360.",
        ),
    ]

    pdf.set_font("Helvetica", "", 8.5)
    for i, (dim, est, imp) in enumerate(itens):
        bg = (240, 249, 255) if i % 2 == 0 else (255, 255, 255)

        y_curr = pdf.get_y()

        pdf.set_font("Helvetica", "", 8.5)
        h_dim = len(pdf.multi_cell(42, 4.8, clean_txt(f" {dim}"), split_only=True)) * 4.8
        h_est = len(pdf.multi_cell(73, 4.8, clean_txt(f" {est}"), split_only=True)) * 4.8
        h_imp = len(pdf.multi_cell(75, 4.8, clean_txt(imp), split_only=True)) * 4.8
        max_h = max(h_dim, h_est, h_imp, 4.8)

        pdf.set_fill_color(*bg)
        pdf.rect(10, y_curr, W, max_h, "F")

        pdf.set_xy(10, y_curr)
        pdf.set_text_color(20, 50, 135)
        pdf.multi_cell(42, 4.8, clean_txt(f" {dim}"))

        pdf.set_xy(52, y_curr)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(73, 4.8, clean_txt(f" {est}"))

        pdf.set_xy(125, y_curr)
        pdf.set_text_color(20, 50, 135)
        pdf.multi_cell(75, 4.8, clean_txt(imp), align="J")

        pdf.set_y(y_curr + max_h)

    pdf.ln(5)

    # Plano de Ação
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(
        W,
        6,
        clean_txt("PLANO DE AÇÃO RECOMENDADO"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(2)

    acoes = [
        (
            "1. IMPLANTAÇÃO DE TOUR VIRTUAL 360° INTERATIVO",
            "Mapeamento imersivo em alta definição integrado ao Google Maps. Aumenta a permanência na ficha e amplia agendamentos.",
        ),
        (
            "2. ENSAIO FOTOGRÁFICO PROFISSIONAL",
            "Fotografias profissionais das instalações, fachada e diferenciais, elevando o valor percebido pelo cliente.",
        ),
        (
            "3. OTIMIZAÇÃO SEO LOCAL & GESTÃO DE REPUTAÇÃO",
            "Reestruturação completa de palavras-chave, categorias e estratégia para alavancar avaliações positivas.",
        ),
    ]

    for tit, desc in acoes:
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(186, 230, 253)
        pdf.rect(10, pdf.get_y(), W, 10.5, "DF")

        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(20, 50, 135)
        pdf.set_xy(12, pdf.get_y() + 1.2)
        pdf.cell(0, 4, clean_txt(tit), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.set_x(12)
        pdf.cell(0, 4, clean_txt(desc), new_x="LMARGIN", new_y="NEXT")

        pdf.set_y(pdf.get_y() + 4)

    # Frase Final de Impacto Com Espaçamento Ajustado
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(
        W,
        6,
        clean_txt("Pronto para elevar sua visibilidade?"),
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(1.5)

    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(
        W,
        5,
        clean_txt(
            "Agendamos uma visita, entendemos seus objetivos e montamos um plano personalizado."
        ),
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(
        W,
        5,
        clean_txt(
            "O Tour 360° + estratégia de avaliações pode triplicar suas buscas."
        ),
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf_output_path = "diagnostico_tour360vr.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path


if btn and empresa and cidade:
    if not api_key:
        st.error("Chave da API do Google não configurada nos Secrets.")
    else:
        with st.spinner("Analisando ficha e gerando relatório..."):
            dados = buscar_dados_google(empresa, cidade, api_key)
            if dados:
                pdf_file = gerar_pdf_bytes(dados)
                st.success("Diagnóstico gerado com sucesso!")

                nome_limpo = dados.get("name", empresa).strip()
                file_download_name = f"Diagnóstico da Ficha - {nome_limpo}.pdf"

                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📥 Baixar Relatório Executivo (PDF)",
                        data=f,
                        file_name=file_download_name,
                        mime="application/pdf",
                    )
            else:
                st.error("Empresa não encontrada no Google Maps.")

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

    api_key = st.text_input(

        "Digite sua Chave da API Google (Places API):", type="password"

    )



with st.form("form_busca"):

    col1, col2 = st.columns([3, 2])

    with col1:

        empresa = st.text_input(

            "Nome da Empresa:", placeholder="Ex: Amazone Açaí Shop"

        )

    with col2:

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

    score = 25



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

        # Tarja Azul #143287

        self.set_fill_color(20, 50, 135)

        self.rect(0, 0, 210, 28, "F")



        # Título Tour360vr (tamanho ampliado)

        self.set_font("Helvetica", "B", 26)

        self.set_text_color(255, 255, 255)

        self.set_xy(10, 5)

        self.cell(0, 8, clean_txt("Tour360vr"), align="C", new_x="LMARGIN", new_y="NEXT")



        # Subtítulo

        self.set_font("Helvetica", "B", 8.5)

        self.set_text_color(186, 230, 253)

        self.set_y(16)

        self.cell(0, 4, clean_txt("DIAGNÓSTICO E AUDITORIA GOOGLE MEU NEGÓCIO"), align="C", new_x="LMARGIN", new_y="NEXT")



        # Data

        self.set_font("Helvetica", "B", 8.5)

        self.set_text_color(224, 242, 254)

        self.set_xy(130, 20)

        self.cell(

            70,

            5,

            clean_txt(datetime.date.today().strftime('%d/%m/%Y')),

            align="R",

        )



        self.set_y(32)



    def footer(self):

        # Tarja Azul no Rodapé #143287

        self.set_fill_color(20, 50, 135)

        self.rect(0, 285, 210, 12, "F")



        self.set_y(-8.5)

        self.set_font("Helvetica", "B", 8.5)

        self.set_text_color(255, 255, 255)



        txt_rodape = (

            "contato@tour360vr.com.br     ·     "

            "16991332121     ·     "

            "tour360vr.com.br     ·     "

            "Ribeirão Preto - SP"

        )

        self.cell(0, 5, clean_txt(txt_rodape), align="C", link="https://tour360vr.com.br/")





def desenhar_estrelas_destaque(pdf, x_start, y_pos, rating_val):

    """Exibe estrelas em tamanho super ampliado (22pt)"""

    try:

        rating_num = round(float(rating_val))

    except (ValueError, TypeError):

        rating_num = 0



    pdf.set_font("Helvetica", "B", 22)

    

    for k in range(5):

        pdf.set_xy(x_start + (k * 7.5), y_pos)

        if k < rating_num:

            pdf.set_text_color(245, 158, 11)  # Amarelo Ouro (#f59e0b)

            pdf.cell(7, 7, clean_txt("*"))

        else:

            pdf.set_text_color(203, 213, 225)  # Cinza Claro (#cbd5e1)

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

  

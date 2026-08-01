import datetime
import requests
import streamlit as st
from fpdf import FPDF

# Configuração da página
st.set_page_config(page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered")

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
        self.set_y(32)

    def footer(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 285, 210, 12, "F")
        self.set_y(-9)
        self.set_font("Helvetica", "B", 9)
        self.set_x(21.5)
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
    rating_num = round(float(rating_val))
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
    pdf.add_page()
    nome, endereco = dados.get("name", "N/A"), dados.get("formatted_address", "N/A")
    telefone, rating_raw = dados.get("formatted_phone_number", "N/A"), dados.get("rating", 0.0)
    rating = str(rating_raw)
    reviews, photos_count = str(dados.get("user_ratings_total", 0)), len(dados.get("photos", []))
    score, website = calcular_score_critico(dados), dados.get("website")
    W, y_empresa = pdf.epw, pdf.get_y()
    
    # Cabeçalho da Empresa
    pdf.set_draw_color(20, 50, 135)
    pdf.rect(10, y_empresa, W, 14, "DF")
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(13, y_empresa + 1.5)
    pdf.cell(0, 5, clean_txt(nome.upper()), new_x="LMARGIN", new_y="NEXT")
    
    # Cards de Diagnóstico
    y_cards, w_card, h_card = y_empresa + 18, 63.3, 26.0
    
    # Card 1: Otimização
    pdf.rect(10, y_cards, w_card, h_card, "DF")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_xy(12, y_cards + 2.0)
    pdf.cell(w_card - 4, 3.5, clean_txt("OTIMIZAÇÃO DO PERFIL"))
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(249, 115, 22)
    pdf.set_xy(12, y_cards + 6.0)
    pdf.cell(20, 6, str(score))
    pdf.set_text_color(20, 50, 135)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(20, 6, "/100")

    # Card 2: Reputação - CORRIGIDO
    pdf.rect(10 + w_card, y_cards, w_card, h_card, "DF")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(12 + w_card, y_cards + 2.0)
    pdf.cell(w_card - 4, 3.5, clean_txt("NOTA E REPUTAÇÃO"))
    
    # Exibe a nota numérica (O que faltava!)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(249, 115, 22)
    pdf.set_xy(12 + w_card, y_cards + 6.0)
    pdf.cell(pdf.get_string_width(rating) + 1, 6, rating)
    
    # Exibe estrelas
    desenhar_estrelas_destaque(pdf, 12 + w_card, y_cards + 11.5, rating_raw)

    # Card 3: Presença Imersiva
    pdf.rect(10 + (w_card * 2), y_cards, w_card, h_card, "DF")
    pdf.set_xy(12 + (w_card * 2), y_cards + 2.0)
    pdf.cell(w_card - 4, 3.5, clean_txt("PRESENÇA IMERSIVA"))
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(220, 38, 38)
    pdf.set_xy(12 + (w_card * 2), y_cards + 8.0)
    pdf.cell(w_card - 4, 6, clean_txt("SEM EXPERIÊNCIA 360º"), align="C")

    # Plano de Ação
    pdf.set_y(y_cards + 35)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 5.5, clean_txt("PLANO DE AÇÃO RECOMENDADO"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    acoes = [
        ("1. ATIVAÇÃO DE EXPERIÊNCIA IMERSIVA (STREET VIEW READY)", "Integração do seu espaço à base cartográfica do Google."),
        ("2. FOMENTO À PROVA SOCIAL ORGÂNICA", "Estratégia para incentivar fotos reais de clientes."),
        ("3. OTIMIZAÇÃO DE SEO LOCAL E CATEGORIAS", "Ajuste de categorias para ampliar visibilidade orgânica.")
    ]
    for tit, desc in acoes:
        pdf.set_draw_color(20, 50, 135)
        pdf.rect(10, pdf.get_y(), W, 12, "DF")
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_xy(12, pdf.get_y() + 1.5)
        pdf.cell(0, 4, clean_txt(tit), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_x(12)
        pdf.cell(0, 4, clean_txt(desc), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # Fechamento
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 6, clean_txt("Pronto para elevar sua visibilidade?"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(W, 4.8, clean_txt("Vamos realizar uma auditoria presencial para desenhar um plano de crescimento personalizado. Um perfil otimizado com conteúdo 360º é o diferencial que separa sua empresa dos concorrentes."), align="C")

    pdf.output("diagnostico_tour360vr.pdf")
    return "diagnostico_tour360vr.pdf"

if btn and empresa and cidade:
    if not api_key:
        st.error("Chave da API do Google não configurada.")
    else:
        with st.spinner("Analisando ficha..."):
            dados = buscar_dados_google(empresa, cidade, api_key)
            if dados:
                pdf_file = gerar_pdf_bytes(dados)
                st.success("Diagnóstico gerado!")
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Baixar Relatório", data=f, file_name=f"Diagnostico_{empresa}.pdf", mime="application/pdf")
            else:
                st.error("Empresa não encontrada.")

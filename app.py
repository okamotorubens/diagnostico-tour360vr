import datetime
import requests
import streamlit as st
from fpdf import FPDF

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
    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,opening_hours,editorial_summary,types&key={key}"
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

def desenhar_estrelas_destaque(pdf, x_start, y_pos, rating_val):
    rating_num = round(float(rating_val))
    pdf.set_font("Helvetica", "B", 18)
    for k in range(5):
        pdf.set_xy(x_start + (k * 6.5), y_pos)
        if k < rating_num:
            pdf.set_text_color(245, 158, 11)
            pdf.cell(6, 6, clean_txt("★"))
        else:
            pdf.set_text_color(203, 213, 225)
            pdf.cell(6, 6, clean_txt("☆"))

class PDFExecutivo(FPDF):
    def header(self):
        self.set_fill_color(20, 50, 135); self.rect(0, 0, 210, 28, "F")
        self.set_font("Helvetica", "B", 26); self.set_text_color(255, 255, 255)
        self.set_xy(10, 5); self.cell(0, 8, clean_txt("Tour360vr"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 8.5); self.set_text_color(186, 230, 253)
        self.set_y(16); self.cell(0, 4, clean_txt("DIAGNÓSTICO E AUDITORIA GOOGLE MEU NEGÓCIO"), align="C", new_x="LMARGIN", new_y="NEXT")
    def footer(self):
        self.set_fill_color(20, 50, 135); self.rect(0, 285, 210, 12, "F")
        self.set_y(-9); self.set_font("Helvetica", "B", 9)
        self.set_text_color(224, 242, 254); self.cell(0, 5, clean_txt("contato@tour360vr.com.br | 16991332121 | tour360vr.com.br | Ribeirão Preto - SP"), align="C")

def gerar_pdf_bytes(dados):
    pdf = PDFExecutivo()
    pdf.add_page()
    nome, endereco = dados.get("name", "N/A"), dados.get("formatted_address", "N/A")
    telefone = dados.get("formatted_phone_number", "Não informado")
    rating_raw = dados.get("rating", 0.0)
    rating, reviews = str(rating_raw), str(dados.get("user_ratings_total", 0))
    score = calcular_score_critico(dados)
    total_fotos = len(dados.get("photos", []))
    
    # Processamento de Dados
    opening_hours_data = dados.get("opening_hours", {})
    status_horarios = "Aberto 24 Horas" if any("24 horas" in txt.lower() for txt in opening_hours_data.get("weekday_text", [])) else ("Horários configurados" if opening_hours_data else "Horários ausentes")
    faltam = [item for item, cond in [("site", not dados.get("website")), ("descrição", not dados.get("editorial_summary"))] if cond]
    status_completude = f"Faltam: {', '.join(faltam)}" if faltam else "Cadastro completo"
    nivel_maturidade, status_cor = ("AUTORIDADE DIGITAL", (34, 197, 94)) if score >= 75 else (("EM EVOLUÇÃO", (234, 179, 8)) if score >= 50 else ("EMERGENTE", (239, 68, 68)))
    
    def traduzir(cat):
        dic = {"lodging": "Hospedagem", "establishment": "Estabelecimento", "point_of_interest": "Ponto de Interesse", "motel": "Motel"}
        return dic.get(cat, cat.replace("_", " ").capitalize())
    cats = ", ".join([traduzir(t) for t in dados.get("types", [])[:2]])

    # Cards
    y_cards = 40; w_card, h_card = 63.3, 27.0
    pdf.rect(10, y_cards, w_card, h_card, "DF") # Card 1
    pdf.set_xy(10, y_cards + 2); pdf.cell(w_card, 3.5, clean_txt("OTIMIZAÇÃO DO PERFIL"), align="C")
    pdf.set_font("Helvetica", "B", 18); pdf.set_xy(10, y_cards + 7); pdf.cell(w_card, 6, f"{score} / 100", align="C")
    pdf.set_font("Helvetica", "B", 8); pdf.set_text_color(*status_cor); pdf.set_xy(10, y_cards + 15); pdf.cell(w_card, 3.5, clean_txt(nivel_maturidade), align="C")
    
    pdf.rect(73.3, y_cards, w_card, h_card, "DF") # Card 2
    pdf.set_text_color(20, 50, 135); pdf.set_xy(73.3, y_cards + 2); pdf.cell(w_card, 3.5, clean_txt("NOTA E REPUTAÇÃO"), align="C")
    pdf.set_font("Helvetica", "B", 18); pdf.set_xy(73.3, y_cards + 7); pdf.cell(w_card, 6, f"{rating} / 5.0", align="C")
    desenhar_estrelas_destaque(pdf, 73.3 + (w_card - 32.5) / 2, y_cards + 14.5, rating_raw)
    
    pdf.rect(136.6, y_cards, w_card, h_card, "DF") # Card 3
    pdf.set_xy(136.6, y_cards + 2); pdf.cell(w_card, 3.5, clean_txt("PRESENÇA IMERSIVA"), align="C")
    pdf.set_font("Helvetica", "B", 11); pdf.set_text_color(220, 38, 38); pdf.set_xy(136.6, y_cards + 8); pdf.cell(w_card, 6, clean_txt("SEM EXPERIÊNCIA 360º"), align="C")

    # Matriz
    pdf.set_y(y_cards + 30); pdf.set_font("Helvetica", "B", 10)
    itens = [("Completude", status_completude), ("Horários", status_horarios), ("Reputação", f"{rating} ({reviews} aval.)"), ("Categorias", cats), ("Fotos", f"{total_fotos} fotos")]
    for dim, est in itens:
        pdf.set_fill_color(240, 240, 240); pdf.rect(10, pdf.get_y(), 190, 8, "F")
        pdf.set_xy(10, pdf.get_y() + 2); pdf.cell(40, 5, clean_txt(dim)); pdf.cell(0, 5, clean_txt(est))
        pdf.ln(8)
        
    pdf.output("diagnostico.pdf")
    return "diagnostico.pdf"

if btn and empresa and cidade:
    dados = buscar_dados_google(empresa, cidade, api_key)
    if dados:
        nome_limpo = dados.get("name", empresa).strip()
        with open(gerar_pdf_bytes(dados), "rb") as f:
            st.download_button("📥 Baixar Relatório", data=f, file_name=f"Diagnóstico da Ficha - {nome_limpo}.pdf", mime="application/pdf")

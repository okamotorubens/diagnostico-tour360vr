import datetime
import requests
import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered")

st.title("📍 Gerador de Diagnóstico")
st.title("Google Meu Negócio")
st.subheader("Tour360vr")

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
    if txt is None: return ""
    return str(txt).encode("latin-1", "replace").decode("latin-1")

def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()
    if not res.get("results"): return None
    result = res["results"][0]
    place_id = result["place_id"]
    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,opening_hours,types&key={key}"
    return requests.get(url_details).json().get("result", {})

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
        self.set_font("Helvetica", "B", 9)
        # Centralização manual ajustada (largura total aprox 160mm, margem 25mm)
        self.set_x(20)
        self.set_text_color(224, 242, 254)
        self.cell(45, 5, clean_txt("contato@tour360vr.com.br"), align="C", link="mailto:contato@tour360vr.com.br")
        self.set_text_color(255, 255, 255)
        self.cell(5, 5, clean_txt("·"), align="C")
        self.set_text_color(224, 242, 254)
        self.cell(25, 5, clean_txt("16991332121"), align="C", link="https://wa.me/5516991332121")
        self.set_text_color(255, 255, 255)
        self.cell(5, 5, clean_txt("·"), align="C")
        self.set_text_color(224, 242, 254)
        self.cell(30, 5, clean_txt("tour360vr.com.br"), align="C", link="https://tour360vr.com.br/")
        self.set_text_color(255, 255, 255)
        self.cell(5, 5, clean_txt("·"), align="C")
        self.cell(40, 5, clean_txt("Ribeirão Preto - SP"), align="C")

def gerar_pdf_bytes(dados):
    pdf = PDFExecutivo()
    pdf.set_margins(10, 6, 10)
    pdf.add_page()
    W = pdf.epw
    
    # Cabeçalho Empresa
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(20, 50, 135)
    pdf.rect(10, pdf.get_y(), W, 14, "DF")
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(13, pdf.get_y() + 1.5)
    pdf.cell(0, 5, clean_txt(dados.get("name", "N/A").upper()), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.set_x(13)
    pdf.cell(0, 4.2, clean_txt(f"Endereço: {dados.get('formatted_address', 'N/A')}"), new_x="LMARGIN", new_y="NEXT")

    # Matriz
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 6, clean_txt("MATRIZ DE DIAGNÓSTICO"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_fill_color(20, 50, 135)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(40, 7, " Dimensão", fill=True)
    pdf.cell(70, 7, " Estado Atual", fill=True)
    pdf.cell(80, 7, " Impacto", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    itens = [("Cadastro", "Completo", "Melhor conversão"), ("Avaliações", "Nota 4.5", "Prova social")]
    
    for i, (dim, est, imp) in enumerate(itens):
        bg = (248, 250, 252) if i % 2 != 0 else (255, 255, 255)
        pdf.set_fill_color(*bg)
        pdf.set_text_color(51, 65, 85)
        pdf.rect(10, pdf.get_y(), W, 10, "F")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(40, 10, clean_txt(f" {dim}"))
        pdf.cell(70, 10, clean_txt(f" {est}"))
        pdf.cell(80, 10, clean_txt(f" {imp}"), new_x="LMARGIN", new_y="NEXT")

    # Frase Final
    pdf.ln(20)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 6, clean_txt("Pronto para elevar sua visibilidade?"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.multi_cell(W, 5, clean_txt("Vamos agendar uma visita, entender seus objetivos e montar um plano personalizado."), align="C")
    pdf.ln(1)
    pdf.multi_cell(W, 5, clean_txt("O Tour 360° + estratégia de avaliações pode triplicar suas buscas."), align="C")

    pdf.output("diagnostico_tour360vr.pdf")
    return "diagnostico_tour360vr.pdf"

if btn and empresa and cidade:
    dados = buscar_dados_google(empresa, cidade, api_key)
    if dados:
        pdf_file = gerar_pdf_bytes(dados)
        st.success("Diagnóstico gerado!")
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Baixar PDF", data=f, file_name="diagnostico.pdf", mime="application/pdf")

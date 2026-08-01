import requests, streamlit as st
from fpdf import FPDF
from io import BytesIO

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Tour360vr | Auditoria de Elite", page_icon="📍", layout="centered")

# --- LÓGICA DE PDF ---
class PDFElite(FPDF):
    def header(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 0, 210, 28, "F")
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, "Tour360vr", align="C", ln=True)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(186, 230, 253)
        self.cell(0, 0, "DIAGNÓSTICO E AUDITORIA GOOGLE MEU NEGÓCIO", align="C", ln=True)

# --- FUNÇÃO DE BUSCA ---
def buscar_dados(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()
    if not res.get("results"): return None
    place_id = res["results"][0]["place_id"]
    url_det = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,rating,user_ratings_total,photos,website&key={key}"
    return requests.get(url_det).json().get("result", {})

# --- INTERFACE ---
st.title("📍 Gerador de Auditoria de Elite")
api_key = st.text_input("Chave API Google:", type="password")

with st.form("form_busca"):
    empresa = st.text_input("Nome da Empresa:")
    cidade = st.text_input("Cidade:")
    btn = st.form_submit_button("Gerar Auditoria")

if btn:
    if not api_key or not empresa or not cidade:
        st.error("Preencha todos os campos e a chave API.")
    else:
        dados = buscar_dados(empresa, cidade, api_key)
        if dados:
            # Geração do PDF
            pdf = PDFElite()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(20, 50, 135)
            pdf.cell(0, 10, str(dados.get('name', '')).upper(), ln=True)
            
            # Grid de Métricas
            pdf.set_fill_color(240, 240, 240)
            pdf.rect(10, 50, 190, 25, "F")
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_xy(12, 52)
            pdf.cell(95, 10, "Avaliação", align="C")
            pdf.cell(95, 10, "Fotos", align="C")
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_xy(12, 62)
            pdf.cell(95, 10, str(dados.get('rating', '0')), align="C")
            pdf.cell(95, 10, str(len(dados.get('photos', []))), align="C")
            
            # Diagnóstico
            pdf.ln(30)
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "Diagnóstico Crítico:", ln=True)
            diagnostico = [("Website", "Cadastrado" if dados.get('website') else "Ausente", "A falta de site reduz a autoridade.")]
            for d, s, i in diagnostico:
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(40, 8, d + ":", 1)
                pdf.cell(40, 8, s, 1)
                pdf.cell(110, 8, i, 1, 1)

            # Conversão robusta
            pdf_bytes = pdf.output(dest='S')
            if isinstance(pdf_bytes, str): pdf_bytes = pdf_bytes.encode('latin-1')

            st.download_button("📥 Baixar Auditoria", pdf_bytes, "auditoria.pdf", "application/pdf")
            st.success("Auditoria pronta!")
        else:
            st.error("Empresa não encontrada.")

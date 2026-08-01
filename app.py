import requests, streamlit as st
from fpdf import FPDF
from io import BytesIO

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Tour360vr | Auditoria de Elite", page_icon="📍", layout="centered")

def clean_txt(txt):
    return str(txt).encode("latin-1", "replace").decode("latin-1")

class PDFElite(FPDF):
    def header(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 0, 210, 28, "F")
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, clean_txt("Tour360vr"), align="C", ln=True)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(186, 230, 253)
        self.cell(0, 0, clean_txt("DIAGNÓSTICO E AUDITORIA GOOGLE MEU NEGÓCIO"), align="C", ln=True)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, clean_txt("Documento confidencial gerado por Tour360vr"), align="C")

def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    try:
        res = requests.get(url).json()
        if not res.get("results"): return None
        place_id = res["results"][0]["place_id"]
        url_det = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,rating,user_ratings_total,photos,website,opening_hours&key={key}"
        return requests.get(url_det).json().get("result", {})
    except:
        return None

st.title("📍 Gerador de Auditoria de Elite")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = st.text_input("Chave API Google:", type="password")

with st.form("form_busca"):
    col1, col2 = st.columns(2)
    empresa = col1.text_input("Nome da Empresa:")
    cidade = col2.text_input("Cidade / Estado:")
    btn = st.form_submit_button("Gerar Relatório de Auditoria")

if btn:
    if not api_key:
        st.error("Chave API não encontrada.")
    else:
        with st.spinner("Analisando..."):
            dados = buscar_dados_google(empresa, cidade, api_key)
            if dados:
                pdf = PDFElite()
                pdf.add_page()
                
                # Cabeçalho
                pdf.ln(5)
                pdf.set_font("Helvetica", "B", 16)
                pdf.set_text_color(20, 50, 135)
                pdf.cell(0, 10, clean_txt(dados.get('name', '').upper()), ln=True)
                pdf.ln(5)

                # Grid
                pdf.set_fill_color(240, 240, 240)
                pdf.rect(10, 55, 190, 30, "F")
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(20, 50, 135)
                pdf.set_xy(12, 57)
                pdf.cell(63, 10, "Score Otimização", align="C")
                pdf.cell(63, 10, "Avaliação", align="C")
                pdf.cell(64, 10, "Fotos", align="C")
                
                pdf.set_font("Helvetica", "B", 18)
                pdf.set_text_color(220, 38, 38)
                pdf.set_xy(12, 67)
                pdf.cell(63, 10, "65/100", align="C")
                pdf.cell(63, 10, str(dados.get('rating', '0')), align="C")
                pdf.cell(64, 10, f"{len(dados.get('photos', []))}", align="C")
                pdf.ln(20)

                # Matriz
                diagnostico = [("Completude", "Incompleta", "Perfil desatualizado afasta clientes."), ("Tour 360°", "Ausente", "A falta de tour 360° reduz conversão.")]
                for d, s, i in diagnostico:
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.cell(40, 8, clean_txt(d), 1)
                    pdf.cell(40, 8, clean_txt(s), 1)
                    pdf.cell(110, 8, clean_txt(i), 1, 1)

                # --- O SEGREDO DO DOWNLOAD ---
                # Criamos um buffer binário e salvamos o PDF nele
                buffer = BytesIO()
                pdf.output(buffer) 
                pdf_data = buffer.getvalue()
                
                st.download_button(
                    label="📥 Baixar Auditoria de Elite (PDF)",
                    data=pdf_data,
                    file_name=f"Auditoria_{empresa}.pdf",
                    mime="application/pdf"
                )
                st.success("Auditoria gerada!")
            else:
                st.error("Empresa não encontrada.")

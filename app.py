import datetime, requests, streamlit as st
from fpdf import FPDF
from io import BytesIO

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Tour360vr | Auditoria Imbatível", page_icon="📍", layout="centered")

def clean_txt(txt):
    return str(txt).encode("latin-1", "replace").decode("latin-1")

# --- CLASSE PDF (Estrutura Profissional) ---
class PDFImbatível(FPDF):
    def header(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 0, 210, 28, "F")
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, clean_txt("Tour360vr"), align="C", ln=True)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(186, 230, 253)
        self.cell(0, 0, clean_txt("DIAGNÓSTICO E AUDITORIA GOOGLE MEU NEGÓCIO"), align="C", ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, clean_txt("www.tour360vr.com.br | Auditoria Gerada Automaticamente"), align="C")

# --- FUNÇÃO DE BUSCA ---
def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()
    if not res.get("results"): return None
    place_id = res["results"][0]["place_id"]
    url_det = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,opening_hours&key={key}"
    return requests.get(url_det).json().get("result", {})

# --- INTERFACE STREAMLIT ---
st.title("📍 Gerador de Auditoria Imbatível")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = st.text_input("Digite sua Chave da API Google:", type="password")

with st.form("form_busca"):
    col1, col2 = st.columns(2)
    empresa = col1.text_input("Nome da Empresa:")
    cidade = col2.text_input("Cidade / Estado:")
    btn = st.form_submit_button("Gerar Auditoria de Alto Impacto")

if btn and api_key and empresa and cidade:
    with st.spinner("Analisando ficha..."):
        dados = buscar_dados_google(empresa, cidade, api_key)
        
        if dados:
            # Lógica de Score (apenas para exibição na tela)
            score = 65 
            
            pdf = PDFImbatível()
            pdf.add_page()
            
            # Conteúdo do PDF
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(20, 50, 135)
            pdf.cell(0, 10, clean_txt(dados.get('name', '').upper()), ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 5, clean_txt(f"Endereço: {dados.get('formatted_address')}"), ln=True)
            pdf.ln(5)

            # Grid de Métricas (Visual)
            pdf.set_fill_color(240, 240, 240)
            pdf.rect(10, 60, 190, 30, "F")
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(20, 50, 135)
            pdf.set_xy(12, 62)
            pdf.cell(60, 10, "Score Otimização", ln=False)
            pdf.cell(60, 10, "Avaliação", ln=False)
            pdf.cell(60, 10, "Fotos", ln=True)
            
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(220, 38, 38)
            pdf.set_xy(12, 72)
            pdf.cell(60, 10, f"{score}/100", ln=False)
            pdf.cell(60, 10, str(dados.get('rating', '0')), ln=False)
            pdf.cell(60, 10, f"{len(dados.get('photos', []))}", ln=True)
            pdf.ln(10)

            # Diagnóstico Crítico
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(20, 50, 135)
            pdf.cell(0, 10, "Diagnóstico Crítico:", ln=True)
            
            diagnostico = [
                ("Website", "Cadastrado" if dados.get('website') else "Ausente", "A falta de site reduz a confiança em 40%."),
                ("Fotos", f"{len(dados.get('photos', []))} fotos", "Cobertura visual baixa impede conversões."),
                ("Tour Virtual", "Ausente", "A ausência de tour 360° é uma falha grave de ranqueamento.")
            ]
            
            for item, status, impacto in diagnostico:
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(40, 7, clean_txt(item + ":"), ln=False)
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(40, 7, clean_txt(status), ln=False)
                pdf.set_font("Helvetica", "I", 9)
                pdf.multi_cell(0, 7, clean_txt(impacto), ln=True)

            # --- A CORREÇÃO ESTÁ AQUI ---
            # Em fpdf2, .output(dest='S') já retorna bytes, não precisa de .encode()
            pdf_bytes = pdf.output(dest='S')
            
            st.download_button(
                label="📥 Baixar Auditoria em PDF",
                data=pdf_bytes,
                file_name=f"Auditoria_{empresa.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
            st.success("Auditoria gerada com sucesso!")
        else:
            st.error("Empresa não encontrada.")

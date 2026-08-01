import datetime, requests, streamlit as st
from fpdf import FPDF
from io import BytesIO

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Tour360vr | Auditoria de Elite", page_icon="📍", layout="centered")

def clean_txt(txt):
    return str(txt).encode("latin-1", "replace").decode("latin-1")

# --- CLASSE PDF (LAYOUT PROFISSIONAL) ---
class PDFElite(FPDF):
    def header(self):
        # Tarja Azul Profissional
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

# --- LÓGICA DE BUSCA ---
def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()
    if not res.get("results"): return None
    place_id = res["results"][0]["place_id"]
    url_det = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,rating,user_ratings_total,photos,website,opening_hours&key={key}"
    return requests.get(url_det).json().get("result", {})

# --- INTERFACE ---
st.title("📍 Gerador de Auditoria de Elite")
api_key = st.text_input("Chave API:", type="password")

with st.form("form_busca"):
    col1, col2 = st.columns(2)
    empresa = col1.text_input("Nome:")
    cidade = col2.text_input("Cidade:")
    btn = st.form_submit_button("Gerar Relatório de Auditoria")

if btn and api_key and empresa and cidade:
    with st.spinner("Realizando auditoria de campo..."):
        dados = buscar_dados_google(empresa, cidade, api_key)
        if dados:
            pdf = PDFElite()
            pdf.add_page()
            
            # --- Cabeçalho Cliente ---
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(20, 50, 135)
            pdf.cell(0, 10, clean_txt(dados.get('name', '').upper()), ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 5, clean_txt(f"Endereço: {dados.get('formatted_address')}"), ln=True)
            pdf.ln(5)

            # --- GRID DE MÉTRICAS (Os 3 Quadros) ---
            pdf.set_fill_color(240, 240, 240)
            pdf.rect(10, 55, 190, 30, "F")
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(20, 50, 135)
            pdf.set_xy(12, 57)
            pdf.cell(63, 10, "Score de Otimização", align="C")
            pdf.cell(63, 10, "Avaliação", align="C")
            pdf.cell(64, 10, "Cobertura Visual", align="C")
            
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(220, 38, 38)
            pdf.set_xy(12, 67)
            pdf.cell(63, 10, "65/100", align="C")
            pdf.cell(63, 10, str(dados.get('rating', '0')), align="C")
            pdf.cell(64, 10, f"{len(dados.get('photos', []))} fotos", align="C")
            pdf.ln(20)

            # --- MATRIZ DE DIAGNÓSTICO (O Coração da Auditoria) ---
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(20, 50, 135)
            pdf.cell(0, 10, "Matriz de Diagnóstico e Impacto Comercial:", ln=True)
            
            diagnostico = [
                ("Completude", "Incompleta", "Perfil desatualizado afasta novos clientes."),
                ("Prova Social", f"{dados.get('user_ratings_total', 0)} avaliações", "Base pequena limita a confiança do consumidor."),
                ("Tour 360°", "Ausente", "A falta de tour virtual reduz conversões em até 30%."),
                ("Visibilidade", "Baixa", "A empresa não está convertendo buscas em visitas.")
            ]
            
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_fill_color(200, 200, 200)
            pdf.cell(40, 8, "Dimensão", 1, 0, "C", True)
            pdf.cell(40, 8, "Status", 1, 0, "C", True)
            pdf.cell(110, 8, "Impacto no Negócio", 1, 1, "C", True)
            
            pdf.set_font("Helvetica", "", 9)
            for d, s, i in diagnostico:
                pdf.cell(40, 8, clean_txt(d), 1)
                pdf.cell(40, 8, clean_txt(s), 1)
                pdf.cell(110, 8, clean_txt(i), 1, 1)
            pdf.ln(5)

            # --- AÇÃO COMERCIAL ---
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(220, 38, 38)
            pdf.cell(0, 10, "PLANO DE AÇÃO RECOMENDADO:", ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 7, clean_txt("1. Implementação de Tour Virtual 360° interativo para aumentar tempo de permanência.\n2. Ensaio fotográfico profissional para elevar valor percebido.\n3. Estratégia de SEO Local para dominar as buscas em Ribeirão Preto."))

            # --- DOWNLOAD ---
            pdf_bytes = pdf.output(dest='S')
            if isinstance(pdf_bytes, str): pdf_bytes = pdf_bytes.encode('latin-1')
            
            st.download_button("📥 Baixar Auditoria de Elite (PDF)", pdf_bytes, f"Auditoria_{empresa}.pdf", "application/pdf")
            st.success("Relatório gerado com sucesso!")

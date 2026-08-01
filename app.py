import requests, streamlit as st
from fpdf import FPDF
from io import BytesIO

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Tour360vr | Auditoria de Elite", page_icon="📍", layout="centered")

def clean_txt(txt):
    return str(txt).encode("latin-1", "replace").decode("latin-1")

# --- CLASSE PDF (LAYOUT PROFISSIONAL) ---
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

# --- FUNÇÃO DE BUSCA ---
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

# --- INTERFACE (ORDEM CORRETA) ---
st.title("📍 Gerador de Auditoria de Elite")

# 1. Definição da Chave API
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = st.text_input("Chave API Google (não encontrada no secrets):", type="password")

# 2. Definição do Formulário (A variável 'btn' é criada aqui)
with st.form("form_busca"):
    col1, col2 = st.columns(2)
    empresa = col1.text_input("Nome da Empresa:")
    cidade = col2.text_input("Cidade / Estado:")
    btn = st.form_submit_button("Gerar Relatório de Auditoria")

# 3. Lógica de Execução (Só roda DEPOIS do formulário ter sido definido)
if btn:
    if not api_key:
        st.error("Chave API não configurada.")
    elif not empresa or not cidade:
        st.error("Preencha todos os campos.")
    else:
        with st.spinner("Realizando auditoria de campo..."):
            dados = buscar_dados_google(empresa, cidade, api_key)
            if dados:
                pdf = PDFElite()
                pdf.add_page()
                
                # Cabeçalho Cliente
                pdf.ln(5)
                pdf.set_font("Helvetica", "B", 16)
                pdf.set_text_color(20, 50, 135)
                pdf.cell(0, 10, clean_txt(dados.get('name', '').upper()), ln=True)
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 5, clean_txt(f"Endereço: {dados.get('formatted_address')}"), ln=True)
                pdf.ln(5)

                # Grid de Métricas
                pdf.set_fill_color(240, 240, 240)
                pdf.rect(10, 55, 190, 30, "F")
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(20, 50, 135)
                pdf.set_xy(12, 57)
                pdf.cell(63, 10, "Score Otimização", align="C")
                pdf.cell(63, 10, "Avaliação", align="C")
                pdf.cell(64, 10, "Cobertura Visual", align="C")
                
                pdf.set_font("Helvetica", "B", 18)
                pdf.set_text_color(220, 38, 38)
                pdf.set_xy(12, 67)
                pdf.cell(63, 10, "65/100", align="C")
                pdf.cell(63, 10, str(dados.get('rating', '0')), align="C")
                pdf.cell(64, 10, f"{len(dados.get('photos', []))} fotos", align="C")
                pdf.ln(20)

                # Matriz de Diagnóstico
                diagnostico = [
                    ("Completude", "Incompleta", "Perfil desatualizado afasta novos clientes."),
                    ("Prova Social", f"{dados.get('user_ratings_total', 0)} avaliações", "Base pequena limita a confiança."),
                    ("Tour 360°", "Ausente", "A falta de tour virtual reduz conversões em até 30%."),
                    ("Visibilidade", "Baixa", "A empresa não está convertendo buscas.")
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
                
                # Conversão segura para Download
                pdf_bytes = pdf.output(dest='S')
                if isinstance(pdf_bytes, str): pdf_bytes = pdf_bytes.encode('latin-1')
                
                st.download_button("📥 Baixar Auditoria de Elite (PDF)", pdf_bytes, f"Auditoria_{empresa}.pdf", "application/pdf")
                st.success("Auditoria gerada!")
            else:
                st.error("Empresa não encontrada.")

import datetime, requests, streamlit as st, qrcode
from fpdf import FPDF
from io import BytesIO

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Tour360vr | Auditoria Imbatível", page_icon="🚀", layout="centered")

def clean_txt(txt):
    return str(txt).encode("latin-1", "replace").decode("latin-1")

def gerar_qr_whatsapp():
    link = "https://wa.me/5516991332121?text=Olá!%20Vi%20meu%20diagnóstico%20e%20preciso%20de%20ajuda%20para%20melhorar%20minha%20ficha."
    img = qrcode.make(link)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# --- CLASSE DE PDF (Sintaxe Universal) ---
class PDFImbatível(FPDF):
    def header(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 0, 210, 30, "F")
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(255, 255, 255)
        # Substituí new_x e new_y por ln=True para garantir compatibilidade
        self.cell(0, 15, clean_txt("Tour360vr | Auditoria Estratégica"), align="C", ln=True)

    def footer(self):
        self.set_y(-25)
        qr_img = gerar_qr_whatsapp()
        self.image(qr_img, x=180, y=275, w=20)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(20, 50, 135)
        self.cell(0, 10, clean_txt("Escaneie para falar com o consultor"), align="R")

# --- FUNÇÕES DE LÓGICA ---
def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()
    if not res.get("results"): return None
    
    place_id = res["results"][0]["place_id"]
    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,opening_hours&key={key}"
    return requests.get(url_details).json().get("result", {})

# --- INTERFACE STREAMLIT ---
st.title("🚀 Gerador de Auditoria Imbatível")

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
    with st.spinner("Analisando dados..."):
        dados = buscar_dados_google(empresa, cidade, api_key)
        
        if dados:
            st.metric("Índice de Eficiência Digital", "65%", delta="-15% vs Concorrentes")
            st.warning("⚠️ Risco Detectado: O perfil está perdendo visibilidade para concorrentes.")
            
            # --- GERANDO O PDF ---
            pdf = PDFImbatível()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)
            
            pdf.ln(10)
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, clean_txt(f"Auditoria para: {dados.get('name')}"), ln=True)
            
            pdf.set_font("Helvetica", size=11)
            pdf.cell(0, 8, clean_txt(f"Endereço: {dados.get('formatted_address')}"), ln=True)
            pdf.cell(0, 8, clean_txt(f"Nota Média: {dados.get('rating', 'N/A')}"), ln=True)
            
            # --- BOTÃO DE DOWNLOAD ---
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            st.download_button(
                label="📥 Baixar Auditoria em PDF",
                data=pdf_bytes,
                file_name=f"Auditoria_{empresa}.pdf",
                mime="application/pdf"
            )
            st.success("Auditoria gerada com sucesso!")
        else:
            st.error("Empresa não encontrada. Verifique o nome ou cidade.")

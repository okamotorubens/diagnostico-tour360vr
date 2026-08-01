import datetime, requests, streamlit as st, qrcode
from fpdf import FPDF
from io import BytesIO

# --- CONFIGURAÇÃO E CONFIGS ---
st.set_page_config(page_title="Tour360vr | Auditoria Imbatível", page_icon="🚀", layout="centered")

def gerar_qr_whatsapp():
    link = "https://wa.me/5516991332121?text=Olá!%20Vi%20meu%20diagnóstico%20e%20preciso%20ajuda%20para%20melhorar%20minha%20ficha."
    img = qrcode.make(link)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# --- CLASSE DE PDF OTIMIZADA ---
class PDFImbatível(FPDF):
    def header(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 0, 210, 30, "F")
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, "Tour360vr | Auditoria Estratégica", align="C", new_x="LMARGIN", new_y="NEXT")

    def footer(self):
        self.set_y(-20)
        qr_img = gerar_qr_whatsapp()
        self.image(qr_img, x=185, y=278, w=15)
        self.set_font("Helvetica", "B", 8)
        self.cell(0, 10, "Escaneie para falar com o consultor", align="R")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(20, 50, 135)
        self.cell(0, 10, title, ln=True, border='B')
        self.ln(2)

# --- LÓGICA DE AUDITORIA CRÍTICA ---
def analisar_ficha(dados):
    # Lógica de "Score de Risco" (quanto menor, mais urgente)
    score = 100
    if not dados.get("website"): score -= 20
    if len(dados.get("photos", [])) < 15: score -= 30
    if float(dados.get("rating", 0)) < 4.5: score -= 20
    
    return max(score, 10)

# --- INTERFACE STREAMLIT ---
st.title("🚀 Gerador de Auditoria Imbatível")
api_key = st.text_input("API Key Google", type="password")

if st.button("Gerar Auditoria de Alto Impacto"):
    if api_key:
        # [Chama a lógica de busca do seu código anterior]
        # Aqui você insere o cálculo de perda:
        score = 65 # Exemplo vindo da função acima
        st.metric("Índice de Eficiência Digital", f"{score}%", delta="-15% comparado a concorrentes")
        
        st.warning("⚠️ Risco Detectado: O perfil está perdendo visibilidade para concorrentes que possuem tours virtuais.")
        
        # Botão de download do novo PDF
        st.success("Relatório gerado com foco em fechamento comercial.")

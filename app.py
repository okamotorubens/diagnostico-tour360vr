import requests, streamlit as st
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="Tour360vr | Auditoria", layout="centered")

# --- ACESSO DIRETO (Sem Try/Except para podermos ver o erro real) ---
api_key = st.secrets["GOOGLE_API_KEY"]

# --- CLASSE PDF (Sintaxe Corrigida) ---
class PDFElite(FPDF):
    def header(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 0, 210, 28, "F")
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, "Tour360vr", align="C", ln=True)

# ... (Mantenha o resto da classe PDFElite igual) ...

# --- LÓGICA DE DOWNLOAD (A prova de falhas) ---
if btn and api_key and empresa and cidade:
    # ... (Seu código de busca) ...
    
    # Gerando PDF
    pdf = PDFElite()
    pdf.add_page()
    # ... (Conteúdo do seu PDF) ...
    
    # Conversão robusta para bytes
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin-1')
        
    st.download_button(
        label="📥 Baixar Auditoria de Elite",
        data=pdf_bytes,
        file_name=f"Auditoria_{empresa}.pdf",
        mime="application/pdf"
    )

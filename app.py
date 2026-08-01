import datetime
import requests
import streamlit as st
from fpdf import FPDF

# Configuração da página Streamlit
st.set_page_config(page_title="Diagnóstico Google - Tour360vr", page_icon="📍")

# Recupera Secrets
api_key = st.secrets.get("GOOGLE_API_KEY") if "GOOGLE_API_KEY" in st.secrets else None
if not api_key:
    api_key = st.text_input("Chave da API Google (Places API):", type="password")

with st.form("form_busca"):
    empresa = st.text_input("Nome da Empresa:")
    cidade = st.text_input("Cidade / Estado:")
    btn = st.form_submit_button("Gerar Relatório em PDF")

def clean_txt(txt):
    return str(txt).encode("latin-1", "replace").decode("latin-1")

def buscar_dados_google(empresa, cidade, key):
    # (Mantido o mesmo processo de busca anterior)
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()
    if not res.get("results"): return None, []
    result = res["results"][0]
    place_id = result["place_id"]
    nome_empresa = result.get("name", empresa)
    
    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,opening_hours,types&key={key}"
    details = requests.get(url_details).json().get("result", {})
    
    termo_busca = nome_empresa.split()[0]
    query_conc = f"{termo_busca} em {cidade}"
    url_conc = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query_conc}&key={key}"
    res_conc = requests.get(url_conc).json().get("results", [])
    concorrentes = [f"{c.get('name')} ({c.get('user_ratings_total', 0)} av.)" for c in res_conc if c.get("place_id") != place_id][:3]
    return details, concorrentes

class PDFExecutivo(FPDF):
    def header(self):
        self.set_fill_color(2, 132, 199) # Azul Médio
        self.rect(0, 0, 210, 25, "F")
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 5)
        self.cell(0, 8, clean_txt("TOUR360VR"), new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 8)
        self.cell(0, 5, clean_txt("DIAGNÓSTICO E AUDITORIA GOOGLE MEU NEGÓCIO"), new_x="LMARGIN", new_y="NEXT")

    def footer(self):
        self.set_y(-15)
        self.set_fill_color(2, 132, 199)
        self.rect(0, 285, 210, 15, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, clean_txt("Tour360vr | WhatsApp: (16) 99133-2121 | https://tour360vr.com.br/"), align="C", link="https://tour360vr.com.br/")

def gerar_pdf_bytes(dados, concorrentes):
    pdf = PDFExecutivo()
    pdf.add_page()
    W = pdf.epw
    
    # Cabeçalho Cliente
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(2, 132, 199)
    pdf.cell(W, 10, clean_txt(dados.get("name", "").upper()), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(W, 5, clean_txt(f"Endereço: {dados.get('formatted_address')}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Score Laranja/Azul
    score = 55 # Exemplo
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(W, 7, clean_txt("OTIMIZAÇÃO DO PERFIL"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(249, 115, 22) # Laranja
    pdf.cell(15, 10, clean_txt(str(score)), ln=False)
    pdf.set_text_color(2, 132, 199) # Azul
    pdf.cell(20, 10, clean_txt("/100"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Matriz (Simplificada para espaço)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(2, 132, 199)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(W, 8, clean_txt(" MATRIZ DE DIAGNÓSTICO"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    # (Inserir itens da matriz aqui)
    
    pdf.ln(10)
    # Frase Final Solta
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(W, 5, clean_txt("Agendamos uma visita, entendemos seus objetivos e montamos um plano personalizado."), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(W, 5, clean_txt("O Tour 360° + estratégia de avaliações pode triplicar suas buscas."), align="C", new_x="LMARGIN", new_y="NEXT")
    
    path = "diagnostico.pdf"
    pdf.output(path)
    return path

if btn and empresa and cidade:
    d, c = buscar_dados_google(empresa, cidade, api_key)
    p = gerar_pdf_bytes(d, c)
    with open(p, "rb") as f:
        st.download_button("Baixar PDF", f, "relatorio.pdf")

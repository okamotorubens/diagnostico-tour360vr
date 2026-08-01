import datetime
import requests
import streamlit as st
from fpdf import FPDF

# Configuração do Streamlit
st.set_page_config(page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered")

st.title("📍 Gerador de Diagnóstico")
st.title("Google Meu Negócio - Tour360vr")

# Secrets
try: api_key = st.secrets["GOOGLE_API_KEY"]
except: api_key = None

if not api_key:
    api_key = st.text_input("Digite sua Chave da API Google (Places API):", type="password")

with st.form("form_busca"):
    col1, col2 = st.columns([3, 2])
    empresa = st.text_input("Nome da Empresa:", placeholder="Ex: Amazone Açaí Shop")
    cidade = st.text_input("Cidade / Estado:", placeholder="Ex: Brodowski / SP")
    btn = st.form_submit_button("Gerar Relatório Executivo em PDF")

# Função de limpeza
def clean(val):
    return str(val if val is not None else "")

class PDF(FPDF):
    def header(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 0, 210, 28, "F")
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 5)
        self.cell(0, 8, "Tour360vr", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(186, 230, 253)
        self.set_xy(10, 16)
        self.cell(0, 4, "DIAGNÓSTICO E AUDITORIA GOOGLE MEU NEGÓCIO", align="C", new_x="LMARGIN", new_y="NEXT")

    def footer(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 285, 210, 12, "F")
        self.set_y(-8.5)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(224, 242, 254)
        self.cell(0, 5, "contato@tour360vr.com.br · 16991332121 · tour360vr.com.br · Ribeirão Preto - SP", align="C")

def gerar_pdf_estavel(dados, nome_empresa):
    pdf = PDF()
    pdf.add_page()
    W = pdf.epw
    y = 35 # Posição inicial
    
    # 1. Info Empresa
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(20, 50, 135)
    pdf.rect(10, y, W, 14, "DF")
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(13, y + 2)
    pdf.cell(0, 5, clean(dados.get("name")).upper(), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.set_x(13)
    pdf.cell(0, 5, f"Endereço: {clean(dados.get('formatted_address'))}", new_x="LMARGIN", new_y="NEXT")
    
    # 2. Cards
    y += 20
    w_b, h_b = 63.3, 26
    for i, t in enumerate(["OTIMIZAÇÃO", "NOTA E REPUTAÇÃO", "TOUR VIRTUAL 360"]):
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(10 + (i * w_b), y, w_b, h_b, "DF")
        pdf.set_xy(12 + (i * w_b), y + 2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(20, 50, 135)
        pdf.cell(0, 4, t)
    
    # 3. Matriz (Y dinâmico)
    y += h_b + 5
    pdf.set_y(y)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(W, 8, "MATRIZ DE DIAGNÓSTICO", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_fill_color(20, 50, 135)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(40, 7, " Dimensão", fill=True)
    pdf.cell(70, 7, " Estado Atual", fill=True)
    pdf.cell(80, 7, " Impacto", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    for i, (d, e, imp) in enumerate([("Cadastro", "Site ativo", "Aumenta conversão"), ("Avaliações", "Nota 4.5", "Prova social"), ("Fotos", "Baixa", "Envolvimento")]):
        pdf.set_fill_color(248, 250, 252) if i % 2 != 0 else pdf.set_fill_color(255, 255, 255)
        pdf.rect(10, pdf.get_y(), W, 10, "FD")
        pdf.set_text_color(51, 65, 85)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(40, 10, f" {d}")
        pdf.cell(70, 10, f" {e}")
        pdf.cell(80, 10, f" {imp}", new_x="LMARGIN", new_y="NEXT")

    # 4. Plano Ação
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 8, "PLANO DE AÇÃO", new_x="LMARGIN", new_y="NEXT")
    for a in ["1. Implantação de Tour Virtual 360", "2. Ensaio Fotográfico", "3. Gestão de Reputação"]:
        pdf.rect(10, pdf.get_y(), W, 9, "DF")
        pdf.cell(0, 9, f" {a}", new_x="LMARGIN", new_y="NEXT")

    # 5. Final (Subido 1 linha)
    pdf.ln(7)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(W, 6, "Pronto para elevar sua visibilidade?", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.multi_cell(W, 5, "Vamos agendar uma visita, entender seus objetivos e montar um plano personalizado.\nO Tour 360° + estratégia de avaliações pode triplicar suas buscas.", align="C")

    nome_arquivo = f"Diagnóstico da ficha - {nome_empresa}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

if btn and empresa and cidade:
    # URL de busca
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={empresa}+{cidade}&key={api_key}"
    res = requests.get(url).json()
    if res.get("results"):
        place_id = res["results"][0]["place_id"]
        det_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,rating&key={api_key}"
        dados = requests.get(det_url).json().get("result", {})
        pdf_file = gerar_pdf_estavel(dados, empresa)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Baixar PDF", data=f, file_name=pdf_file, mime="application/pdf")
    else:
        st.error("Empresa não encontrada.")

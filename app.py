import datetime
import requests
import streamlit as st
from fpdf import FPDF

# Configuração
st.set_page_config(page_title="Diagnóstico - Tour360vr", layout="centered")
st.title("📍 Gerador de Diagnóstico")
st.subheader("Google Meu Negócio - Tour360vr")

try: api_key = st.secrets["GOOGLE_API_KEY"]
except: api_key = None

if not api_key:
    api_key = st.text_input("Digite sua Chave da API Google:", type="password")

with st.form("form_busca"):
    col1, col2 = st.columns([3, 2])
    empresa = st.text_input("Nome da Empresa:")
    cidade = st.text_input("Cidade / Estado:")
    btn = st.form_submit_button("Gerar Relatório em PDF")

def clean(txt):
    if txt is None: return ""
    return str(txt).encode("latin-1", "replace").decode("latin-1")

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
        self.cell(0, 4, "DIAGNÓSTICO E AUDITORIA GOOGLE MEU NEGÓCIO", align="C")

    def footer(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 285, 210, 12, "F")
        self.set_y(-8.5)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(224, 242, 254)
        # Rodapé com links distintos
        self.set_x(10)
        self.cell(50, 5, "contato@tour360vr.com.br", align="C", link="mailto:contato@tour360vr.com.br")
        self.cell(5, 5, "·", align="C")
        self.cell(30, 5, "16991332121", align="C", link="https://wa.me/5516991332121")
        self.cell(5, 5, "·", align="C")
        self.cell(30, 5, "tour360vr.com.br", align="C", link="https://tour360vr.com.br/")
        self.cell(5, 5, "·", align="C")
        self.cell(30, 5, "Ribeirão Preto - SP", align="C")

def gerar_pdf_estavel(dados, nome_empresa):
    pdf = PDF()
    pdf.add_page()
    y = 35 
    
    # Bloco 1: Empresa
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(20, 50, 135)
    pdf.rect(10, y, 190, 14, "DF")
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(13, y + 2)
    pdf.cell(0, 5, clean(dados.get("name")).upper())
    y += 7
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(13, y)
    pdf.cell(0, 5, f"Endereço: {clean(dados.get('formatted_address'))}")
    y += 20
    
    # Bloco 2: Cards
    w_b, h_b = 63.3, 26
    for i, t in enumerate(["OTIMIZAÇÃO DO PERFIL", "NOTA E REPUTAÇÃO", "TOUR VIRTUAL 360°"]):
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(10 + (i * w_b), y, w_b, h_b, "DF")
        pdf.set_xy(12 + (i * w_b), y + 2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(20, 50, 135)
        pdf.cell(w_b-4, 4, t)
    y += h_b + 5
    
    # Bloco 3: Matriz
    pdf.set_y(y)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 8, "MATRIZ DE DIAGNÓSTICO E IMPACTO COMERCIAL", ln=True)
    pdf.set_fill_color(20, 50, 135)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(40, 7, " Dimensão", fill=True)
    pdf.cell(70, 7, " Estado Atual Identificado", fill=True)
    pdf.cell(80, 7, " Impacto", fill=True, ln=True)
    
    itens = [("Cadastro", "Site ativo", "Aumenta conversão"), ("Avaliações", "Nota 4.5", "Prova social"), ("Fotos", "Baixa", "Envolvimento")]
    for i, (d, e, imp) in enumerate(itens):
        pdf.set_fill_color(248, 250, 252) if i % 2 != 0 else pdf.set_fill_color(255, 255, 255)
        pdf.rect(10, pdf.get_y(), 190, 10, "FD")
        pdf.set_text_color(51, 65, 85)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(40, 10, f" {d}")
        pdf.cell(70, 10, f" {e}")
        pdf.cell(80, 10, f" {imp}", ln=True)

    # Bloco 4: Plano
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(190, 8, "PLANO DE AÇÃO RECOMENDADO", ln=True)
    for a in ["1. Implantação de Tour Virtual 360°", "2. Ensaio Fotográfico", "3. Gestão de Reputação"]:
        pdf.rect(10, pdf.get_y(), 190, 9, "DF")
        pdf.cell(0, 9, f" {a}", ln=True)

    # Bloco 5: Final (Subi 1 linha)
    pdf.ln(6) 
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 6, "Pronto para elevar sua visibilidade?", align="C", ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.multi_cell(190, 5, "Vamos agendar uma visita, entender seus objetivos e montar um plano personalizado.\nO Tour 360° + estratégia de avaliações pode triplicar suas buscas.", align="C")

    nome_arquivo = f"Diagnóstico da ficha - {nome_empresa}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

if btn and empresa and cidade:
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={empresa}+{cidade}&key={api_key}"
    res = requests.get(url).json()
    if res.get("results"):
        place_id = res["results"][0]["place_id"]
        det_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,rating&key={api_key}"
        dados = requests.get(det_url).json().get("result", {})
        pdf_file = gerar_pdf_estavel(dados, empresa)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Baixar PDF", data=f, file_name=pdf_file, mime="application/pdf")

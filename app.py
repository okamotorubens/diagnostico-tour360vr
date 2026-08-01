import datetime
import requests
import streamlit as st
from fpdf import FPDF

# Configuração do Streamlit
st.set_page_config(page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered")

st.title("📍 Gerador de Diagnóstico")
st.title("Google Meu Negócio")
st.subheader("Tour360vr")

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

# Funções auxiliares
def clean(val, default="N/A"):
    return str(val) if val is not None else default

def buscar_dados(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()
    if not res.get("results"): return None
    p_id = res["results"][0]["place_id"]
    det_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={p_id}&fields=name,formatted_address,rating,user_ratings_total&key={key}"
    return requests.get(det_url).json().get("result", {})

# PDF Class
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
        txt = "contato@tour360vr.com.br     ·     16991332121     ·     tour360vr.com.br     ·     Ribeirão Preto - SP"
        self.cell(0, 5, txt, align="C")

# Gerador PDF
def gerar_pdf_final(dados, nome_empresa):
    pdf = PDF()
    pdf.add_page()
    W = pdf.epw
    
    # 1. Info Empresa
    y = 35
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

    # 2. Cards (Y fixo para evitar sobreposição)
    y_cards = y + 20
    w_box = 63.3
    h_box = 30
    titles = ["OTIMIZAÇÃO", "NOTA E REPUTAÇÃO", "TOUR VIRTUAL 360"]
    for i, t in enumerate(titles):
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(10 + (i * w_box), y_cards, w_box, h_box, "DF")
        pdf.set_xy(12 + (i * w_box), y_cards + 2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(20, 50, 135)
        pdf.cell(0, 4, t)
        if i == 1: # Estrelas
            rating = round(float(dados.get("rating", 0)))
            pdf.set_font("Helvetica", "B", 22)
            for k in range(5):
                pdf.set_xy(12 + (i * w_box) + (k * 8), y_cards + 12)
                pdf.set_text_color(245, 158, 11) if k < rating else pdf.set_text_color(203, 213, 225)
                pdf.cell(7, 7, "*")

    # 3. Matriz (Y relativo)
    pdf.set_y(y_cards + h_box + 5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 8, "MATRIZ DE DIAGNÓSTICO", new_x="LMARGIN", new_y="NEXT")
    
    # Cabeçalho Tabela
    pdf.set_fill_color(20, 50, 135)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(40, 7, " Dimensão", fill=True)
    pdf.cell(70, 7, " Estado Atual", fill=True)
    pdf.cell(80, 7, " Impacto", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    # Conteúdo Tabela
    for i, row in enumerate([("Cadastro", "Ativo", "Aumenta conversão"), ("Avaliações", "Nota 4.5", "Prova social"), ("Fotos", "Baixa", "Envolvimento")]):
        pdf.set_fill_color(248, 250, 252) if i % 2 != 0 else pdf.set_fill_color(255, 255, 255)
        pdf.rect(10, pdf.get_y(), W, 10, "FD")
        pdf.set_text_color(51, 65, 85)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(40, 10, f" {row[0]}")
        pdf.cell(70, 10, f" {row[1]}")
        pdf.cell(80, 10, f" {row[2]}", new_x="LMARGIN", new_y="NEXT")

    # 4. Plano Ação
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 8, "PLANO DE AÇÃO", new_x="LMARGIN", new_y="NEXT")
    for a in ["1. Implantação de Tour Virtual 360", "2. Ensaio Fotográfico", "3. Gestão de Reputação"]:
        pdf.rect(10, pdf.get_y(), W, 9, "DF")
        pdf.cell(0, 9, f" {a}", new_x="LMARGIN", new_y="NEXT")

    # 5. Final
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(W, 6, "Pronto para elevar sua visibilidade?", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.multi_cell(W, 5, "Vamos agendar uma visita, entender seus objetivos e montar um plano personalizado.\nO Tour 360° + estratégia de avaliações pode triplicar suas buscas.", align="C")

    nome_arquivo = f"Diagnóstico da ficha - {nome_empresa}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

if btn and empresa and cidade:
    dados = buscar_dados(empresa, cidade, api_key)
    if dados:
        arquivo = gerar_pdf_final(dados, empresa)
        with open(arquivo, "rb") as f:
            st.download_button("📥 Baixar PDF", data=f, file_name=arquivo, mime="application/pdf")
    else:
        st.error("Empresa não encontrada.")

import datetime
import requests
import streamlit as st
from fpdf import FPDF

# 1. Configuração do App
st.set_page_config(page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered")
st.title("📍 Gerador de Diagnóstico")
st.title("Google Meu Negócio")
st.subheader("Tour360vr")

# 2. Configuração API
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    api_key = st.text_input("Digite sua Chave da API Google (Places API):", type="password")

# 3. Formulário
with st.form("form_busca"):
    col1, col2 = st.columns([3, 2])
    empresa = st.text_input("Nome da Empresa:", placeholder="Ex: Amazone Açaí Shop")
    cidade = st.text_input("Cidade / Estado:", placeholder="Ex: Brodowski / SP")
    btn = st.form_submit_button("Gerar Relatório Executivo em PDF")

# 4. Classe PDF com estrutura modular
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
        self.set_xy(130, 20)
        self.cell(70, 5, datetime.date.today().strftime('%d/%m/%Y'), align="R")
        self.set_y(35) # Margem superior para começar o conteúdo

    def footer(self):
        self.set_fill_color(20, 50, 135)
        self.rect(0, 285, 210, 12, "F")
        self.set_y(-8.5)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(224, 242, 254)
        txt = "contato@tour360vr.com.br     ·     16991332121     ·     tour360vr.com.br     ·     Ribeirão Preto - SP"
        self.cell(0, 5, txt, align="C")

# 5. Função de Geração do PDF
def gerar_relatorio(dados, nome_empresa):
    pdf = PDF()
    pdf.add_page()
    W = pdf.epw
    
    # Bloco 1: Empresa
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(20, 50, 135)
    pdf.rect(10, pdf.get_y(), W, 14, "DF")
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(13, pdf.get_y() + 1.5)
    pdf.cell(0, 5, str(dados.get("name", "N/A")).upper(), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.set_x(13)
    pdf.cell(0, 5, f"Endereço: {dados.get('formatted_address', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)

    # Bloco 2: Cards
    y_cards = pdf.get_y()
    w_box, h_box = 63.3, 30.0
    for i, t in enumerate(["OTIMIZAÇÃO", "NOTA E REPUTAÇÃO", "TOUR VIRTUAL 360"]):
        pdf.set_draw_color(20, 50, 135)
        pdf.rect(10 + (i * w_box), y_cards, w_box, h_box, "DF")
        pdf.set_xy(12 + (i * w_box), y_cards + 2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(20, 50, 135)
        pdf.cell(0, 4, t)
    
    pdf.set_y(y_cards + h_box + 5)

    # Bloco 3: Tabela
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 8, "MATRIZ DE DIAGNÓSTICO", new_x="LMARGIN", new_y="NEXT")
    pdf.set_fill_color(20, 50, 135)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(40, 7, " Dimensão", fill=True)
    pdf.cell(70, 7, " Estado Atual", fill=True)
    pdf.cell(80, 7, " Impacto", fill=True, new_x="LMARGIN", new_y="NEXT")
    
    for i, (d, e, imp) in enumerate([("Cadastro", "Ativo", "Aumenta conversão"), ("Avaliações", "Nota 4.5", "Prova social"), ("Fotos", "Baixa", "Envolvimento")]):
        pdf.set_fill_color(248, 250, 252) if i % 2 != 0 else pdf.set_fill_color(255, 255, 255)
        pdf.rect(10, pdf.get_y(), W, 10, "FD")
        pdf.set_text_color(51, 65, 85)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(40, 10, f" {d}")
        pdf.cell(70, 10, f" {e}")
        pdf.cell(80, 10, f" {imp}", new_x="LMARGIN", new_y="NEXT")

    # Bloco 4: Plano
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 8, "PLANO DE AÇÃO", new_x="LMARGIN", new_y="NEXT")
    for a in ["1. Implantação de Tour Virtual 360", "2. Ensaio Fotográfico", "3. Gestão de Reputação"]:
        pdf.rect(10, pdf.get_y(), W, 9, "DF")
        pdf.cell(0, 9, f" {a}", new_x="LMARGIN", new_y="NEXT")

    # Bloco 5: Final
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(W, 6, "Pronto para elevar sua visibilidade?", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.multi_cell(W, 5, "Vamos agendar uma visita, entender seus objetivos e montar um plano personalizado.\nO Tour 360° + estratégia de avaliações pode triplicar suas buscas.", align="C")

    nome_arquivo = f"Diagnóstico da ficha - {nome_empresa}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# 6. Lógica de execução
if btn and empresa and cidade:
    # Simulação de busca
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={empresa}+{cidade}&key={api_key}"
    res = requests.get(url).json()
    if res.get("results"):
        place_id = res["results"][0]["place_id"]
        det_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,rating&key={api_key}"
        dados = requests.get(det_url).json().get("result", {})
        pdf_file = gerar_relatorio(dados, empresa)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Baixar PDF", data=f, file_name=pdf_file, mime="application/pdf")

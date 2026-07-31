import datetime
from fpdf import FPDF
import requests
import streamlit as st

st.set_page_config(
    page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered"
)

st.title("📍 Gerador de Diagnóstico Google Meu Negócio")
st.subheader("Ferramenta de Prospecção Tour360vr")

# Recupera a chave salva nos Secrets do Streamlit Cloud
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    api_key = st.text_input(
        "Digite sua Chave da API Google (Places API):", type="password"
    )

with st.form("form_busca"):
    empresa = st.text_input(
        "Nome da Empresa:", placeholder="Ex: Amazone Açaí Shop"
    )
    cidade = st.text_input(
        "Cidade / Estado:", placeholder="Ex: Brodowski / SP"
    )
    btn = st.form_submit_button("Gerar Diagnóstico em PDF")


def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()

    if not res.get("results"):
        return None

    place_id = res["results"][0]["place_id"]
    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website&key={key}"
    return requests.get(url_details).json().get("result", {})


def clean_text(text):
    """Converte texto para o encode Latin-1 aceito nativamente pelo FPDF (Helvetica/Arial)"""
    if not text:
        return ""
    return (
        str(text)
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


class PDF(FPDF):

    def header(self):
        # Cabeçalho Azul Escuro
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 32, "F")

        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(0, 8, clean_text("Tour360vr"), new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 8)
        self.set_text_color(56, 189, 248)
        self.cell(
            0,
            4,
            clean_text("TECNOLOGIA E EXPERIENCIAS IMERSIVAS | DIAGNOSTICO LOCAL"),
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.set_y(38)

    def footer(self):
        # Rodapé Fixado na parte inferior
        self.set_y(-15)
        self.set_fill_color(15, 23, 42)
        self.rect(0, 282, 210, 15, "F")
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 284)
        self.cell(
            0,
            10,
            clean_text("www.tour360vr.com.br | Relatorio de Uso Exclusivo Comercial"),
            align="C",
        )


def criar_pdf(dados):
    pdf = PDF()
    pdf.set_margins(10, 10, 10)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    nome = dados.get("name", "N/A")
    endereco = dados.get("formatted_address", "N/A")
    telefone = dados.get("formatted_phone_number", "Não informado")
    rating = dados.get("rating", "N/A")
    reviews = dados.get("user_ratings_total", 0)
    photos = len(dados.get("photos", []))

    largura = pdf.epw

    # Título Principal
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(
        largura,
        8,
        clean_text(f"DIAGNOSTICO DE PRESENCA DIGITAL: {nome.upper()}"),
        new_x="LMARGIN",
        new_y="NEXT",
        border="B",
    )
    pdf.ln(4)

    # Bloco 1: Dados Coletados
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(2, 132, 199)
    pdf.cell(
        largura,
        6,
        clean_text("1. DADOS IDENTIFICADOS NO GOOGLE MAPS:"),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(largura, 5, clean_text(f"Endereco: {endereco}"))
    pdf.multi_cell(largura, 5, clean_text(f"Telefone: {telefone}"))
    pdf.multi_cell(
        largura,
        5,
        clean_text(f"Nota Media: {rating} estrelas | Total de Avaliacoes: {reviews}"),
    )
    pdf.multi_cell(largura, 5, clean_text(f"Fotos Publicadas na Ficha: {photos} fotos"))
    pdf.ln(5)

    # Bloco 2: Oportunidades
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(185, 28, 28)
    pdf.cell(
        largura,
        6,
        clean_text("2. PONTOS DE ATENCAO E OPORTUNIDADES:"),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)

    if photos < 15:
        pdf.multi_cell(
            largura,
            5,
            clean_text("[X] Pouca variedade visual: O perfil possui poucas fotos do espaço interno e da estrutura."),
        )

    try:
        if float(rating) < 4.5:
            pdf.multi_cell(
                largura,
                5,
                clean_text("[X] Reputacao abaixo do ideal: Pontuacao abaixo de 4.5 estrelas reduz a conversao de novos clientes."),
            )
    except ValueError:
        pass

    pdf.multi_cell(
        largura,
        5,
        clean_text("[X] Ausencia de Experiencia Imersiva 360: O perfil nao possui Tour Virtual 360 interativo integrado."),
    )
    pdf.ln(5)

    # Bloco 3: Plano de Ação Tour360vr
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(
        largura,
        6,
        clean_text("3. PLANO DE ACAO RECOMENDADO (TOUR360VR):"),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(
        largura,
        5,
        clean_text(
            "1. Implantacao de Tour Virtual 360: Aumenta o tempo de permanencia no perfil e melhora o ranqueamento organico no Google Maps.\n"
            "2. Ensaio Fotografico Profissional: Fotografias em alta resolucao destacando fachada, interior e produtos.\n"
            "3. Otimizacao e Padronizacao: Atualizacao dos dados cadastrais (NAP) para fortalecer o SEO Local."
        ),
    )

    pdf.output("diagnostico.pdf")
    return "diagnostico.pdf"


if btn and empresa and cidade:
    if not api_key:
        st.error("Chave da API do Google não configurada.")
    else:
        with st.spinner("Buscando dados no Google e gerando relatório..."):
            dados = buscar_dados_google(empresa, cidade, api_key)
            if dados:
                pdf_file = criar_pdf(dados)
                st.success("Diagnóstico gerado com sucesso!")

                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📥 Baixar Relatório em PDF",
                        data=f,
                        file_name=f"Diagnostico_{dados.get('name')}.pdf",
                        mime="application/pdf",
                    )
            else:
                st.error("Empresa não encontrada no Google Maps.")

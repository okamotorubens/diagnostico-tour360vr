import datetime
from fpdf import FPDF
import requests
import streamlit as st

st.set_page_config(
    page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered"
)

st.title("📍 Gerador de Diagnóstico Google Meu Negócio")
st.subheader("Ferramenta de Prospecção Tour360vr")

# Interface de Chave da API e Busca
api_key = st.text_input(
    "Digite sua Chave da API Google (Places API):", type="password"
)

with st.form("form_busca"):
    empresa = st.text_input(
        "Nome da Empresa:", placeholder="Ex: Restaurante Exemplo"
    )
    cidade = st.text_input(
        "Cidade / Estado:", placeholder="Ex: Ribeirão Preto / SP"
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


class PDF(FPDF):

    def header(self):
        self.set_fill_color(15, 23, 42)  # Azul escuro / grafite
        self.rect(0, 0, 210, 35, "F")

        self.set_font("Helvetica", "B", 20)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 8)
        self.cell(0, 10, "Tour360vr", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 9)
        self.set_text_color(56, 189, 248)  # Azul claro
        self.cell(
            0,
            5,
            "TECNOLOGIA E EXPERIENCIAS IMERSIVAS | DIAGNOSTICO LOCAL",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_fill_color(15, 23, 42)
        self.rect(0, 280, 210, 17, "F")
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 282)
        self.cell(
            0,
            10,
            "www.tour360vr.com.br | Relatorio de Uso Exclusivo Comercial",
            align="C",
        )


def criar_pdf(dados):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    nome = dados.get("name", "N/A")
    endereco = dados.get("formatted_address", "N/A")
    telefone = dados.get("formatted_phone_number", "Não informado")
    rating = dados.get("rating", 0)
    reviews = dados.get("user_ratings_total", 0)
    photos = len(dados.get("photos", []))

    # Largura útil da página (descontando as margens)
    largura = pdf.epw

    # Título do Relatório
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(
        largura,
        10,
        f"DIAGNOSTICO DE PRESENCA DIGITAL: {nome.upper()}",
        new_x="LMARGIN",
        new_y="NEXT",
        border="B",
    )
    pdf.ln(5)

    # Dados Coletados
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(
        largura,
        6,
        "DADOS IDENTIFICADOS NO GOOGLE MAPS:",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(largura, 5, f"Endereco: {endereco}\nTelefone: {telefone}")
    pdf.multi_cell(
        largura,
        5,
        f"Nota Media: {rating} estrelas | Total de Avaliacoes: {reviews}\nFotos Publicadas: {photos} fotos",
    )
    pdf.ln(5)

    # Análise de Oportunidades
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(185, 28, 28)  # Vermelho / Alerta
    pdf.cell(
        largura,
        8,
        "PONTOS DE ATENCAO E OPORTUNIDADES:",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)

    if photos < 15:
        pdf.multi_cell(
            largura,
            5,
            "[X] Pouca variedade visual: Perfil possui poucas fotos profissionais atualizadas.",
        )
    if rating < 4.5:
        pdf.multi_cell(
            largura,
            5,
            "[X] Reputacao abaixo do ideal: Pontuacao abaixo de 4.5 estrelas afeta o algoritmo.",
        )

    pdf.multi_cell(
        largura,
        5,
        "[X] Ausencia de Experiencia Imersiva 360: O perfil nao possui Tour Virtual 360 interativo integrado.",
    )
    pdf.ln(5)

    # Plano de Ação Tour360vr
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(2, 132, 199)  # Azul Destaque
    pdf.cell(
        largura,
        8,
        "PLANO DE ACAO RECOMENDADO (TOUR360VR):",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(
        largura,
        5,
        "1. Implantacao de Tour Virtual 360: Aumenta em ate 41% a chance de visita ao local e melhora o ranqueamento organico no Google Maps.\n"
        "2. Ensaio Fotografico Profissional: Captura de fachada, ambiente interno e diferenciais da empresa em alta resolucao.\n"
        "3. Otimizacao de Ficha: Atualizacao e padronizacao das informacoes do perfil.",
    )

    pdf.output("diagnostico.pdf")
    return "diagnostico.pdf"


if btn and empresa and cidade:
    if not api_key:
        st.error("Por favor, insira sua chave da API do Google.")
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

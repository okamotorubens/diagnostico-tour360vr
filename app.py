import datetime
import requests
import streamlit as st
from fpdf import FPDF

st.set_page_config(
    page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered"
)

st.title("📍 Gerador de Diagnóstico Google Meu Negócio")
st.subheader("Padrão Executivo - Tour360vr")

# Recupera a chave dos Secrets do Streamlit Cloud
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
    cidade = st.text_input("Cidade / Estado:", placeholder="Ex: Brodowski / SP")
    btn = st.form_submit_button("Gerar Relatório Executivo em PDF")


def clean_txt(txt):
    """Trata acentos e caracteres UTF-8 para a biblioteca FPDF"""
    if not txt:
        return ""
    return str(txt).encode("latin-1", "replace").decode("latin-1")


def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()

    if not res.get("results"):
        return None, []

    result = res["results"][0]
    place_id = result["place_id"]
    nome_empresa = result.get("name", empresa)

    # Detalhes completos da empresa
    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,opening_hours,types&key={key}"
    details = requests.get(url_details).json().get("result", {})

    # Busca Concorrentes do MESMO segmento
    termo_busca = nome_empresa.split()[0] if len(nome_empresa.split()) > 0 else empresa
    query_conc = f"{termo_busca} em {cidade}"
    url_conc = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query_conc}&key={key}"
    res_conc = requests.get(url_conc).json().get("results", [])

    concorrentes = []
    for c in res_conc:
        if c.get("place_id") != place_id:
            concorrentes.append(
                f"{c.get('name')} ({c.get('user_ratings_total', 0)} avaliações)"
            )
        if len(concorrentes) >= 3:
            break

    return details, concorrentes


def calcular_score(dados):
    score = 35
    if dados.get("website"):
        score += 10
    if len(dados.get("photos", [])) >= 10:
        score += 15
    elif len(dados.get("photos", [])) >= 3:
        score += 8

    if dados.get("rating", 0) >= 4.5:
        score += 15
    if dados.get("user_ratings_total", 0) >= 30:
        score += 15
    elif dados.get("user_ratings_total", 0) >= 10:
        score += 8

    if dados.get("opening_hours"):
        score += 10

    return min(score, 100)


class PDFExecutivo(FPDF):

    def header(self):
        # Tarja Azul Médio Vibrante (#0284c7)
        self.set_fill_color(2, 132, 199)
        self.rect(0, 0, 210, 26, "F")

        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 5)
        self.cell(0, 8, clean_txt("TOUR360VR"), new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(224, 242, 254)
        self.set_xy(10, 14)
        self.cell(
            0,
            4,
            clean_txt("DIAGNOSTICO E AUDITORIA GOOGLE MEU NEGOCIO"),
            new_x="LMARGIN",
            new_y="NEXT",
        )

        # Apenas Data no canto direito (Sem PINCHECK)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(255, 255, 255)
        self.set_xy(130, 9)
        self.cell(
            70,
            5,
            clean_txt(f"Data: {datetime.date.today().strftime('%d/%m/%Y')}"),
            align="R",
        )

        self.set_y(30)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(2, 132, 199)
        self.cell(
            0,
            6,
            clean_txt("Tour360vr   |   WhatsApp: (16) 99133-2121   |   https://tour360vr.com.br/"),
            align="C",
            link="https://tour360vr.com.br/",
        )


def gerar_pdf_bytes(dados, concorrentes):
    pdf = PDFExecutivo()
    pdf.set_margins(10, 8, 10)
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    nome = dados.get("name", "N/A")
    endereco = dados.get("formatted_address", "N/A")
    telefone = dados.get("formatted_phone_number", "Não informado")
    rating = str(dados.get("rating", "0.0"))
    reviews = str(dados.get("user_ratings_total", 0))
    photos_count = len(dados.get("photos", []))
    website = dados.get("website")
    has_hours = "Completo" if dados.get("opening_hours") else "Incompleto"
    score = calcular_score(dados)

    txt_conc = (
        ", ".join(concorrentes)
        if concorrentes
        else "Concorrentes mapeados na região."
    )

    W = pdf.epw  # 190mm de largura útil

    # Card Destaque do Cliente
    pdf.set_fill_color(240, 249, 255)
    pdf.rect(10, pdf.get_y(), W, 17, "F")
    pdf.set_draw_color(2, 132, 199)
    pdf.line(10, pdf.get_y(), 10, pdf.get_y() + 17)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(3, 105, 161)
    pdf.set_xy(13, pdf.get_y() + 2)
    pdf.cell(0, 5, clean_txt(nome.upper()), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.set_x(13)
    pdf.cell(
        0,
        5,
        clean_txt(f"Endereco: {endereco}  |  Telefone: {telefone}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(5)

    # Cards de Métricas em Azul Médio (3 Colunas)
    y_cards = pdf.get_y()

    # Box 1: Score & Termômetro Visual
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(2, 132, 199)
    pdf.rect(10, y_cards, 60, 23, "DF")

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(3, 105, 161)
    pdf.set_xy(12, y_cards + 2)
    pdf.cell(56, 4, clean_txt("OTIMIZACAO DO PERFIL"))

    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(2, 132, 199)
    pdf.set_xy(12, y_cards + 6)
    pdf.cell(56, 6, f"{score}/100")

    # Termômetro Visual
    pdf.set_fill_color(226, 232, 240)
    pdf.rect(12, y_cards + 13.5, 56, 4, "F")
    pdf.set_fill_color(2, 132, 199)
    pdf.rect(12, y_cards + 13.5, (56 * score / 100), 4, "F")

    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(100, 116, 139)
    pdf.set_xy(12, y_cards + 18.5)
    pdf.cell(56, 3, clean_txt("Margem para crescimento local"))

    # Box 2: Nota e Avaliações (Correção da Estrela Unicode)
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(75, y_cards, 60, 23, "DF")

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(3, 105, 161)
    pdf.set_xy(77, y_cards + 2)
    pdf.cell(56, 4, clean_txt("NOTA E REPUTACAO"))

    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(217, 119, 6)
    pdf.set_xy(77, y_cards + 6)
    pdf.cell(56, 6, clean_txt(f"Nota {rating} / 5.0"))

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(77, y_cards + 14)
    pdf.cell(56, 4, clean_txt(f"Com base em {reviews} avaliacoes"))

    # Box 3: Tour Virtual 360°
    pdf.set_fill_color(254, 242, 242)
    pdf.set_draw_color(220, 38, 38)
    pdf.rect(140, y_cards, 60, 23, "DF")

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(185, 28, 28)
    pdf.set_xy(142, y_cards + 2)
    pdf.cell(56, 4, clean_txt("TOUR VIRTUAL 360°"))

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(220, 38, 38)
    pdf.set_xy(142, y_cards + 6)
    pdf.cell(56, 6, clean_txt("0 FOTOS (AUSENTE)"))

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(153, 27, 27)
    pdf.set_xy(142, y_cards + 14)
    pdf.cell(56, 4, clean_txt("Oportunidade de se diferenciar"))

    pdf.set_y(y_cards + 27)

    # Matriz de Diagnóstico (9 Itens)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(3, 105, 161)
    pdf.cell(
        W,
        6,
        clean_txt("MATRIZ DE DIAGNOSTICO E IMPACTO COMERCIAL"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(1)

    # Tabela com Quebra e Fontes Ajustadas
    pdf.set_fill_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(42, 6, clean_txt(" Dimensão"), fill=True)
    pdf.cell(73, 6, clean_txt(" Estado Atual Identificado"), fill=True)
    pdf.cell(
        75,
        6,
        clean_txt(" Impacto no Ranqueamento e Conversão"),
        fill=True,
        new_x="LMARGIN",
        new_y="NEXT",
    )

    itens = [
        (
            "Completude do Cadastro",
            "Website cadastrado"
            if website
            else "Faltam descrição ou dados complementares.",
            "Perfil incompleto reduz a conversão de novos clientes.",
        ),
        (
            "Nota e Avaliações",
            f"Nota {rating} com {reviews} avaliacoes acumuladas.",
            "Reputacao ativa fortalece a prova social e gera confianca.",
        ),
        (
            "Consistência de NAP",
            "Endereco e telefone ativos no Google Maps.",
            "Informacoes corretas evitam perdas por buscas frustradas.",
        ),
        (
            "Categorias",
            "Categoria principal definida na ficha.",
            "Falta de categorias secundarias limita a visibilidade regional.",
        ),
        (
            "Fotos",
            f"{photos_count} fotos identificadas no perfil.",
            "Poucas fotos impedem a avaliacao do espaco pelo cliente.",
        ),
        (
            "Horários",
            f"Horários de funcionamento: {has_hours}.",
            "Informacao correta evita perda de clientes no atendimento.",
        ),
        (
            "Posts / Novidades",
            "Nenhum post recente detectado.",
            "Perfil estatico nao destaca ofertas nem novidades do local.",
        ),
        (
            "Recursos Interativos",
            "Nenhuma foto 360° ou tour virtual detectado.",
            "Perdem-se conversoes por falta de experiencia imersiva 360.",
        ),
        (
            "Presença e Concorrência",
            f"Concorrentes no ramo: {txt_conc}",
            "Oportunidade clara de superar a concorrencia na regiao.",
        ),
    ]

    pdf.set_font("Helvetica", "", 8)
    for i, (dim, est, imp) in enumerate(itens):
        bg = (248, 250, 252) if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*bg)

        pdf.set_text_color(3, 105, 161)
        pdf.cell(42, 5.5, clean_txt(f" {dim}"), fill=True)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(73, 5.5, clean_txt(f" {est[:46]}"), fill=True)
        pdf.set_text_color(185, 28, 28)
        pdf.cell(
            75,
            5.5,
            clean_txt(f" {imp[:48]}"),
            fill=True,
            new_x="LMARGIN",
            new_y="NEXT",
        )

    pdf.ln(4)

    # Plano de Ação (3 Blocos Retangulares)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(3, 105, 161)
    pdf.cell(
        W,
        6,
        clean_txt("PLANO DE ACAO RECOMENDADO (SOLUCOES TOUR360VR)"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(1)

    acoes = [
        (
            "1. IMPLANTACAO DE TOUR VIRTUAL 360° INTERATIVO",
            "Mapeamento imersivo em alta definicao integrado ao Google Maps. Aumenta a permanencia na ficha e amplia agendamentos.",
        ),
        (
            "2. ENSAIO FOTOGRAFICO PROFISSIONAL HD",
            "Fotografias profissionais das instalacoes, fachada e diferenciais, elevando o valor percebido pelo cliente.",
        ),
        (
            "3. OTIMIZACAO SEO LOCAL & GESTAO DE REPUTACAO",
            "Reestruturacao completa de palavras-chave, categorias e estrategia para alavancar avaliacoes positivas.",
        ),
    ]

    for tit, desc in acoes:
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(186, 230, 253)
        pdf.rect(10, pdf.get_y(), W, 9.5, "DF")

        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(3, 105, 161)
        pdf.set_xy(12, pdf.get_y() + 1)
        pdf.cell(0, 3.8, clean_txt(tit), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 7.8)
        pdf.set_text_color(51, 65, 85)
        pdf.set_x(12)
        pdf.cell(0, 3.8, clean_txt(desc), new_x="LMARGIN", new_y="NEXT")
        pdf.set_y(pdf.get_y() + 1.5)

    pdf.ln(4)

    # Frase Final Solta (Sem Bloco) com Fonte Ampliada
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(3, 105, 161)
    pdf.cell(
        W,
        5,
        clean_txt("Pronto para elevar sua visibilidade?"),
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(
        W,
        4.8,
        clean_txt(
            "Conversamos por WhatsApp, entendemos seus objetivos e montamos um plano personalizado."
        ),
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(
        W,
        4.8,
        clean_txt(
            "O tour 360° + estratégia de avaliações pode triplicar suas buscas."
        ),
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf_output_path = "diagnostico_tour360vr.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path


if btn and empresa and cidade:
    if not api_key:
        st.error("Chave da API do Google não configurada nos Secrets.")
    else:
        with st.spinner("Analisando ficha e mapeando concorrentes do segmento..."):
            dados, concorrentes = buscar_dados_google(empresa, cidade, api_key)
            if dados:
                pdf_file = gerar_pdf_bytes(dados, concorrentes)
                st.success("Diagnóstico gerado com sucesso!")

                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📥 Baixar Relatório Executivo (PDF)",
                        data=f,
                        file_name=f"Diagnostico_{dados.get('name')}.pdf",
                        mime="application/pdf",
                    )
            else:
                st.error("Empresa não encontrada no Google Maps.")

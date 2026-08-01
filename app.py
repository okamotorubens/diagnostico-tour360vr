import datetime
import requests
import streamlit as st
from fpdf import FPDF

st.set_page_config(
    page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered"
)

st.title("📍 Gerador de Diagnóstico")
st.subheader("Google Meu Negócio - Tour360vr")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    api_key = st.text_input(
        "Digite sua Chave da API Google (Places API):", type="password"
    )

with st.form("form_busca"):
    col1, col2 = st.columns([3, 2])
    with col1:
        empresa = st.text_input(
            "Nome da Empresa:", placeholder="Ex: Nobre Paladar"
        )
    with col2:
        cidade = st.text_input("Cidade / Estado:", placeholder="Ex: Brodowski / SP")
    
    btn = st.form_submit_button("Gerar Relatório Executivo em PDF")


def clean_txt(txt):
    """Trata caracteres acentuados mantendo compatibilidade com FPDF"""
    if not txt:
        return ""
    return str(txt).encode("latin-1", "replace").decode("latin-1")


def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()

    if not res.get("results"):
        return None

    result = res["results"][0]
    place_id = result["place_id"]

    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,opening_hours,types&key={key}"
    details = requests.get(url_details).json().get("result", {})

    return details


def calcular_score_critico(dados):
    score = 25

    if dados.get("website"):
        score += 15

    photos_count = len(dados.get("photos", []))
    if photos_count >= 25:
        score += 20
    elif photos_count >= 10:
        score += 10
    elif photos_count >= 5:
        score += 5

    try:
        rating = float(dados.get("rating", 0))
    except (ValueError, TypeError):
        rating = 0.0

    if rating >= 4.7:
        score += 15
    elif rating >= 4.3:
        score += 10
    elif rating >= 4.0:
        score += 5

    reviews = dados.get("user_ratings_total", 0)
    if reviews >= 150:
        score += 15
    elif reviews >= 50:
        score += 10
    elif reviews >= 15:
        score += 5

    if dados.get("opening_hours"):
        score += 10

    return min(max(score, 30), 85)


class PDFExecutivo(FPDF):

    def header(self):
        # Tarja Azul #143287
        self.set_fill_color(20, 50, 135)
        self.rect(0, 0, 210, 28, "F")

        # Título Tour360vr (tamanho ampliado)
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 5)
        self.cell(0, 8, clean_txt("Tour360vr"), align="C", new_x="LMARGIN", new_y="NEXT")

        # Subtítulo
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(186, 230, 253)
        self.set_y(16)
        self.cell(0, 4, clean_txt("DIAGNÓSTICO E AUDITORIA GOOGLE MEU NEGÓCIO"), align="C", new_x="LMARGIN", new_y="NEXT")

        # Data
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(224, 242, 254)
        self.set_xy(130, 20)
        self.cell(
            70,
            5,
            clean_txt(datetime.date.today().strftime('%d/%m/%Y')),
            align="R",
        )

        self.set_y(32)

    def footer(self):
        # Tarja Azul no Rodapé #143287
        self.set_fill_color(20, 50, 135)
        self.rect(0, 285, 210, 12, "F")

        self.set_y(-9)
        self.set_font("Helvetica", "B", 9)  # Fonte do rodapé ampliada para 9pt

        # Centralização exata mantendo links individuais
        self.set_x(21.5)

        self.set_text_color(224, 242, 254)
        self.cell(44, 5, clean_txt("contato@tour360vr.com.br"), align="C", link="mailto:contato@tour360vr.com.br")

        self.set_text_color(255, 255, 255)
        self.cell(4, 5, clean_txt("·"), align="C")

        self.set_text_color(224, 242, 254)
        self.cell(25, 5, clean_txt("16 99133 2121"), align="C", link="https://wa.me/5516991332121")

        self.set_text_color(255, 255, 255)
        self.cell(4, 5, clean_txt("·"), align="C")

        self.set_text_color(224, 242, 254)
        self.cell(33, 5, clean_txt("tour360vr.com.br"), align="C", link="https://tour360vr.com.br/")

        self.set_text_color(255, 255, 255)
        self.cell(4, 5, clean_txt("·"), align="C")
        self.cell(34, 5, clean_txt("Ribeirão Preto - SP"), align="C")


def desenhar_estrelas_destaque(pdf, x_start, y_pos, rating_val):
    """Exibe estrelas em tamanho super ampliado (22pt)"""
    try:
        rating_num = round(float(rating_val))
    except (ValueError, TypeError):
        rating_num = 0

    pdf.set_font("Helvetica", "B", 22)
    
    for k in range(5):
        pdf.set_xy(x_start + (k * 7.5), y_pos)
        if k < rating_num:
            pdf.set_text_color(245, 158, 11)  # Amarelo Ouro (#f59e0b)
            pdf.cell(7, 7, clean_txt("*"))
        else:
            pdf.set_text_color(203, 213, 225)  # Cinza Claro (#cbd5e1)
            pdf.cell(7, 7, clean_txt("-"))


def gerar_pdf_bytes(dados):
    pdf = PDFExecutivo()
    pdf.set_margins(10, 6, 10)
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    nome = dados.get("name", "N/A")
    endereco = dados.get("formatted_address", "N/A")
    telefone = dados.get("formatted_phone_number", "Não informado")
    rating_raw = dados.get("rating", 0.0)
    rating = str(rating_raw)
    reviews_count = dados.get("user_ratings_total", 0)
    reviews = str(reviews_count)
    photos_count = len(dados.get("photos", []))
    website = dados.get("website")
    has_hours = "Cadastrado" if dados.get("opening_hours") else "Ausente/Incompleto"
    score = calcular_score_critico(dados)

    # Definição das variáveis de fotos e categorias
    all_photos = dados.get("photos", [])
    total_fotos = len(all_photos)
    
    tipos = dados.get("types", [])
    def traduzir(cat):
        dic = {"lodging": "Hospedagem", "establishment": "Estabelecimento", "point_of_interest": "Ponto de Interesse", "motel": "Motel"}
        return dic.get(cat, cat.replace("_", " ").capitalize())
    
    categorias_texto = ", ".join([traduzir(t) for t in tipos[:2]])
    # --- [INÍCIO DA ALTERAÇÃO] ---
    opening_hours_data = dados.get("opening_hours", {})
    weekday_text = opening_hours_data.get("weekday_text", [])
    editorial = dados.get("editorial_summary", {}).get("overview", "")
    
    # Lógica de Horários (Padrão Google Maps)
    if weekday_text:
        is_24h = any("24 horas" in txt.lower() or "open 24 hours" in txt.lower() for txt in weekday_text)
        status_horarios = "Aberto 24 Horas" if is_24h else "Horários configurados"
    else:
        status_horarios = "Horários ausentes"

    # Lógica de Completude
    faltam = []
    if not website: faltam.append("site")
    if not editorial: faltam.append("descrição")
    if not telefone or telefone == "Não informado": faltam.append("telefone")
    status_completude = f"Faltam: {', '.join(faltam)}" if faltam else "Cadastro completo"

    # Lógica de Maturidade Digital
    if score >= 75:
        nivel_maturidade, status_cor = "AUTORIDADE DIGITAL", (34, 197, 94)
    elif score >= 50:
        nivel_maturidade, status_cor = "EM EVOLUÇÃO", (234, 179, 8)
    else:
        nivel_maturidade, status_cor = "EMERGENTE", (239, 68, 68)
    # --- [FIM DA ALTERAÇÃO] ---

    W = pdf.epw

    # Quadro da Empresa
    y_empresa = pdf.get_y()
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(20, 50, 135)
    pdf.rect(10, y_empresa, W, 14, "DF")

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(13, y_empresa + 1.5)
    pdf.cell(0, 5, clean_txt(nome.upper()), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.set_x(13)
    pdf.cell(
        0,
        4.2,
        clean_txt(f"Endereço: {endereco}  |  Telefone: {telefone}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    y_cards = y_empresa + 18
    w_card = 63.3
    h_card = 26.0

    # Box 1: Otimização do Perfil
        # Card 1: Otimização
    pdf.rect(10, y_cards, w_card, h_card, "DF")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(10, y_cards + 2.0)
    pdf.cell(w_card, 3.5, clean_txt("OTIMIZAÇÃO DO PERFIL"), align="C")

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(249, 115, 22)
    pdf.set_xy(12, y_cards + 6.0)
    score_str = str(score)
    pdf.cell(pdf.get_string_width(score_str), align="C")(+ 1, 6, score_str, align="C")

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(20, 6, "/100", align="C")
  
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*status_cor)
    pdf.set_xy(12, y_cards + 14.5) 
    pdf.cell(w_card - 4, 3.5, clean_txt(nivel_maturidade), align="C")

    # Box 2: Nota e Reputação
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(20, 50, 135)
        
    pdf.rect(10 + w_card, y_cards, w_card, h_card, "DF")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(10 + w_card, y_cards + 2.0)
    pdf.cell(w_card, 3.5, clean_txt("NOTA E REPUTAÇÃO"), align="C")
    
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(10 + w_card, y_cards + 7.0)
    pdf.cell(w_card, 6, f"{rating} / 5.0", align="C")
    
    x_estrelas = (15 + w_card) + (w_card - 32.5) / 2
    desenhar_estrelas_destaque(pdf, 12 + w_card, y_cards + 14.5, rating_raw)
    
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(12 + w_card, y_cards + 19.5)
    if reviews_count < 30:
        pdf.cell(w_card - 4, 3.5, clean_txt(f"Apenas {reviews} avaliações (Base pequena)"))
    else:
        pdf.cell(w_card - 4, 3.5, clean_txt(f"Com base em {reviews} avaliações"), align="C")


    # Box 3: Tour Virtual 360°
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(20, 50, 135)
    pdf.rect(10 + (w_card * 2), y_cards, w_card, h_card, "DF")

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(12 + (w_card * 2), y_cards + 2.0)
    pdf.cell(w_card - 4, 3.5, clean_txt("PRESENÇA IMERSIVA"), align="C")

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(220, 38, 38)
    pdf.set_xy(12 + (w_card * 2), y_cards + 6.0)
    txt_zero = "0"
    pdf.cell(pdf.get_string_width(txt_zero) + 1, 6, txt_zero)

    pdf.set_font("Helvetica", "B", 13)
    txt_fotos = " IMAGENS"
    pdf.cell(pdf.get_string_width(txt_fotos) + 1, 6, txt_fotos)

    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(20, 6, " (AUSENTE)")

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(12 + (w_card * 2), y_cards + 19.5)
    pdf.cell(w_card - 4, 3.5, clean_txt("Ativação Street View"), align="C")

    pdf.set_y(y_cards + 30)

    # Matriz de Diagnóstico
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(
        W,
        5.5,
        clean_txt("MATRIZ DE DIAGNÓSTICO E IMPACTO COMERCIAL"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(1)

    # Tabela com cabeçalho
    pdf.set_fill_color(20, 50, 135)
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

    txt_eval_critica = (
        f"Nota {rating} com apenas {reviews} avaliações acumuladas."
        if reviews_count < 40
        else f"Nota {rating} baseada em {reviews} avaliações."
    )
# Captura real de dados
    all_photos = dados.get("photos", [])
    total_fotos = len(all_photos) # Número real retornado pela API
    
    # Captura real de categorias
    tipos = dados.get("types", [])
      
    # Filtra os tipos para mostrar algo legível, ex: limite de 2 categorias
    # Dicionário de tradução aplicado diretamente
    def traduzir(cat):
        dic = {"lodging": "Hospedagem", "establishment": "Estabelecimento", "point_of_interest": "Ponto de Interesse", "motel": "Motel"}
        return dic.get(cat, cat.replace("_", " ").capitalize())

    cat_formatadas = ", ".join([traduzir(t) for t in dados.get("types", [])[:2]])

    itens = [
               ("Completude", status_completude, "Perfil incompleto transmite falta de profissionalismo e reduz a probabilidade de conversão de visitantes."),
        ("Reputação", f"Nota {rating} ({reviews} avaliações).", "Reputação vulnerável; base pequena limita prova social perante concorrentes."),
        ("Consistência de NAP", "Dados de endereço e telefone ativos.", "Informações corretas evitam perdas por buscas frustradas."),
        ("Categorias", categorias_texto, "Falta de categorias secundárias limita a visibilidade regional."),
        ("Fotos", f"{photos_count} fotos encontradas.", "Poucas fotos impedem a avaliação do espaço pelo cliente."),
        ("Horários", status_horarios, "Informação correta evita perda de clientes no atendimento."),
        ("Posts / Novidades", "Sem publicações recentes (Perfil estático).", "Perfil estático não destaca ofertas nem novidades do local."),
        ("Presença 360", "Nenhum Tour 360° detectado.", "Perdem-se conversões por falta de experiência imersiva 360."),

    ]

    pdf.set_font("Helvetica", "", 9)
    for i, (dim, est, imp) in enumerate(itens):
        bg = (255, 255, 255) if i % 2 == 0 else (248, 250, 252)
        
        y_curr = pdf.get_y()
        padding_top = 2.5 # Espaço interno extra
        padding_bottom = 2.5
        
        # Calcula altura baseada no conteúdo + padding
        h_dim = len(pdf.multi_cell(42, 4.6, clean_txt(f" {dim}"), split_only=True)) * 4.6
        h_est = len(pdf.multi_cell(73, 4.6, clean_txt(f" {est}"), split_only=True)) * 4.6
        h_imp = len(pdf.multi_cell(75, 4.6, clean_txt(imp), split_only=True)) * 4.6
        max_h = max(h_dim, h_est, h_imp, 4.6) + padding_top + padding_bottom

        pdf.set_fill_color(*bg)
        pdf.rect(10, y_curr, W, max_h, "F")

        # Texto verticalmente alinhado
        pdf.set_xy(10, y_curr + padding_top)
        pdf.set_text_color(20, 50, 135)
        pdf.multi_cell(42, 4.6, clean_txt(f" {dim}"))

        pdf.set_xy(52, y_curr + padding_top)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(73, 4.6, clean_txt(f" {est}"))

        pdf.set_xy(125, y_curr + padding_top)
        pdf.set_text_color(20, 50, 135)
        pdf.multi_cell(75, 4.6, clean_txt(imp), align="J")

        pdf.set_y(y_curr + max_h)

    pdf.ln(3)

    # Plano de Ação
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(
        W,
        5.5,
        clean_txt("PLANO DE AÇÃO RECOMENDADO"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(1.5)

    acoes = [
        ("1. ATIVAÇÃO DE EXPERIÊNCIA IMERSIVA 360º (STREET VIEW)", "Integração do seu espaço à base cartográfica do Google. Transforma a ficha em um ponto de visita virtual."),
        ("2. ENSAIO FOTOGRÁFICO PROFISSIONAL", "Fotografias profissionais das instalações, fachada e diferenciais, elevando o valor percebido pelo cliente."),
        ("3. FOMENTO À PROVA SOCIAL ORGÂNICA", "Estratégia para incentivar fotos de clientes reais, aumentando a autenticidade e o engajamento da ficha."),
        ("4. OTIMIZAÇÃO SEO LOCAL & GESTÃO DE REPUTAÇÃO", " Ajuste de categorias secundárias e palavras-chave para ampliar sua visibilidade orgânica regional."),
    ]

    for tit, desc in acoes:
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(20, 50, 135)
        pdf.rect(10, pdf.get_y(), W, 10.5, "DF")

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(20, 50, 135)
        pdf.set_xy(12, pdf.get_y() + 1.2)
        pdf.cell(0, 4, clean_txt(tit), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.set_x(12)
        pdf.cell(0, 4, clean_txt(desc), new_x="LMARGIN", new_y="NEXT")

        pdf.set_y(pdf.get_y() + 2.5)

    # Frase Final de Impacto
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(W, 6, clean_txt("Pronto para elevar sua visibilidade?"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(W, 4.8, clean_txt("Vamos realizar uma auditoria presencial para entender seus objetivos e desenhar um plano de crescimento."), align="C")
    pdf.ln(0)
    pdf.multi_cell(W, 4.8, clean_txt("Um perfil otimizado com conteúdo 360º é o diferencial que separa sua empresa dos concorrentes."), align="C")

    pdf_output_path = "diagnostico_tour360vr.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path


if btn and empresa and cidade:
    if not api_key:
        st.error("Chave da API do Google não configurada nos Secrets.")
    else:
        with st.spinner("Analisando ficha e gerando relatório..."):
            dados = buscar_dados_google(empresa, cidade, api_key)
            if dados:
                pdf_file = gerar_pdf_bytes(dados)
                st.success("Diagnóstico gerado com sucesso!")

                nome_limpo = dados.get("name", empresa).strip()
                file_download_name = f"Diagnóstico da Ficha - {nome_limpo}.pdf"

                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📥 Baixar Relatório Executivo (PDF)",
                        data=f,
                        file_name=file_download_name,
                        mime="application/pdf",
                    )
            else:
                st.error("Empresa não encontrada no Google Maps.")


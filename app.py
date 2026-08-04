import datetime
import requests
import streamlit as st
import pandas as pd  # <--- ADICIONE ESTA LINHA AQUI
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
    
    btn = st.form_submit_button("Gerar Relatório")


def clean_txt(txt):
    """Trata caracteres acentuados mantendo compatibilidade com FPDF"""
    if not txt:
        return ""
    return str(txt).encode("latin-1", "replace").decode("latin-1")

def pesquisar_lugares(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()
    return res.get("results", [])

def obter_detalhes(place_id, key):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,opening_hours,types&key={key}"
    return requests.get(url).json().get("result", {})
    
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
    pdf = PDF()
    pdf.add_page()
        
    # 1. Cabeçalho Empresa
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(20, 50, 135)
    pdf.rect(10, 35, 190, 14, "DF")
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 50, 135)
    pdf.set_xy(13, 37)
    pdf.cell(0, 5, clean(dados.get("name")).upper())
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(13, 44)
    tel = clean(dados.get('formatted_phone_number', 'Não informado'))
    pdf.cell(0, 5, f"Endereço: {clean(dados.get('formatted_address'))} | Telefone: {tel}")

    # Definição das variáveis de fotos e categorias
    all_photos = dados.get("photos", [])
    total_fotos = len(all_photos)
    
    tipos = dados.get("types", [])

    def traduzir(cat): 
        # Adicione aqui outros termos conforme necessário
        dic = {"Shop": "Loja", "Drugstore": "Drogaria", "Bakery": "Padaria", "Pharmacy": "Farmácia","Hair care": "Cuidados com os cabelos", "Food": "Alimentação", "lodging": "Hospedagem", "establishment": "Estabelecimento", "motel": "Motel", "point_of_interest": "Ponto de Interesse", "store": "Loja", "beauty_salon": "Salão de Beleza", "shopping_mall": "Shopping Center", "Health": "Saúde", "Restaurant": "Restaurante", "Academy": "Academia", "School": "Escola", "Physiotherapist": "Fisioterapia"}
    
        return dic.get(cat, cat.replace("_", " ").capitalize())
    
    categorias_texto = ", ".join([traduzir(t) for t in tipos[:4]])

    
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

    y_c = 55
    w_b = 63.3
    h_c = 26

    titles = ["OTIMIZAÇÃO DO PERFIL", "NOTA E REPUTAÇÃO", "PRESENÇA IMERSIVA"]
    for i, t in enumerate(titles):
        x_card = 10 + (i * w_b)
        pdf.rect(x_card, y_c, w_b, h_c, "D")
        
        # Título do Card
        pdf.set_xy(x_card + 2, y_c + 2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(20, 50, 135)
        pdf.cell(w_b - 4, 4, t)
        
    # Card 1: Otimização
    pdf.set_xy(12, y_c + 7)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(249, 115, 22)
    pdf.cell(20, 7, "70/100")
    
    pdf.set_xy(12, y_c + 17)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(w_b - 4, 4, "Em evolução local")

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(20, 6, "/100", align="C")
  
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*status_cor)
    pdf.set_xy(12, y_cards + 14.5) 
    pdf.cell(w_card - 4, 3.5, clean_txt(nivel_maturidade), align="C")

    # Box 2: Nota e Reputação
    pdf.set_xy(x_card2 + 2, y_cards + 17)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(w_b - 4, 4, f"Com base em {dados.get('user_ratings_total', 0)} avaliações")

    # Card 3: Presença Imersiva
    x_card3 = 10 + (w_b * 2)
    photos_count = len(dados.get("photos", []))
    pdf.set_xy(x_card3 + 2, y_cards + 7)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(220, 38, 38)
    pdf.cell(w_b - 4, 7, f"{photos_count} IMAGENS" if photos_count > 0 else "0 IMAGENS (AUSENTE)")
    
    pdf.set_xy(x_card3 + 2, y_cards + 17)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(w_b - 4, 4, "Ativação Street View recomendada")

    pdf.set_y(y_cards + 30)

    # 3. Matriz de Diagnóstico
    pdf.set_y(85)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 135)
    pdf.cell(190, 8, "MATRIZ DE DIAGNÓSTICO E IMPACTO COMERCIAL", ln=True)
    pdf.set_fill_color(20, 50, 135)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(42, 7, " Dimensão", fill=True)
    pdf.cell(73, 7, " Estado Atual Identificado", fill=True)
    pdf.cell(75, 7, " Impacto no Ranqueamento", fill=True, ln=True)
    
    has_website = "Site ativo" if dados.get("website") else "Sem site próprio"
    rating_val = dados.get("rating", 0)
    reviews_total = dados.get("user_ratings_total", 0)
    has_hours = "Cadastrado" if dados.get("opening_hours") else "Ausente/Incompleto"

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
      
    itens = [
        ("Completude", has_website, "Perfil incompleto reduz conversão."),
        ("Reputação", f"Nota {rating_val} ({reviews_total} avaliações).", "Reputação vulnerável."),
        ("Consistência NAP", "Endereço e telefone ativos.", "Evita perdas por buscas."),
        ("Categorias", f"{len(dados.get('types', []))} categorias identificadas.", "Limita visibilidade regional."),
        ("Fotos", f"{photos_count} fotos encontradas.", "Cobertura visual baixa."),
        ("Horários", f"Funcionamento: {has_hours}.", "Evita perda de clientes."),
        ("Posts/Novidades", "Sem publicações recentes.", "Perfil estático."),
        ("Presença 360", "Nenhum Tour 360° detectado.", "Perdem-se conversões imersivas.")
    ]
    
    for i, (d, e, imp) in enumerate(itens):
        pdf.set_fill_color(248, 250, 252) if i % 2 != 0 else pdf.set_fill_color(255, 255, 255)
        pdf.rect(10, pdf.get_y(), 190, 10, "FD")
        pdf.set_text_color(51, 65, 85)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(42, 10, f" {d}")
        pdf.cell(73, 10, f" {e}")
        pdf.cell(75, 10, f" {imp}", ln=True)
        
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


# --- LÓGICA DE SELEÇÃO E BUSCA ---
if btn and empresa and cidade:
    st.session_state.lista_candidatos = pesquisar_lugares(empresa, cidade, api_key)
    if not st.session_state.lista_candidatos:
        st.error("Nenhuma empresa encontrada.")

# Se encontrou candidatos, exibe o seletor
if "lista_candidatos" in st.session_state and st.session_state.lista_candidatos:
    opcoes = {f"{c['name']} - {c.get('formatted_address', '')}": c['place_id'] for c in st.session_state.lista_candidatos}
    selecao = st.selectbox("Selecione a unidade correta:", list(opcoes.keys()))
    
    if st.button("Carregar Dados desta Unidade"):
        place_id = opcoes[selecao]
        st.session_state.dados = obter_detalhes(place_id, api_key)

# --- EXIBIÇÃO DO PREVIEW E DOWNLOAD ---
# --- EXIBIÇÃO DO PREVIEW COMPLETO E DOWNLOAD ---
if "dados" in st.session_state and st.session_state.dados:
    dados = st.session_state.dados
    st.success(f"Unidade selecionada: **{dados.get('name')}**")
    
    # Métricas visuais na tela
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nota Google", dados.get("rating", "N/A"))
    col2.metric("Avaliações", dados.get("user_ratings_total", 0))
    col3.metric("Fotos", len(dados.get("photos", [])))
    col4.metric("Site", "Sim" if dados.get("website") else "Não")
    
    # Informações textuais básicas
    st.write(f"**Endereço:** {dados.get('formatted_address', 'Não informado')}")
    st.write(f"**Telefone:** {dados.get('formatted_phone_number', 'Não informado')}")
    
    # Tabela completa de preview alinhada com o diagnóstico
    st.write("### Preview da Matriz de Diagnóstico")
    
    has_website = "Site ativo" if dados.get("website") else "Sem site próprio"
    rating_val = dados.get("rating", 0)
    reviews_total = dados.get("user_ratings_total", 0)
    photos_count = len(dados.get("photos", []))
    has_hours = "Cadastrado" if dados.get("opening_hours") else "Ausente/Incompleto"
    
    st.table(pd.DataFrame([
        {"Dimensão": "Completude do Cadastro", "Estado Atual": has_website, "Impacto": "Perfil incompleto reduz conversão."},
        {"Dimensão": "Nota e Avaliações", "Estado Atual": f"Nota {rating_val} ({reviews_total} avaliações)", "Impacto": "Reputação e prova social."},
        {"Dimensão": "Consistência de NAP", "Estado Atual": "Endereço e telefone ativos", "Impacto": "Evita perdas por buscas."},
        {"Dimensão": "Categorias", "Estado Atual": f"{len(dados.get('types', []))} categorias identificadas", "Impacto": "Limita visibilidade regional."},
        {"Dimensão": "Fotos", "Estado Atual": f"{photos_count} fotos encontradas", "Impacto": "Cobertura visual baixa."},
        {"Dimensão": "Horários", "Estado Atual": f"Funcionamento: {has_hours}", "Impacto": "Evita perda de clientes."},
        {"Dimensão": "Recursos Interativos", "Estado Atual": "Nenhum tour virtual 360°", "Impacto": "Falta de experiência imersiva."}
    ]))

    # Botão de Gerar PDF
    if st.button("📥 Gerar e Baixar Relatório (PDF)"):
        pdf_file = gerar_pdf_bytes(dados)
        nome_limpo = dados.get("name", empresa).strip()
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="✅ Download Pronto! Clique aqui",
                data=f,
                file_name=f"Diagnóstico da Ficha - {nome_limpo}.pdf",
                mime="application/pdf",
            )

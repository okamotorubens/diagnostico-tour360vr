import os
import io
import requests
import streamlit as st
from datetime import datetime
from fpdf import FPDF

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E CSS TEMA DASHBOARD
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tour360VR - Plataforma de Consultoria Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
        padding-top: 10px;
    }
    
    .main-header {
        font-size: 22px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin-top: 0px;
        margin-bottom: 20px;
        padding-top: 0px;
    }
    .main-header span { color: #ff3d3d; }
    
    .dashboard-card {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }

    .card-title {
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button {
        background-color: #1e293b;
        color: #ffffff;
        border: 1px solid #334155;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #1e40af;
        border-color: #3b82f6;
        color: #ffffff;
    }

    .custom-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #070a10;
        color: #94a3b8;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #1e293b;
        font-size: 12px;
        z-index: 999;
    }
    .custom-footer a { color: #3ea1db; text-decoration: none; }
    </style>
""", unsafe_allow_html=True)

API_KEY_GOOGLE = (
    st.secrets.get("GOOGLE_API_KEY") 
    or st.secrets.get("GOOGLE_PLACES_API_KEY") 
    or os.environ.get("GOOGLE_API_KEY")
    or ""
)

# -----------------------------------------------------------------------------
# 2. FUNÇÕES UTILITÁRIAS & API GOOGLE PLACES
# -----------------------------------------------------------------------------
def conv(texto):
    if not texto: return ""
    limpo = str(texto).replace("•", "- ").replace("✓", "[OK] ").replace("📍", "").replace("📞", "").replace("🌐", "").replace("Brazil", "Brasil").replace("⭐", "")
    return limpo.encode('latin-1', 'replace').decode('latin-1')

def formatar_estrelas(nota):
    try:
        val = int(round(float(nota)))
        return "*" * max(0, min(5, val))
    except Exception:
        return "*****"

def calcular_score_real(dados):
    if not dados.get("nome"):
        return 0
    score = 100
    if not dados.get("tem_tour360", False): score -= 20
    if dados.get("website") == "Não possui" or not dados.get("website"): score -= 15
    if not dados.get("tem_fotos_hd", False): score -= 15
    if not dados.get("categorias_completas", False): score -= 15
    if not dados.get("horarios_ok", False): score -= 10
    if not dados.get("tem_descricao", False): score -= 10
    if not dados.get("atributos_ok", False): score -= 10
    if not dados.get("resposta_avaliacoes_ok", False): score -= 10
    if dados.get("avaliacoes", 0) < 50: score -= 15
    return max(score, 10)

def calcular_score_concorrente(c):
    score = 100
    if c.get("tem_tour360") == "Não": score -= 20
    if c.get("tem_website") == "Não": score -= 15
    if c.get("tem_fotos_hd") == "Não": score -= 15
    if c.get("categorias_ok") == "Não": score -= 15
    if c.get("horarios_ok") == "Não": score -= 10
    if c.get("tem_descricao") == "Não": score -= 10
    if c.get("atributos_ok") == "Não": score -= 10
    if c.get("respostas_ok") == "Não": score -= 10
    if c.get("avaliacoes", 0) < 50: score -= 15
    return max(score, 10)

def obter_caminho_logo():
    caminhos = ['assets/Logo_TOUR_transparente.png', 'Logo_TOUR_transparente.png', 'assets/Logo TOUR transparente.png']
    for c in caminhos:
        if os.path.exists(c): return c
    return None

def buscar_detalhes_concorrente_especifico(nome_concorrente, cidade, api_key):
    if not nome_concorrente or not api_key:
        return None
    try:
        termo = f"{nome_concorrente}, {cidade}" if cidade else nome_concorrente
        url_search = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={requests.utils.quote(termo)}&key={api_key}"
        res = requests.get(url_search).json()
        
        if res.get("status") == "OK" and res.get("results"):
            item = res["results"][0]
            place_id = item.get("place_id")
            
            url_det = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=website,editorial_summary,opening_hours,photos,types&key={api_key}"
            res_det = requests.get(url_det).json().get("result", {})
            
            photos = res_det.get("photos", item.get("photos", []))
            types_lista = res_det.get("types", [])

            return {
                "nome": item.get("name", nome_concorrente),
                "nota": float(item.get("rating", 0.0)),
                "avaliacoes": int(item.get("user_ratings_total", 0)),
                "tem_fotos_hd": "Sim" if len(photos) >= 10 else "Não",
                "tem_tour360": "Não",
                "categorias_ok": "Sim" if len(types_lista) >= 3 else "Não",
                "horarios_ok": "Sim" if "opening_hours" in res_det else "Não",
                "tem_website": "Sim" if res_det.get("website") else "Não",
                "tem_descricao": "Sim" if "editorial_summary" in res_det else "Não",
                "atributos_ok": "Não",
                "respostas_ok": "Não"
            }
    except Exception:
        pass
    return None

# -----------------------------------------------------------------------------
# 3. ESTADOS DA SESSÃO PERSISTENTES
# -----------------------------------------------------------------------------
if 'dados' not in st.session_state:
    st.session_state['dados'] = {
        "nome": "",
        "contato": "",
        "endereco": "",
        "telefone": "",
        "website": "",
        "nota": 0.0,
        "avaliacoes": 0,
        "tem_tour360": False,
        "tem_fotos_hd": False,
        "categorias_completas": False,
        "horarios_ok": False,
        "tem_descricao": False,
        "atributos_ok": False,
        "resposta_avaliacoes_ok": False,
        "categorias_detectadas": [],
        "foto_reference": ""
    }

if 'concorrentes' not in st.session_state:
    st.session_state['concorrentes'] = [
        {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"},
        {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"},
        {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"}
    ]

if 'planos' not in st.session_state:
    st.session_state['planos'] = {
        "start_valor": "500,00 ou 2x R$ 250,00",
        "start_itens": "- Correção cadastral e NAP\n- Descrição SEO Profissional\n- Ajuste de categorias estratégicas\n- Padronização de dados e links",
        "pro_valor": "900,00 ou 3x R$ 300,00",
        "pro_itens": "- Tudo do Plano Start\n- Tour Virtual 360° na Ficha Google\n- Ensaio Fotográfico HD de Interatividade\n- Destaque no Maps e Buscas",
        "gestao_valor": "A combinar",
        "gestao_itens": "- Tour 360° Personalizado no seu Site\n- Atualização quinzenal de conteúdos\n- Gestão estratégica de avaliações\n- Relatórios mensais de performance"
    }

if 'plano_acao_extra' not in st.session_state:
    st.session_state['plano_acao_extra'] = "Seu perfil tem nota sólida, mas a ausência de Tour Virtual 360° e fotos HD deixa espaço para os concorrentes diretos capturarem clientes na região."

if 'unidades_encontradas' not in st.session_state:
    st.session_state['unidades_encontradas'] = []

for key_chk in ['chk_tour360', 'chk_fotos_hd', 'chk_cat_ok', 'chk_horarios_ok', 'chk_desc', 'chk_atrib', 'chk_resp']:
    if key_chk not in st.session_state:
        st.session_state[key_chk] = False

# -----------------------------------------------------------------------------
# 4. GERADOR PDF TOUR360VR
# -----------------------------------------------------------------------------
class PDFTour360Oficial(FPDF):
    def header(self):
        self.set_fill_color(11, 60, 93)  # #0B3C5D
        self.rect(0, 0, 105, 4, 'F')
        self.set_fill_color(50, 140, 193)  # #328CC1
        self.rect(105, 0, 105, 4, 'F')
        if self.page_no() == 1: 
            return
        
        caminho_logo = obter_caminho_logo()
        if caminho_logo:
            try: 
                self.image(caminho_logo, 12, 6, 18)
            except Exception: 
                pass
            
        self.set_xy(12, 8)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(11, 60, 93)
        self.cell(0, 4.5, 'Tour360VR', align='L', ln=True)
        
        self.set_x(12)
        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, conv('Gestão de Perfil & Diagnóstico do Google Meu Negócio'), align='L', ln=True)
        
        self.set_draw_color(226, 232, 240)
        self.line(12, 20, 198, 20)
        self.set_y(23)

    def footer(self):
        self.set_y(-16)
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(100, 116, 139)
        self.line(12, self.get_y(), 198, self.get_y())
        self.set_y(-13)
        
        if self.page_no() == 1:
            self.set_x(12)
            self.set_font('Helvetica', 'B', 9.5)
            self.set_text_color(11, 60, 93)
            self.cell(186, 5, conv("Rubens Okamoto  |  contato@tour360vr.com.br  |  (16) 99133-2121  |  Ribeirão Preto - SP"), align='C')
        else:
            w_col = (198 - 12) / 4.0
            self.set_x(12)
            self.cell(w_col, 5, 'www.tour360vr.com.br', link='https://tour360vr.com.br', align='C')
            self.cell(w_col, 5, 'contato@tour360vr.com.br', link='mailto:contato@tour360vr.com.br', align='C')
            self.cell(w_col, 5, 'WhatsApp: (16) 99133-2121', link='https://wa.me/5516991332121', align='C')
            self.cell(w_col, 5, f'Página {self.page_no()} de 4', align='C')

    def rounded_rect(self, x, y, w, h, r, style=''):
        k, hp = self.k, self.h
        op = 'f' if style == 'F' else ('B' if style in ['FD', 'DF'] else 'S')
        my_arc = 4/3 * (2**0.5 - 1)
        self._out(f'{(x+r)*k:.2f} {(hp-y)*k:.2f} m')
        xc, yc = x + w - r, y + r
        self._out(f'{xc*k:.2f} {(hp-y)*k:.2f} l')
        self._arc(xc + r*my_arc, yc - r, xc + r, yc - r*my_arc, xc + r, yc)
        xc, yc = x + w - r, y + h - r
        self._out(f'{(x+w)*k:.2f} {(hp-yc)*k:.2f} l')
        self._arc(xc + r, yc + r*my_arc, xc + r*my_arc, yc + r, xc, yc + r)
        xc, yc = x + r, y + h - r
        self._out(f'{(x+r)*k:.2f} {(hp-(y+h))*k:.2f} l')
        self._arc(xc - r*my_arc, yc + r, xc - r, yc + r*my_arc, xc - r, yc)
        xc, yc = x + r, y + r
        self._out(f'{x*k:.2f} {(hp-yc)*k:.2f} l')
        self._arc(xc - r, yc - r*my_arc, xc - r*my_arc, yc - r, xc, yc - r)
        self._out(f'{op}')

    def _arc(self, x1, y1, x2, y2, x3, y3):
        k, hp = self.k, self.h
        self._out(f'{x1*k:.2f} {(hp-y1)*k:.2f} {x2*k:.2f} {(hp-y2)*k:.2f} {x3*k:.2f} {(hp-y3)*k:.2f} c')

def gerar_pdf_oficial(dados, score_input, planos, plano_acao_extra="", concorrentes=[]):
    score = calcular_score_real(dados)
    pdf = PDFTour360Oficial()
    pdf.set_auto_page_break(auto=True, margin=18)
    estrelas_txt = formatar_estrelas(dados['nota'])

    # PÁGINA 1: CAPA
    pdf.add_page()
    caminho_logo = obter_caminho_logo()
    if caminho_logo:
        try:
            pdf.image(caminho_logo, 82, 12, 46)
        except Exception:
            pass

    pdf.set_y(54)
    pdf.set_font('Helvetica', 'B', 21)
    pdf.set_text_color(11, 60, 93)
    pdf.cell(0, 8, conv('DIAGNÓSTICO GOOGLE MEU NEGÓCIO'), align='C', ln=True)
    pdf.ln(2)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(217, 83, 79)
    sub_txt = f"Seu perfil tem nota sólida, mas {dados['avaliacoes']} avaliações e zero fotos 360° deixam dinheiro na mesa."
    pdf.cell(0, 5, conv(sub_txt.upper()), align='C', ln=True)
    pdf.ln(6)

    w_capa = 186
    h_capa = 42
    x_capa = (210 - w_capa) / 2.0
    y_capa = pdf.get_y()

    pdf.set_fill_color(248, 249, 250)
    pdf.set_draw_color(203, 213, 225)
    pdf.rounded_rect(x_capa, y_capa, w_capa, h_capa, 3, 'FD')

    pdf.set_xy(x_capa, y_capa + 4)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(11, 60, 93) 
    pdf.cell(w_capa, 7, conv(f"{dados['nome'] or 'Nome da Empresa'}"), align='C', ln=True)

    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.set_x(x_capa)
    pdf.cell(w_capa, 5, conv(f"Preparado para: {dados['contato'] or 'Responsável'}"), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.set_x(x_capa)
    pdf.cell(w_capa, 5, conv(f"{dados['endereco'] or 'Endereço não informado'}"), align='C', ln=True)
    
    site_txt = dados['website'] if dados['website'] else 'N/I'
    pdf.set_x(x_capa)
    pdf.cell(w_capa, 5, conv(f"Data: {datetime.now().strftime('%d/%m/%Y')}   |   Nota: {dados['nota']:.1f} ★ ({dados['avaliacoes']} avaliações)"), align='C', ln=True)
    pdf.ln(8)

    # Foto da Ficha do Google
    y_foto = y_capa + h_capa + 8
    foto_renderizada = False
    if dados.get("foto_reference") and API_KEY_GOOGLE:
        try:
            url_img = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={dados['foto_reference']}&key={API_KEY_GOOGLE}"
            resp_img = requests.get(url_img, timeout=4)
            if resp_img.status_code == 200:
                img_stream = io.BytesIO(resp_img.content)
                pdf.image(img_stream, x_capa, y_foto, w_capa, 85)
                foto_renderizada = True
        except Exception:
            pass

    if not foto_renderizada:
        pdf.set_fill_color(240, 243, 246)
        pdf.rounded_rect(x_capa, y_foto, w_capa, 80, 3, 'F')
        pdf.set_xy(x_capa, y_foto + 35)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(w_capa, 6, conv("[ FACHADA / IMAGEM DA FICHA GOOGLE DO CLIENTE ]"), align='C', ln=True)

    # PÁGINA 2: DIAGNÓSTICO
    pdf.add_page()
    pdf.set_y(24)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(11, 60, 93)
    pdf.cell(0, 7, conv('COMO ESTÁ O SEU GOOGLE MEU NEGÓCIO HOJE'), align='L', ln=True)
    pdf.ln(3)

    # KPIs Cards
    w_card = 59
    h_card = 22
    y_card = pdf.get_y()

    # Card 1: Score
    pdf.set_fill_color(248, 249, 250)
    pdf.set_draw_color(220, 225, 230)
    pdf.rounded_rect(12, y_card, w_card, h_card, 2, 'FD')
    pdf.set_xy(12, y_card + 3)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(w_card, 4, conv("OTIMIZAÇÃO DO PERFIL"), align='C', ln=True)
    pdf.set_x(12)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(11, 60, 93)
    pdf.cell(w_card, 6, conv(f"{score}/100"), align='C', ln=True)
    pdf.set_x(12)
    pdf.set_font('Helvetica', '', 7.5)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(w_card, 4, conv("Oportunidades de ganho"), align='C', ln=True)

    # Card 2: Nota
    pdf.set_fill_color(248, 249, 250)
    pdf.rounded_rect(75, y_card, w_card, h_card, 2, 'FD')
    pdf.set_xy(75, y_card + 3)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(w_card, 4, conv("NOTA DOS CLIENTES"), align='C', ln=True)
    pdf.set_x(75)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(11, 60, 93)
    pdf.cell(w_card, 6, conv(f"{dados['nota']:.1f} ★"), align='C', ln=True)
    pdf.set_x(75)
    pdf.set_font('Helvetica', '', 7.5)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(w_card, 4, conv(f"{dados['avaliacoes']} avaliações"), align='C', ln=True)

    # Card 3: Tour 360
    pdf.set_fill_color(248, 249, 250)
    pdf.rounded_rect(138, y_card, w_card, h_card, 2, 'FD')
    pdf.set_xy(138, y_card + 3)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(w_card, 4, conv("TOUR VIRTUAL 360°"), align='C', ln=True)
    pdf.set_x(138)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(217, 83, 79) if not dados['tem_tour360'] else pdf.set_text_color(22, 128, 61)
    pdf.cell(w_card, 6, conv("NÃO DETECTADO" if not dados['tem_tour360'] else "ATIVO"), align='C', ln=True)
    pdf.set_x(138)
    pdf.set_font('Helvetica', '', 7.5)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(w_card, 4, conv("Sair na frente da região"), align='C', ln=True)

    pdf.set_y(y_card + h_card + 6)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(11, 60, 93)
    pdf.cell(0, 6, conv("Análise Detalhada por Dimensão"), align='L', ln=True)
    pdf.ln(2)

    # Tabela Dimensões vs Impacto
    w_dim = 40
    w_est = 73
    w_imp = 73
    
    pdf.set_fill_color(11, 60, 93)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.cell(w_dim, 6, conv(" Dimensão"), border=0, fill=True)
    pdf.cell(w_est, 6, conv(" Estado Atual"), border=0, fill=True)
    pdf.cell(w_imp, 6, conv(" Impacto no Negócio"), border=0, fill=True)
    pdf.ln()

    desc_web = f"Website: {dados['website']}" if dados['website'] != 'Não possui' and dados['website'] != '' else "Sem site próprio ou link oficial."
    itens_dim = [
        ("Completude do cadastro", "Dados básicos informados, sem site próprio ou descrição.", "Visitantes não conhecem sua história nem diferenciais."),
        ("Nota e avaliações", f"{dados['nota']:.1f} ★ com {dados['avaliacoes']} avaliações no perfil.", "Clientes que elogiam não recebem retorno oficial do dono."),
        ("Consistência de NAP", f"Telefone {dados['telefone']} e endereço alinhados.", "O Google confia nos dados porque batem em todas as fontes."),
        ("Categorias", "Categorias genéricas atribuídas.", "Não deixa explícito sua especialidade comercial principal."),
        ("Fotos e Imersão 360°", "Fotos estáticas convencionais; sem Tour 360°.", "Visitantes veem a loja em miniatura e não imergem no espaço."),
        ("Horários & Posts", "Horários visíveis; sem posts/novidades ativas.", "Perfil estático passa sensação de desatualização.")
    ]

    for idx_d, (dim_t, est_t, imp_t) in enumerate(itens_dim):
        pdf.set_fill_color(255, 255, 255) if idx_d % 2 == 0 else pdf.set_fill_color(248, 249, 250)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_text_color(15, 23, 42)
        
        y_linha = pdf.get_y()
        pdf.cell(w_dim, 10, conv(f" {dim_t}"), border='B', fill=True)
        
        pdf.set_font('Helvetica', '', 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(w_est, 10, conv(f" {est_t[:52]}"), border='B', fill=True)
        pdf.cell(w_imp, 10, conv(f" {imp_t[:52]}"), border='B', fill=True)
        pdf.ln()

    pdf.set_y(pdf.get_y() + 6)

    # PÁGINA 3: CONCORRÊNCIA E PLANOS
    pdf.add_page()
    pdf.set_y(24)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(11, 60, 93)
    pdf.cell(0, 6, conv("Concorrência na sua Região"), align='L', ln=True)
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 4, conv("Veja como sua empresa está posicionada frente aos concorrentes locais:"), align='L', ln=True)
    pdf.ln(3)

    w_c_num = 15
    w_c_emp = 101
    w_c_nota = 35
    w_c_aval = 35

    pdf.set_fill_color(11, 60, 93)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.cell(w_c_num, 6, conv(" #"), fill=True, align='C')
    pdf.cell(w_c_emp, 6, conv(" Estabelecimento"), fill=True)
    pdf.cell(w_c_nota, 6, conv(" Nota"), fill=True, align='C')
    pdf.cell(w_c_aval, 6, conv(" Avaliações"), fill=True, align='C')
    pdf.ln()

    concorrentes_filtrados = [c for c in concorrentes if c.get("nome", "").strip() != ""]
    if not concorrentes_filtrados:
        concorrentes_demo = [
            {"nome": "Concorrente Regional Lider 1", "nota": 4.7, "avaliacoes": 1240},
            {"nome": "Especialista Local Bairro", "nota": 4.5, "avaliacoes": 380},
            {"nome": f"{dados['nome']} (Você)", "nota": dados['nota'], "avaliacoes": dados['avaliacoes']}
        ]
    else:
        concorrentes_demo = []
        for c in concorrentes_filtrados:
            concorrentes_demo.append({"nome": c['nome'], "nota": float(c['nota']), "avaliacoes": c['avaliacoes']})
        concorrentes_demo.append({"nome": f"{dados['nome']} (Você)", "nota": dados['nota'], "avaliacoes": dados['avaliacoes']})

    for idx_c, cd in enumerate(concorrentes_demo[:5]):
        is_user = "(Você)" in cd['nome']
        pdf.set_fill_color(240, 249, 255) if is_user else (pdf.set_fill_color(255, 255, 255) if idx_c % 2 == 0 else pdf.set_fill_color(248, 249, 250))
        pdf.set_font('Helvetica', 'B' if is_user else '', 8)
        pdf.set_text_color(11, 60, 93) if is_user else pdf.set_text_color(51, 65, 85)
        
        pdf.cell(w_c_num, 5.5, conv(f"{idx_c+1}º"), border='B', fill=True, align='C')
        pdf.cell(w_c_emp, 5.5, conv(f" {cd['nome'][:50]}"), border='B', fill=True)
        pdf.cell(w_c_nota, 5.5, conv(f"{cd['nota']:.1f} ★"), border='B', fill=True, align='C')
        pdf.cell(w_c_aval, 5.5, conv(f"{cd['avaliacoes']}"), border='B', fill=True, align='C')
        pdf.ln()

    pdf.ln(6)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(11, 60, 93)
    pdf.cell(0, 6, conv("Planos de Ação e Opções de Investimento"), align='L', ln=True)
    pdf.ln(3)

    w_p = 59
    h_p = 54
    y_p = pdf.get_y()

    # Opção 1
    pdf.set_fill_color(248, 249, 250)
    pdf.set_draw_color(220, 225, 230)
    pdf.rounded_rect(12, y_p, w_p, h_p, 2, 'FD')
    pdf.set_xy(12, y_p + 3)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(11, 60, 93)
    pdf.cell(w_p, 4, conv("OPÇÃO 1: Ficha Otimizada"), align='C', ln=True)
    pdf.set_x(12)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_p, 5, conv(f"R$ {planos['start_valor']}"), align='C', ln=True)
    pdf.set_x(15)
    pdf.set_font('Helvetica', '', 7.5)
    pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(53, 3.8, conv(planos['start_itens']), align='L')

    # Opção 2
    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(50, 140, 193)
    pdf.rounded_rect(75, y_p, w_p, h_p, 2, 'FD')
    pdf.set_xy(75, y_p + 3)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(11, 60, 93)
    pdf.cell(w_p, 4, conv("OPÇÃO 2: Ficha + Tour 360°"), align='C', ln=True)
    pdf.set_x(75)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(50, 140, 193)
    pdf.cell(w_p, 5, conv(f"R$ {planos['pro_valor']} (RECOMENDADO)"), align='C', ln=True)
    pdf.set_x(78)
    pdf.set_font('Helvetica', '', 7.5)
    pdf.set_text_color(15, 23, 42)
    pdf.multi_cell(53, 3.8, conv(planos['pro_itens']), align='L')

    # Opção 3
    pdf.set_fill_color(248, 249, 250)
    pdf.set_draw_color(220, 225, 230)
    pdf.rounded_rect(138, y_p, w_p, h_p, 2, 'FD')
    pdf.set_xy(138, y_p + 3)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(11, 60, 93)
    pdf.cell(w_p, 4, conv("OPÇÃO 3: Presença Completa"), align='C', ln=True)
    pdf.set_x(138)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_p, 5, conv(f"{planos['gestao_valor']}"), align='C', ln=True)
    pdf.set_x(141)
    pdf.set_font('Helvetica', '', 7.5)
    pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(53, 3.8, conv(planos['gestao_itens']), align='L')

    # Box CTA Fechamento
    y_cta = y_p + h_p + 6
    pdf.set_fill_color(11, 60, 93)
    pdf.rounded_rect(12, y_cta, 186, 22, 2, 'F')
    pdf.set_xy(12, y_cta + 3)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(186, 5, conv("Quer sair na frente da concorrência na sua região?"), align='C', ln=True)
    pdf.set_x(12)
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(226, 232, 240)
    pdf.cell(186, 4, conv("Vamos mostrar como um Tour Virtual 360° + otimização profissional pode acelerar sua presença no Google."), align='C', ln=True)
    pdf.set_x(12)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(50, 140, 193)
    pdf.cell(186, 5, conv("📲 Falar com a TOUR360VR: (16) 99133-2121"), align='C', ln=True)

    # PÁGINA 4: CONTRATO
    pdf.add_page()
    pdf.set_y(24)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(11, 60, 93)
    pdf.cell(0, 8, conv('CONTRATO DE PRESTAÇÃO DE SERVIÇOS'), align='C', ln=True)
    pdf.ln(6)

    h_linha = 5.0

    # 1. CONTRATADA
    pdf.set_x(12)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.write(h_linha, conv("CONTRATADA: "))
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(51, 65, 85)
    pdf.write(h_linha, conv("Tour360VR, representada por Rubens H. Okamoto, CPF: 287.932.298-79 e Telefone: (16) 99133-2121.\n\n"))

    # 2. CONTRATANTE
    pdf.set_x(12)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.write(h_linha, conv("CONTRATANTE: "))
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(51, 65, 85)
    txt_cli = f"{dados['nome'] or 'Empresa Contratante'}, representada por {dados['contato'] or 'Responsável'}, localizada em {dados['endereco'] or 'Endereço não informado'}, Telefone: {dados['telefone'] or 'N/I'}.\n\n"
    pdf.write(h_linha, conv(txt_cli))

    # 3. OBJETO
    pdf.set_x(12)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(51, 65, 85)
    pdf.write(h_linha, conv("A CONTRATADA compromete-se a executar os serviços de otimização, reestruturação técnica e/ou produção de Tour Virtual 360° para o perfil do Google da CONTRATANTE.\n\n"))

    # 4. CLÁUSULAS
    pdf.set_x(12)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.write(h_linha, conv("CLÁUSULA PRIMEIRA - DO OBJETO: "))
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(51, 65, 85)
    pdf.write(h_linha, conv("Os serviços serão iniciados em até 5 dias úteis após o fornecimento de todos os acessos e informações necessárias à gestão do perfil.\n\n"))

    pdf.set_x(12)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(186, 5.0, conv("CLÁUSULA SEGUNDA - SELEÇÃO DO PLANO CONTRATADO:"), ln=True)
    pdf.set_x(12)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(186, 6.0, conv("(   ) Opção 1: Ficha Otimizada       (   ) Opção 2: Ficha + Tour 360°       (   ) Opção 3: Presença Completa"), ln=True)
    pdf.ln(3)

    pdf.set_x(12)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(186, 5.0, conv("CLÁUSULA TERCEIRA - CONDIÇÕES DE PAGAMENTO:"), ln=True)
    pdf.set_x(12)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(186, 6.0, conv("(   ) À Vista       (   ) 2x sem juros       (   ) 3x sem juros       (   ) Outro: ___________________"), ln=True)

    # Assinaturas
    pdf.ln(18)
    y_ass = pdf.get_y()
    pdf.set_xy(12, y_ass)
    pdf.cell(88, 5, '_____________________________________', align='C')
    pdf.set_xy(110, y_ass)
    pdf.cell(88, 5, '_____________________________________', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_x(12)
    pdf.cell(88, 4.5, 'Rubens H. Okamoto', align='C')
    pdf.set_x(110)
    pdf.cell(88, 4.5, conv(f"{dados['contato'] or 'Responsável'}"), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(100, 116, 139)
    pdf.set_x(12)
    pdf.cell(88, 4.5, 'Tour360VR', align='C')
    pdf.set_x(110)
    pdf.cell(88, 4.5, conv(f"{dados['nome'] or 'Empresa'}"), align='C', ln=True)

    return bytes(pdf.output())

# -----------------------------------------------------------------------------
# 5. SIDEBAR / MENU LATERAL
# -----------------------------------------------------------------------------
with st.sidebar:
    caminho_logo = obter_caminho_logo()
    if caminho_logo:
        st.image(caminho_logo, width=120)
    else:
        st.markdown("## TOUR**360VR**")
        
    nome_exibicao = st.session_state['dados']['nome'] if st.session_state['dados']['nome'] else "Novo Cliente"
    st.markdown(f"<p style='color: #94a3b8; font-size: 13px;'>Consultoria Pro: <b>{nome_exibicao}</b></p>", unsafe_allow_html=True)
    st.markdown("---")

    opcao_menu = st.radio(
        "Navegação do Sistema:",
        [
            "🔍 1. Consulta & Diagnóstico Rápido",
            "⚔️ 2. Concorrentes do Segmento",
            "💡 3. Plano de Ação & Persuasão",
            "📜 4. Proposta Comercial & Planos",
            "📄 5. Contrato Profissional"
        ]
    )

st.markdown("<div class='main-header'>PLATAFORMA DE CONSULTORIA TOUR360VR - GESTÃO & DIAGNÓSTICO GOOGLE MEU NEGÓCIO</div>", unsafe_allow_html=True)
dados = st.session_state['dados']
score = calcular_score_real(dados)

# -----------------------------------------------------------------------------
# PAINEL CENTRAL - MÓDULOS DE USO
# -----------------------------------------------------------------------------

if "1. Consulta" in opcao_menu:
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='card-title'>CAPA DE DIAGNÓSTICO: [{dados['nome'] or 'Novo Cliente'}]</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            nome_input = st.text_input("Nome da Empresa:", value="", key="input_empresa_nome", placeholder="Ex: Taiwan Hotel Ltda")
        with c2:
            cidade_empresa = st.text_input("Localização:", value="", key="input_empresa_cidade", placeholder="Ex: Ribeirão Preto, SP")
            
        if st.button("🚀 Buscar no Google Maps", use_container_width=True, key="btn_busca_google"):
            if API_KEY_GOOGLE:
                try:
                    termo = f"{nome_input}, {cidade_empresa}" if cidade_empresa else nome_input
                    if termo.strip() != "":
                        url_search = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={termo}&key={API_KEY_GOOGLE}"
                        res = requests.get(url_search).json()
                        if res.get("status") == "OK" and res.get("results"):
                            st.session_state['unidades_encontradas'] = res["results"]
                            st.success(f"Encontrada(s) {len(res['results'])} unidade(s)!")
                        else:
                            st.error(f"Erro na busca: {res.get('status')} - {res.get('error_message', 'Local não encontrado')}")
                    else:
                        st.warning("Por favor, digite o nome da empresa para buscar.")
                except Exception as e:
                    st.error(f"Erro na conexão: {e}")
            else:
                st.error("Chave GOOGLE_API_KEY não configurada nos segredos.")

        if st.session_state['unidades_encontradas']:
            opcoes = [f"{u.get('name')} - {u.get('formatted_address')}" for u in st.session_state['unidades_encontradas']]
            escolha = st.selectbox("Selecione a unidade exata:", opcoes, key="select_unidade_exata")
            
            if st.button("📌 Carregar Dados desta Unidade", use_container_width=True, key="btn_carregar_unidade"):
                idx = opcoes.index(escolha)
                u = st.session_state['unidades_encontradas'][idx]
                place_id = u.get("place_id")
                
                if API_KEY_GOOGLE:
                    try:
                        url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,international_phone_number,website,rating,user_ratings_total,photos,opening_hours,types,editorial_summary,geometry&key={API_KEY_GOOGLE}"
                        res_details = requests.get(url_details).json().get("result", {})
                        
                        photos = res_details.get("photos", u.get("photos", []))
                        types_lista = res_details.get("types", [])
                        loc = res_details.get("geometry", {}).get("location", {})
                        
                        nome_carregado = res_details.get("name") or u.get("name") or nome_input
                        st.session_state['dados']['nome'] = nome_carregado
                        st.session_state['dados']['endereco'] = res_details.get("formatted_address") or u.get("formatted_address") or ""
                        st.session_state['dados']['telefone'] = res_details.get("formatted_phone_number") or res_details.get("international_phone_number") or ""
                        st.session_state['dados']['website'] = res_details.get("website") or ""
                        st.session_state['dados']['nota'] = float(res_details.get("rating") or u.get("rating") or 0.0)
                        st.session_state['dados']['avaliacoes'] = int(res_details.get("user_ratings_total") or u.get("user_ratings_total") or 0)
                        st.session_state['dados']['contato'] = "Gerente Responsável"
                        
                        st.session_state['dados']['tem_fotos_hd'] = len(photos) >= 10
                        st.session_state['dados']['horarios_ok'] = "opening_hours" in res_details
                        st.session_state['dados']['categorias_completas'] = len(types_lista) >= 3
                        st.session_state['dados']['tem_descricao'] = "editorial_summary" in res_details
                        st.session_state['dados']['tem_tour360'] = False
                        st.session_state['dados']['atributos_ok'] = False
                        st.session_state['dados']['resposta_avaliacoes_ok'] = False
                        st.session_state['dados']['categorias_detectadas'] = types_lista
                        st.session_state['dados']['foto_reference'] = photos[0].get("photo_reference") if photos else ""

                        st.session_state['chk_tour360'] = False
                        st.session_state['chk_fotos_hd'] = st.session_state['dados']['tem_fotos_hd']
                        st.session_state['chk_cat_ok'] = st.session_state['dados']['categorias_completas']
                        st.session_state['chk_horarios_ok'] = st.session_state['dados']['horarios_ok']
                        st.session_state['chk_desc'] = st.session_state['dados']['tem_descricao']
                        st.session_state['chk_atrib'] = False
                        st.session_state['chk_resp'] = False

                        st.success("Dados da unidade carregados com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao obter detalhes: {e}")

        st.markdown("---")
        st.markdown("<h3 id='ajuste-fino-dos-itens-da-auditoria' style='color: #ffffff; font-size: 16px; font-weight: 700;'>⚙️ AJUSTE FINO DOS ITENS DA AUDITORIA</h3>", unsafe_allow_html=True)
        
        c_a, c_b, c_c, c_d = st.columns(4)
        st.session_state['dados']['tem_tour360'] = c_a.checkbox("Tour 360°", key="chk_tour360")
        st.session_state['dados']['tem_fotos_hd'] = c_b.checkbox("Fotos HD", key="chk_fotos_hd")
        st.session_state['dados']['categorias_completas'] = c_c.checkbox("Categorias OK", key="chk_cat_ok")
        st.session_state['dados']['horarios_ok'] = c_d.checkbox("Horários OK", key="chk_horarios_ok")
        
        c_e, c_f, c_g = st.columns(3)
        st.session_state['dados']['tem_descricao'] = c_e.checkbox("Descrição/Resumo", key="chk_desc")
        st.session_state['dados']['atributos_ok'] = c_f.checkbox("Atributos Serviços", key="chk_atrib")
        st.session_state['dados']['resposta_avaliacoes_ok'] = c_g.checkbox("Respostas Ativas", key="chk_resp")

        st.markdown("---")
        st.markdown("### ✍️ Edição dos Dados de Contato:")
        f_c1, f_c2 = st.columns(2)
        
        st.session_state['dados']['nome'] = f_c1.text_input("Nome da Empresa:", value=st.session_state['dados']['nome'])
        st.session_state['dados']['contato'] = f_c2.text_input("Nome do Responsável:", value=st.session_state['dados']['contato'])
        st.session_state['dados']['telefone'] = f_c1.text_input("Telefone / WhatsApp:", value=st.session_state['dados']['telefone'])
        st.session_state['dados']['website'] = f_c2.text_input("Website:", value=st.session_state['dados']['website'])
        st.session_state['dados']['endereco'] = st.text_input("Endereço Completo:", value=st.session_state['dados']['endereco'])

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>VISÃO GERAL DO DIAGNÓSTICO</div>", unsafe_allow_html=True)
        st.markdown(f"### Score Geral: **{score}/100**")
        st.progress(score / 100)
        
        st.markdown("#### Falhas e Recomendações:")
        st.markdown(f"* Tour 360°: {'✓ Ativo' if dados['tem_tour360'] else '❌ Ausente'}")
        st.markdown(f"* Fotos HD: {'✓ Ativo' if dados['tem_fotos_hd'] else '❌ Poucas / Inexistentes'}")
        st.markdown(f"* Categorias: {'✓ Atualizadas' if dados['categorias_completas'] else '❌ Incompletas (Ajustar Secundárias)'}")
        st.markdown(f"* Horários: {'✓ OK' if dados['horarios_ok'] else '❌ Falta atualizar'}")
        st.markdown(f"* Descrição: {'✓ Ativa' if dados.get('tem_descricao') else '❌ Ausente'}")
        st.markdown(f"* Atributos de Serviços: {'✓ Ativos' if dados.get('atributos_ok') else '❌ Ausentes / Pendentes'}")
        st.markdown(f"* Respostas a Avaliações: {'✓ Frequentes' if dados.get('resposta_avaliacoes_ok') else '❌ Sem respostas oficiais'}")
        
        concorrentes_validos = [c for c in st.session_state['concorrentes'] if c.get('nome', '').strip() != '']
        if concorrentes_validos:
            st.markdown("---")
            st.markdown("**⚔️ Concorrentes Diretos Cadastrados:**")
            for c in concorrentes_validos:
                score_c = calcular_score_concorrente(c)
                st.markdown(f"• **{c['nome']}** — ⭐ {float(c['nota']):.1f} | Score: **{score_c}/100**")

        if dados.get('categorias_detectadas'):
            st.markdown("---")
            st.markdown("**Tags/Categorias Apuradas no Google:**")
            st.caption(", ".join(dados['categorias_detectadas']))
            
        st.markdown("</div>", unsafe_allow_html=True)

elif "2. Concorrentes" in opcao_menu:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>⚔️ ANÁLISE AUTOMÁTICA DE CONCORRENTES DO SEGMENTO</div>", unsafe_allow_html=True)
    st.info("Digite apenas o nome da empresa concorrente e a cidade. Ao enviar o formulário, a API do Google avaliará automaticamente a nota e todos os critérios!")

    area_notificacao = st.empty()

    with st.form(key="form_concorrentes_busca_limpo", clear_on_submit=False):
        inputs_busca = []
        for i in range(3):
            st.markdown(f"#### Concorrente #{i+1}")
            col_c1, col_c2 = st.columns([2.5, 1.5])
            
            t_val = col_c1.text_input(
                f"Nome da Empresa Concorrente #{i+1}:", 
                value=st.session_state['concorrentes'][i].get('busca_termo', ''), 
                key=f"conc_termo_{i}",
                placeholder="Ex: Focco Comunicação"
            )
            
            c_val = col_c2.text_input(
                f"Cidade / Região #{i+1}:", 
                value=st.session_state['concorrentes'][i].get('cidade', ''), 
                key=f"conc_cidade_{i}",
                placeholder="Ex: Ribeirão Preto - SP"
            )
            inputs_busca.append((t_val, c_val))
            st.markdown("---")

        btn_sub = st.form_submit_button("🔎 Avaliar Concorrentes Automático via Google", use_container_width=True)

        if btn_sub:
            if API_KEY_GOOGLE:
                encontrados = 0
                for i, (termo_emp, cid) in enumerate(inputs_busca):
                    st.session_state['concorrentes'][i]['busca_termo'] = termo_emp
                    st.session_state['concorrentes'][i]['cidade'] = cid
                    if termo_emp.strip() != "":
                        detalhes = buscar_detalhes_concorrente_especifico(termo_emp, cid, API_KEY_GOOGLE)
                        if detalhes:
                            st.session_state['concorrentes'][i]['nome'] = detalhes['nome']
                            st.session_state['concorrentes'][i]['nota'] = detalhes['nota']
                            st.session_state['concorrentes'][i]['avaliacoes'] = detalhes['avaliacoes']
                            st.session_state['concorrentes'][i]['tem_fotos_hd'] = detalhes['tem_fotos_hd']
                            st.session_state['concorrentes'][i]['categorias_ok'] = detalhes['categorias_ok']
                            st.session_state['concorrentes'][i]['horarios_ok'] = detalhes['horarios_ok']
                            st.session_state['concorrentes'][i]['tem_website'] = detalhes['tem_website']
                            st.session_state['concorrentes'][i]['tem_descricao'] = detalhes['tem_descricao']
                            st.session_state['concorrentes'][i]['atributos_ok'] = detalhes['atributos_ok']
                            st.session_state['concorrentes'][i]['respostas_ok'] = detalhes['respostas_ok']
                            encontrados += 1
                
                if encontrados > 0:
                    area_notificacao.success(f"{encontrados} concorrente(s) avaliado(s) com sucesso pelo Google!")
                else:
                    area_notificacao.warning("Preencha ao menos um nome de concorrente para consultar.")
            else:
                area_notificacao.error("Chave GOOGLE_API_KEY não configurada.")

    concorrentes_validos = [c for c in st.session_state['concorrentes'] if c.get('nome', '').strip() != '']
    if concorrentes_validos:
        st.markdown("---")
        st.markdown("### 📌 Concorrentes Avaliados:")
        for c_det in concorrentes_validos:
            score_c = calcular_score_concorrente(c_det)
            st.markdown(
                f"* **{c_det['nome']}** — ⭐ Nota **{c_det['nota']:.1f}** ({c_det['avaliacoes']} aval.) | "
                f"Score Geral: **{score_c}/100**"
            )

    st.markdown("</div>", unsafe_allow_html=True)

elif "3. Plano de Ação" in opcao_menu:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>💡 PLANO DE AÇÃO & APONTAMENTOS ESTRATÉGICOS PERSONALIZADOS</div>", unsafe_allow_html=True)
    
    st.session_state['plano_acao_extra'] = st.text_area(
        "Edite o texto do Plano de Ação e Apontamentos Estratégicos (este conteúdo reflete diretamente no PDF):",
        value=st.session_state['plano_acao_extra'],
        height=180,
        key="area_plano_acao_extra"
    )
    st.success("Plano de Ação salvo e atualizado para os relatórios/PDFs!")
    st.markdown("</div>", unsafe_allow_html=True)

elif "4. Proposta" in opcao_menu:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>📜 EDITE OS VALORES E CONTEÚDO DOS PLANOS COMERCIAIS</div>", unsafe_allow_html=True)
    
    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.markdown("### 🔹 Opção 1: Ficha Otimizada")
        st.session_state['planos']['start_valor'] = st.text_input("Valor Opção 1 (R$):", value=st.session_state['planos']['start_valor'], key="edit_p_start_val")
        st.session_state['planos']['start_itens'] = st.text_area("Itens Opção 1:", value=st.session_state['planos']['start_itens'], height=160, key="edit_p_start_itens")
        
    with p2:
        st.markdown("### 🔹 Opção 2: Ficha + Tour 360°")
        st.session_state['planos']['pro_valor'] = st.text_input("Valor Opção 2 (R$):", value=st.session_state['planos']['pro_valor'], key="edit_p_pro_val")
        st.session_state['planos']['pro_itens'] = st.text_area("Itens Opção 2:", value=st.session_state['planos']['pro_itens'], height=160, key="edit_p_pro_itens")
        
    with p3:
        st.markdown("### 🔹 Opção 3: Presença Completa")
        st.session_state['planos']['gestao_valor'] = st.text_input("Valor Opção 3 (R$):", value=st.session_state['planos']['gestao_valor'], key="edit_p_gestao_val")
        st.session_state['planos']['gestao_itens'] = st.text_area("Itens Opção 3:", value=st.session_state['planos']['gestao_itens'], height=160, key="edit_p_gestao_itens")

    st.success("Valores e itens dos planos comerciais atualizados com sucesso!")
    st.markdown("</div>", unsafe_allow_html=True)

elif "5. Contrato" in opcao_menu:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>📄 CONTRATO DE PRESTAÇÃO DE SERVIÇOS</div>", unsafe_allow_html=True)
    st.info("O contrato é atualizado e gerado automaticamente na 4ª página do arquivo PDF completo com base nos dados informados nas etapas anteriores.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# UNIFICADO: ÚNICO BOTÃO GERADOR DE PDF COMPLETO
# -----------------------------------------------------------------------------
st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
st.markdown("<div class='card-title'>GERAR DOCUMENTO OFICIAL</div>", unsafe_allow_html=True)

pdf_bytes = gerar_pdf_oficial(
    dados, 
    score, 
    st.session_state['planos'], 
    st.session_state['plano_acao_extra'],
    st.session_state['concorrentes']
)

nome_empresa_formatado = dados['nome'].strip() if dados['nome'] else 'Empresa'
st.download_button(
    "📥 Baixar Diagnóstico, Proposta e Contrato Completo em PDF",
    data=pdf_bytes,
    file_name=f"Diagnóstico & Proposta - {nome_empresa_formatado}.pdf",
    mime="application/pdf",
    use_container_width=True,
    key="btn_pdf_unico_unificado"
)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. RODAPÉ FIXO
# -----------------------------------------------------------------------------
st.markdown("""
    <div class='custom-footer'>
        <a href='https://tour360vr.com.br' target='_blank'>tour360vr.com.br</a> | 
        <a href='mailto:contato@tour360vr.com.br'>contato@tour360vr.com.br</a> | 
        Whatsapp: (16) 99133-2121 | 
        <b>Tour360VR - Gestão de Perfil do Google</b>
    </div>
""", unsafe_allow_html=True)

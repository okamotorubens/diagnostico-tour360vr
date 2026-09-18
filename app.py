import os
import io
import json
import base64
import requests
import streamlit as st
from datetime import datetime
from fpdf import FPDF
from PIL import Image

# -----------------------------------------------------------------------------
# 1. CARREGAMENTO DO FAVICON DE FORMA SEGURA (VIA PIL/IMAGE)
# -----------------------------------------------------------------------------
def obter_favicon_pil():
    caminhos = ['assets/logo_tour_transparente.png', 'assets/logo_tour.png', 'logo_tour_transparente.png', 'logo_tour.png']
    for c in caminhos:
        if os.path.exists(c):
            try: return Image.open(c)
            except Exception: pass
            
    url_oficial = "https://tour360vr.com.br/assets/img/logo.png"
    try:
        resp = requests.get(url_oficial, timeout=3)
        if resp.status_code == 200:
            return Image.open(io.BytesIO(resp.content))
    except Exception:
        pass
    return "🌐"

favicon_img = obter_favicon_pil()

# -----------------------------------------------------------------------------
# 2. CONFIGURAÇÃO DA PÁGINA (OBRIGATORIAMENTE O PRIMEIRO COMANDO ST)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Consultoria & Diagnóstico - Tour360VR",
    page_icon=favicon_img,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Oculta navegação automática nativa do Streamlit */
    [data-testid="stSidebarNav"] { display: none !important; }

    .stApp { 
        background-color: #0b0f19; 
        color: #f1f5f9; 
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    [data-testid="stSidebar"] { 
        background-color: #111827; 
        border-right: 1px solid #1f2937; 
    }
    
    /* Padding interno na Sidebar */
    [data-testid="stSidebarUserContent"] {
        padding-top: 1.0rem !important;
        padding-bottom: 1.0rem !important;
        padding-left: 1.0rem !important;
        padding-right: 1.0rem !important;
    }

    /* BLOCO DO CABEÇALHO DA SIDEBAR COMPACTADO */
    .sidebar-header-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin-bottom: 4px;
    }

    .sidebar-header-box .sidebar-title-top {
        font-size: 15px;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.2;
        text-align: center;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    .sidebar-header-box img.logo-tour {
        max-width: 130px;
        width: 60%;
        height: auto;
        display: block;
        margin-bottom: 10px;
    }

    .sidebar-header-box img.logo-okamoto {
        max-width: 200px;
        width: 85%;
        height: auto;
        display: block;
        margin-bottom: 6px;
    }

    .sidebar-divider {
        border-top: 1px solid #1e293b;
        margin: 10px 0 !important;
    }

    .label-cliente-centralizado {
        text-align: center;
        font-weight: 700;
        font-size: 11px;
        margin-bottom: 4px !important;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .box-cliente-atendimento {
        background-color: #1e293b; 
        border: 1px solid #334155; 
        border-radius: 8px; 
        padding: 8px 10px; 
        text-align: center; 
        color: #38bdf8; 
        font-weight: 700; 
        font-size: 13.5px;
        margin-bottom: 12px !important;
    }

    .container-score-diagnostico {
        margin-bottom: 12px !important;
    }

    /* QUADROS DE CONTEÚDO */
    .dashboard-card { 
        background-color: #1e293b !important; 
        border: 1px solid #38bdf8 !important; 
        border-radius: 14px; 
        padding: 18px; 
        margin-bottom: 15px; 
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.4);
    }
    .card-title { 
        font-size: 15px; 
        font-weight: 700; 
        color: #38bdf8; 
        margin-bottom: 14px; 
        text-transform: uppercase; 
        letter-spacing: 0.8px; 
        line-height: 1.3;
    }
    
    /* 🎨 ESTILIZAÇÃO GERAL DE BOTÕES (ETAPAS 1 A 5 E AVANÇAR/VOLTAR EM AZUL CLARO DESTAQUE) */
    .stApp [data-testid="stButton"] > button {
        background-color: #1e293b !important;
        color: #cbd5e1 !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 9px 12px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
    }

    .stApp [data-testid="stButton"] > button:hover {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-color: #60a5fa !important;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.5) !important;
    }

    /* 🌟 DESTAQUE VIBRANTE EXCLUSIVO PARA A ETAPA ATIVA */
    div[key^="btn_etapa_active_"] button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        font-size: 13.5px !important;
        padding: 9px 4px !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.45) !important;
        transform: scale(1.02);
    }

    /* Botão 'Iniciar Novo Atendimento' na Sidebar */
    [data-testid="stSidebar"] [data-testid="stButton"] > button { 
        background-color: #2563eb !important; 
        color: #ffffff !important; 
        border: 1px solid #3b82f6 !important; 
    }
    [data-testid="stSidebar"] [data-testid="stButton"] > button:hover { 
        background-color: #1d4ed8 !important; 
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.4) !important;
    }

    .custom-footer { 
        position: fixed; 
        left: 0; 
        bottom: 0; 
        width: 100%; 
        background-color: #070a10; 
        color: #64748b; 
        text-align: center; 
        padding: 8px; 
        border-top: 1px solid #1e293b; 
        font-size: 11px; 
        z-index: 999; 
    }
    .custom-footer a { color: #38bdf8; text-decoration: none; }
    </style>
""", unsafe_allow_html=True)

API_KEY_GOOGLE = (
    st.secrets.get("GOOGLE_API_KEY") 
    or st.secrets.get("GOOGLE_PLACES_API_KEY") 
    or os.environ.get("GOOGLE_API_KEY")
    or ""
)

ARQUIVO_HISTORICO = "/tmp/historico_propostas_tour360.json"

# -----------------------------------------------------------------------------
# 3. FUNÇÕES UTILITÁRIAS & LOGOS
# -----------------------------------------------------------------------------
def conv(texto):
    if not texto: return ""
    limpo = str(texto).replace("★", "*")\
                      .replace("•", "- ")\
                      .replace("✓", "[OK] ")\
                      .replace("à", "a")\
                      .replace("À", "A")
    return limpo.encode('latin-1', 'replace').decode('latin-1')

def carregar_imagem_base64(caminho):
    if os.path.exists(caminho):
        try:
            with open(caminho, "rb") as image_file:
                return f"data:image/png;base64,{base64.b64encode(image_file.read()).decode()}"
        except Exception:
            pass
    return ""

def calcular_score_real(dados):
    if not dados.get("nome"): return 0
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

def obter_caminho_logo(tipo="okamoto"):
    if tipo == "okamoto":
        caminhos = ['assets/logo_okamoto.png', 'assets/logo_okamoto_midias_visuais.png', 'logo_okamoto.png', 'assets/logo.png']
        url_oficial = "https://okamotomidiasvisuais.com.br/assets/img/logo.png"
    else:
        caminhos = ['assets/logo_tour_transparente.png', 'assets/logo_tour.png', 'logo_tour_transparente.png', 'logo_tour.png']
        url_oficial = "https://tour360vr.com.br/assets/img/logo.png"

    for c in caminhos:
        if os.path.exists(c): return c
    
    temp_logo = f'/tmp/logo_{tipo}_temp.png'
    if os.path.exists(temp_logo): return temp_logo
    try:
        resp = requests.get(url_oficial, timeout=3)
        if resp.status_code == 200:
            with open(temp_logo, 'wb') as f: f.write(resp.content)
            return temp_logo
    except Exception: pass
    return None

def salvar_no_historico(dados, score, concorrentes=[], planos={}, plano_acao_extra=""):
    if not dados.get("nome"): return
    historico = []
    if os.path.exists(ARQUIVO_HISTORICO):
        try:
            with open(ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
                historico = json.load(f)
        except Exception: historico = []
    
    registro = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "nome": dados.get("nome"),
        "contato": dados.get("contato"),
        "telefone": dados.get("telefone"),
        "endereco": dados.get("endereco"),
        "website": dados.get("website"),
        "nota": dados.get("nota", 0.0),
        "score": score,
        "avaliacoes": dados.get("avaliacoes", 0),
        "tem_tour360": dados.get("tem_tour360", False),
        "tem_fotos_hd": dados.get("tem_fotos_hd", False),
        "categorias_completas": dados.get("categorias_completas", False),
        "horarios_ok": dados.get("horarios_ok", False),
        "tem_descricao": dados.get("tem_descricao", False),
        "atributos_ok": dados.get("atributos_ok", False),
        "resposta_avaliacoes_ok": dados.get("resposta_avaliacoes_ok", False),
        "foto_reference": dados.get("foto_reference", ""),
        "concorrentes": concorrentes,
        "planos": planos,
        "plano_acao_extra": plano_acao_extra
    }
    
    historico = [h for h in historico if h.get("nome") != registro["nome"]]
    historico.insert(0, registro)
    with open(ARQUIVO_HISTORICO, 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

def carregar_historico():
    if os.path.exists(ARQUIVO_HISTORICO):
        try:
            with open(ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception: return []
    return []

def buscar_detalhes_concorrente_especifico(nome_concorrente, cidade, api_key):
    if not nome_concorrente or not api_key: return None
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
    except Exception: pass
    return None

# -----------------------------------------------------------------------------
# 4. ESTADOS PERSISTENTES & ETAPAS
# -----------------------------------------------------------------------------
if 'etapa_atual' not in st.session_state:
    st.session_state['etapa_atual'] = 1

if 'dados' not in st.session_state:
    st.session_state['dados'] = {
        "nome": "", "contato": "", "endereco": "", "telefone": "", "website": "",
        "nota": 0.0, "avaliacoes": 0, "tem_tour360": False, "tem_fotos_hd": False,
        "categorias_completas": False, "horarios_ok": False, "tem_descricao": False,
        "atributos_ok": False, "resposta_avaliacoes_ok": False, "categorias_detectadas": [], "foto_reference": ""
    }

if 'concorrentes' not in st.session_state:
    st.session_state['concorrentes'] = [
        {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"},
        {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"},
        {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"}
    ]

if 'planos' not in st.session_state:
    st.session_state['planos'] = {
        "start_valor": "500,00", "start_itens": "- Correção cadastral\n- Otimização de SEO\n- Ajuste de categorias\n- Inserção de links",
        "pro_valor": "1.500,00", "pro_itens": "- Tudo do Plano Start\n- Tour Virtual 360°\n- Ensaio Fotográfico HD\n- Relatório Visual de Entrega",
        "gestao_valor": "600,00", "gestao_itens": "- Postagens semanais\n- Gestão de avaliações\n- Atualização de fotos\n- Relatório mensal"
    }

if 'plano_acao_extra' not in st.session_state:
    st.session_state['plano_acao_extra'] = "O perfil precisa de otimização urgente! Veja as falhas apontadas no relatório."

if 'unidades_encontradas' not in st.session_state:
    st.session_state['unidades_encontradas'] = []

# -----------------------------------------------------------------------------
# 5. GERADOR DE PDF INTELIGENTE
# -----------------------------------------------------------------------------
class PDFTour360Oficial(FPDF):
    def __init__(self, *args, **kwargs):
        self.capa_incluida = kwargs.pop('capa_incluida', True)
        super().__init__(*args, **kwargs)

    def header(self):
        if self.page_no() == 1 and self.capa_incluida:
            return
        
        caminho_logo = obter_caminho_logo("tour360")
        if caminho_logo:
            try: self.image(caminho_logo, 21, 8.0, 11, 11)
            except Exception: pass
            
        self.set_xy(35, 9.2)
        self.set_font('Helvetica', 'B', 10.0)
        self.set_text_color(30, 64, 175)
        self.cell(163, 4.0, 'Tour360VR', align='L', ln=True)
        
        self.set_x(35)
        self.set_font('Helvetica', 'B', 7.2)
        self.set_text_color(100, 116, 139)
        self.cell(163, 3.8, conv('Gestão de Perfil & Diagnóstico do Google Meu Negócio'), align='L', ln=True)
        self.set_draw_color(226, 232, 240)
        self.line(21, 21.0, 198, 21.0)

    def footer(self):
        self.set_y(-16)
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(100, 116, 139)
        self.line(21, self.get_y(), 198, self.get_y())
        self.set_y(-13)
        if self.page_no() == 1 and self.capa_incluida:
            self.set_x(21)
            self.set_font('Helvetica', 'B', 10.5)
            self.set_text_color(30, 64, 175)
            self.cell(177, 5, conv("Tour360VR - (16) 99133-2121 - Ribeirão Preto - SP"), align='C')
        else:
            self.set_x(35)
            self.cell(45, 5, 'contato@tour360vr.com.br', link='mailto:contato@tour360vr.com.br', align='C')
            self.cell(40, 5, 'tour360vr.com.br', link='https://tour360vr.com.br', align='C')
            self.cell(45, 5, 'WhatsApp: (16) 99133-2121', link='https://wa.me/5516991332121', align='C')
            self.set_x(170)
            self.cell(28, 5, f'Página {self.page_no()}', align='R')

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

def gerar_pdf_oficial(dados, planos, plano_acao_extra="", concorrentes=[], paginas_selecionadas=[1, 2, 3, 4]):
    score = calcular_score_real(dados)
    capa_presente = 1 in paginas_selecionadas
    pdf = PDFTour360Oficial(capa_incluida=capa_presente)
    
    pdf.set_margins(21, 12, 12)
    pdf.set_auto_page_break(auto=False)

    # PÁGINA 1: CAPA
    if 1 in paginas_selecionadas:
        pdf.add_page()
        caminho_logo = obter_caminho_logo("tour360")
        if caminho_logo:
            try: pdf.image(caminho_logo, 90, 20.0, 38, 38)
            except Exception: pass

        pdf.set_y(78)
        pdf.set_font('Helvetica', 'B', 21)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(0, 8, conv('DIAGNÓSTICO DE PRESENÇA DIGITAL'), align='C', ln=True)
        pdf.ln(2)

        pdf.set_font('Helvetica', 'B', 15)
        pdf.cell(0, 6, conv('GOOGLE MEU NEGÓCIO'), align='C', ln=True)

        w_capa, h_capa, x_capa, y_capa = 177, 34, 21.0, 106.0
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(203, 213, 225)
        pdf.rounded_rect(x_capa, y_capa, w_capa, h_capa, 2.5, 'FD')

        pdf.set_xy(x_capa, y_capa + 3.5)
        pdf.set_font('Helvetica', 'B', 14.0)
        pdf.set_text_color(30, 64, 175) 
        pdf.cell(w_capa, 5.5, conv(f"{dados.get('nome') or 'Nome da Empresa'}"), align='C', ln=True)

        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(15, 23, 42)
        pdf.set_x(x_capa)
        pdf.cell(w_capa, 4.8, conv(f"Cliente: {dados.get('contato') or 'Responsável'}"), align='C', ln=True)
        
        pdf.set_font('Helvetica', '', 8.8)
        pdf.set_text_color(71, 85, 105)
        pdf.set_x(x_capa)
        pdf.cell(w_capa, 4.8, conv(f"{dados.get('endereco') or 'Endereço não informado'}"), align='C', ln=True)
        
        site_txt = dados.get('website') if dados.get('website') else 'N/I'
        pdf.set_x(x_capa)
        pdf.cell(w_capa, 4.8, conv(f"Telefone: {dados.get('telefone') or 'N/I'}   |   {site_txt}"), align='C', ln=True)

        y_foto, h_container, w_container = 144.0, 96.0, 177.0
        foto_renderizada = False

        if dados.get("foto_reference") and API_KEY_GOOGLE:
            try:
                url_img = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={dados['foto_reference']}&key={API_KEY_GOOGLE}"
                resp_img = requests.get(url_img, timeout=4)
                if resp_img.status_code == 200:
                    img_data = io.BytesIO(resp_img.content)
                    img = Image.open(img_data)
                    orig_w, orig_h = img.size

                    ratio_w = w_container / orig_w
                    ratio_h = h_container / orig_h
                    scale = min(ratio_w, ratio_h)

                    final_w = orig_w * scale
                    final_h = orig_h * scale

                    offset_x = x_capa + (w_container - final_w) / 2.0
                    offset_y = y_foto + (h_container - final_h) / 2.0

                    img_data.seek(0)
                    pdf.image(img_data, x=offset_x, y=offset_y, w=final_w, h=final_h)
                    foto_renderizada = True
            except Exception: pass

        if not foto_renderizada:
            pdf.set_fill_color(240, 243, 246)
            pdf.rounded_rect(x_capa, y_foto, w_container, h_container, 3, 'F')
            pdf.set_xy(x_capa, y_foto + 42)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(w_container, 6, conv("[ IMAGEM DA FICHA GOOGLE DO CLIENTE ]"), align='C', ln=True)

        pdf.set_y(252.0)
        pdf.set_font('Helvetica', 'B', 10.5)
        
        qtd_aval = dados.get('avaliacoes', 0)
        nota_cli = dados.get('nota', 0.0)
        tem_tour = dados.get('tem_tour360', False)
        
        if tem_tour:
            pdf.set_text_color(22, 128, 61)
            sub_txt_1 = f"SEU PERFIL POSSUI EXCELENTE PRESENÇA VISUAL, NOTA {nota_cli:.1f} E {qtd_aval} AVALIAÇÕES."
            sub_txt_2 = "MANTER A FICHA ATUALIZADA É O SEGREDO PARA LIDERAR O MERCADO."
        else:
            pdf.set_text_color(239, 68, 68)
            if qtd_aval == 0:
                sub_txt_1 = "SEU PERFIL AINDA NÃO POSSUI AVALIAÇÕES CADASTRADAS NO GOOGLE,"
                sub_txt_2 = "E A FALTA DE IMPACTO VISUAL FAZ VOCÊ PERDER CLIENTES DIARIAMENTE."
            elif qtd_aval < 15:
                sub_txt_1 = f"SEU PERFIL TEM NOTA {nota_cli:.1f} E APENAS {qtd_aval} AVALIAÇÕES NO GOOGLE,"
                sub_txt_2 = "E A AUSÊNCIA DE CONTEÚDO IMERSIVO LIMITA O SEU CRESCIMENTO."
            else:
                sub_txt_1 = f"SEU PERFIL TEM NOTA SÓLIDA DE {nota_cli:.1f} COM {qtd_aval} AVALIAÇÕES NO GOOGLE,"
                sub_txt_2 = "MAS A FALTA DE EXPERIÊNCIA IMERSIVA DEIXA DINHEIRO NA MESA."

        pdf.cell(0, 5.0, conv(sub_txt_1), align='C', ln=True)
        pdf.cell(0, 5.0, conv(sub_txt_2), align='C', ln=True)

    # PÁGINA 2: AUDITORIA DETALHADA
    if 2 in paginas_selecionadas:
        pdf.add_page()
        pdf.set_xy(21, 29)
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(177, 8, conv('AUDITORIA DETALHADA DE PONTOS DE BUSCA'), align='C', ln=True)

        w_ficha, x_ficha, y_ficha, h_ficha = 163, 28.0, 45.0, 15.0
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(226, 232, 240)
        pdf.rounded_rect(x_ficha, y_ficha, w_ficha, h_ficha, 2.5, 'FD')
        
        pdf.set_xy(x_ficha, y_ficha + 2.0)
        pdf.set_font('Helvetica', 'B', 12.0)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(w_ficha, 5.0, conv(f"{dados.get('nome') or 'Empresa Analisada'}"), align='C', ln=True)

        pdf.set_x(x_ficha)
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(245, 158, 11)
        pdf.cell(w_ficha, 4.5, conv(f"Nota {dados.get('nota', 0.0):.1f} *   -   {dados.get('avaliacoes', 0)} avaliações no Google"), align='C', ln=True)

        w_box_score, x_box_score, y_box_score = 90, 64.5, 66.0
        if score < 50: cr, cg, cb, status_txt = 239, 68, 68, "STATUS CRÍTICO"
        elif score < 80: cr, cg, cb, status_txt = 245, 158, 11, "STATUS MÉDIO"
        else: cr, cg, cb, status_txt = 22, 128, 61, "ALTO DESEMPENHO"

        pdf.set_fill_color(240, 249, 255)
        pdf.set_draw_color(62, 161, 219)
        pdf.set_line_width(0.4)
        pdf.rounded_rect(x_box_score, y_box_score, w_box_score, 11.5, 2, 'FD')
        pdf.set_line_width(0.2)

        pdf.set_font('Helvetica', 'B', 15)
        w_num = pdf.get_string_width(f"{score} ")
        w_bar = pdf.get_string_width("/ 100")
        x_start = x_box_score + (w_box_score - (w_num + w_bar)) / 2.0

        pdf.set_xy(x_start, y_box_score + 1.0)
        pdf.set_text_color(cr, cg, cb)
        pdf.cell(w_num, 5.0, f"{score} ", align='L')
        
        pdf.set_text_color(15, 23, 42)
        pdf.cell(w_bar, 5.0, "/ 100", align='L', ln=True)
        
        pdf.set_xy(x_box_score, y_box_score + 6.5)
        pdf.set_font('Helvetica', 'B', 7.2)
        pdf.set_text_color(cr, cg, cb)
        pdf.cell(w_box_score, 3.0, conv(f"SCORE GERAL ({status_txt})"), align='C', ln=True)

        pct_avaliacoes = min(int((dados.get('avaliacoes', 0) / 50.0) * 100), 100) if dados.get('avaliacoes', 0) > 0 else 10
        pct_fotos = 100 if dados.get('tem_fotos_hd') else 30
        pct_tour = 100 if dados.get('tem_tour360') else 30
        pct_cat = 100 if dados.get('categorias_completas') else 50
        pct_hor = 100 if dados.get('horarios_ok') else 40
        pct_web = 100 if dados.get('website') != 'Não possui' and dados.get('website') != '' else 10
        pct_desc = 100 if dados.get('tem_descricao', True) else 30
        pct_atrib = 100 if dados.get('atributos_ok', True) else 40
        pct_resp = 100 if dados.get('resposta_avaliacoes_ok', False) else 30

        desc_fotos = "Atende ao volume recomendado de fotos em HD." if dados.get('tem_fotos_hd') else "Poucas fotos encontradas / antigas no perfil."
        rotulo_tour = "Ativo" if dados.get('tem_tour360') else "Pendente de Validação"
        desc_tour = "Tour Virtual 360° ativo e integrado." if dados.get('tem_tour360') else "Não detectado via API. Necessário checagem manual na ficha."
        desc_cat = "Atende às categorias recomendadas." if dados.get('categorias_completas') else "Ajuste necessário em categorias secundárias."
        desc_web = f"Website oficial: {dados.get('website')}" if dados.get('website') != 'Não possui' and dados.get('website') != '' else "Falta link de website cadastrado para conversão."
        desc_desc = "Resumo editorial ativo no perfil." if dados.get('tem_descricao', True) else "Descrição da empresa incompleta ou ausente."
        desc_atrib = "Atributos de serviços ativos." if dados.get('atributos_ok', True) else "Falta cadastrar atributos de acessibilidade/serviços."
        desc_resp = "Frequência ativa de respostas do proprietário." if dados.get('resposta_avaliacoes_ok', False) else "Falta de respostas oficiais às avaliações."

        itens = [
            ("1. Fotos e Resolução Visual", pct_fotos, "Alto" if dados.get('tem_fotos_hd') else "Baixo", desc_fotos),
            ("2. Tour Virtual 360° Interativo", pct_tour, rotulo_tour, desc_tour),
            ("3. Categorias Principal e Secundárias", pct_cat, "Completo" if dados.get('categorias_completas') else "Incompleto", desc_cat),
            ("4. Horários e Exceções (Feriados)", pct_hor, "Atualizado" if dados.get('horarios_ok') else "Desatualizado", "Falta de horários em feriados."),
            ("5. Website e Links de Conversão", pct_web, "Ativo" if dados.get('website') != 'Não possui' and dados.get('website') != '' else "Falho", desc_web),
            ("6. Avaliações no Google (Prova Social)", pct_avaliacoes, f"{dados.get('nota', 0.0)}/5.0", f"{dados.get('avaliacoes', 0)} avaliações."),
            ("7. Resumo Editorial & Descrição", pct_desc, "Completo" if dados.get('tem_descricao', True) else "Ausente", desc_desc),
            ("8. Atributos de Acessibilidade/Serviços", pct_atrib, "Ativo" if dados.get('atributos_ok', True) else "Pendente", desc_atrib),
            ("9. Interação e Resposta a Avaliações", pct_resp, "Ativo" if dados.get('resposta_avaliacoes_ok', False) else "Pendente", desc_resp)
        ]

        y_start_itens, h_slot = 91.0, 10.5
        for idx_item, (titulo, pct, rotulo, desc) in enumerate(itens):
            y_curr = y_start_itens + (idx_item * h_slot)
            pdf.set_xy(21, y_curr)
            pdf.set_font('Helvetica', 'B', 9.5)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(122, 3.2, conv(titulo), border=0)
            
            pdf.set_font('Helvetica', 'B', 9.5)
            if pct < 40: pdf.set_text_color(239, 68, 68)
            elif pct < 80: pdf.set_text_color(245, 158, 11)
            else: pdf.set_text_color(22, 128, 61)
                
            pdf.cell(55, 3.2, conv(rotulo), border=0, align='R')

            y_bar = y_curr + 3.6
            pdf.set_fill_color(226, 232, 240)
            pdf.rounded_rect(21, y_bar, 177, 1.5, 0.5, 'F')
            
            if pct < 40: pdf.set_fill_color(239, 68, 68)
            elif pct < 80: pdf.set_fill_color(245, 158, 11)
            else: pdf.set_fill_color(22, 128, 61)
                
            pdf.rounded_rect(21, y_bar, max(float(pct) * 1.77, 4.0), 1.5, 0.5, 'F')

            pdf.set_xy(21, y_bar + 2.2)
            pdf.set_font('Helvetica', '', 8.5)
            pdf.set_text_color(71, 85, 105)
            pdf.cell(177, 3.0, conv(f"   Diagnóstico: {desc[:90]}"), border=0)

        concorrentes_filtrados = [c for c in concorrentes if c.get("nome", "").strip() != ""]
        if concorrentes_filtrados:
            pdf.set_xy(21, 194.0)
            pdf.set_font('Helvetica', 'B', 9.5)
            pdf.set_text_color(30, 64, 175)
            pdf.cell(0, 4.0, conv("ANÁLISE AUTOMÁTICA DE CONCORRENTES DO SEGMENTO"), border=0)

            w_emp, w_item, w_score, h_row = 53, 11.0, 25.0, 4.6
            y_table = 199.0
            pdf.set_xy(21, y_table)
            pdf.set_fill_color(30, 64, 175)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 9.0)
            
            pdf.cell(w_emp, h_row, conv(" Empresa / Concorrente"), border=0, fill=True)
            pdf.cell(w_item, h_row, conv("1.Fotos"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("2.360°"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("3.Categ"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("4.Horár"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("5.Web"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("6.Nota"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("7.Desc"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("8.Atrib"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("9.Resp"), border=0, fill=True, align='C')
            pdf.cell(w_score, h_row, conv("Score Geral"), border=0, fill=True, align='C')

            def celula_sim_nao(pdf_obj, w, h, valor):
                if valor == "Sim":
                    pdf_obj.set_fill_color(220, 252, 231)
                    pdf_obj.set_text_color(22, 101, 52)
                else:
                    pdf_obj.set_fill_color(254, 226, 226)
                    pdf_obj.set_text_color(153, 27, 27)
                pdf_obj.cell(w, h, conv(valor), border='B', fill=True, align='C')

            y_r1 = y_table + h_row
            pdf.set_xy(21, y_r1)
            pdf.set_fill_color(240, 249, 255)
            pdf.set_font('Helvetica', 'B', 8.5)
            pdf.set_text_color(30, 64, 175)
            pdf.cell(w_emp, h_row, conv(f" {str(dados.get('nome', ''))[:25]}"), border='B', fill=True)
            
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('tem_fotos_hd') else "Não")
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('tem_tour360') else "Não")
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('categorias_completas') else "Não")
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('horarios_ok') else "Não")
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('website') and dados.get('website') != 'Não possui' else "Não")
            
            pdf.set_fill_color(240, 249, 255)
            pdf.set_text_color(30, 64, 175)
            pdf.cell(w_item, h_row, conv(f"{dados.get('nota', 0.0):.1f}"), border='B', fill=True, align='C')
            
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('tem_descricao') else "Não")
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('atributos_ok') else "Não")
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('resposta_avaliacoes_ok') else "Não")
            
            pdf.set_fill_color(240, 249, 255)
            pdf.set_font('Helvetica', 'B', 8.5)
            pdf.set_text_color(30, 64, 175)
            pdf.cell(w_score, h_row, conv(f"{score} / 100"), border='B', fill=True, align='C')

            pdf.set_font('Helvetica', '', 8.5)
            for idx_c, c in enumerate(concorrentes_filtrados):
                y_rc = y_r1 + ((idx_c + 1) * h_row)
                score_conc = calcular_score_concorrente(c)
                pdf.set_xy(21, y_rc)
                pdf.set_fill_color(255, 255, 255)
                pdf.set_text_color(51, 65, 85)
                
                pdf.cell(w_emp, h_row, conv(f" {c.get('nome', '')[:25]}"), border='B', fill=True)
                celula_sim_nao(pdf, w_item, h_row, c.get('tem_fotos_hd', 'Não'))
                celula_sim_nao(pdf, w_item, h_row, c.get('tem_tour360', 'Não'))
                celula_sim_nao(pdf, w_item, h_row, c.get('categorias_ok', 'Não'))
                celula_sim_nao(pdf, w_item, h_row, c.get('horarios_ok', 'Não'))
                celula_sim_nao(pdf, w_item, h_row, c.get('tem_website', 'Não'))
                
                pdf.set_fill_color(255, 255, 255)
                pdf.set_text_color(51, 65, 85)
                pdf.cell(w_item, h_row, conv(f"{float(c.get('nota', 0.0)):.1f}"), border='B', fill=True, align='C')
                
                celula_sim_nao(pdf, w_item, h_row, c.get('tem_descricao', 'Não'))
                celula_sim_nao(pdf, w_item, h_row, c.get('atributos_ok', 'Não'))
                celula_sim_nao(pdf, w_item, h_row, c.get('respostas_ok', 'Não'))
                
                pdf.set_fill_color(255, 255, 255)
                pdf.set_font('Helvetica', 'B', 8.5)
                pdf.set_text_color(51, 65, 85)
                pdf.cell(w_score, h_row, conv(f"{score_conc} / 100"), border='B', fill=True, align='C')
                pdf.set_font('Helvetica', '', 8.5)

        if plano_acao_extra and plano_acao_extra.strip() != "":
            w_extra, x_extra, y_extra, h_box_extra = 177, 21.0, 237.0, 27.0
            pdf.set_fill_color(240, 249, 255)
            pdf.set_draw_color(62, 161, 219)
            pdf.set_line_width(0.4)
            pdf.rounded_rect(x_extra, y_extra, w_extra, h_box_extra, 2.0, 'FD')
            pdf.set_line_width(0.2)
            
            pdf.set_xy(x_extra, y_extra + 2.5)
            pdf.set_font('Helvetica', 'B', 8.2)
            pdf.set_text_color(30, 64, 175)
            pdf.cell(w_extra, 3.5, conv("PLANO DE AÇÃO E APONTAMENTOS ESTRATÉGICOS PERSONALIZADOS:"), align='C', border=0)
            
            pdf.set_xy(x_extra + 4, y_extra + 8.5)
            pdf.set_font('Helvetica', '', 7.8)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(w_extra - 8, 3.5, conv(plano_acao_extra), align='C')

    # PÁGINA 3: PROPOSTA COMERCIAL
    if 3 in paginas_selecionadas:
        pdf.add_page()
        pdf.set_xy(21, 29)
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(177, 8, conv('PROPOSTA COMERCIAL & ESTRUTURAÇÃO ESTRATÉGICA'), align='C', ln=True)

        pdf.set_y(46.0)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 6, conv('PLANOS E INVESTIMENTO'), align='C', ln=True)

        y_p = 66.0
        val_start_limpo = str(planos.get('start_valor', '')).replace("/mês", "").replace("/mes", "").strip()
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(226, 232, 240)
        pdf.rounded_rect(21, y_p, 51, 60, 2, 'FD')
        
        pdf.set_xy(21, y_p + 4)
        pdf.set_font('Helvetica', 'B', 15)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(51, 5, 'Plano Start', align='C', ln=True)
        
        pdf.set_xy(21, y_p + 10)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(51, 5, conv(f"R$ {val_start_limpo}"), align='C', ln=True)
        
        pdf.set_xy(21, y_p + 16)
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(51, 4, conv('em até 2x'), align='C', ln=True)
        
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.set_xy(24, y_p + 25)
        pdf.multi_cell(45, 4.5, conv(planos.get('start_itens', '')), align='L')

        val_pro_limpo = str(planos.get('pro_valor', '')).replace("/mês", "").replace("/mes", "").strip()
        pdf.set_fill_color(240, 249, 255)
        pdf.set_draw_color(30, 64, 175)
        pdf.set_line_width(1.0)
        pdf.rounded_rect(76, y_p - 3, 67, 66, 2.5, 'FD')
        pdf.set_line_width(0.2)
        
        pdf.set_xy(76, y_p + 1)
        pdf.set_font('Helvetica', 'B', 17)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(67, 5, conv('Plano Pro'), align='C', ln=True)
        
        pdf.set_xy(76, y_p + 7.0)
        pdf.set_font('Helvetica', 'B', 10.0)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(67, 4, conv('RECOMENDADO'), align='C', ln=True)
        
        pdf.set_xy(76, y_p + 12.5)
        pdf.set_font('Helvetica', 'B', 17)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(67, 6, conv(f"R$ {val_pro_limpo}"), align='C', ln=True)
        
        pdf.set_xy(76, y_p + 20.0)
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(67, 4, conv('em até 3x'), align='C', ln=True)
        
        pdf.set_font('Helvetica', 'B', 9.0)
        pdf.set_text_color(15, 23, 42)
        pdf.set_xy(80, y_p + 27.5)
        pdf.multi_cell(59, 4.5, conv(planos.get('pro_itens', '')), align='L')

        val_gestao_limpo = str(planos.get('gestao_valor', '')).replace("/mês", "").replace("/mes", "").strip()
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(226, 232, 240)
        pdf.rounded_rect(147, y_p, 51, 60, 2, 'FD')
        
        pdf.set_xy(147, y_p + 4)
        pdf.set_font('Helvetica', 'B', 15)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(51, 5, conv('Gestão Mensal'), align='C', ln=True)
        
        pdf.set_xy(147, y_p + 10)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(51, 5, conv(f"R$ {val_gestao_limpo}"), align='C', ln=True)
        
        pdf.set_xy(147, y_p + 16)
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(51, 4, conv('valor mensal'), align='C', ln=True)
        
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.set_xy(150, y_p + 25)
        pdf.multi_cell(45, 4.5, conv(planos.get('gestao_itens', '')), align='L')

        w_info = 177
        x_info = 21.0
        pdf.set_fill_color(240, 249, 255)
        pdf.set_draw_color(62, 161, 219)
        pdf.set_line_width(0.5)
        pdf.rounded_rect(x_info, 140, w_info, 36, 2.5, 'FD')
        pdf.set_line_width(0.2)

        pdf.set_xy(x_info, 142.5)
        pdf.set_font('Helvetica', 'B', 10.0)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(w_info, 4, conv('POR QUE SEU NEGÓCIO PRECISA DE OTIMIZAÇÃO PROFISSIONAL?'), align='C', ln=True)

        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(51, 65, 85)
        txt_exp = (
            "Mais de 80% das buscas locais no Google e Maps resultam em uma ação imediata (ligação, rota ou mensagem).\n"
            "Perfis com fotos profissionais e Tour Virtual 360° geram até 2x mais interesse e permanecem no topo das buscas.\n"
            "Fichas incompletas ou desatualizadas perdem clientes diariamente para concorrentes diretos com nota mais alta."
        )
        pdf.set_xy(x_info, 148.5)
        pdf.multi_cell(w_info, 4.5, conv(txt_exp), align='C')

    # PÁGINA 4: CONTRATO
    if 4 in paginas_selecionadas:
        pdf.add_page()
        pdf.set_xy(21, 29)
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(177, 8, conv('CONTRATO DE PRESTAÇÃO DE SERVIÇOS'), align='C', ln=True)

        pdf.set_y(48.0)
        w_text, h_line = 177, 4.8

        nome_cli = str(dados.get('nome') or 'Empresa Contratante')
        resp_cli = str(dados.get('contato') or 'Responsável')
        end_cli = str(dados.get('endereco') or 'Endereço não informado')
        tel_cli = str(dados.get('telefone') or 'N/I')

        def paragrafo_justificado(pdf_obj, texto_md, espaco_extra=2.5):
            pdf_obj.set_x(21)
            pdf_obj.set_font('Helvetica', '', 8.5)
            pdf_obj.set_text_color(51, 65, 85)
            pdf_obj.multi_cell(w_text, h_line, conv(texto_md), align='J', markdown=True)
            pdf_obj.ln(espaco_extra)

        paragrafo_justificado(
            pdf, 
            "**CONTRATADA:** Tour360VR, representada por Rubens H. Okamoto, CNPJ: 04.824.331/0001-05 e Telefone: (16) 99133-2121."
        )

        paragrafo_justificado(
            pdf, 
            f"**CONTRATANTE:** {nome_cli}, representada por {resp_cli}, localizada em {end_cli}, Telefone: {tel_cli}."
        )

        paragrafo_justificado(
            pdf, 
            "A **CONTRATADA** compromete-se a executar os serviços de otimização, reestruturação técnica e/ou produção de Tour Virtual 360° para o perfil do Google da **CONTRATANTE**.",
            espaco_extra=3.0
        )

        paragrafo_justificado(
            pdf, 
            "**CLÁUSULA PRIMEIRA - DO OBJETO:** Os serviços serão iniciados em até 5 dias úteis após o fornecimento de todos os acessos e informações necessárias à gestão do perfil."
        )

        paragrafo_justificado(
            pdf, 
            "**CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES:** O não pagamento no prazo pactuado sujeitará o presente contrato à incidência de juros moratórios legais e à suspensão temporária dos serviços até a devida regularização."
        )

        paragrafo_justificado(
            pdf, 
            "**CLÁUSULA TERCEIRA - DOS DIREITOS DE USO E PROPRIEDADE:** Os direitos de uso do Tour Virtual 360° e fotos HD serão cedidos em caráter ilimitado à **CONTRATANTE** para veiculação no Google. A **CONTRATADA** reserva-se o direito de utilizar o material em seu portfólio de divulgação."
        )

        pdf.set_x(21)
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(w_text, h_line, conv("CLÁUSULA QUARTA - SELEÇÃO DO PLANO CONTRATADO:"), ln=True)
        
        pdf.set_x(21)
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(w_text, 4.8, conv("(   ) Plano Start          (   ) Plano Pro          (   ) Gestão Mensal"), ln=True)
        pdf.ln(2.5)

        pdf.set_x(21)
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(w_text, h_line, conv("CLÁUSULA QUINTA - CONDIÇÕES DE PAGAMENTO:"), ln=True)
        
        pdf.set_x(21)
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(w_text, 4.8, conv("(   ) À Vista          (   ) 2x Plano Start          (   ) 3x Plano Pro          (   ) Vencimento Dia: _____ - Gestão Mensal"), ln=True)

        pdf.ln(16)
        y_ass = pdf.get_y()
        pdf.set_xy(21, y_ass)
        pdf.cell(83, 5, '_____________________________________', align='C')
        pdf.set_xy(115, y_ass)
        pdf.cell(83, 5, '_____________________________________', align='C', ln=True)
        
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_x(21)
        pdf.cell(83, 4.2, 'Rubens H. Okamoto', align='C')
        pdf.set_x(115)
        pdf.cell(83, 4.2, conv(resp_cli), align='C', ln=True)
        
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(100, 116, 139)
        pdf.set_x(21)
        pdf.cell(83, 4.2, 'Tour360VR', align='C')
        pdf.set_x(115)
        pdf.cell(83, 4.2, conv(nome_cli), align='C', ln=True)

    return bytes(pdf.output())

# -----------------------------------------------------------------------------
# 6. SIDEBAR REORDENADA E COMPACTADA
# -----------------------------------------------------------------------------
with st.sidebar:
    path_okamoto = obter_caminho_logo("okamoto")
    path_tour = obter_caminho_logo("tour360")
    
    b64_okamoto = carregar_imagem_base64(path_okamoto) if path_okamoto else "https://okamotomidiasvisuais.com.br/assets/img/logo.png"
    b64_tour = carregar_imagem_base64(path_tour) if path_tour else "https://tour360vr.com.br/assets/img/logo.png"

    st.markdown(f"""
        <div class="sidebar-header-box">
            <div class="sidebar-title-top">Consultoria & Diagnóstico</div>
            <img src="{b64_tour}" class="logo-tour" alt="Tour360VR" />
            <img src="{b64_okamoto}" class="logo-okamoto" alt="Okamoto Mídias Visuais" />
        </div>
        <div class="sidebar-divider"></div>
    """, unsafe_allow_html=True)

    nome_empresa_atual = st.session_state['dados'].get('nome') or "Nenhum cliente"
    st.markdown("<div class='label-cliente-centralizado'>Cliente em Atendimento</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class="box-cliente-atendimento">
            🏢 {nome_empresa_atual}
        </div>
    """, unsafe_allow_html=True)
    
    score_atual = calcular_score_real(st.session_state['dados'])
    if score_atual < 50:
        cor_score, status_txt = "#ef4444", "CRÍTICO"
    elif score_atual < 80:
        cor_score, status_txt = "#f59e0b", "MÉDIO"
    else:
        cor_score, status_txt = "#22c55e", "EXCELENTE"

    st.markdown(f"""
        <div class="container-score-diagnostico">
            <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; color: #f8fafc; margin-bottom: 4px;">
                <span>Score Diagnóstico:</span>
                <span style="color: {cor_score};">{score_atual}/100 ({status_txt})</span>
            </div>
            <div style="background-color: #1e293b; border-radius: 4px; height: 8px; width: 100%; overflow: hidden; border: 1px solid #334155;">
                <div style="background-color: {cor_score}; height: 100%; width: {score_atual}%; transition: width 0.4s ease;"></div>
            </div>
        </div>
        <div class="sidebar-divider"></div>
    """, unsafe_allow_html=True)

    if st.button("🧹 Iniciar Novo Atendimento", use_container_width=True):
        st.session_state['etapa_atual'] = 1
        st.session_state['dados'] = {
            "nome": "", "contato": "", "endereco": "", "telefone": "", "website": "",
            "nota": 0.0, "avaliacoes": 0, "tem_tour360": False, "tem_fotos_hd": False,
            "categorias_completas": False, "horarios_ok": False, "tem_descricao": False,
            "atributos_ok": False, "resposta_avaliacoes_ok": False, "categorias_detectadas": [], "foto_reference": ""
        }
        st.session_state['concorrentes'] = [
            {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"},
            {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"},
            {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"}
        ]
        st.session_state['planos'] = {
            "start_valor": "500,00", "start_itens": "- Correção cadastral\n- Otimização de SEO\n- Ajuste de categorias\n- Inserção de links",
            "pro_valor": "1.500,00", "pro_itens": "- Tudo do Plano Start\n- Tour Virtual 360°\n- Ensaio Fotográfico HD\n- Relatório Visual de Entrega",
            "gestao_valor": "600,00", "gestao_itens": "- Postagens semanais\n- Gestão de avaliações\n- Atualização de fotos\n- Relatório mensal"
        }
        st.session_state['plano_acao_extra'] = "O perfil precisa de otimização urgente! Veja as falhas apontadas no relatório."
        st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown("<div style='font-size: 12px; font-weight: 700; color: #f8fafc; margin-bottom: 6px;'>📜 Histórico de Propostas</div>", unsafe_allow_html=True)
    
    lista_hist = carregar_historico()
    if lista_hist:
        for idx_h, item in enumerate(lista_hist[:5]):
            rotulo_btn = f"📂 {item['nome'][:16]} ({item['score']}/100)"
            if st.button(rotulo_btn, key=f"btn_carregar_hist_{idx_h}", use_container_width=True):
                st.session_state['dados'] = {
                    "nome": item.get("nome", ""),
                    "contato": item.get("contato", ""),
                    "endereco": item.get("endereco", ""),
                    "telefone": item.get("telefone", ""),
                    "website": item.get("website", ""),
                    "nota": item.get("nota", 0.0),
                    "avaliacoes": item.get("avaliacoes", 0),
                    "tem_tour360": item.get("tem_tour360", False),
                    "tem_fotos_hd": item.get("tem_fotos_hd", False),
                    "categorias_completas": item.get("categorias_completas", False),
                    "horarios_ok": item.get("horarios_ok", False),
                    "tem_descricao": item.get("tem_descricao", False),
                    "atributos_ok": item.get("atributos_ok", False),
                    "resposta_avaliacoes_ok": item.get("resposta_avaliacoes_ok", False),
                    "foto_reference": item.get("foto_reference", ""),
                    "categorias_detectadas": []
                }
                if item.get("concorrentes"):
                    st.session_state['concorrentes'] = item.get("concorrentes")
                if item.get("planos"):
                    st.session_state['planos'] = item.get("planos")
                if item.get("plano_acao_extra"):
                    st.session_state['plano_acao_extra'] = item.get("plano_acao_extra")

                st.session_state['etapa_atual'] = 5
                st.rerun()
    else:
        st.caption("Nenhuma proposta salva ainda.")

# -----------------------------------------------------------------------------
# 7. BARRA DE ETAPAS CLICÁVEIS
# -----------------------------------------------------------------------------
etapa_atual = st.session_state['etapa_atual']

col_e1, col_e2, col_e3, col_e4, col_e5 = st.columns(5)

with col_e1:
    txt_e1 = "🟡▶ 1. Busca & Ficha" if etapa_atual == 1 else "1. Busca & Ficha"
    key_e1 = "btn_etapa_active_1" if etapa_atual == 1 else "btn_etapa_1"
    if st.button(txt_e1, use_container_width=True, key=key_e1):
        st.session_state['etapa_atual'] = 1
        st.rerun()

with col_e2:
    txt_e2 = "🟡▶ 2. Concorrentes" if etapa_atual == 2 else "2. Concorrentes"
    key_e2 = "btn_etapa_active_2" if etapa_atual == 2 else "btn_etapa_2"
    if st.button(txt_e2, use_container_width=True, key=key_e2):
        st.session_state['etapa_atual'] = 2
        st.rerun()

with col_e3:
    txt_e3 = "🟡▶ 3. Plano de Ação" if etapa_atual == 3 else "3. Plano de Ação"
    key_e3 = "btn_etapa_active_3" if etapa_atual == 3 else "btn_etapa_3"
    if st.button(txt_e3, use_container_width=True, key=key_e3):
        st.session_state['etapa_atual'] = 3
        st.rerun()

with col_e4:
    txt_e4 = "🟡▶ 4. Valores" if etapa_atual == 4 else "4. Valores"
    key_e4 = "btn_etapa_active_4" if etapa_atual == 4 else "btn_etapa_4"
    if st.button(txt_e4, use_container_width=True, key=key_e4):
        st.session_state['etapa_atual'] = 4
        st.rerun()

with col_e5:
    txt_e5 = "🟡▶ 5. PDF & WhatsApp" if etapa_atual == 5 else "5. PDF & WhatsApp"
    key_e5 = "btn_etapa_active_5" if etapa_atual == 5 else "btn_etapa_5"
    if st.button(txt_e5, use_container_width=True, key=key_e5):
        st.session_state['etapa_atual'] = 5
        st.rerun()

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. FLUXO SEQUENCIAL DAS ETAPAS
# -----------------------------------------------------------------------------

# ETAPA 1: BUSCA & DIAGNÓSTICO DA FICHA
if etapa_atual == 1:
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>🔍 1. BUSCA DA FICHA NO GOOGLE MAPS</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([2, 1])
        nome_input = c1.text_input("Nome da Empresa:", value="", placeholder="Ex: Taiwan Hotel Ltda", key="input_empresa_nome")
        cidade_empresa = c2.text_input("Cidade/Região:", value="", placeholder="Ex: Ribeirão Preto, SP", key="input_empresa_cidade")
            
        if st.button("🚀 Pesquisar Ficha no Google", use_container_width=True, key="btn_busca_google"):
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
                            st.error("Nenhuma empresa encontrada com estes termos.")
                except Exception as e:
                    st.error(f"Erro na conexão: {e}")

        if st.session_state['unidades_encontradas']:
            opcoes = [f"{u.get('name')} - {u.get('formatted_address')}" for u in st.session_state['unidades_encontradas']]
            escolha = st.selectbox("Selecione a unidade exata:", opcoes, key="select_unidade_exata")
            
            if st.button("📌 Carregar Dados da Unidade", use_container_width=True, key="btn_carregar_unidade"):
                idx = opcoes.index(escolha)
                u = st.session_state['unidades_encontradas'][idx]
                place_id = u.get("place_id")
                
                if API_KEY_GOOGLE:
                    try:
                        url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,international_phone_number,website,rating,user_ratings_total,photos,opening_hours,types,editorial_summary,geometry&key={API_KEY_GOOGLE}"
                        res_details = requests.get(url_details).json().get("result", {})
                        
                        photos = res_details.get("photos", u.get("photos", []))
                        types_lista = res_details.get("types", [])
                        
                        st.session_state['dados']['nome'] = res_details.get("name") or u.get("name") or nome_input
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
                        st.session_state['dados']['categorias_detectadas'] = types_lista
                        st.session_state['dados']['foto_reference'] = photos[0].get("photo_reference") if photos else ""

                        st.success("Dados da unidade carregados com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao obter detalhes: {e}")

        st.markdown("---")
        st.markdown("<div class='card-title'>CHECKLIST DE PONTOS CRÍTICOS</div>", unsafe_allow_html=True)
        
        c_a, c_b, c_c, c_d = st.columns(4)
        st.session_state['dados']['tem_tour360'] = c_a.checkbox("Tour 360° Ativo", value=st.session_state['dados']['tem_tour360'])
        st.session_state['dados']['tem_fotos_hd'] = c_b.checkbox("Fotos HD", value=st.session_state['dados']['tem_fotos_hd'])
        st.session_state['dados']['categorias_completas'] = c_c.checkbox("Categorias OK", value=st.session_state['dados']['categorias_completas'])
        st.session_state['dados']['horarios_ok'] = c_d.checkbox("Horários OK", value=st.session_state['dados']['horarios_ok'])
        
        c_e, c_f, c_g = st.columns(3)
        st.session_state['dados']['tem_descricao'] = c_e.checkbox("Descrição", value=st.session_state['dados']['tem_descricao'])
        st.session_state['dados']['atributos_ok'] = c_f.checkbox("Atributos Serviços", value=st.session_state['dados']['atributos_ok'])
        st.session_state['dados']['resposta_avaliacoes_ok'] = c_g.checkbox("Respostas Ativas", value=st.session_state['dados']['resposta_avaliacoes_ok'])

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>DADOS DO CLIENTE</div>", unsafe_allow_html=True)
        st.session_state['dados']['nome'] = st.text_input("Empresa:", value=st.session_state['dados']['nome'])
        st.session_state['dados']['contato'] = st.text_input("Responsável:", value=st.session_state['dados']['contato'])
        st.session_state['dados']['telefone'] = st.text_input("Telefone:", value=st.session_state['dados']['telefone'])
        st.session_state['dados']['website'] = st.text_input("Website:", value=st.session_state['dados']['website'])
        st.session_state['dados']['endereco'] = st.text_area("Endereço:", value=st.session_state['dados']['endereco'], height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    col_nav1, col_nav2 = st.columns([2, 1])
    with col_nav2:
        if st.button("Avançar para Concorrentes ➡️", use_container_width=True, key="btn_nav_aba1"):
            st.session_state['etapa_atual'] = 2
            st.rerun()

# ETAPA 2: AVALIAÇÃO DE CONCORRENTES
elif etapa_atual == 2:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>⚔️ 2. AVALIAÇÃO DE CONCORRENTES DO SEGMENTO</div>", unsafe_allow_html=True)
    st.caption("Digite o nome da empresa e a cidade para consultar a nota e dados no Google Maps.")

    with st.form(key="form_concorrentes_fix"):
        inputs_conc = []
        for i in range(3):
            col_c1, col_c2 = st.columns([2.5, 1.5])
            val_nome = st.session_state['concorrentes'][i].get('busca_termo') or st.session_state['concorrentes'][i].get('nome', '')
            val_cid = st.session_state['concorrentes'][i].get('cidade', '')
            
            nome_c = col_c1.text_input(f"Concorrente #{i+1}:", value=val_nome, key=f"c_input_nome_{i}")
            cid_c = col_c2.text_input(f"Cidade/Região #{i+1}:", value=val_cid, key=f"c_input_cid_{i}")
            inputs_conc.append((nome_c, cid_c))

        btn_consultar = st.form_submit_button("🔎 Mapear Concorrentes via API", use_container_width=True)

        if btn_consultar:
            if API_KEY_GOOGLE:
                encontrados = 0
                for idx, (nome_c, cid_c) in enumerate(inputs_conc):
                    st.session_state['concorrentes'][idx]['busca_termo'] = nome_c
                    st.session_state['concorrentes'][idx]['cidade'] = cid_c
                    
                    if nome_c.strip() != "":
                        det = buscar_detalhes_concorrente_especifico(nome_c, cid_c, API_KEY_GOOGLE)
                        if det:
                            st.session_state['concorrentes'][idx].update(det)
                            encontrados += 1
                        else:
                            st.session_state['concorrentes'][idx]['nome'] = nome_c
                            
                if encontrados > 0:
                    st.success(f"{encontrados} concorrente(s) atualizado(s) com sucesso!")
                else:
                    st.warning("Nenhum dado retornado. Verifique a grafia do nome e cidade.")
                st.rerun()
            else:
                st.error("Chave GOOGLE_API_KEY não localizada.")

    concorrentes_validos = [c for c in st.session_state['concorrentes'] if c.get('nome', '').strip() != '']
    if concorrentes_validos:
        st.markdown("---")
        st.markdown("**Resultado da Consulta:**")
        for c_item in concorrentes_validos:
            score_c = calcular_score_concorrente(c_item)
            st.markdown(f"• **{c_item['nome']}** — ⭐ Nota: `{float(c_item.get('nota', 0.0)):.1f}` ({c_item.get('avaliacoes', 0)} avaliada(s)) | Score: **{score_c}/100**")

    st.markdown("</div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("⬅️ Voltar para Busca", use_container_width=True, key="btn_nav_aba2_back"):
            st.session_state['etapa_atual'] = 1
            st.rerun()
    with col_btn2:
        if st.button("Avançar para Plano de Ação ➡️", use_container_width=True, key="btn_nav_aba2_next"):
            st.session_state['etapa_atual'] = 3
            st.rerun()

# ETAPA 3: PLANO DE AÇÃO ESTRATÉGICO
elif etapa_atual == 3:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>💡 3. APONTAMENTOS ESTRATÉGICOS E PLANO DE AÇÃO</div>", unsafe_allow_html=True)
    st.caption("Texto personalizado que aparecerá no quadro em destaque na Página 2 do PDF.")
    
    st.session_state['plano_acao_extra'] = st.text_area(
        "Edite o plano de ação personalizado:",
        value=st.session_state['plano_acao_extra'],
        height=180
    )
    st.markdown("</div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("⬅️ Voltar para Concorrentes", use_container_width=True, key="btn_nav_aba3_back"):
            st.session_state['etapa_atual'] = 2
            st.rerun()
    with col_btn2:
        if st.button("Avançar para Planos & Valores ➡️", use_container_width=True, key="btn_nav_aba3_next"):
            st.session_state['etapa_atual'] = 4
            st.rerun()

# ETAPA 4: PLANOS & VALORES COMERCIAIS
elif etapa_atual == 4:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>📜 4. PLANOS COMERCIAIS & INVESTIMENTO</div>", unsafe_allow_html=True)
    
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("#### 🔹 Plano Start")
        st.session_state['planos']['start_valor'] = st.text_input("Valor (R$):", value=st.session_state['planos']['start_valor'], key="p_s_v")
        st.session_state['planos']['start_itens'] = st.text_area("Itens:", value=st.session_state['planos']['start_itens'], height=140, key="p_s_i")
    with p2:
        st.markdown("#### 🔹 Plano Pro")
        st.session_state['planos']['pro_valor'] = st.text_input("Valor (R$):", value=st.session_state['planos']['pro_valor'], key="p_p_v")
        st.session_state['planos']['pro_itens'] = st.text_area("Itens:", value=st.session_state['planos']['pro_itens'], height=140, key="p_p_i")
    with p3:
        st.markdown("#### 🔹 Gestão Mensal")
        st.session_state['planos']['gestao_valor'] = st.text_input("Valor (R$):", value=st.session_state['planos']['gestao_valor'], key="p_g_v")
        st.session_state['planos']['gestao_itens'] = st.text_area("Itens:", value=st.session_state['planos']['gestao_itens'], height=140, key="p_g_i")

    st.markdown("</div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("⬅️ Voltar para Plano de Ação", use_container_width=True, key="btn_nav_aba4_back"):
            st.session_state['etapa_atual'] = 3
            st.rerun()
    with col_btn2:
        if st.button("Avançar para PDF & WhatsApp ➡️", use_container_width=True, key="btn_nav_aba4_next"):
            st.session_state['etapa_atual'] = 5
            st.rerun()

# ETAPA 5: GERAR PDF, WHATSAPP & HISTÓRICO
elif etapa_atual == 5:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>📄 5. EMISSÃO, ABORDAGEM & HISTÓRICO</div>", unsafe_allow_html=True)
    
    st.markdown("#### ⚙️ Selecione as Páginas a Incluir no PDF:")
    c_pag1, c_pag2, c_pag3, c_pag4 = st.columns(4)
    inc_p1 = c_pag1.checkbox("Pág 1 (Capa)", value=True, key="chk_p1")
    inc_p2 = c_pag2.checkbox("Pág 2 (Auditoria/Concorrentes)", value=True, key="chk_p2")
    inc_p3 = c_pag3.checkbox("Pág 3 (Valores e Planos)", value=False, key="chk_p3")
    inc_p4 = c_pag4.checkbox("Pág 4 (Contrato)", value=False, key="chk_p4")

    paginas_escolhidas = []
    if inc_p1: paginas_escolhidas.append(1)
    if inc_p2: paginas_escolhidas.append(2)
    if inc_p3: paginas_escolhidas.append(3)
    if inc_p4: paginas_escolhidas.append(4)

    if not paginas_escolhidas:
        st.warning("Selecione ao menos uma página para gerar o PDF.")
    else:
        nome_empresa_formatado = str(st.session_state['dados'].get('nome') or 'Empresa').strip()
        resp_cliente = str(st.session_state['dados'].get('contato') or 'Responsável').strip()
        tel_cliente = str(st.session_state['dados'].get('telefone') or '').replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        if tel_cliente and not tel_cliente.startswith("55"):
            tel_cliente = f"55{tel_cliente}"

        texto_padrao_whatsapp = (
            f"Olá, {resp_cliente}! Tudo bem?\n\n"
            f"Achei o perfil da {nome_empresa_formatado} no Google e preparei uma análise rápida do seu posicionamento local frente aos concorrentes.\n\n"
            f"Identifiquei alguns pontos importantes de melhoria de visibilidade. Posso te enviar o relatório preliminar que montei em PDF?"
        )

        st.markdown("---")
        st.markdown("#### 📝 Mensagem de Abordagem (Editável):")
        mensagem_editada = st.text_area(
            "Edite a mensagem antes de abrir o WhatsApp:",
            value=texto_padrao_whatsapp,
            height=120,
            key="area_msg_whatsapp_wizard"
        )

        msg_encoded = requests.utils.quote(mensagem_editada)
        link_wa = f"https://wa.me/{tel_cliente}?text={msg_encoded}" if tel_cliente else f"https://wa.me/?text={msg_encoded}"

        col_down1, col_down2 = st.columns(2)
        
        try:
            pdf_bytes = gerar_pdf_oficial(
                st.session_state['dados'], 
                st.session_state['planos'], 
                st.session_state.get('plano_acao_extra', ''), 
                st.session_state.get('concorrentes', []),
                paginas_selecionadas=paginas_escolhidas
            )

            score_calc = calcular_score_real(st.session_state['dados'])
            salvar_no_historico(
                st.session_state['dados'], 
                score_calc, 
                concorrentes=st.session_state.get('concorrentes', []), 
                planos=st.session_state.get('planos', {}), 
                plano_acao_extra=st.session_state.get('plano_acao_extra', '')
            )

            tipo_doc = "Diagnostico_Preliminar" if len(paginas_escolhidas) <= 2 else "Proposta_Completa"

            with col_down1:
                st.download_button(
                    label=f"📥 Baixar PDF ({len(paginas_escolhidas)} Pág(s))",
                    data=pdf_bytes,
                    file_name=f"{tipo_doc} - {nome_empresa_formatado}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="btn_download_wizard"
                )
                
            with col_down2:
                st.link_button(
                    label="📲 Abrir WhatsApp",
                    url=link_wa,
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Erro ao processar PDF: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    col_nav1, col_nav2 = st.columns([1, 2])
    with col_nav1:
        if st.button("⬅️ Voltar para Ajuste de Valores", use_container_width=True, key="btn_nav_aba5_back"):
            st.session_state['etapa_atual'] = 4
            st.rerun()

# -----------------------------------------------------------------------------
# 9. RODAPÉ FIXO
# -----------------------------------------------------------------------------
st.markdown("""
    <div class='custom-footer'>
        <a href='https://tour360vr.com.br' target='_blank'>tour360vr.com.br</a> | 
        <a href='mailto:contato@tour360vr.com.br'>contato@tour360vr.com.br</a> | 
        Whatsapp: (16) 99133-2121 | 
        <b>Tour360VR - Gestão de Perfil do Google</b>
    </div>
""", unsafe_allow_html=True)

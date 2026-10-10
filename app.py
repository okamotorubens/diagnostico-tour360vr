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
    /* Oculta elementos vazios gerados pelo Streamlit */
    div.element-container:has(div.stMarkdown:empty),
    div.stMarkdown:empty,
    .element-container:empty {
        display: none !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
    }

    /* Oculta navegação automática nativa do Streamlit */
    [data-testid="stSidebarNav"] { display: none !important; }

    .stApp { 
        background-color: #0b0f19 !important; 
        color: #f1f5f9 !important; 
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    }
    
    [data-testid="stSidebar"] { 
        background-color: #111827 !important; 
        border-right: 1px solid #1f2937 !important; 
    }
    
    [data-testid="stSidebarUserContent"] {
        padding-top: 1.0rem !important;
        padding-bottom: 1.0rem !important;
        padding-left: 1.0rem !important;
        padding-right: 1.0rem !important;
    }

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
        border: 1px solid #e2e8f0; 
        border-radius: 8px; 
        padding: 8px 10px; 
        text-align: center; 
        color: #ffffff; 
        font-weight: 700; 
        font-size: 13.5px;
        margin-bottom: 12px !important;
    }

    .container-score-diagnostico {
        margin-bottom: 12px !important;
    }

    /* QUADROS DE CONTEÚDO (Borda Branca Suave) */
    .dashboard-card { 
        background-color: #1e293b !important; 
        border: 1.5px solid #cbd5e1 !important; 
        border-radius: 14px; 
        padding: 18px; 
        margin-top: 10px !important;
        margin-bottom: 15px !important; 
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.4);
    }

    /* TÍTULO DOS QUADROS CENTRALIZADO (Branco) */
    .card-title { 
        font-size: 15px; 
        font-weight: 700; 
        color: #ffffff; 
        margin-bottom: 14px; 
        text-transform: uppercase; 
        letter-spacing: 0.8px; 
        line-height: 1.3;
        text-align: center !important;
    }
    
    /* BOTÕES SECUNDÁRIOS */
    .stApp [data-testid="stBaseButton-secondary"] {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 9px 12px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
    }

    .stApp [data-testid="stBaseButton-secondary"]:hover {
        background-color: #334155 !important;
        color: #ffffff !important;
        border-color: #ffffff !important;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.3) !important;
    }

    /* ETAPA ATIVA */
    .stApp [data-testid="stBaseButton-primary"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        font-size: 13.5px !important;
        padding: 9px 12px !important;
        box-shadow: 0 0 18px rgba(255, 255, 255, 0.85) !important;
    }

    .stApp [data-testid="stBaseButton-primary"]:hover {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border-color: #ffffff !important;
    }

    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] { 
        background-color: #334155 !important; 
        color: #ffffff !important; 
        border: 1px solid #cbd5e1 !important; 
    }

    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover { 
        background-color: #475569 !important; 
        box-shadow: 0 4px 10px rgba(255, 255, 255, 0.2) !important;
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
    .custom-footer a { color: #ffffff; text-decoration: none; }
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
        "pro_valor": "1.500,00", "pro_itens": "- Tudo do Plano Start\n- Tour Virtual 360°\n- Ensaio Fotográfico\n- Relatório Visual de Entrega",
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
        self.exibir_numeracao = kwargs.pop('exibir_numeracao', False)
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
            if self.exibir_numeracao:
                self.set_x(170)
                self.cell(28, 5, f'Página {self.page_no()} de 4', align='R')

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
    exibir_num = len(paginas_selecionadas) == 4
    
    pdf = PDFTour360Oficial(capa_incluida=capa_presente, exibir_numeracao=exibir_num)
    pdf.set_margins(21, 12, 12)
    pdf.set_auto_page_break(auto=False)

    # PÁGINA 1: CAPA
    if 1 in paginas_selecionadas:
        pdf.add_page()
        caminho_logo = obter_caminho_logo("tour360")
        if caminho_

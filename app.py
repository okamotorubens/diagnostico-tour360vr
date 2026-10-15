import os
import re
import io
import base64
import requests
import smtplib
import streamlit as st
from datetime import datetime
from fpdf import FPDF
from PIL import Image

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA (OBRIGATORIAMENTE O PRIMEIRA COMANDO STREAMLIT)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Consultoria & Diagnóstico - Tour360VR",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. ESTILOS CSS CUSTOMIZADOS (SEGURO)
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
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

    .dashboard-card { 
        background-color: #1e293b !important; 
        border: 1.5px solid #cbd5e1 !important; 
        border-radius: 14px; 
        padding: 18px; 
        margin-top: 10px !important;
        margin-bottom: 15px !important; 
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.4);
    }

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

# -----------------------------------------------------------------------------
# 3. CREDENCIAIS & CHAVES (TRATAMENTO SEGURO DE ERROS)
# -----------------------------------------------------------------------------
API_KEY_GOOGLE = ""
try:
    if "GOOGLE_API_KEY" in st.secrets:
        API_KEY_GOOGLE = st.secrets["GOOGLE_API_KEY"]
    elif "GOOGLE_PLACES_API_KEY" in st.secrets:
        API_KEY_GOOGLE = st.secrets["GOOGLE_PLACES_API_KEY"]
    else:
        API_KEY_GOOGLE = os.environ.get("GOOGLE_API_KEY", "")
except Exception:
    API_KEY_GOOGLE = os.environ.get("GOOGLE_API_KEY", "")

SMTP_SERVER = "smtp.tour360vr.com.br"
SMTP_PORT_SSL = 465
SMTP_USER = "contato@tour360vr.com.br"
SMTP_PASS = "Kakaroto@2026"

# -----------------------------------------------------------------------------
# 4. FUNÇÕES UTILITÁRIAS
# -----------------------------------------------------------------------------
def conv(texto):
    if not texto: return ""
    limpo = str(texto).replace("★", "*").replace("•", "- ").replace("✓", "[OK] ")
    return limpo.encode('latin-1', 'replace').decode('latin-1')

def carregar_imagem_base64(caminho):
    if caminho and os.path.exists(caminho):
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
    if dados.get("website") in ["Não possui", "", None]: score -= 15
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
        caminhos = ['assets/logo_okamoto.png', 'assets/logo_okamoto_midias_visuais.png', 'logo_okamoto.png']
        url_oficial = "https://okamotomidiasvisuais.com.br/assets/img/logo.png"
    else:
        caminhos = ['assets/logo_tour_transparente.png', 'assets/logo_tour.png', 'logo_tour_transparente.png']
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

def obter_imagem_mapa_google(dados, api_key, largura=700, altura=320, zoom=14):
    if not api_key: return None
    lat, lng = dados.get("lat"), dados.get("lng")
    endereco = dados.get("endereco")
    
    if lat and lng:
        center_param = f"{lat},{lng}"
    elif endereco:
        center_param = requests.utils.quote(str(endereco))
    else:
        return None

    url_static_map = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"center={center_param}&zoom={zoom}&size={largura}x{altura}"
        f"&scale=2&maptype=roadmap"
        f"&markers=color:red%7Csize:mid%7C{center_param}"
        f"&key={api_key}"
    )
    
    try:
        resp = requests.get(url_static_map, timeout=5)
        if resp.status_code == 200:
            return io.BytesIO(resp.content)
    except Exception: pass
    return None

def buscar_detalhes_concorrente_especifico(nome_concorrente, cidade, api_key):
    if not nome_concorrente or not api_key: return None
    try:
        termo = f"{nome_concorrente}, {cidade}" if cidade else nome_concorrente
        url_search = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={requests.utils.quote(termo)}&key={api_key}"
        res = requests.get(url_search, timeout=5).json()
        if res.get("status") == "OK" and res.get("results"):
            item = res["results"][0]
            place_id = item.get("place_id")
            url_det = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=website,editorial_summary,opening_hours,photos,types&key={api_key}"
            res_det = requests.get(url_det, timeout=5).json().get("result", {})
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

def enviar_lead_zoho_bigin(dados, score):
    url_bigin = "https://bigin.zoho.com/crm/WebToContactForm"
    empresa_nome = dados.get("nome", "Empresa Não Informada").strip()
    responsavel = dados.get("contato", "").strip()
    telefone = dados.get("telefone", "").strip()
    endereco = dados.get("endereco", "").strip()
    website = dados.get("website", "").strip()

    if not responsavel or responsavel.lower() in ["gerente responsável", "responsável", "gerente", ""]:
        primeiro_nome = empresa_nome
        sobrenome = "[Diagnóstico]"
    else:
        partes_nome = responsavel.split(" ", 1)
        primeiro_nome = partes_nome[0]
        sobrenome = (partes_nome[1] + " [Diagnóstico]") if len(partes_nome) > 1 else "[Diagnóstico]"

    payload = {
        'xnQsjsdp': '15d54e8d1dfa724381be9ad892936abd18de3deadc2763d67c0dd5f939138a91',
        'zc_gad': '',
        'xmIwtLD': '7bf1ddf18cd4b2e66bc992eae51f7e88125018eba8806dd498fb7e87e015ca5085bf99ead8aa16f7a6ff561d393a37ef',
        'actionType': 'Q29udGFjdHM=',
        'rmsg': 'true',
        'returnURL': 'null',
        'First Name': primeiro_nome,
        'Last Name': sobrenome,
        'Social Lead ID': 'Sistema de Diagnóstico Tour360VR',
        'Email': 'contato@tour360vr.com.br',
        'Accounts.Account Name': empresa_nome,
        'Phone': telefone,
        'SITE': website if website != "Não possui" else "",
        'CONTACTCF6': f"{score}/100",
        'Description': f"ORIGEM: Sistema de Diagnóstico Tour360VR\nEmpresa: {empresa_nome}\nEndereço: {endereco}\nPontuação Google: {score}/100"
    }
    try:
        res = requests.post(url_bigin, data=payload, timeout=8)
        return res.status_code == 200
    except Exception: return False

def enviar_email_admin_com_pdf(dados, score, pdf_bytes, filename_pdf="Diagnostico.pdf"):
    try:
        empresa_nome = dados.get("nome", "Empresa")
        responsavel = dados.get("contato", "Responsável")
        telefone = dados.get("telefone", "N/I")
        endereco = dados.get("endereco", "N/I")

        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT_SSL, timeout=12)
        server.login(SMTP_USER, SMTP_PASS)

        msg_admin = MIMEMultipart('mixed')
        msg_admin['From'] = f"Tour360VR <{SMTP_USER}>"
        msg_admin['To'] = SMTP_USER
        msg_admin['Subject'] = f"🚀 DIAGNÓSTICO GERADO: {empresa_nome} (Score: {score}/100)"
        
        corpo_admin_html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="font-family: Arial, sans-serif; background-color: #F4F6F9; padding: 15px; margin: 0;">
            <div style="max-width: 580px; background-color: #FFFFFF; padding: 20px; border-radius: 10px; border-top: 5px solid #1565C0; margin: 0 auto;">
                <h2 style="color: #111111; margin-top: 0; font-size: 18px;">Novo Relatório Gerado no Sistema!</h2>
                <hr style="border: 0; border-top: 1px solid #EEEEEE; margin: 12px 0;">
                <p style="font-size: 14px; margin: 4px 0;"><b>Empresa:</b> {empresa_nome}</p>
                <p style="font-size: 14px; margin: 4px 0;"><b>Responsável:</b> {responsavel}</p>
                <p style="font-size: 14px; margin: 4px 0;"><b>Telefone:</b> {telefone}</p>
                <p style="font-size: 14px; margin: 4px 0;"><b>Endereço:</b> {endereco}</p>
                <p style="font-size: 14px; margin: 4px 0;"><b>Pontuação:</b> <span style="font-size: 16px; color: #1565C0; font-weight: bold;">{score} / 100</span></p>
            </div>
        </body>
        </html>
        """
        msg_admin.attach(MIMEText(corpo_admin_html, 'html', 'utf-8'))
        
        if pdf_bytes:
            part_admin = MIMEApplication(pdf_bytes, _subtype="pdf")
            part_admin.add_header('Content-Disposition', 'attachment', filename=filename_pdf)
            msg_admin.attach(part_admin)

        server.send_message(msg_admin)
        server.quit()

        return True, "Enviado com sucesso!"
    except Exception as e:
        return False, f"Falha no envio do e-mail: {str(e)}"

# -----------------------------------------------------------------------------
# 5. ESTADOS PERSISTENTES DA SESSÃO
# -----------------------------------------------------------------------------
if 'etapa_atual' not in st.session_state:
    st.session_state['etapa_atual'] = 1

if 'dados' not in st.session_state:
    st.session_state['dados'] = {
        "nome": "", "contato": "", "endereco": "", "telefone": "", "website": "",
        "nota": 0.0, "avaliacoes": 0, "tem_tour360": False, "tem_fotos_hd": False,
        "categorias_completas": False, "horarios_ok": False, "tem_descricao": False,
        "atributos_ok": False, "resposta_avaliacoes_ok": False, "categorias_detectadas": [], "foto_reference": "",
        "lat": None, "lng": None
    }

if 'concorrentes' not in st.session_state:
    st.session_state['concorrentes'] = [
        {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"},
        {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"},
        {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"}
    ]

if 'planos' not in st.session_state:
    st.session_state['planos'] = {
        "start_valor": "500,00", "start_itens": "Preenchimento completo do perfil\nDescrição profissional com palavras-chave\nCategorias corretas + secundárias\nPadronização de dados: NAP, horários, serviços",
        "pro_valor": "1.500,00", "pro_itens": "Preenchimento completo do perfil\nDescrição profissional com palavras-chave\nCategorias corretas + secundárias\nPadronização de dados: NAP, horários, serviços\nSessão de fotos\nTour Virtual 360°\nFotos 360° para Street View\nIndexação de Fotos & Image SEO AI",
        "gestao_valor": "600,00", "gestao_itens": "Postagens semanais\nGestão de avaliações\nAtualização de fotos\nRelatório mensal\nOtimização Contínua por IA"
    }

TEXTO_PLANO_ACAO_PADRAO = (
    "Ações prioritárias para otimização e diferenciação local:\n"
    "1. Atração Local (SEO): Correção cadastral e otimização das categorias principal e secundárias.\n"
    "2. Segurança & Posicionamento: Frequência de atualização para sinalizar ao Google que o perfil está ativo.\n"
    "3. Confiança & Autoridade: Publicação do Tour Virtual 360° no Street View e fotos em alta resolução.\n"
    "4. Vitrine Imersiva: Padronização do acervo visual do espaço e integração dos canais de contato direto."
)

if 'plano_acao_extra' not in st.session_state:
    st.session_state['plano_acao_extra'] = TEXTO_PLANO_ACAO_PADRAO

if 'unidades_encontradas' not in st.session_state:
    st.session_state['unidades_encontradas'] = []

# -----------------------------------------------------------------------------
# 6. GERADOR PDF
# -----------------------------------------------------------------------------
class PDFTour360Oficial(FPDF):
    def __init__(self, *args, **kwargs):
        self.capa_incluida = kwargs.pop('capa_incluida', True)
        self.exibir_numeracao = kwargs.pop('exibir_numeracao', False)
        self.total_paginas_pdf = kwargs.pop('total_paginas_pdf', 5)
        super().__init__(*args, **kwargs)

    def header(self):
        if self.page_no() == 1 and self.capa_incluida:
            return
        
        caminho_logo = obter_caminho_logo("tour360")
        if caminho_logo:
            try:
                self.image(caminho_logo, 21, 8.0, 11, 11)
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
        self.set_draw_color(226, 232, 240)
        self.line(21, self.get_y(), 198, self.get_y())
        self.set_y(-13)
        self.set_text_color(0, 0, 0)
        
        if self.page_no() == 1 and self.capa_incluida:
            self.set_x(21)
            self.set_font('Helvetica', '', 9.5)
            self.cell(177, 5, conv("Tour360VR  |  (16) 99133-2121  |  Ribeirão Preto - SP  |  tour360vr.com.br"), align='C')
        else:
            self.set_font('Helvetica', '', 8.5)
            self.set_x(35)
            self.cell(45, 5, 'contato@tour360vr.com.br', link='mailto:contato@tour360vr.com.br', align='C')
            self.cell(40, 5, 'tour360vr.com.br', link='https://tour360vr.com.br', align='C')
            self.cell(45, 5, 'WhatsApp: (16) 99133-2121', link='https://wa.me/5516991332121', align='C')
            if self.exibir_numeracao:
                self.set_x(170)
                self.cell(28, 5, f'Página {self.page_no()} de {self.total_paginas_pdf}', align='R')

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

def set_color_safe(pdf_obj, r, g=None, b=None, fn_type='text'):
    try:
        if isinstance(r, (tuple, list)):
            r_v, g_v, b_v = int(r[0]), int(r[1]), int(r[2])
        elif g is not None and b is not None:
            r_v, g_v, b_v = int(r), int(g), int(b)
        else:
            r_v = g_v = b_v = int(r)
    except Exception:
        r_v = g_v = b_v = 0
        
    if fn_type == 'text': pdf_obj.set_text_color(r_v, g_v, b_v)
    elif fn_type == 'fill': pdf_obj.set_fill_color(r_v, g_v, b_v)
    elif fn_type == 'draw': pdf_obj.set_draw_color(r_v, g_v, b_v)

def gerar_pdf_oficial(dados, planos, plano_acao_extra="", concorrentes=[], paginas_selecionadas=[1, 2, 3, 4, 5]):
    score = calcular_score_real(dados)
    capa_presente = 1 in paginas_selecionadas
    tot_pags = len(paginas_selecionadas)
    
    pdf = PDFTour360Oficial(capa_incluida=capa_presente, exibir_numeracao=True, total_paginas_pdf=tot_pags)
    pdf.set_margins(21, 12, 12)
    pdf.set_auto_page_break(auto=False)

    # PÁGINA 1: CAPA
    if 1 in paginas_selecionadas:
        pdf.add_page()
        caminho_logo = obter_caminho_logo("tour360")
        if caminho_logo:
            try: pdf.image(caminho_logo, 90, 15.0, 36, 36)
            except Exception: pass

        pdf.set_y(53.0)
        pdf.ln(8)
        pdf.set_font('Helvetica', 'B', 20)
        set_color_safe(pdf, 30, 64, 175, fn_type='text')
        pdf.cell(0, 8, conv('DIAGNÓSTICO DE PRESENÇA DIGITAL'), align='C', ln=True)
        pdf.ln(1)

        pdf.set_font('Helvetica', 'B', 14)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        pdf.cell(0, 6, conv('GOOGLE MEU NEGÓCIO'), align='C', ln=True)

        pdf.ln(3.5)
        pdf.set_font('Helvetica', '', 10.0)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        pdf.cell(0, 5, conv("Gestão de reputação e imagem online para o segmento no Google Maps"), align='C', ln=True)

        w_capa, x_capa, y_capa, h_capa = 177.0, 21.0, 96.0, 40.0
        set_color_safe(pdf, 248, 250, 252, fn_type='fill')
        set_color_safe(pdf, 203, 213, 225, fn_type='draw')
        pdf.set_line_width(0.3)
        pdf.rounded_rect(x_capa, y_capa, w_capa, h_capa, 3.5, 'FD')

        pdf.set_xy(x_capa + 4.0, y_capa + 4.0)
        pdf.set_font('Helvetica', 'B', 14.0)
        set_color_safe(pdf, 15, 23, 42, fn_type='text') 
        pdf.multi_cell(w_capa - 8.0, 5.5, conv(dados.get('nome') or 'Nome da Empresa'), align='C')

        pdf.ln(2.5)
        pdf.set_font('Helvetica', 'B', 10.5)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        pdf.set_x(x_capa)
        pdf.cell(w_capa, 5.2, conv(f"Preparado para: {dados.get('contato') or 'Responsável'}"), align='C', ln=True)
        
        pdf.set_font('Helvetica', '', 9.5)
        set_color_safe(pdf, 71, 85, 105, fn_type='text')
        pdf.set_x(x_capa)
        pdf.cell(w_capa, 5.0, conv(f"{dados.get('endereco') or 'Endereço não informado'}"), align='C', ln=True)
        
        site_txt = dados.get('website') if dados.get('website') else 'N/I'
        pdf.set_x(x_capa)
        pdf.cell(w_capa, 5.0, conv(f"Telefone: {dados.get('telefone') or 'N/I'}   |   {site_txt}"), align='C', ln=True)

        y_foto, h_container, w_container = 141.0, 90.0, 177.0
        set_color_safe(pdf, 248, 250, 252, fn_type='fill')
        set_color_safe(pdf, 203, 213, 225, fn_type='draw')
        pdf.rounded_rect(x_capa, y_foto, w_container, h_container, 3.0, 'FD')
        pdf.set_xy(x_capa, y_foto + 38)
        pdf.set_font('Helvetica', 'B', 11)
        set_color_safe(pdf, 100, 116, 139, fn_type='text')
        pdf.cell(w_container, 6, conv("[ IMAGEM DA FICHA GOOGLE DO CLIENTE ]"), align='C', ln=True)

        w_alerta, x_alerta, y_alerta, h_alerta = 177.0, 21.0, y_foto + h_container + 6.0, 17.0
        set_color_safe(pdf, 254, 242, 242, fn_type='fill')
        set_color_safe(pdf, 254, 202, 202, fn_type='draw')
        pdf.rounded_rect(x_alerta, y_alerta, w_alerta, h_alerta, 2.5, 'FD')

        pdf.set_xy(x_alerta, y_alerta + 4.0)
        pdf.set_font('Helvetica', 'B', 8.5)
        set_color_safe(pdf, 185, 28, 28, fn_type='text')
        pdf.cell(w_alerta, 4.0, conv(f"SEU PERFIL POSSUI NOTA {dados.get('nota', 0.0):.1f} COM {dados.get('avaliacoes', 0)} AVALIAÇÕES NO GOOGLE."), align='C', ln=True)
        pdf.set_x(x_alerta)
        pdf.cell(w_alerta, 4.0, conv("A OTIMIZAÇÃO E CONTEÚDO 360° SÃO ESSENCIAIS PARA LIDERAR A REGIÃO."), align='C', ln=True)

    # PÁGINA 2: AUDITORIA DETALHADA
    if 2 in paginas_selecionadas:
        pdf.add_page()
        pdf.set_xy(21, 28.0)
        pdf.set_font('Helvetica', 'B', 15)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        pdf.cell(177, 7, conv('AUDITORIA DETALHADA DE PONTOS DE BUSCA'), align='C', ln=True)

        set_color_safe(pdf, 248, 250, 252, fn_type='fill')
        set_color_safe(pdf, 203, 213, 225, fn_type='draw')
        pdf.rounded_rect(21.0, 38.0, 177, 8.5, 2.5, 'FD')
        
        pdf.set_xy(21.0, 39.8)
        pdf.set_font('Helvetica', 'B', 12.0)
        set_color_safe(pdf, 30, 64, 175, fn_type='text')
        pdf.cell(177, 4.8, conv(f"{dados.get('nome') or 'Empresa Analisada'}"), align='C', ln=True)

        # Quadros de Score
        set_color_safe(pdf, 255, 255, 255, fn_type='fill')
        set_color_safe(pdf, 226, 232, 240, fn_type='draw')
        pdf.rounded_rect(21.0, 49.0, 86.0, 20.0, 3.0, 'FD')
        pdf.set_xy(21.0, 51.0)
        pdf.set_font('Helvetica', 'B', 7.8)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        pdf.cell(86.0, 3.0, conv("OTIMIZAÇÃO DO PERFIL"), align='C', ln=True)
        pdf.set_xy(21.0, 54.2)
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(86.0, 5.5, f"{score} /100", align='C')

        pdf.rounded_rect(112.0, 49.0, 86.0, 20.0, 3.0, 'FD')
        pdf.set_xy(112.0, 51.0)
        pdf.set_font('Helvetica', 'B', 7.8)
        pdf.cell(86.0, 3.0, conv("NOTA DOS CLIENTES"), align='C', ln=True)
        pdf.set_xy(112.0, 54.2)
        pdf.set_font('Helvetica', 'B', 16)
        set_color_safe(pdf, 16, 185, 129, fn_type='text')
        pdf.cell(86.0, 5.5, f"{dados.get('nota', 0.0):.1f} *", align='C')

        # Lista de Itens (Compacta - Ajustada conforme referência)
        y_start_itens = 74.0
        h_slot = 8.8
        itens = [
            ("1. Fotos e Resolução Visual", 100 if dados.get('tem_fotos_hd') else 30, "Alto" if dados.get('tem_fotos_hd') else "Baixo", "Fotos HD no perfil.", "Fotos estáticas HD atraem cliques na busca."),
            ("2. Tour Virtual 360° Interativo", 100 if dados.get('tem_tour360') else 30, "Ativo" if dados.get('tem_tour360') else "Pendente de Validação", "Tour 360° interativo.", "Destaque visual e imersão no Street View."),
            ("3. Categorias Principal e Secundárias", 100 if dados.get('categorias_completas') else 50, "Completo" if dados.get('categorias_completas') else "Incompleto", "Categorias configuradas.", "Garante o match correto com buscas locais."),
            ("4. Horários e Exceções (Feriados)", 100 if dados.get('horarios_ok') else 40, "Atualizado" if dados.get('horarios_ok') else "Desatualizado", "Horários atualizados.", "Evita perda de clientes e viagens perdidas."),
            ("5. Website e Links de Conversão", 100 if dados.get('website') not in ["Não possui", "", None] else 10, "Ativo" if dados.get('website') not in ["Não possui", "", None] else "Falho", "Link oficial configurado.", "Encaminha tráfego aquecido para conversão."),
            ("6. Avaliações no Google (Prova Social)", min(int((dados.get('avaliacoes', 0)/50)*100), 100), f"{dados.get('nota', 0.0):.1f}/5.0", f"{dados.get('avaliacoes', 0)} avaliações.", "Prova social decisiva para fechar negócios."),
            ("7. Resumo Editorial & Descrição", 100 if dados.get('tem_descricao') else 30, "Completo" if dados.get('tem_descricao') else "Ausente", "Descrição cadastrada.", "Aumenta a indexação em palavras-chave."),
            ("8. Atributos de Acessibilidade/Serviços", 100 if dados.get('atributos_ok') else 40, "Ativo" if dados.get('atributos_ok') else "Pendente", "Atributos configurados.", "Informa facilidades (wifi, estacionamento)."),
            ("9. Interação e Resposta a Avaliações", 100 if dados.get('resposta_avaliacoes_ok') else 30, "Ativo" if dados.get('resposta_avaliacoes_ok') else "Pendente", "Respostas ativas.", "Responder demonstra atenção e passa confiança.")
        ]

        for idx_item, (titulo, pct, rotulo, desc, impacto) in enumerate(itens):
            y_curr = y_start_itens + (idx_item * h_slot)
            pdf.set_xy(21, y_curr)
            pdf.set_font('Helvetica', 'B', 8.5)
            set_color_safe(pdf, 30, 41, 59, fn_type='text')
            pdf.cell(122, 2.5, conv(titulo), border=0)
            
            if pct < 40: set_color_safe(pdf, 239, 68, 68, fn_type='text')
            elif pct < 80: set_color_safe(pdf, 245, 158, 11, fn_type='text')
            else: set_color_safe(pdf, 22, 128, 61, fn_type='text')
            pdf.cell(55, 2.5, conv(rotulo), border=0, align='R')

            y_bar = y_curr + 3.0
            set_color_safe(pdf, 226, 232, 240, fn_type='fill')
            pdf.rounded_rect(21, y_bar, 177, 1.0, 0.4, 'F')
            
            if pct < 40: set_color_safe(pdf, 239, 68, 68, fn_type='fill')
            elif pct < 80: set_color_safe(pdf, 245, 158, 11, fn_type='fill')
            else: set_color_safe(pdf, 22, 128, 61, fn_type='fill')
            pdf.rounded_rect(21, y_bar, max(float(pct) * 1.77, 4.0), 1.0, 0.4, 'F')

            pdf.set_xy(21, y_bar + 1.8)
            pdf.set_font('Helvetica', '', 7.3)
            set_color_safe(pdf, 71, 85, 105, fn_type='text')
            pdf.cell(177, 2.2, conv(f"   Estado: {desc}  |  Impacto: {impacto}"), border=0)

        # Plano de Ação Personalizado
        if plano_acao_extra:
            y_extra_top = 160.0
            pdf.set_line_width(0.3)
            set_color_safe(pdf, 248, 250, 252, fn_type='fill')
            set_color_safe(pdf, 203, 213, 225, fn_type='draw')
            pdf.rounded_rect(21.0, y_extra_top, 177, 95.0, 2.5, 'FD')
            
            pdf.set_xy(21.0, y_extra_top + 3.0)
            pdf.set_font('Helvetica', 'B', 8.5)
            set_color_safe(pdf, 30, 64, 175, fn_type='text')
            pdf.cell(177, 3.0, conv("PLANO DE AÇÃO E APONTAMENTOS ESTRATÉGICOS PERSONALIZADOS"), align='C')
            
            pdf.set_xy(25.0, y_extra_top + 8.0)
            pdf.set_font('Helvetica', '', 7.5)
            set_color_safe(pdf, 51, 65, 85, fn_type='text')
            pdf.multi_cell(169, 3.5, conv(plano_acao_extra), align='L')

    # PÁGINA 3, 4, 5 (Mapeamento, Proposta, Contrato)
    if 3 in paginas_selecionadas:
        pdf.add_page()
        pdf.set_xy(21, 29.0)
        pdf.set_font('Helvetica', 'B', 15)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        pdf.cell(177, 7, conv('MAPEAMENTO GEOGRÁFICO DE RAIO DE ATRAÇÃO'), align='C', ln=True)

    if 4 in paginas_selecionadas:
        pdf.add_page()
        pdf.set_xy(21, 29.0)
        pdf.set_font('Helvetica', 'B', 15)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        pdf.cell(177, 7, conv('PROPOSTA COMERCIAL & ESTRUTURAÇÃO ESTRATÉGICA'), align='C', ln=True)

    if 5 in paginas_selecionadas:
        pdf.add_page()
        pdf.set_xy(21, 29.0)
        pdf.set_font('Helvetica', 'B', 15)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        pdf.cell(177, 7, conv('CONTRATO DE PRESTAÇÃO DE SERVIÇOS'), align='C', ln=True)

    return bytes(pdf.output())

# -----------------------------------------------------------------------------
# 7. BARRA LATERAL (SIDEBAR)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div class="sidebar-header-box">
            <div class="sidebar-title-top">Consultoria e Diagnóstico</div>
            <div style="font-size:18px; font-weight:800; color:#3b82f6;">Tour360VR</div>
        </div>
        <div class="sidebar-divider"></div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="label-cliente-centralizado">Cliente em Atendimento</div>
        <div class="box-cliente-atendimento">🏢 {st.session_state['dados'].get('nome') or "Nenhum cliente"}</div>
    """, unsafe_allow_html=True)
    
    score_atual = calcular_score_real(st.session_state['dados'])
    st.progress(score_atual / 100.0)
    st.caption(f"Score do Cliente: **{score_atual}/100**")

    if st.button("🧹 Iniciar Novo Atendimento", use_container_width=True, type="secondary"):
        st.session_state['etapa_atual'] = 1
        st.session_state['dados'] = {
            "nome": "", "contato": "", "endereco": "", "telefone": "", "website": "",
            "nota": 0.0, "avaliacoes": 0, "tem_tour360": False, "tem_fotos_hd": False,
            "categorias_completas": False, "horarios_ok": False, "tem_descricao": False,
            "atributos_ok": False, "resposta_avaliacoes_ok": False, "categorias_detectadas": [], "foto_reference": "",
            "lat": None, "lng": None
        }
        st.rerun()

# -----------------------------------------------------------------------------
# 8. NAVEGAÇÃO DE ETAPAS
# -----------------------------------------------------------------------------
etapa_atual = st.session_state['etapa_atual']
col_e1, col_e2, col_e3, col_e4, col_e5 = st.columns(5)

with col_e1:
    if st.button("1. Busca & Ficha", use_container_width=True, type="primary" if etapa_atual == 1 else "secondary"):
        st.session_state['etapa_atual'] = 1; st.rerun()
with col_e2:
    if st.button("2. Concorrentes", use_container_width=True, type="primary" if etapa_atual == 2 else "secondary"):
        st.session_state['etapa_atual'] = 2; st.rerun()
with col_e3:
    if st.button("3. Plano de Ação", use_container_width=True, type="primary" if etapa_atual == 3 else "secondary"):
        st.session_state['etapa_atual'] = 3; st.rerun()
with col_e4:
    if st.button("4. Valores", use_container_width=True, type="primary" if etapa_atual == 4 else "secondary"):
        st.session_state['etapa_atual'] = 4; st.rerun()
with col_e5:
    if st.button("5. PDF & Ações", use_container_width=True, type="primary" if etapa_atual == 5 else "secondary"):
        st.session_state['etapa_atual'] = 5; st.rerun()

# -----------------------------------------------------------------------------
# 9. CONTEÚDO DAS ETAPAS
# -----------------------------------------------------------------------------
if etapa_atual == 1:
    col_left, col_right = st.columns([1.5, 1])
    with col_left:
        st.markdown("<div class='dashboard-card'><div class='card-title'>🔍 1. BUSCA DA FICHA NO GOOGLE MAPS</div>", unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        nome_input = c1.text_input("Nome da Empresa:", placeholder="Ex: Taiwan Hotel Ltda")
        cidade_empresa = c2.text_input("Cidade/Região:", placeholder="Ex: Ribeirão Preto, SP")
            
        if st.button("🚀 Pesquisar Ficha no Google", use_container_width=True, type="secondary"):
            if API_KEY_GOOGLE:
                try:
                    termo = f"{nome_input}, {cidade_empresa}" if cidade_empresa else nome_input
                    url_search = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={termo}&key={API_KEY_GOOGLE}"
                    res = requests.get(url_search, timeout=5).json()
                    if res.get("status") == "OK" and res.get("results"):
                        st.session_state['unidades_encontradas'] = res["results"]
                        st.success(f"Encontrada(s) {len(res['results'])} unidade(s)!")
                    else:
                        st.error("Nenhuma empresa encontrada.")
                except Exception as e:
                    st.error(f"Erro na consulta: {e}")
            else:
                st.warning("Insira uma chave API do Google para utilizar a busca automática.")

        if st.session_state['unidades_encontradas']:
            opcoes = [f"{u.get('name')} - {u.get('formatted_address')}" for u in st.session_state['unidades_encontradas']]
            escolha = st.selectbox("Selecione a unidade exata:", opcoes)
            
            if st.button("📌 Carregar Dados da Unidade", use_container_width=True, type="secondary"):
                idx = opcoes.index(escolha)
                u = st.session_state['unidades_encontradas'][idx]
                st.session_state['dados']['nome'] = u.get("name")
                st.session_state['dados']['endereco'] = u.get("formatted_address")
                st.session_state['dados']['nota'] = float(u.get("rating", 0.0))
                st.session_state['dados']['avaliacoes'] = int(u.get("user_ratings_total", 0))
                st.success("Dados carregados com sucesso!")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='dashboard-card'><div class='card-title'>DADOS DO CLIENTE</div>", unsafe_allow_html=True)
        st.session_state['dados']['nome'] = st.text_input("Empresa:", value=st.session_state['dados']['nome'])
        st.session_state['dados']['contato'] = st.text_input("Responsável:", value=st.session_state['dados']['contato'])
        st.session_state['dados']['telefone'] = st.text_input("Telefone:", value=st.session_state['dados']['telefone'])
        st.session_state['dados']['website'] = st.text_input("Website:", value=st.session_state['dados']['website'])
        st.session_state['dados']['endereco'] = st.text_area("Endereço:", value=st.session_state['dados']['endereco'], height=80)
        st.markdown("</div>", unsafe_allow_html=True)

elif etapa_atual == 2:
    st.markdown("<div class='dashboard-card'><div class='card-title'>⚔️ 2. AVALIAÇÃO DE CONCORRENTES DO SEGMENTO</div>", unsafe_allow_html=True)
    st.info("Adicione dados dos concorrentes da região para comparar o score de visibilidade no relatório.")
    st.markdown("</div>", unsafe_allow_html=True)

elif etapa_atual == 3:
    st.markdown("<div class='dashboard-card'><div class='card-title'>💡 3. APONTAMENTOS ESTRATÉGICOS E PLANO DE AÇÃO</div>", unsafe_allow_html=True)
    st.session_state['plano_acao_extra'] = st.text_area(
        "Edite os apontamentos para a Página 2 do PDF:",
        value=st.session_state['plano_acao_extra'],
        height=180
    )
    st.markdown("</div>", unsafe_allow_html=True)

elif etapa_atual == 4:
    st.markdown("<div class='dashboard-card'><div class='card-title'>📜 4. PLANOS COMERCIAIS & INVESTIMENTO</div>", unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    with p1:
        st.session_state['planos']['start_valor'] = st.text_input("Plano Start (R$):", value=st.session_state['planos']['start_valor'])
    with p2:
        st.session_state['planos']['pro_valor'] = st.text_input("Plano Pro (R$):", value=st.session_state['planos']['pro_valor'])
    with p3:
        st.session_state['planos']['gestao_valor'] = st.text_input("Gestão Mensal (R$):", value=st.session_state['planos']['gestao_valor'])
    st.markdown("</div>", unsafe_allow_html=True)

elif etapa_atual == 5:
    st.markdown("<div class='dashboard-card'><div class='card-title'>📄 5. EMISSÃO DE PDF & AÇÕES</div>", unsafe_allow_html=True)
    
    pdf_bytes = gerar_pdf_oficial(
        st.session_state['dados'], 
        st.session_state['planos'], 
        st.session_state.get('plano_acao_extra', ''),
        st.session_state.get('concorrentes', []),
        paginas_selecionadas=[1, 2]
    )

    st.download_button(
        label="📥 Baixar Diagnóstico PDF",
        data=pdf_bytes,
        file_name=f"Diagnostico - {st.session_state['dados'].get('nome', 'Cliente')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Rodapé Fixo
st.markdown("""
    <div class='custom-footer'>
        <a href='https://tour360vr.com.br' target='_blank'>tour360vr.com.br</a> | 
        Whatsapp: (16) 99133-2121 | 
        <b>Tour360VR - Gestão de Perfil do Google</b>
    </div>
""", unsafe_allow_html=True)

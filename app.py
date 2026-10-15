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
# 1. CARREGAMENTO DO FAVICON DE FORMA SEGURA
# -----------------------------------------------------------------------------
def obter_favicon_pil():
    caminhos = ['assets/logo_tour_transparente.png', 'assets/logo_tour.png', 'logo_tour_transparente.png', 'logo_tour.png']
    for c in caminhos:
        if os.path.exists(c):
            try:
                return Image.open(c)
            except Exception:
                pass
            
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
# 2. CONFIGURAÇÃO DA PÁGINA ST
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Consultoria & Diagnóstico - Tour360VR",
    page_icon=favicon_img,
    layout="wide",
    initial_sidebar_state="expanded"
)

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
# CREDENCIAIS DO SISTEMA
# -----------------------------------------------------------------------------
API_KEY_GOOGLE = (
    st.secrets.get("GOOGLE_API_KEY") 
    or st.secrets.get("GOOGLE_PLACES_API_KEY") 
    or os.environ.get("GOOGLE_API_KEY")
    or "AIzaSyA8ul_9QICNyqxrHgT-CURIZmd1sikHn5U"
)

SMTP_SERVER = "smtp.tour360vr.com.br"
SMTP_PORT_SSL = 465
SMTP_USER = "contato@tour360vr.com.br"
SMTP_PASS = "Kakaroto@2026"

# -----------------------------------------------------------------------------
# 3. FUNÇÕES UTILITÁRIAS, LOGOS, E-MAIL & ZOHO
# -----------------------------------------------------------------------------
def conv(texto):
    if texto is None: 
        return ""
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
    except Exception as e:
        print(f"Erro no Bigin: {e}")
        return False

def enviar_email_admin_com_pdf(dados, score, pdf_bytes):
    try:
        empresa_nome = dados.get("nome", "Empresa")
        responsavel = dados.get("contato", "Responsável")
        telefone = dados.get("telefone", "N/I")
        endereco = dados.get("endereco", "N/I")

        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT_SSL, timeout=15)
        server.login(SMTP_USER, SMTP_PASS)

        filename_clean = f"Diagnostico {empresa_nome}.pdf"

        msg_admin = MIMEMultipart('mixed')
        msg_admin['From'] = f"Tour360VR <{SMTP_USER}>"
        msg_admin['To'] = SMTP_USER
        msg_admin['Reply-To'] = SMTP_USER
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
                <br>
                <p style="font-size: 12px; color: #666666;">O PDF gerado foi anexado a este e-mail e os dados foram salvos no Zoho Bigin.</p>
            </div>
        </body>
        </html>
        """
        msg_admin.attach(MIMEText(corpo_admin_html, 'html', 'utf-8'))
        
        if pdf_bytes:
            part_admin = MIMEApplication(pdf_bytes, _subtype="pdf")
            part_admin.add_header('Content-Disposition', 'attachment', filename=filename_clean)
            msg_admin.attach(part_admin)

        server.send_message(msg_admin)
        server.quit()

        return True, "Enviado com sucesso!"
    except Exception as e:
        return False, f"Falha no envio do e-mail: {str(e)}"

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
# 5. GERADOR DE PDF INTELIGENTE (5 PÁGINAS)
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
                _ = self.image(caminho_logo, 21, 8.0, 11, 11)
            except Exception:
                pass
            
        _ = self.set_xy(35, 9.2)
        _ = self.set_font('Helvetica', 'B', 10.0)
        _ = self.set_text_color(30, 64, 175)
        _ = self.cell(163, 4.0, 'Tour360VR', align='L', ln=True)
        
        _ = self.set_x(35)
        _ = self.set_font('Helvetica', 'B', 7.2)
        _ = self.set_text_color(100, 116, 139)
        _ = self.cell(163, 3.8, conv('Gestão de Perfil & Diagnóstico do Google Meu Negócio'), align='L', ln=True)
        _ = self.set_draw_color(226, 232, 240)
        _ = self.line(21, 21.0, 198, 21.0)

    def footer(self):
        _ = self.set_y(-16)
        _ = self.set_draw_color(226, 232, 240)
        _ = self.line(21, self.get_y(), 198, self.get_y())
        _ = self.set_y(-13)
        
        _ = self.set_text_color(0, 0, 0)
        
        if self.page_no() == 1 and self.capa_incluida:
            _ = self.set_x(21)
            _ = self.set_font('Helvetica', '', 9.5)
            _ = self.cell(177, 5, conv("Tour360VR  |  (16) 99133-2121  |  Ribeirão Preto - SP  |  tour360vr.com.br"), align='C')
        else:
            _ = self.set_font('Helvetica', '', 8.5)
            _ = self.set_x(35)
            _ = self.cell(45, 5, 'contato@tour360vr.com.br', link='mailto:contato@tour360vr.com.br', align='C')
            _ = self.cell(40, 5, 'tour360vr.com.br', link='https://tour360vr.com.br', align='C')
            _ = self.cell(45, 5, 'WhatsApp: (16) 99133-2121', link='https://wa.me/5516991332121', align='C')
            if self.exibir_numeracao:
                _ = self.set_x(170)
                _ = self.cell(28, 5, f'Página {self.page_no()} de {self.total_paginas_pdf}', align='R')

    def rounded_rect(self, x, y, w, h, r, style=''):
        k, hp = self.k, self.h
        op = 'f' if style == 'F' else ('B' if style in ['FD', 'DF'] else 'S')
        my_arc = 4/3 * (2**0.5 - 1)
        _ = self._out(f'{(x+r)*k:.2f} {(hp-y)*k:.2f} m')
        xc, yc = x + w - r, y + r
        _ = self._out(f'{xc*k:.2f} {(hp-y)*k:.2f} l')
        _ = self._arc(xc + r*my_arc, yc - r, xc + r, yc - r*my_arc, xc + r, yc)
        xc, yc = x + w - r, y + h - r
        _ = self._out(f'{(x+w)*k:.2f} {(hp-yc)*k:.2f} l')
        _ = self._arc(xc + r, yc + r*my_arc, xc + r*my_arc, yc + r, xc, yc + r)
        xc, yc = x + r, y + h - r
        _ = self._out(f'{(x+r)*k:.2f} {(hp-(y+h))*k:.2f} l')
        _ = self._arc(xc - r*my_arc, yc + r, xc - r, yc + r*my_arc, xc - r, yc)
        xc, yc = x + r, y + r
        _ = self._out(f'{x*k:.2f} {(hp-yc)*k:.2f} l')
        _ = self._arc(xc - r, yc - r*my_arc, xc - r*my_arc, yc - r, xc, yc - r)
        _ = self._out(f'{op}')

    def _arc(self, x1, y1, x2, y2, x3, y3):
        k, hp = self.k, self.h
        _ = self._out(f'{x1*k:.2f} {(hp-y1)*k:.2f} {x2*k:.2f} {(hp-y2)*k:.2f} {x3*k:.2f} {(hp-y3)*k:.2f} c')

def set_color_safe(pdf_obj, r, g=None, b=None, fn_type='text'):
    if isinstance(r, (tuple, list)):
        r_v, g_v, b_v = int(r[0]), int(r[1]), int(r[2])
    elif g is not None and b is not None:
        r_v, g_v, b_v = int(r), int(g), int(b)
    else:
        r_v = g_v = b_v = int(r)
        
    if fn_type == 'text':
        pdf_obj.set_text_color(r_v, g_v, b_v)
    elif fn_type == 'fill':
        pdf_obj.set_fill_color(r_v, g_v, b_v)
    elif fn_type == 'draw':
        pdf_obj.set_draw_color(r_v, g_v, b_v)

def gerar_pdf_oficial(dados, planos, plano_acao_extra="", concorrentes=[], paginas_selecionadas=[1, 2, 3, 4, 5]):
    score = calcular_score_real(dados)
    capa_presente = 1 in paginas_selecionadas
    tot_pags = len(paginas_selecionadas)
    exibir_num = True
    
    pdf = PDFTour360Oficial(capa_incluida=capa_presente, exibir_numeracao=exibir_num, total_paginas_pdf=tot_pags)
    _ = pdf.set_margins(21, 12, 12)
    _ = pdf.set_auto_page_break(auto=False)

    # PÁGINA 1: CAPA
    if 1 in paginas_selecionadas:
        _ = pdf.add_page()
        caminho_logo = obter_caminho_logo("tour360")
        if caminho_logo:
            try:
                _ = pdf.image(caminho_logo, 90, 15.0, 36, 36)
            except Exception:
                pass

        _ = pdf.set_y(60)
        _ = pdf.set_font('Helvetica', 'B', 20)
        set_color_safe(pdf, 30, 64, 175, fn_type='text')
        _ = pdf.cell(0, 8, conv('DIAGNÓSTICO DE PRESENÇA DIGITAL'), align='C', ln=True)
        _ = pdf.ln(1)

        _ = pdf.set_font('Helvetica', 'B', 14)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(0, 6, conv('GOOGLE MEU NEGÓCIO'), align='C', ln=True)

        _ = pdf.ln(3.5)
        _ = pdf.set_font('Helvetica', '', 10.0)
        set_color_safe(pdf, 71, 85, 105, fn_type='text')
        _ = pdf.cell(0, 5, conv("Gestão de reputação e imagem online para o segmento no Google Maps"), align='C', ln=True)

        w_capa, h_capa, x_capa, y_capa = 177.0, 36.0, 21.0, 90.0
        set_color_safe(pdf, 248, 250, 252, fn_type='fill')
        set_color_safe(pdf, 203, 213, 225, fn_type='draw')
        _ = pdf.set_line_width(0.3)
        _ = pdf.rounded_rect(x_capa, y_capa, w_capa, h_capa, 3.0, 'FD')

        _ = pdf.set_xy(x_capa, y_capa + 3.0)
        
        _ = pdf.set_font('Helvetica', 'B', 14.0)
        set_color_safe(pdf, 15, 23, 42, fn_type='text') 
        _ = pdf.cell(w_capa, 5.0, conv(f"{dados.get('nome') or 'Nome da Empresa'}"), align='C', ln=True)

        _ = pdf.ln(3.0)

        _ = pdf.set_font('Helvetica', 'B', 10.5)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.set_x(x_capa)
        _ = pdf.cell(w_capa, 6.0, conv(f"Preparado para: {dados.get('contato') or 'Responsável'}"), align='C', ln=True)
        
        _ = pdf.set_font('Helvetica', '', 9.8)
        set_color_safe(pdf, 71, 85, 105, fn_type='text')
        _ = pdf.set_x(x_capa)
        _ = pdf.cell(w_capa, 5.5, conv(f"{dados.get('endereco') or 'Endereço não informado'}"), align='C', ln=True)
        
        site_txt = dados.get('website') if dados.get('website') else 'N/I'
        _ = pdf.set_x(x_capa)
        _ = pdf.cell(w_capa, 5.5, conv(f"Telefone: {dados.get('telefone') or 'N/I'}   |   {site_txt}"), align='C', ln=True)

        y_foto, h_container, w_container = 132.0, 92.0, 177.0
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
                    _ = pdf.image(img_data, x=offset_x, y=offset_y, w=final_w, h=final_h)
                    foto_renderizada = True
            except Exception:
                pass

        if not foto_renderizada:
            set_color_safe(pdf, 248, 250, 252, fn_type='fill')
            set_color_safe(pdf, 203, 213, 225, fn_type='draw')
            _ = pdf.rounded_rect(x_capa, y_foto, w_container, h_container, 3.0, 'FD')
            _ = pdf.set_xy(x_capa, y_foto + 40)
            _ = pdf.set_font('Helvetica', 'B', 11)
            set_color_safe(pdf, 100, 116, 139, fn_type='text')
            _ = pdf.cell(w_container, 6, conv("[ IMAGEM DA FICHA GOOGLE DO CLIENTE ]"), align='C', ln=True)

        w_alerta = 177.0
        x_alerta = 21.0
        y_alerta = 236.0
        h_alerta = 17.0
        
        qtd_aval = dados.get('avaliacoes', 0)
        nota_cli = dados.get('nota', 0.0)
        tem_tour = dados.get('tem_tour360', False)

        if tem_tour and nota_cli >= 4.5:
            bg_alerta = (248, 250, 252)
            bd_alerta = (203, 213, 225)
            tx_alerta = (22, 101, 52)
            sub_txt_1 = f"SEU PERFIL POSSUI EXCELENTE PRESENÇA VISUAL, NOTA {nota_cli:.1f} E {qtd_aval} AVALIAÇÕES."
            sub_txt_2 = "MANTER A FICHA ATUALIZADA É O SEGREDO PARA LIDERAR O MERCADO."
        else:
            bg_alerta = (254, 242, 242)
            bd_alerta = (254, 202, 202)
            tx_alerta = (185, 28, 28)
            if qtd_aval == 0:
                sub_txt_1 = "SEU PERFIL AINDA NÃO POSSUI AVALIAÇÕES CADASTRADAS NO GOOGLE,"
                sub_txt_2 = "E A FALTA DE IMPACTO VISUAL FAZ VOCÊ PERDER CLIENTES DIARIAMENTE."
            elif qtd_aval < 15:
                sub_txt_1 = f"SEU PERFIL TEM NOTA {nota_cli:.1f} E APENAS {qtd_aval} AVALIAÇÕES NO GOOGLE,"
                sub_txt_2 = "E A AUSÊNCIA DE CONTEÚDO IMERSIVO LIMITA O SEU CRESCIMENTO."
            else:
                sub_txt_1 = f"SEU PERFIL TEM NOTA SÓLIDA DE {nota_cli:.1f} COM {qtd_aval} AVALIAÇÕES NO GOOGLE,"
                sub_txt_2 = "MAS A FALTA DE EXPERIÊNCIA IMERSIVA DEIXA DINHEIRO NA MESA."

        set_color_safe(pdf, bg_alerta, fn_type='fill')
        set_color_safe(pdf, bd_alerta, fn_type='draw')
        _ = pdf.set_line_width(0.3)
        _ = pdf.rounded_rect(x_alerta, y_alerta, w_alerta, h_alerta, 2.5, 'FD')

        y_text_center = y_alerta + ((h_alerta - 8.5) / 2.0)
        
        _ = pdf.set_xy(x_alerta, y_text_center)
        _ = pdf.set_font('Helvetica', 'B', 8.5)
        set_color_safe(pdf, tx_alerta, fn_type='text')
        _ = pdf.cell(w_alerta, 4.0, conv(sub_txt_1), align='C', ln=True)
        _ = pdf.set_x(x_alerta)
        _ = pdf.cell(w_alerta, 4.0, conv(sub_txt_2), align='C', ln=True)

    # PÁGINA 2: AUDITORIA DETALHADA
    if 2 in paginas_selecionadas:
        _ = pdf.add_page()
        
        _ = pdf.set_xy(21, 29.0)
        _ = pdf.set_font('Helvetica', 'B', 15)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(177, 7, conv('AUDITORIA DETALHADA DE PONTOS DE BUSCA'), align='C', ln=True)

        w_ficha, x_ficha, y_ficha, h_ficha = 177, 21.0, 42.0, 8.5
        set_color_safe(pdf, 248, 250, 252, fn_type='fill')
        set_color_safe(pdf, 203, 213, 225, fn_type='draw')
        _ = pdf.set_line_width(0.3)
        _ = pdf.rounded_rect(x_ficha, y_ficha, w_ficha, h_ficha, 2.5, 'FD')
        
        _ = pdf.set_xy(x_ficha, y_ficha + 1.8)
        _ = pdf.set_font('Helvetica', 'B', 12.0)
        set_color_safe(pdf, 30, 64, 175, fn_type='text')
        _ = pdf.cell(w_ficha, 4.8, conv(f"{dados.get('nome') or 'Empresa Analisada'}"), align='C', ln=True)

        y_quadros_topo = 54.0
        w_q1, w_q2 = 86.0, 86.0
        x_q1, x_q2 = 21.0, 112.0
        h_q = 20.0

        set_color_safe(pdf, 255, 255, 255, fn_type='fill')
        set_color_safe(pdf, 226, 232, 240, fn_type='draw')
        _ = pdf.rounded_rect(x_q1, y_quadros_topo, w_q1, h_q, 3.0, 'FD')

        _ = pdf.set_xy(x_q1, y_quadros_topo + 2.0)
        _ = pdf.set_font('Helvetica', 'B', 7.8)
        set_color_safe(pdf, 71, 85, 105, fn_type='text')
        _ = pdf.cell(w_q1, 3.0, conv("OTIMIZAÇÃO DO PERFIL"), align='C', ln=True)

        _ = pdf.set_xy(x_q1, y_quadros_topo + 5.2)
        _ = pdf.set_font('Helvetica', 'B', 16)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        str_score = f"{score} /100"
        _ = pdf.cell(w_q1, 5.5, str_score, align='C')

        y_term = y_quadros_topo + 14.5
        w_term = 70.0
        x_term_start = x_q1 + (w_q1 - w_term) / 2.0
        set_color_safe(pdf, 241, 245, 249, fn_type='fill')
        _ = pdf.rounded_rect(x_term_start, y_term, w_term, 2.5, 1.0, 'F')
        
        steps = int(w_term * (score / 100.0))
        for step in range(steps):
            ratio = step / float(w_term)
            if ratio < 0.25:
                r, g, b = int(126 + ratio*4*(219-126)), int(34 + ratio*4*(39-34)), int(206 + ratio*4*(119-206))
            elif ratio < 0.50:
                r, g, b = int(219 + (ratio-0.25)*4*(234-219)), int(39 + (ratio-0.25)*4*(88-39)), int(119 + (ratio-0.25)*4*(12-119))
            elif ratio < 0.75:
                r, g, b = int(234 + (ratio-0.50)*4*(234-234)), int(88 + (ratio-0.50)*4*(179-88)), int(12 + (ratio-0.50)*4*(8-12))
            else:
                r, g, b = int(234 + (ratio-0.75)*4*(16-234)), int(179 + (ratio-0.75)*4*(185-179)), int(8 + (ratio-0.75)*4*(129-8))
            set_color_safe(pdf, r, g, b, fn_type='fill')
            _ = pdf.rect(x_term_start + step, y_term, 1.05, 2.5, 'F')

        set_color_safe(pdf, 255, 255, 255, fn_type='fill')
        set_color_safe(pdf, 226, 232, 240, fn_type='draw')
        _ = pdf.rounded_rect(x_q2, y_quadros_topo, w_q2, h_q, 3.0, 'FD')

        _ = pdf.set_xy(x_q2, y_quadros_topo + 2.0)
        _ = pdf.set_font('Helvetica', 'B', 7.8)
        set_color_safe(pdf, 71, 85, 105, fn_type='text')
        _ = pdf.cell(w_q2, 3.0, conv("NOTA DOS CLIENTES"), align='C', ln=True)

        _ = pdf.set_xy(x_q2, y_quadros_topo + 5.2)
        _ = pdf.set_font('Helvetica', 'B', 16)
        set_color_safe(pdf, 16, 185, 129, fn_type='text')
        _ = pdf.cell(w_q2, 5.5, f"{dados.get('nota', 0.0):.1f} *", align='C')

        _ = pdf.set_xy(x_q2, y_quadros_topo + 12.2)
        _ = pdf.set_font('Helvetica', '', 7.5)
        set_color_safe(pdf, 71, 85, 105, fn_type='text')
        _ = pdf.cell(w_q2, 2.8, conv(f"{dados.get('avaliacoes', 0)} avaliações cadastradas no Google"), align='C', ln=True)

        y_start_itens = 81.0
        h_slot = 8.8

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
        desc_tour = "Tour Virtual 360° ativo e integrado." if dados.get('tem_tour360') else "Não detectado via API. Necessário checagem na ficha."
        desc_cat = "Atende às categorias recomendadas." if dados.get('categorias_completas') else "Ajuste necessário em categorias secundárias."
        desc_web = f"Website oficial: {dados.get('website')}" if dados.get('website') != 'Não possui' and dados.get('website') != '' else "Falta link de website cadastrado para conversão."
        desc_desc = "Resumo editorial ativo no perfil." if dados.get('tem_descricao', True) else "Descrição da empresa incompleta ou ausente."
        desc_atrib = "Atributos de serviços ativos." if dados.get('atributos_ok', True) else "Falta cadastrar atributos de acessibilidade/serviços."
        desc_resp = "Frequência ativa de respostas do proprietário." if dados.get('resposta_avaliacoes_ok', False) else "Falta de respostas oficiais às avaliações."

        itens = [
            ("1. Fotos e Resolução Visual", pct_fotos, "Alto" if dados.get('tem_fotos_hd') else "Baixo", desc_fotos, "Fotos estáticas HD atraem cliques na busca."),
            ("2. Tour Virtual 360° Interativo", pct_tour, rotulo_tour, desc_tour, "Destaque visual e imersão no Street View."),
            ("3. Categorias Principal e Secundárias", pct_cat, "Completo" if dados.get('categorias_completas') else "Incompleto", desc_cat, "Garante o match correto com buscas locais."),
            ("4. Horários e Exceções (Feriados)", pct_hor, "Atualizado" if dados.get('horarios_ok') else "Desatualizado", "Falta de horários em feriados.", "Evita perda de clientes e viagens perdidas."),
            ("5. Website e Links de Conversão", pct_web, "Ativo" if dados.get('website') != 'Não possui' and dados.get('website') != '' else "Falho", desc_web, "Encaminha tráfego aquecido para conversão."),
            ("6. Avaliações no Google (Prova Social)", pct_avaliacoes, f"{dados.get('nota', 0.0):.1f}/5.0", f"{dados.get('avaliacoes', 0)} avaliações.", "Prova social decisiva para fechar negócios."),
            ("7. Resumo Editorial & Descrição", pct_desc, "Completo" if dados.get('tem_descricao', True) else "Ausente", desc_desc, "Aumenta a indexação em palavras-chave."),
            ("8. Atributos de Acessibilidade/Serviços", pct_atrib, "Ativo" if dados.get('atributos_ok', True) else "Pendente", desc_atrib, "Informa facilidades (wifi, estacionamento)."),
            ("9. Interação e Resposta a Avaliações", pct_resp, "Ativo" if dados.get('resposta_avaliacoes_ok', False) else "Pendente", desc_resp, "Responder demonstra atenção e passa confiança.")
        ]

        for idx_item, (titulo, pct, rotulo, desc, impacto) in enumerate(itens):
            gap_extra = 3.5 if idx_item > 0 else 0.0
            y_curr = y_start_itens + (idx_item * h_slot) + gap_extra
            _ = pdf.set_xy(21, y_curr)
            
            _ = pdf.set_font('Helvetica', 'B', 8.8)
            set_color_safe(pdf, 30, 41, 59, fn_type='text')
            _ = pdf.cell(122, 2.6, conv(titulo), border=0)
            
            _ = pdf.set_font('Helvetica', 'B', 8.8)
            if pct < 40: set_color_safe(pdf, 239, 68, 68, fn_type='text')
            elif pct < 80: set_color_safe(pdf, 245, 158, 11, fn_type='text')
            else: set_color_safe(pdf, 22, 128, 61, fn_type='text')
                
            _ = pdf.cell(55, 2.6, conv(rotulo), border=0, align='R')

            y_bar = y_curr + 3.2
            set_color_safe(pdf, 226, 232, 240, fn_type='fill')
            _ = pdf.rounded_rect(21, y_bar, 177, 1.1, 0.4, 'F')
            
            if pct < 40: set_color_safe(pdf, 239, 68, 68, fn_type='fill')
            elif pct < 80: set_color_safe(pdf, 245, 158, 11, fn_type='fill')
            else: set_color_safe(pdf, 22, 128, 61, fn_type='fill')
                
            _ = pdf.rounded_rect(21, y_bar, max(float(pct) * 1.77, 4.0), 1.1, 0.4, 'F')

            _ = pdf.set_xy(21, y_bar + 2.0)
            _ = pdf.set_font('Helvetica', '', 7.6)
            set_color_safe(pdf, 71, 85, 105, fn_type='text')
            _ = pdf.cell(177, 2.3, conv(f"   Estado: {desc[:58]}  |  Impacto: {impacto[:55]}"), border=0)

        # QUADRO DE ATENÇÃO
        y_atencao = 166.0
        w_atencao = 177.0
        h_atencao = 13.0

        resp_ok = dados.get('resposta_avaliacoes_ok', False)
        if not resp_ok:
            tit_atencao = "Avaliações negativas sem resposta do gestor"
            txt_atencao = "Existem avaliações com críticas diretas recentes no perfil. O Google e potenciais clientes notam quando o proprietário não responde. Isso afeta a confiança e pode empurrar potenciais clientes diretamente para os concorrentes da região."
        else:
            tit_atencao = "Manutenção ativa da reputação e autoridade no perfil"
            txt_atencao = "O perfil mantém um bom ritmo de interação, mas a otimização contínua de fotos HD e atualização constante das categorias garante que a empresa continue dominando as primeiras posições do mapa na região."

        set_color_safe(pdf, (254, 242, 242) if not resp_ok else (240, 253, 244), fn_type='fill')
        set_color_safe(pdf, (254, 202, 202) if not resp_ok else (187, 247, 208), fn_type='draw')
        _ = pdf.rounded_rect(21, y_atencao, w_atencao, h_atencao, 2.0, 'FD')

        set_color_safe(pdf, (220, 38, 38) if not resp_ok else (22, 163, 74), fn_type='fill')
        _ = pdf.rounded_rect(21, y_atencao, 2.5, h_atencao, 0.8, 'F')

        _ = pdf.set_xy(26, y_atencao + 1.5)
        _ = pdf.set_font('Helvetica', 'B', 8.5)
        set_color_safe(pdf, (153, 27, 27) if not resp_ok else (20, 83, 45), fn_type='text')
        _ = pdf.cell(w_atencao - 10, 2.8, conv(tit_atencao), ln=True)

        _ = pdf.set_xy(26, y_atencao + 4.5)
        _ = pdf.set_font('Helvetica', '', 7.3)
        set_color_safe(pdf, (127, 29, 29) if not resp_ok else (22, 101, 52), fn_type='text')
        _ = pdf.multi_cell(w_atencao - 12, 2.6, conv(txt_atencao), align='L')

        # ANÁLISE AUTOMÁTICA DE CONCORRENTES
        y_tit_conc = 185.0
        concorrentes_filtrados = [c for c in concorrentes if c.get("nome", "").strip() != ""]
        if concorrentes_filtrados:
            _ = pdf.set_xy(21, y_tit_conc)
            _ = pdf.set_font('Helvetica', 'B', 8.5)
            set_color_safe(pdf, 30, 64, 175, fn_type='text')
            _ = pdf.cell(0, 3.5, conv("ANÁLISE AUTOMÁTICA DE CONCORRENTES DO SEGMENTO"), border=0)

            w_emp, w_item, w_score, h_row = 53, 11.0, 25.0, 3.8
            y_table = y_tit_conc + 4.2
            _ = pdf.set_xy(21, y_table)
            set_color_safe(pdf, 30, 64, 175, fn_type='fill')
            set_color_safe(pdf, 255, 255, 255, fn_type='text')
            _ = pdf.set_font('Helvetica', 'B', 7.5)
            
            _ = pdf.cell(w_emp, h_row, conv(" Empresa / Concorrente"), border=0, fill=True)
            _ = pdf.cell(w_item, h_row, conv("1.Fotos"), border=0, fill=True, align='C')
            _ = pdf.cell(w_item, h_row, conv("2.360°"), border=0, fill=True, align='C')
            _ = pdf.cell(w_item, h_row, conv("3.Categ"), border=0, fill=True, align='C')
            _ = pdf.cell(w_item, h_row, conv("4.Horár"), border=0, fill=True, align='C')
            _ = pdf.cell(w_item, h_row, conv("5.Web"), border=0, fill=True, align='C')
            _ = pdf.cell(w_item, h_row, conv("6.Nota"), border=0, fill=True, align='C')
            _ = pdf.cell(w_item, h_row, conv("7.Desc"), border=0, fill=True, align='C')
            _ = pdf.cell(w_item, h_row, conv("8.Atrib"), border=0, fill=True, align='C')
            _ = pdf.cell(w_item, h_row, conv("9.Resp"), border=0, fill=True, align='C')
            _ = pdf.cell(w_score, h_row, conv("Score Geral"), border=0, fill=True, align='C')

            def celula_sim_nao_colorida(pdf_obj, w, h, valor):
                if valor == "Sim":
                    set_color_safe(pdf_obj, 220, 252, 231, fn_type='fill')
                    set_color_safe(pdf_obj, 22, 101, 52, fn_type='text')
                else:
                    set_color_safe(pdf_obj, 254, 226, 226, fn_type='fill')
                    set_color_safe(pdf_obj, 153, 27, 27, fn_type='text')
                
                set_color_safe(pdf_obj, 191, 219, 254, fn_type='draw')
                _ = pdf_obj.cell(w, h, conv(valor), border=1, fill=True, align='C')

            y_r1 = y_table + h_row
            _ = pdf.set_xy(21, y_r1)
            set_color_safe(pdf, 239, 246, 255, fn_type='fill')
            set_color_safe(pdf, 191, 219, 254, fn_type='draw')
            _ = pdf.set_font('Helvetica', 'B', 8.0)
            set_color_safe(pdf, 30, 64, 175, fn_type='text')
            _ = pdf.cell(w_emp, h_row, conv(f" {str(dados.get('nome', ''))[:25]}"), border=1, fill=True)
            
            celula_sim_nao_colorida(pdf, w_item, h_row, "Sim" if dados.get('tem_fotos_hd') else "Não")
            celula_sim_nao_colorida(pdf, w_item, h_row, "Sim" if dados.get('tem_tour360') else "Não")
            celula_sim_nao_colorida(pdf, w_item, h_row, "Sim" if dados.get('categorias_completas') else "Não")
            celula_sim_nao_colorida(pdf, w_item, h_row, "Sim" if dados.get('horarios_ok') else "Não")
            celula_sim_nao_colorida(pdf, w_item, h_row, "Sim" if dados.get('website') and dados.get('website') != 'Não possui' else "Não")
            
            set_color_safe(pdf, 239, 246, 255, fn_type='fill')
            set_color_safe(pdf, 30, 64, 175, fn_type='text')
            _ = pdf.cell(w_item, h_row, conv(f"{dados.get('nota', 0.0):.1f}"), border=1, fill=True, align='C')
            
            celula_sim_nao_colorida(pdf, w_item, h_row, "Sim" if dados.get('tem_descricao') else "Não")
            celula_sim_nao_colorida(pdf, w_item, h_row, "Sim" if dados.get('atributos_ok') else "Não")
            celula_sim_nao_colorida(pdf, w_item, h_row, "Sim" if dados.get('resposta_avaliacoes_ok') else "Não")
            
            set_color_safe(pdf, 239, 246, 255, fn_type='fill')
            _ = pdf.set_font('Helvetica', 'B', 8.0)
            set_color_safe(pdf, 30, 64, 175, fn_type='text')
            _ = pdf.cell(w_score, h_row, conv(f"{score} / 100"), border=1, fill=True, align='C')

            _ = pdf.set_font('Helvetica', '', 8.0)
            for idx_c, c in enumerate(concorrentes_filtrados):
                y_rc = y_r1 + ((idx_c + 1) * h_row)
                score_conc = calcular_score_concorrente(c)
                _ = pdf.set_xy(21, y_rc)
                set_color_safe(pdf, 255, 255, 255, fn_type='fill')
                set_color_safe(pdf, 191, 219, 254, fn_type='draw')
                set_color_safe(pdf, 51, 65, 85, fn_type='text')
                
                _ = pdf.cell(w_emp, h_row, conv(f" {c.get('nome', '')[:25]}"), border=1, fill=True)
                celula_sim_nao_colorida(pdf, w_item, h_row, c.get('tem_fotos_hd', 'Não'))
                celula_sim_nao_colorida(pdf, w_item, h_row, c.get('tem_tour360', 'Não'))
                celula_sim_nao_colorida(pdf, w_item, h_row, c.get('categorias_ok', 'Não'))
                celula_sim_nao_colorida(pdf, w_item, h_row, c.get('horarios_ok', 'Não'))
                celula_sim_nao_colorida(pdf, w_item, h_row, c.get('tem_website', 'Não'))
                
                set_color_safe(pdf, 255, 255, 255, fn_type='fill')
                set_color_safe(pdf, 51, 65, 85, fn_type='text')
                _ = pdf.cell(w_item, h_row, conv(f"{float(c.get('nota', 0.0)):.1f}"), border=1, fill=True, align='C')
                
                celula_sim_nao_colorida(pdf, w_item, h_row, c.get('tem_descricao', 'Não'))
                celula_sim_nao_colorida(pdf, w_item, h_row, c.get('atributos_ok', 'Não'))
                celula_sim_nao_colorida(pdf, w_item, h_row, c.get('respostas_ok', 'Não'))
                
                set_color_safe(pdf, 255, 255, 255, fn_type='fill')
                _ = pdf.set_font('Helvetica', 'B', 8.0)
                set_color_safe(pdf, 51, 65, 85, fn_type='text')
                _ = pdf.cell(w_score, h_row, conv(f"{score_conc} / 100"), border=1, fill=True, align='C')
                _ = pdf.set_font('Helvetica', '', 8.0)

        # PLANO DE AÇÃO
        if plano_acao_extra and plano_acao_extra.strip() != "":
            y_extra_top = 215.0
            w_extra, x_extra, h_box_extra = 177, 21.0, 25.0
            set_color_safe(pdf, 248, 250, 252, fn_type='fill')
            set_color_safe(pdf, 203, 213, 225, fn_type='draw')
            _ = pdf.set_line_width(0.3)
            _ = pdf.rounded_rect(x_extra, y_extra_top, w_extra, h_box_extra, 2.5, 'FD')
            
            _ = pdf.set_xy(x_extra, y_extra_top + 2.5)
            _ = pdf.set_font('Helvetica', 'B', 8.5)
            set_color_safe(pdf, 30, 64, 175, fn_type='text')
            _ = pdf.cell(w_extra, 3.2, conv("PLANO DE AÇÃO E APONTAMENTOS ESTRATÉGICOS PERSONALIZADOS"), align='C', border=0)
            
            linhas_plano = [l for l in plano_acao_extra.split('\n') if l.strip()]
            num_linhas = len(linhas_plano)
            altura_bloco_texto = num_linhas * 3.4
            y_start_texto_centralizado = y_extra_top + 6.2 + max((16.0 - altura_bloco_texto) / 2.0, 0.5)

            _ = pdf.set_xy(x_extra + 5, y_start_texto_centralizado)
            _ = pdf.set_font('Helvetica', '', 7.8)
            set_color_safe(pdf, 51, 65, 85, fn_type='text')
            _ = pdf.multi_cell(w_extra - 10, 3.4, conv(plano_acao_extra), align='L')

    # PÁGINA 3: MAPEAMENTO GEOGRÁFICO & DIAGNÓSTICO (VERSÃO ORIGINAL ESTÁVEL)
    if 3 in paginas_selecionadas:
        _ = pdf.add_page()
        
        _ = pdf.set_xy(21, 29.0)
        _ = pdf.set_font('Helvetica', 'B', 15)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(177, 7, conv('MAPEAMENTO GEOGRÁFICO DE RAIO DE ATRAÇÃO'), align='C', ln=True)

        _ = pdf.set_y(39.5)
        _ = pdf.set_font('Helvetica', '', 10.0)
        set_color_safe(pdf, 71, 85, 105, fn_type='text')
        _ = pdf.cell(177, 4.5, conv("Simulação de visibilidade em buscas locais por proximidade ('próximo a mim')"), align='C', ln=True)

        y_mapa = 48.0
        w_mapa = 177.0
        h_mapa = 92.0
        x_mapa = 21.0

        # Fundo do Google Maps
        set_color_safe(pdf, 229, 227, 223, fn_type='fill')
        set_color_safe(pdf, 203, 213, 225, fn_type='draw')
        _ = pdf.set_line_width(0.3)
        _ = pdf.rounded_rect(x_mapa, y_mapa, w_mapa, h_mapa, 3.0, 'FD')

        cx, cy = x_mapa + (w_mapa / 2.0), y_mapa + (h_mapa / 2.0) - 5.0

        mapa_real_carregado = False
        lat, lng = dados.get("lat"), dados.get("lng")

        if (not lat or not lng) and API_KEY_GOOGLE and dados.get("endereco"):
            try:
                url_geo = f"https://maps.googleapis.com/maps/api/geocode/json?address={requests.utils.quote(dados['endereco'])}&key={API_KEY_GOOGLE}"
                res_geo = requests.get(url_geo, timeout=3).json()
                if res_geo.get("status") == "OK" and res_geo.get("results"):
                    loc = res_geo["results"][0]["geometry"]["location"]
                    lat, lng = loc["lat"], loc["lng"]
            except Exception: pass

        if lat and lng and API_KEY_GOOGLE:
            try:
                url_static_map = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom=14&size=600x300&maptype=roadmap&style=feature:administrative|element:labels.text.fill|color:0x444444&markers=color:red%7Clabel:E%7C{lat},{lng}&key={API_KEY_GOOGLE}"
                resp_m = requests.get(url_static_map, timeout=4)
                if resp_m.status_code == 200:
                    img_m = io.BytesIO(resp_m.content)
                    _ = pdf.image(img_m, x=x_mapa + 1.5, y=y_mapa + 1.5, w=w_mapa - 3.0, h=h_mapa - 18.0)
                    mapa_real_carregado = True
            except Exception: pass

        if not mapa_real_carregado:
            set_color_safe(pdf, 244, 243, 240, fn_type='fill')
            _ = pdf.rect(x_mapa + 5, y_mapa + 5, 40, 25, 'F')
            _ = pdf.rect(x_mapa + 50, y_mapa + 5, 50, 30, 'F')
            _ = pdf.rect(x_mapa + 105, y_mapa + 5, 65, 20, 'F')
            _ = pdf.rect(x_mapa + 5, y_mapa + 35, 35, 30, 'F')
            _ = pdf.rect(x_mapa + 135, y_mapa + 30, 35, 35, 'F')

            set_color_safe(pdf, 255, 255, 255, fn_type='draw')
            _ = pdf.set_line_width(2.5)
            for gx in range(int(x_mapa + 15), int(x_mapa + w_mapa - 10), 22):
                _ = pdf.line(gx, y_mapa + 3, gx, y_mapa + h_mapa - 20)
            for gy in range(int(y_mapa + 12), int(y_mapa + h_mapa - 20), 16):
                _ = pdf.line(x_mapa + 3, gy, x_mapa + w_mapa - 3, gy)

            set_color_safe(pdf, 255, 224, 130, fn_type='draw')
            _ = pdf.set_line_width(3.2)
            _ = pdf.line(x_mapa + 3, cy - 6, x_mapa + w_mapa - 3, cy - 6)
            _ = pdf.line(cx + 12, y_mapa + 3, cx + 12, y_mapa + h_mapa - 20)

            set_color_safe(pdf, 165, 191, 221, fn_type='draw')
            _ = pdf.set_line_width(4.0)
            _ = pdf.line(x_mapa + 3, y_mapa + 12, x_mapa + 45, y_mapa + 50)

            set_color_safe(pdf, 239, 68, 68, fn_type='draw')
            set_color_safe(pdf, 254, 226, 226, fn_type='fill')
            _ = pdf.ellipse(cx - 36, cy - 28, 72, 56, 'FD')

            set_color_safe(pdf, 234, 179, 8, fn_type='draw')
            set_color_safe(pdf, 254, 249, 195, fn_type='fill')
            _ = pdf.ellipse(cx - 22, cy - 17, 44, 34, 'FD')

            set_color_safe(pdf, 34, 197, 94, fn_type='draw')
            set_color_safe(pdf, 220, 252, 231, fn_type='fill')
            _ = pdf.ellipse(cx - 10, cy - 8, 20, 16, 'FD')

            set_color_safe(pdf, 234, 67, 53, fn_type='fill')
            _ = pdf.ellipse(cx - 3.5, cy - 8.0, 7.0, 7.0, 'F')
            _ = pdf.polygon([cx - 3.5, cy - 4.5, cx + 3.5, cy - 4.5, cx, cy], 'F')
            set_color_safe(pdf, 255, 255, 255, fn_type='fill')
            _ = pdf.ellipse(cx - 1.2, cy - 5.7, 2.4, 2.4, 'F')

        # Badge da Empresa
        set_color_safe(pdf, 255, 255, 255, fn_type='fill')
        set_color_safe(pdf, 30, 64, 175, fn_type='draw')
        _ = pdf.set_line_width(0.4)
        _ = pdf.rounded_rect(cx - 38, cy + 6, 76, 5.5, 1.2, 'FD')
        _ = pdf.set_xy(cx - 38, cy + 7.0)
        _ = pdf.set_font('Helvetica', 'B', 7.8)
        set_color_safe(pdf, 30, 64, 175, fn_type='text')
        nome_emp_txt = str(dados.get('nome', 'Sua Empresa'))[:28]
        _ = pdf.cell(76, 3.5, conv(f"Empresa: {nome_emp_txt}"), align='C')

        # Legendas do Raio
        y_leg = y_mapa + h_mapa - 14.0
        
        set_color_safe(pdf, 220, 252, 231, fn_type='fill')
        set_color_safe(pdf, 134, 239, 172, fn_type='draw')
        _ = pdf.rounded_rect(x_mapa + 6, y_leg, 53, 10.0, 1.5, 'FD')
        _ = pdf.set_xy(x_mapa + 8, y_leg + 1.0)
        _ = pdf.set_font('Helvetica', 'B', 7.5)
        set_color_safe(pdf, 22, 101, 52, fn_type='text')
        _ = pdf.cell(49, 3.0, conv("[1.5 km] Raio Bairro"), align='C', ln=True)
        _ = pdf.set_x(x_mapa + 8)
        _ = pdf.set_font('Helvetica', '', 6.8)
        _ = pdf.cell(49, 3.0, conv("Top 3 - Visibilidade Alta"), align='C')

        set_color_safe(pdf, 254, 252, 232, fn_type='fill')
        set_color_safe(pdf, 253, 224, 71, fn_type='draw')
        _ = pdf.rounded_rect(x_mapa + 62, y_leg, 53, 10.0, 1.5, 'FD')
        _ = pdf.set_xy(x_mapa + 64, y_leg + 1.0)
        _ = pdf.set_font('Helvetica', 'B', 7.5)
        set_color_safe(pdf, 133, 77, 14, fn_type='text')
        _ = pdf.cell(49, 3.0, conv("[3.0 km] Raio Regiao"), align='C', ln=True)
        _ = pdf.set_x(x_mapa + 64)
        _ = pdf.set_font('Helvetica', '', 6.8)
        _ = pdf.cell(49, 3.0, conv("Queda de Posicao no Maps"), align='C')

        set_color_safe(pdf, 254, 242, 242, fn_type='fill')
        set_color_safe(pdf, 252, 165, 165, fn_type='draw')
        _ = pdf.rounded_rect(x_mapa + 118, y_leg, 53, 10.0, 1.5, 'FD')
        _ = pdf.set_xy(x_mapa + 120, y_leg + 1.0)
        _ = pdf.set_font('Helvetica', 'B', 7.5)
        set_color_safe(pdf, 153, 27, 27, fn_type='text')
        _ = pdf.cell(49, 3.0, conv("[5.0+ km] Raio Cidade"), align='C', ln=True)
        _ = pdf.set_x(x_mapa + 120)
        _ = pdf.set_font('Helvetica', '', 6.8)
        _ = pdf.cell(49, 3.0, conv("Invisivel nas Buscas"), align='C')

        # DIAGNÓSTICO DE BUSCAS POR INTENÇÃO (ESTRUTURA ORIGINAL)
        y_termos = 146.0
        _ = pdf.set_xy(21, y_termos)
        _ = pdf.set_font('Helvetica', 'B', 10.0)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(177, 4.0, conv("DIAGNÓSTICO DE BUSCAS POR INTENÇÃO DE CLIENTES"), ln=True)

        termos_busca = [
            ("Busca por Proximidade ('Empresa / Servico proximo')", "92% dos usuarios clicam nos 3 primeiros resultados do mapa ao buscar por proximidade.", "#1", (22, 128, 61)),
            ("Busca por Categoria Local ('Servicos em Ribeirao Preto')", "Sem Tour 360 e fotos HD, o Google empurra o perfil para baixo fora do raio imediato.", "#12 a #18", (220, 38, 38)),
            ("Busca Direta por Marca ou Nome Especifico", "Cliente digitando o nome exato encontra a ficha, mas falta a experiencia imersiva 360.", "Top 1", (30, 64, 175))
        ]

        y_t_curr = y_termos + 5.5
        for t_tit, t_desc, t_pos, t_color in termos_busca:
            w_card_b = 118.0
            w_quadro_p = 54.0
            h_card_b = 20.0

            set_color_safe(pdf, 248, 250, 252, fn_type='fill')
            set_color_safe(pdf, 226, 232, 240, fn_type='draw')
            _ = pdf.set_line_width(0.3)
            _ = pdf.rounded_rect(21, y_t_curr, w_card_b, h_card_b, 3.0, 'FD')

            set_color_safe(pdf, t_color[0], t_color[1], t_color[2], fn_type='fill')
            _ = pdf.rounded_rect(21, y_t_curr, 2.5, h_card_b, 0.8, 'F')

            _ = pdf.set_xy(26, y_t_curr + 2.5)
            _ = pdf.set_font('Helvetica', 'B', 8.8)
            set_color_safe(pdf, 15, 23, 42, fn_type='text')
            _ = pdf.cell(w_card_b - 8, 3.8, conv(t_tit), border=0, ln=True)

            _ = pdf.set_xy(26, y_t_curr + 7.2)
            _ = pdf.set_font('Helvetica', '', 8.5)
            set_color_safe(pdf, 71, 85, 105, fn_type='text')
            _ = pdf.multi_cell(w_card_b - 10, 3.6, conv(t_desc))

            x_pos_q = 144.0
            set_color_safe(pdf, 255, 255, 255, fn_type='fill')
            set_color_safe(pdf, 226, 232, 240, fn_type='draw')
            _ = pdf.rounded_rect(x_pos_q, y_t_curr, w_quadro_p, h_card_b, 3.0, 'FD')

            _ = pdf.set_xy(x_pos_q, y_t_curr + 2.5)
            _ = pdf.set_font('Helvetica', 'B', 7.8)
            set_color_safe(pdf, 71, 85, 105, fn_type='text')
            _ = pdf.cell(w_quadro_p, 3.0, conv("POSIÇÃO NO RANKING"), align='C', ln=True)

            _ = pdf.set_xy(x_pos_q, y_t_curr + 7.5)
            _ = pdf.set_font('Helvetica', 'B', 15)
            set_color_safe(pdf, t_color[0], t_color[1], t_color[2], fn_type='text')
            _ = pdf.cell(w_quadro_p, 6.0, conv(str(t_pos)), align='C')

            y_t_curr += 22.0

        y_oport = 219.0
        h_oport = 20.0
        set_color_safe(pdf, 239, 246, 255, fn_type='fill')
        set_color_safe(pdf, 191, 219, 254, fn_type='draw')
        _ = pdf.set_line_width(0.3)
        _ = pdf.rounded_rect(21, y_oport, 177, h_oport, 2.0, 'FD')

        set_color_safe(pdf, 30, 64, 175, fn_type='fill')
        _ = pdf.rounded_rect(21, y_oport, 2.5, h_oport, 0.8, 'F')

        tit_oport_alta = "OPORTUNIDADE DE EXPANSAO DE RAIO COM A REESTRUTURACAO PRO + TOUR 360"
        txt_oport_corpo = "A publicacao do Tour Virtual 360 e a otimizacao de metadados visuais expandem a relevancia do perfil no algoritmo do Google. Isso permite captar clientes em um raio de ate 5 km a 10 km, dobrando o volume diario de chamadas e rotas no GPS."

        _ = pdf.set_xy(26, y_oport + 2.8)
        _ = pdf.set_font('Helvetica', 'B', 8.2)
        set_color_safe(pdf, 30, 64, 175, fn_type='text')
        _ = pdf.cell(168, 3.5, conv(tit_oport_alta), ln=True)

        _ = pdf.set_xy(26, y_oport + 7.2)
        _ = pdf.set_font('Helvetica', '', 7.8)
        set_color_safe(pdf, 51, 65, 85, fn_type='text')
        _ = pdf.multi_cell(168, 3.2, conv(txt_oport_corpo), align='L')

    # PÁGINA 4: PROPOSTA COMERCIAL
    if 4 in paginas_selecionadas:
        _ = pdf.add_page()
        
        _ = pdf.set_xy(21, 29.0)
        _ = pdf.set_font('Helvetica', 'B', 15)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(177, 7, conv('PROPOSTA COMERCIAL & ESTRUTURAÇÃO ESTRATÉGICA'), align='C', ln=True)

        _ = pdf.set_y(41.0)
        _ = pdf.set_font('Helvetica', 'B', 12)
        _ = pdf.cell(0, 4, conv('PLANOS E INVESTIMENTO'), align='C', ln=True)

        y_p = 50.0
        w_card = 55.0
        x1, x2, x3 = 21.0, 82.0, 143.0

        def desenhar_pilulas_itens(pdf_obj, x_card, y_top, texto_itens):
            linhas = [l.strip().lstrip('-').strip() for l in texto_itens.split('\n') if l.strip()]
            
            w_pilula = w_card - 8.0
            x_pilula = x_card + 4.0
            h_item = 7.0
            y_curr = y_top

            for lin in linhas:
                set_color_safe(pdf_obj, 248, 250, 252, fn_type='fill')
                set_color_safe(pdf_obj, 226, 232, 240, fn_type='draw')
                _ = pdf_obj.rounded_rect(x_pilula, y_curr, w_pilula, h_item, 1.2, 'FD')
                
                set_color_safe(pdf_obj, 203, 213, 225, fn_type='fill')
                _ = pdf_obj.rounded_rect(x_pilula + 2.5, y_curr + 2.2, 2.5, 2.5, 1.2, 'F')
                
                n_linhas = 1 + (len(lin) // 25)
                offset_text_y = 0.8 if n_linhas > 1 else 2.0
                
                _ = pdf_obj.set_xy(x_pilula + 6.5, y_curr + offset_text_y)
                _ = pdf_obj.set_font('Helvetica', 'B', 7.0)
                set_color_safe(pdf_obj, 51, 65, 85, fn_type='text')
                _ = pdf_obj.multi_cell(w_pilula - 8.0, 2.5, conv(lin), align='L')
                
                y_curr += h_item + 1.0
            return y_curr

        qtd_itens_start = len([l for l in planos.get('start_itens', '').split('\n') if l.strip()])
        qtd_itens_pro = len([l for l in planos.get('pro_itens', '').split('\n') if l.strip()])
        qtd_itens_gestao = len([l for l in planos.get('gestao_itens', '').split('\n') if l.strip()])

        h_card_start = 25.0 + (qtd_itens_start * 8.0) + 4.0
        h_card_pro = 25.0 + (qtd_itens_pro * 8.0) + 4.0
        h_card_gestao = 25.0 + (qtd_itens_gestao * 8.0) + 4.0

        # Card 1: Start
        set_color_safe(pdf, 255, 255, 255, fn_type='fill')
        set_color_safe(pdf, 226, 232, 240, fn_type='draw')
        _ = pdf.set_line_width(0.3)
        _ = pdf.rounded_rect(x1, y_p, w_card, h_card_start, 3.0, 'FD')
        
        _ = pdf.set_xy(x1 + 4, y_p + 3.0)
        _ = pdf.set_font('Helvetica', 'B', 7.5)
        set_color_safe(pdf, 148, 163, 184, fn_type='text')
        _ = pdf.cell(w_card - 8, 3.0, conv('OPÇÃO 1'), ln=True)
        
        _ = pdf.set_xy(x1 + 4, y_p + 6.5)
        _ = pdf.set_font('Helvetica', 'B', 11.5)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(w_card - 8, 4.0, conv('Plano Start'), ln=True)
        
        _ = pdf.set_xy(x1 + 4, y_p + 10.5)
        _ = pdf.set_font('Helvetica', '', 7.5)
        set_color_safe(pdf, 148, 163, 184, fn_type='text')
        _ = pdf.cell(w_card - 8, 3.0, conv('Otimização completa do perfil'), ln=True)
        
        _ = pdf.set_xy(x1 + 4, y_p + 15.5)
        _ = pdf.set_font('Helvetica', 'B', 14.5)
        set_color_safe(pdf, 30, 64, 175, fn_type='text')
        val_start_limpo = str(planos.get('start_valor', '')).replace("/mês", "").replace("/mes", "").strip()
        _ = pdf.cell(w_card - 8, 4.0, conv(f"R$ {val_start_limpo}"), ln=True)
        
        _ = pdf.set_xy(x1 + 4, y_p + 20.0)
        _ = pdf.set_font('Helvetica', 'B', 7.5)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(w_card - 8, 3.0, conv('em até 2x'), ln=True)
        
        desenhar_pilulas_itens(pdf, x1, y_p + 25.0, planos.get('start_itens', ''))

        # Card 2: Pro
        set_color_safe(pdf, 0, 51, 102, fn_type='fill')
        set_color_safe(pdf, 0, 51, 102, fn_type='draw')
        _ = pdf.set_line_width(0.3)
        _ = pdf.rounded_rect(x2, y_p, w_card, h_card_pro, 3.0, 'FD')
        
        w_badge = 36.0
        x_badge = x2 + (w_card - w_badge) / 2.0
        set_color_safe(pdf, 234, 88, 12, fn_type='fill')
        _ = pdf.rounded_rect(x_badge, y_p - 3.0, w_badge, 5.0, 1.5, 'F')
        _ = pdf.set_xy(x_badge, y_p - 2.5)
        _ = pdf.set_font('Helvetica', 'B', 7.0)
        set_color_safe(pdf, 255, 255, 255, fn_type='text')
        _ = pdf.cell(w_badge, 4.0, conv('RECOMENDADO'), align='C')

        _ = pdf.set_xy(x2 + 4, y_p + 3.0)
        _ = pdf.set_font('Helvetica', 'B', 7.5)
        set_color_safe(pdf, 148, 163, 184, fn_type='text')
        _ = pdf.cell(w_card - 8, 3.0, conv('OPÇÃO 2'), ln=True)
        
        _ = pdf.set_xy(x2 + 4, y_p + 6.5)
        _ = pdf.set_font('Helvetica', 'B', 11.5)
        set_color_safe(pdf, 255, 255, 255, fn_type='text')
        _ = pdf.cell(w_card - 8, 4.0, conv('Plano Pro'), ln=True)
        
        _ = pdf.set_xy(x2 + 4, y_p + 10.5)
        _ = pdf.set_font('Helvetica', '', 7.5)
        set_color_safe(pdf, 203, 213, 225, fn_type='text')
        _ = pdf.cell(w_card - 8, 3.0, conv('Otimização + destaque visual'), ln=True)
        
        _ = pdf.set_xy(x2 + 4, y_p + 15.5)
        _ = pdf.set_font('Helvetica', 'B', 14.5)
        set_color_safe(pdf, 255, 255, 255, fn_type='text')
        val_pro_limpo = str(planos.get('pro_valor', '')).replace("/mês", "").replace("/mes", "").strip()
        _ = pdf.cell(w_card - 8, 4.0, conv(f"R$ {val_pro_limpo}"), ln=True)
        
        _ = pdf.set_xy(x2 + 4, y_p + 20.0)
        _ = pdf.set_font('Helvetica', 'B', 7.5)
        set_color_safe(pdf, 203, 213, 225, fn_type='text')
        _ = pdf.cell(w_card - 8, 3.0, conv('em até 3x'), ln=True)

        desenhar_pilulas_itens(pdf, x2, y_p + 25.0, planos.get('pro_itens', ''))

        # Card 3: Gestão Mensal
        set_color_safe(pdf, 255, 255, 255, fn_type='fill')
        set_color_safe(pdf, 226, 232, 240, fn_type='draw')
        _ = pdf.set_line_width(0.3)
        _ = pdf.rounded_rect(x3, y_p, w_card, h_card_gestao, 3.0, 'FD')
        
        _ = pdf.set_xy(x3 + 4, y_p + 3.0)
        _ = pdf.set_font('Helvetica', 'B', 7.5)
        set_color_safe(pdf, 148, 163, 184, fn_type='text')
        _ = pdf.cell(w_card - 8, 3.0, conv('OPÇÃO 3'), ln=True)
        
        _ = pdf.set_xy(x3 + 4, y_p + 6.5)
        _ = pdf.set_font('Helvetica', 'B', 11.5)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(w_card - 8, 4.0, conv('Gestão Mensal'), ln=True)
        
        _ = pdf.set_xy(x3 + 4, y_p + 10.5)
        _ = pdf.set_font('Helvetica', '', 7.5)
        set_color_safe(pdf, 148, 163, 184, fn_type='text')
        _ = pdf.cell(w_card - 8, 3.0, conv('Acompanhamento e relatórios'), ln=True)
        
        _ = pdf.set_xy(x3 + 4, y_p + 15.5)
        _ = pdf.set_font('Helvetica', 'B', 14.5)
        set_color_safe(pdf, 30, 64, 175, fn_type='text')
        val_gestao_limpo = str(planos.get('gestao_valor', '')).replace("/mês", "").replace("/mes", "").strip()
        _ = pdf.cell(w_card - 8, 4.0, conv(f"R$ {val_gestao_limpo}"), ln=True)
        
        _ = pdf.set_xy(x3 + 4, y_p + 20.0)
        _ = pdf.set_font('Helvetica', 'B', 7.5)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(w_card - 8, 3.0, conv('valor mensal'), ln=True)
        
        desenhar_pilulas_itens(pdf, x3, y_p + 25.0, planos.get('gestao_itens', ''))

        # MATRIZ DE AÇÕES DO AGENTE
        y_agente = y_p + max(h_card_start, h_card_pro, h_card_gestao) + 6.0
        w_agente = 177.0
        
        _ = pdf.set_xy(21, y_agente)
        _ = pdf.set_font('Helvetica', 'B', 10.0)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(w_agente, 4.0, conv("AÇÕES DO AGENTE"), ln=True)

        y_tbl_ag = y_agente + 4.5
        
        set_color_safe(pdf, 30, 64, 175, fn_type='fill')
        set_color_safe(pdf, 30, 64, 175, fn_type='draw')
        set_color_safe(pdf, 255, 255, 255, fn_type='text')
        _ = pdf.set_font('Helvetica', 'B', 8.0)
        
        w_c1, w_c2, w_c3, w_c4 = 34.0, 44.0, 44.0, 55.0
        h_header_ag = 4.8

        _ = pdf.set_xy(21, y_tbl_ag)
        _ = pdf.cell(w_c1, h_header_ag, conv(" Dimensão"), border=1, fill=True)
        _ = pdf.cell(w_c2, h_header_ag, conv(" Estado atual"), border=1, fill=True)
        _ = pdf.cell(w_c3, h_header_ag, conv(" Impacto"), border=1, fill=True)
        _ = pdf.cell(w_c4, h_header_ag, conv(" Ação"), border=1, fill=True, ln=True)

        acoes_matriz = [
            ("Completude do cadastro", "Nome e endereço preenchidos, mas faltam descrição e fotos claras.", "Perfil incompleto passa sensação de desorganização ao cliente.", "Adicione descrição concisa com palavras-chave e foto de capa HD."),
            ("Nota e avaliações", f"Nota {dados.get('nota', 0.0):.1f} com histórico recente de comentários sem resposta.", "Nota baixa e falta de resposta afastam novos clientes.", "Responda com empatia a CADA avaliação para recuperar a reputação."),
            ("Consistência NAP", "Telefone cadastrado, website e dados desalinhados nos canais.", "Sem consistência, o Google reduz a relevância nas buscas locais.", "Sincronize telefone, endereço e horários em todas as redes."),
            ("Categorias", "Categorias secundárias ausentes ou muito genéricas.", "Clientes buscam termos específicos e não encontram sua ficha.", "Revise o perfil para incluir categorias específicas do segmento."),
            ("Fotos & Tour 360°", "Apenas fotos estáticas. Nenhum Tour Virtual 360° detectado.", "Clientes não conseguem sentir o ambiente antes da visita.", "Publique o Tour Virtual 360° interativo no Street View do Google."),
            ("Indexação de Imagens AI", "Fotos estáticas genéricas e sem metadados otimizados.", "O Google ignora imagens sem ALT text e SEO de localização.", "Indexe imagens com IA gerando metadados e ALT text otimizados."),
            ("Horários & Exceções", "Horários gerais preenchidos, sem exceções de feriados.", "Surpreende clientes em feriados, gerando deslocamento em vão.", "Mantenha horários preventivamente precisos no Google."),
            ("Posts / Novidades", "Pouca ou nenhuma publicação recente no perfil.", "Perfil estático passa sinal de pouca atividade comercial.", "Publique 1-2 posts por semana convidando a avaliar e visitar."),
            ("Presença local", "Concorrentes locais dominam posições de destaque no mapa.", "Defasagem enorme. Concorrentes captam a maior fatia de tráfego.", "Execute o plano de otimização Pro para liderar o Top 3 da região.")
        ]

        _ = pdf.set_font('Helvetica', '', 7.2)
        y_curr_ag = y_tbl_ag + h_header_ag

        for idx_m, (dim, est, imp, acao) in enumerate(acoes_matriz):
            bg_line = (248, 250, 252) if idx_m % 2 == 0 else (255, 255, 255)
            set_color_safe(pdf, bg_line, fn_type='fill')
            set_color_safe(pdf, 226, 232, 240, fn_type='draw')
            set_color_safe(pdf, 51, 65, 85, fn_type='text')
            
            n_l1 = max(1, int(len(dim) / 18.0 + 0.95))
            n_l2 = max(1, int(len(est) / 24.0 + 0.95))
            n_l3 = max(1, int(len(imp) / 24.0 + 0.95))
            n_l4 = max(1, int(len(acao) / 30.0 + 0.95))
            
            linhas_max = max(n_l1, n_l2, n_l3, n_l4)
            h_linha_dinamica = max(7.2, (linhas_max * 2.8) + 1.8)

            _ = pdf.rect(21, y_curr_ag, w_c1, h_linha_dinamica, 'FD')
            _ = pdf.rect(21 + w_c1, y_curr_ag, w_c2, h_linha_dinamica, 'FD')
            _ = pdf.rect(21 + w_c1 + w_c2, y_curr_ag, w_c3, h_linha_dinamica, 'FD')
            _ = pdf.rect(21 + w_c1 + w_c2 + w_c3, y_curr_ag, w_c4, h_linha_dinamica, 'FD')

            _ = pdf.set_xy(22, y_curr_ag + ((h_linha_dinamica - (n_l1 * 2.8)) / 2.0))
            _ = pdf.multi_cell(w_c1 - 2.0, 2.8, conv(dim), border=0, align='L')
            
            _ = pdf.set_xy(21 + w_c1 + 1.5, y_curr_ag + ((h_linha_dinamica - (n_l2 * 2.8)) / 2.0))
            _ = pdf.multi_cell(w_c2 - 3.0, 2.8, conv(est), border=0, align='L')
            
            _ = pdf.set_xy(21 + w_c1 + w_c2 + 1.5, y_curr_ag + ((h_linha_dinamica - (n_l3 * 2.8)) / 2.0))
            _ = pdf.multi_cell(w_c3 - 3.0, 2.8, conv(imp), border=0, align='L')
            
            _ = pdf.set_xy(21 + w_c1 + w_c2 + w_c3 + 1.5, y_curr_ag + ((h_linha_dinamica - (n_l4 * 2.8)) / 2.0))
            _ = pdf.multi_cell(w_c4 - 3.0, 2.8, conv(acao), border=0, align='L')
            
            y_curr_ag += h_linha_dinamica
            _ = pdf.set_xy(21, y_curr_ag)

    # PÁGINA 5: CONTRATO
    if 5 in paginas_selecionadas:
        _ = pdf.add_page()
        
        _ = pdf.set_xy(21, 29.0)
        _ = pdf.set_font('Helvetica', 'B', 15)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(177, 7, conv('CONTRATO DE PRESTAÇÃO DE SERVIÇOS'), align='C', ln=True)

        _ = pdf.set_y(42.0)
        w_text, h_line = 177, 4.8

        nome_cli = str(dados.get('nome') or 'Empresa Contratante')
        resp_cli = str(dados.get('contato') or 'Responsável')
        end_cli = str(dados.get('endereco') or 'Endereço não informado')
        tel_cli = str(dados.get('telefone') or 'N/I')

        def renderizar_clausula(pdf_obj, titulo_bold, corpo_normal, espaco_extra=2.5, alinhamento='J'):
            pdf_obj.set_x(21)
            pdf_obj.set_font('Helvetica', 'B', 9.5)
            set_color_safe(pdf_obj, 15, 23, 42, fn_type='text')
            pdf_obj.write(h_line, conv(titulo_bold + " "))
            
            pdf_obj.set_font('Helvetica', '', 9.5)
            set_color_safe(pdf_obj, 51, 65, 85, fn_type='text')
            
            partes = re.split(r'(CONTRATADA|CONTRATANTE)', corpo_normal)
            for p in partes:
                if p in ['CONTRATADA', 'CONTRATANTE']:
                    pdf_obj.set_font('Helvetica', 'B', 9.5)
                    set_color_safe(pdf_obj, 15, 23, 42, fn_type='text')
                    pdf_obj.write(h_line, conv(p))
                    pdf_obj.set_font('Helvetica', '', 9.5)
                    set_color_safe(pdf_obj, 51, 65, 85, fn_type='text')
                else:
                    pdf_obj.write(h_line, conv(p))
            
            pdf_obj.ln(h_line + espaco_extra)

        renderizar_clausula(
            pdf,
            "CONTRATADA:",
            "Tour360VR, representada por Rubens Okamoto, CNPJ: 04.824.331/0001-05 e Telefone: (16) 99133-2121."
        )

        renderizar_clausula(
            pdf,
            "CONTRATANTE:",
            f"{nome_cli}, representada por {resp_cli}, localizada em {end_cli}, Telefone: {tel_cli}."
        )

        _ = pdf.set_x(21)
        _ = pdf.set_font('Helvetica', '', 9.5)
        set_color_safe(pdf, 51, 65, 85, fn_type='text')
        _ = pdf.write(h_line, conv("A "))
        _ = pdf.set_font('Helvetica', 'B', 9.5)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.write(h_line, conv("CONTRATADA "))
        _ = pdf.set_font('Helvetica', '', 9.5)
        set_color_safe(pdf, 51, 65, 85, fn_type='text')
        _ = pdf.write(h_line, conv("compromete-se a executar os serviços de otimização, reestruturação técnica e/ou produção de Tour Virtual 360° para o perfil do Google da "))
        _ = pdf.set_font('Helvetica', 'B', 9.5)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.write(h_line, conv("CONTRATANTE."))
        _ = pdf.ln(h_line + 2.5)

        renderizar_clausula(
            pdf,
            "CLÁUSULA PRIMEIRA - DO OBJETO:",
            "Os serviços serão iniciados em até 5 dias úteis após o fornecimento de todos os acessos e informações necessárias à gestão do perfil."
        )

        renderizar_clausula(
            pdf,
            "CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES:",
            "O não pagamento no prazo pactuado sujeitará o presente contrato à incidência de juros moratórios legais e à suspensão temporária dos serviços até a devida regularização."
        )

        renderizar_clausula(
            pdf,
            "CLÁUSULA TERCEIRA - DOS DIREITOS DE USO E PROPRIEDADE:",
            "Os direitos de uso do Tour Virtual 360° e fotos HD serão cedidos em caráter ilimitado à CONTRATANTE para veiculação no Google. A CONTRATADA reserva-se o direito de utilizar o material em seu portfólio de divulgação."
        )

        renderizar_clausula(
            pdf,
            "CLÁUSULA QUARTA - CONFIDENCIALIDADE E LGPD:",
            "As partes comprometem-se a manter sob sigilo absoluto todas as informações operacionais fornecidas, em conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018)."
        )

        renderizar_clausula(
            pdf,
            "CLÁUSULA QUINTA - VALIDADE DA PROPOSTA:",
            "A presente proposta e condições comerciais possuem validade de 15 (quinze) dias a contar da data de sua emissão."
        )

        _ = pdf.set_x(21)
        _ = pdf.set_font('Helvetica', 'B', 9.5)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(w_text, h_line, conv("CLÁUSULA SEXTA - SELEÇÃO DO PLANO CONTRATADO:"), ln=True)
        
        _ = pdf.set_x(21)
        _ = pdf.set_font('Helvetica', '', 9.5)
        set_color_safe(pdf, 51, 65, 85, fn_type='text')
        _ = pdf.cell(w_text, 4.5, conv("(   ) Plano Start          (   ) Plano Pro          (   ) Gestão Mensal          (   ) Plano de: _____ meses"), ln=True)
        _ = pdf.ln(2.0)

        _ = pdf.set_x(21)
        _ = pdf.set_font('Helvetica', 'B', 9.5)
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        _ = pdf.cell(w_text, h_line, conv("CLÁUSULA SÉTIMA - CONDIÇÕES DE PAGAMENTO:"), ln=True)
        
        _ = pdf.set_x(21)
        _ = pdf.set_font('Helvetica', '', 9.5)
        set_color_safe(pdf, 51, 65, 85, fn_type='text')
        _ = pdf.cell(w_text, 4.5, conv("(   ) À Vista          (   ) 2x Plano Start          (   ) 3x Plano Pro          (   ) Vencimento todo dia: _____ - Gestão Mensal"), ln=True)

        _ = pdf.ln(14)
        y_ass = pdf.get_y()
        
        set_color_safe(pdf, 15, 23, 42, fn_type='draw')
        set_color_safe(pdf, 15, 23, 42, fn_type='text')
        
        _ = pdf.set_xy(21, y_ass)
        _ = pdf.cell(83, 5, '_____________________________________', align='C')
        _ = pdf.set_xy(115, y_ass)
        _ = pdf.cell(83, 5, '_____________________________________', align='C', ln=True)
        
        _ = pdf.set_font('Helvetica', 'B', 9.5)
        _ = pdf.set_x(21)
        _ = pdf.cell(83, 4.5, 'Rubens Okamoto', align='C')
        _ = pdf.set_x(115)
        _ = pdf.cell(83, 4.5, conv(resp_cli), align='C', ln=True)
        
        _ = pdf.set_font('Helvetica', '', 9.5)
        set_color_safe(pdf, 51, 65, 85, fn_type='text')
        _ = pdf.set_x(21)
        _ = pdf.cell(83, 4.5, 'Tour360VR', align='C')
        _ = pdf.set_x(115)
        _ = pdf.cell(83, 4.5, conv(nome_cli), align='C', ln=True)

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
            <div class="sidebar-title-top">Consultoria e Diagnóstico</div>
            <img src="{b64_tour}" class="logo-tour" alt="Tour360VR" />
            <img src="{b64_okamoto}" class="logo-okamoto" alt="Okamoto Mídias Visuais" />
        </div>
        <div class="sidebar-divider"></div>
        <div class="label-cliente-centralizado">Cliente em Atendimento</div>
        <div class="box-cliente-atendimento">🏢 {st.session_state['dados'].get('nome') or "Nenhum cliente"}</div>
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
                <span>Diagnóstico de pontuação:</span>
                <span style="color: {cor_score};">{score_atual}/100 ({status_txt})</span>
            </div>
            <div style="background-color: #1e293b; border-radius: 4px; height: 8px; width: 100%; overflow: hidden; border: 1px solid #334155;">
                <div style="background-color: {cor_score}; height: 100%; width: {score_atual}%; transition: width 0.4s ease;"></div>
            </div>
        </div>
        <div class="sidebar-divider"></div>
    """, unsafe_allow_html=True)

    if st.button("🧹 Iniciar Novo Atendimento", use_container_width=True, type="secondary"):
        st.session_state['etapa_atual'] = 1
        st.session_state['dados'] = {
            "nome": "", "contato": "", "endereco": "", "telefone": "", "website": "",
            "nota": 0.0, "avaliacoes": 0, "tem_tour360": False, "tem_fotos_hd": False,
            "categorias_completas": False, "horarios_ok": False, "tem_descricao": False,
            "atributos_ok": False, "resposta_avaliacoes_ok": False, "categorias_detectadas": [], "foto_reference": "",
            "lat": None, "lng": None
        }
        st.session_state['concorrentes'] = [
            {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"},
            {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"},
            {"nome": "", "nota": 0.0, "avaliacoes": 0, "busca_termo": "", "cidade": "", "tem_fotos_hd": "Não", "tem_tour360": "Não", "categorias_ok": "Não", "horarios_ok": "Não", "tem_website": "Não", "tem_descricao": "Não", "atributos_ok": "Não", "respostas_ok": "Não"}
        ]
        st.session_state['planos'] = {
            "start_valor": "500,00", "start_itens": "Preenchimento completo do perfil\nDescrição profissional com palavras-chave\nCategorias corretas + secundárias\nPadronização de dados: NAP, horários, serviços",
            "pro_valor": "1.500,00", "pro_itens": "Preenchimento completo do perfil\nDescrição profissional com palavras-chave\nCategorias corretas + secundárias\nPadronização de dados: NAP, horários, serviços\nSessão de fotos\nTour Virtual 360°\nFotos 360° para Street View\nIndexação de Fotos & Image SEO AI",
            "gestao_valor": "600,00", "gestao_itens": "Postagens semanais\nGestão de avaliações\nAtualização de fotos\nRelatório mensal\nOtimização Contínua por IA"
        }
        st.session_state['plano_acao_extra'] = TEXTO_PLANO_ACAO_PADRAO
        st.rerun()

# -----------------------------------------------------------------------------
# 7. BARRA DE ETAPAS CLICÁVEIS
# -----------------------------------------------------------------------------
etapa_atual = st.session_state['etapa_atual']

col_e1, col_e2, col_e3, col_e4, col_e5 = st.columns(5)

with col_e1:
    type_e1 = "primary" if etapa_atual == 1 else "secondary"
    if st.button("1. Busca & Ficha", use_container_width=True, type=type_e1, key="btn_e1"):
        st.session_state['etapa_atual'] = 1
        st.rerun()

with col_e2:
    type_e2 = "primary" if etapa_atual == 2 else "secondary"
    if st.button("2. Concorrentes", use_container_width=True, type=type_e2, key="btn_e2"):
        st.session_state['etapa_atual'] = 2
        st.rerun()

with col_e3:
    type_e3 = "primary" if etapa_atual == 3 else "secondary"
    if st.button("3. Plano de Ação", use_container_width=True, type=type_e3, key="btn_e3"):
        st.session_state['etapa_atual'] = 3
        st.rerun()

with col_e4:
    type_e4 = "primary" if etapa_atual == 4 else "secondary"
    if st.button("4. Valores", use_container_width=True, type=type_e4, key="btn_e4"):
        st.session_state['etapa_atual'] = 4
        st.rerun()

with col_e5:
    type_e5 = "primary" if etapa_atual == 5 else "secondary"
    if st.button("5. PDF & Ações", use_container_width=True, type=type_e5, key="btn_e5"):
        st.session_state['etapa_atual'] = 5
        st.rerun()

# -----------------------------------------------------------------------------
# 8. FLUXO SEQUENCIAL DAS ETAPAS
# -----------------------------------------------------------------------------

# ETAPA 1: BUSCA & DIAGNÓSTICO DA FICHA
if etapa_atual == 1:
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.markdown("<div class='dashboard-card'><div class='card-title'>🔍 1. BUSCA DA FICHA NO GOOGLE MAPS</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([2, 1])
        nome_input = c1.text_input("Nome da Empresa:", value="", placeholder="Ex: Taiwan Hotel Ltda", key="input_empresa_nome")
        cidade_empresa = c2.text_input("Cidade/Região:", value="", placeholder="Ex: Ribeirão Preto, SP", key="input_empresa_cidade")
            
        if st.button("🚀 Pesquisar Ficha no Google", use_container_width=True, key="btn_busca_google", type="secondary"):
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
            
            if st.button("📌 Carregar Dados da Unidade", use_container_width=True, key="btn_carregar_unidade", type="secondary"):
                idx = opcoes.index(escolha)
                u = st.session_state['unidades_encontradas'][idx]
                place_id = u.get("place_id")
                
                if API_KEY_GOOGLE:
                    try:
                        url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,international_phone_number,website,rating,user_ratings_total,photos,opening_hours,types,editorial_summary,geometry&key={API_KEY_GOOGLE}"
                        res_details = requests.get(url_details).json().get("result", {})
                        
                        photos = res_details.get("photos", u.get("photos", []))
                        types_lista = res_details.get("types", [])
                        loc_geo = res_details.get("geometry", {}).get("location", {})
                        
                        st.session_state['dados']['nome'] = res_details.get("name") or u.get("name") or nome_input
                        st.session_state['dados']['endereco'] = res_details.get("formatted_address") or u.get("formatted_address") or ""
                        st.session_state['dados']['telefone'] = res_details.get("formatted_phone_number") or res_details.get("international_phone_number") or ""
                        st.session_state['dados']['website'] = res_details.get("website") or ""
                        st.session_state['dados']['nota'] = float(res_details.get("rating") or u.get("rating") or 0.0)
                        st.session_state['dados']['avaliacoes'] = int(res_details.get("user_ratings_total") or u.get("user_ratings_total") or 0)
                        st.session_state['dados']['contato'] = "Gerente Responsável"
                        
                        st.session_state['dados']['lat'] = loc_geo.get("lat")
                        st.session_state['dados']['lng'] = loc_geo.get("lng")
                        
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

        st.markdown("<div class='card-title' style='margin-top:15px;'>CHECKLIST DE PONTOS CRÍTICOS</div>", unsafe_allow_html=True)
        
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
        st.markdown("<div class='dashboard-card'><div class='card-title'>DADOS DO CLIENTE</div>", unsafe_allow_html=True)
        st.session_state['dados']['nome'] = st.text_input("Empresa:", value=st.session_state['dados']['nome'])
        st.session_state['dados']['contato'] = st.text_input("Responsável:", value=st.session_state['dados']['contato'])
        st.session_state['dados']['telefone'] = st.text_input("Telefone:", value=st.session_state['dados']['telefone'])
        st.session_state['dados']['website'] = st.text_input("Website:", value=st.session_state['dados']['website'])
        st.session_state['dados']['endereco'] = st.text_area("Endereço:", value=st.session_state['dados']['endereco'], height=80)
        st.markdown("</div>", unsafe_allow_html=True)

    col_nav1, col_nav2 = st.columns([2, 1])
    with col_nav2:
        if st.button("Avançar para Concorrentes ➡️", use_container_width=True, key="btn_nav_aba1", type="secondary"):
            st.session_state['etapa_atual'] = 2
            st.rerun()

# ETAPA 2: AVALIAÇÃO DE CONCORRENTES
elif etapa_atual == 2:
    st.markdown("<div class='dashboard-card'><div class='card-title'>⚔️ 2. AVALIAÇÃO DE CONCORRENTES DO SEGMENTO</div>", unsafe_allow_html=True)
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
        st.markdown("<div style='margin-top:10px;'><b>Resultado da Consulta:</b></div>", unsafe_allow_html=True)
        for c_item in concorrentes_validos:
            score_c = calcular_score_concorrente(c_item)
            st.markdown(f"• **{c_item['nome']}** — ⭐ Nota: `{float(c_item.get('nota', 0.0)):.1f}` ({c_item.get('avaliacoes', 0)} avaliada(s)) | Score: **{score_c}/100**")

    st.markdown("</div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("⬅️ Voltar para Busca", use_container_width=True, key="btn_nav_aba2_back", type="secondary"):
            st.session_state['etapa_atual'] = 1
            st.rerun()
    with col_btn2:
        if st.button("Avançar para Plano de Ação ➡️", use_container_width=True, key="btn_nav_aba2_next", type="secondary"):
            st.session_state['etapa_atual'] = 3
            st.rerun()

# ETAPA 3: PLANO DE AÇÃO ESTRATÉGICO
elif etapa_atual == 3:
    st.markdown("<div class='dashboard-card'><div class='card-title'>💡 3. APONTAMENTOS ESTRATÉGICOS E PLANO DE AÇÃO</div>", unsafe_allow_html=True)
    st.caption("Texto personalizado que aparecerá no quadro em destaque na Página 2 do PDF.")
    
    st.session_state['plano_acao_extra'] = st.text_area(
        "Edite o plano de ação personalizado:",
        value=st.session_state['plano_acao_extra'],
        height=180
    )
    st.markdown("</div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("⬅️ Voltar para Concorrentes", use_container_width=True, key="btn_nav_aba3_back", type="secondary"):
            st.session_state['etapa_atual'] = 2
            st.rerun()
    with col_btn2:
        if st.button("Avançar para Planos & Valores ➡️", use_container_width=True, key="btn_nav_aba3_next", type="secondary"):
            st.session_state['etapa_atual'] = 4
            st.rerun()

# ETAPA 4: PLANOS & VALORES COMERCIAIS
elif etapa_atual == 4:
    st.markdown("<div class='dashboard-card'><div class='card-title'>📜 4. PLANOS COMERCIAIS & INVESTIMENTO</div>", unsafe_allow_html=True)
    
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("#### 🔹 Plano Start")
        st.session_state['planos']['start_valor'] = st.text_input("Valor (R$):", value=st.session_state['planos']['start_valor'], key="p_s_v")
        st.session_state['planos']['start_itens'] = st.text_area("Itens:", value=st.session_state['planos']['start_itens'], height=180, key="p_s_i")
    with p2:
        st.markdown("#### 🔹 Plano Pro")
        st.session_state['planos']['pro_valor'] = st.text_input("Valor (R$):", value=st.session_state['planos']['pro_valor'], key="p_p_v")
        st.session_state['planos']['pro_itens'] = st.text_area("Itens:", value=st.session_state['planos']['pro_itens'], height=180, key="p_p_i")
    with p3:
        st.markdown("#### 🔹 Gestão Mensal")
        st.session_state['planos']['gestao_valor'] = st.text_input("Valor (R$):", value=st.session_state['planos']['gestao_valor'], key="p_g_v")
        st.session_state['planos']['gestao_itens'] = st.text_area("Itens:", value=st.session_state['planos']['gestao_itens'], height=180, key="p_g_i")

    st.markdown("</div>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("⬅️ Voltar para Plano de Ação", use_container_width=True, key="btn_nav_aba4_back", type="secondary"):
            st.session_state['etapa_atual'] = 3
            st.rerun()
    with col_btn2:
        if st.button("Avançar para PDF & Ações ➡️", use_container_width=True, key="btn_nav_aba4_next", type="secondary"):
            st.session_state['etapa_atual'] = 5
            st.rerun()

# ETAPA 5: GERAR PDF
elif etapa_atual == 5:
    st.markdown("<div class='dashboard-card'><div class='card-title'>📄 5. EMISSÃO, ABORDAGEM & INTEGRAÇÃO CRM</div>", unsafe_allow_html=True)
    
    st.markdown("#### ⚙️ Selecione as Páginas a Incluir no PDF:")
    c_pag1, c_pag2, c_pag3, c_pag4, c_pag5 = st.columns(5)
    
    inc_p1 = c_pag1.checkbox("Pág 1 (Capa)", value=True, key="chk_p1")
    inc_p2 = c_pag2.checkbox("Pág 2 (Auditoria)", value=True, key="chk_p2")
    inc_p3 = c_pag3.checkbox("Pág 3 (Mapa/Raio)", value=True, key="chk_p3")
    inc_p4 = c_pag4.checkbox("Pág 4 (Proposta)", value=False, key="chk_p4")
    inc_p5 = c_pag5.checkbox("Pág 5 (Contrato)", value=False, key="chk_p5")

    paginas_escolhidas = []
    if inc_p1: paginas_escolhidas.append(1)
    if inc_p2: paginas_escolhidas.append(2)
    if inc_p3: paginas_escolhidas.append(3)
    if inc_p4: paginas_escolhidas.append(4)
    if inc_p5: paginas_escolhidas.append(5)

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
            f"Meu nome é Rubens Okamoto, da Okamoto Mídias Visuais e do Tour360VR.\n\n"
            f"Estava analisando a presença da {nome_empresa_formatado} no Google Maps e identifiquei 3 pontos onde a visibilidade do espaço de vocês pode ser bastante ampliada em relação aos concorrentes da região.\n\n"
            f"Montei um relatório curto de diagnóstico em PDF. Posso te enviar por aqui para você dar uma olhada?"
        )

        st.markdown("<br><b>📝 Mensagem de Abordagem (Editável):</b>", unsafe_allow_html=True)
        mensagem_editada = st.text_area(
            "Edite a mensagem antes de abrir o WhatsApp:",
            value=texto_padrao_whatsapp,
            height=120,
            key="area_msg_whatsapp_wizard"
        )

        msg_encoded = requests.utils.quote(mensagem_editada)
        link_wa = f"https://wa.me/{tel_cliente}?text={msg_encoded}" if tel_cliente else f"https://wa.me/?text={msg_encoded}"

        col_down1, col_down2, col_down3 = st.columns(3)
        
        pdf_bytes = None
        try:
            pdf_bytes = gerar_pdf_oficial(
                st.session_state['dados'], 
                st.session_state['planos'], 
                st.session_state.get('plano_acao_extra', ''), 
                st.session_state.get('concorrentes', []),
                paginas_selecionadas=paginas_escolhidas
            )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")

        tipo_doc = "Diagnóstico Preliminar" if len(paginas_escolhidas) <= 3 else "Diagnóstico e Proposta"

        if pdf_bytes:
            with col_down1:
                st.download_button(
                    label=f"📥 Baixar PDF ({len(paginas_escolhidas)} Pág(s))",
                    data=pdf_bytes,
                    file_name=f"{tipo_doc} {nome_empresa_formatado}.pdf",
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

            with col_down3:
                if st.button("📧 Enviar para Meu E-mail & Bigin", use_container_width=True, type="primary", key="btn_enviar_admin_bigin"):
                    score_calc = calcular_score_real(st.session_state['dados'])
                    with st.spinner("Enviando e-mail de notificação e registrando no Bigin..."):
                        sucesso_email, msg_email = enviar_email_admin_com_pdf(st.session_state['dados'], score_calc, pdf_bytes)
                        sucesso_bigin = enviar_lead_zoho_bigin(st.session_state['dados'], score_calc)

                    if sucesso_email:
                        st.success("✅ E-mail com o PDF enviado para contato@tour360vr.com.br!")
                    else:
                        st.error(f"❌ Erro no e-mail: {msg_email}")

                    if sucesso_bigin:
                        st.success("✅ Lead registrado no Zoho Bigin!")
                    else:
                        st.warning("⚠️ Não foi possível salvar automaticamente no Bigin.")

    st.markdown("</div>", unsafe_allow_html=True)

    col_nav1, col_nav2 = st.columns([1, 2])
    with col_nav1:
        if st.button("⬅️ Voltar para Ajuste de Valores", use_container_width=True, key="btn_nav_aba5_back", type="secondary"):
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

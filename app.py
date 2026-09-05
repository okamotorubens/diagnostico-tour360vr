import io
import os
import requests
import streamlit as st
from fpdf import FPDF

# -----------------------------------------------------------------------------
# 1. CONFIGURAÃ‡ÃƒO DA PÃGINA E IDENTIDADE VISUAL TOUR360VR
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tour360VR - Plataforma de Consultoria e DiagnÃ³stico",
    page_icon="ðŸŒ",
    layout="wide"
)

# Cores extraÃ­das diretamente da logo (Logo_TOUR_transparente.png), para que
# a identidade visual do PDF e da interface fique fiel Ã  marca.
BRAND = {
    "vermelho": (255, 49, 49),    # #FF3131 - texto "TOUR 360 VR" / cor primÃ¡ria
    "coral":    (250, 107, 69),   # #FA6B45 - arco da logo
    "laranja":  (255, 165, 48),   # #FFA530 - arco da logo
    "azul":     (72, 165, 217),   # #48A5D9 - arco da logo
    "verde":    (159, 189, 89),   # #9FBD59 - arco da logo
    "texto_escuro": (15, 23, 42),
    "texto_medio": (71, 85, 105),
    "linha": (226, 232, 240),
    "fundo_claro": (248, 250, 252),
}

# As 4 cores do arco da logo tambÃ©m definem os 4 nÃ­veis de status do
# diagnÃ³stico, para que a mesma paleta apareÃ§a em toda a ferramenta.
NIVEIS = [
    (0,  40, "CRÃTICO",   BRAND["vermelho"]),
    (40, 70, "ATENÃ‡ÃƒO",   BRAND["laranja"]),
    (70, 90, "BOM",       BRAND["azul"]),
    (90, 101, "EXCELENTE", BRAND["verde"]),
]

HEX = {k: "#%02x%02x%02x" % v for k, v in BRAND.items()}

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0f172a; color: #f8fafc; }}

    .header-box {{
        border-bottom: 2px solid {HEX['azul']};
        padding-bottom: 12px;
        margin-bottom: 25px;
    }}
    .header-title {{ color: #ffffff; font-size: 26px; font-weight: 700; margin: 0; }}
    .header-title span {{ color: {HEX['vermelho']}; }}
    .header-subtitle {{ color: {HEX['azul']}; font-size: 14px; font-weight: 600; margin-top: 4px; }}

    .card-dark {{
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }}
    .score-card {{
        background-color: #1e293b;
        border: 2px solid {HEX['azul']};
        padding: 20px;
        border-radius: 8px;
        text-align: center;
    }}

    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0b0f19;
        color: #94a3b8;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #1e293b;
        font-size: 12px;
        z-index: 100;
    }}
    </style>
""", unsafe_allow_html=True)

API_KEY_GOOGLE = st.secrets.get("GOOGLE_PLACES_API_KEY", "")

# Resolve o caminho da logo de forma robusta (evita o bug do arquivo "sumido"
# por causa de espaÃ§o/underscore no nome ou pasta diferente em produÃ§Ã£o).
def caminho_logo():
    candidatos = [
        "assets/Logo_TOUR_transparente.png",
        "Logo_TOUR_transparente.png",
        "Logo TOUR transparente.png",
        os.path.join(os.path.dirname(__file__), "assets", "Logo_TOUR_transparente.png"),
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    return None

LOGO_PATH = caminho_logo()

# -----------------------------------------------------------------------------
# INICIALIZAÃ‡ÃƒO DE ESTADOS EDITÃVEIS
# -----------------------------------------------------------------------------
if 'dados' not in st.session_state:
    st.session_state['dados'] = {
        "nome": "Toque de Letra",
        "contato": "Marcio Javaroni",
        "endereco": "RibeirÃ£o Preto / SP",
        "telefone": "16 99622 2121",
        "website": "NÃ£o possui",
        "nota": 4.2,
        "avaliacoes": 38,
        "tem_tour360": False,
        "tem_fotos_hd": False,
        "categorias_completas": False,
        "horarios_ok": False,
        "foto_reference": None,   # referÃªncia da foto no Google Places
        "foto_bytes": None,       # bytes da foto jÃ¡ baixada (cache em sessÃ£o)
    }

if 'planos' not in st.session_state:
    st.session_state['planos'] = {
        "start_valor": "500,00",
        "start_itens": "- CorreÃ§Ã£o cadastral\n- OtimizaÃ§Ã£o de SEO\n- Ajuste de categorias\n- InserÃ§Ã£o de links",
        "pro_valor": "1.150,00",
        "pro_itens": "- Tudo do Plano Start\n- Tour Virtual 360Â°\n- Ensaio FotogrÃ¡fico HD\n- RelatÃ³rio Visual de Entrega",
        "gestao_valor": "600,00/mÃªs",
        "gestao_itens": "- Postagens semanais\n- GestÃ£o de avaliaÃ§Ãµes\n- AtualizaÃ§Ã£o de fotos\n- RelatÃ³rio mensal"
    }

if 'plano_acao_extra' not in st.session_state:
    st.session_state['plano_acao_extra'] = "VocÃª precisa de mim."


def conv(texto):
    """Trata a codificaÃ§Ã£o para Latin-1 e substitui sÃ­mbolos unicode incompatÃ­veis."""
    if not texto:
        return ""
    limpo = str(texto)
    limpo = limpo.replace("â€¢", "- ").replace("âœ“", "[OK] ").replace("X", "[X] ")
    limpo = (limpo.replace("ðŸ“", "").replace("ðŸ“ž", "").replace("â­", "*")
                  .replace("âœ‰ï¸", "").replace("ðŸŒ", "").replace("â˜…", "*")
                  .replace("â˜†", "").replace("â˜", "[ ]"))
    return limpo.encode('latin-1', 'replace').decode('latin-1')


# -----------------------------------------------------------------------------
# 2. PONTUAÃ‡ÃƒO â€” FONTE ÃšNICA DE VERDADE
#    (antes, o score geral e os percentuais de cada item do PDF eram
#    calculados por fÃ³rmulas diferentes e nunca batiam entre si)
# -----------------------------------------------------------------------------
ITENS_CONFIG = [
    {"chave": "tem_tour360", "nome": "Tour Virtual 360Â° Interativo", "peso": 25,
     "desc_ok": "Tour 360Â° publicado e integrado ao perfil.",
     "desc_falta": "Nenhum Tour 360Â° detectado no perfil."},
    {"chave": "website", "nome": "Website e Links de ConversÃ£o", "peso": 20, "tipo": "website",
     "desc_ok": "Site e links diretos de contato cadastrados.",
     "desc_falta": "Sem site ou links diretos de contato/WhatsApp."},
    {"chave": "tem_fotos_hd", "nome": "Fotos em Alta ResoluÃ§Ã£o", "peso": 20,
     "desc_ok": "Fotos profissionais em HD publicadas.",
     "desc_falta": "Poucas fotos ou fotos em baixa resoluÃ§Ã£o."},
    {"chave": "categorias_completas", "nome": "Categorias Principal e SecundÃ¡rias", "peso": 15,
     "desc_ok": "Categorias principal e secundÃ¡rias bem definidas.",
     "desc_falta": "Sem categorias secundÃ¡rias estratÃ©gicas."},
    {"chave": "horarios_ok", "nome": "HorÃ¡rios e ExceÃ§Ãµes (Feriados)", "peso": 10,
     "desc_ok": "HorÃ¡rios completos e atualizados.",
     "desc_falta": "Falta de horÃ¡rios especiais em feriados."},
    {"chave": "avaliacoes", "nome": "AvaliaÃ§Ãµes no Google (Prova Social)", "peso": 10, "tipo": "avaliacoes",
     "desc_ok": "Volume de avaliaÃ§Ãµes saudÃ¡vel.",
     "desc_falta": "Poucas avaliaÃ§Ãµes registradas."},
]


def classificar_status(score):
    for minimo, maximo, label, cor in NIVEIS:
        if minimo <= score < maximo:
            return label, cor
    return NIVEIS[-1][2], NIVEIS[-1][3]


def calcular_diagnostico(dados):
    """Retorna (score, itens) onde cada item jÃ¡ traz seu percentual atingido,
    calculado com o MESMO peso usado para compor o score final."""
    itens = []
    pontos_totais = 0.0
    for cfg in ITENS_CONFIG:
        if cfg.get("tipo") == "website":
            atingiu = dados.get("website", "NÃ£o possui") != "NÃ£o possui"
            pct = 100 if atingiu else 0
        elif cfg.get("tipo") == "avaliacoes":
            qtd = dados.get("avaliacoes", 0) or 0
            pct = min(int((qtd / 50.0) * 100), 100) if qtd > 0 else 0
            atingiu = pct >= 100
        else:
            atingiu = bool(dados.get(cfg["chave"]))
            pct = 100 if atingiu else 0

        pontos = cfg["peso"] * pct / 100.0
        pontos_totais += pontos
        itens.append({
            "nome": cfg["nome"],
            "peso": cfg["peso"],
            "pct": pct,
            "atingiu": atingiu,
            "desc": cfg["desc_ok"] if atingiu else cfg["desc_falta"],
        })

    score = round(pontos_totais)
    return score, itens


# -----------------------------------------------------------------------------
# 2b. BUSCA DA FOTO DO PERFIL NO GOOGLE (Places Photo API)
# -----------------------------------------------------------------------------
def baixar_foto_google(photo_reference, api_key, maxwidth=800):
    if not photo_reference or not api_key:
        return None
    try:
        url = (
            "https://maps.googleapis.com/maps/api/place/photo"
            f"?maxwidth={maxwidth}&photoreference={photo_reference}&key={api_key}"
        )
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and resp.content:
            return resp.content
    except Exception:
        pass
    return None


# -----------------------------------------------------------------------------
# 3. GERADOR DE PDF TOUR360VR
# -----------------------------------------------------------------------------
class PDFTour360Oficial(FPDF):

    def faixa_marca(self, y, altura=3.5):
        """Faixa com as 4 cores do arco da logo, na mesma ordem do sÃ­mbolo."""
        cores = [BRAND["laranja"], BRAND["azul"], BRAND["coral"], BRAND["verde"]]
        largura_total = 210
        largura_seg = largura_total / 4.0
        for i, cor in enumerate(cores):
            self.set_fill_color(*cor)
            self.rect(i * largura_seg, y, largura_seg, altura, 'F')

    def header(self):
        self.faixa_marca(0)
        if self.page_no() == 1:
            return  # a capa tem seu prÃ³prio cabeÃ§alho com a logo grande

        x_pos = 12
        if LOGO_PATH:
            try:
                self.image(LOGO_PATH, 12, 8, 16)
                x_pos = 32
            except Exception:
                x_pos = 12

        self.set_xy(x_pos, 8.5)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(*BRAND["vermelho"])
        self.cell(0, 5, 'TOUR360VR', ln=True)
        self.set_xy(x_pos, 14.5)
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(*BRAND["texto_medio"])
        self.cell(0, 4, conv('GestÃ£o de Perfil & DiagnÃ³stico do Google Meu NegÃ³cio'), ln=True)

        self.set_draw_color(*BRAND["linha"])
        self.set_line_width(0.3)
        self.line(12, 22, 198, 22)
        self.set_line_width(0.2)
        self.ln(19)

    def footer(self):
        self.set_y(-17)
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(*BRAND["texto_medio"])
        self.set_draw_color(*BRAND["linha"])
        self.line(12, self.get_y(), 198, self.get_y())

        self.set_y(-14)
        w_col = (198 - 12) / 4.0
        self.set_x(12)
        self.cell(w_col, 5, 'www.tour360vr.com.br', link='https://tour360vr.com.br', align='C')
        self.cell(w_col, 5, 'contato@tour360vr.com.br', link='mailto:contato@tour360vr.com.br', align='C')
        self.cell(w_col, 5, 'WhatsApp: (16) 99133-2121', link='https://wa.me/5516991332121', align='C')
        self.cell(w_col, 5, f'PÃ¡gina {self.page_no()} de 4', align='C')

        self.faixa_marca(293.5)

    def rounded_rect(self, x, y, w, h, r, style=''):
        k = self.k
        hp = self.h
        if style == 'F':
            op = 'f'
        elif style in ('FD', 'DF'):
            op = 'B'
        else:
            op = 'S'

        my_arc = 4 / 3 * (2 ** 0.5 - 1)
        self._out(f'{(x+r)*k:.2f} {(hp-y)*k:.2f} m')
        xc = x + w - r
        yc = y + r
        self._out(f'{xc*k:.2f} {(hp-y)*k:.2f} l')
        self._arc(xc + r * my_arc, yc - r, xc + r, yc - r * my_arc, xc + r, yc)
        xc = x + w - r
        yc = y + h - r
        self._out(f'{(x+w)*k:.2f} {(hp-yc)*k:.2f} l')
        self._arc(xc + r, yc + r * my_arc, xc + r * my_arc, yc + r, xc, yc + r)
        xc = x + r
        yc = y + h - r
        self._out(f'{xc*k:.2f} {(hp-(y+h))*k:.2f} l')
        self._arc(xc - r * my_arc, yc + r, xc - r, yc + r * my_arc, xc - r, yc)
        xc = x + r
        yc = y + r
        self._out(f'{x*k:.2f} {(hp-yc)*k:.2f} l')
        self._arc(xc - r, yc - r * my_arc, xc - r * my_arc, yc - r, xc, yc - r)
        self._out(f'{op}')

    def _arc(self, x1, y1, x2, y2, x3, y3):
        k = self.k
        hp = self.h
        self._out(f'{x1*k:.2f} {(hp-y1)*k:.2f} {x2*k:.2f} {(hp-y2)*k:.2f} {x3*k:.2f} {(hp-y3)*k:.2f} c')

    def pill_status(self, x, y, w, h, label, cor):
        self.set_fill_color(*cor)
        self.rounded_rect(x, y, w, h, h / 2.0, 'F')
        self.set_xy(x, y + (h - 4) / 2.0)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(255, 255, 255)
        self.cell(w, 4, conv(label), align='C')


def gerar_pdf_oficial(dados, score, itens, planos, plano_acao_extra="", foto_bytes=None):
    pdf = PDFTour360Oficial()
    pdf.set_auto_page_break(auto=True, margin=20)

    status_label, status_cor = classificar_status(score)

    # -------------------------------------------------------------------
    # PÃGINA 1: CAPA â€” logo, foto do cliente, dados e status
    # -------------------------------------------------------------------
    pdf.add_page()

    if LOGO_PATH:
        try:
            pdf.image(LOGO_PATH, 88, 16, 34)
        except Exception:
            pass

    pdf.set_y(54)
    pdf.set_font('Helvetica', 'B', 19)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(0, 8, conv('DIAGNÃ“STICO DE PRESENÃ‡A DIGITAL'), align='C', ln=True)

    pdf.set_font('Helvetica', 'B', 12.5)
    pdf.set_text_color(*BRAND["vermelho"])
    pdf.cell(0, 6, conv('GOOGLE MEU NEGÃ“CIO'), align='C', ln=True)
    pdf.ln(6)

    # --- Foto do perfil do cliente (moldura elegante) ---
    foto_w, foto_h = 62, 62
    foto_x = (210 - foto_w) / 2.0
    foto_y = pdf.get_y()

    pdf.set_draw_color(*BRAND["azul"])
    pdf.set_line_width(0.8)
    pdf.rounded_rect(foto_x - 2, foto_y - 2, foto_w + 4, foto_h + 4, 4, 'D')
    pdf.set_line_width(0.2)

    if foto_bytes:
        try:
            pdf.image(io.BytesIO(foto_bytes), foto_x, foto_y, foto_w, foto_h)
        except Exception:
            foto_bytes = None

    if not foto_bytes:
        pdf.set_fill_color(*BRAND["fundo_claro"])
        pdf.rounded_rect(foto_x, foto_y, foto_w, foto_h, 3, 'F')
        # Ã­cone simples de "sem foto": um cÃ­rculo e um traÃ§o, sem depender de fontes de Ã­cone
        cx, cy = foto_x + foto_w / 2.0, foto_y + foto_h / 2.0 - 5
        pdf.set_fill_color(*BRAND["linha"])
        pdf.ellipse(cx - 7, cy - 7, 14, 14, 'F')
        pdf.set_fill_color(255, 255, 255)
        pdf.ellipse(cx - 3.2, cy - 3.2, 6.4, 6.4, 'F')
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(*BRAND["texto_medio"])
        pdf.set_xy(foto_x, foto_y + foto_h - 12)
        pdf.cell(foto_w, 4, conv('Foto do perfil Google'), align='C', ln=True)
        pdf.set_x(foto_x)
        pdf.cell(foto_w, 4, conv('nÃ£o disponÃ­vel'), align='C')

    pdf.set_y(foto_y + foto_h + 10)

    # --- Nome, endereÃ§o, telefone ---
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(0, 8, conv(dados['nome']), align='C', ln=True)

    pdf.set_font('Helvetica', '', 10.5)
    pdf.set_text_color(*BRAND["texto_medio"])
    pdf.cell(0, 5.5, conv(dados['endereco']), align='C', ln=True)
    pdf.cell(0, 5.5, conv(f"Telefone: {dados['telefone']}"), align='C', ln=True)

    pdf.set_font('Helvetica', 'B', 10.5)
    pdf.set_text_color(*BRAND["laranja"])
    pdf.cell(0, 7, conv(f"Nota {dados['nota']:.1f}/5.0  â€¢  {dados['avaliacoes']} avaliaÃ§Ãµes no Google"), align='C', ln=True)
    pdf.ln(4)

    pill_w = 70
    pdf.pill_status((210 - pill_w) / 2.0, pdf.get_y(), pill_w, 9,
                     f"STATUS: {status_label}  â€¢  {score}/100", status_cor)

    # -------------------------------------------------------------------
    # PÃGINA 2: DIAGNÃ“STICO DETALHADO
    # -------------------------------------------------------------------
    pdf.add_page()

    w_ficha = 160
    x_ficha = (210 - w_ficha) / 2.0

    pdf.set_fill_color(*BRAND["fundo_claro"])
    pdf.set_draw_color(*BRAND["linha"])
    pdf.rounded_rect(x_ficha, 34, w_ficha, 34, 3, 'FD')

    pdf.set_xy(x_ficha, 37)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(*BRAND["texto_medio"])
    pdf.cell(w_ficha, 4, conv('FICHA ANALISADA DO CLIENTE'), align='C', ln=True)

    pdf.set_x(x_ficha)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(w_ficha, 6, conv(dados['nome']), align='C', ln=True)

    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(*BRAND["texto_medio"])
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.2, conv(f"{dados['endereco']}"), align='C', ln=True)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.2, conv(f"Telefone: {dados['telefone']}   |   Website: {dados['website']}"), align='C', ln=True)

    y_score = 76
    w_score = 150
    x_score = (210 - w_score) / 2.0
    pdf.set_fill_color(*status_cor)
    pdf.set_draw_color(*status_cor)
    pdf.rounded_rect(x_score, y_score, w_score, 16, 3, 'FD')

    pdf.set_xy(x_score, y_score + 2)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(w_score, 5, conv(f"{score} / 100"), align='C', ln=True)

    pdf.set_xy(x_score, y_score + 8)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(w_score, 4, conv(f"SCORE GERAL DE OTIMIZAÃ‡ÃƒO ({status_label})"), align='C', ln=True)

    pdf.set_y(y_score + 22)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(0, 6, conv('AUDITORIA DETALHADA DE PONTOS DE BUSCA'), align='C', ln=True)
    pdf.ln(6)

    for item in itens:
        pct = item["pct"]
        cor_pct = BRAND["vermelho"] if pct < 40 else (BRAND["laranja"] if pct < 80 else BRAND["verde"])

        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(120, 3.8, conv(f"{item['nome']}  (peso {item['peso']} pts)"), ln=False)

        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(*cor_pct)
        pdf.cell(66, 3.8, conv(f"| {pct}%"), align='R', ln=True)

        pdf.set_fill_color(*BRAND["linha"])
        pdf.rounded_rect(12, pdf.get_y(), 186, 3, 1.5, 'F')
        pdf.set_fill_color(*cor_pct)
        largura_barra = max(float(pct) * 1.86, 4.0)
        pdf.rounded_rect(12, pdf.get_y(), largura_barra, 3, 1.5, 'F')
        pdf.ln(3.8)

        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(*BRAND["texto_medio"])
        pdf.cell(0, 3, conv(f"  DiagnÃ³stico: {item['desc']}"), ln=True)
        pdf.ln(2)

    if plano_acao_extra and plano_acao_extra.strip():
        pdf.ln(2)
        pdf.set_fill_color(*BRAND["fundo_claro"])
        pdf.set_draw_color(*BRAND["linha"])

        y_extra = pdf.get_y()
        pdf.rounded_rect(12, y_extra, 186, 24, 2, 'FD')

        pdf.set_xy(15, y_extra + 2)
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(*BRAND["azul"])
        pdf.cell(180, 4, conv("PLANO DE AÃ‡ÃƒO E APONTAMENTOS ESTRATÃ‰GICOS PERSONALIZADOS:"), ln=True)

        pdf.set_x(15)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(180, 3.6, conv(plano_acao_extra))

    # -------------------------------------------------------------------
    # PÃGINA 3: PROPOSTA COMERCIAL & PLANOS
    # -------------------------------------------------------------------
    pdf.add_page()

    pdf.set_y(32)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(0, 7, conv('PROPOSTA COMERCIAL & ESTRUTURAÃ‡ÃƒO ESTRATÃ‰GICA'), align='C', ln=True)
    pdf.ln(8)

    box_top = pdf.get_y()
    box_h = 28
    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(*BRAND["azul"])
    pdf.set_line_width(0.6)
    pdf.rounded_rect(12, box_top, 186, box_h, 2, 'FD')
    pdf.set_line_width(0.2)

    pdf.set_xy(12, box_top + 3)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(186, 5, conv('POR QUE SEU NEGÃ“CIO PRECISA DE OTIMIZAÃ‡ÃƒO PROFISSIONAL?'), align='C', ln=True)

    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(51, 65, 85)
    txt_exp = (
        "Mais de 80% das buscas locais no Google e Maps resultam em uma aÃ§Ã£o imediata (ligaÃ§Ã£o, rota ou mensagem).\n"
        "Perfis com fotos profissionais e Tour Virtual 360Â° geram atÃ© 2x mais interesse e permanecem no topo das buscas.\n"
        "Fichas incompletas ou desatualizadas perdem clientes diariamente para concorrentes com nota mais alta."
    )
    pdf.set_xy(15, box_top + 9)
    pdf.multi_cell(180, 4.3, conv(txt_exp), align='C')

    pdf.set_y(box_top + box_h + 12)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(0, 7, conv('PROPOSTA DE PLANOS E INVESTIMENTO'), align='C', ln=True)
    pdf.ln(8)

    y_p = pdf.get_y() + 2
    altura_padrao = 58
    altura_pro = 64          # antes ficava 66 e desalinhava a base dos 3 cards
    topo_pro = y_p - 4

    # --- PLANO START ---
    pdf.set_fill_color(*BRAND["fundo_claro"])
    pdf.set_draw_color(*BRAND["linha"])
    pdf.rounded_rect(12, y_p + 2, 52, altura_padrao, 2, 'FD')

    pdf.set_xy(12, y_p + 5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(52, 5, 'Plano Start', align='C', ln=True)

    pdf.set_xy(12, y_p + 12)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(*BRAND["azul"])
    pdf.cell(52, 6, conv(f"R$ {planos['start_valor']}"), align='C', ln=True)

    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(13, y_p + 20)
    pdf.multi_cell(50, 4, conv(planos['start_itens']), align='L')

    # --- PLANO PRO (destaque) ---
    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(*BRAND["azul"])
    pdf.set_line_width(1.0)
    pdf.rounded_rect(68, topo_pro, 70, altura_pro, 3, 'FD')
    pdf.set_line_width(0.2)

    pdf.set_xy(68, topo_pro + 4)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(*BRAND["azul"])
    pdf.cell(70, 5, conv('Plano Pro'), align='C', ln=True)

    pdf.set_xy(68, topo_pro + 9)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(*BRAND["vermelho"])
    pdf.cell(70, 4, conv('(Recomendado)'), align='C', ln=True)

    pdf.set_xy(68, topo_pro + 15)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(*BRAND["azul"])
    pdf.cell(70, 7, conv(f"R$ {planos['pro_valor']}"), align='C', ln=True)

    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.set_xy(70, topo_pro + 24)
    pdf.multi_cell(66, 4.2, conv(planos['pro_itens']), align='L')

    # --- GESTÃƒO MENSAL ---
    pdf.set_fill_color(*BRAND["fundo_claro"])
    pdf.set_draw_color(*BRAND["linha"])
    pdf.rounded_rect(142, y_p + 2, 54, altura_padrao, 2, 'FD')

    pdf.set_xy(142, y_p + 5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(54, 5, conv('GestÃ£o Mensal'), align='C', ln=True)

    pdf.set_xy(142, y_p + 12)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(*BRAND["azul"])
    pdf.cell(54, 6, conv(f"R$ {planos['gestao_valor']}"), align='C', ln=True)

    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(143, y_p + 20)
    pdf.multi_cell(52, 4, conv(planos['gestao_itens']), align='L')

    # -------------------------------------------------------------------
    # PÃGINA 4: CONTRATO DE PRESTAÃ‡ÃƒO DE SERVIÃ‡OS
    # -------------------------------------------------------------------
    pdf.add_page()

    pdf.set_y(32)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(0, 7, conv('CONTRATO DE PRESTAÃ‡ÃƒO DE SERVIÃ‡OS'), align='C', ln=True)
    pdf.ln(8)

    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85)

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATADA: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("Tour360VR, representada por Rubens H. Okamoto, CPF: 287.932.298-79 e Telefone: (16) 99133-2121.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATANTE: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv(f"{dados['nome']}, A/C: {dados['contato']}, {dados['endereco']}, Telefone: {dados['telefone']}.\n\n"))

    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("A "))
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATADA "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("compromete-se a executar os serviÃ§os de otimizaÃ§Ã£o, reestruturaÃ§Ã£o tÃ©cnica e/ou produÃ§Ã£o de Tour Virtual 360Â° para o perfil do Google da "))
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATANTE.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÃUSULA PRIMEIRA - DO OBJETO: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("Os serviÃ§os serÃ£o iniciados em atÃ© 5 dias Ãºteis apÃ³s o fornecimento dos acessos e informaÃ§Ãµes necessÃ¡rias ao perfil.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÃUSULA SEGUNDA - DAS OBRIGAÃ‡Ã•ES: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("O nÃ£o pagamento na data acordada sujeitarÃ¡ o presente contrato Ã  incidÃªncia de juros legais de mora e interrupÃ§Ã£o temporÃ¡ria dos serviÃ§os.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÃUSULA TERCEIRA - SELEÃ‡ÃƒO DO PLANO CONTRATADO:\n"))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("(  ) Plano Start        (  ) Plano Pro        (  ) GestÃ£o Mensal\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÃUSULA QUARTA - CONDIÃ‡Ã•ES DE PAGAMENTO:\n"))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("(  ) A Vista    (  ) 2x Plano Start    (  ) 3x Plano Pro    (  ) GestÃ£o Mensal - Vencimento Todo Dia: _____\n\n"))

    # Garante que as assinaturas nÃ£o fiquem "penduradas" sozinhas no topo
    # de uma nova pÃ¡gina caso o texto acima chegue perto do rodapÃ©.
    if pdf.get_y() > 250:
        pdf.add_page()
        pdf.set_y(32)
    else:
        pdf.ln(16)

    pdf.cell(88, 5, '__________________________________', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, '__________________________________', align='C', ln=True)

    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(88, 5, 'TOUR360VR (Rubens H. Okamoto)', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, conv(dados['nome']), align='C', ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer


# -----------------------------------------------------------------------------
# 4. INTERFACE STREAMLIT
# -----------------------------------------------------------------------------
st.sidebar.markdown(f"""
    <div style='text-align: center; padding-bottom: 15px;'>
        <h2 style='color: #ffffff; margin: 0;'>TOUR<span style='color: {HEX["vermelho"]};'>360VR</span></h2>
        <p style='color: {HEX["azul"]}; font-size: 12px; margin-top: 2px;'>Plataforma de Consultoria</p>
    </div>
""", unsafe_allow_html=True)

opcao_menu = st.sidebar.radio(
    "NavegaÃ§Ã£o do Sistema:",
    [
        "ðŸ” 1. Consulta & DiagnÃ³stico RÃ¡pido",
        "ðŸ’¡ 2. Plano de AÃ§Ã£o & DiagnÃ³stico",
        "ðŸ’² 3. Proposta & Planos",
        "ðŸ“„ 4. Contrato Profissional"
    ]
)

st.markdown(f"""
    <div class="header-box">
        <div class="header-title">PLATAFORMA DE CONSULTORIA <span>TOUR360VR</span></div>
        <div class="header-subtitle">GESTÃƒO & DIAGNÃ“STICO DO GOOGLE MEU NEGÃ“CIO</div>
    </div>
""", unsafe_allow_html=True)

dados_atuais = st.session_state['dados']
score_atual, itens_atuais = calcular_diagnostico(dados_atuais)
st.session_state['score'] = score_atual
st.session_state['itens_diagnostico'] = itens_atuais

# -----------------------------------------------------------------------------
# ETAPA 1: CONSULTA & DIAGNÃ“STICO
# -----------------------------------------------------------------------------
if "ðŸ”" in opcao_menu:
    st.subheader("ðŸ” 1. Dados do Cliente & DiagnÃ³stico")

    col_busca, col_cidade = st.columns([2, 1])
    with col_busca:
        nome_input = st.text_input("ðŸ¢ Nome do Estabelecimento:", value=st.session_state['dados']['nome'])
        st.session_state['dados']['nome'] = nome_input
    with col_cidade:
        cidade_empresa = st.text_input("ðŸ“ Cidade / Estado da Busca:", value="RibeirÃ£o Preto, SP")

    if st.button("ðŸš€ Buscar e Atualizar Dados no Google", use_container_width=True):
        if nome_input:
            termo_busca = f"{nome_input}, {cidade_empresa}" if cidade_empresa else nome_input

            if API_KEY_GOOGLE:
                try:
                    url_search = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={termo_busca}&key={API_KEY_GOOGLE}"
                    res_search = requests.get(url_search, timeout=10).json()

                    if res_search.get("results"):
                        place = res_search["results"][0]
                        place_id = place.get("place_id")

                        url_details = (
                            "https://maps.googleapis.com/maps/api/place/details/json"
                            f"?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,"
                            f"international_phone_number,website,rating,user_ratings_total,photos&key={API_KEY_GOOGLE}"
                        )
                        res_details = requests.get(url_details, timeout=10).json().get("result", {})

                        photos = res_details.get("photos", place.get("photos", []))

                        st.session_state['dados']['nome'] = res_details.get("name", place.get("name", nome_input))
                        st.session_state['dados']['endereco'] = res_details.get("formatted_address") or place.get("formatted_address") or cidade_empresa
                        st.session_state['dados']['telefone'] = res_details.get("formatted_phone_number") or res_details.get("international_phone_number") or "NÃ£o informado"
                        st.session_state['dados']['website'] = res_details.get("website", "NÃ£o possui")
                        st.session_state['dados']['nota'] = res_details.get("rating", place.get("rating", 4.2))
                        st.session_state['dados']['avaliacoes'] = res_details.get("user_ratings_total", place.get("user_ratings_total", 38))
                        st.session_state['dados']['tem_fotos_hd'] = len(photos) > 10

                        # Guarda a referÃªncia da primeira foto e jÃ¡ baixa os bytes
                        # para usar na capa do PDF (fica em cache na sessÃ£o).
                        if photos:
                            ref = photos[0].get("photo_reference")
                            st.session_state['dados']['foto_reference'] = ref
                            st.session_state['dados']['foto_bytes'] = baixar_foto_google(ref, API_KEY_GOOGLE)
                        else:
                            st.session_state['dados']['foto_reference'] = None
                            st.session_state['dados']['foto_bytes'] = None
                    else:
                        st.warning("Nenhum resultado encontrado para essa busca no Google.")
                except Exception as e:
                    st.error(f"Erro na conexÃ£o com o Google: {e}")
            else:
                st.warning("Configure GOOGLE_PLACES_API_KEY em st.secrets para buscar dados reais do Google.")

            st.rerun()

    st.markdown("---")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.session_state['dados']['contato'] = st.text_input("ðŸ‘¤ Nome do Contato / ResponsÃ¡vel:", value=st.session_state['dados']['contato'])
        st.session_state['dados']['endereco'] = st.text_input("ðŸ“ EndereÃ§o Completo:", value=st.session_state['dados']['endereco'])
    with col_f2:
        st.session_state['dados']['telefone'] = st.text_input("ðŸ“ž Telefone / WhatsApp:", value=st.session_state['dados']['telefone'])
        st.session_state['dados']['website'] = st.text_input("ðŸŒ Website Cadastrado:", value=st.session_state['dados']['website'])

    dados = st.session_state['dados']
    score = st.session_state['score']
    status_label, _ = classificar_status(score)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col1:
        st.markdown(f"""
            <div class="score-card">
                <h2 style="color: {HEX['vermelho']}; font-size: 44px; margin: 0;">{score} / 100</h2>
                <p style="color: #cbd5e1; text-transform: uppercase; font-size: 12px; font-weight: bold;">{status_label}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="card-dark">
                <h3 style="color: {HEX['azul']}; margin-top: 0;">{dados['nome']}</h3>
                <p style="margin: 4px 0;">ðŸ‘¤ <strong>Contato:</strong> {dados['contato']}</p>
                <p style="margin: 4px 0;">ðŸ“ {dados['endereco']}</p>
                <p style="margin: 4px 0;">ðŸ“ž <strong>Telefone:</strong> {dados['telefone']}</p>
                <p style="margin: 4px 0;">ðŸŒ <strong>Website:</strong> {dados['website']}</p>
                <p style="margin: 4px 0;">â­ <strong>AvaliaÃ§Ãµes:</strong> {dados['nota']} ({dados['avaliacoes']} avaliaÃ§Ãµes)</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        if dados.get('foto_bytes'):
            st.image(dados['foto_bytes'], caption="Foto do perfil no Google", use_container_width=True)
        else:
            st.info("Sem foto do Google disponÃ­vel para este perfil ainda.")

    pdf_bytes = gerar_pdf_oficial(
        dados, score, st.session_state['itens_diagnostico'],
        st.session_state['planos'], st.session_state['plano_acao_extra'],
        foto_bytes=dados.get('foto_bytes')
    )

    st.markdown("---")
    st.download_button(
        label="ðŸ“¥ Baixar Documento Oficial de DiagnÃ³stico, Proposta e Contrato em PDF",
        data=pdf_bytes,
        file_name=f"Diagnostico_Tour360VR_{dados['nome'].replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# ETAPA 2: PLANO DE AÃ‡ÃƒO & DIAGNÃ“STICO
# -----------------------------------------------------------------------------
elif "ðŸ’¡" in opcao_menu:
    st.subheader("ðŸ’¡ 2. Editar Plano de AÃ§Ã£o & DiagnÃ³stico")

    st.markdown("""
        * **SEO Local & AtualizaÃ§Ã£o Cadastral:** Ajuste de tÃ­tulos, palavras-chave e categorias principais/secundÃ¡rias.
        * **Tour Virtual 360Â° Interativo:** PublicaÃ§Ã£o de tour imersivo diretamente integrado ao Google Maps.
        * **Fotos de Alta ResoluÃ§Ã£o:** ProduÃ§Ã£o fotogrÃ¡fica profissional em HD para transmitir credibilidade.
        * **Links de ConversÃ£o RÃ¡pida:** BotÃµes para WhatsApp, cardÃ¡pio digital e reserva de serviÃ§os.
    """)

    st.markdown("---")
    st.markdown("### ðŸ“ InformaÃ§Ãµes Adicionais para o Cliente:")
    st.session_state['plano_acao_extra'] = st.text_area(
        "Adicionar apontamentos personalizados (refletem diretamente no PDF):",
        value=st.session_state['plano_acao_extra'],
        height=140
    )
    st.success("AlteraÃ§Ãµes salvas!")

    st.markdown("---")
    st.markdown("### ðŸ“Š Detalhamento da pontuaÃ§Ã£o atual")
    for item in st.session_state['itens_diagnostico']:
        cor = "ðŸŸ¢" if item["pct"] >= 80 else ("ðŸŸ " if item["pct"] >= 40 else "ðŸ”´")
        st.write(f"{cor} **{item['nome']}** (peso {item['peso']} pts) â€” {item['pct']}% â€” {item['desc']}")

# -----------------------------------------------------------------------------
# ETAPA 3: PROPOSTA & PLANOS
# -----------------------------------------------------------------------------
elif "ðŸ’²" in opcao_menu:
    st.subheader("ðŸ’² 3. Editar Itens e Valores da Proposta Comercial")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### ðŸ”¹ Plano Start")
        st.session_state['planos']['start_valor'] = st.text_input("Valor Start (R$):", value=st.session_state['planos']['start_valor'])
        st.session_state['planos']['start_itens'] = st.text_area("Itens Plano Start:", value=st.session_state['planos']['start_itens'], height=150)

    with col2:
        st.markdown("### ðŸ”¹ Plano Pro")
        st.session_state['planos']['pro_valor'] = st.text_input("Valor Pro (R$):", value=st.session_state['planos']['pro_valor'])
        st.session_state['planos']['pro_itens'] = st.text_area("Itens Plano Pro:", value=st.session_state['planos']['pro_itens'], height=150)

    with col3:
        st.markdown("### ðŸ”¹ GestÃ£o Mensal")
        st.session_state['planos']['gestao_valor'] = st.text_input("Valor GestÃ£o (R$):", value=st.session_state['planos']['gestao_valor'])
        st.session_state['planos']['gestao_itens'] = st.text_area("Itens GestÃ£o Mensal:", value=st.session_state['planos']['gestao_itens'], height=150)

    st.success("Valores e itens atualizados com sucesso!")

# -----------------------------------------------------------------------------
# ETAPA 4: CONTRATO
# -----------------------------------------------------------------------------
elif "ðŸ“„" in opcao_menu:
    st.subheader("ðŸ“„ 4. Contrato de PrestaÃ§Ã£o de ServiÃ§os")
    st.info("O contrato Ã© atualizado e gerado automaticamente na 4Âª pÃ¡gina do PDF completo, de acordo com os dados editados nas etapas anteriores.")

# -----------------------------------------------------------------------------
# RODAPÃ‰ FIXO DO APP
# -----------------------------------------------------------------------------
st.markdown(f"""
    <div class="footer">
        Tour360VR â€¢ tour360vr.com.br â€¢ contato@tour360vr.com.br â€¢ WhatsApp: (16) 99133-2121
    </div>
""", unsafe_allow_html=True)

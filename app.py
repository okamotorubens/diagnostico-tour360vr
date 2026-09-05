import io
import os
import datetime
import requests
import streamlit as st
from fpdf import FPDF

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E IDENTIDADE VISUAL TOUR360VR
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tour360VR - Plataforma de Consultoria e Diagnóstico",
    page_icon="🌐",
    layout="wide"
)

BRAND = {
    "vermelho": (255, 49, 49),    # #FF3131
    "coral":    (250, 107, 69),   # #FA6B45
    "laranja":  (255, 165, 48),   # #FFA530
    "azul":     (72, 165, 217),   # #48A5D9
    "verde":    (159, 189, 89),   # #9FBD59
    "texto_escuro": (15, 23, 42),
    "texto_medio": (71, 85, 105),
    "linha": (226, 232, 240),
    "fundo_claro": (248, 250, 252),
    "sombra": (215, 219, 226),
}
HEX = {k: "#%02x%02x%02x" % v for k, v in BRAND.items()}

# 4 faixas de status, usando as 4 cores do arco da logo.
NIVEIS = [
    (0, 40, "CRÍTICO",   BRAND["vermelho"]),
    (40, 70, "ATENÇÃO",   BRAND["laranja"]),
    (70, 90, "BOM",       BRAND["azul"]),
    (90, 101, "EXCELENTE", BRAND["verde"]),
]

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0f172a; color: #f8fafc; }}
    .header-box {{ border-bottom: 2px solid {HEX['azul']}; padding-bottom: 12px; margin-bottom: 25px; }}
    .header-title {{ color: #ffffff; font-size: 26px; font-weight: 700; margin: 0; }}
    .header-title span {{ color: {HEX['vermelho']}; }}
    .header-subtitle {{ color: {HEX['azul']}; font-size: 14px; font-weight: 600; margin-top: 4px; }}
    .card-dark {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
    .status-card {{ background-color: #1e293b; border: 2px solid {HEX['azul']}; padding: 20px; border-radius: 8px; text-align: center; }}
    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0b0f19; color: #94a3b8;
               text-align: center; padding: 10px; border-top: 1px solid #1e293b; font-size: 12px; z-index: 100; }}
    </style>
""", unsafe_allow_html=True)

API_KEY_GOOGLE = st.secrets.get("GOOGLE_PLACES_API_KEY", "")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def resolver_arquivo(nomes_relativos):
    for nome in nomes_relativos:
        caminho_absoluto = os.path.join(BASE_DIR, nome)
        if os.path.exists(caminho_absoluto):
            return caminho_absoluto
    for nome in nomes_relativos:
        if os.path.exists(nome):
            return nome
    return None


LOGO_PATH = resolver_arquivo(["assets/Logo_TOUR_transparente.png", "Logo_TOUR_transparente.png"])
FONTE_REGULAR = resolver_arquivo(["assets/fonts/DejaVuSans.ttf"])
FONTE_BOLD = resolver_arquivo(["assets/fonts/DejaVuSans-Bold.ttf"])

if not LOGO_PATH:
    st.sidebar.warning(
        "⚠️ Logo não encontrada. Verifique se a pasta 'assets/' com "
        "'Logo_TOUR_transparente.png' está ao lado deste arquivo .py no repositório."
    )
if not FONTE_REGULAR or not FONTE_BOLD:
    st.sidebar.warning(
        "⚠️ Fontes não encontradas. Verifique se 'assets/fonts/DejaVuSans.ttf' e "
        "'DejaVuSans-Bold.ttf' estão no repositório — sem elas a acentuação do PDF falha."
    )

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO DE ESTADOS EDITÁVEIS
# -----------------------------------------------------------------------------
if 'dados' not in st.session_state:
    st.session_state['dados'] = {
        "nome": "Toque de Letra",
        "contato": "Marcio Javaroni",
        "endereco": "Ribeirão Preto / SP",
        "telefone": "16 99622 2121",
        "website": "Não possui",
        "nota": 4.2,
        "avaliacoes": 38,
        "tem_tour360": False,
        "tem_fotos_hd": False,
        "categorias_completas": False,
        "horarios_ok": False,
        "foto_bytes": None,
        "foto_origem": None,
    }

if 'planos' not in st.session_state:
    st.session_state['planos'] = {
        "start_valor": "500,00",
        "start_itens": "- Correção cadastral\n- Otimização de SEO\n- Ajuste de categorias\n- Inserção de links",
        "pro_valor": "1.150,00",
        "pro_itens": "- Tudo do Plano Start\n- Tour Virtual 360°\n- Ensaio Fotográfico HD\n- Relatório Visual de Entrega",
        "gestao_valor": "600,00/mês",
        "gestao_itens": "- Postagens semanais\n- Gestão de avaliações\n- Atualização de fotos\n- Relatório mensal"
    }

if 'plano_acao_extra' not in st.session_state:
    st.session_state['plano_acao_extra'] = "Você precisa de mim."


# -----------------------------------------------------------------------------
# 2. PONTUAÇÃO — score geral + percentual por item (visual), sem exibir o
#    peso em pontos de cada critério (removido a pedido).
# -----------------------------------------------------------------------------
ITENS_CONFIG = [
    {"chave": "tem_tour360", "nome": "Tour Virtual 360° Interativo", "peso": 25,
     "desc_ok": "Tour 360° publicado e integrado ao perfil.",
     "desc_falta": "Nenhum Tour 360° detectado no perfil."},
    {"chave": "website", "nome": "Website e Links de Conversão", "peso": 20, "tipo": "website",
     "desc_ok": "Site e links diretos de contato cadastrados.",
     "desc_falta": "Sem site ou links diretos de contato/WhatsApp."},
    {"chave": "tem_fotos_hd", "nome": "Fotos em Boa Quantidade e Resolução", "peso": 20,
     "desc_ok": "Fotos em quantidade e resolução adequadas.",
     "desc_falta": "Poucas fotos ou fotos em baixa resolução."},
    {"chave": "categorias_completas", "nome": "Categorias Principal e Secundárias", "peso": 15,
     "desc_ok": "Categorias principal e secundárias bem definidas.",
     "desc_falta": "Sem categorias secundárias cadastradas."},
    {"chave": "horarios_ok", "nome": "Horários de Funcionamento", "peso": 10,
     "desc_ok": "Horários completos e cadastrados para a semana.",
     "desc_falta": "Horário de funcionamento incompleto ou ausente."},
    {"chave": "avaliacoes", "nome": "Avaliações no Google (Prova Social)", "peso": 10, "tipo": "avaliacoes",
     "desc_ok": "Volume de avaliações saudável.",
     "desc_falta": "Poucas avaliações registradas."},
]


def classificar_status(score):
    for minimo, maximo, label, cor in NIVEIS:
        if minimo <= score < maximo:
            return label, cor
    return NIVEIS[-1][2], NIVEIS[-1][3]


def calcular_diagnostico(dados):
    itens = []
    pontos_totais = 0.0
    for cfg in ITENS_CONFIG:
        if cfg.get("tipo") == "website":
            ok = dados.get("website", "Não possui") not in ("Não possui", "", None)
            pct = 100 if ok else 0
        elif cfg.get("tipo") == "avaliacoes":
            qtd = dados.get("avaliacoes") or 0
            pct = min(int((qtd / 50.0) * 100), 100) if qtd > 0 else 0
            ok = pct >= 100
        else:
            ok = bool(dados.get(cfg["chave"]))
            pct = 100 if ok else 0

        pontos_totais += cfg["peso"] * pct / 100.0
        itens.append({"nome": cfg["nome"], "pct": pct, "ok": ok,
                       "desc": cfg["desc_ok"] if ok else cfg["desc_falta"]})

    score = round(pontos_totais)
    status_label, status_cor = classificar_status(score)
    return score, itens, status_label, status_cor


# -----------------------------------------------------------------------------
# 2b. AVALIAÇÃO REAL DOS DADOS TRAZIDOS PELA BUSCA NO GOOGLE
# -----------------------------------------------------------------------------
TIPOS_GENERICOS = {"point_of_interest", "establishment", "premise", "subpremise"}


def avaliar_categorias(types_api):
    tipos_relevantes = [t for t in (types_api or []) if t not in TIPOS_GENERICOS]
    return len(tipos_relevantes) >= 2


def avaliar_horarios(opening_hours_api):
    if not opening_hours_api:
        return False
    periods = opening_hours_api.get("periods", [])
    dias_cobertos = {p.get("open", {}).get("day") for p in periods if p.get("open")}
    return len(dias_cobertos) >= 6


def avaliar_fotos(photos_api):
    if not photos_api:
        return False
    if len(photos_api) >= 8:
        return True
    return any((p.get("width") or 0) >= 1280 for p in photos_api)


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


def texto_estrelas(nota, unicode_disponivel=True):
    """Os caracteres ★/☆ só existem na fonte Unicode (DejaVu). Se ela não
    estiver disponível (fallback para Helvetica), usar um formato 100%
    seguro em ASCII evita o FPDFUnicodeEncodingException que travava o PDF."""
    cheias = max(0, min(5, round(nota)))
    if unicode_disponivel:
        return "★" * cheias + "☆" * (5 - cheias)
    return "[" + "*" * cheias + "-" * (5 - cheias) + "]"


# -----------------------------------------------------------------------------
# 3. GERADOR DE PDF TOUR360VR (fonte Unicode embutida — corrige acentuação)
# -----------------------------------------------------------------------------
class PDFTour360Oficial(FPDF):

    def faixa_marca(self, y, altura=3.5):
        cores = [BRAND["laranja"], BRAND["azul"], BRAND["coral"], BRAND["verde"]]
        largura_seg = 210 / 4.0
        for i, cor in enumerate(cores):
            self.set_fill_color(*cor)
            self.rect(i * largura_seg, y, largura_seg, altura, 'F')

    def header(self):
        self.faixa_marca(0)
        if self.page_no() == 1:
            return

        x_pos = 12
        if LOGO_PATH:
            try:
                self.image(LOGO_PATH, 12, 8, 16)
                x_pos = 32
            except Exception:
                x_pos = 12

        self.set_xy(x_pos, 8.5)
        self.set_font('DejaVu', 'B', 13)
        self.set_text_color(*BRAND["vermelho"])
        self.cell(0, 5, 'TOUR360VR', ln=True)
        self.set_xy(x_pos, 14.5)
        self.set_font('DejaVu', '', 8.5)
        self.set_text_color(*BRAND["texto_medio"])
        self.cell(0, 4, 'Gestão de Perfil & Diagnóstico do Google Meu Negócio', ln=True)

        self.set_draw_color(*BRAND["linha"])
        self.set_line_width(0.3)
        self.line(12, 22, 198, 22)
        self.set_line_width(0.2)
        self.ln(19)

    def footer(self):
        self.set_y(-17)
        self.set_font('DejaVu', '', 8.5)
        self.set_text_color(*BRAND["texto_medio"])
        self.set_draw_color(*BRAND["linha"])
        self.line(12, self.get_y(), 198, self.get_y())

        self.set_y(-14)
        w_col = (198 - 12) / 4.0
        self.set_x(12)
        self.cell(w_col, 5, 'www.tour360vr.com.br', link='https://tour360vr.com.br', align='C')
        self.cell(w_col, 5, 'contato@tour360vr.com.br', link='mailto:contato@tour360vr.com.br', align='C')
        self.cell(w_col, 5, 'WhatsApp: (16) 99133-2121', link='https://wa.me/5516991332121', align='C')
        self.cell(w_col, 5, f'Página {self.page_no()} de 4', align='C')

        self.faixa_marca(293.5)

    def rounded_rect(self, x, y, w, h, r, style=''):
        k = self.k
        hp = self.h
        op = 'f' if style == 'F' else ('B' if style in ('FD', 'DF') else 'S')
        my_arc = 4 / 3 * (2 ** 0.5 - 1)
        self._out(f'{(x+r)*k:.2f} {(hp-y)*k:.2f} m')
        xc, yc = x + w - r, y + r
        self._out(f'{xc*k:.2f} {(hp-y)*k:.2f} l')
        self._arc(xc + r * my_arc, yc - r, xc + r, yc - r * my_arc, xc + r, yc)
        xc, yc = x + w - r, y + h - r
        self._out(f'{(x+w)*k:.2f} {(hp-yc)*k:.2f} l')
        self._arc(xc + r, yc + r * my_arc, xc + r * my_arc, yc + r, xc, yc + r)
        xc, yc = x + r, y + h - r
        self._out(f'{xc*k:.2f} {(hp-(y+h))*k:.2f} l')
        self._arc(xc - r * my_arc, yc + r, xc - r, yc + r * my_arc, xc - r, yc)
        xc, yc = x + r, y + r
        self._out(f'{x*k:.2f} {(hp-yc)*k:.2f} l')
        self._arc(xc - r, yc - r * my_arc, xc - r * my_arc, yc - r, xc, yc - r)
        self._out(f'{op}')

    def _arc(self, x1, y1, x2, y2, x3, y3):
        k, hp = self.k, self.h
        self._out(f'{x1*k:.2f} {(hp-y1)*k:.2f} {x2*k:.2f} {(hp-y2)*k:.2f} {x3*k:.2f} {(hp-y3)*k:.2f} c')

    def pill_status(self, x, y, w, h, label, cor):
        self.set_fill_color(*cor)
        self.rounded_rect(x, y, w, h, h / 2.0, 'F')
        self.set_xy(x, y + (h - 4) / 2.0)
        self.set_font('DejaVu', 'B', 9)
        self.set_text_color(255, 255, 255)
        self.cell(w, 4, label, align='C')

    def ponto_legenda(self, x, y, cor, texto):
        self.set_fill_color(*cor)
        self.ellipse(x, y, 3, 3, 'F')
        self.set_xy(x + 5, y - 1)
        self.set_font('DejaVu', '', 7.5)
        self.set_text_color(*BRAND["texto_medio"])
        self.cell(0, 4, texto)


def gerar_pdf_oficial(dados, score, itens, status_label, status_cor,
                       planos, plano_acao_extra="", foto_bytes=None):
    pdf = PDFTour360Oficial()
    pdf.set_auto_page_break(auto=True, margin=20)

    fonte_disponivel = bool(FONTE_REGULAR and FONTE_BOLD)
    if fonte_disponivel:
        pdf.add_font("DejaVu", "", FONTE_REGULAR)
        pdf.add_font("DejaVu", "B", FONTE_BOLD)

    def fonte(estilo, tamanho):
        pdf.set_font('DejaVu' if fonte_disponivel else 'Helvetica', estilo, tamanho)

    # -------------------------------------------------------------------
    # PÁGINA 1: CAPA — layout em cartão, moderno
    # -------------------------------------------------------------------
    pdf.add_page()

    if LOGO_PATH:
        try:
            pdf.image(LOGO_PATH, 91, 12, 28)
        except Exception:
            pass

    pdf.set_y(44)
    fonte('B', 18)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(0, 8, 'DIAGNÓSTICO DE PRESENÇA DIGITAL', align='C', ln=True)

    fonte('B', 11)
    pdf.set_text_color(*BRAND["vermelho"])
    pdf.cell(0, 6, 'GOOGLE MEU NEGÓCIO', align='C', ln=True)

    pdf.set_draw_color(*BRAND["linha"])
    pdf.set_line_width(0.4)
    pdf.line(85, 66, 125, 66)
    pdf.set_line_width(0.2)

    # --- Cartão de perfil (sombra + card branco) ---
    card_x, card_y, card_w, card_h = 20, 76, 170, 78
    pdf.set_fill_color(*BRAND["sombra"])
    pdf.rounded_rect(card_x + 1.5, card_y + 2, card_w, card_h, 4, 'F')
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*BRAND["linha"])
    pdf.rounded_rect(card_x, card_y, card_w, card_h, 4, 'FD')

    # Foto à esquerda dentro do cartão
    foto_x, foto_y, foto_w, foto_h = card_x + 8, card_y + 8, 54, 62
    pdf.set_draw_color(*BRAND["azul"])
    pdf.set_line_width(0.6)
    pdf.rounded_rect(foto_x, foto_y, foto_w, foto_h, 3, 'D')
    pdf.set_line_width(0.2)

    if foto_bytes:
        try:
            pdf.image(io.BytesIO(foto_bytes), foto_x + 1, foto_y + 1, foto_w - 2, foto_h - 2)
        except Exception:
            foto_bytes = None

    if not foto_bytes:
        pdf.set_fill_color(*BRAND["fundo_claro"])
        pdf.rounded_rect(foto_x + 1, foto_y + 1, foto_w - 2, foto_h - 2, 2, 'F')
        cx, cy = foto_x + foto_w / 2.0, foto_y + foto_h / 2.0 - 6
        pdf.set_fill_color(*BRAND["linha"])
        pdf.ellipse(cx - 6, cy - 6, 12, 12, 'F')
        pdf.set_fill_color(255, 255, 255)
        pdf.ellipse(cx - 2.8, cy - 2.8, 5.6, 5.6, 'F')
        fonte('', 7)
        pdf.set_text_color(*BRAND["texto_medio"])
        pdf.set_xy(foto_x, foto_y + foto_h - 12)
        pdf.cell(foto_w, 4, 'Foto do perfil', align='C', ln=True)
        pdf.set_x(foto_x)
        pdf.cell(foto_w, 4, 'Google não disponível', align='C')

    # Coluna direita: dados do negócio
    col2_x = foto_x + foto_w + 10
    col2_w = card_x + card_w - col2_x - 8

    pdf.set_xy(col2_x, card_y + 9)
    fonte('B', 15)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.multi_cell(col2_w, 6.5, dados['nome'])

    pdf.set_x(col2_x)
    fonte('', 9.5)
    pdf.set_text_color(*BRAND["texto_medio"])
    pdf.multi_cell(col2_w, 4.6, dados['endereco'])
    pdf.set_x(col2_x)
    pdf.cell(col2_w, 4.6, f"Telefone: {dados['telefone']}", ln=True)

    pdf.set_x(col2_x)
    pdf.ln(2)
    fonte('B', 13)
    pdf.set_text_color(*BRAND["laranja"])
    pdf.set_x(col2_x)
    pdf.cell(col2_w, 6, texto_estrelas(dados['nota'], fonte_disponivel), ln=True)

    fonte('', 9)
    pdf.set_text_color(*BRAND["texto_medio"])
    pdf.set_x(col2_x)
    pdf.cell(col2_w, 5, f"{dados['nota']:.1f}/5.0  •  {dados['avaliacoes']} avaliações no Google", ln=True)

    pdf.set_x(col2_x)
    pdf.ln(3)
    pill_w = 62
    pdf.pill_status(col2_x, pdf.get_y(), pill_w, 9, f"{status_label}  •  {score}/100", status_cor)

    # --- Legenda de status (deixa a leitura mais intuitiva) ---
    y_legenda = card_y + card_h + 14
    fonte('', 7.5)
    pdf.set_text_color(*BRAND["texto_medio"])
    pdf.set_xy(0, y_legenda - 6)
    pdf.cell(210, 4, 'O QUE CADA STATUS SIGNIFICA', align='C', ln=True)

    largura_legenda = 168
    x_legenda = (210 - largura_legenda) / 2.0
    passos = largura_legenda / 4.0
    itens_legenda = [
        (BRAND["vermelho"], "Crítico"),
        (BRAND["laranja"], "Atenção"),
        (BRAND["azul"], "Bom"),
        (BRAND["verde"], "Excelente"),
    ]
    for i, (cor, label) in enumerate(itens_legenda):
        pdf.ponto_legenda(x_legenda + i * passos, y_legenda, cor, label)

    fonte('', 8.5)
    pdf.set_text_color(*BRAND["texto_medio"])
    pdf.set_xy(20, y_legenda + 14)
    pdf.multi_cell(170, 4.4,
        "Este diagnóstico é a base do trabalho que faremos juntos: cada ponto abaixo mostra "
        "exatamente onde o perfil está perdendo oportunidades e o que será corrigido.",
        align='C')

    data_geracao = datetime.date.today().strftime('%d/%m/%Y')
    fonte('', 7.5)
    pdf.set_text_color(*BRAND["texto_medio"])
    pdf.set_xy(0, 262)
    pdf.cell(210, 4, f'Diagnóstico gerado em {data_geracao}  •  Tour360VR', align='C')

    # -------------------------------------------------------------------
    # PÁGINA 2: DIAGNÓSTICO DETALHADO
    # -------------------------------------------------------------------
    pdf.add_page()

    w_ficha = 160
    x_ficha = (210 - w_ficha) / 2.0
    pdf.set_fill_color(*BRAND["fundo_claro"])
    pdf.set_draw_color(*BRAND["linha"])
    pdf.rounded_rect(x_ficha, 34, w_ficha, 34, 3, 'FD')

    pdf.set_xy(x_ficha, 37)
    fonte('B', 8.5)
    pdf.set_text_color(*BRAND["texto_medio"])
    pdf.cell(w_ficha, 4, 'FICHA ANALISADA DO CLIENTE', align='C', ln=True)

    pdf.set_x(x_ficha)
    fonte('B', 13)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(w_ficha, 6, dados['nome'], align='C', ln=True)

    fonte('', 8.5)
    pdf.set_text_color(*BRAND["texto_medio"])
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.2, dados['endereco'], align='C', ln=True)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.2, f"Telefone: {dados['telefone']}   |   Website: {dados['website']}", align='C', ln=True)

    y_score = 76
    w_score = 150
    x_score = (210 - w_score) / 2.0
    pdf.set_fill_color(*status_cor)
    pdf.set_draw_color(*status_cor)
    pdf.rounded_rect(x_score, y_score, w_score, 16, 3, 'FD')

    pdf.set_xy(x_score, y_score + 2)
    fonte('B', 15)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(w_score, 5, f"{score} / 100", align='C', ln=True)
    pdf.set_xy(x_score, y_score + 8)
    fonte('B', 8)
    pdf.cell(w_score, 4, f"SCORE GERAL DE OTIMIZAÇÃO ({status_label})", align='C', ln=True)

    pdf.set_y(y_score + 22)
    fonte('B', 13)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(0, 6, 'AUDITORIA DETALHADA DE PONTOS DE BUSCA', align='C', ln=True)
    pdf.ln(6)

    for item in itens:
        pct = item["pct"]
        cor_pct = BRAND["vermelho"] if pct < 40 else (BRAND["laranja"] if pct < 80 else BRAND["verde"])

        fonte('B', 9)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(120, 3.8, item['nome'], ln=False)

        fonte('B', 8.5)
        pdf.set_text_color(*cor_pct)
        pdf.cell(66, 3.8, f"| {pct}%", align='R', ln=True)

        pdf.set_fill_color(*BRAND["linha"])
        pdf.rounded_rect(12, pdf.get_y(), 186, 3, 1.5, 'F')
        pdf.set_fill_color(*cor_pct)
        largura_barra = max(float(pct) * 1.86, 4.0)
        pdf.rounded_rect(12, pdf.get_y(), largura_barra, 3, 1.5, 'F')
        pdf.ln(3.8)

        fonte('', 8)
        pdf.set_text_color(*BRAND["texto_medio"])
        pdf.cell(0, 3, f"  Diagnóstico: {item['desc']}", ln=True)
        pdf.ln(2)

    if plano_acao_extra and plano_acao_extra.strip():
        pdf.ln(2)
        pdf.set_fill_color(*BRAND["fundo_claro"])
        pdf.set_draw_color(*BRAND["linha"])
        y_extra = pdf.get_y()
        altura_extra = 10 + 3.6 * (len(plano_acao_extra) // 90 + 1)
        pdf.rounded_rect(12, y_extra, 186, altura_extra, 2, 'FD')

        pdf.set_xy(15, y_extra + 2)
        fonte('B', 8.5)
        pdf.set_text_color(*BRAND["azul"])
        pdf.cell(180, 4, 'PLANO DE AÇÃO E APONTAMENTOS PERSONALIZADOS:', ln=True)

        pdf.set_x(15)
        fonte('', 8)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(180, 3.6, plano_acao_extra)

    # -------------------------------------------------------------------
    # PÁGINA 3: PROPOSTA COMERCIAL & PLANOS
    # -------------------------------------------------------------------
    pdf.add_page()

    pdf.set_y(32)
    fonte('B', 14)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(0, 7, 'PROPOSTA COMERCIAL & ESTRUTURAÇÃO ESTRATÉGICA', align='C', ln=True)
    pdf.ln(8)

    box_top = pdf.get_y()
    box_h = 28
    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(*BRAND["azul"])
    pdf.set_line_width(0.6)
    pdf.rounded_rect(12, box_top, 186, box_h, 2, 'FD')
    pdf.set_line_width(0.2)

    pdf.set_xy(12, box_top + 3)
    fonte('B', 10)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(186, 5, 'POR QUE SEU NEGÓCIO PRECISA DE OTIMIZAÇÃO PROFISSIONAL?', align='C', ln=True)

    fonte('', 9)
    pdf.set_text_color(51, 65, 85)
    txt_exp = (
        "Mais de 80% das buscas locais no Google e Maps resultam em uma ação imediata (ligação, rota ou mensagem).\n"
        "Perfis com fotos profissionais e Tour Virtual 360° geram até 2x mais interesse e permanecem no topo das buscas.\n"
        "Fichas incompletas ou desatualizadas perdem clientes diariamente para concorrentes com nota mais alta."
    )
    pdf.set_xy(15, box_top + 9)
    pdf.multi_cell(180, 4.3, txt_exp, align='C')

    pdf.set_y(box_top + box_h + 12)
    fonte('B', 14)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(0, 7, 'PROPOSTA DE PLANOS E INVESTIMENTO', align='C', ln=True)
    pdf.ln(8)

    y_p = pdf.get_y() + 2
    altura_padrao = 58
    altura_pro = 64
    topo_pro = y_p - 4

    pdf.set_fill_color(*BRAND["fundo_claro"])
    pdf.set_draw_color(*BRAND["linha"])
    pdf.rounded_rect(12, y_p + 2, 52, altura_padrao, 2, 'FD')
    pdf.set_xy(12, y_p + 5)
    fonte('B', 11)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(52, 5, 'Plano Start', align='C', ln=True)
    pdf.set_xy(12, y_p + 12)
    fonte('B', 12)
    pdf.set_text_color(*BRAND["azul"])
    pdf.cell(52, 6, f"R$ {planos['start_valor']}", align='C', ln=True)
    fonte('', 8)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(13, y_p + 20)
    pdf.multi_cell(50, 4, planos['start_itens'], align='L')

    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(*BRAND["azul"])
    pdf.set_line_width(1.0)
    pdf.rounded_rect(68, topo_pro, 70, altura_pro, 3, 'FD')
    pdf.set_line_width(0.2)
    pdf.set_xy(68, topo_pro + 4)
    fonte('B', 13)
    pdf.set_text_color(*BRAND["azul"])
    pdf.cell(70, 5, 'Plano Pro', align='C', ln=True)
    pdf.set_xy(68, topo_pro + 9)
    fonte('B', 9)
    pdf.set_text_color(*BRAND["vermelho"])
    pdf.cell(70, 4, '(Recomendado)', align='C', ln=True)
    pdf.set_xy(68, topo_pro + 15)
    fonte('B', 14)
    pdf.set_text_color(*BRAND["azul"])
    pdf.cell(70, 7, f"R$ {planos['pro_valor']}", align='C', ln=True)
    fonte('B', 8.5)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.set_xy(70, topo_pro + 24)
    pdf.multi_cell(66, 4.2, planos['pro_itens'], align='L')

    pdf.set_fill_color(*BRAND["fundo_claro"])
    pdf.set_draw_color(*BRAND["linha"])
    pdf.rounded_rect(142, y_p + 2, 54, altura_padrao, 2, 'FD')
    pdf.set_xy(142, y_p + 5)
    fonte('B', 11)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(54, 5, 'Gestão Mensal', align='C', ln=True)
    pdf.set_xy(142, y_p + 12)
    fonte('B', 12)
    pdf.set_text_color(*BRAND["azul"])
    pdf.cell(54, 6, f"R$ {planos['gestao_valor']}", align='C', ln=True)
    fonte('', 8)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(143, y_p + 20)
    pdf.multi_cell(52, 4, planos['gestao_itens'], align='L')

    # -------------------------------------------------------------------
    # PÁGINA 4: CONTRATO DE PRESTAÇÃO DE SERVIÇOS
    # -------------------------------------------------------------------
    pdf.add_page()

    pdf.set_y(32)
    fonte('B', 14)
    pdf.set_text_color(*BRAND["texto_escuro"])
    pdf.cell(0, 7, 'CONTRATO DE PRESTAÇÃO DE SERVIÇOS', align='C', ln=True)
    pdf.ln(8)

    fonte('', 9.5)
    pdf.set_text_color(51, 65, 85)

    fonte('B', 9.5)
    pdf.write(5.5, "CONTRATADA: ")
    fonte('', 9.5)
    pdf.write(5.5, "Tour360VR, representada por Rubens H. Okamoto, CPF: 287.932.298-79 e Telefone: (16) 99133-2121.\n\n")

    fonte('B', 9.5)
    pdf.write(5.5, "CONTRATANTE: ")
    fonte('', 9.5)
    pdf.write(5.5, f"{dados['nome']}, A/C: {dados['contato']}, {dados['endereco']}, Telefone: {dados['telefone']}.\n\n")

    fonte('', 9.5)
    pdf.write(5.5, "A ")
    fonte('B', 9.5)
    pdf.write(5.5, "CONTRATADA ")
    fonte('', 9.5)
    pdf.write(5.5, "compromete-se a executar os serviços de otimização, reestruturação técnica e/ou produção de Tour Virtual 360° para o perfil do Google da ")
    fonte('B', 9.5)
    pdf.write(5.5, "CONTRATANTE.\n\n")

    fonte('B', 9.5)
    pdf.write(5.5, "CLÁUSULA PRIMEIRA - DO OBJETO: ")
    fonte('', 9.5)
    pdf.write(5.5, "Os serviços serão iniciados em até 5 dias úteis após o fornecimento dos acessos e informações necessárias ao perfil.\n\n")

    fonte('B', 9.5)
    pdf.write(5.5, "CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES: ")
    fonte('', 9.5)
    pdf.write(5.5, "O não pagamento na data acordada sujeitará o presente contrato à incidência de juros legais de mora e interrupção temporária dos serviços.\n\n")

    fonte('B', 9.5)
    pdf.write(5.5, "CLÁUSULA TERCEIRA - SELEÇÃO DO PLANO CONTRATADO:\n")
    fonte('', 9.5)
    pdf.write(5.5, "(  ) Plano Start        (  ) Plano Pro        (  ) Gestão Mensal\n\n")

    fonte('B', 9.5)
    pdf.write(5.5, "CLÁUSULA QUARTA - CONDIÇÕES DE PAGAMENTO:\n")
    fonte('', 9.5)
    pdf.write(5.5, "(  ) A Vista    (  ) 2x Plano Start    (  ) 3x Plano Pro    (  ) Gestão Mensal - Vencimento Todo Dia: _____\n\n")

    if pdf.get_y() > 250:
        pdf.add_page()
        pdf.set_y(32)
    else:
        pdf.ln(16)

    pdf.cell(88, 5, '__________________________________', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, '__________________________________', align='C', ln=True)
    fonte('B', 9)
    pdf.cell(88, 5, 'TOUR360VR (Rubens H. Okamoto)', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, dados['nome'], align='C', ln=True)

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
    "Navegação do Sistema:",
    [
        "🔍 1. Consulta & Diagnóstico Rápido",
        "💡 2. Plano de Ação & Diagnóstico",
        "💲 3. Proposta & Planos",
        "📄 4. Contrato Profissional"
    ]
)

st.markdown(f"""
    <div class="header-box">
        <div class="header-title">PLATAFORMA DE CONSULTORIA <span>TOUR360VR</span></div>
        <div class="header-subtitle">GESTÃO & DIAGNÓSTICO DO GOOGLE MEU NEGÓCIO</div>
    </div>
""", unsafe_allow_html=True)

dados_atuais = st.session_state['dados']
score_atual, itens_atuais, status_label_atual, status_cor_atual = calcular_diagnostico(dados_atuais)
st.session_state['score'] = score_atual
st.session_state['itens_diagnostico'] = itens_atuais

# -----------------------------------------------------------------------------
# ETAPA 1: CONSULTA & DIAGNÓSTICO
# -----------------------------------------------------------------------------
if "🔍" in opcao_menu:
    st.subheader("🔍 1. Dados do Cliente & Diagnóstico")

    if not API_KEY_GOOGLE:
        st.warning(
            "GOOGLE_PLACES_API_KEY não configurada em st.secrets — a busca automática e a "
            "foto do Google não vão funcionar. Você ainda pode preencher tudo manualmente abaixo."
        )

    col_busca, col_cidade = st.columns([2, 1])
    with col_busca:
        nome_input = st.text_input("🏢 Nome do Estabelecimento:", value=st.session_state['dados']['nome'])
        st.session_state['dados']['nome'] = nome_input
    with col_cidade:
        cidade_empresa = st.text_input("📍 Cidade / Estado da Busca:", value="Ribeirão Preto, SP")

    if st.button("🚀 Buscar e Atualizar Dados no Google", use_container_width=True):
        if nome_input and API_KEY_GOOGLE:
            termo_busca = f"{nome_input}, {cidade_empresa}" if cidade_empresa else nome_input
            try:
                url_search = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={termo_busca}&key={API_KEY_GOOGLE}"
                res_search = requests.get(url_search, timeout=10).json()

                if res_search.get("status") != "OK" or not res_search.get("results"):
                    st.warning(f"Nenhum resultado encontrado no Google (status: {res_search.get('status')}).")
                else:
                    place = res_search["results"][0]
                    place_id = place.get("place_id")

                    url_details = (
                        "https://maps.googleapis.com/maps/api/place/details/json"
                        f"?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,"
                        f"international_phone_number,website,rating,user_ratings_total,photos,types,"
                        f"opening_hours&key={API_KEY_GOOGLE}"
                    )
                    res_details = requests.get(url_details, timeout=10).json().get("result", {})

                    photos = res_details.get("photos", place.get("photos", []))
                    types_api = res_details.get("types", place.get("types", []))
                    opening_hours_api = res_details.get("opening_hours")

                    d = st.session_state['dados']
                    d['nome'] = res_details.get("name", place.get("name", nome_input))
                    d['endereco'] = res_details.get("formatted_address") or place.get("formatted_address") or cidade_empresa
                    d['telefone'] = res_details.get("formatted_phone_number") or res_details.get("international_phone_number") or "Não informado"
                    d['website'] = res_details.get("website", "Não possui")
                    d['nota'] = res_details.get("rating", place.get("rating", 4.2))
                    d['avaliacoes'] = res_details.get("user_ratings_total", place.get("user_ratings_total", 0))

                    d['categorias_completas'] = avaliar_categorias(types_api)
                    d['horarios_ok'] = avaliar_horarios(opening_hours_api)
                    d['tem_fotos_hd'] = avaliar_fotos(photos)

                    if photos:
                        ref = photos[0].get("photo_reference")
                        foto = baixar_foto_google(ref, API_KEY_GOOGLE)
                        if foto:
                            d['foto_bytes'] = foto
                            d['foto_origem'] = "google"

                    st.success(f"Dados de \"{d['nome']}\" atualizados a partir do Google.")
            except Exception as e:
                st.error(f"Erro na conexão com o Google: {e}")
        elif not API_KEY_GOOGLE:
            st.warning("Configure GOOGLE_PLACES_API_KEY em st.secrets para buscar dados reais do Google.")
        st.rerun()

    st.markdown("---")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.session_state['dados']['contato'] = st.text_input("👤 Nome do Contato / Responsável:", value=st.session_state['dados']['contato'])
        st.session_state['dados']['endereco'] = st.text_input("📍 Endereço Completo:", value=st.session_state['dados']['endereco'])
    with col_f2:
        st.session_state['dados']['telefone'] = st.text_input("📞 Telefone / WhatsApp:", value=st.session_state['dados']['telefone'])
        st.session_state['dados']['website'] = st.text_input("🌐 Website Cadastrado:", value=st.session_state['dados']['website'])

    st.markdown("##### Itens que exigem checagem manual (o Google não informa isso pela API)")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.session_state['dados']['tem_tour360'] = st.checkbox(
            "Já possui Tour Virtual 360°?", value=st.session_state['dados']['tem_tour360'])
    with col_m2:
        st.session_state['dados']['categorias_completas'] = st.checkbox(
            "Confirmo: categorias secundárias OK", value=st.session_state['dados']['categorias_completas'])
    with col_m3:
        st.session_state['dados']['horarios_ok'] = st.checkbox(
            "Confirmo: horários completos", value=st.session_state['dados']['horarios_ok'])

    st.markdown("##### Foto de capa para o diagnóstico")
    foto_upload = st.file_uploader("Enviar uma foto manualmente (opcional, tem prioridade sobre a foto do Google)",
                                    type=["png", "jpg", "jpeg"])
    if foto_upload is not None:
        st.session_state['dados']['foto_bytes'] = foto_upload.read()
        st.session_state['dados']['foto_origem'] = "manual"

    dados = st.session_state['dados']
    score, itens_diag, status_label, status_cor = calcular_diagnostico(dados)
    st.session_state['score'] = score
    st.session_state['itens_diagnostico'] = itens_diag

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col1:
        cor_css = "#%02x%02x%02x" % status_cor
        st.markdown(f"""
            <div class="status-card">
                <h2 style="color: {cor_css}; font-size: 40px; margin: 0;">{score}/100</h2>
                <p style="color: #cbd5e1; text-transform: uppercase; font-size: 12px; font-weight: bold;">{status_label}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="card-dark">
                <h3 style="color: {HEX['azul']}; margin-top: 0;">{dados['nome']}</h3>
                <p style="margin: 4px 0;">👤 <strong>Contato:</strong> {dados['contato']}</p>
                <p style="margin: 4px 0;">📍 {dados['endereco']}</p>
                <p style="margin: 4px 0;">📞 <strong>Telefone:</strong> {dados['telefone']}</p>
                <p style="margin: 4px 0;">🌐 <strong>Website:</strong> {dados['website']}</p>
                <p style="margin: 4px 0;">⭐ <strong>Avaliações:</strong> {dados['nota']} ({dados['avaliacoes']} avaliações)</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        if dados.get('foto_bytes'):
            legenda = "Foto enviada manualmente" if dados.get('foto_origem') == "manual" else "Foto do perfil no Google"
            st.image(dados['foto_bytes'], caption=legenda, use_container_width=True)
        else:
            st.info("Sem foto ainda — busque no Google ou envie uma manualmente acima.")

    pdf_bytes = gerar_pdf_oficial(
        dados, score, itens_diag, status_label, status_cor,
        st.session_state['planos'], st.session_state['plano_acao_extra'],
        foto_bytes=dados.get('foto_bytes')
    )

    st.markdown("---")
    st.download_button(
        label="📥 Baixar Documento Oficial de Diagnóstico, Proposta e Contrato em PDF",
        data=pdf_bytes,
        file_name=f"Diagnostico_Tour360VR_{dados['nome'].replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# ETAPA 2: PLANO DE AÇÃO & DIAGNÓSTICO
# -----------------------------------------------------------------------------
elif "💡" in opcao_menu:
    st.subheader("💡 2. Editar Plano de Ação & Diagnóstico")

    st.markdown("""
        * **SEO Local & Atualização Cadastral:** Ajuste de títulos, palavras-chave e categorias principais/secundárias.
        * **Tour Virtual 360° Interativo:** Publicação de tour imersivo diretamente integrado ao Google Maps.
        * **Fotos de Alta Resolução:** Produção fotográfica profissional em HD para transmitir credibilidade.
        * **Links de Conversão Rápida:** Botões para WhatsApp, cardápio digital e reserva de serviços.
    """)

    st.markdown("---")
    st.markdown("### 📝 Informações Adicionais para o Cliente:")
    st.session_state['plano_acao_extra'] = st.text_area(
        "Adicionar apontamentos personalizados (refletem diretamente no PDF):",
        value=st.session_state['plano_acao_extra'],
        height=140
    )
    st.success("Alterações salvas!")

    st.markdown("---")
    st.markdown(f"### 📊 Score atual: {st.session_state['score']}/100")
    for item in st.session_state['itens_diagnostico']:
        cor = "🟢" if item["pct"] >= 80 else ("🟠" if item["pct"] >= 40 else "🔴")
        st.write(f"{cor} **{item['nome']}** — {item['pct']}% — {item['desc']}")

# -----------------------------------------------------------------------------
# ETAPA 3: PROPOSTA & PLANOS
# -----------------------------------------------------------------------------
elif "💲" in opcao_menu:
    st.subheader("💲 3. Editar Itens e Valores da Proposta Comercial")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🔹 Plano Start")
        st.session_state['planos']['start_valor'] = st.text_input("Valor Start (R$):", value=st.session_state['planos']['start_valor'])
        st.session_state['planos']['start_itens'] = st.text_area("Itens Plano Start:", value=st.session_state['planos']['start_itens'], height=150)
    with col2:
        st.markdown("### 🔹 Plano Pro")
        st.session_state['planos']['pro_valor'] = st.text_input("Valor Pro (R$):", value=st.session_state['planos']['pro_valor'])
        st.session_state['planos']['pro_itens'] = st.text_area("Itens Plano Pro:", value=st.session_state['planos']['pro_itens'], height=150)
    with col3:
        st.markdown("### 🔹 Gestão Mensal")
        st.session_state['planos']['gestao_valor'] = st.text_input("Valor Gestão (R$):", value=st.session_state['planos']['gestao_valor'])
        st.session_state['planos']['gestao_itens'] = st.text_area("Itens Gestão Mensal:", value=st.session_state['planos']['gestao_itens'], height=150)

    st.success("Valores e itens atualizados com sucesso!")

# -----------------------------------------------------------------------------
# ETAPA 4: CONTRATO
# -----------------------------------------------------------------------------
elif "📄" in opcao_menu:
    st.subheader("📄 4. Contrato de Prestação de Serviços")
    st.info("O contrato é atualizado e gerado automaticamente na 4ª página do PDF completo, de acordo com os dados editados nas etapas anteriores.")

# -----------------------------------------------------------------------------
# RODAPÉ FIXO DO APP
# -----------------------------------------------------------------------------
st.markdown(f"""
    <div class="footer">
        Tour360VR • tour360vr.com.br • contato@tour360vr.com.br • WhatsApp: (16) 99133-2121
    </div>
""", unsafe_allow_html=True)

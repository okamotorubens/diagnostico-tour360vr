import os
import io
import requests
import streamlit as st
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
        padding-top: 0px;
    }
    
    .main-header {
        font-size: 24px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin-bottom: 20px;
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
        font-size: 16px;
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
        padding: 12px;
        border-top: 1px solid #1e293b;
        font-size: 13px;
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
# 2. FUNÇÕES UTILITÁRIAS
# -----------------------------------------------------------------------------
def conv(texto):
    if not texto: return ""
    limpo = str(texto).replace("•", "- ").replace("✓", "[OK] ").replace("📍", "").replace("📞", "").replace("🌐", "")
    return limpo.encode('latin-1', 'replace').decode('latin-1')

def formatar_estrelas(nota):
    try:
        val = int(round(float(nota)))
        return "*" * max(0, min(5, val))
    except:
        return "*****"

def calcular_score_real(dados):
    score = 100
    if not dados.get("tem_tour360", False): score -= 25
    if dados.get("website") == "Não possui" or not dados.get("website"): score -= 20
    if not dados.get("tem_fotos_hd", False): score -= 20
    if not dados.get("categorias_completas", False): score -= 15
    if not dados.get("horarios_ok", False): score -= 10
    if dados.get("avaliacoes", 0) < 50: score -= 10
    return max(score, 10)

def obter_caminho_logo():
    caminhos = ['assets/Logo_TOUR_transparente.png', 'Logo_TOUR_transparente.png', 'assets/Logo TOUR transparente.png']
    for c in caminhos:
        if os.path.exists(c): return c
    return None

# -----------------------------------------------------------------------------
# 3. ESTADOS DA SESSÃO
# -----------------------------------------------------------------------------
if 'dados' not in st.session_state:
    st.session_state['dados'] = {
        "nome": "Restaurante Sabor Local",
        "contato": "Gerente Responsável",
        "endereco": "Ribeirão Preto / SP",
        "telefone": "(16) 99133-2121",
        "website": "Não possui",
        "nota": 4.2,
        "avaliacoes": 38,
        "tem_tour360": False,
        "tem_fotos_hd": False,
        "categorias_completas": False,
        "horarios_ok": False
    }

if 'planos' not in st.session_state:
    st.session_state['planos'] = {
        "start_valor": "500,00",
        "start_itens": "- Correção cadastral\n- Otimização de SEO\n- Ajuste de categorias",
        "pro_valor": "1.150,00",
        "pro_itens": "- Tudo do Plano Start\n- Tour Virtual 360°\n- Ensaio Fotográfico HD",
        "gestao_valor": "600,00/mês",
        "gestao_itens": "- Postagens semanais\n- Gestão de avaliações"
    }

if 'plano_acao_extra' not in st.session_state:
    st.session_state['plano_acao_extra'] = "O perfil precisa de otimização urgente! Veja as falhas apontadas no relatório."

if 'unidades_encontradas' not in st.session_state:
    st.session_state['unidades_encontradas'] = []

# -----------------------------------------------------------------------------
# 4. GERADOR PDF TOUR360VR
# -----------------------------------------------------------------------------
class PDFTour360Oficial(FPDF):
    def header(self):
        self.set_fill_color(30, 64, 175)
        self.rect(0, 0, 105, 4, 'F')
        self.set_fill_color(255, 61, 61)
        self.rect(105, 0, 105, 4, 'F')
        if self.page_no() == 1: return
        
        caminho_logo = obter_caminho_logo()
        if caminho_logo:
            try: self.image(caminho_logo, 12, 9, 18)
            except: pass
            
        self.set_xy(34, 9.5)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(30, 64, 175)
        self.cell(0, 5, 'TOUR360VR', ln=True)
        self.set_xy(34, 15.5)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, conv('Gestão de Perfil & Diagnóstico do Google Meu Negócio'), ln=True)
        self.set_draw_color(226, 232, 240)
        self.line(12, 23, 198, 23)
        self.ln(20)

    def footer(self):
        self.set_y(-16)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(100, 116, 139)
        self.line(12, self.get_y(), 198, self.get_y())
        self.set_y(-13)
        w_col = (198 - 12) / 4.0
        self.set_x(12)
        self.cell(w_col, 5, 'www.tour360vr.com.br', link='https://tour360vr.com.br', align='C')
        self.cell(w_col, 5, 'contato@tour360vr.com.br', link='mailto:contato@tour360vr.com.br', align='C')
        self.cell(w_col, 5, 'WhatsApp: (16) 99133-2121', link='https://wa.me/5516991332121', align='C')
        self.cell(w_col, 5, f'Página {self.page_no()} de 4', align='C')

    def rounded_rect(self, x, y, w, h, r, style=''):
        k = self.k
        hp = self.h
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
        self._out(f'{xc*k:.2f} {(hp-(y+h))*k:.2f} l')
        self._arc(xc - r*my_arc, yc + r, xc - r, yc + r*my_arc, xc - r, yc)
        xc, yc = x + r, y + r
        self._out(f'{x*k:.2f} {(hp-yc)*k:.2f} l')
        self._arc(xc - r, yc - r*my_arc, xc - r*my_arc, yc - r, xc, yc - r)
        self._out(f'{op}')

    def _arc(self, x1, y1, x2, y2, x3, y3):
        k, hp = self.k, self.h
        self._out(f'{x1*k:.2f} {(hp-y1)*k:.2f} {x2*k:.2f} {(hp-y2)*k:.2f} {x3*k:.2f} {(hp-y3)*k:.2f} c')

def gerar_pdf_oficial(dados, score_input, planos, plano_acao_extra=""):
    score = calcular_score_real(dados)
    pdf = PDFTour360Oficial()
    pdf.set_auto_page_break(auto=True, margin=18)
    estrelas_txt = formatar_estrelas(dados['nota'])

    # PÁGINA 1: CAPA
    pdf.add_page()
    caminho_logo = obter_caminho_logo()
    if caminho_logo:
        try: pdf.image(caminho_logo, 82, 18, 46)
        except: pass

    pdf.set_y(68)
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 10, conv('DIAGNÓSTICO DE PRESENÇA DIGITAL'), align='C', ln=True)
    pdf.ln(2)

    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(0, 8, conv('GOOGLE MEU NEGÓCIO'), align='C', ln=True)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 8, conv('Tour360VR'), align='C', ln=True)
    pdf.ln(12)

    w_capa = 180
    x_capa = (210 - w_capa) / 2.0
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rounded_rect(x_capa, 122, w_capa, 78, 4, 'FD')

    pdf.set_xy(x_capa, 128)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_capa, 9, conv(f"{dados['nome']}"), align='C', ln=True)
    
    pdf.set_x(x_capa)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(w_capa, 6, conv(f"Nota: {dados['nota']:.1f} {estrelas_txt}   ({dados['avaliacoes']} avaliações no Google)"), align='C', ln=True)
    pdf.ln(3)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.set_x(x_capa)
    pdf.cell(w_capa, 5.5, conv(f"Cliente: {dados['contato']}"), align='C', ln=True)
    pdf.set_x(x_capa)
    pdf.cell(w_capa, 5.5, conv(f"{dados['endereco']}"), align='C', ln=True)
    pdf.set_x(x_capa)
    pdf.cell(w_capa, 5.5, conv(f"Telefone: {dados['telefone']}   |   Website: {dados['website']}"), align='C', ln=True)
    pdf.ln(4)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_x(x_capa)
    if score < 50:
        pdf.set_text_color(239, 68, 68)
        pdf.cell(w_capa, 6, conv("Status da Ficha: Crítico (Visibilidade Comprometida)"), align='C', ln=True)
    else:
        pdf.set_text_color(34, 197, 94)
        pdf.cell(w_capa, 6, conv("Status da Ficha: Otimizado e Em Expansão"), align='C', ln=True)

    # PÁGINA 2: DIAGNÓSTICO E AUDITORIA
    pdf.add_page()
    w_ficha = 154
    x_ficha = (210 - w_ficha) / 2.0
    
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(x_ficha, 32, w_ficha, 40, 3, 'FD')
    
    pdf.set_xy(x_ficha, 34)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(w_ficha, 4, conv('FICHA ANALISADA DO CLIENTE'), align='C', ln=True)
    pdf.set_x(x_ficha)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_ficha, 7, conv(f"{dados['nome']}"), align='C', ln=True)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(245, 158, 11)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 5, conv(f"Nota {dados['nota']:.1f} {estrelas_txt}   -   {dados['avaliacoes']} avaliações no Google"), align='C', ln=True)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.5, conv(f"{dados['endereco']}"), align='C', ln=True)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.5, conv(f"Telefone: {dados['telefone']}   |   Website: {dados['website']}"), align='C', ln=True)

    w_score = 90
    x_score = (210 - w_score) / 2.0
    pdf.set_y(78)
    if score < 50: cr, cg, cb, status_txt = 239, 68, 68, "STATUS CRÍTICO"
    elif score < 80: cr, cg, cb, status_txt = 245, 158, 11, "STATUS MÉDIO"
    else: cr, cg, cb, status_txt = 34, 197, 94, "ALTO DESEMPENHO"

    pdf.set_fill_color(cr, cg, cb)
    pdf.set_draw_color(cr, cg, cb)
    pdf.rounded_rect(x_score, 78, w_score, 22, 3, 'FD')
    pdf.set_xy(x_score, 80)
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(w_score, 8, conv(f"{score} / 100"), align='C', ln=True)
    pdf.set_xy(x_score, 90)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(w_score, 5, conv(f"SCORE GERAL ({status_txt})"), align='C', ln=True)

    pdf.set_y(108)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, conv('AUDITORIA DETALHADA DE PONTOS DE BUSCA'), align='C', ln=True)
    pdf.ln(8)

    pct_avaliacoes = min(int((dados['avaliacoes'] / 50.0) * 100), 100) if dados['avaliacoes'] > 0 else 10
    desc_fotos = "Atende ao volume recomendado de fotos em HD." if dados['tem_fotos_hd'] else "Poucas fotos encontradas / antigas no perfil."
    desc_tour = "Tour Virtual 360° ativo e integrado." if dados['tem_tour360'] else "Nenhum Tour 360 detectado no perfil do Google."
    desc_cat = "Atende às categorias principais e secundárias recomendadas." if dados['categorias_completas'] else "Ajuste necessário em categorias secundárias no perfil."
    desc_web = f"Website oficial: {dados['website']}" if dados['website'] != 'Não possui' else "Falta link de website cadastrado para conversão."

    itens = [
        ("1. Fotos e Resolução Visual", 100 if dados['tem_fotos_hd'] else 30, "Alto" if dados['tem_fotos_hd'] else "Baixo", desc_fotos),
        ("2. Tour Virtual 360° Interativo", 100 if dados['tem_tour360'] else 0, "Ativo" if dados['tem_tour360'] else "Ausente", desc_tour),
        ("3. Categorias Principal e Secundárias", 100 if dados['categorias_completas'] else 50, "Completo" if dados['categorias_completas'] else "Incompleto", desc_cat),
        ("4. Horários e Exceções (Feriados)", 100 if dados['horarios_ok'] else 40, "Atualizado" if dados['horarios_ok'] else "Desatualizado", "Falta de horários especiais em feriados."),
        ("5. Website e Links de Conversão", 100 if dados['website'] != 'Não possui' else 10, "Ativo" if dados['website'] != 'Não possui' else "Falho", desc_web),
        ("6. Avaliações no Google (Prova Social)", pct_avaliacoes, f"{dados['nota']}/5.0", f"{dados['avaliacoes']} avaliações registradas.")
    ]

    for titulo, pct, rotulo, desc in itens:
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(120, 4, conv(titulo), ln=False)
        
        pdf.set_font('Helvetica', 'B', 8)
        if pct < 40: pdf.set_text_color(239, 68, 68)
        elif pct < 80: pdf.set_text_color(245, 158, 11)
        else: pdf.set_text_color(34, 197, 94)
            
        pdf.cell(66, 4, conv(f"{pct}% - {rotulo}"), align='R', ln=True)

        pdf.set_fill_color(226, 232, 240)
        pdf.rounded_rect(12, pdf.get_y(), 186, 2.8, 1.4, 'F')
        
        if pct < 40: pdf.set_fill_color(239, 68, 68)
        elif pct < 80: pdf.set_fill_color(245, 158, 11)
        else: pdf.set_fill_color(34, 197, 94)
            
        largura_barra = max(float(pct) * 1.86, 4.0)
        pdf.rounded_rect(12, pdf.get_y(), largura_barra, 2.8, 1.4, 'F')
        pdf.ln(3.8)

        # TEXTO DE DIAGNÓSTICO AMPLIADO PARA 9PT
        pdf.set_font('Helvetica', '', 9.0)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(0, 4.2, conv(f"Diagnóstico: {desc}"), ln=True)
        pdf.ln(2.2)

    if plano_acao_extra and plano_acao_extra.strip() != "":
        pdf.ln(10)
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(203, 213, 225)
        y_extra = pdf.get_y()
        pdf.rounded_rect(12, y_extra, 186, 28, 2, 'FD')
        pdf.set_xy(12, y_extra + 3)
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(186, 4, conv("PLANO DE AÇÃO E APONTAMENTOS ESTRATÉGICOS PERSONALIZADOS:"), align='C', ln=True)
        pdf.set_xy(16, y_extra + 8.5)
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(178, 3.8, conv(plano_acao_extra), align='L')

    # PÁGINA 3: PLANOS E INVESTIMENTO
    pdf.add_page()
    pdf.set_y(32)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('PROPOSTA COMERCIAL & ESTRUTURAÇÃO ESTRATÉGICA'), align='C', ln=True)
    pdf.ln(10)

    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, conv('PLANOS E INVESTIMENTO'), align='C', ln=True)
    pdf.ln(8)

    y_p = pdf.get_y() + 2
    
    # Plano Start
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(12, y_p + 2, 54, 62, 2, 'FD')
    pdf.set_xy(12, y_p + 6)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(54, 5, 'Plano Start', align='C', ln=True)
    pdf.set_xy(12, y_p + 13)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(62, 161, 219)
    pdf.cell(54, 6, conv(f"R$ {planos['start_valor']}"), align='C', ln=True)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(17, y_p + 23)
    pdf.multi_cell(44, 4.2, conv(planos['start_itens']), align='L')

    # Plano Pro
    pdf.set_fill_color(238, 242, 255)
    pdf.set_draw_color(30, 64, 175)
    pdf.set_line_width(1.2)
    pdf.rounded_rect(70, y_p - 4, 70, 70, 3, 'FD')
    pdf.set_line_width(0.2)
    pdf.set_xy(70, y_p)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(70, 6, conv('Plano Pro'), align='C', ln=True)
    pdf.set_xy(70, y_p + 6)
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(70, 4, conv('(RECOMENDADO)'), align='C', ln=True)
    pdf.set_xy(70, y_p + 13)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(70, 7, conv(f"R$ {planos['pro_valor']}"), align='C', ln=True)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.set_xy(78, y_p + 24)
    pdf.multi_cell(56, 4.8, conv(planos['pro_itens']), align='L')

    # Gestão Mensal
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(144, y_p + 2, 54, 62, 2, 'FD')
    pdf.set_xy(144, y_p + 6)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(54, 5, conv('Gestão Mensal'), align='C', ln=True)
    pdf.set_xy(144, y_p + 13)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(62, 161, 219)
    pdf.cell(54, 6, conv(f"R$ {planos['gestao_valor']}"), align='C', ln=True)
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(149, y_p + 23)
    pdf.multi_cell(44, 4.2, conv(planos['gestao_itens']), align='L')

    pdf.set_y(y_p + 82)
    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(62, 161, 219)
    pdf.set_line_width(0.5)
    pdf.rounded_rect(12, pdf.get_y(), 186, 36, 2, 'FD')
    pdf.set_line_width(0.2)

    y_info = pdf.get_y() + 4
    pdf.set_xy(12, y_info)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(186, 5, conv('POR QUE SEU NEGÓCIO PRECISA DE OTIMIZAÇÃO PROFISSIONAL?'), align='C', ln=True)
    pdf.ln(2)

    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    txt_exp = (
        "Mais de 80% das buscas locais no Google e Maps resultam em uma ação imediata (ligação, rota ou mensagem).\n"
        "Perfis com fotos profissionais e Tour Virtual 360° geram até 2x mais interesse e permanecem no topo das buscas.\n"
        "Fichas incompletas ou desatualizadas perdem clientes diariamente para concorrentes diretos com nota mais alta."
    )
    pdf.set_x(12)
    pdf.multi_cell(186, 4.5, conv(txt_exp), align='C')

    # PÁGINA 4: CONTRATO
    pdf.add_page()
    pdf.set_y(32)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('CONTRATO DE PRESTAÇÃO DE SERVIÇOS'), align='C', ln=True)
    pdf.ln(14)

    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85)
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATADA: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("Tour360VR, representada por Rubens H. Okamoto, CPF: 287.932.298-79 e Telefone: (16) 99133-2121.\n\n"))
    
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATANTE: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv(f"{dados['nome']}, representada por {dados['contato']}, {dados['endereco']}, Telefone: {dados['telefone']}.\n\n"))
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("A "))
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATADA "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("compromete-se a executar os serviços de otimização, reestruturação técnica e/ou produção de Tour Virtual 360° para o perfil do Google da "))
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATANTE.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA PRIMEIRA - DO OBJETO: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("Os serviços serão iniciados em até 5 dias úteis após o fornecimento dos acessos e informações necessárias ao perfil.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("O não pagamento na data acordada sujeitará o presente contrato à incidência de juros legais de mora e interrupção temporária dos serviços.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA TERCEIRA - SELEÇÃO DO PLANO CONTRATADO:\n"))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("(  ) Plano Start        (  ) Plano Pro        (  ) Gestão Mensal\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA QUARTA - CONDIÇÕES DE PAGAMENTO:\n"))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("(  ) A Vista    (  ) 2x Plano Start    (  ) 3x Plano Pro    (  ) Gestão Mensal - Vencimento Todo Dia: _____\n\n\n"))

    pdf.ln(18)
    pdf.cell(88, 5, '__________________________________', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, '__________________________________', align='C', ln=True)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.cell(88, 5, 'Rubens H. Okamoto - TOUR360VR', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, conv(f"{dados['contato']} - {dados['nome']}"), align='C', ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 5. SIDEBAR / MENU LATERAL
# -----------------------------------------------------------------------------
with st.sidebar:
    caminho_logo = obter_caminho_logo()
    if caminho_logo:
        st.image(caminho_logo, width=120)
    else:
        st.markdown("## TOUR**360VR**")
        
    st.markdown("<p style='color: #94a3b8; font-size: 13px;'>Consultoria Pro: <b>" + st.session_state['dados']['nome'] + "</b></p>", unsafe_allow_html=True)
    st.markdown("---")

    opcao_menu = st.radio(
        "Navegação do Sistema:",
        [
            "🔍 1. Consulta & Diagnóstico Rápido",
            "🤝 2. Relatório de Vendas e Persuasão",
            "📜 3. Proposta & Planos",
            "📄 4. Contrato Profissional",
            "📊 5. Apresentação e Resultados",
            "📅 6. Relatório Mensal"
        ]
    )

st.markdown("<div class='main-header'>PLATAFORMA DE CONSULTORIA <span>TOUR360VR</span> - GESTÃO & DIAGNÓSTICO GOOGLE MEU NEGÓCIO</div>", unsafe_allow_html=True)
dados = st.session_state['dados']
score = calcular_score_real(dados)

# -----------------------------------------------------------------------------
# PAINEL CENTRAL (ETAPA 1 ATUALIZADA COM VERIFICAÇÃO DINÂMICA DE CATEGORIAS)
# -----------------------------------------------------------------------------
if "1. Consulta" in opcao_menu:
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='card-title'>CAPA DE DIAGNÓSTICO: [{dados['nome']}]</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            nome_input = st.text_input("Nome da Empresa:", value=dados['nome'])
        with c2:
            cidade_empresa = st.text_input("Localização:", value="Ribeirão Preto, SP")
            
        if st.button("🚀 Buscar no Google Maps", use_container_width=True):
            if API_KEY_GOOGLE:
                try:
                    termo = f"{nome_input}, {cidade_empresa}" if cidade_empresa else nome_input
                    url_search = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={termo}&key={API_KEY_GOOGLE}"
                    res = requests.get(url_search).json()
                    if res.get("status") == "OK" and res.get("results"):
                        st.session_state['unidades_encontradas'] = res["results"]
                        st.success(f"Encontrada(s) {len(res['results'])} unidade(s)!")
                    else:
                        st.error(f"Erro na busca: {res.get('status')} - {res.get('error_message', 'Local não encontrado')}")
                except Exception as e:
                    st.error(f"Erro na conexão: {e}")
            else:
                st.error("Chave GOOGLE_API_KEY não configurada nos segredos.")

        if st.session_state['unidades_encontradas']:
            opcoes = [f"{u.get('name')} - {u.get('formatted_address')}" for u in st.session_state['unidades_encontradas']]
            escolha = st.selectbox("Selecione a unidade exata:", opcoes)
            
            if st.button("📌 Carregar Dados desta Unidade", use_container_width=True):
                idx = opcoes.index(escolha)
                u = st.session_state['unidades_encontradas'][idx]
                place_id = u.get("place_id")
                
                # REQUISIÇÃO COMPLETA COM CAMPOS DE DETALHE E TYPES (CATEGORIAS)
                if API_KEY_GOOGLE:
                    try:
                        url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,international_phone_number,website,rating,user_ratings_total,photos,opening_hours,types&key={API_KEY_GOOGLE}"
                        res_details = requests.get(url_details).json().get("result", {})
                        
                        photos = res_details.get("photos", u.get("photos", []))
                        types_lista = res_details.get("types", [])
                        
                        st.session_state['dados']['nome'] = res_details.get("name") or u.get("name") or nome_input
                        st.session_state['dados']['endereco'] = res_details.get("formatted_address") or u.get("formatted_address")
                        st.session_state['dados']['telefone'] = res_details.get("formatted_phone_number") or res_details.get("international_phone_number") or "Não informado"
                        st.session_state['dados']['website'] = res_details.get("website") or "Não possui"
                        st.session_state['dados']['nota'] = float(res_details.get("rating") or u.get("rating") or 0.0)
                        st.session_state['dados']['avaliacoes'] = int(res_details.get("user_ratings_total") or u.get("user_ratings_total") or 0)
                        
                        st.session_state['dados']['tem_fotos_hd'] = len(photos) >= 10
                        st.session_state['dados']['horarios_ok'] = "opening_hours" in res_details
                        
                        # AVALIAÇÃO DINÂMICA DAS CATEGORIAS (100% se tiver 3+ categorias; senão 50%)
                        st.session_state['dados']['categorias_completas'] = len(types_lista) >= 3
                        
                        st.success("Dados reais e categorias extraídas do Google com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao obter detalhes: {e}")

        st.markdown("---")
        st.markdown("### ⚙️ Ajustes Manuais da Auditoria:")
        c_a, c_b, c_c, c_d = st.columns(4)
        st.session_state['dados']['tem_tour360'] = c_a.checkbox("Tour 360°", value=st.session_state['dados']['tem_tour360'])
        st.session_state['dados']['tem_fotos_hd'] = c_b.checkbox("Fotos HD", value=st.session_state['dados']['tem_fotos_hd'])
        st.session_state['dados']['categorias_completas'] = c_c.checkbox("Categorias OK", value=st.session_state['dados']['categorias_completas'])
        st.session_state['dados']['horarios_ok'] = c_d.checkbox("Horários OK", value=st.session_state['dados']['horarios_ok'])
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
        st.markdown("</div>", unsafe_allow_html=True)

elif "2. Relatório" in opcao_menu:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>ESTRUTURA DE VENDAS PERSUASIVA</div>", unsafe_allow_html=True)
    st.write("Apresentação de argumentos e gatilhos visuais de persuasão para o cliente.")
    st.markdown("</div>", unsafe_allow_html=True)

elif "3. Proposta" in opcao_menu:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>PROPOSTA & PLANOS COMERCIAIS</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Plano Start", f"R$ {st.session_state['planos']['start_valor']}")
    c2.metric("Plano Pro", f"R$ {st.session_state['planos']['pro_valor']}")
    c3.metric("Gestão Mensal", f"R$ {st.session_state['planos']['gestao_valor']}")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='card-title'>{opcao_menu}</div>", unsafe_allow_html=True)
    st.info("Módulo em exibição.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAINEL DE EXPORTAÇÃO PDF
# -----------------------------------------------------------------------------
st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
st.markdown("<div class='card-title'>GERAR PDF</div>", unsafe_allow_html=True)

pdf_bytes = gerar_pdf_oficial(dados, score, st.session_state['planos'], st.session_state['plano_acao_extra'])

b1, b2, b3 = st.columns(3)
with b1:
    st.download_button("💾 Salvar Diagnóstico em PDF", data=pdf_bytes, file_name=f"Diagnostico_{dados['nome'].replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
with b2:
    st.download_button("📄 Salvar Contrato em PDF", data=pdf_bytes, file_name=f"Contrato_{dados['nome'].replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
with b3:
    st.download_button("📊 Salvar Relatório em PDF", data=pdf_bytes, file_name=f"Relatorio_{dados['nome'].replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. RODAPÉ FIXO
# -----------------------------------------------------------------------------
st.markdown("""
    <div class='custom-footer'>
        <a href='https://tour360vr.com.br' target='_blank'>www.tour360vr.com.br</a> | 
        <a href='mailto:contato@tour360vr.com.br'>contato@tour360vr.com.br</a> | 
        Whatsapp: (16) 99133-2121 | 
        <b>Tour360VR - Gestão de Perfil do Google</b>
    </div>
""", unsafe_allow_html=True)

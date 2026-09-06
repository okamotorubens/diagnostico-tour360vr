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
# 2. FUNÇÕES UTILITÁRIAS
# -----------------------------------------------------------------------------
def conv(texto):
    if not texto: return ""
    limpo = str(texto).replace("•", "- ").replace("✓", "[OK] ").replace("📍", "").replace("📞", "").replace("🌐", "").replace("Brazil", "Brasil")
    return limpo.encode('latin-1', 'replace').decode('latin-1')

def formatar_estrelas(nota):
    try:
        val = int(round(float(nota)))
        return "*" * max(0, min(5, val))
    except:
        return "*****"

def calcular_score_real(dados):
    score = 100
    if not dados.get("tem_tour360", False): score -= 20
    if dados.get("website") == "Não possui" or not dados.get("website"): score -= 15
    if not dados.get("tem_fotos_hd", False): score -= 15
    if not dados.get("categorias_completas", False): score -= 15
    if not dados.get("horarios_ok", False): score -= 10
    if not dados.get("tem_descricao", False): score -= 10
    if dados.get("avaliacoes", 0) < 50: score -= 15
    return max(score, 10)

def obter_caminho_logo():
    caminhos = ['assets/Logo_TOUR_transparente.png', 'Logo_TOUR_transparente.png', 'assets/Logo TOUR transparente.png']
    for c in caminhos:
        if os.path.exists(c): return c
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
        "categorias_detectadas": []
    }

if 'planos' not in st.session_state:
    st.session_state['planos'] = {
        "start_valor": "500,00",
        "start_itens": "- Correção cadastral\n- Otimização de SEO\n- Ajuste de categorias\n- Inserção de links",
        "pro_valor": "1.200,00",
        "pro_itens": "- Tudo do Plano Start\n- Tour Virtual 360°\n- Ensaio Fotográfico HD\n- Relatório Visual de Entrega",
        "gestao_valor": "600,00",
        "gestao_itens": "- Postagens semanais\n- Gestão de avaliações\n- Atualização de fotos\n- Relatório mensal"
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
        if self.page_no() == 1: 
            return
        
        caminho_logo = obter_caminho_logo()
        if caminho_logo:
            try: 
                self.image(caminho_logo, 12, 6, 18)
            except: 
                pass
            
        self.set_xy(32, 10)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(30, 64, 175)
        self.cell(166, 4.5, 'TOUR360VR', align='L', ln=True)
        
        self.set_x(32)
        self.set_font('Helvetica', 'B', 8.5)
        self.set_text_color(100, 116, 139)
        self.cell(166, 4, conv('Gestão de Perfil & Diagnóstico do Google Meu Negócio'), align='L', ln=True)
        
        self.set_draw_color(226, 232, 240)
        self.line(12, 21.5, 198, 21.5)
        self.set_y(25)

    def footer(self):
        self.set_y(-16)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(100, 116, 139)
        self.line(12, self.get_y(), 198, self.get_y())
        self.set_y(-13)
        
        if self.page_no() == 1:
            self.set_x(12)
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(30, 64, 175)
            self.cell(186, 5, conv("Tour360VR - 16 99133 2121 - Ribeirão Preto - SP"), align='C')
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

def gerar_pdf_oficial(dados, score_input, planos, plano_acao_extra=""):
    score = calcular_score_real(dados)
    pdf = PDFTour360Oficial()
    pdf.set_auto_page_break(auto=True, margin=18)
    estrelas_txt = formatar_estrelas(dados['nota'])

    # PÁGINA 1: CAPA
    pdf.add_page()
    caminho_logo = obter_caminho_logo()
    if caminho_logo:
        try:
            pdf.image(caminho_logo, 82, 22, 46)
        except:
            pass

    pdf.set_y(74)
    pdf.set_font('Helvetica', 'B', 23)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 10, conv('DIAGNÓSTICO DE PRESENÇA DIGITAL'), align='C', ln=True)
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 19)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 8, conv('GOOGLE MEU NEGÓCIO'), align='C', ln=True)
    pdf.ln(12)

    w_capa = 170
    h_capa = 68
    x_capa = (210 - w_capa) / 2.0
    y_capa = 126

    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rounded_rect(x_capa, y_capa, w_capa, h_capa, 4, 'FD')

    pdf.set_xy(x_capa, y_capa + 6)
    pdf.set_font('Helvetica', 'B', 21)
    pdf.set_text_color(30, 64, 175) 
    pdf.cell(w_capa, 10, conv(f"{dados['nome'] or 'Nome da Empresa'}"), align='C', ln=True)
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.set_x(x_capa)
    pdf.cell(w_capa, 6.5, conv(f"Cliente: {dados['contato'] or 'Responsável'}"), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.set_x(x_capa)
    pdf.cell(w_capa, 5.5, conv(f"{dados['endereco'] or 'Endereço não informado'}"), align='C', ln=True)
    
    site_txt = dados['website'] if dados['website'] else 'N/I'
    pdf.set_x(x_capa)
    pdf.cell(w_capa, 5.5, conv(f"Telefone: {dados['telefone'] or 'N/I'}   |   {site_txt}"), align='C', ln=True)
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_x(x_capa)
    if score < 50:
        pdf.set_text_color(239, 68, 68)
        pdf.cell(w_capa, 6, conv("Status da Ficha: Crítico (Visibilidade Comprometida)"), align='C', ln=True)
    else:
        pdf.set_text_color(22, 128, 61)
        pdf.cell(w_capa, 6, conv("Status da Ficha: Otimizado e Em Expansão"), align='C', ln=True)

    # PÁGINA 2: DIAGNÓSTICO
    pdf.add_page()
    pdf.set_y(30)
    pdf.set_font('Helvetica', 'B', 17)
    pdf.set_text_color(15, 23, 42)
    
    pdf.cell(0, 7, conv('AUDITORIA DETALHADA DE PONTOS DE BUSCA'), align='C', ln=True)
    pdf.ln(8)

    w_ficha = 145
    x_ficha = (210 - w_ficha) / 2.0
    
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(x_ficha, pdf.get_y(), w_ficha, 28, 3, 'FD')
    
    y_curr = pdf.get_y()
    pdf.set_xy(x_ficha, y_curr + 3.5)
    
    pdf.set_font('Helvetica', 'B', 11.0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_ficha, 5.0, conv('FICHA ANALISADA'), align='C', ln=True)
    pdf.ln(1)
    
    pdf.set_x(x_ficha)
    pdf.set_font('Helvetica', 'B', 14.5)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(w_ficha, 7.0, conv(f"{dados['nome'] or 'Empresa Analisada'}"), align='C', ln=True)
    pdf.ln(1)

    pdf.set_x(x_ficha)
    pdf.set_font('Helvetica', 'B', 13.0)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(w_ficha, 5.5, conv(f"Nota {dados['nota']:.1f} {estrelas_txt}   -   {dados['avaliacoes']} avaliações no Google"), align='C', ln=True)

    # QUADRO SCORE GERAL
    pdf.set_y(y_curr + 35)
    w_box_score = 75
    x_box_score = (210 - w_box_score) / 2.0
    y_box_score = pdf.get_y()
    
    if score < 50:
        cr, cg, cb = 239, 68, 68
        status_txt = "STATUS CRÍTICO"
    elif score < 80:
        cr, cg, cb = 245, 158, 11
        status_txt = "STATUS MÉDIO"
    else:
        cr, cg, cb = 22, 128, 61
        status_txt = "ALTO DESEMPENHO"

    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(62, 161, 219)
    pdf.set_line_width(0.5)
    pdf.rounded_rect(x_box_score, y_box_score, w_box_score, 17, 3, 'FD')
    pdf.set_line_width(0.2)

    pdf.set_xy(x_box_score, y_box_score + 1.5)
    pdf.set_font('Helvetica', 'B', 19)
    pdf.set_text_color(cr, cg, cb)
    
    str_score = f"{score} "
    str_100 = "/ 100"
    w_part1 = pdf.get_string_width(str_score)
    w_part2 = pdf.get_string_width(str_100)
    x_start_text = x_box_score + ((w_box_score - (w_part1 + w_part2)) / 2.0)
    
    pdf.set_x(x_start_text)
    pdf.write(7, conv(str_score))
    pdf.set_text_color(15, 23, 42)
    pdf.write(7, conv(str_100))
    
    pdf.set_xy(x_box_score, y_box_score + 10)
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(cr, cg, cb)
    pdf.cell(w_box_score, 4, conv(f"SCORE GERAL ({status_txt})"), align='C', ln=True)

    pdf.set_y(y_box_score + 28)

    pct_avaliacoes = min(int((dados['avaliacoes'] / 50.0) * 100), 100) if dados['avaliacoes'] > 0 else 10
    pct_fotos = 100 if dados['tem_fotos_hd'] else 30
    pct_tour = 100 if dados['tem_tour360'] else 0
    pct_cat = 100 if dados['categorias_completas'] else 50
    pct_hor = 100 if dados['horarios_ok'] else 40
    pct_web = 100 if dados['website'] != 'Não possui' and dados['website'] != '' else 10
    pct_desc = 100 if dados.get('tem_descricao', True) else 30
    pct_atrib = 100 if dados.get('atributos_ok', True) else 40
    pct_resp = 100 if dados.get('resposta_avaliacoes_ok', False) else 30

    desc_fotos = "Atende ao volume recomendado de fotos em HD." if dados['tem_fotos_hd'] else "Poucas fotos encontradas / antigas no perfil."
    desc_tour = "Tour Virtual 360° ativo e integrado." if dados['tem_tour360'] else "Nenhum Tour 360 detectado no perfil do Google."
    desc_cat = "Atende às categorias principais e secundárias recomendadas." if dados['categorias_completas'] else "Ajuste necessário em categorias secundárias no perfil."
    desc_web = f"Website oficial: {dados['website']}" if dados['website'] != 'Não possui' and dados['website'] != '' else "Falta link de website cadastrado para conversão."
    desc_desc = "Resumo editorial ativo no perfil." if dados.get('tem_descricao', True) else "Descrição da empresa incompleta ou ausente."
    desc_atrib = "Atributos de serviços e acessibilidade ativos." if dados.get('atributos_ok', True) else "Falta cadastrar atributos de acessibilidade/serviços."
    desc_resp = "Boa frequência de respostas do proprietário." if dados.get('resposta_avaliacoes_ok', False) else "Falta de respostas oficiais do proprietário às avaliações."

    itens = [
        ("1. Fotos e Resolução Visual", pct_fotos, "Alto" if dados['tem_fotos_hd'] else "Baixo", desc_fotos),
        ("2. Tour Virtual 360° Interativo", pct_tour, "Ativo" if dados['tem_tour360'] else "Ausente", desc_tour),
        ("3. Categorias Principal e Secundárias", pct_cat, "Completo" if dados['categorias_completas'] else "Incompleto", desc_cat),
        ("4. Horários e Exceções (Feriados)", pct_hor, "Atualizado" if dados['horarios_ok'] else "Desatualizado", "Falta de horários especiais em feriados."),
        ("5. Website e Links de Conversão", pct_web, "Ativo" if dados['website'] != 'Não possui' and dados['website'] != '' else "Falho", desc_web),
        ("6. Avaliações no Google (Prova Social)", pct_avaliacoes, f"{dados['nota']}/5.0", f"{dados['avaliacoes']} avaliações registradas."),
        ("7. Resumo Editorial & Descrição", pct_desc, "Completo" if dados.get('tem_descricao', True) else "Ausente", desc_desc),
        ("8. Atributos de Acessibilidade/Serviços", pct_atrib, "Ativo" if dados.get('atributos_ok', True) else "Pendente", desc_atrib),
        ("9. Interação e Resposta a Avaliações", pct_resp, "Ativo" if dados.get('resposta_avaliacoes_ok', False) else "Pendente", desc_resp)
    ]

    for titulo, pct, rotulo, desc in itens:
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(130, 3.5, conv(titulo), ln=False)
        
        pdf.set_font('Helvetica', 'B', 9.5)
        if pct < 40: pdf.set_text_color(239, 68, 68)
        elif pct < 80: pdf.set_text_color(245, 158, 11)
        else: pdf.set_text_color(22, 128, 61)
            
        pdf.cell(56, 3.5, conv(rotulo), align='R', ln=True)

        pdf.set_fill_color(226, 232, 240)
        pdf.rounded_rect(12, pdf.get_y(), 186, 2.4, 1.0, 'F')
        
        if pct < 40: pdf.set_fill_color(239, 68, 68)
        elif pct < 80: pdf.set_fill_color(245, 158, 11)
        else: pdf.set_fill_color(22, 128, 61)
            
        largura_barra = max(float(pct) * 1.86, 4.0)
        pdf.rounded_rect(12, pdf.get_y(), largura_barra, 2.4, 1.0, 'F')
        pdf.ln(3.0)

        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(0, 3.5, conv(f"  Diagnóstico: {desc}"), ln=True)
        pdf.ln(2.0)

    # PLANO DE AÇÃO
    if plano_acao_extra and plano_acao_extra.strip() != "":
        pdf.ln(6)
        w_extra = 170
        x_extra = (210 - w_extra) / 2.0
        
        pdf.set_fill_color(240, 249, 255)
        pdf.set_draw_color(62, 161, 219)
        pdf.set_line_width(0.5)
        
        y_extra = pdf.get_y()
        pdf.rounded_rect(x_extra, y_extra, w_extra, 25, 2.5, 'FD')
        pdf.set_line_width(0.2)
        
        pdf.set_xy(x_extra, y_extra + 3)
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(w_extra, 4, conv("PLANO DE AÇÃO E APONTAMENTOS ESTRATÉGICOS PERSONALIZADOS:"), align='C', ln=True)
        
        pdf.set_xy(x_extra + 5, y_extra + 9)
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(w_extra - 10, 3.8, conv(plano_acao_extra), align='L')

    # PÁGINA 3: PLANOS
    pdf.add_page()
    pdf.set_y(30)
    pdf.set_font('Helvetica', 'B', 17)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('PROPOSTA COMERCIAL & ESTRUTURAÇÃO ESTRATÉGICA'), align='C', ln=True)
    pdf.ln(10)

    pdf.set_font('Helvetica', 'B', 17)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, conv('PLANOS E INVESTIMENTO'), align='C', ln=True)
    pdf.ln(10)

    y_p = pdf.get_y() + 2
    
    # Plano Start
    val_start_limpo = str(planos['start_valor']).replace("/mês", "").replace("/mes", "").strip()
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(12, y_p, 54, 62, 2, 'FD')
    
    pdf.set_xy(12, y_p + 3.5)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(54, 5, 'Plano Start', align='C', ln=True)
    
    pdf.set_xy(12, y_p + 10)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(54, 5, conv(f"R$ {val_start_limpo}"), align='C', ln=True)
    
    pdf.set_xy(12, y_p + 16)
    pdf.set_font('Helvetica', 'B', 10.0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(54, 4, conv('em até 2x'), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 9.0)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(15, y_p + 26)
    pdf.multi_cell(48, 4.5, conv(planos['start_itens']), align='L')

    # Plano Pro
    val_pro_limpo = str(planos['pro_valor']).replace("/mês", "").replace("/mes", "").strip()
    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(30, 64, 175)
    pdf.set_line_width(1.2)
    pdf.rounded_rect(70, y_p - 4, 70, 70, 3, 'FD')
    pdf.set_line_width(0.2)
    
    pdf.set_xy(70, y_p - 1)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(70, 5, conv('Plano Pro'), align='C', ln=True)
    
    pdf.set_xy(70, y_p + 5.0)
    pdf.set_font('Helvetica', 'B', 9.0)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(70, 4, conv('RECOMENDADO'), align='C', ln=True)
    
    pdf.set_xy(70, y_p + 10.5)
    pdf.set_font('Helvetica', 'B', 19)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(70, 7, conv(f"R$ {val_pro_limpo}"), align='C', ln=True)
    
    pdf.set_xy(70, y_p + 18.5)
    pdf.set_font('Helvetica', 'B', 10.0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(70, 4, conv('em até 3x'), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(15, 23, 42)
    pdf.set_xy(75, y_p + 27.5)
    pdf.multi_cell(60, 4.8, conv(planos['pro_itens']), align='L')

    # Gestão Mensal
    val_gestao_limpo = str(planos['gestao_valor']).replace("/mês", "").replace("/mes", "").strip()
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(144, y_p, 54, 62, 2, 'FD')
    
    pdf.set_xy(144, y_p + 3.5)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(54, 5, conv('Gestão Mensal'), align='C', ln=True)
    
    pdf.set_xy(144, y_p + 10)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(54, 5, conv(f"R$ {val_gestao_limpo}"), align='C', ln=True)
    
    pdf.set_xy(144, y_p + 16)
    pdf.set_font('Helvetica', 'B', 10.0)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(54, 4, conv('valor mensal'), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 9.0)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(147, y_p + 26)
    pdf.multi_cell(48, 4.5, conv(planos['gestao_itens']), align='L')

    # QUADRO INFORMATIVO
    pdf.set_y(y_p + 74)
    w_info = 170
    x_info = (210 - w_info) / 2.0
    
    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(62, 161, 219)
    pdf.set_line_width(0.5)
    pdf.rounded_rect(x_info, pdf.get_y(), w_info, 28, 2, 'FD')
    pdf.set_line_width(0.2)

    y_info = pdf.get_y() + 3
    pdf.set_xy(x_info, y_info)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_info, 5, conv('POR QUE SEU NEGÓCIO PRECISA DE OTIMIZAÇÃO PROFISSIONAL?'), align='C', ln=True)
    pdf.ln(1)

    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    txt_exp = (
        "Mais de 80% das buscas locais no Google e Maps resultam em uma ação imediata (ligação, rota ou mensagem).\n"
        "Perfis com fotos profissionais e Tour Virtual 360° geram até 2x mais interesse e permanecem no topo das buscas.\n"
        "Fichas incompletas ou desatualizadas perdem clientes diariamente para concorrentes diretos com nota mais alta."
    )
    pdf.set_x(x_info)
    pdf.multi_cell(w_info, 4.0, conv(txt_exp), align='C')

    # PÁGINA 4: CONTRATO
    pdf.add_page()
    pdf.set_y(30)
    pdf.set_font('Helvetica', 'B', 17)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('CONTRATO DE PRESTAÇÃO DE SERVIÇOS'), align='C', ln=True)
    pdf.ln(8)

    pdf.set_font('Helvetica', '', 9.0)
    pdf.set_text_color(51, 65, 85)
    pdf.set_font('Helvetica', 'B', 9.0)
    pdf.write(4.5, conv("CONTRATADA: "))
    pdf.set_font('Helvetica', '', 9.0)
    pdf.write(4.5, conv("Tour360VR, representada por Rubens H. Okamoto, CPF: 287.932.298-79 e Telefone: (16) 99133-2121.\n\n"))
    
    pdf.set_font('Helvetica', 'B', 9.0)
    pdf.write(4.5, conv("CONTRATANTE: "))
    pdf.set_font('Helvetica', '', 9.0)
    pdf.write(4.5, conv(f"{dados['nome'] or 'Empresa Contratante'}, representada por {dados['contato'] or 'Responsável'}, {dados['endereco'] or 'Endereço'}, Telefone: {dados['telefone'] or 'N/I'}.\n\n"))
    
    pdf.set_font('Helvetica', '', 9.0)
    pdf.write(4.5, conv("A "))
    pdf.set_font('Helvetica', 'B', 9.0)
    pdf.write(4.5, conv("CONTRATADA "))
    pdf.set_font('Helvetica', '', 9.0)
    pdf.write(4.5, conv("compromete-se a executar os serviços de otimização, reestruturação técnica e/ou produção de Tour Virtual 360° para o perfil do Google da "))
    pdf.set_font('Helvetica', 'B', 9.0)
    pdf.write(4.5, conv("CONTRATANTE.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.0)
    pdf.write(4.5, conv("CLÁUSULA PRIMEIRA - DO OBJETO: "))
    pdf.set_font('Helvetica', '', 9.0)
    pdf.write(4.5, conv("Os serviços serão iniciados em até 5 dias úteis após o fornecimento dos acessos e informações necessárias ao perfil.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.0)
    pdf.write(4.5, conv("CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES: "))
    pdf.set_font('Helvetica', '', 9.0)
    pdf.write(4.5, conv("O não pagamento na data acordada sujeitará o presente contrato à incidência de juros legais de mora e interrupção temporária dos serviços.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.0)
    pdf.write(4.5, conv("CLÁUSULA TERCEIRA - SELEÇÃO DO PLANO CONTRATADO:\n"))
    pdf.set_font('Helvetica', '', 9.0)
    pdf.write(4.5, conv("(    ) Plano Start        (    ) Plano Pro        (    ) Gestão Mensal\n\n"))

    pdf.set_font('Helvetica', 'B', 9.0)
    pdf.write(4.5, conv("CLÁUSULA QUARTA - CONDIÇÕES DE PAGAMENTO:\n"))
    pdf.set_font('Helvetica', '', 9.0)
    pdf.write(6.0, conv("(    ) À Vista       (    ) 2x - Plano Start       (    ) 3x - Plano Pro       (    ) Vencimento Dia: _____ - Gestão Mensal\n\n"))

    pdf.ln(12)
    
    pdf.cell(88, 5, '__________________________________', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, '__________________________________', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.cell(88, 4.5, 'Rubens H. Okamoto', align='C')
    pdf.cell(10, 4.5, '')
    pdf.cell(88, 4.5, conv(f"{dados['contato'] or 'Responsável'}"), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(88, 4.5, 'TOUR360VR', align='C')
    pdf.cell(10, 4.5, '')
    pdf.cell(88, 4.5, conv(f"{dados['nome'] or 'Empresa'}"), align='C', ln=True)

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
        
    nome_exibicao = st.session_state['dados']['nome'] if st.session_state['dados']['nome'] else "Novo Cliente"
    st.markdown(f"<p style='color: #94a3b8; font-size: 13px;'>Consultoria Pro: <b>{nome_exibicao}</b></p>", unsafe_allow_html=True)
    st.markdown("---")

    opcao_menu = st.radio(
        "Navegação do Sistema:",
        [
            "🔍 1. Consulta & Diagnóstico Rápido",
            "💡 2. Plano de Ação & Persuasão",
            "📜 3. Proposta Comercial & Planos",
            "📄 4. Contrato Profissional"
        ]
    )

st.markdown("<div class='main-header'>PLATAFORMA DE CONSULTORIA TOUR360VR - GESTÃO & DIAGNÓSTICO GOOGLE MEU NEGÓCIO</div>", unsafe_allow_html=True)
dados = st.session_state['dados']
score = calcular_score_real(dados)

# -----------------------------------------------------------------------------
# PAINEL CENTRAL - MÓDULOS DE USO
# -----------------------------------------------------------------------------

# MÓDULO 1: CONSULTA E DIAGNÓSTICO COMPLETO
if "1. Consulta" in opcao_menu:
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='card-title'>CAPA DE DIAGNÓSTICO: [{dados['nome'] or 'Novo Cliente'}]</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            nome_input = st.text_input("Nome da Empresa:", value="", key="input_empresa_nome", placeholder="Ex: Toque de Letra Comunicação")
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
                        url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,international_phone_number,website,rating,user_ratings_total,photos,opening_hours,types,editorial_summary&key={API_KEY_GOOGLE}"
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
                        st.session_state['dados']['atributos_ok'] = False
                        st.session_state['dados']['resposta_avaliacoes_ok'] = False
                        st.session_state['dados']['categorias_detectadas'] = types_lista
                        
                        st.success("Dados carregados com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao obter detalhes: {e}")

        st.markdown("---")
        st.markdown("<h3 id='ajuste-fino-dos-itens-da-auditoria' style='color: #ffffff; font-size: 16px; font-weight: 700;'>⚙️ AJUSTE FINO DOS ITENS DA AUDITORIA</h3>", unsafe_allow_html=True)
        
        c_a, c_b, c_c, c_d = st.columns(4)
        st.session_state['dados']['tem_tour360'] = c_a.checkbox("Tour 360°", value=st.session_state['dados']['tem_tour360'], key="chk_tour360_val")
        st.session_state['dados']['tem_fotos_hd'] = c_b.checkbox("Fotos HD", value=st.session_state['dados']['tem_fotos_hd'], key="chk_fotos_hd_val")
        st.session_state['dados']['categorias_completas'] = c_c.checkbox("Categorias OK", value=st.session_state['dados']['categorias_completas'], key="chk_cat_ok_val")
        st.session_state['dados']['horarios_ok'] = c_d.checkbox("Horários OK", value=st.session_state['dados']['horarios_ok'], key="chk_horarios_ok_val")
        
        c_e, c_f, c_g = st.columns(3)
        st.session_state['dados']['tem_descricao'] = c_e.checkbox("Descrição/Resumo", value=st.session_state['dados'].get('tem_descricao', False), key="chk_desc_val")
        st.session_state['dados']['atributos_ok'] = c_f.checkbox("Atributos Serviços", value=st.session_state['dados'].get('atributos_ok', False), key="chk_atrib_val")
        st.session_state['dados']['resposta_avaliacoes_ok'] = c_g.checkbox("Respostas Ativas", value=st.session_state['dados'].get('resposta_avaliacoes_ok', False), key="chk_resp_val")

        st.markdown("---")
        st.markdown("### ✍️ Edição dos Dados de Contato:")
        f_c1, f_c2 = st.columns(2)
        
        st.session_state['dados']['nome'] = f_c1.text_input("Nome da Empresa:", value=st.session_state['dados']['nome'], key=f"edit_nome_{st.session_state['dados']['nome']}")
        st.session_state['dados']['contato'] = f_c2.text_input("Nome do Responsável:", value=st.session_state['dados']['contato'], key=f"edit_contato_{st.session_state['dados']['contato']}")
        st.session_state['dados']['telefone'] = f_c1.text_input("Telefone / WhatsApp:", value=st.session_state['dados']['telefone'], key=f"edit_telefone_{st.session_state['dados']['telefone']}")
        st.session_state['dados']['website'] = f_c2.text_input("Website:", value=st.session_state['dados']['website'], key=f"edit_website_{st.session_state['dados']['website']}")
        st.session_state['dados']['endereco'] = st.text_input("Endereço Completo:", value=st.session_state['dados']['endereco'], key=f"edit_endereco_{st.session_state['dados']['endereco']}")

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
        
        if dados.get('categorias_detectadas'):
            st.markdown("---")
            st.markdown("**Tags/Categorias Apuradas no Google:**")
            st.caption(", ".join(dados['categorias_detectadas']))
            
        st.markdown("</div>", unsafe_allow_html=True)

# MÓDULO 2: PLANO DE AÇÃO
elif "2. Plano de Ação" in opcao_menu:
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

# MÓDULO 3: PROPOSTA COMERCIAL & VALORES
elif "3. Proposta" in opcao_menu:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>📜 EDITE OS VALORES E CONTEÚDO DOS PLANOS COMERCIAIS</div>", unsafe_allow_html=True)
    
    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.markdown("### 🔹 Plano Start")
        st.session_state['planos']['start_valor'] = st.text_input("Valor Start (R$):", value=st.session_state['planos']['start_valor'], key="edit_p_start_val")
        st.session_state['planos']['start_itens'] = st.text_area("Itens Plano Start:", value=st.session_state['planos']['start_itens'], height=160, key="edit_p_start_itens")
        
    with p2:
        st.markdown("### 🔹 Plano Pro")
        st.session_state['planos']['pro_valor'] = st.text_input("Valor Pro (R$):", value=st.session_state['planos']['pro_valor'], key="edit_p_pro_val")
        st.session_state['planos']['pro_itens'] = st.text_area("Itens Plano Pro:", value=st.session_state['planos']['pro_itens'], height=160, key="edit_p_pro_itens")
        
    with p3:
        st.markdown("### 🔹 Gestão Mensal")
        st.session_state['planos']['gestao_valor'] = st.text_input("Valor Gestão (R$):", value=st.session_state['planos']['gestao_valor'], key="edit_p_gestao_val")
        st.session_state['planos']['gestao_itens'] = st.text_area("Itens Gestão Mensal:", value=st.session_state['planos']['gestao_itens'], height=160, key="edit_p_gestao_itens")

    st.success("Valores e itens dos planos comerciais atualizados com sucesso!")
    st.markdown("</div>", unsafe_allow_html=True)

# MÓDULO 4: CONTRATO
elif "4. Contrato" in opcao_menu:
    st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>📄 CONTRATO DE PRESTAÇÃO DE SERVIÇOS</div>", unsafe_allow_html=True)
    st.info("O contrato é atualizado e gerado automaticamente na 4ª página do arquivo PDF completo com base nos dados informados nas etapas anteriores.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# UNIFICADO: ÚNICO BOTÃO GERADOR DE PDF COMPLETO
# -----------------------------------------------------------------------------
st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
st.markdown("<div class='card-title'>GERAR DOCUMENTO OFICIAL</div>", unsafe_allow_html=True)

pdf_bytes = gerar_pdf_oficial(dados, score, st.session_state['planos'], st.session_state['plano_acao_extra'])

nome_arquivo_pdf = dados['nome'].replace(' ', '_') if dados['nome'] else 'Novo_Cliente'
st.download_button(
    "📥 Baixar Diagnóstico, Proposta e Contrato Completo em PDF",
    data=pdf_bytes,
    file_name=f"Diagnostico_Proposta_Contrato_{nome_arquivo_pdf}.pdf",
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
        <a href='https://tour360vr.com.br' target='_blank'>www.tour360vr.com.br</a> | 
        <a href='mailto:contato@tour360vr.com.br'>contato@tour360vr.com.br</a> | 
        Whatsapp: (16) 99133-2121 | 
        <b>Tour360VR - Gestão de Perfil do Google</b>
    </div>
""", unsafe_allow_html=True)

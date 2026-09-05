import io
import requests
import streamlit as st
from fpdf import FPDF

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA DO STREAMLIT (TEMA DARK)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tour360VR - Plataforma de Consultoria e Diagnóstico",
    page_icon="🌐",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    
    .header-box { 
        border-bottom: 2px solid #1e40af; 
        padding-bottom: 12px; 
        margin-bottom: 25px; 
    }
    .header-title { color: #ffffff; font-size: 26px; font-weight: 700; margin: 0; }
    .header-title span { color: #ff3d3d; }
    .header-subtitle { color: #3ea1db; font-size: 14px; font-weight: 600; margin-top: 4px; }
    
    .card-dark { 
        background-color: #1e293b; 
        border: 1px solid #334155; 
        border-radius: 8px; 
        padding: 20px; 
        margin-bottom: 20px; 
    }
    .score-card { 
        background-color: #1e293b; 
        border: 2px solid #1e40af; 
        padding: 20px; 
        border-radius: 8px; 
        text-align: center; 
    }
    
    .footer { 
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
    }
    </style>
""", unsafe_allow_html=True)

API_KEY_GOOGLE = st.secrets.get("GOOGLE_PLACES_API_KEY", "")

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO DE ESTADOS NATIVOS EDITÁVEIS
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
        "horarios_ok": False
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

def conv(texto):
    """Trata a codificação para Latin-1 e substitui símbolos unicode incompatíveis."""
    if not texto:
        return ""
    limpo = str(texto)
    limpo = limpo.replace("•", "- ").replace("✓", "[OK] ").replace("X", "[X] ")
    limpo = limpo.replace("📍", "").replace("📞", "").replace("✉️", "").replace("🌐", "").replace("☐", "[ ]")
    return limpo.encode('latin-1', 'replace').decode('latin-1')

def formatar_estrelas(nota):
    """Gera visualização de estrelas limpa sem caracteres 'o'."""
    try:
        val = float(nota)
        cheias = int(round(val))
        cheias = max(0, min(5, cheias))
        return "*" * cheias
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

# -----------------------------------------------------------------------------
# 2. GERADOR DE PDF TOUR360VR
# -----------------------------------------------------------------------------
class PDFTour360Oficial(FPDF):
    def header(self):
        self.set_fill_color(30, 64, 175)
        self.rect(0, 0, 105, 4, 'F')
        self.set_fill_color(255, 61, 61)
        self.rect(105, 0, 105, 4, 'F')

        if self.page_no() == 1:
            return

        try:
            self.image('assets/Logo_TOUR_transparente.png', 12, 9, 18)
            x_pos = 34
        except:
            x_pos = 12

        self.set_xy(x_pos, 9.5)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(30, 64, 175)
        self.cell(0, 5, 'TOUR360VR', ln=True)
        self.set_xy(x_pos, 15.5)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, conv('Gestão de Perfil & Diagnóstico do Google Meu Negócio'), ln=True)
        
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.3)
        self.line(12, 23, 198, 23)
        self.set_line_width(0.2)
        self.ln(20)

    def footer(self):
        self.set_y(-16)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(100, 116, 139)
        self.set_draw_color(226, 232, 240)
        self.line(12, self.get_y(), 198, self.get_y())
        
        self.set_y(-13)
        w_col = (198 - 12) / 4.0
        self.set_x(12)
        self.cell(w_col, 5, 'www.tour360vr.com.br', link='https://tour360vr.com.br', align='C')
        self.cell(w_col, 5, 'contato@tour360vr.com.br', link='mailto:contato@tour360vr.com.br', align='C')
        self.cell(w_col, 5, 'WhatsApp: (16) 99133-2121', link='https://wa.me/5516991332121', align='C')
        self.cell(w_col, 5, f'Página {self.page_no()} de 4', align='C')

        self.set_fill_color(30, 64, 175)
        self.rect(0, 293.5, 105, 3.5, 'F')
        self.set_fill_color(255, 61, 61)
        self.rect(105, 293.5, 105, 3.5, 'F')

    def rounded_rect(self, x, y, w, h, r, style=''):
        k = self.k
        hp = self.h
        if style == 'F':
            op = 'f'
        elif style == 'FD' or style == 'DF':
            op = 'B'
        else:
            op = 'S'
        
        my_arc = 4/3 * (2**0.5 - 1)
        self._out(f'{(x+r)*k:.2f} {(hp-y)*k:.2f} m')
        xc = x + w - r
        yc = y + r
        self._out(f'{xc*k:.2f} {(hp-y)*k:.2f} l')
        self._arc(xc + r*my_arc, yc - r, xc + r, yc - r*my_arc, xc + r, yc)
        xc = x + w - r
        yc = y + h - r
        self._out(f'{(x+w)*k:.2f} {(hp-yc)*k:.2f} l')
        self._arc(xc + r, yc + r*my_arc, xc + r*my_arc, yc + r, xc, yc + r)
        xc = x + r
        yc = y + h - r
        self._out(f'{xc*k:.2f} {(hp-(y+h))*k:.2f} l')
        self._arc(xc - r*my_arc, yc + r, xc - r, yc + r*my_arc, xc - r, yc)
        xc = x + r
        yc = y + r
        self._out(f'{x*k:.2f} {(hp-yc)*k:.2f} l')
        self._arc(xc - r, yc - r*my_arc, xc - r*my_arc, yc - r, xc, yc - r)
        self._out(f'{op}')

    def _arc(self, x1, y1, x2, y2, x3, y3):
        k = self.k
        hp = self.h
        self._out(f'{x1*k:.2f} {(hp-y1)*k:.2f} {x2*k:.2f} {(hp-y2)*k:.2f} {x3*k:.2f} {(hp-y3)*k:.2f} c')

def gerar_pdf_oficial(dados, score_input, planos, plano_acao_extra=""):
    score = calcular_score_real(dados)
    pdf = PDFTour360Oficial()
    pdf.set_auto_page_break(auto=True, margin=18)
    
    estrelas_txt = formatar_estrelas(dados['nota'])

    # -------------------------------------------------------------------------
    # PÁGINA 1: CAPA
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    try:
        pdf.image('assets/Logo_TOUR_transparente.png', 82, 22, 46)
    except:
        pass

    pdf.set_y(74)
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 9, conv('DIAGNÓSTICO DE PRESENÇA DIGITAL'), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(0, 7, conv('GOOGLE MEU NEGÓCIO'), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 7, conv('Tour360VR'), align='C', ln=True)
    pdf.ln(14)

    w_capa = 180
    x_capa = (210 - w_capa) / 2.0
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rounded_rect(x_capa, 120, w_capa, 76, 4, 'FD')

    pdf.set_xy(x_capa, 126)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_capa, 8, conv(f"{dados['nome']}"), align='C', ln=True)
    
    pdf.set_x(x_capa)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(w_capa, 6, conv(f"Nota: {dados['nota']:.1f} {estrelas_txt}   ({dados['avaliacoes']} avaliações no Google)"), align='C', ln=True)
    pdf.ln(2)

    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(71, 85, 105)
    pdf.set_x(x_capa)
    pdf.cell(w_capa, 5, conv(f"Contato: {dados['contato']}"), align='C', ln=True)
    pdf.set_x(x_capa)
    pdf.cell(w_capa, 5, conv(f"{dados['endereco']}"), align='C', ln=True)
    pdf.set_x(x_capa)
    pdf.cell(w_capa, 5, conv(f"Telefone: {dados['telefone']}   |   Website: {dados['website']}"), align='C', ln=True)
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 10.5)
    pdf.set_x(x_capa)
    if score < 50:
        pdf.set_text_color(239, 68, 68)
        pdf.cell(w_capa, 6, conv("Status da Ficha: Crítico (Visibilidade Comprometida)"), align='C', ln=True)
    else:
        pdf.set_text_color(34, 197, 94)
        pdf.cell(w_capa, 6, conv("Status da Ficha: Otimizado e Em Expansão"), align='C', ln=True)

    # -------------------------------------------------------------------------
    # PÁGINA 2: DIAGNÓSTICO DETALHADO DA FICHA, SCORE E PLANO DE AÇÃO
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    w_ficha = 186
    x_ficha = (210 - w_ficha) / 2.0
    
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(x_ficha, 34, w_ficha, 40, 3, 'FD')
    
    pdf.set_xy(x_ficha, 36)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(w_ficha, 4, conv('FICHA ANALISADA DO CLIENTE'), align='C', ln=True)
    
    pdf.set_x(x_ficha)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_ficha, 6, conv(f"{dados['nome']}"), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(245, 158, 11)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.5, conv(f"Nota {dados['nota']:.1f} {estrelas_txt}   -   {dados['avaliacoes']} avaliações no Google"), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(71, 85, 105)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4, conv(f"{dados['endereco']}"), align='C', ln=True)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4, conv(f"Telefone: {dados['telefone']}   |   Website: {dados['website']}"), align='C', ln=True)

    pdf.set_y(78)
    if score < 50:
        cr, cg, cb = 239, 68, 68
        status_txt = "STATUS CRÍTICO"
    elif score < 80:
        cr, cg, cb = 245, 158, 11
        status_txt = "STATUS MÉDIO"
    else:
        cr, cg, cb = 34, 197, 94
        status_txt = "ALTO DESEMPENHO"

    # COMPACTAÇÃO DO QUADRO DO SCORE (MAIS QUADRADO)
    w_score = 80
    x_score = (210 - w_score) / 2.0
    
    pdf.set_fill_color(cr, cg, cb)
    pdf.set_draw_color(cr, cg, cb)
    pdf.rounded_rect(x_score, 78, w_score, 18, 3, 'FD')
    
    pdf.set_xy(x_score, 80)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(w_score, 6, conv(f"{score} / 100"), align='C', ln=True)
    
    pdf.set_xy(x_score, 88)
    pdf.set_font('Helvetica', 'B', 7.5)
    pdf.cell(w_score, 4, conv(f"SCORE GERAL ({status_txt})"), align='C', ln=True)

    pdf.set_y(102)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, conv('AUDITORIA DETALHADA DE PONTOS DE BUSCA'), align='C', ln=True)
    pdf.ln(6)

    pct_avaliacoes = min(int((dados['avaliacoes'] / 50.0) * 100), 100) if dados['avaliacoes'] > 0 else 10

    desc_fotos = "Atende ao volume recomendado de fotos em HD." if dados['tem_fotos_hd'] else "Poucas fotos encontradas / antigas no perfil."
    desc_tour = "Tour Virtual 360° ativo e integrado." if dados['tem_tour360'] else "Nenhum Tour 360 detectado no perfil do Google."
    desc_web = f"Website oficial: {dados['website']}" if dados['website'] != 'Não possui' else "Falta link de website cadastrado para conversão."

    itens = [
        ("1. Fotos e Resolução Visual", 100 if dados['tem_fotos_hd'] else 30, "Alto" if dados['tem_fotos_hd'] else "Baixo", desc_fotos),
        ("2. Tour Virtual 360° Interativo", 100 if dados['tem_tour360'] else 0, "Ativo" if dados['tem_tour360'] else "Ausente", desc_tour),
        ("3. Categorias Principal e Secundárias", 100 if dados['categorias_completas'] else 50, "Completo" if dados['categorias_completas'] else "Incompleto", "Ajuste necessário em categorias secundárias."),
        ("4. Horários e Exceções (Feriados)", 100 if dados['horarios_ok'] else 40, "Atualizado" if dados['horarios_ok'] else "Desatualizado", "Falta de horários especiais em feriados."),
        ("5. Website e Links de Conversão", 100 if dados['website'] != 'Não possui' else 10, "Ativo" if dados['website'] != 'Não possui' else "Falho", desc_web),
        ("6. Avaliações no Google (Prova Social)", pct_avaliacoes, f"{dados['nota']}/5.0", f"{dados['avaliacoes']} avaliações registradas.")
    ]

    for titulo, pct, rotulo, desc in itens:
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(120, 3.8, conv(titulo), ln=False)
        
        pdf.set_font('Helvetica', 'B', 8.5)
        if pct < 40:
            pdf.set_text_color(239, 68, 68)
        elif pct < 80:
            pdf.set_text_color(245, 158, 11)
        else:
            pdf.set_text_color(34, 197, 94)
            
        pdf.cell(66, 3.8, conv(f"| {pct}% - {rotulo}"), align='R', ln=True)

        pdf.set_fill_color(226, 232, 240)
        pdf.rounded_rect(12, pdf.get_y(), 186, 3, 1.5, 'F')
        
        if pct < 40:
            pdf.set_fill_color(239, 68, 68)
        elif pct < 80:
            pdf.set_fill_color(245, 158, 11)
        else:
            pdf.set_fill_color(34, 197, 94)
            
        largura_barra = max(float(pct) * 1.86, 4.0)
        pdf.rounded_rect(12, pdf.get_y(), largura_barra, 3, 1.5, 'F')
        pdf.ln(3.8)

        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 3, conv(f"  Diagnóstico: {desc}"), ln=True)
        pdf.ln(2)

    # BLOCO DO PLANO DE AÇÃO EXTRA
    if plano_acao_extra and plano_acao_extra.strip() != "":
        pdf.ln(2)
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(203, 213, 225)
        
        y_extra = pdf.get_y()
        pdf.rounded_rect(12, y_extra, 186, 24, 2, 'FD')
        
        pdf.set_xy(15, y_extra + 2)
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(180, 4, conv("PLANO DE AÇÃO E APONTAMENTOS ESTRATÉGICOS PERSONALIZADOS:"), ln=True)
        
        pdf.set_x(15)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(180, 3.6, conv(plano_acao_extra))

    # -------------------------------------------------------------------------
    # PÁGINA 3: PROPOSTA COMERCIAL & PLANOS CENTRALIZADOS
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    pdf.set_y(32)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('PROPOSTA COMERCIAL & ESTRUTURAÇÃO ESTRATÉGICA'), align='C', ln=True)
    pdf.ln(8)

    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(62, 161, 219)
    pdf.set_line_width(0.6)
    pdf.rounded_rect(12, pdf.get_y(), 186, 36, 2, 'FD')
    pdf.set_line_width(0.2)

    y_info = pdf.get_y() + 3
    pdf.set_xy(12, y_info)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(186, 5, conv('POR QUE SEU NEGÓCIO PRECISA DE OTIMIZAÇÃO PROFISSIONAL?'), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(51, 65, 85)
    txt_exp = (
        "Mais de 80% das buscas locais no Google e Maps resultam em uma ação imediata (ligação, rota ou mensagem).\n"
        "Perfis com fotos profissionais e Tour Virtual 360° geram até 2x mais interesse e permanecem no topo das buscas.\n"
        "Fichas incompletas ou desatualizadas perdem clientes diariamente para concorrentes diretos com nota mais alta."
    )
    pdf.set_x(12)
    pdf.multi_cell(186, 4.5, conv(txt_exp), align='C')
    
    pdf.set_y(98)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('PROPOSTA DE PLANOS E INVESTIMENTO'), align='C', ln=True)
    pdf.ln(8)

    y_p = pdf.get_y() + 2
    
    # --- PLANO START ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(12, y_p + 2, 54, 60, 2, 'FD')
    
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
    pdf.set_xy(15, y_p + 22)
    pdf.multi_cell(48, 4.2, conv(planos['start_itens']), align='L')

    # --- PLANO PRO (DESTACADO E CENTRALIZADO) ---
    pdf.set_fill_color(238, 242, 255)
    pdf.set_draw_color(30, 64, 175)
    pdf.set_line_width(1.2)
    pdf.rounded_rect(70, y_p - 4, 70, 68, 3, 'FD')
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
    pdf.set_xy(74, y_p + 23)
    pdf.multi_cell(62, 4.8, conv(planos['pro_itens']), align='L')

    # --- GESTÃO MENSAL ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(144, y_p + 2, 54, 60, 2, 'FD')
    
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
    pdf.set_xy(147, y_p + 22)
    pdf.multi_cell(48, 4.2, conv(planos['gestao_itens']), align='L')

    # -------------------------------------------------------------------------
    # PÁGINA 4: CONTRATO (SEM A/C:)
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    pdf.set_y(32)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('CONTRATO DE PRESTAÇÃO DE SERVIÇOS'), align='C', ln=True)
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
    pdf.write(5.5, conv(f"{dados['nome']}, Responsável: {dados['contato']}, {dados['endereco']}, Telefone: {dados['telefone']}.\n\n"))
    
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

    pdf.ln(16)

    pdf.cell(88, 5, '__________________________________', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, '__________________________________', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(88, 5, 'TOUR360VR (Rubens H. Okamoto)', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, conv(f"{dados['nome']}"), align='C', ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 3. INTERFACE STREAMLIT COM MENU LATERAL E SEÇÕES EDITÁVEIS
# -----------------------------------------------------------------------------
st.sidebar.markdown("""
    <div style='text-align: center; padding-bottom: 15px;'>
        <h2 style='color: #ffffff; margin: 0;'>TOUR<span style='color: #ff3d3d;'>360VR</span></h2>
        <p style='color: #3ea1db; font-size: 12px; margin-top: 2px;'>Plataforma de Consultoria</p>
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

st.markdown("""
    <div class="header-box">
        <div class="header-title">PLATAFORMA DE CONSULTORIA <span>TOUR360VR</span></div>
        <div class="header-subtitle">GESTÃO & DIAGNÓSTICO DO GOOGLE MEU NEGÓCIO</div>
    </div>
""", unsafe_allow_html=True)

# CALCULO DINAMICO DO SCORE
score_calculado = calcular_score_real(st.session_state['dados'])
st.session_state['score'] = score_calculado

# -----------------------------------------------------------------------------
# ETAPA 1: CONSULTA & DIAGNÓSTICO
# -----------------------------------------------------------------------------
if "🔍" in opcao_menu:
    st.subheader("🔍 1. Dados do Cliente & Diagnóstico")
    
    col_busca, col_cidade = st.columns([2, 1])
    with col_busca:
        nome_input = st.text_input("🏢 Nome do Estabelecimento:", value=st.session_state['dados']['nome'])
        st.session_state['dados']['nome'] = nome_input
    with col_cidade:
        cidade_empresa = st.text_input("📍 Cidade / Estado da Busca:", value="Ribeirão Preto, SP")

    if st.button("🚀 Buscar e Atualizar Dados no Google", use_container_width=True):
        if nome_input:
            termo_busca = f"{nome_input}, {cidade_empresa}" if cidade_empresa else nome_input
            
            if API_KEY_GOOGLE:
                try:
                    url_search = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={termo_busca}&key={API_KEY_GOOGLE}"
                    res_search = requests.get(url_search).json()
                    
                    if res_search.get("results"):
                        place = res_search["results"][0]
                        place_id = place.get("place_id")
                        
                        url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,international_phone_number,website,rating,user_ratings_total,photos&key={API_KEY_GOOGLE}"
                        res_details = requests.get(url_details).json().get("result", {})
                        
                        photos = res_details.get("photos", place.get("photos", []))
                        
                        st.session_state['dados']['nome'] = res_details.get("name", place.get("name", nome_input))
                        st.session_state['dados']['endereco'] = res_details.get("formatted_address") or place.get("formatted_address") or f"{cidade_empresa}"
                        st.session_state['dados']['telefone'] = res_details.get("formatted_phone_number") or res_details.get("international_phone_number") or "Não informado"
                        st.session_state['dados']['website'] = res_details.get("website", "Não possui")
                        st.session_state['dados']['nota'] = res_details.get("rating", place.get("rating", 4.2))
                        st.session_state['dados']['avaliacoes'] = res_details.get("user_ratings_total", place.get("user_ratings_total", 38))
                        st.session_state['dados']['tem_fotos_hd'] = len(photos) > 10
                except Exception as e:
                    st.error(f"Erro na conexão com o Google: {e}")

            st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Ajuste Fino dos Itens da Auditoria:")
    
    col_chk1, col_chk2, col_chk3, col_chk4 = st.columns(4)
    with col_chk1:
        st.session_state['dados']['tem_tour360'] = st.checkbox("Possui Tour 360°?", value=st.session_state['dados']['tem_tour360'])
    with col_chk2:
        st.session_state['dados']['tem_fotos_hd'] = st.checkbox("Possui Fotos HD?", value=st.session_state['dados']['tem_fotos_hd'])
    with col_chk3:
        st.session_state['dados']['categorias_completas'] = st.checkbox("Categorias OK?", value=st.session_state['dados']['categorias_completas'])
    with col_chk4:
        st.session_state['dados']['horarios_ok'] = st.checkbox("Horários OK?", value=st.session_state['dados']['horarios_ok'])

    st.markdown("---")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.session_state['dados']['contato'] = st.text_input("👤 Nome do Contato / Responsável:", value=st.session_state['dados']['contato'])
        st.session_state['dados']['endereco'] = st.text_input("📍 Endereço Completo:", value=st.session_state['dados']['endereco'])
    with col_f2:
        st.session_state['dados']['telefone'] = st.text_input("📞 Telefone / WhatsApp:", value=st.session_state['dados']['telefone'])
        st.session_state['dados']['website'] = st.text_input("🌐 Website Cadastrado:", value=st.session_state['dados']['website'])

    dados = st.session_state['dados']
    score = calcular_score_real(dados)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
            <div class="score-card">
                <h2 style="color: #ff3d3d; font-size: 48px; margin: 0;">{score} / 100</h2>
                <p style="color: #cbd5e1; text-transform: uppercase; font-size: 13px; font-weight: bold;">Score Geral de Otimização</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="card-dark">
                <h3 style="color: #3ea1db; margin-top: 0;">{dados['nome']}</h3>
                <p style="margin: 4px 0;">👤 <strong>Contato:</strong> {dados['contato']}</p>
                <p style="margin: 4px 0;">📍 {dados['endereco']}</p>
                <p style="margin: 4px 0;">📞 <strong>Telefone:</strong> {dados['telefone']}</p>
                <p style="margin: 4px 0;">🌐 <strong>Website:</strong> {dados['website']}</p>
                <p style="margin: 4px 0;">⭐ <strong>Avaliações:</strong> {dados['nota']} ({dados['avaliacoes']} avaliações)</p>
            </div>
        """, unsafe_allow_html=True)

    pdf_bytes = gerar_pdf_oficial(dados, score, st.session_state['planos'], st.session_state['plano_acao_extra'])

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
    st.info("O contrato é atualizado e gerado automaticamente na 4ª página do PDF completo de acordo com os dados editados nas etapas anteriores.")

# -----------------------------------------------------------------------------
# 4. RODAPÉ FIXO DO APP
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="footer">
        Tour360VR • tour360vr.com.br • contato@tour360vr.com.br • WhatsApp: (16) 99133-2121
    </div>
""", unsafe_allow_html=True)

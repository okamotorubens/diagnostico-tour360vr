import io
import requests
import streamlit as st
from fpdf import FPDF

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA DO STREAMLIT (TEMA DARK NO APP)
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

def conv(texto):
    """Trata a codificação para Latin-1 e substitui símbolos unicode incompatíveis por caracteres seguros para FPDF."""
    if not texto:
        return ""
    limpo = str(texto)
    limpo = limpo.replace("•", "- ").replace("✓", "[OK] ").replace("X", "[X] ")
    limpo = limpo.replace("📍", "").replace("📞", "").replace("⭐", "").replace("✉️", "").replace("🌐", "").replace("★", "*").replace("☆", "")
    return limpo.encode('latin-1', 'replace').decode('latin-1')

# -----------------------------------------------------------------------------
# 2. GERADOR DE PDF TOUR360VR (TEXTOS CENTRALIZADOS, TELEFONE E ENDEREÇO)
# -----------------------------------------------------------------------------
class PDFTour360Oficial(FPDF):
    def header(self):
        # Barra de acento superior
        self.set_fill_color(30, 64, 175) # Azul
        self.rect(0, 0, 105, 4, 'F')
        self.set_fill_color(255, 61, 61) # Vermelho
        self.rect(105, 0, 105, 4, 'F')

        if self.page_no() == 1:
            return  # Capa com layout próprio

        try:
            self.image('Logo TOUR transparente.png', 12, 7, 18)
            x_pos = 34
        except:
            x_pos = 12

        self.set_xy(x_pos, 7.5)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(30, 64, 175)
        self.cell(0, 5, 'TOUR360VR', ln=True)
        self.set_xy(x_pos, 13.5)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, conv('Gestão de Perfil & Diagnóstico do Google Meu Negócio'), ln=True)
        
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.3)
        self.line(12, 21, 198, 21)
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

def gerar_pdf_oficial(dados, score):
    pdf = PDFTour360Oficial()
    pdf.set_auto_page_break(auto=True, margin=18)
    
    # -------------------------------------------------------------------------
    # PÁGINA 1: CAPA COM DADOS DA EMPRESA (ENDEREÇO E TELEFONE CENTRALIZADOS)
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    try:
        pdf.image('Logo TOUR transparente.png', 82, 22, 46)
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

    # Cartão de Apresentação da Empresa (Textos Centralizados)
    w_capa = 150
    x_capa = (210 - w_capa) / 2.0
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rounded_rect(x_capa, 120, w_capa, 76, 4, 'FD')

    pdf.set_xy(x_capa, 127)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_capa, 8, conv(f"{dados['nome']}"), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(245, 158, 11)
    nota_stars = "*****" if dados['nota'] > 0 else ""
    pdf.cell(w_capa, 6, conv(f"Nota: {dados['nota']:.1f} {nota_stars}  ({dados['avaliacoes']} avaliações no Google)"), align='C', ln=True)
    pdf.ln(2)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(w_capa, 5.5, conv(f"Endereço: {dados['endereco']}"), align='C', ln=True)
    pdf.cell(w_capa, 5.5, conv(f"Telefone: {dados['telefone']}"), align='C', ln=True)
    pdf.cell(w_capa, 5.5, conv(f"Website Cadastrado: {dados['website']}"), align='C', ln=True)
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 10.5)
    if score < 50:
        pdf.set_text_color(239, 68, 68)
        pdf.cell(w_capa, 6, conv("Status da Ficha: Crítico (Visibilidade Comprometida)"), align='C', ln=True)
    else:
        pdf.set_text_color(34, 197, 94)
        pdf.cell(w_capa, 6, conv("Status da Ficha: Otimizado e Em Expansão"), align='C', ln=True)

    # -------------------------------------------------------------------------
    # PÁGINA 2: DIAGNÓSTICO DETALHADO DA FICHA E SCORE GERAL
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    # Cartão Ficha Analisada com Endereço e Telefone Centralizados
    w_ficha = 150
    x_ficha = (210 - w_ficha) / 2.0
    
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(x_ficha, 34, w_ficha, 44, 3, 'FD')
    
    pdf.set_xy(x_ficha, 36)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(w_ficha, 4, conv('FICHA ANALISADA DO CLIENTE'), align='C', ln=True)
    
    pdf.set_x(x_ficha)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_ficha, 7, conv(f"{dados['nome']}"), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(245, 158, 11)
    nota_str = f"Nota {dados['nota']:.1f} *****" if dados['nota'] > 0 else "Sem nota registrada"
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.5, conv(f"{nota_str}  •  {dados['avaliacoes']} avaliações no Google"), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.5, conv(f"Endereço: {dados['endereco']}"), align='C', ln=True)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.5, conv(f"Telefone: {dados['telefone']}  |  Website: {dados['website']}"), align='C', ln=True)

    # Quadro do Score Geral
    pdf.set_y(84)
    if score < 50:
        cr, cg, cb = 239, 68, 68
        status_txt = "STATUS CRÍTICO"
    elif score < 80:
        cr, cg, cb = 245, 158, 11
        status_txt = "STATUS MÉDIO"
    else:
        cr, cg, cb = 34, 197, 94
        status_txt = "ALTO DESEMPENHO"

    w_score = 130
    x_score = (210 - w_score) / 2.0
    
    pdf.set_fill_color(cr, cg, cb)
    pdf.set_draw_color(cr, cg, cb)
    pdf.rounded_rect(x_score, 84, w_score, 18, 3, 'FD')
    
    pdf.set_xy(x_score, 86)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(w_score, 6, conv(f"{score} / 100"), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.cell(w_score, 5, conv(f"SCORE GERAL DE OTIMIZAÇÃO ({status_txt})"), align='C', ln=True)

    # Título da Auditoria
    pdf.set_y(108)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('AUDITORIA DETALHADA DE PONTOS DE BUSCA'), align='C', ln=True)
    pdf.ln(8)

    pct_avaliacoes = min(int((dados['avaliacoes'] / 50.0) * 100), 100) if dados['avaliacoes'] > 0 else 10

    itens = [
        ("1. Fotos e Resolução Visual", 30 if not dados['tem_fotos_hd'] else 100, "Baixo", "Poucas fotos encontradas / antigas."),
        ("2. Tour Virtual 360° Interativo", 0 if not dados['tem_tour360'] else 100, "Ausente", "Nenhum Tour 360 detectado no perfil."),
        ("3. Categorias Principal e Secundárias", 50 if not dados['categorias_completas'] else 100, "Incompleto", "Sem categorias secundárias estratégicas."),
        ("4. Horários e Exceções (Feriados)", 40 if not dados['horarios_ok'] else 100, "Desatualizado", "Falta de horários especiais em feriados."),
        ("5. Website e Links de Conversão", 10 if dados['website'] == 'Não possui' else 100, "Falho", "Sem links diretos de contato e WhatsApp."),
        ("6. Avaliações no Google (Prova Social)", pct_avaliacoes, f"{dados['nota']}/5.0", f"{dados['avaliacoes']} avaliações registradas.")
    ]

    for titulo, pct, rotulo, desc in itens:
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(120, 4, conv(titulo), ln=False)
        
        pdf.set_font('Helvetica', 'B', 9)
        if pct < 40:
            pdf.set_text_color(239, 68, 68)
        elif pct < 80:
            pdf.set_text_color(245, 158, 11)
        else:
            pdf.set_text_color(34, 197, 94)
            
        pdf.cell(66, 4, conv(f"| {pct}% - {rotulo}"), align='R', ln=True)

        pdf.set_fill_color(226, 232, 240)
        pdf.rounded_rect(12, pdf.get_y(), 186, 3.5, 1.5, 'F')
        
        if pct < 40:
            pdf.set_fill_color(239, 68, 68)
        elif pct < 80:
            pdf.set_fill_color(245, 158, 11)
        else:
            pdf.set_fill_color(34, 197, 94)
            
        largura_barra = max(float(pct) * 1.86, 4.0)
        pdf.rounded_rect(12, pdf.get_y(), largura_barra, 3.5, 1.5, 'F')
        pdf.ln(4.5)

        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 3.5, conv(f"  Diagnóstico: {desc}"), ln=True)
        pdf.ln(3)

    # -------------------------------------------------------------------------
    # PÁGINA 3: PROPOSTA COMERCIAL & PLANOS DE INVESTIMENTO
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    pdf.set_y(32)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('PROPOSTA COMERCIAL & ESTRUTURAÇÃO ESTRATÉGICA'), align='C', ln=True)
    pdf.ln(8)

    # Quadro Informativo
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
    
    # Proposta de Planos
    pdf.set_y(98)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('PROPOSTA DE PLANOS E INVESTIMENTO'), align='C', ln=True)
    pdf.ln(8)

    y_p = pdf.get_y() + 2
    
    # --- PLANO START (Centralizado) ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(12, y_p + 2, 52, 52, 2, 'FD')
    
    pdf.set_xy(12, y_p + 5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(52, 5, 'Plano Start', align='C', ln=True)
    
    pdf.set_xy(12, y_p + 12)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(62, 161, 219)
    pdf.cell(52, 6, 'R$ 500,00', align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(12, y_p + 21)
    pdf.cell(52, 4.2, conv('- Correção cadastral'), align='C', ln=True)
    pdf.set_x(12); pdf.cell(52, 4.2, conv('- Otimização de SEO'), align='C', ln=True)
    pdf.set_x(12); pdf.cell(52, 4.2, conv('- Ajuste de categorias'), align='C', ln=True)
    pdf.set_x(12); pdf.cell(52, 4.2, conv('- Inserção de links'), align='C', ln=True)

    # --- PLANO PRO (Centralizado) ---
    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(30, 64, 175)
    pdf.set_line_width(1.0)
    pdf.rounded_rect(68, y_p - 4, 70, 62, 3, 'FD')
    pdf.set_line_width(0.2)
    
    pdf.set_xy(68, y_p)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(70, 5, conv('Plano Pro'), align='C', ln=True)
    
    pdf.set_xy(68, y_p + 5)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(70, 4, conv('(Recomendado)'), align='C', ln=True)
    
    pdf.set_xy(68, y_p + 11)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(70, 7, 'R$ 1.200,00', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.set_xy(68, y_p + 22)
    pdf.cell(70, 4.8, conv('- Tudo do Plano Start'), align='C', ln=True)
    pdf.set_x(68); pdf.cell(70, 4.8, conv('- Tour Virtual 360°'), align='C', ln=True)
    pdf.set_x(68); pdf.cell(70, 4.8, conv('- Ensaio Fotográfico HD'), align='C', ln=True)
    pdf.set_x(68); pdf.cell(70, 4.8, conv('- Relatório Visual de Entrega'), align='C', ln=True)

    # --- GESTÃO MENSAL (Centralizado) ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(142, y_p + 2, 54, 52, 2, 'FD')
    
    pdf.set_xy(142, y_p + 5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(54, 5, conv('Gestão Mensal'), align='C', ln=True)
    
    pdf.set_xy(142, y_p + 12)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(62, 161, 219)
    pdf.cell(54, 6, 'R$ 600,00/mês', align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(142, y_p + 21)
    pdf.cell(54, 4.2, conv('- Postagens semanais'), align='C', ln=True)
    pdf.set_x(142); pdf.cell(54, 4.2, conv('- Gestão de avaliações'), align='C', ln=True)
    pdf.set_x(142); pdf.cell(54, 4.2, conv('- Atualização de fotos'), align='C', ln=True)
    pdf.set_x(142); pdf.cell(54, 4.2, conv('- Relatório mensal'), align='C', ln=True)

    # -------------------------------------------------------------------------
    # PÁGINA 4: CONTRATO DE PRESTAÇÃO DE SERVIÇOS
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
    pdf.write(5.5, conv(f"{dados['nome']}, Endereço: {dados['endereco']}.\n\n"))
    
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
    pdf.write(5.5, conv("(   ) Plano Start          (   ) Plano Pro          (   ) Gestão Mensal\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA QUARTA - CONDIÇÕES DE PAGAMENTO:\n"))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("(   ) A Vista     (   ) 2x Plano Start     (   ) 3x Plano Pro     (   ) Gestão Mensal - Vencimento Todo Dia: _____\n\n\n"))

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
# 3. INTERFACE STREAMLIT COM MENU LATERAL
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

# -----------------------------------------------------------------------------
# ETAPA 1: CONSULTA E DIAGNÓSTICO
# -----------------------------------------------------------------------------
if "🔍" in opcao_menu:
    st.subheader("🔍 Consultar Ficha do Google Meu Negócio")
    
    col_e1, col_e2 = st.columns([2, 1])
    with col_e1:
        nome_empresa = st.text_input("🏢 Nome da Empresa / Estabelecimento:", placeholder="Ex: Personalitté estética")
    with col_e2:
        cidade_empresa = st.text_input("📍 Cidade / Estado:", placeholder="Ex: Ribeirão Preto, SP")

    if st.button("🚀 Analisar Perfil e Gerar Diagnóstico", use_container_width=True):
        if nome_empresa:
            termo_busca = f"{nome_empresa}, {cidade_empresa}" if cidade_empresa else nome_empresa
            dados = None
            
            if API_KEY_GOOGLE:
                try:
                    url_find = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={termo_busca}&inputtype=textquery&fields=place_id&key={API_KEY_GOOGLE}"
                    res_find = requests.get(url_find).json()
                    
                    if res_find.get("candidates"):
                        place_id = res_find["candidates"][0]["place_id"]
                        url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos&key={API_KEY_GOOGLE}"
                        res_details = requests.get(url_details).json()
                        
                        if "result" in res_details:
                            place = res_details["result"]
                            photos = place.get("photos", [])
                            
                            dados = {
                                "nome": place.get("name", nome_empresa),
                                "endereco": place.get("formatted_address", cidade_empresa if cidade_empresa else "Endereço cadastrado"),
                                "telefone": place.get("formatted_phone_number", "Não informado"),
                                "website": place.get("website", "Não possui"),
                                "nota": place.get("rating", 0.0),
                                "avaliacoes": place.get("user_ratings_total", 0),
                                "tem_tour360": False,
                                "tem_fotos_hd": len(photos) > 10,
                                "categorias_completas": False,
                                "horarios_ok": True
                            }
                except Exception as e:
                    st.error(f"Erro na conexão com o Google: {e}")

            if not dados:
                dados = {
                    "nome": nome_empresa,
                    "endereco": f"{cidade_empresa}" if cidade_empresa else "Ribeirão Preto, SP",
                    "telefone": "Não informado",
                    "website": "Não possui",
                    "nota": 4.2,
                    "avaliacoes": 38,
                    "tem_tour360": False,
                    "tem_fotos_hd": False,
                    "categorias_completas": False,
                    "horarios_ok": False
                }

            score = 100
            if not dados["tem_tour360"]: score -= 25
            if dados["website"] == "Não possui": score -= 20
            if not dados["tem_fotos_hd"]: score -= 20
            if not dados["categorias_completas"]: score -= 15
            if not dados["horarios_ok"]: score -= 10
            if dados["avaliacoes"] < 50: score -= 10

            st.session_state['dados'] = dados
            st.session_state['score'] = score

            st.success("Análise do perfil realizada com sucesso!")

    if 'dados' in st.session_state:
        dados = st.session_state['dados']
        score = st.session_state['score']

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
                    <p style="margin: 4px 0;">📍 <strong>Endereço / Cidade:</strong> {dados['endereco']}</p>
                    <p style="margin: 4px 0;">📞 <strong>Telefone:</strong> {dados['telefone']}</p>
                    <p style="margin: 4px 0;">🌐 <strong>Website:</strong> {dados['website']}</p>
                    <p style="margin: 4px 0;">⭐ <strong>Avaliações:</strong> {dados['nota']} ({dados['avaliacoes']} avaliações)</p>
                </div>
            """, unsafe_allow_html=True)

        pdf_bytes = gerar_pdf_oficial(dados, score)

        st.markdown("---")
        st.download_button(
            label="📥 Baixar Documento Oficial de Diagnóstico, Proposta e Contrato em PDF",
            data=pdf_bytes,
            file_name=f"Diagnostico_Tour360VR_{dados['nome'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# -----------------------------------------------------------------------------
# ETAPAS SECUNDÁRIAS DE INFORMAÇÕES
# -----------------------------------------------------------------------------
elif "💡" in opcao_menu:
    st.subheader("💡 Diagnóstico Detalhado & Plano de Ação")
    st.markdown("""
        * **SEO Local & Atualização Cadastral:** Ajuste de títulos, palavras-chave e categorias principais/secundárias.
        * **Tour Virtual 360° Interativo:** Publicação de tour imersivo diretamente integrado ao Google Maps.
        * **Fotos de Alta Resolução:** Produção fotográfica profissional em HD para transmitir credibilidade.
        * **Links de Conversão Rápida:** Botões para WhatsApp, cardápio digital e reserva de serviços.
    """)

elif "💲" in opcao_menu:
    st.subheader("💲 Proposta de Investimento e Planos")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**PLANO START**\n\n**R$ 500,00**\n- Correção cadastral\n- Otimização de SEO\n- Ajuste de categorias\n- Links de conversão")
    with col2:
        st.markdown("**PLANO PRO (Recomendado)**\n\n**R$ 1.200,00**\n- Tudo do Plano Start\n- Tour Virtual 360°\n- Ensaio Fotográfico\n- Relatório de Entrega")
    with col3:
        st.markdown("**GESTÃO MENSAL**\n\n**R$ 600,00/mês**\n- Postagens semanais\n- Gestão de avaliações\n- Atualização de fotos\n- Relatórios mensais")

elif "📄" in opcao_menu:
    st.subheader("📄 Contrato de Prestação de Serviços")
    st.info("O contrato é gerado automaticamente na 4ª página do arquivo PDF completo após a realização da consulta na Etapa 1.")

# -----------------------------------------------------------------------------
# 4. RODAPÉ FIXO DO APP
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="footer">
        Tour360VR • tour360vr.com.br • contato@tour360vr.com.br • WhatsApp: (16) 99133-2121
    </div>
""", unsafe_allow_html=True)

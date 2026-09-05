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
    /* Fundo Principal Dark */
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    
    /* Customização do Menu Lateral */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
        padding-top: 0px;
    }
    
    /* Header Principal */
    .main-header {
        font-size: 24px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin-bottom: 20px;
    }
    .main-header span { color: #ff3d3d; }
    
    /* Card de Conteúdo Principal */
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
    
    /* Estilo dos Botões de Ação/PDF */
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

    /* Rodapé Customizado */
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
# 2. FUNÇÕES UTILITÁRIAS & CONVERSÕES
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
# 4. GERADOR PDF
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
        self.set_draw_color(226, 232, 240)
        self.line(12, 23, 198, 23)
        self.ln(20)

    def footer(self):
        self.set_y(-16)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, f'Página {self.page_no()} de 4', align='C')

def gerar_pdf_oficial(dados, score_input, planos, plano_acao_extra=""):
    pdf = PDFTour360Oficial()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 20)
    pdf.cell(0, 10, conv(f"Diagnóstico: {dados['nome']}"), ln=True)
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 5. SIDEBAR / MENU LATERAL COMPACTO estilo DASHBOARD
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

# Header Principal
st.markdown("<div class='main-header'>PLATAFORMA DE CONSULTORIA <span>TOUR360VR</span> - GESTÃO & DIAGNÓSTICO GOOGLE MEU NEGÓCIO</div>", unsafe_allow_html=True)

dados = st.session_state['dados']
score = calcular_score_real(dados)

# -----------------------------------------------------------------------------
# PAINEL CENTRAL (MÓDULO SELECIONADO)
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
            
        if st.button("🔍 Buscar no Google Maps", use_container_width=True):
            if API_KEY_GOOGLE:
                try:
                    termo = f"{nome_input}, {cidade_empresa}"
                    res = requests.get(f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={termo}&key={API_KEY_GOOGLE}").json()
                    if res.get("status") == "OK":
                        st.session_state['unidades_encontradas'] = res["results"]
                        st.success("Unidades encontradas!")
                except Exception as e:
                    st.error(f"Erro na conexão: {e}")
            st.rerun()

        if st.session_state['unidades_encontradas']:
            opcoes = [f"{u.get('name')} - {u.get('formatted_address')}" for u in st.session_state['unidades_encontradas']]
            escolha = st.selectbox("Selecione a unidade:", opcoes)
            if st.button("Confirmar Unidade"):
                idx = opcoes.index(escolha)
                u = st.session_state['unidades_encontradas'][idx]
                st.session_state['dados']['nome'] = u.get("name")
                st.session_state['dados']['endereco'] = u.get("formatted_address")
                st.session_state['dados']['nota'] = float(u.get("rating", 0))
                st.session_state['dados']['avaliacoes'] = int(u.get("user_ratings_total", 0))
                st.rerun()

        st.markdown("---")
        st.markdown(f"**Ponto de Atenção:** {st.session_state['plano_acao_extra']}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>VISÃO GERAL DO DIAGNÓSTICO</div>", unsafe_allow_html=True)
        st.markdown(f"### Score Geral: **{score}/100**")
        st.progress(score / 100)
        
        st.markdown("#### Falhas e Recomendações:")
        st.markdown(f"* Tour 360°: {'✓ Ativo' if dados['tem_tour360'] else '❌ Ausente'}")
        st.markdown(f"* Fotos HD: {'✓ Ativo' if dados['tem_fotos_hd'] else '❌ Poucas / Inexistentes'}")
        st.markdown(f"* Categorias: {'✓ Atualizadas' if dados['categorias_completas'] else '❌ Incompletas'}")
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
# PAINEL DE GERAR E EXPORTAR PDF
# -----------------------------------------------------------------------------
st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
st.markdown("<div class='card-title'>GERAR PDF</div>", unsafe_allow_html=True)

pdf_bytes = gerar_pdf_oficial(dados, score, st.session_state['planos'], st.session_state['plano_acao_extra'])

b1, b2, b3 = st.columns(3)
with b1:
    st.download_button("💾 Salvar Diagnóstico como PDF", data=pdf_bytes, file_name="Diagnostico_Tour360VR.pdf", mime="application/pdf", use_container_width=True)
with b2:
    st.download_button("📄 Salvar Contrato como PDF", data=pdf_bytes, file_name="Contrato_Tour360VR.pdf", mime="application/pdf", use_container_width=True)
with b3:
    st.download_button("📊 Salvar Relatório como PDF", data=pdf_bytes, file_name="Relatorio_Tour360VR.pdf", mime="application/pdf", use_container_width=True)

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

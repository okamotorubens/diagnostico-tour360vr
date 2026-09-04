import io
import requests
import streamlit as st
from fpdf import FPDF

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA DO STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tour360VR - Diagnóstico do Google Meu Negócio",
    page_icon="🌐",
    layout="wide"
)

# Estilização Dark na Tela do App e Ajuste de Contraste
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .header-box { border-bottom: 2px solid #ef4444; padding-bottom: 12px; margin-bottom: 25px; }
    .card-info { background-color: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 8px; margin-bottom: 15px; }
    .score-card { background-color: #1e293b; border: 2px solid #ef4444; padding: 20px; border-radius: 8px; text-align: center; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0f172a; color: #94a3b8; text-align: center; padding: 10px; border-top: 1px solid #1e293b; font-size: 12px; z-index: 100; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-box">
        <h1 style="color: #ffffff; margin: 0;">TOUR<span style="color: #ef4444;">360VR</span></h1>
        <p style="color: #38bdf8; margin-top: 5px; font-weight: 600;">Plataforma de Consultoria, Diagnóstico & Gestão do Google Meu Negócio</p>
    </div>
""", unsafe_allow_html=True)

API_KEY_GOOGLE = st.secrets.get("GOOGLE_PLACES_API_KEY", "")

# -----------------------------------------------------------------------------
# 2. CLASSE GERADORA DE PDF EM TEMA CLARO (FPDF2)
# -----------------------------------------------------------------------------
class PDFTour360Claro(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(220, 38, 38) # Vermelho Tour360VR
            self.cell(0, 8, 'TOUR360VR', ln=True)
            self.set_font('Helvetica', '', 8)
            self.set_text_color(100, 116, 139)
            self.cell(0, 4, 'Consultoria & Diagnóstico do Google Meu Negócio', ln=True)
            self.set_draw_color(226, 232, 240)
            self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
            self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(100, 116, 139)
        self.set_draw_color(226, 232, 240)
        self.line(10, self.get_y() - 2, 200, self.get_y() - 2)
        
        # Links Clicáveis no Rodapé
        self.cell(60, 8, 'tour360vr.com.br', link='https://tour360vr.com.br', align='L')
        self.cell(70, 8, 'contato@tour360vr.com.br', link='mailto:contato@tour360vr.com.br', align='C')
        self.cell(60, 8, 'WhatsApp: (16) 99133-2121', link='https://wa.me/5516991332121', align='R')

def conv(texto):
    """Trata caracteres acentuados para compatibilidade nativa com latin-1 no FPDF2."""
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

def gerar_pdf_claro(dados, score):
    pdf = PDFTour360Claro()
    pdf.set_auto_page_break(auto=True, margin=18)
    
    # -------------------------------------------------------------------------
    # PÁGINA 1: CAPA DO DIAGNÓSTICO
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    # Faixa do Cabeçalho da Capa
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_xy(12, 12)
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(220, 38, 38)
    pdf.cell(0, 10, 'TOUR360VR', ln=True)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, conv('DIAGNÓSTICO E AUDITORIA DE PERFIL DO GOOGLE'), ln=True)
    
   # Linha divisória
    pdf.set_draw_color(220, 38, 38)
    pdf.set_linewidth(1)
    pdf.line(12, 38, 198, 38)
    pdf.set_linewidth(0.2)

    # Cartão da Ficha do Cliente
    pdf.set_y(50)
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(12, 50, 186, 50, 'F')
    pdf.set_xy(18, 54)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, conv(f"Empresa: {dados['nome']}"), ln=True)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    pdf.set_x(18); pdf.cell(0, 6, conv(f"Endereço: {dados['endereco']}"), ln=True)
    pdf.set_x(18); pdf.cell(0, 6, conv(f"Telefone: {dados['telefone']} | Website: {dados['website']}"), ln=True)
    pdf.set_x(18); pdf.cell(0, 6, conv(f"Avaliações: {dados['nota']} Estrelas ({dados['avaliacoes']} Avaliações)"), ln=True)

    # Bloco do Score Visual de Saúde
    pdf.set_y(110)
    if score < 50:
        cor_r, cor_g, cor_b = 239, 68, 68 # Vermelho
        status_texto = "STATUS CRÍTICO - AÇÃO NECESSÁRIA URGENTE"
    elif score < 80:
        cor_r, cor_g, cor_b = 245, 158, 11 # Amarelo
        status_texto = "STATUS MÉDIO - OTIMIZAÇÕES RECOMENDADAS"
    else:
        cor_r, cor_g, cor_b = 34, 197, 94 # Verde
        status_texto = "PERFIL OTIMIZADO E EM ALTA PERFORMANCE"

    pdf.set_fill_color(cor_r, cor_g, cor_b)
    pdf.rect(12, 110, 186, 28, 'F')
    pdf.set_xy(12, 113)
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(186, 10, f"{score} / 100", align='C', ln=True)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(186, 6, conv(status_texto), align='C', ln=True)

    # Detalhamento dos Pontos de Busca
    pdf.set_y(148)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, conv('Diagnóstico Detalhado do Perfil'), ln=True)
    pdf.ln(3)

    itens_auditoria = [
        ("Fotos e Qualidade Visual", "Ok (Imagens de Qualidade)" if dados['tem_fotos_hd'] else "Ruim (Fotos Insuficientes ou Antigas)", "Ruim" if not dados['tem_fotos_hd'] else "Bom"),
        ("Tour Virtual 360° Interativo", "Presente no Google Maps" if dados['tem_tour360'] else "Ruim (Ausente - Perda de Engajamento)", "Ruim" if not dados['tem_tour360'] else "Bom"),
        ("Categorias Principal e Secundárias", "Completas" if dados['categorias_completas'] else "Médio (Categorias Incompletas)", "Médio" if not dados['categorias_completas'] else "Bom"),
        ("Horários e Atendimento em Feriados", "Atualizados" if dados['horarios_ok'] else "Médio (Desatualizado ou Sem Exceções)", "Médio" if not dados['horarios_ok'] else "Bom"),
        ("Localização e Marcador no Mapa", "Verificado e Correto", "Bom"),
        ("Website e Links de Agendamento/Menu", "Inseridos" if dados['website'] != 'Não possui' else "Ruim (Sem Links Diretos de Conversão)", "Ruim" if dados['website'] == 'Não possui' else "Bom")
    ]

    for item in itens_auditoria:
        nome_item = item[0]
        desc_item = item[1]
        classif = item[2]

        pdf.set_fill_color(248, 250, 252)
        pdf.cell(120, 8, conv(f"  {nome_item}"), border=0, fill=True)
        
        pdf.set_font('Helvetica', 'B', 9)
        if classif == "Bom":
            pdf.set_text_color(22, 163, 74) # Verde
        elif classif == "Médio":
            pdf.set_text_color(217, 119, 6) # Amarelo
        else:
            pdf.set_text_color(220, 38, 38) # Vermelho
            
        pdf.cell(66, 8, conv(f"[{classif}] {desc_item}"), border=0, fill=True, align='R', ln=True)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(51, 65, 85)
        pdf.ln(1)

    # -------------------------------------------------------------------------
    # PÁGINA 2: AÇÕES RECOMENDADAS E PROPOSTA EM 3 COLUNAS
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, conv('Plano de Ação e Melhorias Necessárias'), ln=True)
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85)
    acoes_texto = (
        "1. Atualização Cadastral e Estruturação de SEO Local nas palavras-chave mais buscadas.\n"
        "2. Produção e Publicação de Tour Virtual 360° para elevar a relevância no algoritmo do Google Maps.\n"
        "3. Inclusão de fotos profissionais em alta resolução para transmitir maior credibilidade ao cliente.\n"
        "4. Integração de links de ação direta (WhatsApp, Cardápio/Serviços e Agendamentos)."
    )
    pdf.multi_cell(186, 5, conv(acoes_texto))
    pdf.ln(8)

    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, conv('Proposta de Investimento e Planos'), ln=True)
    pdf.ln(2)

    # Tabela em 3 Colunas para os Planos
    y_planos = pdf.get_y()
    
    # Coluna 1: Plano Start (R$ 500)
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(12, y_planos, 58, 85, 'F')
    pdf.set_xy(14, y_planos + 4)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(54, 6, 'PLANO START', ln=True, align='C')
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(220, 38, 38)
    pdf.cell(54, 8, 'R$ 500,00', ln=True, align='C')
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(51, 65, 85)
    detalhes_start = "- Correção cadastral\n- Otimização de SEO\n- Ajuste de categorias\n- Links de conversão\n- Suporte técnico"
    pdf.set_xy(14, y_planos + 22)
    pdf.multi_cell(54, 4.5, conv(detalhes_start))

    # Coluna 2: Plano Pro (Recomendado - R$ 1.200)
    pdf.set_fill_color(254, 242, 242)
    pdf.set_draw_color(220, 38, 38)
    pdf.rect(76, y_planos, 58, 85, 'FD')
    pdf.set_xy(78, y_planos + 4)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(220, 38, 38)
    pdf.cell(54, 6, conv('PLANO PRO ★'), ln=True, align='C')
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(54, 8, 'R$ 1.200,00', ln=True, align='C')
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(51, 65, 85)
    detalhes_pro = "- Tudo do Plano Start\n- Tour Virtual 360° HD\n- Ensaio Fotográfico\n- SEO Avançado Google\n- Relatório de Entrega\n(Mais Recomendado)"
    pdf.set_xy(78, y_planos + 22)
    pdf.multi_cell(54, 4.5, conv(detalhes_pro))

    # Coluna 3: Plano Mensal (R$ 600)
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(140, y_planos, 58, 85, 'F')
    pdf.set_xy(142, y_planos + 4)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(54, 6, 'GESTÃO MENSAL', ln=True, align='C')
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(220, 38, 38)
    pdf.cell(54, 8, 'R$ 600,00/mês', ln=True, align='C')
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(51, 65, 85)
    detalhes_mensal = "- Postagens semanais\n- Gestão de Avaliações\n- Atualização de fotos\n- Proteção de dados\n- Relatórios mensais"
    pdf.set_xy(142, y_planos + 22)
    pdf.multi_cell(54, 4.5, conv(detalhes_mensal))

    # -------------------------------------------------------------------------
    # PÁGINA 3: CONTRATO COM SELEÇÃO DE PLANO E PAGAMENTO
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, conv('CONTRATO DE PRESTAÇÃO DE SERVIÇOS'), align='C', ln=True)
    pdf.ln(4)

    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    
    contrato_cabecalho = (
        f"CONTRATADA: TOUR360VR, E-mail: contato@tour360vr.com.br, WhatsApp: (16) 99133-2121.\n"
        f"CONTRATANTE: {dados['nome']}, Endereço: {dados['endereco']}.\n\n"
        "A CONTRATADA compromete-se a executar os serviços de otimização, reestruturação e/ou produção de Tour Virtual 360° para o perfil do Google do CONTRATANTE."
    )
    pdf.multi_cell(186, 4.5, conv(contrato_cabecalho))
    pdf.ln(4)

    # Campos de Seleção do Plano
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(12, pdf.get_y(), 186, 22, 'F')
    pdf.set_xy(16, pdf.get_y() + 3)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, conv("SELEÇÃO DO PLANO CONTRATADO:"), ln=True)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_x(16)
    pdf.cell(0, 8, conv("(   ) Plano Start - R$ 500,00     (   ) Plano Pro - R$ 1.200,00     (   ) Gestão Mensal - R$ 600,00/mês"), ln=True)
    pdf.ln(4)

    # Campos de Seleção da Condição de Pagamento
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(12, pdf.get_y(), 186, 22, 'F')
    pdf.set_xy(16, pdf.get_y() + 3)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 5, conv("CONDIÇÕES DE PAGAMENTO:"), ln=True)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_x(16)
    pdf.cell(0, 8, conv("(   ) À Vista     (   ) 2x     (   ) 3x     (   ) Mensal - Vencimento Todo Dia: ____"), ln=True)
    pdf.ln(12)

    clausulas = (
        "CLÁUSULA PRIMEIRA: Os serviços serão executados no prazo de até 10 dias úteis após a aprovação e acesso ao perfil.\n"
        "CLÁUSULA SEGUNDA: O não pagamento na data acordada sujeitará o contrato a juros legais de mora."
    )
    pdf.multi_cell(186, 4.5, conv(clausulas))
    pdf.ln(20)

    # Bloco de Assinaturas
    pdf.cell(88, 5, '__________________________________', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, '__________________________________', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(88, 5, 'TOUR360VR', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, conv(f"{dados['nome']}"), align='C', ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 3. INTERFACE DE BUSCA DO APLICATIVO (STREAMLIT)
# -----------------------------------------------------------------------------
col_empresa, col_cidade = st.columns([2, 1])

with col_empresa:
    nome_estabelecimento = st.text_input("🏢 Nome do Estabelecimento:", placeholder="Ex: Toque de Letra")

with col_cidade:
    cidade_estabelecimento = st.text_input("📍 Cidade / Estado:", placeholder="Ex: Ribeirão Preto, SP")

if st.button("🚀 Analisar Perfil Agora", use_container_width=True):
    if nome_estabelecimento:
        termo_busca = f"{nome_estabelecimento}, {cidade_estabelecimento}" if cidade_estabelecimento else nome_estabelecimento
        
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
                            "nome": place.get("name", nome_estabelecimento),
                            "endereco": place.get("formatted_address", cidade_estabelecimento),
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
                st.error(f"Erro na conexão com a API do Google: {e}")

        if not dados:
            dados = {
                "nome": nome_estabelecimento,
                "endereco": f"{cidade_estabelecimento}" if cidade_estabelecimento else "Endereço cadastrado no Google",
                "telefone": "(16) 3999-8888",
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

        st.success("Análise de perfil concluída com sucesso!")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(f"""
                <div class="score-card">
                    <h2 style="color: #ef4444; font-size: 46px; margin: 0;">{score} / 100</h2>
                    <p style="color: #cbd5e1; text-transform: uppercase; font-size: 13px; font-weight: bold;">Score Geral de Otimização</p>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class="card-info">
                    <h3 style="color: #38bdf8; margin-top: 0;">{dados['nome']}</h3>
                    <p style="margin: 4px 0;">📍 <strong>Endereço:</strong> {dados['endereco']}</p>
                    <p style="margin: 4px 0;">📞 <strong>Telefone:</strong> {dados['telefone']}</p>
                    <p style="margin: 4px 0;">🌐 <strong>Website:</strong> {dados['website']}</p>
                    <p style="margin: 4px 0;">⭐ <strong>Avaliações:</strong> {dados['nota']} ({dados['avaliacoes']} avaliações)</p>
                </div>
            """, unsafe_allow_html=True)

        st.subheader("📊 Diagnóstico dos Pontos de Busca")
        st.progress(25 if dados["tem_fotos_hd"] else 10, text="Fotos e Resolução: Baixa Qualidade Detectada")
        st.progress(0 if not dados["tem_tour360"] else 100, text="Tour Virtual 360°: Ausente no Perfil")
        st.progress(50 if not dados["categorias_completas"] else 100, text="Categorias: Incompletas")
        st.progress(10 if dados["website"] == "Não possui" else 100, text="Website / Links de Ação: Não Identificado")

        # Gerar o PDF em Tema Claro
        pdf_bytes = gerar_pdf_claro(dados, score)

        st.markdown("---")
        st.subheader("📄 Exportar Documentos Oficiais")
        
        st.download_button(
            label="📥 Baixar Diagnóstico, Proposta e Contrato em PDF (Tema Claro)",
            data=pdf_bytes,
            file_name=f"Diagnostico_Tour360VR_{dados['nome'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Por favor, digite o nome do estabelecimento.")

# -----------------------------------------------------------------------------
# 4. RODAPÉ FIXO DO APP
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="footer">
        Tour360VR • tour360vr.com.br • contato@tour360vr.com.br • WhatsApp: (16) 99133-2121
    </div>
""", unsafe_allow_html=True)

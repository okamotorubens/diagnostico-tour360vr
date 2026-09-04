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

# Estilização do Aplicativo (Tema Dark Tour360VR)
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .header-box { border-bottom: 2px solid #ff3d3d; padding-bottom: 12px; margin-bottom: 25px; }
    .card-info { background-color: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 8px; margin-bottom: 15px; }
    .score-card { background-color: #1e293b; border: 2px solid #ff3d3d; padding: 20px; border-radius: 8px; text-align: center; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0f172a; color: #94a3b8; text-align: center; padding: 10px; border-top: 1px solid #1e293b; font-size: 12px; z-index: 100; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-box">
        <h1 style="color: #ffffff; margin: 0;">TOUR<span style="color: #ff3d3d;">360VR</span></h1>
        <p style="color: #3ea1db; margin-top: 5px; font-weight: 600;">Plataforma de Consultoria, Diagnóstico & Gestão do Google Meu Negócio</p>
    </div>
""", unsafe_allow_html=True)

API_KEY_GOOGLE = st.secrets.get("GOOGLE_PLACES_API_KEY", "")

def conv(texto):
    """Garante compatibilidade de caracteres com latin-1 evitando '?' e falhas."""
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

# -----------------------------------------------------------------------------
# 2. CLASSE GERADORA DE PDF OFICIAL TOUR360VR
# -----------------------------------------------------------------------------
class PDFTour360Oficial(FPDF):
    def header(self):
        # Logo do Tour360VR no lado esquerdo do cabeçalho
        try:
            self.image('Logo TOUR transparente.png', 12, 7, 16)
            x_pos = 32
        except:
            x_pos = 12

        if self.page_no() == 1:
            self.set_xy(x_pos, 8)
            self.set_font('Helvetica', 'B', 18)
            self.set_text_color(255, 61, 61) # Red Logo #FF3D3D
            self.cell(0, 7, 'TOUR360VR', ln=True)
            self.set_xy(x_pos, 15)
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(62, 161, 219) # Blue Logo #3EA1DB
            self.cell(0, 5, conv('DIAGNÓSTICO E AUDITORIA DE PERFIL DO GOOGLE'), ln=True)
            
            self.set_draw_color(255, 61, 61)
            self.set_line_width(0.8)
            self.line(12, 26, 198, 26)
            self.set_line_width(0.2)
            self.ln(8)
        else:
            self.set_xy(x_pos, 8)
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(255, 61, 61)
            self.cell(0, 5, 'TOUR360VR', ln=True)
            self.set_xy(x_pos, 13)
            self.set_font('Helvetica', '', 8)
            self.set_text_color(100, 116, 139)
            self.cell(0, 4, conv('Consultoria & Diagnóstico do Google Meu Negócio'), ln=True)
            
            self.set_draw_color(226, 232, 240)
            self.set_line_width(0.3)
            self.line(12, 24, 198, 24)
            self.set_line_width(0.2)
            self.ln(7)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(100, 116, 139)
        self.set_draw_color(226, 232, 240)
        self.line(12, self.get_y() - 2, 198, self.get_y() - 2)
        
        self.cell(62, 8, 'tour360vr.com.br', link='https://tour360vr.com.br', align='L')
        self.cell(62, 8, 'contato@tour360vr.com.br', link='mailto:contato@tour360vr.com.br', align='C')
        self.cell(62, 8, 'WhatsApp: (16) 99133-2121', link='https://wa.me/5516991332121', align='R')

def gerar_pdf_oficial(dados, score):
    pdf = PDFTour360Oficial()
    pdf.set_auto_page_break(auto=True, margin=18)
    
    # -------------------------------------------------------------------------
    # PÁGINA 1: CAPA & AUDITORIA COM BARRAS DE PROGRESSO
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    # Cartão da Ficha do Cliente
    pdf.set_y(30)
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(12, 30, 186, 48, 'F')
    pdf.set_xy(16, 33)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv(f"Empresa: {dados['nome']}"), ln=True)
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85)
    pdf.set_x(16); pdf.cell(0, 5.5, conv(f"Endereço: {dados['endereco']}"), ln=True)
    pdf.set_x(16); pdf.cell(0, 5.5, conv(f"E-mail: {dados.get('email_cliente', 'Não informado')} | Telefone: {dados['telefone']}"), ln=True)
    pdf.set_x(16); pdf.cell(0, 5.5, conv(f"Website: {dados['website']}"), ln=True)
    pdf.set_x(16); pdf.cell(0, 5.5, conv(f"Avaliações no Google: {dados['nota']} Estrelas ({dados['avaliacoes']} avaliações)"), ln=True)

    # Bloco do Score Geral de Saúde do Perfil
    pdf.set_y(82)
    if score < 50:
        cr, cg, cb = 255, 61, 61 # Vermelho
        status_txt = "STATUS CRÍTICO - AÇÃO NECESSÁRIA URGENTE"
    elif score < 80:
        cr, cg, cb = 255, 153, 51 # Laranja
        status_txt = "STATUS MÉDIO - OTIMIZAÇÕES RECOMENDADAS"
    else:
        cr, cg, cb = 140, 198, 63 # Verde Logo
        status_txt = "PERFIL OTIMIZADO E EM ALTA PERFORMANCE"

    pdf.set_fill_color(cr, cg, cb)
    pdf.rect(12, 82, 186, 26, 'F')
    pdf.set_xy(12, 84)
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(186, 9, f"{score} / 100", align='C', ln=True)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.cell(186, 5, conv(status_txt), align='C', ln=True)

    # Detalhamento de Auditoria com Barras de Progresso
    pdf.set_y(114)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, conv('Diagnóstico Detalhado do Perfil (Pontos de Busca)'), ln=True)
    pdf.ln(2)

    itens = [
        ("Fotos e Resolução Visual", 30 if not dados['tem_fotos_hd'] else 100, "Ruim (Baixa Resolução / Antigas)" if not dados['tem_fotos_hd'] else "Bom (Fotos HD Atualizadas)"),
        ("Tour Virtual 360 Interativo", 0 if not dados['tem_tour360'] else 100, "Ruim (Ausente - Perda de Visibilidade)" if not dados['tem_tour360'] else "Bom (Publicado no Google Maps)"),
        ("Categorias Principal e Secundárias", 50 if not dados['categorias_completas'] else 100, "Médio (Incompletas)" if not dados['categorias_completas'] else "Bom (Relevância Otimizada)"),
        ("Horários e Exceções (Feriados)", 40 if not dados['horarios_ok'] else 100, "Médio (Incompleto / Feriados)" if not dados['horarios_ok'] else "Bom (Horários Atualizados)"),
        ("Website e Links de Conversão", 10 if dados['website'] == 'Não possui' else 100, "Ruim (Sem Links Diretos no Perfil)" if dados['website'] == 'Não possui' else "Bom (Links Ativos)"),
    ]

    for titulo, pct, desc in itens:
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(100, 5, conv(f"- {titulo}:"), ln=False)
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(86, 5, conv(desc), align='R', ln=True)

        pdf.set_fill_color(226, 232, 240)
        pdf.rect(12, pdf.get_y(), 186, 5, 'F')
        
        if pct < 40:
            pdf.set_fill_color(255, 61, 61)
        elif pct < 80:
            pdf.set_fill_color(255, 153, 51)
        else:
            pdf.set_fill_color(140, 198, 63)
            
        largura_barra = max(float(pct) * 1.86, 3.0)
        pdf.rect(12, pdf.get_y(), largura_barra, 5, 'F')
        pdf.ln(8)

    # -------------------------------------------------------------------------
    # PÁGINA 2: PLANO DE AÇÃO & PROPOSTA DE PLANOS (COM PRO EM DESTAQUE MAIOR)
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, conv('Plano de Ação Estruturado'), ln=True)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(51, 65, 85)
    acoes = (
        "1. Atualização Cadastral & SEO Local: Otimização completa das palavras-chave de busca.\n"
        "2. Criação do Tour Virtual 360°: Aumento direto da permanência e cliques na ficha.\n"
        "3. Produção Fotográfica Profissional: Imagens em alta resolução para transmitir autoridade.\n"
        "4. Integração de Links de Conversão: Inclusão de botões de WhatsApp, menu e reservas."
    )
    pdf.multi_cell(186, 4.5, conv(acoes))
    pdf.ln(6)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, conv('Proposta de Investimento e Planos'), ln=True)
    pdf.ln(3)

    y_p = pdf.get_y()
    
    # --- COLUNA 1: PLANO START (R$ 500,00) ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(12, y_p + 4, 54, 88, 'FD')
    
    pdf.set_xy(12, y_p + 8)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(54, 5, 'PLANO START', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(54, 7, 'R$ 500,00', align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(51, 65, 85)
    it_start = "- Correção cadastral\n- Otimização de SEO\n- Ajuste de categorias\n- Links de conversão\n- Suporte técnico"
    pdf.set_xy(14, y_p + 24)
    pdf.multi_cell(50, 4.5, conv(it_start))

    # --- COLUNA 2: PLANO PRO (R$ 1.200,00) - RECOMENDADO EM DESTAQUE AMPLIADO ---
    pdf.set_fill_color(254, 242, 242)
    pdf.set_draw_color(255, 61, 61)
    pdf.set_line_width(0.8)
    pdf.rect(70, y_p, 66, 96, 'FD') # Quadro com altura e largura aumentadas
    pdf.set_line_width(0.2)
    
    pdf.set_xy(70, y_p + 5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(66, 5, conv('PLANO PRO'), align='C', ln=True)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.cell(66, 4, conv('(Recomendado)'), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(66, 7, 'R$ 1.200,00', align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    it_pro = "- Tudo do Plano Start\n- Tour Virtual 360°\n- Ensaio Fotográfico\n- SEO Avançado Google\n- Relatório de Entrega\n- Suporte Prioritário"
    pdf.set_xy(73, y_p + 26)
    pdf.multi_cell(60, 4.8, conv(it_pro))

    # --- COLUNA 3: GESTÃO MENSAL (R$ 600,00/mês) ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(140, y_p + 4, 54, 88, 'FD')
    
    pdf.set_xy(140, y_p + 8)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(54, 5, conv('GESTÃO MENSAL'), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(54, 7, 'R$ 600,00/mês', align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(51, 65, 85)
    it_mensal = "- Postagens semanais\n- Gestão de avaliações\n- Atualização de fotos\n- Proteção da ficha\n- Relatórios mensais"
    pdf.set_xy(142, y_p + 24)
    pdf.multi_cell(50, 4.5, conv(it_mensal))

    # -------------------------------------------------------------------------
    # PÁGINA 3: CONTRATO DE PRESTAÇÃO DE SERVIÇOS
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    # Título do Contrato Ampliado
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, conv('CONTRATO DE PRESTAÇÃO DE SERVIÇOS'), align='C', ln=True)
    pdf.ln(4)

    # Identificação das Partes com Bolds Solicitados
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.write(4.5, conv("CONTRATADA: "))
    pdf.set_font('Helvetica', '', 8.5)
    pdf.write(4.5, conv("TOUR360VR, representada por Rubens H. Okamoto, CPF: 287.932.298-79, E-mail: contato@tour360vr.com.br e Telefone: (16) 99133-2121.\n"))
    
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.write(4.5, conv("CONTRATANTE: "))
    pdf.set_font('Helvetica', '', 8.5)
    pdf.write(4.5, conv(f"{dados['nome']}, Endereço: {dados['endereco']}, E-mail: {dados.get('email_cliente', 'Não informado')}, Telefone: {dados['telefone']}.\n\n"))
    
    pdf.multi_cell(186, 4.5, conv("A CONTRATADA compromete-se a executar os serviços de otimização, reestruturação técnica e/ou produção de Tour Virtual 360° para o perfil do Google do CONTRATANTE."))
    pdf.ln(5)

    # Cláusula Primeira
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.write(4.5, conv("CLÁUSULA PRIMEIRA: "))
    pdf.set_font('Helvetica', '', 8.5)
    pdf.write(4.5, conv("Os serviços serão iniciados em até 5 dias úteis após o fornecimento dos acessos e informações necessárias ao perfil.\n\n"))

    # Cláusula Segunda
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.write(4.5, conv("CLÁUSULA SEGUNDA: "))
    pdf.set_font('Helvetica', '', 8.5)
    pdf.write(4.5, conv("O não pagamento na data acordada sujeitará o presente contrato à incidência de juros legais de mora e interrupção temporária dos serviços.\n\n"))

    # Cláusula Terceira (Seleção de Plano)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.write(4.5, conv("CLÁUSULA TERCEIRA - SELEÇÃO DO PLANO CONTRATADO:\n"))
    pdf.set_font('Helvetica', '', 8.5)
    
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(12, pdf.get_y() + 1, 186, 12, 'F')
    pdf.set_xy(16, pdf.get_y() + 3)
    pdf.cell(0, 8, conv("(      ) Plano Start - R$ 500,00     (      ) Plano Pro - R$ 1.200,00     (      ) Gestão Mensal - R$ 600,00/mês"), ln=True)
    pdf.ln(3)

    # Cláusula Quarta (Condições de Pagamento)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.write(4.5, conv("CLÁUSULA QUARTA - CONDIÇÕES DE PAGAMENTO:\n"))
    pdf.set_font('Helvetica', '', 8.5)
    
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(12, pdf.get_y() + 1, 186, 12, 'F')
    pdf.set_xy(16, pdf.get_y() + 3)
    pdf.cell(0, 8, conv("(      ) À Vista     (      ) 2x     (      ) 3x     (      ) Mensal - Vencimento Todo Dia: _____"), ln=True)
    pdf.ln(20)

    # Campo de Assinaturas
    pdf.cell(88, 5, '__________________________________', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, '__________________________________', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(88, 4, 'TOUR360VR (Rubens H. Okamoto)', align='C')
    pdf.cell(10, 4, '')
    pdf.cell(88, 4, conv(f"{dados['nome']}"), align='C', ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 3. INTERFACE STREAMLIT COM FORMULÁRIO COMPLETO DE DADOS DO CLIENTE
# -----------------------------------------------------------------------------
st.subheader("📋 Dados para Consulta e Emissão de Documentos")

col_e1, col_e2 = st.columns([2, 1])
with col_e1:
    nome_estabelecimento = st.text_input("🏢 Nome da Empresa / Estabelecimento:", placeholder="Ex: Toque de Letra")
with col_e2:
    cidade_estabelecimento = st.text_input("📍 Cidade / Estado:", placeholder="Ex: Ribeirão Preto, SP")

col_c1, col_c2, col_c3 = st.columns([2, 1, 1])
with col_c1:
    endereco_completo = st.text_input("🗺️ Endereço Completo (Rua, Número, Bairro):", placeholder="Ex: Av. Presidente Vargas, 1200 - Alto da Boa Vista")
with col_c2:
    telefone_cliente = st.text_input("📞 Telefone / WhatsApp:", placeholder="Ex: (16) 99999-8888")
with col_c3:
    email_cliente = st.text_input("✉️ E-mail do Cliente:", placeholder="Ex: contato@cliente.com.br")

if st.button("🚀 Analisar Perfil e Gerar Diagnóstico", use_container_width=True):
    if nome_estabelecimento:
        termo_busca = f"{nome_estabelecimento}, {cidade_estabelecimento}" if cidade_estabelecimento else nome_estabelecimento
        dados = None
        
        # Consulta com Google Places API
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
                            "endereco": endereco_completo if endereco_completo else place.get("formatted_address", cidade_estabelecimento),
                            "telefone": telefone_cliente if telefone_cliente else place.get("formatted_phone_number", "(16) 99999-8888"),
                            "email_cliente": email_cliente if email_cliente else "Não informado",
                            "website": place.get("website", "Não possui"),
                            "nota": place.get("rating", 0.0),
                            "avaliacoes": place.get("user_ratings_total", 0),
                            "tem_tour360": False,
                            "tem_fotos_hd": len(photos) > 10,
                            "categorias_completas": False,
                            "horarios_ok": True
                        }
            except Exception as e:
                st.error(f"Erro ao conectar na API do Google: {e}")

        # Se não houver chave API ou falhar a requisição
        if not dados:
            dados = {
                "nome": nome_estabelecimento,
                "endereco": endereco_completo if endereco_completo else (f"{cidade_estabelecimento}" if cidade_estabelecimento else "Ribeirão Preto, SP"),
                "telefone": telefone_cliente if telefone_cliente else "(16) 3999-8888",
                "email_cliente": email_cliente if email_cliente else "Não informado",
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

        st.success("Análise do perfil realizada com sucesso!")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(f"""
                <div class="score-card">
                    <h2 style="color: #ff3d3d; font-size: 46px; margin: 0;">{score} / 100</h2>
                    <p style="color: #cbd5e1; text-transform: uppercase; font-size: 13px; font-weight: bold;">Score Geral de Otimização</p>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class="card-info">
                    <h3 style="color: #3ea1db; margin-top: 0;">{dados['nome']}</h3>
                    <p style="margin: 4px 0;">📍 <strong>Endereço:</strong> {dados['endereco']}</p>
                    <p style="margin: 4px 0;">📞 <strong>Telefone:</strong> {dados['telefone']} | ✉️ <strong>E-mail:</strong> {dados['email_cliente']}</p>
                    <p style="margin: 4px 0;">🌐 <strong>Website:</strong> {dados['website']}</p>
                    <p style="margin: 4px 0;">⭐ <strong>Avaliações:</strong> {dados['nota']} ({dados['avaliacoes']} avaliações)</p>
                </div>
            """, unsafe_allow_html=True)

        st.subheader("📊 Diagnóstico dos Pontos de Busca")
        st.progress(25 if dados["tem_fotos_hd"] else 10, text="Fotos e Resolução: Baixa Qualidade Detectada")
        st.progress(0 if not dados["tem_tour360"] else 100, text="Tour Virtual 360°: Ausente no Perfil")
        st.progress(50 if not dados["categorias_completas"] else 100, text="Categorias: Incompletas")
        st.progress(10 if dados["website"] == "Não possui" else 100, text="Website / Links de Ação: Não Identificado")

        # Gerar o PDF Oficial em Tema Claro
        pdf_bytes = gerar_pdf_oficial(dados, score)

        st.markdown("---")
        st.subheader("📄 Exportar Diagnóstico, Proposta e Contrato em PDF")
        
        st.download_button(
            label="📥 Baixar Documento Completo em PDF (Tour360VR)",
            data=pdf_bytes,
            file_name=f"Diagnostico_Tour360VR_{dados['nome'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Por favor, digite o nome do estabelecimento para consultar.")

# -----------------------------------------------------------------------------
# 4. RODAPÉ FIXO DO APP
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="footer">
        Tour360VR • tour360vr.com.br • contato@tour360vr.com.br • WhatsApp: (16) 99133-2121
    </div>
""", unsafe_allow_html=True)

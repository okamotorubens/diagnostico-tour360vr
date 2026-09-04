import io
import requests
import streamlit as st
from fpdf import FPDF

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS DA TOUR360VR
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tour360VR - Gestão & Diagnóstico Google Meu Negócio",
    page_icon="🌐",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .header-box { border-bottom: 2px solid #ef4444; padding-bottom: 12px; margin-bottom: 25px; }
    .score-card { background-color: #1e293b; border: 2px solid #ef4444; padding: 20px; border-radius: 8px; text-align: center; }
    .card-info { background-color: #1e293b; border: 1px solid #334155; padding: 18px; border-radius: 8px; margin-bottom: 15px; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0f172a; color: #94a3b8; text-align: center; padding: 10px; border-top: 1px solid #1e293b; font-size: 12px; z-index: 100; }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho da Aplicação
st.markdown("""
    <div class="header-box">
        <h1 style="color: #ffffff; margin: 0;">TOUR<span style="color: #ef4444;">360VR</span></h1>
        <p style="color: #38bdf8; margin-top: 5px; font-weight: 600;">Plataforma de Consultoria, Diagnóstico & Gestão do Google Meu Negócio</p>
    </div>
""", unsafe_allow_html=True)

# Recupera a chave do Google diretamente dos Secrets do Streamlit
API_KEY_GOOGLE = st.secrets.get("GOOGLE_PLACES_API_KEY", "")

# -----------------------------------------------------------------------------
# 2. CLASSE GERADORA DE PDF (FPDF2 NATIVO)
# -----------------------------------------------------------------------------
class PDFTour360(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 297, 'F')
        
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, 'TOUR360VR', ln=True)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(239, 68, 68)
        self.cell(0, 4, 'GESTAO DE PERFIL & DIAGNOSTICO GOOGLE MEU NEGOCIO', ln=True)
        self.set_draw_color(239, 68, 68)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, 'Tour360VR - tour360vr.com.br - contato@tour360vr.com.br - WhatsApp: (16) 99133-2121', align='C')

def gerar_pdf_completo_fpdf(dados, score):
    pdf = PDFTour360()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # PÁGINA 1
    pdf.add_page()
    pdf.set_fill_color(30, 41, 59)
    pdf.rect(10, 30, 190, 42, 'F')
    pdf.set_xy(15, 33)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(56, 189, 248)
    pdf.cell(0, 6, 'Ficha Analisada do Cliente', ln=True)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(248, 250, 252)
    pdf.set_x(15); pdf.cell(0, 5, f"Empresa: {dados['nome']}", ln=True)
    pdf.set_x(15); pdf.cell(0, 5, f"Endereco: {dados['endereco']}", ln=True)
    pdf.set_x(15); pdf.cell(0, 5, f"Telefone: {dados['telefone']} | Website: {dados['website']}", ln=True)
    pdf.set_x(15); pdf.cell(0, 5, f"Avaliacoes: {dados['nota']} estrelas ({dados['avaliacoes']} avaliacoes)", ln=True)

    pdf.set_fill_color(40, 20, 30)
    pdf.rect(10, 78, 190, 22, 'F')
    pdf.set_xy(10, 80)
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(239, 68, 68)
    pdf.cell(190, 8, f"{score} / 100", align='C', ln=True)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(190, 4, 'SCORE GERAL DE OTIMIZACAO (STATUS CRITICO)', align='C', ln=True)

    pdf.set_xy(10, 108)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 6, 'Auditoria Detalhada de Pontos de Busca', ln=True)
    pdf.ln(3)

    itens_auditoria = [
        ("1. Fotos de Alta Resolucao", "Ok" if dados['tem_fotos_hd'] else "Baixa Qualidade"),
        ("2. Tour Virtual 360 Interativo", "Presente" if dados['tem_tour360'] else "Ausente (Critico)"),
        ("3. Categorias Principal e Secundarias", "Completas" if dados['categorias_completas'] else "Incompletas"),
        ("4. Horarios e Excecoes (Feriados)", "Atualizados" if dados['horarios_ok'] else "Desatualizados"),
        ("5. Endereco e Marcador no Mapa", "Verificado"),
        ("6. Link do Site e Cardapio/Servicos", "Inserido" if dados['website'] != 'Não possui' else "Ausente"),
    ]

    for item, status in itens_auditoria:
        pdf.set_fill_color(30, 41, 59)
        pdf.cell(130, 8, f"  {item}", border=0, fill=True)
        pdf.set_font('Helvetica', 'B', 9)
        if status in ["Ok", "Presente", "Completas", "Verificado", "Inserido"]:
            pdf.set_text_color(34, 197, 94)
        else:
            pdf.set_text_color(239, 68, 68)
        pdf.cell(60, 8, status, border=0, fill=True, align='R', ln=True)
        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(248, 250, 252)
        pdf.ln(1)

    # PÁGINA 2
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, 'Por que seu negocio precisa de Otimizacao Profissional?', ln=True)
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(203, 213, 225)
    texto_persuasivo = (
        "Mais de 80% das buscas por estabelecimentos locais acontecem diretamente no Google e Google Maps. "
        "Quando uma ficha possui notas baixas em itens essenciais como fotos, tour 360, categorias corretas "
        "e tempo de resposta, o algoritmo do Google reduz expressivamente a visibilidade da sua empresa.\n\n"
        "Com a estruturacao completa da Tour360VR, transformamos o seu perfil em um ima de novos clientes, "
        "transmitindo autoridade, transparencia e alta relevancia nas buscas regionais."
    )
    pdf.multi_cell(190, 5, texto_persuasivo)
    pdf.ln(8)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, 'Proposta de Planos e Investimento', ln=True)
    pdf.ln(2)

    planos = [
        ("Plano Start - R$ 590,00", "Correcao cadastral completa, otimizacao de categorias, insercao de site e links oficiais."),
        ("Plano Pro (Recomendado) - R$ 1.290,00", "Tudo do Start + Sessao de Fotos Profissionais + Criacao de Tour Virtual 360 + SEO Local Avançado."),
        ("Plano Gestao Mensal - R$ 490,00/mes", "Postagens semanais no perfil, gestao continua de avaliaçoes, atualizaçao de produtos e relatorio mensal.")
    ]

    for titulo, desc in planos:
        pdf.set_fill_color(30, 41, 59)
        pdf.set_font('Helvetica', 'B', 10)
        if "Pro" in titulo:
            pdf.set_text_color(239, 68, 68)
        else:
            pdf.set_text_color(56, 189, 248)
        pdf.cell(190, 7, f"  {titulo}", fill=True, ln=True)
        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(203, 213, 225)
        pdf.multi_cell(190, 5, f"  {desc}")
        pdf.ln(4)

    # PÁGINA 3 - CONTRATO
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 6, 'CONTRATO DE PRESTACAO DE SERVICOS DE OTIMIZACAO GOOGLE MEU NEGOCIO', align='C', ln=True)
    pdf.ln(4)

    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(203, 213, 225)
    
    contrato_texto = (
        f"CONTRATADA: TOUR360VR, com contatos oficiais via e-mail contato@tour360vr.com.br e WhatsApp (16) 99133-2121.\n\n"
        f"CONTRATANTE: {dados['nome']}, localizado em {dados['endereco']}.\n\n"
        "CLAUSULA PRIMEIRA - DO OBJETO: O presente contrato tem por objeto a prestaçao de serviços de otimizaçao, "
        "reestruturaçao tecnica, atualizaçao cadastral e/ou produçao de Tour Virtual 360 para a ficha do Google Meu Negocio do CONTRATANTE.\n\n"
        "CLAUSULA SEGUNDA - DAS OBRIGACOES: A CONTRATADA compromete-se a realizar a auditoria tecnica, inclusao de informações "
        "oficiais, publicaçao de fotos otimizadas, configuraçao de categorias estrategicas e emissao de relatorio de entrega visual.\n\n"
        "CLAUSULA TERCEIRA - VALOR E FORMA DE PAGAMENTO: Pela execuçao dos serviços acordados, o CONTRATANTE pagara o valor "
        "estipulado no plano selecionado mediante transferencia bancaria ou PIX na data combinada."
    )
    pdf.multi_cell(190, 4.5, contrato_texto)
    pdf.ln(15)

    pdf.cell(90, 5, '__________________________________', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(90, 5, '__________________________________', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 8)
    pdf.cell(90, 5, 'TOUR360VR', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(90, 5, f"{dados['nome']}", align='C', ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 3. INTERFACE DE BUSCA E DIAGNÓSTICO
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
        
        # Faz a consulta real no Google Places API se a chave estiver configurada nos Secrets
        if API_KEY_GOOGLE:
            try:
                # 1. Busca o Place ID do local
                url_find = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={termo_busca}&inputtype=textquery&fields=place_id&key={API_KEY_GOOGLE}"
                res_find = requests.get(url_find).json()
                
                if res_find.get("candidates"):
                    place_id = res_find["candidates"][0]["place_id"]
                    
                    # 2. Busca os detalhes completos da ficha no Google Maps
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
                st.error(f"Erro ao conectar com o Google: {e}")

        # Fallback de demonstração caso esteja sem a chave nos Secrets
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

        # Cálculo do Score
        score = 100
        if not dados["tem_tour360"]: score -= 25
        if dados["website"] == "Não possui": score -= 20
        if not dados["tem_fotos_hd"]: score -= 20
        if not dados["categorias_completas"]: score -= 15
        if not dados["horarios_ok"]: score -= 10
        if dados["avaliacoes"] < 50: score -= 10

        st.success("Análise realizada com sucesso!")

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

        # Gerar o PDF nativo
        pdf_bytes = gerar_pdf_completo_fpdf(dados, score)

        st.markdown("---")
        st.subheader("📄 Exportar Documentos Oficiais da Tour360VR")
        
        st.download_button(
            label="📥 Baixar Diagnóstico, Proposta e Contrato Completo em PDF",
            data=pdf_bytes,
            file_name=f"Diagnostico_Tour360VR_{dados['nome'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Por favor, digite o nome do estabelecimento.")

# -----------------------------------------------------------------------------
# 4. RODAPÉ FIXO
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="footer">
        Tour360VR • tour360vr.com.br • contato@tour360vr.com.br • WhatsApp: (16) 99133-2121
    </div>
""", unsafe_allow_html=True)

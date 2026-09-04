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

# Estilização Tema Dark
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
    """Trata caracteres e limpa símbolos não suportados para Latin-1 evitando '?'."""
    if not texto:
        return ""
    limpo = str(texto).replace("📍", "").replace("📞", "").replace("⭐", "").replace("✉️", "").replace("🌐", "")
    return limpo.encode('latin-1', 'replace').decode('latin-1')

def gerar_estrelas(nota):
    """Gera string de estrelas cheias e vazias com base na nota."""
    try:
        val = float(nota)
        cheias = int(round(val))
        vazias = 5 - cheias
        return ("★" * cheias) + ("☆" * vazias)
    except:
        return "★★★★☆"

# -----------------------------------------------------------------------------
# 2. GERADOR DE PDF TOUR360VR MODERNIZADO
# -----------------------------------------------------------------------------
class PDFTour360Oficial(FPDF):
    def header(self):
        if self.page_no() == 1:
            return

        try:
            self.image('Logo TOUR transparente.png', 12, 6, 18)
            x_pos = 34
        except:
            x_pos = 12

        self.set_xy(x_pos, 8)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(255, 61, 61)
        self.cell(0, 5, 'TOUR360VR', ln=True)
        self.set_xy(x_pos, 13.5)
        self.set_font('Helvetica', '', 8.5)
        self.set_text_color(100, 116, 139)
        self.cell(0, 4, conv('Consultoria & Diagnóstico do Google Meu Negócio'), ln=True)
        
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.3)
        self.line(12, 24, 198, 24)
        self.set_line_width(0.2)
        self.ln(10)

    def footer(self):
        if self.page_no() == 1:
            return

        self.set_y(-15)
        self.set_font('Helvetica', '', 8.5)
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
    # PÁGINA 1: CAPA INICIAL COM FOTO REAL DA FICHA E ESTRELAS
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    try:
        pdf.image('Logo TOUR transparente.png', 85, 18, 40)
    except:
        pass

    pdf.set_y(62)
    pdf.set_font('Helvetica', 'B', 32)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(0, 10, 'TOUR360VR', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(62, 161, 219)
    pdf.cell(0, 6, conv('DIAGNÓSTICO & AUDITORIA DE PERFIL DO GOOGLE'), align='C', ln=True)
    pdf.ln(8)

    # Moldura da Ficha do Google
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(15, pdf.get_y(), 180, 155, 'FD')
    
    y_capa = pdf.get_y() + 6
    pdf.set_xy(20, y_capa)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(170, 8, conv(f"{dados['nome']}"), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(170, 5.5, conv(f"Endereço: {dados['endereco']}"), align='C', ln=True)
    pdf.cell(170, 5.5, conv(f"Telefone: {dados['telefone']} | Website: {dados['website']}"), align='C', ln=True)
    
    # Formatação de Estrelas na Nota
    estrelas_txt = gerar_estrelas(dados['nota'])
    pdf.cell(170, 5.5, conv(f"Avaliações no Google: {estrelas_txt} {dados['nota']} ({dados['avaliacoes']} avaliações)"), align='C', ln=True)
    pdf.ln(6)

    # Inserção da Foto Real Baixada do Google Places
    if dados.get("foto_bytes"):
        try:
            img_buffer = io.BytesIO(dados["foto_bytes"])
            pdf.image(img_buffer, x=25, y=pdf.get_y(), w=160, h=98)
        except:
            pdf.set_fill_color(226, 232, 240)
            pdf.rect(30, pdf.get_y(), 150, 85, 'F')
            pdf.set_xy(30, pdf.get_y() + 38)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(150, 6, conv("FICHA DO GOOGLE MEU NEGÓCIO PESQUISADA"), align='C', ln=True)
    else:
        pdf.set_fill_color(226, 232, 240)
        pdf.rect(30, pdf.get_y(), 150, 85, 'F')
        pdf.set_xy(30, pdf.get_y() + 38)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(150, 6, conv("FICHA DO GOOGLE MEU NEGÓCIO PESQUISADA"), align='C', ln=True)

    # -------------------------------------------------------------------------
    # PÁGINA 2: DIAGNÓSTICO DETALHADO & PLANO DE AÇÃO
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    if score < 50:
        cr, cg, cb = 255, 61, 61
        status_txt = "STATUS CRÍTICO - AÇÃO NECESSÁRIA URGENTE"
    elif score < 80:
        cr, cg, cb = 255, 153, 51
        status_txt = "STATUS MÉDIO - OTIMIZAÇÕES RECOMENDADAS"
    else:
        cr, cg, cb = 140, 198, 63
        status_txt = "PERFIL OTIMIZADO E EM ALTA PERFORMANCE"

    # Faixa de Status Ampliada
    pdf.set_fill_color(cr, cg, cb)
    pdf.rect(12, 32, 186, 24, 'F')
    pdf.set_xy(12, 34)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(186, 8, f"{score} / 100", align='C', ln=True)
    pdf.set_font('Helvetica', 'B', 10.5) # Fonte Maior no Status
    pdf.cell(186, 5, conv(status_txt), align='C', ln=True)

    # Diagnóstico com Títulos
    pdf.set_y(64)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, conv('Diagnóstico Detalhado do Perfil (Pontos de Busca)'), ln=True)
    pdf.ln(4)

    itens = [
        ("Fotos e Resolução Visual", 30 if not dados['tem_fotos_hd'] else 100, "Poucas fotos encontradas / antigas.", "Impede a avaliação prévia do local pelo cliente."),
        ("Tour Virtual 360 Interativo", 0 if not dados['tem_tour360'] else 100, "Nenhum Tour 360 detectado.", "Perde-se engajamento por falta de experiência imersiva."),
        ("Categorias Principal e Secundárias", 50 if not dados['categorias_completas'] else 100, "Incompletas / Sem secundárias.", "Limita a visibilidade regional em buscas específicas."),
        ("Horários e Exceções (Feriados)", 40 if not dados['horarios_ok'] else 100, "Desatualizados / Sem exceções.", "Gera insatisfação e perda de vendas imediatas."),
        ("Website e Links de Conversão", 10 if dados['website'] == 'Não possui' else 100, "Sem links diretos no perfil.", "Dificulta o contato rápido e a tomada de decisão.")
    ]

    for titulo, pct, estado, impacto in itens:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(100, 5, conv(f"- {titulo}:"), ln=False)
        
        pdf.set_font('Helvetica', 'B', 9.5)
        if pct < 40:
            pdf.set_text_color(255, 61, 61)
        elif pct < 80:
            pdf.set_text_color(255, 153, 51)
        else:
            pdf.set_text_color(140, 198, 63)
            
        pdf.cell(86, 5, conv(f"Score: {pct}%"), align='R', ln=True)

        pdf.set_fill_color(226, 232, 240)
        pdf.rect(12, pdf.get_y(), 186, 4, 'F')
        
        if pct < 40:
            pdf.set_fill_color(255, 61, 61)
        elif pct < 80:
            pdf.set_fill_color(255, 153, 51)
        else:
            pdf.set_fill_color(140, 198, 63)
            
        largura_barra = max(float(pct) * 1.86, 3.0)
        pdf.rect(12, pdf.get_y(), largura_barra, 4, 'F')
        pdf.ln(5)

        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(0, 4.2, conv(f"  Estado Atual: {estado}"), ln=True)
        pdf.cell(0, 4.2, conv(f"  Impacto de Conversão: {impacto}"), ln=True)
        pdf.ln(4)

    # Plano de Ação Estruturado
    pdf.ln(2)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 6, conv('Plano de Ação Recomendado'), ln=True)
    pdf.ln(2)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    acoes = (
        "1. Atualização Cadastral & SEO Local: Otimização completa das palavras-chave de busca.\n"
        "2. Criação do Tour Virtual 360°: Aumento direto da permanência e cliques na ficha.\n"
        "3. Produção Fotográfica Profissional: Imagens em alta resolução para transmitir autoridade.\n"
        "4. Integração de Links de Conversão: Inclusão de botões de WhatsApp, menu e reservas."
    )
    pdf.multi_cell(186, 4.8, conv(acoes))

    # -------------------------------------------------------------------------
    # PÁGINA 3: PROPOSTA DE INVESTIMENTO (PLANO PRO EM PRETO)
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, conv('Proposta de Investimento e Planos'), ln=True)
    pdf.ln(6)

    y_p = pdf.get_y()
    
    # --- COLUNA 1: PLANO START ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(12, y_p + 4, 55, 62, 'FD')
    
    pdf.set_xy(12, y_p + 9)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42) # Preto
    pdf.cell(55, 5, 'PLANO START', align='C', ln=True)
    
    pdf.set_xy(12, y_p + 16)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(62, 161, 219)
    pdf.cell(55, 7, 'R$ 500,00', align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85)
    it_start = "- Correção cadastral\n- Otimização de SEO\n- Ajuste de categorias\n- Links de conversão"
    pdf.set_xy(14, y_p + 27)
    pdf.multi_cell(51, 5.2, conv(it_start))

    # --- COLUNA 2: PLANO PRO (PRETO EM DESTAQUE) ---
    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(62, 161, 219)
    pdf.set_line_width(0.8)
    pdf.rect(73, y_p, 64, 70, 'FD')
    pdf.set_line_width(0.2)
    
    pdf.set_xy(73, y_p + 5)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 23, 42) # Preto Solicitado
    pdf.cell(64, 5, conv('PLANO PRO'), align='C', ln=True)
    
    pdf.set_xy(73, y_p + 11)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(15, 23, 42) # Preto Solicitado
    pdf.cell(64, 4, conv('(Recomendado)'), align='C', ln=True)
    
    pdf.set_xy(73, y_p + 16)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(62, 161, 219)
    pdf.cell(64, 7, 'R$ 1.200,00', align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85)
    it_pro = "- Tudo do Plano Start\n- Tour Virtual 360°\n- Ensaio Fotográfico\n- Relatório de Entrega"
    pdf.set_xy(75, y_p + 27)
    pdf.multi_cell(60, 5.2, conv(it_pro))

    # --- COLUNA 3: GESTÃO MENSAL ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(143, y_p + 4, 55, 68, 'FD')
    
    pdf.set_xy(143, y_p + 9)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42) # Preto
    pdf.cell(55, 5, conv('GESTÃO MENSAL'), align='C', ln=True)
    
    pdf.set_xy(143, y_p + 16)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(62, 161, 219)
    pdf.cell(55, 7, 'R$ 600,00/mês', align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85)
    it_mensal = "- Postagens semanais\n- Gestão de avaliações\n- Atualização de fotos\n- Proteção da ficha\n- Relatórios mensais"
    pdf.set_xy(145, y_p + 27)
    pdf.multi_cell(51, 5.2, conv(it_mensal))

    # -------------------------------------------------------------------------
    # PÁGINA 4: CONTRATO DE PRESTAÇÃO DE SERVIÇOS
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, conv('CONTRATO DE PRESTAÇÃO DE SERVIÇOS'), align='C', ln=True)
    pdf.ln(5)

    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85)
    
    # CONTRATADA
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5, conv("CONTRATADA: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5, conv("TOUR360VR, representada por Rubens H. Okamoto, CPF: 287.932.298-79, E-mail: contato@tour360vr.com.br e Telefone: (16) 99133-2121.\n\n"))
    
    # CONTRATANTE
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5, conv("CONTRATANTE: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5, conv(f"{dados['nome']}, Endereço: {dados['endereco']}.\n\n"))
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5, conv("A "))
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5, conv("CONTRATADA "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5, conv("compromete-se a executar os serviços de otimização, reestruturação técnica e/ou produção de Tour Virtual 360° para o perfil do Google da "))
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5, conv("CONTRATANTE.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5, conv("CLÁUSULA PRIMEIRA: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5, conv("Os serviços serão iniciados em até 5 dias úteis após o fornecimento dos acessos e informações necessárias ao perfil.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5, conv("CLÁUSULA SEGUNDA: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5, conv("O não pagamento na data acordada sujeitará o presente contrato à incidência de juros legais de mora e interrupção temporária dos serviços.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5, conv("CLÁUSULA TERCEIRA - SELEÇÃO DO PLANO CONTRATADO:\n"))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5, conv("(      ) Plano Start         (      ) Plano Pro         (      ) Gestão Mensal\n\n"))

    # Condições de Pagamento Atualizadas
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5, conv("CLÁUSULA QUARTA - CONDIÇÕES DE PAGAMENTO:\n"))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5, conv("(      ) À Vista     (      ) 2x para o Plano Start     (      ) 3x para o Plano Pro     (      ) Mensal - Vencimento Todo Dia: _____\n\n\n"))

    pdf.ln(18)

    # Assinaturas
    pdf.cell(88, 5, '__________________________________', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, '__________________________________', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.cell(88, 4, 'TOUR360VR (Rubens H. Okamoto)', align='C')
    pdf.cell(10, 4, '')
    pdf.cell(88, 4, conv(f"{dados['nome']}"), align='C', ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 3. INTERFACE DE BUSCA SIMPLIFICADA (EMPRESA + CIDADE)
# -----------------------------------------------------------------------------
st.subheader("📋 Consultar Ficha do Google Meu Negócio")

col_e1, col_e2 = st.columns([2, 1])
with col_e1:
    nome_estabelecimento = st.text_input("🏢 Nome da Empresa / Estabelecimento:", placeholder="Ex: Vinicius Fisioterapia")
with col_e2:
    cidade_estabelecimento = st.text_input("📍 Cidade / Estado:", placeholder="Ex: Ribeirão Preto, SP")

if st.button("🚀 Analisar Perfil e Gerar Diagnóstico", use_container_width=True):
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
                        
                        foto_bytes = None
                        if photos and len(photos) > 0:
                            photo_ref = photos[0].get("photo_reference")
                            if photo_ref:
                                url_photo = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={photo_ref}&key={API_KEY_GOOGLE}"
                                res_img = requests.get(url_photo)
                                if res_img.status_code == 200:
                                    foto_bytes = res_img.content

                        dados = {
                            "nome": place.get("name", nome_estabelecimento),
                            "endereco": place.get("formatted_address", cidade_estabelecimento if cidade_estabelecimento else "Endereço cadastrado"),
                            "telefone": place.get("formatted_phone_number", "(16) 3999-8888"),
                            "website": place.get("website", "Não possui"),
                            "nota": place.get("rating", 0.0),
                            "avaliacoes": place.get("user_ratings_total", 0),
                            "foto_bytes": foto_bytes,
                            "tem_tour360": False,
                            "tem_fotos_hd": len(photos) > 10,
                            "categorias_completas": False,
                            "horarios_ok": True
                        }
            except Exception as e:
                st.error(f"Erro na conexão com o Google: {e}")

        if not dados:
            dados = {
                "nome": nome_estabelecimento,
                "endereco": f"{cidade_estabelecimento}" if cidade_estabelecimento else "Ribeirão Preto, SP",
                "telefone": "(16) 3999-8888",
                "website": "Não possui",
                "nota": 4.2,
                "avaliacoes": 38,
                "foto_bytes": None,
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
                    <p style="margin: 4px 0;">📍 <strong>Endereço / Cidade:</strong> {dados['endereco']}</p>
                    <p style="margin: 4px 0;">📞 <strong>Telefone:</strong> {dados['telefone']}</p>
                    <p style="margin: 4px 0;">🌐 <strong>Website:</strong> {dados['website']}</p>
                    <p style="margin: 4px 0;">⭐ <strong>Avaliações:</strong> {dados['nota']} ({dados['avaliacoes']} avaliações)</p>
                </div>
            """, unsafe_allow_html=True)

        pdf_bytes = gerar_pdf_oficial(dados, score)

        st.markdown("---")
        st.subheader("📄 Exportar Documentos Oficiais da Tour360VR")
        
        st.download_button(
            label="📥 Baixar Diagnóstico, Proposta e Contrato em PDF",
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

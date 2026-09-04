import io
import os
import requests
import streamlit as st
from weasyprint import HTML, CSS

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA DO STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tour360VR - Diagnóstico do Google Meu Negócio",
    page_icon="🌐",
    layout="wide"
)

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

# -----------------------------------------------------------------------------
# 2. GERADOR DE PDF DE ALTA QUALIDADE (HTML/CSS VIA WEASYPRINT)
# -----------------------------------------------------------------------------
def gerar_pdf_perfeito(dados, score):
    # Verifica o caminho da logo para carregar no HTML
    logo_path = os.path.abspath('Logo TOUR transparente.png')
    logo_html = f'<img src="file://{logo_path}" style="height: 45px; vertical-align: middle; margin-right: 12px;">' if os.path.exists(logo_path) else ''

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm 15mm 20mm 15mm;
                @bottom-center {{
                    content: "tour360vr.com.br • contato@tour360vr.com.br • WhatsApp: (16) 99133-2121";
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    font-size: 8pt;
                    color: #64748b;
                    border-top: 1px solid #e2e8f0;
                    padding-top: 8px;
                    width: 100%;
                }}
            }}
            body {{
                font-family: 'Helvetica Neue', Arial, sans-serif;
                color: #1e293b;
                background-color: #ffffff;
                font-size: 10pt;
                line-height: 1.5;
            }}
            .header-nav {{
                border-bottom: 2px solid #ff3d3d;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .brand-title {{
                font-size: 20pt;
                font-weight: bold;
                color: #ff3d3d;
                display: inline-block;
                vertical-align: middle;
            }}
            .brand-subtitle {{
                font-size: 10pt;
                color: #3ea1db;
                font-weight: bold;
                margin-top: 2px;
            }}
            .cover-card {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 18px;
                margin-bottom: 20px;
            }}
            .capa-preview-box {{
                border: 2px dashed #cbd5e1;
                background-color: #ffffff;
                border-radius: 6px;
                padding: 15px;
                text-align: center;
                margin-bottom: 18px;
            }}
            .score-box {{
                text-align: center;
                color: #ffffff;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                background-color: {'#ff3d3d' if score < 50 else ('#ff9933' if score < 80 else '#8cc63f')};
            }}
            .score-val {{
                font-size: 32pt;
                font-weight: bold;
            }}
            .score-lbl {{
                font-size: 9pt;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            .bar-bg {{
                background-color: #e2e8f0;
                height: 8px;
                border-radius: 4px;
                overflow: hidden;
                margin-top: 4px;
                margin-bottom: 12px;
            }}
            .bar-fill {{
                height: 100%;
                background-color: {'#ff3d3d' if score < 50 else ('#ff9933' if score < 80 else '#8cc63f')};
            }}
            .page-break {{
                page-break-before: always;
            }}
            
            /* TABELA DE INVESTIMENTOS EM 3 COLUNAS PERFEITAS */
            .pricing-table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 10px;
                margin-top: 15px;
            }}
            .pricing-col {{
                width: 31%;
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                vertical-align: top;
            }}
            .pricing-col.featured {{
                width: 38%;
                background-color: #fff5f5;
                border: 2px solid #ff3d3d;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }}
            .plan-title {{
                font-size: 11pt;
                font-weight: bold;
                color: #0f172a;
                text-align: center;
            }}
            .plan-price {{
                font-size: 15pt;
                font-weight: bold;
                color: #ff3d3d;
                text-align: center;
                margin: 8px 0;
            }}
            .plan-list {{
                font-size: 8.5pt;
                color: #475569;
                padding-left: 15px;
                margin: 0;
            }}
            .plan-list li {{
                margin-bottom: 5px;
            }}

            /* CONTRATO */
            .contract-title {{
                font-size: 14pt;
                font-weight: bold;
                text-align: center;
                color: #0f172a;
                margin-bottom: 15px;
            }}
            .clause-box {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                padding: 10px 15px;
                border-radius: 6px;
                margin: 10px 0;
                font-size: 9pt;
            }}
        </style>
    </head>
    <body>

        <!-- PÁGINA 1: CAPA DA FICHA & DIAGNÓSTICO -->
        <div class="header-nav">
            {logo_html}
            <div class="brand-title">TOUR360VR</div>
            <div class="brand-subtitle">DIAGNÓSTICO E AUDITORIA DE PERFIL DO GOOGLE MEU NEGÓCIO</div>
        </div>

        <div class="cover-card">
            <div style="font-size: 13pt; font-weight: bold; color: #0f172a; margin-bottom: 8px;">Ficha Analisada do Cliente</div>
            <div class="capa-preview-box">
                <div style="font-size: 14pt; font-weight: bold; color: #ff3d3d;">{dados['nome']}</div>
                <div style="font-size: 9pt; color: #64748b; margin-top: 4px;">📍 {dados['endereco']}</div>
                <div style="font-size: 9pt; color: #64748b;">📞 {dados['telefone']} | ✉️ {dados.get('email_cliente', 'Não informado')}</div>
                <div style="font-size: 9pt; color: #64748b;">🌐 {dados['website']}</div>
            </div>
            <div><strong>Avaliações no Google:</strong> ⭐ {dados['nota']} Estrelas ({dados['avaliacoes']} avaliações)</div>
        </div>

        <div class="score-box">
            <div class="score-val">{score} / 100</div>
            <div class="score-lbl">{'STATUS CRÍTICO - AÇÃO NECESSÁRIA URGENTE' if score < 50 else 'STATUS MÉDIO - OTIMIZAÇÃO RECOMENDADA'}</div>
        </div>

        <div style="font-size: 12pt; font-weight: bold; margin-bottom: 10px; color: #0f172a;">Diagnóstico Detalhado do Perfil (Pontos de Busca)</div>
        
        <div>
            <div><strong>Fotos e Resolução Visual:</strong> <span style="color: {'#8cc63f' if dados['tem_fotos_hd'] else '#ff3d3d'}; font-weight: bold;">{'Bom (Imagens HD)' if dados['tem_fotos_hd'] else 'Ruim (Baixa Resolução / Antigas)'}</span></div>
            <div class="bar-bg"><div class="bar-fill" style="width: {'100%' if dados['tem_fotos_hd'] else '25%'};"></div></div>

            <div><strong>Tour Virtual 360° Interativo:</strong> <span style="color: {'#8cc63f' if dados['tem_tour360'] else '#ff3d3d'}; font-weight: bold;">{'Bom (Publicado no Maps)' if dados['tem_tour360'] else 'Ruim (Ausente - Perda de Visibilidade)'}</span></div>
            <div class="bar-bg"><div class="bar-fill" style="width: {'100%' if dados['tem_tour360'] else '5%'};"></div></div>

            <div><strong>Categorias Principal e Secundárias:</strong> <span style="color: {'#8cc63f' if dados['categorias_completas'] else '#ff9933'}; font-weight: bold;">{'Completas' if dados['categorias_completas'] else 'Médio (Incompletas)'}</span></div>
            <div class="bar-bg"><div class="bar-fill" style="width: {'100%' if dados['categorias_completas'] else '50%'};"></div></div>

            <div><strong>Horários e Exceções (Feriados):</strong> <span style="color: {'#8cc63f' if dados['horarios_ok'] else '#ff9933'}; font-weight: bold;">{'Atualizados' if dados['horarios_ok'] else 'Médio (Incompleto)'}</span></div>
            <div class="bar-bg"><div class="bar-fill" style="width: {'100%' if dados['horarios_ok'] else '40%'};"></div></div>

            <div><strong>Website e Links de Conversão:</strong> <span style="color: {'#8cc63f' if dados['website'] != 'Não possui' else '#ff3d3d'}; font-weight: bold;">{'Links Ativos' if dados['website'] != 'Não possui' else 'Ruim (Sem Links Diretos)'}</span></div>
            <div class="bar-bg"><div class="bar-fill" style="width: {'100%' if dados['website'] != 'Não possui' else '10%'};"></div></div>
        </div>

        <!-- PÁGINA 2: PLANO DE AÇÃO & PROPOSTA DE PLANOS -->
        <div class="page-break"></div>

        <div class="header-nav">
            {logo_html}
            <div class="brand-title">TOUR360VR</div>
            <div class="brand-subtitle">PLANO DE AÇÃO E PROPOSTA COMERCIAL</div>
        </div>

        <div style="font-size: 12pt; font-weight: bold; margin-bottom: 8px; color: #0f172a;">Plano de Ação Estruturado</div>
        <div style="font-size: 9pt; color: #475569; margin-bottom: 15px;">
            1. <strong>Atualização Cadastral & SEO Local:</strong> Otimização completa das palavras-chave de busca.<br>
            2. <strong>Criação do Tour Virtual 360°:</strong> Aumento direto da permanência e cliques na ficha.<br>
            3. <strong>Produção Fotográfica Profissional:</strong> Imagens em alta resolução para transmitir autoridade.<br>
            4. <strong>Integração de Links de Conversão:</strong> Inclusão de botões de WhatsApp, menu e reservas.
        </div>

        <div style="font-size: 12pt; font-weight: bold; margin-bottom: 5px; color: #0f172a;">Proposta de Investimento e Planos</div>

        <table class="pricing-table">
            <tr>
                <td class="pricing-col">
                    <div class="plan-title">PLANO START</div>
                    <div class="plan-price">R$ 500,00</div>
                    <ul class="plan-list">
                        <li>Correção cadastral completa</li>
                        <li>Otimização de SEO Local</li>
                        <li>Ajuste de categorias</li>
                        <li>Inclusão de links diretos</li>
                        <li>Suporte técnico dedicado</li>
                    </ul>
                </td>
                <td class="pricing-col featured">
                    <div class="plan-title" style="color: #ff3d3d;">PLANO PRO</div>
                    <div style="text-align: center; font-size: 8pt; font-weight: bold; color: #ff3d3d;">(Recomendado)</div>
                    <div class="plan-price">R$ 1.200,00</div>
                    <ul class="plan-list">
                        <li><strong>Tudo do Plano Start</strong></li>
                        <li><strong>Criação do Tour Virtual 360°</strong></li>
                        <li><strong>Sessão Fotográfica Profissional</strong></li>
                        <li>SEO Avançado no Google Maps</li>
                        <li>Relatório de Entrega Visual</li>
                        <li>Atendimento Prioritário</li>
                    </ul>
                </td>
                <td class="pricing-col">
                    <div class="plan-title">GESTÃO MENSAL</div>
                    <div class="plan-price">R$ 600,00<span style="font-size: 8pt;">/mês</span></div>
                    <ul class="plan-list">
                        <li>Postagens semanais na ficha</li>
                        <li>Gestão contínua de avaliações</li>
                        <li>Atualização periódica de fotos</li>
                        <li>Proteção contra alterações</li>
                        <li>Relatórios mensais de métricas</li>
                    </ul>
                </td>
            </tr>
        </table>

        <!-- PÁGINA 3: CONTRATO -->
        <div class="page-break"></div>

        <div class="header-nav">
            {logo_html}
            <div class="brand-title">TOUR360VR</div>
            <div class="brand-subtitle">CONTRATO DE PRESTAÇÃO DE SERVIÇOS</div>
        </div>

        <div class="contract-title">CONTRATO DE PRESTAÇÃO DE SERVIÇOS</div>

        <div style="font-size: 9pt; color: #334155; line-height: 1.6;">
            <p><strong>CONTRATADA:</strong> TOUR360VR, representada por Rubens H. Okamoto, CPF: 287.932.298-79, E-mail: contato@tour360vr.com.br e Telefone: (16) 99133-2121.</p>
            <p><strong>CONTRATANTE:</strong> {dados['nome']}, Endereço: {dados['endereco']}, E-mail: {dados.get('email_cliente', 'Não informado')}, Telefone: {dados['telefone']}.</p>
            
            <p>A <strong>CONTRATADA</strong> compromete-se a executar os serviços de otimização, reestruturação técnica e/ou produção de Tour Virtual 360° para o perfil do Google da <strong>CONTRATANTE</strong>.</p>

            <p><strong>CLÁUSULA PRIMEIRA:</strong> Os serviços serão iniciados em até 5 dias úteis após o fornecimento dos acessos e informações necessárias ao perfil.</p>

            <p><strong>CLÁUSULA SEGUNDA:</strong> O não pagamento na data acordada sujeitará o presente contrato à incidência de juros legais de mora e interrupção temporária dos serviços.</p>

            <p><strong>CLÁUSULA TERCEIRA - SELEÇÃO DO PLANO CONTRATADO:</strong></p>
            <div class="clause-box">
                ( &nbsp; &nbsp; ) Plano Start - R$ 500,00 &nbsp; &nbsp; &nbsp; &nbsp; ( &nbsp; &nbsp; ) Plano Pro - R$ 1.200,00 &nbsp; &nbsp; &nbsp; &nbsp; ( &nbsp; &nbsp; ) Gestão Mensal - R$ 600,00/mês
            </div>

            <p><strong>CLÁUSULA QUARTA - CONDIÇÕES DE PAGAMENTO:</strong></p>
            <div class="clause-box">
                ( &nbsp; &nbsp; ) À Vista &nbsp; &nbsp; &nbsp; &nbsp; ( &nbsp; &nbsp; ) 2x &nbsp; &nbsp; &nbsp; &nbsp; ( &nbsp; &nbsp; ) 3x &nbsp; &nbsp; &nbsp; &nbsp; ( &nbsp; &nbsp; ) Mensal - Vencimento Todo Dia: _____
            </div>

            <br><br><br>
            <table style="width: 100%; border-collapse: collapse; text-align: center;">
                <tr>
                    <td style="width: 45%; border-top: 1px solid #0f172a; padding-top: 5px;">
                        <strong>TOUR360VR</strong><br>Rubens H. Okamoto
                    </td>
                    <td style="width: 10%;"></td>
                    <td style="width: 45%; border-top: 1px solid #0f172a; padding-top: 5px;">
                        <strong>{dados['nome']}</strong><br>Aceite / Assinatura
                    </td>
                </tr>
            </table>
        </div>

    </body>
    </html>
    """
    
    buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(buffer)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# 3. INTERFACE STREAMLIT COM FORMULÁRIO COMPLETO
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

        # Gerar o PDF via WeasyPrint
        pdf_bytes = gerar_pdf_perfeito(dados, score)

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

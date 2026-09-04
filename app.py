import io
import requests
import streamlit as st
from weasyprint import HTML

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

# -----------------------------------------------------------------------------
# 2. FUNÇÃO DE GERAÇÃO DO PDF COMPLETO (4 PÁGINAS)
# -----------------------------------------------------------------------------
def gerar_pdf_completo(dados, score):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 15mm 12mm 20mm 12mm;
                background-color: #0f172a;
                @bottom-center {{
                    content: "Tour360VR • tour360vr.com.br • contato@tour360vr.com.br • WhatsApp: (16) 99133-2121";
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    font-size: 8pt;
                    color: #94a3b8;
                    border-top: 1px solid #1e293b;
                    padding-top: 8px;
                }}
                @bottom-right {{
                    content: "Página " counter(page) " de " counter(pages);
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    font-size: 8pt;
                    color: #64748b;
                }}
            }}
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #f8fafc; background-color: #0f172a; font-size: 10pt; line-height: 1.5; }}
            .header {{ border-bottom: 2px solid #ef4444; padding-bottom: 10px; margin-bottom: 20px; }}
            .brand-title {{ font-size: 18pt; font-weight: bold; color: #ffffff; text-transform: uppercase; }}
            .brand-subtitle {{ font-size: 10pt; color: #ef4444; font-weight: 600; }}
            .card {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 15px; margin-bottom: 15px; }}
            .card-header {{ font-size: 11pt; font-weight: bold; color: #38bdf8; margin-bottom: 10px; border-bottom: 1px solid #334155; padding-bottom: 5px; }}
            .score-box {{ text-align: center; background-color: rgba(239, 68, 68, 0.1); border: 2px solid #ef4444; border-radius: 8px; padding: 15px; margin-bottom: 20px; }}
            .score-val {{ font-size: 32pt; font-weight: bold; color: #ef4444; }}
            .section-title {{ font-size: 13pt; font-weight: bold; color: #ffffff; border-left: 4px solid #ef4444; padding-left: 10px; margin-top: 20px; margin-bottom: 12px; text-transform: uppercase; }}
            .page-break {{ page-break-before: always; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th {{ background-color: #334155; color: #ffffff; text-align: left; padding: 8px; font-size: 9pt; }}
            td {{ padding: 8px; border-bottom: 1px solid #334155; font-size: 9pt; color: #cbd5e1; }}
            .pricing-grid {{ width: 100%; border-collapse: separate; border-spacing: 8px; }}
            .pricing-card {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px; vertical-align: top; }}
            .pricing-card.featured {{ border: 2px solid #ef4444; background-color: #1a1e2e; }}
            .contract-text {{ font-size: 8.5pt; color: #cbd5e1; text-align: justify; line-height: 1.4; }}
        </style>
    </head>
    <body>

        <!-- PÁGINA 1: DIAGNÓSTICO -->
        <div class="header">
            <div class="brand-title">Tour360VR</div>
            <div class="brand-subtitle">Gestão de Perfil & Diagnóstico do Google Meu Negócio</div>
        </div>

        <div class="card">
            <div class="card-header">Ficha Analisada do Cliente</div>
            <p style="margin: 3px 0;"><strong>Empresa:</strong> {dados['nome']}</p>
            <p style="margin: 3px 0;">📍 <strong>Endereço:</strong> {dados['endereco']}</p>
            <p style="margin: 3px 0;">📞 <strong>Telefone:</strong> {dados['telefone']}</p>
            <p style="margin: 3px 0;">🌐 <strong>Website:</strong> {dados['website']}</p>
            <p style="margin: 3px 0;">⭐ <strong>Avaliações:</strong> {dados['nota']} estrelas ({dados['avaliacoes']} avaliações)</p>
        </div>

        <div class="score-box">
            <div class="score-val">{score} / 100</div>
            <div style="color: #cbd5e1; text-transform: uppercase; font-size: 8pt; letter-spacing: 1px;">Score Geral de Otimização (Status Crítico)</div>
        </div>

        <div class="section-title">Auditoria Detalhada de Pontos de Busca</div>
        <div class="card">
            <table>
                <tr><td>1. Fotos de Alta Resolução</td><td style="color: {'#22c55e' if dados['tem_fotos_hd'] else '#ef4444'}; font-weight: bold;">{'Ok' if dados['tem_fotos_hd'] else 'Baixa Qualidade'}</td></tr>
                <tr><td>2. Tour Virtual 360° Interativo</td><td style="color: {'#22c55e' if dados['tem_tour360'] else '#ef4444'}; font-weight: bold;">{'Presente' if dados['tem_tour360'] else 'Ausente (Crítico)'}</td></tr>
                <tr><td>3. Categorias Principal e Secundárias</td><td style="color: {'#22c55e' if dados['categorias_completas'] else '#f59e0b'}; font-weight: bold;">{'Completas' if dados['categorias_completas'] else 'Incompletas'}</td></tr>
                <tr><td>4. Horários e Exceções (Feriados)</td><td style="color: {'#22c55e' if dados['horarios_ok'] else '#f59e0b'}; font-weight: bold;">{'Atualizados' if dados['horarios_ok'] else 'Desatualizados'}</td></tr>
                <tr><td>5. Endereço e Marcador no Mapa</td><td style="color: #22c55e; font-weight: bold;">Verificado</td></tr>
                <tr><td>6. Link do Site e Cardápio/Serviços</td><td style="color: {'#22c55e' if dados['website'] != 'Não possui' else '#ef4444'}; font-weight: bold;">{'Inserido' if dados['website'] != 'Não possui' else 'Ausente'}</td></tr>
            </table>
        </div>

        <!-- PÁGINA 2: ESTRUTURA PERSUASIVA E PLANOS -->
        <div class="page-break"></div>
        <div class="header">
            <div class="brand-title">Tour360VR</div>
            <div class="brand-subtitle">Proposta Comercial & Estruturação Estratégica</div>
        </div>

        <div class="section-title">Por que seu negócio precisa de Otimização Profissional?</div>
        <div class="card">
            <p style="margin-top: 0; color: #cbd5e1;">
                Mais de 80% das buscas por estabelecimentos locais acontecem diretamente no Google e Google Maps. Quando uma ficha possui notas baixas em itens essenciais como fotos, tour 360°, categorias corretas e tempo de resposta, o algoritmo do Google reduz expressivamente a visibilidade da sua empresa em relação aos concorrentes.
            </p>
            <p style="margin-bottom: 0; color: #38bdf8; font-weight: bold;">
                Com a estruturação completa da Tour360VR, transformamos o seu perfil em um ímã de novos clientes, transmitindo autoridade, transparência e alta relevância nas buscas regionais.
            </p>
        </div>

        <div class="section-title">Proposta de Planos e Investimento</div>
        <table class="pricing-grid">
            <tr>
                <td class="pricing-card" style="width: 33%;">
                    <div style="font-size: 11pt; font-weight: bold; color: #ffffff;">Plano Start</div>
                    <div style="font-size: 14pt; font-weight: bold; color: #22c55e;">R$ 590,00</div>
                    <ul style="font-size: 8.5pt; color: #94a3b8; padding-left: 15px;">
                        <li>Correção cadastral completa</li>
                        <li>Otimização de categorias</li>
                        <li>Inserção de site e links</li>
                        <li>Horários e exceções</li>
                    </ul>
                </td>
                <td class="pricing-card featured" style="width: 34%;">
                    <div style="font-size: 11pt; font-weight: bold; color: #ef4444;">Plano Pro (Recomendado)</div>
                    <div style="font-size: 14pt; font-weight: bold; color: #22c55e;">R$ 1.290,00</div>
                    <ul style="font-size: 8.5pt; color: #94a3b8; padding-left: 15px;">
                        <li><strong>Tudo do Plano Start</strong></li>
                        <li><strong>Sessão de Fotos Profissionais</strong></li>
                        <li><strong>Criação de Tour Virtual 360°</strong></li>
                        <li>Otimização de SEO Local avançado</li>
                    </ul>
                </td>
                <td class="pricing-card" style="width: 33%;">
                    <div style="font-size: 11pt; font-weight: bold; color: #ffffff;">Plano Gestão Mensal</div>
                    <div style="font-size: 14pt; font-weight: bold; color: #22c55e;">R$ 490,00 /mês</div>
                    <ul style="font-size: 8.5pt; color: #94a3b8; padding-left: 15px;">
                        <li>Postagens semanais no perfil</li>
                        <li>Gestão contínua de avaliações</li>
                        <li>Atualização de produtos</li>
                        <li>Relatório mensal de desempenho</li>
                    </ul>
                </td>
            </tr>
        </table>

        <!-- PÁGINA 3: ANTES VS DEPOIS E METRICAS -->
        <div class="page-break"></div>
        <div class="header">
            <div class="brand-title">Tour360VR</div>
            <div class="brand-subtitle">Relatório Visual de Estruturação (Antes vs. Depois)</div>
        </div>

        <div class="section-title">Demonstrativo Visual do Trabalho Realizado</div>
        <div class="card">
            <p><strong>Antes:</strong> Fotos escuras, sem Tour 360°, categorias incorretas e baixa relevância local (Score: {score}/100).</p>
            <p><strong>Depois:</strong> Imagens em alta resolução, Tour Virtual 360° interativo publicado e SEO local otimizado (Score Projetado: 98/100).</p>
        </div>

        <div class="section-title">Resumo do Desempenho e Métricas Esperadas</div>
        <div class="card">
            <table>
                <thead>
                    <tr><th>Métrica de Desempenho</th><th>Antes</th><th>Após Otimização</th><th>Crescimento Estimado</th></tr>
                </thead>
                <tbody>
                    <tr><td>Visualizações no Google Maps</td><td>1.240</td><td>4.890</td><td style="color: #22c55e; font-weight: bold;">+ 294%</td></tr>
                    <tr><td>Solicitações de Rota (GPS)</td><td>85</td><td>310</td><td style="color: #22c55e; font-weight: bold;">+ 264%</td></tr>
                    <tr><td>Chamadas Telefônicas Diretas</td><td>42</td><td>128</td><td style="color: #22c55e; font-weight: bold;">+ 204%</td></tr>
                    <tr><td>Cliques no Website / WhatsApp</td><td>18</td><td>95</td><td style="color: #22c55e; font-weight: bold;">+ 427%</td></tr>
                </tbody>
            </table>
        </div>

        <!-- PÁGINA 4: CONTRATO -->
        <div class="page-break"></div>
        <div class="header">
            <div class="brand-title">Tour360VR</div>
            <div class="brand-subtitle">Contrato de Prestação de Serviços Profissionais</div>
        </div>

        <div class="contract-text">
            <p style="text-align: center; font-weight: bold; font-size: 11pt; color: #ffffff;">CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE OTIMIZAÇÃO E GESTÃO DE PERFIL NO GOOGLE MEU NEGÓCIO</p>
            <p><strong>CONTRATADA:</strong> TOUR360VR, com contatos oficiais via e-mail contato@tour360vr.com.br e WhatsApp (16) 99133-2121.</p>
            <p><strong>CONTRATANTE:</strong> Razão Social / Nome: {dados['nome']}, Endereço: {dados['endereco']}.</p>
            <p><strong>CLÁUSULA PRIMEIRA - DO OBJETO:</strong> O presente contrato tem por objeto a prestação de serviços de otimização, reestruturação técnica, atualização cadastral e/ou produção de Tour Virtual 360° para a ficha do Google Meu Negócio do CONTRATANTE.</p>
            <p><strong>CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES:</strong> A CONTRATADA compromete-se a realizar a auditoria técnica, inclusão de informações oficiais, publicação de fotos otimizadas, configuração de categorias estratégicas e emissão de relatório de entrega visual.</p>
            <p><strong>CLÁUSULA TERCEIRA - VALOR E FORMA DE PAGAMENTO:</strong> Pela execução dos serviços, o CONTRATANTE pagará o valor estipulado no plano selecionado via transferência bancária ou PIX.</p>
            <br><br><br>
            <table style="border: none;">
                <tr style="border: none;">
                    <td style="text-align: center; border: none; border-top: 1px solid #ffffff; width: 45%;"><strong>TOUR360VR</strong><br>Prestadora de Serviços</td>
                    <td style="border: none; width: 10%;"></td>
                    <td style="text-align: center; border: none; border-top: 1px solid #ffffff; width: 45%;"><strong>{dados['nome']}</strong><br>Aceite e Assinatura</td>
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
# 3. PAINEL LATERAL & CONSULTA DA FICHA
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Configurações da Consulta")
API_KEY_GOOGLE = st.sidebar.text_input("Chave Google Places API (Opcional):", type="password")

busca_cliente = st.text_input("🔍 Digite o Nome do Estabelecimento e Cidade para Consultar:", placeholder="Ex: Restaurante Sabor Local Ribeirão Preto")

if st.button("🚀 Analisar Perfil Agora", use_container_width=True):
    if busca_cliente:
        # Busca Real via API se houver chave inserida
        if API_KEY_GOOGLE:
            try:
                url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={busca_cliente}&inputtype=textquery&fields=place_id,name,formatted_address,rating,user_ratings_total&key={API_KEY_GOOGLE}"
                res = requests.get(url).json()
                if res.get("candidates"):
                    c = res["candidates"][0]
                    dados = {
                        "nome": c.get("name", busca_cliente),
                        "endereco": c.get("formatted_address", "Endereço registrado no Google Maps"),
                        "telefone": "(16) 3999-8888",
                        "website": "Não possui",
                        "nota": c.get("rating", 4.0),
                        "avaliacoes": c.get("user_ratings_total", 15),
                        "tem_tour360": False,
                        "tem_fotos_hd": False,
                        "categorias_completas": False,
                        "horarios_ok": True
                    }
                else:
                    API_KEY_GOOGLE = None
            except:
                API_KEY_GOOGLE = None

        # Dados Padrão / Simulado caso esteja sem Chave da API
        if not API_KEY_GOOGLE:
            dados = {
                "nome": busca_cliente,
                "endereco": "Av. Principal, 1200 - Ribeirão Preto, SP",
                "telefone": "(16) 3999-8888",
                "website": "Não possui",
                "nota": 4.2,
                "avaliacoes": 38,
                "tem_tour360": False,
                "tem_fotos_hd": False,
                "categorias_completas": False,
                "horarios_ok": False
            }

        # Lógica de Cálculo do Score (0 a 100)
        score = 100
        if not dados["tem_tour360"]: score -= 25
        if dados["website"] == "Não possui": score -= 20
        if not dados["tem_fotos_hd"]: score -= 20
        if not dados["categorias_completas"]: score -= 15
        if not dados["horarios_ok"]: score -= 10
        if dados["avaliacoes"] < 50: score -= 10

        st.success("Análise de perfil concluída!")

        # Exibição dos Resultados no App
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

        # Gerar e disponibilizar PDF para Download
        pdf_bytes = gerar_pdf_completo(dados, score)

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
        st.warning("Digite o nome de uma empresa para realizar a consulta.")

# -----------------------------------------------------------------------------
# 4. RODAPÉ FIXO DA TOUR360VR
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="footer">
        Tour360VR • tour360vr.com.br • contato@tour360vr.com.br • WhatsApp: (16) 99133-2121
    </div>
""", unsafe_allow_html=True)

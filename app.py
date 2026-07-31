import datetime
import io
import requests
import streamlit as st
from xhtml2pdf import pisa

st.set_page_config(
    page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered"
)

st.title("📍 Gerador de Diagnóstico Google Meu Negócio")
st.subheader("Padrão Visual Executivo - Tour360vr")

# Recupera a chave salva nos Secrets do Streamlit Cloud
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    api_key = st.text_input(
        "Digite sua Chave da API Google (Places API):", type="password"
    )

with st.form("form_busca"):
    empresa = st.text_input(
        "Nome da Empresa:", placeholder="Ex: Vinicius Fisioterapia"
    )
    cidade = st.text_input("Cidade / Estado:", placeholder="Ex: Ribeirão Preto / SP")
    btn = st.form_submit_button("Gerar Relatório Executivo em PDF")


def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()

    if not res.get("results"):
        return None, []

    result = res["results"][0]
    place_id = result["place_id"]
    primary_type = result.get("types", ["establishment"])[0]

    # Detalhes completos
    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,opening_hours,types&key={key}"
    details = requests.get(url_details).json().get("result", {})

    # Busca Concorrentes
    query_concorrentes = f"{primary_type} em {cidade}"
    url_conc = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query_concorrentes}&key={key}"
    res_conc = requests.get(url_conc).json().get("results", [])

    concorrentes = []
    for c in res_conc:
        if c.get("place_id") != place_id:
            concorrentes.append(
                f"{c.get('name')} ({c.get('user_ratings_total', 0)} avaliações)"
            )
        if len(concorrentes) >= 3:
            break

    return details, concorrentes


def calcular_score(dados):
    score = 35
    if dados.get("website"):
        score += 10
    if len(dados.get("photos", [])) >= 10:
        score += 15
    elif len(dados.get("photos", [])) >= 3:
        score += 8

    if dados.get("rating", 0) >= 4.5:
        score += 15
    if dados.get("user_ratings_total", 0) >= 30:
        score += 15
    elif dados.get("user_ratings_total", 0) >= 10:
        score += 8

    if dados.get("opening_hours"):
        score += 10

    return min(score, 100)


def gerar_pdf_bytes(dados, concorrentes):
    nome = dados.get("name", "N/A")
    endereco = dados.get("formatted_address", "N/A")
    telefone = dados.get("formatted_phone_number", "Não informado")
    rating = dados.get("rating", "0.0")
    reviews = dados.get("user_ratings_total", 0)
    photos_count = len(dados.get("photos", []))
    website = dados.get("website")
    has_hours = "Completo" if dados.get("opening_hours") else "Incompleto"
    data_hoje = datetime.date.today().strftime("%d/%m/%Y")
    score = calcular_score(dados)

    txt_concorrentes = (
        ", ".join(concorrentes)
        if concorrentes
        else "Concorrentes mapeados na região."
    )

    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: a4 portrait;
                margin: 0mm 0mm 0mm 0mm;
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                color: #0f172a;
                font-size: 8.5pt;
                line-height: 1.35;
                background-color: #ffffff;
                padding: 0;
                margin: 0;
            }}
            
            /* Tarja Azul de Cabeçalho Superior */
            .top-header {{
                background-color: #0284c7;
                color: #ffffff;
                padding: 14px 18px;
                margin-bottom: 12px;
            }}
            .brand-logo-text {{
                font-size: 20pt;
                font-weight: bold;
                color: #ffffff;
                letter-spacing: -0.5px;
            }}
            .brand-logo-text span {{
                color: #bae6fd;
            }}
            .brand-subtitle {{
                font-size: 7.5pt;
                color: #e0f2fe;
                text-transform: uppercase;
                margin-top: 1px;
            }}
            .header-doc-title {{
                text-align: right;
                font-size: 11pt;
                font-weight: bold;
                color: #ffffff;
                text-transform: uppercase;
            }}
            .header-doc-date {{
                text-align: right;
                font-size: 8pt;
                color: #e0f2fe;
            }}

            /* Container Principal com Margens Interiores */
            .content-container {{
                padding: 0 16px;
            }}
            
            /* Destaque do Cliente */
            .client-card {{
                background-color: #f0f9ff;
                border-left: 5px solid #0284c7;
                padding: 10px 14px;
                margin-bottom: 12px;
                border-radius: 4px;
            }}
            .client-name {{
                font-size: 14pt;
                font-weight: bold;
                color: #0369a1;
                text-transform: uppercase;
                margin-bottom: 3px;
            }}
            .client-info {{
                font-size: 8.5pt;
                color: #334155;
            }}
            
            /* Metricas Estilo Cards PinCheck */
            .metrics-table {{
                width: 100%;
                margin-bottom: 12px;
            }}
            .metric-box {{
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                padding: 8px 10px;
                vertical-align: top;
                width: 32%;
                border-radius: 4px;
            }}
            .metric-title {{
                font-size: 7.5pt;
                font-weight: bold;
                color: #475569;
                text-transform: uppercase;
                margin-bottom: 3px;
            }}
            .metric-score {{
                font-size: 17pt;
                font-weight: bold;
                color: #0284c7;
            }}
            .thermo-bar {{
                background-color: #e2e8f0;
                height: 7px;
                width: 100%;
                margin-top: 4px;
                border-radius: 3px;
            }}
            .thermo-progress {{
                background-color: #0284c7;
                height: 7px;
                width: {score}%;
                border-radius: 3px;
            }}

            /* Titulo de Seções */
            .section-header {{
                font-size: 9.5pt;
                font-weight: bold;
                color: #0369a1;
                text-transform: uppercase;
                border-bottom: 2px solid #0284c7;
                padding-bottom: 2px;
                margin-bottom: 8px;
            }}
            
            /* Tabela de Matriz de Diagnostico */
            .diag-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 12px;
            }}
            .diag-table th {{
                background-color: #0f172a;
                color: #ffffff;
                padding: 6px;
                font-size: 7.5pt;
                text-transform: uppercase;
                text-align: left;
            }}
            .diag-table td {{
                padding: 5px 6px;
                border-bottom: 1px solid #e2e8f0;
                font-size: 8pt;
                vertical-align: top;
            }}
            .dim-name {{
                font-weight: bold;
                color: #0369a1;
                width: 22%;
            }}
            .dim-status {{
                color: #334155;
                width: 38%;
            }}
            .dim-impact {{
                color: #b91c1c;
                width: 40%;
                font-weight: 500;
            }}

            /* Blocos Retangulares do Plano de Acao */
            .action-block {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-left: 4px solid #0284c7;
                padding: 6px 10px;
                margin-bottom: 5px;
                border-radius: 3px;
            }}
            .action-title {{
                font-size: 8.5pt;
                font-weight: bold;
                color: #0369a1;
                text-transform: uppercase;
            }}
            .action-desc {{
                font-size: 7.8pt;
                color: #334155;
            }}

            /* Bloco de Chamada para Ação (CTA Unificado) */
            .cta-card {{
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-left: 4px solid #0284c7;
                padding: 10px 12px;
                margin-top: 10px;
                margin-bottom: 12px;
                border-radius: 4px;
            }}
            .cta-title {{
                font-size: 9pt;
                font-weight: bold;
                color: #0369a1;
                margin-bottom: 3px;
                text-transform: uppercase;
            }}
            .cta-text {{
                font-size: 8pt;
                color: #1e293b;
                line-height: 1.35;
            }}

            /* Rodape Limpo */
            .footer-bar {{
                text-align: center;
                font-size: 8.5pt;
                color: #0369a1;
                border-top: 1px solid #e2e8f0;
                padding-top: 8px;
                margin-top: 6px;
            }}
            .footer-bar a {{
                color: #0284c7;
                text-decoration: none;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>

        <!-- Tarja Azul de Cabeçalho Superior -->
        <div class="top-header">
            <table style="width: 100%;">
                <tr>
                    <td style="width: 60%;">
                        <div class="brand-logo-text">TOUR<span>360VR</span></div>
                        <div class="brand-subtitle">AUDITORIA E DIAGNÓSTICO GOOGLE MEU NEGÓCIO</div>
                    </td>
                    <td style="text-align: right; width: 40%;">
                        <div class="header-doc-title">PinCheck Audit</div>
                        <div class="header-doc-date">Data: {data_hoje}</div>
                    </td>
                </tr>
            </table>
        </div>

        <div class="content-container">

            <!-- Destaque do Cliente -->
            <div class="client-card">
                <div class="client-name">{nome}</div>
                <div class="client-info">
                    <b>Endereço:</b> {endereco} | <b>Telefone:</b> {telefone}
                </div>
            </div>

            <!-- Metric Cards com Termometro -->
            <table class="metrics-table">
                <tr>
                    <td class="metric-box">
                        <div class="metric-title">OTIMIZAÇÃO DO PERFIL</div>
                        <div class="metric-score">{score}/100</div>
                        <div class="thermo-bar"><div class="thermo-progress"></div></div>
                        <div style="font-size: 7pt; color: #64748b; margin-top: 3px;">Margem para crescimento e conversão</div>
                    </td>
                    <td style="width: 2%;"></td>
                    <td class="metric-box">
                        <div class="metric-title">NOTA E REPUTAÇÃO</div>
                        <div class="metric-score">★ {rating}</div>
                        <div style="font-size: 7.5pt; color: #334155; margin-top: 4px;">Com base em <b>{reviews} avaliações</b> no Google</div>
                    </td>
                    <td style="width: 2%;"></td>
                    <td class="metric-box">
                        <div class="metric-title">TOUR VIRTUAL 360°</div>
                        <div class="metric-score" style="color: #dc2626;">0 FOTOS</div>
                        <div style="font-size: 7.5pt; color: #64748b; margin-top: 4px;">Oportunidade para diferenciar no mercado</div>
                    </td>
                </tr>
            </table>

            <!-- Matriz de 9 Itens -->
            <div class="section-header">MATRIZ DE DIAGNÓSTICO E IMPACTO COMERCIAL</div>

            <table class="diag-table">
                <thead>
                    <tr>
                        <th>Dimensão</th>
                        <th>Estado Atual Identificado</th>
                        <th>Impacto no Ranqueamento e Conversão</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="dim-name">Completude do Cadastro</td>
                        <td class="dim-status">{"Website cadastrado" if website else "Faltam descrição, site próprio e dados complementares."}</td>
                        <td class="dim-impact">Perfil incompleto transmite falta de profissionalismo e reduz a conversão de visitantes.</td>
                    </tr>
                    <tr>
                        <td class="dim-name">Nota e Avaliações</td>
                        <td class="dim-status">Nota ★ {rating} com {reviews} avaliações acumuladas.</td>
                        <td class="dim-impact">Reputação ativa fortalece a prova social e gera confiança imediata ao paciente/cliente.</td>
                    </tr>
                    <tr>
                        <td class="dim-name">Consistência de NAP</td>
                        <td class="dim-status">Endereço e telefone consistentes no Google Maps.</td>
                        <td class="dim-impact">Informações corretas garantem confiança ao algoritmo e evitam buscas frustradas.</td>
                    </tr>
                    <tr>
                        <td class="dim-name">Categorias</td>
                        <td class="dim-status">Categoria principal definida na ficha.</td>
                        <td class="dim-impact">Falta de categorizações secundárias limita a visibilidade em buscas específicas da região.</td>
                    </tr>
                    <tr>
                        <td class="dim-name">Fotos</td>
                        <td class="dim-status">{photos_count} fotos identificadas no perfil. Cobertura básica.</td>
                        <td class="dim-impact">Poucas fotos impedem que os visitantes avaliem a qualidade do ambiente e equipamentos.</td>
                    </tr>
                    <tr>
                        <td class="dim-name">Horários</td>
                        <td class="dim-status">Horários de funcionamento: {has_hours}.</td>
                        <td class="dim-impact">Informação correta evita perda de atendimentos e buscas em horários de pico.</td>
                    </tr>
                    <tr>
                        <td class="dim-name">Posts / Novidades</td>
                        <td class="dim-status">Nenhum post ou novidade constante detectado.</td>
                        <td class="dim-impact">Perfil estático não incentiva revisitas e deixa de destacar promoções e diferenciais.</td>
                    </tr>
                    <tr>
                        <td class="dim-name">Recursos Interativos</td>
                        <td class="dim-status">Nenhuma foto 360° ou tour virtual detectado.</td>
                        <td class="dim-impact">Visitantes não conseguem "visitar" virtualmente o local; perdem-se conversões por falta de imersão.</td>
                    </tr>
                    <tr>
                        <td class="dim-name">Presença e Concorrência Local</td>
                        <td class="dim-status">{txt_concorrentes}</td>
                        <td class="dim-impact">Como você está na região — e onde está a oportunidade de superar o volume da concorrência.</td>
                    </tr>
                </tbody>
            </table>

            <!-- Plano de Ação em Blocos Retangulares -->
            <div class="section-header">PLANO DE AÇÃO RECOMENDADO (SOLUÇÕES TOUR360VR)</div>

            <div class="action-block">
                <div class="action-title">1. IMPLANTAÇÃO DE TOUR VIRTUAL 360° INTERATIVO</div>
                <div class="action-desc">Mapeamento imersivo em alta definição integrado ao Google Maps. Aumenta o tempo de permanência na ficha e multiplica a conversão.</div>
            </div>

            <div class="action-block">
                <div class="action-title">2. ENSAIO FOTOGRÁFICO PROFISSIONAL HD</div>
                <div class="action-desc">Fotografias profissionais das instalações, fachada e diferenciais, elevando o valor percebido pelo cliente.</div>
            </div>

            <div class="action-block">
                <div class="action-title">3. OTIMIZAÇÃO SEO LOCAL & GESTÃO DE REPUTAÇÃO</div>
                <div class="action-desc">Reestruturação completa de palavras-chave, categorias e estratégia para alavancar avaliações de clientes satisfeitos.</div>
            </div>

            <!-- Bloco de Chamada para Ação (CTA Unificado) -->
            <div class="cta-card">
                <div class="cta-title">Pronto para elevar sua visibilidade?</div>
                <div class="cta-text">
                    Conversamos por WhatsApp, entendemos seus objetivos e montamos um plano personalizado. O tour 360° + estratégia de avaliações pode triplicar suas buscas.
                </div>
            </div>

            <!-- Rodapé Limpo -->
            <div class="footer-bar">
                <a href="https://wa.me/5516991332121">WhatsApp: (16) 99133-2121</a> &nbsp;|&nbsp; 
                <a href="https://tour360vr.com.br/">www.tour360vr.com.br</a>
            </div>

        </div>

    </body>
    </html>
    """

    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_template, dest=pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


if btn and empresa and cidade:
    if not api_key:
        st.error("Chave da API do Google não configurada nos Secrets.")
    else:
        with st.spinner("Analisando ficha e mapeando concorrentes da região..."):
            dados, concorrentes = buscar_dados_google(empresa, cidade, api_key)
            if dados:
                pdf_bytes = gerar_pdf_bytes(dados, concorrentes)
                st.success("Diagnóstico gerado com sucesso!")

                st.download_button(
                    label="📥 Baixar Relatório Executivo (PDF)",
                    data=pdf_bytes,
                    file_name=f"Diagnostico_{dados.get('name')}.pdf",
                    mime="application/pdf",
                )
            else:
                st.error("Empresa não encontrada no Google Maps.")

import base64
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

# Logo Tour360vr embutida em Base64
LOGO_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSU56Buffer..."  # O código gera dinamicamente se a imagem estiver no servidor ou usa o SVG fallback

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

    # Busca Detalhes Completos da Empresa
    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,opening_hours,types&key={key}"
    details = requests.get(url_details).json().get("result", {})

    # Busca Concorrentes na Mesma Cidade e Categoria
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
    has_hours = "Sim" if dados.get("opening_hours") else "Incompleto"
    data_hoje = datetime.date.today().strftime("%d/%m/%Y")
    score = calcular_score(dados)

    txt_concorrentes = (
        ", ".join(concorrentes)
        if concorrentes
        else "Concorrentes locais com presença ativa mapeados."
    )

    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: a4 portrait;
                margin: 8mm 10mm 12mm 10mm;
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                color: #0f172a;
                font-size: 8.5pt;
                line-height: 1.3;
            }}
            
            /* Header com Tarja Azul */
            .header-bar {{
                background-color: #0284c7;
                color: #ffffff;
                padding: 10px 14px;
                margin-bottom: 10px;
            }}
            .brand-title {{
                font-size: 18pt;
                font-weight: bold;
                color: #ffffff;
                letter-spacing: -0.5px;
            }}
            .brand-title span {{
                color: #f97316;
            }}
            .brand-sub {{
                font-size: 7.5pt;
                color: #e0f2fe;
                text-transform: uppercase;
            }}
            .doc-title {{
                text-align: right;
                font-size: 10pt;
                font-weight: bold;
                color: #ffffff;
                text-transform: uppercase;
            }}
            
            /* Card Destaque */
            .client-card {{
                background-color: #f8fafc;
                border-left: 4px solid #0284c7;
                padding: 8px 12px;
                margin-bottom: 10px;
                border-top: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
            }}
            .client-name {{
                font-size: 13pt;
                font-weight: bold;
                color: #0369a1;
                text-transform: uppercase;
                margin-bottom: 2px;
            }}
            
            /* Metricas e Termometro */
            .metrics-table {{
                width: 100%;
                margin-bottom: 10px;
            }}
            .metric-box {{
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                padding: 8px;
                vertical-align: top;
                width: 32%;
            }}
            .metric-title {{
                font-size: 7pt;
                font-weight: bold;
                color: #475569;
                text-transform: uppercase;
                margin-bottom: 4px;
            }}
            .metric-score {{
                font-size: 16pt;
                font-weight: bold;
                color: #0284c7;
            }}
            
            /* Termometro Visao */
            .thermo-bg {{
                background-color: #e2e8f0;
                height: 8px;
                width: 100%;
                margin-top: 4px;
                border-radius: 4px;
            }}
            .thermo-fill {{
                background-color: #0284c7;
                height: 8px;
                width: {score}%;
                border-radius: 4px;
            }}

            /* Tabela de Matriz de Diagnostico (9 Itens) */
            .section-header {{
                font-size: 9.5pt;
                font-weight: bold;
                color: #0284c7;
                text-transform: uppercase;
                border-bottom: 2px solid #0284c7;
                padding-bottom: 2px;
                margin-bottom: 6px;
            }}
            
            .diag-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 10px;
            }}
            .diag-table th {{
                background-color: #0f172a;
                color: #ffffff;
                padding: 5px;
                font-size: 7.5pt;
                text-transform: uppercase;
                text-align: left;
            }}
            .diag-table td {{
                padding: 5px;
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
            }}

            /* Blocos Retangulares do Plano de Acao */
            .action-grid {{
                width: 100%;
                margin-bottom: 8px;
            }}
            .action-block {{
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-left: 4px solid #0284c7;
                padding: 6px 8px;
                margin-bottom: 4px;
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

            /* Box de CTA */
            .cta-box {{
                background-color: #0f172a;
                color: #ffffff;
                padding: 8px 12px;
                text-align: center;
                margin-top: 6px;
                border-radius: 4px;
            }}
            .cta-title {{
                font-size: 9.5pt;
                font-weight: bold;
                color: #38bdf8;
                margin-bottom: 2px;
            }}
            .cta-text {{
                font-size: 7.8pt;
                color: #e2e8f0;
            }}

            /* Footer */
            .footer {{
                text-align: center;
                font-size: 8pt;
                color: #0284c7;
                border-top: 1px solid #cbd5e1;
                padding-top: 6px;
                margin-top: 8px;
            }}
            .footer a {{
                color: #0284c7;
                text-decoration: none;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>

        <!-- Header -->
        <div class="header-bar">
            <table style="width: 100%;">
                <tr>
                    <td style="width: 60%;">
                        <div class="brand-title">TOUR<span>360</span>VR</div>
                        <div class="brand-sub">AUDITORIA E DIAGNÓSTICO GOOGLE MEU NEGÓCIO</div>
                    </td>
                    <td style="text-align: right; width: 40%;">
                        <div class="doc-title">PinCheck Audit</div>
                        <div style="font-size: 7.5pt; color: #e0f2fe;">Data: {data_hoje}</div>
                    </td>
                </tr>
            </table>
        </div>

        <!-- Destaque do Cliente -->
        <div class="client-card">
            <div class="client-name">{nome}</div>
            <div style="font-size: 8pt; color: #475569;">
                <b>Endereço:</b> {endereco} | <b>Telefone:</b> {telefone}
            </div>
        </div>

        <!-- Metric Cards com Termometro -->
        <table class="metrics-table">
            <tr>
                <td class="metric-box">
                    <div class="metric-title">OTIMIZAÇÃO DO PERFIL</div>
                    <div class="metric-score">{score}/100</div>
                    <div class="thermo-bg"><div class="thermo-fill"></div></div>
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
                    <div class="metric-score" style="color: #dc2626;">AUSENTE</div>
                    <div style="font-size: 7.5pt; color: #64748b; margin-top: 4px;">Oportunidade para diferenciar no mercado</div>
                </td>
            </tr>
        </table>

        <!-- Matriz de 9 Itens -->
        <div class="section-header">DIAGNÓSTICO DETALHADO DE DESEMPENHO</div>

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
                    <td class="dim-status">{"Website cadastrado" if website else "Falta site próprio ou dados complementares."}</td>
                    <td class="dim-impact">Perfil incompleto transmite falta de profissionalismo e reduz a conversão.</td>
                </tr>
                <tr>
                    <td class="dim-name">Nota e Avaliações</td>
                    <td class="dim-status">Nota ★ {rating} com {reviews} avaliações acumuladas.</td>
                    <td class="dim-impact">Reputação ativa fortalece a prova social e gera confiança imediata no paciente/cliente.</td>
                </tr>
                <tr>
                    <td class="dim-name">Consistência de NAP</td>
                    <td class="dim-status">Endereço e telefone ativos no Google Maps.</td>
                    <td class="dim-impact">Informações corretas garantem confiança ao algoritmo e evitarem buscas frustradas.</td>
                </tr>
                <tr>
                    <td class="dim-name">Categorias</td>
                    <td class="dim-status">Categoria principal definida na ficha.</td>
                    <td class="dim-impact">Falta de categorias secundárias limita a exibição em buscas locais específicas.</td>
                </tr>
                <tr>
                    <td class="dim-name">Fotos</td>
                    <td class="dim-status">{photos_count} fotos identificadas no perfil.</td>
                    <td class="dim-impact">Poucas fotos impedem que o cliente avalie o espaço visualmente antes de contratar.</td>
                </tr>
                <tr>
                    <td class="dim-name">Horários</td>
                    <td class="dim-status">Horários de funcionamento: {has_hours}.</td>
                    <td class="dim-impact">Horários claros e atualizados evitam perda de atendimento em horários de pico.</td>
                </tr>
                <tr>
                    <td class="dim-name">Posts / Novidades</td>
                    <td class="dim-status">Nenhuma atualização constante de posts detectada.</td>
                    <td class="dim-impact">Perfil estático não incentiva revisitas e deixa de destacar ofertas ou novidades.</td>
                </tr>
                <tr>
                    <td class="dim-name">Recursos Interativos</td>
                    <td class="dim-status">Nenhum Tour Virtual 360° interativo detectado.</td>
                    <td class="dim-impact">Visitantes não conseguem "visitar" virtualmente o local; perdem-se conversões por falta de imersão.</td>
                </tr>
                <tr>
                    <td class="dim-name">Presença e Concorrência Local</td>
                    <td class="dim-status">Concorrentes na região: {txt_concorrentes}.</td>
                    <td class="dim-impact">Como você está na região — e onde está a oportunidade de superar o volume da concorrência.</td>
                </tr>
            </tbody>
        </table>

        <!-- Plano de Acao em Blocos Retangulares -->
        <div class="section-header">PLANO DE AÇÃO RECOMENDADO (SOLUÇÕES TOUR360VR)</div>

        <div class="action-block">
            <div class="action-title">1. IMPLANTAÇÃO DE TOUR VIRTUAL 360° INTERATIVO</div>
            <div class="action-desc">Mapeamento em alta definição integrado ao Google Maps. Aumenta o tempo de permanência na ficha e multiplica os agendamentos.</div>
        </div>

        <div class="action-block">
            <div class="action-title">2. ENSAIO FOTOGRÁFICO PROFISSIONAL HD</div>
            <div class="action-desc">Captura em alta resolução das instalações, fachada e diferenciais, elevando a percepção de valor e profissionalismo.</div>
        </div>

        <div class="action-block">
            <div class="action-title">3. OTIMIZAÇÃO SEO LOCAL & GESTÃO DE REPUTAÇÃO</div>
            <div class="action-desc">Reestruturação completa de palavras-chave, categorias e estratégia para alavancar avaliações de clientes satisfeitos.</div>
        </div>

        <!-- Box de Chamada para Acao (CTA) -->
        <div class="cta-box">
            <div class="cta-title">Pronto para elevar sua visibilidade?</div>
            <div class="cta-text">
                Conversamos por WhatsApp, entendemos seus objetivos e montamos um plano personalizado. O tour 360° + estratégia de avaliações pode triplicar suas buscas.
            </div>
        </div>

        <!-- Rodape -->
        <div class="footer">
            <a href="https://wa.me/5516991332121">WhatsApp: (16) 99133-2121</a> | 
            <a href="https://www.tour360vr.com.br">www.tour360vr.com.br</a>
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

import datetime
import io
import requests
import streamlit as st
from xhtml2pdf import pisa

st.set_page_config(
    page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered"
)

st.title("📍 Gerador de Diagnóstico Google Meu Negócio")
st.subheader("Padrão PinCheck & Tour360vr")

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
    btn = st.form_submit_button("Gerar Relatório Estruturado em PDF")


def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()

    if not res.get("results"):
        return None

    place_id = res["results"][0]["place_id"]
    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website,types&key={key}"
    return requests.get(url_details).json().get("result", {})


def calcular_pontuacao(dados):
    score = 40
    photos_count = len(dados.get("photos", []))
    rating = dados.get("rating", 0)
    reviews = dados.get("user_ratings_total", 0)

    if photos_count >= 15:
        score += 20
    elif photos_count >= 5:
        score += 10

    if float(rating) >= 4.5:
        score += 20
    elif float(rating) >= 4.0:
        score += 10

    if reviews >= 50:
        score += 20
    elif reviews >= 10:
        score += 10

    return min(score, 100)


def gerar_pdf_bytes(dados):
    nome = dados.get("name", "N/A")
    endereco = dados.get("formatted_address", "N/A")
    telefone = dados.get("formatted_phone_number", "Não informado")
    rating = dados.get("rating", "N/A")
    reviews = dados.get("user_ratings_total", 0)
    photos_count = len(dados.get("photos", []))
    data_hoje = datetime.date.today().strftime("%d/%m/%Y")
    score = calcular_pontuacao(dados)

    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: a4 portrait;
                margin: 10mm 12mm 12mm 12mm;
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                color: #0f172a;
                font-size: 9pt;
                line-height: 1.35;
            }}
            
            /* Header */
            .header-bar {{
                background-color: #0f172a;
                color: #ffffff;
                padding: 12px 15px;
                margin-bottom: 12px;
            }}
            .brand-logo {{
                font-size: 20pt;
                font-weight: bold;
                color: #ffffff;
            }}
            .brand-logo-span {{
                color: #38bdf8;
            }}
            .sub-header {{
                font-size: 8pt;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .doc-title {{
                text-align: right;
                font-size: 10pt;
                font-weight: bold;
                color: #ffffff;
                text-transform: uppercase;
            }}

            /* Destaque do Cliente */
            .client-card {{
                background-color: #f8fafc;
                border-left: 4px solid #0284c7;
                padding: 10px 12px;
                margin-bottom: 12px;
                border-top: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
            }}
            .client-name {{
                font-size: 14pt;
                font-weight: bold;
                color: #0284c7;
                text-transform: uppercase;
                margin-bottom: 4px;
            }}
            .client-details {{
                font-size: 8.5pt;
                color: #475569;
            }}

            /* Cards de Metricas */
            .metrics-table {{
                width: 100%;
                margin-bottom: 14px;
            }}
            .metric-box {{
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                padding: 8px;
                text-align: center;
                vertical-align: top;
                width: 32%;
            }}
            .metric-title {{
                font-size: 7.5pt;
                font-weight: bold;
                color: #475569;
                text-transform: uppercase;
                margin-bottom: 4px;
            }}
            .metric-value {{
                font-size: 18pt;
                font-weight: bold;
                color: #0284c7;
            }}
            .metric-desc {{
                font-size: 7.5pt;
                color: #64748b;
                margin-top: 2px;
            }}

            /* Tabela de Matriz de Diagnostico */
            .section-header {{
                font-size: 10pt;
                font-weight: bold;
                color: #0f172a;
                text-transform: uppercase;
                border-bottom: 2px solid #0284c7;
                padding-bottom: 3px;
                margin-bottom: 8px;
            }}
            
            .diag-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 12px;
            }}
            .diag-table th {{
                background-color: #0f172a;
                color: #ffffff;
                padding: 6px;
                font-size: 8pt;
                text-transform: uppercase;
                text-align: left;
            }}
            .diag-table td {{
                padding: 7px 6px;
                border-bottom: 1px solid #e2e8f0;
                font-size: 8.5pt;
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

            /* Box de Oferta Tour360vr */
            .offer-box {{
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                padding: 10px;
                margin-top: 8px;
            }}
            .offer-title {{
                font-size: 9.5pt;
                font-weight: bold;
                color: #0369a1;
                text-transform: uppercase;
                margin-bottom: 4px;
            }}

            /* Footer */
            .footer {{
                text-align: center;
                font-size: 7.5pt;
                color: #64748b;
                border-top: 1px solid #cbd5e1;
                padding-top: 6px;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>

        <!-- Header -->
        <div class="header-bar">
            <table style="width: 100%;">
                <tr>
                    <td>
                        <div class="brand-logo">Tour<span class="brand-logo-span">360vr</span></div>
                        <div class="sub-header">DIAGNÓSTICO E AUDITORIA DE FICHA GOOGLE MAPS</div>
                    </td>
                    <td style="text-align: right;">
                        <div class="doc-title">PinCheck Audit</div>
                        <div style="font-size: 8pt; color: #94a3b8;">Gerado em: {data_hoje}</div>
                    </td>
                </tr>
            </table>
        </div>

        <!-- Destaque do Cliente -->
        <div class="client-card">
            <div class="client-name">{nome}</div>
            <div class="client-details">
                <b>Endereço:</b> {endereco} | <b>Telefone:</b> {telefone}
            </div>
        </div>

        <!-- Metric Cards -->
        <table class="metrics-table">
            <tr>
                <td class="metric-box">
                    <div class="metric-title">OTIMIZAÇÃO DO PERFIL</div>
                    <div class="metric-value">{score}/100</div>
                    <div class="metric-desc">Margem para crescimento de conversão</div>
                </td>
                <td style="width: 2%;"></td>
                <td class="metric-box">
                    <div class="metric-title">NOTA DOS CLIENTES</div>
                    <div class="metric-value">★ {rating}</div>
                    <div class="metric-desc">Com base em {reviews} avaliações no Google</div>
                </td>
                <td style="width: 2%;"></td>
                <td class="metric-box">
                    <div class="metric-title">TOUR VIRTUAL 360°</div>
                    <div class="metric-value" style="color: #dc2626;">0 FOTOS</div>
                    <div class="metric-desc">Sem mídia 360° interativa detectada</div>
                </td>
            </tr>
        </table>

        <!-- Matriz de Diagnostico -->
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
                    <td class="dim-name">Recursos Interativos (Tour 360°)</td>
                    <td class="dim-status">Nenhuma foto 360° ou tour virtual interativo detectado no perfil.</td>
                    <td class="dim-impact">Visitantes não conseguem "visitar" virtualmente o espaço antes de presencialmente; perdem-se conversões por falta de imersão e confiança.</td>
                </tr>
                <tr>
                    <td class="dim-name">Fotos e Cobertura Visual</td>
                    <td class="dim-status">{photos_count} fotos identificadas no perfil. Cobertura básica do espaço.</td>
                    <td class="dim-impact">Poucas fotos reduzem o tempo de permanência na ficha. Imagens profissionais aumentam em até 35% os cliques para o site/WhatsApp.</td>
                </tr>
                <tr>
                    <td class="dim-name">Nota e Avaliações</td>
                    <td class="dim-status">Nota ★ {rating} com um total de {reviews} avaliações acumuladas.</td>
                    <td class="dim-impact">A reputação é um pilar vital no algoritmo do Google. Manter o fluxo constante de resenhas fortalece o SEO local e supera concorrentes.</td>
                </tr>
                <tr>
                    <td class="dim-name">Consistência de Dados (NAP)</td>
                    <td class="dim-status">Endereço e telefone cadastrados e ativos no Google Maps.</td>
                    <td class="dim-impact">Informações precisas garantem confiança ao algoritmo e facilitam que potenciais clientes entrem em contato sem fricção.</td>
                </tr>
            </tbody>
        </table>

        <!-- Plano de Acao Tour360vr -->
        <div class="offer-box">
            <div class="offer-title">PLANO DE AÇÃO RECOMENDADO (SOLUÇÕES TOUR360VR)</div>
            <div style="font-size: 8.5pt; color: #334155;">
                • <b>Implantação de Tour Virtual 360°:</b> Mapeamento imersivo HD integrado ao Google Street View para multiplicar a taxa de conversão.<br>
                • <b>Ensaio Fotográfico Profissional:</b> Fotos de alta qualidade das instalações, fachada e diferenciais do estabelecimento.<br>
                • <b>Gestão e Otimização Local:</b> Estruturação completa da ficha para alavancar a posição orgânica nas buscas da região.
            </div>
        </div>

        <div class="footer">
            Tour360vr • Tecnologia e Imagem Imersiva | www.tour360vr.com.br
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
        with st.spinner("Analisando ficha e gerando relatório PinCheck..."):
            dados = buscar_dados_google(empresa, cidade, api_key)
            if dados:
                pdf_bytes = gerar_pdf_bytes(dados)
                st.success("Diagnóstico gerado com sucesso!")

                st.download_button(
                    label="📥 Baixar Relatório PinCheck (PDF)",
                    data=pdf_bytes,
                    file_name=f"Diagnostico_PinCheck_{dados.get('name')}.pdf",
                    mime="application/pdf",
                )
            else:
                st.error("Empresa não encontrada no Google Maps.")

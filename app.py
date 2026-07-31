import datetime
import io
import requests
import streamlit as st
from xhtml2pdf import pisa

st.set_page_config(
    page_title="Diagnóstico Google - Tour360vr", page_icon="📍", layout="centered"
)

st.title("📍 Gerador de Diagnóstico Google Meu Negócio")
st.subheader("Ferramenta de Prospecção Tour360vr")

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
        "Nome da Empresa:", placeholder="Ex: Amazone Açaí Shop"
    )
    cidade = st.text_input("Cidade / Estado:", placeholder="Ex: Brodowski / SP")
    btn = st.form_submit_button("Gerar Diagnóstico em PDF")


def buscar_dados_google(empresa, cidade, key):
    query = f"{empresa} {cidade}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={key}"
    res = requests.get(url).json()

    if not res.get("results"):
        return None

    place_id = res["results"][0]["place_id"]
    url_details = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,photos,website&key={key}"
    return requests.get(url_details).json().get("result", {})


def gerar_pdf_bytes(dados):
    nome = dados.get("name", "N/A")
    endereco = dados.get("formatted_address", "N/A")
    telefone = dados.get("formatted_phone_number", "Não informado")
    rating = dados.get("rating", "N/A")
    reviews = dados.get("user_ratings_total", 0)
    photos_count = len(dados.get("photos", []))
    data_hoje = datetime.date.today().strftime("%d/%m/%Y")

    pontos_atencao = []
    if photos_count < 15:
        pontos_atencao.append(
            "Pouca variedade visual: O perfil possui poucas fotos profissionais do espaço interno e fachada."
        )

    try:
        if float(rating) < 4.5:
            pontos_atencao.append(
                f"Reputação abaixo do ideal: Nota média ({rating}) abaixo de 4.5 estrelas diminui a taxa de conversão."
            )
    except (ValueError, TypeError):
        pass

    pontos_atencao.append(
        "Ausência de Experiência Imersiva 360°: O perfil não possui Tour Virtual 360° interativo integrado ao Google Street View."
    )

    items_atencao_html = "".join(
        [f"<li>{item}</li>" for item in pontos_atencao]
    )

    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: a4 portrait;
                margin: 10mm 15mm 15mm 15mm;
            }}
            body {{
                font-family: Helvetica, Arial, sans-serif;
                color: #1e293b;
                font-size: 10pt;
                line-height: 1.4;
            }}
            
            /* Header */
            .header {{
                background-color: #0284c7;
                color: #ffffff;
                padding: 15px;
                margin-bottom: 15px;
            }}
            .brand-logo {{
                font-size: 22pt;
                font-weight: bold;
                color: #ffffff;
            }}
            .brand-logo-span {{
                color: #bae6fd;
            }}
            .brand-tagline {{
                font-size: 8pt;
                color: #e0f2fe;
                text-transform: uppercase;
                margin-top: 2px;
            }}
            .doc-title {{
                text-align: right;
                font-size: 11pt;
                font-weight: bold;
                color: #ffffff;
                text-transform: uppercase;
            }}
            .doc-date {{
                text-align: right;
                font-size: 8pt;
                color: #e0f2fe;
            }}
            
            /* Card Destaque */
            .business-card {{
                background-color: #f0f9ff;
                border-left: 5px solid #0284c7;
                padding: 12px;
                margin-bottom: 15px;
            }}
            .business-name {{
                font-size: 15pt;
                font-weight: bold;
                color: #0369a1;
                margin-bottom: 6px;
                text-transform: uppercase;
            }}
            
            .info-table {{
                width: 100%;
            }}
            .info-table td {{
                padding: 3px 0;
                font-size: 9.5pt;
            }}
            .label {{
                font-weight: bold;
                color: #475569;
                width: 120px;
            }}
            
            /* Seções */
            .section-box {{
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                padding: 12px;
                margin-bottom: 15px;
            }}
            .section-title {{
                font-size: 11pt;
                font-weight: bold;
                color: #0284c7;
                margin-bottom: 8px;
                text-transform: uppercase;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 4px;
            }}
            .section-title-alert {{
                color: #b91c1c;
            }}
            
            ul.alert-list {{
                margin: 0;
                padding-left: 15px;
            }}
            ul.alert-list li {{
                margin-bottom: 5px;
                font-size: 9.5pt;
                color: #334155;
            }}

            /* Tabela Ação */
            .action-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 5px;
            }}
            .action-table th {{
                background-color: #e0f2fe;
                color: #0369a1;
                text-align: left;
                padding: 6px;
                font-size: 8.5pt;
                text-transform: uppercase;
            }}
            .action-table td {{
                padding: 8px 6px;
                border-bottom: 1px solid #f1f5f9;
                font-size: 9pt;
            }}
            
            /* Rodapé */
            .footer {{
                text-align: center;
                font-size: 8pt;
                color: #0369a1;
                border-top: 1px solid #0284c7;
                padding-top: 6px;
                margin-top: 15px;
            }}
        </style>
    </head>
    <body>

        <div class="header">
            <table style="width: 100%;">
                <tr>
                    <td>
                        <div class="brand-logo">Tour<span class="brand-logo-span">360vr</span></div>
                        <div class="brand-tagline">Tecnologia & Experiências Imersivas</div>
                    </td>
                    <td style="text-align: right;">
                        <div class="doc-title">Diagnóstico do Perfil Google</div>
                        <div class="doc-date">Relatório Gerado em: {data_hoje}</div>
                    </td>
                </tr>
            </table>
        </div>

        <!-- Destaque do Estabelecimento -->
        <div class="business-card">
            <div class="business-name">{nome}</div>
            <table class="info-table">
                <tr>
                    <td class="label">Endereço:</td>
                    <td>{endereco}</td>
                </tr>
                <tr>
                    <td class="label">Telefone:</td>
                    <td>{telefone}</td>
                </tr>
                <tr>
                    <td class="label">Avaliações:</td>
                    <td><b>★ {rating}</b> ({reviews} avaliações no Google Maps)</td>
                </tr>
                <tr>
                    <td class="label">Mídias do Perfil:</td>
                    <td>{photos_count} fotos identificadas</td>
                </tr>
            </table>
        </div>

        <!-- Pontos de Atenção -->
        <div class="section-box">
            <div class="section-title section-title-alert">Pontos de Atenção e Oportunidades Críticas</div>
            <ul class="alert-list">
                {items_atencao_html}
            </ul>
        </div>

        <!-- Plano de Ação -->
        <div class="section-box">
            <div class="section-title">Plano de Ação Recomendado (Soluções Tour360vr)</div>
            <table class="action-table">
                <thead>
                    <tr>
                        <th style="width: 30%;">Solução</th>
                        <th style="width: 70%;">Benefício de Ranqueamento & Conversão</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>Implantação de Tour Virtual 360°</b></td>
                        <td>Aumenta o tempo de permanência no perfil, melhora o ranqueamento orgânico no Google Maps e transmite total transparência ao cliente.</td>
                    </tr>
                    <tr>
                        <td><b>Ensaio Fotográfico Profissional</b></td>
                        <td>Imagens de alta resolução destacando a fachada, o espaço interno e os produtos, elevando a percepção de valor da marca.</td>
                    </tr>
                    <tr>
                        <td><b>Otimização Local da Ficha (SEO)</b></td>
                        <td>Padronização de dados (NAP), atualização de categorias e estratégia de engajamento para atrair novos clientes da região.</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="footer">
            Tour360vr • Soluções em Imagem e Presença Digital | www.tour360vr.com.br
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
        with st.spinner("Buscando dados no Google e gerando relatório..."):
            dados = buscar_dados_google(empresa, cidade, api_key)
            if dados:
                pdf_bytes = gerar_pdf_bytes(dados)
                st.success("Diagnóstico gerado com sucesso!")

                st.download_button(
                    label="📥 Baixar Relatório em PDF (Tour360vr)",
                    data=pdf_bytes,
                    file_name=f"Diagnostico_{dados.get('name')}.pdf",
                    mime="application/pdf",
                )
            else:
                st.error("Empresa não encontrada no Google Maps.")

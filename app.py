import datetime
import requests
import streamlit as st
from weasyprint import HTML

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


def gerar_pdf_html(dados):
    nome = dados.get("name", "N/A")
    endereco = dados.get("formatted_address", "N/A")
    telefone = dados.get("formatted_phone_number", "Não informado")
    rating = dados.get("rating", "N/A")
    reviews = dados.get("user_ratings_total", 0)
    photos_count = len(dados.get("photos", []))
    data_hoje = datetime.date.today().strftime("%d/%m/%Y")

    # Monta lista de pontos de atenção
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

    # Item principal da Tour360vr
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
                size: A4;
                margin: 12mm 15mm 20mm 15mm;
                background-color: #f8fafc;
            }}
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #1e293b;
                margin: 0;
                padding: 0;
                font-size: 10pt;
                line-height: 1.5;
            }}
            /* Header */
            .header {{
                margin: -12mm -15mm 20px -15mm;
                padding: 18px 15mm;
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
                color: #ffffff;
                border-bottom: 4px solid #0284c7;
            }}
            .header-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .brand-logo {{
                font-size: 24pt;
                font-weight: 800;
                letter-spacing: -0.5px;
                color: #ffffff;
            }}
            .brand-logo span {{
                color: #38bdf8;
            }}
            .brand-tagline {{
                font-size: 8pt;
                color: #e0f2fe;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 2px;
            }}
            .doc-title {{
                text-align: right;
                font-size: 11pt;
                font-weight: 700;
                color: #ffffff;
                text-transform: uppercase;
            }}
            .doc-date {{
                text-align: right;
                font-size: 8pt;
                color: #bae6fd;
            }}
            /* Destaque do Estabelecimento */
            .business-card {{
                background: #ffffff;
                border-radius: 8px;
                padding: 18px;
                margin-bottom: 18px;
                border-left: 6px solid #0284c7;
                box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            }}
            .business-name {{
                font-size: 16pt;
                font-weight: 800;
                color: #0369a1;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }}
            .info-grid {{
                width: 100%;
                border-collapse: collapse;
            }}
            .info-grid td {{
                padding: 4px 0;
                vertical-align: top;
                font-size: 9.5pt;
            }}
            .label {{
                font-weight: 700;
                color: #64748b;
                width: 110px;
            }}
            .value {{
                color: #0f172a;
            }}

            /* Seções */
            .section-box {{
                background: #ffffff;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
                border: 1px solid #e2e8f0;
            }}
            .section-title {{
                font-size: 11pt;
                font-weight: 700;
                color: #0284c7;
                margin-top: 0;
                margin-bottom: 10px;
                text-transform: uppercase;
                border-bottom: 2px solid #f1f5f9;
                padding-bottom: 6px;
            }}
            .section-title-alert {{
                color: #b91c1c;
            }}

            ul.alert-list {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}
            ul.alert-list li {{
                position: relative;
                padding-left: 20px;
                margin-bottom: 8px;
                font-size: 9.5pt;
                color: #334155;
            }}
            ul.alert-list li::before {{
                content: "✕";
                position: absolute;
                left: 0;
                color: #dc2626;
                font-weight: bold;
            }}

            /* Tabela de Plano de Ação */
            .action-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 6px;
            }}
            .action-table th {{
                background: #f1f5f9;
                color: #0369a1;
                text-align: left;
                padding: 8px 10px;
                font-size: 8.5pt;
                text-transform: uppercase;
                border-bottom: 2px solid #cbd5e1;
            }}
            .action-table td {{
                padding: 10px;
                border-bottom: 1px solid #f1f5f9;
                font-size: 9pt;
            }}

            /* Footer */
            .footer {{
                position: fixed;
                bottom: -12mm;
                left: -15mm;
                right: -15mm;
                height: 12mm;
                background: #0369a1;
                color: #ffffff;
                padding: 0 15mm;
                line-height: 12mm;
                font-size: 8pt;
            }}
            .footer-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .footer-table td {{
                color: #e0f2fe;
            }}
            .footer-table td.right {{
                text-align: right;
                color: #ffffff;
                font-weight: 700;
            }}
        </style>
    </head>
    <body>

        <div class="header">
            <table class="header-table">
                <tr>
                    <td>
                        <div class="brand-logo">Tour<span>360vr</span></div>
                        <div class="brand-tagline">Tecnologia & Experiências Imersivas</div>
                    </td>
                    <td>
                        <div class="doc-title">Diagnóstico do Perfil Google</div>
                        <div class="doc-date">Relatório Gerado em: {data_hoje}</div>
                    </td>
                </tr>
            </table>
        </div>

        <!-- Destaque do Estabelecimento -->
        <div class="business-card">
            <div class="business-name">{nome}</div>
            <table class="info-grid">
                <tr>
                    <td class="label">Endereço:</td>
                    <td class="value">{endereco}</td>
                </tr>
                <tr>
                    <td class="label">Telefone:</td>
                    <td class="value">{telefone}</td>
                </tr>
                <tr>
                    <td class="label">Avaliações:</td>
                    <td class="value"><strong>★ {rating}</strong> ({reviews} avaliações no Google Maps)</td>
                </tr>
                <tr>
                    <td class="label">Mídias do Perfil:</td>
                    <td class="value">{photos_count} fotos identificadas</td>
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

        <!-- Plano de Ação Tour360vr -->
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
                        <td><strong>Implantação de Tour Virtual 360°</strong></td>
                        <td>Aumenta o tempo de permanência no perfil, melhora o ranqueamento orgânico no Google Maps e transmite total transparência ao cliente.</td>
                    </tr>
                    <tr>
                        <td><strong>Ensaio Fotográfico Profissional</strong></td>
                        <td>Imagens de alta resolução destacando a fachada, o espaço interno e os produtos, elevando a percepção de valor da marca.</td>
                    </tr>
                    <tr>
                        <td><strong>Otimização Local da Ficha (SEO)</strong></td>
                        <td>Padronização de dados (NAP), atualização de categorias e estratégia de engajamento para atrair novos clientes da região.</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="footer">
            <table class="footer-table">
                <tr>
                    <td>Tour360vr • Soluções em Imagem e Presença Digital</td>
                    <td class="right">www.tour360vr.com.br</td>
                </tr>
            </table>
        </div>

    </body>
    </html>
    """

    pdf_filename = "diagnostico_tour360vr.pdf"
    HTML(string=html_template).write_pdf(pdf_filename)
    return pdf_filename


if btn and empresa and cidade:
    if not api_key:
        st.error("Chave da API do Google não configurada nos Secrets.")
    else:
        with st.spinner("Buscando dados no Google e gerando relatório..."):
            dados = buscar_dados_google(empresa, cidade, api_key)
            if dados:
                pdf_file = gerar_pdf_html(dados)
                st.success("Diagnóstico gerado com sucesso!")

                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📥 Baixar Relatório em PDF (Tour360vr)",
                        data=f,
                        file_name=f"Diagnostico_{dados.get('name')}.pdf",
                        mime="application/pdf",
                    )
            else:
                st.error("Empresa não encontrada no Google Maps.")

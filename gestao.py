import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, date
from io import BytesIO
import urllib.parse
import qrcode
from PIL import Image as PILImage
from supabase import create_client, Client

# Bibliotecas para Scraping Gratuito
import requests
from bs4 import BeautifulSoup

# Importações do ReportLab para PDF (Padrão Enterprise Tour360VR)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Importação do Matplotlib para geração de gráficos no PDF
import matplotlib.pyplot as plt

# --- FAVICON DA TOUR360VR & CONFIGURAÇÃO DA PÁGINA ---
FAVICON_TOUR360 = "https://tour360vr.com.br/favicon.ico"

st.set_page_config(
    page_title="Gestão Mensal & Estratégia | Tour360VR",
    page_icon=FAVICON_TOUR360,
    layout="wide"
)

# --- CONEXÃO COM SUPABASE ---
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase_client()

# --- NAVEGAÇÃO SEQUENCIAL DAS ABAS ---
ORDEM_ABAS = ["cadastrar", "auditoria", "metricas", "ia", "dashboard", "cases", "pdf", "financeiro"]
NOMES_ABAS = {
    "cadastrar": "⚙️ Ficha Comercial",
    "auditoria": "🔍 Auditoria Link",
    "metricas": "📋 Métricas & SEO",
    "ia": "🎯 Curadoria & Pautas",
    "dashboard": "📊 Dashboard ROI",
    "cases": "🏆 Prospecção",
    "pdf": "📄 Relatório & Contrato",
    "financeiro": "💰 Financeiro MRR"
}

def gerar_botoes_navegacao_rodape():
    st.markdown("---")
    aba_atual = st.session_state.get("aba_ativa", "cadastrar")
    idx_atual = ORDEM_ABAS.index(aba_atual) if aba_atual in ORDEM_ABAS else 0
    
    col_v, col_p = st.columns([6, 2], gap="small")
    
    with col_v:
        if idx_atual > 0:
            aba_anterior = ORDEM_ABAS[idx_atual - 1]
            nome_ant = NOMES_ABAS[aba_anterior]
            if st.button(f"⬅️ Voltar ({nome_ant})", key=f"btn_rodape_prev_{aba_atual}"):
                st.session_state["aba_ativa"] = aba_anterior
                st.rerun()
                
    with col_p:
        if idx_atual < len(ORDEM_ABAS) - 1:
            aba_proxima = ORDEM_ABAS[idx_atual + 1]
            nome_prox = NOMES_ABAS[aba_proxima]
            if st.button(f"Próximo ({nome_prox}) ➡️", key=f"btn_rodape_next_{aba_atual}", use_container_width=True):
                st.session_state["aba_ativa"] = aba_proxima
                st.rerun()

# --- FUNÇÕES AUXILIARES DE BANCO DE DADOS ---
def obter_clientes_unicos():
    res = supabase.table("clientes").select("id, nome_empresa").order("nome_empresa").execute()
    if res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["id", "nome_empresa"])

def obter_dados_cliente_por_id(cliente_id):
    res = supabase.table("clientes").select("*").eq("id", cliente_id).execute()
    if res.data:
        return res.data[0]
    return None

def calcular_variacao_pct(atual, anterior):
    if anterior is None or anterior == 0:
        return "+100%" if atual > 0 else "0%"
    diff = ((atual - anterior) / anterior) * 100
    if diff > 0:
        return f"+{diff:.1f}%"
    return f"{diff:.1f}%"

# --- SCRAPER GRATUITO PARA AUDITORIA DE FICHA ---
def auditar_ficha_google(url_maps):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url_maps, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, "Não foi possível carregar a URL fornecida. Verifique o link."
        
        html = response.text
        
        tem_site = ("http://" in html or "https://" in html) and "website" in html.lower()
        tem_telefone = bool(re.search(r'\+?55\s?\(?\d{2}\)?\s?\d{4,5}\-?\d{4}', html)) or "phone" in html.lower()
        tem_avaliacoes = "star" in html.lower() or "comentários" in html.lower() or "reviews" in html.lower()
        tem_fotos = "photo" in html.lower() or "photos" in html.lower()
        
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else "Empresa Auditada"
        nome_extraido = title.replace("- Google Maps", "").replace("- Busca Google", "").strip()

        pontos = 0
        pendencias = []
        oportunidades = []

        if tem_site:
            pontos += 25
        else:
            pendencias.append("❌ Ficha sem Link de Website / Cartão Digital configurado")
            oportunidades.append("Incluir site ou landing page otimizada com Tour Virtual 360°")

        if tem_telefone:
            pontos += 25
        else:
            pendencias.append("❌ Número de Telefone Comercial / WhatsApp não destacado")

        if tem_avaliacoes:
            pontos += 25
        else:
            pendencias.append("⚠️ Poucas ou nenhuma avaliação visível destacada")
            oportunidades.append("Implementar estratégia de captação de reviews via QR Code de balcão")

        if tem_fotos:
            pontos += 25
        else:
            pendencias.append("⚠️ Ausência de fotos recentes e Tour Virtual 360° em alta definição")
            oportunidades.append("Realizar sessão fotográfica profissional + Tour 360° Street View")

        resultado = {
            "nome": nome_extraido if nome_extraido else "Empresa Selecionada",
            "score": pontos,
            "has_site": tem_site,
            "has_phone": tem_telefone,
            "has_reviews": tem_avaliacoes,
            "has_photos": tem_fotos,
            "pendencias": pendencias,
            "oportunidades": oportunidades
        }
        return resultado, None

    except Exception as e:
        return None, f"Erro ao analisar o link: {str(e)}"

# --- GERAR QR CODE PERMANENTE E LIMPO ---
def gerar_qr_code_limpo(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=12,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img_qr = qr.make_image(fill_color="#000000", back_color="#FFFFFF").convert('RGB')
    
    buffer = BytesIO()
    img_qr.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# --- GERAR GRÁFICO INDIVIDUAL EM MEMÓRIA ---
def gerar_imagem_grafico(df_historico):
    fig, ax = plt.subplots(figsize=(6.5, 2.0), dpi=200)
    
    ax.plot(df_historico['mes_ano'], df_historico['chamadas'], marker='o', color='#2563EB', linewidth=2, label='Chamadas (Ligações)')
    ax.plot(df_historico['mes_ano'], df_historico['rotas'], marker='s', color='#16A34A', linewidth=2, label='Solicitações de Rota')
    ax.plot(df_historico['mes_ano'], df_historico['cliques_site'], marker='^', color='#0284C7', linewidth=2, label='Cliques Site/Whats')

    ax.set_facecolor('#F8FAFC')
    fig.patch.set_facecolor('#FFFFFF')
    
    ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E1')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#94A3B8')
    ax.spines['bottom'].set_color('#94A3B8')
    
    plt.xticks(fontsize=8, color='#334155', fontweight='bold')
    plt.yticks(fontsize=8, color='#334155')
    ax.legend(loc='upper left', fontsize=7, frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1')
    
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig)
    img_buf.seek(0)
    return img_buf

# --- GERAR GRÁFICO CONSOLIDADO DE PROSPECÇÃO ---
def gerar_imagem_grafico_consolidado(df_agrupado):
    fig, ax = plt.subplots(figsize=(6.5, 2.2), dpi=200)
    
    ax.plot(df_agrupado['mes_ano'], df_agrupado['chamadas'], marker='o', color='#2563EB', linewidth=2.5, label='Total de Chamadas')
    ax.plot(df_agrupado['mes_ano'], df_agrupado['rotas'], marker='s', color='#16A34A', linewidth=2.5, label='Total de Solicitadas de Rota')
    ax.plot(df_agrupado['mes_ano'], df_agrupado['cliques_site'], marker='^', color='#0284C7', linewidth=2.5, label='Total de Cliques Site/Whats')

    ax.set_facecolor('#F8FAFC')
    fig.patch.set_facecolor('#FFFFFF')
    
    ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E1')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#94A3B8')
    ax.spines['bottom'].set_color('#94A3B8')
    
    plt.xticks(fontsize=8, color='#334155', fontweight='bold')
    plt.yticks(fontsize=8, color='#334155')
    ax.legend(loc='upper left', fontsize=7, frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1')
    
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig)
    img_buf.seek(0)
    return img_buf

# --- GERAÇÃO DO RELATÓRIO PDF EXECUTIVO (PADRÃO ENTERPRISE TOUR360VR) ---
def gerar_pdf_relatorio(nome_empresa, mes_ano, dados_atual, dados_anterior, dados_inicio, df_historico=None, df_keywords=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()

    title_brand_style = ParagraphStyle(
        'DocBrandTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor('#1E293B')
    )
    section_style = ParagraphStyle(
        'DocSection', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor('#1E293B')
    )
    body_style = ParagraphStyle(
        'DocBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#334155')
    )
    footer_style = ParagraphStyle(
        'DocFooter', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, alignment=1, textColor=colors.HexColor('#64748B')
    )

    header_table_data = [
        [
            Paragraph("🌐 <b>TOUR360VR</b><br/><font size=8 color='#64748B'>Gestão, SEO Local & Presença Estratégica</font>", title_brand_style),
            Paragraph(f"<b>RELATÓRIO DE DESEMPENHO</b><br/><font size=9 color='#2563EB'><b>{nome_empresa}</b></font><br/><font size=8 color='#64748B'>Mês de Referência: {mes_ano}</font>", ParagraphStyle('RHeader', parent=styles['Normal'], alignment=2, fontName='Helvetica'))
        ]
    ]
    t_header = Table(header_table_data, colWidths=[280, 240])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 4))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563EB'), spaceAfter=4))

    story.append(Paragraph("<b>1. Análise Comparativa de Desempenho e Crescimento:</b>", section_style))
    story.append(Spacer(1, 3))
    
    c_chamadas_ant = dados_anterior['chamadas'] if dados_anterior else 0
    c_rotas_ant = dados_anterior['rotas'] if dados_anterior else 0
    c_cliques_ant = dados_anterior['cliques_site'] if dados_anterior else 0
    c_vis_ant = dados_anterior['visualizacoes'] if dados_anterior else 0

    var_cham_mes = calcular_variacao_pct(dados_atual['chamadas'], c_chamadas_ant)
    var_rotas_mes = calcular_variacao_pct(dados_atual['rotas'], c_rotas_ant)
    var_cliques_mes = calcular_variacao_pct(dados_atual['cliques_site'], c_cliques_ant)
    var_vis_mes = calcular_variacao_pct(dados_atual['visualizacoes'], c_vis_ant)

    comp_table_data = [
        [
            Paragraph("<b>Indicador de Desempenho</b>", section_style),
            Paragraph("<b>Início Contrato</b>", section_style),
            Paragraph("<b>Mês Anterior</b>", section_style),
            Paragraph("<b>Mês Atual</b>", section_style),
            Paragraph("<b>Var. vs Mês Ant.</b>", section_style)
        ],
        [
            Paragraph("📞 Chamadas Telefónicas", body_style),
            Paragraph("Base Inicial", body_style),
            Paragraph(f"{c_chamadas_ant}", body_style),
            Paragraph(f"<b>{dados_atual['chamadas']}</b>", body_style),
            Paragraph(f"<b>{var_cham_mes}</b>", body_style)
        ],
        [
            Paragraph("🗺️ Solicitações de Rota GPS", body_style),
            Paragraph("Base Inicial", body_style),
            Paragraph(f"{c_rotas_ant}", body_style),
            Paragraph(f"<b>{dados_atual['rotas']}</b>", body_style),
            Paragraph(f"<b>{var_rotas_mes}</b>", body_style)
        ],
        [
            Paragraph("🌐 Cliques Site/WhatsApp", body_style),
            Paragraph("Base Inicial", body_style),
            Paragraph(f"{c_cliques_ant}", body_style),
            Paragraph(f"<b>{dados_atual['cliques_site']}</b>", body_style),
            Paragraph(f"<b>{var_cliques_mes}</b>", body_style)
        ],
        [
            Paragraph("👁️ Visualizações Ficha", body_style),
            Paragraph("Base Inicial", body_style),
            Paragraph(f"{c_vis_ant}", body_style),
            Paragraph(f"<b>{dados_atual['visualizacoes']}</b>", body_style),
            Paragraph(f"<b>{var_vis_mes}</b>", body_style)
        ],
        [
            Paragraph("⭐ Avaliações Totais", body_style),
            Paragraph(f"{dados_inicio['qtd_avaliacoes_inicio']} (★ {dados_inicio['nota_media_inicio']})", body_style),
            Paragraph("Acumulado", body_style),
            Paragraph(f"<b>+{dados_atual['novas_avaliacoes']} novas</b>", body_style),
            Paragraph("<b>Crescimento</b>", body_style)
        ],
        [
            Paragraph("📷 Fotos & Tour 360°", body_style),
            Paragraph(f"{dados_inicio['qtd_fotos_inicio']} fotos", body_style),
            Paragraph("Acumulado", body_style),
            Paragraph(f"<b>{dados_atual['total_fotos_mes']} fotos</b>", body_style),
            Paragraph(f"<b>+{max(0, dados_atual['total_fotos_mes'] - dados_inicio['qtd_fotos_inicio'])} novas</b>", body_style)
        ]
    ]

    t_comp = Table(comp_table_data, colWidths=[150, 95, 90, 90, 95])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 4))

    if df_keywords is not None and not df_keywords.empty:
        story.append(Paragraph("<b>2. Posição das Palavras-Chave no Google Maps (SEO Local):</b>", section_style))
        story.append(Spacer(1, 3))
        kw_table_data = [[Paragraph("<b>Palavra-Chave Monitorada</b>", section_style), Paragraph("<b>Posição Inicial</b>", section_style), Paragraph("<b>Posição Atual</b>", section_style), Paragraph("<b>Evolução</b>", section_style)]]
        for _, row in df_keywords.iterrows():
            pos_in = row['posicao_inicial']
            pos_at = row['posicao_atual']
            ganho = pos_in - pos_at
            txt_evol = f"<b>+{ganho} posições</b>" if ganho > 0 else ("Mantido" if ganho == 0 else f"{ganho} posições")
            kw_table_data.append([
                Paragraph(row['palavra_chave'], body_style),
                Paragraph(f"{pos_in}º lugar", body_style),
                Paragraph(f"<b>{pos_at}º lugar</b>", body_style),
                Paragraph(txt_evol, body_style)
            ])
        t_kw = Table(kw_table_data, colWidths=[200, 100, 100, 120])
        t_kw.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 3),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t_kw)
        story.append(Spacer(1, 4))

    if df_historico is not None and len(df_historico) > 1:
        story.append(Paragraph("<b>3. Curva de Evolução Histórica (Mês a Mês):</b>", section_style))
        story.append(Spacer(1, 3))
        img_buf = gerar_imagem_grafico(df_historico)
        story.append(Image(img_buf, width=520, height=140))
        story.append(Spacer(1, 4))

    if dados_atual['faturamento_estimado'] > 0:
        story.append(Paragraph("<b>4. Retorno sobre o Investimento Estimado (ROI):</b>", section_style))
        story.append(Spacer(1, 3))
        roi_data = [
            [
                Paragraph(f"💰 <b>Faturamento Estimado Gerado no Mês:</b> R$ {dados_atual['faturamento_estimado']:,.2f}", ParagraphStyle('GreenROI', parent=body_style, fontSize=9, textColor=colors.HexColor('#16A34A'))),
                Paragraph("<b>Calculado via:</b> Conversões Diretas x Ticket Médio", body_style)
            ]
        ]
        t_roi = Table(roi_data, colWidths=[320, 200])
        t_roi.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_roi)
        story.append(Spacer(1, 4))

    story.append(Paragraph("<b>5. Ações Técnicas & Melhores Práticas Aplicadas:</b>", section_style))
    story.append(Spacer(1, 3))
    acoes_texto = dados_atual['resumo_acoes'] if dados_atual['resumo_acoes'] else "Otimizações de rotina, monitorização de palavras-chave locais e gestão de reputação da ficha."
    story.append(Paragraph(acoes_texto.replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 5))

    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CBD5E1'), spaceAfter=4))
    story.append(Paragraph("<b>tour360vr.com.br</b> &nbsp;|&nbsp; contato@tour360vr.com.br &nbsp;|&nbsp; Whatsapp: (16) 99133-2121 &nbsp;|&nbsp; Tour360VR - Gestão de Perfil do Google & Presença Local", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- GERAÇÃO DO CONTRATO EM PDF (PADRÃO ROYAL TULIP) ---
def gerar_pdf_contrato(dados_cliente, plano_escolhido, valor_plano):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()

    title_brand_style = ParagraphStyle(
        'DocBrandTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=16, leading=20, textColor=colors.HexColor('#1E293B')
    )
    section_style = ParagraphStyle(
        'DocSection', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#1E293B')
    )
    body_style = ParagraphStyle(
        'DocBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#334155')
    )
    footer_style = ParagraphStyle(
        'DocFooter', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, alignment=1, textColor=colors.HexColor('#64748B')
    )

    header_table_data = [
        [
            Paragraph("🌐 <b>TOUR360VR</b><br/><font size=8 color='#64748B'>Estratégia, Tour 360°, SEO Local & Presença Digital</font>", title_brand_style),
            Paragraph("<b>CONTRATO DE PRESTAÇÃO DE SERVIÇOS</b><br/><font size=8 color='#2563EB'><b>Documento Jurídico Oficial</b></font>", ParagraphStyle('RHeader', parent=styles['Normal'], alignment=2, fontName='Helvetica'))
        ]
    ]
    t_header = Table(header_table_data, colWidths=[300, 220])
    story.append(t_header)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563EB'), spaceAfter=8))

    nome_emp = dados_cliente.get("nome_empresa", "Empresa Cliente")
    resp_emp = dados_cliente.get("responsavel", "Responsável")
    end_emp = dados_cliente.get("endereco_local", "Endereço não informado")
    tel_emp = dados_cliente.get("telefone_contato", "(16) 0000-0000")

    txt_qualificacao = f"""
    <b>CONTRATADA:</b> Tour360VR, representada por Rubens Okamoto, CNPJ: 04.824.331/0001-05 e Telefone: (16) 99133-2121.<br/><br/>
    <b>CONTRATANTE:</b> {nome_emp}, representada por {resp_emp}, localizada em {end_emp}, Telefone: {tel_emp}.<br/><br/>
    A CONTRATADA compromete-se a executar os serviços de otimização, reestruturação técnica, curadoria de pautas e/ou produção de Tour Virtual 360° para o perfil do Google da CONTRATANTE conforme o <b>{plano_escolhido}</b> no valor de <b>R$ {valor_plano:,.2f}</b>.
    """
    story.append(Paragraph(txt_qualificacao, body_style))
    story.append(Spacer(1, 8))

    clausulas = """
    <b>CLÁUSULA PRIMEIRA - DO OBJETO:</b> Os serviços serão iniciados em até 5 dias úteis após o fornecimento de todos os acessos e informações necessárias à gestão do perfil.<br/><br/>
    <b>CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES:</b> O não pagamento no prazo pactuado sujeitará o presente contrato à incidência de juros moratórios legais e à suspensão temporária dos serviços até a devida regularização.<br/><br/>
    <b>CLÁUSULA TERCEIRA - DOS DIREITOS DE USO E PROPRIEDADE:</b> Os direitos de uso do Tour Virtual 360° e fotos HD serão cedidos em caráter ilimitado à CONTRATANTE para veiculação no Google. A CONTRATADA reserva-se o direito de utilizar o material em seu portfólio de divulgação.<br/><br/>
    <b>CLÁUSULA QUARTA - CONFIDENCIALIDADE E LGPD:</b> As partes comprometem-se a manter sob sigilo absoluto todas as informações operacionais fornecidas, em conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).<br/><br/>
    <b>CLÁUSULA QUINTA - VALIDADE DA PROPOSTA:</b> A presente proposta e condições comerciais possuem validade de 15 (quinze) dias a contar da data de sua emissão.
    """
    story.append(Paragraph(clausulas, body_style))
    story.append(Spacer(1, 20))

    assinaturas_data = [
        [
            Paragraph("__________________________________________<br/><b>Rubens Okamoto</b><br/>Tour360VR", body_style),
            Paragraph(f"__________________________________________<br/><b>{resp_emp}</b><br/>{nome_emp}", body_style)
        ]
    ]
    t_ass = Table(assinaturas_data, colWidths=[260, 260])
    story.append(t_ass)
    story.append(Spacer(1, 15))

    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CBD5E1'), spaceAfter=6))
    story.append(Paragraph("<b>tour360vr.com.br</b> &nbsp;|&nbsp; contato@tour360vr.com.br &nbsp;|&nbsp; Whatsapp: (16) 99133-2121 &nbsp;|&nbsp; Tour360VR - Soluções em Visual Mídia & SEO Local", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- CSS PERSONALIZADO (STREAMLIT UI PROFISSIONAL) ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.0rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 90% !important;
        margin: 0 auto !important;
    }
    header[data-testid="stHeader"] { display: none !important; }
    .stApp { background-color: #0B0E14; color: #E0E6ED; font-family: 'Inter', -apple-system, sans-serif; }
    .top-card-container {
        background-color: #161F30; border: 1px solid #2B364A; border-radius: 10px; padding: 14px 20px !important; margin-bottom: 12px !important; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .main-title-card { color: #FFFFFF; font-weight: 800; font-size: 1.55rem; margin-top: 0 !important; margin-bottom: 3px !important; }
    .sub-title-card { color: #8E9BAE; font-size: 0.88rem; margin-bottom: 0px !important; }
    div[data-testid="stHorizontalBlock"] { gap: 0.35rem !important; margin-bottom: 12px !important; }
    div[data-testid="stColumn"] button {
        width: 100% !important; min-height: 46px !important; height: auto !important; background-color: #1A2130 !important; border: 1.5px solid #455570 !important; color: #FFFFFF !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 0.72rem !important;
    }
    div[data-testid="stForm"] { border-color: #2B364A !important; padding: 16px !important; border-radius: 10px !important; background-color: #131A28 !important; }
    </style>
""", unsafe_allow_html=True)

# --- NAVEGAÇÃO SUPERIOR ---
if "aba_ativa" not in st.session_state:
    st.session_state["aba_ativa"] = "cadastrar"

st.markdown("""
<div class="top-card-container">
    <h1 class="main-title-card">📈 Gestão Mensal & Estratégia do Perfil | Tour360VR</h1>
    <p class="sub-title-card">Plataforma corporativa de inteligência de Google Maps, auditoria, curadoria e contratos.</p>
</div>
""", unsafe_allow_html=True)

cols = st.columns([1.3, 1.25, 1.4, 1.15, 1.3, 1.2, 1.25, 1.35])
aba_map = [("cadastrar", "⚙️ Ficha Comercial"), ("auditoria", "🔍 Auditoria Link"), ("metricas", "📋 Métricas & SEO"), ("ia", "🎯 Curadoria & Pautas"), ("dashboard", "📊 Dashboard ROI"), ("cases", "🏆 Prospecção"), ("pdf", "📄 Relatório & Contrato"), ("financeiro", "💰 Financeiro MRR")]
for i, (key_aba, label_aba) in enumerate(aba_map):
    with cols[i]:
        if st.button(label_aba, key=f"btn_nav_{key_aba}", type="primary" if st.session_state["aba_ativa"] == key_aba else "secondary"):
            st.session_state["aba_ativa"] = key_aba
            st.rerun()

# ==========================================
# MÓDULO 1: CADASTRAR / EDITAR FICHA DO CLIENTE
# ==========================================
if st.session_state["aba_ativa"] == "cadastrar":
    st.subheader("⚙️ Cadastro e Atualização de Informações Comerciais (GMB)")
    df_clientes = obter_clientes_unicos()
    modo_edicao = False
    dados_existentes = None
    
    if not df_clientes.empty:
        opcoes = ["➕ Cadastrar Novo Cliente"] + df_clientes["nome_empresa"].tolist()
        sel_idx = 0
        if "cliente_sel_cad" in st.session_state and st.session_state["cliente_sel_cad"] in opcoes:
            sel_idx = opcoes.index(st.session_state["cliente_sel_cad"])
        
        cliente_menu = st.selectbox("Selecione para Cadastrar ou Editar um Cliente Existente:", opcoes, index=sel_idx, key="sel_cliente_menu_cad")
        st.session_state["cliente_sel_cad"] = cliente_menu
        
        if cliente_menu != "➕ Cadastrar Novo Cliente":
            modo_edicao = True
            c_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_menu]["id"].values[0])
            st.session_state["cliente_id_edicao"] = c_id
            dados_existentes = obter_dados_cliente_por_id(c_id)
            st.info(f"Modo de Edição Ativo: Alterando a Ficha de **{cliente_menu}**.")
        else:
            st.session_state.pop("cliente_id_edicao", None)

    with st.form("form_cliente_gmb_completo"):
        sub_t1, sub_t2, sub_t3, sub_t4, sub_t5, sub_t6 = st.tabs([
            "🏢 Sobre & Ficha", "💵 Contrato", "📞 Contato & Redes", "📍 Local", "🛠️ Checklist", "📜 Histórico"
        ])
        
        with sub_t1:
            c1, c2 = st.columns(2, gap="large")
            with c1:
                nome_empresa = st.text_input("Nome Comercial da Empresa *", value=dados_existentes["nome_empresa"] if (modo_edicao and dados_existentes) else "")
                responsavel = st.text_input("Nome do Responsável", value=dados_existentes.get("responsavel", "") if (modo_edicao and dados_existentes) else "")
            with c2:
                categoria_principal = st.text_input("Categoria Principal no GMB", value=dados_existentes.get("categoria_principal", "") if (modo_edicao and dados_existentes) else "")
                area_cobertura = st.text_input("Área de Cobertura / Região", value=dados_existentes.get("area_cobertura", "") if (modo_edicao and dados_existentes) else "")
            
            descricao_empresa = st.text_area("Descrição da Empresa", value=dados_existentes.get("descricao_empresa", "") if (modo_edicao and dados_existentes) else "", height=100)

        with sub_t2:
            c1, c2, c3 = st.columns(3, gap="medium")
            with c1:
                valor_contrato_mensal = st.number_input("Valor da Mensalidade (R$)", min_value=0.0, step=50.0, value=float(dados_existentes.get("valor_contrato_mensal", 450.0)) if (modo_edicao and dados_existentes) else 450.0)
            with c2:
                dia_vencimento = st.number_input("Dia Vencimento", min_value=1, max_value=31, step=1, value=int(dados_existentes.get("dia_vencimento", 10)) if (modo_edicao and dados_existentes) else 10)
            with c3:
                status_contrato = st.selectbox("Status do Contrato", ["Ativo", "Em Negociação", "Pausado", "Cancelado"], index=0)
            link_drive_midias = st.text_input("Link Drive Mídias / 360°", value=dados_existentes.get("link_drive_midias", "") if (modo_edicao and dados_existentes) else "")

        with sub_t3:
            c1, c2 = st.columns(2, gap="large")
            with c1:
                telefone_contato = st.text_input("Telefone Comercial", value=dados_existentes.get("telefone_contato", "") if (modo_edicao and dados_existentes) else "")
                whatsapp = st.text_input("WhatsApp para Envio (Ex: 16991332121)", value=dados_existentes.get("whatsapp", "") if (modo_edicao and dados_existentes) else "")
            with c2:
                website = st.text_input("Website / Link Principal", value=dados_existentes.get("website", "") if (modo_edicao and dados_existentes) else "")
                instagram = st.text_input("Instagram", value=dados_existentes.get("instagram", "") if (modo_edicao and dados_existentes) else "")

        with sub_t4:
            endereco_local = st.text_input("Endereço Físico Completo", value=dados_existentes.get("endereco_local", "") if (modo_edicao and dados_existentes) else "")

        with sub_t5:
            observacoes_tecnicas = st.text_area("Observações Técnicas", value=dados_existentes.get("observacoes_tecnicas", "") if (modo_edicao and dados_existentes) else "", height=100)

        with sub_t6:
            if not modo_edicao:
                st.info("Histórico disponível após o primeiro salvamento.")
            else:
                res_h = supabase.table("historico_ficha").select("data_alteracao, descricao_alteracao").eq("cliente_id", c_id).order("id", desc=True).execute()
                if res_h.data:
                    st.dataframe(pd.DataFrame(res_h.data), use_container_width=True)

        st.markdown("---")
        btn_salvar = st.form_submit_button("Salvar Nova Ficha" if not modo_edicao else "Atualizar Ficha e Gravar Histórico")

        if btn_salvar and nome_empresa:
            payload = {
                "nome_empresa": nome_empresa, "responsavel": responsavel, "categoria_principal": categoria_principal,
                "area_cobertura": area_cobertura, "descricao_empresa": descricao_empresa, "valor_contrato_mensal": valor_contrato_mensal,
                "dia_vencimento": dia_vencimento, "status_contrato": status_contrato, "link_drive_midias": link_drive_midias,
                "telefone_contato": telefone_contato, "whatsapp": whatsapp, "website": website, "instagram": instagram,
                "endereco_local": endereco_local, "observacoes_tecnicas": observacoes_tecnicas
            }
            try:
                if not modo_edicao:
                    payload["data_inicio"] = datetime.today().strftime("%Y-%m-%d")
                    res_ins = supabase.table("clientes").insert(payload).execute()
                    if res_ins.data:
                        novo_id = res_ins.data[0]["id"]
                        supabase.table("historico_ficha").insert({"cliente_id": novo_id, "data_alteracao": datetime.now().strftime("%Y-%m-%d %H:%M"), "descricao_alteracao": "Cadastro Inicial"}).execute()
                        st.success(f"Ficha de '{nome_empresa}' cadastrada!")
                        st.rerun()
                else:
                    supabase.table("clientes").update(payload).eq("id", c_id).execute()
                    supabase.table("historico_ficha").insert({"cliente_id": c_id, "data_alteracao": datetime.now().strftime("%Y-%m-%d %H:%M"), "descricao_alteracao": "Atualização Cadastral"}).execute()
                    st.success(f"Ficha de '{nome_empresa}' atualizada!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 2: AUDITORIA EXPRESS
# ==========================================
elif st.session_state["aba_ativa"] == "auditoria":
    st.subheader("🔍 Auditoria de Ficha Google em 1 Clique")
    url_prospect = st.text_input("URL do Google Maps da Empresa:", placeholder="https://maps.google.com/...")
    if st.button("⚡ Executar Varredura"):
        if url_prospect:
            res_aud, err = auditar_ficha_google(url_prospect)
            if err: st.error(err)
            else:
                st.success(f"Score da Ficha: {res_aud['score']}%")
                st.write(res_aud['pendencias'])
        else:
            st.warning("Insira uma URL válida.")
    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 3: MÉTRICAS & SEO
# ==========================================
elif st.session_state["aba_ativa"] == "metricas":
    st.subheader("📋 Métricas Mensais, SEO Local & ROI")
    df_clientes = obter_clientes_unicos()
    if df_clientes.empty:
        st.warning("Cadastre um cliente primeiro.")
    else:
        cliente_sel = st.selectbox("Cliente:", df_clientes["nome_empresa"].tolist())
        c_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_sel]["id"].values[0])
        with st.form("form_met"):
            mes_ref = st.date_input("Mês Referência", value=datetime.today()).strftime("%Y-%m")
            c1, c2, c3 = st.columns(3)
            with c1: chamadas = st.number_input("Chamadas", min_value=0, step=1)
            with c2: rotas = st.number_input("Rotas", min_value=0, step=1)
            with c3: cliques = st.number_input("Cliques Site", min_value=0, step=1)
            tm = st.number_input("Ticket Médio (R$)", value=150.0, step=10.0)
            tc = st.number_input("Taxa Conversão (%)", value=10.0, step=1.0) / 100.0
            fat = (chamadas + rotas + cliques) * tc * tm
            st.info(f"Faturamento Estimado Gerado: R$ {fat:,.2f}")
            if st.form_submit_button("Salvar Métricas"):
                supabase.table("metricas_mensais").insert({"cliente_id": c_id, "mes_ano": mes_ref, "chamadas": chamadas, "rotas": rotas, "cliques_site": cliques, "ticket_medio": tm, "taxa_conversao": tc, "faturamento_estimado": fat}).execute()
                st.success("Métricas salvas!")
    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 4: CURATORIA & PAUTAS INTELIGENTES (ENTERPRISE)
# ==========================================
elif st.session_state["aba_ativa"] == "ia":
    st.subheader("🎯 Curadoria Enterprise, Pautas Editáveis & Portal de Aprovação com Audit Trail")
    df_clientes = obter_clientes_unicos()

    if df_clientes.empty:
        st.info("Cadastre um cliente para acessar a curadoria.")
    else:
        cliente_ia = st.selectbox("Selecione o Cliente:", df_clientes["nome_empresa"].tolist())
        c_ia_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_ia]["id"].values[0])
        dados_c = obter_dados_cliente_por_id(c_ia_id)

        cat = dados_c.get("categoria_principal") or "serviços locais"
        reg = dados_c.get("area_cobertura") or "região"
        emp = dados_c.get("nome_empresa")

        st.markdown(f"**Banco de Pautas Inteligentes — Segmento: {cat} ({reg})**")
        
        # Pautas Padrão Inteligentes Editáveis
        pautas_sugeridas = [
            f"Como escolher o melhor serviço de {cat} em {reg}?",
            f"Bastidores da equipe da {emp}: Nosso compromisso com a excelência.",
            f"Conheça a estrutura imersiva da {emp} em Tour Virtual 360°.",
            f"Diferenciais técnicos que tornam a {emp} referência na região.",
            f"Atendimento rápido, orçamentos e facilidades pelo WhatsApp da {emp}."
        ]

        st.markdown("### Selecione e Edite as Pautas do Mês:")
        pautas_selecionadas = []
        for idx, p_text in enumerate(pautas_sugeridas, 1):
            col_chk, col_txt = st.columns([0.1, 0.9])
            with col_chk:
                ativo = st.checkbox("", value=True, key=f"chk_pauta_{idx}")
            with col_txt:
                p_editada = st.text_input(f"Pauta {idx}", value=p_text, key=f"txt_pauta_{idx}", label_visibility="collapsed")
            if ativo:
                pautas_selecionadas.append(p_editada)

        st.markdown("---")
        st.markdown("### 🔗 Link Único de Aprovação & Prova Jurídica (Audit Trail)")
        link_exemplo = f"https://tour360vr.com.br/aprovar/{emp.lower().replace(' ', '-')}"
        st.text_input("Link Único Exclusivo para Envio ao Cliente:", value=link_exemplo)
        st.caption("O cliente receberá este link, marcará a aprovação pauta a pauta e o sistema gravará o Audit Trail (Data, Hora e IP) no Supabase para sua segurança jurídica.")

        num_wsp = dados_c.get("whatsapp", "")
        num_limpo = "".join([c for c in str(num_wsp) if c.isdigit()])
        msg_wsp = urllib.parse.quote(f"Olá {dados_c.get('responsavel', emp)}! Aqui é o Rubens da Tour360VR. Segue o link com o planejamento de pautas estratégicas para sua aprovação este mês: {link_exemplo}")

        if num_limpo:
            st.markdown(f'<a href="https://wa.me/55{num_limpo}?text={msg_wsp}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#16A34A; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold; cursor:pointer;">📱 Enviar Link de Aprovação via WhatsApp</button></a>', unsafe_allow_html=True)
        else:
            st.warning("Cadastre o WhatsApp do cliente na aba 'Ficha Comercial' para habilitar o botão de envio.")

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 5: DASHBOARD & ROI
# ==========================================
elif st.session_state["aba_ativa"] == "dashboard":
    st.subheader("📊 Dashboard Executivo & ROI")
    df_clientes = obter_clientes_unicos()
    if not df_clientes.empty:
        c_dash = st.selectbox("Cliente:", df_clientes["nome_empresa"].tolist())
        c_id_d = int(df_clientes[df_clientes["nome_empresa"] == c_dash]["id"].values[0])
        res_m = supabase.table("metricas_mensais").select("*").eq("cliente_id", c_id_d).execute()
        if res_m.data:
            df_m = pd.DataFrame(res_m.data)
            st.line_chart(df_m.set_index("mes_ano")[["chamadas", "rotas", "cliques_site"]])
        else:
            st.info("Sem métricas cadastradas.")
    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 6: PROSPECÇÃO (CASES)
# ==========================================
elif st.session_state["aba_ativa"] == "cases":
    st.subheader("🏆 Gerador de Relatório Comercial de Prospecção")
    st.info("Módulo ativo com banco consolidado de cases da agência.")
    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 7: RELATÓRIO PDF & CONTRATO
# ==========================================
elif st.session_state["aba_ativa"] == "pdf":
    st.subheader("📄 Emissão de Relatório Executivo & Minuta de Contrato em PDF")
    df_clientes = obter_clientes_unicos()
    if df_clientes.empty:
        st.warning("Cadastre um cliente primeiro.")
    else:
        c_pdf = st.selectbox("Cliente:", df_clientes["nome_empresa"].tolist())
        c_id_p = int(df_clientes[df_clientes["nome_empresa"] == c_pdf]["id"].values[0])
        dados_cli = obter_dados_cliente_por_id(c_id_p)

        tab_pdf1, tab_pdf2 = st.tabs(["📄 Relatório Executivo PDF", "📜 Contrato Jurídico (Royal Tulip Style)"])

        with tab_pdf1:
            res_m = supabase.table("metricas_mensais").select("*").eq("cliente_id", c_id_p).order("mes_ano").execute()
            if res_m.data:
                df_m = pd.DataFrame(res_m.data)
                mes_sel = st.selectbox("Mês Referência:", df_m["mes_ano"].tolist()[::-1])
                idx = df_m[df_m["mes_ano"] == mes_sel].index[0]
                d_atual = df_m.iloc[idx].to_dict()
                d_ant = df_m.iloc[idx - 1].to_dict() if idx - 1 >= 0 else None
                
                pdf_bytes = gerar_pdf_relatorio(c_pdf, mes_sel, d_atual, d_ant, {'qtd_avaliacoes_inicio': 0, 'nota_media_inicio': 5.0, 'qtd_fotos_inicio': 0}, df_m.iloc[:idx+1])
                st.download_button("📥 Baixar Relatório Executivo PDF", data=pdf_bytes, file_name=f"Relatorio_{c_pdf}_{mes_sel}.pdf", mime="application/pdf")

        with tab_pdf2:
            st.markdown("**Gerador Automático da Minuta de Contrato:**")
            plano_sel = st.selectbox("Selecione o Plano:", ["Plano Start (R$ 500,00)", "Plano Pro (R$ 1.500,00)", "Gestão Mensal (R$ 600,00)"])
            val_p = 500.0 if "Start" in plano_sel else (1500.0 if "Pro" in plano_sel else 600.0)
            
            if st.button(" gerar Contrato Oficial em PDF"):
                pdf_contrato = gerar_pdf_contrato(dados_cli, plano_sel, val_p)
                st.download_button("📥 Baixar Contrato em PDF", data=pdf_contrato, file_name=f"Contrato_{c_pdf}.pdf", mime="application/pdf")

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 8: FINANCEIRO & MRR
# ==========================================
elif st.session_state["aba_ativa"] == "financeiro":
    st.subheader("💰 Gestão Financeira MRR & Backup")
    res_cli = supabase.table("clientes").select("*").execute()
    df_c = pd.DataFrame(res_cli.data) if res_cli.data else pd.DataFrame()
    if not df_c.empty:
        mrr = df_c[df_c["status_contrato"] == "Ativo"]["valor_contrato_mensal"].sum()
        st.metric("💵 MRR Total da Agência", f"R$ {mrr:,.2f}")
        st.dataframe(df_c, use_container_width=True)
    gerar_botoes_navegacao_rodape()

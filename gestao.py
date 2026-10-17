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

# Importações do ReportLab para PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
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
    "ia": "🎯 Curadoria",
    "dashboard": "📊 Dashboard ROI",
    "cases": "🏆 Prospecção",
    "pdf": "📄 Relatório PDF",
    "financeiro": "💰 Financeiro MRR"
}

def gerar_botoes_navegacao_rodape():
    st.markdown("---")
    aba_atual = st.session_state.get("aba_ativa", "cadastrar")
    idx_atual = ORDEM_ABAS.index(aba_atual) if aba_atual in ORDEM_ABAS else 0
    
    col_v, col_centro, col_p = st.columns([1.5, 3.5, 1.5], gap="large")
    
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
            if st.button(f"Próximo ({nome_prox}) ➡️", key=f"btn_rodape_next_{aba_atual}"):
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

# --- GERAÇÃO DO RELATÓRIO PDF DO CLIENTE ---
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
        fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#1E293B')
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
    story.append(Spacer(1, 6))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3B4866'), spaceAfter=8))

    story.append(Paragraph("<b>1. Análise Comparativa de Desempenho e Crescimento:</b>", section_style))
    story.append(Spacer(1, 4))
    
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
            Paragraph("🗺️ Solicitadas de Rota GPS", body_style),
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
        ('PADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 6))

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
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t_kw)
        story.append(Spacer(1, 6))

    if df_historico is not None and len(df_historico) > 1:
        story.append(Paragraph("<b>3. Curva de Evolução Histórica (Mês a Mês):</b>", section_style))
        story.append(Spacer(1, 3))
        img_buf = gerar_imagem_grafico(df_historico)
        story.append(Image(img_buf, width=520, height=160))
        story.append(Spacer(1, 6))

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
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_roi)
        story.append(Spacer(1, 6))

    story.append(Paragraph("<b>5. Ações Técnicas & Melhores Práticas Aplicadas:</b>", section_style))
    story.append(Spacer(1, 3))
    acoes_texto = dados_atual['resumo_acoes'] if dados_atual['resumo_acoes'] else "Otimizações de rotina, monitorização de palavras-chave locais e gestão de reputação da ficha."
    story.append(Paragraph(acoes_texto.replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 10))

    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CBD5E1'), spaceAfter=6))
    story.append(Paragraph("<b>tour360vr.com.br</b> &nbsp;|&nbsp; contato@tour360vr.com.br &nbsp;|&nbsp; Whatsapp: (16) 99133-2121 &nbsp;|&nbsp; Tour360VR - Gestão de Perfil do Google & Presença Local", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- GERAÇÃO DO PDF COMERCIAL DE PROSPECÇÃO ---
def gerar_pdf_prospeccao_cases(inc_clientes, inc_faturamento, inc_grafico, inc_keywords, qtd_clientes, total_fat, df_agrupado, df_keywords):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()

    title_brand_style = ParagraphStyle(
        'DocBrandTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#1E293B')
    )
    section_style = ParagraphStyle(
        'DocSection', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#1E293B')
    )
    body_style = ParagraphStyle(
        'DocBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#334155')
    )
    footer_style = ParagraphStyle(
        'DocFooter', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, alignment=1, textColor=colors.HexColor('#64748B')
    )

    header_table_data = [
        [
            Paragraph("🌐 <b>TOUR360VR</b><br/><font size=8 color='#64748B'>Estratégia, Tour 360°, SEO Local & Presença Digital</font>", title_brand_style),
            Paragraph("<b>APRESENTAÇÃO DE PERFORMANCE & CASES DE SUCESSO</b><br/><font size=8 color='#2563EB'><b>Mídia & Otimização GMB</b></font>", ParagraphStyle('RHeader', parent=styles['Normal'], alignment=2, fontName='Helvetica'))
        ]
    ]
    t_header = Table(header_table_data, colWidths=[300, 220])
    story.append(t_header)
    story.append(Spacer(1, 6))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563EB'), spaceAfter=10))

    story.append(Paragraph("<b>1. Resumo Consolidado de Resultados da Agência:</b>", section_style))
    story.append(Spacer(1, 4))

    txt_resumo = "A Tour360VR desenvolve estratégias personalizadas de posicionamento local, fotogrametria 360°, otimização de fichas no Google Maps e citabilidade para empresas que buscam liderança de mercado em sua região."
    story.append(Paragraph(txt_resumo, body_style))
    story.append(Spacer(1, 6))

    cards_data = []
    if inc_clientes:
        cards_data.append(Paragraph(f"<b>Empresas Atendidas:</b><br/><font size=12 color='#2563EB'><b>{qtd_clientes} clientes</b></font>", body_style))
    if inc_faturamento:
        cards_data.append(Paragraph(f"<b>Faturamento Gerado Est.:</b><br/><font size=12 color='#16A34A'><b>R$ {total_fat:,.2f}</b></font>", body_style))

    if cards_data:
        t_cards = Table([cards_data], colWidths=[250]*len(cards_data))
        t_cards.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 8),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t_cards)
        story.append(Spacer(1, 10))

    if inc_grafico and df_agrupado is not None and not df_agrupado.empty:
        story.append(Paragraph("<b>2. Curva do Volume de Clientes Gerados (Mês a Mês):</b>", section_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph("Evolução somada do número de ligações telefónicas, rotas no GPS e mensagens no WhatsApp enviadas para nossos parceiros:", body_style))
        story.append(Spacer(1, 4))
        img_buf = gerar_imagem_grafico_consolidado(df_agrupado)
        story.append(Image(img_buf, width=520, height=170))
        story.append(Spacer(1, 10))

    if inc_keywords and df_keywords is not None and not df_keywords.empty:
        story.append(Paragraph("<b>3. Exemplos Reais de Posicionamento no Topo do Google Maps:</b>", section_style))
        story.append(Spacer(1, 4))
        
        kw_table_data = [[Paragraph("<b>Palavra-Chave / Termo de Busca</b>", section_style), Paragraph("<b>Posição Inicial</b>", section_style), Paragraph("<b>Posição Atual</b>", section_style), Paragraph("<b>Ganho de Posições</b>", section_style)]]
        for _, row in df_keywords.iterrows():
            pos_in = row['posicao_inicial']
            pos_at = row['posicao_atual']
            ganho = pos_in - pos_at
            txt_evol = f"<b>+{ganho} posições no Maps</b>" if ganho > 0 else "Liderança Mantida"
            kw_table_data.append([
                Paragraph(row['palavra_chave'], body_style),
                Paragraph(f"{pos_in}º lugar", body_style),
                Paragraph(f"<b>{pos_at}º lugar</b>", body_style),
                Paragraph(txt_evol, body_style)
            ])
        t_kw = Table(kw_table_data, colWidths=[210, 95, 95, 120])
        t_kw.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t_kw)
        story.append(Spacer(1, 10))

    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CBD5E1'), spaceAfter=8))
    story.append(Paragraph("<b>tour360vr.com.br</b> &nbsp;|&nbsp; contato@tour360vr.com.br &nbsp;|&nbsp; Whatsapp: (16) 99133-2121 &nbsp;|&nbsp; Tour360VR - Soluções em Visual Mídia & SEO Local", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- CSS PERSONALIZADO (BOTÕES SEM CORTES, ESPAÇAMENTO ORIGINAL E RESPIRO LATERAL NAS COLUNAS) ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2.8rem !important;
        max-width: 90% !important;
        margin: 0 auto !important;
    }
    
    header[data-testid="stHeader"] {
        display: none !important;
    }

    .stApp {
        background-color: #0B0E14;
        color: #E0E6ED;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .top-card-container {
        background-color: #161F30;
        border: 1px solid #2B364A;
        border-radius: 12px;
        padding: 22px 28px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    }

    .main-title-card {
        color: #FFFFFF;
        font-weight: 800;
        font-size: 1.85rem;
        margin-top: 0 !important;
        margin-bottom: 6px !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.4);
    }

    .sub-title-card {
        color: #8E9BAE;
        font-size: 0.92rem;
        margin-bottom: 0px !important;
    }

    /* ESPAÇAMENTO ENTRE AS COLUNAS DE BOTÕES SUPERIORES */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.5rem !important;
        margin-bottom: 25px !important;
    }

    /* MAIOR ESPAÇAMENTO LATERAL (HORIZONTAL) ENTRE COLUNAS DE CAMPOS */
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        padding-left: 14px !important;
        padding-right: 14px !important;
    }

    div[data-testid="stColumn"] {
        padding: 0px !important;
    }

    /* ESTILIZAÇÃO DOS BOTÕES SUPERIORES (SEM CORTAR TEXTO, LARGURA AUTOMÁTICA) */
    div[data-testid="stColumn"] button {
        width: 100% !important;
        min-height: 46px !important;
        height: 46px !important;
        background-color: #1A2130 !important;
        border: 1.5px solid #455570 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        padding: 2px 8px !important;
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        line-height: 1.1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        transition: all 0.25s ease-in-out !important;
    }

    div[data-testid="stColumn"] button:hover {
        background-color: #222C3E !important;
        border-color: #FFFFFF !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 14px rgba(255, 255, 255, 0.75) !important;
    }

    /* BOTÃO SELECIONADO (EFEITO NEON BRANCO) */
    div[data-testid="stColumn"] button[kind="primary"] {
        background-color: #1A2130 !important;
        border: 2px solid #FFFFFF !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.95) !important;
    }

    /* FORMULÁRIOS E CAIXAS */
    div[data-testid="stForm"] {
        border-color: #2B364A !important;
        padding: 24px !important;
        border-radius: 12px !important;
        margin-top: 15px !important;
        background-color: #131A28 !important;
    }

    /* ESPAÇAMENTO VERTICAL ORIGINAL ENTRE OS CAMPOS */
    div[data-testid="stTextInput"], 
    div[data-testid="stNumberInput"], 
    div[data-testid="stSelectbox"], 
    div[data-testid="stDateInput"],
    div[data-testid="stTextArea"] {
        margin-bottom: 14px !important;
    }

    div[data-baseweb="tab-list"] {
        gap: 12px !important;
        margin-bottom: 22px !important;
    }

    button[data-baseweb="tab"] {
        padding: 8px 16px !important;
        font-size: 0.90rem !important;
    }

    .dia-destaque {
        color: #FFFFFF !important;
        font-weight: 700;
        font-size: 1.05rem;
        margin-top: 1.2rem;
        margin-bottom: 0.4rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONTROLADOR DE NAVEGAÇÃO SUPERIOR ---
if "aba_ativa" not in st.session_state:
    st.session_state["aba_ativa"] = "cadastrar"

st.markdown("""
<div class="top-card-container">
    <h1 class="main-title-card">📈 Gestão Mensal & Estratégia do Perfil | Tour360VR</h1>
    <p class="sub-title-card">Acompanhamento de perfis no Google Maps, auditoria instantânea, curadoria de conteúdo e ROI.</p>
</div>
""", unsafe_allow_html=True)

# COLUNAS COM LARGURAS PROPORCIONAIS
cols = st.columns([1.35, 1.25, 1.25, 1.1, 1.3, 1.2, 1.25, 1.35])

with cols[0]:
    if st.button("⚙️ Ficha Comercial", key="btn_cad", type="primary" if st.session_state["aba_ativa"] == "cadastrar" else "secondary"):
        st.session_state["aba_ativa"] = "cadastrar"
        st.rerun()

with cols[1]:
    if st.button("🔍 Auditoria Link", key="btn_auditoria", type="primary" if st.session_state["aba_ativa"] == "auditoria" else "secondary"):
        st.session_state["aba_ativa"] = "auditoria"
        st.rerun()

with cols[2]:
    if st.button("📋 Métricas & SEO", key="btn_inc", type="primary" if st.session_state["aba_ativa"] == "metricas" else "secondary"):
        st.session_state["aba_ativa"] = "metricas"
        st.rerun()

with cols[3]:
    if st.button("🎯 Curadoria", key="btn_ia", type="primary" if st.session_state["aba_ativa"] == "ia" else "secondary"):
        st.session_state["aba_ativa"] = "ia"
        st.rerun()

with cols[4]:
    if st.button("📊 Dashboard ROI", key="btn_dash", type="primary" if st.session_state["aba_ativa"] == "dashboard" else "secondary"):
        st.session_state["aba_ativa"] = "dashboard"
        st.rerun()

with cols[5]:
    if st.button("🏆 Prospecção", key="btn_cases", type="primary" if st.session_state["aba_ativa"] == "cases" else "secondary"):
        st.session_state["aba_ativa"] = "cases"
        st.rerun()

with cols[6]:
    if st.button("📄 Relatório PDF", key="btn_pdf", type="primary" if st.session_state["aba_ativa"] == "pdf" else "secondary"):
        st.session_state["aba_ativa"] = "pdf"
        st.rerun()

with cols[7]:
    if st.button("💰 Financeiro MRR", key="btn_fin", type="primary" if st.session_state["aba_ativa"] == "financeiro" else "secondary"):
        st.session_state["aba_ativa"] = "financeiro"
        st.rerun()

# ==========================================
# MÓDULO 1: CADASTRAR / EDITAR FICHA DO CLIENTE
# ==========================================
if st.session_state["aba_ativa"] == "cadastrar":
    st.subheader("⚙️ Cadastro e Atualização de Informações Comerciais (GMB)")
    
    df_clientes_existentes = obter_clientes_unicos()
    modo_edicao = False
    dados_existentes = None
    
    if not df_clientes_existentes.empty:
        opcoes_clientes = ["➕ Cadastrar Novo Cliente"] + df_clientes_existentes["nome_empresa"].tolist()
        cliente_selecionado_menu = st.selectbox("Selecione para Cadastrar ou Editar um Cliente Existente:", opcoes_clientes, key="sel_cliente_menu_cad")
        
        if cliente_selecionado_menu != "➕ Cadastrar Novo Cliente":
            modo_edicao = True
            c_id = int(df_clientes_existentes[df_clientes_existentes["nome_empresa"] == cliente_selecionado_menu]["id"].values[0])
            dados_existentes = obter_dados_cliente_por_id(c_id)
            st.info(f"Modo de Edição Ativo: Alterando a Ficha de **{cliente_selecionado_menu}**.")

    with st.form("form_cliente_gmb_completo"):
        sub_tab_sobre, sub_tab_financeiro, sub_tab_contato, sub_tab_local, sub_tab_horario, sub_tab_mais, sub_tab_historico = st.tabs([
            "🏢 Sobre & Status Ficha", "💵 Valor Contrato", "📞 Contato & Redes", "📍 Local & Áreas", "⏰ Horários Rápidos", "🛠️ Checklist", "📜 Histórico"
        ])
        
        with sub_tab_sobre:
            st.markdown("**Identificação Comercial & Auditoria Inicial:**")
            st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
            c_s1, c_s2 = st.columns(2, gap="large")

            opts_reivindicada = ["Reivindicada & Verificada", "Não Reivindicada", "Em Processo"]
            opts_avaliacoes = ["Sim (Com Nota Exibida)", "Não (Sem Avaliações)"]
            opts_respostas = ["100% Respondidas", "Parcialmente", "Nenhuma", "N/A"]

            val_dt_abertura = date.today()
            if modo_edicao and dados_existentes and dados_existentes.get("data_abertura"):
                try:
                    val_dt_abertura = datetime.strptime(dados_existentes["data_abertura"], "%d/%m/%Y").date()
                except ValueError:
                    val_dt_abertura = date.today()

            with c_s1:
                nome_empresa = st.text_input("Nome Comercial da Empresa / Ficha GMB *", value=dados_existentes["nome_empresa"] if modo_edicao else "", key="txt_nome_empresa_cad")
                responsavel = st.text_input("Nome do Responsável / Contato Interno", value=dados_existentes.get("responsavel", "") if modo_edicao else "", key="txt_responsavel_cad")
                
                data_abertura_dt = st.date_input("Data de Abertura (Dia/Mês/Ano)", value=val_dt_abertura, format="DD/MM/YYYY", key="dt_abertura_cad")
                data_abertura_str = data_abertura_dt.strftime("%d/%m/%Y")
                
                v_reiv = dados_existentes.get("ficha_reivindicada", "") if modo_edicao else ""
                idx_reiv = opts_reivindicada.index(v_reiv) if v_reiv in opts_reivindicada else 0
                ficha_reivindicada = st.radio("Status de Reivindicação da Ficha", opts_reivindicada, index=idx_reiv, horizontal=True, key="rad_reivindicada_cad")
                
                v_resp = dados_existentes.get("status_respostas_avaliacoes", "") if modo_edicao else ""
                idx_resp = opts_respostas.index(v_resp) if v_resp in opts_respostas else 0
                status_respostas_avaliacoes = st.radio("Status de Resposta às Avaliações", opts_respostas, index=idx_resp, horizontal=True, key="rad_respostas_cad")

            with c_s2:
                categoria_principal = st.text_input("Categoria Principal no GMB", value=dados_existentes.get("categoria_principal", "") if modo_edicao else "", key="txt_cat_princ_cad")
                categorias_secundarias = st.text_input("Categorias Secundárias", value=dados_existentes.get("categorias_secundarias", "") if modo_edicao else "", key="txt_cat_sec_cad")
                
                v_aval = dados_existentes.get("status_avaliacoes", "") if modo_edicao else ""
                idx_aval = opts_avaliacoes.index(v_aval) if v_aval in opts_avaliacoes else 0
                status_avaliacoes = st.radio("Possui Avaliações de Clientes?", opts_avaliacoes, index=idx_aval, horizontal=True, key="rad_avaliacoes_cad")

                st.markdown("**Métricas no Início da Gestão:**")
                col_av1, col_av2, col_av3 = st.columns(3, gap="medium")
                with col_av1:
                    qtd_avaliacoes_inicio = st.number_input("Avaliações Iniciais", min_value=0, step=1, value=int(dados_existentes.get("qtd_avaliacoes_inicio", 0)) if modo_edicao else 0, key="num_aval_ini_cad")
                with col_av2:
                    nota_media_inicio = st.number_input("Nota Média Inicial", min_value=0.0, max_value=5.0, step=0.1, value=float(dados_existentes.get("nota_media_inicio", 5.0)) if modo_edicao else 5.0, key="num_nota_ini_cad")
                with col_av3:
                    qtd_fotos_inicio = st.number_input("Qtd. Fotos Iniciais", min_value=0, step=1, value=int(dados_existentes.get("qtd_fotos_inicio", 0)) if modo_edicao else 0, key="num_fotos_ini_cad")
            
            st.markdown("---")
            descricao_empresa = st.text_area("Descrição Oficial da Empresa", value=dados_existentes.get("descricao_empresa", "") if modo_edicao else "", height=180, key="txt_desc_empresa_cad")

        with sub_tab_financeiro:
            st.markdown("**Dados do Contrato do Cliente:**")
            st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
            col_f1, col_f2, col_f3 = st.columns([1.2, 1.2, 2.6], gap="medium")
            
            opts_status_contrato = ["Ativo", "Em Negociação", "Pausado", "Cancelado"]
            val_status = dados_existentes.get("status_contrato", "Ativo") if modo_edicao else "Ativo"
            idx_st_c = opts_status_contrato.index(val_status) if val_status in opts_status_contrato else 0

            with col_f1:
                valor_contrato_mensal = st.number_input("Valor da Mensalidade (R$)", min_value=0.0, step=50.0, value=float(dados_existentes.get("valor_contrato_mensal", 450.0)) if modo_edicao else 450.0, key="num_valor_mensalidade_cad")
            with col_f2:
                dia_vencimento = st.number_input("Dia do Vencimento Mensal", min_value=1, max_value=31, step=1, value=int(dados_existentes.get("dia_vencimento", 10)) if modo_edicao else 10, key="num_dia_vencimento_cad")
            with col_f3:
                status_contrato = st.radio("Status do Contrato com a Agência", opts_status_contrato, index=idx_st_c, horizontal=True, key="rad_status_contrato_cad")

            st.markdown("---")
            link_drive_midias = st.text_input("Link da Pasta de Mídias e Fotos 360°", value=dados_existentes.get("link_drive_midias", "") if modo_edicao else "", key="txt_link_drive_cad")

        with sub_tab_contato:
            opts_chat = ["Ativado", "Desativado", "Não Configurado"]
            c_c1, c_c2 = st.columns(2, gap="large")
            with c_c1:
                telefone_contato = st.text_input("Número de Telefone Comercial", value=dados_existentes.get("telefone_contato", "") if modo_edicao else "", key="txt_tel_cad")
                whatsapp = st.text_input("WhatsApp para Atendimento", value=dados_existentes.get("whatsapp", "") if modo_edicao else "", key="txt_wsp_cad")
                website = st.text_input("Website / Link Principal", value=dados_existentes.get("website", "") if modo_edicao else "", key="txt_web_cad")
                
                chat_val = dados_existentes.get("chat_status", "Ativado") if modo_edicao else "Ativado"
                idx_chat = opts_chat.index(chat_val) if chat_val in opts_chat else 0
                chat_status = st.radio("Mensagens / Chat no Perfil", opts_chat, index=idx_chat, horizontal=True, key="rad_chat_cad")
            with c_c2:
                instagram = st.text_input("Link do Instagram", value=dados_existentes.get("instagram", "") if modo_edicao else "", key="txt_ig_cad")
                facebook = st.text_input("Link do Facebook", value=dados_existentes.get("facebook", "") if modo_edicao else "", key="txt_fb_cad")
                linkedin = st.text_input("Link do LinkedIn", value=dados_existentes.get("linkedin", "") if modo_edicao else "", key="txt_li_cad")
                youtube = st.text_input("Link do YouTube", value=dados_existentes.get("youtube", "") if modo_edicao else "", key="txt_yt_cad")
                tiktok = st.text_input("Link do TikTok", value=dados_existentes.get("tiktok", "") if modo_edicao else "", key="txt_tk_cad")

        with sub_tab_local:
            atend_val = bool(dados_existentes.get("atendimento_local_cliente", 0)) if modo_edicao else False
            atendimento_local_cliente = st.checkbox("📍 Atendimento no local do cliente", value=atend_val, key="chk_atend_local_cad")
            st.markdown("---")
            c_l1, c_l2 = st.columns(2, gap="large")
            with c_l1:
                endereco_local = st.text_input("Endereço Físico Completo", value=dados_existentes.get("endereco_local", "") if modo_edicao else "", key="txt_end_cad")
            with c_l2:
                area_cobertura = st.text_input("Áreas de Cobertura", value=dados_existentes.get("area_cobertura", "") if modo_edicao else "", key="txt_area_cad")

        with sub_tab_horario:
            st.markdown("**Horários de Funcionamento:**")
            dias_semana = [
                ("Segunda-feira", "horario_seg", "08:00", "18:00", False),
                ("Terça-feira", "horario_ter", "08:00", "18:00", False),
                ("Quarta-feira", "horario_qua", "08:00", "18:00", False),
                ("Quinta-feira", "horario_qui", "08:00", "18:00", False),
                ("Sexta-feira", "horario_sex", "08:00", "18:00", False),
                ("Sábado", "horario_sab", "08:00", "12:00", False),
                ("Domingo", "horario_dom", "08:00", "12:00", True)
            ]
            
            horarios_coletados = {}
            for dia_nome, campo_db, h_ab_def, h_fe_def, fechado_def in dias_semana:
                st.markdown(f"<p class='dia-destaque'>📅 {dia_nome}</p>", unsafe_allow_html=True)
                col_h1, col_h2, col_h3 = st.columns([2, 2, 1], gap="medium")
                
                is_fechado = fechado_def
                val_ab = h_ab_def
                val_fe = h_fe_def

                if modo_edicao and dados_existentes.get(campo_db):
                    txt_h = dados_existentes.get(campo_db)
                    if txt_h == "Fechado":
                        is_fechado = True
                    elif " - " in txt_h:
                        is_fechado = False
                        parts = txt_h.split(" - ")
                        if len(parts) == 2:
                            val_ab, val_fe = parts[0], parts[1]

                with col_h3:
                    fechado = st.checkbox("Fechado", key=f"chk_fechado_{dia_nome}", value=is_fechado)
                with col_h1:
                    h_abre_sel = st.text_input("Abertura", value=val_ab, disabled=fechado, key=f"txt_ab_{dia_nome}")
                with col_h2:
                    h_fecha_sel = st.text_input("Fechamento", value=val_fe, disabled=fechado, key=f"txt_fe_{dia_nome}")
                
                horarios_coletados[campo_db] = "Fechado" if fechado else f"{h_abre_sel} - {h_fecha_sel}"

            st.markdown("---")
            c_he1, c_he2 = st.columns(2, gap="large")
            with c_he1:
                horarios_especiais = st.text_input("Horários Especiais", value=dados_existentes.get("horarios_especiais", "") if modo_edicao else "", key="txt_hor_esp_cad")
            with c_he2:
                outros_horarios = st.text_input("Outros Horários", value=dados_existentes.get("outros_horarios", "") if modo_edicao else "", key="txt_outros_hor_cad")

        with sub_tab_mais:
            st.markdown("**Checklist de Otimização Identificadas no Diagnóstico:**")
            pendencias_salvas = dados_existentes.get("pendencias_checklist", "") if modo_edicao else ""

            col_p1, col_p2 = st.columns(2, gap="large")
            with col_p1:
                p_fita = st.checkbox("📷 Cadastrar / Atualizar Tour Virtual 360° & Fotos", value="Fotos/Tour 360°" in pendencias_salvas, key="chk_p1_cad")
                p_cat = st.checkbox("🏷️ Otimizar Categoria Principal e Categorias Secundárias", value="Categorias GMB" in pendencias_salvas, key="chk_p2_cad")
                p_desc = st.checkbox("✍️ Reescrever Descrição Comercial com SEO Local", value="Descrição SEO" in pendencias_salvas, key="chk_p3_cad")
                p_redes = st.checkbox("🔗 Vincular Perfis Sociais", value="Redes Sociais" in pendencias_salvas, key="chk_p4_cad")
            with col_p2:
                p_chat = st.checkbox("💬 Ativar e Configurar Chat", value="Chat/Mensagens" in pendencias_salvas, key="chk_p5_cad")
                p_prod = st.checkbox("🛍️ Cadastrar Produtos e/ou Serviços", value="Produtos/Serviços" in pendencias_salvas, key="chk_p6_cad")
                p_aval = st.checkbox("⭐ Gerar Link Curto para Avaliações", value="Link de Avaliações" in pendencias_salvas, key="chk_p7_cad")
                p_hor = st.checkbox("⏰ Validar Horários de Funcionamento", value="Ajuste de Horários" in pendencias_salvas, key="chk_p8_cad")

            st.markdown("---")
            observacoes_tecnicas = st.text_area("Observações Técnicas Adicionais", value=dados_existentes.get("observacoes_tecnicas", "") if modo_edicao else "", height=180, key="txt_obs_tec_cad")

        with sub_tab_historico:
            if not modo_edicao:
                st.info("O histórico de alterações ficará disponível após o primeiro cadastro da ficha.")
            else:
                st.markdown(f"**Histórico de Registros — {cliente_selecionado_menu}:**")
                res_h = supabase.table("historico_ficha").select("data_alteracao, descricao_alteracao").eq("cliente_id", c_id).order("id", desc=True).execute()
                if res_h.data:
                    df_hist = pd.DataFrame(res_h.data)
                    df_hist.columns = ["Data", "Alteração Realizada / Registro"]
                    st.dataframe(df_hist, use_container_width=True)
                else:
                    st.write("Ficha cadastrada na versão inicial.")

        st.markdown("---")
        btn_salvar = st.form_submit_button("Salvar Nova Ficha" if not modo_edicao else "Atualizar Ficha e Gravar Histórico")

        if btn_salvar and nome_empresa:
            checklist_list = []
            if p_fita: checklist_list.append("Fotos/Tour 360°")
            if p_cat: checklist_list.append("Categorias GMB")
            if p_desc: checklist_list.append("Descrição SEO")
            if p_redes: checklist_list.append("Redes Sociais")
            if p_chat: checklist_list.append("Chat/Mensagens")
            if p_prod: checklist_list.append("Produtos/Serviços")
            if p_aval: checklist_list.append("Link de Avaliações")
            if p_hor: checklist_list.append("Ajuste de Horários")
            pendencias_str = ", ".join(checklist_list) if checklist_list else "Nenhuma pendência marcada"

            payload = {
                "nome_empresa": nome_empresa,
                "responsavel": responsavel,
                "data_abertura": data_abertura_str,
                "ficha_reivindicada": ficha_reivindicada,
                "status_avaliacoes": status_avaliacoes,
                "qtd_avaliacoes_inicio": qtd_avaliacoes_inicio,
                "nota_media_inicio": nota_media_inicio,
                "qtd_fotos_inicio": qtd_fotos_inicio,
                "valor_contrato_mensal": valor_contrato_mensal,
                "dia_vencimento": dia_vencimento,
                "status_contrato": status_contrato,
                "status_respostas_avaliacoes": status_respostas_avaliacoes,
                "categoria_principal": categoria_principal,
                "categorias_secundarias": categorias_secundarias,
                "descricao_empresa": descricao_empresa,
                "telefone_contato": telefone_contato,
                "whatsapp": whatsapp,
                "chat_status": chat_status,
                "website": website,
                "instagram": instagram,
                "facebook": facebook,
                "linkedin": linkedin,
                "youtube": youtube,
                "tiktok": tiktok,
                "atendimento_local_cliente": 1 if atendimento_local_cliente else 0,
                "endereco_local": endereco_local,
                "area_cobertura": area_cobertura,
                "horario_seg": horarios_coletados["horario_seg"],
                "horario_ter": horarios_coletados["horario_ter"],
                "horario_qua": horarios_coletados["horario_qua"],
                "horario_qui": horarios_coletados["horario_qui"],
                "horario_sex": horarios_coletados["horario_sex"],
                "horario_sab": horarios_coletados["horario_sab"],
                "horario_dom": horarios_coletados["horario_dom"],
                "horarios_especiais": horarios_especiais,
                "outros_horarios": outros_horarios,
                "pendencias_checklist": pendencias_str,
                "observacoes_tecnicas": observacoes_tecnicas,
                "link_drive_midias": link_drive_midias
            }

            if not modo_edicao:
                payload["data_inicio"] = datetime.today().strftime("%Y-%m-%d")
                res_ins = supabase.table("clientes").insert(payload).execute()
                if res_ins.data:
                    novo_id = res_ins.data[0]["id"]
                    supabase.table("historico_ficha").insert({
                        "cliente_id": novo_id,
                        "data_alteracao": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "descricao_alteracao": f"Cadastro Inicial da Ficha (Mensalidade R$ {valor_contrato_mensal:.2f})"
                    }).execute()
                    st.success(f"Ficha comercial de '{nome_empresa}' cadastrada com sucesso no Supabase!")
            else:
                supabase.table("clientes").update(payload).eq("id", c_id).execute()
                supabase.table("historico_ficha").insert({
                    "cliente_id": c_id,
                    "data_alteracao": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "descricao_alteracao": f"Atualização Ficha e Contrato (Mensalidade: R$ {valor_contrato_mensal:.2f})"
                }).execute()
                st.success(f"Ficha comercial de '{nome_empresa}' atualizada no Supabase!")
            
            st.rerun()

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 2: AUDITORIA EXPRESS DE FICHA GOOGLE
# ==========================================
elif st.session_state["aba_ativa"] == "auditoria":
    st.subheader("🔍 Auditoria de Ficha Google em 1 Clique (Diagnóstico de Vendas)")
    st.caption("Cole o link público do Google Maps da empresa para identificar falhas no perfil e gerar argumentos de vendas instantâneos.")

    url_prospect = st.text_input("Cole aqui a URL do Google Maps da Empresa Prospect:", placeholder="https://maps.google.com/...", key="txt_url_auditoria")

    if st.button("⚡ Executar Varredura da Ficha", key="btn_rodar_auditoria"):
        if url_prospect:
            with st.spinner("Analisando presença digital e elementos da ficha no Google..."):
                resultado, erro = auditar_ficha_google(url_prospect)
                
                if erro:
                    st.error(erro)
                else:
                    st.markdown("---")
                    st.markdown(f"### 🏢 Diagnóstico da Ficha: **{resultado['nome']}**")
                    
                    score = resultado['score']
                    if score >= 75:
                        st.success(f"🏆 **Pontuação da Ficha (Health Score): {score}%** — Ficha com bom preenchimento inicial.")
                    elif score >= 50:
                        st.warning(f"⚠️ **Pontuação da Ficha (Health Score): {score}%** — Presença intermediária com falhas de SEO.")
                    else:
                        st.error(f"🚨 **Pontuação da Ficha (Health Score): {score}%** — Ficha crítica, necessita intervenção profissional urgente.")

                    a1, a2, a3, a4 = st.columns(4, gap="medium")
                    a1.metric("Website Vinculado", "✅ Sim" if resultado['has_site'] else "❌ Ausente")
                    a2.metric("Telefone / Whats", "✅ Sim" if resultado['has_phone'] else "❌ Ausente")
                    a3.metric("Avaliações Destacadas", "✅ Sim" if resultado['has_reviews'] else "⚠️ Poucas/Ausente")
                    a4.metric("Fotos & Tour 360°", "✅ Sim" if resultado['has_photos'] else "⚠️ Ausente/Baixo")

                    st.markdown("---")
                    col_aud1, col_aud2 = st.columns(2, gap="large")
                    
                    with col_aud1:
                        st.markdown("### 🚨 Oportunidades & Falhas Identificadas:")
                        if resultado['pendencias']:
                            for pend in resultado['pendencias']:
                                st.write(f"- {pend}")
                        else:
                            st.write("- Nenhuma pendência crítica de infraestrutura detectada.")

                    with col_aud2:
                        st.markdown("### 💡 Argumentos Comerciais da Tour360VR:")
                        if resultado['oportunidades']:
                            for op in resultado['oportunidades']:
                                st.write(f"- {op}")
                        else:
                            st.write("- Focar em otimização contínua de Palavras-Chave e Tour Virtual 360° imersivo.")

                    st.markdown("---")
                    str_prop = f"Olá! Fiz uma análise rápida da ficha de {resultado['nome']} no Google Maps e identifiquei que existem algumas oportunidades para melhorar seu posicionamento e atrair mais clientes na região. Podemos conversar a respeito?"
                    url_enc_prop = urllib.parse.quote(str_prop)
                    st.markdown(f'<a href="https://wa.me/?text={url_enc_prop}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#2563EB; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📱 Compartilhar Abordagem de Vendas no WhatsApp</button></a>', unsafe_allow_html=True)
        else:
            st.warning("Insira uma URL válida do Google Maps antes de iniciar a varredura.")

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 3: INSERIR MÉTRICAS MENSAIS, RANKING SEO & ROI
# ==========================================
elif st.session_state["aba_ativa"] == "metricas":
    st.subheader("📋 Métricas Mensais, SEO Local & ROI")
    df_clientes = obter_clientes_unicos()
    
    if df_clientes.empty:
        st.warning("Nenhum cliente cadastrado. Cadastre um cliente na aba '⚙️ Ficha Comercial'.")
    else:
        cliente_sel = st.selectbox("Selecione o Cliente para Lançamento", df_clientes["nome_empresa"].tolist(), key="sel_cli_metricas")
        cliente_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_sel]["id"].values[0])

        tab_m1, tab_m2 = st.tabs(["📊 Métricas Mensais & ROI", "🎯 Posição de Palavras-Chave (SEO Local)"])

        with tab_m1:
            with st.form("form_metricas"):
                mes_referencia = st.date_input("Mês de Referência", value=datetime.today(), key="dt_ref_metricas").strftime("%Y-%m")

                st.markdown("---")
                st.markdown("**1. KPIs do Período (Extraídos da Ficha Google):**")
                c1, c2, c3, c4 = st.columns(4, gap="medium")
                with c1:
                    chamadas = st.number_input("📞 Chamadas Telefónicas", min_value=0, step=1, key="num_chamadas_m")
                with c2:
                    rotas = st.number_input("🗺️ Solicitações de Rota", min_value=0, step=1, key="num_rotas_m")
                with c3:
                    cliques_site = st.number_input("🌐 Cliques no Site/WhatsApp", min_value=0, step=1, key="num_cliques_m")
                with c4:
                    visualizacoes = st.number_input("👁️ Total de Visualizações", min_value=0, step=1, key="num_vis_m")

                col_m1, col_m2 = st.columns(2, gap="large")
                with col_m1:
                    novas_avaliacoes = st.number_input("⭐ Novas Avaliações Recebidas no Mês", min_value=0, step=1, key="num_novas_aval_m")
                with col_m2:
                    total_fotos_mes = st.number_input("📷 Total de Fotos Publicadas na Ficha", min_value=0, step=1, key="num_tot_fotos_m")

                st.markdown("---")
                st.markdown("**2. Calculadora de ROI e Faturamento Estimado:**")
                col_r1, col_r2 = st.columns(2, gap="large")
                with col_r1:
                    ticket_medio = st.number_input("Ticket Médio do Cliente (R$)", min_value=0.0, value=150.0, step=10.0, key="num_tm_m")
                with col_r2:
                    taxa_conversao = st.number_input("Taxa de Conversão Estimada (%)", min_value=1.0, max_value=100.0, value=10.0, step=1.0, key="num_tc_m") / 100.0

                conversoes_totais = chamadas + rotas + cliques_site
                faturamento_estimado = conversoes_totais * taxa_conversao * ticket_medio
                st.info(f"💰 **Faturamento Estimado Gerado no Mês:** R$ {faturamento_estimado:,.2f}")

                st.markdown("---")
                resumo_acoes = st.text_area("🛠️ Ações Realizadas no Mês", key="txt_resumo_acoes_m")

                btn_salvar_metricas = st.form_submit_button("Salvar Métricas do Mês")

                if btn_salvar_metricas:
                    supabase.table("metricas_mensais").insert({
                        "cliente_id": cliente_id,
                        "mes_ano": mes_referencia,
                        "chamadas": chamadas,
                        "rotas": rotas,
                        "cliques_site": cliques_site,
                        "visualizacoes": visualizacoes,
                        "novas_avaliacoes": novas_avaliacoes,
                        "total_fotos_mes": total_fotos_mes,
                        "ticket_medio": ticket_medio,
                        "taxa_conversao": taxa_conversao,
                        "faturamento_estimado": faturamento_estimado,
                        "resumo_acoes": resumo_acoes
                    }).execute()
                    st.success(f"Métricas salvas para {cliente_sel} no período {mes_referencia}!")

        with tab_m2:
            st.markdown("**Monitoramento de Palavras-Chave no Google Maps (Ranking SEO Local):**")
            res_kw = supabase.table("ranking_keywords").select("id, palavra_chave, posicao_inicial, posicao_atual").eq("cliente_id", cliente_id).execute()
            if res_kw.data:
                df_kw = pd.DataFrame(res_kw.data)
                df_kw.columns = ["ID", "Palavra-Chave", "Posição Inicial", "Posição Atual"]
                st.dataframe(df_kw, use_container_width=True)

            with st.form("form_add_keyword"):
                col_k1, col_k2, col_k3 = st.columns(3, gap="medium")
                with col_k1:
                    kw_texto = st.text_input("Nova Palavra-Chave", key="txt_kw_add")
                with col_k2:
                    kw_pos_in = st.number_input("Posição Inicial no Maps", min_value=1, value=10, key="num_kw_ini")
                with col_k3:
                    kw_pos_at = st.number_input("Posição Atual no Maps", min_value=1, value=3, key="num_kw_at")
                
                btn_kw = st.form_submit_button("Cadastrar / Atualizar Termo de Busca")

                if btn_kw and kw_texto:
                    supabase.table("ranking_keywords").insert({
                        "cliente_id": cliente_id,
                        "palavra_chave": kw_texto,
                        "posicao_inicial": kw_pos_in,
                        "posicao_atual": kw_pos_at,
                        "data_atualizacao": datetime.now().strftime("%Y-%m-%d")
                    }).execute()
                    st.success(f"Palavra-chave '{kw_texto}' registrada no ranking!")
                    st.rerun()

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 4: CURATORIA, PAUTAS E QR CODE PERMANENTE
# ==========================================
elif st.session_state["aba_ativa"] == "ia":
    st.subheader("🎯 Curadoria Estratégica, QR Code Permanente & Pautas Digitais")
    df_clientes = obter_clientes_unicos()

    if df_clientes.empty:
        st.info("Cadastre um cliente na aba '⚙️ Ficha Comercial' para liberar este módulo.")
    else:
        cliente_ia_sel = st.selectbox("Selecione o Cliente para Curadoria de Conteúdo:", df_clientes["nome_empresa"].tolist(), key="sel_cli_curadoria")
        cliente_ia_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_ia_sel]["id"].values[0])
        dados_c = obter_dados_cliente_por_id(cliente_ia_id)

        cat_nome = dados_c.get("categoria_principal", "serviços especializados")
        cid_nome = dados_c.get("area_cobertura", "região local")
        emp_nome = dados_c.get("nome_empresa", "Empresa")

        tab_ia1, tab_ia2, tab_ia3, tab_ia4, tab_ia5 = st.tabs([
            "✍️ Respostas de Avaliações", 
            "📅 Cronograma Mensal & Pautas", 
            "📱 QR Code Permanente (Balcão)", 
            "❓ Perguntas Frequentes (FAQ)", 
            "🎨 Direção de Arte Visuais"
        ])

        with tab_ia1:
            st.markdown("**Gestão de Reputação & Respostas Profissionais para Avaliações:**")
            avaliacao_recebida = st.text_area("Cole aqui a avaliação deixada pelo cliente no Google Maps:", key="txt_aval_recebida")
            
            if st.button("✨ Gerar Opções de Resposta Consultivas", key="btn_gerar_resp_aval"):
                if avaliacao_recebida:
                    st.success("Opções estruturadas prontas para uso:")
                    st.markdown(f"""
                    **Opção 1 (Agradecida & Curta):**  
                    > *"Olá! Muito obrigado pela avaliação e preferência na {emp_nome}. É um prazer oferecer a melhor experiência em {cat_nome} na nossa região. Conte sempre conosco!"*

                    **Opção 2 (Foco em SEO & Posicionamento Local):**  
                    > *"Ficamos muito felizes com o seu feedback! Na {emp_nome}, nos dedicamos diariamente para ser referência em {cat_nome} em {cid_nome}. Esperamos sua próxima visita!"*

                    **Opção 3 (Institucional & Relacionamento):**  
                    > *"Agradecemos por compartilhar sua experiência positiva! Sua satisfação é nossa prioridade. Um abraço de toda a equipe da {emp_nome}!"*
                    """)
                else:
                    st.warning("Cole o texto da avaliação antes de gerar as opções.")

        with tab_ia2:
            st.markdown(f"**Cronograma de Atração Local e Pautas Estratégicas — {emp_nome}:**")
            st.caption(f"Segmento Comercial: {cat_nome} | Região de Atendimento: {cid_nome}")

            st.markdown("### 📌 Pautas Recomendadas pela Curadoria Técnica:")
            st.checkbox(f"Pauta 1 (Intenção de Busca): 'Como escolher o melhor serviço de {cat_nome} em {cid_nome}?'", value=True, key="chk_p1_cron")
            st.checkbox(f"Pauta 2 (Diferencial & Estrutura 360°): 'Conheça o espaço da {emp_nome} em Tour Virtual 360°'", value=True, key="chk_p2_cron")
            st.checkbox(f"Pauta 3 (Atendimento Direto): 'Atendimento rápido e orçamentos pelo WhatsApp da {emp_nome}'", value=True, key="chk_p3_cron")

            st.markdown("---")
            st.markdown("### ✍️ Oportunidades & Sugestões Personalizadas do Rubens (Okamoto Mídias Visuais):")
            sug_1 = st.text_input("Sugestão Personalizada 1:", value=f"Ação Especial de Destaque: Bastidores do atendimento na {emp_nome}", key="txt_sug_pers_1")
            sug_2 = st.text_input("Sugestão Personalizada 2:", value=f"Diferencial Técnico em {cat_nome} exclusivo na região de {cid_nome}", key="txt_sug_pers_2")
            sug_3 = st.text_input("Sugestão Personalizada 3:", value="Apresentação de fotos em alta resolução da equipe e estrutura", key="txt_sug_pers_3")

            st.markdown("---")
            c_act1, c_act2 = st.columns(2, gap="large")
            with c_act1:
                if st.button("🚀 Confirmar Cronograma Estratégico", key="btn_confirmar_crono"):
                    st.success("Cronograma aprovado!")

            with c_act2:
                num_wsp_c = dados_c.get("whatsapp", "")
                num_limpo_c = "".join([c for c in num_wsp_c if c.isdigit()])
                
                resp_nome = dados_c.get("responsavel") if dados_c.get("responsavel") else emp_nome
                msg_pautas_wsp = f"Olá {resp_nome}, tudo bem? Aqui é o Rubens da Okamoto Mídias Visuais / Tour360VR! Montei o planejamento de pautas estratégicas do seu perfil para este mês, focado em atrair novos clientes na região. Por favor, confira as ideias propostas e me avise se aprova!"
                msg_enc_pautas = urllib.parse.quote(msg_pautas_wsp)

                if num_limpo_c:
                    link_wsp_pautas = f"https://wa.me/55{num_limpo_c}?text={msg_enc_pautas}"
                    st.markdown(f'<a href="{link_wsp_pautas}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#16A34A; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold; cursor:pointer;">📱 Enviar Pautas para Aprovação via WhatsApp</button></a>', unsafe_allow_html=True)
                else:
                    st.info("Cadastre o WhatsApp do cliente para enviar o link direto de aprovação.")

        with tab_ia3:
            st.markdown(f"**Gerador de QR Code Permanente (Limpo & Alta Definição) — {emp_nome}:**")
            url_def_review = dados_c.get("website", "https://maps.google.com")
            url_qr = st.text_input("Link Direto da Ficha / Página de Avaliação no Google Maps:", value=url_def_review, key="txt_url_qr_perm")

            if url_qr:
                buf_qr = gerar_qr_code_limpo(url_qr)
                col_q1, col_q2 = st.columns([1, 2], gap="large")
                with col_q1:
                    st.image(buf_qr, caption=f"QR Code Oficial — {emp_nome}", width=220)
                with col_q2:
                    st.markdown("""
                    ### 📌 Especificações para Impressão da Plaquinha:
                    * **Tipo:** QR Code Estático Direto (Nunca Expira).
                    * **Compatibilidade:** Funciona com qualquer câmera de smartphone Android ou iOS.
                    * **Formatos Sugeridos:** Placa de acrílico de mesa (10x15cm), adesivos para balcão ou cartões.
                    """)
                    st.download_button(
                        label="📥 Baixar QR Code Limpo Alta Resolução (PNG)",
                        data=buf_qr,
                        file_name=f"QRCode_Google_Review_{emp_nome.replace(' ', '_')}.png",
                        mime="image/png",
                        key="btn_dl_qr_png"
                    )

        with tab_ia4:
            st.markdown(f"**Estruturação de Perguntas Frequentes (FAQ Estratégico) — {emp_nome}:**")
            st.markdown(f"""
            ### 📋 Pares de Perguntas e Respostas Institucionais:

            **1. Pergunta:** *Qual é a localização e horário de funcionamento da {emp_nome}?*  
            > **Resposta:** A **{emp_nome}** está localizada em {dados_c.get("endereco_local", cid_nome)}. Nosso horário de atendimento é de Segunda a Sexta das 08h às 18h.

            **2. Pergunta:** *Quais serviços são oferecidos pela {emp_nome}?*  
            > **Resposta:** Somos especializados em **{cat_nome}**, oferecendo soluções personalizadas para clientes em {cid_nome}.

            **3. Pergunta:** *É possível fazer um Tour Virtual 360° ou ver fotos do local?*  
            > **Resposta:** Sim! O perfil oficial da **{emp_nome}** no Google conta com fotos atualizadas e Tour Virtual 360° interativo.
            """)

        with tab_ia5:
            st.markdown(f"**Direção de Arte & Prompts Fotográficos — {emp_nome}:**")
            prompt_gerado = f"Professional commercial photography of a modern {cat_nome} establishment named '{emp_nome}', located in Brazil. High quality ambient lighting, photorealistic, elegant interior, clean design, 8k resolution --ar 16:9"
            st.code(prompt_gerado, language="text")

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 5: DASHBOARD & ROI
# ==========================================
elif st.session_state["aba_ativa"] == "dashboard":
    st.subheader("📊 Análise de Desempenho e ROI")
    df_clientes = obter_clientes_unicos()
    
    if df_clientes.empty:
        st.info("Nenhum cliente cadastrado ainda.")
    else:
        cliente_dash = st.selectbox("Selecione o Cliente para Visualizar", df_clientes["nome_empresa"].tolist(), key="dash_cliente")
        cliente_id_dash = int(df_clientes[df_clientes["nome_empresa"] == cliente_dash]["id"].values[0])
        
        res_m = supabase.table("metricas_mensais").select("*").eq("cliente_id", cliente_id_dash).order("mes_ano").execute()
        if res_m.data:
            df_metricas = pd.DataFrame(res_m.data)
            ultimas = df_metricas.iloc[-1]
            m1, m2, m3, m4 = st.columns(4, gap="medium")
            m1.metric("Chamadas (Último Mês)", ultimas["chamadas"])
            m2.metric("Rotas (Último Mês)", ultimas["rotas"])
            m3.metric("Cliques Site/Whats", ultimas["cliques_site"])
            m4.metric("Faturamento Estimado", f"R$ {ultimas['faturamento_estimado']:,.2f}")

            st.markdown("---")
            st.line_chart(df_metricas.set_index("mes_ano")[["chamadas", "rotas", "cliques_site"]])
        else:
            st.info("Ainda não existem métricas registradas para este cliente.")

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 6: GERADOR DE PDF DE PROSPECÇÃO & CASES
# ==========================================
elif st.session_state["aba_ativa"] == "cases":
    st.subheader("🏆 Gerador de Relatório Comercial de Prospecção (Cases & Prova Social)")
    
    res_c_count = supabase.table("clientes").select("id", count="exact").execute()
    qtd_c = res_c_count.count if res_c_count.count is not None else 0

    res_m_all = supabase.table("metricas_mensais").select("mes_ano, chamadas, rotas, cliques_site, faturamento_estimado").execute()
    df_m_all = pd.DataFrame(res_m_all.data) if res_m_all.data else pd.DataFrame()
    
    fat_c = df_m_all["faturamento_estimado"].sum() if not df_m_all.empty else 0.0

    df_agrupado = None
    if not df_m_all.empty:
        df_agrupado = df_m_all.groupby("mes_ano")[["chamadas", "rotas", "cliques_site"]].sum().reset_index().sort_values("mes_ano")

    res_kw = supabase.table("ranking_keywords").select("palavra_chave, posicao_inicial, posicao_atual").execute()
    df_keywords_all = pd.DataFrame(res_kw.data) if res_kw.data else None

    st.markdown("**Selecione quais informações deseja incluir no PDF:**")
    c_p1, c_p2 = st.columns(2, gap="large")
    with c_p1:
        inc_clientes = st.checkbox("Exibir Quantidade de Clientes Atendidos", value=True, key="chk_inc_cli_cases")
        inc_faturamento = st.checkbox("Exibir Faturamento Estimado Total Gerado", value=True, key="chk_inc_fat_cases")
    with c_p2:
        inc_grafico = st.checkbox("Exibir Gráfico de Crescimento Somado", value=True, key="chk_inc_graf_cases")
        inc_keywords = st.checkbox("Exibir Tabela de Casos de Sucesso SEO", value=True, key="chk_inc_kw_cases")

    st.markdown("---")

    pdf_cases_bytes = gerar_pdf_prospeccao_cases(
        inc_clientes=inc_clientes,
        inc_faturamento=inc_faturamento,
        inc_grafico=inc_grafico,
        inc_keywords=inc_keywords,
        qtd_clientes=qtd_c,
        total_fat=fat_c,
        df_agrupado=df_agrupado,
        df_keywords=df_keywords_all
    )

    st.download_button(
        label="📥 Baixar PDF Comercial de Prospecção (Tour360VR Cases)",
        data=pdf_cases_bytes,
        file_name=f"Apresentacao_Cases_Tour360VR_{datetime.now().strftime('%Y_%m')}.pdf",
        mime="application/pdf",
        key="btn_pdf_cases"
    )

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 7: RELATÓRIO PDF INDIVIDUAL & WHATSAPP
# ==========================================
elif st.session_state["aba_ativa"] == "pdf":
    st.subheader("📄 Emitir Relatório Executivo em PDF & Envio via WhatsApp")
    df_clientes = obter_clientes_unicos()

    if df_clientes.empty:
        st.info("Cadastre um cliente e insira métricas para gerar o relatório.")
    else:
        col_r1, col_r2 = st.columns(2, gap="large")
        with col_r1:
            cliente_pdf_sel = st.selectbox("Selecione o Cliente", df_clientes["nome_empresa"].tolist(), key="pdf_cliente")
            cliente_pdf_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_pdf_sel]["id"].values[0])

        dados_cliente = obter_dados_cliente_por_id(cliente_pdf_id)
        
        dados_inicio = {
            'qtd_avaliacoes_inicio': dados_cliente.get('qtd_avaliacoes_inicio', 0),
            'nota_media_inicio': dados_cliente.get('nota_media_inicio', 5.0),
            'qtd_fotos_inicio': dados_cliente.get('qtd_fotos_inicio', 0)
        }

        res_m = supabase.table("metricas_mensais").select("*").eq("cliente_id", cliente_pdf_id).order("mes_ano").execute()
        df_m = pd.DataFrame(res_m.data) if res_m.data else pd.DataFrame()

        res_kw = supabase.table("ranking_keywords").select("palavra_chave, posicao_inicial, posicao_atual").eq("cliente_id", cliente_pdf_id).execute()
        df_kw = pd.DataFrame(res_kw.data) if res_kw.data else None

        if df_m.empty:
            st.warning("Nenhuma métrica encontrada para este cliente.")
        else:
            with col_r2:
                mes_pdf_sel = st.selectbox("Selecione o Mês de Referência", df_m["mes_ano"].tolist()[::-1], key="sel_mes_pdf")

            idx_sel = df_m[df_m["mes_ano"] == mes_pdf_sel].index[0]
            dados_atual = df_m.iloc[idx_sel].to_dict()

            dados_anterior = None
            if idx_sel - 1 >= 0:
                dados_anterior = df_m.iloc[idx_sel - 1].to_dict()

            df_historico_recorte = df_m.iloc[:idx_sel + 1]

            st.markdown("---")
            st.write(f"**Resumo Selecionado:** {cliente_pdf_sel} - Mês {mes_pdf_sel}")

            pdf_bytes = gerar_pdf_relatorio(
                nome_empresa=cliente_pdf_sel,
                mes_ano=mes_pdf_sel,
                dados_atual=dados_atual,
                dados_anterior=dados_anterior,
                dados_inicio=dados_inicio,
                df_historico=df_historico_recorte,
                df_keywords=df_kw
            )

            c_dw1, c_dw2 = st.columns(2, gap="large")
            with c_dw1:
                st.download_button(
                    label="📥 Baixar Relatório Executivo em PDF (TOUR360VR)",
                    data=pdf_bytes,
                    file_name=f"Relatorio_GMB_{cliente_pdf_sel.replace(' ', '_')}_{mes_pdf_sel}.pdf",
                    mime="application/pdf",
                    key="btn_download_pdf_exec"
                )

            with c_dw2:
                num_wsp = dados_cliente.get("whatsapp", "")
                num_limpo = "".join([c for c in num_wsp if c.isdigit()])
                resp_nome = dados_cliente.get("responsavel") if dados_cliente.get("responsavel") else cliente_pdf_sel
                
                txt_whats = f"Olá {resp_nome}, tudo bem? Aqui é o Rubens da Tour360VR! Segue o resumo do relatório de desempenho do seu perfil no Google referente ao mês {mes_pdf_sel}: Tivemos {dados_atual['chamadas']} chamadas diretas e {dados_atual['rotas']} solicitações de rota no GPS. Estou enviando o relatório completo em PDF em anexo."
                txt_encoded = urllib.parse.quote(txt_whats)

                if num_limpo:
                    link_wsp = f"https://wa.me/55{num_limpo}?text={txt_encoded}"
                    st.markdown(f'<a href="{link_wsp}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#16A34A; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold; cursor:pointer;">📱 Enviar Resumo via WhatsApp</button></a>', unsafe_allow_html=True)
                else:
                    st.info("Cadastre o WhatsApp no formulário do cliente para ativar o envio rápido.")

    gerar_botoes_navegacao_rodape()

# ==========================================
# MÓDULO 8: GESTÃO FINANCEIRA MRR & BACKUP COMPLETO
# ==========================================
elif st.session_state["aba_ativa"] == "financeiro":
    st.subheader("💰 Gestão Financeira & Backup da Agência (MRR)")
    st.caption("Painel restrito para controle de mensalidades e faturamento do Supabase.")

    res_cli = supabase.table("clientes").select("*").order("nome_empresa").execute()
    df_completo = pd.DataFrame(res_cli.data) if res_cli.data else pd.DataFrame()

    if df_completo.empty:
        st.info("Nenhum contrato cadastrado no momento.")
    else:
        df_fin = df_completo[df_completo["status_contrato"] == "Ativo"][["nome_empresa", "responsavel", "telefone_contato", "valor_contrato_mensal", "dia_vencimento", "status_contrato"]]
        df_fin.columns = ["Cliente", "Responsável", "Telefone", "Mensalidade (R$)", "Dia Vencimento", "Status"]

        mrr_total = df_fin['Mensalidade (R$)'].sum()
        qtd_clientes_ativos = len(df_fin)
        ticket_medio_agencia = mrr_total / qtd_clientes_ativos if qtd_clientes_ativos > 0 else 0.0

        f1, f2, f3 = st.columns(3, gap="large")
        f1.metric("💵 Recorrência Mensal (MRR)", f"R$ {mrr_total:,.2f}")
        f2.metric("🏢 Clientes Ativos", f"{qtd_clientes_ativos} empresas")
        f3.metric("🎯 Ticket Médio por Cliente", f"R$ {ticket_medio_agencia:,.2f}")

        st.markdown("---")
        st.markdown("**Contratos Recorrentes Ativos:**")
        st.dataframe(df_fin, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📥 Backup & Exportação Completa de Cadastros")
        csv_excel = df_completo.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')

        st.download_button(
            label="📊 Baixar Planilha Completa (.CSV / Excel)",
            data=csv_excel,
            file_name=f"Backup_Clientes_Tour360VR_{datetime.now().strftime('%Y_%m_%d')}.csv",
            mime="text/csv",
            key="btn_download_excel"
        )

    gerar_botoes_navegacao_rodape()

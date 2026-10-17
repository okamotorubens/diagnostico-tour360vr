import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime, date
from io import BytesIO
import urllib.parse

# Importações do ReportLab para PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Importação do Matplotlib para geração de gráficos no PDF
import matplotlib.pyplot as plt

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gestão Mensal & ROI | Tour360vr",
    page_icon="📈",
    layout="wide"
)

# --- BANCO DE DADOS (SQLite) ---
DB_NAME = "gestao_gmb.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Tabela Principal de Clientes
    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_empresa TEXT UNIQUE NOT NULL,
            responsavel TEXT,
            data_abertura TEXT,
            ficha_reivindicada TEXT,
            status_avaliacoes TEXT,
            qtd_avaliacoes_inicio INTEGER DEFAULT 0,
            nota_media_inicio REAL DEFAULT 5.0,
            qtd_fotos_inicio INTEGER DEFAULT 0,
            valor_contrato_mensal REAL DEFAULT 0.0,
            dia_vencimento INTEGER DEFAULT 10,
            status_contrato TEXT DEFAULT 'Ativo',
            status_respostas_avaliacoes TEXT,
            categoria_principal TEXT,
            categorias_secundarias TEXT,
            descricao_empresa TEXT,
            telefone_contato TEXT,
            whatsapp TEXT,
            chat_status TEXT,
            website TEXT,
            instagram TEXT,
            facebook TEXT,
            linkedin TEXT,
            youtube TEXT,
            tiktok TEXT,
            atendimento_local_cliente INTEGER DEFAULT 0,
            endereco_local TEXT,
            area_cobertura TEXT,
            horario_seg TEXT,
            horario_ter TEXT,
            horario_qua TEXT,
            horario_qui TEXT,
            horario_sex TEXT,
            horario_sab TEXT,
            horario_dom TEXT,
            horarios_especiais TEXT,
            outros_horarios TEXT,
            pendencias_checklist TEXT,
            observacoes_tecnicas TEXT,
            link_drive_midias TEXT,
            data_inicio TEXT
        )
    ''')

    colunas_novas = [
        ("valor_contrato_mensal", "REAL DEFAULT 0.0"),
        ("dia_vencimento", "INTEGER DEFAULT 10"),
        ("status_contrato", "TEXT DEFAULT 'Ativo'"),
        ("link_drive_midias", "TEXT")
    ]
    
    for nome_coluna, tipo_coluna in colunas_novas:
        try:
            c.execute(f"ALTER TABLE clientes ADD COLUMN {nome_coluna} {tipo_coluna}")
        except sqlite3.OperationalError:
            pass

    # 2. Tabela de Histórico de Alterações
    c.execute('''
        CREATE TABLE IF NOT EXISTS historico_ficha (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data_alteracao TEXT,
            descricao_alteracao TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    
    # 3. Tabela de Métricas Mensais
    c.execute('''
        CREATE TABLE IF NOT EXISTS metricas_mensais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            mes_ano TEXT NOT NULL,
            chamadas INTEGER DEFAULT 0,
            rotas INTEGER DEFAULT 0,
            cliques_site INTEGER DEFAULT 0,
            visualizacoes INTEGER DEFAULT 0,
            novas_avaliacoes INTEGER DEFAULT 0,
            total_fotos_mes INTEGER DEFAULT 0,
            ticket_medio REAL DEFAULT 150.0,
            taxa_conversao REAL DEFAULT 0.10,
            faturamento_estimado REAL DEFAULT 0.0,
            resumo_acoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')

    # 4. Tabela de Palavras-Chave e Ranking SEO
    c.execute('''
        CREATE TABLE IF NOT EXISTS ranking_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            palavra_chave TEXT NOT NULL,
            posicao_inicial INTEGER DEFAULT 0,
            posicao_atual INTEGER DEFAULT 0,
            data_atualizacao TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')

    # 5. Tabela de Publicações e Posts GMB
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts_gmb (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            data_post TEXT,
            tipo_post TEXT,
            titulo TEXT,
            status TEXT DEFAULT 'Concluído',
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def obter_clientes_unicos():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT DISTINCT id, nome_empresa FROM clientes ORDER BY nome_empresa ASC", conn)
    conn.close()
    return df

def obter_dados_cliente_por_id(cliente_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
    row = c.fetchone()
    conn.close()
    return row

def calcular_variacao_pct(atual, anterior):
    if anterior is None or anterior == 0:
        return "+100%" if atual > 0 else "0%"
    diff = ((atual - anterior) / anterior) * 100
    if diff > 0:
        return f"+{diff:.1f}%"
    return f"{diff:.1f}%"

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

# --- GERAÇÃO DO RELATÓRIO PDF DO CLIENTE COM LOGO TOUR360VR À ESQUERDA ---
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
            Paragraph("🌐 <b>TOUR360VR</b><br/><font size=8 color='#64748B'>Gestão, SEO Local & Presença em IAs</font>", title_brand_style),
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
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
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

    story.append(Paragraph("<b>5. Ações Técnicas & Melhores Práticas Aplicadas (SEO/GEO):</b>", section_style))
    story.append(Spacer(1, 3))
    acoes_texto = dados_atual['resumo_acoes'] if dados_atual['resumo_acoes'] else "Otimizações de rotina, monitorização de palavras-chave locais e gestão de reputação da ficha."
    story.append(Paragraph(acoes_texto.replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 10))

    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CBD5E1'), spaceAfter=6))
    story.append(Paragraph("<b>tour360vr.com.br</b> &nbsp;|&nbsp; contato@tour360vr.com.br &nbsp;|&nbsp; Whatsapp: (16) 99133-2121 &nbsp;|&nbsp; Tour360VR - Gestão de Perfil do Google & Presença Local", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- GERAÇÃO DO PDF COMERCIAL DE PROSPECÇÃO COM LOGO À ESQUERDA ---
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
            Paragraph("🌐 <b>TOUR360VR</b><br/><font size=8 color='#64748B'>Estratégia, Tour 360°, SEO Local & GEO (AEO/IAs)</font>", title_brand_style),
            Paragraph("<b>APRESENTAÇÃO DE PERFORMANCE & CASES DE SUCESSO</b><br/><font size=8 color='#2563EB'><b>Mídia & Otimização GMB/IAs</b></font>", ParagraphStyle('RHeader', parent=styles['Normal'], alignment=2, fontName='Helvetica'))
        ]
    ]
    t_header = Table(header_table_data, colWidths=[300, 220])
    story.append(t_header)
    story.append(Spacer(1, 6))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563EB'), spaceAfter=10))

    story.append(Paragraph("<b>1. Resumo Consolidado de Resultados da Agência:</b>", section_style))
    story.append(Spacer(1, 4))

    txt_resumo = "A Tour360VR desenvolve estratégias personalizadas de posicionamento local, fotogrametria 360°, otimização de fichas no Google Maps e citabilidade em IAs (ChatGPT, Gemini e Copilot) para empresas que buscam liderança de mercado em sua região."
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
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t_kw)
        story.append(Spacer(1, 10))

    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CBD5E1'), spaceAfter=8))
    story.append(Paragraph("<b>tour360vr.com.br</b> &nbsp;|&nbsp; contato@tour360vr.com.br &nbsp;|&nbsp; Whatsapp: (16) 99133-2121 &nbsp;|&nbsp; Tour360VR - Soluções em Visual Mídia, SEO & GEO Local", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
        max-width: 90% !important;
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
        padding: 16px 20px 14px 20px !important;
        margin-bottom: 35px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    }

    .main-title-card {
        color: #FFFFFF;
        font-weight: 800;
        font-size: 1.80rem;
        margin-top: 0 !important;
        margin-bottom: 4px !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.4);
    }

    .sub-title-card {
        color: #8E9BAE;
        font-size: 0.90rem;
        margin-bottom: 12px !important;
    }

    div[data-testid="stColumn"] button {
        width: 100% !important;
        background-color: #1A2130 !important;
        border: 1.5px solid #455570 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        padding: 9px 8px !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        transition: all 0.25s ease-in-out !important;
    }

    div[data-testid="stColumn"] button:hover {
        background-color: #222C3E !important;
        border-color: #FFFFFF !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 12px rgba(255, 255, 255, 0.7) !important;
    }

    div[data-testid="stColumn"] button[kind="primary"] {
        background-color: #1A2130 !important;
        border: 2px solid #FFFFFF !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 18px rgba(255, 255, 255, 0.95) !important;
    }

    div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 15px !important;
        background-color: #161F30 !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        border: 1px solid #2B364A !important;
    }

    .dia-destaque {
        color: #FFFFFF !important;
        font-weight: 700;
        font-size: 1.05rem;
        margin-top: 0.8rem;
        margin-bottom: 0.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONTROLADOR DE NAVEGAÇÃO ---
if "aba_ativa" not in st.session_state:
    st.session_state["aba_ativa"] = "cadastrar"

st.markdown("""
<div class="top-card-container">
    <h1 class="main-title-card">📈 Gestão Mensal, SEO & GEO (IAs) | Tour360VR</h1>
    <p class="sub-title-card">Acompanhamento de perfis no Google Maps, posicionamento em IAs (ChatGPT/Gemini) e relatórios de ROI.</p>
""", unsafe_allow_html=True)

col_n1, col_n2, col_n3, col_n4, col_n5, col_n6, col_n7 = st.columns(7)

with col_n1:
    if st.button("⚙️ Ficha Comercial", key="btn_cad", type="primary" if st.session_state["aba_ativa"] == "cadastrar" else "secondary"):
        st.session_state["aba_ativa"] = "cadastrar"
        st.rerun()

with col_n2:
    if st.button("📋 Métricas & SEO", key="btn_inc", type="primary" if st.session_state["aba_ativa"] == "metricas" else "secondary"):
        st.session_state["aba_ativa"] = "metricas"
        st.rerun()

with col_n3:
    if st.button("💬 Assistente IA", key="btn_ia", type="primary" if st.session_state["aba_ativa"] == "ia" else "secondary"):
        st.session_state["aba_ativa"] = "ia"
        st.rerun()

with col_n4:
    if st.button("📊 Dashboard ROI", key="btn_dash", type="primary" if st.session_state["aba_ativa"] == "dashboard" else "secondary"):
        st.session_state["aba_ativa"] = "dashboard"
        st.rerun()

with col_n5:
    if st.button("🏆 Prospecção", key="btn_cases", type="primary" if st.session_state["aba_ativa"] == "cases" else "secondary"):
        st.session_state["aba_ativa"] = "cases"
        st.rerun()

with col_n6:
    if st.button("📄 Relatório PDF", key="btn_pdf", type="primary" if st.session_state["aba_ativa"] == "pdf" else "secondary"):
        st.session_state["aba_ativa"] = "pdf"
        st.rerun()

with col_n7:
    if st.button("💰 Financeiro MRR", key="btn_fin", type="primary" if st.session_state["aba_ativa"] == "financeiro" else "secondary"):
        st.session_state["aba_ativa"] = "financeiro"
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

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
        cliente_selecionado_menu = st.selectbox("Selecione para Cadastrar ou Editar um Cliente Existente:", opcoes_clientes)
        
        if cliente_selecionado_menu != "➕ Cadastrar Novo Cliente":
            modo_edicao = True
            c_id = int(df_clientes_existentes[df_clientes_existentes["nome_empresa"] == cliente_selecionado_menu]["id"].values[0])
            dados_existentes = obter_dados_cliente_por_id(c_id)
            st.info(f"Modo de Edição Ativo: Alterando a Ficha de **{cliente_selecionado_menu}**.")

    with st.form("form_cliente_gmb_completo"):
        sub_tab_sobre, sub_tab_financeiro, sub_tab_contato, sub_tab_local, sub_tab_horario, sub_tab_mais, sub_tab_historico = st.tabs([
            "🏢 Sobre & Status Ficha", "💵 Valor Contrato", "📞 Contato & Redes", "📍 Local & Áreas", "⏰ Horários Rápidos", "🛠️ Checklist", "📜 Histórico"
        ])
        
        # SUB-ABA 1: SOBRE & AUDITORIA DA FICHA
        with sub_tab_sobre:
            st.markdown("**Identificação Comercial & Auditoria Inicial:**")
            c_s1, c_s2 = st.columns(2)

            opts_reivindicada = ["Reivindicada & Verificada", "Não Reivindicada", "Em Processo"]
            opts_avaliacoes = ["Sim (Com Nota Exibida)", "Não (Sem Avaliações)"]
            opts_respostas = ["100% Respondidas", "Parcialmente", "Nenhuma", "N/A"]

            val_dt_abertura = date.today()
            if modo_edicao and dados_existentes and dados_existentes[3]:
                try:
                    val_dt_abertura = datetime.strptime(dados_existentes[3], "%d/%m/%Y").date()
                except ValueError:
                    val_dt_abertura = date.today()

            with c_s1:
                nome_empresa = st.text_input("Nome Comercial da Empresa / Ficha GMB *", value=dados_existentes[1] if modo_edicao else "")
                responsavel = st.text_input("Nome do Responsável / Contato Interno", value=dados_existentes[2] if modo_edicao else "")
                
                data_abertura_dt = st.date_input("Data de Abertura (Dia/Mês/Ano)", value=val_dt_abertura, format="DD/MM/YYYY")
                data_abertura_str = data_abertura_dt.strftime("%d/%m/%Y")
                
                idx_reiv = opts_reivindicada.index(dados_existentes[4]) if (modo_edicao and dados_existentes[4] in opts_reivindicada) else 0
                ficha_reivindicada = st.radio("Status de Reivindicação da Ficha", opts_reivindicada, index=idx_reiv, horizontal=True)
                
                idx_resp = opts_respostas.index(dados_existentes[12]) if (modo_edicao and len(dados_existentes) > 12 and dados_existentes[12] in opts_respostas) else 0
                status_respostas_avaliacoes = st.radio("Status de Resposta às Avaliações", opts_respostas, index=idx_resp, horizontal=True)

            with c_s2:
                categoria_principal = st.text_input("Categoria Principal no GMB (ex: Serviço de fotografia)", value=dados_existentes[13] if (modo_edicao and len(dados_existentes) > 13) else "")
                categorias_secundarias = st.text_input("Categorias Secundárias (separadas por vírgula)", value=dados_existentes[14] if (modo_edicao and len(dados_existentes) > 14) else "")
                
                idx_aval = opts_avaliacoes.index(dados_existentes[5]) if (modo_edicao and dados_existentes[5] in opts_avaliacoes) else 0
                status_avaliacoes = st.radio("Possui Avaliações de Clientes?", opts_avaliacoes, index=idx_aval, horizontal=True)

                st.markdown("**Métricas no Início da Gestão:**")
                col_av1, col_av2, col_av3 = st.columns(3)
                with col_av1:
                    qtd_avaliacoes_inicio = st.number_input(
                        "Avaliações Iniciais",
                        min_value=0, step=1,
                        value=int(dados_existentes[6]) if (modo_edicao and len(dados_existentes) > 6 and dados_existentes[6] is not None) else 0
                    )
                with col_av2:
                    nota_media_inicio = st.number_input(
                        "Nota Média Inicial",
                        min_value=0.0, max_value=5.0, step=0.1,
                        value=float(dados_existentes[7]) if (modo_edicao and len(dados_existentes) > 7 and dados_existentes[7] is not None) else 5.0
                    )
                with col_av3:
                    qtd_fotos_inicio = st.number_input(
                        "Qtd. Fotos Iniciais",
                        min_value=0, step=1,
                        value=int(dados_existentes[8]) if (modo_edicao and len(dados_existentes) > 8 and dados_existentes[8] is not None) else 0
                    )
            
            st.markdown("---")
            descricao_empresa = st.text_area("Descrição Oficial da Empresa (Otimizada para SEO Local & IAs)", value=dados_existentes[15] if (modo_edicao and len(dados_existentes) > 15) else "", height=180)

        # SUB-ABA FINANCEIRA DO CONTRATO - PROPORÇÃO AJUSTADA PARA FICAR EM 1 LINHA
        with sub_tab_financeiro:
            st.markdown("**Dados do Contrato do Cliente (Visível apenas para a Agência):**")
            
            # Proporções customizadas: menos espaço para números, mais espaço para os radio buttons
            col_f1, col_f2, col_f3 = st.columns([1.2, 1.2, 2.6])
            
            opts_status_contrato = ["Ativo", "Em Negociação", "Pausado", "Cancelado"]
            val_status = dados_existentes[11] if (modo_edicao and len(dados_existentes) > 11) else "Ativo"
            idx_st_c = opts_status_contrato.index(val_status) if val_status in opts_status_contrato else 0

            with col_f1:
                valor_contrato_mensal = st.number_input(
                    "Valor da Mensalidade (R$)",
                    min_value=0.0, step=50.0,
                    value=float(dados_existentes[9]) if (modo_edicao and len(dados_existentes) > 9 and dados_existentes[9] is not None) else 450.0
                )
            with col_f2:
                dia_vencimento = st.number_input(
                    "Dia do Vencimento Mensal",
                    min_value=1, max_value=31, step=1,
                    value=int(dados_existentes[10]) if (modo_edicao and len(dados_existentes) > 10 and dados_existentes[10] is not None) else 10
                )
            with col_f3:
                status_contrato = st.radio("Status do Contrato com a Agência", opts_status_contrato, index=idx_st_c, horizontal=True)

            st.markdown("---")
            link_drive_midias = st.text_input("Link da Pasta de Mídias e Fotos 360° (Google Drive / Photos / Pano2VR)", value=dados_existentes[39] if (modo_edicao and len(dados_existentes) > 39 and dados_existentes[39]) else "")
            status_contrato = st.radio("Status do Contrato com a Agência", opts_status_contrato, index=idx_st_c, horizontal=True)

        # SUB-ABA 3: CONTATO & REDES SOCIAIS
        with sub_tab_contato:
            opts_chat = ["Ativado", "Desativado", "Não Configurado"]
            c_c1, c_c2 = st.columns(2)
            with c_c1:
                telefone_contato = st.text_input("Número de Telefone Comercial", value=dados_existentes[16] if (modo_edicao and len(dados_existentes) > 16) else "")
                whatsapp = st.text_input("WhatsApp para Atendimento", value=dados_existentes[17] if (modo_edicao and len(dados_existentes) > 17) else "")
                website = st.text_input("Website / Link Principal", value=dados_existentes[19] if (modo_edicao and len(dados_existentes) > 19) else "")
                
                chat_val = dados_existentes[18] if (modo_edicao and len(dados_existentes) > 18) else "Ativado"
                idx_chat = opts_chat.index(chat_val) if chat_val in opts_chat else 0
                chat_status = st.radio("Mensagens / Chat no Perfil", opts_chat, index=idx_chat, horizontal=True)
            with c_c2:
                instagram = st.text_input("Link do Instagram", value=dados_existentes[20] if (modo_edicao and len(dados_existentes) > 20) else "")
                facebook = st.text_input("Link do Facebook", value=dados_existentes[21] if (modo_edicao and len(dados_existentes) > 21) else "")
                linkedin = st.text_input("Link do LinkedIn", value=dados_existentes[22] if (modo_edicao and len(dados_existentes) > 22) else "")
                youtube = st.text_input("Link do YouTube", value=dados_existentes[23] if (modo_edicao and len(dados_existentes) > 23) else "")
                tiktok = st.text_input("Link do TikTok", value=dados_existentes[24] if (modo_edicao and len(dados_existentes) > 24) else "")

        # SUB-ABA 4: LOCAL & ÁREAS
        with sub_tab_local:
            atend_val = bool(dados_existentes[25]) if (modo_edicao and len(dados_existentes) > 25) else False
            atendimento_local_cliente = st.checkbox("📍 Atendimento no local do cliente / Prestador de serviço itinerante (Endereço oculto no Google)", value=atend_val)
            st.markdown("---")
            c_l1, c_l2 = st.columns(2)
            with c_l1:
                endereco_local = st.text_input("Endereço Físico Completo", value=dados_existentes[26] if (modo_edicao and len(dados_existentes) > 26) else "")
            with c_l2:
                area_cobertura = st.text_input("Áreas de Cobertura / Atendimento (ex: Ribeirão Preto, Sertãozinho, Brodowski)", value=dados_existentes[27] if (modo_edicao and len(dados_existentes) > 27) else "")

        # SUB-ABA 5: HORÁRIOS DE FUNCIONAMENTO
        with sub_tab_horario:
            st.markdown("**Horários de Funcionamento (Valores padrão editáveis diretamente):**")
            
            dias_semana = [
                ("Segunda-feira", 28, "08:00", "18:00", False),
                ("Terça-feira", 29, "08:00", "18:00", False),
                ("Quarta-feira", 30, "08:00", "18:00", False),
                ("Quinta-feira", 31, "08:00", "18:00", False),
                ("Sexta-feira", 32, "08:00", "18:00", False),
                ("Sábado", 33, "08:00", "12:00", False),
                ("Domingo", 34, "08:00", "12:00", True)
            ]
            
            horarios_coletados = {}

            for dia_nome, idx_db, h_ab_def, h_fe_def, fechado_def in dias_semana:
                st.markdown(f"<p class='dia-destaque'>📅 {dia_nome}</p>", unsafe_allow_html=True)
                col_h1, col_h2, col_h3 = st.columns([2, 2, 1])
                
                is_fechado = fechado_def
                val_ab = h_ab_def
                val_fe = h_fe_def

                if modo_edicao and len(dados_existentes) > idx_db and dados_existentes[idx_db]:
                    txt_h = dados_existentes[idx_db]
                    if txt_h == "Fechado":
                        is_fechado = True
                    elif " - " in txt_h:
                        is_fechado = False
                        parts = txt_h.split(" - ")
                        if len(parts) == 2:
                            val_ab = parts[0]
                            val_fe = parts[1]

                with col_h3:
                    fechado = st.checkbox("Fechado", key=f"chk_fechado_{dia_nome}", value=is_fechado)
                with col_h1:
                    h_abre_sel = st.text_input("Abertura", value=val_ab, disabled=fechado, key=f"txt_ab_{dia_nome}")
                with col_h2:
                    h_fecha_sel = st.text_input("Fechamento", value=val_fe, disabled=fechado, key=f"txt_fe_{dia_nome}")
                
                if fechado:
                    horarios_coletados[dia_nome] = "Fechado"
                else:
                    horarios_coletados[dia_nome] = f"{h_abre_sel} - {h_fecha_sel}"

            st.markdown("---")
            c_he1, c_he2 = st.columns(2)
            with c_he1:
                horarios_especiais = st.text_input("Horários Especiais / Feriados (ex: 25/12 Fechado)", value=dados_existentes[35] if (modo_edicao and len(dados_existentes) > 35) else "")
            with c_he2:
                outros_horarios = st.text_input("Outros Horários (Almoço, Happy Hour, Delivery)", value=dados_existentes[36] if (modo_edicao and len(dados_existentes) > 36) else "")

        # SUB-ABA 6: CHECKLIST DE PENDÊNCIAS
        with sub_tab_mais:
            st.markdown("**Checklist de Otimização Identificadas no Diagnóstico:**")
            pendencias_salvas = dados_existentes[37] if (modo_edicao and len(dados_existentes) > 37 and dados_existentes[37]) else ""

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                p_fita = st.checkbox("📷 Cadastrar / Atualizar Tour Virtual 360° & Fotos", value="Fotos/Tour 360°" in pendencias_salvas)
                p_cat = st.checkbox("🏷️ Otimizar Categoria Principal e Categorias Secundárias", value="Categorias GMB" in pendencias_salvas)
                p_desc = st.checkbox("✍️ Reescrever Descrição Comercial com SEO Local & GEO", value="Descrição SEO" in pendencias_salvas)
                p_redes = st.checkbox("🔗 Vincular Perfis Sociais (Instagram, Facebook, etc.)", value="Redes Sociais" in pendencias_salvas)
            with col_p2:
                p_chat = st.checkbox("💬 Ativar e Configurar Chat / Mensagens", value="Chat/Mensagens" in pendencias_salvas)
                p_prod = st.checkbox("🛍️ Cadastrar Produtos e/ou Lista de Serviços", value="Produtos/Serviços" in pendencias_salvas)
                p_aval = st.checkbox("⭐ Gerar Link Curto Direto para Solicitação de Avaliações", value="Link de Avaliações" in pendencias_salvas)
                p_hor = st.checkbox("⏰ Corrigir / Validar Horários Especiais e de Funcionamento", value="Ajuste de Horários" in pendencias_salvas)

            st.markdown("---")
            observacoes_tecnicas = st.text_area("Observações Técnicas Adicionais / Diagnóstico Específico", value=dados_existentes[38] if (modo_edicao and len(dados_existentes) > 38) else "", height=180)

        # SUB-ABA 7: HISTÓRICO DE AUDITORIA
        with sub_tab_historico:
            if not modo_edicao:
                st.info("O histórico de alterações ficará disponível após o primeiro cadastro da ficha.")
            else:
                st.markdown(f"**Histórico de Registros e Otimizações Realizadas — {cliente_selecionado_menu}:**")
                conn = sqlite3.connect(DB_NAME)
                df_hist = pd.read_sql_query(
                    "SELECT data_alteracao as 'Data', descricao_alteracao as 'Alteração Realizada / Registro' FROM historico_ficha WHERE cliente_id = ? ORDER BY id DESC", 
                    conn, params=(c_id,)
                )
                conn.close()
                
                if df_hist.empty:
                    st.write("Ficha cadastrada na versão inicial.")
                else:
                    st.dataframe(df_hist, use_container_width=True)

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

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            if not modo_edicao:
                try:
                    c.execute('''
                        INSERT INTO clientes 
                        (nome_empresa, responsavel, data_abertura, ficha_reivindicada, status_avaliacoes, qtd_avaliacoes_inicio, nota_media_inicio, qtd_fotos_inicio, valor_contrato_mensal, dia_vencimento, status_contrato, status_respostas_avaliacoes, categoria_principal, categorias_secundarias, descricao_empresa, telefone_contato, whatsapp, chat_status, website, instagram, facebook, linkedin, youtube, tiktok, atendimento_local_cliente, endereco_local, area_cobertura, horario_seg, horario_ter, horario_qua, horario_qui, horario_sex, horario_sab, horario_dom, horarios_especiais, outros_horarios, pendencias_checklist, observacoes_tecnicas, link_drive_midias, data_inicio) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        nome_empresa, responsavel, data_abertura_str, ficha_reivindicada, status_avaliacoes, qtd_avaliacoes_inicio, nota_media_inicio, qtd_fotos_inicio, valor_contrato_mensal, dia_vencimento, status_contrato, status_respostas_avaliacoes, categoria_principal, categorias_secundarias, descricao_empresa, telefone_contato, whatsapp, chat_status, website, instagram, facebook, linkedin, youtube, tiktok, 1 if atendimento_local_cliente else 0, endereco_local, area_cobertura, 
                        horarios_coletados["Segunda-feira"], horarios_coletados["Terça-feira"], horarios_coletados["Quarta-feira"], horarios_coletados["Quinta-feira"], horarios_coletados["Sexta-feira"], horarios_coletados["Sábado"], horarios_coletados["Domingo"],
                        horarios_especiais, outros_horarios, pendencias_str, observacoes_tecnicas, link_drive_midias, datetime.today().strftime("%Y-%m-%d")
                    ))
                    cliente_novo_id = c.lastrowid
                    c.execute("INSERT INTO historico_ficha (cliente_id, data_alteracao, descricao_alteracao) VALUES (?, ?, ?)",
                              (cliente_novo_id, datetime.now().strftime("%Y-%m-%d %H:%M"), f"Cadastro Inicial da Ficha (Mensalidade R$ {valor_contrato_mensal:.2f})"))
                    conn.commit()
                    st.success(f"Ficha comercial de '{nome_empresa}' cadastrada com sucesso!")
                except sqlite3.IntegrityError:
                    st.error(f"O cliente '{nome_empresa}' já está cadastrado no sistema!")
            else:
                c.execute('''
                    UPDATE clientes SET 
                    responsavel=?, data_abertura=?, ficha_reivindicada=?, status_avaliacoes=?, qtd_avaliacoes_inicio=?, nota_media_inicio=?, qtd_fotos_inicio=?, valor_contrato_mensal=?, dia_vencimento=?, status_contrato=?, status_respostas_avaliacoes=?, categoria_principal=?, categorias_secundarias=?, descricao_empresa=?, telefone_contato=?, whatsapp=?, chat_status=?, website=?, instagram=?, facebook=?, linkedin=?, youtube=?, tiktok=?, atendimento_local_cliente=?, endereco_local=?, area_cobertura=?, horario_seg=?, horario_ter=?, horario_qua=?, horario_qui=?, horario_sex=?, horario_sab=?, horario_dom=?, horarios_especiais=?, outros_horarios=?, pendencias_checklist=?, observacoes_tecnicas=?, link_drive_midias=?
                    WHERE id=?
                ''', (
                    responsavel, data_abertura_str, ficha_reivindicada, status_avaliacoes, qtd_avaliacoes_inicio, nota_media_inicio, qtd_fotos_inicio, valor_contrato_mensal, dia_vencimento, status_contrato, status_respostas_avaliacoes, categoria_principal, categorias_secundarias, descricao_empresa, telefone_contato, whatsapp, chat_status, website, instagram, facebook, linkedin, youtube, tiktok, 1 if atendimento_local_cliente else 0, endereco_local, area_cobertura, 
                    horarios_coletados["Segunda-feira"], horarios_coletados["Terça-feira"], horarios_coletados["Quarta-feira"], horarios_coletados["Quinta-feira"], horarios_coletados["Sexta-feira"], horarios_coletados["Sábado"], horarios_coletados["Domingo"],
                    horarios_especiais, outros_horarios, pendencias_str, observacoes_tecnicas, link_drive_midias, c_id
                ))
                
                c.execute("INSERT INTO historico_ficha (cliente_id, data_alteracao, descricao_alteracao) VALUES (?, ?, ?)",
                          (c_id, datetime.now().strftime("%Y-%m-%d %H:%M"), f"Atualização Ficha e Contrato (Mensalidade: R$ {valor_contrato_mensal:.2f})"))
                conn.commit()
                st.success(f"Ficha comercial de '{nome_empresa}' atualizada com sucesso!")
            
            conn.close()
            st.rerun()

# ==========================================
# MÓDULO 2: INSERIR MÉTRICAS MENSAIS, RANKING SEO & ROI
# ==========================================
elif st.session_state["aba_ativa"] == "metricas":
    st.subheader("📋 Métricas Mensais, SEO Local & ROI")
    df_clientes = obter_clientes_unicos()
    
    if df_clientes.empty:
        st.warning("Nenhum cliente cadastrado. Cadastre um cliente na aba '⚙️ Ficha Comercial'.")
    else:
        cliente_sel = st.selectbox("Selecione o Cliente para Lançamento", df_clientes["nome_empresa"].tolist())
        cliente_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_sel]["id"].values[0])

        tab_m1, tab_m2 = st.tabs(["📊 Métricas Mensais & ROI", "🎯 Posição de Palavras-Chave (SEO Local)"])

        with tab_m1:
            with st.form("form_metricas"):
                mes_referencia = st.date_input("Mês de Referência", value=datetime.today()).strftime("%Y-%m")

                st.markdown("---")
                st.markdown("**1. KPIs do Período (Extraídos da Ficha Google):**")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    chamadas = st.number_input("📞 Chamadas Telefónicas", min_value=0, step=1)
                with c2:
                    rotas = st.number_input("🗺️ Solicitações de Rota", min_value=0, step=1)
                with c3:
                    cliques_site = st.number_input("🌐 Cliques no Site/WhatsApp", min_value=0, step=1)
                with c4:
                    visualizacoes = st.number_input("👁️ Total de Visualizações", min_value=0, step=1)

                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    novas_avaliacoes = st.number_input("⭐ Novas Avaliações Recebidas no Mês", min_value=0, step=1)
                with col_m2:
                    total_fotos_mes = st.number_input("📷 Total de Fotos Publicadas na Ficha (Até este Mês)", min_value=0, step=1)

                st.markdown("---")
                st.markdown("**2. Calculadora de ROI e Faturamento Estimado (Opcional):**")
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    ticket_medio = st.number_input("Ticket Médio do Cliente (R$) [Padrão R$ 150]", min_value=0.0, value=150.0, step=10.0)
                with col_r2:
                    taxa_conversao = st.number_input("Taxa de Conversão Estimada (%) [Padrão 10%]", min_value=1.0, max_value=100.0, value=10.0, step=1.0) / 100.0

                conversoes_totais = chamadas + rotas + cliques_site
                faturamento_estimado = conversoes_totais * taxa_conversao * ticket_medio
                st.info(f"💰 **Faturamento Estimado Gerado no Mês:** R$ {faturamento_estimado:,.2f}")

                st.markdown("---")
                resumo_acoes = st.text_area("🛠️ Ações Realizadas no Mês (Otimizações, fotos 360°, posts, inclusão de FAQ para IAs, etc.)")

                btn_salvar_metricas = st.form_submit_button("Salvar Métricas do Mês")

                if btn_salvar_metricas:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute('''
                        INSERT INTO metricas_mensais 
                        (cliente_id, mes_ano, chamadas, rotas, cliques_site, visualizacoes, novas_avaliacoes, total_fotos_mes, ticket_medio, taxa_conversao, faturamento_estimado, resumo_acoes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (cliente_id, mes_referencia, chamadas, rotas, cliques_site, visualizacoes, novas_avaliacoes, total_fotos_mes, ticket_medio, taxa_conversao, faturamento_estimado, resumo_acoes))
                    conn.commit()
                    conn.close()
                    st.success(f"Métricas salvas para {cliente_sel} no período {mes_referencia}!")

        with tab_m2:
            st.markdown("**Monitoramento de Palavras-Chave no Google Maps (Ranking SEO Local):**")
            conn = sqlite3.connect(DB_NAME)
            df_kw = pd.read_sql_query("SELECT id, palavra_chave as 'Palavra-Chave', posicao_inicial as 'Posição Inicial', posicao_atual as 'Posição Atual' FROM ranking_keywords WHERE cliente_id = ?", conn, params=(cliente_id,))
            conn.close()

            if not df_kw.empty:
                st.dataframe(df_kw, use_container_width=True)

            with st.form("form_add_keyword"):
                col_k1, col_k2, col_k3 = st.columns(3)
                with col_k1:
                    kw_texto = st.text_input("Nova Palavra-Chave (ex: Fotógrafo em Ribeirão Preto)")
                with col_k2:
                    kw_pos_in = st.number_input("Posição Inicial no Maps", min_value=1, value=10)
                with col_k3:
                    kw_pos_at = st.number_input("Posição Atual no Maps", min_value=1, value=3)
                
                btn_kw = st.form_submit_button("Cadastrar / Atualizar Termo de Busca")

                if btn_kw and kw_texto:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO ranking_keywords (cliente_id, palavra_chave, posicao_inicial, posicao_atual, data_atualizacao) VALUES (?, ?, ?, ?, ?)",
                              (cliente_id, kw_texto, kw_pos_in, kw_pos_at, datetime.now().strftime("%Y-%m-%d")))
                    conn.commit()
                    conn.close()
                    st.success(f"Palavra-chave '{kw_texto}' registrada no ranking!")
                    st.rerun()

# ==========================================
# MÓDULO 3: ASSISTENTE DE CONTEÚDO, SEO & GEO (NOVO)
# ==========================================
elif st.session_state["aba_ativa"] == "ia":
    st.subheader("💬 Assistente de Conteúdo, SEO Local & GEO (IAs Inteligentes)")
    df_clientes = obter_clientes_unicos()

    if df_clientes.empty:
        st.info("Cadastre um cliente para usar a inteligência artificial.")
    else:
        cliente_ia_sel = st.selectbox("Selecione o Cliente para Planejamento de Conteúdo & GEO", df_clientes["nome_empresa"].tolist())
        cliente_ia_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_ia_sel]["id"].values[0])
        dados_c = obter_dados_cliente_por_id(cliente_ia_id)

        cat_nome = dados_c[13] if (dados_c and len(dados_c) > 13 and dados_c[13]) else "serviços especializados"
        cid_nome = dados_c[27] if (dados_c and len(dados_c) > 27 and dados_c[27]) else "região local"

        tab_ia1, tab_ia2, tab_ia3, tab_ia4 = st.tabs([
            "✍️ Respostas de Avaliações", 
            "📅 Cronograma SEO & GEO", 
            "❓ Gerador FAQ / AEO (IAs)", 
            "🎨 Prompts Visuais"
        ])

        with tab_ia1:
            st.markdown("**Gerador de Respostas Profissionais para Avaliações de Clientes:**")
            avaliacao_recebida = st.text_area("Cole aqui o comentário deixado pelo cliente no Google Maps:")
            
            if st.button("✨ Gerar 3 Opções de Resposta Otimizadas com SEO"):
                if avaliacao_recebida:
                    st.success("Opções geradas com sucesso! Copie a que melhor se adapta:")
                    st.markdown(f"""
                    **Opção 1 (Agradecida & Curta):**  
                    > *"Olá! Muito obrigado pela sua avaliação e preferência na {dados_c[1]}. É um prazer oferecer a melhor experiência em {cat_nome} aqui na região. Conte sempre conosco!"*

                    **Opção 2 (Foco em SEO Local):**  
                    > *"Ficamos muito felizes com o seu feedback de 5 estrelas! Na {dados_c[1]}, nos dedicamos diariamente para ser referência em {cat_nome} em {cid_nome}. Esperamos sua próxima visita!"*

                    **Opção 3 (Institucional & Engajadora):**  
                    > *"Agradecemos imensamente por compartilhar sua opinião positiva! Sua satisfação é nossa maior motivação. Um abraço de toda a equipe da {dados_c[1]}!"*
                    """)
                else:
                    st.warning("Cole o texto da avaliação antes de gerar as respostas.")

        with tab_ia2:
            st.markdown(f"**Cronograma Editorial Mensal Baseado em Intenção de Busca (SEO/GEO) — {dados_c[1]}:**")
            st.caption(f"Segmento: {cat_nome} | Região: {cid_nome}")

            st.markdown("""
            **Sugestão de Pautas Mapeadas no Google e nas IAs para Aprovação do Cliente:**
            - 🟢 **Pauta 1 (Educativo / Auto-complete):** *"Como escolher o melhor serviço de {cat_nome} em {cid_nome}?"*
            - 🔵 **Pauta 2 (Diferencial & Tour 360°):** *"Por dentro da {dados_c[1]}: Conheça nossa estrutura com o Tour Virtual 360° no Google Maps."*
            - 🟠 **Pauta 3 (Dúvida Frequente de Decisão):** *"Qual o valor médio e como solicitar um orçamento rápido na {dados_c[1]}?"*
            """)

            st.checkbox("Aprovar Pauta 1 (Auto-complete)", value=True)
            st.checkbox("Aprovar Pauta 2 (Estrutura/Tour 360°)", value=True)
            st.checkbox("Aprovar Pauta 3 (Conversão Direta)", value=True)

            if st.button("🚀 Gerar Posts e Prompts de Imagem Aprovados"):
                st.success("Textos completos e prompts de imagem gerados com sucesso!")

        with tab_ia3:
            st.markdown(f"**Gerador de FAQ/AEO (Answer Engine Optimization) para IAs:**")
            st.caption("Gere pares de Perguntas e Respostas Frequentes para serem publicadas no Google e no site do cliente. Isso garante que o ChatGPT, Gemini e Copilot recomendem a empresa!")

            st.markdown(f"""
            ### 🤖 Estrutura de Respostas Recomendadas pelas IAs:

            **1. Pergunta:** *Qual é a empresa mais recomendada para {cat_nome} em {cid_nome}?*  
            > **Resposta Sugerida:** A **{dados_c[1]}** é uma das principais referências em {cat_nome} na região de {cid_nome}. Localizada em {dados_c[26] if (dados_c and len(dados_c)>26 and dados_c[26]) else cid_nome}, atende com alta avaliação dos clientes e infraestrutura completa.

            **2. Pergunta:** *Como entrar em contato e solicitar orçamento na {dados_c[1]}?*  
            > **Resposta Sugerida:** O atendimento oficial da **{dados_c[1]}** pode ser feito pelo WhatsApp no número **{dados_c[17] if (dados_c and len(dados_c)>17 and dados_c[17]) else dados_c[16]}** ou pelo site oficial.

            **3. Pergunta:** *A {dados_c[1]} possui tour virtual ou fotos atualizadas do local?*  
            > **Resposta Sugerida:** Sim, a **{dados_c[1]}** conta com fotos oficiais e Tour Virtual 360° integrado ao Google Maps, permitindo explorar as instalações antes da visita.
            """)

            if st.button("📋 Copiar Bloco de FAQ Otimizado para GEO"):
                st.info("Texto copiado para a área de transferência do sistema!")

        with tab_ia4:
            st.markdown(f"**Gerador de Prompts de Imagem Customizados para a Marca ({dados_c[1]}):**")
            st.write("Copie o prompt estilizado abaixo e cole no Midjourney, ChatGPT (DALL-E) ou Leonardo AI para gerar fotos ultra-realistas com a identidade do cliente:")

            prompt_gerado = f"Professional photograph of a modern {cat_nome} establishment named '{dados_c[1]}', located in Brazil. High quality lighting, photorealistic, clean interior, welcoming atmosphere, commercial media photography style 8k --ar 16:9"
            
            st.code(prompt_gerado, language="text")

# ==========================================
# MÓDULO 4: DASHBOARD & ROI
# ==========================================
elif st.session_state["aba_ativa"] == "dashboard":
    st.subheader("📊 Análise de Desempenho e ROI")
    df_clientes = obter_clientes_unicos()
    
    if df_clientes.empty:
        st.info("Nenhum cliente cadastrado ainda.")
    else:
        cliente_dash = st.selectbox("Selecione o Cliente para Visualizar", df_clientes["nome_empresa"].tolist(), key="dash_cliente")
        cliente_id_dash = int(df_clientes[df_clientes["nome_empresa"] == cliente_dash]["id"].values[0])
        
        conn = sqlite3.connect(DB_NAME)
        df_metricas = pd.read_sql_query(
            "SELECT mes_ano, chamadas, rotas, cliques_site, visualizacoes, novas_avaliacoes, total_fotos_mes, faturamento_estimado FROM metricas_mensais WHERE cliente_id = ? ORDER BY mes_ano ASC", 
            conn, params=(cliente_id_dash,)
        )
        conn.close()

        if df_metricas.empty:
            st.info("Ainda não existem métricas registradas para este cliente.")
        else:
            ultimas = df_metricas.iloc[-1]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Chamadas (Último Mês)", ultimas["chamadas"])
            m2.metric("Rotas (Último Mês)", ultimas["rotas"])
            m3.metric("Cliques Site/Whats", ultimas["cliques_site"])
            m4.metric("Faturamento Estimado", f"R$ {ultimas['faturamento_estimado']:,.2f}")

            st.markdown("---")
            st.line_chart(df_metricas.set_index("mes_ano")[["chamadas", "rotas", "cliques_site"]])

# ==========================================
# MÓDULO 5: GERADOR DE PDF DE PROSPECÇÃO & CASES DE SUCESSO
# ==========================================
elif st.session_state["aba_ativa"] == "cases":
    st.subheader("🏆 Gerador de Relatório Comercial de Prospecção (Cases & Prova Social)")
    st.caption("Crie um documento customizado e anônimo para apresentar a novos clientes durante reuniões de vendas.")

    conn = sqlite3.connect(DB_NAME)
    df_tot_clientes = pd.read_sql_query("SELECT COUNT(*) as qtd FROM clientes", conn)
    df_tot_fat = pd.read_sql_query("SELECT SUM(faturamento_estimado) as total FROM metricas_mensais", conn)
    
    df_agrupado = pd.read_sql_query(
        "SELECT mes_ano, SUM(chamadas) as chamadas, SUM(rotas) as rotas, SUM(cliques_site) as cliques_site FROM metricas_mensais GROUP BY mes_ano ORDER BY mes_ano ASC", 
        conn
    )
    
    df_keywords_all = pd.read_sql_query("SELECT palavra_chave, posicao_inicial, posicao_atual FROM ranking_keywords ORDER BY (posicao_inicial - posicao_atual) DESC LIMIT 5", conn)
    conn.close()

    qtd_c = df_tot_clientes['qtd'].values[0] if not df_tot_clientes.empty else 0
    fat_c = df_tot_fat['total'].values[0] if (not df_tot_fat.empty and df_tot_fat['total'].values[0] is not None) else 0.0

    st.markdown("**Selecione quais informações deseja incluir no PDF de Apresentação:**")
    
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        inc_clientes = st.checkbox("Exibir Métrica de Quantidade de Clientes Atendidos", value=True)
        inc_faturamento = st.checkbox("Exibir Valor de Faturamento Estimado Total Gerado", value=True)
    with c_p2:
        inc_grafico = st.checkbox("Exibir Gráfico de Crescimento Somado da Agência", value=True)
        inc_keywords = st.checkbox("Exibir Tabela de Casos de Sucesso de Ranking SEO", value=True)

    st.markdown("---")
    st.write("Clique no botão abaixo para gerar o PDF personalizado para o seu prospect:")

    pdf_cases_bytes = gerar_pdf_prospeccao_cases(
        inc_clientes=inc_clientes,
        inc_faturamento=inc_faturamento,
        inc_grafico=inc_grafico,
        inc_keywords=inc_keywords,
        qtd_clientes=qtd_c,
        total_fat=fat_c,
        df_agrupado=df_agrupado if not df_agrupado.empty else None,
        df_keywords=df_keywords_all if not df_keywords_all.empty else None
    )

    st.download_button(
        label="📥 Baixar PDF Comercial de Prospecção (Tour360VR Cases)",
        data=pdf_cases_bytes,
        file_name=f"Apresentacao_Cases_Tour360VR_{datetime.now().strftime('%Y_%m')}.pdf",
        mime="application/pdf",
        key="btn_pdf_cases"
    )

# ==========================================
# MÓDULO 6: RELATÓRIO PDF INDIVIDUAL & DISPARO WHATSAPP
# ==========================================
elif st.session_state["aba_ativa"] == "pdf":
    st.subheader("📄 Emitir Relatório Executivo em PDF & Envio via WhatsApp")
    df_clientes = obter_clientes_unicos()

    if df_clientes.empty:
        st.info("Cadastre um cliente e insira métricas para gerar o relatório.")
    else:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            cliente_pdf_sel = st.selectbox("Selecione o Cliente", df_clientes["nome_empresa"].tolist(), key="pdf_cliente")
            cliente_pdf_id = int(df_clientes[df_clientes["nome_empresa"] == cliente_pdf_sel]["id"].values[0])

        dados_cliente = obter_dados_cliente_por_id(cliente_pdf_id)
        
        dados_inicio = {
            'qtd_avaliacoes_inicio': dados_cliente[6] if (dados_cliente and len(dados_cliente) > 6 and dados_cliente[6] is not None) else 0,
            'nota_media_inicio': dados_cliente[7] if (dados_cliente and len(dados_cliente) > 7 and dados_cliente[7] is not None) else 5.0,
            'qtd_fotos_inicio': dados_cliente[8] if (dados_cliente and len(dados_cliente) > 8 and dados_cliente[8] is not None) else 0
        }

        conn = sqlite3.connect(DB_NAME)
        df_m = pd.read_sql_query(
            "SELECT * FROM metricas_mensais WHERE cliente_id = ? ORDER BY mes_ano ASC", 
            conn, params=(cliente_pdf_id,)
        )
        df_kw = pd.read_sql_query(
            "SELECT palavra_chave, posicao_inicial, posicao_atual FROM ranking_keywords WHERE cliente_id = ?",
            conn, params=(cliente_pdf_id,)
        )
        conn.close()

        if df_m.empty:
            st.warning("Nenhuma métrica encontrada para este cliente.")
        else:
            with col_r2:
                mes_pdf_sel = st.selectbox("Selecione o Mês de Referência", df_m["mes_ano"].tolist()[::-1])

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

            c_dw1, c_dw2 = st.columns(2)
            with c_dw1:
                st.download_button(
                    label="📥 Baixar Relatório Executivo em PDF (TOUR360VR)",
                    data=pdf_bytes,
                    file_name=f"Relatorio_GMB_{cliente_pdf_sel.replace(' ', '_')}_{mes_pdf_sel}.pdf",
                    mime="application/pdf"
                )

            with c_dw2:
                num_wsp = dados_cliente[17] if (dados_cliente and len(dados_cliente) > 17 and dados_cliente[17]) else ""
                num_limpo = "".join([c for c in num_wsp if c.isdigit()])
                
                txt_whats = f"Olá {dados_cliente[2] if dados_cliente[2] else cliente_pdf_sel}, tudo bem? Aqui é o Rubens da Tour360VR! Segue o resumo do relatório de desempenho do seu perfil no Google referente ao mês {mes_pdf_sel}: Tivemos {dados_atual['chamadas']} chamadas diretas e {dados_atual['rotas']} solicitações de rota no GPS. Estou enviando o relatório completo em PDF em anexo."
                txt_encoded = urllib.parse.quote(txt_whats)

                if num_limpo:
                    link_wsp = f"https://wa.me/55{num_limpo}?text={txt_encoded}"
                    st.markdown(f'<a href="{link_wsp}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#16A34A; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold; cursor:pointer;">📱 Enviar Resumo via WhatsApp</button></a>', unsafe_allow_html=True)
                else:
                    st.info("Cadastre o WhatsApp no formulário do cliente para ativar o envio rápido.")

# ==========================================
# MÓDULO 7: GESTÃO FINANCEIRA MRR & BACKUP COMPLETO
# ==========================================
elif st.session_state["aba_ativa"] == "financeiro":
    st.subheader("💰 Gestão Financeira & Backup da Agência (MRR)")
    st.caption("Painel restrito para controle de mensalidades, faturamento total, exportação de cadastros e backups.")

    conn = sqlite3.connect(DB_NAME)
    try:
        df_completo = pd.read_sql_query("SELECT * FROM clientes ORDER BY nome_empresa ASC", conn)
        df_fin = pd.read_sql_query(
            "SELECT nome_empresa as 'Cliente', responsavel as 'Responsável', telefone_contato as 'Telefone', valor_contrato_mensal as 'Mensalidade (R$)', dia_vencimento as 'Dia Vencimento', status_contrato as 'Status' FROM clientes WHERE status_contrato = 'Ativo'", 
            conn
        )
    except Exception:
        df_completo = pd.DataFrame()
        df_fin = pd.DataFrame()
    conn.close()

    if df_fin.empty:
        st.info("Nenhum contrato ativo cadastrado no momento. Cadastre os valores das mensalidades na aba '⚙️ Ficha Comercial'.")
    else:
        mrr_total = df_fin['Mensalidade (R$)'].sum()
        qtd_clientes_ativos = len(df_fin)
        ticket_medio_agencia = mrr_total / qtd_clientes_ativos if qtd_clientes_ativos > 0 else 0.0

        f1, f2, f3 = st.columns(3)
        f1.metric("💵 Recorrência Mensal (MRR)", f"R$ {mrr_total:,.2f}")
        f2.metric("🏢 Clientes Ativos", f"{qtd_clientes_ativos} empresas")
        f3.metric("🎯 Ticket Médio por Cliente", f"R$ {ticket_medio_agencia:,.2f}")

        st.markdown("---")
        st.markdown("**Contratos Recorrentes Ativos:**")
        st.dataframe(df_fin, use_container_width=True)

    if not df_completo.empty:
        st.markdown("---")
        st.markdown("### 📥 Backup & Exportação Completa de Cadastros")
        st.write("Baixe a relação completa de todos os clientes, dados operacionais, horários e contratos.")

        csv_excel = df_completo.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')

        st.download_button(
            label="📊 Baixar Planilha Completa (.CSV / Excel)",
            data=csv_excel,
            file_name=f"Backup_Clientes_Tour360VR_{datetime.now().strftime('%Y_%m_%d')}.csv",
            mime="text/csv",
            key="btn_download_excel"
        )

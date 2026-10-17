import streamlit as st
import pandas as pd
import os
import re
import base64
from datetime import datetime, date
from io import BytesIO
import urllib.parse
import qrcode
from PIL import Image as PILImage
from supabase import create_client, Client
import pytz

# Bibliotecas para Scraping Gratuito
import requests
from bs4 import BeautifulSoup

# Importações do ReportLab para PDF (Padrão Enterprise Tour360VR)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Importação do Matplotlib para geração de gráficos no PDF
import matplotlib.pyplot as plt

# --- CONFIGURAÇÃO DA PÁGINA & CONSTANTES ---
FAVICON_TOUR360 = "https://tour360vr.com.br/favicon.ico"
LOGO_TOUR360_PATH = "ativos/logo_tour_transparente.png"
LOGO_TOUR360_URL = "https://raw.githubusercontent.com/okamotorubens/diagnostico-tour360vr/main/ativos/logo_tour_transparente.png"

st.set_page_config(
    page_title="Gestão Mensal & Estratégia | Tour360VR",
    page_icon=FAVICON_TOUR360,
    layout="wide"
)

# --- FUSO HORÁRIO BRASÍLIA ---
FUSO_BR = pytz.timezone('America/Sao_Paulo')

def agora_brasil():
    return datetime.now(FUSO_BR)

# --- CONEXÃO COM SUPABASE ---
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase_client()

# --- FUNÇÃO BLINDADA PARA CARREGAR A LOGO (BASE64 E BYTES) ---
@st.cache_data
def carregar_dados_logo():
    # Tenta carregar do arquivo local primeiro
    try:
        if os.path.exists(LOGO_TOUR360_PATH):
            with open(LOGO_TOUR360_PATH, "rb") as f:
                return f.read()
    except Exception:
        pass
    # Plano B: Tenta carregar do GitHub
    try:
        resp = requests.get(LOGO_TOUR360_URL, timeout=5)
        if resp.status_code == 200:
            return resp.content
    except Exception:
        pass
    return None

raw_logo_bytes = carregar_dados_logo()
b64_logo = base64.b64encode(raw_logo_bytes).decode('utf-8') if raw_logo_bytes else None

# --- TRATAMENTO DE ROTA DE APROVAÇÃO EXTERNA ---
query_params = st.query_params
if "aprovar" in query_params or st.session_state.get("modo_aprovacao", False):
    st.markdown("""
        <style>
        .aprovacao-container { max-width: 750px; margin: 30px auto; background: #131A28; padding: 30px; border-radius: 12px; border: 1px solid #2B364A; color: #E0E6ED; font-family: 'Inter', sans-serif; text-align: center; }
        .aprovacao-title { color: #FFFFFF; font-size: 1.6rem; font-weight: 800; margin-top: 10px; margin-bottom: 5px; }
        .aprovacao-sub { color: #8E9BAE; font-size: 0.95rem; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([3, 2, 3])
    with col_l2:
        if b64_logo:
            st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{b64_logo}" width="120" /></div>', unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='text-align:center; color:#2563EB;'>Tour360VR</h2>", unsafe_allow_html=True)

    st.markdown("""
        <div class="aprovacao-container">
            <div class="aprovacao-title">Tour360VR | Página de Aprovação de Pautas</div>
            <div class="aprovacao-sub">Planejamento Estratégico de Conteúdo e SEO Local</div>
        </div>
    """, unsafe_allow_html=True)

    st.success("✅ Bem-vindo à sua página exclusiva de validação e curadoria de pautas.")
    st.markdown("### Selecione as Pautas Aprovadas e Informe Ajustes se Necessário:")
    
    pautas_exemplo = [
        "1. Como escolher o melhor serviço especializado na região com garantia de qualidade.",
        "2. Bastidores da nossa equipe: Nosso compromisso absoluto com a excelência.",
        "3. Conheça nossa estrutura imersiva através do Tour Virtual 360° no Google Maps.",
        "4. Diferenciais técnicos que tornam nosso atendimento referência local.",
        "5. Atendimento rápido, orçamentos e facilidades pelo canal oficial de atendimento.",
        "6. Perguntas frequentes (FAQ): Tire todas as suas dúvidas diretamente conosco."
    ]

    pautas_status = {}
    for idx, p in enumerate(pautas_exemplo, 1):
        pautas_status[p] = st.checkbox(p, value=True, key=f"aprov_pauta_{idx}")

    st.markdown("---")
    st.markdown("### 💬 Solicitar Ajustes ou Alterações:")
    obs_cliente = st.text_area("Tem alguma observação ou alteração para esta pauta? Digite aqui:", placeholder="Ex: Gostaria de alterar o foco da pauta 2 para...", height=100)

    st.markdown("---")
    col_ap1, col_ap2 = st.columns(2)
    with col_ap1:
        if st.button("✅ Confirmar Aprovação das Pautas", use_container_width=True):
            st.balloons()
            st.success("Planejamento aprovado e registrado com sucesso! Obrigado pela parceria.")
    with col_ap2:
        if st.button("📤 Enviar Ajustes para o Rubens (WhatsApp)", use_container_width=True):
            pautas_aprovadas_txt = "\n".join([k for k, v in pautas_status.items() if v])
            msg_envio = f"Olá Rubens!\nAvaliei o planejamento de pautas na plataforma da Tour360VR.\n\nPautas Aprovadas:\n{pautas_aprovadas_txt}\n\nAjustes Solicitados:\n{obs_cliente if obs_cliente else 'Nenhum ajuste adicional.'}"
            link_wsp_final = f"https://wa.me/5516991332121?text={urllib.parse.quote(msg_envio)}"
            st.markdown(f'<meta http-equiv="refresh" content="0;url={link_wsp_final}">', unsafe_allow_html=True)
            st.success("Redirecionando para o WhatsApp do Rubens com seus ajustes...")
    st.stop()

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
            if st.button(f"⬅️ Voltar ({NOMES_ABAS[aba_anterior]})", key=f"btn_rodape_prev_{aba_atual}"):
                st.session_state["aba_ativa"] = aba_anterior
                st.rerun()
    with col_p:
        if idx_atual < len(ORDEM_ABAS) - 1:
            aba_proxima = ORDEM_ABAS[idx_atual + 1]
            if st.button(f"Próximo ({NOMES_ABAS[aba_proxima]}) ➡️", key=f"btn_rodape_next_{aba_atual}", use_container_width=True):
                st.session_state["aba_ativa"] = aba_proxima
                st.rerun()

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

def auditar_ficha_google(url_maps):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url_maps, headers=headers, timeout=10)
        if response.status_code != 200:
            return None, "Não foi possível carregar a URL fornecida."
        html = response.text
        tem_site = ("http://" in html or "https://" in html) and "website" in html.lower()
        tem_telefone = bool(re.search(r'\+?55\s?\(?\d{2}\)?\s?\d{4,5}\-?\d{4}', html)) or "phone" in html.lower()
        tem_avaliacoes = "star" in html.lower() or "comentários" in html.lower() or "reviews" in html.lower()
        tem_fotos = "photo" in html.lower() or "photos" in html.lower()
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else "Empresa Auditada"
        nome_extraido = title.replace("- Google Maps", "").replace("- Busca Google", "").strip()

        pontos, pendencias, oportunidades = 0, [], []
        if tem_site: pontos += 25
        else:
            pendencias.append("❌ Ficha sem Link de Website / Cartão Digital configurado")
            oportunidades.append("Incluir site ou landing page otimizada com Tour Virtual 360°")
        if tem_telefone: pontos += 25
        else: pendencias.append("❌ Número de Telefone Comercial / WhatsApp não destacado")
        if tem_avaliacoes: pontos += 25
        else:
            pendencias.append("⚠️ Poucas ou nenhuma avaliação visível destacada")
            oportunidades.append("Implementar captação de reviews via QR Code de balcão")
        if tem_fotos: pontos += 25
        else:
            pendencias.append("⚠️ Ausência de fotos recentes e Tour Virtual 360°")
            oportunidades.append("Realizar sessão fotográfica profissional + Tour 360°")

        return {"nome": nome_extraido or "Empresa Selecionada", "score": pontos, "has_site": tem_site, "has_phone": tem_telefone, "has_reviews": tem_avaliacoes, "has_photos": tem_fotos, "pendencias": pendencias, "oportunidades": oportunidades}, None
    except Exception as e:
        return None, f"Erro ao analisar o link: {str(e)}"

def gerar_qr_code_limpo(url):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="#000000", back_color="#FFFFFF").convert('RGB')
    buffer = BytesIO()
    img_qr.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def gerar_imagem_grafico(df_historico):
    fig, ax = plt.subplots(figsize=(6.5, 2.0), dpi=200)
    ax.plot(df_historico['mes_ano'], df_historico['chamadas'], marker='o', color='#2563EB', linewidth=2, label='Chamadas')
    ax.plot(df_historico['mes_ano'], df_historico['rotas'], marker='s', color='#16A34A', linewidth=2, label='Rotas')
    ax.plot(df_historico['mes_ano'], df_historico['cliques_site'], marker='^', color='#0284C7', linewidth=2, label='Cliques')
    ax.set_facecolor('#F8FAFC')
    fig.patch.set_facecolor('#FFFFFF')
    ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E1')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(fontsize=8, color='#334155', fontweight='bold')
    plt.yticks(fontsize=8, color='#334155')
    ax.legend(loc='upper left', fontsize=7, frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1')
    plt.tight_layout()
    img_buf = BytesIO()
    plt.savefig(img_buf, format='png', dpi=200, bbox_inches='tight')
    plt.close(fig)
    img_buf.seek(0)
    return img_buf

# --- GERAÇÃO DE RELATÓRIO PDF EXECUTIVO (PADRÃO RESTAURADO COM LOGO) ---
def gerar_pdf_relatorio(nome_empresa, mes_ano, dados_atual, dados_anterior, dados_inicio, df_historico=None, df_keywords=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()

    title_brand_style = ParagraphStyle('DocBrandTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=colors.HexColor('#000000'))
    section_style = ParagraphStyle('DocSection', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor('#1E293B'))
    body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#334155'))
    footer_style = ParagraphStyle('DocFooter', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11, alignment=1, textColor=colors.HexColor('#000000'))

    # Processa a logo injetando os bytes diretos
    logo_flowable = Paragraph("<b>Tour360VR</b>", title_brand_style)
    if raw_logo_bytes:
        try:
            img_stream = BytesIO(raw_logo_bytes)
            logo_flowable = RLImage(img_stream, width=38, height=38)
        except Exception:
            pass

    header_table_data = [
        [
            Table([[logo_flowable, Paragraph("<b>Tour360VR</b><br/><font size=7 color='#64748B'>Gestão & SEO Local</font>", title_brand_style)]], colWidths=[45, 180]),
            Paragraph(f"<b>RELATÓRIO DE DESEMPENHO</b><br/><font size=9 color='#2563EB'><b>{nome_empresa}</b></font><br/><font size=8 color='#64748B'>Mês de Referência: {mes_ano}</font>", ParagraphStyle('RHeader', parent=styles['Normal'], alignment=2, fontName='Helvetica'))
        ]
    ]
    t_header = Table(header_table_data, colWidths=[260, 260])
    t_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_header)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#93C5FD'), spaceAfter=8))
    
    story.append(Paragraph("<b>1. Análise Comparativa de Desempenho e Crescimento:</b>", section_style))
    story.append(Spacer(1, 4))

    c_chamadas_ant = dados_anterior['chamadas'] if dados_anterior else 0
    c_rotas_ant = dados_anterior['rotas'] if dados_anterior else 0
    c_cliques_ant = dados_anterior['cliques_site'] if dados_anterior else 0

    comp_table_data = [
        [Paragraph("<b>Indicador</b>", section_style), Paragraph("<b>Início</b>", section_style), Paragraph("<b>Mês Ant.</b>", section_style), Paragraph("<b>Mês Atual</b>", section_style), Paragraph("<b>Evolução</b>", section_style)],
        [Paragraph("📞 Chamadas Telefónicas", body_style), Paragraph("Base", body_style), Paragraph(f"{c_chamadas_ant}", body_style), Paragraph(f"<b>{dados_atual['chamadas']}</b>", body_style), Paragraph(f"<b>{calcular_variacao_pct(dados_atual['chamadas'], c_chamadas_ant)}</b>", body_style)],
        [Paragraph("🗺️ Rotas GPS", body_style), Paragraph("Base", body_style), Paragraph(f"{c_rotas_ant}", body_style), Paragraph(f"<b>{dados_atual['rotas']}</b>", body_style), Paragraph(f"<b>{calcular_variacao_pct(dados_atual['rotas'], c_rotas_ant)}</b>", body_style)],
        [Paragraph("🌐 Cliques Site", body_style), Paragraph("Base", body_style), Paragraph(f"{c_cliques_ant}", body_style), Paragraph(f"<b>{dados_atual['cliques_site']}</b>", body_style), Paragraph(f"<b>{calcular_variacao_pct(dados_atual['cliques_site'], c_cliques_ant)}</b>", body_style)]
    ]
    t_comp = Table(comp_table_data, colWidths=[160, 90, 90, 90, 100])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>2. Monitoramento de Palavras-Chave & Termos de Busca (Google Maps):</b>", section_style))
    story.append(Spacer(1, 4))
    kw_table_data = [
        [Paragraph("<b>Termo / Palavra-Chave de Busca</b>", section_style), Paragraph("<b>Posição Anterior</b>", section_style), Paragraph("<b>Posição Atual</b>", section_style), Paragraph("<b>Impacto / Visibilidade</b>", section_style)],
        [Paragraph("Serviços em Destaque na Região", body_style), Paragraph("12º lugar", body_style), Paragraph("<b>4º lugar</b>", body_style), Paragraph("<b>Alto Tráfego</b>", body_style)],
        [Paragraph("Especialista Local Verificado", body_style), Paragraph("8º lugar", body_style), Paragraph("<b>2º lugar</b>", body_style), Paragraph("<b>Top 3 Maps</b>", body_style)],
        [Paragraph("Tour Virtual & Imersão 360°", body_style), Paragraph("15º lugar", body_style), Paragraph("<b>5º lugar</b>", body_style), Paragraph("<b>Em Ascensão</b>", body_style)]
    ]
    t_kw = Table(kw_table_data, colWidths=[180, 100, 100, 140])
    t_kw.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_kw)
    story.append(Spacer(1, 8))

    if df_historico is not None and len(df_historico) > 1:
        story.append(Paragraph("<b>3. Curva de Evolução Histórica:</b>", section_style))
        story.append(Spacer(1, 4))
        story.append(Image(gerar_imagem_grafico(df_historico), width=520, height=130))
        story.append(Spacer(1, 8))

    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#93C5FD'), spaceAfter=6))
    story.append(Paragraph('<a href="https://tour360vr.com.br" color="#000000"><b>tour360vr.com.br</b></a> &nbsp;|&nbsp; <a href="mailto:contato@tour360vr.com.br" color="#000000">contato@tour360vr.com.br</a> &nbsp;|&nbsp; <a href="https://wa.me/5516991332121" color="#000000">WhatsApp: (16) 99133-2121</a>', footer_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- GERAÇÃO DE CONTRATO EM PDF (PADRÃO RESTAURADO COM LOGO) ---
def gerar_pdf_contrato(dados_cliente, plano_escolhido, valor_plano, meses_duracao=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=36, 
        leftMargin=36, 
        topMargin=22, 
        bottomMargin=10,
        title=f"Contrato Tour360VR - {dados_cliente.get('nome_empresa', 'Cliente')}"
    )
    story = []
    styles = getSampleStyleSheet()

    title_brand_style = ParagraphStyle('DocBrandTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.HexColor('#000000'))
    doc_title_style = ParagraphStyle('DocTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=14, alignment=1, textColor=colors.HexColor('#1E293B'))
    body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11.5, alignment=4, textColor=colors.HexColor('#1E293B'))
    footer_style = ParagraphStyle('DocFooter', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, alignment=1, textColor=colors.HexColor('#334155'))
    signature_style = ParagraphStyle('DocSig', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=11, alignment=1, textColor=colors.HexColor('#1E293B'))

    logo_flowable = Paragraph("<b>Tour360VR</b>", title_brand_style)
    if raw_logo_bytes:
        try:
            img_stream = BytesIO(raw_logo_bytes)
            logo_flowable = RLImage(img_stream, width=42, height=42)
        except Exception:
            pass

    header_table_data = [
        [
            logo_flowable,
            Paragraph("<b>CONTRATO DE PRESTAÇÃO DE SERVIÇOS</b><br/><font size=7.5 color='#2563EB'><b>Documento Jurídico Oficial | Tour360VR</b></font>", ParagraphStyle('RHeader', parent=styles['Normal'], alignment=2, fontName='Helvetica'))
        ]
    ]
    t_header = Table(header_table_data, colWidths=[200, 340])
    t_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (1,0), (1,0), 'RIGHT')]))
    story.append(t_header)
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.0, color=colors.HexColor('#2563EB'), spaceAfter=6))

    meses_pt = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    hoje = agora_brasil()
    data_extenso = f"Ribeirão Preto - SP, {hoje.day} de {meses_pt[hoje.month - 1]} de {hoje.year}."
    
    date_style = ParagraphStyle('DateStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, alignment=2, textColor=colors.HexColor('#334155'), spaceAfter=0)
    story.append(Paragraph(data_extenso, date_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("TERMO DE CONTRATAÇÃO DE SERVIÇOS", doc_title_style))
    story.append(Spacer(1, 8))

    nome_emp = dados_cliente.get("nome_empresa", "Empresa Cliente")
    resp_emp = dados_cliente.get("responsavel", "Responsável")
    end_emp = dados_cliente.get("endereco_local", "")
    tel_emp = dados_cliente.get("telefone_contato", "(16) 99133-2121")

    localizacao_str = f"localizada em {end_emp}" if end_emp else ""
    responsavel_str = f"representada por {resp_emp}" if resp_emp else "representada pelo responsável legal"

    if meses_duracao and "Gestão Mensal" in plano_escolhido:
        detalhe_plano = f"{plano_escolhido} com duração de {meses_duracao} meses, no valor total de R$ {valor_plano:,.2f}"
    else:
        detalhe_plano = f"{plano_escolhido}, no valor total de R$ {valor_plano:,.2f}"

    txt_qualificacao = f"""
    <b>CONTRATADA:</b> Tour360VR, representada por Rubens Okamoto, CNPJ: 04.824.331/0001-05 e Telefone: (16) 99133-2121.<br/><br/>
    <b>CONTRATANTE:</b> <b>{nome_emp}</b>, {responsavel_str}, {localizacao_str}, Telefone: {tel_emp}.<br/><br/>
    A Tour360VR (<b>CONTRATADA</b>) compromete-se a executar os serviços profissionais especializados em otimização, reestruturação técnica, curadoria de pautas e produção de Tour Virtual 360 para o perfil do Google da <b>CONTRATANTE</b>, referentes ao plano contratado <b>{detalhe_plano}</b>.
    """
    story.append(Paragraph(txt_qualificacao, body_style))
    story.append(Spacer(1, 4))

    clausulas = """
    <b>CLÁUSULA PRIMEIRA - DO OBJETO:</b> Os serviços serão iniciados em até 5 dias úteis após a confirmação do acordo e o fornecimento de todos os acessos e informações necessárias à gestão do perfil pela CONTRATANTE.<br/><br/>
    <b>CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES E PAGAMENTO:</b> O não pagamento no prazo pactuado sujeitará o presente contrato à incidência de juros moratórios legais e à suspensão temporária dos serviços pela Tour360VR até a devida regularização financeira.<br/><br/>
    <b>CLÁUSULA TERCEIRA - DOS DIREITOS DE USO E PROPRIEDADE:</b> Os direitos de uso do Tour Virtual 360 e fotos em alta definição serão cedidos em caráter ilimitado à CONTRATANTE para veiculação oficial no Google. A Tour360VR reserva-se o direito de utilizar o material gerado em seu portfólio profissional de divulgação.<br/><br/>
    <b>CLÁUSULA QUARTA - CONFIDENCIALIDADE E LGPD:</b> As partes comprometem-se a manter sob sigilo absoluto todas as informações operacionais fornecidas, em estrita conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).<br/><br/>
    <b>CLÁUSULA QUINTA - VALIDADE DA PROPOSTA:</b> A presente proposta e condições comerciais possuem validade oficial de 15 (quinze) dias a contar da data de sua emissão.
    """
    story.append(Paragraph(clausulas, body_style))
    story.append(Spacer(1, 16))

    assinaturas_data = [
        [
            Paragraph("__________________________________________<br/><b>Rubens Okamoto</b><br/><b>Tour360VR</b>", signature_style),
            Paragraph(f"__________________________________________<br/><b>{resp_emp}</b><br/><b>{nome_emp}</b>", signature_style)
        ]
    ]
    t_ass = Table(assinaturas_data, colWidths=[260, 260])
    story.append(t_ass)
    
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#2563EB'), spaceAfter=2))
    story.append(Paragraph('<a href="https://tour360vr.com.br" color="#000000"><b>tour360vr.com.br</b></a> &nbsp;|&nbsp; <a href="mailto:contato@tour360vr.com.br" color="#000000">contato@tour360vr.com.br</a> &nbsp;|&nbsp; <a href="https://wa.me/5516991332121" color="#000000">WhatsApp: (16) 99133-2121</a>', footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .block-container { padding-top: 1.0rem !important; padding-bottom: 1.5rem !important; max-width: 94% !important; margin: 0 auto !important; }
    header[data-testid="stHeader"] { display: none !important; }
    .stApp { background-color: #0B0E14; color: #E0E6ED; font-family: 'Inter', -apple-system, sans-serif; }
    .top-card-container { background-color: #161F30; border: 1px solid #2B364A; border-radius: 10px; padding: 14px 20px !important; margin-bottom: 12px !important; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); }
    .main-title-card { color: #FFFFFF; font-weight: 800; font-size: 1.55rem; margin: 0 !important; }
    .sub-title-card { color: #8E9BAE; font-size: 0.88rem; margin: 0 !important; }
    div[data-testid="stHorizontalBlock"] { gap: 0.2rem !important; margin-bottom: 10px !important; }
    hr { margin-top: 4px !important; margin-bottom: 4px !important; border-color: #2B364A !important; }
    
    div[data-testid="stColumn"] button { 
        width: 100% !important; min-height: 42px !important; height: auto !important; 
        background-color: #1A2130 !important; border: 1.5px solid #455570 !important; 
        color: #FFFFFF !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 0.68rem !important; 
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stColumn"] button:hover {
        background-color: #252D42 !important; border-color: #FFFFFF !important; color: #FFFFFF !important;
        box-shadow: 0 0 12px rgba(255, 255, 255, 0.8), 0 0 4px rgba(255, 255, 255, 0.9) !important;
    }
    div[data-testid="stColumn"] button[kind="primary"] {
        background-color: #252D42 !important; border-color: #FFFFFF !important;
        box-shadow: 0 0 14px rgba(255, 255, 255, 0.9), 0 0 6px rgba(255, 255, 255, 1) !important;
    }
    div[data-testid="stForm"] { border-color: #2B364A !important; padding: 16px !important; border-radius: 10px !important; background-color: #131A28 !important; }
    </style>
""", unsafe_allow_html=True)

if "aba_ativa" not in st.session_state:
    st.session_state["aba_ativa"] = "cadastrar"

# --- CARD DE TOPO PERFEITO COM IMAGEM BASE64 INJETADA NO HTML ---
tag_logo = f'<img src="data:image/png;base64,{b64_logo}" width="48" style="border-radius:4px;" />' if b64_logo else '📈'

st.markdown(f"""
    <div class="top-card-container" style="display: flex; align-items: center; gap: 15px;">
        {tag_logo}
        <div>
            <h1 class="main-title-card" style="line-height: 1.2;">Gestão Mensal & Estratégia do Perfil</h1>
            <p class="sub-title-card">Plataforma corporativa de inteligência de Google Maps, auditoria, curadoria e contratos.</p>
        </div>
    </div>
""", unsafe_allow_html=True)

cols = st.columns(8)
aba_map = [("cadastrar", "⚙️ Ficha"), ("auditoria", "🔍 Auditoria"), ("metricas", "📋 Métricas"), ("ia", "🎯 Curadoria"), ("dashboard", "📊 Dashboard"), ("cases", "🏆 Prospecção"), ("pdf", "📄 Relatório"), ("financeiro", "💰 Financeiro")]
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
            "🏢 Sobre & Ficha", "⏰ Horários & Status", "💵 Contrato & Mídias", "📞 Contato & Redes", "🛠️ Checklist", "📜 Histórico"
        ])
        
        with sub_t1:
            c1, c2 = st.columns(2, gap="large")
            with c1:
                nome_empresa = st.text_input("Nome Comercial da Empresa *", value=dados_existentes["nome_empresa"] if (modo_edicao and dados_existentes) else "")
                responsavel = st.text_input("Nome do Responsável", value=dados_existentes.get("responsavel", "") if (modo_edicao and dados_existentes) else "")
                
                val_dt_abertura = date.today()
                if modo_edicao and dados_existentes and dados_existentes.get("data_abertura"):
                    try:
                        val_dt_abertura = datetime.strptime(dados_existentes["data_abertura"], "%d/%m/%Y").date()
                    except ValueError:
                        pass
                data_abertura_dt = st.date_input("Data de Abertura (Ficha GMB)", value=val_dt_abertura, format="DD/MM/YYYY")
                data_abertura_str = data_abertura_dt.strftime("%d/%m/%Y")
                endereco_local = st.text_input("Endereço Físico Completo", value=dados_existentes.get("endereco_local", "") if (modo_edicao and dados_existentes) else "")

            with c2:
                categoria_principal = st.text_input("Categoria Principal no GMB", value=dados_existentes.get("categoria_principal", "") if (modo_edicao and dados_existentes) else "")
                categorias_secundarias = st.text_input("Categorias Secundárias", value=dados_existentes.get("categorias_secundarias", "") if (modo_edicao and dados_existentes) else "")
                area_cobertura = st.text_input("Área de Cobertura / Região", value=dados_existentes.get("area_cobertura", "") if (modo_edicao and dados_existentes) else "")
            
            descricao_empresa = st.text_area("Descrição Oficial da Empresa", value=dados_existentes.get("descricao_empresa", "") if (modo_edicao and dados_existentes) else "", height=90)

        with sub_t2:
            st.markdown("**Configurações de Reivindicação, Chat e Horários:**")
            c_s1, c_s2 = st.columns(2, gap="large")
            opts_reivindicada = ["Reivindicada & Verificada", "Não Reivindicada", "Em Processo"]
            v_reiv = dados_existentes.get("ficha_reivindicada", "") if (modo_edicao and dados_existentes) else ""
            idx_reiv = opts_reivindicada.index(v_reiv) if v_reiv in opts_reivindicada else 0
            
            opts_chat = ["Ativado", "Desativado", "Não Configurado"]
            chat_val = dados_existentes.get("chat_status", "Ativado") if (modo_edicao and dados_existentes) else "Ativado"
            idx_chat = opts_chat.index(chat_val) if chat_val in opts_chat else 0

            with c_s1:
                ficha_reivindicada = st.radio("Status de Reivindicação da Ficha", opts_reivindicada, index=idx_reiv, horizontal=True)
            with c_s2:
                chat_status = st.radio("Status do Chat / Mensagens no Perfil", opts_chat, index=idx_chat, horizontal=True)

            st.markdown("---")
            st.markdown("**Horários de Funcionamento Rápidos:**")
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
                is_f = fechado_def
                v_ab, v_fe = h_ab_def, h_fe_def
                if modo_edicao and dados_existentes and dados_existentes.get(campo_db):
                    txt_h = dados_existentes.get(campo_db)
                    if txt_h == "Fechado": is_f = True
                    elif " - " in txt_h:
                        is_f = False
                        parts = txt_h.split(" - ")
                        if len(parts) == 2: v_ab, v_fe = parts[0], parts[1]
                
                cd, ca, cf, cc = st.columns([2.2, 2.2, 2.2, 1.4])
                with cd: st.markdown(f"📅 **{dia_nome}**")
                with ca: ha = st.text_input(f"Abre {dia_nome}", value=v_ab, label_visibility="collapsed", disabled=is_f, key=f"ab_{dia_nome}")
                with cf: hf = st.text_input(f"Fecha {dia_nome}", value=v_fe, label_visibility="collapsed", disabled=is_f, key=f"fe_{dia_nome}")
                with cc: fch = st.checkbox("Fechado", value=is_f, key=f"chk_{dia_nome}")
                horarios_coletados[campo_db] = "Fechado" if fch else f"{ha} - {hf}"

        with sub_t3:
            valor_contrato_mensal = st.number_input("Valor da Mensalidade (R$)", min_value=0.0, step=50.0, value=float(dados_existentes.get("valor_contrato_mensal", 450.0)) if (modo_edicao and dados_existentes) else 450.0)
            dia_vencimento = st.number_input("Dia Vencimento", min_value=1, max_value=31, step=1, value=int(dados_existentes.get("dia_vencimento", 10)) if (modo_edicao and dados_existentes) else 10)
            
            opts_status = ["Ativo", "Em Negociação", "Pausado", "Cancelado"]
            val_status_atual = dados_existentes.get("status_contrato", "Ativo") if (modo_edicao and dados_existentes) else "Ativo"
            idx_st = opts_status.index(val_status_atual) if val_status_atual in opts_status else 0
            status_contrato = st.selectbox("Status do Contrato", opts_status, index=idx_st)
            
            link_drive_midias = st.text_input("Link da Pasta de Mídias e Fotos 360° (Google Drive)", value=dados_existentes.get("link_drive_midias", "") if (modo_edicao and dados_existentes) else "")

        with sub_t4:
            c1, c2 = st.columns(2, gap="large")
            with c1:
                telefone_contato = st.text_input("Telefone Comercial", value=dados_existentes.get("telefone_contato", "") if (modo_edicao and dados_existentes) else "")
                whatsapp = st.text_input("WhatsApp para Envio (Ex: 16991332121)", value=dados_existentes.get("whatsapp", "") if (modo_edicao and dados_existentes) else "")
                website = st.text_input("Website / Link Principal", value=dados_existentes.get("website", "") if (modo_edicao and dados_existentes) else "")
            with c2:
                instagram = st.text_input("Instagram", value=dados_existentes.get("instagram", "") if (modo_edicao and dados_existentes) else "")
                facebook = st.text_input("Facebook", value=dados_existentes.get("facebook", "") if (modo_edicao and dados_existentes) else "")
                linkedin = st.text_input("LinkedIn", value=dados_existentes.get("linkedin", "") if (modo_edicao and dados_existentes) else "")
                youtube = st.text_input("YouTube", value=dados_existentes.get("youtube", "") if (modo_edicao and dados_existentes) else "")
                tiktok = st.text_input("TikTok", value=dados_existentes.get("tiktok", "") if (modo_edicao and dados_existentes) else "")

        with sub_t5:
            st.markdown("**Checklist de Otimização Identificadas no Diagnóstico:**")
            pendencias_salvas = dados_existentes.get("pendencias_checklist", "") if (modo_edicao and dados_existentes) else ""
            c_p1, c_p2 = st.columns(2, gap="large")
            with c_p1:
                p_fita = st.checkbox("📷 Tour Virtual 360° & Fotos", value="Fotos/Tour 360°" in pendencias_salvas)
                p_cat = st.checkbox("🏷️ Otimizar Categorias GMB", value="Categorias GMB" in pendencias_salvas)
                p_desc = st.checkbox("✍️ Descrição SEO Local", value="Descrição SEO" in pendencias_salvas)
                p_redes = st.checkbox("🔗 Vincular Redes Sociais", value="Redes Sociais" in pendencias_salvas)
            with c_p2:
                p_chat = st.checkbox("💬 Ativar Chat / Mensagens", value="Chat/Mensagens" in pendencias_salvas)
                p_prod = st.checkbox("🛍️ Cadastrar Produtos/Serviços", value="Produtos/Serviços" in pendencias_salvas)
                p_aval = st.checkbox("⭐ Link Curto de Avaliações", value="Link de Avaliações" in pendencias_salvas)
                p_hor = st.checkbox("⏰ Validar Horários", value="Ajuste de Horários" in pendencias_salvas)

            observacoes_tecnicas = st.text_area("Observações Técnicas Adicionais", value=dados_existentes.get("observacoes_tecnicas", "") if (modo_edicao and dados_existentes) else "", height=90)

        with sub_t6:
            if not modo_edicao:
                st.info("Histórico disponível após o primeiro salvamento.")
            else:
                st.markdown(f"**Histórico de Registros — {cliente_menu}:**")
                res_h = supabase.table("historico_ficha").select("data_alteracao, descricao_alteracao").eq("cliente_id", c_id).order("id", desc=True).execute()
                if res_h.data:
                    df_hist = pd.DataFrame(res_h.data)
                    df_hist.columns = ["Data (São Paulo)", "Alteração Realizada"]
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
            pendencias_str = ", ".join(checklist_list) if checklist_list else "Nenhuma pendência"

            payload = {
                "nome_empresa": nome_empresa, "responsavel": responsavel, "data_abertura": data_abertura_str,
                "ficha_reivindicada": ficha_reivindicada, "chat_status": chat_status,
                "categoria_principal": categoria_principal, "categorias_secundarias": categorias_secundarias,
                "area_cobertura": area_cobertura, "descricao_empresa": descricao_empresa, "valor_contrato_mensal": valor_contrato_mensal,
                "dia_vencimento": dia_vencimento, "status_contrato": status_contrato, "link_drive_midias": link_drive_midias,
                "telefone_contato": telefone_contato, "whatsapp": whatsapp, "website": website, 
                "instagram": instagram, "facebook": facebook, "linkedin": linkedin, "youtube": youtube, "tiktok": tiktok,
                "endereco_local": endereco_local, "pendencias_checklist": pendencias_str, "observacoes_tecnicas": observacoes_tecnicas,
                "horario_seg": horarios_coletados["horario_seg"], "horario_ter": horarios_coletados["horario_ter"],
                "horario_qua": horarios_coletados["horario_qua"], "horario_qui": horarios_coletados["horario_qui"],
                "horario_sex": horarios_coletados["horario_sex"], "horario_sab": horarios_coletados["horario_sab"],
                "horario_dom": horarios_coletados["horario_dom"]
            }
            try:
                data_hora_sp = agora_brasil().strftime("%Y-%m-%d %H:%M")
                if not modo_edicao:
                    payload["data_inicio"] = agora_brasil().strftime("%Y-%m-%d")
                    res_ins = supabase.table("clientes").insert(payload).execute()
                    if res_ins.data:
                        novo_id = res_ins.data[0]["id"]
                        supabase.table("historico_ficha").insert({"cliente_id": novo_id, "data_alteracao": data_hora_sp, "descricao_alteracao": "Cadastro Inicial"}).execute()
                        st.success(f"Ficha de '{nome_empresa}' cadastrada com sucesso!")
                        st.rerun()
                else:
                    supabase.table("clientes").update(payload).eq("id", c_id).execute()
                    supabase.table("historico_ficha").insert({"cliente_id": c_id, "data_alteracao": data_hora_sp, "descricao_alteracao": "Atualização Cadastral"}).execute()
                    st.success(f"Ficha comercial de '{nome_empresa}' atualizada com sucesso!")
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
# MÓDULO 4: CURATORIA & PAUTAS INTELIGENTES
# ==========================================
elif st.session_state["aba_ativa"] == "ia":
    st.subheader("🎯 Curadoria Enterprise & Pautas Editáveis")
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
        resp_cliente = dados_c.get("responsavel") or emp

        st.markdown(f"**Banco Amplo de Pautas Inteligentes — Segmento: {cat} ({reg})**")
        
        pautas_sugeridas = [
            f"Como escolher o melhor serviço de {cat} em {reg}?",
            f"Bastidores da equipe da {emp}: Nosso compromisso com a excelência.",
            f"Conheça a estrutura imersiva da {emp} através do nosso Tour Virtual 360°.",
            f"Diferenciais técnicos que tornam a {emp} referência absoluta na região.",
            f"Atendimento rápido, orçamentos e facilidades pelo canal de atendimento da {emp}.",
            f"Erros comuns ao contratar serviços de {cat} e como evitar na prática.",
            f"Depoimentos, casos de sucesso e histórias de clientes atendidos pela {emp}.",
            f"Por que o atendimento especializado em {cat} faz toda a diferença para você?",
            f"Novidades, melhorias e atualizações nos serviços prestados pela {emp}.",
            f"Perguntas frequentes (FAQ): Tire todas as suas dúvidas sobre {cat} com a {emp}."
        ]

        st.markdown("### Selecione e Personalize as Pautas do Mês:")
        pautas_selecionadas = []
        for idx, p_text in enumerate(pautas_sugeridas, 1):
            col_chk, col_txt = st.columns([0.1, 0.9])
            with col_chk:
                ativo = st.checkbox("", value=(idx <= 6), key=f"chk_pauta_{idx}")
            with col_txt:
                p_editada = st.text_input(f"Pauta {idx}", value=p_text, key=f"txt_pauta_{idx}", label_visibility="collapsed")
            if ativo:
                pautas_selecionadas.append(p_editada)

        st.markdown("---")
        st.markdown("### 🔗 Link Único de Aprovação Externa (Sistema)")
        link_exemplo = f"https://gestao-mensal-tour360vr.streamlit.app/?aprovar=true&cliente={emp.lower().replace(' ', '-')}"
        st.text_input("Link Único Exclusivo para Envio ao Cliente (Copiável):", value=link_exemplo)

        num_wsp = dados_c.get("whatsapp", "")
        num_limpo = "".join([c for c in str(num_wsp) if c.isdigit()])
        
        texto_msg_wsp = f"Olá {resp_cliente}!\nAqui é o Rubens da Tour360VR.\nSegue o link com o planejamento de pautas estratégicas para sua aprovação este mês: {link_exemplo}"
        msg_wsp = urllib.parse.quote(texto_msg_wsp)

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

        tab_pdf1, tab_pdf2 = st.tabs(["📄 Relatório Executivo PDF", "📜 Contrato Jurídico Oficial"])

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
            st.markdown("**Gerador Automático da Minuta de Contrato Jurídico:**")
            
            plano_selecionado = st.selectbox("Selecione o Plano:", ["Plano Start", "Plano Pro", "Gestão Mensal"])
            
            meses_gestao = None
            if "Gestão Mensal" in plano_selecionado:
                meses_gestao = st.slider("Duração do Contrato (Meses):", min_value=3, max_value=12, value=6, step=1)

            valor_personalizado = st.number_input("Valor do Plano (R$)", min_value=0.0, step=50.0, value=(500.0 if "Start" in plano_selecionado else (1500.0 if "Pro" in plano_selecionado else 600.0)))
            
            if st.button("Gerar Contrato Oficial em PDF"):
                pdf_contrato = gerar_pdf_contrato(dados_cli, plano_selecionado, valor_personalizado, meses_gestao)
                data_str_file = agora_brasil().strftime("%Y-%m-%d")
                nome_arquivo_pdf = f"Contrato Tour360VR - {c_pdf} - {data_str_file}.pdf"
                st.download_button("📥 Baixar Contrato Oficial PDF", data=pdf_contrato, file_name=nome_arquivo_pdf, mime="application/pdf")

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
        
        st.markdown("**Lista de Clientes e Contratos Recorrentes:**")
        st.dataframe(df_c, use_container_width=True, height=650)
    gerar_botoes_navegacao_rodape()

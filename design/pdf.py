"""Padrão de PDF Tour360VR (fundo claro para impressão). Usado pela Gestão e pelo Radar."""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.pdfbase.pdfmetrics import stringWidth

AZUL_ESCURO = colors.HexColor("#1E3A8A")
AZUL_LINK = colors.HexColor("#1E40AF")
SLATE_900 = colors.HexColor("#0F172A")
SLATE_600 = colors.HexColor("#475569")
LINHA = colors.HexColor("#BFDBFE")
ZEBRA = colors.HexColor("#F1F5F9")
BORDA = colors.HexColor("#CBD5E1")
PALETA = {"alta": "#F76C4A", "media": "#FFA733", "baixa": "#9DBE5A"}

RODAPE_PARTES = [
    ("tour360vr.com.br", "https://tour360vr.com.br"),
    ("contato@tour360vr.com.br", "mailto:contato@tour360vr.com.br"),
    ("(16) 99133-2121", "https://wa.me/5516991332121"),
]


def margens():
    return dict(rightMargin=40, leftMargin=40, topMargin=15, bottomMargin=55)


def logo_rl(caminho, w=45, h=45):
    if os.path.exists(caminho):
        return RLImage(caminho, width=w, height=h, kind="proportional")
    return Paragraph("<b>Tour360VR</b>", ParagraphStyle("fb", fontName="Helvetica-Bold"))


def cabecalho(titulo_html: str, caminho_logo: str):
    """Logo à esquerda, título à direita e linha divisória. Retorna lista de flowables."""
    t = Table(
        [[logo_rl(caminho_logo),
          Paragraph(titulo_html, ParagraphStyle("rh", fontName="Helvetica-Bold", fontSize=11,
                                                leading=14, alignment=2, textColor=AZUL_ESCURO))]],
        colWidths=[55, 477],
    )
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return [t, Spacer(1, 2), HRFlowable(width="100%", thickness=1.0, color=LINHA, spaceAfter=10)]


def rodape(canvas, doc):
    """Rodapé com links clicáveis, centralizado. Use em onFirstPage e onLaterPages."""
    canvas.saveState()
    canvas.setStrokeColor(LINHA)
    canvas.setLineWidth(0.8)
    canvas.line(40, 32, letter[0] - 40, 32)

    fonte, tam, y = "Helvetica", 8, 16
    sep = "   |   "
    largura = sum(stringWidth(t, fonte, tam) for t, _ in RODAPE_PARTES)
    largura += stringWidth(sep, fonte, tam) * (len(RODAPE_PARTES) - 1)
    x = (letter[0] - largura) / 2
    canvas.setFont(fonte, tam)
    for i, (txt, url) in enumerate(RODAPE_PARTES):
        w = stringWidth(txt, fonte, tam)
        canvas.setFillColor(AZUL_LINK)
        canvas.drawString(x, y, txt)
        canvas.linkURL(url, (x, y - 2, x + w, y + 9), relative=0)
        x += w
        if i < len(RODAPE_PARTES) - 1:
            canvas.setFillColor(SLATE_600)
            canvas.drawString(x, y, sep)
            x += stringWidth(sep, fonte, tam)
    canvas.restoreState()


def tabela_padrao(cabecalho_cols, linhas, larguras):
    """Tabela com cabeçalho azul-escuro, linhas zebradas e padding confortável."""
    st_th = ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.white)
    st_td = ParagraphStyle("td", fontName="Helvetica", fontSize=8, leading=10.5, textColor=colors.HexColor("#334155"))
    dados = [[Paragraph(h, st_th) for h in cabecalho_cols]]
    for linha in linhas:
        dados.append([c if not isinstance(c, str) else Paragraph(c, st_td) for c in linha])
    t = Table(dados, colWidths=larguras, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_ESCURO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ZEBRA]),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#94A3B8")),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, BORDA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def grafico_barras(categorias, valores, cores, largura=532, altura=150):
    """Gráfico de barras com cantos arredondados, rótulos de valor e linha de base."""
    d = Drawing(largura, altura)
    d.add(Rect(0, 0, largura, altura, rx=8, ry=8, fillColor=colors.HexColor("#F8FAFC"),
               strokeColor=BORDA, strokeWidth=0.5))
    n = len(valores)
    if n == 0:
        return d
    margem_x, base_y, topo = 30, 30, altura - 26
    slot = (largura - 2 * margem_x) / n
    bar_w = min(42, slot * 0.55)
    maximo = max(valores) or 1
    for i, (cat, val, cor) in enumerate(zip(categorias, valores, cores)):
        cx = margem_x + slot * i + slot / 2
        h = max((val / maximo) * (topo - base_y), 4)
        d.add(Rect(cx - bar_w / 2, base_y, bar_w, h, rx=4, ry=4, fillColor=colors.HexColor(cor), strokeColor=None))
        d.add(String(cx, base_y + h + 5, str(val), fontName="Helvetica-Bold", fontSize=9,
                     fillColor=SLATE_900, textAnchor="middle"))
        d.add(String(cx, 14, str(cat), fontName="Helvetica", fontSize=7.5,
                     fillColor=SLATE_600, textAnchor="middle"))
    d.add(Line(margem_x, base_y, largura - margem_x, base_y, strokeColor=BORDA, strokeWidth=0.8))
    return d

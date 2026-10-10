def gerar_pdf_oficial(dados, planos, plano_acao_extra="", concorrentes=[], paginas_selecionadas=[1, 2, 3, 4]):
    score = calcular_score_real(dados)
    capa_presente = 1 in paginas_selecionadas
    exibir_num = len(paginas_selecionadas) == 4
    
    pdf = PDFTour360Oficial(capa_incluida=capa_presente, exibir_numeracao=exibir_num)
    pdf.set_margins(21, 12, 12)
    pdf.set_auto_page_break(auto=False)

    # PÁGINA 1: CAPA
    if 1 in paginas_selecionadas:
        pdf.add_page()
        caminho_logo = obter_caminho_logo("tour360")
        if caminho_logo:
            try:
                pdf.image(caminho_logo, 90, 20.0, 38, 38)
            except Exception:
                pass

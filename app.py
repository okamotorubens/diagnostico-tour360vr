# -----------------------------------------------------------------------------
# TRATAMENTO SEGURO DE TEXTO (CORREÇÃO DE ESTRELAS E ACENTOS)
# -----------------------------------------------------------------------------
def conv(texto):
    if not texto:
        return ""
    limpo = str(texto)
    limpo = limpo.replace("•", "- ").replace("✓", "[OK] ").replace("X", "[X] ")
    limpo = limpo.replace("📍", "").replace("📞", "").replace("⭐", "*").replace("✉️", "").replace("🌐", "").replace("★", "*").replace("☆", "")
    return limpo.encode('latin-1', 'replace').decode('latin-1')

# -----------------------------------------------------------------------------
# GERADOR DE PDF (CORRIGIDO)
# -----------------------------------------------------------------------------
def gerar_pdf_oficial(dados, score):
    pdf = PDFTour360Oficial()
    pdf.set_auto_page_break(auto=True, margin=18)
    
    # -------------------------------------------------------------------------
    # PÁGINA 1: CAPA
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    try:
        pdf.image('Logo TOUR transparente.png', 82, 22, 46)
    except:
        pass

    pdf.set_y(74)
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 9, conv('DIAGNÓSTICO DE PRESENÇA DIGITAL'), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(0, 7, conv('GOOGLE MEU NEGÓCIO'), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 7, conv('Tour360VR'), align='C', ln=True)
    pdf.ln(14)

    w_capa = 150
    x_capa = (210 - w_capa) / 2.0
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rounded_rect(x_capa, 120, w_capa, 76, 4, 'FD')

    pdf.set_xy(x_capa, 127)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_capa, 8, conv(f"{dados['nome']}"), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(w_capa, 6, conv(f"Nota: {dados['nota']:.1f} *****  ({dados['avaliacoes']} avaliações no Google)"), align='C', ln=True)
    pdf.ln(2)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(w_capa, 5.5, conv(f"Endereço: {dados['endereco']}"), align='C', ln=True)
    pdf.cell(w_capa, 5.5, conv(f"Telefone: {dados['telefone']}"), align='C', ln=True)
    pdf.cell(w_capa, 5.5, conv(f"Website Cadastrado: {dados['website']}"), align='C', ln=True)
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 10.5)
    if score < 50:
        pdf.set_text_color(239, 68, 68)
        pdf.cell(w_capa, 6, conv("Status da Ficha: Crítico (Visibilidade Comprometida)"), align='C', ln=True)
    else:
        pdf.set_text_color(34, 197, 94)
        pdf.cell(w_capa, 6, conv("Status da Ficha: Otimizado e Em Expansão"), align='C', ln=True)

    # -------------------------------------------------------------------------
    # PÁGINA 2: DIAGNÓSTICO DETALHADO DA FICHA E SCORE GERAL
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    w_ficha = 150
    x_ficha = (210 - w_ficha) / 2.0
    
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(x_ficha, 34, w_ficha, 44, 3, 'FD')
    
    pdf.set_xy(x_ficha, 36)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(w_ficha, 4, conv('FICHA ANALISADA DO CLIENTE'), align='C', ln=True)
    
    pdf.set_x(x_ficha)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_ficha, 7, conv(f"{dados['nome']}"), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(245, 158, 11)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.5, conv(f"Nota {dados['nota']:.1f} *****   •   {dados['avaliacoes']} avaliações no Google"), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.5, conv(f"Endereço: {dados['endereco']}"), align='C', ln=True)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.5, conv(f"Telefone: {dados['telefone']}   |   Website: {dados['website']}"), align='C', ln=True)

    # Quadro do Score Geral (Texto e Valor Corrigidos)
    pdf.set_y(84)
    if score < 50:
        cr, cg, cb = 239, 68, 68
        status_txt = "STATUS CRÍTICO"
    elif score < 80:
        cr, cg, cb = 245, 158, 11
        status_txt = "STATUS MÉDIO"
    else:
        cr, cg, cb = 34, 197, 94
        status_txt = "ALTO DESEMPENHO"

    w_score = 140
    x_score = (210 - w_score) / 2.0
    
    pdf.set_fill_color(cr, cg, cb)
    pdf.set_draw_color(cr, cg, cb)
    pdf.rounded_rect(x_score, 84, w_score, 18, 3, 'FD')
    
    pdf.set_xy(x_score, 86)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(w_score, 6, conv(f"{score} / 100"), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.cell(w_score, 5, conv(f"SCORE GERAL DE OTIMIZAÇÃO ({status_txt})"), align='C', ln=True)

    # Título da Auditoria
    pdf.set_y(108)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('AUDITORIA DETALHADA DE PONTOS DE BUSCA'), align='C', ln=True)
    pdf.ln(8)

    pct_avaliacoes = min(int((dados['avaliacoes'] / 50.0) * 100), 100) if dados['avaliacoes'] > 0 else 10

    itens = [
        ("1. Fotos e Resolução Visual", 30 if not dados['tem_fotos_hd'] else 100, "Baixo", "Poucas fotos encontradas / antigas."),
        ("2. Tour Virtual 360° Interativo", 0 if not dados['tem_tour360'] else 100, "Ausente", "Nenhum Tour 360 detectado no perfil."),
        ("3. Categorias Principal e Secundárias", 50 if not dados['categorias_completas'] else 100, "Incompleto", "Sem categorias secundárias estratégicas."),
        ("4. Horários e Exceções (Feriados)", 40 if not dados['horarios_ok'] else 100, "Desatualizado", "Falta de horários especiais em feriados."),
        ("5. Website e Links de Conversão", 10 if dados['website'] == 'Não possui' else 100, "Falho", "Sem links diretos de contato e WhatsApp."),
        ("6. Avaliações no Google (Prova Social)", pct_avaliacoes, f"{dados['nota']}/5.0", f"{dados['avaliacoes']} avaliações registradas.")
    ]

    for titulo, pct, rotulo, desc in itens:
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(120, 4, conv(titulo), ln=False)
        
        pdf.set_font('Helvetica', 'B', 9)
        if pct < 40:
            pdf.set_text_color(239, 68, 68)
        elif pct < 80:
            pdf.set_text_color(245, 158, 11)
        else:
            pdf.set_text_color(34, 197, 94)
            
        pdf.cell(66, 4, conv(f"| {pct}% - {rotulo}"), align='R', ln=True)

        pdf.set_fill_color(226, 232, 240)
        pdf.rounded_rect(12, pdf.get_y(), 186, 3.5, 1.5, 'F')
        
        if pct < 40:
            pdf.set_fill_color(239, 68, 68)
        elif pct < 80:
            pdf.set_fill_color(245, 158, 11)
        else:
            pdf.set_fill_color(34, 197, 94)
            
        largura_barra = max(float(pct) * 1.86, 4.0)
        pdf.rounded_rect(12, pdf.get_y(), largura_barra, 3.5, 1.5, 'F')
        pdf.ln(4.5)

        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 3.5, conv(f"  Diagnóstico: {desc}"), ln=True)
        pdf.ln(3)

    # -------------------------------------------------------------------------
    # PÁGINA 3: PROPOSTA COMERCIAL
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    pdf.set_y(32)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('PROPOSTA COMERCIAL & ESTRUTURAÇÃO ESTRATÉGICA'), align='C', ln=True)
    pdf.ln(8)

    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(62, 161, 219)
    pdf.set_line_width(0.6)
    pdf.rounded_rect(12, pdf.get_y(), 186, 36, 2, 'FD')
    pdf.set_line_width(0.2)

    y_info = pdf.get_y() + 3
    pdf.set_xy(12, y_info)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(186, 5, conv('POR QUE SEU NEGÓCIO PRECISA DE OTIMIZAÇÃO PROFISSIONAL?'), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(51, 65, 85)
    txt_exp = (
        "Mais de 80% das buscas locais no Google e Maps resultam em uma ação imediata (ligação, rota ou mensagem).\n"
        "Perfis com fotos profissionais e Tour Virtual 360° geram até 2x mais interesse e permanecem no topo das buscas.\n"
        "Fichas incompletas ou desatualizadas perdem clientes diariamente para concorrentes diretos com nota mais alta."
    )
    pdf.set_x(12)
    pdf.multi_cell(186, 4.5, conv(txt_exp), align='C')
    
    pdf.set_y(98)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('PROPOSTA DE PLANOS E INVESTIMENTO'), align='C', ln=True)
    pdf.ln(8)

    y_p = pdf.get_y() + 2
    
    # --- PLANO START ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(12, y_p + 2, 52, 52, 2, 'FD')
    
    pdf.set_xy(12, y_p + 5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(52, 5, 'Plano Start', align='C', ln=True)
    
    pdf.set_xy(12, y_p + 12)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(62, 161, 219)
    pdf.cell(52, 6, 'R$ 500,00', align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(12, y_p + 21)
    pdf.cell(52, 4.2, conv('- Correção cadastral'), align='C', ln=True)
    pdf.set_x(12); pdf.cell(52, 4.2, conv('- Otimização de SEO'), align='C', ln=True)
    pdf.set_x(12); pdf.cell(52, 4.2, conv('- Ajuste de categorias'), align='C', ln=True)
    pdf.set_x(12); pdf.cell(52, 4.2, conv('- Inserção de links'), align='C', ln=True)

    # --- PLANO PRO ---
    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(30, 64, 175)
    pdf.set_line_width(1.0)
    pdf.rounded_rect(68, y_p - 4, 70, 62, 3, 'FD')
    pdf.set_line_width(0.2)
    
    pdf.set_xy(68, y_p)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(70, 5, conv('Plano Pro'), align='C', ln=True)
    
    pdf.set_xy(68, y_p + 5)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(70, 4, conv('(Recomendado)'), align='C', ln=True)
    
    pdf.set_xy(68, y_p + 11)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(70, 7, 'R$ 1.200,00', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.set_xy(68, y_p + 22)
    pdf.cell(70, 4.8, conv('- Tudo do Plano Start'), align='C', ln=True)
    pdf.set_x(68); pdf.cell(70, 4.8, conv('- Tour Virtual 360°'), align='C', ln=True)
    pdf.set_x(68); pdf.cell(70, 4.8, conv('- Ensaio Fotográfico HD'), align='C', ln=True)
    pdf.set_x(68); pdf.cell(70, 4.8, conv('- Relatório Visual de Entrega'), align='C', ln=True)

    # --- GESTÃO MENSAL ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(142, y_p + 2, 54, 52, 2, 'FD')
    
    pdf.set_xy(142, y_p + 5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(54, 5, conv('Gestão Mensal'), align='C', ln=True)
    
    pdf.set_xy(142, y_p + 12)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(62, 161, 219)
    pdf.cell(54, 6, 'R$ 600,00/mês', align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(142, y_p + 21)
    pdf.cell(54, 4.2, conv('- Postagens semanais'), align='C', ln=True)
    pdf.set_x(142); pdf.cell(54, 4.2, conv('- Gestão de avaliações'), align='C', ln=True)
    pdf.set_x(142); pdf.cell(54, 4.2, conv('- Atualização de fotos'), align='C', ln=True)
    pdf.set_x(142); pdf.cell(54, 4.2, conv('- Relatório mensal'), align='C', ln=True)

    # -------------------------------------------------------------------------
    # PÁGINA 4: CONTRATO DE PRESTAÇÃO DE SERVIÇOS
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    pdf.set_y(32)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('CONTRATO DE PRESTAÇÃO DE SERVIÇOS'), align='C', ln=True)
    pdf.ln(8)

    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85)
    
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATADA: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("Tour360VR, representada por Rubens H. Okamoto, CPF: 287.932.298-79 e Telefone: (16) 99133-2121.\n\n"))
    
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATANTE: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv(f"{dados['nome']}, Endereço: {dados['endereco']}.\n\n"))
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("A "))
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATADA "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("compromete-se a executar os serviços de otimização, reestruturação técnica e/ou produção de Tour Virtual 360° para o perfil do Google da "))
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATANTE.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA PRIMEIRA - DO OBJETO: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("Os serviços serão iniciados em até 5 dias úteis após o fornecimento dos acessos e informações necessárias ao perfil.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("O não pagamento na data acordada sujeitará o presente contrato à incidência de juros legais de mora e interrupção temporária dos serviços.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA TERCEIRA - SELEÇÃO DO PLANO CONTRATADO:\n"))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("(  ) Plano Start        (  ) Plano Pro        (  ) Gestão Mensal\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA QUARTA - CONDIÇÕES DE PAGAMENTO:\n"))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("(  ) A Vista    (  ) 2x Plano Start    (  ) 3x Plano Pro    (  ) Gestão Mensal - Vencimento Todo Dia: _____\n\n\n"))

    pdf.ln(16)

    pdf.cell(88, 5, '__________________________________', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, '__________________________________', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(88, 5, 'TOUR360VR (Rubens H. Okamoto)', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, conv(f"{dados['nome']}"), align='C', ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer# -----------------------------------------------------------------------------
# TRATAMENTO SEGURO DE TEXTO (CORREÇÃO DE ESTRELAS E ACENTOS)
# -----------------------------------------------------------------------------
def conv(texto):
    if not texto:
        return ""
    limpo = str(texto)
    limpo = limpo.replace("•", "- ").replace("✓", "[OK] ").replace("X", "[X] ")
    limpo = limpo.replace("📍", "").replace("📞", "").replace("⭐", "*").replace("✉️", "").replace("🌐", "").replace("★", "*").replace("☆", "")
    return limpo.encode('latin-1', 'replace').decode('latin-1')

# -----------------------------------------------------------------------------
# GERADOR DE PDF (CORRIGIDO)
# -----------------------------------------------------------------------------
def gerar_pdf_oficial(dados, score):
    pdf = PDFTour360Oficial()
    pdf.set_auto_page_break(auto=True, margin=18)
    
    # -------------------------------------------------------------------------
    # PÁGINA 1: CAPA
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    try:
        pdf.image('Logo TOUR transparente.png', 82, 22, 46)
    except:
        pass

    pdf.set_y(74)
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 9, conv('DIAGNÓSTICO DE PRESENÇA DIGITAL'), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(0, 7, conv('GOOGLE MEU NEGÓCIO'), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(0, 7, conv('Tour360VR'), align='C', ln=True)
    pdf.ln(14)

    w_capa = 150
    x_capa = (210 - w_capa) / 2.0
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(203, 213, 225)
    pdf.rounded_rect(x_capa, 120, w_capa, 76, 4, 'FD')

    pdf.set_xy(x_capa, 127)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_capa, 8, conv(f"{dados['nome']}"), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(245, 158, 11)
    pdf.cell(w_capa, 6, conv(f"Nota: {dados['nota']:.1f} *****  ({dados['avaliacoes']} avaliações no Google)"), align='C', ln=True)
    pdf.ln(2)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(w_capa, 5.5, conv(f"Endereço: {dados['endereco']}"), align='C', ln=True)
    pdf.cell(w_capa, 5.5, conv(f"Telefone: {dados['telefone']}"), align='C', ln=True)
    pdf.cell(w_capa, 5.5, conv(f"Website Cadastrado: {dados['website']}"), align='C', ln=True)
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 10.5)
    if score < 50:
        pdf.set_text_color(239, 68, 68)
        pdf.cell(w_capa, 6, conv("Status da Ficha: Crítico (Visibilidade Comprometida)"), align='C', ln=True)
    else:
        pdf.set_text_color(34, 197, 94)
        pdf.cell(w_capa, 6, conv("Status da Ficha: Otimizado e Em Expansão"), align='C', ln=True)

    # -------------------------------------------------------------------------
    # PÁGINA 2: DIAGNÓSTICO DETALHADO DA FICHA E SCORE GERAL
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    w_ficha = 150
    x_ficha = (210 - w_ficha) / 2.0
    
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(x_ficha, 34, w_ficha, 44, 3, 'FD')
    
    pdf.set_xy(x_ficha, 36)
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(w_ficha, 4, conv('FICHA ANALISADA DO CLIENTE'), align='C', ln=True)
    
    pdf.set_x(x_ficha)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(w_ficha, 7, conv(f"{dados['nome']}"), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.set_text_color(245, 158, 11)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.5, conv(f"Nota {dados['nota']:.1f} *****   •   {dados['avaliacoes']} avaliações no Google"), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.5, conv(f"Endereço: {dados['endereco']}"), align='C', ln=True)
    pdf.set_x(x_ficha)
    pdf.cell(w_ficha, 4.5, conv(f"Telefone: {dados['telefone']}   |   Website: {dados['website']}"), align='C', ln=True)

    # Quadro do Score Geral (Texto e Valor Corrigidos)
    pdf.set_y(84)
    if score < 50:
        cr, cg, cb = 239, 68, 68
        status_txt = "STATUS CRÍTICO"
    elif score < 80:
        cr, cg, cb = 245, 158, 11
        status_txt = "STATUS MÉDIO"
    else:
        cr, cg, cb = 34, 197, 94
        status_txt = "ALTO DESEMPENHO"

    w_score = 140
    x_score = (210 - w_score) / 2.0
    
    pdf.set_fill_color(cr, cg, cb)
    pdf.set_draw_color(cr, cg, cb)
    pdf.rounded_rect(x_score, 84, w_score, 18, 3, 'FD')
    
    pdf.set_xy(x_score, 86)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(w_score, 6, conv(f"{score} / 100"), align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 8.5)
    pdf.cell(w_score, 5, conv(f"SCORE GERAL DE OTIMIZAÇÃO ({status_txt})"), align='C', ln=True)

    # Título da Auditoria
    pdf.set_y(108)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('AUDITORIA DETALHADA DE PONTOS DE BUSCA'), align='C', ln=True)
    pdf.ln(8)

    pct_avaliacoes = min(int((dados['avaliacoes'] / 50.0) * 100), 100) if dados['avaliacoes'] > 0 else 10

    itens = [
        ("1. Fotos e Resolução Visual", 30 if not dados['tem_fotos_hd'] else 100, "Baixo", "Poucas fotos encontradas / antigas."),
        ("2. Tour Virtual 360° Interativo", 0 if not dados['tem_tour360'] else 100, "Ausente", "Nenhum Tour 360 detectado no perfil."),
        ("3. Categorias Principal e Secundárias", 50 if not dados['categorias_completas'] else 100, "Incompleto", "Sem categorias secundárias estratégicas."),
        ("4. Horários e Exceções (Feriados)", 40 if not dados['horarios_ok'] else 100, "Desatualizado", "Falta de horários especiais em feriados."),
        ("5. Website e Links de Conversão", 10 if dados['website'] == 'Não possui' else 100, "Falho", "Sem links diretos de contato e WhatsApp."),
        ("6. Avaliações no Google (Prova Social)", pct_avaliacoes, f"{dados['nota']}/5.0", f"{dados['avaliacoes']} avaliações registradas.")
    ]

    for titulo, pct, rotulo, desc in itens:
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(120, 4, conv(titulo), ln=False)
        
        pdf.set_font('Helvetica', 'B', 9)
        if pct < 40:
            pdf.set_text_color(239, 68, 68)
        elif pct < 80:
            pdf.set_text_color(245, 158, 11)
        else:
            pdf.set_text_color(34, 197, 94)
            
        pdf.cell(66, 4, conv(f"| {pct}% - {rotulo}"), align='R', ln=True)

        pdf.set_fill_color(226, 232, 240)
        pdf.rounded_rect(12, pdf.get_y(), 186, 3.5, 1.5, 'F')
        
        if pct < 40:
            pdf.set_fill_color(239, 68, 68)
        elif pct < 80:
            pdf.set_fill_color(245, 158, 11)
        else:
            pdf.set_fill_color(34, 197, 94)
            
        largura_barra = max(float(pct) * 1.86, 4.0)
        pdf.rounded_rect(12, pdf.get_y(), largura_barra, 3.5, 1.5, 'F')
        pdf.ln(4.5)

        pdf.set_font('Helvetica', '', 8.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 3.5, conv(f"  Diagnóstico: {desc}"), ln=True)
        pdf.ln(3)

    # -------------------------------------------------------------------------
    # PÁGINA 3: PROPOSTA COMERCIAL
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    pdf.set_y(32)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('PROPOSTA COMERCIAL & ESTRUTURAÇÃO ESTRATÉGICA'), align='C', ln=True)
    pdf.ln(8)

    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(62, 161, 219)
    pdf.set_line_width(0.6)
    pdf.rounded_rect(12, pdf.get_y(), 186, 36, 2, 'FD')
    pdf.set_line_width(0.2)

    y_info = pdf.get_y() + 3
    pdf.set_xy(12, y_info)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(186, 5, conv('POR QUE SEU NEGÓCIO PRECISA DE OTIMIZAÇÃO PROFISSIONAL?'), align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(51, 65, 85)
    txt_exp = (
        "Mais de 80% das buscas locais no Google e Maps resultam em uma ação imediata (ligação, rota ou mensagem).\n"
        "Perfis com fotos profissionais e Tour Virtual 360° geram até 2x mais interesse e permanecem no topo das buscas.\n"
        "Fichas incompletas ou desatualizadas perdem clientes diariamente para concorrentes diretos com nota mais alta."
    )
    pdf.set_x(12)
    pdf.multi_cell(186, 4.5, conv(txt_exp), align='C')
    
    pdf.set_y(98)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('PROPOSTA DE PLANOS E INVESTIMENTO'), align='C', ln=True)
    pdf.ln(8)

    y_p = pdf.get_y() + 2
    
    # --- PLANO START ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(12, y_p + 2, 52, 52, 2, 'FD')
    
    pdf.set_xy(12, y_p + 5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(52, 5, 'Plano Start', align='C', ln=True)
    
    pdf.set_xy(12, y_p + 12)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(62, 161, 219)
    pdf.cell(52, 6, 'R$ 500,00', align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(12, y_p + 21)
    pdf.cell(52, 4.2, conv('- Correção cadastral'), align='C', ln=True)
    pdf.set_x(12); pdf.cell(52, 4.2, conv('- Otimização de SEO'), align='C', ln=True)
    pdf.set_x(12); pdf.cell(52, 4.2, conv('- Ajuste de categorias'), align='C', ln=True)
    pdf.set_x(12); pdf.cell(52, 4.2, conv('- Inserção de links'), align='C', ln=True)

    # --- PLANO PRO ---
    pdf.set_fill_color(240, 249, 255)
    pdf.set_draw_color(30, 64, 175)
    pdf.set_line_width(1.0)
    pdf.rounded_rect(68, y_p - 4, 70, 62, 3, 'FD')
    pdf.set_line_width(0.2)
    
    pdf.set_xy(68, y_p)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(70, 5, conv('Plano Pro'), align='C', ln=True)
    
    pdf.set_xy(68, y_p + 5)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(255, 61, 61)
    pdf.cell(70, 4, conv('(Recomendado)'), align='C', ln=True)
    
    pdf.set_xy(68, y_p + 11)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(30, 64, 175)
    pdf.cell(70, 7, 'R$ 1.200,00', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.set_xy(68, y_p + 22)
    pdf.cell(70, 4.8, conv('- Tudo do Plano Start'), align='C', ln=True)
    pdf.set_x(68); pdf.cell(70, 4.8, conv('- Tour Virtual 360°'), align='C', ln=True)
    pdf.set_x(68); pdf.cell(70, 4.8, conv('- Ensaio Fotográfico HD'), align='C', ln=True)
    pdf.set_x(68); pdf.cell(70, 4.8, conv('- Relatório Visual de Entrega'), align='C', ln=True)

    # --- GESTÃO MENSAL ---
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rounded_rect(142, y_p + 2, 54, 52, 2, 'FD')
    
    pdf.set_xy(142, y_p + 5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(54, 5, conv('Gestão Mensal'), align='C', ln=True)
    
    pdf.set_xy(142, y_p + 12)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(62, 161, 219)
    pdf.cell(54, 6, 'R$ 600,00/mês', align='C', ln=True)
    
    pdf.set_font('Helvetica', '', 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.set_xy(142, y_p + 21)
    pdf.cell(54, 4.2, conv('- Postagens semanais'), align='C', ln=True)
    pdf.set_x(142); pdf.cell(54, 4.2, conv('- Gestão de avaliações'), align='C', ln=True)
    pdf.set_x(142); pdf.cell(54, 4.2, conv('- Atualização de fotos'), align='C', ln=True)
    pdf.set_x(142); pdf.cell(54, 4.2, conv('- Relatório mensal'), align='C', ln=True)

    # -------------------------------------------------------------------------
    # PÁGINA 4: CONTRATO DE PRESTAÇÃO DE SERVIÇOS
    # -------------------------------------------------------------------------
    pdf.add_page()
    
    pdf.set_y(32)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, conv('CONTRATO DE PRESTAÇÃO DE SERVIÇOS'), align='C', ln=True)
    pdf.ln(8)

    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85)
    
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATADA: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("Tour360VR, representada por Rubens H. Okamoto, CPF: 287.932.298-79 e Telefone: (16) 99133-2121.\n\n"))
    
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATANTE: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv(f"{dados['nome']}, Endereço: {dados['endereco']}.\n\n"))
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("A "))
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATADA "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("compromete-se a executar os serviços de otimização, reestruturação técnica e/ou produção de Tour Virtual 360° para o perfil do Google da "))
    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CONTRATANTE.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA PRIMEIRA - DO OBJETO: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("Os serviços serão iniciados em até 5 dias úteis após o fornecimento dos acessos e informações necessárias ao perfil.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA SEGUNDA - DAS OBRIGAÇÕES: "))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("O não pagamento na data acordada sujeitará o presente contrato à incidência de juros legais de mora e interrupção temporária dos serviços.\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA TERCEIRA - SELEÇÃO DO PLANO CONTRATADO:\n"))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("(  ) Plano Start        (  ) Plano Pro        (  ) Gestão Mensal\n\n"))

    pdf.set_font('Helvetica', 'B', 9.5)
    pdf.write(5.5, conv("CLÁUSULA QUARTA - CONDIÇÕES DE PAGAMENTO:\n"))
    pdf.set_font('Helvetica', '', 9.5)
    pdf.write(5.5, conv("(  ) A Vista    (  ) 2x Plano Start    (  ) 3x Plano Pro    (  ) Gestão Mensal - Vencimento Todo Dia: _____\n\n\n"))

    pdf.ln(16)

    pdf.cell(88, 5, '__________________________________', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, '__________________________________', align='C', ln=True)
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(88, 5, 'TOUR360VR (Rubens H. Okamoto)', align='C')
    pdf.cell(10, 5, '')
    pdf.cell(88, 5, conv(f"{dados['nome']}"), align='C', ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

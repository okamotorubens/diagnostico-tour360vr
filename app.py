# PÁGINA 2: AUDITORIA DETALHADA
    if 2 in paginas_selecionadas:
        pdf.add_page()
        pdf.set_xy(21, 29)
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(177, 8, conv('AUDITORIA DETALHADA DE PONTOS DE BUSCA'), align='C', ln=True)

        # Quadro da Empresa Analisada expandido para a largura total útil (177)
        w_ficha, x_ficha, y_ficha, h_ficha = 177, 21.0, 43.0, 15.0
        pdf.set_fill_color(248, 250, 252)
        pdf.set_draw_color(226, 232, 240)
        pdf.rounded_rect(x_ficha, y_ficha, w_ficha, h_ficha, 2.5, 'FD')
        
        pdf.set_xy(x_ficha, y_ficha + 2.0)
        pdf.set_font('Helvetica', 'B', 12.0)
        pdf.set_text_color(30, 64, 175)
        pdf.cell(w_ficha, 5.0, conv(f"{dados.get('nome') or 'Empresa Analisada'}"), align='C', ln=True)

        pdf.set_x(x_ficha)
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(245, 158, 11)
        pdf.cell(w_ficha, 4.5, conv(f"Nota {dados.get('nota', 0.0):.1f} *   -   {dados.get('avaliacoes', 0)} avaliações no Google"), align='C', ln=True)

        # Quadro do SCORE GERAL ampliado (Largura: 65, Altura: 15.0)
        w_box_score = 65
        h_box_score = 15.0
        x_box_score = 21.0 + (177.0 - w_box_score) / 2.0
        y_box_score = 63.0

        if score < 50: cr, cg, cb, status_txt = 239, 68, 68, "STATUS CRÍTICO"
        elif score < 80: cr, cg, cb, status_txt = 245, 158, 11, "STATUS MÉDIO"
        else: cr, cg, cb, status_txt = 22, 128, 61, "ALTO DESEMPENHO"

        pdf.set_fill_color(240, 249, 255)
        pdf.set_draw_color(62, 161, 219)
        pdf.set_line_width(0.4)
        pdf.rounded_rect(x_box_score, y_box_score, w_box_score, h_box_score, 2.5, 'FD')
        pdf.set_line_width(0.2)

        # Nota e barra maiores
        pdf.set_font('Helvetica', 'B', 18)
        w_num = pdf.get_string_width(f"{score} ")
        w_bar = pdf.get_string_width("/ 100")
        x_start = x_box_score + (w_box_score - (w_num + w_bar)) / 2.0

        pdf.set_xy(x_start, y_box_score + 1.2)
        pdf.set_text_color(cr, cg, cb)
        pdf.cell(w_num, 6.0, f"{score} ", align='L')
        
        pdf.set_text_color(15, 23, 42)
        pdf.cell(w_bar, 6.0, "/ 100", align='L', ln=True)
        
        # Texto do status maior
        pdf.set_xy(x_box_score, y_box_score + 8.2)
        pdf.set_font('Helvetica', 'B', 8.5)
        pdf.set_text_color(cr, cg, cb)
        pdf.cell(w_box_score, 4.0, conv(f"SCORE GERAL ({status_txt})"), align='C', ln=True)

        pct_avaliacoes = min(int((dados.get('avaliacoes', 0) / 50.0) * 100), 100) if dados.get('avaliacoes', 0) > 0 else 10
        pct_fotos = 100 if dados.get('tem_fotos_hd') else 30
        pct_tour = 100 if dados.get('tem_tour360') else 30
        pct_cat = 100 if dados.get('categorias_completas') else 50
        pct_hor = 100 if dados.get('horarios_ok') else 40
        pct_web = 100 if dados.get('website') != 'Não possui' and dados.get('website') != '' else 10
        pct_desc = 100 if dados.get('tem_descricao', True) else 30
        pct_atrib = 100 if dados.get('atributos_ok', True) else 40
        pct_resp = 100 if dados.get('resposta_avaliacoes_ok', False) else 30

        desc_fotos = "Atende ao volume recomendado de fotos em HD." if dados.get('tem_fotos_hd') else "Poucas fotos encontradas / antigas no perfil."
        rotulo_tour = "Ativo" if dados.get('tem_tour360') else "Pendente de Validação"
        desc_tour = "Tour Virtual 360° ativo e integrado." if dados.get('tem_tour360') else "Não detectado via API. Necessário checagem manual na ficha."
        desc_cat = "Atende às categorias recomendadas." if dados.get('categorias_completas') else "Ajuste necessário em categorias secundárias."
        desc_web = f"Website oficial: {dados.get('website')}" if dados.get('website') != 'Não possui' and dados.get('website') != '' else "Falta link de website cadastrado para conversão."
        desc_desc = "Resumo editorial ativo no perfil." if dados.get('tem_descricao', True) else "Descrição da empresa incompleta ou ausente."
        desc_atrib = "Atributos de serviços ativos." if dados.get('atributos_ok', True) else "Falta cadastrar atributos de acessibilidade/serviços."
        desc_resp = "Frequência ativa de respostas do proprietário." if dados.get('resposta_avaliacoes_ok', False) else "Falta de respostas oficiais às avaliações."

        itens = [
            ("1. Fotos e Resolução Visual", pct_fotos, "Alto" if dados.get('tem_fotos_hd') else "Baixo", desc_fotos),
            ("2. Tour Virtual 360° Interativo", pct_tour, rotulo_tour, desc_tour),
            ("3. Categorias Principal e Secundárias", pct_cat, "Completo" if dados.get('categorias_completas') else "Incompleto", desc_cat),
            ("4. Horários e Exceções (Feriados)", pct_hor, "Atualizado" if dados.get('horarios_ok') else "Desatualizado", "Falta de horários em feriados."),
            ("5. Website e Links de Conversão", pct_web, "Ativo" if dados.get('website') != 'Não possui' and dados.get('website') != '' else "Falho", desc_web),
            ("6. Avaliações no Google (Prova Social)", pct_avaliacoes, f"{dados.get('nota', 0.0)}/5.0", f"{dados.get('avaliacoes', 0)} avaliações."),
            ("7. Resumo Editorial & Descrição", pct_desc, "Completo" if dados.get('tem_descricao', True) else "Ausente", desc_desc),
            ("8. Atributos de Acessibilidade/Serviços", pct_atrib, "Ativo" if dados.get('atributos_ok', True) else "Pendente", desc_atrib),
            ("9. Interação e Resposta a Avaliações", pct_resp, "Ativo" if dados.get('resposta_avaliacoes_ok', False) else "Pendente", desc_resp)
        ]

        y_start_itens, h_slot = 91.0, 10.5
        for idx_item, (titulo, pct, rotulo, desc) in enumerate(itens):
            y_curr = y_start_itens + (idx_item * h_slot)
            pdf.set_xy(21, y_curr)
            pdf.set_font('Helvetica', 'B', 9.5)
            pdf.set_text_color(30, 41, 59)
            pdf.cell(122, 3.2, conv(titulo), border=0)
            
            pdf.set_font('Helvetica', 'B', 9.5)
            if pct < 40: pdf.set_text_color(239, 68, 68)
            elif pct < 80: pdf.set_text_color(245, 158, 11)
            else: pdf.set_text_color(22, 128, 61)
                
            pdf.cell(55, 3.2, conv(rotulo), border=0, align='R')

            y_bar = y_curr + 3.6
            pdf.set_fill_color(226, 232, 240)
            pdf.rounded_rect(21, y_bar, 177, 1.5, 0.5, 'F')
            
            if pct < 40: pdf.set_fill_color(239, 68, 68)
            elif pct < 80: pdf.set_fill_color(245, 158, 11)
            else: pdf.set_fill_color(22, 128, 61)
                
            pdf.rounded_rect(21, y_bar, max(float(pct) * 1.77, 4.0), 1.5, 0.5, 'F')

            pdf.set_xy(21, y_bar + 2.2)
            pdf.set_font('Helvetica', '', 8.5)
            pdf.set_text_color(71, 85, 105)
            pdf.cell(177, 3.0, conv(f"   Diagnóstico: {desc[:90]}"), border=0)

        concorrentes_filtrados = [c for c in concorrentes if c.get("nome", "").strip() != ""]
        if concorrentes_filtrados:
            pdf.set_xy(21, 194.0)
            pdf.set_font('Helvetica', 'B', 9.5)
            pdf.set_text_color(30, 64, 175)
            pdf.cell(0, 4.0, conv("ANÁLISE AUTOMÁTICA DE CONCORRENTES DO SEGMENTO"), border=0)

            w_emp, w_item, w_score, h_row = 53, 11.0, 25.0, 4.6
            y_table = 199.0
            pdf.set_xy(21, y_table)
            pdf.set_fill_color(30, 64, 175)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 9.0)
            
            pdf.cell(w_emp, h_row, conv(" Empresa / Concorrente"), border=0, fill=True)
            pdf.cell(w_item, h_row, conv("1.Fotos"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("2.360°"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("3.Categ"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("4.Horár"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("5.Web"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("6.Nota"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("7.Desc"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("8.Atrib"), border=0, fill=True, align='C')
            pdf.cell(w_item, h_row, conv("9.Resp"), border=0, fill=True, align='C')
            pdf.cell(w_score, h_row, conv("Score Geral"), border=0, fill=True, align='C')

            def celula_sim_nao(pdf_obj, w, h, valor):
                if valor == "Sim":
                    pdf_obj.set_fill_color(220, 252, 231)
                    pdf_obj.set_text_color(22, 101, 52)
                else:
                    pdf_obj.set_fill_color(254, 226, 226)
                    pdf_obj.set_text_color(153, 27, 27)
                pdf_obj.cell(w, h, conv(valor), border='B', fill=True, align='C')

            y_r1 = y_table + h_row
            pdf.set_xy(21, y_r1)
            pdf.set_fill_color(240, 249, 255)
            pdf.set_font('Helvetica', 'B', 8.5)
            pdf.set_text_color(30, 64, 175)
            pdf.cell(w_emp, h_row, conv(f" {str(dados.get('nome', ''))[:25]}"), border='B', fill=True)
            
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('tem_fotos_hd') else "Não")
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('tem_tour360') else "Não")
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('categorias_completas') else "Não")
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('horarios_ok') else "Não")
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('website') and dados.get('website') != 'Não possui' else "Não")
            
            pdf.set_fill_color(240, 249, 255)
            pdf.set_text_color(30, 64, 175)
            pdf.cell(w_item, h_row, conv(f"{dados.get('nota', 0.0):.1f}"), border='B', fill=True, align='C')
            
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('tem_descricao') else "Não")
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('atributos_ok') else "Não")
            celula_sim_nao(pdf, w_item, h_row, "Sim" if dados.get('resposta_avaliacoes_ok') else "Não")
            
            pdf.set_fill_color(240, 249, 255)
            pdf.set_font('Helvetica', 'B', 8.5)
            pdf.set_text_color(30, 64, 175)
            pdf.cell(w_score, h_row, conv(f"{score} / 100"), border='B', fill=True, align='C')

            pdf.set_font('Helvetica', '', 8.5)
            for idx_c, c in enumerate(concorrentes_filtrados):
                y_rc = y_r1 + ((idx_c + 1) * h_row)
                score_conc = calcular_score_concorrente(c)
                pdf.set_xy(21, y_rc)
                pdf.set_fill_color(255, 255, 255)
                pdf.set_text_color(51, 65, 85)
                
                pdf.cell(w_emp, h_row, conv(f" {c.get('nome', '')[:25]}"), border='B', fill=True)
                celula_sim_nao(pdf, w_item, h_row, c.get('tem_fotos_hd', 'Não'))
                celula_sim_nao(pdf, w_item, h_row, c.get('tem_tour360', 'Não'))
                celula_sim_nao(pdf, w_item, h_row, c.get('categorias_ok', 'Não'))
                celula_sim_nao(pdf, w_item, h_row, c.get('horarios_ok', 'Não'))
                celula_sim_nao(pdf, w_item, h_row, c.get('tem_website', 'Não'))
                
                pdf.set_fill_color(255, 255, 255)
                pdf.set_text_color(51, 65, 85)
                pdf.cell(w_item, h_row, conv(f"{float(c.get('nota', 0.0)):.1f}"), border='B', fill=True, align='C')
                
                celula_sim_nao(pdf, w_item, h_row, c.get('tem_descricao', 'Não'))
                celula_sim_nao(pdf, w_item, h_row, c.get('atributos_ok', 'Não'))
                celula_sim_nao(pdf, w_item, h_row, c.get('respostas_ok', 'Não'))
                
                pdf.set_fill_color(255, 255, 255)
                pdf.set_font('Helvetica', 'B', 8.5)
                pdf.set_text_color(51, 65, 85)
                pdf.cell(w_score, h_row, conv(f"{score_conc} / 100"), border='B', fill=True, align='C')
                pdf.set_font('Helvetica', '', 8.5)

        if plano_acao_extra and plano_acao_extra.strip() != "":
            w_extra, x_extra, y_extra, h_box_extra = 177, 21.0, 237.0, 27.0
            pdf.set_fill_color(240, 249, 255)
            pdf.set_draw_color(62, 161, 219)
            pdf.set_line_width(0.4)
            pdf.rounded_rect(x_extra, y_extra, w_extra, h_box_extra, 2.0, 'FD')
            pdf.set_line_width(0.2)
            
            pdf.set_xy(x_extra, y_extra + 2.5)
            pdf.set_font('Helvetica', 'B', 8.2)
            pdf.set_text_color(30, 64, 175)
            pdf.cell(w_extra, 3.5, conv("PLANO DE AÇÃO E APONTAMENTOS ESTRATÉGICOS PERSONALIZADOS:"), align='C', border=0)
            
            pdf.set_xy(x_extra + 4, y_extra + 8.5)
            pdf.set_font('Helvetica', '', 7.8)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(w_extra - 8, 3.5, conv(plano_acao_extra), align='C')

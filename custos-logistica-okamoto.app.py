class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer_content(num_pages)
            super().showPage()
        super().save()

    def draw_footer_content(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#475569'))
        
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(35, 38, 575, 38)
        
        p_num = self._pageNumber
        
        # Links no rodapé com nomes unicamente prefixados para evitar colisão no ReportLab
        self.setFillColor(colors.HexColor('#1e3a8a'))
        self.drawString(135, 24, "okamotomidiasvisuais.com.br")
        self.linkURL("https://okamotomidiasvisuais.com.br/", (135, 22, 248, 34), relative=0, name=f"lnk_web_{p_num}")
        
        self.setFillColor(colors.HexColor('#475569'))
        self.drawString(252, 24, "|")
        
        self.setFillColor(colors.HexColor('#1e3a8a'))
        self.drawString(262, 24, "contato@okamotomidiasvisuais.com.br")
        self.linkURL("mailto:contato@okamotomidiasvisuais.com.br", (262, 22, 428, 34), relative=0, name=f"lnk_mail_{p_num}")
        
        self.setFillColor(colors.HexColor('#475569'))
        self.drawString(432, 24, "|")
        
        self.setFillColor(colors.HexColor('#1e3a8a'))
        self.drawString(442, 24, "WhatsApp: 16 99133 2121")
        self.linkURL("https://wa.me/5516991332121", (442, 22, 530, 34), relative=0, name=f"lnk_wa_{p_num}")
        
        self.setFillColor(colors.HexColor('#475569'))
        self.drawRightString(575, 24, f"Página {p_num} de {page_count}")
        self.restoreState()

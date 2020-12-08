from fpdf import FPDF, HTMLMixin
from PydoNovosoft.utils import Utils



class HTML2PDF(FPDF, HTMLMixin):

    def set_data(self, route=None, vehicle=None, start_date=None, tolerancia=1,total_pages=1):
        self._route = route
        self._vehicle = vehicle
        self._start_date = start_date
        self._tolerancia = str(tolerancia)+" min."
        self.total_pages = total_pages

    def header(self):
        self.set_font('Arial', 'B', 15)
        # Move to the right
        # Framed title
        self.cell(300, 10, 'MANZANILLO, COLIMA', 0, 0, 'C')
        # Line break
        self.ln(10)
        self.cell(300, 10, 'SISTEMA TUCA', 0, 0, 'C')
        self.ln(10)
        self.cell(300, 10, 'REPORTE DE CHECADAS', 0, 0, 'C')
        self.ln(10)
        self.cell(50, 10, "RUTA "+self._route, 0, 0, 'C')
        self.cell(155, 10, "No. Economico: "+self._vehicle, 0, 0, 'C')
        self.cell(100, 10, "Fecha: "+Utils.format_date(Utils.string_to_date(
            self._start_date, "%Y-%m-%d %H:%M:%S"), "%d/%m/%Y"), 0, 0, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 10)
        # Print centered page number
        self.cell(0, 10, 'Pagina '+str(self.page_no())+'/'+str(self.total_pages), 0, 0, 'C')


class PDFEmpty(FPDF, HTMLMixin):


    def header(self):
        self.set_font('Arial', 'B', 15)
        # Move to the right
        # Framed title
        self.cell(300, 10, 'MANZANILLO, COLIMA', 0, 0, 'C')
        # Line break
        self.ln(10)
        self.cell(300, 10, 'SISTEMA TUCA', 0, 0, 'C')
        self.ln(10)
        self.cell(300, 10, 'REPORTE DE CHECADAS', 0, 0, 'C')
        self.ln(20)
        self.cell(50, 10, "RUTA ", 0, 0, 'C')
        self.cell(155, 10, "No. Economico: ", 0, 0, 'C')
        self.cell(100, 10, "Fecha: ", 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 10)
        # Print centered page number
        self.cell(0, 10, 'Pagina 1', 0, 0, 'C')

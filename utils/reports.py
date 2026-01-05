"""
Módulo para generación de reportes PDF para CHAMPILYTICS.
Utiliza FPDF para crear reportes ejecutivos con datos de métricas sociales.
"""

from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        # Logo o título
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'CHAMPILYTICS - Reporte Ejecutivo', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')


def generate_pdf_report(school_name, period, kpis, anomalies, health_score):
    """
    Genera un reporte PDF ejecutivo con los datos proporcionados.

    Args:
        school_name (str): Nombre del colegio
        period (str): Periodo del reporte (YYYY-MM)
        kpis (dict): Diccionario con KPIs {'seguidores': {'valor': int, 'delta': str}, ...}
        anomalies (list): Lista de anomalías detectadas
        health_score (float): Score de salud digital

    Returns:
        bytes: Contenido del PDF en bytes
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # Encabezado
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'Colegio: {school_name}', 0, 1)
    pdf.cell(0, 10, f'Periodo: {period}', 0, 1)
    pdf.ln(10)

    # Resumen de Salud
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Resumen de Salud Digital', 0, 1)
    pdf.set_font('Arial', '', 16)
    color = (0, 128, 0) if health_score > 80 else (255, 165, 0) if health_score > 60 else (255, 0, 0)
    pdf.set_text_color(*color)
    pdf.cell(0, 15, f'Score: {health_score:.1f}/100', 0, 1)
    pdf.set_text_color(0, 0, 0)  # Reset color
    pdf.ln(5)

    # Sección de KPIs
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Métricas Principales', 0, 1)
    pdf.ln(5)

    # Tabla de KPIs
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 10, 'Métrica', 1)
    pdf.cell(30, 10, 'Valor', 1)
    pdf.cell(40, 10, 'Variación', 1)
    pdf.ln()

    pdf.set_font('Arial', '', 10)
    for kpi_name, data in kpis.items():
        pdf.cell(40, 10, kpi_name.capitalize(), 1)
        pdf.cell(30, 10, str(data.get('valor', 'N/A')), 1)
        pdf.cell(40, 10, data.get('delta', 'N/A'), 1)
        pdf.ln()

    pdf.ln(10)

    # Sección de Hallazgos
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Hallazgos y Anomalías', 0, 1)
    pdf.ln(5)

    if anomalies:
        pdf.set_font('Arial', '', 10)
        for anomaly in anomalies:
            pdf.multi_cell(0, 8, f'- {anomaly}')
            pdf.ln(2)
    else:
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, 'No se detectaron anomalías significativas en este periodo.', 0, 1)

    # Salida a bytes
    pdf_string = pdf.output(dest='S')
    return pdf_string.encode('latin-1')
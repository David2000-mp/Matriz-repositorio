"""
Módulo para la generación de reportes personalizados en formato PDF.
Versión corregida para integración con Streamlit.
"""

from fpdf import FPDF
import plotly.io as pio
import os
import pandas as pd
import uuid

class ReportBuilder(FPDF):
    def __init__(self, df: pd.DataFrame, entity_name: str = "Reporte"):
        """
        Inicializa el reporte con los datos (DF) y el nombre de la entidad.
        """
        super().__init__()
        self.df = df
        # Validación de seguridad: Si entity_name es None, usar string por defecto
        self.entity_name = entity_name if entity_name else "Entidad Desconocida"
        self.output_path = f"reporte_temp_{uuid.uuid4().hex}.pdf" # Nombre único para evitar colisiones
        
        # Configuración inicial del PDF
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font("Arial", size=12)

    def header(self):
        # Encabezado en todas las páginas
        self.set_font("Arial", "B", 10)
        self.cell(0, 10, f"Reporte de Desempeño: {self.encode_text(self.entity_name)}", 0, 1, "R")
        self.ln(5)

    def encode_text(self, text):
        """Manejo robusto de codificación (latin-1) evitando errores NoneType."""
        if text is None:
            return ""
        if not isinstance(text, str):
            text = str(text)
        try:
            return text.encode('latin-1', 'replace').decode('latin-1')
        except Exception:
            return text  # Fallback si falla la codificación

    def add_cover_page(self):
        """Agrega una portada al reporte."""
        print("Paso 1: Generando portada...")
        # (Ya estamos en la página 1 por el __init__)
        self.ln(60)
        self.set_font("Arial", size=24, style="B")
        self.cell(0, 10, self.encode_text(self.entity_name), ln=True, align="C")
        self.ln(10)
        self.set_font("Arial", size=16)
        self.cell(0, 10, "Reporte Mensual de Redes Sociales", ln=True, align="C")
        self.add_page() # Salto de página para lo siguiente

    def add_kpis_table(self):
        """Agrega una tabla de KPIs basada en el DF."""
        print("Paso 2: Generando tabla de KPIs...")
        self.set_font("Arial", size=14, style="B")
        self.cell(0, 10, "Tabla de Datos", ln=True, align="L")
        self.ln(5)

        # Seleccionar columnas clave para que quepan
        cols_to_show = [c for c in self.df.columns if c in ['fecha', 'plataforma', 'seguidores', 'interacciones', 'engagement_rate']]
        if not cols_to_show:
            cols_to_show = self.df.columns[:5] # Fallback
            
        df_table = self.df[cols_to_show].head(15) # Solo las primeras 15 filas para no saturar

        # Configuración de celdas
        col_width = 190 / len(cols_to_show)
        self.set_font("Arial", size=10, style="B")
        
        # Cabeceras
        for col in cols_to_show:
            self.cell(col_width, 10, self.encode_text(col.upper()), border=1, align="C")
        self.ln()

        # Filas
        self.set_font("Arial", size=10)
        for _, row in df_table.iterrows():
            for col in cols_to_show:
                val = str(row[col])
                # Truncar si es muy largo
                if len(val) > 15: val = val[:12] + "..."
                self.cell(col_width, 10, self.encode_text(val), border=1, align="C")
            self.ln()
        
        self.add_page()

    def add_analysis_summary(self):
        """
        Agrega un resumen analítico comparando el primer y último mes registrado.
        """
        print("Paso 2.5: Generando resumen analítico...")
        try:
            # Ordenar por fecha para obtener el primer y último registro
            self.df = self.df.sort_values(by="fecha")
            first_row = self.df.iloc[0]
            last_row = self.df.iloc[-1]

            # Extraer métricas clave
            seguidores_inicio = first_row["seguidores"]
            seguidores_fin = last_row["seguidores"]
            crecimiento = ((seguidores_fin - seguidores_inicio) / seguidores_inicio) * 100 if seguidores_inicio > 0 else 0

            # Agregar texto al PDF
            self.set_font("Arial", size=12)
            self.cell(0, 10, "Análisis Automático", ln=True, align="L")
            self.ln(5)
            self.set_font("Arial", size=10)
            self.multi_cell(0, 10, self.encode_text(
                f"La institución {self.entity_name} inició con {seguidores_inicio:,} seguidores y finalizó con {seguidores_fin:,}, "
                f"representando un crecimiento del {crecimiento:.2f}%."
            ))
            self.ln(10)
        except Exception as e:
            print(f"   [ERROR ANALISIS]: {e}")
            self.set_text_color(255, 0, 0)
            self.cell(0, 10, f"No se pudo generar el análisis: {str(e)}", ln=True)
            self.set_text_color(0, 0, 0)

    def add_trend_graphs(self):
        """
        Genera gráficas simples usando Plotly y las inserta con manejo de errores.
        """
        print("Paso 3: Intentando generar gráficas...")
        try:
            import plotly.express as px

            # Gráfica 1: Seguidores
            fig1 = px.line(self.df, x="fecha", y="seguidores", title="Evolución de Seguidores")
            img_path1 = "temp_chart_1.png"
            pio.write_image(fig1, img_path1, format="png", width=800, height=400)

            self.set_font("Arial", size=14, style="B")
            self.cell(0, 10, "Tendencias Gráficas", ln=True)
            self.image(img_path1, x=10, w=190)
            self.ln(10)

            os.remove(img_path1)
            print("   -> Gráfica 1 insertada")

        except Exception as e:
            print(f"   [ERROR GRAFICAS]: {e}")
            self.set_text_color(255, 0, 0)
            self.cell(0, 10, f"No se pudieron generar las gráficas: {str(e)}", ln=True)
            self.set_text_color(0, 0, 0)

    def generate(self, sections: list):
        """
        Orquesta la generación del reporte y retorna los BYTES del PDF.
        """
        print(f"Paso 0: Iniciando reporte para secciones: {sections}")

        # Lógica de secciones
        # Siempre ponemos portada
        self.add_cover_page()

        if "kpis" in sections:
            self.add_kpis_table()

        if "graficas" in sections:
            self.add_trend_graphs()

        if "analisis" in sections:
            self.add_analysis_summary()

        # Finalizar y guardar temporalmente
        print("Paso 4: Guardando archivo temporal...")
        self.output(self.output_path, "F")

        # Leer los bytes para devolverlos a Streamlit
        print("Paso 5: Leyendo bytes para descarga...")
        with open(self.output_path, "rb") as f:
            pdf_bytes = f.read()

        # Limpieza (borrar el archivo temp del servidor)
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

        return pdf_bytes
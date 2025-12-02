"""
Módulo para la generación de reportes personalizados en CHAMPILYTICS.
Permite seleccionar secciones específicas para incluir en los reportes.
"""

import streamlit as st
import pandas as pd
from typing import List

def generate_report(sections: List[str], data: pd.DataFrame) -> None:
    """
    Genera un reporte personalizado basado en las secciones seleccionadas.

    Args:
        sections (List[str]): Lista de secciones a incluir en el reporte.
        data (pd.DataFrame): Datos a utilizar en el reporte.
    """
    st.title("📄 Reporte Personalizado")

    if "Resumen General" in sections:
        st.header("📊 Resumen General")
        st.write("Incluye un resumen de las métricas principales.")
        st.dataframe(data.describe())

    if "Gráficos de Tendencias" in sections:
        st.header("📈 Gráficos de Tendencias")
        st.write("Visualización de tendencias a lo largo del tiempo.")
        st.line_chart(data)

    if "Análisis por Institución" in sections:
        st.header("🏫 Análisis por Institución")
        st.write("Desglose de métricas por institución.")
        for institution in data["entidad"].unique():
            st.subheader(f"Institución: {institution}")
            st.dataframe(data[data["entidad"] == institution])

    if "Conclusiones" in sections:
        st.header("📝 Conclusiones")
        st.write("Resumen de hallazgos clave y recomendaciones.")

    st.success("✅ Reporte generado exitosamente.")


def render_report_generator(data: pd.DataFrame) -> None:
    """
    Renderiza la interfaz para la generación de reportes personalizados.

    Args:
        data (pd.DataFrame): Datos a utilizar en el generador de reportes.
    """
    st.sidebar.title("🛠️ Generador de Reportes")
    st.sidebar.write("Selecciona las secciones que deseas incluir en tu reporte.")

    sections = st.sidebar.multiselect(
        "Secciones Disponibles",
        ["Resumen General", "Gráficos de Tendencias", "Análisis por Institución", "Conclusiones"],
        default=["Resumen General", "Gráficos de Tendencias"]
    )

    if st.sidebar.button("Generar Reporte"):
        generate_report(sections, data)
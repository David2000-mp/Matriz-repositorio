"""
Vista para la configuración y generación de reportes personalizados.
"""

import streamlit as st
import pandas as pd
from utils.data_manager import load_data
from utils.report_generator import ReportBuilder

def render_report_view(df_metricas, trend_figures):
    """
    Renderiza la vista de reportes en la aplicación Streamlit.
    """
    st.title("Generador de Reportes")

    # Debugging load_data accessibility
    try:
        cuentas, metricas = load_data()
        st.write("load_data executed successfully.")
    except Exception as e:
        st.error(f"Debug: load_data failed with error: {e}")

    # Verificar si las columnas necesarias existen en cuentas
    required_columns = ["entidad", "id_cuenta"]
    for col in required_columns:
        if col not in cuentas.columns:
            st.error(f"❌ La columna '{col}' no está disponible en los datos de cuentas. Verifica los datos de entrada.")
            return

    # Selección de entidad
    entidad = st.selectbox("Selecciona una entidad:", cuentas["entidad"].unique())

    # Filtrar métricas por entidad seleccionada
    metricas_filtradas = metricas[metricas["id_cuenta"].isin(cuentas[cuentas["entidad"] == entidad]["id_cuenta"])]

    if metricas_filtradas.empty:
        st.warning("⚠️ No hay métricas disponibles para la entidad seleccionada.")
        return

    # Selección de secciones
    st.subheader("Selecciona las secciones del reporte:")
    incluir_resumen = st.checkbox("Resumen Ejecutivo")
    incluir_kpis = st.checkbox("KPIs de Crecimiento")
    incluir_graficas = st.checkbox("Gráficas de Tendencia")

    # Botón para generar el reporte
    if st.button("Generar PDF"):
        with st.spinner("Generando reporte..."):
            try:
                # Crear instancia de ReportBuilder
                report = ReportBuilder(df=metricas_filtradas, entity_name=entidad)

                # Agregar secciones seleccionadas
                sections = []
                if incluir_resumen:
                    sections.append("resumen")
                if incluir_kpis:
                    sections.append("kpis")
                if incluir_graficas:
                    sections.append("graficas")

                # Generar el archivo PDF
                pdf_bytes = report.generate(sections=sections)

                # Botón de descarga
                st.download_button(
                    label="Descargar Reporte",
                    data=pdf_bytes,
                    file_name=f"{entidad}_reporte.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"❌ Error al generar el reporte: {e}")
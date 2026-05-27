"""
Vista de Auditoria de Respuestas.
Encapsula la logica de renderizado para mantener app_refactored.py como router.
"""

import logging
import pandas as pd
import streamlit as st

from utils.sheets_connector import cargar_respuestas_forms


def render_audit_view(df_merged=None):
    """Renderiza la vista de auditoria de respuestas.

    Args:
        df_merged: parametro opcional para compatibilidad futura.
    """
    st.header("🔍 Auditoría de Respuestas")

    try:
        df_forms = cargar_respuestas_forms()

        if df_forms.empty:
            st.warning("No hay datos nuevos del formulario")
            st.stop()

        df_forms = df_forms.reset_index(drop=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            total_registros = len(df_forms)
            st.metric("Total de Registros", total_registros)

        with col2:
            promedio_engagement = (
                df_forms["engagement_rate"].mean()
                if "engagement_rate" in df_forms.columns
                else 0.0
            )
            st.metric("Promedio de Engagement", f"{promedio_engagement:.2f}%")

        with col3:
            ultima_fecha = df_forms["fecha"].max() if "fecha" in df_forms.columns else pd.NaT
            st.metric(
                "Última Fecha de Reporte",
                ultima_fecha.strftime("%Y-%m-%d") if pd.notna(ultima_fecha) else "N/A",
            )

        st.subheader("Datos del Formulario")
        st.data_editor(
            df_forms,
            width="stretch",
            num_rows="dynamic",
            column_config={
                "fecha": st.column_config.DateColumn("Fecha del Reporte"),
                "seguidores": st.column_config.NumberColumn("Seguidores Totales", min_value=0),
                "engagement_rate": st.column_config.NumberColumn(
                    "Engagement Rate (%)", min_value=0.0, max_value=100.0, step=0.01
                ),
                "alcance": st.column_config.NumberColumn("Alcance Total", min_value=0),
                "interacciones": st.column_config.NumberColumn("Interacciones Totales", min_value=0),
            },
        )

        if "error_validacion" not in df_forms.columns:
            df_forms["error_validacion"] = ""

        errores = df_forms[df_forms["error_validacion"] != ""]
        if not errores.empty:
            st.error("Filas con errores de validación:")
            error_cols = [
                col for col in ["entidad", "plataforma", "error_validacion"] if col in errores.columns
            ]
            st.dataframe(errores[error_cols], width="stretch")

    except Exception as e:
        st.error(f"Error cargando datos del formulario: {e}")
        logging.error(f"Error en auditoría de respuestas: {e}")

"""
Vista de Comparativas para CHAMPILYTICS.
Provee dos pestañas: 'Distribución' (pie por plataforma) y 'Rendimiento' (barras por institución).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data
from components import COLOR_MAP


def render(df=None):
    """Renderiza la vista de Comparativas.

    - Si `df` no se provee, se cargan datos con `load_data()`.
    - Normaliza columnas básicas generadas por merges.
    """
    st.title("Comparativas")

    # Cargar si es necesario
    if df is None:
        cuentas, metricas = load_data()
        if cuentas.empty or metricas.empty:
            st.warning("No hay datos disponibles. Ve a 'Configuración' para generar datos de prueba.")
            return
        df = pd.merge(metricas, cuentas, on="id_cuenta", how="left")

    # Normalizar columnas (coalesce)
    for logical in ("entidad", "plataforma", "usuario_red"):
        if logical in df.columns:
            continue
        for suff in (f"{logical}_y", f"{logical}_x"):
            if suff in df.columns:
                df.rename(columns={suff: logical}, inplace=True)
                break

    if df.empty:
        st.info("No hay registros después de la normalización.")
        return

    tab_dist, tab_perf = st.tabs(["Distribución", "Rendimiento"])

    with tab_dist:
        st.subheader("Distribución de Seguidores por Plataforma")
        df_plat = df.groupby("plataforma")["seguidores"].sum().reset_index()
        if df_plat.empty:
            st.info("No hay datos para la distribución.")
        else:
            fig = px.pie(df_plat, names="plataforma", values="seguidores", color="plataforma", color_discrete_map=COLOR_MAP)
            fig.update_traces(textposition="inside", textinfo="percent+label")
            fig.update_layout(margin=dict(t=30, b=10))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    with tab_perf:
        st.subheader("Rendimiento por Institución (Seguidores)")
        df_ent = df.groupby("entidad")["seguidores"].sum().reset_index()
        if df_ent.empty:
            st.info("No hay datos para el ranking de instituciones.")
        else:
            df_ent = df_ent.sort_values("seguidores", ascending=False)
            fig2 = px.bar(df_ent, x="seguidores", y="entidad", orientation="h", text="seguidores")
            fig2.update_layout(margin=dict(t=30, b=10))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    st.markdown("---")
    st.info("Usa los filtros globales en la barra lateral para ajustar institución y periodo.")

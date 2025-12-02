"""
Vista Dashboard Global para CHAMPILYTICS.
Panel principal con métricas agregadas de toda la red.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from utils import (
    load_data,
    simular,
    save_batch,
    reset_db,
    generar_reporte_html,
    COLEGIOS_MARISTAS,
)
from utils.data_manager import load_configs
from components import COLOR_MAP
from utils.analytics import calculate_growth_metrics


def render():
    st.title("Tablero Principal")

    # 0. Leer filtro global de institución
    selected_institution = st.session_state.get(
        "global_institution_filter", "Todas las Instituciones"
    )

    # 1. CARGA DE DATOS
    cuentas, metricas = load_data()

    # Validación de carga básica
    if cuentas.empty or metricas.empty:
        st.info("👋 ¡Bienvenido! Aún no hay datos cargados para analizar.")
        st.markdown("Ve a la pestaña **Carga de Datos** para subir tu primer reporte.")
        st.stop()

    # 2. FUSIÓN DE DATOS (EL PASO QUE FALTABA) 🔗
    # Unimos métricas con cuentas para obtener la columna 'entidad'
    df = pd.merge(metricas, cuentas, on="id_cuenta", how="left")
    # Si existe 'entidad_x', renombrar a 'entidad'
    if "entidad_x" in df.columns:
        df = df.rename(columns={"entidad_x": "entidad"})
    elif "entidad_y" in df.columns:
        df = df.rename(columns={"entidad_y": "entidad"})
    # Si existe 'plataforma_x', renombrar a 'plataforma'
    if "plataforma_x" in df.columns:
        df = df.rename(columns={"plataforma_x": "plataforma"})
    elif "plataforma_y" in df.columns:
        df = df.rename(columns={"plataforma_y": "plataforma"})

    # 2.5 Filtrado por institución si aplica
    if selected_institution != "Todas las Instituciones":
        df = df[df["entidad"] == selected_institution]
        cuentas = cuentas[cuentas["entidad"] == selected_institution]
        st.info(f"🔒 Vista filtrada para: {selected_institution}")
        if df.empty:
            st.warning(
                f"No hay datos para la institución seleccionada: {selected_institution}"
            )
            st.stop()

    # 3. VALIDACIÓN DE INTEGRIDAD (Ahora sí pasará) ✅
    required_cols = ["fecha", "entidad", "engagement_rate"]
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        st.error(
            f"⚠️ Error de Datos: Faltan columnas críticas en el archivo fusionado: {missing}"
        )
        st.write("Columnas disponibles:", df.columns.tolist())
        st.stop()

    # --- CONSTRUCTOR DE VISTAS ---
    st.markdown("### Constructor de Vistas: Elige tus gráficas favoritas")
    opciones_graficas = {
        "Torta de Seguidores": "torta",
        "Línea de Crecimiento": "linea",
        "Barras de Interacciones": "barras",
        "Área de Engagement": "area",
        "Comparativa Histórica": "historico",
    }
    seleccionadas = st.multiselect(
        "Selecciona hasta 3 gráficas para mostrar:",
        list(opciones_graficas.keys()),
        default=["Torta de Seguidores"],
        max_selections=3,
    )

    # KPIs rápidos
    st.markdown("### Resumen Ejecutivo")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Seguidores", f"{df['seguidores'].sum():,.0f}")
    col2.metric("Total Interacciones", f"{df['interacciones'].sum():,.0f}")

    # Renderizar gráficas seleccionadas
    for graf in seleccionadas:
        tipo = opciones_graficas[graf]
        if tipo == "torta":
            fig = px.pie(
                df,
                values="seguidores",
                names="entidad",
                title="Distribución de Seguidores por Colegio",
            )
            st.plotly_chart(fig, use_container_width=True)
        elif tipo == "linea":
            if "fecha" in df.columns:
                df_mes = df.copy()
                df_mes["Mes"] = (
                    pd.to_datetime(df_mes["fecha"]).dt.to_period("M").astype(str)
                )
                resumen = (
                    df_mes.groupby("Mes")
                    .agg({"seguidores": "sum", "interacciones": "sum"})
                    .reset_index()
                )
                fig = px.line(
                    resumen,
                    x="Mes",
                    y=["seguidores", "interacciones"],
                    markers=True,
                    title="Crecimiento Mensual",
                )
                st.plotly_chart(fig, use_container_width=True)
        elif tipo == "barras":
            if "entidad" in df.columns and "interacciones" in df.columns:
                resumen = (
                    df.groupby("entidad").agg({"interacciones": "sum"}).reset_index()
                )
                fig = px.bar(
                    resumen,
                    x="entidad",
                    y="interacciones",
                    title="Interacciones por Colegio",
                )
                st.plotly_chart(fig, use_container_width=True)
        elif tipo == "area":
            if "fecha" in df.columns and "engagement_rate" in df.columns:
                df_mes = df.copy()
                df_mes["Mes"] = (
                    pd.to_datetime(df_mes["fecha"]).dt.to_period("M").astype(str)
                )
                resumen = (
                    df_mes.groupby("Mes").agg({"engagement_rate": "mean"}).reset_index()
                )
                fig = px.area(
                    resumen,
                    x="Mes",
                    y="engagement_rate",
                    title="Engagement Rate Mensual",
                )
                st.plotly_chart(fig, use_container_width=True)
        elif tipo == "historico":
            if "fecha" in df.columns and "seguidores" in df.columns:
                df_hist = df.copy()
                df_hist["Mes"] = (
                    pd.to_datetime(df_hist["fecha"]).dt.to_period("M").astype(str)
                )
                fig = px.box(
                    df_hist,
                    x="Mes",
                    y="seguidores",
                    title="Distribución Histórica de Seguidores",
                )
                st.plotly_chart(fig, use_container_width=True)

    # --- Tablas de datos retractiles al final ---
    with st.expander("🔍 Ver datos de cuentas"):
        st.dataframe(cuentas, use_container_width=True)

    with st.expander("🔍 Ver datos de métricas"):
        st.dataframe(metricas, use_container_width=True)

    # --- Tabla de resumen mensual retractil ---
    if "fecha" in df.columns:
        df_mes = df.copy()
        df_mes["Mes"] = pd.to_datetime(df_mes["fecha"]).dt.to_period("M").astype(str)
        resumen_mensual = (
            df_mes.groupby("Mes")
            .agg(
                {"seguidores": "sum", "interacciones": "sum", "engagement_rate": "mean"}
            )
            .reset_index()
        )

        with st.expander("📊 Resumen Mensual de Datos"):
            st.dataframe(resumen_mensual, use_container_width=True)

    # --- Tabla de datos detallados retractil ---
    with st.expander("📋 Datos Detallados"):
        st.dataframe(df, use_container_width=True)

"""
Vista Dashboard Global para CHAMPILYTICS.
Panel principal con métricas agregadas de toda la red.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from utils import load_data, simular, save_batch, reset_db, generar_reporte_html, COLEGIOS_MARISTAS
from utils.data_manager import load_configs
from components import COLOR_MAP
from utils.analytics import calculate_growth_metrics


def render():
    st.title("Tablero Principal")

    # 0. Leer filtro global de institución
    selected_institution = st.session_state.get("global_institution_filter", "Todas las Instituciones")

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
    if 'entidad_x' in df.columns:
        df = df.rename(columns={'entidad_x': 'entidad'})
    elif 'entidad_y' in df.columns:
        df = df.rename(columns={'entidad_y': 'entidad'})
    # Si existe 'plataforma_x', renombrar a 'plataforma'
    if 'plataforma_x' in df.columns:
        df = df.rename(columns={'plataforma_x': 'plataforma'})
    elif 'plataforma_y' in df.columns:
        df = df.rename(columns={'plataforma_y': 'plataforma'})

    # 2.5 Filtrado por institución si aplica
    if selected_institution != "Todas las Instituciones":
        df = df[df["entidad"] == selected_institution]
        cuentas = cuentas[cuentas["entidad"] == selected_institution]
        st.info(f"🔒 Vista filtrada para: {selected_institution}")
        if df.empty:
            st.warning(f"No hay datos para la institución seleccionada: {selected_institution}")
            st.stop()

    # 3. VALIDACIÓN DE INTEGRIDAD (Ahora sí pasará) ✅
    required_cols = ['fecha', 'entidad', 'engagement_rate']
    missing = [c for c in required_cols if c not in df.columns]
    
    if missing:
        st.error(f"⚠️ Error de Datos: Faltan columnas críticas en el archivo fusionado: {missing}")
        st.write("Columnas disponibles:", df.columns.tolist())
        st.stop()

    # --- A PARTIR DE AQUÍ TU CÓDIGO DE VISUALIZACIÓN ---
    
    # Ejemplo de KPIs rápidos
    st.markdown("### Resumen Ejecutivo")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Seguidores", f"{df['seguidores'].sum():,.0f}")
    col2.metric("Total Interacciones", f"{df['interacciones'].sum():,.0f}")
    
    # Gráfico de Torta de ejemplo (Distribución por Entidad)
    fig = px.pie(df, values='seguidores', names='entidad', title='Distribución de Seguidores por Colegio')
    st.plotly_chart(fig, use_container_width=True)
    
    # (Aquí puedes llamar a tus otras gráficas)
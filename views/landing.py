"""
Vista de Landing Page para CHAMPILYTICS.
Página de inicio con hero banner y navegación rápida.
"""

import streamlit as st
import pandas as pd
import logging
from utils import load_data, simular, save_batch, reset_db
from utils.helpers import get_banner_css


def render():
    """
    Renderiza la página de inicio con banner hero y navegación rápida.
    """

    # Hero Banner Minimalista Full-Screen
    banner_css = get_banner_css(
        "banner_landing.jpg"  # Buscará en images/
    )

    # Si no hay banner local, usar gradiente
    if not banner_css:
        banner_css = "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"

    # Calcular total de seguidores actuales
    cuentas, metricas = load_data()
    total_seguidores = 0

    # Verificar si hay datos válidos
    datos_validos = False
    if not metricas.empty and not cuentas.empty:
        try:
            df = pd.merge(metricas, cuentas, on="id_cuenta", how="left")
            if "entidad" in df.columns and not df["entidad"].isna().all():
                # Obtener la fecha más reciente
                ultima_fecha = df["fecha"].max()
                df_actual = df[df["fecha"] == ultima_fecha]
                total_seguidores = int(df_actual["seguidores"].sum())
                datos_validos = True
                logging.info(f"Landing - Seguidores totales: {total_seguidores:,}")
        except Exception as e:
            logging.warning(f"Error calculando seguidores en landing: {e}")

    # Renderizar hero banner
    st.markdown(
        f'''
        <div class="hero-banner" style="{banner_css}">
            <div class="hero-content" style="max-width: 900px;">
                <h1 style="font-size: 7rem; margin-bottom: 30px; letter-spacing: 10px; text-shadow: 2px 2px 20px rgba(0,0,0,0.4); font-weight: 900;">
                    CHAMPILYTICS
                </h1>
                <p style="font-size: 1.2rem; margin-bottom: 20px; opacity: 0.9; text-shadow: 1px 1px 10px rgba(0,0,0,0.3); letter-spacing: 4px; font-weight: 300;">
                    INTELIGENCIA DIGITAL MARISTA
                </p>
                <div class="followers-counter">
                    {total_seguidores:,}
                </div>
                <div class="followers-label" style="margin-bottom: 60px;">
                    Seguidores Totales Red Marista
                </div>
            </div>
        </div>
    ''',
        unsafe_allow_html=True,
    )

    # Sección de navegación rápida
    st.markdown(
        "<div style='margin-top: -80px; position: relative; z-index: 10; max-width: 900px; margin-left: auto; margin-right: auto;'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="background: rgba(255,255,255,0.98); backdrop-filter: blur(10px); border-radius: 0; padding: 50px 60px; box-shadow: 0 4px 30px rgba(0,0,0,0.1);">
            <h2 style="text-align: center; margin-bottom: 40px; color: #003696; font-size: 1.1rem; font-weight: 400; letter-spacing: 3px; text-transform: uppercase;">Navegar</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top: -30px;'>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Dashboard", key="btn_dash", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    with col2:
        if st.button("Captura", key="btn_cap", use_container_width=True):
            st.session_state.page = "captura"
            st.rerun()

    with col3:
        if st.button("Análisis", key="btn_ana", use_container_width=True):
            st.session_state.page = "analisis"
            st.rerun()

    with col4:
        if st.button("Configuración", key="btn_cfg", use_container_width=True):
            st.session_state.page = "config"
            st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Verificar estado de los datos y mostrar alerta si hay problemas
    if not datos_validos:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.warning("⚠️ **Configuración Inicial Requerida**", icon="⚠️")
        st.info(
            "Parece que es la primera vez que usas CHAMPILYTICS o los datos necesitan ser regenerados."
        )

        st.markdown("### 🚀 Inicio Rápido")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Opción 1: Empezar desde Cero**")
            if st.button(
                "🗑️ Resetear + Generar Datos Demo",
                use_container_width=True,
                type="primary",
            ):
                progress = st.progress(0)
                status = st.empty()

                status.text("🧹 Limpiando base de datos...")
                progress.progress(33)
                reset_db()

                status.text("🎲 Generando 6 meses de datos...")
                progress.progress(66)
                from utils.data_manager import COLEGIOS_MARISTAS

                save_batch(simular(n=100, colegios_maristas=COLEGIOS_MARISTAS))

                progress.progress(100)
                status.text("✅ ¡Completado!")
                st.success("Sistema inicializado correctamente")
                st.rerun()

        with col2:
            st.markdown("**Opción 2: Solo Limpiar**")
            if st.button("🧹 Solo Resetear BD", use_container_width=True):
                with st.spinner("Limpiando..."):
                    reset_db()
                st.success("Base de datos limpiada")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

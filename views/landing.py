"""
Vista de Landing Page para CHAMPILYTICS.
Página de inicio con hero banner y navegación rápida.
"""

import streamlit as st
import pandas as pd
import logging
from utils import load_data, simular, save_batch, reset_db
from utils.helpers import get_banner_css


def render(df=None):
    """
    Renderiza la página de inicio con banner hero y navegación rápida.

    Acepta un parámetro `df` por compatibilidad con el enrutador.
    """

    # Hero Banner Minimalista Full-Screen
    banner_css = get_banner_css("banner_landing.jpg")

    # Si no hay banner local, usar gradiente suave institucional
    if not banner_css:
        banner_css = "background: linear-gradient(135deg, #eaf2ff 0%, #d9e7ff 100%);"

    # Calcular total de seguidores actuales
    cuentas, metricas = load_data()
    total_seguidores = 0

    # Verificar si hay datos válidos
    datos_validos = False
    if not metricas.empty and not cuentas.empty:
        try:
            df = pd.merge(metricas, cuentas, on="id_cuenta", how="left")
            # Normalizar columnas para evitar KeyError (entidad/plataforma/usuario_red)
            for logical in ("entidad", "plataforma", "usuario_red"):
                if logical in df.columns:
                    continue
                for suff in (f"{logical}_y", f"{logical}_x", f"{logical}"):
                    if suff in df.columns:
                        ser = df.loc[:, suff]
                        if isinstance(ser, pd.DataFrame):
                            ser = ser.squeeze()  # Convertir DataFrame de una columna a Series
                        df[logical] = ser
                        break
                else:
                    df[logical] = "Unknown"

            if "entidad" in df.columns and not df["entidad"].isna().all():
                # Obtener la fecha más reciente
                if "fecha" in df.columns:
                    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
                    ultima_fecha = df["fecha"].max()
                    df_actual = df[df["fecha"] == ultima_fecha]
                    total_seguidores = int(df_actual["seguidores"].sum())
                    datos_validos = True
                    logging.info(f"Landing - Seguidores totales: {total_seguidores:,}")
        except Exception as e:
            logging.warning(f"Error calculando seguidores en landing: {e}")

    # Renderizar hero banner (estilo minimalista, color institucional)
    st.markdown(
        f'''
        <div class="hero-banner" style="{banner_css}">
            <div class="hero-content" style="max-width: 900px;">
                <h1 style="font-size: 4rem; margin-bottom: 8px; letter-spacing: 4px; color: #003696; font-weight: 700; text-shadow: none;">
                    CHAMPILYTICS
                </h1>
                <p style="font-size: 1rem; margin-bottom: 18px; color: #003696; opacity: 0.9; letter-spacing: 2px; font-weight: 400;">
                    INTELIGENCIA DIGITAL MARISTA
                </p>
                <div class="followers-counter" style="font-size:2rem; margin-bottom:6px; color:#042a5a; font-weight:700;">
                    {f'{total_seguidores:,}' if total_seguidores > 0 else ''}
                </div>
                <div class="followers-label" style="margin-bottom: 40px; color:#042a5a;">
                    {('Seguidores Totales Red Marista' if total_seguidores > 0 else 'Bienvenido a tu Inteligencia Digital')}
                </div>
            </div>
        </div>
    ''',
        unsafe_allow_html=True,
    )

    # Accesos rápidos: filas limpias de 4 columnas con iconos
    st.markdown("<div style='max-width:900px; margin-left:auto; margin-right:auto; margin-top:-30px;'>", unsafe_allow_html=True)
    cols = st.columns(4)
    labels_and_pages = [
        ("📊 Dashboard", "Dashboard Global"),
        ("📝 Captura", "Captura"),
        ("📈 Comparativas", "Comparativas"),
        ("⚙️ Configuración", "Configuración"),
    ]

    for col, (label, page) in zip(cols, labels_and_pages):
        with col:
            if st.button(label, key=f"btn_{page}"):
                st.session_state["page_selection"] = page
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Verificar estado de los datos y mostrar alerta si hay problemas
    if not datos_validos:
        st.warning("⚠️ Configuración Inicial Requerida", icon="⚠️")
        st.info("Parece que es la primera vez que usas CHAMPILYTICS o los datos necesitan ser regenerados.")

        st.markdown("### 🚀 Inicio Rápido")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Opción 1: Empezar desde Cero**")
            if st.button("🗑️ Resetear + Generar Datos Demo"):
                progress = st.progress(0)
                status = st.empty()

                status.text("🧹 Limpiando base de datos...")
                progress.progress(33)
                reset_db()

                status.text("🎲 Generando 6 meses de datos...")
                progress.progress(66)
                from utils.data_manager import COLEGIOS_MARISTAS

                resultados = simular(n=100, colegios_maristas=COLEGIOS_MARISTAS)
                # simular() puede devolver (datos, metas). Aceptar ambas formas.
                try:
                    if isinstance(resultados, (list, tuple)) and len(resultados) >= 1:
                        datos_sim = resultados[0]
                        metas_sim = resultados[1] if len(resultados) > 1 else []
                    else:
                        datos_sim = resultados
                        metas_sim = []
                except Exception:
                    datos_sim = resultados
                    metas_sim = []

                save_batch(datos_sim)  # type: ignore

                progress.progress(100)
                status.text("✅ ¡Completado!")
                st.success("Sistema inicializado correctamente")
                st.rerun()

        with col2:
            st.markdown("**Opción 2: Solo Limpiar**")
            if st.button("🧹 Solo Resetear BD"):
                with st.spinner("Limpiando..."):
                    reset_db()
                st.success("Base de datos limpiada")
                st.rerun()

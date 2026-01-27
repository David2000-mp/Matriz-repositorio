"""
Vista de Landing Page para CHAMPILEAKS.
Página de inicio con hero banner y navegación rápida.
"""

import streamlit as st
import pandas as pd
import logging
from utils.data_provider import data_provider
from utils import simular, save_batch
from utils.helpers import get_banner_css
from utils.analytics import summarize_followers_growth


def render(df=None):
    """
    Renderiza la página de inicio con banner hero y navegación rápida.

    Acepta un parámetro `df` por compatibilidad con el enrutador.
    """

    # Hero Banner Minimalista Full-Screen
    banner_css = get_banner_css("banner_landing.jpg", height="100vh")

    # Si no hay banner local, usar gradiente suave institucional
    if not banner_css:
        banner_css = "background: linear-gradient(135deg, #eaf2ff 0%, #d9e7ff 100%); height: 100vh;"

    # Calcular total de seguidores actuales y delta vs mes anterior
    cuentas, metricas = data_provider.get_data()
    total_seguidores = 0
    delta_pct = 0.0
    breakdown_text = ""

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
                if "fecha" in df.columns:
                    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
                    resumen = summarize_followers_growth(df)
                    total_seguidores = resumen["total"]
                    delta_pct = resumen["delta_pct"]
                    snapshot = resumen["snapshot"]

                    # Calcular desglose por plataforma con el snapshot consolidado
                    platform_breakdown = snapshot.groupby("plataforma")["seguidores"].sum()
                    breakdown_parts = []
                    for platform, followers in platform_breakdown.items():
                        breakdown_parts.append(f"{platform}: {int(followers):,}")
                    breakdown_text = " | ".join(breakdown_parts)

                    datos_validos = total_seguidores > 0
                    logging.info(f"Landing - Seguidores totales: {total_seguidores:,}, Delta: {delta_pct:.1f}%")
        except Exception as e:
            logging.warning(f"Error calculando seguidores en landing: {e}")

    # Renderizar hero banner usando componentes nativos de Streamlit
    # Aplicar CSS con st.markdown pero usar st.container para estructura
    
    # Inyectar CSS personalizado
    st.markdown(f"""
        <style>
        .hero-container {{
            {banner_css}
            padding: 60px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .hero-title {{
            font-size: 4rem;
            letter-spacing: 4px;
            color: white;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .hero-subtitle {{
            font-size: 1rem;
            color: white;
            opacity: 0.9;
            letter-spacing: 2px;
            margin-bottom: 30px;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    if datos_validos and total_seguidores > 0:
        # Banner con datos usando componentes nativos
        with st.container():
            st.markdown('<div class="hero-container">', unsafe_allow_html=True)
            st.markdown('<h1 class="hero-title">CHAMPILEAKS</h1>', unsafe_allow_html=True)
            st.markdown('<p class="hero-subtitle">INTELIGENCIA DIGITAL MARISTA</p>', unsafe_allow_html=True)
            
            # Métricas usando st.metric (componente nativo)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                delta_val = f"{delta_pct:+.1f}%" if delta_pct != 0 else None
                st.metric(
                    label="Seguidores Totales Red Marista",
                    value=f"{total_seguidores:,}",
                    delta=delta_val if delta_val else None,
                    help=breakdown_text if breakdown_text else None
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Banner simple sin datos
        with st.container():
            st.markdown('<div class="hero-container">', unsafe_allow_html=True)
            st.markdown('<h1 class="hero-title">CHAMPILEAKS</h1>', unsafe_allow_html=True)
            st.markdown('<p class="hero-subtitle">INTELIGENCIA DIGITAL MARISTA</p>', unsafe_allow_html=True)
            st.info("Bienvenido a tu Inteligencia Digital")
            st.markdown('</div>', unsafe_allow_html=True)

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

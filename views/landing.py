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

    # Hero Banner Institucional con altura responsiva y overlay optimizado
    banner_css = get_banner_css("banner_landing.jpg")

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
    
    # Colores institucionales Marista (desde config.toml)
    PRIMARY_BLUE = "#003696"         # Azul institucional
    PRIMARY_BLUE_DARK = "#00235A"    # Azul oscuro para texto sobre amarillo (WCAG AA)
    ACCENT_YELLOW = "#FFB81C"        # Amarillo acento
    TEXT_ON_DARK = "#FFFFFF"         # Texto sobre fondos oscuros/imágenes
    TEXT_ON_LIGHT = "#212529"        # Texto sobre fondos claros (métricas)
    DELTA_POSITIVE = "#0A7D35"       # Verde accesible para deltas positivos
    DELTA_NEGATIVE = "#B42318"       # Rojo accesible para deltas negativos
    
    # Detectar tema para adaptar fondos (no afecta colores institucionales)
    try:
        theme = st.get_option("theme.base") or "light"
        is_dark = theme == "dark"
    except:
        is_dark = False
    
    # Fondos adaptativos institucionales (sin glassmorphism genérico)
    card_bg = f"rgba(0, 54, 150, 0.85)" if is_dark else f"rgba(0, 54, 150, 0.9)"  # Azul sólido
    card_hover_bg = f"rgba(255, 184, 28, 0.95)"  # Amarillo al hover
    metrics_bg = "rgba(255, 255, 255, 0.95)" if is_dark else "rgba(255, 255, 255, 0.98)"  # Fondo claro sólido
    
    # Inyectar CSS institucional profesional (sin glassmorphism genérico)
    st.markdown(f"""
        <style>
        /* ====================================
           CHAMPILEAKS - SISTEMA INSTITUCIONAL
           Diseño: Profesional corporativo Marista
           Colores: {PRIMARY_BLUE} (azul) + {ACCENT_YELLOW} (amarillo)
           ==================================== */
        
        /* === TIPOGRAFÍA CORPORATIVA === */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Tipografía SOLO para contenido, NO para widgets internos de Streamlit */
        body, .stMarkdown, h1, h2, h3, h4, h5, h6, p, span {{
            font-family: 'Inter', 'Segoe UI', -apple-system, sans-serif;
        }}
        
        /* Legibilidad mínima obligatoria para accesibilidad */
        .stTextInput input, .stSelectbox select, .stNumberInput input,
        .stTextArea textarea, label, .stMarkdown {{
            font-size: 16px !important;
            line-height: 1.6 !important;
        }}
        
        /* Fix para selectboxes: fondo blanco y texto oscuro */
        .stSelectbox > div > div {{
            background-color: white !important;
            color: #212529 !important;
        }}
        
        .stSelectbox select, .stSelectbox input {{
            background-color: white !important;
            color: #212529 !important;
            border: 1px solid #CED4DA !important;
        }}
        
        /* Dropdown menu del selectbox */
        div[role="listbox"] {{
            background-color: white !important;
        }}
        
        div[role="option"] {{
            background-color: white !important;
            color: #212529 !important;
        }}
        
        div[role="option"]:hover {{
            background-color: #F8F9FA !important;
            color: {PRIMARY_BLUE} !important;
        }}
        
        /* === HERO BANNER INSTITUCIONAL === */
        .hero-container {{
            {banner_css}
            padding: 80px 20px 60px 20px;
            text-align: center;
            margin-bottom: 0;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            /* Mejoras para nitidez de imagen */
            image-rendering: -webkit-optimize-contrast;
            image-rendering: crisp-edges;
            backface-visibility: hidden;
            -webkit-backface-visibility: hidden;
        }}
        
        .hero-title {{
            font-family: 'Inter', sans-serif;
            font-size: clamp(2.8rem, 10vw, 5rem);
            letter-spacing: 8px;
            color: {PRIMARY_BLUE};
            font-weight: 700;
            margin-bottom: 16px;
            text-shadow: 2px 3px 8px rgba(255, 255, 255, 0.8),
                         0px 0px 15px rgba(255, 255, 255, 0.6);
            text-transform: uppercase;
            animation: fadeInDown 0.9s ease-out;
        }}
        
        .hero-subtitle {{
            font-family: 'Inter', sans-serif;
            font-size: clamp(0.95rem, 2.5vw, 1.2rem);
            color: {TEXT_ON_LIGHT};
            opacity: 1;
            letter-spacing: 4px;
            margin-bottom: 40px;
            font-weight: 400;
            text-shadow: 1px 2px 6px rgba(255, 255, 255, 0.5);
            text-transform: uppercase;
            animation: fadeInUp 1.1s ease-out;
        }}
        
        /* === CONTENEDOR DE MÉTRICAS INSTITUCIONAL === */
        .metrics-institutional-container {{
            background: {metrics_bg};
            border-radius: 16px;
            padding: 35px 25px;
            border: 3px solid {PRIMARY_BLUE};
            box-shadow: 
                0 10px 40px rgba(0, 54, 150, 0.25),
                inset 0 1px 0 rgba(255, 255, 255, 0.9);
            margin: 25px auto;
            max-width: 650px;
            position: relative;
        }}
        
        .metrics-institutional-container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, {PRIMARY_BLUE} 0%, {ACCENT_YELLOW} 100%);
            border-radius: 16px 16px 0 0;
        }}
        
        /* Métricas con colores institucionales */
        div[data-testid="stMetricValue"] {{
            font-size: 2.8rem !important;
            font-weight: 700 !important;
            color: {PRIMARY_BLUE} !important;
            text-shadow: none;
        }}
        
        div[data-testid="stMetricLabel"] {{
            font-size: 1.05rem !important;
            color: {TEXT_ON_LIGHT} !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        
        div[data-testid="stMetricDelta"] {{
            font-size: 1.15rem !important;
            font-weight: 600 !important;
            color: {DELTA_POSITIVE} !important;
        }}
        
        /* Delta negativo en rojo accesible */
        div[data-testid="stMetricDelta"][aria-label*="-"] {{
            color: {DELTA_NEGATIVE} !important;
        }}
        
        /* === CARDS DE NAVEGACIÓN INSTITUCIONALES === */
        .stButton > button {{
            width: 100% !important;
            background: {card_bg} !important;
            border-radius: 10px !important;
            border: 2px solid transparent !important;
            padding: 22px 18px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            color: {TEXT_ON_DARK} !important;
            transition: all 0.25s ease !important;
            box-shadow: 0 6px 20px rgba(0, 54, 150, 0.3) !important;
            letter-spacing: 0.8px;
            text-transform: uppercase;
        }}
        
        /* Forzar texto blanco en todos los niveles del botón */
        .stButton > button *,
        .stButton > button p,
        .stButton > button span,
        .stButton > button div,
        .stButton > button div[data-testid="stMarkdownContainer"],
        .stButton > button div[data-testid="stMarkdownContainer"] p {{
            color: {TEXT_ON_DARK} !important;
        }}
        
        .stButton > button:hover {{
            background: {card_hover_bg} !important;
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 10px 30px rgba(255, 184, 28, 0.4) !important;
            border: 2px solid {ACCENT_YELLOW} !important;
            color: {PRIMARY_BLUE_DARK} !important;
        }}
        
        /* Texto oscuro legible en estado hover */
        .stButton > button:hover *,
        .stButton > button:hover p,
        .stButton > button:hover span,
        .stButton > button:hover div,
        .stButton > button:hover div[data-testid="stMarkdownContainer"],
        .stButton > button:hover div[data-testid="stMarkdownContainer"] p {{
            color: {PRIMARY_BLUE_DARK} !important;
        }}
        
        .stButton > button:active {{
            transform: translateY(-1px) scale(1.01) !important;
        }}
        
        .stButton > button:focus {{
            outline: 3px solid {ACCENT_YELLOW};
            outline-offset: 2px;
        }}
        
        /* === ANIMACIONES SUAVES === */
        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-40px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(40px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        /* === RESPONSIVIDAD MOBILE-FIRST === */
        @media (max-width: 768px) {{
            .hero-container {{
                padding: 60px 15px 50px 15px;
            }}
            
            .hero-title {{
                font-size: 2.2rem !important;
                letter-spacing: 4px;
            }}
            
            .hero-subtitle {{
                font-size: 0.85rem !important;
                letter-spacing: 2px;
            }}
            
            .metrics-institutional-container {{
                padding: 25px 15px;
                max-width: 100%;
            }}
            
            .stButton > button {{
                padding: 18px 14px !important;
                font-size: 16px !important;
                letter-spacing: 0.5px;
            }}
        }}
        
        /* Accesibilidad: motion reducido */
        @media (prefers-reduced-motion: reduce) {{
            * {{
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }}
        }}
        </style>
    """, unsafe_allow_html=True)
    
    if datos_validos and total_seguidores > 0:
        # Banner con datos usando componentes nativos
        with st.container():
            st.markdown('<div class="hero-container">', unsafe_allow_html=True)
            st.markdown('<h1 class="hero-title">CHAMPILEAKS</h1>', unsafe_allow_html=True)
            st.markdown('<p class="hero-subtitle">INTELIGENCIA DIGITAL MARISTA</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)  # Cerrar hero-container
            
            # Métricas fuera del hero (sin contenedor visual)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                delta_val = f"{delta_pct:+.1f}%" if delta_pct != 0 else None
                st.metric(
                    label="Seguidores Totales Red Marista",
                    value=f"{total_seguidores:,}",
                    delta=delta_val if delta_val else None,
                    help=breakdown_text if breakdown_text else None
                )
    else:
        # Banner simple sin datos
        with st.container():
            st.markdown('<div class="hero-container">', unsafe_allow_html=True)
            st.markdown('<h1 class="hero-title">CHAMPILEAKS</h1>', unsafe_allow_html=True)
            st.markdown('<p class="hero-subtitle">INTELIGENCIA DIGITAL MARISTA</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Mensaje de bienvenida fuera del hero
            st.info("🚀 Bienvenido a tu Inteligencia Digital - Carga datos para comenzar", icon="ℹ️")

    # Accesos rápidos institucionales: cuadrícula de navegación
    st.markdown("<div style='max-width:950px; margin:40px auto 0; padding:0 20px;'>", unsafe_allow_html=True)
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

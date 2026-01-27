"""
Módulo de estilos CSS para CHAMPILEAKS.
Define constantes de colores y función de inyección de CSS personalizado.
"""

import streamlit as st

# ===========================
# CONSTANTES DE COLOR
# ===========================

# Colores Institucionales Maristas
COLOR_PRIMARY = "#003696"  # Azul Marista
COLOR_SECONDARY = "#002566"  # Azul oscuro para hover
COLOR_BG = "#F4F6F9"  # Gris muy suave para fondo
COLOR_CARD = "#FFFFFF"  # Blanco puro para tarjetas
COLOR_TEXT = "#212529"  # Gris muy oscuro para texto (casi negro)
COLOR_CAPTION = "#6B7280"  # Gris medio para captions

# Colores por plataforma (para gráficos)
COLOR_MAP = {
    "Facebook": "#1877F2",
    "Instagram": "#E1306C",
    "TikTok": "#000000",
    "Twitter/X": "#1DA1F2",
    "LinkedIn": "#0A66C2",
    "YouTube": "#FF0000",
}

# ===========================
# FUNCIÓN DE INYECCIÓN CSS
# ===========================


def inject_custom_css():
    """Inyecta el CSS previo simple (pre-mejoras)."""
    new_css = r"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
        :root {
            --primary-color: #003696;
            --primary-hover: #002566;
            --accent-color: #FFB81C;
            --bg-color: #F4F6F9;
            --card-bg: #FFFFFF;
            --sidebar-bg: #003696;
            --sidebar-text: #ffffff;
            --button-primary: #003696;
            --button-secondary: #FFF4E0;
        }
        .stApp { font-family: 'Montserrat', sans-serif !important; background-color: var(--bg-color); }
        [data-testid="stSidebar"] { background-color: var(--sidebar-bg) !important; }
        [data-testid="stSidebar"] * { color: var(--sidebar-text) !important; }

        /* Card layout for KPIs */
        .kpi-cards { display:flex; gap:16px; flex-wrap:wrap; margin-bottom:12px; }
        .kpi-card { background:var(--card-bg) !important; border-radius:12px; padding:14px; flex:1 1 220px; box-shadow:0 4px 6px rgba(0,0,0,0.05); border:1px solid rgba(0,0,0,0.04); border-left:4px solid var(--accent-color); }
        .kpi-card .kpi-title { color:var(--primary-color); font-weight:700; font-size:0.95rem; }
        .kpi-card .kpi-value { color:var(--primary-color); font-weight:800; font-size:1.8rem; }
        .kpi-card .kpi-delta { color:var(--accent-color); font-weight:700; }
        .kpi-card .kpi-subtitle { color:#666666; font-size:0.85rem; margin-top:6px; }

        /* Botones - múltiples selectores para compatibilidad */
        .stButton button,
        button[data-testid*="baseButton"],
        [data-testid="stBaseButton-primary"],
        button[kind="primary"] {
            background-color: var(--button-primary) !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.5rem 1.2rem !important;
            font-weight: 600 !important;
            text-transform: none !important;
            box-shadow: 0 2px 5px rgba(0, 57, 102, 0.12) !important;
            transition: all 0.18s ease !important;
        }

        .stButton button:hover,
        button[data-testid*="baseButton"]:hover,
        [data-testid="stBaseButton-primary"]:hover,
        button[kind="primary"]:hover {
            background-color: var(--primary-hover) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 14px rgba(0, 57, 102, 0.18) !important;
        }
        button[kind="secondary"],
        [data-testid="stBaseButton-secondary"] {
            background-color: var(--button-secondary) !important;
            border: 1px solid var(--primary-color) !important;
            color: var(--primary-color) !important;
            border-radius: 8px !important;
            padding: 0.5rem 1.2rem !important;
            font-weight: 600 !important;
            text-transform: none !important;
            box-shadow: 0 2px 5px rgba(0, 57, 102, 0.12) !important;
            transition: all 0.18s ease !important;
        }

        /* Contenido dentro de botones */
        .stButton [data-testid="stMarkdownContainer"],
        .stButton [data-testid="stMarkdownContainer"] p,
        button[data-testid*="baseButton"] [data-testid="stMarkdownContainer"],
        button[data-testid*="baseButton"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stBaseButton-primary"] [data-testid="stMarkdownContainer"],
        [data-testid="stBaseButton-primary"] [data-testid="stMarkdownContainer"] p,
        button[kind="primary"] [data-testid="stMarkdownContainer"],
        button[kind="primary"] [data-testid="stMarkdownContainer"] p {
            color: white !important;
            margin: 0 !important;
            font-weight: 600 !important;
        }

        button[kind="secondary"] [data-testid="stMarkdownContainer"],
        button[kind="secondary"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"],
        [data-testid="stBaseButton-secondary"] [data-testid="stMarkdownContainer"] p {
            color: var(--primary-color) !important;
            margin: 0 !important;
            font-weight: 600 !important;
        }

        [data-testid="stMetric"] { background-color:var(--card-bg); padding:12px; border-radius:10px; border:1px solid rgba(0,0,0,0.05); box-shadow:0 2px 6px rgba(0,0,0,0.04); text-align:center; }
        [data-testid="stMetricValue"] { font-size:1.8rem !important; color:var(--primary-color) !important; font-weight:700; }

        /* Logo en Sidebar: más grande, centrado, con padding */
        .logo-marista {
            width: 180px !important;
            height: auto !important;
            display: block !important;
            margin: 20px auto 10px auto !important;
            border-radius: 8px !important;
        }

        /* Banner en Landing: overlay para texto legible */
        .hero-banner {
            position: relative;
            height: 500px !important;  /* Hacer la imagen más grande */
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .hero-banner::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.4);
            z-index: 1;
        }
        .hero-banner .hero-content {
            position: relative;
            z-index: 2;
            color: white !important;
        }
        .hero-banner .hero-content * {
            color: white !important;
        }
        .hero-banner .hero-content svg {
            stroke: white !important;
            fill: white !important;
        }
        
            /* Textareas: asegurar fondo blanco y buen contraste */
            textarea, .stTextArea textarea, .stTextarea textarea, textarea[role="textbox"] {
                background-color: var(--card-bg) !important;
                color: var(--primary-color) !important;
                border: 1px solid rgba(0,0,0,0.08) !important;
                border-radius: 8px !important;
                padding: 8px !important;
            }

            /* Excluir header y toolbar de los estilos globales */
            [data-testid="stHeader"],
            [data-testid="stToolbar"],
            [data-testid="stToolbarActions"],
            .stMainMenu,
            [class*="stAppHeader"],
            [class*="stToolbar"] {
                background-color: transparent !important;
            }
            
            /* Preservar colores de banner, badges y botones */
            .banner * { color: white !important; }
            .badge { color: white !important; }

        /* Responsive table with hover */
        .responsive-table { width:100%; overflow-x:auto; border-radius:8px; }
        .responsive-table table { width:100%; border-collapse:collapse; min-width:600px; }
        .responsive-table th, .responsive-table td { padding:10px 12px; text-align:left; border-bottom:1px solid rgba(0,0,0,0.06); }
        .responsive-table tr:hover { background-color: rgba(0,40,85,0.03); }
        .responsive-table thead th { background:linear-gradient(180deg, rgba(0,40,85,0.05), rgba(0,40,85,0.02)); color:var(--primary-color); font-weight:700; }

        /* Badges */
        .badge { display:inline-block; padding:4px 8px; border-radius:999px; color:white; font-weight:700; font-size:0.75rem; }
        .badge--danger { background:#D62828; }
        .badge--success { background:#2E8B57; }
        .badge--amber { background:var(--accent-color); color:var(--primary-color); }

        /* Minor fade in */
        .kpi-card { animation: fadeInUp 600ms ease both; opacity:0; }
        @keyframes fadeInUp { from { transform:translateY(8px); opacity:0; } to { transform:translateY(0); opacity:1; } }
        [data-testid="stMetric"], .stPlotlyChart, .js-plotly-plot { animation: fadeInUp 650ms ease both; opacity:0; }
        .element-container { animation: fadeInUp 500ms ease both; opacity:0; }

        </style>
    """
    try:
        st.markdown(new_css, unsafe_allow_html=True)
    except Exception:
        pass

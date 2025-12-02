"""
Módulo de estilos CSS para CHAMPILYTICS.
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
    "YouTube": "#FF0000"
}

# ===========================
# FUNCIÓN DE INYECCIÓN CSS
# ===========================

def inject_custom_css():
    """Inyecta el CSS previo simple (pre-mejoras)."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
        :root {
            --primary-color: #003696;
            --primary-hover: #002a75;
            --bg-color: #F0F4FF;
            --card-bg: #E6EEFF;
            --sidebar-bg: #003696;
            --sidebar-text: #ffffff;
            --button-primary: #003696;
            --button-secondary: #E6EEFF;
        }
        .stApp {
            font-family: 'Montserrat', sans-serif !important;
            background-color: var(--bg-color);
        }
        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg) !important;
        }
        [data-testid="stSidebar"] * {
            color: var(--sidebar-text) !important;
        }
        div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
            background-color: var(--card-bg) !important;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            border: 1px solid #B3C6FF;
        }
        .stButton button {
            background-color: var(--button-primary) !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.5rem 1.2rem !important;
            font-weight: 600 !important;
            text-transform: none !important;
            box-shadow: 0 2px 5px rgba(0,54,150,0.2);
            transition: all 0.3s ease !important;
        }
        .stButton button:hover {
            background-color: var(--primary-hover) !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,54,150,0.3);
        }
        button[kind="secondary"] {
            background-color: var(--button-secondary) !important;
            border: 1px solid var(--primary-color) !important;
            color: var(--primary-color) !important;
        }
        [data-testid="stMetric"] {
            background-color: var(--card-bg);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #B3C6FF;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            text-align: center; 
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            color: #6c757d !important;
            font-weight: 500;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            color: var(--primary-color) !important;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

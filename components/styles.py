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
    "YouTube": "#FF0000",
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
        /* Asegurar texto negro en todos los contenedores principales */
        .element-container, .stMarkdown, .stText {
            color: #212529 !important;
        }
        /* Headers y títulos - texto oscuro */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #212529 !important;
        }
        /* Párrafos y texto general - solo aplicar donde no haya override específico */
        .stApp p {
            color: #212529 !important;
        }
        /* Excepciones para sidebar que debe mantener texto blanco */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] label {
            color: white !important;
        }
        /* Cajas de información, advertencia, etc. - texto negro */
        .stAlert {
            background-color: white !important;
        }
        .stAlert p, .stAlert div, .stAlert span {
            color: black !important;
        }
        /* Info boxes específicos */
        [data-testid="stAlert"] {
            background-color: white !important;
        }
        [data-testid="stAlert"] p,
        [data-testid="stAlert"] div,
        [data-testid="stAlert"] span {
            color: black !important;
        }
        /* Success, warning, error, info messages */
        .element-container .stAlert {
            color: black !important;
        }
        /* Tablas - fondo blanco, texto negro */
        .stDataFrame, [data-testid="stDataFrame"] {
            background-color: white !important;
        }
        .stDataFrame th, .stDataFrame td {
            color: black !important;
            background-color: white !important;
        }
        /* Labels de formularios */
        label {
            color: black !important;
        }
        [data-testid="stSidebar"] label {
            color: white !important;
        }
        /* Selectbox - texto negro sobre fondo blanco */
        [data-baseweb="select"] {
            color: black !important;
            background-color: white !important;
        }
        [data-baseweb="select"]:hover {
            border-color: var(--primary-color) !important;
        }
        [data-baseweb="select"] > div {
            color: black !important;
            background-color: white !important;
        }
        [data-baseweb="select"] input {
            color: black !important;
        }
        /* Opciones del dropdown */
        [data-baseweb="menu"] {
            background-color: white !important;
        }
        [data-baseweb="menu"] li {
            color: black !important;
            background-color: white !important;
        }
        [data-baseweb="menu"] li:hover {
            background-color: #f0f0f0 !important;
        }
        /* Text input, number input, date input */
        .stTextInput input, .stNumberInput input, .stDateInput input {
            color: black !important;
            background-color: white !important;
        }
        .stTextInput input::placeholder {
            color: #666 !important;
        }
        /* Text area */
        .stTextArea textarea {
            color: black !important;
            background-color: white !important;
        }
        .stTextArea textarea::placeholder {
            color: #666 !important;
        }
        /* Multiselect */
        [data-baseweb="tag"] {
            color: black !important;
            background-color: #e6eeff !important;
        }
        /* Radio buttons y checkboxes */
        .stRadio label, .stCheckbox label {
            color: black !important;
        }
        /* Slider */
        .stSlider [data-baseweb="slider"] {
            color: black !important;
        }
        /* Tabs - texto negro */
        .stTabs [data-baseweb="tab-list"] button {
            color: black !important;
        }
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            color: var(--primary-color) !important;
        }
        /* Expanders */
        .streamlit-expanderHeader {
            color: black !important;
            background-color: white !important;
        }
        .streamlit-expanderContent {
            background-color: white !important;
        }
        .streamlit-expanderContent p,
        .streamlit-expanderContent div {
            color: black !important;
        }
        /* File uploader */
        .stFileUploader label,
        .stFileUploader section {
            color: black !important;
        }
        /* Download button */
        .stDownloadButton button {
            color: white !important;
            background-color: var(--primary-color) !important;
        }
        /* Caption text */
        .caption, [data-testid="stCaptionContainer"] {
            color: #6c757d !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Animación fade-in para tarjetas KPI y micro-interacciones
    FADE_IN_CSS = """
    .kpi-card {
      animation: fadeInUp 600ms ease both;
      opacity: 0;
    }

    @keyframes fadeInUp {
      from { transform: translateY(8px); opacity: 0; }
      to   { transform: translateY(0); opacity: 1; }
    }

    .kpi-card .stCard { transition: transform 160ms ease, box-shadow 160ms ease; }
    .kpi-card:hover { transform: translateY(-4px); box-shadow: 0 6px 18px rgba(0,0,0,0.08); }
        /* Aplicar fade-in a métricas nativas de Streamlit para compatibilidad */
        [data-testid="stMetric"] {
            animation: fadeInUp 600ms ease both;
            opacity: 0;
        }

        /* Fade-in para contenedores de gráficos (Plotly/Altair) */
        .stPlotlyChart, .js-plotly-plot, [data-testid="stPlotlyChart"] {
            animation: fadeInUp 650ms ease both;
            opacity: 0;
        }
        .element-container {
            animation: fadeInUp 500ms ease both;
            opacity: 0;
        }
    """
    try:
        st.markdown(f"<style>{FADE_IN_CSS}</style>", unsafe_allow_html=True)
    except Exception:
        # No crítico; continuar si no se puede inyectar CSS
        pass

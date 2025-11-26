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
    """
    Inyecta CSS personalizado en la aplicación Streamlit.
    Define estilos minimalistas con alta legibilidad y contraste.
    
    Incluye:
    - Modo claro forzado con contraste alto
    - Tipografía profesional con jerarquía visual
    - Estilos para sidebar, botones, inputs, KPIs
    - Corrección de contraste en selectbox y date picker
    - Estilos para landing page con hero banner
    """
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
        
        /* ===========================
           MODO CLARO Y CONTRASTE
        =========================== */
        [data-testid="stAppViewContainer"] {{
            background-color: {COLOR_BG};
            color: {COLOR_TEXT};
        }}
        [data-testid="stHeader"] {{
            background-color: {COLOR_BG};
        }}
        .stApp {{
            font-family: 'Futura', 'Montserrat', 'Century Gothic', -apple-system, sans-serif;
            padding-top: 0 !important;
        }}
        .main .block-container {{
            padding-top: 2rem !important;
        }}
        
        /* ===========================
           SIDEBAR MINIMALISTA
        =========================== */
        [data-testid="stSidebar"] {{
            background-color: {COLOR_PRIMARY};
            padding-top: 1rem !important;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 1rem !important;
            margin-top: 0 !important;
        }}
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        [data-testid="collapsedControl"], button[kind="header"] {{
            display: block !important;
            visibility: visible !important;
        }}
        [data-testid="stSidebar"] .stRadio > label {{
            background-color: transparent !important;
            padding: 10px 15px !important;
            border-radius: 4px !important;
            transition: all 0.2s ease !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.5px !important;
        }}
        [data-testid="stSidebar"] .stRadio > label:hover {{
            background-color: rgba(255,255,255,0.1) !important;
        }}
        
        /* ===========================
           TARJETAS MINIMALISTAS
        =========================== */
        .css-card {{
            background-color: {COLOR_CARD};
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            margin-bottom: 24px;
            border: none;
            color: {COLOR_TEXT} !important;
        }}
        .css-card * {{
            color: {COLOR_TEXT} !important;
        }}
        .css-card h1, .css-card h2, .css-card h3 {{
            color: {COLOR_PRIMARY} !important;
        }}
        .css-card button, .css-card button * {{
            color: #FFFFFF !important;
        }}
        
        /* ===========================
           BOTONES MINIMALISTAS
        =========================== */
        button, 
        .stButton button,
        .stButton > button,
        .stDownloadButton button,
        .stDownloadButton > button,
        [data-testid="baseButton-primary"],
        [data-testid="baseButton-secondary"],
        [data-testid="baseButton-minimal"],
        [data-testid="stFormSubmitButton"] button,
        button[kind="primary"],
        button[kind="secondary"],
        button[kind="tertiary"],
        input[type="button"],
        input[type="submit"] {{
            background-color: {COLOR_PRIMARY} !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 4px !important;
            font-weight: 500 !important;
            font-size: 0.95rem !important;
            letter-spacing: 0.5px !important;
            padding: 0.65rem 1.5rem !important;
            transition: all 0.15s ease !important;
            cursor: pointer !important;
            text-transform: uppercase !important;
        }}
        button:hover,
        .stButton button:hover,
        .stButton > button:hover,
        .stDownloadButton button:hover,
        .stDownloadButton > button:hover,
        [data-testid="baseButton-primary"]:hover,
        [data-testid="baseButton-secondary"]:hover,
        [data-testid="baseButton-minimal"]:hover,
        [data-testid="stFormSubmitButton"] button:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        button[kind="tertiary"]:hover {{
            background-color: {COLOR_SECONDARY} !important;
            color: #FFFFFF !important;
            opacity: 0.9 !important;
        }}
        button:active,
        .stButton button:active,
        .stDownloadButton button:active {{
            background-color: #001a4d !important;
            color: #FFFFFF !important;
            transform: translateY(0) !important;
        }}
        button span, button p, button div,
        .stButton span, .stDownloadButton span {{
            color: #FFFFFF !important;
        }}
        [data-testid="stFormSubmitButton"] > button {{
            background-color: {COLOR_PRIMARY} !important;
            color: #FFFFFF !important;
            width: 100% !important;
            padding: 0.75rem !important;
            font-size: 16px !important;
            font-weight: 700 !important;
        }}
        [data-testid="stFormSubmitButton"] > button:hover {{
            background-color: {COLOR_SECONDARY} !important;
            color: #FFFFFF !important;
        }}
        
        /* ===========================
           KPIs MINIMALISTAS
        =========================== */
        [data-testid="stMetric"] {{
            background-color: transparent !important;
            border-radius: 0;
            padding: 20px 10px;
            border: none;
            border-bottom: 2px solid #E5E7EB;
            text-align: center;
            box-shadow: none;
        }}
        [data-testid="stMetricLabel"] {{
            font-size: 11px !important;
            color: {COLOR_CAPTION} !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }}
        [data-testid="stMetricValue"] {{
            color: {COLOR_PRIMARY} !important;
            font-size: 32px !important;
            font-weight: 300 !important;
            letter-spacing: -1px !important;
        }}
        [data-testid="stMetricDelta"] {{
            color: {COLOR_TEXT} !important;
            font-weight: 600 !important;
        }}
        
        /* ===========================
           INPUTS Y SELECTBOX
        =========================== */
        .stSelectbox label, .stNumberInput label, .stDateInput label, .stTextInput label {{
            color: {COLOR_TEXT} !important;
            font-weight: 600 !important;
        }}
        .stSelectbox > div > div, .stNumberInput > div > div, 
        .stDateInput > div > div, .stTextInput > div > div {{
            background-color: white !important;
            color: {COLOR_TEXT} !important;
            border: 1px solid #D1D5DB !important;
        }}
        .stSelectbox [data-baseweb="select"] {{
            background-color: white !important;
        }}
        .stSelectbox [data-baseweb="select"] > div {{
            color: {COLOR_TEXT} !important;
            background-color: white !important;
        }}
        .stSelectbox [data-baseweb="select"] span {{
            color: {COLOR_TEXT} !important;
        }}
        [role="listbox"] {{
            background-color: white !important;
        }}
        [role="option"] {{
            color: {COLOR_TEXT} !important;
            background-color: white !important;
        }}
        [role="option"]:hover {{
            background-color: #F3F4F6 !important;
            color: {COLOR_TEXT} !important;
        }}
        input, textarea, select {{
            color: {COLOR_TEXT} !important;
            background-color: white !important;
        }}
        .stSlider label {{
            color: {COLOR_TEXT} !important;
        }}
        .stDateInput input {{
            color: {COLOR_TEXT} !important;
            background-color: white !important;
        }}
        
        /* Date picker calendario */
        [data-baseweb="calendar"] {{
            background-color: white !important;
        }}
        [data-baseweb="calendar"] * {{
            color: {COLOR_TEXT} !important;
            background-color: white !important;
        }}
        [data-baseweb="calendar"] button {{
            color: {COLOR_TEXT} !important;
            background-color: white !important;
        }}
        [data-baseweb="calendar"] button:hover {{
            background-color: #F3F4F6 !important;
            color: {COLOR_TEXT} !important;
        }}
        [data-baseweb="calendar"] [aria-selected="true"] {{
            background-color: {COLOR_PRIMARY} !important;
            color: white !important;
        }}
        [data-baseweb="calendar-header"] {{
            background-color: white !important;
        }}
        [data-baseweb="calendar-header"] * {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* ===========================
           TIPOGRAFÍA PROFESIONAL
        =========================== */
        h1 {{ 
            color: {COLOR_PRIMARY} !important; 
            font-weight: 800 !important; 
            font-size: 2.5rem !important;
            letter-spacing: 2px !important;
            margin-bottom: 0.5rem !important;
            text-transform: uppercase !important;
        }}
        h2 {{ 
            color: {COLOR_PRIMARY} !important; 
            font-weight: 700 !important; 
            font-size: 2rem !important;
            letter-spacing: 1.5px !important;
            margin-bottom: 1rem !important;
        }}
        h3 {{ 
            color: {COLOR_PRIMARY} !important; 
            font-weight: 600 !important; 
            font-size: 1.5rem !important;
            letter-spacing: 1px !important;
            margin-bottom: 0.75rem !important;
        }}
        h4 {{
            color: {COLOR_TEXT} !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
        }}
        p, li, span, div, label {{ 
            color: {COLOR_TEXT} !important;
            font-weight: 400 !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
        }}
        .stCaption {{
            color: {COLOR_CAPTION} !important;
            font-size: 0.875rem !important;
            font-weight: 300 !important;
            letter-spacing: 0.5px !important;
        }}
        
        /* ===========================
           REGLAS GLOBALES DE CONTRASTE
        =========================== */
        [data-testid*="st"] {{
            color: {COLOR_TEXT} !important;
        }}
        .stAlert {{
            background-color: white !important;
        }}
        .stAlert * {{
            color: {COLOR_TEXT} !important;
        }}
        .streamlit-expanderHeader {{
            background-color: white !important;
            color: {COLOR_TEXT} !important;
        }}
        .stMarkdown {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* ===========================
           TABLAS
        =========================== */
        [data-testid="stDataFrame"] {{
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            background-color: white;
        }}
        [data-testid="stDataFrame"] * {{
            color: {COLOR_TEXT} !important;
        }}
        [data-testid="data-grid-canvas"] {{
            background-color: white !important;
        }}
        [data-testid="data-grid-canvas"] * {{
            color: {COLOR_TEXT} !important;
        }}
        
        /* ===========================
           TABS MINIMALISTAS
        =========================== */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: white !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: white !important;
            border: none !important;
            border-bottom: 2px solid transparent !important;
            padding: 12px 20px !important;
        }}
        .stTabs [data-baseweb="tab"] p, 
        .stTabs [data-baseweb="tab"] span,
        .stTabs [data-baseweb="tab"] div {{
            color: {COLOR_CAPTION} !important;
            font-weight: 500 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            font-size: 0.85rem !important;
        }}
        .stTabs [data-baseweb="tab"]:hover p,
        .stTabs [data-baseweb="tab"]:hover span {{
            color: {COLOR_PRIMARY} !important;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            background-color: rgba(0, 54, 150, 0.05) !important;
        }}
        .stTabs [aria-selected="true"] {{
            border-bottom-color: {COLOR_PRIMARY} !important;
            background-color: white !important;
        }}
        .stTabs [aria-selected="true"] p, 
        .stTabs [aria-selected="true"] span,
        .stTabs [aria-selected="true"] div {{
            color: {COLOR_PRIMARY} !important;
        }}
        [data-testid="stTabContent"] {{
            background-color: white !important;
        }}
        [data-testid="stTabContent"] * {{
            color: {COLOR_TEXT} !important;
        }}
        [data-testid="stTabContent"] h1, 
        [data-testid="stTabContent"] h2, 
        [data-testid="stTabContent"] h3 {{
            color: {COLOR_PRIMARY} !important;
        }}
        
        /* ===========================
           LANDING PAGE
        =========================== */
        .hero-banner {{
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            margin: -2rem -6rem 0 -6rem;
            padding: 0;
            width: calc(100% + 12rem);
            min-height: 100vh;
            text-align: center;
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .hero-banner::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(180deg, rgba(0, 54, 150, 0.7) 0%, rgba(0, 0, 0, 0.5) 100%);
            z-index: 1;
        }}
        .hero-content {{
            position: relative;
            z-index: 2;
            color: white !important;
            padding: 40px;
        }}
        .hero-content h1, .hero-content p {{
            color: white !important;
            font-weight: 300 !important;
            letter-spacing: 2px !important;
        }}
        .followers-counter {{
            font-size: 3.5rem !important;
            font-weight: 800 !important;
            color: white !important;
            text-shadow: 2px 2px 20px rgba(0,0,0,0.4);
            letter-spacing: 3px !important;
            margin-top: 20px;
            animation: fadeInUp 1s ease-out;
        }}
        .followers-label {{
            font-size: 1rem !important;
            font-weight: 300 !important;
            color: rgba(255,255,255,0.9) !important;
            letter-spacing: 3px !important;
            text-transform: uppercase;
        }}
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        /* Ocultar elementos nativos */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

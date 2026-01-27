"""
Módulo de estilos CSS para CHAMPILEAKS.
Define constantes de colores institucionales y función de inyección de CSS global.
"""

import streamlit as st

# ===========================
# CONSTANTES DE COLOR INSTITUCIONALES
# ===========================

# ===========================
# CHAMPI_THEME - Single Source of Truth para colores
# ===========================

CHAMPI_THEME = {
    # Colores Institucionales Maristas
    "primary": "#003696",      # Azul Marista
    "secondary": "#002566",    # Azul oscuro
    "accent": "#FFB81C",       # Amarillo acento
    
    # Sistema de fondos
    "bg": "#FFFFFF",           # Fondo blanco absoluto
    "card": "#F2F4F7",         # Cards gris claro
    "sidebar": "#003696",      # Sidebar azul institucional
    
    # Sistema de texto
    "text": "#212529",         # Texto principal negro
    "text_secondary": "#495057",  # Texto secundario gris oscuro
    "text_on_dark": "#FFFFFF",   # Texto sobre fondos oscuros
    "caption": "#6C757D",      # Texto de caption/subtítulos
    
    # Bordes
    "border": "#DEE2E6",       # Bordes sutiles
    
    # Estados
    "success": "#0A7D35",      # Verde accesible WCAG AA
    "danger": "#B42318",       # Rojo accesible WCAG AA
    "warning": "#CC7000",      # Naranja WCAG AA
    "info": "#0056B3",         # Azul información
    
    # Redes Sociales (Corregidos para mayor precisión)
    "facebook": "#1877F2",
    "instagram": "#C13584",    # Corregido de #E1306C
    "tiktok": "#000000",
    "twitter": "#1A8CD8",      # Corregido de #1DA1F2
    "linkedin": "#0A66C2",
    "youtube": "#FF0000",
}

# Compatibilidad con código legacy
COLOR_PRIMARY = CHAMPI_THEME["primary"]
COLOR_SECONDARY = CHAMPI_THEME["secondary"]
COLOR_ACCENT = CHAMPI_THEME["accent"]
COLOR_BG = CHAMPI_THEME["bg"]
COLOR_CARD = CHAMPI_THEME["card"]
COLOR_SIDEBAR = CHAMPI_THEME["sidebar"]
COLOR_TEXT = CHAMPI_THEME["text"]
COLOR_TEXT_SECONDARY = CHAMPI_THEME["text_secondary"]
COLOR_TEXT_ON_DARK = CHAMPI_THEME["text_on_dark"]
COLOR_CAPTION = CHAMPI_THEME["caption"]
COLOR_BORDER = CHAMPI_THEME["border"]
COLOR_SUCCESS = CHAMPI_THEME["success"]
COLOR_DANGER = CHAMPI_THEME["danger"]
COLOR_WARNING = CHAMPI_THEME["warning"]
COLOR_INFO = CHAMPI_THEME["info"]

# Mapa de colores por plataforma (para gráficos)
COLOR_MAP = {
    "Facebook": CHAMPI_THEME["facebook"],
    "Instagram": CHAMPI_THEME["instagram"],
    "TikTok": CHAMPI_THEME["tiktok"],
    "Twitter/X": CHAMPI_THEME["twitter"],
    "LinkedIn": CHAMPI_THEME["linkedin"],
    "YouTube": CHAMPI_THEME["youtube"],
}


def inject_custom_css():
    """
    Inyecta CSS global institucional para toda la aplicación CHAMPILEAKS.
    
    Sistema de diseño:
    - Fondo blanco absoluto (#FFFFFF)
    - Cards gris claro (#F2F4F7)
    - Todo el texto negro/gris oscuro (#212529)
    - Sidebar azul institucional con texto blanco
    - Sin fondos negros, sombras pesadas ni glassmorphism
    - Contraste WCAG AA en todos los elementos
    - Optimización móvil responsive (tablets, móviles)
    """
    from utils.global_styles import get_global_institutional_css
    from utils.mobile_styles import get_mobile_css
    
    # Inyectar estilos base globales
    st.markdown(get_global_institutional_css(), unsafe_allow_html=True)
    
    # Inyectar estilos móviles responsive
    st.markdown(get_mobile_css(), unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        /* ========================================
           INPUTS Y FORMULARIOS (Accesibilidad AA)
        ======================================== */
        
        /* Labels de inputs - tamaño legible */
        .stSelectbox label,
        .stTextInput label,
        .stNumberInput label,
        .stDateInput label,
        .stTextArea label,
        .stFileUploader label,
        .stMultiSelect label,
        .stRadio label,
        .stCheckbox label,
        [data-testid="stWidgetLabel"] {
            color: var(--text-color) !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Inputs - fondo con contraste y tamaño mínimo 16px */
        input,
        textarea,
        select,
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox select,
        .stTextArea textarea,
        [role="textbox"],
        [role="combobox"] {
            background-color: var(--card-bg) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
            font-size: 16px !important; /* Evita zoom en iOS */
            line-height: 1.5 !important;
            transition: border-color 0.2s ease !important;
        }
        
        /* Focus states accesibles */
        input:focus,
        textarea:focus,
        select:focus {
            border-color: var(--primary-color) !important;
            outline: 2px solid var(--primary-color) !important;
            outline-offset: 2px !important;
        }
        
        /* Placeholder legible */
        input::placeholder,
        textarea::placeholder {
            color: var(--text-secondary) !important;
            opacity: 0.7 !important;
        }

        
        /* ========================================
           SIDEBAR - Preservar colores azules
        ======================================== */
        [data-testid="stSidebar"] { 
            background-color: var(--sidebar-bg) !important;
        }
        
        [data-testid="stSidebar"] *,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: var(--sidebar-text) !important;
        }
        
        /* ========================================
           HEADER Y TOOLBAR - No modificar
        ======================================== */
        [data-testid="stHeader"] *,
        [data-testid="stToolbar"] *,
        [data-testid="stToolbarActions"] *,
        .stMainMenu *,
        [class*="stAppHeader"] *,
        [class*="stToolbar"] * {
            color: inherit !important;
            background: inherit !important;
        }

        /* ========================================
           TARJETAS KPI CON CONTRASTE WCAG AA
        ======================================== */
        .kpi-cards { 
            display: flex; 
            gap: 16px; 
            flex-wrap: wrap; 
            margin-bottom: 12px; 
        }
        
        .kpi-card { 
            background: var(--card-bg) !important; 
            border-radius: 12px; 
            padding: 16px 20px; 
            flex: 1 1 220px; 
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); 
            border: 1px solid var(--border-color); 
            border-left: 4px solid var(--accent-color); 
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
        }
        
        .kpi-card .kpi-title { 
            color: var(--primary-color) !important; 
            font-weight: 700 !important; 
            font-size: 1rem !important; 
            margin-bottom: 8px !important;
        }
        
        .kpi-card .kpi-value { 
            color: var(--text-color) !important; 
            font-weight: 800 !important; 
            font-size: 2rem !important; 
            line-height: 1 !important;
        }
        
        .kpi-card .kpi-delta { 
            color: var(--success-color) !important; 
            font-weight: 700 !important; 
            font-size: 0.95rem !important;
            margin-top: 6px !important;
        }
        
        .kpi-card .kpi-subtitle { 
            color: var(--text-secondary) !important; 
            font-size: 0.875rem !important; 
            margin-top: 8px !important;
        }

        /* ========================================
           BOTONES ACCESIBLES
        ======================================== */
        .stButton button,
        button[data-testid*="baseButton"],
        [data-testid="stBaseButton-primary"],
        button[kind="primary"] {
            background-color: var(--button-primary) !important;
            color: var(--button-text) !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            text-transform: none !important;
            box-shadow: 0 2px 6px rgba(0, 57, 102, 0.15) !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
        }
        
        /* Forzar texto blanco en todos los elementos del botón primary */
        .stButton button *,
        button[kind="primary"] *,
        [data-testid="stBaseButton-primary"] *,
        .stButton button p,
        button[kind="primary"] p,
        .stButton button span,
        button[kind="primary"] span {
            color: var(--button-text) !important;
        }

        .stButton button:hover,
        button[kind="primary"]:hover {
            background-color: var(--button-primary-hover) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(0, 57, 102, 0.22) !important;
        }
        
        /* Focus visible para accesibilidad de teclado */
        .stButton button:focus-visible,
        button[kind="primary"]:focus-visible {
            outline: 3px solid var(--accent-color) !important;
            outline-offset: 2px !important;
        }
        
        button[kind="secondary"],
        [data-testid="stBaseButton-secondary"] {
            background-color: var(--button-secondary-bg) !important;
            border: 2px solid var(--primary-color) !important;
            color: var(--primary-color) !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            box-shadow: 0 2px 6px rgba(0, 57, 102, 0.1) !important;
            transition: all 0.2s ease !important;
        }
        
        /* Texto azul en botones secondary */
        button[kind="secondary"] *,
        [data-testid="stBaseButton-secondary"] *,
        button[kind="secondary"] p,
        button[kind="secondary"] span {
            color: var(--primary-color) !important;
        }
        
        button[kind="secondary"]:hover {
            background-color: var(--primary-color) !important;
            color: var(--button-text) !important;
        }
        
        /* Texto blanco en hover de secondary */
        button[kind="secondary"]:hover *,
        button[kind="secondary"]:hover p,
        button[kind="secondary"]:hover span {
            color: var(--button-text) !important;
        }
        
        /* ========================================
           BOTONES DE DESCARGA (Download Button)
        ======================================== */
        .stDownloadButton button,
        .stDownloadButton button[kind="secondary"],
        div[data-testid="stDownloadButton"] button {
            background-color: var(--primary-color) !important;
            color: var(--button-text) !important;
            border: 2px solid var(--primary-color) !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
        }
        
        /* Forzar texto blanco en botones de descarga */
        .stDownloadButton button *,
        .stDownloadButton button p,
        .stDownloadButton button span,
        .stDownloadButton button div,
        div[data-testid="stDownloadButton"] button *,
        div[data-testid="stDownloadButton"] button p {
            color: var(--button-text) !important;
        }
        
        .stDownloadButton button:hover,
        div[data-testid="stDownloadButton"] button:hover {
            background-color: var(--accent-color) !important;
            color: var(--text-color) !important;
            border-color: var(--accent-color) !important;
        }
        
        /* Texto oscuro en hover */
        .stDownloadButton button:hover *,
        .stDownloadButton button:hover p,
        div[data-testid="stDownloadButton"] button:hover * {
            color: var(--text-color) !important;
        }

        /* ========================================
           MÉTRICAS STREAMLIT
        ======================================== */
        [data-testid="stMetric"] { 
            background-color: var(--card-bg) !important; 
            padding: 16px !important; 
            border-radius: 10px !important; 
            border: 1px solid var(--border-color) !important; 
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important; 
            text-align: center !important;
        }
        
        [data-testid="stMetricValue"] { 
            font-size: 2rem !important; 
            color: var(--text-color) !important; 
            font-weight: 700 !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: var(--text-secondary) !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
        }


        /* ========================================
           IMÁGENES Y MULTIMEDIA
        ======================================== */
        /* Logo en Sidebar */
        .logo-marista {
            width: 180px !important;
            height: auto !important;
            display: block !important;
            margin: 20px auto 10px auto !important;
            border-radius: 8px !important;
        }

        /* Banner Hero en Landing */
        .hero-banner {
            position: relative;
            height: 500px !important;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        
        .hero-banner::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(180deg, rgba(0,0,0,0.4), rgba(0,0,0,0.6));
            z-index: 1;
        }
        
        .hero-banner .hero-content {
            position: relative;
            z-index: 2;
            color: white !important;
            text-align: center;
            padding: 20px;
        }
        
        .hero-banner .hero-content * {
            color: white !important;
        }
        
        /* ========================================
           TABLAS RESPONSIVAS Y ACCESIBLES
        ======================================== */
        .responsive-table { 
            width: 100%; 
            overflow-x: auto; 
            border-radius: 8px; 
            margin: 16px 0;
        }
        
        .responsive-table table { 
            width: 100%; 
            border-collapse: collapse; 
            min-width: 600px; 
        }
        
        .responsive-table th, 
        .responsive-table td { 
            padding: 12px 16px; 
            text-align: left; 
            border-bottom: 1px solid var(--border-color);
            font-size: 15px;
        }
        
        .responsive-table thead th { 
            background: var(--primary-color);
            color: #FFFFFF !important;
            font-weight: 700;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .responsive-table tbody tr {
            background: var(--card-bg);
            transition: background-color 0.2s ease;
        }
        
        .responsive-table tbody tr:hover { 
            background-color: rgba(0, 54, 150, 0.05);
        }
        
        .responsive-table tbody tr:nth-child(even) {
            background-color: rgba(0, 0, 0, 0.02);
        }

        /* ========================================
           BADGES Y ETIQUETAS
        ======================================== */
        .badge { 
            display: inline-block; 
            padding: 6px 12px; 
            border-radius: 999px; 
            color: white !important; 
            font-weight: 700; 
            font-size: 0.8rem;
            line-height: 1;
        }
        
        .badge--danger { 
            background: var(--danger-color) !important; 
        }
        
        .badge--success { 
            background: var(--success-color) !important; 
        }
        
        .badge--warning { 
            background: var(--warning-color) !important; 
        }
        
        .badge--info { 
            background: var(--info-color) !important; 
        }
        
        .badge--amber { 
            background: var(--accent-color) !important; 
            color: var(--primary-color) !important; 
        }

        /* ========================================
           ANIMACIONES SUAVES
        ======================================== */
        @keyframes fadeInUp { 
            from { 
                transform: translateY(12px); 
                opacity: 0; 
            } 
            to { 
                transform: translateY(0); 
                opacity: 1; 
            } 
        }
        
        .kpi-card { 
            animation: fadeInUp 600ms ease both; 
            opacity: 0; 
        }
        
        [data-testid="stMetric"], 
        .stPlotlyChart, 
        .js-plotly-plot { 
            animation: fadeInUp 650ms ease both; 
            opacity: 0; 
        }
        
        .element-container { 
            animation: fadeInUp 500ms ease both; 
            opacity: 0; 
        }
        
        /* ========================================
           ACCESIBILIDAD - REDUCIR MOVIMIENTO
        ======================================== */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
        
        /* ========================================
           RESPONSIVE - MÓVILES
        ======================================== */
        @media (max-width: 768px) {
            .stMarkdown h1 {
                font-size: 1.75rem !important;
            }
            
            .stMarkdown h2 {
                font-size: 1.5rem !important;
            }
            
            .kpi-cards {
                flex-direction: column;
            }
            
            .kpi-card {
                flex: 1 1 100%;
            }
        }

        </style>
    """, unsafe_allow_html=True)


def aplicar_estilo_personalizado():
    """
    Sistema de temas dinámico con selector en sidebar.
    Permite al usuario elegir entre Tema Claro y Oscuro.
    Unifica el diseño de todos los inputs con contraste perfecto.
    
    Returns:
        str: Tema seleccionado ('Claro' o 'Oscuro')
    """
    import streamlit as st
    
    # Inicializar tema en session_state si no existe
    if 'tema' not in st.session_state:
        st.session_state.tema = 'Claro'
    
    # Selector de tema en sidebar con emoji
    with st.sidebar:
        st.markdown("---")
        tema_seleccionado = st.radio(
            "🎨 Tema de la Aplicación",
            options=['Claro', 'Oscuro'],
            index=0 if st.session_state.tema == 'Claro' else 1,
            help="Cambia entre modo claro y oscuro para mejor legibilidad"
        )
        
        # Actualizar session_state
        st.session_state.tema = tema_seleccionado
    
    # Definir paletas de color según tema
    if tema_seleccionado == 'Oscuro':
        theme = {
            # Fondos
            'bg_primary': '#0E1117',
            'bg_secondary': '#1E2228',
            'bg_card': '#262730',
            'bg_input': '#1E2228',
            'bg_hover': '#2D3139',
            
            # Textos
            'text_primary': '#FAFAFA',
            'text_secondary': '#B8B8B8',
            'text_caption': '#8B8B8B',
            'text_placeholder': '#6B6B6B',
            
            # Bordes
            'border_color': '#3A3F47',
            'border_focus': '#0056B3',
            
            # Institucionales (mantener)
            'primary': '#4A90E2',  # Azul más claro para oscuro
            'accent': '#FFB81C',
        }
    else:  # Claro
        theme = {
            # Fondos
            'bg_primary': '#FFFFFF',
            'bg_secondary': '#F4F6F9',
            'bg_card': '#FFFFFF',
            'bg_input': '#FFFFFF',
            'bg_hover': '#F0F2F6',
            
            # Textos
            'text_primary': '#1A1A1A',
            'text_secondary': '#4A5568',
            'text_caption': '#5A5A5A',
            'text_placeholder': '#9CA3AF',
            
            # Bordes
            'border_color': '#D1D5DB',
            'border_focus': '#003696',
            
            # Institucionales
            'primary': '#003696',
            'accent': '#FFB81C',
        }
    
    # Inyectar CSS dinámico
    css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* ========================================
           VARIABLES CSS DINÁMICAS - TEMA {tema_seleccionado.upper()}
        ======================================== */
        :root {{
            /* Fondos */
            --background-color: {theme['bg_primary']};
            --bg-secondary: {theme['bg_secondary']};
            --bg-card: {theme['bg_card']};
            --input-bg: {theme['bg_input']};
            --bg-hover: {theme['bg_hover']};
            
            /* Textos */
            --text-color: {theme['text_primary']};
            --text-secondary: {theme['text_secondary']};
            --text-caption: {theme['text_caption']};
            --text-placeholder: {theme['text_placeholder']};
            
            /* Bordes */
            --border-color: {theme['border_color']};
            --border-focus: {theme['border_focus']};
            
            /* Institucionales */
            --primary-color: {theme['primary']};
            --accent-color: {theme['accent']};
            
            /* Sidebar (siempre azul institucional) */
            --sidebar-bg: #003696;
            --sidebar-text: #FFFFFF;
        }}
        
        /* ========================================
           APLICACIÓN GLOBAL DE TEMA
        ======================================== */
        .stApp,
        [data-testid="stAppViewContainer"],
        .main {{
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: var(--background-color) !important;
            color: var(--text-color) !important;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        /* Párrafos con line-height óptimo */
        p, .stMarkdown p {{
            line-height: 1.6 !important;
        }}
        
        /* Contenedores principales */
        [data-testid="stMainBlockContainer"],
        [data-testid="block-container"],
        .block-container {{
            background-color: var(--background-color) !important;
            color: var(--text-color) !important;
        }}
        
        /* ========================================
           INPUTS UNIFICADOS - DISEÑO CONSISTENTE
        ======================================== */
        
        /* SELECTBOX / COMBOBOX */
        .stSelectbox > div > div,
        [data-baseweb="select"],
        [data-baseweb="select"] > div,
        div[role="combobox"],
        div[data-testid="stSelectbox"] > div > div {{
            background-color: var(--input-bg) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            font-size: 16px !important;
            font-weight: 500 !important;
            padding: 10px 16px !important;
            transition: all 0.2s ease !important;
            min-height: 48px !important;
        }}
        
        /* Hover en selectbox */
        .stSelectbox > div > div:hover,
        [data-baseweb="select"]:hover,
        div[role="combobox"]:hover {{
            border-color: var(--border-focus) !important;
            background-color: var(--bg-hover) !important;
            box-shadow: 0 0 0 3px rgba(0, 86, 179, 0.1) !important;
        }}
        
        /* Focus en selectbox */
        .stSelectbox > div > div:focus-within,
        [data-baseweb="select"]:focus-within {{
            border-color: var(--border-focus) !important;
            outline: 2px solid var(--border-focus) !important;
            outline-offset: 2px !important;
            box-shadow: 0 0 0 4px rgba(0, 86, 179, 0.15) !important;
        }}
        
        /* Opciones del dropdown */
        [role="listbox"],
        [data-baseweb="popover"] {{
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
        }}
        
        [role="option"],
        li[role="option"] {{
            background-color: var(--input-bg) !important;
            color: var(--text-color) !important;
            font-size: 16px !important;
            padding: 12px 16px !important;
            transition: background-color 0.15s ease !important;
        }}
        
        [role="option"]:hover,
        li[role="option"]:hover {{
            background-color: var(--bg-hover) !important;
            color: var(--primary-color) !important;
        }}
        
        /* TEXT INPUT */
        .stTextInput input,
        input[type="text"],
        input[type="email"],
        input[type="password"],
        input[type="number"] {{
            background-color: var(--input-bg) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            font-size: 16px !important;
            font-weight: 500 !important;
            padding: 12px 16px !important;
            transition: all 0.2s ease !important;
            caret-color: var(--primary-color) !important;
        }}
        
        .stTextInput input:hover,
        input:hover {{
            border-color: var(--border-focus) !important;
            background-color: var(--bg-hover) !important;
        }}
        
        .stTextInput input:focus,
        input:focus {{
            border-color: var(--border-focus) !important;
            outline: 2px solid var(--border-focus) !important;
            outline-offset: 2px !important;
            box-shadow: 0 0 0 4px rgba(0, 86, 179, 0.15) !important;
        }}
        
        /* Placeholder con contraste perfecto */
        .stTextInput input::placeholder,
        input::placeholder,
        textarea::placeholder {{
            color: var(--text-placeholder) !important;
            opacity: 0.8 !important;
            font-weight: 400 !important;
        }}
        
        /* NUMBER INPUT */
        .stNumberInput input {{
            background-color: var(--input-bg) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            font-size: 16px !important;
            padding: 12px 16px !important;
        }}
        
        /* TEXTAREA */
        .stTextArea textarea,
        textarea {{
            background-color: var(--input-bg) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            font-size: 16px !important;
            padding: 12px 16px !important;
            line-height: 1.6 !important;
            font-family: 'Inter', sans-serif !important;
        }}
        
        .stTextArea textarea:focus {{
            border-color: var(--border-focus) !important;
            outline: 2px solid var(--border-focus) !important;
            outline-offset: 2px !important;
        }}
        
        /* DATE INPUT */
        .stDateInput input {{
            background-color: var(--input-bg) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            font-size: 16px !important;
            padding: 12px 16px !important;
        }}
        
        /* MULTISELECT */
        .stMultiSelect > div > div {{
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        
        /* ========================================
           LABELS CON CONTRASTE PERFECTO
        ======================================== */
        .stSelectbox label,
        .stTextInput label,
        .stNumberInput label,
        .stTextArea label,
        .stDateInput label,
        .stMultiSelect label,
        .stFileUploader label,
        .stRadio label,
        .stCheckbox label,
        [data-testid="stWidgetLabel"] {{
            color: var(--text-color) !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            margin-bottom: 8px !important;
        }}
        
        /* ========================================
           SIDEBAR INSTITUCIONAL (SIEMPRE AZUL)
        ======================================== */
        [data-testid="stSidebar"] {{
            background-color: var(--sidebar-bg) !important;
        }}
        
        [data-testid="stSidebar"] *,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p {{
            color: var(--sidebar-text) !important;
        }}
        
        /* Inputs en sidebar con fondo semi-transparente */
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] select,
        [data-testid="stSidebar"] .stSelectbox > div > div {{
            background-color: rgba(255, 255, 255, 0.15) !important;
            border-color: rgba(255, 255, 255, 0.3) !important;
            color: white !important;
        }}
        
        /* ========================================
           TIPOGRAFÍA CON JERARQUÍA CLARA
        ======================================== */
        .stMarkdown h1 {{
            color: var(--primary-color) !important;
            font-weight: 700 !important;
            font-size: 2.25rem !important;
            margin-bottom: 1rem !important;
        }}
        
        .stMarkdown h2 {{
            color: var(--primary-color) !important;
            font-weight: 600 !important;
            font-size: 1.875rem !important;
            margin-bottom: 0.875rem !important;
        }}
        
        .stMarkdown h3 {{
            color: var(--text-color) !important;
            font-weight: 600 !important;
            font-size: 1.5rem !important;
        }}
        
        .stMarkdown p,
        .stMarkdown li,
        .stMarkdown span {{
            color: var(--text-color) !important;
            font-size: 16px !important;
            line-height: 1.6 !important;
        }}
        
        /* ========================================
           TARJETAS Y MÉTRICAS
        ======================================== */
        [data-testid="stMetric"] {{
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            padding: 16px !important;
            border-radius: 10px !important;
        }}
        
        [data-testid="stMetricValue"] {{
            color: var(--text-color) !important;
            font-weight: 700 !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            color: var(--text-secondary) !important;
        }}
        
        /* ========================================
           BOTONES CON TEMA
        ======================================== */
        .stButton button,
        button[kind="primary"] {{
            background-color: var(--primary-color) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }}
        
        .stButton button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(0, 54, 150, 0.25) !important;
        }}
        
        /* ========================================
           TABLAS ADAPTATIVAS
        ======================================== */
        .dataframe {{
            background-color: var(--bg-card) !important;
            color: var(--text-color) !important;
        }}
        
        .dataframe th {{
            background-color: var(--primary-color) !important;
            color: white !important;
        }}
        
        .dataframe td {{
            border-color: var(--border-color) !important;
        }}
        
        /* ========================================
           INDICADOR DE TEMA ACTIVO
        ======================================== */
        .stRadio > label > div[data-testid="stMarkdownContainer"] p {{
            font-weight: 600 !important;
        }}
        
        </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    
    return tema_seleccionado
    """
    Configuración de tema Plotly accesible con fuentes legibles.
    Retorna diccionario de configuración para update_layout().
    """
    return {
        "font": {
            "family": "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            "size": 14,  # Tamaño mínimo legible
            "color": "#1A1A1A"  # Alto contraste
        },
        "title": {
            "font": {"size": 18, "color": "#003696", "family": "Inter"},
            "x": 0.5,
            "xanchor": "center"
        },
        "xaxis": {
            "title": {"font": {"size": 14, "color": "#4A5568"}},
            "tickfont": {"size": 12, "color": "#1A1A1A"},
            "gridcolor": "rgba(0, 0, 0, 0.08)"
        },
        "yaxis": {
            "title": {"font": {"size": 14, "color": "#4A5568"}},
            "tickfont": {"size": 12, "color": "#1A1A1A"},
            "gridcolor": "rgba(0, 0, 0, 0.08)"
        },
        "legend": {
            "font": {"size": 13, "color": "#1A1A1A"},
            "bgcolor": "rgba(255, 255, 255, 0.9)",
            "bordercolor": "rgba(0, 0, 0, 0.1)",
            "borderwidth": 1
        },
        "plot_bgcolor": "#FFFFFF",
        "paper_bgcolor": "#FFFFFF",
        "margin": {"l": 50, "r": 30, "t": 60, "b": 50},
        "hoverlabel": {
            "bgcolor": "#FFFFFF",
            "font": {"size": 13, "color": "#1A1A1A"},
            "bordercolor": "#003696"
        }
    }
    
    return tema_seleccionado


def configure_plotly_theme():
    """
    Configuración de tema Plotly accesible con fuentes legibles.
    Retorna diccionario de configuración para update_layout().
    """
    return {
        "font": {
            "family": "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            "size": 14,  # Tamaño mínimo legible
            "color": "#1A1A1A"  # Alto contraste
        },
        "title": {
            "font": {"size": 18, "color": "#003696", "family": "Inter"},
            "x": 0.5,
            "xanchor": "center"
        },
        "xaxis": {
            "title": {"font": {"size": 14, "color": "#4A5568"}},
            "tickfont": {"size": 12, "color": "#1A1A1A"},
            "gridcolor": "rgba(0, 0, 0, 0.08)"
        },
        "yaxis": {
            "title": {"font": {"size": 14, "color": "#4A5568"}},
            "tickfont": {"size": 12, "color": "#1A1A1A"},
            "gridcolor": "rgba(0, 0, 0, 0.08)"
        },
        "legend": {
            "font": {"size": 13, "color": "#1A1A1A"},
            "bgcolor": "rgba(255, 255, 255, 0.9)",
            "bordercolor": "rgba(0, 0, 0, 0.1)",
            "borderwidth": 1
        },
        "plot_bgcolor": "#FFFFFF",
        "paper_bgcolor": "#FFFFFF",
        "margin": {"l": 50, "r": 30, "t": 60, "b": 50},
        "hoverlabel": {
            "bgcolor": "#FFFFFF",
            "font": {"size": 13, "color": "#1A1A1A"},
            "bordercolor": "#003696"
        }
    }

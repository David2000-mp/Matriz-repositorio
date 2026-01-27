"""
Sistema de Estilos Global para CHAMPILEAKS.
CSS centralizado para toda la aplicación institucional.
"""


def get_global_institutional_css() -> str:
    """
    Retorna el CSS global institucional para CHAMPILEAKS.
    
    Principios de diseño:
    - Fondo blanco absoluto (#FFFFFF)
    - Cards/contenedores gris claro (#F2F4F7)
    - Todo el texto negro/gris oscuro (#212529)
    - Sidebar azul institucional con texto blanco
    - Sin fondos negros, sombras pesadas ni efectos agresivos
    - Contraste WCAG AA mínimo en todos los elementos
    
    Returns:
        String con CSS completo listo para st.markdown(unsafe_allow_html=True)
    """
    
    # Colores institucionales centralizados
    PRIMARY_BLUE = "#003696"         # Azul institucional Marista
    PRIMARY_BLUE_DARK = "#00235A"    # Azul oscuro para contraste
    ACCENT_YELLOW = "#FFB81C"        # Amarillo acento
    
    # Sistema de fondos
    BG_WHITE = "#FFFFFF"             # Fondo principal app
    BG_LIGHT_GRAY = "#F2F4F7"        # Cards y contenedores
    BG_SIDEBAR = PRIMARY_BLUE        # Sidebar azul institucional
    
    # Sistema de texto
    TEXT_PRIMARY = "#212529"         # Texto principal (negro)
    TEXT_SECONDARY = "#495057"       # Texto secundario (gris oscuro)
    TEXT_ON_DARK = "#FFFFFF"         # Texto sobre azul/sidebar
    
    # Bordes y separadores
    BORDER_LIGHT = "#DEE2E6"         # Bordes sutiles
    BORDER_MEDIUM = "#CED4DA"        # Bordes inputs
    
    # Estados
    HOVER_BG = "#E9ECEF"             # Hover claro
    SUCCESS = "#0A7D35"              # Verde accesible
    ERROR = "#B42318"                # Rojo accesible
    
    return f"""
    <style>
    /* ============================================
       CHAMPILEAKS - SISTEMA INSTITUCIONAL GLOBAL
       Diseño: Profesional Corporativo Marista
       Versión: 2.0 - Institucional Claro
       ============================================ */
    
    /* === RESET Y BASE === */
    
    /* Fondo blanco absoluto para toda la aplicación */
    .main, .block-container, section[data-testid="stMain"] {{
        background-color: {BG_WHITE} !important;
    }}
    
    /* Mejorar layout y spacing - aire respecto al sidebar */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 5rem !important;
        padding-right: 5rem !important;
        max-width: 95% !important;
    }}
    
    /* Tipografía base global con font smoothing */
    body,
    .stApp {{
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}
    
    /* Tipografía base - solo para contenido principal, NO sidebar */
    .main body,
    .main .stMarkdown,
    .main h1,
    .main h2,
    .main h3,
    .main h4,
    .main h5,
    .main h6,
    .main p,
    .main span {{
        font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        color: {TEXT_PRIMARY};
        line-height: 1.6;
    }}
    
    /* === SIDEBAR INSTITUCIONAL === */
    
    /* Sidebar azul institucional - FONDO AZUL FORZADO EN TODO */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarHeader"],
    [data-testid="stSidebarUserContent"],
    section[data-testid="stSidebar"] .st-emotion-cache-1r1cntt,
    section[data-testid="stSidebar"] .st-emotion-cache-8atqhb,
    section[data-testid="stSidebar"] .stVerticalBlock,
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
    section[data-testid="stSidebar"] .element-container {{
        background-color: {BG_SIDEBAR} !important;
    }}
    
    /* ELIMINAR TODOS LOS BORDES EN EL SIDEBAR (excepto inputs) */
    section[data-testid="stSidebar"] hr,
    section[data-testid="stSidebar"] .stMarkdown hr {{
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }}
    
    /* Tipografía sidebar - Inter con font smoothing */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}
    
    /* TODO EL TEXTO DEL SIDEBAR EN BLANCO (texto general) */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stCaption {{
        color: #FFFFFF !important;
        line-height: 1.6;
    }}
    
    /* Labels de widgets en BLANCO */
    section[data-testid="stSidebar"] .stSelectbox > label,
    section[data-testid="stSidebar"] .stRadio > label,
    section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] {{
        color: #FFFFFF !important;
    }}
    
    /* Títulos sidebar - tamaños explícitos para máxima visibilidad */
    section[data-testid="stSidebar"] h1 {{
        color: {TEXT_ON_DARK} !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        line-height: 1.4;
    }}
    
    section[data-testid="stSidebar"] h2 {{
        color: {TEXT_ON_DARK} !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        line-height: 1.4;
    }}
    
    section[data-testid="stSidebar"] h3 {{
        color: {TEXT_ON_DARK} !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        line-height: 1.4;
    }}
    
    /* === SELECTBOXES EN SIDEBAR === */
    
    /* Label del selectbox en BLANCO con alta visibilidad */
    section[data-testid="stSidebar"] .stSelectbox > label,
    section[data-testid="stSidebar"] .stSelectbox > [data-testid="stWidgetLabel"] {{
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }}
    
    /* Contenedor principal del selectbox - BLANCO SIN BORDES */
    section[data-testid="stSidebar"] .stSelectbox > div,
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {{
        background-color: {BG_WHITE} !important;
        border: none !important;
        border-radius: 5px !important;
    }}
    
    /* CRÍTICO: Forzar texto NEGRO en TODOS los elementos del selectbox */
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] *,
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div,
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div *,
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] input,
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] .stSelectbox input,
    section[data-testid="stSidebar"] .stSelectbox div[class*="st-c"],
    section[data-testid="stSidebar"] .stSelectbox div[class*="st-d"],
    section[data-testid="stSidebar"] div[data-baseweb="select"] div[class*="st-"],
    section[data-testid="stSidebar"] div[data-baseweb="select"] div[value] {{
        color: {TEXT_PRIMARY} !important;
        background-color: transparent !important;
    }}
    
    /* Fondo blanco para el input del selectbox */
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
    section[data-testid="stSidebar"] div[data-baseweb="select"] {{
        background-color: {BG_WHITE} !important;
    }}
    
    /* Dropdown (cuando se abre el selectbox) */
    section[data-testid="stSidebar"] div[role="listbox"],
    section[data-testid="stSidebar"] ul[role="listbox"] {{
        background-color: {BG_WHITE} !important;
        color: {TEXT_PRIMARY} !important;
    }}
    
    section[data-testid="stSidebar"] div[role="option"],
    section[data-testid="stSidebar"] li[role="option"] {{
        background-color: {BG_WHITE} !important;
        color: {TEXT_PRIMARY} !important;
    }}
    
    section[data-testid="stSidebar"] div[role="option"]:hover,
    section[data-testid="stSidebar"] li[role="option"]:hover {{
        background-color: {HOVER_BG} !important;
        color: {PRIMARY_BLUE} !important;
    }}
    
    /* === RADIO BUTTONS EN SIDEBAR === */
    
    /* Label del grupo de radio en BLANCO con alta visibilidad */
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {{
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }}
    
    /* Opciones individuales en BLANCO */
    section[data-testid="stSidebar"] .stRadio > div,
    section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"],
    section[data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] {{
        color: {TEXT_ON_DARK} !important;
    }}
    
    /* Texto de cada opción de radio */
    section[data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] p {{
        color: {TEXT_ON_DARK} !important;
    }}
    
    /* === BOTONES EN SIDEBAR === */
    
    section[data-testid="stSidebar"] .stButton > button {{
        background-color: rgba(255, 255, 255, 0.2) !important;
        color: {TEXT_ON_DARK} !important;
        border: none !important;
        font-weight: 500 !important;
    }}
    
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: {ACCENT_YELLOW} !important;
        color: {PRIMARY_BLUE_DARK} !important;
        border: none !important;
        border: 1px solid {ACCENT_YELLOW} !important;
    }}
    
    /* === CARDS Y CONTENEDORES === */
    
    /* Todas las cards con fondo gris claro */
    div[data-testid="stMetricValue"],
    div[data-testid="metric-container"],
    div[class*="card"],
    div[data-testid="column"] > div {{
        background-color: {BG_LIGHT_GRAY} !important;
        border: 1px solid {BORDER_LIGHT} !important;
        border-radius: 8px;
        padding: 16px;
    }}
    
    /* Eliminar fondo de element-container para evitar cajas grises */
    .element-container {{
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }}
    
    /* Métricas institucionales */
    div[data-testid="stMetricValue"] {{
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: {PRIMARY_BLUE} !important;
    }}
    
    div[data-testid="stMetricLabel"] {{
        font-size: 0.95rem !important;
        color: {TEXT_SECONDARY} !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    div[data-testid="stMetricDelta"] {{
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: {SUCCESS} !important;
    }}
    
    div[data-testid="stMetricDelta"][aria-label*="-"] {{
        color: {ERROR} !important;
    }}
    
    /* === INPUTS Y FORMULARIOS === */
    
    /* Todos los inputs con fondo blanco y borde sutil */
    .stTextInput input,
    .stSelectbox select,
    .stNumberInput input,
    .stTextArea textarea {{
        background-color: {BG_WHITE} !important;
        color: {TEXT_PRIMARY} !important;
        border: 1px solid {BORDER_MEDIUM} !important;
        border-radius: 6px !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
        padding: 10px 12px !important;
    }}
    
    .stTextInput input:focus,
    .stSelectbox select:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {{
        border-color: {PRIMARY_BLUE} !important;
        box-shadow: 0 0 0 2px rgba(0, 54, 150, 0.1) !important;
    }}
    
    /* Labels de inputs */
    .stTextInput label,
    .stSelectbox label,
    .stNumberInput label,
    .stTextArea label {{
        color: {TEXT_PRIMARY} !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        margin-bottom: 6px !important;
    }}
    
    /* === SELECTBOXES (FIX PARA CUADROS NEGROS) === */
    
    .stSelectbox > div > div {{
        background-color: {BG_WHITE} !important;
        color: {TEXT_PRIMARY} !important;
        border: 1px solid {BORDER_MEDIUM} !important;
    }}
    
    .stSelectbox select,
    .stSelectbox input {{
        background-color: {BG_WHITE} !important;
        color: {TEXT_PRIMARY} !important;
    }}
    
    /* Dropdown menu del selectbox */
    div[role="listbox"] {{
        background-color: {BG_WHITE} !important;
        border: 1px solid {BORDER_LIGHT} !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }}
    
    div[role="option"] {{
        background-color: {BG_WHITE} !important;
        color: {TEXT_PRIMARY} !important;
        padding: 10px 12px !important;
    }}
    
    div[role="option"]:hover {{
        background-color: {HOVER_BG} !important;
        color: {PRIMARY_BLUE} !important;
    }}
    
    /* === BOTONES === */
    
    .stButton > button {{
        background-color: {PRIMARY_BLUE} !important;
        color: {TEXT_ON_DARK} !important;
        border: 2px solid transparent !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(0, 54, 150, 0.15) !important;
    }}
    
    .stButton > button:hover {{
        background-color: {ACCENT_YELLOW} !important;
        color: {PRIMARY_BLUE_DARK} !important;
        border-color: {ACCENT_YELLOW} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 184, 28, 0.3) !important;
    }}
    
    .stButton > button:active {{
        transform: translateY(0) !important;
    }}
    
    .stButton > button:focus {{
        outline: 3px solid {ACCENT_YELLOW};
        outline-offset: 2px;
    }}
    
    /* === TABLAS === */
    
    .dataframe {{
        background-color: {BG_WHITE} !important;
        border: 1px solid {BORDER_LIGHT} !important;
    }}
    
    .dataframe th {{
        background-color: {BG_LIGHT_GRAY} !important;
        color: {TEXT_PRIMARY} !important;
        font-weight: 600 !important;
        border-bottom: 2px solid {BORDER_MEDIUM} !important;
    }}
    
    .dataframe td {{
        color: {TEXT_PRIMARY} !important;
        border-bottom: 1px solid {BORDER_LIGHT} !important;
    }}
    
    .dataframe tr:hover {{
        background-color: {HOVER_BG} !important;
    }}
    
    /* === GRÁFICAS === */
    
    /* Fondo blanco para todas las gráficas */
    .js-plotly-plot,
    .plot-container {{
        background-color: {BG_WHITE} !important;
    }}
    
    /* === MENSAJES Y ALERTAS === */
    
    .stAlert {{
        background-color: {BG_LIGHT_GRAY} !important;
        border-left: 4px solid {PRIMARY_BLUE} !important;
        color: {TEXT_PRIMARY} !important;
    }}
    
    .stSuccess {{
        background-color: #E8F5E9 !important;
        border-left-color: {SUCCESS} !important;
    }}
    
    .stError {{
        background-color: #FFEBEE !important;
        border-left-color: {ERROR} !important;
    }}
    
    .stWarning {{
        background-color: #FFF3E0 !important;
        border-left-color: {ACCENT_YELLOW} !important;
    }}
    
    .stInfo {{
        background-color: #E3F2FD !important;
        border-left-color: {PRIMARY_BLUE} !important;
    }}
    
    /* === EXPANSORES === */
    
    .streamlit-expanderHeader {{
        background-color: {BG_LIGHT_GRAY} !important;
        color: {TEXT_PRIMARY} !important;
        border: 1px solid {BORDER_LIGHT} !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }}
    
    .streamlit-expanderHeader:hover {{
        background-color: {HOVER_BG} !important;
    }}
    
    .streamlit-expanderContent {{
        background-color: {BG_WHITE} !important;
        border: 1px solid {BORDER_LIGHT} !important;
        border-top: none !important;
    }}
    
    /* === DIVIDERS === */
    
    hr {{
        border-color: {BORDER_LIGHT} !important;
        margin: 20px 0 !important;
    }}
    
    /* === TOOLTIPS === */
    
    .stTooltipIcon {{
        color: {TEXT_SECONDARY} !important;
    }}
    
    /* === RESPONSIVIDAD === */
    
    @media (max-width: 768px) {{
        div[data-testid="stMetricValue"] {{
            font-size: 1.8rem !important;
        }}
        
        .stButton > button {{
            padding: 10px 20px !important;
            font-size: 14px !important;
        }}
    }}
    
    /* === ACCESIBILIDAD === */
    
    /* Motion reducido para usuarios con sensibilidad */
    @media (prefers-reduced-motion: reduce) {{
        * {{
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }}
    }}
    
    /* Focus visible para navegación por teclado */
    *:focus-visible {{
        outline: 3px solid {ACCENT_YELLOW} !important;
        outline-offset: 2px !important;
    }}
    
    /* === LIMPIEZA FINAL === */
    
    /* Eliminar fondos oscuros accidentales */
    div[class*="css-"] {{
        background-color: transparent !important;
    }}
    
    /* Asegurar que no haya sombras negras pesadas */
    * {{
        box-shadow: none !important;
    }}
    
    /* Re-aplicar sombras sutiles solo donde se necesitan */
    .stButton > button,
    div[role="listbox"],
    .stAlert {{
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    }}
    
    </style>
    """

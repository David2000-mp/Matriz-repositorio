# -*- coding: utf-8 -*-
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


def inject_layout_compact_css(hide_streamlit_header: bool = False):
    """Inyecta ajustes de layout y conserva barra superior fija.

    Args:
        hide_streamlit_header: Si True, oculta header/toolbar nativo.
    """
    header_rules = """
    /* Oculta visualmente el header, pero preserva controles de sidebar */
    header[data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
        min-height: 0 !important;
        height: 0 !important;
    }

    div[data-testid="stToolbar"] { display: none !important; }
    div[data-testid="stDecoration"] { display: none !important; }

    /* Mantener visible el toggle del sidebar en ambos estados */
    button[data-testid="stExpandSidebarButton"],
    div[data-testid="stSidebarCollapseButton"] button,
    button[data-testid="stBaseButton-headerNoPadding"] {
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        z-index: 100002 !important;
        color: #FFFFFF !important;
        background: rgba(255, 255, 255, 0.18) !important;
        border: 1px solid rgba(255, 255, 255, 0.55) !important;
        border-radius: 8px !important;
    }

    /* Evita que el sidebar quede desplazado/oculto por estados colapsados previos */
    section[data-testid="stSidebar"] {
        margin-left: 0 !important;
        transform: translateX(0) !important;
        visibility: visible !important;
        z-index: 100001 !important;
    }

    section[data-testid="stSidebar"] > div {
        visibility: visible !important;
    }

    button[data-testid="stExpandSidebarButton"] {
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
    }
    """ if hide_streamlit_header else """
    /* Barra superior fija azul institucional - RECTANGULAR */
    header[data-testid="stHeader"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
        height: 70px !important;
        z-index: 99996 !important;
        background: linear-gradient(135deg, #002366 0%, #001840 100%) !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15) !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
    }

    div[data-testid="stToolbar"] {
        top: 8px !important;
        right: 12px !important;
        z-index: 99998 !important;
    }

    /* Sidebar encima de la barra superior */
    section[data-testid="stSidebar"] {
        z-index: 99999 !important;
        top: 0 !important;
    }

    section[data-testid="stSidebar"] > div {
        margin-top: 0 !important;
    }
    """

    st.markdown(
        f"""
        <style>
        .main .block-container {{
            padding-top: 4.2rem !important;
            margin-top: 0 !important;
        }}

        section[data-testid="stMain"] > div {{
            padding-top: 0 !important;
            margin-top: 0 !important;
        }}

        {header_rules}
        </style>
        """,
        unsafe_allow_html=True,
    )


def scroll_to_top_on_nav_change(nav_state_key: str = "page_selection", tracker_key: str = "_scroll_nav_prev"):
    """Hace scroll al inicio cuando cambia la navegación principal."""
    current = st.session_state.get(nav_state_key, "")
    previous = st.session_state.get(tracker_key)

    changed = previous is None or current != previous
    st.session_state[tracker_key] = current

    if changed:
        st.html(
            """
            <script>
            const moveTop = () => {
              window.scrollTo({ top: 0, left: 0, behavior: "instant" });
              const main = parent.document.querySelector('section[data-testid="stMain"]');
              if (main) main.scrollTop = 0;
            };
            moveTop();
            setTimeout(moveTop, 40);
            setTimeout(moveTop, 120);
            </script>
            """,
            unsafe_allow_javascript=True,
        )


def inject_clipboard_shortcut_guard():
    """Evita que Ctrl/Cmd+C/V/X propaguen a atajos globales de la app."""
    st.html(
        """
        <script>
        (() => {
            const installGuard = (doc) => {
                if (!doc || doc.__champiClipboardGuardInstalled) return;
                doc.__champiClipboardGuardInstalled = true;

                doc.addEventListener(
                    "keydown",
                    (event) => {
                        const key = (event.key || "").toLowerCase();
                        const isClipboardShortcut = (event.ctrlKey || event.metaKey) && ["c", "v", "x"].includes(key);
                        if (!isClipboardShortcut) return;

                        // Bloqueamos la propagación para no activar shortcuts globales de Streamlit.
                        event.stopPropagation();
                    },
                    true
                );
            };

            installGuard(document);
            try {
                installGuard(parent.document);
            } catch (_) {}
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def inject_custom_css():
    # Selector ultra específico para forzar estilos de glass-box
    st.markdown(
        """
        <style>
        section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] .glass-box {
            background: rgba(0, 64, 133, 0.22) !important;
            border-radius: 32px !important;
            padding: 2rem 2rem !important;
            backdrop-filter: blur(10px) !important;
            text-align: center !important;
            font-family: 'Inter', 'Segoe UI', sans-serif !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
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
    # Selector ultra específico para forzar estilos de glassbox hero
    st.markdown(
        """
        <style>
        section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] p.hero-title {
            color: #fff !important;
            font-size: 3.2rem !important;
            font-family: 'Futura', 'Segoe UI', sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: 1px !important;
            text-align: center !important;
            margin-bottom: .1rem !important;
            text-shadow: 0 3px 20px rgba(0,0,0,0.18) !important;
        }
        section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] p.hero-subtitle {
            color: #FFFFFF !important;
            font-size: 1.3rem !important;
            font-family: 'Futura', 'Segoe UI', sans-serif !important;
            font-weight: 600 !important;
            margin-bottom: -10 !important;
            text-align: center !important;
            text-shadow: 0 1px 8px rgba(0,0,0,0.12) !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    from utils.global_styles import get_global_institutional_css
    from utils.mobile_styles import get_mobile_css

    # Inyectar estilos base globales
    st.markdown(get_global_institutional_css(), unsafe_allow_html=True)

    # Inyectar estilos móviles responsive
    st.markdown(get_mobile_css(), unsafe_allow_html=True)

    # Inyectar estilos personalizados para glassbox y hero
    st.markdown(
        """
        <style>
        .glass-box {
            background: rgba(255,255,255,0.22);
            border-radius: 32px;
            padding: 2rem 2rem;
            box-shadow: 0 12px 40px rgba(0,0,0,0.18);
            backdrop-filter: blur(50px);
            text-align: center;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }
        .hero-title {
            color: #FFFFFF;
            font-size: 10rem;      /* Más grande y protagonista */
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-weight:2500;
            letter-spacing: 3px;
            margin-bottom: 1.2rem;
            text-shadow: 0 2px 16px rgba(0,0,0,0.18);
        }
        .hero-subtitle {
            color: #FFB81C;         /* Amarillo institucional para destacar */
            font-size: 1.7rem;      /* Más grande */
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-weight: 600;
            margin-bottom: 0;
            text-shadow: 0 1px 8px rgba(0,0,0,0.12);
        }
        /* Forzar color blanco en p.hero-title y p.hero-subtitle dentro de stMarkdownContainer */
        div[data-testid='stMarkdownContainer'] p.hero-title,
        div[data-testid='stMarkdownContainer'] p.hero-subtitle {
            color: #fff !important;
        }
        div[data-testid="stMarkdownContainer"] .hero-title,
        div[data-testid="stMarkdownContainer"] .hero-subtitle {
            color: #fff !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("""
        <style>

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
            color: var(--text-placeholder) !important;
            opacity: 0.85 !important;
        }

        /* ========================================
           DATAFRAME / DATA EDITOR - TONOS AMIGABLES
        ======================================== */
        [data-testid="stDataFrame"] {
            background: #F7FAFF !important;
            border: 1px solid #DCE8F6 !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 8px rgba(36, 87, 138, 0.08) !important;
            overflow: hidden !important;
        }

        [data-testid="stDataFrame"] .stDataFrameGlideDataEditor,
        [data-testid="stDataFrame"] [class*="gdg-"] {
            --gdg-bg-cell: #FDFEFF;
            --gdg-bg-cell-medium: #F4F8FF;
            --gdg-bg-header: #E8F1FF;
            --gdg-bg-header-has-focus: #DCEBFF;
            --gdg-bg-icon-header: #2E5F8A;
            --gdg-fg-icon-header: #FFFFFF;
            --gdg-text-dark: #22364A;
            --gdg-text-medium: #36506A;
            --gdg-border-color: #D4E3F5;
            --gdg-horizontal-border-color: #E5EEF9;
            --gdg-accent-color: #2F79C2;
            --gdg-accent-fg: #FFFFFF;
            --gdg-link-color: #2F79C2;
        }

        [data-testid="stDataFrame"] .dvn-underlay,
        [data-testid="stDataFrame"] canvas[data-testid="data-grid-canvas"] {
            background: #FDFEFF !important;
        }

        [data-testid="stDataFrame"] [role="columnheader"] {
            background: #E8F1FF !important;
            color: #1E4C75 !important;
            font-weight: 700 !important;
        }

        [data-testid="stDataFrame"] [role="gridcell"] {
            color: #24394D !important;
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

        /* Botón colapsar sidebar: mayor visibilidad y color blanco */
        div[data-testid="stSidebarCollapseButton"] button,
        button[data-testid="stBaseButton-headerNoPadding"] {
            color: #FFFFFF !important;
            background: rgba(255, 255, 255, 0.18) !important;
            border: 1px solid rgba(255, 255, 255, 0.45) !important;
            border-radius: 8px !important;
            min-width: 36px !important;
            min-height: 36px !important;
        }

        div[data-testid="stSidebarCollapsedControl"] {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            position: fixed !important;
            top: 10px !important;
            left: 10px !important;
            z-index: 100003 !important;
        }

        button[data-testid="stExpandSidebarButton"] {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            visibility: visible !important;
            opacity: 1 !important;
            color: #FFFFFF !important;
            background: rgba(255, 255, 255, 0.18) !important;
            border: 1px solid rgba(255, 255, 255, 0.55) !important;
            border-radius: 8px !important;
            min-width: 36px !important;
            min-height: 36px !important;
            z-index: 100004 !important;
        }

        div[data-testid="stSidebarCollapseButton"] button:hover,
        button[data-testid="stBaseButton-headerNoPadding"]:hover {
            background: rgba(255, 255, 255, 0.30) !important;
            border-color: rgba(255, 255, 255, 0.72) !important;
        }

        div[data-testid="stSidebarCollapseButton"] button:focus-visible,
        button[data-testid="stBaseButton-headerNoPadding"]:focus-visible {
            outline: 2px solid #FFFFFF !important;
            outline-offset: 2px !important;
        }

        div[data-testid="stSidebarCollapseButton"] button span,
        div[data-testid="stSidebarCollapseButton"] button [data-testid="stIconMaterial"],
        button[data-testid="stExpandSidebarButton"] span,
        button[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
        button[data-testid="stBaseButton-headerNoPadding"] span,
        button[data-testid="stBaseButton-headerNoPadding"] [data-testid="stIconMaterial"] {
            color: #FFFFFF !important;
            fill: #FFFFFF !important;
            opacity: 1 !important;
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

        /* Ajuste de layout: eliminar gap horizontal dinámico de Streamlit */
        [data-testid="stHorizontalBlock"] {
            gap: 0 !important;
            column-gap: 0 !important;
            row-gap: 0 !important;
        }

        div[class*="st-emotion-cache-"][data-testid="stHorizontalBlock"] {
            gap: 0 !important;
            column-gap: 0 !important;
            row-gap: 0 !important;
        }

        [data-testid="stVerticalBlock"] {
            gap: 0 !important;
            row-gap: 0 !important;
            column-gap: 0 !important;
        }

        div[class*="st-emotion-cache-"][data-testid="stVerticalBlock"] {
            gap: 0 !important;
            row-gap: 0 !important;
            column-gap: 0 !important;
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
        
        /* Texto azul en botones secondary (EXCEPTO Download Buttons) */
        button[kind="secondary"]:not(.stDownloadButton button):not(div[data-testid="stDownloadButton"] button) *,
        [data-testid="stBaseButton-secondary"]:not(.stDownloadButton button):not(div[data-testid="stDownloadButton"] button) *,
        button[kind="secondary"]:not(.stDownloadButton button):not(div[data-testid="stDownloadButton"] button) p,
        button[kind="secondary"]:not(.stDownloadButton button):not(div[data-testid="stDownloadButton"] button) span {
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
           MÁXIMA ESPECIFICIDAD para sobrescribir secondary
        ======================================== */
        .stDownloadButton button,
        .stDownloadButton button[kind="secondary"],
        .stDownloadButton button[data-testid="stBaseButton-secondary"],
        div[data-testid="stDownloadButton"] button,
        div[data-testid="stDownloadButton"] button[kind="secondary"],
        div.stDownloadButton button[kind="secondary"] {
            background-color: var(--primary-color) !important;
            color: var(--button-text) !important;
            border: 2px solid var(--primary-color) !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
        }
        
        /* Forzar texto blanco en TODOS los elementos de botones de descarga */
        .stDownloadButton button *,
        .stDownloadButton button p,
        .stDownloadButton button span,
        .stDownloadButton button div,
        .stDownloadButton button[kind="secondary"] *,
        .stDownloadButton button[kind="secondary"] p,
        .stDownloadButton button[kind="secondary"] span,
        .stDownloadButton button[kind="secondary"] div,
        div[data-testid="stDownloadButton"] button *,
        div[data-testid="stDownloadButton"] button p,
        div[data-testid="stDownloadButton"] button span,
        div[data-testid="stDownloadButton"] button div,
        div[data-testid="stDownloadButton"] button[kind="secondary"] *,
        div[data-testid="stDownloadButton"] button[kind="secondary"] p,
        div.stDownloadButton button[kind="secondary"] *,
        div.stDownloadButton button[kind="secondary"] p {
            color: var(--button-text) !important;
        }
        
        /* Específicamente el contenedor de Markdown */
        .stDownloadButton button div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stDownloadButton"] button div[data-testid="stMarkdownContainer"] p,
        div.stDownloadButton button[kind="secondary"] div[data-testid="stMarkdownContainer"] p {
            color: var(--button-text) !important;
        }
        
        .stDownloadButton button:hover,
        .stDownloadButton button[kind="secondary"]:hover,
        div[data-testid="stDownloadButton"] button:hover,
        div[data-testid="stDownloadButton"] button[kind="secondary"]:hover {
            background-color: var(--accent-color) !important;
            color: var(--text-color) !important;
            border-color: var(--accent-color) !important;
        }
        
        /* Texto oscuro en hover con máxima especificidad */
        .stDownloadButton button:hover *,
        .stDownloadButton button:hover p,
        .stDownloadButton button:hover span,
        .stDownloadButton button[kind="secondary"]:hover *,
        .stDownloadButton button[kind="secondary"]:hover p,
        div[data-testid="stDownloadButton"] button:hover *,
        div[data-testid="stDownloadButton"] button:hover p,
        div[data-testid="stDownloadButton"] button[kind="secondary"]:hover *,
        div[data-testid="stDownloadButton"] button[kind="secondary"]:hover p {
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

    # ========================================
    # ESTILOS PARA CALCULADORA DE ENGAGEMENT
    # ========================================
    st.markdown("""
        <style>
        /* Tarjetas de publicación/video en la calculadora */
        .engagement-post-card {
            background: #F2F4F7;
            border: 2px solid #DEE2E6;
            border-radius: 10px;
            padding: 16px;
            transition: all 0.3s ease;
            margin-bottom: 12px;
        }

        .engagement-post-card:hover {
            border-color: #003696;
            box-shadow: 0 4px 12px rgba(0, 54, 150, 0.15);
        }

        .engagement-post-number {
            font-weight: bold;
            color: #003696;
            margin-bottom: 12px;
            font-size: 14px;
        }

        /* Cajas de resultados con animación de entrada */
        .engagement-result-container {
            animation: slideInUp 0.4s ease;
        }

        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Cajas de información (benchmark, recomendación) */
        .engagement-info-box {
            background: #F2F4F7;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #003696;
            margin-top: 10px;
        }

        .engagement-info-box.success {
            border-left-color: #0A7D35;
        }

        .engagement-info-box.warning {
            border-left-color: #CC7000;
        }

        .engagement-info-box.danger {
            border-left-color: #B42318;
        }

        /* Valores de métricas grandes */
        .engagement-metric-value {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }

        /* Labels de métricas */
        .engagement-metric-label {
            color: #495057;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-weight: 600;
        }

        /* Descripción de métricas */
        .engagement-metric-description {
            color: #495057;
            font-size: 14px;
            line-height: 1.5;
        }

        /* Botones de calculadora */
        .engagement-btn {
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .engagement-btn-primary {
            background: linear-gradient(135deg, #003696 0%, #002566 100%);
            color: white;
        }

        .engagement-btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 54, 150, 0.3);
        }

        .engagement-btn-secondary {
            background: #E8EEF5;
            color: #003696;
            border: 2px solid #003696;
        }

        .engagement-btn-secondary:hover {
            background: #003696;
            color: white;
        }

        /* Estados de colores para engagement */
        .engagement-status-good {
            color: #0A7D35;
            font-weight: 600;
        }

        .engagement-status-warning {
            color: #CC7000;
            font-weight: 600;
        }

        .engagement-status-poor {
            color: #B42318;
            font-weight: 600;
        }

        /* Grid responsivo para publicaciones */
        .engagement-posts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px;
        }

        @media (max-width: 768px) {
            .engagement-posts-grid {
                grid-template-columns: 1fr;
            }

            .engagement-metric-value {
                font-size: 24px;
            }

            .engagement-info-box {
                font-size: 13px;
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
            'text_placeholder': '#A8A8A8',
            
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
           TOASTS Y NOTIFICACIONES
        ======================================== */
        .stToast {{
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-color) !important;
        }}
        
        .stToast,
        .stToast *,
        .stToast p,
        .stToast span,
        .stToast [data-testid="stMarkdownContainer"],
        .stToast [data-testid="stMarkdownContainer"] *,
        .stToast [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] {{
            color: var(--text-color) !important;
            font-weight: 500 !important;
        }}
        
        div[role="alert"][data-testid="stToast"] {{
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-color) !important;
        }}
        
        div[role="alert"][data-testid="stToast"] * {{
            color: var(--text-color) !important;
        }}
        
        [role="alert"] {{
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-color) !important;
        }}
        
        [role="alert"] * {{
            color: var(--text-color) !important;
        }}
        
        [role="alert"] p,
        [role="alert"] span {{
            color: var(--text-color) !important;
            font-weight: 500 !important;
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
            "color": "#000000"
        },
        "title": {
            "font": {"size": 18, "color": "#000000", "family": "Inter"},
            "x": 0.5,
            "xanchor": "center"
        },
        "xaxis": {
            "title": {"font": {"size": 14, "color": "#000000"}},
            "tickfont": {"size": 12, "color": "#000000"},
            "gridcolor": "rgba(0, 0, 0, 0.08)"
        },
        "yaxis": {
            "title": {"font": {"size": 14, "color": "#000000"}},
            "tickfont": {"size": 12, "color": "#000000"},
            "gridcolor": "rgba(0, 0, 0, 0.08)"
        },
        "legend": {
            "font": {"size": 13, "color": "#000000"},
            "bgcolor": "rgba(255, 255, 255, 0.9)",
            "bordercolor": "rgba(0, 0, 0, 0.1)",
            "borderwidth": 1
        },
        "plot_bgcolor": "#FFFFFF",
        "paper_bgcolor": "#FFFFFF",
        "margin": {"l": 50, "r": 30, "t": 60, "b": 50},
        "hoverlabel": {
            "bgcolor": "#FFFFFF",
            "font": {"size": 13, "color": "#000000"},
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
            "color": "#000000"
        },
        "title": {
            "font": {"size": 18, "color": "#000000", "family": "Inter"},
            "x": 0.5,
            "xanchor": "center"
        },
        "xaxis": {
            "title": {"font": {"size": 14, "color": "#000000"}},
            "tickfont": {"size": 12, "color": "#000000"},
            "gridcolor": "rgba(0, 0, 0, 0.08)"
        },
        "yaxis": {
            "title": {"font": {"size": 14, "color": "#000000"}},
            "tickfont": {"size": 12, "color": "#000000"},
            "gridcolor": "rgba(0, 0, 0, 0.08)"
        },
        "legend": {
            "font": {"size": 13, "color": "#000000"},
            "bgcolor": "rgba(255, 255, 255, 0.9)",
            "bordercolor": "rgba(0, 0, 0, 0.1)",
            "borderwidth": 1
        },
        "plot_bgcolor": "#FFFFFF",
        "paper_bgcolor": "#FFFFFF",
        "margin": {"l": 50, "r": 30, "t": 60, "b": 50},
        "hoverlabel": {
            "bgcolor": "#FFFFFF",
            "font": {"size": 13, "color": "#000000"},
            "bordercolor": "#003696"
        }
    }


# ===========================
# CONFIGURACI�N PLOTLY GLOBAL
# ===========================

# Configuración optimizada para gráficos Plotly (rendimiento en la nube)
PLOTLY_CONFIG = {
    "displayModeBar": True,   # Mostrar barra de herramientas para mejor interactividad
    "responsive": True,       # Responsive
    "displaylogo": False,     # Ocultar logo Plotly
    "modeBarButtonsToRemove": [
        "pan2d", "select2d", "lasso2d", "autoScale2d", "resetScale2d",
        "zoomIn2d", "zoomOut2d"
    ],  # Remover solo botones problemáticos, mantener zoom2d y toImage
    "staticPlot": False,      # Mantener interactividad
}

PLOTLY_LAYOUT_DEFAULTS = {
    "font": {"size": 10, "color": "#000000"},
    "margin": {"l": 20, "r": 20, "t": 40, "b": 20},
    "showlegend": True,
    "legend": {"orientation": "h", "y": -0.2},
    "paper_bgcolor": "white",
    "plot_bgcolor": "white",
    "xaxis": {"color": "#000000", "gridcolor": "#E0E0E0"},
    "yaxis": {"color": "#000000", "gridcolor": "#E0E0E0"},
    "hoverlabel": {"bgcolor": "#FFFFFF", "font": {"color": "#000000"}, "bordercolor": "#003696"},
}

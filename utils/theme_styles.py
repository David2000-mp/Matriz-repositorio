"""Sistema visual único de CHAMPILEAKS.

La landing conserva sus estilos de escena en ``views/landing.py``. Este módulo
solo define el shell de Streamlit y componentes compartidos; todos sus
selectores tipográficos quedan fuera de los Material Symbols.
"""

from __future__ import annotations

import streamlit as st


CHAMPI_THEME = {
    "primary": "#003696",
    "primary_interactive": "#1677FF",
    "secondary": "#002566",
    "accent": "#FFB81C",
    "bg": "#FFFFFF",
    "card": "#F2F4F7",
    "sidebar": "#003696",
    "text": "#212529",
    "text_secondary": "#495057",
    "text_on_dark": "#FFFFFF",
    "caption": "#6C757D",
    "border": "#DEE2E6",
    "success": "#0A7D35",
    "danger": "#B42318",
    "warning": "#CC7000",
    "info": "#0756C9",
    "facebook": "#1877F2",
    "instagram": "#C13584",
    "tiktok": "#111111",
    "twitter": "#1A8CD8",
    "linkedin": "#0A66C2",
    "youtube": "#FF0000",
}

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

COLOR_MAP = {
    "Facebook": CHAMPI_THEME["facebook"],
    "Instagram": CHAMPI_THEME["instagram"],
    "TikTok": CHAMPI_THEME["tiktok"],
    "Twitter": CHAMPI_THEME["twitter"],
    "Twitter/X": CHAMPI_THEME["twitter"],
    "X": CHAMPI_THEME["twitter"],
    "LinkedIn": CHAMPI_THEME["linkedin"],
    "YouTube": CHAMPI_THEME["youtube"],
}

PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "toImageButtonOptions": {"format": "png", "scale": 2},
}

PLOTLY_LAYOUT_DEFAULTS = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, Segoe UI, sans-serif", "color": COLOR_TEXT},
    "margin": {"l": 36, "r": 24, "t": 48, "b": 36},
    "hoverlabel": {
        "bgcolor": "#FFFFFF",
        "bordercolor": COLOR_PRIMARY,
        "font": {"color": COLOR_TEXT, "family": "Inter, Segoe UI, sans-serif"},
    },
}


def get_theme_css() -> str:
    """CSS compartido, acotado al shell y a componentes de Streamlit."""
    return """
    <style>
    :root {
        --champi-primary: #003696;
        --champi-primary-interactive: #1677FF;
        --champi-accent: #FFB81C;
        --champi-surface: #FFFFFF;
        --champi-surface-muted: #F2F4F7;
        --champi-text: #212529;
        --champi-text-muted: #495057;
        --champi-border: #DEE2E6;
        --champi-sidebar-text: #FFFFFF;
    }

    section[data-testid="stMain"] {
        background: var(--champi-surface);
        color: var(--champi-text);
    }

    section[data-testid="stMain"] :is(p, label, li, h1, h2, h3, h4, h5, h6),
    section[data-testid="stMain"] span:not([data-testid="stIconMaterial"]) {
        font-family: Inter, "Segoe UI", sans-serif;
    }

    section[data-testid="stMain"] :is(p, label, li) {
        color: var(--champi-text);
    }

    section[data-testid="stMain"] :is(h1, h2, h3) {
        color: var(--champi-primary);
    }

    /* Sidebar nativo: selectores explícitos, sin universales. */
    section[data-testid="stSidebar"] {
        background: #003696;
        color: var(--champi-sidebar-text);
    }

    [data-testid="stSidebarHeader"] {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 0.5rem !important;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        min-height: 76px !important;
    }

    [data-testid="stSidebarHeader"]
        > div:not([data-testid="stSidebarCollapseButton"]) {
        flex: 1 1 auto !important;
        min-width: 0 !important;
        height: auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    [data-testid="stSidebarCollapseButton"] {
        position: relative !important;
        z-index: 2 !important;
        flex: 0 0 2.75rem !important;
        width: 2.75rem !important;
        min-width: 2.75rem !important;
        height: 2.75rem !important;
        margin-left: auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    [data-testid="stSidebarCollapseButton"] button {
        width: 2.75rem !important;
        min-width: 2.75rem !important;
        height: 2.75rem !important;
        padding: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    [data-testid="stLogo"] img,
    [data-testid="stSidebarLogo"],
    [data-testid="stSidebarHeader"] img {
        /* Activo recortado sin margen transparente: se muestra completo. */
        height: 48px !important;
        min-height: 0 !important;
        max-height: 48px !important;
        width: auto !important;
        max-width: 100% !important;
        flex: 0 0 auto !important;
        object-fit: contain !important;
    }

    /* Streamlit aplica colores internos sobre los PageLink. Esta regla se
       limita al nav nativo y gana la cascada en todos sus nodos hijos. */
    [data-testid="stSidebarNav"] * {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebarNav"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        stroke: currentColor !important;
    }

    section[data-testid="stSidebar"] :is(h1, h2, h3, p, label, a),
    section[data-testid="stSidebarNav"] a,
    section[data-testid="stSidebarNav"] a span:not([data-testid="stIconMaterial"]),
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a span:not([data-testid="stIconMaterial"]) {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebarNav"] a,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
        display: flex;
        align-items: center;
        gap: 0.625rem;
        min-height: 2.5rem;
        border-radius: 0.625rem;
        line-height: 1.25;
        text-decoration: none;
        transform: translateX(0);
        transition:
            transform 180ms cubic-bezier(0.2, 0.8, 0.2, 1),
            background-color 180ms ease,
            box-shadow 180ms ease;
        will-change: transform;
    }

    section[data-testid="stSidebarNav"] a:not([aria-current="page"]):hover,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a:not([aria-current="page"]):hover {
        background: rgba(255, 255, 255, 0.09) !important;
        box-shadow: 0 4px 14px rgba(0, 24, 64, 0.18);
        transform: translateX(4px);
    }

    section[data-testid="stSidebarNav"] a:active,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a:active {
        transform: translateX(2px) scale(0.99);
    }

    section[data-testid="stSidebarNav"] a[aria-current="page"],
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
    section[data-testid="stSidebarNav"] [data-testid="stPageLink"]:has(a[aria-current="page"]) {
        background: rgba(255, 255, 255, 0.10) !important;
        box-shadow: inset 3px 0 0 #FFB81C;
    }

    section[data-testid="stSidebarNav"] a[aria-current="page"] span,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] span {
        color: #FFFFFF !important;
        font-weight: 650;
    }

    section[data-testid="stSidebar"] [data-testid="stIconMaterial"],
    section[data-testid="stSidebarNav"] [data-testid="stIconMaterial"] {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined" !important;
        font-weight: normal !important;
        font-style: normal !important;
        font-size: 1.25rem !important;
        transform: scale(1);
        transform-origin: center;
        transition: transform 180ms cubic-bezier(0.2, 0.8, 0.2, 1);
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    section[data-testid="stSidebarNav"] a:hover [data-testid="stIconMaterial"],
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover [data-testid="stIconMaterial"] {
        transform: scale(1.08);
    }

    section[data-testid="stSidebar"] svg,
    section[data-testid="stSidebarNav"] svg {
        color: #FFFFFF !important;
        fill: currentColor !important;
        stroke: currentColor;
    }

    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] {
        background: #FFFFFF !important;
        color: #002566 !important;
        border-color: rgba(255, 255, 255, 0.65) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] :is(div, span, input, svg) {
        color: #002566 !important;
        fill: currentColor !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] input::placeholder {
        color: #495057 !important;
        opacity: 1;
    }

    section[data-testid="stMain"] :is(input, textarea, [role="combobox"]) {
        background: #FFFFFF;
        color: var(--champi-text);
        border: 1px solid var(--champi-border);
        border-radius: 0.625rem;
    }

    section[data-testid="stMain"] :is(input, textarea, [role="combobox"]):focus-within {
        border-color: var(--champi-primary-interactive);
        box-shadow: 0 0 0 3px rgba(22, 119, 255, 0.15);
    }

    [data-testid="stMetric"],
    [data-testid="stDataFrame"],
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--champi-border);
        border-radius: 0.75rem;
    }

    [data-testid="stMetric"] {
        background: var(--champi-surface-muted);
        padding: 1rem;
    }

    section[data-testid="stMain"] [data-testid="stMetric"],
    section[data-testid="stMain"] [data-testid="stPlotlyChart"],
    section[data-testid="stMain"] div[data-testid="stVerticalBlockBorderWrapper"] {
        transition:
            transform 180ms ease,
            box-shadow 180ms ease,
            border-color 180ms ease;
    }

    section[data-testid="stMain"] [data-testid="stMetric"]:hover,
    section[data-testid="stMain"] div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(22, 119, 255, 0.35);
        box-shadow: 0 10px 28px rgba(0, 54, 150, 0.10);
        transform: translateY(-2px);
    }

    section[data-testid="stMain"] [data-testid="stPlotlyChart"],
    section[data-testid="stMain"] [data-testid="stAlert"] {
        animation: champi-fade-up 240ms ease-out both;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 0.625rem;
        transition: transform 150ms ease, box-shadow 150ms ease;
    }

    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"] {
        background: var(--champi-primary);
        color: #FFFFFF;
        border-color: var(--champi-primary);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: var(--champi-accent);
        transform: translateY(-1px);
    }

    .stButton > button:active,
    .stDownloadButton > button:active {
        box-shadow: none;
        transform: translateY(0) scale(0.98);
    }

    [data-baseweb="tab-list"] {
        gap: 0.25rem;
        border-bottom: 1px solid var(--champi-border);
    }

    [data-baseweb="tab"][aria-selected="true"] {
        color: var(--champi-primary);
        border-bottom-color: var(--champi-accent);
    }

    [data-baseweb="tab"] {
        transition: color 160ms ease, background-color 160ms ease;
    }

    /* Animación suave (Fade & Slide Up) para páginas y pestañas */
    @keyframes fade-slide-in {
        0% { opacity: 0; transform: translateY(12px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    [data-testid="stMainBlock"],
    [data-testid="stTabContent"],
    .stTabs [role="tabpanel"] {
        animation: fade-slide-in 0.4s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }

    [data-testid="stTabs"] button {
        transition: color 0.2s ease, border-color 0.2s ease;
    }

    /* Efecto hover genérico para tarjetas/métricas */
    .metric-card-hover {
        transition: all 0.3s ease;
    }
    .metric-card-hover:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }

    /* El video fijo de la landing no debe heredar un contenedor transformado. */
    [data-testid="stMainBlock"]:has(.hero-bg-video) {
        animation: none;
        transform: none;
    }

    @keyframes champi-fade-up {
        from {
            opacity: 0;
            transform: translateY(6px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /*
     * Capa responsive compartida. Las vistas usan columnas, tablas y grÃ¡ficas
     * nativas; estas reglas conservan su comportamiento sin exigir que cada
     * pantalla implemente una versiÃ³n mÃ³vil independiente.
     */
    @media (max-width: 1024px) {
        section[data-testid="stMain"] [data-testid="stMainBlockContainer"] {
            max-width: 100% !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }

        section[data-testid="stMain"] :is(
            [data-testid="stPlotlyChart"],
            [data-testid="stDataFrame"],
            [data-testid="stDataEditor"],
            [data-testid="stIFrame"]
        ) {
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
        }

        section[data-testid="stMain"] [data-testid="stIFrame"] iframe {
            width: 100% !important;
            max-width: 100% !important;
        }

        section[data-testid="stMain"] [data-testid="stMarkdownContainer"]:has(table) {
            max-width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }

        section[data-testid="stMain"] [data-testid="stMarkdownContainer"] table {
            width: 100%;
            min-width: max-content;
        }
    }

    @media (max-width: 767px) {
        html {
            -webkit-text-size-adjust: 100%;
            -webkit-tap-highlight-color: rgba(0, 54, 150, 0.2) !important;
        }

        [data-testid="stAppViewContainer"],
        section[data-testid="stMain"] {
            width: 100%;
            max-width: 100%;
            overflow-x: clip;
        }

        section[data-testid="stMain"] [data-testid="stMainBlockContainer"] {
            box-sizing: border-box !important;
            width: 100% !important;
            max-width: 100% !important;
            margin-top: 0 !important;
            padding-top: calc(3.75rem + env(safe-area-inset-top)) !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-bottom: calc(1.5rem + env(safe-area-inset-bottom)) !important;
        }

        section[data-testid="stMain"] [data-testid="stMainBlockContainer"]:has(
            .hero-bg-video
        ) {
            margin: 0 !important;
            padding: 0 !important;
        }

        section[data-testid="stMain"] :is(
            [data-testid="stVerticalBlock"],
            [data-testid="stVerticalBlockBorderWrapper"],
            [data-testid="stElementContainer"],
            [data-testid="stLayoutWrapper"],
            [data-testid="stMarkdownContainer"]
        ) {
            box-sizing: border-box !important;
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
        }

        /*
         * st.columns genera stHorizontalBlock > stColumn. Forzar una sola
         * columna evita tarjetas o controles demasiado estrechos.
         */
        section[data-testid="stMain"] [data-testid="stHorizontalBlock"]:has(
            > [data-testid="stColumn"]
        ) {
            flex-direction: column !important;
            flex-wrap: nowrap !important;
            align-items: stretch !important;
            gap: 0.75rem !important;
            width: 100% !important;
        }

        section[data-testid="stMain"] [data-testid="stHorizontalBlock"]
            > [data-testid="stColumn"] {
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            flex: 1 1 100% !important;
        }

        /*
         * La captura anual construye una matriz de 12 meses con etiquetas
         * colapsadas. En mÃ³vil ocultamos su cabecera duplicada y recuperamos
         * la etiqueta completa junto a cada campo para que el apilado conserve
         * el contexto de mes y plataforma.
         */
        section[data-testid="stMain"] [data-testid="stHorizontalBlock"]:has(
            > [data-testid="stColumn"]:nth-child(7)
        ):not(:has([data-testid="stNumberInput"])) {
            display: none !important;
        }

        section[data-testid="stMain"] [data-testid="stHorizontalBlock"]:has(
            > [data-testid="stColumn"]:nth-child(7)
        ) [data-testid="stNumberInput"] :is(label, [data-testid="stWidgetLabel"]) {
            position: static !important;
            display: flex !important;
            visibility: visible !important;
            width: auto !important;
            height: auto !important;
            margin: 0 0 0.25rem !important;
            clip: auto !important;
            white-space: normal !important;
        }

        section[data-testid="stMain"] :is(h1, h2, h3, p, label, span) {
            overflow-wrap: anywhere;
        }

        section[data-testid="stMain"] [data-testid="stHeadingWithActionElements"],
        section[data-testid="stMain"] [data-testid="stHeadingWithActionElements"] > div {
            width: 100% !important;
            justify-content: center !important;
            text-align: center !important;
        }

        section[data-testid="stMain"] h1 {
            font-size: clamp(1.75rem, 8vw, 2.4rem) !important;
            line-height: 1.15 !important;
            width: 100% !important;
            margin-left: auto !important;
            margin-right: auto !important;
            text-align: center !important;
        }

        section[data-testid="stMain"] h2 {
            font-size: clamp(1.5rem, 6.5vw, 2rem) !important;
            line-height: 1.2 !important;
            width: 100% !important;
            margin-left: auto !important;
            margin-right: auto !important;
            text-align: center !important;
        }

        section[data-testid="stMain"] h3 {
            font-size: clamp(1.2rem, 5.5vw, 1.6rem) !important;
            line-height: 1.25 !important;
            width: 100% !important;
            margin-left: auto !important;
            margin-right: auto !important;
            text-align: center !important;
        }

        section[data-testid="stMain"] :is(
            [data-testid="stCaptionContainer"],
            [data-testid="stMetric"],
            [data-testid="stMetricLabel"],
            [data-testid="stMetricValue"],
            [data-testid="stMetricDelta"],
            .kpi-card
        ) {
            text-align: center !important;
        }

        section[data-testid="stMain"] :is(
            [data-testid="stMetricLabel"],
            [data-testid="stMetricDelta"]
        ) {
            justify-content: center !important;
        }

        section[data-testid="stMain"] :is(img, video, canvas, svg) {
            max-width: 100%;
        }

        /*
         * 16px evita el zoom automÃ¡tico de iOS; 44px es el objetivo tÃ¡ctil
         * mÃ­nimo para acciones y controles frecuentes.
         */
        section[data-testid="stMain"] :is(input, textarea, [role="combobox"]) {
            min-width: 0 !important;
            max-width: 100% !important;
            font-size: 16px !important;
        }

        section[data-testid="stMain"] :is(
            .stButton > button,
            .stDownloadButton > button,
            [data-testid="stLinkButton"] a,
            [data-testid="stFormSubmitButton"] button,
            [data-testid="stPopover"] button,
            [data-baseweb="tab"],
            [data-baseweb="select"] > div,
            [data-testid="stExpander"] summary
        ) {
            min-height: 44px !important;
            touch-action: manipulation;
        }

        section[data-testid="stMain"] [data-baseweb="tab-list"] {
            display: flex !important;
            flex-wrap: nowrap !important;
            justify-content: flex-start !important;
            max-width: 100% !important;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            overscroll-behavior-inline: contain;
            scroll-snap-type: inline proximity;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: thin;
        }

        section[data-testid="stMain"] [data-baseweb="tab"] {
            flex: 0 0 auto !important;
            min-width: max-content !important;
            padding-left: 0.875rem !important;
            padding-right: 0.875rem !important;
            white-space: nowrap !important;
            scroll-snap-align: start;
        }

        section[data-testid="stMain"] :is(
            [data-testid="stDataFrame"],
            [data-testid="stDataEditor"],
            [data-testid="stFileUploader"],
            [data-testid="stIFrame"]
        ) {
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch !important;
        }

        section[data-testid="stMain"] [data-testid="stPlotlyChart"] {
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
            overflow: hidden !important;
        }

        section[data-testid="stMain"] [data-testid="stPlotlyChart"] :is(
            .js-plotly-plot,
            .plot-container,
            .svg-container
        ) {
            width: 100% !important;
            max-width: 100% !important;
        }

        section[data-testid="stMain"] [data-testid="stPlotlyChart"] .modebar {
            display: flex !important;
            flex-wrap: wrap;
            justify-content: flex-end;
            max-width: 100%;
        }

        section[data-testid="stMain"] [data-testid="stPlotlyChart"] .modebar-btn {
            min-width: 36px;
            min-height: 36px;
        }

        section[data-testid="stMain"] [data-testid="stMarkdownContainer"]:has(table) {
            width: 100%;
            max-width: 100%;
            overflow-x: auto !important;
            overscroll-behavior-inline: contain;
            -webkit-overflow-scrolling: touch !important;
        }

        section[data-testid="stMain"] [data-testid="stMarkdownContainer"] table {
            display: table !important;
            width: max-content !important;
            min-width: 100% !important;
            font-size: 0.9rem !important;
        }

        section[data-testid="stMain"] [data-testid="stMarkdownContainer"] :is(th, td) {
            padding: 0.5rem !important;
            overflow-wrap: normal;
        }

        section[data-testid="stMain"] :is(
            [data-testid="stMetricValue"],
            .kpi-value
        ) {
            font-size: clamp(1.35rem, 7vw, 2rem) !important;
            line-height: 1.15 !important;
            overflow-wrap: anywhere;
        }

        section[data-testid="stSidebar"] {
            z-index: 100002 !important;
            height: 100dvh !important;
            max-height: 100dvh !important;
            background: #003696 !important;
            box-shadow: none !important;
            padding-bottom: env(safe-area-inset-bottom) !important;
        }

        section[data-testid="stSidebarNav"] a,
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
            min-height: 44px !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            height: 100% !important;
            background: #003696 !important;
            overflow-x: hidden;
            overscroll-behavior: contain;
            -webkit-overflow-scrolling: touch;
        }

        [role="dialog"] {
            width: calc(100vw - 2rem) !important;
            max-width: calc(100vw - 2rem) !important;
            max-height: calc(100dvh - 2rem) !important;
            overflow: auto;
        }

        /* El viewport mÃ³vil cambia al mostrar/ocultar la barra del navegador. */
        .hero-bg-video,
        .hero-overlay {
            width: 100% !important;
            height: 100svh !important;
            min-height: 100svh !important;
        }

        .glass-box {
            max-width: calc(100vw - 2rem) !important;
            touch-action: pan-y !important;
            cursor: default !important;
            animation: none !important;
            transform: none !important;
        }
    }

    @media (max-width: 480px) {
        section[data-testid="stMain"] [data-testid="stMainBlockContainer"] {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }

        section[data-testid="stMain"] h1 {
            font-size: 1.75rem !important;
        }

        section[data-testid="stMain"] h2 {
            font-size: 1.5rem !important;
        }

        section[data-testid="stMain"] :is(
            .stButton > button,
            .stDownloadButton > button,
            [data-testid="stLinkButton"] a,
            [data-testid="stFormSubmitButton"] button
        ) {
            width: 100% !important;
        }

        section[data-testid="stMain"] [data-baseweb="tab"] {
            font-size: 0.875rem !important;
        }
    }

    @media (max-width: 767px) and (orientation: landscape) {
        .hero-bg-video,
        .hero-overlay {
            min-height: 100svh !important;
        }
    }

    @media (hover: none) and (pointer: coarse) {
        section[data-testid="stMain"] :is(
            .stButton > button,
            .stDownloadButton > button,
            [data-testid="stLinkButton"] a,
            [data-testid="stFormSubmitButton"] button
        ),
        section[data-testid="stSidebarNav"] a,
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
            min-height: 48px !important;
        }

        section[data-testid="stMain"] [data-testid="stMetric"]:hover,
        section[data-testid="stMain"] div[data-testid="stVerticalBlockBorderWrapper"]:hover,
        section[data-testid="stSidebarNav"] a:hover,
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            transform: none !important;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        section[data-testid="stMain"] *,
        section[data-testid="stSidebar"] * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """


def inject_custom_css() -> None:
    st.markdown(get_theme_css(), unsafe_allow_html=True)


def inject_layout_compact_css(hide_streamlit_header: bool = False) -> None:
    header_css = """
        /*
         * El botón que restaura el sidebar vive dentro del header nativo.
         * Reducimos la cabecera a una capa transparente, pero no la quitamos
         * del DOM: ocultarla con display:none también hacía inaccesible el
         * botón en escritorio y móvil.
         */
        header[data-testid="stHeader"] {
            display: block !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            overflow: visible !important;
            pointer-events: none !important;
            z-index: 100000 !important;
        }
        /*
         * stExpandSidebarButton es descendiente de stToolbar en Streamlit.
         * La barra debe seguir renderizada aunque sus acciones se oculten.
         */
        header[data-testid="stHeader"] div[data-testid="stToolbar"] {
            display: flex !important;
            height: 0 !important;
            min-height: 0 !important;
            background: transparent !important;
            overflow: visible !important;
            pointer-events: none !important;
        }
        header[data-testid="stHeader"] button:not([data-testid="stExpandSidebarButton"]),
        header[data-testid="stHeader"] [data-testid="stStatusWidget"],
        header[data-testid="stHeader"] [data-testid="stMainMenu"],
        div[data-testid="stDecoration"] {
            display: none !important;
        }
        header[data-testid="stHeader"] div[data-testid="stSidebarCollapsedControl"],
        header[data-testid="stHeader"] button[data-testid="stExpandSidebarButton"] {
            display: flex !important;
            visibility: visible !important;
            pointer-events: auto !important;
        }
        header[data-testid="stHeader"] button[data-testid="stExpandSidebarButton"] {
            position: fixed !important;
            top: calc(env(safe-area-inset-top) + .5rem) !important;
            left: calc(env(safe-area-inset-left) + .5rem) !important;
            width: 2.75rem !important;
            min-width: 2.75rem !important;
            height: 2.75rem !important;
            padding: 0 !important;
            z-index: 100001 !important;
        }
    """ if hide_streamlit_header else """
        header[data-testid="stHeader"] {
            background: linear-gradient(135deg, #002566, #001840);
            box-shadow: 0 2px 12px rgba(0,0,0,.15);
        }
    """
    st.markdown(
        f"""
        <style>
        .main .block-container {{ padding-top: 4.2rem; }}
        {header_css}
        button[data-testid="stExpandSidebarButton"],
        div[data-testid="stSidebarCollapseButton"] button {{
            visibility: visible;
            opacity: 1;
            color: #FFFFFF;
            background: rgba(255,255,255,.18);
            border: 1px solid rgba(255,255,255,.5);
            border-radius: .5rem;
        }}
        button[data-testid="stExpandSidebarButton"]:focus-visible,
        div[data-testid="stSidebarCollapseButton"] button:focus-visible {{
            outline: 3px solid #FFB81C;
            outline-offset: 2px;
        }}
        @media (max-width: 767px) {{
            .main .block-container {{
                padding-top: calc(3.75rem + env(safe-area-inset-top)) !important;
            }}
            button[data-testid="stExpandSidebarButton"],
            div[data-testid="stSidebarCollapseButton"] button {{
                width: 2.75rem !important;
                min-width: 2.75rem !important;
                height: 2.75rem !important;
                min-height: 2.75rem !important;
                touch-action: manipulation;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_clipboard_shortcut_guard() -> None:
    st.html(
        """
        <script>
        (() => {
          const install = (doc) => {
            if (!doc || doc.__champiClipboardGuardInstalled) return;
            doc.__champiClipboardGuardInstalled = true;
            doc.addEventListener("keydown", (event) => {
              const key = (event.key || "").toLowerCase();
              if ((event.ctrlKey || event.metaKey) && ["c", "v", "x"].includes(key)) {
                event.stopPropagation();
              }
            }, true);
          };
          install(document);
          try { install(parent.document); } catch (_) {}
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def scroll_to_top_on_nav_change(
    nav_state_key: str = "page_selection",
    tracker_key: str = "_scroll_nav_prev",
) -> None:
    current = st.session_state.get(nav_state_key, "")
    if st.session_state.get(tracker_key) == current:
        return
    st.session_state[tracker_key] = current
    st.html(
        """
        <script>
        window.scrollTo({top: 0, left: 0, behavior: "instant"});
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def aplicar_estilo_personalizado() -> str:
    """Compatibilidad con demos legacy; el tema activo es institucional claro."""
    inject_custom_css()
    return "Claro"


def configure_plotly_theme() -> None:
    """Registra la plantilla Plotly global sin inyectar CSS."""
    try:
        import plotly.io as pio

        from utils.chart_theme import CHAMPILEAKS_TEMPLATE

        pio.templates["champileaks"] = CHAMPILEAKS_TEMPLATE
        pio.templates.default = "champileaks"
    except Exception:
        return

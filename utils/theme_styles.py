"""Sistema visual único de CHAMPILEAKS.

La landing conserva sus estilos de escena en ``views/landing.py``. Este módulo
solo define el shell de Streamlit y componentes compartidos; todos sus
selectores tipográficos quedan fuera de los Material Symbols.
"""

from __future__ import annotations

import streamlit as st


CHAMPI_THEME = {
    "primary": "#1450D2",
    "primary_interactive": "#1677FF",
    "secondary": "#002566",
    "accent": "#FFB81C",
    "bg": "#FFFFFF",
    "card": "#FFFFFF",
    "sidebar": "#071433",
    "text": "#0B1530",
    "text_secondary": "#55627A",
    "text_on_dark": "#FFFFFF",
    "caption": "#64748B",
    "border": "#DCE3EE",
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
        --champi-primary: #1450D2;
        --champi-primary-strong: #003696;
        --champi-primary-interactive: #1677FF;
        --champi-accent: #FFB81C;
        --champi-ink: #0B1530;
        --champi-ink-2: #071433;
        --champi-surface: #FFFFFF;
        --champi-canvas: #F5F7FB;
        --champi-surface-muted: #EEF2F8;
        --champi-text: #0B1530;
        --champi-text-muted: #55627A;
        --champi-border: #DCE3EE;
        --champi-sidebar-text: #E6ECF8;
        --champi-sidebar-muted: #8A9AC0;
        --champi-success: #0A7D35;
        --champi-danger: #B42318;
        --champi-mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
        --champi-shadow-sm: 0 1px 2px rgba(11, 21, 48, 0.04), 0 1px 3px rgba(11, 21, 48, 0.06);
        --champi-shadow-md: 0 8px 24px rgba(11, 21, 48, 0.08);
    }

    /* ---------- Lienzo principal ---------- */
    section[data-testid="stMain"] {
        background:
            radial-gradient(1200px 400px at 85% -120px, rgba(20, 80, 210, 0.07), transparent 70%),
            var(--champi-canvas);
        color: var(--champi-text);
    }

    /* El header nativo está oculto: no hace falta reservarle 6rem. */
    section[data-testid="stMain"] [data-testid="stMainBlockContainer"] {
        padding-top: 2.25rem;
    }

    section[data-testid="stMain"] :is(p, label, li, h1, h2, h3, h4, h5, h6),
    section[data-testid="stMain"] span:not([data-testid="stIconMaterial"]) {
        font-family: Inter, "Segoe UI", sans-serif;
    }

    section[data-testid="stMain"] :is(p, label, li) {
        color: var(--champi-text);
    }

    section[data-testid="stMain"] :is(h1, h2, h3, h4) {
        color: var(--champi-ink);
        letter-spacing: -0.015em;
    }

    section[data-testid="stMain"] h1 { font-weight: 700; }
    section[data-testid="stMain"] :is(h2, h3) { font-weight: 650; }

    /* Cifras con dígitos tabulares: las columnas numéricas se alinean. */
    section[data-testid="stMain"] :is(
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"],
        [data-testid="stDataFrame"],
        table
    ) {
        font-variant-numeric: tabular-nums;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(20, 80, 210, 0.18) 0%, transparent 220px),
            var(--champi-ink-2);
        color: var(--champi-sidebar-text);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
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
        height: 44px !important;
        min-height: 0 !important;
        max-height: 44px !important;
        width: auto !important;
        max-width: 100% !important;
        flex: 0 0 auto !important;
        object-fit: contain !important;
    }

    [data-testid="stSidebarNav"] * {
        color: var(--champi-sidebar-text) !important;
    }

    [data-testid="stSidebarNav"] svg {
        color: var(--champi-sidebar-text) !important;
    }

    /* Encabezados de grupo del menú: etiqueta técnica en monoespaciada. */
    [data-testid="stNavSectionHeader"],
    [data-testid="stNavSectionHeader"] * {
        font-family: var(--champi-mono) !important;
        font-size: 0.68rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        color: var(--champi-sidebar-muted) !important;
    }

    section[data-testid="stSidebar"] :is(h1, h2, h3, p, label, a),
    section[data-testid="stSidebarNav"] a,
    section[data-testid="stSidebarNav"] a span:not([data-testid="stIconMaterial"]),
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a span:not([data-testid="stIconMaterial"]) {
        color: var(--champi-sidebar-text) !important;
    }

    section[data-testid="stSidebarNav"] a,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
        display: flex;
        align-items: center;
        gap: 0.625rem;
        min-height: 2.35rem;
        border-radius: 0.5rem;
        line-height: 1.25;
        text-decoration: none;
        transition: background-color 160ms ease, box-shadow 160ms ease;
    }

    section[data-testid="stSidebarNav"] a:not([aria-current="page"]):hover,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a:not([aria-current="page"]):hover {
        background: rgba(255, 255, 255, 0.06) !important;
    }

    section[data-testid="stSidebarNav"] a[aria-current="page"],
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
    section[data-testid="stSidebarNav"] [data-testid="stPageLink"]:has(a[aria-current="page"]) {
        background: linear-gradient(90deg, rgba(255, 184, 28, 0.16), rgba(255, 184, 28, 0.02)) !important;
        box-shadow: inset 2px 0 0 var(--champi-accent);
    }

    section[data-testid="stSidebarNav"] a[aria-current="page"] span,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] span {
        color: #FFFFFF !important;
        font-weight: 600;
    }

    section[data-testid="stSidebarNav"] a[aria-current="page"] [data-testid="stIconMaterial"] {
        color: var(--champi-accent) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stIconMaterial"],
    section[data-testid="stSidebarNav"] [data-testid="stIconMaterial"] {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined" !important;
        font-weight: normal !important;
        font-style: normal !important;
        font-size: 1.15rem !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        color: var(--champi-sidebar-muted) !important;
    }

    section[data-testid="stSidebar"] svg,
    section[data-testid="stSidebarNav"] svg {
        color: var(--champi-sidebar-text) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] :is(div, span, input, svg) {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSelectbox"] label p {
        font-family: var(--champi-mono) !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--champi-sidebar-muted) !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background: transparent;
        color: var(--champi-sidebar-text);
        border: 1px solid rgba(255, 255, 255, 0.16);
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: var(--champi-accent);
        color: #FFFFFF;
    }

    /* ---------- Controles del área principal ---------- */
    section[data-testid="stMain"] :is(input, textarea, [role="combobox"]) {
        background: #FFFFFF;
        color: var(--champi-text);
        border-radius: 0.625rem;
    }

    section[data-testid="stMain"] :is(input, textarea, [role="combobox"]):focus-within {
        border-color: var(--champi-primary);
        box-shadow: 0 0 0 3px rgba(20, 80, 210, 0.15);
    }

    /* ---------- Superficies: tarjetas, KPIs y tablas ---------- */
    section[data-testid="stMain"] [data-testid="stExpander"] details {
        background: var(--champi-surface);
        border-color: var(--champi-border);
        border-radius: 0.875rem;
        box-shadow: var(--champi-shadow-sm);
    }

    [data-testid="stMetric"] {
        background: var(--champi-surface);
        border: 1px solid var(--champi-border);
        border-radius: 0.875rem;
        padding: 0.95rem 1.1rem 1rem;
        box-shadow: var(--champi-shadow-sm);
        position: relative;
        overflow: hidden;
    }

    /* Línea de acento superior: firma visual de los KPIs. */
    [data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        inset: 0 0 auto 0;
        height: 2px;
        background: linear-gradient(90deg, var(--champi-primary), var(--champi-primary-interactive) 60%, var(--champi-accent));
        opacity: 0.85;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        font-family: var(--champi-mono) !important;
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--champi-text-muted) !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        font-family: var(--champi-mono) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
        color: var(--champi-ink) !important;
    }

    [data-testid="stMetricDelta"] {
        font-family: var(--champi-mono) !important;
        font-size: 0.78rem !important;
    }

    section[data-testid="stMain"] [data-testid="stDataFrame"] {
        border: 1px solid var(--champi-border);
        border-radius: 0.75rem;
        overflow: hidden;
        background: var(--champi-surface);
    }

    section[data-testid="stMain"] [data-testid="stPlotlyChart"] {
        background: var(--champi-surface);
        border: 1px solid var(--champi-border);
        border-radius: 0.875rem;
        padding: 0.5rem 0.5rem 0.25rem;
        box-shadow: var(--champi-shadow-sm);
        animation: champi-fade-up 240ms ease-out both;
    }

    section[data-testid="stMain"] [data-testid="stAlert"] {
        border-radius: 0.75rem;
        animation: champi-fade-up 240ms ease-out both;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 0.625rem;
        font-weight: 500;
        transition: background-color 150ms ease, border-color 150ms ease, box-shadow 150ms ease;
    }

    section[data-testid="stMain"] .stButton > button:hover,
    section[data-testid="stMain"] .stDownloadButton > button:hover {
        border-color: var(--champi-primary);
        color: var(--champi-primary);
    }

    .stButton > button:active,
    .stDownloadButton > button:active {
        transform: scale(0.98);
    }

    [data-baseweb="tab-list"] {
        gap: 0.25rem;
        border-bottom: 1px solid var(--champi-border);
    }

    [data-baseweb="tab"][aria-selected="true"] {
        color: var(--champi-primary);
    }

    [data-baseweb="tab"] {
        transition: color 160ms ease, background-color 160ms ease;
    }

    @keyframes fade-slide-in {
        0% { opacity: 0; transform: translateY(8px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    [data-testid="stTabContent"],
    .stTabs [role="tabpanel"] {
        animation: fade-slide-in 0.3s cubic-bezier(0.2, 0.8, 0.2, 1) both;
    }

    @keyframes champi-fade-up {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ---------- Componentes propios (components/ui.py) ---------- */
    .cl-header {
        display: flex;
        flex-wrap: wrap;
        align-items: flex-end;
        justify-content: space-between;
        gap: 0.75rem 1.5rem;
        padding: 0.25rem 0 1.1rem;
        margin-bottom: 0.4rem;
        border-bottom: 1px solid var(--champi-border);
    }

    .cl-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-family: var(--champi-mono);
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--champi-primary);
        margin: 0 0 0.35rem;
    }

    .cl-eyebrow::before {
        content: "";
        width: 14px;
        height: 2px;
        background: var(--champi-accent);
        border-radius: 2px;
    }

    section[data-testid="stMain"] h1.cl-title {
        font-size: clamp(1.6rem, 2.4vw, 2.1rem);
        line-height: 1.15;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin: 0;
        padding: 0;
        color: var(--champi-ink);
    }

    /* El ancla automática de Streamlit no aporta en estos encabezados y en
       pantallas estrechas salta a una segunda línea. */
    :is(h1.cl-title, h1.cl-hero-title) [data-testid="stHeaderActionElements"] {
        display: none !important;
    }

    section[data-testid="stMain"] p.cl-subtitle {
        margin: 0.4rem 0 0;
        max-width: 72ch;
        font-size: 0.95rem;
        color: var(--champi-text-muted);
    }

    .cl-chips {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.4rem;
    }

    .cl-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.28rem 0.6rem;
        border: 1px solid var(--champi-border);
        border-radius: 999px;
        background: var(--champi-surface);
        font-family: var(--champi-mono);
        font-size: 0.72rem;
        color: var(--champi-text-muted);
        white-space: nowrap;
    }

    .cl-chip b {
        font-weight: 600;
        color: var(--champi-ink);
    }

    .cl-chip--filter {
        border-color: rgba(20, 80, 210, 0.35);
        background: rgba(20, 80, 210, 0.06);
        color: var(--champi-primary);
    }

    .cl-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--champi-success);
        box-shadow: 0 0 0 0 rgba(10, 125, 53, 0.45);
        animation: cl-pulse 2.4s ease-out infinite;
    }

    .cl-dot--idle {
        background: #94A3B8;
        animation: none;
    }

    @keyframes cl-pulse {
        0% { box-shadow: 0 0 0 0 rgba(10, 125, 53, 0.45); }
        70% { box-shadow: 0 0 0 7px rgba(10, 125, 53, 0); }
        100% { box-shadow: 0 0 0 0 rgba(10, 125, 53, 0); }
    }

    .cl-section-label {
        font-family: var(--champi-mono);
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--champi-text-muted);
        margin: 0 0 0.6rem;
    padding-top: 1.5rem;
    }

    .cl-sidebar-status {
        font-family: var(--champi-mono);
        font-size: 0.68rem;
        line-height: 1.6;
        color: var(--champi-sidebar-muted);
    }

    .cl-sidebar-status b {
        color: var(--champi-sidebar-text);
        font-weight: 500;
    }

    /*
     * Capa responsive compartida. Las vistas usan columnas, tablas y gráficas
     * nativas; estas reglas conservan su comportamiento sin exigir que cada
     * pantalla implemente una versión móvil independiente.
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
            -webkit-tap-highlight-color: rgba(20, 80, 210, 0.2) !important;
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
         * colapsadas. En móvil ocultamos su cabecera duplicada y recuperamos
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

        /* Los KPIs conservan la alineación izquierda: etiqueta, valor y
           variación se leen como una columna. */
        section[data-testid="stMain"] :is(
            [data-testid="stCaptionContainer"],
            .kpi-card
        ) {
            text-align: center !important;
        }

        section[data-testid="stMain"] :is(img, video, canvas, svg) {
            max-width: 100%;
        }

        /*
         * 16px evita el zoom automático de iOS; 44px es el objetivo táctil
         * mínimo para acciones y controles frecuentes.
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
            background: var(--champi-ink-2) !important;
            box-shadow: none !important;
            padding-bottom: env(safe-area-inset-bottom) !important;
        }

        section[data-testid="stSidebarNav"] a,
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
            min-height: 44px !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            height: 100% !important;
            background: var(--champi-ink-2) !important;
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

    }

    @media (max-width: 767px) {
        section[data-testid="stMain"] h1.cl-title {
            text-align: left !important;
            margin: 0 !important;
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
            background: #071433;
            border: 1px solid rgba(255,255,255,.18);
            box-shadow: 0 4px 14px rgba(11,21,48,.18);
            border-radius: .5rem;
        }}
        button[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {{
            color: #FFFFFF !important;
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

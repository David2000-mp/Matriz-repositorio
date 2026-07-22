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
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        min-height: 76px !important;
    }

    [data-testid="stSidebarHeader"] div,
    [data-testid="stLogo"] {
        height: auto !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    [data-testid="stLogo"] img,
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
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] svg,
    section[data-testid="stSidebarNav"] svg {
        color: #FFFFFF !important;
        fill: currentColor !important;
        stroke: currentColor;
    }

    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] {
        background: #FFFFFF;
        color: var(--champi-text);
        border-color: rgba(255, 255, 255, 0.45);
    }

    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] * {
        color: var(--champi-text);
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

    [data-baseweb="tab-list"] {
        gap: 0.25rem;
        border-bottom: 1px solid var(--champi-border);
    }

    [data-baseweb="tab"][aria-selected="true"] {
        color: var(--champi-primary);
        border-bottom-color: var(--champi-accent);
    }

    @media (max-width: 767px) {
        section[data-testid="stSidebar"] { max-width: 88vw; }
        section[data-testid="stMain"] [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap;
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
        header[data-testid="stHeader"] { display: none !important; }
        div[data-testid="stToolbar"], div[data-testid="stDecoration"] { display: none; }
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

"""
Paquete de componentes UI para CHAMPILYTICS.
"""

from .styles import (
    inject_custom_css,
    inject_layout_compact_css,
    inject_clipboard_shortcut_guard,
    scroll_to_top_on_nav_change,
    configure_plotly_theme,
    aplicar_estilo_personalizado,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_BG,
    COLOR_CARD,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
    COLOR_CAPTION,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
    COLOR_INFO,
    COLOR_MAP,
    PLOTLY_CONFIG,
    PLOTLY_LAYOUT_DEFAULTS,
)

from .custom_header import render_custom_header

try:
    from .skeleton_loaders import show_kpi_skeleton, show_chart_skeleton
except ImportError:
    # Skeleton loaders opcional durante desarrollo
    show_kpi_skeleton = None
    show_chart_skeleton = None

__all__ = [
    "inject_custom_css",
    "inject_layout_compact_css",
    "inject_clipboard_shortcut_guard",
    "scroll_to_top_on_nav_change",
    "configure_plotly_theme",
    "aplicar_estilo_personalizado",
    "render_custom_header",
    "show_kpi_skeleton",
    "show_chart_skeleton",
    "COLOR_PRIMARY",
    "COLOR_SECONDARY",
    "COLOR_BG",
    "COLOR_CARD",
    "COLOR_TEXT",
    "COLOR_TEXT_SECONDARY",
    "COLOR_CAPTION",
    "COLOR_SUCCESS",
    "COLOR_WARNING",
    "COLOR_DANGER",
    "COLOR_INFO",
    "COLOR_MAP",
    "PLOTLY_CONFIG",
    "PLOTLY_LAYOUT_DEFAULTS",
]

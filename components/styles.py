"""Capa de compatibilidad del sistema visual.

La implementación canónica vive en :mod:`utils.theme_styles`.
"""

from utils.theme_styles import (  # noqa: F401
    CHAMPI_THEME,
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_BORDER,
    COLOR_CAPTION,
    COLOR_CARD,
    COLOR_DANGER,
    COLOR_INFO,
    COLOR_MAP,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SIDEBAR,
    COLOR_SUCCESS,
    COLOR_TEXT,
    COLOR_TEXT_ON_DARK,
    COLOR_TEXT_SECONDARY,
    COLOR_WARNING,
    PLOTLY_CONFIG,
    PLOTLY_LAYOUT_DEFAULTS,
    aplicar_estilo_personalizado,
    configure_plotly_theme,
    inject_clipboard_shortcut_guard,
    inject_custom_css,
    inject_layout_compact_css,
    scroll_to_top_on_nav_change,
)

__all__ = [name for name in globals() if not name.startswith("_")]

"""Compatibilidad temporal para consumidores del antiguo módulo CSS."""

from utils.theme_styles import get_theme_css


def get_global_institutional_css() -> str:
    return get_theme_css()

"""Compatibilidad temporal: las reglas responsive viven en theme_styles."""


def get_mobile_css() -> str:
    """La respuesta móvil ya forma parte del CSS canónico inyectado."""
    return ""

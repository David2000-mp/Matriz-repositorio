"""
Paquete de utilidades para CHAMPILEAKS.
"""

from .data_manager import (
    conectar_sheets,
    COLEGIOS_MARISTAS,
    save_batch,
    save_comment,
    save_username_editado,
    guardar_datos,
    get_id,
    sync_cuentas_to_sheets,
    load_data,
    load_usernames_editados,
    load_configs,
    get_reverse_lookup,
    load_comments,
    COLS_CUENTAS,
    COLS_METRICAS,
    COLS_CONFIG,
    COLS_COMENTARIOS,
    COLS_USERNAMES_EDITADOS,
    METRICAS_CSV,
    CUENTAS_CSV,
)

from .helpers import (
    get_image_base64,
    load_image,
    get_banner_css,
    simular,
    generar_reporte_html,
)

from . import comment_processor

__all__ = [
    # Data manager
    "conectar_sheets",
    "COLEGIOS_MARISTAS",
    "save_batch",
    "save_comment",
    "save_username_editado",
    "guardar_datos",
    "get_id",
    "sync_cuentas_to_sheets",
    "load_data",
    "load_usernames_editados",
    "load_configs",
    "get_reverse_lookup",
    "load_comments",
    "COLS_CUENTAS",
    "COLS_METRICAS",
    "COLS_CONFIG",
    "COLS_COMENTARIOS",
    "COLS_USERNAMES_EDITADOS",
    "METRICAS_CSV",
    "CUENTAS_CSV",
    # Data loader
    # (removed, now imported from data_manager)
    # Helpers
    "get_image_base64",
    "load_image",
    "get_banner_css",
    "simular",
    "generar_reporte_html",
    "comment_processor",
]

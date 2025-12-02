"""
Paquete de utilidades para CHAMPILYTICS.
"""

from .data_manager import (
    conectar_sheets,
    load_data,
    guardar_datos,
    save_batch,
    get_id,
    reset_db,
    COLEGIOS_MARISTAS,
    COLS_CUENTAS,
    COLS_METRICAS,
)

from .helpers import (
    get_image_base64,
    load_image,
    get_banner_css,
    simular,
    generar_reporte_html,
)

__all__ = [
    # Data manager
    "conectar_sheets",
    "load_data",
    "guardar_datos",
    "save_batch",
    "get_id",
    "reset_db",
    "COLEGIOS_MARISTAS",
    "COLS_CUENTAS",
    "COLS_METRICAS",
    # Helpers
    "get_image_base64",
    "load_image",
    "get_banner_css",
    "simular",
    "generar_reporte_html",
]

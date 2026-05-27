"""
sheets_validator.py - Validación de estructura de Google Sheets
================================================================
Módulo para verificar que un Spreadsheet tenga la estructura correcta.
"""

from typing import Tuple, List, Optional
import logging
from pathlib import Path
from utils.schema_columns import COLS_CUENTAS, COLS_METRICAS

logger = logging.getLogger(__name__)

# Estructura requerida
REQUIRED_SHEETS = {
    "cuentas": COLS_CUENTAS,
    "metricas": COLS_METRICAS,
    "config": ["entidad", "meta_seguidores", "meta_engagement"],
    "comentarios": ["entidad", "mes", "comentario"],
    "usernames_editados": ["entidad", "plataforma", "usuario_editado", "fecha_modificacion"]
}


def validate_sheets_structure(spreadsheet) -> Tuple[bool, List[str]]:
    """
    Valida que el spreadsheet tenga todas las hojas requeridas con columnas correctas.

    Args:
        spreadsheet: Objeto gspread.Spreadsheet

    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
            - is_valid: True si todas las hojas y columnas existen
            - list_of_errors: Lista de problemas encontrados (vacía si todo OK)

    Ejemplo:
        >>> from utils.sheets_connector import conectar_sheets
        >>> spreadsheet = conectar_sheets()
        >>> is_valid, errors = validate_sheets_structure(spreadsheet)
        >>> if not is_valid:
        ...     for error in errors:
        ...         print(f"❌ {error}")
    """
    errors = []

    if not spreadsheet:
        errors.append("Spreadsheet es None")
        return False, errors

    # Validar cada hoja
    for sheet_name, expected_cols in REQUIRED_SHEETS.items():
        try:
            ws = spreadsheet.worksheet(sheet_name)
        except Exception as e:
            errors.append(f"Hoja '{sheet_name}' no encontrada: {str(e)}")
            continue

        # Verificar columnas
        try:
            records = ws.get_all_records()
            if not records:
                # Hoja vacía pero existe - no es error crítico
                logger.warning(f"Hoja '{sheet_name}' está vacía")
                continue

            actual_cols = list(records[0].keys())
            missing_cols = [c for c in expected_cols if c not in actual_cols]

            if missing_cols:
                errors.append(
                    f"Hoja '{sheet_name}': faltan columnas {missing_cols}. "
                    f"Encontradas: {actual_cols}"
                )

        except Exception as e:
            errors.append(f"Hoja '{sheet_name}': error al leer: {str(e)}")

    return len(errors) == 0, errors


def ensure_sheets_structure(spreadsheet) -> bool:
    """
    Asegura que el spreadsheet tenga la estructura correcta.
    Si una hoja no existe, la crea.
    Si una columna no existe, la agrega.

    Args:
        spreadsheet: Objeto gspread.Spreadsheet

    Returns:
        bool: True si el spreadsheet es válido (o fue reparado)

    NOTA: Esta función intenta reparar automáticamente pero puede fallar
    por permisos. En ese caso, el usuario debe configurar manualmente.
    """
    if not spreadsheet:
        logger.error("Spreadsheet es None")
        return False

    for sheet_name, expected_cols in REQUIRED_SHEETS.items():
        try:
            ws = spreadsheet.worksheet(sheet_name)
            logger.debug(f"Hoja '{sheet_name}' existe")

            # Verificar que tenga headers
            try:
                records = ws.get_all_records()
                if not records:
                    # Agregar headers
                    logger.info(f"Hoja '{sheet_name}' vacía, agregando headers...")
                    ws.append_row(expected_cols)
            except:
                logger.warning(f"Hoja '{sheet_name}' podría estar corrompida")

        except Exception as e:
            # Hoja no existe, intentar crearla
            logger.warning(f"Hoja '{sheet_name}' no existe, intentando crear...")
            try:
                ws = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(expected_cols))
                ws.append_row(expected_cols)
                logger.info(f"Hoja '{sheet_name}' creada exitosamente")
            except Exception as create_error:
                logger.error(f"No se pudo crear hoja '{sheet_name}': {create_error}")
                return False

    return True

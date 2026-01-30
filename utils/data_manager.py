"""
Data Manager - Hub Central de Configuración y Wrappers
==================================================
Este módulo es el PUNTO CENTRAL de la aplicación.

Responsabilidades:
  1. COLEGIOS_MARISTAS: Catálogo maestro blindado (17 colegios)
  2. conectar_sheets(): Conexión única a Google Sheets usando st.secrets
  3. Wrappers (lazy imports) a funciones de data_loader y data_saver
  
Flujo unidireccional:
  data_loader.py ←  data_manager.py → data_saver.py
                         ↓
                    app.py / views/
                    
REGLA CRÍTICA: Las importaciones de data_loader y data_saver
están AL FINAL del archivo para evitar bloqueos.
"""

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, Tuple
from utils import catalog as catalog

# ============================================================================
# 1. CATÁLOGO MAESTRO - Blindado, nunca se borra
# ============================================================================

PLATAFORMAS_REQUERIDAS = catalog.PLATAFORMAS_REQUERIDAS
COLEGIOS_MARISTAS = catalog.COLEGIOS_MARISTAS


# ============================================================================
# 2. CONEXIÓN A GOOGLE SHEETS
# ============================================================================

def conectar_sheets():
    """
    Función de conexión a Google Sheets (wrapper).
    Delegada a sheets_connector.py para evitar duplicación.
    
    Returns:
        gspread.Spreadsheet: Objeto de la hoja de cálculo, o None si falla
    """
    from utils.sheets_connector import get_sheets_connection
    return get_sheets_connection()


# ============================================================================
# 3. FUNCIONES DE UTILIDAD
# ============================================================================

def reload_colegios_maristas():
    """
    Función mantenida por compatibilidad.
    El catálogo COLEGIOS_MARISTAS es siempre la versión maestra.
    """
    pass


def get_reverse_lookup() -> Dict[str, Dict[str, str]]:
    """
    Crea un lookup inverso de COLEGIOS_MARISTAS para mapear
    usernames a escuela y plataforma.
    
    Returns:
        Dict con username como clave y {'school': str, 'platform': str} como valor.
    """
    reverse_lookup = {}
    for school, platforms in COLEGIOS_MARISTAS.items():
        for platform, username in platforms.items():
            reverse_lookup[username] = {'school': school, 'platform': platform}
    return reverse_lookup


# ============================================================================
# 4. LAZY IMPORTS - Estos vienen AL FINAL para evitar importación circular
# ============================================================================

# Importar constantes de data_loader (re-exportar)
from utils.data_loader import (
    COLS_CUENTAS,
    COLS_METRICAS,
    COLS_CONFIG,
    COLS_COMENTARIOS,
    COLS_USERNAMES_EDITADOS,
    METRICAS_CSV,
    CUENTAS_CSV,
)

# Importar funciones de carga (data_loader)
from utils.data_loader import (
    load_data,
    load_usernames_editados,
    load_comments,
    load_configs,
)


# ============================================================================
# 5. WRAPPERS A FUNCIONES DE data_saver (LAZY IMPORTS)
# ============================================================================

def get_id(entidad: str, plataforma: str, usuario: str, **kwargs) -> str:
    """
    Wrapper que importa get_id de data_saver.
    Genera un ID único MD5 de 8 caracteres (string puro).
    
    Args:
        entidad: Nombre de institución
        plataforma: Red social
        usuario: Nombre de usuario
    
    Returns:
        str: Hash MD5 de 8 caracteres
    """
    from utils.data_saver import get_id as _get_id
    return _get_id(entidad, plataforma, usuario, **kwargs)


def guardar_datos(nuevo_df: pd.DataFrame, modo: str = "append") -> bool:
    """
    Wrapper que importa guardar_datos de data_saver.
    Guarda métricas en Google Sheets con fallback a CSV.
    Invalida cachés automáticamente.
    
    Args:
        nuevo_df: DataFrame con métricas
        modo: "append" o "overwrite"
    
    Returns:
        bool: True si fue exitoso
    """
    from utils.data_saver import guardar_datos as _guardar_datos
    return _guardar_datos(nuevo_df, modo)


def save_batch(df: pd.DataFrame) -> bool:
    """
    Wrapper que importa save_batch de data_saver.
    Alias conveniente para guardar_datos.
    """
    from utils.data_saver import save_batch as _save_batch
    return _save_batch(df)


def save_comment(entidad: str, mes: str, comentario: str) -> bool:
    """
    Wrapper que importa save_comment de data_saver.
    Guarda comentario contextual.
    """
    from utils.data_saver import save_comment as _save_comment
    return _save_comment(entidad, mes, comentario)


def save_username_editado(entidad: str, plataforma: str, usuario_editado: str) -> bool:
    """
    Wrapper que importa save_username_editado de data_saver.
    Guarda username editado con timestamp.
    """
    from utils.data_saver import save_username_editado as _save_username_editado
    return _save_username_editado(entidad, plataforma, usuario_editado)


def sync_cuentas_to_sheets(df_cuentas: pd.DataFrame) -> bool:
    """
    Wrapper que importa sync_cuentas_to_sheets de data_saver.
    Sincroniza DataFrame de cuentas con Google Sheets.
    """
    from utils.data_saver import sync_cuentas_to_sheets as _sync_cuentas_to_sheets
    return _sync_cuentas_to_sheets(df_cuentas)


def reset_db() -> bool:
    """
    Resetea completamente la base de datos:
    1. Limpia hojas de Google Sheets (metricas, cuentas) preservando encabezados
    2. Borra archivos CSV locales
    3. Invalida todos los cachés
    
    Returns:
        bool: True si fue exitoso, False en caso contrario
    """
    from utils.data_saver import reset_db as _reset_db
    return _reset_db()


def invalidate_caches() -> None:
    """
    Invalida cachés de Streamlit y del DataProvider si está disponible.

    Uso: llamar después de operaciones de escritura (save_batch, save_comment, etc.)
    para garantizar que la UI recargue datos frescos.
    """
    # 1) Intentar limpiar caché de Streamlit
    try:
        st.cache_data.clear()
    except Exception as e:
        logger.warning(f"Error limpiando cache_data: {e}")
        try:
            # versiones antiguas de streamlit
            st.legacy_caching.clear_cache()
        except Exception as e2:
            logger.warning(f"Error limpiando legacy_caching: {e2}")

    # 2) Intentar invalidar caches del data_provider si existe
    try:
        from utils.data_provider import data_provider

        if hasattr(data_provider, "invalidate_cache"):
            try:
                data_provider.invalidate_cache()
            except Exception as e:
                logger.warning(f"Error invalidando cache de data_provider: {e}")
                # fallback manual
                data_provider._data_cache = None
                data_provider._merged_cache = None
    except Exception as e:
        logger.warning(f"No hay provider disponible o fallo al invalidar cache: {e}")
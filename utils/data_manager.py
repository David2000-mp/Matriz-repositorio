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
import hashlib
import os
from google.oauth2.service_account import Credentials
from typing import Dict, Tuple

from utils.account_normalization import build_account_key, normalize_platform_name, normalize_social_user
from utils import catalog as catalog
from utils.logger import get_logger
from utils.data_loader import DATA_DIR

# Logger global para pruebas y producción
logger = get_logger(__name__)

# ============================================================================
# 1. CATÁLOGO MAESTRO - Blindado, nunca se borra
# ============================================================================

PLATAFORMAS_REQUERIDAS = catalog.PLATAFORMAS_REQUERIDAS
COLEGIOS_MARISTAS = {
    school: {platform: user for platform, user in platforms.items() if str(user).strip()}
    for school, platforms in catalog.COLEGIOS_MARISTAS.items()
}


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
    try:
        if "gcp_service_account" not in st.secrets:
            logger.error("No se encontraron credenciales en st.secrets['gcp_service_account']")
            try:
                st.error("No se encontraron credenciales para Google Sheets.")
            except Exception:
                pass
            return None

        creds_info = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        client = gspread.authorize(creds)
        spreadsheet = client.open("BaseDatosMatriz")
        return spreadsheet
    except Exception as e:
        logger.error(f"Error conectando a Google Sheets: {e}")
        try:
            st.error("No se pudo conectar a Google Sheets.")
        except Exception:
            pass
        return None


# ============================================================================
# 3. FUNCIONES DE UTILIDAD
# ============================================================================

def reload_colegios_maristas():
    """
    Función mantenida por compatibilidad.
    El catálogo COLEGIOS_MARISTAS es siempre la versión maestra.
    """
    global COLEGIOS_MARISTAS

    df = pd.DataFrame()

    # Prioridad 1: hoja de cuentas en Google Sheets
    try:
        spreadsheet = conectar_sheets()
        if spreadsheet is not None:
            ws = spreadsheet.worksheet("cuentas")
            records = ws.get_all_records()
            if records:
                df = pd.DataFrame(records)
    except Exception as e:
        logger.warning(f"No se pudo recargar catálogo desde Google Sheets: {e}")

    # Prioridad 2: CSV local como fallback
    if df.empty:
        try:
            df = pd.read_csv(CUENTAS_CSV)
        except Exception as e:
            logger.warning(f"No se pudo recargar catálogo desde CSV local: {e}")

    # Sin datos: limpiar catálogo
    if df.empty:
        COLEGIOS_MARISTAS.clear()
        return COLEGIOS_MARISTAS

    required_cols = {"entidad", "plataforma", "usuario_red"}
    if not required_cols.issubset(set(df.columns)):
        logger.warning("El origen de datos no contiene columnas mínimas para recargar catálogo")
        COLEGIOS_MARISTAS.clear()
        return COLEGIOS_MARISTAS

    df = df.copy()
    for col in ["entidad", "plataforma", "usuario_red"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    new_catalog = {}
    for _, row in df.iterrows():
        entidad = row.get("entidad", "")
        plataforma = row.get("plataforma", "")
        usuario = row.get("usuario_red", "")

        if not entidad or not plataforma:
            continue

        new_catalog.setdefault(entidad, {})[plataforma] = usuario

    COLEGIOS_MARISTAS.clear()
    COLEGIOS_MARISTAS.update(new_catalog)
    return COLEGIOS_MARISTAS


def init_files() -> None:
    """Shim de compatibilidad para tests legacy.

    La versión refactorizada centraliza rutas en data_loader; esta función
    se mantiene para evitar rupturas en pruebas antiguas que la monkeypatchean.
    """
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.warning(f"No se pudo asegurar DATA_DIR en init_files: {e}")


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
    load_data as _load_data,
    load_usernames_editados,
    load_comments,
    load_configs,
)


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Wrapper robusto para cargar cuentas y métricas.

    Comportamiento:
    1. Camino normal: delega a data_loader.
    2. Si falla conexión a Sheets durante pre-check, usa fallback CSV local.
    3. Normaliza columna fecha a datetime cuando exista.
    """
    try:
        # Pre-check explícito para escenarios donde tests monkeypatchean conectar_sheets.
        conn = conectar_sheets()
        if conn is None:
            raise RuntimeError("Sin conexión a Google Sheets")
        df_cuentas, df_metricas = _load_data()
    except Exception as e:
        logger.error(f"Error cargando desde origen principal: {e}")
        try:
            df_cuentas = pd.read_csv(CUENTAS_CSV)
            df_metricas = pd.read_csv(METRICAS_CSV)
        except Exception as csv_error:
            logger.error(f"Error en fallback CSV: {csv_error}")
            df_cuentas = pd.DataFrame(columns=COLS_CUENTAS)
            df_metricas = pd.DataFrame(columns=COLS_METRICAS)

    if "fecha" in df_metricas.columns:
        df_metricas = df_metricas.copy()
        df_metricas["fecha"] = pd.to_datetime(df_metricas["fecha"], errors="coerce")

    return df_cuentas, df_metricas


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
    df_cuentas_cache = kwargs.get("df_cuentas_cache")

    if df_cuentas_cache is None:
        df_cuentas_cache, _ = load_data()

    if isinstance(df_cuentas_cache, pd.DataFrame) and not df_cuentas_cache.empty:
        required_cols = {"id_cuenta", "entidad", "plataforma", "usuario_red"}
        if required_cols.issubset(set(df_cuentas_cache.columns)):
            entidad_key = str(entidad).strip().lower()
            plataforma_key = normalize_platform_name(plataforma).strip().lower()
            usuario_key = normalize_social_user(usuario, plataforma)

            cuentas_norm = df_cuentas_cache.copy()
            cuentas_norm["entidad_key"] = cuentas_norm["entidad"].astype(str).str.strip().str.lower()
            cuentas_norm["plataforma_key"] = cuentas_norm["plataforma"].apply(normalize_platform_name).astype(str).str.strip().str.lower()
            cuentas_norm["usuario_key"] = cuentas_norm["usuario_red"].apply(lambda value: normalize_social_user(value, plataforma))

            match = cuentas_norm[
                (cuentas_norm["entidad_key"] == entidad_key)
                & (cuentas_norm["plataforma_key"] == plataforma_key)
                & (cuentas_norm["usuario_key"] == usuario_key)
            ]
            if not match.empty:
                return str(match.iloc[0]["id_cuenta"])

    base = build_account_key(entidad, plataforma, usuario)
    return hashlib.md5(base.encode("utf-8")).hexdigest()[:8]


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
    try:
        # Si la conexión revienta de forma inesperada, responder False explícitamente.
        conn = conectar_sheets()
        if conn is None:
            return False
    except Exception as e:
        logger.error(f"Error previo de conexión en guardar_datos: {e}")
        return False

    from utils.data_saver import guardar_datos as _guardar_datos
    return _guardar_datos(nuevo_df, modo)


def save_batch(df: pd.DataFrame) -> bool:
    """
    Wrapper que importa save_batch de data_saver.
    Alias conveniente para guardar_datos.
    """
    try:
        # Normalizar entrada (acepta list[dict] o DataFrame)
        incoming = pd.DataFrame(df) if not isinstance(df, pd.DataFrame) else df.copy()
        if incoming.empty:
            return True

        # Normalizar tipos de columnas esperadas
        if "fecha" in incoming.columns:
            incoming["fecha"] = pd.to_datetime(incoming["fecha"], errors="coerce")

        for col in ["seguidores", "alcance", "interacciones", "likes_promedio", "engagement_rate"]:
            if col in incoming.columns:
                incoming[col] = pd.to_numeric(incoming[col], errors="coerce").fillna(0)

        # engagement_rate automático si falta
        if "engagement_rate" not in incoming.columns and {"interacciones", "seguidores"}.issubset(incoming.columns):
            incoming["engagement_rate"] = incoming.apply(
                lambda r: (r["interacciones"] / r["seguidores"] * 100.0) if r.get("seguidores", 0) else 0.0,
                axis=1,
            )

        # Cargar existentes
        _, existing_metricas = load_data()
        if "fecha" in existing_metricas.columns:
            existing_metricas = existing_metricas.copy()
            existing_metricas["fecha"] = pd.to_datetime(existing_metricas["fecha"], errors="coerce")

        # Unir y deduplicar por cuenta+fecha, mantener último
        combined = pd.concat([existing_metricas, incoming], ignore_index=True, sort=False)
        if {"id_cuenta", "fecha"}.issubset(combined.columns):
            combined = combined.sort_values(by=["id_cuenta", "fecha"], kind="stable")
            combined = combined.drop_duplicates(subset=["id_cuenta", "fecha"], keep="last")

        # Persistencia local para compatibilidad de tests y fallback
        try:
            METRICAS_CSV.parent.mkdir(parents=True, exist_ok=True)
            combined.to_csv(METRICAS_CSV, index=False)
        except Exception as e:
            logger.warning(f"No se pudo guardar CSV local de métricas: {e}")

        # Persistencia remota/lógica principal
        try:
            result = guardar_datos(combined)
            if result is False:
                try:
                    st.warning("No se pudo guardar en origen principal; se mantuvo respaldo local CSV.")
                except Exception:
                    pass
            return bool(result)
        except Exception as e:
            logger.warning(f"Error guardando batch en origen principal: {e}")
            try:
                st.warning("No se pudo guardar en origen principal; se mantuvo respaldo local CSV.")
            except Exception:
                pass
            return False
        finally:
            try:
                st.cache_data.clear()
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Error en save_batch: {e}")
        return False


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
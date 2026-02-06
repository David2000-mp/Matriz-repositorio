"""
Data Loader - Funciones de lectura de datos
==================================================
Este módulo SOLO carga datos de Google Sheets y CSV local.
NO importa de data_saver ni data_manager a nivel de módulo.
Los IDs se preservan SIEMPRE como strings (nunca pd.to_numeric).

Flujo unidireccional:
data_loader.py → (imports en data_manager.py al final)
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CUENTAS_CSV = DATA_DIR / "cuentas.csv"
METRICAS_CSV = DATA_DIR / "metricas.csv"

COLS_CUENTAS = ["id_cuenta", "entidad", "plataforma", "usuario_red"]
COLS_METRICAS = ["id_cuenta", "fecha", "seguidores", "alcance", "interacciones", "likes_promedio", "engagement_rate"]
COLS_CONFIG = ["entidad", "meta_seguidores", "meta_engagement"]
COLS_COMENTARIOS = ["entidad", "mes", "comentario"]
COLS_USERNAMES_EDITADOS = ["entidad", "plataforma", "usuario_editado", "fecha_modificacion"]


def _normalize_id_column(df: pd.DataFrame, col: str = "id_cuenta") -> pd.DataFrame:
    """
    Asegura que la columna de ID se trata SIEMPRE como string.
    Previene conversiones a número que corrompan datos.
    """
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    return df


def validate_and_fill_columns(df: pd.DataFrame, expected_cols: list) -> pd.DataFrame:
    """
    Valida y normaliza columnas. Protege IDs como strings.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=expected_cols)
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None
    df = df[expected_cols]
    
    # Normalizar fechas si existen
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    # CRÍTICO: Normalizar IDs como strings (NUNCA números)
    if 'id_cuenta' in df.columns:
        df = _normalize_id_column(df, 'id_cuenta')
    
    return df
def _load_data_impl() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga datos desde Google Sheets con fallback a CSV local.
    Preserve todos los IDs como strings.
    Aplica .fillna('') para prevenir propagación de NaN.
    """
    cuentas_df = pd.DataFrame(columns=COLS_CUENTAS)
    metricas_df = pd.DataFrame(columns=COLS_METRICAS)
    sheets_success = False

    try:
        # Lazy import para evitar circularidad
        from utils.sheets_connector import get_sheets_connection
        spreadsheet = get_sheets_connection()
        
        if spreadsheet:
            # Cargar Cuentas
            try:
                ws_c = spreadsheet.worksheet("cuentas")
                c_data = ws_c.get_all_records()
                if c_data:
                    cuentas_df = pd.DataFrame(c_data).fillna('')  # Limpiar NaN inmediatamente
                    cuentas_df = validate_and_fill_columns(cuentas_df, COLS_CUENTAS)
            except:
                logger.warning("Hoja 'cuentas' no encontrada.")
            
            # Cargar Métricas
            try:
                ws_m = spreadsheet.worksheet("metricas")
                
                # Usar get() crudo para evitar conversiones automáticas problemáticas
                raw_data = ws_m.get()
                if raw_data and len(raw_data) > 1:
                    headers = raw_data[0]
                    data_rows = raw_data[1:]
                    
                    # Procesar filas para asegurar longitud correcta
                    max_cols = len(headers)
                    processed_rows = []
                    for row in data_rows:
                        if len(row) < max_cols:
                            row.extend([''] * (max_cols - len(row)))
                        elif len(row) > max_cols:
                            row = row[:max_cols]
                        processed_rows.append(row)
                    
                    metricas_df = pd.DataFrame(processed_rows, columns=headers).fillna('')
                    metricas_df = validate_and_fill_columns(metricas_df, COLS_METRICAS)
                    
                    logger.info(f"Cargadas {len(metricas_df)} métricas usando método crudo")
                else:
                    # Fallback a get_all_records si get() falla
                    m_data = ws_m.get_all_records()
                    if m_data:
                        metricas_df = pd.DataFrame(m_data).fillna('')
                        metricas_df = validate_and_fill_columns(metricas_df, COLS_METRICAS)
            except:
                logger.warning("Hoja 'metricas' no encontrada.")
            
            sheets_success = True
    except Exception as e:
        logger.warning(f"Error conectando a Sheets: {e}")

    # Fallback a CSV local solo si no hubo éxito con Sheets
    if not sheets_success or (cuentas_df.empty and metricas_df.empty):
        if CUENTAS_CSV.exists():
            try:
                cuentas_df = pd.read_csv(CUENTAS_CSV, dtype={"id_cuenta": str}).fillna('')
                cuentas_df = validate_and_fill_columns(cuentas_df, COLS_CUENTAS)
            except Exception as e:
                logger.warning(f"Error cargando cuentas.csv: {e}")
        
        if METRICAS_CSV.exists():
            try:
                metricas_df = pd.read_csv(METRICAS_CSV, dtype={"id_cuenta": str}).fillna('')
                metricas_df = validate_and_fill_columns(metricas_df, COLS_METRICAS)
            except Exception as e:
                logger.warning(f"Error cargando metricas.csv: {e}")

    return cuentas_df, metricas_df


@st.cache_data(ttl=60)
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga datos cacheados (60 segundos).
    Retorna (cuentas_df, metricas_df) con IDs como strings.
    TTL reducido a 60s para reflejar cambios rápidamente sin sobrecargar Sheets.
    """
    return _load_data_impl()
def load_usernames_editados() -> pd.DataFrame:
    """
    Carga usernames editados desde Google Sheets o retorna DataFrame vacío.
    Aplica .fillna('') para prevenir NaN.
    """
    try:
        from utils.sheets_connector import get_sheets_connection
        ss = get_sheets_connection()
        if ss:
            ws = ss.worksheet("usernames_editados")
            records = ws.get_all_records()
            if records:
                df = pd.DataFrame(records).fillna('')
                return validate_and_fill_columns(df, COLS_USERNAMES_EDITADOS)
        return pd.DataFrame(columns=COLS_USERNAMES_EDITADOS)
    except Exception as e:
        logger.warning(f"Error cargando usernames_editados: {e}")
        return pd.DataFrame(columns=COLS_USERNAMES_EDITADOS)


def load_comments() -> pd.DataFrame:
    """
    Carga comentarios contextuales desde Google Sheets.
    Aplica .fillna('') para prevenir NaN.
    """
    try:
        from utils.sheets_connector import get_sheets_connection
        ss = get_sheets_connection()
        if ss:
            ws = ss.worksheet("comentarios")
            records = ws.get_all_records()
            if records:
                df = pd.DataFrame(records).fillna('')
                return validate_and_fill_columns(df, COLS_COMENTARIOS)
        return pd.DataFrame(columns=COLS_COMENTARIOS)
    except Exception as e:
        logger.warning(f"Error cargando comentarios: {e}")
        return pd.DataFrame(columns=COLS_COMENTARIOS)


def load_configs() -> pd.DataFrame:
    """
    Carga configuraciones de metas desde Google Sheets.
    Aplica .fillna('') para prevenir NaN.
    """
    try:
        from utils.sheets_connector import get_sheets_connection
        ss = get_sheets_connection()
        if ss:
            ws = ss.worksheet("config")
            records = ws.get_all_records()
            if records:
                df = pd.DataFrame(records).fillna('')
                return validate_and_fill_columns(df, COLS_CONFIG)
        return pd.DataFrame(columns=COLS_CONFIG)
    except Exception as e:
        logger.warning(f"Error cargando config: {e}")
        return pd.DataFrame(columns=COLS_CONFIG)
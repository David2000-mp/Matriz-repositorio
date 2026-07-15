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
import hashlib
from pathlib import Path
from typing import Tuple, Optional
import os
from utils.logger import get_logger
from utils.schema_columns import (
    COLS_CUENTAS,
    COLS_METRICAS,
    COLS_BASE_MAESTRA_COLEGIOS,
    COLS_BASE_DEMOGRAFICA_COLEGIOS,
)

logger = get_logger(__name__)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CUENTAS_CSV = DATA_DIR / "cuentas.csv"
METRICAS_CSV = DATA_DIR / "metricas.csv"
SAMPLE_UPLOAD_FULL_CSV = DATA_DIR / "sample_upload_full.csv"

COLS_CONFIG = ["entidad", "meta_seguidores", "meta_engagement"]
COLS_COMENTARIOS = ["entidad", "mes", "comentario"]
COLS_USERNAMES_EDITADOS = ["entidad", "plataforma", "usuario_editado", "fecha_modificacion"]

_DEMOGRAPHIC_ALIASES = {
    "fecha de reporte": "fecha_reporte",
    "fecha_reporte": "fecha_reporte",
    "fecha": "fecha_reporte",
    "colegio": "colegio",
    "plataforma": "plataforma",
    "criterio": "criterio",
    "sexo": "sexo",
    "edad": "edad",
    "ubicacion": "ubicacion",
    "ubicación": "ubicacion",
    "valor": "valor",
}

_MAESTRA_ALIASES = {
    "fecha": "fecha",
    "colegio": "colegio",
    "plataforma": "plataforma",
    "metrica": "metrica",
    "métrica": "metrica",
    "valor": "valor",
}


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


def _rename_columns_with_aliases(df: pd.DataFrame, aliases: dict) -> pd.DataFrame:
    """Renombra columnas usando aliases tolerantes a variaciones de nombre."""
    if df is None or df.empty:
        return df

    rename_map = {}
    for col in df.columns:
        key = str(col).strip().lower()
        if key in aliases:
            rename_map[col] = aliases[key]

    if rename_map:
        df = df.rename(columns=rename_map)
    return df


def _load_sheet_as_dataframe(sheet_name: str) -> pd.DataFrame:
    """Carga una hoja de Google Sheets como DataFrame limpio."""
    try:
        from utils.sheets_connector import get_sheets_connection

        ss = get_sheets_connection()
        if not ss:
            return pd.DataFrame()

        ws = ss.worksheet(sheet_name)
        records = ws.get_all_records()
        if not records:
            return pd.DataFrame()
        return pd.DataFrame(records).fillna("")
    except Exception as e:
        logger.warning(f"Error cargando hoja '{sheet_name}': {e}")
        return pd.DataFrame()


def get_form_schema_hash() -> str:
    """
    Calcula hash del esquema (headers) de 'Respuestas de formulario 3'.
    Se usa como token para invalidar cache cuando cambia la estructura.
    """
    try:
        from utils.sheets_connector import get_sheets_connection

        spreadsheet = get_sheets_connection()
        if not spreadsheet:
            return ""

        ws = spreadsheet.worksheet("Respuestas de formulario 3")
        raw_data = ws.get()
        if not raw_data:
            return ""

        headers = [str(h or "").strip().lower() for h in raw_data[0]]
        schema_signature = "|".join(headers)
        return hashlib.md5(schema_signature.encode("utf-8")).hexdigest()
    except Exception as e:
        logger.warning(f"No se pudo calcular hash de esquema de formulario: {e}")
        return ""


def _load_data_impl(_schema_hash_token: str = "") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga datos desde Google Sheets con la siguiente prioridad:
    1. Formulario "Respuestas de formulario 3" (fuente principal)
    2. Hojas "cuentas" y "metricas" (datos manuales)
    3. CSVs locales (fallback)
    
    Preserve todos los IDs como strings.
    Aplica .fillna('') para prevenir propagación de NaN.
    """
    cuentas_df = pd.DataFrame(columns=COLS_CUENTAS)
    metricas_df = pd.DataFrame(columns=COLS_METRICAS)
    sheets_success = False
    data_origin = "csv"

    try:
        # Lazy import para evitar circularidad
        from utils.sheets_connector import get_sheets_connection
        spreadsheet = get_sheets_connection()
        
        if spreadsheet:
            # PRIORIDAD 1: INTENTAR CARGAR DEL FORMULARIO (fuente principal)
            try:
                from utils.form_response_importer import import_form_responses
                logger.info("Intentando cargar datos del formulario...")
                form_cuentas, form_metricas = import_form_responses(spreadsheet)
                
                if not form_cuentas.empty and not form_metricas.empty:
                    cuentas_df = form_cuentas
                    metricas_df = form_metricas
                    logger.info(f"Importadas {len(cuentas_df)} cuentas y {len(metricas_df)} metricas desde formulario")
                    sheets_success = True
                    st.session_state["data_origin"] = "sheets_form"
                    return cuentas_df, metricas_df  # Usar datos del formulario como fuente principal
            except Exception as e:
                logger.warning(f"No se pudo cargar del formulario: {e}")
            
            # PRIORIDAD 2: CARGAR DE LAS HOJAS MANUALES (si el formulario falla)
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
                    
                    logger.info(f"Cargadas {len(metricas_df)} metricas desde hoja de metricas")
                else:
                    # Fallback a get_all_records si get() falla
                    m_data = ws_m.get_all_records()
                    if m_data:
                        metricas_df = pd.DataFrame(m_data).fillna('')
                        metricas_df = validate_and_fill_columns(metricas_df, COLS_METRICAS)
            except:
                logger.warning("Hoja 'metricas' no encontrada.")
            
            sheets_success = True
            if not cuentas_df.empty or not metricas_df.empty:
                data_origin = "sheets"
    
    except Exception as e:
        logger.warning(f"Error conectando a Sheets: {e}")

    # PRIORIDAD 3: Fallback a CSVs locales
    if not sheets_success or (cuentas_df.empty and metricas_df.empty):
        data_origin = "csv"
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

    # COMBINAR CON DATOS DE MUESTRA (sample_upload_full.csv)
    # IMPORTANTE: desactivado por defecto para evitar contaminar producción.
    # Solo se activa cuando ENABLE_SAMPLE_DATA=true.
    enable_sample_data = os.getenv("ENABLE_SAMPLE_DATA", "false").strip().lower() in {
        "1", "true", "yes", "on"
    }

    if enable_sample_data and SAMPLE_UPLOAD_FULL_CSV.exists():
        try:
            sample_df = pd.read_csv(SAMPLE_UPLOAD_FULL_CSV, dtype={"id_cuenta": str}).fillna('')

            # Si tenemos datos de Sheets, combinarlos con sample
            if not cuentas_df.empty:
                # Crear IDs únicos para sample data para evitar conflictos
                base_id = len(cuentas_df)

                # Agregar prefijo 'sample_' a los IDs de muestra
                sample_df['id_cuenta'] = 'sample_' + (sample_df.index + base_id + 1).astype(str)

                # Combinar cuentas
                cuentas_df = pd.concat([cuentas_df, sample_df[COLS_CUENTAS]], ignore_index=True)
                logger.info(f"Agregadas {len(sample_df)} cuentas de muestra")

            # Para métricas de muestra, combinarlas con las existentes
            if all(col in sample_df.columns for col in COLS_METRICAS):
                sample_metricas = sample_df[COLS_METRICAS].copy()
                sample_metricas['id_cuenta'] = 'sample_' + (sample_metricas.index + base_id + 1).astype(str)

                if metricas_df.empty:
                    metricas_df = sample_metricas
                else:
                    metricas_df = pd.concat([metricas_df, sample_metricas], ignore_index=True)

                logger.info(f"Agregadas {len(sample_metricas)} métricas de muestra")

        except Exception as e:
            logger.warning(f"Error cargando sample_upload_full.csv: {e}")
    elif SAMPLE_UPLOAD_FULL_CSV.exists():
        logger.debug("Datos de muestra deshabilitados (ENABLE_SAMPLE_DATA=false)")

    st.session_state["data_origin"] = data_origin

    return cuentas_df, metricas_df


@st.cache_data(ttl=300)
def load_data(schema_hash: str = "") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga datos cacheados (5 minutos).
    Retorna (cuentas_df, metricas_df) con IDs como strings.
    La frescura se controla con invalidación explícita al guardar o refrescar.
    """
    return _load_data_impl(schema_hash)
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


@st.cache_data(ttl=300)
def load_configs() -> pd.DataFrame:
    """
    Carga configuraciones de metas desde Google Sheets.
    Aplica .fillna('') para prevenir NaN.
    Se mantiene en caché para no ralentizar el dashboard en cada navegación.
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


@st.cache_data(ttl=300)
def load_base_maestra_colegios() -> pd.DataFrame:
    """
    Carga y normaliza la hoja Base_Maestra_Colegios.

    Columnas esperadas:
    - fecha, colegio, plataforma, metrica, valor
    """
    df = _load_sheet_as_dataframe("Base_Maestra_Colegios")
    if df.empty:
        return pd.DataFrame(columns=COLS_BASE_MAESTRA_COLEGIOS)

    df = _rename_columns_with_aliases(df, _MAESTRA_ALIASES)
    df.columns = df.columns.str.strip().str.lower()

    for col in COLS_BASE_MAESTRA_COLEGIOS:
        if col not in df.columns:
            df[col] = ""

    df = df[COLS_BASE_MAESTRA_COLEGIOS].copy()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

    for col in ["colegio", "plataforma", "metrica"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    return df


@st.cache_data(ttl=300)
def load_base_demografica_colegios() -> pd.DataFrame:
    """
    Carga y normaliza la hoja Base_Demografica_Colegios.

    Columnas esperadas:
    - fecha_reporte, colegio, plataforma, criterio, sexo, edad, ubicacion, valor
    """
    df = _load_sheet_as_dataframe("Base_Demografica_Colegios")
    if df.empty:
        return pd.DataFrame(columns=COLS_BASE_DEMOGRAFICA_COLEGIOS)

    df = _rename_columns_with_aliases(df, _DEMOGRAPHIC_ALIASES)
    df.columns = df.columns.str.strip().str.lower()

    for col in COLS_BASE_DEMOGRAFICA_COLEGIOS:
        if col not in df.columns:
            df[col] = ""

    df = df[COLS_BASE_DEMOGRAFICA_COLEGIOS].copy()
    df["fecha_reporte"] = pd.to_datetime(df["fecha_reporte"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

    for col in ["colegio", "plataforma", "criterio", "sexo", "edad", "ubicacion"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    return df
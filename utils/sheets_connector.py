"""
Conector para Google Sheets - Cloud Ready.
Maneja conexiones y operaciones con Google Sheets API.
Soporta tanto Streamlit Cloud (st.secrets) como desarrollo local (.env).
"""

import streamlit as st
import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound
from google.oauth2.service_account import Credentials
import os
import json
import re
import hashlib
import unicodedata
import pandas as pd
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from utils.logger import get_logger

# Cargar variables de entorno desde .env (solo en desarrollo local)
load_dotenv()

logger = get_logger(__name__)

# ===========================
# CONFIGURACIÓN DE GOOGLE SHEETS
# ===========================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def _normalize_private_key(pk: str) -> str:
    """
    Normaliza la private_key para manejar tanto \\n literales como saltos de línea reales.
    
    Casos:
    - '\\n' (literal) -> '\n' (newline)
    - '\n' (ya es newline) -> se mantiene
    """
    if not pk:
        return ""
    # Reemplazar literales \\n por saltos de línea reales
    return pk.replace('\\n', '\n')


def _get_service_account_config() -> Optional[Dict[str, Any]]:
    """
    Obtiene credenciales con jerarquía:
    1. st.secrets["gcp_service_account"] (Streamlit Cloud)
    2. GCP_SERVICE_ACCOUNT_JSON env (JSON completo)
    3. Variables individuales GCP_* (desarrollo local)
    """
    
    # ============================================
    # NIVEL 1: Streamlit Cloud - st.secrets
    # ============================================
    try:
        if "gcp_service_account" in st.secrets:
            logger.debug("Credenciales encontradas en st.secrets[gcp_service_account]")
            return dict(st.secrets["gcp_service_account"])
    except Exception as e:
        logger.debug(f"No hay st.secrets disponibles: {e}")
        pass

    # ============================================
    # NIVEL 2: Env JSON completo
    # ============================================
    sa_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    if sa_json:
        try:
            config = json.loads(sa_json)
            logger.debug("Credenciales cargadas desde GCP_SERVICE_ACCOUNT_JSON")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"JSON en GCP_SERVICE_ACCOUNT_JSON inválido: {e}")

    # ============================================
    # NIVEL 3: Variables individuales (Desarrollo local .env)
    # ============================================
    pk = os.getenv("GCP_PRIVATE_KEY")
    client_email = os.getenv("GCP_CLIENT_EMAIL")
    project_id = os.getenv("GCP_PROJECT_ID")
    pk_id = os.getenv("GCP_PRIVATE_KEY_ID")
    # NOTA: Los endpoints OAuth (auth_uri, token_uri, client_x509_cert_url) son estándar de Google.
    # Las credenciales privadas (keys, client_email, etc.) deben almacenarse SIEMPRE en variables de entorno o archivos seguros, nunca hardcodeadas.
    auth_uri = os.getenv("GCP_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
    token_uri = os.getenv("GCP_TOKEN_URI", "https://oauth2.googleapis.com/token")
    auth_provider_cert = os.getenv("GCP_AUTH_PROVIDER_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs")

    if all([pk, client_email, project_id, pk_id]):
        logger.debug("Credenciales cargadas desde variables de entorno individuales")
        return {
            "type": "service_account",
            "private_key": _normalize_private_key(pk),
            "client_email": client_email,
            "project_id": project_id,
            "private_key_id": pk_id,
            "auth_uri": auth_uri,
            "token_uri": token_uri,
            "auth_provider_x509_cert_url": auth_provider_cert,
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}",
            "client_id": "",
            "universe_domain": "googleapis.com"
        }

    logger.warning("No se encontraron credenciales en ningún nivel (st.secrets, JSON env, variables individuales)")
    return None


def _get_google_sheets_id() -> Optional[str]:
    """
    Obtiene el Google Sheets ID con jerarquía:
    1. st.secrets["google_sheets_id"]
    2. st.secrets["general"]["google_sheets_id"]
    3. Env var GOOGLE_SHEETS_ID
    """
    try:
        if "google_sheets_id" in st.secrets:
            sheet_id = st.secrets["google_sheets_id"]
            logger.debug(f"GOOGLE_SHEETS_ID encontrado en st.secrets")
            return sheet_id
    except Exception:
        pass

    try:
        if "general" in st.secrets and "google_sheets_id" in st.secrets["general"]:
            sheet_id = st.secrets["general"]["google_sheets_id"]
            logger.debug(f"GOOGLE_SHEETS_ID encontrado en st.secrets[general]")
            return sheet_id
    except Exception:
        pass

    sheet_id = os.getenv("GOOGLE_SHEETS_ID")
    if sheet_id:
        logger.debug("GOOGLE_SHEETS_ID encontrado en variable de entorno")
        return sheet_id

    logger.error("GOOGLE_SHEETS_ID no configurado en ningún nivel")
    return None



@st.cache_resource(ttl=1800)  # Cache por 30 minutos
def conectar_sheets() -> Optional[gspread.Spreadsheet]:
    """
    Establece conexión con Google Sheets usando credenciales.
    Jerárquica: primero st.secrets (Cloud), luego .env (local).
    Retorna el spreadsheet principal o None si falla.
    """
    try:
        # Obtener credenciales
        creds_dict = _get_service_account_config()
        if not creds_dict:
            logger.error("No se encontraron credenciales de Google Sheets en ningún nivel")
            return None

        # Crear cliente autenticado
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(creds)

        # Obtener ID del spreadsheet
        spreadsheet_id = _get_google_sheets_id()
        if not spreadsheet_id:
            logger.error("GOOGLE_SHEETS_ID no configurado")
            return None

        # Abrir el spreadsheet
        spreadsheet = gc.open_by_key(spreadsheet_id)
        logger.info(f"✓ Conexión exitosa a Google Sheets: {spreadsheet.title}")
        return spreadsheet

    except KeyboardInterrupt:
        logger.error("Conexión interrumpida por el usuario")
        return None
    except Exception as e:
        logger.error(f"Error conectando a Google Sheets: {e}")
        return None


def validate_sheets_connection() -> Dict[str, Any]:
    """
    Valida la conexión a Google Sheets.
    
    Retorna un dict con:
    {
        'success': bool,
        'message': str,
        'error': str | None,
        'config_source': str  # 'st.secrets', 'env_json', 'env_vars', 'none'
    }
    """
    result = {
        'success': False,
        'message': '',
        'error': None,
        'config_source': 'none'
    }

    # Detectar fuente de configuración
    try:
        if "gcp_service_account" in st.secrets:
            result['config_source'] = 'st.secrets'
    except:
        pass

    if result['config_source'] == 'none' and os.getenv("GCP_SERVICE_ACCOUNT_JSON"):
        result['config_source'] = 'env_json'
    
    if result['config_source'] == 'none' and os.getenv("GCP_PRIVATE_KEY"):
        result['config_source'] = 'env_vars'

    # Intentar conexión
    try:
        creds_dict = _get_service_account_config()
        if not creds_dict:
            result['error'] = "No se encontraron credenciales configuradas"
            result['message'] = f"Configura credenciales en Streamlit Cloud (Secrets) o en .env"
            return result

        spreadsheet_id = _get_google_sheets_id()
        if not spreadsheet_id:
            result['error'] = "GOOGLE_SHEETS_ID no está configurado"
            result['message'] = "Agrega GOOGLE_SHEETS_ID a los Secrets"
            return result

        # Intentar conectar
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(creds)
        spreadsheet = gc.open_by_key(spreadsheet_id)

        result['success'] = True
        result['message'] = f"✓ Conectado a: {spreadsheet.title}"
        return result

    except Exception as e:
        result['error'] = str(e)[:150]
        result['message'] = f"Error de conexión: {str(e)[:100]}"
        return result


def display_connection_status():
    """
    Muestra el estado de la conexión en st.sidebar con success o error.
    Llamar al inicio de la app.
    """
    with st.sidebar:
        validation = validate_sheets_connection()
        
        if validation['success']:
            st.success(f"🔗 {validation['message']}", icon="✅")
        else:
            st.error(f"⚠️ {validation['message']}", icon="❌")
            with st.expander("Detalles del error"):
                st.code(f"{validation['error']}\n\nFuente esperada: {validation['config_source']}")
        
        return validation['success']

# ===========================
# ALIAS PARA COMPATIBILIDAD
# ===========================
def get_sheets_connection() -> Optional[gspread.Spreadsheet]:
    """
    Alias para conectar_sheets() para compatibilidad con código existente.
    Establece conexión con Google Sheets.
    """
    return conectar_sheets()


def _normalize_header_label(header: str) -> str:
    """Normaliza headers para comparación tolerante a espacios, tildes y mayúsculas."""
    value = "" if header is None else str(header)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


def _unique_headers(raw_headers: List[str]) -> List[str]:
    """Garantiza nombres de columna únicos preservando orden visual."""
    seen: Dict[str, int] = {}
    unique: List[str] = []

    for raw in raw_headers:
        base = str(raw or "").strip()
        if not base:
            base = "columna_sin_nombre"

        count = seen.get(base, 0) + 1
        seen[base] = count

        unique_name = base if count == 1 else f"{base}__dup_{count}"
        unique.append(unique_name)

    return unique


def _first_non_empty(series: pd.Series):
    """Devuelve el primer valor no vacío de una serie."""
    for value in series:
        text = "" if value is None else str(value).strip()
        if text:
            return value
    return ""


def _consolidate_comment_columns(df: pd.DataFrame, source_cols: List[str]) -> pd.Series:
    """Fusiona columnas de comentarios duplicadas en una sola celda trazable."""
    if not source_cols:
        return pd.Series([""] * len(df), index=df.index)

    def join_non_empty(row: pd.Series) -> str:
        chunks: List[str] = []
        for col in source_cols:
            raw = row.get(col, "")
            text = "" if raw is None else str(raw).strip()
            if text and text not in chunks:
                chunks.append(text)
        return " | ".join(chunks)

    return df.apply(join_non_empty, axis=1)


def _canonical_form_column_groups(columns: List[str]) -> Dict[str, List[str]]:
    """Agrupa columnas de formulario por nombre canónico tolerando variantes."""
    alias_map = {
        "fecha": {
            "fecha del reporte",
            "fecha",
        },
        "entidad": {
            "institucion marista",
            "institucion",
            "entidad",
        },
        "plataforma": {
            "plataforma social",
            "plataforma",
        },
        "usuario_red": {
            "usuario o url de la red",
            "usuario o url",
            "usuario red",
        },
        "seguidores": {
            "seguidores totales: validacion: es un numero > mayor que 0",
            "seguidores totales",
            "seguidores",
        },
        "engagement_rate": {
            "engagement rate (%): validacion: es un numero > entre 0 y 100",
            "engagement rate (%)",
            "engagement rate",
            "engagment rate",
        },
        "alcance": {
            "alcance total",
            "alcance",
        },
        "interacciones": {
            "interacciones totales",
            "interacciones",
        },
        "media_visualizaciones": {
            "media de visualizaciones",
        },
        "tema_mas_visto": {
            "tema mas visto",
        },
        "engagement_contenido_imagenes": {
            "engagment por contenido: imagenes",
            "engagement por contenido: imagenes",
        },
        "engagement_contenido_links": {
            "engagment por contenido: links",
            "engagement por contenido: links",
        },
        "engagement_contenido_videos": {
            "engagment por contenido: videos",
            "engagement por contenido: videos",
        },
        "top_5_publicaciones": {
            "top 5 publicaciones por rendieminto",
            "top 5 publicaciones por rendimiento",
        },
        "engagement_tema_mas_visto": {
            "engagment del tema mas visto",
            "engagement del tema mas visto",
        },
        "publicaciones_por_semana": {
            "publicaciones por semana",
        },
        "tema_principal": {
            "tema principal del contenido del periodo",
        },
        "obs_engagement": {
            "observaciones de engagement del periodo",
        },
        "notas_operacionales": {
            "notas operacionales relevantes",
        },
        "alertas_riesgos": {
            "alertas o riesgos detectados",
        },
        "tuvo_cambios_operacionales": {
            "¿hubo cambios operacionales durante este periodo?",
            "hubo cambios operacionales durante este periodo",
        },
        "publicacion_destacada": {
            "publicacion destacada",
        },
        "comentarios": {
            "comentarios contextuales",
            '"comentarios contextuales"',
            "comentarios contextuales ",
            "comentarios",
        },
    }

    grouped: Dict[str, List[str]] = {key: [] for key in alias_map}

    for col in columns:
        normalized = _normalize_header_label(col)
        for canonical, aliases in alias_map.items():
            if normalized in aliases:
                grouped[canonical].append(col)
                break

    return grouped


def cargar_respuestas_forms() -> pd.DataFrame:
    """
    Carga y sanitiza datos de la hoja 'Respuestas de formulario 3' en Google Sheets.
    
    Returns:
        pd.DataFrame: DataFrame con datos limpios y validados
    """
    try:
        ss = get_sheets_connection()
        if not ss:
            logger.error("No se pudo conectar a Google Sheets")
            return pd.DataFrame()
        
        # Acceder a la hoja 'Respuestas de formulario 3'
        ws = ss.worksheet("Respuestas de formulario 3")
        raw_data = ws.get()

        if not raw_data or len(raw_data) < 2:
            logger.info("La hoja 'Respuestas de formulario 3' está vacía")
            return pd.DataFrame()
        headers = _unique_headers(raw_data[0])
        rows = raw_data[1:]

        max_cols = len(headers)
        normalized_rows = []
        for row in rows:
            row_copy = list(row)
            if len(row_copy) < max_cols:
                row_copy.extend([""] * (max_cols - len(row_copy)))
            elif len(row_copy) > max_cols:
                row_copy = row_copy[:max_cols]
            normalized_rows.append(row_copy)

        df_raw = pd.DataFrame(normalized_rows, columns=headers)

        # Ignorar columna 'Marca temporal' si existe (primera columna A1)
        drop_candidates = [
            col for col in df_raw.columns
            if _normalize_header_label(col).startswith("marca temporal")
        ]
        if drop_candidates:
            df_raw = df_raw.drop(columns=drop_candidates, errors="ignore")

        grouped = _canonical_form_column_groups(list(df_raw.columns))
        df = pd.DataFrame(index=df_raw.index)

        for canonical, source_cols in grouped.items():
            if not source_cols:
                continue

            if canonical == "comentarios":
                consolidated = _consolidate_comment_columns(df_raw, source_cols)
                df["comentarios_consolidados"] = consolidated
                df["comentarios"] = consolidated
                if len(source_cols) > 1:
                    logger.warning(
                        "Se detectaron columnas duplicadas de comentarios: %s. Se consolidaron en comentarios_consolidados.",
                        source_cols,
                    )
                continue

            if len(source_cols) == 1:
                df[canonical] = df_raw[source_cols[0]]
            else:
                df[canonical] = df_raw[source_cols].apply(_first_non_empty, axis=1)
                logger.warning("Columnas duplicadas para %s detectadas: %s", canonical, source_cols)
        
        # Validación de esquema para cache invalidation por hash de columnas
        ordered_schema = "|".join(_normalize_header_label(col) for col in df_raw.columns)
        st.session_state["forms_schema_hash"] = hashlib.md5(ordered_schema.encode("utf-8")).hexdigest()

        # VALIDACIÓN FINAL: Verificar columna crítica 'fecha'
        if 'fecha' not in df.columns:
            st.error(f"Error crítico: No se encuentra la columna 'fecha'. Columnas disponibles: {list(df.columns)}")
            return pd.DataFrame()  # Retorno vacío seguro
        
        # Sanitización y validación
        df = df.fillna('')  # Llenar vacíos con string vacío

        if 'tuvo_cambios_operacionales' in df.columns:
            normalized_changes = (
                df['tuvo_cambios_operacionales']
                .astype(str)
                .str.strip()
                .str.lower()
                .replace({'sí': 'si', 'yes': 'si', 'true': 'si', '1': 'si', 'false': 'no', '0': 'no'})
            )
            df['tuvo_cambios_operacionales'] = normalized_changes.where(
                normalized_changes.isin(['si', 'no']),
                ''
            )
        
        # CONVERSIÓN OBLIGATORIA DE FECHAS
        if 'fecha' in df.columns:
            # Método ultra-seguro: procesar cada fecha individualmente
            def convert_date_safe(date_str):
                if pd.isna(date_str) or date_str == '' or date_str is None:
                    return pd.NaT

                # Convertir a string y limpiar
                date_str = str(date_str).strip()

                # Intentar formatos comunes
                formats_to_try = [
                    '%d/%m/%Y',  # 30/01/2026
                    '%d/%m/%y',  # 30/01/26
                    '%Y-%m-%d',  # 2026-01-30
                    '%Y/%m/%d',  # 2026/01/30
                    '%m/%d/%Y',  # 01/30/2026
                ]

                for fmt in formats_to_try:
                    try:
                        return pd.to_datetime(date_str, format=fmt)
                    except (ValueError, TypeError):
                        continue

                # Último intento sin formato específico
                try:
                    return pd.to_datetime(date_str, errors='coerce')
                except Exception:
                    return pd.NaT

            # Aplicar conversión segura
            df['fecha'] = df['fecha'].apply(convert_date_safe)

            # Verificar si tenemos al menos algunas fechas válidas
            valid_dates = df['fecha'].notna().sum()
            logger.warning(f"Fechas válidas encontradas: {valid_dates} de {len(df)}. Continuando procesamiento...")

            # TEMPORAL: No retornar vacío por fechas inválidas
            # if valid_dates == 0:
            #     logger.error("No se pudo convertir ninguna fecha. Verificar formato de datos.")
            #     return pd.DataFrame()  # Retornar vacío si no hay fechas válidas
        
        # Convertir columnas numéricas de forma robusta
        cols_numericas = [
            'seguidores',
            'alcance',
            'interacciones',
            'media_visualizaciones',
            'engagement_contenido_imagenes',
            'engagement_contenido_links',
            'engagement_contenido_videos',
            'engagement_tema_mas_visto',
            'publicaciones_por_semana',
        ]
        for col in cols_numericas:
            if col in df.columns:
                # Remover separadores de miles y normalizar decimal local
                cleaned = (
                    df[col]
                    .astype(str)
                    .str.replace('%', '', regex=False)
                    .str.replace('\u00a0', '', regex=False)
                    .str.replace(' ', '', regex=False)
                    .str.replace(',', '.', regex=False)
                )
                df[col] = pd.to_numeric(cleaned, errors='coerce').fillna(0)
        
        # Engagement rate especial (tiene %)
        if 'engagement_rate' in df.columns:
            df['engagement_rate'] = pd.to_numeric(df['engagement_rate'].astype(str).str.replace('%', '').str.replace(',', '.').str.strip(), errors='coerce').fillna(0)
        
        # CORRECCIÓN DE ENGAGEMENT RATE: Calcular valores realistas
        if 'engagement_rate' in df.columns and 'seguidores' in df.columns and 'interacciones' in df.columns:
            logger.info("Corrigiendo valores de engagement rate irrealistas...")

            # Función para determinar si un engagement rate es realista
            def is_realistic_engagement(eng_rate):
                return 0 <= eng_rate <= 100  # Máximo 100% engagement

            # Identificar registros con engagement irrealista
            unrealistic_mask = ~df['engagement_rate'].apply(is_realistic_engagement)

            if unrealistic_mask.any():
                logger.warning(f"Encontrados {unrealistic_mask.sum()} registros con engagement irrealista. Recalculando...")

                # Calcular engagement real: (interacciones / seguidores) * 100
                safe_followers = df.loc[unrealistic_mask, 'seguidores'].clip(lower=1)
                df.loc[unrealistic_mask, 'engagement_rate'] = (
                    df.loc[unrealistic_mask, 'interacciones'] / safe_followers * 100
                ).round(2)

                logger.info("Engagement rates corregidos exitosamente")
        
        # Validaciones específicas después de conversión
        if 'seguidores' in df.columns:
            invalid_seguidores = df['seguidores'] <= 0
            if invalid_seguidores.any():
                df.loc[invalid_seguidores, 'error_validacion'] = 'Seguidores Totales debe ser > 0'
        
        if 'engagement_rate' in df.columns:
            # Validación más segura para engagement rate
            invalid_engagement = (df['engagement_rate'] < 0) | (df['engagement_rate'] > 100)
            # Asegurarse de que no haya NaN causando problemas
            invalid_engagement = invalid_engagement.fillna(False)
            if invalid_engagement.any():
                df.loc[invalid_engagement, 'error_validacion'] = 'Engagement Rate debe estar entre 0 y 100'
        
        # Agregar columna de error general si no existe
        if 'error_validacion' not in df.columns:
            df['error_validacion'] = ''

        # Garantizar que Data Editor reciba un índice continuo
        df = df.reset_index(drop=True)
        
        return df
    
    except Exception as e:
        logger.error(f"Error cargando respuestas de forms: {e}")
        return pd.DataFrame()


# Función de testing (comentada para uso en desarrollo)
# def test_data_integrity():
#     print("=== TEST DE INTEGRIDAD DE DATOS ===")
#     df = cargar_respuestas_forms()
#     
#     # Check conexión
#     if df.empty:
#         print("❌ Conexión fallida o hoja vacía")
#         return
#     print("✅ Conexión exitosa")
#     
#     # Check columnas
#     expected_cols = ["marca_temporal", "fecha_reporte", "entidad", "plataforma", "usuario_red", "seguidores", "engagement_rate", "alcance", "interacciones", "comentarios"]
#     missing_cols = [col for col in expected_cols if col not in df.columns]
#     if missing_cols:
#         print(f"❌ Columnas faltantes: {missing_cols}")
#     else:
#         print("✅ Todas las columnas esperadas existen")
#     
#     # Check nulos en campos críticos
#     critical_cols = ["entidad", "fecha_reporte"]
#     for col in critical_cols:
#         nulls = df[col].isnull().sum()
#         if nulls > 0:
#             print(f"⚠️ {nulls} valores nulos en {col}")
#         else:
#             print(f"✅ No hay nulos en {col}")
#     
#     # Primeras 5 filas
#     print("\n=== PRIMERAS 5 FILAS ===")
#     print(df.head().to_string())
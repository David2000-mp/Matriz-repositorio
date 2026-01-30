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
from typing import Optional, Dict, Any
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
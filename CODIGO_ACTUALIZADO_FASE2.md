# 📋 CÓDIGO ACTUALIZADO - Fase 2 Blindaje

## 1️⃣ utils/sheets_connector.py (ACTUALIZADO)

```python
"""
Conector para Google Sheets.
Maneja conexiones y operaciones básicas con Google Sheets API.
ACTUALIZADO: Credenciales OAuth2 completas para compatibilidad total
"""

import streamlit as st
import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound
from google.oauth2.service_account import Credentials
import os
import json
from typing import Optional
from dotenv import load_dotenv
from utils.logger import get_logger

# Cargar variables de entorno desde .env
load_dotenv()

logger = get_logger(__name__)

# ===========================
# CONFIGURACIÓN DE GOOGLE SHEETS
# ===========================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def _get_service_account_config() -> Optional[dict]:
    """Obtiene credenciales desde st.secrets o variables de entorno."""

    # 1) st.secrets
    try:
        if "gcp_service_account" in st.secrets:
            return dict(st.secrets["gcp_service_account"])
    except Exception:
        pass

    # 2) JSON completo en env
    sa_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    if sa_json:
        try:
            return json.loads(sa_json)
        except json.JSONDecodeError as e:
            logger.error(f"JSON en GCP_SERVICE_ACCOUNT_JSON inválido: {e}")

    # 3) Vars individuales (con campos OAuth2 completos)
    pk = os.getenv("GCP_PRIVATE_KEY")
    client_email = os.getenv("GCP_CLIENT_EMAIL")
    project_id = os.getenv("GCP_PROJECT_ID")
    pk_id = os.getenv("GCP_PRIVATE_KEY_ID")
    auth_uri = os.getenv("GCP_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
    token_uri = os.getenv("GCP_TOKEN_URI", "https://oauth2.googleapis.com/token")
    auth_provider_cert = os.getenv("GCP_AUTH_PROVIDER_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs")

    if all([pk, client_email, project_id, pk_id]):
        return {
            "type": "service_account",
            "private_key": pk.replace('\\n', '\n') if pk else "",
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

    return None

@st.cache_resource(ttl=1800)  # Cache por 30 minutos
def conectar_sheets() -> Optional[gspread.Spreadsheet]:
    """
    Establece conexión con Google Sheets usando credenciales.
    Retorna el spreadsheet principal o None si falla.
    """
    try:
        creds_dict = _get_service_account_config()
        if not creds_dict:
            logger.warning("No se encontraron credenciales de Google Sheets")
            return None

        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(creds)

        # ID del spreadsheet (debe estar en secrets o env)
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID") or st.secrets.get("google_sheets_id") or (st.secrets.get("general", {}).get("google_sheets_id") if st.secrets.get("general") else None)
        if not spreadsheet_id:
            logger.error("GOOGLE_SHEETS_ID no configurado")
            return None

        spreadsheet = gc.open_by_key(spreadsheet_id)
        logger.info(f"Conexión exitosa a Google Sheets: {spreadsheet.title}")
        return spreadsheet

    except KeyboardInterrupt:
        logger.error("Conexión interrumpida por el usuario")
        return None
    except Exception as e:
        logger.error(f"Error conectando a Google Sheets: {e}")
        try:
            st.error(f"Error de conexión a Google Sheets: {str(e)[:100]}...")
        except Exception:
            logger.warning("No se pudo mostrar st.error para conectar_sheets")
        return None


def get_sheets_connection() -> Optional[gspread.Spreadsheet]:
    """
    Alias para conectar_sheets() para compatibilidad con nuevo código.
    Establece conexión con Google Sheets.
    """
    return conectar_sheets()
```

## 2️⃣ utils/data_loader.py (CAMBIO CLAVE)

**Línea 127:** Cambiar de `ttl=300` a `ttl=60`

```python
@st.cache_data(ttl=60)  # ← ANTES: ttl=300
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carga datos cacheados (60 segundos).
    Retorna (cuentas_df, metricas_df) con IDs como strings.
    TTL reducido a 60s para reflejar cambios rápidamente sin sobrecargar Sheets.
    """
    return _load_data_impl()
```

## 3️⃣ utils/data_manager.py (CAMBIO CLAVE)

**Línea 121:** Cambiar la función `conectar_sheets()` de 27 líneas a 5 líneas

```python
# ANTES (27 líneas duplicadas):
def conectar_sheets():
    """
    Función única de conexión a Google Sheets.
    Usa st.secrets['gcp_service_account'] como fuente de credenciales.
    """
    try:
        if "gcp_service_account" not in st.secrets:
            st.error("No se encontraron los secrets 'gcp_service_account'")
            return None
        
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[...]
        )
        gc = gspread.authorize(creds)
        name = st.secrets.get("google_sheets_name", "BaseDatosMatriz")
        return gc.open(name)
    except Exception as e:
        st.error(f"Error de conexión a Google Sheets: {e}")
        return None


# DESPUÉS (5 líneas unificadas):
def conectar_sheets():
    """
    Función de conexión a Google Sheets (wrapper).
    Delegada a sheets_connector.py para evitar duplicación.
    """
    from utils.sheets_connector import get_sheets_connection
    return get_sheets_connection()
```

## Cambios Resumidos

| Archivo | Línea | Cambio | Razón |
|---------|-------|--------|-------|
| sheets_connector.py | 32-68 | Agregados campos OAuth2 | Google requiere todas las URLs de autenticación |
| data_loader.py | 127 | ttl=300 → ttl=60 | Reflejar cambios más rápido (1 min vs 5 min) |
| data_manager.py | 121-127 | Delegación a sheets_connector | Eliminar duplicación de código |

## Verificación de Cambios

Ejecutar test:
```bash
python test_connection_final.py
```

Resultado esperado:
```
✅ CONEXIÓN ESTABLECIDA - Todo funciona correctamente
```

## .env Requerido

```bash
GOOGLE_SHEETS_ID=1FXoHqYH3TnesWAvYTWHnZ0LQyfc_E11zpFfL2b0nDGY
GCP_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n
GCP_CLIENT_EMAIL=botmatrizv2@matriz-app-479304.iam.gserviceaccount.com
GCP_PROJECT_ID=matriz-app-479304
GCP_PRIVATE_KEY_ID=e463230e6e16ec4fa86e3c21d178024a8a534102
GCP_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GCP_TOKEN_URI=https://oauth2.googleapis.com/token
GCP_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
```

✅ Todos estos cambios ya están implementados en tu workspace.

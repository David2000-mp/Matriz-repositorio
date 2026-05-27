#!/usr/bin/env python3
"""
Script para verificar y configurar Google Sheets existente.
"""

import streamlit as st
import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound
from google.oauth2.service_account import Credentials
import os
import json
from utils.logger import get_logger
from utils.schema_columns import COLS_CUENTAS, COLS_METRICAS

logger = get_logger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def _get_service_account_config():
    """Obtiene credenciales desde st.secrets o variables de entorno."""
    try:
        if "gcp_service_account" in st.secrets:
            return dict(st.secrets["gcp_service_account"])
    except Exception:
        pass

    sa_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    if sa_json:
        try:
            return json.loads(sa_json)
        except json.JSONDecodeError as e:
            logger.error(f"JSON en GCP_SERVICE_ACCOUNT_JSON inválido: {e}")

    pk = os.getenv("GCP_PRIVATE_KEY")
    client_email = os.getenv("GCP_CLIENT_EMAIL")
    project_id = os.getenv("GCP_PROJECT_ID")
    pk_id = os.getenv("GCP_PRIVATE_KEY_ID")

    if all([pk, client_email, project_id, pk_id]):
        return {
            "type": "service_account",
            "private_key": pk.replace('\\n', '\n'),
            "client_email": client_email,
            "project_id": project_id,
            "private_key_id": pk_id,
        }

    return None

def list_spreadsheets():
    """Lista spreadsheets disponibles."""
    try:
        creds_dict = _get_service_account_config()
        if not creds_dict:
            logger.error("No se encontraron credenciales")
            return []

        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(creds)

        # Listar spreadsheets (solo los que tienen acceso)
        spreadsheets = gc.openall()
        return [(ss.title, ss.id) for ss in spreadsheets]

    except Exception as e:
        logger.error(f"Error listando spreadsheets: {e}")
        return []

def configure_existing_sheets(spreadsheet_id):
    """Configura un spreadsheet existente."""
    try:
        creds_dict = _get_service_account_config()
        if not creds_dict:
            logger.error("No se encontraron credenciales")
            return False

        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(creds)

        # Abrir spreadsheet existente
        spreadsheet = gc.open_by_key(spreadsheet_id)
        logger.info(f"Spreadsheet encontrado: {spreadsheet.title} (ID: {spreadsheet.id})")

        # Verificar/crear hojas necesarias
        sheets_to_check = [
            ("cuentas", COLS_CUENTAS),
            ("metricas", COLS_METRICAS),
            ("config", ["entidad", "meta_seguidores", "meta_engagement"]),
            ("comentarios", ["entidad", "mes", "comentario"]),
            ("usernames_editados", ["entidad", "plataforma", "usuario_editado", "fecha_modificacion"]),
        ]

        for sheet_name, headers in sheets_to_check:
            try:
                # Intentar obtener la hoja
                try:
                    worksheet = spreadsheet.worksheet(sheet_name)
                    print(f"✅ Hoja '{sheet_name}' existe")
                except Exception:
                    # Crear hoja si no existe
                    worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
                    worksheet.update(range_name="A1", values=[headers])
                    print(f"🆕 Hoja '{sheet_name}' creada con headers")
            except Exception as e:
                print(f"⚠️  Error con hoja '{sheet_name}': {e}")

        # Configurar el ID en secrets.toml
        secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")

        try:
            with open(secrets_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Agregar google_sheets_id si no existe
            if 'google_sheets_id' not in content:
                content += f'\n\ngoogle_sheets_id = "{spreadsheet_id}"\n'
            else:
                # Reemplazar el existente
                import re
                content = re.sub(r'google_sheets_id\s*=\s*".*"', f'google_sheets_id = "{spreadsheet_id}"', content)

            with open(secrets_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"ID configurado en secrets.toml: {spreadsheet_id}")
            return True

        except Exception as e:
            logger.error(f"Error configurando secrets.toml: {e}")
            print(f"⚠️  Error configurando secrets.toml: {e}")
            print(f"   Configura manualmente: google_sheets_id = \"{spreadsheet_id}\"")
            return False

    except Exception as e:
        logger.error(f"Error configurando spreadsheet: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando spreadsheets disponibles...")

    spreadsheets = list_spreadsheets()
    if spreadsheets:
        print(f"📄 Spreadsheets encontrados: {len(spreadsheets)}")
        for title, sid in spreadsheets:
            print(f"   - {title} (ID: {sid})")

        # Si hay spreadsheets, usar el primero o pedir selección
        if len(spreadsheets) == 1:
            title, sid = spreadsheets[0]
            print(f"📋 Usando spreadsheet: {title}")
            success = configure_existing_sheets(sid)
            if success:
                print("✅ Configuración completada")
            else:
                print("❌ Error en configuración")
        else:
            print("⚠️  Múltiples spreadsheets encontrados. Especifica cuál usar.")
            for i, (title, sid) in enumerate(spreadsheets):
                print(f"   {i+1}. {title} (ID: {sid})")
    else:
        print("❌ No se encontraron spreadsheets accesibles")
        print("💡 Crea un spreadsheet manualmente en Google Sheets y comparte con:")
        print("   bot-matriz@hybrid-shelter-426922-i8.iam.gserviceaccount.com")
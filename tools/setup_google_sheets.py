#!/usr/bin/env python3
"""
Script para configurar Google Sheets completamente.
Crea un spreadsheet y configura el ID.
"""

import streamlit as st
import gspread
from gspread.exceptions import APIError, SpreadsheetNotFound
from google.oauth2.service_account import Credentials
import os
import json
from utils.logger import get_logger

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

def create_and_configure_sheets():
    """Crea spreadsheet y configura el ID."""
    try:
        creds_dict = _get_service_account_config()
        if not creds_dict:
            logger.error("No se encontraron credenciales")
            return None

        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        gc = gspread.authorize(creds)

        # Crear nuevo spreadsheet
        spreadsheet = gc.create("Matriz de Redes Sociales - Producción")
        logger.info(f"Spreadsheet creado: {spreadsheet.title} (ID: {spreadsheet.id})")

        # Crear hojas necesarias
        sheets_to_create = [
            ("cuentas", ["id_cuenta", "entidad", "plataforma", "usuario_red"]),
            ("metricas", ["id_cuenta", "fecha", "seguidores", "alcance", "interacciones", "likes_promedio", "engagement_rate"]),
            ("config", ["entidad", "meta_seguidores", "meta_engagement"]),
            ("comentarios", ["entidad", "mes", "comentario"]),
            ("usernames_editados", ["entidad", "plataforma", "usuario_editado", "fecha_modificacion"]),
        ]

        for sheet_name, headers in sheets_to_create:
            try:
                # Crear hoja
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
                # Agregar headers
                worksheet.update(range_name="A1", values=[headers])
                logger.info(f"Hoja '{sheet_name}' creada con headers")
            except Exception as e:
                logger.error(f"Error creando hoja '{sheet_name}': {e}")

        # Configurar el ID en secrets.toml
        spreadsheet_id = spreadsheet.id
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

        except Exception as e:
            logger.error(f"Error configurando secrets.toml: {e}")
            print(f"⚠️  Error configurando secrets.toml: {e}")
            print(f"   Configura manualmente: google_sheets_id = \"{spreadsheet_id}\"")

        return spreadsheet_id

    except Exception as e:
        logger.error(f"Error creando spreadsheet: {e}")
        return None

if __name__ == "__main__":
    print("🆕 Creando y configurando Google Sheets...")
    spreadsheet_id = create_and_configure_sheets()
    if spreadsheet_id:
        print(f"✅ Spreadsheet creado y configurado: {spreadsheet_id}")
        print("🔄 Reinicia la aplicación para que tome los cambios")
    else:
        print("❌ Error creando/configurando spreadsheet")
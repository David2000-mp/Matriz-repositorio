"""
Script de prueba para verificar la conexión con Google Sheets
"""

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def test_connection():
    print("🔍 Probando conexión con Google Sheets...")

    try:
        # Scope
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        # Credenciales
        print("📋 Leyendo credenciales desde secrets.toml...")
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

        # Autorizar
        print("🔐 Autorizando cliente...")
        client = gspread.authorize(creds)

        # Abrir hoja
        print("📊 Abriendo hoja 'BaseDatosMatriz'...")
        sheet = client.open("BaseDatosMatriz").sheet1

        # Probar lectura
        print("📖 Leyendo datos...")
        data = sheet.get_all_records()
        print(f"✅ Conexión exitosa! Se encontraron {len(data)} filas.")

        if len(data) > 0:
            print(f"📌 Columnas disponibles: {list(data[0].keys())}")
        else:
            print("⚠️ La hoja está vacía.")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_connection()

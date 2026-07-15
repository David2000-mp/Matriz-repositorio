#!/usr/bin/env python3
"""Test script to verify Google Sheets connection"""

import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
from pathlib import Path

print("=" * 80)
print("🔍 PRUEBA DE CONEXIÓN A GOOGLE SHEETS")
print("=" * 80)

# Verify Sheet ID
if 'google_sheets_id' in st.secrets:
    sheet_id = st.secrets['google_sheets_id']
    print(f"\n📊 Google Sheet ID: {sheet_id}")
else:
    print("❌ No hay google_sheets_id en st.secrets")
    exit(1)

# Verify credentials
if 'gcp_service_account' not in st.secrets:
    print("❌ No hay gcp_service_account en st.secrets")
    exit(1)

try:
    print("\n🔐 Autenticando con Google...")
    creds_info = dict(st.secrets['gcp_service_account'])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    client = gspread.authorize(creds)
    print("✅ Autenticación exitosa")
    
    # Try to open the spreadsheet
    print(f"\n📂 Abriendo Google Sheet...")
    try:
        spreadsheet = client.open_by_key(sheet_id)
        print(f"✅ Google Sheet abierto: '{spreadsheet.title}'")
        
        # List worksheets
        print(f"\n📄 Hojas disponibles:")
        for sheet in spreadsheet.worksheets():
            print(f"   - {sheet.title} (ID: {sheet.id}, {sheet.row_count}x{sheet.col_count})")
        
        # Try to read first sheet
        first_sheet = spreadsheet.sheet1
        print(f"\n📖 Leyendo datos de '{first_sheet.title}'...")
        try:
            data = first_sheet.get_all_values()
            print(f"✅ Datos cargados: {len(data)} filas")
            if data:
                print(f"   Primera fila: {data[0][:5]}...")  # Show first 5 columns
                if len(data) > 1:
                    print(f"   Segunda fila: {data[1][:5]}...")
        except Exception as e:
            print(f"❌ Error al leer datos: {e}")
            
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"❌ No se encontró el Google Sheet ID: {sheet_id}")
        print(f"   Asegúrate de:")
        print(f"   1. Que el ID sea correcto")
        print(f"   2. Que hayas compartido el sheet con: botmatrizv2@matriz-app-479304.iam.gserviceaccount.com")
        print(f"   3. Que le hayas dado acceso de 'Editor'")
    except Exception as e:
        print(f"❌ Error al abrir Google Sheet: {e}")
        
except Exception as e:
    print(f"❌ Error de autenticación: {e}")

print("\n" + "=" * 80)

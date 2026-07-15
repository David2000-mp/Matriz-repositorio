#!/usr/bin/env python3
"""Test script to verify Google Sheets credentials are loaded"""

import streamlit as st
import os
import sys
from pathlib import Path

print("=" * 80)
print("🔍 VERIFICACIÓN DE CREDENCIALES DE GOOGLE SHEETS")
print("=" * 80)

# Check if secrets.toml exists
secrets_path = Path.home() / ".streamlit" / "secrets.toml"
print(f"\n📁 Archivo secrets.toml: {secrets_path}")
print(f"   Existe: {'✅' if secrets_path.exists() else '❌'}")

if secrets_path.exists():
    with open(secrets_path, 'r', encoding='utf-8') as f:
        content = f.read()
        has_gcp = '[gcp_service_account]' in content
        print(f"   Contiene [gcp_service_account]: {'✅' if has_gcp else '❌'}")
        print(f"   Tamaño: {len(content)} bytes")

# Try loading from st.secrets
print("\n🔐 Leyendo desde st.secrets:")
try:
    if 'gcp_service_account' in st.secrets:
        creds = dict(st.secrets['gcp_service_account'])
        print("✅ Credenciales encontradas en st.secrets")
        print(f"   project_id: {creds.get('project_id')}")
        print(f"   client_email: {creds.get('client_email')}")
        print(f"   type: {creds.get('type')}")
        
        # Check key fields
        required_keys = ['project_id', 'private_key', 'client_email', 'client_id']
        for key in required_keys:
            exists = key in creds
            print(f"   {key}: {'✅' if exists else '❌'}")
    else:
        print("❌ No hay [gcp_service_account] en st.secrets")
        print(f"   Claves disponibles: {list(st.secrets.keys())}")
except Exception as e:
    print(f"❌ Error al leer st.secrets: {e}")

# Test connection to Google Sheets
print("\n🔗 Probando conexión a Google Sheets:")
try:
    import gspread
    from google.oauth2.service_account import Credentials
    
    if 'gcp_service_account' in st.secrets:
        creds_info = dict(st.secrets['gcp_service_account'])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        client = gspread.authorize(creds)
        print("✅ Conexión a Google establecida")
        
        # Try to list shared files
        print("   Intentando listar archivos compartidos...")
        try:
            drive = client.auth.client
            print("   ✅ Cliente de Google Drive disponible")
        except Exception as e:
            print(f"   ⚠️ {e}")
    else:
        print("❌ No hay credenciales configuradas")
        
except ImportError as e:
    print(f"❌ Módulos no instalados: {e}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")

print("\n" + "=" * 80)

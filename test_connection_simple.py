#!/usr/bin/env python3
"""
Test de Conexión Rápido - Google Sheets
Verifica que las credenciales y permisos sean correctos.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_connection():
    """Realiza test completo de conexión."""
    
    print("\n" + "="*80)
    print("🔍 TEST DE CONEXIÓN - GOOGLE SHEETS")
    print("="*80 + "\n")
    
    # Step 1: Verificar credenciales
    print("[1/5] Verificando credenciales en .env...")
    sheets_id = os.getenv("GOOGLE_SHEETS_ID")
    if not sheets_id:
        print("❌ GOOGLE_SHEETS_ID vacío")
        return False
    print(f"✅ GOOGLE_SHEETS_ID: {sheets_id[:30]}...")
    
    # Step 2: Verificar privada key
    pk = os.getenv("GCP_PRIVATE_KEY")
    if not pk or "TU_PRIVATE_KEY" in pk:
        print("❌ GCP_PRIVATE_KEY inválida o vacía")
        return False
    if "-----BEGIN PRIVATE KEY-----" not in pk:
        print("❌ GCP_PRIVATE_KEY: Formato inválido (falta BEGIN)")
        return False
    print("✅ GCP_PRIVATE_KEY: Formato válido")
    
    # Step 3: Verificar otros datos
    client_email = os.getenv("GCP_CLIENT_EMAIL")
    project_id = os.getenv("GCP_PROJECT_ID")
    if not all([client_email, project_id]):
        print("❌ Faltan GCP_CLIENT_EMAIL o GCP_PROJECT_ID")
        return False
    print(f"✅ GCP_CLIENT_EMAIL: {client_email}")
    print(f"✅ GCP_PROJECT_ID: {project_id}")
    
    # Step 4: Intentar conexión
    print("\n[2/5] Importando librerías...")
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        print("✅ Librerías importadas correctamente")
    except ImportError as e:
        print(f"❌ Error importando: {e}")
        return False
    
    print("\n[3/5] Creando credenciales...")
    try:
        creds_dict = {
            "type": "service_account",
            "project_id": project_id,
            "private_key": pk,
            "client_email": client_email,
            "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
        }
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        print("✅ Credenciales creadas exitosamente")
    except Exception as e:
        print(f"❌ Error creando credenciales: {e}")
        return False
    
    print("\n[4/5] Autorizando cliente gspread...")
    try:
        gc = gspread.authorize(creds)
        print("✅ Cliente gspread autorizado")
    except Exception as e:
        print(f"❌ Error autorizando gspread: {e}")
        return False
    
    print("\n[5/5] Abriendo spreadsheet...")
    try:
        spreadsheet = gc.open_by_key(sheets_id)
        print(f"✅ Spreadsheet abierto: '{spreadsheet.title}'")
        print(f"   ID: {spreadsheet.id}")
    except Exception as e:
        print(f"❌ Error abriendo spreadsheet: {e}")
        print(f"   Posibles causas:")
        print(f"   - ID incorrecto: {sheets_id}")
        print(f"   - Spreadsheet no compartido con: {client_email}")
        print(f"   - Permisos insuficientes")
        return False
    
    # Step 6: Intentar leer "cuentas"
    print("\n[6/6] Leyendo hoja 'cuentas'...")
    try:
        ws = spreadsheet.worksheet("cuentas")
        records = ws.get_all_records()
        print(f"✅ Hoja 'cuentas' leída exitosamente")
        print(f"   Registros: {len(records)}")
        
        if records:
            first_row = records[0]
            print(f"   Columnas: {list(first_row.keys())}")
            print(f"   Primer registro: {first_row}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error leyendo 'cuentas': {e}")
        print(f"   Posibles causas:")
        print(f"   - Hoja 'cuentas' no existe")
        print(f"   - Hoja está vacía sin encabezados")
        print(f"   - Permiso denegado")
        return False

if __name__ == "__main__":
    print("\n⏳ Iniciando test de conexión...")
    success = test_connection()
    
    print("\n" + "="*80)
    if success:
        print("✅ CONEXIÓN EXITOSA - Todo funciona correctamente")
        print("="*80 + "\n")
        sys.exit(0)
    else:
        print("❌ CONEXIÓN FALLIDA - Revisa los errores arriba")
        print("="*80 + "\n")
        sys.exit(1)

#!/usr/bin/env python3
"""
TEST DE CONEXIÓN A GOOGLE SHEETS - VERSION FINAL
Verifica que la conexión está establecida correctamente
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def print_step(num, status, message):
    """Imprime un paso del test con formato visual"""
    symbol = "✅" if status else "❌"
    print(f"\n[{num}/6] {symbol} {message}")

def test_connection():
    """Ejecuta prueba completa de conexión"""
    
    print("\n" + "="*60)
    print("TEST DE CONEXIÓN A GOOGLE SHEETS")
    print("="*60)
    
    # PASO 1: Verificar variables de entorno
    print_step(1, True, "Verificando variables de entorno...")
    
    sheets_id = os.getenv("GOOGLE_SHEETS_ID")
    project_id = os.getenv("GCP_PROJECT_ID")
    client_email = os.getenv("GCP_CLIENT_EMAIL")
    private_key = os.getenv("GCP_PRIVATE_KEY")
    private_key_id = os.getenv("GCP_PRIVATE_KEY_ID")
    auth_uri = os.getenv("GCP_AUTH_URI")
    token_uri = os.getenv("GCP_TOKEN_URI")
    auth_provider_cert = os.getenv("GCP_AUTH_PROVIDER_CERT_URL")
    
    if not all([sheets_id, project_id, client_email, private_key, private_key_id, token_uri, auth_uri]):
        print_step(1, False, "Falta alguna variable de entorno")
        print(f"  - GOOGLE_SHEETS_ID: {'✓' if sheets_id else '✗'}")
        print(f"  - GCP_PROJECT_ID: {'✓' if project_id else '✗'}")
        print(f"  - GCP_CLIENT_EMAIL: {'✓' if client_email else '✗'}")
        print(f"  - GCP_PRIVATE_KEY: {'✓' if private_key else '✗'}")
        print(f"  - GCP_PRIVATE_KEY_ID: {'✓' if private_key_id else '✗'}")
        print(f"  - GCP_AUTH_URI: {'✓' if auth_uri else '✗'}")
        print(f"  - GCP_TOKEN_URI: {'✓' if token_uri else '✗'}")
        return False
    
    print_step(1, True, "✓ Todas las variables cargadas correctamente")
    print(f"    Sheets ID: {sheets_id[:20]}...")
    print(f"    Proyecto: {project_id}")
    print(f"    Email: {client_email}")
    
    # PASO 2: Importar librerías
    print_step(2, True, "Importando librerías necesarias...")
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        print_step(2, True, "✓ gspread y google-auth importados")
    except ImportError as e:
        print_step(2, False, f"Error importando librerías: {e}")
        return False
    
    # PASO 3: Crear diccionario de credenciales
    print_step(3, True, "Creando credenciales...")
    try:
        # Reemplazar \n literales por saltos de línea reales
        if private_key:
            private_key = private_key.replace('\\n', '\n')
        
        creds_dict = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": private_key,
            "client_email": client_email,
            "client_id": "",  # No necesario para acceso de service account
            "auth_uri": auth_uri,
            "token_uri": token_uri,
            "auth_provider_x509_cert_url": auth_provider_cert or "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{client_email}",
            "universe_domain": "googleapis.com"
        }
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        print_step(3, True, "✓ Credenciales creadas correctamente")
    except Exception as e:
        print_step(3, False, f"Error creando credenciales: {e}")
        return False
    
    # PASO 4: Autorizar gspread
    print_step(4, True, "Autorizando cliente gspread...")
    try:
        gc = gspread.authorize(creds)
        print_step(4, True, "✓ Cliente gspread autorizado")
    except Exception as e:
        print_step(4, False, f"Error autorizando gspread: {e}")
        return False
    
    # PASO 5: Abrir la hoja de cálculo
    print_step(5, True, f"Abriendo hoja (ID: {sheets_id[:20]}...)...")
    try:
        sh = gc.open_by_key(sheets_id)
        print_step(5, True, f"✓ Hoja abierta: '{sh.title}'")
    except Exception as e:
        print_step(5, False, f"Error abriendo hoja: {e}")
        print("  Posibles problemas:")
        print("  - El ID de Sheet es incorrecto")
        print("  - El bot no tiene acceso a la hoja (revisar compartir)")
        print("  - Permisos insuficientes")
        return False
    
    # PASO 6: Leer datos de la hoja 'cuentas'
    print_step(6, True, "Leyendo hoja 'cuentas'...")
    try:
        worksheet = sh.worksheet("cuentas")
        all_records = worksheet.get_all_records()
        
        print_step(6, True, f"✓ Hoja 'cuentas' leída correctamente")
        print(f"  - Registros encontrados: {len(all_records)}")
        
        if all_records:
            cols = list(all_records[0].keys())
            print(f"  - Columnas: {', '.join(cols)}")
            print(f"  - Primera fila: {all_records[0]}")
        
        return True
    except Exception as e:
        print_step(6, False, f"Error leyendo 'cuentas': {e}")
        print("  Posibles problemas:")
        print("  - La hoja 'cuentas' no existe")
        print("  - Formato de datos incorrecto")
        return False

if __name__ == "__main__":
    success = test_connection()
    
    print("\n" + "="*60)
    if success:
        print("✅ CONEXIÓN ESTABLECIDA - Todo funciona correctamente")
        print("="*60)
        sys.exit(0)
    else:
        print("❌ CONEXIÓN FALLIDA - Revisa los errores arriba")
        print("="*60)
        sys.exit(1)

"""
Script de verificación de conexión con Google Sheets
Ejecutar: python verify_sheets_connection.py
"""

import os
import sys
import json

def test_google_sheets_connection():
    """Verifica la conexión con Google Sheets paso a paso"""
    
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DE CONEXIÓN GOOGLE SHEETS")
    print("="*60 + "\n")
    
    # Paso 1: Verificar variable de entorno
    print("📋 Paso 1: Verificando credenciales...")
    
    creds_env = os.getenv("GOOGLE_SHEETS_CREDS")
    if not creds_env:
        print("❌ GOOGLE_SHEETS_CREDS no está configurada en variables de entorno")
        print("   Verifica tu archivo .env o configura la variable")
        return False
    
    print("✅ Variable GOOGLE_SHEETS_CREDS encontrada")
    
    # Paso 2: Validar JSON
    print("\n📋 Paso 2: Validando formato JSON de credenciales...")
    
    try:
        creds_dict = json.loads(creds_env)
        print(f"✅ JSON válido con {len(creds_dict)} claves")
        
        # Verificar claves requeridas
        required_keys = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        missing_keys = [k for k in required_keys if k not in creds_dict]
        
        if missing_keys:
            print(f"❌ Faltan claves requeridas: {missing_keys}")
            return False
        
        print(f"✅ Todas las claves requeridas presentes")
        print(f"   📧 Client email: {creds_dict.get('client_email', 'N/A')}")
        print(f"   📦 Project ID: {creds_dict.get('project_id', 'N/A')}")
        
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON: {e}")
        return False
    
    # Paso 3: Importar bibliotecas
    print("\n📋 Paso 3: Verificando bibliotecas...")
    
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        print("✅ gspread y oauth2client importados correctamente")
    except ImportError as e:
        print(f"❌ Error al importar bibliotecas: {e}")
        print("   Instala con: pip install gspread oauth2client")
        return False
    
    # Paso 4: Autenticar
    print("\n📋 Paso 4: Autenticando con Google...")
    
    try:
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        print("✅ Autenticación exitosa")
        
    except Exception as e:
        print(f"❌ Error en autenticación: {e}")
        return False
    
    # Paso 5: Conectar a la hoja
    print("\n📋 Paso 5: Conectando a Google Sheets...")
    
    sheet_name = "BaseDatosMatriz"
    sheet_id = os.getenv("GOOGLE_SHEETS_ID", "").strip()
    
    try:
        if sheet_id:
            spreadsheet = client.open_by_key(sheet_id)
            print("✅ Conectado por GOOGLE_SHEETS_ID")
        else:
            spreadsheet = client.open(sheet_name)
            print(f"✅ Conectado a '{sheet_name}'")
        print(f"   📊 URL: {spreadsheet.url}")
        
        # Listar hojas disponibles
        worksheets = spreadsheet.worksheets()
        print(f"   📑 Hojas disponibles ({len(worksheets)}):")
        for ws in worksheets:
            print(f"      - {ws.title} ({ws.row_count} filas x {ws.col_count} columnas)")
        
    except gspread.exceptions.SpreadsheetNotFound:
        if sheet_id:
            print(f"❌ No se encontró la hoja con ID '{sheet_id}'")
        else:
            print(f"❌ No se encontró la hoja '{sheet_name}'")
        print("   Verifica que:")
        print("   1. La hoja existe en Google Sheets")
        print("   2. Está compartida con el service account email mostrado arriba")
        return False
    except Exception as e:
        print(f"❌ Error al abrir la hoja: {e}")
        return False
    
    # Paso 6: Leer datos
    print("\n📋 Paso 6: Leyendo datos de la primera hoja...")
    
    try:
        worksheet = spreadsheet.sheet1
        
        # Obtener encabezados
        headers = worksheet.row_values(1)
        print(f"✅ Encabezados encontrados ({len(headers)}):")
        print(f"   {', '.join(headers[:10])}")
        if len(headers) > 10:
            print(f"   ... y {len(headers) - 10} más")
        
        # Contar registros
        all_data = worksheet.get_all_records()
        print(f"✅ Total de registros: {len(all_data)}")
        
        if len(all_data) > 0:
            print(f"\n📌 Muestra del primer registro:")
            first_record = all_data[0]
            for key, value in list(first_record.items())[:5]:
                print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error al leer datos: {e}")
        return False
    
    # Resumen final
    print("\n" + "="*60)
    print("✅ CONEXIÓN EXITOSA CON GOOGLE SHEETS")
    print("="*60)
    print(f"📊 Hoja: {sheet_name}")
    print(f"📈 Registros: {len(all_data)}")
    print(f"📋 Columnas: {len(headers)}")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    # Cargar .env si existe
    try:
        from dotenv import load_dotenv
        if load_dotenv():
            print("📁 Archivo .env cargado\n")
    except ImportError:
        print("⚠️  python-dotenv no instalado, usando variables de entorno del sistema\n")
    
    success = test_google_sheets_connection()
    sys.exit(0 if success else 1)

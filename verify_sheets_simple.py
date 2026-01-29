"""
Verificación simple de conexión a Google Sheets usando el mismo método que la app
"""

import os
import sys

# Cargar .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Importar sheets_connector
sys.path.insert(0, os.path.dirname(__file__))
from utils.sheets_connector import get_sheets_connection

def verify_connection():
    """Verifica la conexión usando get_sheets_connection"""
    
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DE GOOGLE SHEETS")
    print("="*60 + "\n")
    
    try:
        print("📋 Paso 1: Conectando a Google Sheets...")
        spreadsheet = get_sheets_connection()
        
        if not spreadsheet:
            print("❌ No se pudo conectar - get_sheets_connection() retornó None")
            return False
            
        print(f"✅ Conectado a: {spreadsheet.title}")
        print(f"📊 URL: {spreadsheet.url}\n")
        
        print("📋 Paso 2: Listando hojas disponibles...")
        worksheets = spreadsheet.worksheets()
        print(f"✅ Total de hojas: {len(worksheets)}")
        for ws in worksheets:
            print(f"   - {ws.title} ({ws.row_count} filas x {ws.col_count} columnas)")
        
        print("\n📋 Paso 3: Leyendo datos de la primera hoja...")
        worksheet = spreadsheet.sheet1
        headers = worksheet.row_values(1)
        print(f"✅ Encabezados ({len(headers)}):")
        print(f"   {', '.join(headers[:8])}")
        if len(headers) > 8:
            print(f"   ... y {len(headers) - 8} más")
        
        all_data = worksheet.get_all_records()
        print(f"✅ Total de registros: {len(all_data)}\n")
        
        if len(all_data) > 0:
            print("📌 Muestra del primer registro:")
            first = all_data[0]
            for key, value in list(first.items())[:6]:
                print(f"   {key}: {value}")
        
        print("\n" + "="*60)
        print("✅ CONEXIÓN EXITOSA")
        print("="*60)
        print(f"📊 Hoja: {spreadsheet.title}")
        print(f"📈 Registros: {len(all_data)}")
        print(f"📋 Columnas: {len(headers)}")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"\nDetalles: {type(e).__name__}")
        
        import traceback
        print("\n📋 Stack trace:")
        traceback.print_exc()
        
        print("\n💡 Soluciones posibles:")
        print("   1. Verifica que existe archivo .env con GCP_SERVICE_ACCOUNT_JSON")
        print("   2. O configura variables individuales: GCP_PRIVATE_KEY, GCP_CLIENT_EMAIL, etc.")
        print("   3. O configura .streamlit/secrets.toml con [gcp_service_account]")
        return False


if __name__ == "__main__":
    success = verify_connection()
    sys.exit(0 if success else 1)

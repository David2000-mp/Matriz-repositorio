#!/usr/bin/env python
"""
Direct test of Google Sheets connection without Streamlit
"""

import sys
import os
from pathlib import Path

# Add workspace to path
workspace = Path(__file__).parent
sys.path.insert(0, str(workspace))

# Set environment for Google Sheets
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

def test_sheets_connection():
    """Test Google Sheets connection directly"""
    print("=" * 60)
    print("PRUEBA DE CONEXIÓN GOOGLE SHEETS")
    print("=" * 60)
    
    try:
        # Import after setting env
        from utils.data_manager import conectar_sheets
        
        print("\n1. Intentando conectar a Google Sheets...")
        ss = conectar_sheets()
        
        if ss:
            print(f"   ✅ CONEXIÓN EXITOSA")
            print(f"   📊 Nombre del Spreadsheet: '{ss.title}'")
            
            print(f"\n2. Hojas encontradas:")
            worksheets = ss.worksheets()
            for i, ws in enumerate(worksheets, 1):
                print(f"   {i}. {ws.title}")
            
            print(f"\n3. Datos de prueba:")
            try:
                # Try to read cuentas sheet
                ws = ss.worksheet("cuentas")
                records = ws.get_all_records()
                print(f"   📋 Hoja 'cuentas': {len(records)} registros")
                if records:
                    print(f"      Primero: {records[0]}")
            except Exception as e:
                print(f"   ⚠️  Hoja 'cuentas' no accesible: {e}")
            
            print(f"\n" + "=" * 60)
            print("✅ RESULTADO: HAY CONEXIÓN CON GOOGLE SHEETS")
            print("=" * 60)
            return True
        else:
            print(f"   ❌ CONEXIÓN FALLIDA: conectar_sheets() devolvió None")
            print(f"\n" + "=" * 60)
            print("❌ RESULTADO: NO HAY CONEXIÓN")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        print(f"\n" + "=" * 60)
        print("❌ RESULTADO: ERROR DE CONEXIÓN")
        print(f"   Detalles: {str(e)}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_sheets_connection()
    sys.exit(0 if success else 1)

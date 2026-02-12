"""
Diagnóstico: Verificar si import_form_responses() está funcionando correctamente
"""
import pandas as pd
from utils.sheets_connector import get_sheets_connection
from utils.form_response_importer import import_form_responses
from utils.logger import get_logger

logger = get_logger(__name__)

print("=" * 80)
print("DIAGNÓSTICO: Importar datos del formulario")
print("=" * 80)

try:
    spreadsheet = get_sheets_connection()
    
    if not spreadsheet:
        print("❌ No se pudo conectar a Google Sheets")
        exit(1)
    
    print("\n📋 Ejecutando import_form_responses()...")
    cuentas_df, metricas_df = import_form_responses(spreadsheet)
    
    print(f"\n✓ Cuentas importadas: {len(cuentas_df)}")
    if not cuentas_df.empty:
        print("\nContenido de cuentas:")
        print(cuentas_df.to_string(index=False))
    else:
        print("⚠️ DataFrame de cuentas está vacío")
    
    print(f"\n\n✓ Métricas importadas: {len(metricas_df)}")
    if not metricas_df.empty:
        print("\nÚltimas 5 métricas:")
        print(metricas_df.tail(5).to_string(index=False))
        print(f"\nFechas únicas: {metricas_df['fecha'].nunique()}")
        print(f"Plataformas úniques: {metricas_df['plataforma'].nunique() if 'plataforma' in metricas_df.columns else 'N/A'}")
    else:
        print("⚠️ DataFrame de métricas está vacío")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

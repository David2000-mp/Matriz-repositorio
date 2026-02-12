"""
Script de diagnóstico: Verificar que los datos en Google Sheets se están cargando correctamente.
Este script lee directamente de Google Sheets sin cacheo para ver los datos verdaderos.
"""
import pandas as pd
from utils.sheets_connector import get_sheets_connection
from utils.logger import get_logger

logger = get_logger(__name__)

print("=" * 80)
print("DIAGNÓSTICO: Leyendo datos de Google Sheets (SIN CACHEO)")
print("=" * 80)

try:
    spreadsheet = get_sheets_connection()
    
    if not spreadsheet:
        print("❌ No se pudo conectar a Google Sheets")
        exit(1)
    
    # Leer Cuentas
    print("\n📊 HOJA: cuentas")
    print("-" * 80)
    try:
        ws_c = spreadsheet.worksheet("cuentas")
        c_data = ws_c.get_all_records()
        if c_data:
            cuentas_df = pd.DataFrame(c_data)
            print(f"✓ Registros encontrados: {len(cuentas_df)}")
            print("\nContenido:")
            print(cuentas_df.to_string(index=False))
        else:
            print("⚠️ Hoja 'cuentas' vacía")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Leer Métricas
    print("\n\n📊 HOJA: metricas")
    print("-" * 80)
    try:
        ws_m = spreadsheet.worksheet("metricas")
        raw_data = ws_m.get()
        if raw_data and len(raw_data) > 1:
            headers = raw_data[0]
            data_rows = raw_data[1:]
            metricas_df = pd.DataFrame(data_rows, columns=headers)
            print(f"✓ Registros encontrados: {len(metricas_df)}")
            print("\nÚltimos 5 registros:")
            print(metricas_df.tail(5).to_string(index=False))
            print(f"\nFechas únicas: {metricas_df['fecha'].nunique() if 'fecha' in metricas_df.columns else 'N/A'}")
            print(f"Plataformas: {metricas_df['plataforma'].unique() if 'plataforma' in metricas_df.columns else 'N/A'}")
        else:
            print("⚠️ Hoja 'metricas' vacía")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Leer Formulario
    print("\n\n📊 HOJA: Respuestas de formulario 3")
    print("-" * 80)
    try:
        ws_f = spreadsheet.worksheet("Respuestas de formulario 3")
        f_data = ws_f.get_all_records()
        if f_data:
            print(f"✓ Respuestas encontradas: {len(f_data)}")
            print(f"Últimas 3 respuestas:")
            for i, row in enumerate(f_data[-3:], 1):
                print(f"\n  Respuesta {len(f_data) - 3 + i}:")
                for key, val in row.items():
                    if val:  # Solo mostrar campos no vacíos
                        print(f"    {key}: {val}")
        else:
            print("⚠️ Hoja 'Respuestas de formulario 3' vacía")
    except Exception as e:
        print(f"⚠️ Hoja 'Respuestas de formulario 3' no encontrada: {e}")

except Exception as e:
    print(f"❌ Error crítico: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("FIN DEL DIAGNÓSTICO")
print("=" * 80)

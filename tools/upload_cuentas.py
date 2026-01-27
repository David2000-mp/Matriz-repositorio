"""
Script para subir cuentas a Google Sheets
"""

import pandas as pd
from utils.sheets_connector import conectar_sheets

# Cargar cuentas locales
cuentas_df = pd.read_csv('data/cuentas.csv')
print(f'Cuentas locales: {len(cuentas_df)} filas')

# Subir a Google Sheets
ss = conectar_sheets()
if ss:
    try:
        ws_cuentas = ss.worksheet('cuentas')
        # Limpiar y subir cuentas
        ws_cuentas.clear()
        ws_cuentas.update([cuentas_df.columns.tolist()] + cuentas_df.values.tolist())
        print(f'✅ Cuentas subidas a Google Sheets: {len(cuentas_df)} registros')
    except Exception as e:
        print(f'❌ Error subiendo cuentas: {e}')
else:
    print('❌ No se pudo conectar a Google Sheets')
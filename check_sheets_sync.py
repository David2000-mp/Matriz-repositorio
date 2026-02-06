import pandas as pd
from utils.sheets_connector import conectar_sheets

# Cargar datos locales directamente del CSV
df_metricas = pd.read_csv('data/metricas.csv')

print('=== VERIFICACIÓN GOOGLE SHEETS ===')
print(f'Datos locales - Métricas: {len(df_metricas)} filas')

# Verificar engagement en datos locales
if not df_metricas.empty:
    print(f'Engagement local - Rango: {df_metricas["engagement_rate"].min():.4f} - {df_metricas["engagement_rate"].max():.4f}')
    print(f'Engagement local - Promedio: {df_metricas["engagement_rate"].mean():.4f}')
    print(f'Valores > 15%: {(df_metricas["engagement_rate"] > 15).sum()}')

# Intentar leer desde Google Sheets usando gspread
try:
    spreadsheet = conectar_sheets()
    if spreadsheet:
        print(f'Conectado a spreadsheet: {spreadsheet.title}')

        # Listar todas las hojas disponibles
        worksheets = spreadsheet.worksheets()
        print(f'Hojas disponibles: {[ws.title for ws in worksheets]}')

        # Leer la hoja de métricas (con minúscula)
        try:
            worksheet = spreadsheet.worksheet('metricas')
            values = worksheet.get_all_values()
            print(f'Filas en metricas: {len(values)}')

            if len(values) > 1:
                print('Headers:', values[0])

                # Verificar algunas filas de datos
                print('Muestra de datos en Google Sheets:')
                for i in range(1, min(6, len(values))):
                    row = values[i]
                    if len(row) >= 7:
                        id_cuenta = row[0] if len(row) > 0 else 'N/A'
                        fecha = row[1] if len(row) > 1 else 'N/A'
                        engagement_val = row[6] if len(row) > 6 else 'N/A'
                        print(f'  Fila {i+1}: ID={id_cuenta[:15]}..., Fecha={fecha}, ER={engagement_val}')
        except Exception as e:
            print(f'Error leyendo hoja metricas: {e}')
        else:
            print('No hay hojas en el spreadsheet')
    else:
        print('❌ No se pudo conectar a Google Sheets')
except Exception as e:
    print(f'Error conectando a Google Sheets: {e}')
from utils.data_provider import DataProvider
import pandas as pd

dp = DataProvider()
df = dp.get_merged_data()
print('=== ANÁLISIS DE DATOS ===')
print('Filas totales:', len(df))
print('Columnas:', df.columns.tolist())
print()
print('=== TIPOS DE DATOS ===')
print(df.dtypes)
print()
print('=== MUESTRA DE FECHA ===')
print('Primeras fechas:', df['fecha'].head(5).tolist())
print('Tipo de fecha[0]:', type(df['fecha'].iloc[0]) if len(df) > 0 else 'N/A')
print()
print('=== VALORES ÚNICOS ===')
print('Plataformas:', df['plataforma'].unique() if 'plataforma' in df.columns else 'N/A')
print('Entidades:', df['entidad'].nunique() if 'entidad' in df.columns else 'N/A')
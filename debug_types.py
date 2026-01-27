"""
Script para diagnosticar el problema de tipos de datos
"""

import pandas as pd
from utils.data_provider import data_provider

cuentas, metricas = data_provider.get_data()

print('=== DIAGNÓSTICO DE TIPOS DE DATOS ===')
print()

print('CUENTAS:')
if not cuentas.empty:
    print(f'  Filas: {len(cuentas)}')
    print(f'  Tipo de id_cuenta: {cuentas["id_cuenta"].dtype}')
    print(f'  Valores de id_cuenta (primeros 3): {cuentas["id_cuenta"].head(3).tolist()}')
    print(f'  Columnas: {list(cuentas.columns)}')
else:
    print('  CUENTAS VACÍO')

print()
print('MÉTRICAS:')
if not metricas.empty:
    print(f'  Filas: {len(metricas)}')
    print(f'  Tipo de id_cuenta: {metricas["id_cuenta"].dtype}')
    print(f'  Valores de id_cuenta (primeros 3): {metricas["id_cuenta"].head(3).tolist()}')
    print(f'  Columnas: {list(metricas.columns)}')
else:
    print('  MÉTRICAS VACÍO')

print()
print('=== INTENTANDO MERGE ===')
try:
    # Convertir tipos
    if not cuentas.empty and not metricas.empty:
        cuentas_copy = cuentas.copy()
        metricas_copy = metricas.copy()

        cuentas_copy["id_cuenta"] = cuentas_copy["id_cuenta"].astype(str)
        metricas_copy["id_cuenta"] = metricas_copy["id_cuenta"].astype(str)

        print(f'Tipos después de conversión:')
        print(f'  Cuentas id_cuenta: {cuentas_copy["id_cuenta"].dtype}')
        print(f'  Métricas id_cuenta: {metricas_copy["id_cuenta"].dtype}')

        df = pd.merge(metricas_copy, cuentas_copy, on="id_cuenta", how="left")
        print(f'✅ Merge exitoso: {len(df)} filas resultantes')
except Exception as e:
    print(f'❌ Error en merge: {e}')
"""
Diagnóstico completo: Verificar flujo de datos desde formulario hasta data_provider
"""
import pandas as pd
from utils.data_provider import data_provider
from utils.logger import get_logger

logger = get_logger(__name__)

print("=" * 80)
print("DIAGNÓSTICO COMPLETO: Flujo de datos")
print("=" * 80)

# Test 1: Cargar datos sin forzar reload
print("\n📋 PASO 1: Cargar datos del data_provider (sin forzar recarga)")
print("-" * 80)
df_merged_1 = data_provider.get_merged_data(force_reload=False)
print(f"✓ Datos cargados: {len(df_merged_1)} registros")
if not df_merged_1.empty:
    print(f"  Entidades encontradas: {df_merged_1['entidad'].unique().tolist()}")
    print(f"  Plataformas encontradas: {df_merged_1['plataforma'].unique().tolist()}")
    print(f"  Fechas encontradas: {sorted(df_merged_1['fecha'].unique())[:5]}")
    print(f"\n  Últimos 5 registros:")
    print(df_merged_1[['entidad', 'plataforma', 'fecha', 'seguidores', 'engagement_rate']].tail(5).to_string(index=False))
else:
    print("❌ DataFrame está vacío")

# Test 2: Forzar recarga
print("\n\n📋 PASO 2: Forzar recarga de datos (force_reload=True)")
print("-" * 80)
df_merged_2 = data_provider.get_merged_data(force_reload=True)
print(f"✓ Datos recargados: {len(df_merged_2)} registros")
if not df_merged_2.empty:
    print(f"  Entidades encontradas: {df_merged_2['entidad'].unique().tolist()}")
    print(f"  Plataformas encontradas: {df_merged_2['plataforma'].unique().tolist()}")
    print(f"  Fechas encontradas: {sorted(df_merged_2['fecha'].unique())[:5]}")
    print(f"\n  Últimos 5 registros:")
    print(df_merged_2[['entidad', 'plataforma', 'fecha', 'seguidores', 'engagement_rate']].tail(5).to_string(index=False))
else:
    print("❌ DataFrame está vacío")

# Test 3: Cargar datos nuevamente (debe usar caché de 15 segundos)
print("\n\n📋 PASO 3: Cargar datos nuevamente (debe usar caché de 15s)")
print("-" * 80)
df_merged_3 = data_provider.get_merged_data(force_reload=False)
print(f"✓ Datos cargados desde caché: {len(df_merged_3)} registros")
print(f"  ¿Datos iguales a paso 2?: {len(df_merged_2) == len(df_merged_3)}")

print("\n" + "=" * 80)
print("✓ Diagnóstico completo")
print("=" * 80)

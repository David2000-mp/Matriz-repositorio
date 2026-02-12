"""
Script de diagnóstico para verificar por qué las gráficas temporales no muestran evolución.
"""
import pandas as pd
from utils.data_provider import data_provider
from utils.analytics import normalize_monthly_latest, apply_moving_average, detect_anomalies

print("=" * 80)
print("DIAGNÓSTICO DE GRÁFICAS TEMPORALES")
print("=" * 80)

# Paso 1: Cargar datos
print("\n1. Cargando datos...")
df = data_provider.get_merged_data()
print(f"   ✓ Datos cargados: {len(df)} registros")
print(f"   ✓ Columnas: {list(df.columns)}")

# Paso 2: Crear df_full como en dashboard.py
print("\n2. Creando df_full...")
df_full = df.copy()

if "fecha" in df_full.columns:
    print(f"   - Antes conversión datetime: tipo={df_full['fecha'].dtype}")
    df_full["fecha"] = pd.to_datetime(df_full["fecha"], errors="coerce")
    print(f"   - Después conversión datetime: tipo={df_full['fecha'].dtype}")
    
    antes_drop = len(df_full)
    df_full = df_full.dropna(subset=['fecha'])
    print(f"   - Registros después de dropna: {len(df_full)} (eliminados: {antes_drop - len(df_full)})")
    
    antes_normalize = len(df_full)
    df_full = normalize_monthly_latest(df_full)
    print(f"   - Registros después de normalize_monthly_latest: {len(df_full)} (eliminados: {antes_normalize - len(df_full)})")
    
    print(f"   - Fechas únicas después de normalize: {sorted(df_full['fecha'].unique())}")

# Paso 3: Aplicar moving average
print("\n3. Aplicando moving average...")
df_full = apply_moving_average(df_full, col="seguidores")
if "interacciones" in df_full.columns:
    df_full = apply_moving_average(df_full, col="interacciones")
print(f"   ✓ Columnas después de MA: {list(df_full.columns)}")

# Paso 4: Detectar anomalías
print("\n4. Detectando anomalías...")
df_full = detect_anomalies(df_full, threshold=0.20)
print(f"   ✓ DataFrame final: {len(df_full)} registros")

# Paso 5: Simular creación de df_evo (lo que hace la gráfica)
print("\n5. Creando df_evo para gráfica de evolución...")
print(f"   - df_full antes de groupby:")
print(f"     * Registros: {len(df_full)}")
print(f"     * Plataformas únicas: {df_full['plataforma'].unique()}")
print(f"     * Fechas únicas: {len(df_full['fecha'].unique())}")

df_evo = (
    df_full.groupby(["fecha", "plataforma"])["seguidores"].max().reset_index()
)

print(f"\n   - df_evo después de groupby:")
print(f"     * Registros: {len(df_evo)}")
print(f"     * Tipo de fecha: {df_evo['fecha'].dtype}")

# Aplicar conversión como en el fix
df_evo["fecha"] = pd.to_datetime(df_evo["fecha"], errors="coerce")
df_evo = df_evo.dropna(subset=["fecha"]).sort_values(["plataforma", "fecha"])

print(f"\n   - df_evo después de conversión y sort:")
print(f"     * Registros: {len(df_evo)}")
print(f"     * Tipo de fecha: {df_evo['fecha'].dtype}")

print("\n6. Datos por plataforma:")
for plat in df_evo['plataforma'].unique():
    dfp = df_evo[df_evo['plataforma'] == plat]
    print(f"   - {plat}:")
    print(f"     * Puntos: {len(dfp)}")
    print(f"     * Fechas: {sorted(dfp['fecha'].dt.strftime('%Y-%m-%d').unique())}")
    print(f"     * Seguidores: {dfp['seguidores'].tolist()}")

print("\n7. DataFrame completo df_evo:")
print(df_evo.sort_values(['plataforma', 'fecha']))

print("\n" + "=" * 80)
print("DIAGNÓSTICO COMPLETO")
print("=" * 80)

# Verificar si el problema es normalize_monthly_latest colapsando todo a un mes
print("\n8. Verificación de normalize_monthly_latest:")
print(f"   - Registros originales: {len(df)}")
print(f"   - Registros después de normalize: {len(df_full)}")
print(f"   - Fechas únicas originales: {df['fecha'].nunique() if 'fecha' in df.columns else 'N/A'}")
print(f"   - Fechas únicas después de normalize: {df_full['fecha'].nunique()}")

if df_full['fecha'].nunique() == 1:
    print("\n   ⚠️ PROBLEMA ENCONTRADO: normalize_monthly_latest está colapsando todas las fechas a una sola!")
    print(f"   Fecha única: {df_full['fecha'].unique()[0]}")

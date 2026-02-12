"""
Test para verificar qué está pasando con el selector de periodo.
"""
import pandas as pd
from utils.data_provider import data_provider
from utils.analytics import normalize_monthly_latest, apply_moving_average, detect_anomalies

# Cargar datos
df = data_provider.get_merged_data()
df_full = df.copy()

if "fecha" in df_full.columns:
    df_full["fecha"] = pd.to_datetime(df_full["fecha"], errors="coerce")
    df_full = df_full.dropna(subset=['fecha'])
    df_full = normalize_monthly_latest(df_full)

df_full = apply_moving_average(df_full, col="seguidores")
if "interacciones" in df_full.columns:
    df_full = apply_moving_average(df_full, col="interacciones")

df_full = detect_anomalies(df_full, threshold=0.20)

# Simular lo que hace el filtro temporal
meses = sorted(df_full["fecha"].dropna().dt.strftime("%Y-%m").unique(), reverse=True)
mes = meses[0] if meses else None

print("VERIFICACIÓN DE FILTROS TEMPORALES")
print("=" * 80)
print(f"\nMeses disponibles: {meses}")
print(f"Mes actual (más reciente): {mes}")

# Simular selección "Último mes"
print("\n1. Simulando selección 'Último mes':")
df_m_month_ultimo = df_full[df_full["fecha"].dt.strftime("%Y-%m") == mes].copy()
print(f"   - Registros en df_m_month: {len(df_m_month_ultimo)}")
print(f"   - Fechas únicas: {df_m_month_ultimo['fecha'].unique()}")

# Simular selección "Últimos 3 meses"
print("\n2. Simulando selección 'Últimos 3 meses':")
if len(meses) >= 3:
    meses_seleccionados = meses[:3]
    df_m_month_3meses = df_full[df_full["fecha"].dt.strftime("%Y-%m").isin(meses_seleccionados)].copy()
    print(f"   - Meses seleccionados: {meses_seleccionados}")
    print(f"   - Registros en df_m_month: {len(df_m_month_3meses)}")
    print(f"   - Fechas únicas: {sorted(df_m_month_3meses['fecha'].unique())}")

# Simular selección "Histórico"
print("\n3. Simulando selección 'Histórico':")
df_m_month_historico = df_full.copy()
print(f"   - Registros en df_m_month: {len(df_m_month_historico)}")
print(f"   - Fechas únicas: {sorted(df_m_month_historico['fecha'].unique())}")

print("\n" + "=" * 80)
print("IMPORTANTE:")
print("=" * 80)
print(f"df_full siempre mantiene: {len(df_full)} registros con {len(df_full['fecha'].unique())} fechas únicas")
print("Las gráficas de EVOLUCIÓN usan df_full (no df_m_month)")
print("Por lo tanto, las gráficas siempre deberían mostrar TODOS los datos históricos")
print("\nSi solo se ve un punto, el problema está EN EL NAVEGADOR o en PLOTLY, no en los datos.")

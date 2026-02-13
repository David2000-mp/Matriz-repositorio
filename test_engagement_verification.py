"""
Test de verificación del cálculo de Engagement Promedio en Dashboard
"""
import pandas as pd
import sys
import os

# Agregar path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import data_provider

print("=" * 80)
print("VERIFICACIÓN DE CÁLCULO DE ENGAGEMENT PROMEDIO")
print("=" * 80)

# Cargar datos
cuentas, metricas = data_provider.get_data(force_reload=False)

# Fusionar cuentas y métricas
if metricas.empty:
    print("❌ No hay datos de métricas disponibles")
    sys.exit(1)

df_full = metricas

print(f"\n📊 Columnas disponibles: {list(df_full.columns)}")
print(f"📊 Total de registros: {len(df_full)}")

# Obtener mes más reciente
df_full['fecha'] = pd.to_datetime(df_full['fecha'], errors='coerce')
meses_disponibles = sorted(df_full["fecha"].dropna().dt.strftime("%Y-%m").unique(), reverse=True)

if len(meses_disponibles) < 1:
    print("❌ No hay meses disponibles")
    sys.exit(1)

mes_actual = meses_disponibles[0]
mes_anterior = meses_disponibles[1] if len(meses_disponibles) > 1 else None

print(f"\n📅 Mes actual: {mes_actual}")
print(f"📅 Mes anterior: {mes_anterior}")

# Filtrar datos del mes actual
df_mes_actual = df_full[df_full["fecha"].dt.strftime("%Y-%m") == mes_actual]
df_unique = df_mes_actual.drop_duplicates(subset=['entidad', 'plataforma'], keep='last')

print(f"\n📊 Registros del mes actual: {len(df_mes_actual)}")
print(f"📊 Cuentas únicas (entidad+plataforma): {len(df_unique)}")

# Calcular métricas del mes actual
tot_seg = df_unique['seguidores'].sum()
tot_int = df_unique['interacciones'].sum()
er_global = (tot_int / tot_seg * 100.0) if tot_seg > 0 else 0.0

print(f"\n{'=' * 80}")
print(f"MES ACTUAL: {mes_actual}")
print(f"{'=' * 80}")
print(f"Total Seguidores: {tot_seg:,.0f}")
print(f"Total Interacciones: {tot_int:,.0f}")
print(f"Engagement Rate: {er_global:.2f}%")
print(f"Cálculo: ({tot_int:,.0f} / {tot_seg:,.0f}) × 100 = {er_global:.2f}%")

# Mostrar detalle por cuenta
print(f"\n{'=' * 80}")
print("DETALLE POR CUENTA (Mes actual)")
print(f"{'=' * 80}")
print(f"{'Entidad':<40} {'Plataforma':<15} {'Seguidores':>12} {'Interacciones':>15} {'ER%':>8}")
print("-" * 100)

for _, row in df_unique.iterrows():
    entidad = str(row['entidad'])[:38]
    plataforma = str(row['plataforma'])[:13]
    seg = row['seguidores']
    inter = row['interacciones']
    er = (inter / seg * 100) if seg > 0 else 0
    print(f"{entidad:<40} {plataforma:<15} {seg:>12,.0f} {inter:>15,.0f} {er:>7.2f}%")

# Calcular con mes anterior si existe
if mes_anterior:
    df_mes_anterior = df_full[df_full["fecha"].dt.strftime("%Y-%m") == mes_anterior]
    df_prev_unique = df_mes_anterior.drop_duplicates(subset=['entidad', 'plataforma'], keep='last')
    
    seg_prev = df_prev_unique['seguidores'].sum()
    int_prev = df_prev_unique['interacciones'].sum()
    er_prev = (int_prev / seg_prev * 100.0) if seg_prev > 0 else 0.0
    delta_er = er_global - er_prev
    
    print(f"\n{'=' * 80}")
    print(f"MES ANTERIOR: {mes_anterior}")
    print(f"{'=' * 80}")
    print(f"Total Seguidores: {seg_prev:,.0f}")
    print(f"Total Interacciones: {int_prev:,.0f}")
    print(f"Engagement Rate: {er_prev:.2f}%")
    print(f"Cálculo: ({int_prev:,.0f} / {seg_prev:,.0f}) × 100 = {er_prev:.2f}%")
    
    print(f"\n{'=' * 80}")
    print("COMPARACIÓN MES ACTUAL vs MES ANTERIOR")
    print(f"{'=' * 80}")
    print(f"Engagement actual:   {er_global:.2f}%")
    print(f"Engagement anterior: {er_prev:.2f}%")
    print(f"Delta (pp):          {delta_er:+.2f} pp")
    print(f"\n💡 Interpretación:")
    if delta_er > 0:
        print(f"   ✅ El engagement AUMENTÓ {delta_er:.2f} puntos porcentuales")
    elif delta_er < 0:
        print(f"   ⚠️ El engagement DISMINUYÓ {abs(delta_er):.2f} puntos porcentuales")
    else:
        print(f"   ➡️ El engagement se mantuvo igual")

print(f"\n{'=' * 80}")
print("VALIDACIÓN")
print(f"{'=' * 80}")

# Verificar si hay valores sospechosos
issues = []

if er_global > 50:
    issues.append(f"⚠️ Engagement muy alto ({er_global:.2f}%). Revisar datos de interacciones.")

if tot_int > tot_seg * 2:
    issues.append(f"⚠️ Interacciones ({tot_int:,.0f}) > 2× Seguidores ({tot_seg:,.0f}). Posible error en captura.")

if mes_anterior and abs(delta_er) > 20:
    issues.append(f"⚠️ Delta muy grande ({delta_er:+.2f} pp). Verificar consistencia de datos.")

if issues:
    print("\n❌ PROBLEMAS DETECTADOS:")
    for issue in issues:
        print(f"   {issue}")
else:
    print("\n✅ Los cálculos parecen correctos")

print(f"\n{'=' * 80}")

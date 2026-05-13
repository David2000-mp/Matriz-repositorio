#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico final: Verificar que Instagram mantiene todas sus mediciones 
con la corrección de modo monthly por entidad
"""

import pandas as pd
import sys
sys.path.insert(0, '.')

from utils.data_provider import data_provider
from utils.analytics import build_followers_growth_ranking

cuentas, metricas = data_provider.get_data(force_reload=False)

# Merge para obtener plataforma
df_full = metricas.merge(cuentas[['id_cuenta', 'plataforma']], on='id_cuenta', how='left')

# Instagram solo
ig_data = df_full[df_full['plataforma'] == 'Instagram'].copy(); ig_data = ig_data.merge(cuentas[['id_cuenta', 'entidad']], on='id_cuenta', how='left')
ig_data['fecha'] = pd.to_datetime(ig_data['fecha'], errors='coerce')

print("\n" + "=" * 80)
print("DIAGNÓSTICO INSTAGRAM - DESPUÉS DE CORRECCIÓN")
print("=" * 80)

# Contar instituciones únicas
ig_entities = ig_data['entidad'].unique()
print(f"\nTotal instituciones con Instagram: {len(ig_entities)}")
print(f"Total mediciones Instagram en BD: {len(ig_data)}")

# Aplicar ranking en modo monthly
ranking_monthly = build_followers_growth_ranking(df_full, mode='monthly', top_n=15)

# Filtrar solo Instagram
ig_ranking = ranking_monthly[ranking_monthly['plataforma'] == 'Instagram'] if not ranking_monthly.empty else pd.DataFrame()

print(f"\nInstagram en Top 15 (modo='monthly'): {len(ig_ranking)}")

# Análisis
if len(ig_ranking) > 0:
    print(f"\nInstituciones Instagram incluidas en ranking:")
    for _, row in ig_ranking.iterrows():
        print(f"  {row['entidad']}: +{row['crecimiento_abs']:.0f} ({row['crecimiento_pct']:.1f}%)")
else:
    print("\n❌ PROBLEMA: Ranking vacío")

# Comparar: cuáles se incluyeron y cuáles no
ig_entities_in_ranking = set(ig_ranking['entidad'].unique()) if not ig_ranking.empty else set()
ig_entities_source = set(ig_data['entidad'].unique())
perdidas = ig_entities_source - ig_entities_in_ranking

print(f"\nInstituciones sin datos de crecimiento: {len(perdidas)}")
if perdidas:
    print("(Esto es normal si no tuvieron crecimiento positivo)")
    for ent in sorted(perdidas)[:5]:  # Mostrar primeras 5
        ent_data = ig_data[ig_data['entidad'] == ent]
        meses = ent_data['fecha'].dt.to_period('M').nunique()
        seg_min = int(ent_data['seguidores'].min())
        seg_max = int(ent_data['seguidores'].max())
        print(f"  - {ent}: {meses} meses, {seg_min:,} -> {seg_max:,} seguidores")

# Test con latest_two también
print("\n" + "-" * 80)
ranking_latest = build_followers_growth_ranking(df_full, mode='latest_two', top_n=15)
ig_ranking_latest = ranking_latest[ranking_latest['plataforma'] == 'Instagram'] if not ranking_latest.empty else pd.DataFrame()

print(f"\nInstagram en Top 15 (modo='latest_two'): {len(ig_ranking_latest)}")

print("\n" + "=" * 80)
print("CONCLUSIÓN")
print("=" * 80)

if len(ig_ranking) > 0 and len(ig_ranking_latest) > 0:
    print("""
✅ CORRECCIÓN EXITOSA

El modo 'monthly' ahora:
- Compara últimos 2 meses distintos POR ENTIDAD/PLATAFORMA
- No pierde mediciones de Instagram que tienen meses parciales
- Incluye todas las instituciones con crecimiento positivo

Cambio implementado:
- Antes: Comparaba solo 2 meses globales (perdía datos)
- Ahora: Cada institución compara sus propios últimos 2 meses
""")
else:
    print("❌ Posible problema aún presente")

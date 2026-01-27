import pandas as pd
from utils import load_data

cuentas, metricas = load_data()
if 'id_cuenta' in cuentas.columns:
    cuentas['id_cuenta'] = cuentas['id_cuenta'].astype(str)
if 'id_cuenta' in metricas.columns:
    metricas['id_cuenta'] = metricas['id_cuenta'].astype(str)

# Ensure fecha is datetime
if 'fecha' in metricas.columns:
    metricas['fecha'] = pd.to_datetime(metricas['fecha'], errors='coerce')

# Deduplicate metricas by keeping latest snapshot per id_cuenta per month
if 'id_cuenta' in metricas.columns and 'fecha' in metricas.columns:
    metricas['period'] = metricas['fecha'].dt.to_period('M')  # type: ignore
    metricas_dedup = (
        metricas.sort_values('fecha')
        .groupby(['id_cuenta', 'period'], sort=False)
        .tail(1)
        .drop(columns=['period'])
        .reset_index(drop=True)
    )
else:
    metricas_dedup = metricas.copy()

# Merge
df_global = pd.merge(metricas_dedup, cuentas, on='id_cuenta', how='left')
if 'fecha' in df_global.columns:
    df_global['fecha'] = pd.to_datetime(df_global['fecha'], errors='coerce')

meses = sorted(df_global['fecha'].dt.strftime('%Y-%m').dropna().unique(), reverse=True)  # type: ignore
mes = meses[0] if meses else None
print('LATEST_MONTH', mes)
if mes:
    df_m = df_global[df_global['fecha'].dt.strftime('%Y-%m') == mes]  # type: ignore
    if 'id_cuenta' in df_m.columns:
        tot_seg = int(df_m.drop_duplicates(subset=['id_cuenta'])['seguidores'].sum())
    else:
        tot_seg = int(df_m['seguidores'].sum())
    print('TOT_SEG_LATEST', tot_seg)

# previous month
mes_prev = meses[1] if len(meses) > 1 else None
if mes_prev:
    df_prev = df_global[df_global['fecha'].dt.strftime('%Y-%m') == mes_prev]  # type: ignore
    if 'id_cuenta' in df_prev.columns:
        seg_prev = int(df_prev.drop_duplicates(subset=['id_cuenta'])['seguidores'].sum())
    else:
        seg_prev = int(df_prev['seguidores'].sum())
    print('TOT_SEG_PREV', seg_prev)
    if seg_prev > 0:
        print('DELTA_PCT', (tot_seg - seg_prev) / seg_prev * 100)
    else:
        print('DELTA_PCT', 'N/A')
else:
    print('NO_PREV_MONTH')

from utils.analytics import calculate_health_score
print('HEALTH_SCORE', calculate_health_score(df_global))

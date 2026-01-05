import pandas as pd
from utils import load_data

cuentas, metricas = load_data()
if 'id_cuenta' in cuentas.columns:
    cuentas['id_cuenta'] = cuentas['id_cuenta'].astype(str)
if 'id_cuenta' in metricas.columns:
    metricas['id_cuenta'] = metricas['id_cuenta'].astype(str)

df = pd.merge(metricas, cuentas, on='id_cuenta', how='left')
if 'fecha' in df.columns:
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

meses = sorted(df['fecha'].dt.strftime('%Y-%m').dropna().unique(), reverse=True)
mes = meses[0] if meses else None
print('LATEST_MONTH', mes)
if mes:
    df_m = df[df['fecha'].dt.strftime('%Y-%m') == mes]
    if 'id_cuenta' in df_m.columns:
        tot_seg = int(df_m.drop_duplicates(subset=['id_cuenta'])['seguidores'].sum())
    else:
        tot_seg = int(df_m['seguidores'].sum())
    print('TOT_SEG_LATEST', tot_seg)
else:
    print('NO_VALID_MONTH')

# previous month delta
mes_prev = meses[1] if len(meses) > 1 else None
if mes_prev:
    df_prev = df[df['fecha'].dt.strftime('%Y-%m') == mes_prev]
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
print('HEALTH_SCORE', calculate_health_score(df))

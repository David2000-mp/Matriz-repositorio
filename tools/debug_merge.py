import pandas as pd
from utils import load_data

cuentas, metricas = load_data()
print('CUENTAS_ROWS', len(cuentas))
print('METRICAS_ROWS', len(metricas))
print('CUENTAS_UNIQUE_ID', cuentas['id_cuenta'].nunique() if 'id_cuenta' in cuentas.columns else 'no id')
print('METRICAS_UNIQUE_ID', metricas['id_cuenta'].nunique() if 'id_cuenta' in metricas.columns else 'no id')

if 'id_cuenta' in cuentas.columns:
    dup_cuentas = cuentas[cuentas.duplicated(subset=['id_cuenta'], keep=False)]
    print('CUENTAS_DUPLICATES_SAMPLE', dup_cuentas.head(5).to_dict(orient='records'))

# dedup metricas monthly
if 'fecha' in metricas.columns:
    metricas['fecha'] = pd.to_datetime(metricas['fecha'], errors='coerce')
    metricas['period'] = metricas['fecha'].dt.to_period('M')
    metricas_dedup = metricas.sort_values('fecha').groupby(['id_cuenta','period'], sort=False).tail(1).drop(columns=['period']).reset_index(drop=True)
else:
    metricas_dedup = metricas.copy()

print('METRICAS_DEDUP_ROWS', len(metricas_dedup))
print('METRICAS_DEDUP_UNIQUE_ID', metricas_dedup['id_cuenta'].nunique() if 'id_cuenta' in metricas_dedup.columns else 'no id')

# check merge
if 'id_cuenta' in metricas_dedup.columns and 'id_cuenta' in cuentas.columns:
    df_global = pd.merge(metricas_dedup, cuentas, on='id_cuenta', how='left')
    print('MERGED_ROWS', len(df_global))
    # show sample where a given id appears multiple times after merge
    sample = df_global['id_cuenta'].value_counts().head(5)
    print('MERGED_ID_COUNTS_SAMPLE', sample.to_dict())
else:
    print('Cannot merge: id_cuenta missing')

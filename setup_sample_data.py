import pandas as pd
import os
from utils.data_manager import COLEGIOS_MARISTAS

# Leer datos de ejemplo
sample_df = pd.read_csv('data/sample_upload_full.csv')
print('Datos de ejemplo cargados:')
print(sample_df.head())
print(f'Total filas: {len(sample_df)}')

# Crear cuentas únicas usando usernames reales de COLEGIOS_MARISTAS
cuentas_df = sample_df[['entidad', 'plataforma']].drop_duplicates()
cuentas_df['id_cuenta'] = range(1, len(cuentas_df) + 1)

# Mapear a usernames reales
def get_real_username(entidad, plataforma):
    if entidad in COLEGIOS_MARISTAS and plataforma in COLEGIOS_MARISTAS[entidad]:
        return COLEGIOS_MARISTAS[entidad][plataforma]
    else:
        # Fallback si no existe
        return f'@{entidad.lower().replace(" ", "")}_{plataforma.lower()}'

cuentas_df['usuario_red'] = cuentas_df.apply(lambda x: get_real_username(x['entidad'], x['plataforma']), axis=1)
cuentas_df = cuentas_df[['id_cuenta', 'entidad', 'plataforma', 'usuario_red']]

print('\nCuentas creadas:')
print(cuentas_df)

# Crear métricas con id_cuenta
metricas_df = sample_df.merge(cuentas_df, on=['entidad', 'plataforma'], how='left')
metricas_df = metricas_df[['id_cuenta', 'fecha', 'seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']]

print('\nMétricas creadas:')
print(metricas_df)

# Guardar archivos
cuentas_df.to_csv('data/cuentas.csv', index=False)
metricas_df.to_csv('data/metricas.csv', index=False)

print('\n✅ Archivos CSV actualizados con datos de ejemplo')
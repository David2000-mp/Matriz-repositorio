import pandas as pd
from utils.analytics import estimate_reach, calculate_likes_promedio
from utils.data_saver import get_id, METRICAS_CSV, save_batch
from utils.data_manager import invalidate_caches
from utils.data_provider import data_provider
import os

print('START TEST')
# Test input (using existing catalog name 'Centro Universitario México' as substitute for X)
entidad = 'Centro Universitario México'
plataforma = 'Instagram'
seguidores = 10000
engagement_rate = 5.0

likes = calculate_likes_promedio(engagement_rate, seguidores)
est_reach = estimate_reach(plataforma, seguidores, engagement_rate)
print('Calculated likes:', likes)
print('Estimated reach:', est_reach)

# Build registro
usuario_red = ''
from datetime import datetime
fecha = pd.to_datetime('2026-01-01')

# Generate id
id_cuenta = get_id(entidad, plataforma, usuario_red)
print('Generated id_cuenta:', id_cuenta)

registro = {
    'id_cuenta': id_cuenta,
    'entidad': entidad,
    'plataforma': plataforma,
    'usuario_red': usuario_red,
    'fecha': fecha,
    'seguidores': int(seguidores),
    'alcance': int(est_reach),
    'interacciones': int(likes),
    'likes_promedio': float(likes),
    'engagement_rate': float(engagement_rate),
}

df = pd.DataFrame([registro])
print('DataFrame to save:\n', df.to_dict(orient='records'))

# Call save_batch
success = save_batch(df)
print('save_batch returned:', success)

# Check CSV content tail
if METRICAS_CSV.exists():
    print('\nMETRICAS_CSV exists at', METRICAS_CSV)
    tail = pd.read_csv(METRICAS_CSV, dtype={'id_cuenta': str}).tail(5)
    print('\nLast rows in CSV:\n', tail.to_dict(orient='records'))
else:
    print('METRICAS_CSV not found')

# Invalidate caches and check provider caches
invalidate_caches()
print('data_provider._data_cache is', getattr(data_provider, '_data_cache', None))
print('data_provider._merged_cache is', getattr(data_provider, '_merged_cache', None))

print('END TEST')

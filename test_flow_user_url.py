import pandas as pd
from utils.analytics import estimate_reach, calculate_likes_promedio
from utils.data_saver import get_id, METRICAS_CSV, save_batch
from utils.data_manager import invalidate_caches
from utils.data_provider import data_provider

print('START TEST URL')
entidad = 'Centro Universitario México'
plataforma = 'Instagram'
seguidores = 5000
engagement_rate = 3.0
usuario_red = 'https://instagram.com/testuser'

likes = calculate_likes_promedio(engagement_rate, seguidores)
est_reach = estimate_reach(plataforma, seguidores, engagement_rate)

id_cuenta = get_id(entidad, plataforma, usuario_red)
fecha = pd.to_datetime('2026-01-02')

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
print('DataFrame to save:', df.to_dict(orient='records'))
success = save_batch(df)
print('save_batch returned:', success)
if METRICAS_CSV.exists():
    tail = pd.read_csv(METRICAS_CSV, dtype={'id_cuenta': str}).tail(10)
    print('Last rows in CSV:')
    print(tail.to_dict(orient='records'))
else:
    print('METRICAS_CSV not found')

invalidate_caches()
print('After invalidate: data_provider._data_cache =', data_provider._data_cache)
print('After invalidate: data_provider._merged_cache =', data_provider._merged_cache)
print('END TEST URL')

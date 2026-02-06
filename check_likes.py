import pandas as pd

df = pd.read_csv('data/metricas.csv')
print('Estadísticas de likes_promedio:')
print(f'Max: {df["likes_promedio"].max():.2f}')
print(f'Min: {df["likes_promedio"].min():.2f}')
print(f'Valores > 0: {(df["likes_promedio"] > 0).sum()}/{len(df)}')
print()

print('Muestras con likes_promedio > 0:')
sample = df[df['likes_promedio'] > 0][['fecha', 'seguidores', 'engagement_rate', 'likes_promedio']].sample(5)
for _, row in sample.iterrows():
    calc = row['seguidores'] * (row['engagement_rate'] / 100)
    print(f'Fecha: {row["fecha"]}, Seg: {row["seguidores"]}, ER: {row["engagement_rate"]:.4f}, Likes: {row["likes_promedio"]:.2f} (calc: {calc:.2f})')
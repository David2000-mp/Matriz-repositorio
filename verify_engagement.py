import pandas as pd
df = pd.read_csv('data/metricas.csv')
print('Verificación final de engagement:')
print(f'Rango: {df["engagement_rate"].min():.4f} - {df["engagement_rate"].max():.4f}')
print(f'Promedio: {df["engagement_rate"].mean():.4f}')
print(f'Valores > 15: {(df["engagement_rate"] > 15).sum()}')
print(f'Valores = 0: {(df["engagement_rate"] == 0).sum()}')
print()
print('Muestra de datos originales:')
original = df[df['fecha'].str.match(r'^\d{4}-\d{2}-\d{2}$', na=False)]
sample = original[['id_cuenta', 'engagement_rate', 'seguidores']].head(5)
for _, row in sample.iterrows():
    print(f'{row["id_cuenta"][:30]}: ER={row["engagement_rate"]:.2f}, Seg={row["seguidores"]}')
import pandas as pd

df = pd.read_csv('data/metricas.csv')
print('=== VERIFICACIÓN DE CONCORDANCIA ===')
print(f'Total registros: {len(df)}')
print(f'Fechas únicas: {df["fecha"].nunique()}')
print(f'Rango de engagement_rate: {df["engagement_rate"].min():.4f} - {df["engagement_rate"].max():.4f}')
print(f'Valores > 15%: {(df["engagement_rate"] > 15).sum()}')
print(f'Valores = 0%: {(df["engagement_rate"] == 0).sum()}')
print()

# Verificar consistencia: interacciones ≈ (engagement_rate / 100) * alcance
df['interacciones_calculadas'] = ((df['engagement_rate'] / 100) * df['alcance']).round().astype(int)
diferencias = (df['interacciones'] - df['interacciones_calculadas']).abs()
print(f'Interacciones consistentes: {(diferencias <= 1).sum()}/{len(df)} registros')
print(f'Máxima diferencia en interacciones: {diferencias.max()}')
print()

# Verificar alcance = seguidores * 2.5
df['alcance_calculado'] = (df['seguidores'] * 2.5).round().astype(int)
alcance_correcto = (df['alcance'] == df['alcance_calculado']).sum()
print(f'Alcance correcto: {alcance_correcto}/{len(df)} registros')
print()

print('=== MUESTRAS DE CONCORDANCIA ===')
sample = df.sample(5)[['fecha', 'seguidores', 'alcance', 'interacciones', 'engagement_rate']]
for _, row in sample.iterrows():
    er_calc = (row['interacciones'] / row['alcance'] * 100) if row['alcance'] > 0 else 0
    print(f'Fecha: {row["fecha"]}, Seg: {row["seguidores"]}, Alc: {row["alcance"]}, Int: {row["interacciones"]}, ER: {row["engagement_rate"]:.4f} (calc: {er_calc:.4f})')
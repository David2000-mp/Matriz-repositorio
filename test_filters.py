from utils.data_provider import get_merged_data
import pandas as pd

print('Testing filters')
df = get_merged_data(force_reload=True)
print('Merged rows total:', len(df))
if 'entidad' in df.columns:
    df_filtrado = df[df['entidad']=='Centro Universitario México']
    print('Rows for Centro Universitario México:', len(df_filtrado))
    if not df_filtrado.empty:
        print(df_filtrado.tail(5).to_dict(orient='records'))
else:
    print('No columna entidad found')

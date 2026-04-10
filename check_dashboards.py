import pandas as pd
from utils.data_provider import data_provider

# Cargar datos usando data_provider
df_cuentas, df_metricas = data_provider.get_data()

print('=== VERIFICACIÓN DE DATOS PARA DASHBOARDS ===')
print(f'Cuentas cargadas: {len(df_cuentas)} filas')
print(f'Métricas cargadas: {len(df_metricas)} filas')

if not df_metricas.empty:
    # Hacer merge con cuentas para obtener información de plataforma
    df_merged = pd.merge(df_metricas, df_cuentas, on='id_cuenta', how='left')
    
    # Datos del último mes disponible para no depender del calendario real
    df_merged['fecha'] = pd.to_datetime(df_merged['fecha'], errors='coerce')
    available_periods = df_merged['fecha'].dropna().dt.to_period('M')
    latest_period = available_periods.max() if not available_periods.empty else None
    df_current = (
        df_merged[df_merged['fecha'].dt.to_period('M') == latest_period].copy()
        if latest_period is not None
        else pd.DataFrame()
    )

    print(f'Datos del último mes disponible ({latest_period}): {len(df_current)} filas')

    if not df_current.empty:
        # Convertir engagement_rate a numérico antes de agrupar
        df_current = df_current.copy()
        df_current['engagement_rate'] = pd.to_numeric(df_current['engagement_rate'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
        
        # Simular cálculo del dashboard
        platform_summary = df_current.groupby('plataforma').agg({
            'seguidores': 'max',
            'interacciones': 'sum',
            'engagement_rate': 'mean'
        }).reset_index()

        print('\nResumen por plataforma:')
        for _, row in platform_summary.iterrows():
            print(f'  {row["plataforma"]}: Engagement = {row["engagement_rate"]:.2f}%')

    # Verificar datos de comparación
    print('\nMuestra de engagement_rate por entidad:')
    sample = df_current[['id_cuenta', 'engagement_rate']].drop_duplicates().head(5)
    for _, row in sample.iterrows():
        print(f'  {row["id_cuenta"][:15]}...: ER = {row["engagement_rate"]:.2f}%')
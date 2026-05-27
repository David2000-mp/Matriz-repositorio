from utils.data_provider import data_provider
from utils.analytics import build_followers_growth_ranking
import pandas as pd
import numpy as np

def verify_rankings():
    print("--- Iniciando verificación de rankings (usando utils.analytics) ---")
    
    # 1) Cargar datos
    df = data_provider.get_merged_data(force_reload=False)
    
    # 2) Limpiar filas
    df = df.dropna(subset=['entidad', 'plataforma', 'fecha'])
    df['seguidores'] = pd.to_numeric(df['seguidores'], errors='coerce').fillna(0)
    
    # 3) Obtener candidatos con top_n grande
    df_growth = build_followers_growth_ranking(df, mode='monthly', top_n=5000)
    
    plataformas = df_growth['plataforma'].unique().tolist()
    
    results = []
    
    # Análisis por plataforma y General
    cases = [(p, p) for p in plataformas] + [('General', None)]
    
    for label, plat in cases:
        if plat is None:
            subset = df_growth.copy()
        else:
            subset = df_growth[df_growth['plataforma'] == plat].copy()
            
        if subset.empty:
            continue
            
        for metric in ['crecimiento_abs', 'crecimiento_pct']:
            # Lógica: Ordenar descendente y tomar los primeros 15
            full_sorted = subset.sort_values(by=metric, ascending=False)
            expected_ids = full_sorted.head(15)['entidad'].tolist()
            
            # Simulamos lo que el Dashboard mostraría: (sort + head(15))
            # Aquí lo que queremos validar es que si el usuario aplica la lógica actual sobre
            # el resultado de build_followers_growth_ranking(top_n=5000), obtiene los correctos.
            actual_ids = subset.sort_values(by=metric, ascending=False).head(15)['entidad'].tolist()
            
            is_pass = actual_ids == expected_ids
            
            diff = []
            if not is_pass:
                diff = list(set(expected_ids) - set(actual_ids))
            
            results.append({
                'Plataforma': label,
                'Metrica': metric,
                'Status': 'PASS' if is_pass else 'FAIL',
                'Size': len(subset),
                'Diff': diff
            })
            
    # 6) Imprimir resumen
    print(f"{'Plataforma':<15} | {'Métrica':<15} | {'Status':<6} | {'Tamaño':<6}")
    print("-" * 55)
    for res in results:
        print(f"{res['Plataforma']:<15} | {res['Metrica']:<15} | {res['Status']:<6} | {res['Size']:<6}")
        if res['Status'] == 'FAIL':
            print(f"   -> Discrepancias (esperadas pero no encontradas): {res['Diff']}")

if __name__ == '__main__':
    verify_rankings()

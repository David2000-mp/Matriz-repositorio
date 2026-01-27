"""
Script para generar datos de ejemplo más completos basados en COLEGIOS_MARISTAS
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.data_manager import COLEGIOS_MARISTAS

def generate_sample_data():
    """Genera datos de ejemplo para todas las instituciones Maristas"""

    # Fechas de los últimos 6 meses
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    dates = pd.date_range(start=start_date, end=end_date, freq='M')

    data_rows = []

    for entidad, plataformas in COLEGIOS_MARISTAS.items():
        for plataforma, usuario in plataformas.items():
            for date in dates:
                # Generar métricas aleatorias pero realistas
                base_followers = np.random.randint(500, 5000)
                seguidores = int(base_followers * (1 + np.random.normal(0, 0.1)))
                alcance = int(seguidores * np.random.uniform(2, 8))
                interacciones = int(alcance * np.random.uniform(0.05, 0.25))
                likes_promedio = np.random.randint(10, 100)
                engagement_rate = (interacciones / alcance) * 100 if alcance > 0 else 0

                data_rows.append({
                    'entidad': entidad,
                    'plataforma': plataforma,
                    'fecha': date.strftime('%Y-%m-%d'),
                    'seguidores': max(0, seguidores),
                    'alcance': max(0, alcance),
                    'interacciones': max(0, interacciones),
                    'likes_promedio': max(0, likes_promedio),
                    'engagement_rate': round(engagement_rate, 2)
                })

    # Crear DataFrame
    df = pd.DataFrame(data_rows)

    # Guardar como sample_upload_full.csv
    df.to_csv('data/sample_upload_full.csv', index=False)

    print(f"✅ Generados {len(df)} registros de ejemplo")
    print(f"Instituciones: {len(COLEGIOS_MARISTAS)}")
    print(f"Fechas: {len(dates)}")
    print(f"Total combinaciones: {len(COLEGIOS_MARISTAS) * len(dates)}")

    return df

if __name__ == "__main__":
    generate_sample_data()
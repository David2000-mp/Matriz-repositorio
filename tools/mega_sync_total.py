"""
Mega-sincronización total: limpia IDs, registra cuentas faltantes y sube todo a Google Sheets.
Procesa los 471 registros locales y sincroniza con Google Sheets en modo completo.
"""

import pandas as pd
from utils.data_loader import load_data, CUENTAS_CSV, METRICAS_CSV
from utils.data_saver import get_id, sync_cuentas_to_sheets, guardar_datos
from utils.logger import get_logger

logger = get_logger(__name__)

def mega_sync():
    print("=== [SYNC] INICIANDO MEGA-SINCRONIZACIÓN TOTAL ===")
    
    # 1. Cargar datos locales (los 471 registros)
    df_cuentas = pd.read_csv(CUENTAS_CSV)
    df_metricas = pd.read_csv(METRICAS_CSV)
    print(f"-> Datos locales detectados: {len(df_cuentas)} cuentas y {len(df_metricas)} metricas.")
    print(f"   Columnas en cuentas: {df_cuentas.columns.tolist()}")
    print(f"   Columnas en metricas: {df_metricas.columns.tolist()}")

    # 1.5 Merge para obtener entidad/plataforma/usuario_red en metricas
    print("-> Mergeando cuentas con metricas para obtener informacion completa...")
    df_metricas = df_metricas.merge(df_cuentas[['id_cuenta', 'entidad', 'plataforma', 'usuario_red']], 
                                     on='id_cuenta', how='left')
    print(f"   Merge completado. Nuevas columnas en metricas: {df_metricas.columns.tolist()}")
    
    # Limpiar NaN o valores nulos después del merge
    df_metricas['entidad'] = df_metricas['entidad'].fillna('Desconocida').astype(str)
    df_metricas['plataforma'] = df_metricas['plataforma'].fillna('Desconocida').astype(str)
    df_metricas['usuario_red'] = df_metricas['usuario_red'].fillna('Desconocido').astype(str)

    # 2. Corregir IDs "unknown" o vacíos
    print("-> Limpiando y regenerando IDs deterministicos...")
    for idx, row in df_metricas.iterrows():
        # Generamos el ID real basado en Entidad/Plataforma/Usuario
        real_id = get_id(row['entidad'], row['plataforma'], row['usuario_red'], df_cuentas)
        df_metricas.at[idx, 'id_cuenta'] = real_id

    # Aseguramos que la tabla de cuentas tenga todos estos IDs también
    for idx, row in df_metricas.iterrows():
        if row['id_cuenta'] not in df_cuentas['id_cuenta'].values:
            nueva_cuenta = pd.DataFrame([{
                'id_cuenta': row['id_cuenta'],
                'entidad': row['entidad'],
                'plataforma': row['plataforma'],
                'usuario_red': row['usuario_red']
            }])
            df_cuentas = pd.concat([df_cuentas, nueva_cuenta], ignore_index=True)

    df_cuentas = df_cuentas.drop_duplicates(subset=['id_cuenta'])

    # 3. LIMPIAR VALORES INVÁLIDOS (inf, -inf, NaN en floats)
    print("-> Limpiando valores anomalos (inf, NaN) en metricas...")
    numeric_cols = ['seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']
    for col in numeric_cols:
        if col in df_metricas.columns:
            df_metricas[col] = pd.to_numeric(df_metricas[col], errors='coerce')
            # Reemplazar inf y -inf con 0
            df_metricas[col] = df_metricas[col].replace([float('inf'), float('-inf')], 0)
            # Llenar NaN con 0
            df_metricas[col] = df_metricas[col].fillna(0)
    print(f"   [OK] Valores anomalos limpiados.")

    # 3.5 Guardar cambios localmente (METRICAS_CSV sin las columnas extra)
    print("-> Guardando cambios localmente...")
    df_cuentas.to_csv(CUENTAS_CSV, index=False)
    # Guardar solo las columnas originales de metricas
    original_metric_cols = ['id_cuenta', 'fecha', 'seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']
    df_metricas_save = df_metricas[original_metric_cols].copy()
    
    # Asegurar tipos de dato correctos
    df_metricas_save['fecha'] = pd.to_datetime(df_metricas_save['fecha'], errors='coerce').astype(str)
    for col in ['seguidores', 'alcance', 'interacciones', 'likes_promedio']:
        df_metricas_save[col] = pd.to_numeric(df_metricas_save[col], errors='coerce').fillna(0).astype(int)
    df_metricas_save['engagement_rate'] = pd.to_numeric(df_metricas_save['engagement_rate'], errors='coerce').fillna(0)
    
    # Reemplazar NaN uno mas con 0
    df_metricas_save = df_metricas_save.fillna(0)
    
    df_metricas_save.to_csv(METRICAS_CSV, index=False)
    print(f"   [OK] Archivos locales actualizados con IDs correctos.")
    print(f"      - {len(df_cuentas)} cuentas en cuentas.csv")
    print(f"      - {len(df_metricas_save)} metricas en metricas.csv")

    # 4. SUBIR A LA NUBE
    print("-> Sincronizando con Google Sheets (esto puede tardar)...")
    
    # Subir Cuentas
    success_c = sync_cuentas_to_sheets(df_cuentas)
    
    # Subir Metricas (usamos modo 'completo' para limpiar la basura actual)
    success_m = guardar_datos(df_metricas_save, modo="completo")

    if success_c and success_m:
        print("\n[EXITO TOTAL] Los 471 registros ya estan en la nube con IDs validos.")
    else:
        print("\n[ADVERTENCIA] Sincronizacion parcial. Revisa la conexion a Internet.")

if __name__ == "__main__":
    mega_sync()

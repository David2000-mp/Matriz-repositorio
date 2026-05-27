import pandas as pd
import os
from pathlib import Path
from utils.catalog import COLEGIOS_MARISTAS
from utils.data_saver import get_id, sync_cuentas_to_sheets, guardar_datos
from utils.engagement_validation import normalize_engagement_rate

# Ruta al CSV (asumiendo Downloads en Windows)
CSV_PATH = Path.home() / "Downloads" / "CAPTURA MANUAL DE LOS COLEGIOS (respuestas) - Respuestas de formulario 1.csv"

def extract_usuario_red(url: str) -> str:
    """Extrae el usuario_red del último parte de la URL sin @."""
    if not url or pd.isna(url):
        return "usuario_desconocido"
    url = str(url).strip()
    if url.startswith(("http://", "https://")):
        parts = url.rstrip("/").split("/")
        if len(parts) > 0:
            usuario = parts[-1]
        else:
            usuario = "usuario_desconocido"
    else:
        usuario = url
    if usuario.startswith("@"):
        usuario = usuario[1:]
    return usuario.lower().strip()

def main():
    if not CSV_PATH.exists():
        print(f"Error: CSV no encontrado en {CSV_PATH}")
        print("Por favor, coloca el archivo en la ruta especificada o ajusta CSV_PATH.")
        return

    # Leer CSV
    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8")
        print(f"CSV cargado exitosamente: {len(df)} filas.")
        df.columns = df.columns.str.strip()  # Quitar espacios en blanco de los nombres de columnas
        print(f"Columnas encontradas (después de strip): {df.columns.tolist()}")
    except Exception as e:
        print(f"Error leyendo CSV: {e}")
        return

    # Verificar columnas requeridas
    required_cols = ["Selecciona el colegio:", "Selecciona su Red Social", "Engagment:", "Seguidores", "FECHA DE CAPTURA"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Columnas faltantes en CSV: {missing_cols}")
        return

    # Mapear y procesar
    cuentas_list = []
    metricas_list = []
    processed = 0
    errors = 0

    for idx, row in df.iterrows():
        try:
            id_cuenta = None  # Placeholder para evitar errores de variable local
            entidad = str(row["Selecciona el colegio:"]).strip()
            plataforma = str(row["Selecciona su Red Social"]).strip()
            # Normalizar TikTok
            if plataforma.lower() == "tik tok":
                plataforma = "TikTok"
            engagement_raw = pd.to_numeric(row["Engagment:"], errors="coerce")
            seguidores = pd.to_numeric(row["Seguidores"], errors="coerce")
            # Limitar valores extremos
            if pd.isna(engagement_raw) or engagement_raw == float('inf') or engagement_raw == float('-inf'):
                engagement_raw = 0
            if pd.isna(seguidores) or seguidores == float('inf') or seguidores == float('-inf'):
                seguidores = 0
            seguidores = min(seguidores, 10000000)  # Limitar a 10M para evitar overflow
            engagement_raw = min(engagement_raw, 10000000)  # Limitar interacciones
            fecha_raw = str(row["FECHA DE CAPTURA"]).strip()
            # Convertir fecha a YYYY-MM-DD
            dt = pd.to_datetime(fecha_raw, errors="coerce")
            if pd.isna(dt):
                fecha = fecha_raw
            else:
                fecha = dt.strftime("%Y-%m-%d")

            # Calcular alcance estimado: seguidores * 2.5 (basado en lógica de data_entry.py)
            alcance = int(seguidores * 2.5) if not pd.isna(seguidores) else 0

            # Normalización canónica: engagement en porcentaje [0, 100]
            engagement_rate = normalize_engagement_rate(engagement_raw)

            # Calcular interacciones como: (engagement_rate / 100) * alcance
            interacciones = (engagement_rate / 100) * alcance if alcance > 0 and engagement_rate > 0 else 0

            # Buscar URL en catálogo
            usuario_red = "usuario_desconocido"
            if entidad in COLEGIOS_MARISTAS and plataforma in COLEGIOS_MARISTAS[entidad]:
                url = COLEGIOS_MARISTAS[entidad][plataforma]
                usuario_red = extract_usuario_red(url)
            else:
                print(f"Advertencia: Entidad '{entidad}' o plataforma '{plataforma}' no encontrada en catálogo. Usando placeholder.")

            # Generar id_cuenta
            id_cuenta = get_id(entidad, plataforma, usuario_red)

            # Agregar a listas
            cuentas_list.append({
                "id_cuenta": id_cuenta,
                "entidad": entidad,
                "plataforma": plataforma,
                "usuario_red": usuario_red
            })

            # Calcular likes_promedio por inferencia: seguidores * (engagement_rate / 100)
            likes_promedio = seguidores * (engagement_rate / 100) if seguidores > 0 and engagement_rate > 0 else 0.0
            likes_promedio = round(likes_promedio, 2)

            metricas_list.append({
                "id_cuenta": id_cuenta,
                "fecha": fecha,
                "seguidores": seguidores if not pd.isna(seguidores) else 0,
                "alcance": alcance,
                "interacciones": interacciones,
                "likes_promedio": likes_promedio,
                "engagement_rate": engagement_rate if not pd.isna(engagement_rate) else 0.0
            })

            processed += 1
            if processed % 10 == 0:
                print(f"Procesadas {processed} filas...")

        except Exception as e:
            print(f"Error procesando fila {idx}: {e}")
            errors += 1

    # Crear DataFrames
    df_cuentas = pd.DataFrame(cuentas_list).drop_duplicates(subset=["id_cuenta"])
    df_metricas = pd.DataFrame(metricas_list)

    print(f"Procesamiento completado: {processed} filas procesadas, {errors} errores.")
    print(f"Cuentas únicas: {len(df_cuentas)}")
    print(f"Métricas: {len(df_metricas)}")

    # Simulación de datos para rellenar fechas mensuales con interpolación lógica
    df_metricas['fecha'] = pd.to_datetime(df_metricas['fecha'], errors='coerce')
    df_metricas = df_metricas.dropna(subset=['fecha'])  # Eliminar filas con fechas inválidas
    df_metricas = df_metricas.sort_values(['id_cuenta', 'fecha'])

    simulated_list = []
    for id_cuenta, group in df_metricas.groupby('id_cuenta'):
        if len(group) < 2:
            continue  # No hay suficientes puntos para interpolar
        # Eliminar duplicados por fecha, mantener el último
        group = group.drop_duplicates(subset=['fecha'], keep='last')
        group = group.set_index('fecha')
        # Crear rango mensual desde min a max fecha
        date_range = pd.date_range(start=group.index.min(), end=group.index.max(), freq='MS')
        # Incluir las fechas reales en el reindex
        all_dates = sorted(set(date_range) | set(group.index))
        # Calcular el máximo engagement real antes de simular
        max_engagement_real = group['engagement_rate'].max()
        # Reindex y interpolate
        group_reindexed = group.reindex(all_dates)
        numeric_cols = ['seguidores', 'engagement_rate']
        group_reindexed[numeric_cols] = group_reindexed[numeric_cols].interpolate(method='linear')
        # Limitar engagement_rate al máximo real
        group_reindexed['engagement_rate'] = group_reindexed['engagement_rate'].clip(upper=max_engagement_real)
        # Mantener id_cuenta
        group_reindexed['id_cuenta'] = id_cuenta
        # Reset index
        group_reindexed = group_reindexed.reset_index().rename(columns={'index': 'fecha'})
        # Solo agregar las filas que no estaban en el original
        original_dates = set(group.index)
        simulated = group_reindexed[~group_reindexed['fecha'].isin(original_dates)]
        if not simulated.empty:
            simulated_list.append(simulated)

    # Concatenar datos simulados
    if simulated_list:
        df_simulated = pd.concat(simulated_list, ignore_index=True)
        df_metricas = pd.concat([df_metricas, df_simulated], ignore_index=True)

    # Recalcular alcance e interacciones basados en seguidores y engagement interpolados
    df_metricas['alcance'] = (df_metricas['seguidores'] * 2.5).fillna(0).astype(int)
    df_metricas['interacciones'] = ((df_metricas['engagement_rate'] / 100) * df_metricas['alcance']).fillna(0).astype(int)
    # Calcular likes_promedio por inferencia
    df_metricas['likes_promedio'] = (df_metricas['seguidores'] * (df_metricas['engagement_rate'] / 100)).fillna(0).round(2)

    # Ordenar y formatear
    df_metricas = df_metricas.sort_values(['id_cuenta', 'fecha']).reset_index(drop=True)
    df_metricas['fecha'] = df_metricas['fecha'].dt.strftime('%Y-%m-%d')

    print(f"Después de simulación: {len(df_metricas)} métricas totales")

    # Guardar cuentas
    if not df_cuentas.empty:
        success_cuentas = sync_cuentas_to_sheets(df_cuentas)
        if success_cuentas:
            print("Cuentas guardadas exitosamente en Google Sheets.")
        else:
            print("Error guardando cuentas en Google Sheets.")
    else:
        print("No hay cuentas para guardar.")

    # Guardar métricas
    if not df_metricas.empty:
        success_metricas = guardar_datos(df_metricas, modo="replace")
        if success_metricas:
            print("Métricas guardadas exitosamente.")
        else:
            print("Error guardando métricas.")
    else:
        print("No hay métricas para guardar.")

if __name__ == "__main__":
    main()
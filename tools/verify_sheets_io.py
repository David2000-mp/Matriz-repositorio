"""
Verifica escritura y lectura en Google Sheets sin borrar datos existentes.

Pasos:
- Crea un id de prueba y agrega una fila a 'cuentas' (append).
- Agrega una métrica asociada en 'metricas' usando guardar_datos(modo='append').
- Lee con load_data() y verifica que la métrica exista.

Salida por consola con resultados y conteos.
"""

from datetime import datetime
import os
import sys
import pandas as pd

# Asegurar que el proyecto esté en sys.path al ejecutar como script
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils import data_manager as dm
from utils.data_saver import guardar_datos


def main() -> int:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    test_id = f"verif_auto_{ts}"

    print("=== Verificación Sheets I/O (append-only) ===")
    print(f"ID de prueba: {test_id}")

    # 1) Asegurar presencia en 'cuentas' para que load_data no filtre la métrica
    try:
        ss = dm.conectar_sheets()
        if not ss:
            print("[ERROR] No fue posible conectar a Google Sheets")
            return 2
        ws_cuentas = ss.worksheet("cuentas")
        ws_cuentas.append_row([test_id, "Verificación Auto", "Test", "@verif_auto"])  # id, entidad, plataforma, usuario
        print("[OK] Fila de cuentas agregada (append)")
    except Exception as e:
        print(f"[ERROR] No se pudo agregar fila en 'cuentas': {e}")
        return 3

    # 2) Agregar métrica con guardar_datos en modo append (no borra nada)
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        df = pd.DataFrame(
            [{
                "id_cuenta": test_id,
                "fecha": today,
                "seguidores": 100,
                "alcance": 250,
                "interacciones": 10,
                "likes_promedio": 2.5,
                "engagement_rate": round((10/100)*100, 2),
            }]
        )
        ok = guardar_datos(df, modo="append")
        if not ok:
            print("[ERROR] guardar_datos retornó False al intentar append")
            return 4
        print("[OK] Métrica agregada (append)")
    except Exception as e:
        print(f"[ERROR] No se pudo agregar métrica: {e}")
        return 5

    # 3) Leer con load_data() y verificar presencia
    try:
        cuentas_df, metricas_df = dm.load_data()
        total_cuentas = len(cuentas_df)
        total_metricas = len(metricas_df)
        encontrados = metricas_df[metricas_df["id_cuenta"] == test_id]
        print(f"[INFO] Cuentas totales: {total_cuentas} | Métricas totales: {total_metricas}")
        print(f"[INFO] Registros del ID de prueba: {len(encontrados)}")
        if len(encontrados) >= 1:
            print("[OK] Lectura verificada: se encontró la métrica recién agregada")
            return 0
        else:
            print("[ERROR] No se encontró la métrica recién agregada")
            return 6
    except Exception as e:
        print(f"[ERROR] Fallo leyendo con load_data(): {e}")
        return 7


if __name__ == "__main__":
    raise SystemExit(main())

"""
Live Trace Diagnostics for Champilytics (no mocks)

This script performs:
1) Local write verification to METRICAS_CSV
2) Deterministic ID check using get_id() against 'cuentas' sheet
3) Google Sheets fire test: append a 'TEST_ELIMINAR' record to 'metricas'
4) Memory/cache trace on DataProvider.invalidate_cache()

Run with the project virtualenv (e.g., venv_stable).
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path

import pandas as pd

# Local imports (robust fallbacks)
try:
    from utils import data_manager as dm  # preferred source for dynamic paths and connectors
except Exception:
    dm = None  # type: ignore

try:
    from utils.data_loader import COLS_METRICAS, CUENTAS_CSV, METRICAS_CSV as METRICAS_CSV_DEFAULT
except Exception:
    COLS_METRICAS = [
        "id_cuenta", "fecha", "seguidores", "alcance",
        "interacciones", "likes_promedio", "engagement_rate",
        "entidad", "plataforma", "usuario_red"
    ]
    METRICAS_CSV_DEFAULT = Path("data/metricas.csv")
    CUENTAS_CSV = Path("data/cuentas.csv")

try:
    from utils.sheets_connector import conectar_sheets
except Exception:
    conectar_sheets = None  # type: ignore

try:
    from utils.data_saver import get_id
except Exception:
    get_id = None  # type: ignore

try:
    from utils.data_saver import guardar_datos as guardar_metricas
except Exception:
    guardar_metricas = None  # type: ignore

try:
    from utils.data_provider import DataProvider
except Exception:
    DataProvider = None  # type: ignore


def safe_exc_details(e: Exception) -> str:
    """Return detailed exception info including Windows-specific fields when available."""
    parts = [f"type={type(e).__name__}", f"msg={e}"]
    for attr in ("errno", "winerror", "strerror", "filename"):
        if hasattr(e, attr):
            parts.append(f"{attr}={getattr(e, attr)}")
    # Include full traceback last lines for context
    tb = traceback.format_exc(limit=3)
    parts.append(f"trace={tb.strip()}")
    return "; ".join(parts)


def get_metricas_csv_path() -> Path:
    """Resolve METRICAS_CSV path via data_manager if available, else default."""
    if dm is not None and hasattr(dm, "METRICAS_CSV"):
        return getattr(dm, "METRICAS_CSV")
    return METRICAS_CSV_DEFAULT


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"{title}")
    print("=" * 80)


def step1_local_write_verification():
    print_header("1) Verificación de Escritura Local en METRICAS_CSV")
    path = get_metricas_csv_path()
    try:
        abs_path = Path(path).resolve()
    except Exception:
        abs_path = Path(path)
    parent = abs_path.parent

    print(f"Ruta METRICAS_CSV: {abs_path}")
    print(f"Directorio padre existente: {parent.exists()} -> {parent}")
    print(f"Archivo existente antes: {abs_path.exists()}")

    before_rows = None
    if abs_path.exists():
        try:
            df_before = pd.read_csv(abs_path)
            before_rows = len(df_before)
        except Exception as e:
            print(f"ERROR al leer CSV existente: {safe_exc_details(e)}")
    print(f"Filas antes del intento de escritura: {before_rows}")

    # Create minimal test row matching COLS_METRICAS
    now = datetime.now()
    try:
        test_entidad = "PRUEBA_LOCAL"
        test_plataforma = "diagnostico"
        test_usuario = "test_user_local"
        if get_id is not None:
            test_id = get_id(test_entidad, test_plataforma, test_usuario)
        else:
            # simple fallback
            test_id = f"local-{now.strftime('%Y%m%d%H%M%S')}"

        # Build row
        row = {
            "id_cuenta": test_id,
            "fecha": now.strftime("%Y-%m-%d"),
            "seguidores": 0,
            "alcance": 0,
            "interacciones": 0,
            "likes_promedio": 0,
            "engagement_rate": 0.0,
            "entidad": test_entidad,
            "plataforma": test_plataforma,
            "usuario_red": test_usuario,
        }
        # Ensure all expected columns present
        for col in COLS_METRICAS:
            row.setdefault(col, pd.NA)
        df_test = pd.DataFrame([row])[COLS_METRICAS]

        print(f"Intentando escritura de 1 fila de prueba en {abs_path}")
        if abs_path.exists():
            # Append via concat to preserve headers order
            try:
                df_old = pd.read_csv(abs_path)
                combined = pd.concat([df_old, df_test], ignore_index=True)
                combined.to_csv(abs_path, index=False)
                print("Escritura por concatenación OK.")
            except Exception as e:
                print(f"ERROR al concatenar y guardar: {safe_exc_details(e)}")
        else:
            try:
                # Ensure directory exists
                parent.mkdir(parents=True, exist_ok=True)
                df_test.to_csv(abs_path, index=False)
                print("Archivo creado y escrito OK.")
            except Exception as e:
                print(f"ERROR de permisos/ruta al crear CSV: {safe_exc_details(e)}")
    except Exception as e:
        print(f"ERROR preparando DataFrame de prueba: {safe_exc_details(e)}")

    after_rows = None
    if abs_path.exists():
        try:
            df_after = pd.read_csv(abs_path)
            after_rows = len(df_after)
        except Exception as e:
            print(f"ERROR al leer CSV después de escribir: {safe_exc_details(e)}")
    print(f"Filas después del intento de escritura: {after_rows}")


def step2_deterministic_id_verification():
    print_header("2) Verificación de ID Determinístico contra hoja 'cuentas'")
    if conectar_sheets is None:
        print("ERROR: conectar_sheets() no disponible")
        return
    try:
        spreadsheet = conectar_sheets()
        if not spreadsheet:
            print("ERROR: No se pudo conectar a Google Sheets")
            return
        try:
            sheet_cuentas = spreadsheet.worksheet("cuentas")
        except Exception:
            print("ERROR: No existe hoja 'cuentas' en el Spreadsheet")
            return

        # Read all rows; expect header
        try:
            values = sheet_cuentas.get_all_values()
            print(f"Total de filas (incluye encabezado): {len(values)}")
            if not values:
                print("Hoja 'cuentas' vacía.")
                return
            header = values[0]
            rows = values[1:]
            df_cuentas = pd.DataFrame(rows, columns=header)
            print(f"Filas de datos en 'cuentas': {len(df_cuentas)}")
        except Exception as e:
            print(f"ERROR leyendo 'cuentas': {safe_exc_details(e)}")
            return

        if df_cuentas.empty:
            print("No hay registros en 'cuentas' para verificar.")
            return

        # Pick first real institution row
        sample = df_cuentas.iloc[0]
        entidad = str(sample.get("entidad", "")).strip()
        plataforma = str(sample.get("plataforma", "")).strip()
        usuario = str(sample.get("usuario_red", "")).strip()
        id_sheet = str(sample.get("id_cuenta", "")).strip()

        print(f"Ejemplo real: entidad='{entidad}', plataforma='{plataforma}', usuario='{usuario}', id_sheet='{id_sheet}'")

        if get_id is None:
            print("ERROR: get_id() no disponible para verificación")
            return
        try:
            id_calc = get_id(entidad, plataforma, usuario, df_cuentas_cache=df_cuentas)
            print(f"ID calculado (determinístico): {id_calc}")
            match = (id_calc == id_sheet)
            print(f"¿Coincide con 'id_cuenta' en Sheets?: {match}")
            exists_in_sheet = id_calc in set(df_cuentas.get("id_cuenta", []))
            print(f"¿ID calculado existe en hoja 'cuentas'?: {exists_in_sheet}")
        except Exception as e:
            print(f"ERROR calculando/verificando ID: {safe_exc_details(e)}")
    except Exception as e:
        print(f"ERROR conectando a Sheets en verificación de ID: {safe_exc_details(e)}")


def step3_google_sheets_fire_test():
    print_header("3) Prueba de Fuego: append 'TEST_ELIMINAR' en 'metricas'")
    if conectar_sheets is None:
        print("ERROR: conectar_sheets() no disponible")
        return
    try:
        spreadsheet = conectar_sheets()
        if not spreadsheet:
            print("ERROR: No se pudo conectar a Google Sheets")
            return
        try:
            sheet_metricas = spreadsheet.worksheet("metricas")
        except Exception:
            print("Hoja 'metricas' no existe, creando...")
            sheet_metricas = spreadsheet.add_worksheet(title="metricas", rows=2000, cols=max(10, len(COLS_METRICAS)))
            try:
                sheet_metricas.update([COLS_METRICAS])
            except Exception as e:
                print(f"WARN: No se pudo escribir encabezado en hoja nueva: {safe_exc_details(e)}")

        # Count rows before
        rows_before = None
        try:
            values_before = sheet_metricas.get_all_values()
            rows_before = len(values_before)
        except Exception as e:
            print(f"WARN: No se pudo leer filas antes: {safe_exc_details(e)}")
        print(f"Filas en 'metricas' antes: {rows_before}")

        # Build test record consistent with COLS_METRICAS
        now = datetime.now()
        entidad = "TEST_ELIMINAR"
        plataforma = "diagnostico"
        usuario = "test_user_gs"
        try:
            test_id = get_id(entidad, plataforma, usuario) if get_id else f"test-{now.strftime('%Y%m%d%H%M%S')}"
        except Exception as e:
            print(f"WARN: get_id() falló, usando id temporal: {safe_exc_details(e)}")
            test_id = f"test-{now.strftime('%Y%m%d%H%M%S')}"

        row = {
            "id_cuenta": test_id,
            "fecha": now.strftime("%Y-%m-%d"),
            "seguidores": 0,
            "alcance": 0,
            "interacciones": 0,
            "likes_promedio": 0,
            "engagement_rate": 0.0,
            "entidad": entidad,
            "plataforma": plataforma,
            "usuario_red": usuario,
        }
        # Order to match COLS_METRICAS
        data_list = [row.get(col, "") for col in COLS_METRICAS]

        print("Intentando append_row en hoja 'metricas'...")
        try:
            # Prefer append_rows if available in wrapper; else fallback to append_row
            if hasattr(sheet_metricas, "append_rows"):
                resp = sheet_metricas.append_rows([data_list])
            else:
                resp = sheet_metricas.append_row(data_list)
            print(f"Append resultado: {resp}")
        except Exception as e:
            emsg = str(e)
            print(f"ERROR en append: {safe_exc_details(e)}")
            if "429" in emsg or "quota" in emsg.lower() or "rate" in emsg.lower():
                print("Detectado posible error de cuota (429 / Rate Limit)")
            if "credential" in emsg.lower() or "permis" in emsg.lower() or "unauthorized" in emsg.lower():
                print("Detectado posible error de credenciales/permisos")

        # Count rows after
        rows_after = None
        try:
            values_after = sheet_metricas.get_all_values()
            rows_after = len(values_after)
        except Exception as e:
            print(f"WARN: No se pudo leer filas después: {safe_exc_details(e)}")
        print(f"Filas en 'metricas' después: {rows_after}")

    except Exception as e:
        print(f"ERROR conectando a Sheets en Prueba de Fuego: {safe_exc_details(e)}")


def step4_memory_cache_trace():
    print_header("4) Rastreo de Memoria: DataProvider.invalidate_cache()")
    if DataProvider is None:
        print("ERROR: DataProvider no disponible")
        return
    try:
        dp = DataProvider()
        print("Instanciado DataProvider.")

        # Helper to introspect cache-like attributes
        def cache_snapshot(obj):
            snap = {}
            for name in dir(obj):
                if "cache" in name.lower():
                    try:
                        val = getattr(obj, name)
                        snap[name] = None if val is None else (f"type={type(val).__name__}", "truthy" if bool(val) else "falsy")
                    except Exception:
                        snap[name] = "(inaccesible)"
            return snap

        # Before any save
        before_data = None
        try:
            df_merged = dp.get_merged_data()
            before_data = len(df_merged)
            print(f"get_merged_data() filas antes: {before_data}")
        except Exception as e:
            print(f"WARN: get_merged_data() falló antes: {safe_exc_details(e)}")

        print("Snapshot de caches ANTES de guardar:")
        print(cache_snapshot(dp))

        # Perform a save attempt using guardar_datos if available
        save_ok = None
        try:
            now = datetime.now()
            entidad = "TEST_ELIMINAR"
            plataforma = "diagnostico"
            usuario = "test_user_cache"
            test_id = get_id(entidad, plataforma, usuario) if get_id else f"test-{now.strftime('%Y%m%d%H%M%S')}"
            row = {
                "id_cuenta": test_id,
                "fecha": pd.to_datetime(now),
                "seguidores": 0,
                "alcance": 0,
                "interacciones": 0,
                "likes_promedio": 0,
                "engagement_rate": 0.0,
                "entidad": entidad,
                "plataforma": plataforma,
                "usuario_red": usuario,
            }
            for col in COLS_METRICAS:
                row.setdefault(col, pd.NA)
            df = pd.DataFrame([row])[COLS_METRICAS]

            if guardar_metricas is not None:
                print("Invocando guardar_datos() para activar flujos reales...")
                save_ok = guardar_metricas(df, modo="append")
                print(f"guardar_datos() retorno: {save_ok}")
            else:
                print("guardar_datos() no disponible; saltando guardado real.")
        except Exception as e:
            print(f"ERROR en guardar_datos(): {safe_exc_details(e)}")

        # Invalidate cache and check state
        try:
            print("Invocando dp.invalidate_cache()...")
            dp.invalidate_cache()
        except Exception as e:
            print(f"ERROR en invalidate_cache(): {safe_exc_details(e)}")

        print("Snapshot de caches DESPUÉS de invalidate_cache():")
        print(cache_snapshot(dp))

        # Check merged data again after invalidation
        after_data = None
        try:
            df_merged_after = dp.get_merged_data()
            after_data = len(df_merged_after)
            print(f"get_merged_data() filas después: {after_data}")
        except Exception as e:
            print(f"WARN: get_merged_data() falló después: {safe_exc_details(e)}")
    except Exception as e:
        print(f"ERROR creando/inspeccionando DataProvider: {safe_exc_details(e)}")


def main():
    print("Inicio live_trace_test.py — Diagnóstico en vivo (sin mocks)")
    print(f"Python: {sys.version}")
    try:
        import streamlit as st
        print(f"Streamlit: {st.__version__}")
    except Exception:
        print("Streamlit no disponible")
    print("-" * 80)

    step1_local_write_verification()
    step2_deterministic_id_verification()
    step3_google_sheets_fire_test()
    step4_memory_cache_trace()

    print("\nDiagnóstico completo. Revise los mensajes anteriores para detalles.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC TOOL - Google Sheets Connectivity
================================================
Script de diagnóstico exhaustivo para identificar problemas de conectividad.

Uso:
  python diagnostic_sheets.py                    # Diagnóstico completo
  python diagnostic_sheets.py --fix-cache        # Limpiar caché
  python diagnostic_sheets.py --validate-ids     # Validar IDs en Sheets
"""

import os
import sys
import json
from pathlib import Path
from typing import Tuple, Optional, Dict, List
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

RESULTS_FILE = Path(__file__).parent / "diagnostic_results.json"
COLORS = {
    "RESET": "\033[0m",
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
}


def colored(text: str, color: str) -> str:
    """Colorear texto para terminal."""
    if sys.platform == "win32":
        return text  # Windows no soporta ANSI codes fácilmente
    return f"{COLORS.get(color, '')}{text}{COLORS['RESET']}"


# ============================================================================
# PASO 1: VERIFICAR CREDENCIALES
# ============================================================================

def check_credentials() -> Dict[str, any]:
    """Verifica que las credenciales existan y sean válidas."""
    result = {
        "step": "Credenciales",
        "status": "❌ FALLO",
        "details": []
    }

    # 1.1 - Verificar .env
    result["details"].append("\n📄 Verificando .env...")
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        result["details"].append("✅ Archivo .env existe")

        with open(env_path, "r") as f:
            env_content = f.read()

        # Verificar variables críticas
        critical_vars = [
            "GOOGLE_SHEETS_ID",
            "GCP_PRIVATE_KEY",
            "GCP_CLIENT_EMAIL",
            "GCP_PROJECT_ID"
        ]

        for var in critical_vars:
            if var in env_content:
                value = os.getenv(var, "")
                if value and not any(placeholder in value for placeholder in ["TU_", "tu-"]):
                    result["details"].append(f"  ✅ {var}: Configurado")
                else:
                    result["details"].append(f"  ❌ {var}: Vacío o placeholder")
                    result["status"] = "⚠️ INCOMPLETO"
            else:
                result["details"].append(f"  ❌ {var}: No encontrado en .env")
    else:
        result["details"].append("❌ Archivo .env NO existe")
        result["details"].append("   Solución: Crear .env basado en .env.example")

    # 1.2 - Verificar secrets.toml
    result["details"].append("\n📄 Verificando .streamlit/secrets.toml...")
    secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        result["details"].append("✅ Archivo secrets.toml existe")

        with open(secrets_path, "r") as f:
            secrets_content = f.read()

        if "gcp_service_account" in secrets_content:
            result["details"].append("  ✅ Sección [gcp_service_account] encontrada")
        else:
            result["details"].append("  ❌ Sección [gcp_service_account] NO encontrada")

        if "google_sheets_id" in secrets_content:
            result["details"].append("  ✅ Variable google_sheets_id encontrada")
        else:
            result["details"].append("  ⚠️ Variable google_sheets_id NO encontrada (pero podría estar en .env)")
    else:
        result["details"].append("⚠️ Archivo secrets.toml NO existe (es opcional si usas .env)")

    # 1.3 - Intentar cargar como JSON
    result["details"].append("\n🔐 Validando estructura de credenciales...")
    try:
        sheets_id = os.getenv("GOOGLE_SHEETS_ID")
        if not sheets_id:
            result["details"].append("  ❌ GOOGLE_SHEETS_ID vacío")
        else:
            result["details"].append(f"  ✅ GOOGLE_SHEETS_ID: {sheets_id[:20]}...")

        pk = os.getenv("GCP_PRIVATE_KEY")
        if not pk or "TU_PRIVATE_KEY" in pk:
            result["details"].append("  ❌ GCP_PRIVATE_KEY inválida")
        else:
            if "-----BEGIN PRIVATE KEY-----" in pk:
                result["details"].append("  ✅ GCP_PRIVATE_KEY: Formato válido")
                result["status"] = "✅ PASÓ"
            else:
                result["details"].append("  ❌ GCP_PRIVATE_KEY: Formato inválido")

    except Exception as e:
        result["details"].append(f"  ❌ Error validando: {e}")

    return result


# ============================================================================
# PASO 2: VERIFICAR CONECTIVIDAD A GOOGLE SHEETS API
# ============================================================================

def check_api_connection() -> Dict[str, any]:
    """Intenta conectarse a Google Sheets API."""
    result = {
        "step": "Conectividad API",
        "status": "❌ FALLO",
        "details": []
    }

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        result["details"].append("✅ Librerías requeridas (gspread, google-auth) disponibles")

        # Obtener credenciales
        result["details"].append("\n🔑 Intentando obtener credenciales...")

        # Opción 1: JSON completo en env
        sa_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
        if sa_json:
            try:
                creds_dict = json.loads(sa_json)
                result["details"].append("  ✅ Credenciales desde GCP_SERVICE_ACCOUNT_JSON")
            except json.JSONDecodeError:
                result["details"].append("  ❌ GCP_SERVICE_ACCOUNT_JSON: JSON inválido")
                creds_dict = None
        else:
            # Opción 2: Variables individuales
            pk = os.getenv("GCP_PRIVATE_KEY")
            client_email = os.getenv("GCP_CLIENT_EMAIL")
            project_id = os.getenv("GCP_PROJECT_ID")
            pk_id = os.getenv("GCP_PRIVATE_KEY_ID")

            if all([pk, client_email, project_id, pk_id]):
                creds_dict = {
                    "type": "service_account",
                    "private_key": pk.replace('\\n', '\n'),
                    "client_email": client_email,
                    "project_id": project_id,
                    "private_key_id": pk_id,
                }
                result["details"].append("  ✅ Credenciales desde variables de entorno")
            else:
                result["details"].append("  ❌ Variables de entorno incompletas")
                creds_dict = None

        if not creds_dict:
            result["details"].append("❌ No se pudieron cargar credenciales")
            return result

        # Intentar autenticación
        result["details"].append("\n🔐 Intentando autenticación OAuth2...")
        try:
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
            result["details"].append("  ✅ Autenticación exitosa")
        except Exception as e:
            result["details"].append(f"  ❌ Error en autenticación: {e}")
            return result

        # Intentar conectar a API
        result["details"].append("\n📡 Conectando a Google Sheets API...")
        try:
            gc = gspread.authorize(creds)
            result["details"].append("  ✅ Cliente gspread autorizado")
        except Exception as e:
            result["details"].append(f"  ❌ Error autorizando gspread: {e}")
            return result

        # Intentar abrir spreadsheet
        result["details"].append("\n📊 Intentando abrir Spreadsheet...")
        sheets_id = os.getenv("GOOGLE_SHEETS_ID")
        if not sheets_id:
            result["details"].append("  ❌ GOOGLE_SHEETS_ID no configurado")
            return result

        try:
            spreadsheet = gc.open_by_key(sheets_id)
            result["details"].append(f"  ✅ Spreadsheet abierto: {spreadsheet.title}")
            result["status"] = "✅ PASÓ"
            return result, spreadsheet
        except gspread.exceptions.SpreadsheetNotFound:
            result["details"].append(f"  ❌ Spreadsheet NO ENCONTRADO: ID inválido")
        except Exception as e:
            result["details"].append(f"  ❌ Error abriendo spreadsheet: {e}")

    except ImportError:
        result["details"].append("❌ Falta instalar dependencias: pip install gspread google-auth")

    return result


# ============================================================================
# PASO 3: VERIFICAR ESTRUCTURA DE HOJAS
# ============================================================================

def check_sheets_structure(spreadsheet) -> Dict[str, any]:
    """Verifica que las hojas requeridas existan y tengan las columnas correctas."""
    result = {
        "step": "Estructura de Sheets",
        "status": "✅ PASÓ",
        "details": []
    }

    required_sheets = {
        "cuentas": ["id_cuenta", "entidad", "plataforma", "usuario_red"],
        "metricas": ["id_cuenta", "fecha", "seguidores", "alcance", "interacciones", "likes_promedio", "engagement_rate"],
        "config": ["entidad", "meta_seguidores", "meta_engagement"],
        "comentarios": ["entidad", "mes", "comentario"],
        "usernames_editados": ["entidad", "plataforma", "usuario_editado", "fecha_modificacion"]
    }

    for sheet_name, expected_cols in required_sheets.items():
        try:
            ws = spreadsheet.worksheet(sheet_name)
            records = ws.get_all_records()

            result["details"].append(f"\n📋 Hoja '{sheet_name}':")
            result["details"].append(f"  ✅ Existe ({len(records)} registros)")

            if records:
                actual_cols = list(records[0].keys())
                missing_cols = [c for c in expected_cols if c not in actual_cols]

                if missing_cols:
                    result["details"].append(f"  ⚠️ Columnas faltantes: {missing_cols}")
                    result["status"] = "⚠️ INCOMPLETO"
                else:
                    result["details"].append(f"  ✅ Todas las columnas presentes")
        except Exception as e:
            result["details"].append(f"\n📋 Hoja '{sheet_name}':")
            result["details"].append(f"  ❌ Error: {e}")
            result["status"] = "⚠️ INCOMPLETO"

    return result


# ============================================================================
# PASO 4: VERIFICAR IDs
# ============================================================================

def validate_ids(spreadsheet) -> Dict[str, any]:
    """Verifica que los IDs tengan el formato esperado."""
    result = {
        "step": "Validación de IDs",
        "status": "✅ PASÓ",
        "details": []
    }

    try:
        ws = spreadsheet.worksheet("cuentas")
        records = ws.get_all_records()

        if not records:
            result["details"].append("⚠️ Hoja 'cuentas' está vacía")
            return result

        result["details"].append(f"\n📋 Analizando {len(records)} registros en 'cuentas'...\n")

        invalid_ids = []
        for idx, record in enumerate(records):
            id_cuenta = str(record.get("id_cuenta", "")).strip()

            # Validar que sea 8 caracteres hex
            if len(id_cuenta) != 8:
                invalid_ids.append((idx + 2, id_cuenta, "Largo != 8"))
                continue

            try:
                int(id_cuenta, 16)  # Validar hex
            except ValueError:
                invalid_ids.append((idx + 2, id_cuenta, "No es hex válido"))

        if invalid_ids:
            result["details"].append(f"  ❌ {len(invalid_ids)} IDs inválidos encontrados:")
            for row, id_val, reason in invalid_ids[:5]:  # Mostrar primeros 5
                result["details"].append(f"    - Fila {row}: '{id_val}' ({reason})")
            if len(invalid_ids) > 5:
                result["details"].append(f"    ... y {len(invalid_ids) - 5} más")
            result["status"] = "⚠️ ADVERTENCIA"
        else:
            result["details"].append(f"  ✅ Todos los {len(records)} IDs son válidos")

    except Exception as e:
        result["details"].append(f"  ❌ Error validando IDs: {e}")
        result["status"] = "⚠️ NO PUDO VALIDAR"

    return result


# ============================================================================
# PASO 5: VERIFICAR CACHÉ
# ============================================================================

def check_cache() -> Dict[str, any]:
    """Verifica estado del caché de Streamlit."""
    result = {
        "step": "Estado de Caché",
        "status": "✅ PASÓ",
        "details": []
    }

    # Buscar archivos de caché
    cache_paths = [
        Path.home() / ".streamlit" / "cache",
        Path(__file__).parent / ".streamlit" / "cache",
        Path(__file__).parent / "__pycache__"
    ]

    result["details"].append("\n🗂️ Ubicaciones de caché:")
    total_cache_size = 0

    for cache_path in cache_paths:
        if cache_path.exists():
            size = sum(f.stat().st_size for f in cache_path.rglob("*") if f.is_file())
            total_cache_size += size
            result["details"].append(f"  📁 {cache_path}: {size / 1024:.1f} KB")

    if total_cache_size > 10 * 1024 * 1024:  # 10 MB
        result["details"].append(f"\n⚠️ Caché grande ({total_cache_size / 1024 / 1024:.1f} MB)")
        result["details"].append("  Sugerencia: Ejecutar con --fix-cache para limpiar")
        result["status"] = "⚠️ ADVERTENCIA"

    return result


# ============================================================================
# PASO 6: GENERAR REPORTE
# ============================================================================

def print_report(results: List[Dict]) -> None:
    """Imprime reporte formateado."""
    print("\n" + "=" * 80)
    print(colored("🔍 REPORTE DE DIAGNÓSTICO - GOOGLE SHEETS CONNECTIVITY", "CYAN"))
    print(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    overall_status = "✅ TODAS LAS PRUEBAS PASARON"
    for result in results:
        if "FALLO" in result.get("status", ""):
            overall_status = "❌ ERRORES CRÍTICOS ENCONTRADOS"
            break
        elif "INCOMPLETO" in result.get("status", ""):
            overall_status = "⚠️ PROBLEMAS ENCONTRADOS"

    print(f"\n📊 Estado general: {colored(overall_status, 'GREEN' if '✅' in overall_status else 'RED')}\n")

    for result in results:
        status_color = 'GREEN' if '✅' in result['status'] else ('YELLOW' if '⚠️' in result['status'] else 'RED')
        print(f"\n{colored(result['step'], 'BLUE')}")
        print(f"Estado: {colored(result['status'], status_color)}")

        for detail in result['details']:
            print(f"  {detail}")

    # Guardar resultados en JSON
    with open(RESULTS_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "results": results
        }, f, indent=2)

    print(f"\n💾 Resultados guardados en: {RESULTS_FILE}")
    print("\n" + "=" * 80 + "\n")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Ejecuta diagnóstico completo."""
    import argparse

    parser = argparse.ArgumentParser(description="Diagnóstico de conectividad con Google Sheets")
    parser.add_argument("--fix-cache", action="store_true", help="Limpiar caché de Streamlit")
    parser.add_argument("--validate-ids", action="store_true", help="Validar IDs en Sheets")
    args = parser.parse_args()

    if args.fix_cache:
        print("🧹 Limpiando caché de Streamlit...")
        import shutil
        cache_paths = [
            Path.home() / ".streamlit" / "cache",
            Path(__file__).parent / ".streamlit" / "cache",
        ]
        for cache_path in cache_paths:
            if cache_path.exists():
                try:
                    shutil.rmtree(cache_path)
                    print(f"  ✅ Eliminado: {cache_path}")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
        return

    # Ejecutar diagnóstico
    results = []

    # Paso 1: Credenciales
    print("\n[1/5] Verificando credenciales...")
    results.append(check_credentials())

    # Paso 2: Conectividad
    print("[2/5] Verificando conectividad a API...")
    api_result = check_api_connection()
    if isinstance(api_result, tuple):
        api_result, spreadsheet = api_result
        results.append(api_result)

        # Paso 3: Estructura
        print("[3/5] Verificando estructura de Sheets...")
        results.append(check_sheets_structure(spreadsheet))

        # Paso 4: IDs
        print("[4/5] Validando IDs...")
        results.append(validate_ids(spreadsheet))
    else:
        results.append(api_result)
        spreadsheet = None

    # Paso 5: Caché
    print("[5/5] Verificando caché...")
    results.append(check_cache())

    # Generar reporte
    print_report(results)


if __name__ == "__main__":
    main()

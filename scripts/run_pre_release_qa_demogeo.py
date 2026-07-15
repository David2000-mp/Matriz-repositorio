"""Pre-release QA checks for Demographic and Geographic module.

Usage:
  python scripts/run_pre_release_qa_demogeo.py
  python scripts/run_pre_release_qa_demogeo.py --with-sheets
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
APP_FILE = ROOT / "app_refactored.py"
VIEW_FILE = ROOT / "views" / "demographic_geographic_analysis.py"
CHECKLIST_FILE = ROOT / "CHECKLIST_QA_DEMOGRAFICO_GEOGRAFICO.md"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def _version_tuple(version_text: str) -> tuple[int, ...]:
    parts = []
    for token in str(version_text).split("."):
        digits = ""
        for ch in token:
            if ch.isdigit():
                digits += ch
            else:
                break
        if digits == "":
            parts.append(0)
        else:
            parts.append(int(digits))
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def _run_check(name: str, fn: Callable[[], tuple[bool, str]]) -> CheckResult:
    try:
        ok, detail = fn()
        return CheckResult(name=name, ok=bool(ok), detail=detail)
    except Exception as exc:
        return CheckResult(name=name, ok=False, detail=f"Exception: {exc}")


def check_venv() -> tuple[bool, str]:
    exe = sys.executable.replace("\\", "/").lower()
    in_venv = "/.venv/" in exe or exe.endswith("/.venv/scripts/python.exe")
    return in_venv, f"python={sys.executable}"


def check_required_modules() -> tuple[bool, str]:
    required = ["streamlit", "pandas", "plotly", "openpyxl"]
    found = {}

    for mod in required:
        module = importlib.import_module(mod)
        found[mod] = getattr(module, "__version__", "unknown")

    openpyxl_ver = _version_tuple(found["openpyxl"])
    min_ver = (3, 1, 5)
    if openpyxl_ver < min_ver:
        return False, f"openpyxl={found['openpyxl']} < 3.1.5"

    detail = ", ".join(f"{k}={v}" for k, v in found.items())
    return True, detail


def check_files_exist() -> tuple[bool, str]:
    required_files = [APP_FILE, VIEW_FILE, CHECKLIST_FILE]
    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    if missing:
        return False, f"Missing files: {', '.join(missing)}"
    return True, "app/view/checklist presentes"


def check_navigation_wiring() -> tuple[bool, str]:
    content = APP_FILE.read_text(encoding="utf-8")
    menu_ok = "Analisis Demografico y Geografico" in content
    route_ok = 'elif selected == "Analisis Demografico y Geografico":' in content
    render_ok = "render_demographic_geographic_analysis()" in content
    ok = menu_ok and route_ok and render_ok
    return ok, f"menu={menu_ok}, route={route_ok}, render={render_ok}"


def check_core_logic() -> tuple[bool, str]:
    import pandas as pd

    from utils.demographics_geo import (
        build_city_report,
        build_demography_base,
        build_network_comparison,
    )

    df = pd.DataFrame(
        {
            "fecha_reporte": ["2026-07-01"] * 8,
            "colegio": [
                "Colegio A",
                "Colegio A",
                "Colegio A",
                "Colegio A",
                "Colegio B",
                "Colegio B",
                "Colegio B",
                "Colegio B",
            ],
            "plataforma": ["Instagram"] * 8,
            "criterio": [
                "Demografia base",
                "Demografia base",
                "Ciudad",
                "Ciudad",
                "Demografia base",
                "Demografia base",
                "Ciudad",
                "Ciudad",
            ],
            "sexo": ["Hombres", "Mujeres", "", "", "Hombres", "Mujeres", "", ""],
            "edad": ["18-24", "18-24", "", "", "18-24", "18-24", "", ""],
            "ubicacion": ["", "", "Guadalajara", "Ciudad Desconocida", "", "", "Monterrey", "Otra Ciudad"],
            "valor": [120, 130, 80, 20, 100, 110, 70, 30],
        }
    )

    demo = build_demography_base(df)
    mapped, unmapped = build_city_report(df)
    comp = build_network_comparison(df, "Colegio A")

    cond_demo = (not demo.empty) and int(demo["valor"].sum()) == 460
    cond_city = (not mapped.empty) and (not unmapped.empty)
    cond_rule = (not comp.empty) and int(comp["red_valor"].sum()) == 210

    ok = cond_demo and cond_city and cond_rule
    detail = f"demo={cond_demo}, city={cond_city}, exclusion_rule={cond_rule}"
    return ok, detail


def check_sheets(optional: bool = False) -> tuple[bool, str]:
    if not optional:
        return True, "skipped (--with-sheets no especificado)"

    from utils.sheets_connector import get_sheets_connection

    ss = get_sheets_connection()
    if not ss:
        return False, "No se pudo conectar a Google Sheets"

    expected = {"Base_Maestra_Colegios", "Base_Demografica_Colegios"}
    existing = {ws.title for ws in ss.worksheets()}
    missing = sorted(expected - existing)

    if missing:
        return False, f"Hojas faltantes: {', '.join(missing)}"

    return True, "Conexion y hojas requeridas OK"


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-release QA checks for demogeo module")
    parser.add_argument(
        "--with-sheets",
        action="store_true",
        help="Ejecuta checks de conexion real a Google Sheets",
    )
    args = parser.parse_args()

    os.chdir(ROOT)

    checks = [
        _run_check("Entorno .venv", check_venv),
        _run_check("Dependencias criticas", check_required_modules),
        _run_check("Archivos obligatorios", check_files_exist),
        _run_check("Wiring de navegacion", check_navigation_wiring),
        _run_check("Logica critica modulo", check_core_logic),
        _run_check("Google Sheets", lambda: check_sheets(optional=args.with_sheets)),
    ]

    print("\n=== PRE-RELEASE QA: DEMOGRAFICO-GEOGRAFICO ===")
    for result in checks:
        status = "PASS" if result.ok else "FAIL"
        print(f"[{status}] {result.name}: {result.detail}")

    passed = sum(1 for r in checks if r.ok)
    total = len(checks)
    print(f"\nResumen: {passed}/{total} checks exitosos")

    if passed != total:
        print("Resultado final: FALLA")
        return 1

    print("Resultado final: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

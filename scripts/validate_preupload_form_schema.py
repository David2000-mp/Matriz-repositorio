#!/usr/bin/env python3
"""Validacion pre-subida para la nueva estructura de formulario de Google Sheets."""

from __future__ import annotations

import sys
from typing import Dict, List
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.form_response_importer import _build_header_groups, import_form_responses
from utils.schema_columns import COLS_METRICAS
from utils.sheets_connector import get_sheets_connection


REQUIRED_NEW_FORM_FIELDS = [
    "calificacion_redes",
    "tipo_contenido_mas_viral",
    "publicacion_mas_viral_numeros",
    "calificacion_contenido",
    "plataforma_desglose_profundo",
    "comentarios_video_viral",
    "media_interaccion",
    "se_considera_viral_280",
    "publicacion_mas_interacciones",
    "se_considera_viral_250",
    "novedoso_video_viral",
    "calificacion_diseno",
    "publicacion_destacada",
]

CRITICAL_FIELDS = ["id_cuenta", "fecha", "entidad", "plataforma", "seguidores", "engagement_rate"]


def _print_result(ok: bool, message: str) -> bool:
    icon = "OK" if ok else "FAIL"
    print(f"[{icon}] {message}")
    return ok


def _validate_columns(header_groups: Dict[str, List[int]], metricas_df: pd.DataFrame) -> bool:
    status = True

    # Validar que el formulario tenga todas las columnas nuevas (via aliases canónicos)
    missing_form = [field for field in REQUIRED_NEW_FORM_FIELDS if not header_groups.get(field)]
    status &= _print_result(not missing_form, f"Campos nuevos presentes en formulario: faltantes={missing_form}")

    # Validar columnas del DataFrame de métricas mapeado
    missing_metric_cols = [col for col in COLS_METRICAS if col not in metricas_df.columns]
    status &= _print_result(not missing_metric_cols, f"Columnas de salida presentes en metricas_df: faltantes={missing_metric_cols}")

    return status


def _validate_critical_rows(cuentas_df: pd.DataFrame, metricas_df: pd.DataFrame) -> bool:
    status = True
    merged = metricas_df.merge(cuentas_df[["id_cuenta", "entidad", "plataforma"]], on="id_cuenta", how="left")

    empty_mask = pd.Series(False, index=merged.index)
    for col in CRITICAL_FIELDS:
        if col not in merged.columns:
            status &= _print_result(False, f"Campo critico ausente: {col}")
            continue

        # Para strings, vacío o NaN es inválido.
        if col in {"id_cuenta", "entidad", "plataforma"}:
            invalid = merged[col].astype(str).str.strip().eq("") | merged[col].isna()
        else:
            invalid = merged[col].isna()
        empty_mask = empty_mask | invalid

    empty_rows = int(empty_mask.sum())
    status &= _print_result(empty_rows == 0, f"Filas con campos criticos vacios: {empty_rows}")
    return status


def _validate_dtypes(metricas_df: pd.DataFrame) -> bool:
    status = True

    fecha_parsed = pd.to_datetime(metricas_df["fecha"], errors="coerce")
    invalid_fecha = int(fecha_parsed.isna().sum())
    status &= _print_result(invalid_fecha == 0, f"Fechas validas: invalidas={invalid_fecha}")

    int_like_cols = ["seguidores", "alcance", "interacciones"]
    float_like_cols = [
        "likes_promedio",
        "engagement_rate",
        "media_visualizaciones",
        "engagement_contenido_imagenes",
        "engagement_contenido_links",
        "engagement_contenido_videos",
        "engagement_tema_mas_visto",
        "publicaciones_por_semana",
        "calificacion_redes",
        "publicacion_mas_viral_numeros",
        "calificacion_contenido",
        "media_interaccion",
        "calificacion_diseno",
    ]

    for col in int_like_cols + float_like_cols:
        if col not in metricas_df.columns:
            status &= _print_result(False, f"Columna numerica ausente: {col}")
            continue
        parsed = pd.to_numeric(metricas_df[col], errors="coerce")
        invalid = int(parsed.isna().sum())
        status &= _print_result(invalid == 0, f"Tipo numerico valido en {col}: invalidos={invalid}")

    return status


def main() -> int:
    print("=" * 80)
    print("VALIDACION PRE-SUBIDA: NUEVO FORM SCHEMA")
    print("=" * 80)

    spreadsheet = get_sheets_connection()
    if not spreadsheet:
        print("[FAIL] No se pudo conectar a Google Sheets")
        return 2

    ws = spreadsheet.worksheet("Respuestas de formulario 3")
    raw_data = ws.get()
    if not raw_data or len(raw_data) < 2:
        print("[FAIL] Formulario vacio o sin datos")
        return 3

    headers = [str(h or "").strip() for h in raw_data[0]]
    header_groups = _build_header_groups(headers)

    cuentas_df, metricas_df = import_form_responses(spreadsheet)
    if cuentas_df.empty or metricas_df.empty:
        print("[FAIL] import_form_responses devolvio DataFrames vacios")
        return 4

    status = True
    status &= _validate_columns(header_groups, metricas_df)
    status &= _validate_critical_rows(cuentas_df, metricas_df)
    status &= _validate_dtypes(metricas_df)

    # Check recomendado: duplicados por id_cuenta + fecha
    duplicated = int(metricas_df.duplicated(subset=["id_cuenta", "fecha"], keep=False).sum())
    status &= _print_result(duplicated == 0, f"Duplicados por id_cuenta+fecha: {duplicated}")

    # Check recomendado: rango engagement
    er = pd.to_numeric(metricas_df["engagement_rate"], errors="coerce")
    out_of_range = int(((er < 0) | (er > 100) | er.isna()).sum())
    status &= _print_result(out_of_range == 0, f"engagement_rate fuera de [0,100]: {out_of_range}")

    # Reporte nulos por columna (informativo)
    print("\nResumen nulos por columna (top 15):")
    nulls = metricas_df.isna().sum().sort_values(ascending=False).head(15)
    for col, count in nulls.items():
        print(f" - {col}: {int(count)}")

    print("\n" + "=" * 80)
    if status:
        print("VALIDACION EXITOSA")
        return 0

    print("VALIDACION FALLIDA")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

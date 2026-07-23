"""Contratos de entrega y calidad para tablas analíticas de Fase 4."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

import pandas as pd


DATE_CANDIDATES = ("fecha", "fecha_reporte", "month_date", "month_key")


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serializa exactamente las filas/columnas recibidas en CSV UTF-8 con BOM."""
    local = df.copy() if df is not None else pd.DataFrame()
    return local.to_csv(index=False).encode("utf-8-sig")


def safe_file_stem(value: str) -> str:
    """Genera un nombre portable sin alterar los datos exportados."""
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value).strip()).strip("_")
    return normalized.lower() or "datos_grafica"


def _missing_mask(df: pd.DataFrame) -> pd.DataFrame:
    mask = df.isna()
    for column in df.columns:
        if pd.api.types.is_object_dtype(df[column]) or isinstance(
            df[column].dtype, pd.StringDtype
        ):
            mask[column] = mask[column] | df[column].astype(str).str.strip().eq("")
    return mask


def _date_quality(df: pd.DataFrame) -> tuple[int, str, str]:
    for column in DATE_CANDIDATES:
        if column not in df.columns:
            continue
        raw = df[column]
        parsed = pd.to_datetime(
            raw.astype(str) + ("-01" if column == "month_key" else ""),
            errors="coerce",
            format="mixed",
        )
        non_empty = raw.notna() & raw.astype(str).str.strip().ne("")
        invalid = int((non_empty & parsed.isna()).sum())
        valid = parsed.dropna()
        if valid.empty:
            return invalid, "", ""
        return invalid, valid.min().date().isoformat(), valid.max().date().isoformat()
    return 0, "", ""


def build_quality_report(
    sources: Mapping[str, pd.DataFrame],
    required_columns: Mapping[str, Sequence[str]] | None = None,
) -> pd.DataFrame:
    """Resume cobertura, vacíos, duplicados y anomalías sin modificar las fuentes."""
    rows: list[dict[str, object]] = []
    required_columns = required_columns or {}

    for source_name, frame in sources.items():
        df = frame.copy() if frame is not None else pd.DataFrame()
        total_cells = int(df.shape[0] * df.shape[1])
        missing_mask = _missing_mask(df) if total_cells else pd.DataFrame()
        missing_cells = int(missing_mask.sum().sum()) if total_cells else 0
        missing_pct = (missing_cells / total_cells * 100.0) if total_cells else 0.0
        duplicates = int(df.duplicated().sum()) if not df.empty else 0
        negative_values = 0
        if "valor" in df.columns:
            numeric = pd.to_numeric(df["valor"], errors="coerce")
            negative_values = int((numeric < 0).sum())

        invalid_dates, date_from, date_to = _date_quality(df)
        required = list(required_columns.get(source_name, ()))
        absent = [column for column in required if column not in df.columns]
        present_required = [column for column in required if column in df.columns]
        incomplete_keys = (
            int(_missing_mask(df[present_required]).any(axis=1).sum())
            if present_required and not df.empty
            else 0
        )

        rows.append(
            {
                "Fuente": source_name,
                "Filas": len(df),
                "Columnas": len(df.columns),
                "Celdas vacías": missing_cells,
                "Vacíos (%)": round(missing_pct, 2),
                "Duplicados exactos": duplicates,
                "Valores negativos": negative_values,
                "Fechas inválidas": invalid_dates,
                "Llaves incompletas": incomplete_keys,
                "Columnas requeridas ausentes": ", ".join(absent),
                "Desde": date_from,
                "Hasta": date_to,
            }
        )

    return pd.DataFrame(rows)


def quality_has_warnings(report: pd.DataFrame) -> bool:
    """Indica si el reporte contiene anomalías que requieren atención."""
    if report is None or report.empty:
        return True
    numeric_flags = [
        "Duplicados exactos",
        "Valores negativos",
        "Fechas inválidas",
        "Llaves incompletas",
    ]
    if any((pd.to_numeric(report[col], errors="coerce").fillna(0) > 0).any() for col in numeric_flags):
        return True
    return report["Columnas requeridas ausentes"].astype(str).str.strip().ne("").any()

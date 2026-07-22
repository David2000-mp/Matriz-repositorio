"""Repositorio central de las bases analíticas de Google Sheets.

Este módulo es la única ruta de lectura para ``Base_Maestra_Colegios`` y
``Base_Demografica_Colegios``. Ambas hojas comparten conexión, manejo de
errores, normalización de encabezados y reglas de integridad.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Optional, Tuple

import pandas as pd
import streamlit as st

from utils.logger import get_logger
from utils.schema_columns import (
    COLS_BASE_DEMOGRAFICA_COLEGIOS,
    COLS_BASE_MAESTRA_COLEGIOS,
)


logger = get_logger(__name__)


@dataclass(frozen=True)
class SheetSpec:
    """Contrato de una hoja analítica."""

    name: str
    columns: tuple[str, ...]
    date_column: str
    text_columns: tuple[str, ...]
    aliases: Mapping[str, str]


@dataclass(frozen=True)
class AnalyticsBases:
    """Snapshot coherente de las dos bases analíticas."""

    maestra: pd.DataFrame
    demografica: pd.DataFrame

    def as_tuple(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        return self.maestra, self.demografica

    def as_dict(self) -> dict[str, pd.DataFrame]:
        return {
            "base_maestra": self.maestra,
            "base_demografica": self.demografica,
        }


MAESTRA_SPEC = SheetSpec(
    name="Base_Maestra_Colegios",
    columns=tuple(COLS_BASE_MAESTRA_COLEGIOS),
    date_column="fecha",
    text_columns=("colegio", "plataforma", "metrica"),
    aliases={"metrica": "metrica"},
)

DEMOGRAFICA_SPEC = SheetSpec(
    name="Base_Demografica_Colegios",
    columns=tuple(COLS_BASE_DEMOGRAFICA_COLEGIOS),
    date_column="fecha_reporte",
    text_columns=("colegio", "plataforma", "criterio", "sexo", "edad", "ubicacion"),
    aliases={
        "fecha": "fecha_reporte",
        "fecha_de_reporte": "fecha_reporte",
        "fecha_reporte": "fecha_reporte",
        "ubicacion": "ubicacion",
    },
)


def _header_key(value: object) -> str:
    """Normaliza encabezados sin depender de acentos o separadores."""
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = "".join(ch if ch.isalnum() else "_" for ch in text)
    return "_".join(part for part in text.split("_") if part)


def _empty_frame(spec: SheetSpec) -> pd.DataFrame:
    return pd.DataFrame(columns=list(spec.columns))


def normalize_sheet_records(
    records: Sequence[Mapping[str, Any]], spec: SheetSpec
) -> pd.DataFrame:
    """Aplica el contrato común a registros de una hoja analítica."""
    if not records:
        return _empty_frame(spec)

    source = pd.DataFrame(records)
    canonical_sources: dict[str, object] = {}
    expected = set(spec.columns)

    for source_column in source.columns:
        key = _header_key(source_column)
        canonical = spec.aliases.get(key, key)
        if canonical in expected and canonical not in canonical_sources:
            canonical_sources[canonical] = source_column

    normalized = pd.DataFrame(index=source.index)
    for column in spec.columns:
        source_column = canonical_sources.get(column)
        normalized[column] = source[source_column] if source_column is not None else pd.NA

    normalized[spec.date_column] = pd.to_datetime(
        normalized[spec.date_column], errors="coerce", format="mixed"
    )
    normalized["valor"] = pd.to_numeric(normalized["valor"], errors="coerce")

    for column in spec.text_columns:
        normalized[column] = normalized[column].fillna("").astype(str).str.strip()

    valid_rows = normalized[spec.date_column].notna()
    valid_rows &= normalized["valor"].notna() & normalized["valor"].ge(0)
    return normalized.loc[valid_rows, list(spec.columns)].reset_index(drop=True)


class AnalyticsDataRepository:
    """Carga un snapshot de ambas hojas usando una sola conexión."""

    def __init__(self, connection_factory: Optional[Callable[[], object]] = None):
        if connection_factory is None:
            # Resolver en runtime mantiene monkeypatching y pruebas aisladas.
            from utils.sheets_connector import get_sheets_connection

            connection_factory = get_sheets_connection
        self._connection_factory = connection_factory

    def _load_sheet(self, spreadsheet: object, spec: SheetSpec) -> pd.DataFrame:
        try:
            worksheet = spreadsheet.worksheet(spec.name)
            records = worksheet.get_all_records()
            return normalize_sheet_records(records, spec)
        except Exception as exc:
            logger.warning("Error cargando hoja '%s': %s", spec.name, exc)
            return _empty_frame(spec)

    def load(self) -> AnalyticsBases:
        try:
            spreadsheet = self._connection_factory()
        except Exception as exc:
            logger.warning("Error conectando al repositorio analítico: %s", exc)
            spreadsheet = None

        if spreadsheet is None:
            return AnalyticsBases(_empty_frame(MAESTRA_SPEC), _empty_frame(DEMOGRAFICA_SPEC))

        return AnalyticsBases(
            maestra=self._load_sheet(spreadsheet, MAESTRA_SPEC),
            demografica=self._load_sheet(spreadsheet, DEMOGRAFICA_SPEC),
        )


@st.cache_data(ttl=300)
def load_analytics_bases() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Carga ambas bases mediante el repositorio central y cachea el snapshot."""
    return AnalyticsDataRepository().load().as_tuple()

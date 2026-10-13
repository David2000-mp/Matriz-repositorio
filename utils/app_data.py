"""Consultas de datos para la capa de presentación.

Este módulo mantiene Pandas fuera del router y nunca almacena DataFrames en
``st.session_state``. El caché compartido vive en ``utils.data_provider``.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from utils.data_provider import get_shared_merged_data


@dataclass(frozen=True)
class FilterOptions:
    entities: tuple[str, ...]
    months: tuple[str, ...]


def load_app_dataframe() -> pd.DataFrame:
    """Obtiene una copia del DataFrame compartido y normaliza su contrato UI."""
    df = get_shared_merged_data()
    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()
    expected_columns = (
        "id_cuenta",
        "entidad",
        "plataforma",
        "usuario_red",
        "fecha",
        "seguidores",
        "engagement_rate",
        "alcance",
        "interacciones",
        "likes_promedio",
    )
    for column in expected_columns:
        if column not in result.columns:
            result[column] = ""

    result["id"] = (
        result["id_cuenta"].astype(str)
        if "id_cuenta" in result.columns
        else result.index.astype(str)
    )
    result["fecha"] = pd.to_datetime(result["fecha"], errors="coerce")
    return result


def get_filter_options(df: pd.DataFrame) -> FilterOptions:
    """Calcula opciones pequeñas e inmutables para los widgets globales."""
    if df is None or df.empty:
        return FilterOptions(entities=(), months=())

    entities: tuple[str, ...] = ()
    months: tuple[str, ...] = ()

    if "entidad" in df.columns:
        entities = tuple(
            sorted(
                value
                for value in df["entidad"].dropna().astype(str).str.strip().unique()
                if value
            )
        )

    if "fecha" in df.columns:
        dates = pd.to_datetime(df["fecha"], errors="coerce")
        months = tuple(sorted(dates.dt.strftime("%Y-%m").dropna().unique(), reverse=True))

    return FilterOptions(entities=entities, months=months)


def apply_global_filters(
    df: pd.DataFrame,
    *,
    entity: str = "Todas",
    month: str = "Todos",
) -> pd.DataFrame:
    """Aplica los filtros globales sin leer ni modificar estado de Streamlit."""
    if df is None or df.empty:
        return df

    filtered = df.copy()
    if month != "Todos" and "fecha" in filtered.columns:
        dates = pd.to_datetime(filtered["fecha"], errors="coerce")
        filtered = filtered[dates.dt.strftime("%Y-%m") == str(month)]

    if entity != "Todas" and "entidad" in filtered.columns:
        filtered = filtered[filtered["entidad"] == entity]

    return filtered


_MESES_CORTOS = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")


def format_month_label(month: str) -> str:
    """Convierte ``YYYY-MM`` en una etiqueta corta en español (``sep 2026``)."""
    try:
        year, number = str(month).split("-")[:2]
        index = int(number) - 1
    except ValueError:
        return str(month)
    if not 0 <= index < 12:
        return str(month)
    return f"{_MESES_CORTOS[index]} {year}"


@dataclass(frozen=True)
class DataSummary:
    latest_month: str | None
    entities: int
    accounts: int
    records: int


def summarize_dataset(df: pd.DataFrame) -> DataSummary:
    """Resume el corte de datos para los indicadores de estado de la UI."""
    if df is None or df.empty:
        return DataSummary(latest_month=None, entities=0, accounts=0, records=0)

    latest = None
    if "fecha" in df.columns:
        dates = pd.to_datetime(df["fecha"], errors="coerce").dropna()
        if not dates.empty:
            latest = dates.max().strftime("%Y-%m")

    def _distinct(column: str) -> int:
        if column not in df.columns:
            return 0
        values = df[column].dropna().astype(str).str.strip()
        return int(values[values != ""].nunique())

    return DataSummary(
        latest_month=latest,
        entities=_distinct("entidad"),
        accounts=_distinct("id_cuenta"),
        records=len(df),
    )

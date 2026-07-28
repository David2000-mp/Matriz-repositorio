"""Motor analítico puro del Módulo Satélite.

Las funciones de este módulo reciben DataFrames ya validados por la Fase 1.
No cargan datos, no usan Streamlit y no dependen de los filtros globales de
ChampiLeaks.
"""

from __future__ import annotations

from typing import Final

import pandas as pd


class SatelliteAnalyticsContractError(ValueError):
    """Indica que un DataFrame no cumple el contrato mínimo analítico."""


FILTER_ACCOUNT_COLUMNS: Final[tuple[str, ...]] = (
    "id_cuenta",
    "colegio_id",
    "plataforma",
)
FILTER_PUBLICATION_COLUMNS: Final[tuple[str, ...]] = (
    "id_publicacion",
    "id_cuenta",
    "plataforma",
    "mes_clave",
)
FILTER_COMMENT_COLUMNS: Final[tuple[str, ...]] = ("id_publicacion",)

PERFORMANCE_REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "id_publicacion",
    "plataforma",
    "tipo_contenido",
    "visualizaciones",
    "alcance",
    "interacciones",
)
PERFORMANCE_GROUP_COLUMNS: Final[tuple[str, str]] = (
    "plataforma",
    "tipo_contenido",
)
PERFORMANCE_OUTPUT_COLUMNS: Final[tuple[str, ...]] = (
    "plataforma",
    "tipo_contenido",
    "publicaciones_totales",
    "visualizaciones_totales",
    "alcance_total",
    "interacciones_totales",
    "interacciones_promedio",
    "interacciones_mediana",
    "cobertura_visualizaciones_pct",
    "cobertura_alcance_pct",
    "tasa_interacciones_1k_vistas",
    "tasa_interacciones_1k_alcance",
)


def _require_columns(
    frame: pd.DataFrame,
    required_columns: tuple[str, ...],
    *,
    frame_name: str,
) -> None:
    """Falla explícitamente si falta una columna requerida."""
    missing = [column for column in required_columns if column not in frame.columns]
    if missing:
        raise SatelliteAnalyticsContractError(
            f"{frame_name}: faltan columnas requeridas={missing}"
        )


def _platform_filter_key(value: object) -> str:
    """Normaliza valores de plataforma antes de cualquier comparación booleana."""
    return "" if pd.isna(value) else str(value).strip().casefold()


def filter_satellite_data(
    df_cuentas_satellite: pd.DataFrame,
    df_publicaciones: pd.DataFrame,
    df_comentarios: pd.DataFrame,
    *,
    colegio_id: str | None = None,
    plataforma: str | None = None,
    mes_clave: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Filtra publicaciones y después limita comentarios con ``.isin()``.

    ``colegio_id`` se resuelve mediante la dimensión institucional porque no
    forma parte del esquema físico de publicaciones. Un filtro con valor
    ``None`` no restringe esa dimensión.
    """
    _require_columns(
        df_cuentas_satellite,
        FILTER_ACCOUNT_COLUMNS,
        frame_name="df_cuentas_satellite",
    )
    _require_columns(
        df_publicaciones,
        FILTER_PUBLICATION_COLUMNS,
        frame_name="df_publicaciones",
    )
    _require_columns(
        df_comentarios,
        FILTER_COMMENT_COLUMNS,
        frame_name="df_comentarios",
    )

    account_mask = pd.Series(True, index=df_cuentas_satellite.index, dtype="boolean")
    if colegio_id is not None:
        account_mask &= df_cuentas_satellite["colegio_id"].eq(colegio_id)
    if plataforma is not None:
        selected_platform = _platform_filter_key(plataforma)
        account_mask &= (
            df_cuentas_satellite["plataforma"]
            .astype("string")
            .str.strip()
            .str.casefold()
            .eq(selected_platform)
        )

    filtered_accounts = df_cuentas_satellite.loc[account_mask].copy()
    account_ids = filtered_accounts["id_cuenta"].dropna().copy()

    publication_mask = df_publicaciones["id_cuenta"].isin(account_ids)
    if plataforma is not None:
        publication_mask &= (
            df_publicaciones["plataforma"]
            .astype("string")
            .str.strip()
            .str.casefold()
            .eq(selected_platform)
        )
    if mes_clave is not None:
        publication_mask &= df_publicaciones["mes_clave"].eq(mes_clave)

    # Orden contractual: publicaciones -> IDs -> comentarios.
    filtered_publications = df_publicaciones.loc[publication_mask].copy()
    publication_ids = (
        filtered_publications["id_publicacion"].dropna().drop_duplicates().copy()
    )
    filtered_comments = df_comentarios.loc[
        df_comentarios["id_publicacion"].isin(publication_ids)
    ].copy()

    return (
        filtered_publications.reset_index(drop=True),
        filtered_comments.reset_index(drop=True),
    )


def _empty_performance_frame() -> pd.DataFrame:
    """Retorna el contrato vacío y tipado de la agregación."""
    return pd.DataFrame(
        {
            "plataforma": pd.Series(dtype="string"),
            "tipo_contenido": pd.Series(dtype="string"),
            "publicaciones_totales": pd.Series(dtype="Int64"),
            "visualizaciones_totales": pd.Series(dtype="Int64"),
            "alcance_total": pd.Series(dtype="Int64"),
            "interacciones_totales": pd.Series(dtype="Int64"),
            "interacciones_promedio": pd.Series(dtype="Float64"),
            "interacciones_mediana": pd.Series(dtype="Float64"),
            "cobertura_visualizaciones_pct": pd.Series(dtype="Float64"),
            "cobertura_alcance_pct": pd.Series(dtype="Float64"),
            "tasa_interacciones_1k_vistas": pd.Series(dtype="Float64"),
            "tasa_interacciones_1k_alcance": pd.Series(dtype="Float64"),
        },
        columns=list(PERFORMANCE_OUTPUT_COLUMNS),
    )


def _safe_rate_per_thousand(
    numerator: pd.Series,
    denominator: pd.Series,
) -> pd.Series:
    """Calcula una tasa por mil sin dividir entre cero ni propagar infinito."""
    numerator_float = numerator.astype("Float64")
    denominator_float = denominator.astype("Float64")
    result = pd.Series(pd.NA, index=numerator.index, dtype="Float64")
    valid_denominator = denominator_float.notna() & denominator_float.gt(0)
    valid_rows = valid_denominator & numerator_float.notna()
    result.loc[valid_rows] = (
        numerator_float.loc[valid_rows]
        .div(denominator_float.loc[valid_rows])
        .mul(1000.0)
    )
    return result


def aggregate_publication_performance(
    df_publicaciones: pd.DataFrame,
) -> pd.DataFrame:
    """Agrega rendimiento exclusivamente por plataforma × tipo de contenido."""
    _require_columns(
        df_publicaciones,
        PERFORMANCE_REQUIRED_COLUMNS,
        frame_name="df_publicaciones",
    )

    if df_publicaciones.empty:
        return _empty_performance_frame()

    work = df_publicaciones.loc[:, list(PERFORMANCE_REQUIRED_COLUMNS)].copy()
    grouped = (
        work.groupby(
            list(PERFORMANCE_GROUP_COLUMNS),
            as_index=False,
            dropna=False,
            sort=True,
        )
        .agg(
            publicaciones_totales=("id_publicacion", "size"),
            visualizaciones_totales=(
                "visualizaciones",
                lambda series: series.sum(min_count=1),
            ),
            alcance_total=("alcance", lambda series: series.sum(min_count=1)),
            interacciones_totales=(
                "interacciones",
                lambda series: series.sum(min_count=1),
            ),
            interacciones_promedio=("interacciones", "mean"),
            interacciones_mediana=("interacciones", "median"),
            publicaciones_con_visualizaciones=("visualizaciones", "count"),
            publicaciones_con_alcance=("alcance", "count"),
        )
        .copy()
    )

    integer_columns = (
        "publicaciones_totales",
        "visualizaciones_totales",
        "alcance_total",
        "interacciones_totales",
        "publicaciones_con_visualizaciones",
        "publicaciones_con_alcance",
    )
    for column in integer_columns:
        grouped[column] = grouped[column].astype("Int64")

    for column in ("interacciones_promedio", "interacciones_mediana"):
        grouped[column] = grouped[column].astype("Float64")

    publication_count = grouped["publicaciones_totales"].astype("Float64")
    grouped["cobertura_visualizaciones_pct"] = (
        grouped["publicaciones_con_visualizaciones"]
        .astype("Float64")
        .div(publication_count)
        .mul(100.0)
        .astype("Float64")
    )
    grouped["cobertura_alcance_pct"] = (
        grouped["publicaciones_con_alcance"]
        .astype("Float64")
        .div(publication_count)
        .mul(100.0)
        .astype("Float64")
    )

    grouped["tasa_interacciones_1k_vistas"] = _safe_rate_per_thousand(
        grouped["interacciones_totales"],
        grouped["visualizaciones_totales"],
    )
    grouped["tasa_interacciones_1k_alcance"] = _safe_rate_per_thousand(
        grouped["interacciones_totales"],
        grouped["alcance_total"],
    )

    return (
        grouped.loc[:, list(PERFORMANCE_OUTPUT_COLUMNS)]
        .sort_values(list(PERFORMANCE_GROUP_COLUMNS), kind="stable")
        .reset_index(drop=True)
        .copy()
    )


def get_publication_trace(
    df_publicaciones: pd.DataFrame,
    df_comentarios: pd.DataFrame,
    target_pub_id: str,
) -> pd.DataFrame:
    """Cruza una publicación con sus comentarios bajo cardinalidad uno-a-muchos."""
    _require_columns(
        df_publicaciones,
        ("id_publicacion",),
        frame_name="df_publicaciones",
    )
    _require_columns(
        df_comentarios,
        ("id_publicacion",),
        frame_name="df_comentarios",
    )

    target_publication = df_publicaciones.loc[
        df_publicaciones["id_publicacion"].eq(target_pub_id)
    ].copy()
    target_comments = df_comentarios.loc[
        df_comentarios["id_publicacion"].eq(target_pub_id)
    ].copy()

    return pd.merge(
        target_publication,
        target_comments,
        on="id_publicacion",
        how="left",
        validate="one_to_many",
        suffixes=("_publicacion", "_comentario"),
    ).copy()

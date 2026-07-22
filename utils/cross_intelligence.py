"""Utilidades para la Vista de Inteligencia Cruzada."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import AbstractSet, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from utils.analytics_repository import load_analytics_bases
from utils.metric_catalog import (
    INTERACTION_ALIASES,
    METRIC_ALIASES,
    VISUALIZATION_ALIASES,
    metric_aliases,
)


MONTH_NAMES_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

HISTORICAL_KEY = "__historico_completo__"

@dataclass(frozen=True)
class MetricDelta:
    current: float
    previous: float
    delta_abs: float
    delta_pct: Optional[float]


@dataclass(frozen=True)
class CorrelationResult:
    method: str
    coefficient: Optional[float]
    sample_size: int
    interpretation: str
    series: pd.DataFrame


def _normalize_text(value: str) -> str:
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = "".join(ch if (ch.isalnum() or ch.isspace()) else " " for ch in text)
    return " ".join(text.split())


def _filter_nonnegative_values(df: pd.DataFrame) -> pd.DataFrame:
    """Conserva únicamente valores numéricos válidos y no negativos.

    Las funciones analíticas también se usan directamente en pruebas y en
    futuras vistas, no sólo a través de ``load_normalized_bases``. Aplicar la
    misma salvaguarda aquí evita que una llamada directa vuelva a introducir
    valores inválidos en porcentajes o totales.
    """
    if df is None or df.empty or "valor" not in df.columns:
        return df.copy() if df is not None else pd.DataFrame()

    local = df.copy()
    local["valor"] = pd.to_numeric(local["valor"], errors="coerce")
    return local[local["valor"].notna() & (local["valor"] >= 0)].copy()


def _metric_rows(df: pd.DataFrame, metric_key: str) -> pd.DataFrame:
    """Filtra una sola métrica canónica sin combinar escalas incompatibles."""
    local = _filter_nonnegative_values(df)
    if local.empty:
        return local
    if "metrica_norm" not in local.columns:
        local["metrica_norm"] = local["metrica"].apply(_normalize_text)
    return local[local["metrica_norm"].isin(metric_aliases(metric_key))].copy()


def _demographic_base(df: pd.DataFrame) -> pd.DataFrame:
    local = _filter_nonnegative_values(df)
    if local.empty:
        return local
    if "criterio_norm" not in local.columns:
        local["criterio_norm"] = local["criterio"].apply(_normalize_text)
    local = local[local["criterio_norm"] == "demografia base"].copy()
    return local[
        (local["sexo"].astype(str).str.strip() != "")
        & (local["edad"].astype(str).str.strip() != "")
    ].copy()


def _filter_segment(
    df: pd.DataFrame, sexo: str = "Todos", edad: str = "Todos"
) -> pd.DataFrame:
    local = df.copy()
    if sexo and sexo != "Todos":
        local = local[local["sexo"].astype(str) == str(sexo)]
    if edad and edad != "Todos":
        local = local[local["edad"].astype(str) == str(edad)]
    return local


def _normalize_maestra(df: pd.DataFrame) -> pd.DataFrame:
    expected = ["fecha", "colegio", "plataforma", "metrica", "valor"]
    if df is None or df.empty:
        return pd.DataFrame(columns=expected + ["month_key", "metrica_norm"])

    out = df.copy()
    for col in expected:
        if col not in out.columns:
            out[col] = ""

    out = out[expected].copy()
    out["fecha"] = pd.to_datetime(out["fecha"], errors="coerce", format="mixed")
    out["valor"] = pd.to_numeric(out["valor"], errors="coerce")

    for col in ["colegio", "plataforma", "metrica"]:
        out[col] = out[col].fillna("").astype(str).str.strip()

    out = out.dropna(subset=["fecha", "valor"]).copy()
    out = out[out["valor"] >= 0].copy()
    out["month_key"] = out["fecha"].dt.strftime("%Y-%m")
    out["metrica_norm"] = out["metrica"].apply(_normalize_text)
    return out


def _normalize_demografica(df: pd.DataFrame) -> pd.DataFrame:
    expected = ["fecha_reporte", "colegio", "plataforma", "criterio", "sexo", "edad", "ubicacion", "valor"]
    if df is None or df.empty:
        return pd.DataFrame(columns=expected + ["month_key", "criterio_norm"])

    out = df.copy()

    # Estandariza aliases frecuentes antes de proyectar columnas esperadas.
    normalized_aliases = {
        "fecha de reporte": "fecha_reporte",
        "fecha reporte": "fecha_reporte",
        "fecha_reporte": "fecha_reporte",
        "fecha": "fecha_reporte",
    }
    rename_map = {}
    for col in out.columns:
        key = str(col).strip().lower()
        key = " ".join(key.split())
        if key in normalized_aliases:
            rename_map[col] = normalized_aliases[key]
    if rename_map:
        out = out.rename(columns=rename_map)

    for col in expected:
        if col not in out.columns:
            out[col] = ""

    out = out[expected].copy()
    out["fecha_reporte"] = pd.to_datetime(
        out["fecha_reporte"], errors="coerce", format="mixed"
    )
    out["valor"] = pd.to_numeric(out["valor"], errors="coerce")

    for col in ["colegio", "plataforma", "criterio", "sexo", "edad", "ubicacion"]:
        out[col] = out[col].fillna("").astype(str).str.strip()

    out = out.dropna(subset=["fecha_reporte", "valor"]).copy()
    out = out[out["valor"] >= 0].copy()
    out["month_key"] = out["fecha_reporte"].dt.strftime("%Y-%m")
    out["criterio_norm"] = out["criterio"].apply(_normalize_text)
    return out


@st.cache_data(ttl=300)
def load_normalized_bases() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Enriquece el snapshot compartido para los cálculos cruzados."""
    base_maestra, base_demografica = load_analytics_bases()
    maestra = _normalize_maestra(base_maestra)
    demografica = _normalize_demografica(base_demografica)
    return maestra, demografica


@st.cache_data(ttl=300)
def month_key_to_label(month_key: str) -> str:
    if str(month_key) == HISTORICAL_KEY:
        return "Histórico completo"

    if not month_key or "-" not in str(month_key):
        return "Periodo invalido"

    try:
        year_s, month_s = str(month_key).split("-", 1)
        year_i = int(year_s)
        month_i = int(month_s)
        month_name = MONTH_NAMES_ES.get(month_i, month_s)
        return f"{month_name} {year_i}"
    except Exception:
        return str(month_key)


@st.cache_data(ttl=300)
def get_previous_month_key(month_key: str) -> Optional[str]:
    if str(month_key) == HISTORICAL_KEY:
        return None

    try:
        period = pd.Period(str(month_key), freq="M")
        prev = period - 1
        return str(prev)
    except Exception:
        return None


@st.cache_data(ttl=300)
def get_month_bounds(month_key: str) -> Tuple[Optional[pd.Timestamp], Optional[pd.Timestamp]]:
    """Devuelve limites [inicio, fin] del mes para sombreado en graficas."""
    if str(month_key) == HISTORICAL_KEY:
        return None, None

    try:
        period = pd.Period(str(month_key), freq="M")
        start = period.start_time.normalize()
        end = period.end_time
        return start, end
    except Exception:
        return None, None


@st.cache_data(ttl=300)
def get_filter_catalogs() -> Dict[str, List[str]]:
    """Obtiene dimensiones disponibles para los filtros analíticos."""
    maestra, demo = load_normalized_bases()

    colegios = sorted(
        set(maestra.get("colegio", pd.Series(dtype=str)).dropna().astype(str).str.strip())
        | set(demo.get("colegio", pd.Series(dtype=str)).dropna().astype(str).str.strip())
    )
    colegios = [c for c in colegios if c]

    plataformas = sorted(
        set(maestra.get("plataforma", pd.Series(dtype=str)).dropna().astype(str).str.strip())
        | set(demo.get("plataforma", pd.Series(dtype=str)).dropna().astype(str).str.strip())
    )
    plataformas = [p for p in plataformas if p]

    months = sorted(
        set(maestra.get("month_key", pd.Series(dtype=str)).dropna().astype(str))
        | set(demo.get("month_key", pd.Series(dtype=str)).dropna().astype(str)),
        reverse=True,
    )
    months = [HISTORICAL_KEY] + months

    demo_base = _demographic_base(demo)
    sexos = sorted(
        value
        for value in demo_base.get("sexo", pd.Series(dtype=str)).dropna().astype(str).str.strip().unique()
        if value
    )
    edades = sorted(
        (
            value
            for value in demo_base.get("edad", pd.Series(dtype=str)).dropna().astype(str).str.strip().unique()
            if value
        ),
        key=lambda value: (
            int(str(value).split("-", 1)[0])
            if str(value).split("-", 1)[0].isdigit()
            else 999,
            str(value),
        ),
    )

    return {
        "colegios": colegios,
        "plataformas": plataformas,
        "month_keys": months,
        "month_labels": [month_key_to_label(m) for m in months],
        "sexos": sexos,
        "edades": edades,
        "metric_keys": list(METRIC_ALIASES),
    }


def _apply_common_filters(
    df: pd.DataFrame,
    *,
    colegio: str,
    plataforma: str,
    month_key: str = "",
    month_col: str = "month_key",
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=df.columns if df is not None else [])

    out = df.copy()

    if month_key:
        out = out[out[month_col].astype(str) == str(month_key)]

    if colegio and colegio != "Todos":
        out = out[out["colegio"].astype(str) == str(colegio)]

    if plataforma and plataforma != "Todas":
        out = out[out["plataforma"].astype(str) == str(plataforma)]

    return out


@st.cache_data(ttl=300)
def get_monthly_slice(colegio: str, plataforma: str, month_key: str) -> Dict[str, pd.DataFrame]:
    """Construye corte mensual cruzado cacheando agregacion y filtrado por YYYY-MM."""
    maestra, demo = load_normalized_bases()
    prev_key = get_previous_month_key(month_key)

    maestra_current = _apply_common_filters(maestra, colegio=colegio, plataforma=plataforma, month_key=month_key)
    demo_current = _apply_common_filters(demo, colegio=colegio, plataforma=plataforma, month_key=month_key)

    maestra_previous = (
        _apply_common_filters(maestra, colegio=colegio, plataforma=plataforma, month_key=prev_key or "")
        if prev_key
        else pd.DataFrame(columns=maestra.columns)
    )

    network_maestra = _apply_common_filters(maestra, colegio="Todos", plataforma=plataforma, month_key=month_key)
    network_demo = _apply_common_filters(demo, colegio="Todos", plataforma=plataforma, month_key=month_key)

    return {
        "maestra_current": maestra_current,
        "demo_current": demo_current,
        "maestra_previous": maestra_previous,
        "network_maestra": network_maestra,
        "network_demo": network_demo,
        "prev_month_key": prev_key or "",
    }


@st.cache_data(ttl=300)
def get_historical_slice(colegio: str, plataforma: str) -> Dict[str, pd.DataFrame]:
    """Construye corte historico completo por colegio/plataforma sin filtrar a un solo mes."""
    maestra, demo = load_normalized_bases()
    maestra_hist = _apply_common_filters(maestra, colegio=colegio, plataforma=plataforma)
    demo_hist = _apply_common_filters(demo, colegio=colegio, plataforma=plataforma)
    network_maestra = _apply_common_filters(maestra, colegio="Todos", plataforma=plataforma)
    network_demo = _apply_common_filters(demo, colegio="Todos", plataforma=plataforma)
    return {
        "maestra_historical": maestra_hist,
        "demo_historical": demo_hist,
        "network_maestra": network_maestra,
        "network_demo": network_demo,
    }


def _metric_total(df_maestra: pd.DataFrame, aliases: AbstractSet[str]) -> float:
    if df_maestra is None or df_maestra.empty:
        return 0.0

    local = _filter_nonnegative_values(df_maestra)
    if "metrica_norm" not in local.columns:
        local["metrica_norm"] = local["metrica"].apply(_normalize_text)

    return float(local[local["metrica_norm"].isin(aliases)]["valor"].sum())


@st.cache_data(ttl=300)
def calculate_performance_kpis(df_current: pd.DataFrame, df_previous: pd.DataFrame) -> Dict[str, MetricDelta]:
    inter_curr = _metric_total(df_current, INTERACTION_ALIASES)
    inter_prev = _metric_total(df_previous, INTERACTION_ALIASES)
    vis_curr = _metric_total(df_current, VISUALIZATION_ALIASES)
    vis_prev = _metric_total(df_previous, VISUALIZATION_ALIASES)

    def _build(current: float, previous: float) -> MetricDelta:
        delta_abs = current - previous
        delta_pct = None if previous <= 0 else (delta_abs / previous) * 100.0
        return MetricDelta(current=current, previous=previous, delta_abs=delta_abs, delta_pct=delta_pct)

    return {
        "interacciones": _build(inter_curr, inter_prev),
        "visualizaciones": _build(vis_curr, vis_prev),
    }


@st.cache_data(ttl=300)
def calculate_historical_totals(df_historical: pd.DataFrame) -> Dict[str, float]:
    return {
        "interacciones_total": _metric_total(df_historical, INTERACTION_ALIASES),
        "visualizaciones_total": _metric_total(df_historical, VISUALIZATION_ALIASES),
    }


@st.cache_data(ttl=300)
def calculate_metric_delta(
    df_current: pd.DataFrame,
    df_previous: pd.DataFrame,
    metric_key: str,
) -> MetricDelta:
    """Calcula el KPI de una sola métrica seleccionada."""
    current_rows = _metric_rows(df_current, metric_key)
    previous_rows = _metric_rows(df_previous, metric_key)
    current = float(current_rows["valor"].sum()) if "valor" in current_rows else 0.0
    previous = float(previous_rows["valor"].sum()) if "valor" in previous_rows else 0.0
    delta_abs = current - previous
    delta_pct = None if previous <= 0 else (delta_abs / previous) * 100.0
    return MetricDelta(current, previous, delta_abs, delta_pct)


@st.cache_data(ttl=300)
def calculate_metric_total(df: pd.DataFrame, metric_key: str) -> float:
    """Suma únicamente la métrica analítica seleccionada."""
    rows = _metric_rows(df, metric_key)
    return float(rows["valor"].sum()) if "valor" in rows else 0.0


@st.cache_data(ttl=300)
def build_segmented_performance(
    df_maestra: pd.DataFrame,
    df_demo: pd.DataFrame,
    metric_key: str,
    sexo: str = "Todos",
    edad: str = "Todos",
) -> pd.DataFrame:
    """Estima rendimiento atribuible a un segmento por plataforma.

    La estimación multiplica el rendimiento observado de cada
    mes/colegio/plataforma por la participación del segmento en la base
    demográfica equivalente. No se presenta como medición individual.
    """
    cols = [
        "plataforma",
        "metrica",
        "rendimiento_total",
        "volumen_segmento",
        "volumen_demografico_total",
        "participacion_segmento_pct",
        "rendimiento_segmentado_estimado",
    ]
    performance = _metric_rows(df_maestra, metric_key)
    demographic = _demographic_base(df_demo)
    if performance.empty or demographic.empty:
        return pd.DataFrame(columns=cols)

    keys = ["month_key", "colegio", "plataforma"]
    if any(key not in performance.columns or key not in demographic.columns for key in keys):
        return pd.DataFrame(columns=cols)

    totals = (
        demographic.groupby(keys, as_index=False, dropna=False)["valor"]
        .sum()
        .rename(columns={"valor": "volumen_demografico_total"})
    )
    selected = _filter_segment(demographic, sexo, edad)
    selected = (
        selected.groupby(keys, as_index=False, dropna=False)["valor"]
        .sum()
        .rename(columns={"valor": "volumen_segmento"})
    )
    performance = (
        performance.groupby(keys, as_index=False, dropna=False)["valor"]
        .sum()
        .rename(columns={"valor": "rendimiento_total"})
    )

    joined = totals.merge(selected, on=keys, how="left").merge(
        performance, on=keys, how="inner"
    )
    if joined.empty:
        return pd.DataFrame(columns=cols)

    joined["volumen_segmento"] = joined["volumen_segmento"].fillna(0.0)
    joined["participacion"] = joined["volumen_segmento"].div(
        joined["volumen_demografico_total"].replace(0, pd.NA)
    ).fillna(0.0)
    joined["rendimiento_segmentado_estimado"] = (
        joined["rendimiento_total"] * joined["participacion"]
    )

    result = (
        joined.groupby("plataforma", as_index=False, dropna=False)
        .agg(
            rendimiento_total=("rendimiento_total", "sum"),
            volumen_segmento=("volumen_segmento", "sum"),
            volumen_demografico_total=("volumen_demografico_total", "sum"),
            rendimiento_segmentado_estimado=("rendimiento_segmentado_estimado", "sum"),
        )
        .sort_values("rendimiento_segmentado_estimado", ascending=False)
    )
    result["participacion_segmento_pct"] = result["volumen_segmento"].div(
        result["volumen_demografico_total"].replace(0, pd.NA)
    ).fillna(0.0) * 100.0
    result["metrica"] = str(metric_key)
    return result[cols].reset_index(drop=True)


def _correlation_interpretation(coefficient: Optional[float]) -> str:
    if coefficient is None or pd.isna(coefficient):
        return "Datos insuficientes o sin variación para calcular correlación."

    magnitude = abs(float(coefficient))
    if magnitude < 0.2:
        strength = "muy débil"
    elif magnitude < 0.4:
        strength = "débil"
    elif magnitude < 0.6:
        strength = "moderada"
    elif magnitude < 0.8:
        strength = "fuerte"
    else:
        strength = "muy fuerte"

    direction = "positiva" if coefficient > 0 else "negativa" if coefficient < 0 else "nula"
    return f"Relación {direction} {strength}; correlación no implica causalidad."


@st.cache_data(ttl=300)
def calculate_demographic_performance_correlation(
    df_maestra: pd.DataFrame,
    df_demo: pd.DataFrame,
    metric_key: str,
    sexo: str = "Todos",
    edad: str = "Todos",
    method: str = "pearson",
) -> CorrelationResult:
    """Calcula correlación mensual entre volumen demográfico y rendimiento."""
    method_key = str(method or "pearson").strip().lower()
    if method_key not in {"pearson", "spearman"}:
        raise ValueError("El método debe ser 'pearson' o 'spearman'.")

    performance = _metric_rows(df_maestra, metric_key)
    demographic = _filter_segment(_demographic_base(df_demo), sexo, edad)
    empty_series = pd.DataFrame(
        columns=["month_key", "month_date", "volumen_demografico", "rendimiento"]
    )
    if performance.empty or demographic.empty:
        return CorrelationResult(
            method_key, None, 0, _correlation_interpretation(None), empty_series
        )

    performance = (
        performance.groupby("month_key", as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "rendimiento"})
    )
    demographic = (
        demographic.groupby("month_key", as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "volumen_demografico"})
    )
    series = demographic.merge(performance, on="month_key", how="inner")
    series = series.dropna(subset=["volumen_demografico", "rendimiento"])
    series["month_date"] = pd.to_datetime(
        series["month_key"].astype(str) + "-01", errors="coerce"
    )
    series = series[
        ["month_key", "month_date", "volumen_demografico", "rendimiento"]
    ].sort_values("month_key").reset_index(drop=True)

    coefficient: Optional[float] = None
    if (
        len(series) >= 3
        and series["volumen_demografico"].nunique() > 1
        and series["rendimiento"].nunique() > 1
    ):
        left = series["volumen_demografico"]
        right = series["rendimiento"]
        if method_key == "spearman":
            left = left.rank(method="average")
            right = right.rank(method="average")
        raw_coefficient = left.corr(right, method="pearson")
        if pd.notna(raw_coefficient):
            coefficient = float(raw_coefficient)

    return CorrelationResult(
        method=method_key,
        coefficient=coefficient,
        sample_size=len(series),
        interpretation=_correlation_interpretation(coefficient),
        series=series,
    )


@st.cache_data(ttl=300)
def build_cohort_series(
    df_demo: pd.DataFrame,
    sexo: str = "Todos",
    edad: str = "Todos",
) -> pd.DataFrame:
    """Sigue la participación mensual de un segmento demográfico estable."""
    cols = [
        "month_key",
        "month_date",
        "volumen_segmento",
        "volumen_demografico_total",
        "participacion_pct",
    ]
    demographic = _demographic_base(df_demo)
    if demographic.empty:
        return pd.DataFrame(columns=cols)

    totals = (
        demographic.groupby("month_key", as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "volumen_demografico_total"})
    )
    selected = _filter_segment(demographic, sexo, edad)
    selected = (
        selected.groupby("month_key", as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "volumen_segmento"})
    )
    series = totals.merge(selected, on="month_key", how="left")
    series["volumen_segmento"] = series["volumen_segmento"].fillna(0.0)
    series["participacion_pct"] = series["volumen_segmento"].div(
        series["volumen_demografico_total"].replace(0, pd.NA)
    ).fillna(0.0) * 100.0
    series["month_date"] = pd.to_datetime(
        series["month_key"].astype(str) + "-01", errors="coerce"
    )
    return series[cols].sort_values("month_key").reset_index(drop=True)


@st.cache_data(ttl=300)
def get_dominant_demographic(df_demo: pd.DataFrame) -> Optional[Dict[str, object]]:
    if df_demo is None or df_demo.empty:
        return None

    local = _filter_nonnegative_values(df_demo)
    local = local[local["criterio_norm"] == "demografia base"]
    local = local[(local["sexo"].astype(str).str.strip() != "") & (local["edad"].astype(str).str.strip() != "")]
    if local.empty:
        return None

    agg = local.groupby(["sexo", "edad"], as_index=False)["valor"].sum().sort_values("valor", ascending=False)
    top = agg.iloc[0]
    total = float(agg["valor"].sum())
    pct = (float(top["valor"]) / total * 100.0) if total > 0 else 0.0

    return {
        "sexo": str(top["sexo"]),
        "edad": str(top["edad"]),
        "valor": float(top["valor"]),
        "pct": pct,
    }


@st.cache_data(ttl=300)
def get_top_city(df_demo: pd.DataFrame) -> Optional[Dict[str, object]]:
    if df_demo is None or df_demo.empty:
        return None

    local = _filter_nonnegative_values(df_demo)
    local = local[local["criterio_norm"] == "ciudad"]
    local = local[local["ubicacion"].astype(str).str.strip() != ""]
    if local.empty:
        return None

    agg = local.groupby("ubicacion", as_index=False)["valor"].sum().sort_values("valor", ascending=False)
    top = agg.iloc[0]
    total = float(agg["valor"].sum())
    pct = (float(top["valor"]) / total * 100.0) if total > 0 else 0.0

    return {
        "ciudad": str(top["ubicacion"]),
        "valor": float(top["valor"]),
        "pct": pct,
    }


@st.cache_data(ttl=300)
def build_daily_performance_series(df_maestra: pd.DataFrame) -> pd.DataFrame:
    if df_maestra is None or df_maestra.empty:
        return pd.DataFrame(columns=["fecha", "interacciones", "visualizaciones"])

    local = _filter_nonnegative_values(df_maestra)
    local["fecha"] = pd.to_datetime(local["fecha"], errors="coerce", format="mixed")
    local = local.dropna(subset=["fecha"])

    inter = local[local["metrica_norm"].isin(INTERACTION_ALIASES)].groupby("fecha", as_index=False)["valor"].sum()
    inter = inter.rename(columns={"valor": "interacciones"})

    vis = local[local["metrica_norm"].isin(VISUALIZATION_ALIASES)].groupby("fecha", as_index=False)["valor"].sum()
    vis = vis.rename(columns={"valor": "visualizaciones"})

    merged = pd.merge(inter, vis, on="fecha", how="outer").fillna(0.0)
    merged = merged.sort_values("fecha").reset_index(drop=True)
    return merged


@st.cache_data(ttl=300)
def build_historical_performance_series(df_maestra_historical: pd.DataFrame) -> pd.DataFrame:
    """Serie mensual historica de rendimiento (panorama completo)."""
    if df_maestra_historical is None or df_maestra_historical.empty:
        return pd.DataFrame(columns=["month_key", "month_date", "interacciones", "visualizaciones"])

    daily = build_daily_performance_series(df_maestra_historical)
    if daily.empty:
        return pd.DataFrame(columns=["month_key", "month_date", "interacciones", "visualizaciones"])

    daily["month_key"] = pd.to_datetime(daily["fecha"], errors="coerce").dt.strftime("%Y-%m")
    monthly = (
        daily.groupby("month_key", as_index=False)[["interacciones", "visualizaciones"]]
        .sum()
        .sort_values("month_key")
    )
    monthly["month_date"] = pd.to_datetime(monthly["month_key"] + "-01", errors="coerce")
    return monthly


@st.cache_data(ttl=300)
def build_demographic_time_share(df_demo: pd.DataFrame, top_n: int = 2) -> Tuple[pd.DataFrame, List[str]]:
    """Devuelve serie mensual de porcentaje para segmentos demograficos dominantes."""
    if df_demo is None or df_demo.empty:
        return pd.DataFrame(columns=["month_key", "segmento", "pct"]), []

    local = _filter_nonnegative_values(df_demo)
    local = local[local["criterio_norm"] == "demografia base"]
    local = local[(local["sexo"].astype(str).str.strip() != "") & (local["edad"].astype(str).str.strip() != "")]
    if local.empty:
        return pd.DataFrame(columns=["month_key", "segmento", "pct"]), []

    local["segmento"] = local["sexo"].astype(str) + " | " + local["edad"].astype(str)
    overall = local.groupby("segmento", as_index=False)["valor"].sum().sort_values("valor", ascending=False)
    top_segments = overall["segmento"].head(max(top_n, 1)).tolist()

    monthly = local.groupby(["month_key", "segmento"], as_index=False)["valor"].sum()
    monthly_total = monthly.groupby("month_key", as_index=False)["valor"].sum().rename(columns={"valor": "total"})
    monthly = monthly.merge(monthly_total, on="month_key", how="left")
    monthly["pct"] = monthly.apply(
        lambda row: (row["valor"] / row["total"] * 100.0) if row["total"] > 0 else 0.0,
        axis=1,
    )
    plot_df = monthly[monthly["segmento"].isin(top_segments)][["month_key", "segmento", "pct"]].copy()
    plot_df["month_date"] = pd.to_datetime(plot_df["month_key"] + "-01", errors="coerce")
    plot_df = plot_df.sort_values(["segmento", "month_key"]).reset_index(drop=True)
    return plot_df, top_segments


@st.cache_data(ttl=300)
def build_city_performance_drilldown(
    df_maestra_month: pd.DataFrame,
    df_demo_month: pd.DataFrame,
    metric_key: str = "interacciones",
) -> pd.DataFrame:
    """Distribuye una sola métrica por participación demográfica de ciudad."""
    cols = ["ciudad", "city_pct", "metrica", "rendimiento_estimado"]
    if df_maestra_month is None or df_maestra_month.empty or df_demo_month is None or df_demo_month.empty:
        return pd.DataFrame(columns=cols)

    city = _filter_nonnegative_values(df_demo_month)
    city = city[city["criterio_norm"] == "ciudad"]
    city = city[city["ubicacion"].astype(str).str.strip() != ""]
    if city.empty:
        return pd.DataFrame(columns=cols)

    city_agg = city.groupby("ubicacion", as_index=False)["valor"].sum().rename(columns={"ubicacion": "ciudad"})
    city_total = float(city_agg["valor"].sum())
    if city_total <= 0:
        return pd.DataFrame(columns=cols)

    city_agg["city_pct"] = city_agg["valor"] / city_total
    metric_total = calculate_metric_total(df_maestra_month, metric_key)
    city_agg["metrica"] = str(metric_key)
    city_agg["rendimiento_estimado"] = city_agg["city_pct"] * metric_total
    return (
        city_agg.drop(columns=["valor"])
        .sort_values("rendimiento_estimado", ascending=False)
        .reset_index(drop=True)[cols]
    )


@st.cache_data(ttl=300)
def build_school_ranking(
    df_maestra_month_network: pd.DataFrame,
    metric_key: str = "interacciones",
) -> pd.DataFrame:
    """Ranking de colegios para una sola métrica seleccionada."""
    cols = ["colegio", "metrica", "rendimiento", "aporte_pct"]
    if df_maestra_month_network is None or df_maestra_month_network.empty:
        return pd.DataFrame(columns=cols)

    local = _metric_rows(df_maestra_month_network, metric_key)
    rank = (
        local.groupby("colegio", as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "rendimiento"})
    )
    total = float(rank["rendimiento"].sum())
    rank["aporte_pct"] = (rank["rendimiento"] / total * 100.0) if total > 0 else 0.0
    rank["metrica"] = str(metric_key)
    return rank.sort_values("rendimiento", ascending=False).reset_index(drop=True)[cols]


@st.cache_data(ttl=300)
def build_segment_distribution(df_demo_month: pd.DataFrame) -> pd.DataFrame:
    """Distribucion detallada de demografia base por sexo y edad en el mes."""
    cols = ["sexo", "edad", "segmento", "valor", "pct"]
    if df_demo_month is None or df_demo_month.empty:
        return pd.DataFrame(columns=cols)

    local = _filter_nonnegative_values(df_demo_month)
    local = local[local["criterio_norm"] == "demografia base"]
    local = local[(local["sexo"].astype(str).str.strip() != "") & (local["edad"].astype(str).str.strip() != "")]
    if local.empty:
        return pd.DataFrame(columns=cols)

    agg = local.groupby(["sexo", "edad"], as_index=False)["valor"].sum()
    total = float(agg["valor"].sum())
    agg["pct"] = (agg["valor"] / total * 100.0) if total > 0 else 0.0
    agg["segmento"] = agg["sexo"].astype(str) + " | " + agg["edad"].astype(str)
    agg = agg.sort_values("valor", ascending=False).reset_index(drop=True)
    return agg[["sexo", "edad", "segmento", "valor", "pct"]]


@st.cache_data(ttl=300)
def build_performance_vs_network(
    df_maestra_scope: pd.DataFrame,
    selected_school: str,
    metric_key: str = "interacciones",
) -> pd.DataFrame:
    """Compara una métrica de la cuenta vs promedio de red."""
    cols = ["metrica", "cuenta", "red_promedio", "delta"]
    if df_maestra_scope is None or df_maestra_scope.empty or not selected_school or selected_school == "Todos":
        return pd.DataFrame(columns=cols)

    local = _metric_rows(df_maestra_scope, metric_key)
    selected = local[local["colegio"].astype(str) == str(selected_school)].copy()
    network = local[local["colegio"].astype(str) != str(selected_school)].copy()
    if selected.empty or network.empty:
        return pd.DataFrame(columns=cols)

    selected_total = float(selected["valor"].sum())
    network_totals = network.groupby("colegio", as_index=False)["valor"].sum()
    network_average = float(network_totals["valor"].mean()) if not network_totals.empty else 0.0

    result = pd.DataFrame(
        [
            {
                "metrica": str(metric_key),
                "cuenta": selected_total,
                "red_promedio": network_average,
                "delta": selected_total - network_average,
            }
        ]
    )
    return result


@st.cache_data(ttl=300)
def build_demographic_vs_network(df_demo_scope: pd.DataFrame, selected_school: str) -> pd.DataFrame:
    """Compara perfil demografico de cuenta vs red (excluyendo cuenta)."""
    cols = ["segmento", "cuenta_pct", "red_pct", "delta_pp"]
    if df_demo_scope is None or df_demo_scope.empty or not selected_school or selected_school == "Todos":
        return pd.DataFrame(columns=cols)

    local = _filter_nonnegative_values(df_demo_scope)
    local = local[local["criterio_norm"] == "demografia base"]
    local = local[(local["sexo"].astype(str).str.strip() != "") & (local["edad"].astype(str).str.strip() != "")]
    if local.empty:
        return pd.DataFrame(columns=cols)

    selected = local[local["colegio"].astype(str) == str(selected_school)].copy()
    network = local[local["colegio"].astype(str) != str(selected_school)].copy()
    if selected.empty or network.empty:
        return pd.DataFrame(columns=cols)

    def _dist(df: pd.DataFrame, value_name: str) -> pd.DataFrame:
        agg = df.groupby(["sexo", "edad"], as_index=False)["valor"].sum().rename(columns={"valor": value_name})
        total = float(agg[value_name].sum())
        pct_col = f"{value_name}_pct"
        agg[pct_col] = (agg[value_name] / total * 100.0) if total > 0 else 0.0
        return agg

    cuenta = _dist(selected, "cuenta")
    red = _dist(network, "red")

    merged = pd.merge(cuenta, red, on=["sexo", "edad"], how="outer").fillna(0.0)
    merged["segmento"] = merged["sexo"].astype(str) + " | " + merged["edad"].astype(str)
    merged["delta_pp"] = merged["cuenta_pct"] - merged["red_pct"]

    out = merged[["segmento", "cuenta_pct", "red_pct", "delta_pp"]].copy()
    out = out.sort_values("delta_pp", key=lambda s: s.abs(), ascending=False).reset_index(drop=True)
    return out

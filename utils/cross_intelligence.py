"""Utilidades para la Vista de Inteligencia Cruzada."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from utils.data_loader import load_base_demografica_colegios, load_base_maestra_colegios


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

INTERACTION_ALIASES = {"interacciones", "interaccion"}
VISUALIZATION_ALIASES = {"visualizaciones", "visualizacion", "views", "vistas"}


@dataclass(frozen=True)
class MetricDelta:
    current: float
    previous: float
    delta_abs: float
    delta_pct: Optional[float]


def _normalize_text(value: str) -> str:
    text = str(value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = "".join(ch if (ch.isalnum() or ch.isspace()) else " " for ch in text)
    return " ".join(text.split())


def _normalize_maestra(df: pd.DataFrame) -> pd.DataFrame:
    expected = ["fecha", "colegio", "plataforma", "metrica", "valor"]
    if df is None or df.empty:
        return pd.DataFrame(columns=expected + ["month_key", "metrica_norm"])

    out = df.copy()
    for col in expected:
        if col not in out.columns:
            out[col] = ""

    out = out[expected].copy()
    out["fecha"] = pd.to_datetime(out["fecha"], errors="coerce")
    out["valor"] = pd.to_numeric(out["valor"], errors="coerce").fillna(0.0)

    for col in ["colegio", "plataforma", "metrica"]:
        out[col] = out[col].fillna("").astype(str).str.strip()

    out = out.dropna(subset=["fecha"]).copy()
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
    out["fecha_reporte"] = pd.to_datetime(out["fecha_reporte"], errors="coerce")
    out["valor"] = pd.to_numeric(out["valor"], errors="coerce").fillna(0.0)

    for col in ["colegio", "plataforma", "criterio", "sexo", "edad", "ubicacion"]:
        out[col] = out[col].fillna("").astype(str).str.strip()

    out = out.dropna(subset=["fecha_reporte"]).copy()
    out["month_key"] = out["fecha_reporte"].dt.strftime("%Y-%m")
    out["criterio_norm"] = out["criterio"].apply(_normalize_text)
    return out


@st.cache_data(ttl=300)
def load_normalized_bases() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Carga y normaliza ambas bases con parseo de fechas cacheado."""
    maestra = _normalize_maestra(load_base_maestra_colegios())
    demografica = _normalize_demografica(load_base_demografica_colegios())
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
        end = period.end_time.normalize()
        return start, end
    except Exception:
        return None, None


@st.cache_data(ttl=300)
def get_filter_catalogs() -> Dict[str, List[str]]:
    """Obtiene opciones de filtros para colegio/plataforma/mes sobre ambas fuentes."""
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

    return {
        "colegios": colegios,
        "plataformas": plataformas,
        "month_keys": months,
        "month_labels": [month_key_to_label(m) for m in months],
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


def _metric_total(df_maestra: pd.DataFrame, aliases: set[str]) -> float:
    if df_maestra is None or df_maestra.empty:
        return 0.0

    local = df_maestra.copy()
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
def get_dominant_demographic(df_demo: pd.DataFrame) -> Optional[Dict[str, object]]:
    if df_demo is None or df_demo.empty:
        return None

    local = df_demo.copy()
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

    local = df_demo.copy()
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

    local = df_maestra.copy()
    local["fecha"] = pd.to_datetime(local["fecha"], errors="coerce")
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

    local = df_demo.copy()
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
def build_city_performance_drilldown(df_maestra_month: pd.DataFrame, df_demo_month: pd.DataFrame) -> pd.DataFrame:
    """Asigna rendimiento del mes por ciudad usando ponderacion por participacion demografica de ciudad."""
    cols = ["ciudad", "city_pct", "interacciones_estimadas", "visualizaciones_estimadas", "volumen_estimado"]
    if df_maestra_month is None or df_maestra_month.empty or df_demo_month is None or df_demo_month.empty:
        return pd.DataFrame(columns=cols)

    city = df_demo_month.copy()
    city = city[city["criterio_norm"] == "ciudad"]
    city = city[city["ubicacion"].astype(str).str.strip() != ""]
    if city.empty:
        return pd.DataFrame(columns=cols)

    city_agg = city.groupby("ubicacion", as_index=False)["valor"].sum().rename(columns={"ubicacion": "ciudad"})
    city_total = float(city_agg["valor"].sum())
    if city_total <= 0:
        return pd.DataFrame(columns=cols)

    city_agg["city_pct"] = city_agg["valor"] / city_total
    total_inter = _metric_total(df_maestra_month, INTERACTION_ALIASES)
    total_vis = _metric_total(df_maestra_month, VISUALIZATION_ALIASES)

    city_agg["interacciones_estimadas"] = city_agg["city_pct"] * total_inter
    city_agg["visualizaciones_estimadas"] = city_agg["city_pct"] * total_vis
    city_agg["volumen_estimado"] = city_agg["interacciones_estimadas"] + city_agg["visualizaciones_estimadas"]
    city_agg = city_agg.drop(columns=["valor"]).sort_values("volumen_estimado", ascending=False).reset_index(drop=True)
    return city_agg


@st.cache_data(ttl=300)
def build_school_ranking(df_maestra_month_network: pd.DataFrame) -> pd.DataFrame:
    """Ranking de colegios por volumen aportado en el mes."""
    cols = ["colegio", "interacciones", "visualizaciones", "volumen_total", "aporte_pct"]
    if df_maestra_month_network is None or df_maestra_month_network.empty:
        return pd.DataFrame(columns=cols)

    local = df_maestra_month_network.copy()
    inter = (
        local[local["metrica_norm"].isin(INTERACTION_ALIASES)]
        .groupby("colegio", as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "interacciones"})
    )
    vis = (
        local[local["metrica_norm"].isin(VISUALIZATION_ALIASES)]
        .groupby("colegio", as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "visualizaciones"})
    )

    rank = pd.merge(inter, vis, on="colegio", how="outer").fillna(0.0)
    rank["volumen_total"] = rank["interacciones"] + rank["visualizaciones"]
    total = float(rank["volumen_total"].sum())
    rank["aporte_pct"] = (rank["volumen_total"] / total * 100.0) if total > 0 else 0.0
    rank = rank.sort_values("volumen_total", ascending=False).reset_index(drop=True)
    return rank


@st.cache_data(ttl=300)
def build_segment_distribution(df_demo_month: pd.DataFrame) -> pd.DataFrame:
    """Distribucion detallada de demografia base por sexo y edad en el mes."""
    cols = ["sexo", "edad", "segmento", "valor", "pct"]
    if df_demo_month is None or df_demo_month.empty:
        return pd.DataFrame(columns=cols)

    local = df_demo_month.copy()
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
def build_performance_vs_network(df_maestra_scope: pd.DataFrame, selected_school: str) -> pd.DataFrame:
    """Compara cuenta seleccionada vs promedio de red (excluyendo cuenta)."""
    cols = ["metrica", "cuenta", "red_promedio", "delta"]
    if df_maestra_scope is None or df_maestra_scope.empty or not selected_school or selected_school == "Todos":
        return pd.DataFrame(columns=cols)

    local = df_maestra_scope.copy()
    selected = local[local["colegio"].astype(str) == str(selected_school)].copy()
    network = local[local["colegio"].astype(str) != str(selected_school)].copy()
    if selected.empty or network.empty:
        return pd.DataFrame(columns=cols)

    def _school_totals(df: pd.DataFrame, aliases: set[str], out_name: str) -> pd.DataFrame:
        part = df[df["metrica_norm"].isin(aliases)]
        return part.groupby("colegio", as_index=False)["valor"].sum().rename(columns={"valor": out_name})

    selected_inter = _school_totals(selected, INTERACTION_ALIASES, "total")
    selected_vis = _school_totals(selected, VISUALIZATION_ALIASES, "total")
    network_inter = _school_totals(network, INTERACTION_ALIASES, "total")
    network_vis = _school_totals(network, VISUALIZATION_ALIASES, "total")

    cuenta_inter = float(selected_inter["total"].sum())
    cuenta_vis = float(selected_vis["total"].sum())
    red_inter = float(network_inter["total"].mean()) if not network_inter.empty else 0.0
    red_vis = float(network_vis["total"].mean()) if not network_vis.empty else 0.0

    result = pd.DataFrame(
        [
            {
                "metrica": "Interacciones",
                "cuenta": cuenta_inter,
                "red_promedio": red_inter,
                "delta": cuenta_inter - red_inter,
            },
            {
                "metrica": "Visualizaciones",
                "cuenta": cuenta_vis,
                "red_promedio": red_vis,
                "delta": cuenta_vis - red_vis,
            },
        ]
    )
    return result


@st.cache_data(ttl=300)
def build_demographic_vs_network(df_demo_scope: pd.DataFrame, selected_school: str) -> pd.DataFrame:
    """Compara perfil demografico de cuenta vs red (excluyendo cuenta)."""
    cols = ["segmento", "cuenta_pct", "red_pct", "delta_pp"]
    if df_demo_scope is None or df_demo_scope.empty or not selected_school or selected_school == "Todos":
        return pd.DataFrame(columns=cols)

    local = df_demo_scope.copy()
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

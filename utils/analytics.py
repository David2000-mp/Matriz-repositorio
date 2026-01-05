"""
Módulo de lógica de negocio para cálculos de métricas y crecimiento.
"""

from typing import List, Optional
import numpy as np
import pandas as pd

REQUIRED_COLUMNS = [
    "id_cuenta",
    "fecha",
    "seguidores",
    "alcance",
    "interacciones",
    "engagement_rate",
]


def _validate_input(df: pd.DataFrame) -> None:
    """Valida que el DataFrame tenga las columnas necesarias."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas en los datos: {missing}")


def _safe_pct_change(values: pd.Series) -> pd.Series:
    """Calcula el cambio porcentual manejando división por cero y nulos."""
    prev = values.shift(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        delta = (values - prev) / prev * 100.0

    # Si el valor anterior es 0 o nulo, el delta es NaN (o 0 según preferencia)
    delta[(prev == 0) | prev.isna()] = 0.0
    return delta.fillna(0.0)


def calculate_growth_metrics(df_metricas: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula métricas agrupadas por MES y sus variaciones (MoM y YoY).
    """
    # 1. Estructura de retorno vacía para Cold Start
    empty_structure = pd.DataFrame(
        columns=[
            "Mes",
            "Seguidores",
            "Delta_Seguidores",
            "YoY_Seguidores",
            "Interacciones",
            "Delta_Interacciones",
            "YoY_Interacciones",
            "Engagement",
            "Delta_Engagement",
            "YoY_Engagement",
        ]
    )

    if df_metricas is None or df_metricas.empty:
        return empty_structure

    # 2. Validación y Limpieza
    try:
        _validate_input(df_metricas)
    except ValueError as e:
        print(f"Error de validación: {e}")
        return empty_structure

    df = df_metricas.copy()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["fecha"])

    if df.empty:
        return empty_structure

    # 3. Agrupación Mensual (Global o filtrado previo)
    df["Mes_DT"] = df["fecha"].dt.to_period("M").dt.to_timestamp()  # type: ignore

    grouped = df.groupby("Mes_DT", as_index=False).agg(
        Seguidores=("seguidores", "sum"),
        Alcance=("alcance", "sum"),
        Interacciones=("interacciones", "sum"),
    )

    grouped = grouped.sort_values("Mes_DT").reset_index(drop=True)

    # 4. Cálculos de KPIs derivados
    # Preferimos calcular Engagement a partir del promedio de interacciones
    # de las últimas 23 publicaciones si están disponibles en los datos
    avg_last23 = None
    try:
        if len(df) >= 23 and "interacciones" in df.columns:
            avg_last23 = df.sort_values("fecha")["interacciones"].tail(23).mean()
    except Exception:
        avg_last23 = None

    # Evitamos división por cero en Engagement. Si calculamos avg_last23 lo usamos
    # como numerador (promedio por publicación); si no, usamos la suma mensual
    # de interacciones como antes.
    if avg_last23 is not None:
        grouped["Engagement"] = np.where(
            grouped["Seguidores"] > 0,
            (avg_last23 / grouped["Seguidores"]) * 100.0,
            0.0,
        )
    else:
        grouped["Engagement"] = np.where(
            grouped["Seguidores"] > 0,
            (grouped["Interacciones"] / grouped["Seguidores"]) * 100.0,
            0.0,
        )

    # 5. Cálculos de Variación (MoM y YoY)
    grouped["Delta_Seguidores"] = _safe_pct_change(grouped["Seguidores"])
    grouped["Delta_Interacciones"] = _safe_pct_change(grouped["Interacciones"])
    grouped["Delta_Engagement"] = _safe_pct_change(grouped["Engagement"])

    grouped["YoY_Seguidores"] = grouped["Seguidores"].pct_change(periods=12) * 100
    grouped["YoY_Interacciones"] = grouped["Interacciones"].pct_change(periods=12) * 100
    grouped["YoY_Engagement"] = grouped["Engagement"].pct_change(periods=12) * 100

    # Manejo de valores NaN e infinitos
    for col in ["YoY_Seguidores", "YoY_Interacciones", "YoY_Engagement"]:
        grouped[col] = grouped[col].replace([np.inf, -np.inf], np.nan).fillna(0)

    # 6. Formateo Final
    grouped["Mes"] = grouped["Mes_DT"].dt.strftime("%Y-%m")  # type: ignore

    result = grouped[
        [
            "Mes",
            "Seguidores",
            "Delta_Seguidores",
            "YoY_Seguidores",
            "Interacciones",
            "Delta_Interacciones",
            "YoY_Interacciones",
            "Engagement",
            "Delta_Engagement",
            "YoY_Engagement",
        ]
    ].copy()

    return result


def calculate_health_score(df: pd.DataFrame) -> float:
    """
    Calcula un score de salud digital entre 0 y 100.

    Componentes:
    - 50% Engagement Rate comparado contra el promedio histórico de la red.
    - 30% Crecimiento YoY de seguidores (solo positivo aporta puntos).
    - 20% Consistencia: proporción de plataformas con actividad en el mes más reciente.

    La función es robusta ante divisiones por cero y datos faltantes.
    """
    if df is None or df.empty:
        return 0.0

    dfc = df.copy()
    # Asegurar fechas
    if "fecha" in dfc.columns:
        dfc["fecha"] = pd.to_datetime(dfc["fecha"], errors="coerce")
        dfc = dfc.dropna(subset=["fecha"])

    if dfc.empty:
        return 0.0

    # Determinar mes actual (última fecha disponible)
    dfc["Mes"] = dfc["fecha"].dt.to_period("M").dt.to_timestamp()  # type: ignore
    latest_month = dfc["Mes"].max()
    if pd.isna(latest_month):
        return 0.0

    # Engagement current month: sum(interacciones)/sum(seguidores) *100
    curr = dfc[dfc["Mes"] == latest_month]
    total_seguidores_curr = int(curr["seguidores"].sum()) if "seguidores" in curr.columns else 0
    total_interacciones_curr = int(curr["interacciones"].sum()) if "interacciones" in curr.columns else 0

    if total_seguidores_curr > 0:
        engagement_curr = (total_interacciones_curr / total_seguidores_curr) * 100.0
    else:
        engagement_curr = 0.0

    # Historical mean engagement: calcular por mes excluyendo el mes actual
    historical_mean_engagement = 0.0
    if ("interacciones" in dfc.columns) and ("seguidores" in dfc.columns):
        months = dfc.groupby("Mes")[["interacciones", "seguidores"]].sum().reset_index()
        months = months[months["Mes"] != latest_month]
        if not months.empty:
            months["eng_rate"] = months.apply(
                lambda r: (r["interacciones"] / r["seguidores"] * 100.0) if r["seguidores"] > 0 else 0.0,
                axis=1,
            )
            historical_mean_engagement = months["eng_rate"].mean()

    # Engagement score component (50 puntos)
    if historical_mean_engagement > 0:
        ratio = engagement_curr / historical_mean_engagement
        ratio = max(0.0, min(ratio, 2.0))  # cap at 2x
        engagement_component = (ratio / 2.0) * 50.0
    else:
        engagement_component = 50.0 if engagement_curr > 0 else 0.0

    # YoY growth (30 puntos) - comparar mismo mes año anterior
    try:
        prev_year_month = (latest_month - pd.offsets.DateOffset(years=1))
        prev = dfc[dfc["Mes"] == prev_year_month]
        total_seguidores_prev = int(prev["seguidores"].sum()) if not prev.empty and "seguidores" in prev.columns else 0
        if total_seguidores_prev > 0:
            yoy_pct = (total_seguidores_curr - total_seguidores_prev) / total_seguidores_prev * 100.0
        else:
            yoy_pct = 0.0
    except Exception:
        yoy_pct = 0.0

    if yoy_pct > 0:
        yoy_component = min(yoy_pct, 100.0) / 100.0 * 30.0
    else:
        yoy_component = 0.0

    # Consistencia (20 puntos) - plataformas con actividad en el mes más reciente
    total_platforms = int(dfc["plataforma"].nunique()) if "plataforma" in dfc.columns else 0
    platforms_curr = int(curr["plataforma"].nunique()) if "plataforma" in curr.columns else 0
    if total_platforms > 0:
        consistency_component = (platforms_curr / total_platforms) * 20.0
    else:
        consistency_component = 0.0

    score = engagement_component + yoy_component + consistency_component
    # Clamp 0-100
    score = max(0.0, min(score, 100.0))
    return float(score)


def apply_smoothing(df: pd.DataFrame, column: str = "seguidores", window: int = 3) -> pd.DataFrame:
    """
    Añade una columna de tendencia suavizada (promedio móvil) para la columna indicada.

    - Agrupa por `id_cuenta` (si existe) y ordena por `fecha` antes de aplicar
      .rolling(window).mean().
    - Crea la columna `<column>_tendencia` y la deja en el DataFrame retornado.
    """
    if df is None or df.empty:
        return df

    df_out = df.copy()
    if "fecha" not in df_out.columns:
        return df_out

    # Asegurar tipos
    df_out["fecha"] = pd.to_datetime(df_out["fecha"], errors="coerce")
    if "id_cuenta" in df_out.columns:
        # Aplicar por grupo
        trend_col = f"{column}_tendencia"

        def _apply_group(g):
            g = g.sort_values("fecha")
            g[trend_col] = g[column].rolling(window=window, min_periods=1).mean()
            return g

        df_out = df_out.groupby("id_cuenta", group_keys=False).apply(_apply_group)
    else:
        # Global rolling (por fecha ordenada)
        df_out = df_out.sort_values("fecha")
        trend_col = f"{column}_tendencia"
        df_out[trend_col] = df_out[column].rolling(window=window, min_periods=1).mean()

    return df_out  # type: ignore


def apply_moving_average(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Calcula el promedio móvil de 3 meses para `col` y agrega `<col>_ma3`.

    - Fuerza `fecha` a datetime y ordena por fecha.
    - Si existe `id_cuenta`, aplica el rolling por grupo; si no, lo aplica globalmente.
    """
    if df is None or df.empty:
        return df

    # Reutilizar apply_smoothing para lógica de rolling y luego renombrar la columna
    df_out = apply_smoothing(df, column=col, window=3).copy()
    trend_col = f"{col}_tendencia"
    ma_col = f"{col}_ma3"

    if trend_col in df_out.columns:
        df_out[ma_col] = df_out[trend_col]
    else:
        # Fallback manual por si no existía la columna original
        df_out = df_out.copy()
        if "fecha" in df_out.columns:
            df_out["fecha"] = pd.to_datetime(df_out["fecha"], errors="coerce")
            df_out = df_out.sort_values("fecha")
            df_out[ma_col] = df_out[col].rolling(window=3, min_periods=1).mean()

    return df_out

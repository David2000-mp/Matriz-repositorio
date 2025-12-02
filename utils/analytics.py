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
    Calcula métricas agrupadas por MES y sus variaciones (MoM).
    """
    # 1. Estructura de retorno vacía para Cold Start
    empty_structure = pd.DataFrame(columns=[
        "Mes", "Seguidores", "Delta_Seguidores", 
        "Interacciones", "Delta_Interacciones", 
        "Engagement", "Delta_Engagement"
    ])

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
    df["Mes_DT"] = df["fecha"].dt.to_period("M").dt.to_timestamp()

    grouped = df.groupby("Mes_DT", as_index=False).agg(
        Seguidores=("seguidores", "sum"),
        Alcance=("alcance", "sum"),
        Interacciones=("interacciones", "sum"),
    )
    
    grouped = grouped.sort_values("Mes_DT").reset_index(drop=True)

    # 4. Cálculos de KPIs derivados
    # Evitamos división por cero en Engagement
    grouped["Engagement"] = np.where(
        grouped["Seguidores"] > 0,
        (grouped["Interacciones"] / grouped["Seguidores"]) * 100.0,
        0.0
    )

    # 5. Cálculos de Variación (MoM)
    grouped["Delta_Seguidores"] = _safe_pct_change(grouped["Seguidores"])
    grouped["Delta_Interacciones"] = _safe_pct_change(grouped["Interacciones"])
    grouped["Delta_Engagement"] = _safe_pct_change(grouped["Engagement"])

    # 6. Formateo Final
    grouped["Mes"] = grouped["Mes_DT"].dt.strftime("%Y-%m")

    result = grouped[[
        "Mes",
        "Seguidores", "Delta_Seguidores",
        "Interacciones", "Delta_Interacciones",
        "Engagement", "Delta_Engagement",
    ]].copy()

    return result
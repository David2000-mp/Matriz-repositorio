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


def normalize_latest_by_account(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """Devuelve un snapshot con el último registro por cuenta y periodo.

    - Si freq == "M", mantiene el último registro por id_cuenta y mes.
    - Agrega columna `seguidores_prev` para delta contra la medición anterior.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=df.columns if df is not None else [])

    dfc = df.copy()
    if "fecha" not in dfc.columns:
        return dfc

    dfc["fecha"] = pd.to_datetime(dfc["fecha"], errors="coerce")
    dfc = dfc.dropna(subset=["fecha"])
    for col in ("seguidores", "interacciones"):
        if col in dfc.columns:
            dfc[col] = pd.to_numeric(dfc[col], errors="coerce").fillna(0)

    group_keys = ["id_cuenta"] if "id_cuenta" in dfc.columns else ["entidad", "plataforma"]
    dfc = dfc.sort_values(group_keys + ["fecha"])

    if freq.upper() == "M":
        dfc["periodo"] = dfc["fecha"].dt.to_period("M")
        latest_rows = dfc.groupby(group_keys + ["periodo"], as_index=False).tail(1).copy()
        latest_rows["fecha"] = latest_rows["periodo"].dt.to_timestamp()
        latest_rows = latest_rows.drop(columns=["periodo"])
    else:
        latest_rows = dfc.groupby(group_keys, as_index=False).tail(1).copy()

    # Calcula seguidores_prev para cada fila del latest_rows
    # Busca el segundo último registro de cada grupo
    seguidores_prev_list = []
    for group_val, group_df in dfc.groupby(group_keys):
        # Asegurar que group_val sea siempre una tupla
        if not isinstance(group_val, tuple):
            group_val = (group_val,)
        
        if len(group_df) > 1:
            prev_value = group_df.iloc[-2]["seguidores"]
        else:
            prev_value = 0
        seguidores_prev_list.append((group_val, prev_value))
    
    # Crea diccionario para lookup rápido
    prev_dict = {k: v for k, v in seguidores_prev_list}
    
    # Aplica seguidores_prev basado en el grupo
    def get_prev_value(row):
        # Construir la clave del mismo modo que en el groupby
        if len(group_keys) == 1:
            key = (row[group_keys[0]],)
        else:
            key = tuple(row[k] for k in group_keys)
        return prev_dict.get(key, 0)
    
    latest_rows["seguidores_prev"] = latest_rows.apply(get_prev_value, axis=1)
    latest_rows["seguidores_prev"] = latest_rows["seguidores_prev"].fillna(0)
    return latest_rows


def normalize_monthly_latest(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience: obtiene último registro por cuenta y mes."""
    return normalize_latest_by_account(df, freq="M")


def summarize_followers_growth(df_metricas: pd.DataFrame) -> dict:
    """Resumen agregado de seguidores usando el último corte por cuenta.

    Retorna totales actuales, previos, delta absoluto y delta porcentual
    más el snapshot utilizado para desglose.
    """
    snapshot = normalize_latest_by_account(df_metricas)
    total = int(snapshot["seguidores"].sum()) if not snapshot.empty and "seguidores" in snapshot else 0
    total_prev = int(snapshot.get("seguidores_prev", pd.Series()).fillna(0).sum()) if not snapshot.empty else 0
    delta_abs = total - total_prev
    delta_pct = (delta_abs / total_prev * 100.0) if total_prev > 0 else 0.0
    return {
        "total": total,
        "total_prev": total_prev,
        "delta_abs": delta_abs,
        "delta_pct": delta_pct,
        "snapshot": snapshot,
    }


def calculate_likes_promedio(engagement_rate: float, seguidores: int) -> float:
    """Calcula likes_promedio automáticamente basado en engagement_rate.

    Fórmula INVERTIDA (v2.2):
        likes_promedio = seguidores * (engagement_rate / 100)
    
    Esta fórmula representa el número de interacciones/likes totales
    esperadas basadas en la tasa de engagement.

    Args:
        engagement_rate: Tasa de engagement en porcentaje (0-100)
        seguidores: Número total de seguidores

    Returns:
        float: Likes promedio redondeado a 2 decimales
    
    Ejemplo:
        - Seguidores: 10,000
        - Engagement Rate: 5.5%
        - Resultado: 10,000 * 0.055 = 550 likes
    """
    if seguidores <= 0 or engagement_rate <= 0:
        return 0.0
    
    # Fórmula simplificada: likes = seguidores * (engagement_rate / 100)
    likes_promedio = seguidores * (engagement_rate / 100.0)
    
    return round(likes_promedio, 2)


def estimate_reach(plataforma: str, seguidores: int, engagement_rate: float) -> int:
    """
    Estima el alcance esperado combinando un multiplicador por plataforma
    y un bono basado en engagement.

    Fórmula propuesta (heurística):
        base = seguidores * platform_factor
        bonus = seguidores * (engagement_rate / 100.0) * engagement_bonus_factor
        estimated_reach = base + bonus

    Los factores por plataforma son iniciales y ajustables. Dejar un hook
    para reemplazar por un modelo de regresión (scikit-learn) en el futuro.

    Args:
        plataforma: Nombre de la red social (ej. 'Instagram')
        seguidores: Número de seguidores
        engagement_rate: Engagement en porcentaje (0-100)

    Returns:
        int: Estimación de alcance (valor entero)
    """
    if seguidores <= 0:
        return 0

    # Factores iniciales por plataforma (ajustables)
    platform_factors = {
        "Instagram": 0.15,
        "Facebook": 0.10,
        "TikTok": 0.20,
        "Twitter": 0.05,
    }

    platform_factor = platform_factors.get(plataforma, 0.10)
    engagement_bonus_factor = 0.5  # parte del engagement que contribuye al alcance

    base = seguidores * platform_factor
    bonus = seguidores * (engagement_rate / 100.0) * engagement_bonus_factor
    estimated = base + bonus

    # Hook para futura integración ML (ejemplo, reemplazar por model.predict(features))
    # TODO: Entrenar regresor y llamar aquí para obtener estimaciones más precisas.

    return int(round(estimated))


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
    # Forzar consistencia de tipos en id_cuenta para evitar errores de merge
    if "id_cuenta" in df.columns:
        try:
            df["id_cuenta"] = df["id_cuenta"].astype(str)
        except Exception:
            pass
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["fecha"])

    # Usar último registro por cuenta y mes para evitar doble conteo
    df = normalize_monthly_latest(df)
    if df.empty:
        return empty_structure

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

        # Evitar FutureWarning de Pandas pasando include_groups=False
        df_out = df_out.groupby("id_cuenta", group_keys=False).apply(
            _apply_group,
            include_groups=False,
        )
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


def detect_anomalies(df: pd.DataFrame, threshold: float = 0.20) -> pd.DataFrame:
    """
    Detecta anomalías en métricas comparando contra el promedio móvil o mes anterior.

    Para cada registro mensual, calcula la variación porcentual contra:
    1. Promedio Móvil de 3 meses (si disponible)
    2. Mes anterior (como fallback)

    Marca como anomalía si la variación absoluta > threshold (ej. 20%).

    Args:
        df: DataFrame con columnas 'fecha', 'seguidores', 'interacciones', etc.
        threshold: Umbral de variación porcentual (0.20 = 20%)

    Returns:
        DataFrame con columnas adicionales 'anomalia_seguidores', 'anomalia_interacciones'
    """
    if df is None or df.empty:
        return df

    df_out = df.copy()
    df_out["fecha"] = pd.to_datetime(df_out["fecha"], errors="coerce")
    df_out = df_out.dropna(subset=["fecha"]).sort_values("fecha")

    # Aplicar MA si no existe
    if "seguidores_ma3" not in df_out.columns:
        df_out = apply_moving_average(df_out, "seguidores")
    if "interacciones_ma3" not in df_out.columns and "interacciones" in df_out.columns:
        df_out = apply_moving_average(df_out, "interacciones")

    # Función para detectar anomalía en una columna
    def _detect_anomaly(series, ma_series, prev_series):
        anomalies = pd.Series(False, index=series.index)
        for i in range(len(series)):
            current = series.iloc[i]
            # Preferir MA si disponible
            if not pd.isna(ma_series.iloc[i]) and ma_series.iloc[i] != 0:
                baseline = ma_series.iloc[i]
            elif i > 0 and not pd.isna(prev_series.iloc[i-1]):
                baseline = prev_series.iloc[i-1]
            else:
                continue  # No baseline available

            if baseline != 0:
                variation = abs((current - baseline) / baseline)
                if variation > threshold:
                    anomalies.iloc[i] = True
        return anomalies

    # Detectar para seguidores
    if "seguidores" in df_out.columns:
        prev_seguidores = df_out["seguidores"].shift(1)
        ma_seguidores = df_out.get("seguidores_ma3", pd.Series(dtype=float))
        df_out["anomalia_seguidores"] = _detect_anomaly(df_out["seguidores"], ma_seguidores, prev_seguidores)

    # Detectar para interacciones
    if "interacciones" in df_out.columns:
        prev_interacciones = df_out["interacciones"].shift(1)
        ma_interacciones = df_out.get("interacciones_ma3", pd.Series(dtype=float))
        df_out["anomalia_interacciones"] = _detect_anomaly(df_out["interacciones"], ma_interacciones, prev_interacciones)

    return df_out

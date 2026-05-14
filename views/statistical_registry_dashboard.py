"""Vista de registro estadistico 360 para CHAMPILEAKS.

Incluye:
- Resumen ejecutivo de indicadores
- Estadistica descriptiva
- Inferencia (bootstrap + permutaciones)
- Predictiva baseline (tendencia lineal)
- Registro exportable de hallazgos
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components import PLOTLY_CONFIG, PLOTLY_LAYOUT_DEFAULTS
from utils.data_provider import data_provider

FEEDBACK_PATH = Path(__file__).resolve().parent.parent / "data" / "comment_feedback.csv"


def _apply_dark_chart_text(fig: go.Figure) -> None:
    fig.update_layout(
        font={"color": "#212529"},
        title={"font": {"color": "#212529"}},
        legend={"font": {"color": "#212529"}},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
    )
    fig.update_xaxes(
        title_font={"color": "#212529"},
        tickfont={"color": "#212529"},
        color="#212529",
        gridcolor="#E0E0E0",
    )
    fig.update_yaxes(
        title_font={"color": "#212529"},
        tickfont={"color": "#212529"},
        color="#212529",
        gridcolor="#E0E0E0",
    )


def _resolve_global_filters(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    entidad_global = st.session_state.get("filtro_entidad", "Todas")
    mes_global = st.session_state.get("filtro_mes", "Todos")

    if entidad_global != "Todas" and "entidad" in filtered.columns:
        filtered = filtered[filtered["entidad"].astype(str) == str(entidad_global)]

    if mes_global != "Todos" and "fecha" in filtered.columns:
        fechas = pd.to_datetime(filtered["fecha"], errors="coerce")
        periodos = fechas.dt.strftime("%Y-%m")
        filtered = filtered[periodos == str(mes_global)]

    return filtered


def _safe_numeric_series(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[col], errors="coerce").dropna()


def _benjamini_hochberg(p_values: list[float]) -> list[float]:
    """Aplica correccion Benjamini-Hochberg para controlar FDR."""
    if not p_values:
        return []

    m = len(p_values)
    ordered = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [0.0] * m

    prev = 1.0
    for rank in range(m, 0, -1):
        idx, p = ordered[rank - 1]
        bh_val = min(prev, (p * m) / rank)
        adjusted[idx] = float(min(1.0, max(0.0, bh_val)))
        prev = bh_val

    return adjusted


def _wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    """Calcula intervalo de confianza Wilson para una proporcion."""
    if n <= 0:
        return np.nan, np.nan, np.nan

    p = successes / n
    denom = 1 + (z**2 / n)
    center = (p + (z**2 / (2 * n))) / denom
    margin = (z * np.sqrt((p * (1 - p) / n) + (z**2 / (4 * n**2)))) / denom
    return float(p), float(max(0.0, center - margin)), float(min(1.0, center + margin))


def _predict_next_linear(train: np.ndarray) -> float:
    if len(train) < 2:
        return float(train[-1]) if len(train) == 1 else np.nan
    x = np.arange(len(train), dtype=float)
    slope, intercept = np.polyfit(x, train, 1)
    return float(intercept + slope * len(train))


def _predict_next_moving_average(train: np.ndarray, window: int = 3) -> float:
    if len(train) == 0:
        return np.nan
    w = max(1, min(int(window), len(train)))
    return float(np.mean(train[-w:]))


def _walk_forward_backtest(series: pd.Series, min_train: int = 6) -> dict[str, Any]:
    """Backtesting walk-forward para comparar baseline lineal vs moving average."""
    y = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)
    if len(y) <= min_train:
        return {
            "enough_data": False,
            "results": pd.DataFrame(),
            "summary": {},
        }

    rows: list[dict[str, float]] = []
    for t in range(min_train, len(y)):
        train = y[:t]
        actual = float(y[t])
        pred_linear = _predict_next_linear(train)
        pred_ma3 = _predict_next_moving_average(train, window=3)
        rows.append(
            {
                "t": float(t),
                "actual": actual,
                "pred_linear": float(pred_linear),
                "pred_ma3": float(pred_ma3),
            }
        )

    bt = pd.DataFrame(rows)
    for model_col in ["pred_linear", "pred_ma3"]:
        err_col = model_col.replace("pred_", "err_")
        ape_col = model_col.replace("pred_", "ape_")
        bt[err_col] = np.abs(bt["actual"] - bt[model_col])
        denom = np.where(np.abs(bt["actual"]) > 1e-9, np.abs(bt["actual"]), np.nan)
        bt[ape_col] = np.abs((bt["actual"] - bt[model_col]) / denom) * 100.0

    summary = {
        "linear": {
            "mae": float(bt["err_linear"].mean()),
            "mape": float(np.nanmean(bt["ape_linear"])),
        },
        "ma3": {
            "mae": float(bt["err_ma3"].mean()),
            "mape": float(np.nanmean(bt["ape_ma3"])),
        },
    }
    summary["best_model"] = "linear" if summary["linear"]["mae"] <= summary["ma3"]["mae"] else "ma3"

    return {
        "enough_data": True,
        "results": bt,
        "summary": summary,
    }


def _bootstrap_ci_mean_diff(
    x: np.ndarray,
    y: np.ndarray,
    n_boot: int = 2000,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    observed = float(np.mean(x) - np.mean(y))
    if len(x) < 2 or len(y) < 2:
        return observed, np.nan, np.nan

    rng = np.random.default_rng(42)
    samples = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        xs = rng.choice(x, size=len(x), replace=True)
        ys = rng.choice(y, size=len(y), replace=True)
        samples[i] = float(np.mean(xs) - np.mean(ys))

    low = float(np.quantile(samples, alpha / 2))
    high = float(np.quantile(samples, 1 - alpha / 2))
    return observed, low, high


def _permutation_pvalue_mean_diff(
    x: np.ndarray,
    y: np.ndarray,
    n_perm: int = 2000,
) -> float:
    if len(x) < 2 or len(y) < 2:
        return np.nan

    observed = abs(float(np.mean(x) - np.mean(y)))
    combined = np.concatenate([x, y])
    n_x = len(x)

    rng = np.random.default_rng(42)
    count = 0
    for _ in range(n_perm):
        rng.shuffle(combined)
        diff = abs(float(np.mean(combined[:n_x]) - np.mean(combined[n_x:])))
        if diff >= observed:
            count += 1

    return float((count + 1) / (n_perm + 1))


def _cohen_d(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2 or len(y) < 2:
        return np.nan

    s1 = np.var(x, ddof=1)
    s2 = np.var(y, ddof=1)
    n1 = len(x)
    n2 = len(y)
    pooled = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / max(1, (n1 + n2 - 2)))
    if pooled == 0:
        return 0.0
    return float((np.mean(x) - np.mean(y)) / pooled)


def _fit_linear_forecast(series: pd.Series, horizon: int = 6) -> pd.DataFrame:
    if series.empty:
        return pd.DataFrame(columns=["step", "y_hat", "lower", "upper", "kind"])

    y = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)
    if len(y) < 3:
        return pd.DataFrame(columns=["step", "y_hat", "lower", "upper", "kind"])

    x = np.arange(len(y), dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    y_hat_hist = intercept + slope * x
    residuals = y - y_hat_hist
    sigma = float(np.std(residuals, ddof=1)) if len(residuals) > 2 else 0.0

    x_future = np.arange(len(y), len(y) + int(horizon), dtype=float)
    y_hat_future = intercept + slope * x_future
    ci = 1.96 * sigma

    hist = pd.DataFrame(
        {
            "step": np.arange(len(y), dtype=int),
            "y_hat": y_hat_hist,
            "lower": y_hat_hist - ci,
            "upper": y_hat_hist + ci,
            "kind": "historico_ajustado",
            "y_real": y,
        }
    )
    future = pd.DataFrame(
        {
            "step": np.arange(len(y), len(y) + int(horizon), dtype=int),
            "y_hat": y_hat_future,
            "lower": y_hat_future - ci,
            "upper": y_hat_future + ci,
            "kind": "forecast",
            "y_real": np.nan,
        }
    )

    out = pd.concat([hist, future], ignore_index=True)
    return out


def _fit_moving_average_forecast(series: pd.Series, horizon: int = 6, window: int = 3) -> pd.DataFrame:
    if series.empty:
        return pd.DataFrame(columns=["step", "y_hat", "lower", "upper", "kind"])

    y = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)
    if len(y) < 3:
        return pd.DataFrame(columns=["step", "y_hat", "lower", "upper", "kind"])

    hist_hat = np.empty(len(y), dtype=float)
    hist_hat[0] = y[0]
    for i in range(1, len(y)):
        w = min(window, i)
        hist_hat[i] = float(np.mean(y[i - w:i]))

    residuals = y - hist_hat
    sigma = float(np.std(residuals[1:], ddof=1)) if len(residuals) > 3 else 0.0
    ci = 1.96 * sigma

    simulated = list(y.copy())
    future_hat = []
    for _ in range(int(horizon)):
        w = min(window, len(simulated))
        pred = float(np.mean(simulated[-w:]))
        future_hat.append(pred)
        simulated.append(pred)

    hist = pd.DataFrame(
        {
            "step": np.arange(len(y), dtype=int),
            "y_hat": hist_hat,
            "lower": hist_hat - ci,
            "upper": hist_hat + ci,
            "kind": "historico_ajustado",
            "y_real": y,
        }
    )
    future = pd.DataFrame(
        {
            "step": np.arange(len(y), len(y) + int(horizon), dtype=int),
            "y_hat": np.asarray(future_hat, dtype=float),
            "lower": np.asarray(future_hat, dtype=float) - ci,
            "upper": np.asarray(future_hat, dtype=float) + ci,
            "kind": "forecast",
            "y_real": np.nan,
        }
    )
    return pd.concat([hist, future], ignore_index=True)


def _build_recommendation(indicador: str, valor: float) -> tuple[str, str]:
    """Devuelve nivel de riesgo y recomendacion accionable."""
    if indicador == "accuracy_clasificador":
        if valor < 0.70:
            return "alto", "Reentrenar reglas de sentimiento y revisar etiquetas de feedback criticas."
        if valor < 0.85:
            return "medio", "Monitorear casos ambiguos y ampliar muestra de validacion manual."
        return "bajo", "Mantener monitoreo semanal para sostener precision."

    if indicador == "engagement_media":
        if valor < 1.0:
            return "alto", "Activar plan de contenido correctivo y revisar frecuencia de publicacion."
        if valor < 2.5:
            return "medio", "Optimizar mix de formatos y horarios de publicacion."
        return "bajo", "Mantener estrategia actual y hacer pruebas A/B ligeras."

    if indicador == "engagement_mediana":
        if valor < 1.0:
            return "alto", "Reforzar contenidos de mayor respuesta y reducir formatos de bajo rendimiento."
        if valor < 2.0:
            return "medio", "Ajustar calendario y llamadas a la accion por plataforma."
        return "bajo", "Sostener linea editorial y monitorear tendencia mensual."

    return "medio", "Revisar indicador en contexto con filtros de entidad, plataforma y periodo."


def _load_feedback_df() -> pd.DataFrame:
    if not FEEDBACK_PATH.exists():
        return pd.DataFrame(
            columns=[
                "timestamp",
                "comment",
                "predicted_label",
                "predicted_score",
                "correct_label",
                "correct_score",
                "was_correct",
            ]
        )

    df = pd.read_csv(FEEDBACK_PATH)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    if "was_correct" in df.columns:
        df["was_correct"] = df["was_correct"].astype(str).str.lower().map(
            {"true": True, "false": False}
        )

    for col in ["predicted_score", "correct_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def _build_registry_rows(df_metricas: pd.DataFrame, df_feedback: pd.DataFrame) -> pd.DataFrame:
    now = pd.Timestamp.now(tz="UTC")
    rows: list[dict[str, Any]] = []

    eng = _safe_numeric_series(df_metricas, "engagement_rate")
    seguidores = _safe_numeric_series(df_metricas, "seguidores")

    if not eng.empty:
        riesgo, recomendacion = _build_recommendation("engagement_media", float(eng.mean()))
        rows.append(
            {
                "timestamp": now,
                "modulo": "descriptiva",
                "indicador": "engagement_media",
                "valor": float(eng.mean()),
                "interpretacion": "Promedio global de engagement en el periodo filtrado",
                "confianza": "media",
                "riesgo": riesgo,
                "recomendacion": recomendacion,
            }
        )
        riesgo, recomendacion = _build_recommendation("engagement_mediana", float(eng.median()))
        rows.append(
            {
                "timestamp": now,
                "modulo": "descriptiva",
                "indicador": "engagement_mediana",
                "valor": float(eng.median()),
                "interpretacion": "Valor central robusto de engagement",
                "confianza": "media",
                "riesgo": riesgo,
                "recomendacion": recomendacion,
            }
        )

    if not seguidores.empty:
        riesgo, recomendacion = _build_recommendation("seguidores_media", float(seguidores.mean()))
        rows.append(
            {
                "timestamp": now,
                "modulo": "descriptiva",
                "indicador": "seguidores_media",
                "valor": float(seguidores.mean()),
                "interpretacion": "Tamano promedio de audiencia por registro",
                "confianza": "media",
                "riesgo": riesgo,
                "recomendacion": recomendacion,
            }
        )

    if not df_feedback.empty and "was_correct" in df_feedback.columns:
        acc = pd.to_numeric(df_feedback["was_correct"], errors="coerce").dropna()
        if not acc.empty:
            p_hat, wilson_low, wilson_high = _wilson_interval(int(acc.sum()), int(len(acc)))
            riesgo, recomendacion = _build_recommendation("accuracy_clasificador", float(acc.mean()))
            rows.append(
                {
                    "timestamp": now,
                    "modulo": "calidad_feedback",
                    "indicador": "accuracy_clasificador",
                    "valor": float(acc.mean()),
                    "interpretacion": (
                        "Precision historica del clasificador de sentimiento "
                        f"(Wilson 95%: {wilson_low:.3f} - {wilson_high:.3f})"
                    ),
                    "confianza": "alta" if len(acc) >= 30 else "media",
                    "riesgo": riesgo,
                    "recomendacion": recomendacion,
                    "valor_wilson": p_hat,
                    "wilson_low": wilson_low,
                    "wilson_high": wilson_high,
                }
            )

    return pd.DataFrame(rows)


def _render_summary(df_metricas: pd.DataFrame, df_feedback: pd.DataFrame) -> None:
    st.subheader("Resumen ejecutivo")

    engagement = _safe_numeric_series(df_metricas, "engagement_rate")
    seguidores = _safe_numeric_series(df_metricas, "seguidores")
    interacciones = _safe_numeric_series(df_metricas, "interacciones")

    feedback_total = len(df_feedback)
    feedback_acc = np.nan
    feedback_w_low = np.nan
    feedback_w_high = np.nan
    if not df_feedback.empty and "was_correct" in df_feedback.columns:
        acc_values = pd.to_numeric(df_feedback["was_correct"], errors="coerce").dropna()
        feedback_acc = acc_values.mean() if not acc_values.empty else np.nan
        if not acc_values.empty:
            _, feedback_w_low, feedback_w_high = _wilson_interval(int(acc_values.sum()), int(len(acc_values)))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros metricas", f"{len(df_metricas):,}")
    c2.metric("Engagement medio", f"{engagement.mean():.2f}%" if not engagement.empty else "N/A")
    c3.metric("Seguidores medios", f"{seguidores.mean():,.0f}" if not seguidores.empty else "N/A")
    c4.metric("Accuracy feedback", f"{feedback_acc:.1%}" if pd.notna(feedback_acc) else "N/A")

    if not interacciones.empty and not seguidores.empty and seguidores.sum() > 0:
        rate = (interacciones.sum() / seguidores.sum()) * 100
        st.caption(f"Engagement agregado (interacciones/seguidores): {rate:.2f}%")

    st.caption(f"Feedback acumulado: {feedback_total:,} observaciones")
    if pd.notna(feedback_w_low) and pd.notna(feedback_w_high):
        st.caption(f"IC Wilson 95% de accuracy: [{feedback_w_low:.1%}, {feedback_w_high:.1%}]")


def _render_descriptive(df_metricas: pd.DataFrame, df_feedback: pd.DataFrame) -> None:
    st.subheader("Estadistica descriptiva")

    metric_options = [
        col
        for col in ["engagement_rate", "seguidores", "interacciones", "alcance", "likes_promedio"]
        if col in df_metricas.columns
    ]

    if not metric_options:
        st.warning("No hay columnas numericas disponibles en metricas para estadistica descriptiva.")
        return

    selected_metric = st.selectbox("Metrica numerica", options=metric_options, key="stats_desc_metric")
    series = _safe_numeric_series(df_metricas, selected_metric)

    if series.empty:
        st.info("No hay datos numericos suficientes para la metrica seleccionada.")
        return

    q1 = float(series.quantile(0.25))
    q3 = float(series.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = series[(series < lower) | (series > upper)]

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Media", f"{series.mean():.3f}")
    k2.metric("Mediana", f"{series.median():.3f}")
    k3.metric("Desv. estandar", f"{series.std(ddof=1):.3f}" if len(series) > 1 else "0.000")
    k4.metric("IQR", f"{iqr:.3f}")
    k5.metric("Atipicos", f"{len(outliers):,}")

    hist = px.histogram(series.to_frame(name=selected_metric), x=selected_metric, nbins=30, title=f"Distribucion de {selected_metric}")
    hist.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
    _apply_dark_chart_text(hist)
    st.plotly_chart(hist, width="stretch", config=PLOTLY_CONFIG)

    box = px.box(series.to_frame(name=selected_metric), y=selected_metric, title=f"Boxplot de {selected_metric}")
    box.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
    _apply_dark_chart_text(box)
    st.plotly_chart(box, width="stretch", config=PLOTLY_CONFIG)

    if not df_feedback.empty and "correct_label" in df_feedback.columns:
        freq = (
            df_feedback["correct_label"].fillna("Desconocido").astype(str).value_counts().reset_index()
        )
        freq.columns = ["label", "total"]
        fig_bar = px.bar(freq, x="label", y="total", title="Frecuencia de etiqueta correcta en feedback")
        fig_bar.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
        _apply_dark_chart_text(fig_bar)
        st.plotly_chart(fig_bar, width="stretch", config=PLOTLY_CONFIG)


def _render_inference(df_metricas: pd.DataFrame, df_feedback: pd.DataFrame) -> None:
    st.subheader("Inferencia")
    st.caption("Comparacion de grupos con bootstrap (IC) y permutaciones (p-value).")

    group_col = "plataforma" if "plataforma" in df_metricas.columns else None
    if group_col is None:
        st.warning("No se encontro columna de grupo (plataforma) para inferencia.")
        return

    metric_options = [
        col
        for col in ["engagement_rate", "seguidores", "interacciones", "alcance", "likes_promedio"]
        if col in df_metricas.columns
    ]
    if not metric_options:
        st.warning("No hay metricas numericas para inferencia.")
        return

    groups = sorted([str(v) for v in df_metricas[group_col].dropna().unique() if str(v).strip()])
    if len(groups) < 2:
        st.info("Se requieren al menos 2 grupos para comparar.")
        return

    col_a, col_b, col_m = st.columns(3)
    g1 = col_a.selectbox("Grupo A", options=groups, key="stats_inf_g1")
    g2 = col_b.selectbox("Grupo B", options=[g for g in groups if g != g1], key="stats_inf_g2")
    metric = col_m.selectbox("Metrica", options=metric_options, key="stats_inf_metric")

    x = pd.to_numeric(df_metricas[df_metricas[group_col].astype(str) == str(g1)][metric], errors="coerce").dropna().to_numpy(dtype=float)
    y = pd.to_numeric(df_metricas[df_metricas[group_col].astype(str) == str(g2)][metric], errors="coerce").dropna().to_numpy(dtype=float)

    if len(x) < 5 or len(y) < 5:
        st.warning("Muestra insuficiente: se recomiendan al menos 5 observaciones por grupo.")
        return

    diff, ci_low, ci_high = _bootstrap_ci_mean_diff(x, y)
    p_value = _permutation_pvalue_mean_diff(x, y)
    effect = _cohen_d(x, y)

    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Dif media A-B", f"{diff:.4f}")
    i2.metric("IC95% inferior", f"{ci_low:.4f}")
    i3.metric("IC95% superior", f"{ci_high:.4f}")
    i4.metric("p-value", f"{p_value:.4f}" if pd.notna(p_value) else "N/A")

    st.metric("Tamano de efecto (Cohen d)", f"{effect:.3f}" if pd.notna(effect) else "N/A")

    if pd.notna(p_value):
        if p_value < 0.01:
            st.success("Evidencia fuerte de diferencia entre grupos (p < 0.01).")
        elif p_value < 0.05:
            st.info("Evidencia moderada de diferencia entre grupos (p < 0.05).")
        else:
            st.warning("No concluyente: no se detecta diferencia estadisticamente significativa.")

    compare_df = pd.DataFrame(
        {
            "grupo": [g1] * len(x) + [g2] * len(y),
            "valor": np.concatenate([x, y]),
        }
    )
    fig = px.box(compare_df, x="grupo", y="valor", color="grupo", title=f"Comparacion inferencial de {metric}")
    fig.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
    _apply_dark_chart_text(fig)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)

    st.markdown("**Screening de multiples comparaciones con correccion BH**")
    pvals = []
    screening_rows = []
    other_groups = [g for g in groups if g != g1]
    for g_other in other_groups:
        y_other = (
            pd.to_numeric(
                df_metricas[df_metricas[group_col].astype(str) == str(g_other)][metric],
                errors="coerce",
            )
            .dropna()
            .to_numpy(dtype=float)
        )
        if len(x) < 5 or len(y_other) < 5:
            continue

        d_raw, d_low, d_high = _bootstrap_ci_mean_diff(x, y_other)
        p_raw = _permutation_pvalue_mean_diff(x, y_other)
        pvals.append(float(p_raw))
        screening_rows.append(
            {
                "comparacion": f"{g1} vs {g_other}",
                "dif_media": d_raw,
                "ic95_low": d_low,
                "ic95_high": d_high,
                "p_raw": float(p_raw),
            }
        )

    if screening_rows:
        p_adj = _benjamini_hochberg(pvals)
        for i, adj in enumerate(p_adj):
            screening_rows[i]["p_bh"] = adj
            screening_rows[i]["significativa_bh_5pct"] = bool(adj < 0.05)
        st.dataframe(pd.DataFrame(screening_rows), width="stretch", hide_index=True)
    else:
        st.caption("No hubo suficientes muestras para screening multiple con BH.")

    if not df_feedback.empty and "was_correct" in df_feedback.columns and "correct_label" in df_feedback.columns:
        st.markdown("**Inferencia adicional en feedback (accuracy por etiqueta correcta)**")
        tmp = df_feedback.dropna(subset=["correct_label"]).copy()
        tmp["was_correct_num"] = pd.to_numeric(tmp["was_correct"], errors="coerce")
        acc_by_label = (
            tmp.groupby("correct_label", as_index=False)["was_correct_num"].mean().rename(columns={"was_correct_num": "accuracy"})
        )
        fig_acc = px.bar(acc_by_label, x="correct_label", y="accuracy", title="Accuracy por etiqueta correcta")
        fig_acc.update_yaxes(tickformat=".0%")
        fig_acc.update_layout(**PLOTLY_LAYOUT_DEFAULTS)
        _apply_dark_chart_text(fig_acc)
        st.plotly_chart(fig_acc, width="stretch", config=PLOTLY_CONFIG)

        stats_rows: list[dict[str, Any]] = []
        for label, grp in tmp.groupby("correct_label"):
            vals = pd.to_numeric(grp["was_correct_num"], errors="coerce").dropna()
            if vals.empty:
                continue
            p_hat, low, high = _wilson_interval(int(vals.sum()), int(len(vals)))
            stats_rows.append(
                {
                    "label": str(label),
                    "n": int(len(vals)),
                    "accuracy": p_hat,
                    "wilson_low": low,
                    "wilson_high": high,
                }
            )

        if stats_rows:
            stats_df = pd.DataFrame(stats_rows).sort_values("accuracy", ascending=False)
            st.dataframe(stats_df, width="stretch", hide_index=True)


def _render_predictive(df_metricas: pd.DataFrame, df_feedback: pd.DataFrame) -> None:
    st.subheader("Predictiva")
    st.caption("Pronostico baseline con tendencia lineal y banda de incertidumbre.")

    source = st.selectbox(
        "Serie a pronosticar",
        options=["engagement_rate_mensual", "accuracy_feedback_diaria"],
        key="stats_pred_source",
    )
    horizon = st.slider("Horizonte de pronostico", min_value=4, max_value=12, value=6, step=1, key="stats_pred_h")

    if source == "engagement_rate_mensual":
        if "fecha" not in df_metricas.columns or "engagement_rate" not in df_metricas.columns:
            st.warning("No hay columnas necesarias para pronosticar engagement mensual.")
            return

        tmp = df_metricas.copy()
        tmp["fecha"] = pd.to_datetime(tmp["fecha"], errors="coerce")
        tmp = tmp.dropna(subset=["fecha"])
        tmp["periodo"] = tmp["fecha"].dt.to_period("M").dt.to_timestamp()
        serie = tmp.groupby("periodo")["engagement_rate"].mean().sort_index()
        y_label = "engagement_rate"
    else:
        if df_feedback.empty or "timestamp" not in df_feedback.columns or "was_correct" not in df_feedback.columns:
            st.warning("No hay datos de feedback suficientes para pronosticar accuracy.")
            return

        tmp = df_feedback.copy()
        tmp = tmp.dropna(subset=["timestamp"])
        tmp["periodo"] = tmp["timestamp"].dt.to_period("D").dt.to_timestamp()
        tmp["was_correct_num"] = pd.to_numeric(tmp["was_correct"], errors="coerce")
        serie = tmp.groupby("periodo")["was_correct_num"].mean().sort_index()
        y_label = "accuracy"

    if len(serie) < 4:
        st.info("Se necesitan al menos 4 periodos historicos para calcular pronostico.")
        return

    backtest = _walk_forward_backtest(serie, min_train=6)
    selected_model = "linear"
    if backtest.get("enough_data"):
        summary = backtest["summary"]
        selected_model = str(summary.get("best_model", "linear"))
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("MAE lineal", f"{summary['linear']['mae']:.4f}")
        b2.metric("MAE MA(3)", f"{summary['ma3']['mae']:.4f}")
        b3.metric("MAPE lineal", f"{summary['linear']['mape']:.2f}%" if pd.notna(summary['linear']['mape']) else "N/A")
        b4.metric("MAPE MA(3)", f"{summary['ma3']['mape']:.2f}%" if pd.notna(summary['ma3']['mape']) else "N/A")
        st.caption(f"Modelo seleccionado por backtesting walk-forward: {selected_model}")
    else:
        st.caption("Backtesting no disponible por serie corta; se usa baseline lineal.")

    if selected_model == "ma3":
        forecast_df = _fit_moving_average_forecast(serie, horizon=int(horizon), window=3)
    else:
        forecast_df = _fit_linear_forecast(serie, horizon=int(horizon))

    if forecast_df.empty:
        st.info("No fue posible ajustar el modelo baseline con la serie actual.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=forecast_df["step"],
            y=forecast_df["y_hat"],
            mode="lines",
            name="tendencia",
            line={"color": "#003696", "width": 3},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast_df["step"],
            y=forecast_df["upper"],
            mode="lines",
            name="limite superior",
            line={"color": "#9CA3AF", "width": 1},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast_df["step"],
            y=forecast_df["lower"],
            mode="lines",
            name="limite inferior",
            line={"color": "#9CA3AF", "width": 1},
            fill="tonexty",
            fillcolor="rgba(0, 54, 150, 0.10)",
        )
    )

    real_part = forecast_df.dropna(subset=["y_real"]) if "y_real" in forecast_df.columns else pd.DataFrame()
    if not real_part.empty:
        fig.add_trace(
            go.Scatter(
                x=real_part["step"],
                y=real_part["y_real"],
                mode="markers",
                name="historico real",
                marker={"color": "#CC7000", "size": 7},
            )
        )

    fig.update_layout(
        title=f"Pronostico baseline de {y_label} ({selected_model})",
        xaxis_title="indice temporal",
        yaxis_title=y_label,
        **PLOTLY_LAYOUT_DEFAULTS,
    )
    _apply_dark_chart_text(fig)
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)

    if not real_part.empty:
        mae = float(np.mean(np.abs(real_part["y_real"] - real_part["y_hat"])))
        denom = np.where(np.abs(real_part["y_real"]) > 1e-9, np.abs(real_part["y_real"]), np.nan)
        mape = float(np.nanmean(np.abs((real_part["y_real"] - real_part["y_hat"]) / denom)) * 100)
        p1, p2 = st.columns(2)
        p1.metric("MAE historico", f"{mae:.4f}")
        p2.metric("MAPE historico", f"{mape:.2f}%" if pd.notna(mape) else "N/A")


def _render_registry(df_metricas: pd.DataFrame, df_feedback: pd.DataFrame) -> None:
    st.subheader("Registro estadistico")

    registry = _build_registry_rows(df_metricas, df_feedback)
    if registry.empty:
        st.info("No hay indicadores listos para registrar con los datos actuales.")
        return

    risk_map = {"bajo": "🟢", "medio": "🟡", "alto": "🔴"}
    if "riesgo" in registry.columns:
        registry = registry.copy()
        registry["semaforo"] = registry["riesgo"].map(risk_map).fillna("⚪")

    st.dataframe(registry, width="stretch", hide_index=True)

    csv_bytes = registry.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Descargar registro estadistico (CSV)",
        data=csv_bytes,
        file_name="registro_estadistico.csv",
        mime="text/csv",
        key="stats_registry_download",
    )


def render_statistical_registry_dashboard() -> None:
    st.title("Registro Estadistico")
    st.caption("Lectura descriptiva, inferencial y predictiva de metricas globales y feedback.")

    df_metricas = data_provider.get_merged_data(force_reload=False)
    if df_metricas is None:
        df_metricas = pd.DataFrame()

    if not df_metricas.empty and "fecha" in df_metricas.columns:
        df_metricas["fecha"] = pd.to_datetime(df_metricas["fecha"], errors="coerce")

    df_metricas = _resolve_global_filters(df_metricas) if not df_metricas.empty else df_metricas
    df_feedback = _load_feedback_df()

    tab_summary, tab_desc, tab_inf, tab_pred, tab_registry = st.tabs(
        ["Resumen", "Descriptiva", "Inferencia", "Predictiva", "Registro"]
    )

    with tab_summary:
        _render_summary(df_metricas, df_feedback)
    with tab_desc:
        _render_descriptive(df_metricas, df_feedback)
    with tab_inf:
        _render_inference(df_metricas, df_feedback)
    with tab_pred:
        _render_predictive(df_metricas, df_feedback)
    with tab_registry:
        _render_registry(df_metricas, df_feedback)

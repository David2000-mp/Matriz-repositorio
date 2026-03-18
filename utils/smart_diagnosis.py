"""Funciones de diagnostico inteligente para engagement."""

from __future__ import annotations

from typing import Any

import pandas as pd


def compute_volatility_guardrail(values: list[float], threshold: float = 0.30) -> dict[str, Any]:
    """Detecta volatilidad cuando media y mediana difieren mas del umbral relativo."""
    cleaned = pd.to_numeric(pd.Series(values), errors="coerce").dropna()
    if cleaned.empty:
        return {
            "is_volatile": False,
            "mean": 0.0,
            "median": 0.0,
            "relative_diff": 0.0,
            "message": "Sin datos suficientes para evaluar volatilidad.",
        }

    mean_val = float(cleaned.mean())
    median_val = float(cleaned.median())
    base = median_val if median_val > 0 else (mean_val if mean_val > 0 else 1.0)
    relative_diff = abs(mean_val - median_val) / base
    is_volatile = relative_diff > threshold

    if is_volatile:
        message = (
            f"Volatilidad detectada: media {mean_val:.2f}% vs mediana {median_val:.2f}% "
            f"(diferencia relativa {relative_diff * 100:.1f}%)."
        )
    else:
        message = "Comportamiento estable: media y mediana en rango consistente."

    return {
        "is_volatile": is_volatile,
        "mean": mean_val,
        "median": median_val,
        "relative_diff": relative_diff,
        "message": message,
    }


def category_effectiveness(posts_df: pd.DataFrame, followers: int, min_samples: int = 2) -> dict[str, Any]:
    """Agrupa por categoria escolar y retorna categoria mas efectiva (n >= min_samples)."""
    if posts_df is None or posts_df.empty or followers <= 0:
        return {"has_signal": False, "table": pd.DataFrame(), "best_category": None}

    work = posts_df.copy()
    if "categoria" not in work.columns:
        work["categoria"] = "Sin categoria"
    if "total" not in work.columns:
        work["total"] = 0

    work["ER Post"] = pd.to_numeric(work["total"], errors="coerce").fillna(0.0) / float(followers) * 100.0

    grouped = (
        work.groupby("categoria", dropna=False)
        .agg(posts=("categoria", "count"), er_promedio=("ER Post", "mean"), interacciones=("total", "sum"))
        .reset_index()
    )

    eligible = grouped[grouped["posts"] >= int(min_samples)].copy()
    if eligible.empty:
        return {"has_signal": False, "table": grouped, "best_category": None}

    eligible = eligible.sort_values(by=["er_promedio", "interacciones"], ascending=[False, False])
    best_row = eligible.iloc[0].to_dict()

    return {"has_signal": True, "table": eligible, "best_category": best_row}


def build_recommendation_text(
    actor_name: str,
    diagnosis_level: str,
    posts_per_week: float,
    best_category: str | None,
    is_volatile: bool,
) -> str:
    """Construye recomendacion narrativa segun nivel, categoria y estabilidad."""
    name = (actor_name or "Equipo").strip()
    category_text = best_category if best_category else "tu categoria mas consistente"
    volatility_note = (
        " Ojo: tu rendimiento es volatil por un posible post viral; evita tomar decisiones solo por el promedio."
        if is_volatile
        else ""
    )

    level = (diagnosis_level or "").lower()
    if level in {"alto", "bueno"}:
        return (
            f"{name}, tu comunidad esta activa y responde bien. Mantengan la linea editorial en {category_text} "
            f"y sostengan una frecuencia de al menos {posts_per_week:.1f} posts/semana.{volatility_note}"
        )

    if level in {"aceptable", "promedio"}:
        return (
            f"{name}, hay traccion pero falta consistencia. Prioriza {category_text}, mejora la frecuencia "
            f"a 3-5 posts/semana y fortalece CTAs para elevar interacciones.{volatility_note}"
        )

    return (
        f"{name}, tu comunidad necesita una reactivacion. Reestructura contenido alrededor de {category_text}, "
        f"sube frecuencia a 5-7 posts/semana y valida cada semana con datos comparables.{volatility_note}"
    )

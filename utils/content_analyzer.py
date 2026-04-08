"""Analizador de contenido escolar: clasificacion y ranking."""

from __future__ import annotations

from typing import Any

import pandas as pd


CATEGORY_ALIASES = {
    "admisiones": "Admisiones",
    "admision": "Admisiones",
    "eventos": "Eventos",
    "evento": "Eventos",
    "vida estudiantil": "Vida Estudiantil",
    "vida": "Vida Estudiantil",
    "academico": "Academico",
    "academico": "Academico",
    "académico": "Academico",
    "pastoral": "Pastoral",
    "deportes": "Deportes",
    "institucional": "Institucional",
    "venta": "Venta",
    "otro": "Otro",
}


def _normalize_category(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return "Sin categoria"
    return CATEGORY_ALIASES.get(text, str(value).strip())


def classify_school_content(posts_df: pd.DataFrame) -> dict[str, Any]:
    """Normaliza categoria escolar y valida campos clave no vacios."""
    if posts_df is None or posts_df.empty:
        return {
            "data": pd.DataFrame(),
            "missing_rows": [],
            "is_valid": False,
            "message": "Sin datos para clasificar.",
        }

    work = posts_df.copy()
    if "Categoria" not in work.columns:
        work["Categoria"] = "Sin categoria"

    work["Categoria Canonica"] = work["Categoria"].apply(_normalize_category)

    required = ["Post #", "Categoria Canonica", "Tipo"]
    missing_rows: list[int] = []
    for idx, row in work.iterrows():
        has_missing = False
        for col in required:
            if col not in work.columns or str(row.get(col, "")).strip() in {"", "Sin categoria"}:
                has_missing = True
                break
        if has_missing:
            missing_rows.append(int(idx))

    return {
        "data": work,
        "missing_rows": missing_rows,
        "is_valid": len(missing_rows) == 0,
        "message": "OK" if len(missing_rows) == 0 else "Hay filas con datos incompletos.",
    }


def identify_top_performer(posts_df: pd.DataFrame) -> dict[str, Any]:
    """Encuentra post estrella por mayor ER; desempate por interacciones."""
    if posts_df is None or posts_df.empty:
        return {"top_post": None, "has_data": False}

    work = posts_df.copy()
    if "ER Post" not in work.columns:
        work["ER Post"] = 0.0
    if "Interacciones" not in work.columns:
        work["Interacciones"] = 0

    work["ER Post"] = pd.to_numeric(work["ER Post"], errors="coerce").fillna(0.0)
    work["Interacciones"] = pd.to_numeric(work["Interacciones"], errors="coerce").fillna(0).astype(int)

    ranked = work.sort_values(by=["ER Post", "Interacciones"], ascending=[False, False])
    if ranked.empty:
        return {"top_post": None, "has_data": False}

    top = ranked.iloc[0].to_dict()
    return {"top_post": top, "has_data": True}


def summarize_content_insights(posts_df: pd.DataFrame, followers: int = 0) -> dict[str, Any]:
    """Resume formato ganador, formato mas consumido y formato mas guardado."""
    if posts_df is None or posts_df.empty:
        return {
            "has_data": False,
            "table": pd.DataFrame(),
            "best_format": None,
            "most_consumed_format": None,
            "most_saved_format": None,
            "best_combo": None,
            "consumption_metric": "interacciones",
        }

    work = posts_df.copy()

    if "Tipo" not in work.columns and "type" in work.columns:
        work["Tipo"] = work["type"]
    if "Categoria" not in work.columns and "categoria" in work.columns:
        work["Categoria"] = work["categoria"]
    if "Interacciones" not in work.columns and "total" in work.columns:
        work["Interacciones"] = work["total"]
    if "Vistas" not in work.columns and "views" in work.columns:
        work["Vistas"] = work["views"]
    if "Guardados" not in work.columns and "saves" in work.columns:
        work["Guardados"] = work["saves"]

    if "Tipo" not in work.columns:
        work["Tipo"] = "Sin tipo"

    for col in ["Interacciones", "Vistas", "Guardados", "Comentarios", "Compartidos"]:
        if col not in work.columns:
            work[col] = 0
        work[col] = pd.to_numeric(work[col], errors="coerce").fillna(0)

    grouped = (
        work.groupby("Tipo", dropna=False)
        .agg(
            posts=("Tipo", "count"),
            total_interactions=("Interacciones", "sum"),
            total_views=("Vistas", "sum"),
            total_saves=("Guardados", "sum"),
            avg_comments=("Comentarios", "mean"),
            avg_shares=("Compartidos", "mean"),
        )
        .reset_index()
    )

    grouped["avg_engagement"] = (
        grouped["total_interactions"] / grouped["posts"].clip(lower=1) / float(followers) * 100.0
        if followers > 0
        else 0.0
    )

    combo_grouped = (
        work.groupby(["Tipo", "Categoria"], dropna=False)
        .agg(
            posts=("Tipo", "count"),
            total_interactions=("Interacciones", "sum"),
            total_views=("Vistas", "sum"),
            total_saves=("Guardados", "sum"),
        )
        .reset_index()
    )
    combo_grouped["avg_engagement"] = (
        combo_grouped["total_interactions"] / combo_grouped["posts"].clip(lower=1) / float(followers) * 100.0
        if followers > 0
        else 0.0
    )

    best_row = grouped.sort_values(by=["avg_engagement", "total_interactions"], ascending=[False, False]).iloc[0]
    use_views = bool(grouped["total_views"].sum() > 0)
    consumption_metric = "total_views" if use_views else "total_interactions"
    consumed_row = grouped.sort_values(by=[consumption_metric, "avg_engagement"], ascending=[False, False]).iloc[0]

    saved_row = None
    saved_candidates = grouped[grouped["total_saves"] > 0]
    if not saved_candidates.empty:
        saved_row = saved_candidates.sort_values(by=["total_saves", "avg_engagement"], ascending=[False, False]).iloc[0]

    def _row_to_summary(row: pd.Series | None, metric_key: str, metric_label: str) -> dict[str, Any] | None:
        if row is None:
            return None
        return {
            "tipo": str(row.get("Tipo", "Sin tipo")),
            "posts": int(row.get("posts", 0)),
            "avg_engagement": float(row.get("avg_engagement", 0.0)),
            "metric_key": metric_key,
            "metric_label": metric_label,
            "metric_value": float(row.get(metric_key, 0.0)),
        }

    best_combo = None
    if not combo_grouped.empty:
        combo_row = combo_grouped.sort_values(by=["avg_engagement", "total_interactions"], ascending=[False, False]).iloc[0]
        best_combo = {
            "tipo": str(combo_row.get("Tipo", "Sin tipo")),
            "categoria": str(combo_row.get("Categoria", "Sin categoria")),
            "label": f"{str(combo_row.get('Tipo', 'Sin tipo'))} + {str(combo_row.get('Categoria', 'Sin categoria'))}",
            "posts": int(combo_row.get("posts", 0)),
            "avg_engagement": float(combo_row.get("avg_engagement", 0.0)),
            "total_interactions": float(combo_row.get("total_interactions", 0.0)),
        }

    return {
        "has_data": True,
        "table": grouped.sort_values(by=["avg_engagement", consumption_metric], ascending=[False, False]).reset_index(drop=True),
        "best_format": _row_to_summary(best_row, "avg_engagement", "ER promedio"),
        "most_consumed_format": _row_to_summary(
            consumed_row,
            consumption_metric,
            "Vistas totales" if use_views else "Interacciones totales",
        ),
        "most_saved_format": _row_to_summary(saved_row, "total_saves", "Guardados"),
        "best_combo": best_combo,
        "consumption_metric": "views" if use_views else "interactions",
    }


def build_content_action_plan(content_insights: dict[str, Any] | None, best_category: dict[str, Any] | None = None) -> list[str]:
    """Genera recomendaciones accionables basadas en formato, consumo y guardados."""
    insights = content_insights or {}
    actions: list[str] = []

    best_format = insights.get("best_format") or {}
    most_consumed = insights.get("most_consumed_format") or {}
    most_saved = insights.get("most_saved_format") or {}
    best_combo = insights.get("best_combo") or {}

    if best_combo:
        actions.append(
            f"Repite más publicaciones de **{best_combo.get('label', 'tu mejor combinación')}**; es la mezcla con mejor respuesta promedio."
        )
    elif best_format:
        actions.append(
            f"Aumenta la proporción de **{best_format.get('tipo', 'tu formato ganador')}** porque hoy es el formato que mejor convierte."
        )

    if best_format and most_consumed and best_format.get("tipo") != most_consumed.get("tipo"):
        actions.append(
            f"Ojo: lo más consumido no es lo que mejor convierte. **{most_consumed.get('tipo', 'Ese formato')}** atrae atención, pero **{best_format.get('tipo', 'otro formato')}** genera mejor engagement."
        )

    if most_saved:
        actions.append(
            f"Incluye más contenido de valor tipo **{most_saved.get('tipo', 'contenido guardable')}**; es el formato con más guardados."
        )

    if best_category:
        actions.append(
            f"Prioriza temas de **{best_category.get('categoria', 'tu categoría líder')}** porque es la categoría con mejor desempeño actual."
        )

    if not actions:
        actions.append("Sigue capturando más publicaciones para generar recomendaciones más precisas.")

    return actions[:4]

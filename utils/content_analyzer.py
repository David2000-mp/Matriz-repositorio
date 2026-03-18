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

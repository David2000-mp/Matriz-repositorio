"""Motor declarativo de reglas de engagement por plataforma."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EngagementResult:
    """Resultado estandar del calculo de engagement por post."""

    platform: str
    total_interactions: int
    total_source: str
    has_inconsistency: bool
    inconsistency_reason: str
    er_community: float
    er_views: float
    analysis_mode: str
    is_views_only: bool


def _safe_int(value: Any) -> int:
    try:
        if value is None:
            return 0
        return int(float(value))
    except Exception:
        return 0


def _safe_pct(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return (numerator / denominator) * 100.0


def calculate_engagement_engine(platform: str, row: dict[str, Any]) -> EngagementResult:
    """Calcula engagement por post usando reglas estrictas por plataforma.

    Jerarquia Manual vs Desglose:
    - Si suma desglose > 0, usar desglose.
    - Si no, y manual > 0, usar manual.
    - Si no, total = 0.

    Flag de inconsistencia:
    - Si suma desglose != manual y ambos > 0, marcar inconsistencia.
    """

    p = (platform or "").strip().lower()

    followers = _safe_int(row.get("followers", row.get("seguidores_snapshot", row.get("seguidores", 0))))
    views = _safe_int(row.get("views", row.get("Vistas", 0)))
    comments = _safe_int(row.get("comments", row.get("Comentarios", 0)))
    shares = _safe_int(row.get("shares", row.get("Compartidos", 0)))
    likes = _safe_int(row.get("likes", row.get("Me gusta", 0)))
    reactions = _safe_int(row.get("reactions", row.get("Reacciones", 0)))
    manual_total = _safe_int(row.get("manual_interactions", row.get("Interacciones", 0)))

    if p == "facebook":
        breakdown_total = reactions + comments + shares
    elif p == "instagram":
        breakdown_total = likes + comments
    elif p == "tiktok":
        breakdown_total = likes + comments + shares
    else:
        breakdown_total = likes + reactions + comments + shares

    if breakdown_total > 0:
        total = breakdown_total
        source = "breakdown"
    elif manual_total > 0:
        total = manual_total
        source = "manual"
    else:
        total = 0
        source = "none"

    has_inconsistency = breakdown_total > 0 and manual_total > 0 and breakdown_total != manual_total
    inconsistency_reason = "desglose!=manual" if has_inconsistency else ""

    er_community = _safe_pct(total, followers)
    er_views = _safe_pct(total, views) if p == "tiktok" else 0.0
    is_views_only = p == "tiktok" and views > 0 and total == 0
    analysis_mode = "views_only" if is_views_only else "standard"

    return EngagementResult(
        platform=p,
        total_interactions=total,
        total_source=source,
        has_inconsistency=has_inconsistency,
        inconsistency_reason=inconsistency_reason,
        er_community=er_community,
        er_views=er_views,
        analysis_mode=analysis_mode,
        is_views_only=is_views_only,
    )

"""Catálogo canónico de métricas analíticas y sus aliases de origen."""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping, FrozenSet


METRIC_ALIASES: Mapping[str, FrozenSet[str]] = MappingProxyType(
    {
        "interacciones": frozenset({"interacciones", "interaccion"}),
        "visualizaciones": frozenset(
            {"visualizaciones", "visualizacion", "views", "vistas"}
        ),
    }
)

INTERACTION_ALIASES = METRIC_ALIASES["interacciones"]
VISUALIZATION_ALIASES = METRIC_ALIASES["visualizaciones"]


def canonical_metric_name(metric_name: str) -> str | None:
    """Devuelve la métrica canónica para un nombre ya normalizado."""
    normalized = str(metric_name or "").strip().lower()
    for canonical, aliases in METRIC_ALIASES.items():
        if normalized in aliases:
            return canonical
    return None

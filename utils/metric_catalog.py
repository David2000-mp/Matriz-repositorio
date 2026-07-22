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

METRIC_LABELS: Mapping[str, str] = MappingProxyType(
    {
        "interacciones": "Interacciones",
        "visualizaciones": "Visualizaciones",
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


def metric_aliases(metric_name: str) -> FrozenSet[str]:
    """Obtiene aliases de una métrica canónica o falla de forma explícita."""
    canonical = canonical_metric_name(metric_name) or str(metric_name or "").strip().lower()
    if canonical not in METRIC_ALIASES:
        raise ValueError(f"Métrica analítica no soportada: {metric_name}")
    return METRIC_ALIASES[canonical]


def metric_label(metric_name: str) -> str:
    canonical = canonical_metric_name(metric_name) or str(metric_name or "").strip().lower()
    return METRIC_LABELS.get(canonical, str(metric_name))

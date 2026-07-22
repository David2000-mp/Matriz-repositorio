"""Micro-componentes reutilizables de la interfaz de CHAMPILEAKS.

Este módulo contiene componentes de presentación sin lógica de datos. Cada
función recibe valores ya preparados por la vista para conservar la separación
entre la capa visual y el modelo de datos.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import streamlit as st
from streamlit_lottie import st_lottie


_ANIMATIONS_DIR = Path(__file__).resolve().parents[1] / "assets" / "animations"


def _load_lottie_local(filepath: str | Path) -> dict | None:
    """Carga una animación Lottie local sin interrumpir la aplicación.

    Las rutas relativas se resuelven dentro de ``assets/animations``. También
    se aceptan rutas absolutas para facilitar pruebas aisladas del componente.
    """
    path = Path(filepath)
    if not path.is_absolute():
        path = _ANIMATIONS_DIR / path

    try:
        with path.open(encoding="utf-8") as animation_file:
            return json.load(animation_file)
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def _render_lottie_centered(animation: dict | None, *, height: int) -> None:
    """Renderiza una animación centrada cuando el asset está disponible."""
    if animation is None:
        return

    _, animation_column, _ = st.columns([1, 2, 1])
    with animation_column:
        st_lottie(animation, height=height)


def render_loader(tipo: str = "main") -> None:
    """Renderiza el loader principal o el loader compacto de gráficas."""
    is_chart = tipo == "chart"
    filename = "loader_chart.json" if is_chart else "loader_main.json"
    height = 100 if is_chart else 150
    _render_lottie_centered(_load_lottie_local(filename), height=height)


def render_empty_state(mensaje: str, tipo: str = "search") -> None:
    """Muestra un estado vacío de búsqueda o geográfico con su mensaje."""
    filename = "state_empty_geo.json" if tipo == "geo" else "state_empty_search.json"
    _render_lottie_centered(_load_lottie_local(filename), height=150)
    st.caption(mensaje)


def render_status(mensaje: str, tipo: str = "success") -> None:
    """Muestra feedback animado para una acción exitosa o fallida."""
    filename = "status_error.json" if tipo == "error" else "status_success.json"
    _render_lottie_centered(_load_lottie_local(filename), height=100)
    st.caption(mensaje)


def PageHeader(
    title: str,
    subtitle: str | None = None,
    *,
    eyebrow: str | None = None,
    divider: bool = False,
) -> None:
    """Renderiza un encabezado de página consistente dentro de un contenedor.

    Args:
        title: Título principal de la vista.
        subtitle: Contexto breve mostrado debajo del título.
        eyebrow: Etiqueta opcional mostrada sobre el título.
        divider: Inserta un divisor inferior cuando la vista lo requiere.
    """
    with st.container():
        if eyebrow:
            st.caption(eyebrow)
        st.title(title)
        if subtitle:
            st.caption(subtitle)
        if divider:
            st.divider()


def MetricCard(
    label: str,
    value: str | int | float,
    delta: str | int | float | None = None,
    *,
    help: str | None = None,
    delta_color: str = "normal",
) -> None:
    """Renderiza un KPI consistente dentro de un contenedor visual nativo.

    La función no calcula valores ni variaciones: las vistas entregan datos
    listos para presentar y el componente se limita al renderizado.
    """
    with st.container(border=True):
        st.metric(
            label=label,
            value=value,
            delta=delta,
            delta_color=delta_color,
            help=help,
        )


def EmptyState(
    title: str,
    message: str,
    *,
    icon: str = "\U0001f50d",
) -> None:
    """Muestra un estado vacío claro sin mezclarlo con la lógica de datos.

    Las vistas deciden cuándo no existe información y este componente solo
    comunica el resultado al usuario, de forma consistente y sin exponer
    errores internos de Pandas.
    """
    with st.container(border=True):
        st.subheader(f"{icon} {title}")
        st.caption(message)


@dataclass(frozen=True)
class FilterBarActions:
    """Acciones solicitadas por la barra de filtros."""

    reset_requested: bool = False
    reload_requested: bool = False


def FilterBar(
    *,
    entities: Sequence[str],
    months: Sequence[str],
    entity_key: str = "filtro_entidad",
    month_key: str = "filtro_mes",
    show_reload: bool = True,
    version_label: str | None = "v2.1.0 • Maristas",
    on_reset: Callable[[], None] | None = None,
    on_reload: Callable[[], None] | None = None,
) -> FilterBarActions:
    """Renderiza controles globales y devuelve únicamente las acciones UI.

    El componente no interpreta datos ni actualiza cachés. El router conserva
    esas decisiones para mantener la separación entre presentación y lógica.
    """
    with st.container():
        st.divider()
        st.subheader("Filtros globales")
        st.selectbox("Colegio", entities, key=entity_key)
        st.selectbox("Periodo", months, key=month_key)

        reset_requested = st.button(
            "Reset filtros",
            help="Restablece colegio y periodo.",
            use_container_width=True,
            on_click=on_reset,
        )
        reload_requested = False
        if show_reload:
            reload_requested = st.button(
                "Forzar recarga",
                help="Invalida el caché compartido y consulta nuevamente la fuente.",
                use_container_width=True,
                on_click=on_reload,
            )

        st.divider()
        if version_label:
            st.caption(version_label)

    return FilterBarActions(
        reset_requested=reset_requested,
        reload_requested=reload_requested,
    )


__all__ = [
    "EmptyState",
    "FilterBar",
    "FilterBarActions",
    "MetricCard",
    "PageHeader",
    "render_empty_state",
    "render_loader",
    "render_status",
]

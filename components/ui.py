"""Micro-componentes reutilizables de la interfaz de CHAMPILEAKS.

Este módulo contiene componentes de presentación sin lógica de datos. Cada
función recibe valores ya preparados por la vista para conservar la separación
entre la capa visual y el modelo de datos.
"""

from __future__ import annotations

import html
import json
import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import streamlit as st
from streamlit_lottie import st_lottie


_ANIMATIONS_DIR = Path(__file__).resolve().parents[1] / "assets" / "animations"


@st.cache_data(show_spinner=False)
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


def render_live_indicator(mensaje: str = "En vivo") -> None:
    """Muestra un pulso compacto junto al estado activo del Dashboard."""
    animation = _load_lottie_local("icon_pulse_live.json")
    with st.container(
        horizontal=True,
        horizontal_alignment="right",
        vertical_alignment="center",
        gap="small",
    ):
        if animation is not None:
            st_lottie(
                animation,
                height=36,
                width=36,
                key="dashboard-live-pulse",
            )
        st.caption(mensaje)


def _chip(label: str, value: str | None = None, *, variant: str = "", dot: str | None = None) -> str:
    """HTML de un chip monoespaciado; escapa todo el texto recibido."""
    css = f"cl-chip cl-chip--{variant}" if variant else "cl-chip"
    dot_html = ""
    if dot == "live":
        dot_html = '<span class="cl-dot"></span>'
    elif dot:
        dot_html = '<span class="cl-dot cl-dot--idle"></span>'
    body = html.escape(label)
    if value is not None:
        body = f"{body} <b>{html.escape(str(value))}</b>"
    return f'<span class="{css}">{dot_html}{body}</span>'


def status_chip(label: str, value: str | None = None, *, live: bool = True) -> str:
    """Chip de estado de datos con pulso verde (o gris cuando no hay datos)."""
    return _chip(label, value, dot="live" if live else "idle")


def filter_chip(label: str, value: str) -> str:
    """Chip que señala un filtro global activo."""
    return _chip(label, value, variant="filter")


def PageHeader(
    title: str,
    subtitle: str | None = None,
    *,
    eyebrow: str | None = None,
    divider: bool = False,
    chips: Sequence[str] = (),
) -> None:
    """Renderiza el encabezado común de cada vista.

    Args:
        title: Título principal de la vista.
        subtitle: Contexto breve mostrado debajo del título.
        eyebrow: Etiqueta de sección mostrada sobre el título.
        divider: Compatibilidad; el encabezado ya incluye su línea inferior.
        chips: Fragmentos de ``status_chip``/``filter_chip`` alineados a la
            derecha del título.
    """
    del divider
    eyebrow_html = f'<p class="cl-eyebrow">{html.escape(eyebrow)}</p>' if eyebrow else ""
    subtitle_html = f'<p class="cl-subtitle">{html.escape(subtitle)}</p>' if subtitle else ""
    chips_html = f'<div class="cl-chips">{"".join(chips)}</div>' if chips else ""
    st.markdown(
        '<header class="cl-header">'
        f'<div>{eyebrow_html}<h1 class="cl-title">{html.escape(title)}</h1>{subtitle_html}</div>'
        f"{chips_html}</header>",
        unsafe_allow_html=True,
    )


def SectionLabel(text: str) -> None:
    """Etiqueta técnica pequeña para separar bloques dentro de una vista."""
    st.markdown(f'<p class="cl-section-label">{html.escape(text)}</p>', unsafe_allow_html=True)


def render_friendly_error(
    message: str,
    exc: BaseException | None = None,
    *,
    on_retry: Callable[[], None] | None = None,
    key: str = "friendly-error",
) -> None:
    """Explica un fallo en lenguaje de usuario y deja el detalle técnico plegado.

    El traceback completo va al log; en pantalla solo queda el tipo y el
    mensaje dentro de un expander para quien necesite reportarlo.
    """
    if exc is not None:
        logging.getLogger(__name__).error(message, exc_info=exc)
    with st.container(border=True):
        st.markdown(f":material/error: **{message}**")
        st.caption(
            "Puede deberse a la conexión con la fuente de datos o a un registro con "
            "formato inesperado. Reintenta; si persiste, comparte el detalle técnico."
        )
        st.button("Reintentar", icon=":material/refresh:", key=f"{key}-retry", on_click=on_retry)
        if exc is not None:
            with st.expander("Detalle técnico"):
                st.code(f"{type(exc).__name__}: {exc}", language=None)


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
    # El tema ya pinta cada st.metric como tarjeta; un contenedor con borde
    # añadiría un segundo marco.
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
    icon: str = ":material/search_off:",
    action_page=None,
    action_label: str | None = None,
    action_callback: Callable[[], None] | None = None,
) -> None:
    """Muestra un estado vacío claro con una salida concreta.

    Las vistas deciden cuándo no existe información; este componente
    comunica el resultado sin exponer errores internos de Pandas y, si se
    indica, ofrece la acción que lo resuelve (enlace a página o callback).
    """
    with st.container(border=True):
        st.markdown(f"{icon} **{title}**")
        st.caption(message)
        if action_page is not None:
            st.page_link(action_page, label=action_label or "Ir", icon=":material/arrow_forward:")
        elif action_callback is not None:
            st.button(action_label or "Continuar", on_click=action_callback, key=f"empty-{title}")


def _sync_widget_value(widget_key: str, state_key: str) -> None:
    st.session_state[state_key] = st.session_state[widget_key]


def _persistent_selectbox(label: str, options: Sequence[str], state_key: str) -> None:
    """Selectbox cuyo valor vive en ``state_key`` y no en el estado del widget."""
    widget_key = f"_widget_{state_key}"
    current = st.session_state.get(state_key)
    if current not in options:
        current = options[0] if options else None
        st.session_state[state_key] = current
    st.session_state[widget_key] = current
    st.selectbox(
        label,
        options,
        key=widget_key,
        on_change=_sync_widget_value,
        args=(widget_key, state_key),
    )


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
    show_entity: bool = True,
    show_month: bool = True,
    show_reload: bool = True,
    on_reset: Callable[[], None] | None = None,
    on_reload: Callable[[], None] | None = None,
) -> FilterBarActions:
    """Renderiza controles globales y devuelve únicamente las acciones UI.

    El componente no interpreta datos ni actualiza cachés. El router decide
    qué selectores muestra cada página según los filtros que realmente usa.

    ``entity_key`` y ``month_key`` guardan el valor persistente que leen las
    vistas. Streamlit borra el estado de un widget que no se dibuja, así que
    los selectores usan claves propias y copian su valor al cambiar: el
    filtro sobrevive al pasar por páginas que no lo muestran.
    """
    reset_requested = False
    reload_requested = False
    with st.container():
        if show_entity or show_month:
            if show_entity:
                _persistent_selectbox("Colegio", entities, entity_key)
            if show_month:
                _persistent_selectbox("Periodo", months, month_key)
            reset_requested = st.button(
                "Restablecer filtros",
                icon=":material/filter_alt_off:",
                help="Vuelve a todos los colegios y todos los periodos.",
                use_container_width=True,
                on_click=on_reset,
            )
        if show_reload:
            reload_requested = st.button(
                "Recargar datos",
                icon=":material/sync:",
                help="Invalida el caché compartido y consulta nuevamente la fuente.",
                use_container_width=True,
                on_click=on_reload,
            )

    return FilterBarActions(
        reset_requested=reset_requested,
        reload_requested=reload_requested,
    )


__all__ = [
    "EmptyState",
    "SectionLabel",
    "filter_chip",
    "render_friendly_error",
    "status_chip",
    "FilterBar",
    "FilterBarActions",
    "MetricCard",
    "PageHeader",
    "render_empty_state",
    "render_live_indicator",
    "render_loader",
    "render_status",
]

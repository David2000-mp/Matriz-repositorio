"""Integracion global de descargas CSV para graficas Streamlit."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

import pandas as pd
import streamlit as st

from components.analysis_delivery import render_exact_download
from utils.chart_downloads import (
    matplotlib_figure_to_dataframe,
    native_chart_to_dataframe,
    plotly_figure_to_dataframe,
    plotly_file_stem,
)


_COUNTER_KEY = "_champileaks_chart_download_counter"


def _next_key(file_stem: str) -> str:
    counter = int(st.session_state.get(_COUNTER_KEY, 0)) + 1
    st.session_state[_COUNTER_KEY] = counter
    return f"chart_csv_{counter}_{file_stem}"


def _render_automatic_download(data: pd.DataFrame, file_stem: str) -> None:
    render_exact_download(
        data,
        file_stem,
        label="Descargar CSV de esta grafica",
        key=_next_key(file_stem),
    )


def _wrap_plotly_chart(original: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(original)
    def wrapped(fig: Any, *args: Any, **kwargs: Any) -> Any:
        result = original(fig, *args, **kwargs)
        file_stem = plotly_file_stem(fig)
        _render_automatic_download(plotly_figure_to_dataframe(fig), file_stem)
        return result

    return wrapped


def _wrap_native_chart(
    original: Callable[..., Any], chart_name: str
) -> Callable[..., Any]:
    @wraps(original)
    def wrapped(data: Any = None, *args: Any, **kwargs: Any) -> Any:
        result = original(data, *args, **kwargs)
        _render_automatic_download(native_chart_to_dataframe(data), chart_name)
        return result

    return wrapped


def _wrap_pyplot(original: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(original)
    def wrapped(fig: Any = None, *args: Any, **kwargs: Any) -> Any:
        export_figure = fig
        if export_figure is None:
            try:
                import matplotlib.pyplot as plt

                export_figure = plt.gcf()
            except ImportError:
                export_figure = None
        data = matplotlib_figure_to_dataframe(export_figure)
        result = original(fig, *args, **kwargs)
        _render_automatic_download(data, "datos_grafica_matplotlib")
        return result

    return wrapped


def install_global_chart_csv_downloads() -> None:
    """Hace descargables todas las graficas actuales, condicionales y futuras."""
    st.session_state[_COUNTER_KEY] = 0
    if getattr(st, "_champileaks_chart_csv_installed", False):
        return

    st._champileaks_original_plotly_chart = st.plotly_chart
    st.plotly_chart = _wrap_plotly_chart(st.plotly_chart)
    for method_name in ("bar_chart", "line_chart", "area_chart", "scatter_chart", "map"):
        original = getattr(st, method_name)
        setattr(st, method_name, _wrap_native_chart(original, f"datos_{method_name}"))
    st.pyplot = _wrap_pyplot(st.pyplot)
    st._champileaks_chart_csv_installed = True


def render_plotly_with_exact_download(
    fig: Any,
    data: pd.DataFrame,
    file_stem: str,
    *,
    label: str = "Descargar CSV de esta grafica",
    key: str | None = None,
    **chart_kwargs: Any,
) -> Any:
    """Renderiza con una tabla fuente explicita y evita una descarga duplicada."""
    renderer = getattr(st, "_champileaks_original_plotly_chart", st.plotly_chart)
    result = renderer(fig, **chart_kwargs)
    render_exact_download(data, file_stem, label=label, key=key)
    return result


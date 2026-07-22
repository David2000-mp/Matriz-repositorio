"""Tema Plotly central de CHAMPILEAKS."""

from __future__ import annotations

from typing import Any, TypeVar

import plotly.graph_objects as go


AZUL_INSTITUCIONAL = "#0756C9"
AZUL_INTERACTIVO = "#1677FF"
AMARILLO_MARISTA = "#FFB81C"
PALETA_CHAMPILEAKS = [
    AZUL_INSTITUCIONAL,
    AZUL_INTERACTIVO,
    AMARILLO_MARISTA,
    "#003696",
    "#4C9AFF",
    "#FFCF5C",
]

_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "colorway": PALETA_CHAMPILEAKS,
    "font": {"family": "Inter, Segoe UI, sans-serif", "color": "#212529"},
    "margin": {"l": 36, "r": 24, "t": 52, "b": 40},
    "hovermode": "closest",
    "hoverlabel": {
        "bgcolor": "#FFFFFF",
        "bordercolor": AZUL_INSTITUCIONAL,
        "font": {"family": "Inter, Segoe UI, sans-serif", "color": "#212529"},
    },
    "legend": {
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "right",
        "x": 1,
    },
}

CHAMPILEAKS_TEMPLATE = go.layout.Template(
    layout={
        **_LAYOUT,
        "xaxis": {
            "showgrid": True,
            "gridcolor": "rgba(0,54,150,0.10)",
            "zeroline": False,
            "linecolor": "rgba(0,54,150,0.20)",
        },
        "yaxis": {
            "showgrid": True,
            "gridcolor": "rgba(0,54,150,0.10)",
            "zeroline": False,
            "linecolor": "rgba(0,54,150,0.20)",
        },
    }
)

FigureT = TypeVar("FigureT", bound=go.Figure)


def aplicar_tema_champileaks(fig: FigureT) -> FigureT:
    """Aplica el contrato visual común y retorna la misma figura.

    La función es intencionalmente idempotente y se ejecuta al final de la
    construcción de cada gráfica para reemplazar configuraciones manuales.
    """
    if fig is None:
        return fig

    fig.update_layout(template=CHAMPILEAKS_TEMPLATE, **_LAYOUT)
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(0,54,150,0.10)",
        zeroline=False,
        linecolor="rgba(0,54,150,0.20)",
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(0,54,150,0.10)",
        zeroline=False,
        linecolor="rgba(0,54,150,0.20)",
        automargin=True,
    )
    return fig


def renderizar_grafica_champileaks(fig: FigureT, **kwargs: Any) -> None:
    """Renderiza una figura con el tema visual central aplicado."""
    import streamlit as st

    st.plotly_chart(aplicar_tema_champileaks(fig), **kwargs)

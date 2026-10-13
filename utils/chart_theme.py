"""Tema Plotly central de CHAMPILEAKS."""

from __future__ import annotations

from typing import Any, TypeVar

import plotly.graph_objects as go


AZUL_INSTITUCIONAL = "#1450D2"
AZUL_INTERACTIVO = "#1677FF"
AMARILLO_MARISTA = "#FFB81C"
TINTA = "#0B1530"
TEXTO_SECUNDARIO = "#55627A"
GRID = "rgba(11,21,48,0.06)"
EJE = "rgba(11,21,48,0.14)"
FUENTE = "Inter, Segoe UI, sans-serif"
FUENTE_MONO = "JetBrains Mono, ui-monospace, monospace"
PALETA_AZULES = ["#003696", AZUL_INSTITUCIONAL, AZUL_INTERACTIVO, "#4C9AFF"]
# Orden pensado para series categóricas: tonos separados en matiz y luminosidad.
PALETA_CHAMPILEAKS = [
    AZUL_INSTITUCIONAL,
    AMARILLO_MARISTA,
    "#13A89E",
    "#7C5CFF",
    "#4C9AFF",
    "#E8590C",
    "#003696",
    "#94A3B8",
]

_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "colorway": PALETA_CHAMPILEAKS,
    "font": {"family": FUENTE, "color": TINTA, "size": 12},
    "title": {"font": {"family": FUENTE, "size": 15, "color": TINTA}, "x": 0, "xanchor": "left"},
    "margin": {"l": 36, "r": 24, "t": 52, "b": 40},
    "hovermode": "closest",
    "hoverlabel": {
        "bgcolor": TINTA,
        "bordercolor": TINTA,
        "font": {"family": FUENTE_MONO, "color": "#FFFFFF", "size": 12},
    },
    "legend": {
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "right",
        "x": 1,
        "font": {"color": TEXTO_SECUNDARIO},
    },
}

_EJE = {
    "showgrid": True,
    "gridcolor": GRID,
    "zeroline": False,
    "linecolor": EJE,
    "tickfont": {"family": FUENTE_MONO, "color": TEXTO_SECUNDARIO, "size": 11},
    "title": {"font": {"color": TEXTO_SECUNDARIO, "size": 12}},
}

CHAMPILEAKS_TEMPLATE = go.layout.Template(
    layout={**_LAYOUT, "xaxis": _EJE, "yaxis": _EJE}
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
    fig.update_xaxes(**_EJE, automargin=True)
    fig.update_yaxes(**_EJE, automargin=True)
    return fig


def renderizar_grafica_champileaks(fig: FigureT, **kwargs: Any) -> None:
    """Renderiza una figura con el tema visual central aplicado."""
    import streamlit as st

    st.plotly_chart(aplicar_tema_champileaks(fig), **kwargs)

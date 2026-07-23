"""Pruebas del contrato global de descargas para graficas."""

import pandas as pd
import plotly.graph_objects as go

from utils.chart_downloads import (
    native_chart_to_dataframe,
    plotly_figure_to_dataframe,
    plotly_file_stem,
)


def test_plotly_export_materializes_every_visible_trace_point():
    figure = go.Figure()
    figure.add_bar(x=["A", "B"], y=[10, 20], name="Interacciones")
    figure.add_scatter(x=["A", "B"], y=[100, 200], name="Visualizaciones")

    exported = plotly_figure_to_dataframe(figure)

    assert len(exported) == 4
    assert set(exported["serie"]) == {"Interacciones", "Visualizaciones"}
    assert exported[["x", "y"]].to_dict("records") == [
        {"x": "A", "y": 10},
        {"x": "B", "y": 20},
        {"x": "A", "y": 100},
        {"x": "B", "y": 200},
    ]


def test_plotly_export_flattens_heatmap_without_losing_coordinates():
    figure = go.Figure(data=go.Heatmap(x=["Ene", "Feb"], y=["A", "B"], z=[[1, 2], [3, 4]]))

    exported = plotly_figure_to_dataframe(figure)

    assert exported[["x", "y", "z"]].to_dict("records") == [
        {"x": "Ene", "y": "A", "z": 1},
        {"x": "Feb", "y": "A", "z": 2},
        {"x": "Ene", "y": "B", "z": 3},
        {"x": "Feb", "y": "B", "z": 4},
    ]


def test_native_chart_export_preserves_index_and_values():
    source = pd.DataFrame({"valor": [12, 18]}, index=pd.Index(["A", "B"], name="colegio"))

    exported = native_chart_to_dataframe(source)

    assert exported.to_dict("records") == [
        {"colegio": "A", "valor": 12},
        {"colegio": "B", "valor": 18},
    ]


def test_plotly_file_name_uses_chart_title():
    figure = go.Figure().update_layout(title="Engagement por plataforma")

    assert plotly_file_stem(figure) == "engagement_por_plataforma"


def test_app_installs_global_chart_download_contract():
    source = open("app_refactored.py", encoding="utf-8").read()

    assert "install_global_chart_csv_downloads()" in source


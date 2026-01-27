import pandas as pd
import pytest

from utils.helpers import generar_reporte_html


def sample_df():
    return pd.DataFrame(
        [
            {
                "id_cuenta": "a",
                "fecha": pd.to_datetime("2024-01-01"),
                "seguidores": 100,
                "alcance": 1000,
                "interacciones": 10,
                "likes_promedio": 2,
                "engagement_rate": 10.0,
            }
        ]
    )


def test_generar_reporte_html_includes_img_when_logo_present(monkeypatch):
    """Si hay logo disponible, el HTML debe contener una etiqueta <img> y no <svg>."""

    # Forzar que load_image devuelva base64 (simula logo presente)
    monkeypatch.setattr("utils.helpers.load_image", lambda name: "R0lGODdh")

    html = generar_reporte_html(sample_df(), "Test Report")

    assert "<img" in html.lower() or "<img" in html
    assert "<svg" not in html.lower()


def test_generar_reporte_html_includes_svg_when_logo_missing(monkeypatch):
    """Si no hay logo, el fallback SVG debe estar presente en el HTML."""

    # Forzar que load_image devuelva None (logo ausente)
    monkeypatch.setattr("utils.helpers.load_image", lambda name: None)

    html = generar_reporte_html(sample_df(), "Test Report")

    # Debe incluir SVG placeholder
    assert "<svg" in html.lower()
    assert "<img" not in html.lower()

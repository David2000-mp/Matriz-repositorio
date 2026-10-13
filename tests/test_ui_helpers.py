"""Pruebas de los helpers de presentación: etiquetas de mes, resumen y chips."""

import pandas as pd
import pytest

from components.ui import filter_chip, status_chip
from utils.app_data import format_month_label, summarize_dataset


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2026-09", "sep 2026"),
        ("2025-01", "ene 2025"),
        ("2025-12", "dic 2025"),
        ("2026-00", "2026-00"),
        ("2026-13", "2026-13"),
        ("sin-fecha", "sin-fecha"),
        ("", ""),
    ],
)
def test_format_month_label(raw, expected):
    assert format_month_label(raw) == expected


def test_summarize_dataset_cuenta_distintos_e_ignora_vacios():
    df = pd.DataFrame(
        {
            "id_cuenta": ["a", "a", "b", ""],
            "entidad": ["Colegio 1", "Colegio 1", "Colegio 2", None],
            "fecha": ["2026-08-31", "2026-09-30", "2026-07-31", "fecha inválida"],
        }
    )

    summary = summarize_dataset(df)

    assert summary.latest_month == "2026-09"
    assert summary.entities == 2
    assert summary.accounts == 2
    assert summary.records == 4


def test_summarize_dataset_vacio():
    summary = summarize_dataset(pd.DataFrame())

    assert summary.latest_month is None
    assert (summary.entities, summary.accounts, summary.records) == (0, 0, 0)


def test_chips_escapan_html():
    chip = filter_chip("Colegio", "<script>alert(1)</script>")

    assert "<script>" not in chip
    assert "&lt;script&gt;" in chip
    assert "cl-chip--filter" in chip


def test_status_chip_distingue_estado_sin_datos():
    assert 'class="cl-dot"' in status_chip("Corte", "sep 2026")
    assert "cl-dot--idle" in status_chip("Sin datos", live=False)

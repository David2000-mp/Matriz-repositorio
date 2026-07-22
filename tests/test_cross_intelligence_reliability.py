"""Regresiones de integridad para las bases de inteligencia cruzada."""

import pandas as pd

from utils.cross_intelligence import (
    _normalize_demografica,
    _normalize_maestra,
    get_month_bounds,
)


def test_normalizers_reject_invalid_and_negative_values():
    maestra = pd.DataFrame(
        {
            "fecha": ["2026-07-31 23:59:59", "2026-07-31", "2026-07-31"],
            "colegio": ["Colegio A"] * 3,
            "plataforma": ["Instagram"] * 3,
            "metrica": ["Interacciones"] * 3,
            "valor": [10, -1, "no numerico"],
        }
    )
    demografica = pd.DataFrame(
        {
            "fecha_reporte": ["2026-07-31 23:59:59", "2026-07-31", "2026-07-31"],
            "colegio": ["Colegio A"] * 3,
            "plataforma": ["Instagram"] * 3,
            "criterio": ["Demografia base"] * 3,
            "sexo": ["Mujeres"] * 3,
            "edad": ["18-24"] * 3,
            "ubicacion": [""] * 3,
            "valor": [20, -2, "no numerico"],
        }
    )

    normalized_maestra = _normalize_maestra(maestra)
    normalized_demo = _normalize_demografica(demografica)

    assert normalized_maestra["valor"].tolist() == [10]
    assert normalized_demo["valor"].tolist() == [20]
    assert normalized_maestra["fecha"].iloc[0] == pd.Timestamp("2026-07-31 23:59:59")
    assert normalized_demo["fecha_reporte"].iloc[0] == pd.Timestamp("2026-07-31 23:59:59")


def test_month_bounds_include_the_complete_last_day():
    start, end = get_month_bounds("2026-07")

    assert start == pd.Timestamp("2026-07-01 00:00:00")
    assert end > pd.Timestamp("2026-07-31 23:59:59")
    assert end < pd.Timestamp("2026-08-01 00:00:00")

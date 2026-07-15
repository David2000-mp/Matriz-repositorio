"""Pruebas unitarias para utilidades de analisis demografico/geografico."""

import pandas as pd

from utils.demographics_geo import (
    build_city_report,
    build_demography_base,
    build_network_comparison,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "fecha_reporte": [
                "2026-07-01",
                "2026-07-01",
                "2026-07-01",
                "2026-07-01",
                "2026-07-01",
                "2026-07-01",
                "2026-07-01",
                "2026-07-01",
            ],
            "colegio": ["Colegio A", "Colegio A", "Colegio A", "Colegio A", "Colegio B", "Colegio B", "Colegio B", "Colegio B"],
            "plataforma": ["Instagram"] * 8,
            "criterio": [
                "Demografia base",
                "Demografia base",
                "Ciudad",
                "Ciudad",
                "Demografia base",
                "Demografia base",
                "Ciudad",
                "Ciudad",
            ],
            "sexo": ["Hombres", "Mujeres", "", "", "Hombres", "Mujeres", "", ""],
            "edad": ["18-24", "18-24", "", "", "18-24", "18-24", "", ""],
            "ubicacion": ["", "", "Guadalajara", "Ciudad Desconocida", "", "", "Monterrey", "Otra Ciudad"],
            "valor": [120, 130, 80, 20, 100, 110, 70, 30],
        }
    )


def test_build_demography_base_returns_distribution():
    df = _sample_df()
    result = build_demography_base(df)

    assert not result.empty
    assert set(result.columns) == {"edad", "sexo", "valor", "participacion_pct"}
    assert result["valor"].sum() == 460
    assert abs(result["participacion_pct"].sum() - 100.0) < 1e-6


def test_build_city_report_mapped_and_unmapped():
    df = _sample_df()
    mapped, unmapped = build_city_report(df)

    assert not mapped.empty
    assert not unmapped.empty
    assert "Guadalajara" in mapped["ubicacion"].values
    assert "Ciudad Desconocida" in unmapped["ubicacion"].values



def test_build_network_comparison_excludes_selected_school():
    df = _sample_df()
    result = build_network_comparison(df, "Colegio A")

    assert not result.empty

    # Colegio A: 120 + 130 = 250; Colegio B: 100 + 110 = 210
    hombres = result[result["sexo"] == "Hombres"].iloc[0]
    mujeres = result[result["sexo"] == "Mujeres"].iloc[0]

    assert hombres["colegio_valor"] == 120
    assert hombres["red_valor"] == 100
    assert mujeres["colegio_valor"] == 130
    assert mujeres["red_valor"] == 110

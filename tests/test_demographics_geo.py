"""Pruebas unitarias para utilidades de analisis demografico/geografico."""

import pandas as pd

from views.demographic_geographic_analysis import _build_city_impact_map
from utils.demographics_geo import (
    CITY_IMPACT_COLORS,
    CITY_IMPACT_MARKER_SIZES,
    apply_demographic_filters,
    apply_performance_filters,
    build_city_report,
    build_city_metric_estimate,
    build_demography_base,
    build_network_comparison,
    classify_city_impact,
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


def test_date_filter_includes_records_with_time_on_end_date():
    df = pd.DataFrame(
        {
            "fecha_reporte": [
                "2026-07-31 00:00:00",
                "2026-07-31 23:59:59",
                "2026-08-01 00:00:00",
            ],
            "colegio": ["Colegio A"] * 3,
            "plataforma": ["Instagram"] * 3,
            "valor": [1, 2, 3],
        }
    )

    result = apply_demographic_filters(df, end_date=pd.Timestamp("2026-07-31"))

    assert result["valor"].tolist() == [1, 2]


def test_all_schools_filter_keeps_the_complete_network():
    result = apply_demographic_filters(_sample_df(), colegio="Todos")

    assert set(result["colegio"]) == {"Colegio A", "Colegio B"}


def test_unknown_ages_are_grouped_as_otros_without_losing_rows():
    df = pd.DataFrame(
        {
            "criterio": ["Demografia base"] * 3,
            "sexo": ["Mujeres"] * 3,
            "edad": ["18-24", "75-84", "75-84"],
            "valor": [100, 50, -999],
        }
    )

    result = build_demography_base(df)

    assert result["valor"].sum() == 150
    assert set(result["edad"]) == {"18-24", "Otros"}
    assert result.loc[result["edad"] == "Otros", "valor"].iloc[0] == 50
    assert abs(result["participacion_pct"].sum() - 100.0) < 1e-6


def test_city_lookup_is_exact_and_negative_values_are_rejected():
    df = pd.DataFrame(
        {
            "criterio": ["Ciudad"] * 4,
            "ubicacion": ["Ciudad Victoria", "Victoria", "Nueva Ciudad Victoria", "Guadalajara"],
            "valor": [20, 10, 5, -100],
        }
    )

    mapped, unmapped = build_city_report(df)

    assert mapped["ubicacion"].tolist() == ["Ciudad Victoria"]
    assert set(unmapped["ubicacion"]) == {"Victoria", "Nueva Ciudad Victoria"}
    assert "Guadalajara" not in set(mapped["ubicacion"]) | set(unmapped["ubicacion"])


def test_city_impact_uses_red_blue_and_yellow_terciles():
    levels = classify_city_impact(pd.Series([10, 20, 30, 40, 50, 60]))

    assert levels.tolist() == [
        "Impacto bajo",
        "Impacto bajo",
        "Impacto medio",
        "Impacto medio",
        "Impacto alto",
        "Impacto alto",
    ]
    assert CITY_IMPACT_COLORS == {
        "Impacto bajo": "#D62828",
        "Impacto medio": "#FFB81C",
        "Impacto alto": "#0756C9",
    }


def test_city_map_renders_one_explicit_color_per_impact_level():
    mapped = pd.DataFrame(
        {
            "ubicacion": ["Baja", "Media", "Alta"],
            "valor_total": [10, 50, 100],
            "participacion_pct": [6.25, 31.25, 62.5],
            "lat": [19.0, 20.0, 21.0],
            "lon": [-99.0, -100.0, -101.0],
        }
    )

    figure = _build_city_impact_map(mapped)
    trace_colors = {trace.name: trace.marker.color for trace in figure.data}
    trace_sizes = {trace.name: trace.marker.size for trace in figure.data}

    assert trace_colors == CITY_IMPACT_COLORS
    assert trace_sizes == CITY_IMPACT_MARKER_SIZES


def test_performance_filter_uses_inclusive_end_date_and_all_schools():
    performance = pd.DataFrame(
        {
            "fecha": [
                "2026-07-31 23:59:59",
                "2026-08-01 00:00:00",
            ],
            "colegio": ["Colegio A", "Colegio B"],
            "plataforma": ["Instagram", "Instagram"],
            "metrica": ["Interacciones", "Interacciones"],
            "valor": [10, 20],
        }
    )

    result = apply_performance_filters(
        performance,
        colegio="Todos",
        end_date=pd.Timestamp("2026-07-31"),
    )

    assert result["valor"].tolist() == [10]


def test_city_metric_estimate_respects_each_school_before_aggregating():
    demographic = pd.DataFrame(
        [
            ["Colegio A", "Instagram", "Ciudad", "Ciudad 1", 90],
            ["Colegio A", "Instagram", "Ciudad", "Ciudad 2", 10],
            ["Colegio B", "Instagram", "Ciudad", "Ciudad 1", 10],
            ["Colegio B", "Instagram", "Ciudad", "Ciudad 2", 90],
        ],
        columns=["colegio", "plataforma", "criterio", "ubicacion", "valor"],
    )
    performance = pd.DataFrame(
        [
            ["Colegio A", "Instagram", "Interacciones", 1000],
            ["Colegio B", "Instagram", "Interacciones", 100],
            ["Colegio A", "Instagram", "Visualizaciones", 100],
            ["Colegio B", "Instagram", "Visualizaciones", 1000],
        ],
        columns=["colegio", "plataforma", "metrica", "valor"],
    )

    interactions = build_city_metric_estimate(
        demographic, performance, "interacciones"
    ).set_index("ubicacion")
    views = build_city_metric_estimate(
        demographic, performance, "visualizaciones"
    ).set_index("ubicacion")

    assert interactions.loc["Ciudad 1", "valor"] == 910
    assert interactions.loc["Ciudad 2", "valor"] == 190
    assert views.loc["Ciudad 1", "valor"] == 190
    assert views.loc["Ciudad 2", "valor"] == 910

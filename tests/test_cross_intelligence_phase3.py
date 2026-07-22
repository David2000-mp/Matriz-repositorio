"""Pruebas matemáticas de segmentación profunda e inteligencia estadística."""

import pandas as pd
import pytest

from utils.chart_theme import ESCALA_IMPACTO_AMARILLA
from utils.cross_intelligence import (
    build_city_performance_drilldown,
    build_cohort_series,
    build_school_ranking,
    build_segmented_performance,
    calculate_demographic_performance_correlation,
    calculate_metric_total,
)


def _performance_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["2026-01", "Colegio A", "Instagram", "interacciones", 100],
            ["2026-01", "Colegio A", "Instagram", "visualizaciones", 1000],
            ["2026-01", "Colegio A", "Facebook", "interacciones", 200],
            ["2026-01", "Colegio A", "Facebook", "visualizaciones", 2000],
        ],
        columns=["month_key", "colegio", "plataforma", "metrica_norm", "valor"],
    )


def _demographic_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["2026-01", "Colegio A", "Instagram", "Mujeres", "18-24", 30],
            ["2026-01", "Colegio A", "Instagram", "Hombres", "18-24", 70],
            ["2026-01", "Colegio A", "Facebook", "Mujeres", "18-24", 50],
            ["2026-01", "Colegio A", "Facebook", "Hombres", "18-24", 50],
        ],
        columns=["month_key", "colegio", "plataforma", "sexo", "edad", "valor"],
    ).assign(criterio_norm="demografia base")


def test_metric_selector_never_adds_interactions_and_views():
    performance = _performance_df()

    assert calculate_metric_total(performance, "interacciones") == 300
    assert calculate_metric_total(performance, "visualizaciones") == 3000

    ranking = build_school_ranking(performance, "interacciones")
    assert ranking["rendimiento"].sum() == 300
    assert "volumen_total" not in ranking.columns

    assert calculate_metric_total(pd.DataFrame(), "interacciones") == 0


def test_city_impact_uses_only_the_selected_metric():
    city_demo = pd.DataFrame(
        {
            "criterio_norm": ["ciudad", "ciudad"],
            "ubicacion": ["Ciudad A", "Ciudad B"],
            "valor": [75, 25],
        }
    )

    result = build_city_performance_drilldown(
        _performance_df(), city_demo, "interacciones"
    )

    assert result["rendimiento_estimado"].sum() == pytest.approx(300)
    assert result.loc[result["ciudad"] == "Ciudad A", "rendimiento_estimado"].iloc[0] == 225
    assert "volumen_estimado" not in result.columns


def test_segmented_performance_combines_platform_sex_and_age_filters():
    result = build_segmented_performance(
        _performance_df(),
        _demographic_df(),
        "interacciones",
        sexo="Mujeres",
        edad="18-24",
    ).set_index("plataforma")

    assert result.loc["Instagram", "participacion_segmento_pct"] == 30
    assert result.loc["Instagram", "rendimiento_segmentado_estimado"] == 30
    assert result.loc["Facebook", "participacion_segmento_pct"] == 50
    assert result.loc["Facebook", "rendimiento_segmentado_estimado"] == 100


def test_pearson_and_spearman_use_matched_months_and_known_values():
    performance = pd.DataFrame(
        {
            "month_key": ["2026-01", "2026-02", "2026-03"],
            "metrica_norm": ["interacciones"] * 3,
            "valor": [100, 200, 300],
        }
    )
    demographic = pd.DataFrame(
        {
            "month_key": ["2026-01", "2026-02", "2026-03"],
            "criterio_norm": ["demografia base"] * 3,
            "sexo": ["Mujeres"] * 3,
            "edad": ["18-24"] * 3,
            "valor": [10, 20, 30],
        }
    )

    pearson = calculate_demographic_performance_correlation(
        performance, demographic, "interacciones", "Mujeres", "18-24", "pearson"
    )
    spearman = calculate_demographic_performance_correlation(
        performance, demographic, "interacciones", "Mujeres", "18-24", "spearman"
    )

    assert pearson.sample_size == 3
    assert pearson.coefficient == pytest.approx(1.0)
    assert spearman.coefficient == pytest.approx(1.0)


def test_cohort_tracks_monthly_share_for_a_stable_segment():
    demographic = pd.DataFrame(
        [
            ["2026-01", "Mujeres", "18-24", 10],
            ["2026-01", "Hombres", "18-24", 90],
            ["2026-02", "Mujeres", "18-24", 25],
            ["2026-02", "Hombres", "18-24", 75],
        ],
        columns=["month_key", "sexo", "edad", "valor"],
    ).assign(criterio_norm="demografia base")

    cohort = build_cohort_series(demographic, "Mujeres", "18-24")

    assert cohort["participacion_pct"].tolist() == [10, 25]
    assert cohort["month_key"].tolist() == ["2026-01", "2026-02"]


def test_yellow_impact_scale_has_light_and_dark_contrast():
    assert len(ESCALA_IMPACTO_AMARILLA) >= 4
    assert ESCALA_IMPACTO_AMARILLA[0][1] != ESCALA_IMPACTO_AMARILLA[-1][1]

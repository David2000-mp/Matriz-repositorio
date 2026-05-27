import pandas as pd

from utils.analytics import calculate_health_score, detect_anomalies


def test_calculate_health_score_matches_expected_formula_components():
    df = pd.DataFrame(
        {
            "fecha": pd.to_datetime(
                [
                    "2023-05-31",
                    "2024-05-31",
                    "2024-05-31",
                ]
            ),
            "plataforma": ["Instagram", "Instagram", "Facebook"],
            "seguidores": [1000, 1200, 800],
            "interacciones": [50, 96, 64],
        }
    )

    # latest month followers = 2000, interacciones = 160 => engagement_curr = 8.0
    # historical month engagement = 5.0 => ratio 1.6 => engagement_component 40
    # yoy: (2000 - 1000)/1000 = 100% => yoy_component 30
    # consistency: plataformas curr(2) / total plataformas(2) => 20
    # total = 90
    score = calculate_health_score(df)
    assert round(score, 2) == 90.00


def test_detect_anomalies_flags_spike_with_vectorized_baseline():
    df = pd.DataFrame(
        {
            "fecha": pd.to_datetime(
                [
                    "2024-01-31",
                    "2024-02-29",
                    "2024-03-31",
                    "2024-04-30",
                ]
            ),
            "id_cuenta": ["acct_1", "acct_1", "acct_1", "acct_1"],
            "seguidores": [100, 102, 101, 180],
            "interacciones": [20, 21, 20, 45],
        }
    )

    out = detect_anomalies(df, threshold=0.20)

    assert "anomalia_seguidores" in out.columns
    assert "anomalia_interacciones" in out.columns
    assert bool(out.iloc[-1]["anomalia_seguidores"]) is True
    assert bool(out.iloc[-1]["anomalia_interacciones"]) is True

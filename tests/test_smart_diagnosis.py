import pandas as pd

from utils.smart_diagnosis import (
    build_recommendation_text,
    category_effectiveness,
    compute_volatility_guardrail,
)


def test_volatility_guardrail_triggers_when_relative_diff_above_30pct():
    values = [1.0, 1.2, 1.1, 8.0]
    result = compute_volatility_guardrail(values)

    assert result["is_volatile"] is True
    assert result["relative_diff"] > 0.30


def test_category_effectiveness_requires_min_samples():
    df = pd.DataFrame(
        [
            {"categoria": "Admisiones", "total": 120},
            {"categoria": "Admisiones", "total": 100},
            {"categoria": "Eventos", "total": 300},
        ]
    )

    result = category_effectiveness(df, followers=2000, min_samples=2)

    assert result["has_signal"] is True
    assert result["best_category"]["categoria"] == "Admisiones"


def test_recommendation_text_contains_actor_and_guidance():
    text = build_recommendation_text(
        actor_name="David",
        diagnosis_level="promedio",
        posts_per_week=2.0,
        best_category="Admisiones",
        is_volatile=False,
    )

    assert "David" in text
    assert "Admisiones" in text

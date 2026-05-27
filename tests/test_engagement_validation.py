from pathlib import Path
import sys
import importlib

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
engagement_validation = importlib.import_module("utils.engagement_validation")

normalize_engagement_rate = engagement_validation.normalize_engagement_rate
normalize_engagement_series = engagement_validation.normalize_engagement_series


def test_normalize_engagement_rate_handles_fraction_percent_and_comma_values():
    assert normalize_engagement_rate(0.5) == 50.0
    assert normalize_engagement_rate("2,5") == 2.5
    assert normalize_engagement_rate(" 3.2% ") == 3.2


def test_normalize_engagement_rate_clamps_and_handles_invalid_inputs():
    assert normalize_engagement_rate(None) == 0.0
    assert normalize_engagement_rate("no-num") == 0.0
    assert normalize_engagement_rate(-2) == 0.0
    assert normalize_engagement_rate(250) == 100.0


def test_normalize_engagement_series_applies_canonical_rule_vectorized():
    series = pd.Series(["0,8", "4", "180", None, "foo", -1])
    normalized = normalize_engagement_series(series)

    assert normalized.tolist() == [80.0, 4.0, 100.0, 0.0, 0.0, 0.0]

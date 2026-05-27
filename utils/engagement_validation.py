"""Utilities to normalize and validate engagement rate values.

Canonical rule:
- Accept numeric-like values with comma or dot decimal separators.
- If value is in [0, 1], treat as fraction and convert to percentage.
- If value is > 1, treat as percentage directly.
- Clamp final value to [0, max_percent].
"""

from __future__ import annotations

from typing import Any
import pandas as pd


def normalize_engagement_rate(value: Any, max_percent: float = 100.0) -> float:
    """Normalize one engagement value into a percentage in [0, max_percent]."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0

    text = str(value).strip()
    if not text:
        return 0.0

    cleaned = (
        text.replace("%", "")
        .replace("\u00a0", "")
        .replace(" ", "")
        .replace(",", ".")
    )

    numeric = pd.to_numeric(cleaned, errors="coerce")
    if pd.isna(numeric):
        return 0.0

    numeric = float(numeric)
    if numeric <= 1.0:
        numeric *= 100.0

    if numeric < 0.0:
        return 0.0
    if numeric > max_percent:
        return float(max_percent)
    return numeric


def normalize_engagement_series(series: pd.Series, max_percent: float = 100.0) -> pd.Series:
    """Normalize a pandas Series of engagement values into percentages."""
    return series.apply(lambda value: normalize_engagement_rate(value, max_percent=max_percent))

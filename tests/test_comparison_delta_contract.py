import pandas as pd

from views import comparison


def test_delta_table_uses_na_when_periods_are_misaligned(monkeypatch):
    markdown_calls = []
    info_calls = []

    monkeypatch.setattr(comparison.st, "markdown", lambda text, **kwargs: markdown_calls.append(text))
    monkeypatch.setattr(comparison.st, "info", lambda text: info_calls.append(text))

    data_entity = pd.DataFrame(
        {
            "fecha": pd.to_datetime(["2024-02-29"]),
            "plataforma": ["Instagram"],
            "seguidores": [1200],
            "engagement_rate": [6.5],
            "interacciones": [300],
        }
    )

    benchmark = pd.DataFrame(
        {
            "fecha": pd.to_datetime(["2024-01-31"]),
            "plataforma": ["Instagram"],
            "seguidores_avg": [1000],
            "engagement_rate_avg": [5.0],
            "interacciones_avg": [250],
        }
    )

    comparison._render_delta_table("Entidad X", data_entity, benchmark)

    assert info_calls
    assert "desalineación temporal" in info_calls[0]
    assert markdown_calls
    assert "N/A" in markdown_calls[-1]


def test_delta_table_uses_na_when_network_denominator_is_zero(monkeypatch):
    markdown_calls = []

    monkeypatch.setattr(comparison.st, "markdown", lambda text, **kwargs: markdown_calls.append(text))
    monkeypatch.setattr(comparison.st, "info", lambda _text: None)

    aligned_date = pd.to_datetime(["2024-02-29"])

    data_entity = pd.DataFrame(
        {
            "fecha": aligned_date,
            "plataforma": ["Instagram"],
            "seguidores": [1500],
            "engagement_rate": [4.0],
            "interacciones": [210],
        }
    )

    benchmark = pd.DataFrame(
        {
            "fecha": aligned_date,
            "plataforma": ["Instagram"],
            "seguidores_avg": [0.0],
            "engagement_rate_avg": [0.0],
            "interacciones_avg": [0.0],
        }
    )

    comparison._render_delta_table("Entidad X", data_entity, benchmark)

    assert markdown_calls
    assert "N/A" in markdown_calls[-1]

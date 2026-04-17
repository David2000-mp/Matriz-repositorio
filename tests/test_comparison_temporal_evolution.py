from pathlib import Path
import sys
import importlib

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
comparison = importlib.import_module("views.comparison")


class _FakeStreamlit:
    def __init__(self):
        self.figures = []

    def columns(self, n):
        return [self for _ in range(n)]

    def metric(self, *args, **kwargs):
        return None

    def plotly_chart(self, fig, **kwargs):
        self.figures.append(fig)

    def info(self, *args, **kwargs):
        return None


def test_followers_evolution_sums_all_platforms_per_date(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(comparison, "st", fake_st)

    data_a = pd.DataFrame(
        {
            "fecha": ["2026-02-01", "2026-02-01", "2026-03-01", "2026-03-01"],
            "plataforma": ["Facebook", "Instagram", "Facebook", "Instagram"],
            "seguidores": [100, 50, 120, 70],
        }
    )

    data_b = pd.DataFrame(columns=["fecha", "plataforma", "seguidores"])

    comparison._render_followers_evolution_comparison("Entidad A", data_a, "Entidad B", data_b)

    assert fake_st.figures, "No se generó la figura de evolución de seguidores"
    fig = fake_st.figures[-1]

    assert len(fig.data) >= 1
    assert list(fig.data[0].y) == [150, 190]


def test_benchmark_followers_chart_uses_sum_when_all_platforms(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(comparison, "st", fake_st)

    data_entity = pd.DataFrame(
        {
            "fecha": ["2026-03-01", "2026-03-01"],
            "plataforma": ["Facebook", "Instagram"],
            "seguidores": [100, 50],
        }
    )

    benchmark = pd.DataFrame(
        {
            "fecha": ["2026-03-01", "2026-03-01"],
            "plataforma": ["Facebook", "Instagram"],
            "seguidores_avg": [200, 300],
        }
    )

    comparison._render_benchmark_chart(
        entity="Entidad A",
        data_entity=data_entity,
        benchmark=benchmark,
        metric_entity="seguidores",
        metric_bench="seguidores_avg",
        ylabel="Seguidores",
        plataforma_sel="Todas",
    )

    assert fake_st.figures, "No se generó la figura de benchmark"
    fig = fake_st.figures[-1]

    assert len(fig.data) == 2
    assert list(fig.data[0].y) == [150]
    assert list(fig.data[1].y) == [500]


def test_benchmark_engagement_chart_uses_mean_when_all_platforms(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr(comparison, "st", fake_st)

    data_entity = pd.DataFrame(
        {
            "fecha": ["2026-03-01", "2026-03-01"],
            "plataforma": ["Facebook", "Instagram"],
            "engagement_rate": [2.0, 4.0],
        }
    )

    benchmark = pd.DataFrame(
        {
            "fecha": ["2026-03-01", "2026-03-01"],
            "plataforma": ["Facebook", "Instagram"],
            "engagement_rate_avg": [1.0, 3.0],
        }
    )

    comparison._render_benchmark_chart(
        entity="Entidad A",
        data_entity=data_entity,
        benchmark=benchmark,
        metric_entity="engagement_rate",
        metric_bench="engagement_rate_avg",
        ylabel="Engagement (%)",
        plataforma_sel="Todas",
    )

    assert fake_st.figures, "No se generó la figura de benchmark de engagement"
    fig = fake_st.figures[-1]

    assert len(fig.data) == 2
    assert list(fig.data[0].y) == [3.0]
    assert list(fig.data[1].y) == [2.0]
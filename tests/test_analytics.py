import math
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from utils.analytics import calculate_growth_metrics


def make_df(rows):
    return pd.DataFrame(rows)[
        [
            "id_cuenta",
            "fecha",
            "seguidores",
            "alcance",
            "interacciones",
            "engagement_rate",
        ]
    ]


def test_happy_path_delta_seguidores_febrero_10_por_ciento():
    df = make_df(
        [
            {
                "id_cuenta": "A",
                "fecha": "2024-01-15",
                "seguidores": 100,
                "alcance": 1000,
                "interacciones": 20,
                "engagement_rate": 20.0,
            },
            {
                "id_cuenta": "A",
                "fecha": "2024-02-15",
                "seguidores": 110,
                "alcance": 1100,
                "interacciones": 22,
                "engagement_rate": 20.0,
            },
        ]
    )

    res = calculate_growth_metrics(df)
    assert list(res["Mes"]) == ["2024-01", "2024-02"]
    feb_delta = float(res.loc[res["Mes"] == "2024-02", "Delta_Seguidores"].iloc[0])
    assert pytest.approx(feb_delta, abs=1e-6) == 10.0


def test_division_por_cero_mes_anterior_cero_no_inf_ni_excepcion():
    df = make_df(
        [
            {
                "id_cuenta": "A",
                "fecha": "2024-01-10",
                "seguidores": 0,
                "alcance": 0,
                "interacciones": 0,
                "engagement_rate": 0.0,
            },
            {
                "id_cuenta": "A",
                "fecha": "2024-02-10",
                "seguidores": 50,
                "alcance": 500,
                "interacciones": 10,
                "engagement_rate": 20.0,
            },
        ]
    )

    # No debe lanzar excepción
    res = calculate_growth_metrics(df)
    feb_val = res.loc[res["Mes"] == "2024-02", "Delta_Seguidores"].iloc[0]

    # Puede ser NaN (controlado) o un valor finito, pero no inf
    assert not math.isinf(feb_val if pd.notna(feb_val) else 0.0)
    # Aceptamos NaN o un valor finito cualquiera
    assert pd.isna(feb_val) or np.isfinite(feb_val)


def test_engagement_ponderado_sobre_promedio_simple():
    # Mes único con dos cuentas para probar ponderación
    df = make_df(
        [
            {
                "id_cuenta": "A",
                "fecha": "2024-01-05",
                "seguidores": 1000,
                "alcance": 5000,
                "interacciones": 100,
                "engagement_rate": 10.0,  # 100/1000
            },
            {
                "id_cuenta": "B",
                "fecha": "2024-01-12",
                "seguidores": 100,
                "alcance": 800,
                "interacciones": 50,
                "engagement_rate": 50.0,  # 50/100
            },
        ]
    )

    res = calculate_growth_metrics(df)
    assert list(res["Mes"]) == ["2024-01"]
    # Ponderado: (150 / 1100) * 100 ~= 13.63636
    eng = float(res.loc[0, "Engagement"])
    assert eng != pytest.approx(30.0, abs=1e-2)  # no es promedio simple
    assert eng == pytest.approx(13.6364, abs=1e-2)


def test_orden_cronologico_sobre_datos_desordenados():
    df = make_df(
        [
            {
                "id_cuenta": "A",
                "fecha": "2024-03-10",
                "seguidores": 300,
                "alcance": 3000,
                "interacciones": 30,
                "engagement_rate": 10.0,
            },
            {
                "id_cuenta": "A",
                "fecha": "2024-01-10",
                "seguidores": 100,
                "alcance": 1000,
                "interacciones": 10,
                "engagement_rate": 10.0,
            },
            {
                "id_cuenta": "A",
                "fecha": "2024-02-10",
                "seguidores": 200,
                "alcance": 2000,
                "interacciones": 20,
                "engagement_rate": 10.0,
            },
        ]
    )

    res = calculate_growth_metrics(df)
    assert list(res["Mes"]) == ["2024-01", "2024-02", "2024-03"]

import pandas as pd

from utils.validators import (
    get_monthly_pending_institutions,
    normalize_report_date_to_month_start,
)


def test_normalize_report_date_to_month_start():
    normalized = normalize_report_date_to_month_start("2026-03-15")
    assert normalized.strftime("%Y-%m-%d") == "2026-03-01"


def test_pending_report_critical_warning_complete_and_duplicates():
    universe = ["Institucion A", "Institucion B", "Institucion C", "Institucion D"]

    # B: 1 plataforma (Advertencia)
    # C: 2 plataformas (Completa, no debe aparecer)
    # D: duplicados en la misma plataforma (debe contar como 1)
    # A: 0 plataformas (Crítico)
    df = pd.DataFrame(
        [
            {
                "entidad": "Institucion B",
                "plataforma": "Instagram",
                "fecha": "2026-03-10",
            },
            {
                "entidad": "Institucion C",
                "plataforma": "Facebook",
                "fecha": "2026-03-05",
            },
            {
                "entidad": "Institucion C",
                "plataforma": "Instagram",
                "fecha": "2026-03-20",
            },
            {
                "entidad": "Institucion D",
                "plataforma": "TikTok",
                "fecha": "2026-03-04",
            },
            {
                "entidad": "Institucion D",
                "plataforma": "TikTok",
                "fecha": "2026-03-26",
            },
        ]
    )

    report = get_monthly_pending_institutions(
        df,
        min_platforms=2,
        universe_institutions=universe,
    )

    assert report["target_month"] == "2026-03"

    rows = {row["institucion"]: row for row in report["pending_rows"]}

    assert rows["Institucion A"]["estado"] == "Crítico"
    assert rows["Institucion A"]["plataformas_actuales"] == 0

    assert rows["Institucion B"]["estado"] == "Advertencia"
    assert rows["Institucion B"]["plataformas_actuales"] == 1

    assert rows["Institucion D"]["estado"] == "Advertencia"
    assert rows["Institucion D"]["plataformas_actuales"] == 1

    # C tiene 2 plataformas, por lo tanto no está pendiente
    assert "Institucion C" not in rows

    assert report["summary"]["total_activas"] == 4
    assert report["summary"]["completas"] == 1
    assert report["summary"]["pendientes"] == 3

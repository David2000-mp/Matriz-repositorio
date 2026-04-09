from utils.report_generator import generate_engagement_report_html
from views.engagement_calculator_v2 import calculate_growth_potential, validate_post_engagement


def _base_payload(expected: dict, content_stats: dict):
    return {
        "platform": "facebook",
        "followers": 2500,
        "days": 30,
        "posts_list": [
            {"num": 1, "type": "📸 Imagen", "total": 120},
            {"num": 2, "type": "🎥 Video", "total": 90},
        ],
        "engagement_pct": 8.4,
        "engagement_per_post": 4.2,
        "engagement_by_views": 0.0,
        "posts_per_week": 3.5,
        "diagnosis": "🟡 BUENO",
        "content_stats": content_stats,
        "growth_scenarios": {
            10: {"growth_pct": 5, "followers_3m": 2625},
            20: {"growth_pct": 10, "followers_3m": 2750},
            30: {"growth_pct": 15, "followers_3m": 2875},
        },
        "expected": expected,
    }


def test_report_html_accepts_new_expected_contract():
    expected = {"typical": 3.5, "min": 1.5, "max": 8.0, "label": "Tipico 3.5%"}
    content_stats = {
        "📸 Imagen": {"posts": 1, "total_interactions": 120, "avg_engagement": 4.8},
        "🎥 Video": {"posts": 1, "total_interactions": 90, "avg_engagement": 3.6},
    }

    html = generate_engagement_report_html(**_base_payload(expected, content_stats))

    assert "Reporte de Engagement" in html
    assert "4.80%" in html


def test_report_html_accepts_legacy_expected_contract_without_keyerror():
    expected = {
        "bajo": 0.5,
        "aceptable": 1.0,
        "bueno": 2.0,
        "labels": {"bueno": "1% - 2%"},
    }
    content_stats = {
        "📸 Imagen": {"posts": 1, "total_interactions": 120, "avg_engagement": 4.8},
        "🎥 Video": {"posts": 1, "total_interactions": 90, "avg_engagement": 3.6},
    }

    html = generate_engagement_report_html(**_base_payload(expected, content_stats))

    assert "Reporte de Engagement" in html
    assert "1% - 2%" in html


def test_report_prefers_avg_engagement_when_engagement_missing():
    expected = {"typical": 3.5, "min": 1.5, "max": 8.0, "label": "Tipico 3.5%"}
    content_stats = {
        "📸 Imagen": {"posts": 1, "total_interactions": 120, "avg_engagement": 4.8},
        "🎥 Video": {"posts": 1, "total_interactions": 90, "avg_engagement": 3.6},
    }

    html = generate_engagement_report_html(**_base_payload(expected, content_stats))

    assert "4.80%" in html
    assert "3.60%" in html


def test_report_includes_period_header_when_dates_are_provided():
    expected = {"typical": 3.5, "min": 1.5, "max": 8.0, "label": "Tipico 3.5%"}
    content_stats = {
        "📸 Imagen": {"posts": 1, "total_interactions": 120, "avg_engagement": 4.8},
        "🎥 Video": {"posts": 1, "total_interactions": 90, "avg_engagement": 3.6},
    }
    payload = _base_payload(expected, content_stats)
    payload["days"] = 12
    payload["period_start"] = "2026-03-01"
    payload["period_end"] = "2026-03-12"
    payload["total_posts"] = 9

    html = generate_engagement_report_html(**payload)

    assert "Periodo Analizado: 2026-03-01 al 2026-03-12 (12 dias) - Total: 9 posts" in html


def test_report_marks_post_mode_for_hybrid_tiktok():
    expected = {"typical": 3.5, "min": 1.5, "max": 8.0, "label": "Tipico 3.5%"}
    content_stats = {
        "🎥 Video": {"posts": 2, "total_interactions": 50, "avg_engagement": 1.0},
    }
    payload = _base_payload(expected, content_stats)
    payload["platform"] = "tiktok"
    payload["analysis_mode"] = "hybrid"
    payload["posts_list"] = [
        {"num": 1, "type": "🎥 Video", "categoria": "Eventos", "total": 50, "analysis_mode": "standard"},
        {"num": 2, "type": "🎥 Video", "categoria": "Eventos", "total": 0, "analysis_mode": "views_only"},
    ]

    html = generate_engagement_report_html(**payload)

    assert "Modo de análisis:</strong> Hibrido" in html
    assert "<th>Modo</th>" in html
    assert "Comunidad" in html
    assert "Alcance" in html


def test_report_includes_visual_executive_summary_and_action_plan():
    expected = {"typical": 3.5, "min": 1.5, "max": 8.0, "label": "Tipico 3.5%"}
    content_stats = {
        "🎥 Video": {"posts": 2, "total_interactions": 260, "total_views": 12000, "total_saves": 10, "avg_engagement": 5.2},
        "📸 Imagen": {"posts": 2, "total_interactions": 180, "total_views": 18000, "total_saves": 26, "avg_engagement": 3.6},
    }
    payload = _base_payload(expected, content_stats)
    payload["content_insights"] = {
        "best_format": {"tipo": "🎥 Video", "avg_engagement": 5.2},
        "most_consumed_format": {"tipo": "📸 Imagen", "metric_label": "Vistas totales", "metric_value": 18000},
        "most_saved_format": {"tipo": "📸 Imagen", "metric_value": 26},
        "best_combo": {"label": "🎥 Video + Eventos", "avg_engagement": 5.2},
    }

    html = generate_engagement_report_html(**payload)

    assert "Resumen Ejecutivo del Contenido" in html
    assert "🎥 Video + Eventos" in html
    assert "Qué repetir" in html
    assert "lo más consumido no es lo que mejor convierte" in html.lower()
    assert "Cómo se calcularon estas cifras" in html
    assert "(interacciones totales / seguidores) × 100" in html


def test_report_uses_correct_instagram_title():
    expected = {"typical": 3.5, "min": 1.5, "max": 8.0, "label": "Tipico 3.5%"}
    content_stats = {
        "📸 Imagen": {"posts": 1, "total_interactions": 120, "avg_engagement": 4.8},
    }
    payload = _base_payload(expected, content_stats)
    payload["platform"] = "instagram"

    html = generate_engagement_report_html(**payload)

    assert "<title>Reporte de Engagement - Instagram</title>" in html


def test_growth_projection_uses_relative_improvement_not_plus_ten_points():
    scenarios = calculate_growth_potential(2.0, 1000, "facebook")

    assert round(scenarios[10]["new_engagement"], 2) == 2.2
    assert round(scenarios[20]["new_engagement"], 2) == 2.4
    assert round(scenarios[30]["new_engagement"], 2) == 2.6


def test_validate_post_engagement_flags_over_hundred_percent_as_suspicious():
    result = validate_post_engagement(150, 0, 0, 100)

    assert result["status"] == "red"
    assert "sospechosos" in result["message"].lower()

from utils.rules_engine import calculate_engagement_engine


def test_rules_engine_facebook_formula_and_breakdown_priority():
    row = {
        "Reacciones": 100,
        "Comentarios": 20,
        "Compartidos": 10,
        "Interacciones": 999,
        "followers": 1000,
    }
    result = calculate_engagement_engine("facebook", row)

    assert result.total_interactions == 130
    assert result.total_source == "breakdown"
    assert result.er_community == 13.0


def test_rules_engine_manual_fallback_and_inconsistency_flag():
    row_manual = {
        "Reacciones": 0,
        "Comentarios": 0,
        "Compartidos": 0,
        "Interacciones": 77,
        "followers": 1000,
    }
    manual_result = calculate_engagement_engine("facebook", row_manual)
    assert manual_result.total_interactions == 77
    assert manual_result.total_source == "manual"
    assert manual_result.has_inconsistency is False

    row_inconsistent = {
        "Me gusta": 40,
        "Comentarios": 10,
        "Compartidos": 5,
        "Interacciones": 99,
        "followers": 1000,
    }
    inconsistent_result = calculate_engagement_engine("tiktok", row_inconsistent)
    assert inconsistent_result.total_interactions == 55
    assert inconsistent_result.has_inconsistency is True
    assert inconsistent_result.inconsistency_reason == "desglose!=manual"


def test_rules_engine_tiktok_views_only_mode_is_valid():
    row_views_only = {
        "Me gusta": 0,
        "Comentarios": 0,
        "Compartidos": 0,
        "Interacciones": 0,
        "Vistas": 12000,
        "followers": 5000,
    }

    result = calculate_engagement_engine("tiktok", row_views_only)

    assert result.total_interactions == 0
    assert result.total_source == "none"
    assert result.er_community == 0.0
    assert result.analysis_mode == "views_only"
    assert result.is_views_only is True

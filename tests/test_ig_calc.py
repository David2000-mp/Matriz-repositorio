from utils.rules_engine import calculate_engagement_engine


def test_instagram_formula_uses_likes_plus_comments_only():
    row = {
        "Me gusta": 200,
        "Comentarios": 50,
        "Compartidos": 1000,
        "followers": 5000,
    }
    result = calculate_engagement_engine("instagram", row)

    assert result.total_interactions == 250
    assert result.er_community == 5.0

import pandas as pd

from utils.content_analyzer import classify_school_content, identify_top_performer
from utils.rules_engine import calculate_engagement_engine


def test_end_to_end_grid_to_engine_to_ranking():
    followers = 2000
    grid = pd.DataFrame(
        [
            {"Post #": 1, "Categoria": "Eventos", "Tipo": "📸 Imagen", "Me gusta": 100, "Comentarios": 20, "Compartidos": 10, "Interacciones": 0},
            {"Post #": 2, "Categoria": "Admisiones", "Tipo": "🎥 Video", "Me gusta": 80, "Comentarios": 30, "Compartidos": 0, "Interacciones": 0},
        ]
    )

    totals = []
    ers = []
    for _, row in grid.iterrows():
        result = calculate_engagement_engine("instagram", {**row.to_dict(), "followers": followers})
        totals.append(result.total_interactions)
        ers.append(result.er_community)

    grid["Interacciones"] = totals
    grid["ER Post"] = ers

    classified = classify_school_content(grid)
    ranked = identify_top_performer(classified["data"])

    assert classified["is_valid"] is True
    assert ranked["has_data"] is True
    assert int(ranked["top_post"]["Post #"]) == 1


def test_end_to_end_tiktok_hybrid_includes_reach_posts():
    followers = 5000
    grid = pd.DataFrame(
        [
            {"Post #": 1, "Categoria": "Eventos", "Tipo": "🎥 Video", "Me gusta": 40, "Comentarios": 5, "Compartidos": 2, "Vistas": 7000, "Interacciones": 0},
            {"Post #": 2, "Categoria": "Eventos", "Tipo": "🎥 Video", "Me gusta": 0, "Comentarios": 0, "Compartidos": 0, "Vistas": 12000, "Interacciones": 0},
        ]
    )

    modes = []
    totals = []
    for _, row in grid.iterrows():
        result = calculate_engagement_engine("tiktok", {**row.to_dict(), "followers": followers})
        modes.append(result.analysis_mode)
        totals.append(result.total_interactions)

    assert "standard" in modes
    assert "views_only" in modes
    assert totals == [47, 0]

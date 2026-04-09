import pandas as pd

import views.engagement_calculator_v2 as calc_view
from utils.content_analyzer import build_content_action_plan, summarize_content_insights
from views.engagement_calculator_v2 import (
    apply_pending_draft_restore,
    calculate_posts_per_week,
    count_captured_posts,
    load_draft_snapshot,
    queue_draft_restore_request,
    save_draft_snapshot,
)


def test_summarize_content_insights_detects_best_consumed_and_saved_formats():
    df = pd.DataFrame(
        [
            {"Tipo": "🎥 Video", "Categoria": "Eventos", "Interacciones": 220, "Vistas": 9000, "Guardados": 12, "Comentarios": 20, "Compartidos": 10},
            {"Tipo": "🎥 Video", "Categoria": "Vida Estudiantil", "Interacciones": 180, "Vistas": 7000, "Guardados": 8, "Comentarios": 18, "Compartidos": 6},
            {"Tipo": "📸 Imagen", "Categoria": "Admisiones", "Interacciones": 95, "Vistas": 2500, "Guardados": 20, "Comentarios": 7, "Compartidos": 3},
            {"Tipo": "📸 Imagen", "Categoria": "Admisiones", "Interacciones": 75, "Vistas": 2300, "Guardados": 18, "Comentarios": 5, "Compartidos": 2},
        ]
    )

    summary = summarize_content_insights(df, followers=4000)

    assert summary["best_format"]["tipo"] == "🎥 Video"
    assert summary["most_consumed_format"]["tipo"] == "🎥 Video"
    assert summary["most_saved_format"]["tipo"] == "📸 Imagen"


def test_draft_snapshot_round_trip(tmp_path):
    draft_path = tmp_path / "engagement_draft.json"
    payload = {
        "wizard_platform": "tiktok",
        "wizard_followers": 3500,
        "wizard_days": 30,
        "wizard_posts_grid": [
            {"Post #": 1, "Tipo": "🎥 Video", "Guardados": 14, "Comentarios": 5},
        ],
    }

    save_draft_snapshot(payload, draft_path=draft_path)
    loaded = load_draft_snapshot(draft_path=draft_path)

    assert loaded is not None
    assert loaded["wizard_platform"] == "tiktok"
    assert loaded["wizard_followers"] == 3500
    assert loaded["wizard_posts_grid"][0]["Guardados"] == 14
    assert "saved_at" in loaded


def test_summarize_content_insights_detects_best_type_category_combo():
    df = pd.DataFrame(
        [
            {"Tipo": "🎥 Video", "Categoria": "Eventos", "Interacciones": 260, "Vistas": 9200, "Guardados": 16},
            {"Tipo": "🎥 Video", "Categoria": "Eventos", "Interacciones": 220, "Vistas": 8100, "Guardados": 12},
            {"Tipo": "📸 Imagen", "Categoria": "Admisiones", "Interacciones": 120, "Vistas": 3000, "Guardados": 20},
            {"Tipo": "📸 Imagen", "Categoria": "Admisiones", "Interacciones": 80, "Vistas": 2100, "Guardados": 11},
        ]
    )

    summary = summarize_content_insights(df, followers=4000)

    assert summary["best_combo"]["tipo"] == "🎥 Video"
    assert summary["best_combo"]["categoria"] == "Eventos"
    assert summary["best_combo"]["label"] == "🎥 Video + Eventos"


def test_build_content_action_plan_explains_consumption_vs_conversion_gap():
    actions = build_content_action_plan(
        {
            "best_format": {"tipo": "🎥 Video", "avg_engagement": 5.2},
            "most_consumed_format": {"tipo": "📸 Imagen", "metric_label": "Vistas totales", "metric_value": 18000},
            "most_saved_format": {"tipo": "📸 Imagen", "metric_value": 26},
            "best_combo": {"label": "🎥 Video + Eventos", "avg_engagement": 5.2},
        },
        best_category={"categoria": "Eventos"},
    )

    joined = " ".join(actions).lower()
    assert "lo más consumido no es lo que mejor convierte" in joined
    assert "video + eventos" in joined
    assert "eventos" in joined


def test_apply_pending_draft_restore_updates_state_without_touching_widgets():
    state = {}
    payload = {
        "wizard_followers": 4200,
        "wizard_days": 21,
        "wizard_posts_grid": [{"Post #": 1, "Tipo": "🎥 Video", "Guardados": 9}],
        "saved_at": "2026-04-08T10:30:00",
    }

    queue_draft_restore_request(payload, state=state)
    applied = apply_pending_draft_restore(state=state)

    assert applied is True
    assert state["wizard_followers"] == 4200
    assert state["wizard_followers_input"] == 4200
    assert state["wizard_days"] == 21
    assert state["wizard_days_input"] == 21
    assert list(state["wizard_posts_grid"].columns) == ["Post #", "Tipo", "Guardados"]
    assert "wizard_restore_pending" not in state


def test_posting_frequency_counts_captured_posts_not_only_posts_with_interactions():
    df = pd.DataFrame(
        [
            {"Post #": 1, "Fecha Publicacion": "2026-04-01", "Tipo": "📸 Imagen", "Categoria": "Eventos", "Interacciones": 0, "Vistas": 0, "URL/Link": "", "Comentario": "Publicado sin respuesta"},
            {"Post #": 2, "Fecha Publicacion": "2026-04-05", "Tipo": "🎥 Video", "Categoria": "Admisiones", "Interacciones": 80, "Vistas": 0, "URL/Link": "", "Comentario": ""},
        ]
    )

    captured = count_captured_posts(df)
    per_week = calculate_posts_per_week(captured, 14)

    assert captured == 2
    assert per_week == 1.0


def test_summarize_content_insights_ignores_blank_placeholder_rows():
    df = pd.DataFrame(
        [
            {"Post #": 1, "Tipo": "🎥 Video", "Categoria": "Eventos", "Interacciones": 200, "Vistas": 5000, "Guardados": 12},
            {"Post #": 2, "Tipo": "📸 Imagen", "Categoria": "Admisiones", "Interacciones": 100, "Vistas": 2500, "Guardados": 5},
            {"Post #": 3, "Tipo": "", "Categoria": "", "Interacciones": 0, "Vistas": 0, "Guardados": 0},
        ]
    )

    summary = summarize_content_insights(df, followers=1000)

    tipos = set(summary["table"]["Tipo"].tolist())
    assert "" not in tipos
    assert "Sin tipo" not in tipos


def test_load_draft_snapshot_does_not_restore_other_platform_latest_draft(tmp_path):
    original_dir = calc_view.DRAFT_DIR
    calc_view.DRAFT_DIR = tmp_path
    try:
        save_draft_snapshot({"wizard_platform": "facebook", "wizard_followers": 1111}, platform="facebook")

        loaded = load_draft_snapshot(platform="instagram")

        assert loaded is None
    finally:
        calc_view.DRAFT_DIR = original_dir

import pandas as pd

from views.dashboard import (
    _build_google_latest_snapshot,
    _is_google_platform,
    _split_social_and_google,
)


def test_google_aliases_are_identified_without_matching_social_networks():
    google_aliases = [
        "Google",
        "Google Maps",
        "google_maps",
        "Google Business Profile",
        "GBP",
        "Maps",
    ]

    assert all(_is_google_platform(value) for value in google_aliases)
    assert not _is_google_platform("Facebook")
    assert not _is_google_platform("Instagram")
    assert not _is_google_platform("TikTok")


def test_google_is_excluded_from_social_benchmark_source():
    source = pd.DataFrame(
        {
            "entidad": ["A", "A", "B", "B"],
            "plataforma": ["Facebook", "Google Maps", "Instagram", "Google"],
            "engagement_rate": [2.0, 9.8, 3.0, 9.4],
        }
    )

    social, google = _split_social_and_google(source)

    assert social["plataforma"].tolist() == ["Facebook", "Instagram"]
    assert google["plataforma"].tolist() == ["Google Maps", "Google"]
    assert not social["plataforma"].map(_is_google_platform).any()


def test_google_snapshot_keeps_latest_record_per_institution():
    source = pd.DataFrame(
        {
            "entidad": ["A", "A", "B"],
            "plataforma": ["Google Maps", "Google Maps", "Google"],
            "fecha": ["2026-01-01", "2026-03-01", "2026-02-01"],
            "calificacion_redes": [8.0, 9.0, 7.5],
        }
    )

    snapshot = _build_google_latest_snapshot(source)

    assert len(snapshot) == 2
    assert snapshot.set_index("entidad").loc["A", "calificacion_redes"] == 9.0
    assert snapshot.set_index("entidad").loc["A", "fecha"] == pd.Timestamp("2026-03-01")

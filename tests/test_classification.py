import pandas as pd

from utils.content_analyzer import classify_school_content


def test_classification_maps_categories_and_detects_missing():
    df = pd.DataFrame(
        [
            {"Post #": 1, "Categoria": "admisiones", "Tipo": "📸 Imagen"},
            {"Post #": 2, "Categoria": "", "Tipo": "🎥 Video"},
        ]
    )

    result = classify_school_content(df)
    out = result["data"]

    assert out.loc[0, "Categoria Canonica"] == "Admisiones"
    assert result["is_valid"] is False
    assert 1 in result["missing_rows"]

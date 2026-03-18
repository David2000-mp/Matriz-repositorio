import pandas as pd

from utils.content_analyzer import identify_top_performer


def test_identify_top_performer_breaks_tie_with_interactions():
    df = pd.DataFrame(
        [
            {"num": 1, "ER Post": 4.0, "Interacciones": 100},
            {"num": 2, "ER Post": 4.0, "Interacciones": 150},
            {"num": 3, "ER Post": 3.0, "Interacciones": 200},
        ]
    )

    result = identify_top_performer(df)

    assert result["has_data"] is True
    assert int(result["top_post"]["num"]) == 2

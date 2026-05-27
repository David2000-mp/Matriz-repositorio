import pandas as pd

from utils.data_provider import data_provider


def test_dummy_provider_contract_uses_typed_dataframes():
    merged = data_provider.get_merged_data(force_reload=True)

    assert merged is not None
    assert not merged.empty
    assert "id_cuenta" in merged.columns
    assert merged["id_cuenta"].dtype == object
    assert "fecha" in merged.columns
    assert pd.api.types.is_datetime64_any_dtype(merged["fecha"])

"""Pruebas de contratos de descarga exacta y calidad de Fase 4."""

import pandas as pd

from utils.analysis_delivery import (
    build_quality_report,
    dataframe_to_csv_bytes,
    quality_has_warnings,
    safe_file_stem,
)


def test_csv_export_preserves_exact_columns_rows_and_unicode():
    source = pd.DataFrame({"Ciudad": ["Mérida"], "Valor": [12.5]})

    restored = pd.read_csv(pd.io.common.BytesIO(dataframe_to_csv_bytes(source)))

    assert restored.columns.tolist() == source.columns.tolist()
    assert restored.to_dict("records") == source.to_dict("records")


def test_quality_report_detects_structural_anomalies():
    source = pd.DataFrame(
        {
            "fecha": ["2026-01-01", "fecha-invalida", "fecha-invalida"],
            "colegio": ["A", None, None],
            "valor": [10, -1, -1],
        }
    )

    report = build_quality_report(
        {"Rendimiento": source},
        {"Rendimiento": ["fecha", "colegio", "plataforma", "valor"]},
    ).iloc[0]

    assert report["Duplicados exactos"] == 1
    assert report["Valores negativos"] == 2
    assert report["Fechas inválidas"] == 2
    assert report["Llaves incompletas"] == 2
    assert report["Columnas requeridas ausentes"] == "plataforma"
    assert quality_has_warnings(pd.DataFrame([report]))


def test_safe_file_stem_is_portable():
    assert safe_file_stem("Gráfica: Mujeres 18-24 / Julio") == (
        "gr_fica_mujeres_18-24_julio"
    )

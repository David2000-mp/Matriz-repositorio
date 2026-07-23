"""Componentes Streamlit para descargas exactas y paneles de calidad."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import pandas as pd
import streamlit as st

from utils.analysis_delivery import (
    build_quality_report,
    dataframe_to_csv_bytes,
    quality_has_warnings,
    safe_file_stem,
)


def render_exact_download(
    df: pd.DataFrame,
    file_stem: str,
    *,
    label: str = "Descargar datos de esta gráfica",
    key: str | None = None,
) -> None:
    """Descarga exactamente el DataFrame transformado que recibió la gráfica."""
    local = df.copy() if df is not None else pd.DataFrame()
    safe_stem = safe_file_stem(file_stem)
    st.download_button(
        label,
        data=dataframe_to_csv_bytes(local),
        file_name=f"{safe_stem}.csv",
        mime="text/csv",
        key=key or f"download_{safe_stem}",
        disabled=local.empty,
    )
    st.caption(f"Archivo exacto de la visualización: {len(local):,} filas.")


def render_quality_panel(
    sources: Mapping[str, pd.DataFrame],
    required_columns: Mapping[str, Sequence[str]],
    *,
    panel_key: str,
) -> pd.DataFrame:
    """Muestra y permite descargar el diagnóstico de calidad del corte activo."""
    report = build_quality_report(sources, required_columns)
    with st.expander("Calidad y cobertura de datos", expanded=False):
        if quality_has_warnings(report):
            st.warning(
                "El corte contiene vacíos, duplicados, llaves incompletas o columnas "
                "ausentes. Revisa el detalle antes de interpretar resultados."
            )
        else:
            st.success("El corte no presenta anomalías estructurales detectables.")
        st.dataframe(report, width="stretch", hide_index=True)
        render_exact_download(
            report,
            f"calidad_{panel_key}",
            label="Descargar reporte de calidad",
            key=f"download_quality_{panel_key}",
        )
    return report

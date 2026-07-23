"""Exportacion automatica de los datos visibles en graficas de CHAMPILEAKS."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from utils.analysis_delivery import safe_file_stem


PLOTLY_VECTOR_FIELDS = (
    "x",
    "y",
    "lat",
    "lon",
    "labels",
    "values",
    "ids",
    "parents",
    "locations",
    "r",
    "theta",
    "text",
    "hovertext",
    "open",
    "high",
    "low",
    "close",
)


def _as_list(value: Any) -> list[Any]:
    """Convierte arreglos Plotly/Pandas en listas sin romper valores escalares."""
    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        return [value]
    if hasattr(value, "tolist"):
        converted = value.tolist()
        return converted if isinstance(converted, list) else [converted]
    if isinstance(value, Iterable):
        return list(value)
    return [value]


def _trace_name(trace_data: dict[str, Any], index: int) -> str:
    name = trace_data.get("name")
    return str(name) if name not in (None, "") else f"Serie {index + 1}"


def _matrix_trace_rows(trace_data: dict[str, Any], index: int) -> list[dict[str, Any]]:
    z_rows = _as_list(trace_data.get("z"))
    if not z_rows or not isinstance(z_rows[0], list):
        return []

    x_values = _as_list(trace_data.get("x"))
    y_values = _as_list(trace_data.get("y"))
    rows: list[dict[str, Any]] = []
    for row_index, values in enumerate(z_rows):
        for column_index, value in enumerate(_as_list(values)):
            rows.append(
                {
                    "serie": _trace_name(trace_data, index),
                    "tipo_traza": trace_data.get("type", ""),
                    "x": (
                        x_values[column_index]
                        if column_index < len(x_values)
                        else column_index
                    ),
                    "y": y_values[row_index] if row_index < len(y_values) else row_index,
                    "z": value,
                }
            )
    return rows


def _expand_customdata(value: Any, row_count: int) -> dict[str, list[Any]]:
    custom_rows = _as_list(value)
    if not custom_rows:
        return {}
    if custom_rows and not isinstance(custom_rows[0], list):
        return {"customdata": custom_rows}

    width = max((len(_as_list(row)) for row in custom_rows), default=0)
    expanded: dict[str, list[Any]] = {}
    for column_index in range(width):
        expanded[f"customdata_{column_index + 1}"] = [
            (_as_list(row)[column_index] if column_index < len(_as_list(row)) else None)
            for row in custom_rows[:row_count]
        ]
    return expanded


def plotly_figure_to_dataframe(fig: Any) -> pd.DataFrame:
    """Materializa los puntos realmente contenidos en una figura Plotly.

    El resultado usa formato largo: cada fila representa un punto, barra, porcion,
    celda de mapa de calor o coordenada que Plotly recibio para renderizar.
    """
    if fig is None or not hasattr(fig, "data"):
        return pd.DataFrame()

    output_rows: list[dict[str, Any]] = []
    for trace_index, trace in enumerate(fig.data):
        trace_data = (
            trace.to_plotly_json() if hasattr(trace, "to_plotly_json") else dict(trace)
        )
        matrix_rows = _matrix_trace_rows(trace_data, trace_index)
        if matrix_rows:
            output_rows.extend(matrix_rows)
            continue

        vectors = {
            field: _as_list(trace_data.get(field))
            for field in PLOTLY_VECTOR_FIELDS
            if trace_data.get(field) is not None
        }
        row_count = max((len(values) for values in vectors.values()), default=0)
        custom = _expand_customdata(trace_data.get("customdata"), row_count)
        row_count = max([row_count, *(len(values) for values in custom.values())])
        if row_count == 0:
            continue

        for row_index in range(row_count):
            row: dict[str, Any] = {
                "serie": _trace_name(trace_data, trace_index),
                "tipo_traza": trace_data.get("type", ""),
            }
            for field, values in {**vectors, **custom}.items():
                row[field] = values[row_index] if row_index < len(values) else None
            output_rows.append(row)

    return pd.DataFrame(output_rows)


def native_chart_to_dataframe(data: Any) -> pd.DataFrame:
    """Conserva valores e indice de las graficas nativas de Streamlit."""
    if data is None:
        return pd.DataFrame()
    if isinstance(data, pd.Series):
        name = data.name or "valor"
        return data.rename(name).rename_axis(data.index.name or "indice").reset_index()
    if isinstance(data, pd.DataFrame):
        local = data.copy()
        return local.rename_axis(local.index.name or "indice").reset_index()
    try:
        return pd.DataFrame(data)
    except (TypeError, ValueError):
        return pd.DataFrame({"valor": [data]})


def matplotlib_figure_to_dataframe(fig: Any) -> pd.DataFrame:
    """Extrae lineas, barras y puntos visibles de una figura Matplotlib."""
    if fig is None or not hasattr(fig, "axes"):
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for axis_index, axis in enumerate(fig.axes):
        for line_index, line in enumerate(axis.get_lines()):
            for x_value, y_value in zip(line.get_xdata(), line.get_ydata()):
                rows.append(
                    {
                        "eje": axis_index + 1,
                        "serie": line.get_label() or f"Linea {line_index + 1}",
                        "tipo_traza": "linea",
                        "x": x_value,
                        "y": y_value,
                    }
                )
        for patch_index, patch in enumerate(axis.patches):
            if not all(hasattr(patch, attr) for attr in ("get_x", "get_y", "get_height")):
                continue
            rows.append(
                {
                    "eje": axis_index + 1,
                    "serie": f"Barra {patch_index + 1}",
                    "tipo_traza": "barra",
                    "x": patch.get_x(),
                    "y": patch.get_y(),
                    "alto": patch.get_height(),
                    "ancho": patch.get_width() if hasattr(patch, "get_width") else None,
                }
            )
        for collection_index, collection in enumerate(axis.collections):
            if not hasattr(collection, "get_offsets"):
                continue
            for x_value, y_value in collection.get_offsets():
                rows.append(
                    {
                        "eje": axis_index + 1,
                        "serie": f"Puntos {collection_index + 1}",
                        "tipo_traza": "dispersion",
                        "x": x_value,
                        "y": y_value,
                    }
                )
    return pd.DataFrame(rows)


def plotly_file_stem(fig: Any, fallback: str = "datos_grafica") -> str:
    """Obtiene un nombre de archivo legible desde el titulo de la figura."""
    try:
        title = fig.layout.title.text
    except (AttributeError, TypeError):
        title = None
    return safe_file_stem(title or fallback)

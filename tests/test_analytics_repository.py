"""Pruebas del repositorio central de bases analíticas."""

import pandas as pd

from utils.analytics_repository import AnalyticsDataRepository
from utils.metric_catalog import METRIC_ALIASES, canonical_metric_name


class _Worksheet:
    def __init__(self, records):
        self._records = records

    def get_all_records(self):
        if isinstance(self._records, Exception):
            raise self._records
        return self._records


class _Spreadsheet:
    def __init__(self, sheets):
        self._sheets = sheets
        self.requested_sheets = []

    def worksheet(self, name):
        self.requested_sheets.append(name)
        return _Worksheet(self._sheets[name])


def test_repository_loads_both_sheets_with_one_connection_and_shared_contract():
    spreadsheet = _Spreadsheet(
        {
            "Base_Maestra_Colegios": [
                {
                    "Fecha": "2026-07-31 23:59:59",
                    "Colegio": " Colegio A ",
                    "Plataforma": "Instagram",
                    "Métrica": "Interacciones",
                    "Valor": "15",
                },
                {
                    "Fecha": "2026-07-31",
                    "Colegio": "Colegio A",
                    "Plataforma": "Instagram",
                    "Métrica": "Interacciones",
                    "Valor": -1,
                },
            ],
            "Base_Demografica_Colegios": [
                {
                    "Fecha de reporte": "2026-07-31 22:30:00",
                    "Colegio": "Colegio A",
                    "Plataforma": "Instagram",
                    "Criterio": "Ciudad",
                    "Sexo": "",
                    "Edad": "",
                    "Ubicación": "Ciudad Victoria",
                    "Valor": "20",
                },
                {
                    "Fecha de reporte": "fecha inválida",
                    "Colegio": "Colegio A",
                    "Plataforma": "Instagram",
                    "Criterio": "Ciudad",
                    "Sexo": "",
                    "Edad": "",
                    "Ubicación": "Victoria",
                    "Valor": "10",
                },
            ],
        }
    )
    connection_calls = 0

    def connection_factory():
        nonlocal connection_calls
        connection_calls += 1
        return spreadsheet

    snapshot = AnalyticsDataRepository(connection_factory).load()

    assert connection_calls == 1
    assert spreadsheet.requested_sheets == [
        "Base_Maestra_Colegios",
        "Base_Demografica_Colegios",
    ]
    assert snapshot.maestra["valor"].tolist() == [15]
    assert snapshot.maestra["colegio"].tolist() == ["Colegio A"]
    assert snapshot.maestra["fecha"].iloc[0] == pd.Timestamp("2026-07-31 23:59:59")
    assert snapshot.demografica["valor"].tolist() == [20]
    assert snapshot.demografica["ubicacion"].tolist() == ["Ciudad Victoria"]
    assert snapshot.demografica["fecha_reporte"].iloc[0] == pd.Timestamp(
        "2026-07-31 22:30:00"
    )


def test_repository_isolates_a_sheet_failure_without_losing_the_other_base():
    spreadsheet = _Spreadsheet(
        {
            "Base_Maestra_Colegios": RuntimeError("hoja no disponible"),
            "Base_Demografica_Colegios": [
                {
                    "fecha_reporte": "2026-07-01",
                    "colegio": "Colegio B",
                    "plataforma": "Facebook",
                    "criterio": "Demografia base",
                    "sexo": "Mujeres",
                    "edad": "18-24",
                    "ubicacion": "",
                    "valor": 30,
                }
            ],
        }
    )

    snapshot = AnalyticsDataRepository(lambda: spreadsheet).load()

    assert snapshot.maestra.empty
    assert list(snapshot.maestra.columns) == [
        "fecha",
        "colegio",
        "plataforma",
        "metrica",
        "valor",
    ]
    assert snapshot.demografica["valor"].tolist() == [30]


def test_metric_aliases_have_one_canonical_source():
    assert canonical_metric_name("interaccion") == "interacciones"
    assert canonical_metric_name("views") == "visualizaciones"
    assert canonical_metric_name("alcance") is None
    assert METRIC_ALIASES["interacciones"].isdisjoint(
        METRIC_ALIASES["visualizaciones"]
    )

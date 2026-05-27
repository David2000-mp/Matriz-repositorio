import pandas as pd

from utils.form_response_importer import import_form_responses, _generate_account_id


class FakeWorksheet:
    def __init__(self, raw_data):
        self._raw_data = raw_data

    def get(self):
        return self._raw_data


class FakeSpreadsheet:
    def __init__(self, raw_data):
        self._raw_data = raw_data

    def worksheet(self, name: str):
        assert name == "Respuestas de formulario 3"
        return FakeWorksheet(self._raw_data)


FORM_HEADERS = [
    "Marca temporal",
    "Fecha del Reporte",
    "Institución Marista",
    "Plataforma Social",
    "Usuario o URL",
    "Seguidores Totales",
    "Engagement Rate (%)",
    "Alcance Total",
    "Interacciones Totales",
    "Comentarios Contextuales",
]


def test_generate_account_id_normalizes_facebook_url_variants():
    id_base = _generate_account_id(
        "Instituto Hidalguense",
        "Facebook",
        "https://www.facebook.com/MaristasIH",
    )
    id_with_query = _generate_account_id(
        "Instituto Hidalguense",
        "Facebook",
        "https://www.facebook.com/MaristasIH/?locale=es_LA",
    )

    assert id_base == id_with_query


def test_import_form_responses_consolidates_same_facebook_account_when_username_is_blank_later():
    raw_rows = [
        FORM_HEADERS,
        [
            "2026-02-01 10:00",
            "01/02/2026",
            "Instituto Hidalguense",
            "Facebook",
            "https://www.facebook.com/MaristasIH/?locale=es_LA",
            "2800",
            "0.41",
            "0",
            "",
            "",
        ],
        [
            "2026-03-01 10:00",
            "01/03/2026",
            "Instituto Hidalguense",
            "facebook",
            "",
            "2800",
            "0.00",
            "0",
            "",
            "",
        ],
    ]

    cuentas_df, metricas_df = import_form_responses(FakeSpreadsheet(raw_rows))

    fb_accounts = cuentas_df[
        (cuentas_df["entidad"] == "Instituto Hidalguense")
        & (cuentas_df["plataforma"] == "Facebook")
    ]

    assert len(fb_accounts) == 1
    assert metricas_df["id_cuenta"].nunique() == 1
    assert list(pd.to_datetime(metricas_df["fecha"]).dt.strftime("%Y-%m-%d")) == ["2026-02-01", "2026-03-01"]
    assert fb_accounts.iloc[0]["usuario_red"] == "https://www.facebook.com/MaristasIH/?locale=es_LA"


def test_import_form_responses_parses_engagement_values_with_percent_symbol():
    raw_rows = [
        FORM_HEADERS,
        [
            "2026-03-01 10:00",
            "01/03/2026",
            "Universidad Marista de Querétaro",
            "Facebook",
            "https://www.facebook.com/universidadmaristaqro",
            "5900",
            "0.49%",
            "1000",
            "",
            "",
        ],
    ]

    _, metricas_df = import_form_responses(FakeSpreadsheet(raw_rows))

    assert len(metricas_df) == 1
    assert metricas_df.iloc[0]["engagement_rate"] == 0.49
    assert metricas_df.iloc[0]["interacciones"] == 28


def test_import_form_responses_maps_new_fields_without_usuario_red():
    raw_rows = [
        [
            "Fecha del Reporte",
            "Institución Marista",
            "Plataforma Social",
            "Seguidores Totales",
            "Engagement Rate ()",
            "Calificación en Redes",
            "Qué tipo de contenido fue el más viral",
            "Publicación más viral (Números)",
            "Publicación Más viral",
            "Media de interacción",
            "Del 1 al 10, ¿Qué calificación le pones al diseño de la página?",
        ],
        [
            "01/03/2026",
            "Centro Universitario México",
            "Facebook",
            "12000",
            "1.25",
            "8",
            "Video",
            "430",
            "Video institucional marzo",
            "280.5",
            "9",
        ],
    ]

    cuentas_df, metricas_df = import_form_responses(FakeSpreadsheet(raw_rows))

    assert len(cuentas_df) == 1
    assert cuentas_df.iloc[0]["usuario_red"] == ""
    assert cuentas_df.iloc[0]["id_cuenta"].startswith("form_")

    assert len(metricas_df) == 1
    row = metricas_df.iloc[0]
    assert row["calificacion_redes"] == 8.0
    assert row["tipo_contenido_mas_viral"] == "Video"
    assert row["publicacion_mas_viral_numeros"] == 430.0
    assert row["publicacion_destacada"] == "Video institucional marzo"
    assert row["media_interaccion"] == 280.5
    assert row["calificacion_diseno"] == 9.0

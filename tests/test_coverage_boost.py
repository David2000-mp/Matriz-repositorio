"""
========================================
TESTS DE INTEGRACIÓN PARA COBERTURA 80%
========================================

Tests enfocados en aumentar cobertura ejecutando las líneas reales
de manejo de errores y edge cases en data_manager.py.

OBJETIVO: 50% → 80%+

Líneas a cubrir:
- 127-130, 145-149: conectar_sheets() errors
- 183-184, 203-212, 231-240: load_data() sheet reading errors
- 248-287: load_data() error handling (429, CSV fallback)
- 323-374: guardar_datos() errors
- 407, 413-458: save_batch() error paths
- 488-490, 497-499: get_id() with None df
- 539-540, 549-552: reset_db() errors
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime
import os

from utils.data_manager import (
    conectar_sheets,
    load_data,
    guardar_datos,
    save_batch,
    get_id,
    reset_db,
)


# ========================================
# TESTS DE save_batch()
# ========================================


@pytest.mark.integration
def test_save_batch_con_multiples_registros_sin_duplicados(
    mock_conectar_sheets, tmp_path
):
    """
    TEST: save_batch() procesa múltiples registros sin duplicados

    OBJETIVO: Cubrir líneas 401, 411, 418, 425-426 (flujo normal de save_batch)
    """

    # ARRANGE
    datos = [
        {
            "id_cuenta": "test1",
            "entidad": "Entity 1",
            "plataforma": "Facebook",
            "usuario_red": "@entity1",
            "fecha": "2024-03-01",
            "seguidores": 1000,
            "alcance": 5000,
            "interacciones": 200,
            "likes_promedio": 40,
        },
        {
            "id_cuenta": "test2",
            "entidad": "Entity 2",
            "plataforma": "Instagram",
            "usuario_red": "@entity2",
            "fecha": "2024-03-01",
            "seguidores": 2000,
            "alcance": 10000,
            "interacciones": 500,
            "likes_promedio": 100,
        },
        {
            "id_cuenta": "test3",
            "entidad": "Entity 3",
            "plataforma": "LinkedIn",
            "usuario_red": "entity-3",
            "fecha": "2024-03-01",
            "seguidores": 500,
            "alcance": 2000,
            "interacciones": 80,
            "likes_promedio": 16,
        },
    ]

    # Mock CSVs
    csv_cuentas = tmp_path / "cuentas.csv"
    csv_metricas = tmp_path / "metricas.csv"

    def fake_load_data():
        return (
            pd.DataFrame(columns=["id_cuenta", "entidad", "plataforma", "usuario_red"]),
            pd.DataFrame(
                columns=[
                    "id_cuenta",
                    "fecha",
                    "seguidores",
                    "alcance",
                    "interacciones",
                    "likes_promedio",
                    "engagement_rate",
                ]
            ),
        )

    def fake_guardar_datos(df):
        # No hacer nada, solo simular éxito
        pass

    with (
        patch("utils.data_manager.load_data", fake_load_data),
        patch("utils.data_manager.guardar_datos", fake_guardar_datos),
        patch("utils.data_manager.CUENTAS_CSV", csv_cuentas),
        patch("utils.data_manager.METRICAS_CSV", csv_metricas),
        patch("streamlit.cache_data.clear"),
        patch("streamlit.warning"),
    ):
        # ACT
        save_batch(datos)

        # ASSERT
        # Verificar que se creó el CSV
        assert csv_metricas.exists(), "CSV de métricas debe haberse creado"

        # Leer y verificar contenido
        df_saved = pd.read_csv(csv_metricas)
        assert len(df_saved) == 3, "Debe haber 3 registros guardados"
        assert (
            "engagement_rate" in df_saved.columns
        ), "Debe tener engagement_rate calculado"


@pytest.mark.integration
def test_save_batch_con_datos_duplicados_elimina_correctamente(
    mock_conectar_sheets, tmp_path
):
    """
    TEST: save_batch() elimina duplicados por cuenta+fecha

    OBJETIVO: Cubrir líneas 405-408, 439-440 (eliminación de duplicados)
    """

    # ARRANGE: Métricas existentes con una entrada
    csv_cuentas = tmp_path / "cuentas.csv"
    csv_metricas = tmp_path / "metricas.csv"

    # Crear métrica existente (con fecha como datetime)
    df_existing = pd.DataFrame(
        {
            "id_cuenta": ["duplicate_test"],
            "entidad": ["Duplicate Test"],
            "plataforma": ["Facebook"],
            "usuario_red": ["@dup"],
            "fecha": [pd.Timestamp("2024-03-15")],
            "seguidores": [1000],
            "alcance": [5000],
            "interacciones": [200],
            "likes_promedio": [40.0],
            "engagement_rate": [20.0],
        }
    )
    df_existing.to_csv(csv_metricas, index=False)

    # 2 registros con mismo id_cuenta y fecha (duplicados)
    datos = [
        {
            "id_cuenta": "duplicate_test",
            "entidad": "Duplicate Test",
            "plataforma": "Facebook",
            "usuario_red": "@dup",
            "fecha": "2024-03-15",
            "seguidores": 1100,
            "alcance": 5500,
            "interacciones": 220,
            "likes_promedio": 44,
        },
        {
            "id_cuenta": "duplicate_test",
            "entidad": "Duplicate Test",
            "plataforma": "Facebook",
            "usuario_red": "@dup",
            "fecha": "2024-03-15",  # Misma fecha
            "seguidores": 1200,  # Valores diferentes
            "alcance": 6000,
            "interacciones": 240,
            "likes_promedio": 48,
        },
    ]

    def fake_load_data():
        return (
            pd.DataFrame(columns=["id_cuenta", "entidad", "plataforma", "usuario_red"]),
            df_existing,
        )

    with (
        patch("utils.data_manager.load_data", fake_load_data),
        patch("utils.data_manager.guardar_datos"),
        patch("utils.data_manager.CUENTAS_CSV", csv_cuentas),
        patch("utils.data_manager.METRICAS_CSV", csv_metricas),
        patch("streamlit.cache_data.clear"),
        patch("streamlit.warning"),
    ):
        # ACT
        save_batch(datos)

        # ASSERT
        # Leer CSV guardado
        df_saved = pd.read_csv(csv_metricas)
        # Debe haber eliminado duplicados: 1 registro existente eliminado, 1 nuevo guardado
        assert len(df_saved) == 1, "Debe haber eliminado duplicados"
        assert (
            df_saved.iloc[0]["seguidores"] == 1200
        ), "Debe mantener el último registro"


@pytest.mark.integration
def test_save_batch_maneja_error_en_guardar_datos(mock_conectar_sheets, tmp_path):
    """
    TEST: save_batch() maneja error cuando guardar_datos() falla

    OBJETIVO: Cubrir líneas 448 (warning cuando falla guardar_datos)
    """

    # ARRANGE
    csv_cuentas = tmp_path / "cuentas.csv"
    csv_metricas = tmp_path / "metricas.csv"

    datos = [
        {
            "id_cuenta": "test_error",
            "entidad": "Error Entity",
            "plataforma": "Facebook",
            "usuario_red": "@error",
            "fecha": "2024-03-01",
            "seguidores": 1000,
            "alcance": 5000,
            "interacciones": 200,
            "likes_promedio": 40,
        }
    ]

    def fake_load_data():
        return (
            pd.DataFrame(columns=["id_cuenta", "entidad", "plataforma", "usuario_red"]),
            pd.DataFrame(
                columns=[
                    "id_cuenta",
                    "fecha",
                    "seguidores",
                    "alcance",
                    "interacciones",
                    "likes_promedio",
                    "engagement_rate",
                ]
            ),
        )

    def fake_guardar_datos(df):
        # Simular error en Google Sheets
        raise Exception("Google Sheets API Error")

    with (
        patch("utils.data_manager.load_data", fake_load_data),
        patch("utils.data_manager.guardar_datos", fake_guardar_datos),
        patch("utils.data_manager.CUENTAS_CSV", csv_cuentas),
        patch("utils.data_manager.METRICAS_CSV", csv_metricas),
        patch("streamlit.cache_data.clear"),
        patch("streamlit.warning") as mock_warning,
    ):
        # ACT
        save_batch(datos)

        # ASSERT
        # Verificar que se mostró warning
        assert mock_warning.called, "Debe mostrar warning cuando falla guardar_datos"


# ========================================
# TESTS DE get_id() CON CASOS EDGE
# ========================================


@pytest.mark.unit
def test_get_id_cuando_df_cuentas_es_none_carga_desde_load_data(mock_conectar_sheets):
    """
    TEST: get_id() carga df_cuentas desde load_data() si es None

    OBJETIVO: Cubrir líneas 477, 483-485 (llamada a load_data cuando df_cuentas_cache=None)
    """

    # ARRANGE
    fake_df_cuentas = pd.DataFrame(
        columns=["id_cuenta", "entidad", "plataforma", "usuario_red"]
    )
    fake_df_metricas = pd.DataFrame(columns=["id_cuenta", "fecha", "seguidores"])

    with patch(
        "utils.data_manager.load_data", return_value=(fake_df_cuentas, fake_df_metricas)
    ) as mock_load:
        # ACT
        resultado = get_id("Nueva Entidad", "TikTok", "@nueva", df_cuentas_cache=None)

        # ASSERT
        # Verificar que load_data() fue llamado
        assert (
            mock_load.called
        ), "load_data() debe ser llamado cuando df_cuentas_cache=None"

        # Resultado debe ser un nuevo ID
        assert isinstance(resultado, str)
        assert len(resultado) == 32  # MD5 hash length


@pytest.mark.unit
def test_get_id_cuando_df_cuentas_vacio_genera_nuevo_id(mock_conectar_sheets):
    """
    TEST: get_id() genera nuevo ID cuando df_cuentas está vacío

    OBJETIVO: Cubrir líneas 483-485 (generación de ID cuando no hay coincidencias)
    """

    # ARRANGE: DataFrame vacío
    df_empty = pd.DataFrame(
        columns=["id_cuenta", "entidad", "plataforma", "usuario_red"]
    )

    # ACT
    resultado = get_id("New Entity", "Twitter", "@new", df_cuentas_cache=df_empty)

    # ASSERT
    assert isinstance(resultado, str)
    assert len(resultado) == 32  # MD5 hash es 32 caracteres
    # Verificar que es lowercase (normalizado)
    assert resultado == resultado.lower(), "ID debe estar en lowercase"


# ========================================
# TESTS DE MANEJO DE ERRORES EN load_data()
# ========================================


@pytest.mark.integration
def test_load_data_con_worksheet_que_lanza_excepcion(tmp_path):
    """
    TEST: load_data() maneja excepción en worksheet.get_all_records()

    OBJETIVO: Cubrir líneas 193-195, 232-234 (try-except en lectura de sheets)
    """

    # ARRANGE: Mock que lanza excepción en worksheet
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_records.side_effect = Exception("Worksheet read error")
    mock_spreadsheet.worksheet.return_value = mock_worksheet

    # Crear CSVs temporales para fallback
    csv_cuentas = tmp_path / "cuentas.csv"
    csv_metricas = tmp_path / "metricas.csv"

    # CSV vacío pero válido
    pd.DataFrame(columns=["id_cuenta", "entidad", "plataforma", "usuario_red"]).to_csv(
        csv_cuentas, index=False
    )
    pd.DataFrame(
        columns=[
            "id_cuenta",
            "fecha",
            "seguidores",
            "alcance",
            "interacciones",
            "likes_promedio",
            "engagement_rate",
        ]
    ).to_csv(csv_metricas, index=False)

    with (
        patch("utils.data_manager.conectar_sheets", return_value=mock_spreadsheet),
        patch("utils.data_manager.CUENTAS_CSV", csv_cuentas),
        patch("utils.data_manager.METRICAS_CSV", csv_metricas),
        patch("utils.data_manager.DATA_DIR", tmp_path),
        patch("streamlit.warning"),
    ):
        # ACT
        df_cuentas, df_metricas = load_data()

        # ASSERT
        # Debe devolver DataFrames (posiblemente vacíos) sin crashear
        assert isinstance(df_cuentas, pd.DataFrame)
        assert isinstance(df_metricas, pd.DataFrame)


@pytest.mark.integration
def test_load_data_con_error_429_loguea_y_usa_fallback(tmp_path):
    """
    TEST: load_data() detecta error 429 (quota exceeded) y usa CSV fallback

    OBJETIVO: Cubrir líneas 247-248 (detección de error 429)
    """

    # ARRANGE: Mock que lanza error 429
    mock_spreadsheet = MagicMock()
    error_429 = Exception("429: Quota exceeded for quota metric")
    mock_spreadsheet.worksheet.side_effect = error_429

    # Crear CSVs temporales
    csv_cuentas = tmp_path / "cuentas.csv"
    csv_metricas = tmp_path / "metricas.csv"
    data_dir = tmp_path

    pd.DataFrame(
        {
            "id_cuenta": ["test429"],
            "entidad": ["Test Entity"],
            "plataforma": ["Facebook"],
            "usuario_red": ["@test"],
        }
    ).to_csv(csv_cuentas, index=False)

    pd.DataFrame(
        {
            "id_cuenta": ["test429"],
            "fecha": ["2024-01-01"],
            "seguidores": [1000],
            "alcance": [5000],
            "interacciones": [100],
            "likes_promedio": [20.0],
            "engagement_rate": [10.0],
        }
    ).to_csv(csv_metricas, index=False)

    with (
        patch("utils.data_manager.logger") as mock_logger,
        patch("utils.data_manager.conectar_sheets", return_value=mock_spreadsheet),
        patch("utils.data_manager.CUENTAS_CSV", csv_cuentas),
        patch("utils.data_manager.METRICAS_CSV", csv_metricas),
        patch("utils.data_manager.DATA_DIR", data_dir),
        patch("streamlit.error") as mock_error,
        patch("streamlit.warning") as mock_warning,
    ):
        # ACT
        df_cuentas, df_metricas = load_data()
        # ASSERT
        assert (
            mock_error.called
            or mock_warning.called
            or mock_logger.error.called
            or mock_logger.warning.called
        ), "Debe mostrar error o warning para quota 429"
        assert len(df_cuentas) >= 1, "Debe cargar datos desde CSV fallback"
        assert len(df_metricas) >= 1, "Debe cargar métricas desde CSV fallback"


# ========================================
# TESTS DE MANEJO DE ERRORES EN guardar_datos()
# ========================================


@pytest.mark.integration
def test_guardar_datos_con_worksheet_que_falla_maneja_error(mock_conectar_sheets):
    """
    TEST: guardar_datos() maneja error cuando worksheet.append_rows() falla

    OBJETIVO: Cubrir líneas 330-333, 361-365 (try-except en append_rows)
    """

    # ARRANGE
    nuevo_df = pd.DataFrame(
        {
            "id_cuenta": ["errortest123"],
            "entidad": ["Error Test"],
            "plataforma": ["Instagram"],
            "usuario_red": ["@error"],
            "fecha": [pd.Timestamp("2024-05-01")],
            "seguidores": [1000],
            "alcance": [5000],
            "interacciones": [200],
            "likes_promedio": [40.0],
            "engagement_rate": [20.0],
        }
    )

    # Mock de spreadsheet donde append_rows falla
    mock_spreadsheet = MagicMock()
    mock_ws = MagicMock()
    mock_ws.append_rows.side_effect = Exception("API Error al actualizar")
    mock_spreadsheet.worksheet.return_value = mock_ws

    def fake_load_data():
        return (
            pd.DataFrame(columns=["id_cuenta", "entidad", "plataforma", "usuario_red"]),
            pd.DataFrame(
                columns=["id_cuenta", "fecha", "seguidores", "alcance", "interacciones"]
            ),
        )

    with (
        patch("utils.data_manager.conectar_sheets", return_value=mock_spreadsheet),
        patch("utils.data_manager.load_data", fake_load_data),
        patch("streamlit.error"),
    ):
        # ACT
        resultado = guardar_datos(nuevo_df)

        # ASSERT
        # No debe crashear, debe manejar el error gracefully
        # El resultado puede ser False o None dependiendo de dónde falle
        assert resultado is not True


# ========================================
# TESTS DE reset_db()
# ========================================


@pytest.mark.integration
def test_reset_db_con_worksheet_que_falla_maneja_error(mock_conectar_sheets):
    """
    TEST: reset_db() maneja errores cuando worksheet.clear() o append_row() fallan

    OBJETIVO: Cubrir líneas 534-535, 544-547 (manejo de errores en reset_db)
    """

    # ARRANGE: Mock donde clear() funciona pero append_row() falla
    mock_spreadsheet = MagicMock()
    mock_ws = MagicMock()
    mock_ws.clear.return_value = None  # clear() funciona
    mock_ws.append_row.side_effect = Exception("API Error en append_row")
    mock_spreadsheet.worksheet.return_value = mock_ws

    with (
        patch("utils.data_manager.conectar_sheets", return_value=mock_spreadsheet),
        patch("streamlit.error"),
        patch("streamlit.success"),
    ):
        # ACT & ASSERT
        # No debe crashear, debe manejar el error internamente
        try:
            reset_db()
            # Si llega aquí, el error fue manejado correctamente
            assert True
        except Exception:
            # Si lanza excepción, el test falla
            pytest.fail(
                "reset_db() debe manejar errores internamente sin lanzar excepciones"
            )


@pytest.mark.integration
def test_reset_db_sin_conexion_maneja_error():
    """
    TEST: reset_db() maneja caso cuando no hay conexión a Sheets

    OBJETIVO: Cubrir manejo de error cuando conectar_sheets() retorna None
    """

    # ARRANGE: Sin conexión
    with (
        patch("utils.data_manager.conectar_sheets", return_value=None),
        patch("streamlit.error"),
    ):
        # ACT & ASSERT
        try:
            reset_db()
            assert True
        except Exception:
            pytest.fail("reset_db() debe manejar falta de conexión sin crashear")


# ========================================
# NUEVOS TESTS PARA ALCANZAR 80%+ COBERTURA
# ========================================


@pytest.mark.integration
def test_conectar_sheets_falla_sin_credenciales():
    """
    TEST: conectar_sheets() retorna None cuando faltan credenciales

    OBJETIVO: Cubrir líneas 127-130 (error de credenciales)
    """
    # ARRANGE: Secrets sin credenciales
    fake_secrets = {}

    with (
        patch("streamlit.secrets", fake_secrets),
        patch("utils.data_manager.logger") as mock_logger,
        patch("streamlit.error") as mock_error,
    ):
        # ACT
        resultado = conectar_sheets()
        # ASSERT
        assert resultado is None, "Debe retornar None sin credenciales"
        assert mock_error.called or mock_logger.error.called, "Debe mostrar error"


@pytest.mark.integration
def test_conectar_sheets_falla_con_excepcion_gspread():
    """
    TEST: conectar_sheets() maneja excepciones de gspread

    OBJETIVO: Cubrir líneas 145-149 (manejo de excepciones)
    """
    # ARRANGE: Mock que lanza excepción en gspread
    fake_secrets = {
        "gcp_service_account": {"type": "service_account", "project_id": "test"}
    }

    with (
        patch("utils.data_manager.logger") as mock_logger,
        patch("streamlit.secrets", fake_secrets),
        patch(
            "google.oauth2.service_account.Credentials.from_service_account_info"
        ) as mock_creds,
        patch("streamlit.error") as mock_error,
        patch("streamlit.warning") as mock_warning,
    ):
        # Simular error en gspread.authorize
        mock_creds.side_effect = Exception("gspread API error")
        # ACT
        resultado = conectar_sheets()
        # ASSERT
        assert resultado is None, "Debe retornar None cuando falla gspread"
        assert (
            mock_error.called
            or mock_warning.called
            or mock_logger.error.called
            or mock_logger.warning.called
        ), "Debe mostrar error o warning"


@pytest.mark.integration
def test_load_data_sin_conexion_usa_csv_fallback(tmp_path):
    """
    TEST: load_data() usa CSV cuando conectar_sheets() retorna None

    OBJETIVO: Cubrir líneas 183-184, 248-287 (fallback completo a CSV)
    """
    # ARRANGE: Crear CSVs temporales con datos
    csv_cuentas = tmp_path / "cuentas.csv"
    csv_metricas = tmp_path / "metricas.csv"
    data_dir = tmp_path

    # Datos de prueba
    pd.DataFrame(
        {
            "id_cuenta": ["csv_test"],
            "entidad": ["CSV Entity"],
            "plataforma": ["Instagram"],
            "usuario_red": ["@csv"],
        }
    ).to_csv(csv_cuentas, index=False)

    pd.DataFrame(
        {
            "id_cuenta": ["csv_test"],
            "fecha": ["2024-06-01"],
            "seguidores": [2000],
            "alcance": [10000],
            "interacciones": [500],
            "likes_promedio": [100.0],
            "engagement_rate": [25.0],
        }
    ).to_csv(csv_metricas, index=False)

    with (
        patch("utils.data_manager.logger") as mock_logger,
        patch("utils.data_manager.conectar_sheets", return_value=None),
        patch("utils.data_manager.CUENTAS_CSV", csv_cuentas),
        patch("utils.data_manager.METRICAS_CSV", csv_metricas),
        patch("utils.data_manager.DATA_DIR", data_dir),
        patch("streamlit.error") as mock_error,
        patch("streamlit.warning") as mock_warning,
    ):
        # ACT
        df_cuentas, df_metricas = load_data()
        # ASSERT
        assert (
            mock_warning.called
            or mock_error.called
            or mock_logger.warning.called
            or mock_logger.error.called
        ), "Debe mostrar warning o error al usar fallback"
        assert len(df_cuentas) == 1, "Debe cargar datos desde CSV"
        assert len(df_metricas) == 1, "Debe cargar métricas desde CSV"
        assert df_cuentas.iloc[0]["id_cuenta"] == "csv_test"


@pytest.mark.integration
def test_load_data_worksheet_no_encontrado_maneja_error(tmp_path):
    """
    TEST: load_data() maneja error cuando worksheet no existe

    OBJETIVO: Cubrir líneas 203-212, 231-240 (error en worksheet.get_all_records)
    """
    # ARRANGE: Mock spreadsheet donde worksheet() lanza excepción
    mock_spreadsheet = MagicMock()
    mock_spreadsheet.worksheet.side_effect = Exception("Worksheet 'cuentas' not found")

    # CSV de respaldo
    csv_cuentas = tmp_path / "cuentas.csv"
    csv_metricas = tmp_path / "metricas.csv"

    pd.DataFrame(columns=["id_cuenta", "entidad", "plataforma", "usuario_red"]).to_csv(
        csv_cuentas, index=False
    )
    pd.DataFrame(
        columns=[
            "id_cuenta",
            "fecha",
            "seguidores",
            "alcance",
            "interacciones",
            "likes_promedio",
            "engagement_rate",
        ]
    ).to_csv(csv_metricas, index=False)

    with (
        patch("utils.data_manager.conectar_sheets", return_value=mock_spreadsheet),
        patch("utils.data_manager.CUENTAS_CSV", csv_cuentas),
        patch("utils.data_manager.METRICAS_CSV", csv_metricas),
        patch("utils.data_manager.DATA_DIR", tmp_path),
        patch("streamlit.warning"),
    ):
        # ACT
        df_cuentas, df_metricas = load_data()

        # ASSERT
        # Debe cargar desde CSV sin crashear
        assert isinstance(df_cuentas, pd.DataFrame)
        assert isinstance(df_metricas, pd.DataFrame)


@pytest.mark.integration
def test_guardar_datos_falla_al_leer_columnas(mock_conectar_sheets, tmp_path):
    """
    TEST: guardar_datos() maneja error al procesar columnas de DataFrame

    OBJETIVO: Cubrir líneas 323-374 (try-except en guardar_datos)
    """
    # ARRANGE: DataFrame con columnas incorrectas
    df_malo = pd.DataFrame({"columna_invalida": ["test"]})

    with (
        patch("utils.data_manager.load_data", side_effect=Exception("Load error")),
        patch("streamlit.error") as mock_error,
    ):
        # ACT
        resultado = guardar_datos(df_malo)

        # ASSERT
        assert resultado is False, "Debe retornar False cuando falla"
        assert mock_error.called, "Debe registrar error"


@pytest.mark.integration
def test_guardar_datos_worksheet_append_falla(mock_conectar_sheets):
    """
    TEST: guardar_datos() maneja error en worksheet.append_rows()

    OBJETIVO: Cubrir líneas 330-333, 361-365 (errores en append_rows)
    """
    # ARRANGE
    df_test = pd.DataFrame(
        {
            "id_cuenta": ["append_test"],
            "entidad": ["Append Test"],
            "plataforma": ["Facebook"],
            "usuario_red": ["@append"],
            "fecha": [datetime.now()],
            "seguidores": [1500],
            "alcance": [7500],
            "interacciones": [300],
            "likes_promedio": [60.0],
            "engagement_rate": [20.0],
        }
    )

    # Mock spreadsheet donde append_rows falla
    mock_spreadsheet = MagicMock()
    mock_ws = MagicMock()
    mock_ws.append_rows.side_effect = Exception("append_rows API error")
    mock_spreadsheet.worksheet.return_value = mock_ws

    def fake_load():
        return (
            pd.DataFrame(columns=["id_cuenta", "entidad", "plataforma", "usuario_red"]),
            pd.DataFrame(
                columns=["id_cuenta", "fecha", "seguidores", "alcance", "interacciones"]
            ),
        )

    with (
        patch("utils.data_manager.conectar_sheets", return_value=mock_spreadsheet),
        patch("utils.data_manager.load_data", fake_load),
        patch("streamlit.error") as mock_error,
    ):
        # ACT
        resultado = guardar_datos(df_test)

        # ASSERT
        assert resultado is False, "Debe retornar False cuando append falla"
        # Error fue logueado
        assert mock_error.called


@pytest.mark.integration
def test_save_batch_con_csv_metricas_faltante(tmp_path):
    """
    TEST: save_batch() crea archivo CSV si no existe

    OBJETIVO: Cubrir líneas 413-458 (path cuando CSV no existe)
    """
    # ARRANGE - Mockear directamente los archivos CSV con patch
    csv_cuentas = tmp_path / "cuentas.csv"
    csv_metricas = tmp_path / "metricas_nuevo.csv"

    # Crear CSV de cuentas inicial vacío
    pd.DataFrame(columns=["id_cuenta", "entidad", "plataforma", "usuario_red"]).to_csv(
        csv_cuentas, index=False
    )

    datos = [
        {
            "id_cuenta": "test123",
            "entidad": "Test Entity",
            "plataforma": "LinkedIn",
            "usuario_red": "@test",
            "fecha": "2024-07-01",
            "seguidores": 500,
            "alcance": 2000,
            "interacciones": 100,
            "likes_promedio": 20,
        }
    ]

    with (
        patch("utils.data_manager.CUENTAS_CSV", csv_cuentas),
        patch("utils.data_manager.METRICAS_CSV", csv_metricas),
        patch("utils.data_manager.conectar_sheets", return_value=None),
        patch("streamlit.cache_data.clear"),
        patch("streamlit.warning"),
    ):
        # ACT
        save_batch(datos)

        # ASSERT - Verificar que CSV se creó
        assert csv_metricas.exists(), "Debe crear CSV de métricas cuando no existe"


@pytest.mark.integration
def test_save_batch_con_error_guardar_cuentas_csv(tmp_path):
    """
    TEST: save_batch() maneja error al guardar cuentas en CSV

    OBJETIVO: Cubrir líneas 437-447 (try-except al guardar cuentas CSV)
    """
    # ARRANGE
    csv_cuentas = tmp_path / "cuentas_readonly.csv"
    csv_metricas = tmp_path / "metricas.csv"

    datos = [
        {
            "id_cuenta": "error_cuenta",
            "entidad": "Error Entity",
            "plataforma": "TikTok",
            "usuario_red": "@error",
            "fecha": "2024-08-01",
            "seguidores": 600,
            "alcance": 3000,
            "interacciones": 120,
            "likes_promedio": 24,
        }
    ]

    def fake_load():
        return (
            pd.DataFrame(columns=["id_cuenta", "entidad", "plataforma", "usuario_red"]),
            pd.DataFrame(
                columns=[
                    "id_cuenta",
                    "fecha",
                    "seguidores",
                    "alcance",
                    "interacciones",
                    "likes_promedio",
                    "engagement_rate",
                ]
            ),
        )

    with (
        patch("utils.data_manager.load_data", fake_load),
        patch("utils.data_manager.guardar_datos"),
        patch("utils.data_manager.CUENTAS_CSV", csv_cuentas),
        patch("utils.data_manager.METRICAS_CSV", csv_metricas),
        patch("pandas.DataFrame.to_csv", side_effect=Exception("CSV write error")),
        patch("streamlit.cache_data.clear"),
        patch("streamlit.warning"),
    ):
        # ACT & ASSERT
        # No debe crashear, debe manejar el error
        try:
            save_batch(datos)
            assert True, "Debe manejar error en to_csv sin crashear"
        except Exception:
            pytest.fail("save_batch() debe manejar errores de CSV internamente")


@pytest.mark.integration
def test_get_id_con_columnas_faltantes_en_dataframe():
    """
    TEST: get_id() maneja DataFrame sin columnas 'entidad' o 'plataforma'

    OBJETIVO: Cubrir líneas 488-490 (manejo de columnas faltantes)
    """
    # ARRANGE: DataFrame sin columnas esperadas
    df_incompleto = pd.DataFrame(
        {
            "id_cuenta": ["test123"],
            "usuario_red": ["@test"],
            # Faltan 'entidad' y 'plataforma'
        }
    )

    # ACT
    resultado = get_id(
        "Nueva Entidad", "Instagram", "@nueva", df_cuentas_cache=df_incompleto
    )

    # ASSERT
    assert isinstance(resultado, str)
    assert len(resultado) == 32  # MD5 hash
    assert resultado == resultado.lower()  # Normalizado


@pytest.mark.integration
def test_get_id_encuentra_cuenta_existente_case_insensitive():
    """
    TEST: get_id() encuentra cuenta existente (case-insensitive)

    OBJETIVO: Cubrir líneas 497-499 (búsqueda case-insensitive y retorno de ID)
    """
    # ARRANGE: DataFrame con cuenta existente
    df_cuentas = pd.DataFrame(
        {
            "id_cuenta": ["existing123"],
            "entidad": ["TEST ENTITY"],
            "plataforma": ["FACEBOOK"],
            "usuario_red": ["@test"],
        }
    )

    # ACT: Buscar con diferentes mayúsculas/minúsculas
    resultado = get_id("test entity", "facebook", "@test", df_cuentas_cache=df_cuentas)

    # ASSERT
    assert (
        resultado == "existing123"
    ), "Debe encontrar cuenta existente (case-insensitive)"


@pytest.mark.integration
def test_reset_db_worksheet_clear_falla():
    """
    TEST: reset_db() maneja error cuando worksheet.clear() falla

    OBJETIVO: Cubrir líneas 539-540 (error en clear)
    """
    # ARRANGE
    mock_spreadsheet = MagicMock()
    mock_ws = MagicMock()
    mock_ws.clear.side_effect = Exception("clear() API error")
    mock_spreadsheet.worksheet.return_value = mock_ws

    with (
        patch("utils.data_manager.conectar_sheets", return_value=mock_spreadsheet),
        patch("streamlit.error"),
        patch("streamlit.success"),
    ):
        # ACT & ASSERT
        try:
            reset_db()
            assert True, "Debe manejar error en clear()"
        except Exception:
            pytest.fail("reset_db() no debe lanzar excepciones")


@pytest.mark.integration
def test_reset_db_worksheet_append_row_falla():
    """
    TEST: reset_db() maneja error cuando worksheet.append_row() falla

    OBJETIVO: Cubrir líneas 549-552 (error en append_row)
    """
    # ARRANGE
    mock_spreadsheet = MagicMock()
    mock_ws = MagicMock()
    mock_ws.clear.return_value = None  # clear funciona
    mock_ws.append_row.side_effect = Exception("append_row API error")
    mock_spreadsheet.worksheet.return_value = mock_ws

    with (
        patch("utils.data_manager.conectar_sheets", return_value=mock_spreadsheet),
        patch("streamlit.error"),
        patch("streamlit.success"),
    ):
        # ACT & ASSERT
        try:
            reset_db()
            assert True, "Debe manejar error en append_row()"
        except Exception:
            pytest.fail("reset_db() no debe lanzar excepciones")

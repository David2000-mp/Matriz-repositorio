"""
========================================
TESTS DE LOGGING Y MANEJO DE ERRORES
========================================

Tests específicos para cubrir las líneas de manejo de excepciones
que actualmente tienen baja cobertura en data_manager.py.

Objetivo: Aumentar cobertura de 71% a 80%+
"""

import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime

from utils.data_manager import (
    conectar_sheets,
    load_data,
    guardar_datos,
    save_batch,
    get_id,
    reset_db
)


# ========================================
# TESTS DE LOGGING EN conectar_sheets()
# ========================================

@pytest.mark.unit
def test_conectar_sheets_fallo_credenciales_llama_logger(mock_logger):
    """
    TEST: conectar_sheets() loguea error cuando faltan credenciales
    
    OBJETIVO: Verificar que logger.error() se llama cuando no hay secrets
    """
    
    # ARRANGE: Mock de st.secrets vacío
    fake_empty_secrets = {}
    def test_conectar_sheets_fallo_credenciales_llama_logger():
    mock_secrets.__contains__ = lambda self, key: key in fake_empty_secrets
    
    with patch('streamlit.secrets', mock_secrets), \
         patch('streamlit.error'):
        
        # ACT
        resultado = conectar_sheets()
        
        # ASSERT
        assert resultado is None, "Debe devolver None si no hay credenciales"
        
        with patch('utils.data_manager.logger') as mock_logger:
            with patch('streamlit.secrets', mock_secrets), \
                 patch('streamlit.error'):
                # ACT
                resultado = conectar_sheets()
                # ASSERT
                assert resultado is None, "Debe devolver None si no hay credenciales"
                assert mock_logger.error.called, "logger.error() debe ser llamado"
                call_args = str(mock_logger.error.call_args)
                assert "credenciales" in call_args.lower() or "secrets" in call_args.lower()
    
    # ARRANGE: Mock que lanza excepción
    def test_conectar_sheets_fallo_conexion_loguea_excepcion():
        "gcp_service_account": {
            "type": "service_account",
            "project_id": "test",
            "private_key": "-----BEGIN PRIVATE KEY-----\nTEST\n-----END PRIVATE KEY-----\n"
        }
    }
    mock_secrets = MagicMock()
    mock_secrets.__contains__ = lambda self, key: key in fake_secrets
    mock_secrets.__getitem__ = lambda self, key: fake_secrets[key]
    
def test_conectar_sheets_fallo_credenciales_llama_logger():
         patch('streamlit.error'), \
         patch('gspread.authorize') as mock_authorize:
        
        # Simular que authorize lanza excepción
        mock_authorize.side_effect = Exception("API Error")
        
        with patch('utils.data_manager.logger') as mock_logger:
            with patch('streamlit.error'), \
                 patch('gspread.authorize') as mock_authorize:
                # Simular que authorize lanza excepción
                mock_authorize.side_effect = Exception("API Error")
                # ACT
                resultado = conectar_sheets()
                # ASSERT
                assert resultado is None, "Debe devolver None si no hay credenciales"
                assert mock_logger.error.called, "logger.error() debe ser llamado"
                args, _ = mock_logger.error.call_args
                assert "No se encontraron credenciales" in args[0]
    TEST: load_data() maneja fallo de conexión gracefully y loguea
    
    def test_load_data_fallo_conexion_retorna_dataframes_vacios_y_loguea():
    """
    
    # ARRANGE: Mock que devuelve None (conexión fallida)
    with patch('utils.data_manager.conectar_sheets', return_value=None):
        
        # ACT
        df_cuentas, df_metricas = load_data()
        
        # ASSERT
        # Debe devolver DataFrames vacíos pero con columnas correctas
        assert isinstance(df_cuentas, pd.DataFrame)
        assert isinstance(df_metricas, pd.DataFrame)
        assert 'id_cuenta' in df_cuentas.columns
        assert 'id_cuenta' in df_metricas.columns
    with patch('utils.data_manager.logger') as mock_logger:
        with patch('streamlit.secrets', {"gcp_service_account": {}}):
            with patch('gspread.authorize', side_effect=Exception("Connection timeout")):
                with patch('streamlit.error'):
        with patch('utils.data_manager.logger') as mock_logger:
            with patch('streamlit.secrets', {"gcp_service_account": {}}):
                with patch('gspread.authorize', side_effect=Exception("Connection timeout")):
                    with patch('streamlit.error'):
    mock_spreadsheet.worksheet.side_effect = Exception("Sheet not found")
    
    # Crear CSVs vacíos temporales para el fallback
    with patch('utils.data_manager.conectar_sheets', return_value=mock_spreadsheet), \
         patch('utils.data_manager.CUENTAS_CSV', tmp_path / 'cuentas.csv'), \
         patch('utils.data_manager.METRICAS_CSV', tmp_path / 'metricas.csv'), \
def test_load_data_fallo_conexion_retorna_dataframes_vacios_y_loguea():
        
        # ACT
        df_cuentas, df_metricas = load_data()
        
        # ASSERT
        # Verificar que logger.error() fue llamado
        assert mock_logger.error.called, "logger.error() debe ser llamado cuando falla worksheet"


@pytest.mark.unit
def test_load_data_columnas_faltantes_loguea_error(mock_logger):
    """
    TEST: load_data() loguea error cuando faltan columnas en métricas
    
    OBJETIVO: Cubrir líneas 207-214 (validación de columnas)
    """
    
    # ARRANGE: Mock de worksheet con columnas incompletas
    mock_spreadsheet = MagicMock()
    
def test_load_data_error_al_leer_hoja_loguea_excepcion():
    mock_ws_cuentas = MagicMock()
    mock_ws_cuentas.get_all_records.return_value = [
        {"id_cuenta": "test1", "entidad": "Test", "plataforma": "Facebook", "usuario_red": "@test"}
    ]
    
    # Hoja métricas SIN columnas requeridas (solo tiene id_cuenta y fecha)
    mock_ws_metricas = MagicMock()
    mock_ws_metricas.get_all_records.return_value = [
        {"id_cuenta": "test1", "fecha": "2024-01-01"}  # Faltan: seguidores, alcance, etc.
    ]
    
    mock_spreadsheet.worksheet.side_effect = lambda name: {
        'cuentas': mock_ws_cuentas,
        'metricas': mock_ws_metricas
    }.get(name)
    
    with patch('utils.data_manager.conectar_sheets', return_value=mock_spreadsheet), \
         patch('streamlit.error') as mock_st_error:
        
        # ACT
        df_cuentas, df_metricas = load_data()
        assert mock_logger.error.called
        assert any("Error leyendo hoja" in str(call) for call in mock_logger.error.call_args_list)
        # ASSERT
        # El st.error debe haber sido llamado con mensaje de columnas faltantes
def test_load_data_error_429_quota_excedida_loguea_warning():


@pytest.mark.unit
def test_load_data_error_429_quota_excedida_loguea_warning(mock_logger, tmp_path):
    """
    TEST: load_data() loguea warning cuando se excede quota de Google API
    
    OBJETIVO: Cubrir líneas 247-248 (manejo de error 429)
    """
    
    # ARRANGE: Mock que lanza excepción con código 429
    mock_spreadsheet = MagicMock()
    
    # Simular error 429 (quota exceeded)
    error_429 = Exception("429: Quota exceeded")
    mock_spreadsheet.worksheet.side_effect = error_429
    
    # Crear CSVs vacíos temporales para el fallback
    with patch('utils.data_manager.conectar_sheets', return_value=mock_spreadsheet), \
         patch('streamlit.error'), \
         patch('streamlit.warning'), \
         patch('utils.data_manager.CUENTAS_CSV', tmp_path / 'cuentas.csv'), \
         patch('utils.data_manager.METRICAS_CSV', tmp_path / 'metricas.csv'), \
         patch('utils.data_manager.DATA_DIR', tmp_path):
def test_guardar_datos_fallo_conexion_retorna_none_y_loguea():
        # ACT
        df_cuentas, df_metricas = load_data()
        
        # ASSERT
        # Verificar que logger.warning() fue llamado
        assert mock_logger.warning.called, "logger.warning() debe ser llamado para error 429"


# ========================================
# TESTS DE LOGGING EN guardar_datos()
# ========================================

@pytest.mark.unit
def test_guardar_datos_fallo_conexion_retorna_none_y_loguea(mock_logger, sample_cuentas_df):
    """
    TEST: guardar_datos() retorna None y loguea cuando falla conexión
    
    OBJETIVO: Cubrir líneas 368-370 (manejo de excepción en guardar_datos)
    """
    
    # ARRANGE: DataFrame de prueba
    nuevo_df = pd.DataFrame({
        'id_cuenta': ['test123'],
        'entidad': ['Test'],
        'plataforma': ['Facebook'],
        'usuario_red': ['@test'],
        'fecha': [pd.Timestamp('2024-01-01')],
        'seguidores': [1000],
        'alcance': [3000],
        'interacciones': [100],
        'likes_promedio': [25.0],
        'engagement_rate': [10.0]
    })
    
    # Mock que lanza excepción
    with patch('utils.data_manager.conectar_sheets', return_value=None), \
         patch('streamlit.error'):
        
        # ACT
        resultado = guardar_datos(nuevo_df)
        
        # ASSERT
        # guardar_datos() retorna None cuando falla, no False
        assert resultado is None, "Debe devolver None cuando no hay spreadsheet"
        
        # Verificar que logger.error() fue llamado
        assert mock_logger.error.called, "logger.error() debe ser llamado"


@pytest.mark.unit
def test_guardar_datos_excepcion_al_actualizar_cuentas_loguea(
    mock_logger,
    mock_conectar_sheets,
    sample_cuentas_df,
    sample_metricas_df
):
    """
    TEST: guardar_datos() loguea error cuando falla update de cuentas
    
    OBJETIVO: Cubrir líneas 325-326 (error al actualizar hoja cuentas)
    """
    
    # ARRANGE: DataFrame con cuenta nueva
    nuevo_df = pd.DataFrame({
        'id_cuenta': ['nuevacuenta123'],
        'entidad': ['Nueva Entidad'],
        'plataforma': ['Instagram'],
        'usuario_red': ['@nueva'],
        'fecha': [pd.Timestamp('2024-01-01')],
        'seguidores': [5000],
        'alcance': [15000],
        'interacciones': [500],
        'likes_promedio': [100.0],
        'engagement_rate': [10.0]
    })
    
    # Mock de load_data
    def fake_load_data():
        return sample_cuentas_df, sample_metricas_df
    
    # Mock de spreadsheet que lanza error en append_rows
    mock_spreadsheet = MagicMock()
    mock_ws = MagicMock()
    mock_ws.append_rows.side_effect = Exception("API Error al actualizar")
    mock_spreadsheet.worksheet.return_value = mock_ws
    
    with patch('utils.data_manager.load_data', fake_load_data), \
         patch('utils.data_manager.conectar_sheets', return_value=mock_spreadsheet), \
         patch('streamlit.error'):
        
        # ACT
        resultado = guardar_datos(nuevo_df)
        
        # ASSERT
        # Puede devolver False por el error
        # Lo importante es que se logueó
        assert mock_logger.error.called


@pytest.mark.unit
def test_guardar_datos_excepcion_al_actualizar_metricas_loguea(
    mock_logger,
    mock_conectar_sheets,
    sample_cuentas_df,
    sample_metricas_df
):
    """
    TEST: guardar_datos() loguea error cuando falla update de métricas
    
    OBJETIVO: Cubrir líneas 356-361 (error al actualizar hoja métricas)
    """
    
    # ARRANGE: DataFrame con métricas de cuenta existente pero fecha nueva
    nuevo_df = pd.DataFrame({
        'id_cuenta': ['abc123def456'],  # Cuenta que ya existe en sample_cuentas_df
        'entidad': ['Centro Universitario México'],
        'plataforma': ['Facebook'],
        'usuario_red': ['@centrounivmx'],
        'fecha': [pd.Timestamp('2025-01-01')],  # Fecha nueva
        'seguidores': [9999],
        'alcance': [30000],
        'interacciones': [1000],
        'likes_promedio': [200.0],
        'engagement_rate': [10.05]
    })
    
    # Mock de load_data
    def fake_load_data():
        return sample_cuentas_df, sample_metricas_df
    
    # Mock de spreadsheet
    mock_spreadsheet = MagicMock()
    
    # ws_cuentas funciona OK (no hay cuentas nuevas)
    mock_ws_cuentas = MagicMock()
    
    # ws_metricas lanza error
    mock_ws_metricas = MagicMock()
    mock_ws_metricas.append_rows.side_effect = Exception("API Error al agregar métricas")
    
    mock_spreadsheet.worksheet.side_effect = lambda name: {
        'cuentas': mock_ws_cuentas,
        'metricas': mock_ws_metricas
    }.get(name)
    
    with patch('utils.data_manager.load_data', fake_load_data), \
         patch('utils.data_manager.conectar_sheets', return_value=mock_spreadsheet), \
         patch('streamlit.error'):
        
        # ACT
        resultado = guardar_datos(nuevo_df)
        
        # ASSERT
        assert mock_logger.error.called


# ========================================
# TESTS DE LOGGING EN save_batch()
# ========================================

@pytest.mark.unit
def test_save_batch_loguea_informacion_de_procesamiento(
    mock_logger,
    mock_conectar_sheets,
    sample_cuentas_df,
    sample_metricas_df
):
    """
    TEST: save_batch() loguea información sobre el procesamiento
    
    OBJETIVO: Cubrir línea 386 (logger.info en save_batch)
    """
    
    # ARRANGE
    datos = [{
        'id_cuenta': 'test123',
        'entidad': 'Test Entity',
        'plataforma': 'Facebook',
        'usuario_red': '@test',
        'fecha': '2024-02-01',
        'seguidores': 1000,
        'alcance': 5000,
        'interacciones': 150,
        'likes_promedio': 50
    }]
    
    def fake_load_data():
        return sample_cuentas_df, sample_metricas_df
    
    def fake_guardar_datos(df, modo='completo'):
        return True
    
    with patch('utils.data_manager.load_data', fake_load_data), \
         patch('utils.data_manager.guardar_datos', fake_guardar_datos):
        
        # ACT
        save_batch(datos)
        
        # ASSERT
        # Verificar que logger.info() fue llamado
        assert mock_logger.info.called


# ========================================
# TESTS DE FUNCIONES AUXILIARES
# ========================================

@pytest.mark.unit
def test_reset_db_limpia_cache_sin_errores(mock_logger):
    """
    TEST: reset_db() ejecuta sin errores
    
    OBJETIVO: Verificar que reset_db() funciona correctamente
    """
    
    # ACT & ASSERT
    try:
        reset_db()
        assert True
    except Exception as e:
        pytest.fail(f"reset_db() no debe lanzar excepciones: {e}")


# ========================================
# TESTS DE COBERTURA DE LÍNEAS ESPECÍFICAS
# ========================================

@pytest.mark.unit
def test_get_id_con_df_cache_none_usa_load_data(mock_logger, mock_conectar_sheets):
    """
    TEST: get_id() llama a load_data() cuando df_cuentas_cache es None
    
    OBJETIVO: Cubrir líneas 471-479 (carga de df_cuentas si no se provee)
    """
    
    # ARRANGE
    with patch('utils.data_manager.load_data') as mock_load:
        # Mock que devuelve DataFrames vacíos
        mock_load.return_value = (
            pd.DataFrame(columns=['id_cuenta', 'entidad', 'plataforma', 'usuario_red']),
            pd.DataFrame(columns=['id_cuenta', 'fecha', 'seguidores'])
        )
        
        # ACT
        resultado = get_id("Test Entity", "Facebook", "@test", df_cuentas_cache=None)
        
        # ASSERT
        # Verificar que load_data() fue llamado
        assert mock_load.called
        
        # El resultado debe ser un string (nuevo ID generado)
        assert isinstance(resultado, str)
        assert len(resultado) > 0


@pytest.mark.unit
def test_load_data_convierte_fechas_invalidas_a_nat_y_elimina(mock_logger, mock_conectar_sheets):
    """
    TEST: load_data() maneja fechas inválidas correctamente
    
    OBJETIVO: Cubrir líneas 207-210 (conversión de fechas y limpieza de NaT)
    """
    
    # ARRANGE: Mock con fechas inválidas
    mock_spreadsheet = MagicMock()
    
    mock_ws_cuentas = MagicMock()
    mock_ws_cuentas.get_all_records.return_value = [
        {"id_cuenta": "test1", "entidad": "Test", "plataforma": "Facebook", "usuario_red": "@test"}
    ]
    
    mock_ws_metricas = MagicMock()
    mock_ws_metricas.get_all_records.return_value = [
        {
            "id_cuenta": "test1",
            "fecha": "FECHA_INVALIDA",  # Esto generará NaT al parsear
            "seguidores": "1000",
            "alcance": "3000",
            "interacciones": "100",
            "likes_promedio": "25",
            "engagement_rate": "10"
        }
    ]
    
    mock_spreadsheet.worksheet.side_effect = lambda name: {
        'cuentas': mock_ws_cuentas,
        'metricas': mock_ws_metricas
    }.get(name)
    
    with patch('utils.data_manager.conectar_sheets', return_value=mock_spreadsheet):
        
        # ACT
        df_cuentas, df_metricas = load_data()
        
        # ASSERT
        # Las filas con fechas inválidas deben haberse eliminado
        assert len(df_metricas) == 0, "Filas con fechas inválidas deben eliminarse"

"""
========================================
PYTEST CONFIGURATION & FIXTURES
========================================

Este archivo contiene fixtures que se ejecutan ANTES de cada test.
Los fixtures "engañan" a tu código para que no conecte a APIs reales.

CONCEPTOS CLAVE:
1. Fixture: Función que prepara el entorno para tests
2. Mock: Objeto falso que simula el comportamiento de uno real
3. Monkeypatch: Reemplaza temporalmente funciones/objetos

¿CÓMO FUNCIONA EL MOCKING?
--------------------------
Tu código hace:  conectar_sheets() → Google Sheets API → DataFrame real
El mock hace:    conectar_sheets() → Mock Object → DataFrame de prueba

Tu código NO SABE que está usando un mock. Es transparente.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock, patch
from typing import Any, Dict, Tuple


# ========================================
# FIXTURE 1: MOCK DE STREAMLIT SECRETS
# ========================================

@pytest.fixture
def mock_streamlit_secrets(monkeypatch):
    """
    Simula st.secrets para que los tests no necesiten secrets.toml
    
    ¿Cómo funciona?
    ---------------
    1. Tu código hace: st.secrets["gcp_service_account"]["project_id"]
    2. Este mock intercepta esa llamada
    3. Devuelve valores falsos (pero válidos en estructura)
    
    ¿Por qué es importante?
    -----------------------
    - Tests no dependen de archivo secrets.toml (puede no existir en CI/CD)
    - Tests no usan credenciales reales (seguridad)
    - Tests son reproducibles en cualquier máquina
    """
    
    # Crear estructura de secrets falsa
    fake_secrets = {
        "gcp_service_account": {
            "type": "service_account",
            "project_id": "test-project-id",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\nTEST_KEY\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "123456789",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test",
            "universe_domain": "googleapis.com"
        }
    }
    
    # Crear mock de streamlit.secrets que se comporta como un diccionario
    mock_secrets = MagicMock()
    mock_secrets.__getitem__ = lambda self, key: fake_secrets[key]
    mock_secrets.__contains__ = lambda self, key: key in fake_secrets
    mock_secrets.get = lambda key, default=None: fake_secrets.get(key, default)
    
    # CRUCIAL: Reemplazar st.secrets en TODO el código
    # Usa monkeypatch para que el cambio solo dure durante el test
    monkeypatch.setattr("streamlit.secrets", mock_secrets)
    
    return mock_secrets


# ========================================
# FIXTURE 2: DATOS DE PRUEBA (FAKE DATA)
# ========================================

@pytest.fixture
def sample_cuentas_df() -> pd.DataFrame:
    """
    DataFrame de prueba que simula la hoja 'cuentas' de Google Sheets
    
    COLUMNAS REALES DE TU API:
    - id_cuenta (str, lowercase, normalized)
    - entidad (str)
    - plataforma (str)
    - usuario_red (str)
    
    ¿Por qué crear datos falsos?
    -----------------------------
    - Tests deben ser predecibles (siempre los mismos datos)
    - Tests deben ser rápidos (sin llamadas a API)
    - Tests deben funcionar offline
    """
    return pd.DataFrame({
        'id_cuenta': ['abc123def456', 'xyz789ghi012', 'jkl345mno678'],
        'entidad': ['Centro Universitario México', 'Colegio Jacona', 'Instituto Potosino'],
        'plataforma': ['Facebook', 'Instagram', 'TikTok'],
        'usuario_red': ['@centrounivmx', '@colegiojacona', '@institutopotosino']
    })


@pytest.fixture
def sample_metricas_df() -> pd.DataFrame:
    """
    DataFrame de prueba que simula la hoja 'metricas' de Google Sheets
    
    COLUMNAS REALES DE TU API:
    - id_cuenta (str, FK a cuentas)
    - fecha (datetime)
    - seguidores (int)
    - alcance (int)
    - interacciones (int)
    - likes_promedio (float)
    - engagement_rate (float)
    """
    return pd.DataFrame({
        'id_cuenta': ['abc123def456', 'xyz789ghi012', 'jkl345mno678'],
        'fecha': pd.to_datetime(['2024-01-15', '2024-01-16', '2024-01-17']),
        'seguidores': [1000, 2000, 3000],
        'alcance': [5000, 8000, 12000],
        'interacciones': [150, 300, 450],
        'likes_promedio': [50.0, 100.0, 150.0],
        'engagement_rate': [15.0, 15.0, 15.0]
    })


# ========================================
# FIXTURE 3: MOCK DE GOOGLE SHEETS
# ========================================

@pytest.fixture
def mock_gspread_client(sample_cuentas_df, sample_metricas_df):
    """
    Mock completo de gspread (librería de Google Sheets)
    
    ¿Cómo funciona este mock?
    --------------------------
    Tu código hace:
        1. client = gspread.authorize(creds)
        2. spreadsheet = client.open("BaseDatosMatriz")
        3. sheet = spreadsheet.worksheet("cuentas")
        4. data = sheet.get_all_records()
    
    Este mock intercepta CADA paso y devuelve objetos falsos:
        1. client → Mock object
        2. spreadsheet → Mock object
        3. sheet → Mock object con método get_all_records()
        4. data → Lista de diccionarios (convertida desde DataFrame)
    
    Tu código NO SABE que está usando mocks. Cree que habló con Google.
    """
    
    # Crear mock del worksheet (hoja individual)
    mock_sheet_cuentas = MagicMock()
    mock_sheet_cuentas.get_all_records.return_value = sample_cuentas_df.to_dict('records')
    mock_sheet_cuentas.title = "cuentas"
    
    mock_sheet_metricas = MagicMock()
    mock_sheet_metricas.get_all_records.return_value = sample_metricas_df.to_dict('records')
    mock_sheet_metricas.title = "metricas"
    
    # Crear mock del spreadsheet (archivo completo)
    mock_spreadsheet = MagicMock()
    mock_spreadsheet.worksheet.side_effect = lambda name: {
        "cuentas": mock_sheet_cuentas,
        "metricas": mock_sheet_metricas
    }[name]
    mock_spreadsheet.title = "BaseDatosMatriz"
    
    # Crear mock del cliente gspread
    mock_client = MagicMock()
    mock_client.open.return_value = mock_spreadsheet
    
    return mock_client, mock_sheet_cuentas, mock_sheet_metricas


@pytest.fixture
def mock_conectar_sheets(mock_gspread_client, monkeypatch):
    """
    Reemplaza la función conectar_sheets() completa
    
    ¿Por qué este fixture?
    ----------------------
    Tu función conectar_sheets() devuelve SOLO el spreadsheet object:
        return spreadsheet  # (no tupla)
    
    En lugar de mockear cada paso, este fixture reemplaza
    TODA la función conectar_sheets() con una versión falsa
    que devuelve el mock del spreadsheet directamente.
    
    ¿Cómo usarlo en tests?
    ----------------------
    def test_algo(mock_conectar_sheets):
        # Tu código que llama conectar_sheets()
        # Automáticamente usará el mock
        from utils.data_manager import load_data
        df1, df2 = load_data()  # ← Usa mock, no API real
    """
    
    mock_client, mock_cuentas, mock_metricas = mock_gspread_client
    mock_spreadsheet = mock_client.open.return_value
    
    def fake_conectar_sheets():
        """Función falsa que reemplaza conectar_sheets()"""
        # Tu función real devuelve: Optional[gspread.Spreadsheet]
        return mock_spreadsheet
    
    # CRUCIAL: Reemplazar la función real con la falsa
    # Esto hace que CUALQUIER import de conectar_sheets use el mock
    monkeypatch.setattr(
        "utils.data_manager.conectar_sheets",
        fake_conectar_sheets
    )
    
    return fake_conectar_sheets


# ========================================
# FIXTURE 4: MOCK DE STREAMLIT CACHE
# ========================================

@pytest.fixture(autouse=True)
def disable_streamlit_cache(monkeypatch):
    """
    Desactiva @st.cache_resource y @st.cache_data
    
    ¿Por qué?
    ---------
    - El cache de Streamlit no funciona bien en tests
    - Queremos que cada test sea independiente (sin cache compartido)
    - Tests deben ser rápidos (sin overhead de cache)
    
    autouse=True: Se aplica automáticamente a TODOS los tests
    """
    
    # Clase mock que simula el módulo cache con método clear()
    class FakeCacheModule:
        @staticmethod
        def clear():
            """Mock de clear() - no hace nada en tests"""
            pass
        
        def __call__(self, *args, **kwargs):
            """Permite usar como decorador: @st.cache_data"""
            def decorator(func):
                return func  # Devuelve función sin modificar
            
            # Si se llama con función directamente: @st.cache_data
            if len(args) == 1 and callable(args[0]):
                return args[0]
            # Si se llama con parámetros: @st.cache_data(ttl=300)
            return decorator
    
    # Reemplazar los decorators de Streamlit con objetos que tienen clear()
    monkeypatch.setattr("streamlit.cache_resource", FakeCacheModule())
    monkeypatch.setattr("streamlit.cache_data", FakeCacheModule())


# ========================================
# FIXTURE 5: MOCK DE LOGGER
# ========================================

@pytest.fixture
def mock_logger(monkeypatch):
    """
    Mock del sistema de logging para verificar llamadas en tests
    
    ¿Cómo funciona?
    ---------------
    1. Reemplaza el logger real por un MagicMock
    2. Permite verificar que logger.error() fue llamado
    3. Permite verificar los argumentos de las llamadas
    
    Uso:
    ----
    def test_fallo_conexion(mock_logger):
        # Tu código que hace logger.error("Error de conexión")
        
        # Verificar que se llamó error()
        assert mock_logger.error.called
        
        # Verificar el mensaje exacto
        mock_logger.error.assert_called_once_with("Error de conexión")
        
        # O verificar que contiene un substring
        call_args = mock_logger.error.call_args[0][0]
        assert "Error" in call_args
    """
    from unittest.mock import MagicMock
    
    # Crear mock del logger
    fake_logger = MagicMock()
    
    # Reemplazar get_logger para que devuelva nuestro mock
    def fake_get_logger(name):
        return fake_logger
    
    monkeypatch.setattr("utils.logger.get_logger", fake_get_logger)
    
    # También reemplazar en data_manager si ya fue importado
    monkeypatch.setattr("utils.data_manager.logger", fake_logger)
    
    return fake_logger


# ========================================
# FIXTURE 6: CAPTURA DE LOGS REALES
# ========================================

@pytest.fixture
def capture_logs(caplog):
    """
    Captura logs REALES durante tests para verificar mensajes
    
    Este fixture NO mockea el logger, solo captura su output.
    Úsalo cuando quieras verificar que el sistema de logging funciona correctamente.
    
    Uso:
    ----
    def test_algo(capture_logs):
        # Tu código que hace logger.error("Algo falló")
        assert "Algo falló" in capture_logs.text
    """
    import logging
    caplog.set_level(logging.DEBUG)
    return caplog


# ========================================
# FIXTURE 6: RESET DE ESTADO
# ========================================

@pytest.fixture(autouse=True)
def reset_state():
    """
    Limpia estado global antes/después de cada test
    
    ¿Por qué?
    ---------
    Tests deben ser independientes. Si un test modifica
    una variable global, el siguiente test podría fallar.
    """
    # Setup: antes del test
    yield  # ← Aquí se ejecuta el test
    
    # Teardown: después del test
    # Aquí podrías limpiar archivos temporales, cerrar conexiones, etc.
    pass


# ========================================
# HELPERS PARA TESTS
# ========================================

def assert_dataframe_equal(df1: pd.DataFrame, df2: pd.DataFrame, msg: str = ""):
    """
    Helper para comparar DataFrames en tests
    
    Uso:
    ----
    assert_dataframe_equal(df_esperado, df_resultado, "DataFrames no coinciden")
    """
    try:
        pd.testing.assert_frame_equal(df1, df2, check_dtype=False)
    except AssertionError as e:
        raise AssertionError(f"{msg}\n{e}")


# ========================================
# MARKERS PERSONALIZADOS
# ========================================

def pytest_configure(config):
    """
    Configura markers personalizados para pytest
    
    Uso:
    ----
    @pytest.mark.slow
    def test_algo_lento():
        pass
    
    # Correr solo tests rápidos:
    # pytest -m "not slow"
    """
    config.addinivalue_line(
        "markers", "unit: marca tests unitarios (rápidos, sin I/O)"
    )
    config.addinivalue_line(
        "markers", "integration: marca tests de integración (lentos, con I/O)"
    )
    config.addinivalue_line(
        "markers", "api: marca tests que llaman APIs externas (skip en CI)"
    )

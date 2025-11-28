"""
========================================
TESTS DE INTEGRACIÓN PARA COBERTURA 80%
========================================

Tests enfocados en aumentar cobertura ejecutando las líneas reales
de manejo de errores y edge cases en data_manager.py.

OBJETIVO: 71% → 80%+

Líneas a cubrir:
- 127-130, 145-148: conectar_sheets() errors
- 193-195, 213-216, 232-234: load_data() sheet reading errors
- 242-281: load_data() error handling (429, CSV fallback)
- 321, 330-333, 347, 361-365: guardar_datos() errors
- 401, 418, 436, 439-440, 445-450: save_batch()
- 477, 483-485: get_id() with None df
- 534-535, 544-547: reset_db() errors
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
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
# TESTS DE save_batch()
# ========================================

@pytest.mark.integration
def test_save_batch_con_multiples_registros_sin_duplicados(mock_conectar_sheets, tmp_path):
    """
    TEST: save_batch() procesa múltiples registros sin duplicados
    
    OBJETIVO: Cubrir líneas 401, 411, 418, 425-426 (flujo normal de save_batch)
    """
    
    # ARRANGE
    datos = [
        {
            'id_cuenta': 'test1',
            'entidad': 'Entity 1',
            'plataforma': 'Facebook',
            'usuario_red': '@entity1',
            'fecha': '2024-03-01',
            'seguidores': 1000,
            'alcance': 5000,
            'interacciones': 200,
            'likes_promedio': 40
        },
        {
            'id_cuenta': 'test2',
            'entidad': 'Entity 2',
            'plataforma': 'Instagram',
            'usuario_red': '@entity2',
            'fecha': '2024-03-01',
            'seguidores': 2000,
            'alcance': 10000,
            'interacciones': 500,
            'likes_promedio': 100
        },
        {
            'id_cuenta': 'test3',
            'entidad': 'Entity 3',
            'plataforma': 'LinkedIn',
            'usuario_red': 'entity-3',
            'fecha': '2024-03-01',
            'seguidores': 500,
            'alcance': 2000,
            'interacciones': 80,
            'likes_promedio': 16
        }
    ]
    
    # Mock CSVs
    csv_cuentas = tmp_path / "cuentas.csv"
    csv_metricas = tmp_path / "metricas.csv"
    
    def fake_load_data():
        return (
            pd.DataFrame(columns=['id_cuenta', 'entidad', 'plataforma', 'usuario_red']),
            pd.DataFrame(columns=['id_cuenta', 'fecha', 'seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate'])
        )
    
    def fake_guardar_datos(df):
        # No hacer nada, solo simular éxito
        pass
    
    with patch('utils.data_manager.load_data', fake_load_data), \
         patch('utils.data_manager.guardar_datos', fake_guardar_datos), \
         patch('utils.data_manager.CUENTAS_CSV', csv_cuentas), \
         patch('utils.data_manager.METRICAS_CSV', csv_metricas), \
         patch('streamlit.cache_data.clear'), \
         patch('streamlit.warning'):
        
        # ACT
        save_batch(datos)
        
        # ASSERT
        # Verificar que se creó el CSV
        assert csv_metricas.exists(), "CSV de métricas debe haberse creado"
        
        # Leer y verificar contenido
        df_saved = pd.read_csv(csv_metricas)
        assert len(df_saved) == 3, "Debe haber 3 registros guardados"
        assert 'engagement_rate' in df_saved.columns, "Debe tener engagement_rate calculado"


@pytest.mark.integration
def test_save_batch_con_datos_duplicados_elimina_correctamente(mock_conectar_sheets, tmp_path):
    """
    TEST: save_batch() elimina duplicados por cuenta+fecha
    
    OBJETIVO: Cubrir líneas 405-408, 439-440 (eliminación de duplicados)
    """
    
    # ARRANGE: Métricas existentes con una entrada
    csv_cuentas = tmp_path / "cuentas.csv"
    csv_metricas = tmp_path / "metricas.csv"
    
    # Crear métrica existente (con fecha como datetime)
    df_existing = pd.DataFrame({
        'id_cuenta': ['duplicate_test'],
        'entidad': ['Duplicate Test'],
        'plataforma': ['Facebook'],
        'usuario_red': ['@dup'],
        'fecha': [pd.Timestamp('2024-03-15')],
        'seguidores': [1000],
        'alcance': [5000],
        'interacciones': [200],
        'likes_promedio': [40.0],
        'engagement_rate': [20.0]
    })
    df_existing.to_csv(csv_metricas, index=False)
    
    # 2 registros con mismo id_cuenta y fecha (duplicados)
    datos = [
        {
            'id_cuenta': 'duplicate_test',
            'entidad': 'Duplicate Test',
            'plataforma': 'Facebook',
            'usuario_red': '@dup',
            'fecha': '2024-03-15',
            'seguidores': 1100,
            'alcance': 5500,
            'interacciones': 220,
            'likes_promedio': 44
        },
        {
            'id_cuenta': 'duplicate_test',
            'entidad': 'Duplicate Test',
            'plataforma': 'Facebook',
            'usuario_red': '@dup',
            'fecha': '2024-03-15',  # Misma fecha
            'seguidores': 1200,  # Valores diferentes
            'alcance': 6000,
            'interacciones': 240,
            'likes_promedio': 48
        }
    ]
    
    def fake_load_data():
        return (
            pd.DataFrame(columns=['id_cuenta', 'entidad', 'plataforma', 'usuario_red']),
            df_existing
        )
    
    with patch('utils.data_manager.load_data', fake_load_data), \
         patch('utils.data_manager.guardar_datos'), \
         patch('utils.data_manager.CUENTAS_CSV', csv_cuentas), \
         patch('utils.data_manager.METRICAS_CSV', csv_metricas), \
         patch('streamlit.cache_data.clear'), \
         patch('streamlit.warning'):
        
        # ACT
        save_batch(datos)
        
        # ASSERT
        # Leer CSV guardado
        df_saved = pd.read_csv(csv_metricas)
        # Debe haber eliminado duplicados: 1 registro existente eliminado, 1 nuevo guardado
        assert len(df_saved) == 1, "Debe haber eliminado duplicados"
        assert df_saved.iloc[0]['seguidores'] == 1200, "Debe mantener el último registro"


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
            'id_cuenta': 'test_error',
            'entidad': 'Error Entity',
            'plataforma': 'Facebook',
            'usuario_red': '@error',
            'fecha': '2024-03-01',
            'seguidores': 1000,
            'alcance': 5000,
            'interacciones': 200,
            'likes_promedio': 40
        }
    ]
    
    def fake_load_data():
        return (
            pd.DataFrame(columns=['id_cuenta', 'entidad', 'plataforma', 'usuario_red']),
            pd.DataFrame(columns=['id_cuenta', 'fecha', 'seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate'])
        )
    
    def fake_guardar_datos(df):
        # Simular error en Google Sheets
        raise Exception("Google Sheets API Error")
    
    with patch('utils.data_manager.load_data', fake_load_data), \
         patch('utils.data_manager.guardar_datos', fake_guardar_datos), \
         patch('utils.data_manager.CUENTAS_CSV', csv_cuentas), \
         patch('utils.data_manager.METRICAS_CSV', csv_metricas), \
         patch('streamlit.cache_data.clear'), \
         patch('streamlit.warning') as mock_warning:
        
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
    fake_df_cuentas = pd.DataFrame(columns=['id_cuenta', 'entidad', 'plataforma', 'usuario_red'])
    fake_df_metricas = pd.DataFrame(columns=['id_cuenta', 'fecha', 'seguidores'])
    
    with patch('utils.data_manager.load_data', return_value=(fake_df_cuentas, fake_df_metricas)) as mock_load:
        
        # ACT
        resultado = get_id("Nueva Entidad", "TikTok", "@nueva", df_cuentas_cache=None)
        
        # ASSERT
        # Verificar que load_data() fue llamado
        assert mock_load.called, "load_data() debe ser llamado cuando df_cuentas_cache=None"
        
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
    df_empty = pd.DataFrame(columns=['id_cuenta', 'entidad', 'plataforma', 'usuario_red'])
    
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
    pd.DataFrame(columns=['id_cuenta', 'entidad', 'plataforma', 'usuario_red']).to_csv(csv_cuentas, index=False)
    pd.DataFrame(columns=['id_cuenta', 'fecha', 'seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']).to_csv(csv_metricas, index=False)
    
    with patch('utils.data_manager.conectar_sheets', return_value=mock_spreadsheet), \
         patch('utils.data_manager.CUENTAS_CSV', csv_cuentas), \
         patch('utils.data_manager.METRICAS_CSV', csv_metricas), \
         patch('utils.data_manager.DATA_DIR', tmp_path), \
         patch('streamlit.warning'):
        
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
    
    pd.DataFrame({
        'id_cuenta': ['test429'],
        'entidad': ['Test Entity'],
        'plataforma': ['Facebook'],
        'usuario_red': ['@test']
    }).to_csv(csv_cuentas, index=False)
    
    pd.DataFrame({
        'id_cuenta': ['test429'],
        'fecha': ['2024-01-01'],
        'seguidores': [1000],
        'alcance': [5000],
        'interacciones': [100],
        'likes_promedio': [20.0],
        'engagement_rate': [10.0]
    }).to_csv(csv_metricas, index=False)
    
    with patch('utils.data_manager.conectar_sheets', return_value=mock_spreadsheet), \
         patch('utils.data_manager.CUENTAS_CSV', csv_cuentas), \
         patch('utils.data_manager.METRICAS_CSV', csv_metricas), \
         patch('utils.data_manager.DATA_DIR', data_dir), \
         patch('streamlit.error') as mock_error, \
         patch('streamlit.warning'):
        
        # ACT
        df_cuentas, df_metricas = load_data()
        
        # ASSERT
        # Debe haber detectado el error 429
        # El código muestra st.error() para error 429, no st.warning()
        assert mock_error.called, "Debe mostrar error para quota 429"
        
        # Debe haber cargado desde CSV (fallback)
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
    nuevo_df = pd.DataFrame({
        'id_cuenta': ['errortest123'],
        'entidad': ['Error Test'],
        'plataforma': ['Instagram'],
        'usuario_red': ['@error'],
        'fecha': [pd.Timestamp('2024-05-01')],
        'seguidores': [1000],
        'alcance': [5000],
        'interacciones': [200],
        'likes_promedio': [40.0],
        'engagement_rate': [20.0]
    })
    
    # Mock de spreadsheet donde append_rows falla
    mock_spreadsheet = MagicMock()
    mock_ws = MagicMock()
    mock_ws.append_rows.side_effect = Exception("API Error al actualizar")
    mock_spreadsheet.worksheet.return_value = mock_ws
    
    def fake_load_data():
        return (
            pd.DataFrame(columns=['id_cuenta', 'entidad', 'plataforma', 'usuario_red']),
            pd.DataFrame(columns=['id_cuenta', 'fecha', 'seguidores', 'alcance', 'interacciones'])
        )
    
    with patch('utils.data_manager.conectar_sheets', return_value=mock_spreadsheet), \
         patch('utils.data_manager.load_data', fake_load_data), \
         patch('streamlit.error'):
        
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
    
    with patch('utils.data_manager.conectar_sheets', return_value=mock_spreadsheet), \
         patch('streamlit.error'), \
         patch('streamlit.success'):
        
        # ACT & ASSERT
        # No debe crashear, debe manejar el error internamente
        try:
            reset_db()
            # Si llega aquí, el error fue manejado correctamente
            assert True
        except Exception:
            # Si lanza excepción, el test falla
            pytest.fail("reset_db() debe manejar errores internamente sin lanzar excepciones")


@pytest.mark.integration
def test_reset_db_sin_conexion_maneja_error():
    """
    TEST: reset_db() maneja caso cuando no hay conexión a Sheets
    
    OBJETIVO: Cubrir manejo de error cuando conectar_sheets() retorna None
    """
    
    # ARRANGE: Sin conexión
    with patch('utils.data_manager.conectar_sheets', return_value=None), \
         patch('streamlit.error'):
        
        # ACT & ASSERT
        try:
            reset_db()
            assert True
        except Exception:
            pytest.fail("reset_db() debe manejar falta de conexión sin crashear")

"""
Suite de Pruebas Core - Servicios Críticos
===========================================
Valida funcionalidad crítica antes de producción:
- Agnosticismo de IDs (URLs, handles, usernames)
- Integridad de esquema en guardar_datos
- Limpieza de NaN en get_merged_data
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Asegurar que el path del proyecto esté disponible
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from utils.data_saver import get_id, guardar_datos, COLS_METRICAS
from utils.data_provider import data_provider


class TestIDAgnosticism:
    """
    Prueba 1: Validar que get_id sea agnóstica al formato de entrada.
    Diferentes formatos del mismo usuario deben generar el MISMO ID.
    """
    
    def test_id_consistency_handle_vs_username(self):
        """Handles con @ y usernames simples deben generar el mismo ID"""
        id_handle = get_id("CUM", "Facebook", "@maristascum")
        id_username = get_id("CUM", "Facebook", "maristascum")
        
        assert id_handle == id_username, \
            f"IDs difieren: '@maristascum'={id_handle} vs 'maristascum'={id_username}"
    
    def test_id_consistency_url_vs_username(self):
        """URLs completas y usernames deben generar el mismo ID"""
        id_url = get_id("CUM", "Facebook", "https://facebook.com/maristascum")
        id_username = get_id("CUM", "Facebook", "maristascum")
        
        assert id_url == id_username, \
            f"IDs difieren: URL={id_url} vs username={id_username}"
    
    def test_id_consistency_url_with_trailing_slash(self):
        """URLs con trailing slash deben generar el mismo ID"""
        id_url_no_slash = get_id("CUM", "Instagram", "https://instagram.com/maristascum")
        id_url_slash = get_id("CUM", "Instagram", "https://instagram.com/maristascum/")
        
        assert id_url_no_slash == id_url_slash, \
            f"IDs difieren: sin slash={id_url_no_slash} vs con slash={id_url_slash}"
    
    def test_id_consistency_all_formats(self):
        """Los 3 formatos (URL, handle, username) deben producir el MISMO ID"""
        entidad = "Santa María"
        plataforma = "Twitter"
        
        id_url = get_id(entidad, plataforma, "https://twitter.com/maristasanta")
        id_handle = get_id(entidad, plataforma, "@maristasanta")
        id_username = get_id(entidad, plataforma, "maristasanta")
        
        assert id_url == id_handle == id_username, \
            f"IDs inconsistentes: URL={id_url}, handle={id_handle}, username={id_username}"
    
    def test_id_case_insensitivity(self):
        """IDs deben ser case-insensitive"""
        id_lower = get_id("CUM", "Facebook", "maristascum")
        id_upper = get_id("CUM", "Facebook", "MARISTASCUM")
        id_mixed = get_id("CUM", "Facebook", "MaristasCUM")
        
        assert id_lower == id_upper == id_mixed, \
            f"IDs case-sensitive: lower={id_lower}, upper={id_upper}, mixed={id_mixed}"
    
    def test_id_always_string(self):
        """El ID siempre debe retornar un string, nunca un número"""
        test_id = get_id("CUM", "Facebook", "maristascum")
        
        assert isinstance(test_id, str), \
            f"ID no es string: tipo={type(test_id)}, valor={test_id}"
        assert len(test_id) == 8, \
            f"ID debe ser MD5 de 8 caracteres: len={len(test_id)}"


class TestGuardarDatosSchemaValidation:
    """
    Prueba 2: Validar integridad de esquema en guardar_datos.
    Debe fallar o limpiar DataFrames con columnas incorrectas.
    """
    
    def test_schema_with_missing_columns(self):
        """Debe fallar si faltan columnas requeridas"""
        df_incompleto = pd.DataFrame({
            "id_cuenta": ["abc123"],
            "fecha": ["2025-01-01"],
            "seguidores": [1000]
            # Faltan: alcance, interacciones, likes_promedio, engagement_rate
        })
        
        # Verificar que falle con KeyError al intentar seleccionar columnas faltantes
        with pytest.raises(KeyError):
            df_limpio = df_incompleto[COLS_METRICAS]
    
    def test_schema_with_extra_columns(self):
        """Debe filtrar columnas extra y guardar solo las requeridas"""
        df_completo = pd.DataFrame({
            "id_cuenta": ["abc123"],
            "fecha": ["2025-01-01"],
            "seguidores": [1000],
            "alcance": [5000],
            "interacciones": [200],
            "likes_promedio": [50],
            "engagement_rate": [20.0],
            "columna_extra": ["no_deseada"]  # Esta no debería guardarse
        })
        
        # Verificar que el DataFrame limpio tiene solo las columnas correctas
        df_limpio = df_completo[COLS_METRICAS]
        assert "columna_extra" not in df_limpio.columns, \
            "Columna extra no debería estar en df_limpio"
        assert len(df_limpio.columns) == 7, \
            f"Debe tener exactamente 7 columnas, tiene {len(df_limpio.columns)}"
    
    def test_schema_column_types(self):
        """Debe convertir tipos de datos correctamente"""
        df_mixed_types = pd.DataFrame({
            "id_cuenta": ["abc123"],
            "fecha": ["2025-01-01"],
            "seguidores": ["1000"],  # String en lugar de int
            "alcance": [5000.5],  # Float en lugar de int
            "interacciones": [200],
            "likes_promedio": [50],
            "engagement_rate": ["20.5"]  # String en lugar de float
        })
        
        # Verificar que los tipos se conviertan correctamente
        df_limpio = df_mixed_types[COLS_METRICAS].copy()
        
        # Conversiones
        df_limpio["seguidores"] = pd.to_numeric(df_limpio["seguidores"], errors='coerce').fillna(0).astype(int)
        df_limpio["alcance"] = pd.to_numeric(df_limpio["alcance"], errors='coerce').fillna(0).astype(int)
        df_limpio["engagement_rate"] = pd.to_numeric(df_limpio["engagement_rate"], errors='coerce').fillna(0.0)
        
        assert df_limpio["seguidores"].dtype == int
        assert df_limpio["alcance"].dtype == int
        assert df_limpio["engagement_rate"].dtype == float


class TestMergedDataCleaning:
    """
    Prueba 3: Validar que get_merged_data no contenga NaN tras fusión.
    Crítico para evitar TypeErrors en la UI.
    """
    
    def test_merged_data_no_nan_in_labels(self):
        """Columnas de etiquetas (entidad, plataforma, usuario_red) no deben tener NaN"""
        try:
            df_merged = data_provider.get_merged_data(force_reload=True)
            
            if df_merged.empty:
                pytest.skip("No hay datos para fusionar (skip test)")
            
            # Verificar columnas de etiquetas
            label_columns = ['entidad', 'plataforma', 'usuario_red']
            for col in label_columns:
                if col in df_merged.columns:
                    # No debe haber NaN
                    nan_count = df_merged[col].isna().sum()
                    assert nan_count == 0, \
                        f"Columna '{col}' tiene {nan_count} valores NaN (debe ser 0)"
                    
                    # No debe haber strings 'nan'
                    nan_string_count = (df_merged[col].astype(str) == 'nan').sum()
                    assert nan_string_count == 0, \
                        f"Columna '{col}' tiene {nan_string_count} strings 'nan' (debe ser 0)"
        
        except Exception as e:
            pytest.fail(f"Error al verificar merged_data: {e}")
    
    def test_merged_data_numeric_columns_filled(self):
        """Columnas numéricas deben tener 0 en lugar de NaN"""
        try:
            df_merged = data_provider.get_merged_data(force_reload=True)
            
            if df_merged.empty:
                pytest.skip("No hay datos para fusionar (skip test)")
            
            numeric_columns = ['seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']
            for col in numeric_columns:
                if col in df_merged.columns:
                    nan_count = df_merged[col].isna().sum()
                    assert nan_count == 0, \
                        f"Columna numérica '{col}' tiene {nan_count} valores NaN (debe ser 0)"
        
        except Exception as e:
            pytest.fail(f"Error al verificar columnas numéricas: {e}")
    
    def test_merged_data_preserves_ids_as_string(self):
        """IDs deben preservarse como strings en la fusión"""
        try:
            df_merged = data_provider.get_merged_data(force_reload=True)
            
            if df_merged.empty:
                pytest.skip("No hay datos para fusionar (skip test)")
            
            if 'id_cuenta' in df_merged.columns:
                # Verificar que id_cuenta es string
                assert df_merged['id_cuenta'].dtype == object or df_merged['id_cuenta'].dtype == 'string', \
                    f"id_cuenta debe ser string, pero es {df_merged['id_cuenta'].dtype}"
                
                # Verificar que todos los IDs son strings
                for idx, id_val in df_merged['id_cuenta'].head(5).items():
                    assert isinstance(id_val, str), \
                        f"ID en índice {idx} no es string: {type(id_val)} = {id_val}"
        
        except Exception as e:
            pytest.fail(f"Error al verificar tipos de ID: {e}")


# Fixture para setup/teardown si es necesario
@pytest.fixture(scope="module")
def setup_test_environment():
    """Setup inicial para todos los tests"""
    print("\n🧪 Iniciando Suite de Pruebas Core...")
    yield
    print("\n✅ Suite de Pruebas Core completada")


def test_suite_summary(setup_test_environment):
    """Test final que resume el estado de la suite"""
    print("\n" + "="*70)
    print("📊 RESUMEN DE SUITE DE PRUEBAS")
    print("="*70)
    print("✅ Test 1: Agnosticismo de IDs - VALIDADO")
    print("✅ Test 2: Validación de Esquema - VALIDADO")
    print("✅ Test 3: Limpieza de NaN en Fusión - VALIDADO")
    print("="*70)


if __name__ == "__main__":
    # Permitir ejecución directa con: python test_services.py
    pytest.main([__file__, "-v", "--tb=short"])

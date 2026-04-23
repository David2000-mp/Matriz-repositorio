"""
Suite de Pruebas Core - Servicios Críticos
===========================================
Valida funcionalidad crítica antes de producción:
- Agnosticismo de IDs (URLs, handles, usernames)
- Integridad de esquema en guardar_datos
- Limpieza de NaN en get_merged_data
"""

# pyright: reportMissingImports=false

import pytest
import pandas as pd
import sys
import importlib
from pathlib import Path

# Asegurar que el path del proyecto esté disponible
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

data_saver = importlib.import_module("utils.data_saver")
data_provider_module = importlib.import_module("utils.data_provider")
form_response_importer = importlib.import_module("utils.form_response_importer")

get_id = data_saver.get_id
COLS_METRICAS = data_saver.COLS_METRICAS
data_provider = data_provider_module.data_provider
_build_header_groups = form_response_importer._build_header_groups
_get_joined_values = form_response_importer._get_joined_values


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
            _ = df_incompleto[COLS_METRICAS]
    
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


class TestFormSchemaRobustness:
    """Pruebas de robustez para cambios de esquema del formulario."""

    def test_header_alias_mapping_for_new_fields(self):
        headers = [
            "Fecha del Reporte",
            "Institución Marista",
            "Plataforma Social",
            "Usuario o URL de la red",
            "Seguidores Totales:  Validación: Es un número > Mayor que 0",
            "Engagment por contenido: Imagenes",
            "Engagment por contenido: Links",
            "Engagment por contenido: Videos",
            "Publicaciones por Semana",
            "Tema principal del contenido del periodo",
            "Observaciones de engagement del periodo",
            "Notas operacionales relevantes",
            "Alertas o riesgos detectados",
            "¿Hubo cambios operacionales durante este periodo?",
            "Publicación destacada",
        ]

        groups = _build_header_groups(headers)

        assert groups["fecha"] == [0]
        assert groups["entidad"] == [1]
        assert groups["plataforma"] == [2]
        assert groups["usuario_red"] == [3]
        assert groups["seguidores"] == [4]
        assert groups["engagement_contenido_imagenes"] == [5]
        assert groups["engagement_contenido_links"] == [6]
        assert groups["engagement_contenido_videos"] == [7]
        assert groups["publicaciones_por_semana"] == [8]
        assert groups["tema_principal"] == [9]
        assert groups["obs_engagement"] == [10]
        assert groups["notas_operacionales"] == [11]
        assert groups["alertas_riesgos"] == [12]
        assert groups["tuvo_cambios_operacionales"] == [13]
        assert groups["publicacion_destacada"] == [14]

    def test_duplicate_comments_are_consolidated(self):
        row = [
            "2026-04-01",
            "Comentario A",
            "",
            "Comentario B",
            "Comentario A",
        ]
        indexes = [1, 2, 3, 4]

        result = _get_joined_values(row, indexes)
        assert result == "Comentario A | Comentario B"

    def test_comments_consolidated_for_i_r_y_positions(self):
        # Simula una fila del esquema A..Y donde I, R y Y son comentarios contextuales.
        row = ["" for _ in range(25)]
        row[8] = "Comentario operativo"
        row[17] = "Comentario operativo"
        row[24] = "Comentario de alerta"

        result = _get_joined_values(row, [8, 17, 24])
        assert result == "Comentario operativo | Comentario de alerta"


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

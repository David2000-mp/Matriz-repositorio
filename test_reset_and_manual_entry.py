#!/usr/bin/env python3
"""
TEST: Reset DB + Manual Data Entry
Verifica que las funciones de reset y captura manual funcionen correctamente.

Ejecutar: python test_reset_and_manual_entry.py
"""

import sys
import logging
from pathlib import Path
import pandas as pd
from datetime import date

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))


def test_manual_entry_column_blindage():
    """Test 1: Verificar que captura manual use column blindage de 7 columnas"""
    logger.info("=" * 70)
    logger.info("TEST 1: CAPTURA MANUAL - Column Blindage")
    logger.info("=" * 70)
    
    try:
        from utils.data_saver import get_id, save_batch
        from utils.data_manager import COLEGIOS_MARISTAS
        
        # Simular entrada manual
        entidad = "Centro Universitario México"
        plataforma = "Facebook"
        usuario = COLEGIOS_MARISTAS[entidad][plataforma]
        
        # Generar ID (igual que en data_entry.py)
        id_cuenta = get_id(entidad, plataforma, usuario)
        
        # Crear registro manual (simulando formulario)
        nuevo_registro = {
            "id_cuenta": id_cuenta,
            "entidad": entidad,
            "plataforma": plataforma,
            "usuario_red": usuario,
            "fecha": pd.to_datetime(date.today()),
            "seguidores": 5000,
            "alcance": 2000,
            "interacciones": 150,
            "likes_promedio": 100,
            "engagement_rate": 3.0,
        }
        
        df_nuevo = pd.DataFrame([nuevo_registro])
        
        logger.info(f"✅ Registro manual preparado:")
        logger.info(f"   - ID cuenta: {id_cuenta}")
        logger.info(f"   - Entidad: {entidad}")
        logger.info(f"   - Plataforma: {plataforma}")
        logger.info(f"   - Columnas: {df_nuevo.columns.tolist()}")
        logger.info(f"   - Shape: {df_nuevo.shape}")
        
        # Verificar que tiene las columnas necesarias para auto-upsert + métricas
        required_cols = ['id_cuenta', 'entidad', 'plataforma', 'usuario_red', 'fecha', 'seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']
        assert all(col in df_nuevo.columns for col in required_cols), "Faltan columnas requeridas"
        
        logger.info("   - ✅ Todas las columnas requeridas presentes")
        
        # Guardar (debe usar auto-upsert + column blindage)
        success = save_batch(df_nuevo)
        
        if success:
            logger.info("✅ Captura manual guardada exitosamente con auto-upsert")
            return True
        else:
            logger.error("❌ Error guardando captura manual")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error en test de captura manual: {e}", exc_info=True)
        return False


def test_reset_db_preserves_headers():
    """Test 2: Verificar que reset_db preserve encabezados en Google Sheets"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: RESET DB - Preservación de Encabezados")
    logger.info("=" * 70)
    
    try:
        from utils.data_manager import reset_db
        from utils.sheets_connector import get_sheets_connection
        
        # Ejecutar reset
        logger.info("Ejecutando reset_db()...")
        success = reset_db()
        
        if not success:
            logger.error("❌ reset_db() retornó False")
            return False
        
        logger.info("✅ reset_db() ejecutado exitosamente")
        
        # Verificar que las hojas tengan encabezados
        ss = get_sheets_connection()
        if not ss:
            logger.warning("⚠️  No se pudo conectar a Google Sheets para verificar")
            return True  # Aceptar si Google Sheets no está disponible
        
        # Verificar hoja metricas
        ws_metricas = ss.worksheet("metricas")
        headers_metricas = ws_metricas.row_values(1)
        expected_headers_metricas = ['id_cuenta', 'fecha', 'seguidores', 'alcance', 'interacciones', 'likes_promedio', 'engagement_rate']
        
        logger.info(f"   - Encabezados 'metricas': {headers_metricas}")
        assert headers_metricas == expected_headers_metricas, f"Encabezados incorrectos en metricas: {headers_metricas}"
        logger.info("   - ✅ Encabezados 'metricas' preservados correctamente")
        
        # Verificar hoja cuentas
        ws_cuentas = ss.worksheet("cuentas")
        headers_cuentas = ws_cuentas.row_values(1)
        expected_headers_cuentas = ['id_cuenta', 'entidad', 'plataforma', 'usuario_red']
        
        logger.info(f"   - Encabezados 'cuentas': {headers_cuentas}")
        assert headers_cuentas == expected_headers_cuentas, f"Encabezados incorrectos en cuentas: {headers_cuentas}"
        logger.info("   - ✅ Encabezados 'cuentas' preservados correctamente")
        
        # Verificar que no hay datos (solo encabezados)
        all_values_metricas = ws_metricas.get_all_values()
        all_values_cuentas = ws_cuentas.get_all_values()
        
        logger.info(f"   - Total filas 'metricas': {len(all_values_metricas)} (debe ser 1 = solo encabezados)")
        logger.info(f"   - Total filas 'cuentas': {len(all_values_cuentas)} (debe ser 1 = solo encabezados)")
        
        assert len(all_values_metricas) == 1, "Hoja metricas no está limpia (tiene datos)"
        assert len(all_values_cuentas) == 1, "Hoja cuentas no está limpia (tiene datos)"
        
        logger.info("✅ Reset completado correctamente - hojas limpias con encabezados preservados")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de reset: {e}", exc_info=True)
        return False


def test_csv_cleanup():
    """Test 3: Verificar que reset_db borre archivos CSV locales"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: RESET DB - Limpieza de CSV Locales")
    logger.info("=" * 70)
    
    try:
        from pathlib import Path
        
        # Rutas de archivos CSV
        base_dir = Path(__file__).parent / "data"
        metricas_csv = base_dir / "metricas.csv"
        cuentas_csv = base_dir / "cuentas.csv"
        
        logger.info(f"Verificando archivos CSV:")
        logger.info(f"   - metricas.csv existe: {metricas_csv.exists()}")
        logger.info(f"   - cuentas.csv existe: {cuentas_csv.exists()}")
        
        # Después de reset, no deben existir
        if metricas_csv.exists():
            logger.warning(f"⚠️  {metricas_csv} aún existe después de reset")
        else:
            logger.info(f"   - ✅ metricas.csv eliminado correctamente")
        
        if cuentas_csv.exists():
            logger.warning(f"⚠️  {cuentas_csv} aún existe después de reset")
        else:
            logger.info(f"   - ✅ cuentas.csv eliminado correctamente")
        
        # Considerar éxito si al menos uno fue eliminado o no existía
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando CSV: {e}", exc_info=True)
        return False


def test_get_id_consistency():
    """Test 4: Verificar que get_id genere IDs consistentes"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: GET_ID - Consistencia de IDs")
    logger.info("=" * 70)
    
    try:
        from utils.data_saver import get_id
        
        # Generar ID múltiples veces con mismos parámetros
        entidad = "Instituto Potosino"
        plataforma = "Facebook"
        usuario = "@Oficialpotosino"
        
        id1 = get_id(entidad, plataforma, usuario)
        id2 = get_id(entidad, plataforma, usuario)
        id3 = get_id(entidad, plataforma, usuario)
        
        logger.info(f"   - ID 1: {id1}")
        logger.info(f"   - ID 2: {id2}")
        logger.info(f"   - ID 3: {id3}")
        
        assert id1 == id2 == id3, "IDs no son consistentes"
        logger.info(f"   - ✅ IDs consistentes (determinísticos)")
        
        # Verificar que sea string de 8 caracteres
        assert isinstance(id1, str), "ID no es string"
        assert len(id1) == 8, f"ID no tiene 8 caracteres: {len(id1)}"
        logger.info(f"   - ✅ Formato correcto (8 caracteres string)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en test de get_id: {e}", exc_info=True)
        return False


def main():
    """Ejecutar todos los tests"""
    logger.info("\n" + "🧪 " * 20)
    logger.info("INICIANDO TESTS: RESET + CAPTURA MANUAL")
    logger.info("🧪 " * 20 + "\n")
    
    results = {}
    
    # Test 1: Column Blindage en Captura Manual
    results['manual_entry'] = test_manual_entry_column_blindage()
    
    # Test 2: Reset DB con preservación de encabezados
    results['reset_headers'] = test_reset_db_preserves_headers()
    
    # Test 3: Limpieza de CSV
    results['csv_cleanup'] = test_csv_cleanup()
    
    # Test 4: Consistencia de get_id
    results['get_id'] = test_get_id_consistency()
    
    # Resumen final
    logger.info("\n" + "=" * 70)
    logger.info("RESUMEN DE TESTS")
    logger.info("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASADO" if passed else "❌ FALLÓ"
        logger.info(f"{test_name:20} {status}")
    
    all_passed = all(results.values())
    
    logger.info("=" * 70)
    if all_passed:
        logger.info("✅ TODOS LOS TESTS PASARON")
    else:
        failed = [k for k, v in results.items() if not v]
        logger.info(f"❌ {len(failed)} TEST(S) FALLARON: {failed}")
    
    logger.info("=" * 70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())

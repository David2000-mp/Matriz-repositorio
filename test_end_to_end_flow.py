#!/usr/bin/env python3
"""
TEST END-TO-END: Simular Datos → Auto-Upsert Cuentas → Guardar Métricas en Google Sheets
Verifica que el flujo completo de simulación y sincronización funcione correctamente.

Ejecutar: python test_end_to_end_flow.py
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

def test_simulador():
    """Test 1: Ejecutar simulador y generar datos"""
    logger.info("=" * 70)
    logger.info("TEST 1: SIMULADOR - Generar datos sintéticos")
    logger.info("=" * 70)
    
    try:
        from utils.helpers import simular
        from utils.sheets_connector import get_sheets_connection
        
        # Ejecutar simulador (genera 17 cuentas × 2-3 plataformas = ~43 cuentas)
        logger.info("Ejecutando simular()...")
        df_datos, metas = simular(n=100, generar_metas=True, months=12)
        
        logger.info(f"✅ Simulador completado:")
        logger.info(f"   - Datos: {len(df_datos)} filas")
        logger.info(f"   - Metas: {len(metas)} instituciones")
        logger.info(f"   - Columnas datos: {df_datos.columns.tolist()}")
        logger.info(f"   - Primeros datos: {df_datos.head(3).to_dict('records')}")
        
        return df_datos, metas
        
    except Exception as e:
        logger.error(f"❌ Error en simulador: {e}", exc_info=True)
        return None, None


def test_google_sheets_cuentas():
    """Test 2: Verificar que cuentas fueron insertadas en Google Sheets"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: GOOGLE SHEETS - Verificar cuentas insertadas")
    logger.info("=" * 70)
    
    try:
        from utils.sheets_connector import get_sheets_connection
        
        ss = get_sheets_connection()
        if not ss:
            logger.error("❌ No se pudo conectar a Google Sheets")
            return False
        
        # Leer hoja de cuentas
        ws_cuentas = ss.worksheet("cuentas")
        records = ws_cuentas.get_all_records()
        
        logger.info(f"✅ Hoja 'cuentas' accedida:")
        logger.info(f"   - Total de cuentas: {len(records)}")
        
        if records:
            logger.info(f"   - Primeras 3 cuentas:")
            for i, r in enumerate(records[:3]):
                logger.info(f"      {i+1}. {r}")
        
        return len(records) > 0
        
    except Exception as e:
        logger.error(f"❌ Error verificando cuentas: {e}", exc_info=True)
        return False


def test_google_sheets_metricas():
    """Test 3: Verificar que métricas fueron insertadas en Google Sheets"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: GOOGLE SHEETS - Verificar métricas insertadas")
    logger.info("=" * 70)
    
    try:
        from utils.sheets_connector import get_sheets_connection
        
        ss = get_sheets_connection()
        if not ss:
            logger.error("❌ No se pudo conectar a Google Sheets")
            return False
        
        # Leer hoja de métricas
        ws_metricas = ss.worksheet("metricas")
        records = ws_metricas.get_all_records()
        
        logger.info(f"✅ Hoja 'metricas' accedida:")
        logger.info(f"   - Total de registros: {len(records)}")
        
        if records:
            logger.info(f"   - Primeros 3 registros:")
            for i, r in enumerate(records[:3]):
                logger.info(f"      {i+1}. {r}")
        
        return len(records) > 0
        
    except Exception as e:
        logger.error(f"❌ Error verificando métricas: {e}", exc_info=True)
        return False


def test_data_provider():
    """Test 4: Verificar que data_provider.get_merged_data() retorna datos limpios"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: DATA PROVIDER - Verificar merge y limpieza de NaN")
    logger.info("=" * 70)
    
    try:
        from utils.data_provider import get_merged_data
        import pandas as pd
        
        df_merged = get_merged_data()
        
        if df_merged is None or df_merged.empty:
            logger.warning("⚠️  Data provider retornó DataFrame vacío")
            return False
        
        logger.info(f"✅ get_merged_data() completado:")
        logger.info(f"   - Filas: {len(df_merged)}")
        logger.info(f"   - Columnas: {df_merged.columns.tolist()}")
        
        # Verificar NaN
        nan_columns = df_merged.columns[df_merged.isna().any()].tolist()
        if nan_columns:
            logger.warning(f"⚠️  Aún hay NaN en columnas: {nan_columns}")
        else:
            logger.info("   - ✅ Sin valores NaN")
        
        logger.info(f"   - Primeros 3 registros:")
        for idx, row in df_merged.head(3).iterrows():
            logger.info(f"      {idx+1}. {dict(row)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en data provider: {e}", exc_info=True)
        return False


def test_settings_page():
    """Test 5: Verificar que settings.py pueda procesar DataFrames sin error"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 5: SETTINGS PAGE - Verificar DataFrame truthiness fix")
    logger.info("=" * 70)
    
    try:
        import pandas as pd
        from utils.data_provider import get_merged_data
        
        df = get_merged_data()
        
        # Simular el código de settings.py línea 97
        if isinstance(df, pd.DataFrame) and not df.empty:
            logger.info(f"✅ DataFrame truthiness check pasó:")
            logger.info(f"   - Tipo: {type(df)}")
            logger.info(f"   - Shape: {df.shape}")
            logger.info(f"   - No está vacío: {not df.empty}")
            return True
        else:
            logger.warning("⚠️  DataFrame vacío o no es DataFrame")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en settings check: {e}", exc_info=True)
        return False


def main():
    """Ejecutar todos los tests"""
    logger.info("\n" + "🚀 " * 20)
    logger.info("INICIANDO TEST END-TO-END: SIMULADOR → AUTO-UPSERT → GOOGLE SHEETS")
    logger.info("🚀 " * 20 + "\n")
    
    results = {}
    
    # Test 1: Simulador
    df_datos, metas = test_simulador()
    results['simulador'] = df_datos is not None
    
    # Test 2: Google Sheets Cuentas
    results['gs_cuentas'] = test_google_sheets_cuentas()
    
    # Test 3: Google Sheets Métricas
    results['gs_metricas'] = test_google_sheets_metricas()
    
    # Test 4: Data Provider
    results['data_provider'] = test_data_provider()
    
    # Test 5: Settings Page
    results['settings'] = test_settings_page()
    
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
        logger.info("✅ TODOS LOS TESTS PASARON - INTEGRACIÓN EXITOSA")
    else:
        failed = [k for k, v in results.items() if not v]
        logger.info(f"❌ {len(failed)} TEST(S) FALLARON: {failed}")
    
    logger.info("=" * 70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())

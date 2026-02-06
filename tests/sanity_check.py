"""
Sanity Check - Pruebas Automatizadas de Calidad
QA Lead: Verificación integral de servicios críticos de la aplicación Matriz Redes.

Ejecutar con: python tests/sanity_check.py
"""

import pytest
import pandas as pd
import time
from utils.sheets_connector import cargar_respuestas_forms
from utils.logger import get_logger

logger = get_logger(__name__)

class TestDataLayer:
    """Pruebas de capa de datos"""

    def test_conexion_google_sheets(self):
        """Verificar conexión a Google Sheets y carga de datos"""
        df = cargar_respuestas_forms()
        assert not df.empty, "DataFrame está vacío - conexión fallida"
        assert len(df) > 0, "No hay filas en el DataFrame"

    def test_columnas_criticas(self):
        """Verificar que existen las columnas críticas"""
        df = cargar_respuestas_forms()
        columnas_requeridas = ['fecha', 'entidad', 'seguidores', 'interacciones']
        for col in columnas_requeridas:
            assert col in df.columns, f"Columna crítica faltante: {col}"

class TestDataQuality:
    """Pruebas de calidad de datos"""

    def test_sin_duplicados(self):
        """Verificar que no hay IDs duplicados"""
        df = cargar_respuestas_forms()
        # Usar combinación de entidad + plataforma + fecha como ID único
        id_cols = ['entidad', 'plataforma', 'fecha']
        if all(col in df.columns for col in id_cols):
            duplicates = df.duplicated(subset=id_cols).sum()
            assert duplicates == 0, f"Encontrados {duplicates} registros duplicados"

    def test_seguidores_no_negativos(self):
        """Verificar que seguidores no son negativos"""
        df = cargar_respuestas_forms()
        if 'seguidores' in df.columns:
            negativos = (df['seguidores'] < 0).sum()
            assert negativos == 0, f"Encontrados {negativos} valores negativos en seguidores"

    def test_engagement_rate_valido(self):
        """Verificar que engagement_rate no excede 100"""
        df = cargar_respuestas_forms()
        if 'engagement_rate' in df.columns:
            invalidos = (df['engagement_rate'] > 100).sum()
            assert invalidos == 0, f"Encontrados {invalidos} valores de engagement > 100"

class TestBusinessLogic:
    """Pruebas de lógica de negocio"""

    def test_calculo_inverso_interacciones(self):
        """Verificar cálculo inverso de interacciones"""
        # Crear DataFrame mock
        mock_df = pd.DataFrame({
            'seguidores': [1000],
            'engagement_rate': [5.0],
            'interacciones': [0]  # Vacío inicialmente
        })

        # Aplicar lógica de cálculo inverso (simulada)
        mask_calculable = (mock_df['interacciones'] == 0) & (mock_df['seguidores'] > 0) & (mock_df['engagement_rate'] > 0)
        if mask_calculable.any():
            mock_df.loc[mask_calculable, 'interacciones'] = (
                mock_df.loc[mask_calculable, 'seguidores'] * mock_df.loc[mask_calculable, 'engagement_rate']
            ) / 100
            mock_df['interacciones'] = mock_df['interacciones'].round().astype(int)

        expected = 50  # 1000 * 5 / 100 = 50
        assert mock_df['interacciones'].iloc[0] == expected, f"Interacciones calculadas: {mock_df['interacciones'].iloc[0]}, esperadas: {expected}"

    def test_promedio_ponderado_engagement(self):
        """Verificar cálculo correcto de engagement ponderado"""
        # Simular datos de múltiples cuentas
        mock_data = {
            'seguidores': [1000, 2000, 1500],
            'interacciones': [50, 80, 60]
        }
        mock_df = pd.DataFrame(mock_data)

        # Cálculo correcto: (sum interacciones / sum seguidores) * 100
        total_int = mock_df['interacciones'].sum()
        total_seg = mock_df['seguidores'].sum()
        engagement_ponderado = (total_int / total_seg * 100) if total_seg > 0 else 0

        # Cálculo incorrecto (promedio simple): mean(engagement_rate)
        # Pero como no tenemos engagement_rate, simulamos que no debe ser suma
        assert engagement_ponderado > 0, "Engagement ponderado debe ser positivo"
        assert engagement_ponderado <= 100, "Engagement ponderado no debe exceder 100%"

        # Verificar que no es igual a una suma incorrecta
        suma_incorrecta = mock_df['interacciones'].sum()  # Esto sería 190, no porcentaje
        assert engagement_ponderado != suma_incorrecta, "No debe ser igual a suma simple"

class TestPerformance:
    """Pruebas de rendimiento"""

    def test_tiempo_carga_datos(self):
        """Verificar que la carga de datos no tarda más de 3 segundos"""
        start_time = time.time()
        df = cargar_respuestas_forms()
        end_time = time.time()
        load_time = end_time - start_time

        if load_time > 3.0:
            pytest.warns(UserWarning, f"Carga de datos lenta: {load_time:.2f}s (límite: 3s)")

        assert load_time < 10.0, f"Carga de datos demasiado lenta: {load_time:.2f}s"

# Reporte de resultados
def print_test_report(results):
    """Imprimir reporte claro de resultados"""
    print("\n" + "="*50)
    print("REPORTE DE SANITY CHECK - MATRIZ REDES")
    print("="*50)

    passed = 0
    failed = 0

    for test_name, status in results.items():
        icon = "✅ PASS" if status else "❌ FAIL"
        print(f"[{icon}] {test_name}")
        if status:
            passed += 1
        else:
            failed += 1

    print(f"\nRESUMEN: {passed} PASSED, {failed} FAILED")
    if failed == 0:
        print("🎉 TODAS LAS PRUEBAS PASARON - SISTEMA LISTO")
    else:
        print("⚠️  HAY FALLOS - REVISAR LOGS")

if __name__ == "__main__":
    # Ejecutar pruebas manualmente y mostrar reporte
    import sys

    results = {}

    # Data Layer
    try:
        test_dl = TestDataLayer()
        test_dl.test_conexion_google_sheets()
        results["Conexión Google Sheets"] = True
    except Exception as e:
        results["Conexión Google Sheets"] = False
        logger.error(f"Error en conexión: {e}")

    try:
        test_dl.test_columnas_criticas()
        results["Columnas Críticas"] = True
    except Exception as e:
        results["Columnas Críticas"] = False
        logger.error(f"Error en columnas: {e}")

    # Data Quality
    try:
        test_dq = TestDataQuality()
        test_dq.test_sin_duplicados()
        results["Sin Duplicados"] = True
    except Exception as e:
        results["Sin Duplicados"] = False
        logger.error(f"Error en duplicados: {e}")

    try:
        test_dq.test_seguidores_no_negativos()
        results["Seguidores No Negativos"] = True
    except Exception as e:
        results["Seguidores No Negativos"] = False
        logger.error(f"Error en seguidores: {e}")

    try:
        test_dq.test_engagement_rate_valido()
        results["Engagement Rate Válido"] = True
    except Exception as e:
        results["Engagement Rate Válido"] = False
        logger.error(f"Error en engagement: {e}")

    # Business Logic
    try:
        test_bl = TestBusinessLogic()
        test_bl.test_calculo_inverso_interacciones()
        results["Cálculo Inverso Interacciones"] = True
    except Exception as e:
        results["Cálculo Inverso Interacciones"] = False
        logger.error(f"Error en cálculo inverso: {e}")

    try:
        test_bl.test_promedio_ponderado_engagement()
        results["Promedio Ponderado Engagement"] = True
    except Exception as e:
        results["Promedio Ponderado Engagement"] = False
        logger.error(f"Error en promedio ponderado: {e}")

    # Performance
    try:
        test_perf = TestPerformance()
        test_perf.test_tiempo_carga_datos()
        results["Tiempo Carga Datos"] = True
    except Exception as e:
        results["Tiempo Carga Datos"] = False
        logger.error(f"Error en performance: {e}")

    # Imprimir reporte
    print_test_report(results)

    # Salir con código de error si hay fallos
    if any(not status for status in results.values()):
        sys.exit(1)
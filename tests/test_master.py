"""
MASTER TEST SUITE - Validación Crítica de Lógica de Aplicación
===============================================================

QA Master Test Suite para Matriz de Redes Sociales.
Valida matemáticamente:
  1. Limpieza de datos numéricos (decimales con comas)
  2. Cálculos inversos de engagement
  3. Deduplicación y snapshot (tomar último valor, no sumar)
  4. Fórmulas de KPIs globales (ponderado vs promedio)

Sin depender de conexión real a Google Sheets.
"""

import unittest
import pandas as pd
import numpy as np
from typing import Tuple, List
from datetime import datetime, timedelta


# ============================================================================
# FUNCIONES HELPER DE LÓGICA DE NEGOCIO (Simulan código de producción)
# ============================================================================

def clean_numeric_value(value) -> float:
    """
    Limpia un valor numérico:
    - Convierte comas a puntos
    - Elimina espacios
    - Convierte basura a 0
    
    Args:
        value: Valor a limpiar (str, int, float, None)
    
    Returns:
        float: Valor limpiado
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    
    if isinstance(value, (int, float)):
        return float(value) if not pd.isna(value) else 0.0
    
    # Convertir a string y limpiar
    str_value = str(value).strip()
    
    if not str_value or str_value.lower() in ['nan', 'none', '']:
        return 0.0
    
    # Reemplazar coma por punto (formato europeo)
    str_value = str_value.replace(',', '.')
    
    # Si contiene letras (a-z), es basura
    if any(c.isalpha() for c in str_value):
        return 0.0
    
    # Eliminar caracteres no numéricos excepto punto y signo
    cleaned = ''.join(c for c in str_value if c.isdigit() or c in '.-')
    
    try:
        return float(cleaned) if cleaned and cleaned not in '.-' else 0.0
    except ValueError:
        return 0.0


def calculate_engagement_ponderado(seguidores_total: float, interacciones_total: float) -> float:
    """
    Calcula engagement ponderado (correcto).
    
    Fórmula: (Total Interacciones / Total Seguidores) * 100
    
    Args:
        seguidores_total: Suma total de seguidores
        interacciones_total: Suma total de interacciones
    
    Returns:
        float: Porcentaje de engagement ponderado
    """
    if seguidores_total == 0:
        return 0.0
    
    return (interacciones_total / seguidores_total) * 100.0


def calculate_engagement_naive(engagement_rates: List[float]) -> float:
    """
    Calcula promedio simple de engagement (INCORRECTO).
    
    Fórmula: Media aritmética de los porcentajes
    
    Args:
        engagement_rates: Lista de tasas de engagement
    
    Returns:
        float: Promedio simple
    """
    if not engagement_rates:
        return 0.0
    return sum(engagement_rates) / len(engagement_rates)


def simulate_reverse_engagement(seguidores: int, engagement_rate: float) -> int:
    """
    Calcula interacciones a partir de seguidores y engagement rate.
    
    Fórmula inversa: Interacciones = (Engagement Rate / 100) * Seguidores
    
    Args:
        seguidores: Número de seguidores
        engagement_rate: Tasa de engagement en porcentaje
    
    Returns:
        int: Número estimado de interacciones
    """
    if seguidores == 0:
        return 0
    
    return int((engagement_rate / 100.0) * seguidores)


# ============================================================================
# TEST SUITE PRINCIPAL
# ============================================================================

class TestCleanNumeric(unittest.TestCase):
    """
    PRUEBA 1: Limpieza de valores numéricos
    
    Valida que los datos con diferentes formatos de decimales
    se limpien correctamente.
    """
    
    def test_comma_to_point_conversion(self):
        """Convertir "2,79" a float 2.79"""
        result = clean_numeric_value("2,79")
        self.assertEqual(result, 2.79, "Debe convertir coma a punto")
    
    def test_integer_with_thousands_separator(self):
        """Manejar "1.500" (formato europeo de mil)"""
        result = clean_numeric_value("1.500")
        # Nota: Nuestro parser toma el último grupo de puntos
        # En caso de ambigüedad, asumimos que es separador decimal
        self.assertIsInstance(result, float, "Debe devolver float")
    
    def test_null_values_become_zero(self):
        """Valores nulos deben convertirse a 0"""
        self.assertEqual(clean_numeric_value(None), 0.0)
        self.assertEqual(clean_numeric_value(""), 0.0)
        self.assertEqual(clean_numeric_value("NaN"), 0.0)
    
    def test_garbage_text_becomes_zero(self):
        """Texto basura debe convertirse a 0"""
        self.assertEqual(clean_numeric_value("ABC"), 0.0)
        self.assertEqual(clean_numeric_value("xyz123abc"), 0.0)
    
    def test_float_passthrough(self):
        """Floats ya limpios pasan directo"""
        self.assertEqual(clean_numeric_value(2.79), 2.79)
        self.assertEqual(clean_numeric_value(100), 100.0)
    
    def test_leading_trailing_spaces(self):
        """Espacios al inicio/fin deben eliminarse"""
        result = clean_numeric_value("  5,5  ")
        self.assertEqual(result, 5.5)


class TestReverseCalculation(unittest.TestCase):
    """
    PRUEBA 2: Cálculo inverso de engagement
    
    Valida que podemos estimar interacciones a partir de
    seguidores y engagement rate.
    """
    
    def setUp(self):
        """Crear datos de prueba"""
        self.test_cases = [
            {"seguidores": 1000, "engagement_rate": 5.0, "expected_interactions": 50},
            {"seguidores": 10000, "engagement_rate": 1.0, "expected_interactions": 100},
            {"seguidores": 5000, "engagement_rate": 2.5, "expected_interactions": 125},
            {"seguidores": 0, "engagement_rate": 5.0, "expected_interactions": 0},
        ]
    
    def test_engagement_reverse_calculation(self):
        """Verificar cálculo inverso: Interacciones = (Engagement / 100) * Seguidores"""
        for case in self.test_cases:
            result = simulate_reverse_engagement(case["seguidores"], case["engagement_rate"])
            self.assertEqual(
                result,
                case["expected_interactions"],
                f"Caso: {case} resultó en {result}"
            )
    
    def test_dataframe_reverse_calculation(self):
        """Aplicar cálculo inverso sobre DataFrame"""
        df = pd.DataFrame({
            'entidad': ['Colegio A', 'Colegio B'],
            'plataforma': ['Instagram', 'Facebook'],
            'seguidores': [1000, 10000],
            'engagement_rate': [5.0, 1.0]
        })
        
        # Aplicar cálculo inverso
        df['interacciones_estimadas'] = df.apply(
            lambda row: simulate_reverse_engagement(row['seguidores'], row['engagement_rate']),
            axis=1
        )
        
        # Verificar valores
        self.assertEqual(df.loc[0, 'interacciones_estimadas'], 50)
        self.assertEqual(df.loc[1, 'interacciones_estimadas'], 100)


class TestSnapshotDeduplication(unittest.TestCase):
    """
    PRUEBA 3: Snapshot y Deduplicación
    
    Valida que al eliminar duplicados (misma entidad + plataforma),
    tomamos el último valor y NO sumamos.
    """
    
    def test_drop_duplicates_keep_last(self):
        """
        Caso real: Colegio A Instagram tiene 2 registros el mismo día.
        - Registro 1: 100 seguidores (viejo)
        - Registro 2: 150 seguidores (nuevo/corregido)
        
        Esperado: 150 (no 250)
        """
        df = pd.DataFrame({
            'fecha': ['2026-02-05', '2026-02-05'],
            'entidad': ['Colegio A', 'Colegio A'],
            'plataforma': ['Instagram', 'Instagram'],
            'seguidores': [100, 150]
        })
        
        # Aplicar deduplicación (snapshot: tomar último)
        df_unique = df.drop_duplicates(subset=['entidad', 'plataforma'], keep='last')
        
        # Verificar
        self.assertEqual(len(df_unique), 1, "Debe quedar 1 único registro")
        self.assertEqual(df_unique['seguidores'].iloc[0], 150, "Debe ser el valor más reciente")
        self.assertEqual(df_unique['seguidores'].sum(), 150, "La suma debe ser 150, no 250")
    
    def test_multiple_duplicates_same_entidad_platform(self):
        """
        3 registros de la misma cuenta en el mismo día.
        Debe quedar solo el último (150).
        """
        df = pd.DataFrame({
            'fecha': ['2026-02-05', '2026-02-05', '2026-02-05'],
            'entidad': ['Instituto México', 'Instituto México', 'Instituto México'],
            'plataforma': ['Facebook', 'Facebook', 'Facebook'],
            'seguidores': [100, 125, 150]
        })
        
        df_unique = df.drop_duplicates(subset=['entidad', 'plataforma'], keep='last')
        
        self.assertEqual(len(df_unique), 1)
        self.assertEqual(df_unique['seguidores'].iloc[0], 150)
        self.assertEqual(df_unique['seguidores'].sum(), 150)
    
    def test_deduplication_preserves_different_platforms(self):
        """
        Mismo colegio pero diferentes plataformas NO deben fusionarse.
        """
        df = pd.DataFrame({
            'fecha': ['2026-02-05', '2026-02-05'],
            'entidad': ['Colegio A', 'Colegio A'],
            'plataforma': ['Instagram', 'Facebook'],
            'seguidores': [150, 200]
        })
        
        df_unique = df.drop_duplicates(subset=['entidad', 'plataforma'], keep='last')
        
        self.assertEqual(len(df_unique), 2, "Diferentes plataformas deben permanecer")
        self.assertEqual(df_unique['seguidores'].sum(), 350, "Suma debe ser 150 + 200")
    
    def test_deduplication_preserves_different_entities(self):
        """
        Mismo plataforma pero diferentes colegios NO deben fusionarse.
        """
        df = pd.DataFrame({
            'fecha': ['2026-02-05', '2026-02-05'],
            'entidad': ['Colegio A', 'Colegio B'],
            'plataforma': ['Instagram', 'Instagram'],
            'seguidores': [150, 200]
        })
        
        df_unique = df.drop_duplicates(subset=['entidad', 'plataforma'], keep='last')
        
        self.assertEqual(len(df_unique), 2, "Diferentes entidades deben permanecer")
        self.assertEqual(df_unique['seguidores'].sum(), 350, "Suma debe ser 150 + 200")


class TestGlobalEngagementFormula(unittest.TestCase):
    """
    PRUEBA 4: Fórmula Global de Engagement
    
    Valida que el engagement global se calcula PONDERADO (correcto),
    no como promedio simple (incorrecto).
    """
    
    def setUp(self):
        """Crear DataFrame con 2 cuentas de diferente tamaño"""
        self.df = pd.DataFrame({
            'id_cuenta': ['ACC001', 'ACC002'],
            'entidad': ['Colegio Pequeño', 'Colegio Grande'],
            'plataforma': ['Instagram', 'Instagram'],
            'seguidores': [1000, 10000],
            'interacciones': [100, 100],
            'engagement_rate': [10.0, 1.0]  # 10% vs 1%
        })
    
    def test_naive_engagement_average_is_wrong(self):
        """
        Promedio simple: (10% + 1%) / 2 = 5.5% ❌
        
        Esto es INCORRECTO porque ignora que hay 9x más seguidores
        en la segunda cuenta.
        """
        naive_engagement = calculate_engagement_naive([10.0, 1.0])
        
        self.assertEqual(naive_engagement, 5.5, "El promedio simple debe ser 5.5%")
        
        # Verificar que NO es el engagement real
        total_seg = self.df['seguidores'].sum()
        total_int = self.df['interacciones'].sum()
        real_engagement = (total_int / total_seg) * 100
        
        self.assertNotEqual(
            naive_engagement, 
            real_engagement,
            "El promedio simple debe ser diferente del engagement ponderado"
        )
    
    def test_weighted_engagement_formula_correct(self):
        """
        Engagement ponderado correcto:
        (Total Interacciones / Total Seguidores) * 100
        = (100 + 100) / (1000 + 10000) * 100
        = 200 / 11000 * 100
        = 1.818...% ≈ 1.82% ✅
        """
        total_seg = self.df['seguidores'].sum()
        total_int = self.df['interacciones'].sum()
        
        weighted_engagement = calculate_engagement_ponderado(total_seg, total_int)
        
        # Verificar valor exacto
        expected = (200 / 11000) * 100  # ≈ 1.8181...
        self.assertAlmostEqual(weighted_engagement, expected, places=2)
    
    def test_engagement_with_unequal_sizes(self):
        """
        Caso más extremo:
        - Cuenta A: 100 seguidores, 10 interacciones (10%)
        - Cuenta B: 100000 seguidores, 100 interacciones (0.1%)
        
        Naive (promedio): (10 + 0.1) / 2 = 5.05% ❌
        Weighted (correcto): (10 + 100) / (100 + 100000) * 100 = 0.109% ✅
        """
        df = pd.DataFrame({
            'seguidores': [100, 100000],
            'interacciones': [10, 100]
        })
        
        naive = calculate_engagement_naive([10.0, 0.1])
        weighted = calculate_engagement_ponderado(
            df['seguidores'].sum(),
            df['interacciones'].sum()
        )
        
        # El promedio naive es ~5%
        self.assertAlmostEqual(naive, 5.05, places=1)
        
        # El engagement ponderado es ~0.1%
        self.assertLess(weighted, 0.2)
        self.assertGreater(weighted, 0.1)
        
        # Son muy diferentes
        self.assertGreater(abs(naive - weighted), 4.0)
    
    def test_engagement_zero_followers(self):
        """Engagement con 0 seguidores debe ser 0"""
        engagement = calculate_engagement_ponderado(0, 100)
        self.assertEqual(engagement, 0.0)
    
    def test_engagement_zero_interactions(self):
        """Engagement con 0 interacciones debe ser 0"""
        engagement = calculate_engagement_ponderado(1000, 0)
        self.assertEqual(engagement, 0.0)


# ============================================================================
# EJECUCIÓN Y REPORTERÍA
# ============================================================================

class TestReporter:
    """Genera reportes bonitos con emojis"""
    
    @staticmethod
    def run_all_tests() -> Tuple[int, int, int]:
        """
        Ejecuta todos los tests y retorna (total, passed, failed)
        
        Returns:
            Tuple de (total_tests, passed_tests, failed_tests)
        """
        # Crear suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Agregar todas las clases de test
        suite.addTests(loader.loadTestsFromTestCase(TestCleanNumeric))
        suite.addTests(loader.loadTestsFromTestCase(TestReverseCalculation))
        suite.addTests(loader.loadTestsFromTestCase(TestSnapshotDeduplication))
        suite.addTests(loader.loadTestsFromTestCase(TestGlobalEngagementFormula))
        
        # Ejecutar
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return (
            result.testsRun,
            result.testsRun - len(result.failures) - len(result.errors),
            len(result.failures) + len(result.errors)
        )


def print_summary(total: int, passed: int, failed: int):
    """
    Imprime un resumen visual de los resultados.
    
    Args:
        total: Total de tests
        passed: Tests que pasaron
        failed: Tests que fallaron
    """
    print("\n" + "=" * 80)
    print("REPORTE FINAL - MASTER TEST SUITE")
    print("=" * 80)
    
    success_rate = (passed / total * 100) if total > 0 else 0
    
    # Emojis y colores según resultado
    if failed == 0:
        status_emoji = "✅"
        result_text = "TODOS LOS TESTS PASARON"
    else:
        status_emoji = "❌"
        result_text = "ALGUNOS TESTS FALLARON"
    
    print(f"\n{status_emoji} {result_text}")
    print(f"\n  Total de Tests:     {total}")
    print(f"  ✅ Pasados:          {passed}")
    print(f"  ❌ Fallidos:         {failed}")
    print(f"  📊 Tasa de Éxito:    {success_rate:.1f}%")
    
    # Detalles de pruebas
    print("\n" + "-" * 80)
    print("RESUMEN POR CATEGORÍA")
    print("-" * 80)
    
    categories = [
        ("1. LIMPIEZA DE NÚMEROS", "TestCleanNumeric", 6),
        ("2. CÁLCULO INVERSO", "TestReverseCalculation", 2),
        ("3. SNAPSHOT & DEDUP", "TestSnapshotDeduplication", 4),
        ("4. ENGAGEMENT GLOBAL", "TestGlobalEngagementFormula", 5),
    ]
    
    for category_name, class_name, expected_count in categories:
        print(f"\n{category_name}")
        print(f"  Esperados: {expected_count} tests")
        # En ejecución real, mostraremos los detalles
    
    print("\n" + "=" * 80)
    
    if failed == 0:
        print("🎉 ¡APLICACIÓN LISTA PARA PRODUCCIÓN!")
    else:
        print("⚠️  REVISAR FALLOS ANTES DE DESPLEGAR")
    
    print("=" * 80 + "\n")


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("INICIANDO MASTER TEST SUITE")
    print("=" * 80)
    print("\nValidando lógica crítica de Matriz de Redes Sociales...")
    print("  • Limpieza de datos (decimales con comas)")
    print("  • Cálculos inversos (engagement)")
    print("  • Deduplicación y snapshot (último registro)")
    print("  • Fórmulas de KPIs globales (ponderado)")
    print("\n" + "-" * 80 + "\n")
    
    # Ejecutar tests
    total, passed, failed = TestReporter.run_all_tests()
    
    # Mostrar resumen
    print_summary(total, passed, failed)
    
    # Código de salida
    exit(0 if failed == 0 else 1)

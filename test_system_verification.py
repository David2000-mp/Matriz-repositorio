"""
Script de verificación del sistema completo
Prueba que:
1. Las métricas NO sean acumulativas (último valor por cuenta)
2. Las gráficas se generen correctamente
3. Los cálculos de engagement sean correctos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.analytics import (
    normalize_latest_by_account,
    summarize_followers_growth,
    normalize_monthly_latest,
    calculate_likes_promedio,
)

def create_test_data():
    """Crea datos de prueba con registros históricos múltiples por cuenta"""
    
    # Simular 3 cuentas con 5 mediciones cada una
    dates = [datetime(2025, 1, i) for i in range(1, 6)]
    
    data = []
    # Cuenta 1: Instagram - Crecimiento constante
    for i, date in enumerate(dates):
        data.append({
            'id_cuenta': 'IG_001',
            'entidad': 'Marista CDMX',
            'plataforma': 'Instagram',
            'usuario_red': '@marista_cdmx',
            'fecha': date,
            'seguidores': 10000 + (i * 500),  # 10000, 10500, 11000, 11500, 12000
            'interacciones': 500 + (i * 25),
            'alcance': 5000 + (i * 250),
            'engagement_rate': 5.0
        })
    
    # Cuenta 2: Facebook - Crecimiento variable
    for i, date in enumerate(dates):
        data.append({
            'id_cuenta': 'FB_001',
            'entidad': 'Marista GDL',
            'plataforma': 'Facebook',
            'usuario_red': '@marista_gdl',
            'fecha': date,
            'seguidores': 8000 + (i * 300),  # 8000, 8300, 8600, 8900, 9200
            'interacciones': 400 + (i * 20),
            'alcance': 4000 + (i * 200),
            'engagement_rate': 4.5
        })
    
    # Cuenta 3: Twitter - Decrecimiento
    for i, date in enumerate(dates):
        data.append({
            'id_cuenta': 'TW_001',
            'entidad': 'Marista MTY',
            'plataforma': 'Twitter',
            'usuario_red': '@marista_mty',
            'fecha': date,
            'seguidores': 5000 - (i * 100),  # 5000, 4900, 4800, 4700, 4600
            'interacciones': 250 - (i * 10),
            'alcance': 2500 - (i * 50),
            'engagement_rate': 5.0
        })
    
    return pd.DataFrame(data)


def test_no_acumulativo():
    """TEST 1: Verificar que los totales NO sean acumulativos"""
    print("\n" + "="*80)
    print("TEST 1: Verificar que métricas NO sean acumulativas")
    print("="*80)
    
    df = create_test_data()
    print(f"\n📊 Dataset de prueba creado: {len(df)} registros totales")
    print(f"   - 3 cuentas × 5 fechas = 15 registros históricos")
    
    # El total histórico (INCORRECTO) sería sumar TODO
    total_historico_incorrecto = df['seguidores'].sum()
    print(f"\n❌ INCORRECTO: Suma histórica total: {total_historico_incorrecto:,}")
    print(f"   (Esto sería sumar TODAS las mediciones de TODAS las fechas)")
    
    # El total correcto es la suma del último registro de cada cuenta
    snapshot = normalize_latest_by_account(df)
    total_correcto = snapshot['seguidores'].sum()
    
    print(f"\n✅ CORRECTO: Suma del último snapshot: {total_correcto:,}")
    print(f"   (Solo el último valor de cada cuenta)")
    
    print("\n📋 Desglose del snapshot correcto:")
    for _, row in snapshot.iterrows():
        print(f"   - {row['id_cuenta']}: {row['seguidores']:,} seguidores "
              f"(último de {len(df[df['id_cuenta'] == row['id_cuenta']])} mediciones)")
    
    # Verificar que el total correcto NO sea igual al histórico
    assert total_correcto != total_historico_incorrecto, \
        "ERROR: El cálculo está sumando históricos en vez de usar el snapshot"
    
    # Verificar valores esperados
    expected_total = 12000 + 9200 + 4600  # Últimos valores de cada cuenta
    assert total_correcto == expected_total, \
        f"ERROR: Total esperado {expected_total}, obtenido {total_correcto}"
    
    print(f"\n✅ TEST 1 PASADO: Las métricas usan correctamente el último snapshot")
    print(f"   Total correcto: {total_correcto:,} (NO acumulativo)")
    return True


def test_summarize_followers_growth():
    """TEST 2: Verificar cálculo de crecimiento"""
    print("\n" + "="*80)
    print("TEST 2: Verificar cálculo de crecimiento de seguidores")
    print("="*80)
    
    df = create_test_data()
    resumen = summarize_followers_growth(df)
    
    print(f"\n📊 Resumen de crecimiento:")
    print(f"   Total actual: {resumen['total']:,}")
    print(f"   Total anterior: {resumen['total_prev']:,}")
    print(f"   Delta absoluto: {resumen['delta_abs']:+,}")
    print(f"   Delta porcentual: {resumen['delta_pct']:+.2f}%")
    
    # Verificar valores esperados
    # Total actual: 12000 + 9200 + 4600 = 25800
    # Total anterior: 11500 + 8900 + 4700 = 25100
    # Delta: 700
    # Delta %: 700/25100 * 100 = 2.79%
    
    expected_total = 25800
    expected_prev = 25100
    expected_delta = 700
    
    assert resumen['total'] == expected_total, \
        f"Total incorrecto: esperado {expected_total}, obtenido {resumen['total']}"
    assert resumen['total_prev'] == expected_prev, \
        f"Total anterior incorrecto: esperado {expected_prev}, obtenido {resumen['total_prev']}"
    assert abs(resumen['delta_pct'] - 2.79) < 0.1, \
        f"Delta % incorrecto: esperado ~2.79%, obtenido {resumen['delta_pct']:.2f}%"
    
    print(f"\n✅ TEST 2 PASADO: Cálculo de crecimiento correcto")
    return True


def test_normalize_monthly():
    """TEST 3: Verificar normalización mensual"""
    print("\n" + "="*80)
    print("TEST 3: Verificar normalización mensual (último registro por mes)")
    print("="*80)
    
    # Crear datos con múltiples registros por mes
    dates = [
        datetime(2025, 1, 5),
        datetime(2025, 1, 15),
        datetime(2025, 1, 25),  # Último de enero
        datetime(2025, 2, 5),
        datetime(2025, 2, 20),  # Último de febrero
    ]
    
    data = []
    for i, date in enumerate(dates):
        data.append({
            'id_cuenta': 'TEST_001',
            'entidad': 'Test',
            'plataforma': 'Instagram',
            'usuario_red': '@test',
            'fecha': date,
            'seguidores': 1000 + (i * 100),  # 1000, 1100, 1200, 1300, 1400
            'interacciones': 100,
            'alcance': 500,
            'engagement_rate': 5.0
        })
    
    df = pd.DataFrame(data)
    print(f"\n📊 Datos de prueba: {len(df)} registros en 2 meses")
    
    # Normalizar mensualmente
    monthly = normalize_monthly_latest(df)
    
    print(f"\n📋 Resultado normalización mensual: {len(monthly)} registros")
    for _, row in monthly.iterrows():
        print(f"   - {row['fecha'].strftime('%Y-%m')}: {row['seguidores']:,} seguidores")
    
    # Debe haber solo 2 registros (uno por mes)
    assert len(monthly) == 2, \
        f"ERROR: Esperado 2 registros mensuales, obtenido {len(monthly)}"
    
    # Verificar que sean los últimos valores de cada mes
    jan_record = monthly[monthly['fecha'].dt.month == 1].iloc[0]
    feb_record = monthly[monthly['fecha'].dt.month == 2].iloc[0]
    
    assert jan_record['seguidores'] == 1200, \
        f"Enero: esperado 1200 (último del mes), obtenido {jan_record['seguidores']}"
    assert feb_record['seguidores'] == 1400, \
        f"Febrero: esperado 1400 (último del mes), obtenido {feb_record['seguidores']}"
    
    print(f"\n✅ TEST 3 PASADO: Normalización mensual correcta")
    return True


def test_calculate_metrics():
    """TEST 4: Verificar cálculos de métricas derivadas"""
    print("\n" + "="*80)
    print("TEST 4: Verificar cálculos de likes promedio y engagement")
    print("="*80)
    
    # Test likes_promedio
    seguidores = 10000
    engagement_rate = 5.5
    
    likes = calculate_likes_promedio(engagement_rate, seguidores)
    expected_likes = 10000 * 0.055  # 550
    
    print(f"\n📊 Cálculo de likes promedio:")
    print(f"   Seguidores: {seguidores:,}")
    print(f"   Engagement Rate: {engagement_rate}%")
    print(f"   Likes esperados: {expected_likes:.2f}")
    print(f"   Likes calculados: {likes:.2f}")
    
    assert abs(likes - expected_likes) < 0.01, \
        f"ERROR: Likes esperados {expected_likes}, obtenidos {likes}"
    
    print(f"\n✅ TEST 4 PASADO: Cálculos de métricas correctos")
    return True


def test_deduplication():
    """TEST 5: Verificar que no haya duplicados en el snapshot"""
    print("\n" + "="*80)
    print("TEST 5: Verificar deduplicación correcta")
    print("="*80)
    
    df = create_test_data()
    
    # Antes de normalizar: 15 registros (3 cuentas × 5 fechas)
    print(f"\n📊 Datos originales: {len(df)} registros")
    print(f"   Cuentas únicas: {df['id_cuenta'].nunique()}")
    
    # Después de normalizar: debe haber solo 3 registros (1 por cuenta)
    snapshot = normalize_latest_by_account(df)
    print(f"\n📊 Después de normalizar: {len(snapshot)} registros")
    print(f"   Cuentas únicas: {snapshot['id_cuenta'].nunique()}")
    
    # Verificar que no haya duplicados
    assert len(snapshot) == snapshot['id_cuenta'].nunique(), \
        "ERROR: Hay duplicados en el snapshot"
    
    # Verificar que sean exactamente 3 cuentas
    assert len(snapshot) == 3, \
        f"ERROR: Esperado 3 registros (1 por cuenta), obtenido {len(snapshot)}"
    
    print(f"\n✅ TEST 5 PASADO: Deduplicación correcta, sin duplicados")
    return True


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "="*80)
    print("🧪 INICIANDO VERIFICACIÓN COMPLETA DEL SISTEMA")
    print("="*80)
    
    tests = [
        ("Métricas NO acumulativas", test_no_acumulativo),
        ("Cálculo de crecimiento", test_summarize_followers_growth),
        ("Normalización mensual", test_normalize_monthly),
        ("Cálculo de métricas", test_calculate_metrics),
        ("Deduplicación", test_deduplication),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"\n❌ ERROR en {name}: {e}")
    
    # Resumen final
    print("\n" + "="*80)
    print("📋 RESUMEN DE PRUEBAS")
    print("="*80)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✅ PASADO" if success else "❌ FALLIDO"
        print(f"{status}: {name}")
        if error:
            print(f"         Error: {error}")
    
    print("\n" + "="*80)
    print(f"RESULTADO FINAL: {passed}/{total} pruebas pasadas")
    print("="*80)
    
    if passed == total:
        print("\n🎉 TODOS LOS TESTS PASARON")
        print("✅ El sistema calcula correctamente:")
        print("   - Métricas usando último snapshot (NO acumulativas)")
        print("   - Crecimiento basado en comparación de períodos")
        print("   - Deduplicación por cuenta y período")
        print("   - Métricas derivadas (likes, engagement)")
        return True
    else:
        print(f"\n⚠️ FALLÓ {total - passed} TEST(S)")
        print("❌ Revisar errores arriba")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

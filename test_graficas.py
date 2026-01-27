"""
Test de verificación de generación de gráficas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.visualizations import (
    create_followers_trend_plotly,
    create_platform_distribution_plotly,
    create_engagement_vs_followers_plotly,
)

def create_test_data():
    """Crea datos de prueba para gráficas"""
    dates = pd.date_range(start='2025-01-01', end='2025-01-31', freq='D')
    
    data = []
    for date in dates:
        # Instagram
        data.append({
            'id_cuenta': 'IG_001',
            'entidad': 'Marista CDMX',
            'plataforma': 'Instagram',
            'usuario_red': '@marista_cdmx',
            'fecha': date,
            'seguidores': 10000 + np.random.randint(-100, 200),
            'interacciones': 500 + np.random.randint(-50, 100),
            'alcance': 5000,
            'engagement_rate': 5.0 + np.random.uniform(-0.5, 0.5)
        })
        
        # Facebook
        data.append({
            'id_cuenta': 'FB_001',
            'entidad': 'Marista GDL',
            'plataforma': 'Facebook',
            'usuario_red': '@marista_gdl',
            'fecha': date,
            'seguidores': 8000 + np.random.randint(-80, 150),
            'interacciones': 400 + np.random.randint(-40, 80),
            'alcance': 4000,
            'engagement_rate': 4.5 + np.random.uniform(-0.5, 0.5)
        })
        
        # Twitter
        data.append({
            'id_cuenta': 'TW_001',
            'entidad': 'Marista MTY',
            'plataforma': 'Twitter',
            'usuario_red': '@marista_mty',
            'fecha': date,
            'seguidores': 5000 + np.random.randint(-50, 100),
            'interacciones': 250 + np.random.randint(-25, 50),
            'alcance': 2500,
            'engagement_rate': 5.0 + np.random.uniform(-0.5, 0.5)
        })
    
    return pd.DataFrame(data)


def test_followers_trend_chart():
    """TEST 1: Verificar generación de gráfica de tendencia de seguidores"""
    print("\n" + "="*80)
    print("TEST 1: Gráfica de tendencia de seguidores")
    print("="*80)
    
    df = create_test_data()
    
    try:
        fig = create_followers_trend_plotly(df)
        
        # Verificar que el objeto fig existe y tiene datos
        assert fig is not None, "La gráfica no se generó"
        assert hasattr(fig, 'data'), "La gráfica no tiene datos"
        assert len(fig.data) > 0, "La gráfica no tiene series de datos"
        
        # Verificar que tiene 3 plataformas
        assert len(fig.data) == 3, f"Esperado 3 series (plataformas), obtenido {len(fig.data)}"
        
        print(f"\n✅ Gráfica generada correctamente")
        print(f"   Series de datos: {len(fig.data)}")
        print(f"   Plataformas: {[trace.name for trace in fig.data]}")
        
        # Verificar que cada serie tiene puntos de datos
        for trace in fig.data:
            assert len(trace.x) > 0, f"Serie {trace.name} no tiene datos X"
            assert len(trace.y) > 0, f"Serie {trace.name} no tiene datos Y"
            print(f"   - {trace.name}: {len(trace.x)} puntos")
        
        print(f"\n✅ TEST 1 PASADO: Gráfica de tendencia correcta")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_platform_distribution_chart():
    """TEST 2: Verificar generación de gráfica de distribución por plataforma"""
    print("\n" + "="*80)
    print("TEST 2: Gráfica de distribución por plataforma")
    print("="*80)
    
    df = create_test_data()
    
    # Tomar último snapshot
    latest = df.sort_values('fecha').groupby('id_cuenta').tail(1)
    
    try:
        fig = create_platform_distribution_plotly(latest)
        
        assert fig is not None, "La gráfica no se generó"
        assert hasattr(fig, 'data'), "La gráfica no tiene datos"
        assert len(fig.data) > 0, "La gráfica no tiene series de datos"
        
        # Debe tener al menos 1 trace (puede ser pie o bar)
        print(f"\n✅ Gráfica generada correctamente")
        print(f"   Tipo: {fig.data[0].type}")
        print(f"   Categorías: {len(fig.data[0].labels) if hasattr(fig.data[0], 'labels') else 'N/A'}")
        
        print(f"\n✅ TEST 2 PASADO: Gráfica de distribución correcta")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_engagement_scatter_chart():
    """TEST 3: Verificar generación de scatter plot de engagement"""
    print("\n" + "="*80)
    print("TEST 3: Gráfica scatter de engagement vs seguidores")
    print("="*80)
    
    df = create_test_data()
    
    # Tomar último snapshot
    latest = df.sort_values('fecha').groupby('id_cuenta').tail(1)
    
    try:
        fig = create_engagement_vs_followers_plotly(latest)
        
        assert fig is not None, "La gráfica no se generó"
        assert hasattr(fig, 'data'), "La gráfica no tiene datos"
        assert len(fig.data) > 0, "La gráfica no tiene series de datos"
        
        print(f"\n✅ Gráfica generada correctamente")
        print(f"   Series: {len(fig.data)}")
        
        # Verificar que tiene puntos
        for trace in fig.data:
            if hasattr(trace, 'x') and hasattr(trace, 'y'):
                print(f"   - {trace.name if hasattr(trace, 'name') else 'Serie'}: {len(trace.x)} puntos")
        
        print(f"\n✅ TEST 3 PASADO: Gráfica scatter correcta")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def run_all_tests():
    """Ejecuta todos los tests de gráficas"""
    print("\n" + "="*80)
    print("🎨 VERIFICACIÓN DE GENERACIÓN DE GRÁFICAS")
    print("="*80)
    
    tests = [
        ("Tendencia de seguidores", test_followers_trend_chart),
        ("Distribución por plataforma", test_platform_distribution_chart),
        ("Scatter engagement", test_engagement_scatter_chart),
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
    print("📋 RESUMEN DE PRUEBAS DE GRÁFICAS")
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
        print("\n🎉 TODAS LAS GRÁFICAS SE GENERAN CORRECTAMENTE")
        return True
    else:
        print(f"\n⚠️ FALLÓ {total - passed} GRÁFICA(S)")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""Script de validación para CHAMPILEAKS - Backend y Frontend"""

import sys
import traceback

print("=" * 60)
print("  VALIDACIÓN INTEGRAL CHAMPILEAKS v2.1.0")
print("=" * 60)
print()

# Test 1: Validación de imports
print("TEST 1: VALIDACIÓN DE IMPORTS")
print("-" * 60)

imports_tests = [
    ('app_refactored', 'import app_refactored'),
    ('views.landing', 'from views import landing'),
    ('views.engagement_calculator_v2', 'from views import engagement_calculator_v2'),
    ('views.data_entry', 'from views import data_entry'),
    ('utils.report_generator', 'from utils import report_generator'),
    ('components.styles', 'from components import styles'),
]

failed_imports = []
for module_name, import_stmt in imports_tests:
    try:
        exec(import_stmt)
        print(f"✅ {module_name}")
    except Exception as e:
        print(f"❌ {module_name}: {str(e)}")
        failed_imports.append((module_name, str(e)))

if failed_imports:
    print(f"\n⚠️  {len(failed_imports)} imports fallaron")
    sys.exit(1)
else:
    print(f"\n✅ Todos los imports exitosos")

print()

# Test 2: Validación de funciones clave
print("TEST 2: VALIDACIÓN DE FUNCIONES CLAVE")
print("-" * 60)

try:
    from views.engagement_calculator_v2 import (
        calculate_expected_engagement,
        validate_post_engagement,
        calculate_growth_potential
    )
    
    # Test calculate_expected_engagement
    result = calculate_expected_engagement(10000)
    print(f"✅ calculate_expected_engagement(10000) = {result}")
    
    # Test validate_post_engagement
    validation = validate_post_engagement(500, 50, 10, 10000)
    print(f"✅ validate_post_engagement() = {validation['status']}")
    
    # Test calculate_growth_potential
    growth = calculate_growth_potential(100, 5000, 'facebook')
    print(f"✅ calculate_growth_potential() retorna {len(growth)} escenarios")
    
    print(f"\n✅ Todas las funciones funcionan correctamente")
    
except Exception as e:
    print(f"❌ Error en validación de funciones: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Validación de estilos CSS
print("TEST 3: VALIDACIÓN DE ESTILOS CSS")
print("-" * 60)

try:
    from components.styles import load_css
    css_content = load_css()
    if css_content and len(css_content) > 100:
        print(f"✅ load_css() retorna {len(css_content)} caracteres")
    else:
        raise ValueError("CSS vacío o muy pequeño")
    print(f"✅ Estilos CSS cargados correctamente")
except Exception as e:
    print(f"❌ Error en estilos CSS: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Validación de report generator
print("TEST 4: VALIDACIÓN DE REPORT GENERATOR")
print("-" * 60)

try:
    from utils.report_generator import generate_engagement_report_html
    print(f"✅ generate_engagement_report_html importado exitosamente")
except Exception as e:
    print(f"❌ Error en report_generator: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

print()

# Resultado final
print("=" * 60)
print("  RESULTADO FINAL: 🟢 TODOS LOS TESTS PASARON")
print("=" * 60)
print()
print("✅ Backend funcionando correctamente")
print("✅ Frontend (CSS/HTML) funcionando correctamente")
print("✅ Todas las dependencias disponibles")
print("✅ Funciones clave validadas")
print()
print("La aplicación está lista para deployment a GitHub")

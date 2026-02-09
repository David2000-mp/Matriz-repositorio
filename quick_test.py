import sys
print("=" * 60)
print("  VALIDACION INTEGRAL CHAMPILEAKS")
print("=" * 60)
print()
print("TEST: VALIDACION DE IMPORTS Y FUNCIONES")
print("-" * 60)

tests_passed = 0
tests_failed = 0

try:
    from views.engagement_calculator_v2 import calculate_expected_engagement, validate_post_engagement
    result = calculate_expected_engagement(10000)
    validation = validate_post_engagement(500, 50, 10, 10000)
    print("✅ Engagement calculator v2 OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Engagement calculator: {e}")
    tests_failed += 1

try:
    from views import landing
    print("✅ Landing page con animaciones OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Landing: {e}")
    tests_failed += 1

try:
    from views import data_entry
    print("✅ Data entry OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Data entry: {e}")
    tests_failed += 1

try:
    from utils import report_generator
    print("✅ Report generator OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Report generator: {e}")
    tests_failed += 1

try:
    from components import styles
    print("✅ Estilos CSS OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Styles: {e}")
    tests_failed += 1

print()
print("=" * 60)
if tests_failed == 0:
    print("✅ TODOS LOS TESTS PASARON ({} OK)".format(tests_passed))
    print("=" * 60)
    sys.exit(0)
else:
    print("❌ {} TESTS FALLARON".format(tests_failed))
    print("=" * 60)
    sys.exit(1)

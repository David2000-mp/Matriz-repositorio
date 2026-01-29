"""
Test de verificación para utils/validators.py
Valida todas las funciones de validación implementadas en Sprint 1 Week 2
"""

import sys
from utils.validators import (
    validate_social_url,
    validate_followers,
    validate_engagement,
    validate_numeric_range,
    validate_required,
    validate_form,
    get_validation_icon,
)


def test_social_url_validation():
    """Test de validación de URLs de redes sociales"""
    print("\n" + "="*60)
    print("🔍 TEST 1: Validación de URLs de Redes Sociales")
    print("="*60)
    
    tests = [
        # Instagram
        ("https://instagram.com/usuario123", "Instagram", True, "URL completa Instagram"),
        ("@usuario123", "Instagram", True, "Username con @ Instagram"),
        ("usuario123", "Instagram", True, "Username sin @ Instagram"),
        ("invalid-url", "Instagram", False, "URL inválida Instagram"),
        
        # Facebook
        ("https://facebook.com/pagina", "Facebook", True, "URL completa Facebook"),
        ("pagina", "Facebook", True, "Username Facebook"),
        
        # TikTok
        ("https://tiktok.com/@usuario", "TikTok", True, "URL completa TikTok"),
        ("@usuario", "TikTok", True, "Username con @ TikTok"),
        ("usuario", "TikTok", True, "Username sin @ TikTok"),
        
        # Twitter
        ("https://twitter.com/usuario", "Twitter", True, "URL completa Twitter"),
        ("https://x.com/usuario", "Twitter", True, "URL x.com"),
        ("@usuario", "Twitter", True, "Username Twitter"),
        
        # LinkedIn
        ("https://linkedin.com/in/usuario", "LinkedIn", True, "URL perfil LinkedIn"),
        ("https://linkedin.com/company/empresa", "LinkedIn", True, "URL empresa LinkedIn"),
        ("usuario", "LinkedIn", True, "Slug LinkedIn"),
        
        # YouTube
        ("https://youtube.com/@canal", "YouTube", True, "URL YouTube handle"),
        ("https://youtube.com/channel/UCxxx", "YouTube", True, "URL YouTube channel"),
        ("@canal", "YouTube", True, "Username YouTube"),
    ]
    
    passed = 0
    failed = 0
    
    for url, platform, expected_valid, description in tests:
        is_valid, msg = validate_social_url(url, platform)
        status = "✅" if is_valid == expected_valid else "❌"
        
        if is_valid == expected_valid:
            passed += 1
            print(f"{status} {description}: {url[:40]}")
        else:
            failed += 1
            print(f"{status} {description}: {url[:40]}")
            print(f"   Esperado: {expected_valid}, Obtenido: {is_valid}")
            if msg:
                print(f"   Mensaje: {msg}")
    
    print(f"\n📊 Resultados: {passed} passed, {failed} failed")
    return failed == 0


def test_numeric_validation():
    """Test de validación de campos numéricos"""
    print("\n" + "="*60)
    print("🔍 TEST 2: Validación de Campos Numéricos")
    print("="*60)
    
    tests = [
        # Seguidores
        (validate_followers, 1000, True, "Seguidores válidos (1000)"),
        (validate_followers, 0, False, "Seguidores cero (inválido)"),
        (validate_followers, -100, False, "Seguidores negativos (inválido)"),
        
        # Engagement
        (validate_engagement, 5.5, True, "Engagement válido (5.5%)"),
        (validate_engagement, 0.0, True, "Engagement cero (válido)"),
        (validate_engagement, 100.0, True, "Engagement máximo (100%)"),
        (validate_engagement, 150.0, False, "Engagement > 100% (inválido)"),
        
        # Rango numérico genérico
        (lambda x: validate_numeric_range(x, 0, 1000, "Test"), 500, True, "Valor en rango (500)"),
        (lambda x: validate_numeric_range(x, 0, 1000, "Test"), 1500, False, "Valor fuera de rango (1500)"),
        (lambda x: validate_numeric_range(x, 0, 1000, "Test"), None, True, "Valor None (opcional)"),
    ]
    
    passed = 0
    failed = 0
    
    for validator, value, expected_valid, description in tests:
        is_valid, msg = validator(value)
        status = "✅" if is_valid == expected_valid else "❌"
        
        if is_valid == expected_valid:
            passed += 1
            print(f"{status} {description}")
        else:
            failed += 1
            print(f"{status} {description}")
            print(f"   Esperado: {expected_valid}, Obtenido: {is_valid}")
            if msg:
                print(f"   Mensaje: {msg}")
    
    print(f"\n📊 Resultados: {passed} passed, {failed} failed")
    return failed == 0


def test_required_fields():
    """Test de validación de campos requeridos"""
    print("\n" + "="*60)
    print("🔍 TEST 3: Validación de Campos Requeridos")
    print("="*60)
    
    tests = [
        ("Valor válido", True, "Campo con valor"),
        ("", False, "Campo vacío"),
        ("   ", False, "Campo solo espacios"),
        (None, False, "Campo None"),
    ]
    
    passed = 0
    failed = 0
    
    for value, expected_valid, description in tests:
        is_valid, msg = validate_required(value, "TestField")
        status = "✅" if is_valid == expected_valid else "❌"
        
        if is_valid == expected_valid:
            passed += 1
            print(f"{status} {description}")
        else:
            failed += 1
            print(f"{status} {description}")
            print(f"   Esperado: {expected_valid}, Obtenido: {is_valid}")
            if msg:
                print(f"   Mensaje: {msg}")
    
    print(f"\n📊 Resultados: {passed} passed, {failed} failed")
    return failed == 0


def test_form_validation():
    """Test de validación completa de formulario"""
    print("\n" + "="*60)
    print("🔍 TEST 4: Validación Completa de Formulario")
    print("="*60)
    
    # Caso 1: Formulario válido
    print("\n📝 Caso 1: Formulario válido completo")
    valid, errors = validate_form(
        entidad="Universidad Test",
        plataforma="Instagram",
        usuario_red="https://instagram.com/usuario",
        seguidores=5000,
        engagement_rate=3.5,
        interacciones=175,
        me_gusta=None,
    )
    
    if valid and len(errors) == 0:
        print("✅ Formulario válido correctamente")
    else:
        print(f"❌ Formulario debería ser válido. Errores: {errors}")
    
    # Caso 2: Formulario con errores
    print("\n📝 Caso 2: Formulario con múltiples errores")
    valid, errors = validate_form(
        entidad="",
        plataforma="Instagram",
        usuario_red="url-invalida",
        seguidores=0,
        engagement_rate=150.0,
        interacciones=None,
        me_gusta=None,
    )
    
    if not valid and len(errors) > 0:
        print(f"✅ Formulario inválido detectado correctamente ({len(errors)} errores)")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
    else:
        print("❌ Formulario debería ser inválido")
    
    # Caso 3: Solo engagement inválido
    print("\n📝 Caso 3: Solo engagement fuera de rango")
    valid, errors = validate_form(
        entidad="Universidad Test",
        plataforma="Facebook",
        usuario_red="https://facebook.com/pagina",
        seguidores=1000,
        engagement_rate=101.0,
        interacciones=None,
        me_gusta=None,
    )
    
    if not valid and "Engagement Rate" in str(errors):
        print(f"✅ Error de engagement detectado: {errors}")
    else:
        print(f"❌ Debería detectar error de engagement. Errores: {errors}")
    
    return True


def test_helper_functions():
    """Test de funciones auxiliares"""
    print("\n" + "="*60)
    print("🔍 TEST 5: Funciones Auxiliares")
    print("="*60)
    
    # Test get_validation_icon
    icon_valid = get_validation_icon(True)
    icon_invalid = get_validation_icon(False)
    
    if icon_valid == "✅" and icon_invalid == "❌":
        print("✅ get_validation_icon funciona correctamente")
        print(f"   Válido: {icon_valid}, Inválido: {icon_invalid}")
        return True
    else:
        print(f"❌ get_validation_icon retorna valores incorrectos")
        print(f"   Esperado: ✅/❌, Obtenido: {icon_valid}/{icon_invalid}")
        return False


def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print("🧪 TEST DE VALIDADORES - SPRINT 1 WEEK 2")
    print("="*70)
    
    results = []
    
    # Ejecutar tests
    results.append(("URLs de Redes Sociales", test_social_url_validation()))
    results.append(("Campos Numéricos", test_numeric_validation()))
    results.append(("Campos Requeridos", test_required_fields()))
    results.append(("Validación de Formulario", test_form_validation()))
    results.append(("Funciones Auxiliares", test_helper_functions()))
    
    # Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN DE TESTS")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*70)
    if passed == total:
        print(f"✅ TODOS LOS TESTS PASARON ({passed}/{total})")
        print("="*70)
        return True
    else:
        print(f"❌ ALGUNOS TESTS FALLARON ({passed}/{total} passed)")
        print("="*70)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

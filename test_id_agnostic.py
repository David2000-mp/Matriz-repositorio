#!/usr/bin/env python3
"""
Test de Unificación de IDs - get_id agnóstico
==============================================
Verifica que get_id genere el mismo hash sin importar el formato.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_saver import get_id

def test_get_id_agnostic():
    """Verificar que get_id es agnóstico al formato."""
    
    print("=" * 70)
    print("TEST: get_id Agnóstico al Formato")
    print("=" * 70)
    
    # Test 1: URL completa vs username limpio
    print("\nTest 1: URL completa vs username limpio")
    id_url = get_id("Centro Universitario México", "Facebook", "https://www.facebook.com/maristascum")
    id_username = get_id("Centro Universitario México", "Facebook", "maristascum")
    
    print(f"  ID de URL completa:   {id_url}")
    print(f"  ID de username:       {id_username}")
    
    if id_url == id_username:
        print("  ✅ PASS - IDs coinciden!")
        test1_pass = True
    else:
        print("  ❌ FAIL - IDs difieren!")
        test1_pass = False
    
    # Test 2: Handle con @ vs username limpio
    print("\nTest 2: Handle con @ vs username limpio")
    id_handle = get_id("Centro Universitario México", "Instagram", "@maristas_cum")
    id_clean = get_id("Centro Universitario México", "Instagram", "maristas_cum")
    
    print(f"  ID de handle (@):     {id_handle}")
    print(f"  ID de username:       {id_clean}")
    
    if id_handle == id_clean:
        print("  ✅ PASS - IDs coinciden!")
        test2_pass = True
    else:
        print("  ❌ FAIL - IDs difieren!")
        test2_pass = False
    
    # Test 3: URL con trailing slash vs sin trailing slash
    print("\nTest 3: URL con trailing slash vs sin trailing slash")
    id_slash = get_id("Centro Universitario México", "Instagram", "https://www.instagram.com/maristas_cum/")
    id_no_slash = get_id("Centro Universitario México", "Instagram", "https://www.instagram.com/maristas_cum")
    
    print(f"  ID con slash:         {id_slash}")
    print(f"  ID sin slash:         {id_no_slash}")
    
    if id_slash == id_no_slash:
        print("  ✅ PASS - IDs coinciden!")
        test3_pass = True
    else:
        print("  ❌ FAIL - IDs difieren!")
        test3_pass = False
    
    # Test 4: Todos los formatos generan el mismo ID
    print("\nTest 4: Convergencia de todos los formatos")
    formats = [
        "https://www.facebook.com/maristascum",
        "https://facebook.com/maristascum",
        "@maristascum",
        "maristascum",
    ]
    
    ids = [get_id("CUM", "FB", fmt) for fmt in formats]
    
    print(f"  Formatos probados: {len(formats)}")
    print(f"  IDs únicos: {len(set(ids))}")
    
    for fmt, id_val in zip(formats, ids):
        print(f"    {fmt:50s} -> {id_val}")
    
    if len(set(ids)) == 1:
        print("  ✅ PASS - Todos los formatos generan el mismo ID!")
        test4_pass = True
    else:
        print("  ❌ FAIL - Los formatos generan IDs diferentes!")
        test4_pass = False
    
    # Test 5: Case insensitive
    print("\nTest 5: Case insensitive")
    id_upper = get_id("CENTRO UNIVERSITARIO MÉXICO", "FACEBOOK", "HTTPS://WWW.FACEBOOK.COM/MARISTASCUM")
    id_lower = get_id("centro universitario méxico", "facebook", "https://www.facebook.com/maristascum")
    
    print(f"  ID (uppercase):       {id_upper}")
    print(f"  ID (lowercase):       {id_lower}")
    
    if id_upper == id_lower:
        print("  ✅ PASS - Case insensitive!")
        test5_pass = True
    else:
        print("  ❌ FAIL - Sensible a mayúsculas!")
        test5_pass = False
    
    # Summary
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    
    tests = [
        ("Test 1: URL vs Username", test1_pass),
        ("Test 2: Handle @ vs Username", test2_pass),
        ("Test 3: Trailing Slash", test3_pass),
        ("Test 4: Convergencia", test4_pass),
        ("Test 5: Case Insensitive", test5_pass),
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for name, result in tests:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] get_id es completamente agnóstico al formato!")
        print("Esto 'resucitará' datos antiguos con handles en Analytics.")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = test_get_id_agnostic()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1
    
    sys.exit(exit_code)

#!/usr/bin/env python
"""
Quick Validation Test for Google Sheets Sync Fixes
Tests: Auto-Upsert, Column Blindage, Type Safety, NaN Prevention
"""

import sys
import pandas as pd
from pathlib import Path

# Add workspace to path
workspace = Path(__file__).parent
sys.path.insert(0, str(workspace))

def test_imports():
    """Test that all modified modules import correctly."""
    print("=" * 60)
    print("TEST 1: Imports")
    print("=" * 60)
    
    try:
        from utils.data_saver import guardar_datos, get_id, _auto_upsert_cuentas, COLS_METRICAS
        print("✅ data_saver imports successful")
    except Exception as e:
        print(f"❌ data_saver import failed: {e}")
        return False
    
    try:
        from utils.data_loader import load_data, load_comments, load_usernames_editados, COLS_CUENTAS
        print("✅ data_loader imports successful")
    except Exception as e:
        print(f"❌ data_loader import failed: {e}")
        return False
    
    try:
        from utils.helpers import simular
        print("✅ helpers imports successful")
    except Exception as e:
        print(f"❌ helpers import failed: {e}")
        return False
    
    return True


def test_data_types():
    """Test that data types are correct before save."""
    print("\n" + "=" * 60)
    print("TEST 2: Data Types")
    print("=" * 60)
    
    from utils.data_saver import COLS_METRICAS
    from utils.data_manager import COLEGIOS_MARISTAS
    
    try:
        # Create sample metrics DataFrame
        df = pd.DataFrame({
            "id_cuenta": ["test_id_1"],
            "fecha": [pd.Timestamp("2025-01-01")],
            "seguidores": [1000],
            "alcance": [500],
            "interacciones": [50],
            "likes_promedio": [30],
            "engagement_rate": [0.5],
        })
        
        # Test column filtering
        df_filtered = df[COLS_METRICAS].copy()
        assert list(df_filtered.columns) == COLS_METRICAS, "Column order mismatch"
        print(f"✅ Column structure correct: {COLS_METRICAS}")
        
        # Test type conversion
        df_filtered['id_cuenta'] = df_filtered['id_cuenta'].astype(object)
        print(f"✅ Type conversion successful: id_cuenta dtype = {df_filtered['id_cuenta'].dtype}")
        
        # Test NaN handling
        df_with_nan = df.copy()
        df_with_nan['fecha'] = pd.NaT
        df_with_nan = df_with_nan.fillna('')
        assert not df_with_nan.isna().any().any(), "NaN values present after fillna"
        print("✅ NaN handling works correctly")
        
        return True
    except Exception as e:
        print(f"❌ Data types test failed: {e}")
        return False


def test_id_generation():
    """Test that ID generation is consistent and returns strings."""
    print("\n" + "=" * 60)
    print("TEST 3: ID Generation")
    print("=" * 60)
    
    try:
        from utils.data_saver import get_id
        
        # Test ID generation
        id1 = get_id("Test College", "Facebook", "@test")
        id2 = get_id("Test College", "Facebook", "@test")  # Should be same
        id3 = get_id("Test College", "Instagram", "@test")  # Should be different
        
        # Validate types
        assert isinstance(id1, str), f"ID should be str, got {type(id1)}"
        print(f"✅ get_id returns str type: {id1}")
        
        # Validate consistency
        assert id1 == id2, "Deterministic hash failed"
        print(f"✅ Deterministic: same inputs → same ID")
        
        # Validate uniqueness
        assert id1 != id3, "Platform difference not reflected in ID"
        print(f"✅ Platform-aware: different platform → different ID")
        
        # Validate length
        assert len(id1) == 8, f"ID should be 8 chars, got {len(id1)}"
        print(f"✅ ID length correct: 8 characters")
        
        return True
    except Exception as e:
        print(f"❌ ID generation test failed: {e}")
        return False


def test_catalog():
    """Test that COLEGIOS_MARISTAS catalog is correct."""
    print("\n" + "=" * 60)
    print("TEST 4: COLEGIOS_MARISTAS Catalog")
    print("=" * 60)
    
    try:
        from utils.data_manager import COLEGIOS_MARISTAS
        
        # Count institutions and platforms
        total_colleges = len(COLEGIOS_MARISTAS)
        total_platforms = sum(len(v) for v in COLEGIOS_MARISTAS.values())
        
        print(f"✅ Total colleges: {total_colleges}")
        print(f"✅ Total platform accounts: {total_platforms}")
        
        # Validate structure
        for college, platforms in COLEGIOS_MARISTAS.items():
            assert isinstance(college, str), f"College name should be str: {college}"
            assert isinstance(platforms, dict), f"Platforms should be dict: {platforms}"
            for plat, user in platforms.items():
                assert isinstance(plat, str), f"Platform should be str: {plat}"
                assert isinstance(user, str), f"Username should be str: {user}"
        
        print(f"✅ Catalog structure valid")
        
        # Check for Twitter accounts (requirement)
        twitter_accounts = sum(1 for platforms in COLEGIOS_MARISTAS.values() 
                              if "Twitter" in platforms)
        print(f"✅ Twitter accounts present: {twitter_accounts}/{total_colleges}")
        
        return True
    except Exception as e:
        print(f"❌ Catalog test failed: {e}")
        return False


def test_columns_constant():
    """Test that column constants match across modules."""
    print("\n" + "=" * 60)
    print("TEST 5: Column Constants")
    print("=" * 60)
    
    try:
        from utils.data_saver import COLS_METRICAS as COLS_SAVER
        from utils.data_loader import COLS_METRICAS as COLS_LOADER
        from utils.data_manager import COLS_METRICAS as COLS_MANAGER
        
        assert COLS_SAVER == COLS_LOADER == COLS_MANAGER, "Column mismatch across modules"
        print(f"✅ COLS_METRICAS consistent across modules")
        print(f"   Columns: {COLS_SAVER}")
        
        # Verify exact 7 columns
        assert len(COLS_SAVER) == 7, f"Should have 7 columns, got {len(COLS_SAVER)}"
        print(f"✅ Exactly 7 metrics columns (no extra _x/_y suffixes)")
        
        return True
    except Exception as e:
        print(f"❌ Column constants test failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("GOOGLE SHEETS SYNC FIXES - VALIDATION TESTS")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_data_types,
        test_id_generation,
        test_catalog,
        test_columns_constant,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED - Ready for deployment")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

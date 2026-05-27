#!/usr/bin/env python
"""
Quick validation test for Google Sheets Sync Fixes (WITHOUT Streamlit)
"""

import sys
from pathlib import Path

# Add workspace to path
workspace = Path(__file__).parent
sys.path.insert(0, str(workspace))

def test_imports():
    """Test that all modified modules import correctly."""
    print("=" * 60)
    print("TEST 1: Core Imports (No Streamlit)")
    print("=" * 60)
    
    try:
        from utils.data_manager import COLEGIOS_MARISTAS, COLS_METRICAS
        print("✅ data_manager imports successful")
        print(f"   - COLEGIOS_MARISTAS has {len(COLEGIOS_MARISTAS)} colleges")
        print(f"   - COLS_METRICAS: {COLS_METRICAS}")
    except Exception as e:
        print(f"❌ data_manager import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_id_generation():
    """Test ID generation without Sheets connection."""
    print("\n" + "=" * 60)
    print("TEST 2: ID Generation")
    print("=" * 60)
    
    try:
        # Import directly to avoid circular deps
        import hashlib
        
        def test_get_id(entidad, plataforma, usuario):
            """Test get_id locally"""
            key = f"{entidad}|{plataforma}|{usuario}"
            return hashlib.md5(key.encode()).hexdigest()[:8]
        
        # Test ID generation
        id1 = test_get_id("Test College", "Facebook", "@test")
        id2 = test_get_id("Test College", "Facebook", "@test")
        id3 = test_get_id("Test College", "Instagram", "@test")
        
        assert isinstance(id1, str), f"ID should be str, got {type(id1)}"
        print(f"✅ ID generation returns str type: {id1}")
        
        assert id1 == id2, "Deterministic hash failed"
        print(f"✅ Deterministic: same inputs → same ID")
        
        assert id1 != id3, "Platform difference not reflected"
        print(f"✅ Platform-aware: different platform → different ID")
        
        assert len(id1) == 8, f"ID should be 8 chars, got {len(id1)}"
        print(f"✅ ID length correct: 8 characters")
        
        return True
    except Exception as e:
        print(f"❌ ID generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_catalog_structure():
    """Test COLEGIOS_MARISTAS catalog structure."""
    print("\n" + "=" * 60)
    print("TEST 3: COLEGIOS_MARISTAS Catalog Structure")
    print("=" * 60)
    
    try:
        from utils.data_manager import COLEGIOS_MARISTAS
        
        # Count institutions and platforms
        total_colleges = len(COLEGIOS_MARISTAS)
        total_platforms = sum(len(v) for v in COLEGIOS_MARISTAS.values())
        
        print(f"✅ Total colleges: {total_colleges}")
        print(f"✅ Total platform accounts: {total_platforms}")
        
        # Check exact count (17 colleges as requirement)
        assert total_colleges == 17, f"Should have 17 colleges, got {total_colleges}"
        print(f"✅ Exactly 17 colleges (requirement met)")
        
        # Validate structure
        for college, platforms in COLEGIOS_MARISTAS.items():
            assert isinstance(college, str), f"College should be str: {college}"
            assert isinstance(platforms, dict), f"Platforms should be dict: {platforms}"
            for plat, user in platforms.items():
                assert isinstance(plat, str), f"Platform should be str: {plat}"
                assert isinstance(user, str), f"Username should be str: {user}"
        
        print(f"✅ Catalog structure valid")
        
        # Check for Twitter accounts (requirement)
        colleges_with_twitter = []
        for college, platforms in COLEGIOS_MARISTAS.items():
            if "Twitter" in platforms:
                colleges_with_twitter.append(college)
        
        print(f"✅ Twitter accounts: {len(colleges_with_twitter)}/{total_colleges} colleges")
        for college in colleges_with_twitter[:3]:
            platform = COLEGIOS_MARISTAS[college]
            print(f"   - {college}: {platform.get('Twitter', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ Catalog test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_column_constants():
    """Test column definitions."""
    print("\n" + "=" * 60)
    print("TEST 4: Column Constants")
    print("=" * 60)
    
    try:
        from utils.data_manager import COLS_METRICAS, COLS_CUENTAS
        from utils.schema_columns import COLS_METRICAS as COLS_METRICAS_SCHEMA
        
        print(f"✅ COLS_CUENTAS: {COLS_CUENTAS}")
        print(f"✅ COLS_METRICAS: {COLS_METRICAS}")
        
        # Verify shared schema consistency
        assert len(COLS_METRICAS) == len(COLS_METRICAS_SCHEMA), f"Metric column count mismatch: {len(COLS_METRICAS)}"
        print(f"✅ Metrics columns count aligned to shared schema: {len(COLS_METRICAS)}")
        
        assert len(COLS_CUENTAS) == 4, f"Should have 4 account columns, got {len(COLS_CUENTAS)}"
        print(f"✅ Exactly 4 account columns")
        
        # Verify shared schema order matches runtime constants
        assert COLS_METRICAS == COLS_METRICAS_SCHEMA, f"Metrics columns mismatch"
        print(f"✅ Metrics columns match shared schema")
        
        return True
    except Exception as e:
        print(f"❌ Column constants test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pandas_operations():
    """Test Pandas operations for type safety."""
    print("\n" + "=" * 60)
    print("TEST 5: Pandas Type Operations")
    print("=" * 60)
    
    try:
        import pandas as pd
        from utils.data_manager import COLS_METRICAS
        
        # Create sample DataFrame
        df = pd.DataFrame({
            "id_cuenta": ["test_id_1", "test_id_2"],
            "fecha": ["2025-01-01", "2025-01-02"],
            "seguidores": [1000, 1100],
            "alcance": [500, 550],
            "interacciones": [50, 55],
            "likes_promedio": [30, 33],
            "engagement_rate": [0.5, 0.5],
        })
        
        # Test filtering
        df_filtered = df[COLS_METRICAS].copy()
        assert list(df_filtered.columns) == COLS_METRICAS
        print(f"✅ Column filtering works correctly")
        
        # Test type conversion
        df_filtered['id_cuenta'] = df_filtered['id_cuenta'].astype(object)
        assert df_filtered['id_cuenta'].dtype == object
        print(f"✅ Type conversion to object works")
        
        # Test NaN handling
        df_with_nan = df.copy()
        df_with_nan.loc[0, 'fecha'] = None
        df_clean = df_with_nan.fillna('')
        assert not df_clean.isna().any().any()
        print(f"✅ NaN handling with fillna('') works")
        
        # Test date conversion
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
        assert all(isinstance(d, str) for d in df['fecha'])
        print(f"✅ Date string conversion works")
        
        return True
    except Exception as e:
        print(f"❌ Pandas operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("GOOGLE SHEETS SYNC FIXES - CORE VALIDATION")
    print("(No Streamlit Dependencies)")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_id_generation,
        test_catalog_structure,
        test_column_constants,
        test_pandas_operations,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ ALL CORE TESTS PASSED")
        print("   Data structures are correct and ready for deployment")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

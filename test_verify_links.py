"""
Test Script: Verify Literal URL Implementation
================================================
Validates that all social media links are literal HTTPS URLs
and that ID generation works correctly with URLs instead of handles.
"""

import sys
import os

# Set up path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import only what we need, avoiding streamlit initialization
def test_all_urls_are_https():
    """Test 1: Verify all URLs start with https://"""
    print("=" * 70)
    print("TEST 1: Verify All URLs Start with https://")
    print("=" * 70)
    
    # Import here to avoid streamlit initialization
    try:
        from utils.data_manager import COLEGIOS_MARISTAS
    except Exception as e:
        print(f"[ERROR] Could not import COLEGIOS_MARISTAS: {e}")
        return False
    
    failed = []
    success_count = 0
    
    for institution, platforms in COLEGIOS_MARISTAS.items():
        for platform, url in platforms.items():
            if not isinstance(url, str) or not url.startswith("https://"):
                failed.append(f"  [FAIL] {institution} ({platform}): {url}")
            else:
                success_count += 1
    
    total = success_count + len(failed)
    print(f"\nResults: {success_count}/{total} URLs are valid HTTPS")
    
    if failed:
        print("\nFailed entries:")
        for item in failed:
            print(item)
        return False
    else:
        print("[PASS] ALL URLs are valid HTTPS links!")
        return True


def test_institution_count():
    """Test 2: Verify we have expected number of institutions"""
    print("\n" + "=" * 70)
    print("TEST 2: Verify Institution Count")
    print("=" * 70)
    
    count = len(COLEGIOS_MARISTAS)
    expected = 18
    
    print(f"\nTotal institutions: {count}")
    print(f"Expected: {expected}")
    
    if count >= expected:
        print(f"[PASS] Institution count is sufficient (>= {expected})")
        return True
    else:
        print(f"[FAIL] Institution count too low (< {expected})")
        return False


def test_platform_coverage():
    """Test 3: Verify platform coverage"""
    print("\n" + "=" * 70)
    print("TEST 3: Verify Platform Coverage")
    print("=" * 70)
    
    platforms = {}
    
    for institution, plat_dict in COLEGIOS_MARISTAS.items():
        for platform in plat_dict.keys():
            if platform not in platforms:
                platforms[platform] = []
            platforms[platform].append(institution)
    
    print(f"\nSupported platforms: {sorted(platforms.keys())}")
    
    for platform in sorted(platforms.keys()):
        count = len(platforms[platform])
        print(f"  • {platform}: {count} institutions")
    
    required_platforms = {"Facebook", "Instagram", "Twitter", "TikTok"}
    found_platforms = set(platforms.keys())
    missing = required_platforms - found_platforms
    
    if missing:
        print(f"\n[WARN] Missing platforms: {missing}")
        return False
    else:
        print(f"\n[PASS] All required platforms are present!")
        return True


def test_url_passthrough():
    """Test 4: Verify generate_social_url handles literal URLs"""
    print("\n" + "=" * 70)
    print("TEST 4: Verify URL Passthrough in generate_social_url")
    print("=" * 70)
    
    # Test with a literal URL
    test_url = "https://www.facebook.com/maristascum"
    result = generate_social_url("Facebook", test_url)
    
    print(f"\nInput URL: {test_url}")
    print(f"Output: {result}")
    
    if result == test_url:
        print("[PASS] URL passthrough working correctly!")
        return True
    else:
        print("[FAIL] URL passthrough failed!")
        return False


def test_id_generation_with_urls():
    """Test 5: Verify ID generation works with URLs"""
    print("\n" + "=" * 70)
    print("TEST 5: Verify ID Generation with URLs")
    print("=" * 70)
    
    test_cases = [
        ("Centro Universitario México", "Facebook", "https://www.facebook.com/maristascum"),
        ("Centro Universitario México", "Instagram", "https://www.instagram.com/maristas_cum/"),
    ]
    
    generated_ids = {}
    success = True
    
    for institution, platform, url in test_cases:
        try:
            id_val = get_id(institution, platform, url)
            generated_ids[(institution, platform)] = id_val
            print(f"\n[PASS] {institution} - {platform}")
            print(f"   ID: {id_val}")
        except Exception as e:
            print(f"\n[FAIL] {institution} - {platform}")
            print(f"   Error: {e}")
            success = False
    
    # Verify IDs are deterministic
    print("\n\nVerifying ID Determinism:")
    for institution, platform, url in test_cases:
        id_val_1 = get_id(institution, platform, url)
        id_val_2 = get_id(institution, platform, url)
        
        if id_val_1 == id_val_2:
            print(f"[PASS] {institution} - {platform}: Deterministic")
        else:
            print(f"[FAIL] {institution} - {platform}: Non-deterministic!")
            success = False
    
    return success


def test_real_data_with_urls():
    """Test 6: Verify URLs from COLEGIOS_MARISTAS work with generate_social_url"""
    print("\n" + "=" * 70)
    print("TEST 6: Real Data - URLs from COLEGIOS_MARISTAS")
    print("=" * 70)
    
    sample_count = 0
    failed = 0
    
    for institution, platforms in COLEGIOS_MARISTAS.items():
        for platform, url in list(platforms.items())[:2]:  # Sample 2 platforms per institution
            result = generate_social_url(platform, url)
            sample_count += 1
            
            if result == url:
                print(f"[PASS] {institution} - {platform}")
            else:
                print(f"[FAIL] {institution} - {platform}")
                print(f"   Expected: {url}")
                print(f"   Got: {result}")
                failed += 1
    
    print(f"\nResults: {sample_count - failed}/{sample_count} URLs handled correctly")
    return failed == 0


def main():
    """Run all tests"""
    print("\n")
    print("=" * 70)
    print("LITERAL URL IMPLEMENTATION TEST SUITE")
    print("=" * 70)
    
    results = {
        "Test 1: HTTPS Validation": test_all_urls_are_https(),
        "Test 2: Institution Count": test_institution_count(),
        "Test 3: Platform Coverage": test_platform_coverage(),
        "Test 4: URL Passthrough": test_url_passthrough(),
        "Test 5: ID Generation": test_id_generation_with_urls(),
        "Test 6: Real Data Integration": test_real_data_with_urls(),
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n[SUCCESS] ALL TESTS PASSED! Literal URL implementation is working correctly.")
        return 0
    else:
        print(f"\n[WARNING] {total_tests - total_passed} test(s) failed. Please review above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

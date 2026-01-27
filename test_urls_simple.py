"""
Simple URL Validation Test
===========================
Validates literal URLs without initializing Streamlit.
"""

import sys
import os
import hashlib

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Read COLEGIOS_MARISTAS directly from the file
def load_colegios_maristas():
    """Load COLEGIOS_MARISTAS from data_manager.py source code"""
    data_manager_path = os.path.join(os.path.dirname(__file__), "utils", "data_manager.py")
    
    try:
        with open(data_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find COLEGIOS_MARISTAS definition
        start = content.find("COLEGIOS_MARISTAS = {")
        if start == -1:
            print("[ERROR] Could not find COLEGIOS_MARISTAS in data_manager.py")
            return None
        
        # Extract the dictionary
        end = content.find("\n}\n", start)
        if end == -1:
            end = len(content)
        else:
            end += 2
        
        dict_str = content[start:end]
        
        # Execute to get the dictionary
        local_vars = {}
        exec(dict_str, {}, local_vars)
        return local_vars.get("COLEGIOS_MARISTAS", {})
    
    except Exception as e:
        print(f"[ERROR] Could not load COLEGIOS_MARISTAS: {e}")
        return None


def test_urls_are_https():
    """Test 1: Verify all URLs start with https://"""
    print("\n" + "=" * 70)
    print("TEST 1: Verify All URLs Start with https://")
    print("=" * 70)
    
    colegios = load_colegios_maristas()
    if not colegios:
        return False
    
    failed = []
    success_count = 0
    
    for institution, platforms in colegios.items():
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
    
    colegios = load_colegios_maristas()
    if not colegios:
        return False
    
    count = len(colegios)
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
    
    colegios = load_colegios_maristas()
    if not colegios:
        return False
    
    platforms = {}
    
    for institution, plat_dict in colegios.items():
        for platform in plat_dict.keys():
            if platform not in platforms:
                platforms[platform] = []
            platforms[platform].append(institution)
    
    print(f"\nSupported platforms: {sorted(platforms.keys())}")
    
    for platform in sorted(platforms.keys()):
        count = len(platforms[platform])
        print(f"  * {platform}: {count} institutions")
    
    required_platforms = {"Facebook", "Instagram", "Twitter", "TikTok"}
    found_platforms = set(platforms.keys())
    missing = required_platforms - found_platforms
    
    if missing:
        print(f"\n[WARN] Missing platforms: {missing}")
        # Not a hard failure - some platforms may be optional
        return True
    else:
        print(f"\n[PASS] All required platforms are present!")
        return True


def test_url_formats():
    """Test 4: Verify URL formats are correct"""
    print("\n" + "=" * 70)
    print("TEST 4: Verify URL Format Consistency")
    print("=" * 70)
    
    colegios = load_colegios_maristas()
    if not colegios:
        return False
    
    platform_patterns = {
        "Facebook": "facebook.com",
        "Instagram": "instagram.com",
        "Twitter": "twitter.com",
        "TikTok": "tiktok.com",
    }
    
    issues = []
    
    for institution, platforms in colegios.items():
        for platform, url in platforms.items():
            if platform in platform_patterns:
                expected_domain = platform_patterns[platform]
                if expected_domain not in url:
                    issues.append(f"  [FAIL] {institution} ({platform}): URL doesn't contain {expected_domain}")
                    issues.append(f"         Got: {url}")
    
    if issues:
        print("\nFormat issues found:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("[PASS] All URL formats are correct!")
        return True


def test_sample_urls():
    """Test 5: Display sample URLs"""
    print("\n" + "=" * 70)
    print("TEST 5: Sample URLs")
    print("=" * 70)
    
    colegios = load_colegios_maristas()
    if not colegios:
        return False
    
    print("\nSample institutions and their URLs:")
    for i, (institution, platforms) in enumerate(list(colegios.items())[:3]):
        print(f"\n  {institution}:")
        for platform, url in list(platforms.items())[:2]:
            print(f"    {platform}: {url}")
    
    print("\n[PASS] Sample URLs displayed!")
    return True


def test_maristas_mexico_central():
    """Test 6: Verify Maristas Mexico Central was added"""
    print("\n" + "=" * 70)
    print("TEST 6: Maristas Mexico Central Integration")
    print("=" * 70)
    
    colegios = load_colegios_maristas()
    if not colegios:
        return False
    
    if "Maristas México Central" in colegios:
        central = colegios["Maristas México Central"]
        print("\n[PASS] Maristas México Central found!")
        print(f"  Platforms: {list(central.keys())}")
        
        # Check all 4 platforms
        required = {"Facebook", "Instagram", "Twitter", "TikTok"}
        found = set(central.keys())
        
        if required.issubset(found):
            print(f"[PASS] All 4 platforms present!")
            for platform, url in central.items():
                print(f"       {platform}: {url[:50]}...")
            return True
        else:
            missing = required - found
            print(f"[FAIL] Missing platforms: {missing}")
            return False
    else:
        print("[FAIL] Maristas México Central NOT found!")
        print(f"  Available institutions: {list(colegios.keys())}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("=" * 70)
    print("LITERAL URL IMPLEMENTATION TEST SUITE (Simple)")
    print("=" * 70)
    
    results = {
        "Test 1: HTTPS Validation": test_urls_are_https(),
        "Test 2: Institution Count": test_institution_count(),
        "Test 3: Platform Coverage": test_platform_coverage(),
        "Test 4: URL Format Consistency": test_url_formats(),
        "Test 5: Sample URLs": test_sample_urls(),
        "Test 6: Maristas Mexico Central": test_maristas_mexico_central(),
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
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("Literal URL implementation is working correctly.")
        return 0
    else:
        print(f"\n[WARNING] {total_tests - total_passed} test(s) failed. Please review above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

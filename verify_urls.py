#!/usr/bin/env python3
"""
Direct URL Validation - Final Version
======================================
Tests literal URLs in COLEGIOS_MARISTAS
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run validation tests."""
    
    print("=" * 70)
    print("LITERAL URL VALIDATION TEST")
    print("=" * 70)
    print()
    
    # Import dynamically to avoid full Streamlit initialization
    try:
        # Suppress warnings
        import warnings
        warnings.filterwarnings("ignore")
        
        # Import the dictionary
        from utils.data_manager import COLEGIOS_MARISTAS
        
        print(f"[SUCCESS] Loaded COLEGIOS_MARISTAS: {len(COLEGIOS_MARISTAS)} institutions\n")
    
    except ImportError as e:
        print(f"[ERROR] Could not import COLEGIOS_MARISTAS: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return 1
    
    # Test 1: All URLs are HTTPS
    print("=" * 70)
    print("TEST 1: HTTPS URL Validation")
    print("=" * 70)
    
    non_https = []
    for inst, platforms in COLEGIOS_MARISTAS.items():
        for plat, url in platforms.items():
            if not str(url).startswith("https://"):
                non_https.append(f"  [FAIL] {inst} ({plat}): {url}")
    
    total_urls = sum(len(p) for p in COLEGIOS_MARISTAS.values())
    https_urls = total_urls - len(non_https)
    
    print(f"\nResult: {https_urls}/{total_urls} URLs are HTTPS")
    
    if non_https:
        print("\nNon-HTTPS URLs found:")
        for item in non_https[:10]:  # Show first 10
            print(item)
        if len(non_https) > 10:
            print(f"  ... and {len(non_https) - 10} more")
        print(f"\n[FAIL] {len(non_https)} URLs are not HTTPS\n")
        test1_pass = False
    else:
        print("[PASS] All URLs are HTTPS!\n")
        test1_pass = True
    
    # Test 2: Institution count
    print("=" * 70)
    print("TEST 2: Institution Count (Expected: 18)")
    print("=" * 70)
    
    count = len(COLEGIOS_MARISTAS)
    print(f"\nFound: {count} institutions")
    if count >= 18:
        print("[PASS] Institution count is sufficient\n")
        test2_pass = True
    else:
        print(f"[FAIL] Expected at least 18, got {count}\n")
        test2_pass = False
    
    # Test 3: Platform coverage
    print("=" * 70)
    print("TEST 3: Platform Coverage")
    print("=" * 70)
    
    platforms_found = set()
    platform_counts = {}
    
    for platforms in COLEGIOS_MARISTAS.values():
        for plat in platforms.keys():
            platforms_found.add(plat)
            platform_counts[plat] = platform_counts.get(plat, 0) + 1
    
    print(f"\nPlatforms found: {sorted(platforms_found)}")
    print("\nPlatform distribution:")
    for plat in sorted(platform_counts.keys()):
        print(f"  {plat}: {platform_counts[plat]} institutions")
    
    required = {"Facebook", "Instagram", "Twitter", "TikTok"}
    has_required = required.issubset(platforms_found)
    
    if has_required:
        print("\n[PASS] All required platforms present\n")
        test3_pass = True
    else:
        missing = required - platforms_found
        print(f"\n[FAIL] Missing platforms: {missing}\n")
        test3_pass = False
    
    # Test 4: Maristas Mexico Central
    print("=" * 70)
    print("TEST 4: Maristas México Central Integration")
    print("=" * 70)
    
    if "Maristas México Central" in COLEGIOS_MARISTAS:
        central = COLEGIOS_MARISTAS["Maristas México Central"]
        print(f"\n[SUCCESS] Found: Maristas México Central")
        print(f"Platforms: {sorted(central.keys())}")
        
        central_required = {"Facebook", "Instagram", "Twitter", "TikTok"}
        has_all = central_required.issubset(set(central.keys()))
        
        if has_all:
            print("[PASS] Has all 4 required platforms")
            print("\nURLs:")
            for plat in sorted(central.keys()):
                url = central[plat]
                print(f"  {plat:12s}: {url}")
            print()
            test4_pass = True
        else:
            missing = central_required - set(central.keys())
            print(f"[FAIL] Missing platforms: {missing}\n")
            test4_pass = False
    else:
        print("\n[FAIL] Maristas México Central not found")
        print(f"Available institutions: {sorted(COLEGIOS_MARISTAS.keys())}\n")
        test4_pass = False
    
    # Test 5: URL format consistency
    print("=" * 70)
    print("TEST 5: URL Format Consistency")
    print("=" * 70)
    
    format_issues = []
    
    platform_domains = {
        "Facebook": "facebook.com",
        "Instagram": "instagram.com",
        "Twitter": ("twitter.com", "x.com"),  # Twitter may use either domain
        "TikTok": "tiktok.com",
    }
    
    for inst, platforms in COLEGIOS_MARISTAS.items():
        for plat, url in platforms.items():
            if plat in platform_domains:
                expected = platform_domains[plat]
                if isinstance(expected, tuple):
                    # Multiple valid domains
                    if not any(domain in url for domain in expected):
                        format_issues.append(f"  {inst} ({plat}): {url}")
                else:
                    # Single domain
                    if expected not in url:
                        format_issues.append(f"  {inst} ({plat}): {url}")
    
    if format_issues:
        print("\nFormat issues found:")
        for issue in format_issues[:5]:
            print(issue)
        if len(format_issues) > 5:
            print(f"  ... and {len(format_issues) - 5} more")
        print(f"\n[FAIL] {len(format_issues)} URL format issue(s)\n")
        test5_pass = False
    else:
        print("\n[PASS] All URL formats are correct!\n")
        test5_pass = True
    
    # Test 6: Sample URLs
    print("=" * 70)
    print("TEST 6: Sample URLs Display")
    print("=" * 70)
    
    print("\nShowing first 3 institutions:")
    for inst_name in list(COLEGIOS_MARISTAS.keys())[:3]:
        platforms = COLEGIOS_MARISTAS[inst_name]
        print(f"\n{inst_name}:")
        for plat in sorted(platforms.keys())[:3]:  # Show up to 3 platforms
            url = platforms[plat]
            print(f"  {plat:12s}: {url}")
    
    print("\n[PASS] Sample URLs displayed\n")
    test6_pass = True
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()
    
    tests = [
        ("Test 1: HTTPS URLs", test1_pass),
        ("Test 2: Institution Count", test2_pass),
        ("Test 3: Platform Coverage", test3_pass),
        ("Test 4: Maristas Mexico Central", test4_pass),
        ("Test 5: URL Format Consistency", test5_pass),
        ("Test 6: Sample URLs Display", test6_pass),
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for name, result in tests:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "=" * 70)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("Literal URL implementation is working correctly.")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print(f"[WARNING] {total - passed} test(s) failed.")
        print("Please review the failures above.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Test execution cancelled by user.")
        exit_code = 130
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1
    
    sys.exit(exit_code)

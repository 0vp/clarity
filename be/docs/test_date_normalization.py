"""
Test date normalization to ensure all formats convert to MM-DD-YYYY
"""

from scraper.scraper import _normalize_date_format

print("=" * 80)
print("TESTING DATE NORMALIZATION")
print("=" * 80)

test_cases = [
    # (input, expected_output, description)
    ("2025-11-15", "11-15-2025", "YYYY-MM-DD format"),
    ("11-15-2025", "11-15-2025", "Already correct MM-DD-YYYY"),
    ("11/15/2025", "11-15-2025", "MM/DD/YYYY with slashes"),
    ("November 15, 2025", "11-15-2025", "Full month name"),
    ("Nov 15, 2025", "11-15-2025", "Abbreviated month name"),
    ("2025-11-15T10:30:00", "11-15-2025", "ISO format with time"),
    ("2025-11-15 10:30:00", "11-15-2025", "SQL datetime format"),
]

print("\nRunning test cases...\n")

passed = 0
failed = 0

for input_date, expected, description in test_cases:
    result = _normalize_date_format(input_date)
    
    if result == expected:
        print(f"✅ PASS: {description}")
        print(f"   Input:    '{input_date}'")
        print(f"   Expected: '{expected}'")
        print(f"   Got:      '{result}'")
        passed += 1
    else:
        print(f"❌ FAIL: {description}")
        print(f"   Input:    '{input_date}'")
        print(f"   Expected: '{expected}'")
        print(f"   Got:      '{result}'")
        failed += 1
    print()

print("=" * 80)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("=" * 80)

if failed == 0:
    print("\n✅ All date normalization tests PASSED!")
else:
    print(f"\n❌ {failed} tests FAILED!")
    exit(1)

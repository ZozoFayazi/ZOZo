#!/usr/bin/env python3
"""
Upselling System - Unit Test
Tests that upsell data loads and API returns 200
"""

import requests
import json

backend_url = "http://localhost:8001"

print("="*80)
print("UPSELLING SYSTEM - UNIT TEST")
print("="*80)
print()

tests_passed = 0
tests_total = 0

# Test 1: Burger Single (Medium)
tests_total += 1
print("Test 1: Burger Single (Medium)")
print("-"*80)

response = requests.post(
    f"{backend_url}/api/upsells/recommendations",
    json={"product_type": "burger", "is_menu": False, "size": "medium"}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    categories = data.get("categories", [])
    print(f"Categories: {len(categories)}")
    print(f"✅ Test 1 PASSED - {len(categories)} categories returned")
    tests_passed += 1
    
    # Validate structure
    for cat in categories:
        print(f"  - {cat['id']}: {cat['headline']}")
else:
    print(f"❌ Test 1 FAILED - Expected 200, got {response.status_code}")

print()

# Test 2: Burger Menu
tests_total += 1
print("Test 2: Burger Menu")
print("-"*80)

response = requests.post(
    f"{backend_url}/api/upsells/recommendations",
    json={"product_type": "burger", "is_menu": True}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    categories = data.get("categories", [])
    print(f"Categories: {len(categories)}")
    
    # Check for expected categories
    category_ids = [c['id'] for c in categories]
    expected = ['side-swap', 'extra-sidekick', 'dips', 'drinks', 'dessert']
    
    if all(exp in category_ids for exp in expected):
        print(f"✅ Test 2 PASSED - All expected categories present")
        tests_passed += 1
    else:
        print(f"❌ Test 2 FAILED - Missing categories")
        print(f"   Expected: {expected}")
        print(f"   Got: {category_ids}")
else:
    print(f"❌ Test 2 FAILED - Expected 200, got {response.status_code}")

print()

# Test 3: Pizza
tests_total += 1
print("Test 3: Pizza")
print("-"*80)

response = requests.post(
    f"{backend_url}/api/upsells/recommendations",
    json={"product_type": "pizza", "is_menu": False}
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    categories = data.get("categories", [])
    print(f"Categories: {len(categories)}")
    
    # Should have dips, drinks, dessert
    if len(categories) == 3:
        print(f"✅ Test 3 PASSED - Correct number of categories")
        tests_passed += 1
    else:
        print(f"❌ Test 3 FAILED - Expected 3 categories, got {len(categories)}")
else:
    print(f"❌ Test 3 FAILED - Expected 200, got {response.status_code}")

print()
print("="*80)
print("SUMMARY")
print("="*80)
print(f"Tests Passed: {tests_passed}/{tests_total}")
print()

if tests_passed == tests_total:
    print("✅ ALL TESTS PASSED!")
    print("Upselling System is ready!")
else:
    print(f"❌ {tests_total - tests_passed} tests failed")

print()

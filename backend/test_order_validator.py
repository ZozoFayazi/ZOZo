"""
Test Script for Order Validator
Run this to test order validation before sending to ExpertOrder
"""

import asyncio
import sys
sys.path.insert(0, '/app/backend')

from order_validator import OrderValidator, OrderAutoConverter


def test_validator():
    print("=" * 70)
    print("ORDER VALIDATOR - TEST SUITE")
    print("=" * 70)
    print()
    
    # Test 1: WRONG FORMAT (all in customizations)
    print("TEST 1: Falsches Format (alles in customizations)")
    print("-" * 70)
    
    wrong_order = {
        "order_id": "TEST-123",
        "customer_name": "Test",
        "location_id": "rellingen",
        "total": 10.0,
        "items": [
            {
                "name": "Burger Menü",
                "price": 12.90,
                "customizations": [
                    "+ Brioche Brötchen",
                    "+ Pommes Frites",      # WRONG: Should be in modifiers.beilage
                    "+ Cola",               # WRONG: Should be in modifiers.getraenk
                    "+ Ketchup",            # WRONG: Should be in modifiers.sauce
                    "- Ohne Gurken"         # WRONG: Should be in removed_ingredients
                ]
            }
        ]
    }
    
    result = OrderValidator.get_validation_report(wrong_order)
    print(f"Valid: {result['valid']}")
    print(f"Errors: {result['error_count']}")
    for error in result['errors']:
        print(f"  ❌ {error}")
    
    # Test Auto-Conversion
    print("\n🔄 Testing Auto-Conversion...")
    converted, fixes = OrderAutoConverter.convert_order(wrong_order)
    
    if fixes:
        print("✅ Fixes applied:")
        for fix in fixes:
            print(f"  - {fix}")
        
        # Revalidate
        revalidation = OrderValidator.get_validation_report(converted)
        print(f"\nAfter conversion:")
        print(f"  Valid: {revalidation['valid']}")
        print(f"  Errors: {revalidation['error_count']}")
    
    print()
    
    # Test 2: CORRECT FORMAT
    print("TEST 2: Korrektes Format")
    print("-" * 70)
    
    correct_order = {
        "order_id": "TEST-456",
        "customer_name": "Test",
        "location_id": "rellingen",
        "total": 10.0,
        "items": [
            {
                "name": "Burger Menü",
                "size": "medium",
                "price": 12.90,
                "customizations": ["+ Brioche Brötchen"],
                "removed_ingredients": ["Gurken"],
                "extras": [{"name": "Extra Bacon", "price": 0.0}],
                "modifiers": {
                    "beilage": {"name": "Pommes Frites", "price": 0.0},
                    "getraenk": {"name": "Cola", "price": 0.0},
                    "sauce": {"name": "Ketchup", "price": 0.0}
                }
            }
        ]
    }
    
    result = OrderValidator.get_validation_report(correct_order)
    print(f"Valid: {result['valid']}")
    print(f"Message: {result['message']}")
    
    if result['valid']:
        print("✅ Kein Auto-Conversion nötig!")
    
    print()
    print("=" * 70)
    print("✅ TESTS ABGESCHLOSSEN")
    print("=" * 70)


if __name__ == "__main__":
    test_validator()

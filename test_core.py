"""
POC Test Script for ZOZO Burger Multi-Location Ordering System
Tests all core functionality before building the full application
"""
import requests
import json
from datetime import datetime

# Backend URL
BASE_URL = "http://localhost:8001/api"

print("\n" + "=" * 70)
print("🧪 ZOZO BURGER MULTI-LOCATION ORDERING SYSTEM - POC TEST")
print("=" * 70)

# Test Results
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(name, passed, message=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status}: {name}")
    if message:
        print(f"   {message}")
    
    test_results["tests"].append({
        "name": name,
        "passed": passed,
        "message": message
    })
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def print_summary():
    """Print test summary"""
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {test_results['passed'] + test_results['failed']}")
    print(f"Passed: ✅ {test_results['passed']}")
    print(f"Failed: ❌ {test_results['failed']}")
    
    if test_results['failed'] > 0:
        print("\n❌ FAILED TESTS:")
        for test in test_results["tests"]:
            if not test["passed"]:
                print(f"   - {test['name']}: {test['message']}")
    
    print("\n" + "=" * 70)
    if test_results['failed'] == 0:
        print("🎉 ALL TESTS PASSED! Core functionality is working.")
        print("=" * 70 + "\n")
        return True
    else:
        print("⚠️  SOME TESTS FAILED. Fix issues before proceeding.")
        print("=" * 70 + "\n")
        return False

# ============================================================================
# TEST 1: Get Locations
# ============================================================================
print("\n" + "-" * 70)
print("TEST 1: Fetch All Locations")
print("-" * 70)

try:
    response = requests.get(f"{BASE_URL}/locations")
    locations = response.json()
    
    if response.status_code == 200 and len(locations) == 2:
        log_test(
            "Fetch Locations",
            True,
            f"Retrieved {len(locations)} locations: {locations[0]['name']}, {locations[1]['name']}"
        )
        
        # Store location IDs for later tests
        location_rellingen = locations[0]
        location_henstedt = locations[1]
        
        print(f"\n📍 Location 1: {location_rellingen['name']}")
        print(f"   Address: {location_rellingen['address']}, {location_rellingen['city']}")
        print(f"   ID: {location_rellingen['id']}")
        
        print(f"\n📍 Location 2: {location_henstedt['name']}")
        print(f"   Address: {location_henstedt['address']}, {location_henstedt['city']}")
        print(f"   ID: {location_henstedt['id']}")
    else:
        log_test(
            "Fetch Locations",
            False,
            f"Expected 2 locations, got {len(locations) if response.status_code == 200 else 'error'}"
        )
        print(f"Response: {response.text}")
        exit(1)
        
except Exception as e:
    log_test("Fetch Locations", False, str(e))
    print(f"Error: {e}")
    exit(1)

# ============================================================================
# TEST 2: Get Menu for Rellingen
# ============================================================================
print("\n" + "-" * 70)
print("TEST 2: Fetch Menu for Rellingen Location")
print("-" * 70)

try:
    response = requests.get(f"{BASE_URL}/menu", params={"location_id": location_rellingen['id']})
    menu_rellingen = response.json()
    
    if response.status_code == 200 and len(menu_rellingen) > 0:
        total_items = sum(len(cat['items']) for cat in menu_rellingen)
        log_test(
            "Fetch Menu - Rellingen",
            True,
            f"Retrieved {len(menu_rellingen)} categories with {total_items} items"
        )
        
        print(f"\n🍔 Menu Categories for {location_rellingen['name']}:")
        for cat in menu_rellingen:
            print(f"   - {cat['name']}: {len(cat['items'])} items")
    else:
        log_test(
            "Fetch Menu - Rellingen",
            False,
            f"Failed to fetch menu: {response.status_code}"
        )
        print(f"Response: {response.text}")
        exit(1)
        
except Exception as e:
    log_test("Fetch Menu - Rellingen", False, str(e))
    print(f"Error: {e}")
    exit(1)

# ============================================================================
# TEST 3: Get Menu for Henstedt-Ulzburg (Should be same as both have same menu)
# ============================================================================
print("\n" + "-" * 70)
print("TEST 3: Fetch Menu for Henstedt-Ulzburg Location")
print("-" * 70)

try:
    response = requests.get(f"{BASE_URL}/menu", params={"location_id": location_henstedt['id']})
    menu_henstedt = response.json()
    
    if response.status_code == 200 and len(menu_henstedt) > 0:
        total_items = sum(len(cat['items']) for cat in menu_henstedt)
        log_test(
            "Fetch Menu - Henstedt-Ulzburg",
            True,
            f"Retrieved {len(menu_henstedt)} categories with {total_items} items"
        )
        
        print(f"\n🍔 Menu Categories for {location_henstedt['name']}:")
        for cat in menu_henstedt:
            print(f"   - {cat['name']}: {len(cat['items'])} items")
    else:
        log_test(
            "Fetch Menu - Henstedt-Ulzburg",
            False,
            f"Failed to fetch menu: {response.status_code}"
        )
        print(f"Response: {response.text}")
        exit(1)
        
except Exception as e:
    log_test("Fetch Menu - Henstedt-Ulzburg", False, str(e))
    print(f"Error: {e}")
    exit(1)

# ============================================================================
# TEST 4: Create Order for Rellingen
# ============================================================================
print("\n" + "-" * 70)
print("TEST 4: Create Order for Rellingen Location")
print("-" * 70)

# Select some items from the menu
burger_item = menu_rellingen[0]['items'][0]  # First burger
drink_item = None
for cat in menu_rellingen:
    if cat['slug'] == 'drinks':
        drink_item = cat['items'][0]
        break

if not drink_item:
    # Fallback to second category first item
    drink_item = menu_rellingen[1]['items'][0] if len(menu_rellingen) > 1 else burger_item

print(f"\n🛒 Creating order with:")
print(f"   - {burger_item['name']}: €{burger_item.get('price_medium', burger_item.get('price_normal', 0))}")
print(f"   - {drink_item['name']}: €{drink_item.get('price_normal', drink_item.get('price_medium', 0))}")

try:
    order_data = {
        "location_id": location_rellingen['id'],
        "items": [
            {
                "menu_item_id": burger_item['id'],
                "name": burger_item['name'],
                "price": burger_item.get('price_medium', burger_item.get('price_normal', 0)),
                "size": "medium" if burger_item.get('price_medium') else None,
                "quantity": 1
            },
            {
                "menu_item_id": drink_item['id'],
                "name": drink_item['name'],
                "price": drink_item.get('price_normal', drink_item.get('price_medium', 0)),
                "quantity": 2
            }
        ],
        "customer": {
            "name": "Max Mustermann",
            "phone": "+49 123 456789",
            "address": "Teststraße 123",
            "postal_code": "25462",
            "city": "Rellingen",
            "notes": "Bitte klingeln"
        },
        "payment_method": "cash"
    }
    
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    order_rellingen = response.json()
    
    if response.status_code == 200 and order_rellingen.get('order_number'):
        # Verify calculations
        expected_subtotal = sum(item['price'] * item['quantity'] for item in order_data['items'])
        expected_delivery = 2.50 if expected_subtotal < 15 else 0.0
        expected_total = expected_subtotal + expected_delivery
        
        actual_subtotal = order_rellingen['subtotal']
        actual_total = order_rellingen['total']
        
        calculations_correct = (
            abs(actual_subtotal - expected_subtotal) < 0.01 and
            abs(actual_total - expected_total) < 0.01
        )
        
        if calculations_correct:
            log_test(
                "Create Order - Rellingen",
                True,
                f"Order {order_rellingen['order_number']} created with correct totals (€{actual_total:.2f})"
            )
            
            print(f"\n📦 Order Created Successfully!")
            print(f"   Order Number: {order_rellingen['order_number']}")
            print(f"   Subtotal: €{order_rellingen['subtotal']:.2f}")
            print(f"   Delivery Fee: €{order_rellingen['delivery_fee']:.2f}")
            print(f"   Total: €{order_rellingen['total']:.2f}")
            print(f"   Status: {order_rellingen['status']}")
        else:
            log_test(
                "Create Order - Rellingen",
                False,
                f"Total calculation mismatch. Expected: €{expected_total:.2f}, Got: €{actual_total:.2f}"
            )
    else:
        log_test(
            "Create Order - Rellingen",
            False,
            f"Failed to create order: {response.status_code}"
        )
        print(f"Response: {response.text}")
        exit(1)
        
except Exception as e:
    log_test("Create Order - Rellingen", False, str(e))
    print(f"Error: {e}")
    exit(1)

# ============================================================================
# TEST 5: Create Order for Henstedt-Ulzburg
# ============================================================================
print("\n" + "-" * 70)
print("TEST 5: Create Order for Henstedt-Ulzburg Location")
print("-" * 70)

pizza_item = None
for cat in menu_henstedt:
    if cat['slug'] == 'pizza':
        pizza_item = cat['items'][0]
        break

if not pizza_item:
    pizza_item = menu_henstedt[0]['items'][1] if len(menu_henstedt[0]['items']) > 1 else menu_henstedt[0]['items'][0]

print(f"\n🛒 Creating order with:")
print(f"   - {pizza_item['name']}: €{pizza_item.get('price_medium', pizza_item.get('price_normal', 0))}")

try:
    order_data = {
        "location_id": location_henstedt['id'],
        "items": [
            {
                "menu_item_id": pizza_item['id'],
                "name": pizza_item['name'],
                "price": pizza_item.get('price_medium', pizza_item.get('price_normal', 0)),
                "size": "medium" if pizza_item.get('price_medium') else None,
                "quantity": 1
            }
        ],
        "customer": {
            "name": "Anna Schmidt",
            "phone": "+49 987 654321",
            "address": "Hauptstraße 456",
            "postal_code": "24558",
            "city": "Henstedt-Ulzburg"
        },
        "payment_method": "card"
    }
    
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    order_henstedt = response.json()
    
    if response.status_code == 200 and order_henstedt.get('order_number'):
        log_test(
            "Create Order - Henstedt-Ulzburg",
            True,
            f"Order {order_henstedt['order_number']} created (€{order_henstedt['total']:.2f})"
        )
        
        print(f"\n📦 Order Created Successfully!")
        print(f"   Order Number: {order_henstedt['order_number']}")
        print(f"   Total: €{order_henstedt['total']:.2f}")
        print(f"   Status: {order_henstedt['status']}")
    else:
        log_test(
            "Create Order - Henstedt-Ulzburg",
            False,
            f"Failed to create order: {response.status_code}"
        )
        print(f"Response: {response.text}")
        exit(1)
        
except Exception as e:
    log_test("Create Order - Henstedt-Ulzburg", False, str(e))
    print(f"Error: {e}")
    exit(1)

# ============================================================================
# TEST 6: Get Orders for Rellingen (Admin)
# ============================================================================
print("\n" + "-" * 70)
print("TEST 6: Fetch Orders for Rellingen Location (Admin)")
print("-" * 70)

try:
    response = requests.get(
        f"{BASE_URL}/admin/orders",
        params={"location_id": location_rellingen['id'], "token": "POC_TOKEN"}
    )
    orders_rellingen = response.json()
    
    if response.status_code == 200:
        # Should have at least 1 order (the one we just created)
        if len(orders_rellingen) >= 1:
            # Verify location isolation - all orders should be for Rellingen
            all_correct_location = all(
                order['location_id'] == location_rellingen['id'] 
                for order in orders_rellingen
            )
            
            if all_correct_location:
                log_test(
                    "Fetch Orders - Rellingen (Location Isolation)",
                    True,
                    f"Retrieved {len(orders_rellingen)} orders, all for correct location"
                )
                
                print(f"\n📋 Orders for {location_rellingen['name']}:")
                for order in orders_rellingen:
                    print(f"   - {order['order_number']}: €{order['total']:.2f} ({order['status']})")
            else:
                log_test(
                    "Fetch Orders - Rellingen (Location Isolation)",
                    False,
                    "Location isolation broken - found orders from other locations"
                )
        else:
            log_test(
                "Fetch Orders - Rellingen",
                False,
                f"Expected at least 1 order, got {len(orders_rellingen)}"
            )
    else:
        log_test(
            "Fetch Orders - Rellingen",
            False,
            f"Failed to fetch orders: {response.status_code}"
        )
        print(f"Response: {response.text}")
        
except Exception as e:
    log_test("Fetch Orders - Rellingen", False, str(e))
    print(f"Error: {e}")

# ============================================================================
# TEST 7: Get Orders for Henstedt-Ulzburg (Admin)
# ============================================================================
print("\n" + "-" * 70)
print("TEST 7: Fetch Orders for Henstedt-Ulzburg Location (Admin)")
print("-" * 70)

try:
    response = requests.get(
        f"{BASE_URL}/admin/orders",
        params={"location_id": location_henstedt['id'], "token": "POC_TOKEN"}
    )
    orders_henstedt = response.json()
    
    if response.status_code == 200:
        if len(orders_henstedt) >= 1:
            all_correct_location = all(
                order['location_id'] == location_henstedt['id'] 
                for order in orders_henstedt
            )
            
            if all_correct_location:
                log_test(
                    "Fetch Orders - Henstedt (Location Isolation)",
                    True,
                    f"Retrieved {len(orders_henstedt)} orders, all for correct location"
                )
                
                print(f"\n📋 Orders for {location_henstedt['name']}:")
                for order in orders_henstedt:
                    print(f"   - {order['order_number']}: €{order['total']:.2f} ({order['status']})")
            else:
                log_test(
                    "Fetch Orders - Henstedt (Location Isolation)",
                    False,
                    "Location isolation broken - found orders from other locations"
                )
        else:
            log_test(
                "Fetch Orders - Henstedt",
                False,
                f"Expected at least 1 order, got {len(orders_henstedt)}"
            )
    else:
        log_test(
            "Fetch Orders - Henstedt",
            False,
            f"Failed to fetch orders: {response.status_code}"
        )
        print(f"Response: {response.text}")
        
except Exception as e:
    log_test("Fetch Orders - Henstedt", False, str(e))
    print(f"Error: {e}")

# ============================================================================
# TEST 8: Update Order Status (Admin)
# ============================================================================
print("\n" + "-" * 70)
print("TEST 8: Update Order Status")
print("-" * 70)

try:
    # Update the Rellingen order to "accepted"
    response = requests.patch(
        f"{BASE_URL}/admin/orders/{order_rellingen['id']}/status",
        params={"token": "POC_TOKEN"},
        json={"status": "accepted"}
    )
    
    if response.status_code == 200:
        updated_order = response.json()
        if updated_order['status'] == "accepted":
            log_test(
                "Update Order Status",
                True,
                f"Order {order_rellingen['order_number']} status updated to 'accepted'"
            )
            
            print(f"\n✅ Order status updated:")
            print(f"   Order: {updated_order['order_number']}")
            print(f"   New Status: {updated_order['status']}")
        else:
            log_test(
                "Update Order Status",
                False,
                f"Status not updated correctly. Expected 'accepted', got '{updated_order['status']}'"
            )
    else:
        log_test(
            "Update Order Status",
            False,
            f"Failed to update status: {response.status_code}"
        )
        print(f"Response: {response.text}")
        
except Exception as e:
    log_test("Update Order Status", False, str(e))
    print(f"Error: {e}")

# ============================================================================
# Print Final Summary
# ============================================================================
success = print_summary()

if success:
    print("✅ POC VALIDATED: All core functionality is working correctly!")
    print("   - Multi-location support: ✅")
    print("   - Location-specific menus: ✅")
    print("   - Order creation with correct totals: ✅")
    print("   - Location isolation (no cross-location data leakage): ✅")
    print("   - Order management (status updates): ✅")
    print("\n🚀 Ready to proceed with full application development!\n")
    exit(0)
else:
    print("❌ POC FAILED: Please fix the issues above before proceeding.\n")
    exit(1)

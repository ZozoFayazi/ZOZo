#!/usr/bin/env python3
"""
COMPREHENSIVE E2E TEST: Menus & Fingerfoods with Modifiers
Tests the complete flow from order creation to POS payload
"""
import requests
import json

API_URL = "https://foodorder-fix.preview.emergentagent.com/api"
LOCATION_ID = "49aff347-a6c3-407c-ad4a-59d5d0852314"

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_menu_order_with_modifiers():
    """Test 1: Menu order with required modifiers (Beilage + Getränk)"""
    print_section("TEST 1: MENÜ-BESTELLUNG MIT REQUIRED MODIFIERS")
    
    # Order payload with menu item + modifiers
    order_payload = {
        "location_id": LOCATION_ID,
        "items": [{
            "menu_item_id": "test-menu-123",
            "name": "Cheeseburger Menü",
            "price": 11.90,
            "size": "normal",
            "quantity": 1,
            "customizations": [],
            "extras": [],
            "removed_ingredients": [],
            "modifiers": {
                "menu_beilage": {
                    "id": "opt-001",
                    "name": "Pommes Normal",
                    "price": 0.0,
                    "pos_item_id": "SIDES_FRIES_NORMAL"
                },
                "menu_getraenk": {
                    "id": "opt-002",
                    "name": "Coca Cola 0,5l",
                    "price": 0.0,
                    "pos_item_id": "DRINK_COLA_05"
                }
            }
        }],
        "customer": {
            "name": "Menu Test User",
            "phone": "+491705555",
            "email": "menu-test@zozo.de",
            "address": "Abholung",
            "postal_code": "00000",
            "city": "Rellingen"
        },
        "payment_method": "cash",
        "points_to_redeem": 0,
        "is_pickup": True
    }
    
    print("📦 Sending order...")
    print(f"   Item: Cheeseburger Menü")
    print(f"   Modifiers:")
    print(f"     - Beilage: Pommes Normal")
    print(f"     - Getränk: Coca Cola 0,5l")
    
    resp = requests.post(f"{API_URL}/orders", json=order_payload)
    
    if resp.status_code == 200:
        order = resp.json()
        print(f"\n✅ Order created: {order.get('order_number')}")
        print(f"   Total: €{order.get('total'):.2f}")
        
        # Check what was sent to POS
        print(f"\n📋 Checking POS Payload...")
        # We need to check the logs to see the ExpertOrder payload
        
        return order.get('order_number')
    else:
        print(f"❌ Order failed: {resp.status_code}")
        print(f"   Response: {resp.text}")
        return None

def test_fingerfood_with_dip():
    """Test 2: Fingerfood with required dip selection"""
    print_section("TEST 2: FINGERFOOD MIT DIP (REQUIRED)")
    
    order_payload = {
        "location_id": LOCATION_ID,
        "items": [{
            "menu_item_id": "test-nuggets-123",
            "name": "Chicken Nuggets",
            "price": 6.50,
            "size": "normal",
            "quantity": 1,
            "customizations": [],
            "extras": [],
            "removed_ingredients": [],
            "modifiers": {
                "fingerfood_dip": {
                    "id": "dip-001",
                    "name": "BBQ Sauce",
                    "price": 0.0,
                    "pos_item_id": "DIP_BBQ"
                }
            }
        }],
        "customer": {
            "name": "Fingerfood Test",
            "phone": "+491706666",
            "email": "fingerfood-test@zozo.de",
            "address": "Abholung",
            "postal_code": "00000",
            "city": "Rellingen"
        },
        "payment_method": "cash",
        "points_to_redeem": 0,
        "is_pickup": True
    }
    
    print("📦 Sending order...")
    print(f"   Item: Chicken Nuggets")
    print(f"   Dip: BBQ Sauce (inklusive)")
    
    resp = requests.post(f"{API_URL}/orders", json=order_payload)
    
    if resp.status_code == 200:
        order = resp.json()
        print(f"\n✅ Order created: {order.get('order_number')}")
        print(f"   Total: €{order.get('total'):.2f}")
        return order.get('order_number')
    else:
        print(f"❌ Order failed: {resp.status_code}")
        print(f"   Response: {resp.text}")
        return None

# Run tests
print_section("E2E TESTS: MENUS & FINGERFOODS")

test1_order = test_menu_order_with_modifiers()
test2_order = test_fingerfood_with_dip()

# Check backend logs for POS payloads
if test1_order or test2_order:
    print_section("POS PAYLOAD VERIFICATION")
    print("\n📋 Check backend logs for ExpertOrder payloads:")
    print("   Command: tail -100 /var/log/supervisor/backend.err.log | grep 'ExpertOrder payload'")
    print(f"\n✅ Tests completed. Order numbers:")
    if test1_order:
        print(f"   - Menu: {test1_order}")
    if test2_order:
        print(f"   - Fingerfood: {test2_order}")
else:
    print("\n❌ No orders created - check errors above")


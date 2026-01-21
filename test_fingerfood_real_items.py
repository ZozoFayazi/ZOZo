#!/usr/bin/env python3
"""
COMPLETE FINGERFOOD E2E TEST
Tests real fingerfood items from DB with dip selection
"""
import requests
import json

API_URL = "https://foodorder-fix.preview.emergentagent.com/api"
LOCATION_ID = "49aff347-a6c3-407c-ad4a-59d5d0852314"

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

print_section("FINGERFOOD DIP E2E TESTS (ECHTE DB-ITEMS)")

# Test 1: Chicken Nuggets mit BBQ
print_section("TEST 1: Chicken Nuggets + BBQ Sauce")

order1 = {
    "location_id": LOCATION_ID,
    "items": [{
        "menu_item_id": "693c5e30e51d9e97f092cd74",  # Real Chicken Nuggets ID
        "name": "Chicken Nuggets",
        "price": 6.99,
        "size": "normal",
        "quantity": 1,
        "customizations": [],
        "extras": [],
        "removed_ingredients": [],
        "modifiers": {
            "fingerfood_dip": {
                "id": "dip-bbq",
                "name": "BBQ Sauce",
                "price": 0.0,
                "pos_item_id": "DIP_BBQ"
            }
        }
    }],
    "customer": {
        "name": "Fingerfood Test 1",
        "phone": "+4917011111",
        "email": "fingerfood1@zozo.de",
        "address": "Abholung",
        "postal_code": "00000",
        "city": "Rellingen"
    },
    "payment_method": "cash",
    "points_to_redeem": 0,
    "is_pickup": True
}

print("📦 Bestellung:")
print("   Item: Chicken Nuggets (6 Stück)")
print("   Dip: BBQ Sauce (inklusive)")
print("   Erwartet im POS: 2 separate items")

resp = requests.post(f"{API_URL}/orders", json=order1)

if resp.status_code == 200:
    order = resp.json()
    print(f"\n✅ Order created: {order.get('order_number')}")
    print(f"   Total: €{order.get('total'):.2f}")
    order1_num = order.get('order_number')
else:
    print(f"❌ Failed: {resp.status_code}")
    print(f"   Response: {resp.text}")
    order1_num = None

# Test 2: Chicken Wings mit Sweet Chili
print_section("TEST 2: Chicken Wings + Sweet Chili")

order2 = {
    "location_id": LOCATION_ID,
    "items": [{
        "menu_item_id": "693c5e30e51d9e97f092cd75",  # Real Chicken Wings ID
        "name": "Chicken Wings",
        "price": 7.99,
        "size": "normal",
        "quantity": 1,
        "customizations": [],
        "extras": [],
        "removed_ingredients": [],
        "modifiers": {
            "fingerfood_dip": {
                "id": "dip-sweetchili",
                "name": "Sweet Chili",
                "price": 0.0,
                "pos_item_id": "DIP_SWEET_CHILI"
            }
        }
    }],
    "customer": {
        "name": "Fingerfood Test 2",
        "phone": "+4917022222",
        "email": "fingerfood2@zozo.de",
        "address": "Abholung",
        "postal_code": "00000",
        "city": "Rellingen"
    },
    "payment_method": "cash",
    "points_to_redeem": 0,
    "is_pickup": True
}

print("📦 Bestellung:")
print("   Item: Chicken Wings")
print("   Dip: Sweet Chili (inklusive)")
print("   Erwartet im POS: 2 separate items")

resp = requests.post(f"{API_URL}/orders", json=order2)

if resp.status_code == 200:
    order = resp.json()
    print(f"\n✅ Order created: {order.get('order_number')}")
    print(f"   Total: €{order.get('total'):.2f}")
    order2_num = order.get('order_number')
else:
    print(f"❌ Failed: {resp.status_code}")
    print(f"   Response: {resp.text}")
    order2_num = None

# Verify
if order1_num and order2_num:
    print_section("ERFOLG - POS PAYLOADS PRÜFEN")
    print(f"✅ Beide Orders erstellt:")
    print(f"   - {order1_num}: Nuggets + BBQ")
    print(f"   - {order2_num}: Wings + Sweet Chili")
    print(f"\n📋 Backend-Logs zeigen ExpertOrder Payloads:")
    print(f"   tail -200 /var/log/supervisor/backend.err.log | grep 'ExpertOrder payload'")
else:
    print("\n❌ Test failed - check errors above")


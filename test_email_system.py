#!/usr/bin/env python3
"""
E2E Test: Order Confirmation Emails
Tests complete email system with all details
"""
import requests
import json

API_URL = "https://menu-config.preview.emergentagent.com/api"
LOCATION_ID = "49aff347-a6c3-407c-ad4a-59d5d0852314"

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

print_section("EMAIL SYSTEM E2E TESTS")

# Test 1: Pickup Order with Menu
print_section("TEST 1: ABHOLUNG - Menü mit Modifiers")

order1 = {
    "location_id": LOCATION_ID,
    "items": [{
        "menu_item_id": "menu-test-001",
        "name": "Cheeseburger Menü",
        "price": 11.90,
        "size": "normal",
        "quantity": 1,
        "customizations": [],
        "extras": [{"name": "Extra Käse", "price": 1.50}],
        "removed_ingredients": [],
        "modifiers": {
            "menu_beilage": {
                "id": "side-1",
                "name": "Süßkartoffel Pommes",
                "price": 1.5,
                "pos_item_id": "SIDES_SWEET_POTATO"
            },
            "menu_getraenk": {
                "id": "drink-1",
                "name": "ViO Apfelschorle 0,5l",
                "price": 0.0,
                "pos_item_id": "DRINK_VIO_APFEL_05"
            }
        }
    }],
    "customer": {
        "name": "Max Mustermann",
        "phone": "+49 170 1234567",
        "email": "max.mustermann@example.com",
        "address": "Abholung",
        "postal_code": "00000",
        "city": "Rellingen"
    },
    "payment_method": "cash",
    "points_to_redeem": 0,
    "is_pickup": True
}

print("📦 Bestellung:")
print("   Typ: ABHOLUNG")
print("   Item: Cheeseburger Menü")
print("   Modifiers: Süßkartoffel Pommes + ViO Apfelschorle")
print("   Extra: Extra Käse (+€1.50)")

resp = requests.post(f"{API_URL}/orders", json=order1)

if resp.status_code == 200:
    order = resp.json()
    print(f"\n✅ Order created: {order.get('order_number')}")
    print(f"   Total: €{order.get('total'):.2f}")
    print(f"   Email should be sent to: {order1['customer']['email']}")
    test1_order = order.get('order_number')
else:
    print(f"❌ Failed: {resp.status_code}")
    print(f"   Response: {resp.text}")
    test1_order = None

# Test 2: Delivery Order with Fingerfood
print_section("TEST 2: LIEFERUNG - Fingerfood mit Dip")

order2 = {
    "location_id": LOCATION_ID,
    "items": [{
        "menu_item_id": "693c5e30e51d9e97f092cd74",
        "name": "Chicken Nuggets",
        "price": 6.99,
        "size": "normal",
        "quantity": 2,
        "customizations": [],
        "extras": [],
        "removed_ingredients": [],
        "modifiers": {
            "fingerfood_dip": {
                "id": "dip-1",
                "name": "Knoblauch Sauce",
                "price": 0.0,
                "pos_item_id": "DIP_GARLIC"
            }
        }
    }],
    "customer": {
        "name": "Anna Schmidt",
        "phone": "+49 171 9876543",
        "email": "anna.schmidt@example.com",
        "address": "Hauptstraße 123",
        "postal_code": "25462",
        "city": "Rellingen",
        "notes": "Bitte klingeln, 2. Etage"
    },
    "payment_method": "card",
    "points_to_redeem": 0,
    "is_pickup": False
}

print("📦 Bestellung:")
print("   Typ: LIEFERUNG")
print("   Item: 2x Chicken Nuggets")
print("   Dip: Knoblauch Sauce")
print("   Adresse: Hauptstraße 123, 25462 Rellingen")
print("   Hinweis: Bitte klingeln, 2. Etage")

resp = requests.post(f"{API_URL}/orders", json=order2)

if resp.status_code == 200:
    order = resp.json()
    print(f"\n✅ Order created: {order.get('order_number')}")
    print(f"   Total: €{order.get('total'):.2f}")
    print(f"   Email should be sent to: {order2['customer']['email']}")
    test2_order = order.get('order_number')
else:
    print(f"❌ Failed: {resp.status_code}")
    print(f"   Response: {resp.text}")
    test2_order = None

# Summary
print_section("TEST SUMMARY")

if test1_order:
    print(f"✅ Test 1 (Abholung/Menü): {test1_order}")
    print(f"   Email-Check: tail -50 /var/log/supervisor/backend.err.log | grep -i email")

if test2_order:
    print(f"✅ Test 2 (Lieferung/Fingerfood): {test2_order}")
    print(f"   Email-Check: tail -50 /var/log/supervisor/backend.err.log | grep -i email")

print(f"\n📧 Email-Status in Logs prüfen:")
print(f"   tail -100 /var/log/supervisor/backend.err.log | grep 'Email sent\\|Email send'")


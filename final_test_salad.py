#!/usr/bin/env python3
"""
FINAL SALAD TEST - Real DB item with modifiers
"""
import requests

API_URL = "https://menu-config.preview.emergentagent.com/api"
LOCATION_ID = "49aff347-a6c3-407c-ad4a-59d5d0852314"

print("="*80)
print("  FINAL SALAD TEST - MIT DRESSING + PIZZABRÖTCHEN")
print("="*80)

order = {
    "location_id": LOCATION_ID,
    "items": [{
        "menu_item_id": "693c5e30e51d9e97f092ccb4",  # REAL Caesar Salad ID
        "name": "Caesar Salad",
        "price": 9.19,
        "size": "normal",
        "quantity": 1,
        "customizations": [],
        "extras": [],
        "removed_ingredients": [],
        "modifiers": {
            "salad_dressing_required": {
                "id": "dressing-joghurt",
                "name": "Joghurtdressing",
                "price": 0.0,
                "pos_item_id": "SALAD-DRESSING-REQUIRED-JOGHURTDRESSING-2"
            },
            "salad_pizzabroetchen_free_choice": {
                "id": "bread-with3",
                "name": "Mit 3 Pizzabrötchen (gratis)",
                "price": 0.0,
                "pos_item_id": "SALAD-PIZZABROETCHEN-FREE-CHOICE-MIT-3-PIZZABROETCHEN-1"
            }
        }
    }],
    "customer": {
        "name": "Final Test User",
        "phone": "+49170999999",
        "email": "final-test@zozo.de",
        "address": "Abholung",
        "postal_code": "00000",
        "city": "Rellingen"
    },
    "payment_method": "cash",
    "points_to_redeem": 0,
    "is_pickup": True
}

print("\n📦 Bestellung:")
print("   Item: Caesar Salad (ECHTES DB-Item)")
print("   Dressing: Joghurtdressing")
print("   Pizzabrötchen: Mit 3 (gratis)")
print("\nErwartet im POS: 3 separate Items")

resp = requests.post(f"{API_URL}/orders", json=order)

if resp.status_code == 200:
    result = resp.json()
    print(f"\n✅ Order created: {result.get('order_number')}")
    print(f"   Total: €{result.get('total'):.2f}")
    
    order_num = result.get('order_number')
    
    print(f"\n📋 POS Payload Check:")
    print(f"   tail -50 /var/log/supervisor/backend.err.log | grep '{order_num}' | grep 'ExpertOrder payload'")
    
else:
    print(f"\n❌ Order failed: {resp.status_code}")
    print(f"   Response: {resp.text}")


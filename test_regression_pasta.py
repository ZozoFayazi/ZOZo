#!/usr/bin/env python3
"""
REGRESSION TEST: Pasta mit Modifier (sollte weiterhin funktionieren)
"""
import requests

API_URL = "https://menu-config.preview.emergentagent.com/api"
LOCATION_ID = "49aff347-a6c3-407c-ad4a-59d5d0852314"

print("="*70)
print("  REGRESSION TEST: PASTA")
print("="*70)

order = {
    "location_id": LOCATION_ID,
    "items": [{
        "menu_item_id": "pasta-test-001",
        "name": "Pasta Carbonara",
        "price": 12.90,
        "size": "normal",
        "quantity": 1,
        "customizations": [],
        "extras": [],
        "removed_ingredients": [],
        "modifiers": {
            "pasta_type": {
                "id": "pasta-1",
                "name": "Penne",
                "price": 0.0,
                "pos_item_id": "PASTA-TYPE-PENNE-1"
            }
        }
    }],
    "customer": {
        "name": "Pasta Test",
        "phone": "+491709999",
        "email": "pasta-test@zozo.de",
        "address": "Abholung",
        "postal_code": "00000",
        "city": "Rellingen"
    },
    "payment_method": "cash",
    "points_to_redeem": 0,
    "is_pickup": True
}

print("\n📦 Bestellung: Pasta Carbonara mit Penne")

resp = requests.post(f"{API_URL}/orders", json=order)

if resp.status_code == 200:
    result = resp.json()
    print(f"✅ Order created: {result.get('order_number')}")
    print(f"   Total: €{result.get('total'):.2f}")
    print(f"\n✅ REGRESSION: PASS - Pasta funktioniert weiterhin!")
else:
    print(f"❌ REGRESSION FAILURE: {resp.status_code}")
    print(f"   Response: {resp.text}")


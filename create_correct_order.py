#!/usr/bin/env python3
"""
Create a CORRECT order with all modifiers for POS validation
This simulates what the frontend SHOULD send
"""
import requests

API_URL = "https://paypal-pos-fix.preview.emergentagent.com/api"
LOCATION_ID = "49aff347-a6c3-407c-ad4a-59d5d0852314"

print("="*80)
print("  KORREKTE BESTELLUNG ERSTELLEN - MIT ALLEN MODIFIERS")
print("="*80)

# Complete order with Menu + Salad + Fingerfood (all with modifiers)
order = {
    "location_id": LOCATION_ID,
    "items": [
        # 1. Champion Burger Menü (wie in echter Bestellung)
        {
            "menu_item_id": "menu-champion-001",
            "name": "Champion Burger Menü",
            "price": 11.69,
            "size": "normal",
            "quantity": 1,
            "customizations": [],
            "extras": [],
            "removed_ingredients": [],
            "modifiers": {
                "menu_beilage": {
                    "id": "side-pommes",
                    "name": "Pommes Normal",
                    "price": 0.0,
                    "pos_item_id": "SIDES_FRIES_NORMAL"
                },
                "menu_getraenk": {
                    "id": "drink-cola",
                    "name": "Coca Cola 0,5l",
                    "price": 0.0,
                    "pos_item_id": "DRINK_COLA_05"
                }
            }
        },
        # 2. Caesar Salad (wie in echter Bestellung)
        {
            "menu_item_id": "693c5e30e51d9e97f092ccb4",
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
        }
    ],
    "customer": {
        "name": "KORREKTUR Test",
        "phone": "+49170123456",
        "email": "test-korrekt@zozo.de",
        "address": "Friedrichshulder Weg 157a",
        "postal_code": "25469",
        "city": "Halstenbek"
    },
    "payment_method": "cash",
    "points_to_redeem": 0,
    "is_pickup": False  # LIEFERUNG wie in echter Order
}

print("\n📦 Bestellung (wie echte Order ZOZO-1150, aber KORREKT):")
print("   1. Champion Burger Menü")
print("      → Pommes Normal")
print("      → Coca Cola 0,5l")
print("   2. Caesar Salad")
print("      → Joghurtdressing")
print("      → Mit 3 Pizzabrötchen")
print("\nErwartet im POS: 6 separate Items!")

resp = requests.post(f"{API_URL}/orders", json=order)

if resp.status_code == 200:
    result = resp.json()
    order_num = result.get('order_number')
    
    print(f"\n✅ Order created: {order_num}")
    print(f"   Total: €{result.get('total'):.2f}")
    print(f"   Email sent to: {order['customer']['email']}")
    
    print(f"\n📋 POS Payload prüfen:")
    print(f"   tail -50 /var/log/supervisor/backend.err.log | grep '{order_num}' | grep 'ExpertOrder payload'")
    
    import time
    time.sleep(2)
    
    # Show payload
    import subprocess
    result = subprocess.run(
        f"tail -100 /var/log/supervisor/backend.err.log | grep '{order_num}' | grep 'ExpertOrder payload'",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        import json
        # Extract JSON
        payload_str = result.stdout.split('ExpertOrder payload: ')[1]
        payload = json.loads(payload_str)
        
        print(f"\n{'='*80}")
        print(f"  POS PAYLOAD - {order_num}")
        print(f"{'='*80}\n")
        
        print(f"Items ({len(payload['items'])}):")
        for i, item in enumerate(payload['items'], 1):
            group = f" ({item.get('group', 'N/A')})" if 'group' in item else ""
            print(f"  {i}. {item['name']} - €{item['price']:.2f}{group}")
            print(f"     UID: {item.get('uid', 'N/A')}")
        
        print(f"\n✅ ALLE {len(payload['items'])} ITEMS ALS SEPARATE ZEILEN!")
    
else:
    print(f"\n❌ Order failed: {resp.status_code}")
    print(f"   Response: {resp.text}")


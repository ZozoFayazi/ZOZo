#!/usr/bin/env python3
"""
Test Menu Order with proper structure
Hamburger Medium 125g Menü with all components in correct order
"""
import requests, json

API_URL = "https://paypal-pos-fix.preview.emergentagent.com/api"
LOCATION_ID = "49aff347-a6c3-407c-ad4a-59d5d0852314"

order = {
    "location_id": LOCATION_ID,
    "items": [{
        "menu_item_id": "test-hamburger-medium-menu",
        "name": "Hamburger Menü",
        "price": 10.90,
        "size": "Medium",  # Size info
        "quantity": 1,
        "customizations": ["+ Brioche Brötchen"],
        "extras": [{"name": "Extra Käse", "price": 1.50}],
        "removed_ingredients": ["Gurken"],
        "modifiers": {
            "menu_beilage": {
                "id": "side-twister",
                "name": "Twister Fries",
                "price": 0.99,
                "pos_item_id": "SIDES_CURLY_FRIES"
            },
            "menu_getraenk": {
                "id": "drink-fanta",
                "name": "Fanta 0,5l",
                "price": 0.0,
                "pos_item_id": "DRINK_FANTA_05"
            }
        }
    }],
    "customer": {
        "name": "Struktur Test",
        "phone": "+49170555555",
        "email": "struktur@test.de",
        "address": "Abholung",
        "postal_code": "00000",
        "city": "Rellingen"
    },
    "payment_method": "cash",
    "points_to_redeem": 0,
    "is_pickup": True
}

print("="*80)
print("  TEST: MENÜ MIT STRUKTURIERTER REIHENFOLGE")
print("="*80)
print("\n📦 Bestellung:")
print("   Hamburger Medium (125g) Menü")
print("   1. Brioche Brötchen")
print("   2. Ohne Gurken")
print("   3. Extra Käse (+€1.50)")
print("   4. Beilage: Twister Fries (+€0.99)")
print("   5. Getränk: Fanta 0,5l")

resp = requests.post(f"{API_URL}/orders", json=order)

if resp.status_code == 200:
    result = resp.json()
    order_num = result.get('order_number')
    
    print(f"\n✅ Order created: {order_num}")
    print(f"   Total: €{result.get('total'):.2f}")
    
    import time, subprocess
    time.sleep(2)
    
    # Get payload
    cmd_result = subprocess.run(
        f"tail -100 /var/log/supervisor/backend.err.log | grep '{order_num}' | grep 'ExpertOrder payload'",
        shell=True, capture_output=True, text=True
    )
    
    if cmd_result.stdout:
        payload_str = cmd_result.stdout.split('ExpertOrder payload: ')[1]
        payload = json.loads(payload_str)
        
        print(f"\n{'='*80}")
        print(f"  POS PAYLOAD - REIHENFOLGE")
        print(f"{'='*80}\n")
        
        for i, item in enumerate(payload['items'], 1):
            group = item.get('group', 'MAIN')
            print(f"{i}. {item['name']} - €{item['price']:.2f} ({group})")
        
        print(f"\n✅ Erwartete Reihenfolge:")
        print(f"   1. Hauptartikel (mit Größe 'Medium')")
        print(f"   2. Brötchen (BUN)")
        print(f"   3. Abwahl (REMOVAL)")
        print(f"   4. Extra (EXTRA)")
        print(f"   5. Beilage (SIDE)")
        print(f"   6. Getränk (DRINK)")
else:
    print(f"\n❌ Failed: {resp.status_code}")
    print(f"   {resp.text}")


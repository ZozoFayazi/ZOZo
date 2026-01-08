"""Final Smoke-Test vor Go-Live"""
import asyncio
import requests
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

API_URL = "http://localhost:8001/api"

async def final_smoke_test():
    """2 finale Test-Bestellungen vor Go-Live"""
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ.get('DB_NAME', 'test_database')]
    
    print("=" * 80)
    print("🔥 FINAL SMOKE-TEST VOR GO-LIVE")
    print("=" * 80)
    
    # Get locations
    rellingen = await db.locations.find_one({"slug": "rellingen"})
    henstedt = await db.locations.find_one({"slug": "henstedt-ulzburg"})
    
    location_rel_id = rellingen.get('id')
    location_hen_id = henstedt.get('id')
    
    # Get menu item
    menu_item = await db.menu_items.find_one({"active": True})
    
    results = []
    
    # Test 1: Lieferung (Rellingen)
    print("\n1️⃣ Test: Lieferung (Rellingen)...")
    try:
        order_data = {
            "location_id": location_rel_id,
            "items": [{
                "menu_item_id": str(menu_item['_id']),
                "name": menu_item['name'],
                "price": menu_item.get('price_normal', 10.00),
                "size": "normal",
                "quantity": 2
            }],
            "customer": {
                "name": "Final Smoke Test Lieferung",
                "phone": "017000000001",
                "email": "smoke-test@zozo.de",
                "address": "Möwenstraße 1",
                "postal_code": "25462",
                "city": "Rellingen",
                "notes": "FINAL SMOKE TEST - Lieferung"
            },
            "payment_method": "cash",
            "is_pickup": False
        }
        
        response = requests.post(f"{API_URL}/orders", json=order_data)
        assert response.status_code == 200
        result = response.json()
        
        order_num_delivery = result['order_number']
        print(f"   ✅ Bestellung erstellt: {order_num_delivery}")
        print(f"   Total: €{result['total']:.2f}")
        
        # Wait for POS
        await asyncio.sleep(5)
        
        order = await db.orders.find_one({"order_number": order_num_delivery})
        pos_status = order.get('pos_status', 'N/A')
        
        if pos_status == 'sent':
            print(f"   ✅ POS Status: SENT")
            results.append("✅ Lieferung: Bestellt + POS Sync")
        else:
            print(f"   ⚠️ POS Status: {pos_status}")
            results.append(f"⚠️ Lieferung: Bestellt (POS: {pos_status})")
            
    except Exception as e:
        print(f"   ❌ Fehler: {str(e)}")
        results.append(f"❌ Lieferung: {str(e)}")
    
    # Test 2: Abholung (Henstedt)
    print("\n2️⃣ Test: Abholung (Henstedt-Ulzburg)...")
    try:
        order_data = {
            "location_id": location_hen_id,
            "items": [{
                "menu_item_id": str(menu_item['_id']),
                "name": menu_item['name'],
                "price": menu_item.get('price_normal', 10.00),
                "size": "normal",
                "quantity": 1
            }],
            "customer": {
                "name": "Final Smoke Test Abholung",
                "phone": "017000000002",
                "email": "smoke-pickup@zozo.de",
                "address": "Abholung",
                "postal_code": "00000",
                "city": "Henstedt-Ulzburg",
                "notes": "FINAL SMOKE TEST - Abholung"
            },
            "payment_method": "cash",
            "is_pickup": True
        }
        
        response = requests.post(f"{API_URL}/orders", json=order_data)
        assert response.status_code == 200
        result = response.json()
        
        order_num_pickup = result['order_number']
        print(f"   ✅ Bestellung erstellt: {order_num_pickup}")
        print(f"   Total: €{result['total']:.2f}")
        print(f"   is_pickup: {result.get('is_pickup', False)}")
        
        # Wait for POS
        await asyncio.sleep(5)
        
        order = await db.orders.find_one({"order_number": order_num_pickup})
        pos_status = order.get('pos_status', 'N/A')
        
        if pos_status == 'sent':
            print(f"   ✅ POS Status: SENT")
            results.append("✅ Abholung: Bestellt + POS Sync")
        else:
            print(f"   ⚠️ POS Status: {pos_status}")
            results.append(f"⚠️ Abholung: Bestellt (POS: {pos_status})")
            
    except Exception as e:
        print(f"   ❌ Fehler: {str(e)}")
        results.append(f"❌ Abholung: {str(e)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FINAL SMOKE-TEST ERGEBNISSE:")
    print("=" * 80)
    
    for r in results:
        print(f"  {r}")
    
    passed = sum(1 for r in results if r.startswith("✅"))
    
    print(f"\n🎯 Score: {passed}/{len(results)} Tests bestanden")
    
    if passed == len(results):
        print("\n🎉 ALLE SMOKE-TESTS BESTANDEN!")
        print("✅ System ist bereit für Go-Live")
        print("\n📝 Bestellnummern im ExpertOrder POS:")
        print(f"   - {order_num_delivery} (Lieferung)")
        print(f"   - {order_num_pickup} (Abholung)")
        print("\n⚠️ Bitte im POS als Test markieren/löschen")
    else:
        print(f"\n⚠️ {len(results) - passed} Test(s) mit Warnung")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(final_smoke_test())

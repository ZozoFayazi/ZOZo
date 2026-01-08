"""Zeitbestellung für 18:50 Uhr erstellen"""
import asyncio
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

API_URL = "http://localhost:8001/api"

async def create_scheduled_order():
    """Zeitbestellung für 18:50 erstellen"""
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ.get('DB_NAME', 'test_database')]
    
    print("=" * 70)
    print("⏰ ZEITBESTELLUNG FÜR 18:50 UHR")
    print("=" * 70)
    
    # Get Rellingen
    rellingen = await db.locations.find_one({"slug": "rellingen"})
    location_id = rellingen.get('id')
    
    # Get menu item
    menu_item = await db.menu_items.find_one({"active": True})
    
    # Create order
    print("\n📦 Zeitbestellung Details:")
    print(f"   Gewünschte Lieferzeit: 18:50 Uhr")
    print(f"   Location: Rellingen")
    print(f"   Artikel: 2x {menu_item['name']}")
    
    order_data = {
        "location_id": location_id,
        "items": [{
            "menu_item_id": str(menu_item['_id']),
            "name": menu_item['name'],
            "price": menu_item.get('price_normal', 10.00),
            "size": "normal",
            "quantity": 2
        }],
        "customer": {
            "name": "Zeitbestellung Test",
            "phone": "017099999999",
            "email": "zeitbestellung@zozo.de",
            "address": "Möwenstraße 10",
            "postal_code": "25462",
            "city": "Rellingen",
            "notes": "ZEITBESTELLUNG für 18:50 Uhr - TESTBESTELLUNG"
        },
        "payment_method": "cash",
        "is_pickup": False,
        "scheduled_time": "2026-01-08T18:50:00"  # OHNE Z = lokale deutsche Zeit!
    }
    
    print("\n🚀 Sende Zeitbestellung...")
    
    try:
        response = requests.post(f"{API_URL}/orders", json=order_data)
        
        if response.status_code == 200:
            result = response.json()
            order_number = result['order_number']
            
            print(f"\n✅ Zeitbestellung erstellt: {order_number}")
            print(f"   Total: €{result['total']:.2f}")
            
            # Wait for POS push
            await asyncio.sleep(5)
            
            # Check order in DB
            order = await db.orders.find_one({"order_number": order_number})
            
            print(f"\n🏪 ExpertOrder POS:")
            print(f"   Status: {order.get('pos_status', 'N/A')}")
            
            if order.get('pos_status') == 'sent':
                print(f"   ✅ AN EXPERTORDER GESENDET")
                print(f"\n📝 Im ExpertOrder POS sollte zu sehen sein:")
                print(f"   - Bestellung: {order_number}")
                print(f"   - Typ: LIEFERUNG (notification: false)")
                print(f"   - Lieferzeit: 18:50 Uhr")
                print(f"   - NICHT sofort, sondern ZEITBESTELLUNG")
            
        else:
            print(f"\n❌ Fehler: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_scheduled_order())

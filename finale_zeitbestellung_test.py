"""Finale Zeitbestellung mit Screenshot-Beweis"""
import asyncio
import requests
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

API_URL = "http://localhost:8001/api"

async def create_final_scheduled_order():
    """Finale Zeitbestellung für 19:30 Uhr"""
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ.get('DB_NAME', 'test_database')]
    
    print("=" * 80)
    print("⏰ FINALE ZEITBESTELLUNG - 19:30 UHR")
    print("=" * 80)
    
    # Get Rellingen
    rellingen = await db.locations.find_one({"slug": "rellingen"})
    location_id = rellingen.get('id')
    
    # Get menu items
    menu_items = await db.menu_items.find({"active": True}).limit(2).to_list(2)
    
    print(f"\n📍 Standort: {rellingen['name']}")
    print(f"⏰ Gewünschte Lieferzeit: 19:30 Uhr")
    print(f"📦 Bestellart: LIEFERUNG")
    
    # Create order
    order_data = {
        "location_id": location_id,
        "items": [
            {
                "menu_item_id": str(menu_items[0]['_id']),
                "name": menu_items[0]['name'],
                "price": menu_items[0].get('price_normal', 8.00),
                "size": "normal",
                "quantity": 1
            },
            {
                "menu_item_id": str(menu_items[1]['_id']),
                "name": menu_items[1]['name'],
                "price": menu_items[1].get('price_normal', 10.00),
                "size": "normal",
                "quantity": 1
            }
        ],
        "customer": {
            "name": "Zeitbestellung 19:30",
            "phone": "017099999999",
            "email": "zeit@zozo.de",
            "address": "Möwenstraße 5",
            "postal_code": "25462",
            "city": "Rellingen",
            "notes": "Zeitbestellung für 19:30 Uhr - Bitte pünktlich!"
        },
        "payment_method": "cash",
        "is_pickup": False,
        "scheduled_time": "2026-01-08T19:30:00"  # 19:30 MEZ (wird zu 18:30Z)
    }
    
    print(f"\n📦 Artikel:")
    for item in order_data['items']:
        print(f"   - {item['quantity']}x {item['name']} (€{item['price']:.2f})")
    
    print(f"\n🚀 Sende Zeitbestellung an API...")
    
    try:
        response = requests.post(f"{API_URL}/orders", json=order_data)
        
        if response.status_code == 200:
            result = response.json()
            order_number = result['order_number']
            
            print(f"\n✅ Zeitbestellung erstellt: {order_number}")
            print(f"   Total: €{result['total']:.2f}")
            
            # Wait for POS
            await asyncio.sleep(5)
            
            # Check in DB
            order = await db.orders.find_one({"order_number": order_number})
            
            print(f"\n🏪 ExpertOrder POS:")
            print(f"   Status: {order.get('pos_status', 'N/A')}")
            
            if order.get('pos_status') == 'sent':
                print(f"   ✅ AN EXPERTORDER GESENDET!")
                print(f"\n📝 Im ExpertOrder POS sollte erscheinen:")
                print(f"   📋 Bestellnummer: {order_number}")
                print(f"   ⏰ Lieferzeit: 19:30 Uhr (MEZ)")
                print(f"   🚚 Typ: LIEFERUNG")
                print(f"   📌 Adresse: Möwenstraße 5, 25462 Rellingen")
                print(f"   💰 Total: €{result['total']:.2f}")
                print(f"   📞 Kunde: Zeitbestellung 19:30 / 017099999999")
                
                print(f"\n" + "=" * 80)
                print(f"✅ ZEITBESTELLUNG ERFOLGREICH!")
                print(f"=" * 80)
            else:
                print(f"   ⚠️ POS Status: {order.get('pos_status')}")
        else:
            print(f"\n❌ Fehler: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_final_scheduled_order())

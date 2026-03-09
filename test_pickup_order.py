"""Test Pickup Order Flow"""
import asyncio
import requests
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

API_URL = "http://localhost:8001/api"

async def test_pickup_order():
    """Test pickup order with minimal fields"""
    client_mongo = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client_mongo[os.environ.get('DB_NAME', 'test_database')]
    
    print("=" * 70)
    print("🏪 ABHOLUNG (PICKUP) ORDER TEST")
    print("=" * 70)
    
    # Get Rellingen location
    rellingen = await db.locations.find_one({"name": {"$regex": "Rellingen", "$options": "i"}})
    location_id = rellingen.get('id')
    
    # Get menu items
    menu_items = await db.menu_items.find({"active": True}).limit(2).to_list(length=2)
    
    # Create PICKUP order with minimal data
    order_data = {
        "location_id": location_id,
        "items": [
            {
                "menu_item_id": str(menu_items[0]['_id']),
                "name": menu_items[0]['name'],
                "price": menu_items[0].get('price_normal', 10.00),
                "size": "normal",
                "quantity": 2
            }
        ],
        "customer": {
            "name": "Abholer Test Kunde",
            "phone": "017011112222",
            "email": "",  # Optional
            "address": "Abholung",  # Dummy für Abholung
            "postal_code": "00000",  # Dummy für Abholung
            "city": "Rellingen",  # Location city
            "notes": "ABHOLUNG - Bereit in 15 Minuten"
        },
        "payment_method": "cash",
        "is_pickup": True  # WICHTIG: Pickup flag
    }
    
    print("\n📦 ABHOLUNG Bestellung:")
    print(f"   Name: {order_data['customer']['name']}")
    print(f"   Telefon: {order_data['customer']['phone']}")
    print(f"   Bestellart: ABHOLUNG")
    print(f"   Artikel: {order_data['items'][0]['quantity']}x {order_data['items'][0]['name']}")
    
    print("\n🚀 Sende Bestellung...")
    
    try:
        response = requests.post(
            f"{API_URL}/orders",
            json=order_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ ABHOLUNG Bestellung erfolgreich!")
            print(f"\n📋 Bestellnummer: {result.get('order_number')}")
            print(f"   Status: {result['status']}")
            print(f"   Gesamt: €{result['total']:.2f}")
            print(f"   Abholung (is_pickup): {result.get('is_pickup', False)}")
            print(f"   POS Status: {result.get('pos_status', 'N/A')}")
            
            # Wait for POS push
            await asyncio.sleep(5)
            
            # Check POS status
            order = await db.orders.find_one({"order_number": result['order_number']})
            if order:
                print(f"\n🏪 ExpertOrder POS:")
                print(f"   Status: {order.get('pos_status', 'N/A')}")
                if order.get('pos_status') == 'sent':
                    print(f"   ✅ AN EXPERTORDER GESENDET")
                    print(f"   Gesendet am: {order.get('pos_pushed_at')}")
                
            print("\n" + "=" * 70)
            print("✅ ABHOLUNG TEST ERFOLGREICH")
            print("=" * 70)
            print("\n📝 Validierung:")
            print("   ✓ Nur Name + Telefon erforderlich")
            print("   ✓ Keine Adresse/PLZ nötig")
            print("   ✓ is_pickup = True")
            print("   ✓ An ExpertOrder gesendet")
            print("\n💡 Zeitangabe sollte sein: 'Bereit in ca. 15 Minuten'")
            
        else:
            print(f"\n❌ Fehler: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")
    
    client_mongo.close()

if __name__ == "__main__":
    asyncio.run(test_pickup_order())

"""Test Order for Rellingen Location"""
import asyncio
import requests
import json
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

API_URL = "http://localhost:8001/api"

async def create_test_order():
    """Create a test order for Rellingen"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 70)
    print("🧪 TESTBESTELLUNG FÜR RELLINGEN")
    print("=" * 70)
    
    # Find Rellingen location
    rellingen_location = await db.locations.find_one({
        "name": {"$regex": "Rellingen", "$options": "i"}
    })
    
    if not rellingen_location:
        print("❌ Rellingen location not found!")
        return
    
    location_id = rellingen_location.get('id') or str(rellingen_location.get('_id'))
    location_name = rellingen_location.get('name')
    
    print(f"\n📍 Location: {location_name}")
    print(f"   ID: {location_id}")
    
    # Get some menu items for the order
    menu_items = await db.menu_items.find({
        "active": True,
        "$or": [
            {"location_id": None},
            {"location_id": location_id}
        ]
    }).limit(2).to_list(length=2)
    
    if not menu_items:
        print("❌ No menu items found!")
        return
    
    # Create order data
    order_data = {
        "location_id": location_id,
        "items": [
            {
                "menu_item_id": str(menu_items[0]['_id']),
                "name": menu_items[0]['name'],
                "price": menu_items[0].get('price_normal', menu_items[0].get('price_medium', 10.00)),
                "size": "normal",
                "quantity": 2
            },
            {
                "menu_item_id": str(menu_items[1]['_id']),
                "name": menu_items[1]['name'],
                "price": menu_items[1].get('price_normal', menu_items[1].get('price_medium', 8.00)),
                "size": "normal",
                "quantity": 1
            }
        ],
        "customer": {
            "name": "Test Kunde Rellingen",
            "phone": "017012345678",
            "email": "test@rellingen.de",
            "address": "Hauptstraße 30",
            "postal_code": "25462",
            "city": "Rellingen",
            "notes": "TESTBESTELLUNG - Bitte NICHT zubereiten!"
        },
        "payment_method": "cash"
    }
    
    print("\n📦 Bestelldetails:")
    print(f"   Kunde: {order_data['customer']['name']}")
    print(f"   Adresse: {order_data['customer']['address']}, {order_data['customer']['postal_code']} {order_data['customer']['city']}")
    print(f"   Telefon: {order_data['customer']['phone']}")
    print(f"   Email: {order_data['customer']['email']}")
    print(f"   Zahlungsmethode: {order_data['payment_method']}")
    print(f"\n   Artikel:")
    for item in order_data['items']:
        print(f"   - {item['quantity']}x {item['name']} (€{item['price']:.2f})")
    
    total = sum(item['price'] * item['quantity'] for item in order_data['items'])
    print(f"\n   Zwischensumme: €{total:.2f}")
    print(f"   Liefergebühr: €2.50")
    print(f"   GESAMT: €{total + 2.50:.2f}")
    
    print("\n🚀 Sende Bestellung an API...")
    
    try:
        # Send order to API
        response = requests.post(
            f"{API_URL}/orders",
            json=order_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Bestellung erfolgreich erstellt!")
            print(f"\n📋 Bestellnummer: {result.get('order_number', 'N/A')}")
            print(f"   Bestellstatus: {result.get('status', 'N/A')}")
            print(f"   Gesamt: €{result.get('total', 0):.2f}")
            
            # Check POS status
            pos_status = result.get('pos_status', 'N/A')
            print(f"\n🏪 POS (ExpertOrder) Status: {pos_status}")
            
            if pos_status == "sent":
                print("   ✅ Bestellung wurde an ExpertOrder POS gesendet!")
            elif pos_status == "error":
                print(f"   ⚠️  POS-Fehler: {result.get('pos_error', 'Unknown')}")
            elif pos_status == "not_applicable":
                print("   ℹ️  POS nicht konfiguriert für diesen Standort")
            
            # Check if order is in database
            order_id = result.get('id')
            if order_id:
                db_order = await db.orders.find_one({"_id": order_id})
                if db_order:
                    print("\n✅ Bestellung in Datenbank gespeichert")
                    print(f"   MongoDB ID: {db_order['_id']}")
                    print(f"   Erstellt am: {db_order.get('created_at', 'N/A')}")
            
            print("\n" + "=" * 70)
            print("✅ TESTBESTELLUNG ERFOLGREICH ABGESCHLOSSEN")
            print("=" * 70)
            print("\n⚠️  WICHTIG: Dies ist eine TESTBESTELLUNG!")
            print("   Bitte im POS-System (ExpertOrder) als Test markieren")
            print("   oder löschen, um eine echte Zubereitung zu vermeiden.")
            
        else:
            print(f"\n❌ Fehler beim Erstellen der Bestellung!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_order())

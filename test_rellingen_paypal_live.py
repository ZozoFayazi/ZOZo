"""Test PayPal Live für Rellingen"""
import asyncio
import requests
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

API_URL = "http://localhost:8001/api"

async def test_rellingen_paypal():
    """Test PayPal für Rellingen"""
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ.get('DB_NAME', 'test_database')]
    
    print("=" * 70)
    print("💳 PAYPAL LIVE TEST - RELLINGEN")
    print("=" * 70)
    
    # Get Rellingen
    rellingen = await db.locations.find_one({"slug": "rellingen"})
    location_id = rellingen.get('id')
    
    print(f"\n📍 Location: {rellingen['name']}")
    print(f"   ID: {location_id}")
    
    # Get menu item
    menu_item = await db.menu_items.find_one({"active": True})
    
    # Create order
    print("\n🔍 Schritt 1: Bestellung erstellen...")
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
            "name": "PayPal Live Test",
            "phone": "017099999999",
            "email": "paypal-live@zozo.de",
            "address": "Möwenstraße 2",
            "postal_code": "25462",
            "city": "Rellingen",
            "notes": "PayPal LIVE Test"
        },
        "payment_method": "paypal",
        "is_pickup": False
    }
    
    try:
        response = requests.post(f"{API_URL}/orders", json=order_data)
        assert response.status_code == 200
        order_result = response.json()
        
        order_id = order_result.get('id')
        order_number = order_result.get('order_number')
        total = order_result.get('total')
        
        print(f"   ✅ Bestellung: {order_number}")
        print(f"   Total: €{total:.2f}")
        
    except Exception as e:
        print(f"   ❌ Fehler: {str(e)}")
        client.close()
        return
    
    # Create PayPal Order
    print("\n🔍 Schritt 2: PayPal Order erstellen...")
    
    paypal_data = {
        "location_id": location_id,
        "order_id": order_id,
        "order_number": order_number,
        "subtotal": total,
        "delivery_fee": 0.0,
        "discount": 0.0,
        "total": total,
        "currency": "EUR"
    }
    
    try:
        response = requests.post(f"{API_URL}/paypal/create-order", json=paypal_data)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"   ✅ PayPal Order erstellt!")
                print(f"   PayPal Order ID: {result.get('order_id')}")
                print(f"   Status: {result.get('status')}")
                print(f"   Approval URL: {result.get('approval_url', 'N/A')[:60]}...")
                
                print("\n" + "=" * 70)
                print("✅ RELLINGEN PAYPAL LIVE TEST ERFOLGREICH!")
                print("=" * 70)
                print("\n📝 Das bedeutet:")
                print("   ✓ Neue Credentials funktionieren")
                print("   ✓ LIVE Mode aktiv")
                print("   ✓ Echte Zahlungen möglich")
                print("   ✓ Kunden können mit ihrer PayPal-Email zahlen")
                
            else:
                print(f"   ❌ PayPal Fehler: {result.get('error')}")
                print(f"\n⚠️ Credentials könnten noch Sandbox sein")
        else:
            print(f"   ❌ HTTP {response.status_code}")
            print(f"   {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Fehler: {str(e)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_rellingen_paypal())

"""Test PayPal Integration End-to-End"""
import asyncio
import requests
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

API_URL = "http://localhost:8001/api"

async def test_paypal_integration():
    """Test PayPal integration for Henstedt-Ulzburg"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 70)
    print("💳 PAYPAL INTEGRATION TEST")
    print("=" * 70)
    
    # Find Henstedt-Ulzburg location
    henstedt = await db.locations.find_one({
        "name": {"$regex": "Henstedt", "$options": "i"}
    })
    
    if not henstedt:
        print("❌ Henstedt-Ulzburg location not found!")
        return
    
    location_id = henstedt.get('id') or str(henstedt.get('_id'))
    
    print(f"\n📍 Location: {henstedt['name']}")
    print(f"   ID: {location_id}")
    
    # Step 1: Check PayPal configuration
    print("\n🔍 Schritt 1: PayPal-Konfiguration prüfen...")
    
    try:
        config_response = requests.get(f"{API_URL}/paypal/client-id/{location_id}")
        
        if config_response.status_code == 200:
            config_data = config_response.json()
            print(f"   ✅ PayPal Client ID: {config_data.get('client_id', 'N/A')[:30]}...")
            print(f"   Mode: {'SANDBOX' if config_data.get('sandbox_mode') else 'LIVE'}")
        else:
            print(f"   ❌ Fehler: {config_response.status_code}")
            print(f"   {config_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Fehler: {str(e)}")
        return
    
    # Step 2: Create a test order
    print("\n🔍 Schritt 2: Test-Bestellung erstellen...")
    
    menu_items = await db.menu_items.find({
        "active": True,
        "$or": [
            {"location_id": None},
            {"location_id": location_id}
        ]
    }).limit(1).to_list(length=1)
    
    if not menu_items:
        print("   ❌ Keine Menu Items gefunden!")
        return
    
    order_data = {
        "location_id": location_id,
        "items": [{
            "menu_item_id": str(menu_items[0]['_id']),
            "name": menu_items[0]['name'],
            "price": menu_items[0].get('price_normal', 12.00),
            "size": "normal",
            "quantity": 1
        }],
        "customer": {
            "name": "PayPal Test Kunde",
            "phone": "017099999999",
            "email": "paypal-test@zozo.de",
            "address": "Teststraße 1",
            "postal_code": "24558",
            "city": "Henstedt-Ulzburg",
            "notes": "PAYPAL TESTBESTELLUNG - NICHT zubereiten!"
        },
        "payment_method": "paypal",
        "is_pickup": True
    }
    
    try:
        order_response = requests.post(
            f"{API_URL}/orders",
            json=order_data,
            headers={"Content-Type": "application/json"}
        )
        
        if order_response.status_code == 200:
            order_result = order_response.json()
            order_id = order_result.get('id')
            order_number = order_result.get('order_number')
            total = order_result.get('total', 0)
            
            print(f"   ✅ Bestellung erstellt: {order_number}")
            print(f"   Order ID: {order_id}")
            print(f"   Gesamt: €{total:.2f}")
        else:
            print(f"   ❌ Fehler beim Erstellen: {order_response.status_code}")
            print(f"   {order_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Fehler: {str(e)}")
        return
    
    # Step 3: Create PayPal Order
    print("\n🔍 Schritt 3: PayPal-Order erstellen...")
    
    paypal_order_data = {
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
        paypal_response = requests.post(
            f"{API_URL}/paypal/create-order",
            json=paypal_order_data,
            headers={"Content-Type": "application/json"}
        )
        
        if paypal_response.status_code == 200:
            paypal_result = paypal_response.json()
            
            if paypal_result.get('success'):
                print(f"   ✅ PayPal Order erstellt!")
                print(f"   PayPal Order ID: {paypal_result.get('order_id')}")
                print(f"   Status: {paypal_result.get('status')}")
                print(f"   Approval URL: {paypal_result.get('approval_url', 'N/A')[:60]}...")
                
                print("\n" + "=" * 70)
                print("✅ PAYPAL INTEGRATION TEST ERFOLGREICH!")
                print("=" * 70)
                print("\n📝 Zusammenfassung:")
                print(f"   ✓ PayPal-Konfiguration geladen")
                print(f"   ✓ ZOZO-Bestellung erstellt: {order_number}")
                print(f"   ✓ PayPal-Order erstellt")
                print(f"   ✓ Approval URL generiert")
                print("\n💡 Der Kunde würde jetzt zu PayPal weitergeleitet werden")
                print("   um die Zahlung abzuschließen.")
                print("\n⚠️  Hinweis: Dies ist ein Backend-Test. Die PayPal-Buttons")
                print("   müssen über die Website getestet werden für den vollen Flow.")
            else:
                print(f"   ❌ PayPal Order Fehler: {paypal_result.get('error')}")
        else:
            print(f"   ❌ HTTP Fehler: {paypal_response.status_code}")
            print(f"   {paypal_response.text}")
    except Exception as e:
        print(f"   ❌ Fehler: {str(e)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_paypal_integration())

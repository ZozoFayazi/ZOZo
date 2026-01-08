"""Verify test order and POS status"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def verify_order():
    """Verify the test order"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 70)
    print("🔍 BESTELLUNGS-ÜBERPRÜFUNG")
    print("=" * 70)
    
    # Find the test order
    order = await db.orders.find_one(
        {"order_number": "ZOZO-1034"},
        sort=[("created_at", -1)]
    )
    
    if not order:
        print("❌ Bestellung nicht gefunden!")
        return
    
    print(f"\n📋 Bestellnummer: {order['order_number']}")
    print(f"   Status: {order['status']}")
    print(f"   Gesamt: €{order['total']:.2f}")
    print(f"   Kunde: {order['customer']['name']}")
    print(f"   Location ID: {order['location_id']}")
    
    print("\n📦 Artikel:")
    for item in order['items']:
        print(f"   - {item['quantity']}x {item['name']} (€{item['price']:.2f})")
    
    print("\n🏪 POS (ExpertOrder) Status:")
    print(f"   Status: {order.get('pos_status', 'N/A')}")
    print(f"   Gesendet am: {order.get('pos_pushed_at', 'Noch nicht gesendet')}")
    print(f"   POS Order ID: {order.get('pos_order_id', 'N/A')}")
    print(f"   Test Mode: {order.get('pos_is_test_mode', 'N/A')}")
    
    if order.get('pos_error'):
        print(f"   ⚠️  Fehler: {order['pos_error']}")
    
    # Check ExpertOrder integration status
    print("\n🔧 ExpertOrder Konfiguration:")
    location_settings = await db.location_settings.find_one({
        "location_id": order['location_id']
    })
    
    if location_settings:
        print(f"   Enabled: {location_settings.get('expertorder_enabled', False)}")
        print(f"   Test Mode: {location_settings.get('expertorder_test_mode', 'N/A')}")
        print(f"   API Key: {'SET' if location_settings.get('expertorder_api_key') else 'NOT SET'}")
        print(f"   Base URL: {location_settings.get('expertorder_base_url', 'N/A')}")
    else:
        print("   ⚠️  Keine Konfiguration gefunden")
    
    # Check payment method
    print(f"\n💰 Zahlungsmethode: {order['payment_method']}")
    if order['payment_method'] == 'paypal':
        print(f"   PayPal Status: {order.get('payment_status', 'N/A')}")
        print(f"   Transaction ID: {order.get('paypal_transaction_id', 'N/A')}")
    
    print("\n" + "=" * 70)
    print("✅ ÜBERPRÜFUNG ABGESCHLOSSEN")
    print("=" * 70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verify_order())

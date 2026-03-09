"""Verify both test orders sent to ExpertOrder"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def verify_orders():
    """Verify both test orders"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 70)
    print("🔍 VERIFIKATION BEIDER TESTBESTELLUNGEN")
    print("=" * 70)
    
    # Check both orders
    orders = await db.orders.find({
        "order_number": {"$in": ["ZOZO-1046", "ZOZO-1047"]}
    }).to_list(length=2)
    
    for order in orders:
        # Get location
        location = await db.locations.find_one({"id": order['location_id']})
        location_name = location.get('name', 'Unknown') if location else 'Unknown'
        
        print(f"\n{'=' * 70}")
        print(f"📋 Bestellnummer: {order['order_number']}")
        print(f"   Location: {location_name}")
        print(f"   Status: {order['status']}")
        print(f"   Gesamt: €{order['total']:.2f}")
        
        # POS Status
        pos_status = order.get('pos_status', 'N/A')
        pos_sent_at = order.get('pos_pushed_at', 'Nicht gesendet')
        
        print(f"\n🏪 ExpertOrder POS:")
        print(f"   Status: {pos_status}")
        
        if pos_status == "sent":
            print(f"   ✅ ERFOLGREICH GESENDET")
            print(f"   Gesendet am: {pos_sent_at}")
        else:
            print(f"   ⏳ Pending oder Fehler")
        
        # Customer
        print(f"\n👤 Kunde:")
        print(f"   Name: {order['customer']['name']}")
        print(f"   Adresse: {order['customer']['address']}")
        print(f"   PLZ/Ort: {order['customer']['postal_code']} {order['customer']['city']}")
        
        # Items
        print(f"\n📦 Artikel:")
        for item in order['items']:
            print(f"   - {item['quantity']}x {item['name']} (€{item['price']:.2f})")
    
    print("\n" + "=" * 70)
    print("✅ VERIFIKATION ABGESCHLOSSEN")
    print("=" * 70)
    
    # Count successful sends
    sent_count = sum(1 for o in orders if o.get('pos_status') == 'sent')
    
    print(f"\n📊 Zusammenfassung:")
    print(f"   Bestellungen erstellt: {len(orders)}")
    print(f"   An ExpertOrder gesendet: {sent_count}")
    
    if sent_count == 2:
        print("\n🎉 BEIDE Bestellungen erfolgreich an ExpertOrder gesendet!")
        print("   ✅ Rellingen: FUNKTIONIERT")
        print("   ✅ Henstedt-Ulzburg: FUNKTIONIERT")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(verify_orders())

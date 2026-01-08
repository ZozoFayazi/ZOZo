"""Set POS config in location document for Rellingen"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def set_pos_config():
    """Set POS config in location document"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 70)
    print("🔧 POS CONFIG IN LOCATION SETZEN - RELLINGEN")
    print("=" * 70)
    
    # Find Rellingen location
    rellingen = await db.locations.find_one({
        "name": {"$regex": "Rellingen", "$options": "i"}
    })
    
    if not rellingen:
        print("❌ Rellingen location not found!")
        return
    
    location_id = rellingen.get('id') or str(rellingen.get('_id'))
    
    print(f"\n📍 Location: {rellingen['name']}")
    print(f"   ID: {location_id}")
    
    # POS Config for ExpertOrder
    pos_config = {
        "provider": "expertorder",
        "enabled": True,
        "api_key": "4bbc443c82674f93e910399ca7931b37b45e55ba",
        "base_url": "https://s1.eocloud.de/c102285",
        "merchant_id": "c102285",
        "broker_name": "zozo-burger.de",
        "test_mode": False
    }
    
    print("\n✅ Setze POS Config in location...")
    print(f"   Provider: {pos_config['provider']}")
    print(f"   Base URL: {pos_config['base_url']}")
    print(f"   Enabled: {pos_config['enabled']}")
    
    # Update location with pos_config
    result = await db.locations.update_one(
        {"_id": rellingen['_id']},
        {"$set": {"pos_config": pos_config}}
    )
    
    if result.modified_count > 0:
        print("\n✅ POS Config erfolgreich in location gespeichert!")
    else:
        print("\n⚠️  Keine Änderungen (vielleicht schon gesetzt?)")
    
    # Verify
    updated_location = await db.locations.find_one({"_id": rellingen['_id']})
    if updated_location.get('pos_config'):
        print("\n🔍 Verifikation:")
        print(f"   Provider: {updated_location['pos_config'].get('provider')}")
        print(f"   Enabled: {updated_location['pos_config'].get('enabled')}")
        print(f"   Base URL: {updated_location['pos_config'].get('base_url')}")
        print("   ✅ POS Config korrekt gesetzt!")
    
    print("\n" + "=" * 70)
    print("✅ POS CONFIG GESETZT")
    print("=" * 70)
    print("\n📝 Backend neu starten: supervisorctl restart backend")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(set_pos_config())

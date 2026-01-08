"""Fix POS config in location document for Rellingen with CORRECT URL"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def fix_pos_config():
    """Fix POS config in location document with CORRECT URL"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 70)
    print("🔧 EXPERTORDER POS CONFIG KORRIGIEREN - RELLINGEN")
    print("=" * 70)
    
    # Find Rellingen location
    rellingen = await db.locations.find_one({
        "name": {"$regex": "Rellingen", "$options": "i"}
    })
    
    if not rellingen:
        print("❌ Rellingen location not found!")
        return
    
    # CORRECT POS Config for ExpertOrder
    # WICHTIG: Base URL ist https://zozo.eocloud.de NICHT s1.eocloud.de/c102285!
    pos_config = {
        "provider": "expertorder",
        "enabled": True,
        "api_key": "4bbc443c82674f93e910399ca7931b37b45e55ba",
        "base_url": "https://zozo.eocloud.de",  # KORREKTE URL!
        "broker_name": "zozo-burger.de",
        "test_mode": False
    }
    
    print(f"\n📍 Location: {rellingen['name']}")
    print(f"   ID: {rellingen.get('id')}")
    
    print("\n✅ Setze KORREKTE POS Config...")
    print(f"   Provider: {pos_config['provider']}")
    print(f"   Base URL: {pos_config['base_url']}")
    print(f"   API Key: {pos_config['api_key'][:20]}...")
    print(f"   Enabled: {pos_config['enabled']}")
    print(f"   Test Mode: {pos_config['test_mode']}")
    
    # Update location with correct pos_config
    result = await db.locations.update_one(
        {"_id": rellingen['_id']},
        {"$set": {"pos_config": pos_config}}
    )
    
    if result.modified_count > 0:
        print("\n✅ POS Config erfolgreich aktualisiert!")
    else:
        print("\n⚠️  Keine Änderungen (vielleicht schon gesetzt?)")
    
    # Verify
    updated_location = await db.locations.find_one({"_id": rellingen['_id']})
    if updated_location.get('pos_config'):
        print("\n🔍 Verifikation:")
        print(f"   Provider: {updated_location['pos_config'].get('provider')}")
        print(f"   Base URL: {updated_location['pos_config'].get('base_url')}")
        print(f"   Enabled: {updated_location['pos_config'].get('enabled')}")
        print("   ✅ POS Config korrekt!")
    
    print("\n" + "=" * 70)
    print("✅ KORREKTE KONFIGURATION GESETZT")
    print("=" * 70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_pos_config())

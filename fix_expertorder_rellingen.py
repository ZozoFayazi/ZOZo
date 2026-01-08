"""Fix ExpertOrder configuration for Rellingen"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# CORRECT ExpertOrder credentials for Rellingen
RELLINGEN_EXPERTORDER_CONFIG = {
    "expertorder_api_key": "4bbc443c82674f93e910399ca7931b37b45e55ba",
    "expertorder_base_url": "https://s1.eocloud.de/c102285",
    "expertorder_merchant_id": "c102285",
    "expertorder_broker_name": "zozo-burger.de",
    "expertorder_enabled": True,
    "expertorder_test_mode": False
}

async def fix_expertorder_config():
    """Fix ExpertOrder configuration for Rellingen"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 70)
    print("🔧 EXPERTORDER KONFIGURATION KORRIGIEREN - RELLINGEN")
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
    
    print("\n✅ Korrigiere ExpertOrder Konfiguration...")
    print(f"   API Key: {RELLINGEN_EXPERTORDER_CONFIG['expertorder_api_key'][:20]}...")
    print(f"   Base URL: {RELLINGEN_EXPERTORDER_CONFIG['expertorder_base_url']}")
    print(f"   Merchant ID: {RELLINGEN_EXPERTORDER_CONFIG['expertorder_merchant_id']}")
    print(f"   Enabled: {RELLINGEN_EXPERTORDER_CONFIG['expertorder_enabled']}")
    print(f"   Test Mode: {RELLINGEN_EXPERTORDER_CONFIG['expertorder_test_mode']}")
    
    # Update location_settings with correct config
    result = await db.location_settings.update_one(
        {"location_id": location_id},
        {"$set": RELLINGEN_EXPERTORDER_CONFIG}
    )
    
    if result.modified_count > 0:
        print("\n✅ Konfiguration erfolgreich aktualisiert!")
    else:
        print("\n⚠️  Keine Änderungen vorgenommen (vielleicht schon korrekt?)")
    
    # Verify
    print("\n🔍 Verifikation...")
    settings = await db.location_settings.find_one({"location_id": location_id})
    
    print(f"   ExpertOrder Enabled: {settings.get('expertorder_enabled')}")
    print(f"   ExpertOrder Base URL: {settings.get('expertorder_base_url')}")
    print(f"   ExpertOrder Merchant ID: {settings.get('expertorder_merchant_id')}")
    print(f"   ExpertOrder API Key: {settings.get('expertorder_api_key')[:20]}... ✅")
    
    print("\n" + "=" * 70)
    print("✅ KONFIGURATION KORRIGIERT")
    print("=" * 70)
    print("\n📝 Hinweis: Backend muss neu gestartet werden:")
    print("   supervisorctl restart backend")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_expertorder_config())

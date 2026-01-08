"""Setup FINAL ExpertOrder configuration for BOTH locations"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# FINALE FUNKTIONIERENDE KONFIGURATION (basierend auf erfolgreichem Test)
EXPERTORDER_BASE_CONFIG = {
    "provider": "expertorder",
    "enabled": True,
    "base_url": "https://zozo.eocloud.de",
    "broker_name": "zozo-burger.de",
    "test_mode": False
}

RELLINGEN_CONFIG = {
    **EXPERTORDER_BASE_CONFIG,
    "api_key": "4bbc443c82674f93e910399ca7931b37b45e55ba"
}

HENSTEDT_CONFIG = {
    **EXPERTORDER_BASE_CONFIG,
    "api_key": "90dd43e5c58b7c2a8ddd1eb4916ae8196d8e1073"
}

async def setup_final_pos_config():
    """Setup final POS configuration for both locations"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 70)
    print("🔧 FINALE EXPERTORDER KONFIGURATION - BEIDE STANDORTE")
    print("=" * 70)
    
    # Find both locations
    rellingen = await db.locations.find_one({"name": {"$regex": "Rellingen", "$options": "i"}})
    henstedt = await db.locations.find_one({"name": {"$regex": "Henstedt", "$options": "i"}})
    
    if not rellingen or not henstedt:
        print("❌ Locations not found!")
        return
    
    locations = [
        ("Rellingen", rellingen, RELLINGEN_CONFIG),
        ("Henstedt-Ulzburg", henstedt, HENSTEDT_CONFIG)
    ]
    
    for name, location, config in locations:
        print(f"\n📍 {name}")
        print(f"   ID: {location.get('id')}")
        
        # Update pos_config in location document
        await db.locations.update_one(
            {"_id": location['_id']},
            {"$set": {"pos_config": config}}
        )
        
        # Also update location_settings (for admin panel)
        await db.location_settings.update_one(
            {"location_id": location.get('id') or str(location['_id'])},
            {
                "$set": {
                    "expertorder_enabled": True,
                    "expertorder_api_key": config['api_key'],
                    "expertorder_base_url": config['base_url'],
                    "expertorder_broker_name": config['broker_name'],
                    "expertorder_test_mode": False,
                    "expertorder_merchant_id": "zozo"
                }
            },
            upsert=True
        )
        
        print(f"   ✅ POS Config gesetzt:")
        print(f"      Provider: {config['provider']}")
        print(f"      Base URL: {config['base_url']}")
        print(f"      Enabled: {config['enabled']}")
        print(f"      API Key: {config['api_key'][:20]}...")
    
    # Remove/disable Cash-X configs
    print(f"\n🗑️  Entferne alte POS-Konfigurationen...")
    
    # Remove any pos_configs collection entries (not used anymore)
    result = await db.pos_configs.delete_many({})
    print(f"   Gelöscht: {result.deleted_count} pos_configs Dokumente")
    
    # Verify
    print(f"\n🔍 Verifikation...")
    for name, location, config in locations:
        updated = await db.locations.find_one({"_id": location['_id']})
        pos_config = updated.get('pos_config', {})
        
        if pos_config.get('provider') == 'expertorder' and pos_config.get('enabled'):
            print(f"   ✅ {name}: ExpertOrder aktiv")
        else:
            print(f"   ❌ {name}: Fehler in Konfiguration")
    
    print("\n" + "=" * 70)
    print("✅ FINALE KONFIGURATION ABGESCHLOSSEN")
    print("=" * 70)
    print("\n📝 Nur ExpertOrder ist jetzt aktiv für beide Standorte")
    print("   Cash-X und andere POS-Systeme wurden entfernt")
    print("\n🔄 Backend neu starten: supervisorctl restart backend")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_final_pos_config())

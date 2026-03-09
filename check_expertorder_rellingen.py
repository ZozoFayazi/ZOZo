"""Check ExpertOrder configuration for Rellingen"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def check_expertorder_config():
    """Check ExpertOrder configuration"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 70)
    print("🔍 EXPERTORDER KONFIGURATION - RELLINGEN")
    print("=" * 70)
    
    # Find Rellingen location
    rellingen = await db.locations.find_one({
        "name": {"$regex": "Rellingen", "$options": "i"}
    })
    
    if not rellingen:
        print("❌ Rellingen location not found!")
        return
    
    location_id = rellingen.get('id') or str(rellingen.get('_id'))
    location_slug = rellingen.get('slug', '')
    
    print(f"\n📍 Location: {rellingen['name']}")
    print(f"   ID: {location_id}")
    print(f"   Slug: {location_slug}")
    
    # Check location_settings
    settings = await db.location_settings.find_one({"location_id": location_id})
    
    print("\n🔧 Location Settings in DB:")
    if settings:
        print(f"   ExpertOrder Enabled: {settings.get('expertorder_enabled', False)}")
        print(f"   ExpertOrder API Key: {'SET' if settings.get('expertorder_api_key') else 'NOT SET'}")
        print(f"   ExpertOrder Test Mode: {settings.get('expertorder_test_mode', 'N/A')}")
        print(f"   ExpertOrder Merchant ID: {settings.get('expertorder_merchant_id', 'NOT SET')}")
        print(f"   ExpertOrder Base URL: {settings.get('expertorder_base_url', 'NOT SET')}")
        
        # Check all keys in settings
        print("\n📋 Alle Keys in location_settings:")
        for key in settings.keys():
            if key not in ['_id', 'created_at', 'updated_at']:
                value = settings[key]
                if 'key' in key.lower() or 'secret' in key.lower():
                    value = '***' if value else 'NOT SET'
                print(f"   {key}: {value}")
    else:
        print("   ❌ Keine Settings gefunden!")
    
    # Check pos_configs collection
    print("\n🏪 POS Configs Collection:")
    pos_config = await db.pos_configs.find_one({"location_slug": location_slug})
    
    if pos_config:
        print(f"   Provider: {pos_config.get('provider', 'N/A')}")
        print(f"   Enabled: {pos_config.get('enabled', False)}")
        print(f"   API Key: {'SET' if pos_config.get('api_key') else 'NOT SET'}")
        print(f"   Base URL: {pos_config.get('base_url', 'NOT SET')}")
    else:
        print("   ⚠️  Keine POS Config gefunden")
    
    # Also check by location_id
    pos_config_by_id = await db.pos_configs.find_one({"location_id": location_id})
    if pos_config_by_id and pos_config_by_id != pos_config:
        print("\n   📋 Gefunden via location_id:")
        print(f"   Provider: {pos_config_by_id.get('provider', 'N/A')}")
        print(f"   Enabled: {pos_config_by_id.get('enabled', False)}")
    
    print("\n" + "=" * 70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_expertorder_config())

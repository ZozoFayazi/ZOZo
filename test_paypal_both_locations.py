"""Test PayPal Integration for both locations"""
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def test_paypal_integration():
    """Test PayPal configuration for both locations"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 70)
    print("🧪 PAYPAL INTEGRATION TEST - BEIDE STANDORTE")
    print("=" * 70)
    
    all_valid = True
    
    # Test both locations
    locations = [
        {"name_pattern": "Rellingen", "city": "Rellingen"},
        {"name_pattern": "Henstedt", "city": "Henstedt-Ulzburg"}
    ]
    
    for loc_info in locations:
        print(f"\n{'=' * 70}")
        print(f"📍 Testing: {loc_info['city']}")
        print('=' * 70)
        
        # Find location
        location = await db.locations.find_one({
            "name": {"$regex": loc_info['name_pattern'], "$options": "i"}
        })
        
        if not location:
            print(f"❌ {loc_info['city']} location not found!")
            all_valid = False
            continue
        
        location_id = location.get('id') or str(location.get('_id'))
        location_name = location.get('name')
        
        print(f"\n📌 Location: {location_name}")
        print(f"   ID: {location_id}")
        
        # Get PayPal settings
        settings = await db.location_settings.find_one({"location_id": location_id})
        
        if not settings:
            print(f"\n❌ No settings found for {loc_info['city']}!")
            all_valid = False
            continue
        
        print("\n💳 PayPal Configuration:")
        print(f"   Enabled: {settings.get('paypal_enabled', False)}")
        print(f"   Mode: {'LIVE' if not settings.get('paypal_sandbox_mode', True) else 'SANDBOX'}")
        print(f"   Client ID: {settings.get('paypal_client_id', 'NOT SET')[:30]}...")
        print(f"   Secret: {'SET' if settings.get('paypal_client_secret') else 'NOT SET'}")
        
        # Validation
        print("\n✅ Validation:")
        location_errors = []
        
        if not settings.get('paypal_enabled'):
            location_errors.append(f"❌ PayPal is not enabled for {loc_info['city']}")
            all_valid = False
        else:
            print(f"   ✓ PayPal is enabled")
        
        if not settings.get('paypal_client_id'):
            location_errors.append(f"❌ Client ID is missing for {loc_info['city']}")
            all_valid = False
        else:
            print(f"   ✓ Client ID is configured")
        
        if not settings.get('paypal_client_secret'):
            location_errors.append(f"❌ Client Secret is missing for {loc_info['city']}")
            all_valid = False
        else:
            print(f"   ✓ Client Secret is configured")
        
        # Mode check
        if settings.get('paypal_sandbox_mode'):
            print(f"   ⚠️  Running in SANDBOX mode (test)")
        else:
            print(f"   ✓ Running in LIVE mode (production)")
        
        if location_errors:
            for error in location_errors:
                print(f"\n   {error}")
    
    print("\n" + "=" * 70)
    
    if all_valid:
        print("\n✅ PayPal configuration is valid for BEIDE Standorte!")
        print("\n📝 Beide Standorte sind bereit:")
        print("   ✓ ZOZO Burger Rellingen")
        print("   ✓ ZOZO Burger Henstedt-Ulzburg")
        print("\n🔗 Test URL: https://zozo-burger-1.preview.emergentagent.com")
        print("\n💡 Hinweis: Zahlungen werden standort-spezifisch auf die jeweiligen")
        print("   PayPal-Konten gebucht.")
    else:
        print("\n❌ Configuration has errors - see details above")
        sys.exit(1)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_paypal_integration())

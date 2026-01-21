"""Test PayPal Integration for ZOZO Burger"""
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
    """Test PayPal configuration"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 60)
    print("🧪 PAYPAL INTEGRATION TEST")
    print("=" * 60)
    
    # Find Henstedt-Ulzburg location
    henstedt_location = await db.locations.find_one({
        "name": {"$regex": "Henstedt", "$options": "i"}
    })
    
    if not henstedt_location:
        print("❌ Henstedt-Ulzburg location not found!")
        sys.exit(1)
    
    location_id = henstedt_location.get('id') or str(henstedt_location.get('_id'))
    location_name = henstedt_location.get('name')
    
    print(f"\n📍 Location: {location_name}")
    print(f"   ID: {location_id}")
    
    # Get PayPal settings
    settings = await db.location_settings.find_one({"location_id": location_id})
    
    if not settings:
        print("\n❌ No settings found for this location!")
        sys.exit(1)
    
    print("\n💳 PayPal Configuration:")
    print(f"   Enabled: {settings.get('paypal_enabled', False)}")
    print(f"   Mode: {'LIVE' if not settings.get('paypal_sandbox_mode', True) else 'SANDBOX'}")
    print(f"   Client ID: {settings.get('paypal_client_id', 'NOT SET')[:30]}...")
    print(f"   Secret: {'SET' if settings.get('paypal_client_secret') else 'NOT SET'}")
    
    # Validation
    print("\n✅ Validation:")
    errors = []
    
    if not settings.get('paypal_enabled'):
        errors.append("❌ PayPal is not enabled")
    else:
        print("   ✓ PayPal is enabled")
    
    if not settings.get('paypal_client_id'):
        errors.append("❌ Client ID is missing")
    else:
        print("   ✓ Client ID is configured")
    
    if not settings.get('paypal_client_secret'):
        errors.append("❌ Client Secret is missing")
    else:
        print("   ✓ Client Secret is configured")
    
    # Mode check
    if settings.get('paypal_sandbox_mode'):
        print("   ⚠️  Running in SANDBOX mode (test)")
    else:
        print("   ✓ Running in LIVE mode (production)")
    
    print("\n" + "=" * 60)
    
    if errors:
        print("\n❌ Configuration has errors:")
        for error in errors:
            print(f"   {error}")
        sys.exit(1)
    else:
        print("\n✅ PayPal configuration is valid!")
        print("\n📝 Next Steps:")
        print("   1. Place a test order via the website")
        print("   2. Select 'Henstedt-Ulzburg' as location")
        print("   3. Choose 'PayPal' as payment method")
        print("   4. Complete the order and verify PayPal payment")
        print("\n🔗 Test URL: https://foodorder-fix.preview.emergentagent.com")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_paypal_integration())

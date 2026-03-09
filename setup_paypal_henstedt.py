"""Setup PayPal credentials for Henstedt-Ulzburg location"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# PayPal Credentials for Henstedt-Ulzburg
HENSTEDT_PAYPAL_CLIENT_ID = "AWac3d_1EW-cqqAKNYOkOQM6_THWw3jLKGREqFS4heb5jn2TIFHcWcK6E6hNBRirXD3XP5cBhT8w6R8Q"
HENSTEDT_PAYPAL_SECRET = "ECLyn3S30HV4QNiN8gOCFLv--0tp0Zi3FwOBxeRliIcTWzSi-EA0HP03B22_VYFEHC4CdRxRnUBTK1qh"

async def setup_paypal_credentials():
    """Setup PayPal credentials for Henstedt-Ulzburg"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔍 Finding Henstedt-Ulzburg location...")
    
    # Find Henstedt-Ulzburg location
    henstedt_location = await db.locations.find_one({
        "name": {"$regex": "Henstedt", "$options": "i"}
    })
    
    if not henstedt_location:
        print("❌ Henstedt-Ulzburg location not found!")
        return
    
    location_id = henstedt_location.get('id') or str(henstedt_location.get('_id'))
    location_name = henstedt_location.get('name')
    
    print(f"✅ Found location: {location_name} (ID: {location_id})")
    
    # Check if settings already exist
    existing_settings = await db.location_settings.find_one({"location_id": location_id})
    
    if existing_settings:
        print(f"📝 Updating existing PayPal settings...")
        await db.location_settings.update_one(
            {"location_id": location_id},
            {
                "$set": {
                    "paypal_client_id": HENSTEDT_PAYPAL_CLIENT_ID,
                    "paypal_client_secret": HENSTEDT_PAYPAL_SECRET,
                    "paypal_enabled": True,
                    "paypal_sandbox_mode": False,  # Live mode
                    "updated_at": "2025-01-01T00:00:00"
                }
            }
        )
    else:
        print(f"➕ Creating new PayPal settings...")
        await db.location_settings.insert_one({
            "location_id": location_id,
            "paypal_client_id": HENSTEDT_PAYPAL_CLIENT_ID,
            "paypal_client_secret": HENSTEDT_PAYPAL_SECRET,
            "paypal_enabled": True,
            "paypal_sandbox_mode": False,  # Live mode
            "created_at": "2025-01-01T00:00:00"
        })
    
    print(f"\n✅ PayPal configuration completed for {location_name}!")
    print(f"   Client ID: {HENSTEDT_PAYPAL_CLIENT_ID[:20]}...")
    print(f"   Mode: LIVE (Production)")
    print(f"   Status: ENABLED")
    
    # Verify
    updated_settings = await db.location_settings.find_one({"location_id": location_id})
    if updated_settings and updated_settings.get('paypal_client_id') == HENSTEDT_PAYPAL_CLIENT_ID:
        print("\n✅ Verification successful - PayPal credentials saved correctly!")
    else:
        print("\n⚠️  Verification failed - please check database")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_paypal_credentials())

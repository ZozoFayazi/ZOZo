"""Setup PayPal credentials for Rellingen location"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# PayPal Credentials for Rellingen
RELLINGEN_PAYPAL_CLIENT_ID = "AQIFU1U2x5bjA1c4IRrC2PsMUh12DKC-ef8VHIakDAaG4WFz9PgFgm0eno-YcIVZtV9A_A4V7b7cQqUe"
RELLINGEN_PAYPAL_SECRET = "EIFuFZh95NOJ-DaQczZTTAK_Tk4WSMkc7-fXhEK7lfV-uQxb-g40JKbdXQ7YccExKh6p84BWgUJwuwqV"

async def setup_paypal_credentials():
    """Setup PayPal credentials for Rellingen"""
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🔍 Finding Rellingen location...")
    
    # Find Rellingen location
    rellingen_location = await db.locations.find_one({
        "name": {"$regex": "Rellingen", "$options": "i"}
    })
    
    if not rellingen_location:
        print("❌ Rellingen location not found!")
        return
    
    location_id = rellingen_location.get('id') or str(rellingen_location.get('_id'))
    location_name = rellingen_location.get('name')
    
    print(f"✅ Found location: {location_name} (ID: {location_id})")
    
    # Check if settings already exist
    existing_settings = await db.location_settings.find_one({"location_id": location_id})
    
    if existing_settings:
        print(f"📝 Updating existing PayPal settings...")
        await db.location_settings.update_one(
            {"location_id": location_id},
            {
                "$set": {
                    "paypal_client_id": RELLINGEN_PAYPAL_CLIENT_ID,
                    "paypal_client_secret": RELLINGEN_PAYPAL_SECRET,
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
            "paypal_client_id": RELLINGEN_PAYPAL_CLIENT_ID,
            "paypal_client_secret": RELLINGEN_PAYPAL_SECRET,
            "paypal_enabled": True,
            "paypal_sandbox_mode": False,  # Live mode
            "created_at": "2025-01-01T00:00:00"
        })
    
    print(f"\n✅ PayPal configuration completed for {location_name}!")
    print(f"   Client ID: {RELLINGEN_PAYPAL_CLIENT_ID[:20]}...")
    print(f"   Mode: LIVE (Production)")
    print(f"   Status: ENABLED")
    
    # Verify
    updated_settings = await db.location_settings.find_one({"location_id": location_id})
    if updated_settings and updated_settings.get('paypal_client_id') == RELLINGEN_PAYPAL_CLIENT_ID:
        print("\n✅ Verification successful - PayPal credentials saved correctly!")
    else:
        print("\n⚠️  Verification failed - please check database")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_paypal_credentials())

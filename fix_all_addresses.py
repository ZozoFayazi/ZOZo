"""Fix all addresses to correct values"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

CORRECT_ADDRESSES = {
    "rellingen": {
        "address": "Möwenstraße 2, 25462 Rellingen",
        "street": "Möwenstraße 2",
        "postal_code": "25462",
        "city": "Rellingen"
    },
    "henstedt-ulzburg": {
        "address": "Edisonstraße 11, 24558 Henstedt-Ulzburg",
        "street": "Edisonstraße 11",
        "postal_code": "24558",
        "city": "Henstedt-Ulzburg"
    }
}

async def fix_addresses():
    """Fix addresses in database"""
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ.get('DB_NAME', 'test_database')]
    
    print("=" * 70)
    print("🔧 ADRESSEN KORRIGIEREN")
    print("=" * 70)
    
    for slug, correct_addr in CORRECT_ADDRESSES.items():
        print(f"\n📍 {slug.upper()}:")
        
        location = await db.locations.find_one({"slug": slug})
        
        if not location:
            print(f"   ❌ Location nicht gefunden!")
            continue
        
        print(f"   Alte Adresse: {location.get('address', 'N/A')}")
        print(f"   Neue Adresse: {correct_addr['address']}")
        
        # Update location
        await db.locations.update_one(
            {"_id": location['_id']},
            {"$set": {
                "address": correct_addr['address'],
                "street": correct_addr['street'],
                "postal_code": correct_addr['postal_code'],
                "city": correct_addr['city']
            }}
        )
        
        print(f"   ✅ Adresse aktualisiert!")
    
    # Verify
    print("\n" + "=" * 70)
    print("🔍 VERIFIKATION")
    print("=" * 70)
    
    for slug, correct_addr in CORRECT_ADDRESSES.items():
        location = await db.locations.find_one({"slug": slug})
        
        if location:
            db_addr = location.get('address', '')
            if db_addr == correct_addr['address']:
                print(f"\n✅ {slug.upper()}: {db_addr}")
            else:
                print(f"\n❌ {slug.upper()}: Fehler - {db_addr}")
    
    print("\n" + "=" * 70)
    print("✅ ADRESSEN KORRIGIERT")
    print("=" * 70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_addresses())

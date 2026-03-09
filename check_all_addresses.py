"""Check all addresses in the system"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# KORREKTE ADRESSEN
CORRECT_ADDRESSES = {
    "rellingen": {
        "street": "Möwenstraße 2",
        "postal_code": "25462",
        "city": "Rellingen",
        "full": "Möwenstraße 2, 25462 Rellingen"
    },
    "henstedt": {
        "street": "Edisonstraße 11",
        "postal_code": "24558",
        "city": "Henstedt-Ulzburg",
        "full": "Edisonstraße 11, 24558 Henstedt-Ulzburg"
    }
}

async def check_addresses():
    """Check all addresses in database and files"""
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ.get('DB_NAME', 'test_database')]
    
    print("=" * 70)
    print("🔍 ADRESS-ÜBERPRÜFUNG")
    print("=" * 70)
    
    errors = []
    
    # Check locations in database
    print("\n📍 Datenbank - locations Collection:")
    
    for slug, correct in CORRECT_ADDRESSES.items():
        location = await db.locations.find_one({"slug": slug})
        
        if not location:
            print(f"\n❌ {slug.capitalize()}: NICHT GEFUNDEN!")
            errors.append(f"{slug} location not found in database")
            continue
        
        print(f"\n📌 {location.get('name')}:")
        
        # Check address
        db_address = location.get('address', '')
        db_street = location.get('street', '')
        db_city = location.get('city', '')
        db_postal = location.get('postal_code', '')
        
        print(f"   Adresse (DB): {db_address}")
        print(f"   Street (DB): {db_street}")
        print(f"   City (DB): {db_city}")
        print(f"   PLZ (DB): {db_postal}")
        
        print(f"\n   ✓ KORREKT: {correct['full']}")
        
        # Validation
        issues = []
        
        # Check if full address matches
        if db_address and correct['full'] not in db_address and db_address != correct['full']:
            issues.append(f"address: '{db_address}' != '{correct['full']}'")
        
        # Check street
        if db_street and db_street != correct['street']:
            issues.append(f"street: '{db_street}' != '{correct['street']}'")
        
        # Check city
        if db_city and db_city != correct['city']:
            issues.append(f"city: '{db_city}' != '{correct['city']}'")
        
        # Check postal code
        if db_postal and db_postal != correct['postal_code']:
            issues.append(f"postal_code: '{db_postal}' != '{correct['postal_code']}'")
        
        if issues:
            print(f"\n   ❌ FEHLER gefunden:")
            for issue in issues:
                print(f"      - {issue}")
            errors.extend(issues)
        else:
            print(f"   ✅ Adresse korrekt!")
    
    print("\n" + "=" * 70)
    
    if errors:
        print(f"\n❌ {len(errors)} FEHLER GEFUNDEN!")
        print("\n🔧 Korrekturen erforderlich:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("\n✅ ALLE ADRESSEN KORREKT!")
    
    print("\n📝 Korrekte Adressen:")
    print(f"   Rellingen: {CORRECT_ADDRESSES['rellingen']['full']}")
    print(f"   Henstedt-Ulzburg: {CORRECT_ADDRESSES['henstedt']['full']}")
    
    client.close()
    return errors

if __name__ == "__main__":
    errors = asyncio.run(check_addresses())
    exit(1 if errors else 0)

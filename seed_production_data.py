#!/usr/bin/env python3
"""
Production Data Seed Script
Führen Sie dieses Script nach jedem Re-Deployment aus!

Synchronisiert alle Datenbank-Änderungen vom Preview-System:
- PLZ-Listen (44 PLZ)
- Stadt-Regeln (13 Städte)
- LUNCH20 Rabatt-Code
- Burger Builder Zutaten
"""

import sys
sys.path.insert(0, '/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from datetime import datetime, timezone
import uuid

async def seed_data():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("="*80)
    print("🌱 PRODUCTION DATA SEED")
    print("="*80)
    print(f"Database: {db_name}")
    print()
    
    # 1. LIEFERGEBIETE ERWEITERN
    print("1️⃣ Erweitere Liefergebiete...")
    print("-"*80)
    
    # Rellingen
    rellingen_plz = [
        "21465", "21493", "22457", "22459", "22523", "22525", "22527", "22529",
        "22547", "22549", "22587", "22589", "22605", "22607", "22609", "22761",
        "22763", "22869", "25421", "25462", "25469", "25474"
    ]
    
    rellingen_mbw = {plz: 12.00 for plz in rellingen_plz}
    rellingen_mbw["25462"] = 10.00  # Kern-Gebiet
    rellingen_mbw["25469"] = 10.00
    
    rellingen_cities = {
        "quickborn": 15.00,
        "hamburg-schnelsen": 12.00,
        "hamburg-stellingen": 12.00,
        "hamburg-lokstedt": 12.00,
        "hamburg-blankenese": 15.00,
        "schenefeld": 12.00,
        "halstenbek": 12.00
    }
    
    rellingen = await db.locations.find_one({"slug": "rellingen"})
    if rellingen:
        await db.locations.update_one(
            {"slug": "rellingen"},
            {"$set": {
                "delivery_zone.postal_codes": rellingen_plz,
                "delivery_zone.postal_code_mbw": rellingen_mbw,
                "delivery_zone.city_mbw_rules": rellingen_cities
            }}
        )
        print(f"✅ Rellingen: {len(rellingen_plz)} PLZ + {len(rellingen_cities)} Städte")
    
    # Henstedt
    henstedt_plz = [
        "22844", "22846", "22848", "22850", "22851", "22889", "22946", "22952",
        "23611", "23795", "23843", "23879", "24558", "24568", "24576", "24582",
        "24594", "24601", "24610", "24629", "25451", "25486"
    ]
    
    henstedt_mbw = {plz: 15.00 for plz in henstedt_plz}
    henstedt_mbw["24558"] = 12.00  # Kern-Gebiet
    
    henstedt_cities = {
        "wakendorf": 10.00,
        "kaltenkirchen": 15.00,
        "norderstedt": 12.00,
        "bad segeberg": 18.00,
        "ellerau": 15.00,
        "quickborn": 15.00,
        "tangstedt": 12.00
    }
    
    henstedt = await db.locations.find_one({"slug": "henstedt-ulzburg"})
    if henstedt:
        await db.locations.update_one(
            {"slug": "henstedt-ulzburg"},
            {"$set": {
                "delivery_zone.postal_codes": henstedt_plz,
                "delivery_zone.postal_code_mbw": henstedt_mbw,
                "delivery_zone.city_mbw_rules": henstedt_cities
            }}
        )
        print(f"✅ Henstedt: {len(henstedt_plz)} PLZ + {len(henstedt_cities)} Städte")
    
    print()
    
    # 2. LUNCH20 RABATT-CODE
    print("2️⃣ Erstelle LUNCH20 Rabatt-Code...")
    print("-"*80)
    
    location_ids = []
    if rellingen:
        location_ids.append(rellingen.get("id") or str(rellingen.get("_id")))
    if henstedt:
        location_ids.append(henstedt.get("id") or str(henstedt.get("_id")))
    
    lunch20 = await db.discount_codes.find_one({"code": "LUNCH20"})
    
    if not lunch20:
        discount_code = {
            "id": str(uuid.uuid4()),
            "code": "LUNCH20",
            "discount_type": "percentage",
            "discount_value": 20,
            "min_order_value": 40.00,
            "max_uses": None,
            "used_count": 0,
            "valid_from": datetime.now(timezone.utc),
            "valid_until": datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
            "active": True,
            "applicable_locations": location_ids,
            "description": "20% Rabatt ab €40 MBW - Mo-Fr 11-15 Uhr",
            "time_restrictions": {
                "enabled": True,
                "days_of_week": [0, 1, 2, 3, 4],
                "time_from": "11:00",
                "time_until": "15:00",
                "timezone": "Europe/Berlin"
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.discount_codes.insert_one(discount_code)
        print("✅ LUNCH20 Code erstellt")
    else:
        print("⚠️ LUNCH20 existiert bereits")
    
    print()
    
    # 3. BURGER BUILDER ZUTATEN
    print("3️⃣ Initialisiere Burger Builder Zutaten...")
    print("-"*80)
    
    count = await db.burger_builder_ingredients.count_documents({})
    if count == 0:
        from burger_builder_service import BurgerBuilderService
        service = BurgerBuilderService(db)
        await service.initialize_default_ingredients()
        print("✅ Burger Builder Zutaten initialisiert")
    else:
        print(f"⚠️ Burger Builder bereits initialisiert ({count} Zutaten)")
    
    print()
    print("="*80)
    print("✅ PRODUCTION DATA SEED ABGESCHLOSSEN!")
    print("="*80)
    print()
    print("Nächste Schritte:")
    print("1. Validation: python /app/validate_critical_code.py")
    print("2. PLZ-Check: Testen Sie PLZ 22457")
    print("3. Rabatt-Test: Testen Sie LUNCH20 (Mo-Fr 11-15 Uhr)")
    print("4. Burger Builder: Testen Sie /burger-builder")
    print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())

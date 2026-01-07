#!/usr/bin/env python3
"""
ZOZO Burger - Konfiguration verifizieren

Dieses Script prüft, ob alle wichtigen Konfigurationen
korrekt in der Datenbank gespeichert sind.

Verwendung:
    python3 /app/verify_config.py
"""

from pymongo import MongoClient
import os

def verify_config():
    """Verifiziert alle wichtigen Konfigurationen"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_url)
    db = client['test_database']
    
    print("\n" + "="*70)
    print("   ZOZO BURGER - KONFIGURATIONS-VERIFIKATION")
    print("="*70 + "\n")
    
    errors = []
    warnings = []
    success = []
    
    # 1. Prüfe Locations
    print("📍 STANDORTE:")
    locations = list(db.locations.find({}))
    if len(locations) >= 2:
        print(f"   ✅ {len(locations)} Standorte gefunden")
        for loc in locations:
            print(f"      - {loc['name']}")
        success.append("Locations OK")
    else:
        errors.append("Nicht genug Standorte in Datenbank")
        print(f"   ❌ Nur {len(locations)} Standorte!")
    
    print()
    
    # 2. Prüfe ExpertOrder Konfiguration
    print("🔗 EXPERTORDER INTEGRATION:")
    
    for loc in locations:
        loc_name = loc['name'].replace('ZOZO Burger ', '')
        settings = db.location_settings.find_one({'location_id': loc['id']})
        
        if settings and settings.get('expertorder_enabled'):
            api_key = settings.get('expertorder_api_key', '')
            base_url = settings.get('expertorder_base_url', '')
            
            print(f"   ✅ {loc_name}:")
            print(f"      Base URL: {base_url}")
            print(f"      API Key: ***{api_key[-8:] if api_key else 'FEHLT'}")
            print(f"      Status: {'LIVE' if not settings.get('expertorder_test_mode') else 'TEST'}")
            
            # Validierung
            if not api_key:
                errors.append(f"{loc_name}: API Key fehlt")
            elif base_url != "https://zozo.eocloud.de":
                warnings.append(f"{loc_name}: Base URL ist nicht https://zozo.eocloud.de")
            else:
                success.append(f"ExpertOrder {loc_name} OK")
        else:
            errors.append(f"{loc_name}: ExpertOrder nicht konfiguriert")
            print(f"   ❌ {loc_name}: NICHT KONFIGURIERT")
        
        print()
    
    # 3. Prüfe Admin-Accounts
    print("👤 ADMIN-ACCOUNTS:")
    
    required_admins = [
        "admin@zonik-solutions.de",
        "info@zozo-burger.de"
    ]
    
    for email in required_admins:
        admin = db.admins.find_one({'email': email})
        if admin:
            print(f"   ✅ {email}")
            print(f"      Rolle: {admin.get('role', 'N/A')}")
            success.append(f"Admin {email} OK")
        else:
            errors.append(f"Admin-Account {email} fehlt")
            print(f"   ❌ {email} - NICHT GEFUNDEN!")
    
    print()
    
    # 4. Prüfe Menu Items
    print("🍔 MENU:")
    menu_count = db.menu_items.count_documents({})
    if menu_count >= 100:
        print(f"   ✅ {menu_count} Produkte in Datenbank")
        success.append("Menu Items OK")
    else:
        warnings.append(f"Nur {menu_count} Produkte (erwartet: 150+)")
        print(f"   ⚠️  Nur {menu_count} Produkte")
    
    print()
    
    # 5. Prüfe Categories
    print("📂 KATEGORIEN:")
    cat_count = db.categories.count_documents({})
    if cat_count >= 10:
        print(f"   ✅ {cat_count} Kategorien")
        success.append("Categories OK")
    else:
        warnings.append(f"Nur {cat_count} Kategorien")
        print(f"   ⚠️  Nur {cat_count} Kategorien")
    
    print()
    
    # ZUSAMMENFASSUNG
    print("="*70)
    print("   ZUSAMMENFASSUNG")
    print("="*70)
    print(f"\n✅ Erfolgreich: {len(success)}")
    for s in success:
        print(f"   ✅ {s}")
    
    if warnings:
        print(f"\n⚠️  Warnungen: {len(warnings)}")
        for w in warnings:
            print(f"   ⚠️  {w}")
    
    if errors:
        print(f"\n❌ Fehler: {len(errors)}")
        for e in errors:
            print(f"   ❌ {e}")
        print("\n⚠️  ACHTUNG: Es gibt kritische Fehler!")
        print("   Führen Sie /app/restore_expertorder_config.py aus")
    else:
        print("\n🎉 KEINE FEHLER - ALLES IST KORREKT KONFIGURIERT!")
        print("   Die Website ist 100% GO-LIVE bereit!")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    verify_config()

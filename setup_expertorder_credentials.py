#!/usr/bin/env python3
"""
ExpertOrder POS Credentials Setup für ZOZO Burger

ANLEITUNG:
1. Dieses Script mit Ihren echten Credentials ausführen
2. Die Platzhalter durch echte Werte ersetzen
3. Ausführen: python3 /app/setup_expertorder_credentials.py

Nach Ausführung sind beide Standorte für ExpertOrder konfiguriert.
"""

from pymongo import MongoClient
import os
from datetime import datetime

# MongoDB Connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(mongo_url)
db = client['test_database']

# ========================================
# HIER IHRE CREDENTIALS EINTRAGEN:
# ========================================

RELLINGEN_CONFIG = {
    "merchant_id": "HIER_MERCHANT_ID_EINTRAGEN",  # z.B. "c102285"
    "api_key": "HIER_API_KEY_EINTRAGEN",           # Ihr ExpertOrder API Key
    "test_mode": False  # False für LIVE, True für Test-Modus
}

HENSTEDT_CONFIG = {
    "merchant_id": "HIER_MERCHANT_ID_EINTRAGEN",  # z.B. "c102286" oder gleiche wie Rellingen
    "api_key": "HIER_API_KEY_EINTRAGEN",           # Ihr ExpertOrder API Key
    "test_mode": False  # False für LIVE, True für Test-Modus
}

# Gemeinsame Einstellungen
BROKER_NAME = "zozo-burger.de"

# ========================================
# AB HIER NICHTS ÄNDERN
# ========================================

def setup_location(location_id, location_name, config):
    """Setup ExpertOrder für einen Standort"""
    
    # Prüfen ob Platzhalter noch vorhanden
    if "HIER_" in config["merchant_id"] or "HIER_" in config["api_key"]:
        print(f"⚠️  {location_name}: Credentials noch nicht eingetragen!")
        return False
    
    # Base URL konstruieren
    base_url = f"https://s1.eocloud.de/{config['merchant_id']}"
    
    # ExpertOrder Konfiguration
    expertorder_config = {
        "enabled": True,
        "base_url": base_url,
        "merchant_id": config["merchant_id"],
        "api_key": config["api_key"],
        "broker_name": BROKER_NAME,
        "test_mode": config["test_mode"],
        "updated_at": datetime.utcnow()
    }
    
    # In Datenbank speichern
    result = db.location_settings.update_one(
        {"location_id": location_id},
        {
            "$set": {
                "location_id": location_id,
                "expertorder": expertorder_config,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    mode = "TEST-MODUS" if config["test_mode"] else "LIVE"
    print(f"✅ {location_name}: ExpertOrder konfiguriert ({mode})")
    print(f"   - Base URL: {base_url}")
    print(f"   - Broker: {BROKER_NAME}")
    print(f"   - API Key: ***{config['api_key'][-4:]}")
    return True

def main():
    print("\n" + "="*60)
    print("   ZOZO Burger - ExpertOrder POS Setup")
    print("="*60 + "\n")
    
    # Location IDs aus Datenbank holen
    rellingen = db.locations.find_one({"name": {"$regex": "Rellingen", "$options": "i"}})
    henstedt = db.locations.find_one({"name": {"$regex": "Henstedt", "$options": "i"}})
    
    if not rellingen or not henstedt:
        print("❌ Standorte nicht in Datenbank gefunden!")
        return
    
    success_count = 0
    
    # Rellingen einrichten
    if setup_location(rellingen['id'], "Rellingen", RELLINGEN_CONFIG):
        success_count += 1
    
    print()
    
    # Henstedt-Ulzburg einrichten
    if setup_location(henstedt['id'], "Henstedt-Ulzburg", HENSTEDT_CONFIG):
        success_count += 1
    
    print("\n" + "="*60)
    if success_count == 2:
        print("✅ SETUP ERFOLGREICH ABGESCHLOSSEN!")
        print("   Beide Standorte sind für ExpertOrder konfiguriert.")
        print("\n📋 NÄCHSTE SCHRITTE:")
        print("   1. Testbestellung aufgeben")
        print("   2. In ExpertOrder Dashboard prüfen")
        print("   3. Bei Erfolg: test_mode auf False setzen")
    elif success_count == 0:
        print("⚠️  KEINE CREDENTIALS EINGETRAGEN")
        print("   Bitte tragen Sie Ihre Merchant IDs und API Keys ein.")
        print("   Öffnen Sie diese Datei und ersetzen Sie die Platzhalter.")
    else:
        print(f"⚠️  NUR {success_count}/2 STANDORTE KONFIGURIERT")
        print("   Bitte prüfen Sie die Credentials.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

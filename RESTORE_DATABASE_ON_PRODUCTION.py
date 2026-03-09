#!/usr/bin/env python3
"""
🚨 NOTFALL-SCRIPT: Datenbank auf Production (zozo-burger.de) wiederherstellen

WICHTIG: Dieses Script muss auf dem SERVER ausgeführt werden, wo zozo-burger.de läuft!

Verwendung:
1. SSH auf Ihren Production-Server
2. Navigieren Sie zum App-Verzeichnis
3. Führen Sie aus: python3 RESTORE_DATABASE_ON_PRODUCTION.py
"""

import json
import os
from pymongo import MongoClient
from datetime import datetime

# === CONFIGURATION ===
# WICHTIG: Passen Sie diese Werte für Ihre Production-Umgebung an!
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
BACKUP_FILE = '/app/backups/ABSOLUTE_FINAL_COMPLETE_FREEZE_20260121_105946.json'

# === BACKUP PATH ===
# Falls das Backup woanders liegt, passen Sie den Pfad an
if not os.path.exists(BACKUP_FILE):
    print(f"❌ ERROR: Backup file not found: {BACKUP_FILE}")
    print(f"   Please upload the backup file to your server first!")
    exit(1)

print("=" * 60)
print("🚨 NOTFALL-DATENBANK-WIEDERHERSTELLUNG")
print("=" * 60)
print(f"\nMongoDB URL: {MONGO_URL}")
print(f"Database: {DB_NAME}")
print(f"Backup File: {BACKUP_FILE}")
print(f"\n⚠️  WARNUNG: Dies wird ALLE aktuellen Daten überschreiben!")
print("⚠️  Alle Bestellungen nach dem 21.01.2026 10:59 Uhr gehen verloren!")
print("\n" + "=" * 60)

# Safety confirmation
response = input("\n❓ Sind Sie ABSOLUT SICHER? Tippen Sie 'JA RESTORE' ein: ")
if response != "JA RESTORE":
    print("❌ Abbruch. Keine Änderungen vorgenommen.")
    exit(0)

print("\n🔄 Starte Wiederherstellung...")

try:
    # Load backup
    print("📂 Lade Backup-Datei...")
    with open(BACKUP_FILE, 'r') as f:
        backup_data = json.load(f)
    
    print(f"✅ Backup geladen: {len(backup_data)} Collections")
    
    # Connect to MongoDB
    print(f"🔌 Verbinde mit MongoDB...")
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.server_info()
    print("✅ MongoDB Verbindung erfolgreich")
    
    db = client[DB_NAME]
    
    # Create emergency backup of current state
    print("\n💾 Erstelle Emergency-Backup des aktuellen Zustands...")
    emergency_backup = {
        'timestamp': datetime.now().isoformat(),
        'collections': {}
    }
    
    for coll_name in db.list_collection_names():
        docs = list(db[coll_name].find({}))
        emergency_backup['collections'][coll_name] = docs
        print(f"   - Gesichert: {coll_name} ({len(docs)} docs)")
    
    emergency_filename = f'/app/backups/EMERGENCY_BEFORE_RESTORE_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(emergency_filename, 'w') as f:
        json.dump(emergency_backup, f, default=str, indent=2)
    
    print(f"✅ Emergency-Backup erstellt: {emergency_filename}")
    
    # Restore each collection
    print("\n🔄 Stelle Datenbank wieder her...")
    for coll_name, documents in backup_data.items():
        if documents and isinstance(documents, list):
            print(f"   ⚙️  {coll_name}: {len(documents)} Dokumente...")
            db[coll_name].delete_many({})
            if documents:
                db[coll_name].insert_many(documents)
            print(f"      ✅ Fertig")
    
    # Verification
    print("\n🎯 VERIFIKATION:")
    
    # Check burger structure
    burger = db.menu_items.find_one({"name": {"$regex": "Hamburger", "$options": "i"}})
    if burger:
        print(f"✅ Hamburger gefunden:")
        print(f"   Name: {burger.get('name')}")
        print(f"   Preis Medium: €{burger.get('price_medium')}")
        print(f"   Preis Large: €{burger.get('price_large')}")
        print(f"   Größen-Labels: {burger.get('size_labels')}")
    else:
        print("❌ WARNUNG: Kein Hamburger gefunden!")
    
    # Check locations
    locs = list(db.locations.find({}))
    print(f"\n✅ Standorte: {len(locs)}")
    for loc in locs:
        print(f"   - {loc.get('name')}")
    
    # Count items
    total_items = db.menu_items.count_documents({})
    proper_burgers = db.menu_items.count_documents({
        "price_medium": {"$exists": True},
        "has_sizes": True
    })
    
    print(f"\n✅ Gesamt Menü-Items: {total_items}")
    print(f"✅ Burger mit Größen: {proper_burgers}")
    
    print("\n" + "=" * 60)
    print("🎉 WIEDERHERSTELLUNG ERFOLGREICH ABGESCHLOSSEN!")
    print("=" * 60)
    print("\n📋 Nächste Schritte:")
    print("1. Starten Sie Ihren Backend-Service neu")
    print("2. Löschen Sie den Browser-Cache auf allen Geräten")
    print("3. Testen Sie die Website: zozo-burger.de")
    print("4. Verifizieren Sie, dass Burger die richtigen Größen/Preise haben")
    print(f"\n💾 Emergency-Backup gespeichert in: {emergency_filename}")
    print("   (Falls Sie zurück zur vorherigen Version müssen)")
    
except Exception as e:
    print(f"\n❌ FEHLER während der Wiederherstellung:")
    print(f"   {str(e)}")
    print("\n   Die Datenbank könnte in einem inkonsistenten Zustand sein!")
    if 'emergency_filename' in locals():
        print(f"   Verwenden Sie das Emergency-Backup zum Wiederherstellen: {emergency_filename}")
    exit(1)

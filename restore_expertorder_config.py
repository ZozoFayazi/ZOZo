#!/usr/bin/env python3
"""
ZOZO Burger - ExpertOrder Konfiguration Wiederherstellen

Falls die ExpertOrder-Konfiguration jemals verloren geht,
führen Sie dieses Script aus, um sie wiederherzustellen.

Verwendung:
    python3 /app/restore_expertorder_config.py
"""

from pymongo import MongoClient
import os
from datetime import datetime

def restore_expertorder_config():
    """Stellt die ExpertOrder-Konfiguration wieder her"""
    
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_url)
    db = client['test_database']
    
    print("\n" + "="*70)
    print("   ZOZO BURGER - EXPERTORDER KONFIGURATION WIEDERHERSTELLEN")
    print("="*70 + "\n")
    
    # RELLINGEN Konfiguration
    rellingen_config = {
        "location_id": "49aff347-a6c3-407c-ad4a-59d5d0852314",
        "expertorder_api_key": "4bbc443c82674f93e910399ca7931b37b45e55ba",
        "expertorder_enabled": True,
        "expertorder_test_mode": False,
        "expertorder_base_url": "https://zozo.eocloud.de",
        "expertorder_broker_name": "zozo-burger.de",
        "updated_at": datetime.utcnow()
    }
    
    # HENSTEDT-ULZBURG Konfiguration
    henstedt_config = {
        "location_id": "422cac42-cfdf-4869-b2cb-0b09aa24d02c",
        "expertorder_api_key": "90dd43e5c58b7c2a8ddd1eb4916ae8196d8e1073",
        "expertorder_enabled": True,
        "expertorder_test_mode": False,
        "expertorder_base_url": "https://zozo.eocloud.de",
        "expertorder_broker_name": "zozo-burger.de",
        "updated_at": datetime.utcnow()
    }
    
    # Rellingen wiederherstellen
    db.location_settings.update_one(
        {"location_id": rellingen_config["location_id"]},
        {"$set": rellingen_config},
        upsert=True
    )
    print("✅ RELLINGEN konfiguriert")
    print(f"   Base URL: {rellingen_config['expertorder_base_url']}")
    print(f"   API Key: ***{rellingen_config['expertorder_api_key'][-8:]}")
    print(f"   Status: {'TEST' if rellingen_config['expertorder_test_mode'] else 'LIVE'}")
    print()
    
    # Henstedt-Ulzburg wiederherstellen
    db.location_settings.update_one(
        {"location_id": henstedt_config["location_id"]},
        {"$set": henstedt_config},
        upsert=True
    )
    print("✅ HENSTEDT-ULZBURG konfiguriert")
    print(f"   Base URL: {henstedt_config['expertorder_base_url']}")
    print(f"   API Key: ***{henstedt_config['expertorder_api_key'][-8:]}")
    print(f"   Status: {'TEST' if henstedt_config['expertorder_test_mode'] else 'LIVE'}")
    print()
    
    print("="*70)
    print("✅ EXPERTORDER KONFIGURATION ERFOLGREICH WIEDERHERGESTELLT!")
    print("="*70)
    print("\n🎉 Beide Standorte sind wieder mit ExpertOrder verbunden!\n")

if __name__ == "__main__":
    restore_expertorder_config()

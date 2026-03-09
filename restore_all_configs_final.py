#!/usr/bin/env python3
"""
🔒 FINAL CONFIG RESTORATION SCRIPT
Stellt ALLE Configs dauerhaft wieder her:
- PayPal LIVE für beide Standorte
- ExpertOrder POS für beide Standorte
"""
import os
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

print("="*80)
print("🔒 FINAL CONFIG RESTORATION")
print("="*80)
print(f"Timestamp: {datetime.now().isoformat()}\n")

# ============================================================================
# 1. PAYPAL LIVE CREDENTIALS (von PAYPAL_LIVE_FINAL_BACKUP.json)
# ============================================================================
print("\n💳 1️⃣ PayPal LIVE Credentials wiederherstellen...")

paypal_configs = {
    "rellingen": {
        "location_id": "49aff347-a6c3-407c-ad4a-59d5d0852314",
        "current_location_id": "87de5af8-e424-4fd0-9094-b77b0bf2be77",  # Aktuell
        "paypal_client_id": "Ac94dFnQk1qbwEndBfUOAODPMQBhskka3iMusznawOaezGYjzSUpKoyPk5EBgLzKNAgwKEK_UHcUdRB7",
        "paypal_secret_key": "EKX-jMnXB6jQkIl5tw1XakUfHIguAKeQimrMfyD9P9bBN_tnCxcRsAyJ88j2F-nSnVCyMDHzc669exAB",
        "paypal_sandbox_mode": False
    },
    "henstedt": {
        "location_id": "422cac42-cfdf-4869-b2cb-0b09aa24d02c",
        "current_location_id": "e5d3dda4-fd50-4388-b08a-9ddfc4098b6f",  # Aktuell
        "paypal_client_id": "AR7Brjjwwg432MxkzLiRMMeZdtynccfZyUZtpFCTllt2NfKNlIa3ftX6jLH_iDssVdrDMRB8YUmcY9kz",
        "paypal_secret_key": "EHTM6aK5qDXaWn_dXWhEPa32PVJjcByO4xoHLb1r3K-v2TMv0MVQ-KmwwTf5KvMCyja7gSi2a7n8wv8J",
        "paypal_sandbox_mode": False
    }
}

for loc_name, config in paypal_configs.items():
    # Update location document directly
    result = db.locations.update_one(
        {"id": config["current_location_id"]},
        {
            "$set": {
                "paypal_client_id": config["paypal_client_id"],
                "paypal_secret_key": config["paypal_secret_key"],
                "paypal_sandbox_mode": config["paypal_sandbox_mode"],
                "paypal_enabled": True,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count > 0:
        print(f"   ✅ {loc_name.upper()}: PayPal LIVE credentials restored")
    else:
        print(f"   ❌ {loc_name.upper()}: Location not found!")

# ============================================================================
# 2. EXPERTORDER POS CONFIGURATION
# ============================================================================
print("\n🔧 2️⃣ ExpertOrder POS Configuration wiederherstellen...")

expertorder_configs = {
    "rellingen": {
        "current_location_id": "87de5af8-e424-4fd0-9094-b77b0bf2be77",
        "api_key": "4bbc443c82674f93e910399ca7931b37b45e55ba",
        "slug": "rellingen"
    },
    "henstedt": {
        "current_location_id": "e5d3dda4-fd50-4388-b08a-9ddfc4098b6f",
        "api_key": "6d9ff6096cf79ec2ee24db36f87b6f7396a017ebb15d",
        "slug": "henstedt-ulzburg"
    }
}

for loc_name, config in expertorder_configs.items():
    pos_config = {
        "provider": "expertorder",
        "enabled": True,
        "api_key": config["api_key"],
        "base_url": "https://zozo.eocloud.de",
        "broker_name": "zozo-burger.de",
        "test_mode": False
    }
    
    result = db.locations.update_one(
        {"id": config["current_location_id"]},
        {
            "$set": {
                "pos_config": pos_config,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count > 0:
        print(f"   ✅ {loc_name.upper()}: ExpertOrder POS configuration restored")
    else:
        print(f"   ❌ {loc_name.upper()}: Location not found!")

# ============================================================================
# 3. VERIFICATION
# ============================================================================
print("\n\n✅ 3️⃣ Verifikation...")
print("="*80)

locations = list(db.locations.find({}))
for loc in locations:
    print(f"\n📍 {loc['name']} (ID: {loc['id']})")
    
    # PayPal
    if loc.get('paypal_client_id'):
        print(f"   💳 PayPal: ENABLED (LIVE Mode: {not loc.get('paypal_sandbox_mode', True)})")
        print(f"      Client ID: ***{loc['paypal_client_id'][-12:]}")
    else:
        print(f"   💳 PayPal: NOT CONFIGURED")
    
    # POS
    pos = loc.get('pos_config', {})
    if pos and pos.get('enabled'):
        print(f"   🔧 POS: ENABLED ({pos.get('provider', 'unknown').upper()})")
        print(f"      API Key: ***{pos.get('api_key', '')[-12:]}")
        print(f"      Test Mode: {pos.get('test_mode', True)}")
    else:
        print(f"   🔧 POS: NOT CONFIGURED")

print("\n" + "="*80)
print("✅ RESTORATION COMPLETE!")
print("="*80)

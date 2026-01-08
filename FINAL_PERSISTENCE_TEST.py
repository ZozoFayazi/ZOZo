#!/usr/bin/env python3
"""
🔒 FINAL PERSISTENCE & CONNECTION TEST
Testet alle Verbindungen und erstellt Nachweis
"""
import os
import sys
import asyncio
from datetime import datetime
from pymongo import MongoClient

sys.path.insert(0, '/app/backend')

print("="*80)
print("🔒 FINAL PERSISTENCE TEST")
print("="*80)
print(f"Timestamp: {datetime.now().isoformat()}\n")

# MongoDB
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

# Test Results
results = {
    "test_timestamp": datetime.now().isoformat(),
    "tests": []
}

# ============================================================================
# TEST 1: ExpertOrder POS Connection (beide Standorte)
# ============================================================================
print("\n🔧 TEST 1: ExpertOrder POS Verbindungen")
print("-"*80)

from pos_connectors.expertorder import ExpertOrderConnector

for slug in ["rellingen", "henstedt-ulzburg"]:
    location = db.locations.find_one({"slug": slug})
    if not location or not location.get('pos_config', {}).get('enabled'):
        print(f"❌ {slug}: POS nicht konfiguriert")
        results["tests"].append({
            "name": f"ExpertOrder {slug}",
            "status": "FAILED",
            "error": "Not configured"
        })
        continue
    
    connector = ExpertOrderConnector(location['pos_config'])
    
    test_order = {
        "order_id": f"PERSIST-TEST-{slug.upper()}-{datetime.now().strftime('%H%M%S')}",
        "order_number": f"PT-{slug[:3].upper()}-{datetime.now().strftime('%H%M%S')}",
        "customer_name": "Persistence Test",
        "customer_email": "persistence@test.de",
        "customer_phone": "+491700000099",
        "items": [{"product_id": "1", "name": f"Test {slug}", "quantity": 1, "price": 1.00, "size": "normal"}],
        "total": 1.00,
        "delivery_type": "pickup",
        "delivery_address": "Test",
        "payment_method": "cash",
        "notes": "Final Persistence Test",
        "scheduled_time": None
    }
    
    async def test_pos():
        return await connector.push_order(test_order)
    
    result = asyncio.run(test_pos())
    
    if result.get('success'):
        print(f"✅ {slug}: ExpertOrder WORKING")
        print(f"   Order: {test_order['order_number']}")
        results["tests"].append({
            "name": f"ExpertOrder {slug}",
            "status": "SUCCESS",
            "order_number": test_order['order_number']
        })
    else:
        print(f"❌ {slug}: ExpertOrder FAILED")
        print(f"   Error: {result.get('message')}")
        results["tests"].append({
            "name": f"ExpertOrder {slug}",
            "status": "FAILED",
            "error": result.get('message')
        })

# ============================================================================
# TEST 2: PayPal Config Verification
# ============================================================================
print("\n\n💳 TEST 2: PayPal Konfiguration")
print("-"*80)

for location in db.locations.find({}):
    name = location['name']
    pp_cid = location.get('paypal_client_id', '')
    pp_secret = location.get('paypal_secret_key', '')
    pp_sandbox = location.get('paypal_sandbox_mode', True)
    
    if pp_cid and pp_secret:
        mode = "LIVE" if not pp_sandbox else "SANDBOX"
        print(f"✅ {name}: PayPal {mode} configured")
        print(f"   Client ID: ***{pp_cid[-12:]}")
        results["tests"].append({
            "name": f"PayPal {name}",
            "status": "CONFIGURED",
            "mode": mode
        })
    else:
        print(f"❌ {name}: PayPal NOT configured")
        results["tests"].append({
            "name": f"PayPal {name}",
            "status": "FAILED",
            "error": "Missing credentials"
        })

# ============================================================================
# TEST 3: Database Persistence Check
# ============================================================================
print("\n\n💾 TEST 3: Database Persistence")
print("-"*80)

collections_check = {
    "locations": db.locations.count_documents({}),
    "categories": db.categories.count_documents({}),
    "daily_deals": db.daily_deals.count_documents({}),
}

for coll, count in collections_check.items():
    print(f"   {coll}: {count} documents")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n\n📊 FINAL TEST SUMMARY")
print("="*80)

success_count = sum(1 for t in results["tests"] if t["status"] in ["SUCCESS", "CONFIGURED"])
total_count = len(results["tests"])

print(f"\n✅ Passed: {success_count}/{total_count} tests")

if success_count == total_count:
    print("\n🟢 ALL SYSTEMS OPERATIONAL & PERSISTENT!")
    print("   Alle Configs sind gespeichert und funktionieren.")
else:
    print(f"\n🟡 {total_count - success_count} tests failed - Check details above")

# Save test results
with open('/app/FINAL_PERSISTENCE_TEST_RESULTS.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n📄 Test report saved: /app/FINAL_PERSISTENCE_TEST_RESULTS.json")
print("="*80)
FINAL_LOCK

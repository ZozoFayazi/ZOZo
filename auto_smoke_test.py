#!/usr/bin/env python3
"""
Automated Pre/Post Deployment Smoke Test
Runs automatically before and after deployments
"""
import os
import sys
import json
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

def serialize(o):
    if isinstance(o, ObjectId): return str(o)
    if isinstance(o, datetime): return o.isoformat()
    if isinstance(o, dict): return {k: serialize(v) for k, v in o.items()}
    if isinstance(o, list): return [serialize(i) for i in o]
    return o

def run_smoke_test():
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "all_passed": True
    }
    
    # Test 1: Tenants
    tenants = list(db.tenants.find({}))
    if tenants:
        results["tests"].append({"name": "Tenants", "status": "PASS", "count": len(tenants)})
    else:
        results["tests"].append({"name": "Tenants", "status": "FAIL", "error": "No tenants"})
        results["all_passed"] = False
    
    for tenant in tenants:
        tenant_id = tenant["tenant_id"]
        
        # Test 2: Locations
        locs = list(db.locations.find({"tenant_id": tenant_id}))
        if locs:
            results["tests"].append({"name": f"Locations ({tenant_id})", "status": "PASS", "count": len(locs)})
            
            for loc in locs:
                # PayPal
                if loc.get('paypal_client_id'):
                    results["tests"].append({"name": f"PayPal {loc['name']}", "status": "PASS"})
                
                # POS
                if loc.get('pos_config', {}).get('enabled'):
                    results["tests"].append({"name": f"POS {loc['name']}", "status": "PASS"})
        
        # Test 3: Menu
        menu_count = db.menu_items.count_documents({"tenant_id": tenant_id})
        if menu_count > 0:
            results["tests"].append({"name": f"Menu ({tenant_id})", "status": "PASS", "count": menu_count})
    
    return results

def create_backup():
    """Create automatic backup"""
    os.makedirs('/app/backups/auto', exist_ok=True)
    
    backup = {"timestamp": datetime.now().isoformat(), "collections": {}}
    for c in ["tenants", "locations", "menu_items", "categories", "modifier_groups"]:
        backup["collections"][c] = serialize(list(db[c].find({})))
    
    backup_file = f"/app/backups/auto/pre_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w') as f:
        json.dump(backup, f, indent=2)
    
    return backup_file

if __name__ == "__main__":
    print("🧪 Running automated smoke test...")
    
    # Create backup first
    backup_file = create_backup()
    print(f"✅ Backup created: {backup_file}")
    
    # Run smoke test
    results = run_smoke_test()
    
    # Print results
    print(f"\nTest Results ({results['timestamp']}):")
    for test in results["tests"]:
        status_icon = "✅" if test["status"] == "PASS" else "❌"
        print(f"  {status_icon} {test['name']}")
    
    if results["all_passed"]:
        print("\n✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)

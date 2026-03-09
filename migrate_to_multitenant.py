#!/usr/bin/env python3
"""
Migrate existing ZOZO Burger data to multi-tenant architecture
Creates default tenant and adds tenant_id to all existing data
"""
import os
import sys
from pymongo import MongoClient
from datetime import datetime

sys.path.insert(0, '/app/backend')

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

print("="*80)
print("🔄 MULTI-TENANT MIGRATION")
print("="*80)
print(f"Timestamp: {datetime.now().isoformat()}\n")

# 1. Create default tenant (ZOZO Burger)
print("1️⃣ Creating default tenant: ZOZO Burger...")

default_tenant = {
    "tenant_id": "zozo-burger-default",
    "name": "ZOZO Burger",
    "slug": "zozo-burger",
    "status": "active",
    "language": "de",
    "timezone": "Europe/Berlin",
    "branding": {
        "logo_url": None,
        "primary_color": "#DC2626",
        "accent_color": "#F59E0B",
        "font_family": "Inter"
    },
    "template_id": "modern",
    "domain": "zozo-burger.de",
    "urls": {
        "shop": "/",
        "admin": "/admin"
    },
    "subscription": {
        "plan": "enterprise",
        "status": "active",
        "started_at": datetime.utcnow()
    },
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

existing_tenant = db.tenants.find_one({"tenant_id": "zozo-burger-default"})
if not existing_tenant:
    db.tenants.insert_one(default_tenant)
    print("   ✅ Tenant created")
else:
    print("   ℹ️ Tenant already exists")

# 2. Add tenant_id to all collections
print("\n2️⃣ Adding tenant_id to existing data...")

collections_to_migrate = [
    "locations",
    "menu_items",
    "categories",
    "orders",
    "discount_codes",
    "modifier_groups",
    "deals",
    "daily_deals",
    "admin_users"
]

for collection_name in collections_to_migrate:
    try:
        collection = db[collection_name]
        
        # Count documents without tenant_id
        count_without = collection.count_documents({"tenant_id": {"$exists": False}})
        
        if count_without > 0:
            # Add tenant_id
            result = collection.update_many(
                {"tenant_id": {"$exists": False}},
                {"$set": {"tenant_id": "zozo-burger-default"}}
            )
            print(f"   ✅ {collection_name}: {result.modified_count} documents updated")
        else:
            print(f"   ℹ️ {collection_name}: already migrated")
    
    except Exception as e:
        print(f"   ❌ {collection_name}: Error - {str(e)}")

# 3. Create indexes for tenant_id
print("\n3️⃣ Creating tenant_id indexes...")

for collection_name in collections_to_migrate:
    try:
        collection = db[collection_name]
        collection.create_index("tenant_id")
        print(f"   ✅ {collection_name}: Index created")
    except Exception as e:
        print(f"   ⚠️ {collection_name}: {str(e)}")

print("\n" + "="*80)
print("✅ MIGRATION COMPLETE!")
print("="*80)
print(f"\nDefault Tenant ID: zozo-burger-default")
print(f"All existing data now scoped to this tenant.")
print("\nNext: Create new tenants via Super Admin Wizard")
print("="*80)

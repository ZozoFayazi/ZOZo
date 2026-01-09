#!/usr/bin/env python3
"""
Setup complete Salad test case with modifier groups
"""
import os
import sys
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

sys.path.insert(0, '/app/backend')

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

print("🥗 Setting up Salad test products...")
print("="*60)

# 1. Get or create Salat category
salat_category = db.categories.find_one({"slug": "salate"})
if not salat_category:
    salat_category = {
        "id": "salate",
        "name": "Salate",
        "slug": "salate",
        "active": True,
        "order": 10,
        "created_at": datetime.utcnow()
    }
    result = db.categories.insert_one(salat_category)
    salat_category['_id'] = result.inserted_id
    print("✅ Created category: Salate")
else:
    print("✅ Category exists: Salate")

category_id = str(salat_category['_id'])

# 2. Create test salad products
salad_products = [
    {
        "name": "Caesar Salad",
        "description": "Römersalat, Hähnchen, Parmesan, Caesar Dressing",
        "category_id": category_id,
        "price_normal": 8.90,
        "active": True,
        "in_stock": True,
        "location_id": None,
        "modifier_group_ids": ["salad-dressing", "salad-pizzabroetchen"],
        "image_url": "/uploads/products/salad-caesar.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "Greek Salad",
        "description": "Tomaten, Gurken, Oliven, Feta, Zwiebeln",
        "category_id": category_id,
        "price_normal": 7.90,
        "active": True,
        "in_stock": True,
        "location_id": None,
        "modifier_group_ids": ["salad-dressing", "salad-pizzabroetchen"],
        "image_url": "/uploads/products/salad-greek.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "name": "Tuna Salad",
        "description": "Thunfisch, Eisbergsalat, Tomaten, Mais, Zwiebeln",
        "category_id": category_id,
        "price_normal": 9.50,
        "active": True,
        "in_stock": True,
        "location_id": None,
        "modifier_group_ids": ["salad-dressing", "salad-pizzabroetchen"],
        "image_url": "/uploads/products/salad-tuna.jpg",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

for product in salad_products:
    existing = db.menu_items.find_one({"name": product["name"]})
    if existing:
        db.menu_items.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "modifier_group_ids": product["modifier_group_ids"],
                "updated_at": datetime.utcnow()
            }}
        )
        print(f"✅ Updated: {product['name']} (added modifier groups)")
    else:
        db.menu_items.insert_one(product)
        print(f"✅ Created: {product['name']}")

# 3. Verify
print("\n📊 Verification:")
salad_count = db.menu_items.count_documents({"category_id": category_id})
print(f"   Total salads: {salad_count}")

modifier_count = db.modifier_groups.count_documents({})
print(f"   Modifier groups: {modifier_count}")

# Show salads with modifiers
print("\n📝 Salads with modifier groups:")
for salad in db.menu_items.find({"category_id": category_id}):
    modifiers = salad.get('modifier_group_ids', [])
    print(f"   {salad['name']}: {len(modifiers)} modifier groups")
    for mod_id in modifiers:
        mod_group = db.modifier_groups.find_one({"id": mod_id})
        if mod_group:
            print(f"      - {mod_group['name']} ({'Required' if mod_group.get('required') else 'Optional'})")

print("\n✅ Salad setup complete!")
print("="*60)

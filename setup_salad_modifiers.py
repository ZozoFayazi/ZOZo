#!/usr/bin/env python3
"""
Setup Salad Modifier Groups with Dressing (required) + Pizzabrötchen Upsell
"""
import os
import sys
from pymongo import MongoClient
from datetime import datetime

sys.path.insert(0, '/app/backend')

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

print("🥗 Setting up Salad Modifier Groups...")
print("="*60)

# 1. Dressing Selection (REQUIRED)
dressing_group = {
    "id": "salad-dressing",
    "name": "Dressing-Auswahl",
    "type": "radio",
    "required": True,
    "applies_to_categories": ["salate", "salat", "salads"],
    "applies_to_products": [],
    "display_order": 1,
    "options": [
        {
            "id": "american-dressing",
            "name": "American Dressing",
            "price": 0.00,
            "is_default": True
        },
        {
            "id": "joghurt-dressing",
            "name": "Joghurt Dressing",
            "price": 0.00,
            "is_default": False
        },
        {
            "id": "french-dressing",
            "name": "French Dressing",
            "price": 0.00,
            "is_default": False
        }
    ],
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

# 2. Pizzabrötchen Upsell (OPTIONAL)
pizzabroetchen_group = {
    "id": "salad-pizzabroetchen",
    "name": "Mit 3 Pizzabrötchen?",
    "type": "radio",
    "required": True,  # Must answer, but "Nein" is an option
    "applies_to_categories": ["salate", "salat", "salads"],
    "applies_to_products": [],
    "display_order": 2,
    "options": [
        {
            "id": "no-pizzabroetchen",
            "name": "Ohne Pizzabrötchen",
            "price": 0.00,
            "is_default": True
        },
        {
            "id": "with-pizzabroetchen",
            "name": "Mit 3 Pizzabrötchen",
            "price": 2.50,
            "is_default": False,
            "description": "Frisch gebacken, mit Knoblauchbutter"
        }
    ],
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

# Insert or update
for group in [dressing_group, pizzabroetchen_group]:
    existing = db.modifier_groups.find_one({"id": group["id"]})
    if existing:
        db.modifier_groups.replace_one({"id": group["id"]}, group)
        print(f"✅ Updated: {group['name']}")
    else:
        db.modifier_groups.insert_one(group)
        print(f"✅ Created: {group['name']}")

# Verify
print("\n📊 Final verification:")
total = db.modifier_groups.count_documents({})
print(f"   Total modifier groups: {total}")

for group in db.modifier_groups.find({}):
    print(f"\n   {group['name']}:")
    print(f"     Type: {group['type']}")
    print(f"     Required: {group['required']}")
    print(f"     Options: {len(group['options'])}")

print("\n✅ Salad modifier groups setup complete!")
print("="*60)

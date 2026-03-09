"""
Setup Modifier Groups for ZOZO Burger

Modifier Groups:
1. Pizzabrötchen Addon (Salate, Pasta, Tomatensuppe)
2. Dressing Selection (Salate - Required)
3. Pasta Type Selection (Pasta - Required)
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def setup_modifier_groups():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    
    print("🔧 Creating Modifier Groups...\n")
    
    # 1. Pizzabrötchen Addon (für Salate, Pasta, Tomatensuppe)
    pizzabroetchen_group = {
        "id": "pizzabroetchen_addon",
        "title": "Mit 3 Pizzabrötchen?",
        "type": "single_choice",
        "required": True,
        "min": 1,
        "max": 1,
        "options": [
            {"name": "Ohne Pizzabrötchen", "price": 0, "default": True},
            {"name": "Mit 3 Pizzabrötchen", "price": 1.50}
        ]
    }
    
    # 2. Dressing Selection (für Salate)
    dressing_group = {
        "id": "salad_dressing",
        "title": "Dressing wählen",
        "type": "single_choice",
        "required": True,
        "min": 1,
        "max": 1,
        "options": [
            {"name": "American Dressing", "price": 0, "default": True},
            {"name": "Joghurt-Dressing", "price": 0},
            {"name": "French-Dressing", "price": 0}
        ]
    }
    
    # 3. Pasta Type Selection
    pasta_type_group = {
        "id": "pasta_type",
        "title": "Pasta-Typ wählen",
        "type": "single_choice",
        "required": True,
        "min": 1,
        "max": 1,
        "options": [
            {"name": "Penne", "price": 0, "default": True},
            {"name": "Spaghetti", "price": 0},
            {"name": "Tagliatelle", "price": 0}
        ]
    }
    
    # Insert or update modifier groups
    for group in [pizzabroetchen_group, dressing_group, pasta_type_group]:
        await db.modifier_groups.update_one(
            {"id": group["id"]},
            {"$set": group},
            upsert=True
        )
        print(f"✅ Created: {group['title']}")
    
    print("\n📦 Assigning Modifier Groups to Products...\n")
    
    # Assign to Salate
    salate_cat = await db.categories.find_one({"slug": "salate"})
    if salate_cat:
        result = await db.menu_items.update_many(
            {"category_id": salate_cat['_id']},
            {"$set": {"modifier_group_ids": ["pizzabroetchen_addon", "salad_dressing"]}}
        )
        print(f"✅ Salate: {result.modified_count} products → Pizzabrötchen + Dressing")
    
    # Assign to Pasta
    pasta_cat = await db.categories.find_one({"slug": "pasta"})
    if pasta_cat:
        result = await db.menu_items.update_many(
            {"category_id": pasta_cat['_id']},
            {"$set": {"modifier_group_ids": ["pizzabroetchen_addon", "pasta_type"]}}
        )
        print(f"✅ Pasta: {result.modified_count} products → Pizzabrötchen + Pasta-Typ")
    
    # Assign to Tomatensuppe (find by name)
    result = await db.menu_items.update_many(
        {"name": {"$regex": "Tomatensuppe", "$options": "i"}},
        {"$set": {"modifier_group_ids": ["pizzabroetchen_addon"]}}
    )
    print(f"✅ Tomatensuppe: {result.modified_count} products → Pizzabrötchen")
    
    print("\n✅ Modifier Groups Setup Complete!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_modifier_groups())

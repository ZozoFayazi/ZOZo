"""
Seed database with ZOZO Burger menu data
"""
import os
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
client = MongoClient(MONGO_URL)
db = client.get_database()

def clear_database():
    """Clear all collections"""
    db.locations.delete_many({})
    db.categories.delete_many({})
    db.menu_items.delete_many({})
    db.orders.delete_many({})
    db.admin_users.delete_many({})
    print("✓ Database cleared")

def seed_locations():
    """Seed location data"""
    locations = [
        {
            "_id": ObjectId(),
            "name": "ZOZO Burger Rellingen",
            "slug": "rellingen",
            "address": "Möwenstraße 2",
            "city": "Rellingen",
            "postal_code": "25462",
            "lat": 53.6506,
            "lng": 9.8422,
            "phone": "+49 4101 123456",
            "email": "rellingen@zozoburger.de",
            "opening_hours": "11:00 - 22:45",
            "active": True
        },
        {
            "_id": ObjectId(),
            "name": "ZOZO Burger Henstedt-Ulzburg",
            "slug": "henstedt-ulzburg",
            "address": "Edisonstraße 11",
            "city": "Henstedt-Ulzburg",
            "postal_code": "24558",
            "lat": 53.7886,
            "lng": 9.9789,
            "phone": "+49 4193 123456",
            "email": "henstedt@zozoburger.de",
            "opening_hours": "11:00 - 22:45",
            "active": True
        }
    ]
    
    result = db.locations.insert_many(locations)
    print(f"✓ Inserted {len(result.inserted_ids)} locations")
    return locations

def seed_categories():
    """Seed categories (global for all locations)"""
    categories = [
        {"_id": ObjectId(), "name": "Burger", "slug": "burger", "order": 1, "active": True},
        {"_id": ObjectId(), "name": "Pizza", "slug": "pizza", "order": 2, "active": True},
        {"_id": ObjectId(), "name": "Smash Burger & Fisch", "slug": "smash-fisch", "order": 3, "active": True},
        {"_id": ObjectId(), "name": "Classics", "slug": "classics", "order": 4, "active": True},
        {"_id": ObjectId(), "name": "Wraps", "slug": "wraps", "order": 5, "active": True},
        {"_id": ObjectId(), "name": "Pasta", "slug": "pasta", "order": 6, "active": True},
        {"_id": ObjectId(), "name": "Salads", "slug": "salads", "order": 7, "active": True},
        {"_id": ObjectId(), "name": "Pizzabuns", "slug": "pizzabuns", "order": 8, "active": True},
        {"_id": ObjectId(), "name": "Fingerfood", "slug": "fingerfood", "order": 9, "active": True},
        {"_id": ObjectId(), "name": "Kids Menu", "slug": "kids", "order": 10, "active": True},
        {"_id": ObjectId(), "name": "Dips", "slug": "dips", "order": 11, "active": True},
        {"_id": ObjectId(), "name": "Drinks", "slug": "drinks", "order": 12, "active": True}
    ]
    
    result = db.categories.insert_many(categories)
    print(f"✓ Inserted {len(result.inserted_ids)} categories")
    return categories

def parse_price(price_str):
    """Parse price string to float"""
    if not price_str:
        return None
    return float(price_str.replace('€', '').replace(',', '.').strip())

def seed_menu_items(categories):
    """Seed menu items from PDF data"""
    category_map = {cat['slug']: str(cat['_id']) for cat in categories}
    
    menu_items = []
    
    # BURGER Category
    burgers = [
        {"name": "Hamburger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken", "p_m": 7.99, "p_l": 11.19, "img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800"},
        {"name": "Cheeseburger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken, Käse", "p_m": 9.19, "p_l": 12.29, "img": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=800"},
        {"name": "Chili-Cheeseburger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken, Käse, Jalapeños", "p_m": 9.49, "p_l": 11.89, "img": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=800"},
        {"name": "Bacon-Burger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Bacon, Gewürzgurken, BBQ Sauce, Röstzwiebeln", "p_m": 8.69, "p_l": 11.49, "img": "https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=800"},
        {"name": "Veggie Burger", "desc": "Veggie Patty, Tomaten, Salat, Zwiebeln, Gewürzgurken", "p_m": 7.69, "p_l": None, "img": "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=800"},
        {"name": "Crunchy Chicken Burger", "desc": "Crunchy Chicken, Tomaten, Salat, Zwiebeln, Gewürzgurke, Käse", "p_m": 9.49, "p_l": None, "img": "https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=800"},
        {"name": "Monster Bacon Burger", "desc": "Beef, Tomaten, Salat, Gewürzgurken, Zwiebeln, Ei, Champignons, Bacon, Käse", "p_m": 12.99, "p_l": 16.39, "img": "https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=800"},
        {"name": "Greek Burger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Oliven, Hirtenkäse, Gewürzgurken, Peperoni", "p_m": 9.49, "p_l": 11.89, "img": "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=800"},
    ]
    
    for item in burgers:
        menu_items.append({
            "_id": ObjectId(),
            "category_id": category_map['burger'],
            "name": item['name'],
            "description": item['desc'],
            "price_medium": item['p_m'],
            "price_large": item['p_l'],
            "image_url": item['img'],
            "tags": ["burger"],
            "active": True
        })
    
    # PIZZA Category
    pizzas = [
        {"name": "Margherita", "desc": "Tomatensauce, Gouda-Käse", "p_m": 7.49, "p_l": 9.79, "img": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800"},
        {"name": "Las Vegas", "desc": "Tomatensauce, Schinken, Gouda-Käse", "p_m": 8.59, "p_l": 11.89, "img": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800"},
        {"name": "São Paulo", "desc": "Tomatensauce, Schinken, Salami, Champignons, Gouda-Käse", "p_m": 12.39, "p_l": 15.79, "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"},
        {"name": "Hawaii", "desc": "Tomatensauce, Schinken, Ananas, Gouda-Käse", "p_m": 9.69, "p_l": 13.19, "img": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800"},
        {"name": "ZOZO Special", "desc": "Tomatensauce, Hackfleisch, Bacon, Jalapenos, Mais, BBQ-Sauce, Gouda-Käse", "p_m": 13.69, "p_l": 16.99, "img": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=800"},
        {"name": "Little Italy", "desc": "Tomatensauce, rote Zwiebeln, Gouda-Käse, Rucola, Grana Padano, Serrano-Schinken", "p_m": 12.59, "p_l": 15.89, "img": "https://images.unsplash.com/photo-1595708812500-7f82e1a89b92?w=800"},
    ]
    
    for item in pizzas:
        menu_items.append({
            "_id": ObjectId(),
            "category_id": category_map['pizza'],
            "name": item['name'],
            "description": item['desc'],
            "price_medium": item['p_m'],
            "price_large": item['p_l'],
            "image_url": item['img'],
            "tags": ["pizza"],
            "active": True
        })
    
    # PASTA Category
    pastas = [
        {"name": "Pasta Tomato Sauce", "desc": "Pasta nach Wahl, Tomatensauce", "price": 9.99, "img": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800"},
        {"name": "Pasta Cream Chicken", "desc": "Pasta nach Wahl, Hähnchenbrust-Würfel, Sahne, Broccoli, Cherry Tomaten, Paprika", "price": 13.49, "img": "https://images.unsplash.com/photo-1612874742237-6526221588e3?w=800"},
        {"name": "Pasta Tomato Gambas", "desc": "Pasta nach Wahl, Garnelen, Knoblauch, Oliven, Tomatensauce", "price": 15.99, "img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800"},
    ]
    
    for item in pastas:
        menu_items.append({
            "_id": ObjectId(),
            "category_id": category_map['pasta'],
            "name": item['name'],
            "description": item['desc'],
            "price_normal": item['price'],
            "image_url": item['img'],
            "tags": ["pasta"],
            "active": True
        })
    
    # DRINKS Category
    drinks = [
        {"name": "Coca Cola", "price": 2.99, "img": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=800"},
        {"name": "Coca Cola Zero", "price": 2.99, "img": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=800"},
        {"name": "Fanta", "price": 2.99, "img": "https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?w=800"},
        {"name": "Sprite", "price": 2.99, "img": "https://images.unsplash.com/photo-1625772452859-1c03d5bf1137?w=800"},
        {"name": "Vio Still", "price": 2.49, "img": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=800"},
    ]
    
    for item in drinks:
        menu_items.append({
            "_id": ObjectId(),
            "category_id": category_map['drinks'],
            "name": item['name'],
            "description": "",
            "price_normal": item['price'],
            "image_url": item['img'],
            "tags": ["drink"],
            "active": True
        })
    
    # FINGERFOOD Category
    fingerfoods = [
        {"name": "French Fries", "desc": "Knusprige Pommes Frites", "price": 4.99, "img": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=800"},
        {"name": "Chicken Nuggets", "desc": "ca. 6 Stück + Dip nach Wahl", "price": 6.99, "img": "https://images.unsplash.com/photo-1562967914-608f82629710?w=800"},
        {"name": "Chicken Wings", "desc": "ca. 6 Stück + Dip nach Wahl", "price": 7.99, "img": "https://images.unsplash.com/photo-1608039755401-742074f0548d?w=800"},
        {"name": "Onion Rings", "desc": "ca. 8 Stück + Dip nach Wahl", "price": 5.99, "img": "https://images.unsplash.com/photo-1639024471283-03518883512d?w=800"},
    ]
    
    for item in fingerfoods:
        menu_items.append({
            "_id": ObjectId(),
            "category_id": category_map['fingerfood'],
            "name": item['name'],
            "description": item['desc'],
            "price_normal": item['price'],
            "image_url": item['img'],
            "tags": ["fingerfood"],
            "active": True
        })
    
    result = db.menu_items.insert_many(menu_items)
    print(f"✓ Inserted {len(result.inserted_ids)} menu items")
    return menu_items

def seed_all():
    """Run all seed functions"""
    print("\n🌱 Starting database seeding...")
    clear_database()
    locations = seed_locations()
    categories = seed_categories()
    menu_items = seed_menu_items(categories)
    print(f"\n✅ Database seeded successfully!")
    print(f"   - {len(locations)} locations")
    print(f"   - {len(categories)} categories")
    print(f"   - {len(menu_items)} menu items\n")
    
    return {
        'locations': locations,
        'categories': categories,
        'menu_items': menu_items
    }

if __name__ == "__main__":
    seed_all()

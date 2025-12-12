"""
Seed database with ZOZO Burger menu data
"""
import os
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

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
            "delivery_zone": {
                "postal_codes": ["25462", "25421", "25451", "25469", "25479", "25485", "25488"],
                "min_order_value": 10.0,
                "delivery_fee": 2.50,
                "free_delivery_threshold": 15.0
            },
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
            "delivery_zone": {
                "postal_codes": ["24558", "24568", "24576", "24601", "24594", "24623"],
                "min_order_value": 10.0,
                "delivery_fee": 2.50,
                "free_delivery_threshold": 15.0
            },
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
    """Seed menu items from PDF data - COMPLETE MENU"""
    category_map = {cat['slug']: str(cat['_id']) for cat in categories}
    
    menu_items = []
    
    # BURGER Category - COMPLETE (17 items)
    burgers = [
        {"name": "Hamburger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken", "p_m": 7.99, "p_l": 11.19, "img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800"},
        {"name": "Cheeseburger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken, Käse", "p_m": 9.19, "p_l": 12.29, "img": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=800"},
        {"name": "Chili-Cheeseburger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken, Käse, Jalapeños", "p_m": 9.49, "p_l": 11.89, "img": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=800"},
        {"name": "Bacon-Burger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Bacon, Gewürzgurken, BBQ Sauce, Röstzwiebeln", "p_m": 11.49, "p_l": 14.29, "img": "https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=800"},
        {"name": "Veggie Burger", "desc": "Veggie Patty, Tomaten, Salat, Zwiebeln, Gewürzgurken", "p_m": 7.69, "p_l": None, "img": "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=800"},
        {"name": "Crunchy Chicken Burger", "desc": "Crunchy Chicken, Tomaten, Salat, Zwiebeln, Gewürzgurke, Käse", "p_m": 8.09, "p_l": None, "img": "https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=800"},
        {"name": "Monster Bacon Burger", "desc": "Beef, Tomaten, Salat, Gewürzgurken, Zwiebeln, Ei, Champignons, Bacon, Käse", "p_m": 9.49, "p_l": 12.59, "img": "https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=800"},
        {"name": "Chili Bacon Burger", "desc": "Beef, Bacon, Jalapeños, BBQ Sauce, Tomaten, Salat, Gewürzgurken, Röstzwiebeln", "p_m": 9.99, "p_l": 13.99, "img": "https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=800"},
        {"name": "Champion-Burger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken, Champignons", "p_m": 8.69, "p_l": 11.49, "img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800"},
        {"name": "Green Burger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Oliven, Hirtenkäse, Gewürzgurken, Peperoni", "p_m": 9.49, "p_l": 11.89, "img": "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=800"},
        {"name": "Italy Burger", "desc": "Beef, Tomaten, Rucola, Gewürzgurken, Zwiebeln, Grana Padano, Serrano Schinken", "p_m": 9.99, "p_l": 12.59, "img": "https://images.unsplash.com/photo-1585238341710-75a96881e2b7?w=800"},
        {"name": "Farmers Burger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken, Spiegelei", "p_m": 8.79, "p_l": 11.29, "img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800"},
        {"name": "Chicken Nugget Burger", "desc": "Chicken Nuggets, Salat, Tomaten, Gewürzgurken, Zwiebeln", "p_m": 8.09, "p_l": None, "img": "https://images.unsplash.com/photo-1562967914-608f82629710?w=800"},
        {"name": "Crunchy Chicken Bacon Burger", "desc": "Crunchy Chicken, Tomaten, Salat, BBQ Sauce, Gewürzgurken, Röstzwiebeln, Jalapeños, Bacon", "p_m": 10.39, "p_l": 13.99, "img": "https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=800"},
        {"name": "Two Hundred Fifty Burger", "desc": "2x 125g Beef, Salat, Tomaten, Gewürzgurken, Zwiebeln, Käse", "p_m": 9.59, "p_l": 12.69, "img": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=800"},
        {"name": "Three Hundred Sixty Burger", "desc": "2x 180g Beef, Salat, Tomaten, Gewürzgurken, Zwiebeln, Käse", "p_m": 10.39, "p_l": 17.49, "img": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=800"},
        {"name": "Avocado Dream Burger", "desc": "Beef, Rucola Salat, Avocado Slices, Guacamole, Spiegelei", "p_m": 9.49, "p_l": 11.89, "img": "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=800"},
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
    
    # PIZZA Category - COMPLETE (16 items)
    pizzas = [
        {"name": "Margherita", "desc": "Tomatensauce, Gouda-Käse", "p_m": 7.49, "p_l": 9.79, "img": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800"},
        {"name": "L.A", "desc": "Tomatensauce, Salami, Gouda-Käse", "p_m": 8.59, "p_l": 11.89, "img": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=800"},
        {"name": "Las Vegas", "desc": "Tomatensauce, Schinken, Gouda-Käse", "p_m": 8.59, "p_l": 11.89, "img": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800"},
        {"name": "São Paulo", "desc": "Tomatensauce, Schinken, Salami, Champignons, Gouda-Käse", "p_m": 12.39, "p_l": 15.79, "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"},
        {"name": "Hawaii", "desc": "Tomatensauce, Schinken, Ananas, Gouda-Käse", "p_m": 9.69, "p_l": 13.19, "img": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800"},
        {"name": "Greenwood (Veggie)", "desc": "Tomatensauce, Champignons, Broccoli, Mais, Cocktail-Tomaten, Gouda-Käse", "p_m": 11.89, "p_l": 15.19, "img": "https://images.unsplash.com/photo-1511689660979-10d2b1aada49?w=800"},
        {"name": "Little Italy", "desc": "Tomatensauce, rote Zwiebeln, Gouda-Käse, Grana Padano, Serrano-Schinken", "p_m": 12.59, "p_l": 15.89, "img": "https://images.unsplash.com/photo-1595708812500-7f82e1a89b92?w=800"},
        {"name": "Chicago", "desc": "Tomatensauce, Cocktail Tomaten, Mozzarella, Gouda-Käse", "p_m": 11.29, "p_l": 14.19, "img": "https://images.unsplash.com/photo-1571066811602-716837d681de?w=800"},
        {"name": "ZOZO Special", "desc": "Tomatensauce, Hackfleisch, Bacon, Jalapeños, Broccoli, Mais, Gouda-Käse", "p_m": 13.69, "p_l": 16.99, "img": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=800"},
        {"name": "Toronto", "desc": "Tomatensauce, Thunfisch, rote Zwiebeln, Gouda-Käse", "p_m": 10.39, "p_l": 13.69, "img": "https://images.unsplash.com/photo-1571997478779-2adcbbe9ab2f?w=800"},
        {"name": "New York", "desc": "Tomatensauce, Schinken, Broccoli, Gouda-Käse", "p_m": 10.39, "p_l": 13.69, "img": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800"},
        {"name": "Boston", "desc": "Tomatensauce, Baconstreifen, Zwiebeln, Paprika, Gouda-Käse", "p_m": 11.45, "p_l": 14.75, "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"},
        {"name": "Alanya", "desc": "Tomatensauce, Knoblauchwurst, Zwiebeln, Paprika, Hirtenkäse, Gouda-Käse", "p_m": 11.89, "p_l": 15.19, "img": "https://images.unsplash.com/photo-1595854341625-f33ee10dbf94?w=800"},
        {"name": "Detroit", "desc": "Tomatensauce, Salami, Zwiebeln, Champignons, Gouda-Käse", "p_m": 12.99, "p_l": 14.19, "img": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=800"},
        {"name": "Bronx", "desc": "Tomatensauce, Hähnchenbruststreifen, Zwiebeln, Jalapeños, BBQ-Sauce, Gouda-Käse", "p_m": 10.99, "p_l": 14.49, "img": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800"},
        {"name": "Dallas", "desc": "Tomatensauce, Hackfleisch, Bacon, Jalapeños, Mais, BBQ-Sauce, Gouda-Käse", "p_m": 13.49, "p_l": 16.69, "img": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=800"},
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
    
    # SMASH BURGER & FISCH Category - COMPLETE (8 items)
    smash_items = [
        {"name": "Smash Klassik", "desc": "Potato Bun, Ketchup, 2x Beef Patty, Gewürzgurken, rote Zwiebeln, Salat und Tomaten", "price": 10.90, "img": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=800"},
        {"name": "Smash Cheese", "desc": "Potato Bun, Ketchup, 2x Beef Patty, 2x Käse, Gewürzgurken, rote Zwiebeln, Salat und Tomaten", "price": 12.99, "img": "https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=800"},
        {"name": "Smash Bacon", "desc": "Potato Bun, BBQ-Sauce, 2x Beef Patty, Cheddar Käse, Bacon, Gewürzgurken, Röstzwiebeln, Salat und Tomaten", "price": 13.90, "img": "https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=800"},
        {"name": "Smash Chili Cheese", "desc": "Potato Bun, Ketchup, 2x Beef Patty, 2x Käse, Jalapeños, Käse Sauce, Gewürzgurken, rote Zwiebeln, Salat und Tomaten", "price": 13.90, "img": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=800"},
        {"name": "Fischburger", "desc": "Remoulade, Zwiebeln, Gewürzgurken, Käse, Salat und Tomaten", "price": 9.99, "img": "https://images.unsplash.com/photo-1625869016774-3faea40f6c5f?w=800"},
        {"name": "Fisch und Chips", "desc": "Pommes mit 6 Fischnuggets", "price": 9.99, "img": "https://images.unsplash.com/photo-1625869016774-3faea40f6c5f?w=800"},
        {"name": "Fisch Wrap", "desc": "Tortilla Wrap mit Remoulade, Salat, Zwiebeln und Fischburgerpatty", "price": 10.99, "img": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=800"},
        {"name": "Fischsalat", "desc": "Mix-Salat mit Zwiebeln und 6 Fischnuggets", "price": 10.99, "img": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800"},
    ]
    
    for item in smash_items:
        menu_items.append({
            "_id": ObjectId(),
            "category_id": category_map['smash-fisch'],
            "name": item['name'],
            "description": item['desc'],
            "price_normal": item['price'],
            "image_url": item['img'],
            "tags": ["smash", "burger"],
            "active": True
        })
    
    # CLASSICS Category (2 items)
    classics = [
        {"name": "Rinder-Currywurst mit Pommes", "desc": "Currywurst vom Rind serviert mit Pommes", "price": 8.99, "img": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=800"},
        {"name": "Hähnchen-Schnitzel mit Pommes", "desc": "Knuspriges Hähnchen-Schnitzel mit Pommes", "price": 8.99, "img": "https://images.unsplash.com/photo-1600891964092-4316c288032e?w=800"},
    ]
    
    for item in classics:
        menu_items.append({
            "_id": ObjectId(),
            "category_id": category_map['classics'],
            "name": item['name'],
            "description": item['desc'],
            "price_normal": item['price'],
            "image_url": item['img'],
            "tags": ["classic"],
            "active": True
        })
    
    # WRAPS Category - COMPLETE (4 items)
    wraps = [
        {"name": "Spicy Chicken Wrap", "desc": "Weizentortilla, Salat, Spicy Chicken, Mais und Tomate", "price": 8.19, "img": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=800"},
        {"name": "Crunchy Chicken Wrap", "desc": "Weizentortilla, Salat, Crunchy Chicken, Zwiebeln und Tomate", "price": 8.19, "img": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=800"},
        {"name": "Veggie Wrap", "desc": "Weizentortilla, Salat, Veggie Patty, Tomate", "price": 7.69, "img": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=800"},
        {"name": "BBQ-Beef Wrap", "desc": "Weizentortilla, Burger Patty, Bacon, Salat, Röstzwiebeln und BBQ-Sauce", "price": 9.29, "img": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=800"},
    ]
    
    for item in wraps:
        menu_items.append({
            "_id": ObjectId(),
            "category_id": category_map['wraps'],
            "name": item['name'],
            "description": item['desc'],
            "price_normal": item['price'],
            "image_url": item['img'],
            "tags": ["wrap"],
            "active": True
        })
    
    # PASTA Category - COMPLETE (5 items)
    pastas = [
        {"name": "Pasta Tomato Sauce", "desc": "Pasta nach Wahl (Spaghetti, Penne, Tagliatelle), Tomatensauce. Inklusive 3 Brötchen", "price": 9.99, "img": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800"},
        {"name": "Pasta Tomato Gambas", "desc": "Pasta nach Wahl, Garnelen, Knoblauch, Oliven, Tomatensauce. Inklusive 3 Brötchen", "price": 15.99, "img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800"},
        {"name": "Pasta Cream Gambas", "desc": "Pasta nach Wahl, Garnelen, Knoblauch, Sahnesauce. Inklusive 3 Brötchen", "price": 15.99, "img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800"},
        {"name": "Pasta Cream Chicken", "desc": "Pasta nach Wahl, Hähnchenbrust-Würfel, Sahne, Broccoli, Cherry Tomaten, Paprika. Inklusive 3 Brötchen", "price": 13.49, "img": "https://images.unsplash.com/photo-1612874742237-6526221588e3?w=800"},
        {"name": "Pasta Curry Cream Chicken", "desc": "Pasta nach Wahl, Hähnchenbrust-Würfel, Curry-Sahnesauce, Broccoli, Mais. Inklusive 3 Brötchen", "price": 13.49, "img": "https://images.unsplash.com/photo-1612874742237-6526221588e3?w=800"},
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
    
    # SALADS Category - COMPLETE (6 items)
    salads = [
        {"name": "Mix Salad", "desc": "Salat Mix, Cocktail-Tomaten, Karotten, Mais. Dressingsauswahl: Hausdressing, French oder Joghurt", "price": 7.99, "img": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800"},
        {"name": "Caesar Salad", "desc": "Salat Mix, Cocktail-Tomaten, Karotten, Mais, Grana Padano, Croutons", "price": 9.19, "img": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=800"},
        {"name": "Italy Salad", "desc": "Salat Mix, Cocktail-Tomaten, Karotten, Mais, Rucola, Grana Padano, Serrano Schinken", "price": 11.79, "img": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800"},
        {"name": "Greek Salad", "desc": "Salat Mix, Cocktail-Tomaten, Karotten, Mais, Oliven, Peperoni, Hirtenkäse", "price": 11.79, "img": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800"},
        {"name": "Chicken Salad", "desc": "Salat Mix, Cocktail-Tomaten, Karotten, Mais, Hähnchenstreifen", "price": 11.79, "img": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800"},
        {"name": "Pure Burger Salad", "desc": "Salat Mix, Cocktail-Tomaten, Karotten, Mais, Pure Beef Burger", "price": 11.79, "img": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800"},
    ]
    
    for item in salads:
        menu_items.append({
            "_id": ObjectId(),
            "category_id": category_map['salads'],
            "name": item['name'],
            "description": item['desc'],
            "price_normal": item['price'],
            "image_url": item['img'],
            "tags": ["salad"],
            "active": True
        })
    
    # PIZZABUNS Category - COMPLETE (8 items)
    pizzabuns = [
        {"name": "6 Pizzabrötchen", "desc": "6 Pizzabrötchen ohne Belag", "price": 5.95, "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"},
        {"name": "6 Pizzabrötchen mit Käse überbacken", "desc": "6 Pizzabrötchen mit Gouda-Käse überbacken", "price": 6.99, "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"},
        {"name": "8 Pizzabrötchen Ham", "desc": "mit Schinken, Gouda-Käse", "price": 6.99, "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"},
        {"name": "8 Pizzabrötchen Salami", "desc": "mit Salami, Gouda-Käse", "price": 6.99, "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"},
        {"name": "8 Pizzabrötchen Chicken", "desc": "mit Hähnchen, Gouda-Käse", "price": 7.49, "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"},
        {"name": "8 Pizzabrötchen Sucuk", "desc": "mit Knoblauchwurst, Gouda-Käse", "price": 7.49, "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"},
        {"name": "8 Pizzabrötchen Tom-Moz", "desc": "Tomaten, Mozzarella, Gouda-Käse", "price": 7.49, "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"},
        {"name": "8 Pizzabrötchen Johnny Ringo", "desc": "mit Hackfleisch und Jalapeños", "price": 7.79, "img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"},
    ]
    
    for item in pizzabuns:
        menu_items.append({
            "_id": ObjectId(),
            "category_id": category_map['pizzabuns'],
            "name": item['name'],
            "description": item['desc'],
            "price_normal": item['price'],
            "image_url": item['img'],
            "tags": ["pizzabun"],
            "active": True
        })
    
    # DRINKS Category - COMPLETE
    drinks = [
        {"name": "Coca Cola 0,33l", "price": 2.99, "img": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=800"},
        {"name": "Coca Cola Zero 0,33l", "price": 2.99, "img": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=800"},
        {"name": "Fanta 0,33l", "price": 2.99, "img": "https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?w=800"},
        {"name": "Sprite 0,33l", "price": 2.99, "img": "https://images.unsplash.com/photo-1625772452859-1c03d5bf1137?w=800"},
        {"name": "Mezzo Mix 0,33l", "price": 2.99, "img": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=800"},
        {"name": "Vio Still 0,5l", "price": 2.49, "img": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=800"},
        {"name": "Vio Spritzig 0,5l", "price": 2.49, "img": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=800"},
        {"name": "Red Bull 0,25l", "price": 3.49, "img": "https://images.unsplash.com/photo-1591696205602-2f950c417cb9?w=800"},
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
    
    # FINGERFOOD Category - COMPLETE (16 items)
    fingerfoods = [
        {"name": "Mozzarella Sticks", "desc": "ca. 6 Stück + Dip nach Wahl", "price": 6.39, "img": "https://images.unsplash.com/photo-1531749668029-2db88e4276c7?w=800"},
        {"name": "Spicy Chicken Stripes", "desc": "ca. 8 Stück + Dip nach Wahl", "price": 7.29, "img": "https://images.unsplash.com/photo-1562967914-608f82629710?w=800"},
        {"name": "Chicken Nuggets 6 Stück", "desc": "ca. 6 Stück + Dip nach Wahl", "price": 6.99, "img": "https://images.unsplash.com/photo-1562967914-608f82629710?w=800"},
        {"name": "Chicken Wings 6 Stück", "desc": "ca. 6 Stück + Dip nach Wahl", "price": 7.99, "img": "https://images.unsplash.com/photo-1608039755401-742074f0548d?w=800"},
        {"name": "Crunchy Wings 6 Stück", "desc": "ca. 6 Stück + Dip nach Wahl", "price": 8.49, "img": "https://images.unsplash.com/photo-1608039755401-742074f0548d?w=800"},
        {"name": "Crunchy Wings 18 Stück", "desc": "ca. 18 Stück + 2 Dips nach Wahl", "price": 13.99, "img": "https://images.unsplash.com/photo-1608039755401-742074f0548d?w=800"},
        {"name": "Fire Wings 6 Stück (scharf)", "desc": "ca. 6 Stück + Dip nach Wahl", "price": 8.49, "img": "https://images.unsplash.com/photo-1608039755401-742074f0548d?w=800"},
        {"name": "Fire Wings 18 Stück (scharf)", "desc": "ca. 18 Stück + 2 Dips nach Wahl", "price": 13.99, "img": "https://images.unsplash.com/photo-1608039755401-742074f0548d?w=800"},
        {"name": "Chili Cheese Nuggets", "desc": "ca. 8 Stück + Dip nach Wahl", "price": 6.89, "img": "https://images.unsplash.com/photo-1562967914-608f82629710?w=800"},
        {"name": "Onion Rings", "desc": "ca. 8 Stück + Dip nach Wahl", "price": 5.99, "img": "https://images.unsplash.com/photo-1639024471283-03518883512d?w=800"},
        {"name": "French Fries", "desc": "Knusprige Pommes Frites", "price": 4.99, "img": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=800"},
        {"name": "Sweet Potato Fries", "desc": "Süßkartoffel Pommes", "price": 5.49, "img": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=800"},
        {"name": "Twister", "desc": "Twister Pommes", "price": 5.39, "img": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=800"},
        {"name": "Country Potatoes (Kartoffelecken)", "desc": "Kartoffelecken", "price": 5.49, "img": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=800"},
        {"name": "Fingerfood-Box", "desc": "15 Stück: 3 Fingerfood Artikel (je 5 Stück) nach Wahl + 2 Dips. Wählbar: Chili Cheese Nuggets, Mozzarella Sticks, Chicken Wings, Onion Rings, Chicken Nuggets, Spicy Chicken Stripes", "price": 12.39, "img": "https://images.unsplash.com/photo-1608039755401-742074f0548d?w=800"},
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
    
    # KIDS MENU Category - COMPLETE (1 item with 4 variants)
    kids = [
        {"name": "Kiddy Box (Hamburger)", "desc": "Kiddy Hamburger: Beef, Gewürzgurken, Ketchup, dazu Bambini Pommes. Inklusive Getränk und Spielzeug", "price": 9.49, "img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800"},
        {"name": "Kiddy Box (Cheeseburger)", "desc": "Kiddy Cheeseburger: Beef, Gewürzgurken, Käse, Ketchup, dazu Bambini Pommes. Inklusive Getränk und Spielzeug", "price": 9.49, "img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800"},
        {"name": "Kiddy Box (Nuggets Burger)", "desc": "Kiddy Nuggets Burger: Chicken Nuggets, Gewürzgurken, Ketchup, dazu Bambini Pommes. Inklusive Getränk und Spielzeug", "price": 9.49, "img": "https://images.unsplash.com/photo-1562967914-608f82629710?w=800"},
        {"name": "Kiddy Box (Chicken Nuggets)", "desc": "4 Chicken Nuggets, dazu Bambini Pommes. Inklusive Getränk und Spielzeug", "price": 9.49, "img": "https://images.unsplash.com/photo-1562967914-608f82629710?w=800"},
    ]
    
    for item in kids:
        menu_items.append({
            "_id": ObjectId(),
            "category_id": category_map['kids'],
            "name": item['name'],
            "description": item['desc'],
            "price_normal": item['price'],
            "image_url": item['img'],
            "tags": ["kids"],
            "active": True
        })
    
    # DIPS Category
    dips = [
        {"name": "Ketchup", "price": 0.50},
        {"name": "Mayo", "price": 0.50},
        {"name": "BBQ Sauce", "price": 0.80},
        {"name": "Curry Sauce", "price": 0.80},
        {"name": "Knoblauch Sauce", "price": 0.80},
        {"name": "Cocktail Sauce", "price": 0.80},
        {"name": "Sweet Chili", "price": 0.80},
    ]
    
    for item in dips:
        menu_items.append({
            "_id": ObjectId(),
            "category_id": category_map['dips'],
            "name": item['name'],
            "description": "",
            "price_normal": item['price'],
            "image_url": "",
            "tags": ["dip"],
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

"""
Seed ZOZO Burger Real Menu from Foodbooking
Complete menu with all categories, products, prices, and sizes
"""
import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# High-quality image URLs
IMG_BURGER = "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800"
IMG_CHEESEBURGER = "https://images.unsplash.com/photo-1550547660-d9450f859349?w=800"
IMG_BACON_BURGER = "https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=800"
IMG_CHICKEN_BURGER = "https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=800"
IMG_VEGGIE_BURGER = "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=800"
IMG_PIZZA = "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"
IMG_PASTA = "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800"
IMG_SALAD = "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800"
IMG_WRAP = "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=800"
IMG_FRIES = "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=800"
IMG_WINGS = "https://images.unsplash.com/photo-1608039755401-742074f0548d?w=800"
IMG_NUGGETS = "https://images.unsplash.com/photo-1562967914-608f82629710?w=800"
IMG_DRINK = "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=800"

def seed_real_menu():
    """Seed complete ZOZO Burger menu from Foodbooking"""
    
    print("🗑️  Clearing existing menu...")
    db.categories.delete_many({})
    db.menu_items.delete_many({})
    
    # Get locations
    locations = list(db.locations.find())
    if not locations:
        print("❌ No locations found! Run seed_data.py first.")
        return
    
    print(f"✓ Found {len(locations)} locations")
    
    for location in locations:
        location_id = str(location['_id'])
        location_name = location['name']
        print(f"\n📍 Seeding menu for: {location_name}")
        
        # Categories
        categories_data = [
            {"name": "Vorspeisen & Salate", "slug": "vorspeisen-salate", "order": 1},
            {"name": "Burger", "slug": "burger", "order": 2},
            {"name": "Burger Menüs", "slug": "burger-menus", "order": 3},
            {"name": "Smash Burger", "slug": "smash-burger", "order": 4},
            {"name": "Pizza", "slug": "pizza", "order": 5},
            {"name": "Pasta", "slug": "pasta", "order": 6},
            {"name": "Wraps", "slug": "wraps", "order": 7},
            {"name": "Pizzabrötchen", "slug": "pizzabroetchen", "order": 8},
            {"name": "Fingerfood", "slug": "fingerfood", "order": 9},
            {"name": "Imbiss", "slug": "imbiss", "order": 10},
            {"name": "Kiddy Zone", "slug": "kiddy-zone", "order": 11},
            {"name": "Getränke", "slug": "getraenke", "order": 12},
            {"name": "Dessert", "slug": "dessert", "order": 13},
            {"name": "Dips", "slug": "dips", "order": 14},
        ]
        
        categories = []
        for cat_data in categories_data:
            cat_doc = {
                "_id": ObjectId(),
                "name": cat_data["name"],
                "slug": cat_data["slug"],
                "location_id": location_id,
                "order": cat_data["order"],
                "active": True,
                "created_at": datetime.utcnow()
            }
            categories.append(cat_doc)
        
        db.categories.insert_many(categories)
        print(f"✓ Created {len(categories)} categories")
        
        # Create category map
        cat_map = {cat['slug']: str(cat['_id']) for cat in categories}
        
        # Menu Items
        menu_items = []
        
        # === VORSPEISEN & SALATE ===
        vorspeisen = [
            {"name": "Tomato Soup", "desc": "hausgemachte Tomatencremesuppe, inkl. 3 Pizzabrötchen", "price": 6.10, "img": IMG_SALAD},
            {"name": "Mix Salad", "desc": "Gemischter Salat mit Tomaten, Karotten und Mais", "price": 7.99, "img": IMG_SALAD},
            {"name": "Caesar Salad", "desc": "Salat Mix, Cocktail-Tomaten, Karotten, Mais, Grana Padano und Croutons", "price": 8.59, "img": IMG_SALAD},
            {"name": "Italy Salad", "desc": "Mix Salat, Rucola, Grana Padano, Serrano Schinken, Cocktail-Tomaten, Karotten und Mais", "price": 10.79, "img": IMG_SALAD},
            {"name": "Greek Salad", "desc": "Mix Salat, Hirtenkäse, Oliven, Peperoni, Mais, Cocktail-Tomaten und Karotten", "price": 10.79, "img": IMG_SALAD},
            {"name": "Pure Burger Salad", "desc": "Mix Salad, Pure Beef Burger, Cocktail-Tomaten, Karotten und Mais", "price": 10.79, "img": IMG_SALAD},
            {"name": "Chicken Salad", "desc": "Mix Salat, Hähnchenbrust-Streifen, Cocktail-Tomaten, Karotten und Mais", "price": 10.79, "img": IMG_SALAD},
        ]
        
        for item in vorspeisen:
            menu_items.append({
                "_id": ObjectId(),
                "name": item["name"],
                "description": item["desc"],
                "category_id": cat_map["vorspeisen-salate"],
                "location_id": location_id,
                "price_normal": item["price"],
                "image_url": item["img"],
                "available": True,
                "is_menu": False,
                "created_at": datetime.utcnow()
            })
        
        # === BURGER (mit Medium/Large Größen) ===
        burgers = [
            # Burger mit 2 Größen (Medium 125g / Large 180g)
            {"name": "Hamburger", "desc": "Beef Burger mit Tomaten, Salat, Zwiebeln und Gewürzgurken", "price_m": 7.99, "price_l": 11.19, "menu_m": 13.89, "menu_l": 17.09, "has_sizes": True, "img": IMG_BURGER},
            {"name": "Cheeseburger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken, Käse", "price_m": 9.19, "price_l": 12.29, "menu_m": 15.09, "menu_l": 18.19, "has_sizes": True, "img": IMG_CHEESEBURGER},
            {"name": "Bacon Burger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken, Bacon, BBQ-Sauce, Röstzwiebeln", "price_m": 11.49, "price_l": 14.29, "menu_m": 17.39, "menu_l": 20.19, "has_sizes": True, "img": IMG_BACON_BURGER},
            {"name": "Chili-Cheese Burger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken, Cheese-Sauce, Jalapeños", "price_m": 9.49, "price_l": 11.89, "menu_m": 15.39, "menu_l": 17.79, "has_sizes": True, "img": IMG_CHEESEBURGER},
            {"name": "Champion Burger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken, Champignons", "price_m": 8.69, "price_l": 11.49, "menu_m": 14.59, "menu_l": 17.39, "has_sizes": True, "img": IMG_BURGER},
            {"name": "Farmers", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken, Spiegelei", "price_m": 8.79, "price_l": 11.29, "menu_m": 14.69, "menu_l": 17.19, "has_sizes": True, "img": IMG_BURGER},
            {"name": "Greek Burger", "desc": "Beef, Tomaten, Salat, Zwiebeln, Gewürzgurken, Hirtenkäse, Peperoni, Oliven", "price_m": 9.49, "price_l": 11.89, "menu_m": 15.39, "menu_l": 17.79, "has_sizes": True, "img": IMG_BURGER},
            {"name": "Italy Burger", "desc": "Beef, Tomaten, Rucola, Zwiebeln, Gewürzgurken, Grana Padano, Serrano Schinken", "price_m": 9.99, "price_l": 12.59, "menu_m": 15.89, "menu_l": 18.49, "has_sizes": True, "img": IMG_BURGER},
            {"name": "Chili Bacon Burger", "desc": "Beef, Bacon, Jalapeños, BBQ Sauce, Tomaten, Salat, Gewürzgurken, Röstzwiebeln", "price_m": 9.99, "price_l": 13.99, "menu_m": 15.89, "menu_l": 19.89, "has_sizes": True, "img": IMG_BACON_BURGER},
            {"name": "Monster Bacon Burger", "desc": "Burger mit Beef, Ei, Champignons, Bacon, Salat, Tomaten, Zwiebeln, Gewürzgurken und Käse", "price_m": 9.49, "price_l": 12.59, "menu_m": 15.39, "menu_l": 18.49, "has_sizes": True, "img": IMG_BACON_BURGER},
            {"name": "Avocado Dream Burger", "desc": "mit Rucola Salat, Tomaten, Zwiebeln, Guacamole und Spiegelei", "price_m": 9.49, "price_l": 11.89, "menu_m": 15.39, "menu_l": 17.79, "has_sizes": True, "img": IMG_VEGGIE_BURGER},
            {"name": "Bacon Burger Deluxe", "desc": "2x 125g Beef, Bacon, Röstzwiebeln, Gewürzgurken, BBQ-Sauce und Käse", "price_m": 14.49, "price_l": 20.39, "menu_m": 20.39, "menu_l": 26.29, "has_sizes": True, "img": IMG_BACON_BURGER},
            
            # Burger mit nur EINER Größe
            {"name": "Chicken Nugget Burger", "desc": "Burger mit Chicken Nuggets, Salat, Tomaten, Gewürzgurken und Zwiebeln", "price": 8.09, "menu_price": 13.99, "has_sizes": False, "img": IMG_NUGGETS},
            {"name": "Crunchy Chickenburger", "desc": "Crunchy Chicken, Tomate, Salat, Zwiebeln, Gewürzgurke, Käse", "price": 8.09, "menu_price": 13.99, "has_sizes": False, "img": IMG_CHICKEN_BURGER},
            {"name": "Crunchy Chicken Bacon Burger", "desc": "Crunchy Chicken, Bacon, Jalapeños, Tomaten, Salat, BBQ-Sauce, Gewürzgurken, Röstzwiebeln", "price": 10.39, "menu_price": 16.29, "has_sizes": False, "img": IMG_CHICKEN_BURGER},
            {"name": "Veggie Burger", "desc": "Veggie Patty, Tomaten, Salat, Zwiebeln, Gewürzgurken", "price": 7.69, "menu_price": 13.59, "has_sizes": False, "img": IMG_VEGGIE_BURGER},
            {"name": "Two Hundred Fifty Burger", "desc": "2x 125 g Beef, Salat, Tomaten, Zwiebeln, Gurken und Käse", "price": 9.59, "menu_price": 15.49, "has_sizes": False, "img": IMG_CHEESEBURGER},
            {"name": "Three Hundred Sixty Burger", "desc": "2x 180 g Beef, Salat, Tomaten, Zwiebeln, Gurken und Käse", "price": 10.39, "menu_price": 16.29, "has_sizes": False, "img": IMG_CHEESEBURGER},
            {"name": "The Double Crunchy Burger", "desc": "2x Crunchy Chicken, Tomaten, Salat, Zwiebeln, Gewürzgurke, Käse", "price": 12.99, "menu_price": None, "has_sizes": False, "img": IMG_CHICKEN_BURGER},
        ]
        
        for item in burgers:
            doc = {
                "_id": ObjectId(),
                "name": item["name"],
                "description": item["desc"],
                "category_id": cat_map["burger"],
                "location_id": location_id,
                "price_normal": item["price"],
                "image_url": item["img"],
                "available": True,
                "is_menu": False,
                "menu_upgrade_price": item.get("menu_price"),
                "can_upgrade_to_menu": item.get("menu_price") is not None,
                "created_at": datetime.utcnow()
            }
            menu_items.append(doc)
        
        # === SMASH BURGER ===
        smash_burgers = [
            {"name": "Smash Klassik", "desc": "Potato Bun, Ketchup, 2x Beef Patty, Gewürzgurken, Rote Zwiebeln, Salat, Tomaten", "price": 10.90, "img": IMG_BURGER},
            {"name": "Smash Cheese", "desc": "Potato Bun, Ketchup, 2x Beef Patty, 2x Käse, Gewürzgurken, Rote Zwiebeln, Salat, Tomaten", "price": 12.99, "img": IMG_CHEESEBURGER},
            {"name": "Smash Bacon", "desc": "Potato Bun, BBQ-Sauce 2x Beef Patty, 2x Käse, Bacon, Gewürzgurken, Röstzwiebeln, Salat, Tomaten", "price": 13.90, "img": IMG_BACON_BURGER},
            {"name": "Smash Chili Cheese", "desc": "Potato Bun, Ketchup, 2 x Beef Patty, 2x Käse, Jalapeños, Käse Sauce, Gewürzgurken, Rote Zwiebeln, Salat, Tomaten", "price": 13.90, "img": IMG_CHEESEBURGER},
        ]
        
        for item in smash_burgers:
            menu_items.append({
                "_id": ObjectId(),
                "name": item["name"],
                "description": item["desc"],
                "category_id": cat_map["smash-burger"],
                "location_id": location_id,
                "price_normal": item["price"],
                "image_url": item["img"],
                "available": True,
                "is_menu": False,
                "created_at": datetime.utcnow()
            })
        
        # === PIZZA (mit Größen) ===
        pizzas = [
            {"name": "Margherita", "desc": "Grundpizza mit Tomatensoße und Gouda-Käse", "price_m": 7.49, "price_l": 9.79},
            {"name": "L.A.", "desc": "Pizza mit Tomatensoße, Salami und Gouda-Käse", "price_m": 8.99, "price_l": 11.89},
            {"name": "Las Vegas", "desc": "Pizza mit Tomatensoße, Schinken und Gouda-Käse", "price_m": 8.59, "price_l": 11.89},
            {"name": "Dallas", "desc": "Pizza mit Tomatensauce, Hackfleisch (Rind), Bacon, Jalapeños, Mais, BBQ-Sauce, Gouda-Käse", "price_m": 13.49, "price_l": 16.69},
            {"name": "Greenwood (Vegetarisch)", "desc": "Pizza mit Tomatensoße, Champignons, Brokkoli, Cocktail-Tomaten, Mais und Käse", "price_m": 11.89, "price_l": 15.19},
            {"name": "Hawaii", "desc": "Pizza mit Tomatensoße, Schinken, Ananas und Gouda-Käse", "price_m": 9.69, "price_l": 13.19},
            {"name": "São Paulo", "desc": "Pizza mit Tomatensoße, Schinken, Salami, Champignons und Gouda-Käse", "price_m": 12.39, "price_l": 15.79},
            {"name": "Little Italy", "desc": "Pizza mit Tomatensoße, roten Zwiebeln, Grana Padano, Gouda-Käse Rucola und Serrano-Schinken", "price_m": 12.59, "price_l": 15.89},
            {"name": "Chicago", "desc": "Pizza mit Tomatensoße, Tomaten, Mozzarella und Gouda-Käse", "price_m": 11.29, "price_l": 14.19},
            {"name": "Toronto", "desc": "Pizza mit Tomatensoße, Thunfisch, roten Zwiebeln und Gouda-Käse", "price_m": 10.39, "price_l": 13.69},
            {"name": "ZOZO Special", "desc": "Pizza mit Sauce Hollandaise, Hähnchenbrust-Streifen, Jalapeños, Broccoli, Mais, Gouda-Käse", "price_m": 13.69, "price_l": 16.99},
            {"name": "Boston", "desc": "Pizza mit Tomatensauce, Baconstreifen, Zwiebeln, Paprika, Goudakäse", "price_m": 11.45, "price_l": 14.75},
            {"name": "Alanya", "desc": "Pizza mit Tomatensoße, Sucuk, rote Zwiebeln, Paprika und Gouda-Käse", "price_m": 11.89, "price_l": 15.19},
            {"name": "Detroit", "desc": "Pizza mit Tomatensauce, Salami, Zwiebeln, Champignons, Gouda-Käse", "price_m": 12.99, "price_l": 14.19},
            {"name": "Bronx", "desc": "Pizza mit Tomatensauce, Hähnchenbruststreifen, Zwiebeln, Jalapeños, BBQ-Sauce, Gouda-Käse", "price_m": 10.99, "price_l": 14.49},
            {"name": "New York", "desc": "Pizza mit Sauce Hollandaise, Brokkoli, Schinken und Gouda-Käse", "price_m": 10.39, "price_l": 13.69},
            {"name": "Kentucky", "desc": "Pizza mit Tomatensoße, Hähnchenbrust-Würfel, Ananas, Gouda-Käse", "price_m": 10.39, "price_l": 13.69},
            {"name": "Houston", "desc": "Pizza mit Tomatensauce, Hackfleisch, Blattspinat, Hirtenkäse, Knoblauchsauce, Gouda-Käse", "price_m": 12.99, "price_l": 15.89},
            {"name": "San Francisco", "desc": "Pizza mit Tomatensauce, Hähnchenbruststreifen, Blattspinat, Cocktail-Tomaten, Knoblauchsauce, Gouda-Käse", "price_m": 11.99, "price_l": 14.89},
        ]
        
        for item in pizzas:
            menu_items.append({
                "_id": ObjectId(),
                "name": item["name"],
                "description": item["desc"],
                "category_id": cat_map["pizza"],
                "location_id": location_id,
                "price_medium": item["price_m"],
                "price_large": item["price_l"],
                "has_sizes": True,
                "image_url": IMG_PIZZA,
                "available": True,
                "is_menu": False,
                "created_at": datetime.utcnow()
            })
        
        # === PASTA (mit Pasta-Auswahl) ===
        pastas = [
            {"name": "Pasta Tomato Sauce", "desc": "Pasta nach Wahl mit Tomatensoße", "price": 9.99},
            {"name": "Pasta Curry Cream Chicken", "desc": "Pasta nach Wahl mit Hähnchenbrust-Würfel, Curry-Sahnesauce, Broccoli, Mais", "price": 13.49},
            {"name": "Pasta Cream Ham", "desc": "Pasta nach Wahl mit Schinken und Sahne", "price": 13.49},
            {"name": "Pasta Tomato Gambas", "desc": "Pasta nach Wahl mit Garnelen, Knoblauch und Oliven in Tomatensoße", "price": 15.99},
            {"name": "Pasta Cream Chicken", "desc": "Pasta nach Wahl mit Hähnchenbrust-Würfeln, Sahne und Brokkoli, Cherry Tomaten, Lauchzwiebeln und Paprika", "price": 13.49},
            {"name": "Pasta Cream Gambas", "desc": "Pasta nach Wahl mit Garnelen, Sahnesauce und Knoblauch", "price": 15.99},
        ]
        
        for item in pastas:
            menu_items.append({
                "_id": ObjectId(),
                "name": item["name"],
                "description": item["desc"],
                "category_id": cat_map["pasta"],
                "location_id": location_id,
                "price_normal": item["price"],
                "image_url": IMG_PASTA,
                "available": True,
                "is_menu": False,
                "has_pasta_choice": True,
                "created_at": datetime.utcnow()
            })
        
        # === WRAPS ===
        wraps = [
            {"name": "Spicy Chicken Wrap", "desc": "Weizentortilla, Salat, Spicy Chicken, Mais und Tomate", "price": 7.19},
            {"name": "Crunchy Chicken Wrap", "desc": "Weizentortilla, Salat, Crunchy Chicken, Zwiebeln und Tomate", "price": 7.19},
            {"name": "Veggie Wrap", "desc": "Weizentortilla, Salat, Veggie Patty, Tomate", "price": 6.69},
            {"name": "BBQ-Beef Wrap", "desc": "Wrap mit Weizentortilla, Burger Patty, Bacon, Salat, Röstzwiebeln und BBQ-Sauce", "price": 8.29},
        ]
        
        for item in wraps:
            menu_items.append({
                "_id": ObjectId(),
                "name": item["name"],
                "description": item["desc"],
                "category_id": cat_map["wraps"],
                "location_id": location_id,
                "price_normal": item["price"],
                "image_url": IMG_WRAP,
                "available": True,
                "is_menu": False,
                "created_at": datetime.utcnow()
            })
        
        # === PIZZABRÖTCHEN ===
        pizzabroetchen = [
            {"name": "6 Pizzabrötchen", "desc": "Pizzabrötchen ohne Belag", "price": 5.99},
            {"name": "6 Pizzabrötchen mit Käse", "desc": "Pizzabrötchen mit Käse überbacken", "price": 6.99},
            {"name": "PB Ham", "desc": "Pizzabrötchen gefüllt mit Schinken und Käse, 8 Stück", "price": 6.99},
            {"name": "PB Salami", "desc": "Pizzabrötchen gefüllt mit Salami und Käse, 8 Stück", "price": 6.99},
            {"name": "PB Chicken", "desc": "Pizzabrötchen gefüllt mit Hähnchen und Käse, 8 Stück", "price": 7.49},
            {"name": "PB Sucuk", "desc": "Pizzabrötchen gefüllt mit Knoblauchwurst und Käse, 8 Stück", "price": 7.49},
            {"name": "PB Tom-Moz", "desc": "Pizzabrötchen gefüllt mit Tomaten-Mozzarella, 8 Stück", "price": 7.49},
        ]
        
        for item in pizzabroetchen:
            menu_items.append({
                "_id": ObjectId(),
                "name": item["name"],
                "description": item["desc"],
                "category_id": cat_map["pizzabroetchen"],
                "location_id": location_id,
                "price_normal": item["price"],
                "image_url": IMG_PIZZA,
                "available": True,
                "is_menu": False,
                "created_at": datetime.utcnow()
            })
        
        # === FINGERFOOD ===
        fingerfood = [
            {"name": "Mozzarella Sticks", "desc": "Mozzarella Sticks, 6 Stück + Dip", "price": 5.69},
            {"name": "Spicy Chicken Stripes", "desc": "Spicy Chicken Stripes, 8 Stück + Dip", "price": 6.49},
            {"name": "Chicken Nuggets", "desc": "Chicken Nuggets, 6 Stück + Dip", "price": 6.49},
            {"name": "Chicken Wings", "desc": "Chicken Wings + Dip", "price": 7.49},
            {"name": "Crunchy Wings", "desc": "Chicken Wings mit Dip nach Wahl", "price": 8.49},
            {"name": "Fire Wings", "desc": "scharfe Chicken Wings mit Dip nach Wahl", "price": 8.49},
            {"name": "Chili-Cheese Nuggets", "desc": "Chili-Cheese Nuggets, ca. 8 Stück + 1 Dip gratis", "price": 6.29},
            {"name": "Onion Rings", "desc": "Onion Rings, 8 Stück + Dip", "price": 5.69},
            {"name": "French fries", "desc": "Pommes", "price": 4.99},
            {"name": "Sweet potato fries", "desc": "Süßkartoffel-Pommes", "price": 4.99},
            {"name": "Potato Dippers", "desc": "Kartoffelscheiben", "price": 4.99},
            {"name": "Country Potatoes", "desc": "Kartoffelecken", "price": 4.89},
            {"name": "Twister Fries", "desc": "Twister Pommes", "price": 5.39},
            {"name": "Fingerfood-Box", "desc": "3 Fingerfood Artikel (je 5 Stück) nach Wahl + 2 Dips nach Wahl", "price": 11.39},
        ]
        
        for item in fingerfood:
            img = IMG_FRIES if 'fries' in item['name'].lower() or 'Potato' in item['name'] or 'Twister' in item['name'] or 'Country' in item['name'] else (IMG_WINGS if 'Wings' in item['name'] else IMG_NUGGETS)
            menu_items.append({
                "_id": ObjectId(),
                "name": item["name"],
                "description": item["desc"],
                "category_id": cat_map["fingerfood"],
                "location_id": location_id,
                "price_normal": item["price"],
                "image_url": img,
                "available": True,
                "is_menu": False,
                "created_at": datetime.utcnow()
            })
        
        # === IMBISS ===
        imbiss = [
            {"name": "Rinder Currywurst", "desc": "Currywurst vom Rind mit Pommes", "price": 8.99},
            {"name": "Hähnchen-Schnitzel", "desc": "Hähnchen-Schnitzel mit Pommes", "price": 10.99},
        ]
        
        for item in imbiss:
            menu_items.append({
                "_id": ObjectId(),
                "name": item["name"],
                "description": item["desc"],
                "category_id": cat_map["imbiss"],
                "location_id": location_id,
                "price_normal": item["price"],
                "image_url": IMG_FRIES,
                "available": True,
                "is_menu": False,
                "created_at": datetime.utcnow()
            })
        
        # === KIDDY ZONE ===
        kiddy = [
            {"name": "Kiddy Hamburger", "desc": "Kiddy Hamburger mit einer Kiddy Pommes. Inkl. Getränk, Lolly, Luftballon und Spielzeug", "price": 9.49},
            {"name": "Kiddy Cheeseburger", "desc": "Kiddy Cheeseburger mit einer Kiddy Pommes. Inkl. Getränk, Lolly, Luftballon und Spielzeug", "price": 9.49},
            {"name": "Kiddy Nuggets Burger", "desc": "Kiddy Nuggets Burger mit einer Kiddy Pommes. Inkl. Getränk, Lolly, Luftballon und Spielzeug", "price": 9.49},
            {"name": "Kiddy Chicken Nuggets (4 Stück)", "desc": "4 Chicken Nuggets mit Kiddy Pommes. Inkl. Getränk, Lolly, Luftballon und Spielzeug", "price": 9.49},
        ]
        
        for item in kiddy:
            menu_items.append({
                "_id": ObjectId(),
                "name": item["name"],
                "description": item["desc"],
                "category_id": cat_map["kiddy-zone"],
                "location_id": location_id,
                "price_normal": item["price"],
                "image_url": IMG_BURGER,
                "available": True,
                "is_menu": True,
                "created_at": datetime.utcnow()
            })
        
        # === GETRÄNKE ===
        drinks = [
            {"name": "Coca Cola", "desc": "inkl. Pfand", "price": 3.24},
            {"name": "Coca Cola Zero", "desc": "inkl. Pfand", "price": 3.24},
            {"name": "Fanta", "desc": "inkl. Pfand", "price": 3.24},
            {"name": "Mezzo Mix", "desc": "inkl. Pfand", "price": 3.24},
            {"name": "Sprite", "desc": "inkl. Pfand", "price": 4.04},
            {"name": "ViO Still", "desc": "inkl. Pfand", "price": 2.74},
            {"name": "ViO Medium", "desc": "inkl. Pfand", "price": 2.74},
            {"name": "ViO Apfelschorle", "desc": "inkl. Pfand", "price": 3.04},
            {"name": "ViO Rhabarberschorle", "desc": "inkl. Pfand", "price": 3.04},
            {"name": "ViO Johannisbeerschorle", "desc": "inkl. Pfand", "price": 3.04},
            {"name": "Fuze Tea Pfirsich", "desc": "inkl. Pfand", "price": 3.14},
            {"name": "Fuze Tea Zitrone", "desc": "inkl. Pfand", "price": 3.14},
        ]
        
        for item in drinks:
            menu_items.append({
                "_id": ObjectId(),
                "name": item["name"],
                "description": item["desc"],
                "category_id": cat_map["getraenke"],
                "location_id": location_id,
                "price_normal": item["price"],
                "image_url": IMG_DRINK,
                "available": True,
                "is_menu": False,
                "created_at": datetime.utcnow()
            })
        
        # === DESSERT ===
        desserts = [
            {"name": "Tiramizozo", "desc": "mit Alkohol", "price": 3.49},
            {"name": "American ZOZO Brownie", "desc": "supersaftig und superschokoladig", "price": 3.49},
            {"name": "Miss Chocolic Muffin", "desc": "Nuss-Nougat Füllung", "price": 3.49},
        ]
        
        for item in desserts:
            menu_items.append({
                "_id": ObjectId(),
                "name": item["name"],
                "description": item["desc"],
                "category_id": cat_map["dessert"],
                "location_id": location_id,
                "price_normal": item["price"],
                "image_url": "https://images.unsplash.com/photo-1551024601-bec78aea704b?w=800",
                "available": True,
                "is_menu": False,
                "created_at": datetime.utcnow()
            })
        
        # === DIPS ===
        dips = [
            {"name": "Ketchup", "price": 0.99},
            {"name": "Mayonnaise", "price": 0.99},
            {"name": "Sweet Chili-Sauce", "price": 1.19},
            {"name": "BBQ-Sauce", "price": 1.99},
            {"name": "Sour Cream", "price": 1.99},
            {"name": "Remoulade", "price": 1.99},
            {"name": "Knobi-Dip", "price": 1.99},
            {"name": "Chilisauce", "price": 1.49},
            {"name": "Sweet&Sour-Sauce", "price": 0.99},
            {"name": "Curry Sauce", "price": 1.99},
            {"name": "Snack Dressing", "price": 1.99},
        ]
        
        for item in dips:
            menu_items.append({
                "_id": ObjectId(),
                "name": item["name"],
                "description": item.get("desc", ""),
                "category_id": cat_map["dips"],
                "location_id": location_id,
                "price_normal": item["price"],
                "image_url": "https://images.unsplash.com/photo-1472476443507-c7a5948772fc?w=800",
                "available": True,
                "is_menu": False,
                "created_at": datetime.utcnow()
            })
        
        # Insert all menu items
        if menu_items:
            db.menu_items.insert_many(menu_items)
            print(f"✓ Created {len(menu_items)} menu items")

if __name__ == "__main__":
    print("\n🍔 Starting ZOZO Burger Real Menu Seed...\n")
    seed_real_menu()
    print("\n✅ Real menu seeded successfully!\n")

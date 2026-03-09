"""Setup script to create initial locations (Rellingen & Henstedt-Ulzburg)"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

async def setup_locations():
    """Create initial location data"""
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    locations_collection = db.locations
    
    # Default opening hours (Monday-Sunday 11:00-22:45)
    default_hours = [
        {"day": "monday", "is_open": True, "open_time": "11:00", "close_time": "22:45"},
        {"day": "tuesday", "is_open": True, "open_time": "11:00", "close_time": "22:45"},
        {"day": "wednesday", "is_open": True, "open_time": "11:00", "close_time": "22:45"},
        {"day": "thursday", "is_open": True, "open_time": "11:00", "close_time": "22:45"},
        {"day": "friday", "is_open": True, "open_time": "11:00", "close_time": "22:45"},
        {"day": "saturday", "is_open": True, "open_time": "11:00", "close_time": "22:45"},
        {"day": "sunday", "is_open": True, "open_time": "11:00", "close_time": "22:45"}
    ]
    
    locations_to_create = [
        {
            "name": "ZOZO Burger Rellingen",
            "slug": "rellingen",
            "address": "Möwenstraße 2",
            "city": "Rellingen",
            "postal_code": "25462",
            "lat": 53.6479,
            "lng": 9.8344,
            "phone": "041937521001",
            "email": "info@zozo-burger.de",
            "google_review_url": "https://www.google.com/maps/place/ZOZO+Burger+Rellingen/@53.6479,9.8344,17z",
            "opening_hours": default_hours,
            "delivery_area": {
                "mode": "radius",
                "radius_km": 5.0,
                "postal_codes": [],
                "delivery_fee": 2.50,
                "min_order_value": 15.0,
                "estimated_delivery_time": "30-45 Min"
            },
            "seo": {
                "meta_title": "ZOZO Burger Rellingen - Premium Burger Lieferservice",
                "meta_description": "Bestellen Sie bei ZOZO Burger Rellingen - Frische Premium Burger, schnelle Lieferung. Möwenstraße 2, 25462 Rellingen.",
                "keywords": "burger rellingen, burger lieferservice rellingen, zozo burger, premium burger"
            },
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "ZOZO Burger Henstedt-Ulzburg",
            "slug": "henstedt-ulzburg",
            "address": "Edisonstraße 11",
            "city": "Henstedt-Ulzburg",
            "postal_code": "24558",
            "lat": 53.7636,
            "lng": 9.9816,
            "phone": "041937521002",
            "email": "henstedt@zozo-burger.de",
            "google_review_url": "https://www.google.com/maps/place/ZOZO+Burger+Henstedt+Ulzburg/@53.7635827,9.9790643,17z",
            "opening_hours": default_hours,
            "delivery_area": {
                "mode": "radius",
                "radius_km": 5.0,
                "postal_codes": [],
                "delivery_fee": 2.50,
                "min_order_value": 15.0,
                "estimated_delivery_time": "30-45 Min"
            },
            "seo": {
                "meta_title": "ZOZO Burger Henstedt-Ulzburg - Premium Burger Lieferservice",
                "meta_description": "Bestellen Sie bei ZOZO Burger Henstedt-Ulzburg - Frische Premium Burger, schnelle Lieferung. Edisonstraße 11, 24558 Henstedt-Ulzburg.",
                "keywords": "burger henstedt-ulzburg, burger lieferservice henstedt, zozo burger, premium burger"
            },
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    for location_data in locations_to_create:
        # Check if location already exists
        existing = await locations_collection.find_one({"slug": location_data["slug"]})
        
        if existing:
            print(f"✓ Location {location_data['name']} already exists")
            continue
        
        # Insert location
        result = await locations_collection.insert_one(location_data)
        print(f"✓ Created location: {location_data['name']} (ID: {result.inserted_id})")
    
    print("\n" + "="*60)
    print("LOCATION SETUP COMPLETE")
    print("="*60)
    print("\nLocations created:")
    for loc in locations_to_create:
        print(f"  - {loc['name']} ({loc['slug']})")
        print(f"    Address: {loc['address']}, {loc['postal_code']} {loc['city']}")
        print(f"    Phone: {loc['phone']}")
        print(f"    Delivery: {loc['delivery_area']['mode']} ({loc['delivery_area']['radius_km']}km)")
        print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_locations())

"""
Seed database with sample deals
"""
import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

def seed_deals():
    """Seed sample deals"""
    # Clear existing deals
    db.deals.delete_many({})
    
    deals = [
        {
            "_id": ObjectId(),
            "title": "Family Feast Deal",
            "description": "2x Large Pizza + 1x Fingerfood-Box + 2x 1L Getränk",
            "discount_type": "percentage",
            "discount_value": 15,
            "min_order_value": 30.0,
            "code": "FAMILY15",
            "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800",
            "active": True,
            "created_at": datetime.utcnow(),
            "valid_from": datetime.utcnow(),
            "valid_until": datetime.utcnow() + timedelta(days=30)
        },
        {
            "_id": ObjectId(),
            "title": "Burger Lover Special",
            "description": "Jeder XXL Burger mit 20% Rabatt",
            "discount_type": "percentage",
            "discount_value": 20,
            "min_order_value": 15.0,
            "code": "BURGER20",
            "image_url": "https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=800",
            "active": True,
            "created_at": datetime.utcnow(),
            "valid_from": datetime.utcnow(),
            "valid_until": datetime.utcnow() + timedelta(days=30)
        },
        {
            "_id": ObjectId(),
            "title": "Mittwochs-Rabatt",
            "description": "€5 Rabatt auf alle Bestellungen über €25",
            "discount_type": "fixed",
            "discount_value": 5,
            "min_order_value": 25.0,
            "code": "WEDNESDAY5",
            "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800",
            "active": True,
            "created_at": datetime.utcnow(),
            "valid_from": datetime.utcnow(),
            "valid_until": datetime.utcnow() + timedelta(days=30)
        }
    ]
    
    result = db.deals.insert_many(deals)
    print(f"✓ Inserted {len(result.inserted_ids)} deals")
    return deals

if __name__ == "__main__":
    print("\n🌱 Seeding deals...")
    seed_deals()
    print("\n✅ Deals seeded successfully!\n")

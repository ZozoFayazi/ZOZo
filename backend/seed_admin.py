"""
Seed admin users for testing
"""
import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from pathlib import Path

# Import auth utilities
from auth import get_password_hash

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

def seed_admin_users():
    """Seed admin users for both locations and one owner"""
    
    # Get locations
    locations = list(db.locations.find({}))
    if len(locations) < 2:
        print("❌ Error: Need at least 2 locations. Run seed_data.py first.")
        return
    
    rellingen = locations[0]
    henstedt = locations[1]
    
    # Clear existing admin users
    db.admin_users.delete_many({})
    
    admin_users = [
        {
            "_id": ObjectId(),
            "email": "owner@zozoburger.de",
            "password_hash": get_password_hash("owner123"),
            "location_id": None,  # Owner has access to all locations
            "role": "owner",
            "active": True
        },
        {
            "_id": ObjectId(),
            "email": "rellingen@zozoburger.de",
            "password_hash": get_password_hash("rellingen123"),
            "location_id": str(rellingen['_id']),
            "role": "manager",
            "active": True
        },
        {
            "_id": ObjectId(),
            "email": "henstedt@zozoburger.de",
            "password_hash": get_password_hash("henstedt123"),
            "location_id": str(henstedt['_id']),
            "role": "manager",
            "active": True
        }
    ]
    
    result = db.admin_users.insert_many(admin_users)
    
    print("\\n✅ Admin users seeded successfully!")
    print("\\n📧 Login credentials:")
    print("\\n1. Owner (all locations):")
    print("   Email: owner@zozoburger.de")
    print("   Password: owner123")
    print("\\n2. Rellingen Manager:")
    print("   Email: rellingen@zozoburger.de")
    print("   Password: rellingen123")
    print("\\n3. Henstedt-Ulzburg Manager:")
    print("   Email: henstedt@zozoburger.de")
    print("   Password: henstedt123")
    print()

if __name__ == "__main__":
    seed_admin_users()

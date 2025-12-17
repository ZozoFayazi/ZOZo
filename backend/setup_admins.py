"""Setup script to create initial admin accounts"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from admin_auth import AdminAuth, ROLES
import os
from dotenv import load_dotenv

load_dotenv()

async def setup_admins():
    """Create initial admin accounts in database"""
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    admins_collection = db.admins
    
    # Default password for all admins (CHANGE THIS IN PRODUCTION!)
    default_password = "ZozoAdmin2024!"
    
    admins_to_create = [
        {
            "email": "admin@zonik-solutions.de",
            "name": "Super Administrator",
            "role": "super_admin",
            "branch_ids": [],  # Access to all branches
            "password": default_password
        },
        {
            "email": "info@zozo-burger.de",
            "name": "Rellingen Manager",
            "role": "rellingen_admin",
            "branch_ids": ["rellingen"],
            "password": default_password
        },
        {
            "email": "henstedt@zozo-burger.de",
            "name": "Henstedt-Ulzburg Manager",
            "role": "henstedt_admin",
            "branch_ids": ["henstedt-ulzburg"],
            "password": default_password
        }
    ]
    
    for admin_data in admins_to_create:
        # Check if admin already exists
        existing = await admins_collection.find_one({"email": admin_data["email"]})
        
        if existing:
            print(f"✓ Admin {admin_data['email']} already exists")
            continue
        
        # Hash password
        hashed_password = AdminAuth.hash_password(admin_data["password"])
        
        # Create admin document
        admin_doc = {
            "email": admin_data["email"],
            "name": admin_data["name"],
            "password_hash": hashed_password,
            "role": admin_data["role"],
            "branch_ids": admin_data["branch_ids"],
            "is_active": True,
            "created_at": None,
            "last_login": None,
            "totp_enabled": False,
            "totp_secret": None,
            "backup_codes": []
        }
        
        # Insert into database
        result = await admins_collection.insert_one(admin_doc)
        print(f"✓ Created admin: {admin_data['email']} (ID: {result.inserted_id})")
    
    print("\n" + "="*60)
    print("ADMIN SETUP COMPLETE")
    print("="*60)
    print(f"\nDefault password for all admins: {default_password}")
    print("\n⚠️  IMPORTANT: Change these passwords immediately after first login!\n")
    print("Admins created:")
    for admin in admins_to_create:
        print(f"  - {admin['email']} ({admin['name']}) - Role: {admin['role']}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(setup_admins())

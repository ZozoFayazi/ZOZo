"""Create a test admin for automated testing"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from admin_auth import AdminAuth
import os
from dotenv import load_dotenv

load_dotenv()

async def create_test_admin():
    """Create test admin account"""
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    test_email = "test@zozo-testing.de"
    test_password = "TestAdmin123!"
    
    # Check if test admin exists
    existing = await db.admins.find_one({"email": test_email})
    
    if existing:
        # Update password
        hashed_password = AdminAuth.hash_password(test_password)
        await db.admins.update_one(
            {"email": test_email},
            {"$set": {
                "password_hash": hashed_password,
                "must_change_password": False,
                "is_active": True
            }}
        )
        print(f"✓ Updated test admin: {test_email}")
    else:
        # Create new test admin
        hashed_password = AdminAuth.hash_password(test_password)
        admin_doc = {
            "email": test_email,
            "name": "Test Administrator",
            "password_hash": hashed_password,
            "role": "super_admin",
            "branch_ids": [],
            "is_active": True,
            "must_change_password": False,
            "created_at": None,
            "last_login": None,
            "totp_enabled": False,
            "totp_secret": None,
            "backup_codes": []
        }
        await db.admins.insert_one(admin_doc)
        print(f"✓ Created test admin: {test_email}")
    
    print(f"\nTest Admin Credentials:")
    print(f"  Email: {test_email}")
    print(f"  Password: {test_password}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_admin())

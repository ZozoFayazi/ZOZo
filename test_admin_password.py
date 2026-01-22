import asyncio
import sys
sys.path.append('/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
from admin_auth import AdminAuth
import os

async def test_password():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    admin = await db.admins.find_one({'email': 'admin@zonik-solutions.de'})
    
    if admin:
        password_to_test = 'ZozoAdmin2024!'
        password_hash = admin.get('password_hash')
        
        print(f'Testing password: {password_to_test}')
        print(f'Hash from DB: {password_hash[:20]}...')
        
        is_valid = AdminAuth.verify_password(password_to_test, password_hash)
        
        if is_valid:
            print('✅ Password is CORRECT')
        else:
            print('❌ Password is INCORRECT')
            
            # Try to create a new hash and update
            print('\nCreating new password hash...')
            new_hash = AdminAuth.hash_password(password_to_test)
            print(f'New hash: {new_hash[:20]}...')
            
            # Update the admin
            await db.admins.update_one(
                {'email': 'admin@zonik-solutions.de'},
                {'$set': {'password_hash': new_hash}}
            )
            print('✅ Password hash updated in database')
    else:
        print('❌ Admin not found')
    
    client.close()

asyncio.run(test_password())

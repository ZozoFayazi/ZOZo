"""Check PayPal config for Henstedt"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

async def check():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ.get('DB_NAME', 'test_database')]
    
    henstedt = await db.locations.find_one({"name": {"$regex": "Henstedt", "$options": "i"}})
    location_id = henstedt.get('id')
    
    settings = await db.location_settings.find_one({'location_id': location_id})
    
    print('PayPal Config for Henstedt:')
    print(f'  Enabled: {settings.get("paypal_enabled")}')
    print(f'  Client ID: {settings.get("paypal_client_id", "NOT SET")}')
    print(f'  Secret (first 20): {settings.get("paypal_client_secret", "NOT SET")[:20]}...')
    print(f'  Sandbox Mode: {settings.get("paypal_sandbox_mode")}')
    
    client.close()

asyncio.run(check())

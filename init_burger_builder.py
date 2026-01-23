#!/usr/bin/env python3
"""
Initialize Burger Builder Ingredients in Database
Creates default ingredients with layer configuration
"""

import sys
sys.path.insert(0, '/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from burger_builder_service import BurgerBuilderService

async def init_ingredients():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    service = BurgerBuilderService(db)
    
    print("Initializing burger builder ingredients...")
    await service.initialize_default_ingredients()
    print("✅ Done!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(init_ingredients())

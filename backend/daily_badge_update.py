#!/usr/bin/env python3
"""
Daily Badge Update Script
Run this via cron to automatically update product badges based on sales data
"""
import os
import asyncio
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.insert(0, '/app/backend')

from product_analytics_service import ProductAnalyticsService


async def main():
    """
    Main function to update badges
    """
    print("="*80)
    print("🔄 Daily Product Badge Update")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    print("="*80)
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['zozo_burger']
    
    # Initialize service
    analytics_service = ProductAnalyticsService(db)
    
    # Update badges
    result = await analytics_service.update_product_badges()
    
    if result.get('success'):
        print("\n✅ Badge Update Successful!")
        print(f"   📊 Bestsellers: {result['bestsellers']}")
        print(f"   🔥 Trending: {result['trending']}")
        print(f"   🆕 New: {result['new']}")
        print(f"   🕐 Updated at: {result['updated_at']}")
    else:
        print(f"\n❌ Badge Update Failed!")
        print(f"   Error: {result.get('error')}")
    
    print("\n" + "="*80)
    
    # Close connection
    client.close()
    
    return 0 if result.get('success') else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

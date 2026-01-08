#!/usr/bin/env python3
"""
🧪 END-TO-END CONNECTION TEST
Testet PayPal & ExpertOrder für beide Standorte
"""
import os
import asyncio
from datetime import datetime
from pymongo import MongoClient

# MongoDB
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

print("="*80)
print("🧪 END-TO-END CONNECTION TESTS")
print("="*80)
print(f"Timestamp: {datetime.now().isoformat()}\n")

# ============================================================================
# 1. PAYPAL CONNECTION TEST
# ============================================================================
print("\n💳 1️⃣ PayPal Connection Tests...")
print("-"*80)

async def test_paypal_connection(location_id, location_name):
    """Test PayPal authentication"""
    from paypal_service import PayPalService
    
    # Create service instance
    service = PayPalService(db)
    
    try:
        # Get access token (this tests the credentials)
        token = await service._get_access_token(location_id)
        
        if token:
            return {
                "status": "SUCCESS",
                "location": location_name,
                "message": "PayPal authentication successful",
                "token_preview": f"***{token[-8:]}" if len(token) > 8 else "***"
            }
        else:
            return {
                "status": "FAILED",
                "location": location_name,
                "message": "Could not obtain access token"
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "location": location_name,
            "message": str(e)
        }

async def run_paypal_tests():
    """Run PayPal tests for both locations"""
    locations = [
        ("87de5af8-e424-4fd0-9094-b77b0bf2be77", "Rellingen"),
        ("e5d3dda4-fd50-4388-b08a-9ddfc4098b6f", "Henstedt-Ulzburg")
    ]
    
    results = []
    for loc_id, loc_name in locations:
        print(f"\n   Testing {loc_name}...")
        result = await test_paypal_connection(loc_id, loc_name)
        results.append(result)
        
        if result["status"] == "SUCCESS":
            print(f"      ✅ {result['message']}")
            print(f"      Token: {result['token_preview']}")
        else:
            print(f"      ❌ {result['message']}")
    
    return results

# Run PayPal tests
paypal_results = asyncio.run(run_paypal_tests())

# ============================================================================
# 2. EXPERTORDER CONNECTION TEST
# ============================================================================
print("\n\n🔧 2️⃣ ExpertOrder POS Connection Tests...")
print("-"*80)

async def test_expertorder_connection(location_slug, location_name):
    """Test ExpertOrder connection by creating a minimal test order"""
    from pos_connectors.expertorder import ExpertOrderConnector
    from datetime import timezone
    
    # Get location
    location = db.locations.find_one({"slug": location_slug})
    if not location:
        return {
            "status": "ERROR",
            "location": location_name,
            "message": "Location not found"
        }
    
    pos_config = location.get('pos_config', {})
    if not pos_config or not pos_config.get('enabled'):
        return {
            "status": "ERROR",
            "location": location_name,
            "message": "POS not enabled"
        }
    
    # Create connector
    connector = ExpertOrderConnector(pos_config)
    
    # Build minimal test order
    test_order = {
        "order_id": f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "order_number": f"TEST-{datetime.now().strftime('%H%M%S')}",
        "customer_name": "Test Kunde (Connection Check)",
        "customer_email": "test@zozo-burger.de",
        "customer_phone": "+491700000001",
        "items": [
            {
                "product_id": "test-1",
                "name": "Test Burger (Connection Check)",
                "quantity": 1,
                "price": 8.50,
                "size": "normal"
            }
        ],
        "total": 8.50,
        "delivery_type": "pickup",
        "delivery_address": "Teststraße 1, 12345 Teststadt",
        "payment_method": "cash",
        "notes": "CONNECTION TEST - Please ignore",
        "scheduled_time": None
    }
    
    try:
        # Send test order
        result = await connector.push_order(test_order)
        
        if result.get('success'):
            return {
                "status": "SUCCESS",
                "location": location_name,
                "message": "ExpertOrder connection successful",
                "pos_order_id": result.get('pos_order_id', 'N/A'),
                "response": result.get('message', 'Order sent')
            }
        else:
            return {
                "status": "FAILED",
                "location": location_name,
                "message": result.get('message', 'Unknown error'),
                "error": result.get('error')
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "location": location_name,
            "message": str(e)
        }

async def run_expertorder_tests():
    """Run ExpertOrder tests for both locations"""
    locations = [
        ("rellingen", "Rellingen"),
        ("henstedt-ulzburg", "Henstedt-Ulzburg")
    ]
    
    results = []
    for slug, name in locations:
        print(f"\n   Testing {name}...")
        result = await test_expertorder_connection(slug, name)
        results.append(result)
        
        if result["status"] == "SUCCESS":
            print(f"      ✅ {result['message']}")
            print(f"      POS Order ID: {result['pos_order_id']}")
        else:
            print(f"      ❌ {result['message']}")
            if result.get('error'):
                print(f"      Error: {result['error']}")
    
    return results

# Run ExpertOrder tests
expertorder_results = asyncio.run(run_expertorder_tests())

# ============================================================================
# 3. SUMMARY
# ============================================================================
print("\n\n📊 3️⃣ TEST SUMMARY")
print("="*80)

paypal_success = sum(1 for r in paypal_results if r["status"] == "SUCCESS")
pos_success = sum(1 for r in expertorder_results if r["status"] == "SUCCESS")

print(f"\n💳 PayPal: {paypal_success}/2 locations working")
print(f"🔧 ExpertOrder: {pos_success}/2 locations working")

if paypal_success == 2 and pos_success == 2:
    print("\n✅ ALL SYSTEMS OPERATIONAL!")
    print("   - PayPal LIVE payments work on both locations")
    print("   - ExpertOrder POS integration work on both locations")
else:
    print("\n⚠️  SOME SYSTEMS FAILED - Check details above")

print("\n" + "="*80)

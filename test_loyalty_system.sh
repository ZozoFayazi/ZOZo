#!/bin/bash

API_URL="https://menu-management-1.preview.emergentagent.com/api"
LOC_ID="49aff347-a6c3-407c-ad4a-59d5d0852314"

echo "========================================="
echo "BONUSPUNKTE-SYSTEM: E2E TESTS"
echo "========================================="
echo ""

# Test A: Cash mit Email
echo "===== TEST A: Cash-Bestellung MIT Email ====="
TEST_EMAIL="test-a@zozo.de"

echo "1. Vorher:"
curl -s "$API_URL/loyalty/account/$TEST_EMAIL" | python3 -m json.tool | grep -E '"points":|"total_earned":'

echo ""
echo "2. Bestellung (25€ Item, Pickup 10% = 22.50€ → 2 Punkte):"
curl -s -X POST "$API_URL/orders" -H "Content-Type: application/json" -d "{
  \"location_id\": \"$LOC_ID\",
  \"items\": [{\"menu_item_id\": \"693c5e30e51d9e97f092ccb3\", \"name\": \"Test\", \"price\": 25.0, \"size\": \"normal\", \"quantity\": 1}],
  \"customer\": {\"name\": \"Test A\", \"phone\": \"+491701\", \"email\": \"$TEST_EMAIL\", \"address\": \"Abholung\", \"postal_code\": \"00000\", \"city\": \"Rellingen\"},
  \"payment_method\": \"cash\",
  \"points_to_redeem\": 0,
  \"is_pickup\": true
}" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"✅ Order: {d['order_number']}, Total: €{d['total']:.2f}, Points Earned: {d.get('points_earned', 'ERROR')}\")"

sleep 2
echo ""
echo "3. Nachher:"
curl -s "$API_URL/loyalty/account/$TEST_EMAIL" | python3 -m json.tool | grep -E '"points":|"total_earned":'

echo ""
echo "4. Transaktionen:"
curl -s "$API_URL/loyalty/transactions/$TEST_EMAIL?limit=2" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"  - {t['type']}: {t['points']} Punkte ({t['description']})\") for t in data]"

echo ""
echo ""

# Test B: Cash OHNE Email
echo "===== TEST B: Cash-Bestellung OHNE Email ====="
echo "Bestellung ohne Email (sollte funktionieren, aber keine Punkte):"
curl -s -X POST "$API_URL/orders" -H "Content-Type: application/json" -d "{
  \"location_id\": \"$LOC_ID\",
  \"items\": [{\"menu_item_id\": \"693c5e30e51d9e97f092ccb3\", \"name\": \"Test\", \"price\": 15.0, \"size\": \"normal\", \"quantity\": 1}],
  \"customer\": {\"name\": \"Test B\", \"phone\": \"+491702\", \"address\": \"Abholung\", \"postal_code\": \"00000\", \"city\": \"Rellingen\"},
  \"payment_method\": \"cash\",
  \"points_to_redeem\": 0,
  \"is_pickup\": true
}" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"✅ Order: {d['order_number']}, Total: €{d['total']:.2f}, Points Earned: {d.get('points_earned', 'N/A (expected)')}\")"

echo ""
echo ""

# Test C: Punkte einlösen
echo "===== TEST C: Punkte EINLÖSEN (Cash) ====="
TEST_EMAIL_C="test-c@zozo.de"

echo "1. Account mit 20 Punkten vorbereiten..."
# Create account with points via backend
python3 << EOF
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv(Path('/app/backend/.env'))
mongo_url = os.environ['MONGO_URL']

async def setup():
    client = AsyncIOMotorClient(mongo_url)
    db = client['test_database']
    
    # Delete existing
    await db.loyalty_accounts.delete_one({"customer_email": "$TEST_EMAIL_C"})
    await db.loyalty_transactions.delete_many({"customer_email": "$TEST_EMAIL_C"})
    
    # Create new with 20 points
    await db.loyalty_accounts.insert_one({
        "customer_email": "$TEST_EMAIL_C",
        "points": 20,
        "total_earned": 20,
        "total_spent": 0,
        "achievements": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    await db.loyalty_transactions.insert_one({
        "customer_email": "$TEST_EMAIL_C",
        "type": "earned",
        "points": 20,
        "description": "Test-Setup",
        "order_id": None,
        "related_achievement": None,
        "created_at": datetime.utcnow()
    })
    print("✅ Account erstellt")

asyncio.run(setup())
EOF

echo ""
echo "2. Vorher:"
curl -s "$API_URL/loyalty/account/$TEST_EMAIL_C" | python3 -m json.tool | grep -E '"points":'

echo ""
echo "3. Bestellung mit 10 Punkten einlösen (= 5€ Rabatt):"
curl -s -X POST "$API_URL/orders" -H "Content-Type: application/json" -d "{
  \"location_id\": \"$LOC_ID\",
  \"items\": [{\"menu_item_id\": \"693c5e30e51d9e97f092ccb3\", \"name\": \"Test\", \"price\": 20.0, \"size\": \"normal\", \"quantity\": 1}],
  \"customer\": {\"name\": \"Test C\", \"phone\": \"+491703\", \"email\": \"$TEST_EMAIL_C\", \"address\": \"Abholung\", \"postal_code\": \"00000\", \"city\": \"Rellingen\"},
  \"payment_method\": \"cash\",
  \"points_to_redeem\": 10,
  \"is_pickup\": true
}" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"✅ Order: {d['order_number']}, Subtotal: €{d['subtotal']:.2f}, Discount: €{d['discount']:.2f}, Total: €{d['total']:.2f}, Points Used: {d.get('points_redeemed', 'ERROR')}, Points Earned: {d.get('points_earned', 'ERROR')}\")"

sleep 2
echo ""
echo "4. Nachher (Erwartet: 20 - 10 + 1 = 11 Punkte):"
curl -s "$API_URL/loyalty/account/$TEST_EMAIL_C" | python3 -m json.tool | grep -E '"points":|"total_spent":'

echo ""
echo ""

echo "========================================="
echo "ALLE TESTS ABGESCHLOSSEN"
echo "========================================="

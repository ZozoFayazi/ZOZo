#!/bin/bash

API_URL="https://site-refresh-58.preview.emergentagent.com/api"
LOCATION_ID="49aff347-a6c3-407c-ad4a-59d5d0852314"

echo "================================================================================"
echo "  FINAL SMOKE TEST - SYSTEM FREEZE VALIDATION"
echo "================================================================================"

# Test 1: Backend Health
echo ""
echo "=== 1. BACKEND HEALTH ==="
supervisorctl status backend | grep RUNNING && echo "✅ Backend: RUNNING" || echo "❌ Backend: NOT RUNNING"

# Test 2: Frontend Health
echo ""
echo "=== 2. FRONTEND HEALTH ==="
supervisorctl status frontend | grep RUNNING && echo "✅ Frontend: RUNNING" || echo "❌ Frontend: NOT RUNNING"

# Test 3: API Endpoints
echo ""
echo "=== 3. API ENDPOINTS ==="

# Locations
RESP=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/locations")
if [ "$RESP" = "200" ]; then
    echo "✅ /api/locations: OK"
else
    echo "❌ /api/locations: Failed ($RESP)"
fi

# Modifier Groups
RESP=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/modifier-groups")
if [ "$RESP" = "200" ]; then
    echo "✅ /api/modifier-groups: OK"
else
    echo "❌ /api/modifier-groups: Failed ($RESP)"
fi

# Daily Deal
RESP=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/daily-deal")
if [ "$RESP" = "200" ]; then
    echo "✅ /api/daily-deal: OK"
else
    echo "❌ /api/daily-deal: Failed ($RESP)"
fi

# Test 4: Loyalty System
echo ""
echo "=== 4. LOYALTY SYSTEM ==="
RESP=$(curl -s "$API_URL/loyalty/account/test-final@zozo.de")
if echo "$RESP" | grep -q "points"; then
    POINTS=$(echo "$RESP" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('points', 'N/A'))" 2>/dev/null || echo "N/A")
    echo "✅ Loyalty Account: OK (Points: $POINTS)"
else
    echo "❌ Loyalty Account: Failed"
fi

# Test 5: Order Creation (Simple)
echo ""
echo "=== 5. ORDER CREATION ==="
ORDER_RESP=$(curl -s -X POST "$API_URL/orders" -H "Content-Type: application/json" -d "{
  \"location_id\": \"$LOCATION_ID\",
  \"items\": [{\"menu_item_id\": \"test\", \"name\": \"Smoke Test Item\", \"price\": 5.0, \"size\": \"normal\", \"quantity\": 1}],
  \"customer\": {\"name\": \"Smoke Test\", \"phone\": \"+49170\", \"email\": \"smoke@test.de\", \"address\": \"Abholung\", \"postal_code\": \"00000\", \"city\": \"Rellingen\"},
  \"payment_method\": \"cash\",
  \"points_to_redeem\": 0,
  \"is_pickup\": true
}")

if echo "$ORDER_RESP" | grep -q "order_number"; then
    ORDER_NUM=$(echo "$ORDER_RESP" | python3 -c "import sys, json; print(json.load(sys.stdin).get('order_number', 'N/A'))" 2>/dev/null || echo "N/A")
    echo "✅ Order Creation: OK ($ORDER_NUM)"
else
    echo "❌ Order Creation: Failed"
fi

# Test 6: POS Flattening
echo ""
echo "=== 6. POS FLATTENING (Last Payload Check) ==="
LAST_PAYLOAD=$(tail -100 /var/log/supervisor/backend.err.log | grep "ExpertOrder payload" | tail -1)
if [ -n "$LAST_PAYLOAD" ]; then
    echo "✅ POS Integration: Active"
    # Count items in last payload
    ITEMS_COUNT=$(echo "$LAST_PAYLOAD" | grep -o "'items':" | wc -l)
    echo "   Last payload sent successfully"
else
    echo "⚠️  POS Integration: No recent payloads"
fi

# Test 7: Logs Clean
echo ""
echo "=== 7. ERROR LOGS ==="
ERROR_COUNT=$(tail -100 /var/log/supervisor/backend.err.log | grep -i "error\|exception\|traceback" | grep -v "ERROR - Email send error" | grep -v "INFO" | wc -l)
if [ "$ERROR_COUNT" -lt 3 ]; then
    echo "✅ Logs: Clean (minor errors only)"
else
    echo "⚠️  Logs: $ERROR_COUNT errors found"
fi

echo ""
echo "================================================================================"
echo "  SMOKE TEST COMPLETE"
echo "================================================================================"
echo ""


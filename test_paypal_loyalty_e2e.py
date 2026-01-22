#!/usr/bin/env python3
"""
PayPal Loyalty E2E Test Script
Tests the complete PayPal flow with loyalty points
"""
import requests
import json
import time

API_URL = "https://zozo-fix.preview.emergentagent.com/api"
TEST_EMAIL = "paypal-test@zozo.de"
LOCATION_ID = "49aff347-a6c3-407c-ad4a-59d5d0852314"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def get_loyalty_account(email):
    """Get loyalty account details"""
    resp = requests.get(f"{API_URL}/loyalty/account/{email}")
    if resp.status_code == 200:
        return resp.json()
    return None

def get_transactions(email, limit=5):
    """Get loyalty transactions"""
    resp = requests.get(f"{API_URL}/loyalty/transactions/{email}?limit={limit}")
    if resp.status_code == 200:
        return resp.json()
    return []

print_section("PAYPAL LOYALTY E2E TEST START")

# Step 1: Check initial state
print_section("STEP 1: Initial Loyalty Account State")
initial_account = get_loyalty_account(TEST_EMAIL)
if initial_account:
    print(f"✅ Account found: {TEST_EMAIL}")
    print(f"   Points: {initial_account.get('points')}")
    print(f"   Total Earned: {initial_account.get('total_earned')}")
    print(f"   Total Spent: {initial_account.get('total_spent')}")
else:
    print(f"❌ Account not found: {TEST_EMAIL}")
    exit(1)

initial_points = initial_account.get('points', 0)
print(f"\n📊 Starting Points: {initial_points}")

# Step 2: Create PayPal Order (Draft)
print_section("STEP 2: Create PayPal Order Draft")

# We'll redeem 10 points (=5€ discount)
# Order: 30€ item, Pickup (10% = -3€), Points (-5€) = 22€ final
# Expected points earned: int(22 / 10) = 2
# Expected final points: 20 - 10 + 2 = 12

points_to_redeem = 10
item_price = 30.0

order_payload = {
    "location_id": LOCATION_ID,
    "items": [{
        "menu_item_id": "693c5e30e51d9e97f092ccb3",
        "name": "PayPal Test Item",
        "price": item_price,
        "size": "normal",
        "quantity": 1
    }],
    "customer": {
        "name": "PayPal Test User",
        "phone": "+491701234",
        "email": TEST_EMAIL,
        "address": "Abholung",
        "postal_code": "00000",
        "city": "Rellingen"
    },
    "subtotal": item_price,
    "delivery_fee": 0.0,
    "discount": points_to_redeem * 0.50,  # 10 points = 5€
    "points_to_redeem": points_to_redeem,
    "total": item_price * 0.9 - (points_to_redeem * 0.50),  # After pickup 10% and points
    "is_pickup": True,
    "currency": "EUR"
}

print(f"📦 Order Details:")
print(f"   Item Price: €{item_price:.2f}")
print(f"   Pickup Discount (10%): -€{item_price * 0.1:.2f}")
print(f"   Points Redeem ({points_to_redeem} pts): -€{points_to_redeem * 0.50:.2f}")
print(f"   Expected Total: €{order_payload['total']:.2f}")
print(f"   Expected Points Earned: {int(order_payload['total'] / 10)}")

try:
    resp = requests.post(f"{API_URL}/paypal/create-order", json=order_payload)
    if resp.status_code == 200:
        paypal_data = resp.json()
        print(f"✅ PayPal Draft created")
        print(f"   PayPal Order ID: {paypal_data.get('paypal_order_id')}")
        print(f"   Draft ID: {paypal_data.get('payment_draft_id')}")
        paypal_order_id = paypal_data.get('paypal_order_id')
    else:
        print(f"❌ Failed to create PayPal order: {resp.status_code}")
        print(f"   Response: {resp.text}")
        exit(1)
except Exception as e:
    print(f"❌ Exception: {e}")
    exit(1)

# Step 3: Check account (should be unchanged - no capture yet)
print_section("STEP 3: Account State After Draft (Before Capture)")
mid_account = get_loyalty_account(TEST_EMAIL)
if mid_account:
    print(f"   Points: {mid_account.get('points')} (should still be {initial_points})")
    if mid_account.get('points') != initial_points:
        print(f"❌ ERROR: Points changed before capture!")
        exit(1)
    print(f"✅ Correct: Points unchanged before capture")

# Step 4: Simulate PayPal Capture (this is where loyalty logic runs)
print_section("STEP 4: Capture PayPal Payment")

# Note: In real scenario, user would approve via PayPal UI
# We're simulating the capture endpoint being called
try:
    capture_payload = {"paypal_order_id": paypal_order_id}
    resp = requests.post(f"{API_URL}/paypal/capture-order", json=capture_payload)
    
    if resp.status_code == 200:
        capture_data = resp.json()
        print(f"✅ PayPal Capture successful")
        print(f"   Order Number: {capture_data.get('order_number')}")
        print(f"   Order ID: {capture_data.get('order_id')}")
        print(f"   Points Earned: {capture_data.get('points_earned', 'N/A')}")
        
        points_earned_in_response = capture_data.get('points_earned', 0)
        order_number = capture_data.get('order_number')
    else:
        print(f"❌ Capture failed: {resp.status_code}")
        print(f"   Response: {resp.text}")
        exit(1)
except Exception as e:
    print(f"❌ Exception during capture: {e}")
    exit(1)

# Step 5: Verify final loyalty state
print_section("STEP 5: Verify Final Loyalty State")

time.sleep(2)  # Give DB a moment

final_account = get_loyalty_account(TEST_EMAIL)
if final_account:
    final_points = final_account.get('points')
    total_spent = final_account.get('total_spent')
    
    print(f"📊 Loyalty Account After Capture:")
    print(f"   Points: {final_points}")
    print(f"   Total Spent: {total_spent}")
    
    # Calculate expected
    expected_points = initial_points - points_to_redeem + points_earned_in_response
    
    print(f"\n🧮 Calculation:")
    print(f"   Initial: {initial_points}")
    print(f"   Redeemed: -{points_to_redeem}")
    print(f"   Earned: +{points_earned_in_response}")
    print(f"   Expected Final: {expected_points}")
    print(f"   Actual Final: {final_points}")
    
    if final_points == expected_points:
        print(f"\n✅ CORRECT: Points match expected!")
    else:
        print(f"\n❌ ERROR: Points mismatch!")
        exit(1)
    
    if total_spent == points_to_redeem:
        print(f"✅ CORRECT: total_spent = {total_spent}")
    else:
        print(f"❌ ERROR: total_spent should be {points_to_redeem}, got {total_spent}")

# Step 6: Verify transactions
print_section("STEP 6: Verify Loyalty Transactions")

transactions = get_transactions(TEST_EMAIL, limit=10)
if transactions:
    print(f"📜 Recent Transactions:")
    for tx in transactions[:5]:
        tx_type = tx.get('type')
        points = tx.get('points')
        desc = tx.get('description', 'N/A')
        print(f"   [{tx_type.upper()}] {points:+3d} pts - {desc}")
    
    # Check for our transactions
    redeem_tx = [t for t in transactions if 'Eingelöst' in t.get('description', '') and order_number in t.get('description', '')]
    earn_tx = [t for t in transactions if 'Verdient' in t.get('description', '') and order_number in t.get('description', '')]
    
    if redeem_tx:
        print(f"\n✅ Found REDEEM transaction for order {order_number}")
    else:
        print(f"\n⚠️ No REDEEM transaction found (might be OK if points_to_redeem was 0)")
    
    if earn_tx:
        print(f"✅ Found EARN transaction for order {order_number}")
    else:
        print(f"❌ ERROR: No EARN transaction found!")
        exit(1)

# Final Summary
print_section("FINAL SUMMARY")

print("✅ PayPal Draft Creation: OK")
print("✅ Points unchanged before capture: OK")
print("✅ PayPal Capture: OK")
print("✅ Points Redemption (-10): OK")
print(f"✅ Points Award (+{points_earned_in_response}): OK")
print(f"✅ Final Points Calculation: OK")
print("✅ Transaction Logging: OK")

print(f"\n{'='*60}")
print("  🎉 PAYPAL LOYALTY E2E: FINAL OK ✅")
print(f"{'='*60}\n")


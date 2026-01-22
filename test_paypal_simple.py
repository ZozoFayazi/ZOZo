#!/usr/bin/env python3
"""Simplified PayPal Test - Correct Totals"""
import requests

API_URL = "https://menu-management-1.preview.emergentagent.com/api"
TEST_EMAIL = "paypal-test@zozo.de"
LOCATION_ID = "49aff347-a6c3-407c-ad4a-59d5d0852314"

print("=== SIMPLIFIED PAYPAL TEST ===\n")

# Get current points
resp = requests.get(f"{API_URL}/loyalty/account/{TEST_EMAIL}")
if resp.status_code == 200:
    account = resp.json()
    print(f"✅ Initial Points: {account.get('points')}")
    initial_points = account.get('points', 0)
else:
    print("❌ Failed to get account")
    exit(1)

# Create PayPal order WITHOUT points redemption first (simpler test)
# Item: 30€, Pickup 10% = 27€
item_price = 30.0
pickup_discount = item_price * 0.1  # 3€
subtotal = item_price
delivery_fee = 0.0
total_discount = pickup_discount  # Only pickup, no points for now
final_total = subtotal + delivery_fee - total_discount

print(f"\n📦 Order Calculation:")
print(f"   Subtotal: €{subtotal:.2f}")
print(f"   Delivery Fee: €{delivery_fee:.2f}")
print(f"   Total Discount: €{total_discount:.2f}")
print(f"   Final Total: €{final_total:.2f}")
print(f"   Expected Points Earned: {int(final_total / 10)}")

order_payload = {
    "location_id": LOCATION_ID,
    "items": [{
        "menu_item_id": "693c5e30e51d9e97f092ccb3",
        "name": "Test Item",
        "price": item_price,
        "size": "normal",
        "quantity": 1
    }],
    "customer": {
        "name": "PayPal Test",
        "phone": "+491701234",
        "email": TEST_EMAIL,
        "address": "Abholung",
        "postal_code": "00000",
        "city": "Rellingen"
    },
    "subtotal": subtotal,
    "delivery_fee": delivery_fee,
    "discount": total_discount,
    "points_to_redeem": 0,  # No points redemption for simplicity
    "total": final_total,
    "is_pickup": True,
    "currency": "EUR"
}

print(f"\n🔄 Creating PayPal draft...")
resp = requests.post(f"{API_URL}/paypal/create-order", json=order_payload)

if resp.status_code == 200:
    paypal_data = resp.json()
    print(f"✅ Draft created: {paypal_data.get('paypal_order_id')}")
    paypal_order_id = paypal_data.get('paypal_order_id')
else:
    print(f"❌ Failed: {resp.status_code}")
    print(f"   Response: {resp.text}")
    exit(1)

# Check points (should be unchanged)
resp = requests.get(f"{API_URL}/loyalty/account/{TEST_EMAIL}")
if resp.status_code == 200:
    account = resp.json()
    if account.get('points') == initial_points:
        print(f"✅ Points unchanged before capture: {account.get('points')}")
    else:
        print(f"❌ Points changed unexpectedly!")

# Simulate capture
print(f"\n💰 Simulating PayPal capture...")
capture_payload = {"paypal_order_id": paypal_order_id}
resp = requests.post(f"{API_URL}/paypal/capture-order", json=capture_payload)

if resp.status_code == 200:
    capture_data = resp.json()
    print(f"✅ Capture successful!")
    print(f"   Order: {capture_data.get('order_number')}")
    print(f"   Points Earned: {capture_data.get('points_earned', 'N/A')}")
    
    # Wait and check final state
    import time
    time.sleep(2)
    
    resp = requests.get(f"{API_URL}/loyalty/account/{TEST_EMAIL}")
    if resp.status_code == 200:
        account = resp.json()
        final_points = account.get('points')
        expected = initial_points + capture_data.get('points_earned', 0)
        
        print(f"\n📊 Final State:")
        print(f"   Initial: {initial_points}")
        print(f"   Earned: +{capture_data.get('points_earned', 0)}")
        print(f"   Expected: {expected}")
        print(f"   Actual: {final_points}")
        
        if final_points == expected:
            print(f"\n✅ PAYPAL LOYALTY: OK")
        else:
            print(f"\n❌ Points mismatch!")
else:
    print(f"❌ Capture failed: {resp.status_code}")
    print(f"   Response: {resp.text}")


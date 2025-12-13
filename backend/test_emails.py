"""
Test script to send all email templates to a test address
"""
import asyncio
from datetime import datetime
from email_service import (
    send_verification_email,
    send_order_confirmation_email,
    send_status_update_email,
    send_review_request_email
)

TEST_EMAIL = "krischmaazimi@live.de"

async def send_all_test_emails():
    print(f"🧪 Sending test emails to: {TEST_EMAIL}\n")
    
    # 1. Verification Email
    print("1️⃣ Sending verification email...")
    success = send_verification_email(TEST_EMAIL, "123456")
    print(f"   {'✅ Success' if success else '❌ Failed'}\n")
    
    await asyncio.sleep(2)
    
    # 2. Order Confirmation Email
    print("2️⃣ Sending order confirmation email...")
    test_order = {
        "order_number": "TEST-001",
        "items": [
            {"name": "Classic Beef Burger", "quantity": 2, "price": 8.50, "size": "Normal"},
            {"name": "Pommes Frites", "quantity": 1, "price": 3.50, "size": "Groß"},
            {"name": "Cola", "quantity": 2, "price": 2.50, "size": None}
        ],
        "total": 25.50,
        "estimated_time": 30,
        "customer": {
            "name": "Test Kunde",
            "email": TEST_EMAIL,
            "address": "Teststraße 123",
            "postal_code": "25462",
            "city": "Rellingen"
        },
        "payment_method": "PayPal"
    }
    
    test_location = {
        "name": "ZOZO Burger Rellingen",
        "address": "Möwenstraße 2, 25462 Rellingen"
    }
    
    success = send_order_confirmation_email(test_order, test_location)
    print(f"   {'✅ Success' if success else '❌ Failed'}\n")
    
    await asyncio.sleep(2)
    
    # 3. Status Update Emails
    statuses = [
        ("preparing", "In Zubereitung"),
        ("out_for_delivery", "Unterwegs"),
        ("delivered", "Zugestellt")
    ]
    
    for idx, (status, status_name) in enumerate(statuses, start=3):
        print(f"{idx}️⃣ Sending status update email: {status_name}...")
        success = send_status_update_email(test_order, status, test_location)
        print(f"   {'✅ Success' if success else '❌ Failed'}\n")
        await asyncio.sleep(2)
    
    # 4. Review Request Email
    print("6️⃣ Sending review request email...")
    test_location_with_slug = {**test_location, "slug": "rellingen"}
    success = send_review_request_email(test_order, test_location_with_slug)
    print(f"   {'✅ Success' if success else '❌ Failed'}\n")
    
    print("=" * 60)
    print("✅ All test emails sent!")
    print(f"📧 Check your inbox at: {TEST_EMAIL}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(send_all_test_emails())

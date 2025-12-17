"""
ZOZO Burger Backend API Tests
Tests all backend endpoints for the multi-location ordering platform
"""
import requests
import sys
from datetime import datetime

class ZOZOBurgerAPITester:
    def __init__(self, base_url="https://zozofinal.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.location_id = None
        self.menu_item_id = None
        self.order_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        print(f"   URL: {method} {endpoint}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers, timeout=10)
            else:
                print(f"❌ Unsupported method: {method}")
                return False, {}

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"   ✅ PASSED - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"   ❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text[:200]}")
                
                self.failed_tests.append({
                    "test": name,
                    "endpoint": endpoint,
                    "expected": expected_status,
                    "actual": response.status_code
                })
                return False, {}

        except requests.exceptions.Timeout:
            print(f"   ❌ FAILED - Request timeout")
            self.failed_tests.append({"test": name, "endpoint": endpoint, "error": "Timeout"})
            return False, {}
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            self.failed_tests.append({"test": name, "endpoint": endpoint, "error": str(e)})
            return False, {}

    def test_root(self):
        """Test root endpoint"""
        success, response = self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_get_locations(self):
        """Test getting all locations"""
        success, response = self.run_test(
            "Get Locations",
            "GET",
            "locations",
            200
        )
        if success and response:
            if isinstance(response, list) and len(response) >= 2:
                self.location_id = response[0]['id']
                print(f"   📍 Found {len(response)} locations")
                print(f"   Using location: {response[0].get('name')} (ID: {self.location_id})")
                return True
            else:
                print(f"   ⚠️  Expected at least 2 locations, got {len(response) if isinstance(response, list) else 0}")
        return success

    def test_get_menu(self):
        """Test getting menu for a location"""
        if not self.location_id:
            print("   ⚠️  Skipping - No location_id available")
            return False
        
        success, response = self.run_test(
            "Get Menu for Location",
            "GET",
            f"menu?location_id={self.location_id}",
            200
        )
        
        if success and response:
            if isinstance(response, list) and len(response) > 0:
                print(f"   📋 Found {len(response)} categories")
                # Store a menu item for later tests
                for category in response:
                    if 'items' in category and len(category['items']) > 0:
                        self.menu_item_id = category['items'][0]['id']
                        print(f"   🍔 Sample item: {category['items'][0].get('name')}")
                        break
                return True
            else:
                print(f"   ⚠️  No menu categories found")
        return success

    def test_create_order(self):
        """Test creating an order"""
        if not self.location_id or not self.menu_item_id:
            print("   ⚠️  Skipping - Missing location_id or menu_item_id")
            return False
        
        order_data = {
            "location_id": self.location_id,
            "items": [
                {
                    "menu_item_id": self.menu_item_id,
                    "name": "Test Burger",
                    "price": 9.99,
                    "size": "medium",
                    "quantity": 2
                }
            ],
            "customer": {
                "name": "Test Customer",
                "phone": "+49 123 456789",
                "address": "Test Street 123",
                "postal_code": "25462",  # Valid Rellingen postal code
                "city": "Rellingen",
                "notes": "Test order"
            },
            "payment_method": "cash"
        }
        
        success, response = self.run_test(
            "Create Order",
            "POST",
            "orders",
            200,
            data=order_data
        )
        
        if success and response:
            self.order_id = response.get('id')
            order_number = response.get('order_number')
            total = response.get('total')
            print(f"   📦 Order created: {order_number} (Total: €{total})")
            return True
        return success

    def test_admin_login(self):
        """Test admin login"""
        credentials = {
            "email": "owner@zozo.com",
            "password": "owner_password"
        }
        
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data=credentials
        )
        
        if success and response:
            self.token = response.get('access_token')
            user = response.get('user', {})
            print(f"   🔑 Logged in as: {user.get('email')} ({user.get('role')})")
            return True
        return success

    def test_get_current_user(self):
        """Test getting current user info"""
        if not self.token:
            print("   ⚠️  Skipping - No auth token available")
            return False
        
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        
        if success and response:
            print(f"   👤 User: {response.get('email')}")
            return True
        return success

    def test_get_admin_orders(self):
        """Test getting orders (admin)"""
        if not self.token:
            print("   ⚠️  Skipping - No auth token available")
            return False
        
        success, response = self.run_test(
            "Get Admin Orders",
            "GET",
            "admin/orders",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   📋 Found {len(response)} orders")
                return True
        return success

    def test_update_order_status(self):
        """Test updating order status"""
        if not self.token or not self.order_id:
            print("   ⚠️  Skipping - Missing token or order_id")
            return False
        
        status_update = {"status": "preparing"}
        
        success, response = self.run_test(
            "Update Order Status",
            "PATCH",
            f"admin/orders/{self.order_id}/status",
            200,
            data=status_update
        )
        
        if success and response:
            new_status = response.get('status')
            print(f"   ✏️  Order status updated to: {new_status}")
            return True
        return success

    def test_get_dashboard_stats(self):
        """Test getting dashboard statistics"""
        if not self.token:
            print("   ⚠️  Skipping - No auth token available")
            return False
        
        success, response = self.run_test(
            "Get Dashboard Stats",
            "GET",
            "admin/stats",
            200
        )
        
        if success and response:
            print(f"   📊 Stats:")
            print(f"      Total Orders: {response.get('total_orders')}")
            print(f"      New Orders: {response.get('new_orders')}")
            print(f"      Revenue: €{response.get('total_revenue')}")
            return True
        return success

    def test_get_menu_items_admin(self):
        """Test getting menu items (admin)"""
        if not self.token:
            print("   ⚠️  Skipping - No auth token available")
            return False
        
        success, response = self.run_test(
            "Get Menu Items (Admin)",
            "GET",
            "admin/menu-items",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   🍔 Found {len(response)} menu items")
                return True
        return success

    def test_location_manager_login(self):
        """Test location manager login"""
        credentials = {
            "email": "rellingen@zozo.com",
            "password": "manager_password"
        }
        
        success, response = self.run_test(
            "Location Manager Login",
            "POST",
            "auth/login",
            200,
            data=credentials
        )
        
        if success and response:
            manager_token = response.get('access_token')
            user = response.get('user', {})
            print(f"   🔑 Manager logged in: {user.get('email')}")
            print(f"   📍 Location: {user.get('location_id')}")
            return True
        return success

    def test_check_delivery_valid(self):
        """Test delivery check with valid postal code"""
        delivery_data = {
            "postal_code": "25462"  # Rellingen postal code
        }
        
        success, response = self.run_test(
            "Check Delivery (Valid Postal Code)",
            "POST",
            "check-delivery",
            200,
            data=delivery_data
        )
        
        if success and response:
            can_deliver = response.get('can_deliver')
            available_locations = response.get('available_locations', [])
            print(f"   📍 Can deliver: {can_deliver}")
            print(f"   🏪 Available locations: {len(available_locations)}")
            if available_locations:
                loc = available_locations[0]
                print(f"   💰 Delivery fee: €{loc.get('delivery_fee')}")
                print(f"   📦 Min order: €{loc.get('min_order_value')}")
            return True
        return success

    def test_check_delivery_invalid(self):
        """Test delivery check with invalid postal code"""
        delivery_data = {
            "postal_code": "99999"  # Invalid postal code
        }
        
        success, response = self.run_test(
            "Check Delivery (Invalid Postal Code)",
            "POST",
            "check-delivery",
            200,
            data=delivery_data
        )
        
        if success and response:
            can_deliver = response.get('can_deliver')
            message = response.get('message')
            print(f"   📍 Can deliver: {can_deliver}")
            print(f"   💬 Message: {message}")
            return True
        return success

    def test_get_location_settings(self):
        """Test getting location settings (admin)"""
        if not self.token:
            print("   ⚠️  Skipping - No auth token available")
            return False
        
        success, response = self.run_test(
            "Get Location Settings",
            "GET",
            "admin/location-settings",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   🏪 Found {len(response)} location(s)")
                for loc in response:
                    delivery_zone = loc.get('delivery_zone', {})
                    postal_codes = delivery_zone.get('postal_codes', [])
                    print(f"   📍 {loc.get('name')}: {len(postal_codes)} postal codes")
                return True
        return success

    def test_update_location_settings(self):
        """Test updating location settings"""
        if not self.token or not self.location_id:
            print("   ⚠️  Skipping - Missing token or location_id")
            return False
        
        settings_update = {
            "postal_codes": ["25462", "25421", "25451"],
            "min_order_value": 12.0,
            "delivery_fee": 3.0,
            "free_delivery_threshold": 20.0
        }
        
        success, response = self.run_test(
            "Update Location Settings",
            "PATCH",
            f"admin/location-settings/{self.location_id}",
            200,
            data=settings_update
        )
        
        if success and response:
            delivery_zone = response.get('delivery_zone', {})
            print(f"   ✏️  Settings updated:")
            print(f"      Min order: €{delivery_zone.get('min_order_value')}")
            print(f"      Delivery fee: €{delivery_zone.get('delivery_fee')}")
            return True
        return success

    def test_get_deals(self):
        """Test getting all deals (admin)"""
        if not self.token:
            print("   ⚠️  Skipping - No auth token available")
            return False
        
        success, response = self.run_test(
            "Get Deals (Admin)",
            "GET",
            "admin/deals",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   🎁 Found {len(response)} deals")
                return True
        return success

    def test_create_deal(self):
        """Test creating a new deal"""
        if not self.token:
            print("   ⚠️  Skipping - No auth token available")
            return False
        
        deal_data = {
            "title": "Test Deal - 20% Off",
            "description": "Test promotion for automated testing",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "min_order_value": 15.0,
            "location_ids": [],
            "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800"
        }
        
        success, response = self.run_test(
            "Create Deal",
            "POST",
            "admin/deals",
            200,
            data=deal_data
        )
        
        if success and response:
            deal_id = response.get('id')
            title = response.get('title')
            print(f"   🎁 Deal created: {title} (ID: {deal_id})")
            return True
        return success

    def test_get_order_history(self):
        """Test getting order history for quick reorder"""
        # Use the test customer phone from the order we created
        success, response = self.run_test(
            "Get Order History",
            "GET",
            "orders/history?customer_phone=%2B49%20123%20456789",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   📜 Found {len(response)} orders in history")
                return True
        return success

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 70)
        print("🧪 ZOZO Burger Backend API Test Suite - Phase 3")
        print("=" * 70)
        print(f"Base URL: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # Public endpoints (no auth required)
        print("\n📌 PUBLIC ENDPOINTS")
        print("-" * 70)
        self.test_root()
        self.test_get_locations()
        self.test_get_menu()
        self.test_check_delivery_valid()
        self.test_check_delivery_invalid()
        self.test_create_order()

        # Admin authentication
        print("\n📌 AUTHENTICATION")
        print("-" * 70)
        self.test_admin_login()
        self.test_get_current_user()
        self.test_location_manager_login()

        # Admin endpoints (auth required)
        print("\n📌 ADMIN ENDPOINTS")
        print("-" * 70)
        self.test_get_admin_orders()
        self.test_update_order_status()
        self.test_get_dashboard_stats()
        self.test_get_menu_items_admin()
        self.test_get_location_settings()
        self.test_update_location_settings()
        
        # Deals endpoints (premium feature)
        print("\n📌 DEALS & PROMOTIONS (Premium Feature)")
        print("-" * 70)
        self.test_get_deals()
        self.test_create_deal()
        
        # Order history for quick reorder (premium feature)
        print("\n📌 QUICK REORDER (Premium Feature)")
        print("-" * 70)
        self.test_get_order_history()

        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {len(self.failed_tests)} ❌")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"   {i}. {test['test']}")
                print(f"      Endpoint: {test['endpoint']}")
                if 'expected' in test:
                    print(f"      Expected: {test['expected']}, Got: {test['actual']}")
                if 'error' in test:
                    print(f"      Error: {test['error']}")
        
        print("=" * 70)
        
        return 0 if len(self.failed_tests) == 0 else 1

def main():
    tester = ZOZOBurgerAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())

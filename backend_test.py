"""
ZOZO Burger Backend API Tests
Tests all backend endpoints for the multi-location ordering platform
"""
import requests
import sys
from datetime import datetime

class ZOZOBurgerAPITester:
    def __init__(self, base_url="https://eatease-18.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.owner_token = None  # Store owner token separately
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
            "Admin Login (Owner)",
            "POST",
            "auth/login",
            200,
            data=credentials
        )
        
        if success and response:
            self.token = response.get('access_token')
            self.owner_token = self.token  # Store owner token
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
        # Save owner token before manager login
        saved_owner_token = self.owner_token
        
        credentials = {
            "email": "rellingen@zozo.com",
            "password": "manager_password"
        }
        
        success, response = self.run_test(
            "Location Manager Login (Rellingen)",
            "POST",
            "auth/login",
            200,
            data=credentials
        )
        
        if success and response:
            manager_token = response.get('access_token')
            user = response.get('user', {})
            print(f"   🔑 Manager logged in: {user.get('email')}")
            print(f"   📍 Role: {user.get('role')}")
            # Restore owner token for subsequent admin tests
            self.token = saved_owner_token
            print(f"   🔄 Restored owner token")
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

    def test_get_failed_pos_orders(self):
        """Test getting failed POS orders queue"""
        if not self.token:
            print("   ⚠️  Skipping - No auth token available")
            return False
        
        success, response = self.run_test(
            "Get Failed POS Orders",
            "GET",
            "admin/pos/failed-orders",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   📋 Found {len(response)} failed POS orders in queue")
                return True
        return success

    def test_get_product_permissions(self):
        """Test getting product management permissions (Master-Slave)"""
        if not self.token:
            print("   ⚠️  Skipping - No auth token available")
            return False
        
        success, response = self.run_test(
            "Get Product Permissions",
            "GET",
            "admin/products/permissions",
            200
        )
        
        if success and response:
            print(f"   🔐 Permissions:")
            print(f"      Can Create: {response.get('can_create')}")
            print(f"      Can Edit: {response.get('can_edit')}")
            print(f"      Can Reorder: {response.get('can_reorder')}")
            print(f"      Is Master: {response.get('is_master')}")
            print(f"      Location: {response.get('location_slug')}")
            return True
        return success

    def test_get_modifier_groups(self):
        """Test getting modifier groups"""
        success, response = self.run_test(
            "Get Modifier Groups",
            "GET",
            "modifier-groups",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   🍝 Found {len(response)} modifier groups")
                for group in response[:2]:  # Show first 2
                    print(f"      - {group.get('title')}: {len(group.get('options', []))} options")
                return True
        return success

    def test_get_today_daily_deal(self):
        """Test getting today's daily deal (public)"""
        success, response = self.run_test(
            "Get Today's Daily Deal",
            "GET",
            "daily-deal",
            200
        )
        
        if success and response:
            if 'message' in response:
                print(f"   📅 {response.get('message')}")
            else:
                print(f"   🎁 Today's Deal: {response.get('title')}")
                print(f"      Type: {response.get('discount_type')}")
                print(f"      Target: {response.get('target_value')}")
            return True
        return success

    def test_get_all_daily_deals(self):
        """Test getting all daily deals (public)"""
        success, response = self.run_test(
            "Get All Daily Deals",
            "GET",
            "daily-deals",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   📅 Found {len(response)} daily deals")
                for deal in response[:2]:
                    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                    day = weekdays[deal.get('weekday', 0)]
                    print(f"      - {day}: {deal.get('title')}")
                return True
        return success

    def test_get_admin_daily_deals(self):
        """Test getting daily deals (admin)"""
        if not self.token:
            print("   ⚠️  Skipping - No auth token available")
            return False
        
        success, response = self.run_test(
            "Get Daily Deals (Admin)",
            "GET",
            "admin/daily-deals",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   📅 Found {len(response)} daily deals (admin view)")
                return True
        return success

    def test_get_public_features(self):
        """Test getting public features"""
        success, response = self.run_test(
            "Get Public Features",
            "GET",
            "features",
            200
        )
        
        if success and response:
            if isinstance(response, dict):
                enabled_count = sum(1 for v in response.values() if isinstance(v, dict) and v.get('enabled'))
                print(f"   🎛️  Found {len(response)} features")
                print(f"      Enabled: {enabled_count}")
                # Show first 3 features
                for i, (key, feature) in enumerate(list(response.items())[:3]):
                    if isinstance(feature, dict):
                        status = "✅" if feature.get('enabled') else "❌"
                        print(f"      {status} {feature.get('name', key)}")
                return True
        return success

    def test_get_admin_features(self):
        """Test getting all features (admin)"""
        if not self.token:
            print("   ⚠️  Skipping - No auth token available")
            return False
        
        success, response = self.run_test(
            "Get Features (Admin)",
            "GET",
            "admin/features",
            200
        )
        
        if success and response:
            if isinstance(response, dict):
                print(f"   🎛️  Found {len(response)} features (admin view)")
                return True
        return success
    
    def test_create_group_order(self):
        """Test creating a group order"""
        if not self.location_id:
            print("   ⚠️  Skipping - No location_id available")
            return False
        
        success, response = self.run_test(
            "Create Group Order",
            "POST",
            f"group-orders/create?host_name=Test%20Host&location_id={self.location_id}&host_email=test@example.com",
            200
        )
        
        if success and response:
            self.group_code = response.get('group_code')
            print(f"   👥 Group order created: {self.group_code}")
            return True
        return success
    
    def test_get_group_order(self):
        """Test getting group order details"""
        if not hasattr(self, 'group_code') or not self.group_code:
            print("   ⚠️  Skipping - No group_code available")
            return False
        
        success, response = self.run_test(
            "Get Group Order",
            "GET",
            f"group-orders/{self.group_code}",
            200
        )
        
        if success and response:
            print(f"   👥 Group order status: {response.get('status')}")
            print(f"   📦 Items: {len(response.get('items', []))}")
            print(f"   👤 Participants: {len(response.get('participants', []))}")
            return True
        return success
    
    def test_add_items_to_group_order(self):
        """Test adding items to group order"""
        if not hasattr(self, 'group_code') or not self.group_code or not self.menu_item_id:
            print("   ⚠️  Skipping - Missing group_code or menu_item_id")
            return False
        
        items_data = {
            "participant_name": "Test Participant",
            "items": [
                {
                    "menu_item_id": self.menu_item_id,
                    "name": "Test Burger",
                    "price": 9.99,
                    "size": "medium",
                    "quantity": 1
                }
            ]
        }
        
        success, response = self.run_test(
            "Add Items to Group Order",
            "POST",
            f"group-orders/{self.group_code}/add-items",
            200,
            data=items_data
        )
        
        if success and response:
            print(f"   ✅ Items added to group order")
            return True
        return success
    
    def test_finalize_group_order(self):
        """Test finalizing group order"""
        if not hasattr(self, 'group_code') or not self.group_code:
            print("   ⚠️  Skipping - No group_code available")
            return False
        
        success, response = self.run_test(
            "Finalize Group Order",
            "POST",
            f"group-orders/{self.group_code}/finalize",
            200
        )
        
        if success and response:
            print(f"   ✅ Group order finalized")
            print(f"   📦 Total items: {len(response.get('items', []))}")
            return True
        return success

    def test_menu_with_uuid_location(self):
        """Test menu endpoint with UUID location ID (P0 bug fix)"""
        if not self.location_id:
            print("   ⚠️  Skipping - No location_id available")
            return False
        
        # This tests the critical fix: backend now accepts UUID-based location IDs
        success, response = self.run_test(
            "Get Menu with UUID Location ID (P0 Fix)",
            "GET",
            f"menu?location_id={self.location_id}",
            200
        )
        
        if success and response:
            if isinstance(response, list) and len(response) > 0:
                print(f"   ✅ P0 FIX VERIFIED: Menu loads with UUID location ID")
                print(f"   📋 Found {len(response)} categories")
                return True
            else:
                print(f"   ⚠️  Menu returned but no categories found")
        return success

    def test_get_products_admin(self):
        """Test getting products (admin) with master-slave info"""
        if not self.token:
            print("   ⚠️  Skipping - No auth token available")
            return False
        
        success, response = self.run_test(
            "Get Products (Admin)",
            "GET",
            "admin/products",
            200
        )
        
        if success and response:
            products = response.get('products', [])
            print(f"   🍔 Found {len(products)} products")
            if products:
                sample = products[0]
                print(f"      Sample: {sample.get('name')}")
                print(f"      Active: {sample.get('active')}")
                print(f"      In Stock: {sample.get('in_stock')}")
            return True
        return success

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 70)
        print("🧪 ZOZO Burger Backend API Test Suite - Iteration 7")
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
        
        # Admin endpoints (auth required) - Run BEFORE manager login to avoid token issues
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
        
        # POS Integration & Retry Mechanism
        print("\n📌 POS INTEGRATION & RETRY MECHANISM")
        print("-" * 70)
        self.test_get_failed_pos_orders()
        
        # Master-Slave Menu Architecture
        print("\n📌 MASTER-SLAVE MENU ARCHITECTURE")
        print("-" * 70)
        self.test_get_product_permissions()
        self.test_get_products_admin()
        
        # Modifier Groups System
        print("\n📌 MODIFIER GROUPS SYSTEM")
        print("-" * 70)
        self.test_get_modifier_groups()
        
        # Daily Deals System (NEW)
        print("\n📌 DAILY DEALS SYSTEM (NEW FEATURE)")
        print("-" * 70)
        self.test_get_today_daily_deal()
        self.test_get_all_daily_deals()
        self.test_get_admin_daily_deals()
        
        # Feature Toggles System (NEW)
        print("\n📌 FEATURE TOGGLES SYSTEM (NEW FEATURE)")
        print("-" * 70)
        self.test_get_public_features()
        self.test_get_admin_features()
        
        # Test manager login AFTER admin tests
        print("\n📌 LOCATION MANAGER AUTHENTICATION")
        print("-" * 70)
        self.test_location_manager_login()
        
        # P0 Bug Fix Verification
        print("\n📌 P0 BUG FIX VERIFICATION (MenuPage UUID Fix)")
        print("-" * 70)
        self.test_menu_with_uuid_location()
        
        # Group Orders System (CRITICAL FOR PRE-LAUNCH)
        print("\n📌 GROUP ORDERS SYSTEM (CRITICAL)")
        print("-" * 70)
        self.test_create_group_order()
        self.test_get_group_order()
        self.test_add_items_to_group_order()
        self.test_finalize_group_order()

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

"""
ZOZO Burger Admin Dashboard Backend API Tests
Tests all admin endpoints for the multi-tenant restaurant management platform
"""
import requests
import sys
from datetime import datetime

class AdminDashboardTester:
    def __init__(self, base_url="https://menu-management-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.admin_email = "admin@zonik-solutions.de"
        self.admin_password = "ZozoAdmin2024!"  # Default password from setup_admins.py

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        print(f"   URL: {method} {endpoint}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)
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
                    "actual": response.status_code,
                    "method": method
                })
                return False, {}

        except requests.exceptions.Timeout:
            print(f"   ❌ FAILED - Request timeout (15s)")
            self.failed_tests.append({"test": name, "endpoint": endpoint, "error": "Timeout"})
            return False, {}
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            self.failed_tests.append({"test": name, "endpoint": endpoint, "error": str(e)})
            return False, {}

    def test_admin_login(self):
        """Test admin login with admin@zonik-solutions.de"""
        print("\n" + "="*60)
        print("🔐 ADMIN AUTHENTICATION")
        print("="*60)
        
        # Try multiple password variations
        passwords_to_try = [
            "admin123",
            "Admin123",
            "admin",
            "password",
            "zozo123",
            "Zozo123!"
        ]
        
        for password in passwords_to_try:
            credentials = {
                "email": self.admin_email,
                "password": password
            }
            
            print(f"\n🔑 Trying password: {password}")
            success, response = self.run_test(
                f"Admin Login ({self.admin_email})",
                "POST",
                "auth/login",
                200,
                data=credentials
            )
            
            if success and response:
                self.token = response.get('access_token')
                user = response.get('user', {})
                print(f"   ✅ Logged in as: {user.get('email')} ({user.get('role')})")
                print(f"   🎫 Token: {self.token[:20]}...")
                return True
        
        print(f"\n❌ Failed to login with any password variation")
        return False

    def test_admin_dashboard(self):
        """Test admin dashboard endpoint"""
        print("\n" + "="*60)
        print("📊 ADMIN DASHBOARD")
        print("="*60)
        
        success, response = self.run_test(
            "Get Dashboard Stats",
            "GET",
            "admin/dashboard/stats",
            200
        )
        
        if success and response:
            print(f"   📈 Stats loaded: {list(response.keys())}")
        
        return success

    def test_admin_locations(self):
        """Test location management endpoints"""
        print("\n" + "="*60)
        print("📍 LOCATION MANAGEMENT")
        print("="*60)
        
        success, response = self.run_test(
            "Get Admin Locations",
            "GET",
            "admin/locations",
            200
        )
        
        if success and response:
            locations = response.get('locations', [])
            print(f"   📍 Found {len(locations)} locations")
            for loc in locations:
                print(f"      - {loc.get('name')} ({loc.get('slug')})")
        
        return success

    def test_menu_management(self):
        """Test menu management endpoints"""
        print("\n" + "="*60)
        print("🍔 MENU MANAGEMENT")
        print("="*60)
        
        success, response = self.run_test(
            "Get Admin Menu Items",
            "GET",
            "admin/menu-items",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   🍔 Found {len(response)} menu items")
            else:
                print(f"   🍔 Menu items loaded")
        
        return success

    def test_category_management(self):
        """Test category management endpoints"""
        print("\n" + "="*60)
        print("🏷️  CATEGORY MANAGEMENT")
        print("="*60)
        
        success, response = self.run_test(
            "Get Categories",
            "GET",
            "admin/categories",
            200
        )
        
        if success and response:
            categories = response.get('categories', [])
            print(f"   🏷️  Found {len(categories)} categories")
            for cat in categories:
                print(f"      - {cat.get('name')} ({cat.get('slug')})")
        
        return success

    def test_order_management(self):
        """Test order management endpoints"""
        print("\n" + "="*60)
        print("📦 ORDER MANAGEMENT")
        print("="*60)
        
        success, response = self.run_test(
            "Get Admin Orders",
            "GET",
            "admin/orders",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   📦 Found {len(response)} orders")
            else:
                print(f"   📦 Orders loaded")
        
        return success

    def test_featured_products(self):
        """Test featured products management"""
        print("\n" + "="*60)
        print("⭐ FEATURED PRODUCTS (ANGEBOTE)")
        print("="*60)
        
        success, response = self.run_test(
            "Get Featured Products",
            "GET",
            "featured-products",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   ⭐ Found {len(response)} featured products")
        
        return success

    def test_daily_deals(self):
        """Test daily deals management"""
        print("\n" + "="*60)
        print("🎯 DAILY DEALS (TAGESANGEBOTE)")
        print("="*60)
        
        success, response = self.run_test(
            "Get Admin Daily Deals",
            "GET",
            "admin/daily-deals",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   🎯 Found {len(response)} daily deals")
                for deal in response:
                    print(f"      - {deal.get('title')} (Weekday: {deal.get('weekday')})")
        
        return success

    def test_discount_codes(self):
        """Test discount codes management"""
        print("\n" + "="*60)
        print("💰 DISCOUNT CODES (RABATTCODES)")
        print("="*60)
        
        success, response = self.run_test(
            "Get Discount Codes",
            "GET",
            "admin/discount-codes",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   💰 Found {len(response)} discount codes")
                for code in response:
                    print(f"      - {code.get('code')} ({code.get('discount_type')})")
        
        return success

    def test_newsletter_management(self):
        """Test newsletter management endpoints"""
        print("\n" + "="*60)
        print("📧 NEWSLETTER & MARKETING")
        print("="*60)
        
        # Test newsletter stats
        success1, response1 = self.run_test(
            "Get Newsletter Stats",
            "GET",
            "admin/newsletter/stats",
            200
        )
        
        if success1 and response1:
            print(f"   📊 Total subscribers: {response1.get('total_subscribers', 0)}")
            print(f"   📊 Active subscribers: {response1.get('active_subscribers', 0)}")
        
        # Test subscribers list
        success2, response2 = self.run_test(
            "Get Newsletter Subscribers",
            "GET",
            "admin/newsletter/subscribers?status=active",
            200
        )
        
        if success2 and response2:
            if isinstance(response2, list):
                print(f"   📧 Found {len(response2)} active subscribers")
        
        return success1 and success2

    def test_campaign_management(self):
        """Test campaign management endpoints"""
        print("\n" + "="*60)
        print("📨 CAMPAIGN MANAGEMENT")
        print("="*60)
        
        success, response = self.run_test(
            "Get Newsletter Campaigns",
            "GET",
            "admin/newsletter/campaigns",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   📨 Found {len(response)} campaigns")
        
        return success

    def test_pos_settings(self):
        """Test POS system settings"""
        print("\n" + "="*60)
        print("🖥️  POS SYSTEM SETTINGS")
        print("="*60)
        
        # Get POS providers
        success1, response1 = self.run_test(
            "Get POS Providers",
            "GET",
            "admin/pos/providers",
            200
        )
        
        if success1 and response1:
            providers = response1.get('providers', [])
            print(f"   🖥️  Available providers: {len(providers)}")
            for provider in providers:
                print(f"      - {provider.get('name')} ({provider.get('id')})")
        
        return success1

    def test_failed_orders_queue(self):
        """Test failed POS orders queue"""
        print("\n" + "="*60)
        print("⚠️  POS FAILED ORDERS QUEUE")
        print("="*60)
        
        success, response = self.run_test(
            "Get Failed POS Orders",
            "GET",
            "admin/pos/failed-orders",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   ⚠️  Found {len(response)} failed orders")
        
        return success

    def test_feature_toggles(self):
        """Test feature toggles management"""
        print("\n" + "="*60)
        print("🎛️  FEATURE TOGGLES")
        print("="*60)
        
        success, response = self.run_test(
            "Get Admin Features",
            "GET",
            "admin/features",
            200
        )
        
        if success and response:
            if isinstance(response, dict):
                print(f"   🎛️  Found {len(response)} features")
                for key, feature in response.items():
                    status = "✅ Enabled" if feature.get('enabled') else "❌ Disabled"
                    print(f"      - {feature.get('name')}: {status}")
        
        return success

    def test_security_dashboard(self):
        """Test security dashboard endpoints"""
        print("\n" + "="*60)
        print("🔒 SECURITY DASHBOARD")
        print("="*60)
        
        # Test security summary
        success1, response1 = self.run_test(
            "Get Security Summary",
            "GET",
            "admin/security/summary?hours=24",
            200
        )
        
        if success1 and response1:
            print(f"   🔒 Failed logins (24h): {response1.get('failed_logins', 0)}")
            print(f"   🔒 Rate limit events: {response1.get('rate_limit_events', 0)}")
        
        # Test audit logs
        success2, response2 = self.run_test(
            "Get Audit Logs",
            "GET",
            "admin/security/audit-logs?limit=10",
            200
        )
        
        if success2 and response2:
            logs = response2.get('logs', [])
            print(f"   📋 Found {len(logs)} audit log entries")
        
        return success1 and success2

    def test_location_settings(self):
        """Test location settings (PLZ/Delivery area management)"""
        print("\n" + "="*60)
        print("⚙️  LOCATION SETTINGS (PLZ/DELIVERY)")
        print("="*60)
        
        success, response = self.run_test(
            "Get Location Settings",
            "GET",
            "admin/location-settings",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   ⚙️  Found {len(response)} location settings")
        
        return success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {len(self.failed_tests)} ❌")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"   - {test.get('test')}")
                print(f"     Endpoint: {test.get('method', 'GET')} {test.get('endpoint')}")
                print(f"     Expected: {test.get('expected')}, Got: {test.get('actual')}")
                if test.get('error'):
                    print(f"     Error: {test.get('error')}")
        
        return len(self.failed_tests) == 0

def main():
    print("="*60)
    print("🍔 ZOZO BURGER ADMIN DASHBOARD API TESTS")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = AdminDashboardTester()
    
    # Run all tests
    if not tester.test_admin_login():
        print("\n❌ Admin login failed - cannot proceed with other tests")
        return 1
    
    # Test all admin pages
    tester.test_admin_dashboard()
    tester.test_admin_locations()
    tester.test_menu_management()
    tester.test_category_management()
    tester.test_order_management()
    tester.test_featured_products()
    tester.test_daily_deals()
    tester.test_discount_codes()
    tester.test_newsletter_management()
    tester.test_campaign_management()
    tester.test_pos_settings()
    tester.test_failed_orders_queue()
    tester.test_feature_toggles()
    tester.test_security_dashboard()
    tester.test_location_settings()
    
    # Print summary
    all_passed = tester.print_summary()
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

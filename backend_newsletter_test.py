"""
ZOZO Burger Newsletter & Order Management Backend Tests
Tests all newsletter, campaign, and order management endpoints
"""
import requests
import sys
from datetime import datetime, timedelta

class NewsletterOrderManagementTester:
    def __init__(self, base_url="https://site-refresh-58.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.subscriber_id = None
        self.campaign_id = None
        self.order_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, use_admin_auth=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if use_admin_auth and self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'

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
                    print(f"   Response: {response.text[:300]}")
                
                self.failed_tests.append({
                    "test": name,
                    "endpoint": endpoint,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200] if hasattr(response, 'text') else ''
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

    def test_admin_login(self):
        """Test admin login"""
        print("\n" + "="*60)
        print("ADMIN AUTHENTICATION")
        print("="*60)
        
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "admin/auth/login",
            200,
            data={
                "email": "test@zozo-testing.de",
                "password": "TestAdmin123!"
            }
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"   ✅ Admin token obtained")
            return True
        else:
            print(f"   ❌ Failed to get admin token")
            return False

    # ==================== NEWSLETTER TESTS ====================
    
    def test_newsletter_subscribe(self):
        """Test public newsletter subscription"""
        print("\n" + "="*60)
        print("NEWSLETTER SUBSCRIPTION TESTS")
        print("="*60)
        
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@zozo-test.de"
        
        success, response = self.run_test(
            "Newsletter Subscribe (Public)",
            "POST",
            "newsletter/subscribe",
            200,
            data={
                "email": test_email,
                "name": "Test User",
                "source": "checkout"
            }
        )
        
        if success and response.get('success'):
            self.subscriber_id = response.get('subscriber_id')
            print(f"   ✅ Subscriber ID: {self.subscriber_id}")
        
        return success
    
    def test_newsletter_subscribe_duplicate(self):
        """Test subscribing with same email (should handle gracefully)"""
        test_email = f"duplicate_{datetime.now().strftime('%H%M%S')}@zozo-test.de"
        
        # First subscription
        self.run_test(
            "Newsletter Subscribe - First Time",
            "POST",
            "newsletter/subscribe",
            200,
            data={"email": test_email, "source": "footer"}
        )
        
        # Duplicate subscription
        success, response = self.run_test(
            "Newsletter Subscribe - Duplicate",
            "POST",
            "newsletter/subscribe",
            200,
            data={"email": test_email, "source": "footer"}
        )
        
        return success
    
    def test_newsletter_unsubscribe(self):
        """Test newsletter unsubscribe"""
        test_email = f"unsub_{datetime.now().strftime('%H%M%S')}@zozo-test.de"
        
        # Subscribe first
        self.run_test(
            "Newsletter Subscribe for Unsubscribe Test",
            "POST",
            "newsletter/subscribe",
            200,
            data={"email": test_email}
        )
        
        # Unsubscribe
        success, response = self.run_test(
            "Newsletter Unsubscribe",
            "POST",
            "newsletter/unsubscribe",
            200,
            data={"email": test_email}
        )
        
        return success
    
    def test_admin_newsletter_stats(self):
        """Test admin newsletter statistics"""
        print("\n" + "="*60)
        print("ADMIN NEWSLETTER STATS TESTS")
        print("="*60)
        
        success, response = self.run_test(
            "Admin Newsletter Stats",
            "GET",
            "admin/newsletter/stats",
            200,
            use_admin_auth=True
        )
        
        if success:
            print(f"   📊 Total Subscribers: {response.get('total_subscribers', 0)}")
            print(f"   📊 Active: {response.get('active_subscribers', 0)}")
            print(f"   📊 New This Week: {response.get('new_this_week', 0)}")
        
        return success
    
    def test_admin_newsletter_subscribers(self):
        """Test getting subscriber list"""
        success, response = self.run_test(
            "Admin Newsletter Subscribers List",
            "GET",
            "admin/newsletter/subscribers",
            200,
            use_admin_auth=True
        )
        
        if success:
            subscriber_count = len(response) if isinstance(response, list) else 0
            print(f"   📋 Retrieved {subscriber_count} subscribers")
        
        return success
    
    def test_admin_newsletter_segments(self):
        """Test getting segments"""
        success, response = self.run_test(
            "Admin Newsletter Segments",
            "GET",
            "admin/newsletter/segments",
            200,
            use_admin_auth=True
        )
        
        if success and 'segments' in response:
            print(f"   📊 Segments: {response['segments']}")
        
        return success
    
    # ==================== CAMPAIGN TESTS ====================
    
    def test_create_campaign(self):
        """Test creating email campaign"""
        print("\n" + "="*60)
        print("CAMPAIGN MANAGEMENT TESTS")
        print("="*60)
        
        success, response = self.run_test(
            "Create Campaign",
            "POST",
            "admin/newsletter/campaigns",
            200,
            data={
                "title": f"Test Campaign {datetime.now().strftime('%H:%M:%S')}",
                "subject": "🍔 Neue Angebote bei ZOZO Burger!",
                "html_content": "<h1>Hallo!</h1><p>Probieren Sie unsere neuen Burger!</p>",
                "segment": None  # Send to all
            },
            use_admin_auth=True
        )
        
        if success and response.get('success'):
            self.campaign_id = response.get('campaign_id')
            print(f"   ✅ Campaign ID: {self.campaign_id}")
        
        return success
    
    def test_get_campaigns(self):
        """Test getting all campaigns"""
        success, response = self.run_test(
            "Get All Campaigns",
            "GET",
            "admin/newsletter/campaigns",
            200,
            use_admin_auth=True
        )
        
        if success:
            campaign_count = len(response) if isinstance(response, list) else 0
            print(f"   📋 Retrieved {campaign_count} campaigns")
        
        return success
    
    def test_get_single_campaign(self):
        """Test getting single campaign details"""
        if not self.campaign_id:
            print("   ⚠️  Skipped - No campaign ID available")
            return True
        
        success, response = self.run_test(
            "Get Single Campaign",
            "GET",
            f"admin/newsletter/campaigns/{self.campaign_id}",
            200,
            use_admin_auth=True
        )
        
        return success
    
    def test_send_campaign(self):
        """Test sending campaign"""
        if not self.campaign_id:
            print("   ⚠️  Skipped - No campaign ID available")
            return True
        
        success, response = self.run_test(
            "Send Campaign",
            "POST",
            f"admin/newsletter/campaigns/{self.campaign_id}/send",
            200,
            use_admin_auth=True
        )
        
        if success:
            print(f"   📧 Recipients: {response.get('recipients', 0)}")
        
        return success
    
    # ==================== DISCOUNT CODE TESTS ====================
    
    def test_create_discount_code(self):
        """Test creating discount code (auth fix test)"""
        print("\n" + "="*60)
        print("DISCOUNT CODE TESTS (AUTH FIX)")
        print("="*60)
        
        success, response = self.run_test(
            "Create Discount Code",
            "POST",
            "admin/discount-codes",
            200,
            data={
                "code": "ZOZODEAL2025",
                "description": "Test discount code",
                "discount_type": "percentage",
                "discount_value": 10.0,
                "min_order_value": 20.0,
                "order_type": "all",
                "max_uses": 100,
                "valid_from": datetime.now().isoformat(),
                "valid_until": (datetime.now() + timedelta(days=30)).isoformat(),
                "location_ids": [],
                "active": True
            },
            use_admin_auth=True
        )
        
        return success
    
    def test_get_discount_codes(self):
        """Test getting discount codes"""
        success, response = self.run_test(
            "Get Discount Codes",
            "GET",
            "admin/discount-codes",
            200,
            use_admin_auth=True
        )
        
        if success:
            code_count = len(response) if isinstance(response, list) else 0
            print(f"   📋 Retrieved {code_count} discount codes")
        
        return success
    
    # ==================== LOCATION SETTINGS TESTS ====================
    
    def test_get_location_settings(self):
        """Test getting location settings (auth fix test)"""
        print("\n" + "="*60)
        print("LOCATION SETTINGS TESTS (AUTH FIX)")
        print("="*60)
        
        success, response = self.run_test(
            "Get Location Settings",
            "GET",
            "admin/location-settings",
            200,
            use_admin_auth=True
        )
        
        if success:
            location_count = len(response) if isinstance(response, list) else 0
            print(f"   📋 Retrieved {location_count} locations")
        
        return success
    
    # ==================== ORDER MANAGEMENT TESTS ====================
    
    def test_order_management_features(self):
        """Test order management endpoints (ObjectId fix test)"""
        print("\n" + "="*60)
        print("ORDER MANAGEMENT TESTS (ObjectId FIX)")
        print("="*60)
        
        # First, get an order to test with
        success, response = self.run_test(
            "Get Orders for Testing",
            "GET",
            "admin/orders?limit=1",
            200,
            use_admin_auth=True
        )
        
        if success and isinstance(response, list) and len(response) > 0:
            test_order = response[0]
            order_id = test_order.get('id') or test_order.get('_id')
            
            if order_id:
                print(f"   📦 Testing with Order ID: {order_id}")
                
                # Test order details
                self.run_test(
                    "Get Order Details",
                    "GET",
                    f"admin/orders/{order_id}/details",
                    200,
                    use_admin_auth=True
                )
                
                # Test error log
                self.run_test(
                    "Get Order Error Log",
                    "GET",
                    f"admin/orders/{order_id}/error-log",
                    200,
                    use_admin_auth=True
                )
                
                return True
            else:
                print("   ⚠️  No order ID found in response")
                return True
        else:
            print("   ⚠️  No orders available for testing")
            return True

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"\n{i}. {test['test']}")
                print(f"   Endpoint: {test['endpoint']}")
                if 'expected' in test:
                    print(f"   Expected: {test['expected']}, Got: {test['actual']}")
                if 'error' in test:
                    print(f"   Error: {test['error']}")
                if 'response' in test:
                    print(f"   Response: {test['response']}")
        
        return len(self.failed_tests) == 0

def main():
    print("="*60)
    print("ZOZO BURGER - NEWSLETTER & ORDER MANAGEMENT TESTS")
    print("Testing Iteration 11 Bug Fixes")
    print("="*60)
    
    tester = NewsletterOrderManagementTester()
    
    # Admin login first
    if not tester.test_admin_login():
        print("\n❌ Admin login failed - cannot continue with admin tests")
        return 1
    
    # Newsletter Tests
    tester.test_newsletter_subscribe()
    tester.test_newsletter_subscribe_duplicate()
    tester.test_newsletter_unsubscribe()
    tester.test_admin_newsletter_stats()
    tester.test_admin_newsletter_subscribers()
    tester.test_admin_newsletter_segments()
    
    # Campaign Tests
    tester.test_create_campaign()
    tester.test_get_campaigns()
    tester.test_get_single_campaign()
    tester.test_send_campaign()
    
    # Discount Code Tests (Auth Fix)
    tester.test_create_discount_code()
    tester.test_get_discount_codes()
    
    # Location Settings Tests (Auth Fix)
    tester.test_get_location_settings()
    
    # Order Management Tests (ObjectId Fix)
    tester.test_order_management_features()
    
    # Print summary
    all_passed = tester.print_summary()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
ZOZO Burger Admin Dashboard - Backend API Regression Test
Tests the 5 bug fixes applied by main agent
"""

import requests
import sys
from datetime import datetime

class AdminAPITester:
    def __init__(self, base_url="https://menu-management-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_email = "admin@zonik-solutions.de"
        self.admin_password = "ZozoAdmin2024!"

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        print(f"   Endpoint: {method} {endpoint}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"   ✅ PASSED - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        # Print first few keys for debugging
                        keys = list(response_data.keys())[:5]
                        print(f"   Response keys: {keys}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                except:
                    pass
            else:
                print(f"   ❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text[:200]}")

            return success, response.json() if response.status_code < 500 else {}

        except requests.exceptions.Timeout:
            print(f"   ❌ FAILED - Request timeout")
            return False, {}
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login and get token"""
        print("\n" + "="*60)
        print("REGRESSION TEST 1: Admin Login")
        print("="*60)
        
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "/api/admin/auth/login",
            200,
            data={"email": self.admin_email, "password": self.admin_password}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"\n✅ Admin login successful! Token obtained.")
            return True
        else:
            print(f"\n❌ Admin login failed! Cannot proceed with other tests.")
            return False

    def test_admin_stats(self):
        """Test GET /api/admin/stats - Bug fix verification"""
        print("\n" + "="*60)
        print("REGRESSION TEST 2: Admin Stats Endpoint")
        print("Previous bug: /api/admin/dashboard/stats returned 404")
        print("Fix: Correct endpoint is /api/admin/stats")
        print("="*60)
        
        success, response = self.run_test(
            "Admin Dashboard Stats",
            "GET",
            "/api/admin/stats",
            200
        )
        
        if success:
            print(f"\n✅ Admin stats endpoint working correctly!")
            return True
        else:
            print(f"\n❌ Admin stats endpoint failed!")
            return False

    def test_campaign_management_endpoints(self):
        """Test Campaign Management endpoints - Bug fix verification"""
        print("\n" + "="*60)
        print("REGRESSION TEST 3: Campaign Management")
        print("Previous bug: ReferenceError: activeTab is not defined")
        print("Fix: Added useState for activeTab and segments")
        print("="*60)
        
        # Test newsletter campaigns endpoint
        success1, response1 = self.run_test(
            "Get Newsletter Campaigns",
            "GET",
            "/api/admin/newsletter/campaigns",
            200
        )
        
        # Test newsletter stats endpoint
        success2, response2 = self.run_test(
            "Get Newsletter Stats",
            "GET",
            "/api/admin/newsletter/stats",
            200
        )
        
        # Test newsletter segments endpoint
        success3, response3 = self.run_test(
            "Get Newsletter Segments",
            "GET",
            "/api/admin/newsletter/segments",
            200
        )
        
        if success1 and success2 and success3:
            print(f"\n✅ Campaign Management endpoints working correctly!")
            return True
        else:
            print(f"\n❌ Some Campaign Management endpoints failed!")
            return False

    def test_order_management_endpoint(self):
        """Test Order Management endpoint - Bug fix verification"""
        print("\n" + "="*60)
        print("REGRESSION TEST 4: Order Management")
        print("Previous bug: 401 Unauthorized (localStorage vs sessionStorage)")
        print("Fix: Changed to sessionStorage.getItem('adminToken')")
        print("="*60)
        
        success, response = self.run_test(
            "Get Admin Orders",
            "GET",
            "/api/admin/orders",
            200
        )
        
        if success:
            print(f"\n✅ Order Management endpoint working correctly!")
            return True
        else:
            print(f"\n❌ Order Management endpoint failed!")
            return False

    def test_newsletter_management_endpoints(self):
        """Test Newsletter Management endpoints - Bug fix verification"""
        print("\n" + "="*60)
        print("REGRESSION TEST 5: Newsletter Management")
        print("Previous bug: 401 Unauthorized (localStorage.getItem('zozoAuthToken'))")
        print("Fix: Changed to sessionStorage.getItem('adminToken')")
        print("="*60)
        
        # Test newsletter stats
        success1, response1 = self.run_test(
            "Get Newsletter Stats",
            "GET",
            "/api/admin/newsletter/stats",
            200
        )
        
        # Test newsletter subscribers
        success2, response2 = self.run_test(
            "Get Newsletter Subscribers",
            "GET",
            "/api/admin/newsletter/subscribers?status=active",
            200
        )
        
        if success1 and success2:
            print(f"\n✅ Newsletter Management endpoints working correctly!")
            return True
        else:
            print(f"\n❌ Some Newsletter Management endpoints failed!")
            return False

    def test_featured_products_endpoint(self):
        """Test Featured Products endpoint - Bug fix verification"""
        print("\n" + "="*60)
        print("REGRESSION TEST 6: Featured Products")
        print("Previous bug: 401 Unauthorized (localStorage)")
        print("Fix: Changed to sessionStorage.getItem('adminToken')")
        print("="*60)
        
        success, response = self.run_test(
            "Get Admin Menu Items",
            "GET",
            "/api/admin/menu-items",
            200
        )
        
        if success:
            print(f"\n✅ Featured Products endpoint working correctly!")
            return True
        else:
            print(f"\n❌ Featured Products endpoint failed!")
            return False

    def test_location_settings_endpoint(self):
        """Test Location Settings endpoint - Bug fix verification"""
        print("\n" + "="*60)
        print("REGRESSION TEST 7: Location Settings V2")
        print("Previous bug: 401 Unauthorized (localStorage.getItem('zozoAuthToken'))")
        print("Fix: Changed to sessionStorage.getItem('adminToken')")
        print("="*60)
        
        success, response = self.run_test(
            "Get Location Settings",
            "GET",
            "/api/admin/location-settings",
            200
        )
        
        if success:
            print(f"\n✅ Location Settings endpoint working correctly!")
            return True
        else:
            print(f"\n❌ Location Settings endpoint failed!")
            return False

def main():
    print("\n" + "="*60)
    print("ZOZO BURGER ADMIN DASHBOARD - REGRESSION TEST")
    print("Testing 5 Bug Fixes Applied by Main Agent")
    print("="*60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = AdminAPITester()
    
    # Test 1: Admin Login (prerequisite)
    if not tester.test_admin_login():
        print("\n❌ CRITICAL: Admin login failed. Cannot proceed with regression tests.")
        return 1
    
    # Test 2: Admin Stats Endpoint
    tester.test_admin_stats()
    
    # Test 3: Campaign Management (activeTab bug fix)
    tester.test_campaign_management_endpoints()
    
    # Test 4: Order Management (401 bug fix)
    tester.test_order_management_endpoint()
    
    # Test 5: Newsletter Management (401 bug fix)
    tester.test_newsletter_management_endpoints()
    
    # Test 6: Featured Products (401 bug fix)
    tester.test_featured_products_endpoint()
    
    # Test 7: Location Settings (401 bug fix)
    tester.test_location_settings_endpoint()
    
    # Print final results
    print("\n" + "="*60)
    print("REGRESSION TEST RESULTS")
    print("="*60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    print("="*60)
    
    if tester.tests_passed == tester.tests_run:
        print("\n✅ ALL REGRESSION TESTS PASSED!")
        print("All 5 bug fixes are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {tester.tests_run - tester.tests_passed} test(s) failed.")
        print("Some bug fixes may need additional work.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

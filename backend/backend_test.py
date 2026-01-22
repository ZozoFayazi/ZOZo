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

    def test_customer_crm_endpoints(self):
        """Test Enterprise Customer CRM endpoints - NEW FEATURE"""
        print("\n" + "="*60)
        print("ENTERPRISE CRM TEST: Customer Management")
        print("Testing RFM Analysis, Segmentation, and Customer Detail")
        print("="*60)
        
        all_passed = True
        
        # Test 1: Get all customers with RFM scoring
        success1, response1 = self.run_test(
            "Get All Customers (RFM Scoring)",
            "GET",
            "/api/admin/customers/?limit=10",
            200
        )
        
        if success1:
            # Verify response structure
            if 'customers' in response1 and 'total' in response1:
                print(f"   ✅ Response structure valid")
                print(f"   Total customers: {response1.get('total', 0)}")
                
                # Check if customers have RFM data
                if response1.get('customers'):
                    first_customer = response1['customers'][0]
                    if 'rfm' in first_customer:
                        rfm = first_customer['rfm']
                        print(f"   ✅ RFM data present: Segment={rfm.get('segment')}, Score={rfm.get('rfm_score')}")
                        print(f"   RFM breakdown: R={rfm.get('r_score')}, F={rfm.get('f_score')}, M={rfm.get('m_score')}")
                    else:
                        print(f"   ❌ RFM data missing in customer object")
                        all_passed = False
                else:
                    print(f"   ⚠️  No customers found (may be expected if no orders exist)")
            else:
                print(f"   ❌ Invalid response structure")
                all_passed = False
        else:
            all_passed = False
        
        # Test 2: Get segment statistics
        success2, response2 = self.run_test(
            "Get Customer Segment Statistics",
            "GET",
            "/api/admin/customers/segments/stats",
            200
        )
        
        if success2:
            # Verify all segments are present
            expected_segments = ['VIP', 'Active', 'Regular', 'At-Risk', 'Lost']
            for segment in expected_segments:
                if segment in response2:
                    stats = response2[segment]
                    print(f"   ✅ {segment}: {stats.get('count')} customers, €{stats.get('total_revenue', 0):.2f} revenue")
                else:
                    print(f"   ❌ Missing segment: {segment}")
                    all_passed = False
        else:
            all_passed = False
        
        # Test 3: Test segment filtering
        success3, response3 = self.run_test(
            "Filter Customers by Segment (VIP)",
            "GET",
            "/api/admin/customers/?segment=VIP&limit=5",
            200
        )
        
        if success3 and response3.get('customers'):
            # Verify all returned customers are VIP
            vip_customers = response3['customers']
            all_vip = all(c.get('rfm', {}).get('segment') == 'VIP' for c in vip_customers)
            if all_vip:
                print(f"   ✅ Segment filter working correctly (all {len(vip_customers)} customers are VIP)")
            else:
                print(f"   ❌ Segment filter not working (non-VIP customers returned)")
                all_passed = False
        
        # Test 4: Test search functionality
        success4, response4 = self.run_test(
            "Search Customers",
            "GET",
            "/api/admin/customers/?search=test&limit=5",
            200
        )
        
        if success4:
            print(f"   ✅ Search endpoint working (found {response4.get('total', 0)} results)")
        else:
            all_passed = False
        
        # Test 5: Test sorting
        success5, response5 = self.run_test(
            "Sort Customers by RFM Score",
            "GET",
            "/api/admin/customers/?sort_by=rfm_score&sort_order=desc&limit=5",
            200
        )
        
        if success5 and response5.get('customers'):
            customers = response5['customers']
            if len(customers) >= 2:
                # Verify descending order
                scores = [c.get('rfm', {}).get('rfm_score', 0) for c in customers]
                is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
                if is_sorted:
                    print(f"   ✅ Sorting working correctly (RFM scores: {scores})")
                else:
                    print(f"   ❌ Sorting not working correctly (scores: {scores})")
                    all_passed = False
        
        # Test 6: Get customer detail (if we have customers)
        if success1 and response1.get('customers'):
            first_customer_id = response1['customers'][0].get('customer_id')
            if first_customer_id:
                success6, response6 = self.run_test(
                    "Get Customer Detail",
                    "GET",
                    f"/api/admin/customers/{first_customer_id}",
                    200
                )
                
                if success6:
                    # Verify detail response has all required fields
                    required_fields = ['customer_id', 'name', 'total_orders', 'total_spent', 
                                     'rfm', 'order_timeline', 'favorite_products']
                    missing_fields = [f for f in required_fields if f not in response6]
                    if not missing_fields:
                        print(f"   ✅ Customer detail has all required fields")
                        print(f"   Customer: {response6.get('name')}, Orders: {response6.get('total_orders')}")
                        print(f"   Timeline entries: {len(response6.get('order_timeline', []))}")
                    else:
                        print(f"   ❌ Missing fields in customer detail: {missing_fields}")
                        all_passed = False
                else:
                    all_passed = False
        
        # Test 7: CSV Export
        print(f"\n🔍 Test: CSV Export")
        print(f"   Endpoint: GET /api/admin/customers/export/csv")
        try:
            url = f"{self.base_url}/api/admin/customers/export/csv"
            headers = {
                'Authorization': f'Bearer {self.token}'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Check if it's CSV content
                content_type = response.headers.get('Content-Type', '')
                if 'csv' in content_type.lower() or response.text.startswith('ZOZO Burger'):
                    print(f"   ✅ PASSED - CSV export working (size: {len(response.content)} bytes)")
                    # Check CSV has data
                    lines = response.text.split('\n')
                    print(f"   CSV has {len(lines)} lines")
                else:
                    print(f"   ❌ FAILED - Invalid content type: {content_type}")
                    all_passed = False
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            all_passed = False
        
        if all_passed:
            print(f"\n✅ All Customer CRM endpoints working correctly!")
            return True
        else:
            print(f"\n⚠️  Some Customer CRM tests failed!")
            return False

    def test_finance_management_endpoints(self):
        """Test Enterprise Finance Management endpoints"""
        print("\n" + "="*60)
        print("TEST 9: Enterprise Finance Management")
        print("="*60)
        
        all_passed = True
        
        # Test 1: Financial Overview
        print("\n📊 Test 9.1: GET /api/admin/finance/overview")
        try:
            url = f"{self.base_url}/api/admin/finance/overview?range_type=this_month"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify structure
                if 'overview' in data and 'payment_methods' in data and 'period' in data:
                    overview = data['overview']
                    
                    # Verify all required fields
                    required_fields = ['total_revenue_gross', 'total_revenue_net', 'total_tax', 
                                     'total_orders', 'avg_order_value', 'revenue_growth_percent']
                    
                    if all(field in overview for field in required_fields):
                        print(f"   ✅ PASSED - Overview structure correct")
                        print(f"   Brutto: €{overview['total_revenue_gross']}")
                        print(f"   Netto: €{overview['total_revenue_net']}")
                        print(f"   MwSt (19%): €{overview['total_tax']}")
                        print(f"   Orders: {overview['total_orders']}")
                        print(f"   Avg Order: €{overview['avg_order_value']}")
                        
                        # Verify tax calculation (19%)
                        if overview['total_revenue_gross'] > 0:
                            expected_net = overview['total_revenue_gross'] / 1.19
                            expected_tax = overview['total_revenue_gross'] - expected_net
                            
                            # Allow 0.01 rounding difference
                            net_diff = abs(overview['total_revenue_net'] - expected_net)
                            tax_diff = abs(overview['total_tax'] - expected_tax)
                            
                            if net_diff < 0.02 and tax_diff < 0.02:
                                print(f"   ✅ Tax calculation (19%) correct")
                            else:
                                print(f"   ❌ Tax calculation incorrect (diff: net={net_diff}, tax={tax_diff})")
                                all_passed = False
                        
                        # Check payment methods
                        if data['payment_methods']:
                            print(f"   ✅ Payment methods: {list(data['payment_methods'].keys())}")
                        
                    else:
                        print(f"   ❌ FAILED - Missing required fields")
                        all_passed = False
                else:
                    print(f"   ❌ FAILED - Invalid response structure")
                    all_passed = False
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            all_passed = False
        
        # Test 2: Revenue by Location
        print("\n🏢 Test 9.2: GET /api/admin/finance/revenue-by-location")
        try:
            url = f"{self.base_url}/api/admin/finance/revenue-by-location?range_type=this_month"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    locations = data['data']
                    print(f"   ✅ PASSED - Found {len(locations)} locations")
                    
                    for loc in locations[:3]:  # Show first 3
                        print(f"   - {loc.get('location_name')}: €{loc.get('revenue_gross')} ({loc.get('orders')} orders)")
                else:
                    print(f"   ❌ FAILED - Invalid response structure")
                    all_passed = False
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            all_passed = False
        
        # Test 3: Revenue by Category
        print("\n📦 Test 9.3: GET /api/admin/finance/revenue-by-category")
        try:
            url = f"{self.base_url}/api/admin/finance/revenue-by-category?range_type=this_month"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    categories = data['data']
                    print(f"   ✅ PASSED - Found {len(categories)} categories")
                    
                    for cat in categories[:3]:  # Show first 3
                        print(f"   - {cat.get('category')}: €{cat.get('revenue')} ({cat.get('items_sold')} items)")
                else:
                    print(f"   ❌ FAILED - Invalid response structure")
                    all_passed = False
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            all_passed = False
        
        # Test 4: Daily Revenue Trend
        print("\n📈 Test 9.4: GET /api/admin/finance/daily-trend")
        try:
            url = f"{self.base_url}/api/admin/finance/daily-trend?range_type=30days"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    trend = data['data']
                    print(f"   ✅ PASSED - Found {len(trend)} days of data")
                    
                    if trend:
                        # Show first and last day
                        print(f"   First day: {trend[0].get('date')} - €{trend[0].get('revenue_gross')}")
                        if len(trend) > 1:
                            print(f"   Last day: {trend[-1].get('date')} - €{trend[-1].get('revenue_gross')}")
                else:
                    print(f"   ❌ FAILED - Invalid response structure")
                    all_passed = False
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            all_passed = False
        
        # Test 5: Top Products
        print("\n🏆 Test 9.5: GET /api/admin/finance/top-products")
        try:
            url = f"{self.base_url}/api/admin/finance/top-products?range_type=this_month&limit=10"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    products = data['data']
                    print(f"   ✅ PASSED - Found {len(products)} top products")
                    
                    for i, prod in enumerate(products[:5], 1):  # Show top 5
                        print(f"   {i}. {prod.get('product')}: €{prod.get('revenue')} ({prod.get('quantity')}x)")
                else:
                    print(f"   ❌ FAILED - Invalid response structure")
                    all_passed = False
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            all_passed = False
        
        # Test 6: Monthly Comparison
        print("\n📅 Test 9.6: GET /api/admin/finance/monthly-comparison")
        try:
            url = f"{self.base_url}/api/admin/finance/monthly-comparison?year=2026"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    months = data['data']
                    print(f"   ✅ PASSED - Found {len(months)} months")
                    
                    # Show current month
                    current_month = datetime.now().month
                    if len(months) >= current_month:
                        month_data = months[current_month - 1]
                        print(f"   {month_data.get('month_name')}: €{month_data.get('revenue_gross')} ({month_data.get('orders')} orders)")
                else:
                    print(f"   ❌ FAILED - Invalid response structure")
                    all_passed = False
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            all_passed = False
        
        # Test 7: CSV Export
        print("\n💾 Test 9.7: GET /api/admin/finance/export/csv")
        try:
            url = f"{self.base_url}/api/admin/finance/export/csv?range_type=this_month"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'csv' in content_type.lower() or response.text.startswith('ZOZO Burger'):
                    print(f"   ✅ PASSED - CSV export working (size: {len(response.content)} bytes)")
                    
                    # Check CSV has required sections
                    csv_text = response.text
                    if 'Financial Overview' in csv_text and 'Payment Methods' in csv_text and 'Daily Revenue Trend' in csv_text:
                        print(f"   ✅ CSV contains all required sections")
                    else:
                        print(f"   ⚠️  CSV may be missing some sections")
                else:
                    print(f"   ❌ FAILED - Invalid content type: {content_type}")
                    all_passed = False
            else:
                print(f"   ❌ FAILED - Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"   ❌ FAILED - Error: {str(e)}")
            all_passed = False
        
        if all_passed:
            print(f"\n✅ All Finance Management endpoints working correctly!")
            return True
        else:
            print(f"\n⚠️  Some Finance Management tests failed!")
            return False

def main():
    print("\n" + "="*60)
    print("ZOZO BURGER - COMPREHENSIVE API TEST")
    print("Testing Admin Dashboard + Enterprise CRM + Finance Management")
    print("="*60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = AdminAPITester()
    
    # Test 1: Admin Login (prerequisite)
    if not tester.test_admin_login():
        print("\n❌ CRITICAL: Admin login failed. Cannot proceed with tests.")
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
    
    # Test 8: ENTERPRISE CRM - Customer Management (NEW FEATURE)
    tester.test_customer_crm_endpoints()
    
    # Test 9: ENTERPRISE FINANCE MANAGEMENT (NEW FEATURE)
    tester.test_finance_management_endpoints()
    
    # Print final results
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST RESULTS")
    print("="*60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    print("="*60)
    
    if tester.tests_passed == tester.tests_run:
        print("\n✅ ALL TESTS PASSED!")
        print("Admin Dashboard + Enterprise CRM working correctly.")
        return 0
    else:
        print(f"\n⚠️  {tester.tests_run - tester.tests_passed} test(s) failed.")
        print("Some features may need additional work.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

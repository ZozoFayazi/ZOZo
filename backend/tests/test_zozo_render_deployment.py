"""
ZOZO Burger Render Deployment Tests
Tests the live Render deployment APIs: https://zozo-lcx8.onrender.com
"""

import pytest
import requests
import os
from datetime import datetime

# Use the Render production URL
BASE_URL = "https://zozo-lcx8.onrender.com"

class TestHealthAndLocations:
    """Health check and locations API tests"""
    
    def test_health_endpoint(self):
        """Test API health check"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"Health check passed: {data}")
    
    def test_get_locations(self):
        """Test locations endpoint returns both locations"""
        response = requests.get(f"{BASE_URL}/api/locations", timeout=30)
        assert response.status_code == 200
        locations = response.json()
        assert len(locations) >= 2, "Should have at least 2 locations"
        
        # Verify location data
        location_names = [loc["name"] for loc in locations]
        assert any("Rellingen" in name for name in location_names), "Rellingen should exist"
        assert any("Henstedt" in name for name in location_names), "Henstedt-Ulzburg should exist"
        print(f"Found {len(locations)} locations: {location_names}")
    
    def test_rellingen_location_details(self):
        """Test Rellingen location has correct details"""
        response = requests.get(f"{BASE_URL}/api/locations", timeout=30)
        locations = response.json()
        
        rellingen = next((loc for loc in locations if "Rellingen" in loc["name"]), None)
        assert rellingen is not None, "Rellingen location not found"
        assert rellingen["id"] == "49aff347-a6c3-407c-ad4a-59d5d0852314"
        assert "delivery_zone" in rellingen
        assert rellingen["active"] is True


class TestMenuAPI:
    """Menu endpoint tests"""
    
    RELLINGEN_ID = "49aff347-a6c3-407c-ad4a-59d5d0852314"
    HENSTEDT_ID = "422cac42-cfdf-4869-b2cb-0b09aa24d02c"
    
    def test_menu_with_location(self):
        """Test menu endpoint with valid location"""
        response = requests.get(f"{BASE_URL}/api/menu?location_id={self.RELLINGEN_ID}", timeout=30)
        assert response.status_code == 200
        menu = response.json()
        assert len(menu) > 0, "Menu should have categories"
        
        # Check for expected categories
        category_names = [cat["name"] for cat in menu]
        print(f"Menu categories: {category_names}")
        assert "Burger" in category_names, "Should have Burger category"
    
    def test_menu_burger_items(self):
        """Test menu has burger items with correct structure"""
        response = requests.get(f"{BASE_URL}/api/menu?location_id={self.RELLINGEN_ID}", timeout=30)
        menu = response.json()
        
        burger_category = next((cat for cat in menu if cat["name"] == "Burger"), None)
        assert burger_category is not None, "Burger category not found"
        assert "items" in burger_category
        assert len(burger_category["items"]) > 0, "Should have burger items"
        
        # Check first burger has required fields
        burger = burger_category["items"][0]
        assert "name" in burger
        assert "price_medium" in burger or "price_normal" in burger
        print(f"First burger: {burger['name']}")


class TestDailyDeals:
    """Daily deals endpoint tests"""
    
    def test_today_daily_deal(self):
        """Test today's daily deal endpoint"""
        response = requests.get(f"{BASE_URL}/api/daily-deal", timeout=30)
        assert response.status_code == 200
        deal = response.json()
        
        # Today is Monday (weekday=0)
        if "weekday" in deal:
            print(f"Today's deal: {deal.get('title', 'N/A')}")
            assert "title" in deal or "message" in deal
    
    def test_all_daily_deals(self):
        """Test all daily deals endpoint"""
        response = requests.get(f"{BASE_URL}/api/daily-deals", timeout=30)
        assert response.status_code == 200
        deals = response.json()
        
        assert len(deals) >= 1, "Should have at least 1 daily deal configured"
        
        # Check Monday deal (Pasta Montag)
        monday_deal = next((d for d in deals if d.get("weekday") == 0), None)
        if monday_deal:
            assert "Pasta" in monday_deal.get("title", ""), "Monday should be Pasta deal"
            print(f"Monday deal: {monday_deal.get('title')} - {monday_deal.get('description')}")


class TestDiscountCodes:
    """Discount code validation tests"""
    
    RELLINGEN_ID = "49aff347-a6c3-407c-ad4a-59d5d0852314"
    
    def test_zozo10_discount_code(self):
        """Test ZOZO10 discount code (10% off)"""
        payload = {
            "code": "ZOZO10",
            "order_total": 25.0,
            "order_type": "delivery",
            "location_id": self.RELLINGEN_ID
        }
        response = requests.post(
            f"{BASE_URL}/api/validate-discount-code",
            json=payload,
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is True, f"ZOZO10 should be valid: {data}"
        assert data["discount_type"] == "percentage"
        assert data["discount_value"] == 10
        assert data["discount_amount"] == 2.5, "10% of 25€ should be 2.50€"
        print(f"ZOZO10 validated: {data['discount_amount']}€ discount")
    
    def test_zozo10_with_different_totals(self):
        """Test ZOZO10 with various order totals"""
        test_cases = [
            (50.0, 5.0),   # 10% of 50€ = 5€
            (100.0, 10.0), # 10% of 100€ = 10€
            (15.0, 1.5),   # 10% of 15€ = 1.50€
        ]
        
        for order_total, expected_discount in test_cases:
            payload = {
                "code": "ZOZO10",
                "order_total": order_total,
                "order_type": "delivery",
                "location_id": self.RELLINGEN_ID
            }
            response = requests.post(
                f"{BASE_URL}/api/validate-discount-code",
                json=payload,
                timeout=30
            )
            data = response.json()
            assert data["valid"] is True
            assert abs(data["discount_amount"] - expected_discount) < 0.01, \
                f"Expected {expected_discount}€ for {order_total}€ order, got {data['discount_amount']}€"
    
    def test_invalid_discount_code(self):
        """Test invalid discount code returns valid=False"""
        payload = {
            "code": "INVALID123",
            "order_total": 25.0,
            "order_type": "delivery",
            "location_id": self.RELLINGEN_ID
        }
        response = requests.post(
            f"{BASE_URL}/api/validate-discount-code",
            json=payload,
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        print(f"Invalid code correctly rejected: {data['message']}")
    
    @pytest.mark.xfail(reason="BUG: Timezone-aware vs naive datetime comparison causes 500 error")
    def test_lunch20_discount_code(self):
        """Test LUNCH20 discount code (20% off) - KNOWN BUG"""
        payload = {
            "code": "LUNCH20",
            "order_total": 50.0,
            "order_type": "delivery",
            "location_id": self.RELLINGEN_ID
        }
        response = requests.post(
            f"{BASE_URL}/api/validate-discount-code",
            json=payload,
            timeout=30
        )
        # This test is expected to fail due to timezone bug
        assert response.status_code == 200, "Returns 500 Internal Server Error due to datetime bug"
        data = response.json()
        assert data["valid"] is True
        assert data["discount_value"] == 20
    
    @pytest.mark.xfail(reason="BUG: Timezone-aware vs naive datetime comparison causes 500 error")
    def test_zozodeal2025_discount_code(self):
        """Test ZOZODEAL2025 discount code (5€ fixed) - KNOWN BUG"""
        payload = {
            "code": "ZOZODEAL2025",
            "order_total": 30.0,
            "order_type": "delivery",
            "location_id": self.RELLINGEN_ID
        }
        response = requests.post(
            f"{BASE_URL}/api/validate-discount-code",
            json=payload,
            timeout=30
        )
        # This test is expected to fail due to timezone bug
        assert response.status_code == 200, "Returns 500 Internal Server Error due to datetime bug"


class TestDeliveryZone:
    """Delivery zone check tests"""
    
    def test_valid_postal_code_rellingen(self):
        """Test valid postal code for Rellingen"""
        response = requests.get(
            f"{BASE_URL}/api/check-delivery-zone?postal_code=25462",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is True
        assert "Rellingen" in data.get("location", {}).get("name", "")
        print(f"25462 delivery: {data.get('message')}")
    
    def test_invalid_postal_code(self):
        """Test invalid postal code returns not available"""
        response = requests.get(
            f"{BASE_URL}/api/check-delivery-zone?postal_code=00000",
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert data["available"] is False


class TestCategories:
    """Categories endpoint tests"""
    
    def test_get_categories(self):
        """Test categories endpoint"""
        response = requests.get(f"{BASE_URL}/api/categories", timeout=30)
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        
        categories = data["categories"]
        assert len(categories) > 0, "Should have categories"
        
        category_names = [c["name"] for c in categories]
        print(f"Categories: {category_names}")


class TestModifierGroups:
    """Modifier groups API tests"""
    
    def test_get_modifier_groups(self):
        """Test modifier groups endpoint"""
        response = requests.get(f"{BASE_URL}/api/modifier-groups", timeout=30)
        assert response.status_code == 200
        groups = response.json()
        
        print(f"Found {len(groups)} modifier groups")


class TestFeaturedProducts:
    """Featured products API tests"""
    
    def test_get_featured_products(self):
        """Test featured products endpoint"""
        response = requests.get(f"{BASE_URL}/api/featured-products", timeout=30)
        assert response.status_code == 200
        products = response.json()
        
        print(f"Found {len(products)} featured products")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

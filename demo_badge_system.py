#!/usr/bin/env python3
"""
Demo Script: Badge System mit Test-Daten
Zeigt wie das automatische Badge-System funktioniert
"""
import os
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

sys.path.insert(0, '/app/backend')
from product_analytics_service import ProductAnalyticsService


async def create_sample_orders(db):
    """Erstelle Beispiel-Bestellungen für Demo"""
    print("\n📦 Erstelle Test-Bestellungen...")
    
    # Hole ein paar Produkte
    products = await db.menu_items.find({"active": True}).limit(10).to_list(length=10)
    
    if not products:
        print("   ❌ Keine Produkte gefunden!")
        return 0
    
    # Erstelle Orders für die letzten 30 Tage
    orders_created = 0
    
    for days_ago in range(30):
        order_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        # Produkt 1: Bestseller (viele Verkäufe)
        if len(products) > 0:
            await db.orders.insert_one({
                "location_id": "87de5af8-e424-4fd0-9094-b77b0bf2be77",
                "order_number": f"DEMO-{days_ago}-1",
                "items": [{
                    "menu_item_id": str(products[0]["_id"]),
                    "name": products[0]["name"],
                    "price": products[0].get("price_normal", 10.00),
                    "quantity": 2 if days_ago < 7 else 1  # Mehr in letzten 7 Tagen
                }],
                "customer": {
                    "name": f"Demo Kunde {days_ago}",
                    "email": f"demo{days_ago}@test.de",
                    "phone": "0170000000",
                    "address": "Teststr 1",
                    "postal_code": "25462",
                    "city": "Rellingen"
                },
                "status": "delivered",
                "payment_method": "cash",
                "total": 20.00,
                "subtotal": 20.00,
                "delivery_fee": 0,
                "discount": 0,
                "created_at": order_date,
                "updated_at": order_date
            })
            orders_created += 1
        
        # Produkt 2: Trending (wenig verkauft vor 14 Tagen, viel in letzten 7 Tagen)
        if len(products) > 1 and days_ago < 7:
            for _ in range(3):  # 3x pro Tag in letzter Woche = Trend!
                await db.orders.insert_one({
                    "location_id": "87de5af8-e424-4fd0-9094-b77b0bf2be77",
                    "order_number": f"DEMO-{days_ago}-2-{_}",
                    "items": [{
                        "menu_item_id": str(products[1]["_id"]),
                        "name": products[1]["name"],
                        "price": products[1].get("price_normal", 12.00),
                        "quantity": 1
                    }],
                    "customer": {
                        "name": f"Demo Kunde {days_ago}",
                        "email": f"demo{days_ago}@test.de",
                        "phone": "0170000000",
                        "address": "Teststr 1",
                        "postal_code": "25462",
                        "city": "Rellingen"
                    },
                    "status": "delivered",
                    "payment_method": "cash",
                    "total": 12.00,
                    "subtotal": 12.00,
                    "delivery_fee": 0,
                    "discount": 0,
                    "created_at": order_date,
                    "updated_at": order_date
                })
                orders_created += 1
    
    print(f"   ✅ {orders_created} Test-Bestellungen erstellt")
    return orders_created


async def main():
    """Main Demo Function"""
    print("="*80)
    print("🎯 BADGE SYSTEM DEMO")
    print("="*80)
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['zozo_burger']
    
    # Initialize service
    analytics_service = ProductAnalyticsService(db)
    
    # Check if we have products
    product_count = await db.menu_items.count_documents({"active": True})
    print(f"\n📊 Status: {product_count} aktive Produkte gefunden")
    
    # Check if we have orders
    order_count = await db.orders.count_documents({})
    print(f"📊 Status: {order_count} Bestellungen gefunden")
    
    if order_count == 0:
        print("\n⚠️  Keine Bestellungen vorhanden!")
        create = input("   Möchtest du Test-Bestellungen erstellen? (j/n): ")
        if create.lower() == 'j':
            await create_sample_orders(db)
    
    # Calculate bestsellers
    print("\n\n🏆 BESTSELLER (letzte 30 Tage):")
    print("-" * 80)
    bestsellers = await analytics_service.calculate_bestsellers(days=30)
    
    if bestsellers:
        for idx, item in enumerate(bestsellers[:10], 1):
            print(f"{idx}. {item['product_name']}")
            print(f"   📦 Verkauft: {item['total_quantity']} Stück")
            print(f"   🛒 Bestellungen: {item['total_orders']}")
            print(f"   💰 Umsatz: €{item['total_revenue']:.2f}")
            print()
    else:
        print("   ℹ️  Keine Bestseller gefunden (noch keine Verkäufe)")
    
    # Calculate trending
    print("\n🔥 TRENDING PRODUKTE (letzte 7 Tage):")
    print("-" * 80)
    trending = await analytics_service.calculate_trending_products(days=7)
    
    if trending:
        for idx, item in enumerate(trending[:10], 1):
            print(f"{idx}. {item['product_name']}")
            print(f"   📈 Wachstum: +{item['growth_rate']:.1f}%")
            print(f"   📊 Letzte Woche: {item['previous_sales']} → Diese Woche: {item['current_sales']}")
            print()
    else:
        print("   ℹ️  Keine Trending-Produkte gefunden")
    
    # Get new products
    print("\n🆕 NEUE PRODUKTE (letzte 7 Tage):")
    print("-" * 80)
    new_products = await analytics_service.get_new_products(days=7)
    print(f"   {len(new_products)} neue Produkte")
    
    # Update badges
    print("\n\n🔄 BADGES AKTUALISIEREN:")
    print("-" * 80)
    result = await analytics_service.update_product_badges()
    
    if result.get('success'):
        print("   ✅ Badges erfolgreich aktualisiert!")
        print(f"   🏆 Bestsellers: {result['bestsellers']}")
        print(f"   🔥 Trending: {result['trending']}")
        print(f"   🆕 New: {result['new']}")
    else:
        print(f"   ❌ Fehler: {result.get('error')}")
    
    # Show products with badges
    print("\n\n🏷️  PRODUKTE MIT BADGES:")
    print("-" * 80)
    
    badge_query = {
        "active": True,
        "auto_badge": {"$exists": True}
    }
    
    products_with_badges = await db.menu_items.find(badge_query).sort("auto_badge_priority", 1).to_list(length=20)
    
    if products_with_badges:
        for product in products_with_badges:
            badge = product.get('auto_badge', 'none')
            badge_icons = {
                'bestseller': '🏆',
                'trending': '🔥',
                'new': '🆕'
            }
            icon = badge_icons.get(badge, '✨')
            
            print(f"{icon} {product['name']}")
            print(f"   Badge: {badge.upper()}")
            if 'sales_count_30d' in product:
                print(f"   Verkauft (30d): {product['sales_count_30d']}")
            if 'growth_rate_7d' in product:
                print(f"   Wachstum: +{product['growth_rate_7d']:.1f}%")
            print()
    else:
        print("   ℹ️  Noch keine Produkte mit Auto-Badges")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE!")
    print("="*80)
    
    # API Test
    print("\n\n🔌 API ENDPOINTS (für Frontend):")
    print("-" * 80)
    print("GET  /api/analytics/bestsellers?days=30")
    print("GET  /api/analytics/trending")
    print("GET  /api/analytics/summary")
    print("POST /api/admin/analytics/update-badges (Admin only)")
    print()
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(main())

"""
Enterprise Finance Management Service for ZOZO Burger
Provides comprehensive financial reporting and analysis
Created: 22 January 2026
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List
import os

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Tax rate
TAX_RATE = 0.19  # 19% MwSt. in Germany


class FinanceService:
    """Enterprise Finance Management Service"""

    @staticmethod
    async def get_financial_overview(
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[str] = None,
        branch_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Get comprehensive financial overview
        Returns: revenue, taxes, payment methods, trends
        """
        # Build query
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date},
            "status": "completed"  # Only completed orders for financial reports
        }
        
        if location_id:
            query["location_id"] = location_id
        elif branch_ids:
            query["location_id"] = {"$in": branch_ids}
        
        # Get all completed orders
        orders = await db.orders.find(query).to_list(None)
        
        # Calculate totals
        total_revenue_gross = sum(o.get('total', 0) for o in orders)
        total_orders = len(orders)
        
        # Calculate net revenue and tax
        total_revenue_net = total_revenue_gross / (1 + TAX_RATE)
        total_tax = total_revenue_gross - total_revenue_net
        
        # Payment methods breakdown
        payment_methods = {}
        for order in orders:
            payment_method = order.get('payment_method', 'Unbekannt')
            if payment_method not in payment_methods:
                payment_methods[payment_method] = {
                    'count': 0,
                    'revenue': 0
                }
            payment_methods[payment_method]['count'] += 1
            payment_methods[payment_method]['revenue'] += order.get('total', 0)
        
        # Average order value
        avg_order_value = total_revenue_gross / total_orders if total_orders > 0 else 0
        
        # Calculate previous period for comparison
        period_duration = end_date - start_date
        prev_start = start_date - period_duration
        prev_end = start_date
        
        prev_query = dict(query)
        prev_query["created_at"] = {"$gte": prev_start, "$lte": prev_end}
        prev_orders = await db.orders.find(prev_query).to_list(None)
        prev_revenue = sum(o.get('total', 0) for o in prev_orders)
        
        # Calculate growth
        revenue_growth = ((total_revenue_gross - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        return {
            "overview": {
                "total_revenue_gross": round(total_revenue_gross, 2),
                "total_revenue_net": round(total_revenue_net, 2),
                "total_tax": round(total_tax, 2),
                "total_orders": total_orders,
                "avg_order_value": round(avg_order_value, 2),
                "revenue_growth_percent": round(revenue_growth, 1)
            },
            "payment_methods": {
                method: {
                    "count": data['count'],
                    "revenue": round(data['revenue'], 2),
                    "percentage": round((data['revenue'] / total_revenue_gross * 100) if total_revenue_gross > 0 else 0, 1)
                }
                for method, data in payment_methods.items()
            },
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            }
        }

    @staticmethod
    async def get_revenue_by_location(
        start_date: datetime,
        end_date: datetime,
        branch_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get revenue breakdown by location
        Returns: [{location, revenue_gross, revenue_net, orders, avg_order_value}]
        """
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }
        
        if branch_ids:
            query["location_id"] = {"$in": branch_ids}
        
        orders = await db.orders.find(query).to_list(None)
        
        # Get location names
        locations = await db.locations.find({}).to_list(None)
        location_map = {loc['slug']: loc['name'] for loc in locations}
        
        # Group by location
        location_revenue = {}
        for order in orders:
            loc_id = order.get('location_id', 'unknown')
            
            if loc_id not in location_revenue:
                location_revenue[loc_id] = {
                    'name': location_map.get(loc_id, loc_id),
                    'revenue_gross': 0,
                    'orders': 0
                }
            
            location_revenue[loc_id]['revenue_gross'] += order.get('total', 0)
            location_revenue[loc_id]['orders'] += 1
        
        # Calculate net and avg
        result = []
        for loc_id, data in location_revenue.items():
            revenue_gross = data['revenue_gross']
            revenue_net = revenue_gross / (1 + TAX_RATE)
            orders = data['orders']
            
            result.append({
                'location_id': loc_id,
                'location_name': data['name'],
                'revenue_gross': round(revenue_gross, 2),
                'revenue_net': round(revenue_net, 2),
                'tax': round(revenue_gross - revenue_net, 2),
                'orders': orders,
                'avg_order_value': round(revenue_gross / orders, 2) if orders > 0 else 0
            })
        
        # Sort by revenue
        result.sort(key=lambda x: x['revenue_gross'], reverse=True)
        
        return result

    @staticmethod
    async def get_revenue_by_category(
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[str] = None,
        branch_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get revenue breakdown by product category
        Returns: [{category, revenue, orders, items_sold}]
        """
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }
        
        if location_id:
            query["location_id"] = location_id
        elif branch_ids:
            query["location_id"] = {"$in": branch_ids}
        
        orders = await db.orders.find(query).to_list(None)
        
        # Group by category (from items)
        category_revenue = {}
        for order in orders:
            for item in order.get('items', []):
                # Try to get category from item or default to product name
                category = item.get('category', 'Sonstiges')
                quantity = item.get('quantity', 1)
                price = item.get('price', 0)
                revenue = price * quantity
                
                if category not in category_revenue:
                    category_revenue[category] = {
                        'revenue': 0,
                        'items_sold': 0,
                        'orders': set()
                    }
                
                category_revenue[category]['revenue'] += revenue
                category_revenue[category]['items_sold'] += quantity
                category_revenue[category]['orders'].add(order.get('order_id'))
        
        # Format result
        result = []
        for category, data in category_revenue.items():
            result.append({
                'category': category,
                'revenue': round(data['revenue'], 2),
                'items_sold': data['items_sold'],
                'orders': len(data['orders'])
            })
        
        # Sort by revenue
        result.sort(key=lambda x: x['revenue'], reverse=True)
        
        return result

    @staticmethod
    async def get_daily_revenue_trend(
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[str] = None,
        branch_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get daily revenue trend
        Returns: [{date, revenue_gross, revenue_net, orders}]
        """
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }
        
        if location_id:
            query["location_id"] = location_id
        elif branch_ids:
            query["location_id"] = {"$in": branch_ids}
        
        orders = await db.orders.find(query).to_list(None)
        
        # Group by date
        daily_revenue = {}
        for order in orders:
            order_date = order.get('created_at')
            if isinstance(order_date, str):
                order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
            
            date_key = order_date.strftime('%Y-%m-%d')
            
            if date_key not in daily_revenue:
                daily_revenue[date_key] = {
                    'revenue_gross': 0,
                    'orders': 0
                }
            
            daily_revenue[date_key]['revenue_gross'] += order.get('total', 0)
            daily_revenue[date_key]['orders'] += 1
        
        # Format result
        result = []
        for date_key, data in sorted(daily_revenue.items()):
            revenue_gross = data['revenue_gross']
            revenue_net = revenue_gross / (1 + TAX_RATE)
            
            result.append({
                'date': date_key,
                'revenue_gross': round(revenue_gross, 2),
                'revenue_net': round(revenue_net, 2),
                'tax': round(revenue_gross - revenue_net, 2),
                'orders': data['orders']
            })
        
        return result

    @staticmethod
    async def get_top_products_by_revenue(
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[str] = None,
        branch_ids: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get top products by revenue
        Returns: [{product, revenue, quantity, avg_price}]
        """
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }
        
        if location_id:
            query["location_id"] = location_id
        elif branch_ids:
            query["location_id"] = {"$in": branch_ids}
        
        orders = await db.orders.find(query).to_list(None)
        
        # Group by product
        product_revenue = {}
        for order in orders:
            for item in order.get('items', []):
                product_name = item.get('name', 'Unknown')
                quantity = item.get('quantity', 1)
                price = item.get('price', 0)
                revenue = price * quantity
                
                if product_name not in product_revenue:
                    product_revenue[product_name] = {
                        'revenue': 0,
                        'quantity': 0
                    }
                
                product_revenue[product_name]['revenue'] += revenue
                product_revenue[product_name]['quantity'] += quantity
        
        # Format and sort
        result = []
        for product, data in product_revenue.items():
            result.append({
                'product': product,
                'revenue': round(data['revenue'], 2),
                'quantity': data['quantity'],
                'avg_price': round(data['revenue'] / data['quantity'], 2) if data['quantity'] > 0 else 0
            })
        
        result.sort(key=lambda x: x['revenue'], reverse=True)
        
        return result[:limit]

    @staticmethod
    async def get_monthly_comparison(
        year: int,
        location_id: Optional[str] = None,
        branch_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get month-by-month comparison for a year
        Returns: [{month, revenue, orders, avg_order_value}]
        """
        result = []
        
        for month in range(1, 13):
            # Get month start/end
            start_date = datetime(year, month, 1, tzinfo=timezone.utc)
            if month == 12:
                end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
            
            # Build query
            query = {
                "created_at": {"$gte": start_date, "$lt": end_date},
                "status": "completed"
            }
            
            if location_id:
                query["location_id"] = location_id
            elif branch_ids:
                query["location_id"] = {"$in": branch_ids}
            
            # Get orders
            orders = await db.orders.find(query).to_list(None)
            
            revenue = sum(o.get('total', 0) for o in orders)
            order_count = len(orders)
            
            result.append({
                'month': month,
                'month_name': start_date.strftime('%B'),
                'revenue_gross': round(revenue, 2),
                'revenue_net': round(revenue / (1 + TAX_RATE), 2),
                'orders': order_count,
                'avg_order_value': round(revenue / order_count, 2) if order_count > 0 else 0
            })
        
        return result

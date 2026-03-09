"""
Analytics Service for ZOZO Burger
Provides business intelligence metrics and insights
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


class AnalyticsService:
    """Service for analytics and reporting"""

    @staticmethod
    async def get_overview_stats(
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[str] = None,
        branch_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Get comprehensive overview statistics
        Returns: revenue, orders, customers, avg order value with trends
        """
        # Build query filter
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date}
        }
        
        # Filter by location if specified
        if location_id:
            query["location_id"] = location_id
        elif branch_ids:  # Admin with restricted access
            query["location_id"] = {"$in": branch_ids}
        
        # Calculate previous period for comparison
        period_duration = end_date - start_date
        prev_start = start_date - period_duration
        prev_end = start_date
        
        prev_query = dict(query)
        prev_query["created_at"] = {"$gte": prev_start, "$lte": prev_end}
        
        # Current period metrics
        current_orders = await db.orders.find(query).to_list(None)
        completed_orders = [o for o in current_orders if o.get('status') == 'completed']
        
        total_revenue = sum(o.get('total', 0) for o in completed_orders)
        total_orders = len(current_orders)
        avg_order_value = total_revenue / len(completed_orders) if completed_orders else 0
        
        # Unique customers (by email or phone)
        unique_customers = len(set(
            o.get('customer_email') or o.get('customer_phone', '')
            for o in current_orders
            if o.get('customer_email') or o.get('customer_phone')
        ))
        
        # Previous period metrics for trend calculation
        prev_orders = await db.orders.find(prev_query).to_list(None)
        prev_completed = [o for o in prev_orders if o.get('status') == 'completed']
        prev_revenue = sum(o.get('total', 0) for o in prev_completed)
        prev_total_orders = len(prev_orders)
        prev_avg = prev_revenue / len(prev_completed) if prev_completed else 0
        
        # Calculate trends (percentage change)
        revenue_change = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else 0
        orders_change = ((total_orders - prev_total_orders) / prev_total_orders * 100) if prev_total_orders else 0
        avg_change = ((avg_order_value - prev_avg) / prev_avg * 100) if prev_avg else 0
        
        return {
            "revenue": {
                "total": round(total_revenue, 2),
                "change": round(revenue_change, 1),
                "previous": round(prev_revenue, 2)
            },
            "orders": {
                "total": total_orders,
                "change": round(orders_change, 1),
                "previous": prev_total_orders,
                "new": len([o for o in current_orders if o.get('status') == 'new']),
                "preparing": len([o for o in current_orders if o.get('status') == 'preparing']),
                "completed": len(completed_orders)
            },
            "customers": {
                "total": unique_customers,
                "new": 0,  # TODO: Implement new customer detection
                "returning": 0  # TODO: Implement returning customer detection
            },
            "avg_order_value": {
                "value": round(avg_order_value, 2),
                "change": round(avg_change, 1),
                "previous": round(prev_avg, 2)
            }
        }

    @staticmethod
    async def get_revenue_trend(
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[str] = None,
        branch_ids: Optional[List[str]] = None,
        granularity: str = "day"  # day, week, month
    ) -> List[Dict]:
        """
        Get revenue trend over time
        Returns: list of {date, revenue, orders}
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
        trend_data = {}
        for order in orders:
            order_date = order.get('created_at')
            if isinstance(order_date, str):
                order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
            
            # Format date based on granularity
            if granularity == "day":
                date_key = order_date.strftime('%Y-%m-%d')
            elif granularity == "week":
                date_key = order_date.strftime('%Y-W%U')
            else:  # month
                date_key = order_date.strftime('%Y-%m')
            
            if date_key not in trend_data:
                trend_data[date_key] = {"revenue": 0, "orders": 0}
            
            trend_data[date_key]["revenue"] += order.get('total', 0)
            trend_data[date_key]["orders"] += 1
        
        # Convert to sorted list
        result = [
            {
                "date": date_key,
                "revenue": round(data["revenue"], 2),
                "orders": data["orders"]
            }
            for date_key, data in sorted(trend_data.items())
        ]
        
        return result

    @staticmethod
    async def get_top_products(
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[str] = None,
        branch_ids: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get top-selling products
        Returns: list of {name, quantity, revenue}
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
        
        # Aggregate products
        product_stats = {}
        for order in orders:
            items = order.get('items', [])
            for item in items:
                product_name = item.get('name', 'Unknown')
                quantity = item.get('quantity', 1)
                price = item.get('price', 0)
                
                if product_name not in product_stats:
                    product_stats[product_name] = {"quantity": 0, "revenue": 0}
                
                product_stats[product_name]["quantity"] += quantity
                product_stats[product_name]["revenue"] += price * quantity
        
        # Sort by revenue and limit
        result = [
            {
                "name": name,
                "quantity": stats["quantity"],
                "revenue": round(stats["revenue"], 2)
            }
            for name, stats in sorted(
                product_stats.items(),
                key=lambda x: x[1]["revenue"],
                reverse=True
            )[:limit]
        ]
        
        return result

    @staticmethod
    async def get_peak_hours(
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[str] = None,
        branch_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Get peak hours analysis
        Returns: {hour: order_count} for 24 hours
        """
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date}
        }
        
        if location_id:
            query["location_id"] = location_id
        elif branch_ids:
            query["location_id"] = {"$in": branch_ids}
        
        orders = await db.orders.find(query).to_list(None)
        
        # Count orders by hour
        hourly_stats = {str(h).zfill(2): 0 for h in range(24)}
        
        for order in orders:
            order_date = order.get('created_at')
            if isinstance(order_date, str):
                order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
            
            hour = str(order_date.hour).zfill(2)
            hourly_stats[hour] += 1
        
        return hourly_stats

    @staticmethod
    async def get_location_comparison(
        start_date: datetime,
        end_date: datetime,
        branch_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Compare performance across locations
        Returns: list of {location, revenue, orders, avg_order_value}
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
        
        # Aggregate by location
        location_stats = {}
        for order in orders:
            loc_id = order.get('location_id', 'unknown')
            
            if loc_id not in location_stats:
                location_stats[loc_id] = {
                    "revenue": 0,
                    "orders": 0,
                    "name": location_map.get(loc_id, loc_id)
                }
            
            location_stats[loc_id]["revenue"] += order.get('total', 0)
            location_stats[loc_id]["orders"] += 1
        
        # Calculate avg and format result
        result = [
            {
                "location": stats["name"],
                "location_id": loc_id,
                "revenue": round(stats["revenue"], 2),
                "orders": stats["orders"],
                "avg_order_value": round(stats["revenue"] / stats["orders"], 2) if stats["orders"] > 0 else 0
            }
            for loc_id, stats in sorted(
                location_stats.items(),
                key=lambda x: x[1]["revenue"],
                reverse=True
            )
        ]
        
        return result

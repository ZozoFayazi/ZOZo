"""
Enterprise Customer Service for ZOZO Burger
Provides comprehensive customer relationship management
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


class CustomerService:
    """Enterprise Customer Relationship Management Service"""

    @staticmethod
    def calculate_rfm_score(recency_days: int, frequency: int, monetary: float) -> Dict:
        """
        Calculate RFM (Recency, Frequency, Monetary) Score
        Returns: {r_score, f_score, m_score, rfm_score, segment}
        """
        # Recency Score (1-5, lower days = higher score)
        if recency_days <= 7:
            r_score = 5
        elif recency_days <= 30:
            r_score = 4
        elif recency_days <= 60:
            r_score = 3
        elif recency_days <= 90:
            r_score = 2
        else:
            r_score = 1
        
        # Frequency Score (1-5, more orders = higher score)
        if frequency >= 20:
            f_score = 5
        elif frequency >= 10:
            f_score = 4
        elif frequency >= 5:
            f_score = 3
        elif frequency >= 2:
            f_score = 2
        else:
            f_score = 1
        
        # Monetary Score (1-5, higher spend = higher score)
        if monetary >= 500:
            m_score = 5
        elif monetary >= 250:
            m_score = 4
        elif monetary >= 100:
            m_score = 3
        elif monetary >= 50:
            m_score = 2
        else:
            m_score = 1
        
        # Overall RFM Score
        rfm_score = (r_score + f_score + m_score) / 3
        
        # Segment based on RFM
        if rfm_score >= 4.5:
            segment = 'VIP'
        elif rfm_score >= 3.5:
            segment = 'Active'
        elif rfm_score >= 2.5:
            segment = 'Regular'
        elif rfm_score >= 1.5:
            segment = 'At-Risk'
        else:
            segment = 'Lost'
        
        return {
            'r_score': r_score,
            'f_score': f_score,
            'm_score': m_score,
            'rfm_score': round(rfm_score, 2),
            'segment': segment
        }

    @staticmethod
    async def get_all_customers(
        segment: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = 'total_spent',
        sort_order: str = 'desc',
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict]:
        """
        Get all customers with their stats
        Returns: List of customer objects with RFM scores
        """
        # Get all orders grouped by customer
        pipeline = [
            {
                '$match': {
                    '$or': [
                        {'customer_email': {'$exists': True, '$ne': None, '$ne': ''}},
                        {'customer_phone': {'$exists': True, '$ne': None, '$ne': ''}},
                        {'customer.email': {'$exists': True, '$ne': None, '$ne': ''}},
                        {'customer.phone': {'$exists': True, '$ne': None, '$ne': ''}}
                    ]
                }
            },
            {
                '$group': {
                    '_id': {
                        '$ifNull': [
                            '$customer_email',
                            {'$ifNull': ['$customer.email', {'$ifNull': ['$customer_phone', '$customer.phone']}]}
                        ]
                    },
                    'total_orders': {'$sum': 1},
                    'total_spent': {
                        '$sum': {
                            '$cond': [
                                {'$eq': ['$status', 'completed']},
                                '$total',
                                0
                            ]
                        }
                    },
                    'completed_orders': {
                        '$sum': {
                            '$cond': [
                                {'$eq': ['$status', 'completed']},
                                1,
                                0
                            ]
                        }
                    },
                    'last_order_date': {'$max': '$created_at'},
                    'first_order_date': {'$min': '$created_at'},
                    'customer_name': {'$first': '$customer_name'},
                    'customer_email': {'$first': '$customer_email'},
                    'customer_phone': {'$first': '$customer_phone'},
                    'delivery_addresses': {'$addToSet': '$delivery_address'}
                }
            }
        ]
        
        customers_data = await db.orders.aggregate(pipeline).to_list(None)
        
        # Process customers and calculate RFM
        customers = []
        now = datetime.now(timezone.utc)
        
        for customer in customers_data:
            # Handle datetime conversion - robust for all formats
            last_order = customer.get('last_order_date')
            if not last_order:
                continue  # Skip if no orders
            
            # Debug: log the type and value
            logger.debug(f"last_order type: {type(last_order)}, value: {last_order}, tzinfo: {getattr(last_order, 'tzinfo', None)}")
            
            if isinstance(last_order, str):
                last_order = datetime.fromisoformat(last_order.replace('Z', '+00:00'))
            elif isinstance(last_order, datetime):
                if not last_order.tzinfo:
                    last_order = last_order.replace(tzinfo=timezone.utc)
            else:
                # Force timezone if it's a datetime-like object
                try:
                    if not hasattr(last_order, 'tzinfo') or not last_order.tzinfo:
                        last_order = last_order.replace(tzinfo=timezone.utc)
                except:
                    pass
            
            first_order = customer.get('first_order_date')
            if not first_order:
                first_order = last_order  # Fallback
            
            if isinstance(first_order, str):
                first_order = datetime.fromisoformat(first_order.replace('Z', '+00:00'))
            elif isinstance(first_order, datetime):
                if not first_order.tzinfo:
                    first_order = first_order.replace(tzinfo=timezone.utc)
            else:
                # Force timezone if it's a datetime-like object
                try:
                    if not hasattr(first_order, 'tzinfo') or not first_order.tzinfo:
                        first_order = first_order.replace(tzinfo=timezone.utc)
                except:
                    pass
            
            # Calculate recency
            # Ensure last_order has timezone info
            if hasattr(last_order, 'tzinfo') and not last_order.tzinfo:
                last_order = last_order.replace(tzinfo=timezone.utc)
            days_since_last_order = (now - last_order).days
            
            # Calculate RFM
            rfm = CustomerService.calculate_rfm_score(
                recency_days=days_since_last_order,
                frequency=customer['completed_orders'],
                monetary=customer['total_spent']
            )
            
            # Calculate Customer Lifetime (days)
            customer_lifetime_days = (now - first_order).days
            
            # Calculate Average Order Value
            avg_order_value = customer['total_spent'] / customer['completed_orders'] if customer['completed_orders'] > 0 else 0
            
            customer_obj = {
                'customer_id': customer['_id'],
                'name': customer['customer_name'] or 'Unbekannt',
                'email': customer['customer_email'],
                'phone': customer['customer_phone'],
                'total_orders': customer['total_orders'],
                'completed_orders': customer['completed_orders'],
                'total_spent': round(customer['total_spent'], 2),
                'avg_order_value': round(avg_order_value, 2),
                'last_order_date': last_order.isoformat(),
                'first_order_date': first_order.isoformat(),
                'days_since_last_order': days_since_last_order,
                'customer_lifetime_days': customer_lifetime_days,
                'delivery_addresses': [addr for addr in customer['delivery_addresses'] if addr],
                'rfm': rfm
            }
            
            # Apply segment filter
            if segment and rfm['segment'] != segment:
                continue
            
            # Apply search filter
            if search:
                search_lower = search.lower()
                if not any([
                    search_lower in (customer_obj['name'] or '').lower(),
                    search_lower in (customer_obj['email'] or '').lower(),
                    search_lower in (customer_obj['phone'] or '').lower()
                ]):
                    continue
            
            customers.append(customer_obj)
        
        # Sort customers
        if sort_by == 'total_spent':
            customers.sort(key=lambda x: x['total_spent'], reverse=(sort_order == 'desc'))
        elif sort_by == 'total_orders':
            customers.sort(key=lambda x: x['total_orders'], reverse=(sort_order == 'desc'))
        elif sort_by == 'last_order_date':
            customers.sort(key=lambda x: x['last_order_date'], reverse=(sort_order == 'desc'))
        elif sort_by == 'rfm_score':
            customers.sort(key=lambda x: x['rfm']['rfm_score'], reverse=(sort_order == 'desc'))
        
        # Apply pagination
        total = len(customers)
        customers = customers[skip:skip + limit]
        
        return {
            'customers': customers,
            'total': total,
            'limit': limit,
            'skip': skip
        }

    @staticmethod
    async def get_customer_detail(customer_id: str) -> Dict:
        """
        Get detailed customer information
        Returns: Customer object with full order history and timeline
        """
        # Get all orders for this customer
        orders = await db.orders.find({
            '$or': [
                {'customer_email': customer_id},
                {'customer_phone': customer_id}
            ]
        }).sort('created_at', -1).to_list(None)
        
        if not orders:
            return None
        
        # Calculate stats
        now = datetime.now(timezone.utc)
        total_spent = sum(o.get('total', 0) for o in orders if o.get('status') == 'completed')
        completed_orders = [o for o in orders if o.get('status') == 'completed']
        
        # Get first and last order dates
        last_order = orders[0]
        first_order = orders[-1]
        
        last_order_date = last_order.get('created_at')
        if isinstance(last_order_date, str):
            last_order_date = datetime.fromisoformat(last_order_date.replace('Z', '+00:00'))
        
        first_order_date = first_order.get('created_at')
        if isinstance(first_order_date, str):
            first_order_date = datetime.fromisoformat(first_order_date.replace('Z', '+00:00'))
        
        days_since_last_order = (now - last_order_date).days
        customer_lifetime_days = (now - first_order_date).days
        
        # Calculate RFM
        rfm = CustomerService.calculate_rfm_score(
            recency_days=days_since_last_order,
            frequency=len(completed_orders),
            monetary=total_spent
        )
        
        # Get favorite products
        product_counts = {}
        for order in completed_orders:
            for item in order.get('items', []):
                product_name = item.get('name', 'Unknown')
                product_counts[product_name] = product_counts.get(product_name, 0) + item.get('quantity', 1)
        
        favorite_products = sorted(
            [{'name': name, 'count': count} for name, count in product_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:5]
        
        # Get preferred location
        location_counts = {}
        for order in orders:
            loc = order.get('location_id', 'unknown')
            location_counts[loc] = location_counts.get(loc, 0) + 1
        
        preferred_location = max(location_counts.items(), key=lambda x: x[1])[0] if location_counts else None
        
        # Format order timeline
        order_timeline = []
        for order in orders:
            order_date = order.get('created_at')
            if isinstance(order_date, str):
                order_date = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
            
            order_timeline.append({
                'order_id': order.get('order_id'),
                'date': order_date.isoformat(),
                'status': order.get('status'),
                'total': order.get('total', 0),
                'items_count': len(order.get('items', [])),
                'location': order.get('location_id')
            })
        
        return {
            'customer_id': customer_id,
            'name': last_order.get('customer_name', 'Unbekannt'),
            'email': last_order.get('customer_email'),
            'phone': last_order.get('customer_phone'),
            'total_orders': len(orders),
            'completed_orders': len(completed_orders),
            'total_spent': round(total_spent, 2),
            'avg_order_value': round(total_spent / len(completed_orders), 2) if completed_orders else 0,
            'last_order_date': last_order_date.isoformat(),
            'first_order_date': first_order_date.isoformat(),
            'days_since_last_order': days_since_last_order,
            'customer_lifetime_days': customer_lifetime_days,
            'rfm': rfm,
            'favorite_products': favorite_products,
            'preferred_location': preferred_location,
            'order_timeline': order_timeline
        }

    @staticmethod
    async def get_customer_segments_stats() -> Dict:
        """
        Get statistics for all customer segments
        Returns: {VIP: {count, total_revenue}, Active: {...}, ...}
        """
        result = await CustomerService.get_all_customers(limit=10000)
        customers = result['customers']
        
        segments = {
            'VIP': {'count': 0, 'total_revenue': 0},
            'Active': {'count': 0, 'total_revenue': 0},
            'Regular': {'count': 0, 'total_revenue': 0},
            'At-Risk': {'count': 0, 'total_revenue': 0},
            'Lost': {'count': 0, 'total_revenue': 0}
        }
        
        for customer in customers:
            segment = customer['rfm']['segment']
            segments[segment]['count'] += 1
            segments[segment]['total_revenue'] += customer['total_spent']
        
        # Round revenues
        for segment in segments.values():
            segment['total_revenue'] = round(segment['total_revenue'], 2)
        
        return segments

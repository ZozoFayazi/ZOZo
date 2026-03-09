"""
Product Analytics Service
Automatically tracks and analyzes product performance
"""
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ProductAnalyticsService:
    """Service for analyzing product performance and auto-tagging"""
    
    def __init__(self, db):
        self.db = db
    
    async def calculate_bestsellers(self, days: int = 30, location_id: Optional[str] = None) -> List[Dict]:
        """
        Calculate bestsellers based on actual order data
        
        Args:
            days: Number of days to look back (default: 30)
            location_id: Filter by location (None = all locations)
        
        Returns:
            List of products with sales counts
        """
        try:
            # Calculate date threshold
            threshold_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Build query
            query = {
                "created_at": {"$gte": threshold_date},
                "status": {"$nin": ["cancelled", "failed"]}
            }
            
            if location_id:
                query["location_id"] = location_id
            
            # Aggregate orders by product
            pipeline = [
                {"$match": query},
                {"$unwind": "$items"},
                {
                    "$group": {
                        "_id": "$items.menu_item_id",
                        "product_name": {"$first": "$items.name"},
                        "total_quantity": {"$sum": "$items.quantity"},
                        "total_orders": {"$sum": 1},
                        "total_revenue": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}}
                    }
                },
                {"$sort": {"total_quantity": -1}},
                {"$limit": 20}
            ]
            
            results = await self.db.orders.aggregate(pipeline).to_list(length=20)
            
            return [
                {
                    "product_id": str(item["_id"]),
                    "product_name": item["product_name"],
                    "total_quantity": item["total_quantity"],
                    "total_orders": item["total_orders"],
                    "total_revenue": round(item["total_revenue"], 2)
                }
                for item in results
            ]
        
        except Exception as e:
            logger.error(f"Error calculating bestsellers: {str(e)}")
            return []
    
    async def calculate_trending_products(self, days: int = 7) -> List[Dict]:
        """
        Find products with rapidly increasing sales (trending)
        
        Compares last 7 days vs previous 7 days
        """
        try:
            now = datetime.now(timezone.utc)
            week1_start = now - timedelta(days=7)
            week2_start = now - timedelta(days=14)
            
            # Get sales for last week
            last_week_pipeline = [
                {"$match": {
                    "created_at": {"$gte": week1_start},
                    "status": {"$nin": ["cancelled", "failed"]}
                }},
                {"$unwind": "$items"},
                {
                    "$group": {
                        "_id": "$items.menu_item_id",
                        "product_name": {"$first": "$items.name"},
                        "current_sales": {"$sum": "$items.quantity"}
                    }
                }
            ]
            
            # Get sales for previous week
            prev_week_pipeline = [
                {"$match": {
                    "created_at": {"$gte": week2_start, "$lt": week1_start},
                    "status": {"$nin": ["cancelled", "failed"]}
                }},
                {"$unwind": "$items"},
                {
                    "$group": {
                        "_id": "$items.menu_item_id",
                        "previous_sales": {"$sum": "$items.quantity"}
                    }
                }
            ]
            
            current = {item["_id"]: item for item in await self.db.orders.aggregate(last_week_pipeline).to_list(100)}
            previous = {item["_id"]: item["previous_sales"] for item in await self.db.orders.aggregate(prev_week_pipeline).to_list(100)}
            
            # Calculate growth
            trending = []
            for product_id, data in current.items():
                prev_sales = previous.get(product_id, 0)
                curr_sales = data["current_sales"]
                
                # Must have at least 3 sales last week and 50% growth
                if curr_sales >= 3 and prev_sales > 0:
                    growth_rate = ((curr_sales - prev_sales) / prev_sales) * 100
                    if growth_rate >= 50:  # 50% growth threshold
                        trending.append({
                            "product_id": str(product_id),
                            "product_name": data["product_name"],
                            "current_sales": curr_sales,
                            "previous_sales": prev_sales,
                            "growth_rate": round(growth_rate, 1)
                        })
                elif curr_sales >= 5 and prev_sales == 0:
                    # New hot item
                    trending.append({
                        "product_id": str(product_id),
                        "product_name": data["product_name"],
                        "current_sales": curr_sales,
                        "previous_sales": 0,
                        "growth_rate": 100.0
                    })
            
            # Sort by growth rate
            trending.sort(key=lambda x: x["growth_rate"], reverse=True)
            
            return trending[:10]
        
        except Exception as e:
            logger.error(f"Error calculating trending products: {str(e)}")
            return []
    
    async def get_new_products(self, days: int = 7) -> List[str]:
        """
        Get IDs of products created in the last N days
        """
        try:
            threshold = datetime.now(timezone.utc) - timedelta(days=days)
            
            products = await self.db.menu_items.find({
                "created_at": {"$gte": threshold},
                "active": True
            }).to_list(length=100)
            
            return [str(p["_id"]) for p in products]
        
        except Exception as e:
            logger.error(f"Error getting new products: {str(e)}")
            return []
    
    async def update_product_badges(self):
        """
        Main function to update all product badges based on analytics
        Should be run daily via cron
        """
        try:
            logger.info("Starting product badge update...")
            
            # 1. Get bestsellers (last 30 days)
            bestsellers = await self.calculate_bestsellers(days=30)
            bestseller_ids = [b["product_id"] for b in bestsellers[:5]]  # Top 5
            
            # 2. Get trending products
            trending = await self.calculate_trending_products(days=7)
            trending_ids = [t["product_id"] for t in trending[:5]]  # Top 5
            
            # 3. Get new products
            new_ids = await self.get_new_products(days=7)
            
            # 4. Clear old auto-generated badges
            await self.db.menu_items.update_many(
                {},
                {"$unset": {
                    "auto_badge": "",
                    "auto_badge_priority": "",
                    "sales_rank": "",
                    "sales_count_30d": ""
                }}
            )
            
            # 5. Update bestsellers
            for idx, bestseller in enumerate(bestsellers[:5]):
                await self.db.menu_items.update_one(
                    {"_id": bestseller["product_id"]},
                    {"$set": {
                        "auto_badge": "bestseller",
                        "auto_badge_priority": idx + 1,
                        "sales_rank": idx + 1,
                        "sales_count_30d": bestseller["total_quantity"]
                    }}
                )
            
            # 6. Update trending (if not already bestseller)
            for idx, trend in enumerate(trending[:5]):
                if trend["product_id"] not in bestseller_ids:
                    await self.db.menu_items.update_one(
                        {"_id": trend["product_id"]},
                        {"$set": {
                            "auto_badge": "trending",
                            "auto_badge_priority": idx + 1,
                            "growth_rate_7d": trend["growth_rate"]
                        }}
                    )
            
            # 7. Update new products (if not bestseller or trending)
            for new_id in new_ids:
                if new_id not in bestseller_ids and new_id not in trending_ids:
                    await self.db.menu_items.update_one(
                        {"_id": new_id},
                        {"$set": {
                            "auto_badge": "new",
                            "auto_badge_priority": 10  # Lower priority
                        }}
                    )
            
            logger.info(f"Badge update complete: {len(bestseller_ids)} bestsellers, {len(trending_ids)} trending, {len(new_ids)} new")
            
            return {
                "success": True,
                "bestsellers": len(bestseller_ids),
                "trending": len(trending_ids),
                "new": len(new_ids),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error updating product badges: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_product_analytics_summary(self) -> Dict:
        """
        Get a summary of product analytics for admin dashboard
        """
        try:
            bestsellers = await self.calculate_bestsellers(days=30)
            trending = await self.calculate_trending_products(days=7)
            new = await self.get_new_products(days=7)
            
            return {
                "bestsellers": bestsellers[:10],
                "trending": trending[:10],
                "new_products_count": len(new),
                "total_active_products": await self.db.menu_items.count_documents({"active": True}),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting analytics summary: {str(e)}")
            return {
                "error": str(e)
            }

"""
Review & Rating Service for ZOZO Burger
Intelligent rating system with 2h post-delivery trigger
Created: 22 January 2026
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class ReviewService:
    """Enterprise Review & Rating Management"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_review(
        self,
        order_id: str,
        customer_email: str,
        food_rating: int,
        delivery_rating: int,
        value_rating: int,
        comment: Optional[str] = None,
        tags: Optional[List[str]] = None,
        photo_url: Optional[str] = None
    ) -> Dict:
        """
        Create a new review
        
        Args:
            order_id: Order ID being reviewed
            customer_email: Customer email
            food_rating: 1-5 stars for food quality
            delivery_rating: 1-5 stars for delivery
            value_rating: 1-5 stars for price-value
            comment: Optional text comment
            tags: Optional quick tags
            photo_url: Optional photo URL
        
        Returns:
            {success: bool, review_id: str, reward: dict}
        """
        try:
            # Validate ratings
            if not all(1 <= r <= 5 for r in [food_rating, delivery_rating, value_rating]):
                return {
                    "success": False,
                    "message": "Bewertung muss zwischen 1-5 Sternen liegen"
                }
            
            # Check if already reviewed
            existing = await self.db.reviews.find_one({"order_id": order_id})
            if existing:
                return {
                    "success": False,
                    "message": "Diese Bestellung wurde bereits bewertet"
                }
            
            # Get order details
            order = await self.db.orders.find_one({"order_id": order_id})
            if not order:
                return {
                    "success": False,
                    "message": "Bestellung nicht gefunden"
                }
            
            # Calculate overall rating
            overall_rating = (food_rating + delivery_rating + value_rating) / 3
            
            # Determine moderation status
            needs_moderation = overall_rating < 3.0  # Auto-moderate low ratings
            
            # Create review document
            review_doc = {
                "review_id": str(uuid.uuid4()),
                "order_id": order_id,
                "customer_email": customer_email.lower(),
                "customer_name": order.get('customer_name', 'Anonym'),
                "location_id": order.get('location_id'),
                "ratings": {
                    "food": food_rating,
                    "delivery": delivery_rating,
                    "value": value_rating,
                    "overall": round(overall_rating, 1)
                },
                "comment": comment,
                "tags": tags or [],
                "photo_url": photo_url,
                "status": "pending" if needs_moderation else "approved",
                "moderation_reason": "Low rating (< 3 stars)" if needs_moderation else None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "helpful_count": 0,
                "response": None  # Restaurant can respond
            }
            
            result = await self.db.reviews.insert_one(review_doc)
            
            # Mark order as reviewed
            await self.db.orders.update_one(
                {"order_id": order_id},
                {
                    "$set": {
                        "reviewed": True,
                        "review_id": review_doc['review_id'],
                        "reviewed_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            logger.info(f"Review created for order {order_id}: {overall_rating:.1f}/5 stars")
            
            # Auto-reward for 5-star reviews
            reward = None
            if overall_rating >= 4.5:  # All 5 stars or close
                reward = await self._generate_thank_you_discount(customer_email)
                logger.info(f"5-star reward generated for {customer_email}: {reward.get('code')}")
            
            return {
                "success": True,
                "review_id": review_doc['review_id'],
                "overall_rating": overall_rating,
                "needs_moderation": needs_moderation,
                "reward": reward,
                "message": "Bewertung gespeichert"
            }
            
        except Exception as e:
            logger.error(f"Create review error: {str(e)}")
            return {
                "success": False,
                "message": f"Fehler: {str(e)}"
            }
    
    async def _generate_thank_you_discount(self, customer_email: str) -> Optional[Dict]:
        """Generate 5% thank you discount for 5-star reviews"""
        try:
            from personalized_discount_service import PersonalizedDiscountService
            
            discount_service = PersonalizedDiscountService(self.db)
            
            # Generate code (format: DANKE-{INITIALS}-{RANDOM})
            # For simplicity, use generic DANKE5 code
            code = f"DANKE5-{str(uuid.uuid4())[:6].upper()}"
            
            # Check if code exists
            while await self.db.discount_codes.find_one({"code": code}):
                code = f"DANKE5-{str(uuid.uuid4())[:6].upper()}"
            
            # Create discount
            discount_doc = {
                "code": code,
                "discount_type": "percentage",
                "discount_value": 5,
                "is_personal": True,
                "customer_email": customer_email.lower(),
                "max_uses": 1,
                "used_count": 0,
                "used": False,
                "min_order_value": 0,
                "valid_from": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=30),
                "created_by": "system_review_reward",
                "created_at": datetime.now(timezone.utc),
                "reason": "5_star_review"
            }
            
            await self.db.discount_codes.insert_one(discount_doc)
            
            return {
                "code": code,
                "discount": 5,
                "valid_days": 30
            }
            
        except Exception as e:
            logger.error(f"Failed to generate thank you discount: {str(e)}")
            return None
    
    async def get_reviews(
        self,
        location_id: Optional[str] = None,
        status: Optional[str] = None,
        min_rating: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get reviews with filters"""
        query = {}
        
        if location_id:
            query["location_id"] = location_id
        
        if status:
            query["status"] = status
        
        if min_rating:
            query["ratings.overall"] = {"$gte": min_rating}
        
        reviews = await self.db.reviews.find(query).sort("created_at", -1).limit(limit).to_list(None)
        
        return reviews
    
    async def get_location_stats(self, location_id: str) -> Dict:
        """Get review statistics for a location"""
        pipeline = [
            {"$match": {"location_id": location_id, "status": "approved"}},
            {
                "$group": {
                    "_id": None,
                    "total_reviews": {"$sum": 1},
                    "avg_food": {"$avg": "$ratings.food"},
                    "avg_delivery": {"$avg": "$ratings.delivery"},
                    "avg_value": {"$avg": "$ratings.value"},
                    "avg_overall": {"$avg": "$ratings.overall"},
                    "five_star": {
                        "$sum": {
                            "$cond": [{"$gte": ["$ratings.overall", 4.5]}, 1, 0]
                        }
                    },
                    "four_star": {
                        "$sum": {
                            "$cond": [
                                {"$and": [
                                    {"$gte": ["$ratings.overall", 3.5]},
                                    {"$lt": ["$ratings.overall", 4.5]}
                                ]},
                                1, 0
                            ]
                        }
                    },
                    "three_star": {
                        "$sum": {
                            "$cond": [
                                {"$and": [
                                    {"$gte": ["$ratings.overall", 2.5]},
                                    {"$lt": ["$ratings.overall", 3.5]}
                                ]},
                                1, 0
                            ]
                        }
                    },
                    "two_star": {
                        "$sum": {
                            "$cond": [
                                {"$and": [
                                    {"$gte": ["$ratings.overall", 1.5]},
                                    {"$lt": ["$ratings.overall", 2.5]}
                                ]},
                                1, 0
                            ]
                        }
                    },
                    "one_star": {
                        "$sum": {
                            "$cond": [{"$lt": ["$ratings.overall", 1.5]}, 1, 0]
                        }
                    }
                }
            }
        ]
        
        result = await self.db.reviews.aggregate(pipeline).to_list(1)
        
        if not result:
            return {
                "total_reviews": 0,
                "avg_food": 0,
                "avg_delivery": 0,
                "avg_value": 0,
                "avg_overall": 0,
                "distribution": {}
            }
        
        stats = result[0]
        
        return {
            "total_reviews": stats.get('total_reviews', 0),
            "avg_food": round(stats.get('avg_food', 0), 1),
            "avg_delivery": round(stats.get('avg_delivery', 0), 1),
            "avg_value": round(stats.get('avg_value', 0), 1),
            "avg_overall": round(stats.get('avg_overall', 0), 1),
            "distribution": {
                "5_star": stats.get('five_star', 0),
                "4_star": stats.get('four_star', 0),
                "3_star": stats.get('three_star', 0),
                "2_star": stats.get('two_star', 0),
                "1_star": stats.get('one_star', 0)
            }
        }
    
    async def moderate_review(self, review_id: str, action: str, admin_email: str) -> Dict:
        """Moderate a review (approve/reject)"""
        try:
            review = await self.db.reviews.find_one({"review_id": review_id})
            
            if not review:
                return {"success": False, "message": "Review nicht gefunden"}
            
            if action == "approve":
                status = "approved"
            elif action == "reject":
                status = "rejected"
            else:
                return {"success": False, "message": "Ungültige Aktion"}
            
            await self.db.reviews.update_one(
                {"review_id": review_id},
                {
                    "$set": {
                        "status": status,
                        "moderated_by": admin_email,
                        "moderated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            return {"success": True, "message": f"Review {status}"}
            
        except Exception as e:
            logger.error(f"Moderation error: {str(e)}")
            return {"success": False, "message": str(e)}

"""
Review & Rating API Endpoints
Created: 22 January 2026
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from admin_auth import get_current_admin
from utils import serialize_doc


class ReviewCreate(BaseModel):
    order_id: str
    customer_email: EmailStr
    food_rating: int
    delivery_rating: int
    value_rating: int
    comment: Optional[str] = None
    tags: Optional[List[str]] = None


class ReviewModerate(BaseModel):
    action: str  # approve or reject


def create_review_router(db, review_service):
    """Create review management router"""
    
    router = APIRouter(prefix="/api", tags=["Reviews"])
    
    # ==================== PUBLIC ENDPOINTS ====================
    
    @router.post("/reviews")
    async def create_review(review: ReviewCreate):
        """Public: Create a review for an order"""
        result = await review_service.create_review(
            order_id=review.order_id,
            customer_email=review.customer_email,
            food_rating=review.food_rating,
            delivery_rating=review.delivery_rating,
            value_rating=review.value_rating,
            comment=review.comment,
            tags=review.tags
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('message'))
        
        return result
    
    @router.get("/reviews/location/{location_id}")
    async def get_location_reviews(location_id: str, limit: int = 20):
        """Public: Get approved reviews for a location"""
        reviews = await review_service.get_reviews(
            location_id=location_id,
            status="approved",
            limit=limit
        )
        
        return serialize_doc(reviews)
    
    @router.get("/reviews/stats/{location_id}")
    async def get_review_stats(location_id: str):
        """Public: Get review statistics for a location"""
        stats = await review_service.get_location_stats(location_id)
        return stats
    
    # ==================== ADMIN ENDPOINTS ====================
    
    @router.get("/admin/reviews")
    async def get_all_reviews(
        status: Optional[str] = None,
        location_id: Optional[str] = None,
        admin: dict = Depends(get_current_admin)
    ):
        """Admin: Get all reviews with filters"""
        reviews = await review_service.get_reviews(
            location_id=location_id,
            status=status,
            limit=1000
        )
        
        return serialize_doc(reviews)
    
    @router.patch("/admin/reviews/{review_id}/moderate")
    async def moderate_review(
        review_id: str,
        moderation: ReviewModerate,
        admin: dict = Depends(get_current_admin)
    ):
        """Admin: Moderate a review (approve/reject)"""
        result = await review_service.moderate_review(
            review_id=review_id,
            action=moderation.action,
            admin_email=admin.get('email', 'admin')
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('message'))
        
        return result
    
    return router

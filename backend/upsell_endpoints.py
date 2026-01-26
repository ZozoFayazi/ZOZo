"""
Upselling Endpoints
Provides context-aware upsell recommendations
Created: 23 January 2026
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import logging

from upsell_service import UpsellService

logger = logging.getLogger(__name__)


class UpsellRequest(BaseModel):
    product_type: str
    is_menu: bool = False
    size: Optional[str] = None


def create_upsell_router():
    """Create upsell router"""
    router = APIRouter(prefix="/upsells", tags=["upsells"])
    
    @router.post("/recommendations")
    async def get_upsell_recommendations(request: UpsellRequest):
        """Get upsell recommendations based on context"""
        try:
            upsells = UpsellService.get_upsells(
                product_type=request.product_type,
                is_menu=request.is_menu,
                size=request.size
            )
            
            return upsells
            
        except Exception as e:
            logger.error(f"Get upsells error: {str(e)}")
            return {"categories": []}
    
    return router

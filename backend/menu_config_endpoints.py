"""
Menu Configuration API Endpoints
Allows admin to configure menu items with drink/side/sauce selections
Created: 22 January 2026
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from admin_auth import get_current_admin
from bson import ObjectId


class MenuConfigUpdate(BaseModel):
    is_menu: bool
    available_drinks: Optional[List[str]] = None  # Product IDs
    available_sides: Optional[List[str]] = None   # Product IDs
    available_sauces: Optional[List[str]] = None  # Product IDs
    default_drink: Optional[str] = None
    default_side: Optional[str] = None
    default_sauce: Optional[str] = None


def create_menu_config_router(db):
    router = APIRouter(prefix="/api/admin", tags=["Menu Config"])
    
    @router.patch("/products/{product_id}/menu-config")
    async def update_menu_config(
        product_id: str,
        config: MenuConfigUpdate,
        admin: dict = Depends(get_current_admin)
    ):
        """Update menu configuration for a product"""
        try:
            # Find product
            product = await db.products.find_one({"_id": ObjectId(product_id)})
            if not product:
                raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
            
            # Build menu_config
            menu_config = {
                "is_menu": config.is_menu,
                "available_drinks": config.available_drinks or [],
                "available_sides": config.available_sides or [],
                "available_sauces": config.available_sauces or [],
                "default_drink": config.default_drink,
                "default_side": config.default_side,
                "default_sauce": config.default_sauce
            }
            
            # Update product
            await db.products.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": {"menu_config": menu_config}}
            )
            
            return {
                "success": True,
                "message": "Menü-Konfiguration gespeichert"
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/products/by-category/{category_slug}")
    async def get_products_by_category(
        category_slug: str,
        admin: dict = Depends(get_current_admin)
    ):
        """Get all products in a category (for menu configuration)"""
        products = await db.products.find({"category": category_slug}).to_list(None)
        
        # Format for frontend
        result = []
        for p in products:
            result.append({
                "id": str(p['_id']),
                "name": p.get('name'),
                "price": p.get('price', 0),
                "category": p.get('category')
            })
        
        return result
    
    return router

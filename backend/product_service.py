"""
Product Management Service - Master-Slave Architecture

Architecture:
- Master Menu: All products are global (location_id = null)
- Rellingen Admin = Master (full CRUD on products)
- Henstedt Admin = Slave (can only toggle active/in_stock via overrides)
- branch_product_settings: Stores location-specific overrides
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

logger = logging.getLogger(__name__)


class ProductService:
    """Service for managing products with master-slave architecture"""
    
    # Master location (only this location + super_admin can modify product data)
    MASTER_LOCATION = "rellingen"
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_product_for_location(self, product_id: str, location_slug: str) -> Optional[Dict]:
        """
        Get product with location-specific overrides applied
        
        Args:
            product_id: Product ID
            location_slug: Location slug (e.g. 'henstedt-ulzburg')
        
        Returns:
            Product dict with overrides applied, or None if not found
        """
        # Get base product (global)
        product = await self.db.menu_items.find_one({"_id": ObjectId(product_id)})
        if not product:
            return None
        
        # Check for location-specific overrides
        override = await self.db.branch_product_settings.find_one({
            "product_id": product_id,
            "location_slug": location_slug
        })
        
        if override:
            # Apply overrides
            product['is_active'] = override.get('is_active', product.get('active', True))
            product['in_stock'] = override.get('in_stock', product.get('in_stock', True))
            product['has_override'] = True
        else:
            # Use global defaults
            product['is_active'] = product.get('active', True)
            product['in_stock'] = product.get('in_stock', True)
            product['has_override'] = False
        
        return product
    
    async def get_products_for_location(self, location_slug: str, category_id: Optional[str] = None) -> List[Dict]:
        """
        Get all products for a location with overrides applied
        
        Args:
            location_slug: Location slug
            category_id: Optional category filter
        
        Returns:
            List of products with overrides
        """
        query = {"location_id": None}  # Only global products
        if category_id:
            query["category_id"] = category_id
        
        products = await self.db.menu_items.find(query).to_list(1000)
        
        # Get all overrides for this location in one query
        overrides = await self.db.branch_product_settings.find({
            "location_slug": location_slug
        }).to_list(1000)
        
        # Build override lookup
        override_map = {o['product_id']: o for o in overrides}
        
        # Apply overrides
        result = []
        for product in products:
            product_id = str(product['_id'])
            
            if product_id in override_map:
                override = override_map[product_id]
                product['is_active'] = override.get('is_active', product.get('active', True))
                product['in_stock'] = override.get('in_stock', product.get('in_stock', True))
                product['has_override'] = True
            else:
                product['is_active'] = product.get('active', True)
                product['in_stock'] = product.get('in_stock', True)
                product['has_override'] = False
            
            result.append(product)
        
        return result
    
    async def set_product_override(
        self, 
        product_id: str, 
        location_slug: str, 
        is_active: Optional[bool] = None,
        in_stock: Optional[bool] = None,
        admin_email: str = None
    ) -> Dict:
        """
        Set location-specific override for a product
        
        Only affects active/in_stock status, NOT product data itself.
        
        Args:
            product_id: Product ID
            location_slug: Location slug
            is_active: Override active status
            in_stock: Override stock status
            admin_email: Admin who made the change
        
        Returns:
            Updated override document
        """
        # Verify product exists
        product = await self.db.menu_items.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        # Find or create override
        override = await self.db.branch_product_settings.find_one({
            "product_id": product_id,
            "location_slug": location_slug
        })
        
        if override:
            # Update existing override
            update_data = {"updated_at": datetime.now(timezone.utc)}
            if is_active is not None:
                update_data["is_active"] = is_active
            if in_stock is not None:
                update_data["in_stock"] = in_stock
            if admin_email:
                update_data["updated_by"] = admin_email
            
            await self.db.branch_product_settings.update_one(
                {"_id": override['_id']},
                {"$set": update_data}
            )
            
            logger.info(f"Updated product override: {product_id} for {location_slug}")
        else:
            # Create new override
            override_doc = {
                "product_id": product_id,
                "location_slug": location_slug,
                "is_active": is_active if is_active is not None else product.get('active', True),
                "in_stock": in_stock if in_stock is not None else product.get('in_stock', True),
                "created_at": datetime.now(timezone.utc),
                "created_by": admin_email,
                "updated_at": datetime.now(timezone.utc),
                "updated_by": admin_email
            }
            
            result = await self.db.branch_product_settings.insert_one(override_doc)
            override_doc['_id'] = result.inserted_id
            
            logger.info(f"Created product override: {product_id} for {location_slug}")
        
        # Return updated override
        return await self.db.branch_product_settings.find_one({
            "product_id": product_id,
            "location_slug": location_slug
        })
    
    async def can_modify_product(self, admin_role: str, admin_branch_ids: List[str]) -> bool:
        """
        Check if admin can modify product data (not just overrides)
        
        Only Super Admin and Rellingen Admin can modify product data.
        
        Args:
            admin_role: Admin role
            admin_branch_ids: Admin's branch IDs
        
        Returns:
            True if admin can modify products
        """
        if admin_role == "super_admin":
            return True
        
        # Check if admin manages Rellingen (Master location)
        if self.MASTER_LOCATION in admin_branch_ids:
            return True
        
        return False

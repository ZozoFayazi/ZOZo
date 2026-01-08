"""Product Management Endpoints - Master-Slave Architecture

Architecture:
- Master: Rellingen (can CRUD products)
- Slave: Henstedt (can only toggle active/in_stock via overrides)
- Super Admin: Can do everything
"""
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timezone
from bson import ObjectId
import logging

from admin_auth import get_current_admin
from utils import serialize_doc
from product_service import ProductService
from audit_service import AuditService

logger = logging.getLogger(__name__)


class ProductToggleRequest(BaseModel):
    """Request to toggle product active/stock status (slave locations)"""
    is_active: Optional[bool] = None
    in_stock: Optional[bool] = None


class ProductReorderRequest(BaseModel):
    """Request to reorder products"""
    product_ids: List[str]


def create_product_router_v2(db, audit_service: AuditService):
    """Create product router with master-slave architecture"""
    router = APIRouter(prefix="/admin/products", tags=["products"])
    product_service = ProductService(db)
    
    # Master location
    MASTER_LOCATION = "rellingen"
    
    @router.get("")
    async def get_products(admin: dict = Depends(get_current_admin)):
        """
        Get all products with location-specific overrides applied
        
        - Super Admin: sees all global products
        - Rellingen Admin: sees all global products (can edit)
        - Henstedt Admin: sees all global products with Henstedt overrides (read-only except toggles)
        """
        try:
            # Determine which location to show overrides for
            branch_ids = admin.get("branch_ids", [])
            location_slug = None
            
            if admin["role"] != "super_admin" and branch_ids:
                # Branch admin - show overrides for their location
                location_slug = branch_ids[0] if branch_ids else None
            
            # Get all global products (Master data)
            products = await db.menu_items.find({
                "location_id": None,
                "archived": {"$ne": True}
            }).sort("sort_order", 1).to_list(1000)
            
            # If specific location, apply overrides
            if location_slug:
                # Get all overrides for this location
                overrides = await db.branch_product_settings.find({
                    "location_slug": location_slug
                }).to_list(1000)
                
                override_map = {o['product_id']: o for o in overrides}
                
                # Apply overrides to products
                for product in products:
                    product_id = str(product['_id'])
                    
                    if product_id in override_map:
                        override = override_map[product_id]
                        product['is_active'] = override.get('is_active', product.get('active', True))
                        product['in_stock'] = override.get('in_stock', product.get('in_stock', True))
                        product['has_override'] = True
                    else:
                        # Use master defaults
                        product['is_active'] = product.get('active', True)
                        product['in_stock'] = product.get('in_stock', True)
                        product['has_override'] = False
            else:
                # Super Admin or Master location - use master values
                for product in products:
                    product['is_active'] = product.get('active', True)
                    product['in_stock'] = product.get('in_stock', True)
                    product['has_override'] = False
            
            # Serialize
            result = serialize_doc(products)
            
            return {"products": result}
            
        except Exception as e:
            logger.error(f"Get products error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Laden der Produkte")
    
    
    @router.post("/{product_id}/toggle")
    async def toggle_product_status(
        product_id: str,
        toggle: ProductToggleRequest,
        admin: dict = Depends(get_current_admin)
    ):
        """
        Toggle product active/stock status for a specific location
        
        - Super Admin: Can toggle for any location
        - Master (Rellingen): Can edit product directly
        - Slave (Henstedt): Can only create/update override
        """
        try:
            # Check if product exists - try ObjectId parse
            try:
                product = await db.menu_items.find_one({"_id": ObjectId(product_id)})
            except:
                product = None
            
            if not product:
                raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
            
            # Determine if this is master or slave
            branch_ids = admin.get("branch_ids", [])
            is_master = admin["role"] == "super_admin" or MASTER_LOCATION in branch_ids
            
            if is_master:
                # Master can edit product directly
                update_data = {}
                if toggle.is_active is not None:
                    update_data["active"] = toggle.is_active
                if toggle.in_stock is not None:
                    update_data["in_stock"] = toggle.in_stock
                
                if update_data:
                    await db.menu_items.update_one(
                        {"_id": ObjectId(product_id)},
                        {"$set": {**update_data, "updated_at": datetime.now(timezone.utc)}}
                    )
                    
                    logger.info(f"Master updated product {product_id}: {update_data}")
                    
                    # Audit log
                    await audit_service.log_action(
                        actor_email=admin["email"],
                        action="product_toggle_master",
                        result="success",
                        target=product_id,
                        target_type="product",
                        details=update_data
                    )
            else:
                # Slave - create/update override
                if not branch_ids:
                    raise HTTPException(status_code=403, detail="Keine Standort-Zuordnung")
                
                location_slug = branch_ids[0]
                
                # Create/update override
                override = await product_service.set_product_override(
                    product_id=product_id,
                    location_slug=location_slug,
                    is_active=toggle.is_active,
                    in_stock=toggle.in_stock,
                    admin_email=admin["email"]
                )
                
                logger.info(f"Slave override created for {product_id} at {location_slug}")
                
                # Audit log
                await audit_service.log_action(
                    actor_email=admin["email"],
                    action="product_toggle_override",
                    result="success",
                    target=product_id,
                    target_type="product",
                    details={"location": location_slug, "override": toggle.dict()}
                )
            
            return {"success": True, "message": "Status aktualisiert"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Toggle product error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren")
    

    
    @router.delete("/{product_id}")
    async def delete_product(
        product_id: str,
        admin: dict = Depends(get_current_admin)
    ):
        """
        Delete (soft delete) a product - Master only
        
        - Super Admin: Can delete any product
        - Master (Rellingen): Can delete products
        - Slave (Henstedt): Not allowed
        """
        try:
            # Check if product exists - try ObjectId parse
            try:
                product = await db.menu_items.find_one({"_id": ObjectId(product_id)})
            except:
                product = None
            
            if not product:
                raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
            
            # Check permissions
            branch_ids = admin.get("branch_ids", [])
            is_master = admin["role"] == "super_admin" or MASTER_LOCATION in branch_ids
            
            if not is_master:
                raise HTTPException(
                    status_code=403, 
                    detail="Nur Master-Standort kann Produkte löschen"
                )
            
            # Soft delete
            await db.menu_items.update_one(
                {"_id": product["_id"]},
                {"$set": {"active": False, "updated_at": datetime.now(timezone.utc)}}
            )
            
            logger.info(f"Product {product_id} soft-deleted by {admin['email']}")
            
            # Audit log
            await audit_service.log_action(
                actor_email=admin["email"],
                action="product_delete",
                result="success",
                target=product_id,
                details={"product_name": product.get("name")}
            )
            
            return {"success": True, "message": "Produkt deaktiviert"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Delete product error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Löschen")

    
    @router.get("/permissions")
    async def get_product_permissions(admin: dict = Depends(get_current_admin)):
        """
        Get current admin's product management permissions
        
        Returns what UI elements should be shown/hidden
        """
        branch_ids = admin.get("branch_ids", [])
        is_master = admin["role"] == "super_admin" or MASTER_LOCATION in branch_ids
        
        return {
            "can_create": is_master,
            "can_edit": is_master,
            "can_delete": is_master,
            "can_upload_images": is_master,
            "can_change_prices": is_master,
            "can_reorder": is_master,
            "can_toggle_status": True,  # Everyone can toggle
            "is_master": is_master,
            "location_slug": branch_ids[0] if branch_ids else None,
            "master_location": MASTER_LOCATION
        }
    
    
    return router

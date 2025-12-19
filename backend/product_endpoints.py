"""Product Management Endpoints with Role-Based Access Control"""
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Body
from typing import Optional, List
from pathlib import Path
from pydantic import BaseModel
import uuid
import logging

from admin_auth import get_current_admin, AdminAuth
from utils import serialize_doc, parse_object_id
from models import MenuItemCreate, MenuItemUpdate
from audit_service import AuditService


class ProductOrderItem(BaseModel):
    id: str
    sort_order: int

logger = logging.getLogger(__name__)

def create_product_router(db, audit_service: AuditService):
    """Create product management router with admin authentication"""
    router = APIRouter(prefix="/admin/products", tags=["products"])
    
    def can_manage_products(admin: dict) -> bool:
        """Check if admin can manage products (create, edit, delete, upload images)"""
        return AdminAuth.has_permission(admin["role"], "manage_products")
    
    def can_toggle_product(admin: dict) -> bool:
        """Check if admin can toggle product status (active/inactive, in_stock/out_of_stock)"""
        # All admins can toggle, but only for their branch
        return True
    
    @router.get("")
    async def get_products(admin: dict = Depends(get_current_admin)):
        """Get all products (filtered by branch for branch admins)"""
        try:
            query = {}
            
            # Branch admins see all products (they can't edit but can toggle status)
            # Super Admin sees everything
            
            cursor = db.menu_items.find(query)
            products = await cursor.to_list(length=1000)
            
            for product in products:
                product["_id"] = str(product["_id"])
                product["id"] = product["_id"]
            
            return {"products": products}
        except Exception as e:
            logger.error(f"Get products error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch products")
    
    @router.post("")
    async def create_product(
        product: MenuItemCreate,
        admin: dict = Depends(get_current_admin)
    ):
        """Create a new product (only Super Admin and Rellingen Admin)"""
        try:
            # Check permission
            if not can_manage_products(admin):
                raise HTTPException(
                    status_code=403,
                    detail="Nur Super Admin und Rellingen Admin dürfen Produkte erstellen"
                )
            
            # Create product document
            product_doc = product.dict()
            product_doc["created_at"] = None
            product_doc["updated_at"] = None
            
            # Insert product
            result = await db.menu_items.insert_one(product_doc)
            
            # Audit log
            await audit_service.log_action(
                actor_email=admin["email"],
                action="product_created",
                result="success",
                target=str(result.inserted_id),
                target_type="product",
                details={"name": product.name, "price": product.price}
            )
            
            # Fetch and return created product
            created_product = await db.menu_items.find_one({"_id": result.inserted_id})
            created_product["_id"] = str(created_product["_id"])
            created_product["id"] = created_product["_id"]
            
            return created_product
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Create product error: {str(e)}")
            await audit_service.log_action(
                actor_email=admin["email"],
                action="product_created",
                result="failure",
                details={"error": str(e)}
            )
            raise HTTPException(status_code=500, detail="Failed to create product")
    
    @router.put("/{product_id}")
    async def update_product(
        product_id: str,
        update: MenuItemUpdate,
        admin: dict = Depends(get_current_admin)
    ):
        """Update a product (only Super Admin and Rellingen Admin)"""
        try:
            # Check permission
            if not can_manage_products(admin):
                raise HTTPException(
                    status_code=403,
                    detail="Nur Super Admin und Rellingen Admin dürfen Produkte bearbeiten"
                )
            
            # Check if product exists
            product = await db.menu_items.find_one({"_id": parse_object_id(product_id)})
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Update product
            update_data = {k: v for k, v in update.dict().items() if v is not None}
            if not update_data:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            await db.menu_items.update_one(
                {"_id": parse_object_id(product_id)},
                {"$set": update_data}
            )
            
            # Audit log
            await audit_service.log_action(
                actor_email=admin["email"],
                action="product_updated",
                result="success",
                target=product_id,
                target_type="product",
                details={"updated_fields": list(update_data.keys())}
            )
            
            # Fetch and return updated product
            updated_product = await db.menu_items.find_one({"_id": parse_object_id(product_id)})
            updated_product["_id"] = str(updated_product["_id"])
            updated_product["id"] = updated_product["_id"]
            
            return updated_product
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Update product error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update product")
    
    @router.delete("/{product_id}")
    async def delete_product(
        product_id: str,
        admin: dict = Depends(get_current_admin)
    ):
        """Delete a product (only Super Admin and Rellingen Admin)"""
        try:
            # Check permission
            if not can_manage_products(admin):
                raise HTTPException(
                    status_code=403,
                    detail="Nur Super Admin und Rellingen Admin dürfen Produkte löschen"
                )
            
            # Check if product exists
            product = await db.menu_items.find_one({"_id": parse_object_id(product_id)})
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Delete product
            await db.menu_items.delete_one({"_id": parse_object_id(product_id)})
            
            # Audit log
            await audit_service.log_action(
                actor_email=admin["email"],
                action="product_deleted",
                result="success",
                target=product_id,
                target_type="product",
                details={"name": product.get("name")}
            )
            
            return {"message": f"Product {product.get('name')} deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Delete product error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete product")
    
    @router.patch("/{product_id}/toggle-active")
    async def toggle_product_active(
        product_id: str,
        is_active: bool,
        admin: dict = Depends(get_current_admin)
    ):
        """Toggle product active status (all admins can do this)"""
        try:
            # Check if product exists
            product = await db.menu_items.find_one({"_id": parse_object_id(product_id)})
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Update active status
            await db.menu_items.update_one(
                {"_id": parse_object_id(product_id)},
                {"$set": {"active": is_active}}
            )
            
            # Audit log
            await audit_service.log_action(
                actor_email=admin["email"],
                action="product_toggle_active",
                result="success",
                target=product_id,
                target_type="product",
                details={"is_active": is_active, "name": product.get("name")}
            )
            
            # Fetch and return updated product
            updated_product = await db.menu_items.find_one({"_id": parse_object_id(product_id)})
            updated_product["_id"] = str(updated_product["_id"])
            updated_product["id"] = updated_product["_id"]
            
            return updated_product
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Toggle active error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to toggle active status")
    
    @router.patch("/{product_id}/toggle-stock")
    async def toggle_product_stock(
        product_id: str,
        in_stock: bool,
        admin: dict = Depends(get_current_admin)
    ):
        """Toggle product stock status (all admins can do this)"""
        try:
            # Check if product exists
            product = await db.menu_items.find_one({"_id": parse_object_id(product_id)})
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Update stock status
            await db.menu_items.update_one(
                {"_id": parse_object_id(product_id)},
                {"$set": {"in_stock": in_stock}}
            )
            
            # Audit log
            await audit_service.log_action(
                actor_email=admin["email"],
                action="product_toggle_stock",
                result="success",
                target=product_id,
                target_type="product",
                details={"in_stock": in_stock, "name": product.get("name")}
            )
            
            # Fetch and return updated product
            updated_product = await db.menu_items.find_one({"_id": parse_object_id(product_id)})
            updated_product["_id"] = str(updated_product["_id"])
            updated_product["id"] = updated_product["_id"]
            
            return updated_product
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Toggle stock error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to toggle stock status")
    
    @router.post("/{product_id}/upload-image")
    async def upload_product_image(
        product_id: str,
        file: UploadFile = File(...),
        admin: dict = Depends(get_current_admin)
    ):
        """Upload product image (only Super Admin and Rellingen Admin)"""
        try:
            # Check permission
            if not can_manage_products(admin):
                raise HTTPException(
                    status_code=403,
                    detail="Nur Super Admin und Rellingen Admin dürfen Bilder hochladen"
                )
            
            # Check if product exists
            product = await db.menu_items.find_one({"_id": parse_object_id(product_id)})
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Only JPG, PNG, and WebP allowed"
                )
            
            # Generate unique filename
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = Path("uploads/products") / unique_filename
            
            # Ensure uploads directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file
            try:
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
            
            # Update product with image URL
            image_url = f"/uploads/products/{unique_filename}"
            await db.menu_items.update_one(
                {"_id": parse_object_id(product_id)},
                {"$set": {"image_url": image_url}}
            )
            
            # Audit log
            await audit_service.log_action(
                actor_email=admin["email"],
                action="product_image_uploaded",
                result="success",
                target=product_id,
                target_type="product",
                details={"image_url": image_url, "name": product.get("name")}
            )
            
            return {
                "success": True,
                "image_url": image_url,
                "message": "Image uploaded successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Upload image error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to upload image")
    
    @router.patch("/reorder")
    async def reorder_products(
        product_orders: list,
        admin: dict = Depends(get_current_admin)
    ):
        """Reorder products by updating their sort_order field"""
        try:
            # Check permission
            if not can_manage_products(admin):
                raise HTTPException(
                    status_code=403,
                    detail="Nur Super Admin und Rellingen Admin dürfen Produkte sortieren"
                )
            
            # Update each product's sort_order
            for item in product_orders:
                product_id = item.get("id")
                sort_order = item.get("sort_order")
                
                if product_id and sort_order is not None:
                    await db.menu_items.update_one(
                        {"_id": parse_object_id(product_id)},
                        {"$set": {"sort_order": sort_order}}
                    )
            
            # Audit log
            await audit_service.log_action(
                actor_email=admin["email"],
                action="products_reordered",
                result="success",
                details={"count": len(product_orders)}
            )
            
            return {"success": True, "message": f"{len(product_orders)} Produkte neu sortiert"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Reorder products error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to reorder products")
    
    return router

"""
Burger Builder Endpoints
Manages ingredients with images for live preview
Created: 23 January 2026
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timezone
import logging
import uuid
import os
import shutil

from admin_auth import get_current_admin
from utils import serialize_doc
from burger_builder_service import BurgerBuilderService

logger = logging.getLogger(__name__)


class IngredientCreate(BaseModel):
    category: str
    name: str
    price: float
    layer_order: int
    layer_group: str
    position: str = "center"
    sort_order: int = 0


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    layer_order: Optional[int] = None
    layer_group: Optional[str] = None
    position: Optional[str] = None
    sort_order: Optional[int] = None
    active: Optional[bool] = None


def create_burger_builder_router(db):
    """Create burger builder router"""
    router = APIRouter(prefix="/burger-builder", tags=["burger-builder"])
    service = BurgerBuilderService(db)
    
    @router.get("/ingredients")
    async def get_ingredients():
        """Get all active burger builder ingredients"""
        try:
            ingredients = await service.get_all_ingredients()
            return {"ingredients": ingredients}
        except Exception as e:
            logger.error(f"Get ingredients error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Laden der Zutaten")
    
    @router.get("/ingredients/category/{category}")
    async def get_ingredients_by_category(category: str):
        """Get ingredients by category"""
        try:
            ingredients = await service.get_ingredients_by_category(category)
            return {"ingredients": ingredients}
        except Exception as e:
            logger.error(f"Get ingredients by category error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Laden")
    
    @router.post("/admin/ingredients")
    async def create_ingredient(
        ingredient: IngredientCreate,
        admin: dict = Depends(get_current_admin)
    ):
        """Create new ingredient (admin only)"""
        try:
            result = await service.create_ingredient(ingredient.dict())
            return result
        except Exception as e:
            logger.error(f"Create ingredient error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Erstellen")
    
    @router.put("/admin/ingredients/{ingredient_id}")
    async def update_ingredient(
        ingredient_id: str,
        ingredient: IngredientUpdate,
        admin: dict = Depends(get_current_admin)
    ):
        """Update ingredient (admin only)"""
        try:
            # Remove None values
            update_data = {k: v for k, v in ingredient.dict().items() if v is not None}
            
            success = await service.update_ingredient(ingredient_id, update_data)
            
            if not success:
                raise HTTPException(status_code=404, detail="Zutat nicht gefunden")
            
            return {"success": True, "message": "Zutat aktualisiert"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Update ingredient error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren")
    
    @router.delete("/admin/ingredients/{ingredient_id}")
    async def delete_ingredient(
        ingredient_id: str,
        admin: dict = Depends(get_current_admin)
    ):
        """Delete ingredient (admin only)"""
        try:
            success = await service.delete_ingredient(ingredient_id)
            
            if not success:
                raise HTTPException(status_code=404, detail="Zutat nicht gefunden")
            
            return {"success": True, "message": "Zutat gelöscht"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Delete ingredient error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Löschen")
    
    @router.post("/admin/ingredients/{ingredient_id}/upload-image")
    async def upload_ingredient_image(
        ingredient_id: str,
        file: UploadFile = File(...),
        admin: dict = Depends(get_current_admin)
    ):
        """Upload image for ingredient"""
        try:
            # Validate file type
            allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp']
            if file.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail="Nur PNG, JPG oder WebP erlaubt")
            
            # Create upload directory
            upload_dir = "/app/frontend/public/uploads/burger-builder"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = file.filename.split('.')[-1]
            filename = f"{ingredient_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
            filepath = os.path.join(upload_dir, filename)
            
            # Save file
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Update ingredient with image URL
            image_url = f"/uploads/burger-builder/{filename}"
            
            success = await service.update_ingredient(ingredient_id, {
                "image_url": image_url
            })
            
            if not success:
                # Clean up uploaded file
                os.remove(filepath)
                raise HTTPException(status_code=404, detail="Zutat nicht gefunden")
            
            logger.info(f"Image uploaded for ingredient {ingredient_id}: {image_url}")
            
            return {
                "success": True,
                "image_url": image_url,
                "message": "Bild hochgeladen"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Upload image error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Hochladen")
    
    @router.delete("/admin/ingredients/{ingredient_id}/image")
    async def delete_ingredient_image(
        ingredient_id: str,
        admin: dict = Depends(get_current_admin)
    ):
        """Delete ingredient image"""
        try:
            # Get ingredient to find image_url
            ingredient = await db.burger_builder_ingredients.find_one({"id": ingredient_id})
            
            if not ingredient:
                raise HTTPException(status_code=404, detail="Zutat nicht gefunden")
            
            image_url = ingredient.get("image_url")
            
            if image_url:
                # Delete file from filesystem
                filepath = f"/app/frontend/public{image_url}"
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                # Remove image_url from database
                await service.update_ingredient(ingredient_id, {"image_url": None})
            
            return {"success": True, "message": "Bild entfernt"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Delete image error: {str(e)}")
            raise HTTPException(status_code=500, detail="Fehler beim Löschen")
    
    return router

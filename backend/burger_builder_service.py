"""
Burger Builder Ingredients Service
Manages ingredients with images and layer order for live preview
Created: 23 January 2026
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)


class BurgerBuilderService:
    """Service for managing burger builder ingredients"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_all_ingredients(self) -> List[Dict]:
        """Get all active burger builder ingredients"""
        ingredients = await self.db.burger_builder_ingredients.find({
            "active": True
        }).sort("layer_order", 1).to_list(1000)
        
        # Serialize
        from utils import serialize_doc
        return serialize_doc(ingredients)
    
    async def get_ingredients_by_category(self, category: str) -> List[Dict]:
        """Get ingredients by category (buns, proteins, cheese, etc.)"""
        ingredients = await self.db.burger_builder_ingredients.find({
            "category": category,
            "active": True
        }).sort("sort_order", 1).to_list(1000)
        
        from utils import serialize_doc
        return serialize_doc(ingredients)
    
    async def create_ingredient(self, data: Dict) -> Dict:
        """Create new burger builder ingredient"""
        ingredient = {
            "id": str(uuid.uuid4()),
            "category": data.get("category"),
            "name": data.get("name"),
            "price": data.get("price", 0),
            "image_url": data.get("image_url"),
            "layer_order": data.get("layer_order", 50),
            "layer_group": data.get("layer_group", "middle"),
            "position": data.get("position", "center"),
            "sort_order": data.get("sort_order", 0),
            "active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await self.db.burger_builder_ingredients.insert_one(ingredient)
        
        from utils import serialize_doc
        return serialize_doc(ingredient)
    
    async def update_ingredient(self, ingredient_id: str, data: Dict) -> bool:
        """Update burger builder ingredient"""
        update_data = {
            **data,
            "updated_at": datetime.now(timezone.utc)
        }
        
        result = await self.db.burger_builder_ingredients.update_one(
            {"id": ingredient_id},
            {"$set": update_data}
        )
        
        return result.matched_count > 0
    
    async def delete_ingredient(self, ingredient_id: str) -> bool:
        """Soft delete ingredient"""
        result = await self.db.burger_builder_ingredients.update_one(
            {"id": ingredient_id},
            {"$set": {
                "active": False,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        return result.matched_count > 0
    
    async def initialize_default_ingredients(self):
        """Initialize default ingredients if collection is empty"""
        count = await self.db.burger_builder_ingredients.count_documents({})
        
        if count > 0:
            logger.info("Burger builder ingredients already exist")
            return
        
        logger.info("Initializing default burger builder ingredients...")
        
        default_ingredients = [
            # Buns
            {"id": str(uuid.uuid4()), "category": "buns", "name": "Brioche Bun", "price": 1.50, "layer_order": 10, "layer_group": "bun_bottom", "position": "full", "sort_order": 1, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "buns", "name": "Semolina Bun", "price": 1.50, "layer_order": 10, "layer_group": "bun_bottom", "position": "full", "sort_order": 2, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "buns", "name": "Potato Bun (Smash-Style)", "price": 1.90, "layer_order": 10, "layer_group": "bun_bottom", "position": "full", "sort_order": 3, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            
            # Proteins
            {"id": str(uuid.uuid4()), "category": "proteins", "name": "Beef Patty 125g", "price": 5.90, "layer_order": 50, "layer_group": "patty", "position": "center", "sort_order": 1, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "proteins", "name": "Beef Patty 180g", "price": 7.90, "layer_order": 50, "layer_group": "patty", "position": "center", "sort_order": 2, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "proteins", "name": "Crunchy Chicken Patty", "price": 4.90, "layer_order": 50, "layer_group": "patty", "position": "center", "sort_order": 3, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "proteins", "name": "Fisch Patty", "price": 4.90, "layer_order": 50, "layer_group": "patty", "position": "center", "sort_order": 4, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "proteins", "name": "Veggie Patty", "price": 4.90, "layer_order": 50, "layer_group": "patty", "position": "center", "sort_order": 5, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "proteins", "name": "Nuggets (4 Stück)", "price": 3.90, "layer_order": 50, "layer_group": "patty", "position": "center", "sort_order": 6, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            
            # Cheese
            {"id": str(uuid.uuid4()), "category": "cheese", "name": "Chester Käse (2 Scheiben)", "price": 1.50, "layer_order": 60, "layer_group": "cheese", "position": "center", "sort_order": 1, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "cheese", "name": "Chester Käse (3 Scheiben)", "price": 2.00, "layer_order": 60, "layer_group": "cheese", "position": "center", "sort_order": 2, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "cheese", "name": "Hirtenkäse", "price": 2.00, "layer_order": 60, "layer_group": "cheese", "position": "center", "sort_order": 3, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "cheese", "name": "Grana Padano", "price": 2.00, "layer_order": 60, "layer_group": "cheese", "position": "center", "sort_order": 4, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            
            # Veggies Standard
            {"id": str(uuid.uuid4()), "category": "veggies_standard", "name": "Eisbergsalat", "price": 0.50, "layer_order": 30, "layer_group": "salad", "position": "center", "sort_order": 1, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "veggies_standard", "name": "Tomate", "price": 0.50, "layer_order": 40, "layer_group": "tomato", "position": "center", "sort_order": 2, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "veggies_standard", "name": "Zwiebeln", "price": 0.50, "layer_order": 70, "layer_group": "onion", "position": "center", "sort_order": 3, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "veggies_standard", "name": "Rote Zwiebeln", "price": 0.50, "layer_order": 70, "layer_group": "onion", "position": "center", "sort_order": 4, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
            {"id": str(uuid.uuid4()), "category": "veggies_standard", "name": "Gewürzgurken", "price": 0.50, "layer_order": 80, "layer_group": "pickle", "position": "center", "sort_order": 5, "image_url": None, "active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)},
        ]
        
        await self.db.burger_builder_ingredients.insert_many(default_ingredients)
        logger.info(f"Initialized {len(default_ingredients)} default burger builder ingredients")

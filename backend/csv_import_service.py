"""
CSV Import Service for Menu/Products
Imports menu from CSV file and creates categories + products
"""
import csv
import io
import uuid
from datetime import datetime, timezone
from typing import List, Dict
import logging
import re

logger = logging.getLogger(__name__)


class CSVImportService:
    """Service for importing menu data from CSV"""
    
    def __init__(self, db):
        self.db = db
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug"""
        text = text.lower()
        # German umlauts
        text = text.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
        # Remove special chars
        text = re.sub(r'[^a-z0-9]+', '-', text)
        return text.strip('-')
    
    async def import_menu_csv(
        self,
        tenant_id: str,
        csv_content: str,
        location_id: str = None
    ) -> Dict:
        """
        Import menu from CSV file
        
        Expected CSV format:
        category,name,description,price,price_medium,price_large,allergens
        Burger,Classic Burger,Beef patty with lettuce,8.90,,,Gluten
        Pizza,Margherita,Tomato sauce and mozzarella,7.50,9.50,12.50,Gluten,Dairy
        
        Returns:
            {
                "success": bool,
                "categories_created": int,
                "products_created": int,
                "errors": []
            }
        """
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            
            categories_map = {}  # slug -> category_id
            products_created = 0
            errors = []
            
            # First pass: collect unique categories
            rows = list(reader)
            unique_categories = set(row.get('category', '').strip() for row in rows if row.get('category'))
            
            # Create categories
            for idx, cat_name in enumerate(sorted(unique_categories)):
                cat_slug = self._slugify(cat_name)
                
                # Check if category exists
                existing = await self.db.categories.find_one({
                    "tenant_id": tenant_id,
                    "slug": cat_slug
                })
                
                if existing:
                    categories_map[cat_name] = str(existing['_id'])
                else:
                    category = {
                        "tenant_id": tenant_id,
                        "id": str(uuid.uuid4()),
                        "name": cat_name,
                        "slug": cat_slug,
                        "active": True,
                        "order": idx,
                        "created_at": datetime.now(timezone.utc)
                    }
                    result = await self.db.categories.insert_one(category)
                    categories_map[cat_name] = str(result.inserted_id)
            
            # Second pass: create products
            for row in rows:
                try:
                    category_name = row.get('category', '').strip()
                    if not category_name:
                        errors.append(f"Missing category for: {row.get('name', 'unknown')}")
                        continue
                    
                    category_id = categories_map.get(category_name)
                    if not category_id:
                        errors.append(f"Category not found for: {row.get('name')}")
                        continue
                    
                    product = {
                        "tenant_id": tenant_id,
                        "category_id": category_id,
                        "name": row.get('name', '').strip(),
                        "description": row.get('description', '').strip() or None,
                        "price_normal": float(row.get('price', 0)) if row.get('price') else None,
                        "price_medium": float(row.get('price_medium', 0)) if row.get('price_medium') else None,
                        "price_large": float(row.get('price_large', 0)) if row.get('price_large') else None,
                        "allergens": row.get('allergens', '').strip() or None,
                        "active": True,
                        "in_stock": True,
                        "location_id": location_id,
                        "image_url": None,  # Set default or placeholder
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                    
                    await self.db.menu_items.insert_one(product)
                    products_created += 1
                
                except Exception as e:
                    errors.append(f"Error importing {row.get('name', 'unknown')}: {str(e)}")
            
            return {
                "success": True,
                "categories_created": len(categories_map),
                "products_created": products_created,
                "errors": errors
            }
        
        except Exception as e:
            logger.error(f"CSV import error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "categories_created": 0,
                "products_created": 0
            }

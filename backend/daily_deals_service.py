"""
Daily Deals Service - Automatische Tagesangebote für ZOZO Burger

Angebote:
- Montag: 20% auf alle Pasta
- Dienstag: 2-für-1 bei Wraps (gleiche Wraps)
- Mittwoch: 25% auf alle Pizzen
- Donnerstag: 25% auf Hamburger Klein

Features:
- Automatische Erkennung des Wochentags
- Automatische Rabattberechnung im Warenkorb
- Admin-Verwaltung zum Bearbeiten der Angebote
- Beide Filialen
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import uuid

logger = logging.getLogger(__name__)

# Wochentag-Mapping (Python: 0=Montag, 6=Sonntag)
WEEKDAY_NAMES = {
    0: "Montag",
    1: "Dienstag",
    2: "Mittwoch",
    3: "Donnerstag",
    4: "Freitag",
    5: "Samstag",
    6: "Sonntag"
}


class DailyDealsService:
    """Service für automatische Tagesangebote"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_today_deal(self) -> Optional[Dict]:
        """Holt das aktive Tagesangebot für heute"""
        today = datetime.now(timezone.utc).weekday()  # 0=Montag, 6=Sonntag
        
        deal = await self.db.daily_deals.find_one({
            "weekday": today,
            "active": True
        })
        
        if deal:
            deal = self._serialize_deal(deal)
            deal["weekday_name"] = WEEKDAY_NAMES.get(today, "")
        
        return deal
    
    async def get_all_deals(self) -> List[Dict]:
        """Holt alle Tagesangebote (für Admin)"""
        deals = await self.db.daily_deals.find().sort("weekday", 1).to_list(100)
        return [self._serialize_deal(d) for d in deals]
    
    async def get_deal_by_weekday(self, weekday: int) -> Optional[Dict]:
        """Holt das Angebot für einen bestimmten Wochentag"""
        deal = await self.db.daily_deals.find_one({"weekday": weekday})
        return self._serialize_deal(deal) if deal else None
    
    async def create_deal(self, deal_data: Dict, admin_email: str) -> Dict:
        """Erstellt ein neues Tagesangebot"""
        deal_doc = {
            "id": str(uuid.uuid4()),
            "weekday": deal_data["weekday"],
            "title": deal_data["title"],
            "description": deal_data["description"],
            "discount_type": deal_data["discount_type"],  # "percentage", "2for1"
            "discount_value": deal_data.get("discount_value", 0),
            "target_type": deal_data["target_type"],  # "category", "product", "size"
            "target_value": deal_data["target_value"],  # Kategorie-Slug, Produkt-ID, oder Größe
            "target_size": deal_data.get("target_size"),  # Optional: "klein", "medium", "groß"
            "requires_same_item": deal_data.get("requires_same_item", False),  # Für 2-für-1
            "image_url": deal_data.get("image_url"),
            "badge_text": deal_data.get("badge_text", "Tagesangebot"),
            "badge_color": deal_data.get("badge_color", "#FF6B35"),
            "active": deal_data.get("active", True),
            "applies_to_all_locations": deal_data.get("applies_to_all_locations", True),
            "location_ids": deal_data.get("location_ids", []),
            "created_by": admin_email,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Prüfen ob schon ein Deal für diesen Tag existiert
        existing = await self.db.daily_deals.find_one({"weekday": deal_data["weekday"]})
        if existing:
            # Update statt Insert
            await self.db.daily_deals.update_one(
                {"weekday": deal_data["weekday"]},
                {"$set": {**deal_doc, "id": existing.get("id", deal_doc["id"])}}
            )
            deal_doc["id"] = existing.get("id", deal_doc["id"])
        else:
            await self.db.daily_deals.insert_one(deal_doc)
        
        return self._serialize_deal(deal_doc)
    
    async def update_deal(self, deal_id: str, update_data: Dict, admin_email: str) -> Optional[Dict]:
        """Aktualisiert ein Tagesangebot"""
        update_data["updated_at"] = datetime.now(timezone.utc)
        update_data["updated_by"] = admin_email
        
        result = await self.db.daily_deals.update_one(
            {"id": deal_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return None
        
        updated = await self.db.daily_deals.find_one({"id": deal_id})
        return self._serialize_deal(updated) if updated else None
    
    async def delete_deal(self, deal_id: str) -> bool:
        """Löscht ein Tagesangebot (soft delete)"""
        result = await self.db.daily_deals.update_one(
            {"id": deal_id},
            {"$set": {"active": False, "deleted_at": datetime.now(timezone.utc)}}
        )
        return result.modified_count > 0
    
    async def calculate_cart_discounts(self, cart_items: List[Dict], location_id: str = None) -> Dict:
        """
        Berechnet die Tagesangebot-Rabatte für den Warenkorb
        
        Returns:
            {
                "deal": {...},  # Das aktuelle Tagesangebot
                "applicable_items": [...],  # Items die vom Rabatt betroffen sind
                "discount_amount": float,  # Gesamtrabatt
                "discount_details": [...]  # Details pro Item
            }
        """
        today_deal = await self.get_today_deal()
        
        if not today_deal:
            return {
                "deal": None,
                "applicable_items": [],
                "discount_amount": 0,
                "discount_details": []
            }
        
        # Prüfen ob Deal für diese Location gilt
        if not today_deal.get("applies_to_all_locations", True):
            if location_id and location_id not in today_deal.get("location_ids", []):
                return {
                    "deal": today_deal,
                    "applicable_items": [],
                    "discount_amount": 0,
                    "discount_details": [],
                    "reason": "Deal gilt nicht für diesen Standort"
                }
        
        discount_type = today_deal.get("discount_type")
        target_type = today_deal.get("target_type")
        target_value = today_deal.get("target_value", "").lower()
        target_size = today_deal.get("target_size", "").lower() if today_deal.get("target_size") else None
        
        applicable_items = []
        discount_details = []
        total_discount = 0
        
        # Finde passende Items
        for item in cart_items:
            item_category = (item.get("category") or item.get("category_slug") or "").lower()
            item_name = (item.get("name") or "").lower()
            item_size = (item.get("size") or "").lower() if item.get("size") else None
            item_id = item.get("menu_item_id") or item.get("id") or ""
            
            is_match = False
            
            if target_type == "category":
                # Kategorie-Match (z.B. "pasta", "pizza", "wraps")
                is_match = target_value in item_category or item_category == target_value
            
            elif target_type == "product":
                # Produkt-Match (nach ID oder Name)
                is_match = (item_id == target_value) or (target_value in item_name)
            
            elif target_type == "size":
                # Größen-Match (z.B. "klein" bei Hamburger)
                product_match = target_value in item_name or item_category == target_value
                size_match = target_size and item_size and target_size in item_size
                is_match = product_match and size_match
            
            if is_match:
                applicable_items.append(item)
        
        # Rabatt berechnen
        if discount_type == "percentage":
            # Prozent-Rabatt
            discount_percent = today_deal.get("discount_value", 0)
            for item in applicable_items:
                item_price = item.get("price", 0)
                item_qty = item.get("quantity", 1)
                item_total = item_price * item_qty
                item_discount = item_total * (discount_percent / 100)
                total_discount += item_discount
                
                discount_details.append({
                    "item_name": item.get("name"),
                    "item_size": item.get("size"),
                    "original_price": item_total,
                    "discount": round(item_discount, 2),
                    "discount_percent": discount_percent
                })
        
        elif discount_type == "2for1":
            # 2-für-1: Bei gleichen Items ist das günstigere gratis
            requires_same = today_deal.get("requires_same_item", True)
            
            if requires_same:
                # Gruppiere nach Name+Größe
                item_groups = {}
                for item in applicable_items:
                    key = f"{item.get('name')}|{item.get('size', '')}"
                    if key not in item_groups:
                        item_groups[key] = []
                    item_groups[key].append(item)
                
                for key, items in item_groups.items():
                    # Berechne Gesamtmenge
                    total_qty = sum(i.get("quantity", 1) for i in items)
                    free_count = total_qty // 2  # Jedes zweite ist gratis
                    
                    if free_count > 0:
                        # Nimm den günstigsten Preis
                        min_price = min(i.get("price", 0) for i in items)
                        item_discount = min_price * free_count
                        total_discount += item_discount
                        
                        discount_details.append({
                            "item_name": items[0].get("name"),
                            "item_size": items[0].get("size"),
                            "quantity": total_qty,
                            "free_count": free_count,
                            "discount": round(item_discount, 2),
                            "discount_type": "2für1"
                        })
            else:
                # Alle Items zusammen, günstigere gratis
                sorted_items = sorted(applicable_items, key=lambda x: x.get("price", 0))
                total_qty = sum(i.get("quantity", 1) for i in sorted_items)
                free_count = total_qty // 2
                
                # Die günstigsten sind gratis
                free_remaining = free_count
                for item in sorted_items:
                    item_qty = item.get("quantity", 1)
                    free_from_this = min(item_qty, free_remaining)
                    if free_from_this > 0:
                        item_discount = item.get("price", 0) * free_from_this
                        total_discount += item_discount
                        free_remaining -= free_from_this
                        
                        discount_details.append({
                            "item_name": item.get("name"),
                            "free_count": free_from_this,
                            "discount": round(item_discount, 2),
                            "discount_type": "2für1"
                        })
        
        return {
            "deal": today_deal,
            "applicable_items": [{"name": i.get("name"), "size": i.get("size")} for i in applicable_items],
            "discount_amount": round(total_discount, 2),
            "discount_details": discount_details
        }
    
    async def setup_default_deals(self):
        """Richtet die Standard-Tagesangebote ein"""
        default_deals = [
            {
                "weekday": 0,  # Montag
                "title": "Pasta-Montag",
                "description": "20% Rabatt auf alle Pasta-Gerichte",
                "discount_type": "percentage",
                "discount_value": 20,
                "target_type": "category",
                "target_value": "pasta",
                "badge_text": "🍝 -20%",
                "badge_color": "#FF6B35",
                "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=800"
            },
            {
                "weekday": 1,  # Dienstag
                "title": "Wrap-Dienstag",
                "description": "2 für 1 auf alle Wraps - Bestelle 2 gleiche Wraps, zahle nur 1!",
                "discount_type": "2for1",
                "discount_value": 0,
                "target_type": "category",
                "target_value": "wraps",
                "requires_same_item": True,
                "badge_text": "🌯 2für1",
                "badge_color": "#4CAF50",
                "image_url": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=800"
            },
            {
                "weekday": 2,  # Mittwoch
                "title": "Pizza-Mittwoch",
                "description": "25% Rabatt auf alle Pizzen",
                "discount_type": "percentage",
                "discount_value": 25,
                "target_type": "category",
                "target_value": "pizza",
                "badge_text": "🍕 -25%",
                "badge_color": "#E91E63",
                "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800"
            },
            {
                "weekday": 3,  # Donnerstag
                "title": "Hamburger-Donnerstag",
                "description": "25% Rabatt auf Hamburger in Größe Klein",
                "discount_type": "percentage",
                "discount_value": 25,
                "target_type": "size",
                "target_value": "hamburger",
                "target_size": "klein",
                "badge_text": "🍔 -25%",
                "badge_color": "#FF9800",
                "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800"
            }
        ]
        
        for deal in default_deals:
            deal["active"] = True
            deal["applies_to_all_locations"] = True
            deal["location_ids"] = []
            deal["created_by"] = "system"
            await self.create_deal(deal, "system")
        
        logger.info(f"Setup {len(default_deals)} default daily deals")
        return default_deals
    
    def _serialize_deal(self, deal: Dict) -> Dict:
        """Serialisiert ein Deal-Dokument für JSON-Response"""
        if not deal:
            return None
        
        result = {**deal}
        if "_id" in result:
            result["_id"] = str(result["_id"])
        if "created_at" in result and hasattr(result["created_at"], "isoformat"):
            result["created_at"] = result["created_at"].isoformat()
        if "updated_at" in result and hasattr(result["updated_at"], "isoformat"):
            result["updated_at"] = result["updated_at"].isoformat()
        
        # Füge Wochentag-Name hinzu
        if "weekday" in result:
            result["weekday_name"] = WEEKDAY_NAMES.get(result["weekday"], "")
        
        return result

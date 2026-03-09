"""
Feature Toggle Service - Verwaltung von Feature-Sichtbarkeit
Super Admin kann Features ein/ausschalten
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

logger = logging.getLogger(__name__)

# Standard-Features mit Default-Status
DEFAULT_FEATURES = {
    "burger_builder": {
        "name": "Burger Builder",
        "description": "Eigene Burger kreieren",
        "enabled": False,  # Erstmal aus
        "category": "menu"
    },
    "order_tracking": {
        "name": "Bestellstatus",
        "description": "Live-Tracking von Bestellungen",
        "enabled": False,  # Erstmal aus
        "category": "orders"
    },
    "daily_deals": {
        "name": "Tagesangebote",
        "description": "Automatische Tagesrabatte",
        "enabled": True,
        "category": "promotions"
    },
    "group_orders": {
        "name": "Gruppenbestellungen",
        "description": "Gemeinsam bestellen",
        "enabled": True,
        "category": "orders"
    },
    "rewards": {
        "name": "Treueprogramm",
        "description": "Punkte sammeln und einlösen",
        "enabled": True,
        "category": "promotions"
    },
    "reviews": {
        "name": "Bewertungen",
        "description": "Kundenbewertungen anzeigen",
        "enabled": True,
        "category": "social"
    }
}


class FeatureToggleService:
    """Service für Feature-Toggles"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def initialize_features(self):
        """Initialisiert die Standard-Features falls nicht vorhanden"""
        existing = await self.db.feature_toggles.find_one({})
        
        if not existing:
            doc = {
                "id": str(uuid.uuid4()),
                "features": DEFAULT_FEATURES,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            await self.db.feature_toggles.insert_one(doc)
            logger.info("Feature toggles initialized with defaults")
        
        return await self.get_all_features()
    
    async def get_all_features(self) -> Dict:
        """Holt alle Features mit ihrem Status"""
        doc = await self.db.feature_toggles.find_one({})
        
        if not doc:
            await self.initialize_features()
            doc = await self.db.feature_toggles.find_one({})
        
        return doc.get("features", DEFAULT_FEATURES)
    
    async def get_feature(self, feature_key: str) -> Optional[Dict]:
        """Holt ein einzelnes Feature"""
        features = await self.get_all_features()
        return features.get(feature_key)
    
    async def is_feature_enabled(self, feature_key: str) -> bool:
        """Prüft ob ein Feature aktiviert ist"""
        feature = await self.get_feature(feature_key)
        return feature.get("enabled", False) if feature else False
    
    async def toggle_feature(self, feature_key: str, enabled: bool, admin_email: str) -> Dict:
        """Aktiviert/Deaktiviert ein Feature"""
        features = await self.get_all_features()
        
        if feature_key not in features:
            raise ValueError(f"Unknown feature: {feature_key}")
        
        features[feature_key]["enabled"] = enabled
        features[feature_key]["updated_by"] = admin_email
        features[feature_key]["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await self.db.feature_toggles.update_one(
            {},
            {"$set": {
                f"features.{feature_key}": features[feature_key],
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        logger.info(f"Feature '{feature_key}' set to {enabled} by {admin_email}")
        return features[feature_key]
    
    async def update_feature(self, feature_key: str, data: Dict, admin_email: str) -> Dict:
        """Aktualisiert Feature-Metadaten"""
        features = await self.get_all_features()
        
        if feature_key not in features:
            raise ValueError(f"Unknown feature: {feature_key}")
        
        # Update erlaubte Felder
        allowed_fields = ["name", "description", "enabled"]
        for field in allowed_fields:
            if field in data:
                features[feature_key][field] = data[field]
        
        features[feature_key]["updated_by"] = admin_email
        features[feature_key]["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await self.db.feature_toggles.update_one(
            {},
            {"$set": {
                f"features.{feature_key}": features[feature_key],
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        return features[feature_key]
    
    async def get_public_features(self) -> Dict[str, bool]:
        """Holt nur den enabled-Status für Frontend"""
        features = await self.get_all_features()
        return {key: feat.get("enabled", False) for key, feat in features.items()}

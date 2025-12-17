"""POS Service - Factory and Integration Logic"""
import logging
from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from pos_connectors import BasePOSConnector, ExpertOrderConnector, CashXConnector

logger = logging.getLogger(__name__)

class POSService:
    """Service for managing POS integrations"""
    
    # Registry of available connectors
    CONNECTORS = {
        "expertorder": ExpertOrderConnector,
        "cashx": CashXConnector
    }
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    def get_connector(self, vendor: str, config: Dict) -> Optional[BasePOSConnector]:
        """
        Factory method to get POS connector instance
        
        Args:
            vendor: POS vendor name ('expertorder', 'cashx')
            config: Configuration dictionary for the connector
        
        Returns:
            BasePOSConnector instance or None if vendor not found
        """
        connector_class = self.CONNECTORS.get(vendor.lower())
        
        if not connector_class:
            logger.error(f"Unknown POS vendor: {vendor}")
            return None
        
        try:
            return connector_class(config)
        except Exception as e:
            logger.error(f"Failed to initialize {vendor} connector: {str(e)}")
            return None
    
    async def test_location_pos(self, location_id: str) -> Dict:
        """Test POS connection for a specific location"""
        try:
            # Get location with POS config
            location = await self.db.locations.find_one({"_id": location_id})
            
            if not location:
                return {"success": False, "message": "Location not found"}
            
            pos_config = location.get('pos_integration')
            if not pos_config or not pos_config.get('enabled'):
                return {"success": False, "message": "POS integration not configured"}
            
            vendor = pos_config.get('vendor')
            config = pos_config.get('config', {})
            
            connector = self.get_connector(vendor, config)
            if not connector:
                return {"success": False, "message": f"Unknown POS vendor: {vendor}"}
            
            # Test connection
            result = await connector.test_connection()
            
            # Update location with test result
            await self.db.locations.update_one(
                {"_id": location_id},
                {
                    "$set": {
                        "pos_integration.last_test": result,
                        "pos_integration.status": "connected" if result['success'] else "error"
                    }
                }
            )
            
            return result
        except Exception as e:
            logger.error(f"POS test failed for location {location_id}: {str(e)}")
            return {"success": False, "message": str(e)}
    
    async def push_order_to_pos(self, order_data: Dict, location_id: str) -> Dict:
        """
        Push order to location's POS system
        
        Args:
            order_data: Order information
            location_id: Location identifier
        
        Returns:
            Dict with success status and details
        """
        try:
            # Get location with POS config
            location = await self.db.locations.find_one({"_id": location_id})
            
            if not location:
                return {"success": False, "message": "Location not found"}
            
            pos_config = location.get('pos_integration')
            if not pos_config or not pos_config.get('enabled'):
                logger.info(f"POS not enabled for location {location_id}, skipping push")
                return {"success": True, "message": "POS not enabled, order saved locally"}
            
            vendor = pos_config.get('vendor')
            config = pos_config.get('config', {})
            
            connector = self.get_connector(vendor, config)
            if not connector:
                logger.error(f"Unknown POS vendor: {vendor}")
                return {"success": False, "message": f"Unknown POS vendor: {vendor}"}
            
            # Push order
            result = await connector.push_order(order_data)
            
            # Log result
            await self.db.pos_logs.insert_one({
                "location_id": location_id,
                "vendor": vendor,
                "action": "push_order",
                "order_id": order_data.get('order_id'),
                "success": result['success'],
                "result": result,
                "timestamp": None
            })
            
            return result
        except Exception as e:
            logger.error(f"Failed to push order to POS: {str(e)}")
            return {"success": False, "message": str(e)}
    
    async def get_pos_logs(self, location_id: Optional[str] = None, limit: int = 50) -> list:
        """Get POS integration logs"""
        try:
            query = {}
            if location_id:
                query["location_id"] = location_id
            
            cursor = self.db.pos_logs.find(query).sort("timestamp", -1).limit(limit)
            logs = await cursor.to_list(length=limit)
            
            for log in logs:
                log["_id"] = str(log["_id"])
            
            return logs
        except Exception as e:
            logger.error(f"Failed to fetch POS logs: {str(e)}")
            return []

"""POS Service - Factory, Integration Logic, and Logging"""
import logging
from typing import Dict, Optional, List
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from pos_connectors import BasePOSConnector, ExpertOrderConnector, CashXConnector
from pos_models import POSProvider, POSStatus, POSLogEntry

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
    
    def get_connector(self, provider: str, config: Dict) -> Optional[BasePOSConnector]:
        """
        Factory method to get POS connector instance
        
        Args:
            provider: POS provider name ('expertorder', 'cashx')
            config: Configuration dictionary for the connector
        
        Returns:
            BasePOSConnector instance or None if provider not found
        """
        connector_class = self.CONNECTORS.get(provider.lower())
        
        if not connector_class:
            logger.error(f"Unknown POS provider: {provider}")
            return None
        
        try:
            return connector_class(config)
        except Exception as e:
            logger.error(f"Failed to initialize {provider} connector: {str(e)}")
            return None
    
    async def get_location_pos_config(self, location_slug: str) -> Optional[Dict]:
        """Get POS configuration for a location"""
        location = await self.db.locations.find_one({"slug": location_slug})
        if not location:
            return None
        return location.get('pos_config', self._get_default_pos_config())
    
    def _get_default_pos_config(self) -> Dict:
        """Get default POS configuration"""
        return {
            "provider": "none",
            "status": "disconnected",
            "test_mode": True,
            "credentials": {},
            "settings": {},
            "last_sync_at": None,
            "last_error": None,
            "last_error_at": None
        }
    
    async def update_pos_config(self, location_slug: str, config_data: Dict, admin_email: str) -> Dict:
        """
        Update POS configuration for a location
        
        Args:
            location_slug: Location slug identifier
            config_data: New configuration data
            admin_email: Admin who made the change
        
        Returns:
            Updated configuration
        """
        location = await self.db.locations.find_one({"slug": location_slug})
        if not location:
            raise ValueError(f"Location not found: {location_slug}")
        
        # Get existing config or default
        existing_config = location.get('pos_config', self._get_default_pos_config())
        
        # Build new config
        new_config = {
            "provider": config_data.get('provider', existing_config.get('provider', 'none')),
            "status": existing_config.get('status', 'disconnected'),
            "test_mode": config_data.get('test_mode', existing_config.get('test_mode', True)),
            "credentials": {},
            "settings": config_data.get('settings', existing_config.get('settings', {})),
            "last_sync_at": existing_config.get('last_sync_at'),
            "last_error": existing_config.get('last_error'),
            "last_error_at": existing_config.get('last_error_at'),
            "updated_at": datetime.now(timezone.utc),
            "updated_by": admin_email
        }
        
        # Handle credentials - only update if provided
        existing_creds = existing_config.get('credentials', {})
        new_creds = {}
        
        # Only update credentials if they are provided (not empty strings)
        for field in ['api_key', 'merchant_id', 'username', 'secret', 'base_url', 'terminal_id']:
            if config_data.get(field):
                new_creds[field] = config_data[field]
            elif existing_creds.get(field):
                new_creds[field] = existing_creds[field]
        
        new_config['credentials'] = new_creds
        
        # Update in database
        await self.db.locations.update_one(
            {"slug": location_slug},
            {"$set": {"pos_config": new_config}}
        )
        
        # Log the action
        await self._log_action(
            location_id=str(location['_id']),
            location_slug=location_slug,
            provider=new_config['provider'],
            action="config_update",
            success=True,
            message="POS Konfiguration aktualisiert",
            admin_email=admin_email,
            is_test_mode=new_config['test_mode']
        )
        
        return new_config
    
    async def test_connection(self, location_slug: str, admin_email: str, simulate_failure: bool = False) -> Dict:
        """
        Test POS connection for a location
        
        Args:
            location_slug: Location slug
            admin_email: Admin performing the test
            simulate_failure: Force failure simulation in test mode
        
        Returns:
            Test result dictionary
        """
        location = await self.db.locations.find_one({"slug": location_slug})
        if not location:
            return {"success": False, "message": "Standort nicht gefunden"}
        
        pos_config = location.get('pos_config', self._get_default_pos_config())
        provider = pos_config.get('provider', 'none')
        
        if provider == 'none':
            return {
                "success": False,
                "message": "Kein POS-System konfiguriert",
                "is_test_mode": True
            }
        
        # Build connector config
        connector_config = {
            **pos_config.get('credentials', {}),
            'test_mode': pos_config.get('test_mode', True),
            'test_simulate_failure': simulate_failure
        }
        
        connector = self.get_connector(provider, connector_config)
        if not connector:
            return {
                "success": False,
                "message": f"Unbekannter POS-Provider: {provider}",
                "is_test_mode": pos_config.get('test_mode', True)
            }
        
        # Run test
        result = await connector.test_connection()
        
        # Update status in database
        new_status = "connected" if result['success'] else "error"
        update_data = {
            "pos_config.status": new_status,
            "pos_config.last_sync_at": datetime.now(timezone.utc) if result['success'] else pos_config.get('last_sync_at')
        }
        
        if not result['success']:
            update_data["pos_config.last_error"] = result.get('message', 'Unknown error')
            update_data["pos_config.last_error_at"] = datetime.now(timezone.utc)
        
        await self.db.locations.update_one(
            {"slug": location_slug},
            {"$set": update_data}
        )
        
        # Log the action
        await self._log_action(
            location_id=str(location['_id']),
            location_slug=location_slug,
            provider=provider,
            action="test_connection",
            success=result['success'],
            message=result.get('message', ''),
            details=result.get('details'),
            admin_email=admin_email,
            is_test_mode=result.get('is_test_mode', True)
        )
        
        return result
    
    async def push_order(self, order_data: Dict, location_slug: str) -> Dict:
        """
        Push order to location's POS system
        
        Args:
            order_data: Order information
            location_slug: Location slug
        
        Returns:
            Push result dictionary
        """
        location = await self.db.locations.find_one({"slug": location_slug})
        if not location:
            return {
                "success": False,
                "message": "Standort nicht gefunden",
                "pos_status": "not_applicable"
            }
        
        pos_config = location.get('pos_config', self._get_default_pos_config())
        provider = pos_config.get('provider', 'none')
        
        if provider == 'none':
            logger.info(f"POS not configured for {location_slug}, skipping push")
            return {
                "success": True,
                "message": "POS nicht konfiguriert - Bestellung nur lokal gespeichert",
                "pos_status": "not_applicable"
            }
        
        # Build connector config
        connector_config = {
            **pos_config.get('credentials', {}),
            'test_mode': pos_config.get('test_mode', True)
        }
        
        connector = self.get_connector(provider, connector_config)
        if not connector:
            return {
                "success": False,
                "message": f"Unbekannter POS-Provider: {provider}",
                "pos_status": "error"
            }
        
        # Push order
        result = await connector.push_order(order_data)
        
        # Log the action
        await self._log_action(
            location_id=str(location['_id']),
            location_slug=location_slug,
            provider=provider,
            action="push_order",
            success=result['success'],
            message=result.get('message', ''),
            details=result.get('details'),
            order_id=order_data.get('order_id'),
            pos_order_id=result.get('pos_order_id'),
            is_test_mode=result.get('is_test_mode', True)
        )
        
        # Return with POS status for order tracking
        return {
            **result,
            "pos_status": "sent" if result['success'] else "error"
        }
    
    async def retry_order_push(self, order_id: str, admin_email: str) -> Dict:
        """
        Retry pushing a failed order to POS
        
        Args:
            order_id: Order ID to retry
            admin_email: Admin performing the retry
        
        Returns:
            Retry result
        """
        
        # Get order - try both string and ObjectId
        order = await self.db.orders.find_one({"_id": order_id})
        if not order:
            try:
                order = await self.db.orders.find_one({"_id": ObjectId(order_id)})
            except Exception:
                pass
        if not order:
            return {"success": False, "message": "Bestellung nicht gefunden"}
        
        location_slug = order.get('location_slug') or order.get('location_id')
        if not location_slug:
            return {"success": False, "message": "Standort für Bestellung nicht gefunden"}
        
        # Build order data for POS
        order_data = {
            "order_id": str(order['_id']),
            "order_number": order.get('order_number', ''),
            "customer_name": order.get('customer', {}).get('name', ''),
            "customer_email": order.get('customer', {}).get('email', ''),
            "customer_phone": order.get('customer', {}).get('phone', ''),
            "items": order.get('items', []),
            "total": order.get('total', 0),
            "delivery_type": "pickup" if order.get('is_pickup') else "delivery",
            "delivery_address": order.get('customer', {}).get('address', ''),
            "payment_method": order.get('payment_method', 'cash'),
            "notes": order.get('notes', '')
        }
        
        # Use the actual order _id for updates
        order_oid = order['_id']
        
        # Update order to "retrying" status
        await self.db.orders.update_one(
            {"_id": order_oid},
            {"$set": {"pos_status": "retrying", "pos_retry_at": datetime.now(timezone.utc)}}
        )
        
        # Push order
        result = await self.push_order(order_data, location_slug)
        
        # Update order with result
        update_data = {
            "pos_status": result.get('pos_status', 'error'),
            "pos_last_attempt": datetime.now(timezone.utc)
        }
        if result.get('pos_order_id'):
            update_data["pos_order_id"] = result['pos_order_id']
        if not result['success']:
            update_data["pos_error"] = result.get('message', 'Unknown error')
        
        await self.db.orders.update_one(
            {"_id": order_oid},
            {"$set": update_data}
        )
        
        return result
    
    async def get_logs(self, location_slug: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Get POS integration logs
        
        Args:
            location_slug: Filter by location (optional)
            limit: Max number of logs to return
        
        Returns:
            List of log entries
        """
        query = {}
        if location_slug:
            query["location_slug"] = location_slug
        
        cursor = self.db.pos_logs.find(query).sort("timestamp", -1).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        for log in logs:
            log["_id"] = str(log["_id"])
        
        return logs
    
    async def _log_action(
        self,
        location_id: str,
        location_slug: str,
        provider: str,
        action: str,
        success: bool,
        message: str,
        details: Optional[Dict] = None,
        order_id: Optional[str] = None,
        pos_order_id: Optional[str] = None,
        admin_email: Optional[str] = None,
        is_test_mode: bool = True
    ):
        """Log a POS action"""
        log_entry = {
            "location_id": location_id,
            "location_slug": location_slug,
            "provider": provider,
            "action": action,
            "success": success,
            "message": message,
            "details": details,
            "order_id": order_id,
            "pos_order_id": pos_order_id,
            "admin_email": admin_email,
            "is_test_mode": is_test_mode,
            "timestamp": datetime.now(timezone.utc)
        }
        
        try:
            await self.db.pos_logs.insert_one(log_entry)
        except Exception as e:
            logger.error(f"Failed to log POS action: {str(e)}")

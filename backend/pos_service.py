"""POS Service - Factory, Integration Logic, and Logging with Retry Mechanism"""
import logging
import asyncio
from typing import Dict, Optional, List
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from pos_connectors import BasePOSConnector, ExpertOrderConnector
from pos_models import POSProvider, POSStatus, POSLogEntry

logger = logging.getLogger(__name__)


class POSService:
    """Service for managing POS integrations with automatic retry"""
    
    # Registry of available connectors - ONLY ExpertOrder
    CONNECTORS = {
        "expertorder": ExpertOrderConnector
    }
    
    # Retry configuration: delays in seconds between retries
    RETRY_DELAYS = [2, 5, 10]  # 3 retries: after 2s, 5s, 10s
    
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
        
        return new_config
    
    async def test_connection(self, location_slug: str, admin_email: str) -> Dict:
        """
        Test POS connection for a location
        
        Args:
            location_slug: Location slug
            admin_email: Admin performing test
        
        Returns:
            Connection test result
        """
        location = await self.db.locations.find_one({"slug": location_slug})
        if not location:
            return {"success": False, "message": "Standort nicht gefunden"}
        
        pos_config = location.get('pos_config', self._get_default_pos_config())
        provider = pos_config.get('provider', 'none')
        
        if provider == 'none':
            return {"success": False, "message": "Kein POS-System konfiguriert"}
        
        # Build connector config
        connector_config = {
            **pos_config.get('credentials', {}),
            'test_mode': pos_config.get('test_mode', True)
        }
        
        connector = self.get_connector(provider, connector_config)
        if not connector:
            return {"success": False, "message": f"Unbekannter POS-Provider: {provider}"}
        
        # Test connection
        result = await connector.test_connection()
        
        # Update status in location
        status_update = {
            "pos_config.status": "connected" if result['success'] else "error",
            "pos_config.last_sync_at": datetime.now(timezone.utc) if result['success'] else None,
        }
        if not result['success']:
            status_update["pos_config.last_error"] = result.get('message', 'Unknown error')
            status_update["pos_config.last_error_at"] = datetime.now(timezone.utc)
        
        await self.db.locations.update_one(
            {"slug": location_slug},
            {"$set": status_update}
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
    
    async def push_order_with_retry(self, order_data: Dict, location_slug: str, order_oid: ObjectId = None) -> Dict:
        """
        Push order to POS with automatic retries on failure
        
        This is the main method to use for sending orders to POS.
        It handles retries with exponential backoff and queues failed orders.
        
        Args:
            order_data: Order information
            location_slug: Location slug
            order_oid: Optional ObjectId of the order for status updates
        
        Returns:
            Push result dictionary with retry information
        """
        order_number = order_data.get('order_number', 'UNKNOWN')
        last_error = None
        last_error_type = None  # 'hard' (connection) or 'soft' (api error)
        
        # Get location config once
        location = await self.db.locations.find_one({"slug": location_slug})
        if not location:
            return {
                "success": False,
                "message": "Standort nicht gefunden",
                "pos_status": "not_applicable"
            }
        
        pos_config = location.get('pos_config', self._get_default_pos_config())
        provider = pos_config.get('provider', 'none')
        
        # If no POS configured, skip
        if provider == 'none':
            logger.info(f"POS not configured for {location_slug}, skipping push")
            return {
                "success": True,
                "message": "POS nicht konfiguriert - Bestellung nur lokal gespeichert",
                "pos_status": "not_applicable"
            }
        
        # Attempt with retries
        total_attempts = len(self.RETRY_DELAYS) + 1
        
        for attempt in range(1, total_attempts + 1):
            try:
                logger.info(f"POS push attempt {attempt}/{total_attempts} for {order_number}")
                
                # Attempt push
                result = await self._push_order_single(order_data, location, pos_config, provider)
                
                if result.get("success"):
                    # SUCCESS!
                    if attempt > 1:
                        logger.info(f"POS push SUCCESS for {order_number} on attempt {attempt}")
                        await self._log_retry_success(order_data, location_slug, provider, attempt)
                    
                    # Update order status if we have the OID
                    if order_oid:
                        # Save push history entry
                        push_history_entry = {
                            "timestamp": datetime.now(timezone.utc),
                            "status": "success",
                            "provider": provider,
                            "pos_order_id": result.get('pos_order_id'),
                            "message": result.get('message', 'Successfully sent to POS'),
                            "attempt": attempt,
                            "payload": order_data  # Save what was sent
                        }
                        
                        await self.db.orders.update_one(
                            {"_id": order_oid},
                            {
                                "$set": {
                                    "pos_status": "sent",
                                    "pos_order_id": result.get('pos_order_id'),
                                    "pos_sent_at": datetime.now(timezone.utc),
                                    "pos_retry_count": attempt - 1
                                },
                                "$push": {
                                    "pos_push_history": push_history_entry
                                }
                            }
                        )
                    
                    return {
                        **result,
                        "pos_status": "sent",
                        "retry_count": attempt - 1
                    }
                
                # Soft fail - API reachable but returned error
                last_error = result.get("message", "Unknown error")
                last_error_type = "soft"
                logger.warning(f"POS soft fail for {order_number}: {last_error}")
                
            except Exception as e:
                # Hard fail - connection error, timeout, etc.
                last_error = str(e)
                last_error_type = "hard"
                logger.error(f"POS hard fail for {order_number}: {last_error}")
            
            # Wait before retry (except on last attempt)
            if attempt < total_attempts:
                delay = self.RETRY_DELAYS[attempt - 1]
                logger.info(f"Waiting {delay}s before retry {attempt + 1} for {order_number}")
                await asyncio.sleep(delay)
        
        # ALL RETRIES FAILED
        logger.error(f"POS push FAILED for {order_number} after {total_attempts} attempts")
        
        # Queue the failed order
        await self._queue_failed_order(
            order_data=order_data,
            location_slug=location_slug,
            provider=provider,
            error=last_error,
            error_type=last_error_type,
            retry_count=total_attempts,
            order_oid=order_oid
        )
        
        # Send alert email to admins
        try:
            from pos_alert_email import send_pos_failure_alert
            await send_pos_failure_alert(
                db=self.db,
                order_number=order_number,
                location_slug=location_slug,
                error=last_error,
                error_type=last_error_type,
                order_data=order_data,
                retry_count=total_attempts
            )
        except Exception as e:
            logger.error(f"Failed to send POS alert email: {str(e)}")
        
        # Update order status if we have the OID
        if order_oid:
            # Save failed push history entry
            push_history_entry = {
                "timestamp": datetime.now(timezone.utc),
                "status": "failed",
                "provider": provider,
                "message": last_error,
                "error_type": last_error_type,
                "attempts": total_attempts,
                "payload": order_data  # Save what was attempted
            }
            
            await self.db.orders.update_one(
                {"_id": order_oid},
                {
                    "$set": {
                        "pos_status": "error",
                        "pos_error": last_error,
                        "pos_error_at": datetime.now(timezone.utc),
                        "pos_retry_count": total_attempts
                    },
                    "$push": {
                        "pos_push_history": push_history_entry
                    }
                }
            )
        
        return {
            "success": False,
            "message": f"POS nicht erreichbar nach {total_attempts} Versuchen: {last_error}",
            "pos_status": "error",
            "queued": True,
            "retry_count": total_attempts,
            "error_type": last_error_type
        }
    
    async def _push_order_single(self, order_data: Dict, location: Dict, pos_config: Dict, provider: str) -> Dict:
        """Single push attempt without retry logic"""
        
        # Build connector config
        # Support both flat structure and nested credentials structure
        if 'credentials' in pos_config:
            # Legacy format: credentials in sub-object
            connector_config = {
                **pos_config.get('credentials', {}),
                'test_mode': pos_config.get('test_mode', True)
            }
        else:
            # New format: credentials at root level
            connector_config = {
                **pos_config,
                'test_mode': pos_config.get('test_mode', True)
            }
        
        connector = self.get_connector(provider, connector_config)
        if not connector:
            return {
                "success": False,
                "message": f"Unbekannter POS-Provider: {provider}"
            }
        
        # Push order
        result = await connector.push_order(order_data)
        
        # Log the action
        await self._log_action(
            location_id=str(location['_id']),
            location_slug=location.get('slug', ''),
            provider=provider,
            action="push_order",
            success=result['success'],
            message=result.get('message', ''),
            details=result.get('details'),
            order_id=order_data.get('order_id'),
            pos_order_id=result.get('pos_order_id'),
            is_test_mode=result.get('is_test_mode', True)
        )
        
        return result
    
    async def push_order(self, order_data: Dict, location_slug: str) -> Dict:
        """
        Push order to location's POS system (legacy method, now uses retry)
        NOW WITH PRE-SEND VALIDATION AND AUTO-CONVERSION!
        
        Args:
            order_data: Order information
            location_slug: Location slug
        
        Returns:
            Push result dictionary
        """
        # PRE-SEND VALIDATION & AUTO-CONVERSION
        try:
            from order_validator import OrderValidator, OrderAutoConverter
            
            # Step 1: Validate original order
            validation = OrderValidator.get_validation_report(order_data)
            
            if not validation['valid']:
                logger.warning(f"Order validation failed: {validation['errors']}")
                logger.info("Attempting auto-conversion...")
                
                # Step 2: Try to auto-convert
                converted_order, fixes = OrderAutoConverter.convert_order(order_data)
                
                if fixes:
                    logger.info(f"Auto-conversion applied: {fixes}")
                    
                    # Step 3: Validate converted order
                    revalidation = OrderValidator.get_validation_report(converted_order)
                    
                    if revalidation['valid']:
                        logger.info("✅ Auto-conversion successful! Using converted order.")
                        order_data = converted_order
                    else:
                        logger.error(f"Auto-conversion failed. Remaining errors: {revalidation['errors']}")
                        # Continue anyway but log the issues
                else:
                    logger.warning("No auto-conversion possible. Proceeding with original order...")
            else:
                logger.info("✅ Order validation passed!")
        
        except Exception as e:
            logger.error(f"Validation/Conversion error: {str(e)}")
            # Continue anyway
        
        return await self.push_order_with_retry(order_data, location_slug)
    
    async def _queue_failed_order(
        self,
        order_data: Dict,
        location_slug: str,
        provider: str,
        error: str,
        error_type: str,
        retry_count: int,
        order_oid: ObjectId = None
    ):
        """Save failed order to queue for manual retry"""
        
        failed_order = {
            "order_id": str(order_oid) if order_oid else order_data.get('order_id'),
            "order_number": order_data.get('order_number', ''),
            "location_slug": location_slug,
            "provider": provider,
            "order_data": order_data,
            "error": error,
            "error_type": error_type,  # 'hard' or 'soft'
            "retry_count": retry_count,
            "status": "pending",  # pending, resolved, manual
            "created_at": datetime.now(timezone.utc),
            "resolved_at": None,
            "resolved_by": None
        }
        
        await self.db.failed_pos_orders.insert_one(failed_order)
        
        # Audit log
        await self._log_action(
            location_id="",
            location_slug=location_slug,
            provider=provider,
            action="order_queued_for_retry",
            success=False,
            message=f"Bestellung nach {retry_count} Versuchen in Queue: {error}",
            details={"error_type": error_type, "retry_count": retry_count},
            order_id=order_data.get('order_id'),
            is_test_mode=False
        )
        
        logger.warning(f"Order {order_data.get('order_number')} queued for manual retry")
    
    async def _log_retry_success(self, order_data: Dict, location_slug: str, provider: str, attempt: int):
        """Log successful retry"""
        await self._log_action(
            location_id="",
            location_slug=location_slug,
            provider=provider,
            action="push_order_retry_success",
            success=True,
            message=f"Bestellung erfolgreich nach {attempt} Versuchen",
            details={"attempt": attempt, "total_retries": attempt - 1},
            order_id=order_data.get('order_id'),
            is_test_mode=False
        )
    
    async def retry_failed_order(self, failed_order_id: str, admin_email: str) -> Dict:
        """
        Manually retry a failed order from the queue
        
        Args:
            failed_order_id: ID of the failed_pos_orders entry
            admin_email: Admin performing the retry
        
        Returns:
            Retry result
        """
        # Find the failed order
        try:
            failed = await self.db.failed_pos_orders.find_one({"_id": ObjectId(failed_order_id)})
        except Exception:
            return {"success": False, "message": "Ungültige ID"}
        
        if not failed:
            return {"success": False, "message": "Fehlgeschlagene Bestellung nicht gefunden"}
        
        if failed.get("status") == "resolved":
            return {"success": False, "message": "Diese Bestellung wurde bereits erfolgreich gesendet"}
        
        order_data = failed.get("order_data", {})
        location_slug = failed.get("location_slug")
        
        if not order_data or not location_slug:
            return {"success": False, "message": "Unvollständige Bestelldaten"}
        
        # Update status to "retrying"
        await self.db.failed_pos_orders.update_one(
            {"_id": ObjectId(failed_order_id)},
            {"$set": {
                "status": "retrying",
                "last_retry_at": datetime.now(timezone.utc),
                "last_retry_by": admin_email
            }}
        )
        
        # Try single push (no automatic retries for manual retry)
        location = await self.db.locations.find_one({"slug": location_slug})
        if not location:
            return {"success": False, "message": "Standort nicht gefunden"}
        
        pos_config = location.get('pos_config', self._get_default_pos_config())
        provider = pos_config.get('provider', 'none')
        
        if provider == 'none':
            return {"success": False, "message": "POS nicht konfiguriert"}
        
        result = await self._push_order_single(order_data, location, pos_config, provider)
        
        if result.get("success"):
            # SUCCESS - mark as resolved
            await self.db.failed_pos_orders.update_one(
                {"_id": ObjectId(failed_order_id)},
                {"$set": {
                    "status": "resolved",
                    "resolved_at": datetime.now(timezone.utc),
                    "resolved_by": admin_email,
                    "pos_order_id": result.get('pos_order_id')
                }}
            )
            
            # Update original order if exists
            order_id = failed.get("order_id")
            if order_id:
                try:
                    await self.db.orders.update_one(
                        {"_id": ObjectId(order_id)},
                        {"$set": {
                            "pos_status": "sent",
                            "pos_order_id": result.get('pos_order_id'),
                            "pos_sent_at": datetime.now(timezone.utc)
                        }}
                    )
                except Exception:
                    pass
            
            logger.info(f"Manual retry SUCCESS for {order_data.get('order_number')} by {admin_email}")
            
            return {
                "success": True,
                "message": f"Bestellung erfolgreich an POS gesendet",
                "pos_order_id": result.get('pos_order_id')
            }
        else:
            # FAILED - update retry count
            new_retry_count = failed.get("retry_count", 0) + 1
            await self.db.failed_pos_orders.update_one(
                {"_id": ObjectId(failed_order_id)},
                {"$set": {
                    "status": "pending",
                    "retry_count": new_retry_count,
                    "error": result.get('message', 'Unknown error'),
                    "last_retry_at": datetime.now(timezone.utc)
                }}
            )
            
            logger.warning(f"Manual retry FAILED for {order_data.get('order_number')}: {result.get('message')}")
            
            return {
                "success": False,
                "message": f"Retry fehlgeschlagen: {result.get('message', 'Unknown error')}",
                "retry_count": new_retry_count
            }
    
    async def get_failed_orders(self, location_slug: Optional[str] = None, status: str = "pending") -> List[Dict]:
        """
        Get failed POS orders from queue
        
        Args:
            location_slug: Filter by location (optional, None = all)
            status: Filter by status (pending, resolved, all)
        
        Returns:
            List of failed orders
        """
        query = {}
        if location_slug:
            query["location_slug"] = location_slug
        if status != "all":
            query["status"] = status
        
        cursor = self.db.failed_pos_orders.find(query).sort("created_at", -1).limit(100)
        orders = await cursor.to_list(length=100)
        
        for order in orders:
            order["_id"] = str(order["_id"])
            order["id"] = order["_id"]  # Alias for frontend
        
        return orders
    
    async def get_failed_orders_count(self, location_slug: Optional[str] = None) -> int:
        """Get count of pending failed orders"""
        query = {"status": "pending"}
        if location_slug:
            query["location_slug"] = location_slug
        return await self.db.failed_pos_orders.count_documents(query)
    
    async def retry_order_push(self, order_id: str, admin_email: str) -> Dict:
        """
        Retry pushing a failed order to POS (from orders collection)
        
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
        
        # Push order with retry
        result = await self.push_order_with_retry(order_data, location_slug, order_oid)
        
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

"""PayPal Payment Service for ZOZO Burger"""
import os
import logging
from typing import Optional, Dict, Any
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest, OrdersGetRequest
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class PayPalService:
    """Service for handling PayPal payment processing"""
    
    def __init__(self, db):
        self.db = db
        self.clients = {}  # Cache clients by location_id
    
    def _get_client(self, location_id: str, is_sandbox: bool = True) -> Optional[PayPalHttpClient]:
        """Get or create PayPal client for a specific location"""
        # Return cached client if available
        cache_key = f"{location_id}_{is_sandbox}"
        if cache_key in self.clients:
            return self.clients[cache_key]
        
        # Get location settings from DB
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to handle this differently
                return None
            
            settings = loop.run_until_complete(
                self.db.location_settings.find_one({"location_id": location_id})
            )
        except:
            return None
        
        if not settings:
            logger.warning(f"No settings found for location {location_id}")
            return None
        
        client_id = settings.get('paypal_client_id')
        client_secret = settings.get('paypal_client_secret')
        
        if not client_id or not client_secret:
            logger.warning(f"PayPal credentials not configured for location {location_id}")
            return None
        
        # Create environment
        if is_sandbox:
            environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
        else:
            environment = LiveEnvironment(client_id=client_id, client_secret=client_secret)
        
        # Create client
        client = PayPalHttpClient(environment)
        
        # Cache it
        self.clients[cache_key] = client
        
        return client
    
    async def create_order(self, location_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a PayPal order
        
        Args:
            location_id: Location ID for routing payment
            order_data: Order details including items, total, customer info
        
        Returns:
            Dict with PayPal order ID and approval URL
        """
        try:
            # Get location settings
            settings = await self.db.location_settings.find_one({"location_id": location_id})
            if not settings:
                return {
                    "success": False,
                    "error": "PayPal not configured for this location"
                }
            
            client_id = settings.get('paypal_client_id')
            client_secret = settings.get('paypal_client_secret')
            is_sandbox = settings.get('paypal_sandbox_mode', True)
            
            if not client_id or not client_secret:
                return {
                    "success": False,
                    "error": "PayPal credentials not configured"
                }
            
            # Create PayPal environment
            if is_sandbox:
                environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
            else:
                environment = LiveEnvironment(client_id=client_id, client_secret=client_secret)
            
            client = PayPalHttpClient(environment)
            
            # Create order request
            request = OrdersCreateRequest()
            request.prefer('return=representation')
            
            # Build order body
            order_amount = str(order_data.get('total', 0))
            currency = order_data.get('currency', 'EUR')
            
            request.request_body({
                "intent": "CAPTURE",
                "purchase_units": [{
                    "reference_id": order_data.get('order_id', ''),
                    "description": f"ZOZO Burger Order {order_data.get('order_number', '')}",
                    "custom_id": order_data.get('order_id', ''),
                    "amount": {
                        "currency_code": currency,
                        "value": order_amount,
                        "breakdown": {
                            "item_total": {
                                "currency_code": currency,
                                "value": str(order_data.get('subtotal', order_amount))
                            },
                            "shipping": {
                                "currency_code": currency,
                                "value": str(order_data.get('delivery_fee', 0))
                            },
                            "discount": {
                                "currency_code": currency,
                                "value": str(order_data.get('discount', 0))
                            }
                        }
                    }
                }],
                "application_context": {
                    "brand_name": "ZOZO Burger",
                    "landing_page": "BILLING",
                    "user_action": "PAY_NOW",
                    "return_url": order_data.get('return_url', 'https://zozo-burger.de/order-success'),
                    "cancel_url": order_data.get('cancel_url', 'https://zozo-burger.de/checkout')
                }
            })
            
            # Execute request
            response = client.execute(request)
            
            # Extract approval URL
            approval_url = None
            for link in response.result.links:
                if link.rel == 'approve':
                    approval_url = link.href
                    break
            
            return {
                "success": True,
                "order_id": response.result.id,
                "status": response.result.status,
                "approval_url": approval_url
            }
            
        except Exception as e:
            logger.error(f"PayPal create order error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def capture_order(self, location_id: str, paypal_order_id: str) -> Dict[str, Any]:
        """
        Capture (complete) a PayPal order
        
        Args:
            location_id: Location ID
            paypal_order_id: PayPal order ID to capture
        
        Returns:
            Dict with capture status and transaction details
        """
        try:
            # Get location settings
            settings = await self.db.location_settings.find_one({"location_id": location_id})
            if not settings:
                return {
                    "success": False,
                    "error": "PayPal not configured for this location"
                }
            
            client_id = settings.get('paypal_client_id')
            client_secret = settings.get('paypal_client_secret')
            is_sandbox = settings.get('paypal_sandbox_mode', True)
            
            if not client_id or not client_secret:
                return {
                    "success": False,
                    "error": "PayPal credentials not configured"
                }
            
            # Create PayPal environment
            if is_sandbox:
                environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
            else:
                environment = LiveEnvironment(client_id=client_id, client_secret=client_secret)
            
            client = PayPalHttpClient(environment)
            
            # Capture order
            request = OrdersCaptureRequest(paypal_order_id)
            response = client.execute(request)
            
            # Extract transaction details
            capture_status = response.result.status
            transaction_id = None
            
            if response.result.purchase_units:
                purchase_unit = response.result.purchase_units[0]
                if purchase_unit.payments and purchase_unit.payments.captures:
                    transaction_id = purchase_unit.payments.captures[0].id
            
            return {
                "success": True,
                "status": capture_status,
                "transaction_id": transaction_id,
                "paypal_order_id": paypal_order_id,
                "captured_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"PayPal capture order error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_order_details(self, location_id: str, paypal_order_id: str) -> Dict[str, Any]:
        """
        Get PayPal order details
        
        Args:
            location_id: Location ID
            paypal_order_id: PayPal order ID
        
        Returns:
            Dict with order details
        """
        try:
            # Get location settings
            settings = await self.db.location_settings.find_one({"location_id": location_id})
            if not settings:
                return {
                    "success": False,
                    "error": "PayPal not configured for this location"
                }
            
            client_id = settings.get('paypal_client_id')
            client_secret = settings.get('paypal_client_secret')
            is_sandbox = settings.get('paypal_sandbox_mode', True)
            
            # Create PayPal environment
            if is_sandbox:
                environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
            else:
                environment = LiveEnvironment(client_id=client_id, client_secret=client_secret)
            
            client = PayPalHttpClient(environment)
            
            # Get order
            request = OrdersGetRequest(paypal_order_id)
            response = client.execute(request)
            
            return {
                "success": True,
                "order": {
                    "id": response.result.id,
                    "status": response.result.status,
                    "purchase_units": response.result.purchase_units
                }
            }
            
        except Exception as e:
            logger.error(f"PayPal get order error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

"""ExpertOrder / EOCloud POS Connector with Test Mode Support"""
import httpx
import logging
import random
from typing import Dict
from datetime import datetime
from .base import BasePOSConnector

logger = logging.getLogger(__name__)


class ExpertOrderConnector(BasePOSConnector):
    """
    Connector for ExpertOrder / EOCloud POS system
    
    API Documentation:
    - Base URL: https://s1.eocloud.de/{merchant_id}
    - Send Order: PUT /api/v1/osp
    - Check Status: GET /api/v1/osp
    """
    
    # Default EOCloud base URL (without merchant path)
    DEFAULT_EOCLOUD_BASE = "https://s1.eocloud.de"
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # EOCloud uses merchant_id as part of the URL path
        self.merchant_id = config.get('merchant_id', '')
        
        # Build the correct base URL
        # If base_url is provided and contains the merchant path, use it directly
        # Otherwise, construct it from DEFAULT_EOCLOUD_BASE + merchant_id
        provided_base = config.get('base_url', '')
        if provided_base and '/c' in provided_base:
            # User provided full base URL like https://s1.eocloud.de/c102285
            self.base_url = provided_base.rstrip('/')
        elif self.merchant_id:
            # Construct from merchant_id
            self.base_url = f"{self.DEFAULT_EOCLOUD_BASE}/{self.merchant_id}"
        else:
            self.base_url = self.DEFAULT_EOCLOUD_BASE
        
        # API endpoint path
        self.api_path = "/api/v1/osp"
        
        # Authentication credentials
        self.api_key = config.get('api_key')
        self.username = config.get('username')
        self.secret = config.get('secret')
        self.test_mode = config.get('test_mode', True)
        
        # Test mode simulation settings
        self.test_simulate_failure = config.get('test_simulate_failure', False)
        self.test_failure_rate = config.get('test_failure_rate', 0.0)
        
        logger.info(f"ExpertOrder Connector initialized: base_url={self.base_url}, test_mode={self.test_mode}")
    
    def _get_api_url(self) -> str:
        """Get the full API URL for OSP endpoint"""
        return f"{self.base_url}{self.api_path}"
    
    async def test_connection(self) -> Dict:
        """Test connection to EOCloud API using GET on /api/v1/osp"""
        
        # TEST MODE - Simulate connection
        if self.test_mode:
            return await self._simulate_connection_test()
        
        # LIVE MODE - Real API call to GET /api/v1/osp
        api_url = self._get_api_url()
        logger.info(f"Testing EOCloud connection: GET {api_url}")
        
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
                headers = self._get_headers()
                
                response = await client.get(api_url, headers=headers)
                
                logger.info(f"EOCloud test response: status={response.status_code}, content-type={response.headers.get('content-type', 'unknown')}")
                
                # Check for redirects (302) - this means wrong endpoint or no auth
                if response.status_code == 302:
                    return {
                        "success": False,
                        "message": "Redirect erhalten (302) - möglicherweise falscher Endpoint oder fehlende Authentifizierung",
                        "details": {
                            "status_code": 302,
                            "location": response.headers.get('location', 'unknown'),
                            "api_url": api_url
                        },
                        "is_test_mode": False
                    }
                
                # Check content type - should be JSON, not HTML
                content_type = response.headers.get('content-type', '')
                if 'text/html' in content_type:
                    return {
                        "success": False,
                        "message": "HTML-Antwort erhalten statt JSON - falscher Endpoint",
                        "details": {
                            "status_code": response.status_code,
                            "content_type": content_type,
                            "api_url": api_url
                        },
                        "is_test_mode": False
                    }
                
                # Try to parse JSON response
                try:
                    json_response = response.json()
                    error_message = json_response.get('errorMessage', '')
                    
                    # "Order ID required" means auth was successful, just no order ID provided
                    # This is expected for a GET without order ID - connection is valid!
                    if 'Order ID required' in error_message:
                        return {
                            "success": True,
                            "message": "Verbindung zu EOCloud erfolgreich (API Key akzeptiert)",
                            "details": {
                                "environment": "live",
                                "api_url": api_url,
                                "status_code": response.status_code,
                                "api_response": "Order ID required (expected for test)"
                            },
                            "is_test_mode": False
                        }
                    
                    # "API_KEY required" means authentication failed
                    if 'API_KEY required' in error_message:
                        return {
                            "success": False,
                            "message": "API Key fehlt oder ungültig",
                            "details": {
                                "status_code": response.status_code,
                                "api_url": api_url,
                                "api_response": error_message
                            },
                            "is_test_mode": False
                        }
                except:
                    pass
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "Verbindung zu EOCloud erfolgreich",
                        "details": {
                            "environment": "live",
                            "api_url": api_url,
                            "status_code": 200
                        },
                        "is_test_mode": False
                    }
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "message": "Authentifizierung fehlgeschlagen (401)",
                        "details": {
                            "status_code": 401,
                            "api_url": api_url
                        },
                        "is_test_mode": False
                    }
                elif response.status_code == 403:
                    return {
                        "success": False,
                        "message": "Zugriff verweigert (403) - Credentials prüfen",
                        "details": {
                            "status_code": 403,
                            "api_url": api_url
                        },
                        "is_test_mode": False
                    }
                elif response.status_code == 404:
                    return {
                        "success": False,
                        "message": "Endpoint nicht gefunden (404) - URL prüfen",
                        "details": {
                            "status_code": 404,
                            "api_url": api_url
                        },
                        "is_test_mode": False
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Unerwarteter Status: {response.status_code}",
                        "details": {
                            "status_code": response.status_code,
                            "api_url": api_url,
                            "response_preview": response.text[:200] if response.text else "empty"
                        },
                        "is_test_mode": False
                    }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "Verbindungs-Timeout (15s)",
                "details": {"error": "timeout", "api_url": api_url},
                "is_test_mode": False
            }
        except httpx.ConnectError as e:
            return {
                "success": False,
                "message": f"Verbindungsfehler: Server nicht erreichbar",
                "details": {"error": str(e), "api_url": api_url},
                "is_test_mode": False
            }
        except Exception as e:
            logger.error(f"EOCloud connection test failed: {str(e)}")
            return {
                "success": False,
                "message": f"Fehler: {str(e)}",
                "details": {"error": str(e), "api_url": api_url},
                "is_test_mode": False
            }
    
    async def _simulate_connection_test(self) -> Dict:
        """Simulate connection test in test mode"""
        if self.test_simulate_failure:
            return {
                "success": False,
                "message": "[TESTMODUS] Simulierter Verbindungsfehler",
                "details": {
                    "environment": "test",
                    "simulated": True,
                    "reason": "test_simulate_failure=True"
                },
                "is_test_mode": True
            }
        
        # Check if base_url looks valid
        if not self.base_url or self.base_url == self.DEFAULT_EOCLOUD_BASE:
            return {
                "success": False,
                "message": "[TESTMODUS] Base URL nicht konfiguriert - Merchant ID fehlt",
                "details": {
                    "environment": "test",
                    "simulated": True,
                    "missing_field": "base_url/merchant_id",
                    "current_base_url": self.base_url
                },
                "is_test_mode": True
            }
        
        if not self.api_key and not (self.username and self.secret):
            return {
                "success": False,
                "message": "[TESTMODUS] Credentials fehlen (API Key oder Username/Secret)",
                "details": {
                    "environment": "test",
                    "simulated": True,
                    "missing_field": "credentials"
                },
                "is_test_mode": True
            }
        
        # Simulate success
        return {
            "success": True,
            "message": "[TESTMODUS] EOCloud Verbindung simuliert - erfolgreich",
            "details": {
                "environment": "test",
                "simulated": True,
                "api_url": self._get_api_url()
            },
            "is_test_mode": True
        }
    
    async def push_order(self, order_data: Dict) -> Dict:
        """
        Send order to EOCloud POS using PUT /api/v1/osp
        
        IMPORTANT: EOCloud uses PUT method, not POST!
        """
        
        # TEST MODE - Simulate order push
        if self.test_mode:
            return await self._simulate_order_push(order_data)
        
        # LIVE MODE - Real API call using PUT
        api_url = self._get_api_url()
        order_number = order_data.get('order_number', 'UNKNOWN')
        
        logger.info(f"Sending order {order_number} to EOCloud: PUT {api_url}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
                headers = self._get_headers()
                payload = self._transform_order_to_eocloud(order_data)
                
                logger.info(f"EOCloud order payload: {payload}")
                
                # IMPORTANT: Use PUT method as per EOCloud API spec
                response = await client.put(
                    api_url,
                    headers=headers,
                    json=payload
                )
                
                logger.info(f"EOCloud order response: status={response.status_code}")
                
                # Check for redirects
                if response.status_code == 302:
                    return {
                        "success": False,
                        "pos_order_id": None,
                        "message": "Redirect erhalten (302) - Authentifizierung oder Endpoint prüfen",
                        "error": f"Redirect to: {response.headers.get('location', 'unknown')}",
                        "is_test_mode": False
                    }
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                if 'text/html' in content_type:
                    return {
                        "success": False,
                        "pos_order_id": None,
                        "message": "HTML-Antwort erhalten - falscher Endpoint oder Auth-Fehler",
                        "error": "Expected JSON, got HTML",
                        "is_test_mode": False
                    }
                
                if response.status_code in [200, 201, 202]:
                    # Try to parse JSON response
                    try:
                        result = response.json()
                        pos_order_id = result.get('order_id') or result.get('id') or result.get('reference')
                    except:
                        pos_order_id = f"EOC-{order_number}"
                    
                    logger.info(f"Order {order_number} successfully sent to EOCloud, POS ID: {pos_order_id}")
                    
                    return {
                        "success": True,
                        "pos_order_id": pos_order_id,
                        "message": f"Bestellung {order_number} an EOCloud gesendet",
                        "is_test_mode": False
                    }
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "pos_order_id": None,
                        "message": "Authentifizierung fehlgeschlagen (401)",
                        "error": response.text[:200] if response.text else "Unauthorized",
                        "is_test_mode": False
                    }
                elif response.status_code == 400:
                    return {
                        "success": False,
                        "pos_order_id": None,
                        "message": "Ungültige Anfrage (400) - Payload prüfen",
                        "error": response.text[:500] if response.text else "Bad Request",
                        "is_test_mode": False
                    }
                else:
                    return {
                        "success": False,
                        "pos_order_id": None,
                        "message": f"Fehler beim Senden (Status {response.status_code})",
                        "error": response.text[:500] if response.text else "Unknown error",
                        "is_test_mode": False
                    }
                    
        except httpx.TimeoutException:
            logger.error(f"EOCloud timeout for order {order_number}")
            return {
                "success": False,
                "pos_order_id": None,
                "message": "Timeout beim Senden der Bestellung (30s)",
                "error": "timeout",
                "is_test_mode": False
            }
        except Exception as e:
            logger.error(f"EOCloud push order failed for {order_number}: {str(e)}")
            return {
                "success": False,
                "pos_order_id": None,
                "message": "Fehler beim Senden der Bestellung",
                "error": str(e),
                "is_test_mode": False
            }
    
    async def _simulate_order_push(self, order_data: Dict) -> Dict:
        """Simulate order push in test mode"""
        order_number = order_data.get('order_number', 'UNKNOWN')
        
        should_fail = self.test_simulate_failure or (self.test_failure_rate > 0 and random.random() < self.test_failure_rate)
        
        if should_fail:
            logger.info(f"[TESTMODUS] Order {order_number} - Simulierter Fehler")
            return {
                "success": False,
                "pos_order_id": None,
                "message": f"[TESTMODUS] Simulierter Fehler für Bestellung {order_number}",
                "error": "Simulated failure for testing",
                "is_test_mode": True,
                "simulated": True
            }
        
        # Generate fake POS order ID
        fake_pos_id = f"TEST-{order_number}-{datetime.utcnow().strftime('%H%M%S')}"
        
        logger.info(f"[TESTMODUS] Order {order_number} -> POS ID: {fake_pos_id}")
        
        return {
            "success": True,
            "pos_order_id": fake_pos_id,
            "message": f"[TESTMODUS] Bestellung {order_number} simuliert gesendet",
            "is_test_mode": True,
            "simulated": True,
            "details": {
                "items_count": len(order_data.get('items', [])),
                "total": order_data.get('total', 0),
                "api_url": self._get_api_url()
            }
        }
    
    def _get_headers(self) -> Dict:
        """Get HTTP headers for EOCloud API requests"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # EOCloud uses API_KEY header for authentication
        # The API expects the key in a header named "API_KEY" or "api_key"
        if self.api_key:
            # Try multiple header formats that EOCloud might accept
            headers["API_KEY"] = self.api_key
            headers["api_key"] = self.api_key
            headers["X-API-KEY"] = self.api_key
        
        # Also support Basic Auth as fallback
        if self.username and self.secret:
            import base64
            credentials = f"{self.username}:{self.secret}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
        
        logger.info(f"EOCloud headers (masked): API_KEY={'SET' if self.api_key else 'NOT SET'}, Basic Auth={'SET' if (self.username and self.secret) else 'NOT SET'}")
        
        return headers
    
    def _transform_order_to_eocloud(self, order_data: Dict) -> Dict:
        """
        Transform ZOZO order format to EOCloud OSP format
        
        EOCloud OSP API required fields:
        - version: Integer (API version)
        - id: Order ID
        - ordertime: Order timestamp (ISO format)
        - deliverytime: Delivery timestamp (ISO format)
        - orderprice: Total price
        - orderdiscount: Discount amount
        - payment: Payment info object
        - customer: object with street, zip, location
        - items: array with count (not quantity)
        """
        import uuid
        from datetime import datetime, timedelta
        
        # Parse delivery address for street, zip, location
        delivery_address = order_data.get('delivery_address', '')
        address_parts = delivery_address.split(',') if delivery_address else []
        
        street = address_parts[0].strip() if len(address_parts) > 0 else ''
        zip_location = address_parts[1].strip() if len(address_parts) > 1 else ''
        
        # Try to split zip and location (e.g., "24558 Henstedt-Ulzburg")
        zip_parts = zip_location.split(' ', 1) if zip_location else []
        zip_code = zip_parts[0] if len(zip_parts) > 0 else ''
        location = zip_parts[1] if len(zip_parts) > 1 else zip_location
        
        # Build items list with EOCloud required fields
        items = []
        for item in order_data.get('items', []):
            eocloud_item = {
                "name": item.get('name', ''),
                "count": item.get('quantity', 1),  # EOCloud uses "count" not "quantity"
                "price": float(item.get('price', 0)),
            }
            
            # Add customizations if present
            customizations = item.get('customizations', [])
            if customizations:
                eocloud_item["options"] = customizations
            
            items.append(eocloud_item)
        
        # Current time for ordertime, delivery time +30 min
        # EOCloud expects ISO 8601 string format: "2025-12-17T16:30:00"
        now = datetime.utcnow()
        delivery_time = now + timedelta(minutes=30)
        
        # Format as ISO strings
        ordertime_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        deliverytime_str = delivery_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Payment type mapping - EOCloud uses integers:
        # 0 = Cash, 1 = Card, etc.
        payment_method = order_data.get('payment_method', 'cash')
        payment_type = 0 if payment_method == 'cash' else 1  # Integer type required
        
        # Build the OSP payload with all required EOCloud fields
        payload = {
            "version": 1,  # Required by EOCloud - must be INTEGER
            "id": order_data.get('order_number', str(uuid.uuid4())),  # Required
            "ordertime": ordertime_str,  # ISO 8601 string
            "deliverytime": deliverytime_str,  # ISO 8601 string
            "orderprice": float(order_data.get('total', 0)),  # Required
            "orderdiscount": 0.0,  # Required
            "payment": {
                "type": payment_type,  # Integer: 0=cash, 1=card
                "amount": float(order_data.get('total', 0)),
                "provider": "",  # Required by EOCloud
                "transactionid": "",  # Required by EOCloud
                "prepaid": 0.0  # Required by EOCloud - Number, 0.0 = not prepaid
            },
            "customer": {
                "name": order_data.get('customer_name', ''),
                "phone": order_data.get('customer_phone', ''),
                "email": order_data.get('customer_email', ''),
                "street": street,  # Required
                "zip": zip_code,  # Required
                "location": location  # Required (city)
            },
            "items": items,
            "deliveryType": order_data.get('delivery_type', 'delivery'),
            "notes": order_data.get('notes', '')
        }
        
        logger.info(f"EOCloud payload: {payload}")
        
        return payload

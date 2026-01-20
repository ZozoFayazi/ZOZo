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
    Connector for ExpertOrder / EOCloud OSP API
    
    Official API Documentation: https://s1.eocloud.de/{merchant_id}/api/doc/osp
    - Endpoint: PUT /api/v1/osp (for orders)
    - Base URL: https://s1.eocloud.de/{merchant_id}  (NOT osp.expertorder.de!)
    - Auth: API_KEY header
    
    IMPORTANT: Each merchant has their own base URL with their merchant_id!
    Example: https://s1.eocloud.de/c102285/api/v1/osp
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # DEBUG: Log the entire config
        logger.info(f"ExpertOrder __init__ called with config keys: {list(config.keys())}")
        logger.info(f"ExpertOrder config base_url: {config.get('base_url')}")
        logger.info(f"ExpertOrder config merchant_id: {config.get('merchant_id')}")
        
        # CRITICAL: Base URL MUST include the merchant_id!
        # Format: https://s1.eocloud.de/{merchant_id}
        # The merchant_id (e.g., "c102285") is provided by ExpertOrder for each location
        self.merchant_id = config.get('merchant_id', '')
        
        if config.get('base_url'):
            # Use provided base_url if explicitly set
            self.base_url = config.get('base_url').rstrip('/')
        elif self.merchant_id:
            # Construct base_url from merchant_id
            self.base_url = f"https://s1.eocloud.de/{self.merchant_id}"
        else:
            # Fallback - will likely fail without merchant_id
            self.base_url = "https://s1.eocloud.de"
            logger.warning("ExpertOrder: No merchant_id provided! API calls will likely fail.")
        
        # API endpoint path
        self.api_path = "/api/v1/osp"
        
        # Broker name - must match EXACTLY what's registered in ExpertOrder
        self.broker_name = config.get('broker_name', 'ZOZO-Burger')
        
        # Authentication
        self.api_key = config.get('api_key')
        self.merchant_id = config.get('merchant_id', '')
        self.username = config.get('username')  # Legacy support
        self.secret = config.get('secret')  # Legacy support
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
        
        # Check if base_url looks valid (must include merchant_id)
        if not self.base_url or not self.merchant_id:
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
                
                # Log response body for debugging
                try:
                    response_text = response.text[:500]  # First 500 chars
                    logger.info(f"EOCloud response body: {response_text}")
                except:
                    pass
                
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
        
        # Build items list with ExpertOrder required format
        # CRITICAL: Menüs müssen in Bestandteile AUFGESPALTEN werden (flatten)
        # Nicht Parent-Child, sondern separate Top-Level Items!
        items = []
        
        for item in order_data.get('items', []):
            # Check if this is a menu
            is_menu = 'menü' in item.get('name', '').lower() or 'menu' in item.get('name', '').lower()
            
            if is_menu:
                # MENÜ-MODUS: Zerlege in einzelne Artikel
                # 1. Hauptprodukt (ohne "Menü" im Namen)
                base_name = item.get('name', '').replace(' Menü', '').replace(' Menu', '')
                
                items.append({
                    "uid": item.get('menu_item_id', ''),
                    "name": base_name,  # z.B. "Smash Bacon" statt "Smash Bacon Menü"
                    "count": item.get('quantity', 1),
                    "price": float(item.get('price', 0)),  # Gesamtpreis bleibt beim Hauptartikel
                    "items": []
                })
                
                # 2. NEUE MODIFIER SYSTEM: Beilage + Getränk aus modifiers{}
                modifiers = item.get('modifiers', {})
                if modifiers:
                    # modifiers format: {"menu_beilage": {"id": "...", "name": "Pommes Normal", "price": 0, "pos_item_id": "..."}}
                    for group_id, modifier_data in modifiers.items():
                        if isinstance(modifier_data, dict):
                            modifier_name = modifier_data.get('name', '')
                            modifier_price = modifier_data.get('price', 0.0)
                            pos_item_id = modifier_data.get('pos_item_id', '')
                            
                            items.append({
                                "uid": pos_item_id or f"MODIFIER-{group_id}",
                                "name": modifier_name,
                                "count": item.get('quantity', 1),
                                "price": float(modifier_price),
                                "group": "menu_component",
                                "type": "addon"
                            })
                
                # 2b. LEGACY: String-basierte customizations (für alte Orders)
                customizations = item.get('customizations', [])
                for custom in customizations:
                    if isinstance(custom, str):
                        # Entferne "+ " Prefix für sauberen Namen
                        clean_name = custom.replace('+ ', '').replace('+', '').strip()
                        
                        # Skip if already covered by modifiers
                        if not any(clean_name in mod_data.get('name', '') for mod_data in modifiers.values() if isinstance(mod_data, dict)):
                            items.append({
                                "uid": f"CUSTOM-{clean_name[:20].replace(' ', '-').upper()}",
                                "name": clean_name,
                                "count": item.get('quantity', 1),
                                "price": 0.0,
                                "group": "menu_component",
                                "type": "addon"
                            })
                
                # 3. Extras auch als separate Items
                extras = item.get('extras', [])
                for extra in extras:
                    extra_name = extra.get('name', extra) if isinstance(extra, dict) else extra
                    extra_price = extra.get('price', 0) if isinstance(extra, dict) else 0
                    
                    items.append({
                        "uid": f"EXTRA-{extra_name[:20].replace(' ', '-').upper()}",
                        "name": extra_name,
                        "count": item.get('quantity', 1),
                        "price": float(extra_price),
                        "group": "extra",
                        "type": "addon"
                    })
                
                # 4. Removals
                removals = item.get('removed_ingredients', [])
                for removal in removals:
                    items.append({
                        "uid": f"REMOVE-{removal[:20].replace(' ', '-').upper()}",
                        "name": f"- Ohne {removal}",
                        "count": item.get('quantity', 1),
                        "price": 0.0,
                        "group": "removal",
                        "type": "modifier"
                    })
            
            else:
                # KEIN MENÜ: Normale Artikel-Struktur
                # 1. Main product
                main_item = {
                    "uid": item.get('menu_item_id', ''),
                    "name": item.get('name', ''),
                    "count": item.get('quantity', 1),
                    "price": float(item.get('price', 0)),
                    "items": []
                }
                items.append(main_item)
                
                # 2. Customizations als separate Top-Level Items
                customizations = item.get('customizations', [])
                for custom in customizations:
                    items.append({
                        "uid": f"MODIFIER-{custom[:20].replace(' ', '-').upper()}",
                        "name": custom,
                        "count": 1,
                        "price": 0.0,
                        "group": "modifier",
                        "type": "addon"
                    })
                
                # 3. Extras
                extras = item.get('extras', [])
                for extra in extras:
                    extra_name = extra.get('name', extra) if isinstance(extra, dict) else extra
                    extra_price = extra.get('price', 0) if isinstance(extra, dict) else 0
                    
                    items.append({
                        "uid": f"EXTRA-{extra_name[:20].replace(' ', '-').upper()}",
                        "name": extra_name,
                        "count": 1,
                        "price": float(extra_price),
                        "group": "extra",
                        "type": "addon"
                    })
                
                # 4. Removals
                removals = item.get('removed_ingredients', [])
                for removal in removals:
                    items.append({
                        "uid": f"REMOVE-{removal[:20].replace(' ', '-').upper()}",
                        "name": f"- Ohne {removal}",
                        "count": 1,
                        "price": 0.0,
                        "group": "removal",
                        "type": "modifier"
                    })
        
        # Current time for ordertime & deliverytime
        # ExpertOrder interpretiert Zeiten MIT Z-Suffix als UTC
        # Also: 18:50Z wird zu 19:50 MEZ im POS
        # Lösung: Um 18:50 MEZ zu erreichen, müssen wir 17:50Z senden
        
        now = datetime.utcnow()
        
        # Check if scheduled time is provided
        scheduled_time_str = order_data.get('scheduled_time')
        
        if scheduled_time_str:
            # Zeitbestellung: deliverytime = gewünschte Zeit MINUS 1 Stunde (wegen MEZ)
            ordertime_str = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            
            # Parse scheduled time (expected: "2026-01-08T18:50:00" = lokale MEZ Zeit)
            # Wir müssen 1 Stunde abziehen um UTC zu bekommen
            try:
                # Parse without timezone
                if 'T' in scheduled_time_str:
                    time_part = scheduled_time_str.split('T')[1].replace('Z', '').split('.')[0]
                    date_part = scheduled_time_str.split('T')[0]
                    
                    # Parse hour
                    hour = int(time_part.split(':')[0])
                    minute = int(time_part.split(':')[1])
                    
                    # Subtract 1 hour for UTC (MEZ = UTC+1)
                    hour_utc = hour - 1
                    if hour_utc < 0:
                        hour_utc = 23
                    
                    deliverytime_str = f"{date_part}T{hour_utc:02d}:{minute:02d}:00.000Z"
                else:
                    deliverytime_str = scheduled_time_str
            except:
                deliverytime_str = scheduled_time_str
        else:
            # Sofort-Bestellung: deliverytime = ordertime (UTC)
            ordertime_str = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            deliverytime_str = ordertime_str  # GLEICH = sofortige Bestellung!
        
        # Payment type mapping - ExpertOrder spec:
        # 0 = Barzahlung (Cash)
        # 1 = EC mit PIN vor Ort
        # 3 = Onlinezahlung (PayPal, etc.)
        payment_method = order_data.get('payment_method', 'cash')
        payment_type = 0  # Default: Barzahlung
        payment_provider = ""
        transaction_id = ""
        prepaid_amount = 0
        
        if payment_method == 'cash':
            payment_type = 0  # Barzahlung
        elif payment_method == 'card':
            payment_type = 1  # EC mit PIN vor Ort
        elif payment_method == 'paypal':
            payment_type = 3  # Onlinezahlung
            payment_provider = "PayPal"
            transaction_id = order_data.get('paypal_transaction_id', '')
            prepaid_amount = float(order_data.get('total', 0))  # Bei PayPal: Volle Summe vorausbezahlt
        
        # notification Feld: true = ABHOLUNG, false = LIEFERUNG
        # Laut API: "Gibt an, ob der Kunde keine Lieferung wünscht, sondern selbst abholen möchte"
        is_pickup = order_data.get('delivery_type') == 'pickup'
        
        # Build the OSP payload with ALL required ExpertOrder fields (from official API doc)
        payload = {
            "version": 0,  # Required - Integer (0 basierend auf erfolgreichem Test)
            "broker": self.broker_name,  # Required - MUST match registered name EXACTLY
            "fromMobile": False,  # Optional
            "clientIp": "127.0.0.1",  # Optional
            "id": order_data.get('order_number', str(uuid.uuid4())),  # Required - Order ID
            "ordertime": ordertime_str,  # Required - ISO 8601
            "deliverytime": deliverytime_str,  # Required - GLEICH wie ordertime = SOFORT (keine Zeitbestellung!)
            "customerinfo": order_data.get('notes') or '',  # Must be string, not None
            "orderprice": float(order_data.get('total', 0)),  # Required
            "orderdiscount": 0,  # Required - must be 0 or negative
            "bonuscard": "",  # Optional
            "notification": is_pickup,  # TRUE = ABHOLUNG, FALSE = LIEFERUNG
            "deliverycost": 0,  # Optional - delivery fee
            "tip": 0,  # Optional
            "customer": {
                "phone": order_data.get('customer_phone', ''),
                "email": order_data.get('customer_email') or 'noreply@zozo-burger.de',  # Must be valid email
                "name": order_data.get('customer_name', ''),
                "street": street,  # Required
                "zip": zip_code,  # Required
                "location": location  # Required (city)
            },
            "payment": {
                "type": payment_type,  # Required - Integer: 0=cash, 1=card, 3=online
                "provider": payment_provider,  # "PayPal" für type=3
                "transactionid": transaction_id,  # PayPal Transaction ID
                "prepaid": prepaid_amount  # Bei PayPal: Volle Summe
            },
            "items": items  # Required - array of items
        }
        
        logger.info(f"ExpertOrder payload: {payload}")
        
        return payload

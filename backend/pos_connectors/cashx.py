"""Cash-X POS Connector - Cloud Version für ZOZO Burger"""
import httpx
import logging
import uuid
import random
from typing import Dict
from datetime import datetime, timezone
from .base import BasePOSConnector

logger = logging.getLogger(__name__)


class CashXConnector(BasePOSConnector):
    """
    Connector für Cash-X POS System (Cloud)
    
    API Endpoints:
    - GET  /api/health  - Verbindungstest
    - POST /api/orders  - Bestellung senden
    
    Authentifizierung: X-API-Key Header
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Cloud Base URL (konfigurierbar pro Standort)
        self.base_url = config.get('base_url', '').rstrip('/')
        
        # Authentifizierung
        self.api_key = config.get('api_key', '')
        
        # Terminal/Kassen Identifikation
        self.terminal_id = config.get('terminal_id', 'KASSE-1')
        
        # Test-Modus (simuliert Bestellungen ohne echte API-Aufrufe)
        self.test_mode = config.get('test_mode', True)
        
        # Test-Modus Einstellungen
        self.test_simulate_failure = config.get('test_simulate_failure', False)
        self.test_failure_rate = config.get('test_failure_rate', 0.0)
        
        logger.info(f"Cash-X Connector initialisiert: base_url={self.base_url}, terminal={self.terminal_id}, test_mode={self.test_mode}")
    
    def _get_headers(self) -> Dict:
        """HTTP Headers für Cash-X API"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Key": self.api_key,
            "X-Terminal-ID": self.terminal_id,
            "X-Request-ID": str(uuid.uuid4())
        }
    
    async def test_connection(self) -> Dict:
        """
        Testet die Verbindung zur Cash-X API
        
        Returns:
            Dict mit success, message, details, is_test_mode
        """
        
        # TEST-MODUS: Simulation
        if self.test_mode:
            return await self._simulate_connection_test()
        
        # LIVE-MODUS: Echter API-Aufruf
        if not self.base_url:
            return {
                "success": False,
                "message": "Cash-X Base-URL nicht konfiguriert",
                "details": {"error": "missing_base_url"},
                "is_test_mode": False
            }
        
        if not self.api_key:
            return {
                "success": False,
                "message": "Cash-X API-Key nicht konfiguriert",
                "details": {"error": "missing_api_key"},
                "is_test_mode": False
            }
        
        api_url = f"{self.base_url}/api/cashx/health"
        logger.info(f"Cash-X Verbindungstest: GET {api_url}")
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(api_url, headers=self._get_headers())
                
                logger.info(f"Cash-X Antwort: status={response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        return {
                            "success": True,
                            "message": f"Verbindung zu Cash-X erfolgreich ({data.get('terminal', 'OK')})",
                            "details": {
                                "status": data.get('status', 'ok'),
                                "terminal": data.get('terminal'),
                                "version": data.get('version'),
                                "api_url": api_url
                            },
                            "is_test_mode": False
                        }
                    except:
                        return {
                            "success": True,
                            "message": "Verbindung zu Cash-X erfolgreich",
                            "details": {"api_url": api_url},
                            "is_test_mode": False
                        }
                
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "message": "Authentifizierung fehlgeschlagen - API-Key prüfen",
                        "details": {"status_code": 401, "api_url": api_url},
                        "is_test_mode": False
                    }
                
                elif response.status_code == 403:
                    return {
                        "success": False,
                        "message": "Zugriff verweigert - Terminal-ID prüfen",
                        "details": {"status_code": 403, "api_url": api_url},
                        "is_test_mode": False
                    }
                
                elif response.status_code == 404:
                    return {
                        "success": False,
                        "message": "Cash-X Endpoint nicht gefunden - URL prüfen",
                        "details": {"status_code": 404, "api_url": api_url},
                        "is_test_mode": False
                    }
                
                else:
                    return {
                        "success": False,
                        "message": f"Unerwarteter Status: {response.status_code}",
                        "details": {
                            "status_code": response.status_code,
                            "api_url": api_url,
                            "response": response.text[:200] if response.text else ""
                        },
                        "is_test_mode": False
                    }
        
        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "Verbindungs-Timeout (15s) - Server nicht erreichbar",
                "details": {"error": "timeout", "api_url": api_url},
                "is_test_mode": False
            }
        
        except httpx.ConnectError as e:
            return {
                "success": False,
                "message": "Verbindungsfehler - Server nicht erreichbar",
                "details": {"error": str(e), "api_url": api_url},
                "is_test_mode": False
            }
        
        except Exception as e:
            logger.error(f"Cash-X Verbindungstest fehlgeschlagen: {str(e)}")
            return {
                "success": False,
                "message": f"Fehler: {str(e)}",
                "details": {"error": str(e), "api_url": api_url},
                "is_test_mode": False
            }
    
    async def _simulate_connection_test(self) -> Dict:
        """Simuliert Verbindungstest im Test-Modus"""
        
        if self.test_simulate_failure:
            return {
                "success": False,
                "message": "[TESTMODUS] Simulierter Verbindungsfehler",
                "details": {"simulated": True, "reason": "test_simulate_failure=True"},
                "is_test_mode": True
            }
        
        if not self.base_url:
            return {
                "success": False,
                "message": "[TESTMODUS] Base-URL nicht konfiguriert",
                "details": {"simulated": True, "missing": "base_url"},
                "is_test_mode": True
            }
        
        if not self.api_key:
            return {
                "success": False,
                "message": "[TESTMODUS] API-Key nicht konfiguriert",
                "details": {"simulated": True, "missing": "api_key"},
                "is_test_mode": True
            }
        
        return {
            "success": True,
            "message": f"[TESTMODUS] Cash-X Verbindung simuliert - erfolgreich",
            "details": {
                "simulated": True,
                "terminal": self.terminal_id,
                "api_url": f"{self.base_url}/api/health"
            },
            "is_test_mode": True
        }
    
    async def push_order(self, order_data: Dict) -> Dict:
        """
        Sendet Bestellung an Cash-X
        
        Args:
            order_data: Bestelldaten von ZOZO Burger
        
        Returns:
            Dict mit success, pos_order_id, message, is_test_mode
        """
        
        order_number = order_data.get('order_number', 'UNKNOWN')
        
        # TEST-MODUS: Simulation
        if self.test_mode:
            return await self._simulate_order_push(order_data)
        
        # LIVE-MODUS: Echter API-Aufruf
        if not self.base_url or not self.api_key:
            return {
                "success": False,
                "pos_order_id": None,
                "message": "Cash-X nicht konfiguriert (URL oder API-Key fehlt)",
                "error": "missing_config",
                "is_test_mode": False
            }
        
        api_url = f"{self.base_url}/api/cashx/orders"
        logger.info(f"Cash-X Bestellung senden: POST {api_url} - {order_number}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = self._transform_order(order_data)
                
                logger.info(f"Cash-X Payload: {payload}")
                
                response = await client.post(
                    api_url,
                    headers=self._get_headers(),
                    json=payload
                )
                
                logger.info(f"Cash-X Antwort: status={response.status_code}")
                
                if response.status_code in [200, 201]:
                    try:
                        result = response.json()
                        pos_order_id = result.get('order_id') or result.get('orderId') or f"CX-{order_number}"
                        
                        logger.info(f"Bestellung {order_number} erfolgreich an Cash-X gesendet: {pos_order_id}")
                        
                        return {
                            "success": True,
                            "pos_order_id": pos_order_id,
                            "message": f"Bestellung {order_number} an Cash-X gesendet",
                            "is_test_mode": False
                        }
                    except:
                        return {
                            "success": True,
                            "pos_order_id": f"CX-{order_number}",
                            "message": f"Bestellung {order_number} an Cash-X gesendet",
                            "is_test_mode": False
                        }
                
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "pos_order_id": None,
                        "message": "Authentifizierung fehlgeschlagen",
                        "error": "unauthorized",
                        "is_test_mode": False
                    }
                
                elif response.status_code == 400:
                    error_msg = "Ungültige Bestelldaten"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error') or error_data.get('message') or error_msg
                    except:
                        pass
                    return {
                        "success": False,
                        "pos_order_id": None,
                        "message": f"Fehler: {error_msg}",
                        "error": error_msg,
                        "is_test_mode": False
                    }
                
                else:
                    return {
                        "success": False,
                        "pos_order_id": None,
                        "message": f"Fehler beim Senden (Status {response.status_code})",
                        "error": response.text[:200] if response.text else "unknown",
                        "is_test_mode": False
                    }
        
        except httpx.TimeoutException:
            logger.error(f"Cash-X Timeout für Bestellung {order_number}")
            return {
                "success": False,
                "pos_order_id": None,
                "message": "Timeout beim Senden (30s)",
                "error": "timeout",
                "is_test_mode": False
            }
        
        except Exception as e:
            logger.error(f"Cash-X Fehler für {order_number}: {str(e)}")
            return {
                "success": False,
                "pos_order_id": None,
                "message": f"Fehler: {str(e)}",
                "error": str(e),
                "is_test_mode": False
            }
    
    async def _simulate_order_push(self, order_data: Dict) -> Dict:
        """Simuliert Bestellübermittlung im Test-Modus"""
        
        order_number = order_data.get('order_number', 'UNKNOWN')
        
        # Simuliere Fehler wenn gewünscht
        should_fail = self.test_simulate_failure or (
            self.test_failure_rate > 0 and random.random() < self.test_failure_rate
        )
        
        if should_fail:
            logger.info(f"[TESTMODUS] Bestellung {order_number} - Simulierter Fehler")
            return {
                "success": False,
                "pos_order_id": None,
                "message": f"[TESTMODUS] Simulierter Fehler für {order_number}",
                "error": "simulated_failure",
                "is_test_mode": True,
                "simulated": True
            }
        
        # Simuliere erfolgreiche Bestellung
        fake_pos_id = f"CX-TEST-{order_number}-{datetime.now(timezone.utc).strftime('%H%M%S')}"
        
        logger.info(f"[TESTMODUS] Bestellung {order_number} -> {fake_pos_id}")
        
        return {
            "success": True,
            "pos_order_id": fake_pos_id,
            "message": f"[TESTMODUS] Bestellung {order_number} simuliert gesendet",
            "is_test_mode": True,
            "simulated": True,
            "details": {
                "items_count": len(order_data.get('items', [])),
                "total": order_data.get('total', 0),
                "terminal": self.terminal_id
            }
        }
    
    def _transform_order(self, order_data: Dict) -> Dict:
        """
        Transformiert ZOZO Burger Bestellung zu Cash-X Format
        
        Args:
            order_data: ZOZO Burger Bestellformat
        
        Returns:
            Cash-X API Payload
        """
        
        # Items transformieren
        items = []
        for item in order_data.get('items', []):
            items.append({
                "name": item.get('name', ''),
                "quantity": item.get('quantity', 1),
                "price": float(item.get('price', 0))
            })
        
        # Liefer-/Abholtyp
        delivery_type = order_data.get('delivery_type', 'delivery')
        if order_data.get('is_pickup'):
            delivery_type = 'pickup'
        
        # Cash-X Payload
        payload = {
            "order_number": order_data.get('order_number', ''),
            "terminal_id": self.terminal_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "items": items,
            "subtotal": float(order_data.get('subtotal', order_data.get('total', 0))),
            "delivery_fee": float(order_data.get('delivery_fee', 0)),
            "discount": float(order_data.get('discount', 0)),
            "total": float(order_data.get('total', 0)),
            "payment_method": order_data.get('payment_method', 'cash'),
            "customer": {
                "name": order_data.get('customer_name', ''),
                "phone": order_data.get('customer_phone', ''),
                "email": order_data.get('customer_email', ''),
                "address": order_data.get('delivery_address', '')
            },
            "delivery_type": delivery_type,
            "notes": order_data.get('notes', '')
        }
        
        return payload

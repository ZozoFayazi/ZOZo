"""ExpertOrder POS Connector"""
import httpx
import logging
from typing import Dict
from .base import BasePOSConnector

logger = logging.getLogger(__name__)

class ExpertOrderConnector(BasePOSConnector):
    """Connector for ExpertOrder POS system"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://api.expertorder.com/v1')
        self.api_key = config.get('api_key')
        self.merchant_id = config.get('merchant_id')
        self.username = config.get('username')
        self.secret = config.get('secret')
        self.environment = config.get('environment', 'test')  # 'test' or 'live'
    
    async def test_connection(self) -> Dict:
        """Test connection to ExpertOrder API"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = self._get_headers()
                
                # Try to ping the API or get merchant info
                response = await client.get(
                    f"{self.base_url}/merchant/{self.merchant_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "message": "Verbindung erfolgreich",
                        "details": {
                            "environment": self.environment,
                            "merchant_id": self.merchant_id
                        }
                    }
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "message": "Authentifizierung fehlgeschlagen",
                        "details": {"status_code": 401}
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Verbindung fehlgeschlagen (Status {response.status_code})",
                        "details": {"status_code": response.status_code}
                    }
        except httpx.TimeoutException:
            return {
                "success": False,
                "message": "Verbindungs-Timeout",
                "details": {"error": "timeout"}
            }
        except Exception as e:
            logger.error(f"ExpertOrder connection test failed: {str(e)}")
            return {
                "success": False,
                "message": f"Fehler: {str(e)}",
                "details": {"error": str(e)}
            }
    
    async def push_order(self, order_data: Dict) -> Dict:
        """Send order to ExpertOrder POS"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = self._get_headers()
                
                # Transform order data to ExpertOrder format
                payload = self._transform_order(order_data)
                
                response = await client.post(
                    f"{self.base_url}/orders",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return {
                        "success": True,
                        "pos_order_id": result.get('order_id'),
                        "message": "Bestellung an ExpertOrder gesendet"
                    }
                else:
                    error_detail = response.text
                    return {
                        "success": False,
                        "pos_order_id": None,
                        "message": f"Fehler beim Senden (Status {response.status_code})",
                        "error": error_detail
                    }
        except Exception as e:
            logger.error(f"ExpertOrder push order failed: {str(e)}")
            return {
                "success": False,
                "pos_order_id": None,
                "message": "Fehler beim Senden der Bestellung",
                "error": str(e)
            }
    
    def _get_headers(self) -> Dict:
        """Get HTTP headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.username and self.secret:
            # Basic Auth
            import base64
            credentials = f"{self.username}:{self.secret}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
        
        return headers
    
    def _transform_order(self, order_data: Dict) -> Dict:
        """Transform ZOZO order format to ExpertOrder format"""
        return {
            "merchant_id": self.merchant_id,
            "order_number": order_data.get('order_number'),
            "customer": {
                "email": order_data.get('customer_email'),
                "name": order_data.get('customer_name', ''),
                "phone": order_data.get('customer_phone', '')
            },
            "items": [
                {
                    "product_id": item.get('product_id'),
                    "name": item.get('name'),
                    "quantity": item.get('quantity'),
                    "price": item.get('price'),
                    "customizations": item.get('customizations', [])
                }
                for item in order_data.get('items', [])
            ],
            "total": order_data.get('total'),
            "delivery_type": order_data.get('delivery_type', 'delivery'),
            "delivery_address": order_data.get('delivery_address'),
            "payment_method": order_data.get('payment_method'),
            "notes": order_data.get('notes', '')
        }

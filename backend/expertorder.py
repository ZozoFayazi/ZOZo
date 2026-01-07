"""
ExpertOrder Integration Module
Handles communication with ExpertOrder POS system via Push API
"""
import httpx
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel


# ExpertOrder Request Models (based on API spec)
class EOCustomer(BaseModel):
    """ExpertOrder customer data"""
    phone: str
    email: Optional[str] = ""
    companyname: Optional[str] = ""
    departmentname: Optional[str] = ""
    name: str
    street: str
    zip: str
    location: str  # City
    addressinfo: Optional[str] = ""


class EOPayment(BaseModel):
    """ExpertOrder payment data"""
    type: int  # 1=bar, 2=EC-Karte, 3=online bezahlt, 4=Gutschein
    provider: Optional[str] = ""
    transactionid: Optional[str] = ""
    prepaid: float = 0  # Bei Online-Zahlung: Betrag der schon bezahlt wurde


class EOItem(BaseModel):
    """ExpertOrder item (product or extra)"""
    count: int
    name: str
    price: float
    items: List['EOItem'] = []  # Nested items (extras, variants)


EOItem.model_rebuild()  # Required for self-referencing model


class EOOrder(BaseModel):
    """Complete ExpertOrder order format"""
    version: int = 1
    broker: str  # Name of the online shop provider
    fromMobile: bool = False
    clientIp: Optional[str] = ""
    id: str  # Unique order ID from OSP
    oldid: Optional[str] = ""  # If this is an order modification
    ordertime: str  # ISO format: "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
    deliverytime: str  # ISO format
    customerinfo: Optional[str] = ""
    orderprice: float
    orderdiscount: float = 0  # Must be negative if discount
    bonuscard: Optional[str] = ""
    notification: bool = False  # True = pickup, False = delivery
    deliverycost: float = 0
    tip: float = 0
    customer: EOCustomer
    payment: EOPayment
    items: List[EOItem]


class ExpertOrderClient:
    """Client for communicating with ExpertOrder EOCloud API"""
    
    # NEW API Configuration (EOCloud v1.3.2)
    # Each merchant has their own base URL: https://s1.eocloud.de/{merchant_id}
    # API Endpoint: PUT /api/v1/osp
    
    def __init__(self, api_key: str = None, use_test_mode: bool = False, merchant_id: str = "c102285", base_url: str = None):
        """
        Initialize ExpertOrder EOCloud client
        
        Args:
            api_key: ExpertOrder API key for the merchant
            use_test_mode: If True, use test mode (currently same endpoint)
            merchant_id: ExpertOrder merchant ID (e.g., "c102285")
            base_url: Full base URL (e.g., "https://s1.eocloud.de/c102285")
        """
        self.api_key = api_key
        self.merchant_id = merchant_id
        
        # Use provided base_url or construct from merchant_id
        if base_url:
            self.base_url = base_url.rstrip('/')
        else:
            self.base_url = f"https://s1.eocloud.de/{merchant_id}"
        
        self.endpoint = f"{self.base_url}/api/v1/osp"
        self.use_test_mode = use_test_mode
        self.timeout = 30.0
    
    async def send_order(self, order: EOOrder) -> Dict[str, Any]:
        """
        Send order to ExpertOrder
        
        Args:
            order: EOOrder object
            
        Returns:
            Dict with status and response data
            
        Raises:
            Exception: If API call fails
        """
        headers = {
            "API_KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            # Dump model and remove empty strings (ExpertOrder doesn't accept them)
            order_dict = order.model_dump(exclude_none=True)
            # Remove empty strings from dict recursively
            def remove_empty_strings(d):
                if isinstance(d, dict):
                    return {k: remove_empty_strings(v) for k, v in d.items() if v != ''}
                elif isinstance(d, list):
                    return [remove_empty_strings(item) for item in d]
                return d
            order_dict = remove_empty_strings(order_dict)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    self.endpoint,  # KORRIGIERT: Muss endpoint sein, nicht base_url!
                    json=order_dict,
                    headers=headers
                )
                
                # Handle different status codes
                if response.status_code == 200:
                    return {
                        "success": True,
                        "status_code": 200,
                        "message": "Order successfully sent to ExpertOrder"
                    }
                elif response.status_code == 400:
                    return {
                        "success": False,
                        "status_code": 400,
                        "message": "Header parameters incomplete/not set",
                        "error": "INVALID_HEADERS"
                    }
                elif response.status_code == 403:
                    return {
                        "success": False,
                        "status_code": 403,
                        "message": "Broker unknown",
                        "error": "UNKNOWN_BROKER"
                    }
                elif response.status_code == 406:
                    return {
                        "success": False,
                        "status_code": 406,
                        "message": "JSON format incompatible",
                        "error": "INVALID_FORMAT"
                    }
                elif response.status_code == 408:
                    return {
                        "success": False,
                        "status_code": 408,
                        "message": "Target ExpertOrder not connected to service",
                        "error": "NOT_CONNECTED"
                    }
                elif response.status_code == 412:
                    return {
                        "success": False,
                        "status_code": 412,
                        "message": "API key unknown",
                        "error": "INVALID_API_KEY"
                    }
                elif response.status_code == 422:
                    try:
                        error_data = response.json() if response.text else {}
                    except:
                        error_data = {"raw_response": response.text}
                    return {
                        "success": False,
                        "status_code": 422,
                        "message": "Incomplete or incorrect order data",
                        "error": "INVALID_ORDER_DATA",
                        "details": error_data
                    }
                elif response.status_code == 503:
                    return {
                        "success": False,
                        "status_code": 503,
                        "message": "ExpertOrder cannot process order at the moment",
                        "error": "SERVICE_UNAVAILABLE"
                    }
                else:
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "message": f"Unexpected status code: {response.status_code}",
                        "error": "UNKNOWN_ERROR",
                        "raw_response": response.text[:500] if response.text else None
                    }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "status_code": 0,
                "message": "Request timeout",
                "error": "TIMEOUT"
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 0,
                "message": f"Exception: {str(e)}",
                "error": "EXCEPTION"
            }


def map_zozo_order_to_expertorder(zozo_order: Dict, location: Dict) -> EOOrder:
    """
    Map ZOZO order format to ExpertOrder format
    
    Args:
        zozo_order: Order dict from ZOZO database
        location: Location dict from ZOZO database
        
    Returns:
        EOOrder object ready to send
    """
    # Get customer data (check both 'customer' and 'customer_details')
    customer_details = zozo_order.get('customer', zozo_order.get('customer_details', {}))
    
    # Map customer data
    eo_customer = EOCustomer(
        phone=customer_details.get('phone', ''),
        email=customer_details.get('email', ''),
        name=customer_details.get('name', ''),
        street=customer_details.get('address', ''),
        zip=customer_details.get('postal_code', ''),
        location=customer_details.get('city', location.get('city', '')),
        addressinfo=customer_details.get('notes', '')
    )
    
    # Map payment data
    payment_method = zozo_order.get('payment_method', 'cash')
    payment_type_map = {
        'cash': 1,
        'card': 2,
        'online': 3,
        'voucher': 4
    }
    
    eo_payment = EOPayment(
        type=payment_type_map.get(payment_method, 1),
        provider=zozo_order.get('payment_provider', ''),
        transactionid=zozo_order.get('payment_transaction_id', ''),
        prepaid=zozo_order.get('total', 0) if payment_method == 'online' else 0
    )
    
    # Map items (with nested structure for extras)
    eo_items = []
    for item in zozo_order.get('items', []):
        # Main item
        item_price = item.get('price', 0)
        
        # Nested extras/customizations
        nested_items = []
        if 'extras' in item and item['extras']:
            for extra in item['extras']:
                nested_items.append(EOItem(
                    count=1,
                    name=extra.get('name', ''),
                    price=extra.get('price', 0),
                    items=[]
                ))
        
        if 'removed' in item and item['removed']:
            for removed in item['removed']:
                nested_items.append(EOItem(
                    count=1,
                    name=f"Ohne {removed}",
                    price=0,
                    items=[]
                ))
        
        eo_items.append(EOItem(
            count=item.get('quantity', 1),
            name=item.get('name', ''),
            price=item_price,
            items=nested_items
        ))
    
    # Prepare timestamps
    order_time = zozo_order.get('created_at', datetime.utcnow())
    if isinstance(order_time, str):
        order_time = datetime.fromisoformat(order_time.replace('Z', '+00:00'))
    
    delivery_time = zozo_order.get('delivery_time', order_time)
    if isinstance(delivery_time, str):
        delivery_time = datetime.fromisoformat(delivery_time.replace('Z', '+00:00'))
    
    # Format timestamps for ExpertOrder
    ordertime_str = order_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    deliverytime_str = delivery_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    # Build complete order
    eo_order = EOOrder(
        version=1,
        broker="ZOZO Burger",
        fromMobile=zozo_order.get('from_mobile', False),
        clientIp=zozo_order.get('client_ip', ''),
        id=str(zozo_order.get('_id', '')),
        ordertime=ordertime_str,
        deliverytime=deliverytime_str,
        customerinfo=customer_details.get('notes', ''),
        orderprice=zozo_order.get('total', 0),
        orderdiscount=-abs(zozo_order.get('discount', 0)),  # Must be negative
        notification=zozo_order.get('is_pickup', False),
        deliverycost=zozo_order.get('delivery_fee', 0),
        tip=zozo_order.get('tip', 0),
        customer=eo_customer,
        payment=eo_payment,
        items=eo_items
    )
    
    return eo_order

from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, File, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from bson import ObjectId

from auth import create_access_token, get_current_user, verify_password, get_password_hash
from utils import serialize_doc, parse_object_id

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ.get('DB_NAME', 'test_database')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Request/Response Models
# Auth Models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# Menu Item Models
class MenuItemCreate(BaseModel):
    category_id: str
    name: str
    description: Optional[str] = None
    price_medium: Optional[float] = None
    price_large: Optional[float] = None
    price_normal: Optional[float] = None
    image_url: Optional[str] = None
    allergens: Optional[str] = None
    active: bool = True

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_medium: Optional[float] = None
    price_large: Optional[float] = None
    price_normal: Optional[float] = None
    image_url: Optional[str] = None
    allergens: Optional[str] = None
    active: Optional[bool] = None

# Order Models
class OrderItem(BaseModel):
    menu_item_id: str
    name: str
    price: float
    size: Optional[str] = None
    quantity: int = 1

class CustomerInfo(BaseModel):
    name: str
    phone: str
    address: str
    postal_code: str
    city: str
    notes: Optional[str] = None

class OrderCreate(BaseModel):
    location_id: str
    items: List[OrderItem]
    customer: CustomerInfo
    payment_method: str = "cash"

class OrderStatusUpdate(BaseModel):
    status: str

# Location Settings Models
class DeliveryZoneUpdate(BaseModel):
    postal_codes: Optional[List[str]] = None
    min_order_value: Optional[float] = None
    delivery_fee: Optional[float] = None
    free_delivery_threshold: Optional[float] = None

class DeliveryCheckRequest(BaseModel):
    postal_code: str

# ExpertOrder Settings Models
class ExpertOrderSettings(BaseModel):
    expertorder_api_key: Optional[str] = None
    expertorder_enabled: bool = False
    expertorder_test_mode: bool = False

# Deal Models
class DealCreate(BaseModel):
    title: str
    description: str
    discount_type: str
    discount_value: float
    min_order_value: Optional[float] = None
    valid_until: Optional[datetime] = None
    location_ids: List[str] = []
    image_url: Optional[str] = None

class DealUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    min_order_value: Optional[float] = None
    valid_until: Optional[datetime] = None
    location_ids: Optional[List[str]] = None
    image_url: Optional[str] = None
    active: Optional[bool] = None

# Routes
@api_router.get("/")
async def root():
    return {"message": "ZOZO Burger API - POC"}

# Locations
@api_router.get("/locations")
async def get_locations(include_status: bool = Query(False, description="Include opening status")):
    """Get all active locations with optional opening status"""
    from opening_hours_checker import get_opening_status_for_location
    
    cursor = db.locations.find({"active": True})
    locations = await cursor.to_list(length=100)
    
    result = serialize_doc(locations)
    
    # Add opening status if requested
    if include_status:
        for location in result:
            status = get_opening_status_for_location(location)
            location['opening_status'] = status
    
    return result

# Delivery Zone Check
@api_router.get("/check-delivery-zone")
async def check_delivery_zone(postal_code: str = Query(..., description="Customer postal code")):
    """Check if postal code is in any delivery zone and return location + fees"""
    # Find location that serves this postal code
    location = await db.locations.find_one({
        "active": True,
        "delivery_zone.postal_codes": postal_code
    })
    
    if not location:
        return {
            "available": False,
            "message": f"Leider beliefern wir die Postleitzahl {postal_code} aktuell nicht."
        }
    
    delivery_zone = location.get('delivery_zone', {})
    
    return {
        "available": True,
        "location": serialize_doc(location),
        "postal_code": postal_code,
        "min_order_value": delivery_zone.get('min_order_value', 0),
        "delivery_fee": delivery_zone.get('delivery_fee', 0),
        "free_delivery_threshold": delivery_zone.get('free_delivery_threshold', 0),
        "message": f"Lieferung nach {postal_code} möglich!"
    }

# Menu
@api_router.get("/menu")
async def get_menu(location_id: str = Query(...)):
    """Get menu for a specific location with categories"""
    # Verify location exists
    location = await db.locations.find_one({"_id": ObjectId(location_id), "active": True})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get all categories
    categories = await db.categories.find({"active": True}).sort("order", 1).to_list(length=100)
    
    # Get menu items (items without location_id are available at all locations)
    menu_items = await db.menu_items.find({
        "$or": [
            {"location_id": None},
            {"location_id": location_id}
        ],
        "active": True
    }).to_list(length=1000)
    
    # Organize items by category
    result = []
    for category in categories:
        cat_id = str(category['_id'])
        items = [item for item in menu_items if str(item['category_id']) == cat_id]
        if items:
            result.append({
                "id": cat_id,
                "name": category['name'],
                "slug": category['slug'],
                "items": serialize_doc(items)
            })
    
    return result

# Public Deals Endpoint
@api_router.get("/deals")
async def get_active_deals():
    """Get all active deals for homepage display"""
    deals = await db.deals.find({"active": True}).sort("created_at", -1).to_list(length=100)
    return serialize_doc(deals)

# Orders
@api_router.post("/orders")
async def create_order(order: OrderCreate):
    """Create a new order"""
    # Verify location exists
    location = await db.locations.find_one({"_id": ObjectId(order.location_id), "active": True})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Check if delivery zone is configured
    delivery_zone = location.get('delivery_zone', {})
    customer_postal_code = order.customer.postal_code
    
    # Validate postal code is in delivery zone
    if delivery_zone and customer_postal_code not in delivery_zone.get('postal_codes', []):
        raise HTTPException(
            status_code=400,
            detail=f"Wir liefern leider nicht nach {customer_postal_code}. Bitte wähle einen anderen Standort oder prüfe deine Postleitzahl."
        )
    
    # Calculate totals using location-specific settings
    subtotal = sum(item.price * item.quantity for item in order.items)
    min_order_value = delivery_zone.get('min_order_value', 0.0) if delivery_zone else 0.0
    delivery_fee_amount = delivery_zone.get('delivery_fee', 2.50) if delivery_zone else 2.50
    free_delivery_threshold = delivery_zone.get('free_delivery_threshold', 15.0) if delivery_zone else 15.0
    
    # Check minimum order value
    if subtotal < min_order_value:
        raise HTTPException(
            status_code=400,
            detail=f"Mindestbestellwert: €{min_order_value:.2f}. Deine Bestellung: €{subtotal:.2f}"
        )
    
    # Calculate delivery fee
    delivery_fee = delivery_fee_amount if subtotal < free_delivery_threshold else 0.0
    total = subtotal + delivery_fee
    
    # Generate order number
    count = await db.orders.count_documents({})
    order_number = f"ZOZO-{count + 1001}"
    
    # Create order document
    order_doc = {
        "location_id": order.location_id,
        "order_number": order_number,
        "items": [item.dict() for item in order.items],
        "subtotal": round(subtotal, 2),
        "delivery_fee": round(delivery_fee, 2),
        "total": round(total, 2),
        "customer": order.customer.dict(),
        "status": "new",
        "payment_method": order.payment_method,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.orders.insert_one(order_doc)
    order_doc['_id'] = result.inserted_id
    
    # Auto-send to ExpertOrder if API key is configured for this location
    location_settings = await db.location_settings.find_one({"location_id": order.location_id})
    
    if location_settings and location_settings.get('expertorder_api_key') and location_settings.get('expertorder_enabled'):
        try:
            from expertorder import ExpertOrderClient, map_zozo_order_to_expertorder
            
            # Map order to ExpertOrder format
            eo_order = map_zozo_order_to_expertorder(order_doc, location)
            
            # Send to ExpertOrder
            client = ExpertOrderClient(
                api_key=location_settings['expertorder_api_key'],
                use_test_mode=location_settings.get('expertorder_test_mode', False)
            )
            eo_response = await client.send_order(eo_order)
            
            # Update order with ExpertOrder status
            await db.orders.update_one(
                {"_id": result.inserted_id},
                {
                    "$set": {
                        "expertorder_sent": eo_response.get('success', False),
                        "expertorder_status": eo_response.get('status_code'),
                        "expertorder_message": eo_response.get('message'),
                        "expertorder_error": eo_response.get('error'),
                        "expertorder_sent_at": datetime.utcnow() if eo_response.get('success') else None
                    }
                }
            )
        except Exception as e:
            # Log error but don't fail the order creation
            print(f"ExpertOrder auto-send failed: {str(e)}")
    
    return serialize_doc(order_doc)

# ExpertOrder Integration
@api_router.post("/admin/orders/{order_id}/send-to-expertorder")
async def send_order_to_expertorder(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Manually send an order to ExpertOrder (for retry or manual sending)"""
    from expertorder import ExpertOrderClient, map_zozo_order_to_expertorder
    
    # Get order
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get location
    location = await db.locations.find_one({"_id": ObjectId(order['location_id'])})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get location settings (API key)
    location_settings = await db.location_settings.find_one({"location_id": order['location_id']})
    if not location_settings or not location_settings.get('expertorder_api_key'):
        raise HTTPException(
            status_code=400,
            detail="ExpertOrder API key not configured for this location"
        )
    
    # Map order to ExpertOrder format
    eo_order = map_zozo_order_to_expertorder(order, location)
    
    # Send to ExpertOrder
    client = ExpertOrderClient(
        api_key=location_settings['expertorder_api_key'],
        use_test_mode=location_settings.get('expertorder_test_mode', False)
    )
    eo_response = await client.send_order(eo_order)
    
    # Update order with ExpertOrder status
    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {
            "$set": {
                "expertorder_sent": eo_response.get('success', False),
                "expertorder_status": eo_response.get('status_code'),
                "expertorder_message": eo_response.get('message'),
                "expertorder_error": eo_response.get('error'),
                "expertorder_sent_at": datetime.utcnow() if eo_response.get('success') else None,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return eo_response

@api_router.post("/admin/expertorder/test")
async def test_expertorder_connection(
    location_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Test ExpertOrder connection with a test order"""
    from expertorder import ExpertOrderClient, EOOrder, EOCustomer, EOPayment, EOItem
    
    # Get location settings
    location_settings = await db.location_settings.find_one({"location_id": location_id})
    if not location_settings:
        raise HTTPException(status_code=404, detail="Location settings not found")
    
    api_key = location_settings.get('expertorder_api_key')
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="ExpertOrder API key not configured"
        )
    
    # Create test order
    test_order = EOOrder(
        version=1,
        broker="ZOZO Burger (Test)",
        fromMobile=False,
        clientIp="127.0.0.1",
        id=f"TEST-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        ordertime=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        deliverytime=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        customerinfo="Test-Bestellung von ZOZO Website",
        orderprice=13.00,  # Items (10.50) + Delivery (2.50) = 13.00
        orderdiscount=0,
        notification=False,
        deliverycost=2.50,
        tip=0,
        customer=EOCustomer(
            phone="01700000001",
            email="test@zozoburger.de",
            name="Test Kunde",
            street="Teststraße 1",
            zip="12345",
            location="Teststadt"
        ),
        payment=EOPayment(
            type=1,  # Bar
            prepaid=0
        ),
        items=[
            EOItem(
                count=1,
                name="Test Burger",
                price=8.00,
                items=[]
            ),
            EOItem(
                count=1,
                name="Coca Cola 0,33l",
                price=2.50,
                items=[]
            )
        ]
    )
    
    # Send test order
    client = ExpertOrderClient(
        api_key=api_key,
        use_test_mode=True  # Always use test mode for connection tests
    )
    response = await client.send_order(test_order)
    
    return response

# Auth Routes
@api_router.post("/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Admin login"""
    # Find admin user
    admin = await db.admin_users.find_one({"email": credentials.email, "active": True})
    
    if not admin or not verify_password(credentials.password, admin['password_hash']):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={
        "sub": str(admin['_id']),
        "email": admin['email'],
        "role": admin['role'],
        "location_id": admin.get('location_id')
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(admin['_id']),
            "email": admin['email'],
            "role": admin['role'],
            "location_id": admin.get('location_id')
        }
    }

@api_router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Admin Routes (Protected)
@api_router.get("/admin/orders")
async def get_admin_orders(
    location_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get orders with optional filters"""
    query = {}
    
    # If user is location manager, restrict to their location
    if current_user.get('role') == 'manager' and current_user.get('location_id'):
        query["location_id"] = current_user['location_id']
    elif location_id:
        query["location_id"] = location_id
    
    if status:
        query["status"] = status
    
    cursor = db.orders.find(query).sort("created_at", -1).limit(100)
    orders = await cursor.to_list(length=100)
    return serialize_doc(orders)

@api_router.patch("/admin/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    update: OrderStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update order status"""
    # Check if order exists and user has access
    order = await db.orders.find_one({"_id": parse_object_id(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if current_user.get('role') == 'manager':
        if order['location_id'] != current_user.get('location_id'):
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Update order
    result = await db.orders.update_one(
        {"_id": parse_object_id(order_id)},
        {"$set": {"status": update.status, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    updated_order = await db.orders.find_one({"_id": parse_object_id(order_id)})
    return serialize_doc(updated_order)

# Menu Management
@api_router.get("/admin/menu-items")
async def get_all_menu_items(
    location_id: Optional[str] = None,
    category_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all menu items (admin)"""
    query = {}
    
    if current_user.get('role') == 'manager' and current_user.get('location_id'):
        query["$or"] = [
            {"location_id": None},
            {"location_id": current_user['location_id']}
        ]
    elif location_id:
        query["location_id"] = location_id
    
    if category_id:
        query["category_id"] = category_id
    
    items = await db.menu_items.find(query).to_list(length=1000)
    return serialize_doc(items)

@api_router.post("/admin/menu-items")
async def create_menu_item(
    item: MenuItemCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new menu item"""
    item_doc = item.dict()
    
    # If user is location manager, set location_id
    if current_user.get('role') == 'manager' and current_user.get('location_id'):
        item_doc['location_id'] = current_user['location_id']
    
    result = await db.menu_items.insert_one(item_doc)
    item_doc['_id'] = result.inserted_id
    return serialize_doc(item_doc)

@api_router.patch("/admin/menu-items/{item_id}")
async def update_menu_item(
    item_id: str,
    update: MenuItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update menu item"""
    # Check if item exists
    item = await db.menu_items.find_one({"_id": parse_object_id(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Check access
    if current_user.get('role') == 'manager':
        if item.get('location_id') and item['location_id'] != current_user.get('location_id'):
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Update only provided fields
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    await db.menu_items.update_one(
        {"_id": parse_object_id(item_id)},
        {"$set": update_data}
    )
    
    updated_item = await db.menu_items.find_one({"_id": parse_object_id(item_id)})
    return serialize_doc(updated_item)

# Product Image Upload
@api_router.post("/admin/menu-items/{item_id}/upload-image")
async def upload_product_image(
    item_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload product image for menu item"""
    import os
    import uuid
    from pathlib import Path
    
    # Check if item exists
    item = await db.menu_items.find_one({"_id": parse_object_id(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Check access
    if current_user.get('role') == 'manager':
        if item.get('location_id') and item['location_id'] != current_user.get('location_id'):
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, and WebP allowed")
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = Path("uploads/products") / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Update menu item with image URL
    image_url = f"/uploads/products/{unique_filename}"
    await db.menu_items.update_one(
        {"_id": parse_object_id(item_id)},
        {"$set": {"image_url": image_url}}
    )
    
    return {
        "success": True,
        "image_url": image_url,
        "filename": unique_filename
    }

# Dashboard Stats
@api_router.get("/admin/stats")
async def get_dashboard_stats(
    location_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard statistics"""
    query = {}
    
    # If user is location manager, restrict to their location
    if current_user.get('role') == 'manager' and current_user.get('location_id'):
        query["location_id"] = current_user['location_id']
        location_id = current_user['location_id']
    elif location_id:
        query["location_id"] = location_id
    
    # Get order stats
    total_orders = await db.orders.count_documents(query)
    new_orders = await db.orders.count_documents({**query, "status": "new"})
    preparing_orders = await db.orders.count_documents({**query, "status": "preparing"})
    completed_orders = await db.orders.count_documents({**query, "status": "completed"})
    
    # Get revenue (only completed orders)
    pipeline = [
        {"$match": {**query, "status": "completed"}},
        {"$group": {"_id": None, "total_revenue": {"$sum": "$total"}}}
    ]
    revenue_result = await db.orders.aggregate(pipeline).to_list(1)
    total_revenue = revenue_result[0]['total_revenue'] if revenue_result else 0
    
    # Get today's orders
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_query = {**query, "created_at": {"$gte": today_start}}
    today_orders = await db.orders.count_documents(today_query)
    
    return {
        "total_orders": total_orders,
        "new_orders": new_orders,
        "preparing_orders": preparing_orders,
        "completed_orders": completed_orders,
        "total_revenue": round(total_revenue, 2),
        "today_orders": today_orders,
        "location_id": location_id
    }

# Delivery Check Endpoint (Public)
@api_router.post("/check-delivery")
async def check_delivery(request: DeliveryCheckRequest):
    """Check if delivery is available for a postal code"""
    postal_code = request.postal_code
    
    # Find all locations that deliver to this postal code
    locations = await db.locations.find({"active": True}).to_list(length=100)
    
    available_locations = []
    for location in locations:
        delivery_zone = location.get('delivery_zone', {})
        postal_codes = delivery_zone.get('postal_codes', [])
        
        if postal_code in postal_codes:
            available_locations.append({
                "location": serialize_doc(location),
                "delivery_fee": delivery_zone.get('delivery_fee', 2.50),
                "min_order_value": delivery_zone.get('min_order_value', 0.0),
                "free_delivery_threshold": delivery_zone.get('free_delivery_threshold', 15.0)
            })
    
    if available_locations:
        return {
            "can_deliver": True,
            "postal_code": postal_code,
            "available_locations": available_locations,
            "message": f"Lieferung nach {postal_code} verfügbar!"
        }
    else:
        return {
            "can_deliver": False,
            "postal_code": postal_code,
            "available_locations": [],
            "message": f"Leider liefern wir nicht nach {postal_code}. Bitte prüfe deine Postleitzahl oder wähle einen anderen Standort."
        }

# Location Settings Management
@api_router.get("/admin/location-settings")
async def get_location_settings(current_user: dict = Depends(get_current_user)):
    """Get location settings for current user"""
    location_id = current_user.get('location_id')
    
    if current_user.get('role') == 'owner':
        # Owner can see all locations
        locations = await db.locations.find({"active": True}).to_list(length=100)
        return serialize_doc(locations)
    elif location_id:
        # Manager can only see their location
        location = await db.locations.find_one({"_id": parse_object_id(location_id), "active": True})
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        return serialize_doc([location])
    else:
        raise HTTPException(status_code=403, detail="Access denied")

@api_router.patch("/admin/location-settings/{location_id}")
async def update_location_settings(
    location_id: str,
    settings: DeliveryZoneUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update location delivery zone settings"""
    # Check access
    if current_user.get('role') == 'manager':
        if location_id != current_user.get('location_id'):
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Get current location
    location = await db.locations.find_one({"_id": parse_object_id(location_id)})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Update delivery zone
    current_zone = location.get('delivery_zone', {})
    update_data = {}
    
    if settings.postal_codes is not None:
        current_zone['postal_codes'] = settings.postal_codes
    if settings.min_order_value is not None:
        current_zone['min_order_value'] = settings.min_order_value
    if settings.delivery_fee is not None:
        current_zone['delivery_fee'] = settings.delivery_fee
    if settings.free_delivery_threshold is not None:
        current_zone['free_delivery_threshold'] = settings.free_delivery_threshold
    
    await db.locations.update_one(
        {"_id": parse_object_id(location_id)},
        {"$set": {"delivery_zone": current_zone}}
    )
    
    updated_location = await db.locations.find_one({"_id": parse_object_id(location_id)})
    return serialize_doc(updated_location)

# ExpertOrder Settings Management
@api_router.get("/admin/expertorder-settings/{location_id}")
async def get_expertorder_settings(
    location_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get ExpertOrder settings for a location"""
    # Check access
    if current_user.get('role') == 'manager':
        if location_id != current_user.get('location_id'):
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Get or create settings
    settings = await db.location_settings.find_one({"location_id": location_id})
    if not settings:
        # Create default settings
        settings = {
            "location_id": location_id,
            "expertorder_api_key": "",
            "expertorder_enabled": False,
            "expertorder_test_mode": True,
            "created_at": datetime.utcnow()
        }
        await db.location_settings.insert_one(settings)
    
    return serialize_doc(settings)

@api_router.patch("/admin/expertorder-settings/{location_id}")
async def update_expertorder_settings(
    location_id: str,
    settings: ExpertOrderSettings,
    current_user: dict = Depends(get_current_user)
):
    """Update ExpertOrder settings for a location (owner only)"""
    if current_user.get('role') != 'owner':
        raise HTTPException(status_code=403, detail="Only owners can update ExpertOrder settings")
    
    # Get or create settings
    existing = await db.location_settings.find_one({"location_id": location_id})
    
    update_data = {
        "updated_at": datetime.utcnow()
    }
    
    if settings.expertorder_api_key is not None:
        update_data["expertorder_api_key"] = settings.expertorder_api_key
    if settings.expertorder_enabled is not None:
        update_data["expertorder_enabled"] = settings.expertorder_enabled
    if settings.expertorder_test_mode is not None:
        update_data["expertorder_test_mode"] = settings.expertorder_test_mode
    
    if existing:
        await db.location_settings.update_one(
            {"location_id": location_id},
            {"$set": update_data}
        )
    else:
        update_data["location_id"] = location_id
        update_data["created_at"] = datetime.utcnow()
        await db.location_settings.insert_one(update_data)
    
    updated = await db.location_settings.find_one({"location_id": location_id})
    return serialize_doc(updated)

# Deal Management (Admin)
@api_router.get("/admin/deals")
async def get_all_deals(current_user: dict = Depends(get_current_user)):
    """Get all deals (admin)"""
    deals = await db.deals.find({}).sort("created_at", -1).to_list(length=100)
    return serialize_doc(deals)

@api_router.post("/admin/deals")
async def create_deal(deal: DealCreate, current_user: dict = Depends(get_current_user)):
    """Create a new deal (owner only)"""
    if current_user.get('role') != 'owner':
        raise HTTPException(status_code=403, detail="Only owners can create deals")
    
    deal_doc = deal.dict()
    deal_doc['active'] = True
    deal_doc['created_at'] = datetime.utcnow()
    deal_doc['valid_from'] = datetime.utcnow()
    
    result = await db.deals.insert_one(deal_doc)
    deal_doc['_id'] = result.inserted_id
    return serialize_doc(deal_doc)

@api_router.patch("/admin/deals/{deal_id}")
async def update_deal(
    deal_id: str,
    update: DealUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update deal (owner only)"""
    if current_user.get('role') != 'owner':
        raise HTTPException(status_code=403, detail="Only owners can update deals")
    
    deal = await db.deals.find_one({"_id": parse_object_id(deal_id)})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    await db.deals.update_one(
        {"_id": parse_object_id(deal_id)},
        {"$set": update_data}
    )
    
    updated_deal = await db.deals.find_one({"_id": parse_object_id(deal_id)})
    return serialize_doc(updated_deal)

@api_router.delete("/admin/deals/{deal_id}")
async def delete_deal(deal_id: str, current_user: dict = Depends(get_current_user)):
    """Delete (deactivate) deal (owner only)"""
    if current_user.get('role') != 'owner':
        raise HTTPException(status_code=403, detail="Only owners can delete deals")
    
    result = await db.deals.update_one(
        {"_id": parse_object_id(deal_id)},
        {"$set": {"active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return {"message": "Deal deleted successfully"}

# Order History (for Quick Reorder)
@api_router.get("/orders/history")
async def get_order_history(
    customer_email: Optional[str] = None,
    customer_phone: Optional[str] = None
):
    """Get order history for a customer (for quick reorder)"""
    if not customer_email and not customer_phone:
        raise HTTPException(status_code=400, detail="Email or phone required")
    
    query = {"status": {"$in": ["completed", "out_for_delivery"]}}
    if customer_email:
        query["customer.email"] = customer_email
    elif customer_phone:
        query["customer.phone"] = customer_phone
    
    orders = await db.orders.find(query).sort("created_at", -1).limit(5).to_list(length=5)
    return serialize_doc(orders)


# Deal Management (Admin)
@api_router.get("/admin/deals")
async def get_all_deals(current_user: dict = Depends(get_current_user)):
    """Get all deals (admin)"""
    deals = await db.deals.find({}).sort("created_at", -1).to_list(length=100)
    return serialize_doc(deals)

@api_router.post("/admin/deals")
async def create_deal(deal: DealCreate, current_user: dict = Depends(get_current_user)):
    """Create a new deal (owner only)"""
    if current_user.get('role') != 'owner':
        raise HTTPException(status_code=403, detail="Only owners can create deals")
    
    deal_doc = deal.dict()
    deal_doc['active'] = True
    deal_doc['created_at'] = datetime.utcnow()
    deal_doc['valid_from'] = datetime.utcnow()
    
    result = await db.deals.insert_one(deal_doc)
    deal_doc['_id'] = result.inserted_id
    return serialize_doc(deal_doc)

@api_router.patch("/admin/deals/{deal_id}")
async def update_deal(
    deal_id: str,
    update: DealUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update deal (owner only)"""
    if current_user.get('role') != 'owner':
        raise HTTPException(status_code=403, detail="Only owners can update deals")
    
    deal = await db.deals.find_one({"_id": parse_object_id(deal_id)})
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    await db.deals.update_one(
        {"_id": parse_object_id(deal_id)},
        {"$set": update_data}
    )
    
    updated_deal = await db.deals.find_one({"_id": parse_object_id(deal_id)})
    return serialize_doc(updated_deal)

@api_router.delete("/admin/deals/{deal_id}")
async def delete_deal(deal_id: str, current_user: dict = Depends(get_current_user)):
    """Delete (deactivate) deal (owner only)"""
    if current_user.get('role') != 'owner':
        raise HTTPException(status_code=403, detail="Only owners can delete deals")
    
    result = await db.deals.update_one(
        {"_id": parse_object_id(deal_id)},
        {"$set": {"active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return {"message": "Deal deleted successfully"}

# Include the router in the main app
app.include_router(api_router)

# Mount static files for product images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends
from fastapi.security import HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
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
app = FastAPI(title="ZOZO Burger API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# =========================
# Request/Response Models
# =========================

# Auth Models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

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
    email: Optional[str] = None
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

# Category Models
class CategoryCreate(BaseModel):
    name: str
    slug: str
    order: int = 0

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    order: Optional[int] = None
    active: Optional[bool] = None

# =========================
# Public Routes
# =========================

@api_router.get(\"/\")
async def root():
    return {\"message\": \"ZOZO Burger API v1.0\", \"status\": \"running\"}

@api_router.get(\"/locations\")
async def get_locations():
    \"\"\"Get all active locations\"\"\"
    cursor = db.locations.find({\"active\": True})
    locations = await cursor.to_list(length=100)
    return serialize_doc(locations)

@api_router.get(\"/locations/{location_id}\")
async def get_location(location_id: str):
    \"\"\"Get specific location details\"\"\"
    location = await db.locations.find_one({\"_id\": parse_object_id(location_id), \"active\": True})
    if not location:
        raise HTTPException(status_code=404, detail=\"Location not found\")
    return serialize_doc(location)

@api_router.get(\"/menu\")
async def get_menu(location_id: str = Query(...)):
    \"\"\"Get menu for a specific location with categories\"\"\"
    # Verify location exists
    location = await db.locations.find_one({\"_id\": parse_object_id(location_id), \"active\": True})
    if not location:
        raise HTTPException(status_code=404, detail=\"Location not found\")
    
    # Get all categories
    categories = await db.categories.find({\"active\": True}).sort(\"order\", 1).to_list(length=100)
    
    # Get menu items (items without location_id are available at all locations)
    menu_items = await db.menu_items.find({
        \"$or\": [
            {\"location_id\": None},
            {\"location_id\": location_id}
        ],
        \"active\": True
    }).to_list(length=1000)
    
    # Organize items by category
    result = []
    for category in categories:
        cat_id = str(category['_id'])
        items = [item for item in menu_items if str(item['category_id']) == cat_id]
        if items:
            result.append({
                \"id\": cat_id,
                \"name\": category['name'],
                \"slug\": category['slug'],
                \"items\": serialize_doc(items)
            })
    
    return result

@api_router.get(\"/categories\")
async def get_categories():
    \"\"\"Get all active categories\"\"\"
    categories = await db.categories.find({\"active\": True}).sort(\"order\", 1).to_list(length=100)
    return serialize_doc(categories)

@api_router.post(\"/orders\")
async def create_order(order: OrderCreate):
    \"\"\"Create a new order\"\"\"
    # Verify location exists
    location = await db.locations.find_one({\"_id\": parse_object_id(order.location_id), \"active\": True})
    if not location:
        raise HTTPException(status_code=404, detail=\"Location not found\")
    
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in order.items)
    delivery_fee = 2.50 if subtotal < 15 else 0.0
    total = subtotal + delivery_fee
    
    # Generate order number
    count = await db.orders.count_documents({})
    order_number = f\"ZOZO-{count + 1001}\"
    
    # Create order document
    order_doc = {
        \"location_id\": order.location_id,
        \"order_number\": order_number,
        \"items\": [item.dict() for item in order.items],
        \"subtotal\": round(subtotal, 2),
        \"delivery_fee\": round(delivery_fee, 2),
        \"total\": round(total, 2),
        \"customer\": order.customer.dict(),
        \"status\": \"new\",
        \"payment_method\": order.payment_method,
        \"created_at\": datetime.utcnow(),
        \"updated_at\": datetime.utcnow()
    }
    
    result = await db.orders.insert_one(order_doc)
    order_doc['_id'] = result.inserted_id
    
    return serialize_doc(order_doc)

# =========================
# Auth Routes
# =========================

@api_router.post(\"/auth/login\", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    \"\"\"Admin login\"\"\"
    # Find admin user
    admin = await db.admin_users.find_one({\"email\": credentials.email, \"active\": True})
    
    if not admin or not verify_password(credentials.password, admin['password_hash']):
        raise HTTPException(
            status_code=401,
            detail=\"Incorrect email or password\"
        )
    
    # Create access token
    access_token = create_access_token(data={
        \"sub\": str(admin['_id']),
        \"email\": admin['email'],
        \"role\": admin['role'],
        \"location_id\": admin.get('location_id')
    })
    
    return {
        \"access_token\": access_token,
        \"token_type\": \"bearer\",
        \"user\": {
            \"id\": str(admin['_id']),
            \"email\": admin['email'],
            \"role\": admin['role'],
            \"location_id\": admin.get('location_id')
        }
    }

@api_router.get(\"/auth/me\")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    \"\"\"Get current user information\"\"\"
    return current_user

# =========================
# Admin Routes (Protected)
# =========================

# Orders Management
@api_router.get(\"/admin/orders\")
async def get_admin_orders(
    location_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    \"\"\"Get orders with optional filters\"\"\"
    query = {}
    
    # If user is location manager, restrict to their location
    if current_user.get('role') == 'manager' and current_user.get('location_id'):
        query[\"location_id\"] = current_user['location_id']
    elif location_id:
        query[\"location_id\"] = location_id
    
    if status:
        query[\"status\"] = status
    
    cursor = db.orders.find(query).sort(\"created_at\", -1).limit(100)
    orders = await cursor.to_list(length=100)
    return serialize_doc(orders)

@api_router.get(\"/admin/orders/{order_id}\")
async def get_order_details(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    \"\"\"Get specific order details\"\"\"
    order = await db.orders.find_one({\"_id\": parse_object_id(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail=\"Order not found\")
    
    # Check if user has access to this order
    if current_user.get('role') == 'manager':
        if order['location_id'] != current_user.get('location_id'):
            raise HTTPException(status_code=403, detail=\"Access denied\")
    
    return serialize_doc(order)

@api_router.patch(\"/admin/orders/{order_id}/status\")
async def update_order_status(
    order_id: str,
    update: OrderStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    \"\"\"Update order status\"\"\"
    # Check if order exists and user has access
    order = await db.orders.find_one({\"_id\": parse_object_id(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail=\"Order not found\")
    
    if current_user.get('role') == 'manager':
        if order['location_id'] != current_user.get('location_id'):
            raise HTTPException(status_code=403, detail=\"Access denied\")
    
    # Update order
    result = await db.orders.update_one(
        {\"_id\": parse_object_id(order_id)},
        {\"$set\": {\"status\": update.status, \"updated_at\": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail=\"Order not found\")
    
    updated_order = await db.orders.find_one({\"_id\": parse_object_id(order_id)})
    return serialize_doc(updated_order)

# Menu Management
@api_router.get(\"/admin/menu-items\")
async def get_all_menu_items(
    location_id: Optional[str] = None,
    category_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    \"\"\"Get all menu items (admin)\"\"\"
    query = {}
    
    if current_user.get('role') == 'manager' and current_user.get('location_id'):
        query[\"$or\"] = [
            {\"location_id\": None},
            {\"location_id\": current_user['location_id']}
        ]
    elif location_id:
        query[\"location_id\"] = location_id
    
    if category_id:
        query[\"category_id\"] = category_id
    
    items = await db.menu_items.find(query).to_list(length=1000)
    return serialize_doc(items)

@api_router.post(\"/admin/menu-items\")
async def create_menu_item(
    item: MenuItemCreate,
    current_user: dict = Depends(get_current_user)
):
    \"\"\"Create a new menu item\"\"\"
    item_doc = item.dict()
    
    # If user is location manager, set location_id
    if current_user.get('role') == 'manager' and current_user.get('location_id'):
        item_doc['location_id'] = current_user['location_id']
    
    result = await db.menu_items.insert_one(item_doc)
    item_doc['_id'] = result.inserted_id
    return serialize_doc(item_doc)

@api_router.patch(\"/admin/menu-items/{item_id}\")
async def update_menu_item(
    item_id: str,
    update: MenuItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    \"\"\"Update menu item\"\"\"
    # Check if item exists
    item = await db.menu_items.find_one({\"_id\": parse_object_id(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail=\"Menu item not found\")
    
    # Check access
    if current_user.get('role') == 'manager':
        if item.get('location_id') and item['location_id'] != current_user.get('location_id'):
            raise HTTPException(status_code=403, detail=\"Access denied\")
    
    # Update only provided fields
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail=\"No fields to update\")
    
    await db.menu_items.update_one(
        {\"_id\": parse_object_id(item_id)},
        {\"$set\": update_data}
    )
    
    updated_item = await db.menu_items.find_one({\"_id\": parse_object_id(item_id)})
    return serialize_doc(updated_item)

@api_router.delete(\"/admin/menu-items/{item_id}\")
async def delete_menu_item(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    \"\"\"Delete (deactivate) menu item\"\"\"
    # Check if item exists
    item = await db.menu_items.find_one({\"_id\": parse_object_id(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail=\"Menu item not found\")
    
    # Check access
    if current_user.get('role') == 'manager':
        if item.get('location_id') and item['location_id'] != current_user.get('location_id'):
            raise HTTPException(status_code=403, detail=\"Access denied\")
    
    # Soft delete by setting active to False
    await db.menu_items.update_one(
        {\"_id\": parse_object_id(item_id)},
        {\"$set\": {\"active\": False}}
    )
    
    return {\"message\": \"Menu item deleted successfully\"}

# Categories Management
@api_router.get(\"/admin/categories\")
async def get_all_categories(current_user: dict = Depends(get_current_user)):
    \"\"\"Get all categories (admin)\"\"\"
    categories = await db.categories.find({}).sort(\"order\", 1).to_list(length=100)
    return serialize_doc(categories)

@api_router.post(\"/admin/categories\")
async def create_category(
    category: CategoryCreate,
    current_user: dict = Depends(get_current_user)
):
    \"\"\"Create a new category (owner only)\"\"\"
    if current_user.get('role') != 'owner':
        raise HTTPException(status_code=403, detail=\"Only owners can create categories\")
    
    category_doc = category.dict()
    category_doc['active'] = True
    
    result = await db.categories.insert_one(category_doc)
    category_doc['_id'] = result.inserted_id
    return serialize_doc(category_doc)

@api_router.patch(\"/admin/categories/{category_id}\")
async def update_category(
    category_id: str,
    update: CategoryUpdate,
    current_user: dict = Depends(get_current_user)
):
    \"\"\"Update category (owner only)\"\"\"
    if current_user.get('role') != 'owner':
        raise HTTPException(status_code=403, detail=\"Only owners can update categories\")
    
    category = await db.categories.find_one({\"_id\": parse_object_id(category_id)})
    if not category:
        raise HTTPException(status_code=404, detail=\"Category not found\")
    
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail=\"No fields to update\")
    
    await db.categories.update_one(
        {\"_id\": parse_object_id(category_id)},
        {\"$set\": update_data}
    )
    
    updated_category = await db.categories.find_one({\"_id\": parse_object_id(category_id)})
    return serialize_doc(updated_category)

# Dashboard Stats
@api_router.get(\"/admin/stats\")
async def get_dashboard_stats(
    location_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    \"\"\"Get dashboard statistics\"\"\"
    query = {}
    
    # If user is location manager, restrict to their location
    if current_user.get('role') == 'manager' and current_user.get('location_id'):
        query[\"location_id\"] = current_user['location_id']
        location_id = current_user['location_id']
    elif location_id:
        query[\"location_id\"] = location_id
    
    # Get order stats
    total_orders = await db.orders.count_documents(query)
    new_orders = await db.orders.count_documents({**query, \"status\": \"new\"})
    preparing_orders = await db.orders.count_documents({**query, \"status\": \"preparing\"})
    completed_orders = await db.orders.count_documents({**query, \"status\": \"completed\"})
    
    # Get revenue (only completed orders)
    pipeline = [
        {\"$match\": {**query, \"status\": \"completed\"}},
        {\"$group\": {\"_id\": None, \"total_revenue\": {\"$sum\": \"$total\"}}}
    ]
    revenue_result = await db.orders.aggregate(pipeline).to_list(1)
    total_revenue = revenue_result[0]['total_revenue'] if revenue_result else 0
    
    # Get today's orders
    from datetime import date, timedelta
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_query = {**query, \"created_at\": {\"$gte\": today_start}}
    today_orders = await db.orders.count_documents(today_query)
    
    return {
        \"total_orders\": total_orders,
        \"new_orders\": new_orders,
        \"preparing_orders\": preparing_orders,
        \"completed_orders\": completed_orders,
        \"total_revenue\": round(total_revenue, 2),
        \"today_orders\": today_orders,
        \"location_id\": location_id
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event(\"shutdown\")
async def shutdown_db_client():
    client.close()

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

# Routes
@api_router.get("/")
async def root():
    return {"message": "ZOZO Burger API - POC"}

# Locations
@api_router.get("/locations")
async def get_locations():
    """Get all active locations"""
    cursor = db.locations.find({"active": True})
    locations = await cursor.to_list(length=100)
    return serialize_doc(locations)

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

# Orders
@api_router.post("/orders")
async def create_order(order: OrderCreate):
    """Create a new order"""
    # Verify location exists
    location = await db.locations.find_one({"_id": ObjectId(order.location_id), "active": True})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Calculate totals
    subtotal = sum(item.price * item.quantity for item in order.items)
    delivery_fee = 2.50 if subtotal < 15 else 0.0
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
    
    return serialize_doc(order_doc)

@api_router.get("/admin/orders")
async def get_orders(
    location_id: Optional[str] = None,
    status: Optional[str] = None,
    token: str = Query(default="POC_TOKEN")
):
    """Get orders (with optional filters) - POC uses simple token"""
    if token != "POC_TOKEN":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    query = {}
    if location_id:
        query["location_id"] = location_id
    if status:
        query["status"] = status
    
    cursor = db.orders.find(query).sort("created_at", -1)
    orders = await cursor.to_list(length=100)
    return serialize_doc(orders)

@api_router.patch("/admin/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    update: OrderStatusUpdate,
    token: str = Query(default="POC_TOKEN")
):
    """Update order status - POC uses simple token"""
    if token != "POC_TOKEN":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    result = await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": update.status, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    return serialize_doc(order)

# Include the router in the main app
app.include_router(api_router)

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
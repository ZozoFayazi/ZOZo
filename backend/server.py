from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, File, UploadFile, Request
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
from models import *
from admin_auth import AdminAuth, get_current_admin, require_permission, require_super_admin
from admin_models import AdminLoginRequest, AdminLoginResponse, PasswordChangeRequest
from audit_service import AuditService, AuditCategory, AuditAction
from location_models import LocationCreate, LocationUpdate, LocationResponse
from product_endpoints import create_product_router
from product_endpoints_v2 import create_product_router_v2
from pos_service import POSService
from pos_models import POSProvider, POSStatus, POSConfigInput, POSConfigResponse
from rate_limiter import RateLimiter
from totp_service import TOTPService
from daily_deals_service import DailyDealsService
from feature_toggle_service import FeatureToggleService
from paypal_service import PayPalService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ.get('DB_NAME', 'test_database')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Initialize services
audit_service = AuditService(db)
pos_service = POSService(db)
rate_limiter = RateLimiter(db)
totp_service = TOTPService(db)
daily_deals_service = DailyDealsService(db)
feature_toggle_service = FeatureToggleService(db)
paypal_service = PayPalService(db)

# Create product router with admin authentication
# V2: Master-Slave architecture (Rellingen = Master, Henstedt = Override only)
product_router = create_product_router_v2(db, audit_service)

# Create the main app without a prefix
app = FastAPI(
    title="ZOZO Burger API",
    description="Professional Food Ordering System API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

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
    is_pickup: bool = False
    points_to_redeem: int = 0

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

# Discount Code Models
class DiscountCodeCreate(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: str  # "percentage" or "fixed"
    discount_value: float
    min_order_value: Optional[float] = 0
    order_type: Optional[str] = None  # "pickup", "delivery", or None (both)
    max_uses: Optional[int] = None  # None = unlimited
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    location_ids: List[str] = []  # Empty = all locations
    active: bool = True

class DiscountCodeUpdate(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    min_order_value: Optional[float] = None
    order_type: Optional[str] = None
    max_uses: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    location_ids: Optional[List[str]] = None
    active: Optional[bool] = None

class DiscountCodeValidate(BaseModel):
    code: str
    order_total: float
    order_type: str  # "pickup" or "delivery"
    location_id: str

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


@api_router.get("/locations/{slug}")
async def get_location_by_slug(slug: str, include_menu: bool = Query(False)):
    """
    Get a single location by slug for public SEO pages
    Returns detailed location info including opening hours, delivery area, and SEO data
    """
    from opening_hours_checker import get_opening_status_for_location
    
    location = await db.locations.find_one({"slug": slug, "active": True})
    
    if not location:
        raise HTTPException(status_code=404, detail="Standort nicht gefunden")
    
    result = serialize_doc(location)
    
    # Add opening status
    result['opening_status'] = get_opening_status_for_location(location)
    
    # Format opening hours for display
    opening_hours_raw = location.get('opening_hours', [])
    formatted_hours = []
    day_names = {
        'monday': 'Montag',
        'tuesday': 'Dienstag', 
        'wednesday': 'Mittwoch',
        'thursday': 'Donnerstag',
        'friday': 'Freitag',
        'saturday': 'Samstag',
        'sunday': 'Sonntag'
    }
    days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    # Handle different formats
    if isinstance(opening_hours_raw, str):
        # Simple string format like "11:00 - 22:45" - apply to all days
        for day in days_order:
            formatted_hours.append({
                'day': day_names[day],
                'day_key': day,
                'is_open': True,
                'hours': opening_hours_raw or "11:00 - 22:45"
            })
    elif isinstance(opening_hours_raw, list):
        # Structured format with per-day settings
        for hours in opening_hours_raw:
            if isinstance(hours, dict):
                day = hours.get('day', '').lower()
                if hours.get('is_open', True):
                    formatted_hours.append({
                        'day': day_names.get(day, day.capitalize()),
                        'day_key': day,
                        'is_open': True,
                        'hours': f"{hours.get('open_time', '11:00')} - {hours.get('close_time', '22:45')}"
                    })
                else:
                    formatted_hours.append({
                        'day': day_names.get(day, day.capitalize()),
                        'day_key': day,
                        'is_open': False,
                        'hours': 'Geschlossen'
                    })
    
    # If no hours defined, use default
    if not formatted_hours:
        for day in days_order:
            formatted_hours.append({
                'day': day_names[day],
                'day_key': day,
                'is_open': True,
                'hours': "11:00 - 22:45"
            })
    
    result['formatted_hours'] = formatted_hours
    
    # Get delivery area info - handle both old and new format
    delivery_area = location.get('delivery_area', {}) or {}
    delivery_zone = location.get('delivery_zone', {}) or {}
    
    # Merge both formats (new format takes precedence)
    combined_delivery = {**delivery_zone, **delivery_area}
    
    result['delivery_info'] = {
        'mode': combined_delivery.get('mode', 'plz'),
        'radius_km': combined_delivery.get('radius_km', 5.0),
        'postal_codes': combined_delivery.get('postal_codes', []),
        'delivery_fee': combined_delivery.get('delivery_fee', 3.0),
        'min_order_value': combined_delivery.get('min_order_value', 12.0),
        'free_delivery_threshold': combined_delivery.get('free_delivery_threshold', 20.0),
        'estimated_time': combined_delivery.get('estimated_delivery_time', '30-45 Min')
    }
    
    # Get SEO data with defaults
    seo = location.get('seo', {}) or {}
    location_name = location.get('name', '')
    city = location.get('city', '')
    
    # Clean title - avoid double "ZOZO Burger"
    if location_name.startswith('ZOZO Burger'):
        title_name = location_name
    else:
        title_name = f"ZOZO Burger {location_name}"
    
    result['seo'] = {
        'meta_title': seo.get('meta_title') or f"{title_name} - Burger, Pizza & Pasta Lieferservice",
        'meta_description': seo.get('meta_description') or f"Bestelle jetzt bei {location_name}! Premium Burger, Pizza, Pasta & mehr. Lieferung in {city} und Umgebung. ☎ {location.get('phone', '')}",
        'keywords': seo.get('keywords') or f"Burger {city}, Pizza Lieferservice, ZOZO Burger, Lieferservice {city}, {location_name}"
    }
    
    # Include popular menu items if requested
    if include_menu:
        menu_items = await db.menu_items.find({
            "active": True,
            "$or": [
                {"location_id": None},  # Global items
                {"location_id": str(location['_id'])}  # Location-specific items
            ]
        }).limit(6).to_list(length=6)
        result['popular_items'] = serialize_doc(menu_items)
    
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

# Categories
@api_router.get("/categories")
@api_router.get("/admin/categories")
async def get_categories():
    """Get all active categories"""
    categories = await db.categories.find({"active": True}).sort("order", 1).to_list(length=100)
    
    result = []
    for cat in categories:
        result.append({
            "id": str(cat.get("_id")),
            "name": cat.get("name"),
            "slug": cat.get("slug"),
            "order": cat.get("order", 0)
        })
    
    return {"categories": result}
    return {"categories": result}

# Admin: Category Management
class CategoryCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    active: bool = True

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    active: Optional[bool] = None
    order: Optional[int] = None

class CategoryReorder(BaseModel):
    categories: List[dict]  # [{id, order}, ...]

@api_router.post("/admin/categories")
async def create_category(category: CategoryCreate, admin: dict = Depends(get_current_admin)):
    """Create a new category"""
    import uuid
    
    # Auto-generate slug if not provided
    if not category.slug:
        import re
        slug = category.name.lower()
        slug = slug.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
        slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
        category.slug = slug
    
    # Check if slug already exists
    existing = await db.categories.find_one({"slug": category.slug})
    if existing:
        raise HTTPException(status_code=400, detail="Slug bereits vergeben")
    
    # Get max order
    max_order_cat = await db.categories.find_one({}, sort=[("order", -1)])
    next_order = (max_order_cat.get('order', 0) + 1) if max_order_cat else 0
    
    category_doc = {
        "id": str(uuid.uuid4()),
        "name": category.name,
        "slug": category.slug,
        "active": category.active,
        "order": next_order,
        "created_at": datetime.utcnow()
    }
    
    result = await db.categories.insert_one(category_doc)
    category_doc['_id'] = result.inserted_id
    
    return serialize_doc(category_doc)

@api_router.patch("/admin/categories/{category_id}")
async def update_category(
    category_id: str,
    update: CategoryUpdate,
    admin: dict = Depends(get_current_admin)
):
    """Update a category"""
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Keine Felder zum Aktualisieren")
    
    # Try to find by id field first, then by _id
    category = await db.categories.find_one({"id": category_id})
    if not category:
        category = await db.categories.find_one({"_id": parse_object_id(category_id)})
    
    if not category:
        raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")
    
    result = await db.categories.update_one(
        {"_id": category['_id']},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")
    
    updated = await db.categories.find_one({"_id": category['_id']})
    return serialize_doc(updated)

@api_router.delete("/admin/categories/{category_id}")
async def delete_category(category_id: str, admin: dict = Depends(get_current_admin)):
    """Delete a category (soft delete - set active=false)"""
    # Try to find by id field first, then by _id
    category = await db.categories.find_one({"id": category_id})
    if not category:
        category = await db.categories.find_one({"_id": parse_object_id(category_id)})
    
    if not category:
        raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")
    
    result = await db.categories.update_one(
        {"_id": category['_id']},
        {"$set": {"active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Kategorie nicht gefunden")
    
    return {"success": True, "message": "Kategorie deaktiviert"}

@api_router.post("/admin/categories/reorder")
async def reorder_categories(reorder: CategoryReorder, admin: dict = Depends(get_current_admin)):
    """Reorder categories"""
    for item in reorder.categories:
        cat_id = item.get('id')
        order = item.get('order')
        
        # Try id field first, then _id
        category = await db.categories.find_one({"id": cat_id})
        if not category:
            category = await db.categories.find_one({"_id": parse_object_id(cat_id)})
        
        if category:
            await db.categories.update_one(
                {"_id": category['_id']},
                {"$set": {"order": order}}
            )
    
    return {"success": True, "message": "Reihenfolge aktualisiert"}


# ==================== FAILED POS ORDERS MANAGEMENT ====================

@api_router.get("/admin/pos/failed-orders")
async def get_failed_orders(admin: dict = Depends(get_current_admin)):
    """Get all failed POS orders"""
    query = {}
    
    # Filter by admin's branch access
    branch_ids = admin.get('branch_ids', [])
    if branch_ids:
        query["location_slug"] = {"$in": [loc.get('slug') for loc in await db.locations.find({"id": {"$in": branch_ids}}).to_list(10)]}
    
    orders = await db.failed_pos_orders.find(query).sort("created_at", -1).to_list(length=100)
    return serialize_doc(orders)

@api_router.post("/admin/pos/retry-failed-order/{order_id}")
async def retry_failed_order(order_id: str, admin: dict = Depends(get_current_admin)):
    """Retry sending a failed order to POS"""
    from bson import ObjectId
    
    # Get failed order
    failed_order = await db.failed_pos_orders.find_one({"_id": ObjectId(order_id)})
    if not failed_order:
        raise HTTPException(status_code=404, detail="Failed order not found")
    
    # Get location slug
    location_slug = failed_order.get('location_slug')
    order_data = failed_order.get('order_data', {})
    
    # Retry push
    result = await pos_service.push_order(order_data, location_slug)
    
    if result.get('success'):
        # Mark as resolved
        await db.failed_pos_orders.update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "status": "resolved",
                    "resolved_at": datetime.utcnow(),
                    "resolved_by": admin.get('email')
                }
            }
        )
        return {"success": True, "message": "Order successfully sent to POS"}
    else:
        return {"success": False, "message": result.get('message', 'Failed to send')}

@api_router.post("/admin/pos/resolve-failed-order/{order_id}")
async def resolve_failed_order(order_id: str, admin: dict = Depends(get_current_admin)):
    """Mark a failed order as manually resolved"""
    from bson import ObjectId
    
    result = await db.failed_pos_orders.update_one(
        {"_id": ObjectId(order_id)},
        {
            "$set": {
                "status": "manual",
                "resolved_at": datetime.utcnow(),
                "resolved_by": admin.get('email')
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Failed order not found")
    
    return {"success": True, "message": "Order marked as resolved"}


# End of Failed POS Orders endpoints


# Menu
@api_router.get("/menu")
async def get_menu(location_id: str = Query(...)):
    """Get menu for a specific location with categories"""
    # Verify location exists (try both UUID 'id' field and ObjectId '_id' field)
    location = await db.locations.find_one({"id": location_id, "active": True})
    if not location:
        # Fallback: try as ObjectId
        try:
            location = await db.locations.find_one({"_id": ObjectId(location_id), "active": True})
        except:
            pass
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Get all categories
    categories = await db.categories.find({"active": True}).sort("order", 1).to_list(length=100)
    
    # Get menu items (items without location_id are available at all locations)
    menu_items = await db.menu_items.find({
        "$or": [
            {"location_id": None},
            {"location_id": location_id},
            {"location_id": str(location.get("_id"))}
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


@api_router.get("/modifier-groups")
async def get_modifier_groups():
    """Get all modifier groups"""
    groups = await db.modifier_groups.find({}).to_list(100)
    return serialize_doc(groups)


# ==================== DAILY DEALS (TAGESANGEBOTE) ====================

# Pydantic Models für Daily Deals
from pydantic import BaseModel
from typing import Optional, List

class DailyDealCreate(BaseModel):
    weekday: int  # 0=Montag, 6=Sonntag
    title: str
    description: str
    discount_type: str  # "percentage", "2for1"
    discount_value: Optional[float] = 0
    target_type: str  # "category", "product", "size"
    target_value: str  # Kategorie-Slug, Produkt-ID
    target_size: Optional[str] = None
    requires_same_item: Optional[bool] = False
    image_url: Optional[str] = None
    badge_text: Optional[str] = "Tagesangebot"
    badge_color: Optional[str] = "#FF6B35"
    active: Optional[bool] = True
    applies_to_all_locations: Optional[bool] = True
    location_ids: Optional[List[str]] = []

class DailyDealUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[float] = None
    target_type: Optional[str] = None
    target_value: Optional[str] = None
    target_size: Optional[str] = None
    requires_same_item: Optional[bool] = None
    image_url: Optional[str] = None
    badge_text: Optional[str] = None
    badge_color: Optional[str] = None
    active: Optional[bool] = None
    applies_to_all_locations: Optional[bool] = None
    location_ids: Optional[List[str]] = None

class CartDiscountRequest(BaseModel):
    items: List[dict]
    location_id: Optional[str] = None

# Public: Heutiges Tagesangebot
@api_router.get("/daily-deal")
async def get_today_daily_deal():
    """Holt das aktive Tagesangebot für heute (für Homepage)"""
    deal = await daily_deals_service.get_today_deal()
    return deal or {"message": "Kein Tagesangebot heute"}

# Public: Alle Tagesangebote (Wochenübersicht)
@api_router.get("/daily-deals")
async def get_all_daily_deals():
    """Holt alle Tagesangebote für die Wochenübersicht"""
    deals = await daily_deals_service.get_all_deals()
    return deals

# Public: Warenkorb-Rabatt berechnen
@api_router.post("/daily-deal/calculate")
async def calculate_daily_deal_discount(request: CartDiscountRequest):
    """
    Berechnet den Tagesangebot-Rabatt für den Warenkorb.
    
    Erwartet:
    {
        "items": [
            {"menu_item_id": "...", "name": "Pasta Bolognese", "category": "pasta", "price": 12.90, "quantity": 2, "size": "normal"},
            ...
        ],
        "location_id": "..." (optional)
    }
    
    Gibt zurück:
    {
        "deal": {...},
        "discount_amount": 5.16,
        "discount_details": [...]
    }
    """
    result = await daily_deals_service.calculate_cart_discounts(request.items, request.location_id)
    return result

# Admin: Alle Tagesangebote verwalten
@api_router.get("/admin/daily-deals")
async def admin_get_daily_deals(admin: dict = Depends(get_current_admin)):
    """Admin: Alle Tagesangebote abrufen"""
    deals = await daily_deals_service.get_all_deals()
    return deals

@api_router.post("/admin/daily-deals")
async def admin_create_daily_deal(
    deal: DailyDealCreate,
    admin: dict = Depends(get_current_admin)
):
    """Admin: Tagesangebot erstellen oder aktualisieren"""
    result = await daily_deals_service.create_deal(deal.dict(), admin.get("email", "admin"))
    return result

@api_router.patch("/admin/daily-deals/{deal_id}")
async def admin_update_daily_deal(
    deal_id: str,
    update: DailyDealUpdate,
    admin: dict = Depends(get_current_admin)
):
    """Admin: Tagesangebot aktualisieren"""
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    result = await daily_deals_service.update_deal(deal_id, update_data, admin.get("email", "admin"))
    if not result:
        raise HTTPException(status_code=404, detail="Tagesangebot nicht gefunden")
    return result

@api_router.delete("/admin/daily-deals/{deal_id}")
async def admin_delete_daily_deal(
    deal_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Admin: Tagesangebot löschen (deaktivieren)"""
    success = await daily_deals_service.delete_deal(deal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tagesangebot nicht gefunden")
    return {"success": True, "message": "Tagesangebot deaktiviert"}

@api_router.post("/admin/daily-deals/setup-defaults")
async def admin_setup_default_deals(admin: dict = Depends(get_current_admin)):
    """Admin: Standard-Tagesangebote einrichten"""
    deals = await daily_deals_service.setup_default_deals()
    return {"success": True, "message": f"{len(deals)} Tagesangebote eingerichtet", "deals": deals}


# ==================== FEATURE TOGGLES ====================

# Public: Feature-Status abrufen (für Frontend)
@api_router.get("/features")
async def get_public_features():
    """Holt den Status aller Features für das Frontend"""
    features = await feature_toggle_service.get_public_features()
    return features

# Admin: Alle Features mit Details
@api_router.get("/admin/features")
async def admin_get_all_features(admin: dict = Depends(get_current_admin)):
    """Admin: Alle Features mit Details abrufen"""
    features = await feature_toggle_service.get_all_features()
    return features

# Admin: Feature togglen (nur Super Admin)
@api_router.patch("/admin/features/{feature_key}")
async def admin_toggle_feature(
    feature_key: str,
    enabled: bool,
    admin: dict = Depends(get_current_admin)
):
    """Admin: Feature aktivieren/deaktivieren (nur Super Admin)"""
    if admin.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Nur Super Admin kann Features ändern")
    
    try:
        result = await feature_toggle_service.toggle_feature(
            feature_key, 
            enabled, 
            admin.get("email", "admin")
        )
        return {"success": True, "feature": feature_key, "enabled": enabled}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Admin: Feature-Toggles initialisieren
@api_router.post("/admin/features/initialize")
async def admin_initialize_features(admin: dict = Depends(get_current_admin)):
    """Admin: Feature-Toggles initialisieren"""
    if admin.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Nur Super Admin")
    
    features = await feature_toggle_service.initialize_features()


# ==================== PAYPAL PAYMENT INTEGRATION ====================

# Pydantic Models for PayPal
class PayPalOrderCreate(BaseModel):
    location_id: str
    order_id: str
    order_number: str
    subtotal: float
    delivery_fee: float
    discount: float
    total: float
    currency: str = "EUR"
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None

class PayPalOrderCapture(BaseModel):
    paypal_order_id: str
    zozo_order_id: str  # Our internal order ID

class PayPalSettings(BaseModel):
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    paypal_enabled: bool = False
    paypal_sandbox_mode: bool = True

# Public: Create PayPal Order
@api_router.post("/paypal/create-order")
async def create_paypal_order(order_request: PayPalOrderCreate):
    """Create a PayPal order for payment"""
    try:
        result = await paypal_service.create_order(
            location_id=order_request.location_id,
            order_data=order_request.dict()
        )
        return result
    except Exception as e:
        logging.error(f"PayPal create order error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Public: Capture PayPal Payment
@api_router.post("/paypal/capture-order")
async def capture_paypal_order(capture_request: PayPalOrderCapture):
    """Capture a PayPal payment after customer approval"""
    try:
        # Get the ZOZO order to find location
        order = await db.orders.find_one({"_id": parse_object_id(capture_request.zozo_order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Capture PayPal payment
        result = await paypal_service.capture_order(
            location_id=order['location_id'],
            paypal_order_id=capture_request.paypal_order_id
        )
        
        if result.get('success'):
            # Update order with PayPal transaction details
            await db.orders.update_one(
                {"_id": parse_object_id(capture_request.zozo_order_id)},
                {
                    "$set": {
                        "payment_status": "paid",
                        "paypal_transaction_id": result.get('transaction_id'),
                        "paypal_order_id": result.get('paypal_order_id'),
                        "paid_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # NOW push to POS after successful payment
            try:
                order_refreshed = await db.orders.find_one({"_id": parse_object_id(capture_request.zozo_order_id)})
                location = await db.locations.find_one({"id": order_refreshed['location_id']})
                
                pos_order_data = {
                    "order_id": str(order_refreshed['_id']),
                    "order_number": order_refreshed['order_number'],
                    "customer_name": order_refreshed['customer']['name'],
                    "customer_email": order_refreshed['customer'].get('email'),
                    "customer_phone": order_refreshed['customer']['phone'],
                    "items": order_refreshed['items'],
                    "total": order_refreshed['total'],
                    "delivery_type": "pickup" if order_refreshed.get('is_pickup') else "delivery",
                    "delivery_address": f"{order_refreshed['customer']['address']}, {order_refreshed['customer']['postal_code']} {order_refreshed['customer']['city']}",
                    "payment_method": "paypal",
                    "notes": order_refreshed['customer'].get('notes', '')
                }
                
                # Push to POS
                pos_result = await pos_service.push_order(pos_order_data, location.get('slug', ''))
                
                # Update order with POS status
                pos_update = {
                    "pos_status": pos_result.get('pos_status', 'not_applicable'),
                    "pos_pushed_at": datetime.utcnow() if pos_result.get('success') else None,
                    "pos_order_id": pos_result.get('pos_order_id'),
                    "pos_is_test_mode": pos_result.get('is_test_mode', True)
                }
                
                if not pos_result.get('success') and pos_result.get('pos_status') == 'error':
                    pos_update["pos_error"] = pos_result.get('message', 'Unknown error')
                
                await db.orders.update_one(
                    {"_id": parse_object_id(capture_request.zozo_order_id)},
                    {"$set": pos_update}
                )
                
            except Exception as e:
                logging.error(f"POS push after PayPal payment failed: {str(e)}")
        
        return result
    except Exception as e:
        logging.error(f"PayPal capture order error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Admin: Get PayPal Settings for Location
@api_router.get("/admin/paypal-settings/{location_id}")
async def get_paypal_settings(
    location_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get PayPal settings for a location"""
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
            "paypal_client_id": "",
            "paypal_client_secret": "",
            "paypal_enabled": False,
            "paypal_sandbox_mode": True,
            "created_at": datetime.utcnow()
        }
        await db.location_settings.insert_one(settings)
    
    # Don't expose secret in response
    response = serialize_doc(settings)
    if 'paypal_client_secret' in response and response['paypal_client_secret']:
        response['paypal_client_secret'] = '****' + response['paypal_client_secret'][-4:]
    
    return response

# Admin: Update PayPal Settings for Location
@api_router.patch("/admin/paypal-settings/{location_id}")
async def update_paypal_settings(
    location_id: str,
    settings: PayPalSettings,
    current_user: dict = Depends(get_current_user)
):
    """Update PayPal settings for a location (owner only)"""
    if current_user.get('role') != 'owner':
        raise HTTPException(status_code=403, detail="Only owners can update PayPal settings")
    
    # Get or create settings
    existing = await db.location_settings.find_one({"location_id": location_id})
    
    update_data = {
        "updated_at": datetime.utcnow()
    }
    
    if settings.paypal_client_id is not None:
        update_data["paypal_client_id"] = settings.paypal_client_id
    if settings.paypal_client_secret is not None:
        update_data["paypal_client_secret"] = settings.paypal_client_secret
    if settings.paypal_enabled is not None:
        update_data["paypal_enabled"] = settings.paypal_enabled
    if settings.paypal_sandbox_mode is not None:
        update_data["paypal_sandbox_mode"] = settings.paypal_sandbox_mode
    
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
    
    # Don't expose secret in response
    response = serialize_doc(updated)
    if 'paypal_client_secret' in response and response['paypal_client_secret']:
        response['paypal_client_secret'] = '****' + response['paypal_client_secret'][-4:]
    
    return response

# Public: Get PayPal Client ID for Frontend
@api_router.get("/paypal/client-id/{location_id}")
async def get_paypal_client_id(location_id: str):
    """Get PayPal Client ID for frontend (public endpoint)"""
    settings = await db.location_settings.find_one({"location_id": location_id})
    
    if not settings or not settings.get('paypal_enabled'):
        raise HTTPException(status_code=404, detail="PayPal not enabled for this location")
    
    return {
        "client_id": settings.get('paypal_client_id'),
        "sandbox_mode": settings.get('paypal_sandbox_mode', True)
    }


    return {"success": True, "features": features}


# Public Deals Endpoint
@api_router.get("/deals")
async def get_active_deals():
    """Get all active deals for homepage display"""
    deals = await db.deals.find({"active": True}).sort("created_at", -1).to_list(length=100)
    return serialize_doc(deals)

# Featured Products
@api_router.get("/featured-products")
async def get_featured_products():
    """Get featured products for homepage hero carousel"""
    cursor = db.menu_items.find({"is_featured": True, "active": True}).sort("featured_order", 1)
    items = await cursor.to_list(length=20)
    return serialize_doc(items)

# Order History
@api_router.get("/order-history/{email}")
async def get_order_history(email: str, limit: int = 5):
    """Get recent orders for a customer by email"""
    cursor = db.orders.find(
        {"customer.email": email}
    ).sort("created_at", -1).limit(limit)
    orders = await cursor.to_list(length=limit)
    return serialize_doc(orders)

# Custom Burger Builder
@api_router.post("/custom-burgers")
async def create_custom_burger(burger: CustomBurger):
    """Create a custom burger"""
    burger_dict = burger.dict(by_alias=True, exclude={"id"})
    burger_dict["created_at"] = datetime.utcnow()
    
    result = await db.custom_burgers.insert_one(burger_dict)
    created_burger = await db.custom_burgers.find_one({"_id": result.inserted_id})
    
    return serialize_doc(created_burger)

@api_router.get("/custom-burgers")
async def get_custom_burgers(email: Optional[str] = None, public_only: bool = False):
    """Get custom burgers - filtered by email or public ones"""
    query = {}
    if public_only:
        query["is_public"] = True
    elif email:
        query["created_by"] = email
    
    cursor = db.custom_burgers.find(query).sort("created_at", -1).limit(20)
    burgers = await cursor.to_list(length=20)
    return serialize_doc(burgers)

@api_router.get("/custom-burgers/{burger_id}")
async def get_custom_burger(burger_id: str):
    """Get a specific custom burger by ID"""
    burger = await db.custom_burgers.find_one({"_id": parse_object_id(burger_id)})
    if not burger:
        raise HTTPException(status_code=404, detail="Custom burger not found")
    return serialize_doc(burger)

@api_router.post("/custom-burgers/{burger_id}/vote")
async def vote_custom_burger(burger_id: str):
    """Vote for a custom burger"""
    result = await db.custom_burgers.update_one(
        {"_id": parse_object_id(burger_id)},
        {"$inc": {"votes": 1}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Custom burger not found")
    
    burger = await db.custom_burgers.find_one({"_id": parse_object_id(burger_id)})
    return serialize_doc(burger)

# Orders
@api_router.post("/orders")
async def create_order(order: OrderCreate, request: Request):
    """Create a new order"""
    # Rate limiting: Check if allowed
    is_allowed, message = await rate_limiter.check_rate_limit(request, "order")
    if not is_allowed:
        raise HTTPException(status_code=429, detail=message)
    
    # Verify location exists (try both UUID 'id' field and ObjectId '_id' field)
    location = await db.locations.find_one({"id": order.location_id, "active": True})
    if not location:
        # Fallback: try as ObjectId
        try:
            location = await db.locations.find_one({"_id": ObjectId(order.location_id), "active": True})
        except:
            pass
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Check if delivery zone is configured
    delivery_zone = location.get('delivery_zone', {})
    customer_postal_code = order.customer.postal_code
    
    # Skip delivery zone validation for pickup orders
    is_pickup = getattr(order, 'is_pickup', False)
    
    if not is_pickup:
        # Validate postal code is in delivery zone (only for delivery)
        if delivery_zone and customer_postal_code not in delivery_zone.get('postal_codes', []):
            raise HTTPException(
                status_code=400,
                detail=f"Wir liefern leider nicht nach {customer_postal_code}. Bitte wähle einen anderen Standort oder prüfe deine Postleitzahl."
            )
    
    # Calculate totals using location-specific settings
    subtotal = sum(item.price * item.quantity for item in order.items)
    
    # For pickup, no delivery fee or minimum order checks
    if is_pickup:
        min_order_value = 0.0
        delivery_fee = 0.0
    else:
        min_order_value = delivery_zone.get('min_order_value', 0.0) if delivery_zone else 0.0
        delivery_fee_amount = delivery_zone.get('delivery_fee', 2.50) if delivery_zone else 2.50
        free_delivery_threshold = delivery_zone.get('free_delivery_threshold', 15.0) if delivery_zone else 15.0
        delivery_fee = delivery_fee_amount if subtotal < free_delivery_threshold else 0.0
    
    # Check minimum order value (skip for pickup)
    if not is_pickup and subtotal < min_order_value:
        raise HTTPException(
            status_code=400,
            detail=f"Mindestbestellwert: €{min_order_value:.2f}. Deine Bestellung: €{subtotal:.2f}"
        )
    
    # ===== LOYALTY: Apply points redemption =====
    points_discount = 0.0
    points_redeemed = 0
    
    if hasattr(order, 'points_to_redeem') and order.points_to_redeem > 0:
        # Check customer's loyalty account
        loyalty_account = await db.loyalty_accounts.find_one({"customer_email": order.customer.email})
        
        if loyalty_account and loyalty_account.get("points", 0) >= order.points_to_redeem:
            # Calculate discount: 1 point = 0.50€
            points_discount = order.points_to_redeem * 0.50
            points_redeemed = order.points_to_redeem
            
            # Don't allow discount to exceed total
            if points_discount > (subtotal + delivery_fee):
                points_discount = subtotal + delivery_fee
                points_redeemed = int(points_discount / 0.50)
        else:
            raise HTTPException(status_code=400, detail="Nicht genügend Punkte verfügbar")
    
    total = subtotal + delivery_fee - points_discount
    
    # Generate order number
    count = await db.orders.count_documents({})
    order_number = f"ZOZO-{count + 1001}"
    
    # Create order document
    order_doc = {
        "location_id": order.location_id,
        "location_slug": location.get('slug', ''),  # Store slug for POS retry
        "order_number": order_number,
        "items": [item.dict() for item in order.items],
        "subtotal": round(subtotal, 2),
        "delivery_fee": round(delivery_fee, 2),
        "discount": round(points_discount, 2),
        "points_redeemed": points_redeemed,
        "total": round(total, 2),
        "customer": order.customer.dict(),
        "is_pickup": getattr(order, 'is_pickup', False),
        "status": "confirmed",
        "payment_method": order.payment_method,
        "estimated_time": 30,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "status_history": [{
            "status": "confirmed",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Bestellung wurde bestätigt"
        }],
        "pos_status": "pending"  # Initial POS status
    }
    
    result = await db.orders.insert_one(order_doc)
    order_doc['_id'] = result.inserted_id
    
    # ===== LOYALTY SYSTEM: Award points and check achievements =====
    points_earned = 0
    try:
        customer_email = order.customer.email
        
        # Ensure loyalty account exists
        await get_or_create_loyalty_account(customer_email)
        
        # Deduct redeemed points first
        if points_redeemed > 0:
            await add_points_to_account(
                customer_email,
                -points_redeemed,
                f"Eingelöst bei Bestellung {order_number}",
                order_id=str(result.inserted_id)
            )
        
        # Calculate points earned: 10€ = 1 point (so total/10)
        # Note: Points are earned on the FINAL total (after discount)
        points_earned = int(total / 10)
        
        if points_earned > 0:
            # Add earned points
            await add_points_to_account(
                customer_email,
                points_earned,
                f"Verdient bei Bestellung {order_number}",
                order_id=str(result.inserted_id)
            )
        
        # Check and unlock achievements
        unlocked_achievements = await check_achievements(
            customer_email,
            total,
            [item.dict() for item in order.items],
            datetime.utcnow()
        )
        
        # Store achievement info in order for notification purposes
        if unlocked_achievements:
            await db.orders.update_one(
                {"_id": result.inserted_id},
                {"$set": {"unlocked_achievements": unlocked_achievements}}
            )
        
    except Exception as e:
        # Log error but don't fail order creation
        print(f"Loyalty points award failed: {str(e)}")
    
    # ===== POS INTEGRATION: Auto-push to configured POS system =====
    # ONLY for non-PayPal orders - PayPal orders will be pushed after payment capture
    if order.payment_method != 'paypal':
        try:
            # Build POS order data
            pos_order_data = {
            "order_id": str(result.inserted_id),
            "order_number": order_number,
            "customer_name": order.customer.name,
            "customer_email": order.customer.email if hasattr(order.customer, 'email') else None,
            "customer_phone": order.customer.phone,
            "items": [
                {
                    "product_id": item.menu_item_id,
                    "name": item.name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "size": item.size
                }
                for item in order.items
            ],
            "total": round(total, 2),
            "delivery_type": "pickup" if getattr(order, 'is_pickup', False) else "delivery",
            "delivery_address": f"{order.customer.address}, {order.customer.postal_code} {order.customer.city}",
            "payment_method": order.payment_method,
            "notes": order.customer.notes if hasattr(order.customer, 'notes') else ""
            }
            
            # Push to POS via service (uses location's pos_config)
            pos_result = await pos_service.push_order(pos_order_data, location.get('slug', ''))
            
            # Update order with POS status
            pos_update = {
                "pos_status": pos_result.get('pos_status', 'not_applicable'),
                "pos_pushed_at": datetime.utcnow() if pos_result.get('success') else None,
                "pos_order_id": pos_result.get('pos_order_id'),
                "pos_is_test_mode": pos_result.get('is_test_mode', True)
            }
            
            if not pos_result.get('success') and pos_result.get('pos_status') == 'error':
                pos_update["pos_error"] = pos_result.get('message', 'Unknown error')
            
            await db.orders.update_one(
                {"_id": result.inserted_id},
                {"$set": pos_update}
            )
            
        except Exception as e:
            # Log error but don't fail the order creation
            logging.error(f"POS auto-push failed: {str(e)}")
    
    # ===== EMAIL: Send confirmation email =====
    try:
        from email_service import send_order_confirmation_email
        send_order_confirmation_email(order_doc, location)
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
    
    # Add loyalty info to response
    response = serialize_doc(order_doc)
    if points_earned > 0:
        response['points_earned'] = points_earned
    if 'unlocked_achievements' in order_doc:
        response['unlocked_achievements'] = order_doc['unlocked_achievements']
    
    return response

@api_router.get("/order-status/{order_number}")
async def get_order_status(order_number: str):
    """Public endpoint: Get order status by order number"""
    order = await db.orders.find_one({"order_number": order_number})
    
    if not order:
        raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")
    
    # Get location info
    location = await db.locations.find_one({"_id": ObjectId(order['location_id'])})
    location_name = location.get('name', 'Unknown') if location else 'Unknown'
    
    # Return public order info (hide sensitive data)
    return {
        "order_number": order['order_number'],
        "status": order['status'],
        "is_pickup": order.get('is_pickup', False),
        "estimated_time": order.get('estimated_time', 30),
        "created_at": order['created_at'].isoformat() if isinstance(order['created_at'], datetime) else order['created_at'],
        "location_name": location_name,
        "total": order['total'],
        "status_history": order.get('status_history', [])
    }

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
        use_test_mode=location_settings.get('expertorder_test_mode', False),
        merchant_id=location_settings.get('expertorder_merchant_id', 'c102285'),
        base_url=location_settings.get('expertorder_base_url')
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
        use_test_mode=True,  # Always use test mode for connection tests
        merchant_id=location_settings.get('expertorder_merchant_id', 'c102285'),
        base_url=location_settings.get('expertorder_base_url')
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
    admin: dict = Depends(get_current_admin)
):
    """Get orders with optional filters"""
    query = {}
    
    # If admin has restricted branch access, filter by those branches
    branch_ids = admin.get('branch_ids', [])
    if branch_ids:
        query["location_id"] = {"$in": branch_ids}
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
    
    # Update order with status history
    status_entry = {
        "status": update.status,
        "timestamp": datetime.utcnow().isoformat(),
        "note": f"Status geändert zu {update.status}"
    }
    
    result = await db.orders.update_one(
        {"_id": parse_object_id(order_id)},
        {
            "$set": {"status": update.status, "updated_at": datetime.utcnow()},
            "$push": {"status_history": status_entry}
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    updated_order = await db.orders.find_one({"_id": parse_object_id(order_id)})
    
    # ===== EMAIL: Send status update email =====
    try:
        if updated_order.get('customer', {}).get('email'):
            location = await db.locations.find_one({"_id": parse_object_id(order['location_id'])})
            if location:
                send_status_update_email(updated_order, update.status, location)
    except Exception as e:
        print(f"Status update email failed: {str(e)}")
    
    return serialize_doc(updated_order)

# Menu Management
# Admin Products/Menu Items Routes (same endpoint, different names for compatibility)
@api_router.get("/admin/products")
@api_router.get("/admin/menu-items")
async def get_all_menu_items(
    location_id: Optional[str] = None,
    category_id: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """Get all menu items (admin)"""
    query = {}
    
    # Filter by admin's branch access if applicable
    branch_ids = admin.get('branch_ids', [])
    if branch_ids:
        query["$or"] = [
            {"location_id": None},
            {"location_id": {"$in": branch_ids}}
        ]
    elif location_id:
        query["location_id"] = location_id
    
    if category_id:
        query["category_id"] = category_id
    
    items = await db.menu_items.find(query).to_list(length=1000)
    return {"products": serialize_doc(items)}

@api_router.post("/admin/products")
@api_router.post("/admin/menu-items")
async def create_menu_item(
    item: MenuItemCreate,
    admin: dict = Depends(get_current_admin)
):
    """Create a new menu item"""
    item_doc = item.dict()
    
    # If admin has specific branch access, set location_id
    branch_ids = admin.get('branch_ids', [])
    if branch_ids and len(branch_ids) == 1:
        item_doc['location_id'] = branch_ids[0]
    
    result = await db.menu_items.insert_one(item_doc)
    item_doc['_id'] = result.inserted_id
    return serialize_doc(item_doc)

@api_router.patch("/admin/menu-items/{item_id}/featured")
async def update_featured_status(
    item_id: str,
    is_featured: bool,
    badge: Optional[str] = None,
    featured_order: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """Update featured status and badge for menu item"""
    item = await db.menu_items.find_one({"_id": parse_object_id(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    update_data = {"is_featured": is_featured}
    if badge is not None:
        update_data["badge"] = badge
    if featured_order is not None:
        update_data["featured_order"] = featured_order
    
    await db.menu_items.update_one(
        {"_id": parse_object_id(item_id)},
        {"$set": update_data}
    )
    
    updated_item = await db.menu_items.find_one({"_id": parse_object_id(item_id)})
    return serialize_doc(updated_item)

@api_router.put("/admin/products/{item_id}")
@api_router.patch("/admin/menu-items/{item_id}")
async def update_menu_item(
    item_id: str,
    update: MenuItemUpdate,
    admin: dict = Depends(get_current_admin)
):
    """Update menu item"""
    # Check if item exists
    item = await db.menu_items.find_one({"_id": parse_object_id(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Check access - admin can upload for their branches
    branch_ids = admin.get('branch_ids', [])
    if branch_ids and item.get('location_id'):
        if item['location_id'] not in branch_ids:
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
@api_router.post("/admin/products/{item_id}/upload-image")
@api_router.post("/admin/menu-items/{item_id}/upload-image")
async def upload_product_image(
    item_id: str,
    file: UploadFile = File(...),
    admin: dict = Depends(get_current_admin)
):
    """Upload product image for menu item"""
    import os
    import uuid
    from pathlib import Path
    
    # Check if item exists
    item = await db.menu_items.find_one({"_id": parse_object_id(item_id)})
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Check access - admin can upload for their branches
    branch_ids = admin.get('branch_ids', [])
    if branch_ids and item.get('location_id'):
        if item['location_id'] not in branch_ids:
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

# Discount Codes Management
@api_router.post("/admin/discount-codes")
async def create_discount_code(
    code_data: DiscountCodeCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new discount code"""
    # Check if code already exists
    existing = await db.discount_codes.find_one({"code": code_data.code.upper()})
    if existing:
        raise HTTPException(status_code=400, detail="Code already exists")
    
    # Prepare document
    code_doc = {
        "id": str(uuid.uuid4()),
        "code": code_data.code.upper(),
        "description": code_data.description,
        "discount_type": code_data.discount_type,
        "discount_value": code_data.discount_value,
        "min_order_value": code_data.min_order_value or 0,
        "order_type": code_data.order_type,
        "max_uses": code_data.max_uses,
        "current_uses": 0,
        "valid_from": code_data.valid_from,
        "valid_until": code_data.valid_until,
        "location_ids": code_data.location_ids,
        "active": code_data.active,
        "created_by": current_user.get('email'),
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.discount_codes.insert_one(code_doc)
    return serialize_doc(code_doc)

@api_router.get("/admin/discount-codes")
async def get_discount_codes(
    current_user: dict = Depends(get_current_user)
):
    """Get all discount codes"""
    cursor = db.discount_codes.find().sort("created_at", -1)
    codes = await cursor.to_list(length=1000)
    return serialize_doc(codes)

@api_router.patch("/admin/discount-codes/{code_id}")
async def update_discount_code(
    code_id: str,
    code_data: DiscountCodeUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a discount code"""
    update_data = {k: v for k, v in code_data.dict().items() if v is not None}
    
    if "code" in update_data:
        update_data["code"] = update_data["code"].upper()
    
    await db.discount_codes.update_one(
        {"id": code_id},
        {"$set": update_data}
    )
    
    updated_code = await db.discount_codes.find_one({"id": code_id})
    return serialize_doc(updated_code)

@api_router.delete("/admin/discount-codes/{code_id}")
async def delete_discount_code(
    code_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a discount code"""
    result = await db.discount_codes.delete_one({"id": code_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Code not found")
    return {"success": True}

# Validate Discount Code (Public)
@api_router.post("/validate-discount-code")
async def validate_discount_code(validation: DiscountCodeValidate):
    """Validate a discount code"""
    code = await db.discount_codes.find_one({"code": validation.code.upper(), "active": True})
    
    if not code:
        return {"valid": False, "message": "Ungültiger Rabattcode"}
    
    # Check valid dates
    now = datetime.now(timezone.utc)
    if code.get("valid_from") and now < code["valid_from"]:
        return {"valid": False, "message": "Code ist noch nicht gültig"}
    if code.get("valid_until") and now > code["valid_until"]:
        return {"valid": False, "message": "Code ist abgelaufen"}
    
    # Check usage limit
    if code.get("max_uses") and code.get("current_uses", 0) >= code["max_uses"]:
        return {"valid": False, "message": "Code wurde bereits zu oft verwendet"}
    
    # Check minimum order value
    if validation.order_total < code.get("min_order_value", 0):
        return {
            "valid": False, 
            "message": f"Mindestbestellwert von €{code['min_order_value']:.2f} nicht erreicht"
        }
    
    # Check order type (pickup/delivery)
    if code.get("order_type") and code["order_type"] != validation.order_type:
        order_type_text = "Abholung" if code["order_type"] == "pickup" else "Lieferung"
        return {"valid": False, "message": f"Code nur für {order_type_text} gültig"}
    
    # Check location
    if code.get("location_ids") and len(code["location_ids"]) > 0:
        if validation.location_id not in code["location_ids"]:
            return {"valid": False, "message": "Code nicht für diesen Standort gültig"}
    
    # Calculate discount
    if code["discount_type"] == "percentage":
        discount_amount = (validation.order_total * code["discount_value"]) / 100
    else:  # fixed
        discount_amount = code["discount_value"]
    
    # Don't discount more than order total
    discount_amount = min(discount_amount, validation.order_total)
    
    return {
        "valid": True,
        "code_id": code["id"],
        "discount_type": code["discount_type"],
        "discount_value": code["discount_value"],
        "discount_amount": discount_amount,
        "message": f"Rabatt angewendet: €{discount_amount:.2f}"
    }

# Dashboard Stats
@api_router.get("/admin/stats")
async def get_dashboard_stats(
    location_id: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """Get dashboard statistics"""
    query = {}
    
    # If admin has restricted branch access, filter by those branches
    branch_ids = admin.get('branch_ids', [])
    if branch_ids:
        query["location_id"] = {"$in": branch_ids}
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
    
    # Get current location (try both UUID 'id' field and ObjectId '_id' field)
    location = await db.locations.find_one({"id": location_id})
    if not location:
        try:
            location = await db.locations.find_one({"_id": parse_object_id(location_id)})
        except:
            pass
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Use the actual _id for updates
    location_object_id = location['_id']
    
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
        {"_id": location_object_id},
        {"$set": {"delivery_zone": current_zone}}
    )
    
    updated_location = await db.locations.find_one({"_id": location_object_id})
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


# ==================== LOYALTY SYSTEM ENDPOINTS ====================

# Achievements Configuration
ACHIEVEMENTS = [
    {
        "id": "first_order",
        "name": "Erster Biss",
        "description": "Deine erste Bestellung abgeschlossen",
        "icon": "🎯",
        "bonus_points": 5,
        "category": "orders"
    },
    {
        "id": "loyal_customer",
        "name": "Stammkunde",
        "description": "10 Bestellungen abgeschlossen",
        "icon": "⭐",
        "bonus_points": 10,
        "category": "orders"
    },
    {
        "id": "burger_master",
        "name": "Burger-Meister",
        "description": "50 Burger bestellt",
        "icon": "🍔",
        "bonus_points": 20,
        "category": "variety"
    },
    {
        "id": "midnight_snacker",
        "name": "Mitternachts-Snacker",
        "description": "Bestellung nach 22 Uhr aufgegeben",
        "icon": "🌙",
        "bonus_points": 5,
        "category": "time"
    },
    {
        "id": "variety_lover",
        "name": "Vielfalt-Lover",
        "description": "Aus 3+ verschiedenen Kategorien in einer Bestellung",
        "icon": "🎨",
        "bonus_points": 8,
        "category": "variety"
    },
    {
        "id": "custom_king",
        "name": "Custom King",
        "description": "5 eigene Burger kreiert",
        "icon": "👑",
        "bonus_points": 15,
        "category": "custom"
    },
    {
        "id": "big_spender",
        "name": "Großbestellung",
        "description": "Bestellung über 50€",
        "icon": "💎",
        "bonus_points": 25,
        "category": "spending"
    }
]

# Helper: Get or create loyalty account
async def get_or_create_loyalty_account(customer_email: str):
    account = await db.loyalty_accounts.find_one({"customer_email": customer_email})
    if not account:
        account = {
            "customer_email": customer_email,
            "points": 0,
            "total_earned": 0,
            "total_spent": 0,
            "achievements": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.loyalty_accounts.insert_one(account)
        account["_id"] = result.inserted_id
    return account

# Helper: Add points to account
async def add_points_to_account(customer_email: str, points: int, description: str, order_id: str = None, achievement_id: str = None):
    # Create transaction
    transaction = {
        "customer_email": customer_email,
        "type": "earned" if points > 0 else "spent",
        "points": points,
        "description": description,
        "order_id": order_id,
        "related_achievement": achievement_id,
        "created_at": datetime.utcnow()
    }
    await db.loyalty_transactions.insert_one(transaction)
    
    # Update account
    await db.loyalty_accounts.update_one(
        {"customer_email": customer_email},
        {
            "$inc": {
                "points": points,
                "total_earned": points if points > 0 else 0,
                "total_spent": abs(points) if points < 0 else 0
            },
            "$set": {"updated_at": datetime.utcnow()}
        }
    )

# Helper: Check and unlock achievements
async def check_achievements(customer_email: str, order_total: float, order_items: list, order_time: datetime):
    account = await get_or_create_loyalty_account(customer_email)
    unlocked = []
    
    # Get order count
    order_count = await db.orders.count_documents({"customer.email": customer_email})
    
    # Get custom burger count


# ==================== EMAIL VERIFICATION ENDPOINTS ====================

import random
import string
from datetime import timedelta
from email_service import send_verification_email, send_status_update_email, send_review_request_email

class EmailVerificationRequest(BaseModel):
    email: str

class EmailVerificationCheck(BaseModel):
    email: str
    code: str

@api_router.post("/email/send-verification")
async def send_email_verification(request: EmailVerificationRequest):
    """Send verification code to email"""
    try:
        # Generate 6-digit code
        code = ''.join(random.choices(string.digits, k=6))
        
        # Store in database with 10-minute expiry
        verification_doc = {
            "email": request.email,
            "code": code,
            "verified": False,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        }
        
        # Delete old verification codes for this email
        await db.email_verifications.delete_many({"email": request.email})
        
        # Insert new verification
        await db.email_verifications.insert_one(verification_doc)
        
        # Send email
        success = send_verification_email(request.email, code)
        
        if not success:
            raise HTTPException(status_code=500, detail="E-Mail konnte nicht gesendet werden")
        
        return {"message": "Verifizierungscode wurde gesendet", "email": request.email}
        
    except Exception as e:
        print(f"Verification email error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/email/verify-code")
async def verify_email_code(request: EmailVerificationCheck):
    """Verify email with code"""
    try:
        # Find verification record
        verification = await db.email_verifications.find_one({
            "email": request.email,
            "code": request.code,
            "verified": False
        })
        
        if not verification:
            raise HTTPException(status_code=400, detail="Ungültiger Verifizierungscode")
        
        # Check if expired
        if datetime.utcnow() > verification['expires_at']:
            raise HTTPException(status_code=400, detail="Verifizierungscode abgelaufen")
        
        # Mark as verified
        await db.email_verifications.update_one(
            {"_id": verification['_id']},
            {"$set": {"verified": True}}
        )
        
        return {"message": "E-Mail erfolgreich verifiziert", "email": request.email}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Verification check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/email/is-verified/{email}")
async def check_email_verified(email: str):
    """Check if email is verified"""
    verification = await db.email_verifications.find_one({
        "email": email,
        "verified": True
    })
    
    return {"verified": verification is not None, "email": email}

# ==================== SCHEDULED EMAIL TASKS ====================

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()

async def check_and_send_review_emails():
    """Check for orders delivered 2 hours ago and send review requests"""
    try:
        two_hours_ago = datetime.utcnow() - timedelta(hours=2)
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        
        # Find orders delivered around 2 hours ago that haven't received review email
        orders = await db.orders.find({
            "status": "delivered",
            "updated_at": {
                "$gte": two_hours_ago,
                "$lte": five_minutes_ago
            },
            "review_email_sent": {"$ne": True}
        }).to_list(length=100)
        
        for order in orders:
            try:
                # Get location
                location = await db.locations.find_one({"_id": ObjectId(order['location_id'])})
                
                if location and order.get('customer', {}).get('email'):
                    # Send review request
                    success = send_review_request_email(order, location)
                    
                    if success:
                        # Mark as sent
                        await db.orders.update_one(
                            {"_id": order['_id']},
                            {"$set": {"review_email_sent": True}}
                        )
                        print(f"Review email sent for order {order.get('order_number')}")
                        
            except Exception as e:
                print(f"Error sending review email for order {order.get('_id')}: {str(e)}")
                
    except Exception as e:
        print(f"Error in review email task: {str(e)}")

# Start scheduler
@app.on_event("startup")
async def start_scheduler():
    """Start the background scheduler for email tasks"""
    # Run every 5 minutes
    scheduler.add_job(
        check_and_send_review_emails,
        IntervalTrigger(minutes=5),
        id='review_email_task',
        name='Send review request emails',
        replace_existing=True
    )
    scheduler.start()
    print("Email scheduler started")

@app.on_event("shutdown")
async def shutdown_scheduler():
    """Shutdown the scheduler"""
    scheduler.shutdown()


# ==================== SOCIAL ORDERING ENDPOINTS ====================

import secrets

def generate_group_code():
    """Generate unique 6-character group code"""
    return secrets.token_urlsafe(6)[:6].upper()

@api_router.post("/group-orders/create")
async def create_group_order(host_name: str, location_id: str, host_email: str = None):
    """Create a new group order session"""
    try:
        group_code = generate_group_code()
        
        # Ensure unique code
        while await db.group_orders.find_one({"group_code": group_code}):
            group_code = generate_group_code()
        
        group_order = {
            "group_code": group_code,
            "host_name": host_name,
            "host_email": host_email,
            "location_id": location_id,
            "items": [],
            "participants": [],
            "status": "active",
            "expires_at": datetime.utcnow() + timedelta(hours=1),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.group_orders.insert_one(group_order)
        group_order["_id"] = result.inserted_id
        
        return serialize_doc(group_order)
        
    except Exception as e:
        print(f"Error creating group order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/group-orders/{group_code}")
async def get_group_order(group_code: str):
    """Get group order by code"""
    group_order = await db.group_orders.find_one({"group_code": group_code.upper()})
    
    if not group_order:
        raise HTTPException(status_code=404, detail="Gruppenbestellung nicht gefunden")
    
    # Check if expired
    if datetime.utcnow() > group_order["expires_at"]:
        await db.group_orders.update_one(
            {"_id": group_order["_id"]},
            {"$set": {"status": "expired"}}
        )
        group_order["status"] = "expired"
    
    return serialize_doc(group_order)

@api_router.post("/group-orders/{group_code}/add-items")
async def add_items_to_group_order(group_code: str, data: GroupOrderAddItems):
    """Add items to group order"""
    try:
        group_order = await db.group_orders.find_one({"group_code": group_code.upper()})
        
        if not group_order:
            raise HTTPException(status_code=404, detail="Gruppenbestellung nicht gefunden")
        
        if group_order["status"] != "active":
            raise HTTPException(status_code=400, detail="Diese Gruppenbestellung ist nicht mehr aktiv")
        
        if datetime.utcnow() > group_order["expires_at"]:
            raise HTTPException(status_code=400, detail="Diese Gruppenbestellung ist abgelaufen")
        
        # Add items to group
        participant_info = {
            "name": data.participant_name,
            "items_added": len(data.items),
            "added_at": datetime.utcnow()
        }
        
        await db.group_orders.update_one(
            {"_id": group_order["_id"]},
            {
                "$push": {
                    "items": {"$each": data.items},
                    "participants": participant_info
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        # Get updated group order
        updated = await db.group_orders.find_one({"_id": group_order["_id"]})
        return serialize_doc(updated)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding items to group order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class GroupOrderInvite(BaseModel):
    email: str
    sender_name: Optional[str] = None

@api_router.post("/group-orders/{group_code}/invite")
async def invite_to_group_order(group_code: str, data: GroupOrderInvite):
    """Send email invitation to join group order"""
    try:
        group_order = await db.group_orders.find_one({"group_code": group_code.upper()})
        
        if not group_order:
            raise HTTPException(status_code=404, detail="Gruppenbestellung nicht gefunden")
        
        if group_order["status"] != "active":
            raise HTTPException(status_code=400, detail="Diese Gruppenbestellung ist nicht mehr aktiv")
        
        # Check if expired
        if datetime.utcnow() > group_order["expires_at"]:
            raise HTTPException(status_code=400, detail="Diese Gruppenbestellung ist abgelaufen")
        
        # Send invitation email
        from email_service import send_group_order_invite_email
        
        app_url = os.environ.get('APP_URL', 'http://localhost:3000')
        share_link = f"{app_url}/group-order/{group_code.upper()}"
        sender_name = data.sender_name or group_order.get("host_name", "Ein Freund")
        
        success = send_group_order_invite_email(
            to_email=data.email,
            group_code=group_code.upper(),
            host_name=sender_name,
            share_link=share_link
        )
        
        if success:
            return {"success": True, "message": f"Einladung an {data.email} gesendet"}
        else:
            raise HTTPException(status_code=500, detail="Fehler beim Senden der Einladung. Bitte versuche es erneut.")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending group order invite: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/group-orders/{group_code}/finalize")
async def finalize_group_order(group_code: str):
    """Finalize group order (host only) and create actual order"""
    try:
        group_order = await db.group_orders.find_one({"group_code": group_code.upper()})
        
        if not group_order:
            raise HTTPException(status_code=404, detail="Gruppenbestellung nicht gefunden")
        
        if group_order["status"] != "active":
            raise HTTPException(status_code=400, detail="Diese Gruppenbestellung wurde bereits finalisiert")
        
        # Mark as finalized
        await db.group_orders.update_one(
            {"_id": group_order["_id"]},
            {"$set": {"status": "finalized", "updated_at": datetime.utcnow()}}
        )
        
        # Return the group order items for checkout
        return serialize_doc(group_order)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error finalizing group order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/group-orders/{group_code}/remove-item/{item_index}")
async def remove_item_from_group_order(group_code: str, item_index: int):
    """Remove an item from group order"""
    try:
        group_order = await db.group_orders.find_one({"group_code": group_code.upper()})
        
        if not group_order:
            raise HTTPException(status_code=404, detail="Gruppenbestellung nicht gefunden")
        
        if group_order["status"] != "active":
            raise HTTPException(status_code=400, detail="Diese Gruppenbestellung ist nicht mehr aktiv")
        
        # Remove item by index
        items = group_order.get("items", [])
        if 0 <= item_index < len(items):
            items.pop(item_index)
            
            await db.group_orders.update_one(
                {"_id": group_order["_id"]},
                {
                    "$set": {
                        "items": items,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        updated = await db.group_orders.find_one({"_id": group_order["_id"]})
        return serialize_doc(updated)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error removing item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get loyalty account
@api_router.get("/loyalty/account/{email}")
async def get_loyalty_account(email: str):
    """Get loyalty account for a customer"""
    account = await get_or_create_loyalty_account(email)
    return serialize_doc(account)

# Get loyalty transactions
@api_router.get("/loyalty/transactions/{email}")
async def get_loyalty_transactions(email: str, limit: int = 20):
    """Get loyalty transaction history for a customer"""
    transactions = await db.loyalty_transactions.find(
        {"customer_email": email}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    return serialize_doc(transactions)

# Get available achievements
@api_router.get("/loyalty/achievements")
async def get_achievements():
    """Get all available achievements"""
    return ACHIEVEMENTS

# Get rewards catalog (menu items with points prices)
@api_router.get("/loyalty/rewards")
async def get_rewards_catalog():
    """Get all menu items as redeemable rewards with points prices"""
    # Get all active menu items
    items = await db.menu_items.find({"active": True}).to_list(length=1000)
    
    rewards = []
    for item in items:
        # Calculate points needed: price * 2 (since 1 point = 0.50€, so 1€ = 2 points)
        price_normal = item.get("price_normal") or item.get("price_medium") or item.get("price_large", 0)
        points_needed = int(price_normal * 2)
        
        reward = {
            "id": str(item["_id"]),
            "name": item.get("name"),
            "description": item.get("description"),
            "category_id": str(item.get("category_id")),
            "image": item.get("image"),
            "price_euro": price_normal,
            "points_needed": points_needed
        }
        rewards.append(reward)
    
    return rewards


# ============================================================================
# ADMIN AUTHENTICATION & AUTHORIZATION ENDPOINTS
# ============================================================================

@api_router.post("/admin/auth/login", response_model=AdminLoginResponse)
async def admin_login(request: AdminLoginRequest, http_request: Request):
    """Admin login endpoint with role-based authentication and rate limiting"""
    try:
        # Check rate limit FIRST
        client_ip = http_request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or \
                   http_request.headers.get("X-Real-IP", "") or \
                   (http_request.client.host if http_request.client else "unknown")
        
        allowed, message = await rate_limiter.check_rate_limit(http_request, "admin_login")
        if not allowed:
            await audit_service.log_action(
                actor_email=request.email,
                action=AuditAction.LOGIN_FAILED.value,
                result="failure",
                category=AuditCategory.SECURITY.value,
                ip_address=client_ip,
                details={"reason": "rate_limit_exceeded"}
            )
            raise HTTPException(status_code=429, detail=message)
        
        # Find admin by email
        admin = await db.admins.find_one({"email": request.email})
        
        if not admin:
            # Record failed attempt for rate limiting
            await rate_limiter.record_attempt(http_request, "admin_login", success=False)
            
            # Log failed attempt
            await audit_service.log_action(
                actor_email=request.email,
                action=AuditAction.LOGIN_FAILED.value,
                result="failure",
                category=AuditCategory.AUTH.value,
                ip_address=client_ip,
                details={"reason": "Admin not found"}
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if admin is active
        if not admin.get("is_active", True):
            await rate_limiter.record_attempt(http_request, "admin_login", success=False)
            await audit_service.log_action(
                actor_email=request.email,
                action=AuditAction.LOGIN_FAILED.value,
                result="failure",
                category=AuditCategory.AUTH.value,
                ip_address=client_ip,
                details={"reason": "Account inactive"}
            )
            raise HTTPException(status_code=403, detail="Account is inactive")
        
        # Verify password
        if not AdminAuth.verify_password(request.password, admin["password_hash"]):
            await rate_limiter.record_attempt(http_request, "admin_login", success=False)
            await audit_service.log_action(
                actor_email=request.email,
                action=AuditAction.LOGIN_FAILED.value,
                result="failure",
                category=AuditCategory.AUTH.value,
                ip_address=client_ip,
                details={"reason": "Invalid password"}
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # 2FA/Passkey entfernt - nicht benötigt für Go-Live
        
        # Create JWT token
        token = AdminAuth.create_token(
            email=admin["email"],
            role=admin["role"],
            branch_ids=admin.get("branch_ids", [])
        )
        
        # Update last login
        await db.admins.update_one(
            {"_id": admin["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Record successful login (resets rate limit counter)
        await rate_limiter.record_attempt(http_request, "admin_login", success=True)
        
        # Log successful login
        await audit_service.log_action(
            actor_email=request.email,
            action=AuditAction.LOGIN_SUCCESS.value,
            result="success",
            category=AuditCategory.AUTH.value,
            ip_address=client_ip,
            details={"role": admin["role"]}
        )
        
        # Prepare admin response (ohne Passkey-Felder)
        admin_response = {
            "id": str(admin["_id"]),
            "email": admin["email"],
            "name": admin["name"],
            "role": admin["role"],
            "branch_ids": admin.get("branch_ids", []),
            "permissions": AdminAuth.get_permissions(admin["role"]),
            "must_change_password": admin.get("must_change_password", True)
        }
        
        return AdminLoginResponse(
            access_token=token,
            token_type="bearer",
            admin=admin_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Admin login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")


@api_router.get("/admin/auth/me")
async def get_current_admin_info(admin: dict = Depends(get_current_admin)):
    """Get current admin info from token"""
    # Fetch full admin details from database
    admin_doc = await db.admins.find_one({"email": admin["email"]})
    
    if not admin_doc:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return {
        "id": str(admin_doc["_id"]),
        "email": admin_doc["email"],
        "name": admin_doc["name"],
        "role": admin_doc["role"],
        "branch_ids": admin_doc.get("branch_ids", []),
        "permissions": admin["permissions"],
        "totp_enabled": admin_doc.get("totp_enabled", False),
        "last_login": admin_doc.get("last_login")
    }


@api_router.post("/admin/auth/change-password")
async def change_admin_password(
    request: PasswordChangeRequest,
    admin: dict = Depends(get_current_admin)
):
    """Change admin password"""
    # Get admin from database
    admin_doc = await db.admins.find_one({"email": admin["email"]})
    
    if not admin_doc:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # Verify current password
    if not AdminAuth.verify_password(request.current_password, admin_doc["password_hash"]):
        await audit_service.log_action(
            actor_email=admin["email"],
            action="password_change",
            result="failure",
            details={"reason": "Invalid current password"}
        )
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    # Hash new password
    new_hash = AdminAuth.hash_password(request.new_password)
    
    # Update password
    await db.admins.update_one(
        {"_id": admin_doc["_id"]},
        {"$set": {"password_hash": new_hash}}
    )
    
    # Log successful change
    await audit_service.log_action(
        actor_email=admin["email"],
        action="password_change",
        result="success"
    )
    
    return {"message": "Password changed successfully"}


# ============================================================================
# POS INTEGRATION ENDPOINTS
# ============================================================================

class POSConfigUpdate(BaseModel):
    """Request model for updating POS configuration"""
    provider: str = "none"  # "none", "expertorder", "cashx"
    test_mode: bool = True
    api_key: Optional[str] = None
    merchant_id: Optional[str] = None
    username: Optional[str] = None
    secret: Optional[str] = None
    base_url: Optional[str] = None
    terminal_id: Optional[str] = None  # Cash-X Terminal ID
    settings: Optional[dict] = None

class POSTestRequest(BaseModel):
    """Request model for POS connection test"""
    simulate_failure: bool = False


@api_router.get("/admin/locations/{slug}/pos/config")
async def get_pos_config(
    slug: str,
    admin: dict = Depends(get_current_admin)
):
    """Get POS configuration for a location (secrets masked)"""
    try:
        # Check access - Branch admins can view their own location's config
        if admin["role"] != "super_admin":
            if slug not in admin.get("branch_ids", []):
                raise HTTPException(status_code=403, detail="Zugriff auf diesen Standort verweigert")
        
        location = await db.locations.find_one({"slug": slug})
        if not location:
            raise HTTPException(status_code=404, detail="Standort nicht gefunden")
        
        pos_config = location.get('pos_config', {
            "provider": "none",
            "status": "disconnected",
            "test_mode": True,
            "credentials": {},
            "settings": {}
        })
        
        # Return config with masked credentials
        credentials = pos_config.get('credentials', {})
        return {
            "provider": pos_config.get('provider', 'none'),
            "status": pos_config.get('status', 'disconnected'),
            "test_mode": pos_config.get('test_mode', True),
            "has_api_key": bool(credentials.get('api_key')),
            "has_merchant_id": bool(credentials.get('merchant_id')),
            "has_username": bool(credentials.get('username')),
            "has_secret": bool(credentials.get('secret')),
            "base_url": credentials.get('base_url'),
            "settings": pos_config.get('settings', {}),
            "last_sync_at": pos_config.get('last_sync_at'),
            "last_error": pos_config.get('last_error'),
            "last_error_at": pos_config.get('last_error_at'),
            "updated_at": pos_config.get('updated_at'),
            "updated_by": pos_config.get('updated_by')
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get POS config error: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der POS-Konfiguration")


@api_router.put("/admin/locations/{slug}/pos/config")
async def update_pos_config(
    slug: str,
    config: POSConfigUpdate,
    admin: dict = Depends(get_current_admin)
):
    """Update POS configuration for a location"""
    try:
        # Check access - Super Admin can update all, Branch Admin only their own
        if admin["role"] != "super_admin":
            if slug not in admin.get("branch_ids", []):
                raise HTTPException(status_code=403, detail="Zugriff auf diesen Standort verweigert")
        
        # Get location
        location = await db.locations.find_one({"slug": slug})
        if not location:
            raise HTTPException(status_code=404, detail="Standort nicht gefunden")
        
        # Update via service
        new_config = await pos_service.update_pos_config(
            location_slug=slug,
            config_data=config.model_dump(),
            admin_email=admin["email"]
        )
        
        # Audit log
        await audit_service.log_action(
            actor_email=admin["email"],
            action="pos_config_updated",
            result="success",
            target=str(location["_id"]),
            target_type="location",
            details={"slug": slug, "provider": config.provider, "test_mode": config.test_mode}
        )
        
        return {"message": "POS-Konfiguration aktualisiert", "config": {
            "provider": new_config.get('provider'),
            "status": new_config.get('status'),
            "test_mode": new_config.get('test_mode')
        }}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Update POS config error: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren der POS-Konfiguration")


@api_router.post("/admin/locations/{slug}/pos/test")
async def test_pos_connection(
    slug: str,
    request: Optional[POSTestRequest] = None,
    admin: dict = Depends(get_current_admin)
):
    """Test POS connection for a location"""
    try:
        # Check access
        if admin["role"] != "super_admin":
            if slug not in admin.get("branch_ids", []):
                raise HTTPException(status_code=403, detail="Zugriff auf diesen Standort verweigert")
        
        # Get location
        location = await db.locations.find_one({"slug": slug})
        if not location:
            raise HTTPException(status_code=404, detail="Standort nicht gefunden")
        
        # Test connection
        simulate_failure = request.simulate_failure if request else False
        result = await pos_service.test_connection(
            location_slug=slug,
            admin_email=admin["email"],
            simulate_failure=simulate_failure
        )
        
        # Audit log
        await audit_service.log_action(
            actor_email=admin["email"],
            action="pos_test_connection",
            result="success" if result.get("success") else "failure",
            target=str(location["_id"]),
            target_type="location",
            details={"slug": slug, "test_result": result, "simulate_failure": simulate_failure}
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"POS test error: {str(e)}")
        raise HTTPException(status_code=500, detail="POS-Verbindungstest fehlgeschlagen")


@api_router.get("/admin/locations/{slug}/pos/logs")
async def get_pos_logs(
    slug: str,
    limit: int = 50,
    admin: dict = Depends(get_current_admin)
):
    """Get POS integration logs for a location"""
    try:
        # Check access
        if admin["role"] != "super_admin":
            if slug not in admin.get("branch_ids", []):
                raise HTTPException(status_code=403, detail="Zugriff auf diesen Standort verweigert")
        
        # Get location
        location = await db.locations.find_one({"slug": slug})
        if not location:
            raise HTTPException(status_code=404, detail="Standort nicht gefunden")
        
        # Get logs
        logs = await pos_service.get_logs(location_slug=slug, limit=limit)
        
        return {"logs": logs, "location_slug": slug}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get POS logs error: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der POS-Logs")


@api_router.post("/admin/orders/{order_id}/pos/retry")
async def retry_order_pos_push(
    order_id: str,
    admin: dict = Depends(get_current_admin)
):
    """Retry pushing a failed order to POS"""
    try:
        # Get order to check location access - try both string and ObjectId
        order = await db.orders.find_one({"_id": order_id})
        if not order:
            try:
                order = await db.orders.find_one({"_id": ObjectId(order_id)})
            except Exception:
                pass
        if not order:
            raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")
        
        location_slug = order.get('location_slug') or order.get('location_id')
        
        # Check access
        if admin["role"] != "super_admin":
            if location_slug not in admin.get("branch_ids", []):
                raise HTTPException(status_code=403, detail="Zugriff auf diese Bestellung verweigert")
        
        # Retry push
        result = await pos_service.retry_order_push(
            order_id=order_id,
            admin_email=admin["email"]
        )
        
        # Audit log
        await audit_service.log_action(
            actor_email=admin["email"],
            action="pos_order_retry",
            result="success" if result.get("success") else "failure",
            target=order_id,
            target_type="order",
            details={"order_id": order_id, "result": result}
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"POS retry error: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim erneuten Senden an POS")


@api_router.get("/admin/pos/providers")
async def get_pos_providers(admin: dict = Depends(get_current_admin)):
    """Get list of available POS providers"""
    return {
        "providers": [
            {
                "id": "none",
                "name": "Kein POS",
                "description": "Bestellungen nur lokal speichern",
                "available": True
            },
            {
                "id": "expertorder",
                "name": "ExpertOrder",
                "description": "ExpertOrder POS-Integration",
                "available": True,
                "fields": [
                    {"key": "merchant_id", "label": "Merchant ID", "required": True},
                    {"key": "api_key", "label": "API Key", "required": False},
                    {"key": "username", "label": "Benutzername", "required": False},
                    {"key": "secret", "label": "Secret", "required": False},
                    {"key": "base_url", "label": "API URL", "required": False, "default": "https://api.expertorder.com/v1"}
                ]
            },
            {
                "id": "cashx",
                "name": "Cash-X",
                "description": "Cash-X Cloud Kassensystem",
                "available": True,
                "fields": [
                    {"key": "base_url", "label": "API URL", "required": True, "placeholder": "https://cashx.zozo-burger.de"},
                    {"key": "api_key", "label": "API Key", "required": True},
                    {"key": "terminal_id", "label": "Terminal ID", "required": False, "default": "KASSE-1"}
                ]
            }
        ]
    }


@api_router.get("/admin/pos/failed-orders")
async def get_failed_pos_orders(admin: dict = Depends(get_current_admin)):
    """
    Get failed POS orders that need manual retry
    - Super Admin: sees all failed orders
    - Branch Admin: sees only failed orders from their locations
    """
    try:
        # Determine location filter based on role
        location_slug = None
        if admin["role"] != "super_admin":
            # Branch admin - filter by their assigned branches
            branch_ids = admin.get("branch_ids", [])
            if not branch_ids:
                return {"failed_orders": [], "count": 0}
            # For branch admin, we need to filter by locations they manage
            # Since failed_pos_orders stores location_slug, we use that
            location_slug = branch_ids  # Will filter as {"location_slug": {"$in": branch_ids}}
        
        # Get failed orders via service
        if location_slug and isinstance(location_slug, list):
            # Branch admin case - get orders for all their locations
            all_orders = []
            for slug in location_slug:
                orders = await pos_service.get_failed_orders(location_slug=slug, status="pending")
                all_orders.extend(orders)
            failed_orders = all_orders
        else:
            # Super admin case - get all pending orders
            failed_orders = await pos_service.get_failed_orders(location_slug=None, status="pending")
        
        # Get count
        if admin["role"] != "super_admin":
            count = len(failed_orders)
        else:
            count = await pos_service.get_failed_orders_count()
        
        return {
            "failed_orders": failed_orders,
            "count": count
        }
    
    except Exception as e:
        logging.error(f"Get failed POS orders error: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der fehlgeschlagenen Bestellungen")


@api_router.post("/admin/pos/failed-orders/{failed_order_id}/retry")
async def retry_failed_pos_order(
    failed_order_id: str,
    admin: dict = Depends(get_current_admin)
):
    """
    Manually retry a failed POS order from the queue
    
    - Verifies admin has access to the location
    - Attempts to push order to POS
    - Updates order status and failed_pos_orders status on success
    """
    try:
        # Get the failed order first to check access
        try:
            failed = await db.failed_pos_orders.find_one({"_id": ObjectId(failed_order_id)})
        except Exception:
            raise HTTPException(status_code=400, detail="Ungültige Failed Order ID")
        
        if not failed:
            raise HTTPException(status_code=404, detail="Fehlgeschlagene Bestellung nicht gefunden")
        
        location_slug = failed.get("location_slug")
        
        # Check access - Branch admin can only retry orders from their locations
        if admin["role"] != "super_admin":
            branch_ids = admin.get("branch_ids", [])
            if location_slug not in branch_ids:
                raise HTTPException(status_code=403, detail="Zugriff auf diese Bestellung verweigert")
        
        # Retry via service
        result = await pos_service.retry_failed_order(
            failed_order_id=failed_order_id,
            admin_email=admin["email"]
        )
        
        # Audit log
        await audit_service.log_action(
            actor_email=admin["email"],
            action="pos_failed_order_retry",
            result="success" if result.get("success") else "failure",
            target=failed_order_id,
            target_type="failed_pos_order",
            details={
                "order_number": failed.get("order_number"),
                "location_slug": location_slug,
                "result": result.get("message")
            }
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Retry failed POS order error: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim erneuten Senden der Bestellung")


# ============================================================================
# LOCATION MANAGEMENT ENDPOINTS
# ============================================================================

@api_router.get("/admin/locations")
async def get_all_locations(admin: dict = Depends(get_current_admin)):
    """Get all locations (Super Admin) or only assigned locations (Branch Admin)"""
    try:
        query = {}
        
        # Branch admins can only see their assigned locations
        if admin["role"] != "super_admin" and admin["branch_ids"]:
            query["slug"] = {"$in": admin["branch_ids"]}
        
        locations = await db.locations.find(query).to_list(length=100)
        
        # Convert ObjectId to string
        for loc in locations:
            loc["_id"] = str(loc["_id"])
            loc["id"] = loc["_id"]
        
        return {"locations": locations}
    
    except Exception as e:
        logging.error(f"Get locations error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch locations")


@api_router.get("/admin/locations/{slug}")
async def get_location(slug: str, admin: dict = Depends(get_current_admin)):
    """Get a specific location by slug"""
    try:
        # Check if admin can access this location
        if admin["role"] != "super_admin":
            if slug not in admin["branch_ids"]:
                raise HTTPException(status_code=403, detail="Access denied to this location")
        
        location = await db.locations.find_one({"slug": slug})
        
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        location["_id"] = str(location["_id"])
        location["id"] = location["_id"]
        
        return location
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get location error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch location")


@api_router.post("/admin/locations", dependencies=[Depends(require_super_admin())])
async def create_location(location_data: LocationCreate, admin: dict = Depends(get_current_admin)):
    """Create a new location (Super Admin only)"""
    try:
        # Check if slug already exists
        existing = await db.locations.find_one({"slug": location_data.slug})
        if existing:
            raise HTTPException(status_code=400, detail="Location with this slug already exists")
        
        # Prepare location document
        location_dict = location_data.model_dump()
        location_dict["created_at"] = datetime.utcnow()
        location_dict["updated_at"] = datetime.utcnow()
        
        # Insert location
        result = await db.locations.insert_one(location_dict)
        
        # Log action
        await audit_service.log_action(
            actor_email=admin["email"],
            action="location_created",
            result="success",
            target=str(result.inserted_id),
            target_type="location",
            details={"name": location_data.name, "slug": location_data.slug}
        )
        
        # Fetch and return created location
        created_location = await db.locations.find_one({"_id": result.inserted_id})
        created_location["_id"] = str(created_location["_id"])
        created_location["id"] = created_location["_id"]
        
        return created_location
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Create location error: {str(e)}")
        await audit_service.log_action(
            actor_email=admin["email"],
            action="location_created",
            result="failure",
            details={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Failed to create location")


@api_router.put("/admin/locations/{slug}")
async def update_location(
    slug: str,
    location_data: LocationUpdate,
    admin: dict = Depends(get_current_admin)
):
    """Update a location (Super Admin: all fields, Branch Admin: limited fields)"""
    try:
        # Check access
        if admin["role"] != "super_admin":
            if slug not in admin["branch_ids"]:
                raise HTTPException(status_code=403, detail="Access denied to this location")
            
            # Branch admins can only update specific fields
            allowed_fields = {"opening_hours", "delivery_area", "phone", "email"}
            update_dict = location_data.model_dump(exclude_unset=True)
            
            # Check if trying to update forbidden fields
            forbidden_updates = set(update_dict.keys()) - allowed_fields
            if forbidden_updates:
                raise HTTPException(
                    status_code=403,
                    detail=f"Branch admins cannot update these fields: {', '.join(forbidden_updates)}"
                )
        
        # Get existing location
        existing = await db.locations.find_one({"slug": slug})
        if not existing:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Prepare update
        update_dict = location_data.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()
        
        # Update location
        await db.locations.update_one(
            {"slug": slug},
            {"$set": update_dict}
        )
        
        # Log action
        await audit_service.log_action(
            actor_email=admin["email"],
            action="location_updated",
            result="success",
            target=str(existing["_id"]),
            target_type="location",
            details={"slug": slug, "updated_fields": list(update_dict.keys())}
        )
        
        # Fetch and return updated location
        updated_location = await db.locations.find_one({"slug": slug})
        updated_location["_id"] = str(updated_location["_id"])
        updated_location["id"] = updated_location["_id"]
        
        return updated_location
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Update location error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update location")


@api_router.delete("/admin/locations/{slug}", dependencies=[Depends(require_super_admin())])
async def delete_location(slug: str, admin: dict = Depends(get_current_admin)):
    """Delete a location (Super Admin only)"""
    try:
        # Check if location exists
        location = await db.locations.find_one({"slug": slug})
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Delete location
        await db.locations.delete_one({"slug": slug})
        
        # Log action
        await audit_service.log_action(
            actor_email=admin["email"],
            action="location_deleted",
            result="success",
            target=str(location["_id"]),
            target_type="location",
            details={"name": location["name"], "slug": slug}
        )
        
        return {"message": f"Location {location['name']} deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Delete location error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete location")


# ============================================================================
# TWO-FACTOR AUTHENTICATION (2FA) ENDPOINTS
# ============================================================================

class TOTP2FAVerifyRequest(BaseModel):
    temp_token: str
    code: str

class TOTP2FASetupConfirmRequest(BaseModel):
    code: str


@api_router.post("/admin/auth/2fa/verify")
async def verify_2fa_login(
    request: TOTP2FAVerifyRequest,
    http_request: Request
):
    """Verify 2FA code to complete login"""
    try:
        client_ip = http_request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or \
                   http_request.headers.get("X-Real-IP", "") or \
                   (http_request.client.host if http_request.client else "unknown")
        
        # Decode temp token to get email
        try:
            payload = AdminAuth.decode_token(request.temp_token)
            email = payload.get("email")
            if not email or not payload.get("awaiting_2fa"):
                raise HTTPException(status_code=401, detail="Ungültiger Token")
        except Exception:
            raise HTTPException(status_code=401, detail="Token abgelaufen oder ungültig")
        
        # Verify 2FA code
        success, message = await totp_service.verify_2fa_login(email, request.code)
        
        if not success:
            await audit_service.log_action(
                actor_email=email,
                action="2fa_verification_failed",
                result="failure",
                category=AuditCategory.AUTH.value,
                ip_address=client_ip,
                details={"reason": message}
            )
            raise HTTPException(status_code=401, detail=message)
        
        # Get admin for full token
        admin = await db.admins.find_one({"email": email})
        if not admin:
            raise HTTPException(status_code=404, detail="Admin nicht gefunden")
        
        # Create full JWT token
        token = AdminAuth.create_token(
            email=admin["email"],
            role=admin["role"],
            branch_ids=admin.get("branch_ids", [])
        )
        
        # Update last login
        await db.admins.update_one(
            {"_id": admin["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Log successful login
        await audit_service.log_action(
            actor_email=email,
            action=AuditAction.LOGIN_SUCCESS.value,
            result="success",
            category=AuditCategory.AUTH.value,
            ip_address=client_ip,
            details={"role": admin["role"], "2fa_verified": True, "method": message}
        )
        
        # Prepare admin response
        admin_response = {
            "id": str(admin["_id"]),
            "email": admin["email"],
            "name": admin["name"],
            "role": admin["role"],
            "branch_ids": admin.get("branch_ids", []),
            "permissions": AdminAuth.get_permissions(admin["role"]),
            "totp_enabled": admin.get("totp_enabled", False),
            "must_change_password": admin.get("must_change_password", False)
        }
        
        return AdminLoginResponse(
            access_token=token,
            token_type="bearer",
            admin=admin_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"2FA verification error: {str(e)}")
        raise HTTPException(status_code=500, detail="2FA-Verifizierung fehlgeschlagen")


@api_router.post("/admin/auth/2fa/setup")
async def setup_2fa(admin: dict = Depends(get_current_admin)):
    """Initialize 2FA setup - generates QR code and backup codes"""
    try:
        setup_data = await totp_service.setup_2fa(admin["email"])
        
        await audit_service.log_action(
            actor_email=admin["email"],
            action="2fa_setup_started",
            result="success",
            category=AuditCategory.AUTH.value
        )
        
        return {
            "qr_code": setup_data["qr_code"],
            "manual_entry_key": setup_data["manual_entry_key"],
            "backup_codes": setup_data["backup_codes"],
            "message": "Scannen Sie den QR-Code mit Ihrer Authenticator-App"
        }
    
    except Exception as e:
        logging.error(f"2FA setup error: {str(e)}")
        raise HTTPException(status_code=500, detail="2FA-Einrichtung fehlgeschlagen")


@api_router.post("/admin/auth/2fa/confirm")
async def confirm_2fa_setup(
    request: TOTP2FASetupConfirmRequest,
    admin: dict = Depends(get_current_admin)
):
    """Confirm 2FA setup by verifying the first TOTP code"""
    try:
        success, message = await totp_service.confirm_2fa_setup(admin["email"], request.code)
        
        if not success:
            await audit_service.log_action(
                actor_email=admin["email"],
                action="2fa_setup_confirm_failed",
                result="failure",
                category=AuditCategory.AUTH.value,
                details={"reason": message}
            )
            raise HTTPException(status_code=400, detail=message)
        
        await audit_service.log_action(
            actor_email=admin["email"],
            action=AuditAction.TOTP_ENABLED.value,
            result="success",
            category=AuditCategory.AUTH.value
        )
        
        return {"success": True, "message": message}
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"2FA confirm error: {str(e)}")
        raise HTTPException(status_code=500, detail="2FA-Bestätigung fehlgeschlagen")


@api_router.post("/admin/auth/2fa/disable")
async def disable_2fa(
    target_email: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """
    Disable 2FA for self or another admin (Super Admin only for others)
    """
    try:
        email_to_disable = target_email or admin["email"]
        
        # Only Super Admin can disable 2FA for others
        if email_to_disable != admin["email"] and admin["role"] != "super_admin":
            raise HTTPException(status_code=403, detail="Nur Super Admin kann 2FA für andere deaktivieren")
        
        # Super Admin cannot disable their own 2FA
        if email_to_disable == admin["email"] and admin["role"] == "super_admin":
            raise HTTPException(status_code=400, detail="Super Admin kann eigene 2FA nicht deaktivieren")
        
        success, message = await totp_service.disable_2fa(email_to_disable, admin["email"])
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        await audit_service.log_action(
            actor_email=admin["email"],
            action=AuditAction.TOTP_DISABLED.value,
            result="success",
            category=AuditCategory.AUTH.value,
            target=email_to_disable,
            details={"disabled_by": admin["email"]}
        )
        
        return {"success": True, "message": message}
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"2FA disable error: {str(e)}")
        raise HTTPException(status_code=500, detail="2FA-Deaktivierung fehlgeschlagen")


@api_router.post("/admin/auth/2fa/regenerate-backup-codes")
async def regenerate_backup_codes(admin: dict = Depends(get_current_admin)):
    """Generate new backup codes (invalidates old ones)"""
    try:
        success, new_codes, message = await totp_service.regenerate_backup_codes(admin["email"])
        
        if not success:
            raise HTTPException(status_code=400, detail=message)
        
        await audit_service.log_action(
            actor_email=admin["email"],
            action="2fa_backup_codes_regenerated",
            result="success",
            category=AuditCategory.AUTH.value
        )
        
        return {
            "success": True,
            "backup_codes": new_codes,
            "message": "Neue Backup-Codes generiert. Speichern Sie diese sicher!"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Backup code regeneration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Backup-Code-Generierung fehlgeschlagen")


@api_router.get("/admin/auth/2fa/status")
async def get_2fa_status(admin: dict = Depends(get_current_admin)):
    """Get current 2FA status"""
    status = await totp_service.get_2fa_status(admin["email"])
    return status



# ============================================================================
# WEBAUTHN/PASSKEY ENDPOINTS
# ============================================================================

from webauthn_service import WebAuthnService

webauthn_service = WebAuthnService(db)


class PasskeyRegistrationRequest(BaseModel):
    device_name: Optional[str] = None


class PasskeyVerificationRequest(BaseModel):
    credential: dict
    device_name: Optional[str] = None


class PasskeyAuthRequest(BaseModel):
    credential: dict


class BackupCodeRequest(BaseModel):
    code: str


@api_router.post("/admin/auth/passkey/register-options")
async def passkey_register_options(admin: dict = Depends(get_current_admin)):
    """Start passkey registration - returns options for navigator.credentials.create()"""
    try:
        options = await webauthn_service.start_registration(admin["email"])
        
        await audit_service.log_action(
            actor_email=admin["email"],
            action="passkey_setup_started",
            result="success",
            category="auth"
        )
        
        return options
    except Exception as e:
        logger.error(f"Passkey register options error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/auth/passkey/register-verify")
async def passkey_register_verify(
    request: PasskeyVerificationRequest,
    admin: dict = Depends(get_current_admin)
):
    """Complete passkey registration - verify credential and return backup codes"""
    try:
        success, result = await webauthn_service.verify_registration(
            admin_email=admin["email"],
            credential=request.credential,
            device_name=request.device_name
        )
        
        if not success:
            await audit_service.log_action(
                actor_email=admin["email"],
                action="passkey_setup_failed",
                result="failure",
                category="auth",
                details={"error": result}
            )
            raise HTTPException(status_code=400, detail=result)
        
        # result is backup_codes list
        backup_codes = result
        
        await audit_service.log_action(
            actor_email=admin["email"],
            action="passkey_enabled",
            result="success",
            category="auth"
        )
        
        return {
            "success": True,
            "message": "Passkey erfolgreich registriert",
            "backup_codes": backup_codes
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Passkey register verify error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/auth/passkey/login-options")
async def passkey_login_options(email: str):
    """Get authentication options for passkey login (after password verification)"""
    try:
        options = await webauthn_service.start_authentication(email)
        return options
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Passkey login options error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/auth/passkey/login-verify")
async def passkey_login_verify(request: PasskeyAuthRequest, email: str):
    """Verify passkey authentication and return full JWT"""
    try:
        success, message = await webauthn_service.verify_authentication(
            admin_email=email,
            credential=request.credential
        )
        
        if not success:
            await audit_service.log_action(
                actor_email=email,
                action="passkey_login_failed",
                result="failure",
                category="auth",
                details={"reason": message}
            )
            raise HTTPException(status_code=401, detail=message)
        
        # Get admin for full token
        admin = await db.admins.find_one({"email": email})
        if not admin:
            raise HTTPException(status_code=404, detail="Admin nicht gefunden")
        
        # Create full JWT
        from admin_auth import AdminAuth
        token = AdminAuth.create_token(
            email=admin["email"],
            role=admin["role"],
            branch_ids=admin.get("branch_ids", [])
        )
        
        # Update last login
        await db.admins.update_one(
            {"_id": admin["_id"]},
            {"$set": {"last_login": datetime.now(timezone.utc)}}
        )
        
        await audit_service.log_action(
            actor_email=email,
            action="passkey_login_success",
            result="success",
            category="auth"
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "admin": {
                "id": str(admin["_id"]),
                "email": admin["email"],
                "name": admin["name"],
                "role": admin["role"],
                "branch_ids": admin.get("branch_ids", []),
                "passkey_enabled": True
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Passkey login verify error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/auth/passkey/backup-code-login")
async def passkey_backup_code_login(request: BackupCodeRequest, email: str):
    """Login with backup code (recovery)"""
    try:
        success, message = await webauthn_service.verify_backup_code(email, request.code)
        
        if not success:
            await audit_service.log_action(
                actor_email=email,
                action="backup_code_login_failed",
                result="failure",
                category="auth"
            )
            raise HTTPException(status_code=401, detail=message)
        
        # Get admin for full token
        admin = await db.admins.find_one({"email": email})
        if not admin:
            raise HTTPException(status_code=404, detail="Admin nicht gefunden")
        
        # Create full JWT
        from admin_auth import AdminAuth
        token = AdminAuth.create_token(
            email=admin["email"],
            role=admin["role"],
            branch_ids=admin.get("branch_ids", [])
        )
        
        await audit_service.log_action(
            actor_email=email,
            action="backup_code_login_success",
            result="success",
            category="auth",
            details={"warning": message}
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "admin": {
                "id": str(admin["_id"]),
                "email": admin["email"],
                "name": admin["name"],
                "role": admin["role"],
                "branch_ids": admin.get("branch_ids", [])
            },
            "message": message
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backup code login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/admin/security/passkey/status")
async def get_passkey_status(admin: dict = Depends(get_current_admin)):
    """Get passkey status"""
    status = await webauthn_service.get_passkey_status(admin["email"])
    return status


@api_router.post("/admin/security/passkey/regenerate-backup-codes")
async def regenerate_passkey_backup_codes(admin: dict = Depends(get_current_admin)):
    """Regenerate backup codes (invalidates old ones)"""
    try:
        codes = await webauthn_service.regenerate_backup_codes(admin["email"])
        
        await audit_service.log_action(
            actor_email=admin["email"],
            action="passkey_backup_codes_regenerated",
            result="success",
            category="auth"
        )
        
        return {
            "success": True,
            "backup_codes": codes,
            "message": "Neue Backup Codes generiert. Speichern Sie diese sicher!"
        }
    except Exception as e:
        logger.error(f"Regenerate backup codes error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SECURITY & AUDIT ENDPOINTS
# ============================================================================

@api_router.get("/admin/security/audit-logs")
async def get_audit_logs(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    actor_email: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    admin: dict = Depends(get_current_admin)
):
    """Get audit logs (Super Admin only)"""
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Nur Super Admin kann Audit-Logs einsehen")
    
    # Parse dates if provided
    parsed_start = None
    parsed_end = None
    if start_date:
        try:
            parsed_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            pass
    if end_date:
        try:
            parsed_end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            pass
    
    logs = await audit_service.get_logs(
        start_date=parsed_start,
        end_date=parsed_end,
        actor_email=actor_email,
        action=action,
        category=category,
        result=result,
        severity=severity,
        limit=limit,
        offset=offset
    )
    
    return logs


@api_router.get("/admin/security/summary")
async def get_security_summary(
    hours: int = Query(24, ge=1, le=168),
    admin: dict = Depends(get_current_admin)
):
    """Get security summary for the last N hours (Super Admin only)"""
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Nur Super Admin kann Sicherheits-Übersicht einsehen")
    
    summary = await audit_service.get_security_summary(hours=hours)
    return summary


@api_router.get("/admin/security/rate-limit-status")
async def get_rate_limit_status(
    http_request: Request,
    admin: dict = Depends(get_current_admin)
):
    """Get current rate limit status for client (for debugging)"""
    if admin["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Nur Super Admin")
    
    statuses = {}
    for action in ["admin_login", "order", "api_general"]:
        statuses[action] = await rate_limiter.get_client_status(http_request, action)
    
    return {"rate_limits": statuses}


@api_router.post("/admin/security/change-password")
async def change_admin_password(
    http_request: Request,
    admin: dict = Depends(get_current_admin)
):
    """Force password change endpoint"""
    try:
        body = await http_request.json()
        current_password = body.get("current_password")
        new_password = body.get("new_password")
        
        if not current_password or not new_password:
            raise HTTPException(status_code=400, detail="Aktuelles und neues Passwort erforderlich")
        
        # Get admin from DB
        admin_user = await db.admins.find_one({"email": admin["email"]})
        if not admin_user:
            raise HTTPException(status_code=404, detail="Admin nicht gefunden")
        
        # Verify current password
        if not AdminAuth.verify_password(current_password, admin_user["password_hash"]):
            await audit_service.log_action(
                actor_email=admin["email"],
                action=AuditAction.PASSWORD_CHANGED.value,
                result="failure",
                category=AuditCategory.AUTH.value,
                details={"reason": "Invalid current password"}
            )
            raise HTTPException(status_code=401, detail="Aktuelles Passwort ist falsch")
        
        # Validate new password
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Neues Passwort muss mindestens 8 Zeichen haben")
        
        if new_password == current_password:
            raise HTTPException(status_code=400, detail="Neues Passwort muss sich vom aktuellen unterscheiden")
        
        # Hash and save new password
        new_hash = AdminAuth.hash_password(new_password)
        await db.admins.update_one(
            {"email": admin["email"]},
            {
                "$set": {
                    "password_hash": new_hash,
                    "must_change_password": False,
                    "password_changed_at": datetime.utcnow()
                }
            }
        )
        
        # Log success
        await audit_service.log_action(
            actor_email=admin["email"],
            action=AuditAction.PASSWORD_CHANGED.value,
            result="success",
            category=AuditCategory.AUTH.value
        )
        
        return {"message": "Passwort erfolgreich geändert", "must_change_password": False}
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Change password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Fehler beim Ändern des Passworts")


# Include the routers in the main app
app.include_router(api_router)
app.include_router(product_router, prefix="/api")

# Mount static files for product images
# Note: Mount under /api/uploads so it works with the Kubernetes Ingress routing
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/api/uploads", StaticFiles(directory="uploads"), name="api_uploads")

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
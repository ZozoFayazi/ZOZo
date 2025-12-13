from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Location Models
class DeliveryZone(BaseModel):
    postal_codes: List[str] = []  # List of postal codes this location delivers to
    min_order_value: float = 0.0  # Minimum order value for delivery
    delivery_fee: float = 2.50  # Delivery fee
    free_delivery_threshold: float = 15.0  # Free delivery above this amount

class Location(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    slug: str
    address: str
    city: str
    postal_code: str
    lat: float
    lng: float
    phone: str
    email: Optional[str] = None
    opening_hours: str = "11:00 - 22:45"
    delivery_zone: Optional[DeliveryZone] = None
    active: bool = True

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Category Models
class Category(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    location_id: Optional[str] = None  # None means global category
    name: str
    slug: str
    order: int = 0
    active: bool = True

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Menu Item Models
class MenuItem(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    location_id: Optional[str] = None  # None means available at all locations
    category_id: str
    name: str
    description: Optional[str] = None
    price_medium: Optional[float] = None
    price_large: Optional[float] = None
    price_normal: Optional[float] = None
    image_url: Optional[str] = None
    tags: List[str] = []
    allergens: List[str] = []  # e.g. ["gluten", "milk", "eggs", "nuts"]
    nutritional_info: Optional[dict] = None  # {"calories": 500, "protein": 25, "carbs": 45, "fat": 20}
    is_vegetarian: bool = False
    is_vegan: bool = False
    is_spicy: bool = False
    active: bool = True
    is_featured: bool = False  # Show in homepage hero carousel
    badge: Optional[str] = None  # "new", "limited", "bestseller", "hot"
    featured_order: int = 0  # Order in featured carousel

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Deal/Promotion Models
class Deal(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    description: str
    discount_type: str  # "percentage", "fixed_amount", "free_item"
    discount_value: float  # percentage (10 for 10%) or fixed amount (5.00 for €5)
    min_order_value: Optional[float] = None
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    location_ids: List[str] = []  # Empty list means valid for all locations
    image_url: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

# Order Models
class OrderItem(BaseModel):
    menu_item_id: str
    name: str
    price: float
    size: Optional[str] = None  # "medium", "large", "normal"
    quantity: int = 1
    notes: Optional[str] = None

class CustomerInfo(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: str
    postal_code: str
    city: str
    notes: Optional[str] = None

class Order(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    location_id: str
    order_number: str
    items: List[OrderItem]
    subtotal: float
    delivery_fee: float = 0.0
    discount: float = 0.0
    total: float
    customer: CustomerInfo
    is_pickup: bool = False  # True = pickup, False = delivery
    status: str = "confirmed"  # confirmed, preparing, ready, on_the_way, completed, cancelled
    payment_method: str = "cash"  # cash, card, paypal
    estimated_time: Optional[int] = 30  # Estimated time in minutes
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status_history: List[dict] = []  # Track status changes with timestamp

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

# Admin Models
class AdminUser(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: str
    password_hash: str
    location_id: Optional[str] = None  # None means owner with access to all locations
    role: str = "manager"  # owner, manager
    active: bool = True

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Request/Response Models
class OrderCreate(BaseModel):
    location_id: str
    items: List[OrderItem]
    customer: CustomerInfo
    payment_method: str = "cash"

class OrderStatusUpdate(BaseModel):
    status: str

# Custom Burger Models
class CustomBurger(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    description: Optional[str] = None
    bun: str  # "brioche", "sesame", "whole_wheat"
    patty: str  # "beef", "chicken", "veggie", "vegan"
    patty_count: int = 1  # 1-3 patties
    cheese: Optional[str] = None  # "cheddar", "swiss", "blue", "vegan"
    toppings: List[str] = []  # ["lettuce", "tomato", "onions", "pickles", "bacon", "egg", "jalapenos"]
    sauces: List[str] = []  # ["ketchup", "mayo", "bbq", "ranch", "special"]
    price: float
    created_by: Optional[str] = None  # customer email/id
    is_public: bool = False
    votes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}

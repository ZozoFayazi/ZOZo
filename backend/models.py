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
    allergens: Optional[str] = None
    active: bool = True

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

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
    total: float
    customer: CustomerInfo
    status: str = "new"  # new, accepted, preparing, out_for_delivery, completed, cancelled
    payment_method: str = "cash"  # cash, card
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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

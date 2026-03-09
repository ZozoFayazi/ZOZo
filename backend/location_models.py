"""Location Management Request/Response Models"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class OpeningHoursInput(BaseModel):
    day: str
    is_open: bool = True
    open_time: str = "11:00"
    close_time: str = "22:45"

class DeliveryAreaInput(BaseModel):
    mode: str = "radius"  # "radius" or "postal_codes"
    radius_km: Optional[float] = 5.0
    postal_codes: List[str] = []
    delivery_fee: float = 2.50
    min_order_value: float = 15.0
    estimated_delivery_time: str = "30-45 Min"

class LocationSEOInput(BaseModel):
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    keywords: Optional[str] = None

class LocationCreate(BaseModel):
    name: str
    slug: str
    address: str
    city: str
    postal_code: str
    lat: float = 0.0
    lng: float = 0.0
    phone: Optional[str] = None
    email: Optional[str] = None
    google_review_url: Optional[str] = None
    opening_hours: List[OpeningHoursInput] = []
    delivery_area: Optional[DeliveryAreaInput] = None
    seo: Optional[LocationSEOInput] = None
    is_active: bool = True

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    google_review_url: Optional[str] = None
    opening_hours: Optional[List[OpeningHoursInput]] = None
    delivery_area: Optional[DeliveryAreaInput] = None
    seo: Optional[LocationSEOInput] = None
    is_active: Optional[bool] = None

class LocationResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    slug: str
    address: str
    city: str
    postal_code: str
    lat: float
    lng: float
    phone: Optional[str] = None
    email: Optional[str] = None
    google_review_url: Optional[str] = None
    opening_hours: List[dict] = []
    delivery_area: Optional[dict] = None
    seo: Optional[dict] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True

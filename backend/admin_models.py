"""Admin Data Models"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class AdminBase(BaseModel):
    email: EmailStr
    name: str
    role: str  # super_admin, rellingen_admin, henstedt_admin
    branch_ids: List[str] = []  # Empty for super_admin
    is_active: bool = True

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class AdminResponse(AdminBase):
    id: str = Field(alias="_id")
    created_at: datetime
    last_login: Optional[datetime] = None
    totp_enabled: bool = False
    
    class Config:
        populate_by_name = True

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: dict

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

# Audit Log Models
class AuditLogEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor_email: str
    action: str  # e.g., "login", "product_created", "order_status_changed"
    target: Optional[str] = None  # Target resource ID
    target_type: Optional[str] = None  # e.g., "product", "order", "location"
    result: str  # "success" or "failure"
    ip_address: Optional[str] = None
    details: Optional[dict] = None

class AuditLogFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    actor_email: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    limit: int = 50
    offset: int = 0

"""POS Integration Models"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class POSProvider(str, Enum):
    NONE = "none"
    EXPERTORDER = "expertorder"
    CASHX = "cashx"


class POSStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ERROR = "error"
    TESTING = "testing"


class POSConfigInput(BaseModel):
    """Input model for creating/updating POS configuration"""
    provider: POSProvider = POSProvider.NONE
    test_mode: bool = True  # Always start in test mode for safety
    
    # Credentials (will be encrypted before storage)
    api_key: Optional[str] = None
    merchant_id: Optional[str] = None
    username: Optional[str] = None
    secret: Optional[str] = None
    base_url: Optional[str] = None
    
    # Settings
    settings: Optional[Dict[str, Any]] = None  # Tax mapping, payment methods, etc.


class POSConfigResponse(BaseModel):
    """Response model for POS configuration (secrets masked)"""
    provider: str
    status: str
    test_mode: bool
    
    # Credentials are masked - only show if set
    has_api_key: bool = False
    has_merchant_id: bool = False
    has_username: bool = False
    has_secret: bool = False
    base_url: Optional[str] = None
    
    # Status info
    last_sync_at: Optional[datetime] = None
    last_error: Optional[str] = None
    last_error_at: Optional[datetime] = None
    
    # Settings
    settings: Optional[Dict[str, Any]] = None


class POSTestResult(BaseModel):
    """Result of a POS connection test"""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    tested_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    is_test_mode: bool = True


class POSOrderPushResult(BaseModel):
    """Result of pushing an order to POS"""
    success: bool
    pos_order_id: Optional[str] = None
    message: str
    error: Optional[str] = None
    pushed_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    is_test_mode: bool = True


class POSLogEntry(BaseModel):
    """POS integration log entry"""
    id: Optional[str] = Field(alias="_id", default=None)
    location_id: str
    location_slug: str
    provider: str
    action: str  # "test_connection", "push_order", "config_update", etc.
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    order_id: Optional[str] = None
    pos_order_id: Optional[str] = None
    is_test_mode: bool = True
    admin_email: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow())
    
    class Config:
        populate_by_name = True


class OrderPOSStatus(str, Enum):
    """POS status for orders"""
    NOT_APPLICABLE = "not_applicable"  # POS not enabled
    PENDING = "pending"  # Waiting to be pushed
    SENT = "sent"  # Successfully sent to POS
    ERROR = "error"  # Push failed
    RETRYING = "retrying"  # Retry in progress


class OrderRetryRequest(BaseModel):
    """Request to retry sending an order to POS"""
    order_id: str

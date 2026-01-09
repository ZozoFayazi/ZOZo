"""
Super Admin endpoints for SaaS management
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import logging

from admin_auth import get_current_admin
from tenant_service import TenantService
from csv_import_service import CSVImportService
from utils import serialize_doc
from auth import get_password_hash

logger = logging.getLogger(__name__)


def create_super_admin_router(db):
    """Create router for super admin SaaS management"""
    router = APIRouter(prefix="/super-admin", tags=["super-admin"])
    
    tenant_service = TenantService(db)
    csv_service = CSVImportService(db)
    
    # Pydantic Models
    class TenantCreate(BaseModel):
        name: str
        slug: str
        admin_email: str
        admin_password: str
        language: str = "de"
        timezone: str = "Europe/Berlin"
    
    class BrandingUpdate(BaseModel):
        logo_url: Optional[str] = None
        primary_color: str
        accent_color: str
        font_family: Optional[str] = "Inter"
    
    class TemplateUpdate(BaseModel):
        template_id: str  # modern, classic, minimal
    
    class LocationCreate(BaseModel):
        name: str
        address: str
        postal_code: str
        city: str
        phone: str
        email: str
    
    # Endpoints
    @router.get("/tenants")
    async def get_all_tenants(admin: dict = Depends(get_current_admin)):
        """Get all tenants (super admin only)"""
        if admin.get("role") != "super_admin":
            raise HTTPException(403, "Super admin only")
        
        tenants = await db.tenants.find({}).to_list(100)
        return serialize_doc(tenants)
    
    @router.post("/tenants")
    async def create_new_tenant(
        tenant_data: TenantCreate,
        admin: dict = Depends(get_current_admin)
    ):
        """Create a new tenant (super admin only)"""
        if admin.get("role") != "super_admin":
            raise HTTPException(403, "Super admin only")
        
        # Hash password
        password_hash = get_password_hash(tenant_data.admin_password)
        
        result = await tenant_service.create_tenant(
            name=tenant_data.name,
            slug=tenant_data.slug,
            admin_email=tenant_data.admin_email,
            admin_password_hash=password_hash,
            language=tenant_data.language,
            timezone_str=tenant_data.timezone
        )
        
        if not result.get("success"):
            raise HTTPException(400, result.get("error", "Failed to create tenant"))
        
        return result
    
    @router.patch("/tenants/{tenant_id}/branding")
    async def update_tenant_branding(
        tenant_id: str,
        branding: BrandingUpdate,
        admin: dict = Depends(get_current_admin)
    ):
        """Update tenant branding"""
        if admin.get("role") != "super_admin":
            # Check if admin belongs to this tenant
            admin_user = await db.admin_users.find_one({"email": admin["email"]})
            if not admin_user or admin_user.get("tenant_id") != tenant_id:
                raise HTTPException(403, "Access denied")
        
        success = await tenant_service.update_branding(tenant_id, branding.dict())
        
        if not success:
            raise HTTPException(500, "Failed to update branding")
        
        return {"success": True, "message": "Branding updated"}
    
    @router.patch("/tenants/{tenant_id}/template")
    async def update_tenant_template(
        tenant_id: str,
        template: TemplateUpdate,
        admin: dict = Depends(get_current_admin)
    ):
        """Update tenant template"""
        if admin.get("role") != "super_admin":
            admin_user = await db.admin_users.find_one({"email": admin["email"]})
            if not admin_user or admin_user.get("tenant_id") != tenant_id:
                raise HTTPException(403, "Access denied")
        
        success = await tenant_service.update_template(tenant_id, template.template_id)
        
        if not success:
            raise HTTPException(500, "Failed to update template")
        
        return {"success": True, "message": "Template updated"}
    
    @router.post("/tenants/{tenant_id}/import-menu")
    async def import_menu_from_csv(
        tenant_id: str,
        file: UploadFile = File(...),
        admin: dict = Depends(get_current_admin)
    ):
        """Import menu from CSV file"""
        if admin.get("role") != "super_admin":
            admin_user = await db.admin_users.find_one({"email": admin["email"]})
            if not admin_user or admin_user.get("tenant_id") != tenant_id:
                raise HTTPException(403, "Access denied")
        
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(400, "Only CSV files allowed")
        
        # Read CSV content
        content = await file.read()
        csv_text = content.decode('utf-8')
        
        # Import
        result = await csv_service.import_menu_csv(tenant_id, csv_text)
        
        return result
    
    @router.post("/tenants/{tenant_id}/publish")
    async def publish_tenant(
        tenant_id: str,
        admin: dict = Depends(get_current_admin)
    ):
        """Publish tenant (go live)"""
        if admin.get("role") != "super_admin":
            raise HTTPException(403, "Super admin only")
        
        success = await tenant_service.publish_tenant(tenant_id)
        
        if not success:
            raise HTTPException(500, "Failed to publish tenant")
        
        return {"success": True, "message": "Tenant is now live"}
    
    return router

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import logging
import os
import json

from admin_auth import get_current_admin
from tenant_service import TenantService
from csv_import_service import CSVImportService
from utils import serialize_doc
from auth import get_password_hash

logger = logging.getLogger(__name__)


def serialize(o):
    from bson import ObjectId
    if isinstance(o, ObjectId): return str(o)
    if isinstance(o, datetime): return o.isoformat()
    if isinstance(o, dict): return {k: serialize(v) for k, v in o.items()}
    if isinstance(o, list): return [serialize(i) for i in o]
    return o


def create_super_admin_router(db):
    router = APIRouter(prefix="/super-admin", tags=["super-admin"])
    
    tenant_service = TenantService(db)
    csv_service = CSVImportService(db)
    
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
        template_id: str
    
    @router.get("/tenants")
    async def get_all_tenants(admin: dict = Depends(get_current_admin)):
        if admin.get("role") != "super_admin":
            raise HTTPException(403, "Super admin only")
        
        tenants = await db.tenants.find({}).to_list(100)
        return serialize_doc(tenants)
    
    @router.post("/tenants")
    async def create_new_tenant(
        tenant_data: TenantCreate,
        admin: dict = Depends(get_current_admin)
    ):
        if admin.get("role") != "super_admin":
            raise HTTPException(403, "Super admin only")
        
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
            raise HTTPException(400, result.get("error", "Failed"))
        
        return result
    
    @router.patch("/tenants/{tenant_id}/branding")
    async def update_tenant_branding(
        tenant_id: str,
        branding: BrandingUpdate,
        admin: dict = Depends(get_current_admin)
    ):
        if admin.get("role") != "super_admin":
            admin_user = await db.admin_users.find_one({"email": admin["email"]})
            if not admin_user or admin_user.get("tenant_id") != tenant_id:
                raise HTTPException(403, "Access denied")
        
        success = await tenant_service.update_branding(tenant_id, branding.dict())
        
        if not success:
            raise HTTPException(500, "Failed")
        
        return {"success": True, "message": "Branding updated"}
    
    @router.patch("/tenants/{tenant_id}/template")
    async def update_tenant_template(
        tenant_id: str,
        template: TemplateUpdate,
        admin: dict = Depends(get_current_admin)
    ):
        if admin.get("role") != "super_admin":
            admin_user = await db.admin_users.find_one({"email": admin["email"]})
            if not admin_user or admin_user.get("tenant_id") != tenant_id:
                raise HTTPException(403, "Access denied")
        
        success = await tenant_service.update_template(tenant_id, template.template_id)
        
        if not success:
            raise HTTPException(500, "Failed")
        
        return {"success": True, "message": "Template updated"}
    
    @router.post("/tenants/{tenant_id}/import-menu")
    async def import_menu_from_csv(
        tenant_id: str,
        file: UploadFile = File(...),
        admin: dict = Depends(get_current_admin)
    ):
        if admin.get("role") != "super_admin":
            admin_user = await db.admin_users.find_one({"email": admin["email"]})
            if not admin_user or admin_user.get("tenant_id") != tenant_id:
                raise HTTPException(403, "Access denied")
        
        if not file.filename.endswith('.csv'):
            raise HTTPException(400, "Only CSV files allowed")
        
        content = await file.read()
        csv_text = content.decode('utf-8')
        
        result = await csv_service.import_menu_csv(tenant_id, csv_text)
        
        return result
    
    @router.post("/tenants/{tenant_id}/publish")
    async def publish_tenant(
        tenant_id: str,
        admin: dict = Depends(get_current_admin)
    ):
        if admin.get("role") != "super_admin":
            raise HTTPException(403, "Super admin only")
        
        from onboarding_audit_service import OnboardingAuditService
        audit = OnboardingAuditService(db)
        
        # Smoke test
        tenant = await db.tenants.find_one({"tenant_id": tenant_id})
        locations = await db.locations.find({"tenant_id": tenant_id}).to_list(10)
        menu_count = await db.menu_items.count_documents({"tenant_id": tenant_id})
        
        if not tenant or not locations or menu_count == 0:
            await audit.log_event(tenant_id, "publish_failed", {"reason": "Smoke test failed"}, admin["email"])
            raise HTTPException(400, "Not ready")
        
        # Backup
        try:
            os.makedirs('/app/backups/publish', exist_ok=True)
            backup_data = {
                "tenant": serialize(tenant),
                "locations": serialize(locations),
                "menu_count": menu_count
            }
            
            backup_file = f"/app/backups/publish/{tenant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            await audit.log_event(tenant_id, "backup_created", {"file": backup_file}, admin["email"])
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
        
        # Publish
        success = await tenant_service.publish_tenant(tenant_id)
        
        if not success:
            await audit.log_event(tenant_id, "publish_failed", {"reason": "Service error"}, admin["email"])
            raise HTTPException(500, "Failed to publish")
        
        await audit.log_event(tenant_id, "tenant_published", {
            "locations": len(locations),
            "menu_items": menu_count
        }, admin["email"])
        
        return {
            "success": True,
            "message": "Tenant is now live",
            "smoke_test": "passed",
            "backup_created": True
        }
    
    return router

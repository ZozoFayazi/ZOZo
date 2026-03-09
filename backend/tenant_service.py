"""
Tenant Management Service - Multi-Tenant SaaS Core
Handles tenant isolation and data scoping
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class TenantService:
    """Service for managing multi-tenant architecture"""
    
    def __init__(self, db):
        self.db = db
    
    async def create_tenant(
        self,
        name: str,
        slug: str,
        admin_email: str,
        admin_password_hash: str,
        language: str = "de",
        timezone_str: str = "Europe/Berlin"
    ) -> Dict:
        """
        Create a new tenant with default structure
        
        Returns:
            {"success": bool, "tenant_id": str, "tenant": dict}
        """
        try:
            # Check if slug already exists
            existing = await self.db.tenants.find_one({"slug": slug})
            if existing:
                return {"success": False, "error": "Slug bereits vergeben"}
            
            tenant_id = str(uuid.uuid4())
            
            tenant = {
                "tenant_id": tenant_id,
                "name": name,
                "slug": slug,
                "status": "draft",  # draft, active, suspended
                "language": language,
                "timezone": timezone_str,
                "branding": {
                    "logo_url": None,
                    "primary_color": "#DC2626",  # Default red
                    "accent_color": "#F59E0B",   # Default orange
                    "font_family": "Inter"
                },
                "template_id": "modern",  # modern, classic, minimal
                "domain": f"{slug}.zozo-platform.de",
                "urls": {
                    "shop": f"/{slug}",
                    "admin": f"/{slug}/admin"
                },
                "subscription": {
                    "plan": "starter",
                    "status": "active",
                    "started_at": datetime.now(timezone.utc)
                },
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Insert tenant
            await self.db.tenants.insert_one(tenant)
            
            # Create tenant admin user
            admin_user = {
                "tenant_id": tenant_id,
                "email": admin_email,
                "password_hash": admin_password_hash,
                "role": "tenant_admin",
                "name": "Admin",
                "active": True,
                "branch_ids": [],  # Access to all locations
                "created_at": datetime.now(timezone.utc)
            }
            await self.db.admin_users.insert_one(admin_user)
            
            logger.info(f"Tenant created: {tenant_id} ({slug})")
            
            return {
                "success": True,
                "tenant_id": tenant_id,
                "tenant": tenant
            }
        
        except Exception as e:
            logger.error(f"Create tenant error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_tenant(self, tenant_id: str = None, slug: str = None) -> Optional[Dict]:
        """Get tenant by ID or slug"""
        if tenant_id:
            return await self.db.tenants.find_one({"tenant_id": tenant_id})
        elif slug:
            return await self.db.tenants.find_one({"slug": slug})
        return None
    
    async def update_branding(
        self,
        tenant_id: str,
        branding: Dict
    ) -> bool:
        """Update tenant branding"""
        try:
            result = await self.db.tenants.update_one(
                {"tenant_id": tenant_id},
                {
                    "$set": {
                        "branding": branding,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Update branding error: {str(e)}")
            return False
    
    async def update_template(
        self,
        tenant_id: str,
        template_id: str
    ) -> bool:
        """Update tenant template"""
        try:
            result = await self.db.tenants.update_one(
                {"tenant_id": tenant_id},
                {
                    "$set": {
                        "template_id": template_id,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Update template error: {str(e)}")
            return False
    
    async def publish_tenant(self, tenant_id: str) -> bool:
        """Publish tenant (set status to active)"""
        try:
            result = await self.db.tenants.update_one(
                {"tenant_id": tenant_id},
                {
                    "$set": {
                        "status": "active",
                        "published_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return result.matched_count > 0
        except Exception as e:
            logger.error(f"Publish tenant error: {str(e)}")
            return False
    
    async def add_tenant_id_to_collections(self, tenant_id: str):
        """
        Add tenant_id to all existing data for a tenant
        Use this during migration or data import
        """
        collections_to_update = [
            "locations",
            "menu_items",
            "categories",
            "orders",
            "discount_codes",
            "modifier_groups",
            "deals",
            "daily_deals"
        ]
        
        for collection_name in collections_to_update:
            try:
                collection = self.db[collection_name]
                # Add tenant_id to all documents without one
                await collection.update_many(
                    {"tenant_id": {"$exists": False}},
                    {"$set": {"tenant_id": tenant_id}}
                )
                logger.info(f"Added tenant_id to {collection_name}")
            except Exception as e:
                logger.error(f"Error updating {collection_name}: {str(e)}")

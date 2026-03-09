"""
Audit Trail Service for Tenant Onboarding
"""
from datetime import datetime, timezone
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class OnboardingAuditService:
    """Track tenant onboarding events"""
    
    def __init__(self, db):
        self.db = db
    
    async def log_event(
        self,
        tenant_id: str,
        event_type: str,
        event_data: Dict = None,
        actor_email: str = None
    ):
        """
        Log an onboarding event
        
        Event types:
        - tenant_created
        - branding_updated
        - template_selected
        - menu_imported
        - location_added
        - tenant_published
        - smoke_test_passed
        - backup_created
        """
        try:
            event = {
                "tenant_id": tenant_id,
                "event_type": event_type,
                "event_data": event_data or {},
                "actor_email": actor_email,
                "timestamp": datetime.now(timezone.utc)
            }
            
            await self.db.tenant_onboarding_events.insert_one(event)
            logger.info(f"Onboarding event logged: {tenant_id} - {event_type}")
        
        except Exception as e:
            logger.error(f"Failed to log event: {str(e)}")
    
    async def get_tenant_timeline(self, tenant_id: str):
        """Get complete onboarding timeline for a tenant"""
        events = await self.db.tenant_onboarding_events.find(
            {"tenant_id": tenant_id}
        ).sort("timestamp", 1).to_list(100)
        
        return events

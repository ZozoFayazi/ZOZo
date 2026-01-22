"""
Newsletter & Email Marketing API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from admin_auth import get_current_admin
from utils import serialize_doc


class NewsletterSubscribe(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    source: str = "checkout"


class NewsletterUnsubscribe(BaseModel):
    email: Optional[EmailStr] = None
    token: Optional[str] = None


class CampaignCreate(BaseModel):
    title: str
    subject: str
    html_content: str
    segment: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    html_content: Optional[str] = None
    segment: Optional[str] = None
    status: Optional[str] = None


def create_newsletter_router(db, newsletter_service):
    """Create newsletter management router"""
    
    router = APIRouter(prefix="/api", tags=["Newsletter"])
    
    # ==================== PUBLIC ENDPOINTS ====================
    
    @router.post("/newsletter/subscribe")
    async def subscribe_newsletter(subscribe: NewsletterSubscribe):
        """Public: Subscribe to newsletter"""
        result = await newsletter_service.subscribe(
            email=subscribe.email,
            name=subscribe.name,
            source=subscribe.source
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('message'))
        
        return result
    
    @router.post("/newsletter/unsubscribe")
    async def unsubscribe_newsletter(unsubscribe: NewsletterUnsubscribe):
        """Public: Unsubscribe from newsletter (DSGVO one-click)"""
        result = await newsletter_service.unsubscribe(
            email=unsubscribe.email,
            token=unsubscribe.token
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=404, detail=result.get('message'))
        
        return result
    
    @router.get("/newsletter/track-open/{campaign_id}/{email}")
    async def track_email_open(campaign_id: str, email: str):
        """Track email open (via tracking pixel)"""
        await newsletter_service.track_open(campaign_id, email)
        
        # Return 1x1 transparent pixel
        from fastapi.responses import Response
        pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        return Response(content=pixel, media_type="image/gif")
    
    @router.get("/newsletter/track-click/{campaign_id}/{email}")
    async def track_email_click(campaign_id: str, email: str, url: str = Query(...)):
        """Track email click and redirect"""
        await newsletter_service.track_click(campaign_id, email, url)
        
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=url)
    
    # ==================== ADMIN ENDPOINTS ====================
    
    @router.get("/admin/newsletter/subscribers")
    async def get_subscribers(
        status: Optional[str] = None,
        segment: Optional[str] = None,
        admin: dict = Depends(get_current_admin)
    ):
        """Admin: Get all newsletter subscribers"""
        subscribers = await newsletter_service.get_subscribers(status=status, segment=segment)
        return serialize_doc(subscribers)
    
    @router.get("/admin/newsletter/stats")
    async def get_newsletter_stats(admin: dict = Depends(get_current_admin)):
        """Admin: Get newsletter statistics"""
        stats = await newsletter_service.get_stats()
        return stats
    
    @router.get("/admin/newsletter/segments")
    async def get_segments(admin: dict = Depends(get_current_admin)):
        """Admin: Get all segments with counts"""
        segments = await newsletter_service.get_segments()
        return {"segments": segments}
    
    @router.post("/admin/newsletter/campaigns")
    async def create_campaign(
        campaign: CampaignCreate,
        admin: dict = Depends(get_current_admin)
    ):
        """Admin: Create new email campaign"""
        result = await newsletter_service.create_campaign(
            title=campaign.title,
            subject=campaign.subject,
            html_content=campaign.html_content,
            segment=campaign.segment,
            scheduled_at=campaign.scheduled_at,
            created_by=admin.get('email', 'admin')
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('message'))
        
        return result
    
    @router.get("/admin/newsletter/campaigns")
    async def get_campaigns(
        status: Optional[str] = None,
        admin: dict = Depends(get_current_admin)
    ):
        """Admin: Get all campaigns"""
        campaigns = await newsletter_service.get_campaigns(status=status)
        return serialize_doc(campaigns)
    
    @router.get("/admin/newsletter/campaigns/{campaign_id}")
    async def get_campaign(campaign_id: str, admin: dict = Depends(get_current_admin)):
        """Admin: Get single campaign with stats"""
        from bson import ObjectId
        
        campaign = await db.newsletter_campaigns.find_one({"id": campaign_id})
        if not campaign:
            campaign = await db.newsletter_campaigns.find_one({"_id": ObjectId(campaign_id)})
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
        
        return serialize_doc(campaign)
    
    @router.post("/admin/newsletter/campaigns/{campaign_id}/send")
    async def send_campaign(campaign_id: str, admin: dict = Depends(get_current_admin)):
        """Admin: Send campaign to subscribers"""
        result = await newsletter_service.send_campaign(campaign_id)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('message'))
        
        return result
    
    @router.patch("/admin/newsletter/campaigns/{campaign_id}")
    async def update_campaign(
        campaign_id: str,
        update: CampaignUpdate,
        admin: dict = Depends(get_current_admin)
    ):
        """Admin: Update campaign"""
        from bson import ObjectId
        
        update_data = {k: v for k, v in update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now()
        
        campaign = await db.newsletter_campaigns.find_one({"id": campaign_id})
        if not campaign:
            campaign = await db.newsletter_campaigns.find_one({"_id": ObjectId(campaign_id)})
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
        
        result = await db.newsletter_campaigns.update_one(
            {"_id": campaign.get('_id')},
            {"$set": update_data}
        )
        
        return {"success": True, "message": "Kampagne aktualisiert"}
    
    @router.delete("/admin/newsletter/campaigns/{campaign_id}")
    async def delete_campaign(campaign_id: str, admin: dict = Depends(get_current_admin)):
        """Admin: Delete campaign"""
        from bson import ObjectId
        
        campaign = await db.newsletter_campaigns.find_one({"id": campaign_id})
        if not campaign:
            campaign = await db.newsletter_campaigns.find_one({"_id": ObjectId(campaign_id)})
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
        
        # Soft delete - set status to deleted
        await db.newsletter_campaigns.update_one(
            {"_id": campaign.get('_id')},
            {"$set": {"status": "deleted", "deleted_at": datetime.now()}}
        )
        
        return {"success": True, "message": "Kampagne gelöscht"}
    
    return router

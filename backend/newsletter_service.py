"""
Newsletter & Email Marketing Service
DSGVO-compliant email subscription management
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import uuid

logger = logging.getLogger(__name__)


class NewsletterService:
    """Service for managing newsletter subscriptions and campaigns"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def subscribe(self, email: str, name: Optional[str] = None, source: str = "checkout") -> Dict:
        """
        Subscribe a customer to newsletter (DSGVO-compliant)
        NOW WITH AUTOMATIC WELCOME EMAIL!
        
        Args:
            email: Customer email
            name: Customer name (optional)
            source: Where did they subscribe (checkout, footer, etc.)
        
        Returns:
            Subscription result
        """
        try:
            # Check if already subscribed
            existing = await self.db.newsletter_subscribers.find_one({"email": email})
            
            if existing:
                # Already subscribed
                if existing.get('status') == 'active':
                    return {
                        "success": True,
                        "message": "Bereits abonniert",
                        "subscriber_id": str(existing.get('_id'))
                    }
                elif existing.get('status') == 'unsubscribed':
                    # Re-subscribe
                    await self.db.newsletter_subscribers.update_one(
                        {"_id": existing.get('_id')},
                        {
                            "$set": {
                                "status": "active",
                                "resubscribed_at": datetime.now(timezone.utc),
                                "updated_at": datetime.now(timezone.utc)
                            },
                            "$inc": {"resubscribe_count": 1}
                        }
                    )
                    return {
                        "success": True,
                        "message": "Erfolgreich wieder abonniert",
                        "subscriber_id": str(existing.get('_id'))
                    }
            
            # Create new subscriber
            subscriber_doc = {
                "id": str(uuid.uuid4()),
                "email": email.lower().strip(),
                "name": name,
                "status": "active",  # active, unsubscribed, bounced
                "source": source,
                "subscribed_at": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "unsubscribe_token": str(uuid.uuid4()),
                "metadata": {
                    "total_orders": 0,
                    "total_spent": 0.0,
                    "favorite_category": None,
                    "last_order_at": None,
                    "segments": []
                },
                "campaigns_received": [],
                "campaigns_opened": [],
                "campaigns_clicked": [],
                "welcome_email_sent": False,
                "vip_email_sent": False
            }
            
            result = await self.db.newsletter_subscribers.insert_one(subscriber_doc)
            
            logger.info(f"New newsletter subscriber: {email} (source: {source})")
            
            # Trigger welcome email automatically
            try:
                from email_automation_service import EmailAutomationService
                automation = EmailAutomationService(self.db)
                await automation.trigger_welcome_email(email)
                logger.info(f"Welcome email triggered for {email}")
            except Exception as e:
                logger.error(f"Failed to trigger welcome email: {str(e)}")
            
            return {
                "success": True,
                "message": "Erfolgreich abonniert",
                "subscriber_id": str(result.inserted_id)
            }
            
        except Exception as e:
            logger.error(f"Newsletter subscribe error: {str(e)}")
            return {
                "success": False,
                "message": f"Fehler beim Abonnieren: {str(e)}"
            }
    
    async def unsubscribe(self, email: str = None, token: str = None) -> Dict:
        """
        Unsubscribe from newsletter (DSGVO one-click unsubscribe)
        
        Args:
            email: Customer email (optional)
            token: Unsubscribe token (optional)
        
        Returns:
            Unsubscribe result
        """
        try:
            query = {}
            if token:
                query["unsubscribe_token"] = token
            elif email:
                query["email"] = email.lower().strip()
            else:
                return {
                    "success": False,
                    "message": "Email oder Token erforderlich"
                }
            
            subscriber = await self.db.newsletter_subscribers.find_one(query)
            
            if not subscriber:
                return {
                    "success": False,
                    "message": "Abonnement nicht gefunden"
                }
            
            await self.db.newsletter_subscribers.update_one(
                {"_id": subscriber.get('_id')},
                {
                    "$set": {
                        "status": "unsubscribed",
                        "unsubscribed_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            logger.info(f"Newsletter unsubscribe: {subscriber.get('email')}")
            
            return {
                "success": True,
                "message": "Erfolgreich abgemeldet"
            }
            
        except Exception as e:
            logger.error(f"Newsletter unsubscribe error: {str(e)}")
            return {
                "success": False,
                "message": f"Fehler beim Abmelden: {str(e)}"
            }
    
    async def get_subscribers(
        self, 
        status: Optional[str] = None,
        segment: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Get newsletter subscribers with optional filters
        
        Args:
            status: Filter by status (active, unsubscribed, bounced)
            segment: Filter by segment (vip, pizza_lovers, etc.)
            limit: Maximum number of subscribers to return
        
        Returns:
            List of subscribers
        """
        query = {}
        
        if status:
            query["status"] = status
        
        if segment:
            query["metadata.segments"] = segment
        
        subscribers = await self.db.newsletter_subscribers.find(query).limit(limit).to_list(length=limit)
        
        return subscribers
    
    async def get_stats(self) -> Dict:
        """Get newsletter statistics"""
        try:
            total = await self.db.newsletter_subscribers.count_documents({})
            active = await self.db.newsletter_subscribers.count_documents({"status": "active"})
            unsubscribed = await self.db.newsletter_subscribers.count_documents({"status": "unsubscribed"})
            bounced = await self.db.newsletter_subscribers.count_documents({"status": "bounced"})
            
            # Get recent subscribers (last 7 days)
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent = await self.db.newsletter_subscribers.count_documents({
                "subscribed_at": {"$gte": week_ago}
            })
            
            return {
                "total_subscribers": total,
                "active_subscribers": active,
                "unsubscribed": unsubscribed,
                "bounced": bounced,
                "new_this_week": recent,
                "growth_rate": (recent / total * 100) if total > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Newsletter stats error: {str(e)}")
            return {
                "total_subscribers": 0,
                "active_subscribers": 0,
                "unsubscribed": 0,
                "bounced": 0,
                "new_this_week": 0,
                "growth_rate": 0
            }
    
    async def update_subscriber_metadata(self, email: str, order_data: Dict) -> None:
        """
        Update subscriber metadata based on order
        Called automatically after each order
        
        Args:
            email: Customer email
            order_data: Order information
        """
        try:
            subscriber = await self.db.newsletter_subscribers.find_one({"email": email.lower().strip()})
            
            if not subscriber:
                return  # Not subscribed, skip
            
            # Calculate new metadata
            total_orders = subscriber.get('metadata', {}).get('total_orders', 0) + 1
            total_spent = subscriber.get('metadata', {}).get('total_spent', 0.0) + order_data.get('total', 0)
            
            # Determine favorite category (simplified)
            categories = []
            for item in order_data.get('items', []):
                category = item.get('category', '')
                if category:
                    categories.append(category)
            
            favorite_category = max(set(categories), key=categories.count) if categories else None
            
            # Auto-segment based on behavior
            segments = []
            if total_orders >= 10:
                segments.append('vip')
            if total_spent >= 500:
                segments.append('high_value')
            if favorite_category:
                segments.append(f"{favorite_category.lower()}_lover")
            
            update_data = {
                "metadata.total_orders": total_orders,
                "metadata.total_spent": round(total_spent, 2),
                "metadata.last_order_at": datetime.now(timezone.utc),
                "metadata.segments": list(set(segments)),
                "updated_at": datetime.now(timezone.utc)
            }
            
            if favorite_category:
                update_data["metadata.favorite_category"] = favorite_category
            
            await self.db.newsletter_subscribers.update_one(
                {"_id": subscriber.get('_id')},
                {"$set": update_data}
            )
            
            logger.info(f"Updated newsletter metadata for {email}: {total_orders} orders, €{total_spent:.2f} spent")
            
        except Exception as e:
            logger.error(f"Update subscriber metadata error: {str(e)}")
    
    async def create_campaign(
        self,
        title: str,
        subject: str,
        html_content: str,
        segment: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        created_by: str = "admin"
    ) -> Dict:
        """
        Create email marketing campaign
        
        Args:
            title: Campaign name (internal)
            subject: Email subject line
            html_content: Email HTML content
            segment: Target segment (vip, pizza_lovers, etc.) - None = all
            scheduled_at: When to send (None = immediate)
            created_by: Admin email
        
        Returns:
            Campaign creation result
        """
        try:
            campaign_doc = {
                "id": str(uuid.uuid4()),
                "title": title,
                "subject": subject,
                "html_content": html_content,
                "segment": segment,
                "status": "draft" if scheduled_at else "ready",  # draft, ready, sending, sent, failed
                "scheduled_at": scheduled_at,
                "created_by": created_by,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "stats": {
                    "total_recipients": 0,
                    "sent": 0,
                    "delivered": 0,
                    "opened": 0,
                    "clicked": 0,
                    "bounced": 0,
                    "unsubscribed": 0
                },
                "sent_at": None,
                "completed_at": None
            }
            
            result = await self.db.newsletter_campaigns.insert_one(campaign_doc)
            
            return {
                "success": True,
                "campaign_id": str(result.inserted_id),
                "message": "Kampagne erstellt"
            }
            
        except Exception as e:
            logger.error(f"Create campaign error: {str(e)}")
            return {
                "success": False,
                "message": f"Fehler beim Erstellen: {str(e)}"
            }
    
    async def send_campaign(self, campaign_id: str) -> Dict:
        """
        Send campaign to subscribers
        NOW WITH REAL EMAIL SENDING VIA RESEND!
        
        Args:
            campaign_id: Campaign ID
        
        Returns:
            Send result
        """
        try:
            # Import EmailService
            from email_service import EmailService
            
            # Get campaign
            campaign = await self.db.newsletter_campaigns.find_one({"id": campaign_id})
            if not campaign:
                campaign = await self.db.newsletter_campaigns.find_one({"_id": ObjectId(campaign_id)})
            
            if not campaign:
                return {
                    "success": False,
                    "message": "Kampagne nicht gefunden"
                }
            
            # Get subscribers for segment
            segment = campaign.get('segment')
            subscribers = await self.get_subscribers(status="active", segment=segment)
            
            if not subscribers:
                return {
                    "success": False,
                    "message": "Keine Abonnenten gefunden"
                }
            
            # Update campaign status
            await self.db.newsletter_campaigns.update_one(
                {"_id": campaign.get('_id')},
                {
                    "$set": {
                        "status": "sending",
                        "stats.total_recipients": len(subscribers),
                        "sent_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            # Send emails via Resend
            sent_count = 0
            failed_count = 0
            
            for subscriber in subscribers:
                try:
                    # Send email
                    result = await EmailService.send_campaign_email(
                        to_email=subscriber.get('email'),
                        subject=campaign.get('subject'),
                        html_content=campaign.get('html_content'),
                        campaign_id=campaign_id,
                        unsubscribe_token=subscriber.get('unsubscribe_token', '')
                    )
                    
                    if result.get('success'):
                        sent_count += 1
                        
                        # Log to subscriber
                        await self.db.newsletter_subscribers.update_one(
                            {"_id": subscriber.get('_id')},
                            {
                                "$push": {
                                    "campaigns_received": {
                                        "campaign_id": campaign_id,
                                        "sent_at": datetime.now(timezone.utc),
                                        "email_id": result.get('email_id')
                                    }
                                }
                            }
                        )
                    else:
                        failed_count += 1
                        logger.error(f"Failed to send to {subscriber.get('email')}: {result.get('message')}")
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error sending to {subscriber.get('email')}: {str(e)}")
            
            # Update campaign stats
            await self.db.newsletter_campaigns.update_one(
                {"_id": campaign.get('_id')},
                {
                    "$set": {
                        "status": "sent",
                        "stats.sent": sent_count,
                        "stats.failed": failed_count,
                        "completed_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            logger.info(f"Campaign sent: {campaign.get('title')} - {sent_count} sent, {failed_count} failed")
            
            return {
                "success": True,
                "message": f"Kampagne an {sent_count} Abonnenten gesendet ({failed_count} fehlgeschlagen)",
                "recipients": sent_count,
                "failed": failed_count
            }
            
        except Exception as e:
            logger.error(f"Send campaign error: {str(e)}")
            
            # Update campaign status to failed
            try:
                await self.db.newsletter_campaigns.update_one(
                    {"id": campaign_id},
                    {"$set": {"status": "failed", "error": str(e)}}
                )
            except:
                pass
            
            return {
                "success": False,
                "message": f"Fehler beim Senden: {str(e)}"
            }
    
    async def get_campaigns(self, status: Optional[str] = None) -> List[Dict]:
        """Get all campaigns with optional status filter"""
        query = {}
        if status:
            query["status"] = status
        
        campaigns = await self.db.newsletter_campaigns.find(query).sort("created_at", -1).to_list(length=100)
        
        return campaigns
    
    async def track_open(self, campaign_id: str, subscriber_email: str) -> None:
        """Track when a subscriber opens a campaign email"""
        try:
            # Update campaign stats
            await self.db.newsletter_campaigns.update_one(
                {"id": campaign_id},
                {"$inc": {"stats.opened": 1}}
            )
            
            # Update subscriber
            await self.db.newsletter_subscribers.update_one(
                {"email": subscriber_email},
                {
                    "$push": {
                        "campaigns_opened": {
                            "campaign_id": campaign_id,
                            "opened_at": datetime.now(timezone.utc)
                        }
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Track open error: {str(e)}")
    
    async def track_click(self, campaign_id: str, subscriber_email: str, url: str) -> None:
        """Track when a subscriber clicks a link in campaign email"""
        try:
            # Update campaign stats
            await self.db.newsletter_campaigns.update_one(
                {"id": campaign_id},
                {"$inc": {"stats.clicked": 1}}
            )
            
            # Update subscriber
            await self.db.newsletter_subscribers.update_one(
                {"email": subscriber_email},
                {
                    "$push": {
                        "campaigns_clicked": {
                            "campaign_id": campaign_id,
                            "url": url,
                            "clicked_at": datetime.now(timezone.utc)
                        }
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Track click error: {str(e)}")
    
    async def get_segments(self) -> Dict:
        """Get all available segments with subscriber counts"""
        try:
            # Aggregate segments from all subscribers
            pipeline = [
                {"$match": {"status": "active"}},
                {"$unwind": "$metadata.segments"},
                {"$group": {
                    "_id": "$metadata.segments",
                    "count": {"$sum": 1}
                }}
            ]
            
            segment_counts = await self.db.newsletter_subscribers.aggregate(pipeline).to_list(length=100)
            
            segments = {
                "all": await self.db.newsletter_subscribers.count_documents({"status": "active"})
            }
            
            for seg in segment_counts:
                segments[seg.get('_id')] = seg.get('count', 0)
            
            return segments
            
        except Exception as e:
            logger.error(f"Get segments error: {str(e)}")
            return {"all": 0}

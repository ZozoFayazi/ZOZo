"""
Email Marketing Automation Service
Trigger-based automated campaigns
Created: 22 January 2026
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import Dict, List
import logging
from email_service import EmailService

logger = logging.getLogger(__name__)


class EmailAutomationService:
    """Automated email campaigns based on triggers"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def trigger_welcome_email(self, subscriber_email: str) -> Dict:
        """
        Trigger: When someone subscribes to newsletter
        Action: Send welcome email with 10% discount
        """
        try:
            # Get subscriber
            subscriber = await self.db.newsletter_subscribers.find_one({"email": subscriber_email})
            
            if not subscriber:
                return {"success": False, "message": "Subscriber not found"}
            
            # Check if welcome email already sent
            if subscriber.get('welcome_email_sent'):
                return {"success": False, "message": "Welcome email already sent"}
            
            # Send welcome email
            result = await EmailService.send_welcome_email(
                subscriber_email=subscriber_email,
                subscriber_name=subscriber.get('name', ''),
                unsubscribe_token=subscriber.get('unsubscribe_token', '')
            )
            
            if result.get('success'):
                # Mark as sent
                await self.db.newsletter_subscribers.update_one(
                    {"_id": subscriber.get('_id')},
                    {
                        "$set": {
                            "welcome_email_sent": True,
                            "welcome_email_sent_at": datetime.now(timezone.utc)
                        }
                    }
                )
                
                logger.info(f"Welcome email sent to {subscriber_email}")
            
            return result
            
        except Exception as e:
            logger.error(f"Welcome email trigger failed: {str(e)}")
            return {"success": False, "message": str(e)}
    
    async def trigger_order_followup(self, order_id: str) -> Dict:
        """
        Trigger: 24 hours after order completion
        Action: Send feedback request email
        """
        try:
            # Get order
            order = await self.db.orders.find_one({"order_id": order_id})
            
            if not order:
                return {"success": False, "message": "Order not found"}
            
            if order.get('status') != 'completed':
                return {"success": False, "message": "Order not completed yet"}
            
            # Check if followup already sent
            if order.get('followup_email_sent'):
                return {"success": False, "message": "Followup already sent"}
            
            customer_email = order.get('customer_email')
            if not customer_email:
                return {"success": False, "message": "No customer email"}
            
            # Get unsubscribe token
            subscriber = await self.db.newsletter_subscribers.find_one({"email": customer_email})
            unsubscribe_token = subscriber.get('unsubscribe_token', '') if subscriber else 'no-token'
            
            # Send followup email
            result = await EmailService.send_order_followup(
                customer_email=customer_email,
                customer_name=order.get('customer_name', ''),
                order_id=order_id,
                order_total=order.get('total', 0),
                unsubscribe_token=unsubscribe_token
            )
            
            if result.get('success'):
                # Mark as sent
                await self.db.orders.update_one(
                    {"_id": order.get('_id')},
                    {
                        "$set": {
                            "followup_email_sent": True,
                            "followup_email_sent_at": datetime.now(timezone.utc)
                        }
                    }
                )
                
                logger.info(f"Order followup sent for {order_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Order followup trigger failed: {str(e)}")
            return {"success": False, "message": str(e)}
    
    async def trigger_reactivation_emails(self, days_threshold: int = 30) -> Dict:
        """
        Trigger: Daily cron job
        Action: Find at-risk customers and send reactivation emails
        """
        try:
            # Import CustomerService to get at-risk customers
            from customer_service import CustomerService
            from datetime import datetime, timezone
            
            # Get all customers
            result = await CustomerService.get_all_customers(
                segment='At-Risk',
                limit=1000
            )
            
            at_risk_customers = result.get('customers', [])
            
            emails_sent = 0
            errors = 0
            
            for customer in at_risk_customers:
                # Check if reactivation email already sent in last 30 days
                last_email = customer.get('last_reactivation_email_at')
                
                if last_email:
                    if isinstance(last_email, str):
                        last_email = datetime.fromisoformat(last_email.replace('Z', '+00:00'))
                    
                    days_since_email = (datetime.now(timezone.utc) - last_email).days
                    if days_since_email < 30:
                        continue  # Skip, already sent recently
                
                # Get subscriber for unsubscribe token
                subscriber = await self.db.newsletter_subscribers.find_one({"email": customer.get('email')})
                if not subscriber or subscriber.get('status') != 'active':
                    continue  # Skip if not subscribed
                
                # Get favorite product
                favorite_product = "Classic Burger"
                if customer.get('favorite_products') and len(customer['favorite_products']) > 0:
                    favorite_product = customer['favorite_products'][0].get('name', 'Classic Burger')
                
                # Send reactivation email
                result = await EmailService.send_reactivation_email(
                    customer_email=customer.get('email'),
                    customer_name=customer.get('name', ''),
                    favorite_product=favorite_product,
                    days_inactive=customer.get('days_since_last_order', days_threshold),
                    unsubscribe_token=subscriber.get('unsubscribe_token', '')
                )
                
                if result.get('success'):
                    emails_sent += 1
                    
                    # Log to subscriber
                    await self.db.newsletter_subscribers.update_one(
                        {"_id": subscriber.get('_id')},
                        {
                            "$set": {
                                "last_reactivation_email_at": datetime.now(timezone.utc)
                            }
                        }
                    )
                else:
                    errors += 1
            
            logger.info(f"Reactivation campaign: {emails_sent} sent, {errors} errors")
            
            return {
                "success": True,
                "emails_sent": emails_sent,
                "errors": errors,
                "message": f"{emails_sent} Reaktivierungs-Emails versendet"
            }
            
        except Exception as e:
            logger.error(f"Reactivation campaign failed: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    async def trigger_vip_upgrade_emails(self) -> Dict:
        """
        Trigger: Daily cron job
        Action: Find newly promoted VIP customers and congratulate them
        """
        try:
            from customer_service import CustomerService
            
            # Get VIP customers
            result = await CustomerService.get_all_customers(
                segment='VIP',
                limit=1000
            )
            
            vip_customers = result.get('customers', [])
            
            emails_sent = 0
            errors = 0
            
            for customer in vip_customers:
                # Check if VIP email already sent
                subscriber = await self.db.newsletter_subscribers.find_one({"email": customer.get('email')})
                
                if not subscriber or subscriber.get('status') != 'active':
                    continue
                
                if subscriber.get('vip_email_sent'):
                    continue  # Already notified
                
                # Send VIP upgrade email
                result = await EmailService.send_vip_upgrade_email(
                    customer_email=customer.get('email'),
                    customer_name=customer.get('name', ''),
                    total_orders=customer.get('completed_orders', 0),
                    total_spent=customer.get('total_spent', 0),
                    unsubscribe_token=subscriber.get('unsubscribe_token', '')
                )
                
                if result.get('success'):
                    emails_sent += 1
                    
                    # Mark as sent
                    await self.db.newsletter_subscribers.update_one(
                        {"_id": subscriber.get('_id')},
                        {
                            "$set": {
                                "vip_email_sent": True,
                                "vip_email_sent_at": datetime.now(timezone.utc)
                            }
                        }
                    )
                else:
                    errors += 1
            
            logger.info(f"VIP upgrade campaign: {emails_sent} sent, {errors} errors")
            
            return {
                "success": True,
                "emails_sent": emails_sent,
                "errors": errors,
                "message": f"{emails_sent} VIP-Emails versendet"
            }
            
        except Exception as e:
            logger.error(f"VIP upgrade campaign failed: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

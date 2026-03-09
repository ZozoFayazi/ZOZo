"""
Personalized Discount Code Generator for Reactivation Campaigns
Created: 22 January 2026
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
import logging
import uuid
import random
import string

logger = logging.getLogger(__name__)


class PersonalizedDiscountService:
    """Generate personalized, one-time discount codes for customers"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    @staticmethod
    def generate_personal_code(customer_name: str, discount_percent: int = 20) -> str:
        """
        Generate unique personal discount code
        Format: COMEBACK-{INITIALS}-{RANDOM}
        Example: COMEBACK-MAXM-A7X9
        """
        # Get initials from name
        name_parts = customer_name.upper().split()
        initials = ''.join([part[0] for part in name_parts if part])[:4]
        
        # Random suffix
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        # Construct code
        code = f"COMEBACK-{initials}-{random_suffix}"
        
        return code
    
    async def create_personal_discount(
        self,
        customer_email: str,
        customer_name: str,
        discount_percent: int = 20,
        valid_days: int = 14,
        reason: str = "reactivation"
    ) -> Dict:
        """
        Create a personalized, one-time discount code for a specific customer
        
        Args:
            customer_email: Customer email (code is bound to this email)
            customer_name: Customer name (used for code generation)
            discount_percent: Discount percentage (default: 20%)
            valid_days: How many days the code is valid (default: 14)
            reason: Why was this code created (reactivation, vip, birthday, etc.)
        
        Returns:
            {success: bool, code: str, expires_at: datetime}
        """
        try:
            # Check if customer already has an active personal code
            existing = await self.db.discount_codes.find_one({
                "customer_email": customer_email.lower(),
                "is_personal": True,
                "used": False,
                "expires_at": {"$gt": datetime.now(timezone.utc)}
            })
            
            if existing:
                # Customer already has an active personal code
                return {
                    "success": True,
                    "code": existing.get('code'),
                    "message": "Bestehender Code wird wiederverwendet",
                    "expires_at": existing.get('expires_at'),
                    "reused": True
                }
            
            # Generate unique code
            code = self.generate_personal_code(customer_name, discount_percent)
            
            # Ensure code is unique
            while await self.db.discount_codes.find_one({"code": code}):
                code = self.generate_personal_code(customer_name, discount_percent)
            
            # Calculate expiry
            expires_at = datetime.now(timezone.utc) + timedelta(days=valid_days)
            
            # Create discount code document
            discount_doc = {
                "code": code,
                "discount_type": "percentage",
                "discount_value": discount_percent,
                "is_personal": True,
                "customer_email": customer_email.lower(),
                "max_uses": 1,
                "used_count": 0,
                "used": False,
                "min_order_value": 0,  # No minimum
                "valid_from": datetime.now(timezone.utc),
                "expires_at": expires_at,
                "created_by": "system_automation",
                "created_at": datetime.now(timezone.utc),
                "reason": reason,
                "metadata": {
                    "generated_for": customer_name,
                    "customer_segment": reason
                }
            }
            
            await self.db.discount_codes.insert_one(discount_doc)
            
            logger.info(f"Personal discount code created: {code} for {customer_email} ({discount_percent}% off)")
            
            return {
                "success": True,
                "code": code,
                "message": "Persönlicher Rabattcode erstellt",
                "discount_percent": discount_percent,
                "expires_at": expires_at,
                "valid_days": valid_days,
                "reused": False
            }
            
        except Exception as e:
            logger.error(f"Failed to create personal discount: {str(e)}")
            return {
                "success": False,
                "message": f"Fehler: {str(e)}"
            }
    
    async def validate_personal_code(
        self,
        code: str,
        customer_email: str
    ) -> Dict:
        """
        Validate if personal code can be used by this customer
        
        Args:
            code: Discount code
            customer_email: Customer email trying to use the code
        
        Returns:
            {valid: bool, discount_percent: int, message: str}
        """
        try:
            discount = await self.db.discount_codes.find_one({"code": code})
            
            if not discount:
                return {
                    "valid": False,
                    "message": "Code nicht gefunden"
                }
            
            # Check if personal code
            if discount.get('is_personal'):
                # Verify customer email matches
                if discount.get('customer_email') != customer_email.lower():
                    return {
                        "valid": False,
                        "message": "Dieser Code ist für einen anderen Kunden bestimmt"
                    }
            
            # Check if already used
            if discount.get('used'):
                return {
                    "valid": False,
                    "message": "Code wurde bereits verwendet"
                }
            
            # Check expiry
            if discount.get('expires_at') and discount.get('expires_at') < datetime.now(timezone.utc):
                return {
                    "valid": False,
                    "message": "Code ist abgelaufen"
                }
            
            # Check max uses
            if discount.get('used_count', 0) >= discount.get('max_uses', 1):
                return {
                    "valid": False,
                    "message": "Code wurde bereits verwendet"
                }
            
            return {
                "valid": True,
                "discount_percent": discount.get('discount_value'),
                "discount_type": discount.get('discount_type'),
                "message": "Code ist gültig"
            }
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return {
                "valid": False,
                "message": "Validierungsfehler"
            }
    
    async def mark_code_as_used(
        self,
        code: str,
        order_id: str
    ) -> None:
        """
        Mark discount code as used
        
        Args:
            code: Discount code
            order_id: Order ID where it was used
        """
        try:
            await self.db.discount_codes.update_one(
                {"code": code},
                {
                    "$set": {
                        "used": True,
                        "used_at": datetime.now(timezone.utc)
                    },
                    "$inc": {"used_count": 1},
                    "$push": {
                        "usage_history": {
                            "order_id": order_id,
                            "used_at": datetime.now(timezone.utc)
                        }
                    }
                }
            )
            
            logger.info(f"Discount code {code} marked as used for order {order_id}")
            
        except Exception as e:
            logger.error(f"Failed to mark code as used: {str(e)}")

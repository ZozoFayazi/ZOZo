"""Enhanced Audit Logging Service for Security & Compliance"""
from datetime import datetime, timezone
from typing import Optional, Dict, List
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)


class AuditCategory(str, Enum):
    """Categories for audit log entries"""
    AUTH = "auth"
    ADMIN = "admin"
    PRODUCT = "product"
    LOCATION = "location"
    ORDER = "order"
    POS = "pos"
    SECURITY = "security"
    SYSTEM = "system"


class AuditAction(str, Enum):
    """Predefined audit actions for consistency"""
    # Auth
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    TOTP_ENABLED = "totp_enabled"
    TOTP_DISABLED = "totp_disabled"
    
    # Admin
    ADMIN_CREATED = "admin_created"
    ADMIN_UPDATED = "admin_updated"
    ADMIN_DELETED = "admin_deleted"
    PERMISSIONS_CHANGED = "permissions_changed"
    
    # Product
    PRODUCT_CREATED = "product_created"
    PRODUCT_UPDATED = "product_updated"
    PRODUCT_DELETED = "product_deleted"
    PRODUCT_ACTIVATED = "product_activated"
    PRODUCT_DEACTIVATED = "product_deactivated"
    PRODUCT_STOCK_CHANGED = "product_stock_changed"
    CATEGORY_CREATED = "category_created"
    CATEGORY_UPDATED = "category_updated"
    CATEGORY_DELETED = "category_deleted"
    
    # Location
    LOCATION_CREATED = "location_created"
    LOCATION_UPDATED = "location_updated"
    LOCATION_DELETED = "location_deleted"
    LOCATION_ACTIVATED = "location_activated"
    LOCATION_DEACTIVATED = "location_deactivated"
    
    # Order
    ORDER_STATUS_CHANGED = "order_status_changed"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_REFUNDED = "order_refunded"
    
    # POS
    POS_CONFIG_UPDATED = "pos_config_updated"
    POS_CONNECTION_TESTED = "pos_connection_tested"
    POS_ORDER_PUSHED = "pos_order_pushed"
    POS_ORDER_RETRY = "pos_order_retry"
    
    # Security
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    IP_BLOCKED = "ip_blocked"
    ACCESS_DENIED = "access_denied"


class AuditService:
    """Enhanced audit logging with categories, search, and retention"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.audit_logs
    
    async def log_action(
        self,
        actor_email: str,
        action: str,
        result: str = "success",
        target: Optional[str] = None,
        target_type: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict] = None,
        category: Optional[str] = None
    ):
        """
        Log an admin/system action
        
        Args:
            actor_email: Email of the user performing the action
            action: Action being performed (use AuditAction enum values)
            result: Result of the action (success/failure)
            target: ID or identifier of the affected resource
            target_type: Type of the affected resource (product, location, etc.)
            ip_address: Client IP address
            details: Additional context details
            category: Category of the action (use AuditCategory enum values)
        """
        # Auto-detect category if not provided
        if not category:
            category = self._detect_category(action)
        
        entry = {
            "timestamp": datetime.now(timezone.utc),
            "actor_email": actor_email,
            "action": action,
            "result": result,
            "category": category,
            "target": target,
            "target_type": target_type,
            "ip_address": ip_address,
            "details": details or {},
            "severity": self._get_severity(action, result)
        }
        
        try:
            await self.collection.insert_one(entry)
            
            # Log high severity events to application log as well
            if entry["severity"] in ["high", "critical"]:
                logger.warning(f"AUDIT [{entry['severity'].upper()}]: {action} by {actor_email} - {result}")
        except Exception as e:
            logger.error(f"Failed to log audit entry: {str(e)}")
    
    def _detect_category(self, action: str) -> str:
        """Auto-detect category based on action name"""
        action_lower = action.lower()
        
        if any(x in action_lower for x in ["login", "logout", "password", "totp", "auth"]):
            return AuditCategory.AUTH.value
        elif any(x in action_lower for x in ["product", "category", "menu"]):
            return AuditCategory.PRODUCT.value
        elif any(x in action_lower for x in ["location", "branch"]):
            return AuditCategory.LOCATION.value
        elif any(x in action_lower for x in ["order"]):
            return AuditCategory.ORDER.value
        elif any(x in action_lower for x in ["pos"]):
            return AuditCategory.POS.value
        elif any(x in action_lower for x in ["rate", "block", "suspicious", "security"]):
            return AuditCategory.SECURITY.value
        elif any(x in action_lower for x in ["admin", "permission", "user"]):
            return AuditCategory.ADMIN.value
        else:
            return AuditCategory.SYSTEM.value
    
    def _get_severity(self, action: str, result: str) -> str:
        """Determine severity level of an action"""
        action_lower = action.lower()
        
        # Critical: Security breaches, admin deletions
        critical_actions = ["ip_blocked", "suspicious_activity", "admin_deleted"]
        if any(x in action_lower for x in critical_actions):
            return "critical"
        
        # High: Failed logins, permission changes, data deletions
        high_actions = ["login_failed", "permissions_changed", "deleted", "rate_limit"]
        if result == "failure" or any(x in action_lower for x in high_actions):
            return "high"
        
        # Medium: Config changes, status changes
        medium_actions = ["updated", "changed", "config", "activated", "deactivated"]
        if any(x in action_lower for x in medium_actions):
            return "medium"
        
        # Low: Reads, successful operations
        return "low"
    
    async def get_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        actor_email: Optional[str] = None,
        action: Optional[str] = None,
        category: Optional[str] = None,
        result: Optional[str] = None,
        severity: Optional[str] = None,
        target_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict:
        """
        Query audit logs with filters
        
        Returns dict with 'logs' list and 'total' count
        """
        query = {}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        if actor_email:
            query["actor_email"] = actor_email
        
        if action:
            query["action"] = {"$regex": action, "$options": "i"}
        
        if category:
            query["category"] = category
        
        if result:
            query["result"] = result
        
        if severity:
            query["severity"] = severity
        
        if target_type:
            query["target_type"] = target_type
        
        cursor = self.collection.find(query).sort("timestamp", -1).skip(offset).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for log in logs:
            log["_id"] = str(log["_id"])
            # Format timestamp for JSON
            if log.get("timestamp"):
                log["timestamp"] = log["timestamp"].isoformat()
        
        # Get total count
        total = await self.collection.count_documents(query)
        
        return {"logs": logs, "total": total}
    
    async def get_security_summary(self, hours: int = 24) -> Dict:
        """Get summary of security-related events in the last N hours"""
        from datetime import timedelta
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Count by category
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff}}},
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "failures": {"$sum": {"$cond": [{"$eq": ["$result", "failure"]}, 1, 0]}}
            }}
        ]
        
        category_stats = await self.collection.aggregate(pipeline).to_list(length=20)
        
        # Count failed logins
        failed_logins = await self.collection.count_documents({
            "timestamp": {"$gte": cutoff},
            "action": {"$in": ["login_failed", "admin_login_failed"]},
        })
        
        # Count rate limit events
        rate_limits = await self.collection.count_documents({
            "timestamp": {"$gte": cutoff},
            "action": "rate_limit_exceeded"
        })
        
        # Recent high severity events
        high_severity = await self.collection.find({
            "timestamp": {"$gte": cutoff},
            "severity": {"$in": ["high", "critical"]}
        }).sort("timestamp", -1).limit(10).to_list(length=10)
        
        for event in high_severity:
            event["_id"] = str(event["_id"])
            if event.get("timestamp"):
                event["timestamp"] = event["timestamp"].isoformat()
        
        return {
            "period_hours": hours,
            "category_stats": {item["_id"]: item for item in category_stats},
            "failed_logins": failed_logins,
            "rate_limit_events": rate_limits,
            "high_severity_events": high_severity
        }
    
    async def get_admin_activity(self, email: str, days: int = 30) -> List[Dict]:
        """Get activity summary for a specific admin"""
        from datetime import timedelta
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        pipeline = [
            {"$match": {"actor_email": email, "timestamp": {"$gte": cutoff}}},
            {"$group": {
                "_id": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "action": "$action"
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.date": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=100)
        return results

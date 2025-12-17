"""Audit Logging Service"""
from datetime import datetime
from typing import Optional, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase

class AuditService:
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
        details: Optional[Dict] = None
    ):
        """Log an admin action"""
        entry = {
            "timestamp": datetime.utcnow(),
            "actor_email": actor_email,
            "action": action,
            "result": result,
            "target": target,
            "target_type": target_type,
            "ip_address": ip_address,
            "details": details or {}
        }
        await self.collection.insert_one(entry)
    
    async def get_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        actor_email: Optional[str] = None,
        action: Optional[str] = None,
        result: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ):
        """Query audit logs with filters"""
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
            query["action"] = action
        
        if result:
            query["result"] = result
        
        cursor = self.collection.find(query).sort("timestamp", -1).skip(offset).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for log in logs:
            log["_id"] = str(log["_id"])
        
        # Get total count
        total = await self.collection.count_documents(query)
        
        return {"logs": logs, "total": total}

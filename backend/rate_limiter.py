"""Rate Limiting Service for Security Hardening"""
import time
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timezone
from collections import defaultdict
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    In-memory rate limiter with MongoDB persistence for login attempts.
    
    Rate limit configurations:
    - Login: 5 attempts per 15 minutes per IP
    - Admin Login: 3 attempts per 15 minutes per IP
    - Orders: 10 orders per hour per IP
    - API General: 100 requests per minute per IP
    """
    
    # Configuration
    LIMITS = {
        "login": {"max_attempts": 5, "window_seconds": 900, "lockout_seconds": 900},  # 15 min
        "admin_login": {"max_attempts": 3, "window_seconds": 900, "lockout_seconds": 1800},  # 30 min lockout
        "order": {"max_attempts": 10, "window_seconds": 3600, "lockout_seconds": 3600},  # 1 hour
        "api_general": {"max_attempts": 100, "window_seconds": 60, "lockout_seconds": 60},  # 1 min
        "password_reset": {"max_attempts": 3, "window_seconds": 3600, "lockout_seconds": 3600},  # 1 hour
        "pos_test": {"max_attempts": 10, "window_seconds": 300, "lockout_seconds": 300},  # 5 min
    }
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self.db = db
        # In-memory cache: {action_type: {identifier: [(timestamp, count)]}}
        self._cache: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        # Lockout tracking: {action_type: {identifier: lockout_until_timestamp}}
        self._lockouts: Dict[str, Dict[str, float]] = defaultdict(dict)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, handling proxies"""
        # Check X-Forwarded-For header (from reverse proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to client host
        return request.client.host if request.client else "unknown"
    
    def _clean_old_entries(self, entries: list, window_seconds: int) -> list:
        """Remove entries older than the time window"""
        cutoff = time.time() - window_seconds
        return [entry for entry in entries if entry[0] > cutoff]
    
    def _is_locked_out(self, action: str, identifier: str) -> Tuple[bool, int]:
        """Check if identifier is locked out, return (is_locked, seconds_remaining)"""
        lockout_until = self._lockouts.get(action, {}).get(identifier, 0)
        
        if lockout_until > time.time():
            remaining = int(lockout_until - time.time())
            return True, remaining
        
        return False, 0
    
    async def check_rate_limit(
        self, 
        request: Request, 
        action: str,
        identifier: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Check if request is within rate limits.
        
        Args:
            request: FastAPI request object
            action: Rate limit action type (login, admin_login, order, etc.)
            identifier: Optional custom identifier (default: client IP)
        
        Returns:
            Tuple of (is_allowed, message)
        """
        if action not in self.LIMITS:
            return True, "OK"
        
        config = self.LIMITS[action]
        client_id = identifier or self._get_client_ip(request)
        
        # Check lockout first
        is_locked, remaining = self._is_locked_out(action, client_id)
        if is_locked:
            logger.warning(f"Rate limit lockout: {action} for {client_id}, {remaining}s remaining")
            return False, f"Zu viele Versuche. Bitte warten Sie {remaining} Sekunden."
        
        # Get and clean entries
        entries = self._cache[action][client_id]
        entries = self._clean_old_entries(entries, config["window_seconds"])
        self._cache[action][client_id] = entries
        
        # Count attempts in window
        attempt_count = sum(count for _, count in entries)
        
        if attempt_count >= config["max_attempts"]:
            # Apply lockout
            lockout_until = time.time() + config["lockout_seconds"]
            self._lockouts[action][client_id] = lockout_until
            
            logger.warning(f"Rate limit exceeded: {action} for {client_id}, locked until {lockout_until}")
            
            # Log to database if available
            if self.db:
                await self._log_rate_limit_event(client_id, action, "lockout")
            
            return False, f"Rate-Limit überschritten. Bitte warten Sie {config['lockout_seconds'] // 60} Minuten."
        
        return True, "OK"
    
    async def record_attempt(
        self, 
        request: Request, 
        action: str,
        success: bool = True,
        identifier: Optional[str] = None
    ):
        """
        Record an attempt for rate limiting.
        Failed attempts count more towards the limit.
        
        Args:
            request: FastAPI request object
            action: Rate limit action type
            success: Whether the attempt was successful
            identifier: Optional custom identifier
        """
        if action not in self.LIMITS:
            return
        
        client_id = identifier or self._get_client_ip(request)
        
        # Failed attempts count as 1, successful attempts might reset (depending on action)
        weight = 1 if not success else 0  # Only count failures for login-type actions
        
        if action in ["login", "admin_login", "password_reset"]:
            # For login actions, only count failures
            if not success:
                self._cache[action][client_id].append((time.time(), 1))
            else:
                # Successful login resets the counter
                self._cache[action][client_id] = []
                # Clear any lockout
                if client_id in self._lockouts.get(action, {}):
                    del self._lockouts[action][client_id]
        else:
            # For other actions, count all attempts
            self._cache[action][client_id].append((time.time(), 1))
        
        # Log to database if available
        if self.db and not success:
            await self._log_rate_limit_event(client_id, action, "failed_attempt")
    
    async def _log_rate_limit_event(self, client_id: str, action: str, event_type: str):
        """Log rate limit events to database for analysis"""
        try:
            await self.db.security_events.insert_one({
                "timestamp": datetime.now(timezone.utc),
                "type": "rate_limit",
                "event": event_type,
                "action": action,
                "client_id": client_id,
                "details": {
                    "limit_config": self.LIMITS.get(action, {})
                }
            })
        except Exception as e:
            logger.error(f"Failed to log rate limit event: {str(e)}")
    
    async def get_client_status(self, request: Request, action: str) -> Dict:
        """Get rate limit status for a client (for debugging/admin)"""
        client_id = self._get_client_ip(request)
        config = self.LIMITS.get(action, {})
        
        entries = self._cache.get(action, {}).get(client_id, [])
        entries = self._clean_old_entries(entries, config.get("window_seconds", 60))
        
        is_locked, remaining = self._is_locked_out(action, client_id)
        
        return {
            "client_id": client_id,
            "action": action,
            "attempts_in_window": sum(count for _, count in entries),
            "max_attempts": config.get("max_attempts", 0),
            "window_seconds": config.get("window_seconds", 0),
            "is_locked": is_locked,
            "lockout_remaining_seconds": remaining
        }


# Dependency functions for FastAPI
async def check_login_rate_limit(request: Request, rate_limiter: RateLimiter):
    """Check rate limit for login attempts"""
    allowed, message = await rate_limiter.check_rate_limit(request, "login")
    if not allowed:
        raise HTTPException(status_code=429, detail=message)


async def check_admin_login_rate_limit(request: Request, rate_limiter: RateLimiter):
    """Check rate limit for admin login attempts"""
    allowed, message = await rate_limiter.check_rate_limit(request, "admin_login")
    if not allowed:
        raise HTTPException(status_code=429, detail=message)


async def check_order_rate_limit(request: Request, rate_limiter: RateLimiter):
    """Check rate limit for order creation"""
    allowed, message = await rate_limiter.check_rate_limit(request, "order")
    if not allowed:
        raise HTTPException(status_code=429, detail=message)

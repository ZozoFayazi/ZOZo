"""Admin Authentication & Authorization Module"""
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from fastapi import HTTPException, Header, Depends
import os

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Permissions Definition
PERMISSIONS = {
    "super_admin": ["*"],  # All permissions
    "rellingen_admin": [
        "manage_products",  # Full CRUD
        "upload_images",
        "manage_categories",
        "manage_orders_rellingen",
        "manage_branch_rellingen",
        "view_analytics_rellingen"
    ],
    "henstedt_admin": [
        "toggle_product_active",  # Only active/inactive
        "toggle_product_stock",   # Only in stock/out of stock
        "manage_orders_henstedt",
        "view_analytics_henstedt"
    ]
}

# Role Definitions
ROLES = {
    "admin@zonik-solutions.de": {
        "role": "super_admin",
        "branch_ids": [],  # Access to all branches
        "name": "Super Administrator"
    },
    "info@zozo-burger.de": {
        "role": "rellingen_admin",
        "branch_ids": ["rellingen"],
        "name": "Rellingen Branch Manager"
    },
    "henstedt@zozo-burger.de": {
        "role": "henstedt_admin",
        "branch_ids": ["henstedt-ulzburg"],
        "name": "Henstedt-Ulzburg Branch Manager"
    }
}

class AdminAuth:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_token(email: str, role: str, branch_ids: List[str], additional_claims: Dict = None) -> str:
        """Create a JWT token for admin
        
        Args:
            email: Admin email
            role: Admin role
            branch_ids: List of branch IDs the admin can access
            additional_claims: Optional dict with additional JWT claims (e.g., awaiting_2fa, exp_minutes)
        """
        # Handle custom expiration time
        exp_minutes = JWT_EXPIRATION_HOURS * 60
        if additional_claims and 'exp_minutes' in additional_claims:
            exp_minutes = additional_claims.pop('exp_minutes')
        
        payload = {
            "email": email,
            "role": role,
            "branch_ids": branch_ids,
            "exp": datetime.utcnow() + timedelta(minutes=exp_minutes),
            "iat": datetime.utcnow()
        }
        
        # Add any additional claims
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> Dict:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    @staticmethod
    def get_permissions(role: str) -> List[str]:
        """Get permissions for a role"""
        return PERMISSIONS.get(role, [])
    
    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        """Check if a role has a specific permission"""
        perms = PERMISSIONS.get(role, [])
        return "*" in perms or permission in perms
    
    @staticmethod
    def can_access_branch(branch_ids: List[str], target_branch: str) -> bool:
        """Check if admin can access a specific branch"""
        # Empty branch_ids means super admin (access to all)
        if not branch_ids:
            return True
        return target_branch in branch_ids

# Dependency for protected admin routes
async def get_current_admin(authorization: Optional[str] = Header(None)) -> Dict:
    """Dependency to get current admin from token"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace('Bearer ', '')
    try:
        payload = AdminAuth.decode_token(token)
        return {
            "email": payload["email"],
            "role": payload["role"],
            "branch_ids": payload.get("branch_ids", []),
            "permissions": AdminAuth.get_permissions(payload["role"])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# Permission checkers
def require_permission(permission: str):
    """Decorator factory to require specific permission"""
    async def checker(admin: Dict = Depends(get_current_admin)):
        if not AdminAuth.has_permission(admin["role"], permission):
            raise HTTPException(
                status_code=403, 
                detail=f"Permission denied. Required: {permission}"
            )
        return admin
    return checker

def require_super_admin():
    """Require super admin role"""
    async def checker(admin: Dict = Depends(get_current_admin)):
        if admin["role"] != "super_admin":
            raise HTTPException(status_code=403, detail="Super admin access required")
        return admin
    return checker

def require_branch_access(branch_slug: str):
    """Require access to specific branch"""
    async def checker(admin: Dict = Depends(get_current_admin)):
        if not AdminAuth.can_access_branch(admin["branch_ids"], branch_slug):
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied to branch: {branch_slug}"
            )
        return admin
    return checker

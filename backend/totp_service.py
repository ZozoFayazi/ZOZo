"""TOTP Two-Factor Authentication Service"""
import pyotp
import qrcode
import io
import base64
import secrets
import logging
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class TOTPService:
    """Service for managing TOTP-based 2FA"""
    
    # App configuration
    APP_NAME = "ZOZO Burger Admin"
    BACKUP_CODE_COUNT = 10
    BACKUP_CODE_LENGTH = 8
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    def generate_secret(self) -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    def generate_backup_codes(self, count: int = None) -> List[str]:
        """Generate backup codes for account recovery"""
        count = count or self.BACKUP_CODE_COUNT
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = secrets.token_hex(self.BACKUP_CODE_LENGTH // 2).upper()
            # Format as XXXX-XXXX
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        return codes
    
    def get_totp_uri(self, email: str, secret: str) -> str:
        """Generate TOTP URI for authenticator apps"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=self.APP_NAME)
    
    def generate_qr_code(self, email: str, secret: str) -> str:
        """Generate QR code as base64-encoded PNG"""
        uri = self.get_totp_uri(email, secret)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        base64_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{base64_img}"
    
    def verify_totp(self, secret: str, code: str) -> bool:
        """Verify a TOTP code"""
        if not secret or not code:
            return False
        
        try:
            totp = pyotp.TOTP(secret)
            # Allow 1 time window tolerance (30 seconds before/after)
            return totp.verify(code, valid_window=1)
        except Exception as e:
            logger.error(f"TOTP verification error: {str(e)}")
            return False
    
    async def setup_2fa(self, email: str) -> Dict:
        """
        Initialize 2FA setup for an admin
        Returns secret, QR code, and backup codes
        """
        # Generate new secret
        secret = self.generate_secret()
        
        # Generate backup codes
        backup_codes = self.generate_backup_codes()
        
        # Generate QR code
        qr_code = self.generate_qr_code(email, secret)
        
        # Store pending setup (not yet verified)
        await self.db.admins.update_one(
            {"email": email},
            {
                "$set": {
                    "totp_pending_secret": secret,
                    "totp_pending_backup_codes": backup_codes,
                    "totp_setup_started_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "manual_entry_key": secret  # For manual entry in authenticator
        }
    
    async def confirm_2fa_setup(self, email: str, verification_code: str) -> Tuple[bool, str]:
        """
        Confirm 2FA setup by verifying the first TOTP code
        Returns (success, message)
        """
        # Get admin with pending setup
        admin = await self.db.admins.find_one({"email": email})
        if not admin:
            return False, "Admin nicht gefunden"
        
        pending_secret = admin.get("totp_pending_secret")
        if not pending_secret:
            return False, "Keine ausstehende 2FA-Einrichtung"
        
        # Verify the code
        if not self.verify_totp(pending_secret, verification_code):
            return False, "Ungültiger Bestätigungscode"
        
        # Move from pending to active
        backup_codes = admin.get("totp_pending_backup_codes", [])
        
        await self.db.admins.update_one(
            {"email": email},
            {
                "$set": {
                    "totp_secret": pending_secret,
                    "totp_enabled": True,
                    "totp_backup_codes": backup_codes,
                    "totp_enabled_at": datetime.now(timezone.utc)
                },
                "$unset": {
                    "totp_pending_secret": "",
                    "totp_pending_backup_codes": "",
                    "totp_setup_started_at": ""
                }
            }
        )
        
        return True, "2FA erfolgreich aktiviert"
    
    async def verify_2fa_login(self, email: str, code: str) -> Tuple[bool, str]:
        """
        Verify 2FA code during login
        Also accepts backup codes
        """
        admin = await self.db.admins.find_one({"email": email})
        if not admin:
            return False, "Admin nicht gefunden"
        
        if not admin.get("totp_enabled"):
            return False, "2FA nicht aktiviert"
        
        secret = admin.get("totp_secret")
        if not secret:
            return False, "2FA-Secret nicht gefunden"
        
        # First try TOTP verification
        if self.verify_totp(secret, code):
            return True, "TOTP verifiziert"
        
        # Check if it's a backup code
        backup_codes = admin.get("totp_backup_codes", [])
        formatted_code = code.upper()
        
        # Add dash if missing (XXXXXXXX -> XXXX-XXXX)
        if len(formatted_code) == 8 and '-' not in formatted_code:
            formatted_code = f"{formatted_code[:4]}-{formatted_code[4:]}"
        
        if formatted_code in backup_codes:
            # Remove used backup code
            backup_codes.remove(formatted_code)
            await self.db.admins.update_one(
                {"email": email},
                {"$set": {"totp_backup_codes": backup_codes}}
            )
            remaining = len(backup_codes)
            return True, f"Backup-Code verwendet ({remaining} verbleibend)"
        
        return False, "Ungültiger 2FA-Code"
    
    async def disable_2fa(self, email: str, admin_email: str = None) -> Tuple[bool, str]:
        """
        Disable 2FA for an admin
        admin_email is the email of the admin performing the action (for audit)
        """
        admin = await self.db.admins.find_one({"email": email})
        if not admin:
            return False, "Admin nicht gefunden"
        
        if not admin.get("totp_enabled"):
            return False, "2FA ist nicht aktiviert"
        
        await self.db.admins.update_one(
            {"email": email},
            {
                "$set": {
                    "totp_enabled": False,
                    "totp_disabled_at": datetime.now(timezone.utc),
                    "totp_disabled_by": admin_email or email
                },
                "$unset": {
                    "totp_secret": "",
                    "totp_backup_codes": "",
                    "totp_pending_secret": "",
                    "totp_pending_backup_codes": ""
                }
            }
        )
        
        return True, "2FA deaktiviert"
    
    async def regenerate_backup_codes(self, email: str) -> Tuple[bool, List[str], str]:
        """
        Generate new backup codes for an admin
        Returns (success, new_codes, message)
        """
        admin = await self.db.admins.find_one({"email": email})
        if not admin:
            return False, [], "Admin nicht gefunden"
        
        if not admin.get("totp_enabled"):
            return False, [], "2FA ist nicht aktiviert"
        
        # Generate new codes
        new_codes = self.generate_backup_codes()
        
        await self.db.admins.update_one(
            {"email": email},
            {
                "$set": {
                    "totp_backup_codes": new_codes,
                    "totp_backup_codes_regenerated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return True, new_codes, "Neue Backup-Codes generiert"
    
    async def get_2fa_status(self, email: str) -> Dict:
        """Get 2FA status for an admin"""
        admin = await self.db.admins.find_one({"email": email})
        if not admin:
            return {"error": "Admin nicht gefunden"}
        
        return {
            "enabled": admin.get("totp_enabled", False),
            "enabled_at": admin.get("totp_enabled_at"),
            "backup_codes_remaining": len(admin.get("totp_backup_codes", [])),
            "has_pending_setup": bool(admin.get("totp_pending_secret")),
            "required": admin.get("role") == "super_admin"  # Super Admin requires 2FA
        }
    
    def is_2fa_required(self, role: str) -> bool:
        """Check if 2FA is required for a given role"""
        # Super Admin must have 2FA
        return role == "super_admin"

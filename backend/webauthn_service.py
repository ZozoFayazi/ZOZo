"""
WebAuthn/Passkey Service for Admin 2FA

MVP Implementation:
- Register passkey (setup)
- Login with passkey (verify)
- Backup codes for recovery
- Audit logging
"""
import os
import secrets
import base64
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    AuthenticatorAttachment,
    ResidentKeyRequirement,
    PublicKeyCredentialDescriptor,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

import logging

logger = logging.getLogger(__name__)

# WebAuthn Configuration
RP_ID = os.getenv('WEBAUTHN_RP_ID', 'zozo-cashx-pos.preview.emergentagent.com')
RP_NAME = "ZOZO Burger Admin"
ORIGIN = os.getenv('WEBAUTHN_ORIGIN', 'https://eatease-18.preview.emergentagent.com')


class WebAuthnService:
    """Service for managing WebAuthn/Passkey authentication"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def start_registration(self, admin_email: str) -> Dict:
        """
        Start passkey registration (Step 1)
        
        Returns registration options for frontend
        """
        # Get admin
        admin = await self.db.admins.find_one({"email": admin_email})
        if not admin:
            raise ValueError("Admin not found")
        
        admin_id = str(admin['_id'])
        
        # Generate registration options
        options = generate_registration_options(
            rp_id=RP_ID,
            rp_name=RP_NAME,
            user_id=admin_id.encode('utf-8'),  # Must be bytes!
            user_name=admin_email,
            user_display_name=admin.get('name', admin_email),
            authenticator_selection=AuthenticatorSelectionCriteria(
                # Don't force platform - allow both platform (FaceID) and cross-platform (Security Keys)
                # This ensures compatibility across all devices
                authenticator_attachment=None,  # More compatible than PLATFORM
                resident_key=ResidentKeyRequirement.PREFERRED,
                user_verification=UserVerificationRequirement.PREFERRED,
            ),
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
            ],
        )
        
        # Store challenge temporarily
        await self.db.webauthn_challenges.update_one(
            {"admin_email": admin_email, "type": "registration"},
            {
                "$set": {
                    "challenge": base64.b64encode(options.challenge).decode('utf-8'),
                    "created_at": datetime.now(timezone.utc),
                    "expires_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        
        logger.info(f"WebAuthn registration started for {admin_email}")
        
        # Convert to JSON and parse back to dict
        import json
        options_json = options_to_json(options)
        return json.loads(options_json)
    
    async def verify_registration(
        self, 
        admin_email: str, 
        credential: Dict,
        device_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Verify passkey registration (Step 2)
        
        Args:
            admin_email: Admin email
            credential: Registration response from frontend
            device_name: Optional device name (e.g. "iPhone 14")
        
        Returns:
            (success, message) tuple
        """
        try:
            # Get stored challenge
            challenge_doc = await self.db.webauthn_challenges.find_one({
                "admin_email": admin_email,
                "type": "registration"
            })
            
            if not challenge_doc:
                return False, "Challenge nicht gefunden. Bitte starten Sie erneut."
            
            expected_challenge = base64.b64decode(challenge_doc['challenge'])
            
            # Verify registration
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=expected_challenge,
                expected_origin=ORIGIN,
                expected_rp_id=RP_ID,
            )
            
            # Store credential
            admin = await self.db.admins.find_one({"email": admin_email})
            
            credential_doc = {
                "admin_id": str(admin['_id']),
                "admin_email": admin_email,
                "credential_id": base64.b64encode(verification.credential_id).decode('utf-8'),
                "public_key": base64.b64encode(verification.credential_public_key).decode('utf-8'),
                "sign_count": verification.sign_count,
                "device_name": device_name or "Unbenanntes Gerät",
                "transports": credential.get('response', {}).get('transports', []),
                "created_at": datetime.now(timezone.utc),
                "last_used_at": None
            }
            
            await self.db.webauthn_credentials.insert_one(credential_doc)
            
            # Generate backup codes
            backup_codes = self._generate_backup_codes()
            
            # Store hashed backup codes
            from admin_auth import AdminAuth
            hashed_codes = [AdminAuth.hash_password(code) for code in backup_codes]
            
            await self.db.admins.update_one(
                {"email": admin_email},
                {
                    "$set": {
                        "passkey_enabled": True,
                        "passkey_backup_codes": hashed_codes,
                        "passkey_enabled_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            # Delete challenge
            await self.db.webauthn_challenges.delete_one({"_id": challenge_doc['_id']})
            
            logger.info(f"Passkey registered successfully for {admin_email}")
            
            return True, backup_codes
            
        except Exception as e:
            logger.error(f"Passkey registration verification failed: {str(e)}")
            return False, f"Verifizierung fehlgeschlagen: {str(e)}"
    
    async def start_authentication(self, admin_email: str) -> Dict:
        """
        Start passkey authentication (Step 1 of login)
        
        Returns authentication options for frontend
        """
        # Get admin's credentials
        credentials = await self.db.webauthn_credentials.find({
            "admin_email": admin_email
        }).to_list(10)
        
        if not credentials:
            raise ValueError("Keine Passkeys gefunden")
        
        # Convert to PublicKeyCredentialDescriptor
        allow_credentials = [
            PublicKeyCredentialDescriptor(
                id=base64.b64decode(cred['credential_id']),
                transports=cred.get('transports', [])
            )
            for cred in credentials
        ]
        
        # Generate authentication options
        options = generate_authentication_options(
            rp_id=RP_ID,
            allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.PREFERRED,
        )
        
        # Store challenge
        await self.db.webauthn_challenges.update_one(
            {"admin_email": admin_email, "type": "authentication"},
            {
                "$set": {
                    "challenge": base64.b64encode(options.challenge).decode('utf-8'),
                    "created_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        
        logger.info(f"WebAuthn authentication started for {admin_email}")
        
        # Convert to JSON and parse back to dict
        import json
        options_json = options_to_json(options)
        return json.loads(options_json)
    
    async def verify_authentication(
        self, 
        admin_email: str, 
        credential: Dict
    ) -> Tuple[bool, str]:
        """
        Verify passkey authentication (Step 2 of login)
        
        Returns:
            (success, message) tuple
        """
        try:
            # Get stored challenge
            challenge_doc = await self.db.webauthn_challenges.find_one({
                "admin_email": admin_email,
                "type": "authentication"
            })
            
            if not challenge_doc:
                return False, "Challenge nicht gefunden"
            
            expected_challenge = base64.b64decode(challenge_doc['challenge'])
            
            # Get credential from DB
            credential_id_raw = credential.get('rawId') or credential.get('id')
            credential_doc = await self.db.webauthn_credentials.find_one({
                "admin_email": admin_email,
                "credential_id": credential_id_raw
            })
            
            if not credential_doc:
                return False, "Credential nicht gefunden"
            
            # Verify authentication
            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=expected_challenge,
                expected_origin=ORIGIN,
                expected_rp_id=RP_ID,
                credential_public_key=base64.b64decode(credential_doc['public_key']),
                credential_current_sign_count=credential_doc['sign_count'],
            )
            
            # Update sign count and last used
            await self.db.webauthn_credentials.update_one(
                {"_id": credential_doc['_id']},
                {
                    "$set": {
                        "sign_count": verification.new_sign_count,
                        "last_used_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            # Delete challenge
            await self.db.webauthn_challenges.delete_one({"_id": challenge_doc['_id']})
            
            logger.info(f"Passkey authentication successful for {admin_email}")
            
            return True, "Authentifizierung erfolgreich"
            
        except Exception as e:
            logger.error(f"Passkey authentication failed: {str(e)}")
            return False, f"Authentifizierung fehlgeschlagen: {str(e)}"
    
    async def verify_backup_code(self, admin_email: str, code: str) -> Tuple[bool, str]:
        """
        Verify backup code for recovery
        
        Args:
            admin_email: Admin email
            code: Backup code (8 characters)
        
        Returns:
            (success, message) tuple
        """
        admin = await self.db.admins.find_one({"email": admin_email})
        if not admin or not admin.get('passkey_enabled'):
            return False, "Passkey nicht aktiviert"
        
        backup_codes = admin.get('passkey_backup_codes', [])
        if not backup_codes:
            return False, "Keine Backup Codes verfügbar"
        
        # Check code against all stored hashes
        from admin_auth import AdminAuth
        
        for i, hashed_code in enumerate(backup_codes):
            if AdminAuth.verify_password(code, hashed_code):
                # Valid code - remove it (one-time use)
                backup_codes.pop(i)
                
                await self.db.admins.update_one(
                    {"email": admin_email},
                    {"$set": {"passkey_backup_codes": backup_codes}}
                )
                
                remaining = len(backup_codes)
                logger.info(f"Backup code used for {admin_email}. Remaining: {remaining}")
                
                if remaining < 3:
                    return True, f"✅ Code gültig. Warnung: Nur noch {remaining} Backup Codes verfügbar!"
                
                return True, "✅ Backup Code akzeptiert"
        
        return False, "Ungültiger Backup Code"
    
    async def get_passkey_status(self, admin_email: str) -> Dict:
        """Get passkey status for admin"""
        admin = await self.db.admins.find_one({"email": admin_email})
        if not admin:
            return {"enabled": False}
        
        credentials = await self.db.webauthn_credentials.find({
            "admin_email": admin_email
        }).to_list(10)
        
        backup_codes_count = len(admin.get('passkey_backup_codes', []))
        
        return {
            "enabled": admin.get('passkey_enabled', False),
            "credentials_count": len(credentials),
            "credentials": [
                {
                    "device_name": c.get('device_name'),
                    "created_at": c.get('created_at'),
                    "last_used_at": c.get('last_used_at')
                }
                for c in credentials
            ],
            "backup_codes_remaining": backup_codes_count,
            "require_passkey_setup": admin.get('require_passkey_setup', False)
        }
    
    async def remove_credential(
        self, 
        admin_email: str, 
        credential_id: str,
        removed_by: str
    ) -> Tuple[bool, str]:
        """
        Remove a passkey credential
        
        Super Admin cannot remove their own last credential without backup codes
        """
        admin = await self.db.admins.find_one({"email": admin_email})
        if not admin:
            return False, "Admin nicht gefunden"
        
        # Count credentials
        cred_count = await self.db.webauthn_credentials.count_documents({
            "admin_email": admin_email
        })
        
        # Safety check for Super Admin
        if admin.get('role') == 'super_admin' and cred_count == 1:
            backup_codes = admin.get('passkey_backup_codes', [])
            if len(backup_codes) < 3:
                return False, "Super Admin kann letztes Credential nicht entfernen ohne Backup Codes"
        
        # Remove credential
        result = await self.db.webauthn_credentials.delete_one({
            "admin_email": admin_email,
            "credential_id": credential_id
        })
        
        if result.deleted_count == 0:
            return False, "Credential nicht gefunden"
        
        # If no credentials left, disable passkey
        remaining = await self.db.webauthn_credentials.count_documents({
            "admin_email": admin_email
        })
        
        if remaining == 0:
            await self.db.admins.update_one(
                {"email": admin_email},
                {"$set": {"passkey_enabled": False}}
            )
        
        logger.info(f"Passkey credential removed for {admin_email} by {removed_by}")
        
        return True, "Credential entfernt"
    
    def _generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes"""
        codes = []
        for _ in range(count):
            # 8-character alphanumeric code
            code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            codes.append(code)
        return codes
    
    async def regenerate_backup_codes(self, admin_email: str) -> List[str]:
        """Regenerate backup codes (invalidates old ones)"""
        from admin_auth import AdminAuth
        
        backup_codes = self._generate_backup_codes()
        hashed_codes = [AdminAuth.hash_password(code) for code in backup_codes]
        
        await self.db.admins.update_one(
            {"email": admin_email},
            {"$set": {"passkey_backup_codes": hashed_codes}}
        )
        
        logger.info(f"Backup codes regenerated for {admin_email}")
        
        return backup_codes

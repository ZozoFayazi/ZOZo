#!/usr/bin/env python3
"""
Admin-Accounts wiederherstellen nach Re-Deployment
Führen Sie dieses Script aus wenn Admin-Login nicht funktioniert
"""

import sys
sys.path.insert(0, '/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from datetime import datetime, timezone
import uuid
import bcrypt

async def restore_admin_accounts():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'test_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("="*80)
    print("🔑 ADMIN-ACCOUNTS WIEDERHERSTELLEN")
    print("="*80)
    print()
    
    # Standard-Passwort (ÄNDERN SIE DAS!)
    default_password = "ZozoAdmin2024!"
    password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Admin-Accounts definieren
    admin_accounts = [
        {
            "id": str(uuid.uuid4()),
            "email": "admin@zonik-solutions.de",
            "password": password_hash,
            "role": "super_admin",
            "name": "Super Admin",
            "active": True,
            "branch_ids": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "email": "info@zozo-burger.de",
            "password": password_hash,
            "role": "manager",
            "name": "Rellingen Manager",
            "active": True,
            "branch_ids": ["rellingen"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "email": "henstedt@zozo-burger.de",
            "password": password_hash,
            "role": "manager",
            "name": "Henstedt Manager",
            "active": True,
            "branch_ids": ["henstedt-ulzburg"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]
    
    for account in admin_accounts:
        # Prüfen ob Account existiert
        existing = await db.admin_users.find_one({"email": account["email"]})
        
        if existing:
            print(f"⚠️  Account existiert bereits: {account['email']}")
            print(f"   → Passwort wird NICHT überschrieben")
        else:
            await db.admin_users.insert_one(account)
            print(f"✅ Account erstellt: {account['email']}")
            print(f"   Rolle: {account['role']}")
            print(f"   Passwort: {default_password}")
    
    print()
    print("="*80)
    print("✅ ADMIN-ACCOUNTS WIEDERHERGESTELLT!")
    print("="*80)
    print()
    print("Login-Daten:")
    print(f"  E-Mail: admin@zonik-solutions.de")
    print(f"  Passwort: {default_password}")
    print()
    print("⚠️  WICHTIG: Bitte Passwort nach erstem Login ändern!")
    print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(restore_admin_accounts())

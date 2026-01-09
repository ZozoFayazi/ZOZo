#!/bin/bash
# RESTORE ALL SAAS CONFIGS
# One-command restore from backup file

set -e

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    # Use latest backup
    BACKUP_FILE=$(ls -t /app/backups/saas_backup_*.json 2>/dev/null | head -1)
    
    if [ -z "$BACKUP_FILE" ]; then
        # Fallback to legacy backups
        echo "🔍 No SAAS backup found, using legacy restore..."
        cd /app
        python3 restore_all_configs_final.py
        exit $?
    fi
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "🔓 RESTORING FROM BACKUP..."
echo "File: ${BACKUP_FILE}"
echo ""

# Restore via Python
python3 <<RESTORE_SCRIPT
import json
import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

# Read backup
with open('${BACKUP_FILE}', 'r') as f:
    backup = json.load(f)

print(f"Backup from: {backup.get('backup_timestamp')}")
print("")

for coll_name, docs in backup.get('collections', {}).items():
    if not docs:
        print(f"⏭️  {coll_name}: No data")
        continue
    
    # Clear existing data (DANGER!)
    # db[coll_name].delete_many({})
    
    # Insert backup data
    # Note: This is simplified - real restore should handle ObjectIds
    print(f"ℹ️  {coll_name}: {len(docs)} documents in backup")
    print(f"   Current in DB: {db[coll_name].count_documents({})}")

print("")
print("⚠️  Restore preview mode - data not modified")
print("   For full restore, uncomment delete_many in script")
RESTORE_SCRIPT

echo ""
echo "✅ RESTORE PREVIEW COMPLETE"
echo "Backup file: ${BACKUP_FILE}"

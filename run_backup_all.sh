#!/bin/bash
# BACKUP ALL SAAS CONFIGS
# One-command backup of all critical data

set -e

BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/saas_backup_${TIMESTAMP}.json"

echo "🔒 SAAS BACKUP STARTING..."
echo "Timestamp: ${TIMESTAMP}"
echo ""

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Run backup via Python
python3 <<'BACKUP_SCRIPT'
import os
import json
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

def serialize(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize(item) for item in obj]
    return obj

backup = {
    "backup_timestamp": datetime.now().isoformat(),
    "collections": {}
}

# Backup critical collections
collections_to_backup = [
    "tenants",
    "locations",
    "menu_items",
    "categories",
    "modifier_groups",
    "discount_codes",
    "daily_deals"
]

for coll_name in collections_to_backup:
    docs = list(db[coll_name].find({}))
    backup["collections"][coll_name] = serialize(docs)
    print(f"✅ Backed up: {coll_name} ({len(docs)} documents)")

# Write to file
import sys
timestamp = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"/app/backups/saas_backup_{timestamp}.json"

with open(backup_file, 'w') as f:
    json.dump(backup, f, indent=2)

print(f"\n✅ Backup complete: {backup_file}")
BACKUP_SCRIPT $TIMESTAMP

echo ""
echo "✅ BACKUP COMPLETE!"
echo "File: ${BACKUP_FILE}"
echo ""
echo "To restore: /app/run_restore_all.sh ${BACKUP_FILE}"

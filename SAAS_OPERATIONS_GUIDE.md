# 🔧 SaaS Betriebsroutine - Automatisierung
## Automatische Tests, Backups & Health Checks

**Setup Date:** 2026-01-09  
**Purpose:** Maximale Betriebssicherheit durch Automation  

---

## 1️⃣ AUTOMATED SMOKE TESTS

### Pre-Deployment:
```bash
# Before every deployment:
cd /app
python3 auto_smoke_test.py

if [ $? -eq 0 ]; then
    echo "✅ Safe to deploy"
    # proceed with deployment
else
    echo "❌ DO NOT DEPLOY - Tests failed"
    exit 1
fi
```

### Post-Deployment:
```bash
# After every deployment:
sleep 10  # Wait for services to stabilize
cd /app
python3 auto_smoke_test.py

if [ $? -ne 0 ]; then
    echo "❌ DEPLOYMENT FAILED - Rolling back"
    # Restore from backup
    python3 restore_all_configs_final.py
fi
```

---

## 2️⃣ DAILY BACKUPS (Cron)

### Setup:
```bash
# Edit crontab
crontab -e

# Add this line (daily at 3 AM):
0 3 * * * cd /app && python3 -c "import json, os; from pymongo import MongoClient; from datetime import datetime; from bson import ObjectId; os.makedirs('/app/backups/daily', exist_ok=True); client = MongoClient(os.environ.get('MONGO_URL')); db = client['zozo_burger']; serialize = lambda o: str(o) if isinstance(o, ObjectId) else o.isoformat() if isinstance(o, datetime) else {k: serialize(v) for k, v in o.items()} if isinstance(o, dict) else [serialize(i) for i in o] if isinstance(o, list) else o; backup = {'timestamp': datetime.now().isoformat(), 'collections': {c: serialize(list(db[c].find({}))) for c in ['tenants', 'locations', 'menu_items', 'categories']}}; f = f'/app/backups/daily/backup_{datetime.now().strftime(\"%Y%m%d\")}.json'; open(f, 'w').write(json.dumps(backup, indent=2)); print(f'✅ Daily backup: {f}')" >> /var/log/daily_backup.log 2>&1
```

### Cleanup old backups (keep last 30 days):
```bash
# Daily at 4 AM:
0 4 * * * find /app/backups/daily -name "backup_*.json" -mtime +30 -delete
```

---

## 3️⃣ HOURLY HEALTH CHECK

### Setup:
```bash
# Every hour
0 * * * * cd /app && python3 SAAS_PERSISTENCE_SMOKE_TEST.py >> /var/log/health_check.log 2>&1 || echo "❌ Health check failed at $(date)" | mail -s "ZOZO Health Alert" admin@zonik-solutions.de
```

### What it checks:
- Tenants exist
- Locations configured
- PayPal + POS configs present
- Menu items present
- Opening hours configured

### On Failure:
- Email alert sent
- Log entry created
- Exit code 1

---

## 4️⃣ AUTOMATED SMOKE TEST ON PUBLISH

### Implementation:

Publish Button now automatically:
1. ✅ Runs smoke test (validates tenant data)
2. ✅ Creates backup (before publish)
3. ✅ Publishes tenant
4. ✅ Logs audit event

**Code in:** `/app/backend/super_admin_endpoints.py` (publish_tenant function)

### Audit Trail:

All events logged to `tenant_onboarding_events` collection:
```javascript
{
  "tenant_id": "...",
  "event_type": "tenant_published",
  "event_data": {
    "locations": 2,
    "menu_items": 17
  },
  "actor_email": "admin@zonik-solutions.de",
  "timestamp": "2026-01-09T08:50:00Z"
}
```

---

## 5️⃣ FAILURE ALERTS

### Setup Email Alerts:
```bash
# Install mailutils if not present
apt-get install -y mailutils

# Configure SMTP (use Resend API)
echo "set smtp=smtp://smtp.resend.com:587" >> /etc/mail.rc
echo "set smtp-auth=login" >> /etc/mail.rc
echo "set smtp-auth-user=resend" >> /etc/mail.rc
echo "set smtp-auth-password=${RESEND_API_KEY}" >> /etc/mail.rc
```

### Alert Script:
```bash
#!/bin/bash
# /app/alert_on_failure.sh

cd /app
python3 SAAS_PERSISTENCE_SMOKE_TEST.py

if [ $? -ne 0 ]; then
    SUBJECT="❌ ZOZO SaaS Health Check Failed"
    BODY="Smoke test failed at $(date). Check /tmp/persistence_report.txt"
    
    echo "$BODY" | mail -s "$SUBJECT" admin@zonik-solutions.de
fi
```

---

## 📊 MONITORING DASHBOARD (Optional)

### Metrics to track:
- Total Tenants
- Active vs Draft Tenants
- Total Orders (all tenants)
- Smoke Test Success Rate
- Average Onboarding Time
- Backup Success Rate

### Quick Check:
```bash
cd /app
python3 << 'STATS'
from pymongo import MongoClient
import os

client = MongoClient(os.environ.get('MONGO_URL'))
db = client['zozo_burger']

print("📊 SaaS Stats:")
print(f"  Tenants: {db.tenants.count_documents({})}")
print(f"  Active: {db.tenants.count_documents({'status': 'active'})}")
print(f"  Locations: {db.locations.count_documents({})}")
print(f"  Products: {db.menu_items.count_documents({})}")
print(f"  Orders: {db.orders.count_documents({})}")
STATS
```

---

## ✅ RECOMMENDED CRON SETUP:

```cron
# Daily Backup (3 AM)
0 3 * * * cd /app && [backup command from above] >> /var/log/daily_backup.log 2>&1

# Cleanup old backups (4 AM)
0 4 * * * find /app/backups/daily -mtime +30 -delete

# Hourly Health Check
0 * * * * cd /app && python3 SAAS_PERSISTENCE_SMOKE_TEST.py >> /var/log/health.log 2>&1 || /app/alert_on_failure.sh

# Weekly Badge Update (Sunday 2 AM)
0 2 * * 0 cd /app/backend && python3 daily_badge_update.py >> /var/log/badges.log 2>&1
```

---

## 🛡️ RESULT:

**Mit dieser Betriebsroutine:**

✅ **Vor jedem Deploy:** Smoke Test automatisch  
✅ **Nach jedem Deploy:** Smoke Test automatisch  
✅ **Pro Tenant:** 1 Backup pro Tag  
✅ **Pro System:** 1 Health Check pro Stunde  
✅ **Bei Failure:** Email Alert  

**= Maximale Sicherheit + Minimaler Aufwand**

---

**Status:** 🟢 ENTERPRISE-READY

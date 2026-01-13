# 🔒 FINAL CONFIG LOCK - ZOZO Burger Production

**Datum:** 08.01.2026
**Status:** ✅ PRODUCTION READY & LOCKED
**Dokumentationstyp:** FINAL CONFIG BACKUP & RESTORE ANLEITUNG

---

## 📋 Übersicht

Alle kritischen Konfigurationen wurden dauerhaft gesichert und sind **LOCKED**. 
Dieses Dokument dient als Master-Referenz für alle Produktions-Credentials.

---

## 1️⃣ ExpertOrder POS Integration

### Status
✅ **BEIDE Standorte funktionieren**  
✅ **LIVE MODE aktiv**  
✅ **Bestellungen werden erfolgreich an EOCloud gesendet**

### Rellingen Configuration
```json
{
  "location_name": "ZOZO Burger Rellingen",
  "location_id": "87de5af8-e424-4fd0-9094-b77b0bf2be77",
  "location_slug": "rellingen",
  "pos_config": {
    "provider": "expertorder",
    "enabled": true,
    "api_key": "4bbc443c82674f93e910399ca7931b37b45e55ba",
    "base_url": "https://zozo.eocloud.de",
    "broker_name": "zozo-burger.de",
    "test_mode": false
  },
  "test_result": "✅ SUCCESS - Bestellung QT-164012 an EOCloud gesendet"
}
```

### Henstedt-Ulzburg Configuration
```json
{
  "location_name": "ZOZO Burger Henstedt-Ulzburg",
  "location_id": "e5d3dda4-fd50-4388-b08a-9ddfc4098b6f",
  "location_slug": "henstedt-ulzburg",
  "pos_config": {
    "provider": "expertorder",
    "enabled": true,
    "api_key": "90dd43e5c58b7c2a8ddd1eb4916ae8196d8e1073",
    "base_url": "https://zozo.eocloud.de",
    "broker_name": "zozo-burger.de",
    "test_mode": false
  },
  "test_result": "✅ SUCCESS - Bestellung HT-164040 an EOCloud gesendet"
}
```

### Speicherort in Datenbank
- **Collection:** `locations`
- **Field:** `pos_config` (direkt im location document)
- **Wichtig:** Settings sind NICHT in `location_settings`, sondern direkt in `locations`!

---

## 2️⃣ PayPal LIVE Integration

### Status
✅ **BEIDE Standorte im LIVE MODE**  
✅ **Sandbox deaktiviert**  
✅ **Echte Zahlungen werden verarbeitet**

### Rellingen PayPal LIVE
```json
{
  "location_name": "ZOZO Burger Rellingen",
  "location_id": "87de5af8-e424-4fd0-9094-b77b0bf2be77",
  "paypal_client_id": "Ac94dFnQk1qbwEndBfUOAODPMQBhskka3iMusznawOaezGYjzSUpKoyPk5EBgLzKNAgwKEK_UHcUdRB7",
  "paypal_secret_key": "EKX-jMnXB6jQkIl5tw1XakUfHIguAKeQimrMfyD9P9bBN_tnCxcRsAyJ88j2F-nSnVCyMDHzc669exAB",
  "paypal_sandbox_mode": false,
  "paypal_enabled": true,
  "mode": "LIVE",
  "test_order": "ZOZO-1063",
  "test_paypal_order_id": "5088648547814250W"
}
```

### Henstedt-Ulzburg PayPal LIVE
```json
{
  "location_name": "ZOZO Burger Henstedt-Ulzburg",
  "location_id": "e5d3dda4-fd50-4388-b08a-9ddfc4098b6f",
  "paypal_client_id": "AR7Brjjwwg432MxkzLiRMMeZdtynccfZyUZtpFCTllt2NfKNlIa3ftX6jLH_iDssVdrDMRB8YUmcY9kz",
  "paypal_secret_key": "EHTM6aK5qDXaWn_dXWhEPa32PVJjcByO4xoHLb1r3K-v2TMv0MVQ-KmwwTf5KvMCyja7gSi2a7n8wv8J",
  "paypal_sandbox_mode": false,
  "paypal_enabled": true,
  "mode": "LIVE",
  "test_order": "ZOZO-1064",
  "test_paypal_order_id": "4GY35674RY298584J"
}
```

### Speicherort in Datenbank
- **Collection:** `locations`
- **Fields:** `paypal_client_id`, `paypal_secret_key`, `paypal_sandbox_mode`, `paypal_enabled` (direkt im location document)
- **Payment Flow:** Korrekt implementiert - Order wird erst nach erfolgreicher PayPal-Zahlung an POS gesendet

---

## 3️⃣ Environment Variables

### Backend (.env)
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
APP_URL="https://eatease-18.preview.emergentagent.com"
EMERGENT_LLM_KEY=sk-emergent-5882954D84fC35cB4D
RESEND_API_KEY=re_KS2rud3s_GSvEJZHwnpLdJm9TU5WuK18g
SENDER_EMAIL=noreply@zozo-burger.de
RESEND_USE_TEST_DOMAIN=false
POS_ALERT_EMAIL=info@zozo-burger.de
INCLUDE_ORDER_DETAILS_IN_ALERT_EMAIL=false
JWT_SECRET=uKoRwC3BpBOQmf_XfTD5QdtU3fTuxTgBjvbPnTGAngjAReUUIDJirlPLcwxGwgNync49zQly0-_1Md_oknHvJw
ADMIN_JWT_SECRET=eGOlbffRwRjsTGcKja83e6Bt5yJdrF0Wg_6jat3Q6TPj5hGWuVKewbamL4RUV2DDuP0l-_DJ49LGHEk7Lv9fag
```

### Frontend (.env)
```bash
REACT_APP_BACKEND_URL=https://eatease-18.preview.emergentagent.com
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

### ⚠️ KRITISCH - NICHT VERÄNDERN
- `REACT_APP_BACKEND_URL` **MUSS** exakt diesen Wert haben
- `MONGO_URL` ist pre-configured
- Alle JWT Secrets wurden am 06.01.2026 rotiert

---

## 4️⃣ Backup Files

### Verfügbare Backups
```
/app/PAYPAL_LIVE_FINAL_BACKUP.json          ✅ PayPal LIVE Credentials
/app/EXPERTORDER_FINAL_CONFIG_BACKUP.json   ✅ ExpertOrder POS Configuration
/app/FINAL_CONFIG_BACKUP.json               ✅ Complete system backup
```

---

## 5️⃣ Restore Instructions

### Falls Configs verloren gehen:

#### Option A: Automatisches Restore Script
```bash
cd /app
python3 restore_all_configs_final.py
```

#### Option B: Manuelles Restore via Python
```python
import os
from pymongo import MongoClient
from datetime import datetime

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

# Rellingen PayPal
db.locations.update_one(
    {"id": "87de5af8-e424-4fd0-9094-b77b0bf2be77"},
    {"$set": {
        "paypal_client_id": "Ac94dFnQk1qbwEndBfUOAODPMQBhskka3iMusznawOaezGYjzSUpKoyPk5EBgLzKNAgwKEK_UHcUdRB7",
        "paypal_secret_key": "EKX-jMnXB6jQkIl5tw1XakUfHIguAKeQimrMfyD9P9bBN_tnCxcRsAyJ88j2F-nSnVCyMDHzc669exAB",
        "paypal_sandbox_mode": False,
        "paypal_enabled": True
    }}
)

# Henstedt PayPal
db.locations.update_one(
    {"id": "e5d3dda4-fd50-4388-b08a-9ddfc4098b6f"},
    {"$set": {
        "paypal_client_id": "AR7Brjjwwg432MxkzLiRMMeZdtynccfZyUZtpFCTllt2NfKNlIa3ftX6jLH_iDssVdrDMRB8YUmcY9kz",
        "paypal_secret_key": "EHTM6aK5qDXaWn_dXWhEPa32PVJjcByO4xoHLb1r3K-v2TMv0MVQ-KmwwTf5KvMCyja7gSi2a7n8wv8J",
        "paypal_sandbox_mode": False,
        "paypal_enabled": True
    }}
)

# Rellingen ExpertOrder
db.locations.update_one(
    {"id": "87de5af8-e424-4fd0-9094-b77b0bf2be77"},
    {"$set": {
        "pos_config": {
            "provider": "expertorder",
            "enabled": True,
            "api_key": "4bbc443c82674f93e910399ca7931b37b45e55ba",
            "base_url": "https://zozo.eocloud.de",
            "broker_name": "zozo-burger.de",
            "test_mode": False
        }
    }}
)

# Henstedt ExpertOrder
db.locations.update_one(
    {"id": "e5d3dda4-fd50-4388-b08a-9ddfc4098b6f"},
    {"$set": {
        "pos_config": {
            "provider": "expertorder",
            "enabled": True,
            "api_key": "90dd43e5c58b7c2a8ddd1eb4916ae8196d8e1073",
            "base_url": "https://zozo.eocloud.de",
            "broker_name": "zozo-burger.de",
            "test_mode": False
        }
    }}
)

print("✅ All configs restored!")
```

---

## 6️⃣ Verification Script

### Status überprüfen:
```bash
cd /app
python3 << 'VERIFY'
import os
from pymongo import MongoClient

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(mongo_url)
db = client['zozo_burger']

locations = list(db.locations.find({}))
for loc in locations:
    print(f"\n📍 {loc['name']}")
    
    # PayPal
    if loc.get('paypal_client_id'):
        mode = "LIVE" if not loc.get('paypal_sandbox_mode', True) else "SANDBOX"
        print(f"   💳 PayPal: ✅ {mode} Mode")
    else:
        print(f"   💳 PayPal: ❌ Not configured")
    
    # POS
    pos = loc.get('pos_config', {})
    if pos and pos.get('enabled'):
        mode = "TEST" if pos.get('test_mode', True) else "LIVE"
        print(f"   🔧 POS: ✅ {mode} Mode ({pos.get('provider', 'unknown').upper()})")
    else:
        print(f"   🔧 POS: ❌ Not configured")
VERIFY
```

---

## 7️⃣ Connection Tests

### ExpertOrder POS Test (beide Standorte)
```bash
cd /app
PYTHONPATH=/app/backend python3 test_order_rellingen.py
PYTHONPATH=/app/backend python3 test_order_henstedt.py
```

### PayPal Test
```bash
cd /app
python3 test_paypal_both_locations.py
```

---

## 8️⃣ CRITICAL WARNINGS ⚠️

### Was NIEMALS verändert werden darf:
1. ❌ `REACT_APP_BACKEND_URL` in `/app/frontend/.env`
2. ❌ `MONGO_URL` in `/app/backend/.env`
3. ❌ `JWT_SECRET` & `ADMIN_JWT_SECRET` (es sei denn, du rotierst bewusst)
4. ❌ PayPal `client_id` & `secret_key` (es sei denn, Credentials ändern sich)
5. ❌ ExpertOrder `api_key` (es sei denn, neue Keys von EOCloud)

### Was sicher verändert werden kann:
✅ `APP_URL` (wenn Preview URL sich ändert)
✅ `RESEND_API_KEY` (wenn du zu anderem Email-Provider wechselst)
✅ `POS_ALERT_EMAIL` (wenn Admin-Email sich ändert)

---

## 9️⃣ Deployment Protection

### Warum gingen Configs verloren?
BEI DEPLOYMENTS können ENV-Variablen oder DB-Daten überschrieben werden, wenn:
- Seeding-Scripts laufen
- Migrations ausgeführt werden
- `.env` Files aus Repo deployed werden (die möglicherweise alte/Test-Werte haben)

### Schutz vor Datenverlust:
1. ✅ Alle Credentials sind MEHRFACH gesichert (JSON backups)
2. ✅ Restore-Script ist vorhanden und getestet
3. ✅ Dieses Dokument dient als Master-Referenz
4. ✅ Credentials sind in DB, nicht in ENV files (weniger anfällig)

---

## 🎯 FINAL STATUS

```
✅ ExpertOrder Rellingen:      WORKING (LIVE)
✅ ExpertOrder Henstedt:       WORKING (LIVE)
✅ PayPal Rellingen:           CONFIGURED (LIVE)
✅ PayPal Henstedt:            CONFIGURED (LIVE)
✅ Payment Flow:               CORRECTED (Order → PayPal → POS)
✅ Backups:                    MULTIPLE COPIES
✅ Restore Script:             TESTED & WORKING
```

### Last Verified
- **Datum:** 08.01.2026 16:40 UTC
- **Test Results:**
  - Rellingen POS: ✅ Bestellung QT-164012 erfolgreich
  - Henstedt POS: ✅ Bestellung HT-164040 erfolgreich
  - PayPal: ✅ Live credentials confirmed in DB

---

## 📞 Support

Bei Problemen:
1. Überprüfe Status mit Verification Script (Abschnitt 6)
2. Führe Restore Script aus (Abschnitt 5)
3. Teste Verbindungen (Abschnitt 7)
4. Falls alles fehlschlägt: Nutze manuelle Restore Instructions (Abschnitt 5, Option B)

**🔒 DIESES DOKUMENT NIEMALS LÖSCHEN! 🔒**

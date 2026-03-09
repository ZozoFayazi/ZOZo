# 🚨 QUICK RECOVERY GUIDE
## Falls Configs verloren gehen

**Wenn ExpertOrder oder PayPal plötzlich nicht mehr funktioniert:**

---

## 🏃 SCHNELL-ANLEITUNG (2 Minuten)

### Schritt 1: Restore ausführen
```bash
cd /app
python3 restore_all_configs_final.py
```

**Erwartete Ausgabe:**
```
✅ RELLINGEN: PayPal LIVE credentials restored
✅ HENSTEDT: PayPal LIVE credentials restored
✅ RELLINGEN: ExpertOrder POS configuration restored
✅ HENSTEDT: ExpertOrder POS configuration restored
```

---

### Schritt 2: Testen
```bash
cd /app
python3 FINAL_PERSISTENCE_TEST.py
```

**Erwartete Ausgabe:**
```
✅ Passed: 4/4 tests
🟢 ALL SYSTEMS OPERATIONAL & PERSISTENT!
```

---

### Schritt 3: Backend neustarten
```bash
supervisorctl restart backend
```

---

## ✅ FERTIG!

Wenn alle 3 Schritte erfolgreich waren, sind die Configs wiederhergestellt.

---

## 🔍 TROUBLESHOOTING

### Problem: "Backup file not found"

**Lösung:** Manuelle Restore

1. Öffne `/app/CONFIG_LOCKED_FINAL.md`
2. Gehe zu Abschnitt 5 "Restore Instructions"
3. Copy-paste das Python-Script
4. Execute es

---

### Problem: "Database connection failed"

**Lösung:**
```bash
# Check MongoDB
supervisorctl status mongodb

# Falls gestoppt:
supervisorctl start mongodb

# Warte 10 Sekunden
sleep 10

# Retry restore
python3 restore_all_configs_final.py
```

---

### Problem: "Tests schlagen fehl"

**Check 1:** PayPal Credentials
```bash
cd /app
python3 << 'CHECK'
from pymongo import MongoClient
import os

client = MongoClient(os.environ.get('MONGO_URL'))
db = client['zozo_burger']

for loc in db.locations.find({}):
    print(f"{loc['name']}:")
    print(f"  PayPal Client ID: {'SET' if loc.get('paypal_client_id') else 'MISSING'}")
    print(f"  PayPal Secret: {'SET' if loc.get('paypal_secret_key') else 'MISSING'}")
    print(f"  POS API Key: {'SET' if loc.get('pos_config', {}).get('api_key') else 'MISSING'}")
CHECK
```

**Check 2:** ExpertOrder Connection
```bash
curl -H "API_KEY: 4bbc443c82674f93e910399ca7931b37b45e55ba" https://zozo.eocloud.de/api/v1/osp
```

---

## 📞 SUPPORT

Wenn nichts funktioniert:

1. Check alle Backup-Files:
   ```bash
   ls -la /app/*BACKUP*.json /app/*CONFIG*.md
   ```

2. Öffne das neueste Backup und restore manuell

3. Alle Credentials sind auch in `/app/CONFIG_PERSISTENCE_GUARANTEE.md` dokumentiert

---

**Restore dauert max. 2 Minuten! 🚀**

# 🔒 ZOZO Burger - Wichtige Konfigurationsdaten (SICHER AUFBEWAHREN!)

**Erstellt am:** 07.01.2026  
**Status:** PRODUCTION READY - 100% GO-LIVE BEREIT

---

## 🔑 EXPERTORDER POS INTEGRATION

### **Base URL (beide Standorte):**
```
https://zozo.eocloud.de
```

### **API Endpoint:**
```
PUT https://zozo.eocloud.de/api/v1/osp
```

### **Broker Name:**
```
zozo-burger.de
```

---

### **Rellingen:**
- **Location ID:** `49aff347-a6c3-407c-ad4a-59d5d0852314`
- **API Key:** `4bbc443c82674f93e910399ca7931b37b45e55ba`
- **Status:** ✅ LIVE & VERBUNDEN
- **Test Order ID:** `1273C1CF90BF3CEF7D82E7B817EB5881AE267CB3`

### **Henstedt-Ulzburg:**
- **Location ID:** `422cac42-cfdf-4869-b2cb-0b09aa24d02c`
- **API Key:** `90dd43e5c58b7c2a8ddd1eb4916ae8196d8e1073`
- **Status:** ✅ LIVE & VERBUNDEN
- **Test Order ID:** `6C44625F43851586FC95C0409C3B2B9B2A1E93A6`

---

## 👤 ADMIN-ZUGANG

### **Super Administrator:**
- **Email:** admin@zonik-solutions.de
- **Passwort:** Nila1605!
- **Rolle:** Super Admin (alle Rechte)

### **Rellingen Manager:**
- **Email:** info@zozo-burger.de
- **Passwort:** ZozoAdmin2024!
- **Rolle:** Manager (Rellingen-Filiale)

---

## 📍 STANDORT-INFORMATIONEN

### **Rellingen:**
- **Adresse:** Möwenstraße 2, 25462 Rellingen
- **Telefon:** 04101 3984 850
- **Email:** info@zozo-burger.de
- **Öffnungszeiten:** Mo-So 11:00 - 22:45 Uhr

### **Henstedt-Ulzburg:**
- **Adresse:** Edisonstraße 11, Henstedt-Ulzburg
- **Telefon:** 04101 3984 850 (zentral)
- **Email:** info@zozo-burger.de
- **Öffnungszeiten:** Mo-So 11:00 - 22:45 Uhr

---

## 🏢 IMPRESSUM-DATEN

- **Rechtsform:** Einzelunternehmen
- **Inhaber:** Kereschma Fayazi
- **Hauptsitz:** Möwenstraße 2, 25462 Rellingen
- **USt-IdNr:** DE318093819
- **Aufsichtsbehörde:** Gewerbeaufsichtsamt Gemeinde Rellingen

---

## 🎨 WEBSITE-ENTWICKLUNG

- **Entwickler:** Zonik Solutions
- **Ansprechpartner:** Subyr Fayazi
- **Adresse:** Friedrichshulder Weg 157A, 25469 Halstenbek

---

## 🛠️ WIEDERHERSTELLUNG

### **Falls ExpertOrder-Konfiguration verloren geht:**

**Option 1 - Automatisches Script:**
```bash
python3 /app/restore_expertorder_config.py
```

**Option 2 - Manuelle Wiederherstellung:**
```bash
# Siehe Backup-Datei:
cat /app/EXPERTORDER_CONFIG_BACKUP.json
```

**Option 3 - Via Admin-Panel:**
```
1. Login: admin@zonik-solutions.de / Nila1605!
2. Admin → POS-System → ExpertOrder
3. Für Rellingen:
   - API Key: 4bbc443c82674f93e910399ca7931b37b45e55ba
   - Base URL: https://zozo.eocloud.de
   - Speichern
4. Für Henstedt-Ulzburg:
   - API Key: 90dd43e5c58b7c2a8ddd1eb4916ae8196d8e1073
   - Base URL: https://zozo.eocloud.de
   - Speichern
```

---

## 📦 WO SIND DIE DATEN GESPEICHERT?

### **MongoDB Datenbank:**
- **Datenbank:** `test_database`
- **Collection:** `location_settings`
- **Verbindung:** Über MONGO_URL Environment Variable

### **Dateien:**
- `/app/EXPERTORDER_CONFIG_BACKUP.json` - Backup-Konfiguration
- `/app/restore_expertorder_config.py` - Wiederherstellungs-Script
- `/app/backend/expertorder.py` - ExpertOrder Client Code
- `/app/frontend/src/pages/Impressum.jsx` - Impressum-Daten

---

## ✅ PERSISTENZ VERIFIZIEREN

### **Prüfen ob Konfiguration gespeichert ist:**
```bash
python3 << 'EOF'
from pymongo import MongoClient
import os

mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['test_database']

# Beide Standorte prüfen
for name in ['Rellingen', 'Henstedt']:
    loc = db.locations.find_one({'name': {'$regex': name}})
    if loc:
        settings = db.location_settings.find_one({'location_id': loc['id']})
        if settings and settings.get('expertorder_enabled'):
            print(f"✅ {loc['name']}: ExpertOrder AKTIV")
            print(f"   API Key: ***{settings['expertorder_api_key'][-8:]}")
        else:
            print(f"❌ {loc['name']}: Nicht konfiguriert")
EOF
```

---

## 🔒 SICHERHEITSHINWEISE

**WICHTIG - API Keys sind sensible Daten:**

1. ⚠️ Diese Datei enthält **LIVE API Keys**
2. ⚠️ Nicht in öffentliche Repositories hochladen
3. ⚠️ Sicher aufbewahren (z.B. Passwort-Manager)
4. ✅ API Keys können jederzeit im ExpertOrder Dashboard neu generiert werden

**Falls API Keys kompromittiert:**
1. Im ExpertOrder Dashboard neue Keys generieren
2. Dieses Script mit neuen Keys ausführen
3. Backup-Datei aktualisieren

---

## 📞 SUPPORT & NOTFALL

**Bei Problemen:**
1. Prüfen: `tail -f /var/log/supervisor/backend.err.log`
2. MongoDB prüfen: Script oben ausführen
3. Wiederherstellung: `/app/restore_expertorder_config.py`

**ExpertOrder Support:**
- Dashboard: https://zozo.eocloud.de
- Bei API-Problemen: ExpertOrder Kundendienst kontaktieren

---

**Letzte Aktualisierung:** 07.01.2026, 17:45 Uhr  
**Status:** ✅ BEIDE STANDORTE LIVE UND FUNKTIONAL

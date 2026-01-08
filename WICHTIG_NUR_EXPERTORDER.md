# ⚠️ WICHTIG: NUR EXPERTORDER POS AKTIV

## 🎯 Aktuelle Konfiguration

**Datum:** 2026-01-08  
**Status:** ✅ PRODUKTIONSBEREIT

---

## 🏪 POS-System

**Aktives System:** ExpertOrder (EOCloud)  
**Deaktivierte Systeme:** Cash-X (entfernt)

---

## 📍 Standorte

### 1. ZOZO Burger Rellingen
- **Status:** ✅ AKTIV & GETESTET
- **API Key:** `4bbc443c82674f93e910399ca7931b37b45e55ba`
- **Test:** ZOZO-1045 erfolgreich gesendet
- **Base URL:** `https://zozo.eocloud.de`

### 2. ZOZO Burger Henstedt-Ulzburg
- **Status:** ✅ AKTIV
- **API Key:** `90dd43e5c58b7c2a8ddd1eb4916ae8196d8e1073`
- **Base URL:** `https://zozo.eocloud.de`

---

## ✅ Funktionsweise

```
Kunde bestellt
     ↓
ZOZO Backend erstellt Bestellung
     ↓
POS Service erkennt Location
     ↓
ExpertOrder Connector
     ↓
PUT https://zozo.eocloud.de/api/v1/osp
     ↓
Bestellung im ExpertOrder POS
```

---

## 🔧 Technische Details

### API Endpoint
- **URL:** `https://zozo.eocloud.de/api/v1/osp`
- **Methode:** PUT
- **Auth:** API_KEY header
- **Format:** JSON

### Payload
- **Version:** 0
- **Broker:** "zozo-burger.de"
- **Email:** Muss gültig sein (Fallback: noreply@zozo-burger.de)

### Code-Änderungen
- `/app/backend/pos_service.py` - Nur ExpertOrder im Registry
- `/app/backend/pos_connectors/expertorder.py` - Email-Validierung korrigiert

---

## 📋 Konfiguration in Datenbank

**Collection:** `locations`  
**Feld:** `pos_config`

```json
{
  "provider": "expertorder",
  "enabled": true,
  "api_key": "[location-specific]",
  "base_url": "https://zozo.eocloud.de",
  "broker_name": "zozo-burger.de",
  "test_mode": false
}
```

---

## 🚀 Deployment

Diese Konfiguration ist **permanent** und wird beim Deployment beibehalten:

✅ Konfiguration in MongoDB gespeichert  
✅ Keine hardcoded Werte im Code  
✅ Location-spezifische API Keys  
✅ Getestet und funktionsfähig

---

## 🛠️ Restore

Falls die Konfiguration verloren geht:

```bash
cd /app
python setup_final_expertorder_only.py
supervisorctl restart backend
```

---

## ✅ Test

Testbestellung senden:

```bash
cd /app
python test_order_rellingen.py
```

**Erwartetes Ergebnis:**
```
✅ Bestellung erfolgreich erstellt!
🏪 POS (ExpertOrder) Status: pending → sent
```

---

## 📝 Wichtige Dateien

- `/app/setup_final_expertorder_only.py` - Setup-Skript
- `/app/EXPERTORDER_FINAL_CONFIG_BACKUP.json` - Backup
- `/app/test_order_rellingen.py` - Test-Skript
- `/app/WICHTIG_NUR_EXPERTORDER.md` - Diese Datei

---

## ⚠️ KRITISCH

**NUR ExpertOrder verwenden!**

- ❌ Cash-X wurde entfernt
- ❌ Keine anderen POS-Systeme
- ✅ Nur ExpertOrder für beide Standorte

**Bei neuen Bestellungen:**
- Bestellungen werden automatisch an ExpertOrder gesendet
- Keine manuelle Konfiguration nötig
- System verwendet immer die richtige API für jeden Standort

---

**Konfiguriert am:** 08.01.2026  
**Getestet:** ✅ Erfolgreich (ZOZO-1045)  
**Status:** 🔴 LIVE (Production)

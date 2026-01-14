# 🔐 ExpertOrder POS Integration - Setup Anleitung

**Stand:** 07.01.2026  
**Status:** Vorbereitet, Credentials nachzutragen

---

## ✅ WAS BEREITS FUNKTIONIERT:

- ✅ ExpertOrder Connector implementiert und getestet (gestern erfolgreich)
- ✅ Broker Name aktualisiert: **"zozo-burger.de"**
- ✅ Admin-Panel für POS-Verwaltung vorhanden
- ✅ Code für beide Standorte bereit
- ✅ Test-Modus und LIVE-Modus unterstützt

---

## 📋 ZWEI WEGE ZUM EINTRAGEN DER CREDENTIALS:

### **Weg 1: Per Script (Empfohlen - Schneller)**

1. Öffnen Sie: `/app/setup_expertorder_credentials.py`

2. Tragen Sie Ihre Credentials ein:
```python
RELLINGEN_CONFIG = {
    "merchant_id": "IHRE_MERCHANT_ID",  # z.B. "c102285"
    "api_key": "IHR_API_KEY",
    "test_mode": False  # False = LIVE, True = Test
}

HENSTEDT_CONFIG = {
    "merchant_id": "IHRE_MERCHANT_ID",  # Falls anderer Account
    "api_key": "IHR_API_KEY",
    "test_mode": False
}
```

3. Ausführen:
```bash
python3 /app/setup_expertorder_credentials.py
```

4. Das Script zeigt:
```
✅ Rellingen: ExpertOrder konfiguriert (LIVE)
   - Base URL: https://s1.eocloud.de/c102285
   - Broker: zozo-burger.de
   - API Key: ***ABCD

✅ Henstedt-Ulzburg: ExpertOrder konfiguriert (LIVE)
   ...
```

---

### **Weg 2: Über Admin-Panel (Visuell)**

1. Login: https://tastycart-3.preview.emergentagent.com/admin/login
   - Email: `admin@zonik-solutions.de`
   - Passwort: `Nila1605!`

2. Navigation: **Admin Dashboard → POS-System → ExpertOrder**

3. Für jeden Standort:
   - ✏️ **Merchant ID** eintragen
   - ✏️ **API Key** eintragen
   - ☑️ **ExpertOrder aktiviert** anhaken
   - ☑️ **Test-Modus** (für erste Tests empfohlen)
   - 💾 **Speichern**

4. **Test-Bestellung** Button klicken
   - Prüfen ob Bestellung in ExpertOrder Dashboard ankommt

5. Bei Erfolg: Test-Modus deaktivieren → LIVE!

---

## 📊 KONFIGURATIONSDETAILS:

### Für BEIDE Standorte benötigt:

| Feld | Beschreibung | Beispiel |
|------|--------------|----------|
| **Merchant ID** | Ihre ExpertOrder Händler-ID | `c102285` |
| **API Key** | Secret Key für API-Zugriff | `eo_live_abc123...` |
| **Base URL** | Wird automatisch erstellt | `https://s1.eocloud.de/{merchant_id}` |
| **Broker Name** | Bereits gesetzt | `zozo-burger.de` |
| **Test Mode** | Empfohlen für ersten Test | `true` dann `false` |

---

## 🧪 NACH SETUP: TESTBESTELLUNG

### Via Admin-Panel:
1. ExpertOrder Settings öffnen
2. "Test-Bestellung senden" klicken
3. Prüfen: ExpertOrder Dashboard → neue Bestellung?

### Via Website (empfohlen):
1. Als normaler Kunde auf Website gehen
2. Standort wählen (z.B. Rellingen)
3. Produkt in Warenkorb legen
4. Bestellung aufgeben
5. Prüfen:
   - ✅ Bestellung in ZOZO Admin Dashboard sichtbar?
   - ✅ Bestellung in ExpertOrder Dashboard angekommen?
   - ✅ Alle Details korrekt (Produkte, Preis, Kunde)?

---

## ❗ WICHTIGE HINWEISE:

### Bei GLEICHER Merchant ID für beide Standorte:
- Beide Filialen nutzen den gleichen ExpertOrder Account
- Gleiche API Keys für Rellingen & Henstedt-Ulzburg eintragen
- ExpertOrder erkennt anhand der Liefer-Adresse die richtige Filiale

### Bei VERSCHIEDENEN Merchant IDs:
- Jede Filiale hat eigenen ExpertOrder Account
- Verschiedene API Keys eintragen
- Jede Bestellung geht direkt an die richtige Filiale

### Test-Modus vs. LIVE:
- **Test-Modus (true):** Bestellungen werden SIMULIERT (kommen nicht in ExpertOrder an)
- **LIVE (false):** Bestellungen werden ECHT an ExpertOrder gesendet

**Empfehlung:** Erst mit `test_mode: true` testen, dann auf `false` umstellen!

---

## 🔍 TROUBLESHOOTING:

### Bestellung kommt nicht in ExpertOrder an:
1. ✅ Merchant ID korrekt? (keine Leerzeichen)
2. ✅ API Key korrekt kopiert?
3. ✅ ExpertOrder aktiviert? (Checkbox im Admin-Panel)
4. ✅ Test-Modus deaktiviert? (für echte Bestellungen)
5. ✅ Backend Logs prüfen: `tail -f /var/log/supervisor/backend.err.log`

### "401 Unauthorized" Fehler:
- API Key ist falsch oder abgelaufen
- Neue API Keys in ExpertOrder Dashboard generieren

### "404 Not Found" Fehler:
- Merchant ID ist falsch
- Base URL in ExpertOrder Dashboard prüfen

---

## 📞 SUPPORT:

**ExpertOrder Support:**
- Website: https://www.expertorder.de
- Support: Siehe Ihr ExpertOrder Dashboard

**Technischer Support (ZOZO Burger):**
- Backend Logs: `/var/log/supervisor/backend.*.log`
- Admin Dashboard: Bestellstatus prüfen
- POS Fehler-Queue: Admin → POS Fehler-Queue

---

## ✅ CHECKLISTE NACH SETUP:

- [ ] Credentials in Script oder Admin-Panel eingetragen
- [ ] Beide Standorte konfiguriert (Rellingen + Henstedt-Ulzburg)
- [ ] Test-Bestellung erfolgreich gesendet
- [ ] Bestellung in ExpertOrder Dashboard angekommen
- [ ] Test-Modus deaktiviert (auf LIVE umgestellt)
- [ ] Echte Kundenbestellung getestet
- [ ] Alle Produktdetails kommen korrekt an

---

**Nach erfolgreicher Einrichtung: 100% GO-LIVE BEREIT! 🚀**

Broker Name: ✅ `zozo-burger.de` (bereits eingestellt)  
API Integration: ⏳ Credentials nachzutragen  
Code: ✅ Bereit und getestet

# 🚀 ZOZO Burger - GO-LIVE PRE-FLIGHT CHECKLIST

**Mission:** Produktions-Freigabe  
**Datum:** 06.01.2026  
**Status:** ⚠️ **2/4 EXTERNAL ACTIONS PENDING**

---

## ✅ PRE-FLIGHT CHECK (Bereits abgeschlossen)

### RECHTLICHE COMPLIANCE
- [x] Impressum verfügbar unter `/impressum`
- [x] Datenschutzerklärung verfügbar unter `/datenschutz`
- [x] AGB + Widerruf verfügbar unter `/rechtliches`
- [x] Kontaktseite verfügbar unter `/kontakt`
- [x] Footer-Links zu allen Rechtsdokumenten
- [x] Cookie-Banner (3-Button-Lösung, Planet49-konform)
- [x] Google Maps 2-Klick-Lösung (TDDDG §25 erfüllt)

### TECHNISCHE SYSTEME
- [x] POS Retry Mechanismus (4 Auto-Retries, exponential backoff)
- [x] POS Failed Orders Queue (`/admin/pos/failed-orders`)
- [x] POS Failure Alert Email (Auto-Send an `info@zozo-burger.de`)
- [x] JWT Secrets rotiert (86 Zeichen, production-ready)
- [x] Backend Services laufen (supervisorctl status)
- [x] Frontend kompiliert ohne Errors (esbuild check)

---

## ⚠️ EXTERNAL ACTIONS (Du musst diese durchführen)

### 🔴 KRITISCH #1: RESEND DOMAIN VERIFIZIERUNG

**Geschätzter Aufwand:** 30 Min (+ DNS Propagation)

- [ ] **1.1** Gehe zu https://resend.com/domains
- [ ] **1.2** Klicke "Add Domain" → `zozo-burger.de`
- [ ] **1.3** Kopiere die 3 DNS-Records (SPF, DKIM, DMARC)
- [ ] **1.4** Füge Records bei deinem Domain-Provider hinzu
- [ ] **1.5** Warte auf Verifizierung (Resend zeigt "Verified" Badge)
- [ ] **1.6** Screenshot: Resend Dashboard mit "✅ Verified"
- [ ] **1.7** Test-Email senden: `cd /app/backend && python3 test_emails.py`
- [ ] **1.8** Screenshot: Email im Posteingang (Sender: `ZOZO Burger <noreply@zozo-burger.de>`)

**Anleitung:** `/app/RESEND_DOMAIN_SETUP.md`

---

### 🔴 KRITISCH #2: SUPER ADMIN 2FA AKTIVIEREN

**Geschätzter Aufwand:** 10 Min

- [ ] **2.1** Login als Super Admin: `admin@zonik-solutions.de`
- [ ] **2.2** Gehe zu `/admin/security` oder klicke "2FA einrichten" Dialog
- [ ] **2.3** Scanne QR-Code mit Authenticator-App (Google/Authy/Microsoft)
- [ ] **2.4** Gib 6-stelligen Code ein → "Bestätigen"
- [ ] **2.5** **SPEICHERE DIE 10 BACKUP-CODES!** (sicherer Ort, z.B. Passwort-Manager)
- [ ] **2.6** Screenshot: Security Dashboard mit "2FA: ✅ Aktiv" Badge
- [ ] **2.7** Test-Login: Logout → Login → 2FA-Code eingeben → Erfolg

---

### 🟡 WICHTIG #3: ADMIN-PASSWÖRTER ÄNDERN

**Geschätzter Aufwand:** 10 Min (3 Logins)

- [ ] **3.1** Login: `admin@zonik-solutions.de` → Passwort ändern (aktuell: `ZozoAdmin2024!`)
- [ ] **3.2** Login: `info@zozo-burger.de` → Passwort ändern
- [ ] **3.3** Login: `henstedt@zozo-burger.de` → Passwort ändern
- [ ] **3.4** Bestätigung: Alle Passwörter individuell & sicher (12+ Zeichen)
- [ ] **3.5** Check: `must_change_password=false` für alle (via DB oder Login-Test)

**Passwort-Generator:**
```bash
python3 -c "import secrets, string; chars = string.ascii_letters + string.digits + '!@#$%^&*'; print(''.join(secrets.choice(chars) for _ in range(16)))"
```

---

### 🟢 OPTIONAL #4: FINAL SMOKE TEST

**Geschätzter Aufwand:** 5 Min

- [ ] **4.1** Bestellung über öffentliche Website aufgeben (als Gast)
- [ ] **4.2** Bestellbestätigungs-Email erhalten (Sender: `noreply@zozo-burger.de`)
- [ ] **4.3** Admin-Panel: Bestellung sichtbar, Status "confirmed"
- [ ] **4.4** POS Status: "sent" (oder "not_applicable" wenn POS=none)
- [ ] **4.5** Cookie-Banner beim ersten Besuch erscheint
- [ ] **4.6** "Ablehnen" → Google Maps bleiben Placeholder
- [ ] **4.7** Footer-Links funktionieren (Impressum, Datenschutz, AGB)

---

## 🎯 GO-LIVE FREIGABE

**Wenn alle Checkboxen ✅ sind:**

### Final Checklist

- [ ] **Resend Domain:** ✅ Verified
- [ ] **Test-Email:** ✅ Sender korrekt (`noreply@zozo-burger.de`)
- [ ] **Super Admin 2FA:** ✅ Aktiv
- [ ] **Passwörter:** ✅ Alle geändert
- [ ] **Smoke Test:** ✅ Bestellt + Email erhalten

**Dann:** 🚀 **GO-LIVE FREIGEGEBEN**

---

## 📸 DELIVERABLES FÜR FINALE ABNAHME

Bitte liefern:

1. **Screenshot: Resend Domain "Verified"**
2. **Screenshot: Email im Posteingang** (Sender: ZOZO Burger)
3. **Screenshot: Security Dashboard** (2FA aktiv)
4. **Bestätigung:** "Alle Passwörter geändert ✅"

**Optional:**
5. Screenshot: Erfolgreiche Test-Bestellung + Bestätigungs-Email

---

## 🆘 SUPPORT / TROUBLESHOOTING

**Resend Domain funktioniert nicht:**
- Warte länger (DNS Propagation bis 48h)
- Prüfe DNS-Records mit `dig TXT zozo-burger.de`
- Kontakt: Resend Support (support@resend.com)

**2FA-Code funktioniert nicht:**
- Smartphone-Zeit synchronisieren!
- Backup-Code verwenden
- Falls ausgesperrt: Kontakt Neo (DB-Zugriff nötig)

**Passwort vergessen:**
- Aktuell: Kein Self-Service
- Workaround: Super Admin setzt neues Passwort

---

## ⏱️ GESCHÄTZTER ZEITPLAN

| Schritt | Aufwand | Wartezeit |
|---------|---------|-----------|
| Resend DNS Setup | 10 Min | 5-30 Min |
| 2FA Aktivierung | 10 Min | - |
| Passwörter ändern | 10 Min | - |
| Smoke Test | 5 Min | - |
| **TOTAL** | **35 Min** | **~30 Min** |

**Realistische Gesamtdauer:** ~1 Stunde

---

## 🎉 NACH GO-LIVE

**Erste 24 Stunden:**
- [ ] Monitoring: Fehler-Rate prüfen
- [ ] Email-Zustellung: Alle Mails kommen an?
- [ ] POS-Integration: Bestellungen werden übertragen?
- [ ] Failed Orders Queue: Leer? (oder manuelle Retries durchführen)

**Erste Woche:**
- [ ] Kundenfeedback sammeln
- [ ] Analytics prüfen (Cookie-Consent-Rate)
- [ ] Backup-Test durchführen (Mongo Restore)

**Nach 1 Monat:**
- [ ] Security Audit (Audit Logs reviewen)
- [ ] Performance Review (Ladezeiten, API-Response)
- [ ] DSGVO-Prozesse finalisieren (Löschkonzept, AV-Verträge)

---

## ✅ MISSION COMPLETE CRITERIA

**GO-LIVE ist freigegeben wenn:**

1. ✅ Alle Rechtsdokumente live
2. ✅ Cookie-Banner funktioniert
3. ✅ Maps ohne Consent-Verstoß
4. ✅ Resend Domain verified
5. ✅ Super Admin 2FA aktiv
6. ✅ Passwörter geändert
7. ✅ Smoke Test erfolgreich

**DANN:** 🚀 **CLEARED FOR TAKEOFF**

---

*Go-Live Checklist erstellt: 06.01.2026*  
*Agent: Neo*  
*Revision: 1.0*

---

## 🎯 QUICK REFERENCE

**Wichtige Links:**
- Admin Panel: https://tastycart-3.preview.emergentagent.com/admin
- Resend Dashboard: https://resend.com/domains
- Failed POS Orders: https://tastycart-3.preview.emergentagent.com/admin/pos/failed-orders

**Wichtige Credentials:**
- Super Admin: `admin@zonik-solutions.de`
- Resend API Key: (siehe `/app/backend/.env`)
- POS Alert Email: `info@zozo-burger.de`

**Anleitungen:**
- `/app/RESEND_DOMAIN_SETUP.md` - DNS Setup Guide
- `/app/ADMIN_SECURITY_SETUP.md` - 2FA + Passwort Guide
- `/app/GO_LIVE_BLOCKER_ABNAHME.md` - Vollständiger Report

**Support:**
- Agent: Neo (Development Agent)
- Dokumentation: `/app/` Ordner

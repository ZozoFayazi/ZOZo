# ZOZO Burger - Go-Live Checkliste

## Status: IN BEARBEITUNG 🔄

---

## 1. Sicherheit & Zugang (Priorität 1) ✅ GEPRÜFT

### 1.1 Admin Login
- [x] Super Admin (admin@zonik-solutions.de) - Login erfolgreich
- [x] Branch Admin Rellingen (info@zozo-burger.de) - Login erfolgreich
- [x] Branch Admin Henstedt (henstedt@zozo-burger.de) - Login erfolgreich

### 1.2 2FA Pflicht für Super Admin
- [x] `require_2fa_setup: true` bei Super Admin
- [x] 2FA Setup wird nach Passwortänderung erzwungen
- [x] TwoFactorSetup Dialog ist nicht schließbar (forced=true)

### 1.3 mustChangePassword Durchsetzung
- [x] **KRITISCHER FIX ANGEWENDET** (17.12.2025)
  - Geänderte Datei: `/app/frontend/src/components/ProtectedAdminRoute.jsx`
  - Problem: Dialog erschien, war aber nicht blockierend
  - Lösung: `ProtectedAdminRoute` prüft jetzt `mustChangePassword()` und zeigt nicht-schließbaren Dialog
- [x] X-Button versteckt bei `forced=true`
- [x] ESC-Taste blockiert
- [x] Klick außerhalb blockiert
- [x] Kein "Abbrechen" Button

### 1.4 Rate-Limiting
- [x] Admin Login: 3 Versuche → 30 Min Lockout
- [x] Getestet: Nach 3 Fehlversuchen erscheint "Rate-Limit überschritten. Bitte warten Sie 30 Minuten."

---

## 2. Umsatzrelevante Flows (Priorität 2) 🔄 IN PRÜFUNG

### Bestellung aufgeben (Frontend)
- [ ] Bestellung im Warenkorb erstellen
- [ ] Checkout durchführen
- [ ] Bestellung erscheint im Admin

### POS Integration
- [ ] POS-Push im Testmodus erfolgreich
- [ ] Fallback bei POS-Fehler (Bestellung bleibt intern)

---

## 3. Betriebslogik (Priorität 3) - Ausstehend

### Toggle-Funktionen
- [ ] Produkt aktiv/inaktiv
- [ ] Produkt ausverkauft/verfügbar
- [ ] Standort aktiv/inaktiv

---

## 4. Außenwirkung / SEO (Priorität 4) - Ausstehend

### Öffentliche Standortseiten
- [ ] /standorte lädt korrekt
- [ ] /standorte/rellingen lädt korrekt
- [ ] /standorte/henstedt-ulzburg lädt korrekt
- [ ] Meta-Titel & Descriptions korrekt
- [ ] JSON-LD Schema vorhanden
- [ ] Google Maps sichtbar

---

## 5. ExpertOrder POS - Vorbereitung

### Aktueller Status
- [x] Testmodus implementiert und funktional
- [x] Connector-Architektur bereit
- [ ] Live-Modus VORBEREITET (nicht aktiviert)

### Umschalt-Dokumentation
- **Wo umschalten:** Admin → POS-Einstellungen → ExpertOrder
- **Wer darf:** Nur Super Admin
- **Schritte für Live-Schaltung:**
  1. Produktions-Credentials vom POS-Anbieter erhalten
  2. In Admin-Einstellungen hinterlegen
  3. Testmodus deaktivieren
  4. Test-Bestellung durchführen
  5. POS-Log auf Erfolg prüfen

---

## 6. Environment-Konfiguration

### Backend (.env)
- [ ] MONGO_URL - Produktions-DB konfiguriert
- [ ] JWT_SECRET_KEY - Sicherer Key (nicht Default)
- [ ] CORS Origins - Produktions-Domain eingetragen

### Frontend (.env)
- [ ] REACT_APP_BACKEND_URL - Produktions-URL

---

## 7. Datenbank

### Collections (alle vorhanden)
- [x] admins
- [x] locations
- [x] menu_items
- [x] categories
- [x] orders
- [x] audit_logs
- [x] pos_logs
- [x] security_events

---

## 8. Monitoring & Logs

### Logging (implementiert)
- [x] Audit-Logs für Admin-Aktionen
- [x] POS-Logs für Bestellungen
- [x] Security-Events für Rate-Limiting

---

## Bekannte Einschränkungen

| Item | Status | Anmerkung |
|------|--------|-----------|
| SendGrid Email | ❌ Nicht funktional | Ungültiger API-Key aus vorherigem Fork |
| Cash-X POS | ⚠️ Skeleton | Noch keine Spezifikation verfügbar |
| ExpertOrder | ⚠️ Testmodus | Live-Schaltung wartet auf Freigabe |

---

## Kritische Fixes (Go-Live Blocker)

### Fix #1: mustChangePassword Durchsetzung
- **Datum:** 17.12.2025
- **Problem:** `must_change_password` Flag wurde im Login gesetzt, aber der PasswordChangeDialog war nicht blockierend
- **Lösung:** `ProtectedAdminRoute.jsx` wurde erweitert um:
  - Prüfung von `mustChangePassword()` vor Zugriff auf Admin-Bereiche
  - Nicht-schließbaren PasswordChangeDialog (X-Button versteckt, ESC blockiert)
  - Gleiches für 2FA Setup bei Super Admins
- **Geänderte Dateien:**
  - `/app/frontend/src/components/ProtectedAdminRoute.jsx`
  - `/app/frontend/src/components/PasswordChangeDialog.jsx`
  - `/app/frontend/src/components/TwoFactorSetup.jsx`
- **Getestet:** Ja, mit Screenshots dokumentiert

---

## Sign-Off

| Prüfer | Datum | Status |
|--------|-------|--------|
| Entwickler (Neo) | 17.12.2025 | Priorität 1 ✅ |
| QA | | |
| Kunde | | |

---

*Letzte Aktualisierung: 17.12.2025 13:40 UTC*

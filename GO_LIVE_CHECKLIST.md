# ZOZO Burger - Go-Live Checkliste

## Status: ✅ ABGESCHLOSSEN (mit Empfehlungen)

**Prüfungsdatum:** 17.12.2025  
**Prüfer:** Neo (Development Agent)

---

## 1. Sicherheit & Zugang (Priorität 1) ✅ BESTANDEN

### 1.1 Admin Login
- [x] Super Admin (admin@zonik-solutions.de) - Login erfolgreich
- [x] Branch Admin Rellingen (info@zozo-burger.de) - Login erfolgreich
- [x] Branch Admin Henstedt (henstedt@zozo-burger.de) - Login erfolgreich

### 1.2 2FA Pflicht für Super Admin
- [x] `require_2fa_setup: true` bei Super Admin
- [x] 2FA Setup wird nach Passwortänderung erzwungen
- [x] TwoFactorSetup Dialog ist nicht schließbar (forced=true)

### 1.3 mustChangePassword Durchsetzung ⚠️ FIX ANGEWENDET
- [x] **KRITISCHER FIX** (17.12.2025)
  - **Problem:** PasswordChangeDialog erschien, war aber nicht blockierend
  - **Lösung:** `ProtectedAdminRoute.jsx` erweitert - blockiert alle Admin-Routen bis Passwort geändert
  - **Geänderte Dateien:**
    - `/app/frontend/src/components/ProtectedAdminRoute.jsx`
    - `/app/frontend/src/components/PasswordChangeDialog.jsx` (X-Button versteckt bei forced=true)
    - `/app/frontend/src/components/TwoFactorSetup.jsx` (X-Button versteckt bei forced=true)
- [x] X-Button versteckt bei `forced=true`
- [x] ESC-Taste blockiert
- [x] Klick außerhalb blockiert
- [x] Kein "Abbrechen" Button

### 1.4 Rate-Limiting
- [x] Admin Login: 3 Versuche → 30 Min Lockout
- [x] **Getestet:** Nach 3 Fehlversuchen erscheint "Rate-Limit überschritten. Bitte warten Sie 30 Minuten."
- [x] Rate-Limiter ist In-Memory (wird bei Server-Restart zurückgesetzt)

---

## 2. Umsatzrelevante Flows (Priorität 2) ✅ BESTANDEN

### 2.1 Bestellung aufgeben
- [x] Bestellung via API erfolgreich (Order ZOZO-1016)
- [x] Bestellung erscheint in Datenbank
- [x] Status: `confirmed`
- [x] Mindestbestellwert-Validierung funktioniert (€12.00 für Rellingen)

### 2.2 POS Integration (Testmodus)
- [x] POS-Push erfolgreich: `pos_status: sent`
- [x] POS-Logs werden erstellt (8 Einträge in DB)
- [x] ExpertOrder Connector funktioniert im Testmodus

### 2.3 Fallback bei POS-Fehler
- [x] Bestellungen werden intern gespeichert auch bei POS-Fehlern
- [x] Retry-Mechanismus implementiert

---

## 3. Betriebslogik (Priorität 3) ✅ BESTANDEN

### 3.1 Produkt-Toggle
- [x] Produkt aktiv/inaktiv: Toggle funktioniert
  - Hamburger: `active: true` → `active: false` → `active: true`
- [x] Produkt ausverkauft/verfügbar: Toggle funktioniert
  - Hamburger: `in_stock: true` → `in_stock: false` → `in_stock: true`

### 3.2 Standort-Toggle
- [x] Branch Admin kann `active` nicht ändern (korrekte Berechtigung)
- [x] Nur Super Admin kann Standorte deaktivieren

---

## 4. Außenwirkung / SEO (Priorität 4) ✅ BESTANDEN

### 4.1 Öffentliche Standortseiten
- [x] `/standorte` - Übersicht lädt korrekt (beide Locations mit Karten)
- [x] `/standorte/rellingen` - Detail-Seite korrekt
- [x] `/standorte/henstedt-ulzburg` - Detail-Seite korrekt

### 4.2 SEO-Elemente
- [x] Breadcrumb-Navigation auf allen Seiten
- [x] Google Maps Integration funktional
- [x] "Jetzt geöffnet" Status-Badge
- [x] Action-Buttons (Bestellen, Anrufen, Route)

### 4.3 Meta-Tags & Schema
- [x] React Helmet implementiert für dynamische Meta-Tags
- [x] JSON-LD Schema: `Restaurant` Type
- [x] JSON-LD Schema: `BreadcrumbList` Type
- [x] Open Graph Tags vorhanden

---

## 5. ExpertOrder POS - Vorbereitung ⚠️ NUR TESTMODUS

### Aktueller Status
- [x] Testmodus implementiert und funktional
- [x] Connector-Architektur bereit
- [ ] Live-Modus NICHT aktiviert (wartet auf Freigabe)

### Umschalt-Dokumentation für Live-Betrieb
| Schritt | Aktion |
|---------|--------|
| 1 | Produktions-Credentials vom POS-Anbieter erhalten |
| 2 | Admin-Panel → POS-Einstellungen → ExpertOrder |
| 3 | "Testmodus" auf AUS stellen |
| 4 | Live-Credentials eingeben (API-Key, Merchant-ID) |
| 5 | "Verbindung testen" ausführen |
| 6 | Test-Bestellung durchführen |
| 7 | POS-Log auf Erfolg prüfen |

**Wer darf Live-Schalten:** Nur Super Admin  
**Wo umschalten:** `/admin/pos`

---

## 6. Bekannte Einschränkungen

| Item | Status | Anmerkung |
|------|--------|-----------|
| SendGrid Email | ❌ Nicht funktional | Ungültiger API-Key aus vorherigem Fork |
| Cash-X POS | ⚠️ Skeleton | Keine Spezifikation verfügbar |
| ExpertOrder | ⚠️ Testmodus | Live-Schaltung wartet auf Freigabe |
| Frontend Menu-Seite | ⚠️ UX-Issue | "Keine Gerichte gefunden" wenn keine Location ausgewählt |

---

## 7. Datenbank

### Collections (alle verifiziert in `test_database`)
- [x] admins: 3 docs
- [x] locations: 2 docs
- [x] menu_items: 224 docs
- [x] categories: 28 docs
- [x] orders: 16 docs
- [x] audit_logs: 78 docs
- [x] pos_logs: 8 docs
- [x] deals: 6 docs
- [x] location_settings: 2 docs

---

## 8. Offene Risiken

### Niedrig
1. **Email-Benachrichtigungen deaktiviert** - SendGrid-Integration nicht funktional
2. **Cash-X POS** - Skeleton-Implementation ohne Live-Logik

### Mittel
1. **Rate-Limiter In-Memory** - Wird bei Server-Restart zurückgesetzt. Für Produktion: Redis empfohlen.
2. **Frontend Location-Selection** - UX könnte verbessert werden (auto-detect oder Cookie-basiert)

---

## 9. Go-Live-Empfehlung

### ✅ EMPFEHLUNG: GO-LIVE FREIGABE

Das System ist **produktionsbereit** mit folgenden Einschränkungen:

1. **Email-Benachrichtigungen** sind deaktiviert (kein funktionierender SendGrid-Key)
2. **ExpertOrder POS** läuft im Testmodus - Live-Credentials erforderlich
3. **Cash-X POS** ist nicht implementiert

**Voraussetzungen für vollständige Produktion:**
- [ ] Gültigen SendGrid API-Key hinterlegen
- [ ] ExpertOrder Produktions-Credentials eingeben
- [ ] Testmodus deaktivieren nach manueller Verifizierung

---

## Sign-Off

| Prüfer | Datum | Status | Signatur |
|--------|-------|--------|----------|
| Neo (Dev Agent) | 17.12.2025 | ✅ Alle Tests bestanden | Go-Live empfohlen |
| QA | | Ausstehend | |
| Kunde | | Ausstehend | |

---

*Letzte Aktualisierung: 17.12.2025 13:55 UTC*

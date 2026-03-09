# 🚀 ZOZO Burger - Systemumbau Implementierungsplan

## 📋 Übersicht

Vollständige Umstrukturierung zu einem **professionellen, filialfähigen, skalierbaren System** mit serverseitiger Rollenkontrolle, POS-Integration und erweiterten Admin-Features.

---

## 🎯 Ziele

- ✅ Filial-Management als Core Feature
- ✅ Serverseitige Rollen- & Rechteverwaltung
- ✅ POS-Connector-Architektur (Expert Order live, Cash-X vorbereitet)
- ✅ Professionelles Admin-Dashboard
- ✅ Sicherheit (2FA, Audit-Logs, Rate-Limiting)
- ✅ SEO/GEO pro Filiale
- ✅ Skalierbarkeit ohne Umbau

---

## 👥 Admin-Struktur (NEU)

### Neue Admin-Konten:
1. **Super-Admin:** `admin@zonik-solutions.de`
   - Volle Systemrechte
   - Filialverwaltung
   - Rollen & Rechte
   - POS-Integrationen
   - System & Sicherheit

2. **Rellingen Admin:** `info@zozo-burger.de`
   - Produkte hinzufügen/bearbeiten (vollständig)
   - Bilder hochladen/ändern
   - Kategorien/Extras/Varianten anlegen
   - Bestellverwaltung (nur Rellingen)
   - Öffnungszeiten & Aktionen (nur Rellingen)

3. **Henstedt Admin:** `henstedt@zozo-burger.de`
   - Produkte aktiv/inaktiv setzen
   - Produkte ausverkauft/verfügbar setzen
   - Bestellstatus verwalten (nur Henstedt)
   - Keine Produktbearbeitung oder Bildupload

**WICHTIG:** Alte Admin-Logins (`owner@zozo.com`, `rellingen@zozo.com`, `henstedt@zozo.com`) werden NICHT migriert.

---

## 🏗️ Module & Implementierungs-Reihenfolge

### **Modul 1: Authentifizierung & Rollen-System** (P0)

**Backend:**
- ✅ Neues Datenmodell: `Admin` mit Feldern:
  - `email`, `password_hash`, `role` (super_admin, branch_admin, staff)
  - `branch_ids[]` (für branch-spezifische Zuordnung)
  - `permissions{}` (granulare Rechte)
  - `is_active`, `created_at`, `last_login`
  - `totp_secret` (für 2FA, vorerst null)

- ✅ Passwort-Hashing: `bcrypt` verwenden
- ✅ Login-Endpoint: `/api/auth/admin-login`
  - Überprüft E-Mail + Passwort
  - Erstellt Session-Token (JWT vorbereiten)
  - Gibt Rolle, Rechte, zugeordnete Filialen zurück

- ✅ Middleware: `verify_admin_role`
  - Überprüft Rolle serverseitig
  - Überprüft Filialzuordnung bei Branch-spezifischen Requests
  - Blockiert unberechtigte Zugriffe

**Rechte-Definition:**
```python
PERMISSIONS = {
    "super_admin": ["*"],  # Alle Rechte
    "rellingen_admin": [
        "manage_products",  # Vollständiger CRUD
        "upload_images",
        "manage_categories",
        "manage_orders_rellingen",
        "manage_branch_rellingen"
    ],
    "henstedt_admin": [
        "toggle_product_active",  # Nur aktiv/inaktiv
        "toggle_product_stock",   # Nur ausverkauft/verfügbar
        "manage_orders_henstedt"
    ]
}
```

**Frontend:**
- ✅ Neues Login-Formular für Admins
- ✅ Session-Storage für Admin-Daten
- ✅ Route-Guards basierend auf Rolle
- ✅ UI-Elemente bedingt anzeigen basierend auf Rechten

**Tests:**
- Login mit allen 3 Accounts
- Versuch, unautorisierte Aktionen durchzuführen (muss blockieren)
- Serverseitige Validierung testen

**Deliverable:** Screenshot Admin-Login + erfolgreiches Login aller 3 Rollen

---

### **Modul 2: Filial-Management** (P0)

**Backend:**
- ✅ Datenmodell: `Location` erweitern:
  - Bestehende Felder: `name`, `address`, `postal_codes`, `phone`, `email`, `google_review_url`
  - Neue Felder:
    - `delivery_mode`: "radius" | "postal_codes"
    - `delivery_radius_km`: float (wenn radius)
    - `delivery_fee`: float
    - `min_order_value`: float
    - `estimated_delivery_time`: string ("30-45 Min")
    - `is_active`: boolean
    - `opening_hours`: object (Mo-So mit open/close times)
    - `pos_integration`: object (vendor, credentials, status)

- ✅ Endpoints:
  - `GET /api/admin/locations` (Liste aller Filialen)
  - `POST /api/admin/locations` (Neue Filiale anlegen - nur Super-Admin)
  - `PUT /api/admin/locations/{id}` (Filiale bearbeiten - Super-Admin oder zugeordneter Branch-Admin)
  - `DELETE /api/admin/locations/{id}` (Filiale löschen - nur Super-Admin)
  - `PUT /api/admin/locations/{id}/settings` (Liefergebiet, Fees, Zeiten)

- ✅ Migration:
  - Rellingen als erste Filiale in DB eintragen mit allen bestehenden Daten
  - Henstedt-Ulzburg als zweite Filiale anlegen

**Frontend:**
- ✅ Admin-Seite: `/admin/locations`
- ✅ Grid-Layout mit Location-Cards (md:grid-cols-2 lg:grid-cols-3)
- ✅ Jede Card zeigt:
  - Name, Adresse
  - Status-Badge (Aktiv/Inaktiv)
  - Quick Actions: Edit, Deactivate, View Orders
- ✅ Dialog: Add/Edit Location mit Tabs:
  - **Details:** Name, Adresse, Kontakt
  - **Liefergebiet:** 
    - Mode-Switcher (Radius / PLZ-Liste)
    - Radius: Slider + Input
    - PLZ: Command + Badge-Chips mit Remove
  - **Öffnungszeiten:** 
    - Tabelle: Mo-So mit Switch (offen/geschlossen) + Start/End Time-Selects
  - **Liefereinstellungen:**
    - Lieferkosten, Mindestbestellwert, Lieferzeit

**Design:** Gemäß Design Guidelines - Card-Layout, Status-Farben (success/muted), Shadcn Components

**Tests:**
- Filiale hinzufügen (Super-Admin)
- Filiale bearbeiten (Branch-Admin nur eigene, Super-Admin alle)
- Liefergebiet-Konfiguration (Radius und PLZ)
- Öffnungszeiten setzen

**Deliverable:** Screenshots von Locations-Liste + Add/Edit Dialog (alle Tabs)

---

### **Modul 3: Produktrechte-Regeln** (P0)

**Backend:**
- ✅ Produkt-Endpoints erweitern mit Rechteprüfung:
  - `POST /api/admin/products` - Nur Rellingen Admin + Super-Admin
  - `PUT /api/admin/products/{id}` - Nur Rellingen Admin + Super-Admin
  - `DELETE /api/admin/products/{id}` - Nur Rellingen Admin + Super-Admin
  - `PATCH /api/admin/products/{id}/toggle-active` - Alle Admins (nur für ihre Filiale)
  - `PATCH /api/admin/products/{id}/toggle-stock` - Alle Admins (nur für ihre Filiale)

- ✅ Middleware checkt:
  - Rolle des Admins
  - Bei Branch-Admin: Nur Produkte der zugeordneten Filiale(n)

**Frontend:**
- ✅ Menu Management Seite anpassen:
  - Rellingen Admin sieht "Add Product", "Edit", "Delete"
  - Henstedt Admin sieht nur "Active/Inactive Toggle", "In Stock/Out of Stock Toggle"
  - Bedingtes Rendering basierend auf `admin.permissions`

- ✅ Product-Card/Table zeigt Filial-Zuordnung (wenn multi-branch)

**Tests:**
- Rellingen Admin: Produkt hinzufügen/bearbeiten/löschen ✅
- Henstedt Admin: Versuch, Produkt zu bearbeiten ❌ (Blockiert)
- Henstedt Admin: Produkt aktiv/inaktiv setzen ✅

**Deliverable:** Screenshot Menu Management aus Sicht von Rellingen Admin vs. Henstedt Admin

---

### **Modul 4: POS-Connector-Architektur** (P1)

**Backend:**
- ✅ Connector-Interface erstellen: `BasePOSConnector` (abstrakte Klasse)
  - Methoden:
    - `test_connection() -> bool`
    - `push_order(order_data) -> dict`
    - `sync_menu() -> dict` (optional, future)
    - `get_order_status(order_id) -> dict` (optional)

- ✅ Implementierung: `ExpertOrderConnector`
  - Übernimmt bestehende Expert Order Logic
  - Implementiert alle Interface-Methoden
  - Config aus `Location.pos_integration`

- ✅ Vorbereitung: `CashXConnector` (Stub)
  - Dummy-Implementierung mit "Not Implemented" Exceptions
  - Struktur vorbereitet für zukünftige Integration

- ✅ Service: `pos_service.py`
  - Factory-Methode: `get_connector(vendor: str, config: dict) -> BasePOSConnector`
  - Fehlerbehandlung: Bei POS-Fehler -> Bestellung bleibt intern sichtbar

- ✅ Endpoints:
  - `POST /api/admin/locations/{id}/pos/test` - Verbindung testen
  - `POST /api/admin/locations/{id}/pos/sync` - Manuelle Sync
  - `GET /api/admin/locations/{id}/pos/logs` - Sync-Logs anzeigen

**Frontend:**
- ✅ Admin-Seite: `/admin/integrations`
- ✅ POS-Settings pro Filiale:
  - Vendor-Select (Expert Order, Cash-X)
  - Environment-Toggle (Test/Live) mit Warning
  - Credentials-Card (Host, Merchant ID, Username, Secret)
    - Secret maskiert: `••••••••` mit "Reveal" Button (öffnet Confirm-Dialog)
  - Connection Status Chip (Grün=OK, Rot=Error, Gelb=Nicht konfiguriert)
  - Test-Connection Button
  - Sync-Logs Tabelle (Zeit, Aktion, Status, Details)

**Sicherheit:**
- Secrets nur Backend-seitig speichern (verschlüsselt mit Fernet oder ähnlich)
- Reveal/Copy-Aktionen loggen in Audit-Log
- Nur Super-Admin kann Secrets ändern

**Tests:**
- Expert Order Connector testen (mit Test-Credentials)
- Connection-Status korrekt anzeigen
- Bestellung an POS senden (Happy Path)
- Fehlerfall simulieren (POS offline) -> Bestellung bleibt im System

**Deliverable:** Screenshots von POS Settings-Seite + Test-Connection Erfolg/Fehler

---

### **Modul 5: SEO & GEO pro Filiale** (P2)

**Backend:**
- ✅ Endpoint: `GET /api/locations/{slug}/seo` - Liefert SEO-Daten
  - Name, Adresse, Öffnungszeiten, Bewertungen, Kontakt

**Frontend:**
- ✅ Standort-Seiten anpassen:
  - `/locations/rellingen`
  - `/locations/henstedt-ulzburg`

- ✅ SEO-Optimierungen:
  - LocalBusiness Schema.org JSON-LD
  - Meta-Tags (Title, Description, OG-Tags)
  - Öffnungszeiten strukturiert
  - Google Maps Embed
  - Review-Link prominent

- ✅ Sitemap aktualisieren:
  - Automatisch alle aktiven Filialen einbinden

**Tests:**
- SEO-Checker (Google Rich Results Test)
- Mobile-Friendly Test
- Standort-Seiten laden korrekt

**Deliverable:** Screenshot Standort-Seiten + Schema Markup Validation

---

### **Modul 6: Sicherheit & Monitoring** (P1)

**Backend:**
- ✅ Audit-Log System:
  - Datenmodell: `AuditLog`
    - `timestamp`, `actor_email`, `action`, `target`, `result`, `ip_address`, `details`
  - Endpoint: `GET /api/admin/audit-logs` (filterable)
  - Loggen:
    - Admin-Login/Logout
    - Produkt-Änderungen
    - Filial-Änderungen
    - POS-Aktionen (Test, Sync)
    - Rechte-Änderungen

- ✅ Rate-Limiting:
  - Login-Endpoint: 5 Versuche / 15 Minuten
  - Order-Endpoint: 10 Bestellungen / Stunde pro IP
  - Admin-Endpoints: 100 Requests / Minute

- ✅ Backups (Vorbereitung):
  - Script für MongoDB-Backup
  - Cronjob-Setup (täglich)
  - Restore-Prozedur dokumentieren

**Frontend:**
- ✅ Admin-Seite: `/admin/security`
- ✅ Tabs: Audit-Logs | Rate-Limiting | Backups

- ✅ **Audit-Logs:**
  - Filter-Leiste: Date Range (Calendar), Actor (Input), Action (Select), Result (Select)
  - Tabelle: Timestamp | Actor | Action | Target | Result | Details (Expand)
  - Export-Button (CSV)

- ✅ **Rate-Limiting:**
  - KPI-Cards: Total Requests Today, Throttled, Top IPs
  - Policy-Liste (Tabelle): Scope | Limit | Window | Status
  - Edit-Dialog für Policies

- ✅ **Backups:**
  - Cards: Last Backup Time, Size, Retention Policy
  - Buttons: Run Backup Now, Restore (mit Confirm)

**Tests:**
- Audit-Log Eintrag erstellen (beliebige Admin-Aktion) und filtern
- Rate-Limit testen (zu viele Login-Versuche)
- Backup manuell ausführen

**Deliverable:** Screenshots Security-Dashboard (alle 3 Tabs)

---

### **Modul 7: 2FA (TOTP)** (P1)

**Backend:**
- ✅ Library: `pyotp` installieren
- ✅ Admin-Modell erweitern: `totp_secret`, `totp_enabled`, `backup_codes[]`
- ✅ Endpoints:
  - `POST /api/admin/2fa/setup` - Generiert Secret + QR-Code
  - `POST /api/admin/2fa/verify` - Verifiziert 6-Digit Code
  - `POST /api/admin/2fa/disable` - Deaktiviert 2FA (mit Passwort-Bestätigung)
  - `GET /api/admin/2fa/backup-codes` - Generiert Backup-Codes (einmalig)

- ✅ Login-Flow anpassen:
  - Nach Passwort-Check: Wenn `totp_enabled` -> fordere TOTP-Code
  - Backup-Code-Option

**Frontend:**
- ✅ Admin-Profil: `/admin/profile` mit 2FA-Sektion
- ✅ 2FA-Setup-Wizard (Dialog mit Steps):
  - Step 1: Info + "Enable 2FA" Button
  - Step 2: QR-Code scannen + Secret anzeigen (copy)
  - Step 3: 6-Digit Verifizierungscode eingeben
  - Step 4: Backup-Codes anzeigen + Download

- ✅ Login-Seite:
  - Zusätzliches Feld für TOTP-Code (wenn aktiviert)
  - "Use Backup Code" Link

**Tests:**
- 2FA aktivieren mit Google Authenticator
- Login mit TOTP-Code
- Login mit Backup-Code
- 2FA deaktivieren

**Deliverable:** Screenshots 2FA-Setup + Login mit TOTP

---

## 📊 Dashboard-Erweiterungen (Parallel)

### Dashboard-Startseite neu gestalten:

**Komponenten:**
- ✅ Filial-Switcher (nur Super-Admin) - Select-Dropdown oben rechts
- ✅ KPI-Cards (4-Spalten-Grid):
  - Heute: Bestellungen, Umsatz
  - Woche: Bestellungen, Umsatz
  - Monat: Bestellungen, Umsatz
  - Offene Bestellungen
- ✅ Live-Bestellungen Stream (ScrollArea mit Auto-Refresh)
- ✅ Umsatz-Chart (Recharts Area) - Letzte 7 Tage oder 30 Tage

**Design:** Gemäß Design Guidelines - Cards mit border, Status-Farben, Recharts mit dezenten Gradients

---

## 🗄️ Datenmigration

**Schritte:**
1. ✅ Rellingen als erste Filiale in `locations` Collection anlegen
   - Alle bestehenden Daten zuordnen (Produkte, Bestellungen)
2. ✅ Henstedt-Ulzburg als zweite Filiale anlegen
   - Produkte von Rellingen kopieren (gleiche Menü-Basis)
3. ✅ Neue Admin-Konten erstellen:
   - Super-Admin: `admin@zonik-solutions.de`
   - Rellingen: `info@zozo-burger.de`
   - Henstedt: `henstedt@zozo-burger.de`
4. ✅ Bestehende Bestellungen Rellingen zuordnen
5. ✅ Loyalty-Accounts, Custom Burgers, Group Orders behalten (keine Filialzuordnung nötig)

**WICHTIG:** Kein Datenverlust! Alle existierenden Daten müssen erhalten bleiben.

---

## 🧪 Testing-Strategie

**Nach jedem Modul:**
1. Backend-Endpoints mit `curl` testen
2. Frontend UI manuell testen (Happy Path + Fehlerfall)
3. Screenshot erstellen und dokumentieren
4. Rollen-basierte Tests (alle 3 Admin-Accounts)

**Finale Tests:**
- Kompletter User-Flow: Produkt hinzufügen (Rellingen) → Bestellung aufgeben → POS-Sync → Status ändern
- Sicherheitstests: Unautorisierte Zugriffe, Rate-Limits
- Performance: Dashboard-Ladezeit, Tabellen mit vielen Einträgen

---

## 📦 Technische Ergänzungen

### Neue Dependencies:

**Backend:**
```
bcrypt==4.1.2
pyotp==2.9.0
cryptography==42.0.0  # Für Secret-Verschlüsselung
slowapi==0.1.9  # Rate-Limiting
```

**Frontend:**
```
recharts (bereits vorhanden)
framer-motion (bereits vorhanden)
```

### CSS-Updates:
- ✅ Status-Token in `index.css` hinzufügen:
  - `--success`, `--warning`, `--info`
  - Utility-Classes: `.text-success`, `.bg-success-soft`, etc.

---

## 📝 Dokumentation

**Erstellen:**
- ✅ `ADMIN_GUIDE.md` - Anleitung für alle Admin-Funktionen
- ✅ `API_DOCS.md` - Alle neuen Endpoints dokumentieren
- ✅ `POS_INTEGRATION.md` - Anleitung für neue POS-Connectors

---

## ⏱️ Geschätzte Umsetzungszeit

- **Modul 1:** 1-1.5h (Rollen & Rechte)
- **Modul 2:** 1.5-2h (Filial-Management)
- **Modul 3:** 0.5-1h (Produktrechte)
- **Modul 4:** 2-2.5h (POS-Connector)
- **Modul 5:** 1h (SEO/GEO)
- **Modul 6:** 1.5-2h (Sicherheit)
- **Modul 7:** 1-1.5h (2FA)
- **Dashboard:** 1h (parallel)

**Gesamt:** ~10-13 Stunden (mit Tests, Screenshots, Dokumentation)

---

## ✅ Erfolgs-Kriterien

- [ ] Alle 3 Admin-Rollen funktionieren korrekt mit serverseitiger Validierung
- [ ] Neue Filialen können ohne Code-Änderung hinzugefügt werden
- [ ] POS-Integration funktioniert (Expert Order) und ist erweiterbar (Cash-X vorbereitet)
- [ ] Audit-Logs erfassen alle kritischen Aktionen
- [ ] 2FA schützt Admin-Logins
- [ ] SEO/Schema pro Filiale korrekt implementiert
- [ ] Alle Features mit Screenshots dokumentiert
- [ ] Keine Datenverluste bei Migration

---

## 🚀 Start-Kommando

Nach Bestätigung dieses Plans beginne ich mit **Modul 1: Authentifizierung & Rollen-System**.

**Liefere nach jedem Modul:**
1. Kurze Statusmeldung
2. Screenshots aller neuen UI-Elemente
3. Kurze Test-Zusammenfassung

**User-Feedback:** Nach jedem Modul warten auf Freigabe für das nächste Modul.

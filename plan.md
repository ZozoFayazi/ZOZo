# ZOZO Burger - Multi-Location Admin System

## Projekt-Übersicht
ZOZO Burger Multi-Standort Admin-System mit FastAPI Backend, React Frontend und MongoDB. 
Umfassende Architektur-Überarbeitung für professionelles Multi-Tenant-System.

---

## Modul 1: Rollen- & Rechte-System (Status: COMPLETED) ✅
**Ziel:** JWT-basiertes Auth-System mit rollenspezifischen Berechtigungen

### Umgesetzte Features:
- ✅ AdminUser Model mit gehashten Passwörtern (bcrypt)
- ✅ JWT-Token-Authentifizierung für Admin-Bereich
- ✅ 3 Admin-Rollen: Super Admin, Rellingen Admin, Henstedt Admin
- ✅ Server-seitige Berechtigungsprüfung auf allen Endpunkten
- ✅ AdminAuthContext für Frontend-Session-Management
- ✅ Protected Routes für Admin-Seiten

### Admin-Accounts:
- `admin@zonik-solutions.de` (Super Admin) - Voller Systemzugriff
- `info@zozo-burger.de` (Rellingen) - Volle Produkt-Berechtigungen
- `henstedt@zozo-burger.de` (Henstedt) - Nur Active/InStock Toggle

---

## Modul 2: Filial- & Standort-Management (Status: COMPLETED) ✅
**Ziel:** Verwaltung mehrerer Standorte mit eigenen Einstellungen

### Umgesetzte Features:
- ✅ Location Model mit Adresse, Öffnungszeiten, Liefergebieten, SEO
- ✅ CRUD-Endpoints für Locations mit Rollen-Prüfung
- ✅ Super Admin: Alle Standorte verwalten
- ✅ Branch Admin: Nur eigenen Standort bearbeiten (eingeschränkte Felder)
- ✅ LocationDialog mit Tabs (Details, Öffnungszeiten, Liefergebiet, SEO)
- ✅ Collapsible Left Sidebar Navigation

---

## Modul 3: Produktverwaltung (Status: COMPLETED) ✅
**Ziel:** Rollen-basiertes Produkt-CRUD

### Umgesetzte Features:
- ✅ Produkt-Endpoints mit strengen Berechtigungen
- ✅ Super/Rellingen Admin: Volles CRUD (Create, Edit, Delete)
- ✅ Henstedt Admin: Nur Active/InStock Toggle
- ✅ Bildupload-Funktionalität
- ✅ Kategorie-Management
- ✅ ProductDialog für Create/Edit

---

## Modul 4: POS-Connector Architektur (Status: COMPLETED) ✅
**Ziel:** Plug-and-Play POS-Integration pro Standort

### Umgesetzte Features:

#### Backend:
- ✅ `pos_models.py` - Pydantic Models für POS-Konfiguration
- ✅ `pos_connectors/base.py` - Abstract Interface für POS-Connectors
- ✅ `pos_connectors/expertorder.py` - Vollständiger ExpertOrder-Connector mit Testmodus
- ✅ `pos_connectors/cashx.py` - Cash-X Skeleton für zukünftige Integration
- ✅ `pos_service.py` - Service-Schicht mit Factory Pattern

#### Endpoints:
- ✅ `GET /api/admin/pos/providers` - Liste verfügbarer POS-Provider
- ✅ `GET /api/admin/locations/{slug}/pos/config` - POS-Config abrufen (Secrets maskiert)
- ✅ `PUT /api/admin/locations/{slug}/pos/config` - POS-Config aktualisieren
- ✅ `POST /api/admin/locations/{slug}/pos/test` - Verbindungstest (mit simulate_failure Option)
- ✅ `GET /api/admin/locations/{slug}/pos/logs` - POS-Protokoll
- ✅ `POST /api/admin/orders/{order_id}/pos/retry` - Bestellung erneut an POS senden

#### POS-Konfiguration pro Filiale:
- ✅ Provider: NONE / EXPERTORDER / CASHX
- ✅ Status: connected / disconnected / error
- ✅ Credentials (verschlüsselt in DB, nur has_* Flags im Frontend)
- ✅ last_sync_at, last_error, last_error_at
- ✅ **Testmodus-Toggle** (verbindlich)

#### Test-Modus:
- ✅ Simuliert Connected / Disconnected / Error
- ✅ Simuliert Order-Push (Success + Failure)
- ✅ Strukturiertes Logging ohne Secrets
- ✅ Klarer "[TESTMODUS]" Prefix in allen Nachrichten

#### Berechtigungen:
- ✅ Super Admin: POS für alle Filialen konfigurieren
- ✅ Branch Admin: POS nur für eigene Filiale
- ✅ Henstedt sieht nur Henstedt-Standort

#### Bestellfluss + Fallback:
- ✅ Automatischer POS-Push bei Bestellungseingang
- ✅ pos_status in Order: pending → sent / error
- ✅ pos_order_id bei Erfolg gespeichert
- ✅ Retry-Button für fehlerhafte Bestellungen

#### Frontend UI:
- ✅ `POSSettings.jsx` - Vollständige Admin-Seite
- ✅ Standort-Auswahl Dropdown
- ✅ POS-Konfiguration Card mit Status-Badge
- ✅ Credentials-Anzeige (nur ob gesetzt, nie der Wert)
- ✅ Letzte Synchronisation & Fehler-Anzeige
- ✅ "Konfigurieren" Dialog mit Provider-Auswahl
- ✅ "Verbindung testen" Button
- ✅ "Fehler simulieren" Button (nur im Testmodus)
- ✅ POS-Protokoll mit Scroll-Area
- ✅ Test-Ergebnis Dialog

---

## Modul 5: SEO & GEO (Status: NOT STARTED) 📋
**Ziel:** Individuelle, indexierbare Standort-Seiten

### Geplante Features:
- Automatisch generierte Location-Seiten
- LocalBusiness Schema Markup
- Geo-spezifische Meta-Tags
- Sitemap-Integration

---

## Modul 6: Sicherheit (Status: NOT STARTED) 📋
**Ziel:** Professionelle Sicherheitsmaßnahmen

### Geplante Features:
- Rate-Limiting für API-Endpoints
- Umfassende Audit-Logs
- mustChangePassword Flag in UI
- Session-Management

---

## Modul 7: 2FA-Integration (Status: NOT STARTED) 📋
**Ziel:** TOTP-basierte Zwei-Faktor-Authentifizierung

### Geplante Features:
- Google Authenticator Kompatibilität
- Backup-Codes
- 2FA-Setup-Wizard

---

## Technischer Stack
- **Backend**: FastAPI, Motor, Pydantic, JWT Auth, bcrypt
- **Frontend**: React, Vite, Shadcn/UI, Sonner (Toasts), Lucide Icons
- **Database**: MongoDB (Motor)
- **POS**: ExpertOrder (aktiv), Cash-X (vorbereitet)

## Design-Richtlinien
- **Farben**: Primary Red #B00020, Card BG #121214, Border #232326
- **Status**: Success (grün), Warning (orange), Error (rot), Info (blau)
- **Typografie**: Playfair Display (Headings), Chivo (Body)
- **Alle interaktiven Elemente mit `data-testid`**

## Admin-Credentials (Test)
- Super Admin: `admin@zonik-solutions.de` / `ZozoAdmin2024!`
- Rellingen: `info@zozo-burger.de` / `ZozoAdmin2024!`
- Henstedt: `henstedt@zozo-burger.de` / `ZozoAdmin2024!`

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

## Modul 4: POS-Connector Architektur (Status: IN PROGRESS) 🔄
**Ziel:** Plug-and-Play POS-Integration pro Standort

### Anforderungen:
1. **POS-Konfiguration pro Filiale:**
   - Provider: NONE / EXPERTORDER / CASHX
   - Status: connected / disconnected / error
   - Verschlüsselte Credentials
   - lastSyncAt, lastError
   - settingsJson (Mapping, Steuern, Zahlungsarten)
   - **Testmodus-Toggle**

2. **Berechtigungen:**
   - Super Admin: POS für alle Filialen konfigurieren
   - Branch Admin: POS nur für eigene Filiale
   - Henstedt sieht nur Henstedt

3. **Bestellfluss + Fallback:**
   - Wenn POS aktiv: Bestellung pushen
   - Wenn Push fehlschlägt: Status "POS Fehler", manuell bearbeitbar
   - Retry-Button für erneuten Versuch

4. **Test-Modus (VERBINDLICH):**
   - Simuliert Connected/Disconnected/Error
   - Simuliert Order-Push (Success + Failure)
   - Strukturiertes Logging (ohne Secrets)
   - Klarer Toggle "Testmodus" pro Filiale

### Implementierungsschritte:
- [ ] Backend: POS-Config Modelle erweitern
- [ ] Backend: ExpertOrder Connector mit Test-Modus
- [ ] Backend: POS-Endpoints erweitern (Config CRUD, Test, Retry)
- [ ] Backend: Order-Flow mit POS-Integration + Fallback
- [ ] Frontend: POSSettings.jsx Seite erstellen
- [ ] Frontend: POS-Config Dialog pro Standort
- [ ] Frontend: Connection Test UI
- [ ] Frontend: Order Retry Funktionalität
- [ ] Testing: Alle 3 Admin-Rollen testen
- [ ] Screenshots: Dokumentation

### Technische Details:
- **Backend-Dateien:**
  - `/app/backend/pos_connectors/base.py` - Interface
  - `/app/backend/pos_connectors/expertorder.py` - ExpertOrder
  - `/app/backend/pos_connectors/cashx.py` - Cash-X Skeleton
  - `/app/backend/pos_service.py` - Service-Schicht
  
- **Frontend-Dateien:**
  - `/app/frontend/src/pages/POSSettings.jsx` - NEU
  - `/app/frontend/src/components/POSConfigDialog.jsx` - NEU

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

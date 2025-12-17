# ZOZO Burger - Multi-Location Admin System

## Projekt-Übersicht
ZOZO Burger Multi-Standort Admin-System mit FastAPI Backend, React Frontend und MongoDB. 
Umfassende Architektur-Überarbeitung für professionelles Multi-Tenant-System.

---

## Modul 1: Rollen- & Rechte-System (Status: COMPLETED) ✅
- JWT-Token-Authentifizierung für Admin-Bereich
- 3 Admin-Rollen: Super Admin, Rellingen Admin, Henstedt Admin
- Server-seitige Berechtigungsprüfung

---

## Modul 2: Filial- & Standort-Management (Status: COMPLETED) ✅
- CRUD für Locations mit Rollen-Prüfung
- LocationDialog mit Tabs (Details, Öffnungszeiten, Liefergebiet, SEO)

---

## Modul 3: Produktverwaltung (Status: COMPLETED) ✅
- Rollen-basiertes Produkt-CRUD
- Bildupload & Kategorie-Management

---

## Modul 4: POS-Connector Architektur (Status: COMPLETED) ✅
- ExpertOrder mit vollständigem Testmodus
- Automatischer POS-Push bei Bestellungen
- Retry-Funktion & POS-Protokoll

---

## Modul 5: SEO & GEO (Status: COMPLETED) ✅
- Öffentliche Standort-Seiten (/standorte/*)
- JSON-LD Schema (Restaurant, BreadcrumbList)
- Meta Tags, Open Graph, Geo Tags

---

## Modul 6: Sicherheit (Status: COMPLETED) ✅
**Ziel:** Professionelle Sicherheitsmaßnahmen für Go-Live

### Umgesetzte Features:

#### Rate-Limiting (`rate_limiter.py`):
- ✅ **Admin Login**: 3 Versuche pro 15 Minuten, 30 Min Lockout
- ✅ **Bestellungen**: 10 pro Stunde pro IP
- ✅ **API General**: 100 Requests pro Minute
- ✅ **POS Tests**: 10 pro 5 Minuten
- ✅ In-Memory Cache mit automatischer Bereinigung
- ✅ IP-Erkennung (X-Forwarded-For, X-Real-IP)
- ✅ Deutschsprachige Fehlermeldungen

#### Erweitertes Audit-Logging (`audit_service.py`):
- ✅ **Kategorien**: auth, admin, product, location, order, pos, security, system
- ✅ **Schweregrade**: low, medium, high, critical
- ✅ **Auto-Kategorisierung** basierend auf Action-Namen
- ✅ **Security-Summary** Endpoint (24h Übersicht)
- ✅ **Filterbare Logs** (Kategorie, Ergebnis, Schweregrad, Aktion)
- ✅ IP-Adresse wird protokolliert

#### Audit-Actions:
- `login_success`, `login_failed`
- `password_changed`
- `pos_config_updated`, `pos_connection_tested`, `pos_order_pushed`
- `product_created/updated/deleted`
- `location_created/updated/deleted`
- `rate_limit_exceeded`

#### Backend-Endpoints:
- ✅ `GET /api/admin/security/audit-logs` - Filterbare Audit-Logs
- ✅ `GET /api/admin/security/summary` - Security-Übersicht (24h)
- ✅ `GET /api/admin/security/rate-limit-status` - Rate-Limit Status
- ✅ `POST /api/admin/security/change-password` - Passwort ändern

#### Frontend - Security Dashboard:
- ✅ **Übersichtskarten**: Fehlgeschlagene Logins, Rate-Limit Events, Kritische Ereignisse, Gesamt-Logs
- ✅ **Kritische Ereignisse Box** (rot hervorgehoben)
- ✅ **Audit-Protokoll** mit Filtern
- ✅ **Pagination** für große Log-Mengen
- ✅ **Severity Badges** (KRITISCH, HOCH, MITTEL, NIEDRIG)
- ✅ **Category Badges** (AUTH, SECURITY, POS, etc.)
- ✅ Nur für Super Admin zugänglich

#### Password-Change Dialog:
- ✅ `PasswordChangeDialog.jsx` Komponente
- ✅ Passwort-Anforderungen (8+ Zeichen, Groß/Klein, Zahlen, Sonderzeichen)
- ✅ Live-Validierung mit Checkmarks
- ✅ Unterstützt "forced" Modus für mustChangePassword

#### Zusätzliche Sicherheitsmaßnahmen:
- ✅ Rate-Limit auf Admin-Login integriert
- ✅ IP-Adresse bei Login erfasst
- ✅ Erfolgreicher Login setzt Rate-Limit zurück
- ✅ mustChangePassword Flag vorhanden

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
- **Frontend**: React, Vite, Shadcn/UI, Sonner, Lucide Icons, react-helmet
- **Database**: MongoDB (Motor)

## Admin-Credentials (Test)
- Super Admin: `admin@zonik-solutions.de` / `ZozoAdmin2024!`
- Rellingen: `info@zozo-burger.de` / `ZozoAdmin2024!`
- Henstedt: `henstedt@zozo-burger.de` / `ZozoAdmin2024!`

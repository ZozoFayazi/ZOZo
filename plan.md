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
**Ziel:** Individuelle, indexierbare Standort-Seiten

### Umgesetzte Features:

#### SEO-optimierte URLs:
- ✅ `/standorte` - Übersichtsseite aller Standorte
- ✅ `/standorte/rellingen` - Rellingen Detail-Seite
- ✅ `/standorte/henstedt-ulzburg` - Henstedt-Ulzburg Detail-Seite

#### Backend:
- ✅ `GET /api/locations/{slug}` - Öffentlicher Location-Detail-Endpoint
- ✅ SEO-Daten mit intelligenten Defaults (meta_title, meta_description, keywords)
- ✅ Formatierte Öffnungszeiten für alle 7 Wochentage
- ✅ Lieferinformationen (Mindestbestellwert, Gebühren, Lieferzeit, PLZ)
- ✅ Opening-Status (Jetzt geöffnet/Geschlossen)

#### Frontend - LocationDetailPage.jsx:
- ✅ **Google Maps Embed** mit Standort-Marker
- ✅ **Breadcrumb Navigation** (Start > Standorte > [Standort])
- ✅ Status-Badge: "Jetzt geöffnet" / "Geschlossen"
- ✅ CTAs: "Jetzt bestellen", "Anrufen", "Route"
- ✅ Öffnungszeiten-Tabelle (alle 7 Tage)
- ✅ Lieferinformationen (Mindestbestellwert, Liefergebühr, Lieferzeit)
- ✅ Kontakt-Card (Adresse, Telefon, Email)
- ✅ CTA-Box: "Hunger? Jetzt bestellen"

#### JSON-LD Structured Data:
- ✅ **Restaurant Schema** mit:
  - Name, Description, URL, Telefon, Email
  - PostalAddress (Straße, Stadt, PLZ, Land)
  - GeoCoordinates (Latitude, Longitude)
  - openingHoursSpecification (pro Wochentag)
  - servesCuisine (Burger, Pizza, Pasta)
  - priceRange, paymentAccepted
  - aggregateRating
  - areaServed mit GeoCircle
  - hasMenu mit MenuSections
  
- ✅ **BreadcrumbList Schema** für Navigation

#### Meta Tags (SEO):
- ✅ `<title>` - Dynamisch pro Standort
- ✅ `<meta name="description">` - Standort-spezifisch
- ✅ `<meta name="keywords">` - Lokale Keywords
- ✅ `<link rel="canonical">` - Kanonische URL
- ✅ **Open Graph Tags** (og:title, og:description, og:type, og:url, og:image)
- ✅ **Twitter Cards** (summary_large_image)
- ✅ **Geo Tags** (geo.region, geo.placename, geo.position, ICBM)

#### LocationsPage (Übersicht) Erweiterungen:
- ✅ "Mehr Info" Button zu jeder Location
- ✅ JSON-LD Schema für FoodEstablishment mit departments
- ✅ SEO Meta Tags

---

## Modul 6: Sicherheit (Status: NOT STARTED) 📋
- Rate-Limiting für API-Endpoints
- Umfassende Audit-Logs
- mustChangePassword Flag in UI

---

## Modul 7: 2FA-Integration (Status: NOT STARTED) 📋
- TOTP-basierte Zwei-Faktor-Authentifizierung

---

## Technischer Stack
- **Backend**: FastAPI, Motor, Pydantic, JWT Auth, bcrypt
- **Frontend**: React, Vite, Shadcn/UI, Sonner, Lucide Icons, **react-helmet**
- **Database**: MongoDB (Motor)

## Admin-Credentials (Test)
- Super Admin: `admin@zonik-solutions.de` / `ZozoAdmin2024!`
- Rellingen: `info@zozo-burger.de` / `ZozoAdmin2024!`
- Henstedt: `henstedt@zozo-burger.de` / `ZozoAdmin2024!`

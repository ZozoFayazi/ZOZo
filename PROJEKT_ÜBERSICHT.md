# 🍔 ZOZO Burger - Vollständige Projekt-Übersicht

## 📋 Projekt-Beschreibung
Eine hochmoderne, vollständig funktionale E-Commerce-Website für den Burger-Lieferservice ZOZO Burger mit zwei Filialen in Schleswig-Holstein (Rellingen & Henstedt-Ulzburg). Die Website verfügt über ein eigenes Bestellsystem, umfassendes Admin-Dashboard und zahlreiche innovative Features.

---

## 🎨 Design & UI/UX

### Design-Philosophie
- **Dark Theme:** Dunkler, premium Hintergrund mit hochwertigen Food-Visuals
- **Moderne Ästhetik:** Hochwertige Typografie, performante Animationen, Glasmorphismus-Effekte
- **Mobile-First:** Vollständig responsive mit spezifischer mobiler Navigation
- **Accessibility (A11y):** WCAG-konform mit Skip-Links, ARIA-Labels, Focus-States

### UI-Komponenten
- Shadcn/UI Komponentenbibliothek vollständig integriert
- Lucide-React Icons durchgängig verwendet
- Custom-Animationen & Micro-Interactions auf allen Seiten
- Featured Products Carousel mit Embla-Carousel
- Mobile Bottom Navigation Bar
- Toast-Benachrichtigungen (Sonner)

---

## 🎯 Core Features (Hauptfunktionen)

### 1. **Online-Bestellsystem**
**Status:** ✅ Vollständig implementiert

- **Menü-Anzeige:** Kategorisierte Produkte (Burger, Sides, Getränke, Desserts)
- **Warenkorb-System:** 
  - Produkte hinzufügen/entfernen
  - Mengenänderung
  - Persistierung im localStorage
  - Echtzeit-Preisberechnung
- **Checkout-Flow:**
  - E-Mail-Eingabe & Verifizierung
  - Postleitzahl-basierte Filialzuordnung
  - Lieferadresse oder Abholung
  - Zahlungsmethoden (Bar, Karte, PayPal)
  - Loyalty-Punkte-Einlösung
- **Bestellbestätigung:** Automatische Bestellnummer-Generierung

**Technische Details:**
- Frontend: React mit Context API für globalen State
- Backend: FastAPI mit MongoDB
- Validierung: Pydantic Models
- API-Endpunkte: `/api/orders`, `/api/orders/{order_id}/status`

---

### 2. **Burger Builder (Produkt-Konfigurator)**
**Status:** ✅ Implementiert (Warten auf echte Produktbilder)

- **Interaktive Burger-Erstellung:**
  - Basis-Burger als Ausgangspunkt wählen
  - Zutaten individuell hinzufügen/entfernen
  - Toppings, Extras, Saucen anpassen
  - Allergene automatisch tracken
- **Live-Vorschau:** Visuelle Darstellung des Burgers (aktuell CSS-Gradients, wartet auf echte Fotos)
- **Speicherfunktion:** Custom Burgers im Profil speichern & wiederverwenden
- **Preisberechnung:** Dynamic pricing basierend auf Zutaten

**Technische Details:**
- Komponenten: `BurgerBuilder.jsx`, `BurgerPreview.jsx`
- API: `/api/custom-burgers`, `/api/custom-burgers/saved`
- Datenmodell: `CustomBurger` in MongoDB

---

### 3. **Loyalty & Gamification System**
**Status:** ✅ Vollständig implementiert

**Punkte-System:**
- Nutzer verdienen 1 Punkt pro ausgegebenem Euro
- Punkte-Guthaben wird in Echtzeit aktualisiert
- Einlösung: 100 Punkte = 1€ Rabatt beim Checkout
- Anzeige auf dedizierter `/rewards` Seite

**Achievements (Erfolge):**
- Vordefinierte Meilensteine (z.B. "Erste Bestellung", "10 Bestellungen", "50€+ Bestellung")
- Automatisches Freischalten bei Erfüllung der Bedingungen
- Bonus-Punkte für jedes Achievement
- Visuelle Achievement-Badges auf Rewards-Seite

**UI-Integration:**
- `LoyaltyPoints.jsx` Komponente in Header/Navigation
- Rewards-Page mit Fortschrittsbalken und Unlock-Animation
- Checkout-Integration für Punkte-Einlösung

**Technische Details:**
- Modelle: `LoyaltyAccount`, `Achievement`
- API: `/api/loyalty/me`, `/api/achievements`, `/api/loyalty/redeem`
- Backend-Logik: Automatische Punktevergabe nach Bestellabschluss

---

### 4. **Social Ordering (Gruppen-Bestellungen)**
**Status:** ✅ Vollständig implementiert

**Funktionalität:**
- **Host erstellt Bestellung:**
  - Generierung eines einzigartigen Share-Links
  - Auswahl des Lieferstandorts
  - 60 Minuten Gültigkeitsdauer
- **Gäste treten bei:**
  - Öffnen des Share-Links
  - Produkte zum Sammelwarenkorb hinzufügen
  - Eigene Anpassungen vornehmen
- **Finale Bestellung:**
  - Host sieht alle Teilnehmer-Items
  - Gesamtpreis wird berechnet
  - Host schließt die Bestellung ab

**Seiten:**
- `/start-group-order`: Host-Seite zum Initiieren
- `/group-order/:id`: Gäste-Seite zum Beitreten

**Technische Details:**
- Modell: `GroupOrder` mit `items[]` Array
- API: `/api/group-orders`, `/api/group-orders/{id}`, `/api/group-orders/{id}/join`
- Ablauf-Handling: Automatisches Expiry nach 60 Minuten

---

### 5. **E-Mail-Benachrichtigungssystem**
**Status:** ⚠️ Implementiert, aber blockiert (ungültiger SendGrid API-Key)

**E-Mail-Typen:**
1. **E-Mail-Verifizierung:**
   - 6-stelliger Verifizierungscode
   - 15 Minuten Gültigkeitsdauer
   - Sicherheit: Bestellungen nur mit verifizierter E-Mail

2. **Bestellstatus-Updates:**
   - Bestellbestätigung sofort nach Aufgabe
   - Status-Updates: "Bestätigt", "In Zubereitung", "Unterwegs", "Geliefert"
   - Echtzeit-Benachrichtigung bei jedem Status-Wechsel

3. **Review-Anfrage:**
   - Automatisch 1 Stunde nach Lieferung
   - Personalisierte Nachricht mit Google Review Link
   - Filial-spezifischer Link (Rellingen oder Henstedt-Ulzburg)

**Technische Details:**
- Service: `email_service.py` mit SendGrid-Integration
- Templates: Branded HTML-E-Mails mit ZOZO-Design
- Scheduler: APScheduler für verzögerte Review-E-Mails
- API: `/api/request-verification`, `/api/verify-email`
- **BLOCKIERT:** Erfordert gültigen SendGrid API-Key (mit `SG.` Präfix)

---

### 6. **Admin-Dashboard (Multi-Rolle)**
**Status:** ✅ Vollständig implementiert

**Rollen-System:**
- **Owner:** Voller Zugriff auf alle Funktionen und Filialen
- **Manager:** Zugriff nur auf zugewiesene Filiale(n)

**Dashboard-Funktionen:**

**a) Order Management**
- Echtzeit-Übersicht aller Bestellungen
- Filtern nach Status (Ausstehend, In Zubereitung, etc.)
- Status-Update mit einem Klick
- Detailansicht: Kunde, Produkte, Adresse, Zahlungsmethode
- Bestellhistorie mit Suchfunktion

**b) Menü-Verwaltung**
- CRUD für alle Produkte (Create, Read, Update, Delete)
- Kategorien-Management
- Preisanpassung
- Verfügbarkeits-Toggle (In Stock / Out of Stock)
- Bildupload-Integration
- Allergene & Nährwertangaben

**c) Featured Products**
- Auswahl von Produkten für Carousel auf Startseite
- Drag & Drop Reihenfolge (geplant)
- Ein/Aus-Schaltung

**d) Discount Codes**
- Rabattcodes erstellen und verwalten
- Typen: Prozentsatz oder Festbetrag
- Mindestbestellwert-Einstellung
- Ablaufdatum
- Verwendungslimit
- Aktiv/Inaktiv-Status

**e) Analytics (Basis-Version)**
- Gesamtumsatz (gesamt und nach Filiale)
- Anzahl Bestellungen
- Durchschnittlicher Bestellwert
- Beliebteste Produkte

**Technische Details:**
- Route: `/admin/*`
- Authentifizierung: E-Mail & Passwort (JWT-Tokens geplant)
- API: Separate Endpoints für jede Admin-Funktion
- UI: Responsive Tabellen, Dialogs (Shadcn), Toast-Feedback

---

### 7. **Location Management (Filial-Verwaltung)**
**Status:** 🔄 In Planung (Erweiterung des Admin-Dashboards)

**Ziel:**
- Store-Manager können Filial-spezifische Einstellungen selbst vornehmen

**Geplante Features:**
- **Liefergebiet-Konfiguration:**
  - Option 1: Radius in km (z.B. 5 km um Filiale)
  - Option 2: PLZ-Liste (kommagetrennt eingeben)
- **Lieferkosten:** Individuell pro Filiale festlegen
- **Mindestbestellwert:** Anpassbar
- **Lieferzeit-Schätzung:** z.B. "30-45 Minuten"
- **Öffnungszeiten-Verwaltung:** Bearbeitung direkt im Dashboard

**Technische Details:**
- Neues Datenmodell: `LocationSettings` mit Feldern für Radius, PLZ-Liste, Fees
- API: `/api/locations/{id}/settings` (GET/PUT)
- Frontend: Neue Admin-Seite `/admin/locations`

---

### 8. **ExpertOrder POS-Integration**
**Status:** ✅ Implementiert (Test-Environment)

**Funktionalität:**
- Automatische Weiterleitung von Online-Bestellungen an das Kassen-System
- Echtzeit-Synchronisierung
- Fehlerbehandlung mit Retry-Logik
- Fallback: Manuelle Bestellung im Admin-Dashboard sichtbar

**Technische Details:**
- REST API Integration
- Endpoint: Aktuell Test-URL (muss in Produktion angepasst werden)
- Payload-Mapping: ZOZO-Bestellung → ExpertOrder-Format

---

## 🗂️ Weitere Features & Seiten

### 9. **Standort-Seiten**
- Dedizierte Seiten für jede Filiale (`/locations/rellingen`, `/locations/henstedt-ulzburg`)
- Google Maps Embed
- Öffnungszeiten, Kontaktdaten, Anfahrtsbeschreibung
- Liefergebiet-Übersicht

### 10. **Bewertungen & Testimonials**
- Kundenbewertungen auf Startseite
- Google Reviews Integration (Links zu echten Google-Bewertungen)
- Automatische Review-Anfrage via E-Mail nach Bestellung

### 11. **Über Uns**
- Brand Story
- Team-Vorstellung
- Qualitätsversprechen
- Nachhaltigkeits-Fokus

### 12. **Kontakt-Seite**
- Kontaktformular (geplant: E-Mail-Versand via SendGrid)
- Social Media Links
- Öffnungszeiten beider Filialen

### 13. **Deals & Promotions**
- Spezielle Angebote-Sektion auf Homepage
- Zeitlich begrenzte Deals
- Automatische Badge-Anzeige auf Produkten ("20% OFF")

### 14. **Quick Reorder**
- Nutzer können vorherige Bestellungen mit einem Klick wiederholen
- Gespeichert im User-Profil (nach Login)

---

## 🛠️ Technische Architektur

### Frontend
**Framework:** React 18
**Build-Tool:** Vite
**Styling:** 
- Tailwind CSS
- Shadcn/UI Komponenten
- Custom CSS Animations
**State Management:** React Context API + localStorage
**Routing:** React Router v6
**Icons:** Lucide-React
**Carousels:** Embla-Carousel-React
**Notifications:** Sonner (Toast-System)

**Performance-Optimierungen:**
- Code-Splitting mit `React.lazy()` und `Suspense`
- Route-basiertes Lazy Loading
- Bildoptimierung
- Font-Preloading

### Backend
**Framework:** FastAPI (Python)
**Datenbank:** MongoDB
**ODM:** Motor (Async MongoDB Driver)
**Validation:** Pydantic Models
**Task Scheduling:** APScheduler
**E-Mail-Service:** SendGrid (Python SDK)

**API-Struktur:**
- RESTful Endpoints mit `/api` Präfix
- CORS-konfiguriert für Frontend-Integration
- Fehlerbehandlung mit HTTP Status Codes
- Async/Await für Performance

### Datenbank-Schema (Hauptmodelle)

**1. Products:**
```json
{
  "_id": "uuid",
  "name": "string",
  "description": "string",
  "price": "float",
  "category": "string",
  "image_url": "string",
  "allergens": ["array"],
  "is_featured": "boolean",
  "in_stock": "boolean"
}
```

**2. Orders:**
```json
{
  "_id": "uuid",
  "order_number": "string",
  "customer_email": "string",
  "location_id": "uuid",
  "items": [{"product_id", "name", "quantity", "price", "customizations"}],
  "subtotal": "float",
  "delivery_fee": "float",
  "discount": "float",
  "total": "float",
  "delivery_type": "delivery | pickup",
  "delivery_address": "object",
  "payment_method": "string",
  "status": "string",
  "loyalty_points_used": "int",
  "created_at": "datetime"
}
```

**3. Locations:**
```json
{
  "_id": "uuid",
  "name": "string",
  "address": "object",
  "postal_codes": ["array"],
  "phone": "string",
  "email": "string",
  "google_review_url": "string",
  "opening_hours": "object",
  "delivery_fee": "float",
  "min_order_value": "float"
}
```

**4. LoyaltyAccount:**
```json
{
  "user_email": "string",
  "points": "int",
  "unlocked_achievements": ["array"]
}
```

**5. Achievement:**
```json
{
  "_id": "uuid",
  "name": "string",
  "description": "string",
  "condition": "string",
  "points_reward": "int",
  "icon": "string"
}
```

**6. CustomBurger:**
```json
{
  "_id": "uuid",
  "user_email": "string",
  "name": "string",
  "base_burger_id": "uuid",
  "added_ingredients": ["array"],
  "removed_ingredients": ["array"],
  "total_price": "float",
  "created_at": "datetime"
}
```

**7. GroupOrder:**
```json
{
  "_id": "uuid",
  "host_name": "string",
  "host_email": "string",
  "location_id": "uuid",
  "items": [{"added_by", "product_id", "quantity", "customizations"}],
  "created_at": "datetime",
  "expires_at": "datetime"
}
```

**8. UserVerification:**
```json
{
  "email": "string",
  "code": "string",
  "expires_at": "datetime",
  "verified": "boolean"
}
```

**9. DiscountCode:**
```json
{
  "_id": "uuid",
  "code": "string",
  "discount_type": "percentage | fixed",
  "discount_value": "float",
  "min_order_value": "float",
  "expires_at": "datetime",
  "max_uses": "int",
  "current_uses": "int",
  "active": "boolean"
}
```

---

## 🔐 Authentifizierung & Autorisierung

**Status:** Basis-Implementierung (Admin-Bereich)

**Aktuelle Lösung:**
- E-Mail & Passwort-Authentifizierung für Admins
- Session-Storage für aktive Admin-Session
- Rollen-basierter Zugriff (Owner vs. Manager)

**Geplante Verbesserungen:**
- JWT-Token-Authentifizierung
- Refresh-Token-Mechanismus
- Kunden-Login für Bestellhistorie & Profil
- OAuth-Integration (Google, Facebook - optional)

---

## 📱 Mobile Optimierung

- **Vollständig responsive:** Breakpoints für alle Gerätegrößen
- **Touch-optimiert:** Größere Tap-Targets, Swipe-Gesten
- **Mobile Bottom Navigation:** Persistent Navigation Bar am unteren Bildschirmrand
- **Optimierte Performance:** Lazy Loading, kleinere Bilder auf Mobile
- **Mobile-First CSS:** Tailwind Mobile-First Approach

---

## ♿ Accessibility (A11y)

**Implementierte Features:**
- **Skip-to-Content Link:** Ermöglicht Tastatur-Navigation zum Hauptinhalt
- **ARIA-Labels:** Auf allen interaktiven Elementen
- **Keyboard Navigation:** Vollständige Tastatur-Unterstützung
- **Focus-Visible States:** Deutliche visuelle Fokus-Indikatoren
- **Semantic HTML:** Korrekte Nutzung von HTML5-Tags
- **Alt-Text:** Auf allen Bildern
- **Color Contrast:** WCAG AA konform

---

## 🚀 Performance & SEO

### Performance-Optimierungen
- **Code-Splitting:** React.lazy für route-basiertes Splitting
- **Bundle-Size Optimization:** Tree-shaking, minimierte Assets
- **Image Optimization:** WebP-Format, Lazy Loading
- **Font Loading:** Preload kritischer Fonts
- **Caching-Strategie:** Service Worker (in Planung)

### SEO-Optimierungen
- **Meta-Tags:** Title, Description, OG-Tags auf allen Seiten
- **Structured Data:** Schema.org Markup (Restaurant, LocalBusiness)
- **Sitemap:** XML-Sitemap unter `/sitemap.xml`
- **Robots.txt:** Konfiguriert für Crawler
- **URL-Struktur:** SEO-freundliche URLs
- **Canonical Tags:** Duplicate-Content-Prävention
- **Mobile-Friendly:** Google Mobile-First Index ready

---

## 🎨 Design System

### Farb-Palette (Dark Theme)
- **Primary:** Warmes Orange/Rot für CTAs und Akzente
- **Background:** Dunkle Grautöne (#0a0a0a, #1a1a1a)
- **Surface:** Aufgehellte Panels (#2a2a2a)
- **Text:** Weiß (#ffffff) und Grautöne für Hierarchie
- **Accent:** Gold/Gelb für Premium-Elemente

### Typografie
- **Headings:** Custom Font (premium, lesbar)
- **Body:** System-Font Stack für Performance
- **Monospace:** Für Code/Order Numbers

### Spacing-System
- Konsistente Spacing-Scale (Tailwind: 4, 8, 12, 16, 24, 32, 48, 64px)

### Border-Radius
- Small: 4px
- Medium: 8px
- Large: 12px
- XL: 16px

### Shadows & Depth
- Glasmorphismus-Effekte für Overlays
- Subtile Schatten für Card-Elevation
- Glow-Effekte für interaktive Elemente

---

## 🧪 Testing

**Testing-Ansatz:**
- Manuelles Testing via Screenshot-Tool
- Curl-Tests für API-Endpoints
- Testing Agent für umfassende QA
- `data-testid` Attribute auf allen kritischen Elementen

**Getestete Bereiche:**
- Core User-Journey (Browse → Add to Cart → Checkout → Order)
- Admin-Funktionen (CRUD-Operationen)
- Mobile Responsiveness
- Cross-Browser Kompatibilität

---

## 📦 Deployment & Infrastructure

**Hosting:** Kubernetes-Cluster
**Services:**
- Frontend: Port 3000 (React/Vite)
- Backend: Port 8001 (FastAPI)
- MongoDB: Vorkonfiguriert via MONGO_URL

**Process Management:** Supervisor
**Hot Reloading:** Aktiviert für Entwicklung

**Environment Variables:**
- `REACT_APP_BACKEND_URL`: Frontend → Backend Kommunikation
- `MONGO_URL`: MongoDB Connection String
- `SENDGRID_API_KEY`: E-Mail-Service (noch zu konfigurieren)

---

## 🔄 Aktueller Status & Nächste Schritte

### ✅ Abgeschlossen
- Core Bestellsystem mit Checkout
- Admin-Dashboard mit allen CRUD-Funktionen
- Loyalty & Gamification System
- Social Ordering Feature
- Burger Builder (UI fertig, wartet auf Bilder)
- Performance & SEO-Optimierungen
- Accessibility-Verbesserungen
- Mobile-Optimierung

### ⚠️ In Arbeit / Blockiert
- **E-Mail-System:** Vollständig implementiert, aber blockiert durch ungültigen SendGrid API-Key
- **Burger Builder Bilder:** Wartet auf echte Produktfotos vom Kunden
- **Location Management Dashboard:** In Planung (Erweiterung Admin-Bereich)

### 📋 Geplant
1. **Henstedt-Ulzburg Filiale vollständig integrieren**
2. **Location Management im Admin-Dashboard** (Radius/PLZ-Einstellungen)
3. **SendGrid E-Mail-System aktivieren** (sobald gültiger API-Key vorhanden)
4. **User Profile Page:** Zentraler Ort für Bestellhistorie, Loyalty Points, Saved Burgers
5. **Help/FAQ Section**
6. **Kontaktformular mit E-Mail-Versand**
7. **Customer Reviews System** (Optional: Eigene Bewertungen zusätzlich zu Google)
8. **Push-Benachrichtigungen** (Optional: für Order-Status)

---

## 🏆 Besondere Highlights

1. **Vollständig eigenes Bestellsystem** - keine Drittanbieter-Abhängigkeit (außer POS-Integration)
2. **Innovative Gamification** - Loyalty-System motiviert zu Wiederholungsbestellungen
3. **Social Ordering** - Einzigartiges Feature für Gruppen-Bestellungen
4. **Premium-Design** - Hochwertige Dark-Theme-Ästhetik mit Animations
5. **Mobile-First** - Perfekte mobile Erfahrung mit dedizierter Navigation
6. **Accessibility** - WCAG-konform und inklusiv gestaltet
7. **Skalierbar** - Vorbereitet für weitere Filialen und Features

---

## 📞 Support & Wartung

**Zukünftige Wartung:**
- Regelmäßige Dependency-Updates
- Performance-Monitoring
- Fehler-Tracking (z.B. Sentry-Integration geplant)
- Backup-Strategie für MongoDB
- SSL-Zertifikat-Verwaltung

---

## 🎯 Geschäftsziele & KPIs

**Primäre Ziele:**
1. **Conversion-Optimierung:** Maximale Bestellabschlussrate
2. **Kundenbindung:** Loyalty-System für Repeat-Orders
3. **Lokale Dominanz:** SEO für beide Standorte
4. **Markenwirkung:** Premium-Positionierung durch Design

**Messbare KPIs:**
- Online-Bestellungen pro Tag/Woche
- Durchschnittlicher Warenkorbwert
- Loyalty-Programm-Teilnahme
- Wiederkehrende Kunden-Rate
- Google Review-Score
- Website-Traffic & Conversion Rate

---

**Projekt-Status:** 🟢 Produktionsbereit (nach Behebung Email-Blocker)
**Letzte Aktualisierung:** Dezember 2025
**Version:** 1.0 (MVP+)

# 📊 Analytics Dashboard - Vollständige Dokumentation

**Erstellt:** 22. Januar 2026  
**Status:** ✅ IMPLEMENTIERT UND FUNKTIONSFÄHIG  
**Version:** 1.0 - Phase 1 (Core Dashboard)

---

## 🎯 Übersicht

Das Analytics Dashboard bietet Ihnen einen vollständigen Überblick über Ihre Geschäftsmetriken und Performance in Echtzeit.

### ✅ Implementierte Features (Phase 1)

1. **📈 Haupt-Metriken** (4 Karten)
   - Gesamtumsatz (mit Trend %)
   - Anzahl Bestellungen (mit Trend %)
   - Anzahl Kunden
   - Durchschnittlicher Bestellwert (mit Trend %)

2. **📊 Visualisierungen**
   - Umsatz-Verlauf (Area Chart)
   - Stoßzeiten-Analyse (Bar Chart)
   - Top 10 Produkte (Liste mit Rankings)
   - Filial-Vergleich (Horizontale Balken)

3. **🔍 Filter-Optionen**
   - Heute
   - Gestern
   - Letzte 7 Tage
   - Letzte 30 Tage
   - Custom Date Range (vorbereitet)

4. **⚡ Aktionen**
   - Manueller Refresh
   - CSV Export

---

## 🏗️ Technische Architektur

### Backend (FastAPI)

#### Neue Dateien:

**1. `/app/backend/analytics_service.py`**
```python
class AnalyticsService:
  - get_overview_stats()        # Haupt-Metriken mit Trends
  - get_revenue_trend()          # Umsatz-Verlauf
  - get_top_products()           # Bestseller
  - get_peak_hours()             # Stoßzeiten-Analyse
  - get_location_comparison()    # Filial-Vergleich
```

**2. `/app/backend/analytics_endpoints.py`**
```python
Endpoints:
  GET /api/admin/analytics/overview
  GET /api/admin/analytics/revenue-trend
  GET /api/admin/analytics/top-products
  GET /api/admin/analytics/peak-hours
  GET /api/admin/analytics/location-comparison
  GET /api/admin/analytics/export/csv
```

**3. Integration in `/app/backend/server.py`**
```python
from analytics_endpoints import router as analytics_router
app.include_router(analytics_router, prefix="/api")
```

### Frontend (React + Recharts)

#### Neue Komponenten:

1. **`/app/frontend/src/components/MetricCard.jsx`**
   - Wiederverwendbare Metrik-Karte
   - Zeigt Wert, Trend (↗/↘), Icon
   - Loading-State
   - Responsive Design

2. **`/app/frontend/src/components/RevenueChart.jsx`**
   - Area Chart für Umsatz-Verlauf
   - Gradient Fill
   - Hover-Tooltips
   - Zeitachse formatiert (TT.MM)

3. **`/app/frontend/src/components/PeakHoursChart.jsx`**
   - Bar Chart für 24-Stunden-Analyse
   - Zeigt Bestellungen pro Stunde
   - Identifiziert Stoßzeiten visuell

4. **`/app/frontend/src/components/TopProductsList.jsx`**
   - Top 10 Ranking
   - Medaillen für Top 3 (🥇🥈🥉)
   - Zeigt Anzahl + Umsatz
   - Hover-Effekte

5. **`/app/frontend/src/components/LocationComparison.jsx`**
   - Vergleicht Filialen
   - Horizontale Progress Bars
   - Zeigt Umsatz, Orders, Ø Bestellwert

6. **`/app/frontend/src/pages/Analytics.jsx`**
   - Haupt-Dashboard Seite
   - Filter-Management
   - Parallele Datenabfragen
   - CSV Export-Funktion

#### Integration:

**App.js:**
```javascript
const Analytics = lazy(() => import('./pages/Analytics'));

<Route path="/admin/analytics" element={
  <ProtectedAdminRoute>
    <Analytics />
  </ProtectedAdminRoute>
} />
```

**AdminSidebar.jsx:**
```javascript
{
  title: 'Analytics',
  icon: BarChart3,
  path: '/admin/analytics',
  permission: null // Alle Admins
}
```

---

## 📊 Daten-Metriken (Was wird getrackt)

### 1. Umsatz-Metriken
```javascript
{
  total: 1234.50,           // Gesamt-Umsatz
  change: +15.3,            // % Veränderung vs. vorherige Periode
  previous: 1072.10         // Vorheriger Umsatz
}
```

### 2. Bestell-Metriken
```javascript
{
  total: 42,                // Alle Bestellungen
  change: +8.2,             // % Veränderung
  new: 3,                   // Status: new
  preparing: 5,             // Status: preparing
  completed: 34             // Status: completed
}
```

### 3. Kunden-Metriken
```javascript
{
  total: 38,                // Unique Kunden (Email/Phone)
  new: 12,                  // Neukunden (TODO)
  returning: 26             // Stammkunden (TODO)
}
```

### 4. Durchschnittlicher Bestellwert
```javascript
{
  value: 29.40,             // Ø Bestellwert
  change: +3.1,             // % Veränderung
  previous: 28.52           // Vorheriger Ø
}
```

### 5. Umsatz-Verlauf
```javascript
[
  { date: "2026-01-15", revenue: 420.00, orders: 14 },
  { date: "2026-01-16", revenue: 380.50, orders: 12 },
  ...
]
```

### 6. Top Produkte
```javascript
[
  { 
    name: "Classic Burger", 
    quantity: 34, 
    revenue: 420.00 
  },
  ...
]
```

### 7. Stoßzeiten
```javascript
[
  { hour: "00", orders: 0 },
  { hour: "12", orders: 8 },
  { hour: "18", orders: 15 },
  ...
]
```

### 8. Filial-Vergleich
```javascript
[
  {
    location: "Rellingen",
    location_id: "rellingen",
    revenue: 780.00,
    orders: 25,
    avg_order_value: 31.20
  },
  ...
]
```

---

## 🎨 Design

### Farb-Schema (Dark/Light Mode kompatibel)

- **Primär:** `hsl(var(--primary))` - Hauptfarbe (Charts, Buttons)
- **Erfolg:** `emerald-600` - Positive Trends
- **Fehler:** `red-600` - Negative Trends
- **Neutral:** `muted-foreground` - Keine Veränderung

### Icons (Lucide React)

- 💰 Umsatz: `DollarSign`
- 📦 Bestellungen: `ShoppingCart`
- 👥 Kunden: `Users`
- 📈 Durchschnitt: `TrendingUp`
- 🏆 Top Produkte: `Trophy`
- ⏰ Stoßzeiten: `Clock`
- 🏪 Filialen: `Store`

### Chart-Typen (Recharts)

- **Area Chart:** Umsatz-Verlauf (mit Gradient)
- **Bar Chart:** Stoßzeiten
- **Progress Bars:** Filial-Vergleich
- **Cards:** Metriken

---

## 🚀 Verwendung

### Zugriff

1. Admin-Login: `https://menu-management-1.preview.emergentagent.com/admin/login`
2. Nach Login: Klick auf **"Analytics"** in der Sidebar
3. Oder direkt: `/admin/analytics`

### Filter verwenden

```javascript
// Zeitraum ändern
Klick auf: [Heute] [Gestern] [Letzte 7 Tage] [Letzte 30 Tage]

// Filiale filtern (in Entwicklung)
Dropdown: [Alle Filialen ▼] [Rellingen] [Pinneberg]
```

### Daten aktualisieren

```javascript
// Manueller Refresh
Klick auf: [🔄 Aktualisieren]

// Auto-Refresh (geplant für Phase 3)
Alle 30 Sekunden automatisch
```

### CSV Export

```javascript
// Export erstellen
1. Zeitraum wählen
2. Klick auf: [📥 CSV Export]
3. Datei wird heruntergeladen: zozo-analytics-YYYY-MM-DD.csv

// CSV Inhalt:
- Overview Statistics (Umsatz, Orders, Ø)
- Top Products (Name, Quantity, Revenue)
```

---

## 📡 API Endpoints

### 1. Overview Stats
```bash
GET /api/admin/analytics/overview?range_type=7days

Response:
{
  "period": { "range_type": "7days", "start": "...", "end": "..." },
  "stats": {
    "revenue": { "total": 1234.50, "change": 15.3, ... },
    "orders": { "total": 42, "change": 8.2, ... },
    ...
  }
}
```

### 2. Revenue Trend
```bash
GET /api/admin/analytics/revenue-trend?range_type=7days&granularity=day

Response:
{
  "data": [
    { "date": "2026-01-15", "revenue": 420.00, "orders": 14 },
    ...
  ]
}
```

### 3. Top Products
```bash
GET /api/admin/analytics/top-products?range_type=30days&limit=10

Response:
{
  "data": [
    { "name": "Classic Burger", "quantity": 34, "revenue": 420 },
    ...
  ]
}
```

### 4. Peak Hours
```bash
GET /api/admin/analytics/peak-hours?range_type=7days

Response:
{
  "data": [
    { "hour": "12", "orders": 8 },
    ...
  ]
}
```

### 5. Location Comparison
```bash
GET /api/admin/analytics/location-comparison?range_type=30days

Response:
{
  "data": [
    { 
      "location": "Rellingen", 
      "revenue": 780, 
      "orders": 25, 
      "avg_order_value": 31.20 
    },
    ...
  ]
}
```

### 6. CSV Export
```bash
GET /api/admin/analytics/export/csv?range_type=30days

Response: CSV File (text/csv)
```

---

## 🔧 Konfiguration

### Backend Settings

**Zeitzone:** UTC  
**Datumsformat:** ISO 8601  
**Währung:** EUR (€)  

### Frontend Settings

**Datumsformat:** `de-DE` (TT.MM.YYYY)  
**Zahlenformat:** `de-DE` (1.234,56)  
**Chart Library:** Recharts 3.7.0  
**Date Library:** date-fns 4.1.0  

---

## 📈 Zukünftige Erweiterungen (Phase 2-4)

### Phase 2: Erweiterte Insights (geplant)
- ⬜ Kunden-Segmentierung (Neu vs. Stammkunden)
- ⬜ Produktkategorien-Analyse
- ⬜ Zahlungsarten-Übersicht
- ⬜ Tages-Vergleich (Montag vs. Dienstag vs. ...)

### Phase 3: Export & Automation (geplant)
- ⬜ PDF Export
- ⬜ Auto-Refresh (alle 30 Sek)
- ⬜ Custom Date Range Picker
- ⬜ Drill-Down Views (Klick auf Metrik → Details)

### Phase 4: Advanced Features (optional)
- ⬜ KI-Prognosen (Umsatz-Vorhersage)
- ⬜ Ziel-Tracking (Target vs. Actual)
- ⬜ Alerts (E-Mail bei -20% Umsatz)
- ⬜ Automatische tägliche Reports per E-Mail

---

## 🐛 Fehlerbehebung

### Problem: Analytics-Seite zeigt "Keine Daten"

**Ursache:** Keine abgeschlossenen Bestellungen im gewählten Zeitraum

**Lösung:**
1. Zeitraum ändern (z.B. 30 Tage statt Heute)
2. Testbestellungen mit Status "completed" erstellen

### Problem: Charts werden nicht angezeigt

**Ursache:** Recharts nicht geladen oder Daten-Format falsch

**Lösung:**
1. Browser-Konsole prüfen
2. Sicherstellen dass `yarn add recharts` ausgeführt wurde
3. Frontend neu starten: `supervisorctl restart frontend`

### Problem: CSV Export schlägt fehl

**Ursache:** Backend-Endpoint antwortet nicht

**Lösung:**
1. Backend-Logs prüfen: `tail -f /var/log/supervisor/backend.err.log`
2. Endpoint manuell testen: `curl https://.../api/admin/analytics/export/csv?range_type=7days`

---

## 📊 Test-Daten generieren

```bash
# Backend-Konsole
cd /app/backend
python3 -c "
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime, timezone

async def create_test_orders():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    
    # Beispiel: 10 Test-Bestellungen erstellen
    for i in range(10):
        await db.orders.insert_one({
            'order_id': f'TEST-{i}',
            'status': 'completed',
            'total': 25.00 + (i * 5),
            'created_at': datetime.now(timezone.utc),
            'location_id': 'rellingen' if i % 2 == 0 else 'pinneberg',
            'customer_email': f'test{i}@example.com',
            'items': [
                {'name': 'Classic Burger', 'quantity': 1, 'price': 12.00},
                {'name': 'Pommes', 'quantity': 1, 'price': 3.50}
            ]
        })
    print('✅ 10 Test-Bestellungen erstellt')

asyncio.run(create_test_orders())
"
```

---

## ✅ Status

**Phase 1: Core Dashboard** ✅ ABGESCHLOSSEN

- ✅ Backend Analytics Service
- ✅ 6 API Endpoints
- ✅ 5 Chart-Komponenten
- ✅ Haupt-Dashboard Seite
- ✅ Filter-System
- ✅ CSV Export
- ✅ Admin-Menü Integration
- ✅ Responsive Design
- ✅ Dark/Light Mode Support

**Nächste Schritte:**
- Phase 2: Erweiterte Insights
- Phase 3: Export & Automation
- Phase 4: Advanced Features

---

**Erstellt von:** Neo (AI Agent)  
**Datum:** 22. Januar 2026, 12:20 Uhr  
**Version:** 1.0 - Phase 1  
**Status:** ✅ PRODUCTION READY

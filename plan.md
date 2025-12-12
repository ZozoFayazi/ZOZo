# ZOZO Burger - Bestellablauf-Optimierung

## Projekt-Übersicht
ZOZO Burger Lieferservice Website mit FastAPI Backend, React Frontend und MongoDB. Aktuell werden mehrere aufeinanderfolgende Dialoge für die Produktbestellung verwendet. Ziel ist es, die User Experience durch Zusammenführung der Dialoge zu vereinfachen.

## Phase 1: Dialog-Vereinfachung (Status: COMPLETED) ✅
**Ziel:** ProductCustomizer und MenuUpgradeDialog zu einem einzigen, effizienten Dialog zusammenführen

### Umgesetzte Features:
- ✅ Vollständige Menü-Daten aus Foodbooking gescraped und in DB gespeichert
- ✅ Produkt-spezifische abwählbare Zutaten implementiert
- ✅ Menu-Upgrade und Category-Upsell Dialoge entwickelt
- ✅ ExpertOrder POS-Integration erfolgreich getestet

### Aktueller Bestellablauf (3 Dialoge):
1. **ProductCustomizer** → Zutaten entfernen, Extras hinzufügen
2. **MenuUpgradeDialog** → "Als Burger" oder "Als Menü" auswählen
3. **CategoryUpsellDialog** → Cross-Sell für Sidekicks/Desserts

### Neuer optimierter Bestellablauf (2 Dialoge):
1. **Kombinierter ProductCustomizer** → Alles in einem (Zutaten, Extras, Menu-Option)
2. **CategoryUpsellDialog** → Cross-Sell bleibt unverändert

### Technische Änderungen:
- **ProductCustomizer.jsx**: Erweitern mit Menu-Upgrade-Logik
  - Toggle "Als Burger" vs "Als Menü"
  - Dynamische Beilagen- und Getränke-Auswahl bei Menü-Option
  - Preisberechnung inkl. Menu-Upgrade-Kosten
  - Alle bestehenden Features beibehalten (Extras, Removals, Quantity, Special Instructions)
  
- **MenuPage.jsx**: Flow-Logik vereinfachen
  - MenuUpgradeDialog-Import und State entfernen
  - Direkt von ProductCustomizer zu CategoryUpsellDialog
  
- **MenuUpgradeDialog.jsx**: Löschen (redundant)

### Design-Vorgaben (aus design_guidelines.md):
- **Farben**: Primary Red #B00020, Card BG #121214, Border #232326
- **Typografie**: Playfair Display (Headings), Chivo (Body/UI)
- **Buttons**: 10px radius, red glow shadow
- **Spacing**: Großzügige Abstände zwischen Sektionen
- **Testing**: Alle interaktiven Elemente mit `data-testid`

## Phase 2: Produktbilder-Lösung (Status: Not Started) 📋
**Problem:** Aktuelle Bilder sind Stock-Fotos, keine echten Produktbilder

### Optionen:
1. **Admin-Upload-Interface** (empfohlen) - Manueller Upload durch Admin
2. **Scraping von Wolt/Uber Eats** - Automatisch, aber Copyright-Risiko
3. **Stock-Fotos behalten** - Aktuelle hochwertige Bilder

**Nächster Schritt:** Mit Benutzer besprechen und beste Option auswählen

## Phase 3: Zukünftige Integrationen (Status: Planned) 🔮
- Lieferando/Wolt/Uber Eats Webhook-Integration
- CTI (Telephony) Integration für Caller-ID
- iPad Kitchen/Cashier Dashboard

## Technischer Stack
- **Backend**: FastAPI, Motor, Pydantic, JWT Auth
- **Frontend**: React, Vite, Shadcn/UI, Sonner (Toasts), Lucide Icons
- **Database**: MongoDB (Motor)
- **Integration**: ExpertOrder POS System (REST API)

## Wichtige Dateien
- `/app/frontend/src/components/ProductCustomizer.jsx` - Hauptkomponente für diese Phase
- `/app/frontend/src/components/MenuUpgradeDialog.jsx` - Wird entfernt
- `/app/frontend/src/pages/MenuPage.jsx` - Flow-Logik anpassen
- `/app/backend/expertorder.py` - POS Integration (bleibt unverändert)
- `/app/design_guidelines.md` - Design-Richtlinien (strikt befolgen)

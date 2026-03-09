# 🎨 Phase 2: Moderner Produkt-Editor - Konzept & Roadmap

**Status:** ⚠️ **POST GO-LIVE FEATURE**  
**Inspiration:** Toast POS, Square, DoorDash Merchant, Uber Eats Manager

---

## 🏆 WETTBEWERBS-ANALYSE

### Was machen die Besten?

**Toast POS / Square:**
- ✅ Wizard-Flow (4-5 Steps statt ein langes Formular)
- ✅ Live Preview (Kunden-Ansicht während Erstellung)
- ✅ Modifier Groups mit Min/Max
- ✅ Drag & Drop für Reihenfolge
- ✅ Pre-Modifiers ("No", "Extra", "Light")
- ✅ Upsell-Logik ("Möchtest du Pommes dazu?")

**DoorDash Merchant:**
- ✅ Item Variations (Sizes: Small/Medium/Large mit eigenen Preisen)
- ✅ Required vs. Optional Add-ons
- ✅ Bulk-Edit (mehrere Produkte gleichzeitig)
- ✅ Ingredient Removal ("Ohne Zwiebeln, Tomaten")

**Uber Eats Manager:**
- ✅ Smart Categories (Auto-suggest basierend auf Item-Namen)
- ✅ Image Upload mit Crop-Tool
- ✅ Nutritional Info (Allergene, Kalorien)
- ✅ Availability Schedule (z.B. "nur abends")

---

## 🎯 UNSER ZIELBILD FÜR ZOZO BURGER

### Problem mit aktuellem System

**Aktuell:**
- ❌ Ein langes Formular (Name, Beschreibung, Preise, Bild)
- ❌ Keine Varianten (Normal/Medium/Large manuell als separate Felder)
- ❌ Keine Extras/Modifier Groups
- ❌ Keine Zutaten-Abwahl
- ❌ Keine Upsells
- ❌ Keine Live Preview

**Folge:**
- Kunde kann nicht "Ohne Zwiebeln" bestellen
- Keine Upsells im Checkout ("Pommes dazu?")
- Komplizierte Produktpflege (3 Preisfelder für Sizes)

---

## ✅ LÖSUNG: Wizard-basierter Produkt-Editor

### Step 1: Basics (Pflicht-Infos)

**Input-Felder:**
- Name (Pflicht)
- Kategorie (Dropdown)
- Kurzbeschreibung (2-3 Sätze)
- Bild-Upload (mit Crop-Tool, optional)
- Allergene (Multi-Select: A, C, F, G, J, L)
- Zusatzstoffe (Multi-Select: 1, 2, 3, 4, 8)
- Menüposition (Sortier-Nummer, auto-suggest)

**UI-Design:**
- Links: Formular
- Rechts: Live Preview Card (wie Kunde es sieht)

---

### Step 2: Varianten & Preise

**Toggle:** "Hat dieses Produkt Größen/Varianten?"

**Wenn JA:**
- Varianten-Liste:
  - Normal: €X.XX
  - Medium: €X.XX (optional)
  - Large: €X.XX (optional)
- Custom Varianten: z.B. "Family Size", "XL"

**Wenn NEIN:**
- Ein Preis-Feld: €X.XX

**Beispiele:**
- Burger: Normal €7.90, Medium €9.90
- Pizza: Medium €9.90, Large €12.90, Family €18.90
- Getränk: 0.33l €2.50, 0.5l €3.50, 1l €5.90

**UI:** Tabelle mit Add/Remove Rows

---

### Step 3: Zutaten & Abwahl (Optional, aber wichtig)

**Basis-Zutaten definieren:**
- Multi-Select oder Tag-Input
- Beispiel Burger: Fleisch, Käse, Salat, Tomate, Zwiebeln, Gurken, Sauce

**Abwahl erlauben:**
- Toggle: "Kunden dürfen Zutaten abwählen?"
- Max-Abwahl: z.B. max. 3 Zutaten abwählbar

**Frontend-Effekt:**
- Im Checkout erscheint: "Zutaten anpassen" Dialog
- Checkboxen: "Ohne Zwiebeln", "Ohne Tomaten", etc.

**Datenmodell:**
```json
{
  "base_ingredients": ["Fleisch", "Käse", "Salat", "Tomate", "Zwiebeln"],
  "allow_ingredient_removal": true,
  "max_removals": 3
}
```

---

### Step 4: Extras & Modifier Groups

**Modifier Groups hinzufügen:**

Beispiel: Burger

**Group 1: Sauce (Required, Min=1, Max=1)**
- Options: Ketchup, Mayo, BBQ, Curry
- Default: Ketchup (pre-selected)

**Group 2: Extras (Optional, Min=0, Max=5)**
- Extra Käse (+€1.00)
- Bacon (+€1.50)
- Jalapeños (+€0.80)
- Extra Patty (+€2.50)

**Group 3: Beilage (Optional, Min=0, Max=1)**
- Pommes (+€2.90)
- Wedges (+€3.20)
- Salat (+€2.50)

**UI:**
- Liste der Modifier Groups
- Add Group Button
- Für jede Group: Add Option Button
- Drag & Drop zum Sortieren

**Datenmodell:**
```json
{
  "modifier_groups": [
    {
      "id": "sauce",
      "title": "Wähle deine Sauce",
      "required": true,
      "min": 1,
      "max": 1,
      "options": [
        {"name": "Ketchup", "price": 0, "default": true},
        {"name": "BBQ Sauce", "price": 0.30}
      ]
    },
    {
      "id": "extras",
      "title": "Extras hinzufügen",
      "required": false,
      "min": 0,
      "max": 5,
      "options": [
        {"name": "Extra Käse", "price": 1.00},
        {"name": "Bacon", "price": 1.50}
      ]
    }
  ]
}
```

---

### Step 5: Upsells (Optional)

**Upsell Groups definieren:**

**Beispiel:**
- "Menü draus machen?" (+€3.50: Pommes + Getränk)
- "Dessert hinzufügen?" (Brownie, Eis)
- "Extra Dip?" (Aioli, Sweet Chili)

**Trigger:**
- Im Checkout erscheint nach "In den Warenkorb"
- Modal: "Perfekt! Möchtest du noch...?"

**Datenmodell:**
```json
{
  "upsell_groups": [
    {
      "title": "Menü draus machen?",
      "items": [
        {"product_id": "...", "name": "Pommes", "price": 2.90},
        {"product_id": "...", "name": "Cola 0.5l", "price": 2.50}
      ],
      "bundle_price": 3.50,
      "trigger": "add_to_cart"
    }
  ]
}
```

---

## 🎨 UI/UX MOCKUP

### Layout: Split-Screen mit Live Preview

```
┌─────────────────────────────────────────────┐
│  Neues Produkt erstellen                    │
├─────────────────────┬───────────────────────┤
│ WIZARD (Links)      │ LIVE PREVIEW (Rechts) │
├─────────────────────┼───────────────────────┤
│ [1][2][3][4][5]     │  ┌─────────────────┐  │
│                     │  │  Produktbild    │  │
│ Step 1: Basics      │  └─────────────────┘  │
│                     │                       │
│ Name: [ Cheeseburger│  **Cheeseburger**     │
│ Kategorie: [Burger ▼│  Premium Beef mit...  │
│ Beschreibung: [... ]│                       │
│ Bild: [Upload]      │  Ab €7.90             │
│ Allergene: [A][C][G]│                       │
│                     │  🛒 In den Warenkorb  │
│ [Abbrechen][Weiter →│                       │
└─────────────────────┴───────────────────────┘
```

**Live Preview zeigt:**
- Wie das Produkt auf der Kundenwebsite aussieht
- Preis live berechnet (inkl. Varianten)
- Allergene-Badges
- Verfügbarkeits-Status

---

## 📊 DATENMODELL (Erweitert)

### Aktuelles Schema (Phase 1)

```python
{
  "name": str,
  "description": str,
  "category_id": str,
  "price_normal": float,
  "price_medium": float,
  "price_large": float,
  "image_url": str,
  "active": bool,
  "in_stock": bool
}
```

### Neues Schema (Phase 2)

```python
{
  # Basics
  "name": str,
  "description": str,
  "category_id": str,
  "image_url": str,
  "allergens": ["A", "C", "G"],
  "additives": ["1", "2"],
  "sort_order": int,
  
  # Varianten
  "has_variants": bool,
  "variants": [
    {"name": "Normal", "price": 7.90, "sku": "CHEESE-N"},
    {"name": "Medium", "price": 9.90, "sku": "CHEESE-M"},
    {"name": "Large", "price": 12.90, "sku": "CHEESE-L"}
  ],
  
  # Zutaten
  "base_ingredients": ["Beef Patty", "Cheddar", "Salat", "Tomate", "Zwiebeln"],
  "allow_ingredient_removal": true,
  "max_ingredient_removals": 3,
  
  # Modifier Groups
  "modifier_groups": [
    {
      "id": "sauce",
      "title": "Wähle deine Sauce",
      "required": true,
      "min": 1,
      "max": 1,
      "options": [
        {"name": "Ketchup", "price": 0, "default": true},
        {"name": "BBQ", "price": 0.30}
      ]
    }
  ],
  
  # Upsells
  "upsell_groups": [
    {
      "title": "Menü draus machen?",
      "bundle_price": 3.50,
      "items": ["pommes_id", "cola_id"]
    }
  ],
  
  # Status
  "active": bool,
  "in_stock": bool
}
```

**Backward-Kompatibilität:**
- Alte Produkte ohne `variants` → `price_normal` wird verwendet
- Fehlende Felder: Defaults

---

## 🚀 IMPLEMENTATION ROADMAP

### Phase 2.1: MVP Wizard (Priorität 1)

**Aufwand:** ~4-6 Stunden

**Features:**
- ✅ 4-Step Wizard (Basics, Varianten, Zutaten, Modifier)
- ✅ Live Preview (rechte Spalte)
- ✅ Image Upload mit Crop
- ✅ Varianten-Management (Add/Remove Size)
- ✅ Basis-Modifier Groups (Sauce, Extras)

**Liefert:**
- Moderne UX wie Wettbewerb
- Varianten-Support (Normal/Medium/Large)
- Einfache Extras (z.B. Extra Käse)

---

### Phase 2.2: Advanced Features (Priorität 2)

**Aufwand:** ~6-8 Stunden

**Features:**
- ✅ Zutaten-Abwahl ("Ohne Zwiebeln")
- ✅ Pre-Modifiers (No/Extra/Light)
- ✅ Required Modifier Groups (z.B. "Wähle Sauce")
- ✅ Min/Max Validation
- ✅ Upsell-Logik (Checkout-Modal)

**Liefert:**
- Volle Flexibilität wie Konkurrenz
- Bessere Customer Experience
- Höherer Average Order Value (Upsells!)

---

### Phase 2.3: Nice-to-Have (Priorität 3)

**Aufwand:** ~4-6 Stunden

**Features:**
- ✅ Bulk-Edit (mehrere Produkte gleichzeitig)
- ✅ Product Templates ("Kopiere von bestehendem Produkt")
- ✅ Availability Schedule ("nur abends", "Weekends only")
- ✅ Nutrition Info (Kalorien, Allergene erweitert)
- ✅ Product Analytics (Bestseller, Revenue per Product)

---

## 💡 KONKRETE UI-VORSCHLÄGE

### Wizard Navigation

```
[1 Basics] → [2 Varianten] → [3 Zutaten] → [4 Extras] → [5 Vorschau]
   ✓           ○              ○             ○            ○
```

**Jeder Step:**
- Grüner Check wenn ausgefüllt
- "Zurück" / "Weiter" / "Überspringen" Buttons
- Live Preview rechts aktualisiert sich

---

### Live Preview (Rechts)

**Desktop:**
```
┌──────────────────────┐
│ [Produktbild]        │
│                      │
│ **Cheeseburger**     │
│ Premium Beef Patty.. │
│                      │
│ 🏷️ Allergene: A, C, G │
│                      │
│ Größe wählen:        │
│ ○ Normal     €7.90   │
│ ● Medium     €9.90   │
│ ○ Large      €12.90  │
│                      │
│ Extras:              │
│ □ Extra Käse  +€1.00 │
│ ☑ Bacon       +€1.50 │
│                      │
│ Gesamt: €12.40       │
│ [In den Warenkorb]   │
└──────────────────────┘
```

**Mobile:**
- Preview in Accordion (ausklappbar)
- Oder: Bottom Sheet

---

## 📦 DATENMODELL: PHASE 2

### Neue Collections

**`modifier_groups`** (global, reusable)
```json
{
  "_id": "sauce_group_1",
  "title": "Wähle deine Sauce",
  "type": "single_choice",
  "required": true,
  "min": 1,
  "max": 1,
  "options": [
    {"name": "Ketchup", "price": 0, "default": true},
    {"name": "Mayo", "price": 0},
    {"name": "BBQ", "price": 0.30}
  ]
}
```

**`upsell_rules`** (global)
```json
{
  "_id": "burger_upsell_1",
  "trigger_category": "burgers",
  "title": "Menü draus machen?",
  "description": "Pommes + Getränk für nur €3.50",
  "bundle_items": ["pommes_id", "cola_id"],
  "bundle_price": 3.50,
  "active": true
}
```

### Erweiterte `menu_items`

```json
{
  // Existing fields...
  "name": "Cheeseburger",
  "category_id": "...",
  
  // NEW: Variants
  "has_variants": true,
  "variants": [
    {"name": "Normal", "price": 7.90, "calories": 450},
    {"name": "Medium", "price": 9.90, "calories": 650}
  ],
  
  // NEW: Ingredients
  "base_ingredients": ["Beef Patty", "Cheddar", "Salat", "Tomate", "Zwiebeln", "Sauce"],
  "allow_ingredient_removal": true,
  "max_ingredient_removals": 3,
  "removable_ingredients": ["Zwiebeln", "Tomaten", "Gurken"],
  
  // NEW: Modifiers
  "modifier_group_ids": ["sauce_group_1", "extras_group_1"],
  
  // NEW: Upsells
  "upsell_rule_ids": ["burger_upsell_1"]
}
```

---

## 🎯 AUFWANDS-SCHÄTZUNG

### MVP (Minimales Produktfeature-Set)

**Umfang:**
- Wizard UI (4 Steps: Basics, Varianten, Modifier, Preview)
- Live Preview (rechts)
- Image Upload + Crop
- Varianten (Normal/Medium/Large)
- 1-2 Modifier Groups (Sauce, Extras)

**Aufwand:** ~8-10 Stunden
- Backend: Neues Datenmodell, API Endpoints (3h)
- Frontend: Wizard-Komponente, Steps, Preview (5h)
- Tests: E2E Flow (2h)

**Liefert:** Moderne UX, Varianten-Support

---

### Full Feature (Wettbewerbsfähig)

**Zusätzlich:**
- Zutaten-Abwahl
- Pre-Modifiers (No/Extra/Light)
- Upsell-Logik
- Required Modifier Groups
- Bulk-Edit
- Product Templates

**Aufwand:** ~18-24 Stunden total
- MVP: 10h
- Advanced Features: 8h
- Nice-to-Haves: 6h

**Liefert:** Feature-Parität mit Toast/Square/DoorDash

---

## 📋 PRIORISIERUNG

### SOFORT (vor Go-Live):
- ✅ Master-Slave Architektur → **DONE**
- ⚠️ Resend Domain → Pending
- ⚠️ Admin Security → Pending

### NACH GO-LIVE (Woche 1):
- 🎯 Wizard MVP (Basics + Varianten + Preview)
- 🎯 Modifier Groups (Sauce, Extras)

### NACH GO-LIVE (Woche 2-3):
- 🎯 Zutaten-Abwahl
- 🎯 Upsells
- 🎯 Bulk-Edit

---

## 💡 KONKRETE NÄCHSTE SCHRITTE

**Für Wizard-Implementation:**

1. **Backend zuerst:**
   - Datenmodell erweitern (`variants`, `modifier_groups`)
   - API Endpoints: POST/PUT mit neuem Schema
   - Backward-Kompatibilität sicherstellen

2. **Frontend Wizard:**
   - Komponente: `ProductWizard.jsx`
   - Steps: 4-5 separate Components
   - State Management: useState oder React Hook Form
   - Live Preview: Separate Component (CustomerProductCard.jsx)

3. **Tests:**
   - Produkt mit Varianten erstellen
   - Modifier Groups hinzufügen
   - Preview korrekt
   - Checkout zeigt Modifiers

---

## 🆚 VERGLEICH: VORHER / NACHHER

### Aktuell (Phase 1):

**Admin erstellt Burger:**
- Formular: Name, Beschreibung, 3 Preisfelder (normal, medium, large), Bild
- Speichern
- Fertig

**Kunde bestellt:**
- Sieht nur: Name, Preis, Bild
- Kann nicht anpassen

---

### Mit Phase 2 (Wizard):

**Admin erstellt Burger:**
- Step 1: Name "Cheeseburger", Kategorie, Bild
- Step 2: Varianten: Normal €7.90, Medium €9.90
- Step 3: Zutaten: Beef, Käse, Salat, Tomate, Zwiebeln (abwählbar)
- Step 4: Extras: Extra Käse (+€1), Bacon (+€1.50)
- Step 5: Preview → Speichern

**Kunde bestellt:**
- Wählt Größe: Medium
- Wählt Extras: Extra Käse
- Wählt "Ohne Zwiebeln"
- Checkout zeigt: "Cheeseburger Medium + Extra Käse, ohne Zwiebeln" = €10.90

**Upsell erscheint:** "Menü draus machen? Pommes + Cola für nur +€3.50"

---

## ✅ EMPFEHLUNG

**Jetzt:** Go-Live fertig machen (Resend + Security)  
**Dann:** Phase 2.1 MVP (Wizard + Varianten + Modifier) als erste Post-Launch Feature  
**Timeline:** 1-2 Wochen nach Go-Live

**Begründung:**
- Master-Slave ist jetzt stabil
- Wizard verbessert UX massiv
- Höherer AOV durch Upsells/Extras

---

*Konzept erstellt: 06.01.2026*  
*Agent: Neo*  
*Status: Ready for Review*

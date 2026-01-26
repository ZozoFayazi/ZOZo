# 🎯 UPSELLING-SYSTEM - ÜBERSICHT ZUR KONTROLLE

## Bitte prüfen und bestätigen Sie, bevor ich implementiere!

---

## 📋 UPSELL-KATEGORIEN ÜBERSICHT

### A) BURGER EINZELN (ohne Menü)

**Wann:** Kunde bestellt Burger OHNE Menü-Upgrade

**Kategorien (5):**

#### A1 - Mehr Fleisch
```
Headline: "Mehr Fleisch, mehr Glück."

Regel: Nur passende Größe anzeigen!
- Bei Burger 125g → Extra Beef Patty 125g (+€5.90)
- Bei Burger 180g → Extra Beef Patty 180g (+€7.90)

NICHT: Größen-Wechsel (125g → 180g Upgrade)
```

#### A2 - Käse
```
Headline: "Käse macht alles besser."

Optionen:
☐ Extra Käse (+€1.50)
```

#### A3 - Crunch
```
Headline: "Crunch gefällig ?"

Optionen:
☐ Röstzwiebeln (+€1.00)
```

#### A4 - Extra Toppings
```
Headline: "Ein bisschen extra geht immer."

Optionen (Multi-Select):
☐ Jalapeños +€1.00
☐ Champignons +€1.50
☐ Oliven +€1.50
☐ Peperoni +€1.00
☐ Rucola +€1.00
☐ Eisbergsalat +€0.50
☐ Tomate +€0.50
☐ Zwiebeln +€0.50
☐ Rote Zwiebeln +€0.50
☐ Gewürzgurken +€0.50
☐ Bacon +€2.00
☐ Spiegelei +€2.00
```

#### A5 - Dips & Saucen
```
Headline: "Ohne Dip ist es nur halb so wild."

Info: Extra verpackt geliefert
Mehrfachauswahl + Mengenwahl möglich

Optionen:
☐ Mayonnaise €0.99
☐ Ketchup €0.99
☐ Sweet&Sour-Sauce €0.99
☐ Sweet Chili-Sauce €1.19
☐ Chilisauce €1.49
☐ Knobi-Dip €1.99
☐ Snack Dressing €1.99
☐ Sour Cream €1.99
☐ Remoulade €1.99
☐ BBQ-Sauce €1.99
☐ Curry Sauce €1.99
```

---

### B) BURGER MENÜ (mit Menü-Upgrade)

**Wann:** Kunde hat Burger MIT Menü bestellt

**Kategorien (5):**

#### B1 - Beilage tauschen
```
Headline: "Pommes sind top…"

Info: Pommes inklusive, Alternative +€0.99

Standard: ( ) Pommes Frites (inklusive)

Alternativen (statt Pommes, je +€0.99):
( ) Sweet Potato Fries +€0.99
( ) Twister +€0.99
( ) Country Potatoes +€0.99
( ) Potato Dippers +€0.99

Regel: Single-Select (nur 1 Beilage)
Preis: Pommes = €0.00, alle anderen = +€0.99 pauschal
```

#### B2 - Extra Sidekick
```
Headline: "Nur gucken zählt nicht, rein damit."

Info: Zusätzliche Sides (nicht statt Pommes!)

Optionen (Multi-Select):
☐ Mozzarella Sticks (6 Stück) +€6.39
☐ Chicken Nuggets (6 Stück) +€6.99
☐ Chicken Wings (6 Stück) +€7.99
☐ Crunchy Wings (6 Stück) +€8.49
☐ Fire Wings (6 Stück) +€8.49
☐ Chili Cheese Nuggets (8 Stück) +€6.89
☐ Onion Rings (8 Stück) +€5.99
```

#### B3 - Dips & Saucen
```
Gleiche wie A5 (Dip-Liste)
Headline: "Ohne Dip ist es nur halb so wild."
```

#### B4 - Getränke
```
Headline: (keine angegeben)

Info: Pfand separat anzeigen

0,5L (+€0.25 Pfand):
☐ Vio Still €2.49
☐ Coca Cola €2.99
☐ Coca Cola Zero €2.99
☐ Fanta €2.99
☐ Mezzo Mix €2.99
☐ Sprite €2.99

1,0L (+€0.15 Pfand):
☐ Coca Cola €3.89
☐ Coca Cola Zero €3.89
☐ Fanta €3.89
☐ Mezzo Mix €3.89
☐ Sprite €3.89

0,3L (+€0.15 Pfand):
☐ Vio Apfelschorle €2.89
☐ Vio Rhabarberschorle €2.89
☐ Vio Johannisbeer-Schorle €2.89

0,4L (+€0.25 Pfand):
☐ Fuze Tea Pfirsich €2.89
☐ Fuze Tea Zitrone €2.89
```

#### B5 - Dessert
```
Headline: "Nur ein kleines Happy End"

Optionen:
☐ American ZOZO Brownie €3.49
☐ TiramizOZO €3.49 (mit Alkohol-Hinweis)
☐ Miss Chocolic Muffin €3.49
```

---

### C) PIZZA EINZELN

**Wann:** Kunde bestellt Pizza

**Kategorien (3):**
- Dips & Saucen (A5)
- Getränke (B4)
- Dessert (B5)

---

### D) PASTA EINZELN

**Wann:** Kunde bestellt Pasta

**Kategorien (3):**
- Dips & Saucen (A5)
- Getränke (B4)
- Dessert (B5)

---

### E) SALATE EINZELN

**Wann:** Kunde bestellt Salat

**Kategorien (3):**
- Dips & Saucen (A5)
- Getränke (B4)
- Dessert (B5)

---

### F) FINGERFOOD EINZELN

**Wann:** Kunde bestellt Fingerfood (Wings, Nuggets, etc.)

**Kategorien (3):**
- Dips & Saucen (A5)
- Getränke (B4)
- Dessert (B5)

---

## 🎨 UI-STRUKTUR

### Layout-Vorschlag

```
┌─────────────────────────────────────────────┐
│ [Artikel zum Warenkorb hinzugefügt]         │
├─────────────────────────────────────────────┤
│                                             │
│ Perfektioniere deine Bestellung! ✨         │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 💪 Mehr Fleisch, mehr Glück.           │ │
│ ├─────────────────────────────────────────┤ │
│ │ ☐ Extra Beef Patty 125g     +€5.90    │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 🧀 Käse macht alles besser.            │ │
│ ├─────────────────────────────────────────┤ │
│ │ ☐ Extra Käse                +€1.50    │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 🥤 Dips & Saucen                       │ │
│ │ Ohne Dip ist es nur halb so wild.      │ │
│ ├─────────────────────────────────────────┤ │
│ │ ☐ Knobi-Dip          €1.99   [1] [+]  │ │
│ │ ☐ BBQ-Sauce          €1.99   [1] [+]  │ │
│ │ ...                                    │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ [ Nein, danke ]  [ Zum Warenkorb €XX.XX ] │
│                                             │
└─────────────────────────────────────────────┘
```

**Features:**
- Dialog/Modal nach "In den Warenkorb"
- Kategorien als Sections
- Headlines prominent
- Checkboxen für Multi-Select
- Radio-Buttons für Single-Select (Beilage tauschen)
- Mengenwahl [1] [+] [-] für Dips
- Preis-Update live
- "Nein, danke" überspringt Upsells
- "Zum Warenkorb" fügt Upsells hinzu

---

## 🔢 LOGIK-REGELN

### Regel 1: Passende Patty-Größe
```javascript
if (burger.size === "medium") {
  showOption("Extra Beef Patty 125g", 5.90);
} else if (burger.size === "large") {
  showOption("Extra Beef Patty 180g", 7.90);
}
// NICHT beide zeigen!
```

### Regel 2: Beilage tauschen (nur bei Menü)
```javascript
if (isMenu) {
  // Standard: Pommes (€0.00)
  // Alternative: +€0.99 pauschal (egal welche)
  
  if (selectedSide !== "pommes") {
    addCharge(0.99); // Pauschal für Alternative
  }
}
```

### Regel 3: Dips mit Mengenwahl
```javascript
// Kunde kann wählen:
// Knobi-Dip: Menge 2 → €1.99 × 2 = €3.98
// BBQ-Sauce: Menge 1 → €1.99 × 1 = €1.99
```

### Regel 4: Kontext-abhängig
```javascript
if (productType === "burger" && !isMenu) {
  showCategories(["A1", "A2", "A3", "A4", "A5"]);
} else if (productType === "burger" && isMenu) {
  showCategories(["B1", "B2", "B3", "B4", "B5"]);
} else if (productType === "pizza") {
  showCategories(["A5", "B4", "B5"]); // Dips, Getränke, Dessert
}
// etc.
```

---

## 📊 KATEGORIEN-MATRIX

| Produkt-Typ | Einzeln | Menü | Kategorien |
|-------------|---------|------|------------|
| Burger | ✅ | ❌ | A1, A2, A3, A4, A5 |
| Burger | ❌ | ✅ | B1, B2, B3, B4, B5 |
| Pizza | ✅ | - | A5, B4, B5 |
| Pasta | ✅ | - | A5, B4, B5 |
| Salat | ✅ | - | A5, B4, B5 |
| Fingerfood | ✅ | - | A5, B4, B5 |

---

## 💬 HEADLINES (komplett)

```
A1: "Mehr Fleisch, mehr Glück."
A2: "Käse macht alles besser."
A3: "Crunch gefällig ?"
A4: "Ein bisschen extra geht immer."
A5: "Ohne Dip ist es nur halb so wild."

B1: "Pommes sind top…"
B2: "Nur gucken zählt nicht, rein damit."
B3: "Ohne Dip ist es nur halb so wild." (gleich wie A5)
B4: (keine Headline)
B5: "Nur ein kleines Happy End"
```

---

## 💰 PREIS-LISTE (komplett)

### Extra Patties
```
Extra Beef Patty 125g → €5.90
Extra Beef Patty 180g → €7.90
```

### Käse & Crunch
```
Extra Käse → €1.50
Röstzwiebeln → €1.00
```

### Toppings
```
Jalapeños → €1.00
Champignons → €1.50
Oliven → €1.50
Peperoni → €1.00
Rucola → €1.00
Eisbergsalat → €0.50
Tomate → €0.50
Zwiebeln → €0.50
Rote Zwiebeln → €0.50
Gewürzgurken → €0.50
Bacon → €2.00
Spiegelei → €2.00
```

### Beilagen (Menü-Tausch)
```
Pommes Frites → €0.00 (Standard)
Sweet Potato Fries → +€0.99
Twister → +€0.99
Country Potatoes → +€0.99
Potato Dippers → +€0.99
```

### Extra Sidekicks
```
Mozzarella Sticks 6 Stück → €6.39
Chicken Nuggets 6 Stück → €6.99
Chicken Wings 6 Stück → €7.99
Crunchy Wings 6 Stück → €8.49
Fire Wings 6 Stück → €8.49
Chili Cheese Nuggets 8 Stück → €6.89
Onion Rings 8 Stück → €5.99
```

### Dips (11 Optionen)
```
Mayonnaise → €0.99
Ketchup → €0.99
Sweet&Sour-Sauce → €0.99
Sweet Chili-Sauce → €1.19
Chilisauce → €1.49
Knobi-Dip → €1.99
Snack Dressing → €1.99
Sour Cream → €1.99
Remoulade → €1.99
BBQ-Sauce → €1.99
Curry Sauce → €1.99
```

### Getränke 0,5L (Pfand +€0.25)
```
Vio Still → €2.49
Coca Cola → €2.99
Coca Cola Zero → €2.99
Fanta → €2.99
Mezzo Mix → €2.99
Sprite → €2.99
```

### Getränke 1,0L (Pfand +€0.15)
```
Coca Cola → €3.89
Coca Cola Zero → €3.89
Fanta → €3.89
Mezzo Mix → €3.89
Sprite → €3.89
```

### Getränke 0,3L (Pfand +€0.15)
```
Vio Apfelschorle → €2.89
Vio Rhabarberschorle → €2.89
Vio Johannisbeer-Schorle → €2.89
```

### Getränke 0,4L (Pfand +€0.25)
```
Fuze Tea Pfirsich → €2.89
Fuze Tea Zitrone → €2.89
```

### Desserts
```
American ZOZO Brownie → €3.49
TiramizOZO → €3.49 (mit Alkohol)
Miss Chocolic Muffin → €3.49
```

---

## 🎯 SPEZIAL-REGELN

### Regel 1: Keine Patty-Größen-Wechsel
```
❌ NICHT: "Upgrade auf 180g Patty"
✅ RICHTIG: "Extra Patty in gleicher Größe"

Bei 125g Burger → Nur "Extra 125g" anbieten
Bei 180g Burger → Nur "Extra 180g" anbieten
```

### Regel 2: Beilage tauschen = +€0.99 pauschal
```
❌ NICHT: Sweet Potato +€3.50 (voller Preis)
✅ RICHTIG: Sweet Potato +€0.99 (Tausch-Aufpreis)

Kunde zahlt:
- Menü-Grundpreis (enthält Pommes)
- +€0.99 für Alternative statt Pommes
```

### Regel 3: Dips extra verpackt
```
Info-Text anzeigen:
"Dips werden separat verpackt geliefert"

Kunde kann beliebig viele wählen:
- 3x Knobi-Dip = €1.99 × 3 = €5.97
- 1x BBQ = €1.99 × 1 = €1.99
```

### Regel 4: Getränke mit Pfand
```
Anzeige:
Coca Cola 0,5L     €2.99
zzgl. Pfand        €0.25
─────────────────────────
Gesamt            €3.24

Oder als eine Zeile:
Coca Cola 0,5L €2.99 (zzgl. €0.25 Pfand)
```

### Regel 5: Nur aus Speisekarte
```
❌ NICHT: Erfundene Produkte
✅ RICHTIG: Nur was wirklich auf Speisekarte steht

Falls Produkt fehlt → Nicht anzeigen
Keine Platzhalter/Demo-Daten
```

---

## 🔄 USER FLOW

### Beispiel: Burger einzeln bestellen

```
1. Kunde wählt "Champion Burger Medium"
2. Konfiguriert Burger (Brötchen, Extras, etc.)
3. Klickt "In den Warenkorb"
4. → Upsell-Dialog öffnet sich
5. Zeigt Kategorien: A1, A2, A3, A4, A5
6. Kunde wählt:
   - Extra Beef Patty 125g ✓
   - Knobi-Dip (2x) ✓
7. Klickt "Zum Warenkorb €XX.XX"
8. Warenkorb hat:
   - Champion Burger Medium
   - Extra Beef Patty 125g (+€5.90)
   - Knobi-Dip 2x (+€3.98)
```

### Beispiel: Burger-Menü bestellen

```
1. Kunde wählt "Champion Burger Medium Menü"
2. Wählt Beilage: Pommes, Getränk: Cola
3. Klickt "In den Warenkorb"
4. → Upsell-Dialog öffnet sich
5. Zeigt Kategorien: B1, B2, B3, B4, B5
6. Kunde wählt:
   - Beilage tauschen: Twister statt Pommes (+€0.99) ✓
   - Extra Sidekick: Onion Rings (+€5.99) ✓
   - Dessert: Brownie (+€3.49) ✓
7. Klickt "Zum Warenkorb"
8. Warenkorb hat:
   - Champion Burger Medium Menü
   - Twister (statt Pommes) (+€0.99)
   - Onion Rings (+€5.99)
   - Brownie (+€3.49)
```

---

## 📱 UI-KOMPONENTEN

### Dialog-Header
```
"Perfektioniere deine Bestellung! ✨"
Oder: "Noch Appetit auf mehr?"
```

### Kategorie-Section
```
┌─────────────────────────────────────┐
│ [Icon] Headline                     │
├─────────────────────────────────────┤
│ ☐ Option 1   +€X.XX                 │
│ ☐ Option 2   +€X.XX                 │
│ ...                                 │
└─────────────────────────────────────┘
```

### Mengenwahl (für Dips)
```
☐ Knobi-Dip  €1.99   [ - ] [2] [ + ]
```

### Pfand-Anzeige
```
Coca Cola 0,5L         €2.99
zzgl. Pfand           +€0.25
```

### Bottom Buttons
```
[ Nein, danke ]  [ Zum Warenkorb €XX.XX ]
```

---

## ✅ CHECKLISTE ZUR KONTROLLE

**Bitte prüfen Sie:**

- [ ] Alle Headlines korrekt?
- [ ] Alle Preise korrekt?
- [ ] Kategorien korrekt zugeordnet (Burger einzeln vs. Menü)?
- [ ] Beilage-Tausch-Regel klar (+€0.99 pauschal)?
- [ ] Keine Patty-Größen-Wechsel?
- [ ] Dips mit Mengenwahl?
- [ ] Getränke mit Pfand?
- [ ] Dessert-Liste vollständig?
- [ ] Nur Speisekarten-Produkte (keine erfundenen)?
- [ ] UI-Flow sinnvoll?

---

## 🎯 WAS ICH NACH BESTÄTIGUNG MACHE

**Implementierung:**

1. **Backend:**
   - Upsell-Service (Regeln-Engine)
   - API-Endpoints (Upsells abrufen)
   - Kontext-Erkennung (Burger/Menü/Pizza/etc.)

2. **Frontend:**
   - Upsell-Dialog Component
   - Kategorie-Sections
   - Mengenwahl für Dips
   - Preis-Berechnung live
   - Warenkorb-Integration

3. **Datenbank:**
   - Upsell-Produkte konfigurieren
   - Kategorien definieren
   - Regeln hinterlegen

4. **Testing:**
   - Alle Kategorien
   - Alle Produkt-Typen
   - Preis-Berechnungen
   - Warenkorb-Integration

---

## ❓ FRAGEN AN SIE

**Bevor ich implementiere:**

1. **Beilage-Tausch bei Menü:**
   - Kunde hat Pommes im Menü
   - Will Sweet Potato STATT Pommes
   - Zahlt +€0.99
   - Bekommt: Sweet Potato (Pommes wird entfernt)
   **Korrekt so?** ✅ / ❌

2. **Extra Sidekick bei Menü:**
   - Kunde hat Pommes im Menü
   - Will Onion Rings ZUSÄTZLICH
   - Zahlt +€5.99 (voller Preis)
   - Bekommt: Pommes + Onion Rings
   **Korrekt so?** ✅ / ❌

3. **Dips Mengenwahl:**
   - Kunde kann z.B. 5x Knobi-Dip wählen?
   - Oder: Maximum 3-4 pro Dip?
   **Limit?** _________

4. **Wo Upsells zeigen:**
   - Nach "In den Warenkorb" (Dialog)?
   - Oder: Auf Produkt-Seite direkt?
   **Bevorzugt?** _________

5. **Alkohol-Hinweis bei TiramizOZO:**
   - Badge "18+" oder ähnlich?
   - Oder: Nur Text "(mit Alkohol)"?
   **Wie anzeigen?** _________

---

## 📋 BITTE BESTÄTIGEN

**Antworten Sie mit:**

✅ "Alles korrekt, bitte implementieren"

**ODER:**

❌ "Bitte ändern:
   - [Was ändern]
   - [Was ändern]"

**Dann starte ich Implementierung!** 🚀

---

Erstellt: 23.01.2026
Status: Wartet auf Bestätigung

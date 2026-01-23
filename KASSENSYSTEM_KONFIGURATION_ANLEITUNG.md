# 🖥️ KASSENSYSTEM-KONFIGURATION - ZOZO Burger

## An: Emergent / ExpertOrder Support Team
## Von: ZOZO Burger
## Betreff: Artikel-Struktur mit Dialogen und Hilftexten für Mitarbeiter

---

## 🎯 ZIEL

Das Kassensystem soll die **exakt gleiche Struktur** wie der Online-Shop haben:
- Dialog-basierte Auswahl (Popup-Fenster)
- Größen-Auswahl für alle Burger
- Menü-Upgrade-Option mit Beilage/Getränk/Sauce
- Hilftexte für Mitarbeiter (was sie Kunden fragen sollen)
- Modifier-Groups für Brötchen, Dressing, etc.

**Wichtig:** Die Kassensystem-Struktur MUSS mit dem Online-Shop synchron sein, damit:
- Bestellungen korrekt ankommen
- Artikel-Nummern matchen
- Keine "???" auf Kassenbons
- Mitarbeiter können telefonische Bestellungen genauso aufnehmen wie Online

---

## 📋 ARTIKEL-HIERARCHIE & DIALOGE

### 1. BURGER-KATEGORIE

#### Artikel-Typ: "Burger" (z.B. Champion Burger, Farmers Burger, etc.)

**DIALOG 1: Einzeln oder Menü?**
```
╔════════════════════════════════════════════════╗
║  Champion Burger                               ║
╠════════════════════════════════════════════════╣
║                                                ║
║  Hilftext für Mitarbeiter:                     ║
║  "Möchten Sie Ihren Burger einzeln             ║
║   oder als Menü bestellen?"                    ║
║                                                ║
║  [ Einzeln ]  [ Als Menü ]                     ║
║                                                ║
╚════════════════════════════════════════════════╝
```

**Option A: EINZELN gewählt**
→ Weiter zu Dialog 2 (Größe)

**Option B: ALS MENÜ gewählt**
→ Weiter zu Dialog 2 (Größe), dann Dialog 3 (Menü-Komponenten)

---

**DIALOG 2: Größe auswählen**
```
╔════════════════════════════════════════════════╗
║  Champion Burger - Größe                       ║
╠════════════════════════════════════════════════╣
║                                                ║
║  Hilftext für Mitarbeiter:                     ║
║  "Welche Größe möchten Sie?"                   ║
║                                                ║
║  [ Normal 100g ]   €X.XX                       ║
║  [ Medium 125g ]   €X.XX  ← Standard           ║
║  [ Large 180g ]    €X.XX                       ║
║                                                ║
╚════════════════════════════════════════════════╝
```

**Wichtig:**
- **Normal 100g:** Kleinste Größe
- **Medium 125g:** Standard-Größe (empfohlen)
- **Large 180g:** Größte Größe

**Nach Auswahl:**
- Einzeln → Weiter zu Dialog 4 (Brötchen-Auswahl)
- Als Menü → Weiter zu Dialog 3 (Menü-Komponenten)

---

**DIALOG 3: Menü-Komponenten (NUR wenn "Als Menü" gewählt)**
```
╔════════════════════════════════════════════════╗
║  Champion Burger Medium 125g Menü              ║
╠════════════════════════════════════════════════╣
║                                                ║
║  1. BEILAGE WÄHLEN                             ║
║  Hilftext: "Welche Beilage möchten Sie?"       ║
║                                                ║
║  ( ) Pommes Frites Normal         €0.00        ║
║  ( ) Sweet Potato Fries           €0.99        ║
║  ( ) Twister Fries                €0.99        ║
║  ( ) Country Potatoes             €0.99        ║
║                                                ║
║  ────────────────────────────────────────      ║
║                                                ║
║  2. GETRÄNK WÄHLEN                             ║
║  Hilftext: "Welches Getränk dazu?"             ║
║                                                ║
║  ( ) Coca Cola 0,5l                            ║
║  ( ) Coca Cola Zero 0,5l                       ║
║  ( ) Fanta 0,5l                                ║
║  ( ) Mezzo Mix 0,5l                            ║
║  ( ) Sprite 0,5l                               ║
║  ( ) ViO Still 0,5l                            ║
║                                                ║
║  ────────────────────────────────────────      ║
║                                                ║
║  3. SAUCE WÄHLEN (optional)                    ║
║  Hilftext: "Welche Sauce möchten Sie?"         ║
║                                                ║
║  [ ] Ketchup                                   ║
║  [ ] Mayonnaise                                ║
║  [ ] BBQ Sauce                                 ║
║  [ ] Knoblauchsauce                            ║
║  [ ] Keine Sauce                               ║
║                                                ║
║  [ Weiter ]                                    ║
║                                                ║
╚════════════════════════════════════════════════╝
```

**Wichtig:**
- **Beilage:** Radio-Button (nur 1 auswählbar) - PFLICHT
- **Getränk:** Radio-Button (nur 1 auswählbar) - PFLICHT
- **Sauce:** Checkbox (mehrere möglich) - OPTIONAL

**Nach "Weiter":**
→ Dialog 4 (Brötchen-Auswahl)

---

**DIALOG 4: Brötchen-Auswahl**
```
╔════════════════════════════════════════════════╗
║  Champion Burger Medium 125g [Menü]            ║
╠════════════════════════════════════════════════╣
║                                                ║
║  BRÖTCHEN AUSWÄHLEN                            ║
║  Hilftext: "Welches Brötchen möchten Sie?"     ║
║                                                ║
║  ( ) Briochebrötchen                           ║
║  ( ) Semolinabrötchen                          ║
║                                                ║
║  [ Weiter ]                                    ║
║                                                ║
╚════════════════════════════════════════════════╝
```

**Nach "Weiter":**
→ Dialog 5 (Extras/Anpassungen)

---

**DIALOG 5: Extras & Anpassungen (optional)**
```
╔════════════════════════════════════════════════╗
║  Champion Burger Medium 125g Menü              ║
║  + Pommes · Cola · Briochebrötchen             ║
╠════════════════════════════════════════════════╣
║                                                ║
║  EXTRAS HINZUFÜGEN (optional)                  ║
║  Hilftext: "Möchten Sie Extras hinzufügen?"    ║
║                                                ║
║  [ ] Extra Bacon            +€2.00             ║
║  [ ] Extra Käse             +€1.50             ║
║  [ ] Spiegelei              +€2.00             ║
║  [ ] Jalapeños              +€1.00             ║
║                                                ║
║  ────────────────────────────────────────      ║
║                                                ║
║  ZUTATEN ENTFERNEN (optional)                  ║
║  Hilftext: "Soll etwas weggelassen werden?"    ║
║                                                ║
║  [ ] Ohne Zwiebeln                             ║
║  [ ] Ohne Gurken                               ║
║  [ ] Ohne Tomate                               ║
║  [ ] Ohne Salat                                ║
║                                                ║
║  ────────────────────────────────────────      ║
║                                                ║
║  Spezielle Anweisungen:                        ║
║  [_________________________________]           ║
║                                                ║
║  [ In den Warenkorb ]                          ║
║                                                ║
╚════════════════════════════════════════════════╝
```

---

### 2. SALAT-KATEGORIE

**DIALOG 1: Salat-Typ auswählen**
```
╔════════════════════════════════════════════════╗
║  Salate                                        ║
╠════════════════════════════════════════════════╣
║                                                ║
║  Hilftext: "Welchen Salat möchten Sie?"        ║
║                                                ║
║  [ Caesar Salad ]        €9.19                 ║
║  [ Greek Salad ]         €8.99                 ║
║  [ Chicken Salad ]       €10.49                ║
║                                                ║
╚════════════════════════════════════════════════╝
```

**DIALOG 2: Dressing auswählen (PFLICHT)**
```
╔════════════════════════════════════════════════╗
║  Caesar Salad                                  ║
╠════════════════════════════════════════════════╣
║                                                ║
║  DRESSING AUSWÄHLEN                            ║
║  Hilftext: "Welches Dressing möchten Sie?"     ║
║                                                ║
║  ( ) Caesar Dressing      (inklusive)          ║
║  ( ) Italian Dressing     (inklusive)          ║
║  ( ) Balsamico            (inklusive)          ║
║  ( ) Ohne Dressing                             ║
║                                                ║
║  [ Weiter ]                                    ║
║                                                ║
╚════════════════════════════════════════════════╝
```

**DIALOG 3: Extras (optional)**
```
╔════════════════════════════════════════════════╗
║  Caesar Salad + Caesar Dressing                ║
╠════════════════════════════════════════════════╣
║                                                ║
║  EXTRAS HINZUFÜGEN?                            ║
║  Hilftext: "Möchten Sie Extras?"               ║
║                                                ║
║  [ ] Extra Parmesan       +€2.00               ║
║  [ ] Gegrilltes Hähnchen  +€3.50               ║
║  [ ] Avocado              +€2.50               ║
║                                                ║
║  [ In den Warenkorb ]                          ║
║                                                ║
╚════════════════════════════════════════════════╝
```

---

### 3. PIZZA-KATEGORIE

**DIALOG 1: Pizza auswählen**
```
╔════════════════════════════════════════════════╗
║  Pizzen                                        ║
╠════════════════════════════════════════════════╣
║                                                ║
║  [ Pizza Margherita ]    €7.99                 ║
║  [ Pizza Salami ]        €8.99                 ║
║  [ Pizza Tonno ]         €9.49                 ║
║                                                ║
╚════════════════════════════════════════════════╝
```

**DIALOG 2: Größe (falls mehrere Größen)**
```
╔════════════════════════════════════════════════╗
║  Pizza Salami                                  ║
╠════════════════════════════════════════════════╣
║                                                ║
║  Hilftext: "Welche Größe?"                     ║
║                                                ║
║  ( ) Klein (Ø 26cm)      €8.99                 ║
║  ( ) Groß (Ø 32cm)       €11.99                ║
║                                                ║
╚════════════════════════════════════════════════╝
```

**DIALOG 3: Extras**
```
╔════════════════════════════════════════════════╗
║  Pizza Salami Groß                             ║
╠════════════════════════════════════════════════╣
║                                                ║
║  EXTRAS?                                       ║
║  Hilftext: "Zusätzliche Beläge gewünscht?"     ║
║                                                ║
║  [ ] Extra Käse          +€1.50                ║
║  [ ] Extra Salami        +€2.00                ║
║  [ ] Champignons         +€1.50                ║
║  [ ] Oliven              +€1.50                ║
║  [ ] Rucola              +€1.00                ║
║                                                ║
║  [ In den Warenkorb ]                          ║
║                                                ║
╚════════════════════════════════════════════════╝
```

---

### 4. PIZZABRÖTCHEN-KATEGORIE

**DIALOG 1: Pizzabrötchen auswählen**
```
╔════════════════════════════════════════════════╗
║  Pizzabrötchen                                 ║
╠════════════════════════════════════════════════╣
║                                                ║
║  Hilftext: "Wie viele Stück?"                  ║
║                                                ║
║  [ 6 Stück ]             €5.99                 ║
║  [ 12 Stück ]            €10.99                ║
║                                                ║
╚════════════════════════════════════════════════╝
```

**DIALOG 2: Dips auswählen (PFLICHT)**
```
╔════════════════════════════════════════════════╗
║  Pizzabrötchen 6 Stück                         ║
╠════════════════════════════════════════════════╣
║                                                ║
║  DIP AUSWÄHLEN                                 ║
║  Hilftext: "Welchen Dip möchten Sie?"          ║
║  (2 Dips inklusive)                            ║
║                                                ║
║  [✓] Knoblauchsauce      (inklusive)           ║
║  [✓] Kräutersauce        (inklusive)           ║
║  [ ] Chilisauce          +€0.50                ║
║  [ ] BBQ Sauce           +€0.50                ║
║                                                ║
║  Hinweis: 2 Dips kostenlos, ab 3. je €0.50     ║
║                                                ║
║  [ In den Warenkorb ]                          ║
║                                                ║
╚════════════════════════════════════════════════╝
```

---

### 5. FINGERFOOD-KATEGORIE

**DIALOG 1: Fingerfood auswählen**
```
╔════════════════════════════════════════════════╗
║  Fingerfood                                    ║
╠════════════════════════════════════════════════╣
║                                                ║
║  [ Chicken Wings 6 Stück ]    €6.99            ║
║  [ Chicken Wings 12 Stück ]   €12.99           ║
║  [ Onion Rings ]              €4.99            ║
║  [ Mozzarella Sticks ]        €5.99            ║
║                                                ║
╚════════════════════════════════════════════════╝
```

**DIALOG 2: Dips (wie Pizzabrötchen)**
```
╔════════════════════════════════════════════════╗
║  Chicken Wings 6 Stück                         ║
╠════════════════════════════════════════════════╣
║                                                ║
║  DIP AUSWÄHLEN (2 inklusive)                   ║
║  Hilftext: "Welche Dips möchten Sie?"          ║
║                                                ║
║  [✓] BBQ Sauce           (inklusive)           ║
║  [✓] Sour Cream          (inklusive)           ║
║  [ ] Chilisauce          +€0.50                ║
║  [ ] Knoblauchsauce      +€0.50                ║
║                                                ║
║  [ In den Warenkorb ]                          ║
║                                                ║
╚════════════════════════════════════════════════╝
```

---

## 🍔 KOMPLETTES BURGER-BEISPIEL (Schritt für Schritt)

### Szenario: Kunde bestellt "Champion Burger als Menü in Medium"

**Mitarbeiter-Aktionen:**

```
┌─────────────────────────────────────────────────┐
│ SCHRITT 1: Burger antippen                     │
├─────────────────────────────────────────────────┤
│ Mitarbeiter: Tippt auf "Champion Burger"        │
│ System: Dialog öffnet sich                      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ DIALOG 1: "Einzeln oder Menü?"                  │
├─────────────────────────────────────────────────┤
│ Mitarbeiter sagt: "Möchten Sie Ihren Burger     │
│                    einzeln oder als Menü?"      │
│ Kunde sagt: "Als Menü bitte"                    │
│ Mitarbeiter: Tippt auf [ Als Menü ]             │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ DIALOG 2: "Welche Größe?"                       │
├─────────────────────────────────────────────────┤
│ Mitarbeiter sagt: "Welche Größe möchten Sie?"   │
│ Kunde sagt: "Medium"                            │
│ Mitarbeiter: Tippt auf [ Medium 125g ]          │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ DIALOG 3: "Menü-Komponenten"                    │
├─────────────────────────────────────────────────┤
│ Mitarbeiter sagt: "Welche Beilage möchten Sie?" │
│ Kunde sagt: "Pommes"                            │
│ Mitarbeiter: Wählt (○) Pommes Frites Normal     │
│                                                 │
│ Mitarbeiter sagt: "Welches Getränk dazu?"       │
│ Kunde sagt: "Cola"                              │
│ Mitarbeiter: Wählt (○) Coca Cola 0,5l           │
│                                                 │
│ Mitarbeiter sagt: "Welche Sauce möchten Sie?"   │
│ Kunde sagt: "Ketchup und Mayo"                  │
│ Mitarbeiter: Wählt [✓] Ketchup [✓] Mayonnaise  │
│                                                 │
│ Mitarbeiter: Tippt auf [ Weiter ]               │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ DIALOG 4: "Brötchen"                            │
├─────────────────────────────────────────────────┤
│ Mitarbeiter sagt: "Welches Brötchen?"           │
│ Kunde sagt: "Brioche"                           │
│ Mitarbeiter: Wählt (○) Briochebrötchen          │
│ Mitarbeiter: Tippt auf [ Weiter ]               │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ DIALOG 5: "Extras & Anpassungen"                │
├─────────────────────────────────────────────────┤
│ Mitarbeiter sagt: "Möchten Sie Extras?"         │
│ Kunde sagt: "Ja, Extra Bacon"                   │
│ Mitarbeiter: Wählt [✓] Extra Bacon              │
│                                                 │
│ Mitarbeiter sagt: "Soll etwas weggelassen       │
│                    werden?"                     │
│ Kunde sagt: "Ohne Zwiebeln bitte"              │
│ Mitarbeiter: Wählt [✓] Ohne Zwiebeln            │
│                                                 │
│ Mitarbeiter: Tippt auf [ In den Warenkorb ]     │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ RESULT: Artikel im Warenkorb                    │
├─────────────────────────────────────────────────┤
│ Champion Burger Medium 125g Menü                │
│   + Briochebrötchen                             │
│   + Pommes Frites Normal                        │
│   + Coca Cola 0,5l                              │
│   + Ketchup                                     │
│   + Mayonnaise                                  │
│   + Extra Bacon                                 │
│   - Ohne Zwiebeln                               │
│                                                 │
│ Preis: €XX.XX                                   │
└─────────────────────────────────────────────────┘
```

---

## 📐 ARTIKEL-KONFIGURATION IM KASSENSYSTEM

### Burger-Artikel (z.B. Champion Burger)

**Artikel-Stammdaten:**
```
Artikel-Name: Champion Burger
Artikel-Nr: M4;2 (oder Ihre Nummer)
Kategorie: Burger

Eigenschaften:
- Hat Größen: JA (Normal 100g, Medium 125g, Large 180g)
- Kann als Menü: JA
- Brötchen-Auswahl: JA (Pflicht)
- Modifier-Groups: Brötchen, Extras, Removals
```

**Größen-Konfiguration:**
```
Größe 1: Normal 100g     → Preis: €X.XX
Größe 2: Medium 125g     → Preis: €X.XX (Standard)
Größe 3: Large 180g      → Preis: €X.XX
```

**Menü-Upgrade:**
```
Menü-Aufpreis Medium: €X.XX
Menü-Aufpreis Large: €X.XX

Menü enthält:
- 1x Beilage (Pommes/Sweet Potato/Twister/Country)
- 1x Getränk (Cola/Fanta/Sprite/Mezzo/Water)
- 1-2x Sauce (kostenlos)
```

**Modifier-Groups verknüpfen:**
```
1. Brötchen-Gruppe (Pflicht, Single-Select)
   - Briochebrötchen
   - Semolinabrötchen

2. Beilage-Gruppe (nur bei Menü, Single-Select)
   - Pommes Frites Normal (€0.00)
   - Sweet Potato Fries (€0.99 Aufpreis)
   - Twister Fries (€0.99 Aufpreis)
   - Country Potatoes (€0.99 Aufpreis)

3. Getränk-Gruppe (nur bei Menü, Single-Select)
   - Coca Cola 0,5l
   - Coca Cola Zero 0,5l
   - Fanta 0,5l
   - Mezzo Mix 0,5l
   - Sprite 0,5l
   - ViO Still 0,5l

4. Sauce-Gruppe (Multi-Select, max 2-3)
   - Ketchup
   - Mayonnaise
   - BBQ Sauce
   - Knoblauchsauce

5. Extras-Gruppe (Multi-Select)
   - Extra Bacon (+€2.00)
   - Extra Käse (+€1.50)
   - Spiegelei (+€2.00)
   - Jalapeños (+€1.00)

6. Removals-Gruppe (Multi-Select)
   - Ohne Zwiebeln
   - Ohne Gurken
   - Ohne Tomate
   - Ohne Salat
```

---

## 📋 KOMPLETTE ARTIKEL-LISTE MIT DIALOGEN

### Burger (10+ Artikel)

Für JEDEN Burger (Champion, Farmers, Bacon, Cheese, etc.):

```
1. Dialog: Einzeln oder Menü?
   - Hilfstext: "Möchten Sie Ihren Burger einzeln oder als Menü?"
   - Buttons: [ Einzeln ] [ Als Menü ]

2. Dialog: Größe?
   - Hilfstext: "Welche Größe möchten Sie?"
   - Radio: ( ) Normal 100g  ( ) Medium 125g  ( ) Large 180g

3. Dialog: Menü-Komponenten (NUR wenn "Als Menü")
   - Beilage (Pflicht, Single): Pommes/Sweet Potato/Twister/Country
   - Getränk (Pflicht, Single): Cola/Fanta/Sprite/Mezzo/Water
   - Sauce (Optional, Multi): Ketchup, Mayo, BBQ, etc.

4. Dialog: Brötchen (Pflicht)
   - Hilfstext: "Welches Brötchen möchten Sie?"
   - Radio: ( ) Briochebrötchen  ( ) Semolinabrötchen

5. Dialog: Extras & Removals (Optional)
   - Extras: Extra Bacon, Extra Käse, Spiegelei, etc.
   - Removals: Ohne Zwiebeln, Ohne Gurken, etc.
```

### Salate (4+ Artikel)

Für JEDEN Salat (Caesar, Greek, Chicken, etc.):

```
1. Dialog: Dressing (Pflicht)
   - Hilfstext: "Welches Dressing möchten Sie?"
   - Radio: ( ) Caesar  ( ) Italian  ( ) Balsamico  ( ) Ohne

2. Dialog: Extras (Optional)
   - Checkboxen: Extra Parmesan, Hähnchen, Avocado
```

### Pizzabrötchen & Fingerfood

```
1. Dialog: Dips (Multi-Select)
   - Hilfstext: "Welche Dips möchten Sie? (2 inklusive)"
   - Checkboxen: Knoblauch, Kräuter, Chili, BBQ
   - Erste 2 kostenlos, ab 3. +€0.50
```

### Pasta

```
1. Dialog: Pasta-Typ (falls mehrere)
   - Hilfstext: "Welche Pasta möchten Sie?"
   - Radio: ( ) Spaghetti  ( ) Penne  ( ) Tagliatelle

2. Dialog: Sauce
   - Hilfstext: "Welche Sauce?"
   - Radio: ( ) Bolognese  ( ) Carbonara  ( ) Napoli
```

### Getränke & Beilagen (einfach)

**Keine Dialoge nötig**, direkt in Warenkorb:
- Coca Cola 0,5l → €2.50
- Pommes Frites Normal → €3.50
- etc.

---

## 🎨 UI/UX ANFORDERUNGEN

### Dialog-Design
```
- Popup-Fenster (Modal)
- Große, gut lesbare Buttons
- Touch-optimiert (min 44x44px)
- Klar erkennbare Auswahl (Häkchen, Highlight)
- "Weiter" Button immer sichtbar
- "Zurück" Button zum vorherigen Dialog
```

### Hilftexte
```
- Oben im Dialog prominent angezeigt
- Fett formatiert
- In Anführungszeichen
- Mitarbeiter sollen es wörtlich vorlesen
```

### Preis-Anzeige
```
- Immer rechts neben Option
- Format: €X.XX
- Bei Aufpreis: "+€X.XX"
- Bei inklusive: "(inklusive)" oder "€0.00"
```

---

## 📊 MODIFIER-GROUPS STRUKTUR

### Gruppe 1: Brötchen
```
Name: Brötchen-Auswahl
Typ: Single-Select (Radio-Buttons)
Pflicht: JA
Optionen:
  - Briochebrötchen (€0.00 - inklusive)
  - Semolinabrötchen (€0.00 - inklusive)
```

### Gruppe 2: Beilagen (für Menüs)
```
Name: Beilage
Typ: Single-Select (Radio-Buttons)
Pflicht: JA (nur bei Menü)
Optionen:
  - Pommes Frites Normal (€0.00 - inklusive)
  - Sweet Potato Fries (+€0.99)
  - Twister Fries (+€0.99)
  - Country Potatoes (+€0.99)
```

### Gruppe 3: Getränke (für Menüs)
```
Name: Getränk
Typ: Single-Select (Radio-Buttons)
Pflicht: JA (nur bei Menü)
Optionen:
  - Coca Cola 0,5l (€0.00 - inklusive)
  - Coca Cola Zero 0,5l (€0.00 - inklusive)
  - Fanta 0,5l (€0.00 - inklusive)
  - Mezzo Mix 0,5l (€0.00 - inklusive)
  - Sprite 0,5l (€0.00 - inklusive)
  - ViO Still 0,5l (€0.00 - inklusive)
```

### Gruppe 4: Saucen
```
Name: Saucen
Typ: Multi-Select (Checkboxen)
Pflicht: NEIN
Min: 0, Max: unbegrenzt
Optionen:
  - Ketchup (€0.00 - inklusive)
  - Mayonnaise (€0.00 - inklusive)
  - BBQ Sauce (€0.00 - inklusive)
  - Knoblauchsauce (€0.00 - inklusive)
  - Chilisauce (€0.00 - inklusive)
```

### Gruppe 5: Extras
```
Name: Extras
Typ: Multi-Select (Checkboxen)
Pflicht: NEIN
Optionen:
  - Extra Bacon (+€2.00)
  - Extra Käse (2 Scheiben) (+€1.50)
  - Extra Käse (3 Scheiben) (+€2.00)
  - Spiegelei (+€2.00)
  - Jalapeños (+€1.00)
  - Champignons (+€1.50)
  - Avocado Slices (+€2.50)
```

### Gruppe 6: Removals
```
Name: Zutaten entfernen
Typ: Multi-Select (Checkboxen)
Pflicht: NEIN
Optionen:
  - Ohne Zwiebeln (€0.00)
  - Ohne Gurken (€0.00)
  - Ohne Tomate (€0.00)
  - Ohne Salat (€0.00)
```

### Gruppe 7: Dressings (für Salate)
```
Name: Dressing
Typ: Single-Select (Radio-Buttons)
Pflicht: JA (nur bei Salaten)
Optionen:
  - Caesar Dressing (€0.00 - inklusive)
  - Italian Dressing (€0.00 - inklusive)
  - Balsamico (€0.00 - inklusive)
  - Ohne Dressing (€0.00)
```

### Gruppe 8: Dips (für Pizzabrötchen/Fingerfood)
```
Name: Dips
Typ: Multi-Select (Checkboxen)
Pflicht: NEIN
Regel: Erste 2 kostenlos, ab 3. je €0.50
Optionen:
  - Knoblauchsauce (€0.00 für 1-2, €0.50 ab 3.)
  - Kräutersauce (€0.00 für 1-2, €0.50 ab 3.)
  - Chilisauce (€0.00 für 1-2, €0.50 ab 3.)
  - BBQ Sauce (€0.00 für 1-2, €0.50 ab 3.)
  - Sour Cream (€0.00 für 1-2, €0.50 ab 3.)
```

---

## 🔢 ARTIKEL-NUMMERN (POS Item IDs)

**Wichtig:** Diese Nummern müssen im Kassensystem UND im Online-Shop-Backend identisch sein!

### Hauptartikel
```
M4;2    → Champion Burger Medium 125g
M4;1    → Champion Burger Normal 100g
M4;3    → Champion Burger Large 180g
...
```

### Modifier/Beilagen
```
998;1   → Briochebrötchen
999;1   → Semolinabrötchen
POMMES-NORMAL → Pommes Frites Normal
SWEET-POTATO → Sweet Potato Fries
TWISTER → Twister Fries
COLA-05 → Coca Cola 0,5l
...
```

**Diese IDs müssen Sie uns mitteilen oder wir geben Ihnen unsere Liste!**

---

## 📤 DATEN-OUTPUT (was ans POS geht)

### Beispiel: Champion Burger Medium Menü

**Was das Kassensystem senden sollte:**
```json
{
  "name": "Champion Burger Medium 125g Menü",
  "uid": "M4;2",
  "count": 1,
  "price": 16.09,
  "items": [
    {"uid": "998;1", "name": "+ Briochebrötchen", "count": 1, "price": 0.0},
    {"uid": "POMMES-NORMAL", "name": "+ Pommes Frites Normal", "count": 1, "price": 0.0},
    {"uid": "COLA-05", "name": "+ Coca Cola 0,5l", "count": 1, "price": 0.0},
    {"uid": "SAUCE-KETCHUP", "name": "+ Ketchup", "count": 1, "price": 0.0},
    {"uid": "EXTRA-BACON", "name": "+ Extra Bacon", "count": 1, "price": 2.0},
    {"uid": "REMOVE-ZWIEBELN", "name": "- Ohne Zwiebeln", "count": 1, "price": 0.0}
  ]
}
```

**Auf Kassenbon:**
```
Champion Burger Medium 125g Menü         M4;2   16,09€
  + Briochebrötchen                      998;1
  + Pommes Frites Normal                 POMMES-NORMAL
  + Coca Cola 0,5l                       COLA-05
  + Ketchup                              SAUCE-KETCHUP
  + Extra Bacon                          EXTRA-BACON  2,00€
  - Ohne Zwiebeln                        REMOVE-ZWIEBELN
```

---

## 🎯 WICHTIGE REGELN

### 1. Hierarchische Struktur (Verschachtelt)
```
HAUPTARTIKEL (Parent)
  ├─ Kind 1: Brötchen
  ├─ Kind 2: Beilage
  ├─ Kind 3: Getränk
  ├─ Kind 4: Sauce
  ├─ Kind 5: Extras
  └─ Kind 6: Removals
```

**NICHT flach!** Alle Komponenten als Kinder des Hauptartikels!

### 2. Preis-Logik
```
- Beilage Premium (Sweet Potato): Aufpreis €0.99
  → Im Modifier-Preis enthalten
  → NICHT extra als "Aufpreis"-Artikel

- Extras (Bacon, Käse): Aufpreis
  → Als separate Kinder mit eigenem Preis

- Erste 2 Saucen: €0.00
- Ab 3. Sauce: Eigener Preis (€0.50-€0.90)
```

### 3. Namenskonvention
```
✅ RICHTIG:
  + Twister Fries
  + Extra Bacon
  - Ohne Zwiebeln

❌ FALSCH:
  ++ Twister Fries Aufpreis
  ++ Ohne Zwiebeln Medium
```

**Präfix:**
- "+" für Extras/Zutaten
- "-" für Removals
- Kein "++" (nur ein Plus!)

### 4. Größe im Hauptnamen
```
✅ RICHTIG:
  Champion Burger Medium 125g Menü

❌ FALSCH:
  Champion Burger Menü Medium
  Champion Burger Medium 125g Menü Medium
```

**Größe kommt einmal, VOR "Menü"!**

---

## 🛠️ TECHNISCHE UMSETZUNG

### Option A: Emergen Kassensystem Features nutzen

Falls Emergent-Kassensystem diese Features hat:
- Dialog-Builder
- Modifier-Groups
- Conditional-Dialogs (nur bei Menü)
- Hilfstext-Felder

→ Bitte diese Features nutzen und genau wie beschrieben konfigurieren

### Option B: Custom-Lösung

Falls Standard-Features nicht ausreichen:
- Custom-Dialoge programmieren
- API-Integration
- Wir liefern exakte Spezifikation

### Daten-Synchronisation

**Wichtig:** Artikel, Preise, Modifier-Groups müssen synchron sein:
- Online-Shop-Backend (MongoDB)
- Kassensystem (Emergent/ExpertOrder)

**Wir können liefern:**
- Export aller Artikel als CSV/JSON
- Modifier-Groups als JSON
- Preis-Listen
- Artikel-Nummern-Mapping

---

## 📞 KONTAKT & SUPPORT

**Bei Fragen:**
- Welche Features hat das Emergent-Kassensystem?
- Können Dialoge konfiguriert werden?
- Können Hilftexte hinterlegt werden?
- Können Modifier-Groups verknüpft werden?

**Wir brauchen:**
- Zugang zur Kassensystem-Konfiguration
- Dokumentation der verfügbaren Features
- Unterstützung beim Setup

**Wir liefern:**
- Komplette Artikel-Liste (CSV/JSON)
- Modifier-Groups-Definitionen
- Dialog-Flows (detailliert)
- Hilftexte für alle Artikel
- Preis-Listen
- Artikel-Nummern-Mapping

---

## ✅ ERWARTETES ERGEBNIS

**Nach Konfiguration:**

1. ✅ Mitarbeiter tippt auf "Champion Burger"
2. ✅ Dialog öffnet: "Einzeln oder Menü?"
3. ✅ Mitarbeiter wählt basierend auf Kundenwunsch
4. ✅ Weitere Dialoge führen durch Auswahl
5. ✅ Hilftexte zeigen was zu fragen ist
6. ✅ Artikel landet korrekt im System
7. ✅ Kassenbon zeigt alle Komponenten
8. ✅ Synchron mit Online-Shop

**Kassenbons sehen aus wie Online-Bestellungen:**
- Gleiche Struktur
- Gleiche Texte
- Gleiche Artikel-Nummern
- Keine Verwechslungen

---

## 📦 NÄCHSTE SCHRITTE

**1. Prüfen Sie Kassensystem-Features:**
- Unterstützt Emergent-Kassensystem Dialoge?
- Können Modifier-Groups verknüpft werden?
- Können Hilftexte hinterlegt werden?

**2. Wir liefern Daten:**
- Artikel-Export (alle Produkte)
- Modifier-Groups (alle Optionen)
- Dialog-Definitionen (detailliert)
- Hilftexte (für jeden Artikel)

**3. Gemeinsam konfigurieren:**
- Screen-Sharing Session
- Wir zeigen Online-Shop
- Sie konfigurieren Kassensystem
- Wir testen zusammen

**4. Testing:**
- Test-Bestellung im Kassensystem
- Vergleich mit Online-Shop
- Kassenbon-Vergleich
- Feintuning

---

## 📋 ZUSAMMENFASSUNG

**Was wir brauchen von Emergent:**
- Kassensystem-Dokumentation (Features)
- Zugang zur Konfiguration
- Support bei Setup

**Was wir liefern:**
- Komplette Artikel-Struktur
- Modifier-Groups-Definitionen
- Dialog-Flows mit Hilftexten
- Preis-Listen
- Artikel-Nummern

**Ziel:**
- Kassensystem = Online-Shop (identische Struktur)
- Mitarbeiter können telefonische Bestellungen genauso aufnehmen
- Keine "???" auf Kassenbons
- Synchrone Daten

---

Erstellt: 23. Januar 2026
Version: 1.0
Status: Spezifikation für Emergent Kassensystem
Kontakt: ZOZO Burger Team

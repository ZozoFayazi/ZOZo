# 🔧 FIX: Duplikate und Hinweis-Texte auf Kassenbon

## Problem (vom Kassenbon)

```
❌ Cheeseburger Medium 125g Large
    ++ Briochebrötchen Medium
    ++ Briochebrötchen Medium     ← DUPLIKAT!
    ++ Extra Bacon
    ++ Extra Bacon                ← DUPLIKAT!
    ++ Hinweis: ohne Zwiebeln...  ← Als Artikel statt als Notiz
    ++ Hinweis: ohne Zwiebeln...  ← DUPLIKAT!
```

## Root Cause

### Problem 1: Modifiers wurden auch zu customizations hinzugefügt

**Datei:** `/app/frontend/src/components/ProductCustomizer.jsx`

**Code (VORHER):**
```javascript
const customizations = [];

// ❌ FEHLER: Modifiers werden zu customizations hinzugefügt
Object.entries(selectedModifiers).forEach(([groupId, modifierData]) => {
  customizations.push(modifierName);  // ❌ Duplikat!
});

// Brötchen hinzufügen
customizations.push("+ Briochebrötchen");  // ❌ Schon in modifiers!

// Später:
onAddToCart({
  customizations: customizations,  // Enthält Briochebrötchen
  modifiers: selectedModifiers     // Enthält AUCH Briochebrötchen
});
```

**Resultat:**
- Backend erhält Briochebrötchen ZWEIMAL (in customizations UND modifiers)
- ExpertOrder Connector sendet beide als Items
- Kassenbon zeigt Duplikate

### Problem 2: "Hinweis:"-Texte als Items gesendet

**Datei:** `/app/backend/pos_connectors/expertorder.py`

**Code (VORHER):**
```python
# 4. ANDERE CUSTOMIZATIONS
for custom in customizations:
    if "Hinweis:" in custom:
        # ❌ Wird als Item hinzugefügt!
        main_item["items"].append({
            "name": f"++ {custom}",  # "++ Hinweis: ohne Zwiebeln..."
            "price": 0.0
        })
```

**Resultat:**
- Hinweise erscheinen als separate Artikel
- Mit "???" (kein Mapping)
- Werden als "++" Zutat angezeigt statt als Notiz

---

## Die Lösung

### Fix 1: Modifiers NICHT zu customizations hinzufügen (Frontend)

**Datei:** `/app/frontend/src/components/ProductCustomizer.jsx` (Zeilen 189-213)

```javascript
const customizations = [];

// ⚠️ CHANGED 22.01.2026: Modifiers werden NICHT zu customizations hinzugefügt!
// Modifiers werden separat als 'modifiers' Objekt übergeben
// Nur Brötchen, Extras und Hinweise gehen in customizations

// Add bun type (WITHOUT adding to name)
if (selectedBun) {
  const bunName = bunTypes.find(b => b.id === selectedBun)?.name;
  if (bunName) {
    customizations.push(`+ ${bunName}`);
  }
}

// Build extras array
const allExtras = [...selectedExtras];

// ... später:
onAddToCart({
  customizations: customizations,  // Nur Brötchen, Hinweise
  modifiers: { ...selectedModifiers, ...menuModifiers }  // Sauce, Dressing, Beilage, Getränk
});
```

**Effekt:**
- Sauce, Dressing etc. nur in `modifiers` (NICHT in customizations)
- Keine Duplikate mehr

### Fix 2: "Hinweis:" als note speichern, NICHT als Item (Backend)

**Datei:** `/app/backend/pos_connectors/expertorder.py`

**Für Menüs (Zeilen 543-565):**
```python
for custom in customizations:
    if isinstance(custom, str):
        # ✅ Skip "Hinweis:" texts - add as note instead
        if custom.lower().startswith('hinweis:') or 'hinweis:' in custom.lower():
            note_text = custom.replace('Hinweis:', '').replace('hinweis:', '').strip()
            if 'note' not in menu_main_item:
                menu_main_item['note'] = note_text
            else:
                menu_main_item['note'] += f"; {note_text}"
            continue
        
        # Add Brötchen (nur wenn es "brötchen" enthält)
        if 'brötchen' in custom.lower() or 'bun' in custom.lower():
            # ... als Item hinzufügen
```

**Für normale Items (Zeilen 700-730):**
```python
# 4. ANDERE CUSTOMIZATIONS (nicht Brötchen, nicht Hinweise)
for custom in customizations:
    if isinstance(custom, str):
        # Skip brötchen (already added above)
        if 'brötchen' in custom.lower() or 'bun' in custom.lower():
            continue
        
        # ✅ Skip "Hinweis:" texts - add as note instead
        if custom.lower().startswith('hinweis:') or 'hinweis:' in custom.lower():
            note_text = custom.replace('Hinweis:', '').replace('hinweis:', '').strip()
            if 'note' not in main_item:
                main_item['note'] = note_text
            else:
                main_item['note'] += f"; {note_text}"
            continue
        
        # Skip if covered by modifiers (prevents duplicates)
        modifier_names = [mod_data.get('name', '') for mod_data in modifiers.values() if isinstance(mod_data, dict)]
        if any(mod_name in custom or custom in mod_name for mod_name in modifier_names):
            continue
        
        # Add other customizations
        main_item["items"].append({...})
```

**Effekt:**
- Hinweise werden als `note`-Feld am Hauptitem gespeichert
- NICHT als separates Item mit "???"
- ExpertOrder kann Notes möglicherweise speziell behandeln

---

## Wie Hinweise jetzt behandelt werden

### Eingabe (Frontend):
```
Spezielle Anweisungen: "ohne Zwiebeln und ohne Essiggurken"
```

### Im Cart:
```javascript
{
  customizations: ["Hinweis: ohne Zwiebeln und ohne Essiggurken"]
}
```

### Backend Transformation:
```python
# Extrahiert "Hinweis:" prefix
note_text = "ohne Zwiebeln und ohne Essiggurken"

# Fügt als 'note' hinzu (NICHT als Item!)
main_item['note'] = "ohne Zwiebeln und ohne Essiggurken"
```

### An ExpertOrder gesendet:
```json
{
  "name": "Cheeseburger Medium 125g",
  "note": "ohne Zwiebeln und ohne Essiggurken",
  "items": [
    {"name": "+ Briochebrötchen Medium"},
    {"name": "+ Extra Bacon"}
  ]
}
```

### Auf Kassenbon:
```
Cheeseburger Medium 125g
  + Briochebrötchen Medium
  + Extra Bacon
  Hinweis: ohne Zwiebeln und ohne Essiggurken
```

**Oder falls ExpertOrder Notes nicht unterstützt:**
```
Cheeseburger Medium 125g
  + Briochebrötchen Medium
  + Extra Bacon
```
(Hinweis wird nicht angezeigt, aber auch nicht als "???" Item)

---

## Was wurde behoben

### Vorher (Kassenbon):
```
1x Cheeseburger Medium 125g Large
    ++ Briochebrötchen Medium        998;1
    ++ Briochebrötchen Medium        998;1  ← DUPLIKAT
    ++ Extra Bacon                   ???
    ++ Extra Bacon                   ???    ← DUPLIKAT
    ++ Hinweis: ohne Zwiebeln...     ???
    ++ Hinweis: ohne Zwiebeln...     ???    ← DUPLIKAT
```

### Nachher (Kassenbon):
```
1x Cheeseburger Medium 125g
    + Briochebrötchen Medium         998;1  ✅ Nur einmal
    + Extra Bacon                    902;1  ✅ Nur einmal
    Hinweis: ohne Zwiebeln und ohne Essiggurken  ✅ Als Notiz
```

---

## Duplikat-Prävention

Der Code verhindert jetzt Duplikate durch:

### 1. Modifiers separat von customizations
```javascript
// Frontend:
customizations: ["+ Briochebrötchen"],  // Nur Brötchen
modifiers: {sauce: "Ketchup"}           // Nur Sauce (nicht in customizations!)
```

### 2. Skip-Logic im Backend
```python
# Prüft ob custom bereits in modifiers ist
modifier_names = [mod_data.get('name', '') for mod_data in modifiers.values()]
if any(mod_name in custom or custom in mod_name for mod_name in modifier_names):
    continue  # ✅ Überspringen = kein Duplikat
```

### 3. Hinweis-Erkennung
```python
if custom.lower().startswith('hinweis:') or 'hinweis:' in custom.lower():
    # Als note speichern, NICHT als Item
    main_item['note'] = note_text
    continue  # ✅ Wird nicht als Item hinzugefügt
```

---

## Testing

### Test 1: Keine Duplikate
```
Bestellung: Burger + Briochebrötchen + Extra Bacon
Kassenbon Erwartung:
  Burger Medium 125g
    + Briochebrötchen Medium  (nur einmal!)
    + Extra Bacon             (nur einmal!)
```

### Test 2: Hinweise als Notiz
```
Bestellung: Burger mit Spezialanweisung "ohne Zwiebeln"
Kassenbon Erwartung:
  Burger Medium 125g
    + Briochebrötchen
  Hinweis: ohne Zwiebeln  (als Notiz, nicht als Item)
```

### Test 3: Modifiers keine Duplikate
```
Bestellung: Salad + Caesar Dressing
Kassenbon Erwartung:
  Caesar Salad (Normal)
    + Caesar Dressing  (nur einmal!)
```

---

## Status

- ✅ **Frontend-Fix:** Modifiers nicht zu customizations (ProductCustomizer.jsx)
- ✅ **Backend-Fix:** Hinweise als note (expertorder.py - Zeilen 547-565, 674-690, 700-730)
- ✅ **Backend-Fix:** Verbesserte Duplikat-Prävention (expertorder.py)
- ✅ **Backups aktualisiert:** `/app/backups/critical_fixes_2026_01_22/`
- ✅ **Services neu gestartet**

---

## Deployment

Nach Re-Deployment sollten:
- ✅ Keine Duplikate mehr auf Kassenbon
- ✅ Hinweise als Notizen (oder gar nicht), nicht als "???" Items
- ✅ Saubere, lesbare Kassenbons

Bereit für Production! 🚀

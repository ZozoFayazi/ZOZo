# ✅ Größenangaben für ALLE Artikel ans Kassensystem

## Änderung

**ALLE Artikel werden jetzt MIT Größe ans Kassensystem gesendet, nicht nur Burger!**

---

## Vorher vs. Nachher

### Burger (bereits korrekt)
```
VORHER: Champion Burger Medium 125g ✅
NACHHER: Champion Burger Medium 125g ✅ (unverändert)
```

### Wings, Salate, Fingerfood (NEU verbessert)
```
VORHER: Crunchy Wings (ohne Größe)
NACHHER: Crunchy Wings Medium ✅

VORHER: Caesar Salad (ohne Größe)
NACHHER: Caesar Salad Normal ✅

VORHER: Onion Rings (ohne Größe)
NACHHER: Onion Rings Large ✅
```

---

## Implementierung

**Datei:** `/app/backend/pos_connectors/expertorder.py`

**Code (Zeilen 647-685):**

```python
# Für ALLE Produkte: Größe hinzufügen wenn vorhanden
if item_size:
    size_upper = item_size.upper()
    
    # Burger & Smash: Mit Grammzahl
    if is_burger:
        if size_upper == 'MEDIUM':
            full_name = f"{item_name} Medium 125g"
        elif size_upper == 'LARGE':
            full_name = f"{item_name} Large 180g"
        elif size_upper == 'NORMAL':
            full_name = f"{item_name} Normal 100g"
    else:
        # Alle anderen Produkte: Größe direkt
        if size_upper == 'MEDIUM':
            full_name = f"{item_name} Medium"
        elif size_upper == 'LARGE':
            full_name = f"{item_name} Large"
        elif size_upper == 'NORMAL':
            full_name = f"{item_name} Normal"
```

---

## Beispiele

### Crunchy Wings
```
Normal:  "Crunchy Wings Normal"
Medium:  "Crunchy Wings Medium"
Large:   "Crunchy Wings Large"
```

### Caesar Salad
```
Normal:  "Caesar Salad Normal"
Large:   "Caesar Salad Large"
```

### Onion Rings
```
Normal:  "Onion Rings Normal"
Large:   "Onion Rings Large"
```

### Pizzabrötchen
```
6 Stück:   "Pizzabrötchen 6 Stück"  (Größe = Stückzahl)
12 Stück:  "Pizzabrötchen 12 Stück"
```

---

## Kassenbon-Beispiele

**VORHER (ohne Größe):**
```
1x Crunchy Wings
   ++ Knoblauch Sauce
```

**NACHHER (mit Größe):**
```
1x Crunchy Wings Medium
   + Knoblauch Sauce
```

---

**VORHER:**
```
1x Caesar Salad
   + Caesar Dressing
```

**NACHHER:**
```
1x Caesar Salad Normal
   + Caesar Dressing
```

---

## Für Menüs (bereits korrekt)

**Burger-Menüs:**
```
Champion Burger Medium 125g Menü  ✅
Champion Burger Large 180g Menü   ✅
Champion Burger Normal 100g Menü  ✅
```

**Wings-Menü (falls vorhanden):**
```
Crunchy Wings Medium Menü  ✅
```

---

## Status

- ✅ **Implementiert:** Größe für ALLE Produkt-Typen
- ✅ **Backend:** Neu gestartet
- ⏳ **Deployment:** Erforderlich

---

## Nach Re-Deployment

**Alle Kassenbons zeigen:**
```
✅ Burger Medium 125g
✅ Wings Medium
✅ Salad Normal
✅ Onion Rings Large
✅ Pizzabrötchen 6 Stück
```

**KEINE Artikel ohne Größenangabe mehr!**

---

Datum: 23.01.2026
Status: Implementiert, wartet auf Deployment

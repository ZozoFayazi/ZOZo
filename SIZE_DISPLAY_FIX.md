# Größen-Anzeige auf Kassenbon - Verbesserung

## Anforderung

**Kunde wünscht:** Die Größe soll **IMMER** auf dem Kassenbon erscheinen, sowohl bei normalen Artikeln als auch bei Menüs - auch wenn "Normal" gewählt wurde.

## Vorher

### Menüs:
```
Champion Burger Menü          ❌ Keine Größe bei "Normal"
Champion Burger Medium 125g Menü  ✅ Nur bei Medium/Large
Champion Burger Large 180g Menü   ✅ Nur bei Medium/Large
```

### Normale Burger:
```
Champion Burger              ❌ Keine Größe bei "Normal"
Champion Burger Medium 125g  ✅ Nur bei Medium/Large
```

## Nachher

### Menüs:
```
Champion Burger Normal 100g Menü   ✅ Größe IMMER angezeigt
Champion Burger Medium 125g Menü   ✅ Größe IMMER angezeigt
Champion Burger Large 180g Menü    ✅ Größe IMMER angezeigt
```

### Normale Burger:
```
Champion Burger Normal 100g   ✅ Größe IMMER angezeigt
Champion Burger Medium 125g   ✅ Größe IMMER angezeigt
Champion Burger Large 180g    ✅ Größe IMMER angezeigt
```

### Andere Produkte (Salate, Beilagen, etc.):
```
Caesar Salad (Normal)   ✅ Größe wird angezeigt
Pommes Frites (Large)   ✅ Größe wird angezeigt
```

## Implementierung

**Datei:** `/app/backend/pos_connectors/expertorder.py`

### Änderung 1: Menü-Items (Zeilen 502-530)

**VORHER:**
```python
if item_size and item_size.lower() != 'normal':
    # Nur bei Medium/Large Größe hinzufügen
    if size_upper == 'MEDIUM':
        size_with_weight = 'Medium 125g'
    elif size_upper == 'LARGE':
        size_with_weight = 'Large 180g'
```

**NACHHER:**
```python
if item_size:  # ✅ IMMER (auch bei Normal)
    size_upper = item_size.upper()
    
    # Add gram weight based on size (IMMER, auch bei Normal)
    if size_upper == 'MEDIUM':
        size_with_weight = 'Medium 125g'
    elif size_upper == 'LARGE':
        size_with_weight = 'Large 180g'
    elif size_upper == 'NORMAL':  # ✅ NEU
        size_with_weight = 'Normal 100g'
    else:
        size_with_weight = item_size.capitalize()
    
    # Insert before "Menü"
    if 'menü' in item_name.lower():
        base_name = item_name.replace(' Menü', '').replace(' Menu', '').strip()
        full_name = f"{base_name} {size_with_weight} Menü"
else:
    # Kein size-Feld vorhanden - verwende Original-Namen
    full_name = item_name
```

### Änderung 2: Normale Burger (Zeilen 630-656)

**VORHER:**
```python
if is_burger and item_size and item_size.lower() != 'normal':
    # Nur bei Medium/Large
    if size_upper == 'MEDIUM':
        full_name = f"{item_name} Medium 125g"
    elif size_upper == 'LARGE':
        full_name = f"{item_name} Large 180g"
elif item_size and item_size.lower() != 'normal':
    # Andere Produkte: nur non-normal
    full_name = f"{item_name} ({item_size})"
```

**NACHHER:**
```python
if is_burger and item_size:  # ✅ IMMER (auch bei Normal)
    size_upper = item_size.upper()
    if size_upper == 'MEDIUM':
        full_name = f"{item_name} Medium 125g"
    elif size_upper == 'LARGE':
        full_name = f"{item_name} Large 180g"
    elif size_upper == 'NORMAL':  # ✅ NEU
        full_name = f"{item_name} Normal 100g"
    else:
        full_name = f"{item_name} {item_size}"
elif item_size and item_size.lower() != 'normal':
    # Andere Produkte: nur non-normal
    full_name = f"{item_name} ({item_size})"
elif item_size and item_size.lower() == 'normal':  # ✅ NEU
    # Auch Normal-Größe bei nicht-Burgern anzeigen
    full_name = f"{item_name} (Normal)"
```

## Größen-Schema

### Burger & Menüs:
- **Normal:** `100g` (NEU)
- **Medium:** `125g` (unverändert)
- **Large:** `180g` (unverändert)

### Andere Produkte:
- **Normal:** `(Normal)` in Klammern
- **Medium/Large:** `(Medium)` / `(Large)` in Klammern

## Beispiele

### Vor dem Fix:

```
Champion Burger Menü               → Unklar welche Größe
Caesar Salad                       → Unklar welche Größe
Pommes Frites                      → Unklar welche Größe
```

### Nach dem Fix:

```
Champion Burger Normal 100g Menü   → ✅ Klar erkennbar
Champion Burger Medium 125g Menü   → ✅ Klar erkennbar
Caesar Salad (Normal)              → ✅ Größe sichtbar
Pommes Frites (Large)              → ✅ Größe sichtbar
```

## Kassenbon-Beispiel

**Bestellung:**
- 1x Champion Burger Normal Menü
  - Pommes, Cola, Ketchup
- 1x Caesar Salad Normal
  - Caesar Dressing

**Kassenbon (VORHER):**
```
1x Champion Burger Menü              ??? 15,50€
1x Caesar Salad                      ??? 9,19€
```

**Kassenbon (NACHHER):**
```
1x Champion Burger Normal 100g Menü  M4;1 15,50€
     + Pommes Frites Normal
     + Coca Cola 0,5l
     + Ketchup
1x Caesar Salad (Normal)             S1;1 9,19€
     + Caesar Dressing
```

## Vorteile

✅ **Klarheit:** Küche weiß sofort, welche Größe zubereiten
✅ **Keine Verwechslungen:** Unterschied zwischen 100g, 125g, 180g klar
✅ **Konsistenz:** Größe wird IMMER angezeigt, nicht nur manchmal
✅ **POS-Kompatibilität:** ExpertOrder kann Größen besser matchen

## Testing

### Test 1: Normal-Burger-Menü
```
Bestellung: Champion Burger Normal Menü
Erwartung: "Champion Burger Normal 100g Menü"
```

### Test 2: Medium-Burger
```
Bestellung: Champion Burger Medium (kein Menü)
Erwartung: "Champion Burger Medium 125g"
```

### Test 3: Normal-Salad
```
Bestellung: Caesar Salad Normal
Erwartung: "Caesar Salad (Normal)"
```

### Test 4: Large-Pommes
```
Bestellung: Pommes Frites Large
Erwartung: "Pommes Frites (Large)"
```

## Deployment

**Datei geändert:**
- `/app/backend/pos_connectors/expertorder.py`

**Service-Neustart:**
```bash
supervisorctl restart backend
```

**Status:**
- ✅ Implementiert
- ✅ Backend neu gestartet
- ✅ Bereit für Testing

## Zusammenfassung

**Problem:** Größe wurde nur bei Medium/Large angezeigt, nicht bei Normal

**Lösung:** Größe wird IMMER angezeigt:
- Burger: "Normal 100g", "Medium 125g", "Large 180g"
- Andere: "(Normal)", "(Medium)", "(Large)"

**Resultat:** Kassenbon zeigt immer die vollständige Produktbezeichnung mit Größe

Nach Re-Deployment sollten alle Bestellungen die Größe korrekt auf dem Kassenbon zeigen! 📋✅

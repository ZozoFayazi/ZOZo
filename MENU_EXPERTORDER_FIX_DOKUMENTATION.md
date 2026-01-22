# Menü-Struktur ExpertOrder Fix - 22. Januar 2026

## Problem

Menü-Bestellungen (z.B. "Champion Burger Medium 125g Menü") wurden nicht korrekt an ExpertOrder übertragen:

- ❌ Auf dem Kassenbon erschien nur: "Champion Burger Medium 125g Menü"
- ❌ **OHNE** Beilage (Pommes)
- ❌ **OHNE** Getränk (Cola)
- ❌ **OHNE** Sauce (Ketchup, Mayo, etc.)
- ❌ Artikel-Nummern zeigten "???" (nicht gemappt)

## Root Cause Analysis

### Bug 1: Sauce wurde nicht an POS gesendet

**Datei:** `/app/backend/pos_connectors/expertorder.py`

**Problem:** 
In der Funktion `_transform_order_to_eocloud()` wurden nur `beilage` und `getraenk` aus den `modifiers` extrahiert, aber **NICHT `sauce`**.

**Code-Location:** Zeilen 575-608

**Original Code:**
```python
# 5. BEILAGE (aus modifiers) → als Kind hinzufügen
if modifiers:
    for group_id, modifier_data in modifiers.items():
        if isinstance(modifier_data, dict):
            is_side = any(keyword in group_id.lower() for keyword in ['beilage', 'side', 'pommes', 'fries'])
            if is_side:
                # ... add to menu_main_item["items"]

# 6. GETRÄNK (aus modifiers) → als Kind hinzufügen
for group_id, modifier_data in modifiers.items():
    if isinstance(modifier_data, dict):
        is_drink = any(keyword in group_id.lower() for keyword in ['getraenk', 'getr', 'drink', 'beverage'])
        if is_drink:
            # ... add to menu_main_item["items"]

# ❌ SAUCE FEHLTE HIER!
```

**Fix (IMPLEMENTIERT):**
```python
# 7. SAUCE/DIP (aus modifiers) → als Kind hinzufügen
for group_id, modifier_data in modifiers.items():
    if isinstance(modifier_data, dict):
        is_sauce = any(keyword in group_id.lower() for keyword in ['sauce', 'dip', 'soße', 'dressing'])
        
        if is_sauce:
            modifier_name = modifier_data.get('name', '')
            modifier_price = modifier_data.get('price', 0.0)
            pos_item_id = modifier_data.get('pos_item_id', '')
            
            menu_main_item["items"].append({
                "uid": pos_item_id or f"SAUCE-{group_id}",
                "name": f"+ {modifier_name}",
                "count": item.get('quantity', 1),
                "price": float(modifier_price)
            })
```

### Bug 2: POS Push History wurde nicht gespeichert

**Datei:** `/app/backend/pos_service.py`

**Problem:**
Die `pos_push_history` wurde nie in die Datenbank geschrieben. Es wurde nur `pos_status`, `pos_order_id` etc. aktualisiert.

**Fix (IMPLEMENTIERT):**

**Bei Erfolg (Zeile 239-285):**
```python
if order_oid:
    # Save push history entry
    push_history_entry = {
        "timestamp": datetime.now(timezone.utc),
        "status": "success",
        "provider": provider,
        "pos_order_id": result.get('pos_order_id'),
        "message": result.get('message', 'Successfully sent to POS'),
        "attempt": attempt,
        "payload": order_data  # ✅ Speichert was gesendet wurde!
    }
    
    await self.db.orders.update_one(
        {"_id": order_oid},
        {
            "$set": {...},
            "$push": {
                "pos_push_history": push_history_entry  # ✅ Wird jetzt gespeichert!
            }
        }
    )
```

**Bei Fehler (Zeile 309-335):**
```python
if order_oid:
    # Save failed push history entry
    push_history_entry = {
        "timestamp": datetime.now(timezone.utc),
        "status": "failed",
        "provider": provider,
        "message": last_error,
        "error_type": last_error_type,
        "attempts": total_attempts,
        "payload": order_data
    }
    
    await self.db.orders.update_one(
        {"_id": order_oid},
        {
            "$set": {...},
            "$push": {
                "pos_push_history": push_history_entry  # ✅ Auch bei Fehler!
            }
        }
    )
```

## Korrekte Datenstruktur

### In der Datenbank (Order Document)

```json
{
  "order_id": "ZOZO-1234",
  "items": [
    {
      "name": "Champion Burger Medium 125g Menü",
      "price": 16.09,
      "quantity": 1,
      "size": "medium",
      "modifiers": {
        "beilage": {
          "name": "Pommes Frites Normal",
          "price": 0.0,
          "pos_item_id": "POMMES-NORMAL"
        },
        "getraenk": {
          "name": "Coca Cola 0,5l",
          "price": 0.0,
          "pos_item_id": "COLA-05"
        },
        "sauce": {
          "name": "Ketchup",
          "price": 0.0,
          "pos_item_id": "SAUCE-KETCHUP"
        }
      },
      "customizations": ["+ Sesam Brötchen"],
      "removed_ingredients": ["Zwiebeln", "Gurken"]
    }
  ]
}
```

### An ExpertOrder gesendet (transformiert)

```json
{
  "version": 1,
  "id": "ZOZO-1234",
  "items": [
    {
      "uid": "BURGER-CHAMPION-MEDIUM",
      "name": "Champion Burger Medium 125g Menü",
      "count": 1,
      "price": 16.09,
      "items": [
        {
          "uid": "BUN-SESAM-BROTCHEN",
          "name": "+ Sesam Brötchen",
          "count": 1,
          "price": 0.0
        },
        {
          "uid": "REMOVE-ZWIEBELN",
          "name": "- Ohne Zwiebeln",
          "count": 1,
          "price": 0.0
        },
        {
          "uid": "REMOVE-GURKEN",
          "name": "- Ohne Gurken",
          "count": 1,
          "price": 0.0
        },
        {
          "uid": "POMMES-NORMAL",
          "name": "+ Pommes Frites Normal",
          "count": 1,
          "price": 0.0
        },
        {
          "uid": "COLA-05",
          "name": "+ Coca Cola 0,5l",
          "count": 1,
          "price": 0.0
        },
        {
          "uid": "SAUCE-KETCHUP",
          "name": "+ Ketchup",
          "count": 1,
          "price": 0.0
        }
      ]
    }
  ]
}
```

## Deployment-Checklist

Um sicherzustellen, dass die Fixes im Production-System aktiv sind:

### 1. Code-Dateien prüfen

```bash
# Prüfen, ob die Sauce-Logic existiert
grep -A 10 "SAUCE/DIP" /app/backend/pos_connectors/expertorder.py

# Prüfen, ob pos_push_history gespeichert wird
grep -A 5 "pos_push_history" /app/backend/pos_service.py
```

### 2. Backend neu starten

```bash
supervisorctl restart backend
```

### 3. Test-Bestellung aufgeben

1. Menü bestellen (z.B. Champion Burger Medium Menü)
2. Beilage wählen (Pommes)
3. Getränk wählen (Cola)
4. Sauce wählen (Ketchup)
5. Bestellung absenden

### 4. Validierung

**In der Datenbank prüfen:**

```python
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017')
db = client['test_database']

# Neueste Bestellung holen
order = db.orders.find_one(sort=[('created_at', -1)])

# Prüfen: Sind modifiers vollständig?
print(order['items'][0]['modifiers'])
# Sollte enthalten: beilage, getraenk, sauce

# Prüfen: Wurde pos_push_history gespeichert?
print(order.get('pos_push_history', []))
# Sollte mindestens 1 Eintrag haben

# Prüfen: Was wurde an POS gesendet?
if order.get('pos_push_history'):
    latest_push = order['pos_push_history'][-1]
    payload = latest_push.get('payload', {})
    print(payload['items'][0])  # Sollte verschachtelte Struktur zeigen
```

**Auf dem Kassenbon prüfen:**
- ✅ "Champion Burger Medium 125g Menü" als Hauptitem
- ✅ "+ Pommes Frites Normal" als Unterpunkt
- ✅ "+ Coca Cola 0,5l" als Unterpunkt
- ✅ "+ Ketchup" als Unterpunkt
- ✅ "- Ohne Zwiebeln" (falls gewählt)
- ✅ "- Ohne Gurken" (falls gewählt)

## Status

- ✅ **Bug 1 (Sauce fehlt):** GEFIXT in `/app/backend/pos_connectors/expertorder.py`
- ✅ **Bug 2 (pos_push_history fehlt):** GEFIXT in `/app/backend/pos_service.py`
- ⚠️ **Deployment:** Code-Updates müssen auf Production-System deployed werden
- ⏳ **Testing:** Wartet auf Bestätigung durch Test-Bestellung

## Wichtige Hinweise

1. **Dieser Fix gilt nur für die verschachtelte ExpertOrder-Struktur!**
   - Menü-Items haben ein `items`-Array mit allen Komponenten als Kinder
   - Das ist die korrekte Struktur für ExpertOrder OSP API

2. **POS Item Mapping muss konfiguriert sein:**
   - Jede Beilage, jedes Getränk, jede Sauce braucht eine `pos_item_id`
   - Diese wird in den `modifier_groups` oder `menu_items` konfiguriert
   - Ohne Mapping erscheinen "???" auf dem Bon

3. **OrderValidator bleibt aktiv:**
   - Der `OrderValidator` prüft weiterhin alle Bestellungen vor dem Senden
   - Automatische Konvertierung (`OrderAutoConverter`) läuft vor jedem Push
   - Logs zeigen an, wenn Probleme erkannt werden

## Kontakt bei Problemen

Falls nach dem Deployment weiterhin Probleme auftreten:

1. **Backend-Logs prüfen:**
   ```bash
   tail -n 100 /var/log/supervisor/backend.err.log | grep -E "POS|order|menu"
   ```

2. **pos_push_history aus Datenbank extrahieren** (siehe Validierung oben)

3. **OrderValidator-Meldungen prüfen:**
   - Logs zeigen Validation-Fehler und Auto-Conversion-Attempts
   - "✅ Order validation passed!" = Alles korrekt
   - "⚠️ Validation failed, attempting auto-conversion" = Problem erkannt, wird versucht zu fixen

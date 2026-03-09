# 🔒 EXPERTORDER TESTBESTELLUNGEN - NUR KORREKTES FORMAT!

**DATUM:** 22. Januar 2026, 14:30 Uhr  
**STATUS:** ✅ VERIFIZIERT & EINGEFROREN  
**LETZTE ERFOLGREICHE BESTELLUNG:** TEST-MONSTERBACON-CFD6694D

---

## ⚠️ KRITISCH: NUR DIESES FORMAT VERWENDEN!

**ALLE ANDEREN FORMATE SIND FALSCH UND FÜHREN ZU FEHLERN!**

---

## ✅ **KORREKTES FORMAT (SO MUSS ES SEIN!):**

### **Menü-Bestellung:**

```python
{
    "order_id": "TEST-MONSTERBACON-CFD6694D",
    "customer_name": "Test Kunde",
    "customer_email": "test@example.com",
    "customer_phone": "+49...",
    "location_id": "rellingen",  # oder "henstedt-ulzburg"
    "delivery_address": "Straße, PLZ Ort",
    "payment_method": "Karte",
    "status": "new",
    "created_at": datetime.now(timezone.utc),
    "items": [
        {
            "menu_item_id": "UNIQUE-ID-123",
            "name": "Monsterbacon Burger Menü",  # ← OHNE Größe! Connector fügt hinzu
            "size": "medium",  # ← medium = 125g, large = 180g
            "quantity": 1,
            "price": 14.90,
            
            # 1. BRÖTCHEN → customizations Array
            "customizations": [
                "+ Brioche Brötchen"  # Mit + Prefix!
            ],
            
            # 2. REMOVALS → removed_ingredients Array
            "removed_ingredients": [
                "Gurken",      # OHNE "Ohne" oder "-" Prefix!
                "Zwiebeln"
            ],
            
            # 3. EXTRAS → extras Array (Objekte!)
            "extras": [
                {"name": "Extra Bacon", "price": 0.0},
                {"name": "Extra Käse", "price": 1.0}
            ],
            
            # 4. BEILAGE/GETRÄNK/SAUCE → modifiers Objekt
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
            }
        }
    ],
    "subtotal": 14.90,
    "delivery_fee": 2.50,
    "total": 17.40
}
```

---

## ❌ **FALSCHES FORMAT (NIEMALS VERWENDEN!):**

### **❌ FALSCH - Alles in customizations:**

```python
# FALSCH! Führt zu fehlenden Children in ExpertOrder!
{
    "name": "Burger Menü",
    "customizations": [
        "+ Brioche Brötchen",
        "+ Pommes Frites",      # ← FALSCH! Muss in modifiers.beilage
        "+ Cola",               # ← FALSCH! Muss in modifiers.getraenk
        "+ Ketchup",            # ← FALSCH! Muss in modifiers.sauce
        "+ Extra Bacon",        # ← FALSCH! Muss in extras Array
        "- Ohne Gurken"         # ← FALSCH! Muss in removed_ingredients
    ]
}
```

**Resultat:** Nur Brötchen wird als Child gesendet, REST FEHLT! ❌

### **❌ FALSCH - menu_components Objekt:**

```python
# FALSCH! Connector kennt menu_components nicht!
{
    "name": "Burger Menü",
    "menu_components": {  # ← FALSCH! Existiert nicht im Connector
        "bun": "Sesame Bun",
        "side": "Pommes",
        "drink": "Cola"
    }
}
```

**Resultat:** Alle Components werden ignoriert! ❌

---

## ✅ **KORREKTE FELD-ZUORDNUNG:**

| Was | Wohin | Format | Beispiel |
|-----|-------|--------|----------|
| **Brötchen-Wahl** | `customizations` Array | String mit "+ " | `["+ Brioche Brötchen"]` |
| **Removals (Ohne...)** | `removed_ingredients` Array | String OHNE Prefix | `["Gurken", "Zwiebeln"]` |
| **Extras** | `extras` Array | Objekt mit name/price | `[{"name": "Extra Bacon", "price": 0.0}]` |
| **Beilage** | `modifiers.beilage` Objekt | Objekt mit name/price/pos_item_id | `{"name": "Pommes...", "price": 0.0}` |
| **Getränk** | `modifiers.getraenk` Objekt | Objekt mit name/price/pos_item_id | `{"name": "Cola...", "price": 0.0}` |
| **Sauce** | `modifiers.sauce` Objekt | Objekt mit name/price/pos_item_id | `{"name": "Ketchup", "price": 0.0}` |

---

## 📏 **GRÖßEN-HANDLING:**

**Connector fügt automatisch Größe + Gewicht hinzu:**

| size in DB | Name im POS |
|------------|-------------|
| `"medium"` | "... Medium 125g Menü" |
| `"large"` | "... Large 180g Menü" |
| `"normal"` | "... Menü" (keine Größe) |

**WICHTIG:** 
- Name in DB: `"Monsterbacon Burger Menü"` (OHNE Größe!)
- size-Feld: `"medium"`
- Connector erstellt: `"Monsterbacon Burger Medium 125g Menü"`

---

## 🧪 **TESTBESTELLUNG ERSTELLEN - VORLAGE:**

**Kopieren Sie dieses Template für neue Tests:**

```python
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime, timezone
import uuid

async def create_test_order():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    
    order = {
        "order_id": f"TEST-{str(uuid.uuid4())[:8].upper()}",
        "customer_name": "Test Kunde",
        "customer_email": "test@zozo.de",
        "customer_phone": "+49 40 12345678",
        "location_id": "rellingen",
        "delivery_address": "Teststraße 1, 25462 Rellingen",
        "payment_method": "Karte",
        "status": "new",
        "created_at": datetime.now(timezone.utc),
        "items": [
            {
                "menu_item_id": f"ITEM-{uuid.uuid4().hex[:8]}",
                "name": "PRODUKTNAME Menü",  # OHNE Größe!
                "size": "medium",  # medium=125g, large=180g
                "quantity": 1,
                "price": 14.90,
                
                # NUR Brötchen hier:
                "customizations": [
                    "+ Brioche Brötchen"
                ],
                
                # Removals hier (OHNE "Ohne" Prefix):
                "removed_ingredients": [
                    "Gurken",
                    "Zwiebeln"
                ],
                
                # Extras hier (als Objekte):
                "extras": [
                    {"name": "Extra Bacon", "price": 0.0}
                ],
                
                # Beilage/Getränk/Sauce hier:
                "modifiers": {
                    "beilage": {"name": "Pommes Frites Normal", "price": 0.0},
                    "getraenk": {"name": "Coca Cola 0,5l", "price": 0.0},
                    "sauce": {"name": "Ketchup", "price": 0.0}
                }
            }
        ],
        "subtotal": 14.90,
        "delivery_fee": 2.50,
        "total": 17.40
    }
    
    await db.orders.insert_one(order)
    
    # Send to POS
    from pos_service import POSService
    pos_service = POSService(db)
    await pos_service.push_order(order, "rellingen")
    
    print(f"✅ Testbestellung erstellt & gesendet: {order['order_id']}")
    
    client.close()

asyncio.run(create_test_order())
```

---

## 🚨 **REGELN FÜR TESTBESTELLUNGEN:**

### ✅ **IMMER SO:**

1. **Name OHNE Größe:** "Produktname Menü" (nicht "... Medium 125g Menü")
2. **size-Feld verwenden:** `"medium"` oder `"large"`
3. **Brötchen in customizations:** `["+ Brioche Brötchen"]`
4. **Removals in removed_ingredients:** `["Gurken"]` (OHNE Prefix!)
5. **Extras in extras:** `[{"name": "Extra Bacon", "price": 0.0}]`
6. **Beilage/Getränk/Sauce in modifiers:** Objekte mit name/price

### ❌ **NIEMALS SO:**

1. ❌ Alles in customizations Array
2. ❌ "Medium 125g" im name-Feld
3. ❌ menu_components Objekt
4. ❌ "- Ohne Gurken" in customizations (gehört in removed_ingredients)
5. ❌ "Extra Bacon" String (muss Objekt sein)

---

## 🔍 **VERIFIKATION:**

**Aktuelle Testbestellung:**
- Order ID: `TEST-MONSTERBACON-CFD6694D`
- Status: ✅ Gesendet
- Format: ✅ Korrekt
- Erscheint in Rellingen: Bitte prüfen

**Erwartetes Ergebnis in ExpertOrder:**
```
Monsterbacon Burger Medium 125g Menü
  └─ + Brioche Brötchen
  └─ - Ohne Gurken
  └─ - Ohne Zwiebeln
  └─ + Extra Bacon
  └─ + Pommes Frites Normal
  └─ + Coca Cola 0,5l
  └─ + Ketchup
```

---

## 📋 **SCHNELL-REFERENZ:**

**Für neue Testbestellungen:**
1. Verwende Template oben
2. Passe an: name, size, customizations, removed_ingredients, extras, modifiers
3. Sende an: "rellingen" oder "henstedt-ulzburg"
4. Prüfe in ExpertOrder POS

**Bei Problemen:**
1. Prüfe Format gegen diese Dokumentation
2. Prüfe `/app/EXPERTORDER_STRUKTUR_NICHT_AENDERN.md`
3. Prüfe POS Fehler-Queue: `/admin/pos/failed-orders`

---

**ERSTELLT:** 22. Januar 2026, 14:35 Uhr  
**STATUS:** 🔒 EINGEFROREN - NUR DIESES FORMAT VERWENDEN!  
**LETZTE ERFOLGREICHE ORDER:** TEST-MONSTERBACON-CFD6694D

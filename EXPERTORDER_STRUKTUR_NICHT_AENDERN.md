# ⚠️ KRITISCHE DATEI - NICHT ÄNDERN! ⚠️

## ExpertOrder POS-Integration - Verschachtelte Struktur

**Status:** ✅ PRODUKTIV - EINGEFROREN am 22.01.2026  
**Letzte funktionierende Bestellung:** TEST-MONSTERBACON-CFD6694D (22.01.2026)

---

## 🔒 WICHTIG: DIESE STRUKTUR DARF NICHT GEÄNDERT WERDEN!

Die verschachtelte Parent-Child Struktur ist KRITISCH für die korrekte Darstellung im ExpertOrder Kassensystem.

**Korrekte Struktur (SO MUSS ES BLEIBEN):**
```
Monsterbacon Burger Medium 125g Menü    €14.90
  └─ + Brioche Brötchen                  €0.00
  └─ - Ohne Gurken                       €0.00
  └─ - Ohne Zwiebeln                     €0.00
  └─ + Extra Bacon                       €0.00
  └─ + Pommes Frites Normal              €0.00
  └─ + Coca Cola 0,5l                    €0.00
  └─ + Ketchup                           €0.00
```

**FALSCHE Struktur (NICHT verwenden):**
```
1. Monsterbacon Burger Menü            €14.90
2. Brioche Brötchen (separate)         €0.00
3. Pommes Frites (separate)            €0.00
4. Cola (separate)                     €0.00
5. Ketchup (separate)                  €0.00
6. Extra Bacon (separate)              €1.00
```

---

## 📋 KORREKTES DATENFORMAT FÜR BESTELLUNGEN:

### **Für Testbestellungen siehe:** `/app/EXPERTORDER_TESTBESTELLUNGEN_NUR_KORREKTES_FORMAT.md`

**WICHTIG - Felder-Struktur:**

```python
item = {
    "name": "Produktname Menü",  # OHNE Größe im Namen!
    "size": "medium",  # Connector fügt "Medium 125g" automatisch hinzu
    
    # BRÖTCHEN (nur Brötchen!)
    "customizations": [
        "+ Brioche Brötchen"
    ],
    
    # REMOVALS (OHNE "Ohne" Prefix!)
    "removed_ingredients": [
        "Gurken",
        "Zwiebeln"
    ],
    
    # EXTRAS (als Objekte!)
    "extras": [
        {"name": "Extra Bacon", "price": 0.0}
    ],
    
    # BEILAGE/GETRÄNK/SAUCE (als Objekte!)
    "modifiers": {
        "beilage": {"name": "Pommes Frites Normal", "price": 0.0},
        "getraenk": {"name": "Coca Cola 0,5l", "price": 0.0},
        "sauce": {"name": "Ketchup", "price": 0.0}
    }
}
```

**❌ NIEMALS alles in customizations Array!**  
**❌ NIEMALS menu_components Objekt!**  
**❌ NIEMALS Größe im name-Feld!**

---

## 📋 TECHNISCHE DETAILS:

### Datei: `/app/backend/pos_connectors/expertorder.py`

**Funktion:** `_transform_order_to_eocloud()`

**Zeilen:** ~463-714

**Struktur:**
```python
# Für ALLE Artikel (Menüs, Pizza, Salate, etc.):
main_item = {
    "uid": "...",
    "name": "Produktname",
    "price": 10.90,
    "count": 1,
    "items": [
        # ALLE Komponenten hier als Children:
        {"uid": "...", "name": "+ Beilage"},
        {"uid": "...", "name": "+ Getränk"},
        {"uid": "...", "name": "+ Extra..."},
        {"uid": "...", "name": "- Ohne..."}
    ]
}
```

---

## ✅ GILT FÜR:

- ✅ Burger (mit/ohne Menü)
- ✅ Pizza (alle Größen)
- ✅ Salate (mit Dressing-Wahl)
- ✅ Fingerfood (mit Dip-Auswahl)
- ✅ Pasta (mit Nudel-Wahl)
- ✅ Wraps
- ✅ Alle anderen Artikel

**Beide Filialen:**
- ✅ Rellingen
- ✅ Henstedt-Ulzburg

---

## 🎯 KOMPONENTEN-REIHENFOLGE:

**Innerhalb jedes Artikels (als Children):**

1. **Brötchen-Auswahl** (z.B. "+ Sesam Brötchen")
2. **Abwahlen** (z.B. "- Ohne Zwiebeln")
3. **Extras** (z.B. "+ Extra Käse")
4. **Modifiers** (z.B. "+ Pommes Normal", "+ Coca Cola", "+ Caesar Dressing")

**Diese Reihenfolge ist optimal und darf nicht geändert werden!**

---

## 🚨 WARNUNG VOR ÄNDERUNGEN:

**Bei Änderungen an dieser Struktur:**
- ❌ Bestellungen werden im Kassensystem falsch dargestellt
- ❌ Artikel-Mapping funktioniert nicht mehr
- ❌ Menü-Komponenten erscheinen als separate Artikel
- ❌ Übersichtlichkeit geht verloren

**Wenn technische Anpassungen nötig sind:**
1. Backup dieser Datei erstellen
2. Änderungen mit Test-Bestellungen prüfen
3. Mit ExpertOrder im Kassensystem verifizieren
4. Erst dann produktiv schalten

---

## 📊 VERIFIZIERTE TEST-BESTELLUNGEN:

```
ZOZO-1156: Hamburger Menü (verschachtelt) ✅
ZOZO-1157: Cheeseburger Menü (verschachtelt) ✅
ZOZO-1158: Bacon Burger + Greek Salad (beide verschachtelt) ✅
```

**Alle erfolgreich an ExpertOrder gesendet!**

---

## 📞 SUPPORT:

Bei Problemen mit der POS-Integration:
1. Prüfe `/app/test_reports/` für Test-Ergebnisse
2. Prüfe POS-Logs: MongoDB Collection `pos_logs`
3. Prüfe Failed Orders: MongoDB Collection `failed_pos_orders`

**Diese Struktur hat sich als funktionierend bewährt - nicht ändern!**

---

**Datum:** 22.01.2026  
**Version:** FINAL  
**Status:** 🔒 EINGEFROREN - PRODUKTIV

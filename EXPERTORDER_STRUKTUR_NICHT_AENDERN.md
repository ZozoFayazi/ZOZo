# ⚠️ KRITISCHE DATEI - NICHT ÄNDERN! ⚠️

## ExpertOrder POS-Integration - Verschachtelte Struktur

**Status:** ✅ PRODUKTIV - EINGEFROREN am 22.01.2026

**Letzte funktionierende Bestellung:** ZOZO-1158

---

## 🔒 WICHTIG: DIESE STRUKTUR DARF NICHT GEÄNDERT WERDEN!

Die verschachtelte Parent-Child Struktur ist KRITISCH für die korrekte Darstellung im ExpertOrder Kassensystem.

**Korrekte Struktur (SO MUSS ES BLEIBEN):**
```
Hamburger Medium 125g Menü
            + Brioche Brötchen
            - Ohne Gurken
            + Extra Käse
            + Pommes Normal
            + Coca Cola 0,5l
```

**FALSCHE Struktur (NICHT verwenden):**
```
1. Hamburger Menü
2. Brioche Brötchen (separate)
3. Ohne Gurken (separate)
4. Extra Käse (separate)
5. Pommes Normal (separate)
6. Coca Cola (separate)
```

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

# ✅ Feature: Größennamen im Admin Dashboard bearbeitbar

**Implementiert:** 21.01.2026, 16:57 UTC  
**Status:** ✅ Vollständig implementiert und getestet

---

## 🎯 Was wurde hinzugefügt

Sie können jetzt im **Admin Dashboard** die Größennamen (Size Labels) für Burger-Produkte anpassen!

### Vorher:
- ❌ Größennamen waren hardcoded: "Medium (125g)" und "Large (180g)"
- ❌ Keine Möglichkeit, diese zu ändern

### Nachher:
- ✅ Zwei neue Eingabefelder im Produkt-Dialog
- ✅ Vollständige Kontrolle über die Größennamen
- ✅ Änderungen werden in der Datenbank gespeichert (`size_labels` Feld)
- ✅ Werden auf der Kundenwebsite angezeigt

---

## 📋 Wo finden Sie die neuen Felder?

### 1. Admin Dashboard aufrufen:
```
https://zozo-burger.de/admin/login
```

### 2. Zum Menü "Menü" → "Produkte" navigieren

### 3. Einen Burger bearbeiten:
- Klicken Sie auf das **Bearbeiten-Symbol** (Stift) bei einem Burger-Produkt
- Scrollen Sie im Dialog nach unten

### 4. Neuer Abschnitt: "Größennamen anpassen (optional)"

Sie sehen zwei Eingabefelder:

```
┌─────────────────────────────────────────────────┐
│  Größennamen anpassen (optional)                │
├─────────────────────────────────────────────────┤
│  Medium Label                 Large Label        │
│  ┌──────────────────┐       ┌──────────────────┐│
│  │ Medium (125g)    │       │ Large (180g)     ││
│  └──────────────────┘       └──────────────────┘│
│  z.B. "Klein" oder          z.B. "Groß" oder    │
│  "Medium (125g)"            "Large (180g)"      │
└─────────────────────────────────────────────────┘
```

---

## 💡 Verwendungsbeispiele

### Beispiel 1: Deutsche Bezeichnungen
```
Medium Label: Klein (125g)
Large Label:  Groß (180g)
```

### Beispiel 2: Nur Größe ohne Gewicht
```
Medium Label: Medium
Large Label:  Large
```

### Beispiel 3: Mit Gramm-Angabe
```
Medium Label: 125 Gramm
Large Label:  180 Gramm
```

### Beispiel 4: Custom Namen
```
Medium Label: Regular Size
Large Label:  Extra Size
```

---

## 🔧 Technische Details

### Geänderte Dateien:

1. **Backend:**
   - `/app/backend/models.py` - `MenuItemCreate` und `MenuItemUpdate` erweitert um `size_labels`

2. **Frontend:**
   - `/app/frontend/src/components/ProductDialog.jsx` - Neue UI-Felder hinzugefügt

### Datenbank-Struktur:

```json
{
  "_id": "...",
  "name": "Hamburger",
  "price_medium": 7.99,
  "price_large": 11.19,
  "size_labels": {
    "medium": "Medium (125g)",
    "large": "Large (180g)"
  },
  "has_sizes": true
}
```

### API-Endpoint:

```
PUT /api/admin/products/{product_id}

Body:
{
  "size_labels": {
    "medium": "Klein (125g)",
    "large": "Groß (180g)"
  }
}
```

---

## ✅ Funktionsweise

1. **Admin öffnet Produkt-Dialog:**
   - Bei Burgern mit Größen (has_sizes=true) werden die Size-Label-Felder angezeigt

2. **Admin ändert Größennamen:**
   - z.B. "Medium (125g)" → "Klein (125g)"
   - z.B. "Large (180g)" → "Groß (180g)"

3. **Speichern:**
   - Klick auf "Speichern"
   - Daten werden an Backend gesendet
   - `size_labels` wird in MongoDB gespeichert

4. **Anzeige auf Kundenwebsite:**
   - Die neuen Namen werden automatisch auf der Kundenwebsite verwendet
   - Bei Größenauswahl wird "Klein (125g)" statt "Medium (125g)" angezeigt

---

## 🧪 Wie Sie es testen können

### Test 1: Größennamen ändern

1. Melden Sie sich als Admin an
2. Gehen Sie zu Produkte
3. Bearbeiten Sie "Hamburger"
4. Scrollen Sie zu "Größennamen anpassen"
5. Ändern Sie:
   - Medium Label: `Klein (125g)`
   - Large Label: `Groß (180g)`
6. Klicken Sie auf "Speichern"
7. **Erwartetes Ergebnis:** ✅ "Produkt aktualisiert" Toast-Nachricht

### Test 2: Auf Kundenwebsite prüfen

1. Öffnen Sie https://zozo-burger.de
2. Wählen Sie einen Standort
3. Gehen Sie zur Speisekarte
4. Klicken Sie auf "Hamburger"
5. **Erwartetes Ergebnis:** ✅ Sie sehen "Klein (125g)" und "Groß (180g)" statt den alten Bezeichnungen

---

## 📝 Wichtige Hinweise

### Standardwerte:
- Wenn Sie die Felder leer lassen, werden die Standardwerte verwendet:
  - `"Medium (125g)"` für Medium
  - `"Large (180g)"` für Large

### Nur für Burger mit Größen:
- Diese Felder erscheinen **NUR** bei Burgern die `has_sizes: true` haben
- Produkte mit Single Size (z.B. Crunchy Chicken) zeigen diese Felder nicht

### Automatische Aktualisierung:
- Die Änderungen sind **sofort** nach dem Speichern live
- Kein Server-Neustart erforderlich
- Browser-Cache könnte einmal geleert werden müssen

---

## 🔒 Berechtigungen

**Wer kann Größennamen ändern?**
- ✅ Super Admin
- ✅ Rellingen Admin  
- ❌ Henstedt-Ulzburg Admin (nur Read-Only)

---

## 🎉 Vorteil dieser Funktion

1. **Flexibilität:** Passen Sie Größennamen nach Ihren Wünschen an
2. **Mehrsprachig:** Einfach zwischen deutschen und englischen Namen wechseln
3. **Marketing:** Nutzen Sie Custom-Namen wie "Regular" oder "Extra"
4. **Keine Code-Änderungen:** Alles über das Admin Dashboard steuerbar

---

## ❓ FAQ

**F: Was passiert, wenn ich die Felder leer lasse?**  
A: Die Standardwerte "Medium (125g)" und "Large (180g)" werden verwendet.

**F: Kann ich das Gewicht entfernen?**  
A: Ja! Tragen Sie einfach "Klein" oder "Groß" ein ohne Gramm-Angabe.

**F: Werden die Änderungen auch im POS übernommen?**  
A: Nein, das POS erhält die Größen-Information aus anderen Feldern. Die `size_labels` sind nur für die Kundenwebsite.

**F: Kann ich für jeden Burger unterschiedliche Namen verwenden?**  
A: Ja! Jedes Produkt hat seine eigenen `size_labels`.

---

**Bei Fragen oder Problemen:** Kontaktieren Sie Ihren System-Administrator

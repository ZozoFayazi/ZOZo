# ✅ Feature: Erweiterte Menü-Konfiguration im Admin Dashboard

**Implementiert:** 21.01.2026, 17:06 UTC  
**Status:** ✅ Vollständig implementiert (Option 3)

---

## 🎯 Was wurde implementiert

### ❌ Schritt 1: "Burger Menüs" Kategorie entfernt
- ✅ 23 Produkte zurück in "Burger" Kategorie verschoben
- ✅ Falsche "Burger Menüs" Kategorie gelöscht
- ✅ Alle Produkte jetzt korrekt kategorisiert

### ✅ Schritt 2: Erweiterte Menü-Konfiguration (Option 3)
Die **maximale Flexibilität** für Menü-Verwaltung:

```
☑️ Als Menü verfügbar
   ├─ ☑️ Beilage erforderlich
   ├─ ☑️ Getränk erforderlich
   ├─ Medium Menü-Preis: 13.89€
   └─ Large Menü-Preis: 17.09€
```

---

## 📋 Neue Funktionen im Detail

### 1. **Menü Toggle (Haupt-Schalter)**
```
☑️ Als Menü verfügbar
   Kunde kann Beilage + Getränk hinzufügen
```
- **AN:** Kunde sieht "Zum Menü erweitern" Button
- **AUS:** Keine Menü-Option verfügbar

### 2. **Flexible Menü-Komponenten**
Sie können jetzt entscheiden, was im Menü enthalten sein muss:

#### Option A: Vollständiges Menü (Standard)
```
☑️ Beilage erforderlich
☑️ Getränk erforderlich
→ Kunde MUSS Beilage UND Getränk wählen
```

#### Option B: Nur mit Beilage
```
☑️ Beilage erforderlich
☐ Getränk erforderlich
→ Kunde MUSS nur Beilage wählen, Getränk optional
```

#### Option C: Nur mit Getränk
```
☐ Beilage erforderlich
☑️ Getränk erforderlich
→ Kunde MUSS nur Getränk wählen, Beilage optional
```

#### Option D: Beides optional
```
☐ Beilage erforderlich
☐ Getränk erforderlich
→ Kunde kann beides frei wählen oder weglassen
```

### 3. **Individuelle Menü-Preise**
```
Medium Menü: 13.89€  (Basis: 7.99€)
Large Menü:  17.09€  (Basis: 11.19€)
```
- Vollständige Kontrolle über Menü-Aufpreise
- Automatische Anzeige des Basis-Preises zur Orientierung
- Pro Größe individuell anpassbar

---

## 🎨 UI im Admin Dashboard

### So sieht es aus (bei Burgern):

```
┌────────────────────────────────────────────────────┐
│ PRODUKT BEARBEITEN: Hamburger                      │
├────────────────────────────────────────────────────┤
│ [Bild Upload-Bereich]                              │
│                                                     │
│ Name: Hamburger                                    │
│ Kategorie: Burger                                  │
│ Beschreibung: ...                                  │
│                                                     │
│ ┌──────────────────┬──────────────────┐           │
│ │ Medium Preis     │ Large Preis      │           │
│ │ 7.99€            │ 11.19€           │           │
│ └──────────────────┴──────────────────┘           │
│                                                     │
│ ───────────────────────────────────────            │
│ Größennamen anpassen (optional)                    │
│ Medium Label: Medium (125g)                        │
│ Large Label: Large (180g)                          │
│                                                     │
│ ───────────────────────────────────────            │
│ 🍔 Als Menü verfügbar                     [ON ]   │
│    Kunde kann Beilage + Getränk hinzufügen        │
│                                                     │
│    Menü-Komponenten                                │
│    ├─ Beilage erforderlich            [ON ]       │
│    └─ Getränk erforderlich            [ON ]       │
│                                                     │
│    Menü-Preise                                     │
│    ┌─────────────────┬─────────────────┐          │
│    │ Medium Menü     │ Large Menü      │          │
│    │ 13.89€          │ 17.09€          │          │
│    │ Basis: €7.99    │ Basis: €11.19   │          │
│    └─────────────────┴─────────────────┘          │
│                                                     │
│ [Abbrechen]                    [Speichern]         │
└────────────────────────────────────────────────────┘
```

---

## 💡 Verwendungsbeispiele

### Beispiel 1: Standard-Burger-Menü (Vollständig)
**Hamburger:**
- ☑️ Als Menü verfügbar
- ☑️ Beilage erforderlich
- ☑️ Getränk erforderlich
- Medium Menü: 13.89€
- Large Menü: 17.09€

**Ergebnis:** Kunde muss Beilage UND Getränk wählen

---

### Beispiel 2: Premium-Burger (Nur mit Getränk)
**Monster Bacon Burger:**
- ☑️ Als Menü verfügbar
- ☐ Beilage erforderlich (optional)
- ☑️ Getränk erforderlich
- Medium Menü: 15.99€
- Large Menü: 19.99€

**Ergebnis:** Kunde MUSS Getränk wählen, Beilage ist optional

---

### Beispiel 3: Veggie Burger (Beides optional)
**Veggie Burger:**
- ☑️ Als Menü verfügbar
- ☐ Beilage erforderlich
- ☐ Getränk erforderlich
- Medium Menü: 11.99€
- Large Menü: 14.99€

**Ergebnis:** Kunde kann frei entscheiden

---

### Beispiel 4: Single-Size Burger (Kein Menü)
**Crunchy Chicken:**
- ☐ Als Menü verfügbar

**Ergebnis:** Keine Menü-Option für diesen Burger

---

## 🔧 So benutzen Sie die Funktion

### Schritt 1: Admin Dashboard öffnen
```
https://zozo-burger.de/admin/login
→ Menü → Produkte
```

### Schritt 2: Burger bearbeiten
- Finden Sie den Burger in der Produktliste
- Klicken Sie auf das **Bearbeiten-Symbol** (Stift)

### Schritt 3: Zu Menü-Optionen scrollen
- Scrollen Sie im Dialog nach unten
- Sie sehen die Sektion **"Als Menü verfügbar"**

### Schritt 4: Menü konfigurieren

#### A) Menü aktivieren/deaktivieren:
```
Klicken Sie auf den Toggle "Als Menü verfügbar"
```

#### B) Menü-Komponenten festlegen:
```
☑️/☐ Beilage erforderlich
☑️/☐ Getränk erforderlich
```

#### C) Menü-Preise anpassen:
```
Medium Menü: 13.89€
Large Menü:  17.09€
```

### Schritt 5: Speichern
- Klicken Sie auf **"Speichern"**
- ✅ Änderungen sind sofort live!

---

## 🎯 Technische Details

### Geänderte Dateien:

**Backend:**
- `/app/backend/models.py`
  - `MenuItemCreate` erweitert um: `can_upgrade_to_menu`, `menu_requires_side`, `menu_requires_drink`, `menu_upgrade_price_medium`, `menu_upgrade_price_large`
  - `MenuItemUpdate` erweitert um dieselben Felder

**Frontend:**
- `/app/frontend/src/components/ProductDialog.jsx`
  - Switch-Komponente importiert
  - Neue UI-Sektion "Menü-Optionen" hinzugefügt
  - Conditional Rendering (nur wenn Toggle AN)
  - FormData-State erweitert

**Datenbank:**
- `menu_items` Collection erhält neue Felder:
  ```json
  {
    "can_upgrade_to_menu": true,
    "menu_requires_side": true,
    "menu_requires_drink": true,
    "menu_upgrade_price_medium": 13.89,
    "menu_upgrade_price_large": 17.09
  }
  ```

---

## 🧪 Test-Checkliste

### ✅ Test 1: Menü aktivieren
1. Öffnen Sie Admin → Produkte
2. Bearbeiten Sie "Hamburger"
3. Aktivieren Sie "Als Menü verfügbar"
4. Setzen Sie beide Anforderungen (Beilage + Getränk)
5. Setzen Sie Menü-Preise: 13.89€ / 17.09€
6. Speichern Sie
7. **Erwartung:** ✅ Toast "Produkt aktualisiert"

### ✅ Test 2: Auf Kundenwebsite prüfen
1. Öffnen Sie https://zozo-burger.de
2. Wählen Sie Standort
3. Gehen Sie zur Speisekarte → Burger
4. Klicken Sie auf "Hamburger"
5. Wählen Sie eine Größe
6. **Erwartung:** ✅ "Zum Menü erweitern" Button ist sichtbar

### ✅ Test 3: Menü deaktivieren
1. Admin → Produkte → Hamburger bearbeiten
2. Deaktivieren Sie "Als Menü verfügbar"
3. Speichern Sie
4. Prüfen Sie Kundenwebsite
5. **Erwartung:** ✅ Kein "Zum Menü erweitern" Button

### ✅ Test 4: Flexible Komponenten
1. Admin → Hamburger bearbeiten
2. Aktivieren Sie Menü
3. Deaktivieren Sie "Getränk erforderlich"
4. Speichern Sie
5. Bestellen Sie auf Kundenwebsite
6. **Erwartung:** ✅ Beilage ist Pflicht, Getränk optional

---

## ❓ FAQ

**F: Was passiert, wenn ich "Als Menü verfügbar" deaktiviere?**  
A: Der Kunde sieht keinen "Zum Menü erweitern" Button. Produkt ist nur einzeln bestellbar.

**F: Kann ich unterschiedliche Menü-Preise pro Burger haben?**  
A: Ja! Jedes Produkt hat seine eigenen Menü-Preise.

**F: Was bedeutet "Beilage erforderlich"?**  
A: Wenn aktiviert, MUSS der Kunde eine Beilage aus der Liste wählen. Wenn deaktiviert, ist die Beilage optional.

**F: Funktioniert das auch für Pizzen?**  
A: Die UI-Felder erscheinen aktuell nur bei Burgern. Bei Bedarf kann es auch für Pizzen aktiviert werden.

**F: Werden alte Menü-Einstellungen überschrieben?**  
A: Nein! Bestehende Werte bleiben erhalten. Sie bearbeiten nur, was Sie ändern möchten.

**F: Muss ich immer beide Menü-Preise (Medium & Large) angeben?**  
A: Nur wenn der Burger beide Größen hat. Bei Single-Size Burgern erscheinen diese Felder nicht.

---

## 🚀 Vorteile dieser Lösung

1. ✅ **Maximale Flexibilität** - Vollständige Kontrolle über jedes Menü
2. ✅ **Zeit-Ersparnis** - Schnell per Toggle aktivieren/deaktivieren
3. ✅ **Keine Code-Änderungen** - Alles im Admin Dashboard
4. ✅ **Individuelle Preise** - Jeder Burger kann eigene Menü-Preise haben
5. ✅ **Flexible Komponenten** - Beilage/Getränk einzeln steuerbar
6. ✅ **Sofort live** - Keine Server-Neustarts nötig

---

## ⚠️ Wichtige Hinweise

### Berechtigungen:
- **Wer kann Menü-Einstellungen ändern?**
  - ✅ Super Admin
  - ✅ Rellingen Admin
  - ❌ Henstedt-Ulzburg Admin (Read-Only)

### Standardwerte:
- `can_upgrade_to_menu`: `false` (deaktiviert)
- `menu_requires_side`: `true` (Beilage erforderlich)
- `menu_requires_drink`: `true` (Getränk erforderlich)
- `menu_upgrade_price_medium`: leer (muss gesetzt werden)
- `menu_upgrade_price_large`: leer (muss gesetzt werden)

### Vor dem Go-Live:
- ✅ Prüfen Sie ALLE Burger auf korrekte Menü-Einstellungen
- ✅ Testen Sie die Bestellung auf der Kundenwebsite
- ✅ Verifizieren Sie POS-Integration (flattening)

---

## 📝 Nächste Schritte

1. **Alle Burger konfigurieren:**
   - Gehen Sie durch jeden Burger
   - Entscheiden Sie: Menü ja/nein?
   - Setzen Sie Anforderungen (Beilage/Getränk)
   - Setzen Sie Menü-Preise

2. **Testen:**
   - Testbestellung auf Kundenwebsite
   - Prüfen Sie, ob Anforderungen korrekt angezeigt werden
   - Verifizieren Sie Preise

3. **Deployment:**
   - Nutzen Sie `/app/NOTFALL_CUSTOM_DOMAIN_FIX.md`
   - Neuer Build ist ready in `/app/frontend/build/`

---

**Die Funktion ist einsatzbereit!** 🚀

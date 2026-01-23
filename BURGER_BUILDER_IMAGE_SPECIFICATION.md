# 📸 BURGER BUILDER - BILDER SPEZIFIKATION

## Zusammenfassung (TL;DR)

**Format:** PNG mit Transparenz
**Größe:** 800x800px (1:1 quadratisch)
**Perspektive:** Top-Down (von oben)
**Hintergrund:** Transparent
**Stil:** Realistische Fotos
**Zentrierung:** Zutat muss zentriert im Canvas sein

---

## 1️⃣ DATEIFORMAT

### Primär: PNG ✅
- **PNG-24** mit Alpha-Kanal (Transparenz)
- **sRGB Farbraum** (Standard Web)
- **Keine** Hintergrundfarbe
- **Kompression:** PNG Optimierung OK (TinyPNG, ImageOptim)

### Alternativ: WebP
- Falls PNG zu groß (>500KB)
- WebP mit Transparenz
- 80-90% Qualität

### ❌ NICHT: JPG
- Keine Transparenz möglich
- Nur als letzte Option mit weißem Hintergrund

---

## 2️⃣ ABMESSUNGEN

### Canvas-Größe (ALLE Zutaten gleich)
```
Breite:  800px
Höhe:    800px
Ratio:   1:1 (quadratisch)
```

### Zutat im Canvas
**Empfohlene Ausfüllung:**
- **Bottom Bun:** 90% der Canvas (720px Durchmesser)
- **Top Bun:** 90% der Canvas (720px Durchmesser)
- **Patty:** 75% der Canvas (600px Durchmesser)
- **Cheese:** 70% der Canvas (560px Durchmesser)
- **Salat/Tomato:** 65% der Canvas (520px Durchmesser)
- **Onions/Pickles:** 60% der Canvas (480px Durchmesser)
- **Saucen:** 80% der Canvas (640px als Drizzle/Spread)

**Wichtig:**
- Zutat muss **zentriert** sein (400px, 400px Mittelpunkt)
- **Rand freilassen:** Mindestens 40px auf allen Seiten
- Keine Zutat darf Canvas-Grenzen überschreiten

### Preview Container (Frontend)
```
Desktop:  400x400px
Mobile:   320x320px
Aspect:   1:1 (quadratisch, immer)
```

---

## 3️⃣ HINTERGRUND

### ✅ TRANSPARENT (Pflicht)
```
- Alpha-Kanal muss vorhanden sein
- Keine Hintergrundfarbe
- Keine weißen Ränder
- Keine Schatten AUSSERHALB der Zutat
```

### Schatten & Tiefe
**Erlaubt:**
- Leichte Schatten **AUF** der Zutat (z.B. Patty-Grill-Marks)
- Natürliche Textur-Schatten
- Konturen

**Nicht erlaubt:**
- Drop-Shadow UNTER der Zutat
- Harte Konturen-Schatten
- Glow-Effekte

---

## 4️⃣ PERSPEKTIVE & STIL

### Perspektive: **Top-Down (von oben)** ✅

**Kamera-Winkel:**
```
90° von oben (direkt senkrecht)
NICHT: Seitlich, schräg, 45°
```

**Warum Top-Down?**
- Zutaten stapeln sich logisch übereinander
- Keine Perspektiv-Verzerrung
- Einfacheres Layering im Code

**Beispiel:**
```
✅ RICHTIG: Burger von oben fotografiert (wie auf Teller)
❌ FALSCH: Burger seitlich (wie in Werbung)
```

### Stil: **Realistische Food-Fotografie** ✅

**Anforderungen:**
- Echtes Essen fotografieren (keine Illustrationen)
- Professionelle Ausleuchtung
- Hohe Schärfe, kein Blur
- Natürliche Farben (nicht übersättigt)

**Licht-Setup:**
```
- Diffuses Licht von oben
- Keine harten Schatten
- Gleichmäßige Ausleuchtung
- Food-Photography Standard
```

---

## 5️⃣ POSITIONING

### Zentrierung (WICHTIG!)
**Jede Zutat:**
- Muss im **Canvas-Zentrum** (400px, 400px) sein
- Symmetrisch ausgerichtet
- Horizontal & vertikal zentriert

**Keine zusätzlichen Offset-Felder nötig!**
- Frontend verwendet nur `position: center/full/drizzle`
- `center` = 80% Größe, zentriert
- `full` = 100% Größe (für Buns)
- `drizzle` = 80% Größe, als Sauce-Layer

### Sauce-Spezialfall
**Sauce als Drizzle/Spread:**
- Nicht kreisförmig wie Zutat
- Eher organische Form (wie gegossen/gestrichen)
- Transparent mit Sauce-Textur
- Kann leicht asymmetrisch sein

---

## 6️⃣ LAYER-REIHENFOLGE (FINAL)

### Die komplette Reihenfolge:

```
Layer 10:  bun_bottom       (Bottom Bun - PFLICHT)
Layer 20:  sauce_bottom     (Sauce unten - optional)
Layer 30:  salad            (Salat)
Layer 35:  rucola           (Rucola - falls verwendet)
Layer 40:  tomato           (Tomate)
Layer 45:  avocado          (Avocado Slices)
Layer 50:  patty            (Patty - PFLICHT)
Layer 55:  bacon/egg        (Extras auf Patty)
Layer 60:  cheese           (Käse)
Layer 70:  onion            (Zwiebeln)
Layer 75:  mushrooms        (Champignons)
Layer 80:  pickle           (Gurken)
Layer 85:  fried_onions     (Röstzwiebeln)
Layer 90:  sauce_top        (Sauce oben - optional)
Layer 100: bun_top          (Top Bun - PFLICHT)
```

### Bun-Spezial-Regel
**1 Bild = Bottom + Top:**
- Sie liefern NUR 1 Bild pro Brötchen-Typ
- Frontend rendert es 2x:
  - Bei layer_order 10 (Bottom)
  - Bei layer_order 100 (Top, evtl. gespiegelt)

**Keine** separaten Bilder für Top/Bottom nötig!

### Patty-Regel (Single/Double)
**1 Bild = Single Patty:**
- Sie liefern 1 Beef Patty Bild
- Wenn Kunde "2x Patty" wählt → Frontend rendert Bild 2x
- Kein separates "Double Patty" Bild nötig

---

## 7️⃣ NAMING & UPLOAD

### Dateinamen (Empfehlung)
```
brioche_bun.png
semolina_bun.png
potato_bun.png
beef_patty_125g.png
beef_patty_180g.png
chicken_patty.png
fish_patty.png
veggie_patty.png
nuggets.png
chester_cheese_2.png
chester_cheese_3.png
salad_iceberg.png
tomato_slices.png
onions_white.png
onions_red.png
pickles.png
bacon_strips.png
egg_fried.png
avocado_slices.png
guacamole.png
ketchup_drizzle.png
mayo_spread.png
bbq_sauce.png
```

### Upload-Prozess (im Admin)
1. Admin → Burger Builder
2. Zutat in Tabelle finden
3. Auf Upload-Icon klicken (bei "Bild"-Spalte)
4. Bild auswählen (PNG, max 5MB)
5. Upload erfolgt automatisch
6. Preview erscheint in Tabelle
7. **WICHTIG:** "Speichern" Button drücken!

### Ordner-Struktur
```
/app/frontend/public/uploads/burger-builder/
├── brioche_bun_abc123.png
├── beef_patty_125g_def456.png
└── ...
```

---

## 8️⃣ QUALITÄTS-CHECK & TESTS

### Technische Qualitäts-Checks

**Nach Upload prüfen:**
```bash
# Datei-Größe
ls -lh /app/frontend/public/uploads/burger-builder/

# Sollte sein: < 500KB pro Bild
# Falls größer: Komprimieren mit TinyPNG
```

**Im Admin prüfen:**
- ✅ Bild wird in Tabelle angezeigt (Vorschau 64x64px)
- ✅ Bild lädt schnell (< 1 Sekunde)
- ✅ Transparenz sichtbar (Hintergrund durchscheinend)

### Visuelle Qualitäts-Checks (im Builder)

**Test 1: Einzelne Zutat**
1. Burger Builder öffnen
2. NUR Brioche Bun wählen
3. **Prüfen:** Bun sichtbar in Preview? Zentriert?

**Test 2: Layer-Stack**
1. Bottom Bun wählen
2. Salat hinzufügen → **Prüfen:** Liegt über Bun?
3. Tomate hinzufügen → **Prüfen:** Liegt über Salat?
4. Patty hinzufügen → **Prüfen:** Liegt über Tomate?
5. Cheese hinzufügen → **Prüfen:** Liegt über Patty?
6. Top Bun hinzufügen → **Prüfen:** Liegt über allem?

**Test 3: Alignment**
- Alle Zutaten müssen zentriert sein
- Keine Zutat darf "versetzt" aussehen
- Stack muss wie echter Burger wirken

### E2E Test (Vollständiger Burger)

**Konfiguration:**
```
1. Brioche Bun
2. Ketchup (Sauce Bottom, kostenlos)
3. Eisbergsalat
4. Tomate
5. Beef Patty 125g
6. Chester Käse 2 Scheiben
7. Zwiebeln
8. Gewürzgurken
9. Mayo (Sauce Top, kostenlos)
10. (Top Bun - automatisch)
```

**Erwartung:**
- Alle 10 Layer sichtbar
- Korrekte Reihenfolge
- Burger sieht "essbar" aus
- Keine überlappenden Probleme
- Preis korrekt: €10.90

---

## 9️⃣ MVP BILDER-LISTE (Minimal Set)

**Für einen funktionierenden Demo-Burger brauchen Sie MINDESTENS:**

### Pflicht (6 Bilder)
1. ✅ **Brioche Bun** (wird für Bottom + Top verwendet)
2. ✅ **Beef Patty 125g**
3. ✅ **Eisbergsalat**
4. ✅ **Tomate**
5. ✅ **Cheese Slice** (Chester 2 Scheiben)
6. ✅ **Ketchup** (Drizzle/Spread)

**Mit diesen 6 Bildern kann ein Basis-Burger gebaut werden!**

### Empfohlen (12 Bilder = Kompletter Standard-Burger)
7. Zwiebeln
8. Gewürzgurken
9. Mayonnaise
10. BBQ Sauce
11. Bacon
12. Spiegelei

### Vollständig (30+ Bilder = Alle Optionen)
- Alle Brötchen (3x)
- Alle Proteins (6x)
- Alle Käse (4x)
- Alle Veggies Standard (5x)
- Alle Veggies Premium (5x)
- Alle Extras (4x)
- Alle Sauces (14x)

---

## 🔟 FOTO-ANLEITUNG (Schritt für Schritt)

### Setup
```
Kamera:       Smartphone (12MP+) oder DSLR
Stativ:       Ja (direkt über Zutat)
Licht:        2x Softbox links/rechts, diffus
Hintergrund:  Weißes Papier/Foam Board
Höhe:         30-50cm über Zutat
```

### Fotografieren
```
1. Zutat auf weißem Untergrund platzieren
2. Zutat zentrieren (mittig im Sucher)
3. Kamera exakt senkrecht ausrichten
4. Mehrere Aufnahmen (leichte Variationen)
5. Beste Aufnahme auswählen
```

### Post-Processing (Photoshop/GIMP)
```
1. Bild öffnen
2. Canvas auf 800x800px setzen (zentriert croppen)
3. Hintergrund entfernen:
   - Magic Wand Tool (weißer Hintergrund)
   - Delete
   - Transparency Check
4. Zutat zentrieren (falls nötig)
5. Kleine Korrekturen:
   - Farbe/Kontrast anpassen
   - Schatten säubern (nur auf Zutat, nicht darunter)
6. Export:
   - PNG-24
   - Transparenz aktiviert
   - sRGB
   - Dateiname: [zutat]_[typ].png
7. Komprimieren (TinyPNG):
   - Ziel: < 200KB pro Bild
```

---

## 📐 BEISPIEL: BEEF PATTY 125G

### Technische Spezifikation
```yaml
Dateiname:    beef_patty_125g.png
Format:       PNG-24 mit Alpha
Größe:        800x800px
Dateigröße:   < 200KB
Hintergrund:  Transparent
Perspektive:  Top-Down (90° von oben)
Ausfüllung:   ~600px Durchmesser (75% der Canvas)
Zentrierung:  Exakt in Canvas-Mitte
Layer Order:  50
Layer Group:  patty
Position:     center
```

### Foto-Setup
```
1. Gegrilltes Beef Patty (125g, ~10cm Durchmesser)
2. Auf weißem Teller/Papier
3. Kamera direkt von oben
4. Gleichmäßiges Licht (keine harten Schatten)
5. Foto schießen
```

### Post-Processing
```
1. Crop auf 800x800px (Patty zentriert)
2. Hintergrund entfernen (Transparency)
3. Patty etwas aufhellen (Kontrast +10%)
4. Grill-Marks sichtbar machen
5. PNG Export
6. Komprimieren auf ~150KB
```

### Ergebnis-Check
- ✅ Patty füllt ~75% des Canvas
- ✅ Zentriert
- ✅ Transparenter Hintergrund
- ✅ Grill-Marks sichtbar
- ✅ Appetitlich aussehend
- ✅ < 200KB Dateigröße

---

## 📋 LAYER-REIHENFOLGE (Detailliert)

### Standard-Burger Aufbau (von unten nach oben)

```
Layer 10:  BOTTOM BUN         [brioche_bun.png]
           ↓
Layer 20:  SAUCE BOTTOM       [ketchup_drizzle.png] - optional
           ↓
Layer 30:  SALAD              [salad_iceberg.png]
           ↓
Layer 40:  TOMATO             [tomato_slices.png]
           ↓
Layer 45:  AVOCADO            [avocado_slices.png] - optional
           ↓
Layer 50:  PATTY              [beef_patty_125g.png]
           ↓
Layer 55:  BACON/EGG          [bacon_strips.png] - optional
           ↓
Layer 60:  CHEESE             [chester_cheese_2.png]
           ↓
Layer 70:  ONION              [onions_white.png]
           ↓
Layer 75:  MUSHROOMS          [mushrooms.png] - optional
           ↓
Layer 80:  PICKLE             [pickles.png]
           ↓
Layer 90:  SAUCE TOP          [mayo_spread.png] - optional
           ↓
Layer 100: TOP BUN            [brioche_bun.png] - GLEICH wie Bottom!
```

### Spezial-Fälle

**Buns:**
- 1 Bild wird 2x verwendet (Bottom bei 10, Top bei 100)
- Top Bun kann optional horizontal gespiegelt werden

**Saucen:**
- Sauce Bottom (Layer 20): Unter Salat
- Sauce Top (Layer 90): Über Gurken, unter Top Bun
- Form: Drizzle/Spread (organische Form, nicht perfekt rund)

**Mehrfach-Zutaten:**
- Wenn Kunde "2x Cheese" wählt: Gleiches Bild 2x rendern
- Leichter Y-Offset: +5px für 2. Layer

---

## 🎯 MVP BILDER (Start hier!)

### Phase 1: Basis-Demo (6 Bilder)
Damit der Builder funktioniert und getestet werden kann:

```
1. brioche_bun.png          (Layer 10 + 100)
2. beef_patty_125g.png      (Layer 50)
3. salad_iceberg.png        (Layer 30)
4. tomato_slices.png        (Layer 40)
5. chester_cheese_2.png     (Layer 60)
6. ketchup_drizzle.png      (Layer 20)
```

**Ergebnis:** Funktionaler Demo-Burger:
```
Top Bun
  Käse
  Tomate
  Salat
  Ketchup
Bottom Bun
```

### Phase 2: Standard-Set (16 Bilder)
```
+ 7.  semolina_bun.png
+ 8.  beef_patty_180g.png
+ 9.  onions_white.png
+ 10. pickles.png
+ 11. mayo_spread.png
+ 12. bbq_sauce.png
+ 13. bacon_strips.png
+ 14. egg_fried.png
+ 15. onions_red.png
+ 16. chicken_patty.png
```

### Phase 3: Komplett (30+ Bilder)
Alle Optionen aus dem Menü.

---

## 📸 FOTO-BEISPIELE

### Bottom Bun (Brioche)
```
Datei:       brioche_bun.png
Canvas:      800x800px
Zutat-Größe: ~720px Durchmesser (90%)
Ansicht:     Von oben
Details:     
  - Goldbraune Oberfläche sichtbar
  - Sesam-Körner (falls vorhanden)
  - Leichte Textur-Schatten
  - Perfekt rund
  - Zentriert
```

### Beef Patty
```
Datei:       beef_patty_125g.png
Canvas:      800x800px
Zutat-Größe: ~600px Durchmesser (75%)
Ansicht:     Von oben
Details:
  - Gegrillte Oberfläche mit Grill-Marks
  - Braune Farbe (nicht zu dunkel)
  - Leicht unregelmäßige Form (authentisch)
  - Fett-Glanz sichtbar (appetitlich)
  - Zentriert
```

### Salat
```
Datei:       salad_iceberg.png
Canvas:      800x800px
Zutat-Größe: ~520px Durchmesser (65%)
Ansicht:     Von oben
Details:
  - Frische grüne Farbe
  - Zerrupftes/geschnittenes Blatt
  - Natürliche, organische Form
  - Nicht zu perfekt rund
  - Leichte Wellen/Struktur
  - Zentriert
```

### Sauce (Ketchup Drizzle)
```
Datei:       ketchup_drizzle.png
Canvas:      800x800px
Zutat-Größe: ~640px (80%, organisch)
Ansicht:     Von oben
Details:
  - Wie mit Flasche gegossen
  - Kreisförmiger Klecks/Spread
  - Kanten leicht unregelmäßig
  - Glänzende Textur
  - Rote Farbe (nicht zu grell)
  - Leichte Drizzle-Effekte OK
  - Zentriert (grob)
```

---

## 🧪 TEST-PROZEDUR

### Nach Upload eines Bildes:

**1. Admin-Check:**
```
- Bild wird in Tabelle angezeigt? ✅
- Datei-Größe < 500KB? ✅
- Transparenz sichtbar? ✅
```

**2. Builder-Check:**
```
- Burger Builder öffnen
- Zutat auswählen
- Bild erscheint in Live Preview? ✅
- Bild zentriert? ✅
- Richtige Layer-Position? ✅
```

**3. Stack-Check (mehrere Zutaten):**
```
- Brioche Bun wählen → Erscheint bei Layer 10 + 100? ✅
- Salat wählen → Erscheint ÜBER Bun? ✅
- Patty wählen → Erscheint ÜBER Salat? ✅
- Cheese wählen → Erscheint ÜBER Patty? ✅
```

**4. Performance-Check:**
```
- Alle Bilder laden in < 2 Sekunden? ✅
- Kein Flackern beim Auswählen? ✅
- Smooth Transition? ✅
```

---

## 📦 DELIVERY FORMAT

### Was Sie mir liefern:

**Option A: Zip-Datei**
```
burger_builder_images.zip
├── 1_buns/
│   ├── brioche_bun.png
│   ├── semolina_bun.png
│   └── potato_bun.png
├── 2_proteins/
│   ├── beef_patty_125g.png
│   ├── beef_patty_180g.png
│   └── ...
├── 3_veggies/
│   └── ...
└── README.txt (mit Liste)
```

**Option B: Einzeln hochladen**
```
- Im Admin direkt hochladen
- Ich gebe Ihnen Zugang
- Sie laden jede Zutat einzeln hoch
```

### Begleit-Dokumentation
```
README.txt:
- Liste aller Bilder
- Welche Zutat = welches Bild
- Besonderheiten (z.B. "Bacon ist crispy, nicht raw")
```

---

## ✅ CHECKLISTE (Für jedes Bild)

Bevor Sie ein Bild als "fertig" markieren:

- [ ] PNG-24 mit Alpha-Kanal
- [ ] 800x800px Canvas
- [ ] Transparenter Hintergrund (kein Weiß)
- [ ] Zutat zentriert (400px, 400px Mitte)
- [ ] Richtige Ausfüllung (60-90% je nach Typ)
- [ ] Top-Down Perspektive (90°)
- [ ] Scharfes Foto (keine Unschärfe)
- [ ] Natürliche Farben (nicht übersättigt)
- [ ] Dateigröße < 200KB (nach Kompression)
- [ ] sRGB Farbraum
- [ ] Korrekte Dateinamen
- [ ] Keine Drop-Shadows außerhalb

---

## 🚀 NACH BILD-UPLOAD

**Wenn alle MVP-Bilder hochgeladen sind (6 Bilder):**

1. Burger Builder testen
2. Screenshots machen (Layer-Stack)
3. Custom Burger bestellen
4. Kassenbon prüfen: Alle Zutaten korrekt?
5. POS prüfen: ExpertOrder erhält korrekte Daten?

**Dann:** Feature ist PRODUCTION-READY! ✅

---

## 📞 SUPPORT

**Bei Fragen:**
- Spezifikation unklar? → Diese Datei re-lesen
- Technische Probleme? → Logs prüfen
- Bilder passen nicht? → Größe/Zentrierung anpassen

**Wichtig:**
- Lieber 1-2 Test-Bilder erst hochladen
- Testen ob Layer-System funktioniert
- Dann alle weiteren Bilder

---

## ✅ ZUSAMMENFASSUNG (Quick Ref)

| Parameter | Wert |
|-----------|------|
| Format | PNG-24 mit Alpha |
| Größe | 800x800px (1:1) |
| Hintergrund | Transparent |
| Perspektive | Top-Down (90°) |
| Stil | Realistische Fotos |
| Zentrierung | Canvas-Mitte (400, 400) |
| Dateigröße | < 200KB (komprimiert) |
| Farbraum | sRGB |
| MVP Set | 6 Bilder (Bun, Patty, Salat, Tomate, Käse, Ketchup) |

---

Erstellt: 23.01.2026
Version: 1.0
Status: Final Specification

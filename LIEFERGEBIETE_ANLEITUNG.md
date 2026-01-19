# 🗺️ LIEFERGEBIETE - KOMPLETTE ANLEITUNG

**Status:** System vorhanden, temporär deaktiviert  
**Datum:** 14. Januar 2026

---

## 📍 AKTUELLER STATUS

✅ **Temporär deaktiviert** - Alle PLZ können bestellen  
✅ **Admin-UI vorhanden** - Konfiguration möglich  
✅ **Datenbank-Struktur fertig** - delivery_zone in locations  

---

## 🎯 WIE ES FUNKTIONIERT

### 1️⃣ PLZ-LISTEN-MODUS (Empfohlen, einfach)

**So funktioniert es:**
- Sie definieren eine Liste erlaubter PLZ pro Filiale
- Kunde gibt PLZ ein → System prüft ob in Liste
- Wenn JA → Bestellung erlaubt
- Wenn NEIN → Fehlermeldung

**Beispiel Rellingen:**
```json
{
  "mode": "postal_codes",
  "postal_codes": [
    "25462",  // Rellingen
    "25421",  // Pinneberg
    "25451",  // Quickborn
    "22926",  // Ahrensburg
    "22869"   // Schenefeld
  ],
  "min_order_value": 12.0,
  "delivery_fee": 3.0,
  "free_delivery_threshold": 25.0
}
```

**Vorteile:**
- ✅ Sehr präzise Kontrolle
- ✅ Einfach zu konfigurieren
- ✅ Keine Google Maps API nötig
- ✅ Sofort einsatzbereit

**Nachteile:**
- ⚠️ Jede PLZ manuell hinzufügen
- ⚠️ Bei vielen PLZ aufwendig

---

### 2️⃣ RADIUS-MODUS (Automatisch, braucht GPS)

**So funktioniert es:**
- Filiale hat GPS-Koordinaten (lat/lng)
- Kunde-Adresse wird in GPS umgewandelt (Geocoding)
- Distanz wird berechnet (Haversine-Formel)
- Wenn Distanz < Radius → Lieferung möglich

**Beispiel Rellingen:**
```json
{
  "mode": "radius",
  "radius_km": 5.0,  // 5km Umkreis
  "min_order_value": 12.0,
  "delivery_fee": 3.0,
  "free_delivery_threshold": 25.0
}
```

**Voraussetzungen:**
- ✅ Filiale muss GPS-Koordinaten haben (lat/lng)
- ✅ Google Maps Geocoding API Key benötigt
- ⚠️ Aktuell NICHT implementiert (Distanz-Berechnung fehlt)

**Vorteile:**
- ✅ Automatisch - keine PLZ-Listen pflegen
- ✅ Flexible Anpassung (Radius ändern = sofort aktiv)

**Nachteile:**
- ⚠️ Google Maps API Kosten (~5€/1000 Anfragen)
- ⚠️ Braucht GPS-Koordinaten der Kunden-Adresse
- ⚠️ Luftlinie ≠ Fahrtstrecke

---

## 🔧 WIE SIE ES KONFIGURIEREN

### Option A: PLZ-Listen (JETZT sofort möglich)

**Im Admin-Panel:**
1. Login: https://tastycart-3.preview.emergentagent.com/admin/login
2. Menü → **Filialen**
3. Filiale auswählen (z.B. Rellingen)
4. **PLZ hinzufügen:**
   - Eingabefeld: "25462" → Hinzufügen
   - Wiederholen für alle gewünschten PLZ
5. **Kosten einstellen:**
   - Mindestbestellwert: z.B. 12€
   - Liefergebühr: z.B. 3€
   - Gratis ab: z.B. 25€
6. **Speichern** → Sofort aktiv!

**Code-Aktivierung (Backend):**
```python
# In /app/backend/server.py, Zeile 1470-1476:
# Kommentare entfernen um PLZ-Validierung zu aktivieren

if not is_pickup:
    if delivery_zone and customer_postal_code not in delivery_zone.get('postal_codes', []):
        raise HTTPException(
            status_code=400,
            detail=f"Wir liefern leider nicht nach {customer_postal_code}"
        )
```

**Dann:** `supervisorctl restart backend`

---

### Option B: Radius-Modus (Braucht Entwicklung)

**Was noch fehlt:**

1. **Distanz-Berechnung implementieren:**
```python
# Haversine-Formel für Luftlinie-Distanz
def calculate_distance(lat1, lng1, lat2, lng2):
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Erdradius in km
    
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c  # Distanz in km
```

2. **Geocoding für Kunden-Adresse:**
   - PLZ + Stadt → GPS Koordinaten holen
   - Nutzt Google Maps Geocoding API
   - Cached für Performance

3. **Validierung in check_delivery_zone:**
```python
if delivery_zone.get('mode') == 'radius':
    # Kunde-Adresse geocoden
    customer_coords = await geocode_address(postal_code, city)
    
    # Distanz berechnen
    distance = calculate_distance(
        location['lat'], location['lng'],
        customer_coords['lat'], customer_coords['lng']
    )
    
    # Prüfen
    if distance > delivery_zone.get('radius_km', 5.0):
        return {"available": False, "message": f"Zu weit ({distance:.1f}km)"}
```

4. **Google Maps API Key benötigt:**
   - Kostet ca. 5€ pro 1000 Geocoding-Anfragen
   - In `.env`: `GOOGLE_MAPS_API_KEY=your_key`

---

## 💡 EMPFEHLUNG

### Für ZOZO Burger empfehle ich:

**🥇 OPTION 1: PLZ-Listen (Sofort einsetzbar)**

**Warum:**
- ✅ Keine zusätzlichen Kosten
- ✅ Präzise Kontrolle
- ✅ Sofort konfigurierbar
- ✅ Keine Google API nötig
- ✅ Hamburg hat ~100 PLZ → überschaubar

**Beispiel-Konfiguration:**

**Rellingen (Liefergebiet Nord-West):**
```
PLZ: 25462, 25421, 25451, 22926, 22869, 22927, 22844, 22850
Mindestbestellwert: 12€
Liefergebühr: 3€
Gratis ab: 25€
```

**Henstedt-Ulzburg (Liefergebiet Nord-Ost):**
```
PLZ: 24558, 24568, 24576, 24601, 24594, 24623
Mindestbestellwert: 12€
Liefergebühr: 3€
Gratis ab: 25€
```

---

## 🚀 SCHNELLSTART - PLZ-LISTEN AKTIVIEREN

**5 Schritte:**

1. **Admin-Panel öffnen:**
   - https://tastycart-3.preview.emergentagent.com/admin/login
   - Login: admin@zonik-solutions.de / Nila1605!

2. **Filialen-Einstellungen:**
   - Menü → "Filialen"
   - "ZOZO Burger Rellingen" → Einstellungen

3. **PLZ hinzufügen:**
   - Eingabefeld unter "Liefergebiete"
   - PLZ eingeben (z.B. "25462") → Button "Hinzufügen"
   - Wiederholen für alle PLZ

4. **Kosten einstellen:**
   - Mindestbestellwert: 12
   - Liefergebühr: 3
   - Gratis ab: 25
   - Button "Speichern"

5. **Backend aktivieren:**
   ```bash
   # In /app/backend/server.py die Kommentare entfernen
   # Zeile 1470-1476 (PLZ-Validierung)
   # Zeile 1482-1489 (Mindestbestellwert & Gebühren)
   supervisorctl restart backend
   ```

**Fertig!** System validiert nun PLZ pro Filiale.

---

## 🔄 SPÄTER: Radius-Modus implementieren

**Falls Sie Radius-Modus wollen:**

1. Google Maps API Key besorgen
2. Distanz-Berechnung implementieren (siehe oben)
3. check_delivery_zone erweitern
4. Geocoding-Cache für Performance
5. Testen mit verschiedenen Adressen

**Aufwand:** ~2-3 Stunden Entwicklung + Testing

---

## 📊 VERGLEICH

| Feature | PLZ-Listen | Radius |
|---------|-----------|--------|
| Einfachheit | ✅✅✅ Sehr einfach | ⚠️ Komplex |
| Kosten | ✅ Kostenlos | ⚠️ Google API (~5€/1000) |
| Präzision | ✅ 100% genau | ⚠️ Luftlinie ungenau |
| Setup-Zeit | ✅ 10 Minuten | ⚠️ 2-3 Stunden Dev |
| Wartung | ⚠️ PLZ pflegen | ✅ Automatisch |
| Bereit | ✅ JETZT | ❌ Entwicklung nötig |

---

## ✅ MEINE EMPFEHLUNG

**Starten Sie mit PLZ-Listen:**
1. Schnell umsetzbar (heute noch)
2. Keine Kosten
3. Volle Kontrolle
4. Später auf Radius umsteigen möglich

**Radius später ergänzen falls:**
- Sie sehr viele PLZ haben (>200)
- Automatische Anpassung gewünscht
- Google API Budget vorhanden

---

## 🎯 AKTUELLER STAND

**Temporär:** Alle PLZ zugelassen (0€ überall)  
**Bereit:** PLZ-Listen-System komplett im Admin-Panel  
**Optional:** Radius-Modus mit kleiner Entwicklung möglich

Sagen Sie Bescheid, welchen Weg Sie gehen möchten! 🚀

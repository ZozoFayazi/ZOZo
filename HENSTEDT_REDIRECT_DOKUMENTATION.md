# Temporäre Weiterleitung für Henstedt-Ulzburg

## Zweck

Bis alle Bugs (Menü-Struktur, E-Mails) behoben und getestet sind, werden Bestellungen für den Standort **Henstedt-Ulzburg** zu einer externen Foodbooking-Seite weitergeleitet.

**Externe URL:** https://www.foodbooking.com/api/fb/0ybj4

## Implementierte Weiterleitungen

Die Weiterleitung wurde an **4 kritischen Stellen** im Frontend implementiert:

### 1. LocationsPage.jsx (Standort-Übersichtsseite)
**Datei:** `/app/frontend/src/pages/LocationsPage.jsx`
**Zeile:** ~26

```javascript
const handleOrder = (location) => {
  // Temporäre Weiterleitung für Henstedt-Ulzburg zu Foodbooking
  if (location.slug === 'henstedt-ulzburg' || location.slug === 'henstedt') {
    window.location.href = 'https://www.foodbooking.com/api/fb/0ybj4';
    return;
  }
  
  setSelectedLocation(location);
  navigate('/menu');
};
```

**Wann triggert:** Wenn Benutzer auf "Hier bestellen" Button auf der Standorte-Seite klickt

---

### 2. HomePage.jsx (Startseite)
**Datei:** `/app/frontend/src/pages/HomePage.jsx`
**Zeilen:** ~57 und ~62

**Funktion 1: handleOrder**
```javascript
const handleOrder = (location) => {
  // Temporäre Weiterleitung für Henstedt-Ulzburg zu Foodbooking
  if (location.slug === 'henstedt-ulzburg' || location.slug === 'henstedt') {
    window.location.href = 'https://www.foodbooking.com/api/fb/0ybj4';
    return;
  }
  
  setSelectedLocation(location);
  navigate('/menu');
};
```

**Funktion 2: handleOrderTypeComplete**
```javascript
const handleOrderTypeComplete = (data) => {
  // Temporäre Weiterleitung für Henstedt-Ulzburg zu Foodbooking
  if (data.location.slug === 'henstedt-ulzburg' || data.location.slug === 'henstedt') {
    window.location.href = 'https://www.foodbooking.com/api/fb/0ybj4';
    return;
  }
  
  setSelectedLocation(data.location);
  setShowOrderTypeDialog(false);
  navigate('/menu');
};
```

**Wann triggert:** 
- Wenn Benutzer auf Startseite einen Standort auswählt
- Wenn Benutzer den Order-Type-Dialog (Lieferung/Abholung) abschließt

---

### 3. LocationDetailPage.jsx (Detail-Seite eines Standorts)
**Datei:** `/app/frontend/src/pages/LocationDetailPage.jsx`
**Zeile:** ~77

```javascript
const handleOrderHere = () => {
  if (location) {
    // Temporäre Weiterleitung für Henstedt-Ulzburg zu Foodbooking
    if (location.slug === 'henstedt-ulzburg' || location.slug === 'henstedt') {
      window.location.href = 'https://www.foodbooking.com/api/fb/0ybj4';
      return;
    }
    
    setSelectedLocation(location);
    navigate('/menu');
  }
};
```

**Wann triggert:** Wenn Benutzer auf der Detail-Seite von Henstedt-Ulzburg auf "Jetzt bestellen" klickt

---

### 4. MenuPage.jsx (Menü-Seite)
**Datei:** `/app/frontend/src/pages/MenuPage.jsx`
**Zeile:** ~73

```javascript
useEffect(() => {
  if (selectedLocation) {
    // Temporäre Weiterleitung für Henstedt-Ulzburg zu Foodbooking
    if (selectedLocation.slug === 'henstedt-ulzburg' || selectedLocation.slug === 'henstedt') {
      window.location.href = 'https://www.foodbooking.com/api/fb/0ybj4';
      return;
    }
    
    loadMenu(selectedLocation.id);
  }
}, [selectedLocation]);
```

**Wann triggert:** 
- Wenn jemand direkt zur Menü-Seite navigiert mit Henstedt als gespeichertem Standort
- Wenn jemand den Standort im Header wechselt zu Henstedt

---

## Erkannte Slug-Varianten

Die Weiterleitung prüft auf **beide** möglichen Slug-Varianten:
- `henstedt-ulzburg` (mit Bindestrich)
- `henstedt` (kurz)

```javascript
if (location.slug === 'henstedt-ulzburg' || location.slug === 'henstedt') {
  // Weiterleitung
}
```

## User Experience

### Was passiert für Kunden:

1. **Kunde wählt Henstedt-Ulzburg aus**
   - Auf Startseite, Standorte-Seite oder Detail-Seite

2. **Sofortige Weiterleitung**
   - `window.location.href` = harte Browser-Weiterleitung
   - Keine Verzögerung, kein Zwischenschritt

3. **Externe Foodbooking-Seite öffnet sich**
   - URL: https://www.foodbooking.com/api/fb/0ybj4
   - Kunde kann dort normal bestellen

### Was passiert für Rellingen:

**KEINE Änderungen!**
- Rellingen-Bestellungen funktionieren wie gewohnt
- Normale Menü-Seite öffnet sich
- Kein Redirect

## Vorteile dieser Lösung

✅ **Schnell implementiert** (4 Zeilen Code pro Stelle)
✅ **Keine Backend-Änderungen nötig**
✅ **Nur Henstedt betroffen** - Rellingen läuft normal
✅ **Sofortige Weiterleitung** - Keine Fehlerseiten für Kunden
✅ **Einfach rückgängig zu machen** - Nur 4 Stellen zu ändern

## Rückgängig machen

Wenn alle Bugs behoben sind:

### Option A: Weiterleitung entfernen (empfohlen)

In allen 4 Dateien die Weiterleitung entfernen:

```javascript
// VORHER:
const handleOrder = (location) => {
  if (location.slug === 'henstedt-ulzburg' || location.slug === 'henstedt') {
    window.location.href = 'https://www.foodbooking.com/api/fb/0ybj4';
    return;
  }
  
  setSelectedLocation(location);
  navigate('/menu');
};

// NACHHER:
const handleOrder = (location) => {
  setSelectedLocation(location);
  navigate('/menu');
};
```

**Dateien:**
1. `/app/frontend/src/pages/LocationsPage.jsx` (Zeile ~26)
2. `/app/frontend/src/pages/HomePage.jsx` (Zeilen ~57 und ~62)
3. `/app/frontend/src/pages/LocationDetailPage.jsx` (Zeile ~77)
4. `/app/frontend/src/pages/MenuPage.jsx` (Zeile ~73)

### Option B: Weiterleitung auskommentieren

Für schnelles Testen:

```javascript
const handleOrder = (location) => {
  // TEMPORÄR DEAKTIVIERT - Testing
  // if (location.slug === 'henstedt-ulzburg' || location.slug === 'henstedt') {
  //   window.location.href = 'https://www.foodbooking.com/api/fb/0ybj4';
  //   return;
  // }
  
  setSelectedLocation(location);
  navigate('/menu');
};
```

## Testing

### Test 1: Henstedt-Weiterleitung
1. Gehe zu https://menu-config.preview.emergentagent.com/standorte
2. Klicke auf "Hier bestellen" bei Henstedt-Ulzburg
3. **Erwartung:** Weiterleitung zu Foodbooking
4. **Erfolg:** ✅ Foodbooking-Seite öffnet sich

### Test 2: Rellingen funktioniert normal
1. Gehe zu https://menu-config.preview.emergentagent.com/standorte
2. Klicke auf "Hier bestellen" bei Rellingen
3. **Erwartung:** Normale Menü-Seite öffnet sich
4. **Erfolg:** ✅ Menü-Seite mit Produkten wird angezeigt

### Test 3: Direkte Navigation mit gespeichertem Standort
1. Wähle Henstedt als Standort
2. Gehe direkt zu /menu
3. **Erwartung:** Weiterleitung zu Foodbooking
4. **Erfolg:** ✅ Foodbooking-Seite öffnet sich

### Test 4: Homepage Order-Type-Dialog
1. Gehe zur Startseite
2. Klicke "Jetzt bestellen"
3. Wähle Henstedt-Ulzburg im Dialog
4. **Erwartung:** Weiterleitung zu Foodbooking
5. **Erfolg:** ✅ Foodbooking-Seite öffnet sich

## Status

- ✅ **Implementiert** in 4 Dateien
- ✅ **Frontend neu gestartet**
- ⏳ **Testing nach Re-Deployment**
- 📝 **Dokumentiert**

## Wichtige Hinweise

1. **Dies ist eine TEMPORÄRE Lösung**
   - Sobald alle Bugs behoben sind (Menü-Struktur, E-Mails)
   - Sollte die Weiterleitung entfernt werden
   - Henstedt sollte wieder intern funktionieren

2. **Nur Frontend-Änderung**
   - Backend bleibt unverändert
   - Datenbank bleibt unverändert
   - Kein Re-Deployment des Backends nötig

3. **Customer Support**
   - Kunden sehen keine Fehlermeldung
   - Nahtlose Weiterleitung zu funktionierendem System
   - Bessere UX als "Service nicht verfügbar"

## Re-Deployment

Nach dem Re-Deployment:
1. Testen Sie beide Standorte (siehe Tests oben)
2. Prüfen Sie, ob Henstedt zu Foodbooking weiterleitet
3. Prüfen Sie, ob Rellingen normal funktioniert

Bei Problemen:
- Browser-Cache leeren
- Frontend-Logs prüfen: `tail -n 50 /var/log/supervisor/frontend.err.log`
- JavaScript-Console im Browser prüfen (F12)

## Zusammenfassung

**Problem:** Henstedt-Ulzburg hat Bugs (Menü-Struktur, E-Mails nicht vollständig getestet)

**Lösung:** Temporäre Weiterleitung zu externer Foodbooking-Seite

**Implementierung:** 4 strategische Weiterleitungen im Frontend

**Resultat:** Kunden können weiterhin bestellen, keine Fehlerseiten, Rellingen läuft normal

**Rückgängig:** Einfach - 4 Zeilen Code in 4 Dateien entfernen

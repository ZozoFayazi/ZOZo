# 🚨 IONOS CACHE-PROBLEM - LÖSUNG

**Problem:** zozo-burger.de zeigt alte Version, obwohl mehrmals deployed  
**Ursache:** IONOS cached aggressiv (CDN + Server Cache)  
**Lösung:** Cache komplett leeren auf IONOS + Browser

---

## 🔥 SCHRITT-FÜR-SCHRITT LÖSUNG

### **Schritt 1: IONOS Cache leeren**

1. **Loggen Sie sich ein:**
   - Gehen Sie zu: https://www.ionos.de
   - Login mit Ihren Zugangsdaten

2. **Zu Ihrer Domain navigieren:**
   - Dashboard → "Domains & SSL"
   - Wählen Sie "zozo-burger.de"

3. **Performance-Cache leeren:**
   
   **Option A - Wenn Sie "Website & Domains" haben:**
   ```
   Website & Domains → zozo-burger.de
   → Performance & Caching
   → "Cache leeren" / "Purge Cache"
   → Bestätigen
   ```

   **Option B - Wenn Sie ein Hosting-Paket haben:**
   ```
   Hosting → Verwaltung
   → zozo-burger.de auswählen
   → Cache-Einstellungen
   → "Gesamten Cache leeren"
   ```

   **Option C - Wenn nichts davon sichtbar ist:**
   ```
   Kontaktieren Sie IONOS Support:
   - Telefon: 0721 254 47 10
   - Sagen Sie: "Bitte leeren Sie den kompletten Cache für zozo-burger.de"
   ```

---

### **Schritt 2: CDN deaktivieren (temporär)**

Falls IONOS ein CDN hat:

1. IONOS Dashboard
2. zozo-burger.de → CDN-Einstellungen
3. **Temporär deaktivieren** für 10 Minuten
4. Website neu laden
5. CDN wieder aktivieren

---

### **Schritt 3: Browser Cache KOMPLETT leeren**

**Auf ALLEN Geräten:**

1. **Chrome/Edge:**
   ```
   1. Drücken Sie: Strg + Shift + Delete
   2. Zeitraum: "Gesamte Zeit" auswählen
   3. Häkchen bei: "Bilder und Dateien im Cache"
   4. "Daten löschen"
   ```

2. **Dann HARD REFRESH:**
   ```
   Strg + F5
   ODER
   Strg + Shift + R
   ```

---

### **Schritt 4: DNS Cache leeren (auf Ihrem Computer)**

**Windows:**
```
1. CMD als Administrator öffnen
2. Eingeben: ipconfig /flushdns
3. Enter
4. "DNS-Auflösungscache wurde geleert" → Fertig!
```

**Mac:**
```
1. Terminal öffnen
2. Eingeben: sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
3. Passwort eingeben
```

---

### **Schritt 5: Inkognito-Modus testen**

1. Öffnen Sie einen **neuen Inkognito/Privat-Tab**:
   - Chrome: `Strg + Shift + N`
   - Firefox: `Strg + Shift + P`

2. Gehen Sie zu: `https://zozo-burger.de`

3. **Wenn es hier funktioniert:**
   - ✅ Problem ist NUR Browser-Cache
   - ❌ Leeren Sie Browser-Cache (Schritt 3)

4. **Wenn es hier NICHT funktioniert:**
   - ❌ Problem ist Server-seitiger Cache (IONOS)
   - ❌ Gehen Sie zu Schritt 1 zurück

---

### **Schritt 6: IONOS .htaccess Cache-Headers prüfen**

Falls Sie FTP/SSH-Zugriff haben:

1. Verbinden Sie sich via FTP zu IONOS
2. Suchen Sie die `.htaccess` Datei im Root-Verzeichnis
3. Fügen Sie hinzu (oder ändern Sie):

```apache
# Cache-Kontrolle deaktivieren (temporär zum Testen)
<IfModule mod_headers.c>
    Header set Cache-Control "no-cache, no-store, must-revalidate"
    Header set Pragma "no-cache"
    Header set Expires 0
</IfModule>

# ODER falls vorhanden, ändern Sie:
# ExpiresActive On
# ExpiresDefault "access plus 1 hour"
# 
# ZU:
# ExpiresActive Off
```

4. Speichern und Website neu laden

---

## 🔍 DEBUGGING - Welche Version läuft?

### **Test 1: Welcher Build wird geladen?**

1. Öffnen Sie zozo-burger.de
2. Drücken Sie `F12` (Developer Tools)
3. Gehen Sie zum **Network** Tab
4. Laden Sie die Seite neu (`F5`)
5. Suchen Sie nach `main.*.js`
6. Prüfen Sie die Hash-ID:

```
RICHTIG (neue Version):  main.d1c88417.js
FALSCH (alte Version):   main.[anderer-hash].js
```

**Wenn falsche Version:**
- → IONOS cached die JS-Dateien
- → Gehen Sie zurück zu Schritt 1

---

### **Test 2: Welche API wird verwendet?**

1. F12 → Console Tab
2. Eingeben:
   ```javascript
   console.log(process.env.REACT_APP_BACKEND_URL)
   ```
3. Prüfen Sie die URL:
   ```
   RICHTIG: https://site-refresh-58.preview.emergentagent.com
   ODER: Ihre Production Backend-URL
   ```

---

### **Test 3: Timestamp Check**

In der Browser-Console:
```javascript
// Prüfen Sie den Build-Timestamp
document.querySelector('script[src*="main"]').src
```

Vergleichen Sie die Hash-ID mit:
- Aktueller Build: `main.d1c88417.js`

---

## ⚡ SCHNELLSTE LÖSUNG - Cache-Buster URL

**Temporärer Workaround für Ihre Kunden:**

Teilen Sie diese URL statt zozo-burger.de:
```
https://zozo-burger.de/?v=20260121-1812&nocache=1
```

Der `?v=` und `?nocache=` Parameter umgehen den Cache!

**Testen Sie:**
```
https://zozo-burger.de/?v=20260121-1812
```

Wenn das funktioniert → Es ist definitiv ein Cache-Problem!

---

## 🆘 WENN NICHTS FUNKTIONIERT

### **Kontaktieren Sie IONOS Support:**

**Telefon:** 0721 254 47 10 (Deutsch)

**Sagen Sie denen:**
```
"Hallo, ich habe die Domain zozo-burger.de.
Ich habe mehrmals neu deployed, aber die alte Version
wird weiterhin angezeigt.

Bitte leeren Sie:
1. Den kompletten Server-Cache für zozo-burger.de
2. Den CDN-Cache (falls aktiv)
3. Alle Varnish/Redis-Caches

Meine Domain: zozo-burger.de
Kunde-ID: [Ihre IONOS Kunden-ID]
```

Sie sollten das innerhalb von 5 Minuten beheben können!

---

## 📞 ALTERNATIVE: Emergent Custom Domain neu verknüpfen

Falls zozo-burger.de über Emergent Custom Domain Feature verbunden ist:

1. **In diesem Dashboard hier:**
   - Schauen Sie nach "Settings" oder "Domains"
   - Prüfen Sie, ob "zozo-burger.de" aufgelistet ist

2. **Domain-Verknüpfung neu machen:**
   - Entfernen Sie zozo-burger.de
   - Warten Sie 2 Minuten
   - Fügen Sie zozo-burger.de wieder hinzu
   - Warten Sie 5 Minuten

---

## ✅ ERWARTETES RESULTAT

Nach erfolgreichem Cache-Leeren sollten Sie auf zozo-burger.de sehen:

- ✅ **Monster Bacon Burger** (nicht Pure Burger Salad)
- ✅ Neue Preise
- ✅ Admin Dashboard hat neue Features (Size Labels, Menu Config, Upsells)

---

**Probieren Sie ZUERST die Cache-Buster URL:** `https://zozo-burger.de/?v=20260121-1812`

Wenn das funktioniert, wissen wir: Es ist 100% ein IONOS-Cache-Problem! 🎯

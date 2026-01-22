# 🚨 NOTFALL-ANLEITUNG: Custom Domain Fix

**Erstellt:** 21.01.2026, 16:50 UTC  
**Problem:** zozo-burger.de zeigt falsche Version mit "Burger Menüs" Kategorie  
**Ursache:** Datenbank auf Production wurde überschrieben/geändert

---

## ✅ WAS ICH GETAN HABE

1. **Datenbank auf Preview-URL wiederhergestellt** (localhost/Preview funktioniert jetzt)
2. **Production-Restore-Script erstellt** → `/app/RESTORE_DATABASE_ON_PRODUCTION.py`
3. **Backup-Datei bereitgestellt** → `/app/backups/ABSOLUTE_FINAL_COMPLETE_FREEZE_20260121_105946.json`

---

## 🎯 SO BEHEBEN SIE DAS PROBLEM AUF ZOZO-BURGER.DE

### Option 1: Wenn Sie SSH-Zugriff auf den Production-Server haben

```bash
# 1. SSH auf Ihren Production-Server
ssh user@your-production-server.com

# 2. Navigieren Sie zum App-Verzeichnis
cd /pfad/zu/ihrer/app

# 3. Laden Sie das Backup hoch (von diesem Environment)
# Kopieren Sie diese beiden Dateien auf Ihren Production-Server:
#   - /app/backups/ABSOLUTE_FINAL_COMPLETE_FREEZE_20260121_105946.json
#   - /app/RESTORE_DATABASE_ON_PRODUCTION.py

# 4. Führen Sie das Restore-Script aus
python3 RESTORE_DATABASE_ON_PRODUCTION.py

# 5. Folgen Sie den Anweisungen im Script
#    (Es wird Sie um Bestätigung bitten und ein Emergency-Backup erstellen)

# 6. Starten Sie die Services neu
supervisorctl restart backend frontend
# ODER
systemctl restart your-app-service

# 7. Löschen Sie den CDN/Proxy Cache (falls vorhanden)
# (Kontaktieren Sie Ihren Hosting-Provider)
```

### Option 2: Wenn Sie ein Control Panel haben (z.B. cPanel, Plesk)

1. **Datenbank-Backup herunterladen:**
   - Laden Sie diese Datei herunter: `/app/backups/ABSOLUTE_FINAL_COMPLETE_FREEZE_20260121_105946.json`

2. **Via File Manager:**
   - Loggen Sie sich in Ihr Hosting Control Panel ein
   - Gehen Sie zu File Manager
   - Navigieren Sie zum Backup-Ordner Ihrer App
   - Laden Sie die JSON-Datei hoch

3. **MongoDB Restore via phpMyAdmin/MongoDB Manager:**
   - Öffnen Sie Ihr MongoDB Management Tool
   - Löschen Sie die aktuelle Datenbank (VORSICHT!)
   - Importieren Sie die Backup-JSON-Datei
   - Starten Sie die App-Services neu

### Option 3: Kontaktieren Sie Ihren Entwickler/Administrator

Falls Sie selbst keinen Zugriff haben:

**Senden Sie diese Nachricht an Ihren Admin:**

```
DRINGEND: Die Datenbank auf zozo-burger.de wurde mit einer falschen Version überschrieben.

Bitte führen Sie folgende Schritte aus:

1. Backup herunterladen von:
   https://menu-management-1.preview.emergentagent.com/backups/ABSOLUTE_FINAL_COMPLETE_FREEZE_20260121_105946.json

2. Auf dem Production-Server:
   - Backup in /app/backups/ ablegen
   - Script RESTORE_DATABASE_ON_PRODUCTION.py ausführen
   - Backend/Frontend neu starten

3. CDN/Proxy Cache leeren

Das Backup enthält die korrekte, eingefrorene Version vom 21.01.2026 10:59 Uhr
mit allen richtigen Produkten, Preisen und Größenangaben.
```

---

## 🔍 WIE SIE VERIFIZIEREN, DASS ES FUNKTIONIERT

Nach dem Restore auf zozo-burger.de:

### ✅ RICHTIG (So sollte es aussehen):

- **Burger Kategorie:** Zeigt einzelne Burger mit Größenauswahl
  - "Hamburger Medium (125g)" - €7.99
  - "Hamburger Large (180g)" - €11.19
- **KEINE** separate "Burger Menüs" Kategorie
- Beim Klick auf einen Burger: Größenauswahl (Medium/Large)
- Option "Zum Menü erweitern" verfügbar

### ❌ FALSCH (Wenn immer noch die alte Version):

- "Burger Menüs" als separate Kategorie
- Keine Größenangaben bei Produktnamen
- Nur ein Preis pro Burger

---

## 📞 FALLS ES NICHT FUNKTIONIERT

### Problem: Datei kann nicht hochgeladen werden
- **Lösung:** Backup ist 373KB groß. Falls zu groß für Upload: komprimieren Sie es erst (ZIP)

### Problem: MongoDB-Verbindungsfehler
- **Lösung:** Prüfen Sie MONGO_URL und DB_NAME in Ihren Environment Variables

### Problem: "Permission Denied"
- **Lösung:** Script braucht Schreibrechte. Führen Sie aus mit: `sudo python3 RESTORE_DATABASE_ON_PRODUCTION.py`

### Problem: Seite zeigt immer noch alte Version nach Restore
- **Lösung 1:** CDN/Proxy Cache muss geleert werden (Kontakt Hosting-Provider)
- **Lösung 2:** Hard Refresh in Browser: Strg+Shift+R (Windows) / Cmd+Shift+R (Mac)
- **Lösung 3:** Browser-Cache komplett löschen auf ALLEN Geräten

---

## 🛡️ WICHTIGE HINWEISE

1. **Emergency Backup:** Das Script erstellt automatisch ein Backup BEVOR es restored
   - Gespeichert als: `EMERGENCY_BEFORE_RESTORE_[timestamp].json`
   - Falls etwas schiefgeht, können Sie damit zurückrollen

2. **Datenverlust:** Alle Bestellungen/Änderungen NACH 21.01.2026 10:59 Uhr gehen verloren
   - Sie haben bestätigt, dass das okay ist

3. **Testen:** Nach dem Restore SOFORT testen:
   - Burger-Anzeige mit Größen
   - Warenkorb funktioniert
   - Bestellprozess funktioniert
   - POS-Integration sendet korrekte Daten

---

## 📂 DATEIEN ZUM HERUNTERLADEN

Wenn Sie die Dateien von diesem Environment auf Ihren Production-Server transferieren müssen:

1. **Backup-Datei (373KB):**
   ```
   /app/backups/ABSOLUTE_FINAL_COMPLETE_FREEZE_20260121_105946.json
   ```

2. **Restore-Script:**
   ```
   /app/RESTORE_DATABASE_ON_PRODUCTION.py
   ```

**Download-Methode (via SSH):**
```bash
# Vom Production-Server aus:
scp user@preview-server:/app/backups/ABSOLUTE_FINAL_COMPLETE_FREEZE_20260121_105946.json ./
scp user@preview-server:/app/RESTORE_DATABASE_ON_PRODUCTION.py ./
```

---

## ✅ CHECKLISTE NACH ERFOLGREICHER WIEDERHERSTELLUNG

- [ ] Backup auf Production-Server hochgeladen
- [ ] Restore-Script erfolgreich ausgeführt
- [ ] Backend/Frontend Services neu gestartet
- [ ] CDN/Proxy Cache geleert
- [ ] Browser-Cache auf allen Geräten gelöscht
- [ ] Burger zeigen Größenangaben (125g/180g)
- [ ] Keine "Burger Menüs" Kategorie sichtbar
- [ ] Testbestellung erfolgreich durchgeführt
- [ ] POS erhält korrekt "geflattete" Bestellungen

---

**Bei weiteren Fragen:** Kontaktieren Sie mich oder Ihren System-Administrator

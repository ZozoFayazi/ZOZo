# 🎯 WARUM MANCHE ÄNDERUNGEN NICHT DEPLOYED WERDEN

## Das Problem erklärt

**Es gibt 2 ARTEN von Änderungen:**

### 1. CODE-Änderungen ✅
**Werden bei Re-Deployment übernommen:**
- Frontend-Dateien (.jsx, .js, .css)
- Backend-Dateien (.py)
- Git-Commits

**Beispiele:**
- CheckoutDialog.jsx (Duplikat-Fixes)
- expertorder.py (Größen-Fixes)

**Wie übernommen:**
```
Git Repository → Deployed System ✅
```

### 2. DATENBANK-Änderungen ❌
**Werden NICHT automatisch übernommen:**
- PLZ-Listen
- Rabatt-Codes
- Produkte

**Beispiele:**
- PLZ 22457 hinzugefügt
- LUNCH20 Code erstellt

**Was passiert:**
```
Preview-Datenbank → Deployed System ❌
(NICHT übernommen!)
```

---

## Warum PLZ 22457 nicht funktioniert

**Preview-System:** PLZ 22457 in Datenbank ✅
**Deployed System:** PLZ 22457 NICHT in Datenbank ❌

**Separate Datenbanken!**

---

## Lösungen

### Lösung 1: Im Admin hinzufügen (EINFACH)

**Auf deployed System:**
```
1. Admin → Standorte → Rellingen
2. Liefergebiete → PLZ hinzufügen
3. "22457" eingeben
4. MBW €12.00
5. Speichern
6. ✅ Sofort aktiv!
```

### Lösung 2: Seed-Script nach Re-Deploy

**Ich erstelle Script:**
```bash
python /app/seed_production_data.py
```

**Macht alles automatisch:**
- Fügt 44 PLZ hinzu
- Fügt 13 Stadt-Regeln hinzu
- Erstellt LUNCH20 Code
- Initialisiert Burger Builder

---

## Zusammenfassung

**Code:** Re-Deploy übernimmt automatisch ✅
**Datenbank:** Muss manuell synchronisiert werden ⚠️

**Für PLZ 22457:**
1. Re-Deploy (Code)
2. DANN: PLZ im Admin hinzufügen (Datenbank)

**Oder:**
1. Re-Deploy (Code)
2. DANN: Seed-Script ausführen (Datenbank)

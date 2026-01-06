# 🧪 FINAL GO-LIVE SMOKE TEST

**Zweck:** Letzte Verifikation vor Production-Freigabe  
**Dauer:** ~5 Minuten  
**Wann:** NACH Blocker #3 & #4 abgeschlossen

---

## ✅ PRE-REQUISITES

Stelle sicher, dass folgende Punkte abgehakt sind:

- [x] Resend Domain: ✅ Verified
- [x] Super Admin 2FA: ✅ Aktiv
- [x] Passwörter: ✅ Alle geändert
- [x] JWT Secrets: ✅ Rotiert

**Wenn alle ✅, dann weiter mit Smoke Test:**

---

## 🧪 TEST 1: Live-Bestellung durchführen

### Schritt 1: Bestellung aufgeben
1. Öffne die Website als **Gast** (Inkognito-Modus)
2. Wähle Standort: Rellingen oder Henstedt
3. Füge mindestens 1 Produkt zum Warenkorb hinzu (Mindestbestellwert €12)
4. Gehe zur Kasse
5. Gib Testdaten ein:
   - Name: Test Kunde
   - Telefon: 0170 1234567
   - Adresse: Teststraße 1
   - PLZ: 25462 (Rellingen) oder 24558 (Henstedt)
   - Email: **deine echte Email!**
6. Zahlungsart: Bar
7. Klicke **"Kostenpflichtig bestellen"**

### Erwartetes Ergebnis:
- ✅ Bestellung erfolgreich (Bestätigungsseite)
- ✅ Bestellnummer erhalten (z.B. ZOZO-1026)

---

### Schritt 2: Email-Empfang prüfen

**Innerhalb von 30 Sekunden:**

- [ ] Bestellbestätigungs-Email erhalten
- [ ] **Absender korrekt:** `ZOZO Burger <noreply@zozo-burger.de>`
- [ ] NICHT im Spam-Ordner
- [ ] Email enthält: Bestellnummer, Artikel, Preis, Lieferadresse

**Screenshot für Abnahme:**
Email im Posteingang mit korrektem Sender

---

### Schritt 3: Admin-Panel Check

1. Login als Super Admin (mit 2FA!)
2. Gehe zu `/admin/orders`
3. Finde deine Test-Bestellung

**Erwartetes Ergebnis:**
- [ ] Bestellung sichtbar
- [ ] Status: `confirmed`
- [ ] POS Status: `sent` (wenn POS konfiguriert) oder `not_applicable` (wenn POS=none)
- [ ] Alle Daten korrekt (Name, Adresse, Items, Preis)

---

## 🧪 TEST 2: Cookie-Consent-Flow

### Schritt 1: Neue Session starten
1. Öffne Website in **Inkognito-Modus**
2. Warte auf Cookie-Banner (erscheint nach 1s)

**Erwartetes Ergebnis:**
- [ ] Banner erscheint unten
- [ ] 3 Buttons sichtbar: "Ablehnen" | "Einstellungen" | "Alle akzeptieren"

---

### Schritt 2: "Ablehnen" testen
1. Klicke **"Ablehnen"**
2. Gehe zu `/standorte`

**Erwartetes Ergebnis:**
- [ ] Cookie-Banner verschwindet
- [ ] Google Maps sind **PLACEHOLDER** (kein iFrame)
- [ ] Button "Karte laden & Standort anzeigen" sichtbar

---

### Schritt 3: Consent-Widerruf testen
1. Scrolle zum Footer
2. Klicke **"Cookie-Einstellungen"**
3. Schalte "Externe Medien" auf **ON**
4. Klicke **"Auswahl speichern"**
5. Reload Seite

**Erwartetes Ergebnis:**
- [ ] Google Maps lädt jetzt direkt (Consent vorhanden)
- [ ] iFrame sichtbar, Karten funktionieren

---

### Schritt 4: Erneuter Widerruf
1. Footer → "Cookie-Einstellungen"
2. Schalte "Externe Medien" auf **OFF**
3. Klicke **"Auswahl speichern"**
4. Reload Seite

**Erwartetes Ergebnis:**
- [ ] Maps sind wieder **PLACEHOLDER**
- [ ] Kein Google iFrame geladen

---

## 🧪 TEST 3: POS Integration

### Wenn POS konfiguriert (Cash-X oder ExpertOrder):

1. Admin-Panel → `/admin/pos`
2. Wähle Standort
3. Klicke **"Verbindung testen"**

**Erwartetes Ergebnis:**
- [ ] Connection Test: ✅ Erfolgreich (OK)
- [ ] Oder: Klare Fehlermeldung wenn POS offline

---

### Test-Bestellung POS-Status:

1. Finde die Test-Bestellung aus Test 1
2. Prüfe `pos_status` Feld

**Erwartetes Ergebnis:**
- [ ] `pos_status = "sent"` (wenn POS konfiguriert & online)
- [ ] `pos_status = "not_applicable"` (wenn POS=none)
- [ ] `pos_status = "error"` → Dann in `/admin/pos/failed-orders` prüfen

---

## 🧪 TEST 4: Footer-Links

Prüfe alle Footer-Links:

- [ ] `/impressum` - Lädt korrekt, Inhalt vollständig
- [ ] `/datenschutz` - Lädt korrekt, DSGVO-Infos sichtbar
- [ ] `/rechtliches` - Tabs funktionieren (AGB, Widerruf, Allergene)
- [ ] `/kontakt` - Kontaktdaten + Standorte sichtbar
- [ ] "Cookie-Einstellungen" - Dialog öffnet

---

## ✅ SMOKE TEST BESTANDEN WENN:

**Alle Checkboxen ✅:**

### Kritische Tests:
- [ ] **Bestellung:** Erfolgreich durchgeführt
- [ ] **Email:** Erhalten mit korrektem Sender
- [ ] **POS:** Status korrekt (sent/not_applicable)
- [ ] **Cookie-Banner:** Erscheint & funktioniert
- [ ] **Maps-Consent:** Ablehnen blockt, Accept lädt

### Wichtige Tests:
- [ ] **Footer-Links:** Alle Seiten erreichbar
- [ ] **Widerruf:** Cookie-Settings änderbar
- [ ] **Admin 2FA:** Login mit 2FA-Code funktioniert

---

## 📸 FINAL DELIVERABLES

Bitte liefern für finale Abnahme:

1. **Screenshot:** Bestellbestätigungs-Email (Sender: `ZOZO Burger <noreply@zozo-burger.de>`)
2. **Screenshot:** Admin Order-Details (POS Status sichtbar)
3. **Screenshot:** Cookie-Banner "Ablehnen" → Maps Placeholder
4. **Screenshot:** Resend Domain "Verified"
5. **Screenshot:** Security Dashboard (2FA aktiv)

---

## 🚀 NACH ERFOLGREICHER SMOKE TEST

**Wenn alle Tests ✅:**

→ **GO-LIVE FINAL FREIGEGEBEN** 🎉

**Nächste Schritte:**
1. Production URL aktivieren
2. DNS auf Production umstellen
3. Monitoring aktivieren (Sentry empfohlen)
4. Backup-Plan aktivieren (täglich)

---

## 🆘 WENN TESTS FEHLSCHLAGEN

**Email kommt nicht an:**
- Prüfe Resend Domain Status (muss "Verified" sein)
- Prüfe Spam-Ordner
- Prüfe Backend Logs: `tail -f /var/log/supervisor/backend.*.log`

**POS Status = error:**
- Gehe zu `/admin/pos/failed-orders`
- Prüfe Fehlermeldung
- Manueller Retry möglich
- Falls dauerhaft: POS-Konfiguration prüfen

**Cookie-Banner erscheint nicht:**
- localStorage clear: `localStorage.clear()` in Browser Console
- Reload Seite
- Banner sollte nach 1s erscheinen

**Maps laden ohne Consent:**
- 🚨 PROBLEM! Console Logs prüfen
- Falls iFrame direkt lädt: TDDDG-Verstoß!
- Kontakt Neo für Fix

---

**Viel Erfolg! 🚀**

*Smoke Test Guide erstellt: 06.01.2026*  
*Agent: Neo*

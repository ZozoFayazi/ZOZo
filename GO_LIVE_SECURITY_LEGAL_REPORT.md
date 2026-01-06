# 🔐 Go-Live: Sicherheits- & Rechts-Check Report

**Prüfungsdatum:** 06.01.2026  
**Status:** ⚠️ **KRITISCHE LÜCKEN - Go-Live BLOCKIERT**

---

## ❌ KRITISCHE GO-LIVE BLOCKER

Diese Punkte MÜSSEN vor Go-Live implementiert werden:

### 🚨 BLOCKER #1: DSGVO / Datenschutz-Pflichtseiten FEHLEN KOMPLETT

**Status:** ❌ **NICHT VORHANDEN**

**Was fehlt:**
- ❌ Impressum (§5 TMG / §18 MStV - gesetzliche Pflicht!)
- ❌ Datenschutzerklärung (Art. 13 DSGVO - Pflicht!)
- ❌ AGB / Widerruf / Speisen-Hinweise
- ❌ Kontaktseite mit klaren Angaben

**Rechtliches Risiko:** 🚨 **HOCH**
- Abmahnungen möglich (bis zu €5.000 pro Verstoß)
- DSGVO-Bußgelder (bis zu €20 Mio. oder 4% des Jahresumsatzes)
- Keine rechtssichere Geschäftsgrundlage

**Was zu tun ist:**
1. Impressum-Seite mit vollständigen Angaben (Firma, Adresse, Vertretung, Kontakt, Handelsregister, USt-IdNr.)
2. Datenschutzerklärung mit:
   - Datenerhebung (Name, Adresse, Email, Telefon für Bestellung)
   - Cookies & Tracking (auch wenn minimal)
   - Weitergabe an Dritte (POS-System, Email-Versand via Resend)
   - Betroffenenrechte (Auskunft, Löschung, Widerspruch)
   - Verantwortlicher + Datenschutzbeauftragter (falls Pflicht)
3. AGB mit:
   - Vertragsschluss (Button-Lösung)
   - Preise inkl. Lieferkosten
   - Widerrufsbelehrung (Ausschluss bei schnell verderblichen Lebensmitteln nach §312g BGB)
   - Haftungsausschluss / Gewährleistung
4. Kontaktseite oder klare Footer-Links

**Empfehlung:** Generator nutzen (z.B. eRecht24, IT-Recht Kanzlei) + Anwalts-Check

---

### 🚨 BLOCKER #2: Cookie-Banner FEHLT KOMPLETT

**Status:** ❌ **NICHT VORHANDEN**

**Aktueller Zustand:**
- ❌ Kein Cookie-Banner
- ❌ Keine Consent-Verwaltung
- ✅ Google Maps wird OHNE Einwilligung geladen (§25 TDDDG Verstoß!)

**Rechtliches Risiko:** 🚨 **HOCH**
- Verstoß gegen §25 TDDDG (Bußgeld bis €300.000)
- Abmahnfähig
- Planet49-Urteil: Opt-In vor Tracking zwingend

**Was zu tun ist:**

**Option 1: Cookie-Consent-Lösung (empfohlen)**
Library wie `react-cookie-consent` oder `cookie-consent-banner` installieren

**Banner 1. Ebene muss haben:**
- "Alle akzeptieren" Button
- "Ablehnen / Nur notwendige" Button (gleichwertig!)
- "Einstellungen" Button

**Banner 2. Ebene (Einstellungen):**
- ✅ Notwendig (locked, immer an)
- ⬜ Statistik/Analytics (opt-in)
- ⬜ Marketing (opt-in)
- ⬜ Externe Medien (Google Maps) (opt-in)
- "Speichern" + "Alles ablehnen" + "Alles akzeptieren"

**Option 2: Minimalistisch (wenn kein Tracking)**
- Banner nur mit "Verstanden" (aber: Google Maps muss trotzdem Consent!)
- Datenschutzerklärung klar kommunizieren

**Google Maps 2-Klick-Lösung:**
```jsx
{consent ? (
  <iframe src={googleMapsUrl} />
) : (
  <div>
    <p>Google Maps lädt Inhalte von externen Servern.</p>
    <button onClick={() => setConsent(true)}>Karte laden</button>
  </div>
)}
```

---

### 🚨 BLOCKER #3: Resend Domain NICHT VERIFIZIERT

**Status:** ⚠️ **TEST-MODUS AKTIV**

**Aktueller Zustand:**
```
RESEND_USE_TEST_DOMAIN=true
```
→ Emails werden von `onboarding@resend.dev` versendet (nicht von `noreply@zozo-burger.de`)

**Risiko:** 🟡 **MITTEL**
- Emails landen im Spam
- Sender nicht authentisch (Kunde sieht "resend.dev" statt "zozo-burger.de")
- Unvertrauenswürdig für Kunden

**Was zu tun ist:**
1. Domain `zozo-burger.de` bei Resend verifizieren:
   - https://resend.com/domains
   - DNS-Records hinzufügen (MX, TXT, DKIM)
2. In `.env` ändern:
   ```
   RESEND_USE_TEST_DOMAIN=false
   ```
3. Test-Email versenden und prüfen

---

### 🚨 BLOCKER #4: Admin Sicherheit UNZUREICHEND

**Status:** ⚠️ **TEILWEISE IMPLEMENTIERT**

**Aktueller Zustand:**
- ✅ 2FA Infrastruktur vorhanden
- ❌ 2FA bei Super Admin NICHT aktiviert (ist aber Pflicht!)
- ❌ Default-Passwörter noch aktiv (`ZozoAdmin2024!`)
- ⚠️ JWT Secret nicht sichtbar (gut), aber muss für Produktion rotiert werden

**Was zu tun ist:**
1. Super Admin 2FA MUSS aktiviert werden (per Policy erzwungen)
2. ALLE Admin-Passwörter vor Go-Live ändern (nicht das Default verwenden!)
3. JWT Secret für Produktion neu generieren (64+ Zeichen, kryptografisch sicher)

---

## ⚠️ WICHTIGE MÄNGEL (Go-Live möglich, aber dringend nachbessern)

### ⚠️ #1: Keine DSGVO-Prozesse definiert

**Was fehlt:**
- ❌ Löschkonzept (Aufbewahrungsfristen für Bestellungen, Logs, Accounts)
- ❌ Auskunfts-/Löschungs-Flow für Kunden
- ❌ AV-Verträge (Auftragsverarbeitung) mit:
  - Hosting-Provider (Emergent)
  - Resend (Email-Versand)
  - POS-System (Cash-X, ExpertOrder)

**Was zu tun ist:**
1. **Löschkonzept erstellen:**
   - Bestellungen: 10 Jahre Aufbewahrung (Steuerrecht), dann Auto-Delete
   - Logs: 90 Tage, dann Auto-Delete
   - Inaktive Accounts: 2 Jahre, dann Löschung
   - Implementierung: Cronjob für Auto-Delete

2. **Auskunft/Löschung:**
   - Admin-Panel: Funktion "Kundendaten exportieren"
   - Admin-Panel: Funktion "Kunde löschen (DSGVO-konform)"
   - Oder: Prozess dokumentieren (Email an info@, manuell prüfen, löschen)

3. **AV-Verträge:**
   - Bei jedem Drittanbieter anfragen (Standard-Formular)
   - Dokumentieren + Ablage

---

### ⚠️ #2: Monitoring / Error Tracking fehlt

**Status:** ❌ **NICHT VORHANDEN**

**Risiko:**
- Fehler werden zu spät erkannt
- Keine Benachrichtigung bei System-Ausfällen
- Debugging in Produktion schwierig

**Empfehlung:**
- Sentry.io (Frontend + Backend) - kostenlose Tier verfügbar
- Alternative: LogRocket, Rollbar

---

### ⚠️ #3: Backups nicht verifiziert

**Status:** ⚠️ **UNKLAR**

**Was fehlt:**
- Backup-Plan für MongoDB
- Restore-Test (mind. 1x durchführen!)

**Was zu tun ist:**
1. Mongo Backup-Script (täglich, automatisch)
2. Retention: 7 Tage täglich, 4 Wochen wöchentlich
3. Restore-Test durchführen + dokumentieren

---

## ✅ WAS BEREITS GUT IST

### ✅ Sicherheit (Teilweise)

- ✅ Secrets in ENV (nicht im Code)
- ✅ Admin-Auth mit JWT
- ✅ Rate Limiting aktiv (Login Lockout, API Limit)
- ✅ Must-Change-Password erzwungen
- ✅ 2FA Infrastruktur vorhanden

### ✅ Checkout Flow (Rechtlich solide)

- ✅ Preisangaben klar (inkl. Lieferkosten)
- ✅ Mindestbestellwert vor Checkout sichtbar
- ✅ Button: "Kostenpflichtig bestellen" (Button-Lösung konform)
- ✅ Bestellbestätigung per Email
- ✅ Gastbestellung möglich (kein Account-Zwang)

### ✅ Datenminimierung

- ✅ Nur notwendige Daten abgefragt (Name, Adresse, Telefon, Email)
- ✅ Keine überflüssigen Datenerhebungen

---

## 🎯 ZUSAMMENFASSUNG: WAS JETZT ZU TUN IST

### Kritische Go-Live Blocker (MUST-HAVE vor Live):

1. **Impressum + Datenschutzerklärung + AGB erstellen** (rechtlich zwingend!)
2. **Cookie-Banner implementieren** (§25 TDDDG, Planet49-konform)
3. **Google Maps 2-Klick-Lösung** (Consent vor Laden)
4. **Resend Domain verifizieren** (zozo-burger.de)
5. **Admin-Sicherheit härten:**
   - Super Admin 2FA aktivieren
   - Alle Passwörter ändern
   - JWT Secret rotieren

### Wichtig (sollte schnell nachgeholt werden):

6. **DSGVO-Prozesse definieren** (Löschkonzept, Auskunft, AV-Verträge)
7. **Monitoring einrichten** (Sentry)
8. **Backup-Plan + Restore-Test**

---

## 📋 Deliverables für Abnahme

**Noch zu liefern:**

1. ❌ Screenshot Cookie-Banner (1. Layer + Einstellungen) - **NICHT VORHANDEN**
2. ❌ Screenshot Maps Placeholder + Consent Flow - **NICHT VORHANDEN**
3. ❌ Link/Route zu Impressum/Datenschutz - **NICHT VORHANDEN**
4. ⚠️ Resend Domain Verification Status - **TEST-MODUS**
5. ✅ Security Checkliste - **DIESES DOKUMENT**

---

## ✅ FAZIT

**Go-Live Status:** 🚨 **BLOCKIERT**

**Grund:**
- Rechtliche Pflichtseiten fehlen komplett (Impressum, Datenschutz, AGB)
- Cookie-Banner fehlt (TDDDG-Verstoß)
- Google Maps ohne Consent (abmahnfähig)

**Geschätzter Aufwand zur Behebung:**
- Rechtstexte: 2-4 Stunden (mit Generator + Anpassung)
- Cookie-Banner: 3-4 Stunden (Implementierung + Tests)
- Maps 2-Klick: 1-2 Stunden
- Resend Domain: 30 Min (+ DNS-Wartezeit)
- Admin Security: 30 Min

**Total:** ~1 Arbeitstag

**Nach Behebung:** Go-Live technisch möglich, aber DSGVO-Prozesse sollten zeitnah nachgereicht werden.

---

**Status:** ⚠️ **ACTION REQUIRED**  
**Nächster Schritt:** Blocker #1-5 beheben, dann erneuter Check

---

*Geprüft: 06.01.2026*  
*Agent: Neo*

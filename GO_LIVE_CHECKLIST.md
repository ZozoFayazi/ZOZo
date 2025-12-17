# ZOZO Burger - Go-Live Checkliste

## Status: IN BEARBEITUNG 🔄

---

## 1. Environment-Konfiguration

### Backend (.env)
- [ ] MONGO_URL - Produktions-DB konfiguriert
- [ ] JWT_SECRET_KEY - Sicherer Key (nicht Default)
- [ ] CORS Origins - Produktions-Domain eingetragen
- [ ] Debug Mode - Deaktiviert

### Frontend (.env)
- [ ] REACT_APP_BACKEND_URL - Produktions-URL

### Allgemein
- [ ] Keine hardcodierten Test-Credentials
- [ ] Keine Debug-Logs in Produktion
- [ ] Error-Handling für alle kritischen Pfade

---

## 2. ExpertOrder POS

### Aktueller Status
- [x] Testmodus implementiert
- [x] Connector-Architektur bereit
- [ ] Produktions-Credentials eingepflegt
- [ ] Live-Modus getestet

### Vor Go-Live
- [ ] Merchant ID (Produktion)
- [ ] API Key (Produktion)
- [ ] Base URL (Produktion)
- [ ] Test-Bestellung im Live-Modus

---

## 3. Admin-Sicherheit

### Passwörter
- [ ] Default-Passwort geändert: admin@zonik-solutions.de
- [ ] Default-Passwort geändert: info@zozo-burger.de
- [ ] Default-Passwort geändert: henstedt@zozo-burger.de
- [ ] mustChangePassword Flag aktiv bei allen Admins

### 2FA
- [ ] Super Admin: 2FA aktiviert
- [ ] Backup-Codes sicher gespeichert

### Rate-Limiting
- [x] Admin Login: 3 Versuche / 30 Min Lockout
- [x] Bestellungen: 10/Stunde/IP
- [x] API General: 100/Minute/IP

---

## 4. Datenbank & Backup

### MongoDB
- [ ] Produktions-Cluster konfiguriert
- [ ] Backup-Strategie dokumentiert
- [ ] Point-in-Time Recovery aktiviert
- [ ] Index-Optimierung geprüft

### Collections
- [x] admins
- [x] locations
- [x] menu_items
- [x] categories
- [x] orders
- [x] audit_logs
- [x] pos_logs
- [x] security_events

---

## 5. Monitoring & Logs

### Logging
- [x] Audit-Logs für Admin-Aktionen
- [x] POS-Logs für Bestellungen
- [x] Security-Events für Rate-Limiting
- [ ] Error-Alerting konfiguriert

### Monitoring
- [ ] Health-Check Endpoint
- [ ] Uptime-Monitoring
- [ ] Response-Time Tracking

---

## 6. Smoke-Tests

### Bestellung → POS
- [ ] Neue Bestellung erstellen
- [ ] POS-Push erfolgt (oder Fallback)
- [ ] Order-Status korrekt
- [ ] POS-Log erstellt

### Login + 2FA
- [ ] Admin-Login funktioniert
- [ ] 2FA-Verifizierung funktioniert
- [ ] Backup-Code funktioniert
- [ ] Rate-Limiting greift bei Fehlversuchen

### Toggle Produkt / Standort
- [ ] Produkt aktivieren/deaktivieren
- [ ] Standort aktivieren/deaktivieren
- [ ] Änderungen sofort sichtbar

### Öffentliche Standortseiten
- [ ] /standorte lädt korrekt
- [ ] /standorte/rellingen lädt korrekt
- [ ] /standorte/henstedt-ulzburg lädt korrekt
- [ ] JSON-LD Schema vorhanden
- [ ] Meta-Tags korrekt

---

## 7. Performance

- [ ] Bilder optimiert (WebP, Kompression)
- [ ] Lazy Loading aktiviert
- [ ] Bundle-Size geprüft
- [ ] API Response Times < 500ms

---

## 8. SEO Final Check

- [ ] robots.txt konfiguriert
- [ ] sitemap.xml generiert
- [ ] Canonical URLs korrekt
- [ ] Open Graph Tags vollständig

---

## 9. Rechtliches

- [ ] Impressum
- [ ] Datenschutzerklärung
- [ ] Cookie-Banner (falls erforderlich)
- [ ] AGB (falls erforderlich)

---

## Sign-Off

| Prüfer | Datum | Status |
|--------|-------|--------|
| Entwickler | | |
| QA | | |
| Kunde | | |

---

*Letzte Aktualisierung: 17.12.2025*

# 📧 Resend Domain-Verifizierung Anleitung

**Domain:** `zozo-burger.de`  
**Ziel:** Emails von `noreply@zozo-burger.de` versenden (statt `onboarding@resend.dev`)

---

## 🎯 Schritt-für-Schritt Anleitung

### 1. Resend Dashboard öffnen

1. Gehe zu: **https://resend.com/domains**
2. Login mit deinem Resend-Account
3. Klicke auf **"Add Domain"**

---

### 2. Domain hinzufügen

1. Gib `zozo-burger.de` ein
2. Klicke **"Add Domain"**
3. Resend zeigt dir jetzt die erforderlichen DNS-Records

---

### 3. DNS-Records bei deinem Domain-Provider setzen

**Du benötigst Zugang zu deinem Domain-Provider** (z.B. Strato, 1&1, GoDaddy, Cloudflare, etc.)

Resend wird dir **3 verschiedene DNS-Records** anzeigen:

#### A) SPF Record (TXT)

**Beispiel:**
```
Type: TXT
Name: @ (oder leer)
Value: v=spf1 include:send.resend.com ~all
TTL: 3600
```

**Was tun:**
- Gehe zu DNS-Einstellungen deines Providers
- Füge einen **TXT Record** hinzu
- Setze die Werte wie von Resend angezeigt

---

#### B) DKIM Record (CNAME)

**Beispiel:**
```
Type: CNAME
Name: resend._domainkey (oder wie von Resend angezeigt)
Value: resend._domainkey.u.resend.com
TTL: 3600
```

**Was tun:**
- Füge einen **CNAME Record** hinzu
- Name: Exakt wie von Resend angezeigt (meist `resend._domainkey`)
- Value: Exakt wie von Resend angezeigt

---

#### C) DMARC Record (TXT) - Optional, aber empfohlen

**Beispiel:**
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc@zozo-burger.de
TTL: 3600
```

**Was tun:**
- Füge einen **TXT Record** hinzu
- Name: `_dmarc`
- Value: Wie oben oder von Resend empfohlen

---

### 4. DNS-Propagation warten

Nach dem Hinzufügen der Records:

- ⏱️ **Wartezeit:** 5-30 Minuten (manchmal bis zu 48 Stunden)
- ✅ **Status prüfen:** Resend zeigt "Verified" Badge an
- 🔄 **Refresh:** Aktualisiere die Resend-Seite alle paar Minuten

**Status-Check via CLI:**
```bash
dig TXT zozo-burger.de
dig CNAME resend._domainkey.zozo-burger.de
```

---

### 5. Verifizierung in Resend prüfen

1. Gehe zurück zu **https://resend.com/domains**
2. Bei `zozo-burger.de` sollte jetzt stehen:
   - ✅ **Status: Verified** (grüner Badge)
   - ✅ SPF: Verified
   - ✅ DKIM: Verified
   - ✅ (Optional) DMARC: Verified

---

### 6. Test-Email senden

**Nach erfolgreicher Verifizierung:**

```bash
cd /app/backend
python3 test_emails.py
```

**Erwartetes Ergebnis:**
- ✅ Email kommt an
- ✅ Absender: `ZOZO Burger <noreply@zozo-burger.de>`
- ✅ NICHT im Spam-Ordner

---

## 📸 Screenshot für Abnahme

Bitte mache einen Screenshot von:

1. **Resend Dashboard** mit "Verified" Status:
   - `zozo-burger.de` - ✅ Verified
   - SPF ✅ DKIM ✅ DMARC ✅

2. **Email im Posteingang:**
   - Absender: `ZOZO Burger <noreply@zozo-burger.de>`
   - Betreff: "Test-Email von ZOZO Burger"
   - Body: Enthält ZOZO Logo + Text

---

## ⚠️ Häufige Probleme

### Problem: DNS-Records werden nicht übernommen

**Lösung:**
- Warte länger (DNS Propagation kann bis zu 48h dauern)
- Prüfe, ob TTL zu hoch ist (setze auf 3600 oder niedriger)
- Lösche alte/widersprüchliche Records

### Problem: SPF Record existiert bereits

**Lösung:**
- Wenn bereits ein SPF Record existiert, NICHT ersetzen!
- Stattdessen erweitern:
  ```
  Alt: v=spf1 include:_spf.google.com ~all
  Neu: v=spf1 include:_spf.google.com include:send.resend.com ~all
  ```

### Problem: Emails landen im Spam

**Lösung:**
- DMARC Record hinzufügen (falls noch nicht)
- Warte auf vollständige DKIM-Verifizierung
- Teste mit verschiedenen Email-Providern (Gmail, Outlook, etc.)

---

## ✅ Nach erfolgreicher Verifizierung

**In deiner ENV:**
```
RESEND_USE_TEST_DOMAIN=false ✅ (bereits gesetzt)
SENDER_EMAIL=noreply@zozo-burger.de ✅ (bereits gesetzt)
```

**Bestätige:**
- ✅ Domain Status: Verified
- ✅ Test-Email erfolgreich versendet
- ✅ Sender korrekt: `ZOZO Burger <noreply@zozo-burger.de>`

**Dann ist Blocker #3 final abgeschlossen!** ✅

---

*Anleitung erstellt: 06.01.2026*  
*Agent: Neo*

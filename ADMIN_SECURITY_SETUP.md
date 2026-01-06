# 🔐 Admin Security: Go-Live Checkliste

**Status:** ⚠️ **MANUELLE AKTIONEN ERFORDERLICH**  
**Datum:** 06.01.2026

---

## 🚨 PFLICHT VOR GO-LIVE

Diese 3 Schritte MÜSSEN vor Go-Live durchgeführt werden:

### 1. Super Admin 2FA aktivieren ✅ (PFLICHT!)

**Warum:** Super Admin hat vollen Zugriff auf das System. 2FA ist Pflicht.

**Wie:**
1. Login als Super Admin: `admin@zonik-solutions.de`
2. Gehe zu: `/admin/security` (oder direkt nach Login → "2FA Setup" Dialog erscheint)
3. Klicke **"2FA jetzt einrichten"**
4. Scanne QR-Code mit Authenticator-App (Google Authenticator, Authy, Microsoft Authenticator)
5. Gib den 6-stelligen Code ein → **"Bestätigen"**
6. **Speichere die Backup-Codes!** (wichtig für Account-Recovery)

**Status prüfen:**
```
GET /api/admin/auth/2fa/status
```

**Erwartetes Ergebnis:**
```json
{
  "totp_enabled": true,
  "backup_codes_remaining": 10
}
```

**Screenshot für Abnahme:**
- Security Dashboard mit "2FA: ✅ Aktiv" Badge

---

### 2. Default-Passwörter ändern ✅ (PFLICHT!)

**Aktuell:** Alle 3 Admins haben `ZozoAdmin2024!` (DEFAULT - unsicher!)

**Admins:**
1. `admin@zonik-solutions.de` (Super Admin)
2. `info@zozo-burger.de` (Rellingen Admin)
3. `henstedt@zozo-burger.de` (Henstedt Admin)

**Wie:**
1. Login als jeweiliger Admin
2. Dialog "Passwort ändern" erscheint automatisch (`must_change_password: true`)
3. Gib aktuelles Passwort ein: `ZozoAdmin2024!`
4. Gib neues, starkes Passwort ein (mind. 8 Zeichen, komplex)
5. Bestätigen

**Status prüfen:**
```bash
# Check in DB
python3 -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['test_database']
    admins = await db.admins.find({}).to_list(10)
    for admin in admins:
        print(f'{admin[\"email\"]}: must_change={admin.get(\"must_change_password\", True)}')
    client.close()

asyncio.run(check())
"
```

**Erwartetes Ergebnis:**
```
admin@zonik-solutions.de: must_change=False
info@zozo-burger.de: must_change=False
henstedt@zozo-burger.de: must_change=False
```

**Alternative:** Passwörter im Admin-Panel unter `/admin/security/change-password` ändern

---

### 3. JWT Secrets rotiert ✅ (FERTIG!)

**Status:** ✅ **BEREITS ROTIERT**

**Neue Secrets generiert (06.01.2026):**
```
JWT_SECRET=uKoRwC3BpBOQmf_XfTD5QdtU3fTuxTgBjvbPnTGAngjAReUUIDJirlPLcwxGwgNync49zQly0-_1Md_oknHvJw (86 Zeichen)
ADMIN_JWT_SECRET=eGOlbffRwRjsTGcKja83e6Bt5yJdrF0Wg_6jat3Q6TPj5hGWuVKewbamL4RUV2DDuP0l-_DJ49LGHEk7Lv9fag (86 Zeichen)
```

**Länge:** 86 Zeichen (✅ > 64 Zeichen Minimum)  
**Entropy:** 516 Bits (✅ kryptografisch sicher)

**Backend neu gestartet:** ✅ Ja (`supervisorctl restart backend`)

**⚠️ Wichtig:**
Nach Rotation müssen ALLE Admins sich neu einloggen (alte Tokens ungültig).

---

## 📋 Checkliste

### Vor Go-Live (PFLICHT):

- [ ] **1. Super Admin 2FA aktiviert**
  - [ ] QR-Code gescannt
  - [ ] Code verifiziert
  - [ ] Backup-Codes gespeichert
  - [ ] Status: `totp_enabled: true`

- [ ] **2. Admin-Passwörter geändert**
  - [ ] admin@zonik-solutions.de: Neues PW ✓
  - [ ] info@zozo-burger.de: Neues PW ✓
  - [ ] henstedt@zozo-burger.de: Neues PW ✓
  - [ ] Status: `must_change_password: false` (alle)

- [x] **3. JWT Secrets rotiert**
  - [x] JWT_SECRET: 86 Zeichen ✓
  - [x] ADMIN_JWT_SECRET: 86 Zeichen ✓
  - [x] Backend neu gestartet ✓

### Nach Go-Live (empfohlen):

- [ ] **Rate Limiter auf Redis umstellen** (aktuell In-Memory)
- [ ] **Session-Timeout konfigurieren** (z.B. 8 Stunden)
- [ ] **Admin-Aktivitäten monitoren** (via Audit Logs)
- [ ] **Regelmäßige Security-Audits** (monatlich)

---

## 🔐 Passwort-Anforderungen

**Minimum:**
- 8 Zeichen
- Mind. 1 Großbuchstabe
- Mind. 1 Kleinbuchstabe
- Mind. 1 Zahl

**Empfohlen:**
- 12+ Zeichen
- Sonderzeichen
- Keine Wörterbuchwörter
- Einzigartig (nicht bei anderen Diensten verwendet)

**Generator:**
```bash
python3 -c "import secrets, string; chars = string.ascii_letters + string.digits + '!@#$%^&*'; print(''.join(secrets.choice(chars) for _ in range(16)))"
```

---

## 🎯 2FA Backup-Codes

**Nach 2FA-Setup erhältst du 10 Backup-Codes.**

**Wichtig:**
- ✅ Sichere Aufbewahrung (Passwort-Manager, verschlüsseltes File)
- ✅ Jeder Code kann NUR 1x verwendet werden
- ✅ Neue Codes generieren wenn < 3 übrig

**Backup-Codes regenerieren:**
```
POST /api/admin/auth/2fa/regenerate-backup-codes
```

**2FA deaktivieren (Notfall):**
- Nur Super Admin kann 2FA für andere deaktivieren
- Super Admin kann EIGENE 2FA NICHT deaktivieren (Security-Policy)

---

## 📸 Screenshots für Abnahme

Bitte liefern:

1. **Security Dashboard:**
   - Super Admin 2FA Status: ✅ Aktiv
   - Alle Admins: must_change_password: false

2. **2FA QR-Code Dialog** (während Setup):
   - QR-Code sichtbar
   - Backup-Codes angezeigt

3. **Login mit 2FA:**
   - Nach Passwort-Eingabe → 2FA-Code-Eingabe
   - Erfolgreicher Login

---

## ✅ Nach Abschluss

**Blocker #4 ist gelöst wenn:**
- ✅ Super Admin 2FA aktiv
- ✅ Alle 3 Admin-Passwörter geändert
- ✅ JWT Secrets rotiert (bereits done!)

**Dann:** 🚀 **BLOCKER #4 ABGESCHLOSSEN**

---

## 🆘 Support

**Bei Problemen:**

**2FA-Code funktioniert nicht:**
- Prüfe Smartphone-Zeit (muss synchron sein!)
- Verwende Backup-Code stattdessen
- Kontakt: Super Admin kann 2FA zurücksetzen

**Passwort vergessen:**
- Aktuell: Kein Self-Service (TODO)
- Workaround: Super Admin setzt neues Passwort in DB

**Ausgesperrt:**
- Backup-Codes verwenden
- Oder: Direkter DB-Zugriff (mongo shell → 2FA temporär deaktivieren)

---

*Anleitung erstellt: 06.01.2026*  
*Agent: Neo*

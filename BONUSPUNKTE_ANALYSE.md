# BONUSPUNKTE-SYSTEM: Analyse & Dokumentation

**Analysiert am:** 2025-01-14  
**Status:** ⚠️ KRITISCHER BUG GEFUNDEN (PayPal-Flow)

---

## 1. PUNKTE SAMMELN

### Regel
- **10€ Bestellwert = 1 Bonuspunkt**
- Berechnung erfolgt auf dem **Endtotal** (NACH allen Rabatten: Pickup 10%, Daily Deals, Punkte-Rabatt)

### Beispiele
- Bestellung 19,90€ → **1 Punkt** (int(19.90 / 10) = 1)
- Bestellung 29,50€ → **2 Punkte** (int(29.50 / 10) = 2)
- Bestellung 9,90€ → **0 Punkte** (int(9.90 / 10) = 0)

### Rundung
- **Immer abrunden** (int-Konvertierung)
- Code: `points_earned = int(total / 10)`

---

## 2. ZEITPUNKT DER GUTSCHRIFT

### ✅ Cash/Kartenzahlung
**Sofort nach Bestellung erstellt** (Zeile 1681-1688 in server.py)
```python
points_earned = int(total / 10)
if points_earned > 0:
    await add_points_to_account(
        customer_email,
        points_earned,
        f"Verdient bei Bestellung {order_number}",
        order_id=str(result.inserted_id)
    )
```

### ❌ KRITISCHER BUG: PayPal-Flow
**KEINE PUNKTE-VERGABE!**

Das PayPal-Capture-Endpoint (`/api/paypal/capture-order`, Zeile 942-1109) erstellt zwar die finale Bestellung, aber **vergisst komplett** die Loyalty-Logik:
- ❌ Keine Punktevergabe
- ❌ Keine Achievements-Check
- ❌ Keine Transaktionen

**Was passiert:**
1. PayPal-Zahlung erfolgreich
2. Finale Bestellung wird erstellt
3. POS-Push erfolgt
4. **Punkte-System wird komplett übersprungen**

---

## 3. EINLÖSEN

### Mechanismus
- **1 Punkt = 0,50€ Rabatt**
- Einlösung erfolgt als Checkout-Rabatt

### Frontend
- Slider im Checkout-Dialog (CheckoutDialog.jsx, Zeile 782-807)
- Maximal einlösbar: `Math.min(account.points, Math.floor(total / 0.50))`
- User kann nicht mehr Rabatt erhalten als die Bestellung kostet

### Backend-Validierung
1. Prüfung ob genug Punkte vorhanden (Zeile 1586)
2. Punkte-Abzug (Zeile 1669-1675)
3. Rabatt wird vom Total abgezogen (Zeile 1598)

### Einschränkungen
- ✅ Teil-Einlösung möglich (Slider 0 bis max)
- ❌ **Kombinierbar mit anderen Rabatten:** JA (Pickup 10%, Daily Deals)
- ⚠️ Mindestpunkte: Technisch 0, aber 1 Punkt = 0,50€ ergibt nur bei mind. 2 Punkten = 1€ Sinn

---

## 4. SICHTBARKEIT

### Für Kunden

#### a) Checkout-Dialog (CheckoutDialog.jsx)
- **Wo:** Nach Email-Eingabe wird Loyalty-Account geladen
- **Anzeige:** "Verfügbar: X Punkte (€Y.YY)"
- **Slider:** Zum Einlösen

#### b) Rewards-Seite (/rewards)
- **Zugriff:** Header → "MEHR" → "🎁 Belohnungen"
- **LoyaltyPoints Component:** Zeigt aktuellen Stand, Gesamt verdient, Gesamt ausgegeben
- **Tabs:** Belohnungen, Achievements, Historie

#### c) Nach Bestellung
- **Toast-Benachrichtigung:** "🎉 X Treuepunkte verdient!" (NUR bei Cash/Karte, NICHT bei PayPal wegen Bug!)

#### d) Email-Bestätigung
- ❓ **Unklar** - Code-Referenz zu `email_service.py` vorhanden, aber Punkte-Display nicht verifiziert

### Admin-Sichtbarkeit
- ❌ Kein Admin-Dashboard für Loyalty-Verwaltung erkennbar
- ✅ Direkter DB-Zugriff: Collection `loyalty_accounts`

---

## 5. SCOPE

### Pro Tenant (NICHT pro Filiale!)
- **Collection:** `loyalty_accounts`
- **Key:** `customer_email` (String)
- **Filial-unabhängig:** Ein Kunde hat EIN Punkte-Konto für alle Standorte

### Standortwechsel
- **Kein Problem:** Punkte sind global
- Kunde bestellt in Rellingen → 10 Punkte
- Kunde bestellt in Henstedt → kann diese 10 Punkte einlösen

---

## 6. PERSISTENZ & SICHERHEIT

### Datenbank-Schema

#### Collection: `loyalty_accounts`
```json
{
  "customer_email": "kunde@example.com",
  "points": 42,           // Aktueller Stand
  "total_earned": 150,    // Lifetime verdient
  "total_spent": 108,     // Lifetime ausgegeben
  "achievements": ["first_order", "loyal_customer"],
  "created_at": ISODate(...),
  "updated_at": ISODate(...)
}
```

#### Collection: `loyalty_transactions`
```json
{
  "customer_email": "kunde@example.com",
  "type": "earned" | "spent",
  "points": 5,
  "description": "Verdient bei Bestellung ZOZO-1234",
  "order_id": "...",
  "related_achievement": "first_order" | null,
  "created_at": ISODate(...)
}
```

### Restart/Deploy Sicherheit
✅ **Persistent:** Daten liegen in MongoDB, überleben Restarts

### Client vs Server
✅ **Server-seitig:** Alle Berechnungen auf Backend
- Frontend sendet nur `points_to_redeem` (Integer)
- Backend prüft ob genug Punkte vorhanden
- Backend zieht Punkte ab und schreibt Transaction
- ❌ **Manipulation nicht möglich:** Client kann nicht "fake points" senden

---

## 7. ACHIEVEMENTS-SYSTEM

### Verfügbare Achievements
1. **Erster Biss** - Erste Bestellung → +5 Punkte
2. **Stammkunde** - 10 Bestellungen → +10 Punkte
3. **Burger-Meister** - 50 Burger bestellt → +20 Punkte
4. **Mitternachts-Snacker** - Bestellung nach 22 Uhr → +5 Punkte
5. **Vielfalt-Lover** - 3+ Kategorien in einer Bestellung → +8 Punkte
6. **Custom King** - 5 eigene Burger kreiert → +15 Punkte
7. **Großbestellung** - Bestellung über 50€ → +25 Punkte

### Achievement-Bonus
- Werden automatisch bei Bestellung geprüft
- **Bonus-Punkte werden ZUSÄTZLICH zu den Bestell-Punkten vergeben**
- ⚠️ **PayPal-Bug gilt auch hier:** Keine Achievement-Checks bei PayPal-Bestellungen!

---

## 8. KRITISCHE BUGS

### 🚨 BUG #1: Cash/Karte - Email-Check crasht Loyalty-System
**Datei:** `/app/backend/server.py` Zeile 1663  
**Fehler:** `'CustomerInfo' object has no attribute 'email'`

**Problem:**  
```python
customer_email = order.customer.email  # Zeile 1663
# Aber: email ist Optional[str] in CustomerInfo!
# Wenn email = None → AttributeError → try-catch schluckt es → keine Punkte
```

**Impact:**  
- **ALLE Bestellungen ohne Email:** Keine Punkte gutgeschrieben
- **ALLE Bestellungen mit eingelösten Punkten aber ohne Email:** Punkte werden NICHT abgezogen (Betrug möglich!)
- Error wird "silent" geloggt, User bekommt keine Fehlermeldung

**Fix notwendig:** JA (KRITISCH - P0)

---

### 🚨 BUG #2: PayPal-Bestellungen vergeben KEINE Punkte
**Datei:** `/app/backend/server.py`  
**Endpoint:** `/api/paypal/capture-order` (Zeile 942-1109)  

**Problem:**  
Der PayPal-Capture-Flow erstellt die finale Bestellung, aber die komplette Loyalty-Logik fehlt:
```python
# NACH Zeile 1048 (draft finalized) FEHLT:
# - Punkte-Abzug für eingelöste Punkte
# - Punkte-Vergabe für die Bestellung
# - Achievements-Check
```

**Impact:**  
- Kunden die mit PayPal zahlen erhalten **KEINE Bonuspunkte**
- Eingelöste Punkte werden **NICHT abgezogen** (schwerer Fehler!)
- Achievements werden **NICHT freigeschaltet**

**Fix notwendig:** JA (KRITISCH - P0)

---

## 9. TEST-PLAN

### Test 1: Cash-Bestellung (Punkte sammeln)
1. Neue Email: `test-loyalty-{timestamp}@zozo.de`
2. Warenkorb: 20€
3. Zahlung: Bar
4. ✅ Erwartung: 2 Punkte gutgeschrieben + Toast-Notification

### Test 2: Punkte einlösen
1. Account mit 10 Punkten (= 5€ Rabatt)
2. Warenkorb: 15€
3. Einlösen: 10 Punkte
4. ✅ Erwartung: Total 10€ (15€ - 5€), Punkte-Stand: 0

### Test 3: PayPal-Flow (BUG-Nachweis)
1. Account mit bekannter Email
2. Warenkorb: 30€
3. Zahlung: PayPal (bis Capture)
4. ❌ Erwartung (AKTUELL): **KEINE Punkte gutgeschrieben** (BUG!)
5. ✅ Erwartung (NACH FIX): 3 Punkte gutgeschrieben

### Test 4: Abgebrochene PayPal-Zahlung
1. Draft erstellt
2. PayPal-Fenster geschlossen (OHNE Zahlung)
3. ✅ Erwartung: Draft bleibt "pending", keine Order erstellt, keine Punkte

### Test 5: Kombination mit anderen Rabatten
1. Warenkorb: 50€
2. Pickup: -5€ (10%)
3. Daily Deal (2 for 1 Burger): -8€
4. Punkte einlösen: 20 Punkte = -10€
5. ✅ Total: 27€
6. Punkte verdient: int(27 / 10) = 2 Punkte

---

## 10. DB-STATUS (Aktuell)

```
Total loyalty_accounts: 8
Total loyalty_transactions: 0
```

**Analyse:**
- 8 Accounts existieren (vermutlich Test-Accounts)
- **0 Transaktionen** = System wurde nie produktiv genutzt ODER alle Bestellungen waren PayPal (Bug!)

---

## FINALE BEWERTUNG

### Was funktioniert ✅
- Punkte-Sammlung bei Cash/Karte-Bestellungen
- Punkte-Einlösung im Checkout
- UI-Anzeige (Checkout + Rewards-Seite)
- Server-seitige Validierung
- Persistenz in MongoDB
- Schutz gegen Client-Manipulation
- Achievement-System (für Cash/Karte)
- Tenant-weite Punkte (filialübergreifend)

### KRITISCHE BUGS ❌
1. **PayPal-Flow:** Keine Punkte-Vergabe + keine Punkte-Abzüge = DOPPELT-BUG!
2. **PayPal-Flow:** Keine Achievement-Checks

### Kleinere Probleme ⚠️
- Keine Admin-UI für Loyalty-Verwaltung
- Email-Bestätigung mit Punkten nicht verifiziert

---

## NEXT STEPS

1. **KRITISCH:** PayPal-Capture-Endpoint um Loyalty-Logik erweitern
2. Test-Durchlauf mit Screenshots
3. Finale Dokumentation + Übergabe
